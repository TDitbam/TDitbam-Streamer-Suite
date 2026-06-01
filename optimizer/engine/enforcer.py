import psutil
import time
from typing import List
from policy.models import Decision, PolicyType, CorePool
from engine.registry import ProcessState
from engine.cache import ProcessStateCache

class Enforcer:
    def __init__(self, cache: ProcessStateCache, core_pool: CorePool, cooldown_ms: int = 500):
        self.cache = cache
        self.core_pool = core_pool
        self.cooldown_s = cooldown_ms / 1000.0

    def enforce(self, proc: psutil.Process, state: ProcessState, decision: Decision) -> bool:
        now = time.time()
        
        # Mapping intent to hardware
        cores, priority = self._map_decision_to_hardware(decision)
        
        # Idempotency check: hash match + cooldown
        if state.last_decision_id == decision.get_stable_id():
            return False
            
        if (now - state.last_apply_ts) < self.cooldown_s:
            return False

        try:
            if self.cache.needs_update(proc.pid, cores, priority):
                if cores:
                    proc.cpu_affinity(cores)
                proc.nice(priority)
                
                state.last_apply_ts = now
                state.last_decision_id = decision.get_stable_id()
                return True
        except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess):
            self.cache.remove_pid(proc.pid)
            return False
        return False

    def _map_decision_to_hardware(self, decision: Decision):
        if decision.policy_type == PolicyType.P_CORE:
            cores = self.core_pool.performance_cores
        elif decision.policy_type == PolicyType.E_CORE:
            cores = self.core_pool.efficiency_cores
        else:
            cores = list(range(psutil.cpu_count()))
            
        if decision.priority > 0:
            priority = psutil.HIGH_PRIORITY_CLASS
        elif decision.priority < 0:
            priority = psutil.BELOW_NORMAL_PRIORITY_CLASS
        else:
            priority = psutil.NORMAL_PRIORITY_CLASS
            
        return cores, priority
