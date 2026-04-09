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
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# --- LLM Router defaults (prep only; no behavior change yet) ---
LLM_DEFAULT_PROVIDER = os.getenv("LLM_DEFAULT_PROVIDER", "openai")  # "openai" or "ollama"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

LLM_DEFAULTS = {
    "chat": {
        "ollama": os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:14b-instruct"),
        "openai": os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini"),
    },
    "embed": {
        "ollama": os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest"),
        "openai": os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large"),
    },
}

LLM_HTTP_TIMEOUT = int(os.getenv("LLM_HTTP_TIMEOUT", "30"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# Validate SECRET_KEY is secure
if not SECRET_KEY:
    if os.environ.get('DEBUG', 'False') == 'True':
        # In development, generate a random key if none provided (will change on restart)
        SECRET_KEY = get_random_secret_key()
    else:
        raise ValueError(
            "SECRET_KEY environment variable must be set in production. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
elif len(SECRET_KEY) < 50:
    raise ValueError(
        f"SECRET_KEY must be at least 50 characters (current: {len(SECRET_KEY)}). "
        "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
    )

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Dynamic ALLOWED_HOSTS for production
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Security: Prevent wildcard '*' in production
if not DEBUG and '*' in ALLOWED_HOSTS:
    raise ValueError(
        "ALLOWED_HOSTS cannot contain '*' in production (DEBUG=False). "
        "Please specify explicit hostnames in ALLOWED_HOSTS environment variable."
    )

if not DEBUG:
    # Add default production hosts if not already present
    default_production_hosts = [
        '.donkeybetz.com',    # Allow all subdomains
        '.vercel.app',        # Allow Vercel deployments
        '.netlify.app',       # Allow Netlify deployments
        '.herokuapp.com',     # Allow Heroku deployments
        '.railway.app',       # Allow Railway deployments
        '.up.railway.app',    # Allow Railway auto-generated domains
    ]
    for host in default_production_hosts:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

# Platform Configuration
PLATFORM_NAME = os.environ.get('PLATFORM_NAME', 'Unified Donkey Betz')

# Session 1069: Auto-detect Railway URLs from RAILWAY_PUBLIC_DOMAIN when env vars not set
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
_railway_base = f'https://{_railway_domain}' if _railway_domain else ''
FRONTEND_URL = os.environ.get('FRONTEND_URL', _railway_base or 'http://localhost:3000')
BACKEND_URL = os.environ.get('BACKEND_URL', _railway_base or 'http://localhost:8000')
WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL',
    f'wss://{_railway_domain}' if _railway_domain else 'ws://localhost:8001')

# Session 1064: Platform Hardening Configuration
LUNGS_ENFORCE_HARD_LIMIT = os.environ.get('LUNGS_ENFORCE_HARD_LIMIT', 'true').lower() == 'true'
CELERY_TASK_EVENT_RETENTION_DAYS = int(os.environ.get('CELERY_TASK_EVENT_RETENTION_DAYS', '30'))
LLM_CALL_LOG_RETENTION_DAYS = int(os.environ.get('LLM_CALL_LOG_RETENTION_DAYS', '30'))
BODY_THROTTLE_MAX_DELAY_SECONDS = int(os.environ.get('BODY_THROTTLE_MAX_DELAY_SECONDS', '30'))

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
    'django_celery_beat',      # Celery Beat scheduler for automated tasks
    'django_celery_results',   # Celery task result storage
    "pgvector",
    'cloudinary_storage',      # Session 857: Cloudinary storage for production media files
    # Core app only for now
    'core.apps.CoreConfig',    # Core utilities and management (Session 623: with startup health check)

    # Unified platform apps (will be created step by step)
    # 'gateway',                 # Unified API Gateway
    # 'memory',                  # Unified Memory System
    'agents',                  # Agent Registry & Orchestration
    'coleadership',            # AI-Human Co-Leadership System (Session 99)
    'rendering',               # Render Jobs & DaVinci Integration (Session 105)
    'pipelines',               # Creative Pipelines v1 - Template-Based Orchestration (Session 109)
    # 'ai_services',            # Multi-Provider AI Interface
    'ai_core.spiders',         # Spider Army System
    'ai_core',                 # AI Core app for agents, spiders, intelligence
    'ai_core.intelligence',    # AI Intelligence & Learning System (business logic + learning models)
    # 'intelligence_rt',         # Real-Time Intelligence Engine (Spider Quality + Action Plans + Income Tracking)
    'intelligence',            # Real-Time Intelligence Engine (Spider Quality + Action Plans + Income Tracking)
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
    'core.learning_bridges',  # Learning bridges for unified intelligence (NEW)
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
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection ENABLED
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.auth_middleware.UnifiedTokenAuthenticationMiddleware',  # Unified API auth with dev bypass
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Session 789: Disabled for Railway - internal services share IPs causing false rate limits
    # 'core.rate_limiter.RateLimitMiddleware',  # Global rate limiting
    # 'core.auth_middleware.RateLimitingMiddleware',  # Enhanced rate limiting
    'core.vip_middleware.VIPReadOnlyMiddleware',  # OVL: Block writes from VIP demo viewers
    'core.auth_middleware.APILoggingMiddleware',  # API request/response logging
    'core.middleware_error_capture.RequestErrorCaptureMiddleware',  # Session 1069: HTTP errors → PA telemetry
    'core.middleware.RangeRequestMiddleware',  # Session 111: HTTP range requests for video streaming

    # Unified platform middleware (will be created)
    # 'gateway.middleware.UnifiedAPIMiddleware',
    # 'monitoring.middleware.PerformanceMiddleware',
    # 'billing.middleware.UsageTrackingMiddleware',
]

ROOT_URLCONF = 'core.urls'

# Session 688: React frontend is now the primary UI
# Django templates deprecated - React build served from frontend/dist
REACT_BUILD_DIR = BASE_DIR / 'frontend' / 'dist'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(REACT_BUILD_DIR),
            str(BASE_DIR / 'ai_core' / 'templates'),
            str(BASE_DIR / 'core' / 'templates'),  # APP_DIRS backup
            '/app/frontend/dist',  # Railway absolute path
        ],
        'APP_DIRS': True,  # Also checks <app>/templates/ directories
        'OPTIONS': {
            'debug': DEBUG,
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

# Production-Grade Channels Configuration
# Use REDIS_URL for Railway, fallback to localhost for local dev
_redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
try:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [_redis_url],
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
    # Session 141: Set to 0 to fix Celery Beat database connection issues
    # Closes connections immediately instead of pooling them
    DATABASES['default']['CONN_MAX_AGE'] = 0
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
RUNWAY_MOCK_MODE = os.environ.get('RUNWAY_MOCK_MODE', 'False') == 'True'  # Production default: real mode

# DaVinci Resolve Bridge Configuration
# The bridge server runs alongside DaVinci Resolve and provides REST API access
DAVINCI_BRIDGE_URL = os.environ.get('DAVINCI_BRIDGE_URL', 'http://localhost:9090')
DAVINCI_BRIDGE_API_KEY = os.environ.get('DAVINCI_BRIDGE_API_KEY', 'dev-key-change-in-production')

# External Service API Keys (for non-LLM services)
EXTERNAL_API_KEYS = {
    'STABILITY_API_KEY': os.environ.get('STABILITY_API_KEY', ''),
    'RUNWAY_API_KEY': os.environ.get('RUNWAY_API_KEY', ''),
    'REPLICATE_API_KEY': os.environ.get('REPLICATE_API_TOKEN', ''),  # Character training via Replicate
    'REPLICATE_USERNAME': os.environ.get('REPLICATE_USERNAME', 'donkeybetz'),  # Replicate account username
    'ELEVENLABS_API_KEY': os.environ.get('ELEVENLABS_API_KEY', ''),
    'GIPHY_API_KEY': os.environ.get('GIPHY_API_KEY', ''),
    'ALPHA_VANTAGE_API_KEY': os.environ.get('ALPHA_VANTAGE_API_KEY', ''),
    'POLYGON_API_KEY': os.environ.get('POLYGON_API_KEY', ''),
}

# Discord Bot Configuration (Session 419+)
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '')

