#!/usr/bin/env python3
"""
Verify Project Video Associations - Session 135 Follow-up

Quick script to verify all videos in "AI Content Generation Company" project.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory, CreativeProject
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_project_videos():
    """Verify all videos in the project."""
    print("=" * 80)
    print("✅ Verifying Project Video Associations")
    print("=" * 80)
    print()

    # Get user
    user = User.objects.get(username='admin')

    # Find "AI Content Generation Company" project
    project = CreativeProject.objects.filter(
        user=user,
        name__icontains='AI Content'
    ).first()

    if not project:
        print("❌ Project not found!")
        return

    print(f"📁 Project: {project.name}")
    print(f"   ID: {project.id}")
    print()

    # Get all videos in this project
    videos = VideoHistory.objects.filter(
        user=user,
        project=project
    ).order_by('-created_at')

    print(f"📊 Total videos in project: {videos.count()}")
    print()

    if videos.count() == 0:
        print("   No videos found in project")
        print()
        print("=" * 80)
        return

    # Display all videos
    print("🎬 Videos in project:")
    for video in videos:
        print(f"   Video #{video.get_sequential_number()}")
        print(f"      ID: {video.id}")
        print(f"      Created: {video.created_at}")
        print(f"      Status: {video.status}")
        print(f"      Model: {video.model_used}")
        print(f"      Video URL: {video.video_url if video.video_url else 'None'}")
        print()

    print("=" * 80)
    print(f"✅ SUMMARY: '{project.name}' has {videos.count()} video(s)")
    print("=" * 80)

if __name__ == "__main__":
    verify_project_videos()
