"""
News Harvesting Spider - Real-Time News Intelligence
===================================================

Session 534: Simplified to work with spider network interface.
Aggregates financial and tech news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NewsHarvesterSpider:
    """Real-time news harvesting and analysis spider"""

    name = "news"

    # Financial and tech news RSS feeds
    RSS_FEEDS = {
        'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
        'wsj_markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        'ft': 'https://www.ft.com/rss/home',
        'techcrunch': 'https://techcrunch.com/feed/',
        'wired': 'https://www.wired.com/feed/rss',
    }

    # News categories
    CATEGORIES = [
        ('Markets', 'markets', 'Stock market and trading news.'),
        ('Economy', 'economy', 'Economic indicators and policy.'),
        ('Tech', 'technology', 'Technology and startup news.'),
        ('Crypto', 'crypto', 'Cryptocurrency news.'),
        ('Breaking', 'breaking', 'Breaking news alerts.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.news_categories = {
            'earnings': ['earnings', 'quarterly', 'revenue', 'profit', 'eps'],
            'mergers': ['merger', 'acquisition', 'buyout', 'takeover', 'deal'],
            'regulatory': ['regulatory', 'regulation', 'fda', 'sec', 'compliance'],
            'technology': ['technology', 'tech', 'ai', 'software', 'digital'],
            'crypto': ['crypto', 'bitcoin', 'blockchain', 'ethereum', 'defi'],
            'economy': ['economy', 'economic', 'gdp', 'inflation', 'unemployment'],
            'fed': ['federal reserve', 'fed', 'interest rate', 'monetary policy'],
            'breaking': ['breaking', 'urgent', 'alert', 'developing'],
        }
        self.impact_keywords = {
            'high': ['breaking', 'unprecedented', 'major', 'significant', 'massive', 'surge', 'crash'],
            'medium': ['important', 'notable', 'considerable', 'substantial'],
            'low': ['minor', 'slight', 'small', 'limited'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of news content dictionaries
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
            logger.warning(f"Error getting news categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"News spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from news RSS feed."""
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

                # Detect news category and impact
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                market_impact = self._detect_market_impact(text)
                sentiment = self._analyze_sentiment(text)
                tickers = self._extract_tickers(title + ' ' + summary)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.title()),
                    'category': category,
                    'news_category': category,
                    'market_impact': market_impact,
                    'sentiment': sentiment,
                    'tickers': tickers,
                    'is_breaking': category == 'breaking' or market_impact == 'high',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'news',
                    'platform': 'news',
                    'tags': ['news', category, feed_name],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect news category from text."""
        for category, keywords in self.news_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_market_impact(self, text: str) -> str:
        """Detect market impact level from text."""
        for level, keywords in self.impact_keywords.items():
            if any(kw in text for kw in keywords):
                return level
        return 'low'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        positive_words = ['growth', 'profit', 'gain', 'surge', 'rally', 'bullish', 'beat', 'exceed']
        negative_words = ['loss', 'decline', 'fall', 'crash', 'bearish', 'miss', 'disappoint', 'concern']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count * 1.5:
            return 'positive'
        elif negative_count > positive_count * 1.5:
            return 'negative'
        return 'neutral'

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text."""
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        matches = re.findall(ticker_pattern, text)

        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD',
                        'CEO', 'CFO', 'IPO', 'ETF', 'GDP', 'CPI', 'FED', 'SEC', 'FBI', 'CIA'}

        tickers = [t for t in matches if t not in common_words and len(t) >= 2]
        return list(set(tickers))[:5]

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return news category links."""
        return [
            {
                'title': f"News: {name}",
                'url': f'https://www.bloomberg.com/{slug}',
                'link': f'https://www.bloomberg.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'News',
                'data_type': 'news_category',
                'platform': 'news',
                'tags': ['news', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Market News', 'markets', 'Latest stock market news.'),
            ('Economic News', 'economy', 'Economic indicators and policy.'),
            ('Tech News', 'technology', 'Technology and startup news.'),
            ('Crypto News', 'crypto', 'Cryptocurrency market news.'),
            ('Breaking News', 'breaking', 'Breaking financial news.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.bloomberg.com/{category}',
                'link': f'https://www.bloomberg.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'News',
                'data_type': 'news_topic',
                'platform': 'news',
                'tags': ['news', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
