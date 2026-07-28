"""
VIP Access Control Middleware — enforces read-only + workspace scoping for VIP users.

VIP users (primary_role='vip_demo_viewer') are restricted to:
- GET/HEAD/OPTIONS only (no writes except whitelisted paths)
- Only their assigned workspace's data (via cockpit workspace param)
- Whitelisted API paths only (cockpit, deliverables, PA chat)

Non-VIP users pass through unchanged.
"""

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Paths VIP users are allowed to POST to
_VIP_ALLOWED_WRITE_PATHS = frozenset([
    '/api/v1/vip-invites/exchange/',
    '/api/auth/login/',
    '/api/auth/logout/',
    '/api/pa/chat/',
])

# Exact cockpit paths VIP users can access (workspace-scoped or safe)
_VIP_ALLOWED_COCKPIT_PATHS = frozenset([
    '/api/cockpit/vip-context/',
    '/api/cockpit/library/deliverables/',
    '/api/cockpit/library/media/',
])

# GET paths VIP users are allowed to access (prefix match)
_VIP_ALLOWED_READ_PREFIXES = (
    '/api/deliverables/',
    '/api/pa/',
    '/api/v1/health/',
    '/api/auth/',
    '/api/v1/vip-invites/',
    '/health/',
    # Frontend assets and pages
    '/static/',
    '/assets/',
    '/vip/',
    '/cockpit',
    '/favicon',
)


class VIPReadOnlyMiddleware:
    """Enforce read-only + scoped access for VIP demo viewers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_vip_user(request):
            return self.get_response(request)

        # T-VIP-1: enforce VIPInvite.account_expires_at + revoked_at
        # (ADR-0005 §3.5 risk-gate — F-C-VIP-1 preserved HIGH-severity).
        if not self._invite_is_still_active(request.user):
            logger.info(
                "VIP expiry/revoke block: %s %s user=%s",
                request.method, request.path, request.user,
            )
            return JsonResponse(
                {'error': 'Your VIP demo access has expired.'},
                status=401,
            )

        path = request.path

        # Block writes (except whitelisted)
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            if path not in _VIP_ALLOWED_WRITE_PATHS:
                logger.info("VIP write block: %s %s user=%s", request.method, path, request.user)
                return JsonResponse(
                    {'error': 'VIP demo accounts are read-only.'},
                    status=403,
                )

        # For cockpit API: strict allowlist (not blanket /api/cockpit/)
        if path.startswith('/api/cockpit/'):
            if path not in _VIP_ALLOWED_COCKPIT_PATHS:
                logger.info("VIP cockpit block: %s %s user=%s", request.method, path, request.user)
                return JsonResponse(
                    {'error': 'Access restricted.'},
                    status=403,
                )
            return self.get_response(request)

        # Check against allowed read prefixes
        for prefix in _VIP_ALLOWED_READ_PREFIXES:
            if path.startswith(prefix):
                return self.get_response(request)

        # Block everything else for VIP users
        logger.info("VIP default block: %s %s user=%s", request.method, path, request.user)
        return JsonResponse(
            {'error': 'Access restricted.'},
            status=403,
        )

    def _is_vip_user(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        try:
            profile = request.user.enhanced_profile
            return profile.primary_role == 'vip_demo_viewer'
        except Exception as _e:
            logger.warning(
                "vip_middleware._is_vip_user: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def _invite_is_still_active(self, user):
        """Return False if the user's redeeming invite is revoked or past
        account_expires_at. Missing invite row for a vip_demo_viewer user is
        treated as a data-inconsistency deny.
        """
        from django.utils import timezone

        from core.models_vip_invite import VIPInvite

        try:
            invite = (
                VIPInvite.objects
                .filter(redeemed_by=user)
                .order_by('-redeemed_at')
                .first()
            )
            if invite is None:
                logger.warning(
                    "vip_middleware: vip_demo_viewer user has no VIPInvite row — "
                    "denying (user_id=%s username=%s)",
                    getattr(user, 'id', None), getattr(user, 'username', None),
                )
                return False
            if invite.revoked_at is not None:
                return False
            if invite.account_expires_at <= timezone.now():
                return False
            return True
        except Exception as _e:
            logger.warning(
                "vip_middleware._invite_is_still_active: swallowed (%s: %s) — denying",
                type(_e).__name__, _e,
            )
            return False
