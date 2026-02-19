import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tuichat"
CONFIG_PATH = CONFIG_DIR / "user_conf.json"

# Temporary user_conf location for testing purposes
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_PATH = Path(BASE_DIR) / ".." / "user_conf.json"

DEFAULT_CONFIG = {"host": "", "port": "", "username": "Guest"}


def load_config() -> dict:
    """
    Returns the active chatroom ID if ".user_conf.json" file exists in cwd.

    Creates ".user_conf.json" file in the cwd with DEFAULT_CONFIG, if it doesn't find an existing one
    and returns default config.

    """
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict):
    """
    Writes config dictionary to .json file at CONFIG_PATH.

    """
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def get_host() -> str:
    """
    Returns value with key "host" in config file at CONFIG_PATH.

    """
    return load_config()["host"]


def get_port() -> str:
    """
    Returns value with key "port" in config file at CONFIG_PATH.

    """
    return load_config()["port"]


def get_username() -> str:
    """
    Returns value with key "username" in config file at CONFIG_PATH.

    """
    return load_config()["username"]


def set_username(username: str):
    """
    Sets the value of key "username" in config file at CONFIG_PATH.

    """
    cfg = load_config()
    cfg["username"] = username
    save_config(cfg)


def set_host(hostname: str):
    """
    Sets the value of key "host" in config file at CONFIG_PATH.

    """
    cfg = load_config()
    cfg["host"] = hostname
    save_config(cfg)


def set_port(port: str):
    """
    Sets the value of key "port" in config file at CONFIG_PATH.

    """
    cfg = load_config()
    cfg["port"] = port
    save_config(cfg)
