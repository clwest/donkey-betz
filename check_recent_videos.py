#!/usr/bin/env python3
"""
Check for recent videos in the database - Session 135

This script checks if videos were created but not displayed in the UI.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory, ImageHistory
from django.contrib.auth import get_user_model

User = get_user_model()

def check_recent_videos():
    """Check for videos created in the last 24 hours."""
    print("=" * 80)
    print("🎬 Checking Recent Videos - Session 135")
    print("=" * 80)
    print()

    # Get user
    user = User.objects.get(username='admin')
    print(f"👤 User: {user.username}")
    print()

    # Check videos from last 24 hours
    yesterday = datetime.now() - timedelta(hours=24)
    recent_videos = VideoHistory.objects.filter(
        user=user,
        created_at__gte=yesterday
    ).order_by('-created_at')

    print(f"📊 Videos created in last 24 hours: {recent_videos.count()}")
    print()

    if recent_videos.count() == 0:
        print("   No videos found")
        print()
        print("🔍 Checking for ANY videos...")
        all_videos = VideoHistory.objects.filter(user=user).order_by('-created_at')[:5]
        print(f"   Total videos: {all_videos.count()}")

        if all_videos:
            print()
            print("   Last 5 videos:")
            for video in all_videos:
                print(f"      Video #{video.get_sequential_number()}")
                print(f"         ID: {video.id}")
                print(f"         Created: {video.created_at}")
                print(f"         Status: {video.status}")
                print(f"         Model: {video.model_used}")
                print(f"         Project: {video.project.name if video.project else 'None'}")
                print()
    else:
        for video in recent_videos:
            print(f"   Video #{video.get_sequential_number()}:")
            print(f"      ID: {video.id}")
            print(f"      Created: {video.created_at}")
            print(f"      Status: {video.status}")
            print(f"      Model: {video.model_used}")
            print(f"      Source Image: {video.source_image_id if hasattr(video, 'source_image_id') else 'N/A'}")
            print(f"      Project: {video.project.name if video.project else 'None'}")
            print(f"      Video URL: {video.video_url if video.video_url else 'None'}")
            print(f"      Thumbnail: {video.thumbnail_url if video.thumbnail_url else 'None'}")

            # Check agent
            if hasattr(video, 'agent') and video.agent:
                print(f"      Agent: {video.agent.display_name}")
            else:
                print(f"      Agent: None")

            # Check for agent contributions
            from core.models.agents_registry import AgentContribution
            contributions = AgentContribution.objects.filter(video=video)
            if contributions.exists():
                print(f"      ✅ {contributions.count()} agent contribution(s) tracked")
                for contrib in contributions:
                    print(f"         - {contrib.agent.display_name}: {contrib.contribution_type}")
            else:
                print(f"      ⚠️  No agent contributions")

            print()

    # Check for recent LoRA-trained images that might have been animated
    print()
    print("🖼️  Checking recent LoRA-trained images...")
    recent_images = ImageHistory.objects.filter(
        user=user,
        style='lora-trained',
        created_at__gte=yesterday
    ).order_by('-created_at')

    print(f"   LoRA-trained images in last 24 hours: {recent_images.count()}")

    if recent_images:
        print()
        for img in recent_images:
            print(f"   Image #{img.get_sequential_number()}:")
            print(f"      ID: {img.id}")
            print(f"      Created: {img.created_at}")
            print(f"      Model: {img.model_used}")
            print(f"      Project: {img.project.name if img.project else 'None'}")

            # Check if this image has associated videos
            videos_from_image = VideoHistory.objects.filter(
                user=user,
                prompt__icontains=str(img.id)
            )
            print(f"      Videos created from this image: {videos_from_image.count()}")

            print()

    print("=" * 80)

if __name__ == "__main__":
    check_recent_videos()
