---
title: "I-0302 Phase 2 — Predicate Module Design Brief"
status: active
authority: phase-2-design-brief-signed
session_added: 2742
last_updated: 2026-07-10
arc_id: I-0302
arc_phase: Phase 2 (Predicate Module) — shipped locally; awaiting Chris ratification
parent_scoping_doc: docs/research/implementation/tenant_boundary_lockdown/I-0302_scoping.md
parent_scoping_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_scoping.md
phase_1_ledger: docs/research/implementation/tenant_boundary_lockdown/I-030201_model_audit_ledger.md
phase_1_ratification: docs/research/implementation/RATIFICATION_2026-07-10_i0302_phase1_ledger.md
head_at_design: 4712740f
rigby_design_sign_state: SIGN-PASS (after F1..F6 amendments applied)
rigby_implementation_sign_state: SIGN-PASS (after F3.2 AgentExecution superuser exactness test added)
implementation_files:
  - core/security/object_authz.py (new, ~250 lines)
  - core/security/__init__.py (extended — 11 new re-exports)
  - tests/security/test_object_authz_predicates.py (new, 60 tests, all pass locally in 196s)
  - .github/workflows/security-conformance.yml (extended — 6 new model-file triggers + workflow_dispatch)
implementation_notes:
  - Circular-import override — Rigby SIGN F1 hybrid-import guidance overridden for THIS module because core/settings.py imports from core.security. All model imports moved back inside function bodies with local-import comments. Documented in module-head docstring.
constraint: Phase 2 close awaits Chris ratification; Phase 3 opens only after Chris ratifies Phase 2 close
---

# I-0302 Phase 2 — Predicate Module Design Brief

Design contract for `core/security/object_authz.py` — the leaf module that Phase 3 enforcement + Phase 4 regression harness + I-0303 async-boundary enforcement all delegate to.

**Ratified inputs:**
- Scoping §6.1: leaf-module import constraint
- Scoping §6.2: predicate signature contract
- Phase 1 ledger §6: Chris Q7 hybrid boundary D-verdict per model
- Phase 1 ledger §7: nullable-owner policies per model
- Single-user pre-prod operating context (memory)

---

## §1. Module Structure

**File:** `core/security/object_authz.py`

**Contract:** leaf module per scoping §6.1
- MAY import: Django models, settings, `core/security/*` siblings, stdlib
- MUST NOT import: DRF, Celery, `core/views/*`, `core/tasks*`, anything that imports the above

**Import strategy (per Rigby SIGN F1 amendment):** hybrid.
- Top-level imports for stdlib + settings + `core/security/*` siblings + models that are proven safe (no view/task transitive imports)
- Local imports (inside function bodies) ONLY where necessary to break a known cycle, with a `# local import to avoid cycle with <module>` comment
- Module head docstring includes: "Do not import DRF, Celery, views, tasks here (leaf module)."

**Signature contract per scoping §6.2:**
- `can_read_<model>(user, obj) -> bool` — object-level read predicate
- `scope_queryset_<model>(user, qs) -> QuerySet` — queryset filter for list endpoints
- Optionally: `can_write_<model>(user, obj) -> bool` if write authz diverges from read (Phase 2 default: same as read)

**Purity contract:** predicates MUST be pure + deterministic. No request objects. No network. No filesystem.

---

## §2. Canonical Workspace Membership Primitive

**Verify-before-build finding:** `ProjectWorkspace` has a single `user` FK (owner). There is NO `WorkspaceMembership` or members M2M anywhere in the codebase. Existing `_get_workspace(workspace_id, user)` helper at `core/views_workspace_templates.py:27-32` already uses `ProjectWorkspace.objects.get(id=workspace_id, user=user)` — single-owner semantics.

**Phase 2 design:** extract to canonical primitive.

```python
def user_can_access_workspace(user, workspace_id) -> bool:
    """Return True iff `user` has access to the workspace identified by `workspace_id`.

    Under single-user pre-prod operating context (2026-07-10+), access = ownership:
    `ProjectWorkspace.user == user`. When Phase 0 multi-tenant opens, this
    expands to include membership tables (WorkspaceMembership, ProjectRole, etc.).

    Superuser override (per Rigby SIGN F2 amendment): superusers bypass ownership
    checks. Prevents lockouts during migrations / debugging. Documented explicitly
    so future contributors know this is intentional, not an oversight.

    Returns False for:
    - Unauthenticated user (user is None)
    - Workspace that does not exist
    - Workspace owned by a different user (unless requester is superuser)
    """
    if user is None or workspace_id is None:
        return False
    if getattr(user, "is_superuser", False):
        return True  # Superuser bypass — see docstring rationale
    return ProjectWorkspace.objects.filter(id=workspace_id, user=user).exists()
```

