---
title: "ADR-0008 — AgentMemory scope predicate (A.2 cross-user isolation)"
adr_id: ADR-0008
slug: agent-memory-scope-predicate
status: accepted
authority: design-decision
proposed: 2026-07-28
ratified: 2026-07-28
ratifier: chris
chris_ratification: "yes ratify and proceed" 2026-07-28 — after Rigby T0 SIGN (Layer 1 AGREE + Layer 2 REVISE-with-3-changes-applied) and joint Claude+Rigby recommendation per feedback_claude_rigby_agree_first_chris_yes_no. Three-part plain-English framing routed per PLAYBOOK-7.7.3.
supersedes: (none)
superseded_by: (none)
refines: (none — new predicate on core/security/object_authz.py surface)
intake_id: S3017 Fold C `future arc` → S3019 Option A ratified at S3018 close
arc_ref: (none — orthogonal to Cycle-0/1)
source_refs:
  - docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md §F-2 (original F-2 finding + A.1 vs A.2 alternatives)
  - docs/handoffs/SESSION_3017_MEMORY_PALACE_AUTH_GATE.md §Forward carries Fold C (A.2 carry)
  - docs/handoffs/SESSION_3018_PUBLIC_PATHS_GATE_INVARIANT.md §Forward carries (A.2 recommended for S3019)
  - core/views_memory_palace.py:98-176 (`get_memory_detail` — S3017-gated but row-unscoped)
  - core/views_memory_palace.py:518-560 (`get_memory_connections` — S3017-gated but row-unscoped)
  - core/views_memory_palace.py:624-646 (`delete_memory` — S3017-gated but row-unscoped)
  - core/security/object_authz.py:79-107 (`user_can_access_workspace` canonical primitive)
  - core/security/object_authz.py:232-244 (`scope_queryset_agent_execution` — null-user superuser carve-out pattern to mirror)
  - core/models_unified_system.py:455-533 (Agent model, `user_assignments` M2M via AgentAssignment)
  - core/models_unified_system.py:10981+ (AgentMemory model — no direct user FK)
reversibility: 4
  # Adds one new predicate function to object_authz + wires it into 3 views.
  # Rollback: revert PR — the S3017 `@token_auth_required` decorator remains
  # in place; anon-reach is still closed. What we lose on rollback is only
  # the authenticated-cross-user protection (returning to S3017 state).
sign_cycle_1: (pending — dispatched to Rigby T1 pre-merge per PLAYBOOK-7.7.2)
sign_cycle_1_pin: pa-3dadd8178bb342b5
companion_docs:
  - docs/handoffs/SESSION_3017_MEMORY_PALACE_AUTH_GATE.md
  - docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md
owner: claude (S3019 v1 draft)
---

# ADR-0008 — AgentMemory scope predicate (A.2 cross-user isolation)

## 1. Status

**Accepted** — Chris ratified 2026-07-28 via "yes ratify and proceed" following joint Claude+Rigby recommendation per `feedback_claude_rigby_agree_first_chris_yes_no`. Rigby T0 SIGN AGREE'd Layer 1 (security invariant) + REVISE'd Layer 2 (implementation) with 3 changes (data-state numbers, docstring wording, test-helper §3.4 addition) — all applied pre-ratification.

## 2. Context

### 2.1 The S3017 gap

S3017 PR #3719 closed F-2 (anon-readable memory row + silent `access_count` bump) and F-3 (anon-DELETE-any-row) by decorating `get_memory_detail`, `get_memory_connections`, and `delete_memory` with `@token_auth_required`. Anon reachability is closed.

Not closed: **authenticated cross-user access**. Any authenticated user with a valid `memory_id` UUID can still read or delete any memory row belonging to any other user — the view body's `AgentMemory.objects.defer('embedding').get(id=memory_id)` has no ownership filter.

Under the current single-user pre-prod context (Chris sole user), this is not exploitable. But the predicate substrate must ship before multi-tenant Phase 0 opens.

### 2.2 The ownership path challenge

`AgentMemory` has no direct user FK. The scoping path is:

    AgentMemory.agent (FK) → Agent.user_assignments (M2M through AgentAssignment) → User

