"""
Unified Authentication Middleware
Ensures consistent token validation and security policies across all API endpoints
"""

import logging
import json
from typing import Optional
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

from .api_responses import api_unauthorized, api_forbidden, api_error

logger = logging.getLogger(__name__)
User = get_user_model()


class UnifiedTokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Unified token authentication middleware for HTTP requests
    Provides consistent token validation across all API endpoints
    """
    
    # Paths that don't require authentication (support session auth)
    PUBLIC_PATHS = [
        '/api/v1/health/',  # Health check endpoint
        '/api/v1/auth/login/',  # Login endpoint
        '/api/v1/auth/register/',  # Registration endpoint
        '/api/v1/auth/forgot-password/',  # Password reset
        '/api/v1/auth/reset-password/',  # Password reset confirmation
        '/api/v1/intelligence/real-income-builder/',  # Income Builder endpoint - session auth
        '/api/v1/style-memory/',  # Style Memory - Session 169: Learning from user interactions
        '/api/preferences/recommendations/',  # Session 210: Style recommendations (works for anon too)
        '/api/opportunities/',  # Session 223: Opportunity Engine - supports session auth
        '/api/teams/',  # Session 227: Team Power - supports session auth
        '/api/distribution/',  # Session 229: Smart Distribution - supports session auth
        '/api/spider-dashboard/',  # Session 236: Spider Dashboard - supports session auth
        '/api/spider-intelligence/',  # Session 236: Spider Intelligence feeds - supports session auth
        '/api/learning-loop/',  # Session 232: Learning Loop - supports session auth
        '/api/proactive/',  # Session 234: Proactive System - supports session auth
        '/api/ab-testing/',  # Session 235: A/B Testing - supports session auth
        '/api/goals/',  # Session 235: Goal Tracking - supports session auth
        '/api/portfolio/generated_images/',  # Session 237: Legacy URL redirect (no auth needed)
        '/api/agent-dreams/',  # Session 247: Agent Dreams - supports session auth
        '/api/agent-learning/',  # Session 244: Agent Learning - supports session auth
        '/api/autonomous-learning/',  # Session 243: Autonomous Learning - supports session auth
        '/api/learning/',  # Session 248: Learning Feed - supports session auth
        '/api/hive-mind/',  # Session 250: Hive Mind Mode - supports session auth
        '/api/memory-palace/',  # Session 251: Memory Palace - supports session auth
        '/api/agent-mood/',  # Session 252: Agent Mood System - supports session auth
        '/api/agent-relationships/',  # Session 253: Agent Rivalries & Alliances - supports session auth
        '/api/agent-evolution/',  # Session 254: Agent Evolution System - supports session auth
        '/api/time-travel/',  # Session 255: Time Travel Debugging - supports session auth
        '/api/personality/',  # Session 256: Agent Personality System - supports session auth
        '/api/memory-clusters/',  # Session 257: Memory Clusters - supports session auth
        '/api/predictions/',  # Session 258: Agent Predictions - supports session auth
        '/api/time-capsules/',  # Session 259: Time Capsule Messages - supports session auth
        '/admin/',  # Django admin has its own auth
        '/api-auth/',  # DRF browsable API auth
    ]
    
    # Paths that require staff privileges
    STAFF_REQUIRED_PATHS = [
        '/api/v1/admin/',
        '/api/v1/system/',
        '/api/v1/metrics/admin/',
    ]
    
    def process_request(self, request):
        """Process incoming request for authentication"""
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return None

        # Skip public paths
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None

        # Check if user is already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Session authentication is valid for API requests
            logger.debug(f"Session authenticated user {request.user.username} for {request.path}")

            # Check if staff access required
            if any(request.path.startswith(path) for path in self.STAFF_REQUIRED_PATHS):
                if not request.user.is_staff:
                    logger.warning(f"Staff access required for {request.path}, user: {request.user.username}")
                    return api_forbidden("Staff access required")

            return None

        # Extract token from request
        token = self.extract_token(request)

        if not token:
            # No token and no session authentication
            logger.warning(f"No authentication provided for {request.path}")
            return api_unauthorized("Authentication required")

        # Validate token and get user
        user = self.validate_token(token)

        if not user:
            logger.warning(f"Invalid authentication token for {request.path}")
            return api_unauthorized("Invalid authentication token")

        # Check if staff access required
        if any(request.path.startswith(path) for path in self.STAFF_REQUIRED_PATHS):
            if not user.is_staff:
                logger.warning(f"Staff access required for {request.path}, user: {user.username}")
                return api_forbidden("Staff access required")

        # Attach user to request
        request.user = user

        # Log successful authentication
        logger.debug(f"Authenticated user {user.username} for {request.path}")

        return None
    
    def extract_token(self, request) -> Optional[str]:
        """Extract authentication token from request"""
        # Try Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Token '):
            return auth_header.split(' ', 1)[1]
        elif auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
        
        # Try custom header
        custom_token = request.META.get('HTTP_X_API_KEY')
        if custom_token:
            return custom_token
        
        # Try query parameter (less secure, only for development)
        if settings.DEBUG:
            return request.GET.get('token')
        
        return None
    
    def validate_token(self, token_value: str) -> Optional[User]:
        """Validate authentication token and return user"""
        try:
            token = Token.objects.select_related('user').get(key=token_value)
            
            # Check if user is active
            if not token.user.is_active:
                logger.warning(f"Token belongs to inactive user: {token.user.username}")
                return None
            
            return token.user
            
        except Token.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return None


class WebSocketAuthenticationMiddleware(BaseMiddleware):
    """
    WebSocket authentication middleware
    Ensures consistent authentication for WebSocket connections
    """
    
    async def __call__(self, scope, receive, send):
        """Authenticate WebSocket connection"""
        # Only process WebSocket connections
        if scope['type'] != 'websocket':
            return await super().__call__(scope, receive, send)
        
        # Extract token from query string or headers
        token = await self.extract_websocket_token(scope)
        
        # Validate token if provided
        if token:
            user = await self.validate_websocket_token(token)
            scope['user'] = user or AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        # Check if WebSocket authentication is required
        ws_auth_required = getattr(settings, 'REQUIRE_WEBSOCKET_AUTH', True)

        if ws_auth_required and isinstance(scope['user'], AnonymousUser):
            # Close connection with authentication error
            logger.warning("WebSocket connection rejected: authentication required")
            await send({
                'type': 'websocket.close',
                'code': 4001  # Custom close code for authentication required
            })
            return
        
        # Log successful WebSocket authentication
        if not isinstance(scope['user'], AnonymousUser):
            logger.debug(f"WebSocket authenticated: {scope['user'].username}")
        
        return await super().__call__(scope, receive, send)
    
    async def extract_websocket_token(self, scope) -> Optional[str]:
        """Extract authentication token from WebSocket scope"""
        # Try query string first
        query_string = scope.get('query_string', b'').decode('utf-8')
        if query_string:
            parsed_query = parse_qs(query_string)
            token = parsed_query.get('token', [None])[0]
            if token:
                return token
        
        # Try headers
        headers = dict(scope.get('headers', []))
        
        # Authorization header
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        if auth_header.startswith('Token '):
            return auth_header.split(' ', 1)[1]
        elif auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
        
        # Custom header
        custom_token = headers.get(b'x-api-key', b'').decode('utf-8')
        if custom_token:
            return custom_token
        
        return None
    
    @database_sync_to_async
    def validate_websocket_token(self, token_value: str) -> Optional[User]:
        """Validate WebSocket authentication token"""
        try:
            token = Token.objects.select_related('user').get(key=token_value)

            # Check if user is active
            if not token.user.is_active:
                return None

            return token.user

        except Token.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error validating WebSocket token: {str(e)}")
            return None



class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    Provides consistent security headers across the platform
    """
    
    def process_response(self, request, response):
        """Add security headers to response"""
        # Basic security headers for all responses
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Frame options (can be overridden by views if needed)
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        # HTTPS security headers for production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # API-specific headers
        if request.path.startswith('/api/'):
            response['X-API-Version'] = 'v1'
            response['X-Platform'] = 'Unified Donkey Betz'
        
        # CORS headers are handled by django-cors-headers middleware
        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Enhanced rate limiting middleware
    Provides additional rate limiting beyond DRF throttling
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.rate_limits = {
            '/api/v1/auth/login/': (5, 300),  # 5 attempts per 5 minutes
            '/api/v1/auth/register/': (3, 3600),  # 3 attempts per hour
            '/api/v1/auth/forgot-password/': (3, 3600),  # 3 attempts per hour
        }
    
    def process_request(self, request):
        """Apply additional rate limiting"""
        # Skip if not an API request
        if not request.path.startswith('/api/'):
            return None
        
        # Check specific endpoint rate limits
        for endpoint, (limit, window) in self.rate_limits.items():
            if request.path == endpoint:
                client_ip = self.get_client_ip(request)
                
                # Check rate limit (implementation would use Redis/cache)
                if self.is_rate_limited(client_ip, endpoint, limit, window):
                    logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
                    return JsonResponse(
                        {
                            'success': False,
                            'error': {
                                'code': 'rate_limited',
                                'message': 'Too many requests. Please try again later.'
                            }
                        },
                        status=429
                    )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip, endpoint, limit, window):
        """Check if client is rate limited using Django cache (Redis-backed)"""
        from django.core.cache import cache

        cache_key = f"rate_limit:{endpoint}:{client_ip}"

        # Get current count
        current_count = cache.get(cache_key, 0)

        if current_count >= limit:
            return True

        # Increment counter
        if current_count == 0:
            # First request in window
            cache.set(cache_key, 1, window)
        else:
            cache.incr(cache_key)

        return False


class APILoggingMiddleware(MiddlewareMixin):
    """
    Enhanced API request/response logging
    Provides consistent logging across all API endpoints
    """
    
    def process_request(self, request):
        """Log API request"""
        if request.path.startswith('/api/'):
            # Don't log sensitive endpoints in detail
            sensitive_paths = ['/api/v1/auth/login/', '/api/v1/auth/register/']
            
            if any(request.path.startswith(path) for path in sensitive_paths):
                logger.info(f"API Request: {request.method} {request.path} [SENSITIVE]")
            else:
                logger.debug(
                    f"API Request: {request.method} {request.path}",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'user': getattr(request, 'user', None),
                        'ip': self.get_client_ip(request)
                    }
                )
        
        return None
    
    def process_response(self, request, response):
        """Log API response"""
        if request.path.startswith('/api/'):
            logger.debug(
                f"API Response: {request.method} {request.path} -> {response.status_code}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'user': getattr(request, 'user', None)
                }
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip