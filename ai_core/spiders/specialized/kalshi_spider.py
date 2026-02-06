"""
Kalshi Prediction Markets Spider
=================================

Fetches prediction market data from Kalshi's public API endpoints.

Data Sources:
- https://api.elections.kalshi.com/trade-api/v2/markets - All markets
- https://api.elections.kalshi.com/trade-api/v2/series - Market series/categories
- https://api.elections.kalshi.com/trade-api/v2/events - Event collections

Note: Despite the "elections" subdomain, this API provides access to ALL Kalshi markets
including economics, weather, tech, entertainment, and more.

No authentication required for public market data endpoints.

Session 558: Initial implementation
"""

import requests
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KalshiSpider:
    """Spider for fetching prediction market data from Kalshi"""

    name = "kalshi"
    base_url = "https://api.elections.kalshi.com/trade-api/v2"

    # Market categories available on Kalshi
    # Session 950: Added 'sports' as dedicated category
    CATEGORIES = [
        'sports',         # NBA, NFL, MLB, esports, player props, parlays
        'economics',      # Jobs reports, inflation, GDP
        'politics',       # Elections, policy decisions
        'weather',        # Temperature records, hurricanes
        'tech',           # Product launches, company events
        'entertainment',  # Awards, movies, TV
        'finance',        # Stock prices, crypto
        'science',        # Space, discoveries
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

    def fetch_data(self, max_results: int = 500, categories: List[str] = None,
                   include_events: bool = True, include_series: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch prediction market data from Kalshi with full pagination.

        Args:
            max_results: Maximum number of markets to fetch (default 500 for broader coverage)
            categories: Optional list of categories to filter by
            include_events: Whether to include event collections
            include_series: Whether to include series metadata

        Returns:
            List of prediction market data
        """
        all_data = []

        # Fetch active markets with pagination (up to 2000 markets)
        markets = self._fetch_markets(limit=min(max_results, 2000))
        all_data.extend(markets)

        # Fetch trending/high volume markets
        trending = self._fetch_trending_markets(limit=max_results // 4)
        # Deduplicate
        existing_tickers = {m.get('ticker') for m in all_data}
        for market in trending:
            if market.get('ticker') not in existing_tickers:
                all_data.append(market)

        # Fetch events for additional context
        if include_events:
            events_data = self._fetch_events(limit=100)
            all_data.extend(events_data)

        # Fetch series (categories) for context
        if include_series:
            series_data = self._fetch_series(limit=50)
            all_data.extend(series_data)

        logger.info(f"Fetched {len(all_data)} total items from Kalshi (markets + events + series)")
        return all_data[:max_results] if max_results else all_data

    def _fetch_markets(self, limit: int = 100, status: str = 'open') -> List[Dict[str, Any]]:
        """Fetch markets from Kalshi API with pagination support."""
        try:
            url = f"{self.base_url}/markets"
            market_data = []
            cursor = None
            page_size = min(limit, 200)  # API max is 200 per page
            max_pages = 10  # Safety limit to avoid excessive requests

            logger.info(f"Fetching up to {limit} markets from Kalshi with pagination")

            for page in range(max_pages):
                params = {
                    'limit': page_size,
                    'status': status,
                }
                if cursor:
                    params['cursor'] = cursor

                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                markets = data.get('markets', [])

                for market in markets:
                    market_data.append(self._transform_market(market))

                # Check for next page
                cursor = data.get('cursor')
                if not cursor or len(market_data) >= limit:
                    break

                logger.debug(f"Kalshi pagination: page {page+1}, fetched {len(market_data)} so far")

            logger.info(f"Fetched {len(market_data)} markets from Kalshi (paginated)")
            return market_data[:limit]

        except Exception as e:
            logger.error(f"Error fetching markets from Kalshi: {e}")
            return []

    def _fetch_trending_markets(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch markets sorted by volume (trending)."""
        try:
            url = f"{self.base_url}/markets"
            params = {
                'limit': min(limit, 200),
                'status': 'open',
                # Sort by volume to get trending markets
            }

            logger.info(f"Fetching trending markets from Kalshi")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            markets = data.get('markets', [])

            # Sort by volume and filter high-volume markets
            sorted_markets = sorted(
                markets,
                key=lambda m: m.get('volume', 0) or 0,
                reverse=True
            )[:limit]

            market_data = []
            for market in sorted_markets:
                transformed = self._transform_market(market)
                transformed['is_trending'] = True
                market_data.append(transformed)

            logger.info(f"Fetched {len(market_data)} trending markets from Kalshi")
            return market_data

        except Exception as e:
            logger.error(f"Error fetching trending markets from Kalshi: {e}")
            return []

    def _fetch_series(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch market series (categories/topics)."""
        try:
            url = f"{self.base_url}/series"
            params = {'limit': limit}

            logger.info("Fetching series from Kalshi")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            series_list = data.get('series', [])
            series_data = []

            for series in series_list:
                series_data.append({
                    'series_ticker': series.get('ticker'),
                    'title': series.get('title'),
                    'category': series.get('category'),
                    'frequency': series.get('frequency'),
                    'tags': series.get('tags', []),
                    'data_type': 'prediction_series',
                    'source': 'Kalshi',
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(series_data)} series from Kalshi")
            return series_data

        except Exception as e:
            logger.error(f"Error fetching series from Kalshi: {e}")
            return []

    def _fetch_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch event collections."""
        try:
            url = f"{self.base_url}/events"
            params = {'limit': limit}

            logger.info("Fetching events from Kalshi")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            events = data.get('events', [])
            event_data = []

            for event in events:
                event_data.append({
                    'event_ticker': event.get('event_ticker'),
                    'series_ticker': event.get('series_ticker'),
                    'title': event.get('title'),
                    'category': event.get('category'),
                    'mutually_exclusive': event.get('mutually_exclusive'),
                    'data_type': 'prediction_event',
                    'source': 'Kalshi',
                    'timestamp': datetime.now().isoformat(),
                })

            logger.info(f"Fetched {len(event_data)} events from Kalshi")
            return event_data

        except Exception as e:
            logger.error(f"Error fetching events from Kalshi: {e}")
            return []

    def _fetch_market_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Fetch order book for a specific market."""
        try:
            url = f"{self.base_url}/markets/{ticker}/orderbook"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            orderbook = data.get('orderbook', {})

            return {
                'ticker': ticker,
                'yes_bids': orderbook.get('yes', []),
                'no_bids': orderbook.get('no', []),
                'data_type': 'prediction_orderbook',
                'source': 'Kalshi',
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching orderbook for {ticker}: {e}")
            return {}

    def _fetch_market_candlesticks(self, ticker: str, period_interval: int = 60) -> List[Dict[str, Any]]:
        """Fetch OHLC candlestick data for a market."""
        try:
            url = f"{self.base_url}/markets/{ticker}/candlesticks"
            params = {
                'period_interval': period_interval,  # in minutes
            }

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            candlesticks = data.get('candlesticks', [])

            return [{
                'ticker': ticker,
                'timestamp': c.get('end_period_ts'),
                'open': c.get('open'),
                'high': c.get('high'),
                'low': c.get('low'),
                'close': c.get('close'),
                'volume': c.get('volume'),
                'data_type': 'prediction_candlestick',
                'source': 'Kalshi',
            } for c in candlesticks]

        except Exception as e:
            logger.error(f"Error fetching candlesticks for {ticker}: {e}")
            return []

    def _transform_market(self, market: Dict) -> Dict[str, Any]:
        """Transform raw Kalshi market data into standardized format."""
        ticker = market.get('ticker', '')

        # Calculate implied probability from yes_bid/yes_ask
        yes_bid = market.get('yes_bid', 0) or 0
        yes_ask = market.get('yes_ask', 0) or 0
        no_bid = market.get('no_bid', 0) or 0
        no_ask = market.get('no_ask', 0) or 0

        # Session 950: Also check last_price as fallback for probability
        last_price = market.get('last_price', 0) or 0

        # Mid price as probability estimate (prices are in cents, 0-100)
        if yes_bid and yes_ask:
            implied_probability = (yes_bid + yes_ask) / 2 / 100
        elif yes_bid:
            implied_probability = yes_bid / 100
        elif yes_ask:
            implied_probability = yes_ask / 100
        elif last_price:
            # Use last traded price as probability indicator
            implied_probability = last_price / 100
        else:
            implied_probability = 0.5  # Default to 50%

        # Extract category from series or title
        category = self._extract_category(market)

        # Session 950: Clean up multi-leg/parlay titles for readability
        raw_title = market.get('title', '') or ''
        cleaned_title = self._clean_title(raw_title, market)

        # Session 950: Get volume from multiple possible fields
        volume = market.get('volume') or market.get('volume_24h') or market.get('dollar_volume') or 0

        return {
            'ticker': ticker,
            'title': cleaned_title,
            'raw_title': raw_title,  # Keep original for debugging
            'subtitle': market.get('subtitle'),
            'event_ticker': market.get('event_ticker'),
            'series_ticker': market.get('series_ticker'),
            'category': category,
            'status': market.get('status'),
            'yes_bid': yes_bid,
            'yes_ask': yes_ask,
            'no_bid': no_bid,
            'no_ask': no_ask,
            'last_price': last_price,
            'implied_probability': round(implied_probability, 4),
            'implied_probability_pct': round(implied_probability * 100, 2),
            'volume': volume,
            'volume_24h': market.get('volume_24h') or 0,
            'open_interest': market.get('open_interest') or 0,
            'close_time': market.get('close_time'),
            'expiration_time': market.get('expiration_time'),
            'result': market.get('result'),
            'can_close_early': market.get('can_close_early'),
            'expiration_value': market.get('expiration_value'),
            'floor_strike': market.get('floor_strike'),
            'cap_strike': market.get('cap_strike'),
            'data_type': 'prediction_market',
            'source': 'Kalshi',
            'tags': self._extract_tags(market),
            'timestamp': datetime.now().isoformat(),
        }

    def _clean_title(self, title: str, market: Dict) -> str:
        """
        Clean up market titles, especially multi-leg/parlay-style bets.

        Session 950: Handles concatenated bet legs like:
        "yes Kawhi Leonard: 1+,yes Zach LaVine: 1+,..."
        """
        if not title:
            return market.get('subtitle', '') or market.get('ticker', 'Unknown Market')

        # Detect multi-leg pattern (comma-separated "yes/no Name: value" format)
        if title.count(',yes ') >= 2 or title.count(',no ') >= 2:
            # This is a multi-leg parlay, create a summary title
            legs = [leg.strip() for leg in title.split(',') if leg.strip()]
            leg_count = len(legs)

            # Extract player/team names from first few legs
            names = []
            for leg in legs[:3]:
                # Remove "yes " or "no " prefix
                name_part = leg.replace('yes ', '').replace('no ', '')
                # Extract name (before the colon)
                if ':' in name_part:
                    name = name_part.split(':')[0].strip()
                    names.append(name)

            if names:
                if leg_count <= 3:
                    return f"{' + '.join(names)} Parlay ({leg_count} legs)"
                else:
                    return f"{names[0]} + {leg_count - 1} others Parlay ({leg_count} legs)"
            else:
                return f"Multi-Leg Parlay ({leg_count} legs)"

        # Clean up excessively long titles
        if len(title) > 120:
            return title[:117] + '...'

        return title

    def _extract_category(self, market: Dict) -> str:
        """Extract category from market data."""
        # Try to get from series ticker or event ticker
        series_ticker = market.get('series_ticker', '').lower()
        title = market.get('title', '').lower()
        event_ticker = market.get('event_ticker', '').lower()

        # Combine all text for pattern matching
        full_text = f"{series_ticker} {title} {event_ticker}"

        # Category mapping based on common patterns
        # Session 950: Sports/betting category added with comprehensive patterns
        category_patterns = {
            # Sports and betting FIRST (most specific patterns)
            'sports': [
                # Major leagues
                'nba', 'nfl', 'mlb', 'nhl', 'mls', 'wnba', 'ncaa', 'pga', 'ufc', 'mma',
                # Esports
                'esports', 'league of legends', 'valorant', 'counter-strike', 'dota',
                'overwatch', 'call of duty', 'fortnite', 'csgo', 'cs2',
                # Player names (common in prop bets) - detect via patterns
                'points', 'assists', 'rebounds', 'touchdowns', 'yards', 'goals',
                'strikeouts', 'home runs', 'hits', 'saves', 'kills', 'deaths',
                # Betting terms
                'parlay', 'spread', 'over', 'under', 'moneyline', 'prop bet',
                'winner', 'wins by', 'total score', 'first to', 'last to',
                # Team identifiers
                'lakers', 'celtics', 'warriors', 'bulls', 'heat', 'nets', 'knicks',
                'cowboys', 'patriots', 'chiefs', 'eagles', '49ers', 'packers',
                'yankees', 'dodgers', 'red sox', 'cubs', 'mets',
                # Player name patterns (common NBA/NFL players in prop bets)
                'lebron', 'curry', 'durant', 'giannis', 'jokic', 'tatum', 'kawhi',
                'mahomes', 'allen', 'burrow', 'kelce', 'hill', 'diggs',
                # Sport-related terms
                'game', 'match', 'playoff', 'championship', 'finals', 'series',
                'super bowl', 'world series', 'stanley cup', 'march madness',
            ],
            'economics': ['inflation', 'gdp', 'jobs', 'unemployment', 'fed', 'interest', 'cpi', 'ppi',
                         'payroll', 'labor', 'recession', 'rate cut', 'rate hike', 'fomc'],
            'politics': ['election', 'president', 'congress', 'senate', 'vote', 'trump', 'biden',
                        'governor', 'mayor', 'democrat', 'republican', 'poll', 'primary'],
            'weather': ['temperature', 'hurricane', 'storm', 'climate', 'heat', 'cold',
                       'tornado', 'flood', 'drought', 'wildfire', 'snow'],
            'tech': ['apple', 'google', 'tesla', 'ai', 'launch', 'iphone', 'android',
                    'microsoft', 'amazon', 'meta', 'nvidia', 'openai', 'product'],
            'finance': ['stock', 'crypto', 'bitcoin', 'ethereum', 'market', 's&p', 'nasdaq',
                       'dow', 'treasury', 'bond', 'yield', 'ipo'],
            'entertainment': ['oscar', 'emmy', 'grammy', 'golden globe', 'movie', 'film',
                            'tv show', 'streaming', 'netflix', 'box office', 'album'],
            'science': ['space', 'nasa', 'spacex', 'discovery', 'research', 'mars',
                       'moon', 'satellite', 'rocket', 'asteroid'],
        }

        for category, patterns in category_patterns.items():
            for pattern in patterns:
                if pattern in full_text:
                    return category

        return 'general'

    def _extract_tags(self, market: Dict) -> List[str]:
        """Extract relevant tags from market data."""
        tags = ['prediction_market', 'kalshi']

        title = market.get('title', '').lower()
        category = self._extract_category(market)
        tags.append(category)

        # Volume-based tags
        volume = market.get('volume', 0) or 0
        if volume > 100000:
            tags.append('high_volume')
        elif volume > 10000:
            tags.append('active')

        # Probability-based tags
        yes_bid = market.get('yes_bid', 0) or 0
        yes_ask = market.get('yes_ask', 0) or 0
        if yes_bid and yes_ask:
            prob = (yes_bid + yes_ask) / 2
            if prob > 80:
                tags.append('likely')
            elif prob < 20:
                tags.append('unlikely')
            elif 40 <= prob <= 60:
                tags.append('uncertain')

        # Status tags
        status = market.get('status', '')
        if status == 'open':
            tags.append('tradeable')
        elif status == 'closed':
            tags.append('settled')

        return tags

    def get_market_details(self, ticker: str) -> Dict[str, Any]:
        """Get detailed information for a specific market."""
        try:
            url = f"{self.base_url}/markets/{ticker}"

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            market = data.get('market', {})

            # Get additional data
            orderbook = self._fetch_market_orderbook(ticker)
            candlesticks = self._fetch_market_candlesticks(ticker)

            result = self._transform_market(market)
            result['orderbook'] = orderbook
            result['candlesticks'] = candlesticks[-10:] if candlesticks else []  # Last 10

            return result

        except Exception as e:
            logger.error(f"Error fetching market details for {ticker}: {e}")
            return {'ticker': ticker, 'error': str(e)}

    def search_markets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for markets matching a query."""
        try:
            # Kalshi API doesn't have direct search, so we filter locally
            all_markets = self._fetch_markets(limit=200)

            query_lower = query.lower()
            matching = []

            for market in all_markets:
                title = market.get('title', '').lower()
                subtitle = market.get('subtitle', '').lower()
                ticker = market.get('ticker', '').lower()

                if query_lower in title or query_lower in subtitle or query_lower in ticker:
                    matching.append(market)

            logger.info(f"Found {len(matching)} markets matching '{query}'")
            return matching[:limit]

        except Exception as e:
            logger.error(f"Error searching markets: {e}")
            return []

    def get_markets_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get markets filtered by category."""
        try:
            all_markets = self._fetch_markets(limit=200)

            matching = [
                m for m in all_markets
                if m.get('category', '').lower() == category.lower()
            ]

            logger.info(f"Found {len(matching)} markets in category '{category}'")
            return matching[:limit]

        except Exception as e:
            logger.error(f"Error fetching markets by category: {e}")
            return []