But **the `AgentAssignment` table is empty at HEAD** (`d1cb0d9a7`): 0 rows across 97 Agents and 984 AgentMemory records (ORM-confirmed locally 2026-07-28; Rigby T0 tool-allowlist could not verify AgentAssignment directly and confirmed 97 Agents / 981 AgentMemory via `db_health_tool.verify_table`, which lags slightly behind live ORM). Under strict M2M scoping, non-superuser regular users would see zero memories — even for agents they'd conceptually "own" in a future multi-tenant world.

Two additional subtleties:
1. **System agents.** Agents run in system context (Celery beat tasks, autonomous reasoning) with no user assignment. Their memories are non-user-specific. Parallels the `AgentExecution.user=NULL` superuser carve-out at `object_authz.py:229`.
2. **Superuser visibility.** Same rationale as `scope_queryset_agent_execution` — Chris (sole superuser) sees all rows for ops visibility; regular users (future multi-tenant) see only their assigned agents' memories.

### 2.3 Options considered

- **Option 1 — Predicate mirroring `scope_queryset_agent_execution`.** New `scope_queryset_agent_memory(user, qs)` with superuser sees `agent.user_assignments=user OR agent__user_assignments__isnull=True` (own + system); regular user sees `agent__user_assignments=user` only. Under current data state (empty M2M) regular users see nothing; superuser sees everything. **Recommended.**
- **Option 2 — Add `AgentMemory.owner` FK.** Direct scoping at row level, no M2M traversal. Requires migration + backfill logic (which user owns each of the 983 existing rows?). Under single-user context, backfill = "Chris owns everything" is trivial, but the model change is heavier than necessary.
- **Option 3 — Skip the predicate; extend `@token_auth_required` to `@ownership_required(model=AgentMemory)`.** Decorator-level ownership check. Couples auth + ownership at the decorator surface, inconsistent with the 5 existing scope predicates.

## 3. Decision

Adopt **Option 1** — `scope_queryset_agent_memory(user, qs)` on `core/security/object_authz.py`, mirroring the `scope_queryset_agent_execution` shape.

### 3.1 Predicate signature

```python
def can_read_agent_memory(user, memory) -> bool:
    """AgentMemory is per-user-assigned-agent with SUPERUSER carve-out for system-agent memories.

    System agents (agents with no user_assignments) are visible only to
    superusers — parallel to the AgentExecution.user=NULL carve-out per Rigby SIGN F4.
    """
    if not _authed(user) or memory is None:
        return False
    agent = memory.agent
    if agent.user_assignments.filter(id=user.id).exists():
        return True
    # No assignment path — superuser-only visibility for system-agent memories.
    return getattr(user, "is_superuser", False)


def scope_queryset_agent_memory(user, qs):
    """Filter queryset: user's assigned agents' memories + (if superuser) system-agent memories.

    IMPORTANT: superuser path is EXACTLY
    `Q(agent__user_assignments=user) | Q(agent__user_assignments__isnull=True)`.
    Do NOT broaden this to "superuser sees everything"; superuser should see
    only (their assigned agents' memories) + (system/unassigned agents'
    memories) — the same defense-in-depth pattern as
    `scope_queryset_agent_execution`. `.distinct()` guards against M2M row
    duplication if a user ever accrues multiple assignment rows to the same
    agent (future through-model may allow role or priority variants).
    """
    if not _authed(user):
        return qs.none()
    if getattr(user, "is_superuser", False):
        return qs.filter(
            Q(agent__user_assignments=user) | Q(agent__user_assignments__isnull=True)
        ).distinct()
    return qs.filter(agent__user_assignments=user).distinct()
```

### 3.2 View wiring

Three views under `/api/memory-palace/memory/<uuid>/*` currently perform an unscoped `.get(id=memory_id)`. Wire the predicate:

- `get_memory_detail` (`core/views_memory_palace.py:107`):
  ```python
  memory = scope_queryset_agent_memory(
      request.user, AgentMemory.objects.defer('embedding')
  ).get(id=memory_id)
  ```
- `get_memory_connections` (`core/views_memory_palace.py:527`): same pattern.
- `delete_memory` (`core/views_memory_palace.py:633`): same pattern.

