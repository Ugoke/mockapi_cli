import json
import os
from pathlib import Path

from .constants import MOCKS_FILE_PATH, SETTINGS_FILE_PATH, MOCKS_FILE_EXAMPLE_PATH, SETTINGS_FILE_EXAMPLE_PATH
from ..utils import logger


def _read_json(path: Path, fallback: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Can't read %s: %s", path, e)
        try:
            return json.loads(fallback.read_text(encoding="utf-8"))
        except Exception as e2:
            logger.error("Can't read fallback %s: %s", fallback, e2)
            return None


def load_mocks() -> list[dict]:
    env_path = os.environ.get("MOCKS_FILE")
    path = Path(env_path) if env_path and Path(env_path).exists() else (
        MOCKS_FILE_PATH if MOCKS_FILE_PATH.exists() else MOCKS_FILE_EXAMPLE_PATH
    )
    data = _read_json(path, MOCKS_FILE_EXAMPLE_PATH) or []
    return data if isinstance(data, list) else [data]


def load_settings() -> dict:
    path = SETTINGS_FILE_PATH if SETTINGS_FILE_PATH.exists() else SETTINGS_FILE_EXAMPLE_PATH
    data = _read_json(path, SETTINGS_FILE_EXAMPLE_PATH) or {}
    return data if isinstance(data, dict) else {}