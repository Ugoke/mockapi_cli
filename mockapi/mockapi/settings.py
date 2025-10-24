from ..core.config.config import get_version, get_config_value

VERSION: str = get_version()

HOST: str = get_config_value("host", "127.0.0.1")
PORT: str = get_config_value("port", "8000")
APPEND_SLASH: bool = get_config_value("append_slash", False, bool)