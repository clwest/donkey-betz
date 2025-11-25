"""
Centralized decorators for rate limiting and request validation.
Phase 2 High Priority - Task 2.1/2.2/2.3
"""

from functools import wraps
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def get_rate_limit_identifier(request):
    """Get a unique identifier for rate limiting based on user or IP."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"user:{request.user.id}"
    return f"ip:{get_client_ip(request)}"


def is_rate_limited(request, limit_type='default'):
    """
    Check if the request should be rate limited.

    Args:
        request: Django HTTP request
        limit_type: Type of rate limit to apply (from settings.RATE_LIMITS)

    Returns:
        tuple: (is_limited: bool, wait_time: int, remaining: int)
    """
    # Get rate limit config
    rate_limits = getattr(settings, 'RATE_LIMITS', {})
    limits = rate_limits.get(limit_type, rate_limits.get('default', {'requests': 100, 'window': 60}))

    max_requests = limits['requests']
    window_seconds = limits['window']

    # Get identifier
    identifier = get_rate_limit_identifier(request)
    cache_key = f"rate_limit:{limit_type}:{identifier}"

    # Get current count and TTL
    current_count = cache.get(cache_key, 0)

    if current_count >= max_requests:
        # Calculate wait time based on TTL
        try:
            # Some cache backends support ttl()
            wait_time = cache.ttl(cache_key)
            if wait_time is None or wait_time < 0:
                wait_time = window_seconds
        except (AttributeError, TypeError):
            wait_time = window_seconds

        return True, wait_time, 0

    # Increment counter
    if current_count == 0:
        cache.set(cache_key, 1, window_seconds)
    else:
        try:
            cache.incr(cache_key)
        except ValueError:
            # Key expired between get and incr
            cache.set(cache_key, 1, window_seconds)

    remaining = max_requests - current_count - 1
    return False, 0, remaining


def rate_limit(limit_type='default'):
    """
    Decorator for rate limiting views.

    Args:
        limit_type: Type of rate limit to apply (from settings.RATE_LIMITS)
                   Options: 'default', 'ai_generation', 'video_processing',
                           'image_processing', 'api_expensive', 'auth_login',
                           'auth_register', 'auth_password_reset'

    Usage:
        @rate_limit('ai_generation')
        def generate_image(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if rate limiting is enabled
            if not getattr(settings, 'RATE_LIMIT_ENABLED', True):
                return view_func(request, *args, **kwargs)

            is_limited, wait_time, remaining = is_rate_limited(request, limit_type)

            if is_limited:
                identifier = get_rate_limit_identifier(request)
                logger.warning(
                    f"Rate limit exceeded for {limit_type} by {identifier}. "
                    f"Wait {wait_time} seconds."
                )

                response = JsonResponse({
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait before making more requests.',
                    'error_code': 'RATE_LIMITED',
                    'retry_after': wait_time,
                    'limit_type': limit_type
                }, status=429)

                # Add rate limit headers
                response['Retry-After'] = str(wait_time)
                response['X-RateLimit-Limit'] = str(
                    settings.RATE_LIMITS.get(limit_type, {}).get('requests', 100)
                )
                response['X-RateLimit-Remaining'] = '0'

                return response

            # Execute view
            response = view_func(request, *args, **kwargs)

            # Add rate limit headers to successful responses
            if hasattr(response, '__setitem__'):
                rate_limits = getattr(settings, 'RATE_LIMITS', {})
                limits = rate_limits.get(limit_type, {'requests': 100, 'window': 60})
                response['X-RateLimit-Limit'] = str(limits['requests'])
                response['X-RateLimit-Remaining'] = str(remaining)

            return response

        return wrapper
    return decorator


def rate_limit_method(limit_type='default'):
    """
    Decorator for rate limiting class-based view methods.

    Usage:
        class MyView(View):
            @rate_limit_method('ai_generation')
            def post(self, request):
                ...
    """
    def decorator(method):
        @wraps(method)
        def wrapper(self, request, *args, **kwargs):
            # Check if rate limiting is enabled
            if not getattr(settings, 'RATE_LIMIT_ENABLED', True):
                return method(self, request, *args, **kwargs)

            is_limited, wait_time, remaining = is_rate_limited(request, limit_type)

            if is_limited:
                identifier = get_rate_limit_identifier(request)
                logger.warning(
                    f"Rate limit exceeded for {limit_type} by {identifier}. "
                    f"Wait {wait_time} seconds."
                )

                response = JsonResponse({
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait before making more requests.',
                    'error_code': 'RATE_LIMITED',
                    'retry_after': wait_time,
                    'limit_type': limit_type
                }, status=429)

                response['Retry-After'] = str(wait_time)
                return response

            return method(self, request, *args, **kwargs)

        return wrapper
    return decorator


# Convenience decorators for common rate limit types
def rate_limit_ai(view_func):
    """Rate limit decorator for AI generation endpoints (10/min)."""
    return rate_limit('ai_generation')(view_func)


def rate_limit_video(view_func):
    """Rate limit decorator for video processing endpoints (5/min)."""
    return rate_limit('video_processing')(view_func)


def rate_limit_image(view_func):
    """Rate limit decorator for image processing endpoints (20/min)."""
    return rate_limit('image_processing')(view_func)


def rate_limit_expensive(view_func):
    """Rate limit decorator for expensive API operations (20/min)."""
    return rate_limit('api_expensive')(view_func)
