import configparser
import os
import tempfile
import threading

from .game_presets import POPULAR_GAME_PRESETS, POPULAR_GAME_PRESET_VERSION


DEFAULT_SETTINGS = {
    "interval": "5",
    "exclude_core_0": "true",
    "disable_smt": "false",
    "auto_cleanup": "false",
    "cleanup_interval": "1440",
    "last_cleanup": "0",
    "auto_shutdown": "false",
    "shutdown_time": "23:59",
}

_CONFIG_LOCK = threading.RLock()

def get_opt_config_path():
    # ใช้ AppData\Roaming ตามมาตรฐาน Windows
    if os.name == 'nt':
        app_dir = os.path.join(os.environ['APPDATA'], 'TDitbam-Streamer-Suite')
    else:
        app_dir = os.path.join(os.path.expanduser("~"), ".tditbam-streamer-suite")
        
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, "optimizer_config.ini")

def _write_config(config, config_path):
    """Replace the config atomically so the Optimizer never reads half a file."""
    file_descriptor, temp_path = tempfile.mkstemp(
        prefix="optimizer_config_",
        suffix=".tmp",
        dir=os.path.dirname(config_path),
        text=True,
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as config_file:
            config.write(config_file)
        os.replace(temp_path, config_path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


def _apply_popular_game_migration(config):
    """Add each preset release once without overwriting existing policies."""
    if "Presets" not in config:
        config["Presets"] = {}

    installed_version = config["Presets"].getint(
        "popular_games_version", fallback=0
    )
    if installed_version >= POPULAR_GAME_PRESET_VERSION:
        return False

    presets = config["PopularGames"]
    for executable, policy in POPULAR_GAME_PRESETS.items():
        if executable not in presets:
            presets[executable] = policy
    config["Presets"]["popular_games_version"] = str(
        POPULAR_GAME_PRESET_VERSION
    )
    return True


def _load_config_unlocked():
    config = configparser.ConfigParser(delimiters=('=',))
    config_path = get_opt_config_path()
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")

    changed = False
    if "Settings" not in config:
        config["Settings"] = {}
        changed = True
    for name, value in DEFAULT_SETTINGS.items():
        if name not in config["Settings"]:
            config["Settings"][name] = value
            changed = True
    if "Targets" not in config:
        config["Targets"] = {}
        changed = True
    if "PopularGames" not in config:
        config["PopularGames"] = {}
        changed = True
    if "Paths" not in config:
        config["Paths"] = {}
        changed = True
    if _apply_popular_game_migration(config):
        changed = True
    if changed:
        _write_config(config, config_path)
    return config


def load_config():
    with _CONFIG_LOCK:
        return _load_config_unlocked()

def save_config(config):
    with _CONFIG_LOCK:
        _write_config(config, get_opt_config_path())


def update_config(mutator):
    """Atomically apply a focused mutation to the latest on-disk config."""
    with _CONFIG_LOCK:
        config = _load_config_unlocked()
        mutator(config)
        _write_config(config, get_opt_config_path())
        return config

def get_targets(config):
    """Return active presets plus user targets, with user policies winning."""
    targets = dict(config.items("PopularGames")) if "PopularGames" in config else {}
    if "Targets" in config:
        targets.update(config.items("Targets"))
    return list(targets.items())


def get_user_targets(config):
    return config.items("Targets") if "Targets" in config else []


def get_popular_game_count(config):
    return len(config["PopularGames"]) if "PopularGames" in config else 0


def get_paths(config): return config.items("Paths") if "Paths" in config else []
