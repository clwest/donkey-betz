#!/usr/bin/env python3
"""
Session 136: Backfill agent field for existing ImageHistory records

This script assigns existing images to the appropriate agent template based on their image_type:
- generated, dreamup, control_sketch, control_structure, search_replace → image-generation-agent
- edited, upscaled*, background_removed, recolored, erased, inpainted, outpainted → image-editing-agent
- trained, character → trained-creation-agent
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from core.models.agents_registry import UnifiedAgentTemplate
from django.contrib.auth import get_user_model

User = get_user_model()

def backfill_image_agents():
    print("=" * 80)
    print("🖼️  Backfilling Agent Field for ImageHistory")
    print("=" * 80)
    print()

    # Look up agent templates
    try:
        generation_agent = UnifiedAgentTemplate.objects.get(name="image-generation-agent", is_active=True)
        print(f"✅ Found image-generation-agent: {generation_agent.display_name}")
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"❌ image-generation-agent template not found!")
        return

    try:
        editing_agent = UnifiedAgentTemplate.objects.get(name="image-editing-agent", is_active=True)
        print(f"✅ Found image-editing-agent: {editing_agent.display_name}")
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"❌ image-editing-agent template not found!")
        return

    try:
        trained_agent = UnifiedAgentTemplate.objects.get(name="trained-creation-agent", is_active=True)
        print(f"✅ Found trained-creation-agent: {trained_agent.display_name}")
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"⚠️  trained-creation-agent template not found (optional)")
        trained_agent = None

    print()

    # Find all images without an agent assigned
    images_without_agent = ImageHistory.objects.filter(agent__isnull=True)
    total_count = images_without_agent.count()

    print(f"📊 Found {total_count} images without agent assignment")
    print()

    if total_count == 0:
        print("✅ All images already have agents assigned!")
        return

    # Define mapping of image types to agents
    generation_types = ['generated', 'dreamup', 'control_sketch', 'control_structure', 'search_replace']
    editing_types = [
        'edited', 'upscaled', 'upscaled_fast', 'upscaled_conservative', 'upscaled_creative',
        'background_removed', 'recolored', 'erased', 'inpainted', 'outpainted', 'inpaint'
    ]
    trained_types = ['trained', 'character']

    # Count by type
    generation_count = images_without_agent.filter(image_type__in=generation_types).count()
    editing_count = images_without_agent.filter(image_type__in=editing_types).count()
    trained_count = images_without_agent.filter(image_type__in=trained_types).count() if trained_agent else 0
    unknown_count = images_without_agent.exclude(
        image_type__in=generation_types + editing_types + trained_types
    ).count()

    print(f"📊 Breakdown by type:")
    print(f"   - Generation images: {generation_count}")
    print(f"   - Editing images: {editing_count}")
    if trained_agent:
        print(f"   - Trained images: {trained_count}")
    print(f"   - Unknown types: {unknown_count}")
    print()

    # Update generation images
    if generation_count > 0:
        print(f"🔄 Assigning image-generation-agent to {generation_count} images...")
        updated = images_without_agent.filter(image_type__in=generation_types).update(agent=generation_agent)
        print(f"✅ Updated {updated} generation images")
        print()

    # Update editing images
    if editing_count > 0:
        print(f"🔄 Assigning image-editing-agent to {editing_count} images...")
        updated = images_without_agent.filter(image_type__in=editing_types).update(agent=editing_agent)
        print(f"✅ Updated {updated} editing images")
        print()

    # Update trained images
    if trained_agent and trained_count > 0:
        print(f"🔄 Assigning trained-creation-agent to {trained_count} images...")
        updated = images_without_agent.filter(image_type__in=trained_types).update(agent=trained_agent)
        print(f"✅ Updated {updated} trained images")
        print()

    # Handle unknown types by defaulting to generation agent
    if unknown_count > 0:
        print(f"⚠️  Found {unknown_count} images with unknown types:")
        unknown_images = images_without_agent.exclude(
            image_type__in=generation_types + editing_types + trained_types
        )
        unknown_types = unknown_images.values_list('image_type', flat=True).distinct()
        for img_type in unknown_types:
            count = unknown_images.filter(image_type=img_type).count()
            print(f"   - {img_type}: {count}")

        print(f"🔄 Defaulting unknown types to image-generation-agent...")
        updated = unknown_images.update(agent=generation_agent)
        print(f"✅ Updated {updated} unknown type images")
        print()

    # Verify the update
    remaining = ImageHistory.objects.filter(agent__isnull=True).count()
    print("=" * 80)
    print(f"📊 Verification:")
    print(f"   - Total images: {ImageHistory.objects.count()}")
    print(f"   - With agent: {ImageHistory.objects.filter(agent__isnull=False).count()}")
    print(f"   - Without agent: {remaining}")

    if remaining == 0:
        # Show breakdown by agent
        gen_count = ImageHistory.objects.filter(agent=generation_agent).count()
        edit_count = ImageHistory.objects.filter(agent=editing_agent).count()
        print()
        print(f"   Agent breakdown:")
        print(f"   - image-generation-agent: {gen_count}")
        print(f"   - image-editing-agent: {edit_count}")
        if trained_agent:
            train_count = ImageHistory.objects.filter(agent=trained_agent).count()
            print(f"   - trained-creation-agent: {train_count}")

    print("=" * 80)

    if remaining == 0:
        print()
        print("🎉 Success! All images now have agents assigned!")
        print()
        print("ℹ️  Note: AgentContribution records will be created automatically")
        print("   by the post_save signal when new images are created.")
    else:
        print()
        print(f"⚠️  Warning: {remaining} images still missing agents")

if __name__ == "__main__":
    backfill_image_agents()
