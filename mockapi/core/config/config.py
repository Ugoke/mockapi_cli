from importlib.metadata import version, PackageNotFoundError

from ..io.io import load_settings


def get_config_value(key: str, default: str, value_type: classmethod = str) -> str|bool:
    """Returns the value from the settings by key, or the default value."""
    value = load_settings().get(key)
    if isinstance(value, value_type) and value:
        return value
    return default


def get_version() -> str:
    """Returns the library version or 0.0.0 if an error occurred"""
    try:
        return version("mockapi")
    except PackageNotFoundError:
        return "0.0.0"