"""
Project Share Views
Session 149: Public Share Links

Handles creating, viewing, and managing public share links for projects.
"""

import logging
from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from content.models import (
    CreativeProject,
    ProjectShare,
    ImageHistory,
    VideoHistory,
    MiniFigAsset
)
from core.views_image import calculate_project_stats

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_share(request, project_id):
    """
    Create or update public share link for project
    Session 149: Public Share Links

    POST /api/creative-projects/<uuid:project_id>/share/create/

    Body:
    {
        "is_public": true,  # Enable/disable share link
        "password": "optional_password",  # Optional password protection
        "expires_in_days": 7  # Optional expiration (days from now)
    }

    Returns:
    {
        "success": true,
        "share_token": "abc123...",
        "share_url": "http://localhost:8000/share/abc123/",
        "is_active": true,
        "has_password": false,
        "expires_at": "2025-11-27T21:50:00Z",
        "view_count": 0
    }
    """
    try:
        # Verify project ownership
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Get or create share
        share, created = ProjectShare.objects.get_or_create(
            project=project,
            defaults={'is_active': True}
        )

        # Update settings
        is_public = request.data.get('is_public', True)
        password = request.data.get('password')
        expires_in_days = request.data.get('expires_in_days')

        share.is_active = is_public

        # Set password if provided
        if password:
            share.set_password(password)
            logger.info(f"🔒 Password protection enabled for project {project_id}")
        else:
            share.password_hash = None

        # Set expiration if provided
        if expires_in_days:
            share.expires_at = timezone.now() + timedelta(days=expires_in_days)
            logger.info(f"⏰ Share expires in {expires_in_days} days for project {project_id}")
        else:
            share.expires_at = None

        share.save()

        action = "created" if created else "updated"
        logger.info(f"✅ Share link {action} for project {project.name} ({project_id})")

        return Response({
            'success': True,
            'share_token': share.share_token,
            'share_url': share.get_share_url(request),
            'is_active': share.is_active,
            'has_password': bool(share.password_hash),
            'expires_at': share.expires_at.isoformat() if share.expires_at else None,
            'view_count': share.view_count,
            'created': created
        })

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project {project_id} not found or access denied")
        return Response({
            'error': 'Project not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ Create share error for project {project_id}: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def view_shared_project(request, share_token):
    """
    View public shared project (no auth required)
    Session 149: Public Share Links

    GET /share/<share_token>/
    GET /share/<share_token>/?password=xxx  # if password protected
    POST /share/<share_token>/  # with password in body

    Returns: Rendered HTML page or error page
    """
    try:
        share = ProjectShare.objects.select_related('project').get(share_token=share_token)

        # Check if accessible
        if not share.is_accessible():
            if share.is_expired():
                message = 'This share link has expired'
            else:
                message = 'This share link has been revoked'

            logger.warning(f"⛔ Share access denied: {message} (token: {share_token[:8]}...)")

            return render(request, 'share_expired.html', {
                'message': message
            }, status=status.HTTP_410_GONE)

        # Check password
        if share.password_hash:
            password = request.GET.get('password') or request.POST.get('password')

            if not password:
                # Show password prompt
                logger.info(f"🔒 Password prompt for share {share_token[:8]}...")
                return render(request, 'share_password.html', {
                    'share_token': share_token
                })

            if not share.check_password(password):
                # Wrong password
                logger.warning(f"❌ Wrong password for share {share_token[:8]}...")
                return render(request, 'share_password.html', {
                    'share_token': share_token,
                    'error': 'Incorrect password. Please try again.'
                })

        # Increment view count
        share.increment_view_count()
        logger.info(f"👁️ Share viewed (count: {share.view_count}): {share.project.name} ({share_token[:8]}...)")

        # Get project and content
        project = share.project
        images = ImageHistory.objects.filter(project=project).order_by('-created_at')
        videos = VideoHistory.objects.filter(project=project).order_by('-created_at')
        models = MiniFigAsset.objects.filter(project=project).order_by('-created_at')

        # Calculate stats
        stats = calculate_project_stats(project.id, project.user)

        return render(request, 'public_project_view.html', {
            'project': project,
            'images': images,
            'videos': videos,
            'models': models,
            'stats': stats,
            'share': share
        })

    except ProjectShare.DoesNotExist:
        logger.error(f"❌ Share not found: {share_token[:8]}...")
        return render(request, 'share_not_found.html', status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ View share error for {share_token[:8]}...: {e}")
        return render(request, 'share_error.html', {
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_project_share(request, project_id):
    """
    Revoke share link for project
    Session 149: Public Share Links

    POST /api/creative-projects/<uuid:project_id>/share/revoke/

    Returns:
    {
        "success": true,
        "message": "Share link revoked"
    }
    """
    try:
        # Verify project ownership
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Find and revoke share
        try:
            share = ProjectShare.objects.get(project=project)
            share.revoke()

            logger.info(f"🚫 Share link revoked for project {project.name} ({project_id})")

            return Response({
                'success': True,
                'message': 'Share link revoked successfully'
            })

        except ProjectShare.DoesNotExist:
            logger.warning(f"⚠️ No share link found for project {project_id}")
            return Response({
                'error': 'No share link exists for this project'
            }, status=status.HTTP_404_NOT_FOUND)

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project {project_id} not found or access denied")
        return Response({
            'error': 'Project not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ Revoke share error for project {project_id}: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_project_share(request, project_id):
    """
    Get share settings for project
    Session 149: Public Share Links

    GET /api/creative-projects/<uuid:project_id>/share/

    Returns:
    {
        "exists": true,
        "share_token": "abc123...",
        "share_url": "http://localhost:8000/share/abc123/",
        "is_active": true,
        "has_password": false,
        "expires_at": "2025-11-27T21:50:00Z",
        "view_count": 42,
        "last_viewed": "2025-11-20T15:30:00Z"
    }
    """
    try:
        # Verify project ownership
        project = CreativeProject.objects.get(id=project_id, user=request.user)

        # Find share
        try:
            share = ProjectShare.objects.get(project=project)

            return Response({
                'exists': True,
                'share_token': share.share_token,
                'share_url': share.get_share_url(request),
                'is_active': share.is_active,
                'has_password': bool(share.password_hash),
                'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                'view_count': share.view_count,
                'last_viewed': share.last_viewed.isoformat() if share.last_viewed else None,
                'created_at': share.created_at.isoformat()
            })

        except ProjectShare.DoesNotExist:
            return Response({
                'exists': False,
                'message': 'No share link created yet'
            })

    except CreativeProject.DoesNotExist:
        logger.error(f"❌ Project {project_id} not found or access denied")
        return Response({
            'error': 'Project not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ Get share error for project {project_id}: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
