"""S3019 (ADR-0008 §3.4): AgentAssignment test helper.

Under current data state (0 rows in AgentAssignment at ADR ratification
time), regular-user positive-path tests against `AgentMemory`-scoped
endpoints need an explicit assignment step or they hit `.none()` and
fail with "mysterious empty list" semantics. This helper documents the
intended path for future multi-tenant test fixtures.

Rigby T0 SIGN §a — added same-PR as ADR-0008 implementation.
"""
from __future__ import annotations

from core.models_unified_system import AgentAssignment


def assign_agent_to_user(agent, user, *, is_active: bool = True, priority: int = 0):
    """Create an AgentAssignment linking `agent` to `user`.

    Returns the created row for chaining. Idempotent callers should use
    `get_or_create` themselves; this helper always creates.
    """
    return AgentAssignment.objects.create(
        agent=agent,
        user=user,
        is_active=is_active,
        priority=priority,
    )