# AI Configuration
AI_CONFIG = {
    'DEFAULT_LLM_MODEL': 'gpt-5-mini',
    # GPT-5 Reasoning Configuration
    'GPT5_REASONING_LEVELS': ['minimal', 'low', 'medium', 'high'],
    'DEFAULT_REASONING_LEVEL': 'medium',
    # Token Limits
    'MAX_INPUT_TOKENS': {
        'gpt-5': 272000,
        'gpt-5-mini': 128000,
        'gpt-5-nano': 16385,
    },
    'MAX_OUTPUT_TOKENS': {
        'gpt-5': 128000,
        'gpt-5-mini': 4096,
        'gpt-5-nano': 4096,
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
# Session 115: Production-ready mobile authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Mobile apps: Token auth without CSRF (X-API-Key header)
        'core.mobile_authentication.MobileTokenAuthentication',
        # Web browsers: Session auth that skips CSRF when token is present
        'core.mobile_authentication.CsrfExemptSessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require authentication by default
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    # Session 789: Disabled throttling for Railway deployment
    # All internal services share IPs, causing false rate limits
    # TODO: Implement IP whitelist for internal services instead
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100000/hour',
        'user': '500000/hour',
        'rag_ingest': '20/hour',
        'video_ingest': '5/hour',
        'review': '60/minute',
        'review_feedback': '10/minute',
    }
}

# CORS Configuration
# SECURITY: Never use CORS_ALLOW_ALL_ORIGINS in production!
if DEBUG:
    # Development - allow specific origins only
    default_dev_origins = 'http://localhost:3000,http://localhost:8080,http://localhost:8888,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3000,http://127.0.0.1:8888,http://127.0.0.1:5173,http://127.0.0.1:5174'
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', default_dev_origins).split(',')
    # SECURITY WARNING: Set to False for better security even in development
    CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'false').lower() == 'true'
else:
    # Production - strictly controlled origins
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else []
    CORS_ALLOW_ALL_ORIGINS = False  # Never allow all origins in production
    # Allow specific subdomains in production
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://.*\.donkeybetz\.com$",     # Allow all subdomains
        r"^https://.*\.vercel\.app$",         # Allow Vercel deployments
        r"^https://.*\.netlify\.app$",        # Allow Netlify deployments
        r"^https://.*\.railway\.app$",        # Allow Railway deployments
        r"^https://.*\.up\.railway\.app$",    # Allow Railway auto-generated domains
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
        'https://*.netlify.app',
        'https://*.railway.app',
        'https://*.up.railway.app',
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
TIME_ZONE = 'America/Denver'  # MST/MDT - Session 210: Local timezone for temporal recommendations
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Session 688: Include React build assets
# Use tuple format (prefix, path) to serve /static/assets/ from frontend/dist/assets/
_staticfiles_dirs = []
if os.path.exists(BASE_DIR / 'frontend' / 'dist' / 'assets'):
    _staticfiles_dirs.append(('assets', BASE_DIR / 'frontend' / 'dist' / 'assets'))
if os.path.exists(BASE_DIR / 'static'):
    _staticfiles_dirs.append(BASE_DIR / 'static')
STATICFILES_DIRS = _staticfiles_dirs

# WhiteNoise configuration for production
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG  # Only auto-refresh in debug mode
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary configuration (Session 176)
# Used for publicly accessible URLs (required by external APIs like Sync Labs)
import cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'donkeybetz'),
    api_key=os.environ.get('CLOUDINARY_API_KEY', ''),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET', ''),
    secure=True
)

# Session 857: Configure Cloudinary as default storage for production
# This fixes "Permission denied: /app/media" errors in Railway containers
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    # Required settings for django-cloudinary-storage
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', 'donkeybetz'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.UnifiedUser'

# Authentication URLs
# Session 688: Login URL points to React login page
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dashboard'
LOGOUT_REDIRECT_URL = '/login'

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
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Session 984: Reduced from 4 to limit memory pressure
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_RESULT_EXPIRES = 3600  # 1 hour — prevent Redis bloat from uncollected results

# Session 984: Worker memory management
# Railway (Linux): Procfile uses --pool=prefork for memory recycling via max-tasks-per-child
# macOS local: Use --pool=threads via Makefile (prefork causes SIGSEGV on macOS)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50  # Recycle prefork children after 50 tasks
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 300_000  # 300MB per child (KB), kills bloated children
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 min soft limit (warn before 30 min hard kill)

