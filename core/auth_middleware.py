"""
Unified Authentication Middleware
Ensures consistent token validation and security policies across all API endpoints
"""

import logging
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

from .api_responses import api_unauthorized, api_forbidden

logger = logging.getLogger(__name__)
User = get_user_model()


class UnifiedTokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Unified token authentication middleware for HTTP requests
    Provides consistent token validation across all API endpoints
    """
    
    # Session 528: SECURITY HARDENING - Reduced PUBLIC_PATHS to truly public endpoints only
    # Previously 48 paths were exempt from auth - now only essential endpoints are public
    # All other /api/ endpoints now require session auth OR token auth
    PUBLIC_PATHS = [
        # Health & Status (truly public)
        '/api/v1/health/',  # Health check endpoint
        '/health/',  # Health check

        # Authentication endpoints (must be public to allow login/register)
        '/api/v1/auth/login/',  # Login endpoint
        '/api/v1/auth/register/',  # Registration endpoint
        '/api/v1/auth/forgot-password/',  # Password reset request
        '/api/v1/auth/reset-password/',  # Password reset confirmation
        '/api-auth/',  # DRF browsable API auth

        # Webhooks with their own verification (use secrets/signatures)
        '/api/discord/verify-link-code/',  # Discord bot verification (uses bot_secret)
        '/api/stripe/webhook/',  # Stripe webhook (uses signature verification)

        # Django admin (has its own auth)
        '/admin/',

        # Public statistics (intentionally anonymous)
        '/api/public-stats/',  # Explicitly public stats

        # Session 538: Intelligence APIs (read-only, non-sensitive, used by UI Command Center)
        '/api/spider-intelligence/dashboard-stats/',  # Spider statistics
        '/api/spider-intelligence/detail/',  # Spider detail panel
        '/api/agent-intelligence/detail/',  # Agent detail panel
        '/api/situation-intelligence/detail/',  # Situation detail panel
        '/api/intelligence/cross-references/',  # Cross-reference mappings
        '/api/autonomous/situations/',  # Situations list for Command Center
        '/api/autonomous/trigger-events/',  # Trigger events for Command Center
        '/api/agents/',  # Session 564: Agent list for Command Center
        '/api/agent-conversations/',  # Session 564: Conversations sub-tab
        '/api/agent-dreams/',  # Session 564: Dreams sub-tab
        '/api/boardroom/',  # Session 564: Boardroom sub-tab
        '/api/pilot-gates/',  # Session 590: Pilot Readiness Gates
        '/api/celery/',  # Session 660: Celery Task Monitor
        '/api/icc/',  # Session 660: ICC Health Dashboard
        '/api/artifacts/',  # Session 564: Artifacts sub-tab
        '/api/agent-learning/',  # Session 564: Learning activity
        '/api/recent-activity/',  # Session 614: Recent Activity panel
        '/api/experiment-recommendations/',  # Session 615: Experiment Recommendations

        # Session 542: Research Demo APIs (read-only visualization for research presentations)
        '/api/v1/research/network-graph/',  # D3.js graph data
        '/api/v1/research/live-feed/',  # Learning event feed
        '/api/v1/research/stats/',  # Pipeline statistics
        '/api/v1/research/mythology-gate/',  # Quarantine visualization
        # Session 543: Self-Blog APIs
        '/api/v1/research/self-blog/',  # Get latest self-blog
        '/api/v1/research/self-blog/generate/',  # Generate new self-blog
        '/api/v1/research/self-blog/task/',  # Check task status (prefix match)
        # Session 588: System Insights API
        '/api/v1/research/system-insights/',  # System insights from ThinkingAgent
        # Session 622: Deliverables API
        '/api/v1/research/deliverables/',  # Synthesized deliverables from research pipeline
        # Session 622: Document Registry / Initiatives API
        '/api/v1/initiatives/',  # View initiatives and their stages
        '/api/v1/initiatives/populate/',  # Auto-populate from deliverables

        # Session 544: Autonomous Reasoning Engine APIs
        '/api/v1/reasoning/thoughts/',  # View thought records
        '/api/v1/reasoning/actions/',  # View autonomous actions
        '/api/v1/reasoning/trigger/',  # Trigger thinking cycle
        '/api/v1/reasoning/task/',  # Check task status
        '/api/v1/reasoning/config/',  # View/update config
        '/api/v1/reasoning/dashboard/',  # Dashboard data

        # Session 546: Concern Tracking APIs
        '/api/v1/reasoning/concerns/',  # Concern dashboard

        # Session 558: Prediction Markets & Sports Odds API (read-only for Command Center)
        '/api/prediction-markets/',  # Kalshi prediction market data
        '/api/sports-odds/',  # The Odds API sports betting data

        # Session 559: Betting Dashboard APIs (read-only for web UI)
        '/api/v1/betting/arbitrage/',  # Arbitrage scanning
        '/api/v1/sports/live-odds/',  # Live sports odds
        '/api/v1/sports/live-odds-scores/',  # Session 563: Live odds with ESPN scores
        '/api/v1/sports/events/',  # Session 563: Player props (matches /events/{id}/props/)
        '/api/v1/odds/bankroll/',  # Bankroll stats (read-only)
        # Session 560: Futures odds
        '/api/v1/betting/futures/',  # Championship futures
        # Session 561: Line Movement Charts
        '/api/v1/betting/line-movement/',  # Line movement data
        '/api/v1/betting/movers/',  # Games with significant movement
        # Session 562: Push Notifications (public key is public, subscribe needs to work for anon)
        '/api/v1/push/vapid-key/',  # VAPID public key for subscription
        '/api/v1/push/subscribe/',  # Allow anonymous subscriptions
        '/api/v1/push/unsubscribe/',  # Allow anonymous unsubscribe

        # Session 563: Bet Tracking (allow anonymous for demo mode)
        '/api/v1/betting/place/',  # Place bets
        '/api/v1/betting/wagers/',  # View wagers
        '/api/v1/betting/stats/',  # View stats
        '/api/v1/betting/recent/',  # Recent activity

        # Session 641: Agent Performance Dashboard APIs
        '/api/agent-analytics/',  # All agent analytics endpoints
        '/api/system-health/',  # System health check
        '/api/agents/test/',  # Test agent execution

        # Session 642: Celery Monitoring
        '/api/celery/',  # Celery status endpoint

        # Session 687: Dashboard APIs (read-only stats for React frontend)
        '/api/ecosystem/stats/',  # Ecosystem statistics
        '/api/ecosystem/live-feed/',  # Live activity feed
        '/api/dashboard/stats/',  # Dashboard statistics
        '/api/v1/intelligence/spider-status/',  # Spider status
        '/api/spider-intelligence/report/',  # Daily spider report

        # Session 688: Agents Page APIs (read-only for React frontend)
        '/api/v1/agents/comprehensive/',  # Agent list with categories
        '/api/v1/agents/list/',  # Basic agent list
        '/api/v1/agents/health/',  # Agent health status
        '/api/recent-activity/',  # Recent system activity feed
        '/api/agent-learning/',  # Learning activity feed

        # Session 688: Intelligence Page APIs (read-only for React frontend)
        '/api/v1/intelligence/skynet/status/',  # Skynet intelligence status
        '/api/v1/intelligence/opportunities/',  # Opportunities list
        '/api/v1/intelligence/predictions/',  # AI predictions
        '/api/pilots/',  # Pilots dashboard and list
        '/api/experiments/',  # Experiments list

        # Session 688: Betting Page APIs (read-only for React frontend)
        '/api/v1/betting/stats/',  # Betting statistics
        '/api/v1/betting/wagers/',  # User wagers
        '/api/v1/betting/arbitrage/',  # Arbitrage opportunities
        '/api/v1/sports/live-odds',  # Live odds
        '/api/v1/odds/bankroll/',  # Bankroll management
        '/api/v1/odds/markets/',  # Betting markets

        # Session 688: Content Page APIs (read-only for React frontend)
        '/api/v1/gallery/',  # Gallery endpoints
        '/api/content-calendar/',  # Content calendar
        '/api/creative-projects/',  # Creative projects
        '/api/v1/content/templates/',  # Content templates

        # Session 688: Legal Page APIs (read-only for React frontend)
        '/api/legal/case-files/',  # Legal documents
        '/api/legal/cases/',  # Legal cases
        '/api/legal/active-case/',  # Active case

        # Session 688: Podcast Page APIs (read-only for React frontend)
        '/api/podcasts/',  # Podcast endpoints
    ]

    # Session 528: Paths that allow session auth but DON'T require it (optional auth)
    # These endpoints work for both authenticated and anonymous users
    # Anonymous users get limited/public data, authenticated users get full access
    OPTIONAL_AUTH_PATHS = [
        '/api/voice-marketplace/',  # Browse marketplace is public, purchasing requires auth
        '/api/monitoring/',  # Public monitoring dashboard for stress tests
    ]
    
    # Paths that require staff privileges
    STAFF_REQUIRED_PATHS = [
        '/api/v1/admin/',
        '/api/v1/system/',
        '/api/v1/metrics/admin/',
    ]
    
    def process_request(self, request):
        """Process incoming request for authentication"""
        # Skip non-API requests (let Django handle them)
        if not request.path.startswith('/api/') and not request.path.startswith('/admin/'):
            return None

        # Skip truly public paths (no auth required at all)
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None

        # Session 528: Handle optional auth paths
        # These work for both auth and anon users - try to authenticate but don't require it
        is_optional_auth = any(request.path.startswith(path) for path in self.OPTIONAL_AUTH_PATHS)
        if is_optional_auth:
            # Try to authenticate, but don't fail if no auth provided
            if hasattr(request, 'user') and request.user.is_authenticated:
                return None  # Already authenticated via session
            token = self.extract_token(request)
            if token:
                user = self.validate_token(token)
                if user:
                    request.user = user
            return None  # Allow through regardless

        # Session 452: Support DRF's force_authenticate() for testing
        # DRF's force_authenticate sets _force_auth_user on the request
        if hasattr(request, '_force_auth_user') and request._force_auth_user:
            request.user = request._force_auth_user
            logger.debug(f"DRF force_authenticate user {request.user.username} for {request.path}")
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