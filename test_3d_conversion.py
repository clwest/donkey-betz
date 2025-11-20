"""
Test 3D conversion now that Replicate is back online!
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import ImageHistory, CreativeProject
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant

User = get_user_model()
user = User.objects.get(username='admin')

# Get the project
project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

print("=" * 80)
print("🎨 TESTING 3D CONVERSION - Replicate is back online!")
print("=" * 80)

# Get a robot image to convert
image = ImageHistory.objects.filter(user=user, project=project).order_by('-created_at').first()

if image:
    print(f"\n📸 Using image: {image.file_path[:60]}...")
    print(f"   ID: {str(image.id)[:8]}...")
    
    # Create assistant with project context
    assistant = EnhancedPersonalAIAssistant(user)
    assistant.project = project
    
    # Simulate the tool call directly
    print(f"\n🔧 Calling convert_to_3d tool...")
    
    result = assistant._tool_convert_to_3d({
        'image_id': str(image.id),
        'project_id': str(project.id)
    })
    
    print(f"\n📊 Result:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Message: {result.get('message', 'No message')}")
    
    if result.get('success'):
        print(f"\n✅ 3D CONVERSION SUCCESSFUL!")
        print(f"   Asset ID: {result.get('minifig_id', 'Unknown')}")
        print(f"\n🎉 Replicate is working! 3D tool is fully operational!")
    else:
        print(f"\n❌ 3D conversion failed:")
        print(f"   Error: {result.get('error', 'Unknown error')}")

else:
    print("\n❌ No images found in project!")

print("\n" + "=" * 80)
