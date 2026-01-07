"""
Rate Limiting Configuration for External API Calls
Protects against excessive API usage and manages costs
"""

from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Rate limit configurations for different API services
RATE_LIMITS = {
    'espn_api': {
        'calls': 100,
        'period': 60,  # 100 calls per minute
        'burst': 10,   # Allow burst of 10 calls
        'cooldown': 5   # 5 second cooldown after burst
    },
    'odds_api': {
        'calls': 50,
        'period': 60,  # 50 calls per minute (protect free tier)
        'burst': 5,
        'cooldown': 10
    },
    'weather_api': {
        'calls': 60,
        'period': 60,  # 60 calls per minute
        'burst': 5,
        'cooldown': 3
    },
    'openai_api': {
        'calls': 20,
        'period': 60,  # 20 calls per minute
        'burst': 3,
        'cooldown': 15
    },
    'anthropic_api': {
        'calls': 15,
        'period': 60,  # 15 calls per minute
        'burst': 3,
        'cooldown': 20
    },
    'default': {
        'calls': 30,
        'period': 60,  # Default: 30 calls per minute
        'burst': 5,
        'cooldown': 10
    }
}


class RateLimiter:
    """
    Token bucket algorithm implementation for rate limiting
    """
    
    def __init__(self, service_name='default'):
        self.service_name = service_name
        self.config = RATE_LIMITS.get(service_name, RATE_LIMITS['default'])
        self.calls_limit = self.config['calls']
        self.period = self.config['period']
        self.burst_limit = self.config['burst']
        self.cooldown = self.config['cooldown']
    
    def _get_cache_key(self, identifier):
        """Generate cache key for rate limiting"""
        return f"rate_limit:{self.service_name}:{identifier}"
    
    def _get_burst_key(self, identifier):
        """Generate cache key for burst tracking"""
        return f"burst:{self.service_name}:{identifier}"
    
    def check_rate_limit(self, identifier):
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (user_id, IP, or API key)
            
        Returns:
            tuple: (allowed, wait_time, remaining_calls)
        """
        cache_key = self._get_cache_key(identifier)
        burst_key = self._get_burst_key(identifier)
        
        # Get current call count
        current_calls = cache.get(cache_key, 0)
        burst_calls = cache.get(burst_key, 0)
        
        # Check if in cooldown period
        cooldown_key = f"cooldown:{self.service_name}:{identifier}"
        if cache.get(cooldown_key):
            wait_time = cache.ttl(cooldown_key)
            return False, wait_time, 0
        
        # Check burst limit
        if burst_calls >= self.burst_limit:
            # Enforce cooldown
            cache.set(cooldown_key, True, self.cooldown)
            return False, self.cooldown, 0
        
        # Check rate limit
        if current_calls >= self.calls_limit:
            # Calculate wait time
            ttl = cache.ttl(cache_key)
            wait_time = ttl if ttl > 0 else self.period
            return False, wait_time, 0
        
        # Increment counters
        if current_calls == 0:
            # First call in period
            cache.set(cache_key, 1, self.period)
        else:
            cache.incr(cache_key)
        
        # Track burst
        if burst_calls == 0:
            cache.set(burst_key, 1, 1)  # Reset burst counter every second
        else:
            cache.incr(burst_key)
        
        remaining = self.calls_limit - current_calls - 1
        return True, 0, remaining
    
    def reset_limit(self, identifier):
        """Reset rate limit for identifier (admin use)"""
        cache_key = self._get_cache_key(identifier)
        burst_key = self._get_burst_key(identifier)
        cooldown_key = f"cooldown:{self.service_name}:{identifier}"
        
        cache.delete(cache_key)
        cache.delete(burst_key)
        cache.delete(cooldown_key)


def rate_limit_api(service_name='default', identifier_func=None):
    """
    Decorator for rate limiting API endpoints
    
    Args:
        service_name: Name of the service for rate limit config
        identifier_func: Function to extract identifier from request
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get identifier
            if identifier_func:
                identifier = identifier_func(request)
            else:
                # Default: use user ID or IP address
                if request.user and request.user.is_authenticated:
                    identifier = f"user_{request.user.id}"
                else:
                    identifier = f"ip_{get_client_ip(request)}"
            
            # Check rate limit
            limiter = RateLimiter(service_name)
            allowed, wait_time, remaining = limiter.check_rate_limit(identifier)
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded for {service_name} by {identifier}. "
                    f"Wait {wait_time} seconds."
                )
                
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'rate_limit_exceeded',
                        'message': f'Rate limit exceeded. Please wait {wait_time} seconds.',
                        'retry_after': wait_time,
                        'service': service_name
                    }
                }, status=429)
            
            # Add rate limit headers to response
            response = view_func(request, *args, **kwargs)
            response['X-RateLimit-Limit'] = str(limiter.calls_limit)
            response['X-RateLimit-Remaining'] = str(remaining)
            response['X-RateLimit-Reset'] = str(int(datetime.now().timestamp()) + limiter.period)
            
            return response
        
        return wrapped_view
    return decorator


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class ExternalAPIRateLimiter:
    """
    Rate limiter for external API calls made by the backend
    """
    
    @staticmethod
    def check_and_wait(service_name, identifier=None):
        """
        Check rate limit and wait if necessary
        
        Args:
            service_name: Name of external service
            identifier: Optional identifier (defaults to 'system')
            
        Returns:
            bool: True if call allowed, False if should skip
        """
        if not identifier:
            identifier = 'system'
        
        limiter = RateLimiter(service_name)
        allowed, wait_time, remaining = limiter.check_rate_limit(identifier)
        
        if not allowed:
            logger.info(
                f"Rate limit reached for {service_name}. "
                f"Waiting {wait_time} seconds..."
            )
            # In production, you might want to use celery retry instead
            import time
            if wait_time < 30:  # Only wait for short periods
                time.sleep(wait_time)
                return True
            return False
        
        return True


