"""
Test animation with image 270 instead of 271
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()
user = User.objects.get(username='admin')

print("="*80)
print("🎬 TESTING ANIMATION WITH IMAGE #270")
print("="*80)

assistant = EnhancedPersonalAIAssistant(user=user)
message = "animate image 270"

print(f"\n📨 Message: '{message}'")
print(f"🔧 Calling assistant.process_message()...")

result = assistant.process_message(message)

print(f"\n📊 Result:")
print(f"   Success: {result.get('success')}")
print(f"   Agent: {result.get('agent_used')}")
if result.get('success'):
    print(f"   ✅ Task ID: {result.get('task_id')}")
    print(f"   ✅ Video ID: {result.get('video_id')}")
else:
    print(f"   ❌ Error: {result.get('error')}")

print("\n" + "="*80)
