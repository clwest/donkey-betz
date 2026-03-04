"""
Finnhub Spider - Financial Market Intelligence
==============================================

Session 534: Simplified to work with spider network interface.
Uses Finnhub API for real-time stock data and market news.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FinnhubSpider:
    """Finnhub financial data spider - stocks, news, earnings"""

    name = "finnhub"

    BASE_URL = 'https://finnhub.io/api/v1'

    # Fallback finance RSS feeds
    RSS_FEEDS = {
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
        'cnbc': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
    }

    # Tracked symbols
    # Session 981: Sector-diverse tracked symbols (was all tech + 3 others)
    TRACKED_SYMBOLS = [
        'AAPL', 'MSFT', 'NVDA',       # Tech
        'JPM', 'GS', 'V',             # Finance
        'UNH', 'LLY',                 # Healthcare
        'XOM', 'CVX',                 # Energy
        'WMT', 'CAT', 'BA',           # Consumer / Industrial
    ]

    # Market sections
    SECTIONS = [
        ('Stocks', 'stocks', 'Stock market data and news.'),
        ('Earnings', 'earnings', 'Company earnings reports.'),
        ('Market News', 'news', 'Financial market news.'),
        ('Forex', 'forex', 'Currency exchange rates.'),
        ('Crypto', 'crypto', 'Cryptocurrency data.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.api_key = os.getenv('FINNHUB_API_KEY', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch financial data from Finnhub API and fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of financial data dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Finnhub API if key is available
        if self.api_key:
            try:
                api_items = self._fetch_from_finnhub()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from Finnhub API: {e}")

        # Fetch from fallback RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add section links
        try:
            sections = self._get_section_links()
            all_items.extend(sections)
        except Exception as e:
            logger.warning(f"Error getting Finnhub sections: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Finnhub spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_finnhub(self) -> List[Dict[str, Any]]:
        """Fetch data from Finnhub API."""
        items = []

        # Fetch quotes for tracked symbols
        for symbol in self.TRACKED_SYMBOLS[:5]:
            try:
                response = cached_get(
                    f"{self.BASE_URL}/quote",
                    params={'symbol': symbol, 'token': self.api_key},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('c'):  # Current price exists
                        price = data.get('c', 0)
                        change = data.get('d', 0)
                        change_pct = data.get('dp', 0)
                        change_str = f"+{change_pct:.2f}%" if change_pct >= 0 else f"{change_pct:.2f}%"

                        items.append({
                            'title': f"{symbol}: ${price:,.2f} ({change_str})",
                            'url': f"https://finnhub.io/stock/{symbol}",
                            'link': f"https://finnhub.io/stock/{symbol}",
                            'summary': f"{symbol} - Current: ${price:,.2f}, Change: {change_str}",
                            'description': f"Real-time quote for {symbol}. High: ${data.get('h', 0):,.2f}, Low: ${data.get('l', 0):,.2f}",
                            'symbol': symbol,
                            'price': price,
                            'change': change,
                            'change_percent': change_pct,
                            'high': data.get('h', 0),
                            'low': data.get('l', 0),
                            'open': data.get('o', 0),
                            'previous_close': data.get('pc', 0),
                            'category': 'stocks',
                            'source': 'Finnhub',
                            'data_type': 'stock_quote',
                            'platform': 'finnhub',
                            'tags': ['finance', 'stocks', symbol],
                            'timestamp': datetime.now().isoformat(),
                        })

            except Exception as e:
                logger.warning(f"Error fetching quote for {symbol}: {e}")

        # Fetch market news
        try:
            response = cached_get(
                f"{self.BASE_URL}/news",
                params={'category': 'general', 'token': self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                news = response.json()
                for article in news[:10]:
                    items.append({
                        'title': article.get('headline', ''),
                        'url': article.get('url', ''),
                        'link': article.get('url', ''),
                        'summary': article.get('summary', '')[:400],
                        'description': article.get('summary', '')[:400],
                        'published': datetime.fromtimestamp(article.get('datetime', 0)).isoformat() if article.get('datetime') else '',
                        'author': article.get('source', 'Finnhub'),
                        'category': 'news',
                        'related_symbols': article.get('related', ''),
                        'source': article.get('source', 'Finnhub'),
                        'data_type': 'market_news',
                        'platform': 'finnhub',
                        'tags': ['finance', 'news', 'market'],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching market news: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from finance RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': 'news',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'finance_article',
                    'platform': 'finnhub',
                    'tags': ['finance', 'news', 'market'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return Finnhub section links."""
        return [
            {
                'title': f"Finnhub: {name}",
                'url': f'https://finnhub.io/{slug}',
                'link': f'https://finnhub.io/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Finnhub',
                'data_type': 'finance_section',
                'platform': 'finnhub',
                'tags': ['finance', 'finnhub', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Stock Quotes', 'stocks', 'Real-time stock data.'),
            ('Market News', 'news', 'Financial news and analysis.'),
            ('Earnings Calendar', 'earnings', 'Upcoming earnings reports.'),
            ('Forex Rates', 'forex', 'Currency exchange data.'),
            ('Crypto Prices', 'crypto', 'Cryptocurrency data.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://finnhub.io/{category}',
                'link': f'https://finnhub.io/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Finnhub',
                'data_type': 'finance_topic',
                'platform': 'finnhub',
                'tags': ['finance', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
