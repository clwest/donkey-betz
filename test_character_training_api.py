#!/usr/bin/env python3
"""
Test Character Training API Integration
Session 74 Phase 2: Verify backend endpoints and integration
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO

from content.character_training import (
    validate_training_image,
    ImageValidationError,
    MIN_IMAGES,
    MAX_IMAGES
)
from content.replicate_provider import get_replicate_provider

def test_imports():
    """Test that all imports work"""
    print("=" * 60)
    print("TEST 1: Import Verification")
    print("=" * 60)

    try:
        # Test business logic imports
        from content import character_training
        print("✅ content.character_training imported")

        # Test provider imports
        from content import replicate_provider
        print("✅ content.replicate_provider imported")

        # Test views imports
        from core import views_character_training
        print("✅ core.views_character_training imported")

        # Test URL imports
        from core import urls
        print("✅ core.urls imported (with character training routes)")

        print("\n✅ All imports successful!")
        return True

    except Exception as e:
        print(f"\n❌ Import error: {str(e)}")
        return False


def test_image_validation():
    """Test image validation logic"""
    print("\n" + "=" * 60)
    print("TEST 2: Image Validation")
    print("=" * 60)

    try:
        # Create a test image in memory
        img = Image.new('RGB', (1024, 1024), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # Create UploadedFile
        test_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=img_bytes.read(),
            content_type='image/jpeg'
        )

        # Validate
        result = validate_training_image(test_file)

        print(f"✅ Image validated")
        print(f"   Valid: {result['valid']}")
        print(f"   Dimensions: {result['width']}x{result['height']}")
        print(f"   Format: {result['format']}")
        print(f"   Warnings: {len(result['warnings'])}")

        if result['warnings']:
            for warning in result['warnings']:
                print(f"      ⚠️  {warning}")

        return result['valid']

    except Exception as e:
        print(f"❌ Image validation error: {str(e)}")
        return False


def test_provider_connection():
    """Test Replicate provider connection"""
    print("\n" + "=" * 60)
    print("TEST 3: Replicate Provider Connection")
    print("=" * 60)

    try:
        provider = get_replicate_provider()

        print(f"✅ Provider initialized")
        print(f"   Available: {provider.available}")
        print(f"   Has API key: {bool(provider.api_key)}")
        print(f"   Has client: {hasattr(provider, 'client')}")

        # Test method availability
        methods = [
            'train_character',
            'check_training_status',
            'generate_with_character',
            'check_prediction_status'
        ]

        for method in methods:
            has_method = hasattr(provider, method)
            print(f"   {method}(): {'✅' if has_method else '❌'}")

        return provider.available

    except Exception as e:
        print(f"❌ Provider connection error: {str(e)}")
        return False


def test_database_models():
    """Test database models"""
    print("\n" + "=" * 60)
    print("TEST 4: Database Models")
    print("=" * 60)

    try:
        from content.models import CharacterModel, CharacterTrainingImage

        # Check if tables exist
        print(f"✅ CharacterModel imported")
        print(f"   Table name: {CharacterModel._meta.db_table}")

        print(f"✅ CharacterTrainingImage imported")
        print(f"   Table name: {CharacterTrainingImage._meta.db_table}")

        # Check field counts
        char_fields = len(CharacterModel._meta.fields)
        img_fields = len(CharacterTrainingImage._meta.fields)

        print(f"\n   CharacterModel fields: {char_fields}")
        print(f"   CharacterTrainingImage fields: {img_fields}")

        # Check relationships
        print(f"\n   Relationships:")
        print(f"      CharacterModel → training_images (reverse FK)")
        print(f"      CharacterTrainingImage → character_model (FK)")

        # Try to query (should work even if empty)
        count = CharacterModel.objects.count()
        print(f"\n   Existing characters: {count}")

        return True

    except Exception as e:
        print(f"❌ Database model error: {str(e)}")
        return False


def test_api_urls():
    """Test API URL routing"""
    print("\n" + "=" * 60)
    print("TEST 5: API URL Routing")
    print("=" * 60)

    try:
        from django.urls import reverse

        endpoints = [
            ('list-characters', [], {}),
            ('training-requirements', [], {}),
            ('get-character', [], {'character_id': 1}),
            ('create-character', [], {}),
            ('submit-training', [], {'character_id': 1}),
            ('check-training-status', [], {'character_id': 1}),
            ('toggle-character-favorite', [], {'character_id': 1}),
            ('delete-character', [], {'character_id': 1}),
        ]

        print("Testing URL resolution:")
        for name, args, kwargs in endpoints:
            try:
                url = reverse(name, args=args, kwargs=kwargs)
                print(f"   ✅ {name:30s} → {url}")
            except Exception as e:
                print(f"   ❌ {name:30s} → Error: {str(e)}")
                return False

        return True

    except Exception as e:
        print(f"❌ URL routing error: {str(e)}")
        return False


def test_configuration():
    """Test configuration and settings"""
    print("\n" + "=" * 60)
    print("TEST 6: Configuration")
    print("=" * 60)

    try:
        from django.conf import settings

        print("Configuration checks:")

        # Check MEDIA_ROOT
        print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"      Exists: {os.path.exists(settings.MEDIA_ROOT)}")

        # Check MEDIA_URL
        print(f"   MEDIA_URL: {settings.MEDIA_URL}")

        # Check Replicate API key
        api_key = settings.EXTERNAL_API_KEYS.get('REPLICATE_API_KEY', '')
        print(f"   REPLICATE_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")

        # Check training requirements
        print(f"\n   Training Requirements:")
        print(f"      Min images: {MIN_IMAGES}")
        print(f"      Max images: {MAX_IMAGES}")
        print(f"      Min resolution: 512px")
        print(f"      Max resolution: 2048px")

        return True

    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CHARACTER TRAINING API TEST SUITE" + " " * 15 + "║")
    print("║" + " " * 15 + "Session 74 Phase 2 Integration" + " " * 15 + "║")
    print("╚" + "=" * 58 + "╝")

    tests = [
        ("Import Verification", test_imports),
        ("Image Validation", test_image_validation),
        ("Replicate Provider", test_provider_connection),
        ("Database Models", test_database_models),
        ("API URL Routing", test_api_urls),
        ("Configuration", test_configuration),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")

    print(f"\n   Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Character Training API ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
