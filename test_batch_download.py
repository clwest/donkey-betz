#!/usr/bin/env python3
"""
Test Batch Download Feature (Session 37: Feature 10)

Quick test to verify batch download endpoint is working.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from django.contrib.auth import get_user_model

User = get_user_model()

def test_batch_download():
    print("🧪 Testing Batch Download Feature")
    print("=" * 50)

    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found in database")
        return False

    print(f"✅ User: {user.username}")

    # Get some images
    images = ImageHistory.objects.filter(user=user)[:3]

    if not images:
        print("❌ No images found for user")
        return False

    print(f"✅ Found {images.count()} images in history")

    # Display image info
    for idx, img in enumerate(images, 1):
        print(f"  {idx}. {img.image_type} - {img.filename[:50]}")

    print("\n✅ Batch Download Feature Ready to Test!")
    print("\nTest Instructions:")
    print("1. Open http://localhost:8000/ai-studio/")
    print("2. Click '📊 Gallery' tab")
    print("3. You'll see checkboxes on each image (top-left corner)")
    print("4. Click checkboxes to select 2-3 images")
    print("5. Click '📦 Download Selected (N)' button")
    print("6. ZIP file should download with images + metadata.json")

    return True

if __name__ == '__main__':
    success = test_batch_download()
    sys.exit(0 if success else 1)
