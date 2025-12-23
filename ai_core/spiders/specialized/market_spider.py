"""
Market Data Spider - Real-Time Market Intelligence
=================================================

Session 534: Simplified to work with spider network interface.
Aggregates market news and financial data via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MarketDataSpider:
    """Real-time market data and trading intelligence spider"""

    name = "market"

    # Market and financial RSS feeds
    RSS_FEEDS = {
        'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'cnbc_markets': 'https://www.cnbc.com/id/20910258/device/rss/rss.html',
        'reuters_markets': 'https://www.reutersagency.com/feed/?best-sectors=commodities&post_type=best',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
        'yahoo_finance': 'https://finance.yahoo.com/rss/topfinstories',
        'seeking_alpha': 'https://seekingalpha.com/feed.xml',
    }

    # Market categories
    CATEGORIES = [
        ('Stocks', 'stocks', 'Stock market news and analysis.'),
        ('Crypto', 'crypto', 'Cryptocurrency markets.'),
        ('Forex', 'forex', 'Foreign exchange markets.'),
        ('Commodities', 'commodities', 'Commodity markets.'),
        ('Economy', 'economy', 'Economic indicators and news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.market_categories = {
            'stocks': ['stock', 'equity', 's&p', 'nasdaq', 'dow', 'share', 'dividend'],
            'crypto': ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi', 'nft'],
            'forex': ['forex', 'currency', 'dollar', 'euro', 'yen', 'exchange rate'],
            'commodities': ['oil', 'gold', 'silver', 'commodity', 'crude', 'metal'],
            'economy': ['gdp', 'inflation', 'fed', 'interest rate', 'unemployment', 'cpi'],
            'trading': ['trading', 'bullish', 'bearish', 'rally', 'correction', 'volatility'],
        }
        self.sentiment_keywords = {
            'bullish': ['surge', 'rally', 'gain', 'rise', 'up', 'bullish', 'soar', 'jump'],
            'bearish': ['drop', 'fall', 'decline', 'down', 'bearish', 'crash', 'plunge', 'sink'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch market news and data from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of market content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting market categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Market spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from market RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect market category and sentiment
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                sentiment = self._detect_sentiment(text)
                tickers = self._extract_tickers(title + ' ' + summary)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'market_category': category,
                    'sentiment': sentiment,
                    'tickers': tickers,
                    'has_trading_signal': len(tickers) > 0,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'market_data',
                    'platform': 'market',
                    'tags': ['market', 'trading', category],
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

    def _detect_sentiment(self, text: str) -> str:
        """Detect market sentiment from text."""
        bullish_count = sum(1 for word in self.sentiment_keywords['bullish'] if word in text)
        bearish_count = sum(1 for word in self.sentiment_keywords['bearish'] if word in text)

        if bullish_count > bearish_count * 1.5:
            return 'bullish'
        elif bearish_count > bullish_count * 1.5:
            return 'bearish'
        return 'neutral'

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text."""
        # Match common ticker patterns (1-5 uppercase letters)
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(ticker_pattern, text)

        # Filter out common words that look like tickers
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS',
                        'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO',
                        'BOY', 'DID', 'CEO', 'CFO', 'IPO', 'ETF', 'GDP', 'CPI', 'FED', 'SEC'}

        tickers = [t for t in matches if t not in common_words and len(t) >= 2]
        return list(set(tickers))[:5]  # Return up to 5 unique tickers

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return market category links."""
        return [
            {
                'title': f"Markets: {name}",
                'url': f'https://www.marketwatch.com/{slug}',
                'link': f'https://www.marketwatch.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Market Data',
                'data_type': 'market_category',
                'platform': 'market',
                'tags': ['market', 'trading', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Stock Market', 'stocks', 'Equity market news and analysis.'),
            ('Crypto Markets', 'crypto', 'Cryptocurrency price movements.'),
            ('Forex Trading', 'forex', 'Currency exchange markets.'),
            ('Commodities', 'commodities', 'Gold, oil, and commodities.'),
            ('Economic News', 'economy', 'Economic indicators and policy.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.marketwatch.com/{category}',
                'link': f'https://www.marketwatch.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Market Data',
                'data_type': 'market_topic',
                'platform': 'market',
                'tags': ['market', 'trading', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
