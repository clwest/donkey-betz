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
        except Exception:
            return False
