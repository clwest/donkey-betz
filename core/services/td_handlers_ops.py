"""
ToolDispatcher OpsHandlersMixin — extracted handler methods.
"""
from core.services.pa_identity import PA_IDENTITY


def _d14_resolve_min_session(raw):
    """Session 1234 D14 — LLM-autofill guard for the min_session filter.

    The LLM autofills integer params with 0 the same way it autofills
    boolean params with False (memory:
    feedback_llm_autofills_boolean_params_with_false). A min_session=0
    silently filters the corpus to handoffs-only (since only handoffs
    carry session-N tags); combined with the similarity floor it often
    returns 0 results when the user didn't intend any filter.

    Contract: return the int only when > 0; otherwise None (no filter).
    """
    if raw is None:
        return None
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def _resolve_originating_session(raw):
    """Session 2728 F-SD-1 — LLM-autofill guard for the originating_session
    filter on search_docs.

    Same pattern as `_d14_resolve_min_session` for kb_tool's min_session. The
    LLM autofills `originating_session=0` and the pre-patch handler applied
    a "restrict to session 0" filter, which silently returned zero results
    for every RAG query the LLM did not explicitly session-scope. This was
    documented in memory rule `feedback_ratification_workflow_gotchas` with
    the workaround "use kb_tool instead" — the workaround becomes obsolete
    once this guard is in place.

    Contract: return the int only when > 0; otherwise None (no filter).
    Chris ratified the positive-only shape at Batch A tool 3 close.
    """
    if raw is None:
        return None
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None

"""
Tool Dispatcher - Centralized Tool Execution with No Silent Failures
=====================================================================

Session 931: Created to solve the "tool exists != tool works" problem.

Every tool call goes through this dispatcher which:
1. Wraps execution in try/catch
2. Measures latency
3. Generates trace_id for debugging
4. Returns structured result (never fails silently)

Usage:
    from core.services.tool_dispatcher import get_tool_dispatcher

    dispatcher = get_tool_dispatcher()
    result = await dispatcher.execute(
        tool_name="human_decisions_tool",
        payload={"action": "list"},
        user_id=user.id
    )

    # Result is always structured:
    # {
    #     "ok": True/False,
    #     "tool": "human_decisions_tool",
    #     "latency_ms": 234,
    #     "error_code": None,
    #     "error_message": None,
    #     "trace_id": "abc123",
    #     "result": {...}
    # }
"""

import json
import logging
import time
import uuid
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps, lru_cache

logger = logging.getLogger(__name__)


# Session 1145 P2: provenance index for search_docs originating_session filter.
PROVENANCE_INDEX_PATH = Path("docs/_provenance.json")


@lru_cache(maxsize=1)
def _load_provenance_docs() -> dict:
    """Load ``docs/_provenance.json`` once per process; return ``docs`` block.

    Returns an empty dict if the file is missing or invalid — search_docs
    treats "no provenance for path" as "exclude when filter is active",
    so a missing index degrades gracefully (filter just excludes
    everything, surfacing the regen hint to the user).
    """
    if not PROVENANCE_INDEX_PATH.exists():
        return {}
    try:
        data = json.loads(PROVENANCE_INDEX_PATH.read_text(encoding="utf-8"))
        return data.get("docs", {}) or {}
    except (OSError, json.JSONDecodeError):
        return {}


def _filter_chunks_by_originating_session(
    chunks: list, originating_session: int, provenance_docs: dict
) -> tuple[list, int, int]:
    """Filter ranked chunks by source-doc originating_session.

    Returns ``(kept, excluded_with_mismatch, excluded_missing_provenance)``.

    Missing provenance is treated as exclusion when the filter is active
    (per Rigby spec, Session 1145 P2): we can't claim a chunk belongs to
    a session if we don't know its origin.

    Pure function — chunks are dicts with a ``file`` key carrying the
    ``docs/...`` cite path used in ``provenance.docs`` keys.
    """
    kept: list = []
    mismatch = 0
    missing = 0
    for c in chunks:
        path = c.get("file") if isinstance(c, dict) else None
        if not path:
            missing += 1
            continue
        meta = provenance_docs.get(path)
        if not meta:
            missing += 1
            continue
        if meta.get("originating_session") == originating_session:
            kept.append(c)
        else:
            mismatch += 1
    return kept, mismatch, missing


# Error codes for structured failures
class ToolErrorCode:
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_EXCEPTION = "TOOL_EXCEPTION"
    TOOL_INVALID_PAYLOAD = "TOOL_INVALID_PAYLOAD"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    TOOL_DEPENDENCY_FAILED = "TOOL_DEPENDENCY_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)




class OpsHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    def _handle_ops(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1078: Production ops surface — version, SLO status, failure signatures.
        Separate from status_snapshot_tool to keep snapshot cheap and fast.
        """
        action = payload.get('action', 'version')

        if action == 'overview':
            # Session 1103c: one-shot ops snapshot bundling version +
            # slo_status + top failure_signatures + noise_metrics.
            # Added because GPT-5.2 kept emitting action='overview' as
            # a natural guess for 'how is production doing' questions
            # and the dispatcher was returning 'Unknown action' every
            # time. Bundling keeps it to a single tool call so Rigby
            # can answer ops status without burning a multi-step loop.
            window = payload.get('window', '24h')
            result = {'gateway': 'ops_tool', 'action': 'overview', 'window': window}
            try:
                result['version'] = self._ops_version(trace_id)
            except Exception as e:
                result['version'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                result['slo_status'] = self._ops_slo_status(
                    window, False, trace_id, since=None,
                )
            except Exception as e:
                result['slo_status'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                result['queue_pressure'] = self._ops_queue_pressure_rollup(
                    user_id, trace_id,
                )
            except Exception as e:
                result['queue_pressure'] = {
                    'overall_state': 'UNKNOWN',
                    'error': f'{type(e).__name__}: {str(e)[:200]}',
                }
            try:
                result['memory_pressure'] = self._ops_memory_pressure_rollup(trace_id)
            except Exception as e:
                result['memory_pressure'] = {
                    'overall_state': 'UNKNOWN',
                    'error': f'{type(e).__name__}: {str(e)[:200]}',
                }
            try:
                result['failure_signatures'] = self._ops_failure_signatures(
                    window, 5, trace_id, since=None,
                )
            except Exception as e:
                result['failure_signatures'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                from core.services.noise_metrics import compute_runs_metrics
                hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
                result['noise_metrics'] = compute_runs_metrics(hours=hours)
            except Exception as e:
                result['noise_metrics'] = {'error': f'{type(e).__name__}: {e}'}
            return result

        if action == 'version':
            return self._ops_version(trace_id)
        elif action == 'slo_status':
            window = payload.get('window', '24h')
            include_breakdowns = payload.get('include_breakdowns', False)
            since = payload.get('since')  # Session 1080: ISO-8601 override
            return self._ops_slo_status(window, include_breakdowns, trace_id, since=since)
        elif action == 'failure_signatures':
            window = payload.get('window', '24h')
            limit = min(int(payload.get('limit', 10)), 25)
            since = payload.get('since')  # Session 1080: ISO-8601 override
            return self._ops_failure_signatures(window, limit, trace_id, since=since)
        elif action == 'tool_migration_report':
            window = payload.get('window', '7d')
            return self._ops_tool_migration_report(window, trace_id)

        elif action == 'timeout_config_read':
            # Session 1098: Read agent wall-clock timeout config (code defaults + DB overrides)
            agent_names = payload.get('agent_names', [])
            return self._ops_timeout_config_read(agent_names, trace_id)

        elif action == 'proof_bundle':
            # Session 1098: Verification mode — returns timeout config + audit log
            # for specified agents in a single call. Read-only, no mutations.
            agent_names = payload.get('agent_names', [])
            initiative_id = payload.get('initiative_id')
            return self._ops_proof_bundle(agent_names, initiative_id, trace_id)

        elif action == 'beat_schedule':
            # Session 1100: Proxy to cockpit_tool for beat schedule
            return self._handle_cockpit('cockpit_tool', {'action': 'beat_schedule', 'limit': payload.get('limit', 20)}, user_id, trace_id)

        elif action == 'noise_metrics':
            # Session 1077: North Star coverage + run noise breakdown
            from core.services.noise_metrics import compute_runs_metrics
            window = payload.get('window', '24h')
            hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            return compute_runs_metrics(hours=hours)

        elif action == 'conversation_metrics':
            # Session 1077: Topic clustering + zombie rate
            from core.services.noise_metrics import compute_conversation_metrics
            window = payload.get('window', '24h')
            hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            return compute_conversation_metrics(hours=hours)

        elif action == 'focus_mode_status':
            # Session 1077: Read Focus Mode config
            from core.services.focus_mode import get_status
            return {'action': 'focus_mode_status', **get_status()}

        elif action == 'focus_mode_update':
            # Session 1077: Update Focus Mode config
            from core.services.focus_mode import set_config, get_status
            config_updates = payload.get('config_updates', {})
            if not config_updates:
                return {'error': 'config_updates dict required'}
            set_config(config_updates)
            return {'action': 'focus_mode_update', 'applied': list(config_updates.keys()), **get_status()}

        elif action == 'celery_task_history':
            # Session 1100: Query recent Celery task runs (success + failure)
            return self._ops_celery_task_history(payload, trace_id)

        elif action == 'execution_detail':
            # Session 1100: Look up a single AgentExecution by ID (includes heartbeat)
            return self._ops_execution_detail(payload, trace_id)

        elif action == 'execution_search':
            # Session 1100: Search recent executions by agent name / status
            return self._ops_execution_search(payload, trace_id)

        elif action == 'memory_pressure':
            # Session 1167: COO Nervous System Backlog item #5. Reads
            # the latest snapshot from logs/worker_memory/*.jsonl (the
            # cadence task is single-source-of-truth for sampling and
            # thresholds). No re-sampling here — reduce-from-JSONL.
            return self._ops_memory_pressure(trace_id)

        elif action == 'top_consumers':
            # Session 1167: COO Nervous System Backlog item #7. Per
            # task_name aggregation over CeleryTaskEvent.duration_seconds
            # for one window (default 24h). p95 computed server-side via
            # PostgreSQL percentile_cont — single aggregate query.
            # Session 1169: optional group_by='agent' switches the
            # dimension to the new agent_name field (populated by the
            # task_prerun signal). Default group_by='task' preserves
            # backwards-compatible behavior.
            window = payload.get('window', '24h')
            limit = payload.get('limit')
            group_by = payload.get('group_by', 'task')
            return self._ops_top_consumers(window, limit, trace_id, group_by=group_by)

        elif action == 'zombie_thread_rate':
            # Session 1220 P1: surface the wall-clock-timeout incidence
            # captured by core/services/zombie_thread_monitor. Each fire
            # spawns a zombie thread (Phase 3 deliverable cf80d413-…)
            # that keeps running until the agent body returns naturally
            # or the Celery child recycles. Spikes indicate a structural
            # hang (e.g., upstream LLM provider degraded), not a one-off
            # timeout. Suggested alert threshold: >5/hour for any single
            # agent.
            from core.services.zombie_thread_monitor import get_zombie_rate
            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            agent_name = payload.get('agent_name') or None
            result = get_zombie_rate(hours=hours, agent_name=agent_name)
            return {'action': 'zombie_thread_rate', **result}

        elif action == 'tenant_boundary_violations':
            # S2758: surface I-0303 REPORT-ONLY substrate findings from
            # OpsRunEvent. Diagnostic reads on the tenant_boundary_violation
            # envelope with the discriminator preserved (row_id +
            # acting_user_id + support_code + trace_id) — internal operator
            # surface per Phase 2 §2.1 uniform-envelope design.
            return self._ops_tenant_boundary_violations(payload, trace_id)

        elif action == 'staleness_warnings':
            # S2760: surface S2759 stale-process warnings from OpsRunEvent.
            # Complements the live ops_tool.version staleness_verdict — this
            # action reads the accumulated warning history from the 30-min
            # check_process_staleness Beat task. Aggregates by verdict class
            # + head_commit_sha so operators can answer 'which merge did we
            # forget to recycle after?'.
            return self._ops_staleness_warnings(payload, trace_id)

        elif action == 'recent_recycles':
            # S2765: read logs/recycle_events.jsonl — the tail of
            # `make recycle-all` events emitted by the Makefile after each
            # local deploy step. Answers 'when did we last recycle?' and
            # 'which SHAs was the stack recycled at?'. Complements
            # ops_tool.version (live snapshot) + ops_tool.staleness_warnings
            # (Beat-emitted post-hoc detection) with a first-party operator
            # action timeline.
            return self._ops_recent_recycles(payload, trace_id)

        else:
            return {'error': f'Unknown ops_tool action: {action}'}

    def _ops_version(self, trace_id: str) -> Dict[str, Any]:
        """Return build/deploy metadata for the running process.

        S2759 extension: staleness detection. Compares Daphne + Celery worker
        process start times against ``git HEAD`` commit time. Any process
        started BEFORE the current HEAD commit is running pre-merge code —
        typical failure mode: view-layer changes silently unused for hours
        after a close-ceremony merge. See ``feedback_local_truth_no_production``
        memory rule.
        """
        import os
        import time
        import django
        from datetime import timedelta

        _boot_time = getattr(self, '_boot_time', None)
        if not _boot_time:
            self._boot_time = time.time()
            _boot_time = self._boot_time

        from django.utils import timezone

        now = timezone.now()
        uptime_seconds = time.time() - _boot_time

        # S2759 staleness detection block (fails soft: any exception yields
        # verdict=UNKNOWN so ops_tool.version stays useful even when the
        # freshness signal is unavailable).
        try:
            staleness = self._compute_process_staleness()
        except Exception as e:  # noqa: BLE001 — best-effort diagnostic
            logger.warning(
                'ops_tool.version staleness computation failed (swallowed): %s',
                e,
                exc_info=True,
            )
            staleness = {
                'staleness_verdict': 'UNKNOWN',
                'staleness_error': f'{type(e).__name__}: {e}',
            }

        return {
            'action': 'version',
            'service': os.environ.get('RAILWAY_SERVICE_NAME', 'unknown'),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
            'git': {
                'sha': os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'dev'),
                'branch': os.environ.get('RAILWAY_GIT_BRANCH', 'unknown'),
            },
            'railway': {
                'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
            },
            'runtime': {
                'started_at': (now - timedelta(seconds=uptime_seconds)).isoformat(),
                'uptime_seconds': round(uptime_seconds),
            },
            'app': {
                'django_version': django.get_version(),
            },
            **staleness,
        }

    _DAPHNE_PROCESS_PATTERN = 'daphne'
    _CELERY_WORKER_PROCESS_PATTERN = 'celery.*worker'

    def _compute_process_staleness(self) -> Dict[str, Any]:
        """Delegates to ``core.services.process_freshness.compute_process_staleness``.

        S2775 N15 extracted the body to a module-level function so
        callers outside the tool-dispatch lifecycle (specifically
        ``session_lifecycle`` for freshness telemetry) can invoke the
        same computation without instantiating this handler. Return
        shape is byte-identical to pre-extraction.
        """
        from core.services.process_freshness import compute_process_staleness
        return compute_process_staleness()

    def _ops_slo_status(self, window: str, include_breakdowns: bool, trace_id: str, since: str = None) -> Dict[str, Any]:
        """Compute 8 SLOs for the given time window."""
        from django.utils import timezone
        from django.core.cache import cache
        from django.db.models import Count
        from datetime import timedelta, datetime

        # Session 1080: since_timestamp overrides window
        if since:
            cache_key = f'pa:ops_slo:since:{since}:{include_breakdowns}'
        else:
            cache_key = f'pa:ops_slo:{window}:{include_breakdowns}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Parse window (Session 1080: added 1h + since_timestamp)
        now = timezone.now()
        if since:
            try:
                cutoff = datetime.fromisoformat(since.replace('Z', '+00:00'))
                if timezone.is_naive(cutoff):
                    cutoff = timezone.make_aware(cutoff)
                window = f'since:{since}'
            except (ValueError, TypeError):
                window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
                cutoff = now - timedelta(hours=window_hours)
        else:
            window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            cutoff = now - timedelta(hours=window_hours)

        slos = []

        # SLO 1: Celery task success rate (≥99.9%)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            total = CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status__in=['SUCCESS', 'FAILURE']).count()
            failed = CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE').count()
            rate = (total - failed) / total if total > 0 else 1.0
            slo = {
                'key': 'celery_task_success_rate',
                'name': 'Celery task success rate',
                'target': 0.999,
                'current': round(rate, 6),
                'breach': rate < 0.999,
                'numerator': total - failed,
                'denominator': total,
            }
            if include_breakdowns and failed > 0:
                top_failing = list(
                    CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE')
                    .values('task_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failures'] = top_failing
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'celery_task_success_rate', 'error': str(e)})

        # SLO 2: execute_agent_task success rate (≥99.95%)
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            agent_total = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, task_name='core.tasks.execute_agent_task',
                status__in=['SUCCESS', 'FAILURE']
            ).count()
            agent_failed = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, task_name='core.tasks.execute_agent_task',
                status='FAILURE'
            ).count()
            agent_rate = (agent_total - agent_failed) / agent_total if agent_total > 0 else 1.0
            slo = {
                'key': 'agent_task_success_rate',
                'name': 'execute_agent_task success rate',
                'target': 0.9995,
                'current': round(agent_rate, 6),
                'breach': agent_rate < 0.9995,
                'numerator': agent_total - agent_failed,
                'denominator': agent_total,
            }
            if include_breakdowns and agent_failed > 0:
                from core.models_unified_system import AgentExecution
                # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
                # "top_failing_agents" ranks router-agent job failures;
                # PA agentic loop failures would dominate the ranking
                # incorrectly. Use agent__name form per ADR-0002 F1 fold
                # equivalent (Postgres JSONField NULL-semantics make the
                # input_data__source='pa' form unsafe for pre-flag-flip rows).
                top_agents = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed'
                    ).exclude(agent__name='PersonalAssistant')
                    .values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failing_agents'] = top_agents
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'agent_task_success_rate', 'error': str(e)})

        # SLO 3: Agent wall-clock timeout rate (≤0.2%)
        try:
            from core.models_unified_system import AgentExecution
            total_execs = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            timeout_execs = AgentExecution.objects.filter(
                created_at__gte=cutoff, status='failed',
                error_message__icontains='timed out'
            ).count()
            timeout_rate = timeout_execs / total_execs if total_execs > 0 else 0.0
            slo = {
                'key': 'agent_timeout_rate',
                'name': 'Agent wall-clock timeout rate',
                'target_max': 0.002,
                'current': round(timeout_rate, 6),
                'breach': timeout_rate > 0.002,
                'numerator': timeout_execs,
                'denominator': total_execs,
            }
            if include_breakdowns and timeout_execs > 0:
                # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
                # "top_timeout_agents" ranks router-agent job timeouts;
                # PA agentic loop timeouts would dominate the ranking
                # incorrectly. Use agent__name form per ADR-0002 F1 fold
                # equivalent (Postgres JSONField NULL-semantics make the
                # input_data__source='pa' form unsafe for pre-flag-flip rows).
                top_timeout = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed',
                        error_message__icontains='timed out'
                    ).exclude(agent__name='PersonalAssistant')
                    .values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_timeout_agents'] = top_timeout
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'agent_timeout_rate', 'error': str(e)})

        # SLO 4: Deliberation zero-turn rate (0%)
        # Session 1075: Exclude ZOMBIE_REAPED — those are legitimate reaper cleanups
        # (stuck sessions cleaned up by reap_zombie_work), not pipeline bugs.
        try:
            from core.models_deliberation import DeliberationSession
            total_sessions = DeliberationSession.objects.filter(created_at__gte=cutoff).count()
            zero_turn = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='failed'
            ).exclude(
                failure_reason_code='ZOMBIE_REAPED'
            ).annotate(
                turn_count=Count('turns')
            ).filter(turn_count=0).count()
            zt_rate = zero_turn / total_sessions if total_sessions > 0 else 0.0
            zombie_reaped = DeliberationSession.objects.filter(
                created_at__gte=cutoff, status='failed',
                failure_reason_code='ZOMBIE_REAPED'
            ).count()
            slo = {
                'key': 'deliberation_zero_turn_rate',
                'name': 'Deliberation zero-turn failure rate',
                'target_max': 0.001,
                'current': round(zt_rate, 6),
                'breach': zt_rate > 0.001,
                'numerator': zero_turn,
                'denominator': total_sessions,
                'zombie_reaped': zombie_reaped,
            }
            # Include failure reason breakdown if any failed sessions exist
            if include_breakdowns:
                reason_breakdown = list(
                    DeliberationSession.objects.filter(
                        created_at__gte=cutoff, status='failed'
                    ).exclude(failure_reason_code='').values('failure_reason_code')
                    .annotate(count=Count('id')).order_by('-count')
                )
                if reason_breakdown:
                    slo['failure_reasons'] = reason_breakdown
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'deliberation_zero_turn_rate', 'error': str(e)})

        # SLO 5: Content publish conversion (≥40%)
        # Session 1080: Scoped to deliberation-sourced blogs only. Other SelfBlog
        # creators (initiative pipeline, research briefs, audit reports) have no
        # path to PublishGate and were inflating the denominator.
        try:
            from core.models_unified_system import SelfBlog
            delib_filter = {'created_at__gte': cutoff, 'author': 'ContentDeliberation'}
            blogs_created = SelfBlog.objects.filter(**delib_filter).count()
            blogs_published = SelfBlog.objects.filter(
                **delib_filter, status__in=['approved', 'published']
            ).count()
            pub_rate = blogs_published / blogs_created if blogs_created > 0 else None
            slos.append({
                'key': 'content_publish_conversion',
                'name': 'Content publish conversion rate',
                'target': 0.40,
                'current': round(pub_rate, 4) if pub_rate is not None else None,
                'breach': pub_rate < 0.40 if pub_rate is not None else False,
                'numerator': blogs_published,
                'denominator': blogs_created,
                'status': 'no_data' if blogs_created == 0 else ('ok' if pub_rate >= 0.40 else 'breach'),
            })
        except Exception as e:
            slos.append({'key': 'content_publish_conversion', 'error': str(e)})

        # SLO 6: Publish-ready backlog age p95 (≤72h)
        try:
            from core.models_unified_system import SelfBlog
            ready_blogs = SelfBlog.objects.filter(
                publish_ready=True, status__in=['approved', 'pending_review']
            ).order_by('created_at')
            ages_hours = []
            for blog in ready_blogs[:100]:
                age = (now - blog.created_at).total_seconds() / 3600
                ages_hours.append(age)
            if ages_hours:
                ages_hours.sort()
                p95_idx = int(len(ages_hours) * 0.95)
                p95_age = ages_hours[min(p95_idx, len(ages_hours) - 1)]
            else:
                p95_age = 0.0
            slos.append({
                'key': 'publish_ready_age_p95',
                'name': 'Publish-ready backlog age (p95 hours)',
                'target_max': 72.0,
                'current': round(p95_age, 1),
                'breach': p95_age > 72.0,
                'backlog_count': len(ages_hours),
            })
        except Exception as e:
            slos.append({'key': 'publish_ready_age_p95', 'error': str(e)})

        # SLO 7: PA tool success rate (≥99.9%)
        try:
            from core.models import ToolCallRecord
            pa_total = ToolCallRecord.objects.filter(created_at__gte=cutoff).count()
            pa_failed = ToolCallRecord.objects.filter(created_at__gte=cutoff, success=False).count()
            pa_rate = (pa_total - pa_failed) / pa_total if pa_total > 0 else 1.0
            slo = {
                'key': 'pa_tool_success_rate',
                'name': 'PA tool call success rate',
                'target': 0.999,
                'current': round(pa_rate, 6),
                'breach': pa_rate < 0.999,
                'numerator': pa_total - pa_failed,
                'denominator': pa_total,
            }
            if include_breakdowns and pa_failed > 0:
                top_pa_fail = list(
                    ToolCallRecord.objects.filter(created_at__gte=cutoff, success=False)
                    .values('tool_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
                )
                slo['top_failing_tools'] = top_pa_fail
            slos.append(slo)
        except Exception as e:
            slos.append({'key': 'pa_tool_success_rate', 'error': str(e)})

        # SLO 8: External HTTP failure rate (informational, ≤5%)
        try:
            from core.models_diagnostic_pipeline import FailureDetection
            http_errors = FailureDetection.objects.filter(
                detected_at__gte=cutoff, source_type='http_request'
            ).count()
            # Approximate total from celery + tool calls as proxy
            from core.models_celery_telemetry import CeleryTaskEvent
            approx_total = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).count()
            http_rate = http_errors / approx_total if approx_total > 0 else 0.0
            slos.append({
                'key': 'external_http_failure_rate',
                'name': 'External HTTP failure rate (informational)',
                'target_max': 0.05,
                'current': round(http_rate, 6),
                'breach': http_rate > 0.05,
                'numerator': http_errors,
                'denominator': approx_total,
                'note': 'Denominator is approx (total celery tasks as proxy)',
            })
        except Exception as e:
            slos.append({'key': 'external_http_failure_rate', 'error': str(e)})

        breaches = sum(1 for s in slos if s.get('breach'))
        result = {
            'action': 'slo_status',
            'window': window,
            'generated_at': now.isoformat(),
            'total_slos': len(slos),
            'breaches': breaches,
            'all_clear': breaches == 0,
            'slos': slos,
        }

        cache.set(cache_key, result, 120)  # 2-min cache
        return result

    def _ops_failure_signatures(self, window: str, limit: int, trace_id: str, since: str = None) -> Dict[str, Any]:
        """Top failure signatures in the given window, deduped and actionable."""
        from django.utils import timezone
        from datetime import timedelta, datetime
        from django.db.models import Count, Max

        now = timezone.now()
        if since:
            try:
                cutoff = datetime.fromisoformat(since.replace('Z', '+00:00'))
                if timezone.is_naive(cutoff):
                    cutoff = timezone.make_aware(cutoff)
                window = f'since:{since}'
            except (ValueError, TypeError):
                window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
                cutoff = now - timedelta(hours=window_hours)
        else:
            window_hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
            cutoff = now - timedelta(hours=window_hours)

        signatures = []

        try:
            from core.models_diagnostic_pipeline import FailureSignature, FailureDetection

            # Get signatures with recent detections in window
            from django.db.models import Q as _Q
            sig_qs = FailureSignature.objects.filter(
                status='active',
                detections__detected_at__gte=cutoff,
            ).annotate(
                window_count=Count('detections', filter=_Q(detections__detected_at__gte=cutoff)),
                last_detection=Max('detections__detected_at'),
            ).order_by('-window_count')[:limit]

            for sig in sig_qs:
                # Get sample detections for context
                samples = list(
                    FailureDetection.objects.filter(
                        signature=sig, detected_at__gte=cutoff
                    ).order_by('-detected_at')
                    .values('source_type', 'source_name', 'detected_at')[:3]
                )
                for s in samples:
                    s['detected_at'] = s['detected_at'].isoformat()

                signatures.append({
                    'signature': sig.signature,
                    'category': sig.category,
                    'provider': sig.provider or '',
                    'description': sig.description[:200] if sig.description else '',
                    'total_count': sig.occurrence_count,
                    'last_seen': sig.last_seen_at.isoformat() if sig.last_seen_at else '',
                    'status': sig.status,
                    'samples': samples,
                })
        except Exception as e:
            return {'action': 'failure_signatures', 'error': str(e)}

        # Also get top Celery task failures (in case not captured by diagnostic pipeline).
        # Session 1103c: loud on failure so the failure_signatures
        # response reports when the Celery-failures sidecar query
        # errored instead of silently returning an empty list.
        celery_failures = []
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            top_celery = list(
                CeleryTaskEvent.objects.filter(started_at__gte=cutoff, status='FAILURE')
                .values('task_name', 'error_type')
                .annotate(count=Count('id'), last_seen=Max('started_at'))
                .order_by('-count')[:5]
            )
            for cf in top_celery:
                cf['last_seen'] = cf['last_seen'].isoformat() if cf['last_seen'] else ''
            celery_failures = top_celery
        except Exception as e:
            logger.warning(
                "ops_tool.failure_signatures: celery_failures sidecar "
                "query failed (%s: %s) — response will omit the "
                "top-celery-failures section",
                type(e).__name__, e,
            )

        return {
            'action': 'failure_signatures',
            'window': window,
            'generated_at': timezone.now().isoformat(),
            'signatures': signatures,
            'celery_task_failures': celery_failures,
            'total_signatures': len(signatures),
        }


    def _ops_queue_pressure_rollup(
        self, user_id: Optional[int], trace_id: str,
    ) -> Dict[str, Any]:
        """System-level queue pressure rollup for ops_tool.overview.

        Phase 2 of the COO Operator Report queue-pressure work (Phase 1 was
        cockpit_tool.queue_lengths in PR #2289). Reuses the classifier in
        cockpit so thresholds stay single-source-of-truth — this is a
        reduction, never a re-classification.
        """
        from django.utils import timezone

        STATE_ORDER = {'GREEN': 0, 'YELLOW': 1, 'RED': 2, 'CRITICAL': 3, 'UNKNOWN': -1}

        cockpit = self._handle_cockpit(
            'cockpit_tool', {'action': 'queue_lengths'}, user_id, trace_id,
        )
        if not isinstance(cockpit, dict) or 'queues' not in cockpit:
            return {
                'overall_state': 'UNKNOWN',
                'error': cockpit.get('error', 'cockpit queue_lengths returned no queues') if isinstance(cockpit, dict) else 'cockpit queue_lengths returned non-dict',
                'generated_at': timezone.now().isoformat(),
            }

        queues = cockpit.get('queues') or {}
        overall_state = cockpit.get('overall_state', 'UNKNOWN')

        critical_count = 0
        red_count = 0
        offenders: list = []
        for q_name, q_info in queues.items():
            st = (q_info or {}).get('state', 'GREEN')
            if st == 'CRITICAL':
                critical_count += 1
            elif st == 'RED':
                red_count += 1
            if st in ('YELLOW', 'RED', 'CRITICAL'):
                offenders.append({
                    'queue': q_name,
                    'state': st,
                    'depth': q_info.get('depth'),
                    'oldest_age_seconds': q_info.get('oldest_age_seconds'),
                    'reasons': q_info.get('reasons', []),
                })
        offenders.sort(
            key=lambda d: (
                -STATE_ORDER.get(d['state'], 0),
                -(d.get('depth') or 0),
                -(d.get('oldest_age_seconds') or 0),
            )
        )

        rollup: Dict[str, Any] = {
            'overall_state': overall_state,
            'queues_critical_count': critical_count,
            'queues_red_count': red_count,
            'top_offenders': offenders[:3],
            'generated_at': timezone.now().isoformat(),
        }
        if cockpit.get('redis_error'):
            rollup['redis_error'] = cockpit['redis_error']
        return rollup


    def _ops_memory_pressure_rollup(self, trace_id: str) -> Dict[str, Any]:
        """Compact memory-pressure rollup for ops_tool.overview.

        Session 1168 (defer-approved in PR #2305 design pass). Reduces
        the latest ``logs/worker_memory/*.jsonl`` snapshot to a single
        ``overall_state`` + top offender + worker count. Reuses the
        source taxonomy (OK/WARN/CRIT) — never re-classifies
        (Session 1164 rule). Parallel to ``_ops_queue_pressure_rollup``.
        """
        from django.utils import timezone

        try:
            from core.services.memory_telemetry import read_recent_snapshots, LOG_DIR
        except ImportError as e:
            return {
                'overall_state': 'UNKNOWN',
                'error': f'memory_telemetry module unavailable: {e}',
                'generated_at': timezone.now().isoformat(),
            }

        latest = read_recent_snapshots(LOG_DIR, count=1)
        if not latest:
            return {
                'overall_state': 'UNKNOWN',
                'note': (
                    'No JSONL snapshot found at logs/worker_memory/. '
                    'The capture_worker_memory_snapshot beat task may '
                    'not have fired yet (5-min cadence) or workers may '
                    'need restart to pick up the new task.'
                ),
                'generated_at': timezone.now().isoformat(),
            }

        snapshot = latest[0]
        offenders = snapshot.get('top_offenders') or []
        top_offender = None
        if offenders:
            o = offenders[0]
            top_offender = {
                'hostname': o.get('hostname'),
                'pct_of_cap_max': o.get('pct_of_cap_max'),
                'status': o.get('status'),
            }
        return {
            'overall_state': snapshot.get('overall_status', 'UNKNOWN'),
            'worker_count': snapshot.get('worker_count'),
            'top_offender': top_offender,
            'downshift_recommended': snapshot.get(
                'downshift_recommended_global', False,
            ),
            'snapshot_generated_at': snapshot.get('generated_at'),
            'snapshot_generated_at_mt': snapshot.get('generated_at_mt'),
            'generated_at': timezone.now().isoformat(),
        }

    def _ops_memory_pressure(self, trace_id: str) -> Dict[str, Any]:
        """Worker memory pressure surface — reduce-from-JSONL.

        Session 1167 — COO Nervous System Backlog item #5. Reads the
        latest line from ``logs/worker_memory/YYYY-MM-DD.jsonl`` (UTC).
        The cadence task in ``core.tasks.capture_worker_memory_snapshot``
        is single-source-of-truth for sampling, cap parsing, and status
        thresholds. This handler projects + thin-renames for the PA
        tool surface; it does NOT re-classify (Session 1164 rule).
        """
        from django.utils import timezone

        try:
            from core.services.memory_telemetry import read_recent_snapshots, LOG_DIR
        except ImportError as e:
            return {
                'action': 'memory_pressure',
                'error': f'memory_telemetry module unavailable: {e}',
                'generated_at': timezone.now().isoformat(),
            }

        latest = read_recent_snapshots(LOG_DIR, count=1)
        if not latest:
            return {
                'action': 'memory_pressure',
                'overall_status': 'UNKNOWN',
                'note': (
                    'No JSONL snapshot found at logs/worker_memory/. '
                    'The capture_worker_memory_snapshot beat task may '
                    'not have fired yet (5-min cadence) or workers may '
                    'need restart to pick up the new task.'
                ),
                'generated_at': timezone.now().isoformat(),
            }

        snapshot = latest[0]
        # Session 1168: cap_coverage_pct — fraction of sampled workers
        # with a parseable --max-memory-per-child cap. Surfaces when the
        # rollup says OK because no caps were parsed (silent unknown vs
        # explicit "we sampled them and they're fine"). Per Rigby's late
        # add to the 24h watch ask.
        workers = snapshot.get('workers') or []
        worker_count = len(workers)
        capped = sum(
            1 for w in workers if w.get('cap_bytes') is not None
        )
        cap_coverage_pct = (
            round(100.0 * capped / worker_count, 1) if worker_count else None
        )
        return {
            'action': 'memory_pressure',
            'schema_version': snapshot.get('schema_version'),
            'snapshot_generated_at': snapshot.get('generated_at'),
            'snapshot_generated_at_mt': snapshot.get('generated_at_mt'),
            'cadence_seconds': snapshot.get('cadence_seconds'),
            'overall_status': snapshot.get('overall_status', 'OK'),
            'worker_count': snapshot.get('worker_count'),
            'cap_coverage_pct': cap_coverage_pct,
            'workers': snapshot.get('workers', []),
            'top_offenders': snapshot.get('top_offenders', []),
            'downshift_recommended': snapshot.get('downshift_recommended_global', False),
            'suggested_concurrency_by_worker': snapshot.get(
                'suggested_concurrency_by_worker', {}
            ),
            'recommended_actions': snapshot.get('recommended_actions', []),
            'sustain_gating': snapshot.get('sustain_gating', {}),
            'generated_at': timezone.now().isoformat(),
        }


    def _ops_top_consumers(
        self, window: str, limit, trace_id: str, *, group_by: str = 'task',
    ) -> Dict[str, Any]:
        """Top wall-clock consumers per task or agent — single SQL aggregate.

        Session 1167 — COO Nervous System Backlog item #7 (task dim).
        Session 1169 — agent dim added (closes carryover item F). Reduces
        to ``core.services.top_consumers.compute_top_consumers``; the
        service module is single-source-of-truth for the SQL + window
        vocabulary + p95 computation + dimension allowlist.
        """
        from django.utils import timezone

        try:
            from core.services.top_consumers import compute_top_consumers
        except ImportError as e:
            return {
                'action': 'top_consumers',
                'error': f'top_consumers module unavailable: {e}',
                'generated_at': timezone.now().isoformat(),
            }

        try:
            return compute_top_consumers(
                window=window, limit=limit, group_by=group_by,
            )
        except ValueError as e:
            return {
                'action': 'top_consumers',
                'error': str(e),
                'generated_at': timezone.now().isoformat(),
            }


    # ── Session 1100: Ops observability helpers ─────────────────────────────

    def _ops_celery_task_history(self, payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Recent Celery task runs (success + failure) for a given task name."""
        from django.utils import timezone
        from datetime import timedelta
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
        except ImportError:
            return {'error': 'CeleryTaskEvent model not available'}

        task_name = payload.get('task_name', '')
        limit = min(int(payload.get('limit', 20)), 100)
        window = payload.get('window', '6h')
        status_filter = payload.get('status')
        hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 6)
        cutoff = timezone.now() - timedelta(hours=hours)

        qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)
        if task_name:
            qs = qs.filter(task_name__icontains=task_name)
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        events = list(qs.order_by('-started_at').values(
            'task_id', 'task_name', 'status', 'queue', 'worker',
            'started_at', 'finished_at', 'duration_seconds',
            'error_type', 'error_message',
            'rss_mb_start', 'rss_mb_end', 'rss_delta_mb',
        )[:limit])

        for e in events:
            e['started_at'] = e['started_at'].isoformat() if e['started_at'] else None
            e['finished_at'] = e['finished_at'].isoformat() if e['finished_at'] else None
            if e.get('duration_seconds') is not None:
                e['duration_ms'] = int(e['duration_seconds'] * 1000)

        return {
            'action': 'celery_task_history',
            'task_name_filter': task_name or '(all)',
            'window': window,
            'count': len(events),
            'events': events,
        }

    _TENANT_BOUNDARY_FAILURE_KINDS = (
        'missing_row_id',
        'row_not_found',
        'missing_acting_identity',
        'acting_user_not_found',
        'unregistered_model',
        'predicate_rejected',
    )

    def _ops_tenant_boundary_violations(
        self, payload: Dict[str, Any], trace_id: str
    ) -> Dict[str, Any]:
        """Query I-0303 tenant_boundary_violation OpsRunEvent envelopes.

        Returns aggregate counts (by task_name, failure_kind, and their
        composite) plus most-recent sample events. Internal operator
        surface — the discriminator (row_id + acting_user_id + support_code
        + trace_id + failure_kind) is preserved per Phase 2 §2.1 (uniform
        user-facing envelope; operator-side keeps the discriminator for
        diagnostic use). Rigby SIGN F4 confirms this exposure at S2758.

        Payload:
          window: 1h/6h/24h/7d/30d (default 24h)
          task_name: substring filter on task_context.task_name (icontains)
          failure_kind: one of the 6 Phase 2 failure kinds
          limit: max sample_events (default 20, max 100)
        """
        from django.utils import timezone
        from datetime import timedelta

        try:
            from core.models_ops_runs import OpsRunEvent
        except ImportError:
            return {'error': 'OpsRunEvent model not available'}

        window = payload.get('window', '24h')
        hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
        cutoff = timezone.now() - timedelta(hours=hours)

        task_name_filter = payload.get('task_name', '') or ''
        failure_kind_filter = payload.get('failure_kind') or None
        if failure_kind_filter and failure_kind_filter not in self._TENANT_BOUNDARY_FAILURE_KINDS:
            return {
                'error': f'invalid failure_kind {failure_kind_filter!r}; '
                         f'allowed: {list(self._TENANT_BOUNDARY_FAILURE_KINDS)}'
            }
        limit = min(max(int(payload.get('limit', 20) or 20), 1), 100)

        qs = OpsRunEvent.objects.filter(
            label='tenant_boundary_violation',
            created_at__gte=cutoff,
        ).order_by('-created_at')

        # Materialize once for aggregation + sampling (bounded query).
        # Bound the aggregation-side scan by hard limit of 5000 rows to
        # protect the worker from a runaway violation-flood scenario.
        MAX_AGG_SCAN = 5000
        rows = list(qs.values('detail', 'created_at')[:MAX_AGG_SCAN])

        # Apply payload filters in Python (detail is JSONField; portable
        # substring + enum match without dialect-specific JSON operators).
        def _matches(row):
            ctx = (row.get('detail') or {}).get('task_context') or {}
            if task_name_filter:
                tn = ctx.get('task_name') or ''
                if task_name_filter.lower() not in tn.lower():
                    return False
            if failure_kind_filter:
                if ctx.get('failure_kind') != failure_kind_filter:
                    return False
            return True

        filtered = [r for r in rows if _matches(r)]

        by_task_name: Dict[str, int] = {}
        by_failure_kind: Dict[str, int] = {}
        by_task_and_kind: Dict[str, int] = {}

        for r in filtered:
            ctx = (r.get('detail') or {}).get('task_context') or {}
            tn = ctx.get('task_name') or '(unknown)'
            fk = ctx.get('failure_kind') or '(unknown)'
            by_task_name[tn] = by_task_name.get(tn, 0) + 1
            by_failure_kind[fk] = by_failure_kind.get(fk, 0) + 1
            composite = f'{tn}/{fk}'
            by_task_and_kind[composite] = by_task_and_kind.get(composite, 0) + 1

        sample_events = []
        for r in filtered[:limit]:
            d = r.get('detail') or {}
            ctx = d.get('task_context') or {}
            sample_events.append({
                'task_name': ctx.get('task_name'),
                'failure_kind': ctx.get('failure_kind'),
                'model_label': ctx.get('model_label'),
                'row_id': ctx.get('row_id'),
                'acting_user_id': ctx.get('acting_user_id'),
                'support_code': d.get('support_code'),
                'trace_id': d.get('trace_id'),
                'created_at': r['created_at'].isoformat() if r.get('created_at') else None,
            })

        result: Dict[str, Any] = {
            'action': 'tenant_boundary_violations',
            'window': window,
            'window_cutoff': cutoff.isoformat(),
            'task_name_filter': task_name_filter or '(all)',
            'failure_kind_filter': failure_kind_filter or '(all)',
            'total_count': len(filtered),
            'by_task_name': by_task_name,
            'by_failure_kind': by_failure_kind,
            'by_task_and_kind': by_task_and_kind,
            'sample_events': sample_events,
        }

        if len(rows) >= MAX_AGG_SCAN:
            result['aggregation_scan_capped'] = True
            result['aggregation_scan_limit'] = MAX_AGG_SCAN

        if result['total_count'] == 0:
            result['note'] = (
                f'No tenant_boundary_violation events in the last {window}. '
                f"Either traffic isn't hitting decorated tasks, or enforcement "
                f'is passing cleanly.'
            )

        return result

    _STALENESS_WARNING_VERDICTS = (
        'STALE_DAPHNE',
        'STALE_CELERY',
        'STALE_BOTH',
    )

    def _ops_staleness_warnings(
        self, payload: Dict[str, Any], trace_id: str
    ) -> Dict[str, Any]:
        """Query S2759 staleness_warning OpsRunEvent envelopes.

        Returns aggregate counts (by verdict + by head_commit_sha) plus
        most-recent sample events with full process detail preserved. Reads
        the accumulated warning history from the 30-min ``check_process_
        staleness`` Beat task emissions — complements the live ``ops_tool.
        version`` staleness_verdict which is the real-time freshness check.

        The ``by_head_commit_sha`` aggregate is the operational money bucket:
        it surfaces exactly which merges triggered stale-process warnings
        (i.e., which merges the operator forgot to run ``make recycle-all``
        after). Grouping by head commit SHA rather than by timestamp turns
        the 30-min Beat cadence into a clear "which commits leaked" report.

        Payload:
          window: 1h/6h/24h/7d/30d (default 24h)
          verdict: one of STALE_DAPHNE / STALE_CELERY / STALE_BOTH
          limit: max sample_events (default 20, max 100)
        """
        from django.utils import timezone
        from datetime import timedelta

        try:
            from core.models_ops_runs import OpsRunEvent
        except ImportError:
            return {'error': 'OpsRunEvent model not available'}

        window = payload.get('window', '24h')
        hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 24)
        cutoff = timezone.now() - timedelta(hours=hours)

        verdict_filter = payload.get('verdict') or None
        if verdict_filter and verdict_filter not in self._STALENESS_WARNING_VERDICTS:
            return {
                'error': f'invalid verdict {verdict_filter!r}; '
                         f'allowed: {list(self._STALENESS_WARNING_VERDICTS)}'
            }
        limit = min(max(int(payload.get('limit', 20) or 20), 1), 100)

        qs = OpsRunEvent.objects.filter(
            label='staleness_warning',
            created_at__gte=cutoff,
        ).order_by('-created_at')

        # Defensive scan cap (parallel to _ops_tenant_boundary_violations F7)
        MAX_AGG_SCAN = 5000
        rows = list(qs.values('detail', 'created_at')[:MAX_AGG_SCAN])

        def _matches(row):
            detail = row.get('detail') or {}
            if verdict_filter:
                if detail.get('verdict') != verdict_filter:
                    return False
            return True

        filtered = [r for r in rows if _matches(r)]

        by_verdict: Dict[str, int] = {}
        by_head_commit_sha: Dict[str, int] = {}

        for r in filtered:
            detail = r.get('detail') or {}
            v = detail.get('verdict') or '(unknown)'
            sha = detail.get('head_commit_sha') or '(unknown)'
            sha_short = sha[:12] if sha != '(unknown)' else sha
            by_verdict[v] = by_verdict.get(v, 0) + 1
            by_head_commit_sha[sha_short] = by_head_commit_sha.get(sha_short, 0) + 1

        sample_events = []
        for r in filtered[:limit]:
            detail = r.get('detail') or {}
            sha = detail.get('head_commit_sha') or None
            sample_events.append({
                'verdict': detail.get('verdict'),
                'head_commit_sha_short': sha[:12] if sha else None,
                'head_commit_timestamp': detail.get('head_commit_timestamp'),
                'daphne_pid': detail.get('daphne_pid'),
                'daphne_pid_age_seconds': detail.get('daphne_pid_age_seconds'),
                'daphne_started_before_head_commit': detail.get(
                    'daphne_started_before_head_commit',
                ),
                'celery_workers_status': detail.get('celery_workers_status', []),
                'fix': detail.get('fix'),
                'created_at': r['created_at'].isoformat() if r.get('created_at') else None,
            })

        result: Dict[str, Any] = {
            'action': 'staleness_warnings',
            'window': window,
            'window_cutoff': cutoff.isoformat(),
            'verdict_filter': verdict_filter or '(all)',
            'total_count': len(filtered),
            'by_verdict': by_verdict,
            'by_head_commit_sha': by_head_commit_sha,
            'sample_events': sample_events,
        }

        if len(rows) >= MAX_AGG_SCAN:
            result['aggregation_scan_capped'] = True
            result['aggregation_scan_limit'] = MAX_AGG_SCAN

        if result['total_count'] == 0:
            result['note'] = (
                f'No staleness_warning events in the last {window}. '
                f"Either verdict has been FRESH, or the check_process_staleness "
                f"Beat task isn't emitting — confirm via ops_tool.version."
            )

        return result

    def _ops_recent_recycles(
        self, payload: Dict[str, Any], trace_id: str
    ) -> Dict[str, Any]:
        """S2765: read tail of ``logs/recycle_events.jsonl``.

        The ``make recycle-all`` Makefile target appends one JSONL line per
        invocation (POSIX-atomic append; lines < PIPE_BUF). This handler
        reads the tail defensively — malformed lines are skipped so a
        partial write from a rare concurrent invocation doesn't blank the
        whole timeline. Complements the S2759 stale-process detection
        (post-hoc) and ``ops_tool.version`` (live snapshot) with a
        first-party operator-action timeline.

        Payload:
          limit: max events (default 10, max 50)
        """
        import json
        from datetime import datetime, timezone
        from pathlib import Path
        from django.conf import settings

        try:
            limit = int(payload.get('limit', 10) or 10)
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 50))

        log_path = Path(settings.BASE_DIR) / 'logs' / 'recycle_events.jsonl'
        resolved = log_path.resolve()
        base = Path(settings.BASE_DIR).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            return {
                'action': 'recent_recycles',
                'log_exists': False,
                'items': [],
                'count': 0,
                'limit': limit,
                'note': 'log path resolved outside BASE_DIR; refusing to read',
            }

        if not resolved.exists():
            return {
                'action': 'recent_recycles',
                'log_exists': False,
                'items': [],
                'count': 0,
                'limit': limit,
                'note': (
                    'logs/recycle_events.jsonl not present. '
                    'The Makefile emits this file on `make recycle-all`; run '
                    'a local recycle once to bootstrap.'
                ),
            }

        try:
            lines = resolved.read_text(errors='replace').splitlines()
        except OSError as exc:
            return {
                'action': 'recent_recycles',
                'log_exists': True,
                'items': [],
                'count': 0,
                'limit': limit,
                'note': f'read failed: {exc!s}',
            }

        # Defensive: skip malformed lines (Rigby SIGN concern §4.2 —
        # concurrent JSONL writes could interleave; a partial trailing
        # line shouldn't blank the timeline).
        events = []
        malformed = 0
        for line in reversed(lines):  # tail-first
            if len(events) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                malformed += 1
                continue
            if not isinstance(evt, dict):
                malformed += 1
                continue
            ts = evt.get('ts')
            sha = evt.get('sha') or ''
            label = evt.get('label') or 'recycle-all'
            seconds_ago = None
            if isinstance(ts, str):
                try:
                    parsed = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    seconds_ago = int((datetime.now(timezone.utc) - parsed).total_seconds())
                except (ValueError, TypeError):
                    seconds_ago = None
            entry: Dict[str, Any] = {
                'timestamp': ts,
                'sha': sha,
                'sha_short': sha[:12] if sha and sha != 'unknown' else sha,
                'label': label,
                'seconds_ago': seconds_ago,
            }
            # S2768 N7: surface enriched PID + partial-recycle fields when
            # present. Legacy events (pre-N7) lack these keys and pass
            # through unchanged — backward-compat via .get().
            for key in (
                'pids_before',
                'pids_after',
                'partial_recycle',
                'surviving_processes',
            ):
                if key in evt:
                    entry[key] = evt[key]
            events.append(entry)

        result: Dict[str, Any] = {
            'action': 'recent_recycles',
            'log_exists': True,
            'log_path': 'logs/recycle_events.jsonl',
            'items': events,
            'count': len(events),
            'limit': limit,
        }
        if malformed:
            result['malformed_lines_skipped'] = malformed
        if not events:
            result['note'] = 'log file exists but contained no parseable events.'
        return result

    def _ops_execution_detail(self, payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Look up a single AgentExecution by ID, including heartbeat."""
        from core.models_unified_system import AgentExecution
        from django.utils import timezone

        execution_id = payload.get('execution_id', '')
        if not execution_id:
            return {'error': 'execution_id required'}

        try:
            ex = AgentExecution.objects.select_related('agent').get(id=execution_id)
        except AgentExecution.DoesNotExist:
            return {'error': f'Execution {execution_id} not found'}

        now = timezone.now()
        hb = getattr(ex, 'last_heartbeat_at', None)

        return {
            'action': 'execution_detail',
            'execution': {
                'id': str(ex.id),
                'agent_name': ex.agent.name if ex.agent else 'Unknown',
                'task': ex.task[:500] if ex.task else '',
                'status': ex.status,
                'created_at': ex.created_at.isoformat(),
                'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                'last_heartbeat_at': hb.isoformat() if hb else None,
                'seconds_since_heartbeat': int((now - hb).total_seconds()) if hb else None,
                'execution_time_ms': ex.execution_time_ms,
                'error_message': ex.error_message,
                'tokens_used': ex.tokens_used,
                'cost': float(ex.cost) if ex.cost else 0,
            },
        }

    def _ops_execution_search(self, payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Search recent AgentExecutions by agent name / status."""
        from core.models_unified_system import AgentExecution
        from django.utils import timezone
        from datetime import timedelta

        agent_name = payload.get('agent_name', '')
        status_filter = payload.get('status')
        limit = min(int(payload.get('limit', 10)), 50)
        window = payload.get('window', '6h')
        hours = {'1h': 1, '6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 6)
        cutoff = timezone.now() - timedelta(hours=hours)

        qs = AgentExecution.objects.filter(created_at__gte=cutoff).select_related('agent')
        if agent_name:
            qs = qs.filter(agent__name__icontains=agent_name)
        if status_filter:
            qs = qs.filter(status=status_filter)

        executions = list(qs.order_by('-created_at')[:limit])
        now = timezone.now()

        return {
            'action': 'execution_search',
            'agent_name_filter': agent_name or '(all)',
            'status_filter': status_filter or '(all)',
            'window': window,
            'count': len(executions),
            'executions': [
                {
                    'id': str(ex.id),
                    'agent_name': ex.agent.name if ex.agent else 'Unknown',
                    'task': ex.task[:200] if ex.task else '',
                    'status': ex.status,
                    'created_at': ex.created_at.isoformat(),
                    'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                    'last_heartbeat_at': ex.last_heartbeat_at.isoformat() if getattr(ex, 'last_heartbeat_at', None) else None,
                    'seconds_since_heartbeat': int((now - ex.last_heartbeat_at).total_seconds()) if getattr(ex, 'last_heartbeat_at', None) else None,
                    'execution_time_ms': ex.execution_time_ms,
                    'error_message': ex.error_message[:200] if ex.error_message else '',
                }
                for ex in executions
            ],
        }

    # ── Session 1080: Agent Control Tool ────────────────────────────────────

    def _handle_agent_control(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1080: Centralized agent block/unblock/list.
        Replaces hardcoded frozensets across tasks.py, agent_router.py, tool_dispatcher.py.
        """
        from core.models_unified_system import AgentControlEntry
        from django.utils import timezone

        action = payload.get('action', 'list')

        if action == 'list':
            entries = list(
                AgentControlEntry.objects.all()
                .order_by('-updated_at')
                .values('agent_name', 'status', 'reason', 'blocked_at',
                        'blocked_by', 'ttl_hours', 'updated_at')
            )
            for e in entries:
                if e.get('blocked_at'):
                    e['blocked_at'] = e['blocked_at'].isoformat()
                if e.get('updated_at'):
                    e['updated_at'] = e['updated_at'].isoformat()

            # Also show currently blocked set (includes TTL expiry check)
            blocked_now = sorted(AgentControlEntry.get_blocked_names())

            return {
                'action': 'list',
                'blocked_now': blocked_now,
                'total_entries': len(entries),
                'entries': entries,
            }

        elif action == 'block':
            agent_name = payload.get('agent_name', '').strip()
            if not agent_name:
                raise ValueError("agent_name required for block action")
            reason = payload.get('reason', 'Blocked via PA')
            ttl_hours = payload.get('ttl_hours')
            blocked_by = payload.get('blocked_by', 'rigby')

            now = timezone.now()
            entry, created = AgentControlEntry.objects.update_or_create(
                agent_name=agent_name,
                defaults={
                    'status': 'blocked',
                    'reason': reason[:255],
                    'blocked_at': now,
                    'blocked_by': blocked_by[:100],
                    'ttl_hours': ttl_hours,
                }
            )

            return {
                'action': 'block',
                'agent_name': agent_name,
                'status': 'blocked',
                'reason': reason,
                'ttl_hours': ttl_hours,
                'blocked_by': blocked_by,
                'created': created,
                'success': True,
            }

        elif action == 'unblock':
            agent_name = payload.get('agent_name', '').strip()
            if not agent_name:
                raise ValueError("agent_name required for unblock action")
            reason = payload.get('reason', 'Unblocked via PA')

            updated = AgentControlEntry.objects.filter(
                agent_name=agent_name, status='blocked'
            ).update(status='enabled', reason=reason[:255])

            return {
                'action': 'unblock',
                'agent_name': agent_name,
                'status': 'enabled',
                'was_blocked': updated > 0,
                'success': True,
            }

        elif action == 'audit_log':
            # Show recent changes — uses updated_at ordering
            limit = min(int(payload.get('limit', 20)), 50)
            entries = list(
                AgentControlEntry.objects.all()
                .order_by('-updated_at')[:limit]
                .values('agent_name', 'status', 'reason', 'blocked_at',
                        'blocked_by', 'ttl_hours', 'updated_at')
            )
            for e in entries:
                if e.get('blocked_at'):
                    e['blocked_at'] = e['blocked_at'].isoformat()
                if e.get('updated_at'):
                    e['updated_at'] = e['updated_at'].isoformat()

            return {
                'action': 'audit_log',
                'count': len(entries),
                'entries': entries,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: list, block, unblock, audit_log"
            )

    # ── Session 1086: Active Priority Tool (initiative 2dcb79d7) ────────────

    # TTL bounds locked in the design review: min 10min (anti-flap),
    # max 7 days (anti-zombie), default 24h.
    _PRIORITY_TTL_MIN_HOURS = 10 / 60
    _PRIORITY_TTL_MAX_HOURS = 7 * 24
    _PRIORITY_TTL_DEFAULT_HOURS = 24

    def _clamp_priority_ttl(self, ttl_hours) -> float:
        """Clamp TTL to [10min, 7d]; coerce None/invalid to default 24h."""
        try:
            ttl = float(ttl_hours) if ttl_hours is not None else self._PRIORITY_TTL_DEFAULT_HOURS
        except (TypeError, ValueError):
            ttl = self._PRIORITY_TTL_DEFAULT_HOURS
        return max(self._PRIORITY_TTL_MIN_HOURS, min(self._PRIORITY_TTL_MAX_HOURS, ttl))

    def _serialize_priority(self, p) -> Dict[str, Any]:
        """Convert an ActivePriority ORM row to a JSON-friendly dict."""
        return {
            'id': str(p.id),
            'name': p.name,
            'description': p.description,
            'tags': list(p.tags or []),
            'agent_whitelist': list(p.agent_whitelist or []),
            'agent_blacklist': list(p.agent_blacklist or []),
            'enable_keyword_match': p.enable_keyword_match,
            'priority_rank': p.priority_rank,
            'owner': p.owner,
            'status': p.status,
            'activated_at': p.activated_at.isoformat() if p.activated_at else None,
            'expires_at': p.expires_at.isoformat() if p.expires_at else None,
            'is_expired': p.is_expired,
            'enabled': p.enabled,
            'max_daily_executions': p.max_daily_executions,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
        }

    def _handle_active_priority(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1086 PR 1: Rigby's priority-aware routing — PA tool surface.

        PR 1 delivers the schema + tool only; the PriorityRouter matching
        logic ships in PR 2 and agent_router.route() integration + the
        semaphore land in PR 3. test_match is a deliberate stub until PR 2
        provides the actual match function.

        See initiative 2dcb79d7-6f2b-4e67-a366-a54e96d7870f and the Session
        1086 design review conversation for the full contract.
        """
        from core.models_unified_system import ActivePriority
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'list')

        if action == 'list':
            # Active-only view. Triggers the TTL auto-expire side effect via
            # get_active_priorities() so stale rows don't linger visible.
            active_dicts = ActivePriority.get_active_priorities()
            # Also fetch full rows for richer display
            active_rows = list(
                ActivePriority.objects
                .filter(status=ActivePriority.STATUS_ACTIVE)
                .order_by('priority_rank', '-activated_at')
            )
            return {
                'action': 'list',
                'count': len(active_rows),
                'priorities': [self._serialize_priority(p) for p in active_rows],
                'matching_cache_summary': active_dicts,  # shape PR 2 will consume
            }

        elif action == 'set':
            name = (payload.get('name') or '').strip()
            if not name:
                raise ValueError("name required for 'set' action")

            ttl_hours = self._clamp_priority_ttl(payload.get('ttl_hours'))
            expires_at = timezone.now() + timedelta(hours=ttl_hours)

            # Sanitize list inputs — accept list[str], drop anything else
            def _as_str_list(val):
                if not isinstance(val, list):
                    return []
                return [str(x) for x in val if isinstance(x, (str, int, float))]

            # Session 1088: Support enabled toggle and daily budget
            create_kwargs = dict(
                name=name[:120],
                description=str(payload.get('description', ''))[:10_000],
                tags=_as_str_list(payload.get('tags')),
                agent_whitelist=_as_str_list(payload.get('agent_whitelist')),
                agent_blacklist=_as_str_list(payload.get('agent_blacklist')),
                enable_keyword_match=bool(payload.get('enable_keyword_match', False)),
                priority_rank=int(payload.get('priority_rank') or 100),  # Session 1228 PR-B autofill safety
                owner=str(payload.get('owner', 'rigby'))[:60],
                status=ActivePriority.STATUS_ACTIVE,
                expires_at=expires_at,
            )
            if 'enabled' in payload:
                create_kwargs['enabled'] = bool(payload['enabled'])
            if 'max_daily_executions' in payload and payload['max_daily_executions'] is not None:
                create_kwargs['max_daily_executions'] = int(payload['max_daily_executions'])
            priority = ActivePriority.objects.create(**create_kwargs)
            return {
                'action': 'set',
                'success': True,
                'ttl_hours_applied': ttl_hours,
                'priority': self._serialize_priority(priority),
            }

        elif action == 'update':
            priority_id = payload.get('priority_id')
            if not priority_id:
                raise ValueError("priority_id required for 'update' action")
            try:
                priority = ActivePriority.objects.get(id=priority_id)
            except ActivePriority.DoesNotExist:
                return {
                    'action': 'update',
                    'success': False,
                    'error': f'priority_id {priority_id} not found',
                }

            # Only touch fields present in payload — allows partial updates
            updated_fields = []
            if 'name' in payload:
                priority.name = str(payload['name'])[:120]
                updated_fields.append('name')
            if 'description' in payload:
                priority.description = str(payload['description'])[:10_000]
                updated_fields.append('description')
            if 'tags' in payload and isinstance(payload['tags'], list):
                priority.tags = [str(x) for x in payload['tags']]
                updated_fields.append('tags')
            if 'agent_whitelist' in payload and isinstance(payload['agent_whitelist'], list):
                priority.agent_whitelist = [str(x) for x in payload['agent_whitelist']]
                updated_fields.append('agent_whitelist')
            if 'agent_blacklist' in payload and isinstance(payload['agent_blacklist'], list):
                priority.agent_blacklist = [str(x) for x in payload['agent_blacklist']]
                updated_fields.append('agent_blacklist')
            if 'enable_keyword_match' in payload:
                priority.enable_keyword_match = bool(payload['enable_keyword_match'])
                updated_fields.append('enable_keyword_match')
            if 'priority_rank' in payload:
                priority.priority_rank = int(payload['priority_rank'])
                updated_fields.append('priority_rank')
            if 'owner' in payload:
                priority.owner = str(payload['owner'])[:60]
                updated_fields.append('owner')
            if 'ttl_hours' in payload:
                ttl_hours = self._clamp_priority_ttl(payload['ttl_hours'])
                priority.expires_at = timezone.now() + timedelta(hours=ttl_hours)
                updated_fields.append('expires_at')
            # Session 1088: Per-mission governance fields
            if 'enabled' in payload:
                priority.enabled = bool(payload['enabled'])
                updated_fields.append('enabled')
            if 'max_daily_executions' in payload:
                val = payload['max_daily_executions']
                priority.max_daily_executions = int(val) if val is not None else None
                updated_fields.append('max_daily_executions')

            if updated_fields:
                priority.save(update_fields=updated_fields + ['updated_at'])

            return {
                'action': 'update',
                'success': True,
                'updated_fields': updated_fields,
                'priority': self._serialize_priority(priority),
            }

        elif action == 'archive':
            priority_id = payload.get('priority_id')
            if not priority_id:
                raise ValueError("priority_id required for 'archive' action")
            updated = ActivePriority.objects.filter(
                id=priority_id
            ).update(status=ActivePriority.STATUS_ARCHIVED)
            return {
                'action': 'archive',
                'priority_id': str(priority_id),
                'success': updated > 0,
                'was_found': updated > 0,
            }

        elif action == 'test_match':
            # Session 1086 PR 2: Wire through to the real PriorityRouter.
            # Invalidate the cache first so a preview immediately after
            # a set/update in the same PA turn reflects the fresh state.
            from core.services.priority import PriorityRouter
            PriorityRouter.invalidate_cache()

            agent_name = payload.get('agent_name', '')
            task = payload.get('task', '')
            trigger_source = payload.get('trigger_source')  # optional
            if not agent_name:
                raise ValueError("agent_name required for 'test_match' action")

            router = PriorityRouter()
            decision = router.check(
                agent_name=agent_name,
                task=task,
                context=None,
                trigger_source=trigger_source,
            )
            return {
                'action': 'test_match',
                'probe': {
                    'agent_name': agent_name,
                    'task': task[:200] if task else '',
                    'trigger_source': trigger_source,
                },
                'decision': decision.to_dict(),
                'active_priorities_count': len(ActivePriority.get_active_priorities()),
            }

        elif action == 'history':
            limit = min(int(payload.get('limit', 30) or 30), 100)
            rows = list(
                ActivePriority.objects.all()
                .order_by('-updated_at')[:limit]
            )
            return {
                'action': 'history',
                'count': len(rows),
                'limit': limit,
                'priorities': [self._serialize_priority(p) for p in rows],
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: list, set, update, archive, test_match, history"
            )

    # ── Session 1088: Governor Tool ─────────────────────────────────────

    def _handle_governor(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Beat Task Governor — mission alignment + circuit breaker management.

        Actions:
          - status: overview of governor state, missions, tripped breakers
          - test: check if a specific agent would be dispatched
          - reset_breaker: manually reset a tripped circuit breaker
          - coverage: show all agents and their alignment status
        """
        action = payload.get('action', 'status')
        # LLM sometimes sends 'list' when it means 'status'
        if action == 'list':
            action = 'status'

        if action == 'status':
            from core.services.priority.governor import get_governor_status
            return {
                'action': 'status',
                **get_governor_status(),
            }

        elif action == 'test':
            agent_name = payload.get('agent_name', '')
            if not agent_name:
                raise ValueError("agent_name required for 'test' action")

            from core.services.priority.governor import should_dispatch
            from core.services.priority.priority_router import PriorityRouter
            PriorityRouter.invalidate_cache()

            trigger = payload.get('trigger_source', 'schedule')
            decision = should_dispatch(
                agent_name=agent_name,
                trigger_source=trigger,
                task=payload.get('task'),
            )
            return {
                'action': 'test',
                'agent_name': agent_name,
                'trigger_source': trigger,
                **decision.to_dict(),
            }

        elif action == 'reset_breaker':
            agent_name = payload.get('agent_name', '')
            if not agent_name:
                raise ValueError("agent_name required for 'reset_breaker' action")

            from core.services.priority.governor import reset_circuit_breaker
            success = reset_circuit_breaker(agent_name)
            return {
                'action': 'reset_breaker',
                'agent_name': agent_name,
                'success': success,
            }

        elif action == 'coverage':
            from core.services.priority.governor import should_dispatch
            from core.services.priority.priority_router import PriorityRouter
            from core.agent_router import AgentRouter
            PriorityRouter.invalidate_cache()

            router = AgentRouter()
            results = []
            for name in sorted(router.AGENT_MAP.keys()):
                d = should_dispatch(name, trigger_source='schedule')
                results.append({
                    'agent': name,
                    'proceed': d.proceed,
                    'reason': d.reason,
                    'detail': d.detail,
                })

            aligned = sum(1 for r in results if r['proceed'])
            return {
                'action': 'coverage',
                'total': len(results),
                'aligned': aligned,
                'misaligned': len(results) - aligned,
                'coverage_pct': f"{aligned / len(results):.0%}" if results else '0%',
                'agents': results,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: status, test, reset_breaker, coverage"
            )

    # ── Session 1080: Ops Autopilot Tool ──────────────────────────────────

    def _handle_autopilot(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1080: Autopilot visibility — status, history, run, config.
        Lets Rigby inspect and trigger the Ops Autopilot.
        """
        from core.models_diagnostic_pipeline import AutopilotAction
        from core.services.ops_autopilot import OpsAutopilot, AutopilotConfig
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'status')

        # Guard: AutopilotAction table may not exist yet on Railway
        def _safe_autopilot_query(fn, default=None):
            try:
                return fn()
            except Exception:
                return default

        if action == 'status':
            # Current config + last cycle info
            last_action = _safe_autopilot_query(
                lambda: AutopilotAction.objects.first()
            )
            last_cycle = None
            if last_action:
                last_cycle = {
                    'action_type': last_action.action_type,
                    'agent_name': last_action.agent_name,
                    'policy': last_action.policy,
                    'dry_run': last_action.dry_run,
                    'created_at': last_action.created_at.isoformat(),
                    'deploy_sha': last_action.deploy_sha,
                }

            total_actions = _safe_autopilot_query(
                lambda: AutopilotAction.objects.count(), 0
            )
            blocks_24h = _safe_autopilot_query(
                lambda: AutopilotAction.objects.filter(
                    action_type='block_agent',
                    dry_run=False,
                    created_at__gte=timezone.now() - timedelta(hours=24),
                ).count(), 0
            )

            return {
                'action': 'status',
                'config': {
                    'timeout_spike_threshold': AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD,
                    'timeout_spike_window_minutes': AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES,
                    'timeout_block_ttl_minutes': AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES,
                    'max_blocks_per_agent_per_hour': AutopilotConfig.MAX_BLOCKS_PER_AGENT_PER_HOUR,
                    'max_total_blocks_per_cycle': AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE,
                    'stale_block_hours': AutopilotConfig.STALE_BLOCK_HOURS,
                    'dry_run': AutopilotConfig.DRY_RUN,
                },
                'last_action': last_cycle,
                'total_actions_ever': total_actions,
                'blocks_last_24h': blocks_24h,
                'beat_schedule': 'every 10 minutes',
            }

        elif action == 'history':
            limit = min(int(payload.get('limit', 20)), 100)
            # S2856 slate #2: opt-in evidence + result JSON per row so
            # operators can inspect trigger / actor_user_id / reason without
            # dropping to Django shell. Default false preserves prior shape.
            include_evidence = bool(payload.get('include_evidence', False))
            # S2861 slate #1: selected_fields projects evidence + result JSON
            # down to specific top-level keys so operators can request only
            # the fields they need (e.g., ['evidence.actor_user_id',
            # 'result.reason']) instead of dumping full JSONField blobs.
            # Top-level only in v1 — nested dicts/lists returned whole.
            # Allowlist set makes future extension (e.g., verification_result)
            # a single-line change per Rigby Q5b fold-mitigation.
            _ALLOWED_PROJECTION_PREFIXES = ('evidence', 'result')
            _MAX_SELECTED_FIELDS = 20
            raw_selected = payload.get('selected_fields') or []
            if not isinstance(raw_selected, list):
                raw_selected = []
            raw_selected = [str(f) for f in raw_selected[:_MAX_SELECTED_FIELDS]]
            selected_fields: list = []
            projection: dict = {p: [] for p in _ALLOWED_PROJECTION_PREFIXES}
            if include_evidence:
                for path in raw_selected:
                    prefix, _, key = path.partition('.')
                    if prefix in _ALLOWED_PROJECTION_PREFIXES and key:
                        projection[prefix].append(key)
                        selected_fields.append(path)
            fields = [
                'id', 'created_at', 'action_type', 'agent_name',
                'policy', 'dry_run', 'deploy_sha',
            ]
            if include_evidence:
                fields.extend(['evidence', 'result'])
            actions = _safe_autopilot_query(
                lambda: list(
                    AutopilotAction.objects.all()[:limit].values(*fields)
                ), []
            )
            for a in actions:
                a['created_at'] = a['created_at'].isoformat()
                if include_evidence and selected_fields:
                    for prefix in _ALLOWED_PROJECTION_PREFIXES:
                        src = a.get(prefix)
                        if not isinstance(src, dict):
                            a[prefix] = {}
                            continue
                        a[prefix] = {
                            k: src[k] for k in projection[prefix] if k in src
                        }

            return {
                'action': 'history',
                'count': len(actions),
                'include_evidence': include_evidence,
                'selected_fields': selected_fields,
                'actions': actions,
            }

        elif action == 'run':
            dry_run = payload.get('dry_run', False)
            try:
                autopilot = OpsAutopilot(dry_run=dry_run)
                summary = autopilot.run()
            except Exception as e:
                return {
                    'action': 'run',
                    'error': f'Autopilot run failed (table may not exist yet): {str(e)[:200]}',
                }
            return {
                'action': 'run',
                'dry_run': dry_run,
                'summary': summary,
            }

        elif action == 'config':
            return {
                'action': 'config',
                'timeout_spike_threshold': AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD,
                'timeout_spike_window_minutes': AutopilotConfig.TIMEOUT_SPIKE_WINDOW_MINUTES,
                'timeout_block_ttl_minutes': AutopilotConfig.TIMEOUT_BLOCK_TTL_MINUTES,
                'max_blocks_per_agent_per_hour': AutopilotConfig.MAX_BLOCKS_PER_AGENT_PER_HOUR,
                'max_total_blocks_per_cycle': AutopilotConfig.MAX_TOTAL_BLOCKS_PER_CYCLE,
                'stale_block_hours': AutopilotConfig.STALE_BLOCK_HOURS,
                'dry_run': AutopilotConfig.DRY_RUN,
                'note': (
                    'Config is currently code-level. '
                    'Changing thresholds requires a deploy.'
                ),
            }

        elif action == 'dry_run_report':
            # Run autopilot in dry-run mode and return human-readable report
            autopilot = OpsAutopilot(dry_run=True)
            summary = autopilot.run()

            # Also fetch current SLO status for context
            slo_data = self._ops_slo_status(
                window='24h', include_breakdowns=True, trace_id=trace_id,
            )
            breaches = [
                s for s in slo_data.get('slos', [])
                if s.get('breach', False)
            ]

            report_lines = ['## Autopilot Dry-Run Report\n']
            report_lines.append(f"**Mode:** DRY RUN (no actions taken)")
            report_lines.append(f"**Deploy SHA:** {summary.get('deploy_sha', 'unknown')}\n")

            # SLO breaches section
            if breaches:
                report_lines.append(f"### SLO Breaches ({len(breaches)})")
                for b in breaches:
                    report_lines.append(
                        f"- **{b.get('name', b.get('key'))}**: "
                        f"current={b.get('current')} "
                        f"(target {'<=' if 'target_max' in b else '>='} "
                        f"{b.get('target_max', b.get('target', '?'))})"
                    )
            else:
                report_lines.append('### SLO Breaches: None')

            # Timeout spike section
            ts = summary.get('timeout_spike', {})
            agents_checked = ts.get('agents_checked', {})
            if agents_checked:
                report_lines.append(f"\n### Timeout Spike Analysis")
                for agent, count in agents_checked.items():
                    would_block = count >= AutopilotConfig.TIMEOUT_SPIKE_THRESHOLD
                    report_lines.append(
                        f"- {agent}: {count} timeouts "
                        f"{'→ WOULD BLOCK' if would_block else '(below threshold)'}"
                    )
            else:
                report_lines.append(f"\n### Timeout Spike Analysis: No timeouts detected")

            # Blocked agent hygiene
            hygiene = summary.get('blocked_hygiene', {})
            stale = hygiene.get('stale_blocks', [])
            if stale:
                report_lines.append(f"\n### Stale Blocks ({len(stale)})")
                for s in stale:
                    report_lines.append(
                        f"- {s['agent_name']}: blocked {s['blocked_hours']}h "
                        f"({s['reason']}) — consider adding TTL or unblocking"
                    )
            else:
                report_lines.append(f"\n### Stale Blocks: None")

            # Deliberation retry section
            delib = summary.get('deliberation_retry', {})
            retried = delib.get('retried', 0)
            skipped = delib.get('skipped', 0)
            if retried > 0 or skipped > 0:
                report_lines.append(f"\n### Deliberation Retry")
                report_lines.append(f"- Would retry: {retried} failed sessions")
                if skipped:
                    report_lines.append(f"- Skipped: {skipped} (already retried or no valid topic)")
            else:
                report_lines.append(f"\n### Deliberation Retry: No retryable failures")

            # Revenue pipeline section — Session 1222 P4 (audit C1).
            # Pre-fix the dry_run_report's JSON summary carried this data
            # under summary.revenue_pipeline but the formatted text output
            # omitted it, which is what made the "2631 vs 47 mismatch"
            # confusing in the Session 1217 audit. Both numbers shown now,
            # with a clear scope label distinguishing platform-wide pool
            # from the calling user's curated pipeline. See PR description
            # for the lead-discovery-pool pattern.
            revenue = summary.get('revenue_pipeline', {})
            if revenue.get('total_active') or revenue.get('actions_suggested'):
                report_lines.append(f"\n### Revenue Pipeline (platform-wide)")
                report_lines.append(
                    f"- Total active (all users, incl. spider-ingested lead pool): "
                    f"{revenue.get('total_active', 0)}"
                )
                if revenue.get('high_value_active'):
                    report_lines.append(
                        f"- High-value (≥$500): {revenue.get('high_value_active', 0)}"
                    )
                if revenue.get('stale_count'):
                    report_lines.append(
                        f"- Stale (>{48}h since created): {revenue.get('stale_count', 0)}"
                    )
                if revenue.get('critical_stale'):
                    report_lines.append(
                        f"- Critically stale (>7d): {revenue.get('critical_stale', 0)}"
                    )
                if revenue.get('actions_suggested'):
                    report_lines.append(
                        f"- Actions suggested: {revenue.get('actions_suggested', 0)}"
                    )
                report_lines.append(
                    "- Scope note: this is the **platform-wide lead pool**. "
                    "Per-user 'your pipeline' counts come from "
                    "`opportunity_manager_tool action=stats` (caller-scoped)."
                )
            else:
                report_lines.append(f"\n### Revenue Pipeline: No active opportunities")

            # Content sweep section
            content = summary.get('content_sweep', {})
            enhance = content.get('kicked_enhance', 0)
            review = content.get('kicked_review', 0)
            if enhance or review:
                report_lines.append(f"\n### Content Pipeline Sweep")
                if enhance:
                    report_lines.append(f"- Would kick {enhance} stuck needs_enhancement blogs")
                if review:
                    report_lines.append(f"- Would kick {review} unscored pending_review blogs")
            else:
                report_lines.append(f"\n### Content Pipeline Sweep: No stuck content")

            # Attention auto-resolve section
            attn = summary.get('attention_resolve', {})
            resolved = attn.get('resolved', 0)
            if resolved:
                report_lines.append(f"\n### Attention Auto-Resolve")
                report_lines.append(f"- Would auto-resolve: {resolved} stale ops alerts")
            else:
                report_lines.append(f"\n### Attention Auto-Resolve: No stale alerts")

            # Governance auto-decision section
            gov = summary.get('governance_auto', {})
            gov_approved = gov.get('auto_approved', 0)
            gov_dismissed = gov.get('auto_dismissed', 0)
            gov_skipped = gov.get('skipped', 0)
            if gov_approved or gov_dismissed:
                report_lines.append(f"\n### Governance Auto-Decision")
                if gov_approved:
                    report_lines.append(f"- Would auto-approve: {gov_approved} low-risk items")
                if gov_dismissed:
                    report_lines.append(f"- Would auto-dismiss: {gov_dismissed} low-risk items")
                if gov_skipped:
                    report_lines.append(f"- Skipped (high blast radius): {gov_skipped}")
            else:
                report_lines.append(f"\n### Governance Auto-Decision: No eligible items")

            # Actions proposed
            proposed = summary.get('actions', [])
            if proposed:
                report_lines.append(f"\n### Proposed Actions ({len(proposed)})")
                for a in proposed:
                    target = a.get('agent_name', a.get('session_id', a.get('blog_id', a.get('attention_item_id', '?'))))
                    if isinstance(target, str) and len(target) > 20:
                        target = target[:20]
                    report_lines.append(f"- {a.get('type', '?')}: {target} — {a.get('reason', a.get('governance_action', a.get('action', '')))}")
            else:
                report_lines.append(f"\n### Proposed Actions: None (system healthy)")

            # Verification + rollback stats (last 24h)
            try:
                from core.models_diagnostic_pipeline import AutopilotAction
                from django.utils import timezone as tz
                from datetime import timedelta
                day_cutoff = tz.now() - timedelta(hours=24)
                recent_actions = AutopilotAction.objects.filter(
                    created_at__gte=day_cutoff,
                    dry_run=False,
                )
                verif_pending = recent_actions.filter(verification_state='pending').count()
                verif_passed = recent_actions.filter(verification_state='passed').count()
                verif_failed = recent_actions.filter(verification_state='failed').count()
                rolled_back = recent_actions.filter(rolled_back=True).count()
                remediations = recent_actions.filter(action_type='remediate').count()
                report_lines.append(f"\n### Verification & Safety (24h)")
                report_lines.append(f"- Verified passed: {verif_passed}")
                report_lines.append(f"- Pending verification: {verif_pending}")
                report_lines.append(f"- Failed verification: {verif_failed}")
                report_lines.append(f"- Auto-rolled back: {rolled_back}")
                report_lines.append(f"- Auto-remediations applied: {remediations}")
            except Exception as e:
                # Session 1083 (Rigby audit): was bare pass — verification
                # section would silently vanish from ops digest on any DB
                # error, false-greening the operator. Now the report itself
                # shows the degradation and the log carries full context.
                logger.warning(
                    "ops digest: verification/safety section failed "
                    "(%s: %s)", type(e).__name__, e,
                )
                report_lines.append(
                    f"\n### Verification & Safety (24h) — DEGRADED "
                    f"(query failed: {type(e).__name__})"
                )

            # Remediation playbook stats
            try:
                from core.models_diagnostic_pipeline import RemediationPlaybook
                playbook_count = RemediationPlaybook.objects.filter(enabled=True).count()
                if playbook_count > 0:
                    top_playbook = RemediationPlaybook.objects.filter(
                        enabled=True, times_applied__gte=1,
                    ).order_by('-success_rate').first()
                    report_lines.append(f"\n### Remediation Playbook")
                    report_lines.append(f"- Active entries: {playbook_count}")
                    if top_playbook:
                        report_lines.append(
                            f"- Top entry: {top_playbook.signature_pattern} → "
                            f"{top_playbook.remediation_type} "
                            f"({top_playbook.success_rate:.0%} success, "
                            f"{top_playbook.times_applied}x applied)"
                        )
            except Exception as e:
                logger.warning(
                    "ops digest: remediation playbook section failed "
                    "(%s: %s)", type(e).__name__, e,
                )
                report_lines.append(
                    f"\n### Remediation Playbook — DEGRADED "
                    f"(query failed: {type(e).__name__})"
                )

            # Self-tuning status
            try:
                from core.services.ops_autopilot import PolicyOptimizer
                optimizer = PolicyOptimizer()
                tuning_eval = optimizer.evaluate()
                recs = tuning_eval.get('recommendations', [])
                if recs:
                    report_lines.append(f"\n### Self-Tuning Recommendations ({len(recs)})")
                    for r in recs:
                        report_lines.append(
                            f"- **{r['param']}**: {r['old_value']} → "
                            f"{r['new_value']} ({r['confidence']})\n"
                            f"  _{r['reason']}_"
                        )
                else:
                    report_lines.append('\n### Self-Tuning: All parameters optimal')

                overrides = AutopilotConfig._override_cache
                if overrides:
                    report_lines.append(f"\n### Active Config Overrides ({len(overrides)})")
                    for param, val in overrides.items():
                        report_lines.append(f"- {param}: {val}")
            except Exception as e:
                logger.warning(
                    "ops digest: self-tuning section failed (%s: %s)",
                    type(e).__name__, e,
                )
                report_lines.append(
                    f"\n### Self-Tuning — DEGRADED "
                    f"(PolicyOptimizer failed: {type(e).__name__})"
                )

            # QROI attribution section
            try:
                from core.services.ops_autopilot import ROIEnforcer
                enforcer = ROIEnforcer()
                roi_data = enforcer.compute_roi_scores(tz.now(), window_hours=24)
                if roi_data.get('agents'):
                    report_lines.append(f"\n### QROI Attribution (24h)")
                    report_lines.append(
                        f"Total spend: ${roi_data['total_spend']:.2f} — "
                        f"{roi_data['total_outcomes']} outcomes"
                    )
                    for a in roi_data['agents'][:5]:
                        report_lines.append(
                            f"- **{a['agent_name']}**: "
                            f"QROI {a.get('qroi', a['roi']):.1%} "
                            f"(ROI {a['roi']:.1%} × "
                            f"Q {a.get('quality_weight', 0.5):.2f}) — "
                            f"${a['cost']:.4f}, {a['outcomes']} outcomes"
                        )
                    recs = enforcer.get_throttle_recommendations(tz.now())
                    if recs:
                        report_lines.append(
                            f"\n**Would throttle {len(recs)} agents** "
                            f"under budget pressure"
                        )
            except Exception as e:
                logger.warning(
                    "ops digest: QROI attribution section failed "
                    "(%s: %s)", type(e).__name__, e,
                )
                report_lines.append(
                    f"\n### QROI Attribution — DEGRADED "
                    f"(ROIEnforcer failed: {type(e).__name__})"
                )

            return {
                'action': 'dry_run_report',
                'report': '\n'.join(report_lines),
                'summary': summary,
                'slo_breaches': len(breaches),
                'proposed_actions': len(proposed),
            }

        elif action == 'drift_scan':
            # Run contract/schema drift detection on demand
            from core.services.contract_monitor import ContractMonitor
            monitor = ContractMonitor()
            report = monitor.full_scan()
            summary_text = monitor.summary_for_governance(report)
            return {
                'action': 'drift_scan',
                'critical': report['critical'],
                'warning': report['warning'],
                'info': report['info'],
                'total': report['total'],
                'checks_run': report['checks_run'],
                'summary': summary_text,
                'findings': report['findings'],
            }

        elif action == 'tuning_report':
            # Show current tuning state, overrides, and recent changes
            from core.services.ops_autopilot import PolicyOptimizer
            AutopilotConfig.load_overrides()
            optimizer = PolicyOptimizer()

            # Evaluate recommendations (read-only)
            evaluation = optimizer.evaluate()
            tuning_status = optimizer.get_tuning_report()

            report_lines = ['## Policy Self-Tuning Report\n']

            # Active overrides
            overrides = tuning_status.get('overrides_active', {})
            if overrides:
                report_lines.append(f'### Active Overrides ({len(overrides)})')
                for param, value in overrides.items():
                    spec = PolicyOptimizer.TUNABLES.get(param, {})
                    default = spec.get('default', '?')
                    report_lines.append(
                        f'- **{param}**: {value} (default: {default})'
                    )
            else:
                report_lines.append('### Active Overrides: None (all defaults)')

            # Current recommendations
            recs = evaluation.get('recommendations', [])
            if recs:
                report_lines.append(f'\n### Recommendations ({len(recs)})')
                for r in recs:
                    report_lines.append(
                        f'- **{r["param"]}**: {r["old_value"]} → '
                        f'{r["new_value"]} ({r["confidence"]} confidence)\n'
                        f'  {r["reason"]}'
                    )
            else:
                report_lines.append('\n### Recommendations: None (all params optimal)')

            # Recent changes
            changes = tuning_status.get('recent_changes', [])
            if changes:
                report_lines.append(f'\n### Recent Changes (7d)')
                for c in changes[:5]:
                    report_lines.append(
                        f'- **{c["param"]}**: {c["old_value"]} → '
                        f'{c["new_value"]} @ {c["when"][:16]}'
                    )

            # Policy metrics
            pm = evaluation.get('policy_metrics', {})
            if pm:
                report_lines.append('\n### Policy Effectiveness (7d)')
                for policy, m in pm.items():
                    if m.get('error'):
                        continue
                    report_lines.append(
                        f'- **{policy}**: {m.get("action_count", 0)} actions, '
                        f'rollback rate {m.get("rollback_rate", 0):.0%}, '
                        f'verify pass {m.get("verification_pass_rate", 0):.0%}'
                    )

            return {
                'action': 'tuning_report',
                'report': '\n'.join(report_lines),
                'overrides': overrides,
                'recommendations': recs,
                'recent_changes': changes,
                'capped': evaluation.get('capped', False),
                'changes_today': evaluation.get('changes_today', 0),
            }

        elif action == 'budget_report':
            # Show current budget status, spend, and enforcement mode
            from core.services.ops_autopilot import BudgetController
            from django.utils import timezone as tz
            controller = BudgetController()
            try:
                report = controller.get_budget_report(tz.now())
            except Exception as e:
                return {
                    'action': 'budget_report',
                    'error': f'Budget report failed: {str(e)[:200]}',
                }

            report_lines = ['## Budget Report\n']
            report_lines.append(
                f'**Mode:** {report["mode"].upper()}'
            )
            report_lines.append(
                f'**Daily:** ${report["daily_spend"]:.2f} / '
                f'${report["daily_cap"]:.2f} '
                f'({report["daily_utilization"]:.0%}) — '
                f'{report["daily_calls"]} calls'
            )
            report_lines.append(
                f'**Hourly:** ${report["hourly_spend"]:.2f} / '
                f'${report["hourly_cap"]:.2f} '
                f'({report["hourly_utilization"]:.0%}) — '
                f'{report["hourly_calls"]} calls'
            )

            if report.get('top_agents'):
                report_lines.append('\n### Top Spenders (24h)')
                for a in report['top_agents']:
                    report_lines.append(
                        f'- **{a["agent_name"]}**: '
                        f'${a["total_cost"]:.4f} '
                        f'({a["call_count"]} calls)'
                    )

            if report.get('top_models'):
                report_lines.append('\n### Top Models (24h)')
                for m in report['top_models']:
                    report_lines.append(
                        f'- **{m["provider"]}/{m["model_id"]}**: '
                        f'${m["total_cost"]:.4f} '
                        f'({m["call_count"]} calls)'
                    )

            report_lines.append(
                f'\n**Soft limit:** {report["soft_limit_pct"]:.0%} '
                f'→ model downgrade'
            )
            report_lines.append(
                f'**Hard limit:** {report["hard_limit_pct"]:.0%} '
                f'→ freeze non-critical'
            )

            return {
                'action': 'budget_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'roi_report':
            # Show ROI attribution per agent and active throttles
            from core.services.ops_autopilot import ROIEnforcer
            from django.utils import timezone as tz
            enforcer = ROIEnforcer()
            try:
                report = enforcer.get_roi_report(tz.now())
            except Exception as e:
                return {
                    'action': 'roi_report',
                    'error': f'ROI report failed: {str(e)[:200]}',
                }

            report_lines = ['## QROI Attribution Report\n']
            report_lines.append(
                f'**Window:** {report["window_hours"]}h — '
                f'**Total spend:** ${report["total_spend"]:.2f} — '
                f'**Outcomes:** {report["total_outcomes"]}'
            )
            report_lines.append(
                f'**Active throttles:** {report["active_throttles"]} — '
                f'**Budget pressure:** '
                f'{"YES" if report["budget_pressure"] else "No"}'
            )

            # Quality summary
            qs = report.get('quality_summary', {})
            if qs:
                report_lines.append(
                    f'**Avg quality weight:** {qs.get("avg_quality_weight", 0):.3f} — '
                    f'**Agents with quality data:** '
                    f'{qs.get("agents_with_quality_data", 0)}'
                    f'/{qs.get("total_agents", 0)}'
                )

            if report.get('agents'):
                report_lines.append('\n### Agent QROI (worst → best)')
                for a in report['agents'][:10]:
                    detail = a.get('outcome_detail', {})
                    report_lines.append(
                        f'- **{a["agent_name"]}**: '
                        f'QROI {a.get("qroi", a["roi"]):.1%} '
                        f'(ROI {a["roi"]:.1%} × '
                        f'Q {a.get("quality_weight", 0.5):.2f}) — '
                        f'${a["cost"]:.4f} / {a["calls"]} calls → '
                        f'{a["outcomes"]} outcomes '
                        f'(exec: {detail.get("executions", 0)}, '
                        f'content: {detail.get("content", 0)}, '
                        f'impacts: {detail.get("impacts", 0)})'
                    )

            if report.get('throttle_recommendations'):
                report_lines.append('\n### Throttle Recommendations (by QROI)')
                for r in report['throttle_recommendations'][:5]:
                    report_lines.append(
                        f'- **{r["agent_name"]}**: '
                        f'{r["cooldown_minutes"]}min cooldown — '
                        f'{r["reason"]}'
                    )

            return {
                'action': 'roi_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'scheduler_report':
            # Show budget-aware scheduling state
            from core.services.ops_autopilot import BudgetAwareScheduler
            from django.utils import timezone as tz
            scheduler = BudgetAwareScheduler()
            try:
                report = scheduler.get_scheduler_report(tz.now())
            except Exception as e:
                return {
                    'action': 'scheduler_report',
                    'error': f'Scheduler report failed: {str(e)[:200]}',
                }

            report_lines = ['## Budget-Aware Scheduler Report\n']
            report_lines.append(
                f'**Budget:** {report["budget_pct"]:.0%} — '
                f'**Pressure:** {report["pressure"].upper()}'
            )
            report_lines.append(
                f'**Last 24h:** {report["defers_24h"]} deferred, '
                f'{report["downscopes_24h"]} downscoped'
            )
            report_lines.append(
                f'**Task tiers:** '
                f'Tier 1 (cheap): {report["tier_counts"].get(1, 0)}, '
                f'Tier 2 (moderate): {report["tier_counts"].get(2, 0)}, '
                f'Tier 3 (expensive): {report["tier_counts"].get(3, 0)}'
            )
            report_lines.append(
                f'**Deferable tasks:** {report["deferable_tasks"]} — '
                f'**Downscope-capable:** {report["downscope_tasks"]}'
            )

            if report.get('active_overrides'):
                report_lines.append('\n### Active Knob Overrides')
                for key, val in report['active_overrides'].items():
                    report_lines.append(f'- {key}: {val}')

            return {
                'action': 'scheduler_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'portfolio_report':
            # Show IQROI per desk and portfolio allocations
            from core.services.ops_autopilot import PortfolioAllocator
            from django.utils import timezone as tz
            allocator = PortfolioAllocator()
            try:
                report = allocator.get_portfolio_report(tz.now())
            except Exception as e:
                return {
                    'action': 'portfolio_report',
                    'error': f'Portfolio report failed: {str(e)[:200]}',
                }

            report_lines = ['## Portfolio Allocation Report\n']
            report_lines.append(
                f'**Window:** {report["window_hours"]}h — '
                f'**Total impact:** ${report["total_impact_usd"]:.2f} — '
                f'**Total cost:** ${report["total_cost_usd"]:.2f} — '
                f'**Events:** {report["total_events"]}'
            )

            if report.get('desks'):
                report_lines.append('\n### Desk IQROI (best → worst)')
                for desk, data in report['desks'].items():
                    report_lines.append(
                        f'- **{desk}**: '
                        f'IQROI {data["iqroi"]:.2f} — '
                        f'allocation {data["allocation"]}x — '
                        f'${data["impact_usd"]:.2f} impact + '
                        f'{data["impact_points"]} pts / '
                        f'${data["cost_usd"]:.4f} cost — '
                        f'{data["events"]} events'
                    )

            if report.get('active_allocations'):
                report_lines.append('\n### Active Allocations')
                for desk, alloc in report['active_allocations'].items():
                    report_lines.append(
                        f'- **{desk}**: '
                        f'{alloc.get("allocation", 1.0)}x '
                        f'(IQROI {alloc.get("iqroi", 0):.2f})'
                    )

            return {
                'action': 'portfolio_report',
                'report': '\n'.join(report_lines),
                **report,
            }

        elif action == 'backfill_impacts':
            # Backfill ImpactEvents from historical wagers, deliverables, revenue
            from core.services.ops_autopilot import ImpactCollector
            days = payload.get('days', 14)
            days = min(max(int(days), 1), 90)  # Clamp 1-90

            collector = ImpactCollector()
            try:
                result = collector.backfill(days=days)
            except Exception as e:
                return {
                    'action': 'backfill_impacts',
                    'error': f'Backfill failed: {str(e)[:200]}',
                }

            return {
                'action': 'backfill_impacts',
                'message': (
                    f"Backfilled {result['total_created']} impact events "
                    f"over {days} days: "
                    f"{result['wagers']} wagers, "
                    f"{result['deliverable_events']} deliverable events, "
                    f"{result['revenues']} revenues"
                ),
                **result,
            }

        elif action == 'attribution_debt_report':
            # Show attribution debt metrics — unattributed LLM spend
            from core.services.ops_autopilot import AttributionDebtController
            from django.utils import timezone as tz

            ctrl = AttributionDebtController()
            try:
                report = ctrl.get_debt_report(tz.now())
            except Exception as e:
                return {
                    'action': 'attribution_debt_report',
                    'error': f'Debt report failed: {str(e)[:200]}',
                }

            d24 = report['last_24h']
            d72 = report['last_72h']
            lines = [
                '## Attribution Debt Report\n',
                f'**Status:** {report["status"].upper()} — '
                f'**Mapped agents:** {report["mapped_agents"]} — '
                f'**Reallocation:** '
                f'{"BLOCKED" if report["reallocation_blocked"] else "allowed"} — '
                f'**Smoothing α:** {report["smoothing_alpha"]}',
                f'\n### Last 24h',
                f'- Total spend: ${d24["total_spend"]:.2f}',
                f'- Attributed: ${d24["attributed_spend"]:.2f}',
                f'- **Unattributed (debt): ${d24["unattributed_spend"]:.2f} '
                f'({d24["debt_pct"]:.1f}%)**',
            ]

            if d24.get('desk_breakdown'):
                lines.append('\n**Desk breakdown (attributed):**')
                for desk, cost in d24['desk_breakdown'].items():
                    lines.append(f'  - {desk}: ${cost:.4f}')

            if d24.get('top_unattributed'):
                lines.append('\n**Top unattributed agents:**')
                for u in d24['top_unattributed'][:10]:
                    lines.append(
                        f'  - {u["agent"]}: ${u["cost_usd"]:.4f}'
                    )

            lines.append(f'\n### Last 72h')
            lines.append(
                f'- Total: ${d72["total_spend"]:.2f} — '
                f'Debt: ${d72["unattributed_spend"]:.2f} '
                f'({d72["debt_pct"]:.1f}%)'
            )

            lines.append(
                f'\n### Thresholds'
                f'\n- Warning: {report["thresholds"]["warning_pct"]}%'
                f'\n- Critical (blocks reallocation): '
                f'{report["thresholds"]["critical_pct"]}%'
                f'\n- USD floor: ${report["thresholds"]["usd_floor"]}'
            )

            return {
                'action': 'attribution_debt_report',
                'report': '\n'.join(lines),
                **report,
            }

        elif action == 'experiment_report':
            # Show active and recent experiments
            from core.services.ops_autopilot import ExperimentEngine
            from django.utils import timezone as tz

            engine = ExperimentEngine()
            try:
                report = engine.get_experiments_report(tz.now())
            except Exception as e:
                return {
                    'action': 'experiment_report',
                    'error': f'Report failed: {str(e)[:200]}',
                }

            lines = ['## Experiment Engine Report\n']
            lines.append(
                f'**Supported policies:** '
                f'{", ".join(report["supported_policies"])}'
            )
            lines.append(
                f'**Supported metrics:** '
                f'{", ".join(report["supported_metrics"])}'
            )

            if report['active_experiments']:
                lines.append('\n### Active Experiments')
                for exp in report['active_experiments']:
                    lines.append(
                        f'- **{exp["policy_name"]}**: '
                        f'{exp.get("description", "")[:80]} '
                        f'(metric: {exp["success_metric"]}, '
                        f'started: {exp.get("started_at", "N/A")})'
                    )
            else:
                lines.append('\n*No active experiments.*')

            if report['recent_decisions']:
                lines.append('\n### Recent Decisions')
                for exp in report['recent_decisions']:
                    lines.append(
                        f'- {exp["policy_name"]}: '
                        f'**{exp["status"]}** — '
                        f'{exp.get("decision_reason", "")[:100]}'
                    )

            return {
                'action': 'experiment_report',
                'report': '\n'.join(lines),
                **report,
            }

        elif action == 'experiment_create':
            # Create a new experiment
            from core.services.ops_autopilot import ExperimentEngine

            policy = payload.get('policy_name', '')
            treatment = payload.get('treatment_params', {})
            metric = payload.get('success_metric', 'avg_desk_iqroi')
            desc = payload.get('description', '')

            if not policy or not treatment:
                return {
                    'action': 'experiment_create',
                    'error': (
                        'Required: policy_name and treatment_params. '
                        'Example: policy_name="portfolio_allocator", '
                        'treatment_params={"ALLOCATION_CEILING": 2.0}'
                    ),
                }

            engine = ExperimentEngine()
            result = engine.create_experiment(
                policy_name=policy,
                treatment_params=treatment,
                success_metric=metric,
                description=desc,
                created_by=PA_IDENTITY,
            )
            return {'action': 'experiment_create', **result}

        elif action == 'experiment_start':
            # Start a draft experiment
            from core.services.ops_autopilot import ExperimentEngine

            exp_id = payload.get('experiment_id', '')
            if not exp_id:
                return {
                    'action': 'experiment_start',
                    'error': 'Required: experiment_id',
                }

            engine = ExperimentEngine()
            result = engine.start_experiment(exp_id)
            return {'action': 'experiment_start', **result}

        elif action == 'decision_ledger_report':
            # Query decision ledger entries
            from core.models_decision_ledger import DecisionLedgerEntry

            policy_filter = payload.get('policy_name', '')
            decision_filter = payload.get('decision_type', '')
            days = int(payload.get('days') or 1)  # Session 1228 PR-B autofill safety
            limit = min(int(payload.get('limit', 50)), 200)

            cutoff = timezone.now() - timedelta(days=days)
            qs = DecisionLedgerEntry.objects.filter(cycle_ts__gte=cutoff)

            if policy_filter:
                qs = qs.filter(policy=policy_filter)
            if decision_filter:
                qs = qs.filter(decision_type=decision_filter)

            entries = list(
                qs.order_by('-cycle_ts').values(
                    'cycle_id', 'cycle_ts', 'policy', 'decision_type',
                    'decision_summary', 'duration_ms', 'experiment_id',
                )[:limit]
            )

            # Serialize
            for e in entries:
                for k, v in e.items():
                    if hasattr(v, 'isoformat'):
                        e[k] = v.isoformat()
                    elif hasattr(v, 'hex'):
                        e[k] = str(v)

            # Summary stats
            from django.db.models import Count, Avg
            stats = dict(
                qs.values('decision_type').annotate(
                    count=Count('id'),
                    avg_ms=Avg('duration_ms'),
                ).values_list('decision_type', 'count')
            )

            # Distinct cycles
            cycle_count = qs.values('cycle_id').distinct().count()

            return {
                'action': 'decision_ledger_report',
                'period_days': days,
                'total_entries': len(entries),
                'cycles': cycle_count,
                'decision_type_counts': stats,
                'entries': entries,
            }

        elif action == 'timeout_ladder_report':
            # Show agents currently on the timeout remediation ladder
            from core.services.ops_autopilot import TimeoutRemediationPlaybook

            playbook = TimeoutRemediationPlaybook()
            report = playbook.get_ladder_report()

            # Add recent ladder actions
            recent_actions = list(
                AutopilotAction.objects.filter(
                    policy='timeout_remediation_playbook',
                ).order_by('-created_at').values(
                    'agent_name', 'action_type', 'evidence', 'created_at',
                )[:10]
            )
            for a in recent_actions:
                if hasattr(a['created_at'], 'isoformat'):
                    a['created_at'] = a['created_at'].isoformat()

            return {
                'action': 'timeout_ladder_report',
                **report,
                'recent_actions': recent_actions,
            }

        elif action == 'deliberation_pipeline_report':
            # Show deliberation pipeline health + remediation ladder state
            from core.services.ops_autopilot import DeliberationRemediationPlaybook

            playbook = DeliberationRemediationPlaybook()
            report = playbook.get_pipeline_report(timezone.now())
            return {
                'action': 'deliberation_pipeline_report',
                **report,
            }

        elif action == 'backlog_report':
            # Show deliverable backlog health + governor state
            from core.services.ops_autopilot import BacklogGovernor

            governor = BacklogGovernor()
            report = governor.get_backlog_report(timezone.now())
            return {
                'action': 'backlog_report',
                **report,
            }

        elif action == 'goal_report':
            # Show goal-aware allocation state — weights, metrics, desk scores
            from core.services.ops_autopilot import GoalAwareAllocator

            allocator = GoalAwareAllocator()
            report = allocator.get_goal_report(timezone.now())
            return {
                'action': 'goal_report',
                **report,
            }

        elif action == 'goal_set_weights':
            # Update goal objective weights
            from core.services.ops_autopilot import GoalAwareAllocator

            goal_weights = payload.get('goal_weights')
            if not goal_weights or not isinstance(goal_weights, dict):
                return {
                    'action': 'goal_set_weights',
                    'error': 'goal_weights dict required (e.g., {"sports_profit": 0.3, "confirmed_revenue": 0.3, ...})',
                }

            allocator = GoalAwareAllocator()
            result = allocator.set_weights(goal_weights)
            return {
                'action': 'goal_set_weights',
                **result,
            }

        elif action == 'attribution_report':
            # Multi-touch attribution report across desks
            from django.utils import timezone as tz
            from core.services.ops_autopilot import MultiTouchAttributor

            attributor = MultiTouchAttributor()
            report = attributor.get_attribution_report(tz.now())
            return {
                'action': 'attribution_report',
                **report,
            }

        elif action == 'policy_conflict_report':
            # Policy arbitrator conflict detection
            from django.utils import timezone as tz
            from core.services.ops_autopilot import PolicyArbitrator

            arbitrator = PolicyArbitrator()
            report = arbitrator.get_conflict_report(
                tz.now(),
                knob=payload.get('knob', ''),
                policy=payload.get('policy_filter', ''),
            )
            return {
                'action': 'policy_conflict_report',
                **report,
            }

        elif action == 'latest_overrides_snapshot':
            # PolicyArbitrator snapshot — latest, or time-travel via `at`.
            # Session 1163 B-style storage (append-only per-cycle rows in
            # FinalAppliedOverrides). See Disclosure L §14.7 + narrative
            # SELF_TUNING_AND_EXPERIMENTATION.md §6.4.
            from core.services.ops_autopilot import PolicyArbitrator

            arbitrator = PolicyArbitrator()
            snapshot = arbitrator.get_latest_snapshot(
                at=payload.get('at'),
            )
            return {
                'action': 'latest_overrides_snapshot',
                **snapshot,
            }

        elif action == 'release_report':
            # Deploy/release status report
            from django.utils import timezone as tz
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            report = governor.get_release_report(tz.now())
            return {
                'action': 'release_report',
                **report,
            }

        elif action == 'release_freeze':
            # Manually freeze deploys
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            result = governor.set_freeze(True, reason='manual PA freeze')
            return {
                'action': 'release_freeze',
                **result,
            }

        elif action == 'release_unfreeze':
            # Manually unfreeze deploys
            from core.services.ops_autopilot import ReleaseGovernor

            governor = ReleaseGovernor()
            result = governor.set_freeze(False, reason='manual PA unfreeze')
            return {
                'action': 'release_unfreeze',
                **result,
            }

        elif action == 'revenue_pipeline_report':
            # Revenue pipeline health report
            from django.utils import timezone as tz
            from core.services.ops_autopilot import RevenuePipelineAutomator

            automator = RevenuePipelineAutomator()
            report = automator.get_pipeline_report(tz.now())
            return {
                'action': 'revenue_pipeline_report',
                **report,
            }

        elif action == 'prospecting_queue':
            # Outbound lead engine — top scored leads
            from django.utils import timezone as tz
            from core.services.ops_autopilot import OutboundLeadEngine

            engine = OutboundLeadEngine()
            report = engine.get_prospecting_queue(tz.now())
            return {'action': 'prospecting_queue', **report}

        elif action == 'lead_source_report':
            # Which spider sources produce leads
            from django.utils import timezone as tz
            from core.services.ops_autopilot import OutboundLeadEngine

            engine = OutboundLeadEngine()
            report = engine.get_lead_source_report(tz.now())
            return {'action': 'lead_source_report', **report}

        elif action == 'outreach_inbox':
            # Outreach drafts pending approval
            from core.services.ops_autopilot import OutreachSequencer
            from django.utils import timezone as tz

            sequencer = OutreachSequencer()
            report = sequencer.get_inbox(tz.now())
            return {'action': 'outreach_inbox', **report}

        elif action == 'outreach_approve':
            # Approve a draft for sending
            from core.services.ops_autopilot import OutreachSequencer

            draft_id = payload.get('draft_id', '')
            edited_text = payload.get('edited_text', '')
            if not draft_id:
                return {'error': 'draft_id is required'}
            sequencer = OutreachSequencer()
            result = sequencer.approve_draft(draft_id, edited_text)
            return {'action': 'outreach_approve', **result}

        elif action == 'outreach_reject':
            # Reject a draft
            from core.services.ops_autopilot import OutreachSequencer

            draft_id = payload.get('draft_id', '')
            reason = payload.get('reason', '')
            if not draft_id:
                return {'error': 'draft_id is required'}
            sequencer = OutreachSequencer()
            result = sequencer.reject_draft(draft_id, reason)
            return {'action': 'outreach_reject', **result}

        elif action == 'outreach_metrics_report':
            # Outreach conversion funnel
            from core.services.ops_autopilot import OutreachSequencer
            from django.utils import timezone as tz

            sequencer = OutreachSequencer()
            report = sequencer.get_metrics_report(tz.now())
            return {'action': 'outreach_metrics_report', **report}

        elif action == 'outreach_generate':
            # Session 1224 P1 — generate touch=1 OutreachDrafts from Opportunity rows
            from core.services.ops_autopilot import OpportunityDraftGenerator

            limit = payload.get('limit')
            scope = payload.get('scope', 'all')
            offers = payload.get('offers')
            if isinstance(offers, str):
                offers = [o.strip() for o in offers.split(',') if o.strip()]
            report = OpportunityDraftGenerator.generate(
                limit=int(limit) if limit is not None else None,
                scope=scope,
                offers=offers,
            )
            return {'action': 'outreach_generate', **report}

        elif action == 'close_pack_generate':
            # Generate a close pack (proposal + contract + invoice)
            from core.services.ops_autopilot import CloseTheDealEngine

            opportunity_id = payload.get('opportunity_id', '')
            offer_key = payload.get('offer_key', 'consulting')
            price = payload.get('price')
            timeline_days = payload.get('timeline_days', 14)

            if not price:
                return {'error': 'price is required for close_pack_generate'}

            engine = CloseTheDealEngine()
            result = engine.generate_pack(
                opportunity_id=opportunity_id,
                offer_key=offer_key,
                price=float(price),
                timeline_days=int(timeline_days),
            )
            return {'action': 'close_pack_generate', **result}

        elif action == 'close_pack_inbox':
            # Pending close packs for approval
            from core.services.ops_autopilot import CloseTheDealEngine
            from django.utils import timezone as tz

            engine = CloseTheDealEngine()
            inbox = engine.get_inbox(tz.now())
            return {'action': 'close_pack_inbox', **inbox}

        elif action == 'close_pack_approve':
            # Approve a close pack
            from core.services.ops_autopilot import CloseTheDealEngine

            pack_id = payload.get('pack_id')
            if not pack_id:
                return {'error': 'pack_id is required for close_pack_approve'}

            engine = CloseTheDealEngine()
            result = engine.approve_pack(pack_id)
            return {'action': 'close_pack_approve', **result}

        elif action == 'close_pack_metrics_report':
            # Deal metrics — win rate, revenue, etc.
            from core.services.ops_autopilot import CloseTheDealEngine
            from django.utils import timezone as tz

            engine = CloseTheDealEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'close_pack_metrics_report', **report}

        elif action == 'engagement_inbox':
            # Inbound engagement events
            from core.services.ops_autopilot import EngagementEngine
            from django.utils import timezone as tz

            status_filter = payload.get('status_filter', 'unread')
            engine = EngagementEngine()
            inbox = engine.get_inbox(tz.now(), status_filter=status_filter)
            return {'action': 'engagement_inbox', **inbox}

        elif action == 'engagement_classify':
            # Classify engagement intent
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            intent = payload.get('intent')
            if not event_id or not intent:
                return {'error': 'event_id and intent are required'}

            engine = EngagementEngine()
            result = engine.classify_event(
                event_id=event_id,
                intent=intent,
                summary=payload.get('summary', ''),
            )
            return {'action': 'engagement_classify', **result}

        elif action == 'engagement_draft_reply':
            # Draft a reply for approval
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            reply_text = payload.get('reply_text')
            if not event_id or not reply_text:
                return {'error': 'event_id and reply_text are required'}

            engine = EngagementEngine()
            result = engine.draft_reply(event_id=event_id, reply_text=reply_text)
            return {'action': 'engagement_draft_reply', **result}

        elif action == 'engagement_approve_reply':
            # Approve a draft reply
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            if not event_id:
                return {'error': 'event_id is required'}

            engine = EngagementEngine()
            result = engine.approve_reply(
                event_id=event_id,
                edited_text=payload.get('edited_text', ''),
            )
            return {'action': 'engagement_approve_reply', **result}

        elif action == 'engagement_disqualify':
            # Disqualify an engagement
            from core.services.ops_autopilot import EngagementEngine

            event_id = payload.get('event_id')
            if not event_id:
                return {'error': 'event_id is required'}

            engine = EngagementEngine()
            result = engine.disqualify(
                event_id=event_id,
                reason=payload.get('reason', ''),
            )
            return {'action': 'engagement_disqualify', **result}

        elif action == 'engagement_metrics_report':
            # Engagement funnel metrics
            from core.services.ops_autopilot import EngagementEngine
            from django.utils import timezone as tz

            engine = EngagementEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'engagement_metrics_report', **report}

        elif action == 'meeting_create':
            # Create a new meeting
            from core.services.ops_autopilot import MeetingEngine

            scheduled_at = payload.get('scheduled_at')
            if not scheduled_at:
                return {'error': 'scheduled_at is required (ISO datetime)'}

            engine = MeetingEngine()
            result = engine.create_meeting(
                opportunity_id=payload.get('opportunity_id', ''),
                scheduled_at=scheduled_at,
                title=payload.get('title', ''),
                channel=payload.get('channel', 'zoom'),
                duration_minutes=int(payload.get('duration_minutes') or 30),  # Session 1228 PR-B autofill safety
                meeting_link=payload.get('meeting_link', ''),
                prospect_name=payload.get('prospect_name', ''),
                prospect_company=payload.get('prospect_company', ''),
            )
            return {'action': 'meeting_create', **result}

        elif action == 'meeting_inbox':
            # Meeting inbox by filter
            from core.services.ops_autopilot import MeetingEngine
            from django.utils import timezone as tz

            filter_type = payload.get('filter_type', 'upcoming')
            engine = MeetingEngine()
            inbox = engine.get_inbox(tz.now(), filter_type=filter_type)
            return {'action': 'meeting_inbox', **inbox}

        elif action == 'meeting_brief':
            # Generate pre-call brief
            from core.services.ops_autopilot import MeetingEngine

            meeting_id = payload.get('meeting_id')
            if not meeting_id:
                return {'error': 'meeting_id is required'}

            engine = MeetingEngine()
            result = engine.generate_brief(meeting_id=meeting_id)
            return {'action': 'meeting_brief', **result}

        elif action == 'meeting_recap':
            # Add post-meeting recap
            from core.services.ops_autopilot import MeetingEngine

            meeting_id = payload.get('meeting_id')
            if not meeting_id:
                return {'error': 'meeting_id is required'}

            engine = MeetingEngine()
            result = engine.add_recap(
                meeting_id=meeting_id,
                notes=payload.get('notes', ''),
                outcome=payload.get('outcome', ''),
                next_steps=payload.get('next_steps', ''),
            )
            return {'action': 'meeting_recap', **result}

        elif action == 'meeting_metrics_report':
            # Meeting pipeline metrics
            from core.services.ops_autopilot import MeetingEngine
            from django.utils import timezone as tz

            engine = MeetingEngine()
            report = engine.get_metrics_report(tz.now())
            return {'action': 'meeting_metrics_report', **report}

        # ── Governance & Safe-Mode Controls (Policy 30) ──

        elif action == 'governance_status':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            status = engine.get_status()
            return {'action': 'governance_status', **status}

        elif action == 'governance_set_mode':
            from core.services.ops_autopilot import GovernanceEngine

            mode = payload.get('mode', '')
            if not mode:
                return {'error': 'mode is required (normal/throttle/freeze/safe_mode)'}

            engine = GovernanceEngine()
            result = engine.set_mode(
                mode=mode,
                reason=payload.get('reason', ''),
                scope=payload.get('scope', 'global'),
                scope_target=payload.get('scope_target', ''),
                ttl_hours=payload.get('ttl_hours'),
                set_by='pa_tool',
            )
            return {'action': 'governance_set_mode', **result}

        elif action == 'governance_kill_switch':
            from core.services.ops_autopilot import GovernanceEngine

            target = payload.get('target', '')
            if not target:
                return {'error': 'target is required (scheduler/queue/agent_family/publishing/outbound/deploys)'}

            engine = GovernanceEngine()
            result = engine.activate_kill_switch(
                target=target,
                reason=payload.get('reason', ''),
                target_detail=payload.get('target_detail', ''),
                ttl_hours=payload.get('ttl_hours'),
                activated_by='pa_tool',
            )
            return {'action': 'governance_kill_switch', **result}

        elif action == 'governance_deactivate_switch':
            from core.services.ops_autopilot import GovernanceEngine

            switch_id = payload.get('switch_id', '')
            if not switch_id:
                return {'error': 'switch_id is required'}

            engine = GovernanceEngine()
            result = engine.deactivate_kill_switch(switch_id)
            return {'action': 'governance_deactivate_switch', **result}

        elif action == 'governance_throttle_report':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            report = engine.get_throttle_report()
            return {'action': 'governance_throttle_report', **report}

        elif action == 'governance_audit':
            from core.services.ops_autopilot import GovernanceEngine

            engine = GovernanceEngine()
            audit = engine.get_audit_log(limit=payload.get('limit', 20))
            return {'action': 'governance_audit', **audit}

        # ── Revenue Pipeline Orchestrator (Policy 31) ──

        elif action == 'revenue_full_pipeline':
            from core.services.ops_autopilot import RevenueOrchestrator

            engine = RevenueOrchestrator()
            pipeline = engine.get_full_pipeline()
            return {'action': 'revenue_full_pipeline', **pipeline}

        elif action == 'revenue_funnel':
            from core.services.ops_autopilot import RevenueOrchestrator

            days = int(payload.get('days') or 30)  # Session 1228 PR-B autofill safety
            engine = RevenueOrchestrator()
            funnel = engine.get_conversion_funnel(days=days)
            return {'action': 'revenue_funnel', **funnel}

        elif action == 'revenue_forecast':
            from core.services.ops_autopilot import RevenueOrchestrator

            engine = RevenueOrchestrator()
            forecast = engine.get_revenue_forecast()
            return {'action': 'revenue_forecast', **forecast}

        # ── Knowledge & Citation Engine (Policy 32) ──────────────
        elif action == 'knowledge_health':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            health = engine.get_health()
            return {'action': 'knowledge_health', **health}

        elif action == 'knowledge_citation_report':
            from core.services.ops_autopilot import KnowledgeEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = KnowledgeEngine()
            report = engine.get_citation_report(days=days)
            return {'action': 'knowledge_citation_report', **report}

        elif action == 'knowledge_source_report':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            report = engine.get_source_report()
            return {'action': 'knowledge_source_report', **report}

        elif action == 'knowledge_staleness_report':
            from core.services.ops_autopilot import KnowledgeEngine

            engine = KnowledgeEngine()
            report = engine.get_staleness_report()
            return {'action': 'knowledge_staleness_report', **report}

        # ── Close Pack Autonomy (Policy 33) ──────────────────────
        elif action == 'close_pack_followup_queue':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            queue = engine.get_followup_queue()
            return {'action': 'close_pack_followup_queue', **queue}

        elif action == 'close_pack_risk_report':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            report = engine.get_risk_report()
            return {'action': 'close_pack_risk_report', **report}

        elif action == 'close_pack_velocity':
            from core.services.ops_autopilot import ClosePackAutonomyEngine

            engine = ClosePackAutonomyEngine()
            report = engine.get_velocity_report()
            return {'action': 'close_pack_velocity', **report}

        # ── Engagement Autonomy (Policy 34) ──────────────────────
        elif action == 'engagement_sla_queue':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            engine = EngagementAutonomyEngine()
            queue = engine.get_sla_queue()
            return {'action': 'engagement_sla_queue', **queue}

        elif action == 'engagement_meeting_suggestions':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            engine = EngagementAutonomyEngine()
            suggestions = engine.get_meeting_suggestions()
            return {'action': 'engagement_meeting_suggestions', **suggestions}

        elif action == 'engagement_conversion_report':
            from core.services.ops_autopilot import EngagementAutonomyEngine

            days = int(payload.get('days') or 30)  # Session 1228 PR-B autofill safety
            engine = EngagementAutonomyEngine()
            report = engine.get_conversion_report(days=days)
            return {'action': 'engagement_conversion_report', **report}

        # ── Growth & Distribution (Policy 35) ──
        elif action == 'growth_candidates':
            from core.services.ops_autopilot import GrowthEngine

            limit = int(payload.get('limit', 20))
            engine = GrowthEngine()
            candidates = engine.get_candidates(limit=limit)
            return {'action': 'growth_candidates', **candidates}

        elif action == 'growth_schedule':
            from core.services.ops_autopilot import GrowthEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = GrowthEngine()
            schedule = engine.get_schedule(days=days)
            return {'action': 'growth_schedule', **schedule}

        elif action == 'growth_channel_report':
            from core.services.ops_autopilot import GrowthEngine

            engine = GrowthEngine()
            report = engine.get_channel_report()
            return {'action': 'growth_channel_report', **report}

        elif action == 'growth_funnel':
            from core.services.ops_autopilot import GrowthEngine

            days = int(payload.get('days') or 30)  # Session 1228 PR-B autofill safety
            engine = GrowthEngine()
            funnel = engine.get_funnel(days=days)
            return {'action': 'growth_funnel', **funnel}

        # ── Capacity Planning (Policy 36) ──
        elif action == 'capacity_forecast':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = CapacityEngine()
            forecast = engine.get_capacity_forecast(hours=hours)
            return {'action': 'capacity_forecast', **forecast}

        elif action == 'capacity_bottleneck_report':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = CapacityEngine()
            report = engine.get_bottleneck_report(hours=hours)
            return {'action': 'capacity_bottleneck_report', **report}

        elif action == 'capacity_throttle_plan':
            from core.services.ops_autopilot import CapacityEngine

            engine = CapacityEngine()
            plan = engine.get_throttle_plan()
            return {'action': 'capacity_throttle_plan', **plan}

        elif action == 'capacity_budget_envelope':
            from core.services.ops_autopilot import CapacityEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = CapacityEngine()
            envelope = engine.get_budget_envelope(days=days)
            return {'action': 'capacity_budget_envelope', **envelope}

        # ── Security & Abuse (Policy 37) ──
        elif action == 'security_permission_drift':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = SecurityEngine()
            report = engine.get_permission_drift_report(hours=hours)
            return {'action': 'security_permission_drift', **report}

        elif action == 'security_abuse_queue':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            limit = int(payload.get('limit', 50))
            engine = SecurityEngine()
            queue = engine.get_abuse_risk_queue(hours=hours, limit=limit)
            return {'action': 'security_abuse_queue', **queue}

        elif action == 'security_containment_plan':
            from core.services.ops_autopilot import SecurityEngine

            # Session 1228 PR-A — belt-and-suspenders write gate. Live
            # security ops (rate limits, switch expiry cleanup, etc.) —
            # autofilled dry_run=False must not flip a plain preview call
            # into a live containment action. Memory rule:
            # feedback_llm_autofills_boolean_params_with_false.
            from core.services.td_autofill_safety import require_write_authorization
            dry_run, _write_ok = require_write_authorization(payload)
            engine = SecurityEngine()
            plan = engine.get_containment_plan(dry_run=dry_run)
            return {'action': 'security_containment_plan', **plan}

        elif action == 'security_secrets_scan':
            from core.services.ops_autopilot import SecurityEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = SecurityEngine()
            scan = engine.get_secrets_scan(days=days)
            return {'action': 'security_secrets_scan', **scan}

        elif action == 'compliance_pii_scan':
            from core.services.ops_autopilot import ComplianceEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            limit = int(payload.get('limit', 50))
            engine = ComplianceEngine()
            scan = engine.get_pii_scan(days=days, limit=limit)
            return {'action': 'compliance_pii_scan', **scan}

        elif action == 'compliance_retention_report':
            from core.services.ops_autopilot import ComplianceEngine

            engine = ComplianceEngine()
            report = engine.get_retention_report()
            return {'action': 'compliance_retention_report', **report}

        elif action == 'compliance_access_audit':
            from core.services.ops_autopilot import ComplianceEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = ComplianceEngine()
            audit = engine.get_access_audit(hours=hours)
            return {'action': 'compliance_access_audit', **audit}

        elif action == 'compliance_report':
            from core.services.ops_autopilot import ComplianceEngine

            engine = ComplianceEngine()
            report = engine.get_compliance_report()
            return {'action': 'compliance_report', **report}

        elif action == 'integrity_quality_report':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = DataIntegrityEngine()
            report = engine.get_quality_report(hours=hours)
            return {'action': 'integrity_quality_report', **report}

        elif action == 'integrity_null_spike_scan':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = DataIntegrityEngine()
            scan = engine.get_null_spike_scan(hours=hours)
            return {'action': 'integrity_null_spike_scan', **scan}

        elif action == 'integrity_duplicate_report':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
            engine = DataIntegrityEngine()
            report = engine.get_duplicate_report(hours=hours)
            return {'action': 'integrity_duplicate_report', **report}

        elif action == 'integrity_reliability_scores':
            from core.services.ops_autopilot import DataIntegrityEngine

            engine = DataIntegrityEngine()
            scores = engine.get_reliability_scores()
            return {'action': 'integrity_reliability_scores', **scores}

        elif action == 'value_events_report':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = ValueRealizationEngine()
            report = engine.get_value_events_report(days=days)
            return {'action': 'value_events_report', **report}

        elif action == 'value_outcome_rates':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days') or 30)  # Session 1228 PR-B autofill safety
            engine = ValueRealizationEngine()
            rates = engine.get_outcome_rates(days=days)
            return {'action': 'value_outcome_rates', **rates}

        elif action == 'value_usage_gaps':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days') or 7)  # Session 1228 PR-B autofill safety
            engine = ValueRealizationEngine()
            gaps = engine.get_usage_gaps(days=days)
            return {'action': 'value_usage_gaps', **gaps}

        elif action == 'value_realization_summary':
            from core.services.ops_autopilot import ValueRealizationEngine

            engine = ValueRealizationEngine()
            summary = engine.get_realization_summary()
            return {'action': 'value_realization_summary', **summary}

        elif action == 'backfill_failure_reasons':
            # Re-classify sessions that have UNKNOWN or empty failure_reason_code
            from core.models_deliberation import DeliberationSession, classify_failure_reason
            from django.db.models import Q

            sessions = DeliberationSession.objects.filter(
                status='failed',
            ).filter(
                Q(failure_reason_code='') | Q(failure_reason_code='UNKNOWN')
            )
            updated = 0
            for s in sessions:
                detail = getattr(s, 'failure_detail', '') or ''
                if not detail:
                    continue
                new_code = classify_failure_reason(detail)
                if new_code != 'UNKNOWN':
                    s.failure_reason_code = new_code
                    s.save(update_fields=['failure_reason_code'])
                    updated += 1

            return {
                'action': 'backfill_failure_reasons',
                'scanned': sessions.count() + updated,  # approximate
                'reclassified': updated,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Valid: status, history, run, config, dry_run_report, drift_scan, "
                f"tuning_report, budget_report, roi_report, scheduler_report, "
                f"backfill_failure_reasons"
            )

    def _handle_workspace_budget(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """S2847 A1 W1 Phase 3 — per-workspace budget cap management.

        Actions: set_cap / get_status / clear_freeze / list_caps / clear_cap.
        Mutations require caller to own the workspace or be staff, and are
        recorded as AutopilotAction rows for symmetric visibility with the
        automatic enforce_workspace_freeze audit trail.
        """
        from django.contrib.auth import get_user_model
        from django.utils import timezone as tz
        from core.services.ops_autopilot.budget import BudgetController
        from core.models_skin_layer import ProjectWorkspace

        action = payload.get('action', 'get_status')
        workspace_id = payload.get('workspace_id')
        daily_cap_usd = payload.get('daily_cap_usd')

        controller = BudgetController()
        now = tz.now()

        def _resolve_workspace(wid):
            """Return ProjectWorkspace or an error dict — never raises."""
            if not wid:
                return None, {
                    'error': 'workspace_id is required for this action',
                }
            try:
                return ProjectWorkspace.objects.get(id=wid), None
            except (ProjectWorkspace.DoesNotExist, ValueError):
                return None, {
                    'error': f'workspace_id {wid!r} not found',
                }

        def _authorize_mutation(workspace):
            """True/error dict — caller must own workspace or be staff."""
            if user_id is None:
                return {
                    'error': (
                        'authentication required for workspace_budget mutations'
                    ),
                }
            if workspace.user_id == user_id:
                return None
            try:
                User = get_user_model()
                actor = User.objects.get(id=user_id)
            except Exception:
                return {
                    'error': f'actor user_id={user_id} not found',
                }
            if getattr(actor, 'is_staff', False):
                return None
            return {
                'error': (
                    f'user_id={user_id} is not owner of workspace '
                    f'{workspace.id} and is not staff — mutation denied'
                ),
            }

        # S2849 W2 #2a — NULL-bucket copy included in read responses so
        # operators know workspace caps only govern attributed calls.
        _null_bucket_note = (
            'workspace caps apply only to workspace-attributed LLMCallLog '
            'rows (currently PA path); NULL-bucket is governed by GLOBAL '
            'budget controls'
        )

        def _status_context(workspace, *, cleared_flag):
            """S2858 PR#1 — return post-clear spend/threshold context.

            Used by clear_freeze + clear_downgrade to inline enough state
            that operators don't have to re-call get_status. `cleared_flag`
            is 'freeze' or 'downgrade' and drives which re-flag threshold
            + reason string we compute against.

            Enforcement reads the EXPLICIT cap only (not the effective
            default fallback) — so re_flag_likely is computed against
            explicit cap and, when the workspace only has a default cap,
            re_flag_likely is False with an explanatory reason (per
            Rigby SIGN Q5 concern 1).
            """
            from core.services.ops_autopilot.config import AutopilotConfig
            spend = controller.compute_workspace_spend(
                now, workspace_id=workspace.id,
            )
            daily_total = spend['daily_total']
            explicit_cap = controller.get_workspace_daily_cap(workspace.id)
            effective = controller.get_effective_workspace_daily_cap(
                workspace.id,
            )
            effective_cap = effective['cap']
            cap_source = effective['source']

            if effective_cap and effective_cap > 0:
                spend_pct_of_cap = round(100 * daily_total / effective_cap)
            else:
                spend_pct_of_cap = None

            re_flag_likely = False
            re_flag_reason = None
            threshold = None
            threshold_pct = None

            if explicit_cap is None:
                enforcement_note = (
                    f'no explicit cap on this workspace '
                    f'(cap_source={cap_source}) — enforcement will NOT '
                    f're-fire until an explicit cap is set via set_cap '
                    f'or backfill_defaults; effective_cap is display-only'
                )
                re_flag_reason = enforcement_note
            elif cleared_flag == 'freeze':
                threshold = explicit_cap
                threshold_pct = 100
                enforcement_note = (
                    'freeze re-fires when daily spend >= explicit cap'
                )
                if daily_total >= explicit_cap:
                    re_flag_likely = True
                    re_flag_reason = (
                        f'daily spend ${daily_total:.2f} still >= '
                        f'explicit cap ${explicit_cap:.2f} — freeze '
                        f'will re-fire on next enforce_ call'
                    )
                else:
                    re_flag_reason = (
                        f'daily spend ${daily_total:.2f} < explicit cap '
                        f'${explicit_cap:.2f} — freeze will not re-fire '
                        f'unless additional spend crosses the cap'
                    )
            else:  # cleared_flag == 'downgrade'
                soft_pct = AutopilotConfig.BUDGET_SOFT_LIMIT_PCT
                threshold = explicit_cap * soft_pct
                threshold_pct = round(soft_pct * 100)
                enforcement_note = (
                    f'downgrade re-fires when daily spend >= '
                    f'{threshold_pct}% of explicit cap'
                )
                if daily_total >= threshold:
                    re_flag_likely = True
                    re_flag_reason = (
                        f'daily spend ${daily_total:.2f} still >= '
                        f'${threshold:.2f} ({threshold_pct}% of cap '
                        f'${explicit_cap:.2f}) — downgrade will re-fire '
                        f'on next enforce_ call'
                    )
                else:
                    re_flag_reason = (
                        f'daily spend ${daily_total:.2f} < '
                        f'${threshold:.2f} ({threshold_pct}% of cap '
                        f'${explicit_cap:.2f}) — downgrade will not '
                        f're-fire unless spend crosses the soft threshold'
                    )

            return {
                'daily_total': daily_total,
                'effective_cap': effective_cap,
                'cap_source': cap_source,
                'spend_pct_of_cap': spend_pct_of_cap,
                're_flag_likely': re_flag_likely,
                're_flag_reason': re_flag_reason,
                'refire_threshold': threshold,
                'refire_threshold_pct_of_cap': threshold_pct,
                'enforcement_note': enforcement_note,
            }

        if action == 'get_status':
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}
            spend = controller.compute_workspace_spend(now, workspace_id=workspace.id)
            cap = controller.get_workspace_daily_cap(workspace.id)
            effective = controller.get_effective_workspace_daily_cap(workspace.id)
            default_cap = controller.get_workspace_default_cap()
            is_frozen = controller.is_workspace_frozen(workspace.id)
            is_downgraded = controller.is_workspace_downgraded(workspace.id)
            return {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'cap': cap,
                'effective_cap': effective['cap'],
                'cap_source': effective['source'],
                'default_cap': default_cap,
                'daily_total': spend['daily_total'],
                'daily_calls': spend['daily_calls'],
                'hourly_total': spend['hourly_total'],
                'hourly_calls': spend['hourly_calls'],
                'is_frozen': is_frozen,
                'is_downgraded': is_downgraded,
                'enforcement_tier': 'downgrade_and_freeze',
                'window_note': (
                    'daily = last 24h sliding window (not calendar day)'
                ),
                'null_bucket_note': _null_bucket_note,
            }

        if action == 'list_caps':
            include_defaults = bool(payload.get('include_defaults', False))
            default_cap = controller.get_workspace_default_cap()

            # S2852 — same auth scope as enforcement_report (S2851 #3.1).
            # Non-staff sees only own workspaces; staff sees all;
            # unauthenticated returns an empty list + scope_note (was
            # previously exposing all workspace names + spend to any
            # caller — Rigby SIGN Q3 latent-overexposure finding).
            is_staff = False
            if user_id is not None:
                try:
                    User = get_user_model()
                    actor = User.objects.get(id=user_id)
                    is_staff = bool(getattr(actor, 'is_staff', False))
                except Exception:
                    is_staff = False

            # Rigby SIGN Q1 nit: keep scoped_ids as native workspace-id
            # values (UUIDs) — don't str()-coerce early. The str() dance is
            # only needed for the include_defaults=False loop where
            # controller.list_workspace_caps() returns str workspace_ids;
            # do that stringify at the comparison site, not at build time.
            if user_id is None:
                scoped_ids: Optional[set] = set()
                scope_note = (
                    'unauthenticated caller — per-workspace rows omitted'
                )
            elif is_staff:
                scoped_ids = None  # None = no filter, staff sees all
                scope_note = 'staff scope — all workspaces'
            else:
                scoped_ids = set(
                    ProjectWorkspace.objects
                    .filter(user_id=user_id)
                    .values_list('id', flat=True)
                )
                scope_note = f'auto-scoped to workspaces owned by user_id={user_id}'

            enriched = []
            if include_defaults:
                ws_qs = ProjectWorkspace.objects.all().only('id', 'name')
                if scoped_ids is not None:
                    ws_qs = ws_qs.filter(id__in=scoped_ids)
                for ws in ws_qs:
                    effective = controller.get_effective_workspace_daily_cap(ws.id)
                    if effective['cap'] is None:
                        continue
                    spend = controller.compute_workspace_spend(
                        now, workspace_id=ws.id,
                    )
                    enriched.append({
                        'workspace_id': str(ws.id),
                        'workspace_name': ws.name,
                        'cap': controller.get_workspace_daily_cap(ws.id),
                        'effective_cap': effective['cap'],
                        'cap_source': effective['source'],
                        'daily_total': spend['daily_total'],
                        'is_frozen': controller.is_workspace_frozen(ws.id),
                        'is_downgraded': controller.is_workspace_downgraded(ws.id),
                    })
            else:
                import uuid as _uuid
                rows = controller.list_workspace_caps()
                # S2858 PR#2 — batch ProjectWorkspace name lookup to eliminate
                # per-row ProjectWorkspace.objects.get() N+1 (was firing one
                # query per row inside the loop). Pass 1 collects valid+
                # scoped UUIDs; single filter().in_bulk() fetches all names;
                # pass 2 builds rows via dict lookup. Preserves the previous
                # DoesNotExist=None-name behavior and keeps the original
                # `wid` string in the emitted 'workspace_id' unchanged.
                keep_rows = []
                lookup_uuids = []
                for row in rows:
                    wid = row['workspace_id']
                    wid_uuid = None
                    if scoped_ids is not None:
                        try:
                            wid_uuid = _uuid.UUID(str(wid))
                        except (ValueError, TypeError):
                            continue
                        if wid_uuid not in scoped_ids:
                            continue
                    else:
                        try:
                            wid_uuid = _uuid.UUID(str(wid))
                        except (ValueError, TypeError):
                            wid_uuid = None
                    keep_rows.append((row, wid_uuid))
                    if wid_uuid is not None:
                        lookup_uuids.append(wid_uuid)

                name_by_uuid = dict(
                    ProjectWorkspace.objects
                    .filter(id__in=lookup_uuids)
                    .values_list('id', 'name')
                ) if lookup_uuids else {}

                for row, wid_uuid in keep_rows:
                    wid = row['workspace_id']
                    name = name_by_uuid.get(wid_uuid) if wid_uuid else None
                    spend = controller.compute_workspace_spend(
                        now, workspace_id=wid,
                    )
                    enriched.append({
                        'workspace_id': wid,
                        'workspace_name': name,
                        'cap': row['cap'],
                        'effective_cap': row['cap'],
                        'cap_source': 'explicit',
                        'daily_total': spend['daily_total'],
                        'is_frozen': controller.is_workspace_frozen(wid),
                        'is_downgraded': controller.is_workspace_downgraded(wid),
                    })
            return {
                'action': action,
                'count': len(enriched),
                'workspaces': enriched,
                'default_cap': default_cap,
                'include_defaults': include_defaults,
                'scope_note': scope_note,
                'enforcement_tier': 'downgrade_and_freeze',
                'window_note': (
                    'daily = last 24h sliding window (not calendar day)'
                ),
                'null_bucket_note': _null_bucket_note,
            }

        if action == 'set_cap':
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}
            auth_err = _authorize_mutation(workspace)
            if auth_err is not None:
                return {'action': action, **auth_err}
            if daily_cap_usd is None:
                return {
                    'action': action,
                    'error': 'daily_cap_usd is required for set_cap',
                }
            try:
                result = controller.set_workspace_daily_cap(
                    workspace.id, daily_cap_usd, actor_user_id=user_id,
                )
            except ValueError as e:
                return {'action': action, 'error': str(e)}
            spend = controller.compute_workspace_spend(now, workspace_id=workspace.id)
            # S2850 #3.0a — immediate enforcement so operators don't wait
            # for the next autopilot cycle. Both calls are idempotent and
            # thresholded, so they no-op when the new cap doesn't cross a
            # boundary. Auto-clear on cap-raise is also attributed here
            # per Rigby SIGN #4 Q2.
            freeze_action = controller.enforce_workspace_freeze(
                spend, now, workspace.id,
                actor_user_id=user_id,
                trigger='operator_set_cap_immediate',
            )
            downgrade_action = controller.enforce_workspace_downgrade(
                spend, now, workspace.id,
                actor_user_id=user_id,
                trigger='operator_set_cap_immediate',
            )
            is_frozen = controller.is_workspace_frozen(workspace.id)
            warning = None
            if is_frozen and result['cap'] > spend['daily_total']:
                warning = (
                    'workspace is currently frozen but cap now exceeds 24h '
                    'spend — call clear_freeze to resume non-critical calls'
                )
            return {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                **result,
                'daily_total': spend['daily_total'],
                'is_frozen': is_frozen,
                'enforcement_fired': {
                    'freeze': freeze_action,
                    'downgrade': downgrade_action,
                },
                'warning': warning,
            }

        if action == 'clear_cap':
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}
            auth_err = _authorize_mutation(workspace)
            if auth_err is not None:
                return {'action': action, **auth_err}
            cleared = controller.clear_workspace_daily_cap(
                workspace.id, actor_user_id=user_id,
            )
            return {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'cleared': cleared,
                'note': (
                    'freeze flag (if any) is NOT cleared — call '
                    'clear_freeze explicitly to unfreeze'
                    if cleared else 'no cap was configured for this workspace'
                ),
            }

        if action == 'clear_freeze':
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}
            auth_err = _authorize_mutation(workspace)
            if auth_err is not None:
                return {'action': action, **auth_err}
            cleared = controller.clear_workspace_freeze(
                workspace.id, actor_user_id=user_id,
            )
            # S2858 PR#1 — inline post-clear spend/threshold context so
            # operators don't have to re-call get_status to know whether
            # the freeze will immediately re-fire.
            status_context = _status_context(workspace, cleared_flag='freeze')
            return {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'cleared': cleared,
                'note': (
                    'freeze cleared — non-critical LLM calls resume for '
                    'this workspace (state flip only; check re_flag_likely '
                    'below to know if it will re-fire)'
                    if cleared else 'workspace was not frozen (no-op)'
                ),
                'status_context': status_context,
                'null_bucket_note': _null_bucket_note,
            }

        if action == 'clear_downgrade':
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}
            auth_err = _authorize_mutation(workspace)
            if auth_err is not None:
                return {'action': action, **auth_err}
            cleared = controller.clear_workspace_downgrade(
                workspace.id, actor_user_id=user_id,
            )
            status_context = _status_context(workspace, cleared_flag='downgrade')
            return {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'cleared': cleared,
                'note': (
                    'downgrade cleared — LLM calls resume on the requested '
                    'model (state flip only; check re_flag_likely below '
                    'to know if it will re-fire)'
                    if cleared else 'workspace was not downgraded (no-op)'
                ),
                'status_context': status_context,
                'null_bucket_note': _null_bucket_note,
            }

        # S2849 W2 #2a — global default cap + backfill actions. These are
        # staff-only (no workspace to own).
        def _authorize_staff():
            """None on ok / error dict on deny — staff-only gate."""
            if user_id is None:
                return {'error': 'authentication required for this action'}
            try:
                User = get_user_model()
                actor = User.objects.get(id=user_id)
            except Exception:
                return {'error': f'actor user_id={user_id} not found'}
            if not getattr(actor, 'is_staff', False):
                return {
                    'error': (
                        f'user_id={user_id} is not staff — this action '
                        f'requires staff privileges'
                    ),
                }
            return None

        if action == 'get_default_cap':
            default_cap = controller.get_workspace_default_cap()
            return {
                'action': action,
                'default_cap': default_cap,
                'note': (
                    'workspace_default_daily_cap is unset — new workspaces '
                    'have no effective cap until an operator sets a default '
                    'via set_default_cap and backfill_defaults'
                    if default_cap is None
                    else (
                        'default is a LAZY fallback for get_status/list_caps '
                        'display. Autopilot enforcement iterates only '
                        'workspaces with EXPLICIT caps — call '
                        'backfill_defaults to bring workspaces under '
                        'enforcement'
                    )
                ),
            }

        if action == 'set_default_cap':
            auth_err = _authorize_staff()
            if auth_err is not None:
                return {'action': action, **auth_err}
            if daily_cap_usd is None:
                return {
                    'action': action,
                    'error': 'daily_cap_usd is required for set_default_cap',
                }
            try:
                result = controller.set_workspace_default_cap(
                    daily_cap_usd, actor_user_id=user_id,
                )
            except ValueError as e:
                return {'action': action, 'error': str(e)}
            return {
                'action': action,
                **result,
                'note': (
                    'default cap updated. Existing workspaces WITHOUT '
                    'explicit caps now show this value in get_status/'
                    'list_caps (cap_source=default) but autopilot '
                    'enforcement still requires explicit caps — call '
                    'backfill_defaults to apply.'
                ),
            }

        if action == 'backfill_defaults':
            auth_err = _authorize_staff()
            if auth_err is not None:
                return {'action': action, **auth_err}
            dry_run = payload.get('dry_run')
            if dry_run is None:
                dry_run = True
            dry_run = bool(dry_run)
            force = bool(payload.get('force', False))
            include_ids = payload.get('include_workspace_ids')
            exclude_ids = payload.get('exclude_workspace_ids')
            # OpenAI function-calling often passes daily_cap_usd=0 when the
            # optional param isn't intentionally set; coerce to None so the
            # controller reads the stored global default. Callers who want
            # an explicit per-run cap must pass a positive value.
            override_cap = daily_cap_usd if daily_cap_usd else None
            try:
                result = controller.backfill_workspace_defaults(
                    default_cap=override_cap,
                    include_workspace_ids=include_ids,
                    exclude_workspace_ids=exclude_ids,
                    force=force,
                    dry_run=dry_run,
                    actor_user_id=user_id,
                )
            except ValueError as e:
                return {'action': action, 'error': str(e)}
            return {
                'action': action,
                **result,
                'note': (
                    'DRY RUN — no writes performed. Pass dry_run=false to '
                    'apply.' if dry_run else
                    f'wrote {result["wrote"]} caps '
                    f'(planned={result["planned"]}, '
                    f'skipped_existing={result["skipped_existing"]}, '
                    f'errors={result["errors"]})'
                ),
            }

        if action == 'enforcement_report':
            # S2851 W2 #3.1 — fleet auditability over time. Complements
            # set_cap's inline enforcement_fired (S2850 #3.0a) which is the
            # point-of-action trust surface. This report answers "over the
            # last window, whose caps fired, when, and how often?" Query
            # strategy per Rigby SIGN Q1: single-filter narrow using the
            # existing (action_type, -created_at) index, then aggregate in
            # Python — avoids JSONB group-by execution plans on
            # (evidence->>'workspace_id') which has no functional index.
            from datetime import timedelta
            from core.models_diagnostic_pipeline import AutopilotAction
            from core.models_llm_routing import LLMCallLog
            from core.services.ops_autopilot import AutopilotConfig
            from django.db.models import Sum, Count

            window = payload.get('window', '24h')
            window_hours = {'24h': 24, '7d': 168, '30d': 720}.get(window)
            if window_hours is None:
                return {
                    'action': action,
                    'error': (
                        f'invalid window {window!r} — must be one of '
                        f'"24h", "7d", "30d"'
                    ),
                }
            cutoff = now - timedelta(hours=window_hours)
            include_spend = bool(payload.get('include_spend', False))
            include_null_bucket = bool(
                payload.get('include_null_bucket', True)
            )
            include_downgrade_savings = bool(
                payload.get('include_downgrade_savings', False)
            )
            # S2857: simulate_enforcement rows carry evidence.simulated=True.
            # Excluded by default so operator/autopilot counts stay clean;
            # opt in via include_simulated=true to see demo/verification
            # traffic in the fleet report.
            include_simulated = bool(payload.get('include_simulated', False))

            # Auth scope (Rigby SIGN Q3: option c). Non-staff sees only own
            # workspaces; staff sees all. Unauthenticated callers get the
            # null_bucket + note only (no per-workspace rows) so the tool
            # still surfaces something rather than 403-ing.
            is_staff = False
            if user_id is not None:
                try:
                    User = get_user_model()
                    actor = User.objects.get(id=user_id)
                    is_staff = bool(getattr(actor, 'is_staff', False))
                except Exception:
                    is_staff = False

            if user_id is None:
                workspace_scope_qs = ProjectWorkspace.objects.none()
                scope_note = (
                    'unauthenticated caller — per-workspace rows omitted; '
                    'null_bucket only'
                )
            elif is_staff:
                workspace_scope_qs = ProjectWorkspace.objects.all()
                scope_note = 'staff scope — all workspaces'
            else:
                workspace_scope_qs = ProjectWorkspace.objects.filter(
                    user_id=user_id,
                )
                scope_note = f'auto-scoped to workspaces owned by user_id={user_id}'

            # Optional single-workspace narrowing (must be in scope).
            if workspace_id:
                workspace_scope_qs = workspace_scope_qs.filter(
                    id=workspace_id,
                )

            scoped_workspaces = list(
                workspace_scope_qs.only('id', 'name', 'user_id')
            )
            scoped_ids = {str(ws.id) for ws in scoped_workspaces}

            # Q1 (a′): single narrow query, aggregate in Python. Fetches
            # only the two fields we need per row (created_at + evidence).
            enforcement_action_types = [
                'workspace_budget_freeze',
                'workspace_freeze_cleared',
                'workspace_downgrade_set',
                'workspace_downgrade_cleared',
            ]
            enforcement_qs = (
                AutopilotAction.objects
                .filter(
                    action_type__in=enforcement_action_types,
                    created_at__gte=cutoff,
                )
                .values('created_at', 'evidence')
            )
            # S2856 slate #3: split each workspace's enforcement events into
            # auto (autopilot cycle) vs operator (workspace_budget_tool)
            # counts. Decision rule per Rigby SIGN Q1: presence of
            # evidence.actor_user_id → operator, absence → auto. This works
            # uniformly across all 4 filtered action types including
            # manual-clear rows that don't stamp `trigger` (freeze_cleared,
            # manual downgrade_cleared). enforcement_events_count is
            # preserved as the sum for back-compat with any existing
            # consumer of the report shape.
            per_ws_events: Dict[str, Dict[str, Any]] = {}
            for row in enforcement_qs.iterator():
                ev = row.get('evidence') or {}
                wid = ev.get('workspace_id')
                if not wid:
                    continue
                wid = str(wid)
                if wid not in scoped_ids:
                    continue
                # S2857: exclude simulated events unless opted in.
                if not include_simulated and ev.get('simulated'):
                    continue
                bucket = per_ws_events.setdefault(
                    wid,
                    {'count': 0, 'auto_count': 0, 'operator_count': 0,
                     'last': None},
                )
                bucket['count'] += 1
                if ev.get('actor_user_id'):
                    bucket['operator_count'] += 1
                else:
                    bucket['auto_count'] += 1
                if bucket['last'] is None or row['created_at'] > bucket['last']:
                    bucket['last'] = row['created_at']

            # Optional per-workspace spend aggregation using the
            # (workspace, -created_at) index on LLMCallLog.
            per_ws_spend: Dict[str, Dict[str, Any]] = {}
            if include_spend and scoped_ids:
                spend_qs = (
                    LLMCallLog.objects
                    .filter(
                        workspace_id__in=list(scoped_ids),
                        created_at__gte=cutoff,
                    )
                    .values('workspace_id')
                    .annotate(
                        spend=Sum('cost'),
                        calls=Count('id'),
                    )
                )
                for row in spend_qs:
                    wid = str(row['workspace_id'])
                    per_ws_spend[wid] = {
                        'spend_usd': float(row['spend'] or 0),
                        'calls': row['calls'] or 0,
                    }

            # S2853 W2 #3.2 + S2856 unblock: per-workspace forced-downgrade
            # usage + savings estimate. Filter is now was_downgraded=True
            # (S2856 field on LLMCallLog) — enforcer-forced downgrades
            # only, not calls that natively target the downgrade model
            # (PersonalAssistantAgent, orchestration coordinators — see
            # DEFAULT_AGENT_LLM_CONFIGS at ~753+). "downgrade_model_*"
            # names retained for backward-compatible response shape;
            # semantics are now "forced" per S2856. Historical rows
            # written before S2856 migration default to was_downgraded=False
            # and are excluded, so windows overlapping the migration
            # boundary under-report by that amount.
            from core.services.ops_autopilot.pricing import (
                MODEL_PRICES,
                estimate_uncached_cost,
            )
            from decimal import Decimal
            per_ws_downgrade: Dict[str, Dict[str, Any]] = {}
            downgrade_model_id = AutopilotConfig.BUDGET_DOWNGRADE_MODEL
            gpt52_priced = 'gpt-5.2' in MODEL_PRICES
            downgrade_priced = downgrade_model_id in MODEL_PRICES
            if include_downgrade_savings and scoped_ids:
                dg_qs = (
                    LLMCallLog.objects
                    .filter(
                        workspace_id__in=list(scoped_ids),
                        was_downgraded=True,
                        created_at__gte=cutoff,
                    )
                    .values('workspace_id')
                    .annotate(
                        calls=Count('id'),
                        sum_prompt=Sum('prompt_tokens'),
                        sum_completion=Sum('completion_tokens'),
                        actual=Sum('cost'),
                    )
                )
                for row in dg_qs:
                    wid = str(row['workspace_id'])
                    prompt = int(row['sum_prompt'] or 0)
                    completion = int(row['sum_completion'] or 0)
                    actual = Decimal(row['actual'] or 0)
                    # Would-have cost at pre-downgrade model (gpt-5.2)
                    # uncached rates. estimate_uncached_cost returns None
                    # if gpt-5.2 pricing is missing from MODEL_PRICES.
                    would_have = (
                        estimate_uncached_cost('gpt-5.2', prompt, completion)
                        if gpt52_priced else None
                    )
                    savings = (
                        (would_have - actual)
                        if would_have is not None else None
                    )
                    per_ws_downgrade[wid] = {
                        'calls': row['calls'] or 0,
                        'actual': actual,
                        'would_have': would_have,
                        'savings': savings,
                    }

            rows = []
            # NOTE: shared/immutable-by-convention default — do not mutate
            # `events` in the loop below (only reads). Per Rigby post-code
            # SIGN Q3 (S2856 slate #3).
            empty_bucket = {
                'count': 0, 'auto_count': 0, 'operator_count': 0, 'last': None,
            }
            for ws in scoped_workspaces:
                wid = str(ws.id)
                effective = controller.get_effective_workspace_daily_cap(ws.id)
                events = per_ws_events.get(wid, empty_bucket)
                row_out: Dict[str, Any] = {
                    'workspace_id': wid,
                    'workspace_name': ws.name,
                    'cap_usd': controller.get_workspace_daily_cap(ws.id),
                    'effective_cap_usd': effective['cap'],
                    'cap_source': effective['source'],
                    'is_frozen': controller.is_workspace_frozen(ws.id),
                    'is_downgraded': controller.is_workspace_downgraded(ws.id),
                    'enforcement_events_count': events['count'],
                    'auto_events_count': events['auto_count'],
                    'operator_events_count': events['operator_count'],
                    'last_enforcement_at': (
                        events['last'].isoformat() if events['last'] else None
                    ),
                }
                if include_spend:
                    spend = per_ws_spend.get(
                        wid, {'spend_usd': 0.0, 'calls': 0},
                    )
                    row_out['attributed_spend_usd'] = spend['spend_usd']
                    row_out['calls'] = spend['calls']
                else:
                    row_out['attributed_spend_usd'] = None
                    row_out['calls'] = None
                if include_downgrade_savings:
                    dg = per_ws_downgrade.get(wid)
                    if dg is None:
                        row_out['downgrade_model_calls_count'] = 0
                        row_out['downgrade_model_actual_cost_usd'] = 0.0
                        row_out['downgrade_model_would_have_cost_usd'] = (
                            0.0 if gpt52_priced else None
                        )
                        row_out['downgrade_model_estimated_savings_usd'] = (
                            0.0 if gpt52_priced else None
                        )
                    else:
                        row_out['downgrade_model_calls_count'] = dg['calls']
                        row_out['downgrade_model_actual_cost_usd'] = float(
                            dg['actual']
                        )
                        row_out['downgrade_model_would_have_cost_usd'] = (
                            float(dg['would_have'])
                            if dg['would_have'] is not None else None
                        )
                        row_out['downgrade_model_estimated_savings_usd'] = (
                            float(dg['savings'])
                            if dg['savings'] is not None else None
                        )
                rows.append(row_out)

            # Deterministic order — highest enforcement activity first,
            # then by workspace name for stable diff.
            rows.sort(
                key=lambda r: (
                    -r['enforcement_events_count'],
                    (r['workspace_name'] or ''),
                ),
            )

            response: Dict[str, Any] = {
                'action': action,
                'window': window,
                'window_hours': window_hours,
                'cutoff': cutoff.isoformat(),
                'scope_note': scope_note,
                'note': (
                    'Enforcement events counted from AutopilotAction rows '
                    'where workspace_id lives inside evidence JSON — '
                    'best-effort attribution. Point-of-action trust '
                    'surface is set_cap\'s inline enforcement_fired '
                    'payload; this report is fleet auditability over '
                    'time. S2856: auto_events_count vs operator_events_count '
                    'split uses evidence.actor_user_id presence — present → '
                    'operator (workspace_budget_tool), absent → auto '
                    '(autopilot cycle). enforcement_events_count is the sum. '
                    'S2857: rows with evidence.simulated=True (from '
                    'simulate_enforcement) are ' + (
                        'INCLUDED (include_simulated=true)'
                        if include_simulated
                        else 'excluded by default; pass include_simulated=true to see them'
                    ) + '.'
                ),
                'row_count': len(rows),
                'rows': rows,
            }
            if include_spend:
                response['spend_note'] = (
                    'attributed_spend_usd is the workspace-attributed '
                    'subset only (currently the PA path); NULL-bucket is '
                    'governed by GLOBAL budget controls, not per-workspace'
                )
            if include_downgrade_savings:
                # Top-level summary (per Rigby Q4 sign-off): sum
                # per-workspace fields once here so operators / clients
                # don't have to re-aggregate. Preserves Decimal math up
                # to the final float() serialization.
                total_calls = 0
                total_actual = Decimal('0')
                total_would_have = Decimal('0')
                any_priced = False
                for dg in per_ws_downgrade.values():
                    total_calls += dg['calls']
                    total_actual += dg['actual']
                    if dg['would_have'] is not None:
                        total_would_have += dg['would_have']
                        any_priced = True
                response['downgrade_model_totals'] = {
                    'model_id': downgrade_model_id,
                    'calls': total_calls,
                    'actual_cost_usd': float(total_actual),
                    'would_have_cost_usd': (
                        float(total_would_have) if any_priced else None
                    ),
                    'estimated_savings_usd': (
                        float(total_would_have - total_actual)
                        if any_priced else None
                    ),
                }
                response['downgrade_savings_note'] = (
                    'Counts only enforcer-forced downgrades '
                    f'(LLMCallLog.was_downgraded=True → routed to '
                    f'{downgrade_model_id} because a global or per-workspace '
                    'downgrade flag was live). Natively-'
                    f'{downgrade_model_id} agents (PersonalAssistantAgent, '
                    'orchestration coordinators) are excluded. '
                    'would_have_cost is UNCACHED math at gpt-5.2 pre-'
                    'downgrade rates ($1.75/1M input, $14/1M output — '
                    'llm_enforcer.py:606-627); actual_cost comes from '
                    'LLMCallLog.cost. Diagnostic estimate; as-of query '
                    'time, not a reconciled billing ledger. Rows created '
                    'before the S2856 deploy do not have was_downgraded '
                    'populated (default=False); savings will under-report '
                    'until enough post-deploy traffic accrues to fill '
                    'the window.'
                    if downgrade_priced and gpt52_priced else
                    'Pricing table missing entry for '
                    f'{downgrade_model_id!r} or gpt-5.2 in '
                    'core/services/ops_autopilot/pricing.py — savings '
                    'fields will be None until wired.'
                )
            if include_null_bucket:
                null_qs = LLMCallLog.objects.filter(
                    workspace__isnull=True,
                    created_at__gte=cutoff,
                ).aggregate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                )
                response['null_bucket'] = {
                    'spend_usd': float(null_qs['spend'] or 0),
                    'calls': null_qs['calls'] or 0,
                }
            return response

        if action == 'simulate_enforcement':
            # S2857 A1 W2 #4 — exercise the enforcer hot-path against a
            # SYNTHETIC daily-spend value without needing to make real
            # LLM calls from a non-PA agent. Motivating pain: Rigby's
            # calling agent is always 'PersonalAssistant', which
            # bypasses freeze at core/llm_enforcer.py:271 (_critical_
            # agents), so operators/customer demos had to drop to
            # Django shell to see enforcement fire. This action fires
            # BOTH freeze and downgrade branches so the combined tier
            # outcome is visible in one round-trip (Rigby SIGN Q1a).
            #
            # Attribution (Rigby SIGN Q3): rows written when dry_run=
            # false carry evidence.actor_user_id=user_id AND
            # evidence.simulated=True + evidence.trigger='simulate_
            # enforcement'. enforcement_report excludes simulated=True
            # by default (include_simulated=false); operator_events_
            # count is therefore protected from demo/verification
            # pollution.
            workspace, err = _resolve_workspace(workspace_id)
            if err is not None:
                return {'action': action, **err}

            raw_spend = payload.get('simulated_daily_spend_usd')
            if raw_spend is None:
                return {
                    'action': action,
                    'error': (
                        'simulated_daily_spend_usd is required '
                        '(float ≥ 0, USD)'
                    ),
                }
            try:
                simulated_spend = float(raw_spend)
            except (TypeError, ValueError):
                return {
                    'action': action,
                    'error': (
                        f'simulated_daily_spend_usd must be numeric; '
                        f'got {raw_spend!r}'
                    ),
                }
            if simulated_spend < 0:
                return {
                    'action': action,
                    'error': (
                        f'simulated_daily_spend_usd must be ≥ 0; '
                        f'got {simulated_spend}'
                    ),
                }
            # Rigby SIGN Q3 — nan/inf pass the `< 0` check silently
            # (NaN comparisons always False) and pollute SystemConfig
            # descriptions + evidence dicts on dry_run=false.
            import math
            if not math.isfinite(simulated_spend):
                return {
                    'action': action,
                    'error': (
                        f'simulated_daily_spend_usd must be finite; '
                        f'got {simulated_spend}'
                    ),
                }

            dry_run = bool(payload.get('dry_run', True))

            # Auth: dry-run reads AND mutations both require ownership /
            # staff. Rigby SIGN Q2 — dry-run reveals caps + enforcement
            # thresholds so is still a sensitive read; matches S2852
            # latent-overexposure fix.
            auth_err = _authorize_mutation(workspace)
            if auth_err is not None:
                return {'action': action, **auth_err}

            cap = controller.get_workspace_daily_cap(workspace.id)
            if cap is None:
                return {
                    'action': action,
                    'workspace_id': str(workspace.id),
                    'workspace_name': workspace.name,
                    'error': (
                        f'workspace {workspace.id} has no explicit '
                        f'per-workspace cap set; simulate_enforcement '
                        f'requires an explicit cap because the '
                        f'enforcer only runs against workspaces with '
                        f'a cap row. Call set_cap first '
                        f'(or set the global default via '
                        f'set_default_cap + backfill_defaults).'
                    ),
                }

            from core.services.ops_autopilot.config import AutopilotConfig
            soft_pct = AutopilotConfig.BUDGET_SOFT_LIMIT_PCT
            clear_pct = controller._WORKSPACE_DOWNGRADE_CLEAR_PCT
            downgrade_set_threshold = cap * soft_pct
            downgrade_clear_threshold = cap * clear_pct

            currently_frozen = controller.is_workspace_frozen(workspace.id)
            currently_downgraded = controller.is_workspace_downgraded(
                workspace.id,
            )

            # Decision math mirrors enforce_workspace_freeze +
            # enforce_workspace_downgrade branch structure so dry-run
            # tells the operator EXACTLY what a mutation would do.
            if simulated_spend >= cap and not currently_frozen:
                freeze_decision = 'would_freeze'
            elif simulated_spend >= cap and currently_frozen:
                freeze_decision = 'no_op_already_frozen'
            else:
                freeze_decision = 'no_op_below_cap'

            if (
                currently_downgraded
                and simulated_spend < downgrade_clear_threshold
            ):
                downgrade_decision = 'would_clear_downgrade'
            elif (
                simulated_spend >= downgrade_set_threshold
                and not currently_downgraded
            ):
                downgrade_decision = 'would_set_downgrade'
            elif (
                simulated_spend >= downgrade_set_threshold
                and currently_downgraded
            ):
                downgrade_decision = 'no_op_already_downgraded'
            else:
                downgrade_decision = 'no_op_below_soft_limit'

            thresholds = {
                'cap_usd': cap,
                'downgrade_set_threshold_usd': round(
                    downgrade_set_threshold, 4,
                ),
                'downgrade_clear_threshold_usd': round(
                    downgrade_clear_threshold, 4,
                ),
                'soft_limit_pct': soft_pct,
                'clear_pct': clear_pct,
                'currently_frozen': currently_frozen,
                'currently_downgraded': currently_downgraded,
            }

            base_response: Dict[str, Any] = {
                'action': action,
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'simulated_daily_spend_usd': simulated_spend,
                'dry_run': dry_run,
                'thresholds': thresholds,
                'freeze_decision': freeze_decision,
                'downgrade_decision': downgrade_decision,
            }

            if dry_run:
                base_response['note'] = (
                    'dry_run=true — no state written and no '
                    'AutopilotAction rows created. Pass dry_run=false '
                    'to fire the enforcer (WARNING: real workspace '
                    'freeze/downgrade flags WILL be written and '
                    'llm_enforcer will block or downgrade real calls '
                    'for this workspace until clear_freeze / '
                    'clear_downgrade is called).'
                )
                base_response['freeze_action'] = None
                base_response['downgrade_action'] = None
                return base_response

            # dry_run=False — invoke the real enforcer methods with
            # the synthetic spend dict. enforcer only reads daily_total
            # (verified at ops_autopilot/budget.py:651,819,861), so
            # zero-fill the rest.
            synthetic_spend = {
                'daily_total': simulated_spend,
                'daily_calls': 0,
                'hourly_total': 0.0,
                'hourly_calls': 0,
            }
            freeze_action = controller.enforce_workspace_freeze(
                synthetic_spend, now, workspace.id,
                actor_user_id=user_id, trigger='simulate_enforcement',
                simulated=True,
            )
            downgrade_action = controller.enforce_workspace_downgrade(
                synthetic_spend, now, workspace.id,
                actor_user_id=user_id, trigger='simulate_enforcement',
                simulated=True,
            )

            base_response['freeze_action'] = freeze_action
            base_response['downgrade_action'] = downgrade_action
            base_response['note'] = (
                'dry_run=false — enforcer methods invoked with the '
                'synthetic spend value. Any freeze/downgrade flags '
                'written are LIVE and will affect real LLM calls '
                'attributed to this workspace until cleared via '
                'clear_freeze / clear_downgrade. AutopilotAction rows '
                'carry evidence.simulated=True and are excluded from '
                'enforcement_report by default (opt in via '
                'include_simulated=true).'
            )
            return base_response

        return {
            'action': action,
            'error': (
                f'Unknown workspace_budget_tool action: {action!r}. '
                f'Valid: set_cap, get_status, clear_freeze, clear_downgrade, '
                f'list_caps, clear_cap, get_default_cap, set_default_cap, '
                f'backfill_defaults, enforcement_report, simulate_enforcement.'
            ),
        }

    def _handle_ops_digest(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Autonomous ops digest — aggregates live system data into a
        structured summary that can be posted into a conversation.
        """
        from django.utils import timezone
        from datetime import timedelta
        from core.models_diagnostic_pipeline import AutopilotAction
        from core.models_unified_system import AgentControlEntry

        action = payload.get('action', 'generate')
        window = payload.get('window', '1h')
        now = timezone.now()

        window_map = {'10m': 10, '1h': 60, '6h': 360, '24h': 1440}
        window_minutes = window_map.get(window, 60)
        cutoff = now - timedelta(minutes=window_minutes)

        # ── Gather data ──────────────────────────────────────────────
        # Deploy SHA
        import os
        sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', '')
        if not sha:
            try:
                import subprocess
                sha = subprocess.check_output(
                    ['git', 'rev-parse', 'HEAD'],
                    stderr=subprocess.DEVNULL,
                ).decode().strip()[:12]
            except Exception:
                sha = 'unknown'
        sha = sha[:12]

        # Autopilot status
        autopilot_last = 'never'
        total_cycles = 0
        # Session 1083 (Rigby audit): ops digest builds were bare-passing
        # every query, so the digest JSON would silently return zeros or
        # empty lists on DB incident — classic false-green for the "how's
        # production" question. Collect degraded fields into a list so the
        # PA can surface "partial data" in its reply to Chris.
        degraded_fields: list[str] = []

        blocks_24h = 0
        try:
            last_cycle = AutopilotAction.objects.filter(
                policy='cycle_evaluation',
            ).first()
            autopilot_last = last_cycle.created_at.isoformat() if last_cycle else 'never'
            total_cycles = AutopilotAction.objects.filter(policy='cycle_evaluation').count()
            blocks_24h = AutopilotAction.objects.filter(
                action_type='block_agent', dry_run=False,
                created_at__gte=now - timedelta(hours=24),
            ).count()
        except Exception as e:
            degraded_fields.append('autopilot_last_cycle')
            logger.warning(
                "ops digest: autopilot cycle stats failed (%s: %s)",
                type(e).__name__, e,
            )

        # Blocked agents
        blocked_names = []
        try:
            blocked_names = sorted(AgentControlEntry.get_blocked_names())
        except Exception as e:
            degraded_fields.append('blocked_agents')
            logger.warning(
                "ops digest: AgentControlEntry.get_blocked_names failed "
                "(%s: %s) — digest will show empty blocked list",
                type(e).__name__, e,
            )

        # Recent activity (agent executions + celery tasks in window)
        agent_runs = 0
        task_events = 0
        task_failures = 0
        try:
            from core.models_unified_system import AgentExecution
            from core.models_celery_telemetry import CeleryTaskEvent
            agent_runs = AgentExecution.objects.filter(created_at__gte=cutoff).count()
            task_events = CeleryTaskEvent.objects.filter(started_at__gte=cutoff).count()
            task_failures = CeleryTaskEvent.objects.filter(
                started_at__gte=cutoff, status='FAILURE',
            ).count()
        except Exception as e:
            degraded_fields.append('activity')
            logger.warning(
                "ops digest: activity counts failed (%s: %s) — agent_runs, "
                "celery_tasks, task_failures will all report 0",
                type(e).__name__, e,
            )

        # Failure signatures (top 3 in window)
        top_failures = []
        try:
            from core.models_diagnostic_pipeline import FailureSignature
            from django.db.models import Count
            sigs = list(
                FailureSignature.objects.filter(
                    detections__detected_at__gte=cutoff,
                ).annotate(
                    hit_count=Count('detections'),
                ).order_by('-hit_count')[:3].values(
                    'category', 'pattern_hash', 'hit_count',
                )
            )
            top_failures = sigs
        except Exception as e:
            degraded_fields.append('top_failures')
            logger.warning(
                "ops digest: top failure signatures query failed "
                "(%s: %s)", type(e).__name__, e,
            )

        # ── Build digest ─────────────────────────────────────────────
        digest = {
            'timestamp': now.isoformat(),
            'window': window,
            'deploy_sha': sha,
            'autopilot': {
                'status': 'running',
                'last_cycle': autopilot_last,
                'total_cycles': total_cycles,
                'blocks_24h': blocks_24h,
            },
            'blocked_agents': blocked_names,
            'activity': {
                'agent_runs': agent_runs,
                'celery_tasks': task_events,
                'task_failures': task_failures,
            },
            'top_failures': top_failures,
            'degraded_fields': degraded_fields,
        }

        # Render markdown
        fa_lines = []
        for f in top_failures:
            fa_lines.append(f"  - {f['category']}/{f['pattern_hash'][:8]}: {f['hit_count']} hits")

        md = (
            f"## Ops Digest — {now.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"**SHA:** `{sha}` | **Window:** {window}\n\n"
            f"**Autopilot:** running (last cycle: {autopilot_last[:19]}Z) | "
            f"cycles: {total_cycles} | blocks 24h: {blocks_24h}\n\n"
            f"**Blocked agents:** {', '.join(blocked_names) if blocked_names else 'none'}\n\n"
            f"**Activity ({window}):** {agent_runs} agent runs, "
            f"{task_events} tasks, {task_failures} failures\n\n"
        )
        if fa_lines:
            md += "**Top failures:**\n" + '\n'.join(fa_lines) + "\n"
        else:
            md += "**Top failures:** none\n"

        digest['markdown'] = md

        if action == 'generate':
            return {'action': 'generate', 'digest': digest}

        elif action == 'post':
            conversation_id = payload.get('conversation_id')
            if not conversation_id:
                return {'error': 'conversation_id required for post action'}

            from core.models import ChatConversation
            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = None
            if user_id:
                user = User.objects.filter(id=user_id).first()
            if not user:
                user = User.objects.filter(is_superuser=True).first()

            ChatConversation.objects.create(
                user=user,
                conversation_id=conversation_id,
                user_message='[Autonomous Ops Digest]',
                assistant_response=md,
                platform='api',
                source='ops_digest',
                metadata={'digest': digest, 'trace_id': trace_id},
            )

            return {
                'action': 'post',
                'conversation_id': conversation_id,
                'posted_at': now.isoformat(),
                'digest': digest,
            }

        return {'error': f'Unknown action: {action}'}

    def _ops_timeout_config_read(self, agent_names: list, trace_id: str) -> Dict[str, Any]:
        """
        Session 1098: Read agent wall-clock timeout config.
        Returns code defaults from _AGENT_TIMEOUT_SECONDS + any DB overrides
        from SystemConfiguration(key='agent_timeout_override:{name}').
        Strictly read-only.
        """
        from core.models.system import SystemConfiguration

        # Code defaults from tasks.py
        # Session 1222 P2 — trimmed 3 zero-execution names
        # (TalkingCharacterAgent, ResolveAgent, WhaleWatcherAgent). Agent
        # class files remain in core/agents/ for future re-enable; the
        # timeout config entries here are pure dashboard surface noise.
        code_defaults = {
            'AudioAgent': 300, 'ImageAgent': 300, 'VideoAgent': 600,
            'ThreeDAgent': 300, 'ImageEditingAgent': 300, 'VideoEditingAgent': 600,
            'ResearchAgent': 1500, 'SystemIntelligenceAgent': 600,
            'MarketingStrategyAgent': 600, 'CustomerResearchAgent': 1500,
            'CharacterTrainingAgent': 600, 'ContentWriterAgent': 600,
            'CompetitorAnalysisAgent': 600, 'BrandStrategyAgent': 600,
            'ContentStrategyAgent': 600,
            'StockAuditCoordinator': 900, 'WorkflowOrchestrationAgent': 900,
        }
        global_default = 1200  # 20 min fallback

        # Filter to requested agents (or show all if none specified)
        if agent_names:
            names = agent_names
        else:
            names = sorted(code_defaults.keys())

        # DB overrides
        override_keys = [f'agent_timeout_override:{n}' for n in names]
        db_overrides = dict(
            SystemConfiguration.objects.filter(
                key__in=override_keys,
            ).values_list('key', 'value')
        )

        agents = []
        for name in names:
            override_key = f'agent_timeout_override:{name}'
            db_val = db_overrides.get(override_key)
            code_val = code_defaults.get(name, global_default)
            effective = int(db_val) if db_val is not None else code_val
            agents.append({
                'agent_name': name,
                'code_default_seconds': code_val,
                'db_override_seconds': int(db_val) if db_val is not None else None,
                'effective_seconds': effective,
                'source': 'db_override' if db_val is not None else 'code_default',
            })

        return {
            'action': 'timeout_config_read',
            'agents': agents,
            'global_default_seconds': global_default,
            'watchdog_threshold_minutes': 35,
        }

    def _ops_proof_bundle(self, agent_names: list, initiative_id: str, trace_id: str) -> Dict[str, Any]:
        """
        Session 1098: Verification proof bundle — returns timeout config +
        agent control audit + initiative audit in one read-only call.
        Designed for "verification mode" where the user asks to confirm
        what changed and what's configured.
        """
        # Part A: Timeout config
        timeout_config = self._ops_timeout_config_read(agent_names, trace_id)

        # Part B: Agent control audit log (block/unblock history)
        audit_entries = []
        try:
            from core.models_unified_system import AgentControlEntry
            qs = AgentControlEntry.objects.all().order_by('-updated_at')
            if agent_names:
                qs = qs.filter(agent_name__in=agent_names)
            entries = list(qs[:30].values(
                'agent_name', 'status', 'reason', 'blocked_at',
                'blocked_by', 'ttl_hours', 'updated_at',
            ))
            for e in entries:
                for k in ('blocked_at', 'updated_at'):
                    if e.get(k):
                        e[k] = e[k].isoformat()
            audit_entries = entries
        except Exception as exc:
            audit_entries = [{'error': str(exc)}]

        # Part C: Initiative audit (if initiative_id provided)
        initiative_info = None
        if initiative_id:
            try:
                from core.models import Initiative
                from core.models_document_registry import InitiativeStage
                ini = Initiative.objects.filter(id=initiative_id).values(
                    'id', 'name', 'status', 'current_stage', 'created_at', 'updated_at',
                ).first()
                if ini:
                    for k in ('created_at', 'updated_at'):
                        if ini.get(k):
                            ini[k] = ini[k].isoformat()
                    ini['id'] = str(ini['id'])
                    stages = list(InitiativeStage.objects.filter(
                        initiative_id=initiative_id,
                    ).values(
                        'stage', 'status', 'created_at',
                    ).order_by('stage'))
                    for s in stages:
                        if s.get('created_at'):
                            s['created_at'] = s['created_at'].isoformat()
                    ini['stages'] = stages
                    initiative_info = ini
                else:
                    initiative_info = {'error': f'Initiative {initiative_id} not found'}
            except Exception as exc:
                initiative_info = {'error': str(exc)}

        return {
            'action': 'proof_bundle',
            'timeout_config': timeout_config['agents'],
            'global_default_seconds': timeout_config['global_default_seconds'],
            'watchdog_threshold_minutes': timeout_config['watchdog_threshold_minutes'],
            'agent_control_audit': audit_entries,
            'initiative': initiative_info,
            'note': 'Read-only verification bundle. No mutations performed.',
        }

    def _ops_tool_migration_report(self, window: str, trace_id: str) -> Dict[str, Any]:
        """
        Session 1079 Phase 2: Gateway migration telemetry report.

        Queries ToolCallRecord to show:
        - Legacy vs gateway tool call counts
        - Top legacy tools still being used
        - Deprecation readiness per legacy tool
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Max

        window_hours = {'6h': 6, '24h': 24, '7d': 168, '30d': 720}.get(window, 168)
        cutoff = timezone.now() - timedelta(hours=window_hours)

        try:
            from core.models_tool_calls import ToolCallRecord

            removed_names = set(self.REMOVED_TOOL_ALIASES.keys())
            gateway_names = self.GATEWAY_TOOLS

            # Total tool calls in window
            all_calls = ToolCallRecord.objects.filter(created_at__gte=cutoff)
            total = all_calls.count()

            # Count by tool name
            tool_counts = dict(
                all_calls.values('tool_name')
                .annotate(count=Count('id'), last_used=Max('created_at'))
                .order_by('-count')
                .values_list('tool_name', 'count')
            )

            # Classify
            removed_calls = []
            gateway_calls = []
            other_calls = []

            for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
                entry = {'tool': tool_name, 'count': count}
                if tool_name in removed_names:
                    gw, suggested_action = self.REMOVED_TOOL_ALIASES[tool_name]
                    entry['suggested_gateway'] = gw
                    entry['suggested_action'] = suggested_action
                    removed_calls.append(entry)
                elif tool_name in gateway_names:
                    gateway_calls.append(entry)
                else:
                    other_calls.append(entry)

            removed_total = sum(e['count'] for e in removed_calls)
            gateway_total = sum(e['count'] for e in gateway_calls)

            # Split removed-tool calls into PA-originated vs agent-internal
            pa_removed = dict(
                all_calls.filter(tool_name__in=removed_names, agent_name='PersonalAssistant')
                .values('tool_name')
                .annotate(count=Count('id'))
                .values_list('tool_name', 'count')
            )
            pa_removed_total = sum(pa_removed.values())
            agent_removed_total = removed_total - pa_removed_total

            # Tools with 0 calls — fully silent
            silent_tools = [
                tool_name for tool_name in removed_names
                if tool_counts.get(tool_name, 0) == 0
            ]

            # Failure comparison: removed vs gateway success rates
            removed_failures = all_calls.filter(
                tool_name__in=removed_names, success=False
            ).count()
            gateway_failures = all_calls.filter(
                tool_name__in=gateway_names, success=False
            ).count()

            return {
                'action': 'tool_migration_report',
                'window': window,
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_tool_calls': total,
                    'removed_tool_calls': removed_total,
                    'pa_removed_calls': pa_removed_total,
                    'agent_removed_calls': agent_removed_total,
                    'gateway_calls': gateway_total,
                    'other_calls': total - removed_total - gateway_total,
                    'migration_pct': round(gateway_total / max(gateway_total + pa_removed_total, 1) * 100, 1),
                },
                'removed_tools_referenced': removed_calls[:15],
                'pa_removed_breakdown': [
                    {'tool': t, 'count': c, 'suggested_gateway': self.REMOVED_TOOL_ALIASES[t][0]}
                    for t, c in sorted(pa_removed.items(), key=lambda x: -x[1])
                ] if pa_removed else [],
                'gateway_tools': gateway_calls,
                'silent_removed_tools': sorted(silent_tools),
                'failure_comparison': {
                    'removed_failures': removed_failures,
                    'removed_failure_rate': round(removed_failures / max(removed_total, 1) * 100, 2),
                    'gateway_failures': gateway_failures,
                    'gateway_failure_rate': round(gateway_failures / max(gateway_total, 1) * 100, 2),
                },
                'recommendation': (
                    f'{len(silent_tools)} removed tools had zero calls in {window}. '
                    f'{len(removed_calls)} removed tools still referenced '
                    f'({pa_removed_total} PA-originated, {agent_removed_total} agent-internal).'
                    if removed_calls else
                    f'All {len(removed_names)} removed tools silent in {window}. '
                    f'Gateway adoption at {round(gateway_total / max(gateway_total + pa_removed_total, 1) * 100, 1)}%.'
                ),
            }
        except Exception as e:
            return {'action': 'tool_migration_report', 'error': str(e)}


    # ── Codebase introspection ─────────────────────────────────────────────

    def _handle_status_snapshot(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 973: Cheap system status snapshot for broad overview questions.
        9 count() queries, cached 60s.
        """
        from django.core.cache import cache

        cache_key = 'pa:status_snapshot'
        cached = cache.get(cache_key)
        if cached:
            logger.debug(f"[{trace_id}] Status snapshot served from cache")
            return cached

        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        snapshot = {}

        # 1. Initiatives
        try:
            from core.models import Initiative
            active = Initiative.objects.filter(status='ACTIVE').count()
            updated_24h = Initiative.objects.filter(updated_at__gte=last_24h).count()
            snapshot['initiatives'] = {'active': active, 'updated_24h': updated_24h}
        except Exception as e:
            snapshot['initiatives'] = {'error': str(e)}

        # 2. Tool calls (24h)
        try:
            from core.models import ToolCallRecord
            total = ToolCallRecord.objects.filter(created_at__gte=last_24h).count()
            failed = ToolCallRecord.objects.filter(created_at__gte=last_24h, success=False).count()
            snapshot['tool_calls_24h'] = {'total': total, 'failed': failed}
        except Exception as e:
            snapshot['tool_calls_24h'] = {'error': str(e)}

        # 3. Health (latest heartbeat)
        try:
            from core.models_heart import HeartBeat
            hb = HeartBeat.objects.order_by('-recorded_at').first()
            if hb:
                age_min = (now - hb.recorded_at).total_seconds() / 60
                snapshot['health'] = {
                    'status': getattr(hb, 'overall_status', 'unknown'),
                    'score': getattr(hb, 'health_score', None),
                    'age_minutes': round(age_min, 1),
                }
            else:
                snapshot['health'] = {'status': 'no_data'}
        except Exception as e:
            snapshot['health'] = {'error': str(e)}

        # 4. Spiders (24h)
        try:
            from core.models_unified_system import LegacySpiderData
            items = LegacySpiderData.objects.filter(created_at__gte=last_24h).count()
            distinct_spiders = LegacySpiderData.objects.filter(created_at__gte=last_24h).values('spider_name').distinct().count()
            snapshot['spiders_24h'] = {'items': items, 'active_spiders': distinct_spiders}
        except Exception as e:
            snapshot['spiders_24h'] = {'error': str(e)}

        # 5. Conversations (24h)
        try:
            from core.models import HiveMindSession
            convos = HiveMindSession.objects.filter(created_at__gte=last_24h).count()
            snapshot['conversations_24h'] = {'count': convos}
        except Exception as e:
            snapshot['conversations_24h'] = {'error': str(e)}

        # 6. Signal clusters (active)
        try:
            from core.models import SignalCluster
            active_clusters = SignalCluster.objects.filter(status='active').count()
            snapshot['signal_clusters'] = {'active': active_clusters}
        except Exception as e:
            snapshot['signal_clusters'] = {'error': str(e)}

        # 7. Celery tasks (24h) — Session 983: query CeleryTaskEvent instead
        # of django_celery_results.TaskResult (which stays empty when
        # CELERY_RESULT_BACKEND is Redis, not django-db).
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            total = CeleryTaskEvent.objects.filter(started_at__gte=last_24h).count()
            failed = CeleryTaskEvent.objects.filter(started_at__gte=last_24h, status='FAILURE').count()
            snapshot['celery_24h'] = {'total': total, 'failed': failed}
        except Exception as e:
            snapshot['celery_24h'] = {'error': str(e)}

        # 8. Errors (24h)
        try:
            from core.models_diagnostic_pipeline import FailureDetection
            errors = FailureDetection.objects.filter(detected_at__gte=last_24h).count()
            snapshot['errors_24h'] = {'count': errors}
        except Exception as e:
            snapshot['errors_24h'] = {'error': str(e)}

        # 9. Blogs (24h)
        try:
            from core.models import SelfBlog
            total_blogs = SelfBlog.objects.filter(created_at__gte=last_24h).count()
            published = SelfBlog.objects.filter(created_at__gte=last_24h, publish_ready=True).count()
            snapshot['blogs_24h'] = {'total': total_blogs, 'published': published}
        except Exception as e:
            snapshot['blogs_24h'] = {'error': str(e)}

        # 10. Session 983: Actuator score — did the system actually DO things?
        # Sensors (spiders, signals) ingest data; actuators turn it into outputs.
        try:
            from core.models import Initiative, SelfBlog as _SB, HumanAttentionItem
            actuators = {}

            # Initiatives promoted to active in last 24h
            actuators['initiatives_activated'] = Initiative.objects.filter(
                status='active', updated_at__gte=last_24h
            ).count()

            # Publish-ready blog content (available for promotion)
            actuators['blogs_publish_ready'] = _SB.objects.filter(publish_ready=True).count()

            # Human decisions made (items triaged in boardroom)
            actuators['decisions_made'] = HumanAttentionItem.objects.filter(
                decided_at__gte=last_24h
            ).count()

            # Deliverables produced
            try:
                from core.models import Deliverable
                actuators['deliverables_created'] = Deliverable.objects.filter(
                    created_at__gte=last_24h
                ).count()
            except Exception:
                actuators['deliverables_created'] = 0

            snapshot['actuators_24h'] = actuators
        except Exception as e:
            snapshot['actuators_24h'] = {'error': str(e)}

        snapshot['generated_at'] = now.isoformat()

        # Session 1078: Lightweight ops pointer (SLO breach count + version SHA)
        try:
            import os
            sha = os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'dev')
            snapshot['ops'] = {
                'version_sha_short': sha[:8] if len(sha) > 8 else sha,
            }
            # Quick breach check: just celery + agent task success
            celery_total = snapshot.get('celery_24h', {}).get('total', 0)
            celery_failed = snapshot.get('celery_24h', {}).get('failed', 0)
            if celery_total > 0 and (celery_total - celery_failed) / celery_total < 0.999:
                snapshot['ops']['slo_breaches'] = 1
            else:
                snapshot['ops']['slo_breaches'] = 0
        except Exception as e:
            # Session 1083: was bare pass — SLO breach count silently
            # reported as missing instead of degraded. Now flag the
            # snapshot as partial so the UI can show a warning indicator.
            logger.warning(
                "status_snapshot: SLO breach calc failed (%s: %s) — "
                "ops.slo_breaches will be unset",
                type(e).__name__, e,
            )
            snapshot.setdefault('ops', {})['slo_calc_degraded'] = True

        cache.set(cache_key, snapshot, 60)
        logger.info(f"[{trace_id}] Status snapshot generated and cached")
        return snapshot

    def _handle_agent_introspection(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1007: Agent introspection — describe what an agent can do.

        Searches the Agent DB model and agent classes for capabilities,
        description, tools, and recent execution stats.
        """
        from core.models_unified_system import Agent, AgentExecution
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'inspect')
        # Session G3: Normalize aliases
        ACTION_ALIASES = {'detail': 'details', 'inspect': 'details'}
        action = ACTION_ALIASES.get(action, action)
        agent_query = payload.get('agent_name', '').strip().lower()

        # Session 1035-W2: List all PA tool schemas
        if action == 'tools':
            from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
            tools_list = []
            for schema in PA_TOOL_SCHEMAS:
                if not isinstance(schema, dict):
                    continue
                name = schema.get('name', '')
                desc = schema.get('description', '')[:120]
                params = schema.get('parameters', {}).get('properties', {})
                actions_enum = params.get('action', {}).get('enum', [])
                tools_list.append({
                    'name': name,
                    'description': desc,
                    'actions': actions_enum,
                    'param_count': len(params),
                })
            return {
                'action': 'tools',
                'total_tool_schemas': len(tools_list),
                'tools': tools_list,
            }

        # Session 1036+: Support list/stats actions without requiring agent_name
        if action in ('list', 'stats') or (not agent_query and action not in ('details', 'capabilities')):
            all_agents = Agent.objects.filter(is_active=True)
            total = all_agents.count()

            by_agent_type = {}
            for a in all_agents.values('agent_type').distinct():
                atype = a['agent_type'] or 'unknown'
                by_agent_type[atype] = all_agents.filter(agent_type=atype).count()

            # Get agents with recent activity (last 7 days).
            # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
            # "active_last_7d" counts distinct router-agent job dispatch
            # targets; PA agentic loop activity would inflate the count.
            # Use agent__name form per ADR-0002 F1 fold equivalent
            # (Postgres JSONField NULL-semantics make the
            # input_data__source='pa' form unsafe for pre-flag-flip rows).
            now = timezone.now()
            active_ids = set(
                AgentExecution.objects.filter(
                    created_at__gte=now - timedelta(days=7),
                ).exclude(agent__name='PersonalAssistant')
                .values_list('agent_id', flat=True)
            )

            # Router breakdown: routable, blocked, non-specialist
            # Router breakdown: disjoint categories that reconcile cleanly
            # router_routable_total = blocked + rerouted + fully_enabled
            router_routable_total = 0
            blocked_agents: list = []
            rerouted_agents: list = []
            try:
                from core.agent_router import AgentRouter
                from core.models_unified_system import AgentControlEntry
                router_routable_total = len(AgentRouter.AGENT_MAP)
                # Session 1080: DB-backed blocked list
                _BLOCKED = AgentControlEntry.get_blocked_names()
                # Non-specialist: tasks get rerouted to specialist agents
                _NON_SPECIALIST = frozenset({
                    # Session 1115: removed `ContentDistributionAgent` — phantom
                    # entry, no class exists, AGENT_MAP doesn't reference it.
                    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
                    'FullStackDeveloperAgent', 'CodeReviewAgent',
                    'COOAgent', 'CTOAgent', 'AudioAgent',
                })
                # Make disjoint: rerouted = non_specialist minus blocked
                blocked_agents = sorted(_BLOCKED)
                _REROUTE_REASON = {
                    'WorkflowAgent': 'Generic orchestrator — tasks rerouted to specialist agents',
                    'VideoAgent': 'Media agent — tasks rerouted to content specialists',
                    'DevOpsAgent': 'Infra agent — tasks rerouted to relevant domain agent',
                    'FullStackDeveloperAgent': 'Dev agent — tasks rerouted to specialist',
                    'CodeReviewAgent': 'Code agent — tasks rerouted to specialist',
                    'COOAgent': 'Executive agent — tasks rerouted to operational agents',
                    'CTOAgent': 'Executive agent — tasks rerouted to technical agents',
                    'AudioAgent': 'Media agent — tasks rerouted to content specialists',
                }
                rerouted_agents = sorted([
                    {'name': name, 'reason': _REROUTE_REASON.get(name, 'Non-specialist — rerouted to best-fit agent')}
                    for name in (_NON_SPECIALIST - _BLOCKED)
                ], key=lambda x: x['name'])
            except Exception as e:
                # Session 1083: was bare pass — if AGENT_MAP / _BLOCKED /
                # _NON_SPECIALIST import failed, the agent introspection
                # response would silently report zero blocked + zero
                # rerouted agents, making it look like all agents were
                # enabled during a config incident.
                logger.warning(
                    "agent_introspection: blocked/rerouted agent list "
                    "build failed (%s: %s) — response will show zero "
                    "counts", type(e).__name__, e,
                )

            blocked_count = len(blocked_agents)
            rerouted_count = len(rerouted_agents)
            fully_enabled = router_routable_total - blocked_count - rerouted_count

            result: Dict[str, Any] = {
                'requested_action': action,
                'effective_action': action,
                'total_agents_db': total,
                'active_last_7d': len(active_ids),
                'router_routable_total': router_routable_total,
                'blocked_count': blocked_count,
                'blocked_agents': blocked_agents,
                'rerouted_count': rerouted_count,
                'rerouted_agents': rerouted_agents,
                'fully_enabled_count': fully_enabled,
                'reconciliation': f'{blocked_count} blocked + {rerouted_count} rerouted + {fully_enabled} fully_enabled = {router_routable_total} total',
                'by_agent_type': by_agent_type,
            }

            # 'list' includes the agent preview; 'stats' is aggregates only.
            # Session 2728 F-AI-2 — honor the caller's `limit` up to the hard
            # cap so the schema-declared default (20) is applied instead of
            # the prior hard-coded `[:50]` slice. When the caller-requested
            # limit exceeds the cap, surface `limit_capped/requested_limit/
            # effective_limit/hard_max` (mirrors F-D-5 / F-KB-1 / F-S-3
            # pattern approved at earlier Batch A tools).
            if action == 'list':
                _AGENT_LIST_HARD_MAX = 50
                _requested_limit = payload.get('limit', 20)
                try:
                    _requested_limit_int = int(_requested_limit)
                except (TypeError, ValueError):
                    _requested_limit_int = 20
                _effective_limit = min(max(_requested_limit_int, 1), _AGENT_LIST_HARD_MAX)
                _limit_capped = _requested_limit_int > _AGENT_LIST_HARD_MAX
                agent_list = list(
                    all_agents.values('name', 'agent_type', 'specialization', 'effectiveness_score')
                    .order_by('-effectiveness_score', 'name')[:_effective_limit]
                )
                result['agents'] = agent_list
                result['limit'] = _effective_limit
                if _limit_capped:
                    result['limit_capped'] = True
                    result['requested_limit'] = _requested_limit_int
                    result['effective_limit'] = _effective_limit
                    result['hard_max'] = _AGENT_LIST_HARD_MAX

            return result

        # Gap 3 fix: Canonicalize agent name (snake_case → PascalCase, common aliases)
        # Convert snake_case like "thinking_agent" → "ThinkingAgent"
        canonical_query = agent_query
        if '_' in agent_query:
            canonical_query = ''.join(w.capitalize() for w in agent_query.split('_'))

        # Search by name (fuzzy) — try canonical first, then original, then partial
        agents = Agent.objects.filter(name__iexact=canonical_query, is_active=True)
        if not agents.exists():
            agents = Agent.objects.filter(name__icontains=canonical_query, is_active=True)
        if not agents.exists():
            agents = Agent.objects.filter(name__icontains=agent_query, is_active=True)
        if not agents.exists():
            # Try without "agent" suffix
            clean_query = agent_query.replace('agent', '').replace('_', '').strip()
            if clean_query:
                agents = Agent.objects.filter(name__icontains=clean_query, is_active=True)

        if not agents.exists():
            # List available agents as suggestions
            all_agents = list(
                Agent.objects.filter(is_active=True)
                .values_list('name', flat=True)
                .order_by('name')[:20]
            )
            return {
                'found': False,
                'query': agent_query,
                'message': f'No agent found matching "{agent_query}".',
                'suggestions': all_agents,
            }

        agent = agents.first()
        now = timezone.now()

        # Get recent execution stats
        recent_executions = AgentExecution.objects.filter(
            agent=agent,
            created_at__gte=now - timedelta(days=7),
        )
        total_recent = recent_executions.count()
        successful_recent = recent_executions.filter(status='completed').count()

        # Try to get the agent class for system_prompt and tools
        agent_class_info = {}
        try:
            from core.agent_router import get_agent_router
            router = get_agent_router()
            agent_class = router.get_agent_class(agent.name)
            if agent_class:
                agent_class_info['system_prompt'] = getattr(agent_class, 'system_prompt', '')[:500]
                tools = getattr(agent_class, 'tools', [])
                if tools:
                    agent_class_info['tools'] = [
                        t.get('function', {}).get('name', 'unknown')
                        for t in tools if isinstance(t, dict)
                    ]
        except Exception as e:
            # Session 1083: was bare pass — router lookup failure would
            # silently hide system_prompt + tools from introspection
            # output, making it look like agents had no prompt or tools.
            logger.debug(
                "agent_introspection: agent class lookup for %s failed "
                "(%s: %s)", agent.name, type(e).__name__, e,
            )

        return {
            'found': True,
            'agent': {
                'name': agent.name,
                'type': agent.agent_type,
                'description': agent.description,
                'specialization': agent.specialization,
                'capabilities': agent.capabilities,
                'effectiveness_score': agent.effectiveness_score,
                'total_executions': agent.total_executions,
            },
            'recent_7d': {
                'total': total_recent,
                'successful': successful_recent,
                'success_rate': f"{(successful_recent / total_recent * 100):.0f}%" if total_recent > 0 else 'N/A',
            },
            'class_info': agent_class_info,
        }

    def _handle_scheduled_tasks(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1007: Scheduled tasks visibility — list Celery Beat periodic tasks.

        Shows what tasks are scheduled, their intervals, and last run times.
        """
        from django_celery_beat.models import PeriodicTask
        from django.db.models import Q

        action = payload.get('action', 'list')

        # ── Enable/disable a beat entry ──
        if action in ('enable', 'disable'):
            task_id = payload.get('task_id', '') or payload.get('name', '')
            if not task_id:
                return {'error': 'task_id or name required for enable/disable'}
            try:
                task_obj = PeriodicTask.objects.get(name=task_id)
            except PeriodicTask.DoesNotExist:
                try:
                    task_obj = PeriodicTask.objects.get(id=int(task_id))
                except (PeriodicTask.DoesNotExist, ValueError):
                    return {'error': f'Scheduled task not found: {task_id}'}
            new_state = action == 'enable'
            if task_obj.enabled == new_state:
                return {'action': action, 'name': task_obj.name, 'already': True, 'enabled': new_state}
            task_obj.enabled = new_state
            task_obj.save()
            return {'action': action, 'name': task_obj.name, 'enabled': new_state, 'success': True}

        # ── List (default) ──
        filter_keyword = payload.get('filter', '') or payload.get('search', '')
        limit = min(payload.get('limit', 50), 100)
        offset = payload.get('offset', 0)
        show_disabled = payload.get('show_disabled', False)

        tasks = PeriodicTask.objects.all() if show_disabled else PeriodicTask.objects.filter(enabled=True)
        tasks = tasks.order_by('name')
        total_enabled = PeriodicTask.objects.filter(enabled=True).count()

        if filter_keyword:
            tasks = tasks.filter(
                Q(name__icontains=filter_keyword) | Q(task__icontains=filter_keyword)
            )

        filtered_count = tasks.count()
        page = tasks[offset:offset + limit]

        results = []
        for task in page:
            schedule_info = ''
            if task.crontab:
                c = task.crontab
                schedule_info = f"cron({c.minute} {c.hour} {c.day_of_week} {c.day_of_month} {c.month_of_year})"
            elif task.interval:
                i = task.interval
                schedule_info = f"every {i.every} {i.period}"

            results.append({
                'name': task.name,
                'task': task.task,
                'schedule': schedule_info,
                'queue': task.queue or 'default',
                'enabled': task.enabled,
                'last_run': task.last_run_at.isoformat() if task.last_run_at else None,
                'total_runs': task.total_run_count,
            })

        return {
            'total_enabled': total_enabled,
            'filtered': filtered_count,
            'showing': len(results),
            'offset': offset,
            'filter': filter_keyword or 'all',
            'tasks': results,
        }


    def _handle_legislation(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1014: Legislation tool — congressional bill tracking via LegacySpiderData.

        Actions:
        - search: Find bills by keyword
        - status: Status of a specific bill
        - summary: Plain-English explanation of a bill
        - trending: Most recently active bills
        - overview: Dashboard stats
        """
        from core.models_unified_system import LegacySpiderData
        from django.db.models import Q
        import json

        action = payload.get('action', 'search')
        # Session 1062: Alias old schema actions to real handler actions
        _ACTION_ALIASES = {'list': 'trending', 'stats': 'overview', 'details': 'status'}
        action = _ACTION_ALIASES.get(action, action)
        query = payload.get('query', '')
        bill_number = payload.get('bill_number', '') or payload.get('id', '')
        limit = min(payload.get('limit', 10), 20)

        def _bills_from_row(item):
            """Session 1075: Extract bill dicts from a LegacySpiderData row.

            Spider stores data as {'items': [...], 'source': ..., 'dedup_stats': ...}.
            Each element in 'items' is a bill dict with bill_number, topics, state, etc.
            Falls back to treating raw_data itself as a single bill for legacy rows.
            """
            raw = item.raw_data if isinstance(item.raw_data, dict) else {}
            # Primary format: envelope with items array
            if isinstance(raw.get('items'), list):
                return [b for b in raw['items'] if isinstance(b, dict)]
            # Legacy: raw_data is the bill itself
            if raw.get('bill_number'):
                return [raw]
            # Legacy: nested raw_data wrapper
            inner = raw.get('raw_data')
            if isinstance(inner, dict) and inner.get('bill_number'):
                return [inner]
            return []

        qs = LegacySpiderData.objects.filter(spider_name='legislation').order_by('-created_at')
        total_tracked = qs.count()

        if action == 'overview':
            # Dashboard: total bills, top topics, recent activity
            recent = qs[:50]
            topic_counts: Dict[str, int] = {}
            states: set = set()
            status_counts: Dict[str, int] = {}
            bill_count = 0
            for item in recent:
                for bill in _bills_from_row(item):
                    bill_count += 1
                    for t in bill.get('topics', []):
                        topic_counts[t] = topic_counts.get(t, 0) + 1
                    state = bill.get('state', '')
                    if state:
                        states.add(state)
                    st = bill.get('status', '')
                    if st:
                        status_counts[st] = status_counts.get(st, 0) + 1

            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            return {
                'action': 'overview',
                'total_tracked': total_tracked,
                'total_bills': bill_count,
                'recent_rows_scanned': len(recent),
                'top_topics': [{'topic': t, 'count': c} for t, c in top_topics],
                'states_covered': sorted(states),
                'status_breakdown': status_counts,
            }

        elif action == 'trending':
            items = []
            for item in qs[:limit * 2]:  # scan extra rows since each has multiple bills
                for bill in _bills_from_row(item):
                    items.append({
                        'bill_number': bill.get('bill_number', ''),
                        'title': bill.get('title', ''),
                        'state': bill.get('state', ''),
                        'status': bill.get('status', ''),
                        'last_action': bill.get('last_action', ''),
                        'last_action_date': bill.get('last_action_date', ''),
                        'sponsor_count': bill.get('sponsor_count', 0),
                        'url': bill.get('url', ''),
                    })
                    if len(items) >= limit:
                        break
                if len(items) >= limit:
                    break
            return {'action': 'trending', 'items': items, 'total': total_tracked}

        elif action == 'status' and bill_number:
            # Search embedding_text first (most reliable), then scan items arrays
            matches = qs.filter(Q(embedding_text__icontains=bill_number))[:10]
            raw = None
            for m in matches:
                for bill in _bills_from_row(m):
                    if bill_number.lower() in (bill.get('bill_number', '') or '').lower():
                        raw = bill
                        break
                if raw:
                    break
            if not raw:
                return {'action': 'status', 'found': False, 'bill_number': bill_number}
            sponsors = raw.get('sponsors', [])
            return {
                'action': 'status',
                'found': True,
                'bill_number': raw.get('bill_number', bill_number),
                'title': raw.get('title', ''),
                'state': raw.get('state', ''),
                'status': raw.get('status', ''),
                'status_date': raw.get('status_date', ''),
                'last_action': raw.get('last_action', ''),
                'last_action_date': raw.get('last_action_date', ''),
                'sponsors': [s.get('name', '') for s in sponsors[:5]],
                'sponsor_count': raw.get('sponsor_count', 0),
                'committee': raw.get('committee', ''),
                'url': raw.get('url', ''),
            }

        elif action == 'summary':
            target = bill_number or query
            if not target:
                return {'action': 'summary', 'error': 'Provide a bill_number or query'}
            matches = qs.filter(Q(embedding_text__icontains=target))[:10]
            raw = None
            for m in matches:
                for bill in _bills_from_row(m):
                    bn = (bill.get('bill_number', '') or '').lower()
                    ti = (bill.get('title', '') or '').lower()
                    if target.lower() in bn or target.lower() in ti:
                        raw = bill
                        break
                if raw:
                    break
            if not raw:
                return {'action': 'summary', 'found': False, 'query': target}
            return {
                'action': 'summary',
                'found': True,
                'bill_number': raw.get('bill_number', ''),
                'title': raw.get('title', ''),
                'state': raw.get('state', ''),
                'status': raw.get('status', ''),
                'description': raw.get('description', ''),
                'plain_summary': raw.get('plain_summary', ''),
                'sponsors': [s.get('name', '') for s in raw.get('sponsors', [])[:5]],
                'committee': raw.get('committee', ''),
                'topics': raw.get('topics', []),
                'url': raw.get('url', ''),
                'congress_gov_url': raw.get('congress_gov_url', ''),
            }

        elif action == 'ask':
            # Session 1015: RAG-powered "Ask A Bill" — semantic search + LLM answer
            question = query or payload.get('question', '')
            if not question:
                return {'action': 'ask', 'error': 'Provide a question about legislation'}

            source_bills = []
            context_parts = []

            # Try embedding-based semantic search first
            try:
                from core.rag_integration import create_embedding
                import numpy as np

                q_embedding = create_embedding(question)
                if q_embedding:
                    embedded_bills = qs.filter(embedding__isnull=False)[:200]
                    scored = []
                    q_vec = np.array(q_embedding, dtype=np.float32)
                    q_norm = np.linalg.norm(q_vec)
                    if q_norm > 0:
                        q_vec = q_vec / q_norm

                    for item in embedded_bills:
                        try:
                            b_vec = np.array(item.embedding, dtype=np.float32)
                            b_norm = np.linalg.norm(b_vec)
                            if b_norm > 0:
                                b_vec = b_vec / b_norm
                            sim = float(np.dot(q_vec, b_vec))
                            if sim >= 0.25:
                                scored.append((sim, item))
                        except Exception:
                            continue

                    scored.sort(key=lambda x: x[0], reverse=True)
                    for sim, item in scored[:5]:
                        for raw in _bills_from_row(item):
                            bn = raw.get('bill_number', '')
                            title = raw.get('title', '')
                            desc = raw.get('description', '')
                            plain = raw.get('plain_summary', '')
                            sponsors = raw.get('sponsors', [])
                            topics = raw.get('topics', [])
                            sponsor_names = [s.get('name', '') for s in sponsors[:3]] if sponsors else []

                            bill_ctx = f"Bill: {bn} — {title}\n"
                            if desc:
                                bill_ctx += f"Description: {desc}\n"
                            if plain:
                                bill_ctx += f"Summary: {plain}\n"
                            if sponsor_names:
                                bill_ctx += f"Sponsors: {', '.join(sponsor_names)}\n"
                            if topics:
                                bill_ctx += f"Topics: {', '.join(topics[:5])}\n"
                            context_parts.append(bill_ctx)
                            source_bills.append({
                                'bill_number': bn,
                                'title': title,
                                'score': round(sim, 3),
                                'url': raw.get('url', ''),
                            })
            except Exception as e:
                logger.warning(f"Embedding search failed for ask action: {e}")

            # Fallback: keyword search if no embedding results
            if not source_bills:
                import re as _re
                # Extract meaningful keywords (strip stopwords)
                stopwords = {'what', 'which', 'how', 'does', 'will', 'are', 'is', 'the',
                             'a', 'an', 'in', 'on', 'about', 'any', 'do', 'can', 'to',
                             'of', 'for', 'and', 'or', 'this', 'that', 'my', 'me', 'us',
                             'being', 'been', 'bills', 'bill', 'legislation', 'congress',
                             'congressional', 'affect', 'impact', 'explain', 'tell'}
                words = _re.findall(r'[a-zA-Z]+', question.lower())
                keywords = [w for w in words if w not in stopwords and len(w) > 1]
                # Build Q filter from keywords
                q_filter = Q()
                for kw in keywords[:4]:
                    q_filter |= Q(embedding_text__icontains=kw) | Q(raw_data__title__icontains=kw)
                if not q_filter:
                    q_filter = Q(embedding_text__icontains=question[:20])
                kw_matches = qs.filter(q_filter)[:5]
                for item in kw_matches:
                    for raw in _bills_from_row(item):
                        bn = raw.get('bill_number', '')
                        title = raw.get('title', '')
                        desc = raw.get('description', '')
                        plain = raw.get('plain_summary', '')
                        bill_ctx = f"Bill: {bn} — {title}\n"
                        if desc:
                            bill_ctx += f"Description: {desc}\n"
                        if plain:
                            bill_ctx += f"Summary: {plain}\n"
                        context_parts.append(bill_ctx)
                        source_bills.append({
                            'bill_number': bn,
                            'title': title,
                            'score': 0,
                            'url': raw.get('url', ''),
                        })

            if not source_bills:
                # If we have legislation data but no matches, say so specifically
                if total_tracked > 0:
                    no_match_msg = (
                        f"I searched {total_tracked} tracked bills but couldn't find any "
                        f"matching your question. Try asking about specific topics like "
                        f"healthcare, immigration, education, environment, or technology."
                    )
                else:
                    no_match_msg = (
                        "No legislation data is available yet. The legislation spider "
                        "may not have run yet."
                    )
                return {
                    'action': 'ask',
                    'question': question,
                    'answer': no_match_msg,
                    'source_bills': [],
                    'sources_count': 0,
                }

            # Build RAG prompt and call LLM
            bill_context = "\n---\n".join(context_parts)
            system_prompt = (
                "You are a nonpartisan legislative analyst. Answer the user's question based ONLY "
                "on the bill text provided below. Quote specific bill numbers when referencing legislation. "
                "Explain in plain language that anyone can understand. Be factual and nonpartisan. "
                "If the provided bills do not address the question, say so honestly.\n\n"
                f"BILLS:\n{bill_context}"
            )

            try:
                from core.llm_enforcer import LLMEnforcer
                enforcer = LLMEnforcer()
                result = enforcer.enforce_real_ai(
                    prompt=question,
                    context=system_prompt,
                    agent_name="AskABill",
                    task_type="legislation_rag",
                    max_tokens=1500,
                )
                answer = result.get('content', '') if isinstance(result, dict) else str(result)
            except Exception as e:
                logger.error(f"LLM call failed for Ask A Bill: {e}")
                answer = f"I found {len(source_bills)} relevant bill(s) but could not generate an AI analysis right now. Please try again."

            return {
                'action': 'ask',
                'question': question,
                'answer': answer,
                'source_bills': source_bills,
                'sources_count': len(source_bills),
            }

        else:
            # Default: search by keyword
            if not query:
                return {'action': 'search', 'error': 'Provide a search query'}
            matches = qs.filter(
                Q(embedding_text__icontains=query) |
                Q(raw_data__title__icontains=query)
            )[:limit]
            items = []
            for item in matches:
                for raw in _bills_from_row(item):
                    items.append({
                        'bill_number': raw.get('bill_number', ''),
                        'title': raw.get('title', ''),
                        'state': raw.get('state', ''),
                        'status': raw.get('status', ''),
                        'sponsor_count': raw.get('sponsor_count', 0),
                        'last_action_date': raw.get('last_action_date', ''),
                        'url': raw.get('url', ''),
                    })
            return {
                'action': 'search',
                'query': query,
                'items': items,
                'total': len(items),
            }


    # =========================================================================
    # Session 1077: Gap Fixes — spider_status, agent_memory, heartbeat_history,
    # redis_health, db_perf, dependency_matrix, runtime_metrics
    # =========================================================================

    def _handle_spider_status(self, tool_name, payload, user_id, trace_id):
        """Gap 1: Per-spider run history, status, and item counts."""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Max, Min

        action = payload.get('action', 'list')
        limit = min(int(payload.get('limit', 30)), 100)

        try:
            from core.models_unified_system import LegacySpiderData

            if action == 'list':
                now = timezone.now()
                cutoff_24h = now - timedelta(hours=24)
                cutoff_7d = now - timedelta(days=7)

                spider_stats = (
                    LegacySpiderData.objects
                    .values('spider_name')
                    .annotate(
                        total_items=Count('id'),
                        last_run_at=Max('created_at'),
                        first_seen=Min('created_at'),
                        items_24h=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(created_at__gte=cutoff_24h)),
                        items_7d=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(created_at__gte=cutoff_7d)),
                    )
                    .order_by('-last_run_at')
                )

                items = []
                for s in spider_stats:
                    last_run = s['last_run_at']
                    age_hours = (now - last_run).total_seconds() / 3600 if last_run else None
                    items.append({
                        'spider_name': s['spider_name'],
                        'total_runs': s['total_items'],  # renamed: each LegacySpiderData row = one run
                        'runs_24h': s['items_24h'],
                        'runs_7d': s['items_7d'],
                        # Keep legacy keys for backward compat
                        'total_items': s['total_items'],
                        'items_24h': s['items_24h'],
                        'items_7d': s['items_7d'],
                        'last_run_at': last_run.isoformat() if last_run else None,
                        'first_seen': s['first_seen'].isoformat() if s['first_seen'] else None,
                        'age_hours': round(age_hours, 1) if age_hours is not None else None,
                        'status': 'active' if age_hours and age_hours < 48 else 'stale' if age_hours else 'unknown',
                        'count_note': 'total_runs = LegacySpiderData rows (each contains multiple items)',
                    })

                return {
                    'action': 'list',
                    'total_spiders': len(items),
                    'active': sum(1 for i in items if i['status'] == 'active'),
                    'stale': sum(1 for i in items if i['status'] == 'stale'),
                    'spiders': items,
                }

            elif action == 'history':
                spider_name = payload.get('spider_name', '')
                if not spider_name:
                    return {'error': 'spider_name required for history action'}

                runs = (
                    LegacySpiderData.objects
                    .filter(spider_name__iexact=spider_name)
                    .values('created_at', 'data_type', 'source_url')
                    .order_by('-created_at')[:limit]
                )
                items = [{
                    'created_at': r['created_at'].isoformat(),
                    'data_type': r['data_type'],
                    'source_url': r['source_url'][:100],
                } for r in runs]

                return {
                    'action': 'history',
                    'spider_name': spider_name,
                    'count': len(items),
                    'runs': items,
                }

            elif action == 'detail':
                item_id = payload.get('item_id', '') or payload.get('id', '')
                if not item_id:
                    return {'error': 'item_id required for detail action'}
                try:
                    item = LegacySpiderData.objects.get(id=item_id)
                except LegacySpiderData.DoesNotExist:
                    return {'error': f'LegacySpiderData {item_id} not found'}
                return {
                    'action': 'detail',
                    'id': str(item.id),
                    'spider_name': item.spider_name,
                    'data_type': item.data_type,
                    'source_url': item.source_url or '',
                    'created_at': item.created_at.isoformat(),
                    'embedding_text': (item.embedding_text or '')[:500],
                    'raw_data': item.raw_data if isinstance(item.raw_data, (dict, list)) else str(item.raw_data)[:2000],
                    'processed_data': item.processed_data if isinstance(item.processed_data, (dict, list)) else str(item.processed_data)[:2000],
                }

            elif action == 'search':
                query = payload.get('query', '').strip()
                data_type = payload.get('data_type', '').strip()
                spider_name = payload.get('spider_name', '').strip()
                if not query and not data_type and not spider_name:
                    return {'error': 'At least one of query, data_type, or spider_name required'}

                qs = LegacySpiderData.objects.all()
                if spider_name:
                    qs = qs.filter(spider_name__icontains=spider_name)
                if data_type:
                    qs = qs.filter(data_type__iexact=data_type)
                if query:
                    from django.db.models import Q as DQ
                    qs = qs.filter(DQ(embedding_text__icontains=query) | DQ(source_url__icontains=query))

                qs = qs.order_by('-created_at')[:limit]
                items = [{
                    'id': str(r.id),
                    'spider_name': r.spider_name,
                    'data_type': r.data_type,
                    'source_url': (r.source_url or '')[:120],
                    'created_at': r.created_at.isoformat(),
                    'preview': (r.embedding_text or '')[:200],
                } for r in qs]
                return {'action': 'search', 'count': len(items), 'items': items}

            return {'error': f'Unknown spider_status action: {action}. Valid: list, history, detail, search'}

        except Exception as e:
            logger.error(f"[SPIDER_STATUS] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    def _handle_agent_memory(self, tool_name, payload, user_id, trace_id):
        """Gap 2: Agent-scoped memory and knowledge inspection."""
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'list')
        agent_name = payload.get('agent_name', '').strip()
        limit = min(int(payload.get('limit', 20)), 50)
        query = payload.get('query', '').strip()

        try:
            from core.models_unified_system import Agent, AgentMemory, AgentKnowledgeSource

            # Global stats when no agent_name specified
            if action == 'stats' and not agent_name:
                from django.db.models import Count
                total_memories = AgentMemory.objects.count()
                total_kb = AgentKnowledgeSource.objects.count()
                top_agents = list(
                    AgentMemory.objects.values('agent__name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                )
                type_dist = dict(
                    AgentMemory.objects.values_list('memory_type')
                    .annotate(c=Count('id'))
                    .values_list('memory_type', 'c')
                )
                return {
                    'action': 'stats',
                    'scope': 'global',
                    'total_memories': total_memories,
                    'total_knowledge_sources': total_kb,
                    'memory_by_type': type_dist,
                    'top_agents': [{'agent': a['agent__name'], 'count': a['count']} for a in top_agents],
                }

            if not agent_name:
                return {'error': 'agent_name is required. Use stats action without agent_name for global stats.', 'action': action}

            # Resolve agent — support snake_case
            if '_' in agent_name:
                canonical = ''.join(w.capitalize() for w in agent_name.split('_'))
            else:
                canonical = agent_name

            agent = Agent.objects.filter(name__iexact=canonical, is_active=True).first()
            if not agent and canonical != agent_name:
                agent = Agent.objects.filter(name__icontains=agent_name, is_active=True).first()
            if not agent:
                clean = agent_name.replace('agent', '').replace('_', '').strip()
                if clean:
                    agent = Agent.objects.filter(name__icontains=clean, is_active=True).first()

            if not agent:
                return {'error': f'Agent not found: {agent_name}', 'action': action}

            if action == 'list':
                memories = AgentMemory.objects.filter(agent=agent).order_by('-created_at')
                if query:
                    memories = memories.filter(content__icontains=query)
                total = memories.count()
                items = [{
                    'id': str(m.id),
                    'title': m.title[:100] if m.title else '',
                    'memory_type': m.memory_type,
                    'valence': m.valence,
                    'importance_score': m.importance_score,
                    'safety_class': m.safety_class,
                    'source_type': m.source_type,
                    'tags': m.tags or [],
                    'access_count': m.access_count,
                    'created_at': m.created_at.isoformat() if m.created_at else None,
                } for m in memories[:limit]]

                return {
                    'action': 'list',
                    'agent_name': agent.name,
                    'total_memories': total,
                    'count': len(items),
                    'memories': items,
                }

            elif action == 'knowledge':
                kb = AgentKnowledgeSource.objects.filter(agent=agent).order_by('-last_updated_at')
                total = kb.count()
                items = [{
                    'id': str(k.id),
                    'title': k.title[:100],
                    'knowledge_type': k.knowledge_type,
                    'confidence_score': k.confidence_score,
                    'relevance_score': k.relevance_score,
                    'freshness_score': k.freshness_score,
                    'data_points_count': k.data_points_count,
                    'source_spiders': k.source_spider_names or [],
                    'last_updated_at': k.last_updated_at.isoformat() if k.last_updated_at else None,
                } for k in kb[:limit]]

                return {
                    'action': 'knowledge',
                    'agent_name': agent.name,
                    'total_knowledge': total,
                    'count': len(items),
                    'knowledge_sources': items,
                }

            elif action == 'stats':
                mem_count = AgentMemory.objects.filter(agent=agent).count()
                kb_count = AgentKnowledgeSource.objects.filter(agent=agent).count()
                from django.db.models import Avg, Count
                type_dist = dict(
                    AgentMemory.objects.filter(agent=agent)
                    .values_list('memory_type')
                    .annotate(c=Count('id'))
                    .values_list('memory_type', 'c')
                )
                avg_importance = AgentMemory.objects.filter(agent=agent).aggregate(
                    avg=Avg('importance_score')
                )['avg']

                return {
                    'action': 'stats',
                    'agent_name': agent.name,
                    'total_memories': mem_count,
                    'total_knowledge_sources': kb_count,
                    'memory_by_type': type_dist,
                    'avg_importance': round(float(avg_importance or 0), 3),
                }

            return {'error': f'Unknown agent_memory action: {action}. Valid: list, knowledge, stats'}

        except Exception as e:
            logger.error(f"[AGENT_MEMORY] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    def _handle_heartbeat_history(self, tool_name, payload, user_id, trace_id):
        """Gap 8: Heartbeat time-series and historical vitals."""
        action = payload.get('action', 'recent')
        limit = min(int(payload.get('limit', 24)), 100)

        try:
            from core.models_heart import HeartBeat

            if action == 'recent':
                heartbeats = HeartBeat.objects.order_by('-recorded_at')[:limit]
                items = [{
                    'id': str(hb.id),
                    'health_score': hb.health_score,
                    'overall_status': hb.overall_status,
                    'is_alive': hb.is_alive,
                    'components_checked': hb.components_checked,
                    'components_healthy': hb.components_healthy,
                    'components_degraded': hb.components_degraded,
                    'check_duration_ms': hb.check_duration_ms,
                    'recorded_at': hb.recorded_at.isoformat() if hb.recorded_at else None,
                } for hb in heartbeats]

                return {
                    'action': 'recent',
                    'count': len(items),
                    'heartbeats': items,
                }

            elif action == 'trends':
                from django.db.models import Avg, Min, Max, Count
                from django.utils import timezone
                from datetime import timedelta

                hours = int(payload.get('hours') or 24)  # Session 1228 PR-B autofill safety
                cutoff = timezone.now() - timedelta(hours=hours)
                qs = HeartBeat.objects.filter(recorded_at__gte=cutoff)

                agg = qs.aggregate(
                    avg_score=Avg('health_score'),
                    min_score=Min('health_score'),
                    max_score=Max('health_score'),
                    total_checks=Count('id'),
                    avg_duration=Avg('check_duration_ms'),
                )

                # Status distribution
                status_counts = dict(
                    qs.values_list('overall_status')
                    .annotate(c=Count('id'))
                    .values_list('overall_status', 'c')
                )

                return {
                    'action': 'trends',
                    'hours': hours,
                    'total_heartbeats': agg['total_checks'] or 0,
                    'avg_health_score': round(float(agg['avg_score'] or 0), 2),
                    'min_health_score': round(float(agg['min_score'] or 0), 2),
                    'max_health_score': round(float(agg['max_score'] or 0), 2),
                    'avg_check_duration_ms': round(float(agg['avg_duration'] or 0), 1),
                    'status_distribution': status_counts,
                }

            return {'error': f'Unknown heartbeat_history action: {action}. Valid: recent, trends'}

        except Exception as e:
            logger.error(f"[HEARTBEAT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    def _handle_infra_health(self, tool_name, payload, user_id, trace_id):
        """Gaps 11-14: Redis health, DB perf, dependency matrix, runtime metrics."""
        action = payload.get('action', 'dependency_matrix')

        try:
            if action == 'redis_health':
                import redis as redis_lib
                from django.conf import settings

                redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
                r = redis_lib.from_url(redis_url, socket_timeout=5)
                info = r.info(section='memory')
                clients_info = r.info(section='clients')
                stats_info = r.info(section='stats')
                ping_start = time.time()
                r.ping()
                ping_ms = round((time.time() - ping_start) * 1000, 2)

                return {
                    'action': 'redis_health',
                    'ping_ms': ping_ms,
                    'connected': True,
                    'used_memory_human': info.get('used_memory_human', ''),
                    'used_memory_peak_human': info.get('used_memory_peak_human', ''),
                    'maxmemory_human': info.get('maxmemory_human', '0'),
                    'maxmemory_policy': info.get('maxmemory_policy', ''),
                    'connected_clients': clients_info.get('connected_clients', 0),
                    'blocked_clients': clients_info.get('blocked_clients', 0),
                    'evicted_keys': stats_info.get('evicted_keys', 0),
                    'keyspace_hits': stats_info.get('keyspace_hits', 0),
                    'keyspace_misses': stats_info.get('keyspace_misses', 0),
                    'hit_rate_pct': round(
                        stats_info.get('keyspace_hits', 0) /
                        max(stats_info.get('keyspace_hits', 0) + stats_info.get('keyspace_misses', 0), 1) * 100, 2
                    ),
                    'total_commands_processed': stats_info.get('total_commands_processed', 0),
                    'uptime_seconds': info.get('uptime_in_seconds', 0),
                }

            elif action == 'db_perf':
                from django.db import connection

                with connection.cursor() as cursor:
                    # Connection pool info
                    cursor.execute("""
                        SELECT count(*) as total,
                               count(*) FILTER (WHERE state = 'active') as active,
                               count(*) FILTER (WHERE state = 'idle') as idle,
                               count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_tx,
                               max(EXTRACT(EPOCH FROM (now() - query_start)))::int as longest_query_secs
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                    """)
                    pool = dict(zip(
                        ['total_connections', 'active', 'idle', 'idle_in_transaction', 'longest_query_secs'],
                        cursor.fetchone()
                    ))

                    # Database stats
                    cursor.execute("""
                        SELECT xact_commit, xact_rollback, blks_read, blks_hit,
                               tup_returned, tup_fetched, tup_inserted, tup_updated, tup_deleted,
                               deadlocks, conflicts
                        FROM pg_stat_database
                        WHERE datname = current_database()
                    """)
                    cols = ['xact_commit', 'xact_rollback', 'blks_read', 'blks_hit',
                            'tup_returned', 'tup_fetched', 'tup_inserted', 'tup_updated', 'tup_deleted',
                            'deadlocks', 'conflicts']
                    row = cursor.fetchone()
                    db_stats = dict(zip(cols, row)) if row else {}

                    # Cache hit ratio
                    blks_hit = db_stats.get('blks_hit', 0)
                    blks_read = db_stats.get('blks_read', 0)
                    cache_hit_ratio = round(blks_hit / max(blks_hit + blks_read, 1) * 100, 2)

                return {
                    'action': 'db_perf',
                    'connections': pool,
                    'cache_hit_ratio_pct': cache_hit_ratio,
                    'transactions': {
                        'committed': db_stats.get('xact_commit', 0),
                        'rolled_back': db_stats.get('xact_rollback', 0),
                    },
                    'tuples': {
                        'returned': db_stats.get('tup_returned', 0),
                        'fetched': db_stats.get('tup_fetched', 0),
                        'inserted': db_stats.get('tup_inserted', 0),
                        'updated': db_stats.get('tup_updated', 0),
                        'deleted': db_stats.get('tup_deleted', 0),
                    },
                    'deadlocks': db_stats.get('deadlocks', 0),
                    'conflicts': db_stats.get('conflicts', 0),
                }

            elif action == 'dependency_matrix':
                components = {}

                # 1. Web app (self)
                components['web'] = {'status': 'ok', 'detail': 'responding (this request succeeded)'}

                # 2. Database
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                    components['postgres'] = {'status': 'ok'}
                except Exception as e:
                    components['postgres'] = {'status': 'error', 'detail': str(e)[:100]}

                # 3. Redis
                try:
                    import redis as redis_lib
                    from django.conf import settings
                    r = redis_lib.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1'), socket_timeout=3)
                    r.ping()
                    components['redis'] = {'status': 'ok'}
                except Exception as e:
                    components['redis'] = {'status': 'error', 'detail': str(e)[:100]}

                # 4. Celery workers
                try:
                    from core.celery import app as celery_app
                    inspector = celery_app.control.inspect(timeout=5)
                    pong = inspector.ping() or {}
                    worker_count = len(pong)
                    components['celery'] = {'status': 'ok' if worker_count > 0 else 'warning', 'workers': worker_count}
                except Exception as e:
                    components['celery'] = {'status': 'error', 'detail': str(e)[:100]}

                # 5. pgvector
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                        row = cursor.fetchone()
                    components['pgvector'] = {'status': 'ok', 'version': row[0] if row else 'not installed'}
                except Exception as e:
                    components['pgvector'] = {'status': 'error', 'detail': str(e)[:100]}

                # 6. Spiders (recent data check)
                try:
                    from core.models_unified_system import LegacySpiderData
                    from django.utils import timezone
                    from datetime import timedelta
                    recent = LegacySpiderData.objects.filter(created_at__gte=timezone.now() - timedelta(hours=2)).count()
                    components['spiders'] = {'status': 'ok' if recent > 0 else 'warning', 'items_last_2h': recent}
                except Exception as e:
                    components['spiders'] = {'status': 'error', 'detail': str(e)[:100]}

                # 7. Storage (Cloudinary check)
                try:
                    from django.core.files.storage import default_storage
                    backend = type(default_storage).__name__
                    components['storage'] = {'status': 'ok', 'backend': backend}
                except Exception as e:
                    components['storage'] = {'status': 'error', 'detail': str(e)[:100]}

                all_ok = all(c.get('status') == 'ok' for c in components.values())
                has_error = any(c.get('status') == 'error' for c in components.values())

                return {
                    'action': 'dependency_matrix',
                    'overall': 'healthy' if all_ok else 'degraded' if not has_error else 'critical',
                    'components': components,
                    'total': len(components),
                    'healthy': sum(1 for c in components.values() if c.get('status') == 'ok'),
                    'warnings': sum(1 for c in components.values() if c.get('status') == 'warning'),
                    'errors': sum(1 for c in components.values() if c.get('status') == 'error'),
                }

            elif action == 'runtime_metrics':
                import os
                import platform
                import psutil

                process = psutil.Process(os.getpid())
                mem = process.memory_info()
                uptime_secs = time.time() - process.create_time()

                # System-wide
                vm = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                return {
                    'action': 'runtime_metrics',
                    'process': {
                        'pid': os.getpid(),
                        'rss_mb': round(mem.rss / 1024 / 1024, 1),
                        'vms_mb': round(mem.vms / 1024 / 1024, 1),
                        'cpu_percent': process.cpu_percent(interval=0.1),
                        'threads': process.num_threads(),
                        'uptime_seconds': round(uptime_secs),
                        'uptime_human': f"{int(uptime_secs // 3600)}h {int((uptime_secs % 3600) // 60)}m",
                    },
                    'system': {
                        'total_ram_mb': round(vm.total / 1024 / 1024, 1),
                        'available_ram_mb': round(vm.available / 1024 / 1024, 1),
                        'ram_percent': vm.percent,
                        'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 1),
                        'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 1),
                        'disk_percent': disk.percent,
                        'cpu_count': os.cpu_count(),
                        'platform': platform.platform(),
                    },
                    'railway': {
                        'environment': os.environ.get('RAILWAY_ENVIRONMENT', ''),
                        'service': os.environ.get('RAILWAY_SERVICE_NAME', ''),
                        'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', ''),
                        'replica_id': os.environ.get('RAILWAY_REPLICA_ID', ''),
                    },
                }

            all_actions = ['redis_health', 'db_perf', 'dependency_matrix', 'runtime_metrics']
            return {'error': f'Unknown infra_health action: {action}. Valid: {", ".join(all_actions)}'}

        except Exception as e:
            logger.error(f"[INFRA_HEALTH] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # =========================================================================
    # R2-6: KB / Embedding browsing tool
    # =========================================================================

    def _handle_kb_browse(self, tool_name, payload, user_id, trace_id):
        """R2-6: Browse KB documents, embedding collections, and chunk counts."""
        action = payload.get('action', 'stats')
        # Session 2728 F-KB-1 / S2730 F-RL-2 — surface the hard cap on
        # `limit` explicitly via the shared `td_limit_envelope.compute_limit`
        # helper. Rigby sees the `limit_capped/requested_limit/
        # effective_limit/hard_max` F-D-5 shape when she requests more
        # than the handler will return.
        from core.services.td_limit_envelope import compute_limit
        limit, _envelope = compute_limit(payload, default=20, hard_max=50)

        def _apply_limit_envelope(resp: Dict[str, Any]) -> Dict[str, Any]:
            """Attach limit-cap fields when caller exceeded the hard maximum.
            Preserved as a closure wrapper so the four call sites below
            keep their existing shape; the helper's envelope dict is
            spread into the response only when non-empty."""
            resp.update(_envelope)
            return resp

        try:
            if action == 'stats':
                from content.models import Document, DocumentEmbedding
                from persistence.models import UnifiedEmbedding
                from core.models_unified_system import LegacySpiderData
                from django.db.models import Count

                doc_count = Document.objects.count()
                doc_with_embeddings = Document.objects.filter(embeddings__isnull=False).distinct().count()
                doc_embedding_count = DocumentEmbedding.objects.count()
                unified_count = UnifiedEmbedding.objects.count()
                spider_with_embedding = LegacySpiderData.objects.filter(embedding__isnull=False).count()

                # Breakdown by content_type
                unified_by_type = list(
                    UnifiedEmbedding.objects.values('content_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                )

                return {
                    'action': 'stats',
                    'documents': {'total': doc_count, 'with_embeddings': doc_with_embeddings},
                    'document_embeddings': doc_embedding_count,
                    'unified_embeddings': unified_count,
                    'unified_by_type': unified_by_type,
                    'spider_data_with_embedding': spider_with_embedding,
                }

            elif action == 'documents':
                # Session 1234 D11 — filter params over D9/D10 enrichment.
                # The Document table now carries category / document_class /
                # is_pinned / tags / retrieval_boost (D9 sync + D10 backfill);
                # this action exposes them as filters so Rigby can scope
                # browsing to "only current architecture docs", "exclude
                # superseded handoffs", "only docs from session 1200+", etc.
                #
                # Default behavior: exclude `status='superseded'`. Pre-D11
                # the documents listing returned the entire corpus ordered
                # by created_at desc, so a session-649 superseded handoff
                # surfaced ahead of an active spec from last week.
                from content.models import Document, ContentStatus
                from django.db.models import Count

                query = payload.get('query', '').strip()
                f_category = (payload.get('category') or '').strip()
                f_document_class = (payload.get('document_class') or '').strip()
                f_is_pinned = payload.get('is_pinned')
                f_min_session = payload.get('min_session')
                include_superseded = bool(payload.get('include_superseded', False))

                qs = Document.objects.annotate(chunk_count=Count('embeddings'))

                if query:
                    qs = qs.filter(title__icontains=query)
                if f_category:
                    qs = qs.filter(category=f_category)
                if f_document_class:
                    qs = qs.filter(document_class=f_document_class)
                if f_is_pinned is True:
                    qs = qs.filter(is_pinned=True)
                # Note: f_is_pinned=False intentionally NOT filtered — that
                # would mostly return historical docs. Truthy-only check
                # (per memory feedback_llm_autofills_boolean_params_with_false).
                if not include_superseded:
                    qs = qs.exclude(status=ContentStatus.ARCHIVED)
                # Session 1234 D14 — only honor positive min_session. The
                # LLM autofills integer params with 0 the same way it
                # autofills boolean params with False (memory:
                # feedback_llm_autofills_boolean_params_with_false). A
                # min_session=0 silently filters the corpus to handoffs-
                # only (since only handoffs carry session-N tags), then
                # competes them against the similarity threshold — often
                # zero results when the LLM didn't intend any filter.
                if f_min_session is not None:
                    try:
                        threshold = int(f_min_session)
                        if threshold > 0:
                            # Tag format from D9: 'session-1234'. Filter docs
                            # whose tags include any session-N with N >= threshold.
                            # Use a Python-side filter since tags is a JSONField
                            # of variable shape.
                            ids_keep = []
                            for d in qs.only('id', 'tags'):
                                for t in (d.tags or []):
                                    if isinstance(t, str) and t.startswith('session-'):
                                        try:
                                            if int(t.split('-', 1)[1]) >= threshold:
                                                ids_keep.append(d.id)
                                                break
                                        except (ValueError, IndexError):
                                            continue
                            qs = qs.filter(id__in=ids_keep)
                    except (ValueError, TypeError):
                        pass

                # Order: pinned + boost first, then recency. Pre-D11 ordered
                # by created_at only, which surfaced ANY recent doc above
                # high-leverage pinned ones.
                qs = qs.order_by('-is_pinned', '-retrieval_boost', '-created_at')

                docs = qs[:limit]
                return _apply_limit_envelope({
                    'action': 'documents',
                    'count': len(docs),
                    'applied_filters': {
                        'query': query or None,
                        'category': f_category or None,
                        'document_class': f_document_class or None,
                        'is_pinned': f_is_pinned if f_is_pinned is True else None,
                        'min_session': _d14_resolve_min_session(f_min_session),
                        'include_superseded': include_superseded,
                    },
                    'documents': [{
                        'id': str(d.id),
                        'title': d.title,
                        'category': d.category,
                        'document_class': d.document_class,
                        'is_pinned': d.is_pinned,
                        'tags': list(d.tags or []),
                        'retrieval_boost': float(d.retrieval_boost or 1.0),
                        'chunk_count': d.chunk_count,
                        'created_at': d.created_at.isoformat() if hasattr(d, 'created_at') and d.created_at else None,
                    } for d in docs],
                })

            elif action == 'chunks':
                doc_id = payload.get('document_id', '') or payload.get('id', '')
                if not doc_id:
                    return {'error': 'document_id required for chunks action'}
                from content.models import DocumentEmbedding
                chunks = DocumentEmbedding.objects.filter(document_id=doc_id).order_by('chunk_index')[:limit]
                return _apply_limit_envelope({
                    'action': 'chunks',
                    'document_id': doc_id,
                    'count': len(chunks),
                    'chunks': [{
                        'chunk_index': c.chunk_index,
                        'chunk_size': c.chunk_size,
                        'text_preview': c.chunk_text[:300],
                        'has_embedding': c.embedding is not None if hasattr(c, 'embedding') else None,
                    } for c in chunks],
                })

            elif action == 'search_embeddings':
                query = payload.get('query', '').strip()
                content_type = payload.get('content_type', '').strip()
                if not query and not content_type:
                    return {'error': 'query or content_type required for search_embeddings'}
                from persistence.models import UnifiedEmbedding
                qs = UnifiedEmbedding.objects.all()
                if content_type:
                    qs = qs.filter(content_type=content_type)
                if query:
                    from django.db.models import Q as DQ
                    qs = qs.filter(
                        DQ(content_text__icontains=query) | DQ(content_title__icontains=query)
                    )
                qs = qs.order_by('-created_at')[:limit]
                return _apply_limit_envelope({
                    'action': 'search_embeddings',
                    'count': len(qs),
                    'results': [{
                        'id': str(e.id),
                        'content_type': e.content_type,
                        'title': e.content_title[:200],
                        'text_preview': e.content_text[:300],
                        'source_system': e.source_system,
                        'created_at': e.created_at.isoformat() if hasattr(e, 'created_at') and e.created_at else None,
                    } for e in qs],
                })

            elif action == 'semantic_search':
                # Session 1234 D13 — native vector similarity over
                # DocumentEmbedding via pgvector. Rigby's first real
                # semantic search PA tool action; before D13 the only
                # semantic-ish path was `search_docs` (token-overlap
                # over .rag/corpus.jsonl, local-file only) or
                # `search_embeddings` (text icontains over the empty
                # UnifiedEmbedding table). This action threads the
                # full D9/D10 filter pushdown so a query like "morning
                # brief workflow" returns the active spec first, not a
                # random 2025 superseded handoff.
                from core.rag_integration import search_embeddings

                query = (payload.get('query') or '').strip()
                if not query:
                    return {'error': 'query is required for semantic_search'}

                # Session 1234 D15 — default lowered from 0.6 to 0.4.
                # Chris's first verification run with the 0.6 default
                # against "morning_brief workflow" returned 0 chunks
                # because text-embedding-3-small typically produces
                # similarities in the 0.4-0.7 band for related-but-
                # not-identical content. Direct ORM check at 0.3
                # surfaced the right Daily-CoS arc handoffs at
                # similarities 0.567-0.630 — the 0.6 default was
                # cutting almost all real signal. 0.4 keeps obvious
                # noise out while still surfacing the corpus.
                try:
                    sim_threshold = float(payload.get('similarity_threshold', 0.4) or 0.4)
                except (TypeError, ValueError):
                    sim_threshold = 0.4
                # Clamp into a sensible band.
                sim_threshold = max(0.0, min(sim_threshold, 1.0))

                f_category = (payload.get('category') or '').strip() or None
                f_document_class = (payload.get('document_class') or '').strip() or None
                f_is_pinned = payload.get('is_pinned')
                f_min_session = payload.get('min_session')
                include_superseded = bool(payload.get('include_superseded', False))
                # Cycle 1A KFI-3 (ADR-0130): authority-aware retrieval params.
                # Empty string coerced to None for canonical_authority so
                # LLM-autofilled '' does not narrow the corpus.
                f_canonical_authority = (
                    (payload.get('canonical_authority') or '').strip() or None
                )
                f_authority_weighted = bool(
                    payload.get('authority_weighted', False)
                )

                # ═══════════════════════════════════════════════════════════════
                # Session 2824 — Phase-0.5 advisory-only dogfood router
                # feature flag. Per S2823 constitutional package (Chris R1
                # advisory-only): when the flag is off, the retrieval + envelope
                # path below is BYTE-IDENTICAL to pre-flag behavior — no import,
                # no logging, no envelope additions. When the flag is on, the
                # router runs BEFORE search_embeddings, logs to durable JSONL
                # SoT + mirror in `finally` (even on retrieval error per
                # Rigby S2824 Q4 fix), and appends an additive `_router_advisory`
                # v1 field to the envelope. `_parallel_both` is ALWAYS null in
                # Phase-0.5 per §7 CRITICAL SCOPE DISTINCTION.
                # See docs/research/discovery_layer/PHASE_0_5/
                # ROUTER_SCAFFOLDING_DESIGN.md §15 for R1-R7 constraints.
                # ═══════════════════════════════════════════════════════════════
                from django.conf import settings as _p05_settings
                if not getattr(_p05_settings, 'PHASE_0_5_ROUTER_ENABLED', False):
                    # ── BYTE-IDENTICAL FLAG-OFF PATH — do not modify ──
                    chunks = search_embeddings(
                        query=query,
                        limit=limit,
                        similarity_threshold=sim_threshold,
                        category=f_category,
                        document_class=f_document_class,
                        is_pinned=(f_is_pinned if f_is_pinned is True else None),
                        min_session=_d14_resolve_min_session(f_min_session),
                        include_superseded=include_superseded,
                        canonical_authority=f_canonical_authority,
                        authority_weighted=f_authority_weighted,
                    )

                    return _apply_limit_envelope({
                        'action': 'semantic_search',
                        'count': len(chunks),
                        'applied_filters': {
                            'query': query,
                            'category': f_category,
                            'document_class': f_document_class,
                            'is_pinned': f_is_pinned if f_is_pinned is True else None,
                            'min_session': _d14_resolve_min_session(f_min_session),
                            'include_superseded': include_superseded,
                            'similarity_threshold': sim_threshold,
                            'canonical_authority': f_canonical_authority,
                            'authority_weighted': f_authority_weighted,
                        },
                        'chunks': [{
                            'id': c['id'],
                            'similarity': c['similarity_score'],
                            'importance': c['importance_score'],
                            'content_preview': (c.get('content') or '')[:500],
                            'file_path': c['metadata'].get('file_path'),
                            'title': c['metadata'].get('title'),
                            'category': c['metadata'].get('category'),
                            'document_class': c['metadata'].get('document_class'),
                            'is_pinned': c['metadata'].get('is_pinned'),
                            'tags': c['metadata'].get('tags', []),
                            'chunk_index': c['metadata'].get('chunk_index'),
                            'citation': c['metadata'].get('citation'),
                            # Cycle 1A KFI-3: authority-aware fields.
                            'canonical_authority': c.get('canonical_authority'),
                            'authority_weight': c.get('authority_weight'),
                            'weighted_score': c.get('weighted_score'),
                        } for c in chunks],
                    })

                # ── PHASE-0.5 INSTRUMENTED PATH (advisory-only) ──
                from core.services.phase_0_5_router import get_router
                _p05_router = get_router()
                _p05_decision = _p05_router.classify(query)
                _p05_retrieval_error = None
                _p05_retrieval_exception_type = None
                _p05_retrieval_count = 0
                chunks = []
                try:
                    chunks = search_embeddings(
                        query=query,
                        limit=limit,
                        similarity_threshold=sim_threshold,
                        category=f_category,
                        document_class=f_document_class,
                        is_pinned=(f_is_pinned if f_is_pinned is True else None),
                        min_session=_d14_resolve_min_session(f_min_session),
                        include_superseded=include_superseded,
                        canonical_authority=f_canonical_authority,
                        authority_weighted=f_authority_weighted,
                    )
                    _p05_retrieval_count = len(chunks)
                except Exception as _p05_exc:
                    _p05_retrieval_error = str(_p05_exc)[:500]
                    _p05_retrieval_exception_type = type(_p05_exc).__name__
                    logger.error(
                        "[PHASE_0_5_ROUTER] semantic_search raised; logging "
                        "decision-with-error per Rigby Q4 fix: %s: %s",
                        _p05_retrieval_exception_type,
                        _p05_retrieval_error,
                    )
                finally:
                    _p05_router.log_decision(
                        query=query,
                        decision=_p05_decision,
                        chosen_substrate='semantic_search',
                        actual_substrate='semantic_search',
                        retrieval_count=_p05_retrieval_count,
                        retrieval_error=_p05_retrieval_error,
                        retrieval_exception_type=_p05_retrieval_exception_type,
                    )

                return _apply_limit_envelope({
                    'action': 'semantic_search',
                    'count': _p05_retrieval_count,
                    'applied_filters': {
                        'query': query,
                        'category': f_category,
                        'document_class': f_document_class,
                        'is_pinned': f_is_pinned if f_is_pinned is True else None,
                        'min_session': _d14_resolve_min_session(f_min_session),
                        'include_superseded': include_superseded,
                        'similarity_threshold': sim_threshold,
                        'canonical_authority': f_canonical_authority,
                        'authority_weighted': f_authority_weighted,
                    },
                    'chunks': [{
                        'id': c['id'],
                        'similarity': c['similarity_score'],
                        'importance': c['importance_score'],
                        'content_preview': (c.get('content') or '')[:500],
                        'file_path': c['metadata'].get('file_path'),
                        'title': c['metadata'].get('title'),
                        'category': c['metadata'].get('category'),
                        'document_class': c['metadata'].get('document_class'),
                        'is_pinned': c['metadata'].get('is_pinned'),
                        'tags': c['metadata'].get('tags', []),
                        'chunk_index': c['metadata'].get('chunk_index'),
                        'citation': c['metadata'].get('citation'),
                        # Cycle 1A KFI-3: authority-aware fields.
                        'canonical_authority': c.get('canonical_authority'),
                        'authority_weight': c.get('authority_weight'),
                        'weighted_score': c.get('weighted_score'),
                    } for c in chunks],
                    # Phase-0.5 advisory metadata (per B2 §7). Categorical
                    # confidence only per Chris R4/§10.4. `_parallel_both`
                    # ALWAYS null in Phase-0.5 per §7 CRITICAL SCOPE
                    # DISTINCTION (advisory-only-vs-execution boundary).
                    '_router_advisory': {
                        'version': 'v1',
                        'predicted_family': _p05_decision.predicted_family,
                        'confidence_categorical': _p05_decision.confidence_categorical,
                        'matched_rules': list(_p05_decision.matched_rules),
                        'abstain_reason': _p05_decision.abstain_reason,
                        'abstain_option': _p05_decision.abstain_option,
                        'clarify_context_type': _p05_decision.clarify_context_type,
                        'suggested_alternative_substrate': (
                            _p05_decision.suggested_alternative_substrate
                        ),
                        'measurement_window_id': _p05_decision.measurement_window_id,
                        'measurement_window_type': _p05_decision.measurement_window_type,
                        'parallel_both_substrates': None,
                        'integrity_stop': _p05_decision.integrity_stop_trigger,
                        'integrity_stop_reason': _p05_decision.integrity_stop_reason,
                        'retrieval_failed': _p05_retrieval_error is not None,
                    },
                })

            return {'error': f'Unknown kb_tool action: {action}. Valid: stats, documents, chunks, search_embeddings, semantic_search'}

        except Exception as e:
            logger.error(f"[KB_BROWSE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # =========================================================================
    # Session 1142: search_docs — semantic-ish doc search over .rag/corpus.jsonl
    # =========================================================================

    def _handle_search_docs(self, tool_name, payload, user_id, trace_id):
        """Search the /docs/ corpus via core.rag.top_k.

        Returns ranked chunks with [docs/path#chunk_id] citations. The corpus
        is a token-overlap + hint-boosted scorer over .rag/corpus.jsonl (not
        true vector similarity — that path is `kb_tool` over Document +
        DocumentEmbedding). Use this for "find the passage about X" queries
        that need an inline-cited answer grounded in the doc corpus.
        """
        query = (payload.get('query') or '').strip()
        if not query:
            return {'error': 'query is required'}
        try:
            k = max(1, min(int(payload.get('k', 8) or 8), 20))
        except (TypeError, ValueError):
            k = 8
        try:
            max_chars = max(500, min(int(payload.get('max_chars', 6000) or 6000), 12000))
        except (TypeError, ValueError):
            max_chars = 6000

        # Session 1145 P2: optional originating_session filter.
        # Session 2728 F-SD-1: LLM-autofill guard. Prior handler applied a
        # "restrict to originating_session=0" filter whenever GPT-5.2 autofilled
        # the optional integer with 0 — the same LLM-autofill pattern documented
        # in memory rule `feedback_llm_autofills_boolean_params_with_false` for
        # booleans. Autofilled zero filter silently returned zero results and
        # crystallized memory rule `feedback_ratification_workflow_gotchas`
        # (workaround: "use kb_tool instead"). `_resolve_originating_session`
        # applies the same positive-only guard kb_tool uses for min_session
        # via `_d14_resolve_min_session`. A non-int payload still returns the
        # typed error (only guard non-int → error remains); int 0 or negative
        # now falls through as no-filter, matching the schema description
        # "Optional. Restrict results to chunks from docs whose originating
        # session matches" (emphasis on Optional).
        originating_session_raw = payload.get('originating_session')
        originating_session: Optional[int] = None
        if originating_session_raw is not None:
            # Reject non-int inputs with a typed error (unchanged behavior).
            try:
                _tmp = int(originating_session_raw)
            except (TypeError, ValueError):
                return {
                    'error': 'originating_session must be an integer (e.g. 1142)',
                    'query': query,
                }
            # Apply positive-only guard for int inputs (autofill defense).
            originating_session = _resolve_originating_session(originating_session_raw)

        try:
            from core.rag import top_k, CORPUS_PATH

            if not CORPUS_PATH.exists():
                return {
                    'error': (
                        f'RAG corpus not found at {CORPUS_PATH}. '
                        'Run `python manage.py build_rag_corpus` to build it.'
                    ),
                    'query': query,
                }

            # boost_hints=False: skip the legacy learning-loop bias so
            # general doc questions get neutral token-overlap ranking.
            # When a session filter is active, overshoot k so post-filter
            # we still have a useful number of chunks to return.
            k_fetch = min(k * 4, 80) if originating_session is not None else k
            rows = top_k(query, k=k_fetch, boost_hints=False)
            if not rows:
                return {
                    'query': query,
                    'result_count': 0,
                    'chunks': [],
                    'note': (
                        'No matching chunks. Try broader terms; if recently-'
                        'added docs are missing, run `python manage.py build_rag_corpus`.'
                    ),
                }

            chunks = []
            total = 0
            truncated = False
            for r in rows:
                f = r.get('file', '') or ''
                # Corpus paths drop the leading 'docs/'. Add it back so the
                # citation matches a real on-disk path the reader can open.
                cite_path = f if f.startswith('docs/') else f'docs/{f}'
                text = ' '.join((r.get('text') or '').split())
                citation = f"[{cite_path}#{r.get('chunk_id')}]"
                overhead = len(citation) + 1  # +1 for the space joining citation+text
                remaining = max_chars - total - overhead

                if remaining <= 0:
                    # No room even for the citation; stop.
                    truncated = True
                    break

                if len(text) > remaining:
                    # Truncate this chunk's text so we still return *something*.
                    text = text[:remaining].rstrip() + '…'
                    truncated = True

                chunks.append({
                    'file': cite_path,
                    'chunk_id': r.get('chunk_id'),
                    'citation': citation,
                    'text': text,
                })
                total += overhead + len(text)
                if truncated:
                    break

            # Session 1145 P2: apply originating_session filter post-ranking.
            filter_meta: Optional[dict] = None
            if originating_session is not None:
                provenance_docs = _load_provenance_docs()
                if not provenance_docs:
                    return {
                        'query': query,
                        'result_count': 0,
                        'chunks': [],
                        'originating_session': originating_session,
                        'note': (
                            f'Provenance index not found at {PROVENANCE_INDEX_PATH}. '
                            'Run `python manage.py build_docs_provenance` to build it.'
                        ),
                    }
                kept, excluded_mismatch, excluded_missing = (
                    _filter_chunks_by_originating_session(
                        chunks, originating_session, provenance_docs,
                    )
                )
                # Trim to requested k after filter.
                chunks = kept[:k]
                filter_meta = {
                    'originating_session': originating_session,
                    'pre_filter_count': len(kept) + excluded_mismatch + excluded_missing,
                    'excluded_mismatch': excluded_mismatch,
                    'excluded_missing_provenance': excluded_missing,
                }
                # Recompute total_chars + truncated for the trimmed set.
                total = sum(len(c.get('citation', '')) + 1 + len(c.get('text', '')) for c in chunks)
                truncated = False  # k truncation already accounted for above

            result = {
                'query': query,
                'result_count': len(chunks),
                'k_requested': k,
                'max_chars': max_chars,
                'truncated': truncated,
                'total_chars': total,
                'chunks': chunks,
            }
            if filter_meta is not None:
                result['filter'] = filter_meta
            return result

        except Exception as e:
            logger.error(f"[SEARCH_DOCS] error: {e}", exc_info=True)
            return {'error': str(e), 'query': query}

    # =========================================================================
    # Session 1031: Dream Tool — browse, approve, dismiss dreams via PA
    # =========================================================================

    # =========================================================================
    # Session 1202 — Phase A.2: Diagnostic Telemetry Tools
    # =========================================================================
    # Surfaces audit/inventory data Rigby needs to grade subsystem health
    # without ORM bypass. Per CONNECTIVITY_COMPLETION_ROADMAP.md §A.2.
    # PR-1 ships the 4 simple actions (advisor_invocations, provider_calls,
    # beat_schedule_health, workspace_metrics); PR-2 will add the 3 medium-
    # complex actions (schema_handler_diff, learning_bridge_writes,
    # discord_health). Read-only — no new DB tables, no mutations.

    _DIAGNOSTICS_WINDOW_DAYS = {
        '1d': 1, '7d': 7, '14d': 14, '30d': 30, '90d': 90,
    }

    # Session 1202 v3 — schemas intercepted by the PA entrypoint
    # (unified_pa_entrypoint.py:1687) before reaching the dispatcher.
    # These appear as "schema without handler" to a naive diff but are
    # by-design. Keep this list narrow — only entries that match the
    # documented meta-tool pattern. New meta-tools added in the PA loop
    # must be added here.
    _SCHEMA_HANDLER_DIFF_META_TOOLS = {'run_agent'}

    def _diagnostics_resolve_window(self, payload: Dict[str, Any], default_days: int = 7) -> int:
        """Translate a `window` string ("7d", "30d", ...) into days; falls
        back to ``default_days`` for unknown values."""
        window = (payload.get('window') or f'{default_days}d').strip()
        return self._DIAGNOSTICS_WINDOW_DAYS.get(window, default_days)

    def _handle_diagnostics(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Session 1202 §A.2 — Diagnostic telemetry surface.

        Returns structured JSON per action. Each branch is read-only and
        bounded; no new DB tables, no mutations, no agent dispatches.
        """
        action = payload.get('action', '')

        if action == 'advisor_invocations':
            return self._diagnostics_advisor_invocations(payload, trace_id)
        elif action == 'provider_calls':
            return self._diagnostics_provider_calls(payload, trace_id)
        elif action == 'beat_schedule_health':
            return self._diagnostics_beat_schedule_health(payload, trace_id)
        elif action == 'workspace_metrics':
            return self._diagnostics_workspace_metrics(payload, trace_id)

        elif action == 'schema_handler_diff':
            return self._diagnostics_schema_handler_diff(payload, trace_id)
        elif action == 'learning_bridge_writes':
            return self._diagnostics_learning_bridge_writes(payload, trace_id)
        elif action == 'discord_health':
            return self._diagnostics_discord_health(payload, trace_id)

        valid_actions = sorted([
            'advisor_invocations', 'provider_calls', 'beat_schedule_health',
            'workspace_metrics', 'schema_handler_diff', 'learning_bridge_writes',
            'discord_health',
        ])
        return {
            'gateway': 'diagnostics_tool',
            'error': f"Unknown diagnostics_tool action: '{action}'. Valid: {', '.join(valid_actions)}",
        }

    def _diagnostics_advisor_invocations(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Per-advisor invocation count over the requested window.

        Source: ``AgentExecution`` rows where ``agent.name`` matches an
        ``Advisor.name`` row. Both active and inactive advisors are
        listed; advisors with zero invocations surface as 0 (the value
        of this audit is finding *dead* advisors, not just busy ones).
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q

        from core.models_unified_system import Advisor, AgentExecution

        days = self._diagnostics_resolve_window(payload, default_days=7)
        since = timezone.now() - timedelta(days=days)

        advisor_rows = list(
            Advisor.objects.all().values('id', 'name', 'category', 'is_active', 'last_consultation')
        )
        advisor_names = [a['name'] for a in advisor_rows]

        # One aggregate query: count invocations per agent.name in the window
        invocation_counts = dict(
            AgentExecution.objects
            .filter(agent__name__in=advisor_names, created_at__gte=since)
            .values('agent__name')
            .annotate(c=Count('id'))
            .values_list('agent__name', 'c')
        )

        advisors_out = []
        zero_invocation = 0
        for a in advisor_rows:
            count = int(invocation_counts.get(a['name'], 0))
            if count == 0:
                zero_invocation += 1
            advisors_out.append({
                'id': str(a['id']),
                'name': a['name'],
                'category': a['category'],
                'is_active': a['is_active'],
                'last_consultation': a['last_consultation'].isoformat() if a['last_consultation'] else None,
                'invocations_in_window': count,
            })

        # Sort by invocation count desc, then by name for deterministic output
        advisors_out.sort(key=lambda r: (-r['invocations_in_window'], r['name']))

        return {
            'gateway': 'diagnostics_tool',
            'action': 'advisor_invocations',
            'window_days': days,
            'since': since.isoformat(),
            'total_advisors': len(advisors_out),
            'zero_invocation_advisors': zero_invocation,
            'total_invocations_in_window': sum(r['invocations_in_window'] for r in advisors_out),
            'advisors': advisors_out,
        }

    def _diagnostics_provider_calls(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Per-LLM-provider call count + success/cost rollup over the
        requested window.

        Source: ``LLMCallLog``. Reports every distinct provider seen in
        the window, plus zero rows for providers registered but unused
        (so 'dead' providers are visible).
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Sum, Q

        from core.models_llm_routing import LLMCallLog

        days = self._diagnostics_resolve_window(payload, default_days=7)
        since = timezone.now() - timedelta(days=days)

        rows = list(
            LLMCallLog.objects
            .filter(created_at__gte=since)
            .values('provider')
            .annotate(
                total_calls=Count('id'),
                successful_calls=Count('id', filter=Q(success=True)),
                total_cost=Sum('cost'),
                total_tokens=Sum('total_tokens'),
            )
            .order_by('-total_calls')
        )

        providers_out = []
        for r in rows:
            total = int(r['total_calls'] or 0)
            ok = int(r['successful_calls'] or 0)
            providers_out.append({
                'provider': r['provider'],
                'total_calls': total,
                'successful_calls': ok,
                'failure_calls': total - ok,
                'success_rate_pct': round(100.0 * ok / total, 1) if total else None,
                'total_tokens': int(r['total_tokens'] or 0),
                'total_cost_usd': float(r['total_cost'] or 0.0),
            })

        # Flag zero-call providers from the LLMProviderRegistry (if accessible)
        zero_call_providers = []
        try:
            from core.services.llm_provider_registry import LLMProviderRegistry
            registered = set(LLMProviderRegistry.list_provider_names())
            seen = {r['provider'] for r in providers_out}
            zero_call_providers = sorted(registered - seen)
        except Exception:  # noqa: BLE001 — best-effort enrichment
            pass

        return {
            'gateway': 'diagnostics_tool',
            'action': 'provider_calls',
            'window_days': days,
            'since': since.isoformat(),
            'total_providers_called': len(providers_out),
            'zero_call_providers': zero_call_providers,
            'providers': providers_out,
        }

    def _diagnostics_beat_schedule_health(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Beat schedule health snapshot.

        Source: ``django_celery_beat.PeriodicTask``. Sorted by
        ``last_run_at`` ascending so the staleest tasks surface first.
        Flags rows with zero historical runs (``total_run_count == 0``)
        separately — these have been registered but never fired.

        Pagination via ``offset`` + ``limit`` (default 50, max 200).
        Per-row payload stays small (8 fields); the count budget is the
        intent.
        """
        from django_celery_beat.models import PeriodicTask

        limit = min(int(payload.get('limit', 50) or 50), 200)
        offset = max(int(payload.get('offset', 0) or 0), 0)
        include_disabled = bool(payload.get('include_disabled', True))

        qs = PeriodicTask.objects.all()
        if not include_disabled:
            qs = qs.filter(enabled=True)

        total_count = qs.count()
        enabled_count = qs.filter(enabled=True).count()
        disabled_count = qs.filter(enabled=False).count()
        zero_run_count = qs.filter(total_run_count=0).count()
        zero_run_enabled = qs.filter(total_run_count=0, enabled=True).count()

        # Stalest first (NULLs last via -last_run_at desc gives NULLs first;
        # we want NULL last_run_at to be VERY stale, so order ASC and treat
        # NULLs as oldest via .order_by('last_run_at') — Postgres puts NULLs
        # last on ASC by default, so push them first with F+nulls_first.
        from django.db.models import F
        qs = qs.order_by(F('last_run_at').asc(nulls_first=True), 'name')

        rows = list(
            qs[offset:offset + limit].values(
                'id', 'name', 'task', 'enabled', 'last_run_at',
                'total_run_count', 'date_changed', 'one_off',
            )
        )

        tasks_out = []
        for r in rows:
            tasks_out.append({
                'id': r['id'],
                'name': r['name'],
                'task': r['task'],
                'enabled': r['enabled'],
                'last_run_at': r['last_run_at'].isoformat() if r['last_run_at'] else None,
                'total_run_count': r['total_run_count'],
                'date_changed': r['date_changed'].isoformat() if r['date_changed'] else None,
                'one_off': r['one_off'],
                'is_stale': r['last_run_at'] is None,
                'never_ran': r['total_run_count'] == 0,
            })

        return {
            'gateway': 'diagnostics_tool',
            'action': 'beat_schedule_health',
            'total_count': total_count,
            'enabled_count': enabled_count,
            'disabled_count': disabled_count,
            'zero_run_count': zero_run_count,
            'zero_run_enabled_count': zero_run_enabled,
            'limit': limit,
            'offset': offset,
            'returned': len(tasks_out),
            'has_more': (offset + len(tasks_out)) < total_count,
            'tasks': tasks_out,
        }

    def _diagnostics_workspace_metrics(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Per-workspace activity + deliverable count snapshot.

        Source: ``ProjectWorkspace`` joined to its deliverables. Fields:
        ``is_active``, ``allow_autonomous_writes``, ``last_operation_at``
        (closest field to the spec's ``last_activity``), and an
        annotated ``deliverable_count``. Pagination via ``offset`` +
        ``limit``; ``include_inactive`` defaults to True.
        """
        from django.db.models import Count

        from core.models_skin_layer import ProjectWorkspace

        limit = min(int(payload.get('limit', 50) or 50), 200)
        offset = max(int(payload.get('offset', 0) or 0), 0)
        include_inactive = bool(payload.get('include_inactive', True))

        qs = ProjectWorkspace.objects.all()
        if not include_inactive:
            qs = qs.filter(is_active=True)

        qs = qs.annotate(deliverable_count=Count('deliverables', distinct=True))
        total_count = qs.count()
        active_count = qs.filter(is_active=True).count()
        autonomous_count = qs.filter(allow_autonomous_writes=True).count()

        rows = list(
            qs.order_by('-last_operation_at', 'name')[offset:offset + limit].values(
                'id', 'name', 'workspace_type', 'is_active',
                'allow_autonomous_writes', 'last_operation_at',
                'total_operations', 'total_files_written', 'total_commits',
                'deliverable_count', 'created_at',
            )
        )

        workspaces_out = []
        for r in rows:
            workspaces_out.append({
                'id': str(r['id']),
                'name': r['name'],
                'workspace_type': r['workspace_type'],
                'is_active': r['is_active'],
                'allow_autonomous_writes': r['allow_autonomous_writes'],
                'last_operation_at': r['last_operation_at'].isoformat() if r['last_operation_at'] else None,
                'total_operations': r['total_operations'],
                'total_files_written': r['total_files_written'],
                'total_commits': r['total_commits'],
                'deliverable_count': r['deliverable_count'],
                'created_at': r['created_at'].isoformat() if r['created_at'] else None,
            })

        return {
            'gateway': 'diagnostics_tool',
            'action': 'workspace_metrics',
            'total_count': total_count,
            'active_count': active_count,
            'autonomous_count': autonomous_count,
            'limit': limit,
            'offset': offset,
            'returned': len(workspaces_out),
            'has_more': (offset + len(workspaces_out)) < total_count,
            'workspaces': workspaces_out,
        }

    # Canonical Learning Bridge registry (per
    # ``core/learning_bridges/apps.py``). Each entry maps a bridge to a
    # heuristic that estimates its attributable writes. ``writes_to`` is
    # the primary model the bridge persists into; ``filter_kwargs`` is
    # the best-effort attribution filter. Precise per-bridge attribution
    # would require a ``source_bridge`` field on the target model —
    # tracked as a follow-up; for now, learning_domain / learning_source
    # is the closest signal available.
    _LEARNING_BRIDGES = [
        {
            'name': 'agent_execution_bridge',
            'display_name': 'Agent Execution Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_source__in': ['success_pattern', 'failure_analysis', 'performance_tracking']},
            'attribution': 'heuristic',
        },
        {
            'name': 'application_outcome_bridge',
            'display_name': 'Application Outcome Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_domain__in': ['opportunity_matching', 'salary_preferences', 'skill_preferences']},
            'attribution': 'heuristic',
        },
        {
            'name': 'revenue_attribution_bridge',
            'display_name': 'Revenue Attribution Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_domain__in': ['revenue_optimization']},
            'attribution': 'heuristic',
        },
        {
            'name': 'advisor_feedback_bridge',
            'display_name': 'Advisor Feedback Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_source__in': ['user_feedback', 'explicit_instruction']},
            'attribution': 'heuristic',
        },
        {
            'name': 'collaboration_bridge',
            'display_name': 'Collaboration Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_domain__in': ['communication']},
            'attribution': 'heuristic',
        },
        {
            'name': 'personalization_bridge',
            'display_name': 'Personalization Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_source__in': ['interaction_mining']},
            'attribution': 'heuristic',
        },
        {
            'name': 'sports_betting_bridge',
            'display_name': 'Sports Betting Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_domain__startswith': 'sports_betting'},
            'attribution': 'precise',
        },
        {
            'name': 'spider_data_bridge',
            'display_name': 'Spider Data Bridge',
            'writes_to': 'UserAgentLearning',
            'filter_kwargs': {'learning_domain__in': ['general']},
            'attribution': 'heuristic',
        },
    ]

    def _diagnostics_schema_handler_diff(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Programmatic schema↔handler gap detection.

        Memory rule (Session 1201 P11): ``108 vs 173`` framing is false
        drift because 80 handlers are gateway-routed via the
        ``run_agent`` meta-tool, not directly mapped to schemas. This
        action classifies the delta:

        - ``schema_only`` — schema defined, no registered handler
          (real bug: LLM can emit a call that fails)
        - ``schema_only_meta_tool`` — schema defined, intercepted at
          the PA entrypoint layer (``unified_pa_entrypoint.py:1687``)
          before reaching the dispatcher. By design — NOT a bug.
          Currently: ``run_agent``.
        - ``handler_only_gateway`` — handler bound to
          ``_handle_agent_tool`` but not directly named in schemas
          (gateway-pattern-by-design; LLM reaches it via ``run_agent``)
        - ``handler_only_orphan`` — handler with no schema and not a
          gateway agent_tool (real bug: dead handler)
        - ``both_direct`` — schema + direct handler (the healthy case)

        Read-only; no mutations.
        """
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        # Schema-side: function names
        schema_names = {
            (s.get('name') or '').strip()
            for s in PA_TOOL_SCHEMAS
            if s.get('type') == 'function' and s.get('name')
        }
        schema_names.discard('')

        # Handler-side: name → (is_agent_tool, handler_repr)
        try:
            agent_tool_handler = self._handle_agent_tool  # type: ignore[attr-defined]
        except AttributeError:
            agent_tool_handler = None

        handler_meta: Dict[str, Dict[str, Any]] = {}
        # ``self`` is the dispatcher mixed-in; the registry lives on it.
        for name, fn in getattr(self, '_tool_handlers', {}).items():
            method_name = getattr(fn, '__name__', None) or repr(fn)
            is_agent_tool = (
                agent_tool_handler is not None and fn == agent_tool_handler
            ) or method_name == '_handle_agent_tool'
            handler_meta[name] = {
                'method': method_name,
                'is_gateway_agent_tool': is_agent_tool,
            }
        handler_names = set(handler_meta.keys())

        # Classifications
        both_direct = sorted(schema_names & handler_names)
        # Session 1202 v3 — split schema_only into "real bug" vs
        # "by-design meta-tool intercepted upstream." Rigby caught the
        # false positive on the PR-2 smoke: run_agent has a schema but
        # never reaches ToolDispatcher._tool_handlers because
        # unified_pa_entrypoint.py:1687 unpacks `agent_name` and
        # dispatches to the actual tool. Without this split, every
        # schema_handler_diff run flagged run_agent as a bug.
        schema_only_all = sorted(schema_names - handler_names)
        schema_only_meta_tool = sorted(n for n in schema_only_all if n in self._SCHEMA_HANDLER_DIFF_META_TOOLS)
        schema_only = sorted(set(schema_only_all) - set(schema_only_meta_tool))
        handler_only = handler_names - schema_names
        handler_only_gateway = sorted(
            n for n in handler_only if handler_meta[n]['is_gateway_agent_tool']
        )
        handler_only_orphan = sorted(
            n for n in handler_only if not handler_meta[n]['is_gateway_agent_tool']
        )

        return {
            'gateway': 'diagnostics_tool',
            'action': 'schema_handler_diff',
            'totals': {
                'schemas': len(schema_names),
                'handlers': len(handler_names),
                'both_direct': len(both_direct),
                'schema_only': len(schema_only),
                'schema_only_meta_tool': len(schema_only_meta_tool),
                'handler_only_gateway': len(handler_only_gateway),
                'handler_only_orphan': len(handler_only_orphan),
            },
            'schema_only': schema_only,
            'schema_only_meta_tool': schema_only_meta_tool,
            'handler_only_gateway_sample': handler_only_gateway[:20],
            'handler_only_gateway_truncated': len(handler_only_gateway) > 20,
            'handler_only_orphan': handler_only_orphan,
            'note': (
                'schema_only and handler_only_orphan are real gaps. '
                'schema_only_meta_tool is by design — these schemas are '
                'intercepted at the PA entrypoint layer before reaching '
                'the dispatcher (see unified_pa_entrypoint.py:1687). '
                'handler_only_gateway is by design — these handlers are '
                "reachable via the 'run_agent' meta-tool gateway."
            ),
        }

    def _diagnostics_learning_bridge_writes(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Per-bridge attribution of UserAgentLearning writes over a
        window.

        Attribution is heuristic for 6 of 8 bridges (precise per-bridge
        tagging would need a ``source_bridge`` field on
        ``UserAgentLearning``). ``sports_betting_bridge`` is precise
        because its ``learning_domain`` values are uniquely prefixed.
        Each bridge entry carries an ``attribution`` field so callers
        can weight the numbers appropriately.
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count

        from core.models_unified_system import UserAgentLearning

        days = self._diagnostics_resolve_window(payload, default_days=30)
        since = timezone.now() - timedelta(days=days)

        total_writes = UserAgentLearning.objects.filter(updated_at__gte=since).count()

        bridges_out = []
        for bridge in self._LEARNING_BRIDGES:
            try:
                qs = UserAgentLearning.objects.filter(updated_at__gte=since, **bridge['filter_kwargs'])
                count = qs.count()
            except Exception as e:  # noqa: BLE001 — best-effort
                count = -1
                err = f'{type(e).__name__}: {e}'
            else:
                err = None
            bridges_out.append({
                'name': bridge['name'],
                'display_name': bridge['display_name'],
                'writes_to': bridge['writes_to'],
                'attribution': bridge['attribution'],
                'writes_in_window': count,
                'attribution_filter': bridge['filter_kwargs'],
                'error': err,
            })

        # Domain + source breakdowns (the ground truth available)
        by_domain = dict(
            UserAgentLearning.objects
            .filter(updated_at__gte=since)
            .values('learning_domain')
            .annotate(c=Count('id'))
            .values_list('learning_domain', 'c')
        )
        by_source = dict(
            UserAgentLearning.objects
            .filter(updated_at__gte=since)
            .values('learning_source')
            .annotate(c=Count('id'))
            .values_list('learning_source', 'c')
        )

        return {
            'gateway': 'diagnostics_tool',
            'action': 'learning_bridge_writes',
            'window_days': days,
            'since': since.isoformat(),
            'total_writes_to_user_agent_learning': total_writes,
            'bridges': bridges_out,
            'by_domain': by_domain,
            'by_source': by_source,
            'note': (
                'Per-bridge attribution is heuristic for 6 of 8 bridges; '
                "precise tagging requires a future 'source_bridge' field "
                'on UserAgentLearning. by_domain / by_source rollups are '
                'the ground truth — bridges_out is the best-effort split.'
            ),
        }

    def _diagnostics_discord_health(
        self, payload: Dict[str, Any], trace_id: str,
    ) -> Dict[str, Any]:
        """Discord bot health snapshot.

        Sources:
        - ``CeleryTaskEvent`` rows where ``task_name`` matches the
          Discord task family — total invocations + success/failure
          breakdown over the window.
        - The most-recent SUCCESS event timestamp is used as a rough
          "last alive" proxy. Bot uptime in the strict sense (process
          uptime) isn't stored anywhere queryable; the freshest event
          is the best signal available.

        Returns structured JSON; no mutations.
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count, Q

        from core.models_celery_telemetry import CeleryTaskEvent

        days = self._diagnostics_resolve_window(payload, default_days=7)
        since = timezone.now() - timedelta(days=days)

        # Match anything in the discord task family
        discord_q = (
            Q(task_name__icontains='discord') |
            Q(task_name__icontains='Discord')
        )

        qs = CeleryTaskEvent.objects.filter(discord_q, started_at__gte=since)
        total_invocations = qs.count()
        success_count = qs.filter(status='SUCCESS').count()
        failure_count = qs.filter(status='FAILURE').count()
        in_flight = qs.filter(status='STARTED').count()
        success_rate_pct = (
            round(100.0 * success_count / total_invocations, 1)
            if total_invocations else None
        )

        # Per-task breakdown (which discord tasks are running)
        per_task = list(
            qs.values('task_name')
            .annotate(
                total=Count('id'),
                successful=Count('id', filter=Q(status='SUCCESS')),
                failed=Count('id', filter=Q(status='FAILURE')),
            )
            .order_by('-total')[:25]
        )

        # Last-alive proxy: most recent SUCCESS event regardless of window
        latest_success = (
            CeleryTaskEvent.objects
            .filter(discord_q, status='SUCCESS')
            .order_by('-started_at')
            .values('task_name', 'started_at')
            .first()
        )
        if latest_success:
            last_alive_at = latest_success['started_at'].isoformat() if latest_success['started_at'] else None
            last_alive_task = latest_success['task_name']
            mins_since_alive = (
                int((timezone.now() - latest_success['started_at']).total_seconds() / 60)
                if latest_success['started_at'] else None
            )
        else:
            last_alive_at = None
            last_alive_task = None
            mins_since_alive = None

        return {
            'gateway': 'diagnostics_tool',
            'action': 'discord_health',
            'window_days': days,
            'since': since.isoformat(),
            'total_invocations_in_window': total_invocations,
            'success_count': success_count,
            'failure_count': failure_count,
            'in_flight_count': in_flight,
            'success_rate_pct': success_rate_pct,
            'last_alive_at': last_alive_at,
            'last_alive_task': last_alive_task,
            'minutes_since_last_alive': mins_since_alive,
            'per_task': per_task,
            'note': (
                "Uptime in the strict sense (bot process uptime) is not "
                "queryable; minutes_since_last_alive is a proxy based "
                "on the most-recent SUCCESS event for any discord task. "
                "Stale (>60min) likely means the bot is down."
            ),
        }

