"""
Image Generation Views
Phase 2: Frontend Reality Fix - Image Generation

Handles image generation requests using:
- Stability AI (Stable Diffusion) - Primary
- Replicate API - Fallback

Created: September 30, 2025
"""

import os
import logging
import requests
import uuid
import json
import zipfile
import base64
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone  # Session 96 Weekend Project
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from PIL import Image as PILImage

# Phase 2 P1: Rate limiting for image operations
from core.decorators import rate_limit
# Phase 2 P1: Input validation
from core.validators import validate_prompt, sanitize_prompt, validate_uuid, validate_numeric_range
# Phase 2 P1: Safe error handling
# Session 487: Creator watermark integration
from core.services.watermark_integration import save_watermarked_image
# Session 769: Cost tracking for external APIs
from core.services.api_cost_config import calculate_stability_cost

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

def get_system_user():
    """
    Get or create a system user for autonomous/Celery operations.

    Session 794: When agents execute autonomously (via Celery tasks),
    there's no authenticated user. This function provides a system user
    so that generated content (images, videos, etc.) can still be saved
    to history and tracked properly.

    Returns:
        User: The system user for autonomous operations
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    system_user, created = User.objects.get_or_create(
        username='system_autonomous',
        defaults={
            'email': 'system@autonomous.internal',
            'is_active': True,
            'first_name': 'System',
            'last_name': 'Autonomous',
        }
    )

    if created:
        logger.info("🤖 Created system_autonomous user for autonomous operations")

    return system_user


# ========================================
# SESSION MANAGEMENT HELPERS (Session 96: Weekend Project)
# ========================================

def get_or_create_session(user, session_id=None, first_prompt=None, project_id=None):
    """
    Get existing session or create new one for AI Assistant conversations

    Args:
        user: User object
        session_id: UUID of existing session (optional)
        first_prompt: First user message in conversation (for new sessions)
        project_id: UUID of project to associate with (Session 97)

    Returns:
        AISession object
    """
    from content.models import AISession, CreativeProject
    import uuid as uuid_lib

    if session_id:
        # Try to get existing session
        try:
            if isinstance(session_id, str):
                session_id = uuid_lib.UUID(session_id)
            session = AISession.objects.get(session_id=session_id, user=user, is_active=True)
            logger.info(f"📝 Retrieved existing session: {session.session_id}")
            return session
        except AISession.DoesNotExist:
            logger.warning(f"⚠️ Session {session_id} not found, creating new one")

    # Session 97: Get project if provided, or default to Quick Starts
    project = None
    if project_id:
        try:
            if isinstance(project_id, str):
                project_id = uuid_lib.UUID(project_id)
            project = CreativeProject.objects.get(id=project_id, user=user)
            logger.info(f"📁 Linking new session to project: {project.name}")
        except CreativeProject.DoesNotExist:
            logger.warning(f"⚠️ Project {project_id} not found")

    # Fall back to Quick Starts if no project specified
    if not project:
        project = CreativeProject.objects.filter(user=user, is_quick_starts=True).first()
        if project:
            logger.info(f"⚡ Using Quick Starts project for session")

    # Create new session
    # Generate title from first prompt (take first 50 chars or use generic)
    if first_prompt:
        title = first_prompt[:50] + ('...' if len(first_prompt) > 50 else '')
    else:
        title = f"AI Session {timezone.now().strftime('%Y-%m-%d %H:%M')}"

    session = AISession.objects.create(
        user=user,
        title=title,
        first_prompt=first_prompt or '',
        conversation_transcript=[],
        project=project,
        is_active=True
    )

    logger.info(f"✨ Created new session: {session.session_id} - '{title}'")
    return session


def update_session_transcript(session, role, content):
    """
    Add message to session conversation transcript

    Args:
        session: AISession object
        role: 'user' or 'assistant'
        content: Message content
    """
    if not session:
        return

    session.conversation_transcript.append({
        'role': role,
        'content': content,
        'timestamp': timezone.now().isoformat()
    })
    session.save(update_fields=['conversation_transcript'])


def get_image_by_number(user, image_number):
    """
    Get image UUID from sequential number

    Session 96 Weekend Project: Hybrid Image ID system
    Allows AI Assistant to understand "Use image 12" commands

    Args:
        user: User object
        image_number: Sequential number (1-based)

    Returns:
        ImageHistory object or None
    """
    from content.models import ImageHistory

    try:
        # Get all user's images ordered by creation date
        images = ImageHistory.objects.filter(user=user).order_by('created_at')

        # Sequential numbers are 1-based, list indices are 0-based
        if image_number < 1:
            return None

        # Get the image at position (image_number - 1)
        if image_number <= images.count():
            return images[image_number - 1]

        return None

    except Exception as e:
        logger.error(f"❌ Error getting image by number: {e}")
        return None


def increment_session_counter(session, content_type):
    """
    Increment session content counter and trigger auto-project creation if needed

    Args:
        session: AISession object
        content_type: 'image', 'video', or 'audio'

    Returns:
        dict: Project creation info if project was auto-created, None otherwise
    """
    if not session:
        return None

    if content_type == 'image':
        session.total_images += 1
        session.save(update_fields=['total_images'])
    elif content_type == 'video':
        session.total_videos += 1
        session.save(update_fields=['total_videos'])
    elif content_type == 'audio':
        session.total_audio += 1
        session.save(update_fields=['total_audio'])

    logger.info(f"📊 Session {session.session_id}: Updated {content_type} counter")

    # Session 96 Weekend Project: Auto-create project if meaningful content created
    # Trigger when: 3+ images OR 1+ video OR 2+ audio files
    should_create_project = (
        session.total_images >= 3 or
        session.total_videos >= 1 or
        session.total_audio >= 2
    )

    # Session 117: FIXED - Also auto-create if session is using Quick Starts placeholder
    # Quick Starts is just a fallback, not a real user project
    has_real_project = session.project and not session.project.is_quick_starts

    if should_create_project and not has_real_project and not session.auto_created_project:
        logger.info(f"🎯 Auto-creating project for session {session.session_id}")
        project = auto_create_project_from_session(session)
        if project:
            # Session 96: Return project info for frontend notification
            return {
                'project_created': True,
                'project_id': project.id,
                'project_name': project.name
            }

    return None


def _generate_smart_project_name(title):
    """
    Generate a clean, professional project name from a verbose AI prompt.

    Transforms:
    - "Create three cartoon style logos for a mechanic shop" → "Mechanic Shop Logos"
    - "Generate social media posts for coffee brand" → "Coffee Brand Social Media"
    - "Make a modern website design" → "Modern Website Design"

    Algorithm:
    1. Remove common AI prompt prefixes
    2. Extract key subject nouns (last 3-5 important words)
    3. Remove filler words
    4. Title-case result
    5. Limit to 50 characters max
    """
    if not title:
        return "Untitled Project"

    # Step 1: Remove common AI prompt prefixes
    prefixes_to_remove = [
        'create a ', 'create three ', 'create ',
        'make a ', 'make three ', 'make ',
        'generate a ', 'generate three ', 'generate ',
        'design a ', 'design three ', 'design ',
        'build a ', 'build three ', 'build ',
        'draw a ', 'draw ', 'write a ', 'write '
    ]

    title_lower = title.lower()
    for prefix in prefixes_to_remove:
        if title_lower.startswith(prefix):
            title = title[len(prefix):]
            title_lower = title.lower()
            break

    # Step 2: Remove filler words and focus on meaningful content
    filler_words = {
        'a', 'an', 'the', 'some', 'for', 'with', 'about', 'using',
        'in', 'on', 'at', 'by', 'from', 'of', 'to', 'and', 'or', 'but',
        'style', 'styled', 'themed',  # Often redundant in project names
        'called', 'named'  # Session 122: Remove "called/named" from project names (e.g., "tech startup called Cloud" → "Tech Startup Cloud")
    }

    words = title.split()
    meaningful_words = []
    for word in words:
        # Keep words that are:
        # - Not filler words
        # - OR are important content words (capitalized, numbers, etc.)
        clean_word = word.strip('.,!?;:').lower()
        if clean_word not in filler_words or word[0].isupper() or clean_word.isdigit():
            meaningful_words.append(word.strip('.,!?;:'))

    # Step 3: Smart truncation - keep last 3-5 meaningful words (usually the core subject)
    # Example: "cartoon style logos for a mechanic shop" → "logos mechanic shop"
    if len(meaningful_words) > 5:
        # For longer prompts, take last 4-5 words (usually contains the subject)
        meaningful_words = meaningful_words[-5:]
    elif len(meaningful_words) > 3:
        # For medium prompts, keep last 3-4 words
        meaningful_words = meaningful_words[-4:]

    # Step 4: Join and title-case
    project_name = ' '.join(meaningful_words)
    project_name = project_name.title()

    # Step 5: Limit length
    if len(project_name) > 50:
        project_name = project_name[:47] + '...'

    return project_name if project_name else "Untitled Project"


def auto_create_project_from_session(session):
    """
    Automatically create a CreativeProject from an AI session

    Session 96 Weekend Project: Auto-organize content into projects

    Args:
        session: AISession object with meaningful content
    """
    from content.models import CreativeProject

    if not session:
        return None

    # Session 117: FIXED - Skip only if has a REAL project (not Quick Starts placeholder)
    # Quick Starts is okay to replace with auto-created project
    has_real_project = session.project and not session.project.is_quick_starts
    if has_real_project or session.auto_created_project:
        return None

    # Determine project name from session title with smart extraction
    project_name = _generate_smart_project_name(session.title)

    # Determine project category based on session type and content
    category = 'branding'  # Default
    if session.session_type:
        category_map = {
            'logo_design': 'branding',
            'video_creation': 'marketing',
            'content_package': 'marketing',
            'branding': 'branding',
        }
        category = category_map.get(session.session_type, 'branding')
    elif session.total_videos > 0:
        category = 'marketing'

    # Generate project goal from first prompt
    goal = session.first_prompt if session.first_prompt else f"Auto-created from AI session: {session.title}"
    if len(goal) > 200:
        goal = goal[:197] + '...'

    # Create project
    project = CreativeProject.objects.create(
        user=session.user,
        name=project_name,
        category=category,
        goal=goal,
        status='active',
        metadata={'auto_generated': True, 'source': 'ai_session'}  # Mark as auto-created
    )

    # Link session to project
    session.project = project
    session.auto_created_project = True
    session.save(update_fields=['project', 'auto_created_project'])

    # Session 97: Link all session content to the newly created project
    from content.models import ImageHistory, VideoHistory

    # Update all images from this session to belong to the project
    images_updated = ImageHistory.objects.filter(session=session).update(project=project)
    logger.info(f"📸 Linked {images_updated} images to project '{project.name}'")

    # Update all videos from this session to belong to the project
    videos_updated = VideoHistory.objects.filter(session=session).update(project=project)
    logger.info(f"🎬 Linked {videos_updated} videos to project '{project.name}'")

    # Note: Audio doesn't have project field yet, skip for now

    logger.info(f"✨ Auto-created project '{project.name}' (ID: {project.id}) for session {session.session_id}")
    return project


# ========================================
# IMAGE HISTORY HELPER (Session 36: Feature 9)
# ========================================

def save_to_history(user, file_path, image_type, prompt='', parameters=None,
                    model_used='', style='', parent_image=None, seed=None, session=None, project=None):
    """
    Helper function to save image to ImageHistory database.

    Args:
        user: User object
        file_path: Path to saved image file
        image_type: Type of image (generated, erased, inpainted, etc.)
        prompt: Prompt used for generation/editing
        parameters: Dict of parameters used
        model_used: Model name (core, sdxl, sd3, ultra)
        style: Style preset name
        parent_image: Parent ImageHistory object if this is an edit
        seed: Random seed used for generation (for reproducibility) - Session 95
        session: AISession object linking to conversation (Session 96 Weekend Project)
        project: CreativeProject object to associate with (Session 124)
    """
    try:
        from content.models import ImageHistory

        # Get image dimensions and file size
        width, height, file_size = None, None, None
        if file_path.startswith('http'):
            # Cloud-stored image (Cloudinary URL) — download to read metadata
            try:
                import requests as _req
                resp = _req.get(file_path, timeout=10)
                if resp.status_code == 200:
                    from io import BytesIO
                    with PILImage.open(BytesIO(resp.content)) as img:
                        width, height = img.size
                    file_size = len(resp.content)
            except Exception as e:
                logger.warning(f"Could not read cloud image metadata: {e}")
        else:
            try:
                full_path = default_storage.path(file_path)
                with PILImage.open(full_path) as img:
                    width, height = img.size
                file_size = os.path.getsize(full_path)
            except Exception as e:
                logger.warning(f"Could not read image metadata: {e}")

        # Session 119: BUGFIX - Assign project if session already has one
        # When resuming a session with existing project, images need to be linked immediately
        # Session 124: Also support direct project parameter
        image_project = None
        if project:
            # Direct project parameter takes precedence (Session 124)
            image_project = project
            logger.info(f"📁 Assigning image to project (direct): {project.name}")
        elif session and session.project:
            # Fall back to session's project (Session 119)
            image_project = session.project
            logger.info(f"📁 Assigning image to project (from session): {session.project.name}")

        # Session 752: Get the image generation agent for tracking
        image_agent = None
        try:
            from core.models.agents_registry import UnifiedAgentTemplate
            image_agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
        except Exception as e:
            logger.warning(f"Could not find image-generation-agent: {e}")

        # Create history record
        # Session 752: Now includes agent field for proper contribution tracking
        history = ImageHistory.objects.create(
            user=user,
            filename=os.path.basename(file_path),
            file_path=file_path,
            image_type=image_type,
            prompt=prompt,
            parameters=parameters or {},
            model_used=model_used,
            style=style,
            image_width=width,
            image_height=height,
            file_size_bytes=file_size,
            parent_image=parent_image,
            seed=seed,  # Session 95: Save seed for reproducibility
            session=session,  # Session 96 Weekend Project: Link to AI conversation
            project=image_project,  # Session 119: BUGFIX - Assign project if session has one
            agent=image_agent  # Session 752: Set agent for contribution tracking
        )

        # Session 142/752: Track agent contribution
        # Session 752: Project is now optional - track contributions even without project
        if image_agent:
            try:
                from core.models.agents_registry import AgentContribution
                AgentContribution.objects.create(
                    agent=image_agent,
                    image=history,
                    project=image_project,  # Can be None now (Session 752)
                    contribution_type='generation',
                    task_description=f"Generated {image_type} image using {model_used}",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for image {history.id}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
        else:
            logger.debug("Skipping contribution tracking: no agent found")

        logger.info(f"✅ Saved to history: {image_type} - {history.filename} (ID: {history.id})")

        # Session 430: Auto-deliver to Discord if user has linked account
        try:
            from core.services.discord_notifications import discord_notify
            # Build the full image URL
            if history.image_url:
                image_url = history.image_url
                if image_url.startswith('/media/'):
                    image_url = f"http://localhost:8000{image_url}"
                elif not image_url.startswith('http'):
                    image_url = f"http://localhost:8000/media/{image_url}"

                # Deliver to Discord (gallery channel + DM if linked)
                discord_notify.deliver_image_to_user(
                    user=user,
                    image_url=image_url,
                    prompt=prompt or 'No prompt',
                    image_id=history.id,
                    model=model_used or 'Unknown'
                )
        except Exception as discord_error:
            logger.warning(f"Discord delivery failed (non-fatal): {discord_error}")
            # Don't fail image creation if Discord delivery fails

        return history

    except Exception as e:
        logger.error(f"❌ Failed to save image history: {e}")
        # Don't fail the request if history save fails
        return None


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@rate_limit('ai_generation')  # Phase 2 P1: Rate limit AI generation (10 requests/min)
def gallery_generate(request):
    """
    Generate images using Stable Diffusion or Replicate

    Expected request body:
    {
        "prompt": "A beautiful sunset over mountains",
        "negative_prompt": "blurry, low quality",
        "width": 1024,
        "height": 1024,
        "num_images": 1,
        "style": "photorealistic"
    }

    Returns:
    {
        "success": true,
        "images": [
            {
                "id": "uuid",
                "url": "/media/generated_images/...",
                "prompt": "...",
                "created_at": "2025-09-30T..."
            }
        ],
        "provider": "stability|replicate",
        "cost": 0.04
    }
    """
    try:
        user = request.user
        data = request.data

        # Extract parameters
        prompt = data.get('prompt', '')

        # Phase 2 P1: Validate prompt
        is_valid, validation_error = validate_prompt(prompt, min_length=1, max_length=2000)
        if not is_valid:
            return Response({
                'success': False,
                'error': validation_error,
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # Sanitize prompt to prevent injection
        prompt = sanitize_prompt(prompt)

        negative_prompt = data.get('negative_prompt', 'blurry, low quality, distorted')
        if negative_prompt:
            negative_prompt = sanitize_prompt(negative_prompt)

        # Phase 2 P1: Validate dimensions
        width = int(data.get('width', 1024))
        height = int(data.get('height', 1024))
        width_valid, width_error = validate_numeric_range(width, 256, 2048, 'width')
        if not width_valid:
            return Response({'success': False, 'error': width_error, 'error_code': 'VALIDATION_ERROR'}, status=400)
        height_valid, height_error = validate_numeric_range(height, 256, 2048, 'height')
        if not height_valid:
            return Response({'success': False, 'error': height_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        # Phase 2 P1: Validate num_images
        num_images = int(data.get('num_images', 1))
        num_valid, num_error = validate_numeric_range(num_images, 1, 10, 'num_images')
        if not num_valid:
            return Response({'success': False, 'error': num_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        style = data.get('style', 'photorealistic')
        quality = data.get('quality', 'balanced')  # NEW: Support for quality selector

        # Session 124: Extract project_id for project-scoped generation
        project_id = data.get('project_id')

        # Phase 2 P1: Validate project_id if provided
        if project_id:
            is_valid, uuid_error = validate_uuid(project_id)
            if not is_valid:
                return Response({'success': False, 'error': uuid_error, 'error_code': 'VALIDATION_ERROR'}, status=400)
        project = None

        # Check direct parameter first
        if project_id:
            try:
                from content.models import CreativeProject
                project = CreativeProject.objects.get(id=project_id, user=user)
                logger.info(f"🎨 Image generation for project (direct): {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found, generating without project")

        # Session 124: Check Redis for project context set by Assistant
        if not project:
            try:
                import redis
                r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
                stored_project_id = r.get(f"user:{user.id}:current_project")
                if stored_project_id:
                    from content.models import CreativeProject
                    project = CreativeProject.objects.get(id=stored_project_id, user=user)
                    logger.info(f"🎨 Image generation for project (from Redis): {project.name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not retrieve project from Redis: {e}")

        logger.info(f"🎨 Image generation request from {user.username}: {prompt[:50]}... (quality: {quality}, style: {style})")

        # Try Stability AI first (if API key available)
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

        generated_images = []
        provider = None
        cost = 0.0

        # Use the new ImageGenerationService with quality support
        if stability_key:
            logger.info(f"🎨 Attempting generation with Stability AI ({quality} quality)...")
            try:
                from content.image_generation import ImageGenerationService

                service = ImageGenerationService()
                result = service.generate_image(
                    prompt=prompt,
                    size=f"{width}x{height}",
                    style=style,
                    quality=quality,
                    provider='stability',
                    negative_prompt=negative_prompt,
                    num_images=num_images
                )

                if result.success:
                    generated_images = result.images  # Fixed: attribute is 'images' not 'image_urls'
                    provider = 'stability'
                    cost = result.cost if hasattr(result, 'cost') else 0.0
                    logger.info(f"✅ Stability AI generated {len(generated_images)} images (cost: ${cost:.4f})")
            except Exception as e:
                logger.warning(f"⚠️ Stability AI failed: {e}, trying Replicate...")

        # Fallback to Replicate if Stability failed or not available
        if not generated_images and replicate_key:
            logger.info("🎨 Attempting generation with Replicate...")
            try:
                result = generate_with_replicate(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_images=num_images,
                    api_key=replicate_key
                )
                if result['success']:
                    generated_images = result['images']
                    provider = 'replicate'
                    cost = result.get('cost', 0.02)
                    logger.info(f"✅ Replicate generated {len(generated_images)} images")
            except Exception as e:
                logger.error(f"❌ Replicate also failed: {e}")

        # If both failed or no API keys
        if not generated_images:
            return Response({
                'success': False,
                'error': 'Image generation failed. Please check API keys.',
                'details': {
                    'stability_configured': bool(stability_key),
                    'replicate_configured': bool(replicate_key)
                }
            }, status=500)

        # Save images and create records
        saved_images = []
        # Session 95: Extract seeds from result metadata if available
        seeds = []
        if hasattr(result, 'metadata') and result.metadata and 'seeds' in result.metadata:
            seeds = result.metadata['seeds']

        for img_index, img_data in enumerate(generated_images):
            try:
                # Save to media storage
                image_id = str(uuid.uuid4())
                filename = f"generated_images/{user.id}/{image_id}.png"

                # img_data can be either a string (URL/data URI) or dict with 'url' key
                image_url = img_data if isinstance(img_data, str) else img_data.get('url')

                # Handle base64 data URIs vs regular URLs
                if image_url:
                    if image_url.startswith('data:image'):
                        # Extract base64 data from data URI
                        import base64
                        import re
                        base64_match = re.search(r'base64,(.+)', image_url)
                        if base64_match:
                            image_data = base64.b64decode(base64_match.group(1))
                            # Session 487: Apply creator watermark before saving
                            # Session 800: Now returns Cloudinary URL in production
                            file_path = save_watermarked_image(
                                image_bytes=image_data,
                                filename=filename,
                                user=user,
                                generation_params={'prompt': prompt, 'model': quality, 'style': style}
                            )
                            # Session 800: file_path may be Cloudinary URL or local path
                            url = file_path if file_path.startswith('http') else default_storage.url(file_path)
                        else:
                            continue
                    else:
                        # Regular HTTP/HTTPS URL - download it
                        response = requests.get(image_url, timeout=30)
                        if response.status_code == 200:
                            # Session 487: Apply creator watermark before saving
                            # Session 800: Now returns Cloudinary URL in production
                            file_path = save_watermarked_image(
                                image_bytes=response.content,
                                filename=filename,
                                user=user,
                                generation_params={'prompt': prompt, 'model': quality, 'style': style}
                            )
                            # Session 800: file_path may be Cloudinary URL or local path
                            url = file_path if file_path.startswith('http') else default_storage.url(file_path)
                        else:
                            continue

                    # Map quality to model_used for history
                    quality_to_model = {
                        'fast': 'core',
                        'balanced': 'sdxl',
                        'high': 'sd3',
                        'premium': 'ultra'
                    }
                    model_used = quality_to_model.get(quality, 'sdxl')

                    # Session 95: Get seed for this image if available
                    image_seed = seeds[img_index] if img_index < len(seeds) else None

                    # Save to history (Session 36: Feature 9)
                    history = save_to_history(
                        user=user,
                        file_path=file_path,
                        image_type='generated',
                        prompt=prompt,
                        parameters={
                            'provider': provider,
                            'width': width,
                            'height': height,
                            'quality': quality,
                            'negative_prompt': negative_prompt,
                            'num_images': num_images
                        },
                        model_used=model_used,
                        style=style,
                        seed=image_seed,  # Session 95: Add seed for reproducibility
                        project=project  # Session 124: Associate with project
                    )

                    # Session 143: Track agent contribution for gallery generation
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=history,
                            project=project,
                            contribution_type='generation',
                            task_description=f"Generated image via gallery_generate (provider={provider}, quality={quality}, style={style}, resolution={width}x{height})",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {history.id}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        # Don't fail image creation if contribution tracking fails

                    # Session 122: Track generated image in AI Assistant for intelligent chaining
                    try:
                        from django.core.cache import cache
                        cache_key = f'assistant_{user.id}'
                        assistant = cache.get(cache_key)
                        if assistant and history:
                            # Determine asset type based on context
                            asset_type = 'image'
                            if 'logo' in prompt.lower():
                                asset_type = 'logo'
                            elif any(word in prompt.lower() for word in ['character', 'mascot', 'avatar']):
                                asset_type = 'character'
                            elif any(word in prompt.lower() for word in ['product', 'merchandise']):
                                asset_type = 'product'

                            assistant.track_generated_image(
                                image_id=str(history.id),
                                image_url=url,
                                prompt=prompt,
                                asset_type=asset_type
                            )
                            logger.info(f"📸 Tracked image {history.id} as {asset_type} in AI Assistant")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to track image in AI Assistant: {e}")

                    # Save image record (works for both base64 and HTTP URLs)
                    saved_images.append({
                        'id': image_id,
                        'url': url,
                        'prompt': prompt,
                        'width': width,
                        'height': height,
                        'provider': provider,
                        'created_at': datetime.now().isoformat()
                    })
                    logger.info(f"✅ Saved image {image_id}")
            except Exception as e:
                logger.error(f"❌ Failed to save image: {e}")

        if not saved_images:
            return Response({
                'success': False,
                'error': 'Generated images but failed to save'
            }, status=500)

        return Response({
            'success': True,
            'images': saved_images,
            'provider': provider,
            'cost': cost,
            'prompt': prompt,
            'total_images': len(saved_images)
        })

    except Exception as e:
        logger.error(f"❌ Image generation error: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def generate_with_stability(prompt, negative_prompt, width, height, num_images, api_key):
    """
    Generate images using Stability AI API
    Documentation: https://platform.stability.ai/docs/api-reference

    Session 769: Added cost tracking using api_cost_config
    """
    model_id = "stable-diffusion-xl-1024-v1-0"
    url = f"https://api.stability.ai/v1/generation/{model_id}/text-to-image"

    # Session 769: Calculate cost before making the API call
    resolution = f"{width}x{height}"
    cost_info = calculate_stability_cost(
        model=model_id,
        resolution=resolution,
        image_count=num_images
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "text_prompts": [
            {
                "text": prompt,
                "weight": 1
            },
            {
                "text": negative_prompt,
                "weight": -1
            }
        ],
        "cfg_scale": 7,
        "height": height,
        "width": width,
        "samples": num_images,
        "steps": 30
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)

    if response.status_code == 200:
        result = response.json()
        images = []

        # Stability returns base64 encoded images
        for i, artifact in enumerate(result.get('artifacts', [])):
            if artifact.get('base64'):
                import base64
                image_data = base64.b64decode(artifact['base64'])

                # Create temporary URL (we'll save this properly in the main function)
                images.append({
                    'data': image_data,
                    'format': 'png'
                })

        logger.info(f"💰 Stability AI cost: ${cost_info['cost']:.4f} ({num_images} images @ {resolution})")

        return {
            'success': True,
            'images': images,
            'cost': float(cost_info['cost']),  # Session 769: Use calculated cost
            'cost_info': cost_info,  # Session 769: Full cost breakdown
        }
    else:
        error_msg = response.json().get('message', response.text)
        logger.error(f"Stability AI error: {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'cost_info': None,
        }


def generate_with_replicate(prompt, negative_prompt, width, height, num_images, api_key):
    """
    Generate images using Replicate API
    Model: stability-ai/sdxl
    Documentation: https://replicate.com/docs/reference/http
    """
    url = "https://api.replicate.com/v1/predictions"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL
        "input": {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_outputs": num_images,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    }

    # Start prediction
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code == 201:
        prediction = response.json()
        prediction_id = prediction['id']

        # Poll for completion (max 60 seconds)
        import time
        for _ in range(30):  # 30 attempts, 2 seconds each = 60s max
            time.sleep(2)

            status_response = requests.get(
                f"{url}/{prediction_id}",
                headers=headers,
                timeout=10
            )

            if status_response.status_code == 200:
                status_data = status_response.json()

                if status_data['status'] == 'succeeded':
                    output_urls = status_data.get('output', [])
                    images = [{'url': url} for url in output_urls]

                    return {
                        'success': True,
                        'images': images,
                        'cost': 0.02 * num_images  # Approximate cost
                    }
                elif status_data['status'] == 'failed':
                    return {
                        'success': False,
                        'error': status_data.get('error', 'Generation failed')
                    }

        # Timeout
        return {
            'success': False,
            'error': 'Generation timeout after 60 seconds'
        }
    else:
        error_msg = response.json().get('detail', response.text)
        logger.error(f"Replicate error: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_image_generation(request):
    """
    Test endpoint to verify image generation is configured
    """
    stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
    replicate_key = os.getenv('REPLICATE_API_KEY') or settings.AI_PROVIDERS.get('REPLICATE_API_KEY')

    return Response({
        'success': True,
        'image_generation_configured': bool(stability_key or replicate_key),
        'providers': {
            'stability': {
                'configured': bool(stability_key),
                'status': 'ready' if stability_key else 'missing_api_key'
            },
            'replicate': {
                'configured': bool(replicate_key),
                'status': 'ready' if replicate_key else 'missing_api_key'
            }
        },
        'message': 'Image generation is ready' if (stability_key or replicate_key) else 'Configure API keys to enable image generation'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_image_prompt(request):
    """
    Optimize an image generation prompt using the Intelligent Prompting System
    
    Takes a simple prompt like "donkey walking a dog" and a style like "pixar"
    and returns an enhanced, detailed prompt for better image generation.
    
    Expected request body:
    {
        "prompt": "donkey walking a dog",
        "style": "pixar",
        "quality": "balanced"
    }
    
    Returns:
    {
        "success": true,
        "original_prompt": "donkey walking a dog",
        "enhanced_prompt": "A professional animated donkey character walking a friendly dog...",
        "negative_prompt": "...",
        "optimization_notes": "Added lighting details, anatomical specifications..."
    }
    """
    try:
        user = request.user
        data = request.data
        
        original_prompt = data.get('prompt', '').strip()
        style = data.get('style', '')
        quality = data.get('quality', 'balanced')
        
        if not original_prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)
        
        logger.info(f"🎨 Optimizing prompt for {user.username}: '{original_prompt}' (style: {style})")
        
        # Build style-specific guidance
        style_guidance_map = {
            'pixar': 'Pixar-style 3D animation with expressive characters, smooth rendering, professional lighting',
            'disney': 'Disney animated style with vibrant colors, magical atmosphere, professional quality',
            'studio-ghibli': 'Studio Ghibli hand-drawn animation style, detailed backgrounds, atmospheric lighting',
            'dreamworks': 'DreamWorks animation style with dynamic poses, cinematic composition',
            'cinematic': 'Cinematic photography with dramatic lighting, professional composition, 8K quality',
            'photographic': 'Professional photography, crystal clear focus, proper exposure, realistic details',
            'anime': 'Anime art style with clean lines, vibrant colors, dynamic composition',
            'digital-art': 'Digital art style, highly detailed, professional quality, trending on ArtStation',
        }

        style_guidance = style_guidance_map.get(style.lower()) if style else None

        # Use the Intelligent Prompting System
        from content.ai_providers import AIProviderManager

        # Create a specialized optimization request for image generation
        # Build style instruction conditionally
        style_instruction = ""
        if style and style_guidance:
            style_instruction = f"3. Apply style-specific enhancements: {style_guidance}\n"

        optimization_request = f"""Enhance this image generation prompt for Stability AI:

Original Prompt: "{original_prompt}"
Style: {style or 'natural (no specific style)'}
Quality Level: {quality}

ENHANCEMENT REQUIREMENTS:
1. Keep the core concept from the original prompt
2. Add specific details about:
   - Character/subject anatomy (specify "two legs", "two arms", "perfect anatomy" for characters)
   - Lighting (golden hour, cinematic lighting, volumetric lighting, etc.)
   - Composition (hero shot, wide angle, close-up, etc.)
   - Quality markers (8K, professional, crystal clear, highly detailed)
   - Environment/background details
{style_instruction}{"3" if not style_instruction else "4"}. Avoid vague terms - be specific and descriptive
{"4" if not style_instruction else "5"}. Keep the enhanced prompt under 200 words

Return ONLY the enhanced prompt text, no explanations or formatting."""
        
        # Use AI to enhance the prompt
        ai_manager = AIProviderManager()
        try:
            response = ai_manager.generate_completion(
                prompt=optimization_request,
                provider='anthropic',  # Use Claude for prompt optimization
                model='claude-3-5-sonnet-20241022',
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_prompt = response.get('content', '').strip()
            
            # If AI fails, use rule-based enhancement as fallback
            if not enhanced_prompt or len(enhanced_prompt) < 20:
                enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
            
        except Exception as e:
            logger.warning(f"AI optimization failed, using rule-based fallback: {e}")
            enhanced_prompt = _enhance_prompt_rule_based(original_prompt, style, style_guidance)
        
        # Generate style-specific negative prompt
        negative_prompt = "blurry, low quality, distorted, deformed, extra limbs, extra fingers, extra legs, bad anatomy, disfigured, mutated, ugly, poorly drawn, bad proportions, gross proportions"
        
        if style in ['pixar', 'disney', 'studio-ghibli', 'dreamworks', 'anime']:
            negative_prompt += ", realistic, photograph, 3D render"
        elif style in ['photographic', 'cinematic']:
            negative_prompt += ", cartoon, anime, illustrated, painting, drawing"
        
        logger.info(f"✅ Prompt optimized: {len(original_prompt)} → {len(enhanced_prompt)} chars")
        
        return Response({
            'success': True,
            'original_prompt': original_prompt,
            'enhanced_prompt': enhanced_prompt,
            'negative_prompt': negative_prompt,
            'style': style,
            'quality': quality,
            'optimization_method': 'ai_enhanced'
        })
        
    except Exception as e:
        logger.error(f"❌ Prompt optimization error: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'fallback_prompt': data.get('prompt', '')
        }, status=500)


def _enhance_prompt_rule_based(original_prompt: str, style: str, style_guidance: str = None) -> str:
    """
    Rule-based fallback for prompt enhancement when AI fails

    Args:
        original_prompt: The original user prompt
        style: The selected style (can be empty string)
        style_guidance: Style-specific guidance text (can be None if no style)
    """
    # Add anatomical specifications for character prompts
    character_keywords = ['person', 'man', 'woman', 'character', 'donkey', 'dog', 'cat', 'animal', 'creature']
    has_character = any(keyword in original_prompt.lower() for keyword in character_keywords)

    enhanced = original_prompt

    if has_character:
        enhanced += ", with perfect anatomy, correct proportions, two arms, two legs"

    # Add style guidance only if style is specified
    if style and style_guidance:
        enhanced += f", {style_guidance}"

    # Add quality markers
    enhanced += ", professional quality, highly detailed, 8K resolution, sharp focus"

    # Add lighting
    enhanced += ", cinematic lighting, dramatic shadows, golden hour"

    return enhanced


# ========================================
# IMAGE EDITING FUNCTIONS (Session 35)
# ========================================

@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def remove_background(request):
    """
    Remove background from an uploaded image using Stability AI.

    Expected request: Form data with 'image' file
    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎭 Remove background request for {image_file.name}")

        # Call Stability AI remove-background API
        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            # Save the image to media directory for reliable downloads
            filename = f'background_removed_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            # Session 487: Apply creator watermark before saving
            # Session 800: Now returns Cloudinary URL in production
            saved_path = save_watermarked_image(
                image_bytes=response.content,
                filename=filepath,
                user=request.user,
                generation_params={'operation': 'remove_background'}
            )
            # Session 800: saved_path may be Cloudinary URL or local path
            image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

            logger.info(f"✅ Background removed successfully - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='background_removed',
                prompt='',
                parameters={'operation': 'remove_background'}
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Remove background error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def recolor_image(request):
    """
    Recolor a specific object in an image using Stability AI.

    Expected request: Form data with:
    - 'image': image file
    - 'prompt': object to recolor (e.g., 'shirt')
    - 'select_prompt': object to recolor (same as prompt)
    - 'color': new color name (e.g., 'red', 'blue')

    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get parameters
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        select_prompt = request.POST.get('select_prompt', prompt).strip()
        color = request.POST.get('color', '').strip()

        if not prompt or not color:
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt or color'
            }, status=400)

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Recolor request: {prompt} → {color}")

        # Call Stability AI search-and-recolor API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type)
        }

        data = {
            'prompt': f'{select_prompt}, {color}',
            'select_prompt': select_prompt,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the image to media directory for reliable downloads
            filename = f'recolored_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            # Session 487: Apply creator watermark before saving
            # Session 800: Now returns Cloudinary URL in production
            saved_path = save_watermarked_image(
                image_bytes=response.content,
                filename=filepath,
                user=request.user,
                generation_params={'operation': 'recolor', 'object': prompt, 'color': color}
            )
            # Session 800: saved_path may be Cloudinary URL or local path
            image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

            logger.info(f"✅ Recolor complete: {prompt} → {color} - saved to {saved_path}")

            # Save to history (Session 36: Feature 9)
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='recolored',
                prompt=f'Recolor {prompt} to {color}',
                parameters={
                    'operation': 'recolor',
                    'object': prompt,
                    'color': color
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Recolor error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def upscale_image(request):
    """
    Upscale an image using Stability AI.

    Expected request: Form data with:
    - 'image': image file
    - 'method': 'fast' (4x), 'conservative' (4K), or 'creative' (AI enhancement)

    Returns: {success: true, image_url: 'data:image/png;base64,...'}
    """
    try:
        # Get parameters
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)

        image_file = request.FILES['image']
        method = request.POST.get('method', 'fast').strip().lower()

        # Validate method
        valid_methods = ['fast', 'conservative', 'creative']
        if method not in valid_methods:
            return JsonResponse({
                'success': False,
                'error': f'Invalid method. Must be one of: {", ".join(valid_methods)}'
            }, status=400)

        # Get Stability AI API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📈 Upscale request: {method} method")

        # Resize image if needed (max 1,048,576 pixels = 1024x1024)
        from PIL import Image
        import io

        # Read image
        img = Image.open(image_file)
        width, height = img.size
        total_pixels = width * height

        logger.info(f"📏 Image dimensions: {width}x{height} = {total_pixels:,} pixels")

        # Resize if too large
        max_pixels = 1_048_576  # 1024x1024
        if total_pixels > max_pixels:
            # Calculate scaling factor
            scale = (max_pixels / total_pixels) ** 0.5
            new_width = int(width * scale)
            new_height = int(height * scale)

            logger.info(f"🔄 Resizing from {width}x{height} to {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save resized image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            image_data = img_bytes.read()
        else:
            # Use original image
            image_file.seek(0)
            image_data = image_file.read()

        # Map method to Stability AI endpoint
        endpoint_map = {
            'fast': 'https://api.stability.ai/v2beta/stable-image/upscale/fast',
            'conservative': 'https://api.stability.ai/v2beta/stable-image/upscale/conservative',
            'creative': 'https://api.stability.ai/v2beta/stable-image/upscale/creative'
        }

        url = endpoint_map[method]

        files = {
            'image': (image_file.name, image_data, 'image/png')
        }

        data = {
            'output_format': 'png'
        }

        # Creative upscale requires a prompt
        if method == 'creative':
            data['prompt'] = 'enhance quality, add details, improve clarity'

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Check if we got an image or a job ID (creative upscale is async)
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                # Creative upscale returns a job ID - need to poll for result
                import json
                import time

                result_data = json.loads(response.text)
                generation_id = result_data.get('id')

                if not generation_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'No generation ID received from Stability AI'
                    }, status=500)

                logger.info(f"🔄 Creative upscale job started: {generation_id}, polling for result...")

                # Poll for the result (max 60 seconds)
                result_url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}"

                for attempt in range(30):  # 30 attempts * 2 seconds = 60 seconds max
                    time.sleep(2)

                    result_response = requests.get(
                        result_url,
                        headers={
                            'Authorization': f'Bearer {stability_key}',
                            'Accept': 'image/*'
                        }
                    )

                    if result_response.status_code == 200:
                        # Got the image!
                        filename = f'upscaled_{method}_{uuid.uuid4().hex[:8]}.png'
                        filepath = os.path.join('generated_images', filename)
                        # Session 487: Apply creator watermark before saving
                        # Session 800: Now returns Cloudinary URL in production
                        saved_path = save_watermarked_image(
                            image_bytes=result_response.content,
                            filename=filepath,
                            user=request.user,
                            generation_params={'operation': 'upscale', 'method': 'creative'}
                        )
                        # Session 800: saved_path may be Cloudinary URL or local path
                        image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

                        logger.info(f"✅ Creative upscale complete after {(attempt+1)*2}s - saved to {saved_path}")

                        # Save to history (Session 36: Feature 9)
                        save_to_history(
                            user=request.user,
                            file_path=saved_path,
                            image_type='upscaled_creative',
                            prompt='enhance quality, add details, improve clarity',
                            parameters={'operation': 'upscale', 'method': 'creative'}
                        )

                        return JsonResponse({
                            'success': True,
                            'image_url': image_url
                        })
                    elif result_response.status_code == 202:
                        # Still processing
                        logger.info(f"⏳ Still processing... attempt {attempt+1}/30")
                        continue
                    else:
                        # Error
                        logger.error(f"❌ Poll error: {result_response.status_code} - {result_response.text}")
                        return JsonResponse({
                            'success': False,
                            'error': f'Polling error: {result_response.text[:200]}'
                        }, status=500)

                # Timeout
                return JsonResponse({
                    'success': False,
                    'error': 'Creative upscale timed out after 60 seconds. Try fast or conservative method instead.'
                }, status=500)

            elif 'image' in content_type:
                # Fast/Conservative methods return image directly
                filename = f'upscaled_{method}_{uuid.uuid4().hex[:8]}.png'
                filepath = os.path.join('generated_images', filename)

                # Session 487: Apply creator watermark before saving
                # Session 800: Now returns Cloudinary URL in production
                saved_path = save_watermarked_image(
                    image_bytes=response.content,
                    filename=filepath,
                    user=request.user,
                    generation_params={'operation': 'upscale', 'method': method}
                )
                # Session 800: saved_path may be Cloudinary URL or local path
                image_url = saved_path if saved_path.startswith('http') else default_storage.url(saved_path)

                logger.info(f"✅ Upscale complete: {method} method - saved to {saved_path}")

                # Save to history (Session 36: Feature 9)
                image_type_map = {
                    'fast': 'upscaled_fast',
                    'conservative': 'upscaled_conservative'
                }
                save_to_history(
                    user=request.user,
                    file_path=saved_path,
                    image_type=image_type_map.get(method, 'upscaled_fast'),
                    prompt='',
                    parameters={'operation': 'upscale', 'method': method}
                )

                return JsonResponse({
                    'success': True,
                    'image_url': image_url
                })
            else:
                logger.error(f"❌ Unexpected content type: {content_type}")
                return JsonResponse({
                    'success': False,
                    'error': f'Unexpected response type: {content_type}'
                }, status=500)
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Upscale error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def erase_object(request):
    """
    Erase objects from image using Stability AI erase endpoint.
    Requires: image file, mask (drawn areas to erase)
    Optional: project_id, source_image_id for proper association
    Session 198: Updated to support project association and proper image history
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🖌️ Erase request - project: {project_id}, source_image: {source_image_id}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/erase"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {'output_format': 'png'}

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI erase endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Session 198: Save with proper user folder structure
            filename = f'erased_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Erase complete - saved to {saved_path}")

            # Session 198: Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    # Inherit project from source if not specified
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Erased from image #{source_image.get_sequential_number() if source_image else 'unknown'}",
                file_path=saved_path,
                filename=filename,
                model_used='stability-erase',
                image_type='erased',
                project=project,
                session=source_image.session if source_image else None
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI erase error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Erase error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def inpaint_image(request):
    """
    Inpaint (regenerate) areas of image using Stability AI inpaint endpoint.
    Requires: image file, mask (areas to regenerate), prompt (what to generate)
    Optional: project_id, source_image_id for proper association
    Session 199: Updated to support project association and proper image history (like erase)
    """
    try:
        if 'image' not in request.FILES or 'mask' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image or mask file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt'
            }, status=400)

        image_file = request.FILES['image']
        mask_file = request.FILES['mask']
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Inpaint request - prompt: {prompt}, project: {project_id}, source_image: {source_image_id}")

        url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type),
            'mask': (mask_file.name, mask_file.read(), mask_file.content_type)
        }

        data = {
            'prompt': prompt,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI inpaint endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Session 199: Save with proper user folder structure
            filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Inpaint complete - saved to {saved_path}")

            # Session 199: Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    # Inherit project from source if not specified
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Inpainted: {prompt} (from #{source_image.get_sequential_number() if source_image else 'unknown'})",
                file_path=saved_path,
                filename=filename,
                model_used='stability-inpaint',
                image_type='inpainted',
                project=project,
                session=source_image.session if source_image else None
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI inpaint error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Inpaint error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
def outpaint_image(request):
    """
    Outpaint (extend) image beyond edges using Stability AI outpaint endpoint.
    Session 64: Now supports multiple directions in one call!
    Requires: image file, directions (comma-separated: left,right,up,down), pixels, prompt
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'Missing image file'
            }, status=400)

        prompt = request.POST.get('prompt', '').strip()
        directions_str = request.POST.get('directions', '').strip().lower()  # Session 64: Changed from 'direction' to 'directions'
        pixels_str = request.POST.get('pixels', '').strip()

        if not all([prompt, directions_str, pixels_str]):
            return JsonResponse({
                'success': False,
                'error': 'Missing prompt, directions, or pixels'
            }, status=400)

        try:
            pixels = int(pixels_str)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid pixels value'
            }, status=400)

        # Session 64: Parse multiple directions (comma-separated)
        directions = [d.strip() for d in directions_str.split(',') if d.strip()]

        if not directions:
            return JsonResponse({
                'success': False,
                'error': 'No directions specified'
            }, status=400)

        # Validate all directions
        valid_directions = ['left', 'right', 'up', 'down']
        for direction in directions:
            if direction not in valid_directions:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid direction: {direction} (must be left/right/up/down)'
                }, status=400)

        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"📐 Multi-direction outpaint: {', '.join(directions)} by {pixels}px each - {prompt}")

        # Session 64: Sequential outpainting - each uses result from previous
        current_image_data = request.FILES['image'].read()
        current_filename = request.FILES['image'].name

        url = "https://api.stability.ai/v2beta/stable-image/edit/outpaint"
        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        # Process each direction sequentially
        for i, direction in enumerate(directions):
            logger.info(f"  📐 Step {i+1}/{len(directions)}: Extending {direction}...")

            files = {
                'image': (current_filename, current_image_data, 'image/png')
            }

            data = {
                'prompt': prompt,
                direction: pixels,  # e.g., 'left': 500
                'output_format': 'png'
            }

            response = requests.post(url, headers=headers, files=files, data=data)

            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"❌ Stability AI outpaint error on {direction}: {error_msg}")
                return JsonResponse({
                    'success': False,
                    'error': f'Outpaint failed on {direction}: {error_msg}'
                }, status=500)

            # Use this result as input for next direction
            current_image_data = response.content
            logger.info(f"  ✅ {direction.capitalize()} extension complete")

        # Save final result
        filename = f'outpainted_{"_".join(directions)}_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', filename)
        saved_path = default_storage.save(filepath, ContentFile(current_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Multi-direction outpaint complete - saved to {saved_path}")

        # Save to history (Session 36: Feature 9)
        save_to_history(
            user=request.user,
            file_path=saved_path,
            image_type='outpainted',
            prompt=prompt,
            parameters={
                'operation': 'outpaint',
                'directions': directions,  # Session 64: Save as list
                'pixels': pixels,
                'prompt': prompt
            }
        )

        return JsonResponse({
            'success': True,
            'image_url': image_url,
            'directions_completed': directions  # Session 64: Let frontend know what was done
        })

    except Exception as e:
        logger.error(f"❌ Outpaint error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# IMAGE HISTORY / GALLERY (Feature 9)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def image_history(request):
    """
    Retrieve user's image history for gallery display.

    Query parameters:
    - image_type: Filter by type (generated, erased, inpainted, upscaled_fast, etc.)
    - model_used: Filter by model (core, sdxl, sd3, ultra)
    - style: Filter by style preset
    - is_favorite: Filter favorites (true/false)
    - sort_by: Sort field (created_at, view_count, download_count) - default: -created_at
    - limit: Max results (default: 50)
    - offset: Pagination offset (default: 0)

    Returns:
    {
        "success": true,
        "images": [
            {
                "id": 123,
                "filename": "image.png",
                "url": "/media/...",
                "thumbnail_url": "/media/...",
                "image_type": "generated",
                "prompt": "...",
                "model_used": "sdxl",
                "style": "pixar",
                "width": 1024,
                "height": 1024,
                "created_at": "2025-11-03T...",
                "is_favorite": false,
                "view_count": 5,
                "download_count": 2,
                "has_children": true  // has edits
            }
        ],
        "total": 245,
        "limit": 50,
        "offset": 0
    }
    """
    try:
        from content.models import ImageHistory, CreativeProject

        user = request.user

        # Session 293: Check if filtering by project_id
        # If project_id is provided, show ALL images in that project (if user has access)
        # This allows seeing images created by workflow engine which may use a different user context
        project_id = request.query_params.get('project_id') or request.query_params.get('project')
        logger.info(f"📸 image_history: user={user.username}, project_id={project_id}")

        if project_id:
            # Verify user has access to this project (owns it or is a collaborator)
            try:
                project = CreativeProject.objects.get(id=project_id)
                logger.info(f"📸 Found project: {project.name}, owner={project.user_id}")
                # Allow access if user owns the project (single-user app)
                if project.user != user:
                    # Check if this is a shared/public project or user is collaborator
                    # For now, allow read access to all projects (since it's a single-user app)
                    logger.info(f"📸 User {user.id} accessing project owned by {project.user_id}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"📸 Project not found: {project_id}")
                return Response({
                    'success': False,
                    'error': 'Project not found'
                }, status=404)

            # Get ALL images in this project, not just user's images
            # Session 293: DON'T exclude data: URIs for project queries - needed for Creative Toolbox
            # The dropdown only shows metadata (id, prompt), not the actual image data
            queryset = ImageHistory.objects.filter(project_id=project_id).select_related(
                'project', 'session'
            ).prefetch_related('child_images')
            logger.info(f"📸 Query for project {project_id}: {queryset.count()} images found")
        else:
            # No project filter - show only user's own images
            # Session 94: Exclude data URI images (too large for JSON response)
            # Phase 2 P1: Use select_related/prefetch_related to avoid N+1 queries
            queryset = ImageHistory.objects.filter(user=user).exclude(
                file_path__startswith='data:'
            ).select_related('project', 'session').prefetch_related('child_images')

        # Apply filters
        image_type = request.query_params.get('image_type')
        if image_type:
            queryset = queryset.filter(image_type=image_type)

        model_used = request.query_params.get('model_used')
        if model_used:
            queryset = queryset.filter(model_used=model_used)

        style = request.query_params.get('style')
        if style:
            queryset = queryset.filter(style=style)

        is_favorite = request.query_params.get('is_favorite')
        if is_favorite is not None:
            queryset = queryset.filter(is_favorite=is_favorite.lower() == 'true')

        # Get total count
        total = queryset.count()

        # Apply sorting
        sort_by = request.query_params.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)

        # Apply pagination
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))

        queryset = queryset[offset:offset + limit]

        # Build response
        images = []
        for img in queryset:
            # Session 293: For data URIs, don't include the huge base64 in response
            # Just include a placeholder URL - frontend can fetch individual images if needed
            url = img.get_full_url()
            thumbnail_url = img.get_thumbnail_url()

            # Truncate data URIs to prevent huge responses
            if url and url.startswith('data:'):
                url = f"/api/images/{img.id}/view/"  # Use API endpoint instead
            if thumbnail_url and thumbnail_url.startswith('data:'):
                thumbnail_url = f"/api/images/{img.id}/thumbnail/"

            images.append({
                'id': img.id,
                'sequential_number': img.get_sequential_number(),  # Session 96: Hybrid ID system
                'seed': img.seed,  # Session 95: For reproducibility
                'filename': img.filename,
                'url': url,
                'thumbnail_url': thumbnail_url,
                'image_type': img.image_type,
                'prompt': img.prompt,
                'model_used': img.model_used,
                'style': img.style,
                'width': img.image_width,
                'height': img.image_height,
                'file_size': img.file_size_bytes,
                'created_at': img.created_at.isoformat(),
                'is_favorite': img.is_favorite,
                'view_count': img.view_count,
                'download_count': img.download_count,
                'has_children': img.child_images.exists(),
                'user_notes': img.user_notes,
                'tags': img.tags
            })

        logger.info(f"📊 Gallery request: returned {len(images)}/{total} images for {user.username}")

        return Response({
            'success': True,
            'images': images,
            'total': total,
            'limit': limit,
            'offset': offset
        })

    except Exception as e:
        logger.error(f"❌ Image history error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_image(request, image_id):
    """
    Session 293: Serve an image by its UUID.
    Returns the image data (handles both file-based and data URI images).
    """
    from content.models import ImageHistory
    from django.http import HttpResponse
    import base64

    try:
        image = ImageHistory.objects.get(id=image_id)

        # Check if user has access (owns it or it's in a project they can access)
        # For now, allow access if user is authenticated

        if image.file_path.startswith('data:'):
            # Parse data URI: data:image/png;base64,XXXXXX
            try:
                header, encoded = image.file_path.split(',', 1)
                # Extract mime type: data:image/png;base64 -> image/png
                mime_type = header.split(':')[1].split(';')[0]
                image_data = base64.b64decode(encoded)
                return HttpResponse(image_data, content_type=mime_type)
            except Exception as e:
                logger.error(f"Failed to parse data URI: {e}")
                return Response({'error': 'Invalid image data'}, status=500)
        else:
            # File-based image - redirect to actual URL
            from django.shortcuts import redirect
            from django.core.files.storage import default_storage
            return redirect(default_storage.url(image.file_path))

    except ImageHistory.DoesNotExist:
        return Response({'error': 'Image not found'}, status=404)
    except Exception as e:
        logger.error(f"Error serving image {image_id}: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Session 197: Upload an image file to a project.

    Request (multipart/form-data):
    - image: File upload
    - project_id: UUID of the project
    - description: Optional description/prompt

    Returns:
    {
        "success": true,
        "image_id": "uuid",
        "sequential_number": 42,
        "url": "/media/..."
    }
    """
    try:
        from content.models import ImageHistory
        from projects.models import CreativeProject
        import uuid as uuid_lib
        from PIL import Image
        import io

        # Get the uploaded file
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'success': False, 'error': 'No image file provided'}, status=400)

        # Get project
        project_id = request.data.get('project_id')
        project = None
        if project_id:
            try:
                if isinstance(project_id, str):
                    project_id = uuid_lib.UUID(project_id)
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                return Response({'success': False, 'error': 'Project not found'}, status=404)

        # Get description
        description = request.data.get('description', '') or request.data.get('prompt', 'Uploaded image')

        # Read image and get dimensions
        image_data = image_file.read()
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size

        # Generate unique filename
        ext = image_file.name.split('.')[-1].lower() if '.' in image_file.name else 'png'
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            ext = 'png'
        filename = f"uploaded_{uuid_lib.uuid4().hex[:12]}.{ext}"

        # Save to media directory
        import os
        from django.conf import settings

        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_images')
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Create ImageHistory record
        relative_path = f"uploaded_images/{filename}"

        image_record = ImageHistory.objects.create(
            user=request.user,
            filename=filename,
            file_path=relative_path,
            image_type='uploaded',
            prompt=description,
            parameters={},
            model_used='upload',
            image_width=width,
            image_height=height,
            file_size_bytes=len(image_data),
            project=project
        )

        logger.info(f"📤 Image uploaded: {filename} (ID: {image_record.id})")

        return Response({
            'success': True,
            'image_id': str(image_record.id),
            'sequential_number': image_record.get_sequential_number(),
            'url': image_record.get_full_url(),
            'filename': filename
        })

    except Exception as e:
        logger.error(f"❌ Image upload error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, image_id):
    """
    Toggle favorite status for an image.

    Returns updated favorite status.

    Session 489: Now tracks implicit learning signals.
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.is_favorite = not image.is_favorite
        image.save(update_fields=['is_favorite'])

        logger.info(f"⭐ Toggled favorite for image {image_id}: {image.is_favorite}")

        # Session 489: Track implicit learning signal
        try:
            from core.services.implicit_learning import get_learning_service
            learning = get_learning_service()
            if image.is_favorite:
                # Favoriting = positive signal
                learning.track_favorite(
                    user_id=request.user.id,
                    content_id=str(image_id),
                    style=image.style or None,
                    model=image.model_used or None
                )
            # Note: unfavoriting doesn't generate a negative signal (neutral action)
        except Exception as learn_error:
            logger.debug(f"Implicit learning tracking failed (non-fatal): {learn_error}")

        return Response({
            'success': True,
            'is_favorite': image.is_favorite
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    """
    Delete an image from history.

    Also deletes the actual file from storage.

    Session 489: Now tracks implicit learning signals (negative signal).
    """
    try:
        from content.models import ImageHistory

        image = ImageHistory.objects.get(id=image_id, user=request.user)

        # Session 489: Track implicit learning signal BEFORE deleting
        # (need the image data for style/model info)
        try:
            from core.services.implicit_learning import get_learning_service
            learning = get_learning_service()
            learning.track_delete(
                user_id=request.user.id,
                content_id=str(image_id),
                style=image.style or None,
                model=image.model_used or None
            )
        except Exception as learn_error:
            logger.debug(f"Implicit learning tracking failed (non-fatal): {learn_error}")

        # Delete file from storage
        try:
            if default_storage.exists(image.file_path):
                default_storage.delete(image.file_path)
            if image.thumbnail and default_storage.exists(image.thumbnail):
                default_storage.delete(image.thumbnail)
        except Exception as e:
            logger.warning(f"⚠️ Could not delete files for image {image_id}: {e}")

        # Delete database record
        image.delete()

        logger.info(f"🗑️ Deleted image {image_id} for {request.user.username}")

        return Response({
            'success': True,
            'message': 'Image deleted successfully'
        })

    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Delete image error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# BATCH DOWNLOAD (Session 37: Feature 10)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_download_images(request):
    """
    Download multiple images as a ZIP file.

    Expects JSON: { "image_ids": ["uuid1", "uuid2", ...] }

    Returns ZIP file containing:
    - All selected images
    - metadata.json with image information
    """
    try:
        from content.models import ImageHistory

        image_ids = request.data.get('image_ids', [])

        if not image_ids:
            return Response({
                'success': False,
                'error': 'No images selected'
            }, status=400)

        # Fetch images for this user only
        images = ImageHistory.objects.filter(
            id__in=image_ids,
            user=request.user
        ).order_by('-created_at')

        if not images.exists():
            return Response({
                'success': False,
                'error': 'No images found'
            }, status=404)

        logger.info(f"📦 Creating ZIP with {images.count()} images for {request.user.username}")

        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # Metadata for JSON file
            metadata = {
                'downloaded_at': datetime.now().isoformat(),
                'total_images': images.count(),
                'images': []
            }

            # Add each image to ZIP
            for idx, img in enumerate(images, 1):
                try:
                    # Get file from storage
                    if not default_storage.exists(img.file_path):
                        logger.warning(f"⚠️ File not found: {img.file_path}")
                        continue

                    # Read file data
                    logger.info(f"📂 Reading file: {img.file_path}")
                    with default_storage.open(img.file_path, 'rb') as f:
                        image_data = f.read()

                    # Create unique filename
                    file_ext = os.path.splitext(img.filename)[1] or '.png'
                    safe_filename = f"{idx:03d}_{img.image_type}_{img.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, image_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(image_data)} bytes)")

                    # Build metadata entry with safe defaults
                    try:
                        metadata_entry = {
                            'filename': safe_filename,
                            'original_filename': img.filename or 'unknown.png',
                            'image_type': img.image_type or 'unknown',
                            'prompt': img.prompt or '',
                            'model_used': img.model_used or '',
                            'style': img.style or '',
                            'dimensions': f"{img.image_width or 0}x{img.image_height or 0}",
                            'file_size_bytes': img.file_size_bytes or 0,
                            'created_at': img.created_at.isoformat() if img.created_at else '',
                            'is_favorite': bool(img.is_favorite),
                            'tags': img.tags or '',
                            'parameters': img.parameters if img.parameters else {}
                        }
                        metadata['images'].append(metadata_entry)
                        logger.info(f"📝 Added metadata for {safe_filename}")
                    except Exception as meta_error:
                        logger.error(f"❌ Error building metadata for {img.id}: {meta_error}", exc_info=True)
                        # Add simplified metadata entry
                        metadata['images'].append({
                            'filename': safe_filename,
                            'image_type': str(img.image_type),
                            'error': 'Metadata partially unavailable'
                        })

                except Exception as e:
                    logger.error(f"❌ Error processing image {img.id}: {e}", exc_info=True)
                    continue

            # Add metadata.json
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr('metadata.json', metadata_json)
            logger.info("✅ Added metadata.json to ZIP")

        # Prepare response
        zip_buffer.seek(0)

        # Session 489: Track implicit learning signals for each downloaded image
        try:
            from core.services.implicit_learning import get_learning_service
            learning = get_learning_service()
            for img in images:
                learning.track_download(
                    user_id=request.user.id,
                    content_id=str(img.id),
                    style=img.style or None,
                    model=img.model_used or None
                )
        except Exception as learn_error:
            logger.debug(f"Implicit learning tracking failed (non-fatal): {learn_error}")

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="images_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'

        logger.info(f"🎉 ZIP created successfully with {images.count()} images")

        return response

    except Exception as e:
        logger.error(f"❌ Batch download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 38: FEATURE 11 - IMAGE-TO-IMAGE CONTROL
# =============================================================================

def control_sketch(request):
    """
    Convert a sketch into a refined image using Stability AI Control Sketch.

    Expected request: Form data with:
    - 'image': sketch image file (can be hand-drawn or canvas generated)
    - 'prompt': text description of desired result
    - 'control_strength': float 0-1 (how much to follow sketch, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No sketch image provided'
            }, status=400)

        sketch_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎨 Control Sketch request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/sketch endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/sketch"

        files = {
            'image': (sketch_file.name, sketch_file.read(), sketch_file.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'sketch_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Sketch control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='sketch_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_sketch',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control sketch error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def control_structure(request):
    """
    Transform an image while maintaining its structure using Stability AI Control Structure.

    Expected request: Form data with:
    - 'image': reference image file (structure will be preserved)
    - 'prompt': text description of desired style/transformation
    - 'control_strength': float 0-1 (how much to follow structure, default 0.7)
    - 'negative_prompt': optional negative prompt

    Returns: {success: true, image_url: 'url_to_generated_image'}
    """
    try:
        # Validate inputs
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No reference image provided'
            }, status=400)

        ref_image = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_strength = float(request.POST.get('control_strength', 0.7))
        negative_prompt = request.POST.get('negative_prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🏗️ Control Structure request: {prompt} (strength: {control_strength})")

        # Call Stability AI control/structure endpoint
        url = "https://api.stability.ai/v2beta/stable-image/control/structure"

        files = {
            'image': (ref_image.name, ref_image.read(), ref_image.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        if negative_prompt:
            data['negative_prompt'] = negative_prompt

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            # Save the generated image
            filename = f'structure_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', filename)

            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Structure control complete - saved to {saved_path}")

            # Save to history
            save_to_history(
                user=request.user,
                file_path=saved_path,
                image_type='structure_control',
                prompt=prompt,
                parameters={
                    'operation': 'control_structure',
                    'control_strength': control_strength,
                    'negative_prompt': negative_prompt
                }
            )

            return JsonResponse({
                'success': True,
                'image_url': image_url
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control structure error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def control_unified(request):
    """
    Session 199: Unified control endpoint for all Stability AI control types.
    Supports: sketch, structure, style

    Expected request: Form data with:
    - 'image': control image file
    - 'prompt': text description of desired result
    - 'control_type': 'sketch' | 'structure' | 'style'
    - 'control_strength': float 0-1 (default 0.7)
    - 'project_id': optional project ID for association
    - 'source_image_id': optional source image ID

    Returns: {success: true, image_url: '...', image_id: '...', sequential_number: N}
    """
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No control image provided'
            }, status=400)

        image_file = request.FILES['image']
        prompt = request.POST.get('prompt', '').strip()
        control_type = request.POST.get('control_type', 'structure').strip().lower()
        control_strength = float(request.POST.get('control_strength', 0.7))
        project_id = request.POST.get('project_id')
        source_image_id = request.POST.get('source_image_id')

        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)

        # Validate control type
        valid_types = ['sketch', 'structure', 'style']
        if control_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': f'Invalid control type: {control_type}. Must be one of: {", ".join(valid_types)}'
            }, status=400)

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')

        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        logger.info(f"🎛️ Control {control_type} request - prompt: {prompt}, strength: {control_strength}, project: {project_id}")

        # Select the appropriate API endpoint
        url = f"https://api.stability.ai/v2beta/stable-image/control/{control_type}"

        files = {
            'image': (image_file.name, image_file.read(), image_file.content_type or 'image/png')
        }

        data = {
            'prompt': prompt,
            'control_strength': control_strength,
            'output_format': 'png'
        }

        headers = {
            'Authorization': f'Bearer {stability_key}',
            'Accept': 'image/*'
        }

        logger.info(f"📤 Calling Stability AI {control_type} control endpoint...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        logger.info(f"📥 Response status: {response.status_code}, size: {len(response.content)} bytes")

        if response.status_code == 200:
            # Save with proper user folder structure
            filename = f'{control_type}_control_{uuid.uuid4().hex[:8]}.png'
            filepath = os.path.join('generated_images', request.user.username, filename)
            saved_path = default_storage.save(filepath, ContentFile(response.content))
            image_url = default_storage.url(saved_path)

            logger.info(f"✅ Control {control_type} complete - saved to {saved_path}")

            # Get project and source image for proper association
            from content.models import ImageHistory, CreativeProject
            project = None
            source_image = None

            if project_id:
                try:
                    project = CreativeProject.objects.get(id=project_id, user=request.user)
                except CreativeProject.DoesNotExist:
                    pass

            if source_image_id:
                try:
                    source_image = ImageHistory.objects.get(id=source_image_id, user=request.user)
                    if not project and source_image.project:
                        project = source_image.project
                except ImageHistory.DoesNotExist:
                    pass

            # Create ImageHistory record with project association
            new_image = ImageHistory.objects.create(
                user=request.user,
                prompt=f"Control {control_type}: {prompt} (from #{source_image.get_sequential_number() if source_image else 'unknown'})",
                file_path=saved_path,
                filename=filename,
                model_used=f'stability-control-{control_type}',
                image_type=f'{control_type}_control',
                project=project,
                session=source_image.session if source_image else None
            )

            logger.info(f"✅ Created ImageHistory: {new_image.id}, project: {project.id if project else 'none'}")

            return JsonResponse({
                'success': True,
                'image_url': image_url,
                'image_id': str(new_image.id),
                'sequential_number': new_image.get_sequential_number()
            })
        else:
            error_msg = response.text
            logger.error(f"❌ Stability AI {control_type} control error: {error_msg}")
            return JsonResponse({
                'success': False,
                'error': f'Stability AI error: {error_msg}'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Control unified error: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW EXECUTION (Session 41: Real API Integration)
# ========================================

@csrf_exempt
@api_view(['POST'])
def execute_workflow_step(request):
    """
    Execute a single workflow step by routing to the appropriate operation.

    Expected JSON request body:
    {
        "operation": "upscale_fast" | "upscale_conservative" | "upscale_creative" |
                     "remove_background" | "recolor" | "erase" | "inpaint" |
                     "outpaint" | "sketch" | "structure" | "generate",
        "inputImageUrl": "url_to_image" (required for all except generate),
        "config": {
            // Operation-specific parameters
            "prompt": "...",           // for generate, recolor, inpaint, outpaint, sketch, structure
            "search_prompt": "...",    // for recolor
            "select_prompt": "...",    // for recolor
            "creativity": 0.5,         // for outpaint
            "direction": "up",         // for outpaint
            "control_strength": 0.7,   // for sketch, structure
            // ... etc
        }
    }

    Returns: {success: true, imageUrl: "url_to_result_image"}
    """
    try:
        # Parse JSON request (DRF already parses request.body for us)
        data = request.data
        operation = (data.get('operation') or '').strip().lower()
        input_image_url = (data.get('inputImageUrl') or '').strip()
        config = data.get('config', {})

        logger.info(f"🎭 Workflow step execution: {operation}")

        # Validate operation
        valid_operations = [
            'upscale_fast', 'upscale_conservative', 'upscale_creative',
            'remove_background', 'recolor', 'erase', 'inpaint', 'outpaint',
            'sketch', 'structure', 'generate'
        ]

        if operation not in valid_operations:
            return JsonResponse({
                'success': False,
                'error': f'Invalid operation: {operation}'
            }, status=400)

        # Download input image if URL provided (all operations except generate need this)
        image_file = None
        if input_image_url and operation != 'generate':
            try:
                # Download image from URL
                if input_image_url.startswith('http'):
                    img_response = requests.get(input_image_url, timeout=10)
                    img_response.raise_for_status()
                    image_data = img_response.content
                elif input_image_url.startswith('/media/'):
                    # Local file - read from filesystem
                    local_path = os.path.join(settings.MEDIA_ROOT, input_image_url.replace('/media/', ''))
                    with open(local_path, 'rb') as f:
                        image_data = f.read()
                elif input_image_url.startswith('data:image'):
                    # Data URI - extract base64 data
                    if 'base64,' in input_image_url:
                        base64_data = input_image_url.split('base64,')[1]
                        image_data = base64.b64decode(base64_data)
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Invalid data URI format'
                        }, status=400)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid image URL format'
                    }, status=400)

                # Check and resize if needed (Stability AI limits: 10MiB file size, 1,048,576 pixels)
                # Note: Different operations have different limits, using most conservative (1024x1024)
                from PIL import Image
                import io

                max_size_bytes = 10 * 1024 * 1024  # 10MiB
                max_pixels = 1_048_576  # 1024x1024 (most conservative limit across all operations)

                # Open image to check dimensions
                img = Image.open(io.BytesIO(image_data))
                width, height = img.size
                total_pixels = width * height

                logger.info(f"📏 Original image: {width}x{height} = {total_pixels:,} pixels, {len(image_data):,} bytes")

                # Check if we need to resize due to pixel count
                needs_resize = False
                if total_pixels > max_pixels:
                    # Calculate scale factor to fit within pixel limit
                    scale_factor = (max_pixels / total_pixels) ** 0.5
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)

                    logger.info(f"⚠️ Too many pixels ({total_pixels:,}), resizing to {new_width}x{new_height}")

                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    needs_resize = True

                # Check if we need to resize due to file size
                if needs_resize or len(image_data) > max_size_bytes:
                    logger.info(f"⚠️ Optimizing image size...")

                    # Save with optimization
                    quality = 85
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                    image_data = img_bytes.getvalue()

                    # If still too large, reduce quality iteratively
                    while len(image_data) > max_size_bytes and quality > 60:
                        quality -= 10
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG', optimize=True, quality=quality)
                        image_data = img_bytes.getvalue()

                    logger.info(f"✅ Optimized image to {len(image_data):,} bytes (quality={quality})")

                # Create a file-like object
                from django.core.files.uploadedfile import InMemoryUploadedFile

                image_io = io.BytesIO(image_data)
                image_file = InMemoryUploadedFile(
                    image_io,
                    field_name='image',
                    name=f'workflow_input_{uuid.uuid4().hex[:8]}.png',
                    content_type='image/png',
                    size=len(image_data),
                    charset=None
                )

                logger.info(f"✅ Downloaded input image: {len(image_data):,} bytes")

            except Exception as e:
                logger.error(f"❌ Failed to download input image: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download input image: {str(e)}'
                }, status=500)

        # Route to appropriate operation
        if operation == 'upscale_fast':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/fast'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_fast_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_fast',
                        prompt='Fast Upscale (4x)'
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='generation',
                            task_description="Generated image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        # Don't fail content creation if contribution tracking fails

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Fast upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_conservative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/conservative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}

                # Conservative upscale requires a prompt
                prompt = config.get('prompt', 'High quality image, detailed, sharp')
                data = {
                    'output_format': 'png',
                    'prompt': prompt
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'upscaled_conservative_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='upscaled_conservative',
                        prompt='Conservative Upscale (4K)'
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution for image upscaling: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Conservative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'upscale_creative':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/upscale/creative'

                # Prepare image data
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'prompt': config.get('prompt', 'enhance quality, add details, improve clarity')
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'application/json'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    # Creative upscale is async - poll for result
                    import time
                    result_data = response.json()
                    generation_id = result_data.get('id')

                    result_url = f"https://api.stability.ai/v2beta/stable-image/upscale/creative/result/{generation_id}"

                    for attempt in range(30):
                        time.sleep(2)
                        result_response = requests.get(
                            result_url,
                            headers={'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}
                        )

                        if result_response.status_code == 200:
                            filename = f'upscaled_creative_{uuid.uuid4().hex[:8]}.png'
                            filepath = os.path.join('generated_images', request.user.username, filename)
                            saved_path = default_storage.save(filepath, ContentFile(result_response.content))
                            image_url = default_storage.url(saved_path)

                            # Save to history
                            from content.models import ImageHistory
                            image_history = ImageHistory.objects.create(
                                user=request.user,
                                filename=filename,
                                file_path=saved_path,
                                image_type='upscaled_creative',
                                prompt=config.get('prompt', 'enhance quality')
                            )

                            # Session 142: Track agent contribution
                            try:
                                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                                agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                                AgentContribution.objects.create(
                                    agent=agent,
                                    image=image_history,
                                    project=None,
                                    contribution_type='editing',
                                    task_description="Edited image using image-generation-agent",
                                    execution_time_seconds=0.0
                                )
                                logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                            except Exception as e:
                                logger.error(f"❌ Failed to create agent contribution: {e}")
                                logger.error(f"❌ Failed to create agent contribution: {e}")

                            return JsonResponse({'success': True, 'image_url': image_url})

                    return JsonResponse({'success': False, 'error': 'Timeout waiting for creative upscale'}, status=500)
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Creative upscale failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'remove_background':
            # Call Stability AI directly
            try:
                from PIL import Image
                img = Image.open(image_file)

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/remove-background'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'removed_bg_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='background_removed',
                        prompt='Remove Background'
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Remove background failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'recolor':
            # Recolor uses automatic object detection
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate required config
                if not config:
                    config = {}

                search_prompt = config.get('search_prompt', '').strip()
                prompt = config.get('prompt', '').strip()

                # Provide helpful defaults if empty
                if not search_prompt:
                    search_prompt = 'object'
                if not prompt:
                    prompt = 'red color'

                logger.info(f"🎨 Recolor: '{search_prompt}' → '{prompt}'")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'prompt': prompt,
                    'search_prompt': search_prompt,
                    'select_prompt': config.get('select_prompt', search_prompt),
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'recolored_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='recolored',
                        prompt=f"Recolor {config.get('search_prompt', 'object')} to {config.get('prompt', 'red')}"
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Recolor failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'outpaint':
            # Outpaint uses direction parameters
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Validate config
                if not config:
                    config = {}

                # Check if at least one direction is selected
                has_direction = any([
                    config.get('left'),
                    config.get('right'),
                    config.get('up'),
                    config.get('down')
                ])

                if not has_direction:
                    # Default to extending right
                    logger.info("⚠️ No direction specified, defaulting to right")
                    config['right'] = True

                logger.info(f"📐 Outpaint directions: L={config.get('left')} R={config.get('right')} U={config.get('up')} D={config.get('down')}")

                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/outpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {'image': ('image.png', img_bytes.read(), 'image/png')}
                data = {
                    'output_format': 'png',
                    'creativity': config.get('creativity', 0.5)
                }

                # Add prompt if provided
                prompt = config.get('prompt', '').strip()
                if prompt:
                    data['prompt'] = prompt

                # Add direction parameters (in pixels, max 2000 per side)
                if config.get('left'):
                    data['left'] = 500
                if config.get('right'):
                    data['right'] = 500
                if config.get('up'):
                    data['up'] = 500
                if config.get('down'):
                    data['down'] = 500

                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'outpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='outpainted',
                        prompt=config.get('prompt', 'Extend image')
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Outpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'erase':
            # Erase object using mask from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to erase.'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/erase'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {'output_format': 'png'}
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'erased_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='erased',
                        prompt='Erase Object'
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Erase failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'inpaint':
            # Inpaint using mask and prompt from workflow
            try:
                from PIL import Image
                img = Image.open(image_file)

                # Check for mask data
                mask_data = config.get('maskData', '').strip()
                if not mask_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing mask. Please draw areas to inpaint.'
                    }, status=400)

                # Check for prompt
                prompt = config.get('prompt', '').strip()
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Missing prompt. What should we fill the area with?'
                    }, status=400)

                # Decode base64 mask
                if 'base64,' in mask_data:
                    mask_data = mask_data.split('base64,')[1]
                mask_bytes = base64.b64decode(mask_data)

                # Create file-like object for mask
                mask_io = io.BytesIO(mask_bytes)
                mask_file = InMemoryUploadedFile(
                    mask_io,
                    field_name='mask',
                    name='mask.png',
                    content_type='image/png',
                    size=len(mask_bytes),
                    charset=None
                )

                # Call API
                stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
                url = 'https://api.stability.ai/v2beta/stable-image/edit/inpaint'

                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                files = {
                    'image': ('image.png', img_bytes.read(), 'image/png'),
                    'mask': ('mask.png', mask_file.read(), 'image/png')
                }
                data = {
                    'prompt': prompt,
                    'output_format': 'png'
                }
                headers = {'Authorization': f'Bearer {stability_key}', 'Accept': 'image/*'}

                response = requests.post(url, headers=headers, files=files, data=data)

                if response.status_code == 200:
                    filename = f'inpainted_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(response.content))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='inpainted',
                        prompt=prompt
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='editing',
                            task_description="Edited image using image-editing-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({'success': False, 'error': response.text}, status=500)

            except Exception as e:
                logger.error(f"❌ Inpaint failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation == 'generate':
            # Generate image from prompt
            try:
                from content.image_generation import ImageGenerationService

                # Use improved_prompt if available, fallback to basic prompt
                # Session 61: This ensures GPT-5 enhanced prompts are actually used!
                prompt = config.get('improved_prompt') or config.get('prompt', '')
                if not prompt:
                    return JsonResponse({
                        'success': False,
                        'error': 'Prompt is required for generate operation'
                    }, status=400)

                # Get configuration
                style = config.get('style', '')
                quality = config.get('quality', 'balanced')  # fast, balanced, high, premium
                negative_prompt = config.get('negative_prompt', '')

                # Session 61: Add strong negative prompts for logo generation to prevent text/brands
                # If style indicates this is a logo, add logo-specific negative prompts
                if style in ['vector', 'flat'] or 'logo' in prompt.lower():
                    logo_negative = 'text, letters, words, typography, starbucks, nike, apple, brand names, existing logos, trademarks, copyrighted logos, photographic, realistic, people, crowds'
                    negative_prompt = f'{logo_negative}, {negative_prompt}' if negative_prompt else logo_negative
                    logger.info(f"🚫 Added logo-specific negative prompts to prevent text/brands")

                # Map quality to model
                quality_map = {
                    'fast': 'core',
                    'balanced': 'sdxl',
                    'high': 'sd3',
                    'premium': 'ultra'
                }
                model = quality_map.get(quality, 'sdxl')

                logger.info(f"🎨 Generating image: prompt='{prompt[:50]}...', model={model}, style={style}")

                # Generate image
                generator = ImageGenerationService()
                result = generator.generate_image(
                    prompt=prompt,
                    model=model,
                    style=style,
                    negative_prompt=negative_prompt,
                    aspect_ratio='1:1'
                )

                if result.success and result.images:
                    # Save the generated image
                    # Extract base64 data from data URI (format: "data:image/png;base64,...")
                    data_uri = result.images[0]
                    if 'base64,' in data_uri:
                        base64_data = data_uri.split('base64,')[1]
                    else:
                        base64_data = data_uri
                    image_data = base64.b64decode(base64_data)
                    filename = f'generated_{uuid.uuid4().hex[:8]}.png'
                    filepath = os.path.join('generated_images', request.user.username, filename)
                    saved_path = default_storage.save(filepath, ContentFile(image_data))
                    image_url = default_storage.url(saved_path)

                    # Save to history
                    from content.models import ImageHistory
                    image_history = ImageHistory.objects.create(
                        user=request.user,
                        filename=filename,
                        file_path=saved_path,
                        image_type='generated',
                        prompt=prompt
                    )

                    # Session 142: Track agent contribution
                    try:
                        from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                        agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                        AgentContribution.objects.create(
                            agent=agent,
                            image=image_history,
                            project=None,
                            contribution_type='generation',
                            task_description="Generated image using image-generation-agent",
                            execution_time_seconds=0.0
                        )
                        logger.info(f"✅ Agent contribution tracked for image {{ image_history.id }}")
                    except Exception as e:
                        logger.error(f"❌ Failed to create agent contribution: {e}")
                        logger.error(f"❌ Failed to create agent contribution: {e}")

                    return JsonResponse({'success': True, 'image_url': image_url})
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result.error_message or 'Generation failed'
                    }, status=500)

            except Exception as e:
                logger.error(f"❌ Generate failed: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

        elif operation in ['sketch', 'structure']:
            # These operations need separate implementations
            return JsonResponse({
                'success': False,
                'error': f'Operation "{operation}" requires different implementation. Please use the dedicated tab.'
            }, status=400)

        else:
            return JsonResponse({
                'success': False,
                'error': f'Operation not implemented: {operation}'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Workflow step execution error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ========================================
# UNIFIED GALLERY API (Session 53: Phase 2)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_batch_download(request):
    """
    Download multiple items (images, videos, audio) as a ZIP file.

    Expects JSON: {
        "items": [
            {"id": "uuid1", "type": "image"},
            {"id": "uuid2", "type": "video"},
            ...
        ]
    }

    Returns ZIP file containing:
    - All selected media files
    - metadata.json with information about all items
    """
    try:
        from content.models import ImageHistory, VideoHistory
        from django.http import HttpResponse
        import zipfile
        from io import BytesIO
        import os

        items = request.data.get('items', [])

        if not items:
            return Response({
                'success': False,
                'error': 'No items selected'
            }, status=400)

        logger.info(f"📦 Creating unified ZIP with {len(items)} items for {request.user.username}")

        # Separate items by type
        image_ids = [item['id'] for item in items if item['type'] == 'image']
        video_ids = [item['id'] for item in items if item['type'] == 'video']

        # Fetch all items for this user only
        images = ImageHistory.objects.filter(
            id__in=image_ids,
            user=request.user
        ).order_by('-created_at')

        videos = VideoHistory.objects.filter(
            id__in=video_ids,
            user=request.user,
            status='completed'
        ).order_by('-created_at')

        total_items = images.count() + videos.count()

        if total_items == 0:
            return Response({
                'success': False,
                'error': 'No items found'
            }, status=404)

        logger.info(f"📦 Found {images.count()} images and {videos.count()} videos")

        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # Metadata for JSON file
            metadata = {
                'downloaded_at': datetime.now().isoformat(),
                'total_items': total_items,
                'total_images': images.count(),
                'total_videos': videos.count(),
                'items': []
            }

            item_counter = 1

            # Add images to ZIP
            for img in images:
                try:
                    # Get file from storage
                    if not default_storage.exists(img.file_path):
                        logger.warning(f"⚠️ File not found: {img.file_path}")
                        continue

                    # Read file data
                    with default_storage.open(img.file_path, 'rb') as f:
                        image_data = f.read()

                    # Create unique filename
                    file_ext = os.path.splitext(img.filename)[1] or '.png'
                    safe_filename = f"{item_counter:03d}_image_{img.image_type}_{img.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, image_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(image_data)} bytes)")

                    # Add metadata
                    metadata['items'].append({
                        'filename': safe_filename,
                        'type': 'image',
                        'image_type': img.image_type or 'unknown',
                        'prompt': img.prompt or '',
                        'model_used': img.model_used or '',
                        'style': img.style or '',
                        'dimensions': f"{img.image_width or 0}x{img.image_height or 0}",
                        'file_size_bytes': img.file_size_bytes or 0,
                        'created_at': img.created_at.isoformat() if img.created_at else '',
                        'is_favorite': bool(img.is_favorite),
                        'parameters': img.parameters if img.parameters else {}
                    })

                    item_counter += 1

                except Exception as e:
                    logger.error(f"❌ Error processing image {img.id}: {e}")
                    continue

            # Add videos to ZIP
            for video in videos:
                try:
                    # Videos are stored by URL, need to download them
                    import requests

                    # Download video
                    response = requests.get(video.video_url, timeout=60)
                    response.raise_for_status()
                    video_data = response.content

                    # Create unique filename
                    file_ext = '.mp4'  # Runway videos are MP4
                    safe_filename = f"{item_counter:03d}_video_{video.video_type}_{video.id}{file_ext}"

                    # Add to ZIP
                    zip_file.writestr(safe_filename, video_data)
                    logger.info(f"✅ Added {safe_filename} to ZIP ({len(video_data)} bytes)")

                    # Add metadata
                    metadata['items'].append({
                        'filename': safe_filename,
                        'type': 'video',
                        'video_type': video.video_type or 'unknown',
                        'prompt': video.prompt or '',
                        'model_used': video.model_used or '',
                        'duration': video.duration,
                        'ratio': video.ratio or '',
                        'dimensions': f"{video.dimensions}" if video.dimensions else '',
                        'file_size_bytes': len(video_data),
                        'created_at': video.created_at.isoformat() if video.created_at else '',
                        'is_favorite': bool(video.is_favorite),
                        'parameters': video.parameters if video.parameters else {}
                    })

                    item_counter += 1

                except Exception as e:
                    logger.error(f"❌ Error processing video {video.id}: {e}")
                    continue

            # Add metadata.json
            metadata_json = json.dumps(metadata, indent=2)
            zip_file.writestr('metadata.json', metadata_json)
            logger.info("✅ Added metadata.json to ZIP")

        # Prepare response
        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="donkey_betz_content_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'

        logger.info(f"🎉 Unified ZIP created successfully with {total_items} items")

        return response

    except Exception as e:
        logger.error(f"❌ Unified batch download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unified_toggle_favorite(request):
    """
    Toggle favorite status for any media type (image, video, audio).

    Expects JSON: {
        "id": "uuid",
        "type": "image" | "video" | "audio"
    }

    Returns: {
        "success": true,
        "is_favorite": true/false
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory

        item_id = request.data.get('id')
        item_type = request.data.get('type')

        if not item_id or not item_type:
            return Response({
                'success': False,
                'error': 'Missing id or type'
            }, status=400)

        # Toggle favorite based on type
        if item_type == 'image':
            try:
                item = ImageHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Image {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except ImageHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Image not found'
                }, status=404)

        elif item_type == 'video':
            try:
                item = VideoHistory.objects.get(id=item_id, user=request.user)
                item.is_favorite = not item.is_favorite
                item.save()

                logger.info(f"{'⭐' if item.is_favorite else '☆'} Video {item_id} favorite: {item.is_favorite}")

                return Response({
                    'success': True,
                    'is_favorite': item.is_favorite
                })

            except VideoHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Video not found'
                }, status=404)

        else:
            return Response({
                'success': False,
                'error': f'Unsupported type: {item_type}'
            }, status=400)

    except Exception as e:
        logger.error(f"❌ Unified toggle favorite error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_image_view(request, image_id):
    """
    Track when a user views an image in fullsize.

    URL: POST /api/images/view/<uuid>/
    """
    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.view_count += 1
        image.save(update_fields=['view_count'])

        logger.info(f"✅ Image view tracked: {image_id} (total: {image.view_count})")

        return Response({
            'success': True,
            'view_count': image.view_count
        })
    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Track image view error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_image_download(request, image_id):
    """
    Track when a user downloads an image.

    URL: POST /api/images/download/<uuid>/
    """
    try:
        image = ImageHistory.objects.get(id=image_id, user=request.user)
        image.download_count += 1
        image.save(update_fields=['download_count'])

        logger.info(f"✅ Image download tracked: {image_id} (total: {image.download_count})")

        return Response({
            'success': True,
            'download_count': image.download_count
        })
    except ImageHistory.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Image not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Track image download error: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def unified_gallery(request):
    """
    Unified gallery endpoint combining images, videos, and audio.

    Query parameters:
    - type: Filter by media type (all/images/videos/audio) - default: all
    - favorite: Filter favorites (true/false)
    - search: Search term (searches in prompts)
    - sort_by: Sort field (-created_at, created_at, -view_count, etc.) - default: -created_at
    - limit: Max results (default: 20)
    - offset: Pagination offset (default: 0)

    Returns:
    {
        "count": 100,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": "uuid",
                "type": "image" | "video" | "audio",
                "url": "...",
                "thumbnail_url": "...",
                "prompt": "...",
                "created_at": "...",
                "is_favorite": true/false,
                "view_count": 10,
                "download_count": 5,
                "model_used": "...",
                "parameters": {...},
                // Type-specific fields
                "image_type": "generated" (for images),
                "video_type": "text_to_video" (for videos),
                ...
            }
        ]
    }
    """
    try:
        from content.models import ImageHistory, VideoHistory, AudioHistory
        from django.db.models import Q

        user = request.user

        # Get query parameters
        media_type = request.query_params.get('type', 'all').lower()
        is_favorite = request.query_params.get('favorite')
        search_term = request.query_params.get('search', '').strip()
        sort_by = request.query_params.get('sort_by', '-created_at')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))

        # Collect results from different media types
        all_items = []

        # Session 688: Handle anonymous users - return empty gallery
        if not user.is_authenticated:
            return Response({
                'count': 0,
                'next': None,
                'previous': None,
                'results': [],
                'items': []  # For compatibility with React frontend
            })

        # Session 862: Track errors per media type for debugging
        media_errors = []

        # Fetch images if requested
        if media_type in ['all', 'images']:
          try:
            # Session 94: Exclude data URI images (too large for JSON response)
            # Session 865: Include user's own images AND system-generated images
            image_queryset = ImageHistory.objects.filter(
                Q(user=user) | Q(user__username__in=['system_autonomous', 'system', 'admin'])
            ).exclude(
                file_path__startswith='data:'
            )

            # Apply filters
            if is_favorite is not None:
                image_queryset = image_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                image_queryset = image_queryset.filter(
                    Q(prompt__icontains=search_term) |
                    Q(user_notes__icontains=search_term)
                )

            # Convert to unified format
            for img in image_queryset:
                # Session 111: Build absolute URLs for mobile app compatibility
                image_url = img.get_full_url()
                thumbnail_url = img.get_thumbnail_url()

                # Convert relative URLs to absolute URLs
                if image_url and not image_url.startswith(('http://', 'https://', 'data:')):
                    image_url = request.build_absolute_uri(image_url)
                if thumbnail_url and not thumbnail_url.startswith(('http://', 'https://', 'data:')):
                    thumbnail_url = request.build_absolute_uri(thumbnail_url)

                all_items.append({
                    'id': str(img.id),
                    'sequential_number': img.get_sequential_number(),  # Session 117: Sequential ID
                    'type': 'image',
                    'url': image_url,
                    'thumbnail_url': thumbnail_url,
                    'prompt': img.prompt,
                    'created_at': img.created_at,
                    'is_favorite': img.is_favorite,
                    'view_count': img.view_count,
                    'download_count': img.download_count,
                    'model_used': img.model_used,
                    'parameters': img.parameters,
                    # Image-specific fields
                    'image_type': img.image_type,
                    'style': img.style,
                    'width': img.image_width,
                    'height': img.image_height,
                    'filename': img.filename,
                    'user_notes': img.user_notes,
                    'tags': img.tags,
                })
          except Exception as e:
            logger.warning(f"Error fetching images: {e}")
            media_errors.append(f"images: {str(e)}")

          # Session 865: Also fetch images from WorkspaceOperation (ImageAgent outputs)
          try:
            from core.models_skin_layer import WorkspaceOperation
            import re

            # Get ImageAgent operations with Cloudinary URLs
            image_ops = WorkspaceOperation.objects.filter(
                agent_name='ImageAgent',
                success=True
            ).order_by('-created_at')[:50]  # Limit to recent 50

            for op in image_ops:
                content = op.file_content_after or ''
                # Extract Cloudinary URLs
                urls = re.findall(r'https://res\.cloudinary\.com/[^\s\"\'\)]+', content)
                for url in urls:
                    # Clean up URL (remove trailing punctuation)
                    url = url.rstrip('.,;:')
                    all_items.append({
                        'id': str(op.id),
                        'type': 'image',
                        'url': url,
                        'thumbnail_url': url,  # Use same URL for thumbnail
                        'prompt': op.agent_task[:200] if op.agent_task else 'AI Generated Image',
                        'created_at': op.created_at,
                        'is_favorite': False,
                        'view_count': 0,
                        'download_count': 0,
                        'model_used': 'ImageAgent',
                        'parameters': {},
                        'image_type': 'agent_generated',
                        'style': 'AI Generated',
                        'width': None,
                        'height': None,
                        'filename': url.split('/')[-1] if url else None,
                        'user_notes': '',
                        'tags': [],
                        'source': 'workspace_operation',
                    })
          except Exception as e:
            logger.warning(f"Error fetching WorkspaceOperation images: {e}")
            media_errors.append(f"workspace_images: {str(e)}")

        # Fetch videos if requested
        if media_type in ['all', 'videos']:
          try:
            # Session 865: Include user's own videos AND system-generated videos
            # Note: Removed cloudfront exclusion (Session 96) because Runway videos use cloudfront
            video_queryset = VideoHistory.objects.filter(
                Q(user=user) | Q(user__username__in=['system_autonomous', 'system', 'admin']),
                status='completed'
            ).exclude(
                # Only exclude Google Storage URLs (truly expired)
                Q(video_url__icontains='storage.googleapis.com')
            )

            # Apply filters
            if is_favorite is not None:
                video_queryset = video_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                video_queryset = video_queryset.filter(
                    Q(prompt__icontains=search_term) |
                    Q(user_notes__icontains=search_term)
                )

            # Convert to unified format
            for video in video_queryset:
                # Session 111: Build absolute URLs for mobile app compatibility
                video_url = video.video_url
                thumbnail_url = video.thumbnail_url or video.video_url

                # Convert relative URLs to absolute URLs (external CDN URLs are already absolute)
                if video_url and not video_url.startswith(('http://', 'https://', 'data:')):
                    video_url = request.build_absolute_uri(video_url)
                if thumbnail_url and not thumbnail_url.startswith(('http://', 'https://', 'data:')):
                    thumbnail_url = request.build_absolute_uri(thumbnail_url)

                all_items.append({
                    'id': str(video.id),
                    'type': 'video',
                    'url': video_url,
                    'thumbnail_url': thumbnail_url,
                    'prompt': video.prompt,
                    'created_at': video.created_at,
                    'is_favorite': video.is_favorite,
                    'view_count': video.view_count,
                    'download_count': video.download_count,
                    'model_used': video.model_used,
                    'parameters': video.parameters,
                    # Video-specific fields
                    'video_type': video.video_type,
                    'duration': video.duration,
                    'ratio': video.ratio,
                    'video_id': video.video_id,
                    'user_notes': video.user_notes,
                    'tags': video.tags,
                })
          except Exception as e:
            logger.warning(f"Error fetching videos: {e}")
            media_errors.append(f"videos: {str(e)}")

        # Fetch 3D models if requested (Session 137)
        if media_type in ['all', '3d_models', 'models']:
          try:
            from content.models import MiniFigAsset

            # Only show completed 3D models
            model_queryset = MiniFigAsset.objects.filter(user=user, status='completed')

            # Apply filters
            if is_favorite is not None:
                model_queryset = model_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                model_queryset = model_queryset.filter(
                    Q(title__icontains=search_term)
                )

            # Convert to unified format
            for model in model_queryset:
                # Session 172: Prefer local file path over CDN URL (CDN URLs expire)
                # Build absolute URL for 3D file
                if model.local_glb_path:
                    # Use local file (never expires)
                    model_url = f'/media/{model.local_glb_path}'
                else:
                    # Fallback to CDN URL (may be expired)
                    model_url = model.three_d_file or ''
                preview_url = model.preview_image_url or ''

                if model_url and not model_url.startswith(('http://', 'https://')):
                    model_url = request.build_absolute_uri(model_url)
                if preview_url and not preview_url.startswith(('http://', 'https://', 'data:')):
                    preview_url = request.build_absolute_uri(preview_url)

                all_items.append({
                    'id': str(model.id),
                    'type': '3d_model',
                    'url': model_url,
                    'thumbnail_url': preview_url,
                    'prompt': model.title,  # Use title as prompt
                    'created_at': model.created_at,
                    'is_favorite': getattr(model, 'is_favorite', False),
                    'view_count': getattr(model, 'view_count', 0),
                    'download_count': getattr(model, 'download_count', 0),
                    'model_used': 'replicate-trellis',
                    'parameters': model.metadata,
                    # 3D model-specific fields
                    '3d_model_type': 'minifig',
                    'provider': model.provider,
                    'status': model.status,
                    'style': model.metadata.get('style', 'toy'),
                    'scale': model.metadata.get('scale', 'medium'),
                })
          except Exception as e:
            logger.warning(f"Error fetching 3D models: {e}")
            media_errors.append(f"3d_models: {str(e)}")

        # Fetch DaVinci Resolve renders if requested (Session 479)
        if media_type in ['all', 'videos', 'resolve']:
          try:
            from core.models_unified_system import ResolveRenderJob

            # Only show completed resolve renders
            resolve_queryset = ResolveRenderJob.objects.filter(user=user, status='done')

            # Apply filters
            if search_term:
                resolve_queryset = resolve_queryset.filter(
                    Q(color_grade__icontains=search_term) |
                    Q(template__icontains=search_term)
                )

            # Convert to unified format
            for render in resolve_queryset:
                # Build URL for the rendered video
                render_url = render.output_url or ''

                # Convert relative URLs to absolute URLs
                if render_url and not render_url.startswith(('http://', 'https://')):
                    render_url = request.build_absolute_uri(render_url)

                all_items.append({
                    'id': str(render.id),
                    'type': 'resolve',  # Special type for DaVinci Resolve renders
                    'url': render_url,
                    'thumbnail_url': render_url,  # Use video as thumbnail
                    'prompt': f"DaVinci Resolve: {render.color_grade} grade",
                    'created_at': render.created_at,
                    'is_favorite': False,  # No favorite field on ResolveRenderJob yet
                    'view_count': 0,
                    'download_count': 0,
                    'model_used': 'DaVinci Resolve',
                    'parameters': {
                        'template': render.template,
                        'color_grade': render.color_grade,
                        'auto_selected': render.auto_grade_selected,
                        'spider_trends': render.spider_trends_used,
                    },
                    # Resolve-specific fields
                    'video_type': 'resolve_render',
                    'resolve_job_id': render.resolve_job_id,
                    'user_rating': render.user_rating,
                    'was_used': render.was_used,
                    'revenue_generated': float(render.revenue_generated) if render.revenue_generated else 0,
                })
          except Exception as e:
            logger.warning(f"Error fetching Resolve renders: {e}")
            media_errors.append(f"resolve: {str(e)}")

        # Session 865: Add audio support
        if media_type in ['all', 'audio']:
          try:
            # Include user's audio AND system-generated audio
            audio_queryset = AudioHistory.objects.filter(
                Q(user=user) | Q(user__username__in=['system_autonomous', 'system', 'admin'])
            ).order_by('-created_at')

            # Apply filters
            if is_favorite is not None:
                audio_queryset = audio_queryset.filter(is_favorite=is_favorite.lower() == 'true')

            if search_term:
                audio_queryset = audio_queryset.filter(
                    Q(prompt__icontains=search_term) |
                    Q(user_notes__icontains=search_term) |
                    Q(voice_name__icontains=search_term)
                )

            for aud in audio_queryset:
                # Build audio URL
                audio_url = None
                if aud.file_path:
                    if aud.file_path.startswith(('http://', 'https://')):
                        audio_url = aud.file_path
                    else:
                        audio_url = request.build_absolute_uri(f'/media/{aud.file_path}')

                all_items.append({
                    'id': str(aud.id),
                    'type': 'audio',
                    'url': audio_url,
                    'thumbnail_url': None,  # Audio has no thumbnail
                    'prompt': aud.prompt or 'Audio',
                    'created_at': aud.created_at,
                    'is_favorite': aud.is_favorite,
                    'view_count': aud.play_count,
                    'download_count': aud.download_count,
                    'model_used': aud.model_used,
                    'parameters': aud.parameters or {},
                    # Audio-specific fields
                    'audio_type': aud.audio_type,
                    'voice_name': aud.voice_name,
                    'duration_seconds': aud.duration_seconds,
                    'filename': aud.filename,
                    'user_notes': aud.user_notes,
                    'tags': aud.tags or [],
                    'source': 'audio_history',
                })
          except Exception as e:
            logger.warning(f"Error fetching audio: {e}")
            media_errors.append(f"audio: {str(e)}")

        # Session 865: Add 3D model support from WorkspaceOperation
        if media_type in ['all', '3d', 'models']:
          try:
            from core.models_skin_layer import WorkspaceOperation
            import re

            # Get ThreeDAgent operations
            threed_ops = WorkspaceOperation.objects.filter(
                agent_name='ThreeDAgent',
                success=True
            ).order_by('-created_at')[:50]

            for op in threed_ops:
                content = op.file_content_after or ''
                # Extract 3D model URLs (.glb, .gltf, .obj)
                urls = re.findall(r'https://[^\s\"\'\)]+\.(?:glb|gltf|obj)', content, re.IGNORECASE)

                if urls:
                    for url in urls:
                        url = url.rstrip('.,;:')
                        all_items.append({
                            'id': str(op.id),
                            'type': '3d',
                            'url': url,
                            'thumbnail_url': None,  # 3D models need viewer
                            'prompt': op.agent_task[:200] if op.agent_task else '3D Model',
                            'created_at': op.created_at,
                            'is_favorite': False,
                            'view_count': 0,
                            'download_count': 0,
                            'model_used': 'ThreeDAgent',
                            'parameters': {},
                            'model_type': '3d',
                            'filename': url.split('/')[-1] if url else None,
                            'user_notes': '',
                            'tags': [],
                            'source': 'workspace_operation',
                        })
                else:
                    # No URL but has 3D agent output - include as brief/spec
                    all_items.append({
                        'id': str(op.id),
                        'type': '3d',
                        'url': None,
                        'thumbnail_url': None,
                        'prompt': op.agent_task[:200] if op.agent_task else '3D Model Brief',
                        'created_at': op.created_at,
                        'is_favorite': False,
                        'view_count': 0,
                        'download_count': 0,
                        'model_used': 'ThreeDAgent',
                        'parameters': {},
                        'model_type': '3d_brief',
                        'filename': None,
                        'user_notes': content[:500] if content else '',
                        'tags': [],
                        'source': 'workspace_operation',
                    })
          except Exception as e:
            logger.warning(f"Error fetching 3D models: {e}")
            media_errors.append(f"3d_models: {str(e)}")

        # Sort all items
        reverse = sort_by.startswith('-')
        sort_field = sort_by.lstrip('-')

        all_items.sort(
            key=lambda x: x.get(sort_field, ''),
            reverse=reverse
        )

        # Get total count before pagination
        total_count = len(all_items)

        # Apply pagination
        paginated_items = all_items[offset:offset + limit]

        # Convert datetime objects to ISO format strings
        for item in paginated_items:
            if isinstance(item['created_at'], datetime):
                item['created_at'] = item['created_at'].isoformat()

        # Build pagination URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        previous_url = None

        if offset + limit < total_count:
            next_offset = offset + limit
            next_url = f"{base_url}?type={media_type}&limit={limit}&offset={next_offset}"
            if is_favorite:
                next_url += f"&favorite={is_favorite}"
            if search_term:
                next_url += f"&search={search_term}"

        if offset > 0:
            previous_offset = max(0, offset - limit)
            previous_url = f"{base_url}?type={media_type}&limit={limit}&offset={previous_offset}"
            if is_favorite:
                previous_url += f"&favorite={is_favorite}"
            if search_term:
                previous_url += f"&search={search_term}"

        # Session 862: Include errors for debugging (only in non-prod or if requested)
        response_data = {
            'count': total_count,
            'next': next_url,
            'previous': previous_url,
            'results': paginated_items
        }
        if media_errors:
            response_data['_media_errors'] = media_errors
            logger.warning(f"Gallery partial errors: {media_errors}")

        return Response(response_data)

    except Exception as e:
        logger.error(f"❌ Unified gallery error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_gallery(request):
    """
    Get all content (images, videos, audio) for a specific AI session.
    Session 96: Frontend Integration - Session content viewer

    Query parameters:
    - session_id: UUID of the session (required)

    Returns:
    {
        "session": {
            "session_id": "uuid",
            "title": "Session title",
            "created_at": "timestamp",
            "total_images": 5,
            "total_videos": 2,
            "total_audio": 1
        },
        "images": [...],
        "videos": [...],
        "audio": [...]
    }
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory

        user = request.user
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response({
                'error': 'session_id parameter is required'
            }, status=400)

        # Get session
        try:
            session = AISession.objects.get(session_id=session_id, user=user)
        except AISession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=404)

        # Get all images for this session
        images = []
        image_queryset = ImageHistory.objects.filter(
            user=user,
            session=session
        ).exclude(
            file_path__startswith='data:'  # Exclude data URIs
        ).order_by('-created_at')

        for img in image_queryset:
            images.append({
                'id': str(img.id),
                'sequential_number': img.get_sequential_number(),
                'url': img.get_full_url(),
                'thumbnail_url': img.get_thumbnail_url(),
                'prompt': img.prompt,
                'image_type': img.image_type,
                'model_used': img.model_used,
                'style': img.style,
                'seed': img.seed,
                'created_at': img.created_at.isoformat(),
                'is_favorite': img.is_favorite
            })

        # Get all videos for this session
        videos = []
        video_queryset = VideoHistory.objects.filter(
            user=user,
            session=session
        ).order_by('-created_at')

        for vid in video_queryset:
            videos.append({
                'id': str(vid.id),
                'url': vid.video_url,
                'thumbnail_url': vid.thumbnail_url,
                'prompt': vid.prompt,
                'video_type': vid.video_type,
                'model_used': vid.model_used,
                'duration': vid.duration,
                'status': vid.status,
                'created_at': vid.created_at.isoformat(),
                'is_favorite': vid.is_favorite
            })

        # Build response
        response_data = {
            'session': {
                'session_id': str(session.session_id),
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio,
                # Session 117: Include project info for proper resume
                'project': {
                    'id': str(session.project.id),
                    'name': session.project.name,
                    'is_quick_starts': session.project.is_quick_starts
                } if session.project else None,
                # Session 117: Include conversation for AI context (frontend expects 'transcript')
                'transcript': session.conversation_transcript or []
            },
            'images': images,
            'videos': videos,
            'audio': []  # NOTE: Audio support pending AudioHistory model
        }

        logger.info(f"📊 Session gallery: {session_id} - {len(images)} images, {len(videos)} videos")
        return Response(response_data)

    except Exception as e:
        logger.error(f"❌ Session gallery error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sessions(request):
    """
    List all AI sessions for the current user with filtering and sorting
    Session 97: Session Management UI - List View

    Query parameters:
    - sort: 'newest' (default), 'oldest', 'most_content', 'alphabetical'
    - project_filter: 'all' (default), 'with_project', 'no_project'
    - content_filter: 'all' (default), 'images', 'videos', 'audio'

    Returns:
    {
        "sessions": [
            {
                "session_id": "uuid",
                "title": "Session title",
                "created_at": "timestamp",
                "updated_at": "timestamp",
                "total_images": 5,
                "total_videos": 2,
                "total_audio": 1,
                "project": {
                    "id": "uuid",
                    "name": "Project name"
                } or null,
                "first_prompt": "Original user request"
            },
            ...
        ],
        "stats": {
            "total_sessions": 10,
            "total_images": 45,
            "total_videos": 12,
            "total_audio": 5,
            "sessions_with_projects": 6
        }
    }
    """
    try:
        from content.models import AISession

        user = request.user

        # Get query parameters
        sort_by = request.query_params.get('sort', 'newest')
        project_filter = request.query_params.get('project_filter', 'all')
        content_filter = request.query_params.get('content_filter', 'all')

        # Base queryset
        queryset = AISession.objects.filter(user=user)

        # Apply project filter
        if project_filter == 'with_project':
            queryset = queryset.filter(project__isnull=False)
        elif project_filter == 'no_project':
            queryset = queryset.filter(project__isnull=True)

        # Apply content filter
        if content_filter == 'images':
            queryset = queryset.filter(total_images__gt=0)
        elif content_filter == 'videos':
            queryset = queryset.filter(total_videos__gt=0)
        elif content_filter == 'audio':
            queryset = queryset.filter(total_audio__gt=0)

        # Apply sorting
        if sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'most_content':
            # Sort by total content (images + videos + audio) descending
            from django.db.models import F
            queryset = queryset.annotate(
                total_content=F('total_images') + F('total_videos') + F('total_audio')
            ).order_by('-total_content')
        elif sort_by == 'alphabetical':
            queryset = queryset.order_by('title')

        # Format sessions
        sessions_data = []
        for session in queryset:
            session_data = {
                'session_id': str(session.session_id),
                'title': session.title,
                'created_at': session.created_at.isoformat() if session.created_at else None,
                'updated_at': session.updated_at.isoformat() if session.updated_at else None,
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio,
                'first_prompt': session.first_prompt or '',
                'project': None
            }

            # Include project info if linked
            if session.project:
                session_data['project'] = {
                    'id': str(session.project.id),
                    'name': session.project.name
                }

            sessions_data.append(session_data)

        # Calculate stats
        all_sessions = AISession.objects.filter(user=user)
        stats = {
            'total_sessions': all_sessions.count(),
            'total_images': sum(s.total_images for s in all_sessions),
            'total_videos': sum(s.total_videos for s in all_sessions),
            'total_audio': sum(s.total_audio for s in all_sessions),
            'sessions_with_projects': all_sessions.filter(project__isnull=False).count()
        }

        response_data = {
            'sessions': sessions_data,
            'stats': stats
        }

        logger.info(f"📊 List sessions: {len(sessions_data)} sessions returned for user {user.username}")
        return Response(response_data)

    except Exception as e:
        logger.error(f"❌ List sessions error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_sessions(request, project_id):
    """
    Get all AI sessions associated with a specific project
    Session 97: Option 3 - Session Browser in Projects Tab

    Returns sessions with their content counts and last activity
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory, CreativeProject

        # Verify project exists and belongs to user
        try:
            project = CreativeProject.objects.get(id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response({
                'error': 'Project not found'
            }, status=404)

        # Get all sessions that have content linked to this project
        # This includes sessions where images/videos were added to the project
        image_session_ids = ImageHistory.objects.filter(
            user=request.user,
            project_id=project_id
        ).values_list('session_id', flat=True).distinct()

        video_session_ids = VideoHistory.objects.filter(
            user=request.user,
            project_id=project_id
        ).values_list('session_id', flat=True).distinct()

        # Combine session IDs
        session_ids = set(list(image_session_ids) + list(video_session_ids))

        # Remove None values (content without sessions)
        session_ids.discard(None)

        # Get session objects
        sessions = AISession.objects.filter(
            id__in=session_ids,
            user=request.user
        ).order_by('-updated_at')

        # Format sessions
        sessions_data = []
        for session in sessions:
            # Count content in this project from this session
            project_images = ImageHistory.objects.filter(
                session=session,
                project_id=project_id
            ).count()

            project_videos = VideoHistory.objects.filter(
                session=session,
                project_id=project_id
            ).count()

            sessions_data.append({
                'session_id': str(session.session_id),
                'title': session.title or 'Untitled Session',
                'created_at': session.created_at.isoformat(),
                'last_activity': session.updated_at.isoformat(),
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio,
                'project_images': project_images,  # Images from this session in this project
                'project_videos': project_videos,  # Videos from this session in this project
                'has_project': session.project_id is not None,
                'conversation_length': len(session.conversation_transcript or '[]')
            })

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name
            },
            'sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })

    except Exception as e:
        logger.error(f"❌ Get project sessions error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_assets(request, session_id):
    """
    Get all assets (images and videos) for a specific session
    Session 101: Project Browser - Mobile Flutter App

    GET /api/v1/sessions/<session_id>/assets/

    Returns:
    {
        "success": true,
        "session": {
            "session_id": "uuid",
            "title": "...",
            "created_at": "..."
        },
        "images": [
            {
                "id": "uuid",
                "file_path": "...",
                "prompt": "...",
                "created_at": "...",
                "model_used": "...",
                "style": "..."
            }
        ],
        "videos": [
            {
                "id": "uuid",
                "file_path": "...",
                "prompt": "...",
                "created_at": "...",
                "model_used": "...",
                "duration": 5
            }
        ],
        "total_images": 10,
        "total_videos": 3
    }
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory

        # Verify session exists and belongs to user
        try:
            session = AISession.objects.get(id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=404)

        # Get all images for this session
        images = ImageHistory.objects.filter(
            session=session,
            user=request.user
        ).order_by('-created_at')

        images_data = []
        for img in images:
            images_data.append({
                'id': str(img.id),
                'file_path': img.file_path,
                'prompt': img.prompt,
                'created_at': img.created_at.isoformat(),
                'model_used': img.model_used,
                'style': img.style if hasattr(img, 'style') else None,
                'image_type': img.image_type if hasattr(img, 'image_type') else 'generated',
            })

        # Get all videos for this session
        videos = VideoHistory.objects.filter(
            session=session,
            user=request.user
        ).order_by('-created_at')

        videos_data = []
        for vid in videos:
            videos_data.append({
                'id': str(vid.id),
                'file_path': vid.file_path,
                'prompt': vid.prompt,
                'created_at': vid.created_at.isoformat(),
                'model_used': vid.model_used if hasattr(vid, 'model_used') else 'runway',
                'duration': vid.duration if hasattr(vid, 'duration') else None,
                'status': vid.status if hasattr(vid, 'status') else 'completed',
            })

        return Response({
            'success': True,
            'session': {
                'session_id': str(session.session_id),
                'title': session.title or 'Untitled Session',
                'created_at': session.created_at.isoformat(),
                'session_type': session.session_type if hasattr(session, 'session_type') else 'default',
            },
            'images': images_data,
            'videos': videos_data,
            'total_images': len(images_data),
            'total_videos': len(videos_data),
        })

    except Exception as e:
        logger.error(f"❌ Get session assets error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_analytics(request):
    """
    Get comprehensive analytics about user's AI sessions
    Session 97: Option 4 - Session Analytics Dashboard

    Returns:
    - Most used prompts/keywords
    - Content type distribution
    - Average session duration
    - Most productive sessions
    - Style preferences
    - Time-based activity patterns
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory
        from collections import Counter

        user = request.user

        # Get all sessions
        sessions = AISession.objects.filter(user=user)
        total_sessions = sessions.count()

        if total_sessions == 0:
            return Response({
                'success': True,
                'total_sessions': 0,
                'message': 'No sessions yet'
            })

        # Content type distribution
        total_images = sum(s.total_images for s in sessions)
        total_videos = sum(s.total_videos for s in sessions)
        total_audio = sum(s.total_audio for s in sessions)
        total_content = total_images + total_videos + total_audio

        # Sessions with projects
        sessions_with_projects = sessions.filter(project__isnull=False).count()

        # Most productive sessions (by total content)
        most_productive = []
        for session in sessions.order_by('-total_images', '-total_videos', '-total_audio')[:5]:
            content_count = session.total_images + session.total_videos + session.total_audio
            if content_count > 0:
                most_productive.append({
                    'session_id': str(session.session_id),
                    'title': session.title or 'Untitled Session',
                    'total_content': content_count,
                    'images': session.total_images,
                    'videos': session.total_videos,
                    'audio': session.total_audio,
                    'created_at': session.created_at.isoformat()
                })

        # Average content per session
        avg_images = total_images / total_sessions if total_sessions > 0 else 0
        avg_videos = total_videos / total_sessions if total_sessions > 0 else 0
        avg_audio = total_audio / total_sessions if total_sessions > 0 else 0

        # Most common styles (from ImageHistory)
        style_counter = Counter()
        for img in ImageHistory.objects.filter(user=user).exclude(style__isnull=True).exclude(style=''):
            if img.style:
                style_counter[img.style] += 1

        top_styles = [{'style': style, 'count': count} for style, count in style_counter.most_common(10)]

        # Most common models
        model_counter = Counter()
        for img in ImageHistory.objects.filter(user=user).exclude(model_used__isnull=True).exclude(model_used=''):
            if img.model_used:
                model_counter[img.model_used] += 1

        top_models = [{'model': model, 'count': count} for model, count in model_counter.most_common(5)]

        # Activity by day of week
        activity_by_day = {
            'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0,
            'Friday': 0, 'Saturday': 0, 'Sunday': 0
        }
        for session in sessions:
            day_name = session.created_at.strftime('%A')
            activity_by_day[day_name] += 1

        # Recent activity (last 7 days)
        from datetime import timedelta
        from django.utils import timezone
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_sessions = sessions.filter(created_at__gte=seven_days_ago).count()
        recent_content = ImageHistory.objects.filter(
            user=user,
            created_at__gte=seven_days_ago
        ).count() + VideoHistory.objects.filter(
            user=user,
            created_at__gte=seven_days_ago
        ).count()

        # Most common prompt keywords (extract from session titles)
        keyword_counter = Counter()
        for session in sessions:
            if session.title:
                # Simple keyword extraction (split by common words)
                words = session.title.lower().split()
                # Filter out common words
                stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during'}
                keywords = [w for w in words if w not in stop_words and len(w) > 3]
                keyword_counter.update(keywords)

        top_keywords = [{'keyword': kw, 'count': count} for kw, count in keyword_counter.most_common(15)]

        return Response({
            'success': True,
            'overview': {
                'total_sessions': total_sessions,
                'total_content': total_content,
                'total_images': total_images,
                'total_videos': total_videos,
                'total_audio': total_audio,
                'sessions_with_projects': sessions_with_projects,
                'avg_images_per_session': round(avg_images, 2),
                'avg_videos_per_session': round(avg_videos, 2),
                'avg_audio_per_session': round(avg_audio, 2)
            },
            'content_distribution': {
                'images_percentage': round((total_images / total_content * 100) if total_content > 0 else 0, 1),
                'videos_percentage': round((total_videos / total_content * 100) if total_content > 0 else 0, 1),
                'audio_percentage': round((total_audio / total_content * 100) if total_content > 0 else 0, 1)
            },
            'most_productive_sessions': most_productive,
            'style_preferences': top_styles,
            'model_usage': top_models,
            'activity_by_day': activity_by_day,
            'recent_activity': {
                'sessions_last_7_days': recent_sessions,
                'content_last_7_days': recent_content
            },
            'top_keywords': top_keywords
        })

    except Exception as e:
        logger.error(f"❌ Get session analytics error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_session(request, session_id):
    """
    Delete an AI session and optionally its associated content
    Session 97: Delete session functionality

    Query parameters:
    - delete_content: 'true' to also delete images/videos/audio from this session
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory

        # Get the session
        try:
            session = AISession.objects.get(session_id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'error': 'Session not found'
            }, status=404)

        # Check if user wants to delete content too
        delete_content = request.query_params.get('delete_content', 'false').lower() == 'true'

        session_title = session.title or 'Untitled Session'
        content_counts = {
            'images': session.total_images,
            'videos': session.total_videos,
            'audio': session.total_audio
        }

        if delete_content:
            # Delete all content from this session
            images_deleted = ImageHistory.objects.filter(session=session).delete()[0]
            videos_deleted = VideoHistory.objects.filter(session=session).delete()[0]
            # Audio would go here when implemented

            logger.info(f"🗑️ Deleted session '{session_title}' and its content: {images_deleted} images, {videos_deleted} videos")
        else:
            # Just unlink content from session (keep content, remove session reference)
            ImageHistory.objects.filter(session=session).update(session=None)
            VideoHistory.objects.filter(session=session).update(session=None)

            logger.info(f"🗑️ Deleted session '{session_title}', content preserved")

        # Delete the session itself
        session.delete()

        return Response({
            'success': True,
            'message': f"Session '{session_title}' deleted successfully",
            'content_deleted': delete_content,
            'content_counts': content_counts
        })

    except Exception as e:
        logger.error(f"❌ Delete session error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def promote_session_to_project(request, session_id):
    """
    Promote a Quick Starts session to its own standalone project
    Session 98: Quick Starts Promotion Feature

    Request body:
    {
        "project_name": "My New Project",
        "description": "Optional description",
        "category": "Optional category"
    }

    Returns:
    {
        "success": true,
        "project": {
            "id": "uuid",
            "name": "Project name",
            ...
        },
        "session": {
            "session_id": "uuid",
            "new_project_id": "uuid"
        },
        "content_moved": {
            "images": 5,
            "videos": 2
        }
    }
    """
    try:
        from content.models import AISession, ImageHistory, VideoHistory, CreativeProject
        import json

        # Get the session
        try:
            session = AISession.objects.get(session_id=session_id, user=request.user)
        except AISession.DoesNotExist:
            return Response({
                'error': 'Session not found or you do not have permission to access it'
            }, status=404)

        # Verify this session is in Quick Starts project
        quick_starts = None
        if session.project:
            quick_starts = session.project
            if not quick_starts.is_quick_starts:
                return Response({
                    'error': 'This session is not in Quick Starts. Only Quick Starts sessions can be promoted.'
                }, status=400)
        else:
            # Session has no project - this shouldn't happen, but allow it
            logger.warning(f"⚠️ Session {session_id} has no project, proceeding with promotion anyway")

        # Get request data
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}

        project_name = data.get('project_name', '').strip()
        if not project_name:
            # Auto-generate name from session title or first prompt
            project_name = session.title or session.first_prompt or f"Session {session.session_id[:8]}"
            # Clean up the name
            project_name = project_name[:100]  # Limit length

        description = data.get('description', '').strip()
        category = data.get('category', '').strip()

        # Create new standalone project
        new_project = CreativeProject.objects.create(
            user=request.user,
            name=project_name,
            description=description or f"Promoted from Quick Starts session: {session.title or 'Untitled'}",
            category=category or 'general',
            status='in_progress',
            is_quick_starts=False  # NOT a Quick Starts project
        )

        logger.info(f"📁 Created new project: {new_project.name} (ID: {new_project.id})")

        # Move session to new project
        old_project_id = session.project_id
        session.project = new_project
        session.save()

        # Move all content from this session to the new project
        images_moved = ImageHistory.objects.filter(
            session=session,
            user=request.user
        ).update(project=new_project)

        videos_moved = VideoHistory.objects.filter(
            session=session,
            user=request.user
        ).update(project=new_project)

        logger.info(f"✅ Promoted session {session_id} to project '{new_project.name}'")
        logger.info(f"   Moved {images_moved} images and {videos_moved} videos")

        return Response({
            'success': True,
            'message': f"Session promoted to project '{new_project.name}'",
            'project': {
                'id': str(new_project.id),
                'name': new_project.name,
                'description': new_project.description,
                'category': new_project.category,
                'status': new_project.status
            },
            'session': {
                'session_id': str(session.session_id),
                'title': session.title,
                'old_project_id': str(old_project_id) if old_project_id else None,
                'new_project_id': str(new_project.id)
            },
            'content_moved': {
                'images': images_moved,
                'videos': videos_moved
            }
        })

    except Exception as e:
        logger.error(f"❌ Promote session to project error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_featured_examples(request):
    """
    Get curated featured examples for the Examples Gallery
    Session 56: Phase A Task 2
    Returns diverse, high-quality images showcasing platform capabilities
    """
    try:
        from content.models import ImageHistory

        # Get diverse examples - ONLY generated images (Session 56: Bug fix)
        # Edited images (upscale, remove bg, etc.) have operation names as prompts,
        # not useful for "Try This Prompt" feature
        examples = []

        # Strategy: Get up to 12 recent generated images with variety
        # Prioritize diverse models and styles to showcase platform capabilities
        # Session 94: Filter out data URI images (they're too large for JSON response)
        examples = ImageHistory.objects.filter(
            user=request.user,
            image_type='generated'  # ONLY show generated images!
        ).exclude(
            file_path__startswith='data:'  # Exclude base64 data URIs
        ).order_by('-created_at')[:12]

        # Format response
        formatted_examples = []
        for img in examples:
            # Session 94: Additional safety check - skip if file_path is data URI or too long
            if not img.file_path or img.file_path.startswith('data:') or len(img.file_path) > 500:
                continue

            formatted_examples.append({
                'id': str(img.id),
                'url': img.file_path if img.file_path.startswith('http') else f'/media/{img.file_path}',
                'prompt': img.prompt or f'{img.image_type.replace("_", " ").title()}',
                'image_type': img.image_type,
                'model_used': img.model_used or 'sdxl',
                'style': img.style or '',
                'created_at': img.created_at.isoformat()
            })

        logger.info(f"✨ Returning {len(formatted_examples)} featured examples")
        return Response({
            'examples': formatted_examples,
            'count': len(formatted_examples)
        })

    except Exception as e:
        logger.error(f"❌ Error loading featured examples: {str(e)}")
        return Response({
            'error': str(e),
            'examples': []
        }, status=500)


# ========================================
# INTELLIGENT PROMPT IMPROVEMENT (Session 56: Phase B.1)
# ========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def improve_workflow_prompt(request):
    """
    Improve user's workflow prompt using AI intelligence
    Session 56: Phase B.1 - Intelligent Workflow Prompting

    Takes a user's simple prompt and workflow type, returns an optimized
    prompt that will generate better results for that specific workflow.

    Example:
        Input: "Light Work Handyman services" (Logo Creator)
        Output: "Professional logo for 'Light Work' handyman services..."
    """
    try:
        user_prompt = request.data.get('prompt', '').strip()
        workflow_type = request.data.get('workflow_type', '').lower()

        # Normalize workflow type: convert hyphens to underscores
        workflow_type = workflow_type.replace('-', '_')

        if not user_prompt:
            return Response({
                'error': 'Prompt is required'
            }, status=400)

        if not workflow_type:
            return Response({
                'error': 'Workflow type is required'
            }, status=400)

        # Workflow-specific system prompts
        # Session 61: Enhanced with examples, negative prompts, and success patterns
        WORKFLOW_CONTEXTS = {
            'logo_creator': {
                'context': 'logo design for businesses and brands',
                'instructions': """You are an AI prompt enhancement assistant. The user has already built a complete logo prompt with their chosen style (Character Mascot, Vector, Illustrative, etc.).

Your task: ENHANCE the existing prompt by adding specific visual details that will improve the result. DO NOT rewrite or change the style.

CRITICAL RULES:
✅ KEEP the existing style (Character Mascot, Vector, Minimalist, etc.) - NEVER change it
✅ KEEP the brand name, colors, and core concept
✅ ADD helpful visual details (specific features, expressions, poses, details)
✅ ADD quality markers (4K, professional, cinematic lighting)
✅ Be like Claude helping the user - suggest improvements, don't rewrite

❌ NEVER change "Character Mascot" to "minimalist vector"
❌ NEVER change "DreamWorks animation" to "flat design"
❌ NEVER override the user's style choice
❌ NEVER add assumptions (like "sports betting" if not mentioned)

EXAMPLES OF ENHANCEMENT (Not Rewriting):

Example 1:
User's prompt: "Donkey Betz, gray-blue/orange/white colors, character mascot, DreamWorks style"
❌ BAD (Rewriting): "Minimalist vector logo, flat design, avoid cartoonish"
✅ GOOD (Enhancing): "Donkey Betz character mascot with VERY LONG PROMINENT BLACK-TIPPED EARS (key donkey feature), gray-blue colored body with white muzzle, wearing orange accent (vest or gear), confident smart expression, stocky muscular build (not sleek like horse), DreamWorks animation quality, expressive detailed face with personality, cinematic lighting, 4K resolution, professional character design"

Example 2:
User's prompt: "Light Work handyman, navy blue and yellow, wrench and lightbulb, vector style"
❌ BAD (Rewriting): "Character mascot, cartoon style"
✅ GOOD (Enhancing): "Light Work handyman logo in clean vector style, light bulb with wrench incorporated, navy blue and bright yellow colors, simple geometric shapes, sharp clean lines, professional icon design, centered composition, white background, scalable vector art, modern minimalist aesthetic"

Example 3:
User's prompt: "Coffee shop logo, warm browns, illustrative style, hand-drawn feel"
❌ BAD (Rewriting): "Flat minimalist vector"
✅ GOOD (Enhancing): "Coffee shop logo in hand-drawn illustrative style, warm brown tones with cream accents, artistic linework showing coffee cup with steam wisps, cozy approachable feel, sketch-like quality with personality, detailed but not cluttered, professional illustration quality, unique character"

YOUR ROLE:
Think of yourself as Claude did in the conversation - the user said "donkey logo" and Claude said "Great! To make it clearly a DONKEY not a horse, emphasize: VERY LONG EARS with black tips, stocky build, gray-blue coloring, white muzzle."

That's enhancement. That's helpful. That's what you should do.

CRITICAL PROMPT STRUCTURE:
Your enhanced prompt MUST follow this exact order (AI commits to subject in first 10 words!):

1. **SUBJECT FIRST** - What creature/character (T-Rex, donkey, person, etc.)
2. **POSE/ACTION** - What they're doing (standing, dancing, running, etc.)
3. **CLOTHING/ACCESSORIES** - What they're wearing (emphasize heavily!)
4. **STYLE** - Art style (DreamWorks, vector, minimalist, etc.)
5. **COLORS** - Color scheme
6. **DETAILS** - Background, lighting, mood

Example with clothing:
User: "T-Rex wearing disco ball necklace and bell-bottom pants"
❌ WRONG ORDER: "WEARING sparkly disco ball necklace, DRESSED IN bell-bottom pants... T-Rex dinosaur character..."
✅ CORRECT ORDER: "T-Rex dinosaur character standing upright in disco pose, WEARING sparkly disco ball necklace around neck, DRESSED IN purple bell-bottom pants with wide flared legs, platform shoes on feet, DreamWorks animation style..."

WHY: If you say "WEARING disco necklace" first, AI generates a human wearing jewelry. If you say "T-Rex dinosaur" first, AI generates a T-Rex, then adds the jewelry to the T-Rex!

CLOTHING EMPHASIS (after subject is established):
- Use emphatic language: "WEARING [item]", "DRESSED IN [item]", "clearly visible [item]"
- Repeat key items: "disco ball necklace... necklace shining... reflective necklace"
- Describe vividly: colors, materials, fit, details
- AI models ignore clothing unless heavily emphasized!

IMPORTANT: Keep your enhanced prompt under 1200 characters total (Stability AI hard limit is 2000, but shorter is better for accuracy). Be specific but VERY concise - prioritize the most important visual details.

Format your response as a single enhanced prompt. Keep the user's style sacred, just add helpful details."""
            },
            'portrait_enhancer': {
                'context': 'professional portrait photography',
                'instructions': """You are a professional portrait photographer. The user wants to create a high-quality portrait.

Your task: Transform their input into a detailed portrait prompt that will generate professional, polished results.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "headshot"
✅ Good: "professional corporate headshot, business attire, studio lighting with soft key light and rim light, neutral gray background, shallow depth of field, confident friendly expression, sharp focus on eyes, 85mm lens perspective, high resolution"

❌ Bad: "portrait of a woman"
✅ Good: "elegant portrait of a professional woman in her 30s, natural confident expression, soft studio lighting with subtle fill, blurred bokeh background, sharp focus, professional quality, warm color tones, business casual attire"

❌ Bad: "CEO photo"
✅ Good: "executive portrait of confident CEO, tailored suit, modern office environment blurred in background, dramatic side lighting, sharp focus, professional quality, sophisticated composition, approachable expression"

NEGATIVE PROMPTS (avoid these):
- Distorted anatomy, extra limbs, deformed features
- Harsh direct flash, unnatural lighting
- Cluttered busy backgrounds
- Low resolution, blurry, grainy
- Awkward poses, forced expressions
- Oversaturated colors, heavy filters

STABILITY AI SUCCESS PATTERNS:
- Specify lighting: "studio lighting", "soft natural light", "golden hour", "dramatic side lighting"
- Mention depth of field: "shallow depth of field", "bokeh background", "blurred background"
- Include camera details: "85mm lens", "portrait lens", "professional camera"
- Quality markers: "high resolution", "sharp focus", "professional quality", "4K"
- Composition: "centered composition", "rule of thirds", "headshot framing"
- Expression: "confident", "friendly", "professional", "natural smile"

Consider:
- Subject description (person, profession, mood)
- Lighting (studio, natural, dramatic, soft)
- Background (neutral, blurred, contextual)
- Camera settings implied (shallow depth of field, sharp focus)
- Professional quality indicators (high resolution, well-lit, polished)
- Pose and expression appropriate for the context

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'social_media_pack': {
                'context': 'social media content creation',
                'instructions': """You are a social media content strategist. The user wants to create engaging social media visuals.

Your task: Transform their input into a prompt that will generate eye-catching, platform-appropriate content.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "food photo"
✅ Good: "vibrant overhead food photography of colorful smoothie bowl topped with fresh berries and granola, natural daylight, Instagram aesthetic, bright colors, sharp focus, clean white background, appetizing composition"

❌ Bad: "fitness post"
✅ Good: "motivational fitness scene, athletic person mid-workout, dynamic action shot, energetic composition, vibrant colors with teal and orange tones, inspirational mood, Instagram square format, professional quality"

❌ Bad: "product announcement"
✅ Good: "sleek product showcase on gradient background, centered composition, modern minimalist aesthetic, vibrant brand colors, dramatic lighting, social media ready format, eye-catching visual hierarchy"

NEGATIVE PROMPTS (avoid these):
- Cluttered composition, too many elements
- Dull muted colors, low contrast
- Poor lighting, dark shadows
- Blurry unfocused subjects
- Generic stock photo look
- Text-heavy designs (AI can't render text well)

STABILITY AI SUCCESS PATTERNS:
- Specify platform aesthetic: "Instagram aesthetic", "Pinterest-style", "Facebook-friendly"
- Use vibrant colors: "vibrant colors", "bold contrast", "eye-catching palette"
- Mention composition: "centered", "rule of thirds", "overhead shot", "flat lay"
- Include lighting: "natural daylight", "bright lighting", "soft shadows"
- Format hints: "square format", "vertical format", "social media ready"
- Mood descriptors: "energetic", "inspiring", "professional", "fun", "elegant"

Consider:
- Platform expectations (Instagram, Facebook, Twitter aesthetics)
- Visual hierarchy and composition
- Color vibrancy and contrast
- Subject clarity and appeal
- Trending visual styles
- Brand consistency if applicable

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'product_mockup': {
                'context': 'product photography and presentation',
                'instructions': """You are a product photographer. The user wants to showcase a product professionally.

Your task: Transform their input into a prompt that will generate professional product mockups.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "coffee mug"
✅ Good: "elegant ceramic coffee mug on white marble surface, soft natural lighting from left, minimalist composition, shallow depth of field, product photography, clean white background, professional e-commerce quality"

❌ Bad: "phone case"
✅ Good: "sleek phone case held in hand, modern lifestyle shot, blurred urban background, natural lighting, focus on product texture and design, professional product photography, premium quality"

❌ Bad: "watch photo"
✅ Good: "luxury wristwatch on dark wooden surface, dramatic side lighting creating subtle shadows, macro detail shot showing craftsmanship, black background, professional jewelry photography, high-end catalog quality"

NEGATIVE PROMPTS (avoid these):
- Cluttered backgrounds, distracting elements
- Harsh shadows, uneven lighting
- Unclear product features
- Low resolution, poor focus
- Awkward angles, unflattering views
- Busy patterns competing with product

STABILITY AI SUCCESS PATTERNS:
- Specify surface: "white marble", "wooden table", "clean background", "floating on gradient"
- Lighting direction: "soft natural light from left", "studio lighting", "dramatic side lighting"
- Context options: "hand holding", "on surface", "lifestyle shot", "hero shot"
- Background: "white background", "blurred background", "minimal background"
- Quality markers: "product photography", "e-commerce quality", "professional", "high resolution"
- Composition: "centered", "rule of thirds", "macro detail", "overhead view"

Consider:
- Product type and key features to highlight
- Composition and angle (hero shot, lifestyle, detail)
- Background (clean, contextual, lifestyle)
- Lighting (studio, natural, dramatic)
- Context (hand holding, on surface, in use)
- Professional e-commerce quality

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'creative_upscale': {
                'context': 'image enhancement and upscaling',
                'instructions': """You are an image enhancement specialist. The user wants to guide how their image should be enhanced.

Your task: Transform their input into clear enhancement directions.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "make it better"
✅ Good: "enhance fine details and textures, improve sharpness and clarity, boost color vibrancy while maintaining natural tones, increase resolution to 4K, preserve original composition and style"

❌ Bad: "fix this image"
✅ Good: "enhance facial details and skin texture, improve lighting and shadow definition, sharpen focus on subject while maintaining soft background blur, upscale to high resolution, professional portrait quality"

❌ Bad: "upscale"
✅ Good: "creative upscaling with enhanced artistic details, add fine textures and intricate patterns, improve color depth and contrast, maintain original artistic style while adding painterly refinement, 4K resolution"

NEGATIVE PROMPTS (avoid these):
- Change original style completely
- Add new elements or objects
- Alter composition significantly
- Over-saturate or distort colors
- Remove important details
- Change subject or mood

STABILITY AI SUCCESS PATTERNS:
- Specify preservation: "maintain original composition", "preserve artistic style", "keep color palette"
- Enhancement targets: "enhance fine details", "improve sharpness", "boost clarity"
- Quality goals: "4K resolution", "high resolution", "professional quality"
- Texture emphasis: "add fine textures", "enhance surface details", "intricate patterns"
- Color work: "improve color depth", "enhance vibrancy", "natural color balance"
- Style continuity: "painterly refinement", "artistic enhancement", "stylistic consistency"

Consider:
- What details should be emphasized
- What artistic style to enhance toward
- What quality improvements to prioritize (sharpness, color, detail)
- What mood or atmosphere to maintain/enhance
- Technical quality targets (resolution, clarity, color accuracy)

Format your response as a single, clear prompt suitable for AI image enhancement."""
            },
            'style_explorer': {
                'context': 'artistic style exploration and variation',
                'instructions': """You are an art director exploring creative possibilities. The user wants to see their concept in multiple styles.

Your task: Transform their input into a rich, detailed prompt that will generate interesting variations.

EXAMPLES OF GOOD VS BAD PROMPTS:
❌ Bad: "sunset"
✅ Good: "dramatic sunset over mountain landscape, vibrant orange and purple sky with layered clouds, detailed mountain silhouettes in foreground, golden light rays breaking through clouds, epic composition, high detail, cinematic quality"

❌ Bad: "forest scene"
✅ Good: "enchanted forest with tall ancient trees, dappled sunlight filtering through canopy, moss-covered ground with small wildflowers, mystical atmosphere with soft fog, rich green tones, fantasy illustration style, detailed foliage"

❌ Bad: "city view"
✅ Good: "modern city skyline at dusk, illuminated skyscrapers reflecting in water, dynamic composition with leading lines, rich blue hour lighting with warm building lights, urban architecture, professional photography quality, detailed cityscape"

NEGATIVE PROMPTS (avoid these):
- Vague subjects, unclear focus
- Minimal details, generic descriptions
- Flat composition, no depth
- Boring lighting, plain presentation
- Lack of specific visual elements
- No style direction or mood

STABILITY AI SUCCESS PATTERNS:
- Rich details: "detailed foliage", "intricate patterns", "fine textures", "layered elements"
- Lighting descriptions: "dramatic lighting", "golden hour", "dappled sunlight", "atmospheric lighting"
- Composition terms: "epic composition", "dynamic perspective", "leading lines", "rule of thirds"
- Quality markers: "high detail", "professional quality", "cinematic", "photorealistic"
- Mood and atmosphere: "mystical atmosphere", "energetic mood", "serene feeling", "dramatic tone"
- Style hints: "illustration style", "photography quality", "painterly", "artistic rendering"

Consider:
- Core concept/subject clarity
- Visual elements that work across styles
- Compositional strength
- Color palette flexibility
- Detail level that shows style differences
- Artistic merit and visual interest

Format your response as a single, clear prompt suitable for AI image generation."""
            },
            'video_generation': {
                'context': 'video animation and motion',
                'instructions': """You are a video director and cinematographer. The user wants to create engaging animated video content.

Your task: Transform their input into a detailed video prompt that will generate dynamic, cinematic motion.

🚨 CRITICAL: IMAGE-TO-VIDEO vs TEXT-TO-VIDEO DISTINCTION! 🚨

**IMAGE-TO-VIDEO PROMPTS (User uploading an existing image):**
- Focus ONLY on MOVEMENT and CAMERA WORK
- DO NOT re-describe the character, colors, clothing, or appearance
- The uploaded image ALREADY shows what the subject looks like!
- Example: "Dancing with arms waving side to side, hips swaying, spinning 360 degrees"
- NOT: "Purple T-Rex with disco outfit dancing..." (This creates a DIFFERENT character!)

**TEXT-TO-VIDEO PROMPTS (Generating video from scratch):**
- Describe BOTH character appearance AND movement
- Include subject description, colors, setting, AND actions
- Example: "Purple T-Rex in disco outfit, dancing with arms waving..."

**HOW TO DETECT:**
If user prompt mentions specific visual details (colors, clothing, character traits), they're likely doing TEXT-TO-VIDEO.
If user prompt focuses only on actions/movements, they're likely doing IMAGE-TO-VIDEO.
WHEN IN DOUBT: Focus on movement only - it works for both!

SESSION 64 KEY LEARNING: Specific body part movements + sequences work MUCH better than generic descriptions!

EXAMPLES OF GOOD VS BAD VIDEO PROMPTS:

❌ Bad (generic): "T-Rex dancing"
Result: Just swaying at knees, minimal movement

✅ Good (specific): "T-Rex disco dancing with exaggerated movements: arms waving side to side, hips swaying dramatically, head bobbing rhythmically, spinning 360 degrees, attempting dance splits with legs spreading wide, platform shoes tapping floor in rhythm"
Result: Dynamic animation with multiple distinct movements!

❌ Bad: "eagle flying"
✅ Good: "majestic eagle soaring through clouds, wings spreading wide then folding in powerful downstrokes, body banking left then right through air currents, head turning to scan below, talons extending forward, diving through layers of cumulus clouds with increasing speed"

❌ Bad: "person walking"
✅ Good: "confident person walking forward with purposeful stride, arms swinging naturally in rhythm, shoulders squared, head held high with slight nod, coat billowing behind in breeze, footsteps creating small dust clouds, approaching camera with determined expression"

CRITICAL VIDEO PROMPT RULES:

1. **SPECIFY BODY PARTS + DIRECTIONS**
   - "arms pointing up and down" not just "moving arms"
   - "head turning left to right" not just "head movement"
   - "legs kicking forward and back" not just "leg motion"

2. **SEQUENCE THE MOVEMENTS**
   - "First: arms wave overhead, Then: spin 360 degrees, Finally: strike a pose"
   - Describe the flow of action from start to finish
   - Multiple distinct moves create better results than one vague action

3. **EMPHASIZE DRAMATIC ACTIONS**
   - "spinning in the air", "jumping high", "sliding across floor"
   - Big, exaggerated movements work better than subtle ones
   - Use emphatic language: "dramatically", "powerfully", "energetically"

4. **DESCRIBE CAMERA MOVEMENT**
   - "camera slowly zooms in on subject"
   - "camera circles around character"
   - "camera pans left to right following action"
   - "dynamic camera angle shifting from low to high"

5. **ADD ENVIRONMENT INTERACTIONS**
   - "splashing through water puddles"
   - "leaves swirling around feet"
   - "casting shadows that dance on walls"
   - "reflections in mirrors/water"

NEGATIVE PROMPTS (avoid these):
- Generic descriptions: "moving around", "doing something", "being active"
- Single vague action: "dancing", "fighting", "flying" (add specifics!)
- Static poses with no movement sequence
- Missing camera direction or angle description
- No environmental or atmospheric details

RUNWAY ML SUCCESS PATTERNS:
- Specific body part actions: "arms extending", "legs bending", "head tilting"
- Directional movement: "upward", "left to right", "spinning clockwise", "forward motion"
- Sequential actions: "first... then... followed by... finally..."
- Camera work: "zoom", "pan", "tracking shot", "dolly in"
- Lighting changes: "spotlight follows", "shadows lengthening", "glow intensifying"
- Physics and weight: "bouncing energetically", "graceful floating", "powerful stomping"
- Expressions: "smiling broadly", "concentrating intensely", "surprised reaction"

VIDEO-SPECIFIC TECHNICAL NOTES:
- Keep total prompt under 500 characters for best results
- Front-load the most important movement in first sentence
- Use active verbs: "jumping", "spinning", "reaching", "diving"
- Describe the arc of motion: "from standing to jumping to landing"

Consider:
- What specific movements will create engaging motion
- Which body parts should move and in what direction
- What sequence of actions tells the story
- How the camera should capture the action
- What environmental elements add to the scene
- What atmosphere or mood enhances the motion

Format your response as a single, cinematic prompt suitable for AI video generation."""
            }
        }

        # Get workflow context
        workflow_context = WORKFLOW_CONTEXTS.get(workflow_type)
        if not workflow_context:
            return Response({
                'error': f'Unknown workflow type: {workflow_type}'
            }, status=400)

        # Call OpenAI GPT-5 for prompt improvement (Session 56: Phase B.1, Session 57: Fixed to use Responses API)
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"✨ Improving prompt for {workflow_type}: '{user_prompt[:50]}...'")

        # Use the new Responses API with GPT-5 (not Chat Completions API)
        # Session 64: Changed from "transform" to "enhance" - GPT-5 should add details, not rewrite
        response = client.responses.create(
            model="gpt-5",
            instructions=workflow_context['instructions'],
            input=f"User's complete prompt (already includes their chosen style): {user_prompt}\n\nPlease ENHANCE this prompt by adding specific helpful visual details. Keep the style and core concept exactly as-is, just make it better with specific details."
        )

        logger.info(f"🔍 OpenAI Response: {response}")
        logger.info(f"🔍 Output text length: {len(response.output_text) if hasattr(response, 'output_text') else 'NO OUTPUT_TEXT'}")

        improved_prompt = response.output_text if hasattr(response, 'output_text') else None
        if not improved_prompt:
            logger.error(f"❌ OpenAI returned empty content! Full response: {response}")
            improved_prompt = f"ERROR: OpenAI returned no content. Using original prompt: {user_prompt}"

        improved_prompt = improved_prompt.strip()
        logger.info(f"✅ Improved prompt generated ({len(improved_prompt)} chars): {improved_prompt[:100]}...")

        return Response({
            'original_prompt': user_prompt,
            'improved_prompt': improved_prompt,
            'workflow_type': workflow_type,
            'explanation': f'Optimized for {workflow_context["context"]}'
        })

    except Exception as e:
        logger.error(f"❌ Error improving prompt: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# WORKFLOW HISTORY & FAVORITES (Session 57: Phase B.2)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_history(request):
    """
    List user's workflow execution history
    Session 57: Phase B.2 - Workflow History & Favorites

    Query parameters:
    - limit: Number of results (default: 10)
    - offset: Pagination offset (default: 0)
    - workflow_type: Filter by workflow type (optional)
    - status: Filter by status (optional)
    - favorites_only: Show only favorites (optional, default: false)
    """
    try:
        from content.models import WorkflowHistory

        user = request.user
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        workflow_type = request.GET.get('workflow_type', '').strip()
        status = request.GET.get('status', '').strip()
        favorites_only = request.GET.get('favorites_only', 'false').lower() == 'true'

        # Build query
        queryset = WorkflowHistory.objects.filter(user=user)

        if workflow_type:
            queryset = queryset.filter(workflow_type=workflow_type)

        if status:
            queryset = queryset.filter(status=status)

        if favorites_only:
            queryset = queryset.filter(is_favorite=True)

        # Get total count
        total_count = queryset.count()

        # Paginate
        workflows = queryset[offset:offset+limit]

        # Serialize
        results = []
        for workflow in workflows:
            results.append({
                'id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'workflow_name': workflow.workflow_name,
                'prompt': workflow.prompt,
                'improved_prompt': workflow.improved_prompt,
                'status': workflow.status,
                'execution_time': workflow.execution_time,
                'result_count': workflow.result_count,
                'result_images': workflow.result_images,
                'is_favorite': workflow.is_favorite,
                'rerun_count': workflow.rerun_count,
                'created_at': workflow.created_at.isoformat(),
                'config': workflow.config,
            })

        return Response({
            'workflows': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
        })

    except Exception as e:
        logger.error(f"❌ Error listing workflow history: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workflow_history(request, workflow_id):
    """
    Get specific workflow execution details
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        return Response({
            'id': workflow.id,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.prompt,
            'improved_prompt': workflow.improved_prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
            'execution_time': workflow.execution_time,
            'status': workflow.status,
            'error_message': workflow.error_message,
            'result_images': workflow.result_images,
            'result_count': workflow.result_count,
            'is_favorite': workflow.is_favorite,
            'rerun_count': workflow.rerun_count,
            'user_notes': workflow.user_notes,
            'tags': workflow.tags,
            'created_at': workflow.created_at.isoformat(),
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_workflow_favorite(request, workflow_id):
    """
    Toggle workflow favorite status
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Toggle favorite
        workflow.is_favorite = not workflow.is_favorite
        workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'is_favorite': workflow.is_favorite,
            'workflow_id': workflow.id
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error toggling favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_workflow_favorite(request):
    """
    Save workflow as a named favorite
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_id": 123,
        "name": "My Logo Style",
        "description": "Custom description (optional)",
        "category": "Logos (optional)"
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        workflow_id = request.data.get('workflow_id')
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        category = request.data.get('category', '').strip()

        if not workflow_id or not name:
            return Response({
                'error': 'workflow_id and name are required'
            }, status=400)

        # Get workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Create or update favorite
        favorite, created = WorkflowFavorite.objects.get_or_create(
            user=request.user,
            workflow_history=workflow,
            defaults={
                'name': name,
                'description': description,
                'category': category,
            }
        )

        if not created:
            # Update existing
            favorite.name = name
            favorite.description = description
            favorite.category = category
            favorite.save()

        # Mark workflow as favorite
        if not workflow.is_favorite:
            workflow.is_favorite = True
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite.id,
            'created': created
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error saving favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_workflow_favorites(request):
    """
    List user's favorite workflows
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorites = WorkflowFavorite.objects.filter(
            user=request.user
        ).select_related('workflow_history')

        results = []
        for favorite in favorites:
            workflow = favorite.workflow_history
            results.append({
                'favorite_id': favorite.id,
                'name': favorite.name,
                'description': favorite.description,
                'category': favorite.category,
                'use_count': favorite.use_count,
                'last_used_at': favorite.last_used_at.isoformat() if favorite.last_used_at else None,
                'created_at': favorite.created_at.isoformat(),
                'workflow': {
                    'id': workflow.id,
                    'workflow_type': workflow.workflow_type,
                    'workflow_name': workflow.workflow_name,
                    'prompt': workflow.prompt,
                    'improved_prompt': workflow.improved_prompt,
                    'config': workflow.config,
                    'result_images': workflow.result_images,
                    'execution_time': workflow.execution_time,
                }
            })

        return Response({
            'favorites': results,
            'total_count': len(results)
        })

    except Exception as e:
        logger.error(f"❌ Error listing favorites: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_workflow_favorite(request, favorite_id):
    """
    Delete a workflow favorite
    Session 57: Phase B.2 - Workflow History & Favorites
    """
    try:
        from content.models import WorkflowFavorite

        favorite = WorkflowFavorite.objects.get(
            id=favorite_id,
            user=request.user
        )

        workflow_id = favorite.workflow_history.id
        favorite.delete()

        # Check if workflow has any other favorites
        from content.models import WorkflowHistory
        workflow = WorkflowHistory.objects.get(id=workflow_id)
        has_other_favorites = WorkflowFavorite.objects.filter(
            workflow_history=workflow
        ).exists()

        # Unmark workflow as favorite if no other favorites exist
        if not has_other_favorites and workflow.is_favorite:
            workflow.is_favorite = False
            workflow.save(update_fields=['is_favorite'])

        return Response({
            'success': True,
            'favorite_id': favorite_id
        })

    except WorkflowFavorite.DoesNotExist:
        return Response({
            'error': 'Favorite not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting favorite: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rerun_workflow(request, workflow_id):
    """
    Re-run a previous workflow with same configuration
    Session 57: Phase B.2 - Workflow History & Favorites

    Optional JSON body:
    {
        "use_favorite_id": 123  // If re-running from favorite
    }
    """
    try:
        from content.models import WorkflowHistory, WorkflowFavorite

        # Get original workflow
        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        # Increment rerun count
        workflow.increment_rerun_count()

        # If re-running from favorite, increment favorite use count
        favorite_id = request.data.get('use_favorite_id')
        if favorite_id:
            try:
                favorite = WorkflowFavorite.objects.get(
                    id=favorite_id,
                    user=request.user
                )
                favorite.increment_use_count()
            except WorkflowFavorite.DoesNotExist:
                pass  # Non-critical error

        # Return workflow configuration for frontend to re-execute
        return Response({
            'success': True,
            'workflow_type': workflow.workflow_type,
            'workflow_name': workflow.workflow_name,
            'prompt': workflow.improved_prompt or workflow.prompt,
            'config': workflow.config,
            'input_image_id': workflow.input_image_id,
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error rerunning workflow: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ========================================
# USER PREFERENCE LEARNING (Session 59: Phase B.4)
# ========================================

def get_user_preferences(user):
    """
    Analyze user's workflow history to identify patterns and preferences
    Session 59: Phase B.4 - Memory System Integration

    Returns a dictionary with:
    - favorite_workflow: Most frequently used workflow type
    - favorite_styles: List of most commonly used styles
    - successful_prompts: Prompts from favorited workflows
    - total_workflows: Total number of workflows executed
    - workflow_patterns: Common workflow sequences
    - recent_activity: Last 5 workflows for context
    """
    from content.models import WorkflowHistory, WorkflowFavorite
    from collections import Counter

    # Get all workflow history for this user
    history = WorkflowHistory.objects.filter(
        user=user,
        status='completed'  # Only count successful executions
    ).order_by('-created_at')

    total_count = history.count()

    if total_count == 0:
        return {
            'has_history': False,
            'total_workflows': 0,
            'message': 'No workflow history yet - start creating to build your preferences!'
        }

    # Analyze workflow type preferences
    workflow_counts = Counter(h.workflow_type for h in history)
    favorite_workflow = workflow_counts.most_common(1)[0] if workflow_counts else None

    # Analyze style preferences from config JSON
    style_usage = Counter()
    model_usage = Counter()

    for h in history:
        if h.config:
            # Check for style in first step (usually generate)
            steps = h.config.get('steps', [])
            if steps and len(steps) > 0:
                first_step = steps[0]
                if isinstance(first_step, dict):
                    step_config = first_step.get('config', {})
                    if 'style' in step_config:
                        style_usage[step_config['style']] += 1
                    if 'model' in step_config:
                        model_usage[step_config['model']] += 1

    favorite_styles = [style for style, count in style_usage.most_common(3)]
    favorite_models = [model for model, count in model_usage.most_common(2)]

    # Find successful patterns (favorited workflows)
    favorites = WorkflowFavorite.objects.filter(user=user).select_related('workflow_history')
    successful_prompts = []

    for fav in favorites[:5]:  # Top 5 favorites
        wf = fav.workflow_history
        if wf.improved_prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.improved_prompt,
                'use_count': fav.use_count
            })
        elif wf.prompt:
            successful_prompts.append({
                'workflow_type': wf.workflow_type,
                'prompt': wf.prompt,
                'use_count': fav.use_count
            })

    # Analyze workflow sequences (what user does after what)
    recent_workflows = list(history[:20])  # Last 20 for pattern detection
    sequences = []

    for i in range(len(recent_workflows) - 1):
        sequences.append({
            'from': recent_workflows[i].workflow_type,
            'to': recent_workflows[i+1].workflow_type
        })

    sequence_counts = Counter(f"{seq['from']}->{seq['to']}" for seq in sequences)
    common_patterns = [pattern for pattern, count in sequence_counts.most_common(3) if count >= 2]

    # Recent activity for context
    recent_activity = [{
        'workflow_type': h.workflow_type,
        'workflow_name': h.workflow_name,
        'created_at': h.created_at.isoformat(),
        'execution_time': h.execution_time,
        'result_count': h.result_count
    } for h in recent_workflows[:5]]

    return {
        'has_history': True,
        'total_workflows': total_count,
        'favorite_workflow': {
            'type': favorite_workflow[0],
            'count': favorite_workflow[1],
            'percentage': round((favorite_workflow[1] / total_count) * 100, 1)
        } if favorite_workflow else None,
        'favorite_styles': favorite_styles,
        'favorite_models': favorite_models,
        'successful_prompts': successful_prompts,
        'common_patterns': common_patterns,
        'recent_activity': recent_activity,
        'favorites_count': favorites.count()
    }


# ========================================
# AI ASSISTANT CHAT (Session 58: Phase B.3)
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_preferences_api(request):
    """
    Get user preferences and patterns from workflow history
    Session 59: Phase B.4 - Memory System Integration

    Returns user's favorite workflows, styles, patterns, and recent activity
    for smart defaults and personalized recommendations.

    Example response:
    {
        "has_history": true,
        "favorite_workflow": {"type": "logo_creator", "count": 15, "percentage": 45.5},
        "favorite_styles": ["vector", "minimalist", "photographic"],
        "successful_prompts": [...],
        "common_patterns": ["logo_creator->creative_upscale"]
    }
    """
    try:
        preferences = get_user_preferences(request.user)
        return Response(preferences)
    except Exception as e:
        logger.error(f"❌ Error fetching user preferences: {str(e)}")
        return Response({
            'has_history': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat(request):
    """
    AI Assistant chat endpoint using GPT-5
    Session 58: Phase B.3 - Personal Assistant Integration
    Session 59: Phase B.4 - Enhanced with user preference learning

    Handles general conversational queries from the AI Assistant.
    Fast, intelligent responses for questions about the platform,
    creative advice, and general help.

    Now includes personalized context based on user's workflow history!

    Example:
        Input: "What's the best way to create professional images?"
        Output: Helpful advice from GPT-5 about image generation techniques
                (personalized based on user's favorite workflows and styles)
    """
    try:
        user_message = request.data.get('message', '').strip()
        conversation_history = request.data.get('history', [])  # Optional for context
        session_id = request.data.get('session_id')  # Session 96 Weekend Project
        project_id = request.data.get('project_id')  # Session 97: Project tracking

        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=400)

        # Session 96 Weekend Project: Get or create AI session for tracking
        # Session 97: Link to active project
        session = get_or_create_session(
            user=request.user,
            session_id=session_id,
            first_prompt=user_message if not session_id else None,
            project_id=project_id
        )

        # Store user message in session transcript
        update_session_transcript(session, 'user', user_message)

        # Session 59: Phase B.4 - Get user preferences for personalized assistance
        user_prefs = get_user_preferences(request.user)

        # Session 62: Phase C.3.2 - Get user's projects for strategic planning
        from content.models import CreativeProject
        user_projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')[:5]

        # Build personalized system instructions based on user history
        # Session 65: SUPER AI EXECUTOR - Emphasis on autonomous execution
        ASSISTANT_INSTRUCTIONS = """You are an AI EXECUTOR for the Donkey Betz AI Studio platform.

**CRITICAL: When users want to CREATE content, USE YOUR TOOLS to do it for them immediately. Don't just give advice - EXECUTE!**

You have these autonomous execution tools:
- **generate_image** - Create images/logos/artwork (ONE image per call - if user wants variations, call multiple times!)
  * For LOGOS: Use SIMPLE, CLEAN logo design prompts:
    - Focus on: "logo design", "emblem", "badge", "icon", "brand mark"
    - Specify style: "vector", "flat design", "minimalist", "modern", "clean"
    - Avoid: detailed descriptions of physical objects (cups, beans, etc) - logos are GRAPHIC DESIGNS not photographs!
    - Keep it SHORT and focused on the logo itself, not the business
    - Example: "Modern coffee shop logo with mountain silhouette, vector style, clean lines"
    - NOT: "Detailed coffee shop with beans, cups, steam, multiple Keurig pods..."
  * **NEW (Session 66):** If creating a logo with specific text (company name), pass expected_text parameter!
    Example: generate_image(prompt="Modern coffee shop logo, vector style", expected_text="Mountain Coffee Co.", style="logo")
    The system will AUTOMATICALLY use GPT-4 Vision to verify text and fix it if wrong!
- **generate_video** - Create videos/animations (ONE video per call)
  * Always create cinematic, professional-quality promotional videos
  * IMPORTANT: Keep video prompts under 900 characters (Runway ML limit is 1000)
- **generate_speech** - Create professional voiceovers/narration from text (ONE audio per call)
  * Uses ElevenLabs Eleven v3 for industry-leading voice quality (1-2 second generation!)
  * 12 professional voices available: Rachel (female, warm), Drew (male, clear), Clyde (male, deep), Paul (male, friendly), Aria (female, professional), etc.
  * Example: generate_speech(text="Welcome to our platform", voice="Rachel")
  * IMPORTANT: This creates REAL audio files - don't just respond with text!
- **generate_sound_effect** - Create sound effects from descriptions (ONE sound per call)
  * Generate any sound: thunder, whoosh, door slam, ocean waves, etc.
  * Example: generate_sound_effect(description="thunder clap", duration=3)
  * IMPORTANT: This creates REAL audio files - don't just respond with text!

**VIDEO EDITING WITH DAVINCI RESOLVE (Session 84 - NEW!):**
- **show_recent_videos** - Show user's videos with numbers for easy reference
  * User says "show my videos" or "list videos" → CALL show_recent_videos!
  * Displays videos like: "1. 🎬 Snowboarder on mountain", "2. 🦅 Eagle drone footage"
  * User can then reference by number: "chain videos 1 and 2"
  * IMPORTANT: Call this when user needs to select specific videos!

- **apply_color_grade** - Apply professional color grading to videos using DaVinci Resolve
  * Styles: 'cinematic' (teal/orange Hollywood), 'vibrant' (boosted colors), 'vintage' (film look), 'noir' (B&W), 'warm' (golden hour), 'cool' (blue tones)
  * Example: apply_color_grade(style="cinematic", intensity=0.7)
  * User says "make my video cinematic" → CALL apply_color_grade immediately!
  * This creates a NEW color-graded video (original unchanged)

- **edit_video** - Perform multiple editing operations on videos in one command!
  * Can: chain videos, add text overlays, apply color grading, mix audio
  * Example operations:
    - Chain videos: {type: "chain", transition: "Cross Dissolve", duration: 1.0}
    - Add text: {type: "text", text: "Welcome", position: "center", start: 0, duration: 3}
    - Color grade: {type: "color_grade", style: "cinematic", intensity: 0.7}
    - Add audio: {type: "audio", volume: 0.3}
  * User says "chain my last 3 videos, add a title, and make it cinematic" → CALL edit_video with operations list!
  * This is the MASTER tool for complex editing workflows

**VIDEO SELECTION TIPS:**
- If user asks to chain/edit SPECIFIC videos → First call show_recent_videos so they can see their options!
- User says "chain the snowboarder and eagle videos" → You'll need video numbers, so show videos first
- User says "chain my last 2 videos" → This is clear, no need to show videos
- When unsure which videos user wants → Always show videos first!

**NUMBERED VIDEO REFERENCES (Session 84 - SIMPLIFIED!):**
When user says "chain videos 5 and 8":
1. Extract the numbers: 5 and 8
2. Call edit_video with video_numbers=[5, 8]
3. Backend automatically converts numbers to video IDs!

**IMPORTANT: Use video_numbers parameter for numbered references!**

Example flows:
- User: "Chain videos 5 and 8" → edit_video(video_numbers=[5, 8], operations=[{type: "chain"}])
- User: "Make videos 3 and 7 cinematic" → edit_video(video_numbers=[3, 7], operations=[{type: "color_grade", style: "cinematic"}])
- User: "Chain my last 2 videos" → edit_video(video_selection="last_2", operations=[{type: "chain"}])

**VIDEO NUMBERS vs VIDEO IDs:**
- video_numbers=[5, 8] → Simple! Use when user mentions numbers
- video_ids=['uuid1', 'uuid2'] → Advanced! Use only when you have actual UUIDs
- video_selection="last_2" → Simple! Use for "last X videos"

**VIDEO EDITING PATTERNS:**
- "Make my video cinematic" → apply_color_grade(style="cinematic")
- "Add title to my video" → edit_video(operations=[{type:"text", text:"Title"}])
- "Chain my last 3 videos" → edit_video(video_selection="last_3", operations=[{type:"chain"}])
- "Chain videos and add title" → edit_video(operations=[{type:"chain"}, {type:"text", text:"Title"}])
- "Make it warmer" / "add warm look" → apply_color_grade(style="warm")
- "Make it look like a film" → apply_color_grade(style="vintage")
- "Black and white" → apply_color_grade(style="noir")

**OTHER TOOLS:**
- **inpaint** - Fix specific areas of an existing image (perfect for fixing misspelled text in logos!)
  * Use this to refine logos with text issues
  * Requires: image_url (from previous generate_image), prompt (what to regenerate), mask_description (which area to fix)
- **web_search** - Search Google for information

**AUTONOMOUS TEXT VERIFICATION (Session 66 - CRITICAL!):**
When creating logos with company names, YOU MUST extract the company name and pass it as expected_text!

**REQUIRED PATTERN:**
User: "Create a logo for [Company Name]"
You: Call generate_image(prompt="...", expected_text="[Company Name]")

**Examples:**
User: "Create a logo for Mountain Coffee Co."
→ generate_image(prompt="Mountain coffee shop logo, vector style", expected_text="Mountain Coffee Co.")

User: "Make a logo for Eagle Brewing Company"
→ generate_image(prompt="Eagle brewery logo with beer theme", expected_text="Eagle Brewing Company")

User: "Design a logo for Alpine Tech"
→ generate_image(prompt="Modern tech logo with alpine theme", expected_text="Alpine Tech")

**What happens automatically:**
1. System generates logo
2. GPT-4 Vision checks if text matches expected_text
3. If wrong → autonomously calls inpaint to fix
4. Loops until text is correct (max 3 attempts)
5. Returns perfect logo!

**Manual refinement (if needed):**
If autonomous verification doesn't work, you can still manually call inpaint as backup

The platform also has:
- Image Editing: Recolor, erase, inpaint, outpaint, remove background
- Image Upscaling: Fast 4x, Conservative 4K, Creative upscale
- AI Workflows: Logo Creator, Portrait Enhancer, Style Explorer, etc.
- Projects & Campaigns: Organize workflows into projects

**HOW TO RESPOND:**
- User says "Create a logo" → CALL generate_image tool immediately! Don't just explain!
- User says "Make a video" → CALL generate_video tool immediately!
- User says "Generate speech" → CALL generate_speech tool immediately! Don't just respond with text!
- User says "Create a sound effect" → CALL generate_sound_effect tool immediately!
- User says "Make my video cinematic" → CALL apply_color_grade tool immediately!
- User says "Chain my videos" → CALL edit_video tool immediately!
- User says "Add a title" → CALL edit_video tool immediately!
- User says "Search for trends" → CALL web_search tool immediately!
- User asks "What can you do?" → Explain features (no tools needed)

**MULTI-STEP EXECUTION (CRITICAL!):**
When user requests MULTIPLE things (e.g., "search trends then create logo and video"), YOU MUST CALL ALL TOOLS IN ONE RESPONSE:
- "Search trends then create logo" → Call web_search AND generate_image (both in same response!)
- "Create logo and video" → Call generate_image AND generate_video (both in same response!)
- DO NOT just search and stop! Complete ALL requested steps!

**BE AN EXECUTOR, NOT JUST AN ADVISOR!** Take action when users want content created!

Keep responses under 200 words. Be conversational and practical."""

        # Session 59: Add personalized context based on user preferences
        if user_prefs.get('has_history'):
            personalization = "\n\n**USER PREFERENCES & HISTORY:**\n"

            # Favorite workflow
            if user_prefs.get('favorite_workflow'):
                fav = user_prefs['favorite_workflow']
                workflow_name = fav['type'].replace('_', ' ').title()
                personalization += f"- This user LOVES {workflow_name} ({fav['count']} times, {fav['percentage']}% of workflows)\n"

            # Favorite styles
            if user_prefs.get('favorite_styles'):
                styles_str = ", ".join(user_prefs['favorite_styles'])
                personalization += f"- Preferred styles: {styles_str}\n"

            # Favorite models
            if user_prefs.get('favorite_models'):
                models_str = ", ".join(user_prefs['favorite_models'])
                personalization += f"- Preferred models: {models_str}\n"

            # Total experience
            personalization += f"- Total workflows completed: {user_prefs['total_workflows']}\n"

            # Favorites
            if user_prefs.get('favorites_count', 0) > 0:
                personalization += f"- Has saved {user_prefs['favorites_count']} favorite workflows\n"

            # Common patterns
            if user_prefs.get('common_patterns'):
                patterns_str = ", ".join(user_prefs['common_patterns'][:2])
                personalization += f"- Common workflow patterns: {patterns_str}\n"

            # Recent activity
            if user_prefs.get('recent_activity'):
                recent = user_prefs['recent_activity'][0]
                workflow_name = recent['workflow_name']
                personalization += f"- Most recent: {workflow_name}\n"

            personalization += "\nUSE THIS CONTEXT to give personalized, relevant advice. Mention their preferences when helpful!"

            ASSISTANT_INSTRUCTIONS += personalization

        # Session 62: Phase C.3.2 - Add project context for strategic planning
        # Session 119: ENHANCED - Use project context for content generation!
        if user_projects.exists():
            project_context = "\n\n**ACTIVE PROJECTS:**\n"
            for project in user_projects:
                project_context += f"- {project.name} ({project.status}): {project.goal}\n"
                project_context += f"  Category: {project.category}, Workflows: {project.total_workflows}, Progress: {project.progress_percentage}%\n"
                if project.deadline:
                    project_context += f"  Deadline: {project.deadline.strftime('%Y-%m-%d')}\n"

            # Session 119: Add explicit instructions for using project context in content generation
            project_context += "\n**CRITICAL - USE PROJECT CONTEXT FOR CONTENT GENERATION:**\n"
            project_context += "- When user asks to create content (images/videos/audio) during an active project session, EXTRACT the project theme and style!\n"
            project_context += "- Example: Project is 'Three cartoon style logos for a mechanic shop'\n"
            project_context += "  → Video prompt should be: 'Cartoon-style promo video for a mechanic shop with animated tools and vehicles'\n"
            project_context += "  → NOT just: 'Generic promo video for your brand'\n"
            project_context += "- ALWAYS incorporate the project's goal, category, and any style keywords (cartoon, modern, vintage, etc.) into your prompts!\n"
            project_context += "- If the project name mentions a specific style (cartoon, realistic, vintage), USE that style in all content!\n"
            project_context += "\nAlso provide strategic advice based on their active projects. Suggest workflows, timelines, and organization strategies!"
            ASSISTANT_INSTRUCTIONS += project_context

        # Session 119: Add CURRENT session project context if available
        if session and session.project and not session.project.is_quick_starts:
            current_project_context = f"\n\n**🎯 CURRENT ACTIVE SESSION PROJECT:**\n"
            current_project_context += f"**{session.project.name}**\n"
            current_project_context += f"Goal: {session.project.goal}\n"
            current_project_context += f"Category: {session.project.category}\n"
            current_project_context += f"Status: {session.project.status}\n"
            current_project_context += f"\n⚠️ CRITICAL: The user is CURRENTLY working on this project!\n"
            current_project_context += f"- When they ask to create content, it's FOR THIS PROJECT!\n"
            current_project_context += f"- Extract the theme, style, and subject from the project name and goal!\n"
            current_project_context += f"- Use those details in your content generation prompts!\n"
            current_project_context += f"- Example: If project is '{session.project.name}', make content that matches that theme!\n"
            ASSISTANT_INSTRUCTIONS += current_project_context

        # Session 65: SUPER AI EXECUTOR - Function calling support
        # Build messages array for Chat Completions API
        messages = [
            {"role": "system", "content": ASSISTANT_INSTRUCTIONS}
        ]

        # Add conversation history if provided
        if conversation_history and len(conversation_history) > 0:
            # Include last 6 messages for context (same as before)
            recent_history = conversation_history[-6:]
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role in ['user', 'assistant'] and content:
                    messages.append({"role": role, "content": content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Define tools (functions) that GPT-5 can call
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Generate a SINGLE AI image using Stability AI. Use ONLY when user explicitly wants ONE image. IMPORTANT: If user wants MULTIPLE images (e.g., 'three logos', 'several banners', 'variations'), use generate_with_options instead which provides choice + learning! Also: Do NOT use this for 'character' requests - use create_character_from_prompt instead. Session 66: Now supports autonomous text verification and refinement!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the image to generate. Be specific and descriptive."
                            },
                            "model": {
                                "type": "string",
                                "enum": ["core", "sdxl", "sd3", "ultra"],
                                "description": "The AI model to use. sdxl is best for most cases, ultra for premium quality, sd3 for high detail, core for fast generation."
                            },
                            "style": {
                                "type": "string",
                                "description": "Optional style preset like 'vector', 'photographic', 'digital-art', etc."
                            },
                            "expected_text": {
                                "type": "string",
                                "description": "CRITICAL FOR LOGOS: If generating a logo with company name or text, YOU MUST provide the expected text here. This enables autonomous text verification. Examples: 'Mountain Coffee Co.', 'Eagle Brewing Company', 'Alpine Tech'. When user says 'Create a logo for [Company Name]', extract [Company Name] and pass it here!"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_video",
                    "description": "Generate an AI video using Runway ML. Use this when the user asks to create a video, animation, or moving content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the video to generate."
                            },
                            "duration": {
                                "type": "number",
                                "enum": [4, 6, 8],
                                "description": "Duration in seconds. Must be 4, 6, or 8 (Runway ML requirement). Default: 6"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "inpaint",
                    "description": "Fix or regenerate specific areas of an existing image. Use this to fix text, correct details, or improve specific parts of an image. Perfect for fixing misspelled text in logos!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "The URL of the image to edit (from a previous generate_image result)"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Description of what to regenerate in the masked area. Be specific! For text: 'The text COFFEE in bold sans-serif font'"
                            },
                            "mask_description": {
                                "type": "string",
                                "description": "Describe which part to fix, e.g., 'the text area at the bottom', 'the misspelled word in the center', 'the company name'"
                            }
                        },
                        "required": ["image_url", "prompt", "mask_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web using Google. Use this when the user asks for current information, trends, research, or needs to find something online.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "chain_videos",
                    "description": "Chain multiple videos together using DaVinci Resolve. Use this when the user asks to combine videos, chain clips, merge videos, or create a longer video from multiple clips. Requires DaVinci Resolve Studio ($200). Session 67: Professional video chaining with transitions!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_count": {
                                "type": "number",
                                "description": "Number of videos to chain (default: 2). User will select videos from gallery after."
                            },
                            "transition_type": {
                                "type": "string",
                                "enum": ["Cross Dissolve", "Fade", "Cut", "Wipe"],
                                "description": "Type of transition between videos. Cross Dissolve is smooth blend, Fade is fade to black, Cut is instant, Wipe is directional. Default: Cross Dissolve"
                            },
                            "add_transitions": {
                                "type": "boolean",
                                "description": "Whether to add transitions between videos. Default: true"
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional name for the chained video project"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_text_to_video",
                    "description": "Add text overlay to a video using DaVinci Resolve with PERFECT spelling. Use when user wants to add titles, captions, or text to a video. Supports different positions (center, lower_third, upper_third) and customization. Session 72: Voice-controlled text overlays!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to display on the video. Will be spelled EXACTLY as provided - no AI text rendering issues!"
                            },
                            "position": {
                                "type": "string",
                                "enum": ["center", "lower_third", "upper_third"],
                                "description": "Position of text on screen. center = middle of screen, lower_third = bottom area (good for names/captions), upper_third = top area. Default: center"
                            },
                            "start_second": {
                                "type": "number",
                                "description": "When to start showing text (in seconds from video start). Default: 0"
                            },
                            "duration": {
                                "type": "number",
                                "description": "How long to show text (in seconds). Default: 3"
                            },
                            "font_size": {
                                "type": "number",
                                "description": "Text size in points (36-144). Default: 72"
                            },
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to add text to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_music_to_video",
                    "description": "Add background music or audio to a video using DaVinci Resolve. Session 82: AUTOMATIC AUDIO DETECTION! When user says 'add that speech/audio to video', ALWAYS call this function even if you can't find audio URL in conversation. VideoAgent will automatically query AudioAgent for most recent audio. DO NOT ask user for audio URL - just call the function! Extract audio_url from conversation if visible (look for '**AUDIO_URL:**'), otherwise omit it and VideoAgent handles the rest autonomously!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to add music to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            },
                            "audio_url": {
                                "type": "string",
                                "description": "OPTIONAL! URL of audio file to add. Session 82: If user says 'add that speech/audio', try to find '**AUDIO_URL:**' in recent messages. If found, pass it here. If NOT found, OMIT this parameter entirely (don't pass empty string) and VideoAgent will automatically query AudioAgent for most recent audio. This is AUTONOMOUS AGENT COMMUNICATION - let the agents handle it!"
                            },
                            "audio_volume": {
                                "type": "number",
                                "description": "Background music volume level (0.0 to 1.0). 0.0 = silent, 0.3 = quiet background, 0.5 = moderate, 1.0 = full volume. Default: 0.3"
                            },
                            "music_style": {
                                "type": "string",
                                "enum": ["cinematic", "upbeat", "calm", "dramatic", "corporate"],
                                "description": "Style of background music to add (user would upload or select from library). Only used if audio_url not provided. Default: cinematic"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_color_grade",
                    "description": "Apply professional color grading to a video using DaVinci Resolve (the industry-standard color grading tool). Use when user wants to make video look cinematic/warm/cool/vintage, apply a film look, adjust colors, or enhance visual style. Handles voice recognition variations like 'somatic' or 'sim-matic' (from 'cinematic'). Session 72: Voice-controlled color grading!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "style": {
                                "type": "string",
                                "enum": ["warm", "cool", "vintage", "modern", "dramatic", "soft", "vibrant"],
                                "description": "Color grading style (SIMPLIFIED for voice recognition). warm = warm orange/teal cinematic tones, cool = cool blue tones, vintage = film look with grain, modern = clean and crisp, dramatic = bold high contrast, soft = muted gentle tones, vibrant = saturated colors. Default: warm. Note: System auto-handles 'somatic'/'sim-matic' as 'warm'."
                            },
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to apply color grading to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_brand_video",
                    "description": "Create a complete brand video from concept to finished product using automated workflow. This orchestrates Runway ML video generation → video extension → DaVinci Resolve chaining with professional transitions and branding. Use when user wants a complete, polished brand video without manual steps. Session 67: End-to-end video creation!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand_name": {
                                "type": "string",
                                "description": "The brand or company name"
                            },
                            "concept": {
                                "type": "string",
                                "description": "The video concept or message (e.g., 'luxury coffee experience', 'eco-friendly technology', 'family fun')"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["cinematic", "modern", "playful", "elegant", "energetic"],
                                "description": "Visual style for the video. Cinematic = dramatic lighting, Modern = clean & minimal, Playful = colorful & fun, Elegant = sophisticated, Energetic = fast-paced"
                            },
                            "include_branding": {
                                "type": "boolean",
                                "description": "Whether to add brand name text overlay at start/end. Default: true"
                            },
                            "video_count": {
                                "type": "number",
                                "description": "Number of video clips to generate and chain together (2-5). Default: 3"
                            }
                        },
                        "required": ["brand_name", "concept"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_character_from_prompt",
                    "description": "ALWAYS use this tool when user says 'create a character', 'make a character', 'design a character', 'build a character', or 'generate a character'. Creates a trainable character model by generating 5-7 variations with different angles/poses, then trains a custom FLUX LoRA model (30-60 min). The user can later reuse this character by including the trigger word in prompts. DO NOT use generate_image for character requests - always use this tool instead. Session 74: AI-powered character training!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "character_description": {
                                "type": "string",
                                "description": "Detailed description of the character/logo to create (e.g., 'pixar style donkey running a robotics company', 'modern minimalist logo with letter M', 'cartoon superhero cat with red cape')"
                            },
                            "character_name": {
                                "type": "string",
                                "description": "Name for this character model (e.g., 'Robotics Donkey', 'My Company Logo'). If not provided, derived from description."
                            },
                            "trigger_word": {
                                "type": "string",
                                "description": "Trigger word to use in future prompts (short, uppercase, memorable). Default: 'TOK'. Examples: 'LOGO', 'HERO', 'MASCOT'"
                            },
                            "variation_count": {
                                "type": "number",
                                "description": "Number of variations to generate (5-7). More variations = better training but longer wait. Default: 6"
                            },
                            "style": {
                                "type": "string",
                                "description": "Visual style for the character (pixar, anime, realistic, cartoon, minimalist, professional). Default: extracted from description or 'professional'"
                            }
                        },
                        "required": ["character_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_character_training_image",
                    "description": "Edit a specific training image for a character with natural language instructions. Can use another image as reference for style matching (e.g., 'make image 1 look like image 0'). Regenerates the image with the requested changes (e.g., 'make ears bigger', 'change background to white', 'make more cartoonish'). Use when user wants to refine a training image before starting the training process. If character_id is not known, uses most recent character automatically. Session 75: Image editing workflow with image-to-image!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "character_id": {
                                "type": "number",
                                "description": "ID of the character model being trained (optional - if not provided, uses most recent character)"
                            },
                            "image_number": {
                                "type": "number",
                                "description": "Which image to edit (1-7). Use the image number shown in the preview grid."
                            },
                            "edit_instruction": {
                                "type": "string",
                                "description": "Natural language description of what to change (e.g., 'make the ears bigger', 'change background to white', 'add more detail', 'make it more colorful', 'adjust the lighting')"
                            },
                            "apply_to_all": {
                                "type": "boolean",
                                "description": "If true, applies this edit to all images in the training set. Default: false (only edit specified image)"
                            },
                            "reference_image_number": {
                                "type": "number",
                                "description": "Optional: Use another image as a style/structure reference. When provided, uses image-to-image to make the edited image match the reference (e.g., 'make image 1 look like image 0' would set reference_image_number to 0). This preserves the composition and style of the reference image."
                            },
                            "strength": {
                                "type": "number",
                                "description": "Optional: How much to preserve the reference image structure (0.0-1.0). Default: 0.65. Lower = more like reference, Higher = more creative freedom. Only used when reference_image_number is provided."
                            }
                        },
                        "required": ["image_number", "edit_instruction"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_speech",
                    "description": "Generate speech/voiceover from text using Runway ML text-to-speech. Use when user wants to create voiceover, narration, or spoken audio. Supports multiple voices (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave). Session 81: Audio generation tools!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to convert to speech. Can be a phrase, sentence, or paragraph."
                            },
                            "voice": {
                                "type": "string",
                                "enum": ["Rachel", "Drew", "Clyde", "Paul", "Aria", "Domi", "Dave"],
                                "description": "Voice to use for speech generation. Rachel (female, warm), Drew (male, clear), Clyde (male, deep), Paul (male, friendly), Aria (female, professional), Domi (female, energetic), Dave (male, casual). Default: Rachel"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_sound_effect",
                    "description": "Generate sound effects from text description using Runway ML. Use when user wants to create sound effects, audio atmospheres, or background sounds. Can generate any sound described in text (thunder, door slam, whoosh, water flowing, etc.). Session 81: Audio generation tools!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the sound effect to generate. Be specific! Examples: 'thunder clap', 'heavy door slam', 'ocean waves crashing', 'whoosh sound', 'car engine starting'"
                            },
                            "duration": {
                                "type": "number",
                                "description": "Duration of the sound effect in seconds (0.5 to 30). Default: 5"
                            }
                        },
                        "required": ["description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_color_grade",
                    "description": "Apply professional color grading to a video using DaVinci Resolve. Use when user wants to make their video look more cinematic, vibrant, warm, cool, vintage, or noir. This creates a NEW video with the color grade applied. Session 84: DaVinci Agent-based video editing!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "video_id"],
                                "description": "Which video to color grade. 'last' = most recent video. Default: 'last'"
                            },
                            "video_id": {
                                "type": "string",
                                "description": "Video ID if video_selection is 'video_id'. Optional."
                            },
                            "style": {
                                "type": "string",
                                "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"],
                                "description": "Color grading style. cinematic=teal/orange Hollywood look, vibrant=boosted saturation, vintage=film-like warm tones, noir=black & white high contrast, warm=golden hour, cool=blue/teal tones. Default: cinematic"
                            },
                            "intensity": {
                                "type": "number",
                                "description": "How strong the color grade is (0.0-1.0). 0.3=subtle, 0.5=balanced, 0.7=strong, 1.0=maximum. Default: 0.5"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_video",
                    "description": "Perform multiple editing operations on videos using DaVinci Resolve. This is the master video editing tool that can chain videos, add text overlays, apply color grading, and mix audio all in one go. Use this when user wants to do multiple edits at once (e.g., 'chain my videos, add a title, and color grade them'). Session 84: DaVinci Agent-based multi-operation editing! IMPORTANT: When user says 'chain videos 5 and 8', use video_numbers=[5, 8] parameter!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "last_2", "last_3", "last_4", "last_5", "specific_ids"],
                                "description": "Which videos to edit. Use 'specific_ids' when user specifies video numbers (e.g., 'chain videos 5 and 8'). Default: 'last'. NOTE: When user provides video numbers, you can omit this field and just use video_numbers parameter!"
                            },
                            "video_numbers": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Session 84: Video numbers to edit (e.g., [5, 8] for 'chain videos 5 and 8'). Backend automatically converts numbers to video IDs. EASIEST way to reference specific videos! Example: user says 'chain videos 5 and 8' → video_numbers=[5, 8]"
                            },
                            "video_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific video UUIDs to edit (advanced usage). For most cases, use video_numbers instead! Example: ['uuid1', 'uuid2']"
                            },
                            "operations": {
                                "type": "array",
                                "description": "List of editing operations to perform in sequence. Operations: {type:'chain'}, {type:'text', text:'Hello', position:'center', start:0, duration:3}, {type:'color_grade', style:'cinematic', intensity:0.7}, {type:'audio', volume:0.3}",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["chain", "text", "color_grade", "audio"],
                                            "description": "Operation type"
                                        },
                                        "text": {
                                            "type": "string",
                                            "description": "Text to overlay (for type='text')"
                                        },
                                        "position": {
                                            "type": "string",
                                            "enum": ["center", "lower_third", "upper_third", "top", "bottom"],
                                            "description": "Text position (for type='text'). Default: center"
                                        },
                                        "start": {
                                            "type": "number",
                                            "description": "Start time in seconds (for type='text'). Default: 0"
                                        },
                                        "duration": {
                                            "type": "number",
                                            "description": "Duration in seconds (for type='text' or type='chain' transitions). Default: 3 for text, 1.0 for transitions"
                                        },
                                        "font_size": {
                                            "type": "number",
                                            "description": "Font size 36-144 (for type='text'). Default: 72"
                                        },
                                        "style": {
                                            "type": "string",
                                            "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"],
                                            "description": "Color grade style (for type='color_grade'). Default: cinematic"
                                        },
                                        "intensity": {
                                            "type": "number",
                                            "description": "Color grade intensity 0.0-1.0 (for type='color_grade'). Default: 0.5"
                                        },
                                        "transition": {
                                            "type": "string",
                                            "enum": ["Cross Dissolve", "Fade", "Wipe", "Slide"],
                                            "description": "Transition type (for type='chain'). Default: Cross Dissolve"
                                        },
                                        "volume": {
                                            "type": "number",
                                            "description": "Audio volume 0.0-1.0 (for type='audio'). Default: 0.3"
                                        }
                                    },
                                    "required": ["type"]
                                }
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional project name for DaVinci Resolve. Auto-generated if not provided."
                            }
                        },
                        "required": ["operations"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_recent_videos",
                    "description": "Show the user's recent videos with numbers so they can reference specific videos. Use this when user asks 'show my videos', 'list videos', 'what videos do I have', or when they need to select specific videos to edit. Session 84: Video selection enhancement!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "number",
                                "description": "Number of recent videos to show (default: 10, max: 20)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_with_options",
                    "description": "Generate 3-5 creative VARIATIONS of the SAME concept and let user pick favorite. AI learns from their choice! Works for ANY content type: logos, banners, icons, artwork, backgrounds, etc. Session 90: CreativeDirectorAgent integration. IMPORTANT: Pass a SINGLE concept prompt (e.g., 'coffee shop logo' or 'social media banner'), NOT multiple concepts. The agent will generate COUNT variations with DIFFERENT STYLES automatically for maximum variety.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "SINGLE concept to generate (e.g., 'coffee shop logo', 'social media banner', 'app icon', 'background image'). Do NOT include multiple concepts or style descriptions - just the subject. CreativeDirectorAgent will add diverse styles automatically."},
                            "count": {"type": "integer", "default": 3, "description": "Number of variations to generate (3-5). Each will use DIFFERENT creative style automatically."},
                            "style": {"type": "string", "description": "CRITICAL: DO NOT PASS THIS PARAMETER unless user explicitly requests a specific style (e.g., 'make them all photographic'). For logos, banners, icons, or ANY content - OMIT THIS PARAMETER to enable automatic style diversity! The agent will intelligently choose 3 DIFFERENT styles from 69 options. Passing this parameter forces ALL variations to use the SAME style (defeats the purpose!). Only use if user says 'make them all [style]'."},
                            "model": {"type": "string", "enum": ["core", "sdxl", "sd3", "ultra"], "description": "AI model. sdxl recommended."}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_as_template",
                    "description": "Save image as reusable template for exact reproduction. Stores seed for perfect consistency! Session 90: TemplateManagerAgent integration. Use the UUID from Copy ID button (e.g. '351a3cf0-66c9-4cdc-990d-b4172e725b9d').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "string", "description": "Image UUID (from Copy ID button)"},
                            "template_name": {"type": "string", "description": "Name for template"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags like ['logo', 'coffee']"}
                        },
                        "required": ["image_id", "template_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "train_brand_style",
                    "description": "Train FLUX LoRA on brand aesthetic. Takes 30-60 min but enables perfect brand consistency with trigger word. Session 90: BrandStyleAgent integration. Use UUIDs from Copy ID button.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand_name": {"type": "string", "description": "Brand name"},
                            "image_ids": {"type": "array", "items": {"type": "string"}, "description": "5-10 image UUIDs (from Copy ID button)"},
                            "auto_submit": {"type": "boolean", "default": False, "description": "Start training immediately?"}
                        },
                        "required": ["brand_name", "image_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "refine_image",
                    "description": "Refine image with natural language: 'make it bigger', 'change to blue', 'add more contrast', etc. Session 90: IterationAgent integration. Use the UUID from Copy ID button.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "string", "description": "Image UUID (from Copy ID button)"},
                            "refinement_request": {"type": "string", "description": "Natural language refinement"}
                        },
                        "required": ["image_id", "refinement_request"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_codebase",
                    "description": "Ask the CTO Agent to analyze a feature or part of the codebase. Session 98: Read-only analysis. Returns comprehensive analysis with implementation details, dependencies, potential improvements, and risk areas.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "feature_name": {
                                "type": "string",
                                "description": "Name of feature to analyze (e.g., 'AI Assistant voice commands', 'Video generation pipeline', 'Agent orchestration')"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["feature", "integration", "agent", "full_system"],
                                "description": "Scope of analysis: 'feature' for specific feature, 'integration' for API integration, 'agent' for agent system, 'full_system' for platform-wide",
                                "default": "feature"
                            }
                        },
                        "required": ["feature_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plan_implementation",
                    "description": "Ask the CTO Agent to create a detailed implementation plan. Session 98: PLANNING ONLY - does NOT execute changes. Returns step-by-step plan with code snippets, testing strategy, and documentation updates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "What to implement (e.g., 'Add rate limiting to all API endpoints', 'Create new agent for X', 'Refactor Y for performance')"
                            },
                            "approach": {
                                "type": "string",
                                "description": "Implementation approach (e.g., 'decorator_pattern', 'new_agent', 'refactor', 'api_integration')"
                            },
                            "files_to_modify": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: Specific files to modify (e.g., ['core/views_image.py', 'agents/new_agent.py'])"
                            }
                        },
                        "required": ["description", "approach"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_documentation",
                    "description": "Ask the CTO Agent to analyze documentation coverage and identify gaps. Session 98: Read-only analysis. Returns recommendations for docs to create/update but does NOT modify files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "enum": ["changed_files", "all_agents", "all_features", "full"],
                                "description": "Documentation scope: 'changed_files' for recent changes, 'all_agents' for agent docs, 'all_features' for feature docs, 'full' for complete platform",
                                "default": "all_features"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_roadmap",
                    "description": "Ask the COO Agent to analyze the project roadmap and provide strategic recommendations. Session 98: Read-only analysis. Returns summary, priorities, risks, suggested tasks, and timeline.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier (e.g., 'session-management', 'character-training')"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature to analyze (e.g., 'AI Assistant voice commands', 'Video chaining workflow')"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["project", "feature", "platform"],
                                "description": "Analysis scope: 'project' for specific project, 'feature' for single feature, 'platform' for entire platform",
                                "default": "project"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plan_next_sprint",
                    "description": "Ask the COO Agent to plan the next sprint with concrete tasks. Session 98: Planning only - does NOT execute tasks. Returns sprint goals, tasks, success criteria, and estimated effort.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier for sprint focus"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature for sprint focus"
                            },
                            "sprint_duration": {
                                "type": "string",
                                "description": "Sprint length (e.g., '2 weeks', '1 week', '3 days')",
                                "default": "2 weeks"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_risks",
                    "description": "Ask the COO Agent to identify risks, blockers, and mitigation strategies. Session 98: Read-only analysis. Returns critical risks, moderate risks, dependencies, and mitigation strategies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier for risk analysis"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature for risk analysis"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["project", "feature", "platform"],
                                "description": "Risk analysis scope",
                                "default": "project"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "start_executive_meeting",
                    "description": "Start an executive boardroom meeting with any combination of 8 executives (CTO, COO, Product Manager, Legal, Marketing, Strategy, HR, CFO) to discuss a topic collaboratively. Session 100: Returns meeting summary with perspectives from all selected executives, decisions, and action items. Natural language examples: 'Include CFO and Marketing' or 'All executives' or 'Technical team (CTO, Product Manager)'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Meeting topic or agenda (e.g., 'Pricing strategy for Q1', 'AI feature roadmap', 'Platform launch plan')"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for context"
                            },
                            "participants": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CTOAgent", "COOAgent", "ProductManagerAgent", "LegalAgent", "MarketingAgent", "StrategyAgent", "HRAgent", "CFOAgent"]
                                },
                                "description": "List of executive participants. Map natural language to agent names: CTO→CTOAgent, COO→COOAgent, Product Manager/PM→ProductManagerAgent, Legal/General Counsel→LegalAgent, Marketing/CMO→MarketingAgent, Strategy/CSO→StrategyAgent, HR/CHRO→HRAgent, CFO/Finance→CFOAgent. Default: CTO + COO",
                                "default": ["CTOAgent", "COOAgent"]
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        ]

        # Call OpenAI GPT-5 using Chat Completions API with function calling
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"💬 Assistant chat request from {request.user.username}: '{user_message[:50]}...'")

        # Session 65: Use Chat Completions API with tools instead of Responses API
        # Use gpt-5-mini (same as Session 56) which supports function calling
        logger.info(f"🤖 Calling GPT-5-mini with {len(tools)} tools available...")

        response = client.chat.completions.create(
            model="gpt-5-mini",  # Session 56 confirmed this works with Chat Completions API
            messages=messages,
            tools=tools,
            tool_choice="auto"  # Let the model decide when to call tools
            # Note: gpt-5-mini doesn't support max_tokens parameter
        )

        # Check if the model wants to call a tool
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        logger.info(f"🔍 GPT-4o response - tool_calls: {tool_calls}, content: {response_message.content[:100] if response_message.content else 'None'}...")

        if tool_calls:
            # Model wants to execute a tool!
            logger.info(f"🔧 AI wants to call {len(tool_calls)} tool(s)")

            # Return tool call information to frontend
            # Frontend will execute the tool and show progress
            return Response({
                'tool_calls': [
                    {
                        'id': tool_call.id,
                        'name': tool_call.function.name,
                        'arguments': json.loads(tool_call.function.arguments)
                    }
                    for tool_call in tool_calls
                ],
                'model': 'gpt-5-mini',
                'user_message': user_message,
                'session_id': str(session.session_id),  # Session 96: Return session ID for tracking
                'session_title': session.title,  # Session 96: Frontend integration
                'total_images': session.total_images,  # Session 96: Frontend integration
                'total_videos': session.total_videos,  # Session 96: Frontend integration
                'total_audio': session.total_audio  # Session 96: Frontend integration
            })
        else:
            # Normal text response
            assistant_response = response_message.content

            if not assistant_response:
                logger.error(f"❌ GPT-5 returned empty response")
                assistant_response = "I apologize, but I encountered an issue generating a response. Please try rephrasing your question!"

            assistant_response = assistant_response.strip()
            logger.info(f"✅ Assistant response generated ({len(assistant_response)} chars)")

            # Session 96 Weekend Project: Store assistant response in session transcript
            update_session_transcript(session, 'assistant', assistant_response)

            return Response({
                'message': assistant_response,
                'model': 'gpt-5-mini',
                'user_message': user_message,
                'session_id': str(session.session_id),  # Session 96: Return session ID for tracking
                'session_title': session.title,  # Session 96: Frontend integration
                'total_images': session.total_images,  # Session 96: Frontend integration
                'total_videos': session.total_videos,  # Session 96: Frontend integration
                'total_audio': session.total_audio  # Session 96: Frontend integration
            })

    except Exception as e:
        logger.error(f"❌ Error in assistant chat: {str(e)}")
        return Response({
            'error': 'Sorry, I encountered an error. Please try again!',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_audio(request):
    """
    Transcribe audio using OpenAI Whisper API
    Session 64: Voice input for AI Assistant

    Accepts audio file and returns transcribed text.
    User can then edit the text before sending to assistant.

    Example:
        Input: Audio blob (webm/mp4/wav)
        Output: {"text": "I want to create a logo but I'm not sure what prompt to use"}
    """
    try:
        # Get audio file from request
        audio_file = request.FILES.get('audio')

        if not audio_file:
            return Response({
                'error': 'No audio file provided'
            }, status=400)

        logger.info(f"🎤 Transcribing audio for {request.user.username} ({audio_file.size} bytes)")

        # Call OpenAI Whisper API
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Session 81: Convert Django InMemoryUploadedFile to BytesIO for OpenAI SDK
        # OpenAI SDK doesn't accept Django's file object directly
        from io import BytesIO
        audio_file.seek(0)
        audio_bytes = audio_file.read()
        audio_file_like = BytesIO(audio_bytes)

        # Session 124: Use the actual file extension from the uploaded file
        # This ensures OpenAI Whisper gets the correct format hint
        audio_file_like.name = audio_file.name or "recording.webm"
        logger.info(f"🎤 Audio file: {audio_file_like.name} ({len(audio_bytes)} bytes)")

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file_like,
            language="en"  # Can be removed to auto-detect
        )

        transcribed_text = transcript.text.strip()
        logger.info(f"✅ Transcribed: '{transcribed_text[:100]}...'")

        return Response({
            'text': transcribed_text,
            'success': True
        })

    except Exception as e:
        logger.error(f"❌ Error transcribing audio: {str(e)}")
        return Response({
            'error': 'Failed to transcribe audio. Please try again!',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_tool(request):
    """
    Execute a tool called by GPT-5 function calling
    Session 65: SUPER AI EXECUTOR - Autonomous tool execution

    This endpoint receives tool execution requests from the AI assistant
    and routes them to the appropriate service (Stability AI, Runway ML,
    Serper search, spider network, email, etc.)

    Expected JSON:
    {
        "tool_name": "generate_image",
        "parameters": {
            "prompt": "disco dinosaur logo",
            "model": "sdxl",
            "style": "vector"
        }
    }

    Returns:
    {
        "success": true,
        "result": {...},  # Tool-specific result
        "tool_name": "generate_image"
    }
    """
    try:
        tool_name = request.data.get('tool_name')
        parameters = request.data.get('parameters', {})
        session_id = request.data.get('session_id')  # Session 96 Weekend Project
        project_id = request.data.get('project_id')  # Session 156: Project context support

        if not tool_name:
            return Response({
                'error': 'tool_name is required'
            }, status=400)

        logger.info(f"🔧 Executing tool: {tool_name} with params: {parameters}")

        # Session 96 Weekend Project: Get session for linking generated content
        # Session 156: Also support project_id for project context
        session = None
        project = None
        if session_id:
            session = get_or_create_session(user=request.user, session_id=session_id)
        elif project_id:
            # Get project from project_id for context
            # Session 324: Unified to PartnershipProject
            from core.models_partnership import PartnershipProject
            try:
                project = PartnershipProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 Tool execution in project context: {project.project_name} ({project_id})")
            except PartnershipProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found for user {request.user.username}")

        # Session 182: Inject project_id into parameters for project association
        if project_id and 'project_id' not in parameters:
            parameters['project_id'] = project_id
            logger.info(f"📁 Injected project_id into parameters: {project_id}")

        # Route to appropriate tool handler
        # Session 181: Added agent name aliases for GPT function calling compatibility
        # Session 191: Workflow Orchestration Agent - HIGHEST PRIORITY
        # Session 202: AgentRouter for unified routing (Phase 2)

        # Try router-based routing first for supported intents
        # This gradually migrates tools to the new unified agent architecture
        # Session 204: Phase 5 - Tool Consolidation (expanded tool list)
        ROUTER_ENABLED_TOOLS = {
            # Image operations through unified ImageAgent
            'upscale_image', 'remove_background', 'create_variations',
            'recolor_image', 'erase_object', 'search_and_replace',
            'creative_upscale', 'inpaint', 'outpaint',
            # Audio operations through unified AudioAgent
            'generate_speech', 'generate_sound_effect', 'add_voiceover',
            # Video operations through unified VideoAgent
            'add_text_to_video', 'add_music_to_video', 'apply_color_grade',
            'chain_videos',
            # Research operations through unified ResearchAgent (Session 203)
            'web_search', 'research_topic', 'research',
            # Training operations (Session 204)
            'character_training_agent', 'train_character', 'train_style',
            # Talking character (Session 204)
            'talking_character_agent', 'create_talking_character', 'make_image_talk',
            # Workflow operations (Session 204)
            'workflow_orchestration_agent', 'create_brand_video',
            # Leadership operations (Session 204)
            'coleadership_agent', 'strategic_review', 'create_project_from_research',
        }

        if tool_name in ROUTER_ENABLED_TOOLS:
            try:
                from core.agent_router import AgentRouter
                logger.info(f"🔀 Using AgentRouter.execute_tool for: {tool_name}")

                # Session 204: Use execute_tool for full agent routing with preference support
                result = AgentRouter.execute_tool(
                    tool_name=tool_name,
                    arguments=parameters,
                    user=request.user,
                    session=session,
                    project=project
                )

                if result.get('success', True):
                    logger.info(f"✅ Router success for {tool_name}")
                else:
                    # Fall through to legacy handling if router fails
                    logger.warning(f"⚠️ Router failed, falling back to legacy: {result.get('error')}")
                    result = None
            except Exception as e:
                logger.error(f"❌ Router error, falling back to legacy: {e}")
                result = None

            # If router succeeded, return early
            if result is not None and result.get('success', True):
                return Response({
                    'success': True,
                    'result': result,
                    'tool_name': tool_name,
                    'routed': True
                })

        # Legacy routing - will be gradually migrated to AgentRouter
        # This agent handles multi-step workflows like "research and create logos"
        if tool_name == 'workflow_orchestration_agent':
            from core.agents import WorkflowOrchestrationAgent

            agent = WorkflowOrchestrationAgent(
                user=request.user,
                project_id=parameters.get('project_id') or (str(project.id) if project else None)
            )

            result = agent.execute(
                workflow=parameters.get('workflow'),
                topic=parameters.get('topic'),
                count=parameters.get('count', 3),
                style_preferences=parameters.get('style_preferences', ''),
                user_message=parameters.get('user_message', '')  # Session 239: Pass original message
            )

        elif tool_name in ('generate_image', 'image_generation_agent'):
            result = _execute_generate_image(request.user, parameters, session=session)
        elif tool_name in ('generate_video', 'video_generation_agent'):
            # Session 267: SAFETY CHECK - Redirect logo/banner requests to image generation
            # GPT sometimes incorrectly routes these to video generation
            prompt = parameters.get('params', {}).get('prompt', '').lower()
            if 'logo' in prompt or 'banner' in prompt or 'icon' in prompt:
                logger.warning(f"⚠️ Session 267: Blocking video generation for logo/banner request. Redirecting to image generation.")
                logger.warning(f"⚠️ Original prompt: {prompt}")
                # Redirect to image generation instead
                image_params = {
                    'prompt': parameters.get('params', {}).get('prompt', ''),
                    'count': 3,
                    'params': {'width': 1024, 'height': 1024, 'quality': 'high'}
                }
                result = _execute_generate_image(request.user, image_params, session=session)
                result['redirected_from'] = 'video_generation_agent'
                result['redirect_reason'] = 'Logo/banner requests should use image generation, not video'
            else:
                result = _execute_generate_video(request.user, parameters, session=session)
        elif tool_name == 'inpaint':
            result = _execute_inpaint(request.user, parameters)
        elif tool_name == 'resize_image_for_format':
            # Session 182: Resize image for social media formats (Exact Match mode)
            result = _execute_resize_image_for_format(request.user, parameters)
        elif tool_name == 'web_search':
            result = _execute_web_search(parameters)
        elif tool_name == 'scrape_website':
            result = _execute_scrape_website(parameters)
        elif tool_name == 'send_email':
            result = _execute_send_email(request.user, parameters)
        elif tool_name == 'create_brand_video':
            result = _execute_create_brand_video(request.user, parameters)
        # Session 189: Create project from research workflow
        elif tool_name == 'create_project_from_research':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            result = assistant._handle_create_project_from_research(parameters)
        # Session 189: Strategic review - co-leadership review BEFORE image generation
        elif tool_name == 'strategic_review':
            result = _execute_strategic_review(request.user, parameters)
        elif tool_name == 'chain_videos':
            result = _execute_chain_videos(request.user, parameters)
        elif tool_name == 'add_text_to_video':
            # Session 81: Route to VideoAgent
            from core.agents import get_video_agent
            video_agent = get_video_agent(user=request.user)
            result = video_agent.add_text_to_video(**parameters)
        elif tool_name == 'add_music_to_video':
            # Session 81: Route to VideoAgent (auto-queries AudioAgent)
            from core.agents import get_video_agent
            video_agent = get_video_agent(user=request.user)
            result = video_agent.add_music_to_video(**parameters)
        elif tool_name == 'apply_color_grade':
            # Session 84: Route to enhanced execution function
            result = _execute_apply_color_grade(request.user, parameters)
        elif tool_name == 'edit_video':
            # Session 84: Master orchestrator for multi-operation editing
            result = _execute_edit_video(request.user, parameters)
        elif tool_name == 'show_recent_videos':
            # Session 84: Show recent videos with numbers
            result = _execute_show_recent_videos(request.user, parameters)
        elif tool_name == 'create_character_from_prompt':
            result = _execute_create_character_from_prompt(request.user, parameters)
        elif tool_name == 'edit_character_training_image':
            result = _execute_edit_character_training_image(request.user, parameters)
        elif tool_name == 'generate_speech':
            # Session 81: Route to AudioAgent (stores state in memory)
            from core.agents import get_audio_agent
            audio_agent = get_audio_agent(user=request.user)
            result = audio_agent.generate_speech(**parameters)
        elif tool_name == 'generate_sound_effect':
            # Session 81: Route to AudioAgent (stores state in memory)
            from core.agents import get_audio_agent
            audio_agent = get_audio_agent(user=request.user)
            result = audio_agent.generate_sound_effect(**parameters)
        elif tool_name == 'audio_generation_agent':
            # Session 190: GPT sometimes calls this generic name - route to appropriate audio handler
            # But if no text is provided, return error explaining the tool wasn't needed
            text = parameters.get('text') or parameters.get('prompt') or parameters.get('message')
            if not text:
                result = {
                    'success': False,
                    'error': 'audio_generation_agent requires a "text" parameter. Did you mean to call create_project_from_research instead?',
                    'suggestion': 'For logo creation workflows, the final step should be create_project_from_research, not audio_generation_agent.'
                }
            else:
                from core.agents import get_audio_agent
                audio_agent = get_audio_agent(user=request.user)
                operation = parameters.get('operation', 'speech')
                if operation == 'sound_effect':
                    result = audio_agent.generate_sound_effect(**{k: v for k, v in parameters.items() if k != 'operation'})
                else:
                    # Default to speech generation
                    result = audio_agent.generate_speech(text=text)
        elif tool_name == 'generate_with_options':
            # Session 90: Route to WorkflowCoordinatorAgent - Multi-generation with learning
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_generate_with_options_workflow(
                prompt=parameters.get('prompt'),
                count=parameters.get('count', 3),
                style=parameters.get('style'),
                model=parameters.get('model'),
                session=session  # Session 96: Pass session for content linking
            )

            # Store batch_id for later reference
            if result.get('success'):
                # NOTE: batch_id stored in result for frontend reference
                logger.info(f"✅ Generated {len(result.get('options', []))} options, batch_id: {result.get('batch_id')}")

        elif tool_name == 'save_as_template':
            # Session 90: Route to WorkflowCoordinatorAgent - Template creation
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_save_as_template_workflow(
                image_id=parameters.get('image_id'),
                template_name=parameters.get('template_name'),
                tags=parameters.get('tags', []),
                also_add_to_references=True
            )

        elif tool_name == 'train_brand_style':
            # Session 90: Route to WorkflowCoordinatorAgent - Brand training
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_train_brand_style_workflow(
                brand_name=parameters.get('brand_name'),
                image_ids=parameters.get('image_ids'),
                auto_submit=parameters.get('auto_submit', False)
            )

        elif tool_name == 'refine_image':
            # Session 90: Route to IterationAgent - Natural language refinement
            from ai_core.agents.iteration_agent import IterationAgent
            agent = IterationAgent(user=request.user)
            result = agent.refine_image(
                image_id=parameters.get('image_id'),
                refinement_request=parameters.get('refinement_request')
            )

        elif tool_name == 'analyze_codebase':
            # Session 98: Route to CTOAgent - Codebase analysis (read-only)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.analyze_feature(
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'feature')
            )

        elif tool_name == 'plan_implementation':
            # Session 98: Route to CTOAgent - Implementation planning (no execution)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.implement_feature(
                description=parameters.get('description'),
                approach=parameters.get('approach'),
                files_to_modify=parameters.get('files_to_modify')
            )

        elif tool_name == 'analyze_documentation':
            # Session 98: Route to CTOAgent - Documentation analysis (read-only)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.sync_documentation(
                scope=parameters.get('scope', 'all_features')
            )

        elif tool_name == 'analyze_roadmap':
            # Session 98: Route to COOAgent - Roadmap analysis (read-only)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.analyze_roadmap(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'project')
            )

        elif tool_name == 'plan_next_sprint':
            # Session 98: Route to COOAgent - Sprint planning (no execution)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.propose_next_sprint(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                sprint_duration=parameters.get('sprint_duration', '2 weeks')
            )

        elif tool_name == 'analyze_risks':
            # Session 98: Route to COOAgent - Risk analysis (read-only)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.identify_risks(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'project')
            )

        elif tool_name == 'start_executive_meeting':
            # Session 98: Route to MeetingCoordinatorAgent - Executive boardroom meeting
            from core.agents.executive import MeetingCoordinatorAgent
            from content.models import AISession

            coordinator = MeetingCoordinatorAgent(user=request.user)

            # Start the meeting
            meeting_result = coordinator.start_meeting(
                topic=parameters.get('topic'),
                project_id=parameters.get('project_id'),
                participants=parameters.get('participants', ['CTOAgent', 'COOAgent'])
            )

            # Create a boardroom AISession to store results
            if meeting_result.get('status') == 'complete':
                session = AISession.objects.create(
                    user=request.user,
                    title=f"Boardroom: {parameters.get('topic')[:100]}",
                    session_type='boardroom',
                    meeting_topic=parameters.get('topic'),
                    participants=meeting_result.get('participants', []),
                    meeting_summary=meeting_result.get('summary', ''),
                    decisions=meeting_result.get('decisions', []),
                    action_items=meeting_result.get('action_items', []),
                    agent_responses=meeting_result.get('agent_responses', {}),
                    is_active=False,  # Meetings are one-shot
                    conversation_transcript=[{
                        'role': 'system',
                        'content': f"Executive meeting conducted: {parameters.get('topic')}"
                    }]
                )

                logger.info(f"✅ Created boardroom session: {session.session_id}")
                meeting_result['session_id'] = str(session.session_id)

                # Session 99: Create co-leadership decision + log agent recommendations
                from coleadership.services import start_decision, log_agent_recommendation
                from core.models.agents_registry import UnifiedAgentTemplate
                from content.models import CreativeProject

                # Get project if provided
                project = None
                if parameters.get('project_id'):
                    try:
                        import uuid
                        # Validate UUID format
                        project_uuid = uuid.UUID(parameters.get('project_id'))
                        project = CreativeProject.objects.get(
                            id=project_uuid,
                            user=request.user
                        )
                    except (CreativeProject.DoesNotExist, ValueError, TypeError):
                        # If UUID is invalid or project doesn't exist, just skip project linkage
                        logger.warning(f"Invalid or non-existent project_id: {parameters.get('project_id')}")

                # Create decision
                decision = start_decision(
                    project=project,
                    session=session,
                    user=request.user,
                    title=parameters.get('topic'),
                    description=meeting_result.get('summary', '')
                )

                # Log each agent's recommendation
                agent_responses = meeting_result.get('agent_responses', {})
                for agent_name, response_text in agent_responses.items():
                    try:
                        # Find agent template
                        agent_template = UnifiedAgentTemplate.objects.get(name=agent_name)

                        # Simple stance inference (can enhance later)
                        stance = 'neutral'  # Default
                        if 'recommend' in response_text.lower() or 'support' in response_text.lower():
                            stance = 'support'
                        elif 'concern' in response_text.lower() or 'risk' in response_text.lower():
                            stance = 'concern'
                        elif 'alternative' in response_text.lower():
                            stance = 'alternative'

                        # Log recommendation
                        log_agent_recommendation(
                            decision=decision,
                            agent_template=agent_template,
                            payload_dict={
                                'stance': stance,
                                'summary': response_text[:200],  # First 200 chars
                                'recommendation': response_text,
                                'risks': '',  # Can extract later
                                'alternative_paths': [],
                                'confidence': None,  # Can add later
                                'time_horizon': ''
                            }
                        )
                    except UnifiedAgentTemplate.DoesNotExist:
                        logger.warning(f"Agent template not found: {agent_name}")
                        continue

                # Add decision_id, session_id, project_id to response (Session 100: Full integration)
                meeting_result['decision_id'] = str(decision.id)
                meeting_result['session_id'] = str(session.session_id) if session else None
                meeting_result['project_id'] = str(project.id) if project else None
                logger.info(f"✅ Created co-leadership decision: {decision.id} (session: {session.session_id if session else 'none'}, project: {project.id if project else 'none'})")

            result = meeting_result

        elif tool_name == 'image_editing_agent':
            # Session 156: Route to enhanced personal assistant's image editing handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Session 156: Inject project_id into parameters for content linking
            if project:
                parameters['project_id'] = str(project.id)
            result = assistant._handle_image_editing_agent(parameters)

        elif tool_name == 'video_editing_agent':
            # Session 155: Route to enhanced personal assistant's video editing handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Session 156: Inject project_id into parameters for content linking
            if project:
                parameters['project_id'] = str(project.id)
            result = assistant._handle_video_editing_agent(parameters)

        elif tool_name == 'video_generation_agent':
            # Session 157: Route to enhanced personal assistant's video generation handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Session 157: Set project as instance attribute for VideoAgent
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_video_generation_agent(parameters)

        elif tool_name == 'three_d_generation_agent':
            # Session 172: Route to enhanced personal assistant's 3D generation handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Set project as instance attribute for 3D generation
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_three_d_generation_agent(parameters)

        elif tool_name == 'character_training_agent':
            # Session 173: Route to enhanced personal assistant's character training handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Set project as instance attribute for training context
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_character_training_agent(parameters)

        elif tool_name == 'coleadership_agent':
            # Session 173: Route to enhanced personal assistant's co-leadership handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Set project as instance attribute for decision context
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_coleadership_agent(parameters)

        elif tool_name == 'talking_character_agent':
            # Session 175: Route to enhanced personal assistant's talking character handler
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            # Set project as instance attribute for pipeline context
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._tool_talking_character(parameters)

        # Session 324: Business Research Agents
        elif tool_name == 'competitor_analysis_agent':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_competitor_analysis_agent(parameters)

        elif tool_name == 'customer_research_agent':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_customer_research_agent(parameters)

        # Session 335: Brand Strategy Agent
        elif tool_name == 'brand_strategy_agent':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_brand_strategy_agent(parameters)

        # Session 338: Content Strategy Agent
        elif tool_name == 'content_strategy_agent':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_content_strategy_agent(parameters)

        # Session 338: Marketing Strategy Agent
        elif tool_name == 'marketing_strategy_agent':
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            assistant = EnhancedPersonalAIAssistant(user=request.user)
            if project:
                assistant.project = project
                parameters['project_id'] = str(project.id)
            result = assistant._handle_marketing_strategy_agent(parameters)

        else:
            return Response({
                'error': f'Unknown tool: {tool_name}'
            }, status=400)

        logger.info(f"✅ Tool {tool_name} executed successfully")

        return Response({
            'success': True,
            'result': result,
            'tool_name': tool_name
        })

    except Exception as e:
        logger.error(f"❌ Error executing tool {tool_name}: {str(e)}")
        return Response({
            'error': f'Failed to execute tool: {str(e)}',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


# ========================================
# TOOL EXECUTION HANDLERS (Session 65)
# ========================================

def _verify_image_with_vision(image_url, expected_text):
    """
    Use GPT-4 Vision to verify image text accuracy

    Session 66: Vision-powered autonomous refinement

    Parameters:
        image_url (str): URL of image to verify
        expected_text (str): Text that should appear in image

    Returns:
        dict: {
            'correct': True/False,
            'observed_text': 'What Vision actually sees',
            'feedback': 'Specific feedback for correction',
            'confidence': 'high/medium/low'
        }
    """
    try:
        import base64

        logger.info(f"👁️ Using GPT-4 Vision to verify text: '{expected_text}'")

        # Session 66: Fix - Convert local URLs to base64 data URIs
        # OpenAI Vision API can't access localhost URLs, so we need to encode the image
        if image_url.startswith('/'):
            # Local file path - read from disk and convert to base64
            image_path = image_url.lstrip('/')  # Remove leading slash
            full_path = os.path.join(settings.BASE_DIR, image_path)

            logger.info(f"👁️ Reading local image: {full_path}")

            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            # Determine image format from extension
            ext = image_url.split('.')[-1].lower()
            mime_type = f"image/{ext}" if ext in ['png', 'jpg', 'jpeg', 'webp'] else 'image/png'

            # Create data URI
            image_url = f"data:{mime_type};base64,{base64_image}"
            logger.info(f"👁️ Converted to base64 data URI ({len(base64_image)} chars)")

        # Get OpenAI client
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Build Vision API request
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a text verification expert. Analyze images and verify if text matches expectations.

Be VERY specific about what you see:
- Report the EXACT text you observe (including spelling, spacing, punctuation)
- Compare it to the expected text
- Provide specific feedback on what's wrong
- Be critical but accurate"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this image and verify the text.

**Expected Text:** "{expected_text}"

**Your Task:**
1. What text do you actually see in this image? (Report EXACT text, including all words)
2. Does it match "{expected_text}" perfectly?
3. If not, what's different? (spelling, missing words, extra words, wrong order, etc.)

Be specific and accurate. This is for autonomous text correction."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_completion_tokens=300,
            reasoning_effort="medium",
        )

        # Parse Vision response
        vision_feedback = response.choices[0].message.content
        logger.info(f"👁️ Vision feedback: {vision_feedback}")

        # Analyze Vision's response to determine correctness
        lower_feedback = vision_feedback.lower()
        expected_lower = expected_text.lower()

        # Check if Vision confirms match
        correct = any([
            'matches perfectly' in lower_feedback,
            'correct' in lower_feedback and 'incorrect' not in lower_feedback,
            'yes' in lower_feedback and 'does it match' in lower_feedback,
            f'"{expected_lower}"' in lower_feedback and 'matches' in lower_feedback
        ])

        # Determine confidence based on Vision's language
        if 'exactly' in lower_feedback or 'perfect' in lower_feedback:
            confidence = 'high'
        elif 'mostly' in lower_feedback or 'close' in lower_feedback:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Try to extract what Vision actually observed
        observed_text = expected_text  # Default to expected if we can't extract
        if 'see' in lower_feedback or 'says' in lower_feedback or 'reads' in lower_feedback:
            # Vision mentioned what it sees - try to extract it
            import re
            # Look for quoted text
            quotes = re.findall(r'"([^"]+)"', vision_feedback)
            if quotes:
                # First quote is usually what it actually sees
                observed_text = quotes[0] if quotes[0].lower() != expected_lower else expected_text

        result = {
            'correct': correct,
            'observed_text': observed_text,
            'feedback': vision_feedback,
            'confidence': confidence
        }

        logger.info(f"👁️ Verification result: {result}")
        return result

    except Exception as e:
        logger.error(f"❌ Error in _verify_image_with_vision: {str(e)}")
        # Return neutral result on error (don't block generation)
        return {
            'correct': True,  # Assume correct if we can't verify
            'observed_text': expected_text,
            'feedback': f'Vision verification failed: {str(e)}',
            'confidence': 'low'
        }


def _execute_generate_image(user, parameters, session=None):
    """
    Execute image generation tool
    Routes to Stability AI image generation

    Session 65: Phase 2.1 - Autonomous image generation
    Session 96: Weekend Project - Link generated images to AI session

    Parameters:
        prompt (str): Image description
        model (str): Model to use (core/sdxl/sd3/ultra) - optional
        style (str): Style preset - optional
        session (AISession): AI conversation session - optional

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL to generated image',
            'image_id': 'History ID',
            'prompt': 'Actual prompt used'
        }
    """
    try:
        prompt = parameters.get('prompt', '').strip()
        model = parameters.get('model', 'sdxl')  # Default to sdxl (best balance)
        style = parameters.get('style', '')  # Optional style
        expected_text = parameters.get('expected_text', '').strip()  # Session 66: For Vision refinement
        # Session 201: Use negative_prompt from parameters (for text-free logos)
        negative_prompt = parameters.get('negative_prompt', 'blurry, low quality, distorted')

        # Session 181: Support custom sizes from image_generation_agent
        width = parameters.get('width')
        height = parameters.get('height')
        if width and height:
            size = f"{width}x{height}"
        else:
            size = parameters.get('size', '1024x1024')

        # Session 182: Get project for association
        # Session 267: Validate UUID before querying to avoid ValidationError
        # Session 272: uuid is imported at module level - don't re-import locally
        project = None
        project_id = parameters.get('project_id')
        if project_id:
            from content.models import CreativeProject
            # Validate that project_id is a valid UUID before querying
            try:
                uuid.UUID(str(project_id))  # This will raise ValueError if invalid
                project = CreativeProject.objects.get(id=project_id, user=user)
                logger.info(f"📁 Image will be associated with project: {project.name}")
            except ValueError:
                logger.warning(f"⚠️ Invalid project_id format (not a UUID): {project_id}")
                project_id = None  # Clear invalid project_id
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found")

        if not prompt:
            raise ValueError("Prompt is required for image generation")

        logger.info(f"🎨 Executor generating image: {prompt[:50]}... (model: {model}, style: {style}, size: {size})")
        if expected_text:
            logger.info(f"👁️ Expected text for verification: '{expected_text}'")

        # Map model names to quality parameter
        model_to_quality = {
            'core': 'fast',
            'sdxl': 'balanced',
            'sd3': 'high',
            'ultra': 'premium'
        }
        quality = model_to_quality.get(model, 'balanced')

        # Session 184: Support count parameter for batch image generation
        # Extract count from parameters or nested params object
        count = parameters.get('count', 1)
        if isinstance(parameters.get('params'), dict):
            count = parameters['params'].get('count', count)
        count = min(max(int(count), 1), 5)  # Clamp between 1 and 5

        logger.info(f"🎨 Generating {count} image(s) with prompt: {prompt[:50]}...")
        logger.info(f"🚫 Negative prompt: {negative_prompt[:80]}..." if len(negative_prompt) > 80 else f"🚫 Negative prompt: {negative_prompt}")

        # Use ImageGenerationService directly (same as gallery_generate)
        from content.image_generation import ImageGenerationService
        service = ImageGenerationService()

        # Session 184: Generate multiple images in a loop
        # Session 806: Track last error for better error reporting
        generated_images = []
        last_error = None
        for i in range(count):
            logger.info(f"🎨 Generating image {i + 1}/{count}...")

            result = service.generate_image(
                prompt=prompt,
                size=size,  # Session 181: Use dynamic size
                style=style if style else "photographic",
                quality=quality,
                provider='stability',
                negative_prompt=negative_prompt,  # Session 201: Use parameter (for text-free logos)
                num_images=1
            )

            if not result.success:
                last_error = result.error_message or 'Unknown error'
                logger.error(f"❌ Image {i + 1} generation failed: {last_error}")
                continue  # Try to generate remaining images

            # Get the generated image
            images = result.images
            if not images:
                # Session 843: Set last_error even when success=True but images empty
                last_error = result.error_message or "API returned success but no images"
                logger.error(f"❌ Image {i + 1}: No image returned - {last_error}")
                continue

            image_data = images[0]
            image_url = image_data if isinstance(image_data, str) else image_data.get('url')

            # Save image to storage
            # Session 272: Handle anonymous users (use 'anonymous' folder)
            image_id = str(uuid.uuid4())
            user_folder = user.id if user else 'anonymous'
            filename = f"generated_images/{user_folder}/{image_id}.png"

            # Handle base64 data URIs vs regular URLs
            try:
                if image_url.startswith('data:image'):
                    # Extract base64 data from data URI
                    import re
                    base64_match = re.search(r'base64,(.+)', image_url)
                    if base64_match:
                        image_bytes = base64.b64decode(base64_match.group(1))
                        file_path = default_storage.save(filename, ContentFile(image_bytes))
                        saved_url = default_storage.url(file_path)
                    else:
                        raise Exception("Invalid base64 data URI")
                else:
                    # Regular HTTP/HTTPS URL - download it
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        file_path = default_storage.save(filename, ContentFile(response.content))
                        saved_url = default_storage.url(file_path)
                    else:
                        raise Exception(f"Failed to download image: {response.status_code}")

                # Save to ImageHistory for tracking
                # Session 96 Weekend Project: Link to AI conversation session
                # Session 182: Link to project for Social Media Kit workflow
                # Session 272: Only save to history if user is authenticated
                # Session 794: Use system user for autonomous operations (Celery tasks)
                history_user = user
                if not history_user:
                    history_user = get_system_user()
                    logger.info(f"🤖 Using system_autonomous user for image history")

                history_record = save_to_history(
                    user=history_user,
                    file_path=file_path,
                    image_type='generated',
                    prompt=prompt,
                    parameters={
                        'model': model,
                        'style': style,
                        'quality': quality,
                        'batch_index': i + 1,
                        'autonomous': user is None  # Session 794: Track autonomous generation
                    },
                    model_used=model,
                    style=style,
                    parent_image=None,
                    session=session,  # Session 96: Link to AI conversation
                    project=project   # Session 182: Link to project
                )

                generated_images.append({
                    'image_url': saved_url,
                    'image_id': str(history_record.id) if history_record else image_id,
                    'file_path': file_path,
                    'batch_index': i + 1
                })

                logger.info(f"✅ Image {i + 1}/{count} generated successfully: {saved_url}")

            except Exception as img_error:
                # Session 843: Track save errors in last_error for better debugging
                last_error = f"Save failed: {str(img_error)}"
                logger.error(f"❌ Error saving image {i + 1}: {str(img_error)}")
                continue

        # Check if we generated any images
        # Session 806: Include the actual error message for better debugging
        # Session 843: Add prompt info to help debug content moderation issues
        if not generated_images:
            error_detail = last_error or "No images were generated"
            logger.error(f"❌ All {count} image(s) failed. Prompt: {prompt[:100]}... Error: {error_detail}")
            raise Exception(f"Image generation failed: {error_detail}")

        # Use the first image for backwards compatibility
        saved_url = generated_images[0]['image_url']
        file_path = generated_images[0].get('file_path', '')
        history_record = type('obj', (object,), {'id': generated_images[0]['image_id']})() if generated_images[0]['image_id'] else None

        logger.info(f"✅ Executor generated image successfully: {saved_url}")

        # Session 96 Weekend Project: Update session counter and check for auto-project creation
        project_info = increment_session_counter(session, 'image')

        # Session 66: AUTONOMOUS TEXT VERIFICATION & REFINEMENT
        expected_text = parameters.get('expected_text', '').strip()
        refinement_history = []

        if expected_text:
            logger.info(f"👁️ Starting autonomous text verification for: '{expected_text}'")
            max_attempts = 3
            current_url = saved_url
            current_history_id = history_record.id if history_record else None

            for attempt in range(max_attempts):
                logger.info(f"👁️ Verification attempt {attempt + 1}/{max_attempts}")

                # Verify current image with GPT-4 Vision
                verification = _verify_image_with_vision(current_url, expected_text)

                refinement_history.append({
                    'attempt': attempt + 1,
                    'image_url': current_url,
                    'verification': verification
                })

                if verification['correct']:
                    logger.info(f"✅ Text verified correct! Confidence: {verification['confidence']}")
                    break  # Text is correct, we're done!

                if attempt == max_attempts - 1:
                    logger.warning(f"⚠️ Max attempts reached, returning last version")
                    break  # Max attempts, return what we have

                # Text is wrong, use inpaint to fix it
                logger.info(f"🖌️ Text incorrect, calling inpaint to fix...")

                try:
                    inpaint_result = _execute_inpaint(user, {
                        'image_url': current_url,
                        'prompt': f"The text '{expected_text}' in clean, legible font",
                        'mask_description': 'the text area with the company/brand name'
                    })

                    if inpaint_result['success']:
                        current_url = inpaint_result['image_url']
                        current_history_id = inpaint_result['image_id']
                        logger.info(f"✅ Inpaint successful: {current_url}")
                    else:
                        logger.error(f"❌ Inpaint failed, keeping current version")
                        break

                except Exception as e:
                    logger.error(f"❌ Error during inpaint: {str(e)}")
                    break  # Error, return what we have

            # Update return values with final refined version
            saved_url = current_url
            if current_history_id:
                history_record = type('obj', (object,), {'id': current_history_id})()

        result = {
            'success': True,
            'image_url': saved_url,
            'image_id': history_record.id if history_record else None,
            'prompt': prompt,
            'model': model,
            'style': style,
            'refinement_history': refinement_history if refinement_history else None,
            'autonomous_refinement': len(refinement_history) > 1 if refinement_history else False,
            # Session 184: Include all generated images for batch requests
            'images': generated_images,
            'total_generated': len(generated_images),
            'requested_count': count
        }

        # Session 96: Include project creation info if project was auto-created
        if project_info:
            result.update(project_info)

        # Session 96: Include updated session counters for frontend indicator
        if session:
            session.refresh_from_db()  # Get latest counter values
            result['session_data'] = {
                'session_id': str(session.session_id),
                'total_images': session.total_images,
                'total_videos': session.total_videos,
                'total_audio': session.total_audio
            }

        return result

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_image: {str(e)}")
        raise


def _extract_image_reference(text, user):
    """
    Extract and resolve image references from text.

    Session 119: BUGFIX - Enable "create video from image 199" functionality

    Looks for patterns like:
    - "image 199"
    - "image #199"
    - "Image 199"
    - UUID strings

    Returns ImageHistory object if found, None otherwise.
    """
    import re
    from content.models import ImageHistory

    # Pattern 1: "image 199" or "image #199" (sequential number)
    pattern1 = r'image\s*#?(\d+)'
    matches = re.findall(pattern1, text, re.IGNORECASE)

    if matches:
        sequential_num = int(matches[0])
        # Session 183: Use sequential_number field (not id which is UUID)
        # Order by -created_at to handle duplicate sequential numbers
        try:
            image = ImageHistory.objects.filter(
                sequential_number=sequential_num,
                user=user
            ).order_by('-created_at').first()
            if image:
                logger.info(f"📸 Resolved 'image {sequential_num}' to: {image.filename} (ID: {image.id})")
                return image
            else:
                logger.warning(f"⚠️ Image #{sequential_num} not found for user {user.username}")
        except Exception as e:
            logger.warning(f"⚠️ Error finding image #{sequential_num}: {e}")

    # Pattern 2: UUID pattern (8-4-4-4-12 format)
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    uuid_matches = re.findall(uuid_pattern, text, re.IGNORECASE)

    if uuid_matches:
        try:
            image = ImageHistory.objects.get(id=uuid_matches[0], user=user)
            logger.info(f"📸 Resolved UUID to: {image.filename}")
            return image
        except ImageHistory.DoesNotExist:
            logger.warning(f"⚠️ Image UUID {uuid_matches[0]} not found")

    return None


def _execute_generate_video(user, parameters, session=None):
    """
    Execute video generation tool
    Routes to Runway ML video generation

    Session 65: Phase 2.2 - Autonomous video generation
    Session 96: Weekend Project - Link generated videos to AI session
    Session 183: Support both direct params and operation-based params from GPT
    Session 794: Use system user for autonomous operations (Celery tasks)

    Parameters:
        prompt (str): Video description
        duration (int): Duration in seconds (5 or 10) - optional
        session (AISession): AI conversation session - optional

    Also supports operation-based format from GPT:
        operation (str): 'animate' or 'generate'
        params (dict): {prompt, image_id, duration}

    Returns:
        dict: {
            'success': True,
            'task_id': 'Runway task ID',
            'content_id': 'Database ID',
            'status': 'processing',
            'message': 'Video generation started'
        }
    """
    try:
        # Session 794: Use system user for autonomous operations
        is_autonomous = user is None
        if is_autonomous:
            user = get_system_user()
            logger.info(f"🤖 Using system_autonomous user for video generation")
        # Session 183: Handle operation-based format from GPT
        operation = parameters.get('operation')
        if operation:
            # GPT sent operation-based params, extract the actual params
            inner_params = parameters.get('params', {})
            # Session 183: GPT may send motion_prompt OR prompt for animate operation
            prompt = inner_params.get('prompt', '') or inner_params.get('motion_prompt', '')
            prompt = prompt.strip() if prompt else ''
            duration = inner_params.get('duration', 6)
            # For animate operation, get image_id
            if operation == 'animate' and inner_params.get('image_id'):
                parameters['source_image_id'] = inner_params.get('image_id')
                # Session 183: If no prompt provided for animate, use a default motion prompt
                if not prompt:
                    prompt = "smooth natural motion with subtle movement"
            logger.info(f"🎬 Session 183: Extracted from operation={operation}: prompt={prompt[:50] if prompt else 'N/A'}...")
        else:
            # Direct params format
            prompt = parameters.get('prompt', '').strip()
            duration = parameters.get('duration', 6)  # Default to 6 seconds (Runway ML accepts 4, 6, or 8)

        if not prompt:
            raise ValueError("Prompt is required for video generation")

        # Validate duration - Runway ML only accepts 4, 6, or 8 seconds
        if duration not in [4, 6, 8]:
            logger.warning(f"⚠️ Invalid duration {duration}s, defaulting to 6s")
            duration = 6

        # Session 65: Runway ML has 1000 character prompt limit - truncate intelligently
        MAX_PROMPT_LENGTH = 1000
        if len(prompt) > MAX_PROMPT_LENGTH:
            logger.warning(f"⚠️ Prompt too long ({len(prompt)} chars), truncating to {MAX_PROMPT_LENGTH}")
            # Keep the first 950 chars and add ellipsis
            prompt = prompt[:950] + "..."
            logger.info(f"🎬 Truncated prompt: {prompt[:100]}...")

        # Session 122: Check for explicit source_image_id parameter FIRST (intelligent chaining!)
        # Session 119: BUGFIX - Check if prompt references an existing image
        # If found, use image-to-video instead of text-to-video
        source_image = None
        source_image_id = parameters.get('source_image_id')

        if source_image_id:
            # Session 122: AI explicitly passed an image ID - use it!
            # Session 183: Support hybrid IDs (numbers like "13" or UUIDs)
            try:
                from content.models import ImageHistory

                # Session 183: Handle numeric IDs (sequential_number) vs UUIDs
                image_id_str = str(source_image_id).strip()
                if image_id_str.isdigit():
                    # It's a sequential number - resolve to UUID
                    # Session 183: Order by -created_at to get newest record (handles duplicate sequential numbers)
                    seq_num = int(image_id_str)
                    source_image = ImageHistory.objects.filter(
                        user=user,
                        sequential_number=seq_num
                    ).order_by('-created_at').first()
                    if source_image:
                        logger.info(f"📸 Session 183: Resolved sequential #{seq_num} to UUID {source_image.id} (file: {source_image.file_path[:50] if source_image.file_path else 'N/A'}...)")
                    else:
                        logger.warning(f"⚠️ No image found with sequential_number={seq_num}")
                else:
                    # It's a UUID
                    source_image = ImageHistory.objects.get(id=source_image_id, user=user)
                    logger.info(f"📸 Session 122: AI passed explicit source_image_id: {source_image_id}")
            except ImageHistory.DoesNotExist:
                logger.warning(f"⚠️ Source image {source_image_id} not found, falling back to text-to-video")
                source_image = None
            except Exception as e:
                logger.warning(f"⚠️ Error resolving image ID {source_image_id}: {e}, falling back to text-to-video")
                source_image = None

        if not source_image:
            # Fallback to Session 119 text-based extraction
            source_image = _extract_image_reference(prompt, user)

        video_type = 'text_to_video'

        logger.info(f"🎬 Executor generating video: {prompt[:50]}... (duration: {duration}s)")

        # Use Runway ML provider directly (same as text_to_video view)
        from content.video_provider import runway_provider

        if source_image:
            # Image reference found - use image-to-video!
            logger.info(f"🖼️ Image reference detected! Using image-to-video with: {source_image.filename}")
            video_type = 'image_to_video'

            result = runway_provider.image_to_video(
                image_url=source_image.file_path,
                motion_prompt=prompt,
                duration=duration,
                quality='gen4_turbo',  # Use gen4_turbo for image-to-video
                enhance_prompt=True,
                ratio='1280:720'
            )
        else:
            # No image reference - use regular text-to-video
            result = runway_provider.text_to_video(
                prompt=prompt,
                duration=duration,
                quality='veo3.1_fast',  # Use fast model for executor
                style='realistic',
                enhance_prompt=True,
                enhancement_level='advanced',
                ratio='1920:1080'
            )

        if not result.success:
            raise Exception(f"Video generation failed: {result.error_message or 'Unknown error'}")

        # Session 68: Create VideoHistory record (not just ContentGeneration!)
        # This makes AI Assistant videos appear in Video Gallery
        # Session 96 Weekend Project: Link to AI conversation session
        from content.models import VideoHistory

        # Session 119: BUGFIX - Assign project if session already has one
        # When resuming a session with existing project, videos need to be linked immediately
        # Session 183: Also check for project_id in parameters (workflow passes it directly)
        video_project = None
        if session and session.project:
            video_project = session.project
            logger.info(f"📁 Assigning video to project from session: {session.project.name}")
        elif parameters.get('project_id'):
            # Session 183: Get project from parameters (workflow/direct tool call)
            from content.models import CreativeProject
            try:
                video_project = CreativeProject.objects.get(id=parameters['project_id'])
                logger.info(f"📁 Assigning video to project from parameters: {video_project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {parameters['project_id']} not found")

        video = VideoHistory.objects.create(
            user=user,
            video_id=result.task_id,
            video_url='',  # Will be populated when video completes
            video_type=video_type,  # Session 119: BUGFIX - Dynamic type based on image reference
            prompt=prompt,
            parameters={
                'duration': duration,
                'quality': 'gen4_turbo' if source_image else 'veo3.1_fast',
                'style': 'realistic',
                'ratio': '1280:720' if source_image else '1920:1080',
                'enhance_prompt': True,
                'enhancement_level': 'advanced',
                'source_image_id': str(source_image.id) if source_image else None,  # Session 119: Track source
                'autonomous': is_autonomous  # Session 794: Track autonomous generation
            },
            model_used='gen4_turbo' if source_image else 'veo3.1_fast',
            duration=duration,
            ratio='1280:720' if source_image else '1920:1080',
            status='processing',
            session=session,  # Session 96: Link to AI conversation
            project=video_project,  # Session 119: BUGFIX - Assign project if session has one
            source_image=source_image  # Session 119: BUGFIX - Link to source image if image-to-video
        )

        logger.info(f"✅ Executor started video generation: {result.task_id}")
        logger.info(f"📹 Created VideoHistory record: {video.id}")

        # Session 144: Track agent contribution for video generation
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
            AgentContribution.objects.create(
                agent=agent,
                video=video,
                project=video_project,
                contribution_type='generation',
                task_description=f"Generated video via gallery_generate_video (type={video_type}, duration={duration}s)",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for video {video.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            # Don't fail video creation if contribution tracking fails

        # Session 96 Weekend Project: Update session counter and check for auto-project creation
        project_info = increment_session_counter(session, 'video')

        result_dict = {
            'success': True,
            'task_id': result.task_id,
            'content_id': str(video.id),
            'status': result.status,
            'estimated_time': result.estimated_time,
            'message': 'Video generation started successfully'
        }

        # Session 96: Include project creation info if project was auto-created
        if project_info:
            result_dict.update(project_info)

        return result_dict

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_video: {str(e)}")
        raise


def _execute_create_brand_video(user, parameters):
    """
    Execute automated brand video workflow
    Session 67: End-to-end video creation orchestration

    This creates a complete brand video by:
    1. Generating video prompts based on concept and style
    2. Creating multiple video clips with Runway ML
    3. Returning task IDs for user to monitor
    4. User can chain them with DaVinci once complete

    Parameters:
        brand_name (str): Brand or company name
        concept (str): Video concept/message
        style (str): Visual style (cinematic, modern, playful, elegant, energetic)
        include_branding (bool): Add brand text overlays (default: true)
        video_count (int): Number of clips to generate (default: 3)

    Returns:
        dict: {
            'success': True,
            'task_ids': ['id1', 'id2', 'id3'],
            'prompts': ['prompt1', 'prompt2', 'prompt3'],
            'estimated_time': 180,
            'message': 'Brand video workflow started'
        }
    """
    try:
        brand_name = parameters.get('brand_name', '').strip()
        concept = parameters.get('concept', '').strip()
        style = parameters.get('style', 'modern')
        include_branding = parameters.get('include_branding', True)
        video_count = parameters.get('video_count', 3)

        if not brand_name:
            raise ValueError("Brand name is required")
        if not concept:
            raise ValueError("Concept is required")

        # Validate video_count (2-5)
        if video_count < 2 or video_count > 5:
            logger.warning(f"⚠️ Invalid video_count {video_count}, defaulting to 3")
            video_count = 3

        logger.info(f"🎬 Creating brand video for {brand_name}: {concept} ({style} style, {video_count} clips)")

        # Style-specific prompt modifiers
        style_modifiers = {
            'cinematic': 'dramatic lighting, cinematic composition, film grain, depth of field',
            'modern': 'clean lines, minimalist, bright natural lighting, contemporary design',
            'playful': 'vibrant colors, dynamic movement, fun energy, cheerful atmosphere',
            'elegant': 'sophisticated, refined aesthetic, smooth movements, luxury feel',
            'energetic': 'fast-paced, dynamic transitions, bold colors, high energy'
        }

        style_prompt = style_modifiers.get(style, style_modifiers['modern'])

        # Generate prompts for each video clip
        prompts = []
        if video_count == 2:
            prompts = [
                f"{concept}, {style_prompt}, opening shot",
                f"{brand_name} showcase, {concept}, {style_prompt}, closing scene"
            ]
        elif video_count == 3:
            prompts = [
                f"{concept}, {style_prompt}, establishing shot",
                f"{brand_name} product or service, {concept}, {style_prompt}, detail view",
                f"{concept}, {style_prompt}, powerful closing scene with {brand_name}"
            ]
        elif video_count == 4:
            prompts = [
                f"{concept}, {style_prompt}, opening sequence",
                f"{brand_name} highlights, {concept}, {style_prompt}, feature showcase",
                f"{concept} in action, {style_prompt}, dynamic demonstration",
                f"{brand_name} finale, {concept}, {style_prompt}, memorable closing"
            ]
        else:  # 5 clips
            prompts = [
                f"{concept}, {style_prompt}, captivating opening",
                f"{brand_name} introduction, {concept}, {style_prompt}",
                f"{concept}, {style_prompt}, mid-point highlight",
                f"{brand_name} key features, {concept}, {style_prompt}",
                f"{concept}, {style_prompt}, impactful conclusion with {brand_name}"
            ]

        # Generate all videos using Runway ML
        from content.video_provider import runway_provider
        from content.models import ContentGeneration

        task_ids = []
        content_ids = []
        total_estimated_time = 0

        for i, prompt in enumerate(prompts):
            logger.info(f"🎬 Generating clip {i+1}/{len(prompts)}: {prompt[:60]}...")

            result = runway_provider.text_to_video(
                prompt=prompt,
                duration=8,  # 8 seconds per clip for professional feel
                quality='veo3.1_fast',
                style='realistic',
                enhance_prompt=True,
                enhancement_level='advanced',
                ratio='1920:1080'
            )

            if not result.success:
                logger.warning(f"⚠️ Clip {i+1} generation failed: {result.error_message}")
                continue

            # Store in database
            content = ContentGeneration.objects.create(
                user=user,
                prompt=prompt,
                system_prompt=f"Brand video for {brand_name} - Clip {i+1}/{len(prompts)}",
                generation_config={
                    'task_id': result.task_id,
                    'duration': 8,
                    'quality': 'veo3.1_fast',
                    'style': style,
                    'type': 'brand_video_clip',
                    'brand_name': brand_name,
                    'clip_number': i + 1,
                    'total_clips': len(prompts),
                    'estimated_time': result.estimated_time,
                    'status': 'processing',
                    'include_branding': include_branding
                }
            )

            task_ids.append(result.task_id)
            content_ids.append(str(content.id))
            total_estimated_time += result.estimated_time

        logger.info(f"✅ Started {len(task_ids)} video generations for {brand_name}")

        return {
            'success': True,
            'brand_name': brand_name,
            'task_ids': task_ids,
            'content_ids': content_ids,
            'prompts': prompts,
            'video_count': len(task_ids),
            'estimated_time': total_estimated_time,
            'include_branding': include_branding,
            'message': f'Started generating {len(task_ids)} video clips for {brand_name}. Videos will appear in your gallery when ready. Once complete, you can chain them together with transitions and branding!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_create_brand_video: {str(e)}")
        raise


def _execute_chain_videos(user, parameters):
    """
    Execute video chaining via DaVinci Resolve
    Session 71: AI Assistant integration for video chaining!

    This guides the user to chain their videos together:
    1. Gets the user's most recent videos from gallery
    2. Returns video IDs and instructions
    3. Frontend auto-selects videos and opens chain modal

    Parameters:
        video_count (int): Number of videos to chain (default: 2)
        transition_type (str): Transition style (default: 'Cross Dissolve')
        add_transitions (bool): Add transitions (default: true)
        project_name (str): Optional project name

    Returns:
        dict: {
            'success': True,
            'video_ids': ['id1', 'id2', ...],
            'video_count': 2,
            'transition_type': 'Cross Dissolve',
            'message': 'Ready to chain 2 videos...'
        }
    """
    try:
        from content.models import VideoHistory

        video_count = parameters.get('video_count', 2)
        transition_type = parameters.get('transition_type', 'Cross Dissolve')
        add_transitions = parameters.get('add_transitions', True)
        project_name = parameters.get('project_name', None)

        # Validate video_count
        if video_count < 2:
            raise ValueError("Need at least 2 videos to chain")
        if video_count > 10:
            logger.warning(f"⚠️ video_count {video_count} is high, limiting to 10")
            video_count = 10

        logger.info(f"🎬 AI Assistant chain_videos: {video_count} videos, {transition_type} transitions")

        # Get user's most recent completed videos
        recent_videos = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at')[:video_count]

        if recent_videos.count() < video_count:
            available_count = recent_videos.count()
            return {
                'success': False,
                'error': f'You only have {available_count} completed videos in your gallery. Need {video_count} videos to chain.',
                'available_count': available_count,
                'requested_count': video_count,
                'message': f'Please create more videos first, or try chaining {available_count} videos instead.'
            }

        # Get video IDs and URLs
        video_ids = [str(v.id) for v in recent_videos]
        video_urls = []
        video_prompts = []

        for v in recent_videos:
            # Get video URL (either external CDN or local media)
            if v.video_url:
                video_urls.append(v.video_url)
            else:
                logger.warning(f"⚠️ Video {v.id} has no video_url")

            video_prompts.append(v.prompt[:100] if v.prompt else "Untitled video")

        logger.info(f"✅ Found {len(video_ids)} videos for chaining: {video_ids}")

        # Calculate estimated duration
        total_duration = sum([v.duration or 8 for v in recent_videos])

        return {
            'success': True,
            'video_ids': video_ids,
            'video_urls': video_urls,
            'video_prompts': video_prompts,
            'video_count': len(video_ids),
            'transition_type': transition_type,
            'add_transitions': add_transitions,
            'project_name': project_name or f"AI Chained Video {len(video_ids)} clips",
            'total_duration': total_duration,
            'message': f'🎬 Ready to chain {len(video_ids)} videos together! Your {video_count} most recent videos have been selected. The chained video will be approximately {total_duration} seconds long with {transition_type} transitions.',
            'instructions': 'The videos have been auto-selected in your gallery. Click the "Chain Videos" button to create your final video!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_chain_videos: {str(e)}")
        raise


def _execute_add_text_to_video(user, parameters):
    """
    Execute text overlay addition to video via DaVinci Resolve
    Session 72: AI Assistant integration for text overlays!

    This adds text to a user's video with perfect spelling:
    1. Gets the user's most recent video (or lets them select)
    2. Creates new DaVinci project with that video
    3. Adds text overlay with specified parameters
    4. Renders final video with text

    Parameters:
        text (str): Text to display (REQUIRED)
        position (str): 'center', 'lower_third', or 'upper_third' (default: 'center')
        start_second (float): When to start text (default: 0)
        duration (float): How long to show text (default: 3)
        font_size (int): Text size 36-144 (default: 72)
        video_selection (str): 'last' or 'recent' (default: 'last')

    Returns:
        dict: {
            'success': True,
            'video_id': 'id',
            'text': 'Welcome',
            'message': 'Ready to add text overlay...'
        }
    """
    try:
        from content.models import VideoHistory

        text = parameters.get('text', '').strip()
        if not text:
            raise ValueError("Text is required for overlay")

        position = parameters.get('position', 'center')
        start_second = parameters.get('start_second', 0)
        duration = parameters.get('duration', 3)
        font_size = parameters.get('font_size', 72)
        video_selection = parameters.get('video_selection', 'last')

        logger.info(f"📝 AI Assistant add_text_to_video: '{text}' at {position}, {start_second}s-{start_second+duration}s")

        # Get user's most recent completed video
        recent_video = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()

        if not recent_video:
            return {
                'success': False,
                'error': 'You have no completed videos in your gallery.',
                'message': 'Please create a video first, then add text to it!'
            }

        logger.info(f"✅ Found video for text overlay: {recent_video.id} - {recent_video.prompt[:50]}")

        return {
            'success': True,
            'video_id': str(recent_video.id),
            'video_url': recent_video.video_url,
            'video_prompt': recent_video.prompt[:100] if recent_video.prompt else "Untitled video",
            'text': text,
            'position': position,
            'start_second': start_second,
            'duration': duration,
            'font_size': font_size,
            'message': f'📝 Ready to add text overlay "{text}" to your video! The text will appear at {position} starting at {start_second} seconds for {duration} seconds.',
            'instructions': f'This will create a NEW video with the text "{text}" overlaid on your {recent_video.prompt[:30] if recent_video.prompt else "video"}. The text will be spelled PERFECTLY (no AI text rendering issues!) using DaVinci Resolve. Click confirm to proceed!',
            'note': '⚠️ Note: This creates a new video with text overlay. Your original video remains unchanged.'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_add_text_to_video: {str(e)}")
        raise


def _execute_add_music_to_video(user, parameters):
    """
    Execute background music addition to video via DaVinci Resolve
    Session 72: AI Assistant integration for audio mixing!
    Session 81: Added support for audio_url from generated audio!

    This adds background music to a user's video:
    1. Gets the user's most recent video (or lets them select)
    2. If audio_url provided: Use that audio directly (from generate_speech/generate_sound_effect)
    3. If no audio_url: User uploads audio file or selects from library
    4. Creates new DaVinci project with video + audio
    5. Renders final video with mixed audio

    Parameters:
        video_selection (str): 'last' or 'recent' (default: 'last')
        audio_url (str): URL of generated audio (optional, Session 81)
        audio_volume (float): Volume 0.0-1.0 (default: 0.3)
        music_style (str): Style preference (default: 'cinematic')

    Returns:
        dict: {
            'success': True,
            'video_id': 'id',
            'audio_url': 'url' (if provided),
            'audio_volume': 0.3,
            'message': 'Ready to add music...'
        }
    """
    try:
        from content.models import VideoHistory

        video_selection = parameters.get('video_selection', 'last')
        audio_url = parameters.get('audio_url')  # Session 81: Optional audio URL
        audio_volume = parameters.get('audio_volume', 0.3)
        music_style = parameters.get('music_style', 'cinematic')

        # Validate volume
        audio_volume = max(0.0, min(1.0, audio_volume))

        logger.info(f"🎵 AI Assistant add_music_to_video: volume={audio_volume}, style={music_style}, audio_url={'provided' if audio_url else 'none'}")

        # Get user's most recent completed video
        recent_video = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at').first()

        if not recent_video:
            return {
                'success': False,
                'error': 'You have no completed videos in your gallery.',
                'message': 'Please create a video first, then add music to it!'
            }

        logger.info(f"✅ Found video for audio mixing: {recent_video.id} - {recent_video.prompt[:50]}")

        # Session 81: If audio_url is provided, we can proceed directly (no upload needed)
        # Session 83: EXECUTE IMMEDIATELY instead of returning confirmation!
        if audio_url:
            logger.info(f"🎵 Session 83: Audio URL provided, executing mixing immediately...")

            # Call VideoAgent to actually mix the audio
            from core.agents import VideoAgent

            video_agent = VideoAgent(user=user)
            result = video_agent.add_music_to_video(
                video_selection='last',
                audio_url=audio_url,
                audio_volume=audio_volume
            )

            # Session 83: Return the actual mixed video result, not confirmation
            if result.get('success'):
                logger.info(f"✅ Session 83: Audio mixing executed successfully!")
                return {
                    'success': True,
                    'video_url': result.get('video_url'),
                    'video_id': result.get('video_id', str(recent_video.id)),
                    'audio_volume': audio_volume,
                    'music_style': 'custom audio',  # Since we used provided audio
                    'video_prompt': result.get('video_prompt', recent_video.prompt[:100] if recent_video.prompt else "Untitled video"),
                    'message': f'✅ Audio successfully added to video!',
                    'instructions': f'The video has been rendered with audio at {int(audio_volume * 100)}% volume.',
                    'note': '🎬 Your new video is ready in the Video Gallery!'
                }
            else:
                logger.error(f"❌ Session 83: Audio mixing failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Audio mixing failed'),
                    'message': '❌ Failed to mix audio with video',
                    'instructions': 'Please check the logs for details.'
                }
        else:
            # No audio_url provided - require manual upload (original behavior)
            return {
                'success': True,
                'video_id': str(recent_video.id),
                'video_url': recent_video.video_url,
                'video_prompt': recent_video.prompt[:100] if recent_video.prompt else "Untitled video",
                'audio_volume': audio_volume,
                'music_style': music_style,
                'message': f'🎵 Ready to add {music_style} background music to your video! Volume will be set to {int(audio_volume * 100)}%.',
                'instructions': f'This will create a NEW video with background music mixed into your {recent_video.prompt[:30] if recent_video.prompt else "video"}. You\'ll need to upload an audio file (MP3, WAV, etc.) or select from your audio library. The music will be mixed at {int(audio_volume * 100)}% volume. Click confirm and upload your audio file!',
                'note': '⚠️ Note: This creates a new video with mixed audio. Your original video remains unchanged.',
                'requires_audio_upload': True  # Frontend should show audio file upload dialog
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_add_music_to_video: {str(e)}")
        raise


def _execute_apply_color_grade(user, parameters):
    """
    Execute color grading application to video via DaVinci Resolve
    Session 72: AI Assistant integration for color grading!
    Session 84: Enhanced with VideoAgent DaVinci method - NOW ACTUALLY EXECUTES!

    This applies professional color grading to a user's video:
    1. Gets the user's most recent video (or lets them select)
    2. Calls VideoAgent to create DaVinci project
    3. Applies specified color grading style
    4. Renders final video with enhanced colors
    5. Returns the actual color-graded video!

    Parameters:
        style (str): Color grading style (default: 'cinematic')
        video_selection (str): 'last' or 'video_id' (default: 'last')
        video_id (str): Video ID if video_selection is 'video_id'
        intensity (float): Color grade intensity 0.0-1.0 (default: 0.5)

    Returns:
        dict: {
            'success': True,
            'video_id': 'new_video_id',
            'video_url': 'url',
            'style': 'cinematic',
            'intensity': 0.5,
            'message': 'Color grade applied!'
        }
    """
    try:
        from content.models import VideoHistory
        from core.agents import VideoAgent

        # Get parameters
        style = parameters.get('style', 'cinematic').lower()
        video_selection = parameters.get('video_selection', 'last')
        video_id = parameters.get('video_id')
        intensity = parameters.get('intensity', 0.5)

        # Session 84: Map old style names to new ones for backwards compatibility
        style_mappings = {
            'cinematic_warm': 'warm',
            'cinematic_cool': 'cool',
            'somatic': 'cinematic',
            'somatic warm': 'warm',
            'sim-matic': 'cinematic',
            'blue': 'cool',
            'retro': 'vintage',
            'film': 'vintage',
            'modern': 'vibrant',
            'clean': 'vibrant',
            'high_contrast': 'noir',
            'dramatic': 'noir',
            'bold': 'vibrant',
            'soft': 'warm',
            'muted': 'vintage',
            'gentle': 'warm',
            'colorful': 'vibrant',
            'saturated': 'vibrant'
        }

        # Map style or use as-is if it's already a valid new style
        valid_styles = ['cinematic', 'vibrant', 'vintage', 'noir', 'warm', 'cool']
        if style not in valid_styles:
            style = style_mappings.get(style, 'cinematic')

        # Ensure intensity is in range
        intensity = max(0.0, min(1.0, intensity))

        logger.info(f"🎨 AI Assistant apply_color_grade: style={style}, intensity={intensity}")

        # Get video
        if video_selection == 'video_id' and video_id:
            try:
                video = VideoHistory.objects.get(id=video_id, user=user, status='completed')
            except VideoHistory.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Video not found: {video_id}',
                    'message': 'The specified video was not found.'
                }
        else:
            # Get most recent video
            video = VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at').first()

            if not video:
                return {
                    'success': False,
                    'error': 'You have no completed videos in your gallery.',
                    'message': 'Please create a video first, then apply color grading to it!'
                }

        logger.info(f"✅ Found video for color grading: {video.id} - {video.prompt[:50]}")

        # Session 84: ACTUALLY EXECUTE COLOR GRADING using VideoAgent!
        logger.info(f"🎬 Session 84: Executing color grading with VideoAgent...")

        video_agent = VideoAgent(user=user)
        result = video_agent.apply_color_grade_davinci(
            video_id=str(video.id),
            style=style,
            intensity=intensity
        )

        # Return result
        if result.get('success'):
            logger.info(f"✅ Session 84: Color grading executed successfully!")
            return {
                'success': True,
                'video_id': result.get('video_id'),
                'video_url': result.get('video_url'),
                'style': style,
                'intensity': intensity,
                'original_video': str(video.id),
                'message': result.get('message', f'✅ {style.capitalize()} color grade applied successfully!'),
                'instructions': f'Your video has been color graded with a professional {style} look at {int(intensity * 100)}% intensity!',
                'note': '🎬 Your new color-graded video is ready in the Video Gallery!'
            }
        else:
            logger.error(f"❌ Session 84: Color grading failed: {result.get('error')}")
            # Session 84: Include all fields even in error response so frontend doesn't crash
            style_descriptions = {
                'cinematic': 'Teal & orange Hollywood look',
                'vibrant': 'Boosted saturation and vivid colors',
                'vintage': 'Retro film aesthetic',
                'noir': 'High contrast black & white',
                'warm': 'Golden hour glow',
                'cool': 'Blue tones and icy feel'
            }
            return {
                'success': False,
                'error': result.get('error', 'Color grading failed'),
                'error_message': result.get('error', 'Color grading failed'),
                'message': '❌ Failed to apply color grade',
                'instructions': 'Please check the logs for details. DaVinci Resolve Studio must be running.',
                'style': style,
                'style_description': style_descriptions.get(style, 'Professional color grading'),
                'video_prompt': video.prompt[:50] if video.prompt else 'Unknown video',
                'video_id': str(video.id)
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_apply_color_grade: {str(e)}", exc_info=True)
        raise


def _execute_edit_video(user, parameters):
    """
    Execute multi-operation video editing via DaVinci Resolve
    Session 84: Master orchestrator for complex video editing workflows!

    This performs multiple editing operations in sequence:
    - Chain videos together with transitions
    - Add text overlays
    - Apply color grading
    - Mix audio/music

    Parameters:
        video_selection (str): 'last', 'last_2', 'last_3', etc.
        operations (list): List of operation dicts with 'type' and parameters
        project_name (str): Optional project name

    Returns:
        dict: {
            'success': True,
            'video_id': 'new_video_id',
            'video_url': 'url',
            'operations_applied': 4,
            'duration': 24.0,
            'message': 'Video edited successfully!'
        }
    """
    try:
        from content.models import VideoHistory
        from core.agents import VideoAgent

        # Get parameters
        video_selection = parameters.get('video_selection', 'last')
        operations = parameters.get('operations', [])
        project_name = parameters.get('project_name')
        provided_video_ids = parameters.get('video_ids', [])
        video_numbers = parameters.get('video_numbers', [])  # Session 84: NEW! Support for video numbers

        # Validate operations
        if not operations or len(operations) == 0:
            return {
                'success': False,
                'error': 'No operations specified',
                'message': 'Please specify at least one editing operation (chain, text, color_grade, or audio).'
            }

        logger.info(f"🎬 AI Assistant edit_video: {len(operations)} operations on {video_selection}")

        # Session 84: Handle video numbers (e.g., "chain videos 5 and 8")
        if video_numbers and len(video_numbers) > 0:
            logger.info(f"📹 Converting video numbers to IDs: {video_numbers}")

            # Get all completed videos ordered by creation date (most recent first)
            all_videos = list(VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at'))

            if len(all_videos) == 0:
                return {
                    'success': False,
                    'error': 'No videos found',
                    'message': 'You have no completed videos yet.'
                }

            # Convert video numbers to IDs (numbers are 1-indexed in UI)
            video_ids = []
            for num in video_numbers:
                # Convert to 0-indexed array position
                idx = num - 1

                if idx < 0 or idx >= len(all_videos):
                    return {
                        'success': False,
                        'error': f'Video number {num} out of range',
                        'message': f'Video {num} does not exist. You have {len(all_videos)} videos.'
                    }

                video_ids.append(str(all_videos[idx].id))

            logger.info(f"✅ Converted numbers {video_numbers} to IDs: {video_ids}")

        # Session 84: Handle specific video IDs (for numbered references)
        elif video_selection == 'specific_ids' and provided_video_ids:
            logger.info(f"📹 Using specific video IDs: {provided_video_ids}")
            video_ids = provided_video_ids

            # Validate that these videos exist
            videos = VideoHistory.objects.filter(
                id__in=video_ids,
                user=user,
                status='completed'
            )

            if videos.count() != len(video_ids):
                return {
                    'success': False,
                    'error': f'Some video IDs not found. Found {videos.count()}, expected {len(video_ids)}',
                    'message': 'Some of the specified videos were not found or are not completed yet.'
                }
        else:
            # Parse video_selection to get count
            if video_selection == 'last':
                video_count = 1
            elif video_selection.startswith('last_'):
                try:
                    video_count = int(video_selection.split('_')[1])
                except (IndexError, ValueError):
                    video_count = 1
            else:
                video_count = 1

            # Get videos
            videos = VideoHistory.objects.filter(
                user=user,
                status='completed'
            ).order_by('-created_at')[:video_count]

            if videos.count() < video_count:
                return {
                    'success': False,
                    'error': f'Not enough videos. Found {videos.count()}, need {video_count}',
                    'message': f'You only have {videos.count()} completed videos. Please create more videos first.'
                }

            video_ids = [str(v.id) for v in videos]

        logger.info(f"✅ Found {len(video_ids)} videos for editing: {video_ids}")

        # Session 84: EXECUTE VIDEO EDITING using VideoAgent!
        logger.info(f"🎬 Session 84: Executing multi-operation edit with VideoAgent...")

        video_agent = VideoAgent(user=user)
        result = video_agent.create_edited_video(
            video_ids=video_ids,
            operations=operations,
            project_name=project_name
        )

        # Return result
        if result.get('success'):
            logger.info(f"✅ Session 84: Multi-operation edit executed successfully!")

            # Build operation summary
            op_types = [op.get('type', 'unknown') for op in operations]
            op_summary = ', '.join(op_types)

            return {
                'success': True,
                'video_id': result.get('video_id'),
                'video_url': result.get('video_url'),
                'operations_applied': result.get('operations_applied', len(operations)),
                'duration': result.get('duration'),
                'project_name': result.get('project_name'),
                'video_count': len(video_ids),
                'operations_summary': op_summary,
                'message': result.get('message', f'✅ Video edited successfully with {result.get("operations_applied")} operations!'),
                'instructions': f'Your video has been edited with {result.get("operations_applied")} operations: {op_summary}',
                'note': '🎬 Your new edited video is ready in the Video Gallery!'
            }
        else:
            logger.error(f"❌ Session 84: Video editing failed: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error', 'Video editing failed'),
                'operations_applied': result.get('operations_applied', 0),
                'message': '❌ Failed to edit video',
                'instructions': 'Please check the logs for details. DaVinci Resolve Studio must be running.'
            }

    except Exception as e:
        logger.error(f"❌ Error in _execute_edit_video: {str(e)}", exc_info=True)
        raise


def _execute_show_recent_videos(user, parameters):
    """
    Show user's recent videos with numbers for easy reference
    Session 84: Video selection enhancement!

    Parameters:
        count (int): Number of videos to show (default: 10, max: 20)

    Returns:
        dict: {
            'success': True,
            'videos': [list of video info],
            'message': 'Here are your recent videos...'
        }
    """
    try:
        from content.models import VideoHistory

        # Get parameters
        count = min(int(parameters.get('count', 10)), 20)  # Max 20

        logger.info(f"📹 Showing {count} recent videos for user {user.username}")

        # Get recent completed videos
        videos = VideoHistory.objects.filter(
            user=user,
            status='completed'
        ).order_by('-created_at')[:count]

        if videos.count() == 0:
            return {
                'success': True,
                'videos': [],
                'count': 0,
                'message': "📹 **No Videos Yet**\n\nYou haven't created any videos yet! Try generating one first.",
                'instructions': 'Use commands like "generate a video of mountains" to create your first video!'
            }

        # Build video list with numbers
        video_list = []
        message_lines = [f"📹 **Your Recent Videos** ({videos.count()} found):\n"]

        for idx, video in enumerate(videos, 1):
            # Emoji based on video type
            type_emoji = {
                'text_to_video': '🎬',
                'image_to_video': '🖼️',
                'video_to_video': '🔄',
                'extended': '⏱️',
                'chained': '🔗',
                'color_graded': '🎨',
                'text_overlay': '📝',
                'multi_edit': '✨',
                'upscaled': '⬆️'
            }.get(video.video_type, '🎥')

            # Clean up prompt
            prompt_text = video.prompt[:60] if video.prompt else "Untitled video"
            if len(video.prompt or '') > 60:
                prompt_text += "..."

            # Add to message
            message_lines.append(f"**{idx}.** {type_emoji} {prompt_text}")

            # Add to video list for reference
            video_list.append({
                'number': idx,
                'id': str(video.id),
                'prompt': video.prompt,
                'video_type': video.video_type,
                'duration': video.duration,
                'url': video.video_url
            })

        message = "\n".join(message_lines)
        message += "\n\n💡 **How to use:**\n"
        message += "• \"Chain videos 3 and 4\"\n"
        message += "• \"Make video 2 cinematic\"\n"
        message += "• \"Chain the snowboarder and eagle videos\""

        logger.info(f"✅ Displayed {len(video_list)} videos")

        # Store video list in session for number-based reference
        # We'll use this in the next step when implementing number-based selection

        return {
            'success': True,
            'videos': video_list,
            'count': len(video_list),
            'message': message,
            'instructions': 'You can now reference these videos by number or description!'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_show_recent_videos: {str(e)}", exc_info=True)
        raise


def _execute_create_character_from_prompt(user, parameters):
    """
    Execute character training set generation from natural language
    Session 74: AI-powered character training integration!

    This generates multiple image variations and creates a trainable character:
    1. Parse character description and style
    2. Generate 5-7 image variations with different angles/poses
    3. Download generated images
    4. Create character model and submit for training
    5. Return status with training progress

    Parameters:
        character_description (str): Description of character/logo (REQUIRED)
        character_name (str): Name for this character model (optional, derived from description)
        trigger_word (str): Trigger word for prompts (default: 'TOK')
        variation_count (int): Number of variations to generate 5-7 (default: 6)
        style (str): Visual style (pixar, anime, realistic, cartoon, minimalist, professional)

    Returns:
        dict: {
            'success': True,
            'character_id': 123,
            'character_name': 'Robotics Donkey',
            'trigger_word': 'TOK',
            'images_generated': 6,
            'training_status': 'preparing',
            'message': 'Character training set generated! Training will take 30-60 minutes.'
        }
    """
    try:
        import requests
        from django.core.files.uploadedfile import SimpleUploadedFile
        from content.character_training import create_character_workflow
        from content.image_generation import ImageGenerationService

        # Extract parameters
        character_description = parameters.get('character_description', '').strip()
        character_name = parameters.get('character_name', '').strip()
        trigger_word = parameters.get('trigger_word', 'TOK').strip().upper()
        variation_count = parameters.get('variation_count', 6)
        style = parameters.get('style', '').strip().lower()

        # Validate required parameters
        if not character_description:
            raise ValueError("character_description is required")

        # Derive character name from description if not provided
        if not character_name:
            # Take first 3-5 words and capitalize
            words = character_description.split()[:4]
            character_name = ' '.join(words).title()

        # Validate variation_count (5-7)
        if variation_count < 5:
            logger.warning(f"⚠️ variation_count {variation_count} too low, setting to 5")
            variation_count = 5
        elif variation_count > 7:
            logger.warning(f"⚠️ variation_count {variation_count} too high, setting to 7")
            variation_count = 7

        # Extract or default style
        if not style or style == 'professional':
            # Try to extract style from description
            style_keywords = ['pixar', 'anime', 'realistic', 'cartoon', 'minimalist', '3d', '2d', 'watercolor', 'oil painting']
            for keyword in style_keywords:
                if keyword in character_description.lower():
                    style = keyword
                    break
            if not style:
                style = 'professional'

        logger.info(f"🎨 Creating character training set:")
        logger.info(f"   Character: {character_name}")
        logger.info(f"   Description: {character_description}")
        logger.info(f"   Trigger word: {trigger_word}")
        logger.info(f"   Variations: {variation_count}")
        logger.info(f"   Style: {style}")

        # Create prompt variations for different angles/poses/contexts
        prompt_variations = [
            f"{character_description}, {style} style, front view, centered, well-lit, professional photography",
            f"{character_description}, {style} style, side profile view, clear details, studio lighting",
            f"{character_description}, {style} style, three-quarter angle, dynamic pose, professional composition",
            f"{character_description}, {style} style, different angle, varied expression, high quality",
            f"{character_description}, {style} style, close-up detail shot, sharp focus, professional",
            f"{character_description}, {style} style, full body view, different background, cinematic lighting",
            f"{character_description}, {style} style, alternate pose, varied composition, professional quality"
        ]

        # Use only the number of variations requested
        prompt_variations = prompt_variations[:variation_count]

        logger.info(f"📸 Generating {len(prompt_variations)} training images...")

        # Initialize Image Generation Service
        service = ImageGenerationService()

        if not service.stability_key:
            raise ValueError("Stability AI is not available. Please check STABILITY_API_KEY configuration.")

        # Generate images and download them
        temp_files = []
        generated_images = []

        for i, prompt in enumerate(prompt_variations):
            logger.info(f"   Generating image {i+1}/{len(prompt_variations)}: {prompt[:60]}...")

            # Generate image with Stability AI (using sd3 for consistency)
            result = service.generate_image(
                prompt=prompt,
                provider='stability',
                model='sd3',  # SD3 for good quality and consistency
                size='1024x1024',
                cfg_scale=7,  # Moderate adherence to prompt
                steps=40  # Good quality
            )

            if not result.success:
                logger.warning(f"⚠️ Image {i+1} generation failed: {result.error_message}")
                continue

            if not result.images or len(result.images) == 0:
                logger.warning(f"⚠️ Image {i+1} has no URL")
                continue

            # Get image data (handle both URLs and base64 data URIs)
            image_url = result.images[0]
            logger.info(f"   Processing image {i+1}...")

            if image_url.startswith('data:image'):
                # Base64 data URI - decode directly
                import base64
                # Extract base64 data after the comma
                base64_data = image_url.split(',', 1)[1]
                image_content = base64.b64decode(base64_data)
                logger.info(f"   Decoded base64 image {i+1}")
            else:
                # HTTP URL - download
                logger.info(f"   Downloading image {i+1} from URL...")
                img_response = requests.get(image_url, timeout=30)

                if img_response.status_code != 200:
                    logger.warning(f"⚠️ Failed to download image {i+1}")
                    continue

                image_content = img_response.content

            # Create SimpleUploadedFile for Django
            filename = f"character_training_{i+1}.png"
            uploaded_file = SimpleUploadedFile(
                name=filename,
                content=image_content,
                content_type='image/png'
            )

            generated_images.append(uploaded_file)
            logger.info(f"✅ Image {i+1} downloaded and ready")

        if len(generated_images) < 5:
            raise ValueError(f"Not enough images generated: {len(generated_images)}/5 minimum required")

        logger.info(f"✅ Generated {len(generated_images)} training images successfully!")

        # Create character with workflow
        logger.info(f"📝 Creating character model and submitting for training...")

        character, warnings = create_character_workflow(
            user=user,
            name=character_name,
            description=character_description,
            trigger_word=trigger_word,
            image_files=generated_images,
            training_steps=1000,  # Standard training steps
            learning_rate=0.0004,  # Standard learning rate
            auto_submit=False  # Wait for user review and approval!
        )

        logger.info(f"🎉 Character training set created! ID: {character.id}")
        logger.info(f"   Training Status: {character.training_status}")

        # Get training images for preview
        training_images = character.training_images.all().order_by('order')
        training_images_data = [
            {
                'id': img.id,
                'url': img.image.url if img.image else None,
                'order': img.order,
                'width': img.width,
                'height': img.height,
                'file_size': img.file_size
            }
            for img in training_images
        ]

        return {
            'success': True,
            'character_id': character.id,
            'character_name': character.name,
            'description': character.description,
            'trigger_word': character.trigger_word,
            'images_generated': len(generated_images),
            'training_images_count': character.training_images_count,
            'training_status': character.training_status,
            'training_images': training_images_data,
            'warnings': warnings,
            'estimated_time_minutes': 45,  # FLUX LoRA training takes 30-60 minutes
            'message': f'🎉 Generated {len(generated_images)} training images for "{character_name}"! Review them below. You can edit any images or say "These look perfect" to start training.',
            'instructions': f'Review your training images below. If you want to edit any, just say "Make the ears bigger on image 3" or similar. When ready, say "These look perfect, train it!" to start the 30-60 minute training process.',
            'next_action': 'review',  # Frontend should show review UI
            'next_steps': [
                'Review the generated training images',
                'Edit images if needed (optional)',
                'Say "These look perfect, train it!" to start training',
                f'After training, use "{trigger_word}" in your prompts!'
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_create_character_from_prompt: {str(e)}")
        raise


def _execute_edit_character_training_image(user, parameters):
    """
    Edit a specific character training image with natural language instructions

    Session 75: Image editing workflow for character training

    Workflow:
    1. Get character and specified image
    2. Get original prompt/description from character
    3. Apply edit instruction to prompt
    4. Generate new image with edited prompt
    5. Download and replace old image
    6. Update database
    7. Return updated character with all images

    Parameters:
        character_id (int): ID of character model
        image_number (int): Which image to edit (1-7)
        edit_instruction (str): Natural language edit
        apply_to_all (bool): Apply to all images (default: False)

    Returns:
        dict: Updated character data with all training images
    """
    try:
        from content.models import CharacterModel, CharacterTrainingImage

        character_id = parameters.get('character_id')
        image_number = parameters.get('image_number')
        edit_instruction = parameters.get('edit_instruction', '').strip()
        apply_to_all = parameters.get('apply_to_all', False)
        reference_image_number = parameters.get('reference_image_number')
        strength = parameters.get('strength', 0.65)  # Default: preserve reference structure moderately

        logger.info(f"✏️ Editing training image - character_id: {character_id}, image #{image_number}")
        logger.info(f"   Edit: '{edit_instruction}'")
        logger.info(f"   Apply to all: {apply_to_all}")
        if reference_image_number is not None:
            logger.info(f"   🎨 Using image #{reference_image_number} as reference (strength: {strength})")

        # Get character and verify ownership
        if character_id:
            try:
                character = CharacterModel.objects.get(id=character_id, user=user)
                logger.info(f"✅ Using specified character: {character.id} - {character.name}")
            except CharacterModel.DoesNotExist:
                logger.warning(f"⚠️ Character {character_id} not found, trying most recent character...")
                character = None
        else:
            logger.info(f"ℹ️ No character_id provided, using most recent character...")
            character = None

        # If character not found or not provided, use most recent
        if not character:
            character = CharacterModel.objects.filter(
                user=user,
                training_status='pending'  # Only pending (not yet submitted)
            ).order_by('-created_at').first()

            if not character:
                # If no pending characters, just get the most recent one
                character = CharacterModel.objects.filter(user=user).order_by('-created_at').first()

            if not character:
                raise ValueError(f"No characters found for editing")

            logger.info(f"✅ Using most recent character: {character.id} - {character.name}")

        # Get images to edit
        if apply_to_all:
            images_to_edit = character.training_images.all().order_by('order')
            logger.info(f"   Editing all {images_to_edit.count()} images")
        else:
            # Get specific image by order number
            try:
                images_to_edit = [character.training_images.get(order=image_number)]
                logger.info(f"   Editing only image #{image_number}")
            except CharacterTrainingImage.DoesNotExist:
                raise ValueError(f"Image #{image_number} not found in character training set")

        # Initialize image generation service
        from content.image_generation import ImageGenerationService
        service = ImageGenerationService()

        # Check Stability AI availability
        if not service.stability_key:
            raise ValueError("Stability AI is not available. Cannot generate edited images.")

        # Get reference image if provided
        reference_image = None
        if reference_image_number is not None:
            try:
                reference_image = character.training_images.get(order=reference_image_number)
                logger.info(f"✅ Found reference image #{reference_image_number}: {reference_image.image.path}")
            except CharacterTrainingImage.DoesNotExist:
                raise ValueError(f"Reference image #{reference_image_number} not found in character training set")

        edited_count = 0
        for training_image in images_to_edit:
            # Build edited prompt based on original character description
            base_prompt = f"{character.description}, professional photography"

            # Add angle/pose variation based on image order
            angle_variations = {
                1: "front view, centered, well-lit",
                2: "side profile view, clear details",
                3: "three-quarter angle, dynamic pose",
                4: "different angle, varied expression",
                5: "close-up detail shot, sharp focus",
                6: "full body view, different background",
                7: "alternate pose, varied composition"
            }
            angle_desc = angle_variations.get(training_image.order, "professional composition")

            # Combine: base + angle + edit instruction
            edited_prompt = f"{base_prompt}, {angle_desc}, {edit_instruction}"

            # Check if we should use image-to-image with reference
            if reference_image:
                logger.info(f"   🎨 Generating image #{training_image.order} using image-to-image from reference #{reference_image_number}")
                logger.info(f"      Prompt: '{edited_prompt[:100]}...'")
                logger.info(f"      Strength: {strength} (lower = more like reference)")

                # Use image-to-image with reference image
                result = service.image_to_image(
                    base_image=reference_image.image.path,
                    prompt=edited_prompt,
                    strength=strength,
                    model='sd3',
                    provider='stability'
                )
            else:
                logger.info(f"   Generating edited image #{training_image.order} with prompt: '{edited_prompt[:100]}...'")

                # Generate new image from scratch
                result = service.generate_image(
                    provider='stability',
                    model='sd3',
                    prompt=edited_prompt,
                    width=1024,
                    height=1024,
                    user=user,
                    save_to_history=False  # Don't clutter history with training images
                )

            # Get image data (handle both URLs and base64 data URIs)
            import requests
            import base64
            from django.core.files.base import ContentFile

            image_url = result.images[0]

            if image_url.startswith('data:image'):
                # Base64 data URI - decode directly
                logger.info(f"   Decoding base64 image...")
                base64_data = image_url.split(',', 1)[1]
                image_content = base64.b64decode(base64_data)
            else:
                # HTTP URL - download
                logger.info(f"   Downloading image from URL...")
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                image_content = img_response.content

            # Replace the old image file
            old_filename = training_image.original_filename
            training_image.image.save(
                old_filename,
                ContentFile(image_content),
                save=False
            )

            # Update metadata
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_content))
            training_image.width = img.width
            training_image.height = img.height
            training_image.file_size = len(image_content)
            training_image.validation_notes = f"Edited: {edit_instruction}"
            training_image.save()

            edited_count += 1
            logger.info(f"   ✅ Image #{training_image.order} updated successfully")

        # Get updated training images for response
        training_images = character.training_images.all().order_by('order')
        training_images_data = [
            {
                'id': img.id,
                'url': img.image.url if img.image else None,
                'order': img.order,
                'width': img.width,
                'height': img.height,
                'file_size': img.file_size,
                'validation_notes': img.validation_notes
            }
            for img in training_images
        ]

        logger.info(f"✅ Edited {edited_count} image(s) successfully!")

        return {
            'success': True,
            'character_id': character.id,
            'character_name': character.name,
            'trigger_word': character.trigger_word,
            'edited_count': edited_count,
            'training_images': training_images_data,
            'message': f'✅ Edited {edited_count} image(s) successfully! {edit_instruction.capitalize()}.',
            'instructions': f'Review the updated images. When ready, say "These look perfect, train it!" to start training.',
            'next_action': 'review'  # Show review UI again
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_edit_character_training_image: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def _execute_inpaint(user, parameters):
    """
    Execute inpaint tool to fix/regenerate specific areas of an image
    Perfect for fixing text in logos!

    Session 65: Multi-pass autonomous refinement

    Parameters:
        image_url (str): URL of image to edit
        prompt (str): What to regenerate in the masked area
        mask_description (str): Which area to fix

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL of fixed image',
            'image_id': 'Database ID',
            'original_url': 'Original image URL',
            'prompt': 'Inpaint prompt used'
        }
    """
    try:
        image_url = parameters.get('image_url', '').strip()
        prompt = parameters.get('prompt', '').strip()
        mask_description = parameters.get('mask_description', '').strip()

        if not image_url or not prompt:
            raise ValueError("image_url and prompt are required for inpainting")

        logger.info(f"🖌️ Executor inpainting: {mask_description} -> {prompt[:50]}...")

        # Session 66: Use Stability AI Search and Replace API directly
        import requests
        import uuid
        from django.core.files.base import ContentFile
        from django.core.files.storage import default_storage

        # Handle both absolute URLs and relative paths
        if image_url.startswith('/'):
            # Local path - read from disk
            image_path = image_url.lstrip('/')
            full_path = os.path.join(settings.BASE_DIR, image_path)
            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
        else:
            # Remote URL - download
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content

        # Call Stability AI Search and Replace API
        api_key = os.environ.get('STABILITY_API_KEY')
        api_url = 'https://api.stability.ai/v2beta/stable-image/edit/search-and-replace'

        # Prepare the request
        files = {
            'image': ('image.png', image_data, 'image/png')
        }
        data = {
            'prompt': prompt,
            'search_prompt': mask_description,
            'output_format': 'png'
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'image/*'
        }

        logger.info(f"🖌️ Calling Stability AI Search and Replace...")
        api_response = requests.post(api_url, files=files, data=data, headers=headers)

        if api_response.status_code != 200:
            error_msg = api_response.text
            logger.error(f"❌ Stability AI error: {error_msg}")
            raise Exception(f"Inpaint API failed: {error_msg}")

        # Get the inpainted image data
        result_image_data = api_response.content

        # Save the inpainted image
        image_id = uuid.uuid4()
        filename = f"{user.id}/{image_id}.png"
        filepath = f"generated_images/{filename}"

        # Save to storage
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        saved_url = f"/media/{saved_path}"

        # Save to ImageHistory
        from content.models import ImageHistory
        history_record = ImageHistory.objects.create(
            user=user,
            prompt=f"Inpaint: {prompt}",
            image_url=saved_url,
            image_type='inpaint',
            model_used='sdxl',
            style='inpaint',
            image_width=1024,
            image_height=1024
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=history_record,
                project=None,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ history_record.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Executor inpaint complete: {saved_url}")

        return {
            'success': True,
            'image_url': saved_url,
            'image_id': history_record.id,
            'original_url': image_url,
            'prompt': prompt,
            'mask_description': mask_description
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_inpaint: {str(e)}")
        raise


def _execute_resize_image_for_format(user, parameters):
    """
    Session 182: Resize/adapt an image for different social media formats.

    This creates a new image by resizing and/or cropping the source image
    to fit the target dimensions while maintaining the visual content.

    Parameters:
        source_image_id (str): UUID of the source image
        target_width (int): Target width in pixels
        target_height (int): Target height in pixels
        format_name (str): Optional name for the format (e.g., "banner", "avatar")
        fit_mode (str): "cover" (crop to fill), "contain" (fit within), "stretch"
        project_id (str): Optional project to associate with

    Returns:
        dict: {
            'success': True,
            'image_url': 'URL to resized image',
            'image_id': 'History ID',
            'format': 'banner/post/avatar'
        }
    """
    from PIL import Image
    from io import BytesIO
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    from content.models import ImageHistory
    import os

    try:
        # Session 182: Accept both 'image_id' and 'source_image_id' for compatibility
        source_image_id = parameters.get('image_id') or parameters.get('source_image_id')
        target_width = int(parameters.get('target_width', 1080))
        target_height = int(parameters.get('target_height', 1080))
        format_name = parameters.get('format_name', 'resized')
        fit_mode = parameters.get('fit_mode', 'cover')
        project_id = parameters.get('project_id')

        if not source_image_id:
            raise ValueError("image_id or source_image_id is required")

        # Session 182: Support hybrid ID resolution (sequential number or UUID)
        source_image = None
        try:
            # First, try as UUID
            source_image = ImageHistory.objects.get(id=source_image_id, user=user)
        except (ImageHistory.DoesNotExist, ValueError):
            # Try as sequential number (e.g., "7" or "#7")
            try:
                seq_num = int(str(source_image_id).replace('#', '').strip())
                # Get all user's images ordered by creation date
                user_images = ImageHistory.objects.filter(user=user).order_by('created_at')
                if 1 <= seq_num <= user_images.count():
                    source_image = user_images[seq_num - 1]  # Sequential numbers are 1-based
                    logger.info(f"📍 Resolved sequential number #{seq_num} to image {source_image.id}")
            except (ValueError, TypeError):
                pass

        if not source_image:
            raise ValueError(f"Source image {source_image_id} not found")

        # Load the image
        source_path = source_image.file_path
        if source_path.startswith('/'):
            full_path = source_path
        else:
            full_path = os.path.join(settings.MEDIA_ROOT, source_path)

        if not os.path.exists(full_path):
            # Try with default_storage
            if default_storage.exists(source_path):
                with default_storage.open(source_path, 'rb') as f:
                    img = Image.open(f)
                    img.load()
            else:
                raise ValueError(f"Source image file not found: {source_path}")
        else:
            img = Image.open(full_path)

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        original_width, original_height = img.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if fit_mode == 'cover':
            # Crop to fill target dimensions (most common for social media)
            if original_ratio > target_ratio:
                # Image is wider, crop sides
                new_width = int(original_height * target_ratio)
                left = (original_width - new_width) // 2
                img = img.crop((left, 0, left + new_width, original_height))
            else:
                # Image is taller, crop top/bottom
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                img = img.crop((0, top, original_width, top + new_height))
            # Resize to target
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        elif fit_mode == 'contain':
            # Fit within dimensions with padding
            img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
            # Create background and paste centered
            background = Image.new('RGB', (target_width, target_height), (255, 255, 255))
            offset = ((target_width - img.size[0]) // 2, (target_height - img.size[1]) // 2)
            background.paste(img, offset)
            img = background

        else:  # stretch
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        buffer.seek(0)

        # Save to storage
        new_filename = f"generated_images/{user.id}/{format_name}_{uuid.uuid4().hex[:8]}.png"
        file_path = default_storage.save(new_filename, ContentFile(buffer.read()))
        saved_url = default_storage.url(file_path)

        # Get project if specified
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=user)
            except CreativeProject.DoesNotExist:
                pass

        # Session 183: Detect if this is a social media kit image based on format_name
        is_social_media = any(keyword in format_name.lower() for keyword in [
            'social media', 'banner', 'post', 'avatar', 'profile', 'story', 'instagram', 'facebook', 'twitter', 'linkedin'
        ])

        # Save to ImageHistory
        history_record = save_to_history(
            user=user,
            file_path=file_path,
            image_type='social_media' if is_social_media else 'resized',
            prompt=f"Resized for {format_name} ({target_width}x{target_height}) from Image #{source_image.get_sequential_number()}",
            parameters={
                'source_id': str(source_image_id),
                'width': target_width,
                'height': target_height,
                'fit_mode': fit_mode,
                'is_social_media_kit': is_social_media,
                'format_name': format_name
            },
            model_used='PIL',
            style=format_name,
            parent_image=source_image,
            project=project
        )

        logger.info(f"✅ Resized image for {format_name}: {target_width}x{target_height}")

        return {
            'success': True,
            'image_url': saved_url,
            'image_id': str(history_record.id) if history_record else None,
            'format': format_name,
            'dimensions': f"{target_width}x{target_height}"
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_resize_image_for_format: {str(e)}")
        raise


def _execute_web_search(parameters):
    """
    Execute web search tool
    Uses Serper API for Google search

    Session 65: Phase 2.3 - Autonomous web search

    Parameters:
        query (str): Search query

    Returns:
        dict: {
            'success': True,
            'results': [
                {
                    'title': 'Result title',
                    'link': 'URL',
                    'snippet': 'Description'
                },
                ...
            ],
            'query': 'Search query'
        }
    """
    try:
        query = parameters.get('query', '').strip()

        if not query:
            raise ValueError("Query is required for web search")

        logger.info(f"🔍 Executor searching web: {query}")

        # Use Serper API for Google search
        serper_key = os.getenv('SERPER_API_KEY')
        if not serper_key:
            raise Exception("Serper API key not configured")

        # Call Serper API
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": serper_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 5  # Get top 5 results
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract organic search results
        results = []
        organic = data.get('organic', [])
        for item in organic[:5]:  # Top 5 results
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })

        logger.info(f"✅ Executor found {len(results)} search results for '{query}'")

        return {
            'success': True,
            'results': results,
            'query': query
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_web_search: {str(e)}")
        raise


def _execute_scrape_website(parameters):
    """
    Execute website scraping tool
    Simple web scraper to extract text content

    Session 65: Phase 2.4 - Autonomous web scraping

    Parameters:
        url (str): Website URL to scrape

    Returns:
        dict: {
            'success': True,
            'url': 'URL scraped',
            'title': 'Page title',
            'text': 'Extracted text content (first 1000 chars)',
            'links': ['list', 'of', 'links']
        }
    """
    try:
        url = parameters.get('url', '').strip()

        if not url:
            raise ValueError("URL is required for web scraping")

        logger.info(f"🕷️ Executor scraping website: {url}")

        # Simple scraping with requests + basic parsing
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; DonkeyBetzBot/1.0)'
        })
        response.raise_for_status()

        html = response.text

        # Extract title (simple regex)
        import re
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        title = title_match.group(1) if title_match else 'No title'

        # Extract links (simple regex)
        link_matches = re.findall(r'href=["\']([^"\']+)["\']', html)
        links = [link for link in link_matches if link.startswith('http')][:10]  # Top 10 links

        # Extract text (remove HTML tags)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text[:1000]  # First 1000 chars

        logger.info(f"✅ Executor scraped {url}: {len(text)} chars, {len(links)} links")

        return {
            'success': True,
            'url': url,
            'title': title,
            'text': text,
            'links': links
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_scrape_website: {str(e)}")
        raise


def _execute_send_email(user, parameters):
    """
    Execute email sending tool
    Uses Resend API for transactional email

    Session 65: Phase 2.5 - Autonomous email sending

    Parameters:
        to_email (str): Recipient email
        subject (str): Email subject
        body (str): Email body (text or HTML)
        attachments (list): Optional list of attachment URLs

    Returns:
        dict: {
            'success': True,
            'message_id': 'Resend message ID',
            'to': 'recipient@email.com'
        }
    """
    try:
        to_email = parameters.get('to_email', '').strip()
        subject = parameters.get('subject', '').strip()
        body = parameters.get('body', '').strip()

        if not to_email or not subject or not body:
            raise ValueError("to_email, subject, and body are required for email")

        logger.info(f"📧 Executor sending email to: {to_email}")

        # Use Resend API
        resend_key = os.getenv('RESEND_API_KEY')
        if not resend_key:
            raise Exception("Resend API key not configured")

        # Call Resend API
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": "AI Assistant <noreply@donkeybetz.com>",
            "to": [to_email],
            "subject": subject,
            "html": f"<p>{body}</p>"
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        message_id = data.get('id')

        logger.info(f"✅ Executor sent email: {message_id}")

        return {
            'success': True,
            'message_id': message_id,
            'to': to_email
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_send_email: {str(e)}")
        raise


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_workflow_execution(request):
    """
    Create workflow history record when workflow execution starts
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "workflow_type": "logo_creator",
        "workflow_name": "Logo Creator",
        "prompt": "User's prompt",
        "improved_prompt": "AI-improved prompt (optional)",
        "config": {...},  // Workflow configuration
        "input_image_id": 123,  // Optional
        "project_id": "uuid-string"  // Optional - Session 183
    }

    Returns: {"workflow_history_id": 123}
    """
    try:
        from content.models import WorkflowHistory, CreativeProject

        workflow_type = request.data.get('workflow_type', '').strip()
        workflow_name = request.data.get('workflow_name', '').strip()
        prompt = request.data.get('prompt', '').strip()
        improved_prompt = request.data.get('improved_prompt', '').strip()
        config = request.data.get('config', {})
        input_image_id = request.data.get('input_image_id')
        project_id = request.data.get('project_id')  # Session 183: Project association

        if not workflow_type or not workflow_name:
            return Response({
                'error': 'workflow_type and workflow_name are required'
            }, status=400)

        # Session 183: Get project if provided
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found for user {request.user.id}")

        # Create workflow history record
        workflow_history = WorkflowHistory.objects.create(
            user=request.user,
            project=project,  # Session 183: Associate with project
            workflow_type=workflow_type,
            workflow_name=workflow_name,
            prompt=prompt,
            improved_prompt=improved_prompt,
            config=config,
            input_image_id=input_image_id,
            status='running'
        )

        logger.info(f"✅ Started tracking workflow execution: {workflow_history.id} ({workflow_name})")

        return Response({
            'success': True,
            'workflow_history_id': workflow_history.id
        })

    except Exception as e:
        logger.error(f"❌ Error starting workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_workflow_execution(request, workflow_id):
    """
    Update workflow history record when workflow completes
    Session 57: Phase B.2 - Workflow History & Favorites

    Expected JSON:
    {
        "status": "completed" | "failed",
        "execution_time": 12.5,  // seconds
        "result_images": ["url1", "url2"],  // For completed
        "error_message": "Error details"  // For failed
    }
    """
    try:
        from content.models import WorkflowHistory

        workflow = WorkflowHistory.objects.get(
            id=workflow_id,
            user=request.user
        )

        status = request.data.get('status', '').strip().lower()
        execution_time = float(request.data.get('execution_time', 0))

        if status == 'completed':
            result_images = request.data.get('result_images', [])
            workflow.mark_completed(execution_time, result_images)
            logger.info(f"✅ Completed workflow execution: {workflow.id} ({workflow.workflow_name}) - {len(result_images)} results")

        elif status == 'failed':
            error_message = request.data.get('error_message', 'Unknown error')
            workflow.mark_failed(error_message)
            workflow.execution_time = execution_time
            workflow.save(update_fields=['execution_time'])
            logger.error(f"❌ Failed workflow execution: {workflow.id} ({workflow.workflow_name}) - {error_message}")

        else:
            return Response({
                'error': 'status must be "completed" or "failed"'
            }, status=400)

        return Response({
            'success': True,
            'workflow_history_id': workflow.id,
            'status': workflow.status
        })

    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error completing workflow execution: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 60: PHASE C.1.2 - PROJECT MANAGEMENT API ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def list_projects(request):
    """
    List all creative projects for current user
    Session 60: Phase C.1.2 - Project Management API
    Session 350: Changed to AllowAny, made user-aware for session auth

    GET /api/projects/

    Returns:
        {
            "projects": [
                {
                    "id": "uuid",
                    "name": "Brand Launch Campaign",
                    "description": "...",
                    "goal": "...",
                    "status": "in_progress",
                    "category": "Branding",
                    "deadline": "2025-12-31T23:59:59Z",
                    "total_workflows": 5,
                    "completed_workflows": 2,
                    "progress_percentage": 40,
                    "is_overdue": false,
                    "created_at": "2025-11-06T12:00:00Z",
                    "updated_at": "2025-11-06T14:00:00Z"
                }
            ]
        }
    """
    try:
        from content.models import CreativeProject

        # Session 350: Support both authenticated and anonymous users
        if request.user.is_authenticated:
            projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')
        else:
            # Anonymous users get empty list (no shared projects to show)
            projects = CreativeProject.objects.none()

        project_data = []
        for project in projects:
            project_data.append({
                'id': str(project.id),
                'name': project.name,
                'sequential_number': project.get_sequential_number(),  # Session 117: Sequential ID
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'is_overdue': project.is_overdue,
                'is_shared': project.is_shared,
                'is_quick_starts': project.is_quick_starts,  # Session 97: Quick Starts flag
                'last_activity': project.updated_at.isoformat(),  # Session 97: For sorting
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            })

        logger.info(f"✅ Loaded {len(project_data)} projects for user {request.user.username}")

        return Response({'projects': project_data})

    except Exception as e:
        logger.error(f"❌ Error listing projects: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """
    Create a new creative project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/
    Body:
        {
            "name": "Brand Launch Campaign",
            "description": "Complete brand identity for new startup",
            "goal": "Create professional brand assets",
            "deadline": "2025-12-31T23:59:59Z" (optional),
            "category": "Branding" (optional),
            "tags": ["logo", "branding", "social"] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... project data ... }
        }
    """
    try:
        # Session 324: Use unified PartnershipProject model
        from core.models_partnership import PartnershipProject
        from django.utils.dateparse import parse_datetime

        # Validate required fields
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()
        goal = request.data.get('goal', '').strip()

        if not name:
            return Response({
                'error': 'Project name is required'
            }, status=400)

        # Goal is optional for unified model (backward compatible)
        # if not goal:
        #     return Response({
        #         'error': 'Project goal is required'
        #     }, status=400)

        # Optional fields
        deadline_str = request.data.get('deadline')
        deadline = None
        if deadline_str:
            deadline = parse_datetime(deadline_str)

        category = request.data.get('category', '')
        colors = request.data.get('colors', '')  # Session 63: Professional agency intake field
        tags = request.data.get('tags', [])
        project_type = request.data.get('project_type', 'content_creation')

        # Session 324: Create project using unified PartnershipProject model
        project = PartnershipProject.objects.create(
            user=request.user,
            project_name=name,  # PartnershipProject uses project_name
            description=description,
            goal=goal,
            deadline=deadline,
            category=category,
            colors=colors,
            tags=tags,
            project_type=project_type,
            status='planning'
        )

        logger.info(f"✅ Created project '{name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'total_workflows': project.total_workflows,
                'completed_workflows': project.completed_workflows,
                'progress_percentage': project.progress_percentage,
                'created_at': project.created_at.isoformat()
            }
        }, status=201)

    except Exception as e:
        logger.error(f"❌ Error creating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


def calculate_project_stats(project_id, user):
    """
    Calculate comprehensive project statistics
    Session 146: Project Stats Header

    Args:
        project_id: UUID of the project
        user: User object for filtering

    Returns:
        Dict containing content counts, collaboration metrics, and timeline
    """
    from content.models import ImageHistory, VideoHistory, MiniFigAsset
    from core.models.agents_registry import AgentContribution
    from coleadership.models import CoLeadershipDecision
    from django.db.models import Sum, Max

    # Content counts
    images_count = ImageHistory.objects.filter(project_id=project_id, user=user).count()
    videos_count = VideoHistory.objects.filter(project_id=project_id, user=user).count()
    models_count = MiniFigAsset.objects.filter(project_id=project_id, user=user).count()

    # Agent stats (Session 147: Return list of agent names for dropdown)
    # Session 148 Fix: Get agent names, not UUIDs, for JSON serialization
    agent_contributions = AgentContribution.objects.filter(
        project_id=project_id
    ).select_related('agent').values('agent__name').distinct()

    # Create unique list by converting to set and back to list
    unique_agents_list = sorted(list(set([a['agent__name'] for a in agent_contributions if a['agent__name']])))
    unique_agents_count = len(unique_agents_list)

    total_execution_time = AgentContribution.objects.filter(
        project_id=project_id
    ).aggregate(total=Sum('execution_time_seconds'))['total'] or 0

    # Decision count (from Decision Timeline / Co-Leadership)
    decisions_count = CoLeadershipDecision.objects.filter(project_id=project_id).count()

    # Session 183: Workflow count (from WorkflowHistory)
    from content.models import WorkflowHistory
    workflows_count = WorkflowHistory.objects.filter(project_id=project_id, user=user).count()

    # Get project created_at
    from content.models import CreativeProject
    try:
        project = CreativeProject.objects.get(id=project_id, user=user)
        created_at = project.created_at
    except CreativeProject.DoesNotExist:
        created_at = None

    # Last active (most recent content creation)
    last_active_candidates = []

    image_latest = ImageHistory.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if image_latest:
        last_active_candidates.append(image_latest)

    video_latest = VideoHistory.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if video_latest:
        last_active_candidates.append(video_latest)

    model_latest = MiniFigAsset.objects.filter(
        project_id=project_id, user=user
    ).aggregate(latest=Max('created_at'))['latest']
    if model_latest:
        last_active_candidates.append(model_latest)

    last_active = max(last_active_candidates) if last_active_candidates else created_at

    return {
        'content': {
            'images': images_count,
            'videos': videos_count,
            'models': models_count,
            'total': images_count + videos_count + models_count
        },
        'collaboration': {
            'unique_agents': unique_agents_list,  # Session 147: List of agent names
            'unique_agents_count': unique_agents_count,  # Session 147: Count for stats display
            'decisions_count': decisions_count,
            'workflows_count': workflows_count,  # Session 183: Workflows completed
            'execution_time_seconds': int(total_execution_time)
        },
        'timeline': {
            'created_at': created_at.isoformat() if created_at else None,
            'last_active': last_active.isoformat() if last_active else None
        }
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project(request, project_id):
    """
    Get detailed information about a specific project
    Session 60: Phase C.1.2 - Project Management API
    Session 146: Added stats field with comprehensive project metrics

    GET /api/projects/<uuid:project_id>/

    Returns:
        {
            "project": {
                ... project data ...,
                "stats": {
                    "content": {"images": 42, "videos": 15, "models": 3},
                    "collaboration": {"unique_agents": 3, "decisions_count": 5, "execution_time_seconds": 9000},
                    "timeline": {"created_at": "...", "last_active": "..."}
                },
                "workflows": [
                    {
                        "id": "uuid",
                        "workflow_name": "Logo Creator",
                        "workflow_type": "logo_creator",
                        "status": "completed",
                        "order": 0,
                        "notes": "Main logo design",
                        "created_at": "...",
                        "result_count": 3
                    }
                ]
            }
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get all workflows in this project
        workflows_data = []
        for pw in project.workflows.all():
            workflows_data.append({
                'id': str(pw.id),
                'workflow_history_id': str(pw.workflow_history.id),
                'workflow_name': pw.workflow_history.workflow_name,
                'workflow_type': pw.workflow_history.workflow_type,
                'status': pw.workflow_history.status,
                'order': pw.order,
                'notes': pw.notes,
                'added_at': pw.added_at.isoformat(),
                'result_count': pw.workflow_history.result_count,
                'execution_time': pw.workflow_history.execution_time
            })

        # Session 146: Calculate comprehensive project stats
        stats = calculate_project_stats(project_id, request.user)

        project_data = {
            'id': str(project.id),
            'name': project.name,
            'description': project.description,
            'goal': project.goal,
            'status': project.status,
            'category': project.category,
            'colors': project.colors,  # Session 63: Professional agency intake field
            'tags': project.tags,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'total_workflows': project.total_workflows,
            'completed_workflows': project.completed_workflows,
            'progress_percentage': project.progress_percentage,
            'is_overdue': project.is_overdue,
            'is_shared': project.is_shared,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'stats': stats,  # Session 146: Project Stats Header
            'metadata': project.metadata,  # Session 201: Rich workflow data (research links, agent recommendations)
            'workflows': workflows_data
        }

        return Response({'project': project_data})

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error getting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """
    Update an existing project
    Session 60: Phase C.1.2 - Project Management API

    PUT/PATCH /api/projects/<uuid:project_id>/
    Body:
        {
            "name": "Updated Name" (optional),
            "description": "..." (optional),
            "goal": "..." (optional),
            "status": "in_progress" (optional),
            "deadline": "..." (optional),
            "category": "..." (optional),
            "tags": [...] (optional)
        }

    Returns:
        {
            "success": true,
            "project": { ... updated project data ... }
        }
    """
    try:
        from content.models import CreativeProject
        from django.utils.dateparse import parse_datetime

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Update fields if provided
        if 'name' in request.data:
            project.name = request.data['name'].strip()

        if 'description' in request.data:
            project.description = request.data['description'].strip()

        if 'goal' in request.data:
            project.goal = request.data['goal'].strip()

        if 'status' in request.data:
            status = request.data['status']
            valid_statuses = ['planning', 'in_progress', 'review', 'completed', 'archived']
            if status in valid_statuses:
                project.status = status

        if 'deadline' in request.data:
            deadline_str = request.data['deadline']
            if deadline_str:
                project.deadline = parse_datetime(deadline_str)
            else:
                project.deadline = None

        if 'category' in request.data:
            project.category = request.data['category']

        if 'colors' in request.data:  # Session 63: Professional agency intake field
            project.colors = request.data['colors']

        if 'tags' in request.data:
            project.tags = request.data['tags']

        project.save()

        logger.info(f"✅ Updated project '{project.name}' for user {request.user.username}")

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'goal': project.goal,
                'status': project.status,
                'category': project.category,
                'colors': project.colors,  # Session 63: Professional agency intake field
                'tags': project.tags,
                'deadline': project.deadline.isoformat() if project.deadline else None,
                'progress_percentage': project.progress_percentage,
                'updated_at': project.updated_at.isoformat()
            }
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error updating project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """
    Delete a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/

    Returns:
        {
            "success": true,
            "message": "Project deleted successfully"
        }
    """
    try:
        from content.models import CreativeProject

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        project_name = project.name
        project.delete()

        logger.info(f"✅ Deleted project '{project_name}' for user {request.user.username}")

        return Response({
            'success': True,
            'message': f"Project '{project_name}' deleted successfully"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error deleting project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_workflow_to_project(request, project_id):
    """
    Add a workflow to a project
    Session 60: Phase C.1.2 - Project Management API

    POST /api/projects/<uuid:project_id>/workflows/
    Body:
        {
            "workflow_history_id": "uuid",
            "order": 0 (optional),
            "notes": "Main logo design" (optional)
        }

    Returns:
        {
            "success": true,
            "project_workflow": { ... }
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow, WorkflowHistory

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        workflow_history_id = request.data.get('workflow_history_id')
        if not workflow_history_id:
            return Response({
                'error': 'workflow_history_id is required'
            }, status=400)

        # Session 60: Using UUID for workflow lookup
        workflow_history = WorkflowHistory.objects.get(
            id=workflow_history_id,
            user=request.user
        )

        # Check if already in project
        existing = ProjectWorkflow.objects.filter(
            project=project,
            workflow_history=workflow_history
        ).exists()

        if existing:
            return Response({
                'error': 'Workflow already in this project'
            }, status=400)

        # Get order (default to end of list)
        order = request.data.get('order')
        if order is None:
            # Add to end
            max_order = project.workflows.count()
            order = max_order

        notes = request.data.get('notes', '')

        # Create link
        project_workflow = ProjectWorkflow.objects.create(
            project=project,
            workflow_history=workflow_history,
            order=order,
            notes=notes
        )

        logger.info(f"✅ Added workflow '{workflow_history.workflow_name}' to project '{project.name}'")

        return Response({
            'success': True,
            'project_workflow': {
                'id': str(project_workflow.id),
                'project_id': str(project.id),
                'workflow_history_id': str(workflow_history.id),
                'workflow_name': workflow_history.workflow_name,
                'order': project_workflow.order,
                'notes': project_workflow.notes,
                'added_at': project_workflow.added_at.isoformat()
            }
        }, status=201)

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except WorkflowHistory.DoesNotExist:
        return Response({
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error adding workflow to project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_workflow_from_project(request, project_id, workflow_id):
    """
    Remove a workflow from a project
    Session 60: Phase C.1.2 - Project Management API

    DELETE /api/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/

    Returns:
        {
            "success": true,
            "message": "Workflow removed from project"
        }
    """
    try:
        from content.models import CreativeProject, ProjectWorkflow

        # Session 60: Using UUID for project lookup
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Session 60: Using UUID for ProjectWorkflow lookup
        project_workflow = ProjectWorkflow.objects.get(
            id=workflow_id,
            project=project
        )

        workflow_name = project_workflow.workflow_history.workflow_name
        project_workflow.delete()

        logger.info(f"✅ Removed workflow '{workflow_name}' from project '{project.name}'")

        return Response({
            'success': True,
            'message': f"Workflow '{workflow_name}' removed from project"
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except ProjectWorkflow.DoesNotExist:
        return Response({
            'error': 'Workflow not in this project'
        }, status=404)
    except Exception as e:
        logger.error(f"❌ Error removing workflow from project: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# ===================================================================
# SESSION 61: PHASE C.2.1 - PORTFOLIO VIEW API
# ===================================================================
# Portfolio aggregates ALL content (images, videos, audio) from ALL projects
# Provides unified view with filtering and sorting capabilities
# ===================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio(request):
    """
    GET /api/portfolio/

    Aggregate all content (images, videos, audio) from all user's creative projects

    Query Parameters:
    - project_id: Filter by specific project (UUID)
    - content_type: Filter by type (image/video/audio)
    - date_from: Start date (ISO format)
    - date_to: End date (ISO format)
    - sort_by: Sort field (created_at/project_name/type/rating) default: -created_at
    - search: Search across prompts, models, styles (Session 62: Phase C.2.1)
    - agent: Filter by agent name (Session 147: Agent filtering)
    """
    try:
        # Import models locally
        from content.models import ImageHistory, VideoHistory
        from django.utils.dateparse import parse_datetime
        from django.db.models import Q  # Session 96: Needed for video URL filtering

        logger.info(f"📊 Loading portfolio for user: {request.user.username}")

        # Get query parameters
        project_id = request.GET.get('project_id')
        content_type = request.GET.get('content_type')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        sort_by = request.GET.get('sort_by', '-created_at')
        search_query = request.GET.get('search', '').strip()  # Session 62: Phase C.2.1
        agent_filter = request.GET.get('agent', '').strip()  # Session 147: Agent filtering

        # Base filters
        image_filter = {'user': request.user}
        video_filter = {'user': request.user}
        audio_filter = {'user': request.user}

        # Apply date filtering
        if date_from:
            try:
                from_date = parse_datetime(date_from)
                if from_date:
                    image_filter['created_at__gte'] = from_date
                    video_filter['created_at__gte'] = from_date
                    audio_filter['created_at__gte'] = from_date
            except Exception as e:
                logger.warning(f"⚠️ Invalid date_from: {date_from}")

        if date_to:
            try:
                to_date = parse_datetime(date_to)
                if to_date:
                    image_filter['created_at__lte'] = to_date
                    video_filter['created_at__lte'] = to_date
                    audio_filter['created_at__lte'] = to_date
            except Exception as e:
                logger.warning(f"⚠️ Invalid date_to: {date_to}")

        # Session 147: Agent filtering - Get content IDs created by specific agent
        agent_image_ids = None
        agent_video_ids = None
        agent_model_ids = None
        if agent_filter:
            from core.models.agents_registry import AgentContribution

            logger.info(f"🤖 Filtering by agent: {agent_filter}")

            # Get all contributions by this agent for this user's content
            if project_id:
                # Filter by project if specified
                contributions = AgentContribution.objects.filter(
                    project_id=project_id,
                    agent=agent_filter
                )
            else:
                # All contributions by this agent (would need user filter if available)
                # AgentContribution doesn't have user field, so we filter by project ownership later
                contributions = AgentContribution.objects.filter(agent=agent_filter)

            # Extract content IDs
            agent_image_ids = set(contributions.filter(
                image_id__isnull=False
            ).values_list('image_id', flat=True))

            agent_video_ids = set(contributions.filter(
                video_id__isnull=False
            ).values_list('video_id', flat=True))

            agent_model_ids = set(contributions.filter(
                minifig_asset_id__isnull=False
            ).values_list('minifig_asset_id', flat=True))

            logger.info(f"🎯 Agent {agent_filter}: {len(agent_image_ids)} images, {len(agent_video_ids)} videos, {len(agent_model_ids)} models")

        # Collect content items
        portfolio_items = []

        # Query images
        if not content_type or content_type == 'image':
            images_query = ImageHistory.objects.filter(**image_filter).select_related('user')

            # Session 62: Phase C.2.1 - Apply search filter
            if search_query:
                images_query = images_query.filter(
                    Q(prompt__icontains=search_query) |
                    Q(model_used__icontains=search_query) |
                    Q(style__icontains=search_query) |
                    Q(image_type__icontains=search_query)
                )

            # Session 147: Apply agent filter
            if agent_image_ids is not None:
                images_query = images_query.filter(id__in=agent_image_ids)

            images = images_query
            for img in images:
                # Session 63: Find associated projects - check direct project field first
                projects = []

                # Session 63: Check direct project relationship (new approach)
                if hasattr(img, 'project') and img.project:
                    if not project_id or str(img.project.id) == project_id:
                        projects.append({
                            'id': str(img.project.id),
                            'name': img.project.name,
                            'status': img.project.status
                        })
                # Also check via WorkflowHistory (legacy approach)
                elif hasattr(img, 'workflow_executions') and img.workflow_executions.exists():
                    for wf in img.workflow_executions.all():
                        project_workflows = wf.projects.select_related('project').all()
                        for pw in project_workflows:
                            if not project_id or str(pw.project.id) == project_id:
                                projects.append({
                                    'id': str(pw.project.id),
                                    'name': pw.project.name,
                                    'status': pw.project.status
                                })

                # Skip if project filter doesn't match
                if project_id and not projects:
                    continue

                portfolio_items.append({
                    'id': str(img.id),
                    'sequential_number': img.get_sequential_number(),  # Session 117: Sequential ID
                    'type': 'image',
                    'image_type': img.image_type,  # Session 183: For social media filtering
                    'content_url': img.get_full_url(),
                    'thumbnail_url': img.get_thumbnail_url(),
                    'prompt': img.prompt,
                    'model': img.model_used,
                    'style': img.style,
                    'operation_type': img.image_type,
                    'created_at': img.created_at.isoformat(),
                    'view_count': img.view_count,
                    'download_count': img.download_count,
                    'is_favorite': img.is_favorite,
                    'user_rating': getattr(img, 'user_rating', None),  # Session 147: For sorting by rating
                    'projects': projects,
                    'parameters': img.parameters,  # Session 183: For social media filtering
                    'metadata': {
                        'width': img.image_width,
                        'height': img.image_height,
                        'file_size': img.file_size_bytes,
                        'parameters': img.parameters
                    }
                })

        # Query videos
        if not content_type or content_type == 'video':
            # Session 96: Exclude videos with expired external CDN URLs
            # Session 119: Filter disabled - videos are now downloaded to local storage automatically
            videos_query = VideoHistory.objects.filter(**video_filter).select_related('user')
            # CDN filter no longer needed - all new videos download automatically (Session 119)
            # Existing videos rescued via rescue_cdn_videos.py script

            # Session 62: Phase C.2.1 - Apply search filter
            if search_query:
                videos_query = videos_query.filter(
                    Q(prompt__icontains=search_query) |
                    Q(model_used__icontains=search_query) |
                    Q(video_type__icontains=search_query)
                )

            # Session 147: Apply agent filter
            if agent_video_ids is not None:
                videos_query = videos_query.filter(id__in=agent_video_ids)

            videos = videos_query
            for vid in videos:
                # Session 63: Find associated projects - check direct project field first
                projects = []

                # Session 63: Check direct project relationship (new approach)
                if hasattr(vid, 'project') and vid.project:
                    if not project_id or str(vid.project.id) == project_id:
                        projects.append({
                            'id': str(vid.project.id),
                            'name': vid.project.name,
                            'status': vid.project.status
                        })
                # Also check via WorkflowHistory (legacy approach)
                elif hasattr(vid, 'workflow_executions') and vid.workflow_executions.exists():
                    for wf in vid.workflow_executions.all():
                        project_workflows = wf.projects.select_related('project').all()
                        for pw in project_workflows:
                            if not project_id or str(pw.project.id) == project_id:
                                projects.append({
                                    'id': str(pw.project.id),
                                    'name': pw.project.name,
                                    'status': pw.project.status
                                })

                if project_id and not projects:
                    continue

                portfolio_items.append({
                    'id': str(vid.id),
                    'sequential_number': vid.get_sequential_number(),  # Session 119: Sequential ID for videos
                    'type': 'video',
                    'content_url': vid.video_url,
                    'thumbnail_url': vid.thumbnail_url or vid.video_url,
                    'prompt': vid.prompt,
                    'operation_type': vid.video_type,
                    'created_at': vid.created_at.isoformat(),
                    'view_count': vid.view_count,
                    'download_count': vid.download_count,
                    'is_favorite': vid.is_favorite,
                    'user_rating': getattr(vid, 'user_rating', None),  # Session 147: For sorting by rating
                    'projects': projects,
                    'metadata': {
                        'duration': vid.duration,
                        'width': vid.video_width,
                        'height': vid.video_height,
                        'provider': 'runway',
                        'model': vid.model_used,
                        'status': vid.status
                    }
                })

        # Query 3D models (Session 137: Add MiniFigAsset support)
        if not content_type or content_type == '3d_model' or content_type == 'model':
            from content.models import MiniFigAsset

            # Session 182: Show all 3D models (including pending/processing for polling)
            # Frontend will handle display based on status
            models_query = MiniFigAsset.objects.filter(
                user=request.user,
                status__in=['completed', 'pending', 'processing']
            ).select_related('user')

            # Session 137: Apply search filter
            if search_query:
                models_query = models_query.filter(
                    Q(title__icontains=search_query) |
                    Q(provider__icontains=search_query)
                )

            # Session 147: Apply agent filter
            if agent_model_ids is not None:
                models_query = models_query.filter(id__in=agent_model_ids)

            models = models_query
            for model_obj in models:
                # Session 137: Find associated projects - check direct project field
                projects = []

                if hasattr(model_obj, 'project') and model_obj.project:
                    if not project_id or str(model_obj.project.id) == project_id:
                        projects.append({
                            'id': str(model_obj.project.id),
                            'name': model_obj.project.name,
                            'status': model_obj.project.status
                        })

                # Skip if project filter doesn't match
                if project_id and not projects:
                    continue

                # Session 172: Prefer local file path over CDN URL (CDN URLs expire)
                # Build absolute URL for 3D file
                if model_obj.local_glb_path:
                    model_url = f'/media/{model_obj.local_glb_path}'
                else:
                    model_url = model_obj.three_d_file or ''
                preview_url = model_obj.preview_image_url or ''

                if model_url and not model_url.startswith(('http://', 'https://')):
                    model_url = request.build_absolute_uri(model_url)
                if preview_url and not preview_url.startswith(('http://', 'https://', 'data:')):
                    preview_url = request.build_absolute_uri(preview_url)

                portfolio_items.append({
                    'id': str(model_obj.id),
                    'sequential_number': model_obj.get_sequential_number() if hasattr(model_obj, 'get_sequential_number') else 0,
                    'type': '3d_model',
                    'status': model_obj.status,  # Session 182: Expose status for frontend polling
                    'content_url': model_url,
                    'thumbnail_url': preview_url,
                    'prompt': model_obj.title,
                    'operation_type': 'image-to-3d',
                    'created_at': model_obj.created_at.isoformat(),
                    'view_count': model_obj.view_count if hasattr(model_obj, 'view_count') else 0,
                    'download_count': model_obj.download_count if hasattr(model_obj, 'download_count') else 0,
                    'is_favorite': model_obj.is_favorite if hasattr(model_obj, 'is_favorite') else False,
                    'user_rating': getattr(model_obj, 'user_rating', None),  # Session 147: For sorting by rating
                    'projects': projects,
                    'metadata': {
                        'provider': model_obj.provider,
                        'status': model_obj.status,
                        'style': model_obj.metadata.get('style', 'toy') if model_obj.metadata else 'toy',
                        'scale': model_obj.metadata.get('scale', 'medium') if model_obj.metadata else 'medium',
                        'model_type': 'minifig'
                    }
                })

        # Query audio
        # NOTE: AudioHistory model not yet implemented. Audio via Runway ML without model tracking.
        # if not content_type or content_type == 'audio':
        #     audio_items = AudioHistory.objects.filter(**audio_filter).select_related('user')
        #     for aud in audio_items:
        #         # Find associated projects
        #         projects = []
        #         if hasattr(aud, 'workflow_executions') and aud.workflow_executions.exists():
        #             for wf in aud.workflow_executions.all():
        #                 project_workflows = wf.projects.select_related('project').all()
        #                 for pw in project_workflows:
        #                     if not project_id or str(pw.project.id) == project_id:
        #                         projects.append({
        #                             'id': str(pw.project.id),
        #                             'name': pw.project.name,
        #                             'status': pw.project.status
        #                         })
        #
        #         if project_id and not projects:
        #             continue
        #
        #         portfolio_items.append({
        #             'id': str(aud.id),
        #             'type': 'audio',
        #             'content_url': aud.audio_url,
        #             'thumbnail_url': None,
        #             'prompt': aud.prompt,
        #             'operation_type': aud.operation_type,
        #             'created_at': aud.created_at.isoformat(),
        #             'view_count': aud.view_count,
        #             'download_count': aud.download_count,
        #             'is_favorite': aud.is_favorite,
        #             'projects': projects,
        #             'metadata': {
        #                 'duration': aud.duration,
        #                 'voice': aud.voice,
        #                 'provider': 'runway'
        #             }
        #         })

        # Sort results
        if sort_by == 'created_at':
            portfolio_items.sort(key=lambda x: x['created_at'])
        elif sort_by == '-created_at':
            portfolio_items.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'type':
            portfolio_items.sort(key=lambda x: x['type'])
        elif sort_by == 'project_name':
            # Sort by first project name if exists
            portfolio_items.sort(key=lambda x: x['projects'][0]['name'] if x['projects'] else 'zzzz')
        elif sort_by == 'rating':
            # Session 147: Sort by user rating (lowest to highest, null last)
            # Handle None values: convert to -1 for sorting (Python 3 can't compare None with int)
            portfolio_items.sort(key=lambda x: x.get('user_rating') if x.get('user_rating') is not None else -1)
        elif sort_by == '-rating':
            # Session 147: Sort by user rating (highest to lowest, null last)
            # Handle None values: convert to -1 for sorting (Python 3 can't compare None with int)
            portfolio_items.sort(key=lambda x: x.get('user_rating') if x.get('user_rating') is not None else -1, reverse=True)

        # Get summary stats (Session 137: Add 3D models count)
        stats = {
            'total_items': len(portfolio_items),
            'images': sum(1 for item in portfolio_items if item['type'] == 'image'),
            'videos': sum(1 for item in portfolio_items if item['type'] == 'video'),
            'audio': sum(1 for item in portfolio_items if item['type'] == 'audio'),
            'models': sum(1 for item in portfolio_items if item['type'] == '3d_model'),
            'favorites': sum(1 for item in portfolio_items if item['is_favorite']),
            'total_views': sum(item['view_count'] for item in portfolio_items),
            'total_downloads': sum(item['download_count'] for item in portfolio_items)
        }

        logger.info(f"✅ Portfolio loaded: {stats['total_items']} items ({stats['images']} images, {stats['videos']} videos, {stats['audio']} audio, {stats['models']} 3D models)")

        # Session 96: Add no-cache headers to prevent browser caching of expired video URLs
        response = Response({
            'success': True,
            'portfolio': portfolio_items,
            'stats': stats,
            'filters': {
                'project_id': project_id,
                'content_type': content_type,
                'date_from': date_from,
                'date_to': date_to,
                'sort_by': sort_by,
                'agent': agent_filter  # Session 147: Include agent filter in response
            }
        })
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    except Exception as e:
        logger.error(f"❌ Error loading portfolio: {str(e)}")
        return Response({
            'error': str(e)
        }, status=500)


# Session 237: Portfolio Delete Functionality
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio_item(request, item_type, item_id):
    """
    DELETE /api/portfolio/<item_type>/<item_id>/delete/

    Delete a single portfolio item (image, video, or 3d_model)
    Only the owner can delete their content.
    """
    try:
        from content.models import ImageHistory, VideoHistory

        logger.info(f"🗑️ Deleting {item_type} {item_id} for user {request.user.username}")

        if item_type == 'image':
            try:
                item = ImageHistory.objects.get(id=item_id, user=request.user)
                item.delete()
                logger.info(f"✅ Deleted image {item_id}")
            except ImageHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Image not found or not owned by you'
                }, status=404)

        elif item_type == 'video':
            try:
                item = VideoHistory.objects.get(id=item_id, user=request.user)
                item.delete()
                logger.info(f"✅ Deleted video {item_id}")
            except VideoHistory.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Video not found or not owned by you'
                }, status=404)

        elif item_type == '3d_model':
            try:
                from content.models import MinifigAsset
                item = MinifigAsset.objects.get(id=item_id, user=request.user)
                item.delete()
                logger.info(f"✅ Deleted 3D model {item_id}")
            except Exception:
                return Response({
                    'success': False,
                    'error': '3D model not found or not owned by you'
                }, status=404)
        else:
            return Response({
                'success': False,
                'error': f'Unknown item type: {item_type}'
            }, status=400)

        return Response({
            'success': True,
            'message': f'{item_type.capitalize()} deleted successfully'
        })

    except Exception as e:
        logger.error(f"❌ Error deleting portfolio item: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_delete_portfolio_items(request):
    """
    POST /api/portfolio/bulk-delete/

    Delete multiple portfolio items at once.
    Request body: { "items": [{"id": "uuid", "type": "image"}, ...] }
    """
    try:
        from content.models import ImageHistory, VideoHistory

        items = request.data.get('items', [])

        if not items:
            return Response({
                'success': False,
                'error': 'No items provided'
            }, status=400)

        logger.info(f"🗑️ Bulk deleting {len(items)} items for user {request.user.username}")

        deleted_count = 0
        errors = []

        for item in items:
            item_id = item.get('id')
            item_type = item.get('type')

            if not item_id or not item_type:
                errors.append(f"Missing id or type for item: {item}")
                continue

            try:
                if item_type == 'image':
                    ImageHistory.objects.get(id=item_id, user=request.user).delete()
                    deleted_count += 1
                elif item_type == 'video':
                    VideoHistory.objects.get(id=item_id, user=request.user).delete()
                    deleted_count += 1
                elif item_type == '3d_model':
                    from content.models import MinifigAsset
                    MinifigAsset.objects.get(id=item_id, user=request.user).delete()
                    deleted_count += 1
                else:
                    errors.append(f"Unknown type: {item_type}")
            except Exception as e:
                errors.append(f"Failed to delete {item_type} {item_id}: {str(e)}")

        logger.info(f"✅ Bulk delete complete: {deleted_count} deleted, {len(errors)} errors")

        return Response({
            'success': True,
            'deleted_count': deleted_count,
            'errors': errors if errors else None,
            'message': f'Successfully deleted {deleted_count} items'
        })

    except Exception as e:
        logger.error(f"❌ Error in bulk delete: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_portfolio_broken_links(request):
    """
    GET /api/portfolio/check-broken/

    Check for portfolio items with broken/expired links.
    Returns list of items that can't be loaded.
    """
    try:
        import requests
        from content.models import ImageHistory, VideoHistory

        logger.info(f"🔍 Checking broken links for user {request.user.username}")

        broken_items = []
        checked_count = 0

        # Check images
        images = ImageHistory.objects.filter(user=request.user)
        for img in images:
            checked_count += 1
            url = img.get_full_url()

            # Skip data URIs (always valid)
            if url and url.startswith('data:'):
                continue

            # Skip local files that exist
            if url and url.startswith('/media/'):
                continue

            # Check remote URLs
            if url and url.startswith(('http://', 'https://')):
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_items.append({
                            'id': str(img.id),
                            'type': 'image',
                            'url': url,
                            'prompt': img.prompt[:100] if img.prompt else 'No description',
                            'created_at': img.created_at.isoformat(),
                            'status_code': response.status_code
                        })
                except requests.RequestException as e:
                    broken_items.append({
                        'id': str(img.id),
                        'type': 'image',
                        'url': url,
                        'prompt': img.prompt[:100] if img.prompt else 'No description',
                        'created_at': img.created_at.isoformat(),
                        'error': str(e)
                    })
            elif not url:
                broken_items.append({
                    'id': str(img.id),
                    'type': 'image',
                    'url': None,
                    'prompt': img.prompt[:100] if img.prompt else 'No description',
                    'created_at': img.created_at.isoformat(),
                    'error': 'No URL'
                })

        # Check videos
        videos = VideoHistory.objects.filter(user=request.user)
        for vid in videos:
            checked_count += 1
            url = vid.video_url

            if url and url.startswith(('http://', 'https://')):
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_items.append({
                            'id': str(vid.id),
                            'type': 'video',
                            'url': url,
                            'prompt': vid.prompt[:100] if vid.prompt else 'No description',
                            'created_at': vid.created_at.isoformat(),
                            'status_code': response.status_code
                        })
                except requests.RequestException as e:
                    broken_items.append({
                        'id': str(vid.id),
                        'type': 'video',
                        'url': url,
                        'prompt': vid.prompt[:100] if vid.prompt else 'No description',
                        'created_at': vid.created_at.isoformat(),
                        'error': str(e)
                    })
            elif not url:
                broken_items.append({
                    'id': str(vid.id),
                    'type': 'video',
                    'url': None,
                    'prompt': vid.prompt[:100] if vid.prompt else 'No description',
                    'created_at': vid.created_at.isoformat(),
                    'error': 'No URL'
                })

        logger.info(f"✅ Checked {checked_count} items, found {len(broken_items)} broken")

        return Response({
            'success': True,
            'checked_count': checked_count,
            'broken_count': len(broken_items),
            'broken_items': broken_items
        })

    except Exception as e:
        logger.error(f"❌ Error checking broken links: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_workflow_for_project(request):
    """
    Session 63: Execute workflow and link results to project
    Endpoint: /api/workflows/execute-for-project/
    """
    try:
        project_id = request.data.get('project_id')
        workflow_type = request.data.get('workflow_type')
        form_data = request.data.get('form_data')

        if not all([project_id, workflow_type, form_data]):
            return Response({
                'success': False,
                'error': 'Missing required fields: project_id, workflow_type, form_data'
            }, status=400)

        # Verify project exists and belongs to user
        from content.models import CreativeProject
        try:
            project = CreativeProject.objects.get(id=project_id, user=request.user)
        except CreativeProject.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=404)

        logger.info(f"🎨 Executing {workflow_type} for project: {project.name}")

        # Session 63: Build prompt from form data AND PROJECT GOAL!
        prompt = build_prompt_from_form(workflow_type, form_data, project)

        if not prompt:
            return Response({
                'success': False,
                'error': f'Could not build prompt for workflow type: {workflow_type}'
            }, status=400)

        logger.info(f"📝 Built prompt: {prompt}")

        # Execute workflow based on type
        results = []
        error_messages = []  # Session 64: Collect error messages for debugging

        if workflow_type == 'logo-creator':
            # Session 64: Choose model based on logo style - SDXL for character mascots, Core for flat logos
            logo_style = form_data.get('logoStyle', 'character-mascot')
            model = 'sdxl' if logo_style == 'character-mascot' else 'core'

            # Session 64: Truncate prompt if too long (SDXL limit is 2000 chars)
            if len(prompt) > 2000:
                logger.warning(f"⚠️ Prompt too long ({len(prompt)} chars), truncating intelligently")

                # Session 64: Intelligent truncation - prioritize CRITICAL keywords
                # GPT-5 puts clothing in the middle, which gets cut by naive truncation!

                # Extract sentences with critical keywords (clothing, accessories, key features)
                import re
                critical_keywords = ['WEARING', 'DRESSED', 'PLATFORM', 'necklace', 'pants', 'shoes',
                                   'outfit', 'clothing', 'accessory', 'bell-bottom', 'disco ball']

                # Split into sentences
                sentences = re.split(r'[.!?]\s+', prompt)

                # Categorize sentences
                critical_sentences = []
                normal_sentences = []

                for sent in sentences:
                    if any(keyword.lower() in sent.lower() for keyword in critical_keywords):
                        critical_sentences.append(sent)
                    else:
                        normal_sentences.append(sent)

                # Build truncated prompt: critical details + as many normal details as fit
                prompt_parts = []
                char_count = 0

                # Always include critical sentences (clothing!)
                for sent in critical_sentences:
                    if char_count + len(sent) + 2 < 1900:  # Leave room for period
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2

                # Add normal sentences until we hit limit
                for sent in normal_sentences:
                    if char_count + len(sent) + 2 < 1950:
                        prompt_parts.append(sent)
                        char_count += len(sent) + 2
                    else:
                        break

                prompt = '. '.join(prompt_parts) + '.'
                logger.info(f"📝 Intelligently truncated to {len(prompt)} chars, kept {len(critical_sentences)} critical sentences")
                logger.info(f"📝 Truncated prompt: {prompt[:200]}...")

            # Generate 1 logo (style already included in prompt by build_prompt_from_form)
            # Session 64: Pass empty string as style since prompt already contains style terms
            result = generate_image_with_stability(
                prompt=prompt,
                model=model,
                style='',  # Use empty string to avoid applying additional style preset (prompt has style terms already)
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)
            elif result and result.get('error'):
                error_messages.append(f"Logo generation failed: {result.get('error')}")
            else:
                error_messages.append("Logo generation returned no result")

        elif workflow_type == 'portrait-enhancer':
            # Generate 1 high-quality portrait
            result = generate_image_with_stability(
                prompt=prompt,
                model='sd3',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'style-explorer':
            # Generate 5 images in different styles
            styles = ['photographic', 'digital-art', 'cinematic', 'anime', 'fantasy-art']
            for style in styles:
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style=style,
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'social-media-pack':
            # Generate 3 optimized images
            for i in range(3):
                result = generate_image_with_stability(
                    prompt=prompt,
                    model='sdxl',
                    style='photographic',
                    user=request.user
                )
                if result and result.get('success'):
                    results.append(result)

        elif workflow_type == 'product-mockup':
            # Generate 1 product visualization
            result = generate_image_with_stability(
                prompt=prompt,
                model='ultra',
                style='photographic',
                user=request.user
            )
            if result and result.get('success'):
                results.append(result)

        elif workflow_type == 'creative-upscale':
            # Note: This requires an existing image - handle separately
            return Response({
                'success': False,
                'error': 'Creative Upscale requires selecting an existing image first'
            }, status=400)

        # Link all generated images to the project
        if results:
            from content.models import ImageHistory
            linked_count = 0

            for result in results:
                if result.get('image_id'):
                    try:
                        image = ImageHistory.objects.get(id=result['image_id'], user=request.user)
                        image.project = project
                        image.save()
                        linked_count += 1
                        logger.info(f"✅ Linked image {image.id} to project {project.name}")
                    except ImageHistory.DoesNotExist:
                        logger.warning(f"⚠️ Image {result['image_id']} not found")

            logger.info(f"🎉 Successfully generated and linked {linked_count} assets to project {project.name}")

            return Response({
                'success': True,
                'count': linked_count,
                'message': f'Generated {linked_count} assets for {project.name}'
            })
        else:
            # Session 64: Include actual error messages for debugging
            error_detail = 'No images were generated'
            if error_messages:
                error_detail += ': ' + '; '.join(error_messages)

            return Response({
                'success': False,
                'error': error_detail
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Error executing workflow for project: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


def build_prompt_from_form(workflow_type, form_data, project=None):
    """
    Build prompt string from form data based on workflow type
    Session 63: GOAL-DRIVEN prompt builder - Vision comes FIRST!
    """
    # Session 63: If user provided a custom prompt, use it directly
    custom_prompt = form_data.get('customPrompt', '').strip()
    if custom_prompt:
        return custom_prompt

    if workflow_type == 'logo-creator':
        parts = []

        # Session 64: CORE VISUAL SUBJECT FIRST! AI commits to the subject in first few tokens.
        # If we say "Disco Dinosaur logo" first, AI generates disco (human dancer).
        # If we say "T-Rex dinosaur in disco style" first, AI generates T-Rex!
        details = form_data.get('additionalDetails', '')
        if details:
            parts.append(details)

        # Session 64: Style terms come SECOND to reinforce the subject
        logo_style = form_data.get('logoStyle', 'character-mascot')
        style_map = {
            'character-mascot': 'cool cartoon character mascot standing upright, anthropomorphic, DreamWorks animation style, expressive, detailed illustration, cinematic lighting, 4K resolution, professional quality',
            'vector': 'professional vector art, flat design, clean lines, minimalist, iconic symbol, modern, simple shapes',
            'illustrative': 'hand-drawn illustration style, artistic, detailed linework, creative, sketch-like quality, unique character',
            'minimalist': 'minimalist design, simple and clean, negative space, modern, geometric, essential elements only',
            'badge': 'badge design, emblem style, traditional, detailed ornamental, crest, vintage feel, professional seal',
            'geometric': 'geometric shapes, abstract patterns, angular design, modern, mathematical precision, structured'
        }
        style_terms = style_map.get(logo_style, style_map['character-mascot'])
        parts.append(style_terms)

        # Business name comes AFTER subject is clear
        business_name = form_data.get('businessName', '')
        if business_name:
            parts.append(f"for {business_name}")

        colors = form_data.get('colors', '')
        if colors:
            parts.append(f'color scheme: {colors}')

        # Session 63: Vision/Goal adds context but comes AFTER core subject
        if project and project.goal:
            parts.append(f"Brand vision: {project.goal.strip()}")

        industry = form_data.get('industry', '')
        if industry:
            industry_map = {
                'tech': 'technology company',
                'coffee': 'coffee shop',
                'fitness': 'fitness gym',
                'food': 'restaurant',
                'finance': 'financial services',
                'health': 'healthcare',
                'education': 'education',
                'retail': 'retail store',
                'creative': 'creative agency',
                'construction': 'construction company'
            }
            parts.append(industry_map.get(industry, industry))

        # Additional project context comes last
        if project and project.description:
            parts.append(project.description.strip())

        parts.append('logo design')

        return ', '.join(parts)

    elif workflow_type == 'portrait-enhancer':
        subject = form_data.get('subject', '')
        style = form_data.get('style', '')
        lighting = form_data.get('lighting', '')
        background = form_data.get('background', '')

        parts = [subject, 'professional portrait']

        if style:
            parts.append(style)

        if lighting:
            parts.append(f'{lighting}')

        if background:
            parts.append(f'{background} background')

        parts.extend(['high quality', '4K', 'sharp focus', 'professional photography'])

        return ', '.join(parts)

    elif workflow_type == 'social-media-pack':
        content = form_data.get('content', '')
        platform = form_data.get('platform', '')
        colors = form_data.get('colors', '')
        mood = form_data.get('mood', '')

        parts = [content]

        if mood:
            parts.append(mood)

        if colors:
            parts.append(f'colors: {colors}')

        if platform:
            parts.append(f'optimized for {platform}')

        parts.extend(['high quality', 'professional', 'eye-catching'])

        return ', '.join(parts)

    elif workflow_type == 'product-mockup':
        description = form_data.get('description', '')
        colors = form_data.get('colors', '')
        context = form_data.get('context', '')
        style = form_data.get('style', '')

        parts = [description]

        if colors:
            parts.append(colors)

        if context:
            context_map = {
                'studio': 'studio white background',
                'lifestyle': 'lifestyle in-use setting',
                'desk': 'on modern desk workspace',
                'outdoor': 'outdoor natural environment',
                'premium': 'luxury premium setting'
            }
            parts.append(context_map.get(context, context))

        if style:
            parts.append(style)

        parts.extend(['product photography', 'high quality', 'professional'])

        return ', '.join(parts)

    elif workflow_type == 'style-explorer':
        subject = form_data.get('subject', '')
        description = form_data.get('description', '')

        parts = [subject]

        if description:
            parts.append(description)

        return ', '.join(parts)

    return None


def generate_image_with_stability(prompt, model, style, user):
    """
    Helper function to generate image using Stability AI
    Session 63: Wrapper around existing generation logic
    """
    try:
        from content.image_generation import ImageGenerationService
        from content.models import ImageHistory

        service = ImageGenerationService()

        # Map model to quality
        quality_map = {
            'core': 'fast',
            'sdxl': 'balanced',
            'sd3': 'high',
            'ultra': 'premium'
        }
        quality = quality_map.get(model, 'balanced')

        # Generate image
        result = service.generate_image(
            prompt=prompt,
            size='1024x1024',
            style=style,
            quality=quality,
            provider='stability',
            negative_prompt='blurry, low quality, distorted',
            num_images=1
        )

        if result.success and result.images:
            # Get the first image
            image_url = result.images[0]

            # Save to ImageHistory
            image_history = ImageHistory.objects.create(
                user=user,
                filename=image_url.split('/')[-1][:255],  # Session 63: Truncate to 255 chars for database constraint
                file_path=image_url,
                prompt=prompt,
                model_used=model,  # Session 63: Fixed field name
                style=style,
                image_type='generated'  # Session 64: Fixed - 'generated' not 'generation' to match model choices
            )

            logger.info(f"✅ Generated and saved image {image_history.id}")

            return {
                'success': True,
                'image_id': image_history.id,
                'url': image_url
            }
        else:
            # Session 64: Return error info instead of None
            error_msg = getattr(result, 'error_message', 'Unknown error')
            logger.error(f"❌ Image generation failed: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

    except Exception as e:
        logger.error(f"❌ Error generating image: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Session 64: Return error info instead of None
        return {
            'success': False,
            'error': str(e)
        }


def _execute_generate_speech(user, parameters):
    """
    Execute speech generation via Runway ML text-to-speech
    Session 81: AI Assistant integration for audio generation!

    This generates speech/voiceover from text:
    1. Gets text and voice parameters
    2. Calls Runway ML text-to-speech API
    3. Returns task ID for polling

    Parameters:
        text (str): Text to convert to speech (required)
        voice (str): Voice name (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave) - default: Rachel

    Returns:
        dict: {
            'success': True,
            'task_id': 'uuid',
            'voice': 'Rachel',
            'text_preview': 'first 50 chars...',
            'estimated_time': 10,
            'message': 'Generating speech...'
        }
    """
    try:
        from content.video_provider import runway_provider

        text = parameters.get('text', '').strip()
        voice = parameters.get('voice', 'Rachel')

        if not text:
            return {
                'success': False,
                'error': 'Text is required for speech generation',
                'message': 'Please provide text to convert to speech!'
            }

        logger.info(f"🗣️ AI Assistant generate_speech: voice={voice}, text={text[:50]}...")

        # Call Runway ML text-to-speech
        result = runway_provider.text_to_speech(
            text=text,
            voice=voice
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error_message', 'Speech generation failed'),
                'message': f'Failed to generate speech: {result.get("error_message", "Unknown error")}'
            }

        logger.info(f"✅ Speech generation started: task_id={result.get('task_id')}")

        return {
            'success': True,
            'task_id': result.get('task_id'),
            'voice': voice,
            'text_preview': text[:50] + ('...' if len(text) > 50 else ''),
            'estimated_time': result.get('estimated_time', 10),
            'message': f'🗣️ Generating speech with {voice}\'s voice... This will take about {result.get("estimated_time", 10)} seconds.',
            'instructions': f'Your speech is being generated! The voice will say: "{text[:100]}{"..." if len(text) > 100 else ""}". You\'ll be notified when it\'s ready.',
            'audio_type': 'speech'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_speech: {str(e)}")
        raise


def _execute_generate_sound_effect(user, parameters):
    """
    Execute sound effect generation via Runway ML text-to-sound
    Session 81: AI Assistant integration for audio generation!

    This generates sound effects from text descriptions:
    1. Gets description and duration parameters
    2. Calls Runway ML text-to-sound API
    3. Returns task ID for polling

    Parameters:
        description (str): Description of the sound effect (required)
        duration (float): Duration in seconds (0.5 to 30) - default: 5

    Returns:
        dict: {
            'success': True,
            'task_id': 'uuid',
            'description': 'thunder clap',
            'duration': 5.0,
            'estimated_time': 10,
            'message': 'Generating sound effect...'
        }
    """
    try:
        from content.video_provider import runway_provider

        description = parameters.get('description', '').strip()
        duration = parameters.get('duration', 5.0)

        if not description:
            return {
                'success': False,
                'error': 'Description is required for sound effect generation',
                'message': 'Please describe the sound effect you want to create!'
            }

        # Validate duration
        duration = max(0.5, min(30.0, float(duration)))

        logger.info(f"🔊 AI Assistant generate_sound_effect: description={description}, duration={duration}s")

        # Call Runway ML text-to-sound
        result = runway_provider.text_to_sound(
            prompt=description,
            duration=duration
        )

        if not result.get('success'):
            return {
                'success': False,
                'error': result.get('error_message', 'Sound effect generation failed'),
                'message': f'Failed to generate sound effect: {result.get("error_message", "Unknown error")}'
            }

        logger.info(f"✅ Sound effect generation started: task_id={result.get('task_id')}")

        return {
            'success': True,
            'task_id': result.get('task_id'),
            'description': description,
            'duration': duration,
            'estimated_time': result.get('estimated_time', int(duration) + 5),
            'message': f'🔊 Generating {duration}s sound effect: "{description}"... This will take about {result.get("estimated_time", int(duration) + 5)} seconds.',
            'instructions': f'Your sound effect is being generated! Creating a {duration}-second audio clip of: "{description}". You\'ll be notified when it\'s ready.',
            'audio_type': 'sound_effect'
        }

    except Exception as e:
        logger.error(f"❌ Error in _execute_generate_sound_effect: {str(e)}")
        raise


# ========================================
# SESSION 100: LEADERSHIP DASHBOARD ENDPOINTS
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_executive_meetings(request):
    """
    List all executive boardroom meetings for the current user.

    Session 100: Part 11 - Leadership Dashboard with Meeting History

    Returns list of meetings with summary info:
    - Meeting topic
    - Participants
    - Date/time
    - Summary
    - Decision count
    - Action item count
    """
    try:
        from intelligence.shared_memory import redis_client

        # Scan for all meeting keys in meeting_coordinator's memory
        # Keys are stored in db=2 with pattern: shared_memory:agent:meeting_coordinator:boardroom_meeting_*
        pattern = "shared_memory:agent:meeting_coordinator:boardroom_meeting_*"
        cursor = 0
        meetings = []

        while True:
            cursor, keys = redis_client.scan(cursor, match=pattern, count=100)

            for key in keys:
                try:
                    # Get meeting data
                    data = redis_client.get(key)
                    if data:
                        meeting_wrapper = json.loads(data)
                        # Meeting data is inside the 'content' field
                        meeting = meeting_wrapper.get('content', meeting_wrapper)

                        # Extract summary info
                        meetings.append({
                            'key': key.decode('utf-8') if isinstance(key, bytes) else key,
                            'topic': meeting.get('topic', 'Untitled Meeting'),
                            'participants': meeting.get('participants', []),
                            'met_at': meeting.get('met_at'),
                            'summary': meeting.get('summary', '')[:200],  # First 200 chars
                            'decision_count': len(meeting.get('decisions', [])),
                            'action_item_count': len(meeting.get('action_items', [])),
                            'project_id': meeting.get('project_id')
                        })
                except Exception as e:
                    logger.error(f"Error parsing meeting {key}: {str(e)}")
                    continue

            if cursor == 0:
                break

        # Sort by date (newest first)
        meetings.sort(key=lambda x: x.get('met_at', ''), reverse=True)

        logger.info(f"✅ Retrieved {len(meetings)} executive meetings for user {request.user.username}")

        return Response({
            'success': True,
            'meetings': meetings,
            'total': len(meetings)
        })

    except Exception as e:
        logger.error(f"❌ Error listing executive meetings: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': 'Failed to retrieve meetings',
            'details': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meeting_details(request, meeting_key):
    """
    Get full details of a specific executive meeting.

    Session 100: Part 11 - Returns complete meeting data:
    - All executive perspectives
    - Full summary
    - All decisions
    - All action items with ownership
    - Participant info
    """
    try:
        from intelligence.shared_memory import redis_client

        # Get meeting data from Redis
        data = redis_client.get(meeting_key)

        if not data:
            return Response({
                'success': False,
                'error': 'Meeting not found'
            }, status=404)

        meeting_wrapper = json.loads(data)
        # Meeting data is inside the 'content' field
        meeting = meeting_wrapper.get('content', meeting_wrapper)

        logger.info(f"✅ Retrieved meeting details: {meeting.get('topic')}")

        return Response({
            'success': True,
            'meeting': meeting
        })

    except Exception as e:
        logger.error(f"❌ Error getting meeting details: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': 'Failed to retrieve meeting details',
            'details': str(e)
        }, status=500)


# ========================================
# SESSION 125: Image Editing Wrappers (Accept image_id)
# ========================================

@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def upscale_image_view(request):
    """
    Upscale an existing image from history using its ID.
    Accepts JSON: {image_id: uuid, project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"📈 Upscaling image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            # Data URI - extract base64 data
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            # File path - read from storage
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
        files = {"image": image_data}
        data_params = {
            "prompt": "high quality upscale",  # Required by Stability AI API
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI upscale failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Upscale failed: {api_response.text}'}, status=500)

        # Save the upscaled image to file (NOT as data URI!)
        upscaled_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'upscaled_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved upscaled image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Upscaled from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-upscale-4x",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-generation-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Image upscaled successfully: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Upscale error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def remove_background_view(request):
    """
    Remove background from an existing image from history using its ID.
    Accepts JSON: {image_id: uuid, project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎭 Removing background from image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            # Data URI - extract base64 data
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            # File path - read from storage
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI remove-background API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"
        files = {"image": image_data}
        data_params = {"output_format": "png"}

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI remove-background failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Remove background failed: {api_response.text}'}, status=500)

        # Save the result image to file (NOT as data URI!)
        result_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'no_bg_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved background-removed image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Background removed from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-remove-bg",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Background removed successfully: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Remove background error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def create_variations_view(request):
    """
    Create variations of an existing image using structure control.
    Accepts JSON: {image_id: uuid, count: int (default 3), prompt: str (optional), project_id: uuid (optional)}
    Note: @login_required removed to support internal RequestFactory calls from agents
    """
    try:
        # Manual authentication check for web requests
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"⚠️ Unauthenticated request to create_variations_view")

        logger.info(f"🎨 create_variations_view called - user: {request.user}, authenticated: {request.user.is_authenticated}")

        data = json.loads(request.body)
        image_id = data.get('image_id')
        count = data.get('count', 3)
        variation_prompt = data.get('prompt', 'creative variation')
        project_id = data.get('project_id')

        logger.info(f"🎨 Params: image_id={image_id}, count={count}, prompt={variation_prompt}")

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
            logger.info(f"✅ Found image: {image.id}")
        except ImageHistory.DoesNotExist:
            logger.error(f"❌ Image not found: {image_id} for user {request.user}")
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Creating {count} variations of image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Get project if provided
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        # Create variations using structure control
        url = "https://api.stability.ai/v2beta/stable-image/control/structure"
        created_images = []

        for i in range(count):
            # Vary the control strength slightly for each variation
            control_strength = 0.6 + (i * 0.05)  # 0.6, 0.65, 0.7, etc.

            files = {'image': image_data}
            data_params = {
                'prompt': variation_prompt,
                'control_strength': min(control_strength, 0.9),
                'output_format': 'png'
            }

            headers = {
                "Authorization": f"Bearer {stability_key}",
                "Accept": "image/*"
            }

            api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

            if api_response.status_code == 200:
                # Save the variation to disk (not as data URI!)
                result_image_data = api_response.content

                # Create unique filename and save to disk
                filename = f'variation_{i+1}_{uuid.uuid4().hex[:8]}.png'
                filepath = os.path.join('generated_images', request.user.username, filename)
                saved_path = default_storage.save(filepath, ContentFile(result_image_data))
                image_url = default_storage.url(saved_path)

                new_image = ImageHistory.objects.create(
                    user=request.user,
                    prompt=f"Variation {i+1} of image #{seq_num}",
                    file_path=saved_path,  # Save FILE PATH, not data URI!
                    filename=filename,
                    model_used="stability-structure-control",
                    project=project
                )

                # Session 142: Track agent contribution
                try:
                    from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                    agent = UnifiedAgentTemplate.objects.get(name='image-generation-agent')
                    AgentContribution.objects.create(
                        agent=agent,
                        image=new_image,
                        project=project,
                        contribution_type='generation',
                        task_description="Generated image using image-generation-agent",
                        execution_time_seconds=0.0
                    )
                    logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
                except Exception as e:
                    logger.error(f"❌ Failed to create agent contribution: {e}")
                    logger.error(f"❌ Failed to create agent contribution: {e}")

                created_images.append({
                    'image_id': str(new_image.id),
                    'image_url': image_url,  # Return actual URL, not data URI
                    'sequential_number': new_image.get_sequential_number()
                })
                logger.info(f"✅ Created variation {i+1}/{count}: {new_image.id} → {saved_path}")
            else:
                error_detail = api_response.text
                logger.error(f"❌ Variation {i+1} failed (status {api_response.status_code}): {error_detail}")

        if not created_images:
            # Return detailed error message with first failure reason
            error_msg = 'Failed to create any variations - check server logs for API error details'
            return JsonResponse({'success': False, 'error': error_msg}, status=500)

        return JsonResponse({
            'success': True,
            'count': len(created_images),
            'images': created_images
        })

    except Exception as e:
        logger.error(f"❌ Create variations error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def search_and_replace_view(request):
    """
    Search and replace objects in an image (erase functionality).
    Accepts JSON: {image_id: uuid, search_prompt: str, replace_prompt: str (optional), project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        search_prompt = data.get('search_prompt')
        replace_prompt = data.get('replace_prompt', '')  # Empty means remove/erase
        project_id = data.get('project_id')

        if not image_id or not search_prompt:
            return JsonResponse({'success': False, 'error': 'image_id and search_prompt required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        action = "Erasing" if not replace_prompt else "Replacing"
        logger.info(f"🎯 {action} '{search_prompt}' in image {image_id} (sequential #{seq_num})")
        logger.info(f"   Replace prompt: '{replace_prompt if replace_prompt else '(seamless blend - text removal mode)'}'")  # Session 197: Debug logging

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Call Stability AI search-and-replace API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"

        files = {'image': image_data}

        # Session 197/198: Improved text removal logic
        # When removing text (no replace_prompt), use a smarter replacement that preserves the image
        # Session 198 v2: "seamless continuation" creates weird shapes on graphics/logos
        # Using a more aggressive removal prompt that works better for both photos and graphics
        if not replace_prompt:
            # For text removal, tell the API to remove completely and fill with background
            effective_prompt = "nothing, empty space, blank area, remove completely"
        else:
            effective_prompt = replace_prompt

        data_params = {
            'search_prompt': search_prompt,
            'prompt': effective_prompt,
            'output_format': 'png'
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-and-replace failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Search and replace failed: {api_response.text}'}, status=500)

        # Save the result image to file (NOT as data URI!)
        result_image_data = api_response.content

        # Generate unique filename and save to disk
        filename = f'search_replace_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(result_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved search-and-replace result: {saved_path}")

        # Create new image history entry
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        prompt_desc = f"Removed '{search_prompt}'" if not replace_prompt else f"Replaced '{search_prompt}' with '{replace_prompt}'"
        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"{prompt_desc} from image #{seq_num}",
            file_path=saved_path,  # Save FILE PATH, not data URI!
            filename=filename,
            model_used="stability-search-replace",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Search and replace successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Search and replace error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def recolor_image_view(request):
    """
    Recolor specific objects/areas in an image.
    Accepts JSON: {image_id: uuid, select_prompt: str, color: str (optional), project_id: uuid (optional)}
    """
    try:
        data = json.loads(request.body)
        image_id = data.get('image_id')
        select_prompt = data.get('select_prompt', 'entire image')
        color = data.get('color', 'vibrant colors')
        project_id = data.get('project_id')

        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required'}, status=400)

        # Get the image from history
        from content.models import ImageHistory, CreativeProject
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Recoloring '{select_prompt}' to '{color}' in image {image_id} (sequential #{seq_num})")

        # Get image data (handle both data URIs and file paths)
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Get API key
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({'success': False, 'error': 'Stability AI API key not configured'}, status=500)

        # Call Stability AI search-and-recolor API
        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"

        files = {'image': image_data}
        data_params = {
            'prompt': f'{select_prompt}, {color}',
            'select_prompt': select_prompt,
            'output_format': 'png'
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-and-recolor failed: {api_response.text}")
            return JsonResponse({'success': False, 'error': f'Recolor failed: {api_response.text}'}, status=500)

        # Save the result image
        result_image_data = api_response.content
        image_base64 = base64.b64encode(result_image_data).decode('utf-8')

        # Create new image history entry
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Recolored '{select_prompt}' to '{color}' from image #{seq_num}",
            file_path=f"data:image/png;base64,{image_base64}",
            model_used="stability-search-recolor",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description="Edited image using image-editing-agent",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {{ new_image.id }}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Recolor successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Recolor error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# SESSION 148: PROJECT EXPORT ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_zip(request, project_id):
    """
    Export complete project as ZIP archive
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/zip/

    Returns: Binary ZIP file with all assets + metadata.json + README.txt
    """
    import io
    import json
    from zipfile import ZipFile
    from pathlib import Path
    from datetime import datetime
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset

    try:
        # Get project
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get all content
        images = ImageHistory.objects.filter(project_id=project_id, user=request.user)
        videos = VideoHistory.objects.filter(project_id=project_id, user=request.user)
        models = MiniFigAsset.objects.filter(project_id=project_id, user=request.user)

        # Get stats
        stats = calculate_project_stats(project_id, request.user)

        # Create in-memory ZIP
        zip_buffer = io.BytesIO()

        with ZipFile(zip_buffer, 'w') as zip_file:
            # Add metadata.json
            metadata = {
                'project': {
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description or '',
                    'created_at': project.created_at.isoformat(),
                },
                'stats': stats,
                'exported_at': datetime.now().isoformat(),
                'exported_by': request.user.email
            }
            zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))

            # Add README
            readme = f"""# {project.name}

{project.description or 'No description provided'}

## Contents
- Images: {len(images)}
- Videos: {len(videos)}
- 3D Models: {len(models)}

## Statistics
- Total Assets: {stats['content']['total']}
- Unique Agents: {stats['collaboration']['unique_agents_count']}
- Total Execution Time: {stats['collaboration']['execution_time_seconds']} seconds
- Decisions Made: {stats['collaboration']['decisions_count']}

## Timeline
- Created: {stats['timeline']['created_at']}
- Last Active: {stats['timeline']['last_active']}

## Exported
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated by AI Content Studio
https://github.com/anthropics/unified-donkey-betz
"""
            zip_file.writestr('README.txt', readme)

            # Add images
            for i, img in enumerate(images):
                if img.file_path and not img.file_path.startswith('data:'):
                    file_path = img.file_path
                    if os.path.exists(file_path):
                        zip_file.write(file_path, f'images/image-{i+1}{Path(file_path).suffix}')

            # Add videos
            for i, vid in enumerate(videos):
                if vid.video_url and not vid.video_url.startswith('http'):
                    # Local file
                    if os.path.exists(vid.video_url):
                        zip_file.write(vid.video_url, f'videos/video-{i+1}.mp4')

            # Add 3D models
            for i, model in enumerate(models):
                if model.three_d_file and os.path.exists(model.three_d_file):
                    zip_file.write(model.three_d_file, f'models-3d/model-{i+1}.glb')

        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}.zip"'

        logger.info(f"✅ Project exported as ZIP: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export ZIP error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_pdf(request, project_id):
    """
    Export project as professional PDF portfolio
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/pdf/

    Returns: Binary PDF file with images, stats, and timeline
    """
    import io
    from datetime import datetime
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors

    try:
        project = CreativeProject.objects.get(id=project_id, user=request.user)
        stats = calculate_project_stats(project_id, request.user)

        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, spaceAfter=12)

        # Build PDF content
        story = []

        # Title page
        story.append(Paragraph(project.name, title_style))
        if project.description:
            story.append(Paragraph(project.description, styles['Normal']))
        story.append(Spacer(1, 0.5*inch))

        # Stats section
        story.append(Paragraph('Project Statistics', heading_style))

        stats_data = [
            ['Metric', 'Value'],
            ['Images', str(stats['content']['images'])],
            ['Videos', str(stats['content']['videos'])],
            ['3D Models', str(stats['content']['models'])],
            ['Total Assets', str(stats['content']['total'])],
            ['Unique Agents', str(stats['collaboration']['unique_agents_count'])],
            ['Execution Time', f"{stats['collaboration']['execution_time_seconds']} seconds"],
            ['Decisions Made', str(stats['collaboration']['decisions_count'])],
        ]

        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))

        # Agent list
        if stats['collaboration']['unique_agents']:
            story.append(Paragraph('Contributing Agents', heading_style))
            agents_text = ', '.join(stats['collaboration']['unique_agents'])
            story.append(Paragraph(agents_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))

        story.append(PageBreak())

        # Images section
        images = ImageHistory.objects.filter(project_id=project_id, user=request.user)
        if images:
            story.append(Paragraph('Image Gallery', heading_style))
            for img in images:
                if img.file_path and not img.file_path.startswith('data:') and os.path.exists(img.file_path):
                    try:
                        # Add image
                        rl_img = RLImage(img.file_path, width=4*inch, height=4*inch, kind='proportional')
                        story.append(rl_img)

                        # Add caption
                        caption = f"<b>Image #{img.get_sequential_number()}</b>: {img.prompt or 'No prompt'}"
                        story.append(Paragraph(caption, styles['Normal']))
                        story.append(Spacer(1, 0.3*inch))
                    except Exception as e:
                        logger.warning(f"Couldn't add image to PDF: {e}")

        # Videos section
        videos = VideoHistory.objects.filter(project_id=project_id, user=request.user)
        if videos:
            story.append(PageBreak())
            story.append(Paragraph('Video Gallery', heading_style))
            for vid in videos:
                video_info = f"""
                <b>Video #{vid.get_sequential_number()}</b><br/>
                Prompt: {vid.prompt or 'No prompt'}<br/>
                Status: {vid.status}
                """
                story.append(Paragraph(video_info, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        # 3D Models section
        models = MiniFigAsset.objects.filter(project_id=project_id, user=request.user)
        if models:
            story.append(PageBreak())
            story.append(Paragraph('3D Models', heading_style))
            for model in models:
                model_info = f"""
                <b>Model #{model.get_sequential_number() if hasattr(model, 'get_sequential_number') else 'N/A'}</b><br/>
                Status: {model.status}
                """
                story.append(Paragraph(model_info, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))

        # Footer
        story.append(PageBreak())
        story.append(Paragraph('Generated by AI Content Studio', styles['Normal']))
        story.append(Paragraph(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        # Build PDF
        doc.build(story)

        # Prepare response
        pdf_buffer.seek(0)
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_portfolio.pdf"'

        logger.info(f"✅ Project exported as PDF: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export PDF error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_project_csv(request, project_id):
    """
    Export project statistics as CSV
    Session 148: Project Export

    GET /api/projects/<uuid:project_id>/export/csv/

    Returns: CSV file with stats and agent contributions
    """
    import io
    import csv
    from django.http import HttpResponse
    from content.models import CreativeProject, ImageHistory, VideoHistory, MiniFigAsset
    from core.models.agents_registry import AgentContribution
    from collections import defaultdict

    try:
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Create CSV buffer
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)

        # Header
        writer.writerow(['Project Export - AI Content Studio'])
        writer.writerow([])
        writer.writerow(['Project Information'])
        writer.writerow(['Name', project.name])
        writer.writerow(['Description', project.description or ''])
        writer.writerow(['Created', project.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])

        # Content summary
        writer.writerow(['Content Summary'])
        writer.writerow(['Content Type', 'Count'])
        images_count = ImageHistory.objects.filter(project_id=project_id, user=request.user).count()
        videos_count = VideoHistory.objects.filter(project_id=project_id, user=request.user).count()
        models_count = MiniFigAsset.objects.filter(project_id=project_id, user=request.user).count()
        writer.writerow(['Images', images_count])
        writer.writerow(['Videos', videos_count])
        writer.writerow(['3D Models', models_count])
        writer.writerow(['Total', images_count + videos_count + models_count])
        writer.writerow([])

        # Agent contributions
        writer.writerow(['Agent Contributions'])
        writer.writerow(['Agent', 'Images', 'Videos', '3D Models', 'Total', 'Execution Time (s)'])
        contributions = AgentContribution.objects.filter(project_id=project_id)

        # Group by agent
        agent_stats = defaultdict(lambda: {'images': 0, 'videos': 0, 'models': 0, 'time': 0})

        for contrib in contributions:
            agent = contrib.agent.name if contrib.agent else 'Unknown'
            if contrib.image_id:
                agent_stats[agent]['images'] += 1
            if contrib.video_id:
                agent_stats[agent]['videos'] += 1
            if contrib.minifig_asset_id:
                agent_stats[agent]['models'] += 1
            agent_stats[agent]['time'] += contrib.execution_time_seconds or 0

        for agent, stats in sorted(agent_stats.items()):
            total_contributions = stats['images'] + stats['videos'] + stats['models']
            writer.writerow([
                agent,
                stats['images'],
                stats['videos'],
                stats['models'],
                total_contributions,
                round(stats['time'], 2)
            ])

        writer.writerow([])
        writer.writerow(['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

        # Prepare response
        csv_buffer.seek(0)
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{project.name.replace(" ", "_")}_stats.csv"'

        logger.info(f"✅ Project exported as CSV: {project.name}")
        return response

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project not found: {project_id}")
        return HttpResponse('Project not found', status=404)
    except Exception as e:
        logger.error(f"❌ Export CSV error: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Export failed: {str(e)}', status=500)


# ========================================
# SESSION 151: ADVANCED IMAGE EDITING SUITE
# ========================================
# Note: search_and_replace_view already exists at line 11735
# Adding creative_upscale_view as new capability

@rate_limit('image_processing')  # Phase 2 P1: Rate limit image operations (20 requests/min)
def creative_upscale_view(request):
    """
    Creative upscale with prompt - upscale image AND add creative details based on prompt.
    Not just pixel upscaling - actually generates new details!

    Session 151: Advanced Image Editing Suite
    Accepts JSON: {
        image_id: uuid,
        prompt: str (what details to add/enhance),
        creativity: float (0.0-0.35, default 0.3),
        project_id: uuid (optional)
    }
    Note: @login_required removed to support internal RequestFactory calls from agents
    """
    try:
        # Manual authentication check for web requests
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"⚠️ Unauthenticated request to creative_upscale_view")
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

        data = json.loads(request.body)
        image_id = data.get('image_id')
        prompt = data.get('prompt', '').strip()
        creativity = float(data.get('creativity', 0.3))
        project_id = data.get('project_id')

        if not image_id or not prompt:
            return JsonResponse({
                'success': False,
                'error': 'image_id and prompt required'
            }, status=400)

        # Validate creativity range
        if not (0.0 <= creativity <= 0.35):
            creativity = 0.3

        # Get the image from history
        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'}, status=404)

        seq_num = image.get_sequential_number()
        logger.info(f"✨ Creative upscale image {image_id} (#{seq_num}) with prompt: '{prompt}'")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI creative upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return JsonResponse({
                'success': False,
                'error': 'Stability AI API key not configured'
            }, status=500)

        url = "https://api.stability.ai/v2beta/stable-image/upscale/creative"

        files = {"image": image_data}
        data_params = {
            "prompt": prompt,
            "creativity": creativity,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=90)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI creative upscale failed: {api_response.text}")
            return JsonResponse({
                'success': False,
                'error': f'Creative upscale failed: {api_response.text}'
            }, status=500)

        # Save the upscaled image
        upscaled_image_data = api_response.content

        filename = f'creative_upscale_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', request.user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        logger.info(f"✅ Saved creative upscale image: {saved_path}")

        # Create new image history entry
        from content.models import CreativeProject
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass

        new_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Creative upscale from image #{seq_num}: {prompt}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-creative-upscale",
            project=project
        )

        # Session 142: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='image-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=new_image,
                project=project,
                contribution_type='editing',
                task_description=f"Creative upscale with details: {prompt}",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ Agent contribution tracked for image {new_image.id}")
        except Exception as e:
            logger.error(f"❌ Failed to create agent contribution: {e}")

        logger.info(f"✅ Creative upscale successful: {new_image.id}")

        return JsonResponse({
            'success': True,
            'image_id': str(new_image.id),
            'image_url': new_image.file_path,
            'sequential_number': new_image.get_sequential_number()
        })

    except Exception as e:
        logger.error(f"❌ Creative upscale error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _execute_strategic_review(user, parameters):
    """
    Execute strategic review by co-leadership agents.

    Session 189: Get executive team review BEFORE generating content.
    This ensures research findings are analyzed by CTO, COO, and Creative Director
    who then provide strategic direction for the content creation.

    Parameters:
        research_topic (str): The original research topic
        research_findings (str): Summary of web search results
        content_type (str): Type of content to create (logo, banner, etc.)
        user_context (str): Additional user context

    Returns:
        dict: {
            'success': True,
            'strategic_direction': {
                'key_insights': [...],
                'creative_recommendations': [...],
                'prompt_suggestions': [...],
                'technical_considerations': [...],
                'executive_summary': str
            },
            'participants': ['CTO', 'COO', 'Creative Director'],
            'meeting_summary': str
        }
    """
    try:
        research_topic = parameters.get('research_topic', '').strip()
        research_findings = parameters.get('research_findings', '').strip()
        content_type = parameters.get('content_type', 'general')
        user_context = parameters.get('user_context', '')

        if not research_topic or not research_findings:
            raise ValueError("research_topic and research_findings are required")

        logger.info(f"🏢 Strategic Review: Analyzing research for '{research_topic}'")
        logger.info(f"📋 Content type: {content_type}, Findings length: {len(research_findings)} chars")

        # Use MeetingCoordinatorAgent for strategic boardroom discussion
        from core.agents.executive import MeetingCoordinatorAgent
        coordinator = MeetingCoordinatorAgent(user=user)

        # Build strategic review topic with research context
        meeting_topic = f"""Strategic Review: {research_topic}

RESEARCH FINDINGS:
{research_findings[:2000]}

CONTENT TYPE TO CREATE: {content_type}
USER CONTEXT: {user_context}

OBJECTIVE: Provide strategic direction and creative recommendations for content creation based on this research.
Include specific prompt suggestions that incorporate the research insights."""

        # Start boardroom meeting with relevant executives
        # Include Creative Director for this creative-focused review
        participants = ['CTOAgent', 'COOAgent']

        # Check if CreativeDirectorAgent exists, add if so
        from core.models.agents_registry import UnifiedAgentTemplate
        try:
            UnifiedAgentTemplate.objects.get(name='CreativeDirectorAgent')
            participants.append('CreativeDirectorAgent')
        except UnifiedAgentTemplate.DoesNotExist:
            logger.info("CreativeDirectorAgent not found, proceeding with CTO + COO")

        meeting_results = coordinator.start_meeting(
            topic=meeting_topic,
            participants=participants
        )

        # Process meeting results into strategic direction format
        if meeting_results.get('status') != 'complete':
            raise Exception(f"Strategic review failed: {meeting_results.get('error', 'Unknown error')}")

        # Extract key insights and recommendations from agent responses
        key_insights = []
        creative_recommendations = []
        prompt_suggestions = []
        technical_considerations = []

        for agent_name, response in meeting_results.get('agent_responses', {}).items():
            # Extract insights based on agent type
            if 'CTO' in agent_name:
                technical_considerations.append(f"[CTO] {response}")
            elif 'COO' in agent_name:
                key_insights.append(f"[Operations] {response}")
            elif 'Creative' in agent_name:
                creative_recommendations.append(f"[Creative] {response}")

        # Generate prompt suggestions based on decisions
        decisions = meeting_results.get('decisions', [])
        for i, decision in enumerate(decisions[:3]):
            prompt_suggestions.append(decision)

        # Build executive summary
        executive_summary = meeting_results.get('summary', 'Strategic review complete.')

        result = {
            'success': True,
            'strategic_direction': {
                'key_insights': key_insights,
                'creative_recommendations': creative_recommendations,
                'prompt_suggestions': prompt_suggestions if prompt_suggestions else [
                    f"Modern {content_type} design incorporating research trends",
                    f"Professional {content_type} with industry best practices",
                    f"Creative {content_type} that stands out from competitors"
                ],
                'technical_considerations': technical_considerations,
                'executive_summary': executive_summary
            },
            'participants': participants,
            'meeting_summary': executive_summary,
            'action_items': meeting_results.get('action_items', []),
            'research_topic': research_topic,
            'content_type': content_type
        }

        logger.info(f"✅ Strategic Review complete: {len(prompt_suggestions)} prompt suggestions, "
                    f"{len(key_insights)} insights from {len(participants)} executives")

        return result

    except Exception as e:
        logger.error(f"❌ Error in _execute_strategic_review: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


# =============================================================================
# CLEAN ARCHITECTURE AGENT WRAPPERS
# Session 269: Phase 4 - Internal functions for agent tool execution
# These functions are called by the clean architecture agents (not views)
# =============================================================================

def _execute_upscale(user, parameters, session=None):
    """
    Internal function for upscaling images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, scale_factor, creative_upscale
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        if not image_id:
            return {'success': False, 'error': 'image_id required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"📈 Agent upscaling image {image_id} (sequential #{seq_num})")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI upscale API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/upscale/conservative"
        files = {"image": image_data}
        data_params = {
            "prompt": "high quality upscale",
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI upscale failed: {api_response.text}")
            return {'success': False, 'error': f'Upscale failed: {api_response.text}'}

        # Save the upscaled image
        upscaled_image_data = api_response.content
        filename = f'upscaled_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(upscaled_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Upscaled from image #{seq_num}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-upscale-4x",
        )

        logger.info(f"✅ Agent upscaled image: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image upscaled successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent upscale error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_remove_background(user, parameters, session=None):
    """
    Internal function for removing image backgrounds.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        if not image_id:
            return {'success': False, 'error': 'image_id required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🎭 Agent removing background from image {image_id} (#{seq_num})")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI remove-background API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/remove-background"
        files = {"image": image_data}
        data_params = {"output_format": "png"}

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI remove-bg failed: {api_response.text}")
            return {'success': False, 'error': f'Remove background failed: {api_response.text}'}

        # Save the processed image
        processed_image_data = api_response.content
        filename = f'nobg_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(processed_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Background removed from image #{seq_num}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-remove-bg",
        )

        logger.info(f"✅ Agent removed background: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Background removed successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent remove-bg error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_create_variations(user, parameters, session=None):
    """
    Internal function for creating image variations.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, count, variation_strength
        session: Optional session for tracking

    Returns:
        Dict with success, images list
    """
    try:
        image_id = parameters.get('image_id')
        count = parameters.get('count', 3)
        strength = parameters.get('variation_strength', 0.5)

        if not image_id:
            return {'success': False, 'error': 'image_id required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Agent creating {count} variations from image {image_id} (#{seq_num})")

        # For now, use image-to-image with variation prompts
        # This would use the Stability AI img2img endpoint
        return {
            'success': False,
            'error': 'Image variations not yet implemented in clean architecture'
        }

    except Exception as e:
        logger.error(f"❌ Agent variations error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_recolor(user, parameters, session=None):
    """
    Internal function for recoloring images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, target_color, new_color
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        target_color = parameters.get('target_color')
        new_color = parameters.get('new_color')

        if not image_id or not target_color or not new_color:
            return {'success': False, 'error': 'image_id, target_color, and new_color required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🎨 Agent recoloring image {image_id} (#{seq_num}): {target_color} → {new_color}")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI search-and-recolor API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-recolor"
        files = {"image": image_data}
        data_params = {
            "prompt": f"Change {target_color} to {new_color}",
            "select_prompt": target_color,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI recolor failed: {api_response.text}")
            return {'success': False, 'error': f'Recolor failed: {api_response.text}'}

        # Save the recolored image
        recolored_image_data = api_response.content
        filename = f'recolor_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(recolored_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Recolored from image #{seq_num}: {target_color} → {new_color}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-recolor",
        )

        logger.info(f"✅ Agent recolored image: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image recolored successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent recolor error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_search_replace(user, parameters, session=None):
    """
    Internal function for search-and-replace in images.
    Called by ImageEditingAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, search_prompt, replace_prompt
        session: Optional session for tracking

    Returns:
        Dict with success, image_id, image_url
    """
    try:
        image_id = parameters.get('image_id')
        search_prompt = parameters.get('search_prompt')
        replace_prompt = parameters.get('replace_prompt')

        if not image_id or not search_prompt or not replace_prompt:
            return {'success': False, 'error': 'image_id, search_prompt, and replace_prompt required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🔄 Agent search-replace on image {image_id} (#{seq_num}): {search_prompt} → {replace_prompt}")

        # Get image data
        if image.file_path.startswith('data:'):
            image_data = base64.b64decode(image.file_path.split(',')[1])
        else:
            file_full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            with open(file_full_path, 'rb') as f:
                image_data = f.read()

        # Call Stability AI search-and-replace API
        stability_key = os.getenv('STABILITY_API_KEY') or settings.EXTERNAL_API_KEYS.get('STABILITY_API_KEY')
        if not stability_key:
            return {'success': False, 'error': 'Stability AI API key not configured'}

        url = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"
        files = {"image": image_data}
        data_params = {
            "prompt": replace_prompt,
            "search_prompt": search_prompt,
            "output_format": "png"
        }

        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*"
        }

        api_response = requests.post(url, headers=headers, files=files, data=data_params, timeout=60)

        if api_response.status_code != 200:
            logger.error(f"❌ Stability AI search-replace failed: {api_response.text}")
            return {'success': False, 'error': f'Search-replace failed: {api_response.text}'}

        # Save the modified image
        modified_image_data = api_response.content
        filename = f'edited_{uuid.uuid4().hex[:8]}.png'
        filepath = os.path.join('generated_images', user.username, filename)
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        saved_path = default_storage.save(filepath, ContentFile(modified_image_data))
        image_url = default_storage.url(saved_path)

        # Create new image history entry
        new_image = ImageHistory.objects.create(
            user=user,
            prompt=f"Edited from image #{seq_num}: replaced {search_prompt} with {replace_prompt}",
            file_path=saved_path,
            filename=filename,
            model_used="stability-search-replace",
        )

        logger.info(f"✅ Agent search-replace complete: {new_image.id}")

        return {
            'success': True,
            'image_id': str(new_image.id),
            'image_url': image_url,
            'sequential_number': new_image.get_sequential_number(),
            'message': f"Image edited successfully (#{new_image.get_sequential_number()})"
        }

    except Exception as e:
        logger.error(f"❌ Agent search-replace error: {e}")
        return {'success': False, 'error': str(e)}


def _execute_convert_to_3d(user, parameters, session=None):
    """
    Internal function for converting images to 3D models.
    Called by ThreeDAgent.

    Args:
        user: Django user object
        parameters: Dict with image_id, output_format, quality
        session: Optional session for tracking

    Returns:
        Dict with success, model_url
    """
    try:
        image_id = parameters.get('image_id')
        output_format = parameters.get('output_format', 'glb')
        quality = parameters.get('quality', 'standard')

        if not image_id:
            return {'success': False, 'error': 'image_id required'}

        from content.models import ImageHistory
        try:
            image = ImageHistory.objects.get(id=image_id, user=user)
        except ImageHistory.DoesNotExist:
            return {'success': False, 'error': 'Image not found'}

        seq_num = image.get_sequential_number()
        logger.info(f"🎮 Agent converting image {image_id} (#{seq_num}) to 3D ({output_format})")

        # Get image URL for Replicate API
        if image.file_path.startswith('data:'):
            # Data URI - would need to upload first
            return {'success': False, 'error': 'Data URI images not supported for 3D conversion'}
        else:
            image_url = f"{settings.MEDIA_URL}{image.file_path}"

        # Call Replicate API for 3D conversion
        import replicate
        replicate_key = os.getenv('REPLICATE_API_TOKEN') or settings.EXTERNAL_API_KEYS.get('REPLICATE_API_TOKEN')
        if not replicate_key:
            return {'success': False, 'error': 'Replicate API key not configured'}

        os.environ['REPLICATE_API_TOKEN'] = replicate_key

        # Use TripoSR or similar model
        output = replicate.run(
            "stability-ai/stable-fast-3d:5ddcbc15a0c1e0154cfe0969f9ae1e06f3d5e0bcc44119f7c7e29f23b7a04a05",
            input={
                "image": image_url,
            }
        )

        if output:
            return {
                'success': True,
                'model_url': str(output),
                'format': output_format,
                'message': f"3D model generated from image #{seq_num}"
            }
        else:
            return {'success': False, 'error': '3D conversion returned no output'}

    except Exception as e:
        logger.error(f"❌ Agent 3D conversion error: {e}")
        return {'success': False, 'error': str(e)}


# Session 990: Moved to core/views_audio.py — re-export for backwards compatibility
def _execute_generate_voice(user, parameters, session=None):
    from core.views_audio import _execute_generate_voice as _impl
    return _impl(user, parameters, session)


def _execute_add_voiceover(user, parameters, session=None):
    from core.views_audio import _execute_add_voiceover as _impl
    return _impl(user, parameters, session)
