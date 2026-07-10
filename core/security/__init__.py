"""
core.security — Real User Readiness safety substrate.

Implements the ratified Failure-Data Safety Contract at
docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
(RATIFICATION_2026-07-10_i0301_safety_contract.md).

Public API:
    * from core.security import build_user_facing_envelope
    * from core.security import build_operator_envelope
    * from core.security import get_reason
    * from core.security import make_support_code
    * from core.security.error_envelope import drf_exception_handler
    * from core.security.error_envelope import RURErrorEnvelopeMiddleware
"""
from core.security.reason_codes import (
    REASON_CODES,
    ReasonCode,
    get_reason,
)
from core.security.support_code import make_support_code
from core.security.error_envelope import (
    build_user_facing_envelope,
    build_operator_envelope,
)

__all__ = [
    "REASON_CODES",
    "ReasonCode",
    "get_reason",
    "make_support_code",
    "build_user_facing_envelope",
    "build_operator_envelope",
]
