"""
UNIFIED DONKEY BETZ PLATFORM
Django settings for the unified mega-platform

This configuration unifies:
- Donkey Betz (Sports Analytics)
- AI Content Studio (Content Generation)
- DBAO (Agent Orchestration)
- Self-Awareness & Intelligence Layer
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Dynamic ALLOWED_HOSTS for production
if DEBUG:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,192.168.*,*').split(',')
else:
    # Production hosts
    default_hosts = [
        'localhost',
        '127.0.0.1',
        '.donkeybetz.com',  # Allow all subdomains
        '.vercel.app',      # Allow Vercel deployments
        '.netlify.app',     # Allow Netlify deployments
        '.herokuapp.com',   # Allow Heroku deployments
        '.railway.app',     # Allow Railway deployments
    ]
    custom_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []
    ALLOWED_HOSTS = default_hosts + custom_hosts

# Platform Configuration
PLATFORM_NAME = os.environ.get('PLATFORM_NAME', 'Unified Donkey Betz')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')
WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8001')

# Application definition
INSTALLED_APPS = [
    # ASGI/WebSocket support (MUST be first)
    'daphne',
    
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party packages
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'channels',
    # 'django_celery_beat',      # Will add when package is installed
    # 'django_celery_results',   # Will add when package is installed
    
    # Core app only for now
    'core',                    # Core utilities and management

    # Unified platform apps (will be created step by step)
    # 'gateway',                 # Unified API Gateway
    # 'memory',                  # Unified Memory System
    'agents',                  # Agent Registry & Orchestration
    # 'ai_services',            # Multi-Provider AI Interface
    'ai_core.spiders',         # Spider Army System
    'ai_core',                 # AI Core app for agents, spiders, intelligence
    'ai_core.intelligence',   # Intelligence & Learning System
    'ml',                     # Machine Learning Engine
    'sports',                 # Sports Analytics Engine
    'content',                # Content Generation System
    'persistence',            # Data Persistence Infrastructure (NEW)
    'self_awareness',         # Code Introspection & Self-Modification
    'style_memory',           # Style Memory System
    'dashboard',              # Dashboard API endpoints
    # 'campaigns',              # Campaign management (archived)
    'workflows',              # Workflow management
    'mythology',              # Mythology detection and prevention system
    'ai_opportunities',       # AI Project Generation & Storage
    # 'realtime',               # WebSocket & Event Bus
    # 'monitoring',             # System Health & Analytics
    # 'billing',                # Unified billing system
    # 'security',               # Security and authentication
    # 'workflow',               # Workflow orchestration
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files in production
    'corsheaders.middleware.CorsMiddleware',
    'core.auth_middleware.SecurityHeadersMiddleware',  # Enhanced security headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.DisableCSRFForAuthEndpoints',  # Custom CSRF exemption
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Temporarily disabled for testing
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.auth_middleware.UnifiedTokenAuthenticationMiddleware',  # Unified API auth with dev bypass
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.rate_limiter.RateLimitMiddleware',  # Global rate limiting
    'core.auth_middleware.RateLimitingMiddleware',  # Enhanced rate limiting
    'core.auth_middleware.APILoggingMiddleware',  # API request/response logging
    
    # Unified platform middleware (will be created)
    # 'gateway.middleware.UnifiedAPIMiddleware',
    # 'monitoring.middleware.PerformanceMiddleware',
    # 'billing.middleware.UsageTrackingMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Production-Grade Channels Configuration - SIMPLIFIED
try:
    import channels_redis
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('localhost', 6379)],  # Simple configuration
            },
        },
    }
except ImportError:
    # Fallback to in-memory channel layer
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Database - PostgreSQL with pgvector support
import dj_database_url

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Database-specific configuration
if 'postgresql' in os.environ.get('DATABASE_URL', ''):
    # PostgreSQL specific configuration
    DATABASES['default']['OPTIONS'] = {
        'application_name': 'unified_donkey_betz',
        'client_encoding': 'UTF8',
        'connect_timeout': 10,
        'options': '-c search_path=studio,public,dbao,shared'  # Include all schemas
    }
    DATABASES['default']['CONN_MAX_AGE'] = 600
else:
    # SQLite configuration
    DATABASES['default']['OPTIONS'] = {}
    DATABASES['default']['CONN_MAX_AGE'] = 0

# Production-Grade Cache Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
        'KEY_PREFIX': 'udb',  # Unified Donkey Betz prefix
        'TIMEOUT': 300,  # Default 5 minutes
        'OPTIONS': {
            'max_connections': 50,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'socket_keepalive': True,
            'socket_keepalive_options': {},
            'retry_on_timeout': True,
            'health_check_interval': 30,
        },
        'VERSION': 1,
    }
}

# Production Redis connection with retry logic
try:
    import redis
    from redis.retry import Retry
    from redis.backoff import ExponentialBackoff

    # Test connection with production settings
    r = redis.from_url(
        REDIS_URL,
        socket_connect_timeout=5,
        socket_timeout=5,
        socket_keepalive=True,
        health_check_interval=30,
        retry=Retry(ExponentialBackoff(), 3),
        retry_on_timeout=True
    )
    r.ping()

    # Redis connection is healthy
    REDIS_HEALTHY = True
except Exception as e:
    REDIS_HEALTHY = False
    # Fallback to local memory cache if Redis is not available
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }

    # Log Redis connection issue
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f'Redis connection failed, using local memory cache: {e}')

# AI Provider Configuration
AI_PROVIDERS = {
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
    'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY', ''),
    'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', ''),
    'REPLICATE_API_KEY': os.environ.get('REPLICATE_API_KEY', ''),
    'MISTRAL_API_KEY': os.environ.get('MISTRAL_API_KEY', ''),
    'COHERE_API_KEY': os.environ.get('COHERE_API_KEY', ''),
    'GROQ_API_KEY': os.environ.get('GROQ_API_KEY', ''),
    'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', ''),
    'RUNWAY_API_KEY': os.environ.get('RUNWAY_API_KEY', ''),
}

# Make Runway key directly accessible for video provider
RUNWAY_API_KEY = os.environ.get('RUNWAY_API_KEY', '')
RUNWAY_MOCK_MODE = os.environ.get('RUNWAY_MOCK_MODE', 'True') == 'True'  # Enable mock mode by default

# External Service API Keys (for non-LLM services)
EXTERNAL_API_KEYS = {
    'STABILITY_API_KEY': os.environ.get('STABILITY_API_KEY', ''),
    'RUNWAY_API_KEY': os.environ.get('RUNWAY_API_KEY', ''),
    'ELEVENLABS_API_KEY': os.environ.get('ELEVENLABS_API_KEY', ''),
    'GIPHY_API_KEY': os.environ.get('GIPHY_API_KEY', ''),
    'ALPHA_VANTAGE_API_KEY': os.environ.get('ALPHA_VANTAGE_API_KEY', ''),
    'POLYGON_API_KEY': os.environ.get('POLYGON_API_KEY', ''),
}

# AI Configuration
AI_CONFIG = {
    'DEFAULT_LLM_MODEL': 'gpt-5-mini',
    # GPT-5 Reasoning Configuration
    'GPT5_REASONING_LEVELS': ['minimal', 'low', 'medium', 'high'],
    'DEFAULT_REASONING_LEVEL': 'medium',
    # Token Limits
    'MAX_INPUT_TOKENS': {
        'gpt-5': 272000,
        'gpt-5-mini': 272000,
        'gpt-5-nano': 272000,
        'gpt-5-mini': 128000,
        'gpt-5-nano': 16385
    },
    'MAX_OUTPUT_TOKENS': {
        'gpt-5': 128000,
        'gpt-5-mini': 128000,
        'gpt-5-nano': 128000,
        'gpt-5-mini': 4096,
        'gpt-5-nano': 4096
    },
    # Prompt Caching
    'ENABLE_PROMPT_CACHING': True,
    'PROMPT_CACHE_TTL': 300,
    'GPT5_FALLBACK_MODEL': 'gpt-5-mini',
    'ENABLE_GPT5_MIGRATION': True,
}

# Self-Awareness & Intelligence Configuration
SELF_AWARENESS = {
    'ENABLE_SELF_AWARENESS': os.environ.get('ENABLE_SELF_AWARENESS', 'True') == 'True',
    'ENABLE_CODE_EMBEDDING': os.environ.get('ENABLE_CODE_EMBEDDING', 'True') == 'True',
    'ENABLE_SELF_MODIFICATION': os.environ.get('ENABLE_SELF_MODIFICATION', 'False') == 'True',
    'SCAN_INTERVAL': int(os.environ.get('SELF_AWARENESS_SCAN_INTERVAL', '3600')),
}

# Agent Orchestration Configuration
AGENT_ORCHESTRATION = {
    'MAX_CONCURRENT_AGENTS': int(os.environ.get('MAX_CONCURRENT_AGENTS', '100')),
    'AGENT_TIMEOUT_SECONDS': int(os.environ.get('AGENT_TIMEOUT_SECONDS', '300')),
    'ENABLE_CROSS_DOMAIN_AGENTS': os.environ.get('ENABLE_CROSS_DOMAIN_AGENTS', 'True') == 'True',
    'AGENT_REGISTRY_CACHE_TTL': int(os.environ.get('AGENT_REGISTRY_CACHE_TTL', '900')),
}

# WebSocket Security Configuration
def env_bool(key, default=False):
    """Helper to parse boolean environment variables"""
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes')

REQUIRE_WEBSOCKET_AUTH = env_bool('REQUIRE_WEBSOCKET_AUTH', not DEBUG)
ENABLE_WEBSOCKET_AUTH = env_bool('ENABLE_WEBSOCKET_AUTH', True)

# Sports Analytics Configuration
SPORTS_ANALYTICS = {
    'ENABLE_SPORTS_ANALYTICS': os.environ.get('ENABLE_SPORTS_ANALYTICS', 'True') == 'True',
    'CONFIDENCE_THRESHOLD': float(os.environ.get('SPORTS_CONFIDENCE_THRESHOLD', '0.6')),
    'MIN_EDGE': float(os.environ.get('SPORTS_MIN_EDGE', '0.04')),
    'MAX_CONCURRENT_ANALYSES': int(os.environ.get('SPORTS_MAX_CONCURRENT_ANALYSES', '5')),
}

# Content Generation Configuration
CONTENT_GENERATION = {
    'ENABLE_CONTENT_GENERATION': os.environ.get('ENABLE_CONTENT_GENERATION', 'True') == 'True',
    'MAX_TOKENS': int(os.environ.get('CONTENT_GENERATION_MAX_TOKENS', '4000')),
    'TEMPERATURE': float(os.environ.get('CONTENT_GENERATION_TEMPERATURE', '0.7')),
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Temporarily allow all requests
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# CORS Configuration
# SECURITY: Never use CORS_ALLOW_ALL_ORIGINS in production!
if DEBUG:
    # Development - allow specific origins only
    default_dev_origins = 'http://localhost:3000,http://localhost:8080,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174'
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', default_dev_origins).split(',')
    # SECURITY WARNING: Set to False for better security even in development
    CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'false').lower() == 'true'
else:
    # Production - strictly controlled origins
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else []
    CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production
    # Allow specific subdomains in production
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://.*\.donkeybetz\.com$",  # Allow all subdomains
        r"^https://.*\.vercel\.app$",      # Allow Vercel deployments
        r"^https://.*\.netlify\.app$",     # Allow Netlify deployments
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-client-version',  # Custom header from frontend
    'x-orchestrator',    # Custom header for orchestra
    'x-agent-request',   # Custom header for agent requests
    'x-orchestra-client',  # Custom header for agent orchestra client
    'x-dbao-client',     # Custom header for DBAO client
]

# CSRF Configuration  
if DEBUG:
    CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000,http://localhost:8080,http://localhost:5173').split(',')
else:
    # In production, trust HTTPS origins
    default_trusted = [
        'https://*.donkeybetz.com',
        'https://*.vercel.app', 
        'https://*.netlify.app'
    ]
    custom_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []
    CSRF_TRUSTED_ORIGINS = default_trusted + custom_origins

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # for any project-level static files
] if os.path.exists(BASE_DIR / 'static') else []

# WhiteNoise configuration for production
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG  # Only auto-refresh in debug mode
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.UnifiedUser'

# Authentication URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/intelligence/'
LOGOUT_REDIRECT_URL = '/'

# Development Tools
if DEBUG:
    ENABLE_DEBUG_TOOLBAR = os.environ.get('ENABLE_DEBUG_TOOLBAR', 'True') == 'True'

# Testing Configuration
TESTING_MODE = os.environ.get('TESTING_MODE', 'False') == 'True'

# Production-Grade Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/2')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Production Celery Broker Settings
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_CONNECTION_TIMEOUT = 5
CELERY_BROKER_HEARTBEAT = 120
CELERY_BROKER_POOL_LIMIT = 20
CELERY_RESULT_BACKEND_HEALTH_CHECK_INTERVAL = 30
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_debug.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'content': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# =============================================================================
# PRODUCTION SECURITY CONFIGURATION
# =============================================================================

# Import secure environment manager
try:
    from core.security import env, env_bool, env_int, env_list
except ImportError:
    # Fallback functions if security module isn't available
    def env(key, default=''):
        return os.environ.get(key, default)

    def env_bool(key, default=False):
        return os.environ.get(key, str(default)).lower() in ('true', '1', 'yes')

    def env_int(key, default=0):
        try:
            return int(os.environ.get(key, default))
        except (ValueError, TypeError):
            return default

    def env_list(key, default=None):
        if default is None:
            default = []
        value = os.environ.get(key, '')
        return value.split(',') if value else default

# =============================================================================
# PRODUCTION WEBSOCKET CONFIGURATION
# =============================================================================

# WebSocket connection settings for production stability
WEBSOCKET_CONNECTION_TIMEOUT = env_int('WEBSOCKET_CONNECTION_TIMEOUT', 60)
WEBSOCKET_HEARTBEAT_INTERVAL = env_int('WEBSOCKET_HEARTBEAT_INTERVAL', 30)
WEBSOCKET_MAX_CONNECTIONS = env_int('WEBSOCKET_MAX_CONNECTIONS', 1000)
WEBSOCKET_RECONNECT_INTERVAL = env_int('WEBSOCKET_RECONNECT_INTERVAL', 5)
WEBSOCKET_MAX_RETRIES = env_int('WEBSOCKET_MAX_RETRIES', 5)

# Redis persistence settings for production
REDIS_MAXMEMORY_POLICY = env('REDIS_MAXMEMORY_POLICY', 'allkeys-lru')
REDIS_SAVE_POLICY = env('REDIS_SAVE_POLICY', '900 1 300 10 60 10000')  # Background save
REDIS_APPENDONLY = env_bool('REDIS_APPENDONLY', True)  # Enable AOF
REDIS_APPENDFSYNC = env('REDIS_APPENDFSYNC', 'everysec')

# Security Headers and HTTPS
if not DEBUG:
    # HTTPS and Security Headers
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = env_int('SECURE_HSTS_SECONDS', 31536000)  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', True)
    
    # Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF = env_bool('SECURE_CONTENT_TYPE_NOSNIFF', True)
    SECURE_BROWSER_XSS_FILTER = env_bool('SECURE_BROWSER_XSS_FILTER', True)
    X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', 'DENY')
    
    # Cookie Security
    # For local development, we need to allow WebSocket cookies to work properly
    if DEBUG:
        SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP in development
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = 'Lax'  # Allow cookies in WebSocket connections
    else:
        SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', True)
        SESSION_COOKIE_HTTPONLY = env_bool('SESSION_COOKIE_HTTPONLY', True)
        SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', 'Strict')
    SESSION_COOKIE_AGE = env_int('SESSION_COOKIE_AGE', 1209600)  # 2 weeks
    SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool('SESSION_EXPIRE_AT_BROWSER_CLOSE', False)
    
    # CSRF Cookie Security
    if DEBUG:
        CSRF_COOKIE_SECURE = False  # Allow CSRF cookies over HTTP in development
        CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access in development for WebSocket
        CSRF_COOKIE_SAMESITE = 'Lax'  # Allow CSRF cookies in WebSocket connections
    else:
        CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', True)
        CSRF_COOKIE_HTTPONLY = env_bool('CSRF_COOKIE_HTTPONLY', True)
        CSRF_COOKIE_SAMESITE = env('CSRF_COOKIE_SAMESITE', 'Strict')
    CSRF_USE_SESSIONS = env_bool('CSRF_USE_SESSIONS', False)
    
    # Content Security Policy (CSP)
    CSP_DEFAULT_SRC = env_list('CSP_DEFAULT_SRC', ["'self'"])
    CSP_SCRIPT_SRC = env_list('CSP_SCRIPT_SRC', ["'self'", "'unsafe-inline'"])
    CSP_STYLE_SRC = env_list('CSP_STYLE_SRC', ["'self'", "'unsafe-inline'"])
    CSP_IMG_SRC = env_list('CSP_IMG_SRC', ["'self'", 'data:', 'https:'])
    CSP_FONT_SRC = env_list('CSP_FONT_SRC', ["'self'", 'data:'])
    CSP_CONNECT_SRC = env_list('CSP_CONNECT_SRC', ["'self'", 'ws:', 'wss:', 'https:'])
    CSP_FRAME_ANCESTORS = env_list('CSP_FRAME_ANCESTORS', ["'none'"])
    
    # Referrer Policy
    SECURE_REFERRER_POLICY = env('SECURE_REFERRER_POLICY', 'strict-origin-when-cross-origin')

# Enhanced Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': env_int('PASSWORD_MIN_LENGTH', 12),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Rate Limiting Configuration
RATE_LIMIT_ENABLED = env_bool('RATE_LIMIT_ENABLED', not DEBUG)
if RATE_LIMIT_ENABLED:
    RATELIMIT_ENABLE = True
    # RATELIMIT_VIEW = 'core.views.ratelimit_exceeded'  # Uncomment when view is created
    RATELIMIT_RATE = env('RATELIMIT_RATE', '100/h')  # Default: 100 requests per hour
    
    # Specific rate limits
    LOGIN_RATE_LIMIT = env('LOGIN_RATE_LIMIT', '5/m')  # 5 login attempts per minute
    API_RATE_LIMIT = env('API_RATE_LIMIT', '1000/h')  # 1000 API calls per hour
    REGISTER_RATE_LIMIT = env('REGISTER_RATE_LIMIT', '3/h')  # 3 registrations per hour

# Account Security
ACCOUNT_LOCKOUT_ATTEMPTS = env_int('ACCOUNT_LOCKOUT_ATTEMPTS', 5)
ACCOUNT_LOCKOUT_DURATION = env_int('ACCOUNT_LOCKOUT_DURATION', 1800)  # 30 minutes
PASSWORD_RESET_TIMEOUT = env_int('PASSWORD_RESET_TIMEOUT', 3600)  # 1 hour

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int('FILE_UPLOAD_MAX_MEMORY_SIZE', 5242880)  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = env_int('DATA_UPLOAD_MAX_MEMORY_SIZE', 5242880)  # 5MB
MAX_UPLOAD_SIZE = env_int('MAX_UPLOAD_SIZE', 10485760)  # 10MB

# Allowed file extensions for uploads
ALLOWED_UPLOAD_EXTENSIONS = env_list(
    'ALLOWED_UPLOAD_EXTENSIONS',
    ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.csv', '.json']
)

# Two-Factor Authentication
ENABLE_2FA = env_bool('ENABLE_2FA', False)
if ENABLE_2FA:
    INSTALLED_APPS += ['django_otp', 'django_otp.plugins.otp_totp']
    MIDDLEWARE += ['django_otp.middleware.OTPMiddleware']
    OTP_TOTP_ISSUER = env('2FA_ISSUER_NAME', 'Unified Donkey Betz')

# API Security
API_KEY_CUSTOM_HEADER = 'HTTP_X_API_KEY'
REQUIRE_API_KEY = env_bool('REQUIRE_API_KEY', not DEBUG)

# Audit Logging
ENABLE_AUDIT_LOG = env_bool('ENABLE_AUDIT_LOG', not DEBUG)
AUDIT_LOG_RETENTION_DAYS = env_int('AUDIT_LOG_RETENTION_DAYS', 90)

# Security Monitoring
ENABLE_SECURITY_MONITORING = env_bool('ENABLE_SECURITY_MONITORING', not DEBUG)
SECURITY_ALERT_EMAIL = env('SECURITY_ALERT_EMAIL', '')
FAILED_LOGIN_THRESHOLD = env_int('FAILED_LOGIN_THRESHOLD', 10)

# IP Whitelisting/Blacklisting
ENABLE_IP_FILTERING = env_bool('ENABLE_IP_FILTERING', False)
IP_WHITELIST = env_list('IP_WHITELIST', [])
IP_BLACKLIST = env_list('IP_BLACKLIST', [])

# Session Security
SESSION_SAVE_EVERY_REQUEST = env_bool('SESSION_SAVE_EVERY_REQUEST', True)
SESSION_COOKIE_NAME = env('SESSION_COOKIE_NAME', 'sessionid')
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# CSRF Protection
# CSRF_FAILURE_VIEW = 'core.views.csrf_failure'  # Uncomment when view is created
CSRF_COOKIE_NAME = env('CSRF_COOKIE_NAME', 'csrftoken')

# Clickjacking Protection
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', 'DENY')

# Host Header Validation
USE_X_FORWARDED_HOST = env_bool('USE_X_FORWARDED_HOST', False)
USE_X_FORWARDED_PORT = env_bool('USE_X_FORWARDED_PORT', False)

# SQL Injection Protection (already handled by Django ORM)
# XSS Protection (handled by Django templates and CSP)

# Directory Traversal Protection
DISALLOWED_USER_AGENTS = env_list('DISALLOWED_USER_AGENTS', [])

# Secure Random Number Generation
# Django uses os.urandom() by default which is cryptographically secure

# Backup and Recovery Configuration
if not DEBUG:
    BACKUP_ENABLED = env_bool('BACKUP_ENABLED', True)
    BACKUP_RETENTION_DAYS = env_int('BACKUP_RETENTION_DAYS', 30)
    BACKUP_ENCRYPTION_KEY = env('BACKUP_ENCRYPTION_KEY', '')

# Environment Validation
if env_bool('VALIDATE_ENVIRONMENT', not DEBUG):
    from core.security import validate_environment
    validation_results = validate_environment()
    if not validation_results['valid']:
        import warnings
        for error in validation_results['errors']:
            warnings.warn(f"SECURITY ERROR: {error}", RuntimeWarning)
        if not DEBUG:
            raise ImproperlyConfigured(
                "Security validation failed. Please fix the errors above."
            )

# =============================================================================
# ADDITIONAL SETTINGS FROM BACKEND/SETTINGS.PY
# =============================================================================

# Environment indicator
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development' if DEBUG else 'production')

# Agent System Configuration
AGENT_SYSTEM = {
    'ENABLED': os.environ.get('AGENT_SYSTEM_ENABLED', 'True') == 'True',
    'MAX_AGENTS': int(os.environ.get('MAX_AGENTS', '100')),
    'AGENT_TIMEOUT': int(os.environ.get('AGENT_TIMEOUT', '30')),
}

# Sports API Keys
SPORTRADAR_API_KEY = os.environ.get('SPORTRADAR_API_KEY', '')
SPORTSDB_API_KEY = os.environ.get('SPORTSDB_API_KEY', '')
THE_ODDS_API_KEY = os.environ.get('THE_ODDS_API_KEY', '')
ODDS_API_KEY = os.environ.get('ODDS_API_KEY', '')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')

# API Rate Limits
API_RATE_LIMITS = {
    'DEFAULT': '100/hour',
    'AUTHENTICATED': '1000/hour',
    'PREMIUM': '10000/hour',
}

# Additional Redis Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

# Redis key patterns for caching
REDIS_KEY_PATTERNS = {
    'agents': 'agents:*',
    'sports': 'sports:*',
    'content': 'content:*',
    'ml': 'ml:*',
}

# Celery Task Routing
CELERY_TASK_ROUTES = {
    'agents.*': {'queue': 'agents'},
    'sports.*': {'queue': 'sports'},
    'content.*': {'queue': 'content'},
    'ml.*': {'queue': 'ml'},
}

# Celery Worker Settings
CELERY_WORKER_CONCURRENCY = int(os.environ.get('CELERY_WORKER_CONCURRENCY', '4'))
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# DRF Spectacular Settings for API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Unified Donkey Betz API',
    'DESCRIPTION': 'Unified Platform API for Sports Analytics, AI Agents, and Content Generation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
