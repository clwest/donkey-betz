#!/usr/bin/env python3
"""
Test Stability AI structure control API for variations.
"""
import os
import sys
import django
import requests

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from django.contrib.auth import get_user_model

User = get_user_model()

# Get all users and their image counts
users = User.objects.all()
print(f"Found {users.count()} users:")
for user in users:
    image_count = ImageHistory.objects.filter(user=user).count()
    print(f"  - {user.username}: {image_count} images")

# Get the user with the most images
user_with_images = None
max_images = 0
for user in users:
    count = ImageHistory.objects.filter(user=user).count()
    if count > max_images:
        max_images = count
        user_with_images = user

if not user_with_images or max_images == 0:
    print("❌ No users with images found")
    sys.exit(1)

print(f"\n✅ Using user: {user_with_images.username} ({max_images} images)")

# Get the first image for testing
image = ImageHistory.objects.filter(user=user_with_images).order_by('created_at').first()
print(f"✅ Testing with image: {image.id}")
print(f"   Prompt: {image.prompt[:60] if image.prompt else 'No prompt'}...")
print(f"   File path: {image.file_path[:80]}...")

# Get image data
if image.file_path.startswith('data:'):
    import base64
    image_data = base64.b64decode(image.file_path.split(',')[1])
else:
    from django.conf import settings
    file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
    if not os.path.exists(file_full_path):
        print(f"❌ File not found: {file_full_path}")
        sys.exit(1)
    with open(file_full_path, 'rb') as f:
        image_data = f.read()

print(f"✅ Loaded image data: {len(image_data)} bytes")

# Get API key
stability_key = os.getenv('STABILITY_API_KEY')
if not stability_key:
    print("❌ STABILITY_API_KEY not found in environment")
    sys.exit(1)

print(f"✅ API key found: {stability_key[:8]}...")

# Test the API call
url = "https://api.stability.ai/v2beta/stable-image/control/structure"
files = {'image': image_data}
data_params = {
    'prompt': 'creative variation',
    'control_strength': 0.6,
    'output_format': 'png'
}
headers = {
    "Authorization": f"Bearer {stability_key}",
    "Accept": "image/*"
}

print(f"\n🚀 Testing Stability AI structure control API...")
print(f"   URL: {url}")
print(f"   Params: {data_params}")

response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

print(f"\n📊 Response:")
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   ❌ Error: {response.text}")
else:
    print(f"   ✅ Success! Image size: {len(response.content)} bytes")
