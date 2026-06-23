"""
Campaign Orchestrator Agent - The Marketing Campaign Hub
=========================================================

Session 513: The missing connector that ties together:
- Intelligence (spider data, web search, research)
- Agents (creation, strategy, writing)
- Autonomous (performance monitoring)
- Delivery (Discord, download, client management)

This agent takes a client brief and produces a complete marketing campaign.

Pipeline:
1. RESEARCH - Market trends, competitor analysis, customer insights
2. STRATEGY - Content strategy, brand direction, SEO keywords
3. CREATION - Ad copy, images, videos, emails, social posts
4. PACKAGING - Bundle deliverables for client
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to 5 min to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent
from ml.auto_selection import TaskType

# Session 1208: Outbound pack hardening constants ($2k Automation Sprint).
# Spec: deliverable ecddb62d-ab01-4b3b-83c4-2601670395d3 on Initiative
# 29154d73-… (Platform Capability Audit). The hardened path is reached
# only via _is_outbound_pack_request — the existing 5-phase campaign
# pipeline (research/strategy/creation) is untouched.
OUTBOUND_PACK_DBZ_WORKSPACE_ID = 'b4503364-2573-4401-9e28-61a739e0ce50'
OUTBOUND_PACK_OFFER_NAME = '$2k Automation Sprint'
OUTBOUND_PACK_SEGMENT_KEYS = ('smb_founder', 'agency_owner')
OUTBOUND_PACK_MESSAGE_TYPES = ('initial_outreach', 'follow_up_1', 'follow_up_2', 'breakup')
OUTBOUND_PACK_DRIFT_KEYWORDS = (
    'thumbnail', 'youtube', 'blog post', ' seo', 'midjourney',
    'dall-e', 'dall·e', 'image prompt', 'video script',
)
OUTBOUND_PACK_OUTBOUND_TOKENS = ('cold', 'dm', 'email', 'outreach')
OUTBOUND_PACK_MAX_ATTEMPTS = 3
OUTBOUND_PACK_SHORT_MAX_CHARS = 300
OUTBOUND_PACK_LONG_MAX_CHARS = 900
OUTBOUND_PACK_MIN_OBJECTIONS = 3
OUTBOUND_PACK_MIN_OUTCOME_BULLETS = 3
OUTBOUND_PACK_MIN_PERSONALIZATION_TOKENS = 2
OUTBOUND_PACK_JSON_MODEL = 'gpt-5-mini'
OUTBOUND_PACK_JSON_MAX_TOKENS = 6000

logger = logging.getLogger(__name__)


def analyze_campaign_with_ml(campaign_data: dict) -> dict:
    """Analyze marketing campaign using ML models (Text + Clustering)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=campaign_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'campaign_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML campaign analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CampaignOrchestratorAgent(BaseAgent):
    """
    Master orchestrator for marketing campaigns.

    Takes a campaign brief and coordinates multiple agents to produce
    a complete marketing package including:
    - Market research and competitor analysis
    - Content strategy and brand direction
    - Ad copy variations
    - Images (hero shots, banners, social graphics)
    - Video ads (optional based on tier)
    - Email sequences
    - Social media posts

    This is the HUB that finally connects all the pieces.
    """

    name = "CampaignOrchestratorAgent"

    system_prompt = """You are CampaignOrchestratorAgent, the master coordinator for marketing campaigns.

Your job is to take a client brief and orchestrate the creation of a complete marketing package.

You have access to specialized agents for each phase:
- ResearchAgent: Market research, competitor analysis, trend discovery
- CompetitorAnalysisAgent: Deep competitor research and SWOT analysis
- CustomerResearchAgent: Customer personas and pain points
- BrandIdentityAgent: Visual direction and brand consistency
- ContentStrategyAgent: Content planning and pillars
- SEOOptimizerAgent: Keywords, hashtags, metadata
- SocialMediaAgent: Platform-specific strategy
- ContentWriterAgent: Ad copy, emails, social posts
- ImageAgent: Hero images, banners, graphics
- VideoAgent: Video ads (for higher tiers)
- AudioAgent: Voiceovers (for higher tiers)

Campaign Flow:
1. RESEARCH PHASE (20% of progress)
   - Analyze market trends for the product/service
   - Research competitors
   - Identify target customer personas

2. STRATEGY PHASE (20% of progress)
   - Define brand direction and visual style
   - Create content strategy
   - Identify SEO keywords and hashtags

3. CREATION PHASE (50% of progress)
   - Generate ad copy variations
   - Create images for each platform
   - Write email sequence
   - Create social media posts
   - Generate video (if tier includes it)

4. PACKAGING PHASE (10% of progress)
   - Bundle all deliverables
   - Create campaign summary
   - Prepare for delivery

For each phase, you should:
1. Call the appropriate tool to delegate to specialized agents
2. Store results in the campaign
3. Update campaign progress
4. Move to the next phase

Always provide status updates and be transparent about what's being created."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_research_phase",
                "description": "Execute the research phase: market trends, competitor analysis, customer research",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_strategy_phase",
                "description": "Execute the strategy phase: brand direction, content strategy, SEO",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_creation_phase",
                "description": "Execute the creation phase: ad copy, images, videos, emails, social posts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_campaign_status",
                "description": "Get the current status and progress of a campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {
                            "type": "string",
                            "description": "UUID of the campaign"
                        }
                    },
                    "required": ["campaign_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_campaign",
                "description": "Create a new campaign from a client brief",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Campaign name"
                        },
                        "product_name": {
                            "type": "string",
                            "description": "Product or service name"
                        },
                        "product_description": {
                            "type": "string",
                            "description": "Detailed description of the product/service"
                        },
                        "target_market": {
                            "type": "string",
                            "description": "Target audience description"
                        },
                        "budget_tier": {
                            "type": "string",
                            "enum": ["starter", "pro", "enterprise", "premium"],
                            "description": "Budget tier determines deliverables",
                            "default": "starter"
                        },
                        "competitors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of competitor names or URLs"
                        },
                        "platforms": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Target platforms (facebook, instagram, craigslist, email, etc.)"
                        }
                    },
                    "required": ["name", "product_name", "product_description", "target_market"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._research_agent = None
        self._competitor_agent = None
        self._customer_agent = None
        self._brand_agent = None
        self._content_strategy_agent = None
        self._seo_agent = None
        self._writer_agent = None
        self._image_agent = None
        self._video_agent = None

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the campaign orchestration."""
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 739: Store context for sub-agent calls
        self._current_spider_context = spider_context
        self._current_scifi_context = scifi_context

        # Session 1208: Outbound pack hardened path. Precedence:
        #   1) context['mode'] == 'outbound_pack' (deterministic override)
        #   2) narrow keyword trigger in task
        #   3) fall through to existing 5-phase pipeline
        # Spec: deliverable ecddb62d-…, AC-1 through AC-5.
        if self._is_outbound_pack_request(task, context):
            with self.time_travel_session(
                "outbound_pack_generation", task, input_data=context
            ):
                return self._execute_outbound_pack(
                    task=task, context=context, start_time=start_time
                )

        with self.time_travel_session("campaign_orchestration", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                attribution = None  # Legacy compatibility

                # Call GPT to determine actions
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []

                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Executing {tool_name}",
                            reasoning=f"Campaign orchestration step",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'action': tool_name,
                                'data': tool_result.get('data', {})
                            })

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else f"Campaign orchestration completed with {len(all_results)} actions"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'results': all_results,
                            'content': synthesis,
                            'task': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        tool_calls=tool_calls_made,
                        knowledge_attribution=attribution
                    )

                    # Record learning outcome
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )

                    return result

                else:
                    # Conversational response
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'campaign_discussion',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        knowledge_attribution=attribution
                    )

            except Exception as e:
                logger.error(f"CampaignOrchestratorAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    # ===================================================================
    # Session 1208: Outbound pack hardened path ($2k Automation Sprint)
    # ===================================================================

    def _is_outbound_pack_request(
        self, task: str, context: Dict[str, Any]
    ) -> bool:
        """Detect whether to take the hardened outbound-pack path.

        Precedence (per Rigby pa-2d74e36cc3a04787 design call):
          1) context['mode'] == 'outbound_pack' (deterministic override)
          2) explicit phrase 'outbound pack' in normalized task
          3) composite signal: '$2k' + 'automation sprint' + an
             outbound-ish token (cold/dm/email/outreach)
        Otherwise fall through to the existing 5-phase pipeline.
        """
        if (context or {}).get('mode') == 'outbound_pack':
            return True
        if not task:
            return False

        normalized = task.lower().replace('—', '-').replace('–', '-')
        if 'outbound pack' in normalized:
            return True
        if (
            '$2k' in normalized
            and 'automation sprint' in normalized
            and any(token in normalized for token in OUTBOUND_PACK_OUTBOUND_TOKENS)
        ):
            return True
        return False

    def _execute_outbound_pack(
        self,
        task: str,
        context: Dict[str, Any],
        start_time: float,
    ) -> AgentResult:
        """Pipeline: generate_json → validate → retry (max 3) → render → save.

        Per AC-1 produces exactly one Deliverable on success (workspace=DBZ,
        category=Outbound). Per AC-3 retries up to 2 times (3 total attempts)
        with structured error feedback; on terminal failure marks failure
        without creating a deliverable (AC-4 preserves output_data shape).
        Follows MIC pattern (PR #2467 + #2469): deliverable_id + warnings
        convention, hook isolation around learning/memory writes.
        """
        context = context or {}
        offer_name = OUTBOUND_PACK_OFFER_NAME
        payload: Optional[Dict[str, Any]] = None
        attempt_records: List[Dict[str, Any]] = []
        last_errors: List[str] = []
        soft_warnings: List[Dict[str, str]] = []

        for attempt in range(1, OUTBOUND_PACK_MAX_ATTEMPTS + 1):
            system_prompt, user_prompt = self._build_outbound_prompt(
                offer_name=offer_name,
                attempt=attempt,
                previous_errors=last_errors,
            )
            candidate, parse_error = self._call_openai_json(
                user_prompt=user_prompt, system_prompt=system_prompt
            )

            if candidate is None:
                attempt_records.append({
                    'attempt': attempt,
                    'parse_error': parse_error,
                    'validation_errors': [],
                })
                last_errors = [f'JSON parse failed: {parse_error}']
                continue

            errors, warnings = self._validate_outbound_pack(candidate)
            attempt_records.append({
                'attempt': attempt,
                'validation_errors': errors,
                'soft_warnings_count': len(warnings),
            })

            if not errors:
                payload = candidate
                soft_warnings = warnings
                break
            last_errors = errors

        execution_time = int((time.time() - start_time) * 1000)

        # ===== Failure path (§4.4) =====
        if payload is None:
            result = AgentResult(
                success=False,
                message=(
                    f'Outbound pack validation failed after '
                    f'{len(attempt_records)} attempts'
                ),
                error=(
                    f'outbound_pack_validation_failed after '
                    f'{len(attempt_records)} attempts'
                ),
                data={
                    'attempts': attempt_records,
                    'attempts_used': len(attempt_records),
                    'validation_errors': last_errors,
                    'warnings': [],
                    'task': task,
                },
                agent_name=self.name,
                execution_time_ms=execution_time,
            )
            self._run_outbound_hooks(
                result=result, task=task, context=context, success=False
            )
            return result

        # ===== Success path (AC-1) =====
        title, body = self._render_outbound_pack_markdown(
            payload=payload,
            attempts_used=len(attempt_records),
            warnings=soft_warnings,
            context=context,
        )

        segments_count = len(payload.get('segments') or [])
        result = AgentResult(
            success=True,
            message=(
                f'Generated outbound pack for {offer_name} — '
                f'{segments_count} segments, attempts_used={len(attempt_records)}'
            ),
            data={
                'payload': payload,
                'attempts': attempt_records,
                'attempts_used': len(attempt_records),
                'warnings': list(soft_warnings),
                'title': title,
                'task': task,
            },
            agent_name=self.name,
            execution_time_ms=execution_time,
        )

        # Persist deliverable. MIC pattern (PR #2467 + #2469):
        # - deliverable_id lifted onto result.data on success
        # - structured warnings entries for gated / persist_failed
        # - try/except so persist failure never flips result.success
        try:
            segment_keys_present = [
                seg.get('segment_key')
                for seg in (payload.get('segments') or [])
                if isinstance(seg, dict)
            ]
            saved = self._save_to_deliverable(
                title=title,
                content=body,
                deliverable_type='document',
                category='Outbound',
                tags=['outbound', 'automation-sprint', 'campaign-orchestrator'],
                content_format='markdown',
                workspace_id=OUTBOUND_PACK_DBZ_WORKSPACE_ID,
                quality_score=0.85,
                confidence_score=0.8,
                metadata={
                    'sensitivity': 'internal',
                    'offer_name': offer_name,
                    'offer_min_deal_size_usd': 2000,
                    'segments': segment_keys_present,
                    'attempts_used': len(attempt_records),
                    'soft_warnings_count': len(soft_warnings),
                    'trigger_source': context.get('trigger_source') or 'manual',
                },
            )
            if saved is not None and getattr(saved, 'id', None):
                result.data['deliverable_id'] = str(saved.id)
            else:
                result.data['warnings'].append({
                    'type': 'deliverable_gated',
                    'message': (
                        'create_deliverable returned None — likely a '
                        'quality-gate rejection or dedupe hit. Check '
                        '[DeliverableFactory] log lines for reason_code.'
                    ),
                })
        except Exception as dlv_exc:
            logger.warning(
                'CampaignOrchestrator: outbound pack deliverable persist '
                'failed (non-blocking): %s', dlv_exc,
            )
            result.data['warnings'].append({
                'type': 'deliverable_persist_failed',
                'message': f'{type(dlv_exc).__name__}: {dlv_exc}',
            })

        self._run_outbound_hooks(
            result=result, task=task, context=context, success=True
        )
        return result

    def _run_outbound_hooks(
        self,
        result: AgentResult,
        task: str,
        context: Dict[str, Any],
        success: bool,
    ) -> None:
        """Run learning + memory hooks with isolation (MIC PR #2467 pattern).

        Each hook is wrapped individually so one failure doesn't block the
        other, and neither can flip result.success.
        """
        try:
            self._record_learning_outcome(
                result=result,
                task=task,
                context=context,
                spider_data_used=False,
                scifi_context_used=False,
            )
        except Exception as exc:
            logger.warning(
                'CampaignOrchestrator outbound %s-path '
                '_record_learning_outcome hook failed: %s',
                'success' if success else 'failure', exc,
            )

        try:
            self._create_execution_memory(
                result=result,
                task=task,
                memory_type='success' if success else 'failure',
                importance=0.8 if success else 0.9,
            )
        except Exception as exc:
            logger.warning(
                'CampaignOrchestrator outbound %s-path '
                '_create_execution_memory hook failed: %s',
                'success' if success else 'failure', exc,
            )

    def _call_openai_json(
        self,
        user_prompt: str,
        system_prompt: str = '',
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """JSON-mode LLM call. Returns (parsed_dict, parse_error_str).

        Uses response_format={"type":"json_object"} to radically reduce
        format failures so retry budget is spent on semantic validation
        (per Rigby's Q2 design call). Caller treats parse_error as a
        validation failure and proceeds with the retry loop.
        """
        messages: List[Any] = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': user_prompt})

        # Session 1222 P5 (audit #3) — migrated to llm_call_wrapper so the
        # call lands an LLMCallEvent telemetry row. Routes through the
        # canonical wrapper boundary that the check-llm-sdk.yml enforce
        # flip now polices.
        from core.services.llm_call_wrapper import llm_call_span
        try:
            with llm_call_span(
                provider='openai',
                model=OUTBOUND_PACK_JSON_MODEL,
                agent_name='CampaignOrchestratorAgent',
            ) as _span:
                response = self.client.chat.completions.create(  # noqa: direct-llm-call — wrapped above
                    model=OUTBOUND_PACK_JSON_MODEL,
                    messages=messages,
                    max_completion_tokens=OUTBOUND_PACK_JSON_MAX_TOKENS,
                    response_format={'type': 'json_object'},
                )
                _span.attach_response(response)
            raw = (response.choices[0].message.content or '').strip()
        except Exception as exc:
            logger.error(
                'CampaignOrchestrator outbound JSON LLM call failed: %s', exc,
            )
            return None, f'{type(exc).__name__}: {exc}'

        if not raw:
            return None, 'empty_response'

        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError) as exc:
            return None, f'json_parse_error: {exc}'

        if not isinstance(parsed, dict):
            return None, 'json_root_not_object'
        return parsed, None

    def _build_outbound_prompt(
        self,
        offer_name: str,
        attempt: int,
        previous_errors: List[str],
    ) -> Tuple[str, str]:
        """Build (system, user) prompts for attempt N. §3/§4 of spec.

        Attempt 1: normal prompt + required-fields summary.
        Attempt 2: adds structured validation errors + drift reminder.
        Attempt 3: same as 2 + an inline JSON skeleton template.
        """
        system_prompt = (
            'You are CampaignOrchestratorAgent generating a strict outbound '
            'messaging pack. Return ONLY valid JSON conforming to the '
            'outbound pack schema. No markdown, no commentary, no extra text. '
            'DO NOT generate blog posts, thumbnails, images, SEO content, '
            'video scripts, or any creative beyond the outbound messages.'
        )

        base_user = (
            f'Generate a complete outbound messaging pack for the offer '
            f'"{offer_name}".\n\n'
            f'Hard requirements:\n'
            f'- offer.min_deal_size_usd MUST be exactly 2000\n'
            f'- offer.name MUST be exactly "{offer_name}" (case-insensitive '
            f'match; do not append, prepend, or compound)\n'
            f'- offer.primary_outcome_bullets MUST have >= '
            f'{OUTBOUND_PACK_MIN_OUTCOME_BULLETS} non-empty entries\n'
            f'- segments[] MUST contain EXACTLY 2 entries with segment_keys: '
            f'{list(OUTBOUND_PACK_SEGMENT_KEYS)}\n'
            f'- Each segment MUST include messages for ALL of: '
            f'{list(OUTBOUND_PACK_MESSAGE_TYPES)}\n'
            f'- Each message type MUST have both "short" '
            f'(<= ~{OUTBOUND_PACK_SHORT_MAX_CHARS} chars) and "long" '
            f'(<= ~{OUTBOUND_PACK_LONG_MAX_CHARS} chars) variants\n'
            f'- Each segment objection_handling MUST have >= '
            f'{OUTBOUND_PACK_MIN_OBJECTIONS} entries with '
            f'{{objection, reply_short, reply_long}}\n'
            f'- Each segment MUST have personalization_tokens >= '
            f'{OUTBOUND_PACK_MIN_PERSONALIZATION_TOKENS} entries\n'
            f'- Each segment MUST have a cta.primary string\n\n'
            f'Target audiences: SMB founders + agency owners.\n'
            f'Tone: direct, competent, low-hype.\n'
            f'Preserve personalization tokens like {{first_name}}, '
            f'{{company}}, {{trigger}} as literal braces.\n\n'
            f'Return ONLY the JSON object — no markdown wrappers, no '
            f'commentary.'
        )

        if attempt == 1:
            return system_prompt, base_user

        errors_block = (
            '\n'.join(f'- {err}' for err in previous_errors)
            if previous_errors else '- (no errors recorded)'
        )
        retry_user = (
            f'{base_user}\n\n'
            f'PREVIOUS ATTEMPT VALIDATION ERRORS:\n{errors_block}\n\n'
            f'Fix every error above. Return ONLY JSON. No markdown. '
            f'No commentary.\n'
            f'Reminder: do NOT generate blogs, thumbnails, SEO content, '
            f'images, or video scripts. Only the outbound pack JSON above.'
        )

        if attempt >= 3:
            skeleton = self._outbound_pack_skeleton(offer_name)
            retry_user += (
                f'\n\nUse this EXACT JSON skeleton as your starting '
                f'template — fill in every empty string:\n\n'
                f'```\n{skeleton}\n```\n\n'
                f'Return ONLY the filled JSON.'
            )

        return system_prompt, retry_user

    def _outbound_pack_skeleton(self, offer_name: str) -> str:
        """JSON skeleton used as the Try-3 inline template."""
        skeleton = {
            'offer': {
                'name': offer_name,
                'min_deal_size_usd': 2000,
                'positioning_one_liner': '',
                'who_its_for': ['SMB founders', 'Agency owners'],
                'primary_outcome_bullets': ['', '', ''],
                'timeline': '5 days',
                'guarantee_or_risk_reversal': '',
            },
            'segments': [
                {
                    'segment_key': key,
                    'segment_label': '',
                    'icp_assumptions': [''],
                    'personalization_tokens': [
                        '{first_name}', '{company}', '{trigger}',
                    ],
                    'messages': {
                        mt: {'short': '', 'long': ''}
                        for mt in OUTBOUND_PACK_MESSAGE_TYPES
                    },
                    'objection_handling': [
                        {'objection': '', 'reply_short': '', 'reply_long': ''}
                        for _ in range(OUTBOUND_PACK_MIN_OBJECTIONS)
                    ],
                    'cta': {'primary': '', 'secondary': ''},
                }
                for key in OUTBOUND_PACK_SEGMENT_KEYS
            ],
            'global': {
                'tone': 'direct, competent, low-hype',
                'compliance_notes': [],
                'do_not_generate': ['blog posts', 'thumbnails', 'images'],
            },
        }
        return json.dumps(skeleton, indent=2)

    def _validate_outbound_pack(
        self, payload: Optional[Dict[str, Any]],
    ) -> Tuple[List[str], List[Dict[str, str]]]:
        """Validate per §4. Returns (hard_errors, soft_warnings).

        Hard errors block deliverable creation and trigger the retry loop.
        Soft warnings (length overshoot) pass but surface on output_data.
        """
        errors: List[str] = []
        warnings: List[Dict[str, str]] = []

        if not isinstance(payload, dict):
            errors.append('payload is not a JSON object')
            return errors, warnings

        # === Offer block ===
        offer = payload.get('offer') or {}
        if not isinstance(offer, dict):
            errors.append('offer is missing or not an object')
        else:
            offer_name = offer.get('name', '')
            if not isinstance(offer_name, str) or not offer_name.strip():
                errors.append('offer.name is missing or empty')
            elif (
                offer_name.strip().lower()
                != OUTBOUND_PACK_OFFER_NAME.lower()
            ):
                # Tightened Session 1208 PR follow-up: exact match
                # (case-insensitive). Old check accepted any value
                # containing "automation sprint", which let the LLM
                # return composites like "Automation Sprint — $2k
                # Automation Sprint" and bleed into deterministic
                # rendering paths.
                errors.append(
                    f'offer.name must be exactly '
                    f'{OUTBOUND_PACK_OFFER_NAME!r} '
                    f'(got: {offer_name!r})'
                )
            if offer.get('min_deal_size_usd') != 2000:
                errors.append(
                    f'offer.min_deal_size_usd must be exactly 2000 '
                    f'(got: {offer.get("min_deal_size_usd")!r})'
                )
            bullets = offer.get('primary_outcome_bullets') or []
            non_empty_bullets = [
                b for b in bullets if isinstance(b, str) and b.strip()
            ]
            if len(non_empty_bullets) < OUTBOUND_PACK_MIN_OUTCOME_BULLETS:
                errors.append(
                    f'offer.primary_outcome_bullets must have >= '
                    f'{OUTBOUND_PACK_MIN_OUTCOME_BULLETS} non-empty strings '
                    f'(got {len(non_empty_bullets)})'
                )

        # === Segments block ===
        segments = payload.get('segments') or []
        if not isinstance(segments, list):
            errors.append('segments must be a list')
            segments = []
        if len(segments) != 2:
            errors.append(
                f'segments must have exactly 2 entries (got {len(segments)})'
            )

        seg_keys_found: List[Any] = []
        for idx, seg in enumerate(segments):
            if not isinstance(seg, dict):
                errors.append(f'segments[{idx}] is not an object')
                continue
            seg_key = seg.get('segment_key')
            seg_keys_found.append(seg_key)
            label = f'segments[{idx}] ({seg_key!r})'

            if not (
                isinstance(seg.get('segment_label'), str)
                and seg['segment_label'].strip()
            ):
                errors.append(f'{label}.segment_label is missing or empty')

            tokens = seg.get('personalization_tokens') or []
            non_empty_tokens = [
                t for t in tokens if isinstance(t, str) and t.strip()
            ]
            if len(non_empty_tokens) < OUTBOUND_PACK_MIN_PERSONALIZATION_TOKENS:
                errors.append(
                    f'{label}.personalization_tokens must have >= '
                    f'{OUTBOUND_PACK_MIN_PERSONALIZATION_TOKENS} non-empty '
                    f'entries (got {len(non_empty_tokens)})'
                )

            messages = seg.get('messages') or {}
            if not isinstance(messages, dict):
                errors.append(f'{label}.messages is not an object')
                messages = {}
            for mt in OUTBOUND_PACK_MESSAGE_TYPES:
                mt_obj = messages.get(mt) or {}
                if not isinstance(mt_obj, dict):
                    errors.append(
                        f'{label}.messages.{mt} is missing or not an object'
                    )
                    continue
                short = mt_obj.get('short', '')
                long_text = mt_obj.get('long', '')
                if not (isinstance(short, str) and short.strip()):
                    errors.append(
                        f'{label}.messages.{mt}.short is missing or empty'
                    )
                if not (isinstance(long_text, str) and long_text.strip()):
                    errors.append(
                        f'{label}.messages.{mt}.long is missing or empty'
                    )
                if (
                    isinstance(short, str)
                    and len(short) > OUTBOUND_PACK_SHORT_MAX_CHARS
                ):
                    warnings.append({
                        'type': 'length_exceeded',
                        'message': (
                            f'{label}.messages.{mt}.short is {len(short)} '
                            f'chars (target <= {OUTBOUND_PACK_SHORT_MAX_CHARS})'
                        ),
                    })
                if (
                    isinstance(long_text, str)
                    and len(long_text) > OUTBOUND_PACK_LONG_MAX_CHARS
                ):
                    warnings.append({
                        'type': 'length_exceeded',
                        'message': (
                            f'{label}.messages.{mt}.long is {len(long_text)} '
                            f'chars (target <= {OUTBOUND_PACK_LONG_MAX_CHARS})'
                        ),
                    })

            objections = seg.get('objection_handling') or []
            if (
                not isinstance(objections, list)
                or len(objections) < OUTBOUND_PACK_MIN_OBJECTIONS
            ):
                got = (
                    len(objections) if isinstance(objections, list) else 'non-list'
                )
                errors.append(
                    f'{label}.objection_handling must have >= '
                    f'{OUTBOUND_PACK_MIN_OBJECTIONS} entries (got {got})'
                )
            else:
                for oidx, obj in enumerate(objections):
                    if not isinstance(obj, dict):
                        errors.append(
                            f'{label}.objection_handling[{oidx}] '
                            f'is not an object'
                        )
                        continue
                    for fld in ('objection', 'reply_short', 'reply_long'):
                        val = obj.get(fld, '')
                        if not (isinstance(val, str) and val.strip()):
                            errors.append(
                                f'{label}.objection_handling[{oidx}].{fld} '
                                f'is missing or empty'
                            )

            cta = seg.get('cta') or {}
            if not (
                isinstance(cta, dict)
                and isinstance(cta.get('primary'), str)
                and cta['primary'].strip()
            ):
                errors.append(f'{label}.cta.primary is missing or empty')

        for required_key in OUTBOUND_PACK_SEGMENT_KEYS:
            if required_key not in seg_keys_found:
                errors.append(
                    f'segments missing required segment_key: {required_key!r}'
                )

        # === §4.2 No-drift keyword scan ===
        # Scope: message content only (offer copy + segment messages +
        # objection replies + ctas). NOT metadata (do_not_generate /
        # compliance_notes / personalization_tokens / segment_key /
        # icp_assumptions) which legitimately mentions the same words.
        message_text = ' '.join(
            self._collect_outbound_message_strings(payload)
        ).lower()
        drift_hits = sorted({
            kw.strip() for kw in OUTBOUND_PACK_DRIFT_KEYWORDS
            if kw in message_text
        })
        if drift_hits:
            errors.append(
                f'drift keywords detected in message content (must not '
                f'generate blog/thumbnail/SEO/video content): {drift_hits}'
            )

        return errors, warnings

    @staticmethod
    def _collect_outbound_message_strings(
        payload: Dict[str, Any],
    ) -> List[str]:
        """Collect strings the outbound recipient would actually read.

        Excludes metadata fields (do_not_generate, compliance_notes,
        personalization_tokens, icp_assumptions, segment_key) that
        legitimately reference drift keywords.
        """
        parts: List[str] = []
        offer = payload.get('offer') or {}
        if isinstance(offer, dict):
            for field in ('positioning_one_liner', 'timeline',
                          'guarantee_or_risk_reversal'):
                val = offer.get(field)
                if isinstance(val, str):
                    parts.append(val)
            for bullet in (offer.get('primary_outcome_bullets') or []):
                if isinstance(bullet, str):
                    parts.append(bullet)

        for seg in (payload.get('segments') or []):
            if not isinstance(seg, dict):
                continue
            label = seg.get('segment_label')
            if isinstance(label, str):
                parts.append(label)
            messages = seg.get('messages') or {}
            if isinstance(messages, dict):
                for mt_obj in messages.values():
                    if not isinstance(mt_obj, dict):
                        continue
                    for variant in ('short', 'long'):
                        val = mt_obj.get(variant)
                        if isinstance(val, str):
                            parts.append(val)
            for obj in (seg.get('objection_handling') or []):
                if not isinstance(obj, dict):
                    continue
                for fld in ('objection', 'reply_short', 'reply_long'):
                    val = obj.get(fld)
                    if isinstance(val, str):
                        parts.append(val)
            cta = seg.get('cta') or {}
            if isinstance(cta, dict):
                for fld in ('primary', 'secondary'):
                    val = cta.get(fld)
                    if isinstance(val, str):
                        parts.append(val)

        global_block = payload.get('global') or {}
        if isinstance(global_block, dict):
            tone = global_block.get('tone')
            if isinstance(tone, str):
                parts.append(tone)

        return parts

    @staticmethod
    def _format_outbound_pack_title(date_str: Optional[str] = None) -> str:
        """Return the deterministic outbound-pack title.

        Locked to the constant offer name so the LLM's `offer.name` value
        can never bleed into the title (see Rigby pa-2d74e36cc3a04787
        review — LLM smoke returned "Automation Sprint — $2k Automation
        Sprint" which would double-render under the old f-string).

        Note: `deliverable_factory._clean_deliverable_title` will prepend
        `CampaignOrchestratorAgent: ` to the persisted Deliverable.title
        because the cleaner can't tell our title is already canonical.
        That's a factory-level concern (affects all agents the same way,
        documented as cosmetic follow-up in the Session 1208 handoff).
        The post-prefix portion is locked here.
        """
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        return f'Outbound Pack — {OUTBOUND_PACK_OFFER_NAME} — {date_str}'

    def _render_outbound_pack_markdown(
        self,
        payload: Dict[str, Any],
        attempts_used: int,
        warnings: List[Dict[str, str]],
        context: Dict[str, Any],
    ) -> Tuple[str, str]:
        """Render §5 markdown body. Returns (title, body)."""
        offer = payload.get('offer') or {}
        title = self._format_outbound_pack_title()

        lines: List[str] = [f'# {title}', '']

        # Provenance
        lines.append('## Provenance')
        lines.append('')
        lines.append(f'- **Generated:** {datetime.now().isoformat()}')
        lines.append(f'- **Agent:** {self.name}')
        lines.append(
            '- **Inputs:** audience=[SMB founders, Agency owners], '
            'min_deal_size_usd=2000, flagships_per_week=2'
        )
        lines.append(
            f'- **Validation:** pass (attempts_used={attempts_used})'
        )
        if context.get('trigger_source'):
            lines.append(
                f'- **Trigger source:** {context["trigger_source"]}'
            )
        if warnings:
            lines.append(
                f'- **Soft warnings:** {len(warnings)} '
                '(see footer)'
            )
        lines.append('')

        # Offer summary
        lines.append('## Offer Summary')
        lines.append('')
        if offer.get('positioning_one_liner'):
            lines.append(
                f'**Positioning:** {offer["positioning_one_liner"]}'
            )
            lines.append('')
        bullets = offer.get('primary_outcome_bullets') or []
        if bullets:
            lines.append('**Outcomes:**')
            for bullet in bullets:
                if isinstance(bullet, str) and bullet.strip():
                    lines.append(f'- {bullet}')
            lines.append('')
        if offer.get('timeline'):
            lines.append(f'**Timeline:** {offer["timeline"]}')
            lines.append('')
        if offer.get('guarantee_or_risk_reversal'):
            lines.append(
                f'**Guarantee / risk reversal:** '
                f'{offer["guarantee_or_risk_reversal"]}'
            )
            lines.append('')

        # Segments
        for seg in (payload.get('segments') or []):
            if not isinstance(seg, dict):
                continue
            seg_label = (
                seg.get('segment_label')
                or seg.get('segment_key')
                or 'Segment'
            )
            lines.append(f'## Segment: {seg_label}')
            lines.append('')
            tokens = seg.get('personalization_tokens') or []
            tokens_str = ', '.join(
                t for t in tokens if isinstance(t, str) and t.strip()
            )
            if tokens_str:
                lines.append(f'**Personalization tokens:** {tokens_str}')
                lines.append('')

            messages = seg.get('messages') or {}
            for mt in OUTBOUND_PACK_MESSAGE_TYPES:
                mt_obj = messages.get(mt) or {}
                heading = mt.replace('_', ' ').title()
                lines.append(f'### {heading}')
                lines.append('')
                short = mt_obj.get('short') or ''
                long_text = mt_obj.get('long') or ''
                if short:
                    lines.append(f'**Short ({len(short)} chars):**')
                    lines.append('')
                    lines.append(short)
                    lines.append('')
                if long_text:
                    lines.append(f'**Long ({len(long_text)} chars):**')
                    lines.append('')
                    lines.append(long_text)
                    lines.append('')

            objections = seg.get('objection_handling') or []
            if objections:
                lines.append('### Objection Handling')
                lines.append('')
                lines.append('| Objection | Reply (short) | Reply (long) |')
                lines.append('|---|---|---|')
                for obj in objections:
                    if not isinstance(obj, dict):
                        continue
                    o = (obj.get('objection') or '').replace('|', '\\|').replace('\n', ' ')
                    rs = (obj.get('reply_short') or '').replace('|', '\\|').replace('\n', ' ')
                    rl = (obj.get('reply_long') or '').replace('|', '\\|').replace('\n', ' ')
                    lines.append(f'| {o} | {rs} | {rl} |')
                lines.append('')

            cta = seg.get('cta') or {}
            if isinstance(cta, dict) and (cta.get('primary') or cta.get('secondary')):
                lines.append('### CTA')
                lines.append('')
                if cta.get('primary'):
                    lines.append(f'- **Primary:** {cta["primary"]}')
                if cta.get('secondary'):
                    lines.append(f'- **Secondary:** {cta["secondary"]}')
                lines.append('')

        # Notes / Guardrails
        global_block = payload.get('global') or {}
        if isinstance(global_block, dict) and global_block:
            lines.append('## Notes / Guardrails')
            lines.append('')
            if global_block.get('tone'):
                lines.append(f'- **Tone:** {global_block["tone"]}')
            compliance = global_block.get('compliance_notes') or []
            if isinstance(compliance, list) and compliance:
                lines.append('- **Compliance notes:**')
                for note in compliance:
                    if isinstance(note, str) and note.strip():
                        lines.append(f'  - {note}')
            do_not = global_block.get('do_not_generate') or []
            if isinstance(do_not, list) and do_not:
                do_not_str = ', '.join(
                    n for n in do_not if isinstance(n, str) and n.strip()
                )
                if do_not_str:
                    lines.append(f'- **Do not generate:** {do_not_str}')
            lines.append('')

        # Soft warnings footer
        if warnings:
            lines.append('## Warnings')
            lines.append('')
            for warn in warnings:
                wtype = warn.get('type', 'warning')
                wmsg = warn.get('message', '')
                lines.append(f'- **{wtype}:** {wmsg}')
            lines.append('')

        return title, '\n'.join(lines).strip()

    # ===================================================================
    # End Session 1208 outbound pack hardened path
    # ===================================================================

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call."""

        if tool_name == "create_campaign":
            return self._create_campaign(arguments)

        elif tool_name == "get_campaign_status":
            return self._get_campaign_status(arguments.get('campaign_id'))

        elif tool_name == "run_research_phase":
            return self._run_research_phase(arguments.get('campaign_id'))

        elif tool_name == "run_strategy_phase":
            return self._run_strategy_phase(arguments.get('campaign_id'))

        elif tool_name == "run_creation_phase":
            return self._run_creation_phase(arguments.get('campaign_id'))

        return super()._execute_tool_call(tool_name, arguments)

    def _create_campaign(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.create(
                user=self.user,
                name=args.get('name'),
                product_name=args.get('product_name'),
                product_description=args.get('product_description'),
                target_market=args.get('target_market'),
                budget_tier=args.get('budget_tier', 'starter'),
                competitors=args.get('competitors', []),
                platforms=args.get('platforms', ['general']),
                status='intake'
            )

            logger.info(f"Created campaign: {campaign.id} - {campaign.name}")

            return {
                'success': True,
                'data': {
                    'campaign_id': str(campaign.id),
                    'name': campaign.name,
                    'status': campaign.status,
                    'budget_tier': campaign.budget_tier,
                    'included_deliverables': campaign.get_included_deliverables()
                }
            }

        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return {'success': False, 'error': str(e)}

    def _get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign status."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.get(id=campaign_id)

            deliverables = list(campaign.deliverables.values(
                'id', 'name', 'deliverable_type', 'status', 'platform'
            ))

            return {
                'success': True,
                'data': {
                    'campaign_id': str(campaign.id),
                    'name': campaign.name,
                    'status': campaign.status,
                    'progress_percent': campaign.progress_percent,
                    'current_phase': campaign.current_phase,
                    'deliverables_count': len(deliverables),
                    'deliverables': deliverables[:10],  # First 10
                    'budget_tier': campaign.budget_tier
                }
            }

        except Exception as e:
            logger.error(f"Failed to get campaign status: {e}")
            return {'success': False, 'error': str(e)}

    def _run_research_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the research phase."""
        try:
            from core.models_campaign import Campaign, CampaignResearch
            from core.services.smart_trending_service import get_smart_trending_service

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'research'
            campaign.current_phase = 'research'
            campaign.start_campaign()

            research_results = []

            # 1. Market trends research using SmartTrendingService (with web search fallback)
            logger.info(f"[Campaign {campaign_id}] Starting market trends research")
            trending_service = get_smart_trending_service()
            trends = trending_service.get_trending_for_query(
                f"What's trending for {campaign.product_name} in {campaign.target_market}?",
                use_cache=False
            )

            if trends.get('articles'):
                research = CampaignResearch.objects.create(
                    campaign=campaign,
                    research_type='market_trends',
                    title=f"Market Trends for {campaign.product_name}",
                    summary=f"Found {len(trends['articles'])} relevant articles",
                    data={
                        'trends': trends.get('trends', []),
                        'articles': trends.get('articles', [])[:10],
                        'used_web_search': trends.get('used_web_search', False)
                    },
                    source='web_search' if trends.get('used_web_search') else 'spider_network',
                    source_urls=[a.get('url', '') for a in trends.get('articles', [])[:5]],
                    agent_name='SmartTrendingService'
                )
                research_results.append({
                    'type': 'market_trends',
                    'articles_found': len(trends.get('articles', [])),
                    'used_web_search': trends.get('used_web_search', False)
                })

            # 2. Competitor research (if competitors provided)
            if campaign.competitors:
                logger.info(f"[Campaign {campaign_id}] Researching competitors: {campaign.competitors}")

                # Use web search for competitor research
                for competitor in campaign.competitors[:3]:  # Max 3 competitors
                    comp_trends = trending_service.get_trending_for_query(
                        f"{competitor} marketing strategy advertising",
                        use_cache=False
                    )

                    CampaignResearch.objects.create(
                        campaign=campaign,
                        research_type='competitor',
                        title=f"Competitor Analysis: {competitor}",
                        summary=f"Found {len(comp_trends.get('articles', []))} articles about {competitor}",
                        data={
                            'competitor': competitor,
                            'articles': comp_trends.get('articles', [])[:5]
                        },
                        source='web_search',
                        agent_name='SmartTrendingService'
                    )

                research_results.append({
                    'type': 'competitor_analysis',
                    'competitors_analyzed': len(campaign.competitors[:3])
                })

            # Update campaign progress
            campaign.research_data = {
                'trends': trends.get('trends', []),
                'articles_count': len(trends.get('articles', [])),
                'completed_at': datetime.now().isoformat()
            }
            campaign.update_progress('research', 20, {'completed': True})
            campaign.log_execution('research_phase_complete', {'results': research_results})

            logger.info(f"[Campaign {campaign_id}] Research phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'research',
                    'progress': 20,
                    'results': research_results
                }
            }

        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _run_strategy_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the strategy phase."""
        try:
            from core.models_campaign import Campaign

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'strategy'
            campaign.current_phase = 'strategy'
            campaign.save()

            strategy_results = []

            # 1. Generate content strategy based on research
            research_items = campaign.research_items.filter(research_type='market_trends').first()
            market_trends = research_items.data if research_items else {}

            # Build content pillars based on trends
            content_pillars = []
            if market_trends.get('trends'):
                for trend in market_trends['trends'][:5]:
                    content_pillars.append({
                        'topic': trend,
                        'content_types': ['ad_copy', 'social_post', 'image']
                    })

            campaign.content_strategy = {
                'pillars': content_pillars,
                'tone': 'professional' if 'enterprise' in campaign.budget_tier else 'conversational',
                'platforms': campaign.platforms,
                'generated_at': datetime.now().isoformat()
            }

            # 2. Generate SEO keywords from trends
            seo_keywords = []
            if market_trends.get('trends'):
                seo_keywords = [campaign.product_name] + market_trends['trends'][:10]

            campaign.seo_keywords = seo_keywords

            # 3. Brand direction
            campaign.brand_direction = {
                'style': campaign.brand_style or 'modern',
                'colors': campaign.brand_colors or ['#2563eb', '#1e40af', '#ffffff'],
                'tone': 'professional',
                'generated_at': datetime.now().isoformat()
            }

            campaign.update_progress('strategy', 40, {'completed': True})
            campaign.log_execution('strategy_phase_complete', {
                'content_pillars': len(content_pillars),
                'seo_keywords': len(seo_keywords)
            })

            logger.info(f"[Campaign {campaign_id}] Strategy phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'strategy',
                    'progress': 40,
                    'content_pillars': len(content_pillars),
                    'seo_keywords': seo_keywords[:5]
                }
            }

        except Exception as e:
            logger.error(f"Strategy phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _run_creation_phase(self, campaign_id: str) -> Dict[str, Any]:
        """Execute the creation phase - generate all deliverables."""
        try:
            from core.models_campaign import Campaign, CampaignDeliverable

            campaign = Campaign.objects.get(id=campaign_id)
            campaign.status = 'creation'
            campaign.current_phase = 'creation'
            campaign.save()

            included_deliverables = campaign.get_included_deliverables()
            creation_results = []

            # Get research data for context
            research = campaign.research_items.filter(research_type='market_trends').first()
            trends = research.data.get('trends', []) if research else []

            # 1. Generate Ad Copy Variations
            if 'ad_copy' in included_deliverables:
                ad_copies = self._generate_ad_copies(campaign, trends)
                for i, copy in enumerate(ad_copies):
                    CampaignDeliverable.objects.create(
                        campaign=campaign,
                        deliverable_type='ad_copy',
                        name=f"Ad Copy Variation {i+1}",
                        status='complete',
                        platform='general',
                        content_text=copy['text'],
                        content_data=copy,
                        created_by_agent='CampaignOrchestratorAgent'
                    )
                creation_results.append({'type': 'ad_copy', 'count': len(ad_copies)})

            # 2. Generate Social Posts
            if 'social_posts' in included_deliverables:
                posts = self._generate_social_posts(campaign, trends)
                for platform, post_list in posts.items():
                    for i, post in enumerate(post_list):
                        CampaignDeliverable.objects.create(
                            campaign=campaign,
                            deliverable_type='social_post',
                            name=f"{platform.title()} Post {i+1}",
                            status='complete',
                            platform=platform,
                            content_text=post,
                            created_by_agent='CampaignOrchestratorAgent'
                        )
                creation_results.append({'type': 'social_posts', 'count': sum(len(p) for p in posts.values())})

            # 3. Generate Email Sequence
            if 'email_sequence' in included_deliverables:
                emails = self._generate_email_sequence(campaign)
                for i, email in enumerate(emails):
                    CampaignDeliverable.objects.create(
                        campaign=campaign,
                        deliverable_type='email',
                        name=f"Email {i+1}: {email['subject'][:30]}",
                        status='complete',
                        platform='email',
                        content_text=email['body'],
                        content_data=email,
                        created_by_agent='CampaignOrchestratorAgent'
                    )
                creation_results.append({'type': 'email_sequence', 'count': len(emails)})

            # Update progress
            campaign.update_progress('creation', 90, {'completed': True})
            campaign.log_execution('creation_phase_complete', {'results': creation_results})

            # Mark campaign as complete
            campaign.complete_campaign()

            logger.info(f"[Campaign {campaign_id}] Creation phase complete")

            return {
                'success': True,
                'data': {
                    'campaign_id': campaign_id,
                    'phase': 'creation',
                    'progress': 100,
                    'deliverables_created': creation_results,
                    'status': 'complete'
                }
            }

        except Exception as e:
            logger.error(f"Creation phase failed: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_ad_copies(self, campaign, trends: List[str], use_agent: bool = True) -> List[Dict[str, Any]]:
        """
        Generate ad copy variations.

        Session 653 COMPOSABILITY FIX: Now uses ContentWriterAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('ContentWriterAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Write 5 compelling ad copy variations for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}
Location: {campaign.target_location or 'global'}
Trending Topics: {', '.join(trends[:5]) if trends else 'none'}

For each ad copy, provide:
1. The ad text (compelling, concise)
2. A variant letter (A, B, C, D, E)
3. The tone (professional, casual, urgent, emotional, etc.)
4. Key keywords used

Format: Return 5 distinct ad variations with different angles (benefit-focused, urgency, social proof, question-based, direct)."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context={},
                            spider_context={'trends': trends}
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    # Parse agent response into structured format
                    if result.success and result.message:
                        logger.info(f"✅ ContentWriterAgent generated ad copies for campaign {campaign.id}")
                        return self._parse_ad_copies_from_agent(result.message, trends)

            except FuturesTimeoutError:
                logger.warning(f"⏰ ContentWriterAgent timed out after {SUB_AGENT_TIMEOUT}s for ad copies")
            except Exception as e:
                logger.warning(f"Agent-based ad copy generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        base_copies = []
        templates = [
            f"Discover {campaign.product_name} - {campaign.product_description[:100]}. {campaign.target_market} love it!",
            f"Looking for the best {campaign.product_name}? We've got you covered. Contact us today!",
            f"Special offer on {campaign.product_name}! Don't miss out. Perfect for {campaign.target_market}.",
            f"{campaign.product_name} - Quality you can trust. Serving {campaign.target_location or 'your area'}.",
            f"Why choose {campaign.product_name}? {campaign.product_description[:80]}. Get yours now!"
        ]

        for i, template in enumerate(templates):
            base_copies.append({
                'text': template,
                'variant': chr(65 + i),
                'tone': 'professional',
                'keywords': trends[:3] if trends else [],
                'generated_by': 'template'
            })

        return base_copies

    def _parse_ad_copies_from_agent(self, agent_response: str, trends: List[str]) -> List[Dict[str, Any]]:
        """Parse ContentWriterAgent response into structured ad copies."""
        copies = []
        # Split by variant markers or numbered sections
        sections = agent_response.split('\n\n')

        for i, section in enumerate(sections[:5]):
            if section.strip():
                copies.append({
                    'text': section.strip()[:500],  # Limit length
                    'variant': chr(65 + i),
                    'tone': 'professional',
                    'keywords': trends[:3] if trends else [],
                    'generated_by': 'ContentWriterAgent'
                })

        # Ensure we have at least 5 copies
        while len(copies) < 5:
            copies.append({
                'text': f"Discover quality with our product. Contact us today!",
                'variant': chr(65 + len(copies)),
                'tone': 'professional',
                'keywords': trends[:3] if trends else [],
                'generated_by': 'fallback'
            })

        return copies[:5]

    def _generate_social_posts(self, campaign, trends: List[str], use_agent: bool = True) -> Dict[str, List[str]]:
        """
        Generate social media posts for each platform.

        Session 653 COMPOSABILITY FIX: Now uses SocialMediaAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('SocialMediaAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Create social media posts for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}
Trending Topics: {', '.join(trends[:5]) if trends else 'none'}

Create posts for each platform:
1. FACEBOOK (2 posts): Longer form, engaging, with call-to-action
2. INSTAGRAM (2 posts): Visual-focused captions with relevant hashtags
3. TWITTER (2 posts): Short, punchy, under 280 characters

Label each post clearly with the platform name."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context={},
                            spider_context={'trends': trends}
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    if result.success and result.message:
                        logger.info(f"✅ SocialMediaAgent generated posts for campaign {campaign.id}")
                        return self._parse_social_posts_from_agent(result.message, campaign, trends)

            except FuturesTimeoutError:
                logger.warning(f"⏰ SocialMediaAgent timed out after {SUB_AGENT_TIMEOUT}s for social posts")
            except Exception as e:
                logger.warning(f"Agent-based social post generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        posts = {
            'facebook': [],
            'instagram': [],
            'twitter': []
        }

        posts['facebook'] = [
            f"Introducing {campaign.product_name}! {campaign.product_description[:200]}...\n\nPerfect for {campaign.target_market}. Learn more!",
            f"Check out what our customers are saying about {campaign.product_name}! Contact us today.",
        ]

        hashtags = ' '.join([f"#{t.replace(' ', '')}" for t in trends[:5]]) if trends else '#sale #new'
        posts['instagram'] = [
            f"{campaign.product_name} - Available now!\n\n{hashtags}",
            f"Your next favorite {campaign.product_name} is here.\n\n{hashtags}",
        ]

        posts['twitter'] = [
            f"New: {campaign.product_name}! {campaign.product_description[:80]}... #new",
            f"Looking for {campaign.product_name}? We've got you! Contact us today.",
        ]

        return posts

    def _parse_social_posts_from_agent(self, agent_response: str, campaign, trends: List[str]) -> Dict[str, List[str]]:
        """Parse SocialMediaAgent response into structured posts."""
        posts = {'facebook': [], 'instagram': [], 'twitter': []}
        response_lower = agent_response.lower()

        # Try to extract platform-specific sections
        for platform in ['facebook', 'instagram', 'twitter']:
            if platform in response_lower:
                # Find content after platform name
                start_idx = response_lower.find(platform)
                # Find next platform or end
                next_platforms = [response_lower.find(p, start_idx + len(platform)) for p in ['facebook', 'instagram', 'twitter'] if response_lower.find(p, start_idx + len(platform)) > 0]
                end_idx = min(next_platforms) if next_platforms else len(agent_response)

                section = agent_response[start_idx:end_idx]
                # Extract lines that look like posts
                lines = [l.strip() for l in section.split('\n') if l.strip() and len(l.strip()) > 20 and platform not in l.lower()[:20]]
                posts[platform] = lines[:2]

        # Ensure each platform has at least 2 posts (fallback)
        hashtags = ' '.join([f"#{t.replace(' ', '')}" for t in trends[:5]]) if trends else '#new'
        defaults = {
            'facebook': [f"{campaign.product_name} - Perfect for {campaign.target_market}!"],
            'instagram': [f"{campaign.product_name} is here! {hashtags}"],
            'twitter': [f"Check out {campaign.product_name}! #new"]
        }

        for platform in posts:
            while len(posts[platform]) < 2:
                posts[platform].append(defaults[platform][0] if defaults[platform] else f"Great {platform} post!")

        return posts

    def _generate_email_sequence(self, campaign, use_agent: bool = True) -> List[Dict[str, str]]:
        """
        Generate a 5-email nurture sequence.

        Session 653 COMPOSABILITY FIX: Now uses ContentWriterAgent instead of templates!
        """
        if use_agent:
            try:
                from core.agent_router import AgentRouter
                router = AgentRouter()

                agent_class = router.AGENT_MAP.get('ContentWriterAgent')
                if agent_class:
                    agent = agent_class(user=self.user)
                    task = f"""Write a 5-email nurture sequence for a marketing campaign:

Product: {campaign.product_name}
Description: {campaign.product_description}
Target Market: {campaign.target_market}

Create 5 emails with this flow:
1. INTRODUCTION: Welcome and introduce the product
2. VALUE: Explain why the product is right for them
3. OFFER: Present a special offer or discount
4. URGENCY: Last chance reminder
5. FOLLOW-UP: Thank you and stay in touch

For each email provide:
- Subject line (compelling, under 60 chars)
- Body (personalized, with greeting and sign-off)

Label each email clearly (Email 1, Email 2, etc.)."""

                    # Session 895: Add timeout to prevent coordinator hangs
                    def execute_agent():
                        return agent.execute(
                            task=task,
                            context={'campaign_id': str(campaign.id), 'phase': 'creation'},
                            scifi_context=getattr(self, '_current_scifi_context', {}),
                            spider_context=getattr(self, '_current_spider_context', {})
                        )

                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(execute_agent)
                        result = future.result(timeout=SUB_AGENT_TIMEOUT)

                    if result.success and result.message:
                        logger.info(f"✅ ContentWriterAgent generated email sequence for campaign {campaign.id}")
                        return self._parse_emails_from_agent(result.message, campaign)

            except FuturesTimeoutError:
                logger.warning(f"⏰ ContentWriterAgent timed out after {SUB_AGENT_TIMEOUT}s for email sequence")
            except Exception as e:
                logger.warning(f"Agent-based email generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        emails = [
            {
                'subject': f"Introducing {campaign.product_name}",
                'body': f"Hi there,\n\nWe're excited to introduce {campaign.product_name}.\n\n{campaign.product_description}\n\nPerfect for {campaign.target_market}.\n\nLearn more by replying to this email!\n\nBest regards",
                'generated_by': 'template'
            },
            {
                'subject': f"Why {campaign.product_name} is right for you",
                'body': f"Hi,\n\nStill thinking about {campaign.product_name}?\n\nHere's why customers love it:\n- Quality you can trust\n- Perfect for {campaign.target_market}\n- Great value\n\nReply to learn more!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Special offer on {campaign.product_name}",
                'body': f"Hi,\n\nFor a limited time, we're offering a special deal on {campaign.product_name}.\n\nDon't miss out - reply now to claim your offer!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Last chance - {campaign.product_name}",
                'body': f"Hi,\n\nThis is your last chance to take advantage of our special offer on {campaign.product_name}.\n\nReply today!\n\nBest",
                'generated_by': 'template'
            },
            {
                'subject': f"Thank you for your interest in {campaign.product_name}",
                'body': f"Hi,\n\nThank you for your interest in {campaign.product_name}.\n\nWe're here whenever you're ready. Just reply to this email with any questions.\n\nBest regards",
                'generated_by': 'template'
            }
        ]

        return emails

    def _parse_emails_from_agent(self, agent_response: str, campaign) -> List[Dict[str, str]]:
        """Parse ContentWriterAgent response into structured emails."""
        emails = []
        response = agent_response

        # Try to split by email markers
        for i in range(1, 6):
            markers = [f"Email {i}", f"EMAIL {i}", f"{i}.", f"#{i}"]
            for marker in markers:
                if marker in response:
                    start_idx = response.find(marker)
                    # Find next email marker or end
                    next_starts = []
                    for j in range(i + 1, 7):
                        for next_marker in [f"Email {j}", f"EMAIL {j}", f"{j}.", f"#{j}"]:
                            idx = response.find(next_marker, start_idx + len(marker))
                            if idx > 0:
                                next_starts.append(idx)
                    end_idx = min(next_starts) if next_starts else len(response)

                    section = response[start_idx:end_idx]

                    # Try to extract subject and body
                    subject = f"{campaign.product_name} - Email {i}"
                    body = section

                    if 'subject' in section.lower():
                        subj_idx = section.lower().find('subject')
                        subj_end = section.find('\n', subj_idx)
                        if subj_end > subj_idx:
                            subject = section[subj_idx:subj_end].replace('Subject:', '').replace('subject:', '').strip()[:60]

                    emails.append({
                        'subject': subject,
                        'body': section[:1000],
                        'generated_by': 'ContentWriterAgent'
                    })
                    break

        # Ensure we have 5 emails
        while len(emails) < 5:
            emails.append({
                'subject': f"{campaign.product_name} - Update {len(emails) + 1}",
                'body': f"Hi,\n\nThank you for your interest in {campaign.product_name}.\n\nBest regards",
                'generated_by': 'fallback'
            })

        return emails[:5]


# Factory function for convenience
def get_campaign_orchestrator_agent(user=None) -> CampaignOrchestratorAgent:
    """Get a CampaignOrchestratorAgent instance."""
    return CampaignOrchestratorAgent(user=user)
