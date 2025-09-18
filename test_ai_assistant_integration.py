#!/usr/bin/env python
"""
Test the AI-Powered Personal Assistant with Unified Memory Manager
==================================================================

This script tests:
1. Real AI responses instead of templates
2. UnifiedMemoryManager integration
3. Bidirectional communication between Assistant and Agents
4. Memory storage and retrieval
5. Cross-agent insights
"""

import os
import sys
import django
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from core.unified_memory_manager import UnifiedMemoryManager
from backend.agents.ai_enforced_base import AIEnforcedAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

User = get_user_model()


class TestIncomeBuilderAgent(AIEnforcedAgent):
    """Test agent that simulates income generation activities"""

    async def execute(self, task: str):
        """Simulate executing a task and storing memories"""
        # Use real AI to generate response
        response = self.generate_ai_text(
            f"Generate a brief report about completing this task: {task}",
            context="You are an income generation agent",
            task_type="report"
        )

        # Store agent action in memory
        self.store_agent_memory(
            'agent_action',
            f"Completed task: {task}",
            importance=7,
            task=task,
            result=response[:100]
        )

        # Store learning
        self.store_agent_memory(
            'agent_learning',
            f"Learned efficient method for: {task}",
            importance=6
        )

        return {
            'success': True,
            'response': response,
            'task': task
        }


def test_ai_assistant():
    """Test the AI-powered Personal Assistant"""
    print("\n" + "=" * 80)
    print("🤖 Testing AI-Powered Personal Assistant with Unified Memory")
    print("=" * 80 + "\n")

    # Get or create test user
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        print(f"✅ Created test user: {user.username}")

    # Initialize components
    print("\n📦 Initializing components...")
    assistant = EnhancedPersonalAIAssistant(user)
    memory_manager = UnifiedMemoryManager(user)

    # Test 1: Real AI Response
    print("\n1️⃣ Testing Real AI Response (not templates)...")
    print("-" * 40)

    test_message = "What can you help me with today?"
    response = assistant.process_message(test_message)

    print(f"User: {test_message}")
    print(f"Assistant: {response.get('response', 'No response')[:200]}...")
    print(f"AI Generated: {response.get('ai_generated', False)}")
    print(f"Model Used: {response.get('model', 'Unknown')}")
    print(f"Confidence: {response.get('confidence', 0):.2f}")

    # Check if it's actually AI-generated (not template)
    is_template = any(template_phrase in response.get('response', '') for template_phrase in [
        "I can help you find opportunities",
        "Based on your skills in",
        "Your profile is currently"
    ])

    if not is_template and response.get('ai_generated'):
        print("✅ Response is AI-generated, not a template!")
    else:
        print("⚠️ Response appears to be template-based")

    # Test 2: Memory Storage
    print("\n2️⃣ Testing Memory Storage via UnifiedMemoryManager...")
    print("-" * 40)

    # Store various types of memories
    memories_to_store = [
        ('preference', 'I prefer remote work opportunities', 7),
        ('goal', 'I want to earn $5000 per month through freelancing', 8),
        ('skill', 'Expert in Python and machine learning', 6),
        ('project', 'Building an AI-powered content platform', 7)
    ]

    for mem_type, content, importance in memories_to_store:
        memory = memory_manager.store_memory(
            user=user,
            source='assistant',
            memory_type=mem_type,
            content=content,
            importance=importance
        )
        print(f"✅ Stored {mem_type} memory: {content[:50]}...")

    # Test 3: Agent Activity Simulation
    print("\n3️⃣ Testing Agent Activities and Memory Storage...")
    print("-" * 40)

    # Create test agent
    agent = TestIncomeBuilderAgent(agent_name='IncomeBuilder', user=user)

    # Execute agent task
    import asyncio
    result = asyncio.run(agent.execute("Find high-paying freelance opportunities"))
    print(f"Agent executed: {result['task']}")
    print(f"Agent response: {result['response'][:100]}...")

    # Test 4: Retrieve Agent Activities
    print("\n4️⃣ Testing Retrieval of Agent Activities...")
    print("-" * 40)

    activities = memory_manager.get_agent_activities(user, limit=5)
    print(f"Found {len(activities)} agent activities:")
    for activity in activities:
        print(f"  - {activity['source']}: {activity['content'][:50]}...")

    # Test 5: Cross-Agent Insights
    print("\n5️⃣ Testing Cross-Agent Insights...")
    print("-" * 40)

    insights = memory_manager.get_cross_agent_insights(user)
    print(f"Total learnings: {insights['total_learnings']}")
    print(f"Active agents: {insights['active_agents']}")
    print(f"Key patterns: {len(insights['key_patterns'])}")
    print(f"Recommendations: {len(insights['recommendations'])}")

    # Test 6: Assistant References Agent Work
    print("\n6️⃣ Testing Assistant Referencing Agent Work...")
    print("-" * 40)

    context_message = "What have my agents been working on?"
    context_response = assistant.process_message(context_message)

    print(f"User: {context_message}")
    print(f"Assistant: {context_response.get('response', '')[:200]}...")

    # Check if assistant mentions agent activities
    if 'agent' in context_response.get('response', '').lower() or \
       'IncomeBuilder' in context_response.get('response', ''):
        print("✅ Assistant successfully referenced agent activities!")
    else:
        print("⚠️ Assistant may not be referencing agent activities")

    # Test 7: Memory Statistics
    print("\n7️⃣ Testing Memory Statistics...")
    print("-" * 40)

    stats = memory_manager.get_memory_statistics(user)
    print(f"Total memories: {stats['total_memories']}")
    print("Memory types:")
    for mem_type, count in stats['by_type'].items():
        print(f"  - {mem_type}: {count}")
    print("Memory sources:")
    for source, count in stats['by_source'].items():
        print(f"  - {source}: {count}")

    # Test 8: Bidirectional Communication
    print("\n8️⃣ Testing Bidirectional Communication...")
    print("-" * 40)

    # Agent gets assistant context
    assistant_context = agent.get_assistant_context()
    print(f"Agent retrieved assistant context:")
    print(f"  - Recent conversations: {len(assistant_context.get('recent_conversations', []))}")
    print(f"  - User preferences: {len(assistant_context.get('user_preferences', []))}")
    print(f"  - Communication style: {assistant_context.get('communication_style', 'Not set')}")

    # Agent shares with other agents
    agent.share_with_agents(
        "Found high-paying opportunity: $150/hour Python consulting",
        ['JobMatcher', 'RevenueOptimizer'],
        importance=9
    )
    print("✅ Agent shared memory with other agents")

    # Final Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)

    test_results = {
        'AI Response': response.get('ai_generated', False),
        'Memory Storage': stats['total_memories'] > 0,
        'Agent Activities': len(activities) > 0,
        'Cross-Agent Insights': insights['total_learnings'] > 0,
        'Bidirectional Comm': len(assistant_context) > 0
    }

    all_passed = all(test_results.values())

    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    if all_passed:
        print("\n🎉 All tests PASSED! The AI Assistant is fully integrated!")
    else:
        print("\n⚠️ Some tests failed. Check the configuration.")

    return all_passed


if __name__ == "__main__":
    try:
        success = test_ai_assistant()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)