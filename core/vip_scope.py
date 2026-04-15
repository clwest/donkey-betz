"""
VIP Scope — workspace + personalization scoping for VIP demo viewers.

Looks up the VIPInvite associated with a request user to determine:
- Which workspace to filter cockpit data to
- Which prospect profile to use for personalization
- The recipient's display name

Usage in cockpit views:
    from core.vip_scope import get_vip_scope

    scope = get_vip_scope(request)
    if scope.is_vip:
        qs = qs.filter(workspace_id=scope.workspace_id)
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VIPScope:
    is_vip: bool = False
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    prospect_profile_id: Optional[str] = None
    recipient_name: Optional[str] = None
    invite_label: Optional[str] = None


def get_vip_scope(request) -> VIPScope:
    """Extract VIP workspace scope from the request user.

    Checks if the user was created via a VIP invite and returns
    their assigned workspace + prospect profile for cockpit filtering.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return VIPScope()

    # Check if this is a VIP user by looking up their invite
    try:
        from core.models_vip_invite import VIPInvite
        invite = VIPInvite.objects.select_related('workspace', 'prospect_profile').filter(
            redeemed_by=user,
        ).order_by('-redeemed_at').first()

        if not invite:
            return VIPScope()

        return VIPScope(
            is_vip=True,
            workspace_id=str(invite.workspace_id) if invite.workspace_id else None,
            workspace_name=invite.workspace.name if invite.workspace else None,
            prospect_profile_id=str(invite.prospect_profile_id) if invite.prospect_profile_id else None,
            recipient_name=invite.recipient_name or '',
            invite_label=invite.label or '',
        )
    except Exception as e:
        logger.debug(f"VIP scope lookup failed: {e}")
        return VIPScope()


def is_vip_user(request) -> bool:
    """Quick check if current user is a VIP demo viewer."""
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return False
    try:
        from core.models import EnhancedUserProfile
        profile = EnhancedUserProfile.objects.filter(user=user).first()
        return profile and profile.primary_role == 'vip_demo_viewer'
    except Exception as _e:
        logger.warning(
            "vip_scope.is_vip_user: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return False
