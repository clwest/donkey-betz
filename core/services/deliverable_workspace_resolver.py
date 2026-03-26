"""
Centralized workspace resolution for deliverable creation.

All deliverable creation paths should use resolve_workspace() to determine
which workspace a deliverable belongs to. This prevents drift and ensures
consistent behavior across agents, pipelines, extractors, and tasks.

Resolution priority:
1. Explicit workspace_id (from context, kwargs, or caller)
2. Initiative's target_workspace (when initiative is available)
3. Active workspace fallback (ProjectWorkspace.is_active=True)
4. None (preserves current behavior for ephemeral outputs)
"""
import logging

logger = logging.getLogger(__name__)


def resolve_workspace(workspace_id=None, initiative=None, fallback_to_active=True):
    """
    Resolve the workspace for a deliverable.

    Args:
        workspace_id: Explicit workspace UUID string or object
        initiative: Initiative model instance (will check target_workspace)
        fallback_to_active: Whether to fall back to the active workspace

    Returns:
        (workspace, is_saved) tuple — workspace instance or None, and whether
        the deliverable should be marked as saved.
    """
    workspace = None

    # Priority 1: Explicit workspace_id
    if workspace_id:
        try:
            from core.models_skin_layer import ProjectWorkspace
            if hasattr(workspace_id, 'pk'):
                workspace = workspace_id  # Already a model instance
            else:
                workspace = ProjectWorkspace.objects.filter(id=workspace_id).first()
        except Exception as e:
            logger.warning(f"Failed to resolve workspace_id={workspace_id}: {e}")

    # Priority 2: Initiative's target workspace
    if not workspace and initiative:
        try:
            ws = getattr(initiative, 'target_workspace', None)
            if ws:
                workspace = ws
        except Exception as e:
            logger.warning(f"Failed to resolve initiative workspace: {e}")

    # Priority 3: Active workspace fallback
    if not workspace and fallback_to_active:
        try:
            from core.models_skin_layer import ProjectWorkspace
            workspace = ProjectWorkspace.objects.filter(is_active=True).first()
        except Exception:
            pass

    is_saved = bool(workspace)

    if workspace:
        logger.debug(f"Resolved workspace: {workspace.name} (id={workspace.id})")

    return workspace, is_saved
