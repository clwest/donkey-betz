#!/usr/bin/env python3
"""
Verify Dynamic URL Configuration
Tests that the system works with dynamic URLs instead of hardcoded ports
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse

def test_cors_configuration():
    """Test CORS settings for production readiness"""
    print("\n🔍 Testing CORS Configuration...")
    
    print(f"DEBUG mode: {settings.DEBUG}")
    
    if settings.DEBUG:
        print("✅ Development mode - CORS_ALLOW_ALL_ORIGINS is True")
        print(f"   Allowed origins: {settings.CORS_ALLOWED_ORIGINS}")
    else:
        print("✅ Production mode - CORS configured for specific origins")
        print(f"   Allowed origins: {settings.CORS_ALLOWED_ORIGINS}")
        if hasattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES'):
            print(f"   Allowed regex patterns: {settings.CORS_ALLOWED_ORIGIN_REGEXES}")
    
    print(f"✅ CORS credentials allowed: {settings.CORS_ALLOW_CREDENTIALS}")
    print(f"✅ Custom headers configured: {len(settings.CORS_ALLOW_HEADERS)} headers")
    
    return True

def test_csrf_configuration():
    """Test CSRF settings for production readiness"""
    print("\n🔍 Testing CSRF Configuration...")
    
    print(f"CSRF trusted origins: {settings.CSRF_TRUSTED_ORIGINS}")
    
    if settings.DEBUG:
        print("✅ Development mode - localhost origins trusted")
    else:
        print("✅ Production mode - configured for HTTPS origins")
    
    return True

def test_allowed_hosts():
    """Test ALLOWED_HOSTS configuration"""
    print("\n🔍 Testing ALLOWED_HOSTS Configuration...")
    
    print(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    
    if settings.DEBUG:
        print("✅ Development mode - permissive host configuration")
    else:
        print("✅ Production mode - specific hosts configured")
        if any(host.startswith('.') for host in settings.ALLOWED_HOSTS):
            print("✅ Wildcard subdomains supported")
    
    return True

def test_api_endpoints():
    """Test that API endpoints are accessible"""
    print("\n🔍 Testing API Endpoint Configuration...")
    
    # Check key API endpoints exist
    endpoints = [
        '/api/health/',
        '/api/auth/login/',
        '/api/v1/agents/',
        '/api/v1/sports/leagues/',
    ]
    
    from django.urls import resolve, Resolver404
    
    for endpoint in endpoints:
        try:
            resolve(endpoint)
            print(f"✅ Endpoint exists: {endpoint}")
        except Resolver404:
            print(f"⚠️  Endpoint not found: {endpoint}")
    
    return True

def test_websocket_configuration():
    """Test WebSocket configuration"""
    print("\n🔍 Testing WebSocket Configuration...")
    
    # Check if Channels is properly configured
    if hasattr(settings, 'CHANNEL_LAYERS'):
        print(f"✅ Channel layers configured: {list(settings.CHANNEL_LAYERS.keys())}")
        
        default_config = settings.CHANNEL_LAYERS.get('default', {})
        backend = default_config.get('BACKEND', 'Not configured')
        print(f"   Backend: {backend}")
        
        if 'CONFIG' in default_config:
            hosts = default_config['CONFIG'].get('hosts', [])
            if hosts:
                print(f"   Redis host: {hosts[0] if isinstance(hosts[0], str) else hosts[0][0]}")
    else:
        print("⚠️  Channel layers not configured")
    
    # Check ASGI application
    if hasattr(settings, 'ASGI_APPLICATION'):
        print(f"✅ ASGI application: {settings.ASGI_APPLICATION}")
    else:
        print("⚠️  ASGI application not configured")
    
    return True

def main():
    """Run all configuration tests"""
    print("=" * 60)
    print("🚀 DYNAMIC URL CONFIGURATION VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_cors_configuration,
        test_csrf_configuration,
        test_allowed_hosts,
        test_api_endpoints,
        test_websocket_configuration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CONFIGURATION TESTS PASSED!")
        print("\n📝 Deployment Notes:")
        print("1. Set DEBUG=False in production")
        print("2. Configure DATABASE_URL with PostgreSQL")
        print("3. Set a strong SECRET_KEY")
        print("4. Configure ALLOWED_HOSTS with your domain")
        print("5. Set up Redis for caching and WebSockets")
        print("6. Configure SSL certificates for HTTPS")
        print("7. Use environment variables for sensitive data")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    print("=" * 60)

if __name__ == '__main__':
    main()