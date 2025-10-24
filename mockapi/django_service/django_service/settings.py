from pathlib import Path
from mockapi.core.config.config import get_config_value


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-mockapi-local"
DEBUG = True
ALLOWED_HOSTS = [get_config_value("host", "127.0.0.1")]

INSTALLED_APPS = []
MIDDLEWARE = []

ROOT_URLCONF = "mockapi.django_service.django_service.urls"
WSGI_APPLICATION = "mockapi.django_service.django_service.wsgi.application"

APPEND_SLASH = get_config_value("append_slash", False, bool)