import logging
import threading
import unittest

# Another test module installs a deliberately minimal app_logger stub during
# discovery. Complete the one attribute gui.app imports so this regression
# test remains order-independent while leaving the real module unchanged.
import core.app_logger as app_logger

if not hasattr(app_logger, "logger"):
    app_logger.logger = logging.getLogger("StreamerSuite")

from gui.app import App


class FakeWindow:
    def __init__(self, *, revealed=True, run_callbacks=True):
        self.shutdown_event = threading.Event()
        self.dashboard_metrics_active = threading.Event()
        self._window_visible = False
        self._window_has_been_revealed = revealed
        self._restore_pending = False
        self._current_page = "dashboard"
        self._state = "withdrawn"
        self.run_callbacks = run_callbacks
        self.queued_callbacks = []
        self.attribute_calls = []
        self.deiconify_calls = 0
        self.update_calls = 0
        self.lift_calls = 0
        self.focus_calls = 0

    def call_in_ui(self, callback):
        self.queued_callbacks.append(callback)
        if self.run_callbacks:
            callback()
        return True

    def _restore_window(self):
        App._restore_window(self)

    def _release_restore_topmost(self):
        App._release_restore_topmost(self)

    def state(self):
        return self._state

    def deiconify(self):
        self.deiconify_calls += 1
        self._state = "normal"

    def update_idletasks(self):
        self.update_calls += 1

    def attributes(self, name, value):
        self.attribute_calls.append((name, value))

    def after(self, _delay, callback):
        callback()

    def lift(self):
        self.lift_calls += 1

    def focus_force(self):
        self.focus_calls += 1


class WindowRestoreTests(unittest.TestCase):
    def test_subsequent_restore_keeps_existing_ui_visible(self):
        window = FakeWindow(revealed=True)

        self.assertTrue(App.show_from_tray(window))

        self.assertEqual(1, window.deiconify_calls)
        self.assertEqual(0, window.update_calls)
        self.assertNotIn(("-alpha", 0.0), window.attribute_calls)
        self.assertNotIn(("-alpha", 1.0), window.attribute_calls)
        self.assertTrue(window.dashboard_metrics_active.is_set())

    def test_start_minimized_window_runs_first_reveal_only_once(self):
        window = FakeWindow(revealed=False)

        App.show_from_tray(window)
        window._window_visible = False
        window._state = "withdrawn"
        App.show_from_tray(window)

        self.assertEqual(2, window.deiconify_calls)
        self.assertEqual(1, window.update_calls)
        self.assertEqual(1, window.attribute_calls.count(("-alpha", 1.0)))
        self.assertNotIn(("-alpha", 0.0), window.attribute_calls)

    def test_repeated_activation_requests_are_coalesced(self):
        window = FakeWindow(revealed=True, run_callbacks=False)

        self.assertTrue(App.show_from_tray(window))
        self.assertFalse(App.show_from_tray(window))
        self.assertEqual(1, len(window.queued_callbacks))

        window.queued_callbacks[0]()
        self.assertFalse(window._restore_pending)
        self.assertTrue(App.show_from_tray(window))
        self.assertEqual(2, len(window.queued_callbacks))


if __name__ == "__main__":
    unittest.main()