**On workspace `is_active` check (per Rigby SIGN F2 amendment):** `ProjectWorkspace` does NOT expose a canonical `is_active` field (verified against `core/models_skin_layer.py:31`). Skipped per "don't invent it" rule. If added later, revisit here.

**Follow-on:** existing `_get_workspace` helper migration to call `user_can_access_workspace` — Phase 3 or later follow-on.

---

## §3. Per-Model Predicates

### §3.1 Deliverable (Q7 workspace-scoped)

```python
def can_read_deliverable(user, deliverable) -> bool:
    """Deliverable is workspace-scoped: access iff user can access the workspace.

    Null-workspace policy (per Rigby SIGN F3 amendment):
    - Non-staff: deny (leakage protection)
    - Staff: allow (visibility for admin cleanup + migration audit trail)
    """
    if user is None or deliverable is None:
        return False
    if deliverable.workspace_id is None:
        # Staff-only visibility for workspace-orphaned rows
        return getattr(user, "is_staff", False)
    return user_can_access_workspace(user, deliverable.workspace_id)


def scope_queryset_deliverable(user, qs):
    """Filter queryset to deliverables user can access.

    - Non-staff: only deliverables in workspaces user owns
    - Staff: non-staff set + workspace-null rows (cleanup visibility)
    """
    if user is None:
        return qs.none()
    accessible_workspace_ids = ProjectWorkspace.objects.filter(user=user).values_list("id", flat=True)
    if getattr(user, "is_staff", False):
        from django.db.models import Q
        return qs.filter(Q(workspace_id__in=accessible_workspace_ids) | Q(workspace_id__isnull=True))
    return qs.filter(workspace_id__in=accessible_workspace_ids)
```

**Note on nullable workspace:** Phase 1 ledger §7 policy for Deliverable is "backfill user for 45 rows + migrate to NOT NULL" — plus workspace-null rows (per §4 informational: workspace FK is separately nullable). Under single-user pre-prod, Phase 3 pre-flight handles user-null via canonical primary-user migration; workspace-null rows get staff-only visibility (F3 amendment) to enable admin cleanup during the audit trail.

### §3.2 ChatConversation (Q7 workspace-scoped)

```python
def can_read_chat_conversation(user, conv) -> bool:
    """ChatConversation is workspace-scoped. Transitional fallback: when workspace
    is null, gate on direct user ownership.

    IMPORTANT (per Rigby SIGN F3 amendment): this dual-authority model is
    TRANSITIONAL. Phase 0 multi-tenant should eliminate workspace-null
    conversations OR attach them deterministically. Do NOT let this fallback
    become permanent — it creates two truth-sources for the same access decision.
    """
    if user is None or conv is None:
        return False
    if conv.workspace_id is not None:
        return user_can_access_workspace(user, conv.workspace_id)
    # Transitional fallback (per SIGN F3): workspace-null conversations gate on direct user ownership
    return conv.user_id == user.id if conv.user_id else False


def scope_queryset_chat_conversation(user, qs):
    """Filter queryset to conversations user can access via workspace membership OR direct ownership.

    Transitional fallback caveat: see docstring on can_read_chat_conversation.
    """
    if user is None:
        return qs.none()
    from django.db.models import Q
    accessible_workspace_ids = ProjectWorkspace.objects.filter(user=user).values_list("id", flat=True)
    return qs.filter(Q(workspace_id__in=accessible_workspace_ids) | Q(user=user))
```

**Note on ChatConversation dual-fallback (per Rigby SIGN F3 amendment):** the docstring on the model documents that `null=True` on user is INTENTIONAL for unlinked Discord users. Phase 1 ledger §7 minimal invariant: null-user rows are staff-only if they ever appear. **The workspace-OR-user dual authority is explicitly TRANSITIONAL.** When workspace and user both exist, workspace wins; test coverage in §5 pins this. Multi-tenant Phase 0 revisits + eliminates.

### §3.3 Initiative (Q7 per-user)

```python
def can_read_initiative(user, initiative) -> bool:
    """Initiative is per-user: access iff initiative.owner == user."""
    if user is None or initiative is None:
        return False
    return initiative.owner_id == user.id if initiative.owner_id else False


def scope_queryset_initiative(user, qs):
    """Filter queryset to initiatives owned by user."""
    if user is None:
        return qs.none()
    return qs.filter(owner=user)
```

