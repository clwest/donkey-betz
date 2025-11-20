"""
Diagnostic script to trace animation routing through AI Assistant
"""
import os
import sys
import django
import logging

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Enable ALL logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)

print("="*80)
print("DIAGNOSTIC: Testing Animation Routing")
print("="*80)

try:
    from django.contrib.auth import get_user_model
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

    User = get_user_model()
    user = User.objects.get(username='admin')
    print(f"\n✅ Got user: {user.username}")

    # Initialize assistant
    print("\n📝 Initializing EnhancedPersonalAIAssistant...")
    assistant = EnhancedPersonalAIAssistant(user=user)
    print(f"✅ Assistant initialized: {type(assistant).__name__}")

    # Test message
    message = "animate image 271"
    print(f"\n📨 Sending message: '{message}'")
    print("-"*80)

    # Call process_message (this should trigger the routing logic)
    result = assistant.process_message(message)

    print("-"*80)
    print(f"\n📊 Result type: {type(result)}")
    print(f"📊 Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    print(f"\n📋 Full Result:")
    import json
    print(json.dumps(result, indent=2, default=str))

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
