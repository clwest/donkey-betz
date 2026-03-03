"""
Session 962 Phase 1 + Session 963 Phase 3: Deliberation API Endpoints
Session 970 Phase 5.1: Verification report endpoint

Provides read-only API access to deliberation sessions, turns, contracts,
doc versions, evidence packs, traces, replay, and verification reports.
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.db.models import Count, Q

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
    DocVersion,
)

logger = logging.getLogger(__name__)


def _get_blog_for_session(session_id):
    """Reverse-lookup SelfBlog linked to a deliberation session via stats_snapshot."""
    try:
        from core.models_unified_system import SelfBlog
        blog = SelfBlog.objects.filter(
            stats_snapshot__deliberation__session_id=str(session_id)
        ).first()
        if blog:
            delib = (blog.stats_snapshot or {}).get('deliberation', {})
            return {
                'blog_title': blog.title,
                'blog_id': str(blog.id),
                'verdict': delib.get('decision'),
                'quality_score': blog.quality_score,
                'structure_score': blog.structure_score,
                'publish_ready': blog.publish_ready,
            }
    except Exception:
        pass
    return None


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
            'failure_reason_code': getattr(s, 'failure_reason_code', '') or '',
            'failure_detail': (getattr(s, 'failure_detail', '') or '')[:300],
            'blog': _get_blog_for_session(s.id),
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


# ---------------------------------------------------------------------------
# Session 963 Phase 3: Evidence Pack, Trace, and Replay endpoints
# ---------------------------------------------------------------------------

@require_GET
def deliberation_evidence(request, session_id):
    """GET /api/deliberation/sessions/<uuid>/evidence/ - Evidence pack JSON."""
    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

    pack = s.evidence_pack or {}
    return JsonResponse({
        'session_id': str(s.id),
        'evidence_pack': pack,
        'stats': {
            'sources': len(pack.get('sources', [])),
            'claims': len(pack.get('claims', [])),
            'contradictions': len(pack.get('contradictions', [])),
            'internal_refs': len(pack.get('internal_refs', [])),
            'memory_retrievals': len(pack.get('memory_retrievals', [])),
            'assembled_at': pack.get('assembled_at'),
        },
    })


@require_GET
def deliberation_trace(request, session_id):
    """GET /api/deliberation/sessions/<uuid>/trace/ - Session trace JSON."""
    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

    trace = s.trace or {}
    return JsonResponse({
        'session_id': str(s.id),
        'trace': trace,
        'stats': {
            'turns': len(trace.get('deliberation', [])),
            'decisions': len(trace.get('decisions', [])),
            'performance': trace.get('performance', {}),
        },
    })


@require_GET
def deliberation_replay(request, session_id):
    """
    GET /api/deliberation/sessions/<uuid>/replay/ - Full replay payload.

    Combines turns (full content), trace, evidence pack, and contracts
    into a single response suitable for UI replay or audit review.
    """
    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

    turns = DeliberationTurn.objects.filter(
        session_id=session_id
    ).order_by('turn_number')

    contracts = ContractRecord.objects.filter(
        session_id=session_id
    ).order_by('created_at')

    turn_data = []
    for t in turns:
        turn_data.append({
            'turn_number': t.turn_number,
            'agent_name': t.agent_name,
            'role': t.role,
            'content': t.content,
            'content_hash': t.content_hash,
            'created_at': t.created_at.isoformat() if t.created_at else None,
        })

    contract_data = []
    for c in contracts:
        contract_data.append({
            'contract_type': c.contract_type,
            'contract_data': c.contract_data,
            'created_at': c.created_at.isoformat() if c.created_at else None,
        })

    return JsonResponse({
        'session_id': str(s.id),
        'session_type': s.session_type,
        'status': s.status,
        'objective': s.objective,
        'participants': s.participants,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'completed_at': s.completed_at.isoformat() if s.completed_at else None,
        'turns': turn_data,
        'contracts': contract_data,
        'trace': s.trace or {},
        'evidence_pack': s.evidence_pack or {},
    })


# ---------------------------------------------------------------------------
# Phase 4: Blog deliberation detail endpoint
# ---------------------------------------------------------------------------

@require_GET
def blog_deliberation_detail(request, blog_id):
    """
    GET /api/blog/<uuid>/deliberation/ — Return deliberation replay for a blog.

    Looks up stats_snapshot['deliberation']['session_id'] on SelfBlog,
    then returns the full replay (turns + evidence + trace) inline.
    """
    try:
        from core.models_unified_system import SelfBlog
        blog = SelfBlog.objects.get(id=blog_id)
    except Exception:
        return JsonResponse({'error': 'Blog not found'}, status=404)

    stats = blog.stats_snapshot or {}
    delib = stats.get('deliberation', {})
    session_id = delib.get('session_id') if isinstance(delib, dict) else None

    if not session_id:
        return JsonResponse({
            'blog_id': str(blog.id),
            'deliberation': None,
            'message': 'No deliberation session linked',
        })

    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({
            'blog_id': str(blog.id),
            'deliberation': None,
            'message': f'Deliberation session {session_id} not found',
        })

    turns = DeliberationTurn.objects.filter(session_id=s.id).order_by('turn_number')
    contracts = ContractRecord.objects.filter(session_id=s.id).order_by('created_at')

    turn_data = [{
        'turn_number': t.turn_number,
        'agent_name': t.agent_name,
        'role': t.role,
        'content': t.content,
        'created_at': t.created_at.isoformat() if t.created_at else None,
    } for t in turns]

    contract_data = [{
        'contract_type': c.contract_type,
        'contract_data': c.contract_data,
        'created_at': c.created_at.isoformat() if c.created_at else None,
    } for c in contracts]

    return JsonResponse({
        'blog_id': str(blog.id),
        'deliberation': {
            'session_id': str(s.id),
            'status': s.status,
            'objective': s.objective,
            'participants': s.participants,
            'decision': delib.get('decision'),
            'review_verdicts': delib.get('review_verdicts', []),
            'turns': turn_data,
            'contracts': contract_data,
            'trace': s.trace or {},
            'evidence_pack': s.evidence_pack or {},
        },
    })


# ---------------------------------------------------------------------------
# Session 970 Phase 5.1: Verification Report endpoint
# ---------------------------------------------------------------------------

@require_GET
def deliberation_verification_report(request, session_id):
    """
    GET /api/deliberation/sessions/<uuid>/verification-report/

    Single-request enriched report combining turns, contracts, evidence stats,
    and verification checks for Surgical Moves Phases 0-3.
    """
    try:
        s = DeliberationSession.objects.get(id=session_id)
    except DeliberationSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

    turns = DeliberationTurn.objects.filter(session_id=s.id).order_by('turn_number')
    contracts = ContractRecord.objects.filter(session_id=s.id).order_by('created_at')
    ep = s.evidence_pack or {}
    trace = s.trace or {}

    turn_count = turns.count()
    agent_names = list(turns.values_list('agent_name', flat=True).distinct())

    contract_list = []
    has_execution_contract = False
    for c in contracts:
        cdata = c.contract_data or {}
        verdict_summary = None
        if c.contract_type == 'execution':
            has_execution_contract = True
            verdict_summary = cdata.get('chosen_path', cdata.get('decision', ''))
            if isinstance(verdict_summary, str):
                verdict_summary = verdict_summary[:200]
        contract_list.append({
            'type': c.contract_type,
            'data_size': len(json.dumps(cdata)),
            'verdict_summary': verdict_summary,
        })

    evidence_stats = {
        'sources': len(ep.get('sources', [])),
        'claims': len(ep.get('claims', [])),
        'contradictions': len(ep.get('contradictions', [])),
        'internal_refs': len(ep.get('internal_refs', [])),
        'memory_retrievals': len(ep.get('memory_retrievals', [])),
    }

    trace_turns = trace.get('deliberation', [])
    trace_decisions = trace.get('decisions', [])

    trace_stats = {
        'turns_recorded': len(trace_turns),
        'has_contracts': len(contract_list) > 0,
        'has_decisions': len(trace_decisions) > 0,
    }

    # Build verification checks
    checks = []

    # Phase 0: Contract serialization
    contract_count = len(contract_list)
    if contract_count > 0:
        total_size = sum(c['data_size'] for c in contract_list)
        checks.append({
            'phase': 'Phase 0',
            'name': 'Contract serialization',
            'status': 'pass',
            'detail': f'{contract_count} records (total {total_size} bytes)',
        })
    else:
        checks.append({
            'phase': 'Phase 0',
            'name': 'Contract serialization',
            'status': 'warn',
            'detail': 'No contracts found',
        })

    # Phase 0: Decision enforcement
    if has_execution_contract:
        exec_contracts = [c for c in contract_list if c['type'] == 'execution']
        verdict = exec_contracts[0]['verdict_summary'] if exec_contracts else ''
        checks.append({
            'phase': 'Phase 0',
            'name': 'Decision enforcement',
            'status': 'pass',
            'detail': f'Execution contract with verdict: {verdict or "present"}',
        })
    else:
        checks.append({
            'phase': 'Phase 0',
            'name': 'Decision enforcement',
            'status': 'warn',
            'detail': 'No execution contract found',
        })

    # Phase 0: Doc read tracking
    internal_ref_count = evidence_stats['internal_refs']
    checks.append({
        'phase': 'Phase 0',
        'name': 'Doc read tracking',
        'status': 'pass' if internal_ref_count > 0 else 'warn',
        'detail': f'{internal_ref_count} internal_refs in evidence pack',
    })

    # Phase 1: Session persistence
    checks.append({
        'phase': 'Phase 1',
        'name': 'DeliberationSession created',
        'status': 'pass' if s.status == 'completed' else 'warn',
        'detail': f'Status: {s.status}',
    })

    checks.append({
        'phase': 'Phase 1',
        'name': 'DeliberationTurn count',
        'status': 'pass' if turn_count > 0 else 'fail',
        'detail': f'{turn_count} turns',
    })

    checks.append({
        'phase': 'Phase 1',
        'name': 'ContractRecord count',
        'status': 'pass' if contract_count > 0 else 'warn',
        'detail': f'{contract_count} contracts',
    })

    # Phase 3: Evidence pack
    evidence_total = sum(evidence_stats.values())
    checks.append({
        'phase': 'Phase 3',
        'name': 'Evidence pack',
        'status': 'pass' if evidence_total > 0 else 'warn',
        'detail': (
            f'{evidence_stats["sources"]} sources, '
            f'{evidence_stats["claims"]} claims, '
            f'{evidence_stats["contradictions"]} contradictions, '
            f'{evidence_stats["internal_refs"]} internal_refs'
        ),
    })

    # Phase 3: Session trace
    checks.append({
        'phase': 'Phase 3',
        'name': 'Session trace',
        'status': 'pass' if len(trace_turns) > 0 else 'warn',
        'detail': f'{len(trace_turns)} turns recorded',
    })

    # Phase 3: Memory retrievals
    mem_count = evidence_stats['memory_retrievals']
    checks.append({
        'phase': 'Phase 3',
        'name': 'Memory retrievals',
        'status': 'pass' if mem_count > 0 else 'warn',
        'detail': f'{mem_count} retrievals',
    })

    return JsonResponse({
        'session': {
            'id': str(s.id),
            'status': s.status,
            'objective': s.objective,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'completed_at': s.completed_at.isoformat() if s.completed_at else None,
            'participant_count': len(s.participants) if s.participants else 0,
        },
        'blog': _get_blog_for_session(s.id),
        'turns': {
            'count': turn_count,
            'agents': agent_names,
        },
        'contracts': contract_list,
        'evidence_stats': evidence_stats,
        'trace_stats': trace_stats,
        'checks': checks,
    })


# ---------------------------------------------------------------------------
# Failure Stats
# ---------------------------------------------------------------------------

@require_GET
def deliberation_failure_stats(request):
    """
    GET /api/deliberation/failure-stats/
    Aggregated failure breakdown for the last N hours (default 24).
    Returns counts per failure_reason_code and recent failed sessions.
    """
    from datetime import timedelta
    from django.utils import timezone

    hours = min(int(request.GET.get('hours', 24)), 168)  # max 7 days
    cutoff = timezone.now() - timedelta(hours=hours)

    failed_qs = DeliberationSession.objects.filter(
        status='failed',
        created_at__gte=cutoff,
    )

    # Count by reason code
    reason_counts = {}
    for s in failed_qs.values('failure_reason_code'):
        code = s['failure_reason_code'] or 'UNKNOWN'
        reason_counts[code] = reason_counts.get(code, 0) + 1

    total_failed = sum(reason_counts.values())
    total_sessions = DeliberationSession.objects.filter(
        created_at__gte=cutoff,
    ).count()

    # Recent failures (last 10)
    recent = failed_qs.order_by('-created_at')[:10]
    recent_list = [
        {
            'id': str(s.id),
            'objective': (s.objective or '')[:150],
            'failure_reason_code': getattr(s, 'failure_reason_code', '') or 'UNKNOWN',
            'failure_detail': (getattr(s, 'failure_detail', '') or '')[:200],
            'created_at': s.created_at.isoformat() if s.created_at else None,
        }
        for s in recent
    ]

    return JsonResponse({
        'hours': hours,
        'total_sessions': total_sessions,
        'total_failed': total_failed,
        'failure_rate': round(total_failed / total_sessions, 3) if total_sessions else 0,
        'by_reason': reason_counts,
        'recent_failures': recent_list,
    })
