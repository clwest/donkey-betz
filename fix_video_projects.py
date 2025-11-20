#!/usr/bin/env python3
"""
Fix Video-Project Associations - Session 135 Follow-up

This script finds videos without project associations and links them to the correct project.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory, CreativeProject
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_video_projects():
    """Find and fix videos without project associations."""
    print("=" * 80)
    print("🔧 Fixing Video-Project Associations - Session 135")
    print("=" * 80)
    print()

    # Get user
    user = User.objects.get(username='admin')
    print(f"👤 User: {user.username}")
    print()

    # Find all videos without projects
    orphaned_videos = VideoHistory.objects.filter(
        user=user,
        project__isnull=True
    ).order_by('-created_at')

    print(f"📊 Videos without project: {orphaned_videos.count()}")
    print()

    if orphaned_videos.count() == 0:
        print("✅ No orphaned videos found!")
        print()
        print("=" * 80)
        return

    # Display orphaned videos
    print("🎬 Orphaned Videos:")
    for video in orphaned_videos:
        print(f"   Video #{video.get_sequential_number()}")
        print(f"      ID: {video.id}")
        print(f"      Created: {video.created_at}")
        print(f"      Status: {video.status}")
        print(f"      Model: {video.model_used}")
        print(f"      Prompt: {video.prompt[:80]}...")
        print()

    # Find the "AI Content Generation Company" project
    print("🔍 Looking for 'AI Content Generation Company' project...")
    projects = CreativeProject.objects.filter(
        user=user,
        name__icontains='AI Content'
    )

    if not projects.exists():
        print("   ❌ Project not found!")
        print()
        print("   Available projects:")
        all_projects = CreativeProject.objects.filter(user=user).order_by('-created_at')[:10]
        for proj in all_projects:
            print(f"      - {proj.name} (ID: {proj.id})")
        print()
        print("   Please specify the correct project name in the script.")
        print()
        print("=" * 80)
        return

    project = projects.first()
    print(f"   ✅ Found: {project.name}")
    print(f"      ID: {project.id}")
    print()

    # Count current videos in project
    current_video_count = VideoHistory.objects.filter(
        user=user,
        project=project
    ).count()
    print(f"📊 Current videos in '{project.name}': {current_video_count}")
    print()

    # Ask for confirmation (commented out for automation)
    # response = input(f"Associate {orphaned_videos.count()} videos with '{project.name}'? (y/n): ")
    # if response.lower() != 'y':
    #     print("❌ Cancelled")
    #     return

    # Fix the associations
    print(f"🔧 Associating {orphaned_videos.count()} videos with '{project.name}'...")
    print()

    fixed_count = 0
    for video in orphaned_videos:
        video.project = project
        video.save()
        print(f"   ✅ Video #{video.get_sequential_number()} → {project.name}")
        fixed_count += 1

    print()
    print(f"✅ Fixed {fixed_count} video associations!")
    print()

    # Verify the fix
    new_video_count = VideoHistory.objects.filter(
        user=user,
        project=project
    ).count()
    print(f"📊 New video count in '{project.name}': {new_video_count}")
    print(f"   (was {current_video_count}, added {fixed_count})")
    print()

    print("🎉 Videos should now appear in the project gallery!")
    print()
    print("=" * 80)

if __name__ == "__main__":
    fix_video_projects()
