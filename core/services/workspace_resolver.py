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
    except Exception:
        return None


def get_active_workspace_id(user):
    """
    Get the user's active workspace ID as string.
    Returns str or None.
    """
    ws = get_active_workspace(user)
    return str(ws.id) if ws else None
