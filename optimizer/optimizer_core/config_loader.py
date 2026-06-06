import configparser
import os
import sys

def get_opt_config_path():
    # ใช้ AppData\Roaming ตามมาตรฐาน Windows
    if os.name == 'nt':
        app_dir = os.path.join(os.environ['APPDATA'], 'TDitbam-Streamer-Suite')
    else:
        app_dir = os.path.join(os.path.expanduser("~"), ".tditbam-streamer-suite")
        
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, "optimizer_config.ini")

def load_config():
    config = configparser.ConfigParser(delimiters=('=',))
    config_path = get_opt_config_path()
    if not os.path.exists(config_path):
        config["Settings"] = {
            "interval": "5",
            "exclude_core_0": "true",
            "disable_smt": "false",
            "auto_cleanup": "false",
            "cleanup_interval": "1440",
            "last_cleanup": "0"
        }
        config["Targets"] = {"BlackDesert64.exe": "P-CORE", "cs2.exe": "P-CORE", "cyberpunk2077.exe": "P-CORE"}
        config["Paths"] = {}
        with open(config_path, "w") as f: config.write(f)
    config.read(config_path)
    if "Settings" not in config: config["Settings"] = {"interval": "5"}
    if "Targets" not in config: config["Targets"] = {}
    if "Paths" not in config: config["Paths"] = {}
    return config

def save_config(config):
    with open(get_opt_config_path(), "w") as f: config.write(f)

def get_targets(config): return config.items("Targets")
def get_paths(config): return config.items("Paths") if "Paths" in config else []