**Note on null-owner enforcement:** Phase 1 ledger §7 Chris Option C — backfill all 62 null-owner rows to canonical primary user + migrate NOT NULL BEFORE Phase 3 enforcement lands. Predicate deny-by-default for null-owner is a defense-in-depth against migration-lag rows. After migration, `initiative.owner_id` is guaranteed non-null.

### §3.4 AgentExecution (Q7 per-user + staff carve-out)

**Canonical class:** `core.models_unified_system.AgentExecution` (line 882) — 1600 rows in local DB, 65% null-user (Session 642 intentional Celery nullability).

```python
def can_read_agent_execution(user, execution) -> bool:
    """AgentExecution is per-user with SUPERUSER carve-out for system-context runs.

    Session 642 nullability policy: user=NULL is intentional for Celery
    system-context runs (agent-triggered agents, beat tasks). SUPERUSER users
    (per Rigby SIGN F4 amendment) see all system-context runs for ops
    visibility; regular staff + non-staff see only their own runs.

    SECURITY NOTE (per Rigby SIGN F4): the null-user carve-out was originally
    proposed as is_staff. Changed to is_superuser to avoid overreach when
    staff role expands to non-admin operators in the future. If we later
    define a canonical "platform-ops" role, revisit here.
    """
    if user is None or execution is None:
        return False
    if execution.user_id is not None:
        return execution.user_id == user.id
    # user=NULL case: superuser-only visibility for system-context runs
    return getattr(user, "is_superuser", False)


def scope_queryset_agent_execution(user, qs):
    """Filter queryset: user's own executions + (if superuser) system-context runs.

    IMPORTANT (per Rigby SIGN F4 amendment): superuser path is EXACTLY
    Q(user=user) | Q(user__isnull=True). Do NOT broaden to "superuser sees
    everything regardless of user not null" — that would leak cross-user
    executions to the superuser.
    """
    if user is None:
        return qs.none()
    from django.db.models import Q
    if getattr(user, "is_superuser", False):
        return qs.filter(Q(user=user) | Q(user__isnull=True))
    return qs.filter(user=user)
```

**Staff carve-out (per Rigby SIGN F4 amendment):** changed from `is_staff` to `is_superuser` for the null-user carve-out. Under single-user pre-prod, Chris is superuser + only user, so functionally equivalent to "Chris sees everything." Multi-tenant Phase 0 stays safe — staff role can expand to non-admin operators without granting them global visibility to system-context runs.

### §3.5 Document (Q7 per-user)

```python
def can_read_document(user, doc) -> bool:
    """Document is per-user: access iff doc.owner == user."""
    if user is None or doc is None:
        return False
    return doc.owner_id == user.id


def scope_queryset_document(user, qs):
    """Filter queryset to documents owned by user."""
    if user is None:
        return qs.none()
    return qs.filter(owner=user)
```

**Note:** Document.owner is NOT NULL (verified in Phase 1). No fallback needed. Simplest predicate of the 5.

---

## §4. Module Exports

**`core/security/object_authz.py` public API:**

```python
__all__ = [
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
```

**`core/security/__init__.py` extension** (re-export the canonical primitive + the 10 per-model helpers):

```python
from core.security.object_authz import (
    user_can_access_workspace,
    can_read_deliverable, scope_queryset_deliverable,
    can_read_chat_conversation, scope_queryset_chat_conversation,
    can_read_initiative, scope_queryset_initiative,
    can_read_agent_execution, scope_queryset_agent_execution,
    can_read_document, scope_queryset_document,
)
```

---

## §5. Test Suite Design

**File:** `tests/security/test_object_authz_predicates.py`

**Coverage per predicate:**
1. User owns the row → `can_read` returns True; `scope_queryset` includes the row
2. Different user owns the row → `can_read` returns False; `scope_queryset` excludes the row
3. Null owner (where applicable) → predicate applies §3 nullable-owner rule
4. Unauthenticated user (user is None) → both predicates return False / .none()
5. Null obj → `can_read` returns False
6. `scope_queryset` with empty queryset returns empty queryset (invariant)
7. `scope_queryset` with mixed-ownership queryset returns only user's rows

**Special cases:**
- **AgentExecution superuser carve-out (per F4 amendment):** 4 cases — non-staff sees own only; regular staff sees own only; superuser sees own + null-user; user=None returns .none()
- **AgentExecution queryset invariant (per F4 amendment):** superuser scope MUST be exactly `Q(user=user) | Q(user__isnull=True)` — dedicated test asserts a foreign user_c's execution is NOT visible to superuser (only null-user rows + own rows)
- **ChatConversation dual-fallback (per F3 amendment):** 4 cases — workspace-scoped access; user-direct access when workspace is null; both null returns False; **workspace and user both present but disagree → workspace wins, user fallback ignored**
- **Deliverable null-workspace (per F3 amendment):** 3 cases — non-staff denied; staff allowed (cleanup visibility); non-null-workspace normal path

