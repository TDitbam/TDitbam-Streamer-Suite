import psutil
import os
import ctypes
from ctypes import wintypes

# --- Windows API Definitions ---
RelationProcessorCore = 0

class GROUP_AFFINITY(ctypes.Structure):
    _fields_ = [
        ("Mask", ctypes.c_size_t),
        ("Group", wintypes.WORD),
        ("Reserved", wintypes.WORD * 3),
    ]

class PROCESSOR_RELATIONSHIP(ctypes.Structure):
    _fields_ = [
        ("Flags", ctypes.c_byte),
        ("EfficiencyClass", ctypes.c_byte),
        ("Reserved", ctypes.c_byte * 20),
        ("GroupCount", wintypes.WORD),
        ("GroupMask", GROUP_AFFINITY * 1),
    ]

class SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX(ctypes.Structure):
    _fields_ = [
        ("Relationship", ctypes.c_int),
        ("Size", wintypes.DWORD),
        ("Processor", PROCESSOR_RELATIONSHIP),
    ]

def get_cpu_topology_windows():
    """
    Uses Windows API GetLogicalProcessorInformationEx to get core efficiency classes.
    Returns a list of tuples: (logical_cores_list, efficiency_class)
    """
    if os.name != 'nt':
        return None

    try:
        kernel32 = ctypes.windll.kernel32
        buffer_size = wintypes.DWORD(0)
        kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, None, ctypes.byref(buffer_size))
        
        if buffer_size.value == 0:
            return None
            
        buffer = ctypes.create_string_buffer(buffer_size.value)
        if not kernel32.GetLogicalProcessorInformationEx(RelationProcessorCore, buffer, ctypes.byref(buffer_size)):
            return None
            
        topology = []
        offset = 0
        while offset < buffer_size.value:
            addr = ctypes.addressof(buffer) + offset
            info = ctypes.cast(addr, ctypes.POINTER(SYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX)).contents
            
            if info.Relationship == RelationProcessorCore:
                proc = info.Processor
                eff_class = proc.EfficiencyClass
                
                logical_cores = []
                for g in range(proc.GroupCount):
                    mask = proc.GroupMask[g].Mask
                    group_offset = proc.GroupMask[g].Group * 64
                    
                    for i in range(64):
                        if (mask >> i) & 1:
                            logical_cores.append(group_offset + i)
                
                topology.append((logical_cores, eff_class))
            
            if info.Size == 0: break
            offset += info.Size
            
        return topology
    except Exception:
        return None

def get_cpu_topology():
    logical = psutil.cpu_count(logical=True)
    physical = psutil.cpu_count(logical=False)
    if logical is None or physical is None: return []
    smt_pairs_count = logical - physical
    topology = []
    for i in range(smt_pairs_count): topology.append([2*i, 2*i + 1])
    for i in range(smt_pairs_count * 2, logical): topology.append([i])
    return topology

def calculate_affinity_mask(cores_list):
    mask = 0
    for core in cores_list:
        if isinstance(core, int): mask |= (1 << core)
    return mask

def split_p_e_cores(exclude_core_0=True, disable_smt=False):
    win_topo = get_cpu_topology_windows()
    if win_topo:
        all_classes = sorted(list(set(t[1] for t in win_topo)))
        p_phys_cores = []
        e_phys_cores = []
        if len(all_classes) > 1:
            max_class = all_classes[-1]
            for cores, eff in win_topo:
                if eff == max_class: p_phys_cores.append(cores)
                else: e_phys_cores.append(cores)
        else:
            p_phys_cores = [t[0] for t in win_topo]
            e_phys_cores = []
            
        if exclude_core_0 and len(p_phys_cores) > 1:
            p_phys_cores = p_phys_cores[1:]
            
        if disable_smt:
            p_cores = [phys[0] for phys in p_phys_cores]
            e_cores = [phys[0] for phys in e_phys_cores]
        else:
            p_cores = [c for phys in p_phys_cores for c in phys]
            e_cores = [c for phys in e_phys_cores for c in phys]
        return p_cores or [0], e_cores

    topology = get_cpu_topology()
    if not topology: return [0], []
    logical = psutil.cpu_count(logical=True)
    physical = psutil.cpu_count(logical=False)
    smt_pairs_count = logical - physical
    p_phys_groups = []
    e_phys_groups = []
    if smt_pairs_count > 0:
        if smt_pairs_count < physical:
            p_phys_groups = topology[:smt_pairs_count]
            e_phys_groups = topology[smt_pairs_count:]
        else:
            p_phys_groups = topology
            e_phys_groups = []
    else:
        p_phys_groups = topology
        e_phys_groups = []
    if exclude_core_0 and len(p_phys_groups) > 1:
        p_phys_groups = p_phys_groups[1:]
    if disable_smt:
        p_cores = [phys[0] for phys in p_phys_groups]
        e_cores = [phys[0] for phys in e_phys_groups]
    else:
        p_cores = [core for phys in p_phys_groups for core in phys]
        e_cores = [core for phys in e_phys_groups for core in phys]
    return p_cores or [0], e_cores