# ── Session 1074: Executor Settings ──────────────────────────────────────────
# Single-repo MVP — pinned to this repo and main branch.
EXECUTOR_SINGLE_REPO_MODE = True
EXECUTOR_DEFAULT_REPO_NAME = 'donkey-betz-platform'
EXECUTOR_REPO_URL = os.environ.get(
    'EXECUTOR_REPO_URL', 'https://github.com/clwest/donkey-betz-platform'
)
EXECUTOR_DEFAULT_BASE_BRANCH = 'main'
EXECUTOR_PROTECTED_BRANCHES = ['main', 'production']
EXECUTOR_NETWORK_EGRESS_DEFAULT = False
EXECUTOR_MAX_RUN_SECONDS = int(os.environ.get('EXECUTOR_MAX_RUN_SECONDS', '1800'))
EXECUTOR_WORKDIR_ROOT = os.environ.get(
    'EXECUTOR_WORKDIR_ROOT', os.path.join(BASE_DIR, '.executor_runs')
)
# When True, the Tier A/B/C pattern classifier gates steps (Tier B → approval).
# When False (default), only explicit requires_approval and network:on trigger approval.
EXECUTOR_CLASSIFIER_GATING_ENABLED = os.environ.get(
    'EXECUTOR_CLASSIFIER_GATING_ENABLED', 'false'
).lower() == 'true'

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

# =============================================================================
# Session 562: Web Push Notifications (VAPID)
# =============================================================================
# VAPID (Voluntary Application Server Identification) keys for Web Push API
# These enable browser push notifications for arbitrage alerts and other events

VAPID_PUBLIC_KEY = env('VAPID_PUBLIC_KEY', 'BFoZhpwPq8Ioe1RW1oXsKSRI8jklazhBxJIh03ipg-aiBy1xLQS0q5KEmSjx-vvZ7j8iaVdiE5-yMVhV-tiVSHI')
VAPID_PRIVATE_KEY = env('VAPID_PRIVATE_KEY', '263F9LYf3-EQ408J2M8l0qDXi77QMmbgMPxGnDmNuis')
VAPID_ADMIN_EMAIL = env('VAPID_ADMIN_EMAIL', 'admin@donkeybetz.com')

# Push notification settings
PUSH_NOTIFICATIONS_ENABLED = env_bool('PUSH_NOTIFICATIONS_ENABLED', True)
PUSH_ARB_MIN_PROFIT_DEFAULT = 1.0  # Default minimum profit % for arb alerts

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
# Session 789: Disabled for Railway - internal services share IPs causing false limits
# Set RATE_LIMIT_ENABLED=True in Railway env vars to re-enable after fixing IP whitelisting
RATE_LIMIT_ENABLED = env_bool('RATE_LIMIT_ENABLED', False)

# Centralized rate limit configuration (requests per window in seconds)
# Used by core/rate_limiter.py and core/decorators.py
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 60},  # 100 requests per minute
    'ai_generation': {'requests': 10, 'window': 60},  # 10 AI calls per minute
    'video_processing': {'requests': 5, 'window': 60},  # 5 video ops per minute
    'image_processing': {'requests': 20, 'window': 60},  # 20 image ops per minute
    'api_expensive': {'requests': 20, 'window': 60},  # 20 expensive ops per minute
    'auth_login': {'requests': 5, 'window': 300},  # 5 login attempts per 5 minutes
    'auth_register': {'requests': 3, 'window': 3600},  # 3 registrations per hour
    'auth_password_reset': {'requests': 3, 'window': 3600},  # 3 resets per hour
}

if RATE_LIMIT_ENABLED:
    RATELIMIT_ENABLE = True
    # RATELIMIT_VIEW = 'core.views.ratelimit_exceeded'  # Uncomment when view is created
    RATELIMIT_RATE = env('RATELIMIT_RATE', '100/h')  # Default: 100 requests per hour

    # Specific rate limits (legacy format)
    LOGIN_RATE_LIMIT = env('LOGIN_RATE_LIMIT', '5/m')  # 5 login attempts per minute
    API_RATE_LIMIT = env('API_RATE_LIMIT', '1000/h')  # 1000 API calls per hour
    REGISTER_RATE_LIMIT = env('REGISTER_RATE_LIMIT', '3/h')  # 3 registrations per hour

# Account Security
ACCOUNT_LOCKOUT_ATTEMPTS = env_int('ACCOUNT_LOCKOUT_ATTEMPTS', 5)
ACCOUNT_LOCKOUT_DURATION = env_int('ACCOUNT_LOCKOUT_DURATION', 1800)  # 30 minutes
PASSWORD_RESET_TIMEOUT = env_int('PASSWORD_RESET_TIMEOUT', 3600)  # 1 hour

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int('FILE_UPLOAD_MAX_MEMORY_SIZE', 104857600)  # 100MB (video support)
DATA_UPLOAD_MAX_MEMORY_SIZE = env_int('DATA_UPLOAD_MAX_MEMORY_SIZE', 104857600)  # 100MB (video support)
MAX_UPLOAD_SIZE = env_int('MAX_UPLOAD_SIZE', 104857600)  # 100MB
VIDEO_INGEST_MAX_SIZE = env_int('VIDEO_INGEST_MAX_SIZE', 104857600)  # 100MB

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

# Sports API Keys
SPORTRADAR_API_KEY = os.environ.get('SPORTRADAR_API_KEY', '')
SPORTSDB_API_KEY = os.environ.get('SPORTSDB_API_KEY', '')
THE_ODDS_API_KEY = os.environ.get('THE_ODDS_API_KEY', '')
ODDS_API_KEY = os.environ.get('ODDS_API_KEY', '')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')

# Additional Redis Configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

