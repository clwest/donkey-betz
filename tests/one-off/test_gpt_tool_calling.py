#!/usr/bin/env python3
"""
Test script to see what GPT-5 extracts from natural language requests.
Session 134: Debugging why character_model_name isn't being extracted.
"""

import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()

def test_tool_extraction():
    """Test what parameters GPT-5 extracts from natural language."""
    print("=" * 80)
    print("🧪 Testing GPT-5 Tool Calling - Session 134")
    print("=" * 80)

    user = User.objects.get(username='admin')
    assistant = EnhancedPersonalAIAssistant(user=user)

    test_prompts = [
        "Generate a professional logo",
        "Generate an image using AI content generation company style",
        "Generate an image using ai-content-generation-company-style",
        "Create an image with the ai-content-generation-company-style model"
    ]

    for prompt in test_prompts:
        print(f"\n{'=' * 80}")
        print(f"📝 Test Prompt: {prompt}")
        print(f"{'=' * 80}")

        # Call the assistant
        context = {'project_id': None}
        response = assistant.process_message(prompt, context)

        print(f"\n✅ Response:")
        print(json.dumps(response, indent=2))
        print(f"\n{'=' * 80}")

if __name__ == "__main__":
    test_tool_extraction()
