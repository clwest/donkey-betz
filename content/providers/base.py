"""
Base Provider for External API Integrations
==========================================

Provides a standardized base class for all external API providers with:
- Consistent error handling
- Retry logic with exponential backoff
- Rate limit handling
- Timeout management
- Logging

Session 184: Created as part of Phase 3 Architecture Improvements (Task 3.6)
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(self, message: str, status_code: int = None, details: str = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class RateLimitError(ProviderError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class AuthenticationError(ProviderError):
    """Raised when API authentication fails."""
    pass


class ValidationError(ProviderError):
    """Raised when request validation fails."""
    pass


class BaseProvider(ABC):
    """
    Abstract base class for all external API providers.

    Provides standardized:
    - HTTP request handling with retries
    - Error handling and logging
    - Rate limit management
    - Timeout configuration

    Subclasses must implement:
    - provider_name: Name for logging
    - api_key: API key for authentication
    - base_url: Base URL for API requests

    Example usage:
        class MyProvider(BaseProvider):
            @property
            def provider_name(self) -> str:
                return "MyAPI"

            @property
            def api_key(self) -> str:
                return settings.MY_API_KEY

            @property
            def base_url(self) -> str:
                return "https://api.example.com"

            def generate_content(self, prompt: str) -> Dict[str, Any]:
                return self._make_request(
                    "POST",
                    f"{self.base_url}/generate",
                    json={"prompt": prompt}
                )
    """

    def __init__(self):
        """Initialize the provider with default configuration."""
        self._timeout = getattr(settings, 'API_TIMEOUT', 60)
        self._max_retries = getattr(settings, 'API_MAX_RETRIES', 3)
        self._retry_delay = getattr(settings, 'API_RETRY_DELAY', 1)
        self._session = requests.Session()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider for logging and error messages."""
        pass

    @property
    @abstractmethod
    def api_key(self) -> str:
        """API key for authentication."""
        pass

    @property
    def base_url(self) -> str:
        """Base URL for API requests. Override in subclasses."""
        return ""

    @property
    def timeout(self) -> int:
        """Request timeout in seconds."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        """Set request timeout."""
        self._timeout = max(1, value)

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        return self._max_retries

    @max_retries.setter
    def max_retries(self, value: int):
        """Set maximum retries."""
        self._max_retries = max(0, value)

    def _get_headers(self) -> Dict[str, str]:
        """
        Get default headers for API requests.

        Override in subclasses to customize authentication.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        json: Dict[str, Any] = None,
        data: Any = None,
        files: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        timeout: int = None,
        stream: bool = False,
    ) -> requests.Response:
        """
        Make HTTP request with retry logic and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Full URL for the request
            headers: Additional headers (merged with defaults)
            json: JSON body data
            data: Form data
            files: File uploads
            params: URL query parameters
            timeout: Request timeout (uses default if not specified)
            stream: Whether to stream the response

        Returns:
            requests.Response object

        Raises:
            RateLimitError: When rate limited
            AuthenticationError: When auth fails
            ValidationError: When request validation fails
            ProviderError: For other API errors
        """
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        # Don't set Content-Type for file uploads
        if files:
            request_headers.pop('Content-Type', None)

        request_timeout = timeout or self._timeout

        for attempt in range(self._max_retries):
            try:
                logger.debug(f"{self.provider_name}: {method} {url} (attempt {attempt + 1})")

                response = self._session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                    timeout=request_timeout,
                    stream=stream,
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(
                        f"{self.provider_name}: Rate limited, waiting {retry_after}s"
                    )
                    if attempt < self._max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    raise RateLimitError(retry_after)

                # Handle authentication errors
                if response.status_code in (401, 403):
                    raise AuthenticationError(
                        f"{self.provider_name}: Authentication failed",
                        status_code=response.status_code,
                        details=response.text[:500]
                    )

                # Handle validation errors
                if response.status_code == 400:
                    raise ValidationError(
                        f"{self.provider_name}: Invalid request",
                        status_code=response.status_code,
                        details=response.text[:500]
                    )

                # Handle server errors with retry
                if response.status_code >= 500:
                    logger.warning(
                        f"{self.provider_name}: Server error {response.status_code}"
                    )
                    if attempt < self._max_retries - 1:
                        time.sleep(self._retry_delay * (attempt + 1))
                        continue
                    response.raise_for_status()

                return response

            except requests.exceptions.Timeout:
                logger.warning(
                    f"{self.provider_name}: Timeout on attempt {attempt + 1}"
                )
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise ProviderError(
                        f"{self.provider_name}: Request timed out after {request_timeout}s"
                    )

            except requests.exceptions.ConnectionError as e:
                logger.warning(
                    f"{self.provider_name}: Connection error on attempt {attempt + 1}"
                )
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise ProviderError(
                        f"{self.provider_name}: Connection failed",
                        details=str(e)
                    )

            except (RateLimitError, AuthenticationError, ValidationError):
                raise

            except requests.exceptions.RequestException as e:
                logger.error(f"{self.provider_name}: Request failed: {e}")
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise ProviderError(
                        f"{self.provider_name}: Request failed",
                        details=str(e)
                    )

    def _handle_response(
        self,
        response: requests.Response,
        success_codes: tuple = (200, 201)
    ) -> Dict[str, Any]:
        """
        Handle API response and return standardized result.

        Args:
            response: requests.Response object
            success_codes: Tuple of successful HTTP status codes

        Returns:
            Dictionary with 'success', 'data' or 'error' keys
        """
        try:
            data = response.json() if response.content else {}
        except ValueError:
            data = {'raw_content': response.text[:1000]}

        if response.status_code in success_codes:
            return {
                'success': True,
                'data': data,
                'status_code': response.status_code,
            }
        else:
            error_message = data.get('error', data.get('message', response.text[:500]))
            return {
                'success': False,
                'error': error_message,
                'status_code': response.status_code,
                'details': data,
            }

    def _format_error_response(
        self,
        error: Exception,
        operation: str = None
    ) -> Dict[str, Any]:
        """
        Format exception into standardized error response.

        Args:
            error: Exception that occurred
            operation: Name of the operation that failed

        Returns:
            Standardized error dictionary
        """
        if isinstance(error, ProviderError):
            return {
                'success': False,
                'error': error.message,
                'status_code': error.status_code,
                'details': error.details,
                'provider': self.provider_name,
                'operation': operation,
            }
        else:
            return {
                'success': False,
                'error': str(error),
                'provider': self.provider_name,
                'operation': operation,
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the provider.

        Override in subclasses to implement provider-specific health checks.

        Returns:
            Dictionary with 'healthy' boolean and optional details
        """
        return {
            'healthy': bool(self.api_key),
            'provider': self.provider_name,
            'has_api_key': bool(self.api_key),
        }

    def get_usage(self) -> Dict[str, Any]:
        """
        Get current API usage/credits.

        Override in subclasses that support usage tracking.

        Returns:
            Dictionary with usage information
        """
        return {
            'provider': self.provider_name,
            'usage_tracking': 'not_implemented',
        }
