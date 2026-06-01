from typing import Dict, List, Tuple
from policy.models import Decision, PolicyType

class PolicyEngine:
    def __init__(self, targets: Dict[str, str], paths: List[Tuple[str, str]]):
        self.targets = {name.lower(): policy for name, policy in targets.items()}
        self.paths = [(path.lower().replace('\\', '/'), policy) for path, policy in paths]

    def decide(self, proc_name: str, proc_path: str, disable_smt: bool) -> Decision:
        policy_str = self._match_policy(proc_name, proc_path)
        
        if policy_str == "P-CORE":
            policy_type = PolicyType.P_CORE
            priority = 1
        elif policy_str == "E-CORE":
            policy_type = PolicyType.E_CORE
            priority = -1
        else:
            policy_type = PolicyType.NORMAL
            priority = 0

        return Decision(priority=priority, policy_type=policy_type, disable_smt=disable_smt)

    def _match_policy(self, proc_name: str, proc_path: str) -> str:
        name_lower = proc_name.lower()
        if name_lower in self.targets:
            return self.targets[name_lower]
        
        if proc_path:
            norm_path = proc_path.lower().replace('\\', '/')
            for folder, policy in self.paths:
                if norm_path.startswith(folder):
                    return policy
        return "NORMAL"
