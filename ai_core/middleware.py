"""
Unified middleware for the Donkey Betz Platform

This module provides consistent middleware components across all API endpoints
including authentication, rate limiting, security headers, and error handling.
"""

import json
import time
from datetime import datetime
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)


class UnifiedAPIResponseMiddleware(MiddlewareMixin):
    """
    Ensures all API responses follow a consistent format:
    Success: { success: true, data: {...} }
    Error: { success: false, error: { code, message, details } }
    """
    
    def process_response(self, request, response):
        # Only process API endpoints
        if not request.path.startswith('/api/'):
            return response
        
        # Skip if response is already in the correct format or is not JSON
        if not hasattr(response, 'content') or response.get('content-type', '').find('application/json') == -1:
            return response
        
        try:
            # Parse existing response
            if hasattr(response, 'data'):  # DRF Response
                data = response.data
            else:  # Django JsonResponse
                data = json.loads(response.content.decode('utf-8'))
            
            # If already wrapped with success field, return as-is
            if isinstance(data, dict) and 'success' in data:
                return response
            
            # Wrap successful responses
            if 200 <= response.status_code < 300:
                wrapped_data = {
                    'success': True,
                    'data': data,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            else:
                # Wrap error responses
                wrapped_data = {
                    'success': False,
                    'error': {
                        'code': response.status_code,
                        'message': data.get('detail', str(data)) if isinstance(data, dict) else str(data),
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
                }
            
            # Update response content
            response.content = json.dumps(wrapped_data).encode('utf-8')
            
        except (json.JSONDecodeError, AttributeError, TypeError):
            # If we can't parse or modify, return as-is
            pass
        
        return response


class UnifiedSecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds consistent security headers to all responses
    """
    
    def process_response(self, request, response):
        # Add security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }
        
        # Add HSTS in production
        if not settings.DEBUG:
            security_headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        for header, value in security_headers.items():
            response[header] = value
        
        return response


class UnifiedRateLimitingMiddleware(MiddlewareMixin):
    """
    Consistent rate limiting across all API endpoints
    """
    
    def get_client_identifier(self, request):
        """Get unique identifier for rate limiting"""
        # Try to get user ID first, then fall back to IP
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return f"ip:{ip}"
    
    def is_rate_limited(self, request):
        """Check if request should be rate limited"""
        # Skip rate limiting for certain endpoints
        skip_paths = ['/api/docs/', '/api/schema/', '/api/redoc/', '/admin/']
        if any(request.path.startswith(path) for path in skip_paths):
            return False
        
        # Only apply to API endpoints
        if not request.path.startswith('/api/'):
            return False
        
        client_id = self.get_client_identifier(request)
        
        # Different limits for authenticated vs anonymous users
        is_authenticated = hasattr(request, 'user') and request.user.is_authenticated
        
        # Rate limits per hour
        if is_authenticated:
            max_requests = 1000  # Higher limit for authenticated users
            window = 3600  # 1 hour
        else:
            max_requests = 100   # Lower limit for anonymous users
            window = 3600  # 1 hour
        
        # Burst rate limit (per minute)
        burst_key = f"rate_limit:burst:{client_id}"
        burst_count = cache.get(burst_key, 0)
        if burst_count >= 60:  # 60 requests per minute max
            return True
        
        # Hourly rate limit
        hourly_key = f"rate_limit:hourly:{client_id}"
        hourly_count = cache.get(hourly_key, 0)
        if hourly_count >= max_requests:
            return True
        
        # Increment counters
        cache.set(burst_key, burst_count + 1, 60)  # 1 minute window
        cache.set(hourly_key, hourly_count + 1, window)  # 1 hour window
        
        return False
    
    def process_request(self, request):
        """Process incoming request for rate limiting"""
        if self.is_rate_limited(request):
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 429,
                    'message': 'Rate limit exceeded. Please try again later.',
                    'details': {
                        'retry_after': 60,  # seconds
                        'limit_type': 'requests_per_hour'
                    }
                }
            }, status=429)
        
        return None


class UnifiedAuthenticationMiddleware(MiddlewareMixin):
    """
    Consistent JWT/Token authentication across all API endpoints
    """
    
    def process_request(self, request):
        """Process authentication for API requests"""
        # Only process API endpoints
        if not request.path.startswith('/api/'):
            return None
        
        # Skip authentication for public endpoints
        public_endpoints = [
            '/api/docs/',
            '/api/schema/',
            '/api/redoc/',
            '/api/',
            '/api-auth/',
        ]
        
        if any(request.path.startswith(endpoint) for endpoint in public_endpoints):
            return None
        
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token_key = auth_header.split(' ')[1]
        elif auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
        else:
            # No valid auth header, let DRF handle it
            return None
        
        try:
            # Validate token
            token = Token.objects.select_related('user').get(key=token_key)
            request.user = token.user
            request.auth = token
            
            # Log successful authentication
            logger.info(f"Authenticated user {token.user.username} via token")
            
        except Token.DoesNotExist:
            # Invalid token
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 401,
                    'message': 'Invalid authentication token.',
                    'details': {
                        'expected_format': 'Authorization: Bearer <token> or Authorization: Token <token>'
                    }
                }
            }, status=401)
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests for monitoring and debugging
    """
    
    def process_request(self, request):
        """Log incoming requests"""
        if request.path.startswith('/api/'):
            request._start_time = time.time()
            
            # Log request details
            # Log request details (user may not be available yet)
            username = getattr(request, 'user', None)
            if username and hasattr(username, 'username'):
                username = username.username
            else:
                username = 'anonymous'
            
            logger.info(f"API Request: {request.method} {request.path} - "
                       f"User: {username} - "
                       f"IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    def process_response(self, request, response):
        """Log response details"""
        if hasattr(request, '_start_time') and request.path.startswith('/api/'):
            duration = time.time() - request._start_time
            
            logger.info(f"API Response: {request.method} {request.path} - "
                       f"Status: {response.status_code} - "
                       f"Duration: {duration:.3f}s")
        
        return response