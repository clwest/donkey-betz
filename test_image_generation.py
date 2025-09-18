#!/usr/bin/env python
"""
Test Image Generation API
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
from content.image_generation import image_generation_service


def test_image_service_direct():
    """Test the image generation service directly"""
    print("\n" + "="*60)
    print("TEST 1: Direct Service Test")
    print("="*60)

    # Test if service is initialized
    print(f"OpenAI Key Available: {bool(image_generation_service.openai_key)}")
    print(f"Stability Key Available: {bool(image_generation_service.stability_key)}")
    print(f"Replicate Key Available: {bool(image_generation_service.replicate_key)}")

    # Try to generate an image
    result = image_generation_service.generate_image(
        prompt="A beautiful sunset over mountains",
        size="1024x1024",
        provider="auto"
    )

    print(f"\nGeneration Success: {result.success}")
    if result.success:
        print(f"Provider Used: {result.provider_used}")
        print(f"Images Generated: {len(result.images)}")
        if result.images:
            print(f"First Image URL: {result.images[0][:100]}...")
    else:
        print(f"Error: {result.error_message}")

    return result.success


def test_api_with_auth():
    """Test the API endpoint with authentication"""
    print("\n" + "="*60)
    print("TEST 2: API Endpoint Test with Auth")
    print("="*60)

    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )

    if created:
        user.set_password('testpass123')
        user.save()

    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    print(f"Using token: {token.key}")

    # Test the API
    url = 'http://localhost:8000/api/v1/content/create/'
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'content_type': 'image',
        'prompt': 'A futuristic city at night',
        'style': 'digital-art',
        'size': '1024x1024',
        'batch_size': 1,
        'quality': 'standard'
    }

    print(f"Testing endpoint: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")

            if data.get('success'):
                content = data.get('content', {})
                print(f"Content ID: {content.get('id')}")
                print(f"Content Type: {content.get('type')}")

                # Check for images
                images = content.get('images', [])
                if images:
                    print(f"Images Generated: {len(images)}")
                    print(f"First Image URL: {images[0].get('url', 'N/A')[:100]}...")
                else:
                    print("No images in response")

                # Check metadata
                metadata = content.get('metadata', {})
                if metadata:
                    print(f"Provider: {metadata.get('provider')}")
                    print(f"Model: {metadata.get('model')}")
            else:
                print("Success=False in response")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API call failed!")
            print(f"Response: {response.text[:500]}")

            # If 500 error, check server logs
            if response.status_code == 500:
                print("\nLikely causes:")
                print("1. Missing API keys in environment")
                print("2. Import error in image_generation module")
                print("3. Database model issue")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def diagnose_issues():
    """Diagnose common issues"""
    print("\n" + "="*60)
    print("DIAGNOSTICS")
    print("="*60)

    # Check environment variables
    print("\n1. Environment Variables:")
    api_keys = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
        'STABILITY_API_KEY': os.environ.get('STABILITY_API_KEY', ''),
        'REPLICATE_API_KEY': os.environ.get('REPLICATE_API_KEY', '')
    }

    for key, value in api_keys.items():
        if value:
            print(f"   {key}: {'*' * 10} (configured)")
        else:
            print(f"   {key}: NOT SET")

    # Check imports
    print("\n2. Module Imports:")
    try:
        import openai
        print("   ✅ openai module available")
    except ImportError:
        print("   ❌ openai module not installed (pip install openai)")

    try:
        import replicate
        print("   ✅ replicate module available")
    except ImportError:
        print("   ❌ replicate module not installed (pip install replicate)")

    # Check database models
    print("\n3. Database Models:")
    try:
        from content.models import ContentGeneration, ContentStatus
        print("   ✅ Content models available")

        # Check if tables exist
        count = ContentGeneration.objects.count()
        print(f"   ContentGeneration records: {count}")
    except Exception as e:
        print(f"   ❌ Content models error: {e}")
        print("   Run: python manage.py migrate")


def main():
    """Run all tests"""
    print("\n🎨 IMAGE GENERATION TEST SUITE")

    results = {
        'Direct Service': test_image_service_direct(),
        'API with Auth': test_api_with_auth()
    }

    # Run diagnostics regardless
    diagnose_issues()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    if all(results.values()):
        print("\n🎉 All tests passed! Image generation is working!")
    else:
        print("\n⚠️ Some tests failed. Review the diagnostics above.")
        print("\nTo fix:")
        print("1. Set API keys in .env file:")
        print("   OPENAI_API_KEY=your-key-here")
        print("   STABILITY_API_KEY=your-key-here")
        print("2. Install required packages:")
        print("   pip install openai replicate")
        print("3. Run migrations:")
        print("   python manage.py migrate")


if __name__ == "__main__":
    main()