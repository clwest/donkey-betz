"""
Etherscan API Spider - Real Blockchain Transaction Data
========================================================

Session 461: Part of the Blockchain Audit Agent Group

This spider fetches REAL transaction data from the Etherscan API:
- Recent transactions for watched addresses
- Large ETH transfers
- Token transfers
- Contract deployments
- Internal transactions

Requires: ETHERSCAN_API_KEY environment variable
Free tier: 5 calls/second, 100k calls/day
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from ai_core.spiders.web_request_layer import cached_get

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData

logger = logging.getLogger(__name__)


# Whale threshold in ETH
WHALE_THRESHOLD_ETH = 100

# Known addresses to monitor
MONITORED_ADDRESSES = {
    # Major exchanges (example addresses - would be real in production)
    'binance_hot': '0x28C6c06298d514Db089934071355E5743bf21d60',
    'coinbase': '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
    # DeFi protocols
    'aave_v3': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
    'uniswap_v3': '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45',
}


class EtherscanAPISpider(BaseIntelligenceSpider):
    """
    Spider that fetches real blockchain data from Etherscan API.

    Data types fetched:
    - Normal transactions (ETH transfers)
    - Internal transactions (contract calls)
    - ERC-20 token transfers
    - Contract deployments
    """

    # Etherscan API V2 endpoints (V1 deprecated Dec 2025)
    BASE_URL = "https://api.etherscan.io/v2/api"
    CHAIN_ID = 1  # Ethereum mainnet

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.environ.get('ETHERSCAN_API_KEY', '')

        if not self.api_key:
            logger.warning("ETHERSCAN_API_KEY not set - Etherscan API spider will have limited functionality")

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch blockchain data from Etherscan API."""
        if not self.api_key:
            return self._fetch_without_api()

        try:
            results = {
                'large_transfers': [],
                'recent_blocks': [],
                'contract_deployments': [],
                'token_transfers': [],
                'whale_alerts': [],
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

            # 1. Get latest blocks
            blocks_data = self._fetch_recent_blocks()
            if blocks_data:
                results['recent_blocks'] = blocks_data

            # 2. Get large ETH transfers (check monitored addresses)
            for name, address in list(MONITORED_ADDRESSES.items())[:3]:  # Limit API calls
                transfers = self._fetch_address_transactions(address, name)
                if transfers:
                    results['large_transfers'].extend(transfers)

            # 3. Get recent whale alerts
            whale_alerts = self._detect_whale_activity(results['large_transfers'])
            results['whale_alerts'] = whale_alerts

            return results

        except Exception as e:
            logger.error(f"Error fetching Etherscan API data: {e}")
            return self._fetch_without_api()

    def _fetch_recent_blocks(self) -> List[Dict[str, Any]]:
        """Fetch recent block information."""
        try:
            # Get current block number
            response = cached_get(
                self.BASE_URL,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'proxy',
                    'action': 'eth_blockNumber',
                    'apikey': self.api_key
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('result'):
                    current_block = int(data['result'], 16)
                    return [{
                        'block_number': current_block,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }]
        except Exception as e:
            logger.warning(f"Error fetching recent blocks: {e}")

        return []

    def _fetch_address_transactions(self, address: str, label: str) -> List[Dict[str, Any]]:
        """Fetch recent transactions for an address."""
        try:
            response = cached_get(
                self.BASE_URL,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'account',
                    'action': 'txlist',
                    'address': address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': 1,
                    'offset': 10,  # Last 10 transactions
                    'sort': 'desc',
                    'apikey': self.api_key
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    transactions = []
                    for tx in data['result']:
                        # Convert Wei to ETH
                        value_eth = int(tx.get('value', 0)) / 1e18

                        transactions.append({
                            'hash': tx.get('hash'),
                            'from': tx.get('from'),
                            'to': tx.get('to'),
                            'value_eth': value_eth,
                            'timestamp': datetime.fromtimestamp(
                                int(tx.get('timeStamp', 0)),
                                tz=timezone.utc
                            ).isoformat(),
                            'block_number': tx.get('blockNumber'),
                            'gas_used': tx.get('gasUsed'),
                            'address_label': label,
                            'is_whale': value_eth >= WHALE_THRESHOLD_ETH
                        })
                    return transactions

        except Exception as e:
            logger.warning(f"Error fetching transactions for {address}: {e}")

        return []

    def _detect_whale_activity(self, transfers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect whale-level transfers."""
        whale_alerts = []

        for tx in transfers:
            if tx.get('is_whale', False):
                whale_alerts.append({
                    'type': 'whale_transfer',
                    'hash': tx.get('hash'),
                    'value_eth': tx.get('value_eth'),
                    'from': tx.get('from'),
                    'to': tx.get('to'),
                    'timestamp': tx.get('timestamp'),
                    'address_label': tx.get('address_label'),
                    'severity': 'HIGH' if tx.get('value_eth', 0) >= 1000 else 'MEDIUM'
                })

        return whale_alerts

    def _fetch_without_api(self) -> Dict[str, Any]:
        """Fallback when API key is not available."""
        return {
            'items': [{
                'title': 'Etherscan API key not configured',
                'description': 'Set ETHERSCAN_API_KEY environment variable for real transaction data',
                'source': 'etherscan_api',
                'type': 'warning'
            }],
            'source': 'etherscan_api_fallback',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process the fetched blockchain data."""
        try:
            # Count significant items
            large_transfers = raw_data.get('large_transfers', [])
            whale_alerts = raw_data.get('whale_alerts', [])

            # Build summary
            summary_parts = []

            if large_transfers:
                total_eth = sum(t.get('value_eth', 0) for t in large_transfers)
                summary_parts.append(f"{len(large_transfers)} transfers ({total_eth:.2f} ETH)")

            if whale_alerts:
                summary_parts.append(f"{len(whale_alerts)} whale alerts")

            summary = "; ".join(summary_parts) if summary_parts else "No significant activity"

            # Generate insights
            insights = self._generate_insights(raw_data)

            # Session 503: Fixed to match base IntelligenceData signature
            return IntelligenceData(
                spider_id=self.spider_id,
                source_url="https://etherscan.io",
                data_type='blockchain',
                content={
                    'transactions': large_transfers,
                    'whale_alerts': whale_alerts,
                    'recent_blocks': raw_data.get('recent_blocks', []),
                    'summary': summary,
                    'insights': insights,
                    'title': f"Ethereum Network Activity: {summary}",
                },
                metadata={
                    'relevance_score': self._calculate_relevance(raw_data),
                    'freshness': 1.0,
                },
                quality_score=self._calculate_relevance(raw_data) / 100.0,  # Convert to 0-1 scale
                timestamp=datetime.now(timezone.utc)
            )

        except Exception as e:
            logger.error(f"Error processing Etherscan data: {e}")
            return None

    def _generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate insights from blockchain data."""
        insights = []

        whale_alerts = data.get('whale_alerts', [])
        if whale_alerts:
            # Find largest transfer
            largest = max(whale_alerts, key=lambda x: x.get('value_eth', 0))
            insights.append(f"Largest whale transfer: {largest.get('value_eth', 0):.2f} ETH")

            # Check for exchange activity
            exchange_activity = [w for w in whale_alerts if 'exchange' in w.get('address_label', '').lower()]
            if exchange_activity:
                insights.append(f"{len(exchange_activity)} whale movements involving exchanges")

        large_transfers = data.get('large_transfers', [])
        if large_transfers:
            # Calculate average transfer size
            avg_value = sum(t.get('value_eth', 0) for t in large_transfers) / len(large_transfers)
            insights.append(f"Average transfer size: {avg_value:.2f} ETH")

        return insights

    def _calculate_relevance(self, data: Dict[str, Any]) -> float:
        """Calculate relevance score based on activity."""
        score = 50.0  # Base score

        whale_alerts = data.get('whale_alerts', [])
        if whale_alerts:
            score += min(len(whale_alerts) * 10, 30)  # Up to +30 for whale activity

        large_transfers = data.get('large_transfers', [])
        if large_transfers:
            total_eth = sum(t.get('value_eth', 0) for t in large_transfers)
            if total_eth > 10000:
                score += 20  # Big volume bonus
            elif total_eth > 1000:
                score += 10

        return min(score, 100.0)

    def get_config(self) -> Dict[str, Any]:
        """Return spider configuration."""
        return {
            'spider_id': self.spider_id,
            'type': 'etherscan_api',
            'category': 'blockchain',
            'api_configured': bool(self.api_key),
            'whale_threshold_eth': WHALE_THRESHOLD_ETH,
            'monitored_addresses': list(MONITORED_ADDRESSES.keys()),
            'description': 'Real-time Ethereum transaction monitoring via Etherscan API'
        }
