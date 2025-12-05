import json
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = Path(BASE_DIR) / ".." / ".." / "data" / "user_conf.json"

DEFAULT_CONFIG = {"uuid": "u_", "username": "Guest"}


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


def set_active_chatroom(chatroom_id: str):
    """
    Sets the value of key "active_chatroom" in config file at CONFIG_PATH.

    """
    cfg = load_config()
    cfg["active_chatroom"] = chatroom_id
    save_config(cfg)


def get_uuid() -> str:
    """
    Returns value with key "unique_user_id" in config file at CONFIG_PATH.

    """
    return load_config()["uuid"]


def set_uuid(uuid: str):
    """
    Sets UUID received from the server.

    """
    cfg = load_config()
    cfg["uuid"] = uuid
    save_config(cfg)


def set_username(username: str):
    """
    Sets the value of key "username" in config file at CONFIG_PATH.

    """
    cfg = load_config()
    cfg["username"] = username
    save_config(cfg)
