#!/usr/bin/env python
"""
Session 142: Backfill Agent Contributions for Existing Content

This script creates AgentContribution records for all existing content items
that don't have contributions yet. This brings the tracking rate from 46% to 95%+.

Usage:
    python backfill_agent_contributions_session_142.py [--dry-run]

Options:
    --dry-run    Show what would be created without actually creating records
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory, VideoHistory, MiniFigAsset
from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
from django.db import transaction

def get_or_none(model, **kwargs):
    """Helper to get object or None if doesn't exist"""
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def backfill_image_contributions(dry_run=False):
    """Backfill agent contributions for ImageHistory records"""
    print("\n" + "="*80)
    print("BACKFILLING IMAGE HISTORY CONTRIBUTIONS")
    print("="*80)

    # Get agents
    generation_agent = get_or_none(UnifiedAgentTemplate, name='image-generation-agent')
    editing_agent = get_or_none(UnifiedAgentTemplate, name='image-editing-agent')

    if not generation_agent:
        print("❌ ERROR: image-generation-agent not found!")
        return 0

    if not editing_agent:
        print("❌ ERROR: image-editing-agent not found!")
        return 0

    print(f"✅ Found image-generation-agent: {generation_agent.id}")
    print(f"✅ Found image-editing-agent: {editing_agent.id}")

    # Get all images without contributions
    images = ImageHistory.objects.filter(
        agent_contributions__isnull=True
    ).order_by('created_at')

    total = images.count()
    print(f"\n📊 Found {total} ImageHistory records without contributions")

    if total == 0:
        print("✅ All images already have contributions!")
        return 0

    created = 0

    for i, image in enumerate(images, 1):
        # Determine which agent based on image_type
        editing_types = [
            'background_removal', 'inpaint', 'erase', 'outpaint',
            'search_replace', 'recolor', 'structure'
        ]

        if image.image_type in editing_types:
            agent = editing_agent
            agent_name = "image-editing-agent"
        else:
            agent = generation_agent
            agent_name = "image-generation-agent"

        if dry_run:
            print(f"[DRY RUN] Would create contribution for Image {image.id} ({image.image_type}) → {agent_name}")
        else:
            try:
                contribution = AgentContribution.objects.create(
                    agent=agent,
                    image=image,
                    project=image.project,
                    contribution_type='generation' if image.image_type not in ['background_removal', 'inpaint', 'erase', 'outpaint', 'search_replace', 'recolor', 'structure'] else 'editing',
                    task_description=f"Backfilled: {image.image_type or 'generated'} image (prompt: {image.prompt[:50] if image.prompt else 'none'}...)",
                    execution_time_seconds=0.0
                )
                created += 1
                print(f"✅ [{i}/{total}] Created contribution for Image {image.id} ({image.image_type}) → {agent_name}")
            except Exception as e:
                print(f"❌ [{i}/{total}] Failed to create contribution for Image {image.id}: {e}")

    return created

def backfill_video_contributions(dry_run=False):
    """Backfill agent contributions for VideoHistory records"""
    print("\n" + "="*80)
    print("BACKFILLING VIDEO HISTORY CONTRIBUTIONS")
    print("="*80)

    # Get agent
    video_agent = get_or_none(UnifiedAgentTemplate, name='VideoAgent')

    if not video_agent:
        print("❌ ERROR: VideoAgent not found!")
        return 0

    print(f"✅ Found VideoAgent: {video_agent.id}")

    # Get all videos without contributions
    videos = VideoHistory.objects.filter(
        agent_contributions__isnull=True
    ).order_by('created_at')

    total = videos.count()
    print(f"\n📊 Found {total} VideoHistory records without contributions")

    if total == 0:
        print("✅ All videos already have contributions!")
        return 0

    created = 0

    for i, video in enumerate(videos, 1):
        if dry_run:
            print(f"[DRY RUN] Would create contribution for Video {video.id} ({video.video_type})")
        else:
            try:
                contribution = AgentContribution.objects.create(
                    agent=video_agent,
                    video=video,
                    project=video.project,
                    contribution_type='generation',
                    task_description=f"Backfilled: {video.video_type or 'generated'} video (prompt: {video.prompt[:50] if video.prompt else 'none'}...)",
                    execution_time_seconds=0.0
                )
                created += 1
                print(f"✅ [{i}/{total}] Created contribution for Video {video.id} ({video.video_type})")
            except Exception as e:
                print(f"❌ [{i}/{total}] Failed to create contribution for Video {video.id}: {e}")

    return created

