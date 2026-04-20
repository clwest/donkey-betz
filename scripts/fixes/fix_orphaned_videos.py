#!/usr/bin/env python3
"""
Session 135: Fix orphaned videos - associate with "AI Content Generation Company" project

This script finds videos without project association and links them to the user's primary project.
Run with: python fix_orphaned_videos.py
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

def fix_orphaned_videos():
    """Find and fix videos that have no project association"""
    print("=" * 80)
    print("🔧 Fixing Orphaned Videos - Session 135")
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

    print(f"📁 Target Project: {project.name}")
    print(f"   ID: {project.id}")
    print()

    # Find orphaned videos (videos without project)
    orphaned_videos = VideoHistory.objects.filter(
        user=user,
        project__isnull=True
    ).order_by('created_at')

    print(f"📊 Found {orphaned_videos.count()} orphaned video(s)")
    print()

    if orphaned_videos.count() == 0:
        print("✅ No orphaned videos found!")
        print()
        print("=" * 80)
        return

    # Fix each orphaned video
    for video in orphaned_videos:
        print(f"🔧 Fixing Video #{video.get_sequential_number()}")
        print(f"   ID: {video.id}")
        print(f"   Status: {video.status}")
        print(f"   Created: {video.created_at}")
        print(f"   Current project: {video.project}")
        print()

        # Associate with project
        video.project = project
        video.save()

        print(f"   ✅ Now associated with: {project.name}")
        print()

    # Verify fix
    project_videos = VideoHistory.objects.filter(
        user=user,
        project=project
    ).count()

    print("=" * 80)
    print(f"✅ FIX COMPLETE!")
    print(f"   Project '{project.name}' now has {project_videos} video(s)")
    print("=" * 80)

if __name__ == "__main__":
    fix_orphaned_videos()
