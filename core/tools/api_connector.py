"""
API Connector Tool - Universal API Integration

Provides universal API connectivity for agents to interact with external services.
Handles authentication, rate limiting, retries, and response processing.
"""

import os
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin
import hashlib

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls"""

    def __init__(self, max_calls: int, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    async def acquire(self):
        """Acquire a rate limit slot"""
        now = time.time()
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]

        if len(self.calls) >= self.max_calls:
            # Wait until we can make another call
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            return await self.acquire()

        self.calls.append(now)


class APIConnectorTool:
    """
    Universal API connector tool for making HTTP requests to various APIs.
    Handles authentication, rate limiting, retries, and error handling.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.APIConnector")
        self.is_configured = True  # Always available
        self.rate_limiters = {}
        self.session_cache = {}

        # Default configurations for common APIs
        self.api_configs = {
            'stripe': {
                'base_url': 'https://api.stripe.com/v1/',
                'auth_type': 'bearer',
                'rate_limit': {'max_calls': 100, 'window': 60}
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1/',
                'auth_type': 'bearer',
                'rate_limit': {'max_calls': 60, 'window': 60}
            },
            'github': {
                'base_url': 'https://api.github.com/',
                'auth_type': 'token',
                'rate_limit': {'max_calls': 60, 'window': 3600}
            },
            'slack': {
                'base_url': 'https://slack.com/api/',
                'auth_type': 'bearer',
                'rate_limit': {'max_calls': 50, 'window': 60}
            }
        }

        self.logger.info("API connector tool initialized")

    def configure_api(self,
                     api_name: str,
                     base_url: str,
                     auth_type: str = 'bearer',
                     max_calls: int = 60,
                     time_window: int = 60) -> Dict[str, Any]:
        """
        Configure a new API endpoint

        Args:
            api_name: Name of the API
            base_url: Base URL for the API
            auth_type: Authentication type (bearer, basic, api_key, etc.)
            max_calls: Maximum calls per time window
            time_window: Time window in seconds

        Returns:
            Configuration result
        """
        try:
            self.api_configs[api_name] = {
                'base_url': base_url,
                'auth_type': auth_type,
                'rate_limit': {'max_calls': max_calls, 'window': time_window}
            }

            # Initialize rate limiter
            self.rate_limiters[api_name] = RateLimiter(max_calls, time_window)

            self.logger.info(f"Configured API: {api_name}")

            return {
                'success': True,
                'api_name': api_name,
                'base_url': base_url,
                'configured_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to configure API {api_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_name': api_name
            }

    async def make_request(self,
                          api_name: str,
                          endpoint: str,
                          method: str = 'GET',
                          data: Optional[Dict] = None,
                          params: Optional[Dict] = None,
                          headers: Optional[Dict] = None,
                          auth_token: Optional[str] = None,
                          timeout: int = 30,
                          retries: int = 3) -> Dict[str, Any]:
        """
        Make an API request with authentication and rate limiting

        Args:
            api_name: Name of the configured API
            endpoint: API endpoint
            method: HTTP method
            data: Request body data
            params: URL parameters
            headers: Custom headers
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retries: Number of retry attempts

        Returns:
            API response data
        """
        if api_name not in self.api_configs:
            return {
                'success': False,
                'error': f'API {api_name} not configured',
                'api_name': api_name
            }

        config = self.api_configs[api_name]

        # Apply rate limiting
        if api_name in self.rate_limiters:
            await self.rate_limiters[api_name].acquire()
        else:
            rate_limit = config.get('rate_limit', {'max_calls': 60, 'window': 60})
            self.rate_limiters[api_name] = RateLimiter(
                rate_limit['max_calls'],
                rate_limit['window']
            )
            await self.rate_limiters[api_name].acquire()

        # Build URL
        base_url = config['base_url']
        url = urljoin(base_url, endpoint)

        # Prepare headers
        request_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'UnifiedDonkeyBetz-Agent/1.0'
        }

        if headers:
            request_headers.update(headers)

        # Add authentication
        if auth_token:
            auth_type = config.get('auth_type', 'bearer')
            if auth_type == 'bearer':
                request_headers['Authorization'] = f'Bearer {auth_token}'
            elif auth_type == 'token':
                request_headers['Authorization'] = f'token {auth_token}'
            elif auth_type == 'api_key':
                request_headers['X-API-Key'] = auth_token

        # Retry logic
        for attempt in range(retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    request_data = {
                        'method': method,
                        'url': url,
                        'headers': request_headers
                    }

                    if params:
                        request_data['params'] = params

                    if data and method in ['POST', 'PUT', 'PATCH']:
                        request_data['json'] = data

                    async with session.request(**request_data) as response:
                        response_data = {
                            'success': response.status < 400,
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'api_name': api_name,
                            'endpoint': endpoint,
                            'method': method,
                            'timestamp': datetime.now().isoformat()
                        }

                        try:
                            response_data['data'] = await response.json()
                        except (ValueError, TypeError, aiohttp.ContentTypeError) as e:
                            # Session 1103c: was a BARE 'except:' —
                            # narrowed to JSON-parse-specific errors
                            # so we don't accidentally swallow
                            # KeyboardInterrupt or unrelated
                            # exceptions during async body read.
                            self.logger.debug(
                                "api_connector: JSON parse failed for "
                                "%s %s (%s: %s) — falling back to text",
                                method, endpoint, type(e).__name__, e,
                            )
                            response_data['data'] = await response.text()

                        if response.status < 400:
                            self.logger.info(f"API call successful: {api_name} {method} {endpoint}")
                            return response_data
                        else:
                            self.logger.warning(
                                f"API call failed: {api_name} {method} {endpoint} - "
                                f"Status: {response.status}"
                            )

                            if attempt < retries and response.status >= 500:
                                # Retry on server errors
                                wait_time = 2 ** attempt
                                self.logger.info(f"Retrying in {wait_time} seconds...")
                                await asyncio.sleep(wait_time)
                                continue

                        return response_data

            except asyncio.TimeoutError:
                self.logger.error(f"API call timeout: {api_name} {method} {endpoint}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

                return {
                    'success': False,
                    'error': 'Request timeout',
                    'api_name': api_name,
                    'endpoint': endpoint,
                    'method': method
                }

            except Exception as e:
                self.logger.error(f"API call error: {api_name} {method} {endpoint} - {e}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue

                return {
                    'success': False,
                    'error': str(e),
                    'api_name': api_name,
                    'endpoint': endpoint,
                    'method': method
                }

        return {
            'success': False,
            'error': f'Max retries ({retries}) exceeded',
            'api_name': api_name,
            'endpoint': endpoint,
            'method': method
        }

    async def stripe_request(self,
                           endpoint: str,
                           method: str = 'GET',
                           data: Optional[Dict] = None,
                           stripe_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a Stripe API request

        Args:
            endpoint: Stripe API endpoint
            method: HTTP method
            data: Request data
            stripe_key: Stripe API key

        Returns:
            Stripe API response
        """
        if not stripe_key:
            stripe_key = os.getenv('STRIPE_API_KEY')

        if not stripe_key:
            return {
                'success': False,
                'error': 'Stripe API key not provided',
                'api_name': 'stripe'
            }

        return await self.make_request(
            api_name='stripe',
            endpoint=endpoint,
            method=method,
            data=data,
            auth_token=stripe_key
        )

    async def openai_request(self,
                           endpoint: str,
                           method: str = 'POST',
                           data: Optional[Dict] = None,
                           openai_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Make an OpenAI API request

        Args:
            endpoint: OpenAI API endpoint
            method: HTTP method
            data: Request data
            openai_key: OpenAI API key

        Returns:
            OpenAI API response
        """
        if not openai_key:
            openai_key = os.getenv('OPENAI_API_KEY')

        if not openai_key:
            return {
                'success': False,
                'error': 'OpenAI API key not provided',
                'api_name': 'openai'
            }

        return await self.make_request(
            api_name='openai',
            endpoint=endpoint,
            method=method,
            data=data,
            auth_token=openai_key
        )

    async def github_request(self,
                           endpoint: str,
                           method: str = 'GET',
                           data: Optional[Dict] = None,
                           github_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Make a GitHub API request

        Args:
            endpoint: GitHub API endpoint
            method: HTTP method
            data: Request data
            github_token: GitHub token

        Returns:
            GitHub API response
        """
        if not github_token:
            github_token = os.getenv('GITHUB_TOKEN')

        return await self.make_request(
            api_name='github',
            endpoint=endpoint,
            method=method,
            data=data,
            auth_token=github_token
        )

    def create_webhook_handler(self,
                              api_name: str,
                              secret: str,
                              handler_func) -> Dict[str, Any]:
        """
        Create a webhook handler for an API

        Args:
            api_name: Name of the API
            secret: Webhook secret for verification
            handler_func: Function to handle webhook data

        Returns:
            Webhook handler configuration
        """
        try:
            webhook_config = {
                'api_name': api_name,
                'secret': secret,
                'handler': handler_func,
                'created_at': datetime.now().isoformat()
            }

            self.logger.info(f"Created webhook handler for {api_name}")

            return {
                'success': True,
                'webhook_id': hashlib.md5(f"{api_name}_{secret}".encode()).hexdigest()[:8],
                'api_name': api_name,
                'created_at': webhook_config['created_at']
            }

        except Exception as e:
            self.logger.error(f"Failed to create webhook handler: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_name': api_name
            }

    def batch_request(self,
                     requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple API requests in batch

        Args:
            requests: List of request configurations

        Returns:
            List of responses
        """
        async def execute_batch():
            tasks = []
            for request_config in requests:
                task = self.make_request(**request_config)
                tasks.append(task)

            return await asyncio.gather(*tasks, return_exceptions=True)

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(execute_batch())

        # Convert exceptions to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'request_index': i
                })
            else:
                processed_results.append(result)

        return processed_results

    def get_api_status(self, api_name: str) -> Dict[str, Any]:
        """
        Get status information for an API

        Args:
            api_name: Name of the API

        Returns:
            API status information
        """
        if api_name not in self.api_configs:
            return {
                'configured': False,
                'api_name': api_name,
                'error': 'API not configured'
            }

        config = self.api_configs[api_name]
        rate_limiter = self.rate_limiters.get(api_name)

        status = {
            'configured': True,
            'api_name': api_name,
            'base_url': config['base_url'],
            'auth_type': config['auth_type'],
            'rate_limit': config.get('rate_limit', {}),
        }

        if rate_limiter:
            now = time.time()
            active_calls = len([
                call_time for call_time in rate_limiter.calls
                if now - call_time < rate_limiter.time_window
            ])
            status['rate_limit_status'] = {
                'active_calls': active_calls,
                'max_calls': rate_limiter.max_calls,
                'remaining_calls': rate_limiter.max_calls - active_calls
            }

        return status

    def get_statistics(self) -> Dict[str, Any]:
        """Get API connector statistics"""
        return {
            'configured_apis': list(self.api_configs.keys()),
            'api_count': len(self.api_configs),
            'rate_limiters': len(self.rate_limiters),
            'is_configured': self.is_configured,
            'default_timeout': 30,
            'default_retries': 3
        }