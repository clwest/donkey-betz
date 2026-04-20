#!/usr/bin/env python3
"""
Test script to verify the Session 134 project association fix.

This script:
1. Generates an image using TrainedCreationAgent
2. Verifies the image is linked to the project in the database
3. Confirms the image appears in the project's asset list
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CharacterModel, ImageHistory, CreativeProject
from core.agents.training import TrainedCreationAgent

User = get_user_model()


def test_project_association():
    """Test that images are properly linked to projects."""
    print("=" * 80)
    print("🧪 Testing Project Association Fix - Session 134")
    print("=" * 80)

    # Step 1: Get user and project
    user = User.objects.get(username='admin')
    print(f"\n✅ User: {user.username}")

    project = CreativeProject.objects.filter(user=user).first()
    if not project:
        print("❌ No projects found for user")
        return False

    print(f"✅ Project: {project.name} ({project.id})")

    # Step 2: Get completed character model
    character_model = CharacterModel.objects.filter(
        user=user,
        training_status='completed'
    ).first()

    if not character_model:
        print("❌ No completed character models found")
        return False

    print(f"✅ Character Model: {character_model.name}")

    # Step 3: Count images in project BEFORE generation
    before_count = ImageHistory.objects.filter(
        user=user,
        project=project
    ).count()
    print(f"\n📊 Images in project BEFORE: {before_count}")

    # Step 4: Generate image using TrainedCreationAgent
    print(f"\n🚀 Generating test image with TrainedCreationAgent...")
    agent = TrainedCreationAgent(user=user, project_id=str(project.id))

    result = agent.execute(
        prompt="a minimalist tech logo for Session 134 testing",
        character_model_name=character_model.name,
        width=1024,
        height=1024,
        num_outputs=1,
        lora_scale=0.8
    )

    # Step 5: Check result
    print(f"\n📊 Generation Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")

    if not result.get('success'):
        print(f"   Error: {result.get('error')}")
        return False

    image_ids = result.get('image_ids', [])
    print(f"   Image IDs: {image_ids}")

    # Step 6: Count images in project AFTER generation
    after_count = ImageHistory.objects.filter(
        user=user,
        project=project
    ).count()
    print(f"\n📊 Images in project AFTER: {after_count}")
    print(f"   New images: {after_count - before_count}")

    # Step 7: Verify the new image is linked to the project
    if image_ids:
        new_image = ImageHistory.objects.get(id=image_ids[0])
        print(f"\n🔍 Verifying new image:")
        print(f"   Image ID: {new_image.id}")
        print(f"   Sequential #: {new_image.get_sequential_number()}")
        print(f"   Model: {new_image.model_used}")
        print(f"   Project: {new_image.project.name if new_image.project else 'None'}")
        print(f"   Project ID: {new_image.project.id if new_image.project else 'None'}")

        # Check if project matches
        if new_image.project and new_image.project.id == project.id:
            print(f"\n✅ SUCCESS! Image is correctly linked to project!")
            return True
        else:
            print(f"\n❌ FAILED! Image is not linked to the correct project!")
            print(f"   Expected: {project.id}")
            print(f"   Actual: {new_image.project.id if new_image.project else 'None'}")
            return False
    else:
        print(f"\n❌ FAILED! No image IDs returned")
        return False


if __name__ == "__main__":
    success = test_project_association()

    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED - Project association is working correctly!")
    else:
        print("❌ TEST FAILED - Project association is broken")
    print("=" * 80)

    sys.exit(0 if success else 1)
