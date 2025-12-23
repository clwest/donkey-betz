"""
Wired Spider - Tech Culture & Future Trends Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Aggregates tech culture, trends, and in-depth stories via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class WiredSpider:
    """Wired spider - tech culture, trends, and deep stories"""

    name = "wired"

    # Wired and tech culture RSS feeds
    RSS_FEEDS = {
        'wired_main': 'https://www.wired.com/feed/rss',
        'wired_business': 'https://www.wired.com/feed/category/business/latest/rss',
        'wired_gear': 'https://www.wired.com/feed/category/gear/latest/rss',
        'wired_science': 'https://www.wired.com/feed/category/science/latest/rss',
        'wired_security': 'https://www.wired.com/feed/category/security/latest/rss',
    }

    # News categories
    CATEGORIES = [
        ('Business', 'business', 'Tech business and startups.'),
        ('Gear', 'gear', 'Gadgets and product reviews.'),
        ('Science', 'science', 'Science and discovery.'),
        ('Security', 'security', 'Cybersecurity and privacy.'),
        ('Culture', 'culture', 'Tech culture and society.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.topic_categories = {
            'ai_future': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'future', 'machine learning'],
            'cybersecurity': ['security', 'hacker', 'breach', 'privacy', 'encryption', 'cyberattack'],
            'culture': ['culture', 'social media', 'internet', 'digital life', 'online', 'community'],
            'gadgets': ['gadget', 'device', 'gear', 'review', 'best', 'wired recommends'],
            'science': ['science', 'physics', 'biology', 'space', 'climate', 'discovery'],
            'business': ['business', 'startup', 'company', 'silicon valley', 'tech industry'],
            'transportation': ['car', 'ev', 'tesla', 'autonomous', 'transportation', 'self-driving'],
            'environment': ['climate', 'sustainability', 'environment', 'renewable', 'green'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch tech culture news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of tech culture content dictionaries
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
            logger.warning(f"Error getting Wired categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Wired spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch tech culture content from RSS feed."""
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
                topics = self._detect_topics(text)
                story_type = self._detect_story_type(text)
                is_security = 'cybersecurity' in topics
                is_future_focused = self._is_future_focused(text)
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
                    'author': entry.get('author', 'Wired'),
                    'topics': topics,
                    'category': topics[0] if topics else 'general',
                    'story_type': story_type,
                    'is_security_related': is_security,
                    'is_future_focused': is_future_focused,
                    'sentiment': sentiment,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'tech_culture',
                    'platform': 'wired',
                    'tags': ['tech', 'culture', 'wired'] + topics[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topics(self, text: str) -> List[str]:
        """Detect topics from text."""
        topics = []
        for topic, keywords in self.topic_categories.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        return topics or ['general']

    def _detect_story_type(self, text: str) -> str:
        """Detect story type from text."""
        story_types = {
            'longform': ['deep dive', 'investigation', 'inside', 'exclusive', 'untold'],
            'review': ['review', 'hands-on', 'tested', 'recommends', 'best'],
            'analysis': ['why', 'how', 'what it means', 'explained', 'future of'],
            'news': ['breaking', 'announces', 'launches', 'just', 'new'],
        }
        for stype, keywords in story_types.items():
            if any(kw in text for kw in keywords):
                return stype
        return 'news'

    def _is_future_focused(self, text: str) -> bool:
        """Check if content is future-focused."""
        future_keywords = ['future', 'will', 'next', 'coming', '2025', '2026', 'prediction']
        return any(kw in text for kw in future_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['breakthrough', 'innovative', 'exciting', 'promising', 'impressive']
        negative = ['warning', 'danger', 'threat', 'crisis', 'failure', 'problem']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'optimistic'
        elif neg_count > pos_count:
            return 'critical'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Wired category links."""
        return [
            {
                'title': f"Wired: {name}",
                'url': f'https://www.wired.com/category/{slug}/',
                'link': f'https://www.wired.com/category/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Wired',
                'data_type': 'culture_category',
                'platform': 'wired',
                'tags': ['tech', 'culture', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('AI & Future Tech', 'ai', 'Artificial intelligence and future trends.'),
            ('Cybersecurity News', 'security', 'Hacking, privacy, and security.'),
            ('Gear & Reviews', 'gear', 'Gadget reviews and recommendations.'),
            ('Science & Discovery', 'science', 'Scientific breakthroughs.'),
            ('Tech Business', 'business', 'Silicon Valley and startups.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.wired.com/category/{category}/',
                'link': f'https://www.wired.com/category/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Wired',
                'data_type': 'culture_topic',
                'platform': 'wired',
                'tags': ['tech', 'culture', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
