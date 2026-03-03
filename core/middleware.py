"""
Custom middleware for the Unified Donkey Betz Platform.
Session 111: Added RangeRequestMiddleware for video streaming support
"""
import logging
import os
import re
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
from django.http import StreamingHttpResponse, HttpResponse, FileResponse
from django.core.files.storage import default_storage


class DisableCSRFForAuthEndpoints(MiddlewareMixin):
    """
    Disable CSRF protection for API endpoints.

    Session 115: Enhanced to skip CSRF for:
    1. Any request with X-API-Key header (mobile apps)
    2. Any request with Authorization token header
    3. Specific auth endpoints
    """

    # Webhook paths that legitimately need CSRF exemption without auth headers
    WEBHOOK_PATHS = {
        '/api/stripe/webhook/',
        '/api/discord/verify-link-code/',
    }

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Session 1088: Targeted CSRF exemption — only exempt when token/API-key
        # auth is present, NOT blanket /api/ exemption (was a CSRF vulnerability).
        # Browser session-auth requests now get CSRF protection on write operations.

        # Check if request has API key authentication (mobile apps)
        if request.META.get('HTTP_X_API_KEY'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            return None

        # Check if request has token authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token ') or auth_header.startswith('Bearer '):
            setattr(request, '_dont_enforce_csrf_checks', True)
            return None

        # Exempt known webhook paths (external services that can't send CSRF tokens)
        if request.path in self.WEBHOOK_PATHS:
            setattr(request, '_dont_enforce_csrf_checks', True)
            return None

        # List of paths that should be exempt from CSRF (backwards compatibility)
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


class RangeRequestMiddleware:
    """
    Middleware to handle HTTP range requests for video streaming.
    iOS AVPlayer requires range request support to stream videos.
    Session 111: Galleries & Assets - Video Playback
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process media file requests (videos, images, etc.)
        if not request.path.startswith('/media/'):
            return response

        # Check if this is a range request
        range_header = request.META.get('HTTP_RANGE', '').strip()
        if not range_header:
            return response

        # Only handle FileResponse and successful responses
        if not isinstance(response, (FileResponse, StreamingHttpResponse, HttpResponse)):
            return response

        if response.status_code != 200:
            return response

        # Parse range header (format: "bytes=start-end")
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not range_match:
            return response

        # Get file path from request
        file_path = request.path.replace('/media/', '', 1)

        try:
            # Check if file exists
            if not default_storage.exists(file_path):
                return response

            # Get file size
            file_size = default_storage.size(file_path)

            # Parse range
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

            # Validate range
            if start >= file_size or end >= file_size or start > end:
                response = HttpResponse(status=416)  # Range Not Satisfiable
                response['Content-Range'] = f'bytes */{file_size}'
                return response

            # Calculate content length
            length = end - start + 1

            # Open file and seek to start position
            file_obj = default_storage.open(file_path, 'rb')
            file_obj.seek(start)

            # Create streaming response
            def file_iterator(file_obj, chunk_size=8192, length=length):
                """Generator to stream file in chunks"""
                remaining = length
                while remaining > 0:
                    chunk_to_read = min(chunk_size, remaining)
                    data = file_obj.read(chunk_to_read)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
                file_obj.close()

            # Create response with partial content
            response = StreamingHttpResponse(
                file_iterator(file_obj, length=length),
                status=206,  # Partial Content
                content_type=self._get_content_type(file_path)
            )

            # Set required headers for range response
            response['Content-Length'] = str(length)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'

            # Set caching headers for better performance
            response['Cache-Control'] = 'public, max-age=3600'

            return response

        except Exception as e:
            # If anything fails, return original response
            logger.warning(f"Range request error: {e}")
            return response

    def _get_content_type(self, file_path):
        """Get content type based on file extension"""
        ext = os.path.splitext(file_path)[1].lower()

        content_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.ogg': 'video/ogg',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.m4v': 'video/x-m4v',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }

        return content_types.get(ext, 'application/octet-stream')