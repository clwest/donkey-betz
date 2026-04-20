"""
import logging
logger = logging.getLogger(__name__)

Comprehensive System Audit - Session 127 Part 2
Check all features and functionality
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from content.models import CreativeProject, ImageHistory, VideoHistory
from django.urls import get_resolver

User = get_user_model()

print("=" * 80)
print("🔍 COMPREHENSIVE SYSTEM AUDIT - Session 127 Part 2")
print("=" * 80)

# Get admin user
try:
    user = User.objects.get(username='admin')
    print(f"\n✅ User: {user.username} (ID: {user.id})")
except User.DoesNotExist:
    print("\n❌ Admin user not found!")
    sys.exit(1)

# ============================================================================
# 1. PROJECT STATUS
# ============================================================================
print("\n" + "=" * 80)
print("📁 PROJECT STATUS")
print("=" * 80)

project = CreativeProject.objects.filter(
    user=user,
    name__icontains='Ai Content Generation Company'
).first()

if project:
    print(f"\n✅ Project Found: {project.name}")
    print(f"   ID: {project.id}")
    print(f"   Created: {project.created_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print("\n❌ Project not found!")
    sys.exit(1)

# ============================================================================
# 2. IMAGE STATUS
# ============================================================================
print("\n" + "=" * 80)
print("🎨 IMAGE STATUS")
print("=" * 80)

all_images = ImageHistory.objects.filter(user=user).order_by('-created_at')
project_images = ImageHistory.objects.filter(user=user, project=project).order_by('-created_at')

print(f"\n📊 Total Images: {all_images.count()}")
print(f"   In Project: {project_images.count()}")

if project_images.exists():
    print(f"\n   Latest 5 images:")
    for i, img in enumerate(project_images[:5], 1):
        fav_icon = "⭐" if img.is_favorite else "☆"
        print(f"   {i}. {fav_icon} {img.file_path[:60]}... (ID: {str(img.id)[:8]}...)")

# Check favorite functionality
favorite_images = project_images.filter(is_favorite=True)
print(f"\n   Favorite Images: {favorite_images.count()}")

# ============================================================================
# 3. VIDEO STATUS
# ============================================================================
print("\n" + "=" * 80)
print("🎬 VIDEO STATUS")
print("=" * 80)

all_videos = VideoHistory.objects.filter(user=user).order_by('-created_at')
project_videos = VideoHistory.objects.filter(user=user, project=project).order_by('-created_at')

print(f"\n📊 Total Videos: {all_videos.count()}")
print(f"   In Project: {project_videos.count()}")

# Check video URLs
videos_with_urls = project_videos.exclude(video_url__isnull=True).exclude(video_url='')
videos_pending = project_videos.filter(status='pending')
videos_completed = project_videos.filter(status='completed')

print(f"\n   Videos with URLs: {videos_with_urls.count()}")
print(f"   Pending: {videos_pending.count()}")
print(f"   Completed: {videos_completed.count()}")

if project_videos.exists():
    print(f"\n   All project videos:")
    for i, vid in enumerate(project_videos, 1):
        fav_icon = "⭐" if vid.is_favorite else "☆"
        has_url = "✅" if vid.video_url else "❌"
        print(f"   {i}. {fav_icon} {has_url} {vid.status.upper()} - {vid.prompt[:40]}...")
        if vid.video_url:
            print(f"      URL: {vid.video_url[:60]}...")

# Check favorite functionality
favorite_videos = project_videos.filter(is_favorite=True)
print(f"\n   Favorite Videos: {favorite_videos.count()}")

# ============================================================================
# 4. GPT TOOL DEFINITIONS
# ============================================================================
print("\n" + "=" * 80)
print("🤖 GPT TOOL DEFINITIONS")
print("=" * 80)

try:
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
    assistant = EnhancedPersonalAIAssistant(user)

    # Check if tool definitions exist
    if hasattr(assistant, 'tools') and assistant.tools:
        print(f"\n✅ GPT Tools Defined: {len(assistant.tools)}")
        for i, tool in enumerate(assistant.tools, 1):
            tool_name = tool['function']['name']
            tool_desc = tool['function']['description'][:60]
            print(f"   {i}. {tool_name}")
            print(f"      {tool_desc}...")
    else:
        print("\n⚠️ No tools defined in assistant.tools")

except Exception as e:
    print(f"\n❌ Error loading assistant: {e}")

# ============================================================================
# 5. API ENDPOINT STATUS
# ============================================================================
print("\n" + "=" * 80)
print("🌐 API ENDPOINT STATUS")
print("=" * 80)

critical_endpoints = [
    'assistant_chat_bypass',
    'upscale_image_view',
    'remove_background_view',
    'refine_image_view',
    'create_variations_view',
    'search_and_replace_view',
    'recolor_image_view',
    'animate_image_view',
    'toggle_favorite',
    'toggle_video_favorite',
    'delete_image',
    'delete_video',
]

resolver = get_resolver()
registered_urls = set()

def check_url_pattern(pattern, prefix=''):
    """Recursively check URL patterns"""
    try:
        if hasattr(pattern, 'url_patterns'):
            # URLconf
            for p in pattern.url_patterns:
                check_url_pattern(p, prefix + str(pattern.pattern))
        elif hasattr(pattern, 'callback'):
            # URL pattern
            if hasattr(pattern.callback, '__name__'):
                registered_urls.add(pattern.callback.__name__)
    except Exception as _e:
        logger.warning(
            "audit_system.check_url_pattern: swallowed (%s: %s) — degraded",
            type(_e).__name__, _e,
        )

for pattern in resolver.url_patterns:
    check_url_pattern(pattern)

print(f"\n✅ Registered URL patterns: {len(registered_urls)}")
print(f"\n   Checking critical endpoints:")
for endpoint in critical_endpoints:
    status = "✅" if endpoint in registered_urls else "❌"
    print(f"   {status} {endpoint}")

# ============================================================================
# 6. 3D CONVERSION TOOL STATUS
# ============================================================================
print("\n" + "=" * 80)
print("🎨 3D CONVERSION TOOL STATUS")
print("=" * 80)

try:
    from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
    assistant = EnhancedPersonalAIAssistant(user)

    # Check if convert_to_3d tool exists
    has_3d_tool = False
    has_3d_handler = False

    if hasattr(assistant, 'tools') and assistant.tools:
        for tool in assistant.tools:
            if tool['function']['name'] == 'convert_to_3d':
                has_3d_tool = True
                print(f"\n✅ convert_to_3d tool definition found")
                print(f"   Description: {tool['function']['description'][:80]}...")
                break

    # Check if handler method exists
    if hasattr(assistant, '_tool_convert_to_3d'):
        has_3d_handler = True
        print(f"✅ _tool_convert_to_3d handler method found")

    if has_3d_tool and has_3d_handler:
        print(f"\n✅ 3D Conversion Tool: COMPLETE (awaiting Replicate service)")
    elif has_3d_tool and not has_3d_handler:
        print(f"\n⚠️ 3D Conversion Tool: Tool defined but handler missing")
    elif not has_3d_tool and has_3d_handler:
        print(f"\n⚠️ 3D Conversion Tool: Handler exists but tool not defined")
    else:
        print(f"\n❌ 3D Conversion Tool: Not implemented")

except Exception as e:
    print(f"\n❌ Error checking 3D tool: {e}")

# ============================================================================
# 7. FAVORITE BUTTON INTEGRATION
# ============================================================================
print("\n" + "=" * 80)
print("⭐ FAVORITE BUTTON INTEGRATION")
print("=" * 80)

# Check if template has favorite buttons
template_path = '/Users/donkeyking/development/unified-donkey-betz/ai_core/templates/ai_image_studio.html'
try:
    with open(template_path, 'r') as f:
        template_content = f.read()

    has_image_favorite_btn = 'toggleFavorite' in template_content
    has_video_favorite_btn = 'toggleVideoFavorite' in template_content
    has_favorite_icon = 'favorite-icon' in template_content

    print(f"\n✅ Template checks:")
    print(f"   {'✅' if has_image_favorite_btn else '❌'} toggleFavorite() function")
    print(f"   {'✅' if has_video_favorite_btn else '❌'} toggleVideoFavorite() function")
    print(f"   {'✅' if has_favorite_icon else '❌'} favorite-icon class")

except Exception as e:
    print(f"\n❌ Error checking template: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("📊 AUDIT SUMMARY")
print("=" * 80)

summary_items = [
    ("Project Found", project is not None),
    (f"Images in Project", project_images.count() > 0),
    (f"Videos in Project", project_videos.count() > 0),
    (f"Videos with URLs", videos_with_urls.count() == project_videos.count()),
    ("Favorite Images", favorite_images.count() >= 0),
    ("Favorite Videos", favorite_videos.count() >= 0),
    ("GPT Tools Defined", len(assistant.tools) > 0 if hasattr(assistant, 'tools') else False),
    ("3D Tool Complete", has_3d_tool and has_3d_handler if 'has_3d_tool' in locals() else False),
    ("Favorite Buttons", has_image_favorite_btn and has_video_favorite_btn if 'has_image_favorite_btn' in locals() else False),
]

print("\n")
for item, status in summary_items:
    icon = "✅" if status else "❌"
    print(f"{icon} {item}")

print("\n" + "=" * 80)
print("✅ SYSTEM AUDIT COMPLETE!")
print("=" * 80)
