"""
Real Estate Spider - Property Market Intelligence
==================================================

Session 534: Simplified to work with spider network interface.
Aggregates real estate and housing market news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RealEstateSpider:
    """Real estate spider - property markets, housing, and investment news"""

    name = "real_estate"

    # Real estate RSS feeds
    RSS_FEEDS = {
        'realtor_news': 'https://www.realtor.com/news/feed/',
        'inman': 'https://www.inman.com/feed/',
        'housingwire': 'https://www.housingwire.com/feed/',
        'curbed': 'https://www.curbed.com/rss/index.xml',
        'biggerpockets': 'https://www.biggerpockets.com/blog/feed/',
        'nar': 'https://www.nar.realtor/newsroom/rss.xml',
    }

    # Real estate categories
    CATEGORIES = [
        ('Buying', 'buying', 'Home buying tips and guides.'),
        ('Selling', 'selling', 'Selling strategies and listings.'),
        ('Renting', 'renting', 'Rental market and tenant info.'),
        ('Investing', 'investing', 'Real estate investment.'),
        ('Market Trends', 'market', 'Housing market analysis.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.real_estate_categories = {
            'buying': ['buy', 'purchase', 'buyer', 'mortgage', 'down payment', 'loan', 'first-time'],
            'selling': ['sell', 'seller', 'listing', 'asking price', 'offer', 'staging'],
            'renting': ['rent', 'rental', 'tenant', 'landlord', 'lease', 'apartment'],
            'investing': ['invest', 'roi', 'flip', 'rental income', 'portfolio', 'cashflow'],
            'market': ['market', 'price', 'appreciation', 'trend', 'forecast', 'inventory'],
            'commercial': ['commercial', 'office', 'retail', 'industrial', 'warehouse'],
            'luxury': ['luxury', 'mansion', 'estate', 'high-end', 'million'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch real estate news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of real estate content dictionaries
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
            logger.warning(f"Error getting real estate categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Real Estate spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from real estate RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect real estate category
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                sentiment = self._analyze_sentiment(text)
                price_mentioned = self._extract_price(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'sentiment': sentiment,
                    'price_mentioned': price_mentioned,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'real_estate_news',
                    'platform': 'real_estate',
                    'tags': ['realestate', 'property', 'housing'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect real estate categories from text."""
        categories = []
        for category, keywords in self.real_estate_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories if categories else ['general']

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze market sentiment."""
        positive_words = ['grow', 'rise', 'increase', 'boom', 'strong', 'recover', 'hot market']
        negative_words = ['fall', 'decline', 'crash', 'slow', 'weak', 'cooling', 'bubble']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'bullish'
        elif negative_count > positive_count:
            return 'bearish'
        return 'neutral'

    def _extract_price(self, text: str) -> str:
        """Extract price mentions from text."""
        price_patterns = [
            r'\$[\d,]+(?:k|K|M|million)?',
            r'[\d,]+\s*(?:thousand|million)',
            r'median\s*(?:price|home).*?\$[\d,]+',
        ]
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return ''

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return real estate category links."""
        return [
            {
                'title': f"Real Estate: {name}",
                'url': f'https://www.realtor.com/news/{slug}/',
                'link': f'https://www.realtor.com/news/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Realtor.com',
                'data_type': 'real_estate_category',
                'platform': 'real_estate',
                'tags': ['realestate', 'property', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Home Buying Guide', 'buying', 'Tips for first-time buyers.'),
            ('Selling Your Home', 'selling', 'Maximize your sale price.'),
            ('Rental Market', 'renting', 'Rental trends and tips.'),
            ('Investment Properties', 'investing', 'Real estate investing strategies.'),
            ('Market Analysis', 'market', 'Housing market trends.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.realtor.com/news/{category}/',
                'link': f'https://www.realtor.com/news/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Realtor.com',
                'data_type': 'real_estate_topic',
                'platform': 'real_estate',
                'tags': ['realestate', 'property', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
