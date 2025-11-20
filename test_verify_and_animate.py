"""
Verify new images are files (not data URIs) and test animation
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
print("📊 VERIFICATION: New Images Are Files (Not Data URIs)")
print("=" * 80)

# Get the 2 newest images (the variations we just created)
new_images = ImageHistory.objects.filter(user=user).order_by('-created_at')[:2]

for img in new_images:
    is_data_uri = img.file_path.startswith('data:')
    file_type = "❌ DATA URI (BUG!)" if is_data_uri else "✅ FILE PATH (FIXED!)"

    print(f"\nImage #{img.get_sequential_number()}:")
    print(f"  ID: {img.id}")
    print(f"  Type: {file_type}")
    print(f"  Path: {img.file_path}")
    print(f"  Size: {len(img.file_path):,} chars")

# Now test animating the newest image
print("\n" + "=" * 80)
print("🎬 ANIMATION TEST: Animate the newest variation")
print("=" * 80)

newest_image = new_images[0]
print(f"\nAnimating image #{newest_image.get_sequential_number()}")
print(f"Path: {newest_image.file_path}")

assistant = EnhancedPersonalAIAssistant(user=user)
animate_msg = f"animate image {newest_image.get_sequential_number()}"

print(f"\nSending: '{animate_msg}'")
result = assistant.process_message(animate_msg)

# Check if animation was triggered
if "video" in str(result).lower() or "animat" in str(result).lower():
    print("\n✅ SUCCESS! Animation triggered!")
    print(f"Response: {result}")
else:
    print(f"\n⚠️  Response: {result}")

print("\n" + "=" * 80)
