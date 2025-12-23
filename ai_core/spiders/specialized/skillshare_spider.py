"""
Skillshare Spider - Creative Learning & Project-Based Education Intelligence
=============================================================================

Session 534: Simplified to work with spider network interface.
Aggregates creative learning and design education content via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SkillshareSpider:
    """Skillshare spider - creative learning and project-based education"""

    name = "skillshare"

    # Creative education RSS feeds
    RSS_FEEDS = {
        'creative_bloq': 'https://www.creativebloq.com/feed',
        'design_shack': 'https://designshack.net/feed/',
        'skillshare_blog': 'https://www.skillshare.com/blog/feed',
        'ux_collective': 'https://uxdesign.cc/feed',
        'dribbble_stories': 'https://dribbble.com/stories.rss',
    }

    # Learning categories
    CATEGORIES = [
        ('Illustration', 'illustration', 'Drawing and digital art.'),
        ('Graphic Design', 'graphic_design', 'Logo, branding, and typography.'),
        ('UI/UX Design', 'ui_ux', 'User interface and experience.'),
        ('Photography', 'photography', 'Photo editing and techniques.'),
        ('Video & Animation', 'video', 'Motion graphics and filmmaking.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.creative_categories = {
            'illustration': ['illustration', 'drawing', 'sketch', 'digital art', 'character design'],
            'graphic_design': ['graphic design', 'logo', 'branding', 'typography', 'layout'],
            'ui_ux': ['ui', 'ux', 'user interface', 'user experience', 'product design', 'figma'],
            'photography': ['photography', 'photo editing', 'lightroom', 'photoshop', 'camera'],
            'video': ['video editing', 'filmmaking', 'animation', 'motion graphics', 'after effects'],
            'writing': ['creative writing', 'copywriting', 'storytelling', 'content', 'blogging'],
            'crafts': ['crafts', 'diy', 'handmade', 'pottery', 'knitting', 'calligraphy'],
        }
        self.skill_aspects = {
            'tools': ['photoshop', 'illustrator', 'figma', 'procreate', 'premiere', 'after effects'],
            'techniques': ['technique', 'how to', 'tips', 'tutorial', 'guide', 'masterclass'],
            'business': ['freelance', 'client', 'pricing', 'portfolio', 'career'],
            'trends': ['trend', 'style', 'modern', '2024', '2025', 'new'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch creative learning content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of creative learning content dictionaries
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
            logger.warning(f"Error getting learning categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Skillshare spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch creative learning content from RSS feed."""
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
                aspects = self._detect_aspects(text)
                is_tutorial = self._is_tutorial(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'category': category,
                    'aspects': aspects,
                    'is_tutorial': is_tutorial,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creative_learning',
                    'platform': 'skillshare',
                    'tags': ['creative', 'learning', 'design', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect creative category from text."""
        for category, keywords in self.creative_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_aspects(self, text: str) -> List[str]:
        """Detect skill aspects from text."""
        aspects = []
        for aspect, keywords in self.skill_aspects.items():
            if any(kw in text for kw in keywords):
                aspects.append(aspect)
        return aspects

    def _is_tutorial(self, text: str) -> bool:
        """Check if content is a tutorial."""
        tutorial_keywords = ['tutorial', 'how to', 'guide', 'learn', 'step by step', 'course', 'class']
        return any(kw in text for kw in tutorial_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['amazing', 'creative', 'inspiring', 'beautiful', 'best', 'master', 'pro']
        negative = ['difficult', 'mistake', 'avoid', 'bad', 'hard', 'fail']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return creative learning category links."""
        return [
            {
                'title': f"Skillshare: {name}",
                'url': f'https://www.skillshare.com/browse/{slug}',
                'link': f'https://www.skillshare.com/browse/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Skillshare',
                'data_type': 'learning_category',
                'platform': 'skillshare',
                'tags': ['creative', 'learning', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Illustration Basics', 'illustration', 'Learn digital illustration.'),
            ('Graphic Design Fundamentals', 'graphic_design', 'Logo and branding design.'),
            ('UI/UX Design Course', 'ui_ux', 'User experience design.'),
            ('Photography for Beginners', 'photography', 'Camera and editing skills.'),
            ('Motion Graphics', 'video', 'Animation and video editing.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.skillshare.com/classes/{category}',
                'link': f'https://www.skillshare.com/classes/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Skillshare',
                'data_type': 'learning_topic',
                'platform': 'skillshare',
                'tags': ['creative', 'learning', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
