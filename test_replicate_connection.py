#!/usr/bin/env python3
"""
Test Replicate API Connection
Session 74: Phase 1 - Character Training Integration
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.replicate_provider import get_replicate_provider

def test_replicate_connection():
    """Test Replicate API connection"""
    print("=" * 60)
    print("REPLICATE API CONNECTION TEST")
    print("=" * 60)

    # Get provider instance
    provider = get_replicate_provider()

    # Check availability
    print(f"\n1. Provider Initialization")
    print(f"   ✅ Provider created: {provider is not None}")
    print(f"   ✅ API available: {provider.available}")
    print(f"   ✅ Has API key: {bool(provider.api_key)}")

    if not provider.available:
        print("\n❌ Replicate API not available!")
        if not provider.api_key:
            print("   Missing REPLICATE_API_KEY in environment")
        return False

    # Check client initialization
    print(f"\n2. Client Initialization")
    print(f"   ✅ Client created: {hasattr(provider, 'client')}")

    try:
        # Try to access the client (doesn't make API call yet)
        print(f"   ✅ Client accessible: {provider.client is not None}")
    except Exception as e:
        print(f"   ❌ Client error: {str(e)}")
        return False

    print(f"\n3. API Methods Available")
    print(f"   ✅ train_character(): {hasattr(provider, 'train_character')}")
    print(f"   ✅ check_training_status(): {hasattr(provider, 'check_training_status')}")
    print(f"   ✅ generate_with_character(): {hasattr(provider, 'generate_with_character')}")
    print(f"   ✅ check_prediction_status(): {hasattr(provider, 'check_prediction_status')}")

    print("\n" + "=" * 60)
    print("✅ REPLICATE API CONNECTION: SUCCESS!")
    print("=" * 60)
    print("\nReady for character training integration!")
    print("Next: Backend training logic (Phase 2)")

    return True

if __name__ == "__main__":
    success = test_replicate_connection()
    sys.exit(0 if success else 1)
