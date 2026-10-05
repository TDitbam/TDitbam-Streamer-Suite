import configparser
import logging
import os
import tempfile
import threading
from urllib.request import Request, urlopen

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

OPTIMIZER_CONFIG_URL = (
    "https://raw.githubusercontent.com/TDitbam/"
    "TDitbam-Streamer-Suite/main/optimizer-config.ini"
)
CONFIG_DOWNLOAD_TIMEOUT = 8
CONFIG_DOWNLOAD_MAX_BYTES = 1024 * 1024
_REQUIRED_REMOTE_SECTIONS = {"Settings", "Targets", "PopularGames", "Paths"}

_CONFIG_LOCK = threading.RLock()
_LOGGER = logging.getLogger(__name__)


class RemoteConfigError(RuntimeError):
    """Raised when the shared Optimizer profile cannot be downloaded safely."""


def _new_config_parser():
    return configparser.ConfigParser(delimiters=('=',), interpolation=None)


def _create_ready_default_config():
    """Build a complete first-run profile that users can fine-tune later."""
    config = _new_config_parser()
    config["Settings"] = dict(DEFAULT_SETTINGS)
    config["Targets"] = {}
    config["PopularGames"] = dict(POPULAR_GAME_PRESETS)
    config["Paths"] = {}
    config["Presets"] = {
        "popular_games_version": str(POPULAR_GAME_PRESET_VERSION),
    }
    return config


def _download_ready_config():
    """Download and validate the shared Optimizer profile from GitHub."""
    request = Request(
        OPTIMIZER_CONFIG_URL,
        headers={
            "Accept": "text/plain",
            "User-Agent": "TDitbam-Streamer-Suite/3.6.4",
        },
    )
    try:
        with urlopen(request, timeout=CONFIG_DOWNLOAD_TIMEOUT) as response:
            payload = response.read(CONFIG_DOWNLOAD_MAX_BYTES + 1)
    except Exception as error:
        raise RemoteConfigError(f"download failed: {error}") from error

    if not payload or len(payload) > CONFIG_DOWNLOAD_MAX_BYTES:
        raise RemoteConfigError("downloaded config is empty or too large")

    try:
        config_text = payload.decode("utf-8-sig")
        config = _new_config_parser()
        config.read_string(config_text)
    except (UnicodeDecodeError, configparser.Error) as error:
        raise RemoteConfigError(f"downloaded config is invalid: {error}") from error

    missing_sections = _REQUIRED_REMOTE_SECTIONS.difference(config.sections())
    if missing_sections:
        missing = ", ".join(sorted(missing_sections))
        raise RemoteConfigError(f"downloaded config is missing sections: {missing}")
    if not config["PopularGames"]:
        raise RemoteConfigError("downloaded config contains no game presets")

    changed = False
    for name, value in DEFAULT_SETTINGS.items():
        if name not in config["Settings"]:
            config["Settings"][name] = value
            changed = True
    if "Presets" not in config:
        config["Presets"] = {}
        changed = True
    if _apply_popular_game_migration(config):
        changed = True
    if changed:
        _LOGGER.info("Completed missing values in downloaded Optimizer config.")
    return config


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
    config_path = get_opt_config_path()
    if not os.path.exists(config_path):
        try:
            config = _download_ready_config()
            _LOGGER.info("Downloaded Optimizer config from GitHub.")
        except RemoteConfigError as error:
            # First launch must remain usable when GitHub or the network is
            # unavailable. The embedded profile mirrors the published file.
            _LOGGER.warning(
                "Unable to download Optimizer config; using embedded defaults: %s",
                error,
            )
            config = _create_ready_default_config()
        _write_config(config, config_path)
        return config

    config = _new_config_parser()
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


def reset_config():
    """Replace the profile with GitHub config, or embedded defaults offline."""
    with _CONFIG_LOCK:
        try:
            config = _download_ready_config()
            _LOGGER.info("Downloaded Optimizer config from GitHub for reset.")
        except RemoteConfigError as error:
            _LOGGER.warning(
                "Unable to download Optimizer config for reset; using embedded "
                "defaults: %s",
                error,
            )
            config = _create_ready_default_config()
        _write_config(config, get_opt_config_path())
        return config


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
