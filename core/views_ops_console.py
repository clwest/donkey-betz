"""
Session 1077: Ops Console REST endpoints.

Exposes SLO status, failure signatures, and blocked agents as REST
endpoints for the frontend OpsConsoleTab. These were previously only
available through PA tool gateway (ops_tool).
"""

import logging
import re
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@require_GET
@login_required
def slo_status(request):
    """GET /api/ops/slo-status/ — SLO dashboard data."""
    try:
        from core.services.td_handlers_ops import OpsHandlersMixin

        class _Proxy(OpsHandlersMixin):
            pass

        proxy = _Proxy()
        result = proxy._handle_ops(
            'ops_tool',
            {'action': 'slo_status', 'window': '24h'},
            user_id=request.user.id,
            trace_id='ops-console',
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"SLO status error: {e}")
        return JsonResponse({'slos': [], 'error': str(e)})


@require_GET
@login_required
def failure_signatures(request):
    """GET /api/ops/failure-signatures/ — Recent failure patterns."""
    try:
        from core.services.td_handlers_ops import OpsHandlersMixin

        class _Proxy(OpsHandlersMixin):
            pass

        proxy = _Proxy()
        window = request.GET.get('window', '24h')
        limit = int(request.GET.get('limit', 10))
        result = proxy._handle_ops(
            'ops_tool',
            {'action': 'failure_signatures', 'window': window, 'limit': limit},
            user_id=request.user.id,
            trace_id='ops-console',
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Failure signatures error: {e}")
        return JsonResponse({'signatures': [], 'error': str(e)})


@require_GET
@login_required
def blocked_agents(request):
    """GET /api/ops/blocked-agents/ — Currently blocked agents."""
    try:
        from core.models_unified_system import AgentControlEntry
        entries = AgentControlEntry.objects.filter(status='blocked').order_by('-blocked_at')
        blocked = []
        for e in entries:
            blocked.append({
                'agent_name': e.agent_name,
                'reason': e.reason,
                'blocked_by': e.blocked_by,
                'blocked_at': e.blocked_at.isoformat() if e.blocked_at else None,
                'ttl_hours': e.ttl_hours,
            })
        return JsonResponse({'blocked': blocked, 'count': len(blocked)})
    except Exception as e:
        logger.error(f"Blocked agents error: {e}")
        return JsonResponse({'blocked': [], 'error': str(e)})


@require_GET
@login_required
def health_summary(request):
    """GET /api/ops/health-summary/ — S2761 Command Center Ops Health tile.

    Composes the three S2755→S2760 operational-diagnostic surfaces into a
    single last-mile UI payload: current freshness verdict + accumulated
    tenant-boundary violations (I-0303) + accumulated staleness warnings
    (S2759). Window fixed at 24h to match the Rigby round-trip protocol.
    """
    from core.services.td_handlers_ops import OpsHandlersMixin

    class _Proxy(OpsHandlersMixin):
        pass

    proxy = _Proxy()
    user_id = request.user.id
    trace_id = 'ops-console-health'

    def _safe_call(payload, error_key):
        try:
            return proxy._handle_ops('ops_tool', payload, user_id=user_id, trace_id=trace_id)
        except Exception as e:  # noqa: BLE001 — surface degradation, not 500
            logger.warning(f"health_summary {payload.get('action')} failed: {e}")
            return {'error': str(e), '_source': error_key}

    version = _safe_call({'action': 'version'}, 'version')
    tbv = _safe_call({'action': 'tenant_boundary_violations', 'window': '24h', 'limit': 0}, 'tbv')
    stw = _safe_call({'action': 'staleness_warnings', 'window': '24h', 'limit': 0}, 'stw')
    slo = _safe_call({'action': 'slo_status', 'window': '24h'}, 'slo')

    head_sha = (version.get('head_commit_sha') or '')[:12] if isinstance(version, dict) else ''
    slo_summary = _summarize_slos(slo)
    return JsonResponse({
        'window': '24h',
        'verdict': (version.get('staleness_verdict') if isinstance(version, dict) else None) or 'UNKNOWN',
        'head_commit_sha_short': head_sha,
        'tenant_boundary_violations': {
            'total': tbv.get('total_count', 0) if isinstance(tbv, dict) else 0,
            'by_task_name': tbv.get('by_task_name', {}) if isinstance(tbv, dict) else {},
            'by_failure_kind': tbv.get('by_failure_kind', {}) if isinstance(tbv, dict) else {},
        },
        'staleness_warnings': {
            'total': stw.get('total_count', 0) if isinstance(stw, dict) else 0,
            'by_verdict': stw.get('by_verdict', {}) if isinstance(stw, dict) else {},
        },
        'slo_status': slo_summary,
    })


def _summarize_slos(slo_payload) -> dict:
    """S2764: Reduce slo_status list to a compact tile summary.

    Handles the two SLO polarities cleanly: ``target`` present ⇒ lower-is-worse
    (breach gap = target - current); ``target_max`` present ⇒ upper-is-worse
    (breach gap = current - target_max). SLOs missing both directions or
    lacking a numeric ``current`` are counted but excluded from worst-breach
    ranking. Errored SLO entries (``error`` key) do not contribute to totals.
    """
    default = {'total': 0, 'breach_count': 0, 'healthy_count': 0, 'worst_breach': None}
    if not isinstance(slo_payload, dict):
        return default
    slos = slo_payload.get('slos') or []
    if not isinstance(slos, list):
        return default

    total = 0
    breaches = 0
    worst = None
    worst_gap = None
    for s in slos:
        if not isinstance(s, dict) or s.get('error'):
            continue
        total += 1
        if not s.get('breach'):
            continue
        breaches += 1
        current = s.get('current')
        if not isinstance(current, (int, float)):
            continue
        if 'target_max' in s and isinstance(s.get('target_max'), (int, float)):
            gap = current - s['target_max']  # positive when breaching upper bound
            target_display = s['target_max']
        elif 'target' in s and isinstance(s.get('target'), (int, float)):
            gap = s['target'] - current  # positive when below lower bound
            target_display = s['target']
        else:
            continue
        if worst_gap is None or gap > worst_gap:
            worst_gap = gap
            worst = {
                'key': s.get('key'),
                'name': s.get('name'),
                'current': current,
                'target': target_display,
            }
    return {
        'total': total,
        'breach_count': breaches,
        'healthy_count': max(0, total - breaches),
        'worst_breach': worst,
    }


# S2763: fixed filesystem roots for close_ceremony_ledger. Never
# accept a caller-supplied path; only the fixed BASE_DIR/docs/... roots
# are read. Defense-in-depth: resolved paths are checked to be inside
# BASE_DIR before their relative form is emitted.
_HANDOFFS_ROOT = Path(settings.BASE_DIR) / 'docs' / 'handoffs'
_ENVELOPES_ROOT = Path(settings.BASE_DIR) / 'docs' / 'research' / 'implementation'
_SESSION_FILENAME_RE = re.compile(r'^SESSION_(\d+)_')
_H1_TITLE_RE = re.compile(r'^#\s+Session\s+\d+\s+[—-]\s+(.+?)\s*$', re.MULTILINE)
_DATE_LINE_RE = re.compile(r'^\*\*Date:\*\*\s+(\d{4}-\d{2}-\d{2})', re.MULTILINE)
_ENVELOPE_SESSION_RE = re.compile(r'^session_added:\s*(\d+)\s*$', re.MULTILINE)


def _safe_relpath(path: Path) -> str | None:
    """Return path relative to BASE_DIR if it resolves inside BASE_DIR; else None."""
    base = Path(settings.BASE_DIR).resolve()
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        return None
    try:
        rel = resolved.relative_to(base)
    except ValueError:
        return None
    return str(rel)


def _index_envelopes_by_session() -> dict[int, str]:
    """Map session_added → envelope relative path. Only files under _ENVELOPES_ROOT."""
    idx: dict[int, str] = {}
    if not _ENVELOPES_ROOT.exists():
        return idx
    for f in _ENVELOPES_ROOT.glob('RATIFICATION_*.md'):
        rel = _safe_relpath(f)
        if rel is None:
            continue
        try:
            head = f.read_text(errors='replace')[:2000]  # frontmatter block only
        except OSError:
            continue
        m = _ENVELOPE_SESSION_RE.search(head)
        if not m:
            continue
        try:
            session_n = int(m.group(1))
        except ValueError:
            continue
        # keep first match per session_n; later envelopes for same session are rare
        idx.setdefault(session_n, rel)
    return idx


@require_GET
@login_required
def close_ceremony_ledger(request):
    """GET /api/ops/close-ceremony-ledger/?limit=10 — S2763 close-ceremony ledger.

    Returns the last N session handoffs in descending session order, each
    optionally paired with its ratification envelope (matched via the
    envelope's ``session_added:`` frontmatter field).

    Reads filesystem only from fixed roots ``docs/handoffs/`` and
    ``docs/research/implementation/``. No caller-controlled paths; all
    emitted paths are validated to resolve inside ``BASE_DIR``.
    """
    try:
        limit = int(request.GET.get('limit', 10))
    except (TypeError, ValueError):
        limit = 10
    limit = max(1, min(limit, 50))

    if not _HANDOFFS_ROOT.exists():
        return JsonResponse({'items': [], 'count': 0, 'error': 'handoffs root missing'})

    entries: list[tuple[int, Path]] = []
    for f in _HANDOFFS_ROOT.glob('SESSION_*.md'):
        m = _SESSION_FILENAME_RE.match(f.name)
        if not m:
            continue
        try:
            entries.append((int(m.group(1)), f))
        except ValueError:
            continue
    entries.sort(key=lambda t: t[0], reverse=True)
    entries = entries[:limit]

    envelope_idx = _index_envelopes_by_session()
    items = []
    for session_n, path in entries:
        rel = _safe_relpath(path)
        if rel is None:
            continue
        try:
            head = path.read_text(errors='replace')[:4000]
        except OSError:
            continue
        title_m = _H1_TITLE_RE.search(head)
        date_m = _DATE_LINE_RE.search(head)
        envelope_rel = envelope_idx.get(session_n)
        items.append({
            'session_number': session_n,
            'title': title_m.group(1) if title_m else path.stem.replace('_', ' '),
            'date': date_m.group(1) if date_m else None,
            'handoff_path': rel,
            'envelope_path': envelope_rel,
            'envelope_exists': envelope_rel is not None,
        })

    return JsonResponse({
        'items': items,
        'count': len(items),
        'limit': limit,
    })
