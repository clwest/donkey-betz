"""
ToolDispatcher OpsHandlersMixin — extracted handler methods.
"""
from core.services.pa_identity import PA_IDENTITY

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
            window = payload.get('window', '24h')
            limit = payload.get('limit')
            return self._ops_top_consumers(window, limit, trace_id)

        else:
            return {'error': f'Unknown ops_tool action: {action}'}

    def _ops_version(self, trace_id: str) -> Dict[str, Any]:
        """Return build/deploy metadata for the running process."""
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
        }

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
                top_agents = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed'
                    ).values('agent__name')
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
                top_timeout = list(
                    AgentExecution.objects.filter(
                        created_at__gte=cutoff, status='failed',
                        error_message__icontains='timed out'
                    ).values('agent__name')
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
        self, window: str, limit, trace_id: str,
    ) -> Dict[str, Any]:
        """Top wall-clock consumers per task_name — single SQL aggregate.

        Session 1167 — COO Nervous System Backlog item #7. Reduces to
        ``core.services.top_consumers.compute_top_consumers``; the
        service module is single-source-of-truth for the SQL + window
        vocabulary + p95 computation.
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
            return compute_top_consumers(window=window, limit=limit)
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
                priority_rank=int(payload.get('priority_rank', 100)),
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
            actions = _safe_autopilot_query(
                lambda: list(
                    AutopilotAction.objects.all()[:limit].values(
                        'id', 'created_at', 'action_type', 'agent_name',
                        'policy', 'dry_run', 'deploy_sha',
                    )
                ), []
            )
            for a in actions:
                a['created_at'] = a['created_at'].isoformat()

            return {
                'action': 'history',
                'count': len(actions),
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
            days = int(payload.get('days', 1))
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
                duration_minutes=int(payload.get('duration_minutes', 30)),
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

            days = int(payload.get('days', 30))
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

            days = int(payload.get('days', 7))
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

            days = int(payload.get('days', 30))
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

            days = int(payload.get('days', 7))
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

            days = int(payload.get('days', 30))
            engine = GrowthEngine()
            funnel = engine.get_funnel(days=days)
            return {'action': 'growth_funnel', **funnel}

        # ── Capacity Planning (Policy 36) ──
        elif action == 'capacity_forecast':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours', 24))
            engine = CapacityEngine()
            forecast = engine.get_capacity_forecast(hours=hours)
            return {'action': 'capacity_forecast', **forecast}

        elif action == 'capacity_bottleneck_report':
            from core.services.ops_autopilot import CapacityEngine

            hours = int(payload.get('hours', 24))
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

            days = int(payload.get('days', 7))
            engine = CapacityEngine()
            envelope = engine.get_budget_envelope(days=days)
            return {'action': 'capacity_budget_envelope', **envelope}

        # ── Security & Abuse (Policy 37) ──
        elif action == 'security_permission_drift':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours', 24))
            engine = SecurityEngine()
            report = engine.get_permission_drift_report(hours=hours)
            return {'action': 'security_permission_drift', **report}

        elif action == 'security_abuse_queue':
            from core.services.ops_autopilot import SecurityEngine

            hours = int(payload.get('hours', 24))
            limit = int(payload.get('limit', 50))
            engine = SecurityEngine()
            queue = engine.get_abuse_risk_queue(hours=hours, limit=limit)
            return {'action': 'security_abuse_queue', **queue}

        elif action == 'security_containment_plan':
            from core.services.ops_autopilot import SecurityEngine

            dry_run = payload.get('dry_run', True)
            engine = SecurityEngine()
            plan = engine.get_containment_plan(dry_run=dry_run)
            return {'action': 'security_containment_plan', **plan}

        elif action == 'security_secrets_scan':
            from core.services.ops_autopilot import SecurityEngine

            days = int(payload.get('days', 7))
            engine = SecurityEngine()
            scan = engine.get_secrets_scan(days=days)
            return {'action': 'security_secrets_scan', **scan}

        elif action == 'compliance_pii_scan':
            from core.services.ops_autopilot import ComplianceEngine

            days = int(payload.get('days', 7))
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

            hours = int(payload.get('hours', 24))
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

            hours = int(payload.get('hours', 24))
            engine = DataIntegrityEngine()
            report = engine.get_quality_report(hours=hours)
            return {'action': 'integrity_quality_report', **report}

        elif action == 'integrity_null_spike_scan':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours', 24))
            engine = DataIntegrityEngine()
            scan = engine.get_null_spike_scan(hours=hours)
            return {'action': 'integrity_null_spike_scan', **scan}

        elif action == 'integrity_duplicate_report':
            from core.services.ops_autopilot import DataIntegrityEngine

            hours = int(payload.get('hours', 24))
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

            days = int(payload.get('days', 7))
            engine = ValueRealizationEngine()
            report = engine.get_value_events_report(days=days)
            return {'action': 'value_events_report', **report}

        elif action == 'value_outcome_rates':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days', 30))
            engine = ValueRealizationEngine()
            rates = engine.get_outcome_rates(days=days)
            return {'action': 'value_outcome_rates', **rates}

        elif action == 'value_usage_gaps':
            from core.services.ops_autopilot import ValueRealizationEngine

            days = int(payload.get('days', 7))
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
        code_defaults = {
            'AudioAgent': 300, 'ImageAgent': 300, 'VideoAgent': 600,
            'ThreeDAgent': 300, 'ImageEditingAgent': 300, 'VideoEditingAgent': 600,
            'TalkingCharacterAgent': 600, 'ResolveAgent': 600,
            'ResearchAgent': 1500, 'SystemIntelligenceAgent': 600,
            'MarketingStrategyAgent': 600, 'CustomerResearchAgent': 1500,
            'CharacterTrainingAgent': 600, 'ContentWriterAgent': 600,
            'CompetitorAnalysisAgent': 600, 'BrandStrategyAgent': 600,
            'ContentStrategyAgent': 600, 'WhaleWatcherAgent': 1500,
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
            from core.models_unified_system import SpiderData
            items = SpiderData.objects.filter(created_at__gte=last_24h).count()
            distinct_spiders = SpiderData.objects.filter(created_at__gte=last_24h).values('spider_name').distinct().count()
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

            # Get agents with recent activity (last 7 days)
            now = timezone.now()
            active_ids = set(
                AgentExecution.objects.filter(
                    created_at__gte=now - timedelta(days=7),
                ).values_list('agent_id', flat=True)
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

            # 'list' includes the top-50 agent preview; 'stats' is aggregates only
            if action == 'list':
                agent_list = list(
                    all_agents.values('name', 'agent_type', 'specialization', 'effectiveness_score')
                    .order_by('-effectiveness_score', 'name')[:50]
                )
                result['agents'] = agent_list

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
        Session 1014: Legislation tool — congressional bill tracking via SpiderData.

        Actions:
        - search: Find bills by keyword
        - status: Status of a specific bill
        - summary: Plain-English explanation of a bill
        - trending: Most recently active bills
        - overview: Dashboard stats
        """
        from core.models_unified_system import SpiderData
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
            """Session 1075: Extract bill dicts from a SpiderData row.

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

        qs = SpiderData.objects.filter(spider_name='legislation').order_by('-created_at')
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
            from core.models_unified_system import SpiderData

            if action == 'list':
                now = timezone.now()
                cutoff_24h = now - timedelta(hours=24)
                cutoff_7d = now - timedelta(days=7)

                spider_stats = (
                    SpiderData.objects
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
                        'total_runs': s['total_items'],  # renamed: each SpiderData row = one run
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
                        'count_note': 'total_runs = SpiderData rows (each contains multiple items)',
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
                    SpiderData.objects
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
                    item = SpiderData.objects.get(id=item_id)
                except SpiderData.DoesNotExist:
                    return {'error': f'SpiderData {item_id} not found'}
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

                qs = SpiderData.objects.all()
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

                hours = int(payload.get('hours', 24))
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
                    from core.models_unified_system import SpiderData
                    from django.utils import timezone
                    from datetime import timedelta
                    recent = SpiderData.objects.filter(created_at__gte=timezone.now() - timedelta(hours=2)).count()
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
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            if action == 'stats':
                from content.models import Document, DocumentEmbedding
                from persistence.models import UnifiedEmbedding
                from core.models_unified_system import SpiderData
                from django.db.models import Count

                doc_count = Document.objects.count()
                doc_with_embeddings = Document.objects.filter(embeddings__isnull=False).distinct().count()
                doc_embedding_count = DocumentEmbedding.objects.count()
                unified_count = UnifiedEmbedding.objects.count()
                spider_with_embedding = SpiderData.objects.filter(embedding__isnull=False).count()

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
                from content.models import Document
                from django.db.models import Count

                query = payload.get('query', '').strip()
                qs = Document.objects.annotate(chunk_count=Count('embeddings')).order_by('-created_at')
                if query:
                    qs = qs.filter(title__icontains=query)
                docs = qs[:limit]
                return {
                    'action': 'documents',
                    'count': len(docs),
                    'documents': [{
                        'id': str(d.id),
                        'title': d.title,
                        'doc_type': getattr(d, 'doc_type', ''),
                        'chunk_count': d.chunk_count,
                        'created_at': d.created_at.isoformat() if hasattr(d, 'created_at') and d.created_at else None,
                    } for d in docs],
                }

            elif action == 'chunks':
                doc_id = payload.get('document_id', '') or payload.get('id', '')
                if not doc_id:
                    return {'error': 'document_id required for chunks action'}
                from content.models import DocumentEmbedding
                chunks = DocumentEmbedding.objects.filter(document_id=doc_id).order_by('chunk_index')[:limit]
                return {
                    'action': 'chunks',
                    'document_id': doc_id,
                    'count': len(chunks),
                    'chunks': [{
                        'chunk_index': c.chunk_index,
                        'chunk_size': c.chunk_size,
                        'text_preview': c.chunk_text[:300],
                        'has_embedding': c.embedding is not None if hasattr(c, 'embedding') else None,
                    } for c in chunks],
                }

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
                return {
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
                }

            return {'error': f'Unknown kb_tool action: {action}. Valid: stats, documents, chunks, search_embeddings'}

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
        originating_session_raw = payload.get('originating_session')
        originating_session: Optional[int] = None
        if originating_session_raw is not None:
            try:
                originating_session = int(originating_session_raw)
            except (TypeError, ValueError):
                return {
                    'error': 'originating_session must be an integer (e.g. 1142)',
                    'query': query,
                }

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

