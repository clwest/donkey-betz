"""
Failure-Data Safety Contract enforcement — Layer 1 (DRF exception handler)
and Layer 2 (Django middleware).

Implements contract §3 (user-facing envelope) + §6 (operator envelope) +
§8.1-§8.2 (enforcement layers 1 and 2).

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
    docs/research/implementation/RATIFICATION_2026-07-10_i0301_safety_contract.md

Rigby Stage 1 SIGN constraints folded in:
    * Q4: DRF-standard exception mapping; NEVER echo `detail` / `exception_message`
      into `human_message`. Always contract-default English copy.
    * Q5: middleware placement is an invariant (after auth-population, before
      response rendering / debug), safe for anonymous requests.
    * Q8: trace_id emitted as per-exception UUID with clear "non-propagated
      interim" naming; NEVER exposed to user (only in operator envelope).
    * Q9: OpsRunEvent write is BEST-EFFORT — failure to write MUST NOT break
      the user response.
"""
from __future__ import annotations

import logging
import time
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from django.http import JsonResponse

from core.security.reason_codes import (
    DRF_EXCEPTION_REASON_MAP,
    REASON_CODES,
    ReasonCode,
    get_reason,
)
from core.security.support_code import make_support_code

logger = logging.getLogger(__name__)

# Mapping of reason_code → support_code component (contract §5.1 enum).
_REASON_TO_COMPONENT = {
    "not_found": "MISSING",
    "not_authenticated": "AUTH",
    "permission_denied": "PERM",
    "workspace_not_accessible": "WORKSPACE",
    "invalid_input": "INPUT",
    "validation_error": "VALIDATE",
    "rate_limited": "RATE",
    "busy": "BUSY",
    "upstream_provider_error": "UPSTREAM",
    "upstream_provider_timeout": "UPSTREAM",
    "cost_cap_exceeded": "COST",
    "cancelled": "CANCEL",
    "internal_error": "INTERNAL",
    "unavailable": "INTERNAL",
    "tenant_boundary_violation": "TENANT",
}

# Long-lived parent OpsRun title used by every safety-contract emission.
# See ``_get_or_create_rur_failure_run`` for the rationale.
_RUR_FAILURE_RUN_TITLE = "rur_safety_contract_failures"


# ─────────────────────────────────────────────────────────────────────
# Envelope construction (contract §3.1 + §6.1)
# ─────────────────────────────────────────────────────────────────────


def build_user_facing_envelope(
    reason_code: str,
    support_code: Optional[str] = None,
    retry_after_seconds: Optional[int] = None,
    include_timestamp: bool = True,
) -> dict[str, Any]:
    """Construct the user-facing error envelope per contract §3.1.

    Returns a dict with ONLY the permitted fields (per contract §3.1):
    ``support_code``, ``reason_code``, ``human_message``, ``retryable``,
    ``terminal_state``, and optionally ``timestamp`` +
    ``retry_after_seconds``.

    No additional fields are ever emitted.
    """
    reason = get_reason(reason_code)

    if support_code is None:
        support_code = make_support_code(_REASON_TO_COMPONENT[reason_code])

    envelope: dict[str, Any] = {
        "support_code": support_code,
        "reason_code": reason.code,
        # Contract §3.2 + Rigby SIGN Q4: NEVER echo exception message.
        # Use only the ratified default copy.
        "human_message": reason.default_message,
        "retryable": reason.retryable,
        "terminal_state": reason.terminal_state,
    }

    if include_timestamp:
        # Contract §3.1: server-generated request handling time; never
        # echoed from client input.
        envelope["timestamp"] = datetime.now(timezone.utc).isoformat()

    if retry_after_seconds is not None and reason.terminal_state in {
        "RATE_LIMITED",
        "BUSY",
    }:
        # Contract §3.1: retry_after_seconds only meaningful for these states.
        envelope["retry_after_seconds"] = int(retry_after_seconds)

    return envelope


