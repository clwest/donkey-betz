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
from datetime import datetime

from django.utils import timezone

logger = logging.getLogger(__name__)


# Feature flag (also defined in conversation_orchestrator.py)
ENABLE_ACTION_DISPATCH = True


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

        result.total_actions = len(next_steps)

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

            # Dispatch the action
            dispatch_result = self._dispatch_to_agent(
                agent_name=agent_or_error,
                task=parsed.task,
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

            task_context = {
                'source': 'conversation_action_dispatch',
                'conversation_id': conversation_id,
                'participants': participants,
                **(context or {})
            }

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
