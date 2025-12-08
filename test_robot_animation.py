"""
Test robot animation with motion prompt for picking up bat and ball

This script tests the fixed robot images from "Ai Content Generation Company" project
with a Runway ML motion prompt designed for bat/ball pickup motion.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from core.agents import VideoAgent

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🤖⚾ ROBOT ANIMATION TEST - BAT AND BALL PICKUP!")
print("=" * 80)

# Step 1: Get image 272 (the robot we've been working with)
print("\n🔍 STEP 1: Finding robot image 272...")
image = ImageHistory.objects.filter(user=user).order_by('created_at')[271]  # 0-indexed
seq_num = ImageHistory.objects.filter(user=user, created_at__lte=image.created_at).count()

print(f"   Found: Image #{seq_num}")
print(f"   ID: {image.id}")
print(f"   file_path: {image.file_path}")
print(f"   Is data URI: {image.file_path.startswith('data:')}")

if image.file_path.startswith('data:'):
    print(f"\n   ❌ ERROR: Image still has data URI storage!")
    print(f"   The fix script may not have run successfully.")
    sys.exit(1)

print(f"   ✅ Image has proper PNG file path!")

# Step 2: Craft the motion prompt
motion_prompt = "The robot's metallic arms reach down smoothly, grasp a baseball bat in one hand and a baseball in the other, then lift them up triumphantly with steady mechanical motion, slight head tilt upward"

print(f"\n🎬 STEP 2: Testing animation with Runway ML...")
print(f"   Motion Prompt: '{motion_prompt}'")
print(f"   Duration: 5 seconds")
print(f"   Model: gen4_turbo (correct image-to-video model)")

# Step 3: Animate!
video_agent = VideoAgent(user=user)

print(f"\n⚡ STEP 3: Calling VideoAgent.animate_image()...")
result = video_agent.animate_image(
    image_id=str(image.id),
    motion_prompt=motion_prompt,
    duration=5,
    quality='gen4_turbo'  # Correct model for image-to-video
)

# Step 4: Check results
print(f"\n📊 STEP 4: Results:")
print(f"   Success: {result.get('success', False)}")

if result.get('success'):
    task_id = result.get('task_id', 'N/A')
    status = result.get('status', 'N/A')
    print(f"   ✅ Task ID: {task_id}")
    print(f"   Status: {status}")
    print(f"\n🎉 ANIMATION STARTED SUCCESSFULLY!")
    print(f"   The robot will be animated picking up the bat and ball!")
    print(f"   Processing will take ~2-3 minutes...")
    print(f"   The video will appear in your gallery automatically!")
else:
    error_msg = result.get('error', result.get('message', 'Unknown error'))
    print(f"   ❌ Error: {error_msg}")
    print(f"\n💡 Troubleshooting:")
    print(f"   - Check if image file exists: media/{image.file_path}")
    print(f"   - Verify Runway ML credits remaining")
    print(f"   - Check logs for API errors")

print("\n" + "=" * 80)
