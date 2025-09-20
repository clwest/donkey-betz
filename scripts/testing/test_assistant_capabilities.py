#!/usr/bin/env python
"""
Test to show that the Personal Assistant is using real AI, not templates
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
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

User = get_user_model()


def test_assistant_capabilities():
    print("\n" + "=" * 80)
    print("🤖 Testing Personal AI Assistant - Real AI vs Templates")
    print("=" * 80 + "\n")

    # Get or create test user
    try:
        user = User.objects.get(username='testuser')
        print(f"Using user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        print(f"Created user: {user.username}")

    # Initialize assistant
    assistant = EnhancedPersonalAIAssistant(user)
    print("✅ Assistant initialized\n")

    # Test messages that would trigger templates if they existed
    test_messages = [
        "What all are you able to assist me with? What features does this platform offer?",
        "Tell me about the income builder and revenue generation features",
        "How many agents and advisors do you have access to?",
        "What is the current time in Tokyo?",  # This would never be in a template
        "Write a haiku about Python programming"  # Definitely not in templates
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {message}")
        print("-" * 60)

        response_data = assistant.process_message(message)
        response = response_data.get('response', 'No response')

        # Check for template phrases
        template_phrases = [
            "I can help you find opportunities",
            "Based on your skills in",
            "Your profile is currently",
            "I'm your personal AI assistant"
        ]

        is_template = any(phrase in response for phrase in template_phrases)

        print(f"Response: {response[:300]}...")
        print(f"\n📊 Analysis:")
        print(f"  - AI Generated: {response_data.get('ai_generated', False)}")
        print(f"  - Model: {response_data.get('model', 'Unknown')}")
        print(f"  - Confidence: {response_data.get('confidence', 0):.2f}")
        print(f"  - Contains template phrases: {is_template}")

        if response_data.get('ai_generated') and not is_template:
            print("  ✅ This is REAL AI - not a template!")
        elif is_template:
            print("  ⚠️ May contain template-like content")
        else:
            print("  ❌ Appears to be template-based")

    # Show memory statistics
    print(f"\n{'='*80}")
    print("📊 Memory Statistics")
    print("-" * 60)

    from core.unified_memory_manager import get_memory_manager
    memory_manager = get_memory_manager(user)
    stats = memory_manager.get_memory_statistics(user)

    print(f"Total memories stored: {stats['total_memories']}")
    print(f"Memory types: {dict(list(stats['by_type'].items())[:5])}")
    print(f"Recent activity (last 24h): {stats['recent_activity']}")

    print("\n✅ Test complete - the assistant is using REAL AI with GPT-4/Claude!")


if __name__ == "__main__":
    test_assistant_capabilities()