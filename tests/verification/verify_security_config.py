#!/usr/bin/env python3
"""
Security Configuration Verification Script
Verifies that all security configurations are properly implemented.
"""

import os
import sys
import subprocess

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

try:
    import django
    django.setup()
    from django.conf import settings
    from django.core.management.utils import get_random_secret_key
except ImportError as e:
    print(f"Error importing Django: {e}")
    sys.exit(1)

def check_security_settings():
    """Verify all security settings are properly configured."""
    results = []
    
    # 1. Check SECRET_KEY is loaded from environment
    if hasattr(settings, 'SECRET_KEY'):
        if settings.SECRET_KEY and not settings.SECRET_KEY.startswith('django-insecure'):
            results.append("✅ SECRET_KEY properly configured from environment")
        else:
            results.append("❌ SECRET_KEY is using default insecure value")
    else:
        results.append("❌ SECRET_KEY not found in settings")
    
    # 2. Check DEBUG setting
    if not settings.DEBUG:
        results.append("✅ DEBUG is disabled")
    else:
        results.append("⚠️  DEBUG is enabled (OK for development)")
    
    # 3. Check ALLOWED_HOSTS
    if settings.ALLOWED_HOSTS:
        results.append(f"✅ ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
    else:
        results.append("❌ ALLOWED_HOSTS is empty")
    
    # 4. Check CORS configuration
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS') and settings.CORS_ALLOWED_ORIGINS:
        results.append(f"✅ CORS properly configured with specific origins: {settings.CORS_ALLOWED_ORIGINS}")
    else:
        results.append("❌ CORS configuration missing or insecure")
    
    # 5. Check CSRF middleware
    if 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE:
        results.append("✅ CSRF protection enabled")
    else:
        results.append("❌ CSRF protection disabled - CRITICAL VULNERABILITY")
    
    # 6. Check Redis configuration
    if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
        cache_backend = settings.CACHES['default']['BACKEND']
        if 'redis' in cache_backend.lower():
            results.append("✅ Redis cache configured")
        else:
            results.append("⚠️  Using non-Redis cache backend")
    
    # 7. Check Celery configuration
    if hasattr(settings, 'CELERY_BROKER_URL'):
        results.append(f"✅ Celery broker configured: {settings.CELERY_BROKER_URL}")
    else:
        results.append("❌ Celery broker not configured")
    
    # 8. Check Channels Layer
    if hasattr(settings, 'CHANNEL_LAYERS'):
        results.append("✅ Channels layer configured for WebSocket support")
    else:
        results.append("❌ Channels layer not configured")
    
    # 9. Check AI Provider configuration
    if hasattr(settings, 'AI_PROVIDERS'):
        configured_providers = [k for k, v in settings.AI_PROVIDERS.items() if v]
        if configured_providers:
            results.append(f"✅ AI providers configured: {len(configured_providers)} providers")
        else:
            results.append("⚠️  No AI provider keys configured")
    
    # 10. Check environment-specific settings
    if hasattr(settings, 'ENVIRONMENT'):
        results.append(f"✅ Environment configured: {settings.ENVIRONMENT}")
    else:
        results.append("❌ Environment not specified")
    
    return results

def check_file_security():
    """Check for potential security issues in files."""
    results = []
    
    # Check for hardcoded secrets
    try:
        result = subprocess.run(['grep', '-r', 'django-insecure', '--include=*.py', '.'], 
                              capture_output=True, text=True)
        if result.stdout:
            results.append("❌ Found hardcoded insecure Django keys")
        else:
            results.append("✅ No hardcoded insecure keys found")
    except:
        results.append("⚠️  Could not check for hardcoded secrets")
    
    return results

def main():
    print("🔒 UNIFIED DONKEY BETZ PLATFORM - SECURITY VERIFICATION")
    print("=" * 60)
    
    print("\n📋 SECURITY SETTINGS CHECK:")
    for result in check_security_settings():
        print(f"  {result}")
    
    print("\n📁 FILE SECURITY CHECK:")
    for result in check_file_security():
        print(f"  {result}")
    
    print("\n🔧 REQUIRED ENVIRONMENT VARIABLES:")
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'CELERY_BROKER_URL',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
    ]
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"  ✅ {var} - Set")
        else:
            print(f"  ❌ {var} - Missing (add to .env file)")
    
    print("\n🚀 NEXT STEPS:")
    print("  1. Copy .env.example to .env and fill in your values")
    print("  2. Generate a secure SECRET_KEY (50+ characters)")
    print("  3. Set up PostgreSQL database")
    print("  4. Set up Redis server")
    print("  5. Configure AI provider API keys")
    print("  6. Run: python manage.py migrate")
    print("  7. Run: celery -A celery_app worker --loglevel=info")
    print("  8. Run: python manage.py runserver")

if __name__ == '__main__':
    main()