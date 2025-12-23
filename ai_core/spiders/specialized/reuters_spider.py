"""
Reuters Spider - Global News Wire Intelligence
================================================

Session 534: Simplified to work with spider network interface.
Aggregates global news wire content with market impact analysis.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReutersSpider:
    """Reuters spider - global news wire and financial intelligence"""

    name = "reuters"

    # News wire RSS feeds
    RSS_FEEDS = {
        'reuters_business': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
        'reuters_world': 'https://www.reutersagency.com/feed/?best-topics=world&post_type=best',
        'ap_business': 'https://rsshub.app/apnews/topics/apf-business',
        'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'ft': 'https://www.ft.com/rss/home',
        'wsj': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.news_categories = {
            'markets': ['market', 'stock', 'trading', 'wall street', 'nasdaq', 'dow', 's&p'],
            'economy': ['economy', 'gdp', 'inflation', 'fed', 'central bank', 'rate', 'jobs'],
            'corporate': ['company', 'earnings', 'ceo', 'merger', 'acquisition', 'ipo', 'profit'],
            'commodities': ['oil', 'gold', 'commodity', 'crude', 'energy', 'opec', 'gas'],
            'crypto': ['bitcoin', 'crypto', 'blockchain', 'ethereum', 'digital currency'],
            'politics': ['congress', 'white house', 'government', 'regulation', 'policy'],
            'global': ['china', 'europe', 'asia', 'emerging', 'global', 'international'],
        }
        self.urgency_keywords = {
            'breaking': ['breaking', 'urgent', 'just in', 'flash', 'alert'],
            'update': ['update', 'latest', 'developing', 'new'],
            'analysis': ['analysis', 'insight', 'exclusive', 'special report'],
        }
        self.regions = {
            'us': ['u.s.', 'us', 'america', 'washington', 'new york', 'fed'],
            'europe': ['europe', 'eu', 'uk', 'britain', 'germany', 'france', 'ecb'],
            'asia': ['china', 'japan', 'asia', 'india', 'korea', 'taiwan'],
            'emerging': ['emerging', 'brazil', 'mexico', 'turkey', 'south africa'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch global news wire content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of news wire dictionaries
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

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Reuters spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch news from wire service RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Analysis
                text = f"{title} {description}".lower()
                category = self._detect_category(text)
                urgency = self._detect_urgency(text)
                region = self._detect_region(text)
                has_market_impact = self._has_market_impact(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'category': category,
                    'urgency': urgency,
                    'region': region,
                    'is_breaking': urgency == 'breaking',
                    'has_market_impact': has_market_impact,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'news_wire',
                    'platform': 'reuters',
                    'tags': ['reuters', 'wire', 'news', category, region],
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

    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level from text."""
        for level, keywords in self.urgency_keywords.items():
            if any(kw in text for kw in keywords):
                return level
        return 'standard'

    def _detect_region(self, text: str) -> str:
        """Detect geographic region from text."""
        for region, keywords in self.regions.items():
            if any(kw in text for kw in keywords):
                return region
        return 'global'

    def _has_market_impact(self, text: str) -> bool:
        """Check if news has market impact."""
        impact_keywords = ['surge', 'plunge', 'rally', 'selloff', 'crash', 'soar', 'tumble', 'spike']
        return any(kw in text for kw in impact_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        bullish = ['gain', 'rise', 'surge', 'rally', 'bullish', 'record high', 'beat', 'exceed']
        bearish = ['fall', 'drop', 'decline', 'crash', 'bearish', 'loss', 'miss', 'warning']

        bull_count = sum(1 for word in bullish if word in text)
        bear_count = sum(1 for word in bearish if word in text)

        if bull_count > bear_count:
            return 'bullish'
        elif bear_count > bull_count:
            return 'bearish'
        return 'neutral'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Markets Overview', 'markets', 'global', 'Stock market updates.'),
            ('Economic News', 'economy', 'us', 'Economic indicators and Fed.'),
            ('Corporate Earnings', 'corporate', 'us', 'Earnings and M&A news.'),
            ('Global Markets', 'global', 'global', 'International market news.'),
            ('Commodities', 'commodities', 'global', 'Oil, gold, and energy.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.reuters.com/{category}/',
                'link': f'https://www.reuters.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'region': region,
                'source': 'Reuters',
                'data_type': 'wire_topic',
                'platform': 'reuters',
                'tags': ['reuters', 'wire', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, region, desc in topics
        ]
