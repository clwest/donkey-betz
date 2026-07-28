"""
core.security.object_authz — per-model ownership predicates.

Ratified via I-0302 Phase 2 (2026-07-10). Design brief:
docs/research/implementation/tenant_boundary_lockdown/I-030202_predicate_module_design.md

**LEAF MODULE — do not import DRF, Celery, views, tasks here.**
Import contract per scoping §6.1: MAY import stdlib, Django models/settings,
core/security siblings. MUST NOT import anything that transitively pulls in
DRF/Celery/views/tasks — that would break Celery worker boot + create
request-time cascades.

Public API (per design brief §4):
- user_can_access_workspace(user, workspace_id) -> bool  (canonical primitive)
- can_read_deliverable / scope_queryset_deliverable       (workspace-scoped)
- can_read_chat_conversation / scope_queryset_chat_conversation (workspace-scoped w/ transitional user fallback)
- can_read_initiative / scope_queryset_initiative         (per-user)
- can_read_agent_execution / scope_queryset_agent_execution (per-user + superuser carve-out for null-user Celery runs)
- can_read_document / scope_queryset_document             (per-user)
- can_read_agent_memory / scope_queryset_agent_memory     (per-user-assigned-agent + superuser carve-out for system-agent memories — ADR-0008)

Predicates are pure + deterministic. No request context, no network, no
filesystem. Both request-time (DRF views) + async-time (Celery task boundaries
per I-0303) callers use these directly.

Q7 hybrid boundary (Chris D-verdict at I-0302 scoping ratification):
- Workspace-scoped: Deliverable, ChatConversation
- Per-user:        Initiative, AgentExecution, Document

Under single-user pre-prod operating context (2026-07-10+), Chris is the sole
user + superuser. Multi-tenant Phase 0 will expand user_can_access_workspace
to check WorkspaceMembership tables + workspace_id__in shapes remain compatible.
"""
from django.db.models import Q


# NOTE: `ProjectWorkspace` and other model classes are imported INSIDE function
# bodies below (not at module top) to avoid a settings-import cycle:
# core/settings.py imports from core.security → triggers this module → would
# trigger model imports → models_skin_layer calls get_user_model() at module
# load time → fails because Django apps aren't ready yet.
#
# Rigby SIGN F1 hybrid-import guidance defers to the strict leaf-module rule
# from scoping §6.1 for THIS specific module because of the settings.py
# consumer path.


# --------------------------------------------------------------------------
# Internal helper — authenticated-user guard
# --------------------------------------------------------------------------


def _authed(user) -> bool:
    """Return True iff user is present AND authenticated.

    Guards every predicate below against both `None` and Django's
    `AnonymousUser`. Duck-typed via ``getattr`` so this leaf module stays
    free of ``django.contrib.auth`` imports (import contract per scoping §6.1).

    Behavior:
    - ``None`` → False (unauthenticated request)
    - ``AnonymousUser`` (``is_authenticated == False``) → False
    - Any user object with ``is_authenticated == True`` → True

    Added 2026-07-10 via I-0302 Phase 3 Sub-phase A2 predicate hardening
    (Rigby SIGN Q4 fold). Prior contract only rejected ``None`` — passing
    ``AnonymousUser`` would raise ``ValueError`` inside ``.filter(owner=user)``
    because ``AnonymousUser`` has no primary key. This helper turns that
    500 into an empty result / False, preserving predicate-only-boundary
    semantics for the ``views_research_demo.py`` endpoints that A2 wires.
    """
    return getattr(user, "is_authenticated", False)


