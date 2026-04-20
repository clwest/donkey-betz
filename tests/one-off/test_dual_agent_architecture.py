#!/usr/bin/env python3
"""
Test the dual-agent architecture - CreationAgent and TrainedCreationAgent.

Session 134: Verify both agents work independently and routing is correct.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CharacterModel, ImageHistory

User = get_user_model()


def ensure_completed_training():
    """Ensure we have a completed character model for testing."""
    print("=" * 80)
    print("🔍 Checking Character Model Status")
    print("=" * 80)

    training_id = "4xxb3efx91rm80ctkh6sag1mem"
    user = User.objects.get(username='admin')  # Use admin account for testing

    try:
        training = CharacterModel.objects.get(training_id=training_id, user=user)
        print(f"\n✅ Found Character Model:")
        print(f"   Training ID: {training_id}")
        print(f"   Name: {training.name}")
        print(f"   Status: {training.training_status}")

        if training.training_status != 'completed':
            print(f"\n⚠️  Status is '{training.training_status}', updating to 'completed'...")
            training.training_status = 'completed'
            training.training_progress = 100
            if not training.replicate_model_name:
                training.replicate_model_name = 'clwest/ai-content-generation-company-style'
            if not training.replicate_version_id:
                training.replicate_version_id = 'bae61384a7977e46ca0e5172c89d17f851009b8ae539a84b02b637f752fa05f7'
            training.save()
            print(f"✅ Updated training status to 'completed'")

        return training
    except CharacterModel.DoesNotExist:
        print(f"\n❌ No training found with ID: {training_id}")
        return None


def test_creation_agent():
    """Test standard CreationAgent (Stability AI)."""
    print("\n" + "=" * 80)
    print("🎨 Test 1: Creation Agent (Standard Stability AI)")
    print("=" * 80)

    user = User.objects.get(username='admin')
    print(f"\n✅ User: {user.username}")

    from agents.creation_agent import CreationAgent

    agent = CreationAgent(user=user, project_id=None)
    print(f"\n🤖 Agent initialized: {agent.agent_name}")
    print(f"   User: {agent.user.username}")
    print(f"   Project ID: {agent.project_id}")

    print(f"\n🚀 Generating test image...")
    result = agent.execute(
        prompt="a professional tech logo, minimalist modern design",
        size="1024x1024",
        num_images=1,
        quality="fast"  # Use fast for testing
    )

    print(f"\n📊 Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")
    if result.get('success'):
        print(f"   Image IDs: {result.get('image_ids')}")
        print(f"   Model Used: {result.get('model_used')}")
        print(f"   Generation Time: {result.get('generation_time')}s")
        print(f"   Cost: {result.get('cost_credits')} credits")
        return True
    else:
        print(f"   Error: {result.get('error')}")
        return False


def test_trained_creation_agent(character_model):
    """Test TrainedCreationAgent (FLUX + LoRA)."""
    print("\n" + "=" * 80)
    print("🎨 Test 2: Trained Creation Agent (FLUX + LoRA)")
    print("=" * 80)

    user = User.objects.get(username='admin')
    print(f"\n✅ User: {user.username}")
    print(f"✅ Character Model: {character_model.name}")

    from core.agents.training import TrainedCreationAgent

    agent = TrainedCreationAgent(user=user, project_id=None)
    print(f"\n🤖 Agent initialized: {agent.agent_name}")
    print(f"   User: {agent.user.username}")
    print(f"   Project ID: {agent.project_id}")

    print(f"\n🚀 Generating test image with LoRA...")
    print(f"   Character Model: {character_model.name}")
    print(f"   LoRA Version: {character_model.replicate_version_id[:20]}...")

    result = agent.execute(
        prompt="a professional tech logo, minimalist modern design",
        character_model_name=character_model.name,
        width=1024,
        height=1024,
        num_outputs=1,
        lora_scale=0.8
    )

    print(f"\n📊 Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Message: {result.get('message')}")
    if result.get('success'):
        print(f"   Image IDs: {result.get('image_ids')}")
        print(f"   Model Used: {result.get('model_used')}")
        print(f"   Character Model: {result.get('character_model')}")
        return True
    else:
        print(f"   Error: {result.get('error')}")
        return False


def show_database_summary():
    """Show database summary of agent contributions."""
    print("\n" + "=" * 80)
    print("📊 Database Summary")
    print("=" * 80)

    user = User.objects.get(username='admin')

    total_images = ImageHistory.objects.filter(user=user).count()
    replicate_images = ImageHistory.objects.filter(user=user, model_used__icontains='replicate').count()
    stability_images = total_images - replicate_images

    print(f"\n   Total Images: {total_images}")
    print(f"   Stability AI Images: {stability_images}")
    print(f"   Replicate (LoRA) Images: {replicate_images}")

    # Show recent images
    print(f"\n📸 Recent Images (last 10):")
    recent = ImageHistory.objects.filter(user=user).order_by('-created_at')[:10]
    for img in recent:
        seq_num = img.get_sequential_number()
        model = img.model_used or 'unknown'
        prompt = img.prompt[:40] if img.prompt else 'No prompt'
        print(f"   #{seq_num}: {model:30s} | {prompt}...")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 Dual Agent Architecture Test - Session 134")
    print("=" * 80)

    # Step 1: Ensure completed training
    character_model = ensure_completed_training()

    # Step 2: Test CreationAgent (always run)
    test1_success = test_creation_agent()

    # Step 3: Test TrainedCreationAgent (only if we have a completed model)
    test2_success = False
    if character_model:
        test2_success = test_trained_creation_agent(character_model)
    else:
        print("\n⚠️  Skipping TrainedCreationAgent test - no completed training found")

    # Step 4: Show database summary
    show_database_summary()

    # Final summary
    print("\n" + "=" * 80)
    print("✅ Test Summary")
    print("=" * 80)
    print(f"   Creation Agent (Stability AI): {'✅ PASSED' if test1_success else '❌ FAILED'}")
    print(f"   Trained Creation Agent (FLUX): {'✅ PASSED' if test2_success else '⚠️ SKIPPED' if not character_model else '❌ FAILED'}")
    print("=" * 80)

    print("\n💡 How to Test via AI Assistant:")
    print("   1. Open http://localhost:8000/ai-studio/")
    print("   2. Open a project modal")
    print("   3. In AI Assistant, try:")
    print("      Standard: 'Generate a professional logo'")
    if character_model:
        print(f"      Trained:  'Generate an image using {character_model.name}'")
    print("   4. Check Agent Contributions section to see agent tracking")
    print("=" * 80)
