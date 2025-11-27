"""
Real-Time Project Collaboration API Endpoints

Session 220 Phase E: REST API for managing collaborative projects,
collaborators, invitations, and comments.

Endpoints:
- GET/POST /api/projects/shared/ - List/create projects
- GET/PUT/DELETE /api/projects/shared/{id}/ - Project CRUD
- POST /api/projects/shared/{id}/invite/ - Invite collaborator
- POST /api/projects/invitations/{id}/accept/ - Accept invitation
- POST /api/projects/invitations/{id}/decline/ - Decline invitation
- GET /api/projects/invitations/ - List pending invitations
- GET /api/projects/shared/{id}/collaborators/ - List collaborators
- DELETE /api/projects/shared/{id}/collaborators/{user_id}/ - Remove collaborator
- GET /api/projects/shared/{id}/activity/ - Get activity log
- GET /api/projects/shared/{id}/comments/ - Get comments
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
@login_required
def list_create_projects(request):
    """
    GET: List all projects user has access to (owned + collaborator)
    POST: Create a new shared project
    """
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectActivity

    if request.method == "GET":
        # Get owned projects
        owned = SharedProject.objects.filter(owner=request.user)

        # Get projects where user is a collaborator
        collab_project_ids = ProjectCollaborator.objects.filter(
            user=request.user,
            status='accepted'
        ).values_list('project_id', flat=True)

        collaborated = SharedProject.objects.filter(id__in=collab_project_ids)

        # Combine and serialize
        projects = list(owned) + list(collaborated)
        projects = sorted(projects, key=lambda p: p.updated_at, reverse=True)

        return JsonResponse({
            'success': True,
            'projects': [{
                'id': str(p.id),
                'name': p.name,
                'description': p.description,
                'thumbnail': p.thumbnail,
                'owner_id': str(p.owner_id),
                'owner_name': p.owner.username,
                'is_owner': p.owner_id == request.user.id,
                'visibility': p.visibility,
                'status': p.status,
                'version': p.version,
                'collaborator_count': p.collaborators.filter(status='accepted').count(),
                'created_at': p.created_at.isoformat(),
                'updated_at': p.updated_at.isoformat()
            } for p in projects],
            'count': len(projects)
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body)

            project = SharedProject.objects.create(
                name=body.get('name', 'Untitled Project'),
                description=body.get('description', ''),
                owner=request.user,
                visibility=body.get('visibility', 'private'),
                content=body.get('content', {}),
                project_settings=body.get('project_settings', {})
            )

            # Log creation
            ProjectActivity.objects.create(
                project=project,
                user=request.user,
                action='created',
                details={'name': project.name}
            )

            return JsonResponse({
                'success': True,
                'project': {
                    'id': str(project.id),
                    'name': project.name,
                    'description': project.description,
                    'visibility': project.visibility,
                    'created_at': project.created_at.isoformat()
                },
                'message': 'Project created successfully'
            })

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@require_http_methods(["GET", "PUT", "DELETE"])
@login_required
def project_detail(request, project_id):
    """
    GET: Get project details
    PUT: Update project
    DELETE: Delete project (owner only)
    """
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectActivity

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check access
    is_owner = project.owner_id == request.user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        status='accepted'
    ).exists()

    if not is_owner and not is_collaborator:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    if request.method == "GET":
        return JsonResponse({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name,
                'description': project.description,
                'thumbnail': project.thumbnail,
                'content': project.content,
                'project_settings': project.project_settings,
                'owner_id': str(project.owner_id),
                'owner_name': project.owner.username,
                'is_owner': is_owner,
                'visibility': project.visibility,
                'status': project.status,
                'version': project.version,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat(),
                'collaborators': [{
                    'user_id': str(c.user_id),
                    'username': c.user.username,
                    'role': c.role,
                    'status': c.status
                } for c in project.collaborators.select_related('user')]
            }
        })

    elif request.method == "PUT":
        # Collaborators with editor+ role can edit
        collab = ProjectCollaborator.objects.filter(
            project=project,
            user=request.user,
            status='accepted'
        ).first()

        if not is_owner and (not collab or not collab.can_edit()):
            return JsonResponse({
                'success': False,
                'error': 'Edit access denied'
            }, status=403)

        try:
            body = json.loads(request.body)

            if 'name' in body:
                project.name = body['name']
            if 'description' in body:
                project.description = body['description']
            if 'thumbnail' in body:
                project.thumbnail = body['thumbnail']
            if 'content' in body:
                project.content = body['content']
            if 'project_settings' in body:
                project.project_settings = body['project_settings']
            if 'visibility' in body and is_owner:
                project.visibility = body['visibility']
            if 'status' in body and is_owner:
                project.status = body['status']

            project.last_edited_by = request.user
            project.save()
            project.increment_version()

            # Log edit
            ProjectActivity.objects.create(
                project=project,
                user=request.user,
                action='edited',
                details={'fields': list(body.keys())}
            )

            return JsonResponse({
                'success': True,
                'message': 'Project updated',
                'version': project.version
            })

        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    elif request.method == "DELETE":
        if not is_owner:
            return JsonResponse({
                'success': False,
                'error': 'Only the owner can delete the project'
            }, status=403)

        project.delete()
        return JsonResponse({
            'success': True,
            'message': 'Project deleted'
        })


@require_http_methods(["POST"])
@login_required
def invite_collaborator(request, project_id):
    """Invite a user to collaborate on a project"""
    from core.models_unified_system import SharedProject, ProjectCollaborator
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check permission (owner or admin can invite)
    is_owner = project.owner_id == request.user.id
    is_admin = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        role='admin',
        status='accepted'
    ).exists()

    if not is_owner and not is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Only owner or admin can invite collaborators'
        }, status=403)

    try:
        body = json.loads(request.body)
        username_or_email = body.get('user')
        role = body.get('role', 'editor')

        # Find user
        user = User.objects.filter(
            Q(username=username_or_email) | Q(email=username_or_email)
        ).first()

        if not user:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            }, status=404)

        if user.id == project.owner_id:
            return JsonResponse({
                'success': False,
                'error': 'Cannot invite the project owner'
            }, status=400)

        # Check if already invited/collaborating
        existing = ProjectCollaborator.objects.filter(
            project=project,
            user=user
        ).first()

        if existing:
            if existing.status == 'accepted':
                return JsonResponse({
                    'success': False,
                    'error': 'User is already a collaborator'
                }, status=400)
            else:
                # Update existing invitation
                existing.role = role
                existing.status = 'pending'
                existing.invited_by = request.user
                existing.invited_at = timezone.now()
                existing.save()

                return JsonResponse({
                    'success': True,
                    'message': f'Invitation resent to {user.username}'
                })

        # Create invitation
        invitation = ProjectCollaborator.objects.create(
            project=project,
            user=user,
            role=role,
            status='pending',
            invited_by=request.user
        )

        return JsonResponse({
            'success': True,
            'invitation': {
                'id': str(invitation.id),
                'user_id': str(user.id),
                'username': user.username,
                'role': role,
                'status': 'pending'
            },
            'message': f'Invitation sent to {user.username}'
        })

    except Exception as e:
        logger.error(f"Error inviting collaborator: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def list_invitations(request):
    """List pending invitations for the current user"""
    from core.models_unified_system import ProjectCollaborator

    try:
        invitations = ProjectCollaborator.objects.filter(
            user=request.user,
            status='pending'
        ).select_related('project', 'invited_by')

        invitation_list = []
        for inv in invitations:
            try:
                invitation_list.append({
                    'id': str(inv.id),
                    'project_id': str(inv.project_id),
                    'project_name': inv.project.name if inv.project else 'Unknown Project',
                    'invited_by': inv.invited_by.username if inv.invited_by else 'Unknown',
                    'role': inv.role,
                    'invited_at': inv.invited_at.isoformat() if inv.invited_at else None
                })
            except Exception as e:
                logger.warning(f"Error serializing invitation {inv.id}: {e}")
                continue

        return JsonResponse({
            'success': True,
            'invitations': invitation_list,
            'count': len(invitation_list)
        })
    except Exception as e:
        logger.error(f"Error listing invitations: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def accept_invitation(request, invitation_id):
    """Accept a collaboration invitation"""
    from core.models_unified_system import ProjectCollaborator, ProjectActivity

    try:
        invitation = ProjectCollaborator.objects.get(
            id=invitation_id,
            user=request.user,
            status='pending'
        )
    except ProjectCollaborator.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Invitation not found'
        }, status=404)

    invitation.status = 'accepted'
    invitation.accepted_at = timezone.now()
    invitation.save()

    # Log join
    ProjectActivity.objects.create(
        project=invitation.project,
        user=request.user,
        action='joined',
        details={'role': invitation.role}
    )

    return JsonResponse({
        'success': True,
        'message': f'You joined "{invitation.project.name}" as {invitation.role}',
        'project_id': str(invitation.project_id)
    })


@require_http_methods(["POST"])
@login_required
def decline_invitation(request, invitation_id):
    """Decline a collaboration invitation"""
    from core.models_unified_system import ProjectCollaborator

    try:
        invitation = ProjectCollaborator.objects.get(
            id=invitation_id,
            user=request.user,
            status='pending'
        )
    except ProjectCollaborator.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Invitation not found'
        }, status=404)

    invitation.status = 'declined'
    invitation.save()

    return JsonResponse({
        'success': True,
        'message': 'Invitation declined'
    })


@require_http_methods(["GET"])
@login_required
def list_collaborators(request, project_id):
    """List all collaborators for a project"""
    from core.models_unified_system import SharedProject, ProjectCollaborator

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check access
    is_owner = project.owner_id == request.user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        status='accepted'
    ).exists()

    if not is_owner and not is_collaborator:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    collaborators = ProjectCollaborator.objects.filter(
        project=project
    ).select_related('user', 'invited_by')

    return JsonResponse({
        'success': True,
        'owner': {
            'user_id': str(project.owner_id),
            'username': project.owner.username,
            'role': 'owner'
        },
        'collaborators': [{
            'id': str(c.id),
            'user_id': str(c.user_id),
            'username': c.user.username,
            'role': c.role,
            'status': c.status,
            'invited_by': c.invited_by.username if c.invited_by else None,
            'invited_at': c.invited_at.isoformat(),
            'accepted_at': c.accepted_at.isoformat() if c.accepted_at else None
        } for c in collaborators],
        'count': collaborators.count() + 1  # +1 for owner
    })


@require_http_methods(["DELETE"])
@login_required
def remove_collaborator(request, project_id, user_id):
    """Remove a collaborator from a project"""
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectActivity

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check permission
    is_owner = project.owner_id == request.user.id
    is_admin = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        role='admin',
        status='accepted'
    ).exists()

    # User can remove themselves or owner/admin can remove others
    is_self = str(request.user.id) == str(user_id)

    if not is_self and not is_owner and not is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        }, status=403)

    try:
        collaborator = ProjectCollaborator.objects.get(
            project=project,
            user_id=user_id
        )
        username = collaborator.user.username
        collaborator.delete()

        # Log removal
        ProjectActivity.objects.create(
            project=project,
            user=request.user,
            action='left' if is_self else 'invited',  # Using 'invited' as removal log
            details={'username': username, 'action': 'removed'}
        )

        return JsonResponse({
            'success': True,
            'message': f'{username} removed from project'
        })

    except ProjectCollaborator.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Collaborator not found'
        }, status=404)


@require_http_methods(["GET"])
@login_required
def get_activity(request, project_id):
    """Get activity log for a project"""
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectActivity

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check access
    is_owner = project.owner_id == request.user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        status='accepted'
    ).exists()

    if not is_owner and not is_collaborator:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    limit = int(request.GET.get('limit', 50))
    activities = ProjectActivity.objects.filter(
        project=project
    ).select_related('user').order_by('-created_at')[:limit]

    return JsonResponse({
        'success': True,
        'activities': [{
            'id': str(a.id),
            'user_id': str(a.user_id),
            'username': a.user.username,
            'action': a.action,
            'action_display': a.get_action_display(),
            'details': a.details,
            'created_at': a.created_at.isoformat()
        } for a in activities],
        'count': len(activities)
    })


@require_http_methods(["GET", "POST"])
@login_required
def project_comments(request, project_id):
    """
    GET: List comments for a project
    POST: Add a comment
    """
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectComment, ProjectActivity

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check access
    is_owner = project.owner_id == request.user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        status='accepted'
    ).exists()

    if not is_owner and not is_collaborator:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    if request.method == "GET":
        comments = ProjectComment.objects.filter(
            project=project
        ).select_related('user', 'resolved_by').order_by('created_at')

        return JsonResponse({
            'success': True,
            'comments': [{
                'id': str(c.id),
                'text': c.text,
                'target_type': c.target_type,
                'target_id': c.target_id,
                'user_id': str(c.user_id),
                'username': c.user.username,
                'parent_id': str(c.parent_id) if c.parent_id else None,
                'is_resolved': c.is_resolved,
                'resolved_by': c.resolved_by.username if c.resolved_by else None,
                'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
                'created_at': c.created_at.isoformat()
            } for c in comments],
            'count': comments.count()
        })

    elif request.method == "POST":
        try:
            body = json.loads(request.body)

            comment = ProjectComment.objects.create(
                project=project,
                user=request.user,
                text=body.get('text', ''),
                target_type=body.get('target_type', ''),
                target_id=body.get('target_id', ''),
                parent_id=body.get('parent_id')
            )

            # Log activity
            ProjectActivity.objects.create(
                project=project,
                user=request.user,
                action='commented',
                details={'comment_id': str(comment.id)}
            )

            return JsonResponse({
                'success': True,
                'comment': {
                    'id': str(comment.id),
                    'text': comment.text,
                    'target_type': comment.target_type,
                    'target_id': comment.target_id,
                    'created_at': comment.created_at.isoformat()
                },
                'message': 'Comment added'
            })

        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@require_http_methods(["GET"])
@login_required
def get_presences(request, project_id):
    """Get current active presences for a project"""
    from core.models_unified_system import SharedProject, ProjectCollaborator, ProjectPresence

    try:
        project = SharedProject.objects.get(id=project_id)
    except SharedProject.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)

    # Check access
    is_owner = project.owner_id == request.user.id
    is_collaborator = ProjectCollaborator.objects.filter(
        project=project,
        user=request.user,
        status='accepted'
    ).exists()

    if not is_owner and not is_collaborator:
        return JsonResponse({
            'success': False,
            'error': 'Access denied'
        }, status=403)

    # Clean up stale presences
    ProjectPresence.cleanup_stale()

    presences = ProjectPresence.objects.filter(
        project=project,
        is_active=True
    ).select_related('user')

    return JsonResponse({
        'success': True,
        'presences': [{
            'user_id': str(p.user_id),
            'username': p.user.username,
            'status': p.status,
            'color': p.color,
            'cursor_position': p.cursor_position,
            'connected_at': p.connected_at.isoformat(),
            'last_activity': p.last_activity.isoformat()
        } for p in presences],
        'count': presences.count()
    })
