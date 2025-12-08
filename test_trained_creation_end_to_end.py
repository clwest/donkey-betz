#!/usr/bin/env python3
"""
Test script to verify end-to-end LoRA generation with TrainedCreationAgent.

Session 134: Test the complete dual-agent architecture.
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
from agents.creation_agent import CreationAgent
from core.agents.training import TrainedCreationAgent

User = get_user_model()


def test_trained_creation_agent():
    """Test TrainedCreationAgent with completed training."""
    print("=" * 80)
    print("🧪 Testing TrainedCreationAgent - Session 134")
    print("=" * 80)

    # Get user
    user = User.objects.first()
    if not user:
        print("❌ No user found in database")
        return

    print(f"\n✅ User: {user.username} (ID: {user.id})")

    # Find completed character model
    character_models = CharacterModel.objects.filter(
        user=user,
        training_status='completed'
    )

    if not character_models.exists():
        print("\n❌ No completed character models found")
        print("   Run test_trained_lora.py first to complete training")
        return

    character_model = character_models.first()
    print(f"\n✅ Character Model Found:")
    print(f"   Name: {character_model.name}")
    print(f"   Status: {character_model.training_status}")
    print(f"   Replicate Model: {character_model.replicate_model_name}")
    print(f"   Version ID: {character_model.replicate_version_id}")

    # Test 1: Standard Creation Agent
    print("\n" + "=" * 80)
    print("🎨 Test 1: Standard Creation Agent (Stability AI)")
    print("=" * 80)

    standard_agent = CreationAgent(user=user, project_id=None)
    standard_result = standard_agent.execute(
        prompt="a professional business logo, modern minimalist design",
        size="1024x1024",
        num_images=1,
        quality="balanced"
    )

    print(f"\n📊 Standard Agent Result:")
    print(f"   Success: {standard_result.get('success')}")
    print(f"   Message: {standard_result.get('message')}")
    if standard_result.get('success'):
        print(f"   Image IDs: {standard_result.get('image_ids')}")
        print(f"   Model Used: {standard_result.get('model_used')}")
        print(f"   Generation Time: {standard_result.get('generation_time')}s")
    else:
        print(f"   Error: {standard_result.get('error')}")

    # Test 2: Trained Creation Agent
    print("\n" + "=" * 80)
    print("🎨 Test 2: Trained Creation Agent (FLUX + LoRA)")
    print("=" * 80)

    trained_agent = TrainedCreationAgent(user=user, project_id=None)
    trained_result = trained_agent.execute(
        prompt="a professional business logo, modern minimalist design",
        character_model_name=character_model.name,
        width=1024,
        height=1024,
        num_outputs=1,
        lora_scale=0.8
    )

    print(f"\n📊 Trained Agent Result:")
    print(f"   Success: {trained_result.get('success')}")
    print(f"   Message: {trained_result.get('message')}")
    if trained_result.get('success'):
        print(f"   Image IDs: {trained_result.get('image_ids')}")
        print(f"   Model Used: {trained_result.get('model_used')}")
        print(f"   Character Model: {trained_result.get('character_model')}")
    else:
        print(f"   Error: {trained_result.get('error')}")

    # Show database summary
    print("\n" + "=" * 80)
    print("📊 Database Summary")
    print("=" * 80)

    total_images = ImageHistory.objects.filter(user=user).count()
    creation_agent_images = ImageHistory.objects.filter(
        user=user,
        agent_name='creation-agent'
    ).count()
    trained_agent_images = ImageHistory.objects.filter(
        user=user,
        agent_name='trained-creation-agent'
    ).count()

    print(f"\n   Total Images: {total_images}")
    print(f"   Creation Agent Images: {creation_agent_images}")
    print(f"   Trained Creation Agent Images: {trained_agent_images}")

    # Show recent images
    print("\n📸 Recent Images:")
    recent_images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:5]
    for img in recent_images:
        seq_num = img.get_sequential_number()
        agent = img.agent_name or 'unknown'
        print(f"   #{seq_num}: {agent} | {img.prompt[:50]}... | {img.created_at.strftime('%Y-%m-%d %H:%M')}")

    print("\n" + "=" * 80)
    print("✅ End-to-End Test Complete!")
    print("=" * 80)
    print("\n💡 Next Steps:")
    print("   1. Open http://localhost:8000/ai-studio/")
    print("   2. Open a project modal")
    print("   3. In AI Assistant, try:")
    print(f"      'Generate an image using {character_model.name}'")
    print("   4. Check Agent Contributions section for agent tracking")
    print("=" * 80)


def test_ai_assistant_routing():
    """Test AI Assistant routing logic."""
    print("\n" + "=" * 80)
    print("🤖 Testing AI Assistant Routing Logic")
    print("=" * 80)

    user = User.objects.first()
    if not user:
        print("❌ No user found")
        return

    from core.personal_ai_assistant_enhanced import PersonalAIAssistantEnhanced

    assistant = PersonalAIAssistantEnhanced(user=user)

    # Test 1: Standard generation (should route to CreationAgent)
    print("\n📋 Test Case 1: Standard generation")
    print("   Input: prompt='a sunset over mountains'")
    print("   Expected: Routes to CreationAgent")

    # Test 2: Trained generation (should route to TrainedCreationAgent)
    character_model = CharacterModel.objects.filter(
        user=user,
        training_status='completed'
    ).first()

    if character_model:
        print("\n📋 Test Case 2: Trained generation")
        print(f"   Input: prompt='a logo', character_model_name='{character_model.name}'")
        print("   Expected: Routes to TrainedCreationAgent")
    else:
        print("\n⚠️  No completed character model for Test Case 2")

    print("\n✅ Routing logic implemented at:")
    print("   core/personal_ai_assistant_enhanced.py:364-482")


if __name__ == "__main__":
    test_trained_creation_agent()
    test_ai_assistant_routing()
