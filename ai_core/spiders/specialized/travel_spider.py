"""
Travel Spider - Travel & Tourism Industry Intelligence
=======================================================

Session 534: Simplified to work with spider network interface.
Aggregates travel, tourism, and hospitality content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TravelSpider:
    """Travel spider - travel news, destinations, and tourism industry"""

    name = "travel"

    # Travel and tourism RSS feeds
    RSS_FEEDS = {
        'lonely_planet': 'https://www.lonelyplanet.com/news/feed',
        'conde_nast': 'https://www.cntraveler.com/feed/rss',
        'travel_leisure': 'https://www.travelandleisure.com/feeds/all',
        'the_points_guy': 'https://thepointsguy.com/feed/',
        'nomadic_matt': 'https://www.nomadicmatt.com/feed/',
        'skift': 'https://skift.com/feed/',
    }

    # Travel categories
    CATEGORIES = [
        ('Destinations', 'destinations', 'Travel destinations and guides.'),
        ('Hotels', 'hotels', 'Hotel reviews and bookings.'),
        ('Flights', 'flights', 'Airlines and flight deals.'),
        ('Budget Travel', 'budget', 'Affordable travel tips.'),
        ('Luxury Travel', 'luxury', 'Premium travel experiences.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.travel_categories = {
            'destinations': ['destination', 'city', 'country', 'beach', 'mountain', 'island', 'visit'],
            'hotels': ['hotel', 'resort', 'accommodation', 'stay', 'airbnb', 'hostel', 'lodge'],
            'flights': ['flight', 'airline', 'airport', 'miles', 'points', 'booking', 'ticket'],
            'budget': ['budget', 'cheap', 'affordable', 'deal', 'save', 'hack', 'backpack'],
            'luxury': ['luxury', 'premium', 'first class', 'exclusive', 'boutique', 'five star'],
            'adventure': ['adventure', 'hiking', 'outdoor', 'trek', 'safari', 'explore'],
            'business': ['business travel', 'corporate', 'industry', 'tourism', 'hospitality'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch travel content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of travel content dictionaries
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
            logger.warning(f"Error getting travel categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Travel spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch travel content from RSS feed."""
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

                # Analysis
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                is_deal = self._is_deal(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'is_deal': is_deal,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'travel_content',
                    'platform': 'travel',
                    'tags': ['travel', 'tourism'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect travel categories from text."""
        categories = []
        for category, keywords in self.travel_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories or ['general']

    def _is_deal(self, text: str) -> bool:
        """Check if content is about travel deals."""
        deal_keywords = ['deal', 'sale', 'discount', 'offer', 'save', 'cheap', 'budget', '%', 'off']
        return any(kw in text for kw in deal_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['beautiful', 'amazing', 'stunning', 'best', 'paradise', 'perfect', 'love']
        negative = ['avoid', 'cancel', 'delay', 'crowded', 'expensive', 'disappointing', 'bad']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return travel category links."""
        return [
            {
                'title': f"Travel: {name}",
                'url': f'https://www.lonelyplanet.com/{slug}',
                'link': f'https://www.lonelyplanet.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Lonely Planet',
                'data_type': 'travel_category',
                'platform': 'travel',
                'tags': ['travel', 'tourism', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Top Destinations 2025', 'destinations', 'Best places to visit this year.'),
            ('Flight Deals', 'flights', 'Current flight sales and deals.'),
            ('Hotel Reviews', 'hotels', 'Latest hotel ratings and reviews.'),
            ('Budget Travel Tips', 'budget', 'Save money while traveling.'),
            ('Adventure Travel', 'adventure', 'Outdoor and adventure trips.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.lonelyplanet.com/{category}',
                'link': f'https://www.lonelyplanet.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Lonely Planet',
                'data_type': 'travel_topic',
                'platform': 'travel',
                'tags': ['travel', 'tourism', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
