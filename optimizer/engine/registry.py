import hashlib
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

STATE_NEW = "NEW"
STATE_STABLE = "STABLE"

@dataclass
class ProcessState:
    pid: int
    create_time: float
    exe_hash: str
    last_decision_id: Optional[Tuple] = None
    last_apply_ts: float = 0.0
    state: str = STATE_NEW

class ProcessRegistry:
    def __init__(self):
        self._entries: Dict[Tuple, ProcessState] = {}

    def _get_exe_hash(self, exe_path: str) -> str:
        return hashlib.sha256(exe_path.lower().encode()).hexdigest()

    def update_or_create(self, pid: int, create_time: float, exe_path: str) -> ProcessState:
        exe_hash = self._get_exe_hash(exe_path)
        key = (pid, create_time, exe_hash)
        if key not in self._entries:
            self._entries[key] = ProcessState(pid, create_time, exe_hash)
        return self._entries[key]

    def remove_stale(self, active_keys: Dict[Tuple, bool]):
        for key in list(self._entries.keys()):
            if key not in active_keys:
                del self._entries[key]

    def get_entry_key(self, pid: int, create_time: float, exe_path: str) -> Tuple:
        return (pid, create_time, self._get_exe_hash(exe_path))
