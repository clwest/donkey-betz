"""
Session 1098: LLM Call Wrapper

Centralized wrapper for LLM API calls. Produces one LLMCallEvent row
per invocation with execution_id correlation, provider/model,
duration, token counts, retry/error classification, and cancellation
flag.

Scope (PR #1 of 4 — see conversation pa-3c7ddc058db1):

    #1 (this module): execution_id + per-call telemetry
    #2: CI lint forbidding direct SDK calls outside this wrapper
    #3: Cooperative cancel_token end-to-end (provider aborts)
    #4: Nested dispatch budget (parent token propagates to children)

Deliberately out of scope for PR #1:

- Cancellation semantics beyond entry-time token check. The wrapper
  accepts ``cancel_token`` and ``LLMCallCancelled`` today so callers can
  adopt the wrapper without signature churn when PR #3 lands; provider
  adapters do not yet abort in-flight sockets.
- Provider migration. Callers still use get_openai_client() /
  get_anthropic_client() and invoke the provider SDK themselves. The
  wrapper only brackets the call with telemetry.

Telemetry is best-effort: a failing LLMCallEvent save must never mask
the real LLM response or exception, so every ORM call is wrapped in a
``_save_event_safe()`` helper.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union

from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────── public types ──────────────────────────── #


class LLMCallCancelled(Exception):
    """Raised when an LLM call is cancelled via its ``CancelToken``.

    PR #1 only observes the token at span entry. PR #3 will add
    provider-adapter level aborts so in-flight sockets are torn down
    when the orchestration layer cancels an execution.
    """


@dataclass
class CancelToken:
    """Cooperative cancellation token.

    PR #1 ships this as a no-op holder — ``is_cancelled()`` returns
    False unless the caller explicitly calls ``cancel()``. PR #3 will
    wire orchestration-level cancellation so every in-flight LLM call
    observes the signal.
    """

    _cancelled: bool = field(default=False)

    def cancel(self) -> None:
        self._cancelled = True

    def is_cancelled(self) -> bool:
        return self._cancelled


# ──────────────────────── internal helpers ─────────────────────────── #


_ExecutionIdLike = Optional[Union[uuid.UUID, str]]


def _coerce_execution_id(value: _ExecutionIdLike) -> Optional[uuid.UUID]:
    """Accept UUID, str, or None; return UUID or None. Never raises."""
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        return None


def _classify_error(exc: BaseException) -> str:
    """Collapse provider SDK exceptions into LLMCallEvent error codes.

    Unknown types fall back to 'unknown'. Keep the classifier conservative
    so dashboards can rely on the small error_type enum.
    """
    name = type(exc).__name__.lower()
    msg = (str(exc) or '').lower()
    if 'timeout' in name or 'timeout' in msg:
        return 'timeout'
    if 'ratelimit' in name or 'rate limit' in msg or 'too many requests' in msg:
        return 'rate_limit'
    if (
        'authentication' in name
        or 'permissiondenied' in name
        or 'unauthorized' in msg
        or 'invalid api key' in msg
    ):
        return 'auth'
    if (
        'apiconnection' in name
        or 'connectionerror' in name
        or 'remotedisconnected' in name
        or 'connection refused' in msg
    ):
        return 'client_error'
    if 'apistatuserror' in name or 'apierror' in name or 'badrequest' in name:
        return 'api_error'
    return 'unknown'


def _extract_usage(response: Any) -> Dict[str, Optional[int]]:
    """Best-effort token-usage extraction from common provider shapes.

    - OpenAI: ``response.usage.prompt_tokens`` / ``completion_tokens``
    - Anthropic: ``response.usage.input_tokens`` / ``output_tokens``
    - Response dict (some wrappers): ``response['usage'][...]``

    Returns ``{'tokens_in': int|None, 'tokens_out': int|None}``.
    """
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    try:
        usage = getattr(response, 'usage', None)
        if usage is None and isinstance(response, dict):
            usage = response.get('usage')
        if usage is None:
            return {'tokens_in': None, 'tokens_out': None}
        tokens_in = (
            getattr(usage, 'prompt_tokens', None)
            or getattr(usage, 'input_tokens', None)
        )
        tokens_out = (
            getattr(usage, 'completion_tokens', None)
            or getattr(usage, 'output_tokens', None)
        )
        if tokens_in is None and isinstance(usage, dict):
            tokens_in = usage.get('prompt_tokens') or usage.get('input_tokens')
        if tokens_out is None and isinstance(usage, dict):
            tokens_out = (
                usage.get('completion_tokens') or usage.get('output_tokens')
            )
    except Exception:  # pragma: no cover - defensive
        pass
    return {'tokens_in': tokens_in, 'tokens_out': tokens_out}


def _save_event_safe(event: Any, **updates: Any) -> None:
    """Update + save an LLMCallEvent, swallowing every DB error.

    Telemetry failures must never mask the real LLM response or error.
    """
    if event is None:
        return
    try:
        for k, v in updates.items():
            setattr(event, k, v)
        event.save()
    except Exception as save_exc:  # pragma: no cover - defensive
        logger.exception(
            f"[llm_call_wrapper] LLMCallEvent save failed: {save_exc}"
        )


def _create_event_safe(
    *,
    call_id: uuid.UUID,
    execution_id: Optional[uuid.UUID],
    agent_name: str,
    provider: str,
    model: str,
    started_at,
    metadata: Dict[str, Any],
) -> Any:
    """Create the STARTED row, returning None on failure.

    Same 'best-effort' contract as ``_save_event_safe``.
    """
    try:
        from core.models_llm_telemetry import LLMCallEvent
        return LLMCallEvent.objects.create(
            call_id=call_id,
            execution_id=execution_id,
            agent_name=agent_name or '',
            provider=provider or '',
            model=model or '',
            status='STARTED',
            started_at=started_at,
            metadata=metadata or {},
        )
    except Exception as create_exc:  # pragma: no cover - defensive
        logger.exception(
            f"[llm_call_wrapper] LLMCallEvent create failed: {create_exc}"
        )
        return None


class _Span:
    """Handle returned by ``llm_call_span`` — callers attach the raw
    provider response so the wrapper can extract token usage on exit."""

    def __init__(self, call_id: uuid.UUID) -> None:
        self.call_id: uuid.UUID = call_id
        self.response: Any = None

    def attach_response(self, response: Any) -> None:
        self.response = response


# ─────────────────────────── public API ────────────────────────────── #


def _check_cancel(
    *,
    cancel_token: Optional[CancelToken],
    execution_id: Optional[uuid.UUID],
    location: str,
    provider: str,
    model: str,
) -> None:
    """Raise LLMCallCancelled if either the direct token OR the registry
    (keyed by execution_id) reports cancellation.

    Session 1098 PR #3: the registry is the single source of truth for
    cooperative cancel. The direct ``cancel_token`` kwarg stays
    supported for test harnesses + callers that don't have an
    execution_id, but production code paths cancel by writing to the
    registry via ``request_execution_cancel()``.
    """
    if cancel_token is not None and cancel_token.is_cancelled():
        raise LLMCallCancelled(
            f"LLM call cancelled before start (cancel_token; "
            f"provider={provider}, model={model})"
        )

    if execution_id is not None:
        try:
            from core.services.cancel_registry import (
                is_execution_cancelled,
                mark_observed,
            )
            if is_execution_cancelled(execution_id):
                mark_observed(execution_id, location=location)
                raise LLMCallCancelled(
                    f"LLM call cancelled via registry "
                    f"(execution_id={execution_id}, location={location}, "
                    f"provider={provider}, model={model})"
                )
        except LLMCallCancelled:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug(
                "[llm_call_wrapper] registry check failed at %s: %s",
                location, exc,
            )


@contextmanager
def llm_call_span(
    *,
    provider: str,
    model: str,
    execution_id: _ExecutionIdLike = None,
    agent_name: str = '',
    cancel_token: Optional[CancelToken] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Bracket a sync LLM call with one LLMCallEvent span.

    Usage::

        with llm_call_span(
            provider='openai',
            model='gpt-5-mini',
            execution_id=ctx.get('execution_id'),
            agent_name='ThinkingAgent',
        ) as span:
            response = client.chat.completions.create(...)
            span.attach_response(response)  # enables token-usage capture
        # telemetry row is written on context exit

    Exceptions (including ``LLMCallCancelled``) propagate. The span row
    is always finalized — success, failure, or cancellation.

    PR #3 addition: before yielding to the caller, checks the global
    ``cancel_registry`` by execution_id. If the registry reports the
    execution cancelled, raises LLMCallCancelled immediately and
    records the observation location. Orchestration-level cancel
    signals reach in-flight LLM calls without threading a CancelToken.

    Note: the sync context manager uses ``model`` as its kwarg because
    there's no forwarding collision — the caller invokes the provider
    SDK themselves inside the block. The async wrapper, which *does*
    forward kwargs to the provider, uses ``model_name`` instead.
    """
    exec_uuid = _coerce_execution_id(execution_id)

    _check_cancel(
        cancel_token=cancel_token,
        execution_id=exec_uuid,
        location=f"LLMCallWrapper.span:pre-call:{agent_name or 'unknown'}",
        provider=provider,
        model=model,
    )
    call_id = uuid.uuid4()
    started_at = timezone.now()
    started_perf = time.perf_counter()

    event = _create_event_safe(
        call_id=call_id,
        execution_id=exec_uuid,
        agent_name=agent_name,
        provider=provider,
        model=model,
        started_at=started_at,
        metadata=metadata or {},
    )

    span = _Span(call_id=call_id)

    try:
        yield span
    except LLMCallCancelled as exc:
        _save_event_safe(
            event,
            status='CANCELLED',
            cancelled=True,
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            error_type='cancelled',
            error_message=str(exc)[:2000],
        )
        raise
    except Exception as exc:
        _save_event_safe(
            event,
            status='FAILED',
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            error_type=_classify_error(exc),
            error_message=str(exc)[:2000],
        )
        raise
    else:
        usage = _extract_usage(span.response)
        _save_event_safe(
            event,
            status='SUCCESS',
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            tokens_in=usage['tokens_in'],
            tokens_out=usage['tokens_out'],
        )


