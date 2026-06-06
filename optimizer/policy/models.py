from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List

class PolicyType(Enum):
    P_CORE = "P-CORE"
    E_CORE = "E-CORE"
    NORMAL = "NORMAL"

@dataclass(frozen=True)
class Decision:
    priority: int
    policy_type: PolicyType
    disable_smt: bool

    def get_stable_id(self) -> Tuple:
        return (self.priority, self.policy_type.value, self.disable_smt)

@dataclass
class CorePool:
    performance_cores: List[int]
    efficiency_cores: List[int]
    is_hybrid: bool
