"""
Test the full variations flow: PersonalAssistant → ImageEditingAgent → View
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

# Get image #1
images = ImageHistory.objects.filter(user=user).order_by('created_at')
if images.count() >= 1:
    image = images[0]
    logger.info(f"✅ Image #1: {image.id}")
    logger.info(f"   Prompt: {image.prompt[:60]}...")

    # Simulate GPT-5.1 calling the tool via PersonalAssistant
    logger.info(f"\n🤖 Simulating GPT-5.1 tool call...")
    logger.info(f"   Tool: create_image_variations")
    logger.info(f"   Arguments: {{image_id: '1', count: 3}}")

    # Test 1: Call with sequential number (like GPT-5.1 would)
    logger.info(f"\n📝 Test 1: Using sequential number '1'")
    agent = ImageEditingAgent(user=user, project_id=None)
    result = agent.execute(
        operation='variations',
        image_id='1',  # Sequential number, not UUID!
        count=1,
        prompt='creative variation'
    )
    logger.info(f"   Result: {result}")

    # Test 2: Call with UUID (like direct API call)
    logger.info(f"\n📝 Test 2: Using UUID '{image.id}'")
    agent2 = ImageEditingAgent(user=user, project_id=None)
    result2 = agent2.execute(
        operation='variations',
        image_id=str(image.id),
        count=1,
        prompt='creative variation'
    )
    logger.info(f"   Result: {result2}")

else:
    logger.error("❌ No images found!")
