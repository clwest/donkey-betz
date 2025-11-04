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
            content = ContentGeneration.objects.get(
                user=request.user,
                metadata__task_id=task_id
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

                # Check if VideoHistory already exists for this task
                video_history, created = VideoHistory.objects.get_or_create(
                    user=request.user,
                    video_id=task_id,
                    defaults={
                        'video_url': result.video_url,
                        'thumbnail_url': result.thumbnail_url or '',
                        'video_type': video_type,
                        'prompt': content.prompt,
                        'parameters': metadata,
                        'model_used': model_used,
                        'duration': result.duration,
                        'ratio': metadata.get('ratio', ''),
                        'status': 'completed',
                        'source_image': source_image,
                        'generation_completed': timezone.now()
                    }
                )

                # Update if already exists
                if not created:
                    video_history.video_url = result.video_url
                    video_history.thumbnail_url = result.thumbnail_url or ''
                    video_history.status = 'completed'
                    video_history.generation_completed = timezone.now()
                    video_history.save()

                logger.info(f"✅ Video saved to gallery: {video_history.id}")
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
            pass
        
        # Return status response
        response_data = {
            'status': result.status,
            'progress': result.progress
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
        queryset = VideoHistory.objects.filter(user=request.user)

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
            VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='video_to_video',
                prompt=prompt or f"{mode} mode transformation",
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_aleph'),
                ratio="1280:720",
                status='pending'
            )

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
            VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='upscale_video',
                prompt=prompt,
                model_used=getattr(result, 'model_used', 'upscale_v1'),
                ratio="3840:2160",  # 4K
                status='pending'
            )

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
            VideoHistory.objects.create(
                video_id=result.task_id,
                user=request.user if request.user.is_authenticated else None,
                video_type='character_performance',
                prompt=prompt,
                duration=duration,
                model_used=getattr(result, 'model_used', 'gen4_character'),
                ratio="1280:720",
                status='pending'
            )

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
