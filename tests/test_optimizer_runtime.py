import unittest
from threading import Event
from unittest.mock import patch

from optimizer.engine.cache import ProcessStateCache
from optimizer.engine.registry import ProcessRegistry
from optimizer.optimizer_core import optimizer_engine


class OptimizerRuntimeTests(unittest.TestCase):
    def test_reused_pid_gets_a_fresh_cache_identity(self):
        cache = ProcessStateCache()
        first_process = (4242, 100.0, "hash-a")
        reused_pid = (4242, 200.0, "hash-a")

        self.assertTrue(cache.needs_update(first_process, [1, 2], 128))
        self.assertFalse(cache.needs_update(first_process, [1, 2], 128))
        self.assertTrue(cache.needs_update(reused_pid, [1, 2], 128))

    def test_registry_reports_stale_identity_for_cache_cleanup(self):
        registry = ProcessRegistry()
        state = registry.update_or_create(99, 123.0, "C:/Game/game.exe")

        removed = registry.remove_stale({})

        self.assertEqual([state.identity], removed)

    def test_pre_stopped_optimizer_does_no_config_or_cleanup_work(self):
        stop_event = Event()
        stop_event.set()

        with patch.object(optimizer_engine, "load_config") as load_config, patch.object(
            optimizer_engine, "clean_junk"
        ) as clean_junk:
            optimizer_engine.optimize_processes(stop_event, 5.0)

        load_config.assert_not_called()
        clean_junk.assert_not_called()


if __name__ == "__main__":
    unittest.main()
