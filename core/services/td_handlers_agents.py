"""
ToolDispatcher AgentHandlersMixin — extracted handler methods.
"""
from core.services.pa_identity import PA_IDENTITY
from core.services.td_error import _handler_error

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

from django.db import OperationalError, ProgrammingError
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


class AgentHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    def _tool_to_agent_name(self, tool_name: str) -> str:
        """Map tool name to agent class name."""
        mappings = {
            # ── Media Creation & Editing ──
            'image_generation_agent': 'ImageAgent',
            'image_editing_agent': 'ImageEditingAgent',
            'video_generation_agent': 'VideoAgent',
            'video_editing_agent': 'VideoEditingAgent',
            'resolve_agent': 'ResolveAgent',
            'audio_generation_agent': 'AudioAgent',
            'three_d_generation_agent': 'ThreeDAgent',
            'character_training_agent': 'CharacterTrainingAgent',
            'talking_character_agent': 'TalkingCharacterAgent',
            # ── Research & Analysis ──
            'research_agent': 'ResearchAgent',
            'trend_analysis_agent': 'TrendAnalysisAgent',
            'opportunity_scoring_agent': 'OpportunityScoringAgent',
            'platform_audit_agent': 'PlatformAuditAgent',
            'thinking_agent': 'ThinkingAgent',
            # ── Strategy & Content ──
            'brand_identity_agent': 'BrandIdentityAgent',
            'seo_optimizer_agent': 'SEOOptimizerAgent',
            'social_media_agent': 'SocialMediaAgent',
            'editor_agent': 'EditorAgent',
            'content_audit_agent': 'ContentAuditAgent',
            'creative_director_agent': 'CreativeDirectorAgent',
            # ── Business Research ──
            'competitor_analysis_agent': 'CompetitorAnalysisAgent',
            'customer_research_agent': 'CustomerResearchAgent',
            'brand_strategy_agent': 'BrandStrategyAgent',
            'content_strategy_agent': 'ContentStrategyAgent',
            'marketing_strategy_agent': 'MarketingStrategyAgent',
            'content_writer_agent': 'ContentWriterAgent',
            # ── Executive & Orchestration ──
            'cto_agent': 'CTOAgent',
            'coo_agent': 'COOAgent',
            'meeting_coordinator_agent': 'MeetingCoordinatorAgent',
            'campaign_orchestrator_agent': 'CampaignOrchestratorAgent',
            'opportunity_pipeline_agent': 'OpportunityPipelineAgent',
            'ai_series_workflow_agent': 'AISeriesWorkflowAgent',
            # WorkflowOrchestrationAgent (template-based, 16+ workflows) is
            # distinct from WorkflowAgent (delegate coordinator); both are
            # registered separately in AGENT_MAP.
            'workflow_orchestration_agent': 'WorkflowOrchestrationAgent',
            # ── Development (Session 1093 P3) ──
            'code_review_agent': 'CodeReviewAgent',
            'create_brand_video': 'WorkflowAgent',
            'create_project_from_research': 'WorkflowAgent',
            'strategic_review': 'ContentStrategyAgent',  # Session 1068: StrategyAgent doesn't exist
            'system_intelligence_agent': 'SystemIntelligenceAgent',
            # ── Stock & Markets ──
            'stock_audit_coordinator': 'StockAuditCoordinator',
            'stock_analyst_agent': 'StockAnalystAgent',
            'bear_case_agent': 'BearCaseAgent',
            'market_intelligence_coordinator': 'MarketIntelligenceCoordinator',
            'market_intelligence_agent': 'MarketIntelligenceAgent',
            # ── Sports & Betting ──
            'prediction_market_analyst': 'PredictionMarketAnalyst',
            'game_predictor': 'GamePredictor',
            'line_movement_analyzer': 'LineMovementAnalyzer',
            'sharp_action_detector': 'SharpActionDetector',
            # ── Blockchain Audit ──
            'blockchain_audit_coordinator': 'BlockchainAuditCoordinator',
            'whale_watcher_agent': 'WhaleWatcherAgent',
            # ── Narrative Drift ──
            # ── Content Studio ──
            'autonomous_content_studio_coordinator': 'AutonomousContentStudioCoordinator',
            'topic_miner_agent': 'TopicMinerAgent',
            'contrarian_agent': 'ContrarianAgent',
            'performance_analyst_agent': 'PerformanceAnalystAgent',
            'voice_critic_agent': 'VoiceCriticAgent',
            'content_diversity_orchestrator': 'ContentDiversityOrchestrator',
            # ── Podcast ──
            'podcast_coordinator_agent': 'PodcastCoordinatorAgent',
            # ── Training & Security ──
            'trained_creation_agent': 'TrainedCreationAgent',
            'memory_isolation_agent': 'MemoryIsolationAgent',
            'security_agent': 'MemoryIsolationAgent',
            # ── Legal ──
            'legal_doc_drafter_agent': 'LegalDocDrafterAgent',
        }
        if tool_name in mappings:
            return mappings[tool_name]
        # Fallback: convert snake_case tool_name → CamelCase agent class name.
        # Prior implementation used `.title()`, which leaves underscores intact
        # (e.g. 'market_intelligence_agent' → 'Market_IntelligenceAgent'). That
        # produced a name that matches no Agent row and no agent class, so
        # dispatch silently no-op'd while Celery still returned SUCCESS — the
        # exact reliability-embarrassment the A1 wedge would surface. The join
        # form here strips underscores so 'market_intelligence_agent' resolves
        # to 'MarketIntelligenceAgent'. Explicit mapping entries above still win
        # for special cases (e.g. 'three_d_generation_agent' → 'ThreeDAgent').
        stem = tool_name[:-len('_agent')] if tool_name.endswith('_agent') else tool_name
        return ''.join(part.capitalize() for part in stem.split('_')) + 'Agent'

    def _get_agent_execution_output(self, celery_task_id: str, execution_id: str = None) -> Dict[str, Any]:
        """Enrich job_status with AgentExecution output data — full content, media URLs, deliverables.

        Session 1088: Bridge between Celery task IDs and rich agent outputs.
        Session 1089: Deep extraction for all agent types:
          - ContentWriterAgent: metadata.content.full_text (or metadata.full_text)
          - ImageAgent: metadata.images[*].url
          - VideoAgent/AudioAgent/TalkingCharacterAgent: metadata media URLs
          - Generic: output.content as fallback
        """
        extras: Dict[str, Any] = {}
        try:
            from core.models_unified_system import AgentExecution
            from datetime import timedelta

            execution = None
            if execution_id:
                execution = AgentExecution.objects.filter(id=execution_id).first()
            if not execution:
                execution = AgentExecution.objects.filter(
                    input_data__celery_task_id=celery_task_id,
                ).order_by('-created_at').first()

            if not execution:
                return extras

            extras['agent'] = extras.get('agent') or execution.agent.name
            extras['execution_id'] = str(execution.id)

            output = execution.output_data or {}
            metadata = output.get('metadata', {}) or {}
            if not isinstance(metadata, dict):
                metadata = {}

            # --- Content extraction (deep) ---
            # Priority: metadata.content.full_text > metadata.full_text > output.content
            full_text = ''

            # ContentWriterAgent: result.data = {'content': {'full_text': '...', 'sections': [...]}}
            meta_content = metadata.get('content')
            if isinstance(meta_content, dict):
                full_text = meta_content.get('full_text', '')
            elif isinstance(meta_content, str) and meta_content:
                full_text = meta_content

            # Some agents put full_text directly in metadata
            if not full_text:
                full_text = metadata.get('full_text', '')

            # Fallback: output['content'] (result.message — usually a summary)
            if not full_text:
                full_text = output.get('content', '') or ''

            if full_text:
                extras['content'] = full_text[:3000]
                extras['content_preview'] = full_text[:500]

            # --- Image extraction ---
            images = metadata.get('images', [])
            if isinstance(images, list) and images:
                image_urls = [img.get('url', '') for img in images if isinstance(img, dict) and img.get('url')]
                if image_urls:
                    extras['image_urls'] = image_urls
                    extras['image_url'] = image_urls[0]
                    extras['image_count'] = len(image_urls)

            # --- Direct media URL keys ---
            for key in ('image_url', 'video_url', 'audio_url', 'thumbnail_url',
                        'file_url', 'cloudinary_url', 'final_video_url'):
                val = metadata.get(key)
                if val and key not in extras:
                    extras[key] = val

            # --- Deliverable info from metadata ---
            if metadata.get('deliverable_id'):
                extras['deliverable_id'] = metadata['deliverable_id']
            if metadata.get('deliverable_title'):
                extras['deliverable_title'] = metadata['deliverable_title']

            # --- Deliverable lookup by agent + time window ---
            # Session 1083 (Rigby audit): was `except Exception: pass` which
            # silently dropped deliverable linkage whenever the lookup hit a
            # transient DB error (ProgrammingError on schema drift,
            # OperationalError on connection issues). Narrowed + logged so
            # Chris can see when agent executions lose their deliverable tie.
            if not extras.get('deliverable_id'):
                try:
                    from core.models_deliverables import Deliverable
                    end_time = (execution.completed_at or execution.created_at) + timedelta(seconds=30)
                    recent_del = Deliverable.objects.filter(
                        agent_name=execution.agent.name,
                        created_at__gte=execution.created_at - timedelta(seconds=10),
                        created_at__lte=end_time,
                    ).order_by('-created_at').first()
                    if recent_del:
                        extras['deliverable_id'] = str(recent_del.id)
                        extras['deliverable_title'] = recent_del.title
                        # If no content yet, pull from deliverable
                        if not extras.get('content') and recent_del.content:
                            extras['content'] = recent_del.content[:3000]
                            extras['content_preview'] = recent_del.content[:500]
                except ImportError as e:
                    logger.warning(f"Deliverable model unavailable for enrichment: {e}")
                except (OperationalError, ProgrammingError) as e:
                    logger.warning(
                        f"DB error fetching deliverable for execution {execution.id}: {e}"
                    )

            # --- Image history fallback ---
            # Session 1083: same LIAR pattern — silent drop of image_url when
            # ImageHistory query degrades. Narrowed to import + DB errors.
            if not extras.get('image_url'):
                try:
                    from content.models import ImageHistory
                    recent_img = ImageHistory.objects.filter(
                        created_at__gte=execution.created_at,
                    ).order_by('-created_at').first()
                    if recent_img and hasattr(recent_img, 'file_path') and recent_img.file_path:
                        if recent_img.file_path.startswith('http'):
                            extras['image_url'] = recent_img.file_path
                            if hasattr(recent_img, 'prompt') and recent_img.prompt:
                                extras['image_prompt'] = recent_img.prompt[:200]
                except ImportError as e:
                    logger.debug(f"ImageHistory model unavailable: {e}")
                except (OperationalError, ProgrammingError) as e:
                    logger.warning(
                        f"DB error fetching image history for execution {execution.id}: {e}"
                    )

        except Exception as e:
            logger.debug(f"_get_agent_execution_output failed: {e}")
        return extras

    def _handle_legal_agent(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1035: Handle legal assistant via AgentRouter.route().
        Session 1062: Made async — dispatches to Celery task to avoid PA tool timeout.
        S2803 Phase 3.0: routes through shared dispatch_legal_draft helper —
            same disclaimer_acknowledged gate + LegalDocumentDispatchLog audit
            as the UI /api/legal/draft/ endpoint. Rigby PA callers MUST set
            disclaimer_acknowledged=True in the payload (or the top-level
            context) or dispatch is rejected.
        """
        task_description = payload.get('task') or payload.get('query', '')
        context = payload.get('context', {}) or {}
        # Accept the ack from either the payload root or the nested context.
        disclaimer_acknowledged = bool(
            payload.get('disclaimer_acknowledged')
            or context.get('disclaimer_acknowledged')
        )
        client_session_pin = str(
            payload.get('conversation_id')
            or context.get('conversation_id')
            or ''
        )

        from django.contrib.auth import get_user_model
        from core.services.legal_dispatch import (
            DisclaimerRequired,
            dispatch_legal_draft,
        )

        User = get_user_model()
        user = User.objects.filter(id=user_id).first() if user_id else None
        if user is None:
            return {
                'agent': 'LegalDocDrafterAgent',
                'action': 'draft_legal_document',
                'success': False,
                'error': 'Authenticated user required for legal drafting.',
            }

        try:
            result = dispatch_legal_draft(
                user=user,
                task_description=task_description,
                disclaimer_acknowledged=disclaimer_acknowledged,
                ip_address=None,  # not available from PA tool dispatch surface
                user_agent='',
                client_session_pin=client_session_pin,
                context=context,
            )
        except DisclaimerRequired as exc:
            return {
                'agent': 'LegalDocDrafterAgent',
                'action': 'draft_legal_document',
                'success': False,
                'error_code': 'disclaimer_required',
                'error': str(exc),
                'message': (
                    'Legal drafting requires explicit disclaimer acknowledgement. '
                    'Include disclaimer_acknowledged=true in the tool call payload '
                    'after confirming the user understands this is not legal advice.'
                ),
            }

        if result.get('success') is False:
            return {
                'agent': 'LegalDocDrafterAgent',
                'action': 'draft_legal_document',
                **result,
            }

        return {
            'agent': 'LegalDocDrafterAgent',
            'action': 'draft_legal_document',
            'mode': 'async',
            'task': task_description,
            'task_id': result['task_id'],
            'dispatch_log_id': result['dispatch_log_id'],
            'message': (
                'Legal document drafting has been queued. This typically takes '
                '1-3 minutes. Use task_breakdown_tool to check progress.'
            ),
        }

    def _handle_web_search(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle web search — synchronous via Serper API.

        Serves both the legacy `web_search` tool name and the gateway
        `intelligence_tool` with `action=search, source=web` path. Honors a
        caller-supplied `limit` (gateway convention) or `num_results` (legacy
        convention) so the gateway migration doesn't silently regress callers
        that requested more results. Clamped to a hard ceiling of 10 to keep
        Serper cost/latency bounded for any oversized request.
        """
        from core.tools.web_search import WebSearchTool

        query = payload.get('query', '')
        raw_max = payload.get('limit') or payload.get('num_results') or 5
        try:
            max_results = min(int(raw_max), 10)
        except (ValueError, TypeError):
            max_results = 5
        search_tool = WebSearchTool()
        result = search_tool.execute(query=query, max_results=max_results, search_type='text')

        if result.get('success'):
            data = result.get('data', {})
            results = data.get('results', [])
            return {
                'query': query,
                'results': results,
                'total_results': len(results),
                'search_methods_used': data.get('search_methods_used', []),
            }
        return {
            'query': query,
            'results': [],
            'error': result.get('error', 'Search failed'),
        }

    def _handle_web_fetch(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Raw HTTP fetch tool (Rigby Tool Gap Ledger #15, shipped S2865).

        Minimal GET/POST fetch surface so PA / Rigby can self-service the
        raw-HTTP verification cases that previously required Claude off-tool
        (S2863 Q1 HF Hub API check, S2864 post-code Q4 local feed check).

        Future concerns (Rigby zoom-out SIGN S2865 — folded here, not
        acted on this slate): (a) if platform ever goes multi-tenant this
        becomes primary SSRF vector — flip allow_private_networks default
        to false + add cloud-metadata blocklist then; (b) exfiltration via
        fetch + summarize workflows is out-of-scope for this tool but
        worth watching if deliverables start containing sensitive bodies;
        (c) bot-protection / CORS / cookies misconceptions — this is not
        a browser, docstring makes it clear.
        """
        import httpx
        from urllib.parse import urlparse

        _TEXT_LIKE_PREFIXES = (
            'text/',
            'application/json',
            'application/javascript',
            'application/xml',
        )

        url = (payload.get('url') or '').strip()
        if not url:
            return {'ok': False, 'error': 'url is required'}

        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return {
                'ok': False,
                'error': f"disallowed scheme '{parsed.scheme}' (only http/https allowed)",
                'url': url,
            }

        method = (payload.get('method') or 'GET').upper()
        if method not in ('GET', 'POST'):
            return {
                'ok': False,
                'error': f"unsupported method '{method}' (only GET/POST allowed)",
                'url': url,
            }

        # Clamp timeout to [1, 60]
        try:
            timeout_seconds = float(payload.get('timeout_seconds') or 15)
        except (TypeError, ValueError):
            timeout_seconds = 15.0
        timeout_seconds = max(1.0, min(timeout_seconds, 60.0))

        # Clamp max_bytes to [1024, 2_000_000]
        try:
            max_bytes = int(payload.get('max_bytes') or 500_000)
        except (TypeError, ValueError):
            max_bytes = 500_000
        max_bytes = max(1024, min(max_bytes, 2_000_000))

        headers = payload.get('headers') or {}
        if not isinstance(headers, dict):
            headers = {}
        params = payload.get('params') or None
        if params is not None and not isinstance(params, dict):
            params = None
        json_body = payload.get('json_body') if method == 'POST' else None
        allow_private_networks = bool(payload.get('allow_private_networks', True))

        # S3000 v2 item #5: opt-in DRF Token auth for internal endpoints.
        # When the caller sets `use_user_auth=True` AND we have a `user_id`
        # in the dispatch context, look up the user's DRF Token and inject
        # `Authorization: Token <key>` — but only if the caller hasn't
        # already supplied an Authorization header (respect explicit
        # overrides). Fail-open: no token → proceed unauthenticated; the
        # endpoint will 401 and the caller sees that in the response.
        # Precedent: `td_handlers_core.py:854` uses the same lookup.
        use_user_auth = bool(payload.get('use_user_auth'))
        auth_injected = False
        if use_user_auth and user_id is not None:
            has_auth_header = any(k.lower() == 'authorization' for k in headers)
            if not has_auth_header:
                try:
                    from rest_framework.authtoken.models import Token
                    token_obj = Token.objects.filter(user_id=user_id).first()
                    if token_obj:
                        headers = dict(headers)  # avoid mutating caller
                        headers['Authorization'] = f'Token {token_obj.key}'
                        auth_injected = True
                except Exception:  # noqa: BLE001 — auth injection is best-effort
                    logger.warning(
                        "web_fetch_tool: Token lookup failed user_id=%s trace_id=%s",
                        user_id, trace_id, exc_info=True,
                    )

        # Log without leaking Authorization header value or body content
        header_names = sorted(headers.keys())
        logger.info(
            "web_fetch_tool call: method=%s url=%s header_names=%s "
            "timeout=%.1fs max_bytes=%d allow_private=%s auth_injected=%s "
            "trace_id=%s",
            method,
            url,
            header_names,
            timeout_seconds,
            max_bytes,
            allow_private_networks,
            auth_injected,
            trace_id,
        )

        started = time.monotonic()
        try:
            with httpx.Client(
                timeout=httpx.Timeout(
                    connect=min(5.0, timeout_seconds),
                    read=timeout_seconds,
                    write=min(5.0, timeout_seconds),
                    pool=min(5.0, timeout_seconds),
                ),
                follow_redirects=True,
                max_redirects=5,
            ) as client:
                if method == 'GET':
                    resp = client.get(url, headers=headers, params=params)
                else:
                    resp = client.post(
                        url,
                        headers=headers,
                        params=params,
                        json=json_body,
                    )
        except httpx.TimeoutException as e:
            return {
                'ok': False,
                'error': f"timeout after {timeout_seconds:.1f}s: {e}",
                'url': url,
                'latency_ms': int((time.monotonic() - started) * 1000),
            }
        except httpx.HTTPError as e:
            return {
                'ok': False,
                'error': f"http error ({type(e).__name__}): {e}",
                'url': url,
                'latency_ms': int((time.monotonic() - started) * 1000),
            }

        latency_ms = int((time.monotonic() - started) * 1000)
        raw_bytes = resp.content or b''
        body_bytes_total = len(raw_bytes)
        truncated = body_bytes_total > max_bytes
        body_slice = raw_bytes[:max_bytes] if truncated else raw_bytes

        content_type = (resp.headers.get('content-type') or '').lower()
        is_text_like = any(content_type.startswith(p) for p in _TEXT_LIKE_PREFIXES)

        body_text = ''
        body_text_note = None
        parsed_json = None
        if is_text_like:
            body_text = body_slice.decode('utf-8', errors='replace')
            # Only try JSON parse when server said JSON; don't parse text/html as JSON.
            if 'json' in content_type and not truncated:
                try:
                    parsed_json = resp.json()
                except (ValueError, Exception):
                    parsed_json = None
        elif content_type:
            body_text_note = 'omitted_non_text_content_type'
        else:
            body_text_note = 'omitted_unknown_content_type'

        response_headers = {k: v for k, v in resp.headers.items()}

        return {
            'ok': True,
            'status_code': resp.status_code,
            'final_url': str(resp.url),
            'content_type': content_type,
            'body_bytes': body_bytes_total,
            'truncated': truncated,
            'body_text': body_text,
            'body_text_note': body_text_note,
            'json': parsed_json,
            'response_headers': response_headers,
            'latency_ms': latency_ms,
        }

    def _handle_orm_inspect(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Bounded ORM row inspector (Rigby Tool Gap Ledger #3 / b5a22ea7, S2866).

        Read-only, allowlist-scoped Django ORM inspection. Closes the S2845-
        class false-negative gap where a tool surface reports 'no data' but
        rows exist under a different filter path (140 AI-community clusters
        found via ORM after enum-restricted source filter returned 0).

        Design contract (per pre-code SIGN S2866 Q3+Q6 F-BLOCKING):
          - Per-model policy dict (allowlist + sensitivity flag + expensive
            text field list) — no field-name heuristic alone.
          - JSONField default: excluded for high-sensitivity models
            (LLMCallLog, AutopilotAction, OpsRun); included with recursive
            key-redaction for others.
          - No FK traversal / deep __ chains (single-underscore lookups only).
          - No .save / .update / .delete surface — construction only.

        S2867 extension — added action='count_by' (aggregate group-by counts).
        Design contract per pre-code SIGN S2867 Q1+Q2+Q3+Q6 F-AGREE:
          - New _validate_groupby_field mirrors _validate_filter_kwargs strictness
            (field exists + not sensitive + not JSONField + not expensive_text).
          - FK fields group on <field>_id (matches _serialize_row convention).
          - DateTimeField auto-buckets to day via TruncDate (matches "how many
            rows match X by day" original ask; explicit truncate= is v2).
          - Group cardinality bounded: default limit=50, max=500. total_matching
            (pre-group row count) + group_count (distinct group values) reported
            separately from returned/truncated so operators see when a cap hit.

        Future v2 (Rigby zoom-out folded, not shipped this slate):
          - Token-shape heuristic redaction (JWT-ish, Bearer, long-base64).
          - Per-model per-field lookup allowlist (currently global lookup set).
          - order_by allowlist per model (currently common-field intersection).
          - Multi-tenant workspace_id enforcement (deferred per single-tenant
            pre-prod context; flip to required if multi-tenant ever ships).
          - Euphemistic-name coverage: fields like `opaque`, `blob`, `payload`,
            `header_value`, `signed_value` can carry secrets but don't match
            name heuristics. Mitigation: per-model explicit allowed_fields
            (v2) — for v1, the JSONField-omission-by-default posture on
            sensitive models is the primary net.
          - count_by extensions: explicit truncate='day'|'week'|'month' for
            DateTimeField (auto-day covers the primary ask), multi-field
            group-by, opt-in value_repr batched lookup for FK groups. Carve
            out to separate orm_aggregate_tool per Q6 zoom-out only if any of
            those v2 items land (this tool stays "bounded inspection").
          - count_by group_key_note (post-code SIGN Q2 fold): add an optional
            human-readable one-liner describing how group_key was resolved
            (e.g., "FK grouped on attname <field>_id", "DateTimeField grouped
            by TruncDate(field)"). Not shipped in v1 — group_key + the field
            type on describe_model already carry the information.
          - count_by high-cardinality guardrail (post-code SIGN Q5 fold): if
            an operator groups on a high-cardinality unindexed column of a
            large table (e.g., LLMCallLog.trace_id when it exists), the
            GROUP BY can be heavy. Considered adding a total_matching
            threshold that nudges callers to filter first, or a soft-warning
            field. Deferred — the row cap (limit + max 500) and truncation
            signal already bound the response size; DB-plan-cost surfacing
            is out of scope for a "bounded inspection" tool.
        """
        from django.apps import apps as _apps
        from django.core.exceptions import FieldError, ObjectDoesNotExist
        from django.db.models import Count, DateField, DateTimeField, JSONField, TextField
        from django.db.models.functions import TruncDate

        # ── Policy tables ────────────────────────────────────────────────────
        # Sensitive field-name rules — post-code SIGN S2866 Case 3 fold:
        # naive `'token' in name.lower()` matched `total_tokens`/`prompt_tokens`
        # (numeric counters, non-sensitive). Switched to two-layer match:
        #   1) COMPOSITE substrings for known-dangerous multi-word field names
        #      (`api_key`, `access_key`, etc.) — match anywhere in the name.
        #   2) EXACT word matching against SENSITIVE_WORDS after splitting the
        #      field name on '_'/'-' — so `access_token` splits to
        #      {'access','token'} and matches, but `total_tokens` splits to
        #      {'total','tokens'} and does NOT match (no 'tokens' in set).
        _SENSITIVE_WORDS = frozenset({
            'password', 'secret', 'authorization',
            'token', 'apikey', 'cookie', 'credential', 'creds',
            'session', 'csrf', 'xsrf',
            'signature', 'salt', 'nonce',
            'encrypted', 'encryption',
        })

        _SENSITIVE_COMPOSITES = (
            'api_key', 'access_key', 'refresh_token', 'id_token',
            'client_secret', 'private_key', 'ssh_key', 'rsa_key',
            'set_cookie', 'auth_token', 'session_token', 'session_key',
            'bearer_token', 'webhook_secret', 'webhook_key',
            'pem_key', 'pem_cert',
            # Post-code SIGN round 2 Case B fold-ins (provider + header names)
            'auth_header', 'authorization_header',
            'x_api_key', 'openai_key', 'anthropic_key', 'github_pat',
        )

        # Exact keys to redact recursively inside JSONField values.
        _JSON_REDACT_KEYS = frozenset({
            'token', 'api_key', 'apikey', 'access_key', 'authorization',
            'cookie', 'set_cookie', 'secret', 'client_secret',
            'credential', 'creds', 'password',
            'refresh_token', 'id_token', 'private_key',
            'auth', 'signature', 'bearer', 'session_token',
        })

        _SAFE_LOOKUPS = frozenset({
            'exact', 'iexact', 'isnull',
            'gt', 'gte', 'lt', 'lte',
            'contains', 'icontains',
            'startswith', 'istartswith',
            'in',
            'has_key', 'has_keys',
        })

        _COMMON_ORDER_FIELDS = frozenset({
            'id', 'created_at', 'updated_at',
            'detected_at', 'started_at', 'finished_at',
            'first_seen', 'last_seen', 'signal_window_start',
        })

        # Per-model policy. app_label + model_name resolved via apps.get_model.
        # sensitive=True → include_json_fields defaults false.
        # expensive_text_fields → contains/icontains rejected on these fields.
        _MODEL_POLICIES: Dict[str, Dict[str, Any]] = {
            'SignalCluster': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': (),
            },
            'Deliverable': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('content', 'preview_content', 'agent_task'),
            },
            'Initiative': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': (
                    'description', 'stop_rule', 'manual_priority_reason',
                    'next_action', 'blocking_reason', 'boardroom_approval_notes',
                ),
            },
            'LLMCallLog': {
                'app_label': 'core', 'sensitive': True,
                'expensive_text_fields': ('response_preview', 'error_message'),
            },
            'Agent': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('description',),
            },
            # S2931 Rigby Tool Gap Ledger #33 — AgentExecution surfacing.
            # Complements Agent (already in allowlist). S2930 recon forced
            # 3× Django shell fallback to trace agent-run status/latency/cost;
            # this closes that gap so Rigby can filter/count executions by
            # agent/status/user/tenant/trace without leaving the tool surface.
            # `task` + `error_message` are TextFields that can each exceed
            # a few KB per row so both are blocked from contains lookups.
            # `input_data` / `output_data` are JSONFields — model marked
            # non-sensitive so they render with recursive key-redaction (no
            # tokens/creds expected in agent I/O, but redaction is defensive).
            'AgentExecution': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('task', 'error_message'),
            },
            # S2942 Ledger #38 gate satisfy — UserFeedback surfacing so
            # dry_run acceptance-gate verification (pre/post count identical
            # after dry_run=true submit) runs entirely on Rigby's tool
            # surface. `message` + `resolution_notes` are TextFields
            # (user-authored, can be lengthy) so both are blocked from
            # contains lookups. Model is non-sensitive; content is user
            # feedback, not credentials.
            'UserFeedback': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('message', 'resolution_notes'),
            },
            # S2942 Ledger #38 gate satisfy — SelfBlog surfacing so
            # dry_run acceptance-gate verification of the SelfBlog path
            # (blog_tool.approve/reject with type='blog') can confirm
            # status/publish_ready unchanged after dry_run=true. `full_text`
            # is a large TextField (article bodies), blocked from contains.
            'SelfBlog': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('full_text',),
            },
            'AutopilotAction': {
                'app_label': 'core', 'sensitive': True,
                'expensive_text_fields': (),
            },
            'Budget': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': (),
            },
            'OpsRun': {
                'app_label': 'core', 'sensitive': True,
                'expensive_text_fields': (),
            },
            # S2871 Ledger #23 — spider-data inspection unblocks list-form
            # raw_data prevalence checks that S2870 pre-code SIGN couldn't
            # ground. Public web content; embedding_text is a TextField that
            # can hold ~4KB per row so it's blocked from contains lookups.
            'LegacySpiderData': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('embedding_text',),
            },
            # S2873 Rigby Tool Gap Ledger wish-list #2 — persistence.SpiderData
            # is the canonical spider-persistence model (116K rows vs LegacySpiderData's
            # 15K). Same public-web-content sensitivity level as LegacySpiderData.
            # content (article bodies) + raw_html (full page source) can each
            # exceed 10KB per row, so both are blocked from contains lookups.
            'SpiderData': {
                'app_label': 'persistence', 'sensitive': False,
                'expensive_text_fields': ('content', 'raw_html'),
            },
            # S2873 Rigby Tool Gap Ledger wish-list #3 — core.Opportunity is
            # the revenue-side opportunities model (2.6K rows, user-facing).
            # description is the only TextField on the model. FKs (user,
            # workspace, spider_data, project, recommended_by) emit as *_id
            # per existing FK-attname pattern; single-tenant pre-prod context
            # (per project_single_user_pre_prod_operating_context) means no
            # workspace_id gating required at v1.
            'Opportunity': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('description',),
            },
            # S2964 canon_v2 Item 1 (Fold P2, S2962 → ratified S2963 arc-close):
            # Golden Evals slice 8 (rigby_agent.yaml) pivoted the eval substrate
            # from AgentExecution to ChatConversation to capture buyer-facing
            # Rigby PA turns (source IN ('web', 'pa') — 1,018 all-time / 508 30d).
            # Without this allowlist entry, harness dogfood + operational
            # verification for the ChatConversation substrate would require
            # dropping to Django shell every run — accretes the same tool-gap
            # ledger #19 pattern this canon_v2 item explicitly closes.
            # user_message + assistant_response are TextFields that can each
            # exceed 10KB per row (largest observed ~50KB analytic responses),
            # so both are blocked from contains lookups. context_used /
            # metadata / agent_results are JSONFields (handled by the JSON
            # redaction path). Model is non-sensitive; content is user-authored
            # Chris↔Rigby traffic, not credentials.
            'ChatConversation': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('user_message', 'assistant_response'),
            },
            # S2964 canon_v2 Item 1 (continued): ToolCallRecord is the primary
            # evidence-pointer substrate declared in rigby_agent.yaml's
            # canonical_field_mapping.evidence_pointers (per Rigby T1 Q1 REVISE
            # at S2962). Harness validators join ToolCallRecord rows to
            # ChatConversation rows by trace_id / created_at window; without
            # this allowlist entry, harness dogfood cannot verify tool-run
            # counts or dispatch outcomes via Rigby's tool surface.
            # result_summary is capped at 4KB per row but authored as TextField
            # (with '... [truncated]' suffix marker) so contains lookups would
            # scan the truncated text; full_result is capped at 64KB
            # (full_result_dropped=True when payload exceeds cap); error_message
            # is unbounded TextField. All three blocked from contains lookups.
            # parameters is JSONField (redaction path). task_summary is
            # CharField(500) — safe for contains.
            'ToolCallRecord': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('result_summary', 'full_result', 'error_message'),
            },
            # S2991 v2 item #5 — DocResearchFinding surfacing so Rigby's
            # A2 SIGN cycles on the Findings surface can verify row state
            # directly instead of relying on Claude-side ORM shells. Same
            # blocker hit at S2990 close (marking) + S2991 close_mode
            # migration A2 (verification) — two triggers within two
            # sessions justify closing the tool-surface gap. Non-sensitive:
            # rows are docs/research/ bullet extractions, no credentials.
            # `text` (finding body) + `resolution_note` (Chris/Rigby close
            # notes, often multi-line) are TextFields that can exceed 4KB
            # per row so both blocked from contains lookups. `tags` +
            # `metadata` are JSONFields (redaction path).
            'DocResearchFinding': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': ('text', 'resolution_note'),
            },
            # S3032 Rigby Tool Gap Ledger — AgentDecisionSummary allowlist
            # entry. Live trigger at S3030 T1 SIGN: Rigby needed to run the
            # canonical-drift probe (filter status='canonical' +
            # is_canonical=False → count) but the model wasn't in the
            # allowlist, forcing a fallback to Django shell via Claude.
            # Session 3026 → S3031 arc closed the drift-class at code
            # level; this closes the tool-surface gap so future S30XX arcs
            # touching decision lifecycle (drift audits, promotion state
            # verification, backfill dry-runs) can be verified end-to-end
            # on Rigby's tool surface without leaving it.
            # Non-sensitive: content is agent-authored decision text
            # (recommendations, rationale, feature suggestions), not
            # credentials or user PII. `recommended_stance` +
            # `suggested_feature` + `rationale` are TextFields with
            # potentially long content — blocked from contains lookups.
            # `topic` is CharField(255), safe for contains. `key_insights`
            # + `participants` are JSONFields (bullet list + agent name
            # list), handled by recursive-key-redaction path.
            'AgentDecisionSummary': {
                'app_label': 'core', 'sensitive': False,
                'expensive_text_fields': (
                    'recommended_stance', 'suggested_feature', 'rationale',
                ),
            },
        }

        _MAX_LIMIT = 200
        _DEFAULT_LIMIT = 20
        _MAX_STR_LEN = 4096  # per-field truncation cap
        _MAX_IN_LIST = 100
        _DEFAULT_GROUP_LIMIT = 50   # count_by default distinct groups returned
        _MAX_GROUP_LIMIT = 500      # count_by hard cap on distinct groups returned

        # ── Helpers ──────────────────────────────────────────────────────────
        def _is_sensitive_field_name(name: str) -> bool:
            lower = name.lower()
            if any(c in lower for c in _SENSITIVE_COMPOSITES):
                return True
            words = set(lower.replace('-', '_').split('_'))
            return bool(words & _SENSITIVE_WORDS)

        def _redact_json(value: Any, depth: int = 0) -> Any:
            if depth > 8:
                return '<redacted:depth>'
            if isinstance(value, dict):
                out: Dict[str, Any] = {}
                for k, v in value.items():
                    if isinstance(k, str) and k.lower() in _JSON_REDACT_KEYS:
                        out[k] = '<redacted>'
                    else:
                        out[k] = _redact_json(v, depth + 1)
                return out
            if isinstance(value, list):
                return [_redact_json(x, depth + 1) for x in value]
            if isinstance(value, str) and len(value) > _MAX_STR_LEN:
                return value[:_MAX_STR_LEN] + f'…<truncated:{len(value)}b>'
            return value

        def _truncate_str(value: Any) -> Any:
            if isinstance(value, str) and len(value) > _MAX_STR_LEN:
                return value[:_MAX_STR_LEN] + f'…<truncated:{len(value)}b>'
            return value

        def _get_model_class(name: str):
            policy = _MODEL_POLICIES.get(name)
            if policy is None:
                return None, None
            try:
                model_cls = _apps.get_model(policy['app_label'], name)
            except LookupError:
                return None, policy
            return model_cls, policy

        def _serialize_row(instance, model_cls, policy, requested_fields, include_json) -> Dict[str, Any]:
            row: Dict[str, Any] = {}
            for field in model_cls._meta.get_fields():
                if field.is_relation and not field.many_to_one:
                    continue  # skip reverse relations
                fname = field.name
                if requested_fields is not None and fname not in requested_fields:
                    continue
                if _is_sensitive_field_name(fname):
                    row[fname] = '<redacted:field_name>'
                    continue
                # FK: return the id, not the object
                if field.many_to_one:
                    fk_id_attr = fname + '_id'
                    row[fname] = getattr(instance, fk_id_attr, None)
                    continue
                # JSONField policy
                if isinstance(field, JSONField):
                    if not include_json:
                        row[fname] = '<omitted:json_field>'
                        continue
                    raw = getattr(instance, fname, None)
                    row[fname] = _redact_json(raw)
                    continue
                raw = getattr(instance, fname, None)
                # Coerce UUID / Decimal / datetime to string for JSON transport
                if raw is None:
                    row[fname] = None
                elif isinstance(raw, (str, int, float, bool)):
                    row[fname] = _truncate_str(raw)
                else:
                    row[fname] = _truncate_str(str(raw))
            return row

        def _validate_filter_kwargs(kwargs: Dict[str, Any], model_cls, policy) -> Optional[str]:
            model_field_names = {f.name for f in model_cls._meta.get_fields()}
            expensive_fields = set(policy.get('expensive_text_fields') or ())
            for key, value in kwargs.items():
                parts = key.split('__')
                # Reject deep chains — one lookup segment max
                if len(parts) > 2:
                    return f"filter key '{key}' has deep __ chain (only field or field__lookup allowed)"
                field_name = parts[0]
                lookup = parts[1] if len(parts) == 2 else 'exact'
                if field_name not in model_field_names:
                    return f"field '{field_name}' not on model {model_cls.__name__}"
                if lookup not in _SAFE_LOOKUPS:
                    return f"lookup '{lookup}' not allowed (allowed: {sorted(_SAFE_LOOKUPS)})"
                if _is_sensitive_field_name(field_name):
                    return f"filter on sensitive field '{field_name}' rejected"
                if lookup in ('contains', 'icontains') and field_name in expensive_fields:
                    return (
                        f"contains/icontains rejected on expensive text field "
                        f"'{field_name}' — use exact or a shorter startswith prefix"
                    )
                if lookup == 'in':
                    if not isinstance(value, list):
                        return f"'in' lookup on '{field_name}' requires a list value"
                    if len(value) > _MAX_IN_LIST:
                        return f"'in' list on '{field_name}' capped at {_MAX_IN_LIST} (got {len(value)})"
            return None

        def _validate_groupby_field(field_name: str, model_cls, policy) -> Optional[str]:
            """Guardrails for count_by target field per pre-code SIGN Q1 F-AGREE.

            Strictness parity with _validate_filter_kwargs plus JSONField and
            expensive_text_fields blocks (grouping on JSON or long free text
            yields unbounded distinct values → runaway query cost).
            """
            model_field_names = {f.name for f in model_cls._meta.get_fields()}
            if field_name not in model_field_names:
                return f"field '{field_name}' not on model {model_cls.__name__}"
            if _is_sensitive_field_name(field_name):
                return f"group-by on sensitive field '{field_name}' rejected"
            field_obj = model_cls._meta.get_field(field_name)
            if isinstance(field_obj, JSONField):
                return (
                    f"group-by on JSONField '{field_name}' rejected — group values "
                    f"would be raw JSON blobs. Use filter_kwargs with has_key + "
                    f"count_by on a categorical column instead."
                )
            expensive = set(policy.get('expensive_text_fields') or ())
            if field_name in expensive:
                return (
                    f"group-by on expensive text field '{field_name}' rejected "
                    f"(would produce unbounded distinct values)"
                )
            return None

        def _coerce_group_value(value: Any) -> Any:
            """Serialize a group-by result value for JSON transport."""
            if value is None:
                return None
            if isinstance(value, (str, int, float, bool)):
                return value
            # UUID / Decimal / date / datetime → string
            return str(value)

        # ── Action dispatch ──────────────────────────────────────────────────
        action = (payload.get('action') or '').strip()
        logger.info(
            "orm_inspect_tool call: action=%s model=%s user_id=%s trace_id=%s",
            action, payload.get('model'), user_id, trace_id,
        )

        _VALID_ACTIONS = ('list_models', 'describe_model', 'get', 'filter', 'count_by')
        if action not in _VALID_ACTIONS:
            return {'ok': False, 'error': f"unknown action '{action}' (allowed: {', '.join(_VALID_ACTIONS)})"}

        if action == 'list_models':
            models_out = []
            for name, pol in sorted(_MODEL_POLICIES.items()):
                model_cls, _ = _get_model_class(name)
                if model_cls is None:
                    continue
                models_out.append({
                    'name': name,
                    'app_label': pol['app_label'],
                    'sensitive': pol['sensitive'],
                    'expensive_text_fields': list(pol.get('expensive_text_fields') or ()),
                    'field_count': len(model_cls._meta.get_fields()),
                })
            return {'ok': True, 'action': 'list_models', 'count': len(models_out), 'models': models_out}

        model_name = (payload.get('model') or '').strip()
        if not model_name:
            return {'ok': False, 'error': "model is required for describe_model/get/filter"}

        model_cls, policy = _get_model_class(model_name)
        if policy is None:
            return {
                'ok': False,
                'error': f"model '{model_name}' not in allowlist",
                'allowlist': sorted(_MODEL_POLICIES.keys()),
            }
        if model_cls is None:
            return {'ok': False, 'error': f"model '{model_name}' allowlisted but not resolvable via apps.get_model"}

        if action == 'describe_model':
            fields_out = []
            for field in model_cls._meta.get_fields():
                if field.is_relation and not field.many_to_one:
                    continue
                fname = field.name
                sensitive_flag = _is_sensitive_field_name(fname)
                fields_out.append({
                    'name': fname,
                    'type': type(field).__name__,
                    'is_json': isinstance(field, JSONField),
                    'is_text': isinstance(field, TextField),
                    'sensitive_by_name': sensitive_flag,
                    'is_fk': bool(field.many_to_one),
                })
            return {
                'ok': True, 'action': 'describe_model', 'model': model_name,
                'sensitive_model': policy['sensitive'],
                'expensive_text_fields': list(policy.get('expensive_text_fields') or ()),
                'field_count': len(fields_out),
                'fields': fields_out,
            }

        # get + filter share projection args
        requested_fields = payload.get('fields')
        if requested_fields is not None:
            if not isinstance(requested_fields, list) or not all(isinstance(f, str) for f in requested_fields):
                return {'ok': False, 'error': "fields must be a list of strings"}
            requested_fields = set(requested_fields)
        include_json = payload.get('include_json_fields')
        if include_json is None:
            include_json = not policy['sensitive']
        include_json = bool(include_json)

        if action == 'get':
            pk_value = payload.get('pk')
            if pk_value is None or pk_value == '':
                return {'ok': False, 'error': "pk is required for 'get' action"}
            try:
                instance = model_cls.objects.get(pk=pk_value)
            except ObjectDoesNotExist:
                return {'ok': False, 'error': f"no {model_name} row with pk={pk_value}"}
            except (ValueError, TypeError) as e:
                return {'ok': False, 'error': f"invalid pk value '{pk_value}': {e}"}
            row = _serialize_row(instance, model_cls, policy, requested_fields, include_json)
            return {
                'ok': True, 'action': 'get', 'model': model_name,
                'include_json_fields': include_json, 'row': row,
            }

        if action == 'filter':
            filter_kwargs = payload.get('filter_kwargs') or {}
            if not isinstance(filter_kwargs, dict):
                return {'ok': False, 'error': "filter_kwargs must be a dict"}
            err = _validate_filter_kwargs(filter_kwargs, model_cls, policy)
            if err:
                return {'ok': False, 'error': err}

            try:
                limit_raw = int(payload.get('limit') or _DEFAULT_LIMIT)
            except (TypeError, ValueError):
                limit_raw = _DEFAULT_LIMIT
            limit = max(1, min(limit_raw, _MAX_LIMIT))

            order_by = (payload.get('order_by') or '').strip() or None
            if order_by:
                order_field = order_by.lstrip('-')
                model_field_names = {f.name for f in model_cls._meta.get_fields()}
                if order_field not in _COMMON_ORDER_FIELDS:
                    return {
                        'ok': False,
                        'error': f"order_by '{order_field}' not in allowlist {sorted(_COMMON_ORDER_FIELDS)}",
                    }
                if order_field not in model_field_names:
                    return {'ok': False, 'error': f"order_by '{order_field}' not on model {model_name}"}
            else:
                order_field_default = None
                model_field_names = {f.name for f in model_cls._meta.get_fields()}
                for candidate in ('created_at', 'detected_at', 'started_at', 'first_seen'):
                    if candidate in model_field_names:
                        order_field_default = f'-{candidate}'
                        break
                order_by = order_field_default or '-id'

            try:
                queryset = model_cls.objects.filter(**filter_kwargs).order_by(order_by)
                total_matching = queryset.count()
                rows_qs = list(queryset[:limit])
            except FieldError as e:
                return {'ok': False, 'error': f"queryset FieldError: {e}"}
            except (ValueError, TypeError) as e:
                return {'ok': False, 'error': f"queryset value error: {e}"}

            rows = [_serialize_row(inst, model_cls, policy, requested_fields, include_json) for inst in rows_qs]
            return {
                'ok': True, 'action': 'filter', 'model': model_name,
                'include_json_fields': include_json,
                'order_by': order_by,
                'limit': limit,
                'total_matching': total_matching,
                'returned': len(rows),
                'truncated': total_matching > len(rows),
                'rows': rows,
            }

        if action == 'count_by':
            field_name = (payload.get('field') or '').strip()
            if not field_name:
                return {'ok': False, 'error': "field is required for 'count_by' action"}
            err = _validate_groupby_field(field_name, model_cls, policy)
            if err:
                return {'ok': False, 'error': err}

            filter_kwargs = payload.get('filter_kwargs') or {}
            if not isinstance(filter_kwargs, dict):
                return {'ok': False, 'error': "filter_kwargs must be a dict"}
            err = _validate_filter_kwargs(filter_kwargs, model_cls, policy)
            if err:
                return {'ok': False, 'error': err}

            try:
                limit_raw = int(payload.get('limit') or _DEFAULT_GROUP_LIMIT)
            except (TypeError, ValueError):
                limit_raw = _DEFAULT_GROUP_LIMIT
            limit = max(1, min(limit_raw, _MAX_GROUP_LIMIT))

            order_by_count = (payload.get('order_by_count') or 'desc').lower()
            if order_by_count not in ('desc', 'asc'):
                return {'ok': False, 'error': "order_by_count must be 'desc' or 'asc'"}
            count_order_prefix = '-' if order_by_count == 'desc' else ''

            # Resolve the group-by column expression per field type per SIGN Q1+Q2+Q3.
            field_obj = model_cls._meta.get_field(field_name)
            group_key: str
            annotate_kwargs: Dict[str, Any] = {}
            if field_obj.many_to_one:
                # FK — group on attname (<field>_id) per Q3 F-AGREE + serializer parity
                group_key = field_name + '_id'
            elif isinstance(field_obj, DateTimeField):
                # DateTimeField auto-bucket to day per Q2 F-AGREE.
                # Django's DateTimeField extends DateField, so isinstance-DateTimeField
                # alone selects only true datetime columns (plain DateField is
                # already day-grained and falls through to the else branch).
                group_key = '_count_by_day_bucket'
                annotate_kwargs[group_key] = TruncDate(field_name)
            else:
                group_key = field_name

            try:
                filtered_qs = model_cls.objects.filter(**filter_kwargs)
                total_matching = filtered_qs.count()
                grouped_qs = filtered_qs
                if annotate_kwargs:
                    grouped_qs = grouped_qs.annotate(**annotate_kwargs)
                grouped_qs = (
                    grouped_qs
                    .values(group_key)
                    .annotate(_count=Count('id'))
                    .order_by(f'{count_order_prefix}_count', group_key)
                )
                # Materialize +1 beyond limit so we can detect truncation without
                # a second COUNT(DISTINCT) query.
                head_plus_one = list(grouped_qs[:limit + 1])
            except FieldError as e:
                return {'ok': False, 'error': f"queryset FieldError: {e}"}
            except (ValueError, TypeError) as e:
                return {'ok': False, 'error': f"queryset value error: {e}"}

            truncated = len(head_plus_one) > limit
            head_rows = head_plus_one[:limit]
            groups = [
                {'value': _coerce_group_value(row[group_key]), 'count': row['_count']}
                for row in head_rows
            ]
            # group_count semantics: exact distinct-value count when
            # truncated=false; a lower bound (returned + 1) when truncated=true.
            # We intentionally skip a separate COUNT(DISTINCT) query — the
            # `truncated` flag already tells callers to interpret group_count
            # as a lower bound. Post-code SIGN Q4 F-DISAGREE (S2867) dropped
            # a redundant `group_count_is_lower_bound` field that always
            # flipped with `truncated` — the docstring here carries the
            # semantics instead.
            if truncated:
                group_count_reported = len(head_rows) + 1
            else:
                group_count_reported = len(head_rows)

            logger.info(
                "orm_inspect_tool count_by: model=%s field=%s total_matching=%d "
                "group_count=%d returned=%d truncated=%s trace_id=%s",
                model_name, field_name, total_matching,
                group_count_reported, len(groups), truncated, trace_id,
            )

            return {
                'ok': True, 'action': 'count_by', 'model': model_name,
                'field': field_name,
                'group_key': group_key,  # exposes the actual column (e.g., <fk>_id, bucket)
                'total_matching': total_matching,
                'group_count': group_count_reported,  # exact when truncated=false, lower bound when true
                'returned': len(groups),
                'truncated': truncated,
                'order_by_count': order_by_count,
                'limit': limit,
                'groups': groups,
            }

        # Should be unreachable — _VALID_ACTIONS guard covers all branches.
        return {'ok': False, 'error': f"unhandled action '{action}'"}

    def _handle_opportunity_manager(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle opportunity manager tool.

        NOTE: Session 933 audit - Fixed field names:
        - category → opportunity_type
        - score → match_score
        """
        from core.models_unified_system import Opportunity

        action = payload.get('action', 'list')

        # Session 1222 P4 (audit C1) — scope param. Default behavior is
        # unchanged: 'mine' filters by user_id when a caller is
        # authenticated, matching the pre-Session-1222 contract. Passing
        # scope='all' opts into the platform-wide view, surfacing the
        # spider-ingested lead pool (~2,600 system-owned rows as of
        # this writing). Guardrail: explicit opt-in only — chris doesn't
        # accidentally stare at thousands of leads when he asks
        # "what's in my pipeline?".
        scope = (payload.get('scope') or 'mine').lower()
        if scope not in ('mine', 'all'):
            scope = 'mine'

        # Build base queryset - filter by user when scope='mine' (the
        # default, preserving the pre-Session-1222 contract).
        base_qs = Opportunity.objects.all()
        if scope == 'mine' and user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            status = payload.get('status')
            limit = payload.get('limit', 20)

            qs = base_qs
            if status:
                qs = qs.filter(status=status)

            opportunities = list(qs.order_by('-created_at')[:limit].values(
                'id', 'title', 'status', 'opportunity_type', 'match_score', 'created_at'
            ))

            # Session 987: Serialize UUIDs and datetimes for clean display
            for opp in opportunities:
                opp['id'] = str(opp['id'])
                if opp.get('created_at'):
                    opp['created_at'] = opp['created_at'].isoformat()

            return {'action': 'list', 'count': len(opportunities), 'opportunities': opportunities}

        elif action == 'get':
            opp_id = payload.get('opportunity_id') or payload.get('id')
            if not opp_id:
                raise ValueError("opportunity_id is required for get action")
            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                raise ValueError(f"Opportunity {opp_id} not found")
            return {'action': 'get', 'opportunity': {
                'id': str(opp.id), 'title': opp.title, 'status': opp.status,
                'description': opp.description, 'opportunity_type': opp.opportunity_type,
                'match_score': opp.match_score, 'potential_revenue': str(opp.potential_revenue),
            }}

        elif action == 'stats':
            from django.db.models import Count, Sum
            by_status = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
            by_type = dict(base_qs.values('opportunity_type').annotate(c=Count('id')).values_list('opportunity_type', 'c'))
            total_potential = base_qs.aggregate(total=Sum('potential_revenue'))['total'] or 0
            # Session 1222 P4 (audit C1): include an explicit scope label so
            # callers know whether they're seeing the caller-scoped 'your
            # pipeline' view or the un-filtered platform-wide pool. The 2631
            # vs 47 audit confusion came from there being no clear marker
            # on the returned shape. See pa_tool_schemas.py
            # opportunity_manager_tool description.
            response = {
                'action': 'stats',
                'scope': scope,
                'scope_note': (
                    'Filtered to your opportunities (owner=caller, default). '
                    'Pass scope="all" to see the platform-wide lead pool '
                    '(includes spider-ingested rows owned by the system user).'
                    if scope == 'mine'
                    else (
                        'Platform-wide pool — counts every Opportunity row '
                        'regardless of owner. Most rows here are spider-'
                        'ingested job listings owned by the system user; '
                        'check owner_breakdown below for attribution.'
                    )
                ),
                'total': sum(by_status.values()),
                'by_status': by_status,
                'by_type': by_type,
                'total_potential_revenue': str(total_potential),
            }
            if scope == 'all':
                # Session 1222 P4 — Rigby's review tweak. When the caller
                # opts into the platform-wide view, surface the owner
                # breakdown so the 2,600+ row spike is immediately
                # interpretable as "system pool" vs human-owned rows.
                owner_qs = base_qs.values('user_id').annotate(c=Count('id')).order_by('-c')[:10]
                from django.contrib.auth import get_user_model
                _user_model = get_user_model()
                owner_breakdown = []
                for row in owner_qs:
                    uid = row['user_id']
                    uname = '(orphan)'
                    if uid:
                        try:
                            uname = _user_model.objects.get(id=uid).username
                        except _user_model.DoesNotExist:
                            uname = '(deleted user)'
                    owner_breakdown.append({'user': uname, 'count': row['c']})
                response['owner_breakdown'] = owner_breakdown
            return response

        # Session 993: Update opportunity status
        elif action == 'update_status':
            opp_id = payload.get('id') or payload.get('opportunity_id')
            new_status = payload.get('status', '')
            valid_statuses = ['active', 'pending', 'applied', 'accepted', 'rejected', 'expired']

            if not opp_id:
                raise ValueError("id is required for update_status action")
            if new_status not in valid_statuses:
                raise ValueError(f"Invalid status '{new_status}'. Valid: {', '.join(valid_statuses)}")

            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                raise ValueError(f"Opportunity {opp_id} not found")

            old_status = opp.status
            opp.status = new_status
            opp.save(update_fields=['status'])

            return {
                'action': 'update_status',
                'id': str(opp.id),
                'title': opp.title,
                'old_status': old_status,
                'new_status': new_status,
                'success': True,
            }

        elif action == 'create':
            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")
            if not user_id:
                raise ValueError("User context required to create an opportunity")

            from decimal import Decimal, InvalidOperation
            pot_rev = payload.get('potential_revenue', 0)
            try:
                potential_revenue = Decimal(str(pot_rev))
            except (InvalidOperation, TypeError):
                potential_revenue = Decimal('0')

            opp = Opportunity.objects.create(
                user_id=user_id,
                title=title,
                description=payload.get('description', ''),
                opportunity_type=payload.get('opportunity_type', 'general'),
                source=payload.get('source', 'pa'),
                potential_revenue=potential_revenue,
                status='active',
            )
            return {
                'action': 'create',
                'id': str(opp.id),
                'title': opp.title,
                'opportunity_type': opp.opportunity_type,
                'potential_revenue': str(opp.potential_revenue),
                'status': opp.status,
                'success': True,
            }

        elif action == 'delete':
            opp_id = payload.get('id', '') or payload.get('opportunity_id', '')
            if not opp_id:
                raise ValueError("'id' is required for delete action")
            opp = base_qs.filter(id=opp_id).first()
            if not opp:
                return {'action': 'delete', 'success': False, 'error': f'Opportunity {opp_id} not found'}
            title = opp.title
            # Count linked tasks before CASCADE deletes them
            from core.models_unified_system import OpportunityTask as _OT
            task_count = _OT.objects.filter(opportunity=opp).count()
            opp.delete()
            return {
                'action': 'delete', 'success': True,
                'id': str(opp_id), 'title': title,
                'tasks_deleted': task_count,
                'message': f"Deleted opportunity '{title}' and {task_count} linked task(s)",
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, get, stats, update_status, create, delete"
            )

    def _handle_task_manager(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle task manager tool for opportunity-linked tasks."""
        from core.models_unified_system import OpportunityTask

        action = payload.get('action', 'list')

        # Build base queryset - filter by user if available
        base_qs = OpportunityTask.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            status = payload.get('status')
            priority = payload.get('priority')
            limit = payload.get('limit', 20)

            qs = base_qs
            if status:
                qs = qs.filter(status=status)
            if priority:
                qs = qs.filter(priority=priority)

            tasks = list(qs.order_by('-created_at')[:limit].values(
                'id', 'title', 'status', 'priority', 'created_at', 'opportunity_id'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for t in tasks:
                t['id'] = str(t['id'])
                if t.get('opportunity_id'):
                    t['opportunity_id'] = str(t['opportunity_id'])
                if t.get('created_at'):
                    t['created_at'] = t['created_at'].isoformat()

            return {'action': 'list', 'count': len(tasks), 'tasks': tasks}

        elif action == 'stats':
            from django.db.models import Count
            by_status = dict(base_qs.values('status').annotate(c=Count('id')).values_list('status', 'c'))
            by_priority = dict(base_qs.values('priority').annotate(c=Count('id')).values_list('priority', 'c'))
            return {
                'action': 'stats',
                'total': sum(by_status.values()),
                'by_status': by_status,
                'by_priority': by_priority,
            }

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create a task")
            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")

            opp_id = payload.get('opportunity_id')
            opp = None
            if opp_id:
                from core.models_unified_system import Opportunity
                opp = Opportunity.objects.filter(id=opp_id).first()
                if not opp:
                    raise ValueError(f"Opportunity {opp_id} not found")

            if not opp:
                # Create a standalone opportunity to satisfy the required FK
                from core.models_unified_system import Opportunity
                from decimal import Decimal as _TDecimal
                opp = Opportunity.objects.create(
                    user_id=user_id,
                    title=title,
                    description=payload.get('description', ''),
                    opportunity_type='task',
                    source='pa',
                    potential_revenue=_TDecimal('0'),
                    status='active',
                )

            task = OpportunityTask.objects.create(
                user_id=user_id,
                opportunity=opp,
                title=title,
                description=payload.get('description', ''),
                priority=payload.get('priority', 'medium'),
                status='pending',
            )
            return {
                'action': 'create',
                'id': str(task.id),
                'title': task.title,
                'priority': task.priority,
                'opportunity_id': str(opp.id),
                'success': True,
            }

        elif action == 'update':
            task_id = payload.get('id')
            if not task_id:
                raise ValueError("'id' is required for update action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            update_fields = []
            if payload.get('status'):
                task.status = payload['status']
                update_fields.append('status')
            if payload.get('priority'):
                task.priority = payload['priority']
                update_fields.append('priority')
            if payload.get('title'):
                task.title = payload['title']
                update_fields.append('title')
            # Session 1228 PR-A — switched from `is not None` to key-in-payload
            # guard. GPT-5.2 autofills declared optional string params with ''
            # (mirror of the bool=False / int=0 autofill class). Falsy-string
            # gate so an LLM autofill of '' doesn't silently clear an existing
            # task description. Empty description requires explicit `clear` UX.
            if payload.get('description'):
                task.description = payload['description']
                update_fields.append('description')

            if update_fields:
                task.save(update_fields=update_fields)

            return {
                'action': 'update',
                'id': str(task.id),
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'updated_fields': update_fields,
                'success': True,
            }

        elif action == 'complete':
            task_id = payload.get('id')
            if not task_id:
                raise ValueError("'id' is required for complete action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                raise ValueError(f"Task {task_id} not found")

            old_status = task.status
            task.status = 'won'
            task.save(update_fields=['status'])

            return {
                'action': 'complete',
                'id': str(task.id),
                'title': task.title,
                'old_status': old_status,
                'new_status': 'won',
                'success': True,
            }

        elif action == 'delete':
            task_id = payload.get('id', '').strip()
            if not task_id:
                raise ValueError("'id' is required for delete action")
            task = base_qs.filter(id=task_id).first()
            if not task:
                return {'action': 'delete', 'success': False, 'error': f'Task {task_id} not found'}
            title = task.title
            task.delete()
            return {'action': 'delete', 'success': True, 'id': task_id, 'title': title, 'message': f"Deleted task '{title}'"}

        else:
            raise ValueError(f"Unknown action: {action}. Valid: list, stats, create, update, complete, delete")

    def _handle_pipeline_orchestrator(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle pipeline orchestrator tool.

        NOTE: Session 933 audit - This is a status-only stub.
        The actual pipeline orchestration happens via Celery tasks and
        the Initiative pipeline (5 stages). This tool provides status visibility.
        """
        from core.models import Initiative
        from django.db.models import Count

        action = payload.get('action', 'status')

        if action == 'status':
            # Get real pipeline stats from Initiative model
            # Initiative.status uses UPPERCASE values ('ACTIVE' not 'active')
            total = Initiative.objects.count()
            by_stage = {}
            for stage in range(1, 6):
                by_stage[f'stage_{stage}'] = Initiative.objects.filter(current_stage=stage).count()
            active = Initiative.objects.filter(current_stage__lt=5, status='ACTIVE').count()

            # Add status breakdown for visibility
            by_status = dict(
                Initiative.objects.values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            )

            return {
                'action': 'status',
                'pipeline': 'operational',
                'initiatives_total': total,
                'initiatives_active': active,
                'by_stage': by_stage,
                'by_status': by_status,
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_revenue_tracker(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle revenue tracker tool.

        NOTE: Session 933 audit - Wired to real Revenue model in core/models.py
        """
        from core.models import Revenue
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'stats')

        # Build base queryset - filter by user if available
        base_qs = Revenue.objects.all()
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'stats':
            # Get total revenue
            total = base_qs.aggregate(total=Sum('amount'))['total'] or 0

            # Get by source
            by_source = dict(
                base_qs.values('source_type').annotate(
                    total=Sum('amount')
                ).values_list('source_type', 'total')
            )

            # Get by status
            by_status = dict(
                base_qs.values('status').annotate(
                    c=Count('id')
                ).values_list('status', 'c')
            )

            # Get recent (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_total = base_qs.filter(
                created_at__gte=thirty_days_ago
            ).aggregate(total=Sum('amount'))['total'] or 0

            return {
                'action': 'stats',
                'total_revenue': str(total),
                'revenue_last_30_days': str(recent_total),
                'by_source': {k: str(v) for k, v in by_source.items()},
                'by_status': by_status,
                'record_count': base_qs.count(),
            }

        elif action == 'list':
            limit = payload.get('limit', 20)
            revenues = list(base_qs.order_by('-created_at')[:limit].values(
                'id', 'amount', 'source_type', 'status', 'created_at', 'description'
            ))

            # Session 987: Serialize UUIDs and datetimes
            for r in revenues:
                r['id'] = str(r['id'])
                if r.get('created_at'):
                    r['created_at'] = r['created_at'].isoformat()

            return {'action': 'list', 'count': len(revenues), 'revenues': revenues}

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create revenue record")

            from decimal import Decimal, InvalidOperation
            try:
                amount = Decimal(str(payload.get('amount', 0)))
            except (InvalidOperation, TypeError):
                raise ValueError("'amount' must be a valid number")
            if amount <= 0:
                raise ValueError("'amount' must be positive")

            source_type = payload.get('source', payload.get('source_type', 'other')).strip()
            description = payload.get('description', '').strip()
            status = payload.get('status', 'confirmed')

            rev = Revenue.objects.create(
                user_id=user_id,
                amount=amount,
                source_type=source_type,
                description=description,
                status=status,
            )
            return {
                'action': 'create',
                'id': str(rev.id),
                'amount': str(rev.amount),
                'source_type': rev.source_type,
                'status': rev.status,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, list, create")

    def _handle_ml_analysis(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle ML analysis tool.

        NOTE: Session 933 audit - MLEngine doesn't have generic 'analyze' method.
        Available actions: status, decision_pattern, detect_opportunity
        """
        from ml.core.ml_engine import MLEngine

        action = payload.get('action', 'status')

        engine = MLEngine()

        if action == 'status':
            # Get ML engine system health
            health = engine.get_system_health()
            return {
                'action': 'status',
                'engine': 'MLEngine',
                'health': health,
            }

        elif action == 'decision_pattern':
            # Analyze user decision pattern
            decision_data = payload.get('data', {})
            if not decision_data:
                raise ValueError("data is required for decision_pattern analysis")
            confidence = engine.analyze_user_decision_pattern(decision_data)
            return {
                'action': 'decision_pattern',
                'confidence': confidence,
                'data': decision_data,
            }

        elif action == 'detect_opportunity':
            # Detect cross-domain opportunities
            market_data = payload.get('data', {})
            if not market_data:
                raise ValueError("data (market_data) is required for detect_opportunity")
            opportunities = engine.detect_cross_domain_opportunity(market_data)
            return {
                'action': 'detect_opportunity',
                'opportunities': [o.__dict__ for o in opportunities] if opportunities else [],
                'count': len(opportunities) if opportunities else 0,
            }

        else:
            # Return available actions
            return {
                'action': action,
                'error': f"Unknown action: {action}",
                'available_actions': ['status', 'decision_pattern', 'detect_opportunity'],
            }

    def _handle_universal_agent(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle universal agent tool - invoke agent by name or auto-route.

        Session 1088: Converted to Celery async dispatch (same pattern as
        _handle_agent_tool) to eliminate 60s PA timeouts.
        """
        from core.tasks import execute_agent_task
        from core.agent_router import AgentRouter

        agent_name = payload.get('agent_name', '')
        task_text = payload.get('task', '')
        context = payload.get('context', {})

        # Session 1094: promote top-level `content` and `workspace_id` params
        # into context so they reach the agent. Schema exposes these as
        # structured parameters (see pa_tool_schemas.py run_agent) because
        # GPT-5.2 routing is unreliable about passing arbitrary fields inside
        # the `context` blob. Top-level wins if both provided — caller's
        # structured intent is more trustworthy than LLM-assembled context.
        top_level_content = payload.get('content')
        if top_level_content and 'content' not in context:
            context['content'] = top_level_content
        top_level_ws = payload.get('workspace_id')
        if top_level_ws and 'workspace_id' not in context:
            context['workspace_id'] = top_level_ws
        # Session 1174 PR-1: promote conversation_id too. The PA entrypoint
        # injects it at the payload root (unified_pa_entrypoint.py:1549) for
        # every tool call; _handle_agent_tool gets it via _CONTEXT_PROMOTE_KEYS
        # but this universal-agent handler doesn't share that promotion. Without
        # this line, universal_agent_tool dispatches would persist NULL on
        # AgentExecution.conversation_id and silently opt out of the follow-up
        # wake design.
        top_level_conv = payload.get('conversation_id')
        if top_level_conv and 'conversation_id' not in context:
            context['conversation_id'] = top_level_conv

        # Session 1178 Phase 2 — auto-wake opt-out kwarg. Same plumbing pattern
        # as conversation_id above; this handler doesn't share _CONTEXT_PROMOTE_KEYS
        # with _handle_agent_tool, so promote explicitly. False is meaningful
        # (skip auto-sub), so test for membership rather than truthiness.
        if 'auto_followup' in payload and 'auto_followup' not in context:
            context['auto_followup'] = payload['auto_followup']

        if not task_text:
            raise ValueError("task is required")

        # Session 2728 F-RA-2/F-RA-3 — track the caller's originally-requested
        # agent_name so we can surface substitution in the dispatch response.
        # Prior behavior silently substituted unknown agents to 'ResearchAgent'
        # (WARN log only); Rigby had no response-side signal that the executed
        # agent differed from the requested one. Chris ratified option (a) at
        # Batch A tool 5 close: additive fields mirroring the F-D-2/F-D-4
        # inference-envelope pattern.
        _agent_name_requested = payload.get('agent_name') or None

        # GPT often passes tool names (snake_case) instead of agent class names
        if agent_name and '_' in agent_name:
            agent_name = self._tool_to_agent_name(agent_name)

        # Session 1088: Validate agent name against AGENT_MAP and auto-extract
        # from task text if the name is invalid (e.g. LLM sends 'RunAgent' or
        # other hallucinated names via keyword routing without schema).
        _substitution_reason = None
        router = AgentRouter()
        if agent_name and agent_name not in router.AGENT_MAP:
            # Try to find actual agent name in the task text
            extracted = None
            for name in router.AGENT_MAP:
                if name.lower() in task_text.lower():
                    extracted = name
                    break
            if extracted:
                logger.info(f"[run_agent] Corrected '{agent_name}' -> '{extracted}' from task text")
                _substitution_reason = f"agent_name '{agent_name}' not in AGENT_MAP; extracted '{extracted}' from task text"
                agent_name = extracted
            else:
                logger.warning(f"[run_agent] Unknown agent '{agent_name}', no match in task text, defaulting to ResearchAgent")
                _substitution_reason = f"agent_name '{agent_name}' not in AGENT_MAP; no task-text match; defaulted to ResearchAgent"
                agent_name = 'ResearchAgent'

        # Auto-route to best agent when no name given
        if not agent_name:
            for name in router.AGENT_MAP:
                if name.lower() in task_text.lower():
                    agent_name = name
                    break
            if not agent_name:
                agent_name = 'ResearchAgent'

        if user_id:
            context['user_id'] = str(user_id)

        # Session 1088: Route to long_running (matches CELERY_TASK_ROUTES in settings).
        # Was hardcoded to 'agents' queue which no worker consumes.
        celery_task = execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='long_running')

        # Session 2728 F-RA-1 — surface auto_followup + follow_up_will_fire
        # (mirrors F-CC-3 approved at Batch A tool 4). Same task-side gate
        # as `_handle_agent_tool` in tool_dispatcher.py:1215-1237.
        _auto_followup = context.get('auto_followup', True)
        _auto_followup_effective = _auto_followup is not False
        _conv_id_for_followup = context.get('conversation_id')
        _follow_up_will_fire = bool(_conv_id_for_followup) and _auto_followup_effective

        # Session 2728 F-RA-2/F-RA-3 — build substitution envelope. Substitution
        # fires when caller requested a specific agent name and the effective
        # agent differs; the `auto_routed` field (unchanged) still signals the
        # no-name-given path.
        _agent_substituted = bool(
            _agent_name_requested
            and _agent_name_requested != agent_name
        )
        _response = {
            'task_id': str(celery_task.id),
            'mode': 'async',
            'agent': agent_name,
            'agent_name_requested': _agent_name_requested,
            'agent_name_effective': agent_name,
            'agent_substituted': _agent_substituted,
            'auto_routed': not payload.get('agent_name'),
            'auto_followup': _auto_followup_effective,
            'follow_up_will_fire': _follow_up_will_fire,
            'message': (
                f'{agent_name} dispatched (task {celery_task.id}). '
                f'Use job_status to check progress.'
            ),
        }
        if _substitution_reason:
            _response['substitution_reason'] = _substitution_reason
        return _response

    def _serialize_workspace(self, workspace) -> Dict[str, Any]:
        """Return a compact workspace summary for tool responses."""
        return {
            'id': str(workspace.id),
            'name': workspace.name,
            'description': workspace.description or '',
            'workspace_type': workspace.workspace_type,
            'root_path': workspace.root_path,
            'is_active': workspace.is_active,
            'current_branch': workspace.current_branch or '',
            'total_operations': workspace.total_operations,
            'total_files_written': workspace.total_files_written,
            'last_operation_at': workspace.last_operation_at.isoformat() if workspace.last_operation_at else None,
        }

    def _resolve_workspace_for_payload(
        self,
        manager,
        user_id: Optional[int],
        payload: Dict[str, Any],
        allow_active_fallback: bool = True,
    ):
        """Resolve the workspace to operate on, favoring an explicit workspace_id."""
        from core.models_skin_layer import ProjectWorkspace

        workspace_id = str(payload.get('workspace_id') or payload.get('workspace') or '').strip()
        if workspace_id:
            workspace = ProjectWorkspace.objects.filter(user_id=user_id, id=workspace_id).first()
            if workspace:
                return workspace, None
            return None, f'Workspace not found: {workspace_id}'

        if allow_active_fallback:
            workspace = manager.get_active_workspace()
            if workspace:
                return workspace, None

        return None, 'No active workspace'

    def _handle_workspace(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle workspace tool."""
        from core.services.workspace_manager import get_workspace_manager
        from django.contrib.auth import get_user_model

        action = payload.get('action', 'list')
        User = get_user_model()
        user = User.objects.filter(id=user_id).first() if user_id else None
        manager = get_workspace_manager(user)

        if action == 'list':
            workspaces = manager.list_workspaces()
            # Support name filter for search
            name_filter = payload.get('name', '').strip()
            if name_filter:
                workspaces = [ws for ws in workspaces if name_filter.lower() in ws.name.lower()]
            # Apr 2026: Pagination support — offset/limit to avoid truncation
            total_count = len(workspaces)
            offset = int(payload.get('offset', 0))
            limit = int(payload.get('limit', 50))
            workspaces = workspaces[offset:offset + limit]
            serialized = []
            for ws in workspaces:
                ws_data = {
                    'id': str(ws.id),
                    'name': ws.name,
                    'description': ws.description or '',
                    'workspace_type': ws.workspace_type,
                    'root_path': ws.root_path,
                    'is_active': ws.is_active,
                    'current_branch': ws.current_branch or '',
                    'total_operations': ws.total_operations,
                    'last_operation_at': ws.last_operation_at.isoformat() if ws.last_operation_at else None,
                }
                # Include config info if available
                config = getattr(ws, 'config', None)
                if config:
                    ws_data['template'] = config.template.name if config.template else None
                    ws_data['business_status'] = config.status
                    ws_data['has_brief'] = bool(config.workspace_brief)
                serialized.append(ws_data)
            return {
                'action': 'list',
                'workspaces': serialized,
                'count': len(serialized),
                'total': total_count,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total_count,
            }

        elif action == 'get':
            # Direct lookup by ID or name
            from core.models_skin_layer import ProjectWorkspace
            workspace_id = payload.get('workspace_id', '').strip()
            workspace_name = payload.get('name', '').strip()

            ws = None
            if workspace_id:
                ws = ProjectWorkspace.objects.filter(user_id=user_id, id=workspace_id).first()
            elif workspace_name:
                ws = ProjectWorkspace.objects.filter(user_id=user_id, name__icontains=workspace_name).first()

            if not ws:
                return {'action': 'get', 'error': f'Workspace not found: {workspace_id or workspace_name}'}

            config = getattr(ws, 'config', None)
            result = {
                'action': 'get',
                **self._serialize_workspace(ws),
            }
            if config:
                result['template'] = config.template.name if config.template else None
                result['business_status'] = config.status
                result['workspace_brief'] = config.workspace_brief
                result['pipeline_config'] = config.pipeline_config
                result['agent_pool'] = config.agent_pool

            # Recent pipeline runs
            from core.models_workspace_templates import PipelineRun
            recent_runs = PipelineRun.objects.filter(workspace=ws).order_by('-created_at')[:3]
            result['recent_pipeline_runs'] = [{
                'id': str(r.id),
                'status': r.status,
                'created_at': r.created_at.isoformat(),
                'stage_count': len(r.pipeline_snapshot),
            } for r in recent_runs]

            # Deliverable count
            from core.models_deliverables import Deliverable
            result['deliverable_count'] = Deliverable.objects.filter(workspace=ws).count()

            return result

        elif action == 'status':
            workspaces = manager.list_workspaces()
            active = [ws for ws in workspaces if ws.is_active]
            return {
                'action': 'status',
                'total_workspaces': len(workspaces),
                'active_workspace': self._serialize_workspace(active[0]) if active else None,
            }

        elif action == 'create':
            from core.models_skin_layer import ProjectWorkspace
            import os

            name = payload.get('name', '').strip()
            if not name:
                raise ValueError("'name' is required for create action")

            description = payload.get('description', '')

            # Check for duplicate name
            existing = ProjectWorkspace.objects.filter(user_id=user_id, name=name).first()
            if existing:
                return {
                    'action': 'create',
                    'created': False,
                    'id': str(existing.id),
                    'name': existing.name,
                    'message': f"Workspace '{name}' already exists",
                }

            # Create sandbox workspace (no filesystem path required)
            base_dir = os.environ.get('WORKSPACE_BASE_DIR', '/app/workspaces')
            root_path = os.path.join(base_dir, name.lower().replace(' ', '-'))

            workspace = ProjectWorkspace.objects.create(
                user_id=user_id,
                name=name,
                description=description,
                workspace_type='sandbox',
                root_path=root_path,
                is_active=True,
            )

            return {
                'action': 'create',
                'created': True,
                'id': str(workspace.id),
                'name': workspace.name,
                'description': workspace.description,
                'workspace_type': workspace.workspace_type,
                'message': f"Created workspace '{name}'",
            }

        elif action == 'scan':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'scan', 'success': False, 'error': error}

            context = manager.rescan_workspace(workspace)
            return {
                'action': 'scan',
                'success': True,
                'message': f"Scanned workspace: {workspace.name}",
                'workspace': self._serialize_workspace(workspace),
                'stats': {
                    'total_files': context.total_files,
                    'total_directories': context.total_directories,
                    'total_lines_of_code': context.total_lines_of_code,
                    'file_types': context.file_type_counts,
                    'scan_duration_ms': context.scan_duration_ms,
                },
                'context': {
                    # Session 1246 audit fix: workspace_name / root_path /
                    # tech_stack live on the related ProjectWorkspace, not on
                    # WorkspaceContext itself. The old direct attribute access
                    # crashed scan with `'WorkspaceContext' object has no
                    # attribute 'workspace_name'`, breaking FilesTab (S1247
                    # audit deliverable 1c3e63ec-…). Route through the FK.
                    'workspace_name': context.workspace.name,
                    'root_path': context.workspace.root_path,
                    'tech_stack': context.workspace.tech_stack,
                    'key_files': context.key_files,
                    'total_files': context.total_files,
                    'total_directories': context.total_directories,
                },
            }

        elif action == 'read':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'read', 'success': False, 'error': error}

            path = payload.get('path', '').strip()
            if not path:
                return {'action': 'read', 'success': False, 'error': 'path is required for read action'}

            try:
                manager.file_writer._resolve_workspace_path(workspace, path)
            except ValueError as e:
                return {'action': 'read', 'success': False, 'error': str(e)}

            content = manager.read_file(workspace, path)
            if content is None:
                return {'action': 'read', 'success': False, 'error': f'File not found: {path}'}

            max_chars = min(int(payload.get('max_chars') or 50000), 50000)  # Session 1228 PR-B autofill safety
            return {
                'action': 'read',
                'success': True,
                'workspace': self._serialize_workspace(workspace),
                'file_path': path,
                'content': content[:max_chars],
                'truncated': len(content) > max_chars,
            }

        elif action == 'write':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'write', 'success': False, 'error': error}

            path = payload.get('path', '').strip()
            content = payload.get('content')
            agent_name = payload.get('agent_name', 'PersonalAssistant')
            agent_task = payload.get('task', '') or payload.get('message', '')

            if not path:
                return {'action': 'write', 'success': False, 'error': 'path is required for write action'}
            if content is None:
                return {'action': 'write', 'success': False, 'error': 'content is required for write action'}

            try:
                manager.file_writer._resolve_workspace_path(workspace, path)
            except ValueError as e:
                return {'action': 'write', 'success': False, 'error': str(e)}

            operation = manager.write_file(workspace, path, content, agent_name, agent_task)
            return {
                'action': 'write',
                'success': operation.success,
                'message': f"{'Wrote' if operation.success else 'Failed to write'} {path}",
                'workspace': self._serialize_workspace(workspace),
                'operation_id': str(operation.id),
                'file_path': operation.file_path,
                'error': operation.error_message if not operation.success else None,
            }

        elif action == 'git_status':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'git_status', 'success': False, 'error': error}

            status = manager.git_status(workspace)
            return {
                'action': 'git_status',
                'success': True,
                'workspace': self._serialize_workspace(workspace),
                'git_status': status,
            }

        elif action == 'git_commit':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'git_commit', 'success': False, 'error': error}

            message = payload.get('message', '').strip()
            agent_name = payload.get('agent_name', 'PersonalAssistant')
            if not message:
                return {'action': 'git_commit', 'success': False, 'error': 'message is required for git_commit'}

            operation = manager.git_commit(workspace, message, agent_name)
            return {
                'action': 'git_commit',
                'success': operation.success,
                'message': f"{'Committed' if operation.success else 'Failed to commit'}: {message[:50]}...",
                'workspace': self._serialize_workspace(workspace),
                'operation_id': str(operation.id),
                'error': operation.error_message if not operation.success else None,
            }

        elif action == 'git_branch':
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'git_branch', 'success': False, 'error': error}

            branch_name = payload.get('branch_name', '').strip()
            agent_name = payload.get('agent_name', 'PersonalAssistant')
            if not branch_name:
                return {'action': 'git_branch', 'success': False, 'error': 'branch_name is required'}

            operation = manager.git_create_branch(workspace, branch_name)
            return {
                'action': 'git_branch',
                'success': operation.success,
                'message': f"{'Created branch' if operation.success else 'Failed'}: {branch_name}",
                'workspace': self._serialize_workspace(workspace),
                'operation_id': str(operation.id),
                'error': operation.error_message if not operation.success else None,
                'agent_name': agent_name,
            }

        elif action == 'operations':
            # Session 1246 audit fix: WorkspaceOperation was never imported in
            # this file (every other model in this handler uses inline scoped
            # imports — ProjectWorkspace appears 7 times the same way). The
            # `operations` action branch raised NameError on every call.
            # S1247 workspace tab audit deliverable 1c3e63ec-… caught it.
            from core.models_skin_layer import WorkspaceOperation
            workspace, error = self._resolve_workspace_for_payload(manager, user_id, payload)
            if error:
                return {'action': 'operations', 'success': False, 'error': error}

            limit = min(int(payload.get('limit', 10)), 100)
            offset = max(int(payload.get('offset', 0)), 0)

            ops_qs = WorkspaceOperation.objects.filter(workspace=workspace).order_by('-created_at')
            total = ops_qs.count()
            ops = ops_qs[offset:offset + limit]

            return {
                'action': 'operations',
                'success': True,
                'workspace': self._serialize_workspace(workspace),
                'operations': [
                    {
                        'id': str(op.id),
                        'type': op.operation_type,
                        'agent': op.agent_name,
                        'file_path': op.file_path,
                        'success': op.success,
                        'created_at': op.created_at.isoformat(),
                        'can_rollback': op.can_rollback and not op.rolled_back,
                        'rolled_back': op.rolled_back,
                        'requires_review': op.requires_review,
                        'reviewed_by_human': op.reviewed_by_human,
                    }
                    for op in ops
                ],
                'count': len(ops),
                'total': total,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total,
            }

        elif action == 'rollback':
            workspace, error = self._resolve_workspace_for_payload(
                manager, user_id, payload, allow_active_fallback=False
            )
            if error:
                return {'action': 'rollback', 'success': False, 'error': error}

            confirm_rollback = payload.get('confirm_rollback')
            if confirm_rollback not in (True, 'true', 'True', 1, '1'):
                return {
                    'action': 'rollback',
                    'success': False,
                    'error': 'confirm_rollback=true is required before rolling back an operation',
                }

            operation_id = str(payload.get('operation_id', '')).strip()
            if not operation_id:
                return {'action': 'rollback', 'success': False, 'error': 'operation_id is required for rollback'}

            # Session 1246: same missing import as the `operations` branch above.
            from core.models_skin_layer import WorkspaceOperation
            operation = WorkspaceOperation.objects.filter(id=operation_id, user_id=user_id).first()
            if not operation:
                return {'action': 'rollback', 'success': False, 'error': f'Operation not found: {operation_id}'}

            if operation.workspace_id != workspace.id:
                return {
                    'action': 'rollback',
                    'success': False,
                    'error': 'Operation does not belong to the active workspace',
                }

            rollback_op = manager.rollback_operation(operation)
            return {
                'action': 'rollback',
                'success': rollback_op.success,
                'message': f"{'Rolled back' if rollback_op.success else 'Failed to rollback'} operation",
                'workspace': self._serialize_workspace(workspace),
                'original_operation_id': str(operation.id),
                'rollback_operation_id': str(rollback_op.id),
                'error': rollback_op.error_message if not rollback_op.success else None,
            }

        elif action == 'update':
            # Session 2967 Slice 7 — Ledger #22 discharge. Before this action
            # existed, any workspace attribute drift (root_path after repo move,
            # rename, description edit, business_status transition) required
            # raw ORM. Rigby's tool surface IS the A1 SaaS product surface, so
            # every gap she hits a customer hits. See feedback_rigby_tool_gap_ledger.
            from core.models_skin_layer import ProjectWorkspace
            import os as _os

            ws_id = (payload.get('workspace_id') or payload.get('id') or '').strip()
            if not ws_id:
                return {'action': 'update', 'success': False, 'error': "'workspace_id' is required for update action"}

            ws = ProjectWorkspace.objects.filter(user_id=user_id, id=ws_id).first()
            if not ws:
                return {'action': 'update', 'success': False, 'error': f'Workspace {ws_id} not found (or not owned by caller)'}

            # Collect requested mutations. `new_name` maps to `name` on the model
            # (the `name` payload key is reserved for lookup on other actions).
            updatable = {
                'root_path': payload.get('root_path'),
                'name': payload.get('new_name'),
                'description': payload.get('description'),
                'workspace_type': payload.get('workspace_type'),
            }
            updates = {k: v for k, v in updatable.items() if v is not None and str(v).strip() != ''}

            # business_status lives on the related WorkspaceConfig, not the workspace row itself.
            # A2 SIGN bug catch: Rigby's PA function-calling layer serializes missing string
            # params as "" (not None), so `if business_status is not None` incorrectly
            # treated absent-in-payload as intentional-clear-to-empty. Require a truthy
            # value; callers who genuinely want to blank the field can pass a whitespace
            # sentinel or (better) use a future explicit `clear_business_status=true` flag.
            business_status_raw = payload.get('business_status')
            business_status = business_status_raw if (business_status_raw is not None and str(business_status_raw).strip() != '') else None
            config_update_applied = False

            if not updates and business_status is None:
                return {
                    'action': 'update',
                    'success': False,
                    'error': 'No update fields provided. Supported: root_path, new_name, description, workspace_type, business_status',
                }

            # Validate root_path exists on disk before persisting (prevents the
            # exact regression that triggered Ledger #22 — pointing at a
            # nonexistent directory silently breaks claude_code_tool + workspace
            # read/write/scan).
            if 'root_path' in updates:
                new_root = str(updates['root_path']).strip()
                if not new_root:
                    return {'action': 'update', 'success': False, 'error': 'root_path cannot be empty'}
                if not _os.path.isdir(new_root):
                    return {'action': 'update', 'success': False, 'error': f'root_path does not exist on disk: {new_root}'}
                updates['root_path'] = new_root

            # Snapshot old values for the audit-trail envelope.
            old_values = {field: getattr(ws, field, None) for field in updates.keys()}
            for field, val in updates.items():
                setattr(ws, field, val)
            if updates:
                ws.save(update_fields=list(updates.keys()))

            # Apply business_status on the config row if present.
            if business_status is not None:
                config = getattr(ws, 'config', None)
                if config is not None:
                    old_values['business_status'] = config.status
                    config.status = business_status
                    config.save(update_fields=['status'])
                    updates['business_status'] = business_status
                    config_update_applied = True
                else:
                    updates['business_status_skipped'] = 'no WorkspaceConfig row exists for this workspace'

            return {
                'action': 'update',
                'success': True,
                'id': str(ws.id),
                'name': ws.name,
                'updates': updates,
                'old_values': old_values,
                'config_update_applied': config_update_applied,
                'message': f"Updated workspace '{ws.name}' ({len(updates)} field(s))",
            }

        elif action == 'delete':
            from core.models_skin_layer import ProjectWorkspace

            ws_id = payload.get('id', '').strip()
            if not ws_id:
                raise ValueError("'id' is required for delete action")

            ws = ProjectWorkspace.objects.filter(user_id=user_id, id=ws_id).first()
            if not ws:
                return {'action': 'delete', 'success': False, 'error': f'Workspace {ws_id} not found'}

            # Safety: only allow deleting sandbox workspaces owned by user
            if ws.workspace_type != 'sandbox':
                return {'action': 'delete', 'success': False, 'error': 'Only sandbox workspaces can be deleted'}
            if user_id and ws.user_id and ws.user_id != user_id:
                return {'action': 'delete', 'success': False, 'error': 'Cannot delete another user\'s workspace'}

            name = ws.name
            ws.delete()
            return {'action': 'delete', 'success': True, 'name': name, 'message': f"Deleted workspace '{name}'"}

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: "
                "list, get, status, create, update, delete, scan, read, write, "
                "git_status, git_commit, git_branch, operations, rollback"
            )

    def _handle_deliverables(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle deliverables library tool."""
        from core.models_deliverables import Deliverable
        from django.db.models import Count
        import uuid as _uuid_mod

        # S3038-S8 — Structured intent log at handler entry. Paired with
        # [PA_DELIVERABLES_ENVELOPE] emitted from the create branch's
        # try/finally. Cross-reference trace_id against Deliverable rows to
        # isolate the Rigby persistence-gap class:
        #   - 0 INTENT logs for a dispatch → PA loop never reached the handler
        #     (LLM never emitted deliverable_tool call — prompt convergence /
        #     PA_TASK_SUMMARY shows tools=... with no deliverable_tool).
        #   - INTENT logged, no ENVELOPE for same trace_id → handler raised
        #     before hitting the create branch's finally (unlikely — action
        #     dispatch is above the create-specific try/finally).
        #   - INTENT + ENVELOPE(ok=False) → handler ran, validation/gate
        #     rejected; error_code names the class.
        #   - INTENT + ENVELOPE(ok=True) + no Deliverable row → factory silent
        #     drop despite raise_on_gated=True (contract violation, unlikely).
        logger.info(
            "[PA_DELIVERABLES_INTENT] trace_id=%s tool=%s raw_action=%r "
            "title=%r workspace_id=%s user_id=%s payload_keys=%s",
            trace_id, tool_name,
            payload.get('action', 'list'),
            (payload.get('title') or '')[:80],
            payload.get('workspace_id') or payload.get('workspace') or 'none',
            user_id,
            sorted(payload.keys()),
        )

        # Apr 2026: Sanitize UUID fields — GPT-5.2 sometimes injects its tool
        # call ID (e.g. "tool-1-6a55c355") into UUID fields like id, workspace_id,
        # initiative_id, causing Django ORM validation errors.
        for uuid_field in ('id', 'workspace_id', 'workspace', 'initiative_id', 'deliverable_id'):
            val = payload.get(uuid_field, '')
            if val and isinstance(val, str):
                try:
                    _uuid_mod.UUID(val)
                except ValueError:
                    logger.warning(f"[deliverables] Sanitized invalid UUID in '{uuid_field}': {val}")
                    payload[uuid_field] = ''

        action = payload.get('action', 'list')

        # Session 1077+: Smart action inference — GPT-5.2 sometimes drops the
        # action field or defaults to 'list' even when title+content indicate create.
        # Session 2728 F-D-2/F-D-4 — inference is now consolidated at the
        # direct-dispatcher (layer 1, `_handle_deliverable_direct` in
        # td_handlers_content.py) which surfaces `original_action` +
        # `inferred_action` in the response envelope. The layer-2 block here
        # remains as a defence-in-depth safety net for callers that reach
        # `_handle_deliverables` outside the PA gateway path (some legacy
        # tests + `deliverables_tool` legacy schema); it now marks
        # `_action_inferred_at_layer_2` so response injection works even on
        # the direct path.
        _action_original_at_l2 = payload.get('action', 'list')
        _action_inferred_at_l2 = False
        if action == 'list':
            has_title = bool(payload.get('title', ''))
            has_content = bool(payload.get('content', ''))
            if has_title and has_content:
                action = 'create'
                _action_inferred_at_l2 = True
                logger.info(f"[deliverables] Inferred action=create from title+content (was 'list')")
            elif has_content and payload.get('id'):
                action = 'append'
                _action_inferred_at_l2 = True
                logger.info(f"[deliverables] Inferred action=append from id+content (was 'list')")

        # Session 2728 F-D-5 / S2730 F-RL-2 — list/search limit is capped
        # at 50; when a caller requests more, the response spreads
        # `**_envelope` from the shared `compute_limit` helper so Rigby
        # sees the `limit_capped/requested_limit/effective_limit/hard_max`
        # F-D-5 shape.
        from core.services.td_limit_envelope import compute_limit
        limit, _envelope = compute_limit(payload, default=10, hard_max=50)
        offset = max(payload.get('offset', 0), 0)

        # Build base queryset scoped to user
        # Session 1075: Include user-owned AND unowned (user=NULL) deliverables.
        # Agents in Celery create deliverables with user=NULL (or the real user
        # after the _save_to_deliverable fix). Include both so PA can always
        # find agent-created content.
        from django.db.models import Q
        base_qs = Deliverable.objects.all()
        # If workspace_id is in payload, scope to workspace (skip user filter — workspace is authoritative)
        ws_scope = payload.get('workspace_id') or payload.get('workspace')

        # Fallback: if no workspace in payload, check user's AssistantProfile
        # for workspace scoping. Session 1103c: was 'except Exception: pass'
        # which silently dropped workspace scoping on any DB hiccup, so PA
        # deliverable queries from the user ran unscoped and could return
        # cross-workspace deliverables.
        if not ws_scope and user_id:
            try:
                from core.models_assistant_profile import AssistantProfile
                ap = AssistantProfile.objects.filter(user_id=user_id).first()
                if ap and ap.workspace_id:
                    ws_scope = str(ap.workspace_id)
                    logger.info(f"[deliverables] Workspace from AssistantProfile: {ws_scope}")
            except Exception as e:
                logger.warning(
                    "[deliverables] AssistantProfile workspace lookup failed "
                    "for user_id=%s (%s: %s) — PA deliverable query will run "
                    "unscoped and may return cross-workspace results",
                    user_id, type(e).__name__, e,
                )

        logger.info(f"[deliverables] workspace_scope={ws_scope} user_id={user_id}")
        if ws_scope:
            base_qs = base_qs.filter(workspace_id=ws_scope)
            logger.info(f"[deliverables] Filtered to workspace {ws_scope}: {base_qs.count()} items")
        elif user_id:
            # PA service account and staff/superusers see all deliverables
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                requesting_user = User.objects.get(id=user_id)
                is_pa_or_staff = (
                    requesting_user.is_staff
                    or requesting_user.is_superuser
                    or requesting_user.username == 'pa-service'
                )
            except User.DoesNotExist:
                is_pa_or_staff = False

            if not is_pa_or_staff:
                base_qs = base_qs.filter(Q(user_id=user_id) | Q(user__isnull=True))
                logger.info(f"[deliverables] Filtered to user_id {user_id} + NULL: {base_qs.count()} items")
            else:
                logger.info(f"[deliverables] Staff/PA user — showing all {base_qs.count()} items")

        # Session 1227 — show_all flag bypasses the optional filters that
        # GPT-5.2 has been observed autofilling with `False` (has_initiative
        # in particular). When True, the bypass applies to: has_initiative,
        # orphans, saved, status. Other filters (agent/category/type/
        # workspace/initiative_id) still respect explicit caller intent.
        _show_all = payload.get('show_all') in (True, 'true', 'True', 1, '1')

        # Session 1227 — track which optional filters actually fired so the
        # response can echo them. Closes the diagnostic gap that let the
        # has_initiative autofill bug ship unnoticed for ~one session.
        _applied = {}

        def _apply_common_filters(qs):
            """Apply category/agent/type/saved/status/date filters."""
            dtype = payload.get('type')
            if dtype:
                qs = qs.filter(deliverable_type=dtype)
                _applied['type'] = dtype
            cat = payload.get('category')
            if cat:
                qs = qs.filter(category__iexact=cat)
                _applied['category'] = cat
            agent = payload.get('agent')
            if agent:
                qs = qs.filter(agent_name__iexact=agent)
                _applied['agent'] = agent
            if not _show_all and payload.get('saved'):
                qs = qs.filter(is_saved=True)
                _applied['saved'] = True
            # Session 1101: Status filter (with aliases for LLM confusion)
            _STATUS_ALIASES = {'approved': 'ready', 'pending_review': 'ready', 'rejected': 'archived'}
            status = payload.get('status')
            if not _show_all and status and status.lower() != 'all':
                status = _STATUS_ALIASES.get(status, status)
                qs = qs.filter(status=status)
                _applied['status'] = status
            # Session 1101: Date range filters
            created_before = payload.get('created_before')
            created_after = payload.get('created_after')
            if created_before:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_before)
                if dt:
                    qs = qs.filter(created_at__lt=dt)
                    _applied['created_before'] = created_before
            if created_after:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(created_after)
                if dt:
                    qs = qs.filter(created_at__gte=dt)
                    _applied['created_after'] = created_after
            # Session 1077: Initiative filter
            init_id = payload.get('initiative_id')
            if init_id:
                qs = qs.filter(initiative_id=init_id)
                _applied['initiative_id'] = init_id
            # Session 1227 — has_initiative gate hardened. GPT-5.2 in function
            # calling mode autofills declared optional booleans with `False`,
            # which trips a naive `is not None` check and silently filters out
            # every deliverable WITH an initiative attached (Session 1227 root
            # cause; misdiagnosed as F3 'blocked + archived hidden' in Session
            # 1226 audit `e2964e4a-…`). Mirror the `orphans` truthy-only
            # pattern: only fire on explicit caller intent. Python bool False
            # is now treated as autofill → no filter. To explicitly request
            # "deliverables WITHOUT an initiative", pass the STRING 'false'.
            # `show_all=true` also bypasses this filter entirely.
            has_init = payload.get('has_initiative')
            if not _show_all:
                if has_init in (True, 'true', 'True', 1, '1'):
                    qs = qs.filter(initiative_id__isnull=False)
                    _applied['has_initiative'] = True
                elif has_init in ('false', 'False'):  # explicit string sentinel only
                    qs = qs.filter(initiative_id__isnull=True)
                    _applied['has_initiative'] = False
                # else: None, '', 0, False (python bool) → no filter
            # Workspace filter — scopes deliverable results to a workspace
            ws_id = payload.get('workspace_id') or payload.get('workspace')
            if ws_id:
                qs = qs.filter(workspace_id=ws_id)
                _applied['workspace_id'] = ws_id
            # Session 1091 — orphan filter so Rigby can audit "show me
            # deliverables with no workspace assignment". Accepts truthy
            # values (true/True/1/"true"). When set, ignores any other
            # workspace filter implied above (orphans by definition have
            # no workspace_id, so a positive ws_id filter would zero out
            # the result set anyway, but be explicit).
            orphans_only = payload.get('orphans')
            if not _show_all and orphans_only in (True, 'true', 'True', 1, '1'):
                qs = qs.filter(workspace_id__isnull=True)
                _applied['orphans'] = True
            return qs

        # Session 1091 — surface workspace_id + workspace name in list responses.
        # Previously the list payload omitted any workspace identifier, which
        # made it impossible for Rigby to audit orphans through PA tools and
        # forced Django-shell round-trips for any deliverable→workspace check.
        # Session 1194 — add `status` so deliverable_tool.list and
        # content_tool.content_recent return the same shape (AC1 of
        # INITIATIVES_FIRST_BACKBONE.md).
        # Session 2728 F-D-20 — include `updated_at` so callers can detect
        # freshness / staleness of rows without a follow-up detail fetch.
        # Auto_now on Deliverable keeps it live per S1231 P3.
        _LIST_FIELDS = (
            'id', 'title', 'deliverable_type', 'category',
            'agent_name', 'quality_score', 'is_saved', 'created_at',
            'updated_at',
            'status',
            'initiative_id', 'initiative__name',
            'workspace_id', 'workspace__name',
        )

        def _sanitize_deliverable(d: dict) -> dict:
            """Fill empty deliverable fields with sensible defaults."""
            if not (d.get('title') or '').strip():
                d['title'] = 'Untitled Deliverable'
            if not (d.get('agent_name') or '').strip():
                d['agent_name'] = 'System'
            if not (d.get('category') or '').strip():
                d['category'] = 'General'
            if not (d.get('deliverable_type') or '').strip():
                d['deliverable_type'] = 'document'
            # Session 1091 — explicit orphan marker so callers (PA tools, UI)
            # can highlight unassigned deliverables without re-deriving the
            # check from a missing FK.
            d['is_orphan'] = d.get('workspace_id') is None
            # Session 1091 follow-up — alias the Django ORM .values() join key
            # `workspace__name` (double underscore) as `workspace_name` (single
            # underscore) so PA-tool consumers and REST consumers see the same
            # field shape. The REST serializer in core/views_deliverables.py
            # already returns `workspace_name`; without this alias, anyone
            # comparing the two surfaces would think the field is "missing"
            # depending on which channel they look at. Keeps the original
            # `workspace__name` for backwards compatibility.
            if 'workspace_name' not in d and 'workspace__name' in d:
                d['workspace_name'] = d.get('workspace__name')
            return d

        def _resolve_deliverable(qs, payload, action_name):
            """Resolve a deliverable by id OR title. Returns (obj, None) or (None, error_dict)."""
            did = payload.get('id')
            if did:
                obj = qs.filter(id=did).first()
                if not obj:
                    raise ValueError(f"Deliverable {did} not found")
                return obj, None

            # Fallback: resolve by title
            title_q = payload.get('title', '').strip() or payload.get('query', '').strip()
            if not title_q:
                raise ValueError(f"id or title required for {action_name} action")

            # Try exact match first, then partial
            matches = qs.filter(title__iexact=title_q)
            if not matches.exists():
                matches = qs.filter(title__icontains=title_q)

            count = matches.count()
            if count == 0:
                raise ValueError(f'No deliverable found matching "{title_q}"')
            if count == 1:
                return matches.first(), None
            # Multiple matches — return disambiguation list
            items = list(
                matches.order_by('-created_at')[:10]
                .values('id', 'title', 'deliverable_type', 'created_at')
            )
            return None, {
                'action': action_name,
                'error': 'multiple_matches',
                'message': f'Found {count} deliverables matching "{title_q}". Please specify which one by id or a more specific title.',
                'matches': items,
            }

        # Session 1169 — id-based mutation actions (detail, save, unsave,
        # update, append, delete, export_pdf) need a lookup queryset that
        # respects user-ownership but does NOT apply the workspace scope
        # filter from base_qs. Otherwise orphans (workspace_id NULL) and
        # cross-workspace deliverables are unfindable for the user who
        # legitimately passed their id. PR #2311 added this only for
        # `update` when payload had workspace_id; this is the symmetric
        # extension to the rest of the id-based actions. (link_initiative
        # has a different — unscoped — lookup pattern in
        # td_handlers_content.py and is intentionally not touched.)
        def _id_lookup_qs():
            qs = Deliverable.objects.all()
            if not user_id:
                return qs
            from django.contrib.auth import get_user_model
            _UserId = get_user_model()
            try:
                _ru = _UserId.objects.get(id=user_id)
                _is_pa_or_staff = (
                    _ru.is_staff
                    or _ru.is_superuser
                    or _ru.username == 'pa-service'
                )
            except _UserId.DoesNotExist:
                return qs.filter(Q(user_id=user_id) | Q(user__isnull=True))
            if _is_pa_or_staff:
                return qs
            return qs.filter(Q(user_id=user_id) | Q(user__isnull=True))

        if action == 'list':
            qs = _apply_common_filters(base_qs)
            total = qs.count()

            items = [
                _sanitize_deliverable(d) for d in
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            ]
            _resp = {
                'action': 'list', 'total': total, 'offset': offset,
                'limit': limit, 'count': len(items), 'items': items,
                # Session 1227 — applied_filters echo + show_all flag so
                # callers can see exactly which optional filters fired.
                'applied_filters': dict(_applied),
                'show_all': _show_all,
            }
            # Session 2728 F-D-5 / S2730 F-RL-2 — surface limit-cap via
            # the shared envelope dict from `compute_limit`. Empty dict
            # spread is a no-op on the happy path.
            _resp.update(_envelope)
            return _resp

        elif action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")

            qs = _apply_common_filters(base_qs.filter(title__icontains=query))
            total = qs.count()

            items = [
                _sanitize_deliverable(d) for d in
                qs.order_by('-created_at')[offset:offset + limit].values(*_LIST_FIELDS)
            ]
            _resp = {
                'action': 'search', 'query': query, 'total': total,
                'offset': offset, 'limit': limit, 'count': len(items), 'items': items,
                # Session 1227 — same applied_filters surface as list action.
                'applied_filters': dict(_applied),
                'show_all': _show_all,
            }
            # Session 2728 F-D-5 / S2730 F-RL-2 — same shared envelope
            # as the list branch above.
            _resp.update(_envelope)
            return _resp

        elif action == 'detail':
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'detail')
            if disambiguation:
                return disambiguation

            # Emit view event for dashboard tracking
            try:
                from core.models_deliverables import DeliverableEvent
                DeliverableEvent.objects.create(
                    deliverable=obj,
                    event_type='synthesis_viewed',
                    source='pa_tool',
                    metadata={'trace_id': trace_id},
                )
            except Exception:
                pass  # fire-and-forget

            # Session 1086: Return content for PA reading.
            # Session 1077: Support full=true to bypass 8K cap, and
            # offset/limit for paginated reading of long documents.
            full_content = obj.content or ''
            want_full = str(payload.get('full', '')).lower() in ('true', '1', 'yes')
            content_offset = int(payload.get('content_offset', 0))
            content_limit = int(payload.get('content_limit', 0))

            if content_offset or content_limit:
                # Paginated read: return a slice of the content
                end = content_offset + (content_limit or 8000)
                content_slice = full_content[content_offset:end]
                is_truncated = end < len(full_content)
            elif want_full:
                # Full read: no cap (caller opted in to large payload)
                content_slice = full_content
                is_truncated = False
            else:
                # Default: cap at 8000 chars for LLM context safety
                content_slice = full_content[:8000]
                is_truncated = len(full_content) > 8000

            # Session 1184: surface the canonical provenance chain on detail.
            # origin_execution_id resolves to parent_object_id when
            # parent_object_type='agent_execution' (or 'deliverable_factory'
            # for PA-direct receipts). See core/services/deliverable_provenance.
            from core.services.deliverable_provenance import build_provenance_block
            return _sanitize_deliverable({
                'action': 'detail',
                'id': str(obj.id),
                'title': obj.title,
                'deliverable_type': obj.deliverable_type,
                'category': obj.category,
                'agent_name': obj.agent_name,
                'content_format': obj.content_format,
                'content': content_slice,
                'content_truncated': is_truncated,
                'content_length': len(full_content),
                'content_preview': full_content[:500],
                'quality_score': obj.quality_score,
                'is_saved': obj.is_saved,
                'is_template': obj.is_template,
                'status': obj.status,
                'tags': obj.tags or [],
                'created_at': obj.created_at.isoformat() if obj.created_at else None,
                # Session 1092: include workspace fields so _sanitize_deliverable
                # can compute is_orphan correctly. Without these, every detail
                # call returned is_orphan=true, breaking workspace-flow-canary.
                'workspace_id': str(obj.workspace_id) if obj.workspace_id else None,
                'workspace__name': obj.workspace.name if obj.workspace_id and getattr(obj, 'workspace', None) else None,
                # Session 1194 Plan B §3.B.1 — surface initiative linkage on
                # detail so callers can do initiative ↔ deliverable round-trip
                # without a follow-on query. Closes AC2 of
                # INITIATIVES_FIRST_BACKBONE.md.
                'initiative_id': str(obj.initiative_id) if obj.initiative_id else None,
                'initiative__name': obj.initiative.name if obj.initiative_id and getattr(obj, 'initiative', None) else None,
                'provenance': build_provenance_block(obj),
            })

        elif action == 'save':
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'save')
            if disambiguation:
                return disambiguation
            obj.is_saved = True
            obj.save(update_fields=['is_saved'])
            try:
                from core.models_deliverables import DeliverableEvent
                DeliverableEvent.objects.create(
                    deliverable=obj, event_type='deliverable_saved',
                    source='pa_tool', metadata={'trace_id': trace_id},
                )
            except Exception as _e:
                logger.warning(
                    "td_handlers_agents._resolve_deliverable: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
            return {'action': 'save', 'id': str(obj.id), 'title': obj.title, 'saved': True}

        elif action == 'unsave':
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'unsave')
            if disambiguation:
                return disambiguation
            obj.is_saved = False
            obj.save(update_fields=['is_saved'])
            return {'action': 'unsave', 'id': str(obj.id), 'title': obj.title, 'saved': False}

        elif action == 'create':
            # S3038-S8 — Envelope logging for the create path. `_s8_emit`
            # emits [PA_DELIVERABLES_ENVELOPE] with the same trace_id used
            # by [PA_DELIVERABLES_INTENT] and [PA_TASK_SUMMARY], so log
            # lines cross-reference to Deliverable rows and PA-loop
            # iterations. Every exit (return or raise) below runs `_s8_emit`
            # before leaving the branch.
            import time as _s8_time
            _s8_start = _s8_time.monotonic()

            def _s8_emit(ok, deliverable_id=None, error_code=None, reason_code=None, exception=None):
                logger.info(
                    "[PA_DELIVERABLES_ENVELOPE] trace_id=%s action=create ok=%s "
                    "id=%s error_code=%s reason_code=%s exception=%s "
                    "duration_ms=%d title=%r workspace_id=%s",
                    trace_id,
                    'true' if ok is True else ('false' if ok is False else 'unknown'),
                    deliverable_id or 'none',
                    error_code or 'none',
                    reason_code or 'none',
                    exception or 'none',
                    int((_s8_time.monotonic() - _s8_start) * 1000),
                    (payload.get('title') or '')[:80],
                    payload.get('workspace_id') or payload.get('workspace') or 'none',
                )

            # Session 1065: Allow PA to save arbitrary content to Deliverables
            # Session 1077: Accept category, tags, workspace, data_sensitivity, is_pinned
            title = payload.get('title', '').strip()
            content = payload.get('content', '').strip()
            if not title or not content:
                _s8_emit(ok=False, error_code='title_content_required')
                raise ValueError("title and content are required for create action")

            import uuid as _d_uuid
            from django.utils.text import slugify as _d_slugify

            content_format = payload.get('content_format', 'markdown')
            # S2868: normalize empty string / whitespace / None to 'document'.
            # Prior behavior let payload.get('type', 'document') return '' if
            # the caller explicitly passed type=''. That polluted downstream
            # type-based logic (exemption checks, stats aggregations, UI
            # icons) and produced 26 orphan-typed rows in production.
            _raw_dtype = payload.get('type')
            dtype = (_raw_dtype.strip() if isinstance(_raw_dtype, str) else _raw_dtype) or 'document'
            slug = f"{_d_slugify(title[:100])}-{_d_uuid.uuid4().hex[:8]}"

            # Resolve user
            resolved_user = None
            if user_id:
                from django.contrib.auth import get_user_model
                _DUser = get_user_model()
                try:
                    resolved_user = _DUser.objects.get(id=user_id)
                except _DUser.DoesNotExist:
                    pass

            # Resolve workspace
            resolved_workspace = None
            ws_id = payload.get('workspace_id') or payload.get('workspace')
            if ws_id:
                try:
                    from core.models_skin_layer import ProjectWorkspace
                    resolved_workspace = ProjectWorkspace.objects.get(id=ws_id)
                except Exception as _e:
                    logger.warning(
                        "td_handlers_agents._resolve_deliverable: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            preview = content[:500]
            if len(content) > 500:
                preview += '...'

            # Accept payload overrides with sensible defaults
            category = payload.get('category', 'PA Created')
            tags = payload.get('tags', ['pa-created'])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',') if t.strip()]
            agent_name = payload.get('agent_name', PA_IDENTITY)
            data_sensitivity = payload.get('data_sensitivity', 'internal')
            is_pinned = bool(payload.get('is_pinned', False))

            # Session 2728 F-D-6 — honor caller's `status` intent, default to
            # 'ready' (not 'completed'). Prior behavior hardcoded 'completed'
            # regardless of payload, so every PA-created row landed immutable
            # (per Playbook §5.5 lifecycle intent) and Rigby's explicit
            # `status='draft'` was silently dropped. Whitelist maps to
            # Deliverable.STATUS_CHOICES ratified values; unknown values fall
            # back to 'ready' with a WARNING (LLM string-drift defence).
            # `completed` cannot be reached via create — it is a lifecycle
            # terminal state and must be set via `content_tool.content_complete`
            # / the approved completion path (see F-D-7).
            _CREATE_STATUS_WHITELIST = {'draft', 'ready', 'published', 'archived'}
            _raw_status = payload.get('status')
            _requested_status = (_raw_status or '').strip().lower() if isinstance(_raw_status, str) else ''
            if _requested_status == 'completed':
                _s8_emit(ok=False, error_code='status_completed_not_allowed_on_create')
                return {
                    'action': 'create',
                    'ok': False,
                    'error_code': 'status_completed_not_allowed_on_create',
                    'message': (
                        "status='completed' cannot be set via deliverable_tool.create. "
                        "Create the deliverable with status='ready' (or omit to use the "
                        "default), then flip to completed via content_tool."
                        "content_complete or deliverable_tool.set_status "
                        "(status='completed')."
                    ),
                    'retry_suggestions': [
                        "Retry create without status (defaults to 'ready').",
                        "Retry create with status='ready', 'draft', or 'published'.",
                    ],
                    'trace_id': trace_id,
                }
            if _requested_status in _CREATE_STATUS_WHITELIST:
                _create_status = _requested_status
            else:
                if _raw_status not in (None, ''):
                    logger.warning(
                        "[deliverables.create] Unknown status=%r requested; "
                        "falling back to 'ready'. Whitelist=%s",
                        _raw_status, sorted(_CREATE_STATUS_WHITELIST),
                    )
                _create_status = 'ready'

            from core.services.deliverable_factory import create_deliverable
            # Session 1168: trigger_source='pa_tool' tells the factory's gate 3
            # (min content length) that this is a legitimate PA-initiated save,
            # not background noise. Without this, short PA saves trip the gate
            # and the factory silently returns None.
            # Session 1169 — Layer C Phase 1: opt in to typed exception
            # so the gated response carries the factory's actual
            # reason_code (gate_1_media_stub / gate_2_smoke_pattern /
            # gate_3_min_length) instead of the previous generic
            # 'unknown_gate'. The retry hint stays callable-built so
            # the user always sees something actionable, but now the
            # machine-parseable reason_code matches the actual gate
            # that fired.
            from core.services.deliverable_factory import DeliverableGatedError
            try:
                obj = create_deliverable(
                    title=title[:255],
                    content=content,
                    agent_name=agent_name,
                    category=category,
                    deliverable_type=dtype,
                    user=resolved_user,
                    workspace_id=str(resolved_workspace.id) if resolved_workspace else None,
                    trace_id=trace_id,
                    tags=tags,
                    content_format=content_format,
                    quality_score=float(payload.get('quality_score', 0.7)),
                    confidence_score=float(payload.get('confidence_score', 0.8)),
                    is_saved=True,
                    is_pinned=is_pinned,
                    metadata={
                        'source': 'pa_deliverables_tool',
                        'trigger_source': 'pa_tool',
                        'trace_id': trace_id,
                    },
                    slug=slug,
                    preview_content=preview,
                    status=_create_status,
                    data_sensitivity=data_sensitivity,
                    workspace=resolved_workspace,
                    raise_on_gated=True,
                    # S2859 Ledger #8: PA tool-surface callers pass user-
                    # authored titles verbatim (identifier-like governance
                    # artifacts, ratification records). Skip the auto-
                    # prefix reconstruction + 120-char cap in the factory.
                    preserve_title=True,
                )
            except DeliverableGatedError as e:
                _s8_emit(ok=False, error_code='deliverable_gated', reason_code=e.reason_code)
                return {
                    'action': 'create',
                    'ok': False,
                    'id': None,
                    'error_code': 'deliverable_gated',
                    'reason_code': e.reason_code,
                    'reason': e.reason,
                    'human_message': (
                        'Deliverable creation was blocked by the quality gate. '
                        'The title may have matched smoke-test patterns '
                        '(e.g. "smoke test", "sanity check"), or the content '
                        'was below the 300-character minimum for this trigger '
                        'source. Try a non-smoke-test title and ensure the '
                        'content is substantial, then retry.'
                    ),
                    'retry_suggestions': [
                        'Rename the title to avoid words like smoke test / sanity check / heartbeat',
                        'Ensure content is at least 300 characters',
                    ],
                    'trace_id': trace_id,
                }
            # Defensive: a non-opted-in code path (e.g., dedup hit) can
            # still return an existing Deliverable. The factory itself
            # never returns None when raise_on_gated=True, so this
            # branch is unreachable under the current contract — keep
            # the assertion-style guard so a future regression in the
            # factory's dedup logic doesn't reintroduce the silent crash.
            if obj is None:  # pragma: no cover
                _s8_emit(ok=False, error_code='factory_returned_none')
                raise RuntimeError(
                    "deliverable_factory.create_deliverable returned None "
                    "despite raise_on_gated=True — internal contract violation"
                )

            # Session 1248 P2b — close the verify-then-set_status round-trip
            # documented in `feedback_deliverable_create_defaults_to_completed.md`.
            # The factory defaults new rows to status='completed' regardless
            # of explicit status='draft'/'ready' params, so every caller had
            # to follow create with a separate detail/ORM check + set_status
            # to_status=ready. Two complementary fixes:
            #
            #   1. ALWAYS echo the actual stored `status` (Rigby's Q1c delta
            #      #1 + #2): top-level field, canonical name, source of truth.
            #      BC-safe (extra key, callers ignore extras).
            #   2. OPT-IN `return_detail=True` triggers a follow-up detail
            #      fetch and embeds the sanitized dict under a `detail` key
            #      (Rigby's delta #3: detail.status echoed but top-level
            #      status remains canonical). `detail_included: bool` flag
            #      tells callers whether the embedded fetch succeeded
            #      without making them parse for key existence (delta #4).
            #
            # Detail-fetch failure is soft: log warning + set
            # `detail_included=False`; the create itself still reports ok=True.
            response = {
                'action': 'create',
                'ok': True,
                'id': str(obj.id),
                'title': obj.title,
                'deliverable_type': obj.deliverable_type,
                'category': obj.category,
                'status': obj.status,
                'saved': True,
                'message': f'Created and saved "{obj.title}" to your Deliverables library.',
            }

            if payload.get('return_detail') in (True, 'true', 'True', 1, '1'):
                response['detail_included'] = False
                try:
                    detail_result = self._handle_deliverables(
                        tool_name,
                        {'action': 'detail', 'id': str(obj.id)},
                        user_id,
                        trace_id,
                    )
                    if isinstance(detail_result, dict) and 'error' not in detail_result:
                        response['detail'] = detail_result
                        response['detail_included'] = True
                    else:
                        logger.warning(
                            "[deliverables.create] return_detail follow-up "
                            "returned no usable detail dict for id=%s: %r",
                            obj.id, detail_result,
                        )
                except Exception as _detail_err:
                    logger.warning(
                        "[deliverables.create] return_detail follow-up "
                        "raised for id=%s (%s: %s) — create succeeded; "
                        "embedding detail_included=False",
                        obj.id, type(_detail_err).__name__, _detail_err,
                    )

            _s8_emit(ok=True, deliverable_id=str(obj.id))
            return response

        elif action == 'update':
            # Session 1168 bug #2 + Session 1169 item 3: use the
            # _id_lookup_qs helper which respects user-ownership but
            # doesn't apply workspace scoping. Covers both the
            # explicit attach intent (payload has workspace_id) and the
            # latent case where AssistantProfile's workspace would have
            # excluded an orphan the user owns.
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'update')
            if disambiguation:
                return disambiguation

            update_fields = []
            if 'title' in payload and payload['title'] and payload['title'].strip():
                obj.title = payload['title'].strip()[:255]
                update_fields.append('title')

            # Support prepend/append without requiring full content
            # Session 1077: GPT-5.2 often sends content="" alongside append,
            # so prioritize append/prepend over empty content replacement
            prepend_text = payload.get('prepend', '').strip()
            append_text = payload.get('append', '').strip()
            raw_content = payload.get('content', '')
            has_real_content = raw_content and raw_content.strip()

            if prepend_text or append_text:
                current = obj.content or ''
                if prepend_text:
                    current = prepend_text + '\n\n' + current
                if append_text:
                    current = current + '\n\n' + append_text
                obj.content = current
                preview = current[:500]
                if len(current) > 500:
                    preview += '...'
                obj.preview_content = preview
                # Session 1231 P3 — include updated_at so Django's auto_now
                # fires (silenced by update_fields if not listed). Closes
                # audit-trail gap from tracking deliverable 61f4312b-….
                update_fields.extend(['content', 'preview_content', 'updated_at'])
            elif has_real_content:
                obj.content = raw_content
                preview = raw_content[:500]
                if len(raw_content) > 500:
                    preview += '...'
                obj.preview_content = preview
                update_fields.extend(['content', 'preview_content', 'updated_at'])

            if 'type' in payload and payload['type'] and str(payload['type']).strip():
                obj.deliverable_type = str(payload['type']).strip()
                update_fields.append('deliverable_type')
            if 'content_format' in payload and payload['content_format'] and str(payload['content_format']).strip():
                obj.content_format = str(payload['content_format']).strip()
                update_fields.append('content_format')
            if 'tags' in payload:
                raw_tags = payload['tags']
                if isinstance(raw_tags, list):
                    obj.tags = [str(t).strip() for t in raw_tags if str(t).strip()]
                else:
                    obj.tags = [t.strip() for t in str(raw_tags).split(',') if t.strip()]
                update_fields.append('tags')
            if 'category' in payload and payload['category'] and payload['category'].strip():
                obj.category = payload['category'].strip()[:100]
                update_fields.append('category')
            if 'data_sensitivity' in payload and payload['data_sensitivity']:
                obj.data_sensitivity = payload['data_sensitivity']
                update_fields.append('data_sensitivity')
            if 'status' in payload and payload['status']:
                # Session 2728 F-D-7 — status='completed' cannot be reached via
                # update. It is a lifecycle terminal state governed by the
                # PublishGate state machine (see MEMORY
                # `feedback_deliverable_status_via_content_complete`). Prior
                # behavior silently dropped 'completed' (whitelist match miss)
                # which meant Rigby's flip attempt landed as a no-op and she
                # could not detect the drop from the response shape. Now
                # returns a typed Rigby-safe error pointing at the correct
                # completion path.
                new_status = payload['status'].strip().lower() if isinstance(payload['status'], str) else ''
                if new_status == 'completed':
                    return {
                        'action': 'update',
                        'ok': False,
                        'error_code': 'status_completed_not_allowed_on_update',
                        'id': str(obj.id),
                        'title': obj.title,
                        'message': (
                            "status='completed' cannot be set via "
                            "deliverable_tool.update. `completed` is a "
                            "lifecycle terminal state governed by the "
                            "PublishGate state machine. Use "
                            "content_tool.content_complete "
                            "(the approved completion path) or "
                            "deliverable_tool.set_status status='completed' "
                            "(surgical audited flip)."
                        ),
                        'retry_suggestions': [
                            "content_tool.content_complete id=<uuid>",
                            "deliverable_tool.set_status id=<uuid> status=completed",
                        ],
                        'trace_id': trace_id,
                    }
                valid_statuses = {'draft', 'ready', 'published', 'archived'}
                if new_status in valid_statuses:
                    obj.status = new_status
                    update_fields.append('status')
            if 'workspace_id' in payload or 'workspace' in payload:
                ws_id = payload.get('workspace_id') or payload.get('workspace')
                if ws_id:
                    try:
                        from core.models_skin_layer import ProjectWorkspace
                        obj.workspace = ProjectWorkspace.objects.get(id=ws_id)
                        update_fields.append('workspace')
                    except Exception as _e:
                        logger.warning(
                            "td_handlers_agents._resolve_deliverable: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

            # Session 1195 — Plan C Phase 1: support initiative_id updates so
            # missing_initiative_id diagnostics can be resolved via the update
            # path (auto-clear ratified). Mirrors the workspace setter pattern:
            # if Initiative.objects.get() raises, log + degrade rather than
            # block the update.
            if 'initiative_id' in payload:
                init_id = payload.get('initiative_id')
                if init_id:
                    try:
                        from core.models import Initiative
                        obj.initiative = Initiative.objects.get(id=init_id)
                        update_fields.append('initiative')
                    except Exception as _e:
                        logger.warning(
                            "td_handlers_agents._handle_deliverables: "
                            "initiative_id=%s lookup failed (%s: %s) — "
                            "dropping initiative update for deliverable=%s",
                            init_id, type(_e).__name__, _e, obj.id,
                        )

            if not update_fields:
                raise ValueError("update requires at least one of: title, content, prepend, append, type, content_format, tags, category, status, data_sensitivity, workspace_id, initiative_id")

            # Session 1195 — Plan C Phase 1: re-evaluate Initiative alignment
            # after the user-requested field changes are applied to `obj`.
            # Per Rigby's idempotency nudge: only emit transition logs
            # (NULL → diagnostic, code A → code B). Auto-clear is silent
            # except for an info log keyed code=auto_clear.
            from core.services.deliverable_factory import _evaluate_initiative_alignment
            from django.utils import timezone as _tz
            from datetime import timedelta as _timedelta
            from django.conf import settings as _settings

            prior_diag_status = obj.diagnostic_status
            prior_diag_code = obj.diagnostic_code
            new_diag_eval = _evaluate_initiative_alignment(
                initiative_id=str(obj.initiative_id) if obj.initiative_id else None,
                workspace_id=str(obj.workspace_id) if obj.workspace_id else None,
                deliverable_type=obj.deliverable_type,  # S2859 Ledger #9
            )
            DIAG_FIELDS = [
                'diagnostic_status', 'diagnostic_code',
                'diagnostic_payload', 'diagnostic_marked_at',
                'diagnostic_expires_at',
            ]
            if new_diag_eval is None:
                # Aligned now — auto-clear if previously diagnostic OR
                # manually-cleared. Includes 'cleared' so a caller that fixes
                # the alignment (e.g., links an initiative) fully resets the
                # sentinel back to NULL rather than leaving audit residue.
                if prior_diag_status in ('diagnostic', 'cleared'):
                    obj.diagnostic_status = None
                    obj.diagnostic_code = None
                    obj.diagnostic_payload = None
                    obj.diagnostic_marked_at = None
                    obj.diagnostic_expires_at = None
                    update_fields.extend(DIAG_FIELDS)
                    logger.info(
                        "[ORPHAN-DELIVERABLE] code=auto_clear "
                        "deliverable_id=%s prior_status=%s prior_code=%s trace_id=%s",
                        str(obj.id), prior_diag_status, prior_diag_code, trace_id or '-',
                    )
            else:
                new_code, expected_ws_id = new_diag_eval
                # S2868: sticky-clear sentinel — if an operator explicitly
                # cleared this row via clear_diagnostic AND the alignment
                # eval would re-raise the same code, suppress the re-mark.
                # Only suppresses missing_initiative_id (the semantic
                # covered by the manual clear); workspace_mismatch is a
                # stronger integrity signal and any code transition
                # (missing_initiative_id → workspace_mismatch) still fires.
                if (
                    prior_diag_status == 'cleared'
                    and new_code == 'missing_initiative_id'
                    and prior_diag_code == 'missing_initiative_id'
                ):
                    logger.info(
                        "[ORPHAN-DELIVERABLE] code=cleared_sticky "
                        "deliverable_id=%s trace_id=%s "
                        "(suppressed missing_initiative_id re-mark)",
                        str(obj.id), trace_id or '-',
                    )
                # Mark diagnostic on transition (NULL → diagnostic OR code change).
                elif prior_diag_status != 'diagnostic' or prior_diag_code != new_code:
                    ttl_hours = getattr(_settings, 'DELIVERABLE_DIAGNOSTIC_TTL_HOURS', 168)
                    diag_now = _tz.now()
                    obj.diagnostic_status = 'diagnostic'
                    obj.diagnostic_code = new_code
                    obj.diagnostic_marked_at = diag_now
                    obj.diagnostic_expires_at = diag_now + _timedelta(hours=ttl_hours)
                    obj.diagnostic_payload = {
                        'initiative_id': str(obj.initiative_id) if obj.initiative_id else None,
                        'expected_workspace_id': str(expected_ws_id) if expected_ws_id else None,
                        'actual_workspace_id': str(obj.workspace_id) if obj.workspace_id else None,
                        'agent_name': obj.agent_name,
                        'tool': 'deliverable_tool.update',
                        'trace_id': trace_id,
                        'caller': 'td_handlers_agents._handle_deliverables',
                        'reason': new_code.replace('_', ' '),
                        'marked_at': diag_now.isoformat(),
                        'ttl_hours': ttl_hours,
                    }
                    update_fields.extend(DIAG_FIELDS)
                    if new_code == 'missing_initiative_id':
                        logger.warning(
                            "[ORPHAN-DELIVERABLE] code=missing_initiative_id "
                            "deliverable_id=%s agent_name=%s tool=deliverable_tool.update "
                            "caller=_handle_deliverables trace_id=%s workspace_id=%s ttl_hours=%s",
                            str(obj.id), obj.agent_name, trace_id or '-',
                            str(obj.workspace_id) if obj.workspace_id else 'null', ttl_hours,
                        )
                    else:  # workspace_mismatch
                        logger.warning(
                            "[ORPHAN-DELIVERABLE] code=workspace_mismatch "
                            "deliverable_id=%s agent_name=%s tool=deliverable_tool.update "
                            "caller=_handle_deliverables trace_id=%s initiative_id=%s "
                            "expected_workspace_id=%s actual_workspace_id=%s ttl_hours=%s",
                            str(obj.id), obj.agent_name, trace_id or '-',
                            str(obj.initiative_id),
                            str(expected_ws_id) if expected_ws_id else 'null',
                            str(obj.workspace_id) if obj.workspace_id else 'null',
                            ttl_hours,
                        )

            obj.save(update_fields=update_fields)
            return {
                'action': 'update',
                'id': str(obj.id),
                'title': obj.title,
                # Session 2728 F-D-8 — mirror the create-response shape and
                # surface the persisted status so callers do not need a
                # follow-up detail fetch to verify the write. Especially
                # useful when combined with the F-D-7 gate: if a caller
                # requests status='completed', the typed error surfaces the
                # correct completion path; otherwise, this echoes the stored
                # value that survived the update.
                'status': obj.status,
                'updated_fields': update_fields,
                'message': f'Updated "{obj.title}" ({", ".join(update_fields)}).',
            }

        elif action == 'append':
            # Session 1077: Dedicated append action — simpler than update for GPT.
            # Only appends text; never replaces content or touches other fields.
            # Session 1169: use _id_lookup_qs (orphan-inclusive) to match update.
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'append')
            if disambiguation:
                return disambiguation
            text = payload.get('content', '') or payload.get('text', '') or payload.get('append', '')
            if not text or not text.strip():
                raise ValueError("content or text is required for append action")
            current = obj.content or ''
            obj.content = current + '\n\n' + text.strip() if current else text.strip()
            obj.preview_content = obj.content[:500] + ('...' if len(obj.content) > 500 else '')
            # Session 1231 P3 — include updated_at so Django's auto_now fires
            # (auto_now is silenced by update_fields if not listed). Closes
            # audit-trail gap from tracking deliverable 61f4312b-….
            obj.save(update_fields=['content', 'preview_content', 'updated_at'])
            return {
                'action': 'append',
                'id': str(obj.id),
                'title': obj.title,
                'content_length': len(obj.content),
                'appended_chars': len(text.strip()),
                'message': f'Appended {len(text.strip())} chars to "{obj.title}" (total: {len(obj.content)} chars).',
            }

        elif action == 'delete':
            # S2860 Ledger #10: hard-delete a single deliverable by id. This
            # path was implemented since Session 1169 but never exposed in the
            # deliverable_tool schema enum, so Rigby had to fall back to
            # content_tool.content_reject (soft-archive) for genuine cleanup.
            # Exposing the action here — with two-factor gate + published
            # guard + audit log line (DeliverableEvent cascades on delete, so
            # we cannot rely on it for the audit trail).
            from core.services.td_autofill_safety import require_write_authorization
            dry_run, _write_ok = require_write_authorization(payload)

            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'delete')
            if disambiguation:
                return disambiguation

            # Cascade counts (surfaced in dry-run preview + live response so
            # the caller can see the blast radius before/after the delete).
            # ContentPacketItem uses related_name='packet_items'; other two
            # use 'exports' / 'events'.
            cascades = {
                'exports_count': obj.exports.count(),
                'events_count': obj.events.count(),
                'packet_items_count': obj.packet_items.count(),
            }

            raw_reason = payload.get('reason')
            reason = raw_reason.strip() if isinstance(raw_reason, str) else ''
            allow_published = payload.get('allow_published') is True

            # Published guard — reject by default; allow_published=true is the
            # explicit escape hatch and additionally requires a non-empty
            # reason (defence against LLM autofilling allow_published=True
            # blindly on a published row).
            if obj.status == 'published':
                if not allow_published:
                    return {
                        'action': 'delete',
                        'ok': False,
                        'error_code': 'delete_published_requires_allow_published',
                        'id': str(obj.id),
                        'title': obj.title,
                        'status': obj.status,
                        'message': (
                            f"Refusing to delete published deliverable "
                            f'"{obj.title}". Published rows must set '
                            "allow_published=true AND provide a non-empty "
                            "reason. Prefer set_status='archived' for "
                            "reversible cleanup of published content."
                        ),
                        'cascades': cascades,
                        'trace_id': trace_id,
                    }
                if not reason:
                    return {
                        'action': 'delete',
                        'ok': False,
                        'error_code': 'delete_published_requires_reason',
                        'id': str(obj.id),
                        'title': obj.title,
                        'status': obj.status,
                        'message': (
                            f"allow_published=true set for published deliverable "
                            f'"{obj.title}" but reason is missing/empty. '
                            "Provide a non-empty reason explaining why this "
                            "published row must be permanently deleted."
                        ),
                        'cascades': cascades,
                        'trace_id': trace_id,
                    }

            title = obj.title
            del_id = str(obj.id)
            status = obj.status
            workspace_id = str(obj.workspace_id) if getattr(obj, 'workspace_id', None) else None
            agent_name = getattr(obj, 'agent_name', None)

            if dry_run:
                return {
                    'action': 'delete',
                    'dry_run': True,
                    'id': del_id,
                    'title': title,
                    'status': status,
                    'workspace_id': workspace_id,
                    'agent_name': agent_name,
                    'cascades': cascades,
                    'will_delete': True,
                    'reason': reason or None,
                    'message': (
                        f'DRY RUN: would permanently delete "{title}" '
                        f'({cascades["exports_count"]} exports, '
                        f'{cascades["events_count"]} events, '
                        f'{cascades["packet_items_count"]} packet items cascade). '
                        "Set dry_run=false AND confirm=true to execute."
                    ),
                    'trace_id': trace_id,
                }

            # Live path — pre-delete WARNING log line is the durable audit
            # trail because DeliverableEvent CASCADEs with the row (see
            # core/models_deliverables.py:584-588). Logs land in application
            # log aggregation; grep by deliverable_id / trace_id / user_id.
            logger.warning(
                "[DELIVERABLE_DELETE] %s deliverable_id=%s title=%r status=%s "
                "workspace_id=%s agent_name=%s user_id=%s reason=%r cascades=%s",
                trace_id, del_id, title, status, workspace_id, agent_name,
                user_id, reason or None, cascades,
            )
            obj.delete()
            return {
                'action': 'delete',
                'dry_run': False,
                'id': del_id,
                'title': title,
                'status': status,
                'workspace_id': workspace_id,
                'cascades': cascades,
                'reason': reason or None,
                'message': (
                    f'Permanently deleted "{title}" '
                    f'({cascades["exports_count"]} exports, '
                    f'{cascades["events_count"]} events, '
                    f'{cascades["packet_items_count"]} packet items cascaded).'
                ),
                'trace_id': trace_id,
            }

        elif action == 'clear_diagnostic':
            # S2868 Ledger #7/#17/#18: sticky operator clear of the
            # missing_initiative_id diagnostic. Sets diagnostic_status to
            # the 'cleared' sentinel (distinct from NULL which the update
            # path treats as 'never marked') so subsequent updates on a
            # row whose alignment state is unchanged do NOT re-fire the
            # same diagnostic. Preserves the prior code + marked_at as
            # audit residue in diagnostic_payload alongside the manual
            # clear metadata.
            #
            # Scope: missing_initiative_id only. Workspace_mismatch is a
            # stronger integrity signal — its transition still fires
            # even if a row was previously cleared (the update path
            # branches on prior_diag_code != new_code).
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'clear_diagnostic')
            if disambiguation:
                return disambiguation

            if obj.diagnostic_status != 'diagnostic':
                return {
                    'action': 'clear_diagnostic',
                    'ok': False,
                    'id': str(obj.id),
                    'title': obj.title,
                    'diagnostic_status': obj.diagnostic_status,
                    'error_code': 'not_diagnostic',
                    'message': (
                        f'Deliverable "{obj.title}" has diagnostic_status='
                        f'{obj.diagnostic_status!r}; clear_diagnostic only '
                        "applies to rows currently marked 'diagnostic'."
                    ),
                    'trace_id': trace_id,
                }

            raw_reason = payload.get('reason')
            reason = raw_reason.strip() if isinstance(raw_reason, str) else ''
            if not reason:
                return {
                    'action': 'clear_diagnostic',
                    'ok': False,
                    'id': str(obj.id),
                    'title': obj.title,
                    'error_code': 'reason_required',
                    'message': (
                        "reason is required for clear_diagnostic — a "
                        "non-empty free-text explanation for why the "
                        "diagnostic mark is being manually cleared "
                        "(persisted under diagnostic_payload.manual_clear_reason)."
                    ),
                    'trace_id': trace_id,
                }

            from django.utils import timezone as _tz_cd
            prior_code = obj.diagnostic_code
            prior_payload = dict(obj.diagnostic_payload) if obj.diagnostic_payload else {}
            prior_marked_at = obj.diagnostic_marked_at
            clear_now = _tz_cd.now()

            obj.diagnostic_status = 'cleared'
            # Preserve prior_code + marked_at as audit residue; NULL out
            # expires_at so the sweep task (which looks for
            # diagnostic_status='diagnostic' only) does not touch this row.
            obj.diagnostic_expires_at = None
            obj.diagnostic_payload = {
                **prior_payload,
                'manually_cleared_at': clear_now.isoformat(),
                'manually_cleared_by_user_id': str(user_id) if user_id else None,
                'manual_clear_reason': reason,
                'manual_clear_trace_id': trace_id,
                'prior_diagnostic_code': prior_code,
                'prior_marked_at': prior_marked_at.isoformat() if prior_marked_at else None,
            }
            obj.save(update_fields=[
                'diagnostic_status',
                'diagnostic_expires_at',
                'diagnostic_payload',
            ])

            logger.info(
                "[ORPHAN-DELIVERABLE] code=manual_clear "
                "deliverable_id=%s prior_code=%s user_id=%s trace_id=%s reason=%r",
                str(obj.id), prior_code, user_id, trace_id or '-', reason,
            )

            return {
                'action': 'clear_diagnostic',
                'ok': True,
                'id': str(obj.id),
                'title': obj.title,
                'diagnostic_status': 'cleared',
                'prior_diagnostic_code': prior_code,
                'reason': reason,
                'message': (
                    f'Cleared diagnostic (prior code={prior_code!r}) on '
                    f'"{obj.title}". Subsequent updates on this row will '
                    "not re-fire missing_initiative_id."
                ),
                'trace_id': trace_id,
            }

        elif action == 'export_pdf':
            # Session 1169: use _id_lookup_qs (orphan-inclusive) to match update.
            obj, disambiguation = _resolve_deliverable(_id_lookup_qs(), payload, 'export_pdf')
            if disambiguation:
                return disambiguation
            from core.services.pdf_export_service import export_deliverable_to_pdf
            result = export_deliverable_to_pdf(str(obj.id), user_id)
            return result

        elif action == 'stats':
            total = base_qs.count()
            saved = base_qs.filter(is_saved=True).count()
            templates = base_qs.filter(is_template=True).count()
            with_user = base_qs.filter(user__isnull=False).count()
            orphans = base_qs.filter(user__isnull=True).count()
            by_type = dict(
                base_qs.values('deliverable_type')
                .annotate(count=Count('id'))
                .values_list('deliverable_type', 'count')
            )
            by_category = dict(
                base_qs.values('category')
                .annotate(count=Count('id'))
                .order_by('-count')
                .values_list('category', 'count')[:10]
            )
            # Session 1227 — full_by_agent=true returns the entire agent_name
            # long tail (Session 1226 audit `e2964e4a-…` §4.6 (C) requested
            # this so future audits can skip the ORM detour). Truthy-only
            # check so LLM-autofilled False is treated as "no override".
            _full_by_agent = payload.get('full_by_agent') in (True, 'true', 'True', 1, '1')
            _by_agent_qs = (
                base_qs.values('agent_name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            by_agent = dict(
                _by_agent_qs.values_list('agent_name', 'count')
                if _full_by_agent
                else _by_agent_qs.values_list('agent_name', 'count')[:10]
            )
            # Session 1091 Sprint B — workspace breakdown.
            # NOTE: this handler's existing 'orphans' field counts
            # user__isnull=True (system-created deliverables) — it has
            # NOTHING to do with workspace assignment. Don't conflate.
            # The workspace metrics below use distinct, prefixed names:
            #   workspace_orphans  = workspace_id IS NULL (post-PR #1965 should be 0)
            #   workspace_unassigned = lives in the "Unassigned" sentinel bucket
            #   by_workspace = list of {workspace_id, workspace_name, count, is_orphan, is_unassigned}
            by_workspace_rows = list(
                base_qs.values('workspace_id', 'workspace__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            by_workspace = [
                {
                    'workspace_id': str(r['workspace_id']) if r['workspace_id'] else None,
                    'workspace_name': r['workspace__name'] or 'Orphan (no workspace)',
                    'count': r['count'],
                    'is_orphan': r['workspace_id'] is None,
                    'is_unassigned': r['workspace__name'] == 'Unassigned',
                }
                for r in by_workspace_rows
            ]
            workspace_orphans = base_qs.filter(workspace_id__isnull=True).count()
            workspace_unassigned = base_qs.filter(workspace__name='Unassigned').count()
            # Count duplicate excess (exclude archived deliverables)
            active_qs = base_qs.exclude(status='archived')
            dupe_groups = list(
                active_qs.values('title')
                .annotate(count=Count('id'))
                .filter(count__gt=1)
                .order_by('-count')[:5]
            )
            dupe_excess = sum(d['count'] - 1 for d in dupe_groups)
            return {
                'action': 'stats',
                'total': total,
                'saved': saved,
                'templates': templates,
                'with_user': with_user,
                'orphans': orphans,
                'duplicate_excess': dupe_excess,
                'by_type': by_type,
                'by_category': by_category,
                'by_agent': by_agent,
                # Session 1227 — surface the truncation status so callers
                # know whether by_agent is the full long tail or the
                # default top-10. by_agent_truncated=true means a
                # follow-up call with full_by_agent=true is needed.
                'by_agent_truncated': not _full_by_agent and len(by_agent) >= 10,
                'by_workspace': by_workspace,
                'workspace_orphans': workspace_orphans,
                'workspace_unassigned': workspace_unassigned,
                'top_duplicates': [
                    {'title': d['title'][:100], 'count': d['count']}
                    for d in dupe_groups
                ],
            }

        elif action == 'cleanup':
            strategy = payload.get('strategy', 'duplicates')
            # Session 1228 PR-A — belt-and-suspenders write gate. The cleanup
            # strategies (duplicates, orphans, low_quality) each issue a bulk
            # .delete() when write authorized, so a silent LLM autofill of
            # dry_run=False alone must NOT execute. Require BOTH an explicit
            # dry_run falsy value AND a separate confirm=true. Memory rule:
            # feedback_llm_autofills_boolean_params_with_false.
            from core.services.td_autofill_safety import require_write_authorization
            dry_run, _write_ok = require_write_authorization(payload)

            if strategy == 'duplicates':
                # Find all titles that appear more than once
                from django.db.models import Max
                dupe_titles = (
                    base_qs.values('title')
                    .annotate(count=Count('id'), newest=Max('created_at'))
                    .filter(count__gt=1)
                )
                # For each duplicate title, keep the newest, mark rest for deletion
                to_delete_ids = []
                summary = []
                for group in dupe_titles:
                    title = group['title']
                    newest_dt = group['newest']
                    # Keep the newest one, delete the rest
                    dupes = list(
                        base_qs.filter(title=title)
                        .exclude(created_at=newest_dt)
                        .values_list('id', flat=True)
                    )
                    # If multiple share the same newest timestamp, keep just one
                    if not dupes:
                        all_ids = list(
                            base_qs.filter(title=title)
                            .order_by('-created_at')
                            .values_list('id', flat=True)
                        )
                        dupes = all_ids[1:]  # keep first (newest), delete rest
                    to_delete_ids.extend(dupes)
                    if len(summary) < 10:
                        summary.append({'title': title[:100], 'deleting': len(dupes), 'keeping': 1})

                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'duplicates', 'dry_run': True,
                        'would_delete': len(to_delete_ids),
                        'sample': summary,
                        'message': f'Would delete {len(to_delete_ids)} duplicate deliverables. Set dry_run=false AND confirm=true to execute.',
                    }
                else:
                    deleted_count = Deliverable.objects.filter(id__in=to_delete_ids).delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'duplicates', 'dry_run': False,
                        'deleted': deleted_count,
                        'sample': summary,
                        'message': f'Deleted {deleted_count} duplicate deliverables.',
                    }

            elif strategy == 'orphans':
                orphan_qs = base_qs.filter(user__isnull=True, is_saved=False)
                count = orphan_qs.count()
                sample = list(
                    orphan_qs.order_by('-created_at')[:10]
                    .values('id', 'title', 'agent_name', 'category')
                )
                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'orphans', 'dry_run': True,
                        'would_delete': count,
                        'sample': [{'title': s['title'][:100], 'agent': s['agent_name'], 'category': s['category']} for s in sample],
                        'message': f'Would delete {count} orphan deliverables (no user, not saved). Set dry_run=false AND confirm=true to execute.',
                    }
                else:
                    deleted_count = orphan_qs.delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'orphans', 'dry_run': False,
                        'deleted': deleted_count,
                        'message': f'Deleted {deleted_count} orphan deliverables.',
                    }

            elif strategy == 'low_quality':
                lq_qs = base_qs.filter(quality_score__lt=0.5, is_saved=False)
                count = lq_qs.count()
                sample = list(
                    lq_qs.order_by('quality_score')[:10]
                    .values('id', 'title', 'quality_score', 'agent_name')
                )
                if dry_run:
                    return {
                        'action': 'cleanup', 'strategy': 'low_quality', 'dry_run': True,
                        'would_delete': count,
                        'sample': [{'title': s['title'][:100], 'quality': s['quality_score'], 'agent': s['agent_name']} for s in sample],
                        'message': f'Would delete {count} low-quality deliverables (score < 0.5, not saved). Set dry_run=false AND confirm=true to execute.',
                    }
                else:
                    deleted_count = lq_qs.delete()[0]
                    return {
                        'action': 'cleanup', 'strategy': 'low_quality', 'dry_run': False,
                        'deleted': deleted_count,
                        'message': f'Deleted {deleted_count} low-quality deliverables.',
                    }

            else:
                raise ValueError(f"Unknown cleanup strategy: {strategy}. Use 'duplicates', 'orphans', or 'low_quality'.")

        elif action == 'duplicates':
            # Session 1227 — first-class duplicates action. Returns aggregate
            # groups so callers can audit duplicate titles in one tool call
            # instead of an ORM round-trip. Closes Session 1226 audit
            # `e2964e4a-…` §4.6 item 3. Each row matches the audit spec:
            # (group_key fields, count, first_created_at, last_created_at,
            #  last_7d_count, agent_name_distribution, status_distribution).
            from django.db.models import Min, Max
            from django.utils import timezone as _tz
            from datetime import timedelta as _timedelta

            # group_by — accept the list form per the schema; also accept a
            # single string for ergonomics. Whitelist the three supported
            # shapes (Rigby Session 1227 design call: predictable index usage,
            # no arbitrary combos in v1).
            raw_group_by = payload.get('group_by') or ['title']
            if isinstance(raw_group_by, str):
                raw_group_by = [raw_group_by]
            _ALLOWED_GROUP_BY = (
                ('title',),
                ('title', 'agent_name'),
                ('title', 'category'),
            )
            group_tuple = tuple(raw_group_by)
            if group_tuple not in _ALLOWED_GROUP_BY:
                raise ValueError(
                    "group_by must be one of "
                    f"{[list(g) for g in _ALLOWED_GROUP_BY]}; got {list(group_tuple)}"
                )

            # Other params (defaults match Session 1227 design pass).
            # Session 1227 PR2 — falsy-or-default pattern on int params. GPT-5.2
            # in function-calling mode autofills declared int params with 0
            # the same way it autofills booleans with False (see PR1 / memory
            # rule feedback_llm_autofills_boolean_params_with_false). Treat
            # missing/0/None/'' as "use the documented default" so the call
            # `deliverable_tool action=duplicates workspace_id=…` returns the
            # default-50 rows even when the LLM silently passes limit=0.
            min_count = max(2, int(payload.get('min_count') or 2))
            dup_limit = min(int(payload.get('limit') or 50), 200)
            window_days = max(1, int(payload.get('window_days') or 7))
            exclude_archived_raw = payload.get('exclude_archived')
            # Truthy-only check (LLM-autofill safety mirror of PR1).
            exclude_archived = exclude_archived_raw in (True, 'true', 'True', 1, '1')

            # show_all bypasses exclude_archived (and any future status-
            # related filter); workspace_id remains a primary scope guardrail
            # NOT bypassable by show_all (Rigby Session 1227 design call).
            dup_qs = base_qs
            if not _show_all and exclude_archived:
                dup_qs = dup_qs.exclude(status='archived')

            window_start = _tz.now() - _timedelta(days=window_days)

            # Aggregate groups in one pass.
            groups_qs = (
                dup_qs.values(*group_tuple)
                .annotate(
                    count=Count('id'),
                    first_created_at=Min('created_at'),
                    last_created_at=Max('created_at'),
                )
                .filter(count__gte=min_count)
                .order_by('-count', '-last_created_at')
            )
            total_above_threshold = groups_qs.count()
            groups = list(groups_qs[:dup_limit])

            # Per-group: last_7d_count + agent_name_distribution + status_distribution.
            # N+1-ish but bounded by dup_limit (default 50, max 200). Good
            # enough for the audit-style call pattern this action serves.
            results = []
            for g in groups:
                group_filter = {k: g[k] for k in group_tuple}
                group_qs = dup_qs.filter(**group_filter)
                last_7d_count = group_qs.filter(created_at__gte=window_start).count()
                agent_dist = dict(
                    group_qs.values('agent_name')
                    .annotate(n=Count('id'))
                    .order_by('-n')
                    .values_list('agent_name', 'n')
                )
                status_dist = dict(
                    group_qs.values('status')
                    .annotate(n=Count('id'))
                    .order_by('-n')
                    .values_list('status', 'n')
                )
                row = {k: g[k] for k in group_tuple}
                row.update({
                    'count': g['count'],
                    'first_created_at': (
                        g['first_created_at'].isoformat()
                        if g['first_created_at'] else None
                    ),
                    'last_created_at': (
                        g['last_created_at'].isoformat()
                        if g['last_created_at'] else None
                    ),
                    'last_7d_count': last_7d_count,
                    'agent_name_distribution': agent_dist,
                    'status_distribution': status_dist,
                })
                results.append(row)

            _dup_applied = {
                'group_by': list(group_tuple),
                'min_count': min_count,
                'limit': dup_limit,
                'window_days': window_days,
            }
            if exclude_archived and not _show_all:
                _dup_applied['exclude_archived'] = True
            if ws_scope:
                _dup_applied['workspace_id'] = ws_scope

            return {
                'action': 'duplicates',
                'count': len(results),
                'total_groups_above_threshold': total_above_threshold,
                'window_days': window_days,
                'groups': results,
                'applied_filters': _dup_applied,
                'show_all': _show_all,
            }

        elif action == 'normalize':
            # Session 1227 PR4 — alias-map sweep tool surface. Reads the
            # canonical alias map from core/services/deliverable_aliases
            # (the same source `deliverable_factory._canonicalize_agent_name`
            # uses at write time). Defaults to dry_run=true so callers see
            # what WOULD change before flipping. Writes require BOTH
            # `dry_run=false` AND `confirm=true` (Rigby D4 nuance —
            # belt-and-suspenders against LLM autofill).
            #
            # Closes Session 1226 audit `e2964e4a-…` §4.6 item 5 (optional)
            # — "automates future alias-map sweeps."
            from core.services.deliverable_aliases import AGENT_NAME_ALIASES

            field = (payload.get('field') or 'agent_name').strip()
            _ALLOWED_FIELDS = ('agent_name',)
            if field not in _ALLOWED_FIELDS:
                raise ValueError(
                    f"normalize only supports field='agent_name' in v1. "
                    f"Got field={field!r}. Allowed: {list(_ALLOWED_FIELDS)}."
                )

            # Scope — workspace by default (Rigby D2: don't silently sweep
            # globally). show_all=true is the explicit global override.
            normalize_qs = base_qs
            scope_label = (
                f'workspace:{ws_scope}' if ws_scope
                else ('global' if _show_all else 'unscoped')
            )
            if not _show_all and not ws_scope:
                raise ValueError(
                    "normalize requires either workspace_id (default scope) "
                    "or show_all=true (explicit global sweep). "
                    "Workspace scope is the safer default for a "
                    "mutation-capable surface."
                )

            # dry_run — defaults to TRUE; writes require BOTH dry_run=false
            # AND confirm=true (Rigby D4: belt-and-suspenders).
            dry_run_raw = payload.get('dry_run')
            # Only an EXPLICIT falsy passes through; anything else (missing,
            # None, True, Python False from LLM autofill) keeps dry_run=true.
            explicit_write = dry_run_raw in (False, 'false', 'False', 0, '0')
            confirm_raw = payload.get('confirm')
            confirm = confirm_raw in (True, 'true', 'True', 1, '1')
            dry_run = not (explicit_write and confirm)

            # Build preview rows.
            alias_map = AGENT_NAME_ALIASES
            preview = []
            total_affected = 0
            for variant, canonical in alias_map.items():
                if variant == canonical:
                    continue  # defensive — no row should canonicalize to itself
                variant_qs = normalize_qs.filter(**{field: variant})
                n = variant_qs.count()
                row = {
                    'from_value': variant,
                    'to_value': canonical,
                    'count': n,
                }
                if n:
                    sample_ids = [
                        str(uid) for uid in
                        variant_qs.values_list('id', flat=True)[:5]
                    ]
                    row['sample_ids'] = sample_ids
                preview.append(row)
                total_affected += n

            # Apply (only when explicitly opted in to write).
            rows_changed = 0
            if not dry_run and total_affected:
                for variant, canonical in alias_map.items():
                    if variant == canonical:
                        continue
                    n = normalize_qs.filter(**{field: variant}).update(
                        **{field: canonical}
                    )
                    rows_changed += n
                logger.info(
                    "[normalize] sweep applied: field=%s scope=%s "
                    "alias_map=%s rows_changed=%d actor=%s trace_id=%s",
                    field, scope_label, alias_map,
                    rows_changed,
                    str(user_id) if user_id else '-',
                    trace_id or '-',
                )

            _norm_applied = {
                'field': field,
                'dry_run': dry_run,
            }
            if ws_scope:
                _norm_applied['workspace_id'] = ws_scope
            if _show_all:
                _norm_applied['show_all'] = True

            if dry_run:
                msg_action = (
                    'Preview' if not explicit_write
                    else 'Preview (write requires both dry_run=false AND confirm=true)'
                )
                message = (
                    f'{msg_action}: {total_affected} row(s) in {scope_label} '
                    f'would be normalized on field={field!r}. '
                    f'Pass dry_run=false + confirm=true to apply.'
                )
            else:
                message = (
                    f'Applied: {rows_changed} row(s) normalized in '
                    f'{scope_label} on field={field!r}.'
                )

            return {
                'action': 'normalize',
                'field': field,
                'scope': scope_label,
                'dry_run': dry_run,
                'alias_map_used': alias_map,
                'preview': preview,
                'total_rows_affected': total_affected,
                'rows_changed': rows_changed,
                'applied_filters': _norm_applied,
                'message': message,
            }

        elif action == 'set_status':
            # Session 1227 PR3 — surgical, audited status flips.
            # Tight scope (Chris Session 1227 design call): only the
            # `completed ↔ ready` transitions are allowed. Closes the
            # "Rigby can't flip a premature `completed` back to `ready`"
            # gap from Session 1226 audit `e2964e4a-…` §4.6 item 4.
            #
            # For other transitions, callers continue to use
            # `deliverable_tool.update` (not audited / not whitelisted).
            new_status = (payload.get('status') or '').strip().lower()
            _ALLOWED_TARGETS = ('ready', 'completed')
            if new_status not in _ALLOWED_TARGETS:
                raise ValueError(
                    "set_status only supports status='ready' or status='completed'. "
                    f"Got status={new_status!r}. For other transitions, use "
                    "deliverable_tool.update (not audited / not whitelisted)."
                )

            # Id-first lookup (Rigby D5 nuance — title allowed only when
            # exactly one row resolves, so a duplicates-heavy workspace
            # can't accidentally flip the wrong row).
            did = payload.get('id')
            if did:
                obj = _id_lookup_qs().filter(id=did).first()
                if not obj:
                    raise ValueError(f"Deliverable {did} not found")
            else:
                title_q = (payload.get('title') or '').strip()
                if not title_q:
                    raise ValueError(
                        "set_status requires `id` (preferred) or a `title` "
                        "that resolves to exactly one deliverable."
                    )
                matches = _id_lookup_qs().filter(title__iexact=title_q)
                count = matches.count()
                if count == 0:
                    raise ValueError(f'No deliverable found matching "{title_q}"')
                if count > 1:
                    raise ValueError(
                        f'Multiple deliverables share title "{title_q}" '
                        f'({count} rows). Provide `id` to disambiguate.'
                    )
                obj = matches.first()

            current_status = obj.status
            _ALLOWED_TRANSITIONS = (
                ('completed', 'ready'),
                ('ready', 'completed'),
            )
            if (current_status, new_status) not in _ALLOWED_TRANSITIONS:
                raise ValueError(
                    f"set_status only supports completed→ready and ready→completed. "
                    f"Current status={current_status!r}, target={new_status!r}. "
                    "For other transitions, use deliverable_tool.update "
                    "(not audited / not whitelisted)."
                )

            # Reason — required on completed→ready (the explicit-unblock
            # direction; this is the path that fixes premature `completed`
            # flips). Optional on ready→completed. Trim + length cap apply
            # to both. Empty string after strip() ≠ provided.
            raw_reason = payload.get('reason')
            reason = (raw_reason or '').strip() if isinstance(raw_reason, str) else ''
            if current_status == 'completed' and new_status == 'ready' and not reason:
                raise ValueError(
                    "reason is required when flipping completed → ready. "
                    "Provide a short explanation (e.g., 'work not actually done')."
                )
            if reason and len(reason) > 500:
                raise ValueError(
                    f"reason must be ≤500 chars (got {len(reason)})."
                )
            if not reason:
                reason = None  # store NULL rather than empty string (Rigby D2)

            # Stash ephemeral context on the instance so the
            # deliverable_status_signals.record_status_transition post_save
            # receiver picks it up. The signal removes the attribute after
            # reading, preventing leak to subsequent saves on this instance.
            obj._transition_context = {
                'reason': reason,
                'actor_user_id': str(user_id) if user_id else None,
                'trace_id': trace_id,
                'source': 'deliverable_tool.set_status',
            }
            obj.status = new_status
            obj.save(update_fields=['status'])

            # Look up the event the signal just wrote so we can return its
            # id. The signal is best-effort, so this may be None.
            transition_event_id = None
            try:
                from core.models_deliverables import DeliverableEvent
                latest_event = (
                    DeliverableEvent.objects
                    .filter(deliverable=obj, event_type='status_transition')
                    .order_by('-created_at')
                    .first()
                )
                if latest_event:
                    transition_event_id = str(latest_event.id)
            except Exception as _e:
                logger.warning(
                    "[set_status] event_id lookup failed (%s: %s) — "
                    "transition still persisted, response will omit event id",
                    type(_e).__name__, _e,
                )

            return {
                'action': 'set_status',
                'id': str(obj.id),
                'title': obj.title,
                'from_status': current_status,
                'to_status': new_status,
                'reason': reason,
                'transition_event_id': transition_event_id,
                'message': (
                    f'Flipped "{obj.title}" from {current_status} to {new_status}'
                    + (f' (reason: "{reason}")' if reason else '.')
                ),
            }

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_media(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle media library tool (images, videos, audio)."""
        from content.models import ImageHistory, VideoHistory, AudioHistory
        from django.db.models import Count

        action = payload.get('action', 'list')
        media_type = payload.get('media_type', 'all')
        limit = min(payload.get('limit', 10), 50)

        # Helper to build per-model querysets scoped to user
        def _qs(model):
            qs = model.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        if action == 'list':
            content_type = payload.get('content_type')
            items = []

            if media_type in ('image', 'all'):
                qs = _qs(ImageHistory)
                if content_type:
                    qs = qs.filter(image_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'image',
                        'filename': obj.filename,
                        'image_type': obj.image_type,
                        'prompt': (obj.prompt or '')[:200],
                        'file_path': obj.file_path,
                        'url': obj.get_full_url(),
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            if media_type in ('video', 'all'):
                qs = _qs(VideoHistory)
                if content_type:
                    qs = qs.filter(video_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'video',
                        'video_type': obj.video_type,
                        'prompt': (obj.prompt or '')[:200],
                        'video_url': obj.video_url or '',
                        'thumbnail_url': obj.thumbnail_url or '',
                        'duration': obj.duration,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            if media_type in ('audio', 'all'):
                qs = _qs(AudioHistory)
                if content_type:
                    qs = qs.filter(audio_type=content_type)
                for obj in qs.order_by('-created_at')[:limit]:
                    items.append({
                        'id': str(obj.id), 'media_type': 'audio',
                        'filename': obj.filename,
                        'audio_type': obj.audio_type,
                        'prompt': (obj.prompt or '')[:200],
                        'voice_name': obj.voice_name or '',
                        'file_path': obj.file_path,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    })

            # Sort combined results by created_at descending, take limit
            items.sort(key=lambda x: x.get('created_at') or '', reverse=True)
            items = items[:limit]
            return {'action': 'list', 'count': len(items), 'items': items}

        elif action == 'detail':
            mid = payload.get('id')
            if not mid:
                raise ValueError("id parameter required for detail action")

            # Search across all three models
            for model, mtype, extra_fields in [
                (ImageHistory, 'image', lambda o: {
                    'filename': o.filename, 'image_type': o.image_type,
                    'file_path': o.file_path, 'url': o.get_full_url(),
                    'model_used': o.model_used,
                    'style': o.style, 'prompt': o.prompt or '',
                }),
                (VideoHistory, 'video', lambda o: {
                    'video_type': o.video_type, 'video_url': o.video_url or '',
                    'thumbnail_url': o.thumbnail_url or '',
                    'duration': o.duration, 'ratio': o.ratio,
                    'video_width': o.video_width, 'video_height': o.video_height,
                    'model_used': o.model_used, 'prompt': o.prompt or '',
                }),
                (AudioHistory, 'audio', lambda o: {
                    'filename': o.filename, 'audio_type': o.audio_type,
                    'file_path': o.file_path,
                    'url': o.get_full_url() if hasattr(o, 'get_full_url') else o.file_path,
                    'voice_id': o.voice_id,
                    'voice_name': o.voice_name or '', 'prompt': o.prompt or '',
                }),
            ]:
                obj = _qs(model).filter(id=mid).first()
                if obj:
                    result = {
                        'action': 'detail', 'id': str(obj.id),
                        'media_type': mtype,
                        'created_at': obj.created_at.isoformat() if obj.created_at else None,
                    }
                    result.update(extra_fields(obj))
                    return result

            raise ValueError(f"Media asset {mid} not found")

        elif action == 'stats':
            counts = {}
            if media_type in ('image', 'all'):
                counts['images'] = _qs(ImageHistory).count()
            if media_type in ('video', 'all'):
                counts['videos'] = _qs(VideoHistory).count()
            if media_type in ('audio', 'all'):
                counts['audio'] = _qs(AudioHistory).count()
            counts['total'] = sum(counts.values())
            return {'action': 'stats', **counts}

        elif action == 'delete':
            mid = payload.get('id')
            if not mid:
                raise ValueError("id parameter required for delete action")

            for model, mtype in [
                (ImageHistory, 'image'),
                (VideoHistory, 'video'),
                (AudioHistory, 'audio'),
            ]:
                obj = _qs(model).filter(id=mid).first()
                if obj:
                    info = getattr(obj, 'filename', '') or getattr(obj, 'video_url', '') or str(mid)
                    obj.delete()
                    return {
                        'action': 'delete', 'id': str(mid),
                        'media_type': mtype, 'message': f'Deleted {mtype} asset: {info}',
                    }

            raise ValueError(f"Media asset {mid} not found")

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_voice_clone(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle voice cloning tool - clone voices, list cloned voices, manage voice profiles."""
        from core.models_voice_marketplace import VoiceProfile, VoiceCloneRequest

        action = payload.get('action', 'list')

        # Helper for user-scoped queries
        def _user_qs(model):
            qs = model.objects.all()
            if user_id:
                qs = qs.filter(owner_id=user_id) if hasattr(model, 'owner') else qs.filter(user_id=user_id)
            return qs

        if action == 'list':
            # List user's cloned voices
            voices = _user_qs(VoiceProfile).filter(is_active=True).order_by('-created_at')[:20]
            items = []
            for v in voices:
                items.append({
                    'id': str(v.id),
                    'name': v.name,
                    'elevenlabs_voice_id': v.elevenlabs_voice_id,
                    'gender': v.gender,
                    'creation_method': v.creation_method,
                    'is_public': v.is_public,
                    'total_uses': v.total_uses,
                    'average_rating': round(v.average_rating, 1),
                    'created_at': v.created_at.isoformat(),
                })
            return {'action': 'list', 'count': len(items), 'voices': items}

        elif action == 'detail':
            voice_id = payload.get('id')
            if not voice_id:
                raise ValueError("id parameter required for detail action")
            voice = VoiceProfile.objects.filter(id=voice_id, is_active=True).first()
            if not voice:
                raise ValueError(f"Voice {voice_id} not found")
            return {
                'action': 'detail',
                'id': str(voice.id),
                'name': voice.name,
                'description': voice.description,
                'elevenlabs_voice_id': voice.elevenlabs_voice_id,
                'gender': voice.gender,
                'age_range': voice.age_range,
                'accent': voice.accent,
                'language': voice.language,
                'style_tags': voice.style_tags,
                'primary_use_case': voice.primary_use_case,
                'creation_method': voice.creation_method,
                'is_public': voice.is_public,
                'price_display': voice.get_price_display(),
                'total_uses': voice.total_uses,
                'average_rating': round(voice.average_rating, 1),
                'owner': voice.owner.username,
                'created_at': voice.created_at.isoformat(),
            }

        elif action == 'clone_requests':
            # List clone request history
            requests = VoiceCloneRequest.objects.all()
            if user_id:
                requests = requests.filter(user_id=user_id)
            requests = requests.order_by('-created_at')[:10]
            items = []
            for r in requests:
                items.append({
                    'id': str(r.id),
                    'status': r.status,
                    'recording_duration': r.recording_duration_seconds,
                    'voice_id': str(r.voice_profile.id) if r.voice_profile else None,
                    'error': r.error_message or None,
                    'created_at': r.created_at.isoformat(),
                })
            return {'action': 'clone_requests', 'count': len(items), 'requests': items}

        elif action == 'marketplace':
            # Browse public marketplace voices
            limit = min(payload.get('limit', 10), 30)
            search = payload.get('search', '')
            from django.db.models import Q
            qs = VoiceProfile.objects.filter(is_public=True, is_active=True)
            if search:
                qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
            qs = qs.order_by('-is_featured', '-average_rating')[:limit]
            items = []
            for v in qs:
                items.append({
                    'id': str(v.id),
                    'name': v.name,
                    'description': (v.description or '')[:150],
                    'gender': v.gender,
                    'price_display': v.get_price_display(),
                    'total_uses': v.total_uses,
                    'average_rating': round(v.average_rating, 1),
                    'owner': v.owner.username,
                })
            return {'action': 'marketplace', 'count': len(items), 'voices': items}

        elif action == 'stats':
            my_voices = _user_qs(VoiceProfile).filter(is_active=True)
            total_public = VoiceProfile.objects.filter(is_public=True, is_active=True).count()
            return {
                'action': 'stats',
                'my_voices': my_voices.count(),
                'marketplace_total': total_public,
                'my_total_uses': sum(v.total_uses for v in my_voices),
                'my_total_revenue': str(sum(v.total_revenue for v in my_voices)),
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. "
                f"Available: list, detail, clone_requests, marketplace, stats"
            )

    def _handle_davinci(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle DaVinci Resolve control surface tool."""
        from core.agents.resolve_agent import ResolveNodeClient

        client = ResolveNodeClient()
        action = payload.get('action', 'health')

        if action == 'health':
            result = client.health_check()
            return {'action': 'health', **result}

        elif action == 'render':
            clip_paths = payload.get('clip_paths')
            if not clip_paths:
                raise ValueError("clip_paths required for render action")
            template = payload.get('template', 'default_mp4')
            timeline_name = payload.get('timeline_name')
            result = client.start_render(
                clip_paths=clip_paths,
                template=template,
                timeline_name=timeline_name,
            )
            return {'action': 'render', **result}

        elif action == 'status':
            job_id = payload.get('job_id')
            if not job_id:
                raise ValueError("job_id required for status action")
            result = client.get_status(job_id)
            return {'action': 'status', **result}

        elif action == 'result':
            job_id = payload.get('job_id')
            if not job_id:
                raise ValueError("job_id required for result action")
            url = client.get_result_url(job_id)
            return {'action': 'result', 'job_id': job_id, 'download_url': url}

        elif action == 'jobs':
            result = client.list_jobs()
            return {'action': 'jobs', **result}

        elif action == 'grades':
            from resolve_node.color_grades import COLOR_GRADE_PRESETS
            grades = [
                {'name': name, 'description': g.get('description', ''), 'use_case': g.get('use_case', '')}
                for name, g in COLOR_GRADE_PRESETS.items()
            ]
            return {'action': 'grades', 'count': len(grades), 'grades': grades}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_obs(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle OBS recording control tool via platform proxy endpoints."""
        from core.views_obs import _obs_enabled, _obs_bridge_request

        action = payload.get('action', 'health')

        if not _obs_enabled():
            return {'ok': False, 'action': action, 'error': {'code': 'OBS_DISABLED', 'message': 'OBS integration is not enabled'}}

        action_map = {
            'health':      ('GET',  '/health', None, 5),
            'status':      ('GET',  '/v1/recording/status', None, 15),
            'start':       ('POST', '/v1/recording/start', None, 15),
            'stop':        ('POST', '/v1/recording/stop', None, 15),
            'last':        ('GET',  '/v1/recording/last', None, 15),
        }

        if action == 'upload_last':
            body = {}
            if payload.get('stopIfRecording'):
                body['stopIfRecording'] = True
            if payload.get('title'):
                body['title'] = payload['title']
            if payload.get('tags'):
                body['tags'] = payload['tags']
            status_code, data, latency = _obs_bridge_request(
                'POST', '/v1/recording/upload_last',
                body=body if body else None,
                timeout=60,
            )
        elif action in action_map:
            method, path, body, timeout = action_map[action]
            status_code, data, latency = _obs_bridge_request(method, path, body, timeout)
        else:
            raise ValueError(f"Unknown obs_tool action: {action}")

        if status_code == 0:
            return {'ok': False, 'action': action, 'bridgeReachable': False,
                    'error': {'code': 'BRIDGE_UNREACHABLE', 'message': data.get('error', 'Bridge unreachable')}}
        if status_code == 401:
            return {'ok': False, 'action': action, 'bridgeReachable': True,
                    'error': {'code': 'BRIDGE_AUTH_FAILED', 'message': 'Bridge rejected token'}}

        return {
            'ok': data.get('ok', True),
            'action': action,
            'bridgeReachable': True,
            'latency_ms': latency,
            'result': data,
        }

    def _handle_video_history(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle video history tool — list, search, detail."""
        from content.models import VideoHistory
        from django.db.models import Q

        action = payload.get('action', 'list')
        limit = min(payload.get('limit', 10), 50)

        def _qs():
            qs = VideoHistory.objects.all()
            if user_id:
                qs = qs.filter(user_id=user_id)
            return qs

        def _serialize(v):
            return {
                'id': str(v.id),
                'sequential_number': v.get_sequential_number(),
                'title': (v.prompt or '')[:200],
                'original_filename': v.original_filename or '',
                'video_url': v.video_url or '',
                'thumbnail_url': v.thumbnail_url or '',
                'video_type': v.video_type or '',
                'source_type': getattr(v, 'source_type', ''),
                'status': v.status or '',
                'duration': v.duration,
                'resolution': f"{v.video_width}x{v.video_height}" if v.video_width else None,
                'file_size_bytes': v.file_size_bytes,
                'created_at': v.created_at.isoformat() if v.created_at else None,
            }

        if action == 'list':
            qs = _qs()
            if payload.get('video_type'):
                qs = qs.filter(video_type=payload['video_type'])
            if payload.get('status'):
                qs = qs.filter(status=payload['status'])
            else:
                qs = qs.filter(status='completed')
            videos = [_serialize(v) for v in qs.order_by('-created_at')[:limit]]
            return {'action': 'list', 'count': len(videos), 'videos': videos}

        elif action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query parameter required for search action")
            qs = _qs().filter(
                Q(prompt__icontains=query) | Q(original_filename__icontains=query)
            ).filter(status='completed')
            videos = [_serialize(v) for v in qs.order_by('-created_at')[:limit]]
            return {'action': 'search', 'query': query, 'count': len(videos), 'videos': videos}

        elif action == 'detail':
            vid = payload.get('id')
            seq = payload.get('sequential_number')
            if not vid and not seq:
                raise ValueError("id or sequential_number required for detail action")
            if vid:
                v = _qs().filter(id=vid).first()
            else:
                # sequential_number is computed, not a DB field — get all user videos ordered by created_at and index
                all_videos = list(_qs().order_by('created_at').values_list('id', flat=True))
                if seq and 1 <= seq <= len(all_videos):
                    v = _qs().filter(id=all_videos[seq - 1]).first()
                else:
                    v = None
            if not v:
                raise ValueError("Video not found")
            detail = _serialize(v)
            detail.update({
                'model_used': v.model_used or '',
                'tags': v.tags,
                'user_notes': v.user_notes or '',
                'is_favorite': v.is_favorite,
                'view_count': v.view_count,
                'download_count': v.download_count,
                'fps': v.fps,
                'codec': v.codec,
                'ratio': v.ratio,
                'view_url': '/video-studio',
            })
            return {'action': 'detail', 'video': detail}

        elif action == 'resolve':
            from core.video_resolver import resolve_video
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            elif payload.get('query'):
                ref['url'] = payload['query']
            if not ref:
                raise ValueError("Provide id, sequential_number, or query (URL) for resolve")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            return {'action': 'resolve', 'video': resolved.to_dict()}

        elif action == 'transcribe':
            from content.models import VideoTranscript
            from core.video_resolver import resolve_video
            from core.tasks import transcribe_video_task
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            if not ref:
                raise ValueError("Provide id or sequential_number to transcribe")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            video = _qs().get(id=resolved.id)
            # Check existing
            existing = VideoTranscript.objects.filter(
                video=video, status__in=['queued', 'running']
            ).first()
            if existing:
                return {'action': 'transcribe', 'transcript_id': str(existing.id),
                        'status': existing.status, 'message': 'Already in progress'}
            transcript = VideoTranscript.objects.create(
                video=video, language=payload.get('language', 'en'), status='queued')
            transcribe_video_task.delay(str(transcript.id))
            return {'action': 'transcribe', 'transcript_id': str(transcript.id),
                    'status': 'queued', 'video_title': resolved.title}

        elif action == 'transcript_status':
            from content.models import VideoTranscript
            tid = payload.get('transcript_id')
            if not tid:
                # Get latest for a video
                ref = {}
                if payload.get('id'):
                    ref['id'] = payload['id']
                elif payload.get('sequential_number'):
                    ref['sequential_number'] = payload['sequential_number']
                if ref:
                    from core.video_resolver import resolve_video
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id) if user_id else None
                    resolved = resolve_video(ref, user=user)
                    if resolved:
                        t = VideoTranscript.objects.filter(video_id=resolved.id).order_by('-created_at').first()
                        if t:
                            tid = str(t.id)
                if not tid:
                    raise ValueError("Provide transcript_id, or id/sequential_number of the video")
            t = VideoTranscript.objects.get(id=tid)
            result = {
                'action': 'transcript_status',
                'transcript_id': str(t.id),
                'status': t.status,
                'language': t.language,
                'error': t.error or None,
            }
            if t.status == 'completed':
                result['text'] = t.text[:3000]
                result['text_length'] = len(t.text)
                result['segment_count'] = len(t.segments_json) if t.segments_json else 0
                result['duration_seconds'] = t.duration_seconds
                if len(t.text) > 3000:
                    result['truncated'] = True
            return result

        elif action == 'content_pack':
            from content.models import VideoTranscript
            from core.video_resolver import resolve_video
            from core.tasks import generate_video_content_pack_task
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id) if user_id else None
            ref = {}
            if payload.get('id'):
                ref['id'] = payload['id']
            elif payload.get('sequential_number'):
                ref['sequential_number'] = payload['sequential_number']
            if not ref:
                raise ValueError("Provide id or sequential_number for content_pack")
            resolved = resolve_video(ref, user=user)
            if not resolved:
                raise ValueError("Video not found")
            # Verify transcript exists
            has_transcript = VideoTranscript.objects.filter(
                video_id=resolved.id, status='completed'
            ).exists()
            if not has_transcript:
                raise ValueError("No completed transcript. Transcribe the video first.")
            task = generate_video_content_pack_task.delay(
                resolved.id, str(user_id), payload.get('language', 'en')
            )
            return {
                'action': 'content_pack',
                'task_id': str(task.id),
                'status': 'queued',
                'video_title': resolved.title,
                'message': 'Content pack generation started. Check task status for results.',
            }

        else:
            raise ValueError(f"Unknown video_history_tool action: {action}")

    def _handle_body_vitals(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle body vitals tool."""
        from core.services.body_vitals import get_body_vitals_service

        systems = payload.get('systems', ['all'])
        include_details = payload.get('include_details', False)

        vitals = get_body_vitals_service()

        if 'all' in systems:
            result = vitals.get_all_vitals(include_details=include_details)
        else:
            # get_system_vitals takes one system at a time
            result = {}
            for system_name in systems:
                result[system_name] = vitals.get_system_vitals(
                    system_name, include_details=include_details
                )

        return {
            'systems_requested': systems,
            'vitals': result,
        }

    def _handle_check_budget(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle budget check tool."""
        from core.services.body_vitals import get_body_vitals_service

        estimated_tokens = payload.get('estimated_tokens', 0)
        estimated_cost = payload.get('estimated_cost', 0)

        vitals = get_body_vitals_service()
        budget = vitals.check_budget(estimated_tokens, estimated_cost)

        return {
            'estimated_tokens': estimated_tokens,
            'estimated_cost': estimated_cost,
            'budget_status': budget.get('status', 'unknown'),
            'oxygen_level': budget.get('oxygen_level', 0),
            'can_proceed': budget.get('can_proceed', True),
            'warning': budget.get('warning'),
            'recommendation': budget.get('recommendation'),
        }

    # Schema-to-handler severity-domain mapping (S2906 drift fix).
    # Schema exposes 4 marketing-standard levels (critical/high/medium/low);
    # BodyCoordinator alerts use 3 log-level-standard values (info/warning/
    # critical). Mapping is intentionally lossy on the schema side — `high`
    # and `medium` both collapse to `warning` — because the handler-side
    # substrate has no distinct threshold between them. Full drift context:
    # `docs/research/tools/validation/get_system_alerts_validation.md` §5.
    _SEVERITY_SCHEMA_TO_INTERNAL: Dict[str, str] = {
        'critical': 'critical',
        'high': 'warning',
        'medium': 'warning',
        'low': 'info',
    }

    def _handle_system_alerts(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle system alerts tool.

        Accepts `severity` (schema-declared, preferred) or `severity_threshold`
        (legacy handler param) — S2906 drift fix. When both are present,
        `severity` wins. Schema enum values map into the handler's internal
        info/warning/critical domain via ``_SEVERITY_SCHEMA_TO_INTERNAL``.
        Unknown values fall through to the ``warning`` default.
        """
        from core.services.body_vitals import get_body_vitals_service

        severity_order = ['info', 'warning', 'critical']

        raw_severity = payload.get('severity')
        raw_threshold = payload.get('severity_threshold')

        if raw_severity is not None:
            severity_threshold = self._SEVERITY_SCHEMA_TO_INTERNAL.get(
                raw_severity, 'warning'
            )
        elif raw_threshold is not None:
            # Legacy path: normalize unknown values to 'warning' so callers
            # passing invalid severity_threshold (e.g. 'HIGH', 'medium' from
            # the schema domain) don't silently downgrade to 'info' —
            # Rigby S2906 T1 SIGN B edit.
            severity_threshold = (
                raw_threshold if raw_threshold in severity_order else 'warning'
            )
        else:
            severity_threshold = 'warning'

        vitals = get_body_vitals_service()
        all_vitals = vitals.get_all_vitals()

        alerts = all_vitals.get('alerts', [])

        # Filter by severity
        threshold_idx = severity_order.index(severity_threshold) if severity_threshold in severity_order else 0

        filtered_alerts = [
            a for a in alerts
            if severity_order.index(a.get('severity', 'info')) >= threshold_idx
        ]

        return {
            'severity_threshold': severity_threshold,
            'alert_count': len(filtered_alerts),
            'alerts': filtered_alerts,
        }

    def _handle_cost_telemetry(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 1036: Cost telemetry tool — real spend data from LLMCallLog.

        Returns last 24h spend, top agents by cost, cost by task type, trend.
        """
        from core.models_llm_routing import LLMCallLog
        from django.db.models import Sum, Count, Avg, F, Q
        from django.utils import timezone
        from datetime import timedelta

        action = payload.get('action', 'summary')
        hours = payload.get('hours', 24)
        limit = min(payload.get('limit', 10), 50)

        now = timezone.now()
        cutoff = now - timedelta(hours=hours)

        base_qs = LLMCallLog.objects.filter(created_at__gte=cutoff)

        if action == 'summary':
            # Overall spend summary
            totals = base_qs.aggregate(
                total_cost=Sum('cost'),
                total_calls=Count('id'),
                total_tokens=Sum('total_tokens'),
                avg_latency=Avg('latency_ms'),
                failed_calls=Count('id', filter=Q(success=False)),
            )

            # Cost by provider
            by_provider = list(
                base_qs.values('provider', 'model_id')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                    tokens=Sum('total_tokens'),
                )
                .order_by('-spend')[:10]
            )

            # Cost by task type
            by_task_type = list(
                base_qs.values('task_type')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                )
                .order_by('-spend')[:10]
            )

            # Trend: compare current period to previous same-length period
            prev_cutoff = cutoff - timedelta(hours=hours)
            prev_totals = LLMCallLog.objects.filter(
                created_at__gte=prev_cutoff,
                created_at__lt=cutoff,
            ).aggregate(
                total_cost=Sum('cost'),
                total_calls=Count('id'),
            )

            current_cost = float(totals['total_cost'] or 0)
            prev_cost = float(prev_totals['total_cost'] or 0)
            cost_change_pct = (
                round((current_cost - prev_cost) / prev_cost * 100, 1)
                if prev_cost > 0 else None
            )

            return {
                'action': 'summary',
                'period_hours': hours,
                'total_cost_usd': round(current_cost, 4),
                'total_calls': totals['total_calls'] or 0,
                'total_tokens': totals['total_tokens'] or 0,
                'avg_latency_ms': round(float(totals['avg_latency'] or 0), 0),
                'failed_calls': totals['failed_calls'] or 0,
                'by_provider': [
                    {
                        'provider': r['provider'],
                        'model': r['model_id'],
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                        'tokens': r['tokens'] or 0,
                    }
                    for r in by_provider
                ],
                'by_task_type': [
                    {
                        'task_type': r['task_type'] or 'unknown',
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                    }
                    for r in by_task_type
                ],
                'trend': {
                    'previous_period_cost_usd': round(prev_cost, 4),
                    'cost_change_pct': cost_change_pct,
                },
                'generated_at': now.isoformat(),
            }

        elif action == 'top_agents':
            # Top N agents by cost
            top_agents = list(
                base_qs.values('agent_name')
                .annotate(
                    spend=Sum('cost'),
                    calls=Count('id'),
                    tokens=Sum('total_tokens'),
                    avg_latency=Avg('latency_ms'),
                    failures=Count('id', filter=Q(success=False)),
                )
                .order_by('-spend')[:limit]
            )

            return {
                'action': 'top_agents',
                'period_hours': hours,
                'agents': [
                    {
                        'agent_name': r['agent_name'],
                        'spend_usd': round(float(r['spend'] or 0), 4),
                        'calls': r['calls'],
                        'tokens': r['tokens'] or 0,
                        'avg_latency_ms': round(float(r['avg_latency'] or 0), 0),
                        'failures': r['failures'],
                    }
                    for r in top_agents
                ],
                'generated_at': now.isoformat(),
            }

        elif action == 'recent_calls':
            # Most recent N calls (for debugging)
            recent = list(
                base_qs.order_by('-created_at')
                .values(
                    'agent_name', 'provider', 'model_id', 'task_type',
                    'total_tokens', 'cost', 'latency_ms', 'success',
                    'error_message', 'created_at',
                )[:limit]
            )

            return {
                'action': 'recent_calls',
                'period_hours': hours,
                'calls': [
                    {
                        'agent': r['agent_name'],
                        'provider': r['provider'],
                        'model': r['model_id'],
                        'task_type': r['task_type'],
                        'tokens': r['total_tokens'],
                        'cost_usd': round(float(r['cost'] or 0), 6),
                        'latency_ms': r['latency_ms'],
                        'success': r['success'],
                        'error': r['error_message'][:200] if r['error_message'] else None,
                        'at': r['created_at'].isoformat() if r['created_at'] else None,
                    }
                    for r in recent
                ],
                'generated_at': now.isoformat(),
            }

        else:
            return _handler_error(
                action,
                'unknown_action',
                f'Unknown action: {action}. Supported: summary, top_agents, recent_calls',
            )

    def _handle_predictions(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle predictions tool.

        NOTE: AgentPrediction model is DEPRECATED (Session 284).
        This handler returns deprecation notice instead of querying dead model.
        """
        action = payload.get('action', 'list')

        # Return deprecation notice for all actions
        return {
            'action': action,
            'deprecated': True,
            'message': (
                'AgentPrediction is deprecated (Session 284). '
                'No predictions have ever been recorded. '
                'Use HumanAttentionItem for tracking opportunities and decisions instead.'
            ),
            'count': 0,
            'predictions': [],
        }

    def _handle_gates(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle gates tool.

        NOTE: Session 933 audit - PilotReadinessGate has no 'name' field.
        Uses 'summary' and 'decision__topic' instead.
        """
        from core.models_pilot_readiness import PilotReadinessGate

        action = payload.get('action', 'list')
        # Session G3: Alias 'details' -> 'detail'
        ACTION_ALIASES = {'details': 'detail'}
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)  # Session 1057: Reduced from 20 to match schema

        if action == 'list':
            gates = list(
                PilotReadinessGate.objects.select_related('decision').order_by('-created_at')[:limit].values(
                    'id', 'summary', 'status', 'risk_level', 'created_at', 'decision__topic'
                )
            )
            # Flatten decision__topic to topic for cleaner response
            # Session 987: Serialize UUIDs and datetimes for clean display
            # Session 1057: Truncate summary to prevent GPT-5.2 rendering failure on large results
            for gate in gates:
                gate['topic'] = gate.pop('decision__topic', '')
                gate['id'] = str(gate['id'])
                if gate.get('created_at'):
                    gate['created_at'] = gate['created_at'].isoformat()
                if gate.get('summary') and len(gate['summary']) > 200:
                    gate['summary'] = gate['summary'][:200] + '...'
            return {'action': 'list', 'count': len(gates), 'gates': gates}

        elif action == 'detail':
            gate_id = payload.get('id', '')
            if not gate_id:
                raise ValueError("id is required for detail action")
            gate = PilotReadinessGate.objects.select_related('decision').filter(id=gate_id).first()
            if not gate:
                return {'action': 'detail', 'found': False, 'id': gate_id}
            return {
                'action': 'detail', 'found': True,
                'gate': {
                    'id': str(gate.id),
                    'summary': gate.summary,
                    'status': gate.status,
                    'risk_level': gate.risk_level,
                    'created_at': gate.created_at.isoformat() if gate.created_at else None,
                    'topic': gate.decision.topic if gate.decision else '',
                },
            }

        elif action == 'stats':
            from django.db.models import Count
            total = PilotReadinessGate.objects.count()
            by_status = dict(
                PilotReadinessGate.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
            )
            by_risk = dict(
                PilotReadinessGate.objects.values('risk_level').annotate(c=Count('id')).values_list('risk_level', 'c')
            )
            return {'action': 'stats', 'total': total, 'by_status': by_status, 'by_risk_level': by_risk}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_pilots(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle pilots tool - track pilot executions and outcomes."""
        from core.models_pilot_readiness import PilotExecution

        action = payload.get('action', 'list')
        # Session G3: Alias 'details' -> 'detail'
        ACTION_ALIASES = {'details': 'detail'}
        action = ACTION_ALIASES.get(action, action)
        limit = payload.get('limit', 10)  # Session 1057: Reduced from 20 to match schema

        if action == 'detail':
            pilot_id = payload.get('id', '')
            if not pilot_id:
                raise ValueError("id is required for detail action")
            pilot = PilotExecution.objects.filter(id=pilot_id).first()
            if not pilot:
                return {'action': 'detail', 'found': False, 'id': pilot_id}
            return {
                'action': 'detail', 'found': True,
                'pilot': {
                    'id': str(pilot.id),
                    'name': pilot.name,
                    'status': pilot.status,
                    'outcome': pilot.outcome,
                    'created_at': pilot.created_at.isoformat() if pilot.created_at else None,
                },
            }

        elif action == 'list':
            pilots = list(
                PilotExecution.objects.order_by('-created_at')[:limit].values(
                    'id', 'name', 'status', 'outcome', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            # Session 1057: Truncate name to prevent GPT-5.2 rendering failure
            for pilot in pilots:
                pilot['id'] = str(pilot['id'])
                if pilot.get('created_at'):
                    pilot['created_at'] = pilot['created_at'].isoformat()
                if pilot.get('name') and len(pilot['name']) > 150:
                    pilot['name'] = pilot['name'][:150] + '...'
            return {'action': 'list', 'count': len(pilots), 'pilots': pilots}

        elif action == 'running':
            pilots = list(
                PilotExecution.objects.filter(status='running').values(
                    'id', 'name', 'status', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            for pilot in pilots:
                pilot['id'] = str(pilot['id'])
                if pilot.get('created_at'):
                    pilot['created_at'] = pilot['created_at'].isoformat()
                if pilot.get('name') and len(pilot['name']) > 150:
                    pilot['name'] = pilot['name'][:150] + '...'
            return {'action': 'running', 'count': len(pilots), 'pilots': pilots}

        elif action == 'stats':
            from django.db.models import Count
            total = PilotExecution.objects.count()
            by_status = dict(
                PilotExecution.objects.values('status').annotate(c=Count('id')).values_list('status', 'c')
            )
            by_outcome = dict(
                PilotExecution.objects.values('outcome').annotate(c=Count('id')).values_list('outcome', 'c')
            )
            return {'action': 'stats', 'total': total, 'by_status': by_status, 'by_outcome': by_outcome}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_human_decisions(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Handle human decisions tool.

        NOTE: Session 933 audit - Uses HumanAttentionItem (not HumanDecisionItem which doesn't exist).
        Field mappings: description → summary, feedback → decision_feedback
        """
        from core.models_human_interface import HumanAttentionItem

        action = payload.get('action', 'list')
        limit = payload.get('limit', 10)

        # Build base queryset - filter by user if available
        base_qs = HumanAttentionItem.objects
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)

        if action == 'list':
            items = list(
                base_qs.filter(
                    status__in=['pending', 'viewed']
                ).order_by('-priority_score', '-created_at')[:limit].values(
                    'id', 'title', 'summary', 'urgency', 'item_type', 'created_at',
                    'source_agent', 'ml_recommendation'
                )
            )
            return {'action': 'list', 'count': len(items), 'items': items}

        elif action == 'stats':
            from django.db.models import Count
            total = base_qs.count()
            pending = base_qs.filter(status__in=['pending', 'viewed']).count()
            by_urgency = dict(
                base_qs.filter(status__in=['pending', 'viewed']).values('urgency').annotate(
                    c=Count('id')
                ).values_list('urgency', 'c')
            )
            by_type = dict(
                base_qs.filter(status__in=['pending', 'viewed']).values('item_type').annotate(
                    c=Count('id')
                ).values_list('item_type', 'c')
            )
            return {
                'action': 'stats',
                'total': total,
                'pending': pending,
                'by_urgency': by_urgency,
                'by_type': by_type,
            }

        elif action == 'decide':
            item_id = payload.get('item_id')
            decision = payload.get('decision')
            feedback = payload.get('feedback', '')

            if not item_id or not decision:
                raise ValueError("item_id and decision are required")

            item = base_qs.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Attention item {item_id} not found")

            # Use the model's record_decision method for proper status handling
            item.record_decision(
                decision=decision,
                feedback=feedback,
            )

            return {
                'action': 'decide',
                'item_id': str(item_id),
                'decision': decision,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'create':
            if not user_id:
                raise ValueError("User context required to create a decision request")

            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create action")

            summary = payload.get('summary', '').strip() or title
            item_type = payload.get('item_type', 'decision')
            urgency = payload.get('urgency', 'medium')

            item = HumanAttentionItem.objects.create(
                user_id=user_id,
                title=title[:200],
                summary=summary,
                item_type=item_type,
                urgency=urgency,
                source_type='pa',
                source_agent=PA_IDENTITY,
                status='pending',
            )
            return {
                'action': 'create',
                'id': str(item.id),
                'title': item.title,
                'item_type': item.item_type,
                'urgency': item.urgency,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid: list, stats, decide, create")

    def _handle_reasoning_engine(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle reasoning engine tool."""
        from core.agents.registry import get_agent_registry

        action = payload.get('action', 'status')

        if action == 'status':
            return {
                'action': 'status',
                'engine': 'ThinkingAgent',
                'status': 'operational',
            }

        elif action == 'thoughts':
            limit = payload.get('limit', 10)
            # Get recent thought cycles from AgentExecution
            # S2911: fixed FK traversal. AgentExecution has `agent` FK to Agent;
            # Agent has `name` field (not `agent_name`). Prior code used the
            # non-existent field `agent_name` and raised FieldError at first
            # dispatch. Caught during batch 6a schema-drift-fix harness run.
            from core.models import AgentExecution
            thoughts = list(
                AgentExecution.objects.filter(
                    agent__name='ThinkingAgent'
                ).order_by('-created_at')[:limit].values(
                    'id', 'task', 'status', 'created_at'
                )
            )
            # Session 987: Serialize UUIDs and datetimes for clean display
            for thought in thoughts:
                thought['id'] = str(thought['id'])
                if thought.get('created_at'):
                    thought['created_at'] = thought['created_at'].isoformat()
            return {'action': 'thoughts', 'count': len(thoughts), 'thoughts': thoughts}

        elif action == 'trigger':
            # Trigger a new thinking cycle
            # Session 948: Use execute_agent instead of calling .run() on metadata dict
            registry = get_agent_registry()
            agent_metadata = registry.get_agent('ThinkingAgent')
            if agent_metadata:
                task_data = {'task': "Reflect on recent system activity and generate insights"}
                result = registry.execute_agent('ThinkingAgent', task_data)
                return {
                    'action': 'trigger',
                    'triggered': True,
                    'output': result if result else 'Thinking cycle triggered',
                }
            else:
                return {'action': 'trigger', 'triggered': False, 'error': 'ThinkingAgent not found'}

        else:
            raise ValueError(f"Unknown action: {action}")

    def _handle_boardroom(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 940: Comprehensive boardroom tool for PA to act on pending items.

        Actions:
        - stats: Get overall boardroom statistics
        - list_attention: List pending attention items
        - list_decisions: List draft decisions
        - approve_attention: Approve an attention item (id required)
        - ignore_attention: Ignore an attention item (id required)
        - promote_decision: Promote a draft decision to canonical (id required)
        - reject_decision: Reject a draft decision (id required)
        """
        from core.models_human_interface import HumanAttentionItem
        from core.models_unified_system import AgentDecisionSummary
        from django.db.models import Count

        action = payload.get('action', 'stats')
        limit = payload.get('limit', 10)
        item_type_filter = payload.get('item_type')
        decision_type_filter = payload.get('decision_type')
        urgency_filter = payload.get('urgency')

        # Build base querysets - filter by user if available
        attention_qs = HumanAttentionItem.objects.filter(status='pending')
        if user_id:
            attention_qs = attention_qs.filter(user_id=user_id)

        decisions_qs = AgentDecisionSummary.objects.filter(status='draft')

        if action == 'stats':
            # Get attention item stats
            attention_count = attention_qs.count()
            attention_by_urgency = dict(
                attention_qs.values('urgency')
                .annotate(count=Count('id'))
                .values_list('urgency', 'count')
            )
            attention_by_type = dict(
                attention_qs.values('item_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('item_type', 'count')
            )

            # Session 985: Fetch top critical/high items so PA can reference
            # actual items instead of just counts
            top_items = list(
                attention_qs.filter(urgency__in=['critical', 'high'])
                .order_by('-priority_score', '-created_at')[:10]
                .values(
                    'id', 'title', 'summary', 'urgency', 'item_type',
                    'source_agent', 'priority_score', 'created_at'
                )
            )

            # Get decision stats
            decision_count = decisions_qs.count()
            decisions_by_type = dict(
                decisions_qs.values('decision_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
                .values_list('decision_type', 'count')
            )

            return {
                'action': 'stats',
                'total_pending': attention_count + decision_count,
                'attention_items': {
                    'count': attention_count,
                    'by_urgency': attention_by_urgency,
                    'by_type': attention_by_type,
                },
                'draft_decisions': {
                    'count': decision_count,
                    'by_type': decisions_by_type,
                },
                'top_items': top_items,
            }

        # Session 1000B: Lookup item by title or ID
        elif action == 'lookup':
            item_id = payload.get('id', '')
            title_query = payload.get('title_query', '')

            # Session 1097: Direct ID lookup — fast path
            if item_id:
                item = HumanAttentionItem.objects.filter(id=item_id).first()
                if item:
                    return {
                        'action': 'lookup',
                        'found': True,
                        'item_type': 'attention',
                        'id': str(item.id),
                        'title': item.title,
                        'summary': item.summary or '',
                        'urgency': item.urgency or 'medium',
                        'status': item.status,
                        'source_agent': item.source_agent or '',
                        'item_category': item.item_type or '',
                        'created_at': item.created_at.isoformat() if item.created_at else '',
                        'priority_score': item.priority_score,
                        'ml_recommendation': getattr(item, 'ml_recommendation', '') or '',
                        'impact_estimate': getattr(item, 'impact_estimate', '') or '',
                        'payload': item.payload if isinstance(item.payload, dict) else {},
                    }
                # Try decisions by ID
                decision = AgentDecisionSummary.objects.filter(id=item_id).first()
                if decision:
                    return {
                        'action': 'lookup',
                        'found': True,
                        'item_type': 'decision',
                        'id': str(decision.id),
                        'title': decision.topic,
                        'summary': decision.key_insights or '',
                        'decision_type': decision.decision_type or '',
                        'recommended_stance': decision.recommended_stance or '',
                        'impact_area': decision.impact_area or '',
                        'status': decision.status,
                        'created_at': decision.created_at.isoformat() if decision.created_at else '',
                    }
                return {'action': 'lookup', 'found': False, 'id': item_id, 'error': 'Item not found'}

            if not title_query:
                return {'action': 'lookup', 'found': False, 'error': 'Provide id or title_query'}

            # Search attention items first (most common source of "tell me more")
            item = (
                HumanAttentionItem.objects
                .filter(title__icontains=title_query[:80])
                .order_by('-created_at')
                .first()
            )
            if not item:
                # Broaden: try first few significant words
                words = [w for w in title_query.split() if len(w) > 3][:4]
                if words:
                    from django.db.models import Q
                    q = Q()
                    for w in words:
                        q &= Q(title__icontains=w)
                    item = (
                        HumanAttentionItem.objects
                        .filter(q)
                        .order_by('-created_at')
                        .first()
                    )

            if item:
                return {
                    'action': 'lookup',
                    'found': True,
                    'item_type': 'attention',
                    'title': item.title,
                    'summary': item.summary or '',
                    'urgency': item.urgency or 'medium',
                    'status': item.status,
                    'source_agent': item.source_agent or '',
                    'item_category': item.item_type or '',
                    'created_at': item.created_at.isoformat() if item.created_at else '',
                    'priority_score': item.priority_score,
                    'ml_recommendation': getattr(item, 'ml_recommendation', '') or '',
                    'impact_estimate': getattr(item, 'impact_estimate', '') or '',
                    'payload': item.payload if isinstance(item.payload, dict) else {},
                }

            # Try decisions
            decision = (
                AgentDecisionSummary.objects
                .filter(topic__icontains=title_query[:80])
                .order_by('-created_at')
                .first()
            )
            if decision:
                return {
                    'action': 'lookup',
                    'found': True,
                    'item_type': 'decision',
                    'title': decision.topic,
                    'summary': decision.key_insights or '',
                    'decision_type': decision.decision_type or '',
                    'recommended_stance': decision.recommended_stance or '',
                    'impact_area': decision.impact_area or '',
                    'status': decision.status,
                    'created_at': decision.created_at.isoformat() if decision.created_at else '',
                }

            return {'action': 'lookup', 'found': False, 'query': title_query}

        elif action == 'list_attention':
            # Apply filters
            qs = attention_qs
            if item_type_filter:
                qs = qs.filter(item_type=item_type_filter)
            if urgency_filter:
                qs = qs.filter(urgency=urgency_filter)

            items = list(
                qs.order_by('-priority_score', '-created_at')[:limit].values(
                    'id', 'title', 'summary', 'urgency', 'item_type',
                    'created_at', 'source_agent', 'ml_recommendation',
                    'priority_score', 'ml_confidence', 'impact_estimate'
                )
            )
            return {
                'action': 'list_attention',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'item_type': item_type_filter,
                    'urgency': urgency_filter,
                }
            }

        elif action == 'list_decisions':
            # Apply filters
            qs = decisions_qs
            if decision_type_filter:
                qs = qs.filter(decision_type=decision_type_filter)

            items = list(
                qs.order_by('-created_at')[:limit].values(
                    'id', 'topic', 'decision_type', 'impact_area',
                    'recommended_stance', 'key_insights', 'created_at'
                )
            )
            return {
                'action': 'list_decisions',
                'count': len(items),
                'items': items,
                'filters_applied': {
                    'decision_type': decision_type_filter,
                }
            }

        elif action == 'approve_attention':
            item_id = payload.get('id')
            feedback = payload.get('feedback', 'Approved via PA')

            if not item_id:
                raise ValueError("id is required for approve_attention")

            item = attention_qs.filter(id=item_id).first()
            if not item:
                raise ValueError(f"Attention item {item_id} not found or not pending")

            # Use the model's record_decision method
            item.record_decision(
                decision='approved',
                feedback=feedback,
            )

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_attention_decision(
                        user=user,
                        item_id=str(item_id),
                        decision='approved',
                        source_agent=item.source_agent or 'Unknown',
                        item_type=item.item_type or 'unknown',
                        urgency=item.urgency or 'medium',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            # Session 1031: Dream approval -> triggers existing signal chain
            if item.source_type == 'dream_pipeline' and item.payload and item.payload.get('dream_id'):
                try:
                    from core.models_unified_system import AgentDream
                    dream = AgentDream.objects.get(id=item.payload['dream_id'])
                    dream.decision_outcome = 'approved'
                    dream.user_reaction = 'loved'
                    dream.user_feedback = feedback
                    dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
                    # post_save signal (dream_signals.py:47) fires automatically:
                    #   1. promote_to_initiative() -> Initiative + Stage 1
                    #   2. execute_single_dream.delay() -> PartnershipProject + workflow
                except Exception as e:
                    logger.warning(f"Dream approval hook failed: {e}")

            return {
                'action': 'approve_attention',
                'id': str(item_id),
                'title': item.title,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'ignore_attention':
            item_id = payload.get('id')
            feedback = payload.get('feedback', 'Ignored via PA')

            if not item_id:
                raise ValueError("id is required for ignore_attention")

            item = attention_qs.filter(id=item_id).first()
            if not item:
                # Session 1075: Idempotent — if item exists but already acted, return success
                already_acted = HumanAttentionItem.objects.filter(id=item_id).first()
                if already_acted:
                    return {
                        'action': 'ignore_attention',
                        'id': str(item_id),
                        'title': already_acted.title,
                        'new_status': already_acted.status,
                        'success': True,
                        'no_op': True,
                        'note': f'Already {already_acted.status}',
                    }
                raise ValueError(f"Attention item {item_id} not found")

            # Use the model's record_decision method
            item.record_decision(
                decision='ignored',
                feedback=feedback,
            )

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_attention_decision(
                        user=user,
                        item_id=str(item_id),
                        decision='ignored',
                        source_agent=item.source_agent or 'Unknown',
                        item_type=item.item_type or 'unknown',
                        urgency=item.urgency or 'medium',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            # Session 1031: Dream dismiss
            if item.source_type == 'dream_pipeline' and item.payload and item.payload.get('dream_id'):
                try:
                    from core.models_unified_system import AgentDream
                    dream = AgentDream.objects.get(id=item.payload['dream_id'])
                    dream.decision_outcome = 'rejected'
                    dream.user_reaction = 'dismissed'
                    dream.user_feedback = feedback
                    dream.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])
                except Exception as e:
                    logger.warning(f"Dream dismiss hook failed: {e}")

            return {
                'action': 'ignore_attention',
                'id': str(item_id),
                'title': item.title,
                'new_status': item.status,
                'success': True,
            }

        elif action == 'promote_decision':
            decision_id = payload.get('id')
            promoted_by = payload.get('promoted_by', 'PA')

            if not decision_id:
                raise ValueError("id is required for promote_decision")

            decision = decisions_qs.filter(id=decision_id).first()
            if not decision:
                raise ValueError(f"Draft decision {decision_id} not found")

            # Promote to canonical
            # S3031: gate broadcast on did_promote to avoid duplicate
            # emits when a competing path already canonicalized this row.
            did_promote = decision.promote_to_canonical(promoted_by=promoted_by)

            # S3028: emit canonical-promotion broadcast so the PA path fires
            # the same event the boardroom UI + Celery auto-promoter fire.
            # Best-effort; never fails the promotion.
            if did_promote:
                from core.services.canonical_decision_broadcast import (
                    ACTOR_PA_TOOL,
                    emit_canonical_promotion_broadcast,
                )
                emit_canonical_promotion_broadcast(decision, actor=ACTOR_PA_TOOL)

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_decision_action(
                        user=user,
                        decision_id=str(decision_id),
                        action='promoted',
                        decision_type=decision.decision_type or 'unknown',
                        impact_area=decision.impact_area or 'unknown',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            return {
                'action': 'promote_decision',
                'id': str(decision_id),
                'topic': decision.topic,
                'new_status': decision.status,
                'is_canonical': decision.is_canonical,
                'success': True,
            }

        elif action == 'reject_decision':
            decision_id = payload.get('id')
            reason = payload.get('reason', 'Rejected via PA')

            if not decision_id:
                raise ValueError("id is required for reject_decision")

            decision = decisions_qs.filter(id=decision_id).first()
            if not decision:
                raise ValueError(f"Draft decision {decision_id} not found")

            # S3034: model method + gated broadcast for lifecycle symmetry
            # with promote_decision. did_reject gates the emit so racing
            # paths don't double-broadcast.
            from core.services.canonical_decision_broadcast import (
                ACTOR_PA_TOOL,
                emit_canonical_rejection_broadcast,
            )
            did_reject = decision.reject(rejected_by='pa')
            if did_reject:
                emit_canonical_rejection_broadcast(decision, actor=ACTOR_PA_TOOL)

            # Session 940: Record for learning
            if user_id:
                try:
                    from core.services.boardroom_learning_service import get_boardroom_learning_service
                    learning_service = get_boardroom_learning_service()
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=user_id)
                    learning_service.record_decision_action(
                        user=user,
                        decision_id=str(decision_id),
                        action='rejected',
                        decision_type=decision.decision_type or 'unknown',
                        impact_area=decision.impact_area or 'unknown',
                        via='PA'
                    )
                except Exception as e:
                    logger.warning(f"Failed to record learning: {e}")

            return {
                'action': 'reject_decision',
                'id': str(decision_id),
                'topic': decision.topic,
                'new_status': decision.status,
                'reason': reason,
                'success': True,
            }

        elif action == 'get_triage_batch':
            # Session 940: Get items for triage mode
            from django.db.models import Case, When, IntegerField

            triage_type = payload.get('triage_type', 'attention')
            batch_size = payload.get('batch_size', 5)

            if triage_type == 'attention':
                # Prioritize critical/high urgency
                qs = attention_qs.order_by(
                    Case(
                        When(urgency='critical', then=0),
                        When(urgency='high', then=1),
                        When(urgency='medium', then=2),
                        default=3,
                        output_field=IntegerField()
                    ),
                    '-priority_score',
                    '-created_at'
                )[:batch_size]

                items = []
                for item in qs:
                    items.append({
                        'id': str(item.id),
                        'title': item.title,
                        'summary': item.summary or '',
                        'urgency': item.urgency,
                        'item_type': item.item_type,
                        'source_agent': item.source_agent or 'System',
                        'ml_recommendation': item.ml_recommendation,
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                    })

                return {
                    'action': 'get_triage_batch',
                    'triage_type': 'attention',
                    'count': len(items),
                    'total_remaining': attention_qs.count(),
                    'items': items,
                }

            elif triage_type == 'decisions':
                qs = decisions_qs.order_by('-created_at')[:batch_size]

                items = []
                for item in qs:
                    items.append({
                        'id': str(item.id),
                        'topic': item.topic,
                        'decision_type': item.decision_type,
                        'impact_area': item.impact_area,
                        'recommended_stance': item.recommended_stance[:200] if item.recommended_stance else '',
                        'key_insights': item.key_insights[:3] if item.key_insights else [],
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                    })

                return {
                    'action': 'get_triage_batch',
                    'triage_type': 'decisions',
                    'count': len(items),
                    'total_remaining': decisions_qs.count(),
                    'items': items,
                }

            else:
                raise ValueError(f"Invalid triage_type: {triage_type}. Use 'attention' or 'decisions'")

        # Session 1070: Decision gate actions
        elif action == 'list_unclassified':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifacts = ExtractedArtifact.objects.filter(
                status='pending',
                classified=False,
                composite_score__gte=0.4,
            ).order_by('-composite_score')[:limit]

            items = []
            for a in artifacts:
                items.append({
                    'id': str(a.id),
                    'title': a.title,
                    'type': a.artifact_type,
                    'description': a.description[:200],
                    'composite_score': a.composite_score,
                    'source_agent': a.source_agent.name if a.source_agent else None,
                    'extracted_at': a.extracted_at.isoformat() if a.extracted_at else None,
                })

            return {
                'action': 'list_unclassified',
                'count': len(items),
                'items': items,
                'note': 'These artifacts need classification before they can be approved. '
                        'Each needs: what_is_this, who_is_it_for, data_allowed, phase_approved.',
            }

        elif action == 'classify_suggest':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifact_id = payload.get('artifact_id') or payload.get('id')
            if not artifact_id:
                raise ValueError("artifact_id is required for classify_suggest")

            artifact = ExtractedArtifact.objects.select_related('source_agent').get(id=artifact_id)
            title_lower = artifact.title.lower()
            desc_lower = artifact.description.lower()

            # Deterministic heuristic for what_is_this
            if artifact.artifact_type == 'risk':
                what_is_this = 'risk_flag'
            elif artifact.artifact_type == 'insight':
                what_is_this = 'informational'
            elif artifact.artifact_type in ('proposal', 'action_item'):
                what_is_this = 'actionable_recommendation'
            elif artifact.artifact_type == 'experiment':
                what_is_this = 'research_finding'
            elif any(w in title_lower for w in ['scope', 'expand', 'pivot', 'redesign']):
                what_is_this = 'scope_change'
            else:
                what_is_this = 'research_finding'

            # who_is_it_for heuristic
            if any(w in desc_lower for w in ['user', 'customer', 'subscriber']):
                who_is_it_for = 'end_users'
            elif any(w in desc_lower for w in ['platform', 'system', 'infra', 'celery', 'redis']):
                who_is_it_for = 'platform'
            elif any(w in desc_lower for w in ['agent', 'spider', 'ml ']):
                who_is_it_for = 'agents'
            else:
                who_is_it_for = 'founder'

            # data_allowed heuristic
            if any(w in desc_lower for w in ['user data', 'personal', 'private']):
                data_allowed = 'user_data'
            elif any(w in desc_lower for w in ['api', 'external']):
                data_allowed = 'api_data'
            elif any(w in desc_lower for w in ['internal', 'ops']):
                data_allowed = 'internal_ops'
            else:
                data_allowed = 'public_only'

            # phase_approved heuristic
            if artifact.composite_score >= 0.8:
                phase_approved = 'pilot'
            elif artifact.composite_score >= 0.6:
                phase_approved = 'prototype'
            else:
                phase_approved = 'research'

            return {
                'action': 'classify_suggest',
                'artifact_id': str(artifact.id),
                'artifact_title': artifact.title,
                'suggestions': {
                    'what_is_this': what_is_this,
                    'who_is_it_for': who_is_it_for,
                    'data_allowed': data_allowed,
                    'phase_approved': phase_approved,
                },
                'note': 'These are AI suggestions based on heuristics. '
                        'Human must confirm before applying.',
            }

        elif action == 'classify_apply':
            from core.models_conversation_artifacts import ExtractedArtifact
            artifact_id = payload.get('artifact_id') or payload.get('id')
            if not artifact_id:
                raise ValueError("artifact_id is required for classify_apply")

            classification = payload.get('classification', {})
            valid_keys = {'what_is_this', 'who_is_it_for', 'data_allowed', 'phase_approved'}
            filtered = {k: v for k, v in classification.items() if k in valid_keys}
            if not filtered:
                raise ValueError("classification must contain at least one of: what_is_this, who_is_it_for, data_allowed, phase_approved")

            artifact = ExtractedArtifact.objects.get(id=artifact_id)

            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first() if user_id else None

            artifact.classify(filtered, user=user)

            return {
                'action': 'classify_apply',
                'artifact_id': str(artifact.id),
                'artifact_title': artifact.title,
                'classification': filtered,
                'classified': True,
                'success': True,
            }

        elif action == 'classify_apply_batch':
            from core.models_conversation_artifacts import ExtractedArtifact

            items = payload.get('items', [])
            if not items:
                raise ValueError("items is required: list of {artifact_id, classification}")

            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.filter(id=user_id).first() if user_id else None

            valid_keys = {'what_is_this', 'who_is_it_for', 'data_allowed', 'phase_approved'}
            results = []
            for item in items[:50]:  # Cap at 50 per call
                aid = item.get('artifact_id') or item.get('id')
                classification = item.get('classification', {})
                filtered = {k: v for k, v in classification.items() if k in valid_keys}
                if not aid or not filtered:
                    continue
                try:
                    artifact = ExtractedArtifact.objects.get(id=aid)
                    artifact.classify(filtered, user=user)
                    results.append({'id': str(artifact.id), 'ok': True})
                except ExtractedArtifact.DoesNotExist:
                    results.append({'id': str(aid), 'ok': False, 'error': 'not found'})

            return {
                'action': 'classify_apply_batch',
                'classified_count': sum(1 for r in results if r['ok']),
                'total': len(results),
                'results': results,
                'success': True,
            }

        elif action == 'create_attention':
            if not user_id:
                raise ValueError("User context required to create attention item")

            title = payload.get('title', '').strip()
            if not title:
                raise ValueError("'title' is required for create_attention")

            summary = payload.get('summary', '').strip() or title
            item_type = payload.get('item_type', 'decision')
            urgency = payload.get('urgency', 'medium')

            item = HumanAttentionItem.objects.create(
                user_id=user_id,
                title=title[:200],
                summary=summary,
                item_type=item_type,
                urgency=urgency,
                source_type='pa',
                source_agent=PA_IDENTITY,
                status='pending',
            )
            return {
                'action': 'create_attention',
                'id': str(item.id),
                'title': item.title,
                'item_type': item.item_type,
                'urgency': item.urgency,
                'success': True,
            }

        else:
            raise ValueError(f"Unknown action: {action}. Valid actions: stats, lookup, list_attention, list_decisions, approve_attention, ignore_attention, promote_decision, reject_decision, get_triage_batch, list_unclassified, classify_suggest, classify_apply, classify_apply_batch, create_attention")

    def _handle_brainstorm(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """
        Session 943: Brainstorm search tool for accessing Discussion/Panel insights.

        Allows PA and Boardroom to search through past brainstorming conversations
        without creating pending action items.

        Actions:
        - search: Search brainstorming content by query
        - recent: Get recent brainstorming summaries
        - details: Get details of a specific conversation
        - by_category: Get ideas filtered by category
        - stats: Get brainstorming activity statistics
        """
        from core.services.brainstorm_search_service import brainstorm_search_service

        action = payload.get('action', 'search')

        if action == 'search':
            query = payload.get('query', '')
            if not query:
                raise ValueError("query is required for search action")

            days_back = payload.get('days_back') or 30  # Session 1228 PR-B autofill safety
            limit = payload.get('limit', 10)
            conv_type = payload.get('type')  # 'discussion', 'panel', or None

            result = brainstorm_search_service.search(
                query=query,
                days_back=days_back,
                limit=limit,
                conversation_type=conv_type
            )
            return {'action': 'search', **result}

        elif action == 'recent':
            days = payload.get('days') or 7  # Session 1228 PR-B autofill safety
            limit = payload.get('limit', 20)

            result = brainstorm_search_service.get_recent_summaries(
                days=days,
                limit=limit
            )
            return {'action': 'recent', **result}

        elif action == 'details':
            conversation_id = payload.get('conversation_id') or payload.get('id')
            if not conversation_id:
                raise ValueError("conversation_id (or id) is required for details action")

            include_full = payload.get('include_full_content', False)

            result = brainstorm_search_service.get_conversation_insights(
                conversation_id=conversation_id,
                include_full_content=include_full
            )
            return {'action': 'details', **result}

        elif action == 'by_category':
            category = payload.get('category', '')
            if not category:
                raise ValueError("category is required for by_category action")

            days_back = payload.get('days_back') or 30  # Session 1228 PR-B autofill safety
            limit = payload.get('limit', 10)

            result = brainstorm_search_service.get_ideas_by_category(
                category=category,
                days_back=days_back,
                limit=limit
            )
            return {'action': 'by_category', **result}

        elif action == 'list':
            days_back = payload.get('days') or 30  # Session 1228 PR-B autofill safety
            offset = payload.get('offset', 0)
            limit = min(payload.get('limit', 50), 200)  # cap at 200
            conv_type = payload.get('type')
            status = payload.get('status')
            include_transcript = payload.get('include_transcript', False)

            result = brainstorm_search_service.list_conversations(
                days_back=days_back,
                offset=offset,
                limit=limit,
                conversation_type=conv_type,
                status=status,
                include_transcript=include_transcript,
            )
            return {'action': 'list', **result}

        elif action == 'stats':
            days = payload.get('days', 30)

            result = brainstorm_search_service.get_stats(days=days)
            return {'action': 'stats', **result}

        elif action == 'create':
            topic = payload.get('topic', payload.get('query', '')).strip()
            if not topic:
                raise ValueError("'topic' is required for create action")

            # Dispatch brainstorm via ConversationOrchestrator as a Celery task
            from core.tasks import execute_agent_task
            task = execute_agent_task.apply_async(
                args=['ThinkingAgent', f'Brainstorm and discuss: {topic}',
                      {'user_id': str(user_id) if user_id else None, 'topic': topic}],
                queue='long_running',
            )

            return {
                'action': 'create',
                'topic': topic,
                'task_id': str(task.id),
                'mode': 'async',
                'message': f'Brainstorm discussion on "{topic}" dispatched. Use job_status to check progress.',
                'success': True,
            }

        else:
            raise ValueError(
                f"Unknown action: {action}. Valid actions: list, search, recent, details, by_category, stats, create"
            )

    # ── BPaaS Tool Handler ────────────────────────────────────────────────

    def _handle_bpaas(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str
    ) -> Dict[str, Any]:
        """Handle BPaaS tool — create projects from build packets, generate close packs.

        S2878: error envelopes migrated to structured shape per S2874 canonical
        (`{success, error_code, error, action}`). Eliminates dispatcher-layer
        `legacy_error` backfill for this handler (S2876 breadcrumb telemetry
        showed `bpaas_tool.generate_close_pack` as the only real production hit).
        """
        action = payload.get('action')
        if not action:
            return {
                'success': False,
                'error_code': 'missing_required_params',
                'error': 'action is required',
                'action': action,
            }

        try:
            if action == 'create_project':
                from core.services.bpaas.packet_service import create_project_from_packet
                from core.models_skin_layer import ProjectWorkspace
                from django.contrib.auth import get_user_model
                User = get_user_model()

                workspace_id = payload.get('workspace_id')
                packet = payload.get('packet')
                if not workspace_id or not packet:
                    return {
                        'success': False,
                        'error_code': 'missing_required_params',
                        'error': 'workspace_id and packet are required',
                        'action': action,
                    }

                workspace = ProjectWorkspace.objects.get(id=workspace_id)
                user = User.objects.get(id=user_id) if user_id else None
                result = create_project_from_packet(workspace=workspace, packet=packet, created_by=user)
                return {'success': True, 'action': 'create_project', **result}

            elif action == 'generate_close_pack':
                from core.services.bpaas.packet_service import generate_close_pack

                packet = payload.get('packet')
                if not packet:
                    return {
                        'success': False,
                        'error_code': 'missing_required_params',
                        'error': 'packet is required',
                        'action': action,
                    }
                return {'success': True, 'action': 'generate_close_pack', **generate_close_pack(packet)}

            elif action == 'get_schema':
                from core.services.bpaas.build_packet_schema import BUILD_PACKET_SCHEMA
                return {'success': True, 'action': 'get_schema', 'schema': BUILD_PACKET_SCHEMA}

            elif action == 'get_example':
                from core.services.bpaas.build_packet_schema import NORMAN_HANDYMAN_EXAMPLE
                return {'success': True, 'action': 'get_example', 'example': NORMAN_HANDYMAN_EXAMPLE}

            else:
                return {
                    'success': False,
                    'error_code': 'unknown_action',
                    'error': f"Unknown action: {action}. Valid: create_project, generate_close_pack, get_schema, get_example",
                    'action': action,
                }

        except Exception as e:
            logger.error(f"[bpaas_tool] Error: {e}", exc_info=True)
            return {
                'success': False,
                'error_code': 'handler_exception',
                'error': str(e),
                'action': action,
            }


    # ── Session 1174 PR-2b-1: schedule_followup ──────────────────────────────
    # Pairs with PR-2a's fire_agent_followup_subscriptions in core/tasks_agents.py
    # (signal handler at terminal-state save) + AgentFollowupSubscription model.
    # Full design: docs/handoffs/SESSION_1174_FOLLOWUP_WAKE_PR1_SHIP.md.

    @staticmethod
    def _make_followup_response(
        success: bool,
        *,
        mode: Optional[str] = None,
        subscription_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        execution_status: Optional[str] = None,
        state: Optional[str] = None,
        expires_at: Optional[str] = None,
        fired_at: Optional[str] = None,
        after_seconds: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Session 1175 PR-2b-2: stable 11-key contract for schedule_followup. Rigby's
        # PR-2b-1 review ask — every return path (success or error) emits the full key
        # set with None where not applicable, so callers can treat the shape as fixed.
        return {
            'success': success,
            'mode': mode,
            'subscription_id': subscription_id,
            'execution_id': execution_id,
            'execution_status': execution_status,
            'state': state,
            'expires_at': expires_at,
            'fired_at': fired_at,
            'after_seconds': after_seconds,
            'message': message,
            'error': error,
        }

    def _handle_schedule_followup(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Subscribe THIS conversation to a completion notification for an in-flight agent task.

        - Pulls conversation_id from the PA context (injected by unified_pa_entrypoint).
        - Resolves AgentExecution via execution_id (canonical) or task_id (convenience lookup
          through input_data__celery_task_id).
        - Caps after_seconds at 600s (Phase 1 D4 ratification).
        - If execution is already terminal, fires immediately (subscribe-after-terminal
          invariant Rigby added during the after_seconds pushback round) — atomic via the
          existing fire_agent_followup_subscriptions helper.
        - Otherwise creates AgentFollowupSubscription in state='armed' with expires_at TTL.
        - Idempotent: unique_together (execution, conversation_id) means duplicate
          schedule_followup calls return the existing subscription rather than crashing.
        """
        from datetime import timedelta
        from django.db import IntegrityError
        from django.utils import timezone
        from core.models_unified_system import AgentExecution, AgentFollowupSubscription
        from core.tasks_agents import fire_agent_followup_subscriptions

        # Session 1178 follow-up: pulled from AgentFollowupSubscription model
        # constants so Phase 1 explicit + Phase 2 auto-wake share one source
        # of truth and can't drift apart again.
        AFTER_SECONDS_CAP = AgentFollowupSubscription.MAX_TTL_SECONDS
        AFTER_SECONDS_DEFAULT = AgentFollowupSubscription.DEFAULT_TTL_SECONDS

        # 1. Conversation_id from PA context (promoted into payload root by
        # unified_pa_entrypoint at line 1549; also promoted into payload['context']
        # by _CONTEXT_PROMOTE_KEYS in tool_dispatcher). Tool only valid when the
        # caller is the PA — fail loud if missing.
        conversation_id = (
            payload.get('conversation_id')
            or (payload.get('context') or {}).get('conversation_id')
        )
        if not conversation_id:
            return self._make_followup_response(
                success=False,
                error='schedule_followup requires a PA conversation context (no conversation_id available).',
            )

        # 2. Parse + validate after_seconds. Cap at 600. Coerce missing/invalid to default.
        try:
            after_seconds = int(payload.get('after_seconds', AFTER_SECONDS_DEFAULT))
        except (TypeError, ValueError):
            after_seconds = AFTER_SECONDS_DEFAULT
        if after_seconds <= 0:
            after_seconds = AFTER_SECONDS_DEFAULT
        if after_seconds > AFTER_SECONDS_CAP:
            after_seconds = AFTER_SECONDS_CAP

        # 3. Resolve AgentExecution. Prefer explicit execution_id; fall back to
        # task_id lookup via input_data__celery_task_id (the field _impl_execute_agent_task
        # writes on dispatch).
        execution_id = (payload.get('execution_id') or '').strip()
        task_id = (payload.get('task_id') or '').strip()
        if not execution_id and not task_id:
            return self._make_followup_response(
                success=False,
                error='schedule_followup requires execution_id OR task_id.',
            )

        execution = None
        if execution_id:
            execution = AgentExecution.objects.filter(id=execution_id).first()
            if not execution:
                return self._make_followup_response(
                    success=False,
                    error=f'No AgentExecution found with execution_id={execution_id}.',
                )
        else:
            execution = AgentExecution.objects.filter(
                input_data__celery_task_id=task_id,
            ).order_by('-created_at').first()
            if not execution:
                return self._make_followup_response(
                    success=False,
                    error=f'No AgentExecution found with celery task_id={task_id}.',
                )

        # 4. Reject non-PA dispatches (NULL conversation_id) — the signal handler's
        # scope-rules invariant means non-PA executions can't fire follow-up. Subscribing
        # to one is always nonsense (the resulting row would never transition out of armed).
        if not execution.conversation_id:
            return self._make_followup_response(
                success=False,
                execution_id=str(execution.id),
                execution_status=execution.status,
                error=(
                    f'Cannot subscribe: execution {execution.id} was not dispatched from a PA '
                    'conversation (conversation_id is NULL). Follow-up requires a PA-originated dispatch.'
                ),
            )

        # 5. Reject cross-conversation subscriptions — the signal handler fires only on
        # subscriptions whose conversation_id matches the execution's stamped conversation_id.
        # A subscription from a different conversation would silently never fire, which is
        # worse UX than rejecting the call. Phase 2 cross-conversation follow-up (different
        # design) would lift this restriction with a separate mechanism.
        if execution.conversation_id != conversation_id:
            return self._make_followup_response(
                success=False,
                execution_id=str(execution.id),
                execution_status=execution.status,
                error=(
                    f'Cross-conversation subscription rejected: execution {execution.id} was '
                    f'dispatched from {execution.conversation_id!r}, but this call is from '
                    f'{conversation_id!r}. Subscribe from the same conversation that dispatched.'
                ),
            )

        # 6. Subscribe-after-terminal: if execution is already done, fire immediately
        # rather than creating an armed-but-doomed subscription. Per Rigby's after_seconds
        # pushback closing invariant — closes the "fast agent finished before subscribe"
        # gap that immediate-arm alone wouldn't catch.
        terminal_statuses = {'completed', 'failed', 'cancelled'}
        if execution.status in terminal_statuses:
            # Create an armed sub first (or get the existing one), then call the helper
            # which atomically transitions armed → fired using the same race-safe queryset
            # update path as the signal handler. This keeps the dedupe and broadcast
            # logic in one place (no duplicated payload-contract construction here).
            now = timezone.now()
            sub, created = AgentFollowupSubscription.objects.get_or_create(
                execution=execution,
                conversation_id=conversation_id,
                defaults={
                    'state': AgentFollowupSubscription.STATE_ARMED,
                    'expires_at': now + timedelta(seconds=after_seconds),
                },
            )
            if sub.state == AgentFollowupSubscription.STATE_ARMED:
                # Atomically fire it via the existing helper (handles dedupe + broadcast).
                fire_agent_followup_subscriptions(execution)
                sub.refresh_from_db()
            return self._make_followup_response(
                success=True,
                mode='delivered_immediately',
                subscription_id=str(sub.id),
                execution_id=str(execution.id),
                execution_status=execution.status,
                state=sub.state,
                fired_at=sub.fired_at.isoformat() if sub.fired_at else None,
                after_seconds=after_seconds,
                message=(
                    f'Agent {execution.agent.name if execution.agent_id else "?"} already finished '
                    f'(status={execution.status}); follow-up delivered immediately.'
                ),
            )

        # 5. Normal path: create an armed subscription with TTL.
        now = timezone.now()
        expires_at = now + timedelta(seconds=after_seconds)
        try:
            sub, created = AgentFollowupSubscription.objects.get_or_create(
                execution=execution,
                conversation_id=conversation_id,
                defaults={
                    'state': AgentFollowupSubscription.STATE_ARMED,
                    'expires_at': expires_at,
                },
            )
        except IntegrityError as e:
            return self._make_followup_response(
                success=False,
                execution_id=str(execution.id),
                execution_status=execution.status,
                error=f'Subscription create failed: {e}',
            )

        return self._make_followup_response(
            success=True,
            mode='subscribed' if created else 'already_subscribed',
            subscription_id=str(sub.id),
            execution_id=str(execution.id),
            execution_status=execution.status,
            state=sub.state,
            expires_at=sub.expires_at.isoformat() if sub.expires_at else None,
            after_seconds=after_seconds,
            message=(
                f'Subscribed to {execution.agent.name if execution.agent_id else "?"} completion; '
                f"you'll get an inline notification when it finishes (or in {after_seconds}s if not, whichever first)."
            ),
        )

    def _handle_agent_job_status(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Immediate status snapshot for an agent job dispatched via run_agent.

        Sibling to schedule_followup — same lookup shape (task_id OR execution_id),
        but returns status/output preview immediately instead of subscribing to a
        completion notification. Use to poll long-running dispatches when you don't
        want to wait for the follow-up banner.
        """
        from core.models_unified_system import AgentExecution

        execution_id = (payload.get('execution_id') or '').strip()
        task_id = (payload.get('task_id') or '').strip()
        if not execution_id and not task_id:
            return {
                'ok': False,
                'error': 'agent_job_status requires execution_id OR task_id',
            }

        if execution_id:
            execution = AgentExecution.objects.filter(id=execution_id).first()
            lookup = f'execution_id={execution_id}'
        else:
            execution = AgentExecution.objects.filter(
                input_data__celery_task_id=task_id,
            ).order_by('-created_at').first()
            lookup = f'task_id={task_id}'

        if not execution:
            # Distinguish "queued but not yet materialized" from "unknown task_id".
            # When Rigby dispatches via run_agent, the AgentExecution row is created
            # once the worker picks up the Celery task and calls execute(). Between
            # dispatch and that first ORM write, agent_job_status has no row to find
            # — a valid transient state that we surface as 'pending', not an error.
            # Falls back to 'unknown' only when Celery has no knowledge of the task_id.
            if task_id:
                try:
                    from core.celery import app as celery_app
                    async_result = celery_app.AsyncResult(task_id)
                    celery_state = async_result.status  # PENDING/STARTED/SUCCESS/FAILURE/RETRY
                    if celery_state in ('PENDING', 'RECEIVED', 'STARTED', 'RETRY'):
                        return {
                            'ok': True,
                            'status': 'pending',
                            'task_id': task_id,
                            'celery_state': celery_state,
                            'message': (
                                'Celery task queued or running; AgentExecution row not yet '
                                'created. Poll again in 5–15 seconds.'
                            ),
                        }
                except Exception:
                    pass
            return {
                'ok': False,
                'status': 'unknown',
                'error': f'No AgentExecution found for {lookup}',
            }

        output_preview = None
        if isinstance(execution.output_data, dict):
            msg = execution.output_data.get('message') or execution.output_data.get('content') or ''
            output_preview = msg[:800] if msg else None

        return {
            'ok': True,
            'execution_id': str(execution.id),
            'task_id': (execution.input_data or {}).get('celery_task_id'),
            'agent_name': execution.agent.name if execution.agent_id else None,
            'status': execution.status,
            'created_at': execution.created_at.isoformat() if execution.created_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'duration_ms': execution.execution_time_ms,
            'error_message': (execution.error_message or '')[:500] or None,
            'output_preview': output_preview,
        }

    def _handle_agent_capability_drift(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[int],
        trace_id: str,
    ) -> Dict[str, Any]:
        """S2953: Rigby-callable read-only agent-capability drift audit.

        Same codepath as ``scan_agent_capability_drift`` management command
        (Rigby SIGN-refined single-codepath rule).
        """
        from core.services.agent_capability_drift import (
            DEFAULT_RECENT_WINDOW_DAYS,
            AgentCapabilityDriftScanner,
        )

        action = (payload.get('action') or 'summary').strip()
        window = payload.get('recent_window_days') or DEFAULT_RECENT_WINDOW_DAYS
        invariant_filter = (payload.get('invariant') or 'all').strip()

        scanner = AgentCapabilityDriftScanner(recent_window_days=int(window))
        report = scanner.run_all()
        result = report.to_dict()

        if invariant_filter != 'all':
            result['findings'] = [
                f for f in result['findings'] if f.get('invariant') == invariant_filter
            ]
            result['suppressed_findings'] = [
                f for f in result['suppressed_findings'] if f.get('invariant') == invariant_filter
            ]

        if action == 'summary':
            return {
                'ok': True,
                'action': 'summary',
                'scanned_at': result['scanned_at'],
                'totals': result['totals'],
                'has_active_failures': result['has_active_failures'],
                'has_active_warnings': result['has_active_warnings'],
            }
        return {'ok': True, 'action': 'scan', **result}