# Celery Task Routing
# Session 573: Added dedicated queues to prevent bottlenecks
# - long_running: Tasks that take 1+ minutes (spider network, agent conversations, dreams)
# - broadcast: High-frequency status broadcast tasks (every 60-180s)
# - default: Everything else (quick tasks)
CELERY_TASK_ROUTES = {
    # Remote Code Worker
    'core.tasks.execute_code_job': {'queue': 'code_jobs'},
    # Existing module-based routing
    'agents.*': {'queue': 'agents'},
    'sports.*': {'queue': 'default'},
    'content.*': {'queue': 'content'},
    'ml.*': {'queue': 'ml'},
    # Session 1066: Route to long_running — loads torch/transformers via AIIncomeBuilder→MLEngine
    'intelligence.tasks.monitor_and_process_opportunities': {'queue': 'long_running'},
    'intelligence.*': {'queue': 'long_running'},  # Session 884: Intelligence tasks are long-running

    # Session 573: Long-running tasks — heavy memory (ML models, coordinators)
    'core.tasks.run_spider_network': {'queue': 'long_running'},
    'core.tasks.generate_agent_dreams': {'queue': 'long_running'},
    'core.tasks.run_autonomous_intelligence_loop': {'queue': 'long_running'},
    'core.tasks.run_agent_learning_cycle': {'queue': 'long_running'},
    'core.tasks.score_and_promote_dreams': {'queue': 'long_running'},
    'core.tasks.process_approved_dreams': {'queue': 'default'},  # 171ms avg, 348/day — lightweight dispatcher
    # Session 1004: Moved I/O-bound LLM API tasks off long_running (was saturating c=1)
    # Session 1034: Moved run_agent_conversation back to long_running — max 72min, OOM on 200MB default worker
    'core.tasks.run_agent_conversation': {'queue': 'long_running'},
    'core.tasks.run_multi_agent_conversation': {'queue': 'long_running'},  # Session 1029: OOM fix — loads 30 agents
    'core.tasks.run_autonomous_thinking_cycle': {'queue': 'long_running'},  # Session 1029: OOM fix — heavy context gather
    'core.tasks.trigger_spider_conversations': {'queue': 'default'},
    'core.tasks.trigger_project_research': {'queue': 'default'},
    'core.tasks.agent_think_and_synthesize': {'queue': 'default'},
    # Session 1034: Route heavy tasks that were falling through to default queue
    'core.tasks.run_triggered_conversation': {'queue': 'long_running'},  # LLM conversation, max 471s
    # Session 1040: Moved 3 heavy tasks off content → long_running to fix OOM
    # Content worker was crashing with 25+ completed initiatives driving heavy LLM tasks
    'core.tasks.generate_initiative_stage_document': {'queue': 'long_running'},  # TechnicalDocumentAgent, heavy context build
    'core.tasks.execute_approved_artifacts': {'queue': 'default'},  # Fan-out dispatcher (<1s), moved off long_running to reduce saturation
    'core.tasks.execute_single_artifact': {'queue': 'default'},  # p50=86ms, 5700 runs/day — lightweight, was saturating long_running
    'core.tasks.generate_pending_reviews': {'queue': 'long_running'},  # LLM review generation, max 254s
    # Session 1000: Intelligence desks — 4 coordinators, heavy memory
    'core.tasks.run_all_desks_intelligence': {'queue': 'long_running'},
    # Session 1004: Moved heartbeat + nervous off long_running to unblock desk intelligence.
    # broadcast worker uses --pool=threads, so SentenceTransformer loads once and threads share it.
    'core.tasks.run_heartbeat': {'queue': 'broadcast'},
    'core.tasks.check_nervous': {'queue': 'broadcast'},
    # Session 885: Content generation tasks - dedicated content worker
    'core.tasks.generate_self_blog_task': {'queue': 'content'},
    'core.tasks.generate_self_blog_deliberation_task': {'queue': 'content'},
    'core.tasks.generate_operator_edge_newsletter': {'queue': 'content'},
    'core.tasks.generate_blog_with_topic_task': {'queue': 'content'},  # Session 1057
    'core.tasks.summarize_conversation_task': {'queue': 'content'},
    'core.tasks.execute_initiative_stage_task': {'queue': 'long_running'},  # Session 1040: Heavy LLM pipeline execution
    'core.tasks.advance_initiative_pipeline': {'queue': 'content'},
    'core.tasks.auto_kickstart_stuck_initiatives': {'queue': 'content'},
    'core.tasks.execute_dream_implementations': {'queue': 'long_running'},  # Session 1040: Heavy LLM processing
    # Session 1009: Removed 4 phantom routes (tasks don't exist):
    #   autonomous_studio.run_main_loop, generate_podcast_task, generate_image_task, generate_video_task
    'content.tasks.poll_pending_trainings': {'queue': 'content'},
    # Session 1009: Moved workspace/rotation tasks from content → long_running
    # These run ALL agents in a category (~20-74 agents) and caused OOM on content worker (512MB).
    # .delay() calls in views_platform_command.py and views_workspace_triggers.py route via
    # CELERY_TASK_ROUTES, so they must point to long_running (not content).
    'core.tasks.run_source_pack_workflow': {'queue': 'content'},
    'core.tasks.agent_daily_summary': {'queue': 'long_running'},
    'core.tasks.agent_workspace_status_report': {'queue': 'long_running'},
    'core.tasks.agent_research_to_workspace': {'queue': 'long_running'},
    'core.tasks.agent_content_to_workspace': {'queue': 'long_running'},
    'core.tasks.universal_agent_workspace_output': {'queue': 'long_running'},
    'core.tasks.agent_category_rotation': {'queue': 'default'},  # 149ms avg, 301/day — lightweight
    'core.tasks.full_agent_rotation': {'queue': 'long_running'},
    'autonomous.blockchain_security_monitor': {'queue': 'agents'},  # Session 1004: LLM API calls
    # Session 989: Removed phantom autonomous.stock_market_intelligence routing (task didn't exist)

    # Session 1031: Dream surfacing — lightweight DB queries only
    'core.tasks.surface_top_dreams': {'queue': 'default'},

    # Session 1065: Move heavy tasks off default queue to prevent celery-worker OOM
    # auto_process_extracted_artifacts: iterates up to 42K+ artifacts in batches of 2000
    # process_gates_and_deploy_pilots: instantiates OpenAI() per gate for doc generation
    # record_all_user_style_evolution: loads ALL active users × 3 domains with LearningService
    # ai_promote_decisions: GPT-5-mini batch of 50 decisions
    # send_personalized_opportunity_alerts: N users × N opportunities loop
    # update_learning_profiles: iterates ALL users with distributions
    # validate_knowledge_sources: iterates 3900+ unvalidated sources
    'core.tasks.auto_process_extracted_artifacts': {'queue': 'long_running'},
    'core.tasks.process_gates_and_deploy_pilots': {'queue': 'long_running'},
    'core.tasks.record_all_user_style_evolution': {'queue': 'long_running'},
    'core.tasks.ai_promote_decisions': {'queue': 'long_running'},
    'core.tasks.send_personalized_opportunity_alerts': {'queue': 'long_running'},
    'core.tasks.update_learning_profiles': {'queue': 'long_running'},
    'core.tasks.validate_knowledge_sources': {'queue': 'long_running'},

    # Session 1066: Move remaining heavy unrouted tasks off default queue
    # These were falling through to celery-worker (512MB) and piling up at peak times
    # LLM / heavy iteration tasks → long_running (c=1, 512MB, recycled aggressively)
    'core.tasks.run_daily_learning_pipeline': {'queue': 'long_running'},  # Chains 5 sub-tasks, loads all users
    'core.tasks.execute_pending_opportunity_tasks': {'queue': 'long_running'},  # Runs agents per opportunity
    'core.tasks.agent_think_and_synthesize': {'queue': 'long_running'},  # LLM synthesis per agent
    'core.tasks.discover_success_patterns': {'queue': 'long_running'},  # Iterates all distributions × 90 days
    'core.tasks.generate_user_insights': {'queue': 'long_running'},  # LLM insight generation per user
    'core.tasks.run_proactive_system_check': {'queue': 'long_running'},  # Chains alerts + suggestions + automations
    'core.tasks.generate_smart_suggestions': {'queue': 'long_running'},  # LLM suggestion generation
    'core.tasks.score_opportunities_from_spider_data': {'queue': 'long_running'},  # Scores up to 100 spider items
    'core.tasks.process_gate_progression': {'queue': 'default'},  # 472ms avg, 348/day — DB operations, not memory-heavy
    'core.tasks.generate_human_attention_items': {'queue': 'default'},  # 274ms avg, 348/day — DB scan, lightweight
    # Content pipeline tasks that call LLM → content worker
    'core.tasks.reevaluate_enhanced_blogs': {'queue': 'content'},  # PublishGate LLM calls per blog
    'core.tasks.evaluate_unscored_blogs': {'queue': 'content'},  # PublishGate LLM calls per blog
    'core.tasks.auto_enhance_blogs': {'queue': 'content'},  # EditorAgent LLM per blog
    'core.tasks.score_unscored_deliverables': {'queue': 'content'},  # Quality scoring

    # Session 1066b: Tasks caught by telemetry spiking on celery-worker
    # send_proactive_opportunity_alerts: 3GB spike — N users × N opportunities loop
    # poll_processing_videos: 1.2GB spike — video processing accumulates responses
    # aggregate_tool_call_stats: 480MB spike — scans all ToolCallRecord rows
    # apply_mood_trigger_rules: 385MB spike — lightweight but triggers on default
    # check_workflow_schedules/sync_workflow_schedules: workflow iteration
    'core.tasks.send_proactive_opportunity_alerts': {'queue': 'default'},  # 209ms avg, 174/day — lightweight
    'core.tasks.poll_processing_videos': {'queue': 'content'},
    'core.tasks.aggregate_tool_call_stats': {'queue': 'long_running'},
    'core.tasks.apply_mood_trigger_rules': {'queue': 'broadcast'},
    'core.tasks.check_workflow_schedules': {'queue': 'broadcast'},
    'core.tasks.sync_workflow_schedules': {'queue': 'broadcast'},

    # Session 1064: Telemetry cleanup — weekly DB deletes, safe on broadcast worker
    'core.tasks.cleanup_celery_task_events': {'queue': 'broadcast'},
    'core.tasks.cleanup_llm_call_logs': {'queue': 'broadcast'},

    # Session 976: PA chat — dedicated queue so user isn't blocked by spider/body-system traffic
    'core.tasks.process_pa_chat_task': {'queue': 'pa'},

    # Session 573: High-frequency broadcast tasks (60-180s) - separate worker
    'core.tasks.broadcast_learning_status': {'queue': 'broadcast'},
    'core.tasks.summarize_learning_readback': {'queue': 'broadcast'},
    'core.tasks.cleanup_learning_readback_events': {'queue': 'broadcast'},
    'core.tasks.broadcast_conversation_status': {'queue': 'broadcast'},
    'core.tasks.broadcast_dream_journal': {'queue': 'broadcast'},
    'core.tasks.broadcast_relationship_status': {'queue': 'broadcast'},
    'core.tasks.broadcast_evolution_status': {'queue': 'broadcast'},
    'core.tasks.process_realtime_scoring_queue': {'queue': 'broadcast'},
    'core.tasks.process_event_bus_scoring_queue': {'queue': 'broadcast'},
    'core.tasks.process_event_bus_validation_queue': {'queue': 'broadcast'},
    'core.tasks.process_event_bus_analytics_queue': {'queue': 'broadcast'},
    'core.tasks.refresh_system_state_cache': {'queue': 'broadcast'},  # Session 573: PA system awareness

    # Session 1000C: Move heavy tasks off celery-worker (default queue) to prevent OOM
    # Embedding backfills — call OpenAI API, process hundreds of items per run
    'core.tasks.backfill_spider_embeddings': {'queue': 'ml'},
    'core.tasks.backfill_memory_embeddings': {'queue': 'ml'},
    'core.tasks.backfill_conversation_embeddings': {'queue': 'ml'},
    # ML prediction enrichment — calls OpenAI embedding API per item
    'core.tasks.enrich_boardroom_ml_predictions': {'queue': 'ml'},
    # Session 1004: Pipeline execution tasks — LLM calls
    'core.tasks.process_high_scoring_opportunities': {'queue': 'default'},
    'core.tasks.process_spider_actions': {'queue': 'default'},
    'core.tasks.process_hivemind_sessions': {'queue': 'long_running'},  # Session 1029: OOM fix — orchestration heavy
    'core.tasks.execute_approved_dreams_via_orchestration': {'queue': 'long_running'},  # Session 1029: OOM fix — up to 10 dreams
    # Content pipeline tasks
    'core.tasks.process_content_ideas': {'queue': 'content'},
    'core.tasks.generate_weekly_opportunity_digest': {'queue': 'content'},
    # ai_core tasks — scrape external sites, initialize spiders
    # Session 1004: Moved scraping off long_running — I/O-bound, not memory-bound.
    'ai_core.tasks.collect_real_opportunities': {'queue': 'default'},
    'ai_core.tasks.refresh_ai_content_opportunities': {'queue': 'default'},
    'ai_core.tasks.warm_up_spider_network': {'queue': 'long_running'},  # Session 1029: OOM fix — initializes 77 spiders
    # Session 1004: Agent exercise tasks — LLM API calls, moved to agents queue
    'core.tasks.run_market_monitoring_agents': {'queue': 'agents'},
    'core.tasks.run_blockchain_monitoring_agents': {'queue': 'agents'},
    'core.tasks.run_business_strategy_agents': {'queue': 'agents'},
    'core.tasks.run_content_creation_agents': {'queue': 'agents'},
    'core.tasks.run_strategy_marketing_agents': {'queue': 'agents'},
    'core.tasks.run_research_analysis_agents': {'queue': 'agents'},
    'core.tasks.run_stock_financial_agents': {'queue': 'agents'},
    'core.tasks.run_prediction_market_agents': {'queue': 'agents'},
    'core.tasks.run_narrative_culture_agents': {'queue': 'agents'},
    'core.tasks.run_development_tech_agents': {'queue': 'agents'},
    'core.tasks.run_executive_leadership_agents': {'queue': 'agents'},
    'core.tasks.run_podcast_debate_agents': {'queue': 'agents'},
    'core.tasks.run_content_studio_agents': {'queue': 'agents'},
    'core.tasks.run_campaign_series_agents': {'queue': 'agents'},
    'core.tasks.run_system_orchestration_agents': {'queue': 'agents'},
    'core.tasks.run_quality_audit_agents': {'queue': 'agents'},
    'core.tasks.run_specialty_agents': {'queue': 'agents'},
    'core.tasks.exercise_all_dormant_agents': {'queue': 'agents'},
    'core.tasks.auto_generate_podcast_episode': {'queue': 'content'},
    # Session 1004: Autonomous situations — LLM API calls, moved to agents queue
    'core.tasks.run_design_trends_monitor': {'queue': 'agents'},
    'core.tasks.run_viral_content_predictor': {'queue': 'agents'},
    'core.tasks.run_job_match_intelligence': {'queue': 'agents'},
    'core.tasks.run_side_hustle_detector': {'queue': 'agents'},
    'core.tasks.run_crypto_sentiment_monitor': {'queue': 'agents'},
    'core.tasks.run_tech_stack_tracker': {'queue': 'agents'},
    'core.tasks.run_ai_model_monitor': {'queue': 'agents'},
    'core.tasks.run_case_law_monitor': {'queue': 'agents'},
    'core.tasks.run_regulatory_change_detector': {'queue': 'agents'},
    'core.tasks.run_thumbnail_optimizer': {'queue': 'agents'},
    'core.tasks.run_freelance_opportunity_scout': {'queue': 'agents'},
    'core.tasks.run_sec_filing_analyzer': {'queue': 'agents'},
    'core.tasks.run_earnings_predictor': {'queue': 'agents'},
    'core.tasks.run_skill_gap_analyzer': {'queue': 'agents'},
    # ML scoring tasks — load ML models
    'core.tasks.train_ml_scoring_model': {'queue': 'ml'},
    'core.tasks.evaluate_ml_model_performance': {'queue': 'ml'},
    'core.tasks.process_batch_scoring_queue': {'queue': 'ml'},
    # Session 1004: Market intelligence desk — LLM calls, moved to agents
    'core.tasks.run_market_intelligence_desk': {'queue': 'agents'},
    'core.tasks.check_market_events_and_rerun': {'queue': 'agents'},
    # Betting tasks — light DB queries, keep on sports worker
    'core.tasks.snapshot_odds_for_line_movement': {'queue': 'sports'},
    'core.tasks.scan_arbs_and_notify': {'queue': 'sports'},
    'core.tasks.verify_betting_outcomes': {'queue': 'sports'},
    'core.tasks.generate_daily_betting_brief': {'queue': 'sports'},
    'core.tasks.evaluate_ml_predictions': {'queue': 'sports'},
    # Initiative pipeline tasks
    'core.tasks.process_initiative_auto_progression': {'queue': 'content'},
    'core.tasks.evaluate_unscored_blogs': {'queue': 'content'},
    # Session 1004: Content Review Automation Pipeline — LLM calls, moved to content
    # Session 1009: Removed phantom enhance_all_blogs_needing_enhancement (task doesn't exist)
    'core.tasks.reevaluate_enhanced_blogs': {'queue': 'content'},  # PublishGate = heuristic only
    'core.tasks.auto_publish_approved_blogs': {'queue': 'content'},  # Simple status update
    # Session 1004: Narrative/pipeline module tasks — LLM calls, moved to default
    'narrative_drift.run_detector_cycle': {'queue': 'default'},
    'narrative_drift.process_spider_data': {'queue': 'default'},
    'narrative_drift.update_narrative_statuses': {'queue': 'default'},
    'narrative_drift.send_daily_digest': {'queue': 'default'},
    'narrative_drift.process_shifts_for_content': {'queue': 'content'},
    'unified_pipeline.run_complete_cycle': {'queue': 'default'},
    'unified_pipeline.health_check': {'queue': 'default'},
    # Session 1009: Removed phantom autonomous_studio.track_performance (task doesn't exist)
    # Session 1028: Route unrouted tasks off celery-worker to prevent OOM
    # These 7 tasks had no routing and all landed on default queue,
    # causing repeated OOM crashes (4 restarts in 2 hours).
    'core.tasks.check_celery_health': {'queue': 'broadcast'},
    'core.tasks.check_orphan_deliverables': {'queue': 'broadcast'},
    'core.tasks.enforce_db_retention': {'queue': 'long_running'},  # Daily cleanup, may take a few minutes
    'core.tasks.claude_code_agent_respond': {'queue': 'pa'},  # Fast response, same queue as PA
    'core.tasks.claude_code_engineer_task': {'queue': 'code_jobs'},  # Heavy engineering — dedicated worker
    'core.tasks.process_core_spider_data': {'queue': 'default'},  # p50=155ms, 2610 runs/day — lightweight, moved off long_running
    'core.tasks.batch_extract_artifacts': {'queue': 'long_running'},
    'core.tasks.collect_kalshi_prediction_markets': {'queue': 'long_running'},
    'core.tasks.run_stock_audit_cycle': {'queue': 'long_running'},
    'core.tasks.process_agent_activity_xp': {'queue': 'broadcast'},
    'core.tasks.monitor_running_experiments': {'queue': 'broadcast'},
    # Session 1043: Route heavy unrouted tasks off celery-worker (200MB) to prevent OOM
    # execute_agent_task loads AgentRouter (all 92 agents, ~300-500MB)
    'core.tasks.execute_agent_task': {'queue': 'long_running'},
    'core.tasks.create_talking_video_task': {'queue': 'agents'},
    # Spider tasks instantiate SpiderRegistry + fetch/scrape
    'core.tasks.run_spider_by_category': {'queue': 'long_running'},
    'core.tasks.execute_single_spider': {'queue': 'long_running'},
    'core.tasks.execute_single_spider_lightweight': {'queue': 'long_running'},
    # Content orchestration — multi-agent LLM calls
    'core.tasks.produce_content_package': {'queue': 'long_running'},
    # Hive mind — OpenAI API calls for 10+ agents
    'core.tasks.run_hive_mind_session': {'queue': 'long_running'},
    # Dream exploration — LLM calls
    'core.tasks.explore_dream_topic': {'queue': 'long_running'},
    # Pilot evaluation — ThinkingAgent LLM calls
    'core.tasks.evaluate_pilots_with_thinking_agent': {'queue': 'long_running'},
    # Learning loop — orchestrator data extraction
    'core.tasks.run_learning_loop_cycle': {'queue': 'long_running'},

    # Session 1063: Route body system checks to broadcast — high-frequency (60s-5min),
    # lightweight DB queries, were pounding the 200MB default worker
    'core.tasks.coordinate_body': {'queue': 'broadcast'},
    'core.tasks.check_breathing': {'queue': 'broadcast'},
    'core.tasks.check_circulation': {'queue': 'broadcast'},
    'core.tasks.check_spine_alignment': {'queue': 'broadcast'},
    'core.tasks.immune_scan': {'queue': 'broadcast'},
    'core.tasks.check_digestion': {'queue': 'broadcast'},
    'core.tasks.check_muscular': {'queue': 'broadcast'},
    'core.tasks.check_brain': {'queue': 'broadcast'},
    'core.tasks.check_skin': {'queue': 'broadcast'},
    'core.tasks.check_orchestration_timeouts': {'queue': 'broadcast'},
    'core.tasks.check_orchestration_auto_approvals': {'queue': 'broadcast'},

    # Session 1063: Route heavy LLM/agent tasks off default queue to prevent OOM
    'core.tasks.process_spider_data_automatic': {'queue': 'long_running'},
    'core.tasks.run_autonomy_cycle': {'queue': 'long_running'},
    'core.tasks.market_intelligence_scan': {'queue': 'long_running'},
    'core.tasks.run_stock_market_intelligence': {'queue': 'long_running'},
    'core.tasks.check_content_diversity': {'queue': 'long_running'},
    'core.tasks.run_daily_intelligence_digest': {'queue': 'long_running'},
    'core.tasks.auto_resolve_knowledge_gaps': {'queue': 'default'},  # 186ms avg, 840/day — lightweight
    'core.tasks.mine_learning_patterns': {'queue': 'long_running'},
    'core.tasks.run_system_self_audit': {'queue': 'long_running'},
    'core.tasks.generate_weekly_intelligence_brief': {'queue': 'long_running'},
    'core.tasks.generate_weekly_synthesis': {'queue': 'long_running'},
    'core.tasks.run_project_learning_cycle': {'queue': 'long_running'},
    'core.tasks.run_metrics_action_check': {'queue': 'long_running'},
    'core.tasks.market_movement_alerts': {'queue': 'long_running'},
    'core.tasks.check_sec_filings_alert': {'queue': 'long_running'},
    'core.tasks.workspace_autopilot_tick': {'queue': 'long_running'},
    'core.tasks.dispatch_pending_action_items': {'queue': 'default'},  # 192ms avg, 174/day — lightweight
    'core.tasks.aggregate_spider_signals': {'queue': 'long_running'},
    'core.tasks.process_pending_auto_topics': {'queue': 'long_running'},

    # Session 1063: Route embedding tasks to ml queue
    'core.tasks.embed_agent_activity': {'queue': 'ml'},
    'core.tasks.embed_daily_agent_learning': {'queue': 'ml'},
    'core.tasks.generate_document_embeddings': {'queue': 'ml'},
    'core.tasks.ingest_video_task': {'queue': 'long_running'},
    'core.tasks.youtube_whisper_task': {'queue': 'long_running'},
    'core.tasks.generate_memory_embedding': {'queue': 'ml'},
    'core.tasks.collect_training_data': {'queue': 'ml'},

    # Session 1063: Route content-generation tasks to content queue
    'core.tasks.auto_enhance_blogs': {'queue': 'content'},
    'core.tasks.score_opportunities_from_spider_data': {'queue': 'content'},

    # Session 1063: Route lightweight initiative pipeline tasks to content queue
    'core.tasks.auto_triage_dreams': {'queue': 'content'},
    'core.tasks.auto_promote_decisions': {'queue': 'content'},
    'core.tasks.auto_approve_low_risk_gates': {'queue': 'content'},
    'core.tasks.auto_complete_pilots': {'queue': 'content'},

    # Session 1063: Route PA-triggered tasks to pa queue
    'core.tasks.draft_legal_document_task': {'queue': 'pa'},

    # Session 1063: Route alert checks to agents queue
    'core.tasks.check_all_alerts': {'queue': 'agents'},

    # Session 1064: Route core.tasks_agents.* — NOT covered by 'agents.*' glob
    # (glob matches 'agents.update_agent_performance', not 'core.tasks_agents.*')
    # execute_agent loads AgentRouter with all ~92 agents (~300-500MB)
    'core.tasks_agents.execute_agent': {'queue': 'long_running'},
    'core.tasks_agents.execute_agent_async': {'queue': 'long_running'},
    'core.tasks_agents.execute_orchestration': {'queue': 'long_running'},
    'core.tasks_agents.execute_sports_orchestration': {'queue': 'long_running'},
    'core.tasks_agents.check_stuck_executions': {'queue': 'broadcast'},
    'core.tasks_agents.cleanup_old_executions': {'queue': 'broadcast'},

    # Session 1064: Route ai_core.spiders.tasks.* — spider init/deploy is heavy
    'ai_core.spiders.tasks.deploy_full_army': {'queue': 'long_running'},
    'ai_core.spiders.tasks.deploy_spider_batch': {'queue': 'long_running'},
    'ai_core.spiders.tasks.collect_spider_data': {'queue': 'long_running'},
    'ai_core.spiders.tasks.activate_spider_wave': {'queue': 'long_running'},
    'ai_core.spiders.tasks.quick_deploy': {'queue': 'long_running'},
    'ai_core.spiders.tasks.spider_heartbeat': {'queue': 'broadcast'},
    'ai_core.spiders.tasks.clean_inactive_spiders': {'queue': 'broadcast'},

    # Session 1064: Route standalone/module tasks missing routes
    'autonomous_studio.generate_content': {'queue': 'long_running'},
    'trigger_signal_driven_conversation': {'queue': 'long_running'},
    'pipelines.tasks.run_pipeline_task': {'queue': 'long_running'},
    'workspace.autopilot_tick': {'queue': 'long_running'},
    'aggregate_spider_signals': {'queue': 'long_running'},
    'process_pending_auto_topics': {'queue': 'long_running'},
    'backfill_signal_scores': {'queue': 'ml'},
    'cleanup_expired_signals': {'queue': 'default'},
    'content_studio.backfill_voice_scores': {'queue': 'content'},
    'content_studio.score_episode_voice': {'queue': 'content'},
    'ai_core.tasks.clean_stale_data': {'queue': 'default'},
    'ai_core.tasks.sync_revenue_metrics': {'queue': 'default'},
    'learning_loop.calculate_agent_accuracy': {'queue': 'broadcast'},
    'learning_loop.track_prediction_outcomes': {'queue': 'broadcast'},
    'triggers.create_default_triggers': {'queue': 'default'},
    'triggers.process_trigger_events': {'queue': 'default'},
    'roi_metrics.record_opportunity_application': {'queue': 'default'},
    'roi_metrics.record_opportunity_click': {'queue': 'default'},
    'roi_metrics.record_opportunity_view': {'queue': 'default'},
    'roi_metrics.record_revenue': {'queue': 'default'},

    # Session 1064: Route remaining heavy core.tasks.* that were falling to default
    'core.tasks.execute_orchestration_async': {'queue': 'long_running'},
    'core.tasks.run_autonomous_content_studio': {'queue': 'long_running'},
    'core.tasks.run_conceptforge_pipeline': {'queue': 'long_running'},
    'core.tasks.run_daily_learning_pipeline': {'queue': 'long_running'},
    'core.tasks.run_project_conversation': {'queue': 'long_running'},
    'core.tasks.run_single_project_learning': {'queue': 'long_running'},
    'core.tasks.run_diagnostic_pipeline_task': {'queue': 'default'},  # 178ms avg, 348/day — lightweight
    'core.tasks.run_proactive_system_check': {'queue': 'long_running'},
    'core.tasks.run_agent_health_rotation': {'queue': 'long_running'},
    'core.tasks.run_daily_priority_scan': {'queue': 'broadcast'},
    'core.tasks.generate_content_package': {'queue': 'long_running'},
    'core.tasks.generate_ai_series': {'queue': 'long_running'},
    'core.tasks.generate_podcast_episode': {'queue': 'content'},
    'core.tasks.generate_smart_suggestions': {'queue': 'long_running'},
    'core.tasks.generate_step_content': {'queue': 'long_running'},
    'core.tasks.generate_user_insights': {'queue': 'long_running'},
    'core.tasks.generate_opportunity_report': {'queue': 'long_running'},
    'core.tasks.generate_checklist_content_async': {'queue': 'long_running'},
    'core.tasks.enhance_blog': {'queue': 'content'},
    'core.tasks.collect_kalshi_market_intelligence': {'queue': 'long_running'},
    'core.tasks.collect_spider_data': {'queue': 'long_running'},
    'core.tasks.collect_sports_odds': {'queue': 'sports'},
    'core.tasks.collect_sports_odds_intelligence': {'queue': 'sports'},
    'core.tasks.daily_betting_digest': {'queue': 'sports'},
    'core.tasks.discover_success_patterns': {'queue': 'long_running'},
    'core.tasks.execute_pending_opportunity_tasks': {'queue': 'long_running'},
    'core.tasks.execute_pilot_implementations': {'queue': 'long_running'},
    'core.tasks.execute_single_dream': {'queue': 'long_running'},
    'core.tasks.execute_scheduled_workflow': {'queue': 'long_running'},
    'core.tasks.execute_scheduled_automations': {'queue': 'long_running'},
    'core.tasks.evolve_agent_relationships': {'queue': 'long_running'},
    'core.tasks.isolate_documents_batch': {'queue': 'long_running'},
    'core.tasks.backfill_stage_documents': {'queue': 'long_running'},
    'core.tasks.score_spider_data_async': {'queue': 'ml'},
    'core.tasks.collect_training_data_full': {'queue': 'ml'},
    'core.tasks.score_unscored_deliverables': {'queue': 'content'},
    'core.tasks.track_content_performance': {'queue': 'content'},
    'core.tasks.monitor_celery_health': {'queue': 'broadcast'},
    'core.tasks.check_kpi_alerts': {'queue': 'broadcast'},
    'core.tasks.get_event_bus_stats': {'queue': 'broadcast'},
    'core.tasks.analyze_pa_tool_patterns': {'queue': 'default'},
    'core.tasks.cleanup_expired_pa_insights': {'queue': 'default'},
}

