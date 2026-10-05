import configparser
import logging
import os
import sys
import tempfile
import threading
import time
import types
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# AppLogic only needs the logger API in these unit tests. Stub it before the
# module import so tests never touch the user's live AppData log directory.
app_logger_stub = types.ModuleType("core.app_logger")
app_logger_stub.get_app_dir = lambda: ""
app_logger_stub.get_config_path = lambda: ""
app_logger_stub.get_logger = logging.getLogger
sys.modules["core.app_logger"] = app_logger_stub

from gui.logic import AppLogic


class BoolValue:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeWidget:
    def __init__(self):
        self.values = {"state": "normal"}

    def cget(self, name):
        return self.values.get(name)

    def configure(self, **values):
        self.values.update(values)


def make_app(start_minimized=False, run_on_startup=False):
    config = configparser.ConfigParser()
    config.add_section("settings")
    return SimpleNamespace(
        config=config,
        start_minimized=BoolValue(start_minimized),
        run_on_startup=BoolValue(run_on_startup),
        _saved_run_on_startup=run_on_startup,
        auto_start_optimizer=BoolValue(False),
        windows_notifications=BoolValue(False),
        auto_check_updates=BoolValue(True),
    )


class StartupSettingsTests(unittest.TestCase):
    def save(self, logic):
        with tempfile.TemporaryDirectory() as directory:
            config_path = os.path.join(directory, "config.ini")
            with patch("core.app_logger.get_config_path", return_value=config_path):
                logic.save_app_settings()

    def test_start_minimized_change_does_not_touch_task_scheduler(self):
        app = make_app()
        logic = AppLogic(app, engine=None)
        logic.sync_startup_task = MagicMock(return_value=True)

        app.start_minimized.value = True
        self.save(logic)

        logic.sync_startup_task.assert_not_called()

    def test_run_on_startup_change_syncs_task_once(self):
        app = make_app()
        logic = AppLogic(app, engine=None)
        logic.sync_startup_task = MagicMock(return_value=True)

        app.run_on_startup.value = True
        self.save(logic)

        logic.sync_startup_task.assert_called_once_with()
        self.assertTrue(app._saved_run_on_startup)

    def test_optimizer_reset_requires_confirmation(self):
        app = make_app()
        app.tr = lambda text: text
        logic = AppLogic(app, engine=None)

        with (
            patch("gui.logic.messagebox.askyesno", return_value=False),
            patch("gui.logic.reset_opt_config_file") as reset_file,
        ):
            self.assertFalse(logic.reset_opt_config())

        reset_file.assert_not_called()

    def test_confirmed_optimizer_reset_updates_runtime_and_ui(self):
        app = make_app()
        app.tr = lambda text: text
        app.opt_exclude_c0 = BoolValue(False)
        app.opt_disable_smt = BoolValue(True)
        app.opt_auto_clean = BoolValue(True)
        app.opt_clean_interval = BoolValue("30")
        app.opt_auto_shutdown = BoolValue(True)
        app.opt_shutdown_time = BoolValue("20:00")
        optimizer_frame = SimpleNamespace(
            refresh_preset_summary=MagicMock(),
        )
        app.frames = {"optimizer": optimizer_frame}

        defaults = configparser.ConfigParser(delimiters=("=",))
        defaults["Settings"] = {
            "exclude_core_0": "true",
            "disable_smt": "false",
            "auto_cleanup": "false",
            "cleanup_interval": "1440",
            "auto_shutdown": "false",
            "shutdown_time": "23:59",
        }
        defaults["Targets"] = {}
        defaults["PopularGames"] = {"game.exe": "P-CORE"}
        defaults["Paths"] = {}
        defaults["Presets"] = {"popular_games_version": "1"}

        logic = AppLogic(app, engine=None)
        logic.sync_shutdown_task = MagicMock(return_value=True)
        logic.update_topology_stats = MagicMock()
        logic.refresh_opt_list = MagicMock()
        logic.refresh_path_list = MagicMock()

        with (
            patch("gui.logic.messagebox.askyesno", return_value=True),
            patch("gui.logic.messagebox.showinfo"),
            patch("gui.logic.reset_opt_config_file", return_value=defaults),
        ):
            self.assertTrue(logic.reset_opt_config())

        self.assertIs(defaults, app.opt_config)
        self.assertTrue(app.opt_exclude_c0.get())
        self.assertFalse(app.opt_disable_smt.get())
        self.assertFalse(app.opt_auto_clean.get())
        self.assertEqual("1440", app.opt_clean_interval.get())
        self.assertFalse(app.opt_auto_shutdown.get())
        self.assertEqual("23:59", app.opt_shutdown_time.get())
        logic.sync_shutdown_task.assert_called_once_with()
        logic.update_topology_stats.assert_called_once_with()
        logic.refresh_opt_list.assert_called_once_with()
        logic.refresh_path_list.assert_called_once_with()
        optimizer_frame.refresh_preset_summary.assert_called_once_with()

    @unittest.skipUnless(os.name == "nt", "Task Scheduler is Windows-only")
    def test_enabling_startup_updates_without_deleting_first(self):
        app = make_app(run_on_startup=True)
        logic = AppLogic(app, engine=None)
        completed = SimpleNamespace(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", return_value=completed) as run:
            self.assertTrue(logic.sync_startup_task())

        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(1, len(commands))
        self.assertEqual("/create", commands[0][1])
        self.assertNotIn("/delete", commands[0])

    def test_optimizer_restart_never_overlaps_workers(self):
        app = make_app()
        app.opt_stop_event = threading.Event()
        app.cpu_monitor_stop_event = threading.Event()
        app.shutdown_event = threading.Event()
        app.opt_running = False
        app.engine = SimpleNamespace(is_running=False)
        app.tr = lambda text: text
        app.notify_windows = lambda *_args: None
        app.call_in_ui = lambda callback: (callback(), True)[1]
        app.frames = {
            "dashboard": SimpleNamespace(
                btn_toggle_opt=FakeWidget(), status_label=FakeWidget()
            )
        }
        logic = AppLogic(app, engine=app.engine)
        active = 0
        peak = 0
        session_events = []
        state_lock = threading.Lock()

        def fake_optimizer(stop_event, _interval, log_callback=None):
            nonlocal active, peak
            with state_lock:
                active += 1
                peak = max(peak, active)
                session_events.append(stop_event)
            try:
                stop_event.wait()
            finally:
                with state_lock:
                    active -= 1

        def wait_for(predicate, timeout=1.0):
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if predicate():
                    return True
                time.sleep(0.005)
            return False

        with patch("gui.logic.optimize_processes", side_effect=fake_optimizer):
            for expected_sessions in range(1, 6):
                logic.toggle_optimizer()
                self.assertTrue(
                    wait_for(
                        lambda: len(session_events) == expected_sessions
                        and app.frames["dashboard"].btn_toggle_opt.cget("state") == "normal"
                    )
                )
                logic.toggle_optimizer()
                self.assertTrue(
                    wait_for(
                        lambda: not app.opt_running
                        and logic._optimizer_thread is None
                        and app.frames["dashboard"].btn_toggle_opt.cget("state") == "normal"
                    )
                )

        self.assertEqual(1, peak)
        self.assertEqual(5, len({id(event) for event in session_events}))


if __name__ == "__main__":
    unittest.main()
