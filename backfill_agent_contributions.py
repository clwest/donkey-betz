#!/usr/bin/env python3
"""
Session 136: Backfill AgentContribution records for existing content

This script creates AgentContribution records for all ImageHistory and VideoHistory
records that have both an agent and a project assigned, but don't yet have
a corresponding contribution record.

The backfill scripts updated the agent field, but signals only fire on creation,
not on updates. So we need to manually create the contribution records.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory
from core.models.agents_registry import AgentContribution
from agents.services import AgentContributionService

def backfill_contributions():
    print("=" * 80)
    print("📊 Backfilling Agent Contributions")
    print("=" * 80)
    print()

    service = AgentContributionService()

    # Track stats
    image_contributions_created = 0
    video_contributions_created = 0
    image_contributions_skipped = 0
    video_contributions_skipped = 0

    # === Process Images ===
    print("🖼️  Processing ImageHistory records...")
    print()

    # Find all images with agent + project
    images_with_agent_and_project = ImageHistory.objects.filter(
        agent__isnull=False,
        project__isnull=False
    ).select_related('agent', 'project', 'user')

    total_images = images_with_agent_and_project.count()
    print(f"   Found {total_images} images with agent + project")

    for image in images_with_agent_and_project:
        # Check if contribution already exists
        existing = AgentContribution.objects.filter(
            agent=image.agent,
            project=image.project,
            image=image
        ).exists()

        if existing:
            image_contributions_skipped += 1
            continue

        # Create contribution
        try:
            # Determine contribution type based on image type
            if image.image_type in ['generated', 'dreamup', 'control_sketch', 'control_structure', 'search_replace']:
                contribution_type = 'image_generation'
            elif image.image_type in ['edited', 'upscaled', 'upscaled_fast', 'upscaled_conservative',
                                       'upscaled_creative', 'background_removed', 'recolored',
                                       'erased', 'inpainted', 'outpainted', 'inpaint']:
                contribution_type = 'image_editing'
            elif image.image_type in ['trained', 'character']:
                contribution_type = 'trained_creation'
            else:
                contribution_type = 'image_generation'  # default

            service.track_image_contribution(
                agent=image.agent,
                project=image.project,
                image=image,
                contribution_type=contribution_type,
                task_description=f"Backfilled: {image.image_type} image"
            )
            image_contributions_created += 1

            if image_contributions_created % 10 == 0:
                print(f"   ✅ Created {image_contributions_created} image contributions...")

        except Exception as e:
            print(f"   ⚠️  Failed to create contribution for image {image.id}: {e}")

    print()
    print(f"   ✅ Image contributions created: {image_contributions_created}")
    print(f"   ⏭️  Image contributions skipped (already exist): {image_contributions_skipped}")
    print()

    # === Process Videos ===
    print("🎬 Processing VideoHistory records...")
    print()

    # Find all videos with agent + project
    videos_with_agent_and_project = VideoHistory.objects.filter(
        agent__isnull=False,
        project__isnull=False
    ).select_related('agent', 'project', 'user')

    total_videos = videos_with_agent_and_project.count()
    print(f"   Found {total_videos} videos with agent + project")

    for video in videos_with_agent_and_project:
        # Check if contribution already exists
        existing = AgentContribution.objects.filter(
            agent=video.agent,
            project=video.project,
            video=video
        ).exists()

        if existing:
            video_contributions_skipped += 1
            continue

        # Create contribution
        try:
            # Determine contribution type based on video type
            if video.video_type == 'text_to_video':
                contribution_type = 'video_generation'
            elif video.video_type == 'image_to_video':
                contribution_type = 'image_to_video'
            elif video.video_type == 'video_extension':
                contribution_type = 'video_extension'
            else:
                contribution_type = 'video_generation'  # default

            service.track_video_contribution(
                agent=video.agent,
                project=video.project,
                video=video,
                contribution_type=contribution_type,
                task_description=f"Backfilled: {video.video_type} video"
            )
            video_contributions_created += 1

            if video_contributions_created % 5 == 0:
                print(f"   ✅ Created {video_contributions_created} video contributions...")

        except Exception as e:
            print(f"   ⚠️  Failed to create contribution for video {video.id}: {e}")

    print()
    print(f"   ✅ Video contributions created: {video_contributions_created}")
    print(f"   ⏭️  Video contributions skipped (already exist): {video_contributions_skipped}")
    print()

    # === Summary ===
    print("=" * 80)
    print("📊 Backfill Summary")
    print("=" * 80)
    print(f"   Image contributions created: {image_contributions_created}")
    print(f"   Video contributions created: {video_contributions_created}")
    print(f"   Total contributions created: {image_contributions_created + video_contributions_created}")
    print()

    # Verify final counts
    total_contributions = AgentContribution.objects.count()
    image_contribs = AgentContribution.objects.filter(image__isnull=False).count()
    video_contribs = AgentContribution.objects.filter(video__isnull=False).count()

    print(f"📊 Verification:")
    print(f"   Total contributions in database: {total_contributions}")
    print(f"   Image contributions: {image_contribs}")
    print(f"   Video contributions: {video_contribs}")
    print("=" * 80)

    if image_contributions_created > 0 or video_contributions_created > 0:
        print()
        print("🎉 Success! Agent contributions backfilled!")
        print()
        print("ℹ️  Note: Future images/videos will have contributions")
        print("   created automatically by the post_save signal.")
    else:
        print()
        print("ℹ️  No new contributions needed - all existing content already tracked!")

if __name__ == "__main__":
    backfill_contributions()
