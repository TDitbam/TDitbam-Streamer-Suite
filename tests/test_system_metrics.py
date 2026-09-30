import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.system_metrics import sample_program_usage


def fake_process(pid, name, created, cpu_total, ram_bytes):
    return SimpleNamespace(
        info={
            "pid": pid,
            "name": name,
            "create_time": created,
            "cpu_times": SimpleNamespace(user=cpu_total, system=0.0),
            "memory_info": SimpleNamespace(rss=ram_bytes),
        }
    )


class SystemMetricsTests(unittest.TestCase):
    @patch("core.system_metrics.psutil.cpu_count", return_value=4)
    @patch("core.system_metrics.psutil.virtual_memory")
    @patch("core.system_metrics.time.monotonic")
    @patch("core.system_metrics.psutil.process_iter")
    def test_bulk_cpu_delta_and_pid_reuse(self, process_iter, monotonic, memory, _cpu_count):
        memory.return_value = SimpleNamespace(total=1_000)
        cache = {}

        monotonic.return_value = 10.0
        process_iter.return_value = [fake_process(7, "game.exe", 1.0, 2.0, 100)]
        first = sample_program_usage({}, cache)
        self.assertEqual(0.0, first[0]["cpu"])

        monotonic.return_value = 11.0
        process_iter.return_value = [fake_process(7, "game.exe", 1.0, 4.0, 100)]
        second = sample_program_usage({}, cache)
        self.assertEqual(50.0, second[0]["cpu"])

        # The same PID with a new creation time is a different process and
        # must start from a fresh CPU baseline instead of inheriting a spike.
        monotonic.return_value = 12.0
        process_iter.return_value = [fake_process(7, "game.exe", 2.0, 20.0, 100)]
        reused = sample_program_usage({}, cache)
        self.assertEqual(0.0, reused[0]["cpu"])


if __name__ == "__main__":
    unittest.main()
