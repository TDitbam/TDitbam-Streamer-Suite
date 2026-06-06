import os
import platform

def get_junk_paths():
    paths = []
    if platform.system() == "Windows":
        # System & User Temp
        user_temp = os.environ.get('TEMP')
        if user_temp: paths.append(user_temp)
        sys_temp = "C:\\Windows\\Temp"
        if os.path.exists(sys_temp): paths.append(sys_temp)
        
        # GPU Caches (NVIDIA, AMD, Intel)
        gpu_paths = [
            "%LocalAppData%\\NVIDIA\\DXCache",
            "%LocalAppData%\\NVIDIA\\GLCache",
            "%LocalAppData%\\NVIDIA Corporation\\NV_Cache",
            "%LocalAppData%\\AMD\\DXCache",
            "%LocalAppData%\\Intel\\ShaderCache"
        ]
        for p in gpu_paths:
            expanded = os.path.expandvars(p)
            if os.path.exists(expanded):
                paths.append(expanded)
    return paths

def clean_junk(progress_callback=None):
    def _log(msg):
        if progress_callback: progress_callback(msg)

    files_deleted = 0
    bytes_saved = 0
    whitelist = ["steam", "epic", "unity", "unreal", "riot games", "localbackups", "discord", "spotify", "roblox", "minecraft", "hoyoverse"]
    paths = get_junk_paths()
    
    for path in paths:
        if not os.path.exists(path): continue
        _log(f"[*] Scanning: {path}")
        for root, dirs, files in os.walk(path, topdown=False):
            if any(w_word in root.lower() for w_word in whitelist): continue
            
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    files_deleted += 1
                    bytes_saved += size
                    _log(f"[OK] Deleted: {name}")
                except Exception:
                    continue
            
            for name in dirs:
                dir_path = os.path.join(root, name)
                if any(w_word in dir_path.lower() for w_word in whitelist): continue
                try:
                    os.rmdir(dir_path)
                    _log(f"[OK] Removed Empty Dir: {name}")
                except Exception:
                    continue
    return files_deleted, bytes_saved
