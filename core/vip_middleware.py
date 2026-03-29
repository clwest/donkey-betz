"""
VIP Read-Only Middleware — blocks non-GET requests from VIP demo viewers.

VIP users (primary_role='vip_demo_viewer') can only read data. Any
POST/PUT/PATCH/DELETE is rejected with 403, except for the auth
exchange endpoint itself.
"""

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Paths VIP users are allowed to POST to (token exchange, auth, PA chat)
_VIP_ALLOWED_WRITE_PATHS = frozenset([
    '/api/v1/vip-invites/exchange/',
    '/api/auth/login/',
    '/api/auth/logout/',
    '/api/pa/chat/',
])


class VIPReadOnlyMiddleware:
    """Block write requests from VIP demo viewers."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            if self._is_vip_user(request) and request.path not in _VIP_ALLOWED_WRITE_PATHS:
                logger.info("VIP read-only block: %s %s user=%s", request.method, request.path, request.user)
                return JsonResponse(
                    {'error': 'VIP demo accounts are read-only.'},
                    status=403,
                )
        return self.get_response(request)

    def _is_vip_user(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
        try:
            profile = request.user.enhanced_profile
            return profile.primary_role == 'vip_demo_viewer'
        except Exception:
            return False
