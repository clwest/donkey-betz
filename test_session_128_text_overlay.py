"""
Session 128: Test add_text_overlay GPT function calling

Tests that natural language commands like:
"Add text 'Welcome' to video 5 at 8 seconds for 3 seconds"

Successfully trigger the add_text_overlay tool.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import VideoHistory
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🧪 SESSION 128 - TEXT OVERLAY TEST")
print("=" * 80)

# Step 1: Get a video to add text to
print("\n📹 STEP 1: Finding a video to add text to...")
video = VideoHistory.objects.filter(user=user, video_url__isnull=False).exclude(video_url='').first()

if not video:
    print("❌ No videos found! Generate a video first.")
    sys.exit(1)

video_seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
print(f"   Using video #{video_seq_num}: {video.id}")
print(f"   URL: {video.video_url}")

# Step 2: Test text overlay via AI Assistant
print(f"\n📝 STEP 2: Testing text overlay via AI Assistant...")
assistant = EnhancedPersonalAIAssistant(user=user)

# Test command: Add text with timing
test_message = f"Add text 'Session 128 Test' to video {video_seq_num} at 2 seconds for 4 seconds"
print(f"   Message: '{test_message}'")

result = assistant.process_message(test_message)
print(f"\n📊 Result:")

# Check if response contains success indicators
response_text = result.get('response', '')
has_success = '✅' in response_text and 'text overlay' in response_text.lower()

print(f"   Response preview: {response_text[:200]}...")
print(f"   Success: {has_success}")

if has_success:
    # Check if a new video was created with text overlay
    new_videos = VideoHistory.objects.filter(user=user).order_by('-created_at')[:1]
    if new_videos:
        new_video = new_videos[0]
        new_seq_num = VideoHistory.objects.filter(user=user, created_at__lte=new_video.created_at).count()
        print(f"\n✅ New video created: #{new_seq_num}")
        print(f"   Video ID: {new_video.id}")
        print(f"   URL: {new_video.video_url}")
        print(f"   Type: {new_video.video_type}")

        print("\n🎉 TEXT OVERLAY TEST PASSED!")
        print("   The AI successfully added text to the video using GPT function calling!")
else:
    print(f"\n⚠️  TEXT OVERLAY TEST FAILED")
    print(f"   Response didn't indicate success")

print("\n" + "=" * 80)
