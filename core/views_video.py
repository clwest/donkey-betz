"""
Video Generation Views

Handles video generation requests using RunwayML Gen-3 Alpha.
"""

import json
import logging
from typing import Dict, Any

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from content.models import ContentGeneration
from content.video_provider import runway_provider

logger = logging.getLogger(__name__)


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
        duration = int(data.get('duration', 5))
        quality = data.get('quality', 'gen3a_turbo')
        style = data.get('style', 'realistic')
        enhance_prompt = data.get('enhance_prompt', True)
        enhancement_level = data.get('enhancement_level', 'advanced')
        
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
        
        # Extract parameters with defaults
        duration = int(data.get('duration', 5))
        quality = data.get('quality', 'gen3a_turbo')
        enhance_prompt = data.get('enhance_prompt', True)
        enhancement_level = data.get('enhancement_level', 'advanced')
        
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
        result = runway_provider.image_to_video(
            image_url=image_url,
            motion_prompt=motion_prompt,
            duration=duration,
            quality=quality,
            enhance_prompt=enhance_prompt,
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