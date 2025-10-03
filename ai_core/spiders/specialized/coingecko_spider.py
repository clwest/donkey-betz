"""
CoinGecko Crypto Market Data Spider
====================================

Fetches cryptocurrency market data from CoinGecko's free public API.

Data Sources:
- https://api.coingecko.com/api/v3/coins/markets - Top cryptocurrencies by market cap
- https://api.coingecko.com/api/v3/trending - Trending coins
- https://api.coingecko.com/api/v3/global - Global crypto market data

No API key required for basic usage (free tier).
"""

import requests
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CoinGeckoSpider:
    """Spider for fetching cryptocurrency data from CoinGecko"""

    name = "coingecko"
    base_url = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'application/json',
        })

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch cryptocurrency market data

        Args:
            max_results: Maximum number of coins to fetch

        Returns:
            List of cryptocurrency data
        """
        all_data = []

        # Fetch top coins by market cap
        all_data.extend(self._fetch_top_coins(max_results // 2))

        # Fetch trending coins
        all_data.extend(self._fetch_trending_coins(max_results // 4))

        # Fetch global market data
        global_data = self._fetch_global_data()
        if global_data:
            all_data.append(global_data)

        return all_data[:max_results]

    def _fetch_top_coins(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch top cryptocurrencies by market cap"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h,7d'
            }

            logger.info(f"Fetching top {limit} coins from CoinGecko")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            coins = response.json()
            coin_data = []

            for coin in coins:
                coin_data.append({
                    'coin_id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'current_price': coin.get('current_price'),
                    'market_cap': coin.get('market_cap'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'total_volume': coin.get('total_volume'),
                    'high_24h': coin.get('high_24h'),
                    'low_24h': coin.get('low_24h'),
                    'price_change_24h': coin.get('price_change_24h'),
                    'price_change_percentage_24h': coin.get('price_change_percentage_24h'),
                    'price_change_percentage_7d': coin.get('price_change_percentage_7d_in_currency'),
                    'circulating_supply': coin.get('circulating_supply'),
                    'total_supply': coin.get('total_supply'),
                    'ath': coin.get('ath'),
                    'ath_date': coin.get('ath_date'),
                    'atl': coin.get('atl'),
                    'atl_date': coin.get('atl_date'),
                    'last_updated': coin.get('last_updated'),
                    'data_type': 'crypto_market_data',
                    'source': 'CoinGecko',
                    'tags': self._extract_tags(coin),
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(coin_data)} top coins from CoinGecko")
            return coin_data

        except Exception as e:
            logger.error(f"Error fetching top coins from CoinGecko: {e}")
            return []

    def _fetch_trending_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch trending cryptocurrencies"""
        try:
            url = f"{self.base_url}/search/trending"
            logger.info("Fetching trending coins from CoinGecko")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            trending_data = []

            coins = data.get('coins', [])[:limit]
            for item in coins:
                coin = item.get('item', {})
                trending_data.append({
                    'coin_id': coin.get('id'),
                    'symbol': coin.get('symbol', '').upper(),
                    'name': coin.get('name'),
                    'market_cap_rank': coin.get('market_cap_rank'),
                    'price_btc': coin.get('price_btc'),
                    'score': coin.get('score'),
                    'thumb': coin.get('thumb'),
                    'data_type': 'trending_crypto',
                    'source': 'CoinGecko Trending',
                    'tags': ['crypto', 'trending', 'popular'],
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(trending_data)} trending coins from CoinGecko")
            return trending_data

        except Exception as e:
            logger.error(f"Error fetching trending coins from CoinGecko: {e}")
            return []

    def _fetch_global_data(self) -> Dict[str, Any]:
        """Fetch global cryptocurrency market data"""
        try:
            url = f"{self.base_url}/global"
            logger.info("Fetching global crypto market data from CoinGecko")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json().get('data', {})

            global_data = {
                'total_market_cap_usd': data.get('total_market_cap', {}).get('usd'),
                'total_volume_usd': data.get('total_volume', {}).get('usd'),
                'market_cap_percentage': data.get('market_cap_percentage', {}),
                'market_cap_change_percentage_24h': data.get('market_cap_change_percentage_24h_usd'),
                'active_cryptocurrencies': data.get('active_cryptocurrencies'),
                'markets': data.get('markets'),
                'ongoing_icos': data.get('ongoing_icos'),
                'ended_icos': data.get('ended_icos'),
                'updated_at': data.get('updated_at'),
                'data_type': 'global_crypto_market',
                'source': 'CoinGecko Global',
                'tags': ['crypto', 'global', 'market_overview'],
                'timestamp': datetime.now().isoformat(),
            }

            logger.info("Fetched global crypto market data from CoinGecko")
            return global_data

        except Exception as e:
            logger.error(f"Error fetching global data from CoinGecko: {e}")
            return {}

    def _extract_tags(self, coin: Dict) -> List[str]:
        """Extract relevant tags from coin data"""
        tags = ['crypto', 'cryptocurrency']

        # Add symbol as tag
        symbol = coin.get('symbol', '').upper()
        if symbol:
            tags.append(symbol)

        # Market cap based tags
        rank = coin.get('market_cap_rank')
        if rank:
            if rank <= 10:
                tags.append('top_10')
            elif rank <= 50:
                tags.append('top_50')
            elif rank <= 100:
                tags.append('top_100')

        # Price movement tags
        change_24h = coin.get('price_change_percentage_24h')
        if change_24h:
            if change_24h > 10:
                tags.append('pumping')
            elif change_24h < -10:
                tags.append('dumping')
            elif abs(change_24h) > 5:
                tags.append('volatile')

        # Popular coins
        name_lower = coin.get('name', '').lower()
        if 'bitcoin' in name_lower:
            tags.append('bitcoin')
        elif 'ethereum' in name_lower:
            tags.append('ethereum')
        elif any(word in name_lower for word in ['stable', 'usd', 'usdt', 'usdc']):
            tags.append('stablecoin')

        return tags
