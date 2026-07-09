"""
Workspace Resolver — get active workspace for a user.

Used by media creation paths (ImageHistory, VideoHistory, AudioHistory)
and DeliverableFactory to auto-assign workspace.

Usage:
    from core.services.workspace_resolver import get_active_workspace

    workspace = get_active_workspace(user)
    # Returns ProjectWorkspace instance or None
"""

import logging

logger = logging.getLogger(__name__)


# Session 2728 F-WS-4 — Batch B tool 5 close: narrow-except allowlist for
# `get_active_workspace`. Extends the S1234 D17-D21 discipline (already
# applied to `search_personal_memories`, `search_embeddings`, and several
# retrieval-adjacent helpers per `test_d20_views_rag_embeddings_narrow_
# except.py::test_all_four_allowlists_have_same_shape`) to the workspace
# resolver so environmental errors return `None` with an error log, but
# logic errors propagate to callers instead of silently degrading to
# "no workspace" (indistinguishable from "user has no workspace"). Same
# tuple shape as the D17-D21 invariant. Chris ratified at Batch B tool 5
# close.
_WORKSPACE_RESOLVER_ENV_ERRORS = (
    __import__('django.db.utils', fromlist=['DatabaseError']).DatabaseError,
    ConnectionError,
    OSError,
)


def get_active_workspace(user):
    """
    Get the user's active workspace, or their first workspace as fallback.
    Returns ProjectWorkspace instance or None.
    """
    if not user:
        return None
    try:
        from core.models_skin_layer import ProjectWorkspace
        # Active workspace first
        ws = ProjectWorkspace.objects.filter(
            user=user, is_active=True
        ).first()
        if ws:
            return ws
        # Fallback: any workspace owned by user
        return ProjectWorkspace.objects.filter(user=user).first()
    except _WORKSPACE_RESOLVER_ENV_ERRORS as _e:
        # Session 2728 F-WS-4 — narrow-except discipline. Pre-patch this
        # branch caught every Exception and returned None with a WARNING
        # log. That silent None is indistinguishable from "user has no
        # workspace," and downstream DeliverableFactory / media creation
        # paths route creates into orphan-Deliverable state without any
        # signal that a DB or environmental error caused the fallback.
        # Now only environmental errors (DB down, network unreachable,
        # OS I/O) return None with the error log; logic errors propagate
        # so future refactors that break the resolver are visible. Mirrors
        # F-RG-1 (search_embeddings) shipped in Batch B tool 1.
        logger.error(
            "workspace_resolver.get_active_workspace: environmental "
            "error: %s: %s",
            type(_e).__name__, _e,
        )
        return None


def get_active_workspace_id(user):
    """
    Get the user's active workspace ID as string.
    Returns str or None.
    """
    ws = get_active_workspace(user)
    return str(ws.id) if ws else None
