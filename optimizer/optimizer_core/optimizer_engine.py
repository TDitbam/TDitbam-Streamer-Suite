import time
import psutil
from .config_loader import load_config, get_targets, get_paths, update_config
from .cpu_topology import split_p_e_cores, calculate_affinity_mask
from .cleaner import clean_junk
from ..engine.cache import ProcessStateCache
from ..engine.enforcer import Enforcer
from ..engine.registry import ProcessRegistry
from ..policy.models import CorePool
from ..policy.engine import PolicyEngine

def optimize_processes(stop_event, default_interval, log_callback=None):
    # Initialize v3 Engine Components
    cache = ProcessStateCache()
    registry = ProcessRegistry()
    
    # Topology Tracking
    last_exclude = None
    last_disable_smt = None
    core_pool = None
    enforcer = None

    def _log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    while True:
        if stop_event and stop_event.is_set():
            break
        config = load_config()
        try:
            exclude_core_0 = config["Settings"].getboolean("exclude_core_0", fallback=True)
            disable_smt = config["Settings"].getboolean("disable_smt", fallback=False)
            auto_cleanup = config["Settings"].getboolean("auto_cleanup", fallback=False)
            last_cleanup = float(config["Settings"].get("last_cleanup", 0))
            interval = min(
                300.0,
                max(1.0, float(config["Settings"].get("interval", default_interval))),
            )
        except (ValueError, TypeError, KeyError):
            exclude_core_0, disable_smt, auto_cleanup, last_cleanup = True, False, False, 0
            interval = default_interval
            
        # Update Topology if settings changed
        if exclude_core_0 != last_exclude or disable_smt != last_disable_smt:
            p, e = split_p_e_cores(exclude_core_0, disable_smt)
            core_pool = CorePool(p, e, len(e) > 0)
            if not enforcer:
                enforcer = Enforcer(cache, core_pool)
            else:
                enforcer.core_pool = core_pool
            last_exclude, last_disable_smt = exclude_core_0, disable_smt

        # Policy Brain
        policy_engine = PolicyEngine(dict(get_targets(config)), list(get_paths(config)))
            
        # Auto Cleanup
        current_time = time.time()
        try:
            cleanup_interval_min = min(
                525600.0,
                max(1.0, float(config["Settings"].get("cleanup_interval", 1440))),
            )
        except (ValueError, TypeError, KeyError):
            cleanup_interval_min = 1440.0
        cleanup_interval_sec = cleanup_interval_min * 60

        if auto_cleanup and (current_time - last_cleanup > cleanup_interval_sec):
            _log("[*] Running Scheduled Auto-Cleanup...")
            clean_junk(log_callback, cancel_event=stop_event)
            if stop_event and stop_event.is_set():
                break
            config = update_config(
                lambda latest: latest["Settings"].__setitem__(
                    "last_cleanup", str(current_time)
                )
            )

        # Monitor & Enforce
        active_keys = {}
        # Fetch only PID/name for the full process list. Executable paths and
        # creation times are relatively expensive Windows queries, so request
        # them only for a process that can actually match a configured policy.
        for proc in psutil.process_iter(['pid', 'name']):
            if stop_event and stop_event.is_set():
                break
            try:
                pid, name = proc.info['pid'], proc.info['name']
                if not pid or not name: continue

                exe_path = ""
                if name.lower() not in policy_engine.targets:
                    if not policy_engine.paths:
                        continue
                    exe_path = proc.exe() or ""
                decision = policy_engine.decide(name, exe_path, disable_smt)
                if decision is None:
                    continue
                create_time = proc.create_time()
                state = registry.update_or_create(pid, create_time, exe_path)
                
                if enforcer.enforce(proc, state, decision):
                    cores, _ = enforcer._map_decision_to_hardware(decision)
                    mask = calculate_affinity_mask(cores)
                    _log(f"[OPT] PID: {pid} | {name} | Mode: {decision.policy_type.value} | Mask: {hex(mask)}")

                active_keys[registry.get_entry_key(pid, create_time, exe_path)] = True
            except (psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess, OSError):
                continue
                
        for stale_key in registry.remove_stale(active_keys):
            cache.remove(stale_key)

        if stop_event and stop_event.is_set(): break
        if stop_event:
            if stop_event.wait(interval):
                break
        else: time.sleep(interval)
