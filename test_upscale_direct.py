#!/usr/bin/env python3
"""
Test upscale directly - Session 131 diagnostic
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from core.agents import ImageEditingAgent

User = get_user_model()

print("=" * 80)
print("UPSCALE DIRECT TEST - Session 131")
print("=" * 80)

user = User.objects.first()
if not user:
    print("❌ No users found")
    exit(1)

print(f"\n👤 Testing with user: {user.username}")

# Get an existing image
images = ImageHistory.objects.filter(user=user).order_by('-created_at')
if not images.exists():
    print("❌ No images found in database")
    exit(1)

test_image = images.first()
print(f"\n📸 Testing with image #{test_image.get_sequential_number()}")
print(f"   UUID: {test_image.id}")
print(f"   Filename: {test_image.filename}")
print(f"   Prompt: {test_image.prompt[:60] if test_image.prompt else 'No prompt'}...")

# Count current images
image_count_before = ImageHistory.objects.filter(user=user).count()
print(f"\n📊 Image count BEFORE: {image_count_before}")

# Test: Direct agent call with UUID for upscale
print(f"\n🧪 TEST: Upscale image")
print("=" * 80)

agent = ImageEditingAgent(user=user, project_id=None)
result = agent.execute(operation='upscale', image_id=str(test_image.id))

print(f"\n📋 Agent Result:")
print(json.dumps(result, indent=2))

# Count images after
image_count_after = ImageHistory.objects.filter(user=user).count()
print(f"\n📊 Image count AFTER: {image_count_after}")

if image_count_after > image_count_before:
    print(f"✅ SUCCESS! New image created ({image_count_after - image_count_before} new image(s))")

    # Show the new image
    new_image = ImageHistory.objects.filter(user=user).order_by('-created_at').first()
    print(f"\n🎉 New Image:")
    print(f"   ID: {new_image.id}")
    print(f"   Sequential #: {new_image.get_sequential_number()}")
    print(f"   Filename: {new_image.filename}")
    print(f"   Prompt: {new_image.prompt}")
    print(f"   Model: {new_image.model_used}")
else:
    print(f"❌ FAILED! No new images created")
    print(f"   Agent returned success: {result.get('success')}")
    print(f"   Agent message: {result.get('message')}")
    print(f"   Agent error: {result.get('error')}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
