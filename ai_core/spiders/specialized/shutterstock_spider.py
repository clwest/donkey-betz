"""
Shutterstock Spider - Stock Media & Licensing Intelligence
=============================================================

Session 534: Simplified to work with spider network interface.
Aggregates stock media news and photography content via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ShutterstockSpider:
    """Shutterstock spider - stock media and licensing intelligence"""

    name = "shutterstock"

    # Stock media and photography RSS feeds
    RSS_FEEDS = {
        'shutterstock_blog': 'https://www.shutterstock.com/blog/feed',
        'petapixel': 'https://petapixel.com/feed/',
        'photography_life': 'https://photographylife.com/feed',
        'fstoppers': 'https://fstoppers.com/rss.xml',
        'dpreview': 'https://www.dpreview.com/feeds/news.xml',
    }

    # Media categories
    CATEGORIES = [
        ('Stock Photos', 'photos', 'Stock photography and image licensing.'),
        ('Stock Video', 'video', 'Stock footage and video clips.'),
        ('Vectors', 'vectors', 'Vector graphics and illustrations.'),
        ('Music', 'music', 'Royalty-free music and audio.'),
        ('Editorial', 'editorial', 'News and editorial content.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.media_types = {
            'photos': ['photo', 'image', 'photography', 'stock photo', 'picture', 'portrait'],
            'video': ['video', 'footage', 'stock video', 'clip', '4k', 'hd', 'motion'],
            'music': ['music', 'audio', 'soundtrack', 'royalty-free', 'track', 'sound'],
            'editorial': ['editorial', 'news', 'event', 'celebrity', 'sports', 'journalism'],
            'vectors': ['vector', 'illustration', 'icon', 'graphic', 'eps', 'svg'],
        }
        self.use_cases = {
            'commercial': ['commercial', 'advertising', 'marketing', 'brand', 'business'],
            'social_media': ['social media', 'instagram', 'facebook', 'tiktok', 'youtube'],
            'web': ['website', 'blog', 'web design', 'landing page', 'banner'],
            'print': ['print', 'brochure', 'flyer', 'poster', 'magazine'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch stock media news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of stock media content dictionaries
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
            logger.warning(f"Error getting media categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Shutterstock spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch stock media content from RSS feed."""
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
                media_type = self._detect_media_type(text)
                use_cases = self._detect_use_cases(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'media_type': media_type,
                    'category': media_type,
                    'use_cases': use_cases,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'stock_media',
                    'platform': 'shutterstock',
                    'tags': ['stock media', 'photography', media_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_media_type(self, text: str) -> str:
        """Detect media type from text."""
        for mtype, keywords in self.media_types.items():
            if any(kw in text for kw in keywords):
                return mtype
        return 'general'

    def _detect_use_cases(self, text: str) -> List[str]:
        """Detect use cases mentioned in text."""
        use_cases = []
        for use_case, keywords in self.use_cases.items():
            if any(kw in text for kw in keywords):
                use_cases.append(use_case)
        return use_cases

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['beautiful', 'stunning', 'amazing', 'creative', 'trending', 'best', 'top']
        negative = ['avoid', 'mistake', 'problem', 'bad', 'cheap', 'poor']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return stock media category links."""
        return [
            {
                'title': f"Shutterstock: {name}",
                'url': f'https://www.shutterstock.com/{slug}/',
                'link': f'https://www.shutterstock.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'media_type': slug,
                'source': 'Shutterstock',
                'data_type': 'media_category',
                'platform': 'shutterstock',
                'tags': ['stock media', 'shutterstock', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Stock Photography Tips', 'photos', 'How to choose and use stock photos.'),
            ('Video Production', 'video', 'Stock footage and video editing.'),
            ('Vector Graphics', 'vectors', 'Illustrations and graphic design.'),
            ('Royalty-Free Music', 'music', 'Audio for videos and projects.'),
            ('Photography Trends', 'trends', 'Visual trends and styles.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.shutterstock.com/blog/{category}/',
                'link': f'https://www.shutterstock.com/blog/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'media_type': category,
                'source': 'Shutterstock',
                'data_type': 'media_topic',
                'platform': 'shutterstock',
                'tags': ['stock media', 'photography', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
