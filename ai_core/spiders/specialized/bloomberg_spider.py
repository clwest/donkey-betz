"""
Bloomberg Spider - Professional Finance & Markets Intelligence
===============================================================

Session 534: Simplified to work with spider network interface.
Uses professional finance RSS feeds for market and economic news.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BloombergSpider:
    """Bloomberg spider - professional finance and markets intelligence"""

    name = "bloomberg"

    # Professional finance RSS feeds
    RSS_FEEDS = {
        'wsj_markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        'wsj_business': 'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
        'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
        'cnbc': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
    }

    # Market sections
    SECTIONS = [
        ('Markets', 'markets', 'Stock and bond market news.'),
        ('Economics', 'economics', 'Economic data and analysis.'),
        ('Companies', 'companies', 'Corporate news and earnings.'),
        ('Technology', 'technology', 'Tech sector coverage.'),
        ('Crypto', 'crypto', 'Cryptocurrency and digital assets.'),
        ('Commodities', 'commodities', 'Oil, gold, and commodities.'),
        ('Personal Finance', 'personal-finance', 'Investing and wealth.'),
        ('Real Estate', 'real-estate', 'Property market news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch financial news from professional sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of article dictionaries
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

        # Add market section links
        try:
            sections = self._get_section_links()
            all_items.extend(sections)
        except Exception as e:
            logger.warning(f"Error getting Bloomberg sections: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Bloomberg spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from finance RSS feed."""
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

                # Detect market topic and indicators
                text = f"{title} {description}".lower()
                market_topic = self._detect_market_topic(text)
                economic_indicator = self._detect_economic_indicator(text)
                is_high_impact = self._is_high_impact(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': market_topic,
                    'market_topic': market_topic,
                    'economic_indicator': economic_indicator,
                    'is_high_impact': is_high_impact,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'finance_article',
                    'platform': 'bloomberg',
                    'tags': ['finance', 'markets', 'economics', market_topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_market_topic(self, text: str) -> str:
        """Detect market topic from text."""
        topics = {
            'equities': ['stock', 'equity', 'shares', 'nasdaq', 'nyse', 's&p 500', 'dow'],
            'fixed_income': ['bond', 'treasury', 'yield', 'fixed income', 'credit'],
            'forex': ['forex', 'currency', 'dollar', 'euro', 'yen', 'exchange rate'],
            'commodities': ['oil', 'gold', 'commodity', 'crude', 'copper'],
            'crypto': ['bitcoin', 'crypto', 'ethereum', 'digital asset'],
        }

        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_economic_indicator(self, text: str) -> str:
        """Detect economic indicator from text."""
        indicators = {
            'monetary': ['fed', 'central bank', 'interest rate', 'rate hike'],
            'inflation': ['inflation', 'cpi', 'pce', 'price'],
            'employment': ['jobs', 'employment', 'unemployment', 'payroll'],
            'gdp': ['gdp', 'growth', 'recession', 'economic'],
        }

        for indicator, keywords in indicators.items():
            if any(kw in text for kw in keywords):
                return indicator
        return None

    def _is_high_impact(self, text: str) -> bool:
        """Check if news is high impact."""
        high_impact = ['surge', 'plunge', 'crash', 'soar', 'tumble', 'record',
                       'historic', 'breaking', 'alert', 'urgent']
        return any(word in text for word in high_impact)

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return Bloomberg section links."""
        return [
            {
                'title': f"Bloomberg: {name}",
                'url': f'https://www.bloomberg.com/{slug}',
                'link': f'https://www.bloomberg.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Bloomberg',
                'data_type': 'finance_section',
                'platform': 'bloomberg',
                'tags': ['finance', 'bloomberg', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Market News', 'markets', 'Stock and bond markets.'),
            ('Economic Data', 'economics', 'Economic indicators and data.'),
            ('Company News', 'companies', 'Corporate earnings and news.'),
            ('Tech Sector', 'technology', 'Technology company coverage.'),
            ('Crypto Markets', 'crypto', 'Digital asset news.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.bloomberg.com/{category}',
                'link': f'https://www.bloomberg.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Bloomberg',
                'data_type': 'finance_topic',
                'platform': 'bloomberg',
                'tags': ['finance', 'bloomberg', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