**Queryset invariants (per Rigby SIGN F5 amendment):**
- **Idempotence / monotonicity:** `scope(scope(qs)) == scope(qs)` — applying twice does not broaden. Tested for all 5 predicates.
- **None-safety:** `scope(user=None, qs)` returns `.none()`; never raises.
- **Mixed null + owned rows:** each queryset test seeds a mix of user_a-owned, user_b-owned, and (where applicable) null-owner rows, verifies only owner-scoped rows come back.

**Test fixtures:**
- Three real users (`user_a`, `user_b`, `user_c` — for the AgentExecution superuser invariant)
- One `staff_user` (is_staff=True, is_superuser=False)
- One `superuser` (is_superuser=True)
- One workspace per user (`ws_a` owned by user_a, `ws_b` owned by user_b, `ws_c` for user_c)
- Rows per model owned by each user, including edge cases (null owner where applicable + null workspace where applicable)

**Total tests:** ~65 tests (5 predicates × ~13 cases each on average, more for AgentExecution + ChatConversation given carve-outs).

**CI-blocking (per Rigby SIGN F6 amendment):** added to `.github/workflows/security-conformance.yml` via new `object_authz` job.

Trigger paths (expanded per F6):
- `core/security/**` (entire folder — authz semantics also change when helpers change)
- `core/models_deliverables.py`
- `core/models_document_registry.py`
- `core/models/conversations/**`
- `core/models_unified_system.py`
- `content/models.py`
- `core/models_skin_layer.py` (ProjectWorkspace lives here)
- `tests/security/test_object_authz_predicates.py`

Triggers: `pull_request` (merge gate) + `push` to main + `workflow_dispatch` (for manual runs during refactors).

Test selection: `pytest -q tests/security/test_object_authz_predicates.py` (narrow — keeps CI fast + deterministic).

---

## §6. Phase 2 Implementation Plan

1. Write `core/security/object_authz.py` per §2 + §3 + §4.
2. Extend `core/security/__init__.py` per §4 re-exports.
3. Write `tests/security/test_object_authz_predicates.py` per §5.
4. Run tests locally, iterate until all pass.
5. Extend `.github/workflows/security-conformance.yml` with `object_authz` job.
6. Route to Rigby for Phase 2 SIGN.
7. Chris ratifies Phase 2 close if design SIGN clean; Phase 3 opens.

**Non-goals for Phase 2:**
- Apply predicates to views/services (that's Phase 3)
- Migrate Initiative owner backfill (that's Phase 3 pre-flight)
- Migrate NOT NULL on Deliverable / AgentTaskExecution (that's Phase 3 pre-flight)
- Modify the `_get_workspace` helper in views_workspace_templates.py (that's follow-on)
- Cross-tenant regression harness (that's Phase 4)

---

## §7. Rigby Design SIGN Focus Areas

**F1 — Module structure + leaf-module constraint:** does `core/security/object_authz.py` correctly slot into the I-0301 substrate without violating the leaf-module rule?

**F2 — `user_can_access_workspace` primitive:** is single-owner semantics the right shape for pre-prod single-user? Should the primitive check anything beyond `ProjectWorkspace.user`?

**F3 — Per-model predicate correctness:** does each predicate match the Phase 1 ledger §6 Q7 boundary + §7 nullable-owner policy?

**F4 — AgentExecution staff carve-out shape:** approve `is_staff` as the gate for null-user rows? Any bias with `user__isnull=True` scoping in `scope_queryset_agent_execution`?

**F5 — Test suite coverage:** is ~50 tests + 7 case types per predicate adequate? Any missing edge case?

**F6 — CI wiring:** should `object_authz` be its own job, or fold into existing conformance job? Which files should trigger it?

---

## §8. Rigby SIGN Cycle + Chris Ratification Contract

This design brief is `authority: phase-2-design-brief` until Rigby signs. Ratification signals for Phase 2 close (after design SIGN + implementation):

- Rigby design SIGN on this brief with any material amendment applied
- Implementation matches the SIGN'd design
- ~50 tests all pass locally
- Rigby implementation SIGN on the shipped module + test suite
- Chris ratifies Phase 2 close (transitions this doc from `authority: phase-2-design-brief` → `authority: phase-2-design-brief-ratified` + phase status flips to CLOSED)
- Phase 3 (per-model enforcement application) authorized to open

---

**End of I-0302 Phase 2 Predicate Module Design Brief. Ready for Rigby design SIGN.**
