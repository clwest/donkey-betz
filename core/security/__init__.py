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
    * from core.security import user_can_access_workspace
    * from core.security import can_read_deliverable, scope_queryset_deliverable
    * from core.security import can_read_chat_conversation, scope_queryset_chat_conversation
    * from core.security import can_read_initiative, scope_queryset_initiative
    * from core.security import can_read_agent_execution, scope_queryset_agent_execution
    * from core.security import can_read_document, scope_queryset_document

Object-authz predicates added per I-0302 Phase 2 (2026-07-10). Ratification:
docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md
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
from core.security.object_authz import (
    user_can_access_workspace,
    can_read_deliverable,
    scope_queryset_deliverable,
    can_read_chat_conversation,
    scope_queryset_chat_conversation,
    can_read_initiative,
    scope_queryset_initiative,
    can_read_agent_execution,
    scope_queryset_agent_execution,
    can_read_document,
    scope_queryset_document,
)

__all__ = [
    "REASON_CODES",
    "ReasonCode",
    "get_reason",
    "make_support_code",
    "build_user_facing_envelope",
    "build_operator_envelope",
    "user_can_access_workspace",
    "can_read_deliverable",
    "scope_queryset_deliverable",
    "can_read_chat_conversation",
    "scope_queryset_chat_conversation",
    "can_read_initiative",
    "scope_queryset_initiative",
    "can_read_agent_execution",
    "scope_queryset_agent_execution",
    "can_read_document",
    "scope_queryset_document",
]
