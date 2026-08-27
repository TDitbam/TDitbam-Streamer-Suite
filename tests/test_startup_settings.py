import configparser
import logging
import os
import sys
import tempfile
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


if __name__ == "__main__":
    unittest.main()
