#!/usr/bin/env python3
"""
Test to verify video_editing_agent tool is being called by GPT-5-mini.
Session 155: Debugging agent connectivity issues.
"""
import os
import sys
import django
import json

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()

# Get user (assuming user ID 1 exists)
user = User.objects.first()
if not user:
    print("❌ No user found in database")
    sys.exit(1)

print(f"✅ Testing with user: {user.username} (ID: {user.id})")

# Create assistant instance
assistant = EnhancedPersonalAIAssistant(user=user)

# Test message
test_message = "Upscale video number 1 to 2x"

print(f"\n📝 Test message: '{test_message}'")
print(f"🤖 Sending to GPT-5-mini to see if it triggers video_editing_agent tool...\n")

# Process message
try:
    # Add some fake context
    context = {
        'project_id': None,
        'session_id': None
    }

    result = assistant.process_message(test_message, context)

    print(f"\n✅ Result received:")
    print(json.dumps(result, indent=2, default=str))

    # Check if tool was called
    if 'tool_calls' in result:
        print(f"\n🔧 Tool calls detected: {len(result['tool_calls'])}")
        for tool_call in result['tool_calls']:
            print(f"  - Tool: {tool_call.get('name')}")
            print(f"    Arguments: {tool_call.get('arguments')}")
    else:
        print(f"\n⚠️ No tool_calls in result!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
