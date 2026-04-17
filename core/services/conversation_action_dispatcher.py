"""
Conversation Action Dispatcher
==============================

Session 811: Dispatches next_steps from conversation DecisionSummary to actual agent tasks.

When agents have a conversation and produce a DecisionSummary with next_steps like:
    "ResearchAgent: Investigate current market trends"
    "ContentStrategyAgent: Draft content calendar"

This service parses those steps and queues Celery tasks to execute them,
turning conversation conclusions into actual work.

Usage:
    from core.services.conversation_action_dispatcher import ConversationActionDispatcher

    dispatcher = ConversationActionDispatcher()
    result = dispatcher.dispatch_actions(
        conversation_id="uuid-here",
        decision_summary={'next_steps': ['ResearchAgent: ...', ...]},
        participants=['ResearchAgent', 'ContentStrategyAgent']
    )
"""

import logging
import re
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


# Feature flag (also defined in conversation_orchestrator.py)
ENABLE_ACTION_DISPATCH = True

# Session 1031: Task-agent routing overrides.
# When a task's text matches one of these patterns, force-reroute to the
# specialist agent instead of whatever the LLM suggested.  Prevents
# WorkflowAgent / VideoAgent / DevOpsAgent from receiving competitor audits,
# trend analyses, etc. they cannot handle.
TASK_ROUTING_OVERRIDES = [
    # (compiled regex, correct agent name)
    (re.compile(r'competitor\s+(audit|analysis|landscape|benchmark)', re.I), 'CompetitorAnalysisAgent'),
    (re.compile(r'trend\s+(analysis|report|summary)', re.I), 'TrendAnalysisAgent'),
    (re.compile(r'customer\s+(research|interview|persona)', re.I), 'CustomerResearchAgent'),
    (re.compile(r'brand\s+(strategy|positioning|audit)', re.I), 'BrandStrategyAgent'),
    (re.compile(r'market(ing)?\s+(strategy|plan|recommendation)', re.I), 'MarketingStrategyAgent'),
]

# Agents that should NEVER receive research/analysis tasks dispatched from
# conversation next_steps.  These are infrastructure or production agents.
NON_RESEARCH_AGENTS = frozenset({
    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
    'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
})

# Session 1036: Media agents can ONLY generate/edit content — block non-generative
# tasks like "list recent images", "review workspace", "catalog assets"
_MEDIA_AGENTS = frozenset({
    'ImageAgent', 'VideoAgent', 'ThreeDAgent', 'AudioAgent',
    'ImageEditingAgent', 'VideoEditingAgent',
})
_MEDIA_GENERATION_RE = re.compile(
    r'(generat|creat|design|draw|render|produc|make|build|edit|enhance|'
    r'upscale|retouch|composit|illustrat|paint|sketch|draft|style|transform)',
    re.I,
)


@dataclass
class ParsedAction:
    """A parsed action from a next_step string."""
    agent_name: str
    task: str
    raw_text: str
    confidence: float = 1.0


@dataclass
class DispatchResult:
    """Result of dispatching conversation actions."""
    conversation_id: str
    total_actions: int = 0
    dispatched_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'total_actions': self.total_actions,
            'dispatched_count': self.dispatched_count,
            'failed_count': self.failed_count,
            'skipped_count': self.skipped_count,
            'actions': self.actions,
            'errors': self.errors,
        }


