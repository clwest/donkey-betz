"""
Video Generation Views

Handles video generation requests using RunwayML Gen-3 Alpha.
"""

import json
import logging
import requests
from io import BytesIO
from PIL import Image
import tempfile
import os
import subprocess

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from content.models import ContentGeneration, VideoHistory, ImageHistory
from content.video_provider import runway_provider
from django.utils import timezone
from core.utils.url_validator import validate_url_for_download, validate_url_permissive

# Phase 2 P1: Rate limiting for video operations
from core.decorators import rate_limit
# Phase 2 P1: Input validation
from core.validators import validate_prompt, sanitize_prompt, validate_uuid, validate_numeric_range, validate_url
# Phase 2 P1: Safe error handling

logger = logging.getLogger(__name__)

# Time module for timestamp generation (Session 167)
import time


# =============================================================================
# Session 185: Safe subprocess runner with timeout
# Prevents hung ffmpeg processes on corrupt files or infinite streams
# =============================================================================

def _run_ffmpeg(cmd, timeout=None, long_operation=False):
    """
    Run ffmpeg command with timeout protection.

    Args:
        cmd: Command list to execute
        timeout: Custom timeout in seconds (optional)
        long_operation: If True, use FFMPEG_TIMEOUT_LONG setting

    Returns:
        subprocess.CompletedProcess result

    Raises:
        subprocess.TimeoutExpired: If command times out
    """
    if timeout is None:
        timeout = settings.FFMPEG_TIMEOUT_LONG if long_operation else settings.FFMPEG_TIMEOUT

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"ffmpeg operation timed out after {timeout}s: {' '.join(cmd[:5])}...")
        raise


# =============================================================================
# Session 168: Module-level video helper functions
# Used by render_professional, apply_lut, and grade_professional
# =============================================================================

def _resolve_video_by_id(video_id, user, project_id=None):
    """
    Session 168: Resolve video ID (numeric or UUID) to VideoHistory object.

    Supports:
    - UUID strings: Returns VideoHistory directly
    - Numeric IDs: Maps to nth video in project or all user videos

    Args:
        video_id: String UUID or numeric ID (1-based)
        user: Django User object
        project_id: Optional project UUID to scope the search

    Returns:
        VideoHistory object or None if not found
    """
    if isinstance(video_id, str):
        video_id = video_id.strip().strip('"').strip("'")

    # Try as UUID first
    try:
        import uuid as uuid_module
        video_uuid = uuid_module.UUID(video_id)
        return VideoHistory.objects.filter(id=video_uuid, user=user).first()
    except (ValueError, AttributeError, TypeError):
        pass

    # Try as numeric ID
    try:
        numeric_id = int(video_id)
        if numeric_id < 1:
            return None

        # Scope by project if provided, order by created_at to match frontend
        if project_id:
            videos = VideoHistory.objects.filter(user=user, project_id=project_id).order_by('created_at')
            scope = 'project'
        else:
            videos = VideoHistory.objects.filter(user=user).order_by('created_at')
            scope = 'all videos'

        if numeric_id > videos.count():
            return None

        video = videos[numeric_id - 1]
        logger.info(f"🔄 [Session 168] Resolved hybrid ID {numeric_id} → {video.id} (scope: {scope})")
        return video
    except (ValueError, TypeError):
        return None


def _get_video_local_path(video):
    """
    Session 168: Get local filesystem path for a VideoHistory object.

    Handles various URL formats:
    - /media/videos/filename.mp4 -> /full/path/to/media/videos/filename.mp4
    - https://... -> Downloads to temp file
    - Local file path -> Returns as-is

    Args:
        video: VideoHistory object

    Returns:
        String path to local file, or None if not found
    """
    if not video or not video.video_url:
        return None

    video_url = video.video_url

    # Handle relative media paths
    if video_url.startswith('/media/'):
        file_path = video_url[7:]  # Remove '/media/'
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            return full_path
        # Try without 'videos/' prefix if not found
        logger.warning(f"⚠️ Video file not found at: {full_path}")
        return None

    # Handle http/https URLs (Runway uploads, etc.)
    if video_url.startswith('http://') or video_url.startswith('https://'):
        # Session 185: SSRF protection - validate URL before downloading
        is_valid, error = validate_url_for_download(video_url)
        if not is_valid:
            logger.warning(f"🛡️ SSRF Protection blocked URL: {video_url} - {error}")
            return None

        try:
            # Download to temp file
            response = requests.get(video_url, stream=True, timeout=60)
            response.raise_for_status()

            # Determine extension from URL or content type
            ext = 'mp4'
            if '.mov' in video_url.lower():
                ext = 'mov'
            elif '.webm' in video_url.lower():
                ext = 'webm'

            temp_file = tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False)
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.close()
            logger.info(f"📥 Downloaded video to temp file: {temp_file.name}")
            return temp_file.name
        except Exception as e:
            logger.error(f"❌ Failed to download video: {e}")
            return None

    # Assume it's already a local path
    if os.path.exists(video_url):
        return video_url

    return None


