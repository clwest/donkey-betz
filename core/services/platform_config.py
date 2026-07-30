"""
Platform Configuration Service
Session 910: Centralized configuration for primary workspace and user.

This module provides a single source of truth for:
1. The primary workspace (where all operations go)
2. The primary user (owner of the primary workspace)

These values can be configured via:
1. Django settings (PRIMARY_WORKSPACE_NAME, PRIMARY_USERNAME)
2. Environment variables (DONKEY_BETZ_PRIMARY_WORKSPACE, DONKEY_BETZ_PRIMARY_USER)
3. Automatic detection (workspace with most operations)

Usage:
    from core.services.platform_config import get_primary_workspace, get_primary_user

    workspace = get_primary_workspace()
    user = get_primary_user()
"""

import logging
from functools import lru_cache
from typing import Optional, Tuple, TYPE_CHECKING

from django.conf import settings
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from core.models_skin_layer import ProjectWorkspace

logger = logging.getLogger(__name__)

# Cache timeout (in seconds) - clear cache periodically for fresh data
_CACHE_TIMEOUT = 300  # 5 minutes


class PrimaryWorkspaceUnavailable(Exception):
    """Raised when the primary workspace is configured but cannot be resolved.

    Distinct from "no primary workspace configured" — that case still returns
    ``None`` from :func:`get_primary_workspace`. This exception fires only when
    a workspace id is present in the cache but the underlying row cannot be
    fetched (invalid id, DB error, workspace deleted out from under us).

    Callers who want graceful degradation should wrap in::

        try:
            workspace = get_primary_workspace()
        except PrimaryWorkspaceUnavailable:
            workspace = None  # degrade / fall through per site semantics

    Callers who want the platform to fail loudly on misconfiguration should
    let it propagate. Per S3042/T1 v1 §5 (Spine Contract v1 §3 Corollary),
    silent-None on config error was the DEFECT this contract closes.
    """


def _get_config_value(setting_name: str, env_name: str, default: str) -> str:
    """
    Get a configuration value from settings or environment.

    Priority:
    1. Django settings
    2. Environment variable
    3. Default value
    """
    import os

    # Try Django settings first
    value = getattr(settings, setting_name, None)
    if value:
        return value

    # Try environment variable
    value = os.environ.get(env_name)
    if value:
        return value

    return default


def get_primary_workspace_name() -> str:
    """
    Get the name pattern for the primary workspace.

    Returns:
        String pattern to match workspace name (case-insensitive)
    """
    return _get_config_value(
        'PRIMARY_WORKSPACE_NAME',
        'DONKEY_BETZ_PRIMARY_WORKSPACE',
        'donkey betz'  # Default - can be changed via settings/env
    )


def get_primary_username() -> str:
    """
    Get the username for the primary user.

    Returns:
        Username string
    """
    return _get_config_value(
        'PRIMARY_USERNAME',
        'DONKEY_BETZ_PRIMARY_USER',
        'Donkeyking'  # Default - can be changed via settings/env
    )


@lru_cache(maxsize=1)
def _cached_primary_workspace_id() -> Optional[int]:
    """
    Cached lookup for primary workspace ID.
    Uses lru_cache for performance, call clear_config_cache() to refresh.
    """
    try:
        from core.models_skin_layer import ProjectWorkspace

        workspace_name = get_primary_workspace_name()

        # Look for workspace matching the configured name
        workspace = ProjectWorkspace.objects.filter(
            name__icontains=workspace_name,
            is_active=True
        ).order_by('-total_operations').first()

        if workspace:
            logger.debug(
                f"[Platform Config] Found primary workspace: {workspace.name} "
                f"(id={workspace.id}, ops={workspace.total_operations})"
            )
            return workspace.id

        # Fallback: get the workspace with most operations
        workspace = ProjectWorkspace.objects.filter(
            is_active=True
        ).order_by('-total_operations').first()

        if workspace:
            logger.warning(
                f"[Platform Config] Primary workspace '{workspace_name}' not found, "
                f"using fallback: {workspace.name}"
            )
            return workspace.id

        logger.warning("[Platform Config] No active workspace found")
        return None

    except Exception as e:
        logger.error(f"[Platform Config] Error getting primary workspace: {e}")
        return None


