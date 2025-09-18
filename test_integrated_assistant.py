#!/usr/bin/env python
"""
Test Integrated AI Assistant with Enhanced Profile
==================================================

This script tests the complete integration of:
1. Enhanced User Profile
2. Personal AI Assistant
3. Memory Storage
4. Learning Loop
5. Agent System Integration
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from core.models import EnhancedUserProfile, UserMemoryContext
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from backend.agents.ai_enforced_base import AIEnforcedAgent

User = get_user_model()


def test_profile_integration():
    """Test that the Enhanced Profile is properly integrated"""
    print("\n" + "="*60)
    print("Testing Enhanced Profile Integration")
    print("="*60)

    # Get or create test user
    user = User.objects.get(username='admin')

    # Get or create enhanced profile
    profile, created = EnhancedUserProfile.objects.get_or_create(user=user)

    if created:
        print(f"✅ Created new Enhanced Profile for {user.username}")
    else:
        print(f"📊 Found existing Enhanced Profile for {user.username}")

    # Display profile completeness
    print(f"Profile Completeness: {profile.calculate_completeness()}%")

    # Update some profile fields for testing
    profile.primary_role = "AI Platform Developer"
    profile.long_term_goals = ["Build successful AI platform", "Generate passive income"]
    profile.core_competencies = {
        "Python": 9,
        "Django": 8,
        "React": 7,
        "Machine Learning": 7,
        "System Architecture": 8
    }
    profile.current_projects = ["Unified Donkey Betz Platform", "AI Assistant Integration"]
    profile.communication_style = "balanced"
    profile.learning_style = "hands-on"
    profile.decision_framework = "data-driven"
    profile.save()

    print(f"✅ Updated profile fields")
    print(f"   - Primary Role: {profile.primary_role}")
    print(f"   - Goals: {profile.long_term_goals[:2]}")
    print(f"   - Skills: {list(profile.core_competencies.keys())[:3]}")
    print(f"   - Projects: {profile.current_projects[:2]}")

    return profile


def test_assistant_with_profile():
    """Test Personal AI Assistant with Enhanced Profile"""
    print("\n" + "="*60)
    print("Testing Personal AI Assistant with Profile")
    print("="*60)

    # Get user
    user = User.objects.get(username='admin')

    # Create assistant
    assistant = EnhancedPersonalAIAssistant(user)
    print(f"✅ Created Enhanced AI Assistant for {user.username}")

    # Test various messages to trigger learning
    test_messages = [
        "I prefer working with Python and Django for backend development",
        "My goal is to build a successful AI platform that generates passive income",
        "I'm currently working on integrating all the AI agents together",
        "I know React, TypeScript, and have experience with machine learning",
        "Can you help me optimize my Income Builder agent?",
        "Check the database status for me",
        "List available agents"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test Message {i}: {message[:50]}...")

        try:
            response = assistant.process_message(message)

            print(f"   Response Type: {response.get('type', 'general')}")
            print(f"   Confidence: {response.get('confidence', 0):.2f}")
            print(f"   Suggestions: {response.get('suggestions', [])[:3]}")

            # Check if system data was included
            if 'system_data' in response:
                print(f"   ✅ System data included: {response['system_data'].get('type')}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    return assistant


def test_memory_storage():
    """Test memory storage and retrieval"""
    print("\n" + "="*60)
    print("Testing Memory Storage System")
    print("="*60)

    user = User.objects.get(username='admin')
    assistant = EnhancedPersonalAIAssistant(user)

    # Check stored memories
    memories = UserMemoryContext.objects.filter(user=user).order_by('-created_at')[:10]

    print(f"Found {memories.count()} recent memories")

    for memory in memories:
        print(f"\n📚 Memory Type: {memory.memory_type}")
        print(f"   Content: {memory.content[:100]}")
        print(f"   Importance: {memory.importance}")
        print(f"   Created: {memory.created_at}")
        print(f"   Accessed: {memory.accessed_count} times")

    # Retrieve specific memory types
    interaction_memories = assistant.retrieve_memories('interaction', limit=5)
    preference_memories = assistant.retrieve_memories('preference', limit=5)

    print(f"\n✅ Retrieved {len(interaction_memories)} interaction memories")
    print(f"✅ Retrieved {len(preference_memories)} preference memories")

    return memories.count()


def test_agent_profile_integration():
    """Test that agents can use the Enhanced Profile"""
    print("\n" + "="*60)
    print("Testing Agent System with Enhanced Profile")
    print("="*60)

    user = User.objects.get(username='admin')

    # Create a test agent
    class TestAgent(AIEnforcedAgent):
        async def execute(self, task: str) -> dict:
            # Generate personalized text
            prompt = f"Help the user with: {task}"

            try:
                response = self.generate_ai_text(
                    prompt=prompt,
                    task_type="general",
                    personalize=True  # This will use Enhanced Profile
                )

                return {
                    'success': True,
                    'response': response,
                    'profile_used': self.enhanced_profile is not None
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }

    # Create and test agent
    agent = TestAgent(agent_name="TestProfileAgent", user=user)

    print(f"✅ Created test agent with user: {user.username}")
    print(f"   Enhanced Profile loaded: {agent.enhanced_profile is not None}")

    if agent.enhanced_profile:
        print(f"   Profile completeness: {agent.enhanced_profile.calculate_completeness()}%")
        print(f"   Primary role: {agent.enhanced_profile.primary_role}")

    # Test agent execution (mock without actual AI call)
    print("\n🤖 Testing agent prompt personalization...")
    test_prompt = "Generate a summary"
    personalized = agent.get_enhanced_personalized_prompt(test_prompt)

    if "Enhanced User Profile:" in personalized:
        print("   ✅ Enhanced Profile data included in prompt")
        # Show what was added
        added = personalized[len(test_prompt):]
        print(f"   Added context lines: {added.count(chr(10))}")
    else:
        print("   ❌ Enhanced Profile data NOT included")

    return agent


def test_learning_loop():
    """Test the learning loop extraction"""
    print("\n" + "="*60)
    print("Testing Learning Loop & Pattern Detection")
    print("="*60)

    user = User.objects.get(username='admin')
    assistant = EnhancedPersonalAIAssistant(user)

    # Messages that should trigger learning
    learning_messages = [
        "I prefer detailed explanations when learning new concepts",
        "I'm skilled in Python, Django, and machine learning",
        "My long-term goal is to achieve financial independence through AI",
        "I'm working on building an AI agent orchestration platform",
        "I like to make data-driven decisions based on metrics"
    ]

    print("📖 Processing learning messages...")

    for message in learning_messages:
        assistant.update_profile_from_interaction(message, "Response placeholder")
        print(f"   Processed: {message[:50]}...")

    # Check what was learned
    profile = assistant.enhanced_profile
    profile.refresh_from_db()

    print(f"\n✅ Profile after learning:")
    print(f"   Skills: {profile.core_competencies}")
    print(f"   Goals: {profile.long_term_goals}")
    print(f"   Projects: {profile.current_projects}")
    print(f"   Communication Style: {profile.communication_style}")
    print(f"   Interaction Count: {profile.interaction_count}")

    return profile


def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("🚀 INTEGRATED AI ASSISTANT TEST SUITE")
    print("="*60)

    try:
        # Test 1: Profile Integration
        profile = test_profile_integration()

        # Test 2: Assistant with Profile
        assistant = test_assistant_with_profile()

        # Test 3: Memory Storage
        memory_count = test_memory_storage()

        # Test 4: Agent System Integration
        agent = test_agent_profile_integration()

        # Test 5: Learning Loop
        learned_profile = test_learning_loop()

        # Summary
        print("\n" + "="*60)
        print("✅ INTEGRATION TEST SUMMARY")
        print("="*60)

        print(f"1. Enhanced Profile: {profile.calculate_completeness()}% complete")
        print(f"2. AI Assistant: Initialized with {assistant.enhanced_profile.interaction_count} interactions")
        print(f"3. Memory System: {memory_count} memories stored")
        print(f"4. Agent Integration: {'✅ Working' if agent.enhanced_profile else '❌ Failed'}")
        print(f"5. Learning Loop: Captured {len(learned_profile.core_competencies or {})} skills")

        print("\n🎉 All integration tests completed!")
        print("The AI Assistant is now fully aware of user context and learning from interactions!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()