def resize_image_for_runway(image_url: str, max_size_mb: int = 5, max_dimension: int = 1920) -> str:
    """
    Download and resize image to meet RunwayML's size requirements.
    Saves resized image to Django media storage and returns new URL.
    """
    try:
        logger.info(f"🔍 Checking image: {image_url[:100]}...")

        # Handle both absolute URLs and relative media paths
        if image_url.startswith('/media/') or image_url.startswith('media/'):
            # Local media file - read from disk
            from django.conf import settings
            import os

            # Remove /media/ prefix if present
            file_path = image_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]  # Remove 'media/'

            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            logger.info(f"📂 Reading local file: {full_path}")

            with open(full_path, 'rb') as f:
                image_data = f.read()

            img = Image.open(BytesIO(image_data))
            original_format = img.format or 'PNG'
        else:
            # Remote URL - download it
            # Session 185: SSRF protection - validate URL before downloading
            is_valid, error = validate_url_permissive(image_url)
            if not is_valid:
                raise ValueError(f"SSRF Protection blocked URL: {error}")

            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content

            img = Image.open(BytesIO(image_data))
            original_format = img.format or 'PNG'

        # Check if image needs resizing
        needs_resize = False
        width, height = img.size

        # Check file size
        original_size_mb = len(image_data) / (1024 * 1024)
        if original_size_mb > max_size_mb:
            needs_resize = True
            logger.info(f"📦 Image too large: {original_size_mb:.2f}MB > {max_size_mb}MB")

        # Check dimensions
        if width > max_dimension or height > max_dimension:
            needs_resize = True
            logger.info(f"📏 Image dimensions too large: {width}x{height}")

        if not needs_resize:
            logger.info(f"✅ Image already meets requirements: {original_size_mb:.2f}MB, {width}x{height}")
            return image_url

        # Resize image maintaining aspect ratio
        if width > height:
            new_width = min(width, max_dimension)
            new_height = int(height * (new_width / width))
        else:
            new_height = min(height, max_dimension)
            new_width = int(width * (new_height / height))

        logger.info(f"🔄 Resizing image: {width}x{height} → {new_width}x{new_height}")

        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # Resize with high-quality resampling
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to BytesIO with compression
        output = BytesIO()
        quality = 85

        # Try different quality levels to get under max_size_mb
        for attempt in range(3):
            output.seek(0)
            output.truncate()
            img.save(output, 'JPEG', quality=quality, optimize=True)

            final_size_mb = len(output.getvalue()) / (1024 * 1024)

            if final_size_mb <= max_size_mb:
                break

            quality -= 10
            logger.info(f"🔄 Reducing quality to {quality}% (size: {final_size_mb:.2f}MB)")

        output.seek(0)
        final_size_mb = len(output.getvalue()) / (1024 * 1024)
        logger.info(f"✅ Resized image: {final_size_mb:.2f}MB, {new_width}x{new_height}, quality={quality}%")

        # Save to Django media storage
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import hashlib
        from datetime import datetime

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        hash_suffix = hashlib.md5(image_url.encode()).hexdigest()[:8]
        filename = f"video_resized/{timestamp}_{hash_suffix}.jpg"

        # Save file
        saved_path = default_storage.save(filename, ContentFile(output.getvalue()))

        # Get full URL
        if hasattr(default_storage, 'url'):
            resized_url = default_storage.url(saved_path)
        else:
            # Fallback to local media URL
            from django.conf import settings
            resized_url = f"{settings.MEDIA_URL}{saved_path}"
            # Make it absolute
            if not resized_url.startswith('http'):
                # Get the current site URL from settings or construct it
                site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                resized_url = f"{site_url}{resized_url}"

        logger.info(f"💾 Saved resized image to: {saved_path}")
        logger.info(f"🔗 New URL: {resized_url}")

        return resized_url

    except Exception as e:
        logger.error(f"❌ Image resize error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return image_url  # Fall back to original


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Set to IsAuthenticated in production
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video generation (5 requests/min)
def text_to_video(request):
    """
    Generate video from text prompt using RunwayML.

    Expected payload:
    {
        "prompt": "A majestic eagle soaring...",
        "duration": 5,
        "quality": "gen3a_turbo",
        "style": "cinematic",
        "enhance_prompt": true,
        "enhancement_level": "advanced"
    }
    """
    try:
        data = request.data

        # Phase 2 P1: Validate prompt
        prompt = data.get('prompt', '').strip()
        is_valid, validation_error = validate_prompt(prompt, min_length=1, max_length=2000)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': validation_error,
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # Sanitize prompt to prevent injection
        prompt = sanitize_prompt(prompt)

        # Extract parameters with defaults
        duration = int(data.get('duration', 4))  # Changed default to 4 for veo3.1 models

        # Phase 2 P1: Validate duration
        dur_valid, dur_error = validate_numeric_range(duration, 2, 10, 'duration')
        if not dur_valid:
            return JsonResponse({'success': False, 'error': dur_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        quality = data.get('quality', 'veo3.1_fast')  # Updated default model
        style = data.get('style', 'realistic')
        enhance_prompt = data.get('enhance_prompt', True)
        enhancement_level = data.get('enhancement_level', 'advanced')
        ratio = data.get('ratio', '1920:1080')  # Default landscape ratio
        
        # Additional options
        kwargs = {}
        if data.get('seed'):
            kwargs['seed'] = data['seed']
        
        # Check for voiceover options (for future implementation)
        include_voiceover = data.get('include_voiceover', False)
        if include_voiceover:
            kwargs['voiceover_script'] = data.get('voiceover_script', '')
            kwargs['voiceover_voice'] = data.get('voiceover_voice', 'default')
            kwargs['voiceover_style'] = data.get('voiceover_style', 'narrative')
        
        # Generate video using RunwayML
        result = runway_provider.text_to_video(
            prompt=prompt,
            duration=duration,
            quality=quality,
            style=style,
            enhance_prompt=enhance_prompt,
            enhancement_level=enhancement_level,
            ratio=ratio,  # Pass ratio parameter
            **kwargs
        )
        
        if not result.success:
            return JsonResponse({
                'success': False,
                'error': result.error_message or 'Failed to generate video'
            }, status=500)
        
        # Store generation request in database
        content = ContentGeneration.objects.create(
            user=request.user,
            prompt=prompt,
            system_prompt=f"Generate a {style} style video",
            generation_config={
                'task_id': result.task_id,
                'duration': duration,
                'quality': quality,
                'style': style,
                'type': 'text_to_video',
                'estimated_time': result.estimated_time,
                'status': 'processing'
            }
        )
        
        return JsonResponse({
            'success': True,
            'task_id': result.task_id,
            'content_id': content.id,
            'status': result.status,
            'estimated_time': result.estimated_time,
            'message': 'Video generation started successfully'
        })
        
    except Exception as e:
        logger.error(f"Text-to-video generation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video generation (5 requests/min)
def image_to_video(request):
    """
    Generate video from image using RunwayML.

    Expected payload:
    {
        "image_url": "https://...",
        "motion_prompt": "Camera slowly zooms in...",
        "duration": 5,
        "quality": "gen3a_turbo",
        "enhance_prompt": true
    }
    """
    try:
        data = request.data

        # Validate required fields
        image_url = data.get('image_url', '').strip()
        image_id = data.get('image_id')

        logger.info(f"🎬 [IMAGE-TO-VIDEO] Received request")
        logger.info(f"   image_url: {image_url}")
        logger.info(f"   image_id: {image_id}")

        if not image_url and not image_id:
            return JsonResponse({
                'success': False,
                'error': 'Image URL or image ID is required',
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # Phase 2 P1: Validate image_url if provided
        if image_url:
            is_valid, url_error = validate_url(image_url)
            if not is_valid:
                return JsonResponse({'success': False, 'error': url_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        # Phase 2 P1: Validate image_id if provided
        if image_id:
            is_valid, uuid_error = validate_uuid(str(image_id))
            if not is_valid:
                return JsonResponse({'success': False, 'error': uuid_error, 'error_code': 'VALIDATION_ERROR'}, status=400)

        motion_prompt = data.get('motion_prompt', '').strip()

        # Phase 2 P1: Validate motion_prompt
        is_valid, prompt_error = validate_prompt(motion_prompt, min_length=1, max_length=2000)
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': prompt_error,
                'error_code': 'VALIDATION_ERROR'
            }, status=400)

        # Sanitize motion prompt
        motion_prompt = sanitize_prompt(motion_prompt)

        # If image_id is provided, try to get the URL from our database
        if image_id and not image_url:
            try:
                # Try to find the image in ContentGeneration
                image_content = ContentGeneration.objects.get(
                    id=image_id,
                    user=request.user
                )
                image_url = image_content.metadata.get('image_url') or image_content.generated_content
            except ContentGeneration.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Image not found'
                }, status=404)

        # CRITICAL: Resize image if too large for RunwayML (max 5MB recommended)
        logger.info(f"🔍 Checking image size for RunwayML compatibility...")
        try:
            resized_url = resize_image_for_runway(image_url, max_size_mb=5, max_dimension=1920)
            if resized_url != image_url:
                logger.info(f"✅ Using resized image")
                image_url = resized_url  # Actually use the resized image!
        except Exception as resize_error:
            logger.warning(f"⚠️  Image resize failed: {resize_error}, using original")

        # Extract parameters with defaults
        duration = int(data.get('duration', 5))
        quality = data.get('quality', 'gen4_turbo')  # Updated default model for image-to-video
        enhance_prompt = data.get('enhance_prompt', True)
        enhancement_level = data.get('enhancement_level', 'advanced')
        ratio = data.get('ratio', '1280:720')  # Default ratio for gen4_turbo
        
        # Additional options
        kwargs = {}
        if data.get('seed'):
            kwargs['seed'] = data['seed']
        
        # Check for voiceover options
        include_voiceover = data.get('include_voiceover', False)
        if include_voiceover:
            kwargs['voiceover_script'] = data.get('voiceover_script', '')
            kwargs['voiceover_voice'] = data.get('voiceover_voice', 'default')
            kwargs['voiceover_style'] = data.get('voiceover_style', 'narrative')
        
        # Generate video using RunwayML
        logger.info(f"🎬 [IMAGE-TO-VIDEO] Calling runway_provider.image_to_video()")
        logger.info(f"   image_url: {image_url}")
        logger.info(f"   motion_prompt: {motion_prompt}")
        logger.info(f"   duration: {duration}")
        logger.info(f"   quality: {quality}")
        logger.info(f"   ratio: {ratio}")

        result = runway_provider.image_to_video(
            image_url=image_url,
            motion_prompt=motion_prompt,
            duration=duration,
            quality=quality,
            enhance_prompt=enhance_prompt,
            ratio=ratio,  # Pass ratio parameter
            **kwargs
        )

        logger.info(f"🎬 [IMAGE-TO-VIDEO] runway_provider result: success={result.success}, error={result.error_message}")
        
        if not result.success:
            return JsonResponse({
                'success': False,
                'error': result.error_message or 'Failed to generate video'
            }, status=500)
        
        # Store generation request in database  
        content = ContentGeneration.objects.create(
            user=request.user,
            prompt=motion_prompt,
            status='processing',
            metadata={
                'task_id': result.task_id,
                'source_image': image_url,
                'image_id': image_id,
                'duration': duration,
                'quality': quality,
                'type': 'image_to_video',
                'estimated_time': result.estimated_time
            }
        )
        
        return JsonResponse({
            'success': True,
            'task_id': result.task_id,
            'content_id': content.id,
            'status': result.status,
            'estimated_time': result.estimated_time,
            'message': 'Video generation started successfully'
        })
        
    except Exception as e:
        logger.error(f"Image-to-video generation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_video_status(request, task_id):
    """
    Check the status of a video generation task.
    
    Returns:
    {
        "status": "pending|processing|completed|failed",
        "progress": 0-100,
        "video_url": "...",
        "thumbnail_url": "...",
        "duration": 5,
        "error": "..."
    }
    """
    try:
        # Check status with RunwayML
        result = runway_provider.check_status(task_id)
        
        # Update database if we have a matching content
        try:
            # Session 70: Try both metadata (old) and generation_config (brand videos)
            content = None
            try:
                content = ContentGeneration.objects.get(
                    user=request.user,
                    metadata__task_id=task_id
                )
            except ContentGeneration.DoesNotExist:
                # Brand videos store task_id in generation_config
                content = ContentGeneration.objects.get(
                    user=request.user,
                    generation_config__task_id=task_id
                )
            
            # Update status
            if result.status == 'completed':
                content.status = 'completed'
                content.file_url = result.video_url
                content.thumbnail_url = result.thumbnail_url
                metadata = content.metadata or {}
                metadata['video_url'] = result.video_url
                metadata['thumbnail_url'] = result.thumbnail_url
                metadata['actual_duration'] = result.duration
                content.metadata = metadata
                content.save()

                # Save to VideoHistory for gallery
                video_type = metadata.get('type', 'text_to_video')
                model_used = metadata.get('quality', 'veo3.1_fast')

                # Try to find source image if image-to-video
                source_image = None
                if video_type == 'image_to_video' and metadata.get('image_id'):
                    try:
                        source_image = ImageHistory.objects.get(id=metadata['image_id'])
                    except ImageHistory.DoesNotExist:
                        pass

                # Session 70: Use requested duration as fallback if Runway returns 0
                video_duration = result.duration
                if video_duration == 0:
                    # Try generation_config first (brand videos), then metadata
                    config = content.generation_config or {}
                    video_duration = config.get('duration') or metadata.get('duration', 8)
                    logger.info(f"⚠️ Runway returned duration=0, using fallback: {video_duration}s")

                # Session 96: Download video to local storage (prevent expired CDN URLs)
                local_video_url = result.video_url
                try:
                    import requests
                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage

                    # Download video from CDN
                    logger.info(f"📥 Downloading video from CDN: {result.video_url[:80]}...")
                    response = requests.get(result.video_url, timeout=120, stream=True)
                    response.raise_for_status()

                    # Read video content
                    video_content = b''
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            video_content += chunk

                    # Generate filename
                    filename = f"videos/{request.user.id}/{task_id}.mp4"

                    # Save to local storage
                    file_path = default_storage.save(filename, ContentFile(video_content))
                    local_video_url = default_storage.url(file_path)

                    logger.info(f"✅ Video saved to local storage: {file_path}")
                except Exception as download_error:
                    logger.warning(f"⚠️ Failed to download video, using CDN URL: {str(download_error)}")
                    # Fall back to CDN URL if download fails
                    local_video_url = result.video_url

                # Check if VideoHistory already exists for this task
                # Session 122: If it exists, preserve its session/project (set by _execute_generate_video)
                existing_video = None
                try:
                    existing_video = VideoHistory.objects.get(user=request.user, video_id=task_id)
                except VideoHistory.DoesNotExist:
                    pass

                video_history, created = VideoHistory.objects.get_or_create(
                    user=request.user,
                    video_id=task_id,
                    defaults={
                        'video_url': local_video_url,  # Session 96: Use local URL
                        'thumbnail_url': result.thumbnail_url or '',
                        'video_type': video_type,
                        'prompt': content.prompt,
                        'parameters': metadata,
                        'model_used': model_used,
                        'duration': video_duration,
                        'ratio': metadata.get('ratio', ''),
                        'status': 'completed',
                        'source_image': source_image,
                        # Session 122: Inherit session/project from source image (for image-to-video) or existing_video
                        'session': existing_video.session if existing_video else (source_image.session if source_image else None),
                        'project': existing_video.project if existing_video else (source_image.project if source_image else None),
                        'generation_completed': timezone.now()
                    }
                )

                # Update if already exists
                if not created:
                    video_history.video_url = local_video_url  # Session 96: Use local URL
                    video_history.thumbnail_url = result.thumbnail_url or ''
                    video_history.status = 'completed'
                    video_history.duration = video_duration  # Session 70: Update duration too
                    video_history.generation_completed = timezone.now()
                    video_history.save()

                logger.info(f"✅ Video saved to gallery: {video_history.id}")

                # Session 122: Track generated video for intelligent chaining
                # Apr 2026: Fixed — was calling undefined method on cached PA object.
                # Now writes directly to cache instead.
                try:
                    from django.core.cache import cache
                    from django.utils import timezone
                    if video_history:
                        source_image_id = str(source_image.id) if source_image else None

                        cache_key = f'recent_assets:{request.user.id}'
                        assets = cache.get(cache_key, {'images': [], 'videos': []})
                        assets['videos'].append({
                            'id': str(video_history.id),
                            'url': local_video_url,
                            'prompt': content.prompt,
                            'source_image_id': source_image_id,
                            'timestamp': timezone.now().isoformat(),
                        })
                        assets['videos'] = assets['videos'][-10:]  # Keep last 10
                        cache.set(cache_key, assets, 3600)  # 1 hour TTL
                        logger.info(f"Tracked video {video_history.id} (source_image: {source_image_id})")
                except Exception as e:
                    logger.warning(f"Failed to track video in cache: {e}")
            elif result.status == 'failed':
                content.status = 'failed'
                metadata = content.metadata or {}
                metadata['error'] = result.error_message
                content.metadata = metadata
                content.save()
            elif result.status == 'processing':
                content.status = 'processing'
                metadata = content.metadata or {}
                metadata['progress'] = result.progress
                content.metadata = metadata
                content.save()
                
        except ContentGeneration.DoesNotExist:
            # Session 68: AI Assistant creates VideoHistory directly (not ContentGeneration)
            # So we need to check for VideoHistory records and update them too!
            try:
                video_history = VideoHistory.objects.get(
                    user=request.user,
                    video_id=task_id
                )

                # Update VideoHistory status directly
                if result.status == 'completed':
                    # Session 119: Download video to local storage (prevent expired CDN URLs)
                    local_video_url = result.video_url
                    try:
                        import requests
                        from django.core.files.base import ContentFile
                        from django.core.files.storage import default_storage

                        # Download video from CDN
                        logger.info(f"📥 Downloading AI Assistant video from CDN: {result.video_url[:80]}...")
                        response = requests.get(result.video_url, timeout=120, stream=True)
                        response.raise_for_status()

                        # Read video content
                        video_content = b''
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                video_content += chunk

                        # Generate filename using video_history ID
                        filename = f"videos/{request.user.id}/assistant_{video_history.id}.mp4"

                        # Save to local storage
                        file_path = default_storage.save(filename, ContentFile(video_content))
                        local_video_url = default_storage.url(file_path)

                        logger.info(f"✅ AI Assistant video saved to local storage: {file_path}")
                    except Exception as download_error:
                        logger.warning(f"⚠️ Failed to download AI Assistant video, using CDN URL: {str(download_error)}")
                        # Fall back to CDN URL if download fails
                        local_video_url = result.video_url

                    video_history.video_url = local_video_url  # Session 119: Use local URL
                    video_history.thumbnail_url = result.thumbnail_url or ''
                    video_history.status = 'completed'
                    video_history.generation_completed = timezone.now()
                    video_history.save()
                    logger.info(f"✅ AI Assistant video completed: {video_history.id} (task: {task_id})")

                    # Session 122: Track generated video in AI Assistant for intelligent chaining
                    try:
                        from django.core.cache import cache
                        cache_key = f'assistant_{request.user.id}'
                        assistant = cache.get(cache_key)
                        if assistant and video_history:
                            # Determine source image ID if this was image-to-video
                            source_image_id = None
                            if video_history.source_image:
                                source_image_id = str(video_history.source_image.id)

                            assistant.track_generated_video(
                                video_id=str(video_history.id),
                                video_url=local_video_url,
                                prompt=video_history.prompt,
                                source_image_id=source_image_id
                            )
                            logger.info(f"🎬 Tracked AI Assistant video {video_history.id} (source_image: {source_image_id})")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to track AI Assistant video: {e}")

                elif result.status == 'failed':
                    video_history.status = 'failed'
                    # Store error in parameters JSON
                    params = video_history.parameters or {}
                    params['error'] = result.error_message
                    video_history.parameters = params
                    video_history.save()
                    logger.error(f"❌ AI Assistant video failed: {video_history.id} - {result.error_message}")

                elif result.status == 'processing':
                    # Store progress in parameters JSON
                    params = video_history.parameters or {}
                    params['progress'] = result.progress
                    video_history.parameters = params
                    video_history.save()
                    logger.info(f"⏳ AI Assistant video processing: {video_history.id} - {result.progress}%")

            except VideoHistory.DoesNotExist:
                logger.warning(f"⚠️ No ContentGeneration or VideoHistory found for task: {task_id}")

        # Return status response
        response_data = {
            'status': result.status,
            'progress': result.progress,
            'progress_message': result.progress_message
        }

        if result.status == 'completed':
            response_data.update({
                'video_url': result.video_url,
                'thumbnail_url': result.thumbnail_url,
                'duration': result.duration
            })
        elif result.status == 'failed':
            response_data['error'] = result.error_message

        # Add estimated remaining time for processing
        if result.status in ['pending', 'processing']:
            response_data['estimated_remaining'] = max(0, result.estimated_time - result.progress)

        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return JsonResponse({
            'status': 'failed',
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_detail(request, video_id):
    """
    Get details of a specific video.
    """
    try:
        content = ContentGeneration.objects.get(
            id=video_id,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'video': {
                'id': content.id,
                'title': content.metadata.get('title', f"Video #{content.id}") if content.metadata else f"Video #{content.id}",
                'description': content.prompt or 'Generated video',
                'video_url': content.metadata.get('video_url', content.generated_content) if content.metadata else content.generated_content,
                'thumbnail_url': content.metadata.get('thumbnail_url', '') if content.metadata else '',
                'status': content.status,
                'created_at': content.created_at.isoformat(),
                'metadata': content.metadata or {},
                'tags': content.metadata.get('tags', []) if content.metadata else [],
                'is_public': content.metadata.get('is_public', False) if content.metadata else False,
                'is_favorite': content.metadata.get('is_favorite', False) if content.metadata else False
            }
        })
        
    except ContentGeneration.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Get video detail error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def video_gallery(request):
    """
    Get user's video gallery.
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        category = request.GET.get('category')
        search = request.GET.get('search')
        
        # Build query - filter by video-related generations
        queryset = ContentGeneration.objects.filter(
            user=request.user,
            status='processed'  # Use the correct status from ContentStatus choices
        ).exclude(
            generated_content__isnull=True
        ).exclude(
            generated_content__exact=''
        ).order_by('-created_at')
        
        # Apply filters
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(original_prompt__icontains=search)
        
        # Get total count
        total_count = queryset.count()
        
        # Apply pagination
        videos = queryset[offset:offset + limit]
        
        # Format response
        video_list = []
        for video in videos:
            video_list.append({
                'id': video.id,
                'title': video.metadata.get('title', f"Video #{video.id}") if video.metadata else f"Video #{video.id}",
                'description': video.prompt or 'Generated video',
                'video_url': video.metadata.get('video_url', video.generated_content) if video.metadata else video.generated_content,
                'thumbnail_url': video.metadata.get('thumbnail_url', '') if video.metadata else '',
                'duration': video.metadata.get('duration', 0) if video.metadata else 0,
                'created_at': video.created_at.isoformat(),
                'tags': video.metadata.get('tags', []) if video.metadata else [],
                'category': video.metadata.get('category', 'uncategorized') if video.metadata else 'uncategorized',
                'is_favorite': video.metadata.get('is_favorite', False) if video.metadata else False,
                'is_public': hasattr(video, 'is_public') and video.is_public,
                'metadata': video.metadata or {}
            })
        
        return JsonResponse({
            'success': True,
            'videos': video_list,
            'total_count': total_count,
            'has_more': (offset + limit) < total_count
        })
        
    except Exception as e:
        logger.error(f"Video gallery error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_video_history(request):
    """
    Get user's video generation history from VideoHistory model.
    Supports filtering, sorting, and pagination.
    """
    try:
        # Get query parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        video_type = request.GET.get('type')  # text_to_video or image_to_video
        model = request.GET.get('model')
        status = request.GET.get('status', 'completed')  # Default to completed only
        is_favorite = request.GET.get('favorite')
        sort_by = request.GET.get('sort', '-created_at')  # Default newest first

        # Build query
        # Session 96: Exclude videos with expired external CDN URLs
        # Phase 2 P1: Use select_related to avoid N+1 queries on source_image
        from django.db.models import Q
        queryset = VideoHistory.objects.filter(user=request.user).exclude(
            Q(video_url__icontains='cloudfront.net') |
            Q(video_url__icontains='storage.googleapis.com') |
            Q(video_url__icontains='_jwt=')
        ).select_related('source_image', 'project', 'session')

        # Apply filters
        if video_type:
            queryset = queryset.filter(video_type=video_type)
        if model:
            queryset = queryset.filter(model_used=model)
        if status:
            queryset = queryset.filter(status=status)
        if is_favorite:
            queryset = queryset.filter(is_favorite=(is_favorite.lower() == 'true'))

        # Apply sorting
        queryset = queryset.order_by(sort_by)

        # Get total count
        total_count = queryset.count()

        # Apply pagination
        videos = queryset[offset:offset + limit]

        # Format response
        video_list = []
        for video in videos:
            # Try to get source image URL from source_image ForeignKey
            source_image_url = None
            if video.source_image:
                source_image_url = video.source_image.file_path
            else:
                # Fallback: check ContentGeneration metadata for source_image URL
                try:
                    content = ContentGeneration.objects.get(metadata__task_id=video.video_id)
                    if content.metadata:
                        source_image_url = content.metadata.get('source_image')
                except ContentGeneration.DoesNotExist:
                    pass

            video_list.append({
                'id': video.id,
                'sequential_number': video.get_sequential_number(),  # Session 119: Sequential ID for videos
                'video_id': video.video_id,
                'video_url': video.video_url,
                'thumbnail_url': video.thumbnail_url,
                'video_type': video.video_type,
                'prompt': video.prompt,
                'model_used': video.model_used,
                'duration': video.duration,
                'ratio': video.ratio,
                'status': video.status,
                'is_favorite': video.is_favorite,
                'view_count': video.view_count,
                'download_count': video.download_count,
                'created_at': video.created_at.isoformat(),
                'generation_time_seconds': video.generation_time_seconds,
                'source_image_id': video.source_image.id if video.source_image else None,
                'source_image_url': source_image_url,
                'tags': video.tags,
                'user_notes': video.user_notes,
            })

        return JsonResponse({
            'success': True,
            'videos': video_list,
            'total_count': total_count,
            'has_more': (offset + limit) < total_count,
            'offset': offset,
            'limit': limit
        })

    except Exception as e:
        logger.error(f"Get video history error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_video_favorite(request, video_id):
    """
    Toggle favorite status for a video.

    Accepts either integer ID or video_id (UUID)
    """
    try:
        # Try to find by video_id (UUID) first, then by id (integer)
        try:
            video = VideoHistory.objects.get(video_id=video_id, user=request.user)
        except VideoHistory.DoesNotExist:
            video = VideoHistory.objects.get(id=video_id, user=request.user)
        video.is_favorite = not video.is_favorite
        video.save()

        return JsonResponse({
            'success': True,
            'is_favorite': video.is_favorite
        })

    except VideoHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Toggle favorite error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def delete_video(request, video_id):
    """
    GET: Get video details
    DELETE: Delete a video from history

    Accepts either integer ID or video_id (UUID)
    """
    try:
        # Try to find by video_id (UUID) first, then by id (integer)
        try:
            video = VideoHistory.objects.get(video_id=video_id, user=request.user)
        except VideoHistory.DoesNotExist:
            video = VideoHistory.objects.get(id=video_id, user=request.user)

        if request.method == 'GET':
            # Return video details
            return JsonResponse({
                'success': True,
                'video': {
                    'id': video.id,
                    'video_id': video.video_id,
                    'video_url': video.video_url,
                    'thumbnail_url': video.thumbnail_url,
                    'video_type': video.video_type,
                    'prompt': video.prompt,
                    'model_used': video.model_used,
                    'duration': video.duration,
                    'ratio': video.ratio,
                    'status': video.status,
                    'is_favorite': video.is_favorite,
                    'view_count': video.view_count,
                    'download_count': video.download_count,
                    'created_at': video.created_at.isoformat(),
                }
            })

        elif request.method == 'DELETE':
            # Delete video
            video.delete()
            return JsonResponse({
                'success': True,
                'message': 'Video deleted successfully'
            })

    except VideoHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Video operation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_video_download(request, video_id):
    """
    Increment download count for a video

    Accepts either integer ID or video_id (UUID)
    """
    try:
        # Try to find by video_id (UUID) first, then by id (integer)
        try:
            video = VideoHistory.objects.get(video_id=video_id, user=request.user)
        except VideoHistory.DoesNotExist:
            video = VideoHistory.objects.get(id=video_id, user=request.user)
        video.download_count += 1
        video.save()

        return JsonResponse({
            'success': True,
            'download_count': video.download_count
        })

    except VideoHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Increment download error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increment_video_view(request, video_id):
    """
    Increment view count for a video

    Accepts either integer ID or video_id (UUID)
    """
    try:
        # Try to find by video_id (UUID) first, then by id (integer)
        try:
            video = VideoHistory.objects.get(video_id=video_id, user=request.user)
        except VideoHistory.DoesNotExist:
            video = VideoHistory.objects.get(id=video_id, user=request.user)
        video.view_count += 1
        video.save()

        return JsonResponse({
            'success': True,
            'view_count': video.view_count
        })

    except VideoHistory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Increment view error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_video_to_gallery(request):
    """
    Save a generated video to the user's gallery.
    """
    try:
        data = request.data
        
        # Validate required fields
        video_url = data.get('video_url')
        if not video_url:
            return JsonResponse({
                'success': False,
                'error': 'Video URL is required'
            }, status=400)
        
        # Create or update video in gallery
        content = ContentGeneration.objects.create(
            user=request.user,
            prompt=data.get('original_prompt', ''),
            generated_content=video_url,  # Store video URL as generated content
            status='processed',
            metadata={
                'video_url': video_url,
                'thumbnail_url': data.get('thumbnail_url', ''),
                'category': data.get('category', 'uncategorized'),
                'tags': data.get('tags', []),
                'type': 'video',
                'is_public': data.get('is_public', False),
                **data.get('metadata', {})
            }
        )
        
        return JsonResponse({
            'success': True,
            'video_id': content.id,
            'message': 'Video saved to gallery successfully'
        })
        
    except Exception as e:
        logger.error(f"Save video error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_runway_connection(request):
    """
    Test endpoint to verify RunwayML connection without authentication.
    GET: Check if API key is configured
    POST: Test a simple text-to-video generation
    """
    if request.method == 'GET':
        # Check if API key is configured
        from django.conf import settings
        has_key = bool(getattr(settings, 'RUNWAY_API_KEY', ''))
        
        return JsonResponse({
            'success': True,
            'runway_configured': has_key,
            'api_base': runway_provider.api_base if has_key else None,
            'message': 'RunwayML is configured and ready' if has_key else 'RunwayML API key not configured'
        })
    
    elif request.method == 'POST':
        # Test text-to-video generation
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")
            prompt = data.get('prompt', 'A beautiful sunset over the ocean, cinematic')
            
            # Test with minimal parameters
            result = runway_provider.text_to_video(
                prompt=prompt,
                duration=5,
                quality='gen3a_turbo',
                enhance_prompt=False
            )
            
            return JsonResponse({
                'success': result.success,
                'task_id': result.task_id if result.success else None,
                'status': result.status,
                'error': result.error_message if not result.success else None,
                'estimated_time': result.estimated_time,
                'message': 'Video generation started successfully' if result.success else 'Failed to start generation'
            })
            
        except Exception as e:
            logger.error(f"Test RunwayML error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ====================================================================
# NEW VIDEO ENDPOINTS (Session 49)
# ====================================================================

@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def video_to_video_endpoint(request):
    """
    POST /api/v1/video/video-to-video/
    Transform existing video with AI

    Form Data:
        - video: video file
        - mode: 'extend' or 'interpolate'
        - prompt: optional transformation description
        - duration: 4, 6, or 8 seconds
    """
    try:
        # Get gallery video URL or uploaded video
        gallery_video_url = request.POST.get('video_url', '').strip()
        video_file = request.FILES.get('video')
        mode = request.POST.get('mode', 'extend')
        prompt = request.POST.get('prompt', '')
        duration = int(request.POST.get('duration', 6))

        # Check if video source is provided (gallery URL or file upload)
        if not gallery_video_url and not video_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Video file or gallery video is required'
            }, status=400)

        logger.info(f"🎬 Video-to-Video request: mode={mode}, duration={duration}s")

        # Use gallery video URL or save uploaded video temporarily
        if gallery_video_url:
            logger.info(f"📹 Using video from gallery: {gallery_video_url}")
            video_url = gallery_video_url
            file_path = None
        else:
            logger.info(f"📤 Uploading new video file")
            file_name = f"temp_v2v_{video_file.name}"
            file_path = default_storage.save(file_name, ContentFile(video_file.read()))
            video_url = request.build_absolute_uri(default_storage.url(file_path))

        # Call Runway ML provider
        result = runway_provider.video_to_video(
            video_url=video_url,
            prompt=prompt or f"Video transformation with {mode} mode",
            duration=duration,
            quality="gen4_aleph",
            ratio="1280:720"
        )

        # Clean up temp file (if we created one)
        if file_path:
            try:
                default_storage.delete(file_path)
            except Exception:
                pass

        # Save to history if successful
        if result.success and result.task_id:
            from core.services.workspace_resolver import get_active_workspace
            _user = request.user if request.user.is_authenticated else None
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=_user,
                video_type='video_to_video',
                prompt=prompt or f"{mode} mode transformation",
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_aleph'),
                ratio="1280:720",
                status='pending',
                workspace=get_active_workspace(_user) if _user else None,
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

        return JsonResponse({
            'success': result.success,
            'task_id': result.task_id if result.success else None,
            'status': result.status,
            'error_message': result.error_message if not result.success else None,
            'message': 'Video-to-video generation started successfully' if result.success else 'Failed to start generation'
        })

    except Exception as e:
        logger.error(f"❌ Video-to-video error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def video_upscale_endpoint(request):
    """
    POST /api/v1/video/upscale/
    Upscale video to 4K resolution

    Form Data:
        - video: video file
        - prompt: video description
        - quality: 'standard' or 'high'
    """
    try:
        # Get gallery video URL or uploaded video
        gallery_video_url = request.POST.get('video_url', '').strip()
        video_file = request.FILES.get('video')
        prompt = request.POST.get('prompt', '')
        quality = request.POST.get('quality', 'high')

        # Check if video source is provided (gallery URL or file upload)
        if not gallery_video_url and not video_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Video file or gallery video is required'
            }, status=400)

        if not prompt:
            return JsonResponse({
                'success': False,
                'error_message': 'Prompt description is required for upscaling'
            }, status=400)

        logger.info(f"⬆️ Video Upscale request: quality={quality}")

        # Use gallery video URL or save uploaded video temporarily
        if gallery_video_url:
            logger.info(f"📹 Using video from gallery: {gallery_video_url}")
            video_url = gallery_video_url
            file_path = None
        else:
            logger.info(f"📤 Uploading new video file")
            file_name = f"temp_upscale_{video_file.name}"
            file_path = default_storage.save(file_name, ContentFile(video_file.read()))
            video_url = request.build_absolute_uri(default_storage.url(file_path))

        # Call Runway ML provider
        result = runway_provider.video_upscale(
            video_url=video_url
        )

        # Clean up temp file (if we created one)
        if file_path:
            try:
                default_storage.delete(file_path)
            except Exception:
                pass

        # Save to history if successful
        if result.success and result.task_id:
            from core.services.workspace_resolver import get_active_workspace
            _user = request.user if request.user.is_authenticated else None
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=_user,
                video_type='upscale_video',
                prompt=prompt,
                model_used=getattr(result, 'model_used', 'upscale_v1'),
                ratio="3840:2160",  # 4K
                status='pending',
                workspace=get_active_workspace(_user) if _user else None,
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='editing',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

        return JsonResponse({
            'success': result.success,
            'task_id': result.task_id if result.success else None,
            'status': result.status,
            'error_message': result.error_message if not result.success else None,
            'message': 'Video upscaling started successfully' if result.success else 'Failed to start upscaling'
        })

    except Exception as e:
        logger.error(f"❌ Video upscale error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def extend_video_endpoint(request):
    """
    POST /api/v1/video/extend/
    Extend video duration by generating continuation

    Session 66 Part 2: Runway Extend feature!
    Can extend up to 3 times: 8 → 18 → 28 → 38 seconds!

    Form Data:
        - video_url: URL of video from gallery (required)
        - extension_seconds: 4, 6, 8, or 10 (default: 10 for max extension)
        - prompt: Optional guidance for extension (default: continue motion)
    """
    try:
        # Handle JSON request body (Flutter sends JSON, not form data)
        import json
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        # Get video URL (must be from gallery)
        video_url = data.get('video_url', '').strip()
        extension_seconds = int(data.get('extension_seconds', 10))
        prompt = data.get('prompt', '').strip()

        # Validate video URL provided
        if not video_url:
            return JsonResponse({
                'success': False,
                'error_message': 'Video URL from gallery is required'
            }, status=400)

        # Validate extension duration
        if extension_seconds not in [4, 6, 8, 10]:
            return JsonResponse({
                'success': False,
                'error_message': 'Extension must be 4, 6, 8, or 10 seconds'
            }, status=400)

        logger.info(f"🎬 Extend Video request: {extension_seconds}s extension")
        logger.info(f"📹 Source video: {video_url}")

        # Call Runway ML extend feature
        result = runway_provider.extend_video(
            video_url=video_url,
            extension_seconds=extension_seconds,
            prompt=prompt if prompt else None,  # Use default if not provided
            quality="gen4_aleph"  # Best quality for video-to-video
        )

        # Save to history if successful
        if result.success and result.task_id:
            from core.services.workspace_resolver import get_active_workspace
            _user = request.user if request.user.is_authenticated else None
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=_user,
                video_type='extend_video',
                prompt=prompt or f"Extended by {extension_seconds}s",
                duration=extension_seconds,
                model_used='gen4_aleph',
                ratio="1280:720",
                status='pending',
                parent_video_url=video_url,  # Track which video was extended
                workspace=get_active_workspace(_user) if _user else None,
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

        return JsonResponse({
            'success': result.success,
            'task_id': result.task_id if result.success else None,
            'status': result.status,
            'extension_seconds': extension_seconds,
            'error_message': result.error_message if not result.success else None,
            'message': f'Video extension started! Adding {extension_seconds}s' if result.success else 'Failed to start extension'
        })

    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error_message': f'Invalid input: {str(e)}'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Video extend error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def character_performance_endpoint(request):
    """
    POST /api/v1/video/character-performance/
    Animate character portrait with reference video

    Form Data:
        - image: portrait image file
        - reference_video: optional reference performance video
        - prompt: performance description
        - stabilization: 'none', 'standard', or 'high'
        - duration: 4, 6, or 8 seconds
    """
    try:
        # Get gallery URLs or uploaded files
        gallery_image_url = request.POST.get('image_url', '').strip()
        gallery_video_url = request.POST.get('video_url', '').strip()
        image_file = request.FILES.get('image')
        reference_video = request.FILES.get('reference_video')
        prompt = request.POST.get('prompt', '')
        stabilization = request.POST.get('stabilization', 'standard')
        duration = int(request.POST.get('duration', 6))

        # Check if image source is provided (gallery URL or file upload)
        if not gallery_image_url and not image_file:
            return JsonResponse({
                'success': False,
                'error_message': 'Portrait image or gallery image is required'
            }, status=400)

        if not prompt:
            return JsonResponse({
                'success': False,
                'error_message': 'Performance description is required'
            }, status=400)

        logger.info(f"🎭 Character Performance request: stabilization={stabilization}, duration={duration}s")

        # Use gallery image URL or save uploaded image temporarily
        if gallery_image_url:
            logger.info(f"🖼️ Using image from gallery: {gallery_image_url}")
            image_url = gallery_image_url
            image_path = None
        else:
            logger.info(f"📤 Uploading new image file")
            image_name = f"temp_cp_image_{image_file.name}"
            image_path = default_storage.save(image_name, ContentFile(image_file.read()))
            image_url = request.build_absolute_uri(default_storage.url(image_path))

        # Use gallery reference video URL or save uploaded reference video if provided
        reference_video_url = None
        reference_video_path = None
        if gallery_video_url:
            logger.info(f"📹 Using reference video from gallery: {gallery_video_url}")
            reference_video_url = gallery_video_url
            reference_video_path = None
        elif reference_video:
            # Save uploaded reference video (will be converted to base64 by video_provider)
            logger.info(f"📤 Uploading reference video: {reference_video.name}")
            ref_file_name = f"reference_{reference_video.name}"
            reference_video_path = default_storage.save(ref_file_name, ContentFile(reference_video.read()))
            reference_video_url = request.build_absolute_uri(default_storage.url(reference_video_path))
            logger.info(f"✅ Reference video saved: {reference_video_url} (will be converted to base64 for RunwayML)")

        # If no reference video provided, return error
        if not reference_video_url:
            # Character performance requires a reference video
            # Clean up temp files
            if image_path:
                try:
                    default_storage.delete(image_path)
                except Exception:
                    pass

            return JsonResponse({
                'success': False,
                'error_message': 'Reference video is required for character performance. Please upload or select a 3-30 second video of a person performing.'
            }, status=400)

        # Call Runway ML provider
        result = runway_provider.character_performance(
            image_url=image_url,
            reference_video_url=reference_video_url,
            prompt=prompt,
            body_control=True,
            expression_intensity=3,
            ratio="1280:720"
        )

        # Clean up temp files (if we created any)
        try:
            if image_path:
                default_storage.delete(image_path)
            if reference_video_path:
                default_storage.delete(reference_video_path)
        except Exception:
            pass

        # Save to history if successful
        if result.success and result.task_id:
            from core.services.workspace_resolver import get_active_workspace
            _user = request.user if request.user.is_authenticated else None
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=_user,
                video_type='character_performance',
                prompt=prompt,
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_character'),
                ratio="1280:720",
                status='pending',
                workspace=get_active_workspace(_user) if _user else None,
            )

            # Session 142: Track agent contribution
            try:
                from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
                agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')
                AgentContribution.objects.create(
                    agent=agent,
                    video=video_history,
                    project=None,
                    contribution_type='generation',
                    task_description="Generated video using VideoAgent",
                    execution_time_seconds=0.0
                )
                logger.info(f"✅ Agent contribution tracked for video {{ video_history.id }}")
            except Exception as e:
                logger.error(f"❌ Failed to create agent contribution: {e}")
                # Don't fail content creation if contribution tracking fails

        return JsonResponse({
            'success': result.success,
            'task_id': result.task_id if result.success else None,
            'status': result.status,
            'error_message': result.error_message if not result.success else None,
            'message': 'Character performance started successfully' if result.success else 'Failed to start generation'
        })

    except Exception as e:
        logger.error(f"❌ Character performance error: {e}")
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)


# ============================================================================
# Session 154: Video Enhancement Operations
# ============================================================================


@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def upscale_video(request):
    """
    Upscale a video using ffmpeg lanczos scaling

    Session 154: Video Enhancement
    Note: @login_required removed to support internal RequestFactory calls from agents

    POST /api/video/upscale/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "scale_factor": 2 or 4,  # 2x or 4x upscaling
        "quality": "high" (optional)
    }
    """
    # Manual authentication check for web requests
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        scale_factor = data.get('scale_factor', 2)  # Default 2x
        quality = data.get('quality', 'high')
        project_id = data.get('project_id')  # Session 156: Accept project_id for linking

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Session 154 Bug Fix: Strip quotes if video_id is double-encoded (e.g., '"12"' instead of '12')
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
            logger.info(f"🔍 [Session 154] Cleaned video_id: {video_id}")

        if scale_factor not in [2, 4]:
            return JsonResponse({'success': False, 'error': 'scale_factor must be 2 or 4'}, status=400)

        # Resolve hybrid ID (support both UUID and numeric IDs like "1", "2", "3")
        try:
            import uuid
            video_uuid = uuid.UUID(video_id)
            logger.info(f"✅ [Session 154] Parsed as UUID: {video_uuid}")
        except (ValueError, AttributeError):
            # Numeric ID - resolve to UUID
            try:
                numeric_id = int(video_id)
                videos = VideoHistory.objects.filter(user=request.user).order_by('-created_at')
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"✅ [Session 154] Resolved numeric ID {numeric_id} → UUID {video_uuid}")
            except (ValueError, IndexError) as e:
                logger.error(f"❌ [Session 154] Invalid video_id '{video_id}': {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid video_id: {video_id}'
                }, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Video is {video.status}, must be completed to upscale'
            }, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🎬 [Session 154] Upscaling video {video.id} by {scale_factor}x")

        # Get input video path
        input_path = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            # Local file
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Video file not found: {full_path}'
                }, status=404)
        else:
            # Remote URL - download first
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()

                # Save to temp file
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"📥 Downloaded video from CDN to {input_path}")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download video: {str(e)}'
                }, status=500)

        # Generate output filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/{request.user.id}/upscaled_{scale_factor}x_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Upscale using ffmpeg with lanczos algorithm (high quality)
        # -vf scale=iw*2:ih*2:flags=lanczos (2x) or scale=iw*4:ih*4:flags=lanczos (4x)
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'scale=iw*{scale_factor}:ih*{scale_factor}:flags=lanczos',
            '-c:v', 'libx264',
            '-preset', 'slow' if quality == 'high' else 'medium',
            '-crf', '18' if quality == 'high' else '23',
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y',  # Overwrite output file
            output_path
        ]

        logger.info(f"🚀 Running ffmpeg upscale: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg upscale failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg upscale failed: {result.stderr[:200]}'
            }, status=500)

        # Get file size and duration
        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Upscaled video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Session 156: Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 156] Linking upscaled video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 156] Project {project_id} not found")

        # Create new VideoHistory record for upscaled video
        from core.services.workspace_resolver import get_active_workspace
        upscaled_video = VideoHistory.objects.create(
            user=request.user,
            video_type='upscaled',
            prompt=f"Upscaled {scale_factor}x from video {video.id}",
            duration=video.duration,
            model_used=f'ffmpeg_lanczos_{scale_factor}x',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=timezone.now(),
            project=project,  # Session 156: Associate with project
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 154] Video upscaled: {video.id} → {upscaled_video.id} ({scale_factor}x)")

        # Session 155: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=upscaled_video,
                project=video.project if hasattr(video, 'project') and video.project else None,
                contribution_type='editing',
                task_description=f"Upscaled video {scale_factor}x using ffmpeg lanczos scaling",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 155] Agent contribution tracked for video {upscaled_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 155] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(upscaled_video.id),
            'video_url': upscaled_video.video_url,
            'scale_factor': scale_factor,
            'message': f'Video upscaled {scale_factor}x successfully'
        })

    except Exception as e:
        logger.error(f"❌ [Session 154] Upscale error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def apply_video_effect(request):
    """
    Apply color grading/effects to a video using ffmpeg

    Session 154: Video Enhancement
    Note: @login_required removed to support internal RequestFactory calls from agents

    POST /api/video/effects/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "effect": "cinematic|vibrant|vintage|noir|warm|cool",
        "intensity": 0.5-1.0 (optional)
    }
    """
    # Manual authentication check for web requests
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        effect = data.get('effect', 'cinematic')
        intensity = float(data.get('intensity', 0.7))

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Session 154 Bug Fix: Strip quotes if video_id is double-encoded (e.g., '"12"' instead of '12')
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
            logger.info(f"🔍 [Session 154] Cleaned video_id: {video_id}")

        # Validate effect
        valid_effects = ['cinematic', 'vibrant', 'vintage', 'noir', 'warm', 'cool']
        if effect not in valid_effects:
            return JsonResponse({
                'success': False,
                'error': f'Invalid effect. Choose from: {", ".join(valid_effects)}'
            }, status=400)

        # Validate intensity
        if intensity < 0.0 or intensity > 1.0:
            return JsonResponse({'success': False, 'error': 'intensity must be 0.0-1.0'}, status=400)

        # Resolve hybrid ID (support both UUID and numeric IDs like "1", "2", "3")
        try:
            import uuid
            video_uuid = uuid.UUID(video_id)
            logger.info(f"✅ [Session 154] Parsed as UUID: {video_uuid}")
        except (ValueError, AttributeError):
            # Numeric ID - resolve to UUID
            try:
                numeric_id = int(video_id)
                videos = VideoHistory.objects.filter(user=request.user).order_by('-created_at')
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"✅ [Session 154] Resolved numeric ID {numeric_id} → UUID {video_uuid}")
            except (ValueError, IndexError) as e:
                logger.error(f"❌ [Session 154] Invalid video_id '{video_id}': {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid video_id: {video_id}'
                }, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Video is {video.status}, must be completed to apply effects'
            }, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🎨 [Session 154] Applying {effect} effect to video {video.id} (intensity: {intensity})")

        # Get input video path (same logic as upscale_video)
        input_path = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Video file not found: {full_path}'
                }, status=404)
        else:
            # Remote URL - download first
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()

                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"📥 Downloaded video from CDN to {input_path}")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download video: {str(e)}'
                }, status=500)

        # Generate output filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/{request.user.id}/{effect}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Build ffmpeg filter chain based on effect
        # Each effect uses different combinations of eq, curves, and colorlevels filters
        filter_chain = _build_effect_filter(effect, intensity)

        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vf', filter_chain,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',
            output_path
        ]

        logger.info(f"🚀 Running ffmpeg effect: {effect}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg effect failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg effect failed: {result.stderr[:200]}'
            }, status=500)

        # Get file size
        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Effect applied: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Create new VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        effect_video = VideoHistory.objects.create(
            user=request.user,
            video_type='enhanced',
            prompt=f"{effect.capitalize()} effect applied to video {video.id}",
            duration=video.duration,
            model_used=f'ffmpeg_{effect}',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=timezone.now(),
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 154] Effect applied: {video.id} → {effect_video.id} ({effect})")

        # Session 155: Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=effect_video,
                project=video.project if hasattr(video, 'project') and video.project else None,
                contribution_type='editing',
                task_description=f"Applied {effect} color grading effect using ffmpeg",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 155] Agent contribution tracked for video {effect_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 155] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(effect_video.id),
            'video_url': effect_video.video_url,
            'effect': effect,
            'message': f'{effect.capitalize()} effect applied successfully'
        })

    except Exception as e:
        logger.error(f"❌ [Session 154] Effect error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _build_effect_filter(effect: str, intensity: float) -> str:
    """
    Build ffmpeg filter chain for video effects

    Args:
        effect: Effect name (cinematic, vibrant, vintage, noir, warm, cool)
        intensity: Effect intensity (0.0-1.0)

    Returns:
        str: ffmpeg filter chain
    """
    # Base filters for each effect
    filters = {
        'cinematic': f"eq=contrast=1.1:saturation=0.9,curves=all='0/0 0.5/0.4 1/1'",
        'vibrant': f"eq=contrast=1.2:saturation={1.0 + intensity * 0.5}:brightness=0.05",
        'vintage': f"eq=contrast=0.9:saturation=0.7,curves=r='0/0.1 1/0.9':g='0/0.1 1/0.9':b='0/0.2 1/0.8'",
        'noir': f"eq=contrast={1.2 + intensity * 0.3}:saturation=0,curves=all='0/0 0.5/{0.45 + intensity * 0.1} 1/1'",
        'warm': f"eq=saturation=1.1,colortemperature={6500 + intensity * 1500}",
        'cool': f"eq=saturation=1.1,colortemperature={6500 - intensity * 2000}"
    }

    return filters.get(effect, filters['cinematic'])


def extract_video_frame(request):
    """
    Extract a single frame from a video at a specific timestamp.

    Session 159: Frame Extraction Feature
    Creates a thumbnail/still image from any point in a video.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/extract-frame/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "timestamp": 5.0,  # seconds into video
        "format": "jpg" or "png" (optional, default jpg)
    }

    Natural language examples:
    - "Extract frame at 5 seconds from video 1"
    - "Get thumbnail from video 3 at 10s"
    - "Pull a still from video 2 at the 3 second mark"
    """
    # Manual authentication check for web requests
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        timestamp = data.get('timestamp', 0.0)  # Default to start
        output_format = data.get('format', 'jpg').lower()
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Clean video_id if double-encoded
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
            logger.info(f"🔍 [Session 159] Cleaned video_id: {video_id}")

        # Validate format
        if output_format not in ['jpg', 'jpeg', 'png']:
            output_format = 'jpg'

        # Validate timestamp
        try:
            timestamp = float(timestamp)
            if timestamp < 0:
                timestamp = 0.0
        except (ValueError, TypeError):
            timestamp = 0.0

        # Resolve hybrid ID (support both UUID and numeric IDs like "1", "2", "3")
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
            logger.info(f"✅ [Session 159] Parsed as UUID: {video_uuid}")
        except (ValueError, AttributeError):
            # Numeric ID - resolve to UUID
            try:
                numeric_id = int(video_id)
                videos = VideoHistory.objects.filter(user=request.user).order_by('-created_at')
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"✅ [Session 159] Resolved numeric ID {numeric_id} → UUID {video_uuid}")
            except (ValueError, IndexError) as e:
                logger.error(f"❌ [Session 159] Invalid video_id '{video_id}': {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid video_id: {video_id}'
                }, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Video is {video.status}, must be completed to extract frame'
            }, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        # Validate timestamp against video duration
        if video.duration and timestamp > video.duration:
            logger.warning(f"⚠️ [Session 159] Timestamp {timestamp}s exceeds video duration {video.duration}s, clamping")
            timestamp = max(0, video.duration - 0.1)  # Clamp to near end

        logger.info(f"🎬 [Session 159] Extracting frame from video {video.id} at {timestamp}s")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            # Local file
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Video file not found: {full_path}'
                }, status=404)
        else:
            # Remote URL - download first
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()

                # Save to temp file
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"📥 Downloaded video from CDN to {input_path}")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download video: {str(e)}'
                }, status=500)

        # Generate output filename
        from django.utils import timezone as tz
        time_str = tz.now().strftime('%Y%m%d_%H%M%S')
        extension = 'jpg' if output_format in ['jpg', 'jpeg'] else 'png'
        output_filename = f"images/{request.user.id}/frame_{time_str}_{timestamp}s.{extension}"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Extract frame using ffmpeg
        # -ss BEFORE -i for fast seeking, -frames:v 1 for single frame
        cmd = [
            'ffmpeg',
            '-ss', str(timestamp),
            '-i', input_path,
            '-frames:v', '1',
            '-q:v', '2',  # High quality JPEG (1-31, lower is better)
            '-y',  # Overwrite output file
            output_path
        ]

        logger.info(f"🚀 Running ffmpeg frame extraction: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg frame extraction failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg frame extraction failed: {result.stderr[:200]}'
            }, status=500)

        # Clean up temp file if used
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        # Verify output file exists
        if not os.path.exists(output_path):
            return JsonResponse({
                'success': False,
                'error': 'Frame extraction produced no output'
            }, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Frame extracted: {output_path} ({file_size / 1024:.1f} KB)")

        # Get project - Session 179: Inherit from source video if not explicitly provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking extracted frame to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")
        elif video.project:
            # Session 179: Inherit from source video
            project = video.project
            logger.info(f"🔗 [Session 179] Inheriting project from source video: {project.name}")

        # Create ImageHistory record for the extracted frame
        # Use the correct field names for ImageHistory model
        from core.services.workspace_resolver import get_active_workspace
        extracted_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Frame extracted at {timestamp}s from video {video.id}",
            image_type='generated',  # Use existing type; 'extracted_frame' isn't in choices
            filename=os.path.basename(output_filename),
            file_path=f'/media/{output_filename}',
            parameters={'source_video_id': str(video.id), 'timestamp': timestamp, 'operation': 'frame_extraction'},
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 159] Frame extracted: video {video.id} @ {timestamp}s → image {extracted_image.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                image=extracted_image,
                project=project,
                contribution_type='extraction',
                task_description=f"Extracted frame at {timestamp}s from video using ffmpeg",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 159] Agent contribution tracked for image {extracted_image.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 159] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'image_id': str(extracted_image.id),
            'image_url': extracted_image.file_path,  # file_path contains the URL
            'timestamp': timestamp,
            'format': extension,
            'message': f'Frame extracted at {timestamp}s successfully',
            'agent': 'VideoEditingAgent',
            'operation': 'extract_frame',
            'operation_display': f'Extracting frame at {timestamp}s'
        })

    except Exception as e:
        logger.error(f"❌ [Session 159] Frame extraction error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def reverse_video(request):
    """
    Reverse a video (play backwards) using ffmpeg.

    Session 159: Video Reverse Feature
    Creates a reversed version of a video with optional audio reversal.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/reverse/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "reverse_audio": true (default) or false
    }

    Natural language examples:
    - "Reverse video 1"
    - "Play video 3 backwards"
    - "Reverse video 2 without audio"
    """
    # Manual authentication check for web requests
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        reverse_audio = data.get('reverse_audio', True)
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Clean video_id if double-encoded
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
            logger.info(f"🔍 [Session 159] Cleaned video_id: {video_id}")

        # Resolve hybrid ID (support both UUID and numeric IDs like "1", "2", "3")
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
            logger.info(f"✅ [Session 159] Parsed as UUID: {video_uuid}")
        except (ValueError, AttributeError):
            # Numeric ID - resolve to UUID
            try:
                numeric_id = int(video_id)
                videos = VideoHistory.objects.filter(user=request.user).order_by('-created_at')
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"✅ [Session 159] Resolved numeric ID {numeric_id} → UUID {video_uuid}")
            except (ValueError, IndexError) as e:
                logger.error(f"❌ [Session 159] Invalid video_id '{video_id}': {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid video_id: {video_id}'
                }, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Video is {video.status}, must be completed to reverse'
            }, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🎬 [Session 159] Reversing video {video.id} (audio: {reverse_audio})")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            # Local file
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Video file not found: {full_path}'
                }, status=404)
        else:
            # Remote URL - download first
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()

                # Save to temp file
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"📥 Downloaded video from CDN to {input_path}")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download video: {str(e)}'
                }, status=500)

        # Generate output filename
        from django.utils import timezone as tz
        time_str = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/{request.user.id}/reversed_{time_str}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Reverse video using ffmpeg
        # -vf reverse: reverse video frames
        # -af areverse: reverse audio (optional)

        if reverse_audio:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', 'reverse',
                '-af', 'areverse',
                '-y',  # Overwrite output file
                output_path
            ]
        else:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-vf', 'reverse',
                '-an',  # Remove audio
                '-y',  # Overwrite output file
                output_path
            ]

        logger.info(f"🚀 Running ffmpeg reverse: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg reverse failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg reverse failed: {result.stderr[:200]}'
            }, status=500)

        # Clean up temp file if used
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        # Verify output file exists
        if not os.path.exists(output_path):
            return JsonResponse({
                'success': False,
                'error': 'Video reverse produced no output'
            }, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Reversed video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project - Session 179: Inherit from source video if not explicitly provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking reversed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")
        elif video.project:
            # Session 179: Inherit from source video
            project = video.project
            logger.info(f"🔗 [Session 179] Inheriting project from source video: {project.name}")

        # Create VideoHistory record for the reversed video
        from core.services.workspace_resolver import get_active_workspace
        reversed_video = VideoHistory.objects.create(
            user=request.user,
            video_type='reversed',
            prompt=f"Reversed version of video {video.id}" + (" (with audio)" if reverse_audio else " (silent)"),
            duration=video.duration,
            model_used='ffmpeg_reverse',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 159] Video reversed: {video.id} → {reversed_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=reversed_video,
                project=project,
                contribution_type='editing',
                task_description=f"Reversed video using ffmpeg" + (" with audio" if reverse_audio else " (silent)"),
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 159] Agent contribution tracked for video {reversed_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 159] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(reversed_video.id),
            'video_url': reversed_video.video_url,
            'reverse_audio': reverse_audio,
            'message': f'Video reversed successfully' + (' (with audio)' if reverse_audio else ' (silent)'),
            'agent': 'VideoEditingAgent',
            'operation': 'reverse',
            'operation_display': f'Reversing video' + (' with audio' if reverse_audio else ' (silent)')
        })

    except Exception as e:
        logger.error(f"❌ [Session 159] Video reverse error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def trim_video(request):
    """
    Trim a video to a specific time range using ffmpeg.

    Session 159: Video Trimming Feature
    Cuts a video to keep only the specified segment.
    Uses ffmpeg with -c copy for fast, lossless trimming!

    POST /api/video/trim/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "start_time": 10.0,  # seconds or "00:00:10"
        "end_time": 20.0,    # seconds or "00:00:20"
        "keep_audio": true (default)
    }

    Natural language examples:
    - "Trim video 1 from 10 to 20 seconds"
    - "Keep only the first 15 seconds of video 2"
    - "Cut video 3 from 0:30 to 1:45"
    """
    # Manual authentication check for web requests
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        start_time = data.get('start_time', 0)
        end_time = data.get('end_time')
        keep_audio = data.get('keep_audio', True)
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        if end_time is None:
            return JsonResponse({'success': False, 'error': 'end_time required'}, status=400)

        # Clean video_id if double-encoded
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
            logger.info(f"🔍 [Session 159] Cleaned video_id: {video_id}")

        # Parse time values (support both seconds and HH:MM:SS format)
        def parse_time(t):
            if isinstance(t, (int, float)):
                return float(t)
            if isinstance(t, str):
                t = t.strip()
                if ':' in t:
                    # Parse HH:MM:SS or MM:SS
                    parts = t.split(':')
                    if len(parts) == 3:
                        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                    elif len(parts) == 2:
                        return int(parts[0]) * 60 + float(parts[1])
                return float(t)
            return 0.0

        start_seconds = parse_time(start_time)
        end_seconds = parse_time(end_time)

        if start_seconds < 0:
            start_seconds = 0
        if end_seconds <= start_seconds:
            return JsonResponse({
                'success': False,
                'error': f'end_time ({end_seconds}s) must be greater than start_time ({start_seconds}s)'
            }, status=400)

        # Resolve hybrid ID
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
            logger.info(f"✅ [Session 159] Parsed as UUID: {video_uuid}")
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                videos = VideoHistory.objects.filter(user=request.user).order_by('-created_at')
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"✅ [Session 159] Resolved numeric ID {numeric_id} → UUID {video_uuid}")
            except (ValueError, IndexError) as e:
                logger.error(f"❌ [Session 159] Invalid video_id '{video_id}': {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid video_id: {video_id}'
                }, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Video is {video.status}, must be completed to trim'
            }, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        # Validate against video duration
        if video.duration and end_seconds > video.duration:
            logger.warning(f"⚠️ [Session 159] end_time {end_seconds}s exceeds duration {video.duration}s, clamping")
            end_seconds = video.duration

        duration_trimmed = end_seconds - start_seconds
        logger.info(f"✂️ [Session 159] Trimming video {video.id}: {start_seconds}s → {end_seconds}s ({duration_trimmed}s)")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Video file not found: {full_path}'
                }, status=404)
        else:
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logger.info(f"📥 Downloaded video from CDN to {input_path}")
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Failed to download video: {str(e)}'
                }, status=500)

        # Generate output filename
        from django.utils import timezone as tz
        time_str = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/{request.user.id}/trimmed_{start_seconds}-{end_seconds}s_{time_str}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Trim video using ffmpeg
        # -ss before -i for fast seeking, -to for end time, -c copy for lossless

        cmd = [
            'ffmpeg',
            '-ss', str(start_seconds),
            '-i', input_path,
            '-to', str(duration_trimmed),  # Duration from seek point
            '-c', 'copy',  # Fast, lossless copy
        ]

        if not keep_audio:
            cmd.extend(['-an'])  # Remove audio

        cmd.extend(['-y', output_path])

        logger.info(f"🚀 Running ffmpeg trim: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg trim failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg trim failed: {result.stderr[:200]}'
            }, status=500)

        # Clean up temp file if used
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        # Verify output file exists
        if not os.path.exists(output_path):
            return JsonResponse({
                'success': False,
                'error': 'Video trim produced no output'
            }, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Trimmed video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project - Session 179: Inherit from source video if not explicitly provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking trimmed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")
        elif video.project:
            # Session 179: Inherit from source video
            project = video.project
            logger.info(f"🔗 [Session 179] Inheriting project from source video: {project.name}")

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        trimmed_video = VideoHistory.objects.create(
            user=request.user,
            video_type='trimmed',
            prompt=f"Trimmed {start_seconds}s-{end_seconds}s from video {video.id}",
            duration=duration_trimmed,
            model_used='ffmpeg_trim',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 159] Video trimmed: {video.id} → {trimmed_video.id} ({duration_trimmed}s)")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=trimmed_video,
                project=project,
                contribution_type='editing',
                task_description=f"Trimmed video from {start_seconds}s to {end_seconds}s using ffmpeg",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 159] Agent contribution tracked for video {trimmed_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 159] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(trimmed_video.id),
            'video_url': trimmed_video.video_url,
            'start_time': start_seconds,
            'end_time': end_seconds,
            'duration': duration_trimmed,
            'message': f'Video trimmed to {start_seconds}s-{end_seconds}s ({duration_trimmed}s)',
            'agent': 'VideoEditingAgent',
            'operation': 'trim',
            'operation_display': f'Trimming video to {start_seconds}s-{end_seconds}s'
        })

    except Exception as e:
        logger.error(f"❌ [Session 159] Video trim error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 160: Speed Control (DaVinci Expansion Phase 1)
# =============================================================================
# Speed up or slow down video playback using ffmpeg setpts/atempo filters
# Commands: "Make video 1 slow motion (0.5x)", "Speed up video 2 to 2x"
# Cost: FREE! Uses ffmpeg locally
# =============================================================================

@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def change_video_speed(request):
    """
    Session 160: Change video playback speed using ffmpeg.

    Supports:
    - Slow motion: 0.25x, 0.5x (2x slower, 4x slower)
    - Normal: 1.0x (no change)
    - Fast: 1.5x, 2x, 4x (faster playback)

    Uses ffmpeg setpts filter for video, atempo for audio.
    Note: atempo only supports 0.5-2.0 range, so we chain for extreme speeds.

    Cost: FREE! Uses ffmpeg locally.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Manual auth check (for internal agent calls)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        speed = data.get('speed', 1.0)  # Speed multiplier (0.25-4.0)
        preserve_audio = data.get('preserve_audio', True)
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({
                'success': False,
                'error': 'video_id is required'
            }, status=400)

        # Validate speed range
        try:
            speed = float(speed)
        except (TypeError, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'speed must be a number'
            }, status=400)

        if speed <= 0 or speed > 4.0:
            return JsonResponse({
                'success': False,
                'error': 'speed must be between 0.1 and 4.0'
            }, status=400)

        # Get video - support both UUID and hybrid numeric ID
        from content.models import VideoHistory
        video = None

        # First try as UUID
        try:
            import uuid
            uuid.UUID(str(video_id))
            video = VideoHistory.objects.get(id=video_id, user=request.user)
        except (ValueError, VideoHistory.DoesNotExist):
            # Try as numeric ID (hybrid support)
            try:
                numeric_id = int(video_id)
                user_videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                if 1 <= numeric_id <= user_videos.count():
                    video = user_videos[numeric_id - 1]
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({
                'success': False,
                'error': f'Video {video_id} not found'
            }, status=404)

        # Get source video path
        source_path = None
        if video.video_url:
            if video.video_url.startswith('/media/'):
                source_path = os.path.join(settings.MEDIA_ROOT, video.video_url.replace('/media/', ''))
            elif video.video_url.startswith('http'):
                # Download from URL
                import tempfile
                import requests
                temp_dir = tempfile.mkdtemp()
                temp_path = os.path.join(temp_dir, 'source.mp4')
                response = requests.get(video.video_url)
                with open(temp_path, 'wb') as f:
                    f.write(response.content)
                source_path = temp_path

        if not source_path or not os.path.exists(source_path):
            return JsonResponse({
                'success': False,
                'error': 'Source video file not found'
            }, status=404)

        # Create output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        speed_label = f"{speed}x".replace('.', '_')
        output_filename = f"videos/{video.id}/speed_{speed_label}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        logger.info(f"🎬 [Session 160] Changing video speed: {video.id} to {speed}x")

        # Check if video has audio stream using ffprobe
        has_audio = False
        try:
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', source_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in probe_result.stdout
            logger.info(f"🔊 [Session 160] Video has audio: {has_audio}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 160] Could not probe audio: {e}")

        # Build ffmpeg command
        # Video: setpts=PTS/speed (e.g., PTS/2 for 2x speed, PTS*2 for 0.5x)
        # Audio: atempo filter (only supports 0.5-2.0, chain for extreme values)

        video_filter = f"setpts=PTS/{speed}"

        if preserve_audio and has_audio and speed >= 0.5 and speed <= 2.0:
            # Normal atempo range
            audio_filter = f"atempo={speed}"
            cmd = [
                'ffmpeg', '-i', source_path,
                '-filter_complex', f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                '-map', '[v]', '-map', '[a]',
                '-y', output_path
            ]
        elif preserve_audio and has_audio and speed < 0.5:
            # Chain atempo for very slow speeds (e.g., 0.25 = atempo=0.5,atempo=0.5)
            atempo_chain = []
            remaining = speed
            while remaining < 0.5:
                atempo_chain.append("atempo=0.5")
                remaining *= 2
            if remaining != 1.0:
                atempo_chain.append(f"atempo={remaining}")
            audio_filter = ','.join(atempo_chain) if atempo_chain else f"atempo={speed}"
            cmd = [
                'ffmpeg', '-i', source_path,
                '-filter_complex', f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                '-map', '[v]', '-map', '[a]',
                '-y', output_path
            ]
        elif preserve_audio and has_audio and speed > 2.0:
            # Chain atempo for very fast speeds (e.g., 4.0 = atempo=2.0,atempo=2.0)
            atempo_chain = []
            remaining = speed
            while remaining > 2.0:
                atempo_chain.append("atempo=2.0")
                remaining /= 2
            if remaining != 1.0:
                atempo_chain.append(f"atempo={remaining}")
            audio_filter = ','.join(atempo_chain) if atempo_chain else f"atempo={speed}"
            cmd = [
                'ffmpeg', '-i', source_path,
                '-filter_complex', f"[0:v]{video_filter}[v];[0:a]{audio_filter}[a]",
                '-map', '[v]', '-map', '[a]',
                '-y', output_path
            ]
        else:
            # No audio preservation
            cmd = [
                'ffmpeg', '-i', source_path,
                '-vf', video_filter,
                '-an',  # Remove audio
                '-y', output_path
            ]

        logger.info(f"🔧 [Session 160] Running: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        if result.returncode != 0:
            logger.error(f"❌ [Session 160] ffmpeg speed change failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg speed change failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output file exists
        if not os.path.exists(output_path):
            return JsonResponse({
                'success': False,
                'error': 'Video speed change produced no output'
            }, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Speed-changed video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Calculate new duration
        original_duration = video.duration or 5  # Default to 5 if unknown
        new_duration = original_duration / speed

        # Get project - Session 179: Inherit from source video if not explicitly provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 160] Linking speed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 160] Project {project_id} not found")
        elif video.project:
            # Session 179: Inherit from source video
            project = video.project
            logger.info(f"🔗 [Session 179] Inheriting project from source video: {project.name}")

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        speed_video = VideoHistory.objects.create(
            user=request.user,
            video_type='speed_change',
            prompt=f"Speed {speed}x of video {video.id}",
            duration=new_duration,
            model_used='ffmpeg_speed',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        speed_description = "slow motion" if speed < 1.0 else "sped up" if speed > 1.0 else "normal speed"
        logger.info(f"✅ [Session 160] Video speed changed: {video.id} → {speed_video.id} ({speed}x {speed_description})")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=speed_video,
                project=project,
                contribution_type='editing',
                task_description=f"Changed video speed to {speed}x using ffmpeg",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 160] Agent contribution tracked for video {speed_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 160] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(speed_video.id),
            'video_url': speed_video.video_url,
            'speed': speed,
            'original_duration': original_duration,
            'new_duration': new_duration,
            'preserve_audio': preserve_audio,
            'message': f'Video speed changed to {speed}x ({speed_description})',
            'agent': 'VideoEditingAgent',
            'operation': 'speed_change',
            'operation_display': f'Changing video speed to {speed}x'
        })

    except Exception as e:
        logger.error(f"❌ [Session 160] Video speed change error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 160: Video Concatenation (DaVinci Expansion Phase 1)
# =============================================================================
# Combine multiple videos into a single video using ffmpeg concat demuxer
# Commands: "Combine videos 1, 2, 3", "Merge videos 5-8 together"
# Cost: FREE! Uses ffmpeg locally
# =============================================================================

@rate_limit('video_processing')  # Phase 2 P1: Rate limit video processing (5 requests/min)
def concatenate_videos(request):
    """
    Session 160: Concatenate multiple videos into one using ffmpeg.

    Uses the concat demuxer for lossless concatenation when codecs match,
    or re-encodes when necessary.

    Cost: FREE! Uses ffmpeg locally.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Manual auth check (for internal agent calls)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        video_ids = data.get('video_ids', [])  # List of video IDs
        project_id = data.get('project_id')
        transition = data.get('transition', 'none')  # Future: fade, dissolve, etc.

        if not video_ids or len(video_ids) < 2:
            return JsonResponse({
                'success': False,
                'error': 'At least 2 video_ids are required'
            }, status=400)

        # Get all videos
        from content.models import VideoHistory
        videos = []
        source_paths = []

        for vid in video_ids:
            video = None

            # First try as UUID
            try:
                import uuid
                uuid.UUID(str(vid))
                video = VideoHistory.objects.get(id=vid, user=request.user)
            except (ValueError, VideoHistory.DoesNotExist):
                # Try as numeric ID (hybrid support)
                try:
                    numeric_id = int(vid)
                    user_videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    if 1 <= numeric_id <= user_videos.count():
                        video = user_videos[numeric_id - 1]
                except (ValueError, TypeError):
                    pass

            if not video:
                return JsonResponse({
                    'success': False,
                    'error': f'Video {vid} not found'
                }, status=404)

            videos.append(video)

            # Get source path
            source_path = None
            if video.video_url:
                if video.video_url.startswith('/media/'):
                    source_path = os.path.join(settings.MEDIA_ROOT, video.video_url.replace('/media/', ''))
                elif video.video_url.startswith('http'):
                    # Download from URL
                    temp_dir = tempfile.mkdtemp()
                    temp_path = os.path.join(temp_dir, f'source_{vid}.mp4')
                    response = requests.get(video.video_url)
                    with open(temp_path, 'wb') as f:
                        f.write(response.content)
                    source_path = temp_path

            if not source_path or not os.path.exists(source_path):
                return JsonResponse({
                    'success': False,
                    'error': f'Source file not found for video {vid}'
                }, status=404)

            source_paths.append(source_path)

        logger.info(f"🎬 [Session 160] Concatenating {len(videos)} videos")

        # Create output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/concatenated/combined_{len(videos)}_videos_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create concat file list for ffmpeg
        concat_list_path = os.path.join(settings.MEDIA_ROOT, f"videos/concatenated/concat_list_{timestamp}.txt")
        os.makedirs(os.path.dirname(concat_list_path), exist_ok=True)

        with open(concat_list_path, 'w') as f:
            for path in source_paths:
                f.write(f"file '{path}'\n")

        logger.info(f"📝 [Session 160] Created concat list: {concat_list_path}")

        # Run ffmpeg concat
        # Using concat demuxer which is fast for same-codec videos
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_list_path,
            '-c', 'copy',  # Copy streams without re-encoding (fast!)
            '-y', output_path
        ]

        logger.info(f"🔧 [Session 160] Running: {' '.join(cmd)}")

        result = _run_ffmpeg(cmd)

        # If concat demuxer failed (different codecs), try re-encoding
        if result.returncode != 0:
            logger.warning(f"⚠️ [Session 160] Concat demuxer failed, trying re-encode")
            # Re-encode using filter_complex concat
            input_args = []
            filter_parts = []
            for i, path in enumerate(source_paths):
                input_args.extend(['-i', path])
                filter_parts.append(f'[{i}:v:0][{i}:a:0]')

            filter_complex = f"{''.join(filter_parts)}concat=n={len(source_paths)}:v=1:a=1[v][a]"

            cmd = ['ffmpeg'] + input_args + [
                '-filter_complex', filter_complex,
                '-map', '[v]', '-map', '[a]',
                '-y', output_path
            ]

            logger.info(f"🔧 [Session 160] Re-encode: {' '.join(cmd)}")
            result = _run_ffmpeg(cmd)

            # If still failing (maybe no audio), try video-only
            if result.returncode != 0:
                logger.warning(f"⚠️ [Session 160] Audio concat failed, trying video-only")
                filter_parts = []
                for i in range(len(source_paths)):
                    filter_parts.append(f'[{i}:v:0]')

                filter_complex = f"{''.join(filter_parts)}concat=n={len(source_paths)}:v=1:a=0[v]"

                cmd = ['ffmpeg'] + input_args + [
                    '-filter_complex', filter_complex,
                    '-map', '[v]',
                    '-y', output_path
                ]

                logger.info(f"🔧 [Session 160] Video-only: {' '.join(cmd)}")
                result = _run_ffmpeg(cmd)

        # Clean up concat list
        try:
            os.remove(concat_list_path)
        except Exception:
            pass

        if result.returncode != 0:
            logger.error(f"❌ [Session 160] ffmpeg concatenation failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'ffmpeg concatenation failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output file exists
        if not os.path.exists(output_path):
            return JsonResponse({
                'success': False,
                'error': 'Video concatenation produced no output'
            }, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Concatenated video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Calculate total duration
        total_duration = sum(v.duration or 0 for v in videos)

        # Get project if project_id provided, or use first video's project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 160] Linking concatenated video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 160] Project {project_id} not found")
        elif videos[0].project:
            project = videos[0].project
            logger.info(f"🔗 [Session 160] Using first video's project: {project.name}")

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        concat_video = VideoHistory.objects.create(
            user=request.user,
            video_type='concatenated',
            prompt=f"Concatenated {len(videos)} videos: {', '.join(str(v.id) for v in videos)}",
            duration=total_duration,
            model_used='ffmpeg_concat',
            ratio=videos[0].ratio,  # Use first video's ratio
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 160] Videos concatenated: {[str(v.id) for v in videos]} → {concat_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=concat_video,
                project=project,
                contribution_type='editing',
                task_description=f"Concatenated {len(videos)} videos using ffmpeg",
                execution_time_seconds=0.0
            )
            logger.info(f"✅ [Session 160] Agent contribution tracked for video {concat_video.id}")
        except Exception as e:
            logger.warning(f"⚠️ [Session 160] Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(concat_video.id),
            'video_url': concat_video.video_url,
            'video_count': len(videos),
            'source_videos': [str(v.id) for v in videos],
            'total_duration': total_duration,
            'message': f'Combined {len(videos)} videos into one ({total_duration}s total)',
            'agent': 'VideoEditingAgent',
            'operation': 'concatenate',
            'operation_display': f'Combining {len(videos)} videos'
        })

    except Exception as e:
        logger.error(f"❌ [Session 160] Video concatenation error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# SESSION 161: DAVINCI EXPANSION PHASE 2 - 5 NEW VIDEO EDITING FEATURES
# =============================================================================

def rotate_flip_video(request):
    """
    Rotate or flip a video using ffmpeg.

    Session 161: Rotate/Flip Feature
    Rotate by 90/180/270 degrees or flip horizontally/vertically.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/rotate/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "rotation": 90 | 180 | 270 | "horizontal" | "vertical" | "both"
    }

    Natural language examples:
    - "Rotate video 1 by 90 degrees"
    - "Flip video 3 horizontally"
    - "Turn video 2 upside down"
    - "Mirror video 5"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        rotation = data.get('rotation', 90)  # 90, 180, 270, "horizontal", "vertical", "both"
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Clean video_id
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")

        # Resolve hybrid ID - Session 162: Use project scope and created_at ordering for accurate ID resolution
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                # Session 162: Filter by project if provided, order by created_at to match frontend gallery
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = f'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 162] Resolved hybrid ID {numeric_id} → {video_uuid} (scope: {scope})")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🔄 [Session 161] Rotating/flipping video {video.id} with rotation={rotation}")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            # Download remote video
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        # Build ffmpeg filter based on rotation type
        if rotation in [90, '90', 'cw', 'clockwise']:
            vf_filter = 'transpose=1'  # 90 degrees clockwise
            rotation_desc = '90° clockwise'
        elif rotation in [180, '180', 'upside_down', 'upside-down']:
            vf_filter = 'transpose=1,transpose=1'  # 180 degrees
            rotation_desc = '180°'
        elif rotation in [270, '270', 'ccw', 'counterclockwise', -90, '-90']:
            vf_filter = 'transpose=2'  # 90 degrees counter-clockwise
            rotation_desc = '90° counter-clockwise'
        elif rotation in ['horizontal', 'hflip', 'mirror']:
            vf_filter = 'hflip'
            rotation_desc = 'horizontal flip'
        elif rotation in ['vertical', 'vflip']:
            vf_filter = 'vflip'
            rotation_desc = 'vertical flip'
        elif rotation in ['both', 'hvflip']:
            vf_filter = 'hflip,vflip'
            rotation_desc = 'horizontal and vertical flip'
        else:
            return JsonResponse({'success': False, 'error': f'Invalid rotation: {rotation}. Use 90, 180, 270, horizontal, vertical, or both'}, status=400)

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/rotated/rotated_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Run ffmpeg
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filter,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y', output_path
        ]

        logger.info(f"🚀 Running ffmpeg rotate: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp file
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg rotation failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg rotation failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Rotation produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Video rotated: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        rotated_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Rotated video {video.id} ({rotation_desc})",
            duration=video.duration,
            model_used='ffmpeg_rotate',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 161] Video rotated: {video.id} → {rotated_video.id} ({rotation_desc})")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=rotated_video,
                project=project,
                contribution_type='editing',
                task_description=f"Rotated video {rotation_desc} using ffmpeg",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(rotated_video.id),
            'video_url': rotated_video.video_url,
            'rotation': rotation_desc,
            'message': f'Video rotated ({rotation_desc}) successfully',
            'agent': 'VideoEditingAgent',
            'operation': 'rotate_flip',
            'operation_display': f'Rotating video {rotation_desc}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 161] Video rotation error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def fade_video(request):
    """
    Add fade in/out effects to a video using ffmpeg.

    Session 161: Fade In/Out Feature
    Add smooth fade transitions at the beginning and/or end of videos.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/fade/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "fade_in": 1.0,  # seconds for fade in (0 to disable)
        "fade_out": 1.0,  # seconds for fade out (0 to disable)
        "fade_color": "black"  # black or white
    }

    Natural language examples:
    - "Add fade in to video 1"
    - "Fade out video 3 over 2 seconds"
    - "Add 1 second fade in and fade out to video 2"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        fade_in = float(data.get('fade_in', 1.0))
        fade_out = float(data.get('fade_out', 1.0))
        fade_color = data.get('fade_color', 'black')
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        if fade_in <= 0 and fade_out <= 0:
            return JsonResponse({'success': False, 'error': 'At least one of fade_in or fade_out must be > 0'}, status=400)

        # Clean video_id
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")

        # Resolve hybrid ID - Session 162: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                # Session 162: Filter by project if provided, order by created_at to match frontend gallery
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 162] Fade: Resolved hybrid ID {numeric_id} → {video_uuid} (scope: {scope})")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🎬 [Session 161] Adding fade to video {video.id}: in={fade_in}s, out={fade_out}s")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        # Get video duration for fade out calculation
        duration = video.duration
        if not duration:
            # Get duration from ffprobe
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
            try:
                duration = float(probe_result.stdout.strip())
            except Exception:
                duration = 10.0  # Default fallback

        # Build video filter
        vf_filters = []
        af_filters = []

        if fade_in > 0:
            vf_filters.append(f"fade=t=in:st=0:d={fade_in}:color={fade_color}")
            af_filters.append(f"afade=t=in:st=0:d={fade_in}")

        if fade_out > 0:
            fade_out_start = max(0, duration - fade_out)
            vf_filters.append(f"fade=t=out:st={fade_out_start}:d={fade_out}:color={fade_color}")
            af_filters.append(f"afade=t=out:st={fade_out_start}:d={fade_out}")

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/faded/faded_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Check if video has audio
        has_audio = _video_has_audio(input_path)

        # Run ffmpeg
        if has_audio and af_filters:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', ','.join(vf_filters),
                '-af', ','.join(af_filters),
                '-y', output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', ','.join(vf_filters),
                '-c:a', 'copy',
                '-y', output_path
            ]

        logger.info(f"🚀 Running ffmpeg fade: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp file
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg fade failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg fade failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Fade produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Video faded: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Build description
        fade_desc = []
        if fade_in > 0:
            fade_desc.append(f"fade in {fade_in}s")
        if fade_out > 0:
            fade_desc.append(f"fade out {fade_out}s")
        fade_description = ' + '.join(fade_desc)

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        faded_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Added {fade_description} to video {video.id}",
            duration=duration,
            model_used='ffmpeg_fade',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 161] Video faded: {video.id} → {faded_video.id} ({fade_description})")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=faded_video,
                project=project,
                contribution_type='editing',
                task_description=f"Added {fade_description} using ffmpeg",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(faded_video.id),
            'video_url': faded_video.video_url,
            'fade_in': fade_in,
            'fade_out': fade_out,
            'message': f'Added {fade_description} successfully',
            'agent': 'VideoEditingAgent',
            'operation': 'fade',
            'operation_display': f'Adding {fade_description}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 161] Video fade error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def crop_resize_video(request):
    """
    Crop or resize a video using ffmpeg.

    Session 161: Crop/Resize Feature
    Crop to specific region or resize to new dimensions/aspect ratio.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/crop/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "mode": "crop" | "resize" | "aspect",
        "width": 1920,  # target width (for resize)
        "height": 1080,  # target height (for resize)
        "crop_x": 0,  # crop start X (for crop)
        "crop_y": 0,  # crop start Y (for crop)
        "crop_width": 640,  # crop width (for crop)
        "crop_height": 480,  # crop height (for crop)
        "aspect": "16:9" | "9:16" | "1:1" | "4:3"  # for aspect mode
    }

    Natural language examples:
    - "Crop video 1 to square"
    - "Resize video 3 to 1920x1080"
    - "Make video 2 portrait (9:16)"
    - "Convert video 5 to 4:3 aspect ratio"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        mode = data.get('mode', 'resize')  # crop, resize, aspect
        width = data.get('width')
        height = data.get('height')
        crop_x = data.get('crop_x', 0)
        crop_y = data.get('crop_y', 0)
        crop_width = data.get('crop_width')
        crop_height = data.get('crop_height')
        aspect = data.get('aspect', '16:9')
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Clean video_id
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")

        # Resolve hybrid ID - Session 162: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                # Session 162: Filter by project if provided, order by created_at to match frontend gallery
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 162] Crop/Resize: Resolved hybrid ID {numeric_id} → {video_uuid} (scope: {scope})")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"✂️ [Session 161] Crop/resize video {video.id}: mode={mode}")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        # Get current video dimensions
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', input_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        try:
            current_dims = probe_result.stdout.strip().split('x')
            current_width = int(current_dims[0])
            current_height = int(current_dims[1])
        except Exception:
            current_width, current_height = 1280, 720  # Default fallback

        # Build filter based on mode
        if mode == 'crop':
            if not crop_width or not crop_height:
                return JsonResponse({'success': False, 'error': 'crop_width and crop_height required for crop mode'}, status=400)
            vf_filter = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"
            operation_desc = f"cropped to {crop_width}x{crop_height}"
            new_ratio = f"{crop_width}:{crop_height}"

        elif mode == 'resize':
            if not width and not height:
                return JsonResponse({'success': False, 'error': 'width and/or height required for resize mode'}, status=400)
            if width and height:
                vf_filter = f"scale={width}:{height}"
                operation_desc = f"resized to {width}x{height}"
                new_ratio = f"{width}:{height}"
            elif width:
                vf_filter = f"scale={width}:-2"  # -2 maintains aspect ratio, ensures even number
                operation_desc = f"resized to width {width}"
                new_ratio = video.ratio
            else:
                vf_filter = f"scale=-2:{height}"
                operation_desc = f"resized to height {height}"
                new_ratio = video.ratio

        elif mode == 'aspect':
            # Aspect ratio presets
            aspect_ratios = {
                '16:9': (16, 9),
                '9:16': (9, 16),
                '1:1': (1, 1),
                '4:3': (4, 3),
                '3:4': (3, 4),
                '21:9': (21, 9),
                'square': (1, 1),
                'portrait': (9, 16),
                'landscape': (16, 9),
                'cinematic': (21, 9),
            }

            if aspect not in aspect_ratios:
                return JsonResponse({'success': False, 'error': f'Invalid aspect ratio: {aspect}. Use: {", ".join(aspect_ratios.keys())}'}, status=400)

            target_w, target_h = aspect_ratios[aspect]

            # Calculate crop dimensions to achieve target aspect ratio
            target_aspect = target_w / target_h
            current_aspect = current_width / current_height

            if current_aspect > target_aspect:
                # Video is wider than target - crop width
                new_width = int(current_height * target_aspect)
                new_height = current_height
                crop_x_offset = (current_width - new_width) // 2
                crop_y_offset = 0
            else:
                # Video is taller than target - crop height
                new_width = current_width
                new_height = int(current_width / target_aspect)
                crop_x_offset = 0
                crop_y_offset = (current_height - new_height) // 2

            vf_filter = f"crop={new_width}:{new_height}:{crop_x_offset}:{crop_y_offset}"
            operation_desc = f"converted to {aspect} aspect ratio"
            new_ratio = aspect
        else:
            return JsonResponse({'success': False, 'error': f'Invalid mode: {mode}. Use: crop, resize, or aspect'}, status=400)

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/cropped/cropped_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Run ffmpeg
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', vf_filter,
            '-c:a', 'copy',
            '-y', output_path
        ]

        logger.info(f"🚀 Running ffmpeg crop/resize: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp file
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg crop/resize failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg crop/resize failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Crop/resize produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Video cropped/resized: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        edited_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Video {video.id} {operation_desc}",
            duration=video.duration,
            model_used='ffmpeg_crop',
            ratio=new_ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 161] Video edited: {video.id} → {edited_video.id} ({operation_desc})")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=edited_video,
                project=project,
                contribution_type='editing',
                task_description=f"Video {operation_desc} using ffmpeg",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(edited_video.id),
            'video_url': edited_video.video_url,
            'mode': mode,
            'new_ratio': new_ratio,
            'message': f'Video {operation_desc} successfully',
            'agent': 'VideoEditingAgent',
            'operation': 'crop_resize',
            'operation_display': f'Video {operation_desc}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 161] Video crop/resize error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def audio_controls(request):
    """
    Control audio in a video using ffmpeg.

    Session 161: Audio Controls Feature
    Adjust volume, mute, or extract audio from videos.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/audio/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "operation": "volume" | "mute" | "extract",
        "volume": 1.5,  # for volume operation (0.5 = 50%, 2.0 = 200%)
        "output_format": "mp3" | "wav" | "aac"  # for extract operation
    }

    Natural language examples:
    - "Increase volume of video 1 to 150%"
    - "Mute video 3"
    - "Extract audio from video 2"
    - "Make video 5 quieter (50% volume)"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        operation = data.get('operation', 'volume')  # volume, mute, extract
        volume = float(data.get('volume', 1.0))
        output_format = data.get('output_format', 'mp3')
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Clean video_id
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")

        # Resolve hybrid ID - Session 162: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                # Session 162: Filter by project if provided, order by created_at to match frontend gallery
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 162] Audio: Resolved hybrid ID {numeric_id} → {video_uuid} (scope: {scope})")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🔊 [Session 161] Audio control on video {video.id}: operation={operation}")

        # Get input video path
        input_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        if operation == 'volume':
            # Adjust volume
            if volume < 0:
                return JsonResponse({'success': False, 'error': 'Volume must be >= 0'}, status=400)

            output_filename = f"videos/audio/volume_{timestamp}.mp4"
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            cmd = [
                'ffmpeg', '-i', input_path,
                '-af', f'volume={volume}',
                '-c:v', 'copy',
                '-y', output_path
            ]

            operation_desc = f"volume adjusted to {int(volume * 100)}%"

        elif operation == 'mute':
            # Remove audio completely
            output_filename = f"videos/audio/muted_{timestamp}.mp4"
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            cmd = [
                'ffmpeg', '-i', input_path,
                '-an',  # Remove audio
                '-c:v', 'copy',
                '-y', output_path
            ]

            operation_desc = "audio removed (muted)"

        elif operation == 'extract':
            # Extract audio to separate file
            if output_format not in ['mp3', 'wav', 'aac', 'm4a', 'flac']:
                output_format = 'mp3'

            output_filename = f"audio/extracted/audio_{timestamp}.{output_format}"
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if output_format == 'mp3':
                cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', '-y', output_path]
            elif output_format == 'wav':
                cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'pcm_s16le', '-y', output_path]
            elif output_format == 'aac':
                cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'aac', '-b:a', '192k', '-y', output_path]
            elif output_format == 'm4a':
                cmd = ['ffmpeg', '-i', input_path, '-vn', '-acodec', 'aac', '-b:a', '192k', '-y', output_path]
            else:
                cmd = ['ffmpeg', '-i', input_path, '-vn', '-y', output_path]

            operation_desc = f"audio extracted as {output_format.upper()}"

        else:
            return JsonResponse({'success': False, 'error': f'Invalid operation: {operation}. Use: volume, mute, or extract'}, status=400)

        logger.info(f"🚀 Running ffmpeg audio: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp file
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg audio operation failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg audio operation failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Audio operation produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Audio operation complete: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        if operation == 'extract':
            # For extract, we create an audio file, not a video
            # Return the audio URL directly
            return JsonResponse({
                'success': True,
                'audio_url': f'/media/{output_filename}',
                'format': output_format,
                'source_video_id': str(video.id),
                'message': f'Audio extracted from video as {output_format.upper()}',
                'agent': 'VideoEditingAgent',
                'operation': 'audio_extract',
                'operation_display': f'Extracting audio as {output_format.upper()}'
            })

        # For volume/mute, create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        edited_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Video {video.id} {operation_desc}",
            duration=video.duration,
            model_used='ffmpeg_audio',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 161] Video audio edited: {video.id} → {edited_video.id} ({operation_desc})")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=edited_video,
                project=project,
                contribution_type='editing',
                task_description=f"Audio {operation_desc} using ffmpeg",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(edited_video.id),
            'video_url': edited_video.video_url,
            'operation': operation,
            'volume': volume if operation == 'volume' else None,
            'message': f'Video {operation_desc} successfully',
            'agent': 'VideoEditingAgent',
            'operation': f'audio_{operation}',
            'operation_display': f'Video {operation_desc}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 161] Audio control error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def picture_in_picture(request):
    """
    Create picture-in-picture effect by overlaying one video on another.

    Session 161: Picture-in-Picture Feature
    Overlay a smaller video on top of a larger background video.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/pip/
    {
        "background_video_id": "uuid or hybrid ID",
        "overlay_video_id": "uuid or hybrid ID",
        "position": "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center",
        "scale": 0.25,  # scale of overlay (0.1-0.5, default 0.25 = 25%)
        "margin": 10,  # pixels from edge
        "opacity": 1.0  # overlay opacity (0.0-1.0)
    }

    Natural language examples:
    - "Put video 2 in the corner of video 1"
    - "Add video 3 as picture-in-picture on video 5"
    - "Overlay video 1 on video 4 in top right corner"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        bg_video_id = data.get('background_video_id')
        overlay_video_id = data.get('overlay_video_id')
        position = data.get('position', 'bottom-right')
        scale = float(data.get('scale', 0.25))
        margin = int(data.get('margin', 10))
        opacity = float(data.get('opacity', 1.0))
        project_id = data.get('project_id')

        if not bg_video_id or not overlay_video_id:
            return JsonResponse({'success': False, 'error': 'background_video_id and overlay_video_id required'}, status=400)

        if scale < 0.1 or scale > 0.8:
            return JsonResponse({'success': False, 'error': 'scale must be between 0.1 and 0.8'}, status=400)

        # Helper to resolve video ID - Session 162: Use project scope and created_at ordering
        def resolve_video_id(vid, user, proj_id=None):
            if isinstance(vid, str):
                vid = vid.strip().strip('"').strip("'")
            try:
                import uuid as uuid_module
                return uuid_module.UUID(vid)
            except (ValueError, AttributeError):
                try:
                    numeric_id = int(vid)
                    # Session 162: Filter by project if provided, order by created_at to match frontend gallery
                    if proj_id:
                        videos = VideoHistory.objects.filter(user=user, project_id=proj_id).order_by('created_at')
                        scope = 'project'
                    else:
                        videos = VideoHistory.objects.filter(user=user).order_by('created_at')
                        scope = 'all videos'
                    if numeric_id < 1 or numeric_id > videos.count():
                        return None
                    resolved_uuid = videos[numeric_id - 1].id
                    logger.info(f"🔄 [Session 162] PiP: Resolved hybrid ID {numeric_id} → {resolved_uuid} (scope: {scope})")
                    return resolved_uuid
                except Exception:
                    return None

        bg_uuid = resolve_video_id(bg_video_id, request.user, project_id)
        overlay_uuid = resolve_video_id(overlay_video_id, request.user, project_id)

        if not bg_uuid:
            return JsonResponse({'success': False, 'error': f'Background video {bg_video_id} not found'}, status=404)
        if not overlay_uuid:
            return JsonResponse({'success': False, 'error': f'Overlay video {overlay_video_id} not found'}, status=404)

        # Get videos from database
        try:
            bg_video = VideoHistory.objects.get(id=bg_uuid, user=request.user)
            overlay_video = VideoHistory.objects.get(id=overlay_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'One or both videos not found'}, status=404)

        if bg_video.status != 'completed' or overlay_video.status != 'completed':
            return JsonResponse({'success': False, 'error': 'Both videos must be completed'}, status=400)

        if not bg_video.video_url or not overlay_video.video_url:
            return JsonResponse({'success': False, 'error': 'Both videos must have video URLs'}, status=400)

        logger.info(f"🖼️ [Session 161] PiP: bg={bg_video.id}, overlay={overlay_video.id}, pos={position}")

        # Get input video paths
        temp_dir = tempfile.mkdtemp()

        def get_video_path(video, temp_dir, suffix):
            if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
                file_path = video.video_url.lstrip('/')
                if file_path.startswith('media/'):
                    file_path = file_path[6:]
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                if os.path.exists(full_path):
                    return full_path
            # Download
            response = requests.get(video.video_url, timeout=60, stream=True)
            response.raise_for_status()
            temp_path = os.path.join(temp_dir, f'{suffix}.mp4')
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return temp_path

        try:
            bg_path = get_video_path(bg_video, temp_dir, 'bg')
            overlay_path = get_video_path(overlay_video, temp_dir, 'overlay')
        except Exception as e:
            import shutil
            shutil.rmtree(temp_dir)
            return JsonResponse({'success': False, 'error': f'Failed to get video files: {str(e)}'}, status=500)

        # Get background video dimensions
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', bg_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        try:
            bg_dims = probe_result.stdout.strip().split('x')
            bg_width = int(bg_dims[0])
            bg_height = int(bg_dims[1])
        except Exception:
            bg_width, bg_height = 1280, 720

        # Calculate overlay size
        overlay_width = int(bg_width * scale)
        overlay_height = int(bg_height * scale)

        # Calculate position
        position_map = {
            'top-left': (margin, margin),
            'top-right': (bg_width - overlay_width - margin, margin),
            'bottom-left': (margin, bg_height - overlay_height - margin),
            'bottom-right': (bg_width - overlay_width - margin, bg_height - overlay_height - margin),
            'center': ((bg_width - overlay_width) // 2, (bg_height - overlay_height) // 2),
        }

        if position not in position_map:
            position = 'bottom-right'

        x_pos, y_pos = position_map[position]

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/pip/pip_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Build ffmpeg filter for PiP
        # Scale overlay and position it
        if opacity < 1.0:
            filter_complex = f"[1:v]scale={overlay_width}:{overlay_height},format=rgba,colorchannelmixer=aa={opacity}[pip];[0:v][pip]overlay={x_pos}:{y_pos}:shortest=1"
        else:
            filter_complex = f"[1:v]scale={overlay_width}:{overlay_height}[pip];[0:v][pip]overlay={x_pos}:{y_pos}:shortest=1"

        cmd = [
            'ffmpeg',
            '-i', bg_path,
            '-i', overlay_path,
            '-filter_complex', filter_complex,
            '-c:a', 'copy',
            '-y', output_path
        ]

        logger.info(f"🚀 Running ffmpeg PiP: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp dir
        import shutil
        shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg PiP failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg PiP failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'PiP produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ PiP video created: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif bg_video.project:
            project = bg_video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        pip_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Picture-in-Picture: {bg_video.id} + {overlay_video.id} ({position})",
            duration=min(bg_video.duration or 10, overlay_video.duration or 10),
            model_used='ffmpeg_pip',
            ratio=bg_video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 161] PiP video created: {pip_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=pip_video,
                project=project,
                contribution_type='editing',
                task_description=f"Created PiP with overlay at {position} using ffmpeg",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(pip_video.id),
            'video_url': pip_video.video_url,
            'background_video': str(bg_video.id),
            'overlay_video': str(overlay_video.id),
            'position': position,
            'scale': scale,
            'message': f'Picture-in-Picture created with overlay in {position}',
            'agent': 'VideoEditingAgent',
            'operation': 'picture_in_picture',
            'operation_display': f'Creating PiP with overlay in {position}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 161] PiP error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _video_has_audio(video_path):
    """Helper to check if video has an audio stream."""
    try:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
        result = _run_ffmpeg(cmd)
        return 'audio' in result.stdout
    except Exception:
        return True  # Assume it has audio if we can't check


def add_watermark(request):
    """
    Add watermark/logo overlay to video using ffmpeg.

    Session 163: Phase 3 Watermark Feature
    Overlay an image (logo, watermark) on video at specified position.
    Uses ffmpeg - completely FREE operation!

    POST /api/video/watermark/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "image_id": "uuid or hybrid ID of image to use as watermark",
        "position": "top_left" | "top_right" | "bottom_left" | "bottom_right" | "center",
        "opacity": 0.0-1.0 (default 0.8),
        "scale": 0.05-0.5 (default 0.15 = 15% of video width),
        "margin": pixels from edge (default 20)
    }

    Natural language examples:
    - "Add watermark to video 1 using image 5"
    - "Put my logo on video 2 in the bottom right"
    - "Add image 3 as watermark to videos 1-5"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        image_id = data.get('image_id')
        position = data.get('position', 'bottom_right')  # Default to bottom-right corner
        opacity = float(data.get('opacity', 0.8))  # Default 80% opacity
        scale = float(data.get('scale', 0.15))  # Default 15% of video width
        margin = int(data.get('margin', 20))  # Default 20px from edge
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)
        if not image_id:
            return JsonResponse({'success': False, 'error': 'image_id required (the watermark image)'}, status=400)

        # Validate parameters
        if opacity < 0 or opacity > 1:
            return JsonResponse({'success': False, 'error': 'opacity must be between 0 and 1'}, status=400)
        if scale < 0.05 or scale > 0.5:
            return JsonResponse({'success': False, 'error': 'scale must be between 0.05 and 0.5'}, status=400)
        if margin < 0 or margin > 200:
            return JsonResponse({'success': False, 'error': 'margin must be between 0 and 200'}, status=400)

        valid_positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center']
        if position not in valid_positions:
            return JsonResponse({'success': False, 'error': f'position must be one of: {valid_positions}'}, status=400)

        # Clean IDs
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")
        if isinstance(image_id, str):
            image_id = image_id.strip().strip('"').strip("'")

        # Resolve video hybrid ID - Session 163: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 163] Resolved video hybrid ID {numeric_id} → {video_uuid}")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Resolve image hybrid ID - Session 163: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            image_uuid = uuid_module.UUID(image_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(image_id)
                if project_id:
                    images = ImageHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    images = ImageHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all images'
                if numeric_id < 1 or numeric_id > images.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Image {numeric_id} not found in {scope} (valid range: 1-{images.count()})'
                    }, status=404)
                image_uuid = images[numeric_id - 1].id
                logger.info(f"🔄 [Session 163] Resolved image hybrid ID {numeric_id} → {image_uuid}")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid image_id: {image_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        # Get image from database
        try:
            image = ImageHistory.objects.get(id=image_uuid, user=request.user)
        except ImageHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Watermark image not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        if not image.file_path and not image.image_url:
            return JsonResponse({'success': False, 'error': 'Watermark image has no file_path or image_url'}, status=400)

        logger.info(f"🏷️ [Session 163] Adding watermark to video {video.id} using image {image.id} at {position}")

        # Get input video path
        input_video_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_video_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            # Download remote video
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_video_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        # Get watermark image path
        watermark_path = None
        watermark_temp = None
        if image.file_path:
            # Local file path
            if image.file_path.startswith('/media/') or image.file_path.startswith('media/'):
                file_path = image.file_path.lstrip('/')
                if file_path.startswith('media/'):
                    file_path = file_path[6:]
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            else:
                full_path = os.path.join(settings.MEDIA_ROOT, image.file_path)
            if os.path.exists(full_path):
                watermark_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Watermark image file not found: {full_path}'}, status=404)
        elif image.image_url:
            # Download remote image
            try:
                response = requests.get(image.image_url, timeout=30)
                response.raise_for_status()
                if not temp_dir:
                    temp_dir = tempfile.mkdtemp()
                watermark_temp = os.path.join(temp_dir, 'watermark.png')
                with open(watermark_temp, 'wb') as f:
                    f.write(response.content)
                watermark_path = watermark_temp
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download watermark image: {str(e)}'}, status=500)

        # Build ffmpeg filter for watermark overlay
        # Scale watermark to percentage of video width, apply opacity, position at specified corner
        # Position calculations:
        # - top_left: overlay=margin:margin
        # - top_right: overlay=W-w-margin:margin
        # - bottom_left: overlay=margin:H-h-margin
        # - bottom_right: overlay=W-w-margin:H-h-margin
        # - center: overlay=(W-w)/2:(H-h)/2

        position_map = {
            'top_left': f'{margin}:{margin}',
            'top_right': f'W-w-{margin}:{margin}',
            'bottom_left': f'{margin}:H-h-{margin}',
            'bottom_right': f'W-w-{margin}:H-h-{margin}',
            'center': '(W-w)/2:(H-h)/2'
        }
        overlay_position = position_map[position]

        # Build filter complex:
        # 1. Scale watermark to percentage of video width (maintain aspect ratio)
        # 2. Apply opacity using format and colorchannelmixer
        # 3. Overlay on video at specified position
        if opacity < 1.0:
            # With opacity: scale watermark, apply alpha, overlay
            filter_complex = f"[1:v]scale=iw*{scale}:-1,format=rgba,colorchannelmixer=aa={opacity}[wm];[0:v][wm]overlay={overlay_position}"
        else:
            # Full opacity: just scale and overlay
            filter_complex = f"[1:v]scale=iw*{scale}:-1[wm];[0:v][wm]overlay={overlay_position}"

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/watermarked/watermarked_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Run ffmpeg
        cmd = [
            'ffmpeg', '-i', input_video_path, '-i', watermark_path,
            '-filter_complex', filter_complex,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y', output_path
        ]

        logger.info(f"🚀 Running ffmpeg watermark: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp files
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg watermark failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg watermark failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Watermark operation produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Video watermarked: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        watermarked_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Added watermark (image {image.id}) to video {video.id} at {position}",
            duration=video.duration,
            model_used='ffmpeg_watermark',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 163] Video watermarked: {video.id} → {watermarked_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=watermarked_video,
                project=project,
                contribution_type='editing',
                task_description=f"Added watermark at {position} ({int(scale*100)}% scale, {int(opacity*100)}% opacity)",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(watermarked_video.id),
            'video_url': watermarked_video.video_url,
            'watermark_image_id': str(image.id),
            'position': position,
            'scale': scale,
            'opacity': opacity,
            'message': f'Watermark added at {position} ({int(scale*100)}% scale, {int(opacity*100)}% opacity)',
            'agent': 'VideoEditingAgent',
            'operation': 'add_watermark',
            'operation_display': f'Adding watermark at {position}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 163] Watermark error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def blur_region(request):
    """
    Blur a region of a video using ffmpeg.

    Session 163: Phase 3 Blur Region Feature
    Apply blur to a specific area of video for privacy/censoring.
    Uses ffmpeg boxblur - completely FREE operation!

    POST /api/video/blur/
    {
        "video_id": "uuid or hybrid ID (1, 2, 3)",
        "region": "top_left" | "top_right" | "bottom_left" | "bottom_right" | "center" | "custom",
        "x": pixel position (for custom region),
        "y": pixel position (for custom region),
        "width": region width (for custom, or percentage like "25%"),
        "height": region height (for custom, or percentage like "25%"),
        "blur_strength": 1-30 (default 15),
        "start_time": optional start time in seconds,
        "end_time": optional end time in seconds
    }

    Natural language examples:
    - "Blur the top left corner of video 1"
    - "Add blur to video 2"
    - "Blur the center of video 3"
    - "Add privacy blur to video 4 from 5 to 10 seconds"
    """
    if not request.user or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        region = data.get('region', 'center')  # Preset regions or 'custom'
        x = data.get('x', 0)
        y = data.get('y', 0)
        width = data.get('width')
        height = data.get('height')
        blur_strength = int(data.get('blur_strength', 15))  # 1-30, higher = more blur
        start_time = data.get('start_time')  # Optional: blur only during this time range
        end_time = data.get('end_time')
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Validate blur strength
        if blur_strength < 1 or blur_strength > 30:
            return JsonResponse({'success': False, 'error': 'blur_strength must be between 1 and 30'}, status=400)

        # Clean video_id
        if isinstance(video_id, str):
            video_id = video_id.strip().strip('"').strip("'")

        # Resolve video hybrid ID - Session 163: Use project scope and created_at ordering
        try:
            import uuid as uuid_module
            video_uuid = uuid_module.UUID(video_id)
        except (ValueError, AttributeError):
            try:
                numeric_id = int(video_id)
                if project_id:
                    videos = VideoHistory.objects.filter(user=request.user, project_id=project_id).order_by('created_at')
                    scope = 'project'
                else:
                    videos = VideoHistory.objects.filter(user=request.user).order_by('created_at')
                    scope = 'all videos'
                if numeric_id < 1 or numeric_id > videos.count():
                    return JsonResponse({
                        'success': False,
                        'error': f'Video {numeric_id} not found in {scope} (valid range: 1-{videos.count()})'
                    }, status=404)
                video_uuid = videos[numeric_id - 1].id
                logger.info(f"🔄 [Session 163] Resolved video hybrid ID {numeric_id} → {video_uuid}")
            except (ValueError, IndexError) as e:
                return JsonResponse({'success': False, 'error': f'Invalid video_id: {video_id}'}, status=400)

        # Get video from database
        try:
            video = VideoHistory.objects.get(id=video_uuid, user=request.user)
        except VideoHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'}, status=404)

        if video.status != 'completed':
            return JsonResponse({'success': False, 'error': f'Video is {video.status}, must be completed'}, status=400)

        if not video.video_url:
            return JsonResponse({'success': False, 'error': 'Video has no video_url'}, status=400)

        logger.info(f"🔲 [Session 163] Adding blur to video {video.id} at region={region}")

        # Get input video path
        input_video_path = None
        temp_dir = None
        if video.video_url.startswith('/media/') or video.video_url.startswith('media/'):
            file_path = video.video_url.lstrip('/')
            if file_path.startswith('media/'):
                file_path = file_path[6:]
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(full_path):
                input_video_path = full_path
            else:
                return JsonResponse({'success': False, 'error': f'Video file not found: {full_path}'}, status=404)
        else:
            # Download remote video
            try:
                response = requests.get(video.video_url, timeout=60, stream=True)
                response.raise_for_status()
                temp_dir = tempfile.mkdtemp()
                input_video_path = os.path.join(temp_dir, 'input.mp4')
                with open(input_video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Failed to download video: {str(e)}'}, status=500)

        # Get video dimensions using ffprobe
        try:
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', input_video_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
            dimensions = probe_result.stdout.strip().split(',')
            video_width = int(dimensions[0])
            video_height = int(dimensions[1])
            logger.info(f"📐 Video dimensions: {video_width}x{video_height}")
        except Exception as e:
            logger.warning(f"⚠️ Could not get video dimensions, using defaults: {e}")
            video_width = 1920
            video_height = 1080

        # Calculate blur region based on preset or custom
        valid_regions = ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center', 'custom', 'full']
        if region not in valid_regions:
            return JsonResponse({'success': False, 'error': f'region must be one of: {valid_regions}'}, status=400)

        # Default region size is 25% of video dimensions
        default_w = video_width // 4
        default_h = video_height // 4

        if region == 'full':
            # Blur entire video
            blur_x, blur_y = 0, 0
            blur_w, blur_h = video_width, video_height
        elif region == 'custom':
            # Use provided x, y, width, height
            blur_x = int(x) if x else 0
            blur_y = int(y) if y else 0
            blur_w = int(width) if width else default_w
            blur_h = int(height) if height else default_h
        else:
            # Preset regions (corners and center)
            blur_w = int(width) if width else default_w
            blur_h = int(height) if height else default_h

            region_positions = {
                'top_left': (0, 0),
                'top_right': (video_width - blur_w, 0),
                'bottom_left': (0, video_height - blur_h),
                'bottom_right': (video_width - blur_w, video_height - blur_h),
                'center': ((video_width - blur_w) // 2, (video_height - blur_h) // 2)
            }
            blur_x, blur_y = region_positions[region]

        # Ensure blur region is within video bounds
        blur_x = max(0, min(blur_x, video_width - 1))
        blur_y = max(0, min(blur_y, video_height - 1))
        blur_w = max(1, min(blur_w, video_width - blur_x))
        blur_h = max(1, min(blur_h, video_height - blur_y))

        logger.info(f"🔲 Blur region: x={blur_x}, y={blur_y}, w={blur_w}, h={blur_h}, strength={blur_strength}")

        # Build ffmpeg filter
        # Method: Crop the region, blur it, overlay back on original position
        if region == 'full':
            # Full video blur is simpler
            filter_complex = f"boxblur={blur_strength}:{blur_strength}"
        else:
            # Region blur: crop -> blur -> overlay
            filter_complex = f"[0:v]crop={blur_w}:{blur_h}:{blur_x}:{blur_y},boxblur={blur_strength}:{blur_strength}[blur];[0:v][blur]overlay={blur_x}:{blur_y}"

        # Add time-based enable if start/end times provided
        if start_time is not None or end_time is not None:
            start_t = float(start_time) if start_time is not None else 0
            end_t = float(end_time) if end_time is not None else 9999
            # Use enable expression for time-based blur
            if region == 'full':
                filter_complex = f"boxblur={blur_strength}:{blur_strength}:enable='between(t,{start_t},{end_t})'"
            else:
                filter_complex = f"[0:v]crop={blur_w}:{blur_h}:{blur_x}:{blur_y},boxblur={blur_strength}:{blur_strength}[blur];[0:v][blur]overlay={blur_x}:{blur_y}:enable='between(t,{start_t},{end_t})'"

        # Generate output path
        from django.utils import timezone as tz
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"videos/blurred/blurred_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Run ffmpeg
        cmd = [
            'ffmpeg', '-i', input_video_path,
            '-filter_complex' if '[' in filter_complex else '-vf', filter_complex,
            '-c:a', 'copy',  # Copy audio without re-encoding
            '-y', output_path
        ]

        logger.info(f"🚀 Running ffmpeg blur: {' '.join(cmd)}")
        result = _run_ffmpeg(cmd)

        # Clean up temp files
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

        if result.returncode != 0:
            logger.error(f"❌ ffmpeg blur failed: {result.stderr}")
            return JsonResponse({'success': False, 'error': f'ffmpeg blur failed: {result.stderr[:200]}'}, status=500)

        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Blur operation produced no output'}, status=500)

        file_size = os.path.getsize(output_path)
        logger.info(f"✅ Video blurred: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

        # Get project
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
            except CreativeProject.DoesNotExist:
                pass
        elif video.project:
            project = video.project

        # Build region description
        time_desc = ""
        if start_time is not None or end_time is not None:
            time_desc = f" from {start_time or 0}s to {end_time or 'end'}s"

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        blurred_video = VideoHistory.objects.create(
            user=request.user,
            video_type='edited',
            prompt=f"Added blur to video {video.id} at {region} (strength {blur_strength}){time_desc}",
            duration=video.duration,
            model_used='ffmpeg_blur',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 163] Video blurred: {video.id} → {blurred_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=blurred_video,
                project=project,
                contribution_type='editing',
                task_description=f"Added blur at {region} (strength {blur_strength}){time_desc}",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(blurred_video.id),
            'video_url': blurred_video.video_url,
            'region': region,
            'blur_strength': blur_strength,
            'blur_area': {'x': blur_x, 'y': blur_y, 'width': blur_w, 'height': blur_h},
            'message': f'Blur added at {region} (strength {blur_strength}){time_desc}',
            'agent': 'VideoEditingAgent',
            'operation': 'blur_region',
            'operation_display': f'Adding blur at {region}'
        })

    except Exception as e:
        logger.error(f"❌ [Session 163] Blur error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def stabilize_video(request):
    """
    Session 164: Phase 3 - Video Stabilization

    Stabilizes shaky video footage using ffmpeg's vidstab filters.
    Two-pass process: detect motion -> apply stabilization.

    Parameters:
        video_id: Video ID (UUID or hybrid number like "1", "2")
        shakiness: Detection sensitivity 1-10 (default 5, higher = detect more shake)
        accuracy: Detection accuracy 1-15 (default 15, higher = more accurate but slower)
        smoothing: Smoothing strength 0-100 (default 10, higher = smoother but may crop more)
        crop: How to handle borders - 'black' (pad with black) or 'keep' (zoom to hide)
        zoom: Additional zoom 0-10% (default 0, helps hide black borders)
        project_id: Optional project ID for scoping

    Returns:
        JSON with stabilized video details

    Voice commands:
        "Stabilize video 1"
        "Fix shaky video 2"
        "Smooth out video 3"
        "Remove camera shake from video 4"
    """
    import tempfile
    import subprocess
    from django.utils import timezone as tz
    from content.models import VideoHistory, CreativeProject

    logger.info("🎬 [Session 164] stabilize_video() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id = data.get('video_id') or request.POST.get('video_id')
        shakiness = int(data.get('shakiness', 5))
        accuracy = int(data.get('accuracy', 15))
        smoothing = int(data.get('smoothing', 10))
        crop_mode = data.get('crop', 'keep')  # 'black' or 'keep'
        zoom = float(data.get('zoom', 0))
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id is required'}, status=400)

        # Validate parameters
        shakiness = max(1, min(10, shakiness))
        accuracy = max(1, min(15, accuracy))
        smoothing = max(0, min(100, smoothing))
        zoom = max(0, min(10, zoom))
        if crop_mode not in ['black', 'keep']:
            crop_mode = 'keep'

        logger.info(f"📊 [Session 164] Stabilization params: shakiness={shakiness}, accuracy={accuracy}, smoothing={smoothing}, crop={crop_mode}, zoom={zoom}")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Resolve video ID (hybrid ID support)
        video = None
        from django.core.exceptions import ValidationError

        # Try as UUID first
        try:
            video = VideoHistory.objects.get(id=video_id)
        except (VideoHistory.DoesNotExist, ValueError, ValidationError):
            pass

        # Try as hybrid number
        if not video and video_id:
            try:
                video_num = int(str(video_id).strip())
                if project:
                    videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                else:
                    videos = VideoHistory.objects.order_by('created_at')

                if 1 <= video_num <= videos.count():
                    video = videos[video_num - 1]
                    logger.info(f"🔢 [Session 164] Resolved video {video_num} → {video.id}")
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({'success': False, 'error': f'Video not found: {video_id}'}, status=404)

        # Get video file path
        if video.video_url:
            if video.video_url.startswith('/media/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
            else:
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url)
        else:
            return JsonResponse({'success': False, 'error': 'Video has no file path'}, status=400)

        if not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': f'Video file not found: {video_path}'}, status=404)

        logger.info(f"📁 [Session 164] Source video: {video_path}")

        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'stabilized')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'videos/stabilized/stabilized_{timestamp}.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Create temp file for transforms data
        transforms_file = tempfile.NamedTemporaryFile(suffix='.trf', delete=False)
        transforms_path = transforms_file.name
        transforms_file.close()

        try:
            # PASS 1: Detect motion and create transforms file
            logger.info(f"🔍 [Session 164] Pass 1: Detecting motion (shakiness={shakiness}, accuracy={accuracy})...")

            detect_filter = f"vidstabdetect=shakiness={shakiness}:accuracy={accuracy}:result={transforms_path}"

            detect_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', detect_filter,
                '-f', 'null', '-'  # Don't output video, just analyze
            ]

            logger.info(f"🔧 [Session 164] Detect command: {' '.join(detect_cmd)}")

            result1 = subprocess.run(
                detect_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for analysis
            )

            if result1.returncode != 0:
                logger.error(f"❌ [Session 164] Motion detection failed: {result1.stderr}")
                return JsonResponse({
                    'success': False,
                    'error': f'Motion detection failed. vidstab may not be installed. Error: {result1.stderr[:200]}'
                }, status=500)

            # Verify transforms file was created
            if not os.path.exists(transforms_path):
                return JsonResponse({
                    'success': False,
                    'error': 'Motion analysis file was not created'
                }, status=500)

            logger.info(f"✅ [Session 164] Pass 1 complete. Transforms file: {transforms_path}")

            # PASS 2: Apply stabilization
            logger.info(f"🎬 [Session 164] Pass 2: Applying stabilization (smoothing={smoothing}, crop={crop_mode}, zoom={zoom})...")

            # Build transform filter
            transform_opts = [
                f"smoothing={smoothing}",
                f"crop={crop_mode}",
                f"zoom={zoom}",
                f"input={transforms_path}"
            ]
            transform_filter = f"vidstabtransform={':'.join(transform_opts)}"

            # Check if video has audio
            probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in probe_result.stdout

            # Build ffmpeg command
            if has_audio:
                transform_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', transform_filter,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    output_path
                ]
            else:
                transform_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', transform_filter,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-an',
                    output_path
                ]

            logger.info(f"🔧 [Session 164] Transform command: {' '.join(transform_cmd)}")

            result2 = subprocess.run(
                transform_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for processing
            )

            if result2.returncode != 0:
                logger.error(f"❌ [Session 164] Stabilization failed: {result2.stderr}")
                return JsonResponse({
                    'success': False,
                    'error': f'Stabilization failed: {result2.stderr[:200]}'
                }, status=500)

        finally:
            # Clean up transforms file
            if os.path.exists(transforms_path):
                os.remove(transforms_path)

        # Verify output was created
        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Stabilized video was not created'}, status=500)

        output_size = os.path.getsize(output_path)
        logger.info(f"✅ [Session 164] Stabilized video created: {output_path} ({output_size} bytes)")

        # Get project from source video if not specified
        if not project and video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        _user = request.user if request.user.is_authenticated else None
        stabilized_video = VideoHistory.objects.create(
            user=_user,
            prompt=f"Stabilized video {video.id} (shakiness={shakiness}, smoothing={smoothing}, crop={crop_mode})",
            duration=video.duration,
            model_used='ffmpeg_vidstab',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(_user) if _user else None,
        )

        logger.info(f"✅ [Session 164] Video stabilized: {video.id} → {stabilized_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=stabilized_video,
                project=project,
                contribution_type='editing',
                task_description=f"Stabilized video (shakiness={shakiness}, smoothing={smoothing})",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(stabilized_video.id),
            'video_url': stabilized_video.video_url,
            'shakiness': shakiness,
            'accuracy': accuracy,
            'smoothing': smoothing,
            'crop': crop_mode,
            'zoom': zoom,
            'message': f'Video stabilized (shakiness={shakiness}, smoothing={smoothing}, crop={crop_mode})',
            'agent': 'VideoEditingAgent',
            'operation': 'stabilize_video',
            'operation_display': 'Stabilizing shaky video'
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 164] Stabilization timed out")
        return JsonResponse({'success': False, 'error': 'Stabilization timed out - video may be too long'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 164] Stabilization error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def add_text_animation(request):
    """
    Session 164: Phase 3 - Animated Text Overlays

    Adds animated text to videos with various effects like scrolling,
    fade in/out, typing effect, and more.

    Parameters:
        video_id: Video ID (UUID or hybrid number like "1", "2")
        text: The text to display
        animation: Animation type - 'static', 'scroll_left', 'scroll_right',
                   'scroll_up', 'scroll_down', 'fade_in', 'fade_out', 'fade_in_out'
        position: Position - 'top', 'center', 'bottom', 'top_left', 'top_right',
                  'bottom_left', 'bottom_right' (default: 'bottom')
        font_size: Font size in pixels (default: 48)
        font_color: Font color (default: 'white')
        bg_color: Background box color (default: None/transparent)
        bg_opacity: Background opacity 0.0-1.0 (default: 0.5)
        start_time: When to start showing text in seconds (default: 0)
        duration: How long to show text in seconds (default: entire video)
        speed: Animation speed for scrolling (default: 100 pixels/second)
        project_id: Optional project ID for scoping

    Returns:
        JSON with text-animated video details

    Voice commands:
        "Add scrolling text to video 1"
        "Add title 'Hello World' to video 2"
        "Add credits to video 3"
        "Add text 'Subscribe!' at the bottom of video 4"
    """
    import subprocess
    from django.utils import timezone as tz
    from django.core.exceptions import ValidationError
    from content.models import VideoHistory, CreativeProject

    logger.info("🎬 [Session 164] add_text_animation() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id = data.get('video_id') or request.POST.get('video_id')
        text = data.get('text', 'Sample Text')
        animation = data.get('animation', 'static')
        position = data.get('position', 'bottom')
        font_size = int(data.get('font_size', 48))
        font_color = data.get('font_color', 'white')
        bg_color = data.get('bg_color')
        bg_opacity = float(data.get('bg_opacity', 0.5))
        start_time = float(data.get('start_time', 0))
        duration = data.get('duration')  # None means entire video
        speed = int(data.get('speed', 100))
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id is required'}, status=400)

        if not text:
            return JsonResponse({'success': False, 'error': 'text is required'}, status=400)

        # Validate parameters
        font_size = max(12, min(200, font_size))
        bg_opacity = max(0.0, min(1.0, bg_opacity))
        speed = max(10, min(500, speed))

        valid_animations = ['static', 'scroll_left', 'scroll_right', 'scroll_up', 'scroll_down',
                           'fade_in', 'fade_out', 'fade_in_out']
        if animation not in valid_animations:
            animation = 'static'

        valid_positions = ['top', 'center', 'bottom', 'top_left', 'top_right',
                          'bottom_left', 'bottom_right']
        if position not in valid_positions:
            position = 'bottom'

        logger.info(f"📊 [Session 164] Text animation params: text='{text[:20]}...', animation={animation}, position={position}")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Resolve video ID (hybrid ID support)
        video = None

        # Try as UUID first
        try:
            video = VideoHistory.objects.get(id=video_id)
        except (VideoHistory.DoesNotExist, ValueError, ValidationError):
            pass

        # Try as hybrid number
        if not video and video_id:
            try:
                video_num = int(str(video_id).strip())
                if project:
                    videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                else:
                    videos = VideoHistory.objects.order_by('created_at')

                if 1 <= video_num <= videos.count():
                    video = videos[video_num - 1]
                    logger.info(f"🔢 [Session 164] Resolved video {video_num} → {video.id}")
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({'success': False, 'error': f'Video not found: {video_id}'}, status=404)

        # Get video file path
        if video.video_url:
            if video.video_url.startswith('/media/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
            else:
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url)
        else:
            return JsonResponse({'success': False, 'error': 'Video has no file path'}, status=400)

        if not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': f'Video file not found: {video_path}'}, status=404)

        logger.info(f"📁 [Session 164] Source video: {video_path}")

        # Get video dimensions using ffprobe
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                     '-show_entries', 'stream=width,height,duration',
                     '-of', 'csv=p=0', video_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)

        try:
            parts = probe_result.stdout.strip().split(',')
            video_width = int(parts[0])
            video_height = int(parts[1])
            video_duration = float(parts[2]) if len(parts) > 2 and parts[2] else 10.0
        except (ValueError, IndexError):
            video_width, video_height, video_duration = 1920, 1080, 10.0

        logger.info(f"📐 [Session 164] Video dimensions: {video_width}x{video_height}, duration: {video_duration}s")

        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'text_animated')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'videos/text_animated/text_animated_{timestamp}.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Calculate text position based on position parameter
        margin = 20
        position_map = {
            'top': f'x=(w-text_w)/2:y={margin}',
            'center': 'x=(w-text_w)/2:y=(h-text_h)/2',
            'bottom': f'x=(w-text_w)/2:y=h-text_h-{margin}',
            'top_left': f'x={margin}:y={margin}',
            'top_right': f'x=w-text_w-{margin}:y={margin}',
            'bottom_left': f'x={margin}:y=h-text_h-{margin}',
            'bottom_right': f'x=w-text_w-{margin}:y=h-text_h-{margin}'
        }
        base_position = position_map.get(position, position_map['bottom'])

        # Escape special characters in text for ffmpeg
        escaped_text = text.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\")

        # Build drawtext filter based on animation type
        if animation == 'static':
            # Static text - just display at position
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:{base_position}"

        elif animation == 'scroll_left':
            # Scroll from right to left (news ticker style)
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:x=w-mod(t*{speed}\\,w+text_w):y=h-text_h-{margin}"

        elif animation == 'scroll_right':
            # Scroll from left to right
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:x=-text_w+mod(t*{speed}\\,w+text_w):y=h-text_h-{margin}"

        elif animation == 'scroll_up':
            # Scroll from bottom to top (credits style)
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=h-mod(t*{speed}\\,h+text_h)"

        elif animation == 'scroll_down':
            # Scroll from top to bottom
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=-text_h+mod(t*{speed}\\,h+text_h)"

        elif animation == 'fade_in':
            # Fade in over 1 second
            fade_duration = 1.0
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}@'if(lt(t,{fade_duration}),t/{fade_duration},1)':{base_position}"

        elif animation == 'fade_out':
            # Fade out at the end
            fade_start = video_duration - 1.0
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}@'if(gt(t,{fade_start}),1-(t-{fade_start}),1)':{base_position}"

        elif animation == 'fade_in_out':
            # Fade in at start, fade out at end
            fade_duration = 1.0
            fade_out_start = video_duration - fade_duration
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}@'if(lt(t,{fade_duration}),t/{fade_duration},if(gt(t,{fade_out_start}),1-(t-{fade_out_start})/{fade_duration},1))':{base_position}"

        else:
            drawtext_filter = f"drawtext=text='{escaped_text}':fontsize={font_size}:fontcolor={font_color}:{base_position}"

        # Add background box if specified
        if bg_color:
            box_opacity = int(bg_opacity * 255)
            drawtext_filter += f":box=1:boxcolor={bg_color}@{bg_opacity}:boxborderw=10"

        # Add time-based enable if start_time or duration specified
        if start_time > 0 or duration:
            end_time = start_time + duration if duration else video_duration
            drawtext_filter += f":enable='between(t,{start_time},{end_time})'"

        logger.info(f"🎨 [Session 164] Drawtext filter: {drawtext_filter[:100]}...")

        # Check if video has audio
        audio_probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                          '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
        audio_result = subprocess.run(audio_probe_cmd, capture_output=True, text=True, timeout=30)
        has_audio = 'audio' in audio_result.stdout

        # Build ffmpeg command
        if has_audio:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', drawtext_filter,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]
        else:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', drawtext_filter,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-an',
                output_path
            ]

        logger.info(f"🔧 [Session 164] FFmpeg command: {' '.join(ffmpeg_cmd)[:200]}...")

        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"❌ [Session 164] Text animation failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'Text animation failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output was created
        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Text animated video was not created'}, status=500)

        output_size = os.path.getsize(output_path)
        logger.info(f"✅ [Session 164] Text animated video created: {output_path} ({output_size} bytes)")

        # Get project from source video if not specified
        if not project and video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        _user = request.user if request.user.is_authenticated else None
        animated_video = VideoHistory.objects.create(
            user=_user,
            prompt=f"Added '{animation}' text animation: '{text[:30]}...' to video {video.id}",
            duration=video.duration,
            model_used='ffmpeg_drawtext',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(_user) if _user else None,
        )

        logger.info(f"✅ [Session 164] Text animation added: {video.id} → {animated_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=animated_video,
                project=project,
                contribution_type='editing',
                task_description=f"Added {animation} text animation: '{text[:30]}...'",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(animated_video.id),
            'video_url': animated_video.video_url,
            'text': text,
            'animation': animation,
            'position': position,
            'font_size': font_size,
            'font_color': font_color,
            'message': f"Text animation added: '{text[:30]}...' ({animation} at {position})",
            'agent': 'VideoEditingAgent',
            'operation': 'add_text_animation',
            'operation_display': f"Adding {animation} text animation"
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 164] Text animation timed out")
        return JsonResponse({'success': False, 'error': 'Text animation timed out - video may be too long'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 164] Text animation error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def chroma_key(request):
    """
    Session 165: Phase 3 - Green Screen / Chroma Key

    Removes a specified background color (green screen, blue screen, etc.)
    and either makes it transparent or replaces it with a background video/image.

    Parameters:
        video_id: Video ID (UUID or hybrid number like "1", "2")
        key_color: Color to remove - 'green', 'blue', or hex color '#00FF00' (default: 'green')
        similarity: How similar colors need to be to key_color (0.0-1.0, default: 0.3)
        blend: How much to blend edges (0.0-1.0, default: 0.1)
        background_video_id: Optional video ID to use as background replacement
        background_image_id: Optional image ID to use as background replacement
        background_color: Optional solid color for background (default: transparent if no background)
        project_id: Optional project ID for scoping

    Returns:
        JSON with chroma-keyed video details

    Voice commands:
        "Remove green screen from video 1"
        "Apply chroma key to video 2"
        "Remove blue screen from video 3"
        "Replace green screen in video 4 with video 5"
        "Remove green background from video 1"
    """
    import subprocess
    from django.utils import timezone as tz
    from django.core.exceptions import ValidationError
    from content.models import VideoHistory, ImageHistory, CreativeProject

    logger.info("🎬 [Session 165] chroma_key() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id = data.get('video_id') or request.POST.get('video_id')
        key_color = data.get('key_color', 'green')
        similarity = float(data.get('similarity', 0.3))
        blend = float(data.get('blend', 0.1))
        background_video_id = data.get('background_video_id')
        background_image_id = data.get('background_image_id')
        background_color = data.get('background_color')
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id is required'}, status=400)

        # Validate parameters
        similarity = max(0.01, min(1.0, similarity))
        blend = max(0.0, min(1.0, blend))

        # Convert named colors to hex
        color_map = {
            'green': '00FF00',
            'blue': '0000FF',
            'magenta': 'FF00FF',
            'red': 'FF0000',
            'yellow': 'FFFF00',
            'cyan': '00FFFF',
            'lime': '32CD32',
            'chroma_green': '00B140',  # Standard chroma green
            'chroma_blue': '0047AB'    # Standard chroma blue
        }

        if key_color.lower() in color_map:
            hex_color = color_map[key_color.lower()]
        elif key_color.startswith('#'):
            hex_color = key_color[1:]  # Remove # prefix
        else:
            hex_color = key_color

        # Validate hex color
        if not all(c in '0123456789ABCDEFabcdef' for c in hex_color) or len(hex_color) != 6:
            hex_color = '00FF00'  # Default to green if invalid

        logger.info(f"📊 [Session 165] Chroma key params: color={key_color} (#{hex_color}), similarity={similarity}, blend={blend}")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Resolve video ID (hybrid ID support)
        video = None

        # Try as UUID first
        try:
            video = VideoHistory.objects.get(id=video_id)
        except (VideoHistory.DoesNotExist, ValueError, ValidationError):
            pass

        # Try as hybrid number
        if not video and video_id:
            try:
                video_num = int(str(video_id).strip())
                if project:
                    videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                else:
                    videos = VideoHistory.objects.order_by('created_at')

                if 1 <= video_num <= videos.count():
                    video = videos[video_num - 1]
                    logger.info(f"🔢 [Session 165] Resolved video {video_num} → {video.id}")
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({'success': False, 'error': f'Video not found: {video_id}'}, status=404)

        # Get video file path
        if video.video_url:
            if video.video_url.startswith('/media/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
            else:
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url)
        else:
            return JsonResponse({'success': False, 'error': 'Video has no file path'}, status=400)

        if not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': f'Video file not found: {video_path}'}, status=404)

        logger.info(f"📁 [Session 165] Source video: {video_path}")

        # Resolve background video if specified
        bg_video_path = None
        if background_video_id:
            bg_video = None
            try:
                bg_video = VideoHistory.objects.get(id=background_video_id)
            except (VideoHistory.DoesNotExist, ValueError, ValidationError):
                pass

            if not bg_video:
                try:
                    bg_num = int(str(background_video_id).strip())
                    if project:
                        videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                    else:
                        videos = VideoHistory.objects.order_by('created_at')
                    if 1 <= bg_num <= videos.count():
                        bg_video = videos[bg_num - 1]
                except (ValueError, TypeError):
                    pass

            if bg_video and bg_video.video_url:
                if bg_video.video_url.startswith('/media/'):
                    bg_video_path = os.path.join(settings.MEDIA_ROOT, bg_video.video_url[7:])
                else:
                    bg_video_path = os.path.join(settings.MEDIA_ROOT, bg_video.video_url)

                if not os.path.exists(bg_video_path):
                    logger.warning(f"⚠️ Background video not found: {bg_video_path}")
                    bg_video_path = None

        # Resolve background image if specified
        bg_image_path = None
        if background_image_id and not bg_video_path:
            bg_image = None
            try:
                bg_image = ImageHistory.objects.get(id=background_image_id)
            except (ImageHistory.DoesNotExist, ValueError, ValidationError):
                pass

            if not bg_image:
                try:
                    bg_num = int(str(background_image_id).strip())
                    if project:
                        images = ImageHistory.objects.filter(project=project).order_by('created_at')
                    else:
                        images = ImageHistory.objects.order_by('created_at')
                    if 1 <= bg_num <= images.count():
                        bg_image = images[bg_num - 1]
                except (ValueError, TypeError):
                    pass

            if bg_image and bg_image.image_url:
                if bg_image.image_url.startswith('/media/'):
                    bg_image_path = os.path.join(settings.MEDIA_ROOT, bg_image.image_url[7:])
                else:
                    bg_image_path = os.path.join(settings.MEDIA_ROOT, bg_image.image_url)

                if not os.path.exists(bg_image_path):
                    logger.warning(f"⚠️ Background image not found: {bg_image_path}")
                    bg_image_path = None

        # Get video dimensions using ffprobe
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                     '-show_entries', 'stream=width,height,duration',
                     '-of', 'csv=p=0', video_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)

        try:
            parts = probe_result.stdout.strip().split(',')
            video_width = int(parts[0])
            video_height = int(parts[1])
            video_duration = float(parts[2]) if len(parts) > 2 and parts[2] else 10.0
        except (ValueError, IndexError):
            video_width, video_height, video_duration = 1920, 1080, 10.0

        logger.info(f"📐 [Session 165] Video dimensions: {video_width}x{video_height}, duration: {video_duration}s")

        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'chroma_keyed')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')

        # Build ffmpeg filter and command based on background type
        if bg_video_path:
            # Replace green screen with background video
            output_filename = f'videos/chroma_keyed/chromakey_{timestamp}.mp4'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            # Filter: overlay chroma-keyed foreground on background video
            # [0:v] = foreground (with green screen)
            # [1:v] = background video
            filter_complex = (
                f"[0:v]chromakey=0x{hex_color}:similarity={similarity}:blend={blend}[fg];"
                f"[1:v]scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
                f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2[bg];"
                f"[bg][fg]overlay=0:0:shortest=1[out]"
            )

            # Check if videos have audio
            audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                          '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
            audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in audio_result.stdout

            if has_audio:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', bg_video_path,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-map', '0:a?',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-shortest',
                    output_path
                ]
            else:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-i', bg_video_path,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-an',
                    '-shortest',
                    output_path
                ]

            bg_description = f"video background"

        elif bg_image_path:
            # Replace green screen with background image
            output_filename = f'videos/chroma_keyed/chromakey_{timestamp}.mp4'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            # Filter: overlay chroma-keyed foreground on background image (looped)
            filter_complex = (
                f"[0:v]chromakey=0x{hex_color}:similarity={similarity}:blend={blend}[fg];"
                f"[1:v]scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
                f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2,loop=-1:1:0[bg];"
                f"[bg][fg]overlay=0:0[out]"
            )

            # Check if video has audio
            audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                          '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
            audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in audio_result.stdout

            if has_audio:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', bg_image_path,
                    '-i', video_path,
                    '-filter_complex', (
                        f"[1:v]chromakey=0x{hex_color}:similarity={similarity}:blend={blend}[fg];"
                        f"[0:v]scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
                        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2[bg];"
                        f"[bg][fg]overlay=0:0[out]"
                    ),
                    '-map', '[out]',
                    '-map', '1:a?',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-t', str(video_duration),
                    output_path
                ]
            else:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-loop', '1',
                    '-i', bg_image_path,
                    '-i', video_path,
                    '-filter_complex', (
                        f"[1:v]chromakey=0x{hex_color}:similarity={similarity}:blend={blend}[fg];"
                        f"[0:v]scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,"
                        f"pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2[bg];"
                        f"[bg][fg]overlay=0:0[out]"
                    ),
                    '-map', '[out]',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-an',
                    '-t', str(video_duration),
                    output_path
                ]

            bg_description = f"image background"

        elif background_color:
            # Replace green screen with solid color
            output_filename = f'videos/chroma_keyed/chromakey_{timestamp}.mp4'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            # Normalize background color
            if background_color.startswith('#'):
                bg_hex = background_color[1:]
            elif background_color.lower() in color_map:
                bg_hex = color_map[background_color.lower()]
            else:
                bg_hex = background_color

            # Filter: replace chroma key with solid color
            filter_complex = (
                f"color=c=0x{bg_hex}:s={video_width}x{video_height}:d={video_duration}[bg];"
                f"[0:v]chromakey=0x{hex_color}:similarity={similarity}:blend={blend}[fg];"
                f"[bg][fg]overlay=0:0[out]"
            )

            # Check if video has audio
            audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                          '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
            audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in audio_result.stdout

            if has_audio:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-map', '0:a?',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    output_path
                ]
            else:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-filter_complex', filter_complex,
                    '-map', '[out]',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-an',
                    output_path
                ]

            bg_description = f"solid color (#{bg_hex})"

        else:
            # Output with transparent background (WebM format supports alpha)
            output_filename = f'videos/chroma_keyed/chromakey_{timestamp}.webm'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            # Filter: apply chroma key with alpha channel output
            chroma_filter = f"chromakey=0x{hex_color}:similarity={similarity}:blend={blend}"

            # Check if video has audio
            audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                          '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
            audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)
            has_audio = 'audio' in audio_result.stdout

            if has_audio:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', chroma_filter,
                    '-c:v', 'libvpx-vp9',
                    '-pix_fmt', 'yuva420p',
                    '-b:v', '2M',
                    '-c:a', 'libopus',
                    '-b:a', '128k',
                    output_path
                ]
            else:
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', chroma_filter,
                    '-c:v', 'libvpx-vp9',
                    '-pix_fmt', 'yuva420p',
                    '-b:v', '2M',
                    '-an',
                    output_path
                ]

            bg_description = "transparent (WebM alpha)"

        logger.info(f"🔧 [Session 165] FFmpeg command: {' '.join(ffmpeg_cmd)[:200]}...")

        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for complex operations
        )

        if result.returncode != 0:
            logger.error(f"❌ [Session 165] Chroma key failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'Chroma key failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output was created
        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Chroma keyed video was not created'}, status=500)

        output_size = os.path.getsize(output_path)
        logger.info(f"✅ [Session 165] Chroma keyed video created: {output_path} ({output_size} bytes)")

        # Get project from source video if not specified
        if not project and video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        _user = request.user if request.user.is_authenticated else None
        keyed_video = VideoHistory.objects.create(
            user=_user,
            prompt=f"Chroma key ({key_color}) applied to video {video.id}, background: {bg_description}",
            duration=video.duration,
            model_used='ffmpeg_chromakey',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(_user) if _user else None,
        )

        logger.info(f"✅ [Session 165] Chroma key applied: {video.id} → {keyed_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=keyed_video,
                project=project,
                contribution_type='editing',
                task_description=f"Applied chroma key ({key_color}) with {bg_description}",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(keyed_video.id),
            'video_url': keyed_video.video_url,
            'key_color': key_color,
            'hex_color': f'#{hex_color}',
            'similarity': similarity,
            'blend': blend,
            'background': bg_description,
            'message': f'Chroma key applied: removed {key_color}, {bg_description}',
            'agent': 'VideoEditingAgent',
            'operation': 'chroma_key',
            'operation_display': f'Removing {key_color} screen background'
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 165] Chroma key timed out")
        return JsonResponse({'success': False, 'error': 'Chroma key timed out - video may be too long or complex'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 165] Chroma key error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def export_for_platform(request):
    """
    Session 166: Export Presets - Optimize video for specific platforms.

    Automatically adjusts resolution, aspect ratio, bitrate, and codec
    for optimal playback on YouTube, TikTok, Instagram, Twitter, etc.

    Parameters:
        video_id: Video ID (UUID or hybrid number)
        platform: Target platform - 'youtube', 'youtube_shorts', 'tiktok',
                  'instagram_reels', 'instagram_feed', 'instagram_story',
                  'twitter', 'linkedin', 'facebook' (default: 'youtube')
        quality: Quality level - 'high', 'medium', 'low' (default: 'high')
        max_duration: Optional max duration in seconds (platform-specific limits)
        project_id: Optional project ID for scoping

    Returns:
        JSON with optimized video details

    Voice commands:
        "Export video 1 for YouTube"
        "Optimize video 2 for TikTok"
        "Export video 3 for Instagram Reels"
        "Make video 4 ready for Twitter"
    """
    import subprocess
    from django.utils import timezone as tz
    from django.core.exceptions import ValidationError
    from content.models import VideoHistory, CreativeProject

    logger.info("🎬 [Session 166] export_for_platform() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id = data.get('video_id') or request.POST.get('video_id')
        platform = data.get('platform', 'youtube').lower()
        quality = data.get('quality', 'high').lower()
        max_duration = data.get('max_duration')
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id is required'}, status=400)

        # Platform presets with optimal settings
        # Format: (width, height, video_bitrate, audio_bitrate, max_duration, description)
        platform_presets = {
            'youtube': {
                'width': 1920, 'height': 1080, 'video_bitrate': '8M',
                'audio_bitrate': '192k', 'max_duration': None, 'fps': 30,
                'description': 'YouTube HD (1080p)'
            },
            'youtube_4k': {
                'width': 3840, 'height': 2160, 'video_bitrate': '35M',
                'audio_bitrate': '256k', 'max_duration': None, 'fps': 30,
                'description': 'YouTube 4K'
            },
            'youtube_shorts': {
                'width': 1080, 'height': 1920, 'video_bitrate': '6M',
                'audio_bitrate': '128k', 'max_duration': 60, 'fps': 30,
                'description': 'YouTube Shorts (9:16 vertical)'
            },
            'tiktok': {
                'width': 1080, 'height': 1920, 'video_bitrate': '6M',
                'audio_bitrate': '128k', 'max_duration': 180, 'fps': 30,
                'description': 'TikTok (9:16 vertical)'
            },
            'instagram_reels': {
                'width': 1080, 'height': 1920, 'video_bitrate': '6M',
                'audio_bitrate': '128k', 'max_duration': 90, 'fps': 30,
                'description': 'Instagram Reels (9:16 vertical)'
            },
            'instagram_feed': {
                'width': 1080, 'height': 1080, 'video_bitrate': '5M',
                'audio_bitrate': '128k', 'max_duration': 60, 'fps': 30,
                'description': 'Instagram Feed (1:1 square)'
            },
            'instagram_story': {
                'width': 1080, 'height': 1920, 'video_bitrate': '5M',
                'audio_bitrate': '128k', 'max_duration': 15, 'fps': 30,
                'description': 'Instagram Story (9:16 vertical)'
            },
            'twitter': {
                'width': 1280, 'height': 720, 'video_bitrate': '5M',
                'audio_bitrate': '128k', 'max_duration': 140, 'fps': 30,
                'description': 'Twitter/X (720p)'
            },
            'linkedin': {
                'width': 1920, 'height': 1080, 'video_bitrate': '8M',
                'audio_bitrate': '192k', 'max_duration': 600, 'fps': 30,
                'description': 'LinkedIn (1080p)'
            },
            'facebook': {
                'width': 1280, 'height': 720, 'video_bitrate': '6M',
                'audio_bitrate': '128k', 'max_duration': 240, 'fps': 30,
                'description': 'Facebook (720p)'
            },
            'facebook_reels': {
                'width': 1080, 'height': 1920, 'video_bitrate': '6M',
                'audio_bitrate': '128k', 'max_duration': 90, 'fps': 30,
                'description': 'Facebook Reels (9:16 vertical)'
            }
        }

        # Validate platform
        if platform not in platform_presets:
            available = ', '.join(platform_presets.keys())
            return JsonResponse({
                'success': False,
                'error': f'Unknown platform: {platform}. Available: {available}'
            }, status=400)

        preset = platform_presets[platform]

        # Quality adjustments
        quality_multipliers = {
            'high': 1.0,
            'medium': 0.7,
            'low': 0.5
        }
        q_mult = quality_multipliers.get(quality, 1.0)

        # Adjust bitrate based on quality
        video_br_num = float(preset['video_bitrate'].replace('M', ''))
        adjusted_video_br = f"{video_br_num * q_mult:.1f}M"

        audio_br_num = int(preset['audio_bitrate'].replace('k', ''))
        adjusted_audio_br = f"{int(audio_br_num * q_mult)}k"

        logger.info(f"📊 [Session 166] Export preset: {platform} ({preset['description']}), quality={quality}")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Resolve video ID (hybrid ID support)
        video = None
        try:
            video = VideoHistory.objects.get(id=video_id)
        except (VideoHistory.DoesNotExist, ValueError, ValidationError):
            pass

        if not video and video_id:
            try:
                video_num = int(str(video_id).strip())
                if project:
                    videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                else:
                    videos = VideoHistory.objects.order_by('created_at')
                if 1 <= video_num <= videos.count():
                    video = videos[video_num - 1]
                    logger.info(f"🔢 [Session 166] Resolved video {video_num} → {video.id}")
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({'success': False, 'error': f'Video not found: {video_id}'}, status=404)

        # Get video file path
        if video.video_url:
            if video.video_url.startswith('/media/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
            else:
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url)
        else:
            return JsonResponse({'success': False, 'error': 'Video has no file path'}, status=400)

        if not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': f'Video file not found: {video_path}'}, status=404)

        logger.info(f"📁 [Session 166] Source video: {video_path}")

        # Get source video info
        probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                     '-show_entries', 'stream=width,height,duration',
                     '-of', 'csv=p=0', video_path]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)

        try:
            parts = probe_result.stdout.strip().split(',')
            src_width = int(parts[0])
            src_height = int(parts[1])
            src_duration = float(parts[2]) if len(parts) > 2 and parts[2] else 10.0
        except (ValueError, IndexError):
            src_width, src_height, src_duration = 1920, 1080, 10.0

        logger.info(f"📐 [Session 166] Source: {src_width}x{src_height}, duration: {src_duration}s")

        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'exported')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'videos/exported/{platform}_{timestamp}.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Determine duration limit
        final_duration = src_duration
        duration_limited = False
        effective_max = max_duration if max_duration else preset['max_duration']

        if effective_max and src_duration > effective_max:
            final_duration = effective_max
            duration_limited = True
            logger.info(f"⏱️ [Session 166] Duration limited: {src_duration}s → {final_duration}s")

        # Build scale filter for aspect ratio conversion
        target_w, target_h = preset['width'], preset['height']
        src_aspect = src_width / src_height
        target_aspect = target_w / target_h

        if abs(src_aspect - target_aspect) < 0.01:
            # Same aspect ratio - just scale
            scale_filter = f"scale={target_w}:{target_h}"
        elif src_aspect > target_aspect:
            # Source is wider - crop sides or letterbox
            scale_filter = f"scale={target_w}:-2,crop={target_w}:{target_h}"
        else:
            # Source is taller - crop top/bottom or pillarbox
            scale_filter = f"scale=-2:{target_h},crop={target_w}:{target_h}"

        # Check if video has audio
        audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                      '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
        audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)
        has_audio = 'audio' in audio_result.stdout

        # Build ffmpeg command
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', scale_filter,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-b:v', adjusted_video_br,
            '-maxrate', adjusted_video_br,
            '-bufsize', f"{float(adjusted_video_br.replace('M', '')) * 2}M",
            '-r', str(preset['fps']),
            '-pix_fmt', 'yuv420p',  # Maximum compatibility
        ]

        if has_audio:
            ffmpeg_cmd.extend([
                '-c:a', 'aac',
                '-b:a', adjusted_audio_br,
                '-ar', '44100'
            ])
        else:
            ffmpeg_cmd.append('-an')

        if duration_limited:
            ffmpeg_cmd.extend(['-t', str(final_duration)])

        ffmpeg_cmd.append(output_path)

        logger.info(f"🔧 [Session 166] FFmpeg command: {' '.join(ffmpeg_cmd)[:200]}...")

        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            logger.error(f"❌ [Session 166] Export failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'Export failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output
        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Exported video was not created'}, status=500)

        output_size = os.path.getsize(output_path)
        output_size_mb = output_size / (1024 * 1024)
        logger.info(f"✅ [Session 166] Exported video: {output_path} ({output_size_mb:.1f}MB)")

        # Get project from source video if not specified
        if not project and video.project:
            project = video.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        _user = request.user if request.user.is_authenticated else None
        exported_video = VideoHistory.objects.create(
            user=_user,
            prompt=f"Exported for {platform}: {preset['description']}",
            duration=final_duration,
            model_used=f'ffmpeg_export_{platform}',
            ratio=f"{target_w}:{target_h}",
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(_user) if _user else None,
        )

        logger.info(f"✅ [Session 166] Export complete: {video.id} → {exported_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=exported_video,
                project=project,
                contribution_type='export',
                task_description=f"Exported video for {platform} ({preset['description']})",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(exported_video.id),
            'video_url': exported_video.video_url,
            'platform': platform,
            'preset': preset['description'],
            'resolution': f"{target_w}x{target_h}",
            'video_bitrate': adjusted_video_br,
            'audio_bitrate': adjusted_audio_br if has_audio else 'none',
            'duration': final_duration,
            'duration_limited': duration_limited,
            'file_size_mb': round(output_size_mb, 1),
            'message': f"Video exported for {platform} ({preset['description']}, {output_size_mb:.1f}MB)",
            'agent': 'VideoEditingAgent',
            'operation': 'export_for_platform',
            'operation_display': f'Exporting for {platform}'
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 166] Export timed out")
        return JsonResponse({'success': False, 'error': 'Export timed out'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 166] Export error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def video_transition(request):
    """
    Session 166: Video Transitions - Add transition effects between two videos.

    Uses ffmpeg xfade filter to create smooth transitions like crossfade,
    wipe, slide, zoom, etc. between two video clips.

    Parameters:
        video_id_1: First video ID (plays first)
        video_id_2: Second video ID (plays after transition)
        transition: Transition type - 'fade', 'wipeleft', 'wiperight', 'wipeup',
                    'wipedown', 'slideleft', 'slideright', 'slideup', 'slidedown',
                    'circlecrop', 'rectcrop', 'distance', 'fadeblack', 'fadewhite',
                    'radial', 'smoothleft', 'smoothright', 'circleopen', 'circleclose',
                    'dissolve', 'pixelize', 'diagtl', 'diagtr', 'diagbl', 'diagbr'
                    (default: 'fade')
        duration: Transition duration in seconds (default: 1.0)
        project_id: Optional project ID for scoping

    Returns:
        JSON with combined video details

    Voice commands:
        "Add crossfade between video 1 and video 2"
        "Add wipe transition from video 3 to video 4"
        "Combine videos 1 and 2 with dissolve effect"
        "Add slide transition between video 5 and 6"
    """
    import subprocess
    from django.utils import timezone as tz
    from django.core.exceptions import ValidationError
    from content.models import VideoHistory, CreativeProject

    logger.info("🎬 [Session 166] video_transition() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id_1 = data.get('video_id_1') or request.POST.get('video_id_1')
        video_id_2 = data.get('video_id_2') or request.POST.get('video_id_2')
        transition = data.get('transition', 'fade').lower()
        duration = float(data.get('duration', 1.0))
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id_1 or not video_id_2:
            return JsonResponse({
                'success': False,
                'error': 'Both video_id_1 and video_id_2 are required'
            }, status=400)

        # Validate duration
        duration = max(0.1, min(5.0, duration))

        # Available transitions in ffmpeg xfade
        valid_transitions = [
            'fade', 'wipeleft', 'wiperight', 'wipeup', 'wipedown',
            'slideleft', 'slideright', 'slideup', 'slidedown',
            'circlecrop', 'rectcrop', 'distance', 'fadeblack', 'fadewhite',
            'radial', 'smoothleft', 'smoothright', 'smoothup', 'smoothdown',
            'circleopen', 'circleclose', 'vertopen', 'vertclose',
            'horzopen', 'horzclose', 'dissolve', 'pixelize',
            'diagtl', 'diagtr', 'diagbl', 'diagbr',
            'hlslice', 'hrslice', 'vuslice', 'vdslice',
            'hblur', 'fadegrays', 'squeezev', 'squeezeh', 'zoomin'
        ]

        if transition not in valid_transitions:
            transition = 'fade'

        logger.info(f"📊 [Session 166] Transition: {transition}, duration: {duration}s")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Helper function to resolve video
        def resolve_video(vid_id):
            video = None
            try:
                video = VideoHistory.objects.get(id=vid_id)
            except (VideoHistory.DoesNotExist, ValueError, ValidationError):
                pass

            if not video and vid_id:
                try:
                    video_num = int(str(vid_id).strip())
                    if project:
                        videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                    else:
                        videos = VideoHistory.objects.order_by('created_at')
                    if 1 <= video_num <= videos.count():
                        video = videos[video_num - 1]
                except (ValueError, TypeError):
                    pass
            return video

        video1 = resolve_video(video_id_1)
        video2 = resolve_video(video_id_2)

        if not video1:
            return JsonResponse({'success': False, 'error': f'First video not found: {video_id_1}'}, status=404)
        if not video2:
            return JsonResponse({'success': False, 'error': f'Second video not found: {video_id_2}'}, status=404)

        # Get video paths
        def get_video_path(video):
            if video.video_url:
                if video.video_url.startswith('/media/'):
                    return os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
                else:
                    return os.path.join(settings.MEDIA_ROOT, video.video_url)
            return None

        video_path_1 = get_video_path(video1)
        video_path_2 = get_video_path(video2)

        if not video_path_1 or not os.path.exists(video_path_1):
            return JsonResponse({'success': False, 'error': 'First video file not found'}, status=404)
        if not video_path_2 or not os.path.exists(video_path_2):
            return JsonResponse({'success': False, 'error': 'Second video file not found'}, status=404)

        logger.info(f"📁 [Session 166] Videos: {video_path_1} + {video_path_2}")

        # Get video durations
        def get_video_duration(path):
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', path]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
            try:
                return float(result.stdout.strip())
            except Exception:
                return 5.0

        dur1 = get_video_duration(video_path_1)
        dur2 = get_video_duration(video_path_2)

        logger.info(f"⏱️ [Session 166] Durations: {dur1}s + {dur2}s")

        # Calculate offset (where transition starts)
        offset = dur1 - duration

        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'transitions')
        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename
        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'videos/transitions/transition_{transition}_{timestamp}.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

        # Check if videos have audio
        def has_audio(path):
            probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                    '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', path]
            result = subprocess.run(probe, capture_output=True, text=True, timeout=30)
            return 'audio' in result.stdout

        audio1 = has_audio(video_path_1)
        audio2 = has_audio(video_path_2)

        # Build ffmpeg command with xfade filter
        if audio1 and audio2:
            # Both have audio - crossfade audio too
            filter_complex = (
                f"[0:v][1:v]xfade=transition={transition}:duration={duration}:offset={offset}[v];"
                f"[0:a][1:a]acrossfade=d={duration}[a]"
            )
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path_1,
                '-i', video_path_2,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]
        elif audio1 or audio2:
            # Only one has audio
            filter_complex = f"[0:v][1:v]xfade=transition={transition}:duration={duration}:offset={offset}[v]"
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path_1,
                '-i', video_path_2,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-an',
                output_path
            ]
        else:
            # No audio
            filter_complex = f"[0:v][1:v]xfade=transition={transition}:duration={duration}:offset={offset}[v]"
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-i', video_path_1,
                '-i', video_path_2,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-an',
                output_path
            ]

        logger.info(f"🔧 [Session 166] FFmpeg command: {' '.join(ffmpeg_cmd)[:200]}...")

        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            logger.error(f"❌ [Session 166] Transition failed: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'Transition failed: {result.stderr[:200]}'
            }, status=500)

        # Verify output
        if not os.path.exists(output_path):
            return JsonResponse({'success': False, 'error': 'Transition video was not created'}, status=500)

        output_size = os.path.getsize(output_path)
        final_duration = dur1 + dur2 - duration  # Overlap reduces total duration

        logger.info(f"✅ [Session 166] Transition video: {output_path} ({output_size} bytes)")

        # Get project from source video if not specified
        if not project:
            project = video1.project or video2.project

        # Create VideoHistory record
        from core.services.workspace_resolver import get_active_workspace
        _user = request.user if request.user.is_authenticated else None
        transition_video = VideoHistory.objects.create(
            user=_user,
            prompt=f"{transition} transition: video {video_id_1} → video {video_id_2}",
            duration=final_duration,
            model_used=f'ffmpeg_xfade_{transition}',
            ratio=video1.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=tz.now(),
            project=project,
            workspace=get_active_workspace(_user) if _user else None,
        )

        logger.info(f"✅ [Session 166] Transition complete: {video1.id} + {video2.id} → {transition_video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=transition_video,
                project=project,
                contribution_type='editing',
                task_description=f"Added {transition} transition between videos",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': str(transition_video.id),
            'video_url': transition_video.video_url,
            'transition': transition,
            'duration': duration,
            'final_duration': final_duration,
            'message': f'{transition} transition added between videos ({duration}s overlap)',
            'agent': 'VideoEditingAgent',
            'operation': 'video_transition',
            'operation_display': f'Adding {transition} transition'
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 166] Transition timed out")
        return JsonResponse({'success': False, 'error': 'Transition timed out'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 166] Transition error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def auto_caption(request):
    """
    Session 166: Auto-Captioning - Generate and burn subtitles using Whisper.

    Extracts audio from video, transcribes with OpenAI Whisper API,
    generates SRT subtitles, and burns them into the video.

    Parameters:
        video_id: Video ID (UUID or hybrid number)
        language: Language code for transcription (default: 'en')
        font_size: Subtitle font size in pixels (default: 24)
        font_color: Subtitle font color (default: 'white')
        bg_color: Background box color (default: 'black')
        bg_opacity: Background opacity 0.0-1.0 (default: 0.7)
        position: Subtitle position - 'bottom', 'top' (default: 'bottom')
        burn_in: Whether to burn subtitles into video (default: True)
        project_id: Optional project ID for scoping

    Returns:
        JSON with captioned video details and SRT file

    Voice commands:
        "Add captions to video 1"
        "Generate subtitles for video 2"
        "Auto-caption video 3"
        "Add subtitles to video 4"
    """
    import subprocess
    from django.utils import timezone as tz
    from django.core.exceptions import ValidationError
    from content.models import VideoHistory, CreativeProject
    from openai import OpenAI

    logger.info("🎬 [Session 166] auto_caption() called")

    try:
        # Parse request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        video_id = data.get('video_id') or request.POST.get('video_id')
        language = data.get('language', 'en')
        font_size = int(data.get('font_size', 24))
        font_color = data.get('font_color', 'white')
        bg_color = data.get('bg_color', 'black')
        bg_opacity = float(data.get('bg_opacity', 0.7))
        position = data.get('position', 'bottom')
        burn_in = data.get('burn_in', True)
        project_id = data.get('project_id') or request.POST.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id is required'}, status=400)

        # Validate parameters
        font_size = max(12, min(72, font_size))
        bg_opacity = max(0.0, min(1.0, bg_opacity))

        logger.info(f"📊 [Session 166] Auto-caption params: language={language}, font_size={font_size}")

        # Get project for scoping
        project = None
        if project_id:
            try:
                project = CreativeProject.objects.get(id=project_id)
            except (CreativeProject.DoesNotExist, ValueError):
                pass

        # Resolve video ID
        video = None
        try:
            video = VideoHistory.objects.get(id=video_id)
        except (VideoHistory.DoesNotExist, ValueError, ValidationError):
            pass

        if not video and video_id:
            try:
                video_num = int(str(video_id).strip())
                if project:
                    videos = VideoHistory.objects.filter(project=project).order_by('created_at')
                else:
                    videos = VideoHistory.objects.order_by('created_at')
                if 1 <= video_num <= videos.count():
                    video = videos[video_num - 1]
                    logger.info(f"🔢 [Session 166] Resolved video {video_num} → {video.id}")
            except (ValueError, TypeError):
                pass

        if not video:
            return JsonResponse({'success': False, 'error': f'Video not found: {video_id}'}, status=404)

        # Get video file path
        if video.video_url:
            if video.video_url.startswith('/media/'):
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url[7:])
            else:
                video_path = os.path.join(settings.MEDIA_ROOT, video.video_url)
        else:
            return JsonResponse({'success': False, 'error': 'Video has no file path'}, status=400)

        if not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': f'Video file not found: {video_path}'}, status=404)

        logger.info(f"📁 [Session 166] Source video: {video_path}")

        # Check if video has audio
        audio_probe = ['ffprobe', '-v', 'error', '-select_streams', 'a',
                      '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', video_path]
        audio_result = subprocess.run(audio_probe, capture_output=True, text=True, timeout=30)

        if 'audio' not in audio_result.stdout:
            return JsonResponse({
                'success': False,
                'error': 'Video has no audio track - cannot generate captions'
            }, status=400)

        # Create temp directory for audio extraction
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'captioned')
        os.makedirs(output_dir, exist_ok=True)

        timestamp = tz.now().strftime('%Y%m%d_%H%M%S')

        # Extract audio to temporary file
        audio_path = os.path.join(output_dir, f'audio_{timestamp}.mp3')

        extract_cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ar', '16000',  # 16kHz for Whisper
            '-ac', '1',  # Mono
            '-b:a', '64k',
            audio_path
        ]

        logger.info(f"🎵 [Session 166] Extracting audio...")
        extract_result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=300)

        if extract_result.returncode != 0:
            logger.error(f"❌ Audio extraction failed: {extract_result.stderr}")
            return JsonResponse({
                'success': False,
                'error': f'Audio extraction failed: {extract_result.stderr[:200]}'
            }, status=500)

        if not os.path.exists(audio_path):
            return JsonResponse({'success': False, 'error': 'Audio extraction failed'}, status=500)

        audio_size = os.path.getsize(audio_path) / (1024 * 1024)
        logger.info(f"✅ [Session 166] Audio extracted: {audio_size:.1f}MB")

        # Transcribe with Whisper
        logger.info(f"🎤 [Session 166] Transcribing with Whisper...")

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )

        # Generate SRT from segments
        def format_timestamp(seconds):
            """Convert seconds to SRT timestamp format HH:MM:SS,mmm"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        srt_content = []
        segments = getattr(transcript, 'segments', [])

        if not segments:
            # Fallback: create single segment from full text
            srt_content.append("1")
            srt_content.append("00:00:00,000 --> 00:00:10,000")
            srt_content.append(transcript.text)
            srt_content.append("")
        else:
            for i, segment in enumerate(segments, 1):
                start_time = format_timestamp(segment.get('start', 0))
                end_time = format_timestamp(segment.get('end', 0))
                text = segment.get('text', '').strip()

                srt_content.append(str(i))
                srt_content.append(f"{start_time} --> {end_time}")
                srt_content.append(text)
                srt_content.append("")

        srt_text = "\n".join(srt_content)
        subtitle_count = len(segments) if segments else 1

        logger.info(f"✅ [Session 166] Generated {subtitle_count} subtitle segments")

        # Save SRT file
        srt_filename = f'videos/captioned/subtitles_{timestamp}.srt'
        srt_path = os.path.join(settings.MEDIA_ROOT, srt_filename)

        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_text)

        logger.info(f"✅ [Session 166] SRT saved: {srt_path}")

        # Burn subtitles into video if requested
        if burn_in:
            output_filename = f'videos/captioned/captioned_{timestamp}.mp4'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

            # Build subtitle filter
            # Note: we need to escape special characters in the path
            srt_escaped = srt_path.replace(':', '\\:').replace("'", "\\'")

            # Position: bottom or top
            margin = 30
            if position == 'top':
                margin_v = f":MarginV={margin}"
            else:
                margin_v = f":MarginV={margin}"

            # Style options
            style_options = f"FontSize={font_size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=4"

            subtitle_filter = f"subtitles={srt_escaped}:force_style='{style_options}'"

            burn_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', subtitle_filter,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]

            logger.info(f"🔥 [Session 166] Burning subtitles into video...")
            burn_result = subprocess.run(burn_cmd, capture_output=True, text=True, timeout=600)

            if burn_result.returncode != 0:
                logger.error(f"❌ Subtitle burn failed: {burn_result.stderr}")
                # Try simpler approach without complex styling
                simple_filter = f"subtitles={srt_escaped}"
                burn_cmd_simple = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-vf', simple_filter,
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23',
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    output_path
                ]
                burn_result = subprocess.run(burn_cmd_simple, capture_output=True, text=True, timeout=600)

                if burn_result.returncode != 0:
                    logger.error(f"❌ Simple subtitle burn also failed: {burn_result.stderr}")
                    return JsonResponse({
                        'success': False,
                        'error': f'Subtitle burn failed: {burn_result.stderr[:200]}'
                    }, status=500)

            if not os.path.exists(output_path):
                return JsonResponse({'success': False, 'error': 'Captioned video was not created'}, status=500)

            output_size = os.path.getsize(output_path)
            logger.info(f"✅ [Session 166] Captioned video created: {output_path} ({output_size} bytes)")

            video_url = f'/media/{output_filename}'
        else:
            # Don't burn in - just return SRT
            video_url = video.video_url
            output_filename = None

        # Clean up temp audio file
        try:
            os.remove(audio_path)
        except Exception:
            pass

        # Get project from source video if not specified
        if not project and video.project:
            project = video.project

        # Create VideoHistory record if we burned subtitles
        if burn_in:
            from core.services.workspace_resolver import get_active_workspace
            _user = request.user if request.user.is_authenticated else None
            captioned_video = VideoHistory.objects.create(
                user=_user,
                prompt=f"Auto-captioned video with {subtitle_count} subtitles ({language})",
                duration=video.duration,
                model_used='ffmpeg_whisper_subtitles',
                ratio=video.ratio,
                status='completed',
                video_url=video_url,
                generation_completed=tz.now(),
                project=project,
                workspace=get_active_workspace(_user) if _user else None,
            )
            result_video_id = str(captioned_video.id)
        else:
            result_video_id = str(video.id)

        logger.info(f"✅ [Session 166] Auto-caption complete: {video.id}")

        # Track agent contribution
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentContribution
            agent = UnifiedAgentTemplate.objects.get(name='video-editing-agent')
            AgentContribution.objects.create(
                agent=agent,
                video=captioned_video if burn_in else video,
                project=project,
                contribution_type='captioning',
                task_description=f"Auto-captioned with {subtitle_count} subtitles ({language})",
                execution_time_seconds=0.0
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not track agent contribution: {e}")

        return JsonResponse({
            'success': True,
            'video_id': result_video_id,
            'video_url': video_url,
            'srt_url': f'/media/{srt_filename}',
            'subtitle_count': subtitle_count,
            'language': language,
            'transcript': transcript.text[:500] + '...' if len(transcript.text) > 500 else transcript.text,
            'burn_in': burn_in,
            'message': f'Generated {subtitle_count} captions and {"burned into video" if burn_in else "saved SRT file"}',
            'agent': 'VideoEditingAgent',
            'operation': 'auto_caption',
            'operation_display': 'Generating captions with Whisper'
        })

    except subprocess.TimeoutExpired:
        logger.error("❌ [Session 166] Auto-caption timed out")
        return JsonResponse({'success': False, 'error': 'Auto-caption timed out'}, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 166] Auto-caption error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION 175: LIP SYNC - Sync Labs Lipsync-2 via Replicate
# Make AI-generated characters TALK with natural mouth movements!
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def lip_sync(request):
    """
    Session 175: Generate video with lip-synced speech.

    Takes a video and audio file, returns a new video where the speaker's
    lips are synced to match the audio. Uses Sync Labs Lipsync-2 via Replicate.

    POST /api/video/lip-sync/

    Request body:
        - video_url OR video_id: Source video (must have a face visible)
        - audio_url OR audio_id: Audio to sync lips to
        - sync_mode: How to handle duration mismatch (default: "cut_off")
            - "cut_off": Cut video when audio ends
            - "loop": Loop video to match audio length
            - "bounce": Bounce video to match audio
        - temperature: Expression intensity 0-1 (default: 0.5)
        - active_speaker: Auto-detect active speaker (default: false)
        - project_id: Optional project association

    Returns:
        - prediction_id: ID for polling status
        - estimated_time: Estimated processing time

    Cost: ~$0.05 per second of output video
    """
    logger.info("🎬 [Session 175] Lip sync request received")

    try:
        # Parse request
        data = json.loads(request.body) if request.body else {}

        # Get video input
        video_url = data.get('video_url')
        video_id = data.get('video_id')

        # Get audio input
        audio_url = data.get('audio_url')
        audio_id = data.get('audio_id')

        # Options
        sync_mode = data.get('sync_mode', 'cut_off')
        temperature = float(data.get('temperature', 0.5))
        active_speaker = data.get('active_speaker', False)
        lipsync_model = data.get('lipsync_model', 'auto')  # Session 177: Model selection
        project_id = data.get('project_id')

        # Resolve video URL from video_id if needed
        if not video_url and video_id:
            from content.models import VideoHistory
            try:
                video = VideoHistory.objects.get(id=video_id)
                if video.video_url:
                    video_url = video.video_url
                elif video.video_file:
                    # Need a public URL - construct from request
                    video_url = request.build_absolute_uri(video.video_file.url)
            except VideoHistory.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Video {video_id} not found'
                }, status=404)

        # Resolve audio URL from audio_id if needed (if we add audio history)
        # For now, audio_url is required
        if not audio_url and audio_id:
            # NOTE: audio_id lookup pending AudioHistory model implementation
            return JsonResponse({
                'success': False,
                'error': 'audio_id lookup not yet supported, use audio_url'
            }, status=400)

        if not video_url:
            return JsonResponse({
                'success': False,
                'error': 'video_url or video_id is required'
            }, status=400)

        if not audio_url:
            return JsonResponse({
                'success': False,
                'error': 'audio_url is required - provide URL to audio file'
            }, status=400)

        logger.info(f"   Video: {video_url[:60]}...")
        logger.info(f"   Audio: {audio_url[:60]}...")
        logger.info(f"   Mode: {sync_mode}, Temp: {temperature}")
        logger.info(f"   Lip Sync Model: {lipsync_model}")  # Session 177

        # Call Replicate provider
        from content.replicate_provider import get_replicate_provider

        provider = get_replicate_provider()

        # Session 177: Select model based on lipsync_model parameter
        if lipsync_model == 'latentsync' or lipsync_model == 'auto':
            # Use ByteDance LatentSync (cartoon-optimized)
            logger.info("🎨 Using ByteDance LatentSync (cartoon-optimized)")
            result = provider.lip_sync_latent(
                video_url=video_url,
                audio_url=audio_url,
            )
        else:
            # Use Sync Labs Lipsync-2 (photorealistic)
            logger.info("👤 Using Sync Labs Lipsync-2 (photorealistic)")
            result = provider.lip_sync(
                video_url=video_url,
                audio_url=audio_url,
                sync_mode=sync_mode,
                temperature=temperature,
                active_speaker=active_speaker
            )

        if not result.success:
            return JsonResponse({
                'success': False,
                'error': result.error_message
            }, status=500)

        # Store prediction info for polling
        # We'll create the VideoHistory entry when the prediction completes
        response_data = {
            'success': True,
            'prediction_id': result.prediction_id,
            'status': result.status,
            'estimated_time': result.estimated_time,
            'message': 'Lip sync started! Use the prediction_id to check status.',
            'poll_endpoint': f'/api/video/lip-sync/status/{result.prediction_id}/',
            'agent': 'LipSyncAgent',
            'operation': 'lip_sync',
            'operation_display': 'Syncing lip movements to audio'
        }

        if project_id:
            response_data['project_id'] = project_id

        logger.info(f"✅ [Session 175] Lip sync started: {result.prediction_id}")
        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ [Session 175] Lip sync error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def lip_sync_status(request, prediction_id):
    """
    Session 175: Check lip sync prediction status.

    GET /api/video/lip-sync/status/<prediction_id>/

    Returns:
        - status: starting, processing, succeeded, failed
        - progress: 0-100
        - video_url: URL of synced video (when complete)
        - error: Error message (if failed)
    """
    logger.info(f"🎬 [Session 175] Checking lip sync status: {prediction_id}")

    try:
        from content.replicate_provider import get_replicate_provider

        provider = get_replicate_provider()
        result = provider.check_lip_sync_status(prediction_id)

        if not result.get('success'):
            return JsonResponse({
                'success': False,
                'error': result.get('error_message', 'Unknown error')
            }, status=500)

        response = {
            'success': True,
            'prediction_id': prediction_id,
            'status': result.get('status'),
            'progress': result.get('progress', 0),
            'progress_message': result.get('progress_message', '')
        }

        # If complete, include video URL and save to gallery
        if result.get('status') == 'succeeded' and result.get('video_url'):
            response['video_url'] = result['video_url']
            response['message'] = 'Lip sync complete! Video is ready.'

            # Session 176: Save lip-synced video to VideoHistory
            # Check if we already saved this prediction to avoid duplicates
            from content.models import VideoHistory, CreativeProject
            existing = VideoHistory.objects.filter(
                parameters__prediction_id=prediction_id
            ).first()

            if not existing:
                try:
                    # Download video from Replicate
                    import requests
                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage
                    import uuid

                    logger.info(f"📥 Downloading lip-synced video from Replicate...")
                    video_response = requests.get(result['video_url'], timeout=120, stream=True)
                    video_response.raise_for_status()

                    # Read video content
                    video_content = b''
                    for chunk in video_response.iter_content(chunk_size=8192):
                        if chunk:
                            video_content += chunk

                    logger.info(f"✅ Downloaded {len(video_content)} bytes")

                    # Save to local storage
                    video_id = str(uuid.uuid4())
                    filename = f"talking_character_{video_id}.mp4"
                    filepath = f"videos/{request.user.id}/lip_synced_{filename}"

                    saved_path = default_storage.save(filepath, ContentFile(video_content))
                    local_video_url = default_storage.url(saved_path)

                    logger.info(f"✅ Saved locally: {local_video_url}")

                    # Session 177: Determine which model was used
                    # Get the original video to check parameters
                    original_video = VideoHistory.objects.filter(
                        video_id=prediction_id.split('_')[0] if '_' in prediction_id else prediction_id
                    ).first()

                    lipsync_model_used = 'bytedance_latentsync'  # Default to new model
                    if original_video and original_video.parameters:
                        lipsync_model_used = original_video.parameters.get('lipsync_model', 'latentsync')
                        if lipsync_model_used == 'sync_labs':
                            lipsync_model_used = 'sync_labs_lipsync2'
                        elif lipsync_model_used in ['auto', 'latentsync']:
                            lipsync_model_used = 'bytedance_latentsync'

                    # Create VideoHistory record
                    from core.services.workspace_resolver import get_active_workspace
                    video_history = VideoHistory.objects.create(
                        user=request.user,
                        video_id=video_id,
                        video_url=local_video_url,
                        prompt="Talking character with lip sync",
                        model_used=lipsync_model_used,
                        video_type='lip_synced_talking_character',
                        status='completed',
                        workspace=get_active_workspace(request.user),
                        parameters={
                            'prediction_id': prediction_id,
                            'original_video_url': result['video_url'],
                            'lipsync_model': lipsync_model_used,
                            'pipeline_stage': 'lip_sync_complete'
                        }
                    )

                    # Associate with project if we can find it from the request
                    # The frontend should have passed project_id, but if not we skip
                    project_id = request.GET.get('project_id') or request.POST.get('project_id')
                    logger.info(f"🔍 Looking for project_id in request: GET={request.GET.get('project_id')}, POST={request.POST.get('project_id')}")

                    if project_id:
                        try:
                            project = CreativeProject.objects.get(id=project_id)
                            video_history.project = project
                            video_history.save()
                            logger.info(f"✅ Associated lip-synced video with project: {project_id}")
                        except CreativeProject.DoesNotExist:
                            logger.warning(f"⚠️ Project {project_id} not found")
                    else:
                        logger.warning(f"⚠️ No project_id found in request - video will be orphaned!")

                    response['video_history_id'] = str(video_history.id)
                    logger.info(f"✅ Saved lip-synced video to gallery: {video_history.id}")

                except Exception as e:
                    logger.error(f"⚠️ Failed to save lip-synced video: {e}")
                    # Don't fail the request - video URL is still valid

        elif result.get('status') == 'failed':
            response['error'] = result.get('error', 'Lip sync failed')

        return JsonResponse(response)

    except Exception as e:
        logger.error(f"❌ [Session 175] Lip sync status error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION 175: TALKING CHARACTER PIPELINE - Complete Image → Video → Lip Sync!
# One-step talking character video generation! 🎨→🎬→👄✨
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def talking_character(request):
    """
    Session 175: Generate a complete talking character video from image + text.

    This is the end-to-end pipeline that combines:
    1. Text-to-Speech (ElevenLabs) - Generate audio from script
    2. Image-to-Video (Runway) - Animate the character image
    3. Lip Sync (Sync Labs) - Sync mouth movements to audio

    POST /api/video/talking-character/

    Request body:
        - image_url OR image_id: Character image to animate
        - text: Script text for character to speak
        - voice: ElevenLabs voice name (default: "Rachel")
        - motion_prompt: Description of motion (default: "subtle talking motion")
        - duration: Target video duration in seconds (5 or 10)
        - sync_mode: Lip sync mode (cut_off, loop, bounce)
        - temperature: Expression intensity 0-1 (default: 0.5)
        - project_id: Optional project association
        - sync: Wait for completion (default: false)

    Returns:
        Async mode (sync=false):
            - audio_url: Generated speech audio
            - video_task_id: Runway task ID for video generation
            - status: Current pipeline status

        Sync mode (sync=true):
            - final_video_url: Complete talking character video
            - All intermediate URLs (audio, base_video)

    Cost per 10-second video: ~$0.60-1.00
        - TTS: ~$0.05
        - Image-to-Video: ~$0.15 (10 Runway credits)
        - Lip Sync: ~$0.50 (10 seconds × $0.05)
    """
    logger.info("🎬 [Session 175] Talking character request received")

    try:
        # Parse request
        data = json.loads(request.body) if request.body else {}

        # Get image input
        image_url = data.get('image_url')
        image_id = data.get('image_id')

        # Get script and voice
        text = data.get('text')
        voice = data.get('voice', 'Rachel')

        # Video options
        motion_prompt = data.get('motion_prompt', 'subtle talking motion, slight head movements')
        duration = int(data.get('duration', 5))

        # Lip sync options
        sync_mode = data.get('sync_mode', 'cut_off')
        temperature = float(data.get('temperature', 0.5))

        # Project and mode
        project_id = data.get('project_id')
        sync = data.get('sync', False)  # Wait for completion?

        # Resolve image URL from image_id if needed
        if not image_url and image_id:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            if user:
                from content.models import ImageHistory
                try:
                    # Support hybrid ID (numeric or UUID)
                    if str(image_id).isdigit():
                        # Numeric ID - get nth image
                        images = ImageHistory.objects.filter(user=user).order_by('created_at')
                        numeric_id = int(image_id)
                        if numeric_id > 0 and numeric_id <= images.count():
                            image = images[numeric_id - 1]
                        else:
                            return JsonResponse({
                                'success': False,
                                'error': f'Image {image_id} not found (you have {images.count()} images)'
                            }, status=404)
                    else:
                        # UUID
                        image = ImageHistory.objects.get(id=image_id, user=user)

                    # Get public URL
                    if image.image_url:
                        image_url = image.image_url
                    elif image.image_file:
                        image_url = request.build_absolute_uri(image.image_file.url)
                except ImageHistory.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': f'Image {image_id} not found'
                    }, status=404)

        # Validate inputs
        if not image_url:
            return JsonResponse({
                'success': False,
                'error': 'image_url or image_id is required'
            }, status=400)

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'text is required - provide script for character to speak'
            }, status=400)

        if duration not in [5, 10]:
            return JsonResponse({
                'success': False,
                'error': 'duration must be 5 or 10 seconds'
            }, status=400)

        logger.info(f"   Image: {image_url[:60]}...")
        logger.info(f"   Text: {text[:50]}...")
        logger.info(f"   Voice: {voice}, Duration: {duration}s")
        logger.info(f"   Mode: {'SYNC (wait for completion)' if sync else 'ASYNC (return task IDs)'}")

        # Create pipeline instance
        from content.talking_character_pipeline import get_talking_character_pipeline

        pipeline = get_talking_character_pipeline(user=request.user if hasattr(request, 'user') else None)

        # Show cost estimate
        cost_estimate = pipeline.estimate_cost(text, duration)
        logger.info(f"   💰 Estimated cost: ${cost_estimate['total_cost']:.3f}")

        # Execute pipeline
        if sync:
            # Synchronous mode - wait for completion
            result = pipeline.generate_talking_video_sync(
                image_url=image_url,
                text=text,
                voice=voice,
                motion_prompt=motion_prompt,
                duration=duration,
                sync_mode=sync_mode,
                temperature=temperature,
                project_id=project_id,
                timeout=300
            )
        else:
            # Asynchronous mode - return task IDs
            result = pipeline.generate_talking_video_async(
                image_url=image_url,
                text=text,
                voice=voice,
                motion_prompt=motion_prompt,
                duration=duration,
                sync_mode=sync_mode,
                temperature=temperature,
                project_id=project_id
            )

        # Convert PipelineResult to JSON response
        response_data = {
            'success': result.success,
            'status': result.status.value,
            'current_stage': result.current_stage,
            'progress_percent': result.progress_percent,
            'progress_message': result.progress_message,
            'estimated_cost': result.estimated_cost,
            'agent': 'TalkingCharacterAgent',
            'operation': 'talking_character',
            'operation_display': 'Creating talking character video'
        }

        # Add task IDs for polling
        if result.tts_task_id:
            response_data['tts_task_id'] = result.tts_task_id
        if result.video_task_id:
            response_data['video_task_id'] = result.video_task_id
            response_data['video_poll_endpoint'] = f'/api/video/status/{result.video_task_id}/'
        if result.lipsync_task_id:
            response_data['lipsync_task_id'] = result.lipsync_task_id
            response_data['lipsync_poll_endpoint'] = f'/api/video/lip-sync/status/{result.lipsync_task_id}/'

        # Add URLs when available
        if result.audio_url:
            response_data['audio_url'] = result.audio_url
        if result.base_video_url:
            response_data['base_video_url'] = result.base_video_url
        if result.final_video_url:
            response_data['final_video_url'] = result.final_video_url

        # Add error info if failed
        if not result.success:
            response_data['error'] = result.error_message
            response_data['failed_stage'] = result.failed_stage

        if project_id:
            response_data['project_id'] = project_id

        status_code = 200 if result.success else 500

        logger.info(f"✅ [Session 175] Talking character pipeline: {result.status.value}")
        return JsonResponse(response_data, status=status_code)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"❌ [Session 175] Talking character error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# SESSION 167: DaVinci Resolve Studio Integration - Making the $295 COUNT!
