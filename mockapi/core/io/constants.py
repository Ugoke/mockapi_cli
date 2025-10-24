from importlib.resources import files


MOCKAPI_ROOT = files("mockapi")
SETTINGS_FILE_PATH = MOCKAPI_ROOT / "data" / "settings.json"
MOCKS_FILE_PATH = MOCKAPI_ROOT / "data" / "mocks.json"
SETTINGS_FILE_EXAMPLE_PATH = MOCKAPI_ROOT / "data.example" / "settings.json"
MOCKS_FILE_EXAMPLE_PATH = MOCKAPI_ROOT / "data.example" / "mocks.json"