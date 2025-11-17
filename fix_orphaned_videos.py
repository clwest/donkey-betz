#!/usr/bin/env python
"""
Session 122: Fix orphaned videos that have a session but no project

This script links videos to their session's project if they're missing the association.
Run with: python fix_orphaned_videos.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory

def fix_orphaned_videos():
    """Find and fix videos that have a session but no project"""

    # Find videos with session but no project
    orphaned = VideoHistory.objects.filter(
        session__isnull=False,  # Has a session
        project__isnull=True,    # But no project
        session__project__isnull=False  # And the session HAS a project
    )

    count = orphaned.count()
    print(f"\n🔍 Found {count} orphaned videos with sessions that have projects")

    if count == 0:
        print("✅ No orphaned videos found! All videos are properly linked.")
        return

    # Show details
    print("\n📹 Orphaned videos:")
    for video in orphaned:
        print(f"  - Video {str(video.id)[:8]}...: '{video.prompt[:50]}...' → Session: {str(video.session.session_id)[:8]} → Project: {video.session.project.name}")

    # Fix them
    print(f"\n🔧 Fixing {count} orphaned videos...")
    fixed_count = 0

    for video in orphaned:
        video.project = video.session.project
        video.save(update_fields=['project'])
        fixed_count += 1
        print(f"  ✅ Linked video {str(video.id)[:8]}... to project: {video.session.project.name}")

    print(f"\n🎉 Fixed {fixed_count} videos!")
    print(f"   All videos are now properly linked to their projects.")

if __name__ == '__main__':
    fix_orphaned_videos()
