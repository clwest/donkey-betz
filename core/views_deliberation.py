"""
Session 962 Phase 1: Deliberation API Endpoints

Provides read-only API access to deliberation sessions, turns, contracts, and doc versions.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Count

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
    DocVersion,
)

logger = logging.getLogger(__name__)


@require_GET
def deliberation_sessions_list(request):
    """GET /api/deliberation/sessions/ - List deliberation sessions."""
    status_filter = request.GET.get('status', '')
    session_type = request.GET.get('session_type', '')
    q = request.GET.get('q', '')
    limit = min(int(request.GET.get('limit', 50)), 200)

    qs = DeliberationSession.objects.annotate(
        turn_count=Count('turns'),
        contract_count=Count('contracts'),
    )

    if status_filter:
        qs = qs.filter(status=status_filter)
    if session_type:
        qs = qs.filter(session_type=session_type)
    if q:
        qs = qs.filter(objective__icontains=q)

    sessions = qs.order_by('-created_at')[:limit]

    data = []
    for s in sessions:
        data.append({
            'id': str(s.id),
            'session_type': s.session_type,
            'status': s.status,
            'objective': (s.objective or '')[:200],
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'completed_at': s.completed_at.isoformat() if s.completed_at else None,
            'trace_id': s.trace_id,
            'participant_count': len(s.participants) if s.participants else 0,
            'turn_count': s.turn_count,
            'contract_count': s.contract_count,
        })

    return JsonResponse({'count': len(data), 'sessions': data})


@require_GET
def deliberation_session_detail(request, session_id):
    """GET /api/deliberation/sessions/<uuid>/ - Session detail."""
    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

    return JsonResponse({
        'id': str(s.id),
        'session_type': s.session_type,
        'status': s.status,
        'objective': s.objective,
        'participants': s.participants,
        'evidence_pack': s.evidence_pack,
        'trace': s.trace,
        'trace_id': s.trace_id,
        'parent_session_id': str(s.parent_session_id) if s.parent_session_id else None,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None,
        'completed_at': s.completed_at.isoformat() if s.completed_at else None,
    })


@require_GET
def deliberation_turns(request, session_id):
    """GET /api/deliberation/sessions/<uuid>/turns/ - List turns."""
    full = request.GET.get('full', '0') == '1'

    turns = DeliberationTurn.objects.filter(
        session_id=session_id
    ).order_by('turn_number')

    data = []
    for t in turns:
        item = {
            'turn_number': t.turn_number,
            'agent_name': t.agent_name,
            'role': t.role,
            'created_at': t.created_at.isoformat() if t.created_at else None,
            'content_hash': t.content_hash,
            'trace_id': t.trace_id,
        }
        if full:
            item['content'] = t.content
        else:
            item['content'] = (t.content or '')[:500]
        data.append(item)

    return JsonResponse({'count': len(data), 'turns': data})


@require_GET
def deliberation_contracts(request, session_id):
    """GET /api/deliberation/sessions/<uuid>/contracts/ - List contracts."""
    contracts = ContractRecord.objects.filter(
        session_id=session_id
    ).order_by('created_at')

    data = []
    for c in contracts:
        data.append({
            'id': c.id,
            'contract_type': c.contract_type,
            'created_at': c.created_at.isoformat() if c.created_at else None,
            'contract_data': c.contract_data,
            'trace_id': c.trace_id,
        })

    return JsonResponse({'count': len(data), 'contracts': data})


@require_GET
def doc_versions_list(request):
    """GET /api/docs/versions/?doc_path= - List doc versions."""
    doc_path = request.GET.get('doc_path', '')
    limit = min(int(request.GET.get('limit', 50)), 200)

    qs = DocVersion.objects.all()
    if doc_path:
        qs = qs.filter(doc_path__icontains=doc_path)

    versions = qs.order_by('-created_at')[:limit]

    data = []
    for v in versions:
        data.append({
            'id': v.id,
            'doc_path': v.doc_path,
            'version_number': v.version_number,
            'created_at': v.created_at.isoformat() if v.created_at else None,
            'author_agent': v.author_agent,
            'change_reason': v.change_reason,
            'content_hash': v.content_hash,
            'trace_id': v.trace_id,
        })

    return JsonResponse({'count': len(data), 'versions': data})


@require_GET
def doc_version_detail(request, version_id):
    """GET /api/docs/versions/<id>/ - Doc version with content snapshot."""
    try:
        v = DocVersion.objects.get(id=version_id)
    except DocVersion.DoesNotExist:
        return JsonResponse({'error': 'Version not found'}, status=404)

    return JsonResponse({
        'id': v.id,
        'doc_path': v.doc_path,
        'version_number': v.version_number,
        'content_hash': v.content_hash,
        'content_snapshot': v.content_snapshot,
        'author_agent': v.author_agent,
        'change_reason': v.change_reason,
        'trace_id': v.trace_id,
        'created_at': v.created_at.isoformat() if v.created_at else None,
        'deliberation_session_id': str(v.deliberation_session_id) if v.deliberation_session_id else None,
    })
