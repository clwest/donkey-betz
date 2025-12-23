"""
The Verge Spider - Consumer Tech & Culture News Intelligence
===========================================================

Session 534: Simplified to work with spider network interface.
Aggregates consumer tech, gadgets, and culture news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TheVergeSpider:
    """The Verge spider - consumer tech, reviews, and culture"""

    name = "verge"

    # The Verge and tech culture RSS feeds
    RSS_FEEDS = {
        'verge_main': 'https://www.theverge.com/rss/index.xml',
        'verge_tech': 'https://www.theverge.com/tech/rss/index.xml',
        'verge_reviews': 'https://www.theverge.com/reviews/rss/index.xml',
        'verge_science': 'https://www.theverge.com/science/rss/index.xml',
        'engadget': 'https://www.engadget.com/rss.xml',
    }

    # News categories
    CATEGORIES = [
        ('Tech', 'tech', 'Technology and gadgets.'),
        ('Reviews', 'reviews', 'Product reviews and ratings.'),
        ('Science', 'science', 'Science and discovery.'),
        ('Entertainment', 'entertainment', 'Gaming and streaming.'),
        ('Policy', 'policy', 'Tech policy and regulation.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.product_categories = {
            'smartphones': ['iphone', 'android', 'pixel', 'galaxy', 'smartphone', 'phone'],
            'computers': ['macbook', 'laptop', 'pc', 'desktop', 'chromebook', 'tablet', 'ipad'],
            'wearables': ['watch', 'airpods', 'earbuds', 'headphones', 'fitbit', 'wearable'],
            'gaming': ['playstation', 'xbox', 'nintendo', 'switch', 'game', 'gaming', 'steam'],
            'smart_home': ['smart home', 'alexa', 'google home', 'nest', 'ring', 'thermostat'],
            'ev': ['tesla', 'ev', 'electric vehicle', 'rivian', 'charging', 'lucid'],
            'ai_tools': ['chatgpt', 'ai', 'copilot', 'gemini', 'claude', 'midjourney'],
        }
        self.companies = {
            'apple': ['apple', 'iphone', 'mac', 'ipad', 'airpods', 'wwdc'],
            'google': ['google', 'android', 'pixel', 'chrome', 'youtube', 'gemini'],
            'microsoft': ['microsoft', 'windows', 'xbox', 'surface', 'copilot'],
            'meta': ['meta', 'facebook', 'instagram', 'whatsapp', 'quest'],
            'amazon': ['amazon', 'alexa', 'echo', 'kindle', 'fire', 'prime'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch consumer tech news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of tech news dictionaries
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
            logger.warning(f"Error getting tech categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"The Verge spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch tech news from RSS feed."""
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
                product_cats = self._detect_products(text)
                companies = self._detect_companies(text)
                is_review = self._is_review(text, feed_name)
                sentiment = self._analyze_sentiment(text)

                # Extract tags from entry if available
                entry_tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    entry_tags = [tag.term for tag in entry.tags[:5]]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'The Verge'),
                    'product_categories': product_cats,
                    'category': product_cats[0] if product_cats else 'general',
                    'companies_mentioned': companies,
                    'is_review': is_review,
                    'sentiment': sentiment,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'consumer_tech',
                    'platform': 'verge',
                    'tags': ['tech', 'gadgets', 'consumer'] + product_cats[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_products(self, text: str) -> List[str]:
        """Detect product categories from text."""
        categories = []
        for category, keywords in self.product_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories or ['general']

    def _detect_companies(self, text: str) -> List[str]:
        """Detect companies mentioned in text."""
        companies = []
        for company, keywords in self.companies.items():
            if any(kw in text for kw in keywords):
                companies.append(company)
        return companies

    def _is_review(self, text: str, feed_name: str) -> bool:
        """Check if content is a review."""
        if 'review' in feed_name:
            return True
        review_keywords = ['review', 'hands-on', 'tested', 'verdict', 'first look']
        return any(kw in text for kw in review_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['great', 'amazing', 'best', 'love', 'impressive', 'excellent', 'recommend']
        negative = ['disappointing', 'bad', 'poor', 'avoid', 'fails', 'broken', 'worst']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return tech category links."""
        return [
            {
                'title': f"The Verge: {name}",
                'url': f'https://www.theverge.com/{slug}',
                'link': f'https://www.theverge.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'The Verge',
                'data_type': 'tech_category',
                'platform': 'verge',
                'tags': ['tech', 'consumer', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Latest Tech News', 'tech', 'Breaking technology news.'),
            ('Product Reviews', 'reviews', 'Gadget and device reviews.'),
            ('Apple Coverage', 'apple', 'iPhone, Mac, and Apple news.'),
            ('Gaming News', 'gaming', 'Video games and console news.'),
            ('AI & ChatGPT', 'ai', 'Artificial intelligence updates.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.theverge.com/{category}',
                'link': f'https://www.theverge.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'The Verge',
                'data_type': 'tech_topic',
                'platform': 'verge',
                'tags': ['tech', 'consumer', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
