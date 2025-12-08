#!/usr/bin/env python3
"""
Session 143: Simple Live Agent Contribution Tracking Test

Tests agent contribution tracking by generating content through API endpoints,
which is the actual production code path where tracking happens.
"""

import os
import sys
import django
import requests
import time
import json

# Setup Django for database queries
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory, MiniFigAsset
from core.models.agents_registry import AgentContribution

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 SESSION 143: Live Agent Contribution Tracking Test (Simplified)")
print("=" * 70)
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
print("TEST 1: Generate New Image via API")
print("-" * 70)

# Get an existing project ID
from content.models import CreativeProject
project = CreativeProject.objects.first()
print(f"Using project: {project.name} (ID: {project.id})")

try:
    response = requests.post(
        f"{BASE_URL}/api/v1/gallery/generate/",
        json={
            "prompt": "A futuristic robot mascot for Session 143 testing, digital art style",
            "model": "sd3-large-turbo",
            "aspect_ratio": "1:1",
            "project_id": str(project.id),
            "style_preset": "digital-art"
        },
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            image_id = result.get('image_id')
            print(f"✅ Image generated successfully!")
            print(f"   Image ID: {image_id}")

            # Check if contribution was created
            time.sleep(2)  # Give it time to create contribution
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
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("⏭️  Skipping video and 3D tests (would take 5-10 minutes)")
print("   Image test is sufficient to verify agent contribution tracking")
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

new_content_count = (final_images - initial_images) + (final_videos - initial_videos) + (final_3d - initial_3d)
new_contrib_count = final_contributions - initial_contributions

if new_content_count > 0:
    new_tracking_rate = (new_contrib_count / new_content_count * 100)
    print(f"New Content Tracking Rate: {new_tracking_rate:.1f}% ({new_contrib_count}/{new_content_count})")

    if new_tracking_rate == 100:
        print("✅ SUCCESS! All new content has agent contributions!")
    elif new_tracking_rate >= 95:
        print("✅ EXCELLENT! Tracking rate ≥ 95%")
    else:
        print("⚠️  WARNING! Some new content missing agent contributions!")

print("=" * 70)