def build_operator_envelope(
    request,
    exc: BaseException,
    support_code: str,
    reason_code: str,
    trace_id: Optional[str] = None,
    request_started_at: Optional[float] = None,
) -> dict[str, Any]:
    """Construct the operator-side envelope per contract §6.1.

    This is the diagnostic envelope written to OpsRunEvent.detail. The
    fields here MAY contain tenant identifiers because the row itself
    is tenant-scoped at read time (per contract §6.2).

    trace_id is non-propagated interim per Rigby SIGN Q8. RUR-C2 will
    replace this with a request-scoped propagated trace_id.
    """
    reason = get_reason(reason_code)

    # request may be None (e.g., middleware called before request assembly)
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    if request is not None:
        try:
            user = getattr(request, "user", None)
            if user is not None and getattr(user, "is_authenticated", False):
                user_id = str(user.pk) if user.pk is not None else None
        except Exception:  # noqa: BLE001 — best-effort per Rigby SIGN Q9
            pass
        endpoint = getattr(request, "path", None)
        http_method = getattr(request, "method", None)

    if trace_id is None:
        # Rigby SIGN Q8: per-exception UUID; RUR-C2 will propagate a
        # request-scoped trace_id. Naming preserved for cross-arc
        # consistency.
        trace_id = str(uuid.uuid4())

    exc_class = type(exc).__name__
    # Contract §3.2 + §6.1: exception_message stays operator-only.
    exc_message = str(exc) if exc is not None else ""

    request_completed_at = time.time()
    if request_started_at is not None:
        duration_ms = int((request_completed_at - request_started_at) * 1000)
    else:
        duration_ms = None

    return {
        "support_code": support_code,
        "trace_id": trace_id,
        "reason_code": reason.code,
        "exception_class": exc_class,
        "exception_message": exc_message,
        "request_context": {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "endpoint": endpoint,
            "http_method": http_method,
        },
        "timing": {
            "request_completed_at": datetime.fromtimestamp(
                request_completed_at, tz=timezone.utc
            ).isoformat(),
            "request_duration_ms": duration_ms,
        },
    }


# ─────────────────────────────────────────────────────────────────────
# OpsRunEvent write (contract §6.1 + Rigby SIGN Q9 best-effort discipline)
# ─────────────────────────────────────────────────────────────────────


def _get_or_create_rur_failure_run():
    """Return the shared long-lived OpsRun used as the parent for
    safety-contract failure events.

    OpsRunEvent requires an OpsRun FK. A per-request OpsRun would double
    the write volume. A shared long-lived Run keeps writes minimal while
    still using the ratified substrate.

    Tenant scoping happens at query time on the child OpsRunEvent rows
    via the ``detail.request_context.workspace_id`` key.
    """
    from core.models_ops_runs import OpsRun

    run, _created = OpsRun.objects.get_or_create(
        title=_RUR_FAILURE_RUN_TITLE,
        defaults={
            "run_type": "manual",
            "triggered_by": "manual",
            "domain": "ops",
            "run_kind": "safety_contract",
            "status": "running",
        },
    )
    return run


def _emit_operator_envelope_best_effort(operator_envelope: dict[str, Any]) -> None:
    """Write the operator envelope to OpsRunEvent as a child of the
    shared safety-contract Run. Best-effort: any exception is swallowed
    per Rigby SIGN Q9 (never break the user response by trying to log
    a failure).
    """
    try:
        from core.models_ops_runs import OpsRunEvent

        run = _get_or_create_rur_failure_run()
        OpsRunEvent.objects.create(
            run=run,
            event_type="step_fail",
            label=operator_envelope.get("reason_code", "unknown"),
            detail=operator_envelope,
        )
    except Exception:  # noqa: BLE001
        # Rigby SIGN Q9: MUST NOT break user response on emit failure.
        logger.warning(
            "RUR safety-contract operator envelope write failed (swallowed): %s",
            traceback.format_exc(limit=2),
        )


# ─────────────────────────────────────────────────────────────────────
# Layer 1: DRF exception handler (contract §8.1)
# ─────────────────────────────────────────────────────────────────────


