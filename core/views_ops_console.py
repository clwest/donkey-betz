"""
Session 1077: Ops Console REST endpoints.

Exposes SLO status, failure signatures, and blocked agents as REST
endpoints for the frontend OpsConsoleTab. These were previously only
available through PA tool gateway (ops_tool).

────────────────────────────────────────────────────────────────────────
S2772 N16 Ops-Endpoint Scope Policy (ratified by Chris; Rigby Q3 #1)

Every view in this module SHALL:

  1. Be aggregate / read-only. No mutation endpoints; no side effects
     beyond logging and cache reads. Never accept POST/PUT/PATCH/DELETE.
  2. Return no raw DB dumps, no secrets, no user content (chat bodies,
     PA conversation payloads, deliverable bodies except those already
     public per auth_middleware.py:436 registration).
  3. Reject unknown query parameters via `_reject_unknown_query_params`
     with the endpoint's `_OPS_ALLOWED_PARAMS__<NAME>` frozenset (S2773
     N18v2). Every endpoint that accepts query params declares an
     allowlist constant; endpoints that accept none declare an empty
     frozenset. Unknown params → 400 with `code='unknown_query_params'`
     and machine-readable `{unknown, allowed}` body. Never evaluate
     arbitrary strings.
  4. Require both `@login_required` AND `@user_passes_test(is_staff)`.
     Anon → 302 (redirect to login). Authenticated-non-staff → 403.
     Authenticated-staff → 200. Auth-regression tests in
     `core/tests/test_ops_auth_regression_2772.py` lock this contract.
  5. Fail soft on downstream error — degrade the response, do not 500.
     Upstream health tile survival takes priority over precise fidelity.
  6. If composing sub-calls (e.g. health_summary), call the underlying
     handler FUNCTIONS directly, never HTTP-loop through the URL router.

Adding a new /api/ops/* endpoint? MUST also add matching
`test_<name>_blocks_anonymous` + `test_<name>_blocks_non_staff` methods
to the auth-regression test file. The inventory guard test in that
file will fail loudly if you forget.
────────────────────────────────────────────────────────────────────────
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required, user_passes_test

# S2772 N16 (Chris-ratified per Rigby Q3 #2): staff-only gate for ops
# endpoints. Layered with @login_required so both anon and non-staff
# users get redirected to LOGIN_URL (302). The auth-regression test
# suite (`core/tests/test_ops_auth_regression_2772.py`) accepts any of
# {302, 401, 403} as blocking evidence, so both fail-paths are correctly
# guarded. Order matters — @login_required MUST be the outer decorator
# so anon short-circuits at the auth check before this test runs.
_ops_staff_only = user_passes_test(
    lambda u: u.is_authenticated and u.is_staff,
)


# S2773 N18v2 (Rigby Q3 #2): per-endpoint query-param allowlists.
# Every ops endpoint declares its accepted query params as a frozenset
# constant with the `_OPS_ALLOWED_PARAMS__<ENDPOINT>` prefix — the
# shared naming convention lets meta-tests enumerate + validate them
# in bulk (Rigby Q2 nudge). Endpoints that accept no params declare
# an empty frozenset — they'll still reject arbitrary keys via
# `_reject_unknown_query_params`.
_OPS_ALLOWED_PARAMS__SLO_STATUS: frozenset[str] = frozenset()
_OPS_ALLOWED_PARAMS__FAILURE_SIGNATURES: frozenset[str] = frozenset({'window', 'limit'})
_OPS_ALLOWED_PARAMS__BLOCKED_AGENTS: frozenset[str] = frozenset()
_OPS_ALLOWED_PARAMS__HEALTH_SUMMARY: frozenset[str] = frozenset()
_OPS_ALLOWED_PARAMS__CLOSE_CEREMONY_LEDGER: frozenset[str] = frozenset({
    'limit',
    'session_min',
    'session_max',
    'envelope_only',
    'date_from',
    'date_to',
    'text',
})
_OPS_ALLOWED_PARAMS__RECENT_RECYCLES: frozenset[str] = frozenset({'limit'})


def _reject_unknown_query_params(
    request,
    allowed: frozenset[str],
) -> JsonResponse | None:
    """S2773 N18v2 (Rigby Q3 #2 mitigation): reject unknown ?params with 400.

    Returns a JsonResponse to short-circuit the view on drift, or None
    if all query params are recognized. Response body carries a machine-
    stable `code` field so downstream test/UI code doesn't couple to the
    English error string (Rigby Q1 MODIFY).

    Silently ignoring unknown params (the pre-S2773 default) makes it
    too easy for a debugging shortcut like ?raw=1 or ?include_body=1 to
    leak into production and become an exfiltration vector. Mechanical
    enforcement in the helper means the policy in the module docstring
    stops being "on paper only."
    """
    supplied = set(request.GET.keys())
    unknown = supplied - allowed
    if not unknown:
        return None
    return JsonResponse(
        {
            'error': 'Unknown query parameter(s)',
            'code': 'unknown_query_params',
            'unknown': sorted(unknown),
            'allowed': sorted(allowed),
        },
        status=400,
    )


def _call_ops_tool(
    request,
    payload: Dict[str, Any],
    trace_id: str = 'ops-console',
) -> Dict[str, Any]:
    """S2773 N18v2 (Rigby Q3 #1): shared ops_tool dispatch helper.

    Replaces the four-copy `_Proxy(OpsHandlersMixin)` boilerplate that
    slo_status / failure_signatures / health_summary / recent_recycles
    each carried. Callers pass the full payload dict (Rigby Q1 PASS —
    keeps the helper dumb and free of a mini-DSL). Returns the raw dict
    from `_handle_ops`, coerced to `{}` if the handler produced a
    non-dict (defensive; upstream contract is dict-valued).
    """
    from core.services.td_handlers_ops import OpsHandlersMixin

    class _Proxy(OpsHandlersMixin):
        pass

    proxy = _Proxy()
    result = proxy._handle_ops(
        'ops_tool',
        payload,
        user_id=request.user.id,
        trace_id=trace_id,
    )
    return result if isinstance(result, dict) else {}

logger = logging.getLogger(__name__)


@require_GET
@login_required
@_ops_staff_only
def slo_status(request):
    """GET /api/ops/slo-status/ — SLO dashboard data."""
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__SLO_STATUS)
    if reject is not None:
        return reject
    try:
        result = _call_ops_tool(request, {'action': 'slo_status', 'window': '24h'})
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"SLO status error: {e}")
        return JsonResponse({'slos': [], 'error': str(e)})


@require_GET
@login_required
@_ops_staff_only
def failure_signatures(request):
    """GET /api/ops/failure-signatures/ — Recent failure patterns."""
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__FAILURE_SIGNATURES)
    if reject is not None:
        return reject
    try:
        window = request.GET.get('window', '24h')
        limit = int(request.GET.get('limit', 10))
        result = _call_ops_tool(
            request,
            {'action': 'failure_signatures', 'window': window, 'limit': limit},
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Failure signatures error: {e}")
        return JsonResponse({'signatures': [], 'error': str(e)})


@require_GET
@login_required
@_ops_staff_only
def blocked_agents(request):
    """GET /api/ops/blocked-agents/ — Currently blocked agents."""
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__BLOCKED_AGENTS)
    if reject is not None:
        return reject
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
@_ops_staff_only
def health_summary(request):
    """GET /api/ops/health-summary/ — S2761 Command Center Ops Health tile.

    Composes the three S2755→S2760 operational-diagnostic surfaces into a
    single last-mile UI payload: current freshness verdict + accumulated
    tenant-boundary violations (I-0303) + accumulated staleness warnings
    (S2759). Window fixed at 24h to match the Rigby round-trip protocol.
    """
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__HEALTH_SUMMARY)
    if reject is not None:
        return reject

    def _safe_call(payload, error_key):
        try:
            return _call_ops_tool(request, payload, trace_id='ops-console-health')
        except Exception as e:  # noqa: BLE001 — surface degradation, not 500
            logger.warning(f"health_summary {payload.get('action')} failed: {e}")
            return {'error': str(e), '_source': error_key}

    version = _safe_call({'action': 'version'}, 'version')
    tbv = _safe_call({'action': 'tenant_boundary_violations', 'window': '24h', 'limit': 0}, 'tbv')
    stw = _safe_call({'action': 'staleness_warnings', 'window': '24h', 'limit': 0}, 'stw')
    slo = _safe_call({'action': 'slo_status', 'window': '24h'}, 'slo')
    # S2770 N11: fetch newest recycle event so we can override verdict to
    # PARTIAL_RECYCLE when the operator's most recent recycle was partial
    # (some role's PID survived) AND base verdict is currently stale.
    recycles = _safe_call({'action': 'recent_recycles', 'limit': 1}, 'recycles')

    head_sha = (version.get('head_commit_sha') or '')[:12] if isinstance(version, dict) else ''
    slo_summary = _summarize_slos(slo)
    base_verdict = (version.get('staleness_verdict') if isinstance(version, dict) else None) or 'UNKNOWN'

    # S2770 N11: PARTIAL_RECYCLE override.
    # Fires only when:
    #   - base verdict is a STALE_* variant (real operator pain right now)
    #   - AND newest recycle event has partial_recycle=true (N7 evidence)
    # Legacy pre-N7 rows lack the field; treated as False via .get() default
    # so pre-N7 history doesn't falsely alarm.
    verdict = base_verdict
    partial_details: Dict[str, Any] | None = None
    if base_verdict in ('STALE_DAPHNE', 'STALE_CELERY', 'STALE_BOTH') and isinstance(recycles, dict):
        items = recycles.get('items') or []
        newest = items[0] if items else None
        if isinstance(newest, dict) and newest.get('partial_recycle') is True:
            verdict = 'PARTIAL_RECYCLE'
            partial_details = {
                'surviving_processes': newest.get('surviving_processes') or [],
                'recycle_sha_short': newest.get('sha_short') or '',
            }

    payload: Dict[str, Any] = {
        'window': '24h',
        'verdict': verdict,
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
    }
    if partial_details is not None:
        payload['partial_recycle_details'] = partial_details
    return JsonResponse(payload)


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
# S2769 N8: match both `**Date:** YYYY-MM-DD` markdown (older handoffs)
# and `date: YYYY-MM-DD` YAML frontmatter (S2767+ handoffs).
_DATE_LINE_RE = re.compile(
    r'^(?:\*\*Date:\*\*\s+|date:\s+)(\d{4}-\d{2}-\d{2})',
    re.MULTILINE,
)
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


def _parse_int_param(raw: str | None) -> int | None:
    """Parse a query-string int; return None on missing/blank/invalid."""
    if raw is None or raw == '':
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _parse_date_param(raw: str | None) -> str | None:
    """Return raw string if it matches YYYY-MM-DD; else None."""
    if raw is None or raw == '':
        return None
    if len(raw) == 10 and raw[4] == '-' and raw[7] == '-':
        try:
            int(raw[:4]); int(raw[5:7]); int(raw[8:10])
            return raw
        except ValueError:
            return None
    return None


@require_GET
@login_required
@_ops_staff_only
def close_ceremony_ledger(request):
    """GET /api/ops/close-ceremony-ledger/ — S2763 close-ceremony ledger + S2769 filters + S2771 text search.

    Query params (all optional):

    - ``limit`` (int, 1..50, default 10): max items returned after filtering.
    - ``session_min`` (int): include only sessions with number >= this.
    - ``session_max`` (int): include only sessions with number <= this.
    - ``envelope_only`` (bool, default false): include only entries whose
      envelope exists.
    - ``date_from`` / ``date_to`` (YYYY-MM-DD): filter by the parsed
      ``**Date:**`` line in the handoff body. Undated entries are excluded
      when either date filter is set.
    - ``text`` (str, S2771 N14): include only entries whose handoff body
      contains the case-insensitive substring. Each returned item gains a
      ``text_match_count`` field. Applied AFTER cheap filters so full-body
      reads only happen for already-narrowed entries.

    Returns items sorted by session number descending, each optionally
    paired with its ratification envelope (matched via the envelope's
    ``session_added:`` frontmatter field). Includes ``total_available``
    (pre-limit filter-matching count) so the UI can offer "showing X of Y".

    Reads filesystem only from fixed roots ``docs/handoffs/`` and
    ``docs/research/implementation/``. No caller-controlled paths; all
    emitted paths are validated to resolve inside ``BASE_DIR``.
    """
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__CLOSE_CEREMONY_LEDGER)
    if reject is not None:
        return reject
    try:
        limit = int(request.GET.get('limit', 10))
    except (TypeError, ValueError):
        limit = 10
    limit = max(1, min(limit, 50))

    # S2769 N8 filter params — all optional; None means "no filter"
    session_min = _parse_int_param(request.GET.get('session_min'))
    session_max = _parse_int_param(request.GET.get('session_max'))
    envelope_only = request.GET.get('envelope_only', '').lower() in ('true', '1', 'yes')
    date_from = _parse_date_param(request.GET.get('date_from'))
    date_to = _parse_date_param(request.GET.get('date_to'))
    date_filter_active = date_from is not None or date_to is not None
    # S2771 N14 text search — case-insensitive; applied AFTER cheap filters.
    # Blank string means "no filter" (same as absent param).
    text_raw = (request.GET.get('text') or '').strip()
    text_needle = text_raw.lower() if text_raw else None

    if not _HANDOFFS_ROOT.exists():
        return JsonResponse({
            'items': [], 'count': 0, 'total_available': 0, 'limit': limit,
            'error': 'handoffs root missing',
        })

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

    envelope_idx = _index_envelopes_by_session()

    # S2769 N8: two-pass — build full filtered set (for total_available),
    # then slice by limit. Reading handoff bodies for title+date is done
    # only for entries that pass session_number + envelope filters, so
    # cheap filters short-circuit the expensive body read.
    matched: list[dict] = []
    for session_n, path in entries:
        if session_min is not None and session_n < session_min:
            continue
        if session_max is not None and session_n > session_max:
            continue
        envelope_rel = envelope_idx.get(session_n)
        envelope_exists = envelope_rel is not None
        if envelope_only and not envelope_exists:
            continue

        rel = _safe_relpath(path)
        if rel is None:
            continue
        try:
            head = path.read_text(errors='replace')[:4000]
        except OSError:
            continue
        title_m = _H1_TITLE_RE.search(head)
        date_m = _DATE_LINE_RE.search(head)
        parsed_date = date_m.group(1) if date_m else None

        if date_filter_active:
            if parsed_date is None:
                # exclude undated entries when a date filter is set
                continue
            if date_from is not None and parsed_date < date_from:
                continue
            if date_to is not None and parsed_date > date_to:
                continue

        matched.append({
            'session_number': session_n,
            'title': title_m.group(1) if title_m else path.stem.replace('_', ' '),
            'date': parsed_date,
            'handoff_path': rel,
            'envelope_path': envelope_rel,
            'envelope_exists': envelope_exists,
            '_path': path,  # internal only — stripped before response
        })

    # S2771 N14 text-search phase — runs only when text is set. Reads the
    # full body of each already-narrowed entry (cheap filters have done
    # their job), does case-insensitive substring count, drops zeros,
    # adds text_match_count. Fail-soft on unopenable files; skipped_count
    # tracks silent IO failures so partial results are traceable
    # (Rigby S2771 meta-critique addressed).
    text_skipped_count = 0
    if text_needle is not None:
        text_matched: list[dict] = []
        for entry in matched:
            path: Path = entry['_path']
            try:
                body = path.read_text(errors='replace')
            except OSError:
                text_skipped_count += 1
                continue
            count = body.lower().count(text_needle)
            if count > 0:
                entry['text_match_count'] = count
                text_matched.append(entry)
        matched = text_matched

    # Strip internal _path key before returning.
    for entry in matched:
        entry.pop('_path', None)

    total_available = len(matched)
    items = matched[:limit]

    # S2771 N14 (Rigby meta-critique): echo applied filters so operators
    # and UI can see exactly what fired without re-parsing the query
    # string. Also surface skipped_count when text scan hit unopenable
    # files — silent partial results become traceable.
    applied_filters: Dict[str, Any] = {}
    if session_min is not None:
        applied_filters['session_min'] = session_min
    if session_max is not None:
        applied_filters['session_max'] = session_max
    if envelope_only:
        applied_filters['envelope_only'] = True
    if date_from is not None:
        applied_filters['date_from'] = date_from
    if date_to is not None:
        applied_filters['date_to'] = date_to
    if text_needle is not None:
        applied_filters['text'] = text_raw

    response_payload: Dict[str, Any] = {
        'items': items,
        'count': len(items),
        'total_available': total_available,
        'limit': limit,
        'applied_filters': applied_filters,
    }
    if text_needle is not None:
        response_payload['skipped_count'] = text_skipped_count
    return JsonResponse(response_payload)


@require_GET
@login_required
@_ops_staff_only
def recent_recycles(request):
    """GET /api/ops/recent-recycles/?limit=<N> — S2765 recycle events timeline.

    Thin REST wrapper over ``ops_tool.recent_recycles`` handler for the
    Ops Console frontend. Same fail-soft + defensive-parse discipline;
    same fixed-root safety (handler resolves ``logs/recycle_events.jsonl``
    against ``BASE_DIR``).
    """
    reject = _reject_unknown_query_params(request, _OPS_ALLOWED_PARAMS__RECENT_RECYCLES)
    if reject is not None:
        return reject
    try:
        limit = int(request.GET.get('limit', 10))
        result = _call_ops_tool(request, {'action': 'recent_recycles', 'limit': limit})
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Recent recycles error: {e}")
        return JsonResponse({'items': [], 'count': 0, 'log_exists': False, 'error': str(e)})
