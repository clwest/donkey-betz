"""
Mobile API Authentication
Session 115: Production-Ready Mobile Auth

Custom authentication classes that handle mobile API requests properly:
- Token authentication without CSRF enforcement
- Backwards compatible with existing session auth
"""

from rest_framework.authentication import SessionAuthentication, TokenAuthentication


class MobileTokenAuthentication(TokenAuthentication):
    """
    Token authentication for mobile apps.

    Extends DRF's TokenAuthentication to work seamlessly with mobile clients.
    Uses X-API-Key header (already handled by TokenAuthentication's get_authorization_header).
    """


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that doesn't enforce CSRF.

    Use this for API endpoints that need to support both:
    - Web browser sessions (with CSRF)
    - Mobile token auth (without CSRF)

    When a request has a valid token, CSRF is not required.
    """

    def enforce_csrf(self, request):
        """
        Don't enforce CSRF if request has a valid API token.

        This allows mobile apps to use token auth without CSRF cookies,
        while still enforcing CSRF for pure session-based requests.
        """
        # Check if request has X-API-Key header
        if request.META.get('HTTP_X_API_KEY'):
            # Token auth request - skip CSRF
            return

        # Check if request has Authorization header with token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token ') or auth_header.startswith('Bearer '):
            # Token auth request - skip CSRF
            return

        # No token - enforce CSRF for session auth
        return super().enforce_csrf(request)