# Middleware for global rate limiting
class RateLimitMiddleware:
    """
    Global rate limiting middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        # Skip rate limiting in DEBUG mode
        if settings.DEBUG:
            return self.get_response(request)

        # Skip rate limiting for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Apply global rate limit for anonymous users
        if not request.user or not request.user.is_authenticated:
            ip = get_client_ip(request)
            cache_key = f"global_rate:{ip}"

            # 500 requests per minute for anonymous users (increased from 100)
            current = cache.get(cache_key, 0)
            if current >= 500:
                # Django's cache doesn't have ttl(), use 60 seconds as default
                ttl = 60
                return JsonResponse({
                    'success': False,
                    'error': {
                        'code': 'rate_limit_exceeded',
                        'message': f'Too many requests. Please wait {ttl} seconds.',
                        'retry_after': ttl
                    }
                }, status=429)
            
            if current == 0:
                cache.set(cache_key, 1, 60)
            else:
                cache.incr(cache_key)
        
        response = self.get_response(request)
        return response


# Utility functions for monitoring
def get_rate_limit_stats(service_name=None):
    """
    Get current rate limit statistics
    
    Returns:
        dict: Statistics for rate limiting
    """
    stats = {}
    
    if service_name:
        services = [service_name]
    else:
        services = RATE_LIMITS.keys()
    
    for service in services:
        # This would need Redis SCAN in production
        # For now, return config
        stats[service] = {
            'config': RATE_LIMITS[service],
            'active_limiters': 0,  # Would count active keys
            'cooldowns': 0  # Would count cooldown keys
        }
    
    return stats


def reset_all_limits():
    """
    Reset all rate limits (admin function)
    """
    # In production, use Redis SCAN to find and delete keys
    # For now, this is a placeholder
    logger.info("Rate limits reset requested")
    return True
