#!/usr/bin/env python
"""
Test script to verify AI provider keys are loading correctly
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
from dotenv import load_dotenv

print("=== AI Provider Keys Test ===")

# Test 1: Direct .env loading
print("\n1. Testing direct .env loading:")
load_dotenv(BASE_DIR / '.env')
print(f"   OPENAI_API_KEY: {'✓ Present' if os.environ.get('OPENAI_API_KEY') else '✗ Missing'}")
print(f"   ANTHROPIC_API_KEY: {'✓ Present' if os.environ.get('ANTHROPIC_API_KEY') else '✗ Missing'}")
print(f"   GOOGLE_API_KEY: {'✓ Present' if os.environ.get('GOOGLE_API_KEY') else '✗ Missing'}")

# Test 2: Django settings loading
print("\n2. Testing Django settings loading:")
try:
    django.setup()
    from django.conf import settings
    
    if hasattr(settings, 'AI_PROVIDERS'):
        providers = settings.AI_PROVIDERS
        print(f"   OpenAI: {'✓ Present' if providers.get('OPENAI_API_KEY') else '✗ Missing'}")
        print(f"   Anthropic: {'✓ Present' if providers.get('ANTHROPIC_API_KEY') else '✗ Missing'}")
        print(f"   Google: {'✓ Present' if providers.get('GOOGLE_API_KEY') else '✗ Missing'}")
    else:
        print("   ✗ AI_PROVIDERS not found in settings")
except Exception as e:
    print(f"   ✗ Django setup failed: {e}")

# Test 3: AI Provider Manager
print("\n3. Testing AI Provider Manager:")
try:
    from content.ai_providers import AIProviderManager
    
    manager = AIProviderManager()
    available = manager.get_available_providers()
    
    print(f"   Available providers: {available}")
    print(f"   Provider count: {len(available)}")
    
    if available:
        print("   ✓ AI providers successfully initialized")
    else:
        print("   ✗ No AI providers initialized")
        
except Exception as e:
    print(f"   ✗ AI Provider Manager failed: {e}")

print("\n=== Test Complete ===")