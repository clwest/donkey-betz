"""
Project Share Views
Session 149: Public Share Links

Handles creating, viewing, and managing public share links for projects.
"""

import logging
from datetime import timedelta

from django.http import HttpResponse
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


# Session 1110 (PR fix/mounted-broken-route-fallbacks):
# The legacy share_*.html templates (share_expired, share_password,
# public_project_view, share_not_found, share_error) are gone — the public
# share surface never made it through the SPA migration. Until a React
# equivalent exists, we return minimal inline HTML fallbacks that preserve
# the original status codes and error semantics so /share/<token>/ stops
# 500-ing on TemplateDoesNotExist.
def _share_fallback_html(*, title: str, body: str) -> str:
    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{title}</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<style>body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,"
        "Helvetica,Arial,sans-serif;background:#0b0f17;color:#e7eaf0;"
        "display:flex;align-items:center;justify-content:center;"
        "min-height:100vh;margin:0;padding:24px}"
        ".card{max-width:560px;width:100%;background:#141a26;border-radius:12px;"
        "padding:32px;box-shadow:0 8px 32px rgba(0,0,0,.4)}"
        "h1{margin:0 0 12px;font-size:20px}p{margin:0 0 16px;line-height:1.55;color:#aab2c0}"
        "a{color:#7cc4ff;text-decoration:none}a:hover{text-decoration:underline}"
        "</style></head><body><div class=\"card\">"
        f"<h1>{title}</h1>{body}"
        "<p><a href=\"/\">Return to Donkey Betz</a></p>"
        "</div></body></html>"
    )


def _share_password_form(share_token: str, error: str | None = None) -> str:
    error_html = f"<p style=\"color:#ff6b7a\">{error}</p>" if error else ""
    body = (
        "<p>This share link is password protected.</p>"
        f"{error_html}"
        f"<form method=\"post\" action=\"/share/{share_token}/\">"
        "<input type=\"password\" name=\"password\" placeholder=\"Password\" "
        "style=\"width:100%;padding:10px;border-radius:8px;border:1px solid #2a3243;"
        "background:#0b0f17;color:#e7eaf0;margin-bottom:12px\">"
        "<button type=\"submit\" style=\"padding:10px 16px;border-radius:8px;"
        "border:0;background:#3b82f6;color:white;cursor:pointer\">View shared project</button>"
        "</form>"
    )
    return _share_fallback_html(title="Password required", body=body)


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

            return HttpResponse(
                _share_fallback_html(
                    title="Share unavailable",
                    body=f"<p>{message}.</p>",
                ),
                status=status.HTTP_410_GONE,
            )

        # Check password
        if share.password_hash:
            password = request.GET.get('password') or request.POST.get('password')

            if not password:
                # Show password prompt
                logger.info(f"🔒 Password prompt for share {share_token[:8]}...")
                return HttpResponse(_share_password_form(share_token))

            if not share.check_password(password):
                # Wrong password
                logger.warning(f"❌ Wrong password for share {share_token[:8]}...")
                return HttpResponse(
                    _share_password_form(
                        share_token,
                        error='Incorrect password. Please try again.',
                    ),
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # Increment view count
        share.increment_view_count()
        logger.info(f"👁️ Share viewed (count: {share.view_count}): {share.project.name} ({share_token[:8]}...)")

        # Get project and content (preserved for view-count + side effects)
        project = share.project
        _images = ImageHistory.objects.filter(project=project).order_by('-created_at')
        _videos = VideoHistory.objects.filter(project=project).order_by('-created_at')
        _models = MiniFigAsset.objects.filter(project=project).order_by('-created_at')
        _stats = calculate_project_stats(project.id, project.user)

        # Session 1110: public_project_view.html no longer exists. Until a
        # React equivalent ships, return a minimal landing fallback that
        # confirms the share is valid and points users back to the app.
        body = (
            f"<p><strong>{project.name}</strong> has been shared with you.</p>"
            "<p>The public viewer is being rebuilt as part of the SPA migration. "
            "If you have an account, sign in to view the full project.</p>"
        )
        return HttpResponse(
            _share_fallback_html(title="Shared project", body=body)
        )

    except ProjectShare.DoesNotExist:
        logger.error(f"❌ Share not found: {share_token[:8]}...")
        return HttpResponse(
            _share_fallback_html(
                title="Share not found",
                body="<p>This share link does not exist or has been removed.</p>",
            ),
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"❌ View share error for {share_token[:8]}...: {e}")
        return HttpResponse(
            _share_fallback_html(
                title="Something went wrong",
                body="<p>We hit an unexpected error loading this share. "
                     "Please try again later.</p>",
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
