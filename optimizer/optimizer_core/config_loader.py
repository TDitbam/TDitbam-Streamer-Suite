import configparser
import os

CONFIG_FILE = "config/config.ini"

def load_config():
    config = configparser.ConfigParser(delimiters=('=',))
    if not os.path.exists(CONFIG_FILE):
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
        config_dir = os.path.dirname(CONFIG_FILE)
        if config_dir and not os.path.exists(config_dir): os.makedirs(config_dir)
        with open(CONFIG_FILE, "w") as f: config.write(f)
    config.read(CONFIG_FILE)
    if "Settings" not in config: config["Settings"] = {"interval": "5"}
    if "Targets" not in config: config["Targets"] = {}
    if "Paths" not in config: config["Paths"] = {}
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f: config.write(f)

def get_targets(config): return config.items("Targets")
def get_paths(config): return config.items("Paths") if "Paths" in config else []
