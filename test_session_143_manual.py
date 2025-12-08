#!/usr/bin/env python3
"""
Session 143: Manual Live Agent Contribution Tracking Test

Simplest possible test - just manually check the UI to generate content,
then verify agent contributions were created.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory, MiniFigAsset
from core.models.agents_registry import AgentContribution

print("=" * 70)
print("🧪 SESSION 143: Agent Contribution Verification")
print("=" * 70)
print()

# Count current content
images = ImageHistory.objects.count()
videos = VideoHistory.objects.count()
models_3d = MiniFigAsset.objects.count()
total_content = images + videos + models_3d

# Count contributions
contributions = AgentContribution.objects.count()

# Calculate tracking rate
tracking_rate = (contributions / total_content * 100) if total_content > 0 else 0

print(f"📊 CURRENT STATUS:")
print(f"   Images: {images}")
print(f"   Videos: {videos}")
print(f"   3D Models: {models_3d}")
print(f"   Total Content: {total_content}")
print()
print(f"   Agent Contributions: {contributions}")
print(f"   Tracking Rate: {tracking_rate:.1f}% ({contributions}/{total_content})")
print()

# Check most recent items
latest_image = ImageHistory.objects.latest('created_at') if ImageHistory.objects.exists() else None
latest_video = VideoHistory.objects.latest('created_at') if VideoHistory.objects.exists() else None
latest_3d = MiniFigAsset.objects.latest('created_at') if MiniFigAsset.objects.exists() else None

print("📅 MOST RECENT CONTENT:")
if latest_image:
    contrib = AgentContribution.objects.filter(image=latest_image).first()
    status = "✅ YES" if contrib else "❌ NO"
    created_str = latest_image.created_at.strftime("%Y-%m-%d %H:%M:%S")
    print(f"   Latest Image: {latest_image.id}")
    print(f"     Created: {created_str}")
    print(f"     Has Contribution: {status}")
    if contrib:
        print(f"     Agent: {contrib.agent.name}")
        print(f"     Type: {contrib.contribution_type}")

if latest_video:
    contrib = AgentContribution.objects.filter(video=latest_video).first()
    status = "✅ YES" if contrib else "❌ NO"
    created_str = latest_video.created_at.strftime("%Y-%m-%d %H:%M:%S")
    print(f"   Latest Video: {latest_video.id}")
    print(f"     Created: {created_str}")
    print(f"     Has Contribution: {status}")
    if contrib:
        print(f"     Agent: {contrib.agent.name}")
        print(f"     Type: {contrib.contribution_type}")

if latest_3d:
    contrib = AgentContribution.objects.filter(minifig_asset=latest_3d).first()
    status = "✅ YES" if contrib else "❌ NO"
    created_str = latest_3d.created_at.strftime("%Y-%m-%d %H:%M:%S")
    print(f"   Latest 3D Model: {latest_3d.id}")
    print(f"     Created: {created_str}")
    print(f"     Has Contribution: {status}")
    if contrib:
        print(f"     Agent: {contrib.agent.name}")
        print(f"     Type: {contrib.contribution_type}")

print()
print("=" * 70)
print("📋 INSTRUCTIONS FOR MANUAL TEST:")
print("=" * 70)
print("1. Open AI Studio: http://localhost:8000/ai-studio/")
print("2. Generate ONE new image with any prompt")
print("3. Run this script again to verify tracking")
print("=" * 70)
