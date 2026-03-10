"""
Image views — portfolio functions.
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