def backfill_3d_contributions(dry_run=False):
    """Backfill agent contributions for MiniFigAsset records"""
    print("\n" + "="*80)
    print("BACKFILLING MINIFIG ASSET CONTRIBUTIONS")
    print("="*80)

    # Get agent
    three_d_agent = get_or_none(UnifiedAgentTemplate, name='three-d-generation-agent')

    if not three_d_agent:
        print("❌ ERROR: three-d-generation-agent not found!")
        return 0

    print(f"✅ Found three-d-generation-agent: {three_d_agent.id}")

    # Get all 3D models without contributions
    models = MiniFigAsset.objects.filter(
        agent_contributions__isnull=True
    ).order_by('created_at')

    total = models.count()
    print(f"\n📊 Found {total} MiniFigAsset records without contributions")

    if total == 0:
        print("✅ All 3D models already have contributions!")
        return 0

    created = 0

    for i, model in enumerate(models, 1):
        if dry_run:
            print(f"[DRY RUN] Would create contribution for MiniFig {model.id} ({model.status})")
        else:
            try:
                contribution = AgentContribution.objects.create(
                    agent=three_d_agent,
                    minifig_asset=model,
                    project=model.project,
                    contribution_type='generation',
                    task_description=f"Backfilled: 3D model '{model.title or 'Untitled'}' (status: {model.status})",
                    execution_time_seconds=0.0
                )
                created += 1
                print(f"✅ [{i}/{total}] Created contribution for MiniFig {model.id} ({model.status})")
            except Exception as e:
                print(f"❌ [{i}/{total}] Failed to create contribution for MiniFig {model.id}: {e}")

    return created

def main():
    """Main backfill function"""
    dry_run = '--dry-run' in sys.argv

    print("\n" + "="*80)
    print("SESSION 142: AGENT CONTRIBUTION BACKFILL")
    print("="*80)
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (will create records)'}")
    print(f"Time: {datetime.now()}")

    # Get current stats
    print("\n" + "="*80)
    print("CURRENT TRACKING STATISTICS")
    print("="*80)

    total_images = ImageHistory.objects.count()
    total_videos = VideoHistory.objects.count()
    total_3d = MiniFigAsset.objects.count()
    total_content = total_images + total_videos + total_3d

    total_contributions = AgentContribution.objects.count()

    print(f"📊 Total Content Items: {total_content}")
    print(f"   - Images: {total_images}")
    print(f"   - Videos: {total_videos}")
    print(f"   - 3D Models: {total_3d}")
    print(f"\n📊 Current Contributions: {total_contributions}")
    print(f"📊 Current Tracking Rate: {total_contributions/total_content*100:.1f}%")
    print(f"📊 Missing Contributions: {total_content - total_contributions}")

    # Backfill each content type
    images_created = backfill_image_contributions(dry_run)
    videos_created = backfill_video_contributions(dry_run)
    models_created = backfill_3d_contributions(dry_run)

    total_created = images_created + videos_created + models_created

    # Final stats
    print("\n" + "="*80)
    print("BACKFILL SUMMARY")
    print("="*80)

    if dry_run:
        print(f"[DRY RUN] Would create {total_created} agent contributions:")
        print(f"   - Images: {images_created}")
        print(f"   - Videos: {videos_created}")
        print(f"   - 3D Models: {models_created}")

        expected_contributions = total_contributions + total_created
        expected_rate = expected_contributions / total_content * 100
        print(f"\nExpected tracking rate after backfill: {expected_rate:.1f}%")

        print("\n✅ To apply changes, run without --dry-run flag:")
        print("   python backfill_agent_contributions_session_142.py")
    else:
        print(f"✅ Created {total_created} agent contributions:")
        print(f"   - Images: {images_created}")
        print(f"   - Videos: {videos_created}")
        print(f"   - 3D Models: {models_created}")

        # Get new stats
        new_contributions = AgentContribution.objects.count()
        new_rate = new_contributions / total_content * 100

        print(f"\n📊 NEW Tracking Statistics:")
        print(f"   - Total Contributions: {new_contributions}")
        print(f"   - Tracking Rate: {new_rate:.1f}%")
        print(f"   - Improvement: +{new_rate - (total_contributions/total_content*100):.1f}%")

        if new_rate >= 95:
            print(f"\n🎉 SUCCESS! Tracking rate {new_rate:.1f}% exceeds 95% target!")
        elif new_rate >= 90:
            print(f"\n✅ GOOD! Tracking rate {new_rate:.1f}% meets 90% minimum!")
        else:
            print(f"\n⚠️  WARNING: Tracking rate {new_rate:.1f}% below 90% target")

if __name__ == '__main__':
    main()
