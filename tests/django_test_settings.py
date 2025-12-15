# tests/django_test_settings.py
"""
Django test settings - SQLite-based for CI/CD and quick local testing.

This configuration excludes apps requiring PostgreSQL-specific features
(pgvector, ArrayField). For full integration testing with all features,
use the main settings with a PostgreSQL database.

Note: Some models use ArrayField which requires PostgreSQL. These tests
mock the database operations to work with SQLite.
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "test-secret-key-for-testing-only"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# All platform apps - using PostgreSQL so we can include everything
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "channels",
    "pgvector",

    # Core app (required by agents, content, etc.)
    "core",

    # Platform apps
    "agents",          # Agent system
    "content",         # Content models (images, videos, projects)
    "sports",          # Sports analytics
    "mythology",       # Mythology detection
    "pipelines",       # Creative pipelines
    "persistence",     # Data persistence with pgvector
    "intelligence",    # Real-time intelligence
    "coleadership",    # Co-leadership system
    "rendering",       # Render jobs
    "ai_core",         # AI core components
    "ml",              # ML models
    "style_memory",    # Style memory system
    "dashboard",       # Dashboard API
    "workflows",       # Workflow management
    "ai_opportunities", # AI project generation
    "self_awareness",  # Code introspection
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "tests.test_urls"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Simplified for testing
    ],
}

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

# Use PostgreSQL for testing (required for ArrayField, pgvector)
import dj_database_url

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres@localhost:5432/unified_donkey_betz'
)

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# Configure test database - pytest-django will create test_<dbname>
DATABASES['default']['TEST'] = {
    'NAME': 'test_unified_donkey_betz_pytest',
}

USE_TZ = True
TIME_ZONE = "UTC"

STATIC_URL = "/static/"

# Use core's unified user model
AUTH_USER_MODEL = "core.UnifiedUser"

# Speed up tests
AUTH_PASSWORD_VALIDATORS = []
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {'null': {'class': 'logging.NullHandler'}},
    'root': {'handlers': ['null'], 'level': 'CRITICAL'},
}

# Channel layers for testing
CHANNEL_LAYERS = {
    "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}
}

# Default storage for file fields
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')
MEDIA_URL = '/media/'

# Redis URL for testing (uses Redis if available, fake if not)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

# OpenAI/GPT configuration for testing
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'test-key-not-used-in-tests')

# Stability AI configuration for testing
STABILITY_API_KEY = os.environ.get('STABILITY_API_KEY', 'test-key')

# ElevenLabs configuration for testing
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', 'test-key')

# Use clean agent architecture
USE_CLEAN_AGENT_ARCHITECTURE = True