# One person + AI Assistant + AI Agents = UNSTOPPABLE! 🚀
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def davinci_status(request):
    """
    Session 167: Get DaVinci Resolve status and hybrid processor info.

    Returns whether DaVinci Resolve Studio is:
    - Installed
    - Running
    - Available for GPU-accelerated rendering
    - What professional codecs are available
    """
    logger.info("🎬 [Session 167] DaVinci status check")

    try:
        from content.hybrid_video_processor import get_hybrid_processor

        processor = get_hybrid_processor()
        status = processor.get_status()

        return JsonResponse({
            'success': True,
            **status
        })

    except Exception as e:
        logger.error(f"❌ [Session 167] Status check error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'davinci_installed': False,
            'davinci_running': False,
            'active_processor': 'ffmpeg'
        })


@csrf_exempt
@require_http_methods(["POST"])
def render_professional(request):
    """
    Session 167: Professional video rendering with DaVinci Resolve or ffmpeg fallback.

    When DaVinci is running:
    - GPU-accelerated rendering (5-10x faster)
    - True ProRes, DNxHD encoding
    - Industry-leading quality

    When DaVinci not available:
    - FFmpeg fallback with best-effort encoding
    - Still produces professional-quality output

    Codecs available:
    - prores_422: Apple ProRes 422 (~150 Mbps)
    - prores_422_hq: Apple ProRes 422 HQ (~220 Mbps)
    - prores_4444: Apple ProRes 4444 (with alpha)
    - dnxhd: Avid DNxHD
    - dnxhr_hq: Avid DNxHR HQ
    - h264: Standard H.264
    - h265: HEVC/H.265
    """
    logger.info("🎬 [Session 167] Professional render requested")

    try:
        data = json.loads(request.body) if request.body else {}

        video_id = data.get('video_id')
        codec = data.get('codec', 'prores_422_hq')
        resolution = data.get('resolution', '1920x1080')
        frame_rate = data.get('frame_rate', 30)
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Resolve video
        video = _resolve_video_by_id(video_id, request.user, project_id)
        if not video:
            return JsonResponse({'success': False, 'error': f'Video {video_id} not found'}, status=404)

        # Get video path
        video_path = _get_video_local_path(video)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': 'Video file not found'}, status=404)

        # Import hybrid processor
        from content.hybrid_video_processor import get_hybrid_processor, ProfessionalCodec

        processor = get_hybrid_processor()

        # Map codec string to enum
        codec_map = {
            'prores_422': ProfessionalCodec.PRORES_422,
            'prores_422_hq': ProfessionalCodec.PRORES_422_HQ,
            'prores_4444': ProfessionalCodec.PRORES_4444,
            'dnxhd': ProfessionalCodec.DNXHD,
            'dnxhr_hq': ProfessionalCodec.DNXHR_HQ,
            'h264': ProfessionalCodec.H264,
            'h265': ProfessionalCodec.H265,
        }

        codec_enum = codec_map.get(codec, ProfessionalCodec.PRORES_422_HQ)

        # Determine output extension
        ext_map = {
            'prores_422': 'mov',
            'prores_422_hq': 'mov',
            'prores_4444': 'mov',
            'dnxhd': 'mxf',
            'dnxhr_hq': 'mxf',
            'h264': 'mp4',
            'h265': 'mp4',
        }
        ext = ext_map.get(codec, 'mov')

        # Generate output path
        timestamp = int(time.time())
        output_filename = f"pro_render_{video.id}_{codec}_{timestamp}.{ext}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Render!
        result = processor.render_professional(
            video_path=video_path,
            output_path=output_path,
            codec=codec_enum,
            resolution=resolution,
            frame_rate=frame_rate
        )

        if result.success:
            # Create VideoHistory record
            from core.services.workspace_resolver import get_active_workspace
            new_video = VideoHistory.objects.create(
                user=request.user,
                prompt=f"Professional render ({codec}) of video {video.id}",
                video_url=f'/media/videos/{output_filename}',
                status='completed',
                project=video.project if hasattr(video, 'project') else None,
                workspace=get_active_workspace(request.user),
            )

            return JsonResponse({
                'success': True,
                'video_id': str(new_video.id),
                'video_url': new_video.video_url,
                'processor_used': result.processor_used,
                'gpu_accelerated': result.gpu_accelerated,
                'codec': result.codec_used or codec,
                'resolution': resolution,
                'message': f'Professional render complete using {result.processor_used.upper()}' +
                          (' (GPU accelerated!)' if result.gpu_accelerated else ''),
                'agent': 'VideoEditingAgent',
                'operation': 'render_professional',
                'operation_display': f'Professional {codec} render'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error_message or 'Render failed',
                'processor_used': result.processor_used
            }, status=500)

    except Exception as e:
        logger.error(f"❌ [Session 167] Professional render error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def apply_lut(request):
    """
    Session 167: Apply LUT (Look-Up Table) to video.

    DaVinci Resolve has industry-leading color science for LUT application.
    Falls back to ffmpeg lut3d filter when DaVinci isn't available.

    Supports:
    - .cube files (most common)
    - .3dl files
    - Custom LUTs uploaded to the platform

    Built-in LUTs:
    - cinematic_orange_teal: Popular film look
    - vintage_film: 70s/80s film emulation
    - bleach_bypass: Desaturated high-contrast
    - day_for_night: Convert day footage to night
    """
    logger.info("🎨 [Session 167] LUT application requested")

    try:
        data = json.loads(request.body) if request.body else {}

        video_id = data.get('video_id')
        lut_name = data.get('lut_name', 'cinematic_orange_teal')
        lut_path = data.get('lut_path')  # Custom LUT path
        intensity = float(data.get('intensity', 1.0))
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        # Resolve video
        video = _resolve_video_by_id(video_id, request.user, project_id)
        if not video:
            return JsonResponse({'success': False, 'error': f'Video {video_id} not found'}, status=404)

        video_path = _get_video_local_path(video)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': 'Video file not found'}, status=404)

        # Built-in LUT paths (you'd place these in a luts/ directory)
        builtin_luts = {
            'cinematic_orange_teal': os.path.join(settings.BASE_DIR, 'luts', 'cinematic_orange_teal.cube'),
            'vintage_film': os.path.join(settings.BASE_DIR, 'luts', 'vintage_film.cube'),
            'bleach_bypass': os.path.join(settings.BASE_DIR, 'luts', 'bleach_bypass.cube'),
            'day_for_night': os.path.join(settings.BASE_DIR, 'luts', 'day_for_night.cube'),
        }

        # Get LUT path
        if lut_path:
            actual_lut_path = lut_path
        elif lut_name in builtin_luts:
            actual_lut_path = builtin_luts[lut_name]
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown LUT: {lut_name}. Available: {list(builtin_luts.keys())}'
            }, status=400)

        # Check if LUT file exists
        if not os.path.exists(actual_lut_path):
            # Create a simple fallback - use ffmpeg color grading instead
            logger.warning(f"⚠️ LUT file not found: {actual_lut_path}, using color grade fallback")
            # Fall back to color grading
            return _apply_color_grade_fallback(request, video, video_path, lut_name, project_id)

        # Generate output path
        timestamp = int(time.time())
        output_filename = f"lut_{video.id}_{lut_name}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Apply LUT
        from content.hybrid_video_processor import get_hybrid_processor

        processor = get_hybrid_processor()
        result = processor.apply_lut(
            video_path=video_path,
            lut_path=actual_lut_path,
            output_path=output_path,
            intensity=intensity
        )

        if result.success:
            from core.services.workspace_resolver import get_active_workspace
            new_video = VideoHistory.objects.create(
                user=request.user,
                prompt=f"Applied {lut_name} LUT to video {video.id}",
                video_url=f'/media/videos/{output_filename}',
                status='completed',
                project=video.project if hasattr(video, 'project') else None,
                workspace=get_active_workspace(request.user),
            )

            return JsonResponse({
                'success': True,
                'video_id': str(new_video.id),
                'video_url': new_video.video_url,
                'lut_applied': lut_name,
                'processor_used': result.processor_used,
                'gpu_accelerated': result.gpu_accelerated,
                'message': f'Applied {lut_name} LUT using {result.processor_used.upper()}',
                'agent': 'VideoEditingAgent',
                'operation': 'apply_lut',
                'operation_display': f'Applying {lut_name} LUT'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error_message or 'LUT application failed'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ [Session 167] LUT error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _apply_color_grade_fallback(request, video, video_path, style, project_id):
    """Fallback when LUT file doesn't exist - use ffmpeg color grading"""
    logger.info(f"🎨 Using color grade fallback for {style}")

    # Map LUT names to ffmpeg color grades
    grade_map = {
        'cinematic_orange_teal': 'colorbalance=rs=0.15:gs=-0.05:bs=-0.15:rm=0.1:bm=-0.1',
        'vintage_film': 'curves=preset=vintage,eq=saturation=0.8',
        'bleach_bypass': 'eq=saturation=0.5:contrast=1.3',
        'day_for_night': 'colorbalance=rs=-0.2:gs=-0.2:bs=0.3,eq=brightness=-0.2',
    }

    filter_chain = grade_map.get(style, 'eq=saturation=1.0')

    timestamp = int(time.time())
    output_filename = f"grade_{video.id}_{style}_{timestamp}.mp4"
    output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-vf', filter_chain,
        '-c:v', 'libx264', '-crf', '18',
        '-c:a', 'copy',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 0:
        from core.services.workspace_resolver import get_active_workspace
        new_video = VideoHistory.objects.create(
            user=request.user,
            prompt=f"Applied {style} grade to video {video.id}",
            video_url=f'/media/videos/{output_filename}',
            status='completed',
            project=video.project if hasattr(video, 'project') else None,
            workspace=get_active_workspace(request.user),
        )

        return JsonResponse({
            'success': True,
            'video_id': str(new_video.id),
            'video_url': new_video.video_url,
            'grade_applied': style,
            'processor_used': 'ffmpeg',
            'message': f'Applied {style} color grade (LUT fallback)',
            'agent': 'VideoEditingAgent',
            'operation': 'apply_lut',
            'operation_display': f'Applying {style} grade'
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Color grade fallback failed'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def color_grade_professional(request):
    """
    Session 167: Professional color grading using DaVinci's color science.

    DaVinci Resolve is THE industry standard for color grading!

    When DaVinci is running:
    - Full color wheel access (Lift, Gamma, Gain)
    - Node-based color pipeline
    - Film emulation

    Presets:
    - cinematic: Film-like contrast and color
    - warm: Golden hour warmth
    - cool: Blue-tinted coolness
    - vintage: Retro film look
    - vibrant: Punchy saturated colors
    - noir: Black and white with contrast
    - custom: Use lift/gamma/gain parameters
    """
    logger.info("🎨 [Session 167] Professional color grading requested")

    try:
        data = json.loads(request.body) if request.body else {}

        video_id = data.get('video_id')
        grade_type = data.get('grade_type', 'cinematic')
        saturation = float(data.get('saturation', 1.0))
        contrast = float(data.get('contrast', 1.0))
        project_id = data.get('project_id')

        # Advanced parameters (DaVinci only)
        lift = data.get('lift')  # [R, G, B] for shadows
        gamma = data.get('gamma')  # [R, G, B] for midtones
        gain = data.get('gain')  # [R, G, B] for highlights

        if not video_id:
            return JsonResponse({'success': False, 'error': 'video_id required'}, status=400)

        video = _resolve_video_by_id(video_id, request.user, project_id)
        if not video:
            return JsonResponse({'success': False, 'error': f'Video {video_id} not found'}, status=404)

        video_path = _get_video_local_path(video)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': 'Video file not found'}, status=404)

        # Generate output path
        timestamp = int(time.time())
        output_filename = f"grade_{video.id}_{grade_type}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        from content.hybrid_video_processor import get_hybrid_processor

        processor = get_hybrid_processor()
        result = processor.color_grade_professional(
            video_path=video_path,
            output_path=output_path,
            grade_type=grade_type,
            lift=tuple(lift) if lift else None,
            gamma=tuple(gamma) if gamma else None,
            gain=tuple(gain) if gain else None,
            saturation=saturation,
            contrast=contrast
        )

        if result.success:
            from core.services.workspace_resolver import get_active_workspace
            new_video = VideoHistory.objects.create(
                user=request.user,
                prompt=f"Professional {grade_type} grade on video {video.id}",
                video_url=f'/media/videos/{output_filename}',
                status='completed',
                project=video.project if hasattr(video, 'project') else None,
                workspace=get_active_workspace(request.user),
            )

            return JsonResponse({
                'success': True,
                'video_id': str(new_video.id),
                'video_url': new_video.video_url,
                'grade_type': grade_type,
                'processor_used': result.processor_used,
                'gpu_accelerated': result.gpu_accelerated,
                'message': f'Professional {grade_type} grade complete using {result.processor_used.upper()}' +
                          (' (GPU accelerated!)' if result.gpu_accelerated else ''),
                'agent': 'VideoEditingAgent',
                'operation': 'color_grade_professional',
                'operation_display': f'Professional {grade_type} grading'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result.error_message or 'Grading failed'
            }, status=500)

    except Exception as e:
        logger.error(f"❌ [Session 167] Color grade error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 171: ElevenLabs Audio Integration
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def generate_voice_view(request):
    """
    Generate standalone audio from text using ElevenLabs.

    Session 171: Completes the ElevenLabs integration that was missing from Session 82.

    Expected JSON body:
        - text: str - Text to convert to speech
        - voice: str - Voice preset (Rachel, Drew, Clyde, Paul, Aria, etc.)
        - project_id: str (optional) - Project to associate audio with

    Returns:
        - success: bool
        - audio_url: str - URL to generated audio file
        - task_id: str - Unique ID for the audio
    """
    try:
        data = json.loads(request.body) if request.body else {}

        text = data.get('text')
        voice = data.get('voice', 'Rachel')
        project_id = data.get('project_id')

        if not text:
            return JsonResponse({
                'success': False,
                'error_message': 'text is required'
            }, status=400)

        logger.info(f"🎤 [Session 171] Generating voice with ElevenLabs...")
        logger.info(f"   Voice: {voice}")
        logger.info(f"   Text: {text[:60]}...")

        # Call ElevenLabs provider
        from content.elevenlabs_provider import elevenlabs_provider

        result = elevenlabs_provider.text_to_speech(
            text=text,
            voice=voice
        )

        if result.get('success'):
            logger.info(f"✅ [Session 171] Voice generated successfully!")
            logger.info(f"   Audio URL: {result.get('audio_url')}")

            return JsonResponse({
                'success': True,
                'audio_url': result.get('audio_url'),
                'task_id': result.get('task_id'),
                'voice': voice,
                'agent': 'AudioGenerationAgent',
                'operation': 'generate_voice',
                'operation_display': f'Voice generation ({voice})'
            })
        else:
            return JsonResponse({
                'success': False,
                'error_message': result.get('error_message', 'Voice generation failed')
            }, status=500)

    except Exception as e:
        logger.error(f"❌ [Session 171] Generate voice error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error_message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_voiceover_view(request):
    """
    Add voiceover to an existing video using ElevenLabs + ffmpeg.

    Session 171: Generates voice audio and mixes it with video.

    Expected JSON body:
        - video_id: str - Video to add voiceover to
        - text: str - Text for voiceover narration
        - voice: str - Voice preset (Rachel, Drew, Clyde, Paul, Aria, etc.)
        - volume: float (optional) - Voiceover volume 0.0-1.0 (default 0.8)
        - project_id: str (optional) - Project to associate result with

    Returns:
        - success: bool
        - video_url: str - URL to new video with voiceover
        - video_id: str - ID of new video
    """
    try:
        data = json.loads(request.body) if request.body else {}

        video_id = data.get('video_id')
        text = data.get('text')
        voice = data.get('voice', 'Rachel')
        volume = float(data.get('volume', 0.8))
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({
                'success': False,
                'error_message': 'video_id is required'
            }, status=400)

        if not text:
            return JsonResponse({
                'success': False,
                'error_message': 'text is required'
            }, status=400)

        logger.info(f"🎤 [Session 171] Adding voiceover to video {video_id}...")
        logger.info(f"   Voice: {voice}")
        logger.info(f"   Volume: {volume}")
        logger.info(f"   Text: {text[:60]}...")

        # Get the video
        video = _resolve_video_by_id(video_id, request.user, project_id)
        if not video:
            return JsonResponse({
                'success': False,
                'error_message': f'Video {video_id} not found'
            }, status=404)

        video_path = _get_video_local_path(video)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({
                'success': False,
                'error_message': 'Video file not found on disk'
            }, status=404)

        # Step 1: Generate voice audio
        logger.info(f"   Step 1: Generating voice audio...")
        from content.elevenlabs_provider import elevenlabs_provider

        audio_result = elevenlabs_provider.text_to_speech(
            text=text,
            voice=voice
        )

        if not audio_result.get('success'):
            return JsonResponse({
                'success': False,
                'error_message': f"Voice generation failed: {audio_result.get('error_message')}"
            }, status=500)

        audio_url = audio_result.get('audio_url')
        logger.info(f"   ✅ Voice audio generated: {audio_url}")

        # Step 2: Get audio file path
        # audio_url is like /media/audio/elevenlabs/filename.mp3
        if audio_url.startswith('/media/'):
            audio_path = os.path.join(settings.MEDIA_ROOT, audio_url.replace('/media/', ''))
        else:
            audio_path = audio_url

        if not os.path.exists(audio_path):
            return JsonResponse({
                'success': False,
                'error_message': 'Generated audio file not found'
            }, status=500)

        # Step 3: Mix audio with video using ffmpeg
        logger.info(f"   Step 2: Mixing audio with video...")
        timestamp = int(time.time())
        output_filename = f"voiceover_{video.id}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        import subprocess

        # FFmpeg command to mix audio
        # This replaces original audio with voiceover
        # Use amix if you want to blend both audio tracks
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-map', '0:v',  # Video from first input
            '-map', '1:a',  # Audio from second input
            '-c:v', 'copy',  # Copy video codec (fast)
            '-c:a', 'aac',   # Re-encode audio to AAC
            '-b:a', '192k',
            '-shortest',     # End when shortest stream ends
            output_path
        ]

        logger.info(f"   FFmpeg command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            logger.error(f"   FFmpeg error: {result.stderr}")
            return JsonResponse({
                'success': False,
                'error_message': f'FFmpeg mixing failed: {result.stderr[:200]}'
            }, status=500)

        logger.info(f"   ✅ Audio mixed successfully!")

        # Step 4: Create new video record
        from core.services.workspace_resolver import get_active_workspace
        new_video = VideoHistory.objects.create(
            user=request.user,
            prompt=f"Voiceover ({voice}) added to video {video.id}",
            video_url=f'/media/videos/{output_filename}',
            status='completed',
            project=video.project if hasattr(video, 'project') else None,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 171] Voiceover added successfully!")
        logger.info(f"   New video ID: {new_video.id}")
        logger.info(f"   Video URL: {new_video.video_url}")

        return JsonResponse({
            'success': True,
            'video_id': str(new_video.id),
            'video_url': new_video.video_url,
            'voice': voice,
            'original_video_id': str(video.id),
            'agent': 'AudioGenerationAgent',
            'operation': 'add_voiceover',
            'operation_display': f'Voiceover addition ({voice})'
        })

    except subprocess.TimeoutExpired:
        logger.error(f"❌ [Session 171] FFmpeg timeout")
        return JsonResponse({
            'success': False,
            'error_message': 'Audio mixing timed out'
        }, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 171] Add voiceover error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error_message': str(e)}, status=500)


# ============================================================================
# Session 1013: Add SFX to Video
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def add_sfx_to_video_view(request):
    """
    Add sound effects to an existing video using ElevenLabs SFX + ffmpeg.

    Session 1013: Generates SFX audio from a text description and mixes it
    with an existing video, mirroring the voiceover flow.

    Expected JSON body:
        - video_id: str - Video to add SFX to
        - description: str - Text description of the sound effect
        - duration: float (optional) - Duration in seconds 0.5-22 (default 5.0)
        - volume: float (optional) - SFX volume 0.0-1.0 (default 0.5)
        - project_id: str (optional) - Project to associate result with

    Returns:
        - success: bool
        - video_url: str - URL to new video with SFX
        - video_id: str - ID of new video
        - audio_url: str - URL to generated SFX audio
    """
    try:
        data = json.loads(request.body) if request.body else {}

        video_id = data.get('video_id')
        description = data.get('description')
        duration = float(data.get('duration', 5.0))
        volume = float(data.get('volume', 0.5))
        project_id = data.get('project_id')

        if not video_id:
            return JsonResponse({
                'success': False,
                'error_message': 'video_id is required'
            }, status=400)

        if not description:
            return JsonResponse({
                'success': False,
                'error_message': 'description is required'
            }, status=400)

        # Clamp duration to ElevenLabs limits
        duration = max(0.5, min(22.0, duration))

        logger.info(f"🔊 [Session 1013] Adding SFX to video {video_id}...")
        logger.info(f"   Description: {description[:60]}...")
        logger.info(f"   Duration: {duration}s, Volume: {volume}")

        # Get the video
        video = _resolve_video_by_id(video_id, request.user, project_id)
        if not video:
            return JsonResponse({
                'success': False,
                'error_message': f'Video {video_id} not found'
            }, status=404)

        video_path = _get_video_local_path(video)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({
                'success': False,
                'error_message': 'Video file not found on disk'
            }, status=404)

        # Step 1: Generate SFX audio via ElevenLabs
        logger.info(f"   Step 1: Generating SFX audio...")
        from content.elevenlabs_provider import elevenlabs_provider

        sfx_result = elevenlabs_provider.text_to_sound(
            prompt=description,
            duration=duration
        )

        if not sfx_result.get('success'):
            return JsonResponse({
                'success': False,
                'error_message': f"SFX generation failed: {sfx_result.get('error_message')}"
            }, status=500)

        audio_url = sfx_result.get('audio_url')
        logger.info(f"   ✅ SFX audio generated: {audio_url}")

        # Step 2: Resolve audio file path
        if audio_url.startswith('/media/'):
            audio_path = os.path.join(settings.MEDIA_ROOT, audio_url.replace('/media/', ''))
        else:
            audio_path = audio_url

        if not os.path.exists(audio_path):
            return JsonResponse({
                'success': False,
                'error_message': 'Generated SFX audio file not found'
            }, status=500)

        # Step 3: Mix SFX with video using ffmpeg
        logger.info(f"   Step 2: Mixing SFX with video...")
        timestamp = int(time.time())
        output_filename = f"sfx_{video.id}_{timestamp}.mp4"
        output_path = os.path.join(settings.MEDIA_ROOT, 'videos', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        import subprocess

        # Mix SFX audio with original video audio using amix filter
        # This blends both tracks rather than replacing
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-filter_complex',
            f'[1:a]volume={volume}[sfx];[0:a][sfx]amix=inputs=2:duration=first:dropout_transition=2[aout]',
            '-map', '0:v',
            '-map', '[aout]',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '192k',
            output_path
        ]

        logger.info(f"   FFmpeg command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            # Fallback: video may have no audio track — use simpler command
            logger.warning(f"   amix failed (video may lack audio), trying simple overlay...")
            cmd_fallback = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-map', '0:v',
                '-map', '1:a',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-shortest',
                output_path
            ]
            result = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                logger.error(f"   FFmpeg error: {result.stderr}")
                return JsonResponse({
                    'success': False,
                    'error_message': f'FFmpeg mixing failed: {result.stderr[:200]}'
                }, status=500)

        logger.info(f"   ✅ SFX mixed successfully!")

        # Step 4: Create new video record
        from core.services.workspace_resolver import get_active_workspace
        new_video = VideoHistory.objects.create(
            user=request.user,
            prompt=f"SFX ({description[:40]}) added to video {video.id}",
            video_url=f'/media/videos/{output_filename}',
            status='completed',
            project=video.project if hasattr(video, 'project') else None,
            workspace=get_active_workspace(request.user),
        )

        logger.info(f"✅ [Session 1013] SFX added successfully!")
        logger.info(f"   New video ID: {new_video.id}")
        logger.info(f"   Video URL: {new_video.video_url}")

        return JsonResponse({
            'success': True,
            'video_id': str(new_video.id),
            'video_url': new_video.video_url,
            'audio_url': audio_url,
            'description': description,
            'original_video_id': str(video.id),
            'agent': 'AudioGenerationAgent',
            'operation': 'add_sfx',
            'operation_display': f'SFX addition ({description[:30]})'
        })

    except subprocess.TimeoutExpired:
        logger.error(f"❌ [Session 1013] FFmpeg timeout")
        return JsonResponse({
            'success': False,
            'error_message': 'Audio mixing timed out'
        }, status=500)
    except Exception as e:
        logger.error(f"❌ [Session 1013] Add SFX error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error_message': str(e)}, status=500)


# ============================================================================
# Session 479: DaVinci Resolve Renders Gallery API
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resolve_renders(request):
    """
    Get user's DaVinci Resolve render jobs for the gallery.

    Session 479: Display professional Resolve renders in the web gallery.

    Query parameters:
        - limit: Number of results (default: 20)
        - offset: Pagination offset (default: 0)
        - status: Filter by status (default: 'done')
        - grade: Filter by color grade

    Returns:
        List of completed Resolve render jobs with download URLs
    """
    try:
        from core.models_unified_system import ResolveRenderJob
        from pathlib import Path

        # Get query parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        status_filter = request.GET.get('status', 'done')
        grade_filter = request.GET.get('grade')

        # Build query
        queryset = ResolveRenderJob.objects.filter(user=request.user)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if grade_filter:
            queryset = queryset.filter(color_grade=grade_filter)

        # Order by newest first
        queryset = queryset.order_by('-created_at')

        # Get total count
        total_count = queryset.count()

        # Apply pagination
        renders = queryset[offset:offset + limit]

        # Format response
        render_list = []
        for render in renders:
            # Build download URL
            download_url = None
            if render.output_file_path:
                # Check if file exists
                file_path = Path(render.output_file_path)
                if file_path.exists():
                    # Build relative URL for download
                    download_url = f'/api/resolve-renders/{render.id}/download/'

            render_list.append({
                'id': str(render.id),
                'job_id': render.resolve_job_id,
                'status': render.status,
                'color_grade': render.color_grade or 'natural_vibrant',
                'auto_grade': render.auto_grade_selected,
                'template': render.template,
                'source_video_ids': render.source_video_ids,
                'file_size_mb': render.file_size_mb,
                'render_duration_seconds': render.render_duration_seconds,
                'download_url': download_url,
                'output_url': render.output_url,
                'created_at': render.created_at.isoformat(),
                'user_rating': render.user_rating,
                'was_used': render.was_used,
                'thumbnail_url': None,  # Could generate from video in future
                'spider_trends': render.spider_trends_used or {},
            })

        return JsonResponse({
            'success': True,
            'renders': render_list,
            'total_count': total_count,
            'has_more': (offset + limit) < total_count
        })

    except Exception as e:
        logger.error(f"Get resolve renders error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_resolve_render(request, render_id):
    """
    Download a completed DaVinci Resolve render.

    Session 479: Stream the rendered video file to the browser.
    """
    try:
        from core.models_unified_system import ResolveRenderJob
        from django.http import FileResponse
        from pathlib import Path
        import mimetypes

        # Get the render job
        render = ResolveRenderJob.objects.get(id=render_id, user=request.user)

        if render.status != 'done':
            return JsonResponse({
                'success': False,
                'error': f'Render is not complete (status: {render.status})'
            }, status=400)

        if not render.output_file_path:
            return JsonResponse({
                'success': False,
                'error': 'No output file available'
            }, status=404)

        file_path = Path(render.output_file_path)
        if not file_path.exists():
            return JsonResponse({
                'success': False,
                'error': 'Output file not found on disk'
            }, status=404)

        # Determine content type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = 'video/mp4'

        # Build filename
        filename = f"resolve_{render.resolve_job_id}_{render.color_grade or 'render'}{file_path.suffix}"

        # Stream the file
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type,
            as_attachment=True,
            filename=filename
        )

        # Track download
        render.was_used = True
        render.save(update_fields=['was_used'])

        return response

    except ResolveRenderJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Render not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Download resolve render error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_resolve_render(request, render_id):
    """
    Rate a DaVinci Resolve render for the learning loop.

    Session 479: User feedback improves automatic grade selection.

    Body:
        - rating: 1-5 star rating
        - feedback: Optional text feedback
    """
    try:
        from core.models_unified_system import ResolveRenderJob
        import json

        # Get the render job
        render = ResolveRenderJob.objects.get(id=render_id, user=request.user)

        # Parse request
        data = json.loads(request.body) if request.body else {}
        rating = data.get('rating')
        feedback = data.get('feedback', '')

        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return JsonResponse({
                    'success': False,
                    'error': 'Rating must be an integer between 1 and 5'
                }, status=400)
            render.user_rating = rating

        if feedback:
            render.user_feedback = feedback

        render.save(update_fields=['user_rating', 'user_feedback'])

        logger.info(f"⭐ Resolve render {render_id} rated: {rating}/5")

        return JsonResponse({
            'success': True,
            'message': f'Rating saved: {rating}/5',
            'render_id': str(render.id)
        })

    except ResolveRenderJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Render not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Rate resolve render error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