async def llm_call_async(
    fn: Callable[..., Any],
    *args,
    provider: str,
    model_name: str,
    execution_id: _ExecutionIdLike = None,
    agent_name: str = '',
    cancel_token: Optional[CancelToken] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Any:
    """Async twin of ``llm_call_span``. Runs ``fn(*args, **kwargs)`` with
    LLMCallEvent telemetry around it; returns ``fn``'s return value.

    ``fn`` may be sync or async. The wrapper inspects the return and
    awaits when needed. This lets ``async def`` callers (e.g. ThinkingAgent
    ._call_llm) adopt the wrapper without restructuring their call site.

    Parameter naming: we use ``model_name`` (not ``model``) because the
    wrapper forwards ``**kwargs`` straight into ``fn``. Most provider
    SDK calls also accept ``model=...`` — naming collisions there would
    force callers to double-specify or use awkward wrappers. The
    telemetry value ends up in the ``model`` column of LLMCallEvent.
    """
    from asgiref.sync import sync_to_async

    exec_uuid = _coerce_execution_id(execution_id)

    # PR #3: registry + direct-token cancel check (see ``_check_cancel``).
    _check_cancel(
        cancel_token=cancel_token,
        execution_id=exec_uuid,
        location=f"LLMCallWrapper.async:pre-call:{agent_name or 'unknown'}",
        provider=provider,
        model=model_name,
    )

    call_id = uuid.uuid4()
    started_at = timezone.now()
    started_perf = time.perf_counter()

    event = await sync_to_async(_create_event_safe, thread_sensitive=False)(
        call_id=call_id,
        execution_id=exec_uuid,
        agent_name=agent_name,
        provider=provider,
        model=model_name,
        started_at=started_at,
        metadata=metadata or {},
    )

    try:
        result = fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
    except LLMCallCancelled as exc:
        await sync_to_async(_save_event_safe, thread_sensitive=False)(
            event,
            status='CANCELLED',
            cancelled=True,
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            error_type='cancelled',
            error_message=str(exc)[:2000],
        )
        raise
    except Exception as exc:
        await sync_to_async(_save_event_safe, thread_sensitive=False)(
            event,
            status='FAILED',
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            error_type=_classify_error(exc),
            error_message=str(exc)[:2000],
        )
        raise
    else:
        usage = _extract_usage(result)
        await sync_to_async(_save_event_safe, thread_sensitive=False)(
            event,
            status='SUCCESS',
            finished_at=timezone.now(),
            duration_ms=int((time.perf_counter() - started_perf) * 1000),
            tokens_in=usage['tokens_in'],
            tokens_out=usage['tokens_out'],
        )
        return result


__all__ = [
    'LLMCallCancelled',
    'CancelToken',
    'llm_call_span',
    'llm_call_async',
]
