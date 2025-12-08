"""
Test variations creation to debug the failure.
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
from core.agents import ImageEditingAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

# Get user
user = User.objects.get(username='admin')
logger.info(f"✅ User: {user.username}")

# Get image #5
images = ImageHistory.objects.filter(user=user).order_by('created_at')
if images.count() >= 5:
    image = images[4]  # 0-indexed, so image #5 is index 4
    logger.info(f"✅ Image #5: {image.id}")
    logger.info(f"   Prompt: {image.prompt}")
    logger.info(f"   File path: {image.file_path}")
    logger.info(f"   Created: {image.created_at}")

    # Get project
    project_id = str(image.project.id) if image.project else None
    logger.info(f"   Project ID: {project_id}")

    # Test with agent
    logger.info("\n🧪 Testing ImageEditingAgent.execute()...")
    agent = ImageEditingAgent(user=user, project_id=project_id)

    result = agent.execute(
        operation='variations',
        image_id=str(image.id),
        count=3,
        prompt='creative variation'
    )

    logger.info(f"\n📦 Result: {result}")

    if result.get('success'):
        logger.info(f"✅ SUCCESS! Created {len(result.get('image_ids', []))} variations")
    else:
        logger.error(f"❌ FAILED: {result.get('error')}")
else:
    logger.error(f"❌ Not enough images. Found {images.count()}, need at least 5")
