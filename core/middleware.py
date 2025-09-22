"""
Custom middleware for the Unified Donkey Betz Platform.
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAuthEndpoints(MiddlewareMixin):
    """
    Disable CSRF protection for authentication endpoints to allow API access.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # List of paths that should be exempt from CSRF
        csrf_exempt_paths = [
            '/api/v1/auth/login/',
            '/api/auth/login/',
            '/api/v1/auth/register/',
            '/api/v1/auth/forgot-password/',
            '/api/v1/auth/reset-password/',
            '/api/freelance/analyze/',
            '/api/freelance/',
        ]
        
        # Check if the current path should be exempt
        path_to_check = request.path
        if (path_to_check in csrf_exempt_paths or
            any(path_to_check.startswith(path) for path in csrf_exempt_paths) or
            '/api/freelance/' in path_to_check or
            path_to_check.startswith('/api/freelance/')):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None