"""
Context Tracing Service
=======================

Session 875: Comprehensive tracing to identify where context type mutations occur.

This service provides:
1. Trace ID generation and propagation
2. Logging at mutation points (LLM, parser, pre-enqueue, post-deserialize)
3. BadContextEvent persistence for forensic analysis
4. Schema validation for next_steps

Usage:
    from core.services.context_tracing import ContextTracer, trace_context

    # Start a trace
    tracer = ContextTracer.start_trace(source='autonomy_cycle')

    # Log at mutation points
    tracer.log_llm_output(raw_response, parsed_next_steps)
    tracer.log_parser_output(action_name, agent_name, context)
    tracer.log_pre_enqueue(task_name, payload)
    tracer.log_post_deserialize(context)

    # Or use decorator
    @trace_context
    def my_function(context, trace_id=None):
        ...
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from functools import wraps
from django.utils import timezone

logger = logging.getLogger(__name__)

# Thread-local storage for trace context
import threading
_trace_context = threading.local()


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID from thread-local storage."""
    return getattr(_trace_context, 'trace_id', None)


def set_current_trace_id(trace_id: str) -> None:
    """Set the current trace ID in thread-local storage."""
    _trace_context.trace_id = trace_id


def generate_trace_id() -> str:
    """Generate a new trace ID."""
    return f"ctx_{uuid.uuid4().hex[:12]}"


def safe_repr(obj: Any, max_length: int = 500) -> str:
    """Safely represent an object for logging (truncated, no sensitive data)."""
    try:
        if obj is None:
            return "None"
        if isinstance(obj, dict):
            # Redact sensitive fields
            redacted = {
                k: "***REDACTED***" if k.lower() in ('password', 'token', 'secret', 'api_key', 'key')
                else safe_repr(v, max_length // 2) if isinstance(v, (dict, list)) else repr(v)[:100]
                for k, v in list(obj.items())[:20]  # Limit keys
            }
            result = str(redacted)
        elif isinstance(obj, list):
            result = f"[list of {len(obj)} items: {[safe_repr(x, 50) for x in obj[:5]]}...]"
        else:
            result = repr(obj)
        return result[:max_length] + "..." if len(result) > max_length else result
    except Exception as e:
        return f"<repr error: {e}>"


@dataclass
class ContextSnapshot:
    """Snapshot of context at a specific point in execution."""
    trace_id: str
    stage: str  # 'llm_raw', 'parser', 'pre_enqueue', 'post_deserialize', 'router', 'agent'
    timestamp: datetime
    context_type: str
    context_keys: List[str] = field(default_factory=list)
    context_preview: str = ""
    agent_name: str = ""
    action_name: str = ""
    task_name: str = ""
    is_valid: bool = True
    error_message: str = ""
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'stage': self.stage,
            'timestamp': self.timestamp.isoformat(),
            'context_type': self.context_type,
            'context_keys': self.context_keys,
            'context_preview': self.context_preview,
            'agent_name': self.agent_name,
            'action_name': self.action_name,
            'task_name': self.task_name,
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'extra_data': self.extra_data,
        }


