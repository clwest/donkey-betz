"""
Test variations creation API directly to isolate the issue.
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory
from django.test import RequestFactory
from core.views_image import create_variations_view
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

# Get user
user = User.objects.get(username='admin')
logger.info(f"✅ User: {user.username}")

# Get image #1 (most recent blue robot)
images = ImageHistory.objects.filter(user=user).order_by('created_at')
if images.count() >= 1:
    image = images[0]  # First image
    logger.info(f"✅ Image #1: {image.id}")
    logger.info(f"   File path: {image.file_path}")
    logger.info(f"   Prompt: {image.prompt}")

    # Create request
    factory = RequestFactory()
    request_data = {
        'image_id': str(image.id),
        'count': 1,  # Just create 1 to test faster
        'prompt': 'creative variation'
    }

    request = factory.post(
        '/api/stability/create-variations/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    request.user = user

    logger.info(f"🚀 Calling create_variations_view...")
    response = create_variations_view(request)
    result = json.loads(response.content)

    logger.info(f"📦 Result: {result}")

    if result.get('success'):
        logger.info(f"✅ SUCCESS! Created {len(result.get('images', []))} variations")
        for img in result.get('images', []):
            logger.info(f"   - {img['image_id']}")
    else:
        logger.error(f"❌ FAILED: {result.get('error')}")
else:
    logger.error("❌ No images found!")