# Celery Worker Settings
CELERY_WORKER_CONCURRENCY = int(os.environ.get('CELERY_WORKER_CONCURRENCY', '4'))
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'
CELERY_BEAT_SCHEDULER = 'core.schedulers:QueuePreservingScheduler'

# Session 1007: Removed ~600 lines of dead CELERY_BEAT_SCHEDULE.
# The authoritative beat schedule is in core/celery.py (app.conf.beat_schedule).
# settings.py's copy was completely overwritten by celery.py and never used.
# Views that referenced it now read from celery_app.conf.beat_schedule.

# ffmpeg Timeout Configuration (in seconds)
# Used for all subprocess calls to ffmpeg to prevent hung processes
FFMPEG_TIMEOUT = int(os.environ.get('FFMPEG_TIMEOUT', 300))  # 5 minutes default
FFMPEG_TIMEOUT_LONG = int(os.environ.get('FFMPEG_TIMEOUT_LONG', 600))  # 10 minutes for concatenation, complex ops

# DRF Spectacular Settings for API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Unified Donkey Betz API',
    'DESCRIPTION': 'Unified Platform API for Sports Analytics, AI Agents, and Content Generation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# =============================================================================
# Session 268: Clean Architecture Feature Flags
# =============================================================================
# When True, uses the new layered architecture:
#   User → Personal Assistant → Agent Router → Specialized Agents → Tools
# When False, uses the current architecture with all tools exposed to GPT
#
# Phase 1: Feature flag starts disabled, test ImageAgent in isolation
# Phase 4: Enable flag after all agents migrated and tested
# Phase 6: Remove flag after cleanup
#
# Session 280: ENABLED by default (was 'False')
# - All 10 core agents are working
# - Compatibility shim in agents/__init__.py redirects with deprecation warnings
# - Can still disable via: USE_CLEAN_AGENT_ARCHITECTURE=False make start
USE_CLEAN_AGENT_ARCHITECTURE = os.environ.get('USE_CLEAN_AGENT_ARCHITECTURE', 'True') == 'True'

# Session 1036: LLM-driven function calling for PA (replaces keyword router)
# When True, PA uses GPT-5.2 function calling to route messages instead of
# the 506-line _detect_intent_and_route() keyword matching chain.
PA_USE_FUNCTION_CALLING = os.environ.get('PA_USE_FUNCTION_CALLING', 'false').lower() == 'true'

# Learning feedback loop flags
# Session 1078: Both enabled by default — learning loop fully closed
LEARNING_ROUTING_ENABLED = os.environ.get('LEARNING_ROUTING_ENABLED', 'true').lower() == 'true'
LEARNING_PROMPT_INJECTION_ENABLED = os.environ.get('LEARNING_PROMPT_INJECTION_ENABLED', 'true').lower() == 'true'

# Session G2: Recording Mode — controls artifact persistence and log verbosity
# off: don't auto-save intermediate outputs; minimize payload logging
# on: reproducible; saves all artifacts and intermediate outputs
# public_safe: on + stricter redaction + no sensitive payload storage
RECORDING_MODE = os.environ.get('RECORDING_MODE', 'off').lower()
if RECORDING_MODE not in ('off', 'on', 'public_safe'):
    RECORDING_MODE = 'off'
