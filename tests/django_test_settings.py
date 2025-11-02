# tests/django_test_settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "test-secret-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",

    # your apps
    "core",
    "agents",
    "content",
    "sports",
    "mythology",
]

# If you have app configs like "core.apps.CoreConfig", prefer those:
# INSTALLED_APPS += ["core.apps.CoreConfig", ...]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# Point this at your project urls module
ROOT_URLCONF = "backend.urls"  # change if your urls live elsewhere

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
TIME_ZONE = "UTC"

STATIC_URL = "/static/"

# If you have a custom user model in core/models/base/models.py
AUTH_USER_MODEL = "core.UnifiedUser"

# Speed up tests: disable password validators
AUTH_PASSWORD_VALIDATORS = []