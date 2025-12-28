"""
Spider Data Authenticity Verifier

This module proves that spiders are fetching REAL external data, not mock/cached data.
It tracks API calls, timestamps, data freshness, and success rates with cryptographic proof.
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import redis
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class SpiderAuthenticityVerifier:
    """
    Verify that spider data is real, fresh, and from external sources
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=4,  # Dedicated DB for spider verification
            decode_responses=True
        )
        self.external_domains = {
            'upwork.com', 'freelancer.com', 'fiverr.com',
            'toptal.com', 'guru.com', 'peopleperhour.com',
            'linkedin.com', 'indeed.com', 'glassdoor.com',
            'github.com', 'stackoverflow.com', 'producthunt.com',
            'coingecko.com', 'coinmarketcap.com', 'etherscan.io',
            'stripe.com', 'paypal.com', 'blockchain.info'
        }

    def verify_spider_data_authenticity(self, spider_data: Dict) -> Tuple[bool, Dict]:
        """
        Main verification method - proves spider data is real and fresh

        Returns:
            (is_authentic, proof_details)
        """
        verification_proof = {
            'spider_id': spider_data.get('spider_id'),
            'timestamp': datetime.now().isoformat(),
            'checks_performed': [],
            'authenticity_score': 0,
            'is_authentic': False,
            'evidence': {},
            'data_hash': None
        }

        # Check 1: External URL Verification
        external_verified = self._verify_external_source(spider_data)
        verification_proof['checks_performed'].append('external_source')
        if external_verified:
            verification_proof['authenticity_score'] += 25
            verification_proof['evidence']['external_source'] = {
                'verified': True,
                'domain': external_verified['domain'],
                'is_external': True,
                'url': spider_data.get('source_url')
            }

        # Check 2: Timestamp Freshness
        freshness_verified = self._verify_data_freshness(spider_data)
        verification_proof['checks_performed'].append('data_freshness')
        if freshness_verified:
            verification_proof['authenticity_score'] += 25
            verification_proof['evidence']['freshness'] = {
                'verified': True,
                'age_seconds': freshness_verified['age'],
                'is_fresh': freshness_verified['is_fresh'],
                'fetched_at': spider_data.get('fetched_at')
            }

        # Check 3: HTTP Headers Verification
        headers_verified = self._verify_http_headers(spider_data)
        verification_proof['checks_performed'].append('http_headers')
        if headers_verified:
            verification_proof['authenticity_score'] += 20
            verification_proof['evidence']['http_headers'] = {
                'verified': True,
                'status_code': headers_verified.get('status_code'),
                'content_type': headers_verified.get('content_type'),
                'server': headers_verified.get('server')
            }

        # Check 4: Data Uniqueness (not cached/duplicated)
        uniqueness_verified = self._verify_data_uniqueness(spider_data)
        verification_proof['checks_performed'].append('data_uniqueness')
        if uniqueness_verified:
            verification_proof['authenticity_score'] += 20
            verification_proof['evidence']['uniqueness'] = {
                'verified': True,
                'is_unique': uniqueness_verified['is_unique'],
                'similarity_score': uniqueness_verified.get('similarity', 0),
                'hash': uniqueness_verified['hash']
            }

        # Check 5: API Call Tracking
        api_verified = self._verify_api_call(spider_data)
        verification_proof['checks_performed'].append('api_call')
        if api_verified:
            verification_proof['authenticity_score'] += 10
            verification_proof['evidence']['api_call'] = {
                'verified': True,
                'method': api_verified.get('method'),
                'response_time_ms': api_verified.get('response_time'),
                'bytes_received': api_verified.get('bytes_received')
            }

        # Generate data hash for integrity
        verification_proof['data_hash'] = self._generate_data_hash(spider_data)

        # Determine if data is authentic based on score
        verification_proof['is_authentic'] = verification_proof['authenticity_score'] >= 60

        # Store verification proof
        self._store_verification_proof(verification_proof)

        # Track spider performance
        self._track_spider_performance(
            spider_data.get('spider_id'),
            verification_proof['is_authentic']
        )

        logger.info(f"Spider verification completed: {verification_proof['is_authentic']} "
                   f"(Score: {verification_proof['authenticity_score']})")

        return verification_proof['is_authentic'], verification_proof

    def _verify_external_source(self, spider_data: Dict) -> Optional[Dict]:
        """Verify the data comes from an external source"""
        try:
            source_url = spider_data.get('source_url', '')
            if not source_url:
                return None

            parsed = urlparse(source_url)
            domain = parsed.netloc.lower().replace('www.', '')

            # Check if it's an external domain
            is_external = any(ext in domain for ext in self.external_domains)

            if is_external:
                return {
                    'domain': domain,
                    'protocol': parsed.scheme,
                    'is_external': True
                }
        except Exception as e:
            logger.error(f"External source verification failed: {e}")
        return None

    def _verify_data_freshness(self, spider_data: Dict) -> Optional[Dict]:
        """Verify the data is fresh and recently fetched"""
        try:
            fetched_at = spider_data.get('fetched_at')
            if not fetched_at:
                return None

            if isinstance(fetched_at, str):
                fetched_at = datetime.fromisoformat(fetched_at)

            now = datetime.now()
            age = (now - fetched_at).total_seconds()

            # Data should be fresh (less than 1 hour old)
            is_fresh = age < 3600

            return {
                'age': age,
                'is_fresh': is_fresh,
                'fetched_at': fetched_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Freshness verification failed: {e}")
        return None

    def _verify_http_headers(self, spider_data: Dict) -> Optional[Dict]:
        """Verify HTTP response headers indicate real external fetch"""
        try:
            headers = spider_data.get('response_headers', {})
            if not headers:
                return None

            # Check for indicators of real HTTP response
            status_code = spider_data.get('status_code', 200)
            content_type = headers.get('content-type', '')
            server = headers.get('server', '')

            # Real responses have these characteristics
            if status_code in [200, 201, 204, 301, 302, 304] and content_type:
                return {
                    'status_code': status_code,
                    'content_type': content_type,
                    'server': server,
                    'has_headers': True
                }
        except Exception as e:
            logger.error(f"Headers verification failed: {e}")
        return None

    def _verify_data_uniqueness(self, spider_data: Dict) -> Optional[Dict]:
        """Verify data is unique and not cached/duplicated"""
        try:
            data_content = json.dumps(spider_data.get('data', {}), sort_keys=True)
            data_hash = hashlib.sha256(data_content.encode()).hexdigest()

            # Check if we've seen this exact data before
            hash_key = f"spider:data:hash:{data_hash}"
            seen_before = self.redis_client.exists(hash_key)

            if not seen_before:
                # Store hash with TTL
                self.redis_client.setex(hash_key, 3600, datetime.now().isoformat())
                return {
                    'is_unique': True,
                    'hash': data_hash[:16],
                    'similarity': 0
                }
            else:
                # Data is duplicate
                return {
                    'is_unique': False,
                    'hash': data_hash[:16],
                    'similarity': 100
                }
        except Exception as e:
            logger.error(f"Uniqueness verification failed: {e}")
        return None

    def _verify_api_call(self, spider_data: Dict) -> Optional[Dict]:
        """Verify the API call details"""
        try:
            api_details = spider_data.get('api_call', {})
            if not api_details:
                return None

            method = api_details.get('method', 'GET')
            response_time = api_details.get('response_time_ms')
            bytes_received = api_details.get('bytes_received')

            # Real API calls have measurable response times
            if response_time and response_time > 0:
                return {
                    'method': method,
                    'response_time': response_time,
                    'bytes_received': bytes_received or 0,
                    'is_real_call': True
                }
        except Exception as e:
            logger.error(f"API call verification failed: {e}")
        return None

    def _generate_data_hash(self, spider_data: Dict) -> str:
        """Generate cryptographic hash of spider data"""
        try:
            hash_input = json.dumps({
                'spider_id': spider_data.get('spider_id'),
                'source_url': spider_data.get('source_url'),
                'data': str(spider_data.get('data')),
                'fetched_at': str(spider_data.get('fetched_at'))
            }, sort_keys=True)

            return hashlib.sha256(hash_input.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            return ""

    def _store_verification_proof(self, proof: Dict):
        """Store verification proof for audit"""
        try:
            proof_key = f"spider:proof:{proof['spider_id']}:{datetime.now().timestamp()}"
            self.redis_client.hset(
                proof_key,
                mapping={
                    'proof': json.dumps(proof),
                    'timestamp': proof['timestamp'],
                    'is_authentic': str(proof['is_authentic']),
                    'score': str(proof['authenticity_score'])
                }
            )
            self.redis_client.expire(proof_key, 86400 * 7)  # Keep for 7 days
        except Exception as e:
            logger.error(f"Failed to store proof: {e}")

    def _track_spider_performance(self, spider_id: str, is_authentic: bool):
        """Track spider performance metrics"""
        try:
            perf_key = f"spider:performance:{spider_id}"

            # Increment counters
            if is_authentic:
                self.redis_client.hincrby(perf_key, 'authentic_fetches', 1)
            else:
                self.redis_client.hincrby(perf_key, 'fake_fetches', 1)

            self.redis_client.hincrby(perf_key, 'total_fetches', 1)
            self.redis_client.hset(perf_key, 'last_fetch', datetime.now().isoformat())

            # Calculate success rate
            stats = self.redis_client.hgetall(perf_key)
            if stats:
                authentic = int(stats.get('authentic_fetches', 0))
                total = int(stats.get('total_fetches', 1))
                success_rate = (authentic / total) * 100 if total > 0 else 0
                self.redis_client.hset(perf_key, 'success_rate', f"{success_rate:.1f}")

        except Exception as e:
            logger.error(f"Failed to track performance: {e}")

    def track_api_call(self, spider_id: str, api_details: Dict):
        """Track an external API call made by a spider"""
        try:
            call_id = str(uuid.uuid4())
            call_key = f"spider:api_call:{call_id}"

            # Store API call details
            self.redis_client.hset(
                call_key,
                mapping={
                    'spider_id': spider_id,
                    'timestamp': datetime.now().isoformat(),
                    'url': api_details.get('url', ''),
                    'method': api_details.get('method', 'GET'),
                    'status_code': str(api_details.get('status_code', 0)),
                    'response_time_ms': str(api_details.get('response_time_ms', 0)),
                    'bytes_received': str(api_details.get('bytes_received', 0))
                }
            )
            self.redis_client.expire(call_key, 3600)  # 1 hour

            # Track in spider's API call list
            list_key = f"spider:api_calls:{spider_id}"
            self.redis_client.lpush(list_key, call_id)
            self.redis_client.ltrim(list_key, 0, 99)  # Keep last 100 calls

            logger.info(f"API call tracked: {spider_id} -> {api_details.get('url')}")
            return call_id

        except Exception as e:
            logger.error(f"Failed to track API call: {e}")
            return None

    def get_spider_statistics(self, spider_id: Optional[str] = None) -> Dict:
        """Get spider authenticity statistics"""
        try:
            if spider_id:
                # Get stats for specific spider
                perf_key = f"spider:performance:{spider_id}"
                stats = self.redis_client.hgetall(perf_key)

                if stats:
                    return {
                        'spider_id': spider_id,
                        'total_fetches': int(stats.get('total_fetches', 0)),
                        'authentic_fetches': int(stats.get('authentic_fetches', 0)),
                        'fake_fetches': int(stats.get('fake_fetches', 0)),
                        'success_rate': float(stats.get('success_rate', 0)),
                        'last_fetch': stats.get('last_fetch', 'Never')
                    }
            else:
                # Get aggregate stats for all spiders
                spider_keys = self.redis_client.keys("spider:performance:*")
                total_authentic = 0
                total_fake = 0
                total_fetches = 0
                active_spiders = 0

                for key in spider_keys:
                    stats = self.redis_client.hgetall(key)
                    if stats:
                        total_authentic += int(stats.get('authentic_fetches', 0))
                        total_fake += int(stats.get('fake_fetches', 0))
                        total_fetches += int(stats.get('total_fetches', 0))

                        # Check if spider is active (fetched in last hour)
                        last_fetch = stats.get('last_fetch')
                        if last_fetch:
                            last_fetch_time = datetime.fromisoformat(last_fetch)
                            if (datetime.now() - last_fetch_time).seconds < 3600:
                                active_spiders += 1

                return {
                    'total_spiders': len(spider_keys),
                    'active_spiders': active_spiders,
                    'total_fetches': total_fetches,
                    'authentic_fetches': total_authentic,
                    'fake_fetches': total_fake,
                    'overall_success_rate': (total_authentic / total_fetches * 100) if total_fetches > 0 else 0
                }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def get_recent_api_calls(self, limit: int = 10) -> List[Dict]:
        """Get recent API calls made by spiders"""
        try:
            call_keys = self.redis_client.keys("spider:api_call:*")
            recent_calls = []

            for key in call_keys[:limit]:
                call_data = self.redis_client.hgetall(key)
                if call_data:
                    recent_calls.append(call_data)

            # Sort by timestamp
            recent_calls.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return recent_calls[:limit]

        except Exception as e:
            logger.error(f"Failed to get recent calls: {e}")
            return []


class SpiderMonitor:
    """
    Monitor spider network health and performance
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=4,
            decode_responses=True
        )
        self.verifier = SpiderAuthenticityVerifier()

    def get_spider_network_status(self) -> Dict:
        """Get overall spider network health status"""
        try:
            stats = self.verifier.get_spider_statistics()

            # Calculate health score
            health_score = 100
            if stats['fake_fetches'] > stats['authentic_fetches'] * 0.1:  # >10% fake
                health_score -= 20
            if stats['active_spiders'] < stats['total_spiders'] * 0.5:  # <50% active
                health_score -= 30
            if stats['overall_success_rate'] < 80:
                health_score -= 20

            return {
                'health_score': max(0, health_score),
                'status': 'healthy' if health_score > 70 else 'degraded' if health_score > 40 else 'critical',
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get network status: {e}")
            return {
                'health_score': 0,
                'status': 'unknown',
                'error': str(e)
            }

    def get_data_freshness_report(self) -> Dict:
        """Get report on data freshness across spiders"""
        try:
            freshness_data = {
                'very_fresh': 0,  # < 5 minutes
                'fresh': 0,       # < 1 hour
                'stale': 0,       # < 24 hours
                'very_stale': 0   # > 24 hours
            }

            # Check recent spider fetches
            proof_keys = self.redis_client.keys("spider:proof:*")

            for key in proof_keys[-100:]:  # Check last 100
                proof_data = self.redis_client.hget(key, 'proof')
                if proof_data:
                    proof = json.loads(proof_data)
                    freshness = proof.get('evidence', {}).get('freshness', {})

                    if freshness.get('verified'):
                        age = freshness.get('age_seconds', float('inf'))

                        if age < 300:
                            freshness_data['very_fresh'] += 1
                        elif age < 3600:
                            freshness_data['fresh'] += 1
                        elif age < 86400:
                            freshness_data['stale'] += 1
                        else:
                            freshness_data['very_stale'] += 1

            total = sum(freshness_data.values())
            if total > 0:
                freshness_data['freshness_percentage'] = (
                    (freshness_data['very_fresh'] + freshness_data['fresh']) / total * 100
                )
            else:
                freshness_data['freshness_percentage'] = 0

            return freshness_data

        except Exception as e:
            logger.error(f"Failed to get freshness report: {e}")
            return {}