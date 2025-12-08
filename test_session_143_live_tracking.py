#!/usr/bin/env python3
"""
Session 143: Test Live Agent Contribution Tracking

This script generates new content and verifies that AgentContribution
records are created automatically by the Session 142 wiring.
"""

import os
import sys
import django
import time

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory, MiniFigAsset, CreativeProject
from core.models.agents_registry import AgentContribution
from content.image_generation import ImageGenerationService
from content.video_provider import VideoProvider
from content.minifig_services import generate_3d_from_images

print("=" * 70)
print("🧪 SESSION 143: Live Agent Contribution Tracking Test")
print("=" * 70)
print()

# Get or create a test project
project, created = CreativeProject.objects.get_or_create(
    name="Session 143 Test Project",
    defaults={
        'description': 'Testing agent contribution tracking for live content generation',
        'status': 'active'
    }
)
print(f"✅ Using project: {project.name} (ID: {project.id})")
print()

# Record counts before generation
initial_images = ImageHistory.objects.count()
initial_videos = VideoHistory.objects.count()
initial_3d = MiniFigAsset.objects.count()
initial_contributions = AgentContribution.objects.count()

print(f"📊 Initial Counts:")
print(f"   Images: {initial_images}")
print(f"   Videos: {initial_videos}")
print(f"   3D Models: {initial_3d}")
print(f"   Contributions: {initial_contributions}")
print()

# Test 1: Generate a new image
print("-" * 70)
print("TEST 1: Generate New Image")
print("-" * 70)
try:
    service = ImageGenerationService()
    result = service.generate_image(
        prompt="A futuristic robot mascot for Session 143 testing, digital art style",
        model="sd3-large-turbo",
        size="1024x1024",
        project_id=str(project.id)
    )

    if result.get('success'):
        image_id = result['image_id']
        print(f"✅ Image generated successfully!")
        print(f"   Image ID: {image_id}")

        # Check if contribution was created
        time.sleep(1)  # Give it a moment
        image = ImageHistory.objects.get(id=image_id)
        contrib = AgentContribution.objects.filter(image=image).first()

        if contrib:
            print(f"   ✅ AgentContribution created!")
            print(f"      Agent: {contrib.agent.name}")
            print(f"      Type: {contrib.contribution_type}")
            print(f"      Description: {contrib.task_description[:60]}...")
        else:
            print(f"   ❌ NO AgentContribution found!")
    else:
        print(f"❌ Image generation failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Error generating image: {e}")

print()

# Test 2: Generate a video from the new image
print("-" * 70)
print("TEST 2: Generate Video from Image")
print("-" * 70)
try:
    # Get the latest image
    latest_image = ImageHistory.objects.latest('created_at')
    print(f"   Using image: {latest_image.id}")

    provider = VideoProvider()
    result = provider.image_to_video(
        image_path=latest_image.image_path,
        prompt_text="The robot waves hello and smiles",
        duration=5,
        project_id=str(project.id)
    )

    if result.get('success'):
        video_id = result['video_id']
        print(f"✅ Video generation initiated!")
        print(f"   Video ID: {video_id}")
        print(f"   Status: {result.get('status', 'pending')}")

        # Check if contribution was created
        time.sleep(1)
        video = VideoHistory.objects.get(id=video_id)
        contrib = AgentContribution.objects.filter(video=video).first()

        if contrib:
            print(f"   ✅ AgentContribution created!")
            print(f"      Agent: {contrib.agent.name}")
            print(f"      Type: {contrib.contribution_type}")
            print(f"      Description: {contrib.task_description[:60]}...")
        else:
            print(f"   ❌ NO AgentContribution found!")
    else:
        print(f"❌ Video generation failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Error generating video: {e}")

print()

# Test 3: Generate a 3D model from an image
print("-" * 70)
print("TEST 3: Generate 3D Model from Image")
print("-" * 70)
try:
    # Get the latest image
    latest_image = ImageHistory.objects.latest('created_at')
    print(f"   Using image: {latest_image.id}")

    result = generate_3d_from_images(
        image_ids=[str(latest_image.id)],
        project=project
    )

    if result.get('success'):
        model_id = result['model_id']
        print(f"✅ 3D model generation initiated!")
        print(f"   Model ID: {model_id}")
        print(f"   Status: {result.get('status', 'pending')}")

        # Check if contribution was created
        time.sleep(1)
        model_3d = MiniFigAsset.objects.get(id=model_id)
        contrib = AgentContribution.objects.filter(minifig_asset=model_3d).first()

        if contrib:
            print(f"   ✅ AgentContribution created!")
            print(f"      Agent: {contrib.agent.name}")
            print(f"      Type: {contrib.contribution_type}")
            print(f"      Description: {contrib.task_description[:60]}...")
        else:
            print(f"   ❌ NO AgentContribution found!")
    else:
        print(f"❌ 3D generation failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Error generating 3D model: {e}")

print()

# Final counts
final_images = ImageHistory.objects.count()
final_videos = VideoHistory.objects.count()
final_3d = MiniFigAsset.objects.count()
final_contributions = AgentContribution.objects.count()

print("=" * 70)
print("📊 FINAL RESULTS")
print("=" * 70)
print(f"Content Generated:")
print(f"   Images: {initial_images} → {final_images} (+{final_images - initial_images})")
print(f"   Videos: {initial_videos} → {final_videos} (+{final_videos - initial_videos})")
print(f"   3D Models: {initial_3d} → {final_3d} (+{final_3d - initial_3d})")
print()
print(f"Contributions: {initial_contributions} → {final_contributions} (+{final_contributions - initial_contributions})")
print()

# Calculate new tracking rate
total_content = final_images + final_videos + final_3d
tracking_rate = (final_contributions / total_content * 100) if total_content > 0 else 0
print(f"Tracking Rate: {tracking_rate:.1f}% ({final_contributions}/{total_content})")

if final_contributions - initial_contributions == (final_images - initial_images) + (final_videos - initial_videos) + (final_3d - initial_3d):
    print("✅ SUCCESS! All new content has agent contributions!")
else:
    print("⚠️  WARNING! Some content missing agent contributions!")

print("=" * 70)
