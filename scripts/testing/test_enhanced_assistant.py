#!/usr/bin/env python
"""
Test the Enhanced Personal AI Assistant's database and system capabilities
"""
import os
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()

def test_enhanced_assistant():
    print("🧪 Testing Enhanced Personal AI Assistant with Profile System")
    print("=" * 60)

    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='assistant_test',
        defaults={'email': 'assistant@test.com'}
    )

    # Initialize enhanced assistant
    assistant = EnhancedPersonalAIAssistant(user)
    print("✅ Enhanced assistant initialized")
    print(f"✅ Enhanced profile created: {assistant.enhanced_profile}")

    # Test system status
    print("\n📊 Testing System Status:")
    status = assistant.get_system_status()
    print(f"  - Total Embeddings: {status.get('embeddings', {}).get('total_count', 0)}")
    print(f"  - Total Agents: {status.get('agents', {}).get('total_registered', 0)}")
    print(f"  - WebSocket Active: {status.get('websockets', {}).get('active', False)}")
    print(f"  - Platform Health: {status.get('platform', {}).get('health', 'unknown')}")
    print(f"  - Operational %: {status.get('platform', {}).get('operational_percentage', 0):.0f}%")

    # Test database query
    print("\n🔍 Testing Database Query:")
    result = assistant.execute_database_query(
        "SELECT COUNT(*) as count FROM django_content_type"
    )
    if result.get('success'):
        print(f"  - Content types in database: {result.get('data', [{}])[0].get('count', 0)}")
    else:
        print(f"  - Query failed: {result.get('error')}")

    # Test embeddings search
    print("\n🔎 Testing Embeddings Search:")
    embeddings = assistant.search_embeddings("income", limit=3)
    print(f"  - Found {len(embeddings)} embeddings matching 'income'")
    for emb in embeddings[:2]:
        print(f"    • {emb.get('content_text', emb.get('content', ''))[:50]}...")

    # Test system commands
    print("\n💬 Testing System Commands:")

    commands = [
        "check database status",
        "list agents",
        "check websocket status",
        "search embeddings for job"
    ]

    for cmd in commands:
        print(f"\n  Command: '{cmd}'")
        result = assistant.process_system_command(cmd)
        print(f"  Response: {result.get('response', 'No response')[:100]}...")

    # Test message processing with system awareness
    print("\n🤖 Testing Message Processing:")

    messages = [
        "How many embeddings are in the database?",
        "What agents are available?",
        "Is the system healthy?"
    ]

    for msg in messages:
        print(f"\n  User: {msg}")
        response = assistant.process_message(msg)
        print(f"  Assistant: {response.get('response')[:150]}...")
        if response.get('system_data'):
            print(f"  System Data Type: {response.get('system_data', {}).get('type')}")
        print(f"  Confidence: {response.get('confidence', 0):.2f}")

    # Test Enhanced Profile and Memory System
    print("\n🧠 Testing Enhanced Profile & Memory:")

    # Test storing memories
    messages_to_test = [
        "I prefer working in the morning when I have more energy",
        "My goal is to generate $5000 per month through automated income",
        "I decide to focus on AI-related opportunities first"
    ]

    for msg in messages_to_test:
        print(f"\n  Processing: {msg[:50]}...")
        response = assistant.process_message(msg)
        print(f"  Response stored as memory")

    # Retrieve and display memories
    print("\n📚 Retrieved Memories:")
    memories = assistant.retrieve_memories(limit=5)
    for memory in memories:
        print(f"  - [{memory.memory_type}] {memory.content[:50]}... (importance: {memory.importance})")

    # Check enhanced profile context
    print("\n🎯 Enhanced Profile Context:")
    context = assistant.get_enhanced_context()
    if 'enhanced_profile' in context:
        profile_data = context['enhanced_profile']
        print(f"  - Primary Role: {profile_data.get('primary_role', 'Not set')}")
        print(f"  - Communication Style: {profile_data.get('communication_style')}")
        print(f"  - Decision Framework: {profile_data.get('decision_framework')}")
        print(f"  - Timezone: {profile_data.get('timezone')}")

    # Check profile completeness
    completeness = assistant.enhanced_profile.calculate_completeness()
    print(f"\n  Profile Completeness: {completeness:.1f}%")

    print("\n" + "=" * 60)
    print("✅ Enhanced Assistant with Profile System Test Complete!")

if __name__ == "__main__":
    test_enhanced_assistant()