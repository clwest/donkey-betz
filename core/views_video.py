"""
Video Generation Views

Handles video generation requests using RunwayML Gen-3 Alpha.
"""

import json
import logging
from typing import Dict, Any
import requests
from io import BytesIO
from PIL import Image
import tempfile
import os
import subprocess

from django.conf import settings
from django.contrib.auth.decorators import login_required
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

logger = logging.getLogger(__name__)


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
        
        # Validate required fields
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return JsonResponse({
                'success': False,
                'error': 'Prompt is required'
            }, status=400)
        
        # Extract parameters with defaults
        duration = int(data.get('duration', 4))  # Changed default to 4 for veo3.1 models
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
                'error': 'Image URL or image ID is required'
            }, status=400)
        
        motion_prompt = data.get('motion_prompt', '').strip()
        if not motion_prompt:
            return JsonResponse({
                'success': False,
                'error': 'Motion prompt is required'
            }, status=400)
        
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

                # Session 122: Track generated video in AI Assistant for intelligent chaining
                try:
                    from django.core.cache import cache
                    cache_key = f'assistant_{request.user.id}'
                    assistant = cache.get(cache_key)
                    if assistant and video_history:
                        # Determine source image ID if this was image-to-video
                        source_image_id = None
                        if source_image:
                            source_image_id = str(source_image.id)

                        assistant.track_generated_video(
                            video_id=str(video_history.id),
                            video_url=local_video_url,
                            prompt=content.prompt,
                            source_image_id=source_image_id
                        )
                        logger.info(f"🎬 Tracked video {video_history.id} in AI Assistant (source_image: {source_image_id})")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to track video in AI Assistant: {e}")
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
                pass

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
        from django.db.models import Q
        queryset = VideoHistory.objects.filter(user=request.user).exclude(
            Q(video_url__icontains='cloudfront.net') |
            Q(video_url__icontains='storage.googleapis.com') |
            Q(video_url__icontains='_jwt=')
        )

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
            except:
                pass

        # Save to history if successful
        if result.success and result.task_id:
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='video_to_video',
                prompt=prompt or f"{mode} mode transformation",
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_aleph'),
                ratio="1280:720",
                status='pending'
            )

            # Session 142: Track agent contribution
            try:
                from agents.models import UnifiedAgentTemplate, AgentContribution
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
            except:
                pass

        # Save to history if successful
        if result.success and result.task_id:
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='upscale_video',
                prompt=prompt,
                model_used=getattr(result, 'model_used', 'upscale_v1'),
                ratio="3840:2160",  # 4K
                status='pending'
            )

            # Session 142: Track agent contribution
            try:
                from agents.models import UnifiedAgentTemplate, AgentContribution
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
        except:
            data = request.POST.dict()

        # Get video URL (must be from gallery)
        video_url = data.get('video_url', '').strip()
        extension_seconds = int(data.get('extension_seconds', 10))
        prompt = data.get('prompt', '').strip()

        # DEBUG: Print what we received
        print(f"🔍 DEBUG - Received data: {data}")
        print(f"🔍 DEBUG - video_url: '{video_url}'")
        print(f"🔍 DEBUG - extension_seconds: {extension_seconds}")

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
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='extend_video',
                prompt=prompt or f"Extended by {extension_seconds}s",
                duration=extension_seconds,
                model_used='gen4_aleph',
                ratio="1280:720",
                status='pending',
                parent_video_url=video_url  # Track which video was extended
            )

            # Session 142: Track agent contribution
            try:
                from agents.models import UnifiedAgentTemplate, AgentContribution
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
                except:
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
        except:
            pass

        # Save to history if successful
        if result.success and result.task_id:
            video_history = VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='character_performance',
                prompt=prompt,
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_character'),
                ratio="1280:720",
                status='pending'
            )

            # Session 142: Track agent contribution
            try:
                from agents.models import UnifiedAgentTemplate, AgentContribution
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
                videos = VideoHistory.objects.filter(user=request.user).order_by('id')
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

        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)

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
            project=project  # Session 156: Associate with project
        )

        logger.info(f"✅ [Session 154] Video upscaled: {video.id} → {upscaled_video.id} ({scale_factor}x)")

        # Session 155: Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
                videos = VideoHistory.objects.filter(user=request.user).order_by('id')
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

        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)

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
        effect_video = VideoHistory.objects.create(
            user=request.user,
            video_type='enhanced',
            prompt=f"{effect.capitalize()} effect applied to video {video.id}",
            duration=video.duration,
            model_used=f'ffmpeg_{effect}',
            ratio=video.ratio,
            status='completed',
            video_url=f'/media/{output_filename}',
            generation_completed=timezone.now()
        )

        logger.info(f"✅ [Session 154] Effect applied: {video.id} → {effect_video.id} ({effect})")

        # Session 155: Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
                videos = VideoHistory.objects.filter(user=request.user).order_by('id')
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

        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)

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

        # Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking extracted frame to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")

        # Create ImageHistory record for the extracted frame
        # Use the correct field names for ImageHistory model
        extracted_image = ImageHistory.objects.create(
            user=request.user,
            prompt=f"Frame extracted at {timestamp}s from video {video.id}",
            image_type='generated',  # Use existing type; 'extracted_frame' isn't in choices
            filename=os.path.basename(output_filename),
            file_path=f'/media/{output_filename}',
            parameters={'source_video_id': str(video.id), 'timestamp': timestamp, 'operation': 'frame_extraction'},
            project=project
        )

        logger.info(f"✅ [Session 159] Frame extracted: video {video.id} @ {timestamp}s → image {extracted_image.id}")

        # Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
                videos = VideoHistory.objects.filter(user=request.user).order_by('id')
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
        import subprocess

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

        result = subprocess.run(cmd, capture_output=True, text=True)

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

        # Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking reversed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")

        # Create VideoHistory record for the reversed video
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
            project=project
        )

        logger.info(f"✅ [Session 159] Video reversed: {video.id} → {reversed_video.id}")

        # Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
                videos = VideoHistory.objects.filter(user=request.user).order_by('id')
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
        import subprocess

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

        result = subprocess.run(cmd, capture_output=True, text=True)

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

        # Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 159] Linking trimmed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 159] Project {project_id} not found")

        # Create VideoHistory record
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
            project=project
        )

        logger.info(f"✅ [Session 159] Video trimmed: {video.id} → {trimmed_video.id} ({duration_trimmed}s)")

        # Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
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

        result = subprocess.run(cmd, capture_output=True, text=True)

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

        # Get project if project_id provided
        project = None
        if project_id:
            from content.models import CreativeProject
            try:
                project = CreativeProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 [Session 160] Linking speed video to project: {project.name}")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ [Session 160] Project {project_id} not found")

        # Create VideoHistory record
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
            project=project
        )

        speed_description = "slow motion" if speed < 1.0 else "sped up" if speed > 1.0 else "normal speed"
        logger.info(f"✅ [Session 160] Video speed changed: {video.id} → {speed_video.id} ({speed}x {speed_description})")

        # Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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

        result = subprocess.run(cmd, capture_output=True, text=True)

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
            result = subprocess.run(cmd, capture_output=True, text=True)

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
                result = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up concat list
        try:
            os.remove(concat_list_path)
        except:
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
            project=project
        )

        logger.info(f"✅ [Session 160] Videos concatenated: {[str(v.id) for v in videos]} → {concat_video.id}")

        # Track agent contribution
        try:
            from agents.models import UnifiedAgentTemplate, AgentContribution
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