class ConversationActionDispatcher:
    """
    Dispatches conversation next_steps to agent execution tasks.

    Parses DecisionSummary next_steps in formats like:
    - "AgentName: task description"
    - "AgentName should task description"
    - "Task: AgentName - task description"

    Then queues Celery tasks to execute each action.
    """

    # Known agent name patterns for matching
    AGENT_PATTERN = re.compile(
        r'^(?P<agent>[A-Z][a-zA-Z]+(?:Agent|Coordinator|Analyst|Detector)?)\s*[:\-]\s*(?P<task>.+)$',
        re.IGNORECASE
    )

    # Alternative pattern: "AgentName should/will/can..."
    ALT_PATTERN = re.compile(
        r'^(?P<agent>[A-Z][a-zA-Z]+(?:Agent|Coordinator|Analyst|Detector)?)\s+(?:should|will|can|needs? to)\s+(?P<task>.+)$',
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize the dispatcher."""
        self._router = None

    @property
    def router(self):
        """Lazy-load the agent router to validate agent names."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter()
        return self._router

    def parse_next_step(self, step: str) -> Optional[ParsedAction]:
        """
        Parse a single next_step string into an agent name and task.

        Handles formats like:
        - "ResearchAgent: Investigate market trends"
        - "ContentStrategyAgent - Draft content calendar"
        - "ResearchAgent should analyze competitor data"

        Args:
            step: A single next_step string

        Returns:
            ParsedAction if parsing succeeded, None otherwise
        """
        if not step or not isinstance(step, str):
            return None

        step = step.strip()

        # Remove leading numbers/bullets (e.g., "1.", "2)", "-", "*")
        step = re.sub(r'^[\d\.\)\-\*\s]+', '', step).strip()

        # Try main pattern first
        match = self.AGENT_PATTERN.match(step)
        if match:
            return ParsedAction(
                agent_name=match.group('agent'),
                task=match.group('task').strip(),
                raw_text=step,
                confidence=1.0
            )

        # Try alternative pattern
        match = self.ALT_PATTERN.match(step)
        if match:
            return ParsedAction(
                agent_name=match.group('agent'),
                task=match.group('task').strip(),
                raw_text=step,
                confidence=0.9
            )

        return None

    def _validate_agent(self, agent_name: str) -> Tuple[bool, str]:
        """
        Validate that an agent exists in the router.

        Args:
            agent_name: Name of the agent to validate

        Returns:
            Tuple of (is_valid, normalized_name_or_error)
        """
        # Normalize agent name (ensure "Agent" suffix)
        normalized = agent_name
        if not normalized.endswith(('Agent', 'Coordinator', 'Analyst', 'Detector')):
            normalized = f"{normalized}Agent"

        # Check if agent exists
        agent_class = self.router.get_agent_class(normalized)
        if agent_class:
            return True, normalized

        # Try original name
        agent_class = self.router.get_agent_class(agent_name)
        if agent_class:
            return True, agent_name

        return False, f"Unknown agent: {agent_name}"

    @staticmethod
    def _apply_routing_override(agent_name: str, task_text: str) -> str:
        """
        Session 1031: Force-reroute tasks to the correct specialist agent.

        When the LLM assigns a specialist task (e.g. competitor audit) to a
        non-specialist agent (e.g. WorkflowAgent), override the routing.
        """
        for pattern, correct_agent in TASK_ROUTING_OVERRIDES:
            if pattern.search(task_text):
                if agent_name != correct_agent and agent_name in NON_RESEARCH_AGENTS:
                    logger.info(
                        f"[routing-override] Rerouting '{task_text[:60]}' "
                        f"from {agent_name} -> {correct_agent}"
                    )
                    return correct_agent
        return agent_name

    @staticmethod
    def _recently_dispatched(agent_name: str, task_text: str) -> bool:
        """
        Session 1031: Check if the same agent already ran a very similar task
        in the last 2 hours.  Prevents the same competitor audit from being
        dispatched dozens of times.
        """
        try:
            from django.utils import timezone as _tz
            from datetime import timedelta
            from core.models_unified_system import AgentExecution

            cutoff = _tz.now() - timedelta(hours=6)  # Session 1035: Extended from 2h to 6h
            # Use the first 80 chars of the task as a similarity key
            task_prefix = task_text[:80]
            return AgentExecution.objects.filter(
                agent__name=agent_name,
                created_at__gte=cutoff,
                task__startswith=task_prefix,
            ).exists()
        except Exception:
            return False  # fail-open: don't block dispatches on DB errors

    def dispatch_actions(
        self,
        conversation_id: str,
        decision_summary: Optional[Dict[str, Any]],
        participants: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> DispatchResult:
        """
        Parse and dispatch all next_steps from a conversation.

        Args:
            conversation_id: ID of the conversation that produced these actions
            decision_summary: The DecisionSummary dict with next_steps
            participants: List of agent names that participated in the conversation
            context: Additional context to pass to executing agents

        Returns:
            DispatchResult with details about dispatched actions
        """
        result = DispatchResult(conversation_id=conversation_id)

        if not ENABLE_ACTION_DISPATCH:
            result.skipped_count = 1
            result.errors.append("Action dispatch is disabled")
            return result

        if not decision_summary:
            result.errors.append("No decision summary provided")
            return result

        next_steps = decision_summary.get('next_steps', [])
        if not next_steps:
            result.errors.append("No next_steps in decision summary")
            return result

        # Session 875: Trace and validate next_steps schema at parser stage.
        # Session 1083 (Rigby audit): validate_next_steps is a module-level
        # function in context_tracing, not a ContextTracer method. Old
        # code called `tracer.validate_next_steps(...)` which threw
        # `AttributeError: 'ContextTracer' object has no attribute
        # 'validate_next_steps'` every time the conversation orchestrator
        # hit its fallback action dispatch path — surfaced in logs
        # tonight. Function returns a tuple (valid_directives, schema_errors)
        # so we unpack instead of using the return as a truthy errors list.
        from core.services.context_tracing import (
            ContextTracer,
            validate_next_steps as _validate_next_steps,
        )
        tracer = ContextTracer(source=f"dispatch_actions:{conversation_id}")

        # Validate next_steps schema (should be List[str])
        _valid_directives, validation_errors = _validate_next_steps(next_steps)
        if validation_errors:
            logger.warning(
                f"[dispatch_actions] next_steps schema issues: {validation_errors}"
            )
            # Still proceed but log the issue

        result.total_actions = len(next_steps)

        # Session 1031: Track dispatched (agent, task_prefix) for dedup within this batch
        dispatched_keys: set = set()

        # Parse and dispatch each action
        for step in next_steps:
            parsed = self.parse_next_step(step)

            if not parsed:
                result.skipped_count += 1
                result.errors.append(f"Could not parse: {step[:50]}...")
                continue

            # Validate agent
            is_valid, agent_or_error = self._validate_agent(parsed.agent_name)

            if not is_valid:
                result.skipped_count += 1
                result.errors.append(agent_or_error)
                continue

            agent_name = agent_or_error
            task_text = parsed.task

            # Session 1031: Routing override — force-reroute specialist tasks
            agent_name = self._apply_routing_override(agent_name, task_text)

            # Session 1036: Block non-generative tasks for media agents.
            # ImageAgent etc. can only generate/edit — "list images", "review
            # workspace assets" etc. waste API spend for nothing.
            if agent_name in _MEDIA_AGENTS and not _MEDIA_GENERATION_RE.search(task_text):
                result.skipped_count += 1
                logger.info(
                    f"[dispatch] Blocked non-generative task for {agent_name}: "
                    f"'{task_text[:60]}'"
                )
                continue

            # Session 1031: Dedup within this dispatch batch
            dedup_key = (agent_name, task_text[:80].lower())
            if dedup_key in dispatched_keys:
                result.skipped_count += 1
                logger.info(f"[dispatch] Dedup skip: {agent_name} already has similar task")
                continue
            dispatched_keys.add(dedup_key)

            # Session 1031: Cross-batch dedup — skip if same agent ran similar task recently
            if self._recently_dispatched(agent_name, task_text):
                result.skipped_count += 1
                logger.info(f"[dispatch] Recent-dedup skip: {agent_name} ran similar task in last 6h")
                continue

            # Session 1035: Per-agent daily cap — no agent should run more than 8 times/day
            # from conversation dispatch alone. Session 1103c: surface
            # cap-check failures instead of silently failing open. A
            # silent fail-open here could cause runaway dispatching if
            # the AgentExecution schema drifts or the query breaks, and
            # we'd never see it in logs.
            _DAILY_AGENT_DISPATCH_CAP = 8
            try:
                from django.utils import timezone as _tz2
                from core.models_unified_system import AgentExecution
                daily_cutoff = _tz2.now() - timedelta(hours=24)
                daily_count = AgentExecution.objects.filter(
                    agent__name=agent_name,
                    created_at__gte=daily_cutoff,
                    input_data__context_injected__has_key='conversation_id',
                ).count()
                if daily_count >= _DAILY_AGENT_DISPATCH_CAP:
                    result.skipped_count += 1
                    logger.info(
                        f"[dispatch] Daily cap skip: {agent_name} already dispatched "
                        f"{daily_count} times today"
                    )
                    continue
            except Exception as e:
                logger.warning(
                    "[dispatch] Daily cap check failed for agent %s (%s: %s) "
                    "— failing open (dispatching anyway). Check AgentExecution "
                    "schema if this repeats.",
                    agent_name, type(e).__name__, e,
                )

            # Dispatch the action
            dispatch_result = self._dispatch_to_agent(
                agent_name=agent_name,
                task=task_text,
                conversation_id=conversation_id,
                participants=participants,
                context=context
            )

            if dispatch_result.get('success'):
                result.dispatched_count += 1
                result.actions.append(dispatch_result)
            else:
                result.failed_count += 1
                result.errors.append(dispatch_result.get('error', 'Unknown error'))

        logger.info(
            f"Action dispatch complete for conversation {conversation_id}: "
            f"{result.dispatched_count} dispatched, {result.failed_count} failed, "
            f"{result.skipped_count} skipped"
        )

        return result

    def _dispatch_to_agent(
        self,
        agent_name: str,
        task: str,
        conversation_id: str,
        participants: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatch a single task to an agent via Celery.

        Args:
            agent_name: Name of the agent to execute the task
            task: Task description
            conversation_id: Source conversation ID
            participants: Agents that participated in the conversation
            context: Additional context

        Returns:
            Dict with dispatch result
        """
        try:
            from core.tasks import execute_agent_task
            from core.services.context_tracing import ContextTracer
            from core.services.editor_dispatch_helpers import (
                gather_workspace_content_for_editor as _gather_workspace_content_for_editor,
            )

            task_context = {
                'source': 'conversation_action_dispatch',
                'conversation_id': conversation_id,
                'participants': participants,
                **(context or {})
            }

            # Session 1092: When a conversation produces a next_step like
            # "EditorAgent: Synthesize the Platform Audit + CTO + COO briefs",
            # the LLM doesn't attach the actual artifact bodies — it just
            # references them by name in the task text. EditorAgent then
            # fails with "No content provided" because its job is to edit,
            # not synthesize from thin air. Mirror the Session 1090
            # workspace-gather fallback that lives in ToolDispatcher's
            # _handle_agent_tool, so this dispatch path gets the same
            # caller-side recovery instead of dropping 9 fails/day on
            # CTOAgent's platform analysis.
            if (
                agent_name == 'EditorAgent'
                and 'content' not in task_context
                and 'blog_id' not in task_context
            ):
                # Session 1097: blog_id often arrives in the task text
                # (e.g. "Enhance the blog (blog_id=UUID)...") instead of
                # task_context. Pre-extract it so EditorAgent receives
                # the right hint and avoids the "No content provided"
                # fail-loud fallback we otherwise hit on conversation
                # action dispatches.
                _blog_id_match = re.search(
                    r'blog_id[=:"\'\s]+([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
                    task or '',
                    flags=re.IGNORECASE,
                )
                if _blog_id_match:
                    task_context['blog_id'] = _blog_id_match.group(1)
                    logger.info(
                        "[EditorAgent dispatch] Extracted blog_id=%s from task text",
                        task_context['blog_id'],
                    )

            if (
                agent_name == 'EditorAgent'
                and 'content' not in task_context
                and 'blog_id' not in task_context
            ):
                gathered = _gather_workspace_content_for_editor(
                    workspace_id=task_context.get('workspace_id')
                                  or task_context.get('workspace'),
                    task_text=task,
                )
                if gathered:
                    task_context['content'] = gathered
                    logger.info(
                        f"[EditorAgent dispatch] Pre-injected workspace content "
                        f"({len(gathered.get('sections') or [])} sections) before enqueue"
                    )

            # Session 875: Log context at pre-enqueue stage (before Celery serializes it)
            tracer = ContextTracer(source=f"conversation_action_dispatch:{conversation_id}")
            tracer.log_pre_enqueue(
                context=task_context,
                agent_name=agent_name,
                action_name=task[:100] if task else "",
                task_name="execute_agent_task"
            )

            # Queue the Celery task
            async_result = execute_agent_task.delay(
                agent_name=agent_name,
                task=task,
                context=task_context
            )

            logger.info(
                f"Dispatched task to {agent_name}: {task[:50]}... "
                f"(task_id={async_result.id})"
            )

            # Link dispatched task back to conversation for traceability
            # Record the dispatched task in Redis so future dispatch
            # passes can see what's already been queued for this
            # conversation. Session 1103c discovery: the previous
            # implementation wrote to AgentConversation.metadata which
            # *does not exist as a field* — that model is deprecated
            # and was never extended with a metadata JSONField. Every
            # dispatch had been silently failing its bookkeeping save
            # for an unknown number of sessions, which meant
            # conversations could never tell they had already queued
            # a task and re-dispatched the same work on every cycle
            # (likely contributor to the 'stuck running/pending'
            # pilot pattern Rigby flagged).
            #
            # Replaced with a Redis set per conversation, 24h TTL. The
            # set holds celery task IDs so callers can check
            # membership before dispatching. Failures here are still
            # logged but non-fatal.
            if conversation_id:
                try:
                    from django.core.cache import cache
                    cache_key = f'conv_dispatched:{conversation_id}'
                    dispatched = cache.get(cache_key) or []
                    dispatched.append({
                        'agent': agent_name,
                        'task_id': str(async_result.id),
                        'task_preview': (task[:100] if task else ''),
                        'dispatched_at': timezone.now().isoformat(),
                    })
                    dispatched = dispatched[-20:]  # Keep last 20
                    cache.set(cache_key, dispatched, timeout=86400)  # 24h TTL
                    logger.debug(
                        "[dispatch] Recorded task %s on conversation %s "
                        "(%d tracked)",
                        async_result.id, conversation_id, len(dispatched),
                    )
                except Exception as e:
                    logger.warning(
                        "[dispatch] Failed to record dispatched task on "
                        "conversation %s for agent %s task %s (%s: %s) — "
                        "dedupe may miss this entry",
                        conversation_id, agent_name,
                        getattr(async_result, 'id', '<unknown>'),
                        type(e).__name__, e,
                    )

            return {
                'success': True,
                'agent_name': agent_name,
                'task': task,
                'celery_task_id': async_result.id,
                'dispatched_at': timezone.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to dispatch task to {agent_name}: {e}")
            return {
                'success': False,
                'agent_name': agent_name,
                'task': task,
                'error': str(e),
            }


# Singleton instance
_dispatcher_instance = None


def get_action_dispatcher() -> ConversationActionDispatcher:
    """Get or create the singleton ConversationActionDispatcher."""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = ConversationActionDispatcher()
    return _dispatcher_instance


def dispatch_conversation_actions(
    conversation_id: str,
    decision_summary: Optional[Dict[str, Any]],
    participants: List[str],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to dispatch conversation actions.

    Args:
        conversation_id: ID of the source conversation
        decision_summary: DecisionSummary with next_steps
        participants: Participating agents
        context: Additional context

    Returns:
        Dict with dispatch results
    """
    dispatcher = get_action_dispatcher()
    result = dispatcher.dispatch_actions(
        conversation_id=conversation_id,
        decision_summary=decision_summary,
        participants=participants,
        context=context
    )
    return result.to_dict()


__all__ = [
    'ConversationActionDispatcher',
    'get_action_dispatcher',
    'dispatch_conversation_actions',
    'ParsedAction',
    'DispatchResult',
    'ENABLE_ACTION_DISPATCH',
]
