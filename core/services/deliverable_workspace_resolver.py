"""
Canonical workspace resolution for all work objects.

Every work object (deliverable, initiative, opportunity, task, alert) should
use resolve_workspace() or resolve_workspace_context() to determine which
workspace it belongs to. This is the single source of truth for workspace
resolution logic across the entire platform.

Resolution priority:
1. Explicit workspace_id (from context, kwargs, or caller)
2. Conversation-bound workspace (ChatConversation.workspace FK)
3. Initiative's target_workspace
4. User's active workspace (server-side, user-bound)
5. Global active workspace fallback (for system/autonomous operations)
6. None (only if force_ephemeral or no workspace exists)
"""
import logging

logger = logging.getLogger(__name__)

# Valid resolution sources for observability
RESOLUTION_SOURCES = (
    'explicit',
    'conversation',
    'initiative',
    'user_active',
    'global_active',
    'none',
)


def resolve_workspace(workspace_id=None, initiative=None, fallback_to_active=True):
    """
    Simple resolver for backward compatibility.
    Prefer resolve_workspace_context() for new code.

    Returns:
        (workspace, is_saved) tuple
    """
    workspace, is_saved, _ = resolve_workspace_context(
        explicit_workspace_id=workspace_id,
        initiative=initiative,
        fallback_to_active=fallback_to_active,
    )
    return workspace, is_saved


def resolve_workspace_context(
    *,
    user=None,
    explicit_workspace_id=None,
    conversation_id=None,
    initiative=None,
    initiative_id=None,
    opportunity=None,
    fallback_to_active=True,
):
    """
    Full canonical workspace resolver with conversation + user support.

    Args:
        user: User model instance (for user-bound active workspace)
        explicit_workspace_id: Explicit workspace UUID string or model instance
        conversation_id: PA conversation ID (e.g. 'pa-abc123') to look up bound workspace
        initiative: Initiative model instance
        initiative_id: Initiative UUID (will be looked up if initiative not provided)
        opportunity: Opportunity model instance (will check workspace if present)
        fallback_to_active: Whether to fall back to active workspace

    Returns:
        (workspace, is_saved, source) tuple — workspace instance or None,
        whether to mark as saved, and resolution source string.
    """
    workspace = None
    source = 'none'

    # Priority 1: Explicit workspace_id
    if explicit_workspace_id:
        try:
            from core.models_skin_layer import ProjectWorkspace
            if hasattr(explicit_workspace_id, 'pk'):
                workspace = explicit_workspace_id
            else:
                workspace = ProjectWorkspace.objects.filter(id=explicit_workspace_id).first()
            if workspace:
                source = 'explicit'
        except Exception as e:
            logger.warning(f"[workspace-resolver] Failed to resolve explicit workspace_id={explicit_workspace_id}: {e}")

    # Priority 2: Conversation-bound workspace
    if not workspace and conversation_id:
        try:
            from core.models.conversations.models import ChatConversation
            conv = ChatConversation.objects.filter(
                conversation_id=conversation_id,
                workspace__isnull=False,
            ).select_related('workspace').first()
            if conv and conv.workspace:
                workspace = conv.workspace
                source = 'conversation'
        except Exception as e:
            logger.debug(f"[workspace-resolver] Conversation workspace lookup failed: {e}")

    # Priority 3: Initiative's target workspace
    if not workspace and (initiative or initiative_id):
        try:
            if not initiative and initiative_id:
                from core.models_document_registry import Initiative
                initiative = Initiative.objects.filter(id=initiative_id).first()
            if initiative:
                ws = getattr(initiative, 'target_workspace', None)
                if ws:
                    workspace = ws
                    source = 'initiative'
        except Exception as e:
            logger.debug(f"[workspace-resolver] Initiative workspace lookup failed: {e}")

    # Priority 4: Opportunity's workspace (if model has it)
    if not workspace and opportunity:
        try:
            ws = getattr(opportunity, 'workspace', None)
            if ws:
                workspace = ws
                source = 'opportunity'
        except Exception as e:
            logger.warning(
                "[workspace-resolver] opportunity.workspace lookup failed "
                "(%s: %s)", type(e).__name__, e,
            )

    # Priority 5: User's active workspace (server-side, user-bound)
    if not workspace and user and fallback_to_active:
        try:
            from core.services.workspace_manager import WorkspaceManager
            wm = WorkspaceManager(user=user)
            workspace = wm.get_active_workspace()
            if workspace:
                source = 'user_active'
        except Exception as e:
            logger.warning(
                "[workspace-resolver] user active workspace lookup failed "
                "(%s: %s)", type(e).__name__, e,
            )

    # Priority 6: Global active workspace fallback (for system operations without user)
    if not workspace and fallback_to_active:
        try:
            from core.models_skin_layer import ProjectWorkspace
            workspace = ProjectWorkspace.objects.filter(is_active=True).order_by('-total_operations', '-created_at').first()
            if workspace:
                source = 'global_active'
        except Exception as e:
            logger.warning(
                "[workspace-resolver] global active workspace lookup failed "
                "(%s: %s)", type(e).__name__, e,
            )

    is_saved = bool(workspace)

    if workspace:
        logger.debug(f"[workspace-resolver] Resolved: {workspace.name} (source={source})")
    else:
        # Session 1103c: upgrade from debug to warning so orphan
        # deliverable creations are visible. Was previously hidden at
        # debug level, which meant orphans slipped in unnoticed unless
        # DEBUG logging was on.
        logger.warning(
            "[workspace-resolver] No workspace resolved — caller will "
            "create UNSCOPED deliverable. priorities: conversation=%s, "
            "initiative=%s, opportunity=%s, user=%s, fallback_to_active=%s",
            bool(conversation_id), bool(initiative or initiative_id),
            bool(opportunity), bool(user), fallback_to_active,
        )

    return workspace, is_saved, source
