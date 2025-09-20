#!/usr/bin/env python
"""
Test to diagnose the Personal Assistant 500 error
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

User = get_user_model()


def test_assistant():
    print("\n" + "=" * 60)
    print("Testing Personal AI Assistant Error")
    print("=" * 60 + "\n")

    try:
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

        # Initialize assistant
        print("\n1. Initializing Enhanced Personal AI Assistant...")
        assistant = EnhancedPersonalAIAssistant(user)
        print("✅ Assistant initialized successfully")

        # Test simple message processing
        print("\n2. Testing message processing...")
        test_message = "Hello, what can you help me with?"
        print(f"Message: {test_message}")

        response_data = assistant.process_message(test_message)
        print("✅ Message processed successfully")
        print(f"Response: {response_data.get('response', 'No response')[:200]}...")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print("\n--- Full Traceback ---")
        traceback.print_exc()
        print("--- End Traceback ---")

        # Try to diagnose the issue
        print("\n🔍 Diagnosing the issue...")

        # Check if it's an import error
        try:
            from core.llm_enforcer import LLMEnforcer
            print("✅ LLMEnforcer import OK")
        except ImportError as ie:
            print(f"❌ LLMEnforcer import failed: {ie}")

        try:
            from core.unified_memory_manager import UnifiedMemoryManager
            print("✅ UnifiedMemoryManager import OK")
        except ImportError as ie:
            print(f"❌ UnifiedMemoryManager import failed: {ie}")

        # Check if it's a database issue
        try:
            from core.models import EnhancedUserProfile, UserMemoryContext
            print("✅ Model imports OK")

            # Check if profile exists
            profile = EnhancedUserProfile.objects.filter(user=user).first()
            if profile:
                print(f"✅ Enhanced profile exists for user")
            else:
                print(f"⚠️ No enhanced profile for user")

        except Exception as me:
            print(f"❌ Model check failed: {me}")

        # Check API keys
        import os
        if os.getenv('OPENAI_API_KEY'):
            print("✅ OpenAI API key is set")
        else:
            print("⚠️ OpenAI API key not set")

        if os.getenv('ANTHROPIC_API_KEY'):
            print("✅ Anthropic API key is set")
        else:
            print("⚠️ Anthropic API key not set")


if __name__ == "__main__":
    test_assistant()