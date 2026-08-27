import unittest

from optimizer.policy.engine import PolicyEngine
from optimizer.policy.models import PolicyType


class OptimizerPolicyTests(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngine(
            {
                "game.exe": "P-CORE",
                "background.exe": "E-CORE",
                "reset.exe": "NORMAL",
            },
            [("C:/Managed/", "E-CORE")],
        )

    def test_unmanaged_windows_processes_are_ignored(self):
        for name in ("explorer.exe", "dwm.exe", "RuntimeBroker.exe"):
            with self.subTest(name=name):
                self.assertIsNone(
                    self.engine.decide(name, f"C:/Windows/{name}", False)
                )

    def test_explicit_target_policies_are_preserved(self):
        expected = {
            "game.exe": PolicyType.P_CORE,
            "background.exe": PolicyType.E_CORE,
            "reset.exe": PolicyType.NORMAL,
        }
        for name, policy_type in expected.items():
            with self.subTest(name=name):
                decision = self.engine.decide(name, f"C:/Apps/{name}", False)
                self.assertEqual(policy_type, decision.policy_type)

    def test_managed_directory_still_matches(self):
        decision = self.engine.decide(
            "worker.exe", "C:\\Managed\\worker.exe", False
        )
        self.assertEqual(PolicyType.E_CORE, decision.policy_type)


if __name__ == "__main__":
    unittest.main()
