"""
API Key Management System for Spider Army
Phase 2: Authentication & API Integration
Manages API keys, rate limits, quotas, and automatic key rotation
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from cryptography.fernet import Fernet
from dataclasses import dataclass
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class APIQuota:
    """Track API quota and usage"""
    service: str
    total_quota: int
    used_quota: int
    reset_time: datetime
    rate_limit: int  # requests per second
    last_request_time: float

    @property
    def remaining(self) -> int:
        """Calculate remaining quota"""
        return self.total_quota - self.used_quota

    @property
    def is_exhausted(self) -> bool:
        """Check if quota is exhausted"""
        return self.remaining <= 0

    def should_reset(self) -> bool:
        """Check if quota should reset"""
        return datetime.now() >= self.reset_time


@dataclass
class APIHealth:
    """Track API health and errors"""
    service: str
    success_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    consecutive_errors: int = 0
    is_healthy: bool = True

    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        total = self.success_count + self.error_count
        return self.error_count / total if total > 0 else 0.0


class APIKeyVault:
    """Secure storage and management of API keys with encryption"""

    def __init__(self, vault_file: str = "api_keys.vault"):
        self.vault_file = Path(vault_file)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        self.keys = self._load_keys()
        self.quotas: Dict[str, APIQuota] = {}
        self.health: Dict[str, APIHealth] = {}
        self._initialize_quotas()
        self._initialize_health()

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for vault"""
        key_file = Path(".vault_key")

        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key

    def _load_keys(self) -> Dict[str, Optional[str]]:
        """Load API keys from environment and vault"""
        # First, try loading from environment variables
        keys = {
            # Financial APIs
            'alpha_vantage': os.environ.get('ALPHA_VANTAGE_KEY'),
            'polygon': os.environ.get('POLYGON_KEY'),
            'iex_cloud': os.environ.get('IEX_CLOUD_KEY'),
            'finnhub': os.environ.get('FINNHUB_KEY'),

            # News & Content APIs
            'newsapi': os.environ.get('NEWS_API_KEY'),
            'gnews': os.environ.get('GNEWS_API_KEY'),

            # Social Media APIs
            'twitter': os.environ.get('TWITTER_BEARER_TOKEN'),
            'reddit_client_id': os.environ.get('REDDIT_CLIENT_ID'),
            'reddit_client_secret': os.environ.get('REDDIT_CLIENT_SECRET'),
            'linkedin': os.environ.get('LINKEDIN_ACCESS_TOKEN'),
            'facebook': os.environ.get('FACEBOOK_ACCESS_TOKEN'),

            # Job Board APIs
            'indeed': os.environ.get('INDEED_API_KEY'),
            'adzuna_app_id': os.environ.get('ADZUNA_APP_ID'),
            'adzuna_app_key': os.environ.get('ADZUNA_APP_KEY'),
            'usajobs': os.environ.get('USAJOBS_API_KEY'),

            # AI/ML APIs
            'openai': os.environ.get('OPENAI_API_KEY'),
            'anthropic': os.environ.get('ANTHROPIC_API_KEY'),
            'huggingface': os.environ.get('HUGGINGFACE_TOKEN'),

            # Web Scraping Services
            'scrapingbee': os.environ.get('SCRAPINGBEE_API_KEY'),
            'scraperapi': os.environ.get('SCRAPERAPI_KEY'),
            'brightdata': os.environ.get('BRIGHTDATA_API_KEY'),
        }

        # Then, load from encrypted vault if exists
        if self.vault_file.exists():
            try:
                with open(self.vault_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                vault_keys = json.loads(decrypted_data.decode())

                # Merge with environment keys (environment takes precedence)
                for key, value in vault_keys.items():
                    if key not in keys or keys[key] is None:
                        keys[key] = value

            except Exception as e:
                logger.warning(f"Could not load vault file: {e}")

        return keys

    def save_keys(self):
        """Save keys to encrypted vault"""
        try:
            # Filter out None values
            keys_to_save = {k: v for k, v in self.keys.items() if v is not None}

            # Encrypt and save
            data = json.dumps(keys_to_save).encode()
            encrypted_data = self.cipher.encrypt(data)

            with open(self.vault_file, 'wb') as f:
                f.write(encrypted_data)

            # Set restrictive permissions
            os.chmod(self.vault_file, 0o600)

            logger.info(f"Saved {len(keys_to_save)} API keys to vault")

        except Exception as e:
            logger.error(f"Error saving keys to vault: {e}")

    def _initialize_quotas(self):
        """Initialize quota tracking for each API"""
        # Define default quotas (can be customized per API)
        default_quotas = {
            'alpha_vantage': {'total': 500, 'rate_limit': 5},  # 500/day, 5/min
            'polygon': {'total': 10000, 'rate_limit': 100},  # Free tier
            'newsapi': {'total': 500, 'rate_limit': 10},  # Developer tier
            'twitter': {'total': 500000, 'rate_limit': 300},  # v2 API
            'reddit': {'total': 60, 'rate_limit': 1},  # 60 requests/min
            'openai': {'total': 10000, 'rate_limit': 3},  # Tokens, not requests
            'coingecko': {'total': 50, 'rate_limit': 0.83},  # 50/min free tier
            'remoteok': {'total': 100, 'rate_limit': 1},  # Estimated
            'hackernews': {'total': 10000, 'rate_limit': 10},  # Very generous
        }

        for service, limits in default_quotas.items():
            self.quotas[service] = APIQuota(
                service=service,
                total_quota=limits['total'],
                used_quota=0,
                reset_time=datetime.now() + timedelta(hours=1),
                rate_limit=limits['rate_limit'],
                last_request_time=0
            )

    def _initialize_health(self):
        """Initialize health tracking for each API"""
        for service in self.quotas.keys():
            self.health[service] = APIHealth(service=service)

    def get_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        return self.keys.get(service)

    def set_key(self, service: str, key: str):
        """Set API key for a service"""
        self.keys[service] = key
        self.save_keys()

    async def can_make_request(self, service: str) -> bool:
        """Check if we can make a request to this service"""
        if service not in self.quotas:
            return True  # No quota tracking for this service

        quota = self.quotas[service]

        # Check if quota should reset
        if quota.should_reset():
            quota.used_quota = 0
            quota.reset_time = datetime.now() + timedelta(hours=1)

        # Check quota exhaustion
        if quota.is_exhausted:
            logger.warning(f"Quota exhausted for {service}: {quota.used_quota}/{quota.total_quota}")
            return False

        # Check rate limiting
        current_time = time.time()
        time_since_last = current_time - quota.last_request_time
        min_interval = 1.0 / quota.rate_limit if quota.rate_limit > 0 else 0

        if time_since_last < min_interval:
            # Need to wait
            wait_time = min_interval - time_since_last
            logger.debug(f"Rate limiting {service}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        return True

    def record_request(self, service: str, success: bool = True, error: Optional[str] = None):
        """Record API request for tracking"""
        # Update quota
        if service in self.quotas:
            quota = self.quotas[service]
            quota.used_quota += 1
            quota.last_request_time = time.time()

        # Update health
        if service in self.health:
            health = self.health[service]

            if success:
                health.success_count += 1
                health.consecutive_errors = 0
                health.is_healthy = True
            else:
                health.error_count += 1
                health.consecutive_errors += 1
                health.last_error = error
                health.last_error_time = datetime.now()

                # Mark unhealthy after 5 consecutive errors
                if health.consecutive_errors >= 5:
                    health.is_healthy = False
                    logger.error(f"API {service} marked unhealthy after {health.consecutive_errors} errors")

    def get_quota_status(self, service: str) -> Optional[Dict]:
        """Get quota status for a service"""
        if service not in self.quotas:
            return None

        quota = self.quotas[service]
        return {
            'service': service,
            'used': quota.used_quota,
            'total': quota.total_quota,
            'remaining': quota.remaining,
            'percentage_used': (quota.used_quota / quota.total_quota * 100) if quota.total_quota > 0 else 0,
            'reset_time': quota.reset_time.isoformat(),
            'is_exhausted': quota.is_exhausted
        }

    def get_health_status(self, service: str) -> Optional[Dict]:
        """Get health status for a service"""
        if service not in self.health:
            return None

        health = self.health[service]
        return {
            'service': service,
            'is_healthy': health.is_healthy,
            'success_count': health.success_count,
            'error_count': health.error_count,
            'error_rate': f"{health.error_rate:.2%}",
            'consecutive_errors': health.consecutive_errors,
            'last_error': health.last_error,
            'last_error_time': health.last_error_time.isoformat() if health.last_error_time else None
        }

    def get_all_status(self) -> Dict:
        """Get complete status of all APIs"""
        return {
            'keys_configured': {k: v is not None for k, v in self.keys.items()},
            'quotas': {s: self.get_quota_status(s) for s in self.quotas.keys()},
            'health': {s: self.get_health_status(s) for s in self.health.keys()},
            'summary': {
                'total_apis': len(self.keys),
                'configured_apis': sum(1 for v in self.keys.values() if v is not None),
                'healthy_apis': sum(1 for h in self.health.values() if h.is_healthy),
                'exhausted_quotas': sum(1 for q in self.quotas.values() if q.is_exhausted)
            }
        }

    def rotate_key(self, service: str, new_key: str):
        """Rotate API key for a service"""
        old_key = self.keys.get(service)
        self.keys[service] = new_key
        self.save_keys()

        # Reset health status for fresh start
        if service in self.health:
            self.health[service] = APIHealth(service=service)

        logger.info(f"Rotated API key for {service}")
        return old_key

    async def auto_rotate_unhealthy(self, backup_keys: Dict[str, List[str]]):
        """Automatically rotate keys for unhealthy APIs if backups available"""
        rotated = []

        for service, health in self.health.items():
            if not health.is_healthy and service in backup_keys:
                backups = backup_keys[service]
                current_key = self.keys.get(service)

                # Find next available backup key
                for backup_key in backups:
                    if backup_key != current_key:
                        self.rotate_key(service, backup_key)
                        rotated.append(service)
                        logger.info(f"Auto-rotated key for unhealthy API: {service}")
                        break

        return rotated


class APIRequestManager:
    """Manages API requests with authentication, rate limiting, and failover"""

    def __init__(self, vault: APIKeyVault):
        self.vault = vault
        self.fallback_apis = self._configure_fallbacks()
        self.last_request_metadata: Dict[str, Any] = {}
        self.last_fallback_metadata: Dict[str, Any] = {}

    def _reset_request_metadata(self, service: str) -> Dict[str, Any]:
        metadata = {
            'success': False,
            'service': service,
            'failure_type': None,
            'error': None,
            'error_type': None,
            'http_status': None,
            'quota_blocked': False,
            'rate_limited': False,
            'wait_seconds': 0.0,
        }
        self.last_request_metadata = metadata
        return metadata

    def _reset_fallback_metadata(self, service_type: str) -> Dict[str, Any]:
        metadata = {
            'success': False,
            'service_type': service_type,
            'fallback_used': False,
            'attempted_services': [],
            'failed_services': [],
            'failure_type': None,
            'last_error': None,
            'last_error_type': None,
        }
        self.last_fallback_metadata = metadata
        return metadata

    def _configure_fallbacks(self) -> Dict[str, List[str]]:
        """Configure fallback APIs for each service type"""
        return {
            'financial': ['alpha_vantage', 'polygon', 'iex_cloud', 'finnhub', 'yahoo_finance'],
            'news': ['newsapi', 'gnews', 'hackernews'],
            'social': ['twitter', 'reddit'],
            'jobs': ['remoteok', 'remotive', 'indeed', 'adzuna'],
            'crypto': ['coingecko', 'coinmarketcap', 'messari']
        }

    async def make_authenticated_request(
        self,
        service: str,
        url: str,
        method: str = 'GET',
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Any] = None
    ) -> Optional[Dict]:
        """Make authenticated API request with rate limiting and error handling"""
        metadata = self._reset_request_metadata(service)

        # Check if we can make the request
        if not await self.vault.can_make_request(service):
            logger.warning(f"Cannot make request to {service}: rate limit or quota exceeded")
            quota = self.vault.quotas.get(service)
            if quota and quota.is_exhausted:
                metadata['failure_type'] = 'quota_blocked'
                metadata['quota_blocked'] = True
                metadata['error'] = f"Quota exhausted for {service}"
                metadata['error_type'] = 'QuotaExceeded'
            else:
                metadata['failure_type'] = 'rate_limited'
                metadata['rate_limited'] = True
                metadata['error'] = f"Rate limited for {service}"
                metadata['error_type'] = 'RateLimited'
            return None

        # Get API key
        api_key = self.vault.get_key(service)
        if not api_key and self._requires_auth(service):
            logger.error(f"No API key configured for {service}")
            self.vault.record_request(service, success=False, error="No API key")
            metadata['failure_type'] = 'missing_auth'
            metadata['error'] = "No API key"
            metadata['error_type'] = 'MissingAuth'
            return None

        # Prepare headers with authentication
        request_headers = headers or {}
        request_headers.update(self._get_auth_headers(service, api_key))

        # Prepare params with API key if needed
        request_params = params or {}
        if self._uses_param_auth(service):
            request_params.update(self._get_auth_params(service, api_key))

        try:
            # Import web request layer
            from web_request_layer import web_request_layer

            # Make the request
            response = await web_request_layer.fetch(
                url=url,
                method=method,
                headers=request_headers,
                params=request_params,
                data=data
            )

            # Check response
            if response['status'] == 200:
                self.vault.record_request(service, success=True)
                metadata.update({
                    'success': True,
                    'failure_type': None,
                    'http_status': response['status'],
                    'error': None,
                    'error_type': None,
                })
                return response
            else:
                error_msg = f"HTTP {response['status']}"
                self.vault.record_request(service, success=False, error=error_msg)
                logger.error(f"API request to {service} failed: {error_msg}")
                metadata.update({
                    'failure_type': 'http_error',
                    'http_status': response['status'],
                    'error': error_msg,
                    'error_type': 'HTTPError',
                })
                return None

        except Exception as e:
            self.vault.record_request(service, success=False, error=str(e))
            logger.error(f"Error making request to {service}: {e}")
            metadata.update({
                'failure_type': 'exception',
                'error': str(e),
                'error_type': type(e).__name__,
            })
            return None

    def _requires_auth(self, service: str) -> bool:
        """Check if service requires authentication"""
        no_auth_services = ['coingecko', 'hackernews', 'remoteok']
        return service not in no_auth_services

    def _uses_param_auth(self, service: str) -> bool:
        """Check if service uses parameter-based auth"""
        param_auth_services = ['alpha_vantage', 'polygon', 'newsapi', 'adzuna']
        return service in param_auth_services

    def _get_auth_headers(self, service: str, api_key: str) -> Dict:
        """Get authentication headers for service"""
        if not api_key:
            return {}

        # Service-specific auth headers
        auth_headers = {
            'twitter': {'Authorization': f'Bearer {api_key}'},
            'reddit': {'Authorization': f'Bearer {api_key}'},
            'linkedin': {'Authorization': f'Bearer {api_key}'},
            'openai': {'Authorization': f'Bearer {api_key}'},
            'anthropic': {'X-API-Key': api_key},
            'huggingface': {'Authorization': f'Bearer {api_key}'},
            'scrapingbee': {'API-Key': api_key},
            'scraperapi': {'API-Key': api_key},
        }

        return auth_headers.get(service, {})

    def _get_auth_params(self, service: str, api_key: str) -> Dict:
        """Get authentication parameters for service"""
        if not api_key:
            return {}

        # Service-specific auth params
        auth_params = {
            'alpha_vantage': {'apikey': api_key},
            'polygon': {'apiKey': api_key},
            'newsapi': {'apiKey': api_key},
            'iex_cloud': {'token': api_key},
            'finnhub': {'token': api_key},
        }

        return auth_params.get(service, {})

    async def request_with_fallback(
        self,
        service_type: str,
        request_func,
        **kwargs
    ) -> Optional[Dict]:
        """Make request with automatic fallback to alternative APIs"""
        metadata = self._reset_fallback_metadata(service_type)

        if service_type not in self.fallback_apis:
            logger.error(f"Unknown service type: {service_type}")
            metadata.update({
                'failure_type': 'unknown_service_type',
                'last_error': f"Unknown service type: {service_type}",
                'last_error_type': 'UnknownServiceType',
            })
            return None

        fallback_services = self.fallback_apis[service_type]

        for service in fallback_services:
            metadata['attempted_services'].append(service)
            # Check if service is healthy
            health = self.vault.health.get(service)
            if health and not health.is_healthy:
                logger.debug(f"Skipping unhealthy service: {service}")
                failed_entry = {
                    'service': service,
                    'failure_type': 'unhealthy_service',
                    'error': 'Service marked unhealthy',
                    'error_type': 'UnhealthyService',
                }
                metadata['failed_services'].append(failed_entry)
                metadata['last_error'] = failed_entry['error']
                metadata['last_error_type'] = failed_entry['error_type']
                continue

            # Try the request
            result = await request_func(service, **kwargs)
            if result:
                metadata.update({
                    'success': True,
                    'fallback_used': len(metadata['attempted_services']) > 1,
                    'failure_type': None,
                    'last_error': None,
                    'last_error_type': None,
                })
                return result

            request_metadata = getattr(self, 'last_request_metadata', {}) or {}
            failed_entry = {
                'service': service,
                'failure_type': request_metadata.get('failure_type') or 'request_failed',
                'error': request_metadata.get('error'),
                'error_type': request_metadata.get('error_type'),
                'http_status': request_metadata.get('http_status'),
            }
            metadata['failed_services'].append(failed_entry)
            metadata['last_error'] = failed_entry['error']
            metadata['last_error_type'] = failed_entry['error_type']
            logger.warning(f"Request to {service} failed, trying fallback...")

        logger.error(f"All fallback services failed for {service_type}")
        metadata.update({
            'failure_type': 'fallback_exhausted',
            'fallback_used': len(metadata['attempted_services']) > 1,
            'success': False,
        })
        return None


# Singleton instance
api_vault = APIKeyVault()
api_manager = APIRequestManager(api_vault)


async def test_api_manager():
    """Test the API management system"""
    print("Testing API Key Management System\n" + "="*50)

    # Initialize vault
    vault = APIKeyVault()
    manager = APIRequestManager(vault)

    # Check configured keys
    status = vault.get_all_status()
    print(f"\nConfigured APIs: {status['summary']['configured_apis']}/{status['summary']['total_apis']}")

    # Show which APIs are configured
    print("\nAPI Configuration Status:")
    for api, configured in status['keys_configured'].items():
        if configured:
            print(f"  ✅ {api}")
        else:
            print(f"  ❌ {api}")

    # Test rate limiting
    print("\n\nTesting Rate Limiting...")
    for i in range(3):
        can_request = await vault.can_make_request('coingecko')
        print(f"  Request {i+1}: {'Allowed' if can_request else 'Blocked'}")
        if can_request:
            vault.record_request('coingecko', success=True)

    # Show quota status
    print("\n\nQuota Status:")
    for service in ['coingecko', 'newsapi', 'twitter']:
        quota = vault.get_quota_status(service)
        if quota:
            print(f"  {service}: {quota['used']}/{quota['total']} ({quota['percentage_used']:.1f}% used)")

    # Test actual API request (CoinGecko - no auth required)
    print("\n\nTesting Actual API Request (CoinGecko)...")
    response = await manager.make_authenticated_request(
        service='coingecko',
        url='https://api.coingecko.com/api/v3/simple/price',
        params={'ids': 'bitcoin', 'vs_currencies': 'usd'}
    )

    if response and response['json']:
        btc_price = response['json'].get('bitcoin', {}).get('usd')
        print(f"  ✅ Success! Bitcoin price: ${btc_price:,.2f}")
    else:
        print("  ❌ Request failed")

    # Show health status
    print("\n\nAPI Health Status:")
    for service in ['coingecko', 'newsapi', 'twitter']:
        health = vault.get_health_status(service)
        if health:
            status = "✅ Healthy" if health['is_healthy'] else "❌ Unhealthy"
            print(f"  {service}: {status} (Error rate: {health['error_rate']})")

    print("\n" + "="*50)
    print("API Management System Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_api_manager())
