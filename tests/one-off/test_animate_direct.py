"""
Direct test of image animation WITHOUT VideoAgent
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import ImageHistory
from content.video_provider import runway_provider

# Get image 271
try:
    image = ImageHistory.objects.filter(user__username='admin').order_by('created_at')[270]  # 0-indexed
    print(f"✅ Found image: {image.id}")
    print(f"   Created: {image.created_at}")
    print(f"   Prompt: {image.prompt if hasattr(image, 'prompt') else 'N/A'}")
    
    # Get URL using proper method
    image_url = image.get_full_url()
    print(f"   URL: {image_url[:100]}...")
    
    # Call Runway directly
    print(f"\n🎬 Calling Runway ML...")
    result = runway_provider.image_to_video(
        image_url=image_url,
        prompt='natural motion',
        duration=5,
        quality="veo3.1_fast"
    )
    
    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    print(f"   Task ID: {result.task_id}")
    print(f"   Error: {result.error_message}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