class ContextTracer:
    """
    Traces context through the execution pipeline to identify type mutations.
    """

    def __init__(self, trace_id: str = None, source: str = "unknown"):
        self.trace_id = trace_id or generate_trace_id()
        self.source = source
        self.snapshots: List[ContextSnapshot] = []
        self.created_at = timezone.now()

        # Set thread-local trace ID
        set_current_trace_id(self.trace_id)

        logger.info(f"[TRACE:{self.trace_id}] Started context trace from source={source}")

    @classmethod
    def start_trace(cls, source: str = "unknown") -> 'ContextTracer':
        """Start a new trace with a fresh trace ID."""
        return cls(source=source)

    @classmethod
    def continue_trace(cls, trace_id: str, source: str = "unknown") -> 'ContextTracer':
        """Continue an existing trace."""
        return cls(trace_id=trace_id, source=source)

    def _create_snapshot(
        self,
        stage: str,
        context: Any,
        agent_name: str = "",
        action_name: str = "",
        task_name: str = "",
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """Create a snapshot of the current context state."""
        context_type = type(context).__name__
        is_valid = isinstance(context, dict) or context is None

        snapshot = ContextSnapshot(
            trace_id=self.trace_id,
            stage=stage,
            timestamp=timezone.now(),
            context_type=context_type,
            context_keys=list(context.keys()) if isinstance(context, dict) else [],
            context_preview=safe_repr(context),
            agent_name=agent_name,
            action_name=action_name,
            task_name=task_name,
            is_valid=is_valid,
            error_message="" if is_valid else f"Expected dict, got {context_type}",
            extra_data=extra_data or {},
        )

        self.snapshots.append(snapshot)
        return snapshot

    def log_llm_output(
        self,
        raw_response: Any,
        parsed_next_steps: List[Any],
        model: str = "",
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point A: Immediately after LLM response.

        This tells you: "did the model emit a list where it shouldn't?"
        """
        snapshot = self._create_snapshot(
            stage="llm_raw",
            context=parsed_next_steps,
            extra_data={
                'model': model,
                'raw_response_type': type(raw_response).__name__,
                'raw_response_preview': safe_repr(raw_response, 300),
                'next_steps_count': len(parsed_next_steps) if isinstance(parsed_next_steps, list) else 0,
                **(extra_data or {}),
            }
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] LLM_OUTPUT stage={snapshot.stage} "
            f"next_steps_type={snapshot.context_type} count={len(parsed_next_steps) if isinstance(parsed_next_steps, list) else 'N/A'} "
            f"model={model}"
        )

        return snapshot

    def log_parser_output(
        self,
        action_name: str,
        agent_name: str,
        context: Any,
        raw_step: str = "",
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point B: After parsing next_steps into dispatcher input.

        This tells you: "did the parser create the list?"
        """
        snapshot = self._create_snapshot(
            stage="parser",
            context=context,
            agent_name=agent_name,
            action_name=action_name,
            extra_data={
                'raw_step_preview': raw_step[:200] if raw_step else "",
                **(extra_data or {}),
            }
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] PARSER stage={snapshot.stage} "
            f"agent={agent_name} action={action_name[:50]} "
            f"context_type={snapshot.context_type} "
            f"context_keys={snapshot.context_keys}"
        )

        if not snapshot.is_valid:
            self._record_bad_context_event(snapshot)

        return snapshot

    def log_pre_enqueue(
        self,
        task_name: str,
        agent_name: str,
        context: Any,
        queue: str = "",
        serializer: str = "json",
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point C: Right before Celery enqueue (serialize boundary).

        This tells you: "did we enqueue a dict or a list?"
        """
        # Check payload size
        try:
            payload_size = len(json.dumps(context, default=str)) if context else 0
        except Exception:
            payload_size = -1

        snapshot = self._create_snapshot(
            stage="pre_enqueue",
            context=context,
            agent_name=agent_name,
            task_name=task_name,
            extra_data={
                'queue': queue,
                'serializer': serializer,
                'payload_size': payload_size,
                **(extra_data or {}),
            }
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] PRE_ENQUEUE stage={snapshot.stage} "
            f"task={task_name} agent={agent_name} "
            f"context_type={snapshot.context_type} "
            f"payload_size={payload_size} serializer={serializer}"
        )

        if not snapshot.is_valid:
            self._record_bad_context_event(snapshot)

        return snapshot

    def log_post_deserialize(
        self,
        context: Any,
        agent_name: str = "",
        task_name: str = "",
        args_types: List[str] = None,
        kwargs_keys: List[str] = None,
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point D: Inside Celery task at start (post-deserialize boundary).

        This tells you: "did Celery change it?"
        """
        snapshot = self._create_snapshot(
            stage="post_deserialize",
            context=context,
            agent_name=agent_name,
            task_name=task_name,
            extra_data={
                'args_types': args_types or [],
                'kwargs_keys': kwargs_keys or [],
                **(extra_data or {}),
            }
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] POST_DESERIALIZE stage={snapshot.stage} "
            f"task={task_name} agent={agent_name} "
            f"context_type={snapshot.context_type} "
            f"args_types={args_types} kwargs_keys={kwargs_keys}"
        )

        if not snapshot.is_valid:
            self._record_bad_context_event(snapshot)

        return snapshot

    def log_router(
        self,
        agent_name: str,
        task: str,
        context: Any,
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point E: At AgentRouter.route() entry.
        """
        snapshot = self._create_snapshot(
            stage="router",
            context=context,
            agent_name=agent_name,
            action_name=task[:100] if task else "",
            extra_data=extra_data,
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] ROUTER stage={snapshot.stage} "
            f"agent={agent_name} "
            f"context_type={snapshot.context_type} "
            f"context_keys={snapshot.context_keys}"
        )

        if not snapshot.is_valid:
            self._record_bad_context_event(snapshot)

        return snapshot

    def log_agent(
        self,
        agent_name: str,
        context: Any,
        extra_data: Dict[str, Any] = None
    ) -> ContextSnapshot:
        """
        Log at Point F: At agent.execute() entry.
        """
        snapshot = self._create_snapshot(
            stage="agent",
            context=context,
            agent_name=agent_name,
            extra_data=extra_data,
        )

        log_level = logging.WARNING if not snapshot.is_valid else logging.DEBUG
        logger.log(
            log_level,
            f"[TRACE:{self.trace_id}] AGENT stage={snapshot.stage} "
            f"agent={agent_name} "
            f"context_type={snapshot.context_type} "
            f"context_keys={snapshot.context_keys}"
        )

        if not snapshot.is_valid:
            self._record_bad_context_event(snapshot)

        return snapshot

    def _record_bad_context_event(self, snapshot: ContextSnapshot) -> None:
        """Persist a bad context event to the database."""
        try:
            from core.models_unified_system import BadContextEvent

            BadContextEvent.objects.create(
                trace_id=self.trace_id,
                stage=snapshot.stage,
                agent_name=snapshot.agent_name,
                action_name=snapshot.action_name,
                task_name=snapshot.task_name,
                context_type=snapshot.context_type,
                context_preview=snapshot.context_preview[:1000],
                error_message=snapshot.error_message,
                extra_data=snapshot.extra_data,
                source=self.source,
            )

            logger.warning(
                f"[TRACE:{self.trace_id}] BAD_CONTEXT_EVENT recorded: "
                f"stage={snapshot.stage} type={snapshot.context_type}"
            )

            # Send alert
            self._send_alert(snapshot)

        except Exception as e:
            logger.error(f"[TRACE:{self.trace_id}] Failed to record BadContextEvent: {e}")

    def _send_alert(self, snapshot: ContextSnapshot) -> None:
        """Send Discord alert for bad context event."""
        try:
            from core.services.discord_bot import send_discord_alert

            send_discord_alert(
                title="Bad Context Type Detected",
                message=(
                    f"**Trace ID:** `{self.trace_id}`\n"
                    f"**Stage:** {snapshot.stage}\n"
                    f"**Agent:** {snapshot.agent_name or 'N/A'}\n"
                    f"**Expected:** dict\n"
                    f"**Got:** {snapshot.context_type}\n"
                    f"**Preview:** ```{snapshot.context_preview[:300]}```"
                ),
                level="warning"
            )
        except Exception as e:
            logger.debug(f"[TRACE:{self.trace_id}] Discord alert skipped: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all snapshots in this trace."""
        invalid_snapshots = [s for s in self.snapshots if not s.is_valid]

        return {
            'trace_id': self.trace_id,
            'source': self.source,
            'created_at': self.created_at.isoformat(),
            'total_snapshots': len(self.snapshots),
            'invalid_snapshots': len(invalid_snapshots),
            'stages_visited': [s.stage for s in self.snapshots],
            'first_invalid_stage': invalid_snapshots[0].stage if invalid_snapshots else None,
            'snapshots': [s.to_dict() for s in self.snapshots],
        }


# ============================================================================
# Schema Validation for next_steps
# ============================================================================

@dataclass
class ActionDirective:
    """Validated action directive from next_steps."""
    agent: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    raw_text: str = ""


def validate_next_steps(
    next_steps: Any,
    trace_id: str = None
) -> Tuple[List[ActionDirective], List[str]]:
    """
    Validate and parse next_steps into ActionDirectives.

    Args:
        next_steps: Raw next_steps from LLM (expected: list of strings or dicts)
        trace_id: Optional trace ID for logging

    Returns:
        Tuple of (valid_directives, schema_errors)
    """
    trace_id = trace_id or get_current_trace_id() or "no_trace"
    valid_directives = []
    schema_errors = []

    if next_steps is None:
        return [], []

    if not isinstance(next_steps, list):
        schema_errors.append(f"next_steps must be list, got {type(next_steps).__name__}")
        logger.warning(f"[TRACE:{trace_id}] SCHEMA_VIOLATION: next_steps is not a list")
        return [], schema_errors

    for i, step in enumerate(next_steps):
        try:
            if isinstance(step, str):
                # Parse string format: "AgentName: action description"
                directive = _parse_string_step(step)
                if directive:
                    valid_directives.append(directive)
                else:
                    schema_errors.append(f"Step {i}: Could not parse string: {step[:100]}")

            elif isinstance(step, dict):
                # Structured format: {agent: str, action: str, context: dict}
                directive = _parse_dict_step(step)
                if directive:
                    valid_directives.append(directive)
                else:
                    schema_errors.append(f"Step {i}: Invalid dict structure: {step}")
            else:
                schema_errors.append(f"Step {i}: Invalid type {type(step).__name__}")

        except Exception as e:
            schema_errors.append(f"Step {i}: Parse error: {e}")

    if schema_errors:
        logger.warning(
            f"[TRACE:{trace_id}] SCHEMA_VALIDATION: {len(schema_errors)} errors, "
            f"{len(valid_directives)} valid directives"
        )

    return valid_directives, schema_errors


def _parse_string_step(step: str) -> Optional[ActionDirective]:
    """Parse a string step like 'AgentName: action description'."""
    import re

    # Pattern: "AgentName: action" or "AgentName - action"
    pattern = r'^(?P<agent>[A-Z][a-zA-Z]+(?:Agent|Coordinator|Analyst|Detector)?)\s*[:\-]\s*(?P<action>.+)$'
    match = re.match(pattern, step.strip())

    if match:
        return ActionDirective(
            agent=match.group('agent'),
            action=match.group('action').strip(),
            context={},
            confidence=1.0,
            raw_text=step
        )

    return None


def _parse_dict_step(step: Dict[str, Any]) -> Optional[ActionDirective]:
    """Parse a dict step like {agent: 'Name', action: 'desc', context: {...}}."""
    agent = step.get('agent') or step.get('agent_name')
    action = step.get('action') or step.get('task') or step.get('description')
    context = step.get('context', {})

    if not agent or not action:
        return None

    # Validate context is a dict
    if not isinstance(context, dict):
        # Auto-repair: wrap list in dict
        if isinstance(context, list):
            context = {'items': context}
        else:
            context = {}

    return ActionDirective(
        agent=agent,
        action=action,
        context=context,
        confidence=step.get('confidence', 1.0),
        raw_text=str(step)
    )


# ============================================================================
# Auto-Repair Functions
# ============================================================================

def auto_repair_context(
    context: Any,
    expected_schema: str = "generic",
    trace_id: str = None
) -> Dict[str, Any]:
    """
    Attempt to repair an invalid context into a valid dict.

    Args:
        context: The potentially invalid context
        expected_schema: What kind of context is expected ('topics', 'generic', etc.)
        trace_id: Optional trace ID for logging

    Returns:
        A valid dict context (repaired or empty)
    """
    trace_id = trace_id or get_current_trace_id() or "no_trace"

    if isinstance(context, dict):
        return context

    if context is None:
        return {}

    # Repair strategies based on expected schema
    if isinstance(context, list):
        if expected_schema == 'topics' and all(isinstance(x, str) for x in context):
            # List of topic strings -> wrap in dict
            logger.info(f"[TRACE:{trace_id}] AUTO_REPAIR: Wrapped list of topics in dict")
            return {'topics': context}
        elif all(isinstance(x, str) for x in context):
            # Generic list of strings
            logger.info(f"[TRACE:{trace_id}] AUTO_REPAIR: Wrapped list of strings in dict")
            return {'items': context}
        else:
            # Complex list
            logger.info(f"[TRACE:{trace_id}] AUTO_REPAIR: Wrapped complex list in dict")
            return {'data': context}

    if isinstance(context, str):
        logger.info(f"[TRACE:{trace_id}] AUTO_REPAIR: Wrapped string in dict")
        return {'message': context}

    # Unknown type - return empty
    logger.warning(f"[TRACE:{trace_id}] AUTO_REPAIR: Could not repair {type(context).__name__}, using empty dict")
    return {}


# ============================================================================
# Decorator for tracing
# ============================================================================

def trace_context(stage: str = "generic"):
    """
    Decorator to trace context at function entry.

    Usage:
        @trace_context(stage="router")
        def route(self, agent_name, task, context=None):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context = kwargs.get('context')
            trace_id = kwargs.get('trace_id') or get_current_trace_id()

            if trace_id and context is not None:
                tracer = ContextTracer.continue_trace(trace_id, source=func.__name__)
                tracer.log_router(
                    agent_name=kwargs.get('agent_name', args[1] if len(args) > 1 else 'unknown'),
                    task=kwargs.get('task', args[2] if len(args) > 2 else ''),
                    context=context
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Singleton tracer cache
# ============================================================================

_active_tracers: Dict[str, ContextTracer] = {}


def get_or_create_tracer(trace_id: str = None, source: str = "unknown") -> ContextTracer:
    """Get an existing tracer or create a new one."""
    if trace_id and trace_id in _active_tracers:
        return _active_tracers[trace_id]

    tracer = ContextTracer(trace_id=trace_id, source=source)
    _active_tracers[tracer.trace_id] = tracer

    # Cleanup old tracers (keep last 100)
    if len(_active_tracers) > 100:
        oldest_keys = sorted(_active_tracers.keys())[:50]
        for key in oldest_keys:
            del _active_tracers[key]

    return tracer
