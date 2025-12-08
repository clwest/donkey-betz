#!/usr/bin/env python3
"""
Session 136: Backfill agent field for existing VideoHistory records

This script assigns all existing videos to the VideoAgent template since
the VideoGenerationAgent is responsible for creating all videos.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import VideoHistory
from core.models.agents_registry import UnifiedAgentTemplate
from django.contrib.auth import get_user_model

User = get_user_model()

def backfill_video_agents():
    print("=" * 80)
    print("🎬 Backfilling Agent Field for VideoHistory")
    print("=" * 80)
    print()

    # Look up VideoAgent template
    try:
        video_agent = UnifiedAgentTemplate.objects.get(name="VideoAgent", is_active=True)
        print(f"✅ Found VideoAgent: {video_agent.display_name}")
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"❌ VideoAgent template not found!")
        print(f"   Please ensure the VideoAgent is registered in the system.")
        return

    print()

    # Find all videos without an agent assigned
    videos_without_agent = VideoHistory.objects.filter(agent__isnull=True)
    total_count = videos_without_agent.count()

    print(f"📊 Found {total_count} videos without agent assignment")
    print()

    if total_count == 0:
        print("✅ All videos already have agents assigned!")
        return

    # Update all videos
    print(f"🔄 Assigning VideoAgent to {total_count} videos...")
    updated_count = videos_without_agent.update(agent=video_agent)

    print(f"✅ Updated {updated_count} videos")
    print()

    # Verify the update
    remaining = VideoHistory.objects.filter(agent__isnull=True).count()
    print("=" * 80)
    print(f"📊 Verification:")
    print(f"   - Total videos: {VideoHistory.objects.count()}")
    print(f"   - With agent: {VideoHistory.objects.filter(agent__isnull=False).count()}")
    print(f"   - Without agent: {remaining}")
    print("=" * 80)

    if remaining == 0:
        print()
        print("🎉 Success! All videos now have agents assigned!")
        print()
        print("ℹ️  Note: AgentContribution records will be created automatically")
        print("   by the post_save signal when new videos are created.")
    else:
        print()
        print(f"⚠️  Warning: {remaining} videos still missing agents")

if __name__ == "__main__":
    backfill_video_agents()
