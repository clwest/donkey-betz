"""
Web Request Layer for Spider Army
Implements real web scraping with rate limiting, retries, and proxy support
Phase 1: Transform spiders from mock to real data collection
"""

import aiohttp
import asyncio
import random
import time
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import hashlib
import json
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class WebRequestLayer:
    """Unified request handler for all spiders with advanced features

    Session 884: Fixed "Timeout context manager should be used inside a task" error
    by tracking which event loop the session was created in and recreating it
    when called from a different loop (common when asyncio.run() is used in Celery).
    """

    # User agent rotation pool
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/117.0 Firefox/121.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]

    # Redis cache TTLs by status code range
    CACHE_TTL_BY_STATUS = {
        200: 600,      # 10 min for success
        301: 86400,    # 24h for permanent redirects
        302: 86400,    # 24h for temp redirects (cache resolved URL)
        304: 600,      # 10 min for not-modified
        404: 1800,     # 30 min for not-found
        429: 60,       # 60s for rate-limited (back off)
        500: 60,       # 60s for server errors
        503: 60,       # 60s for service unavailable
    }
    CACHE_PREFIX = 'fetch'
    FLIGHT_PREFIX = 'fetchlock'

    def __init__(self):
        self.session = None
        self._session_loop = None  # Session 884: Track which event loop owns the session
        self.rate_limiters = {}  # Per-domain rate limiting
        self.cookie_jars = {}  # Per-domain cookie management
        self.proxy_list = self._load_proxies()
        self.current_proxy_index = 0
        self.request_count = 0
        self.error_counts = {}  # Track errors per domain

        # Global rate limiting
        self.global_rate_limit = 10  # requests per second
        self.last_request_time = 0

        # Retry configuration
        self.max_retries = 3
        self.base_backoff = 1  # seconds
        self.max_backoff = 60  # seconds

    def _load_proxies(self) -> List[Optional[str]]:
        """Load proxy list from environment or return None for direct connection"""
        proxy_endpoint = os.environ.get('PROXY_ENDPOINT')
        if proxy_endpoint:
            # In production, load from proxy service
            return [proxy_endpoint]
        return [None]  # Direct connection if no proxy configured

    async def initialize(self):
        """Initialize the aiohttp session with connection pooling

        Session 884: Check if session was created in a different event loop.
        When asyncio.run() is used (common in Celery tasks), each call creates
        a new event loop. Sessions from old loops must be recreated.
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        # Session 884: If session exists but was created in a different loop, close it
        # Session 902: Fixed memory leak - must close connector before discarding session
        if self.session and self._session_loop and current_loop and self._session_loop != current_loop:
            logger.debug("Session created in different event loop, recreating...")
            try:
                # connector.close() is synchronous and safe to call from any context
                # This properly closes TCP connections to prevent memory leaks
                if self.session.connector and not self.session.connector.closed:
                    self.session.connector.close()
                self.session = None
                self._session_loop = None
            except Exception as e:
                logger.warning(f"Error closing old session connector: {e}")
                self.session = None
                self._session_loop = None

        if not self.session:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool limit
                limit_per_host=10,  # Per-host connection limit
                ttl_dns_cache=300,  # DNS cache timeout
                enable_cleanup_closed=True
            )

            timeout = aiohttp.ClientTimeout(
                total=30,
                connect=10,
                sock_read=10
            )

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'Accept-Encoding': 'gzip, deflate, br'}
            )
            self._session_loop = current_loop

    async def close(self):
        """Clean up session and connector properly"""
        if self.session:
            try:
                # Session 902: Close connector first to release TCP connections
                if self.session.connector and not self.session.connector.closed:
                    self.session.connector.close()
                await self.session.close()
            except Exception as e:
                logger.warning(f"Error closing aiohttp session: {e}")
            finally:
                self.session = None
                self._session_loop = None

    def close_sync(self):
        """Synchronous close for use outside async context (e.g., cleanup)"""
        if self.session:
            try:
                if self.session.connector and not self.session.connector.closed:
                    self.session.connector.close()
            except Exception as e:
                logger.warning(f"Error in sync close: {e}")
            finally:
                self.session = None
                self._session_loop = None

    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key for URL and params (normalized)"""
        # Normalize: sort query params, strip fragments
        parsed = urlparse(url)
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            # Sort query params, strip tracking params
            from urllib.parse import parse_qs, urlencode
            qs = parse_qs(parsed.query)
            qs = {k: v for k, v in sorted(qs.items()) if not k.startswith('utm_')}
            if qs:
                normalized_url += '?' + urlencode(qs, doseq=True)
        cache_data = f"{normalized_url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_ttl_for_status(self, status_code: int) -> int:
        """Get cache TTL based on HTTP status code."""
        if status_code in self.CACHE_TTL_BY_STATUS:
            return self.CACHE_TTL_BY_STATUS[status_code]
        if 200 <= status_code < 300:
            return 600   # 10 min default for 2xx
        if 300 <= status_code < 400:
            return 86400  # 24h for redirects
        if 400 <= status_code < 500:
            return 1800   # 30 min for client errors
        return 60         # 60s for server errors

    def _redis_cache_get(self, cache_key: str) -> Optional[Dict]:
        """Get cached response from Redis."""
        try:
            from django.core.cache import cache
            return cache.get(f'{self.CACHE_PREFIX}:{cache_key}')
        except Exception:
            return None

    def _redis_cache_set(self, cache_key: str, data: Dict, status_code: int) -> None:
        """Store response in Redis with status-appropriate TTL."""
        try:
            from django.core.cache import cache
            ttl = self._get_ttl_for_status(status_code)
            cache.set(f'{self.CACHE_PREFIX}:{cache_key}', data, timeout=ttl)
        except Exception as e:
            logger.debug(f"Spider cache set failed (non-fatal): {e}")

    def _flight_lock_acquire(self, cache_key: str) -> bool:
        """Acquire single-flight lock for a URL. Returns True if acquired."""
        try:
            from django.core.cache import cache
            return cache.add(f'{self.FLIGHT_PREFIX}:{cache_key}', '1', timeout=120)
        except Exception:
            return True  # Proceed on lock failure

    def _flight_lock_release(self, cache_key: str) -> None:
        """Release single-flight lock."""
        try:
            from django.core.cache import cache
            cache.delete(f'{self.FLIGHT_PREFIX}:{cache_key}')
        except Exception as _e:
            logger.warning(
                "web_request_layer._flight_lock_release: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

    async def _enforce_rate_limit(self, domain: str):
        """Enforce per-domain and global rate limiting"""
        # Global rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1.0 / self.global_rate_limit:
            await asyncio.sleep((1.0 / self.global_rate_limit) - time_since_last)
        self.last_request_time = time.time()

        # Per-domain rate limiting
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = {
                'last_request': 0,
                'rate_limit': 2  # Default 2 requests per second per domain
            }

        limiter = self.rate_limiters[domain]
        time_since_last = current_time - limiter['last_request']
        if time_since_last < 1.0 / limiter['rate_limit']:
            await asyncio.sleep((1.0 / limiter['rate_limit']) - time_since_last)
        limiter['last_request'] = time.time()

    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the pool"""
        return random.choice(self.USER_AGENTS)

    def _get_next_proxy(self) -> Optional[str]:
        """Get next proxy from rotation list"""
        if not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy

    async def _handle_error_response(self, response: aiohttp.ClientResponse, domain: str):
        """Handle error responses with adaptive behavior"""
        status = response.status

        if domain not in self.error_counts:
            self.error_counts[domain] = {}

        if status not in self.error_counts[domain]:
            self.error_counts[domain][status] = 0
        self.error_counts[domain][status] += 1

        if status == 429:  # Too Many Requests
            # Increase rate limit for this domain
            if domain in self.rate_limiters:
                self.rate_limiters[domain]['rate_limit'] = max(
                    0.5,  # Minimum 0.5 requests per second
                    self.rate_limiters[domain]['rate_limit'] * 0.5
                )
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                await asyncio.sleep(int(retry_after))
            else:
                await asyncio.sleep(self.base_backoff * 2)

        elif status == 403:  # Forbidden
            # Try rotating proxy on next request
            logger.warning(f"403 Forbidden from {domain}, rotating proxy")
            self._get_next_proxy()

        elif status >= 500:  # Server errors
            # Exponential backoff
            await asyncio.sleep(self.base_backoff)

    async def fetch(
        self,
        url: str,
        method: str = 'GET',
        params: Dict = None,
        data: Dict = None,
        json_data: Dict = None,
        headers: Dict = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch URL with all the bells and whistles
        Returns: {'status': int, 'text': str, 'json': dict/None, 'headers': dict}
        """
        # Session 884: Always call initialize() to check for event loop changes
        # The previous check "if not self.session" missed cases where session
        # existed but was created in a different event loop (common in Celery)
        await self.initialize()

        domain = urlparse(url).netloc

        # Check Redis cache first
        cache_key = self._get_cache_key(url, params) if use_cache and method == 'GET' else None
        if cache_key:
            cached = self._redis_cache_get(cache_key)
            if cached is not None:
                logger.info("[fetch_cache] HIT url=%s", url[:100])
                return cached
            # Single-flight lock — prevent stampede on same URL
            if not self._flight_lock_acquire(cache_key):
                logger.info("[fetch_cache] DEDUP in-flight url=%s", url[:100])
                return {'status': 0, 'text': '', 'json': None, 'headers': {},
                        'url': url, 'dedup': True, 'timestamp': datetime.now().isoformat()}

        # Prepare headers
        request_headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if headers:
            request_headers.update(headers)

        # Prepare proxy
        proxy = self._get_next_proxy()

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Rate limiting
                await self._enforce_rate_limit(domain)

                # Make request
                async with self.session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    proxy=proxy,
                    ssl=True,  # Enable SSL verification for production
                    **kwargs
                ) as response:

                    # Handle errors
                    if response.status >= 400:
                        await self._handle_error_response(response, domain)
                        if attempt < self.max_retries - 1:
                            backoff = min(
                                self.base_backoff * (2 ** attempt),
                                self.max_backoff
                            )
                            logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {backoff}s")
                            await asyncio.sleep(backoff)
                            continue

                    # Success! Process response
                    text = await response.text()

                    try:
                        json_response = await response.json()
                    except:
                        json_response = None

                    result = {
                        'status': response.status,
                        'text': text,
                        'json': json_response,
                        'headers': dict(response.headers),
                        'url': str(response.url),
                        'timestamp': datetime.now().isoformat()
                    }

                    # Cache GET responses in Redis (all status codes, with appropriate TTLs)
                    if cache_key:
                        self._redis_cache_set(cache_key, result, response.status)
                        self._flight_lock_release(cache_key)

                    # Store cookies
                    if response.cookies:
                        if domain not in self.cookie_jars:
                            self.cookie_jars[domain] = {}
                        for cookie in response.cookies.values():
                            self.cookie_jars[domain][cookie.key] = cookie.value

                    logger.info(f"Successfully fetched {url} (status: {response.status})")
                    return result

            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {url} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.base_backoff * (2 ** attempt))
                    continue

            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)} (attempt {attempt + 1})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.base_backoff * (2 ** attempt))
                    continue

        # All retries failed — release flight lock
        if cache_key:
            self._flight_lock_release(cache_key)
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return {
            'status': 0,
            'text': '',
            'json': None,
            'headers': {},
            'url': url,
            'error': f'Failed after {self.max_retries} attempts',
            'timestamp': datetime.now().isoformat()
        }

    async def fetch_batch(self, urls: List[str], max_concurrent: int = 5) -> List[Dict]:
        """Fetch multiple URLs concurrently with rate limiting"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def fetch_with_semaphore(url):
            async with semaphore:
                return await self.fetch(url)

        tasks = [fetch_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)

    def get_statistics(self) -> Dict:
        """Get request statistics"""
        return {
            'total_requests': self.request_count,
            'cache_backend': 'redis',
            'domains_tracked': len(self.rate_limiters),
            'error_counts': self.error_counts,
            'proxy_count': len(self.proxy_list),
            'current_proxy_index': self.current_proxy_index
        }


# ── Synchronous cached_get() for specialized spiders ────────────────
# Drop-in replacement for `requests.get()` that adds Redis caching.
# Usage:  from ai_core.spiders.web_request_layer import cached_get
#         response = cached_get(url, params={...}, timeout=10)
#         response.status_code, response.json(), response.text  # same API

class _CachedResponse:
    """Lightweight response object matching requests.Response interface."""
    __slots__ = ('status_code', 'text', '_json', 'headers', 'url', 'ok')

    def __init__(self, status_code, text, json_data, headers, url):
        self.status_code = status_code
        self.text = text
        self._json = json_data
        self.headers = headers or {}
        self.url = url
        self.ok = 200 <= status_code < 300

    def json(self):
        if self._json is not None:
            return self._json
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


# TTLs for sync cached_get (mirrors WebRequestLayer)
_SYNC_TTL = {200: 600, 301: 86400, 302: 86400, 404: 1800, 429: 60, 500: 60, 503: 60}
_CACHE_PREFIX = 'sfetch'  # "sync fetch" — separate from async fetch prefix


def _sync_cache_key(url: str, params: dict = None) -> str:
    """Normalized cache key for sync requests."""
    parsed = urlparse(url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        from urllib.parse import parse_qs, urlencode
        qs = {k: v for k, v in sorted(parse_qs(parsed.query).items()) if not k.startswith('utm_')}
        if qs:
            normalized += '?' + urlencode(qs, doseq=True)
    raw = f"{normalized}:{json.dumps(params or {}, sort_keys=True)}"
    return hashlib.md5(raw.encode()).hexdigest()


def _sync_ttl(status_code: int) -> int:
    if status_code in _SYNC_TTL:
        return _SYNC_TTL[status_code]
    if 200 <= status_code < 300:
        return 600
    if 300 <= status_code < 400:
        return 86400
    if 400 <= status_code < 500:
        return 1800
    return 60


def cached_get(url: str, params: dict = None, headers: dict = None,
               timeout: int = 15, **kwargs) -> _CachedResponse:
    """
    Drop-in replacement for requests.get() with Redis caching.
    Returns a _CachedResponse with .status_code, .text, .json(), .ok.
    """
    import requests as _requests

    cache_key = _sync_cache_key(url, params)
    full_key = f'{_CACHE_PREFIX}:{cache_key}'

    # Check cache
    try:
        from django.core.cache import cache
        cached = cache.get(full_key)
        if cached is not None:
            logger.info("[spider_cache] HIT url=%s status=%s", url[:100], cached.get('status'))
            return _CachedResponse(
                status_code=cached['status'],
                text=cached.get('text', ''),
                json_data=cached.get('json'),
                headers=cached.get('headers', {}),
                url=cached.get('url', url),
            )
    except Exception:
        pass  # Cache unavailable — fall through to live request

    # Live request (cache miss)
    logger.info("[spider_cache] MISS url=%s", url[:100])
    resp = _requests.get(url, params=params, headers=headers, timeout=timeout, **kwargs)

    # Build cacheable payload (cap text at 500KB to avoid Redis bloat)
    text = resp.text[:512_000] if len(resp.text) > 512_000 else resp.text
    try:
        json_data = resp.json()
    except Exception:
        json_data = None

    payload = {
        'status': resp.status_code,
        'text': text,
        'json': json_data,
        'headers': dict(resp.headers),
        'url': str(resp.url),
    }

    # Store in cache
    try:
        from django.core.cache import cache
        cache.set(full_key, payload, timeout=_sync_ttl(resp.status_code))
    except Exception:
        pass  # Cache write failure is non-fatal

    return _CachedResponse(
        status_code=resp.status_code,
        text=text,
        json_data=json_data,
        headers=dict(resp.headers),
        url=str(resp.url),
    )


# Singleton instance
web_request_layer = WebRequestLayer()


async def test_web_request_layer():
    """Test the web request layer with real URLs"""
    layer = WebRequestLayer()
    await layer.initialize()

    # Test single fetch
    print("Testing single fetch...")
    result = await layer.fetch('https://api.github.com/repos/python/cpython')
    print(f"Status: {result['status']}")
    if result['json']:
        print(f"Stars: {result['json'].get('stargazers_count', 'N/A')}")

    # Test batch fetch
    print("\nTesting batch fetch...")
    urls = [
        'https://api.github.com/repos/django/django',
        'https://api.github.com/repos/pallets/flask',
        'https://api.github.com/repos/encode/django-rest-framework'
    ]
    results = await layer.fetch_batch(urls)
    for r in results:
        if r['json']:
            print(f"{r['json'].get('name', 'Unknown')}: {r['json'].get('stargazers_count', 0)} stars")

    # Print statistics
    print("\nStatistics:")
    print(json.dumps(layer.get_statistics(), indent=2))

    await layer.close()


if __name__ == "__main__":
    asyncio.run(test_web_request_layer())