def drf_exception_handler(exc, context):
    """Custom DRF exception handler conforming to contract §8.1.

    Wraps DRF's default handler. Maps known DRF exception types to
    ratified reason_codes; falls back to `internal_error` for anything
    unexpected. Emits operator envelope to OpsRunEvent (best-effort).

    Wired via ``REST_FRAMEWORK['EXCEPTION_HANDLER']`` in settings.
    """
    from rest_framework.views import exception_handler as drf_default_handler

    request = context.get("request") if context else None
    request_started_at = getattr(request, "_rur_start_time", None) if request else None

    # Map exception → reason_code
    exc_class_name = type(exc).__name__
    reason_code = DRF_EXCEPTION_REASON_MAP.get(exc_class_name, "internal_error")

    # Determine typical HTTP status
    reason = get_reason(reason_code)
    http_status = reason.typical_status

    # Let DRF's default handler compute its status (it may differ, e.g.
    # for Throttled it computes 429 + Retry-After). If DRF returns a
    # response, take its status; otherwise use our default.
    drf_response = drf_default_handler(exc, context)
    if drf_response is not None:
        http_status = drf_response.status_code

    # retry_after_seconds for Throttled exceptions
    retry_after_seconds = None
    wait = getattr(exc, "wait", None)
    if wait is not None:
        try:
            retry_after_seconds = int(wait)
        except (TypeError, ValueError):
            pass

    support_code = make_support_code(_REASON_TO_COMPONENT[reason_code])

    user_envelope = build_user_facing_envelope(
        reason_code=reason_code,
        support_code=support_code,
        retry_after_seconds=retry_after_seconds,
    )
    operator_envelope = build_operator_envelope(
        request=request,
        exc=exc,
        support_code=support_code,
        reason_code=reason_code,
        request_started_at=request_started_at,
    )
    _emit_operator_envelope_best_effort(operator_envelope)

    # Return a fresh Response so we don't leak any DRF-produced `detail`.
    from rest_framework.response import Response

    return Response(user_envelope, status=http_status)


# ─────────────────────────────────────────────────────────────────────
# Layer 2: Django middleware (contract §8.2)
# ─────────────────────────────────────────────────────────────────────


class RURErrorEnvelopeMiddleware:
    """Catches uncaught exceptions from non-DRF Django views and emits
    the safety-contract envelope.

    Placement invariant (Rigby S2742 Stage 1 SIGN Q5):
        * AFTER any middleware that populates ``request.user`` (auth /
          session middleware)
        * BEFORE any middleware that renders error responses (debug /
          whitenoise / static)
        * Safe for anonymous requests (operator envelope tolerates
          missing ``request.user``)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach start time so the DRF handler and any downstream middleware
        # can compute duration for the operator envelope. Attribute name is
        # namespaced to avoid collisions.
        request._rur_start_time = time.time()
        return self.get_response(request)

    def process_exception(self, request, exc):
        """Return a safety-contract-conformant response for any exception
        that escapes non-DRF view code.

        DRF-handled paths are already covered by ``drf_exception_handler``
        (Layer 1). This middleware fires only for exceptions that DRF's
        handler did not catch (plain function views, class-based generic
        views, streaming errors, etc.).
        """
        # Determine reason_code from exception type
        exc_class_name = type(exc).__name__
        reason_code = DRF_EXCEPTION_REASON_MAP.get(exc_class_name, "internal_error")
        reason = get_reason(reason_code)

        support_code = make_support_code(_REASON_TO_COMPONENT[reason_code])

        user_envelope = build_user_facing_envelope(
            reason_code=reason_code,
            support_code=support_code,
        )
        operator_envelope = build_operator_envelope(
            request=request,
            exc=exc,
            support_code=support_code,
            reason_code=reason_code,
            request_started_at=getattr(request, "_rur_start_time", None),
        )
        _emit_operator_envelope_best_effort(operator_envelope)

        return JsonResponse(user_envelope, status=reason.typical_status)
