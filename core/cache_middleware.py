"""
Redis caching middleware for API responses
"""
import json
import logging
from django.http import JsonResponse
from functools import wraps
import redis

logger = logging.getLogger(__name__)

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=1,  # Use db 1 for caching
    decode_responses=True
)

def cache_api_response(timeout=300):
    """
    Decorator to cache API responses in Redis
    timeout: Cache timeout in seconds (default 5 minutes)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            
            # Create cache key from URL and query params
            cache_key = f"api_cache:{request.path}:{request.GET.urlencode()}"
            
            # Add user ID to cache key if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                cache_key += f":user_{request.user.id}"
            
            # Try to get from cache
            try:
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    response = JsonResponse(data)
                    response['X-Cache'] = 'HIT'
                    return response
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
            
            # Call the actual view
            response = view_func(request, *args, **kwargs)
            
            # Cache the response if it's successful
            if hasattr(response, 'status_code') and response.status_code == 200:
                try:
                    if hasattr(response, 'data'):
                        # DRF Response
                        redis_client.setex(
                            cache_key,
                            timeout,
                            json.dumps(response.data)
                        )
                    elif hasattr(response, 'content'):
                        # JsonResponse
                        redis_client.setex(
                            cache_key,
                            timeout,
                            response.content.decode('utf-8')
                        )
                    response['X-Cache'] = 'MISS'
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")
                    response['X-Cache'] = 'ERROR'
            
            return response
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern
    """
    try:
        for key in redis_client.scan_iter(match=f"api_cache:{pattern}*"):
            redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")
        return False


class RedisCacheMiddleware:
    """
    Middleware to add caching headers and handle cache invalidation
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cache headers for static assets
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=31536000'
        elif request.path.startswith('/api/'):
            # API responses are cached by decorator
            pass
        
        return response