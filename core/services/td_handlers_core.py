"""
ToolDispatcher CoreHandlersMixin — extracted handler methods.
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

import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


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




_ACTIVE_REPO_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
_ACTIVE_REPO_CACHE_KEY = "pa:active_repo:user:{user_id}"


def _active_repo_cache_key(user_id) -> str:
    return _ACTIVE_REPO_CACHE_KEY.format(user_id=user_id or "anonymous")


class CoreHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    def _handle_active_repo(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Session 1119 carryover #4 (v1 graduation #1) — persist the
        'currently working in repo X' pointer across messages so Claude
        Code's handshake doesn't have to be re-stated every turn.

        Per-user state (one active repo per operator at a time), stored
        in Redis via Django's cache with a 7-day TTL. Auto-clears.

        Actions:
          set    — payload['repo'] = repo_id (or workspace name); resolves
                   to the ProjectWorkspace and caches workspace_id + name
          get    — returns the currently active repo, or null
          clear  — drops the pointer
        """
        from django.core.cache import cache
        from datetime import datetime, timezone as dt_timezone
        from core.models_skin_layer import ProjectWorkspace

        action = (payload or {}).get("action", "get")
        cache_key = _active_repo_cache_key(user_id)

        if action == "get":
            value = cache.get(cache_key)
            return {
                "action": "get",
                "active_repo": value,
                "set": value is not None,
                "cache_key": cache_key,
            }

        if action == "clear":
            had = cache.get(cache_key) is not None
            cache.delete(cache_key)
            return {"action": "clear", "cleared": had, "cache_key": cache_key}

        if action == "set":
            repo = (payload or {}).get("repo")
            if not repo:
                return {
                    "action": "set",
                    "ok": False,
                    "error": "Provide payload.repo (workspace name / repo_id)",
                }
            workspace = (
                ProjectWorkspace.objects.filter(name=repo, user_id=user_id).first()
                or ProjectWorkspace.objects.filter(name=repo).first()
            )
            if not workspace:
                return {
                    "action": "set",
                    "ok": False,
                    "error": f"No ProjectWorkspace named {repo!r} found",
                }
            value = {
                "repo_id": repo,
                "workspace_id": str(workspace.id),
                "name": workspace.name,
                "root_path": workspace.root_path,
                "set_at": datetime.now(dt_timezone.utc).isoformat(timespec="seconds"),
                "ttl_seconds": _ACTIVE_REPO_TTL_SECONDS,
            }
            cache.set(cache_key, value, _ACTIVE_REPO_TTL_SECONDS)
            return {"action": "set", "ok": True, "active_repo": value}

        return {
            "action": action,
            "ok": False,
            "error": f"Unknown action {action!r}. Use set / get / clear.",
        }

    def _handle_fleet_health(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Session 1126 — fleet_health PA tool.

        Read-only rollup of every Dockerized fleet app's /api/health
        endpoint. Calls the same `probe_fleet` function the
        `fleet_health_rollup` management command uses, so the tool and
        the CLI never drift.

        Payload (all optional):
          repo (str)            — single-repo probe (e.g. 'mentorforge')
          timeout_seconds (num) — per-app HTTP timeout, default 3.0
          include_healthy (bool) — default True. When False, only
                                   degraded/unreachable apps are returned
                                   (concise output for status pings).
        """
        from core.management.commands.fleet_health_rollup import (
            probe_fleet, DEFAULT_TIMEOUT_S,
        )

        payload = payload or {}
        repo = payload.get("repo")
        timeout_s = float(payload.get("timeout_seconds") or DEFAULT_TIMEOUT_S)
        include_healthy = payload.get("include_healthy", True)

        result = probe_fleet(repo_filter=repo, timeout_s=timeout_s)
        if not include_healthy:
            result["apps"] = [a for a in result["apps"] if not a["ok"]]
        return result

    def _handle_paid_interest_status(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Session 1138 — paid_interest_status PA tool.

        Returns the Decision 13 demand-gate state for a fleet app's
        paid-interest signal. Delegates to
        `core.services.fleet_paid_interest.evaluate_trigger_state` so the
        tool and any admin surface never drift.

        Payload (all optional):
          app_slug (str)         — defaults to 'signal-studio'
          manual_override (bool) — defaults False
        """
        from core.services.fleet_paid_interest import evaluate_trigger_state

        payload = payload or {}
        app_slug = (payload.get("app_slug") or "signal-studio").strip()
        manual_override = bool(payload.get("manual_override", False))

        state = evaluate_trigger_state(app_slug, manual_override=manual_override)
        return state.to_dict()

    def _handle_signal_studio_judge_stats(
        self, tool_name, payload, user_id, trace_id
    ) -> Dict:
        """Session 1140 — signal_studio_judge_stats PA tool.

        Calls signal-studio's `/api/judge-stats?days=N` endpoint and
        returns the LLM auto-summarizer judge breakdown so Rigby can
        answer 'how is the entity-token clusterer doing?' without
        shelling into docker. signal-studio is auth-less by design so
        no fleet HMAC signing is needed; we just GET over the
        configured base URL.

        URL resolution: `SIGNAL_STUDIO_API_URL` env var (default
        `http://localhost:8007`). On fleet-net set to
        `http://signal_studio_api:8007`.

        Payload (all optional):
          days (int) — lookback window, 1..90, default 7

        Returns the endpoint's JSON unchanged plus an `ok: bool` /
        `error: str` envelope so the LLM gets a uniform shape.
        """
        import os
        import httpx

        payload = payload or {}
        days = payload.get("days")
        try:
            days = int(days) if days is not None else 7
        except (TypeError, ValueError):
            days = 7
        # Clamp to the endpoint's enforced range so a bad value doesn't
        # round-trip a 422 — keeps the PA loop snappy.
        days = max(1, min(days, 90))

        base = os.environ.get(
            "SIGNAL_STUDIO_API_URL", "http://localhost:8007"
        ).rstrip("/")
        url = f"{base}/api/judge-stats?days={days}"

        try:
            with httpx.Client(timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)) as client:
                resp = client.get(url)
        except httpx.HTTPError as e:
            return {
                "ok": False,
                "error": f"signal-studio unreachable at {base}: {e}",
                "days": days,
            }

        if resp.status_code != 200:
            return {
                "ok": False,
                "error": f"signal-studio /api/judge-stats HTTP {resp.status_code}: {resp.text[:200]}",
                "status_code": resp.status_code,
                "days": days,
            }
        try:
            data = resp.json()
        except ValueError as e:
            return {
                "ok": False,
                "error": f"signal-studio response not JSON: {e}",
                "status_code": resp.status_code,
                "days": days,
            }
        return {"ok": True, **data}

    def _handle_dream(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Handle dream browsing and approval actions."""
        from core.models_unified_system import AgentDream
        from django.db.models import Avg, Count, Q

        action = payload.get('action', 'list_top')
        dream_id = payload.get('id')

        if action == 'list_top':
            limit = payload.get('limit', 10)
            dreams = (
                AgentDream.objects
                .filter(composite_score__gte=0.5)
                .select_related('agent')
                .order_by('-composite_score', '-dreamed_at')[:limit]
            )
            return {
                'action': 'list_top',
                'dreams': [
                    {
                        'id': str(d.id),
                        'title': d.title,
                        'content_preview': d.content[:200],
                        'dream_type': d.dream_type,
                        'agent_name': d.agent.name if d.agent else 'Unknown',
                        'composite_score': d.composite_score,
                        'creativity_score': d.creativity_score,
                        'actionability_score': d.actionability_score,
                        'relevance_score': d.relevance_score,
                        'decision_outcome': d.decision_outcome or 'none',
                        'dreamed_at': d.dreamed_at.isoformat(),
                    }
                    for d in dreams
                ],
                'count': len(dreams),
            }

        elif action == 'details':
            if not dream_id:
                raise ValueError("id is required for dream details")
            dream = AgentDream.objects.select_related('agent').get(id=dream_id)
            return {
                'action': 'details',
                'dream': {
                    'id': str(dream.id),
                    'title': dream.title,
                    'content': dream.content,
                    'dream_type': dream.dream_type,
                    'agent_name': dream.agent.name if dream.agent else 'Unknown',
                    'origin': dream.origin,
                    'inspiration_source': dream.inspiration_source,
                    'related_topics': dream.related_topics,
                    'composite_score': dream.composite_score,
                    'creativity_score': dream.creativity_score,
                    'actionability_score': dream.actionability_score,
                    'relevance_score': dream.relevance_score,
                    'vividness_score': dream.vividness_score,
                    'promoted_to_decision': dream.promoted_to_decision,
                    'decision_outcome': dream.decision_outcome or 'none',
                    'user_reaction': dream.user_reaction,
                    'shown_to_user': dream.shown_to_user,
                    'initiative_id': str(dream.initiative_id) if dream.initiative_id else None,  # type: ignore[attr-defined]
                    'dreamed_at': dream.dreamed_at.isoformat(),
                },
            }

        elif action == 'approve':
            if not dream_id:
                raise ValueError("id is required to approve a dream")
            dream = AgentDream.objects.get(id=dream_id)
            dream.decision_outcome = 'approved'
            dream.user_reaction = 'loved'
            dream.user_feedback = payload.get('feedback', 'Approved via PA')
            dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
            # post_save signal fires: promote_to_initiative() + execute_single_dream.delay()
            return {
                'action': 'approve',
                'id': str(dream.id),
                'title': dream.title,
                'success': True,
                'message': 'Dream approved — initiative creation and execution triggered.',
            }

        elif action == 'dismiss':
            if not dream_id:
                raise ValueError("id is required to dismiss a dream")
            dream = AgentDream.objects.get(id=dream_id)
            dream.decision_outcome = 'rejected'
            dream.user_reaction = 'dismissed'
            dream.user_feedback = payload.get('feedback', 'Dismissed via PA')
            dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
            return {
                'action': 'dismiss',
                'id': str(dream.id),
                'title': dream.title,
                'success': True,
            }

        elif action == 'create':
            title = payload.get('title', '').strip()
            content = payload.get('content', '').strip()
            dream_type = payload.get('dream_type', 'user_request')
            if not title:
                raise ValueError("'title' is required for create action")

            # Resolve PA agent as the dreaming agent
            from core.models_unified_system import Agent
            pa_agent = Agent.objects.filter(name__icontains='personal assistant').first()
            if not pa_agent:
                pa_agent = Agent.objects.filter(is_active=True).first()
            if not pa_agent:
                raise ValueError("No active agent found to attribute dream to")

            dream = AgentDream.objects.create(
                agent=pa_agent,
                title=title,
                content=content or title,
                dream_type=dream_type,
                shown_to_user=True,
            )
            return {
                'action': 'create',
                'id': str(dream.id),
                'title': dream.title,
                'dream_type': dream.dream_type,
                'success': True,
            }

        elif action == 'stats':
            total = AgentDream.objects.count()
            by_outcome = dict(
                AgentDream.objects
                .exclude(decision_outcome='')
                .values_list('decision_outcome')
                .annotate(c=Count('id'))
                .values_list('decision_outcome', 'c')
            )
            shown_count = AgentDream.objects.filter(shown_to_user=True).count()
            with_initiative = AgentDream.objects.filter(initiative__isnull=False).count()
            avg_scores = AgentDream.objects.aggregate(
                avg_composite=Avg('composite_score'),
                avg_creativity=Avg('creativity_score'),
                avg_actionability=Avg('actionability_score'),
                avg_relevance=Avg('relevance_score'),
            )
            return {
                'action': 'stats',
                'total_dreams': total,
                'by_outcome': by_outcome,
                'shown_to_user': shown_count,
                'with_initiative': with_initiative,
                'avg_scores': {
                    k: round(v, 3) if v else 0
                    for k, v in avg_scores.items()
                },
            }

        else:
            raise ValueError(f"Unknown dream action: {action}")

    # ── Session 1034: Research-and-Create ──────────────────────────────

    def _handle_research_and_create(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1034: Chain web search → LLM content generation → Deliverable save.

        User says something like "Research Clawbot and create a comparison for a YouTube video".
        This handler:
        1. Runs web search on the research topic
        2. Sends research results + user's creation request to LLM
        3. Saves the generated content as a Deliverable
        4. Returns the content + deliverable link
        """
        from core.tools.web_search import WebSearchTool
        from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest
        from core.models_deliverables import Deliverable
        from django.utils.text import slugify
        import uuid as _uuid

        message = payload.get('query', '')
        research_topic = payload.get('research_topic', message)
        output_type = payload.get('output_type', 'content')
        output_type_label = payload.get('output_type_label', 'Content')

        # Step 1: Web search
        search_tool = WebSearchTool()
        search_result = search_tool.execute(query=research_topic, max_results=8, search_type='text')

        search_data = []
        if search_result.get('success'):
            raw_results = search_result.get('data', {}).get('results', [])
            for r in raw_results[:8]:
                search_data.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('snippet', ''),
                })

        # Build research context for LLM
        research_text = ""
        for i, item in enumerate(search_data, 1):
            research_text += f"\n{i}. **{item['title']}**\n   URL: {item['url']}\n   {item['snippet']}\n"

        if not research_text:
            research_text = "(No search results found. Generate content based on general knowledge.)"

        # Step 2: LLM generation
        # Import platform identity for context
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        platform_identity = UnifiedPAEntrypoint._get_platform_identity()

        system_prompt = f"""You are a professional content creator for the Donkey Betz Unified AI Platform.

{platform_identity}

TASK: The user asked: "{message}"

Based on the research data below, create the requested content. Follow these rules:
- Ground all claims in the research data provided — cite sources with URLs where relevant
- Be comprehensive but well-structured with clear sections
- Use markdown formatting (headers, bullet points, bold text)
- If creating a YouTube script, include: Hook, Introduction, Main Segments, Call to Action, Outro
- If creating a comparison, use a structured format with clear categories
- If creating a report/analysis, include Executive Summary, Key Findings, Recommendations
- Make the content ready to use — not a draft outline, but complete content
- Length: 800-2000 words depending on complexity

RESEARCH DATA:
{research_text}"""

        try:
            registry = get_llm_provider_registry()
            llm_response = registry.complete(
                provider='openai',
                model_id='gpt-4.1-mini',
                request=LLMRequest(
                    prompt=f'Create the {output_type_label} now. Make it complete and ready to use.',
                    system_prompt=system_prompt,
                    max_tokens=4000,
                    temperature=0.7,
                )
            )
            generated_content = llm_response.content if llm_response and llm_response.success and llm_response.content else ''
        except Exception as e:
            logger.error(f"[{trace_id}] Research-and-create LLM failed: {e}")
            generated_content = ''

        if not generated_content:
            return {
                'success': False,
                'error': 'Content generation failed. Research results were gathered but LLM could not generate the content.',
                'search_results': search_data,
            }

        # Step 3: Save as Deliverable
        # Use the extracted research_topic for a clean title
        import re as _rc_re
        clean_topic = research_topic[:100].strip()
        if clean_topic:
            title = f"{output_type_label}: {clean_topic[0].upper() + clean_topic[1:]}"
        else:
            title = f"{output_type_label}: Research Output"

        slug_base = slugify(title)[:250]
        slug = f"{slug_base}-{_uuid.uuid4().hex[:6]}"

        # Determine deliverable_type from output_type
        type_map = {
            'script': 'script',
            'comparison': 'analysis',
            'report': 'report',
            'analysis': 'analysis',
            'outline': 'plan',
            'summary': 'document',
            'brief': 'document',
            'guide': 'document',
            'plan': 'plan',
            'proposal': 'strategy',
        }
        deliverable_type = type_map.get(output_type, 'document')

        try:
            # Session 1065: Resolve user so deliverable shows as "You"
            resolved_user = None
            if user_id:
                from django.contrib.auth import get_user_model
                _User = get_user_model()
                try:
                    resolved_user = _User.objects.get(id=user_id)
                except _User.DoesNotExist:
                    pass

            # Session 1169 — Layer C Phase 1: opt in to typed exception
            # so the gate rejection (previously swallowed by the broad
            # except Exception below as an unhelpful AttributeError on
            # the next str(deliverable.id) line) is logged with structured
            # reason_code instead. Broad except still catches DB / other
            # failures unchanged.
            from core.services.deliverable_factory import (
                create_deliverable,
                DeliverableGatedError,
            )
            deliverable = create_deliverable(
                title=title,
                content=generated_content,
                agent_name=PA_IDENTITY,
                category='PA Research & Create',
                deliverable_type=deliverable_type,
                user=resolved_user,
                trace_id=trace_id,
                content_format='markdown',
                quality_score=0.7,
                confidence_score=0.7,
                tags=['pa-created', 'research-and-create', output_type],
                metadata={
                    'research_query': research_topic,
                    'search_results_count': len(search_data),
                    'output_type': output_type,
                    'source': 'pa_research_and_create',
                    'trace_id': trace_id,
                },
                slug=slug,
                raise_on_gated=True,
            )
            deliverable_id = str(deliverable.id)
            logger.info(f"[{trace_id}] Research-and-create saved deliverable: {deliverable_id}")
        except DeliverableGatedError as gate_err:
            logger.info(
                f"[{trace_id}] Research-and-create gated by quality check: "
                f"reason_code={gate_err.reason_code} reason={gate_err.reason}"
            )
            deliverable_id = None
        except Exception as e:
            logger.error(f"[{trace_id}] Failed to save deliverable: {e}")
            deliverable_id = None

        return {
            'success': True,
            'content': generated_content,
            'title': title,
            'output_type': output_type,
            'output_type_label': output_type_label,
            'deliverable_id': deliverable_id,
            'search_results_count': len(search_data),
            'search_results': search_data[:3],  # Include top 3 for reference
        }


    # ── Session 1048: Task Volume Breakdown ────────────────────────────────

    def _handle_task_breakdown(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1048: Celery task volume breakdown.

        action='summary': aggregated task volume with totals, by_task, by_agent
        action='drilldown': recent executions for a specific task_name
        """
        from datetime import timedelta
        from django.db.models import Count, Q, Avg
        from django.utils import timezone
        from core.models_celery_telemetry import CeleryTaskEvent

        WINDOW_MAP = {
            '15m': 15,
            '60m': 60,
            '2h': 120,
            '6h': 360,
            '24h': 1440,
        }

        action = payload.get('action', 'summary')
        window = payload.get('window', '60m')
        minutes = WINDOW_MAP.get(window, 60)
        cutoff = timezone.now() - timedelta(minutes=minutes)

        if action == 'drilldown':
            task_name = payload.get('task_name', '')
            if not task_name:
                return {'error': 'task_name is required for drilldown'}

            limit = min(int(payload.get('limit', 50)), 200)
            status = payload.get('status', '')
            qs = CeleryTaskEvent.objects.filter(task_name=task_name, started_at__gte=cutoff)
            if status:
                qs = qs.filter(status=status.upper())
            rows = qs.order_by('-started_at')[:limit]

            executions = []
            for r in rows:
                dur_ms = round(r.duration_seconds * 1000) if r.duration_seconds else None
                executions.append({
                    'task_id': r.task_id,
                    'started_at': r.started_at.isoformat() if r.started_at else None,
                    'finished_at': r.finished_at.isoformat() if r.finished_at else None,
                    'duration_ms': dur_ms,
                    'status': r.status,
                    'queue': r.queue or 'default',
                    'worker': r.worker,
                    'error_type': r.error_type or None,
                    'error_message': (r.error_message or '')[:500] or None,
                })

            return {
                'action': 'drilldown',
                'task_name': task_name,
                'window': window,
                'count': len(executions),
                'executions': executions,
            }

        # ── Summary ──
        limit = min(int(payload.get('limit', 25)), 50)
        qs = CeleryTaskEvent.objects.filter(started_at__gte=cutoff)

        totals = qs.aggregate(
            tasks=Count('id'),
            success=Count('id', filter=Q(status='SUCCESS')),
            failure=Count('id', filter=Q(status='FAILURE')),
            started=Count('id', filter=Q(status='STARTED')),
        )

        by_task_qs = (
            qs.values('task_name')
            .annotate(
                count_total=Count('id'),
                count_success=Count('id', filter=Q(status='SUCCESS')),
                count_failure=Count('id', filter=Q(status='FAILURE')),
                avg_duration=Avg('duration_seconds'),
            )
            .order_by('-count_total')[:limit]
        )

        top_task_names = [row['task_name'] for row in by_task_qs]

        # Percentiles
        def _percentile(sorted_list, p):
            if not sorted_list:
                return 0
            k = (len(sorted_list) - 1) * p
            f = int(k)
            return sorted_list[f]

        duration_rows = (
            qs.filter(task_name__in=top_task_names, duration_seconds__isnull=False)
            .values_list('task_name', 'duration_seconds')
        )
        durations_by_task: Dict[str, list] = {}
        for tn, dur in duration_rows:
            durations_by_task.setdefault(tn, []).append(dur)
        for v in durations_by_task.values():
            v.sort()

        # Queue breakdown
        queue_rows = (
            qs.filter(task_name__in=top_task_names)
            .values('task_name', 'queue')
            .annotate(count=Count('id'))
        )
        queues_by_task: Dict[str, list] = {}
        for row in queue_rows:
            queues_by_task.setdefault(row['task_name'], []).append(
                {'queue': row['queue'] or 'default', 'count': row['count']}
            )

        by_task = []
        for row in by_task_qs:
            tn = row['task_name']
            ct = row['count_total']
            cf = row['count_failure']
            durs = durations_by_task.get(tn, [])
            avg_dur = row['avg_duration'] or 0
            by_task.append({
                'task_name': tn,
                'count_total': ct,
                'count_success': row['count_success'],
                'count_failure': cf,
                'failure_rate': round(cf / ct, 3) if ct else 0,
                'avg_duration_ms': round(avg_dur * 1000),
                'p50_ms': round(_percentile(durs, 0.5) * 1000),
                'p95_ms': round(_percentile(durs, 0.95) * 1000),
                'top_queues': sorted(
                    queues_by_task.get(tn, []),
                    key=lambda q: q['count'], reverse=True
                )[:3],
            })

        # By agent
        from core.models import AgentExecution
        by_agent_raw = list(
            AgentExecution.objects.filter(created_at__gte=cutoff)
            .values('agent__name')
            .annotate(
                execution_count=Count('id'),
                count_failure=Count('id', filter=Q(status='failed')),
            )
            .order_by('-execution_count')[:limit]
        )
        by_agent = []
        for row in by_agent_raw:
            ec = row['execution_count']
            cf = row['count_failure']
            by_agent.append({
                'agent_name': row['agent__name'],
                'execution_count': ec,
                'count_failure': cf,
                'failure_rate': round(cf / ec, 3) if ec else 0,
            })

        return {
            'action': 'summary',
            'window': window,
            'generated_at': timezone.now().isoformat(),
            'totals': totals,
            'by_task': by_task,
            'by_agent': by_agent,
        }


    # ── Session 1071: Platform Awareness ─────────────────────────────────────

    def _handle_platform_awareness(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Platform awareness: manifest, routes, capabilities, deploy verification."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from core.views_app_manifest import get_manifest_data

        action = payload.get('action', 'get_manifest')

        # Resolve user object for RBAC filtering
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        if action == 'verify_deploy':
            # Admin-only deploy verification
            if user and (user.is_superuser or user.is_staff):
                from core.views_deploy_verify import run_verification
                import os
                base_url = os.getenv(
                    'DEPLOY_BASE_URL',
                    'https://donkey-betz-platform-production.up.railway.app'
                )
                from rest_framework.authtoken.models import Token
                token_obj = Token.objects.filter(user=user).first()
                token = token_obj.key if token_obj else None
                return run_verification(base_url, token=token)
            return {'error': 'Admin access required for deploy verification'}

        if not user:
            # If no user, return unfiltered manifest
            from core.views_app_manifest import _load_manifest
            manifest = _load_manifest()
        else:
            manifest = get_manifest_data(user)

        routes = manifest.get('routes', [])

        if action == 'get_manifest':
            return manifest

        if action == 'list_routes':
            category = payload.get('category')
            auth_required = payload.get('auth_required')
            filtered = routes
            if category:
                filtered = [r for r in filtered if r.get('category') == category]
            if auth_required is not None:
                filtered = [r for r in filtered if r.get('authRequired') == auth_required]
            return {
                'count': len(filtered),
                'routes': filtered,
            }

        if action == 'check_route':
            path = payload.get('path', '')
            match = next((r for r in routes if r.get('path') == path), None)
            if match:
                return {'exists': True, 'route': match}
            return {'exists': False, 'path': path}

        if action == 'system_overview':
            categories = {}
            for r in routes:
                cat = r.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
            studios = manifest.get('studios', {})
            capabilities = manifest.get('capabilities', {})
            api_deps = manifest.get('api_dependencies', {})
            return {
                'route_count': len(routes),
                'routes_by_category': categories,
                'studio_count': sum(1 for s in studios.values() if isinstance(s, dict) and s.get('enabled')),
                'studios': list(studios.keys()),
                'capability_count': sum(1 for v in capabilities.values() if v),
                'capabilities': capabilities,
                'build_sha': manifest.get('build_sha', 'unknown'),
                'api_dependency_routes': len(api_deps),
                'api_dependency_total_endpoints': sum(len(v) for v in api_deps.values() if isinstance(v, list)),
            }

        if action == 'list_api_dependencies':
            api_deps = manifest.get('api_dependencies', {})
            path = payload.get('path')
            writes_only = payload.get('writes_only', False)
            if path:
                deps = api_deps.get(path, [])
                if not isinstance(deps, list):
                    deps = []
                if writes_only:
                    deps = [d for d in deps if isinstance(d, dict) and d.get('writes')]
                return {'route': path, 'endpoint_count': len(deps), 'endpoints': deps}
            else:
                result = {}
                for rp, rp_deps in api_deps.items():
                    if not isinstance(rp_deps, list):
                        continue
                    filtered = rp_deps
                    if writes_only:
                        filtered = [d for d in rp_deps if isinstance(d, dict) and d.get('writes')]
                    result[rp] = {'endpoint_count': len(filtered), 'endpoints': filtered}
                return {'route_count': len(result), 'routes': result}

        if action == 'tool_registry':
            from core.views_app_manifest import _summarize_tool_schemas
            tools = _summarize_tool_schemas()
            return {'action': 'tool_registry', 'tools': tools, 'count': len(tools)}

        return {'error': f'Unknown action: {action}'}

    # ── Session 1071: Studio Tool ────────────────────────────────────────────

    def _handle_studio(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Unified creative studio: generate images, videos, audio, check jobs."""
        action = payload.get('action', 'list_jobs')

        if action == 'generate_image':
            # Session 1088: Dispatch to Celery async to avoid PA/Railway proxy timeout
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            # Prefix with "Generate image:" so _is_media_task_blocked() recognizes it
            task_text = f'Generate image: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'design', 'draw', 'render', 'produc')) else raw_prompt
            context = {}
            if payload.get('style'):
                context['style'] = payload['style']
            if payload.get('model'):
                context['model'] = payload['model']
            if payload.get('width'):
                context['width'] = payload['width']
            if payload.get('height'):
                context['height'] = payload['height']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['ImageAgent', task_text, context], queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'ImageAgent',
                'message': f'Image generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'generate_video':
            # Session 1077: Dispatch to Celery async to avoid PA tool timeout
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            task_text = f'Generate video: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'produc', 'render')) else raw_prompt
            context = {}
            if payload.get('style'):
                context['style'] = payload['style']
            if payload.get('duration'):
                context['duration'] = payload['duration']
            if payload.get('ratio'):
                context['ratio'] = payload['ratio']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['VideoAgent', task_text, context], queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'VideoAgent',
                'message': f'Video generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'generate_talking_video':
            # Dispatch to Celery async — pipeline is long-running (TTS + video + lip sync)
            from core.tasks import execute_agent_task
            raw_script = payload.get('script') or payload.get('prompt', '')
            task_text = f'Generate talking character video: {raw_script}'
            context = {
                'image_url': payload.get('image_url', ''),
                'script': raw_script,
                'voice': payload.get('voice', 'Rachel'),
                'duration': payload.get('duration', 10),
                'lipsync_model': payload.get('lipsync_model', 'auto'),
                'mode': payload.get('mode', 'multi_clip'),
                'sync_mode': payload.get('sync_mode', 'cut_off'),
                'color_grade': payload.get('color_grade'),
            }
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['TalkingCharacterAgent', task_text, context], queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'TalkingCharacterAgent',
                'message': f'Talking character video dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'create_talking_video':
            # Pipeline: generate character image → talking video in one task
            from core.tasks import create_talking_video_task
            image_prompt = payload.get('prompt', '')
            script = payload.get('script', '')
            if not image_prompt:
                return {'error': 'prompt is required (image description for the character)'}
            if not script:
                return {'error': 'script is required (what the character should say)'}
            context = {
                'voice': payload.get('voice', 'Rachel'),
                'duration': payload.get('duration', 10),
                'lipsync_model': payload.get('lipsync_model', 'auto'),
                'mode': payload.get('mode', 'multi_clip'),
                'sync_mode': payload.get('sync_mode', 'cut_off'),
                'color_grade': payload.get('color_grade'),
            }
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = create_talking_video_task.apply_async(
                args=[image_prompt, script, context], queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'ImageAgent → TalkingCharacterAgent',
                'message': (
                    f'Talking video pipeline dispatched (task {celery_task.id}). '
                    f'Will generate character image then create talking video. '
                    f'Use job_status to check progress.'
                ),
            }

        if action == 'generate_audio':
            # Session 1088: Dispatch to Celery async (matches video/image pattern)
            from core.tasks import execute_agent_task
            raw_prompt = payload.get('prompt', '')
            task_text = f'Generate audio: {raw_prompt}' if not raw_prompt.lower().startswith(('generat', 'creat', 'make', 'produc', 'render')) else raw_prompt
            context = {}
            if payload.get('voice'):
                context['voice'] = payload['voice']
            if user_id:
                context['user_id'] = str(user_id)
            celery_task = execute_agent_task.apply_async(
                args=['AudioAgent', task_text, context], queue='long_running',
            )
            return {
                'task_id': str(celery_task.id),
                'mode': 'async',
                'agent': 'AudioAgent',
                'message': f'Audio generation dispatched (task {celery_task.id}). Use job_status to check progress.',
            }

        if action == 'job_status':
            job_id = payload.get('job_id')
            if not job_id:
                return {'error': 'job_id is required for job_status'}

            # 1. Check CeleryTaskEvent (completed tasks with telemetry)
            try:
                from core.models_celery_telemetry import CeleryTaskEvent
                event = CeleryTaskEvent.objects.filter(task_id=job_id).first()
                if event:
                    result = {
                        'job_id': job_id,
                        'status': event.status,
                        'started_at': event.started_at.isoformat() if event.started_at else None,
                        'finished_at': event.finished_at.isoformat() if event.finished_at else None,
                        'duration_ms': round(event.duration_seconds * 1000) if event.duration_seconds else None,
                    }
                    # Enrich with AgentExecution output if available
                    result.update(self._get_agent_execution_output(job_id))
                    return result
            except Exception as _e:
                logger.warning(
                    "td_core._handle_studio: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

            # 2. Check Celery AsyncResult (in-flight or recently completed)
            try:
                from celery.result import AsyncResult
                async_result = AsyncResult(job_id)
                state = async_result.state  # PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED
                result = {
                    'job_id': job_id,
                    'status': state.lower(),
                }
                if state == 'SUCCESS':
                    task_return = async_result.result or {}
                    if isinstance(task_return, dict):
                        result['status'] = 'completed'
                        result['success'] = task_return.get('success', True)
                        result['agent'] = task_return.get('agent_name', '')
                        result['execution_time_ms'] = task_return.get('execution_time_ms')
                        # Enrich with full content/media from AgentExecution
                        exec_id = task_return.get('execution_id')
                        if exec_id:
                            result.update(self._get_agent_execution_output(job_id, exec_id))
                        # Fallback: use content from task return if enrichment found nothing
                        if not result.get('content'):
                            result['content'] = task_return.get('content', '')
                elif state == 'FAILURE':
                    result['status'] = 'failed'
                    result['error'] = str(async_result.result)[:500] if async_result.result else 'Unknown error'
                elif state == 'STARTED':
                    result['status'] = 'running'
                elif state == 'PENDING':
                    result['status'] = 'queued'
                return result
            except Exception as e:
                logger.debug(f"AsyncResult check failed for {job_id}: {e}")

            return {'job_id': job_id, 'status': 'unknown'}

        if action == 'list_jobs':
            limit = min(int(payload.get('limit', 10)), 50)
            jobs = []
            try:
                from content.models import ImageHistory
                for img in ImageHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(img.id),
                        'type': 'image',
                        'prompt': getattr(img, 'prompt', '')[:100] if getattr(img, 'prompt', '') else '',
                        'created_at': img.created_at.isoformat() if hasattr(img, 'created_at') and img.created_at else None,
                    })
            except Exception as _e:
                logger.warning(
                    "td_core._handle_studio: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
            try:
                from content.models import VideoHistory
                for vid in VideoHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(vid.id),
                        'type': 'video',
                        'prompt': getattr(vid, 'prompt', '')[:100] if getattr(vid, 'prompt', '') else '',
                        'created_at': vid.created_at.isoformat() if hasattr(vid, 'created_at') and vid.created_at else None,
                    })
            except Exception as _e:
                logger.warning(
                    "td_core._handle_studio: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
            try:
                from content.models import AudioHistory
                for aud in AudioHistory.objects.order_by('-created_at')[:limit]:
                    jobs.append({
                        'id': str(aud.id),
                        'type': 'audio',
                        'prompt': getattr(aud, 'text', '')[:100] if getattr(aud, 'text', '') else '',
                        'created_at': aud.created_at.isoformat() if hasattr(aud, 'created_at') and aud.created_at else None,
                    })
            except Exception as _e:
                logger.warning(
                    "td_core._handle_studio: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
            # Sort by created_at descending
            jobs.sort(key=lambda j: j.get('created_at') or '', reverse=True)
            return {
                'count': len(jobs[:limit]),
                'jobs': jobs[:limit],
            }

        return {'error': f'Unknown studio action: {action}'}

    def _handle_persona(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Session 1088: Browse and invoke 139 DB-only persona agents."""
        from core.models_unified_system import Agent as AgentModel
        from core.agent_router import AgentRouter

        action = payload.get('action', 'list')

        if action == 'list':
            category = payload.get('category')
            qs = AgentModel.objects.filter(is_active=True)

            # Exclude AGENT_MAP agents so we only show DB-only personas
            map_names = set(AgentRouter.AGENT_MAP.keys())
            qs = qs.exclude(name__in=map_names)

            if category:
                qs = qs.filter(agent_type=category)

            personas = list(
                qs.order_by('agent_type', 'name')
                .values('name', 'agent_type', 'specialization', 'description',
                        'effectiveness_score', 'total_executions')[:50]
            )

            # Truncate descriptions for LLM context
            for p in personas:
                if p.get('description') and len(p['description']) > 150:
                    p['description'] = p['description'][:147] + '...'

            # Category summary
            from collections import Counter
            all_types = list(
                AgentModel.objects.filter(is_active=True)
                .exclude(name__in=map_names)
                .values_list('agent_type', flat=True)
            )
            categories = dict(Counter(all_types).most_common())

            return {
                'action': 'list',
                'filter': category,
                'count': len(personas),
                'personas': personas,
                'categories': categories,
            }

        if action == 'invoke':
            persona_name = payload.get('persona_name')
            task = payload.get('task')
            if not persona_name:
                return {'error': 'persona_name is required for invoke action'}
            if not task:
                return {'error': 'task is required for invoke action'}

            # Verify persona exists and is active
            agent_obj = AgentModel.objects.filter(
                name=persona_name, is_active=True
            ).first()
            if not agent_obj:
                return {'error': f'Persona "{persona_name}" not found or inactive'}

            # Route through AgentRouter (DynamicPersonaAgent fallback)
            router = AgentRouter()
            result = router.route(persona_name, task, context=payload.get('context', {}))

            response = {
                'action': 'invoke',
                'persona': persona_name,
                'success': result.success if result else False,
                'output': result.message if result else 'Persona execution failed',
            }
            if result and result.data:
                response['data'] = result.data
            return response

        return {'error': f'Unknown persona action: {action}'}

    # ── Session 1069: Platform Config ─────────────────────────────────────────

    def _handle_platform_config(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1069: Platform config introspection — runtime settings, LLM providers,
        env vars (secrets masked), and feature flags.
        """
        import os
        from django.conf import settings as django_settings

        action = payload.get('action', 'overview')

        SECRET_PATTERNS = (
            'KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'CREDENTIAL',
            'DSN', 'DATABASE_URL', 'REDIS_URL', 'BROKER_URL',
        )

        def _mask(key, value):
            """Mask secret values, show first 8 chars + ..."""
            if not value:
                return value
            val = str(value)
            for pat in SECRET_PATTERNS:
                if pat in key.upper():
                    return val[:8] + '...' if len(val) > 8 else '***'
            return val

        if action == 'overview':
            return {
                'action': 'overview',
                'service_context': os.environ.get('RAILWAY_SERVICE_NAME', 'local'),
                'platform': getattr(django_settings, 'PLATFORM_NAME', 'unknown'),
                'debug': django_settings.DEBUG,
                'allowed_hosts': getattr(django_settings, 'ALLOWED_HOSTS', []),
                'default_llm_provider': getattr(django_settings, 'LLM_DEFAULT_PROVIDER', 'unknown'),
                'database_engine': django_settings.DATABASES.get('default', {}).get('ENGINE', 'unknown'),
                'database_name': django_settings.DATABASES.get('default', {}).get('NAME', 'unknown'),
                'redis_url': _mask('REDIS_URL', os.environ.get('REDIS_URL', 'not set')),
                'celery_broker': _mask('BROKER_URL', getattr(django_settings, 'CELERY_BROKER_URL', 'not set')),
                'cors_allow_all': getattr(django_settings, 'CORS_ALLOW_ALL_ORIGINS', False),
                'csrf_trusted_origins': getattr(django_settings, 'CSRF_TRUSTED_ORIGINS', []),
                'frontend_url': getattr(django_settings, 'FRONTEND_URL', 'not set'),
                'backend_url': getattr(django_settings, 'BACKEND_URL', 'not set'),
                'railway_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
                'railway_service': os.environ.get('RAILWAY_SERVICE_NAME', 'local'),
            }

        elif action == 'web_config':
            # Fetch config from the web service via its internal API
            # so the PA can compare web vs celery-pa environments
            import urllib.request
            import json as _json
            web_url = os.environ.get(
                'WEB_SERVICE_URL',
                'https://donkey-betz-platform-production.up.railway.app'
            )
            try:
                req = urllib.request.Request(
                    f'{web_url}/api/v1/health/',
                    headers={'Accept': 'application/json'},
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    health_data = _json.loads(resp.read())
            except Exception as e:
                health_data = {'error': str(e)}

            try:
                req2 = urllib.request.Request(
                    f'{web_url}/api/internal/config-snapshot/',
                    headers={'Accept': 'application/json'},
                )
                with urllib.request.urlopen(req2, timeout=5) as resp:
                    web_config = _json.loads(resp.read())
            except Exception as e:
                web_config = {'error': str(e), 'note': 'config-snapshot endpoint may not be deployed yet'}

            return {
                'action': 'web_config',
                'service_context': 'web (remote)',
                'web_service_url': web_url,
                'health': health_data,
                'config': web_config,
            }

        elif action == 'llm_providers':
            providers = {}
            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY', '')
            providers['openai'] = {
                'configured': bool(openai_key),
                'key_prefix': openai_key[:8] + '...' if openai_key else 'not set',
            }
            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY', '')
            providers['anthropic'] = {
                'configured': bool(anthropic_key),
                'key_prefix': anthropic_key[:8] + '...' if anthropic_key else 'not set',
            }
            # Together AI
            together_key = os.environ.get('TOGETHER_AI_API_KEY', '') or os.environ.get('TOGETHER_API_KEY', '')
            providers['together_ai'] = {
                'configured': bool(together_key),
                'key_prefix': together_key[:8] + '...' if together_key else 'not set',
            }
            # DeepSeek
            deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
            providers['deepseek'] = {
                'configured': bool(deepseek_key),
                'key_prefix': deepseek_key[:8] + '...' if deepseek_key else 'not set',
            }
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY', os.environ.get('GOOGLE_API_KEY', ''))
            providers['gemini'] = {
                'configured': bool(gemini_key),
                'key_prefix': gemini_key[:8] + '...' if gemini_key else 'not set',
            }
            # Ollama
            ollama_url = os.environ.get('OLLAMA_BASE_URL', getattr(django_settings, 'OLLAMA_BASE_URL', ''))
            providers['ollama'] = {
                'configured': bool(ollama_url),
                'base_url': ollama_url or 'not set',
            }
            return {
                'action': 'llm_providers',
                'default_provider': getattr(django_settings, 'LLM_DEFAULT_PROVIDER', 'unknown'),
                'providers': providers,
            }

        elif action == 'env_vars':
            # Show all env vars with secrets masked
            env_snapshot = {}
            for key in sorted(os.environ.keys()):
                # Skip overly noisy system vars
                if key.startswith(('__', 'npm_', 'LESS_', 'LS_')):
                    continue
                env_snapshot[key] = _mask(key, os.environ[key])
            return {
                'action': 'env_vars',
                'count': len(env_snapshot),
                'variables': env_snapshot,
            }

        elif action == 'feature_flags':
            flags = {}
            flag_attrs = [
                'LUNGS_ENFORCE_HARD_LIMIT',
                'CELERY_TASK_EVENT_RETENTION_DAYS',
                'LLM_CALL_LOG_RETENTION_DAYS',
                'BODY_THROTTLE_MAX_DELAY_SECONDS',
                'CONTENT_AUTO_PUBLISH',
                'SPIDER_ENABLED',
                'DREAM_ENABLED',
            ]
            for attr in flag_attrs:
                flags[attr] = getattr(django_settings, attr, 'not set')
            return {
                'action': 'feature_flags',
                'flags': flags,
            }

        return {'error': f'Unknown platform_config action: {action}'}

    # ── Session 1069: DB Health ───────────────────────────────────────────────

    def _handle_db_health(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1069: Database health — connection status, migration state,
        table row counts, and pgvector extension status.
        """
        from django.db import connection

        action = payload.get('action', 'overview')

        if action == 'overview':
            result = {'action': 'overview'}

            # Connection check
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    row = cursor.fetchone()
                    result['postgres_version'] = row[0] if row else 'unknown'
                    result['connected'] = True
            except Exception as e:
                result['connected'] = False
                result['connection_error'] = str(e)
                return result

            # Database name and size
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT current_database(), pg_size_pretty(pg_database_size(current_database()))")
                    row = cursor.fetchone()
                    if row:
                        result['database_name'] = row[0]
                        result['database_size'] = row[1]
            except Exception as e:
                result['db_size_error'] = str(e)

            # Migration summary
            try:
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command('showmigrations', '--plan', stdout=out)
                lines = out.getvalue().strip().split('\n')
                applied = sum(1 for l in lines if l.strip().startswith('[X]'))
                unapplied = sum(1 for l in lines if l.strip().startswith('[ ]'))
                result['migrations'] = {
                    'applied': applied,
                    'unapplied': unapplied,
                    'status': 'up_to_date' if unapplied == 0 else f'{unapplied}_pending',
                }
                if unapplied > 0:
                    result['migrations']['pending'] = [
                        l.strip()[4:] for l in lines if l.strip().startswith('[ ]')
                    ][:20]
            except Exception as e:
                result['migrations'] = {'error': str(e)}

            # pgvector check
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                    row = cursor.fetchone()
                    result['pgvector'] = {
                        'installed': bool(row),
                        'version': row[0] if row else None,
                    }
            except Exception as e:
                result['pgvector'] = {'error': str(e)}

            return result

        elif action == 'migrations':
            try:
                from django.core.management import call_command
                from io import StringIO
                out = StringIO()
                call_command('showmigrations', '--plan', stdout=out)
                lines = out.getvalue().strip().split('\n')
                unapplied = [l.strip()[4:] for l in lines if l.strip().startswith('[ ]')]
                applied_count = sum(1 for l in lines if l.strip().startswith('[X]'))
                return {
                    'action': 'migrations',
                    'applied_count': applied_count,
                    'unapplied_count': len(unapplied),
                    'unapplied': unapplied[:50],
                    'status': 'up_to_date' if not unapplied else 'pending',
                }
            except Exception as e:
                return {'action': 'migrations', 'error': str(e)}

        elif action == 'tables':
            try:
                key_tables = [
                    'core_chatconversation', 'core_agentexecution',
                    'core_toolcallrecord', 'core_initiative',
                    'core_spiderdata', 'core_deliverable',
                    'core_failuresignature', 'core_failuredetection',
                    'core_celerytaskevent', 'core_llmcalllog',
                    'core_selfblog', 'core_heartbeat',
                    'core_signalcluster', 'core_agentdream',
                    'core_humanattentionitem', 'core_mlprediction',
                    'core_imagehistory', 'core_videohistory',
                    'core_audiohistory',
                ]
                table_counts = {}
                with connection.cursor() as cursor:
                    for table in key_tables:
                        try:
                            cursor.execute(
                                "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                                [table]
                            )
                            row = cursor.fetchone()
                            table_counts[table] = row[0] if row else 0
                        except Exception:
                            table_counts[table] = 'error'
                return {
                    'action': 'tables',
                    'table_count': len(table_counts),
                    'row_counts': table_counts,
                    'note': 'Row counts are estimates from pg_class.reltuples (fast, updated by ANALYZE)',
                }
            except Exception as e:
                return {'action': 'tables', 'error': str(e)}

        elif action == 'verify_table':
            table_name = payload.get('table_name', '')
            if not table_name:
                return {'error': 'table_name is required'}
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = 'public' AND table_name = %s",
                        [table_name]
                    )
                    exists = cursor.fetchone() is not None
                    result = {'action': 'verify_table', 'table_name': table_name, 'exists': exists}
                    if exists:
                        cursor.execute(
                            "SELECT reltuples::bigint FROM pg_class WHERE relname = %s",
                            [table_name]
                        )
                        row = cursor.fetchone()
                        result['row_count'] = row[0] if row else 0
                        cursor.execute(
                            "SELECT column_name, data_type FROM information_schema.columns "
                            "WHERE table_schema = 'public' AND table_name = %s "
                            "ORDER BY ordinal_position",
                            [table_name]
                        )
                        result['columns'] = [
                            {'name': r[0], 'type': r[1]} for r in cursor.fetchall()
                        ]
                    return result
            except Exception as e:
                return {'action': 'verify_table', 'error': str(e)}

        elif action == 'search_tables':
            prefix = payload.get('prefix', 'core_')
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT c.relname, c.reltuples::bigint "
                        "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                        "WHERE n.nspname = 'public' AND c.relkind = 'r' "
                        "AND c.relname LIKE %s ORDER BY c.relname",
                        [prefix + '%']
                    )
                    tables = [{'name': r[0], 'estimated_rows': r[1]} for r in cursor.fetchall()]
                    return {'action': 'search_tables', 'prefix': prefix, 'tables': tables, 'count': len(tables)}
            except Exception as e:
                return {'action': 'search_tables', 'error': str(e)}

        elif action == 'pgvector':
            result = {'action': 'pgvector'}
            try:
                with connection.cursor() as cursor:
                    # Extension status
                    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
                    row = cursor.fetchone()
                    result['installed'] = bool(row)
                    result['version'] = row[0] if row else None

                    if row:
                        # Count vector columns
                        cursor.execute("""
                            SELECT table_name, column_name
                            FROM information_schema.columns
                            WHERE udt_name = 'vector'
                            ORDER BY table_name
                        """)
                        vector_cols = cursor.fetchall()
                        result['vector_columns'] = [
                            {'table': r[0], 'column': r[1]} for r in vector_cols
                        ]
                        result['vector_column_count'] = len(vector_cols)

                        # Count rows with embeddings in key table
                        try:
                            cursor.execute("""
                                SELECT reltuples::bigint FROM pg_class
                                WHERE relname = 'core_spiderdata'
                            """)
                            row = cursor.fetchone()
                            result['spider_data_rows'] = row[0] if row else 0
                        except Exception as _e:
                            logger.warning(
                                "td_core._handle_db_health: swallowed (%s: %s) — degraded",
                                type(_e).__name__, _e,
                            )

                        # Vector indexes
                        cursor.execute("""
                            SELECT indexname, tablename
                            FROM pg_indexes
                            WHERE indexdef LIKE '%%vector%%' OR indexdef LIKE '%%ivfflat%%' OR indexdef LIKE '%%hnsw%%'
                        """)
                        indexes = cursor.fetchall()
                        result['vector_indexes'] = [
                            {'index': r[0], 'table': r[1]} for r in indexes
                        ]
            except Exception as e:
                result['error'] = str(e)
            return result

        elif action == 'learning_stats':
            result = {'action': 'learning_stats'}
            try:
                with connection.cursor() as cursor:
                    # Readback event totals (Session 1078: added prompt_injection metrics)
                    cursor.execute(
                        "SELECT COUNT(*), "
                        "COUNT(*) FILTER (WHERE learning_consulted = true), "
                        "COUNT(*) FILTER (WHERE learning_used = true), "
                        "MIN(created_at), MAX(created_at), "
                        "COUNT(*) FILTER (WHERE prompt_injection_applied = true) "
                        "FROM core_learningreadbackevent"
                    )
                    row = cursor.fetchone()
                    result['readback_events'] = {
                        'total': row[0],
                        'consulted_true': row[1],
                        'used_true': row[2],
                        'oldest': str(row[3]) if row[3] else None,
                        'newest': str(row[4]) if row[4] else None,
                        'prompt_injection_true': row[5],
                    }
                    if row[0] > 0:
                        result['readback_events']['consultation_rate'] = round(row[1] / row[0] * 100, 1)
                        result['readback_events']['usage_rate'] = round(row[2] / row[0] * 100, 1)

                    # Last 24h breakdown
                    cursor.execute(
                        "SELECT COUNT(*), "
                        "COUNT(*) FILTER (WHERE learning_consulted = true), "
                        "COUNT(*) FILTER (WHERE learning_used = true), "
                        "COUNT(*) FILTER (WHERE prompt_injection_applied = true) "
                        "FROM core_learningreadbackevent "
                        "WHERE created_at > NOW() - INTERVAL '24 hours'"
                    )
                    row = cursor.fetchone()
                    result['last_24h'] = {
                        'total': row[0],
                        'consulted_true': row[1],
                        'used_true': row[2],
                        'prompt_injection_true': row[3],
                    }

                    # UserAgentLearning record counts (the source data)
                    cursor.execute(
                        "SELECT COUNT(*), "
                        "COUNT(DISTINCT learning_domain), "
                        "COUNT(DISTINCT agent_name) "
                        "FROM core_useragentlearning "
                        "WHERE is_active = true"
                    )
                    row = cursor.fetchone()
                    result['learning_records'] = {
                        'active_total': row[0],
                        'distinct_domains': row[1],
                        'distinct_agents': row[2],
                    }

                    # Top 5 routed_to agents in readback events
                    cursor.execute(
                        "SELECT routed_to, COUNT(*) "
                        "FROM core_learningreadbackevent "
                        "WHERE routed_to IS NOT NULL "
                        "GROUP BY routed_to ORDER BY COUNT(*) DESC LIMIT 5"
                    )
                    result['top_routed_agents'] = [
                        {'agent': r[0], 'count': r[1]} for r in cursor.fetchall()
                    ]

                    # used_via breakdown (routing_override vs prompt_injection)
                    cursor.execute(
                        "SELECT elem, COUNT(*) "
                        "FROM core_learningreadbackevent, "
                        "LATERAL jsonb_array_elements_text(used_via) AS elem "
                        "GROUP BY elem ORDER BY COUNT(*) DESC"
                    )
                    result['used_via_breakdown'] = {
                        r[0]: r[1] for r in cursor.fetchall()
                    }

                    # Feature flags
                    from django.conf import settings
                    result['flags'] = {
                        'LEARNING_ROUTING_ENABLED': getattr(settings, 'LEARNING_ROUTING_ENABLED', False),
                        'LEARNING_PROMPT_INJECTION_ENABLED': getattr(settings, 'LEARNING_PROMPT_INJECTION_ENABLED', False),
                    }

            except Exception as e:
                result['error'] = str(e)
            return result

        return {'error': f'Unknown db_health action: {action}'}

    def _handle_http_smoke_test(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Run HTTP smoke tests against cockpit API endpoints."""
        from core.tools.http_smoke_test import run_smoke_test
        from core.tools.ops_run_tracker import OpsRunTracker

        suite = payload.get('suite', 'default')
        with OpsRunTracker(f'Smoke: {suite}', 'smoke_test', 'pa_tool') as tracker:
            result = tracker.step(suite, lambda: run_smoke_test(payload))
            tracker.set_summary(result if isinstance(result, dict) else {})

        if isinstance(result, dict):
            result['ops_run_id'] = tracker.ops_run_id
        return result

    def _handle_learning(self, tool_name, payload, user_id, trace_id):
        """Manage PA tool-usage insights (learning loop)."""
        from core.models_tool_calls import PAToolInsight

        action = payload.get('action', 'stats')
        limit = min(payload.get('limit', 10), 50)
        filter_tool = payload.get('tool_name')

        _fields = (
            'id', 'tool_name', 'insight_type', 'prompt_snippet',
            'evidence_count', 'confidence', 'expires_at', 'created_at',
        )

        if action == 'list_candidates':
            qs = PAToolInsight.objects.filter(safety_class='candidate')
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-evidence_count', '-confidence')[:limit].values(*_fields))
            return {'candidates': items, 'count': len(items)}

        elif action == 'list_approved':
            qs = PAToolInsight.objects.filter(safety_class='approved')
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-confidence', '-evidence_count')[:limit].values(*_fields))
            return {'approved': items, 'count': len(items)}

        elif action == 'list_expired':
            from django.utils import timezone as _tz
            now = _tz.now()
            qs = PAToolInsight.objects.filter(expires_at__isnull=False, expires_at__lte=now)
            if filter_tool:
                qs = qs.filter(tool_name=filter_tool)
            items = list(qs.order_by('-expires_at')[:limit].values(*_fields, 'safety_class'))
            return {'expired': items, 'count': len(items)}

        elif action == 'approve':
            insight_id = payload.get('id')
            if not insight_id:
                return {'error': 'id is required for approve action'}
            updated = PAToolInsight.objects.filter(
                id=insight_id, safety_class='candidate'
            ).update(safety_class='approved')
            return {'approved': bool(updated), 'id': insight_id}

        elif action == 'reject':
            insight_id = payload.get('id')
            if not insight_id:
                return {'error': 'id is required for reject action'}
            updated = PAToolInsight.objects.filter(
                id=insight_id, safety_class='candidate'
            ).update(safety_class='rejected')
            return {'rejected': bool(updated), 'id': insight_id}

        elif action == 'stats':
            from django.db.models import Count
            stats = list(
                PAToolInsight.objects.values('safety_class', 'insight_type')
                .annotate(count=Count('id'))
                .order_by('safety_class', 'insight_type')
            )
            totals = {
                'candidate': 0, 'approved': 0, 'rejected': 0,
            }
            for s in stats:
                totals[s['safety_class']] = totals.get(s['safety_class'], 0) + s['count']
            return {'stats': stats, 'totals': totals}

        return {'error': f'Unknown action: {action}'}

    def _handle_conversation(self, tool_name, payload, user_id, trace_id):
        """Handle conversation memory tool — cross-thread PA recall."""
        from core.models import ChatConversation, ConversationMemory
        from django.db.models import Q
        from datetime import timedelta
        from django.utils import timezone

        action = payload.get('action', 'search')
        limit = min(payload.get('limit', 10), 50)

        if action == 'get':
            cid = payload.get('conversation_id')
            if not cid:
                return {'error': 'conversation_id required for get action'}

            # Session 1086: Support pagination via offset so the PA can
            # reach later turns in long conversations.
            offset = max(payload.get('offset', 0), 0)
            page_size = min(limit, 30)  # max 30 turns per page
            # Content cap per turn — 1000 chars gives more context than 500
            content_cap = 1000

            total = ChatConversation.objects.filter(conversation_id=cid).count()
            if total == 0:
                return {'action': 'get', 'conversation_id': cid, 'turns': [], 'message': 'No conversation found'}

            turns = list(
                ChatConversation.objects.filter(conversation_id=cid)
                .order_by('created_at')
                .values('user_message', 'assistant_response', 'created_at', 'source', 'session_title')
                [offset:offset + page_size]
            )

            return {
                'action': 'get',
                'conversation_id': cid,
                'session_title': turns[0].get('session_title', '') if turns else '',
                'turn_count': total,
                'offset': offset,
                'page_size': page_size,
                'has_more': (offset + page_size) < total,
                'turns': [
                    {
                        'role_user': t['user_message'][:content_cap],
                        'role_assistant': t['assistant_response'][:content_cap],
                        'timestamp': t['created_at'].isoformat() if t['created_at'] else None,
                    }
                    for t in turns
                ],
            }

        elif action == 'search':
            query = payload.get('query', '')
            days_back = payload.get('days_back')
            if not query:
                return {'error': 'query required for search action'}

            results = []

            # Primary: pgvector semantic search on ConversationMemory
            try:
                from pgvector.django import CosineDistance
                from core.services.embedding_service import EmbeddingService
                emb_svc = EmbeddingService()
                emb_result = emb_svc.create_embedding(query, agent_name='conversation_tool')
                vector = emb_result.embedding

                cm_qs = ConversationMemory.objects.exclude(embedding__isnull=True)
                if user_id:
                    cm_qs = cm_qs.filter(user_id=user_id)
                if days_back:
                    cm_qs = cm_qs.filter(created_at__gte=timezone.now() - timedelta(days=days_back))

                semantic_hits = list(
                    cm_qs.annotate(distance=CosineDistance('embedding', vector))
                    .order_by('distance')[:limit]
                    .values('id', 'message', 'response', 'created_at', 'distance')
                )
                for hit in semantic_hits:
                    results.append({
                        'source': 'semantic',
                        'score': round(1.0 - (hit['distance'] or 1.0), 3),
                        'user_message': hit['message'][:300],
                        'assistant_response': hit['response'][:300],
                        'timestamp': hit['created_at'].isoformat() if hit['created_at'] else None,
                    })
            except Exception as e:
                logger.warning(f"[CONVERSATION] Semantic search failed: {e}")

            # Fallback/supplement: keyword search on ChatConversation
            kw_qs = ChatConversation.objects.filter(
                Q(user_message__icontains=query) | Q(assistant_response__icontains=query)
            )
            if user_id:
                kw_qs = kw_qs.filter(user_id=user_id)
            if days_back:
                kw_qs = kw_qs.filter(created_at__gte=timezone.now() - timedelta(days=days_back))

            kw_hits = list(
                kw_qs.order_by('-created_at')[:limit]
                .values('conversation_id', 'user_message', 'assistant_response', 'created_at', 'session_title')
            )

            # Dedupe: skip keyword hits already covered by semantic
            seen_snippets = {r['user_message'][:100] for r in results}
            for hit in kw_hits:
                snippet = hit['user_message'][:100]
                if snippet not in seen_snippets:
                    seen_snippets.add(snippet)
                    results.append({
                        'source': 'keyword',
                        'score': 0.5,
                        'conversation_id': hit['conversation_id'],
                        'session_title': hit.get('session_title', ''),
                        'user_message': hit['user_message'][:300],
                        'assistant_response': hit['assistant_response'][:300],
                        'timestamp': hit['created_at'].isoformat() if hit['created_at'] else None,
                    })

            # Sort by score desc
            results.sort(key=lambda r: r['score'], reverse=True)
            results = results[:limit]

            return {
                'action': 'search',
                'query': query,
                'count': len(results),
                'results': results,
            }

        elif action == 'summary':
            cid = payload.get('conversation_id')
            if not cid:
                return {'error': 'conversation_id required for summary action'}

            from core.tasks import summarize_conversation_task
            task = summarize_conversation_task.delay(
                conversation_id=cid,
                user_id=user_id,
            )
            return {
                'action': 'summary',
                'mode': 'async',
                'task_id': str(task.id),
                'message': f'Summarizing conversation {cid}...',
            }

        elif action == 'pin_memory':
            pin_title = payload.get('pin_title', '').strip()
            pin_content = payload.get('pin_content', '').strip()
            if not pin_title or not pin_content:
                return {'error': 'pin_title and pin_content required for pin_memory action'}

            pin_tags = payload.get('pin_tags') or ['pa-memory']

            from core.services.deliverable_factory import create_deliverable
            d = create_deliverable(
                title=pin_title,
                content=pin_content,
                agent_name=PA_IDENTITY,
                category='Memory',
                deliverable_type='document',
                is_pinned=True,
                is_saved=True,
                content_format='markdown',
                tags=pin_tags,
                metadata={'source': 'conversation_tool', 'pinned_by': 'pa'},
                user_id=user_id,
            )

            # Also embed for future semantic search
            try:
                from core.services.embedding_service import EmbeddingService
                emb_svc = EmbeddingService()
                emb_result = emb_svc.create_embedding(pin_content, agent_name='conversation_tool')
                if user_id:
                    ConversationMemory.objects.create(
                        user_id=user_id,
                        message=f"[PINNED] {pin_title}",
                        response=pin_content,
                        intent='pin_memory',
                        embedding=emb_result.embedding,
                    )
            except Exception as e:
                logger.warning(f"[CONVERSATION] Embedding for pinned memory failed: {e}")

            return {
                'action': 'pin_memory',
                'deliverable_id': str(d.id),
                'title': pin_title,
                'message': f'Pinned memory: "{pin_title}"',
            }

        elif action == 'recent':
            # List most recent PA conversations with IDs + timestamps.
            # Enables cross-channel discovery (find UI conversation from CLI).
            qs = ChatConversation.objects.filter(
                conversation_id__startswith='pa-',
            ).order_by('-created_at')

            if user_id:
                qs = qs.filter(user_id=user_id)

            # Distinct conversation IDs with latest timestamp
            from django.db.models import Max
            convos = list(
                qs.values('conversation_id', 'source')
                .annotate(last_activity=Max('created_at'))
                .order_by('-last_activity')[:limit]
            )

            return {
                'action': 'recent',
                'count': len(convos),
                'conversations': [
                    {
                        'conversation_id': c['conversation_id'],
                        'source': c['source'] or 'unknown',
                        'last_activity': c['last_activity'].isoformat() if c['last_activity'] else None,
                    }
                    for c in convos
                ],
            }

        return {'error': f'Unknown action: {action}'}

    def _handle_remember(self, tool_name, payload, user_id, trace_id):
        """Handle remember_tool: save/list/delete/search persistent memories."""
        import os
        import re
        import hashlib
        from django.contrib.auth import get_user_model
        from core.models import UserMemoryContext, EnhancedUserProfile
        from core.services.memory_context_service import get_memory_context_service

        User = get_user_model()
        action = payload.get('action', 'save')

        if not user_id:
            return {'error': 'User context required for memory operations'}
        user = User.objects.get(id=user_id)

        if action == 'save':
            content = (payload.get('content') or '').strip()
            if not content:
                return {'error': 'content is required for save action'}

            # Secret redaction
            from core.services.tool_dispatcher import _redact_secrets
            content = _redact_secrets(content)

            memory_type = payload.get('memory_type', 'preference')
            importance = min(max(payload.get('importance', 7), 1), 10)
            tags = payload.get('tags') or []

            # Env-var cap check
            max_items = int(os.environ.get('MEMORY_MAX_ITEMS', '200'))
            current_count = UserMemoryContext.objects.filter(user=user).count()
            if current_count >= max_items:
                return {
                    'error': f'Memory limit reached ({max_items} items). Delete old memories first.',
                    'current_count': current_count,
                    'max_items': max_items,
                }

            # Deduplication: hash of normalized content + memory_type
            content_hash = hashlib.sha256(
                f"{content.lower().strip()}:{memory_type}".encode()
            ).hexdigest()[:16]

            existing = UserMemoryContext.objects.filter(
                user=user,
                memory_type=memory_type,
                context_metadata__content_hash=content_hash,
            ).first()
            if existing:
                # Update importance if higher, bump timestamp
                if importance > existing.importance:
                    existing.importance = importance
                    existing.save(update_fields=['importance'])
                return {
                    'action': 'save',
                    'status': 'duplicate_updated',
                    'memory_id': existing.id,
                    'message': f'Memory already exists (updated importance to {max(importance, existing.importance)})',
                }

            # Save
            profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)
            memory = UserMemoryContext.objects.create(
                user=user,
                profile=profile,
                memory_type=memory_type,
                content=content[:500],
                importance=importance,
                source='remember_tool',
                tags=tags,
                context_metadata={
                    'content_hash': content_hash,
                    'trace_id': trace_id,
                },
            )

            # Clear memory context cache
            svc = get_memory_context_service()
            svc.clear_cache(user)

            # OpsRun event
            from core.tools.ops_run_tracker import get_active_tracker
            tracker = get_active_tracker()
            if tracker:
                tracker.info('memory_saved', {
                    'memory_id': memory.id,
                    'memory_type': memory_type,
                    'importance': importance,
                })

            return {
                'action': 'save',
                'memory_id': memory.id,
                'memory_type': memory_type,
                'importance': importance,
                'message': f'Remembered: "{content[:80]}"',
            }

        elif action == 'list':
            memories = UserMemoryContext.objects.filter(user=user).order_by('-importance', '-created_at')[:20]
            return {
                'action': 'list',
                'count': UserMemoryContext.objects.filter(user=user).count(),
                'memories': [
                    {
                        'id': str(m.id),
                        'type': m.memory_type,
                        'content': m.content[:200],
                        'importance': m.importance,
                        'tags': m.tags,
                        'created_at': m.created_at.isoformat(),
                    }
                    for m in memories
                ],
            }

        elif action == 'delete':
            memory_id = payload.get('memory_id')
            if not memory_id:
                return {'error': 'memory_id required for delete action'}
            deleted, _ = UserMemoryContext.objects.filter(user=user, id=memory_id).delete()
            if deleted:
                svc = get_memory_context_service()
                svc.clear_cache(user)
            return {
                'action': 'delete',
                'deleted': deleted > 0,
                'message': 'Memory deleted' if deleted else 'Memory not found',
            }

        elif action == 'search':
            query = (payload.get('query') or '').strip()
            if not query:
                return {'error': 'query required for search action'}
            results = UserMemoryContext.objects.filter(
                user=user,
                content__icontains=query,
            ).order_by('-importance')[:10]
            return {
                'action': 'search',
                'query': query,
                'count': len(results),
                'memories': [
                    {
                        'id': str(m.id),
                        'type': m.memory_type,
                        'content': m.content[:200],
                        'importance': m.importance,
                    }
                    for m in results
                ],
            }

        return {'error': f'Unknown action: {action}'}


    # ── Session 1078: Work Tool (Gateway) ──────────────────────────────────────
    def _handle_work(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1078: Work gateway — thin dispatcher over initiative_tool.
        Translates work_tool actions to initiative_tool actions and delegates.
        """
        action = payload.get('action', 'initiative_list')

        # Action name mapping: work_tool action → initiative_tool action + payload overrides
        # Session 1194 Plan B §3.B.3 — initiative_deliverables wired through
        # to _handle_initiative's new paginated reverse-projection branch.
        ACTION_MAP = {
            'initiative_list': ('list', {}),
            'initiative_detail': ('details', {}),
            'initiative_deliverables': ('initiative_deliverables', {}),
            'initiative_create': ('create', {}),
            'initiative_promote': ('promote', {}),
            'initiative_update_status': ('update_status', {}),
            'action_item_list': ('action_items', {}),
            'action_item_start': ('start_action_item', {}),
            'action_item_complete': ('complete_action_item', {}),
            'action_item_cleanup': ('cleanup_action_items', {}),
            'bulk_cleanup': ('bulk_cleanup', {}),
        }

        # ── Session 1100: Direct data actions (not delegated to initiative_tool) ──
        if action == 'agent_conversations':
            try:
                from core.models_unified_system import AgentConversation
                limit = min(int(payload.get('limit', 10)), 30)
                convs = AgentConversation.objects.select_related('initiator').prefetch_related('participants').order_by('-started_at')[:limit]
                return {
                    'gateway': 'work_tool', 'action': action,
                    'count': len(convs),
                    'conversations': [{
                        'id': str(c.id),
                        'topic': c.topic,
                        'initiator': c.initiator.name if c.initiator else 'unknown',
                        'participants': [p.name for p in c.participants.all()[:5]],
                        'status': c.status,
                        'message_count': c.message_count,
                        'conclusion': (c.conclusion or '')[:200],
                        'started_at': c.started_at.isoformat() if c.started_at else None,
                    } for c in convs],
                }
            except Exception as e:
                return {'gateway': 'work_tool', 'action': action, 'error': str(e)}

        if action == 'stats':
            # Session 1103c: aggregate counts for Rigby status snapshots.
            # Added because GPT-5.2 kept emitting action='stats' as a
            # natural guess for status update requests — previously the
            # dispatcher returned 'Unknown action' every single time,
            # leaving Rigby unable to answer status questions without
            # listing all initiatives and burning tokens.
            try:
                from core.models import Initiative, InitiativeActionItem
                from core.models_unified_system import (
                    AgentConversation, AgentExecution,
                )
                from django.db.models import Count

                init_counts = dict(
                    Initiative.objects.values_list('status')
                    .annotate(c=Count('id'))
                    .values_list('status', 'c')
                )
                item_counts = dict(
                    InitiativeActionItem.objects.values_list('status')
                    .annotate(c=Count('id'))
                    .values_list('status', 'c')
                )
                workflow_count = AgentExecution.objects.filter(
                    agent__name__in=[
                        'WorkflowAgent', 'WorkflowOrchestrationAgent',
                        'CampaignOrchestratorAgent', 'AISeriesWorkflowAgent',
                    ]
                ).count()
                conv_count = AgentConversation.objects.count()
                return {
                    'gateway': 'work_tool',
                    'action': 'stats',
                    'initiatives': {
                        'total': sum(init_counts.values()),
                        'by_status': init_counts,
                    },
                    'action_items': {
                        'total': sum(item_counts.values()),
                        'by_status': item_counts,
                    },
                    'workflows_total': workflow_count,
                    'agent_conversations_total': conv_count,
                }
            except Exception as e:
                return {
                    'gateway': 'work_tool',
                    'action': 'stats',
                    'error': f'{type(e).__name__}: {e}',
                }

        if action == 'workflows':
            try:
                from core.models_unified_system import AgentExecution
                limit = min(int(payload.get('limit', 10)), 30)
                execs = AgentExecution.objects.filter(
                    agent__name__in=['WorkflowAgent', 'WorkflowOrchestrationAgent',
                                     'CampaignOrchestratorAgent', 'AISeriesWorkflowAgent']
                ).select_related('agent').order_by('-created_at')[:limit]
                return {
                    'gateway': 'work_tool', 'action': action,
                    'count': len(execs),
                    'workflows': [{
                        'id': str(e.id),
                        'agent': e.agent.name if e.agent else 'unknown',
                        'status': e.status,
                        'task': (e.input_data or {}).get('task', '')[:150],
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in execs],
                }
            except Exception as e:
                return {'gateway': 'work_tool', 'action': action, 'error': str(e)}

        mapping = ACTION_MAP.get(action)
        if not mapping:
            extra_actions = ['agent_conversations', 'workflows', 'stats']
            all_acts = sorted(list(ACTION_MAP) + extra_actions)
            return {'error': f'Unknown work_tool action: {action}. Valid: {", ".join(all_acts)}'}

        initiative_action, overrides = mapping

        # Build the initiative_tool payload
        initiative_payload = dict(payload)
        initiative_payload['action'] = initiative_action
        initiative_payload.update(overrides)

        # Translate work_tool param names → initiative_tool param names
        # action_item_list: status → item_status (initiative_tool uses item_status for action items)
        if action == 'action_item_list':
            if 'status' in initiative_payload and 'item_status' not in initiative_payload:
                initiative_payload['item_status'] = initiative_payload.pop('status')

        # action_item_start / action_item_complete: id → item_id
        if action in ('action_item_start', 'action_item_complete'):
            if 'id' in initiative_payload and 'item_id' not in initiative_payload:
                initiative_payload['item_id'] = initiative_payload.get('id')

        # Delegate to existing initiative handler
        result = self._handle_initiative('initiative_tool', initiative_payload, user_id, trace_id)

        # Normalize the response action name to the work_tool action
        if isinstance(result, dict):
            result['gateway'] = 'work_tool'
            result['action'] = action

        return result

    # ── Session 1079: Intelligence Tool (gateway) ────────────────────────────────
    def _handle_rag_query(self, tool_name, payload, user_id, trace_id):
        """Search RAG knowledge base and get embedding stats."""
        action = payload.get('action', 'search')

        if action == 'search':
            query = payload.get('query', '').strip()
            if not query:
                return {'error': 'query is required for search action'}

            top_k = min(payload.get('top_k', 5), 20)
            threshold = payload.get('similarity_threshold', 0.3)
            doc_filter = payload.get('document_id')

            from content.embeddings import rag_system
            results = rag_system.semantic_search_sync(
                query=query,
                limit=top_k,
                similarity_threshold=threshold,
            )

            items = []
            for r in results:
                if doc_filter and r.document_id != doc_filter:
                    continue
                items.append({
                    'document_id': r.document_id,
                    'document_title': r.document_title,
                    'document_type': r.document_type,
                    'chunk_index': r.chunk_index,
                    'chunk_text': r.chunk_text[:1000],
                    'similarity_score': round(r.similarity_score, 4),
                    'source_type': getattr(r, 'source_type', 'unknown'),
                })

            return {
                'action': 'search',
                'query': query,
                'count': len(items),
                'results': items,
            }

        elif action == 'stats':
            from content.models import Document, DocumentEmbedding
            from django.db.models import Count

            total_embeddings = DocumentEmbedding.objects.count()
            total_docs = Document.objects.filter(status='processed').count()

            recent = list(
                Document.objects.filter(status='processed')
                .annotate(chunk_count=Count('embeddings'))
                .order_by('-created_at')[:5]
                .values('id', 'title', 'document_type', 'chunk_count', 'created_at')
            )
            for doc in recent:
                doc['id'] = str(doc['id'])
                doc['created_at'] = str(doc['created_at'])

            return {
                'action': 'stats',
                'total_documents': total_docs,
                'total_embeddings': total_embeddings,
                'recent_documents': recent,
            }

        elif action == 'list_documents':
            from content.models import Document
            from django.db.models import Count

            limit = min(payload.get('limit', 20), 50)
            doc_type = payload.get('document_type')

            qs = Document.objects.filter(status='processed')
            if doc_type:
                qs = qs.filter(document_type__icontains=doc_type)

            docs = list(
                qs.annotate(chunk_count=Count('embeddings'))
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'document_type', 'chunk_count', 'created_at', 'source_url')
            )
            for doc in docs:
                doc['id'] = str(doc['id'])
                doc['created_at'] = str(doc['created_at'])

            return {
                'action': 'list_documents',
                'count': len(docs),
                'documents': docs,
            }

        elif action == 'ingest':
            url = payload.get('url', '').strip()
            if not url:
                raise ValueError("'url' is required for ingest action")

            # Dispatch URL ingestion as async task
            from core.tasks import process_url_async
            task = process_url_async.delay(url=url, generate_embeddings=True)

            return {
                'action': 'ingest',
                'url': url,
                'task_id': str(task.id),
                'mode': 'async',
                'message': f'URL "{url}" queued for RAG ingestion. Use job_status to check progress.',
                'success': True,
            }

        elif action == 'promote':
            document_id = payload.get('document_id', '').strip()
            if not document_id:
                return {'error': 'document_id is required for promote action'}

            from content.models import Document
            try:
                doc = Document.objects.get(id=document_id)
            except Document.DoesNotExist:
                return {'error': f'Document {document_id} not found'}

            old_status = doc.promotion_status
            doc.promotion_status = 'promoted'
            doc.save(update_fields=['promotion_status', 'updated_at'])
            return {
                'action': 'promote',
                'document_id': str(doc.id),
                'title': doc.title,
                'old_status': old_status,
                'new_status': 'promoted',
                'message': f'Document "{doc.title}" promoted — now retrievable via RAG.',
            }

        elif action == 'staged':
            from content.models import Document
            limit = min(payload.get('limit', 20), 50)
            docs = list(
                Document.objects.filter(promotion_status='staged')
                .order_by('-created_at')[:limit]
                .values('id', 'title', 'document_type', 'source', 'created_at')
            )
            for d in docs:
                d['id'] = str(d['id'])
                d['created_at'] = str(d['created_at'])
            return {
                'action': 'staged',
                'count': len(docs),
                'documents': docs,
            }

        return {'error': f'Unknown action: {action}. Valid: search, stats, list_documents, ingest, promote, staged'}

    # ── Session G1: Competitor Comparison ────────────────────────────────────

    def _handle_competitor_comparison(self, tool_name, payload, user_id, trace_id):
        """Generate, check status, list, or view competitor comparisons."""
        action = payload.get('action', 'list')

        if action == 'generate':
            competitor_name = payload.get('competitor_name', '').strip()
            if not competitor_name:
                return {'error': 'competitor_name is required for generate action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.tasks import generate_competitor_comparison_task

            source_document_id = payload.get('source_document_id')
            focus_areas = payload.get('focus_areas')
            auto_research = payload.get('auto_research', True)

            comparison = CompetitorComparison.objects.create(
                competitor_name=competitor_name,
                source_document_id=source_document_id,
                generated_by='PA',
                user_id=user_id,
            )

            task = generate_competitor_comparison_task.delay(
                comparison_id=str(comparison.id),
                source_document_id=str(source_document_id) if source_document_id else None,
                competitor_name=competitor_name,
                focus_areas=focus_areas,
                auto_research=auto_research,
            )

            return {
                'action': 'generate',
                'comparison_id': str(comparison.id),
                'task_id': str(task.id),
                'message': f'Competitor comparison for "{competitor_name}" started',
            }

        elif action == 'status':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for status action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            result = {
                'action': 'status',
                'comparison_id': str(c.id),
                'competitor_name': c.competitor_name,
                'status': c.status,
                'quality_score': c.quality_score,
            }
            if c.status == 'complete':
                result['summary'] = c.summary[:500]
                result['completed_at'] = c.completed_at.isoformat() if c.completed_at else None
                result['executive_summary'] = c.executive_summary_json
            elif c.status == 'needs_sources':
                result['error_message'] = c.error_message[:500]
                result['recommended_queries'] = (c.metadata or {}).get('recommended_queries', [])
            elif c.status == 'failed':
                result['error_message'] = c.error_message[:500]
            return result

        elif action == 'list':
            from core.models_competitor_comparison import CompetitorComparison

            limit = min(int(payload.get('limit', 10)), 50)
            qs = CompetitorComparison.objects.order_by('-created_at')[:limit]

            return {
                'action': 'list',
                'count': len(qs),
                'comparisons': [
                    {
                        'id': str(c.id),
                        'competitor_name': c.competitor_name,
                        'status': c.status,
                        'quality_score': c.quality_score,
                        'evidence_count': len(c.evidence_json) if isinstance(c.evidence_json, list) else 0,
                        'summary': (c.summary[:200] if c.summary else ''),
                        'created_at': c.created_at.isoformat(),
                    }
                    for c in qs
                ],
            }

        elif action == 'detail':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for detail action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            return {
                'action': 'detail',
                'comparison': {
                    'id': str(c.id),
                    'competitor_name': c.competitor_name,
                    'status': c.status,
                    'quality_score': c.quality_score,
                    'executive_summary': c.executive_summary_json,
                    'quality_rubric': c.quality_rubric_json,
                    'sources': c.sources_json,
                    'review': c.review_json,
                    'comparison_table': c.comparison_table_json,
                    'gap_backlog': c.gap_backlog_json,
                    'tools_stack': c.tools_stack_json,
                    'evidence_count': len(c.evidence_json) if isinstance(c.evidence_json, list) else 0,
                    'summary': c.summary,
                    'created_at': c.created_at.isoformat(),
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                    'metadata': c.metadata,
                },
            }

        elif action == 'delete':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for delete action'}

            from core.models_competitor_comparison import CompetitorComparison
            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            name = c.competitor_name
            c.delete()
            return {
                'action': 'delete',
                'deleted': True,
                'competitor_name': name,
                'message': f'Comparison for "{name}" deleted',
            }

        elif action == 'regenerate':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for regenerate action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.tasks import generate_competitor_comparison_task

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            # Reset and re-dispatch
            c.status = 'pending'
            c.error_message = ''
            c.save(update_fields=['status', 'error_message', 'updated_at'])

            task = generate_competitor_comparison_task.delay(
                comparison_id=str(c.id),
                source_document_id=str(c.source_document_id) if c.source_document_id else None,
                competitor_name=c.competitor_name,
            )

            return {
                'action': 'regenerate',
                'comparison_id': str(c.id),
                'task_id': str(task.id),
                'message': f'Regenerating comparison for "{c.competitor_name}"',
            }

        elif action == 'create_initiative_from_gap':
            comparison_id = payload.get('comparison_id')
            gap_index = payload.get('gap_index', 0)
            if not comparison_id:
                return {'error': 'comparison_id is required for create_initiative_from_gap action'}

            from core.models_competitor_comparison import CompetitorComparison
            from core.models_document_registry import Initiative

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            if c.status != 'complete':
                return {'error': f'Comparison must be complete (current: {c.status})'}

            gaps = c.gap_backlog_json if isinstance(c.gap_backlog_json, list) else c.gap_backlog_json.get('gaps', [])
            if not gaps:
                return {'error': 'No gaps found in this comparison'}
            if gap_index >= len(gaps):
                return {'error': f'gap_index {gap_index} out of range (0-{len(gaps)-1})'}

            gap = gaps[gap_index]
            gap_title = gap.get('gap', gap.get('title', f'Gap #{gap_index + 1}'))
            effort = gap.get('effort', 'M')
            impact = gap.get('impact', 'medium')
            acceptance = gap.get('acceptance_test', gap.get('acceptance_criteria', ''))
            evidence_refs = gap.get('evidence_refs', [])

            # Map effort to purpose
            purpose = 'expansion' if impact == 'high' else 'learning'
            urgency_score = {'high': 0.8, 'medium': 0.5, 'low': 0.3}.get(impact, 0.5)

            name = f"[Competitive] {gap_title}"
            if Initiative.objects.filter(name=name).exists():
                return {
                    'error': f'Initiative "{name}" already exists',
                    'action': 'create_initiative_from_gap',
                }

            description_parts = [
                f"**Source:** Competitor comparison vs {c.competitor_name}",
                f"**Gap:** {gap_title}",
                f"**Effort:** {effort} | **Impact:** {impact}",
            ]
            if acceptance:
                description_parts.append(f"**Acceptance Criteria:** {acceptance}")
            if evidence_refs:
                description_parts.append(f"**Evidence:** {', '.join(evidence_refs)}")

            initiative = Initiative.objects.create(
                name=name,
                description='\n'.join(description_parts),
                status='ACTIVE',
                purpose=purpose,
                program='growth_intelligence',
                urgency=urgency_score,
                impact_score=urgency_score,
                confidence=c.quality_score,
                created_by='competitor_comparison',
                parent_topic=c.competitor_name,
            )

            return {
                'action': 'create_initiative_from_gap',
                'initiative_id': str(initiative.id),
                'initiative_name': initiative.name,
                'gap_title': gap_title,
                'message': f'Initiative created from gap: "{gap_title}"',
            }

        elif action == 'export_markdown':
            comparison_id = payload.get('comparison_id')
            if not comparison_id:
                return {'error': 'comparison_id is required for export_markdown action'}

            from core.models_competitor_comparison import CompetitorComparison

            try:
                c = CompetitorComparison.objects.get(id=comparison_id)
            except CompetitorComparison.DoesNotExist:
                return {'error': f'Comparison {comparison_id} not found'}

            if c.status != 'complete':
                return {'error': f'Comparison must be complete (current: {c.status})'}

            lines = [f"# Competitor Analysis: {c.competitor_name}", ""]

            # Executive summary
            exec_sum = c.executive_summary_json or {}
            if exec_sum.get('verdict'):
                lines += [f"## Executive Summary", "", exec_sum['verdict'], ""]
                if exec_sum.get('top_advantages'):
                    lines += ["### Top Advantages"]
                    for adv in exec_sum['top_advantages']:
                        lines.append(f"- {adv}")
                    lines.append("")
                if exec_sum.get('top_gaps'):
                    lines += ["### Top Gaps"]
                    for gap in exec_sum['top_gaps']:
                        lines.append(f"- {gap}")
                    lines.append("")

            # Comparison table
            table_data = c.comparison_table_json
            rows = table_data if isinstance(table_data, list) else table_data.get('rows', [])
            if rows:
                lines += ["## Side-by-Side Comparison", ""]
                lines.append("| Feature | Competitor | Donkey Betz | Evidence |")
                lines.append("|---------|-----------|-------------|----------|")
                for row in rows:
                    feature = row.get('feature', row.get('area', ''))
                    comp = row.get('competitor', row.get('them', ''))
                    us = row.get('donkey_betz', row.get('us', ''))
                    refs = ', '.join(row.get('evidence_refs', []))
                    lines.append(f"| {feature} | {comp} | {us} | {refs} |")
                lines.append("")

            # Gap backlog
            gaps = c.gap_backlog_json if isinstance(c.gap_backlog_json, list) else c.gap_backlog_json.get('gaps', [])
            if gaps:
                lines += ["## Gap Backlog", ""]
                for i, gap in enumerate(gaps):
                    title = gap.get('gap', gap.get('title', f'Gap #{i+1}'))
                    effort = gap.get('effort', '?')
                    impact = gap.get('impact', '?')
                    acceptance = gap.get('acceptance_test', gap.get('acceptance_criteria', ''))
                    refs = ', '.join(gap.get('evidence_refs', []))
                    lines.append(f"### {i+1}. {title}")
                    lines.append(f"- **Effort:** {effort} | **Impact:** {impact}")
                    if acceptance:
                        lines.append(f"- **Acceptance:** {acceptance}")
                    if refs:
                        lines.append(f"- **Evidence:** {refs}")
                    lines.append("")

            # Tools/Stack
            tools = c.tools_stack_json
            tools_list = tools if isinstance(tools, list) else tools.get('tools', [])
            if tools_list:
                lines += ["## Tools & Stack", ""]
                for t in tools_list:
                    if isinstance(t, str):
                        lines.append(f"- {t}")
                    else:
                        lines.append(f"- **{t.get('name', t.get('tool', ''))}**: {t.get('category', t.get('purpose', ''))}")
                lines.append("")

            # Sources
            sources = c.sources_json or []
            if sources:
                lines += ["## Sources", ""]
                for s in sources:
                    if isinstance(s, dict):
                        lines.append(f"- {s.get('title', 'Unknown')} ({s.get('source_type', '')})")
                    else:
                        lines.append(f"- {s}")
                lines.append("")

            # Quality rubric
            rubric = c.quality_rubric_json or {}
            if rubric:
                lines += ["## Quality Rubric", ""]
                lines.append(f"- **Overall Score:** {c.quality_score:.2f}")
                for key, val in rubric.items():
                    if key != 'composite_score':
                        lines.append(f"- **{key.replace('_', ' ').title()}:** {val}")
                lines.append("")

            lines.append(f"---\n*Generated {c.created_at.strftime('%Y-%m-%d %H:%M')} UTC*")

            markdown_content = '\n'.join(lines)

            # Save as Deliverable
            save_as_deliverable = payload.get('save', True)
            deliverable_id = None
            if save_as_deliverable:
                from core.models_deliverables import Deliverable
                from django.utils.text import slugify
                slug_base = slugify(f"competitor-{c.competitor_name}")[:250]
                slug = slug_base
                counter = 1
                while Deliverable.objects.filter(slug=slug).exists():
                    slug = f"{slug_base}-{counter}"
                    counter += 1

                from core.services.deliverable_factory import create_deliverable
                d = create_deliverable(
                    title=f"Competitor Analysis: {c.competitor_name}",
                    content=markdown_content,
                    agent_name='competitor_comparison_tool',
                    category='Competitive Intelligence',
                    deliverable_type='document',
                    tags=['competitor', 'analysis', c.competitor_name.lower()],
                    agent_task=f'Export comparison {c.id}',
                    content_format='markdown',
                    quality_score=c.quality_score,
                    confidence_score=c.quality_score,
                    slug=slug,
                    preview_content=markdown_content[:500],
                    user_id=user_id,
                    metadata={
                        'trigger_source': 'pa_tool',
                        'comparison_id': str(c.id),
                        'competitor_name': c.competitor_name,
                    },
                )
                deliverable_id = str(d.id)

            return {
                'action': 'export_markdown',
                'comparison_id': str(c.id),
                'competitor_name': c.competitor_name,
                'markdown': markdown_content,
                'deliverable_id': deliverable_id,
                'message': f'Exported comparison for "{c.competitor_name}" as Markdown' + (' (saved as Deliverable)' if deliverable_id else ''),
            }

        return {'error': f'Unknown action: {action}'}

    # ── Workflow Run Tool ────────────────────────────────────────────────
    def _handle_workflow_run(self, tool_name, payload, user_id, trace_id):
        """Start, poll, list, detail, or cancel multi-step workflow runs."""
        action = payload.get('action', 'list')

        if action == 'start':
            workflow_key = payload.get('workflow_key', 'source_pack_comparison')
            competitor_name = payload.get('competitor_name', '').strip()
            if not competitor_name:
                return {'error': 'competitor_name is required to start a workflow'}

            from core.models_workflow_run import WorkflowRun
            from core.tasks import run_source_pack_workflow

            run = WorkflowRun.objects.create(
                workflow_key=workflow_key,
                user_id=user_id,
                input_json={
                    'competitor_name': competitor_name,
                    'queries': payload.get('queries', []),
                    'target_count': payload.get('target_count', 8),
                    'comparison_id': payload.get('comparison_id'),
                    'focus_areas': payload.get('focus_areas'),
                },
            )

            logger.info(f"[WORKFLOW] Dispatching run_source_pack_workflow for run={run.id}")
            task = run_source_pack_workflow.apply_async(
                kwargs={'run_id': str(run.id)},
                queue='content',
            )
            logger.info(f"[WORKFLOW] Dispatched task_id={task.id} to queue=content for run={run.id}")
            run.celery_task_id = str(task.id)
            run.save(update_fields=['celery_task_id', 'updated_at'])

            return {
                'action': 'start',
                'run_id': str(run.id),
                'task_id': str(task.id),
                'workflow_key': workflow_key,
                'message': f'Source pack workflow started for "{competitor_name}"',
            }

        elif action == 'status':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for status action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            result = {
                'action': 'status',
                'run_id': str(run.id),
                'workflow_key': run.workflow_key,
                'status': run.status,
                'stage': run.stage,
                'percent': run.percent,
                'stage_detail': run.stage_detail,
            }
            if run.status == 'complete':
                result['output'] = run.output_json
                result['completed_at'] = run.completed_at.isoformat() if run.completed_at else None
            elif run.status == 'failed':
                result['error_message'] = run.error_message[:500]
                result['output'] = run.output_json
            # Include recent events
            events = run.events_json if isinstance(run.events_json, list) else []
            result['recent_events'] = events[-5:]
            return result

        elif action == 'list':
            from core.models_workflow_run import WorkflowRun

            limit = min(int(payload.get('limit', 10)), 50)
            qs = WorkflowRun.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            qs = qs.order_by('-created_at')[:limit]

            return {
                'action': 'list',
                'count': len(qs),
                'runs': [
                    {
                        'id': str(r.id),
                        'workflow_key': r.workflow_key,
                        'status': r.status,
                        'stage': r.stage,
                        'percent': r.percent,
                        'created_at': r.created_at.isoformat(),
                        'competitor_name': (r.input_json or {}).get('competitor_name', ''),
                    }
                    for r in qs
                ],
            }

        elif action == 'detail':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for detail action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            return {
                'action': 'detail',
                'run': {
                    'id': str(run.id),
                    'workflow_key': run.workflow_key,
                    'status': run.status,
                    'stage': run.stage,
                    'percent': run.percent,
                    'stage_detail': run.stage_detail,
                    'input': run.input_json,
                    'output': run.output_json,
                    'events': run.events_json,
                    'error_message': run.error_message,
                    'celery_task_id': run.celery_task_id,
                    'created_at': run.created_at.isoformat(),
                    'started_at': run.started_at.isoformat() if run.started_at else None,
                    'completed_at': run.completed_at.isoformat() if run.completed_at else None,
                    'metadata': run.metadata,
                },
            }

        elif action == 'cancel':
            run_id = payload.get('run_id')
            if not run_id:
                return {'error': 'run_id is required for cancel action'}

            from core.models_workflow_run import WorkflowRun
            try:
                run = WorkflowRun.objects.get(id=run_id)
            except WorkflowRun.DoesNotExist:
                return {'error': f'Workflow run {run_id} not found'}

            if run.status in ('complete', 'failed', 'cancelled'):
                return {'error': f'Cannot cancel a workflow in {run.status} state'}

            # Revoke celery task
            if run.celery_task_id:
                from core.celery import app as celery_app
                celery_app.control.revoke(run.celery_task_id, terminate=True)

            run.mark_cancelled()
            run.save()

            return {
                'action': 'cancel',
                'run_id': str(run.id),
                'message': 'Workflow cancelled',
            }

        return {'error': f'Unknown action: {action}'}

    # ── Conversation Memory ──────────────────────────────────────────────────

    def _handle_intelligence(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Intelligence gateway — unified desk for stocks, sports,
        legislation, search (KB/spider/web), and ML analytics.
        Wraps stock_intelligence_tool, sports_betting_tool, legislation_tool,
        rag_query_tool, spider_data_tool, web_search.
        """
        action = payload.get('action', 'overview')

        def _tag(result):
            if isinstance(result, dict):
                result['gateway'] = 'intelligence_tool'
                result['action'] = action
            return result

        # ── Composite: overview (merge 3 desk overviews) ──
        if action == 'overview':
            combined = {'desks': {}}
            for desk, tool, handler in [
                ('stocks', 'stock_intelligence_tool', self._handle_stock_intelligence),
                ('sports', 'sports_betting_tool', self._handle_sports_betting),
                ('legislation', 'legislation_tool', self._handle_legislation),
            ]:
                try:
                    desk_result = handler(tool, {'action': 'overview'}, user_id, trace_id)
                    combined['desks'][desk] = desk_result
                except Exception as e:
                    combined['desks'][desk] = {'error': str(e)}
            return _tag(combined)

        # ── Composite: briefs (desk param selects source) ──
        if action == 'briefs':
            desk = payload.get('desk', 'all')
            limit = payload.get('limit', 5)
            briefs_result = {'briefs': {}}
            desk_map = {
                'stocks': ('stock_intelligence_tool', self._handle_stock_intelligence, 'briefs'),
                'sports': ('sports_betting_tool', self._handle_sports_betting, 'brief'),
                'legislation': ('legislation_tool', self._handle_legislation, 'trending'),
            }
            desks_to_query = desk_map.keys() if desk == 'all' else [desk] if desk in desk_map else []
            for d in desks_to_query:
                tool_name_inner, handler, inner_action = desk_map[d]
                try:
                    r = handler(tool_name_inner, {'action': inner_action, 'limit': limit}, user_id, trace_id)
                    briefs_result['briefs'][d] = r
                except Exception as e:
                    briefs_result['briefs'][d] = {'error': str(e)}
            if not desks_to_query:
                briefs_result['error'] = f'Unknown desk: {desk}. Valid: stocks, sports, legislation, all'
            return _tag(briefs_result)

        # ── Composite: search (source param selects backend) ──
        if action == 'search':
            source = payload.get('source', 'kb')
            query = payload.get('query', '')
            limit = payload.get('limit', 10)
            if source == 'kb':
                result = self._handle_rag_query('rag_query_tool', {'action': 'search', 'query': query, 'limit': limit}, user_id, trace_id)
            elif source == 'spider':
                result = self._handle_spider_data('spider_data_tool', {'action': 'search', 'query': query, 'limit': limit}, user_id, trace_id)
            elif source == 'web':
                result = self._handle_web_search('web_search', {'query': query}, user_id, trace_id)
            else:
                result = {'error': f'Unknown source: {source}. Valid: kb, spider, web'}
            return _tag(result)

        # ── Stocks desk ──
        STOCKS_MAP = {
            'stocks_alerts': 'alerts',
            'stocks_predictions': 'predictions',
            'stocks_sec_filings': 'sec_filings',
        }
        if action in STOCKS_MAP:
            sp = dict(payload)
            sp['action'] = STOCKS_MAP[action]
            return _tag(self._handle_stock_intelligence('stock_intelligence_tool', sp, user_id, trace_id))

        # ── Sports desk ──
        SPORTS_MAP = {
            'sports_predictions': 'predictions',
            'sports_arbs': 'arbs',
            'sports_wagers': 'wagers',
            'sports_record_wager': 'record_wager',
        }
        if action in SPORTS_MAP:
            sp = dict(payload)
            sp['action'] = SPORTS_MAP[action]
            return _tag(self._handle_sports_betting('sports_betting_tool', sp, user_id, trace_id))

        # ── Legislation desk ──
        LEGISLATION_MAP = {
            'legislation_search': 'search',
            'legislation_summary': 'summary',
        }
        if action in LEGISLATION_MAP:
            lp = dict(payload)
            lp['action'] = LEGISLATION_MAP[action]
            return _tag(self._handle_legislation('legislation_tool', lp, user_id, trace_id))

        # ── KB ──
        if action == 'kb_ingest':
            return _tag(self._handle_rag_query('rag_query_tool', {'action': 'ingest', 'url': payload.get('url', '')}, user_id, trace_id))

        # ── Session 1100: Stock/market intelligence briefs ──
        if action == 'stock_briefs':
            try:
                from core.models_unified_system import MarketIntelligenceBrief
                limit = min(int(payload.get('limit', 10)), 50)
                briefs = MarketIntelligenceBrief.objects.order_by('-brief_date')[:limit]
                return _tag({
                    'action': 'stock_briefs',
                    'count': len(briefs),
                    'briefs': [{
                        'id': str(b.id),
                        'brief_date': str(b.brief_date),
                        'brief_type': b.brief_type,
                        'executive_summary': (b.executive_summary or '')[:300],
                        'high_conviction_count': len(b.high_conviction_opportunities or []),
                        'debate_zone_count': len(b.debate_zone) if hasattr(b, 'debate_zone') and b.debate_zone else 0,
                    } for b in briefs],
                })
            except Exception as e:
                return _tag({'action': 'stock_briefs', 'error': str(e)})

        # ── Session 1100: ML predictions ──
        if action == 'ml_predictions':
            try:
                from sports.models import MLPrediction
                limit = min(int(payload.get('limit', 10)), 30)
                preds = MLPrediction.objects.select_related('game', 'predicted_winner').order_by('-created_at')[:limit]
                total = MLPrediction.objects.count()
                evaluated = MLPrediction.objects.filter(evaluated_at__isnull=False).count()
                return _tag({
                    'action': 'ml_predictions',
                    'total': total,
                    'evaluated': evaluated,
                    'predictions': [{
                        'id': str(p.id),
                        'game': str(p.game) if p.game else None,
                        'predicted_winner': str(p.predicted_winner) if p.predicted_winner else None,
                        'confidence': p.confidence if hasattr(p, 'confidence') else None,
                        'correct': p.was_correct if hasattr(p, 'was_correct') else None,
                        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') and p.created_at else None,
                    } for p in preds],
                })
            except Exception as e:
                return _tag({'action': 'ml_predictions', 'error': str(e)})

        # ── Session 1100: Signal clusters ──
        if action == 'signal_clusters':
            try:
                from core.models import SignalCluster
                limit = min(int(payload.get('limit', 10)), 30)
                clusters = SignalCluster.objects.order_by('-detected_at')[:limit]
                return _tag({
                    'action': 'signal_clusters',
                    'count': len(clusters),
                    'clusters': [{
                        'id': str(c.id),
                        'name': c.name,
                        'pattern_type': c.pattern_type,
                        'signal_count': len(c.spider_data_ids) if c.spider_data_ids else 0,
                        'confidence': c.confidence if hasattr(c, 'confidence') else None,
                        'detected_at': c.detected_at.isoformat() if c.detected_at else None,
                    } for c in clusters],
                })
            except Exception as e:
                return _tag({'action': 'signal_clusters', 'error': str(e)})

        # ── Gap 4: Sharp action signals feed ──
        if action == 'sports_sharp_signals':
            try:
                from core.models_deliverables import Deliverable
                from django.utils import timezone as tz
                from datetime import timedelta

                limit = min(int(payload.get('limit', 10)), 30)
                sport = payload.get('sport', '').strip().lower()
                hours = int(payload.get('hours', 48))
                cutoff = tz.now() - timedelta(hours=hours)

                qs = Deliverable.objects.filter(
                    category='Sharp Action Detection',
                    created_at__gte=cutoff,
                ).order_by('-created_at')

                if sport:
                    qs = qs.filter(tags__icontains=sport)

                items = []
                for d in qs[:limit]:
                    content = d.content or ''
                    items.append({
                        'id': str(d.id),
                        'title': d.title,
                        'agent_name': d.agent_name,
                        'content_preview': content[:500],
                        'quality_score': d.quality_score,
                        'tags': d.tags or [],
                        'created_at': d.created_at.isoformat() if d.created_at else None,
                    })

                return _tag({
                    'action': 'sports_sharp_signals',
                    'count': len(items),
                    'total_in_window': qs.count(),
                    'hours': hours,
                    'items': items,
                })
            except Exception as e:
                return _tag({'action': 'sports_sharp_signals', 'error': str(e)})

        # ── Gap 6: Congress member lookup ──
        if action == 'congress_members':
            try:
                from core.models_government import CongressMember

                limit = min(int(payload.get('limit', 20)), 50)
                state = payload.get('state', '').strip().upper()
                chamber = payload.get('chamber', '').strip().lower()
                party = payload.get('party', '').strip()
                q = payload.get('query', '').strip()

                qs = CongressMember.objects.filter(in_office=True)
                if state:
                    qs = qs.filter(state=state)
                if chamber:
                    qs = qs.filter(chamber=chamber)
                if party:
                    qs = qs.filter(party__icontains=party)
                if q:
                    from django.db.models import Q as DQ
                    # Resolve full state name to 2-letter code
                    from core.services.congress_sync import STATE_ABBREV
                    state_code = STATE_ABBREV.get(q.title(), '')
                    q_filter = (
                        DQ(first_name__icontains=q) |
                        DQ(last_name__icontains=q) |
                        DQ(state__iexact=q) |
                        DQ(party__icontains=q)
                    )
                    if state_code:
                        q_filter = q_filter | DQ(state__iexact=state_code)
                    qs = qs.filter(q_filter)

                total = qs.count()
                members = []
                for m in qs.order_by('state', 'last_name')[:limit]:
                    members.append({
                        'bioguide_id': m.bioguide_id,
                        'name': m.full_name,
                        'party': m.party,
                        'state': m.state,
                        'district': m.district,
                        'chamber': getattr(m, 'chamber', ''),
                        'leadership_role': m.leadership_role or '',
                        'committees': (m.committees or [])[:5],
                    })

                return _tag({
                    'action': 'congress_members',
                    'total': total,
                    'count': len(members),
                    'members': members,
                })
            except Exception as e:
                return _tag({'action': 'congress_members', 'error': str(e)})

        # ── Gap 7: Tracked legislation list ──
        if action == 'legislation_tracked':
            try:
                from core.models_government import Bill

                limit = min(int(payload.get('limit', 20)), 50)
                status = payload.get('status', '').strip()
                chamber = payload.get('chamber', '').strip().lower()
                q = payload.get('query', '').strip()

                qs = Bill.objects.all()
                if status:
                    qs = qs.filter(status__icontains=status)
                if chamber:
                    qs = qs.filter(chamber=chamber)
                if q:
                    qs = qs.filter(title__icontains=q)

                total = qs.count()
                bills = []
                for b in qs.order_by('-updated_at')[:limit]:
                    bills.append({
                        'bill_uid': b.bill_uid,
                        'title': (b.title or '')[:150],
                        'status': getattr(b, 'status', ''),
                        'chamber': getattr(b, 'chamber', ''),
                        'jurisdiction': getattr(b, 'jurisdiction', ''),
                        'topics': (b.topics or [])[:5] if hasattr(b, 'topics') else [],
                        'has_embedding': b.embedding is not None if hasattr(b, 'embedding') else False,
                        'updated_at': b.updated_at.isoformat() if hasattr(b, 'updated_at') and b.updated_at else None,
                    })

                return _tag({
                    'action': 'legislation_tracked',
                    'total': total,
                    'count': len(bills),
                    'bills': bills,
                })
            except Exception as e:
                return _tag({'action': 'legislation_tracked', 'error': str(e)})

        all_actions = [
            'overview', 'briefs', 'search',
            'stocks_alerts', 'stocks_predictions', 'stocks_sec_filings',
            'sports_predictions', 'sports_arbs', 'sports_wagers', 'sports_record_wager',
            'legislation_search', 'legislation_summary',
            'kb_ingest',
            'stock_briefs', 'ml_predictions', 'signal_clusters',
            'sports_sharp_signals', 'congress_members', 'legislation_tracked',
        ]
        return {'error': f'Unknown intelligence_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── Session 1079: Governance Tool (gateway) ──────────────────────────────────
    def _handle_governance(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """
        Session 1079: Governance gateway — unified human-in-the-loop inbox.
        Wraps boardroom_tool and human_decisions_tool into one surface.
        """
        action = payload.get('action', 'inbox')

        # ── boardroom_tool actions ──
        BOARDROOM_MAP = {
            'inbox': 'stats',
            'attention_list': 'list_attention',
            'attention_approve': 'approve_attention',
            'attention_ignore': 'ignore_attention',
            'attention_detail': 'lookup',  # Session 1097: ID-based detail
            'attention_lookup': 'lookup',
            'decision_list': 'list_decisions',
            'decision_promote': 'promote_decision',
            'decision_reject': 'reject_decision',
            'triage_batch': 'get_triage_batch',
        }

        # Session 1103c: plain 'stats' action — GPT-5.2 kept guessing
        # this natural name and hitting 'Unknown action'. Bundled
        # overview across boardroom inbox + decision stats + failure
        # signatures + remediation tasks so one call answers
        # 'governance status?' questions instead of forcing the model
        # into a multi-step chain.
        if action == 'stats':
            bundled = {'gateway': 'governance_tool', 'action': 'stats'}
            try:
                inbox = self._handle_boardroom(
                    'boardroom_tool', {'action': 'stats'}, user_id, trace_id,
                )
                bundled['inbox'] = inbox if isinstance(inbox, dict) else {'raw': inbox}
            except Exception as e:
                bundled['inbox'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                decisions = self._handle_human_decisions(
                    'human_decisions_tool', {'action': 'stats'}, user_id, trace_id,
                )
                bundled['decisions'] = decisions if isinstance(decisions, dict) else {'raw': decisions}
            except Exception as e:
                bundled['decisions'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                from core.models_diagnostic_pipeline import FailureSignature
                bundled['failure_signatures_total'] = FailureSignature.objects.count()
            except Exception as e:
                bundled['failure_signatures_total'] = {'error': f'{type(e).__name__}: {e}'}
            try:
                from core.models_audit_tracking import AuditRemediationTask
                bundled['remediation_tasks_total'] = AuditRemediationTask.objects.count()
            except Exception as e:
                bundled['remediation_tasks_total'] = {'error': f'{type(e).__name__}: {e}'}
            return bundled

        if action in BOARDROOM_MAP:
            br_payload = dict(payload)
            br_payload['action'] = BOARDROOM_MAP[action]
            result = self._handle_boardroom('boardroom_tool', br_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'governance_tool'
                result['action'] = action
            return result

        # ── human_decisions_tool actions ──
        DECISIONS_MAP = {
            'decisions_list': 'list',
            'decisions_stats': 'stats',
            'decision_create': 'create',
            'decision_decide': 'decide',
        }

        if action in DECISIONS_MAP:
            hd_payload = dict(payload)
            hd_payload['action'] = DECISIONS_MAP[action]
            # Translate param: id → item_id for decide action
            if action == 'decision_decide':
                if 'id' in hd_payload and 'item_id' not in hd_payload:
                    hd_payload['item_id'] = hd_payload.get('id')
            result = self._handle_human_decisions('human_decisions_tool', hd_payload, user_id, trace_id)
            if isinstance(result, dict):
                result['gateway'] = 'governance_tool'
                result['action'] = action
            return result

        # ── Session 1100: Failure signatures (read-only) ──
        if action == 'failure_signatures':
            try:
                from core.models_diagnostic_pipeline import FailureSignature
                limit = min(int(payload.get('limit', 10)), 30)
                sigs = FailureSignature.objects.order_by('-last_seen_at')[:limit]
                return {
                    'gateway': 'governance_tool', 'action': action,
                    'count': len(sigs),
                    'signatures': [{
                        'id': str(s.id),
                        'category': s.category,
                        'signature_hash': s.signature_hash[:16] if hasattr(s, 'signature_hash') else '',
                        'occurrence_count': s.occurrence_count if hasattr(s, 'occurrence_count') else 0,
                        'description': (s.description or '')[:200] if hasattr(s, 'description') else '',
                        'last_seen_at': s.last_seen_at.isoformat() if s.last_seen_at else None,
                    } for s in sigs],
                }
            except Exception as e:
                return {'gateway': 'governance_tool', 'action': action, 'error': str(e)}

        # ── Session 1100: Remediation tasks (read-only) ──
        if action == 'remediation_tasks':
            try:
                from core.models_audit_tracking import AuditRemediationTask
                limit = min(int(payload.get('limit', 10)), 30)
                tasks = AuditRemediationTask.objects.select_related('finding').order_by('-id')[:limit]
                return {
                    'gateway': 'governance_tool', 'action': action,
                    'count': len(tasks),
                    'tasks': [{
                        'id': str(t.id),
                        'title': t.title,
                        'status': t.status,
                        'assigned_agent': t.assigned_agent or '',
                        'finding': t.finding.title if t.finding else '',
                    } for t in tasks],
                }
            except Exception as e:
                return {'gateway': 'governance_tool', 'action': action, 'error': str(e)}

        extra_actions = ['failure_signatures', 'remediation_tasks', 'stats']
        all_actions = sorted(list(BOARDROOM_MAP) + list(DECISIONS_MAP) + extra_actions)
        return {'error': f'Unknown governance_tool action: {action}. Valid: {", ".join(all_actions)}'}

    # ── In-App Messaging Tool ──────────────────────────────────────────────────

    def _handle_messaging(self, tool_name, payload, user_id, trace_id):
        """Handle in-app messaging between platform users."""
        from django.contrib.auth import get_user_model
        from core.models_messaging import MessageThread, ThreadParticipant, DirectMessage

        User = get_user_model()
        action = payload.get('action', '')

        if not user_id:
            return {'error': 'Authentication required for messaging'}

        try:
            sender = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return {'error': 'User not found'}

        if action == 'send_message':
            recipient_username = payload.get('recipient_username', '').strip()
            message_body = payload.get('message', '').strip()

            if not recipient_username:
                return {'error': 'recipient_username is required'}
            if not message_body:
                return {'error': 'message is required'}

            try:
                recipient = User.objects.get(username=recipient_username)
            except User.DoesNotExist:
                # List available users to help
                usernames = list(
                    User.objects.filter(is_active=True, is_staff=True)
                    .exclude(id=user_id)
                    .values_list('username', flat=True)
                )
                return {
                    'error': f'User "{recipient_username}" not found',
                    'available_users': usernames,
                }

            # Find or create DM thread between these two users
            existing_thread = (
                MessageThread.objects
                .filter(thread_type='dm', is_archived=False)
                .filter(threadparticipant__user=sender)
                .filter(threadparticipant__user=recipient)
                .first()
            )

            if existing_thread:
                thread = existing_thread
            else:
                thread = MessageThread.objects.create(
                    thread_type='rigby_routed',
                    subject=payload.get('subject', ''),
                    metadata={'routed_by': 'rigby', 'trace_id': trace_id},
                )
                ThreadParticipant.objects.create(thread=thread, user=sender)
                ThreadParticipant.objects.create(thread=thread, user=recipient)

            # Create the message
            msg = DirectMessage.objects.create(
                thread=thread,
                sender=sender,
                body=message_body,
                sender_type='rigby',
                metadata={
                    'routed_by': 'rigby',
                    'trace_id': trace_id,
                    'on_behalf_of': sender.username,
                },
            )

            # Update thread timestamp
            from django.utils import timezone
            thread.updated_at = timezone.now()
            thread.save(update_fields=['updated_at'])

            # Broadcast via WebSocket
            from core.views_inbox import _broadcast_new_message
            _broadcast_new_message(thread, msg)

            return {
                'action': 'send_message',
                'status': 'sent',
                'thread_id': str(thread.id),
                'message_id': str(msg.id),
                'recipient': recipient.username,
                'message_preview': message_body[:100],
                'message': f'Message sent to {recipient.username}: "{message_body[:60]}..."' if len(message_body) > 60 else f'Message sent to {recipient.username}: "{message_body}"',
            }

        elif action == 'list_threads':
            participations = (
                ThreadParticipant.objects
                .filter(user=sender, thread__is_archived=False)
                .select_related('thread')
                .order_by('-thread__updated_at')[:20]
            )

            threads = []
            for p in participations:
                other_users = list(
                    User.objects.filter(thread_participations__thread=p.thread)
                    .exclude(id=sender.id)
                    .values_list('username', flat=True)
                )
                last_msg = p.thread.messages.order_by('-created_at').first()
                threads.append({
                    'thread_id': str(p.thread.id),
                    'participants': other_users,
                    'unread_count': p.unread_count,
                    'last_message': last_msg.body[:80] if last_msg else None,
                    'last_message_at': last_msg.created_at.isoformat() if last_msg else None,
                    'thread_type': p.thread.thread_type,
                })

            return {
                'action': 'list_threads',
                'thread_count': len(threads),
                'threads': threads,
            }

        elif action == 'get_thread':
            thread_id = payload.get('thread_id', '')
            if not thread_id:
                return {'error': 'thread_id is required'}

            try:
                participant = ThreadParticipant.objects.get(
                    thread_id=thread_id, user=sender
                )
            except ThreadParticipant.DoesNotExist:
                return {'error': 'Thread not found or access denied'}

            messages = (
                DirectMessage.objects
                .filter(thread_id=thread_id)
                .select_related('sender')
                .order_by('created_at')[:50]
            )

            return {
                'action': 'get_thread',
                'thread_id': thread_id,
                'messages': [{
                    'sender': m.sender.username if m.sender else m.sender_type,
                    'body': m.body,
                    'created_at': m.created_at.isoformat(),
                    'sender_type': m.sender_type,
                } for m in messages],
            }

        elif action == 'unread_count':
            participations = ThreadParticipant.objects.filter(
                user=sender, thread__is_archived=False, is_muted=False,
            )
            total = sum(p.unread_count for p in participations)
            return {
                'action': 'unread_count',
                'unread_count': total,
                'message': f'You have {total} unread message{"s" if total != 1 else ""}.',
            }

        valid = ['send_message', 'list_threads', 'get_thread', 'unread_count']
        return {'error': f'Unknown messaging_tool action: {action}. Valid: {", ".join(valid)}'}

    # ── Session tool: conversation health + fresh session creation ──────────────

    def _handle_session(self, tool_name, payload, user_id, trace_id) -> Dict:
        """Handle conversation session management: health check, create fresh, list recent."""
        action = payload.get('action', 'health_check')

        if action == 'health_check':
            from core.services.session_health_service import get_session_health

            conversation_id = payload.get('conversation_id') or getattr(self, '_current_conversation_id', None)
            if not conversation_id:
                return {'error': 'No conversation_id provided and no current conversation context.'}

            health = get_session_health(conversation_id, user_id)
            return {
                'action': 'health_check',
                **health,
            }

        elif action == 'create_fresh':
            import uuid
            from core.models import ChatConversation

            new_id = f"pa-{uuid.uuid4().hex[:16]}"
            title = payload.get('title', 'New session')
            carry_forward = payload.get('carry_forward_summary', '')

            # Create the first message in the new conversation to establish it
            ChatConversation.objects.create(
                conversation_id=new_id,
                user_id=user_id,
                session_title=title,
                user_message=f"[Session created] {carry_forward}" if carry_forward else "[Session created]",
                assistant_response=f"Fresh session started. {('Context carried forward: ' + carry_forward[:500]) if carry_forward else 'Ready to go.'}",
            )

            # Generate a starter prompt from the old conversation if we have one
            old_conversation_id = getattr(self, '_current_conversation_id', None)
            starter_prompt = ''
            if old_conversation_id:
                try:
                    from core.services.session_health_service import get_session_health
                    old_health = get_session_health(old_conversation_id, user_id)
                    starter_prompt = old_health.get('starter_prompt', '')
                except Exception as _e:
                    logger.warning(
                        "td_core._handle_session: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            return {
                'action': 'create_fresh',
                'conversation_id': new_id,
                'title': title,
                'starter_prompt': starter_prompt,
                'message': f'Fresh conversation created: {new_id}',
            }

        elif action == 'list_recent':
            from core.models import ChatConversation
            from django.db.models import Count, Max

            limit = min(payload.get('limit', 10), 25)

            recent = (
                ChatConversation.objects.filter(user_id=user_id)
                .values('conversation_id', 'session_title')
                .annotate(
                    message_count=Count('id'),
                    last_message=Max('created_at'),
                )
                .order_by('-last_message')[:limit]
            )

            conversations = []
            for conv in recent:
                conversations.append({
                    'conversation_id': conv['conversation_id'],
                    'title': conv['session_title'] or 'Untitled',
                    'message_count': conv['message_count'],
                    'last_message': conv['last_message'].isoformat() if conv['last_message'] else None,
                })

            return {
                'action': 'list_recent',
                'conversations': conversations,
                'count': len(conversations),
            }

        valid = ['health_check', 'create_fresh', 'list_recent']
        return {'error': f'Unknown session_tool action: {action}. Valid: {", ".join(valid)}'}

    # ── Session 1079: Content Tool (gateway) ─────────────────────────────────────
