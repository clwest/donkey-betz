"""
Session 128: Complete End-to-End Test

Tests both DaVinci tools in sequence:
1. Text overlay - "Add text 'Test' to video X"
2. Color grading - "Make video Y look vintage"

Verifies GPT function calling works for both tools.
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
print("🧪 SESSION 128 - COMPLETE END-TO-END TEST")
print("=" * 80)

# Get initial video count
initial_count = VideoHistory.objects.filter(user=user).count()
print(f"\n📊 Initial video count: {initial_count}")

# Step 1: Get a video to work with
print("\n📹 STEP 1: Finding a video for testing...")
video = VideoHistory.objects.filter(user=user, video_url__isnull=False).exclude(video_url='').first()

if not video:
    print("❌ No videos found! Generate a video first.")
    sys.exit(1)

video_seq_num = VideoHistory.objects.filter(user=user, created_at__lte=video.created_at).count()
print(f"   Using video #{video_seq_num}: {video.id}")

assistant = EnhancedPersonalAIAssistant(user=user)

# Test 1: Text Overlay
print("\n" + "=" * 80)
print("📝 TEST 1: TEXT OVERLAY")
print("=" * 80)

text_message = f"Add text 'Session 128' to video {video_seq_num} at 1 second for 3 seconds in the lower_third position"
print(f"Message: '{text_message}'")

text_result = assistant.process_message(text_message)
print(f"\nResult:")

# Check if response contains success indicators
response_text = text_result.get('response', '')
has_success = '✅' in response_text and 'text overlay' in response_text.lower()

print(f"  Response preview: {response_text[:150]}...")
print(f"  Success: {has_success}")

if has_success:
    print(f"  ✅ Text overlay applied!")

    # Get the new video with text
    text_video = VideoHistory.objects.filter(user=user).order_by('-created_at').first()
    text_seq_num = VideoHistory.objects.filter(user=user, created_at__lte=text_video.created_at).count()
    print(f"  New video: #{text_seq_num}")
else:
    print(f"  ❌ Failed: Response didn't indicate success")
    print("\n⚠️  Stopping test - text overlay failed")
    sys.exit(1)

# Test 2: Color Grading
print("\n" + "=" * 80)
print("🎨 TEST 2: COLOR GRADING")
print("=" * 80)

# Use the text overlay video for color grading
grade_message = f"Apply vintage color grading to video {text_seq_num}"
print(f"Message: '{grade_message}'")

grade_result = assistant.process_message(grade_message)
print(f"\nResult:")

# Check if response contains success indicators
grade_response_text = grade_result.get('response', '')
grade_has_success = '✅' in grade_response_text and 'color grading' in grade_response_text.lower()

print(f"  Response preview: {grade_response_text[:150]}...")
print(f"  Success: {grade_has_success}")

if grade_has_success:
    print(f"  ✅ Color grading applied!")

    # Get the new video with color grading
    graded_video = VideoHistory.objects.filter(user=user).order_by('-created_at').first()
    graded_seq_num = VideoHistory.objects.filter(user=user, created_at__lte=graded_video.created_at).count()
    print(f"  New video: #{graded_seq_num}")
else:
    print(f"  ❌ Failed: Response didn't indicate success")
    print("\n⚠️  Color grading failed")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 80)
print("🎉 SESSION 128 - ALL TESTS PASSED!")
print("=" * 80)

final_count = VideoHistory.objects.filter(user=user).count()
videos_created = final_count - initial_count

print(f"\n📊 Summary:")
print(f"  Initial videos: {initial_count}")
print(f"  Final videos: {final_count}")
print(f"  Videos created: {videos_created}")
print(f"\n✅ Text overlay tool: WORKING")
print(f"✅ Color grading tool: WORKING")
print(f"\n🚀 DaVinci Resolve video editing tools are fully integrated with GPT function calling!")
print("\n" + "=" * 80)
