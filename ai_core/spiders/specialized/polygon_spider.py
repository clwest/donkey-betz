"""
Polygon Spider - Financial Market Data Intelligence
====================================================

Session 534: Simplified to work with spider network interface.
Uses Polygon.io API when available, RSS fallback for market news.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PolygonSpider:
    """Polygon.io spider - stock market data and financial news"""

    name = "polygon"

    BASE_URL = 'https://api.polygon.io'

    # Financial news RSS feeds (fallback)
    RSS_FEEDS = {
        'yahoo_finance': 'https://finance.yahoo.com/news/rssindex',
        'marketwatch': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
        'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'seeking_alpha': 'https://seekingalpha.com/feed.xml',
        'investing_com': 'https://www.investing.com/rss/news.rss',
    }

    # Top stocks to track
    TRACKED_TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
        'BRK.B', 'JPM', 'V', 'UNH', 'XOM', 'JNJ', 'WMT', 'PG'
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.api_key = os.getenv('POLYGON_API_KEY', '')
        self.market_categories = {
            'tech': ['tech', 'technology', 'software', 'ai', 'semiconductor', 'cloud'],
            'finance': ['bank', 'finance', 'interest rate', 'fed', 'treasury'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind'],
            'healthcare': ['pharma', 'biotech', 'healthcare', 'drug', 'fda'],
            'retail': ['retail', 'consumer', 'e-commerce', 'shopping'],
            'crypto': ['crypto', 'bitcoin', 'ethereum', 'blockchain'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch market data from Polygon.io API and RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of financial market dictionaries
        """
        all_items = []
        seen_keys = set()

        # Try Polygon.io API if key available
        if self.api_key:
            try:
                api_items = self._fetch_polygon_api()
                for item in api_items:
                    key = item.get('ticker', item.get('url', ''))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching Polygon API: {e}")

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_keys:
                        seen_keys.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Polygon spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_polygon_api(self) -> List[Dict[str, Any]]:
        """Fetch stock data from Polygon.io API."""
        items = []

        # Fetch ticker snapshots
        for ticker in self.TRACKED_TICKERS[:5]:  # Limit for rate limits
            try:
                response = cached_get(
                    f"{self.BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}",
                    params={'apiKey': self.api_key},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'OK' and data.get('ticker'):
                        ticker_data = data['ticker']
                        day = ticker_data.get('day', {})
                        prev = ticker_data.get('prevDay', {})

                        price = day.get('c', 0)
                        change = ticker_data.get('todaysChange', 0)
                        change_pct = ticker_data.get('todaysChangePerc', 0)

                        sentiment = 'bullish' if change_pct > 1 else 'bearish' if change_pct < -1 else 'neutral'

                        items.append({
                            'title': f"{ticker}: ${price:.2f} ({change_pct:+.2f}%)",
                            'url': f"polygon_{ticker}",
                            'link': f'https://polygon.io/quote/{ticker}',
                            'summary': f"{ticker} trading at ${price:.2f}, {'+' if change >= 0 else ''}{change:.2f} ({change_pct:+.2f}%)",
                            'description': f"Open: ${day.get('o', 0):.2f}, High: ${day.get('h', 0):.2f}, Low: ${day.get('l', 0):.2f}, Vol: {day.get('v', 0):,}",
                            'ticker': ticker,
                            'price': price,
                            'change': change,
                            'change_percent': change_pct,
                            'volume': day.get('v', 0),
                            'sentiment': sentiment,
                            'category': 'stocks',
                            'source': 'Polygon.io',
                            'data_type': 'stock_quote',
                            'platform': 'polygon',
                            'tags': ['polygon', 'stocks', 'finance', ticker.lower()],
                            'timestamp': datetime.now().isoformat(),
                        })

            except Exception as e:
                logger.warning(f"Error fetching {ticker}: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch financial news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect market category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                tickers = self._extract_tickers(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'tickers': tickers,
                    'category': category,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'financial_news',
                    'platform': 'polygon',
                    'tags': ['polygon', 'finance', 'markets', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect market category from text."""
        for category, keywords in self.market_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text."""
        tickers = []
        for ticker in self.TRACKED_TICKERS:
            if ticker.lower() in text or f"${ticker}" in text.upper():
                tickers.append(ticker)
        return tickers[:5]

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze market sentiment."""
        bullish = ['gain', 'rise', 'surge', 'rally', 'bullish', 'record high', 'beat']
        bearish = ['fall', 'drop', 'decline', 'crash', 'bearish', 'loss', 'miss']

        bull_count = sum(1 for word in bullish if word in text)
        bear_count = sum(1 for word in bearish if word in text)

        if bull_count > bear_count:
            return 'bullish'
        elif bear_count > bull_count:
            return 'bearish'
        return 'neutral'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Market Overview', 'markets', 'Stock market overview and indices.'),
            ('Tech Stocks', 'tech', 'Technology sector analysis.'),
            ('Earnings Reports', 'earnings', 'Quarterly earnings coverage.'),
            ('Economic Data', 'economy', 'Economic indicators and Fed news.'),
            ('Crypto Markets', 'crypto', 'Cryptocurrency market data.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://polygon.io/{category}',
                'link': f'https://polygon.io/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Polygon.io',
                'data_type': 'financial_topic',
                'platform': 'polygon',
                'tags': ['polygon', 'finance', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
