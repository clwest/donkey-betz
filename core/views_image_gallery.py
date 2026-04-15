"""
Image views — gallery functions.
"""

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

from django.views.decorators.csrf import csrf_exempt


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

                    # Session 122: Track generated image for intelligent chaining
                    # Apr 2026: Fixed — was calling undefined method on cached PA object.
                    # Now writes directly to cache instead.
                    try:
                        from django.core.cache import cache
                        from django.utils import timezone
                        if history:
                            asset_type = 'image'
                            if 'logo' in prompt.lower():
                                asset_type = 'logo'
                            elif any(word in prompt.lower() for word in ['character', 'mascot', 'avatar']):
                                asset_type = 'character'
                            elif any(word in prompt.lower() for word in ['product', 'merchandise']):
                                asset_type = 'product'

                            cache_key = f'recent_assets:{user.id}'
                            assets = cache.get(cache_key, {'images': [], 'videos': []})
                            assets['images'].append({
                                'id': str(history.id),
                                'url': url,
                                'prompt': prompt,
                                'type': asset_type,
                                'timestamp': timezone.now().isoformat(),
                            })
                            assets['images'] = assets['images'][-10:]  # Keep last 10
                            cache.set(cache_key, assets, 3600)  # 1 hour TTL
                            logger.info(f"Tracked image {history.id} as {asset_type}")
                    except Exception as e:
                        logger.warning(f"Failed to track image in cache: {e}")

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
        workspace_id = request.query_params.get('workspace')  # Filter by workspace

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

            # Filter by workspace — strict (only shows workspace-linked media)
            if workspace_id:
                image_queryset = image_queryset.filter(workspace_id=workspace_id)

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

            # Filter by workspace if specified
            if workspace_id:
                video_queryset = video_queryset.filter(workspace_id=workspace_id)

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

            # Filter by workspace if specified
            if workspace_id:
                audio_queryset = audio_queryset.filter(workspace_id=workspace_id)

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



# Session 1083 (Rigby audit): 4 undefined names — module-level imports
# triggered circular init cycles. Resolved via lazy proxies so the
# existing call sites stay unchanged but the actual symbols don't
# bind until first call.
def generate_with_replicate(*args, **kwargs):
    from core.views_image_generate import generate_with_replicate as _f
    return _f(*args, **kwargs)

def save_to_history(*args, **kwargs):
    from core.image_views.session import save_to_history as _f
    return _f(*args, **kwargs)

class _ImageHistoryProxy:
    def __getattr__(self, name):
        from content.models import ImageHistory as _ih
        return getattr(_ih, name)

ImageHistory = _ImageHistoryProxy()
