#!/usr/bin/env python3
"""
Test complete flow: Generate fresh image → Upscale it
Session 131 - Test with newly generated image instead of derived images
"""

import os
import django
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from core.agents import ImageEditingAgent
from content.image_generation import ImageGenerationService

User = get_user_model()

print("=" * 80)
print("GENERATE → UPSCALE TEST - Session 131")
print("=" * 80)

user = User.objects.first()
if not user:
    print("❌ No users found")
    exit(1)

print(f"\n👤 Testing with user: {user.username}")

# Count images before
image_count_before = ImageHistory.objects.filter(user=user).count()
print(f"\n📊 Image count BEFORE generation: {image_count_before}")

# Step 1: Generate a brand new image
print(f"\n🎨 STEP 1: Generating fresh image with Stability AI")
print("=" * 80)

service = ImageGenerationService()
result = service.generate_image(
    prompt="a simple blue robot on white background",
    size='1024x1024',
    style='realistic',
    quality='balanced',
    provider='stability',
    negative_prompt='blurry, low quality',
    num_images=1
)

print(f"\n📋 Generation Result:")
print(f"   Success: {result.success}")
if hasattr(result, 'error_message'):
    print(f"   Error: {result.error_message}")
if result.success and result.images:
    print(f"   Images: {len(result.images)}")
    print(f"   URL: {result.images[0]}")
else:
    print("❌ FAILED! Image generation failed")
    exit(1)

# Save to ImageHistory (following generate_image_with_stability pattern)
image_url = result.images[0]
new_image = ImageHistory.objects.create(
    user=user,
    filename=image_url.split('/')[-1][:255],
    file_path=image_url,
    prompt="a simple blue robot on white background",
    model_used='sd3',
    style='realistic',
    image_type='generated'
)

print(f"\n✅ New image created and saved!")
print(f"   ID: {new_image.id}")
print(f"   Sequential #: {new_image.get_sequential_number()}")
print(f"   Filename: {new_image.filename}")
print(f"   File Path: {new_image.file_path}")
print(f"   Model: {new_image.model_used}")

# Wait a moment
time.sleep(1)

# Count images after generation
image_count_after_gen = ImageHistory.objects.filter(user=user).count()
print(f"\n📊 Image count AFTER generation: {image_count_after_gen}")

# Step 2: Upscale the newly generated image
print(f"\n🔍 STEP 2: Upscaling the fresh image")
print("=" * 80)

agent = ImageEditingAgent(user=user, project_id=None)
upscale_result = agent.execute(operation='upscale', image_id=str(new_image.id))

print(f"\n📋 Upscale Result:")
print(json.dumps(upscale_result, indent=2))

# Count images after upscale
image_count_final = ImageHistory.objects.filter(user=user).count()
print(f"\n📊 Image count AFTER upscale: {image_count_final}")

if image_count_final > image_count_after_gen:
    print(f"\n✅ SUCCESS! Upscaled image created ({image_count_final - image_count_after_gen} new image(s))")

    upscaled_image = ImageHistory.objects.filter(user=user).order_by('-created_at').first()
    print(f"\n🎉 Upscaled Image:")
    print(f"   ID: {upscaled_image.id}")
    print(f"   Sequential #: {upscaled_image.get_sequential_number()}")
    print(f"   Filename: {upscaled_image.filename}")
    print(f"   File Path: {upscaled_image.file_path}")
    print(f"   Model: {upscaled_image.model_used}")
else:
    print(f"\n❌ FAILED! Upscale didn't create new image")
    print(f"   Agent success: {upscale_result.get('success')}")
    print(f"   Agent message: {upscale_result.get('message')}")
    print(f"   Agent error: {upscale_result.get('error')}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
