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
    """Unified request handler for all spiders with advanced features"""

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

    def __init__(self):
        self.session = None
        self.rate_limiters = {}  # Per-domain rate limiting
        self.cache = {}  # Response cache with TTL
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
        """Initialize the aiohttp session with connection pooling"""
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

    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()

    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key for URL and params"""
        cache_data = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _is_cache_valid(self, cached_item: Dict) -> bool:
        """Check if cached item is still valid (15-minute TTL)"""
        if not cached_item:
            return False
        cached_time = datetime.fromisoformat(cached_item['timestamp'])
        return datetime.now() - cached_time < timedelta(minutes=15)

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
        if not self.session:
            await self.initialize()

        domain = urlparse(url).netloc

        # Check cache first
        if use_cache and method == 'GET':
            cache_key = self._get_cache_key(url, params)
            if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
                logger.debug(f"Cache hit for {url}")
                return self.cache[cache_key]['data']

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

                    # Cache successful GET requests
                    if use_cache and method == 'GET' and response.status == 200:
                        cache_key = self._get_cache_key(url, params)
                        self.cache[cache_key] = {
                            'data': result,
                            'timestamp': datetime.now().isoformat()
                        }

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

        # All retries failed
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
            'cache_size': len(self.cache),
            'domains_tracked': len(self.rate_limiters),
            'error_counts': self.error_counts,
            'proxy_count': len(self.proxy_list),
            'current_proxy_index': self.current_proxy_index
        }


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