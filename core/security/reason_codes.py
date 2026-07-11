"""
reason_code enum per Failure-Data Safety Contract §4.

Public API discipline (Rigby S2742 Stage 1 SIGN Q2 constraint):
- Callers reference `reason_code` as a string only.
- Callers use ``get_reason(reason_code)`` to fetch the ReasonCode row.
- Callers MUST NOT construct ad-hoc codes; every `reason_code` string
  MUST appear in REASON_CODES.

The frozen enum per contract §4. Additions require a new ratification
record referencing the safety contract per contract §10. Current
amendments:

- ``tenant_boundary_violation`` — added at I-0303 Phase 2 (2026-07-11)
  per docs/research/implementation/RATIFICATION_2026-07-11_i0303_phase2_task_enforcement.md.
  Emitted by ``core.security.task_enforcement`` when an async-boundary
  tenant check fails (missing row / missing acting identity / predicate
  rejection). Same user-facing envelope regardless of failure_kind —
  existence-oracle protection per I-0303 scoping §1 harness contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ReasonCode:
    """Single row of the reason_code enum.

    Fields:
        code: the string emitted in the user-facing envelope §3.1
        default_message: the default English `human_message`; safe copy
            per §3.2 — never a raw exception message
        retryable: whether the client should auto-retry with backoff
        terminal_state: enum from §3.1 (`FAILED` / `CANCELLED` / `DENIED` /
            `RATE_LIMITED` / `BUSY`)
        typical_status: the HTTP status the envelope commonly ships with
    """

    code: str
    default_message: str
    retryable: bool
    terminal_state: str
    typical_status: int


REASON_CODES: Final[dict[str, ReasonCode]] = {
    r.code: r
    for r in (
        ReasonCode(
            code="not_found",
            default_message="The requested resource could not be found.",
            retryable=False,
            terminal_state="FAILED",
            typical_status=404,
        ),
        ReasonCode(
            code="permission_denied",
            default_message="You do not have permission to access that resource.",
            retryable=False,
            terminal_state="DENIED",
            typical_status=403,
        ),
        ReasonCode(
            code="not_authenticated",
            default_message="You must be signed in to do that.",
            retryable=False,
            terminal_state="DENIED",
            typical_status=401,
        ),
        ReasonCode(
            # parse / schema shape failure per contract §4 differentiator
            code="invalid_input",
            default_message="The request contained invalid data.",
            retryable=False,
            terminal_state="FAILED",
            typical_status=400,
        ),
        ReasonCode(
            # business-rule failure per contract §4 differentiator
            code="validation_error",
            default_message="The request failed validation.",
            retryable=False,
            terminal_state="FAILED",
            typical_status=400,
        ),
        ReasonCode(
            code="workspace_not_accessible",
            default_message="That workspace isn't accessible from your account.",
            retryable=False,
            terminal_state="DENIED",
            typical_status=403,
        ),
        ReasonCode(
            code="rate_limited",
            default_message="Too many requests. Please wait a moment and try again.",
            retryable=True,
            terminal_state="RATE_LIMITED",
            typical_status=429,
        ),
        ReasonCode(
            code="busy",
            default_message="The system is busy. Please try again shortly.",
            retryable=True,
            terminal_state="BUSY",
            typical_status=503,
        ),
        ReasonCode(
            code="upstream_provider_error",
            default_message="An upstream service is temporarily unavailable.",
            retryable=True,
            terminal_state="FAILED",
            typical_status=502,
        ),
        ReasonCode(
            code="upstream_provider_timeout",
            default_message="An upstream service did not respond in time.",
            retryable=True,
            terminal_state="FAILED",
            typical_status=504,
        ),
        ReasonCode(
            code="cost_cap_exceeded",
            default_message=(
                "This operation exceeds the configured cost cap for your workspace."
            ),
            retryable=False,
            terminal_state="DENIED",
            typical_status=402,
        ),
        ReasonCode(
            code="cancelled",
            default_message="The operation was cancelled.",
            retryable=False,
            terminal_state="CANCELLED",
            typical_status=200,
        ),
        ReasonCode(
            # fallback of last resort — contract §4 discipline
            code="internal_error",
            default_message="Something went wrong on our side. Support has been notified.",
            retryable=False,
            terminal_state="FAILED",
            typical_status=500,
        ),
        ReasonCode(
            code="unavailable",
            default_message="This feature is temporarily unavailable.",
            retryable=False,
            terminal_state="FAILED",
            typical_status=503,
        ),
        ReasonCode(
            code="tenant_boundary_violation",
            default_message="You do not have access to that resource.",
            retryable=False,
            terminal_state="DENIED",
            typical_status=403,
        ),
    )
}


def get_reason(code: str) -> ReasonCode:
    """Fetch a ReasonCode row.

    Raises KeyError if the code is not in the ratified enum. Callers
    MUST NOT emit unratified codes.
    """
    try:
        return REASON_CODES[code]
    except KeyError as exc:
        raise KeyError(
            f"Unknown reason_code {code!r}. "
            f"Valid codes: {sorted(REASON_CODES.keys())}"
        ) from exc


# DRF-standard exception → reason_code mapping (Rigby S2742 Stage 1 SIGN Q4).
# Keys are DRF exception class names (as strings, to avoid import cycles at
# module load); the handler looks them up by type name.
DRF_EXCEPTION_REASON_MAP: Final[dict[str, str]] = {
    "NotAuthenticated": "not_authenticated",
    "AuthenticationFailed": "not_authenticated",
    "PermissionDenied": "permission_denied",
    "NotFound": "not_found",
    "Http404": "not_found",
    "MethodNotAllowed": "invalid_input",
    "NotAcceptable": "invalid_input",
    "UnsupportedMediaType": "invalid_input",
    "Throttled": "rate_limited",
    "ValidationError": "validation_error",
    "ParseError": "invalid_input",
}
