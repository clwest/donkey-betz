#!/usr/bin/env python3
"""
Test Runway ML authentication and API key loading
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.video_provider import RunwayMLProvider
from dotenv import load_dotenv

load_dotenv()

def test_runway_auth():
    """Test Runway ML API key loading"""

    print("\n🧪 Testing Runway ML Authentication\n")
    print("=" * 60)

    # Check API key in .env
    runway_key = os.getenv('RUNWAY_API_KEY')
    print(f"1. API Key in .env: {'✅ Found' if runway_key else '❌ Missing'}")
    if runway_key:
        print(f"   Key preview: {runway_key[:15]}...{runway_key[-4:]}")

    # Test RunwayMLProvider
    print(f"\n2. Testing RunwayMLProvider...")
    try:
        provider = RunwayMLProvider()
        print(f"   ✅ Provider initialized")
        print(f"   - API key loaded: {'✅ Yes' if provider.api_key else '❌ No'}")
        if provider.api_key:
            print(f"   - Key preview: {provider.api_key[:15]}...{provider.api_key[-4:]}")
        print(f"   - API base: {provider.api_base}")
        print(f"   - Mock mode: {provider.mock_mode}")

    except Exception as e:
        print(f"   ❌ Exception occurred: {type(e).__name__}")
        print(f"   - Message: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test complete!\n")

if __name__ == '__main__':
    test_runway_auth()
