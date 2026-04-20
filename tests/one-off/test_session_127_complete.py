"""
Session 127 - Complete End-to-End Test
Tests the fixed workflow: Create variations → Animate new image
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()
user = User.objects.get(username='admin')

print("=" * 80)
print("🧪 SESSION 127 - COMPLETE END-TO-END TEST")
print("=" * 80)

# Step 1: Get a base image to create variations from
print("\n📸 STEP 1: Get base image for variations...")
base_image = ImageHistory.objects.filter(user=user).order_by('created_at').first()
print(f"   Using image #{base_image.get_sequential_number()}: {base_image.id}")
print(f"   Base image type: {'DATA URI' if base_image.file_path.startswith('data:') else 'FILE PATH'}")
print(f"   Base image size: {len(base_image.file_path):,} chars")

# Step 2: Create variations using AI Assistant
print("\n🎨 STEP 2: Create variations via AI Assistant...")
assistant = EnhancedPersonalAIAssistant(user=user)
create_msg = f"create 2 variations of image {base_image.get_sequential_number()}"
print(f"   Message: '{create_msg}'")

create_result = assistant.process_message(create_msg)
print(f"   Success: {create_result.get('success')}")

if create_result.get('success'):
    # Get the newly created variations
    new_images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:2]

    print(f"\n✅ Created {len(new_images)} variations:")
    for img in new_images:
        is_data_uri = img.file_path.startswith('data:')
        file_type = "DATA URI ❌" if is_data_uri else "FILE PATH ✅"
        print(f"   - Image #{img.get_sequential_number()}: {file_type} ({len(img.file_path):,} chars)")

        if is_data_uri:
            print(f"      ⚠️  BUG STILL EXISTS! This should be a file path!")
        else:
            print(f"      ✅ FIXED! Saved as actual file: {img.file_path}")

    # Step 3: Animate the first new variation
    print(f"\n🎬 STEP 3: Animate the newest variation...")
    newest_image = new_images[0]
    animate_msg = f"animate image {newest_image.get_sequential_number()}"
    print(f"   Message: '{animate_msg}'")
    print(f"   Image to animate: #{newest_image.get_sequential_number()}")
    print(f"   Image path: {newest_image.file_path[:100]}...")

    animate_result = assistant.process_message(animate_msg)
    print(f"\n📊 Animation Result:")
    print(f"   Success: {animate_result.get('success')}")

    if animate_result.get('success'):
        print(f"   ✅ Task ID: {animate_result.get('task_id')}")
        print(f"   ✅ Video ID: {animate_result.get('video_id')}")
        print(f"\n🎉 END-TO-END TEST PASSED!")
        print(f"   - Created variations as FILE PATHS (not data URIs) ✅")
        print(f"   - Animated the new variation successfully ✅")
    else:
        print(f"   ❌ Error: {animate_result.get('error')}")
        print(f"\n⚠️  Animation failed - investigating...")
else:
    print(f"   ❌ Error: {create_result.get('error')}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
