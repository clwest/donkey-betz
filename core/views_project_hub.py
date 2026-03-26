"""
Project Hub API — unified view of everything related to a project/workspace.

Aggregates deliverables, initiatives, conversations, and agent activity
into a single response so the frontend can show a complete project view.
"""

import logging
from datetime import timedelta

from django.db.models import Count, Q, Max
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from core.auth_middleware import token_auth_required

logger = logging.getLogger(__name__)


@require_GET
@token_auth_required
def list_projects(request):
    """List all project workspaces as cards with summary stats."""
    try:
        from core.models_skin_layer import ProjectWorkspace
        from core.models_deliverables import Deliverable
        from core.models import Initiative

        workspaces = ProjectWorkspace.objects.filter(
            user=request.user,
        ).order_by('-updated_at')

        projects = []
        for ws in workspaces:
            # Count deliverables linked to this workspace OR matching by name
            ws_name_first_word = ws.name.split(' ')[0].split('-')[0] if ws.name else ''
            deliverable_count = Deliverable.objects.filter(
                Q(workspace=ws) | (
                    Q(title__icontains=ws_name_first_word) &
                    Q(workspace__isnull=True)
                ) if ws_name_first_word and len(ws_name_first_word) > 3 else Q(workspace=ws)
            ).exclude(status='archived').count()

            # Count initiatives matching this workspace name
            initiative_count = Initiative.objects.filter(
                name__icontains=ws_name_first_word,
            ).count() if ws_name_first_word and len(ws_name_first_word) > 3 else 0

            # Get latest activity
            latest_deliverable = Deliverable.objects.filter(
                Q(workspace=ws) | (
                    Q(title__icontains=ws_name_first_word) &
                    Q(workspace__isnull=True)
                ) if ws_name_first_word and len(ws_name_first_word) > 3 else Q(workspace=ws)
            ).exclude(status='archived').aggregate(
                latest=Max('created_at'),
            )['latest']

            projects.append({
                'id': str(ws.id),
                'name': ws.name,
                'description': getattr(ws, 'description', '') or '',
                'deliverable_count': deliverable_count,
                'initiative_count': initiative_count,
                'latest_activity': latest_deliverable.isoformat() if latest_deliverable else None,
                'created_at': ws.created_at.isoformat() if hasattr(ws, 'created_at') and ws.created_at else None,
                'updated_at': ws.updated_at.isoformat() if hasattr(ws, 'updated_at') and ws.updated_at else None,
            })

        return JsonResponse({
            'success': True,
            'projects': projects,
            'total': len(projects),
        })
    except Exception as e:
        logger.error(f"list_projects error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
@token_auth_required
def project_hub(request, workspace_id):
    """Get the full hub view for a project — everything in one response."""
    try:
        from core.models_skin_layer import ProjectWorkspace
        from core.models_deliverables import Deliverable
        from core.models import Initiative, ChatConversation

        ws = ProjectWorkspace.objects.get(id=workspace_id)

        # Fuzzy name matching for unlinked content
        ws_name_first_word = ws.name.split(' ')[0].split('-')[0] if ws.name else ''
        name_q = (
            Q(title__icontains=ws_name_first_word) & Q(workspace__isnull=True)
        ) if ws_name_first_word and len(ws_name_first_word) > 3 else Q(pk=None)

        # Deliverables
        deliverables = Deliverable.objects.filter(
            Q(workspace=ws) | name_q
        ).exclude(status='archived').order_by('-created_at')[:50]

        deliverable_list = [{
            'id': str(d.id),
            'title': d.title,
            'type': d.deliverable_type,
            'category': d.category or '',
            'status': d.status,
            'agent_name': d.agent_name or '',
            'quality_score': d.quality_score,
            'word_count': d.word_count,
            'created_at': d.created_at.isoformat() if d.created_at else None,
            'preview': (d.preview_content or '')[:200],
        } for d in deliverables]

        # Initiatives
        init_q = Q(name__icontains=ws_name_first_word) if ws_name_first_word and len(ws_name_first_word) > 3 else Q(pk=None)
        initiatives = Initiative.objects.filter(init_q).order_by('-updated_at')[:20]

        initiative_list = [{
            'id': str(i.id),
            'name': i.name,
            'status': i.status,
            'current_stage': i.current_stage,
            'priority_score': getattr(i, 'priority_score', None),
            'purpose': getattr(i, 'purpose', ''),
            'program': getattr(i, 'program', ''),
            'updated_at': i.updated_at.isoformat() if i.updated_at else None,
        } for i in initiatives]

        # Conversations mentioning this project
        conv_q = Q(user_message__icontains=ws_name_first_word) if ws_name_first_word and len(ws_name_first_word) > 3 else Q(pk=None)
        conversations = ChatConversation.objects.filter(
            conv_q,
            user=request.user,
        ).values('conversation_id').annotate(
            message_count=Count('id'),
            last_at=Max('created_at'),
        ).order_by('-last_at')[:10]

        conversation_list = []
        for conv in conversations:
            first = ChatConversation.objects.filter(
                conversation_id=conv['conversation_id'],
            ).order_by('created_at').first()
            conversation_list.append({
                'conversation_id': conv['conversation_id'],
                'title': first.session_title if first and first.session_title else 'Untitled',
                'message_count': conv['message_count'],
                'last_at': conv['last_at'].isoformat() if conv['last_at'] else None,
            })

        # Stats summary
        stats = {
            'total_deliverables': len(deliverable_list),
            'total_initiatives': len(initiative_list),
            'total_conversations': len(conversation_list),
            'deliverables_by_type': {},
            'deliverables_by_status': {},
        }
        for d in deliverable_list:
            stats['deliverables_by_type'][d['type']] = stats['deliverables_by_type'].get(d['type'], 0) + 1
            stats['deliverables_by_status'][d['status']] = stats['deliverables_by_status'].get(d['status'], 0) + 1

        return JsonResponse({
            'success': True,
            'project': {
                'id': str(ws.id),
                'name': ws.name,
                'description': getattr(ws, 'description', '') or '',
            },
            'deliverables': deliverable_list,
            'initiatives': initiative_list,
            'conversations': conversation_list,
            'stats': stats,
        })
    except ProjectWorkspace.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)
    except Exception as e:
        logger.error(f"project_hub error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
