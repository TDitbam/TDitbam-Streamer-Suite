from typing import List

class ProcessStateCache:
    def __init__(self):
        self._cache = {} # PID -> {affinity: [], priority: int}

    def needs_update(self, pid: int, affinity: List[int], priority: int) -> bool:
        if pid not in self._cache:
            self._cache[pid] = {"affinity": affinity, "priority": priority}
            return True
        
        state = self._cache[pid]
        if sorted(state["affinity"]) != sorted(affinity) or state["priority"] != priority:
            state["affinity"] = affinity
            state["priority"] = priority
            return True
            
        return False

    def remove_pid(self, pid: int):
        if pid in self._cache:
            del self._cache[pid]
