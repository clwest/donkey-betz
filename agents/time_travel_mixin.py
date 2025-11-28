"""
Time Travel Debugging Mixin for Agents
=======================================

Session 255: Provides time travel debugging capabilities for content generation agents.

This mixin allows agents to record their decision-making process for later replay
and debugging. It tracks:
- Session lifecycle (start/end)
- Decision points with reasoning and alternatives
- Thought bubbles (internal monologue)
- Execution outcomes

Usage:
    class MyAgent(TimeTravelMixin, BaseContentAgent):
        def execute(self, **kwargs):
            with self.time_travel_session("image_generation", "Generate logo"):
                # Your execution code
                self.record_decision(
                    decision_type="style_selection",
                    action="Selected modern minimalist style",
                    reasoning="User requested clean, professional look",
                    alternatives=["vintage", "playful", "corporate"]
                )
                # More execution...
"""

import logging
import time
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from functools import wraps
from django.utils import timezone

logger = logging.getLogger(__name__)


class TimeTravelMixin:
    """
    Mixin class that adds time travel debugging capabilities to agents.

    Agents using this mixin can record their decision-making process
    for later replay and analysis.
    """

    # Time travel state
    _tt_session = None
    _tt_decision_count = 0
    _tt_enabled = True  # Can be disabled for performance

    def _get_agent_db_object(self):
        """Get the Agent database object for this agent."""
        try:
            from agents.models import Agent
            # Try to find by name
            agent = Agent.objects.filter(name__iexact=self.agent_name).first()
            if not agent:
                # Try partial match
                agent = Agent.objects.filter(name__icontains=self.agent_name.replace('Agent', '')).first()
            return agent
        except Exception as e:
            logger.warning(f"Could not get Agent DB object for {self.agent_name}: {e}")
            return None

    @contextmanager
    def time_travel_session(
        self,
        task_type: str,
        task_description: str,
        input_data: Dict[str, Any] = None
    ):
        """
        Context manager for a time travel debugging session.

        Args:
            task_type: Type of task (e.g., 'image_generation', 'research')
            task_description: Human-readable description
            input_data: Input parameters for the session

        Yields:
            The AgentSession object (or None if disabled)

        Example:
            with self.time_travel_session("image_gen", "Create logo") as session:
                self.record_decision(...)
        """
        if not self._tt_enabled:
            yield None
            return

        try:
            from core.models_unified_system import AgentSession

            agent = self._get_agent_db_object()
            if not agent:
                logger.debug(f"Time travel disabled - no agent DB object for {self.agent_name}")
                yield None
                return

            # Create session
            self._tt_session = AgentSession.objects.create(
                agent=agent,
                task_type=task_type,
                task_description=task_description,
                input_data=input_data or {},
                status='running'
            )
            self._tt_decision_count = 0
            self._tt_start_time = time.time()

            logger.info(f"Time travel session started: {self._tt_session.id}")

            try:
                yield self._tt_session

                # Success - update session
                self._tt_session.status = 'completed'
                self._tt_session.ended_at = timezone.now()
                self._tt_session.duration_ms = int((time.time() - self._tt_start_time) * 1000)
                self._tt_session.total_decisions = self._tt_decision_count
                self._tt_session.save()

                logger.info(f"Time travel session completed: {self._tt_decision_count} decisions")

            except Exception as e:
                # Failure - mark session as failed
                self._tt_session.status = 'failed'
                self._tt_session.ended_at = timezone.now()
                self._tt_session.duration_ms = int((time.time() - self._tt_start_time) * 1000)
                self._tt_session.total_decisions = self._tt_decision_count
                self._tt_session.output_data = {'error': str(e)}
                self._tt_session.save()
                raise

        except ImportError:
            logger.debug("Time travel models not available")
            yield None
        except Exception as e:
            logger.warning(f"Time travel session error: {e}")
            yield None
        finally:
            self._tt_session = None
            self._tt_decision_count = 0

    def record_decision(
        self,
        decision_type: str,
        action: str,
        reasoning: str = "",
        alternatives: List[str] = None,
        context: Dict[str, Any] = None,
        confidence: float = 0.8,
        thoughts: List[str] = None
    ) -> Optional[Any]:
        """
        Record a decision point during agent execution.

        Args:
            decision_type: Type of decision (analysis, selection, action, etc.)
            action: The action taken
            reasoning: Why this decision was made
            alternatives: Other options that were considered
            context: Additional context data
            confidence: Confidence score (0-1)
            thoughts: List of internal thoughts leading to this decision

        Returns:
            DecisionPoint object or None
        """
        if not self._tt_session:
            return None

        try:
            from core.models_unified_system import DecisionPoint, ThoughtBubble

            start_time = time.time()
            self._tt_decision_count += 1

            decision = DecisionPoint.objects.create(
                session=self._tt_session,
                sequence_number=self._tt_decision_count,
                decision_type=decision_type,
                context=context or {},
                reasoning=reasoning,
                alternatives=alternatives or [],
                action_taken=action,
                action_params={},
                confidence_score=confidence,
                duration_ms=int((time.time() - start_time) * 1000)
            )

            # Record thoughts if provided
            if thoughts:
                for i, thought in enumerate(thoughts, 1):
                    ThoughtBubble.objects.create(
                        decision=decision,
                        sequence_number=i,
                        thought_type='reasoning',
                        content=thought,
                        importance=0.7,
                        influences_decision=True
                    )

            logger.debug(f"Recorded decision {self._tt_decision_count}: {decision_type} - {action[:50]}")
            return decision

        except Exception as e:
            logger.warning(f"Failed to record decision: {e}")
            return None

    def record_thought(
        self,
        content: str,
        thought_type: str = "observation",
        importance: float = 0.5
    ):
        """
        Record a thought bubble for the current decision.

        Args:
            content: The thought content
            thought_type: Type (observation, hypothesis, evaluation, insight, concern)
            importance: How important this thought is (0-1)
        """
        if not self._tt_session:
            return

        try:
            from core.models_unified_system import DecisionPoint, ThoughtBubble

            # Get most recent decision
            decision = DecisionPoint.objects.filter(
                session=self._tt_session
            ).order_by('-sequence_number').first()

            if decision:
                thought_count = ThoughtBubble.objects.filter(decision=decision).count()
                ThoughtBubble.objects.create(
                    decision=decision,
                    sequence_number=thought_count + 1,
                    thought_type=thought_type,
                    content=content,
                    importance=importance,
                    influences_decision=importance > 0.6
                )

        except Exception as e:
            logger.warning(f"Failed to record thought: {e}")

    def mark_decision_outcome(self, success: bool, result_summary: str = ""):
        """
        Mark the outcome of the most recent decision.

        Args:
            success: Whether the decision led to a successful outcome
            result_summary: Summary of the result
        """
        if not self._tt_session:
            return

        try:
            from core.models_unified_system import DecisionPoint

            decision = DecisionPoint.objects.filter(
                session=self._tt_session
            ).order_by('-sequence_number').first()

            if decision:
                decision.was_successful = success
                decision.result_summary = result_summary
                decision.save()

        except Exception as e:
            logger.warning(f"Failed to mark decision outcome: {e}")

    def flag_decision(self, reason: str):
        """
        Flag the most recent decision for review.

        Args:
            reason: Why this decision should be reviewed
        """
        if not self._tt_session:
            return

        try:
            from core.models_unified_system import DecisionPoint

            decision = DecisionPoint.objects.filter(
                session=self._tt_session
            ).order_by('-sequence_number').first()

            if decision:
                decision.is_flagged = True
                decision.flag_reason = reason
                decision.save()

        except Exception as e:
            logger.warning(f"Failed to flag decision: {e}")


def time_travel_tracked(task_type: str):
    """
    Decorator to automatically wrap an agent method with time travel tracking.

    Args:
        task_type: Type of task for the session

    Example:
        @time_travel_tracked("image_generation")
        def generate_image(self, prompt, style):
            # Your code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if this object has time travel mixin
            if not hasattr(self, 'time_travel_session'):
                return func(self, *args, **kwargs)

            # Build description from args
            description = f"{func.__name__}: {str(kwargs)[:100]}"

            with self.time_travel_session(task_type, description, input_data=kwargs):
                return func(self, *args, **kwargs)

        return wrapper
    return decorator
