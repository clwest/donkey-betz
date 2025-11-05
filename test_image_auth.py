#!/usr/bin/env python3
"""
Test image generation authentication and API calls
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.image_generation import ImageGenerationService
from dotenv import load_dotenv

load_dotenv()

def test_image_generation():
    """Test image generation with Stability AI"""

    print("\n🧪 Testing Image Generation Authentication\n")
    print("=" * 60)

    # Check API key
    stability_key = os.getenv('STABILITY_API_KEY')
    print(f"1. API Key check: {'✅ Found' if stability_key else '❌ Missing'}")
    if stability_key:
        print(f"   Key preview: {stability_key[:15]}...{stability_key[-4:]}")

    # Get or create test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    print(f"\n2. Test user: {'✅ Created' if created else '✅ Found'} - {user.username}")

    # Test ImageGenerationService
    print(f"\n3. Testing ImageGenerationService...")
    try:
        service = ImageGenerationService()
        print(f"   ✅ Service initialized")

        # Try generating an image
        print(f"\n4. Attempting image generation...")
        result = service.generate_image(
            prompt="A cute red panda in a forest",
            size="1024x1024",
            style="photorealistic",
            quality="balanced",
            provider='stability'
        )

        if result.success:
            print(f"   ✅ Generation SUCCESS!")
            print(f"   - Images generated: {len(result.images)}")
            print(f"   - Cost: ${result.cost:.4f}" if hasattr(result, 'cost') else "")
        else:
            print(f"   ❌ Generation FAILED!")
            print(f"   - Error: {result.error if hasattr(result, 'error') else 'Unknown'}")

    except Exception as e:
        print(f"   ❌ Exception occurred: {type(e).__name__}")
        print(f"   - Message: {str(e)}")
        import traceback
        print(f"\n   Full traceback:")
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test complete!\n")

if __name__ == '__main__':
    test_image_generation()