Post-fix, any authenticated user who requests a memory belonging to an agent they're not assigned to gets `AgentMemory.DoesNotExist` (view's existing `except` returns 404 `Memory not found`). No new envelope shape needed.

### 3.3 Test coverage

Extend `core/tests/test_s3017_memory_detail_auth_gate.py` (or a new S3019 file) with:

1. Superuser sees any memory (baseline).
2. Regular user with assignment to memory's agent sees the memory.
3. Regular user WITHOUT assignment to memory's agent gets 404.
4. Regular user cannot DELETE another user's agent's memory (row survives).
5. Superuser can DELETE a system-agent memory (no user_assignments).

### 3.4 Test helper (Rigby T0 zoom-out §a)

Because current `AgentAssignment` = 0 and regular users see nothing under strict scoping, tests exercising the regular-user positive path need an explicit assignment step. Ship a small helper alongside the implementation:

```python
# core/tests/helpers/agent_assignment.py
def assign_agent_to_user(agent, user, *, is_active=True, priority=0):
    from core.models_unified_system import AgentAssignment
    return AgentAssignment.objects.create(
        agent=agent, user=user, is_active=is_active, priority=priority,
    )
```

Prevents "mysterious empty-list" test failures downstream and documents the intended path for future multi-tenant test fixtures.

## 4. Consequences

### 4.1 What changes

- `core/security/object_authz.py` gains one new predicate + one canonical-primitive method (`can_read_agent_memory`).
- Three views drop the unscoped `.get()` in favor of `scope_queryset_agent_memory(user, ...).get(id=...)`.
- The 5-predicate surface documented in the module docstring becomes 6.
- The S3018 invariant test snapshot remains unchanged (views were already `decorator:token_required`; predicate call is inside view body, invisible to the invariant).

### 4.2 What DOESN'T change under current data state

- Chris (sole superuser) continues to see all memories via the superuser carve-out.
- No user-facing behavior change today.

### 4.3 What activates when multi-tenant Phase 0 opens

- Regular users see only memories of agents they're assigned to via `AgentAssignment`.
- Cross-user memory reads / DELETEs return 404.
- System-agent memories remain superuser-only.

### 4.4 Reversibility

Score 4. Rollback = revert the PR. The S3017 `@token_auth_required` decorator remains in place; anon-reach stays closed. Only the authenticated-cross-user protection returns to the S3017 state.

## 5. Alternatives rejected

### 5.1 Option 2 (direct `AgentMemory.owner` FK)

Rejected. Requires migration + backfill script. Under single-user context backfill is trivial ("Chris owns everything"), but the model change is disproportionate to the substrate need. Option 1 gets the same scoping semantics via M2M traversal without touching the schema.

### 5.2 Option 3 (`@ownership_required(model=...)` decorator)

Rejected. Couples auth (decorator layer) with ownership (predicate layer), inconsistent with the existing 5 scope predicates. Ownership decisions should live where all other ownership decisions live — `object_authz.py`.

### 5.3 Skipping the predicate entirely and relying on the S3017 decorator + future superuser lockdown

Rejected. Leaves an active authenticated-cross-user gap. The gap is not currently exploitable (single-user context) but the invariant substrate should be in place before it becomes exploitable.

## 6. Open questions

None substantial. Rigby T1 SIGN (pre-merge) will pressure-test the `.distinct()` guard + system-agent superuser carve-out semantics + edge cases where a user is assigned to Agent A but requests memory from Agent B under the same superuser account.

## 7. Companion sources

- `docs/audits/PUBLIC_PATHS_BARE_PREFIX_AUDIT_S3016.md` §F-2 — original A.1 vs A.2 dichotomy.
- `docs/handoffs/SESSION_3017_MEMORY_PALACE_AUTH_GATE.md` — S3017 close referencing A.2 as forward-carry.
- `docs/handoffs/SESSION_3018_PUBLIC_PATHS_GATE_INVARIANT.md` — S3018 close referencing A.2 as S3019 Option A.

---

*Ratification workflow: draft → Rigby T0 SIGN on ADR shape → Chris ratifies → implementation PR under adr_ref: ADR-0008 → Rigby T1 SIGN on code + tests → merge → recycle.*