# --------------------------------------------------------------------------
# Canonical workspace-access primitive
# --------------------------------------------------------------------------


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
    - workspace_id is None
    - Workspace that does not exist
    - Workspace owned by a different user (unless requester is superuser)
    """
    if not _authed(user) or workspace_id is None:
        return False
    if getattr(user, "is_superuser", False):
        return True  # Superuser bypass — see docstring rationale
    from core.models_skin_layer import ProjectWorkspace  # local import: avoid settings cycle

    return ProjectWorkspace.objects.filter(id=workspace_id, user=user).exists()


# --------------------------------------------------------------------------
# Deliverable (Q7 workspace-scoped)
# --------------------------------------------------------------------------


def can_read_deliverable(user, deliverable) -> bool:
    """Deliverable is workspace-scoped: access iff user can access the workspace.

    Null-workspace policy (per Rigby SIGN F3 amendment):
    - Non-staff: deny (leakage protection)
    - Staff: allow (visibility for admin cleanup + migration audit trail)
    """
    if not _authed(user) or deliverable is None:
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
    if not _authed(user):
        return qs.none()
    from core.models_skin_layer import ProjectWorkspace  # local import: avoid settings cycle

    accessible_workspace_ids = ProjectWorkspace.objects.filter(user=user).values_list("id", flat=True)
    if getattr(user, "is_staff", False):
        return qs.filter(Q(workspace_id__in=accessible_workspace_ids) | Q(workspace_id__isnull=True))
    return qs.filter(workspace_id__in=accessible_workspace_ids)


# --------------------------------------------------------------------------
# ChatConversation (Q7 workspace-scoped with transitional user fallback)
# --------------------------------------------------------------------------


def can_read_chat_conversation(user, conv) -> bool:
    """ChatConversation is workspace-scoped. Transitional fallback: when workspace
    is null, gate on direct user ownership.

    IMPORTANT (per Rigby SIGN F3 amendment): this dual-authority model is
    TRANSITIONAL. Phase 0 multi-tenant should eliminate workspace-null
    conversations OR attach them deterministically. Do NOT let this fallback
    become permanent — it creates two truth-sources for the same access decision.

    Workspace-wins invariant: when both workspace_id and user_id are set,
    workspace membership decides. The user fallback is only consulted when
    workspace_id is null.
    """
    if not _authed(user) or conv is None:
        return False
    if conv.workspace_id is not None:
        return user_can_access_workspace(user, conv.workspace_id)
    # Transitional fallback (per SIGN F3): workspace-null conversations gate on direct user ownership
    return conv.user_id == user.id if conv.user_id else False


def scope_queryset_chat_conversation(user, qs):
    """Filter queryset to conversations user can access via workspace membership OR direct ownership.

    Transitional fallback caveat: see docstring on can_read_chat_conversation.
    """
    if not _authed(user):
        return qs.none()
    from core.models_skin_layer import ProjectWorkspace  # local import: avoid settings cycle

    accessible_workspace_ids = ProjectWorkspace.objects.filter(user=user).values_list("id", flat=True)
    return qs.filter(Q(workspace_id__in=accessible_workspace_ids) | Q(user=user))


# --------------------------------------------------------------------------
# Initiative (Q7 per-user)
# --------------------------------------------------------------------------


def can_read_initiative(user, initiative) -> bool:
    """Initiative is per-user: access iff initiative.owner == user.

    Nullable-owner defense-in-depth: null-owner rows are DENIED (deny-by-default).
    Phase 3 Sub-phase A1 migration (2026-07-10) backfilled all null-owner
    rows to canonical primary user + flipped owner to NOT NULL, eliminating
    this class of row at the DB layer. Predicate keeps the null-owner
    check as input-hardening against stale/adversarial instances.
    """
    if not _authed(user) or initiative is None:
        return False
    return initiative.owner_id == user.id if initiative.owner_id else False


def scope_queryset_initiative(user, qs):
    """Filter queryset to initiatives owned by user."""
    if not _authed(user):
        return qs.none()
    return qs.filter(owner=user)


# --------------------------------------------------------------------------
# AgentExecution (Q7 per-user + superuser carve-out for null-user Celery runs)
# --------------------------------------------------------------------------


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
    if not _authed(user) or execution is None:
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
    if not _authed(user):
        return qs.none()
    if getattr(user, "is_superuser", False):
        return qs.filter(Q(user=user) | Q(user__isnull=True))
    return qs.filter(user=user)


# --------------------------------------------------------------------------
# Document (Q7 per-user)
# --------------------------------------------------------------------------


def can_read_document(user, doc) -> bool:
    """Document is per-user: access iff doc.owner == user.

    Document.owner is NOT NULL (verified in I-0302 Phase 1 ledger §3). No
    nullable-owner fallback needed. Simplest predicate of the 5.
    """
    if not _authed(user) or doc is None:
        return False
    return doc.owner_id == user.id


def scope_queryset_document(user, qs):
    """Filter queryset to documents owned by user."""
    if not _authed(user):
        return qs.none()
    return qs.filter(owner=user)


# --------------------------------------------------------------------------
# AgentMemory (ADR-0008 — per-user-assigned-agent + null-assignment
# superuser carve-out for system-agent memories)
# --------------------------------------------------------------------------


def can_read_agent_memory(user, memory) -> bool:
    """AgentMemory is per-user-assigned-agent with SUPERUSER carve-out for
    system-agent memories.

    Ownership path: AgentMemory.agent (FK) → Agent.user_assignments (M2M
    through AgentAssignment) → User. System agents (agents with no
    user_assignments) are visible only to superusers — parallel to the
    AgentExecution.user=NULL carve-out per Rigby SIGN F4.

    Ratified by ADR-0008 (S3019, 2026-07-28) after S3017 shipped the
    `@token_auth_required` gate (A.1) that closed anon-reach but left the
    authenticated cross-user gap open.
    """
    if not _authed(user) or memory is None:
        return False
    agent = memory.agent
    if agent.user_assignments.filter(id=user.id).exists():
        return True
    # System-agent carve-out: superuser sees memories of agents with NO
    # user_assignments at all. This mirrors the queryset shape
    # `Q(agent__user_assignments__isnull=True)` in scope_queryset_agent_memory.
    # Do NOT broaden to "superuser sees everything" — that leaks cross-user
    # memories of assigned agents (ADR-0008 §3.1 explicit warning).
    if not agent.user_assignments.exists():
        return getattr(user, "is_superuser", False)
    return False


def scope_queryset_agent_memory(user, qs):
    """Filter queryset: user's assigned agents' memories + (if superuser)
    system-agent memories.

    IMPORTANT: superuser path is EXACTLY
    ``Q(agent__user_assignments=user) | Q(agent__user_assignments__isnull=True)``.
    Do NOT broaden this to "superuser sees everything"; superuser should see
    only (their assigned agents' memories) + (system/unassigned agents'
    memories) — the same defense-in-depth pattern as
    ``scope_queryset_agent_execution``. ``.distinct()`` guards against M2M
    row duplication if a user ever accrues multiple assignment rows to the
    same agent (future through-model may allow role or priority variants).
    """
    if not _authed(user):
        return qs.none()
    if getattr(user, "is_superuser", False):
        return qs.filter(
            Q(agent__user_assignments=user) | Q(agent__user_assignments__isnull=True)
        ).distinct()
    return qs.filter(agent__user_assignments=user).distinct()


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
    "can_read_agent_memory",
    "scope_queryset_agent_memory",
]
