#!/usr/bin/env python3
"""
Systematic 3D Conversion and Download Workflow
Converts 10 character images to 3D models with proper names
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory, MiniFigAsset

User = get_user_model()

# Character names from prompts (in order)
CHARACTER_NAMES = [
    "01_Basic_T_Pose_Humanoid",
    "02_Standing_Neutral",
    "03_Basic_Forward_Facing",
    "04_Athletic_Walking",
    "05_Stocky_Character",
    "06_Slender_Casual",
    "07_Action_Arms_Extended",
    "08_Tall_Stylized_Dynamic",
    "09_Short_Exaggerated",
    "10_Twisted_Action_Complex",
]

def main():
    print("=" * 80)
    print("🎨 3D CONVERSION & DOWNLOAD WORKFLOW")
    print("=" * 80)
    print()

    # Get admin user
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return

    # Get 10 most recent images
    images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:10]

    if images.count() < 10:
        print(f"⚠️  Only found {images.count()} images, expected 10")
        print("Proceeding with available images...")
        print()

    print(f"✅ Found {images.count()} images to convert\n")

    # Display mapping
    print("=" * 80)
    print("IMAGE → CHARACTER MAPPING")
    print("=" * 80)
    for i, img in enumerate(images):
        char_name = CHARACTER_NAMES[i] if i < len(CHARACTER_NAMES) else f"Character_{i+1}"
        print(f"\n[{i+1}] {char_name}")
        print(f"    Image ID: {img.id}")
        print(f"    Created: {img.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Prompt: {img.prompt[:60]}..." if img.prompt else "    Prompt: (no prompt)")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("Option 1: Manual Conversion (Recommended for First Time)")
    print("  1. Open http://localhost:8000/ai-studio/")
    print("  2. Go to 'MiniFig 3D Characters' or 'Image-to-3D' tab")
    print("  3. For each image above, in order:")
    print("     - Select the image")
    print("     - Use the character name as title (e.g., '01_Basic_T_Pose_Humanoid')")
    print("     - Click 'Generate 3D Model'")
    print("     - Wait for completion (~60 seconds)")
    print()
    print("Option 2: Automated Conversion (Coming Soon)")
    print("  - Will require API endpoint for 3D generation with custom titles")
    print()
    print("After conversion, run: python blender_tests/download_models.py")
    print()

if __name__ == '__main__':
    main()
