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
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

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
    'sports',                 # Sports Analytics Engine
    'content',                # Content Generation System
    'self_awareness',         # Code Introspection & Self-Modification
    'dashboard',              # Dashboard API endpoints
    'campaigns',              # Campaign management
    'workflows',              # Workflow management
    # 'realtime',               # WebSocket & Event Bus
    # 'monitoring',             # System Health & Analytics
    # 'billing',                # Unified billing system
    # 'security',               # Security and authentication
    # 'workflow',               # Workflow orchestration
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Unified platform middleware (will be created)
    # 'gateway.middleware.UnifiedAPIMiddleware',
    # 'security.middleware.UnifiedAuthMiddleware',
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

# Channels Configuration
try:
    import channels_redis
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [os.environ.get('REDIS_CHANNELS_URL', 'redis://localhost:6379/3')],
                'capacity': 300,
                'expiry': 60,
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
        'gpt-4': 128000,
        'gpt-3.5-turbo': 16385
    },
    'MAX_OUTPUT_TOKENS': {
        'gpt-5': 128000,
        'gpt-5-mini': 128000,
        'gpt-5-nano': 128000,
        'gpt-4': 4096,
        'gpt-3.5-turbo': 4096
    },
    # Prompt Caching
    'ENABLE_PROMPT_CACHING': True,
    'PROMPT_CACHE_TTL': 300,
    'GPT5_FALLBACK_MODEL': 'gpt-4',
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
        'rest_framework.permissions.IsAuthenticated',
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
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # For development only
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
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')

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

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.UnifiedUser'

# Development Tools
if DEBUG:
    ENABLE_DEBUG_TOOLBAR = os.environ.get('ENABLE_DEBUG_TOOLBAR', 'True') == 'True'

# Testing Configuration
TESTING_MODE = os.environ.get('TESTING_MODE', 'False') == 'True'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/2')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
