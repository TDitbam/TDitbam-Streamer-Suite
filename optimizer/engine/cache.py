from typing import Hashable, List

class ProcessStateCache:
    def __init__(self):
        # PID alone is unsafe because Windows can reuse it for a new process.
        self._cache = {}  # Process identity -> {affinity: [], priority: int}

    def needs_update(self, process_key: Hashable, affinity: List[int], priority: int) -> bool:
        if process_key not in self._cache:
            self._cache[process_key] = {"affinity": affinity, "priority": priority}
            return True
        
        state = self._cache[process_key]
        if sorted(state["affinity"]) != sorted(affinity) or state["priority"] != priority:
            state["affinity"] = affinity
            state["priority"] = priority
            return True
            
        return False

    def remove(self, process_key: Hashable):
        self._cache.pop(process_key, None)