@lru_cache(maxsize=1)
def _cached_primary_user_id() -> Optional[int]:
    """
    Cached lookup for primary user ID.
    Uses lru_cache for performance, call clear_config_cache() to refresh.
    """
    try:
        User = get_user_model()

        username = get_primary_username()

        # Look for user matching the configured username (case-insensitive)
        user = User.objects.filter(username__iexact=username).first()

        if user:
            logger.debug(f"[Platform Config] Found primary user: {user.username} (id={user.id})")
            return user.id

        # Fallback: get the superuser
        user = User.objects.filter(is_superuser=True).first()

        if user:
            logger.warning(
                f"[Platform Config] Primary user '{username}' not found, "
                f"using fallback superuser: {user.username}"
            )
            return user.id

        logger.warning("[Platform Config] No primary user found")
        return None

    except Exception as e:
        logger.error(f"[Platform Config] Error getting primary user: {e}")
        return None


def get_primary_workspace() -> Optional['ProjectWorkspace']:
    """
    Get the primary workspace for all platform operations.

    This is THE single source of truth for which workspace to use.
    All components should call this instead of hardcoding workspace names.

    Returns:
        ProjectWorkspace instance, or None when no primary workspace is
        configured (no PRIMARY_WORKSPACE_NAME / env override / auto-detected
        candidate). This is the "unconfigured" case and is not an error.

    Raises:
        PrimaryWorkspaceUnavailable: when a workspace id resolves from
        configuration but the underlying row cannot be fetched — invalid id,
        DB error, workspace deleted. This is a MISCONFIGURATION signal and
        callers should either fail loudly or wrap in
        ``try/except PrimaryWorkspaceUnavailable`` for graceful degradation.
    """
    workspace_id = _cached_primary_workspace_id()
    if not workspace_id:
        return None

    try:
        from core.models_skin_layer import ProjectWorkspace
        return ProjectWorkspace.objects.get(id=workspace_id)
    except Exception as e:
        logger.error(
            "[Platform Config] Primary workspace id=%s configured but "
            "cannot be resolved: %s: %s",
            workspace_id, type(e).__name__, e,
        )
        raise PrimaryWorkspaceUnavailable(
            f"Primary workspace id={workspace_id} configured but cannot be "
            f"resolved: {type(e).__name__}: {e}"
        ) from e


def get_primary_user():
    """
    Get the primary user for platform operations.

    This is THE single source of truth for which user to use.
    All components should call this instead of hardcoding usernames.

    Returns:
        User instance, or None if not found
    """
    user_id = _cached_primary_user_id()
    if not user_id:
        return None

    try:
        User = get_user_model()
        return User.objects.get(id=user_id)
    except Exception as e:
        logger.error(f"[Platform Config] Error fetching user: {e}")
        return None


def get_primary_workspace_and_user() -> Tuple[Optional[object], Optional['ProjectWorkspace']]:
    """
    Get both primary user and workspace in a single call.

    Returns:
        Tuple of (user, workspace)
    """
    return get_primary_user(), get_primary_workspace()


def clear_config_cache():
    """
    Clear the configuration cache.

    Call this after:
    - Changing the primary workspace or user
    - Updating settings/environment variables
    - Database migrations
    """
    _cached_primary_workspace_id.cache_clear()
    _cached_primary_user_id.cache_clear()
    logger.info("[Platform Config] Cache cleared")


def set_primary_workspace(workspace_name: str):
    """
    Update the primary workspace configuration.

    Note: This updates the runtime setting but does NOT persist.
    For persistent changes, update Django settings or environment variables.

    Args:
        workspace_name: New workspace name pattern to match
    """
    # We can't easily update settings at runtime, so we log a warning
    logger.warning(
        f"[Platform Config] To change primary workspace to '{workspace_name}', "
        f"set PRIMARY_WORKSPACE_NAME in settings or DONKEY_BETZ_PRIMARY_WORKSPACE env var"
    )
    clear_config_cache()


def set_primary_user(username: str):
    """
    Update the primary user configuration.

    Note: This updates the runtime setting but does NOT persist.
    For persistent changes, update Django settings or environment variables.

    Args:
        username: New primary username
    """
    logger.warning(
        f"[Platform Config] To change primary user to '{username}', "
        f"set PRIMARY_USERNAME in settings or DONKEY_BETZ_PRIMARY_USER env var"
    )
    clear_config_cache()


def get_config_status() -> dict:
    """
    Get the current configuration status for debugging.

    Returns:
        Dict with configuration details
    """
    workspace = get_primary_workspace()
    user = get_primary_user()

    return {
        'configured_workspace_pattern': get_primary_workspace_name(),
        'configured_username': get_primary_username(),
        'active_workspace': workspace.name if workspace else None,
        'active_workspace_id': workspace.id if workspace else None,
        'active_workspace_operations': workspace.total_operations if workspace else None,
        'active_user': user.username if user else None,
        'active_user_id': user.id if user else None,
        'cache_hit': bool(_cached_primary_workspace_id.cache_info().hits),
    }


# Convenience aliases for backwards compatibility
get_workspace_for_skin_layer = get_primary_workspace_and_user
