"""
Udemy Spider - Online Learning Marketplace Intelligence
=========================================================

Session 534: Simplified to work with spider network interface.
Aggregates e-learning and online course content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class UdemySpider:
    """Udemy spider - online course marketplace intelligence"""

    name = "udemy"

    # E-learning and course platform RSS feeds
    RSS_FEEDS = {
        'elearning_industry': 'https://elearningindustry.com/feed',
        'edtech_magazine': 'https://edtechmagazine.com/higher/rss.xml',
        'class_central': 'https://www.classcentral.com/report/feed/',
        'coursera_blog': 'https://blog.coursera.org/feed/',
        'edx_blog': 'https://blog.edx.org/feed/',
    }

    # Course categories
    CATEGORIES = [
        ('Programming', 'programming', 'Coding and software development.'),
        ('Data Science', 'data_science', 'Machine learning and analytics.'),
        ('Business', 'business', 'Management and entrepreneurship.'),
        ('Design', 'design', 'UI/UX and graphic design.'),
        ('Marketing', 'marketing', 'Digital marketing skills.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.course_topics = {
            'programming': ['python', 'javascript', 'java', 'programming', 'coding', 'web development'],
            'data_science': ['data science', 'machine learning', 'ai', 'analytics', 'deep learning', 'sql'],
            'business': ['business', 'management', 'project management', 'leadership', 'mba'],
            'marketing': ['digital marketing', 'seo', 'social media', 'content marketing', 'advertising'],
            'design': ['ui/ux', 'graphic design', 'photoshop', 'figma', 'web design'],
            'finance': ['finance', 'accounting', 'investing', 'trading', 'cryptocurrency'],
            'personal_dev': ['productivity', 'communication', 'career', 'public speaking'],
        }
        self.skill_levels = {
            'beginner': ['beginner', 'introduction', 'fundamentals', 'basics', 'getting started'],
            'intermediate': ['intermediate', 'advanced beginner', 'next level'],
            'advanced': ['advanced', 'expert', 'master', 'professional'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch e-learning content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of e-learning content dictionaries
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
            logger.warning(f"Error getting course categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Udemy spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch e-learning content from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Analysis
                text = f"{title} {description}".lower()
                topic = self._detect_topic(text)
                skill_level = self._detect_skill_level(text)
                is_trending = self._is_trending(text)
                sentiment = self._analyze_sentiment(text)

                # Extract tags from entry if available
                tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    tags = [tag.term for tag in entry.tags[:5]]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'topic': topic,
                    'category': topic,
                    'skill_level': skill_level,
                    'is_trending': is_trending,
                    'sentiment': sentiment,
                    'entry_tags': tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'e_learning',
                    'platform': 'udemy',
                    'tags': ['courses', 'e-learning', 'education', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect course topic from text."""
        for topic, keywords in self.course_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_skill_level(self, text: str) -> str:
        """Detect skill level from text."""
        for level, keywords in self.skill_levels.items():
            if any(kw in text for kw in keywords):
                return level
        return 'all_levels'

    def _is_trending(self, text: str) -> bool:
        """Check if content is about trending topics."""
        trending_keywords = ['trending', 'popular', 'top', 'best', 'most', 'new', 'hot']
        return any(kw in text for kw in trending_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['best', 'top', 'amazing', 'essential', 'learn', 'master', 'success']
        negative = ['difficult', 'hard', 'problem', 'issue', 'fail', 'avoid']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return course category links."""
        return [
            {
                'title': f"Udemy: {name}",
                'url': f'https://www.udemy.com/courses/{slug}/',
                'link': f'https://www.udemy.com/courses/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'topic': slug,
                'source': 'Udemy',
                'data_type': 'course_category',
                'platform': 'udemy',
                'tags': ['courses', 'e-learning', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Programming Courses', 'programming', 'Learn coding and development.'),
            ('Data Science Bootcamp', 'data_science', 'Machine learning and AI skills.'),
            ('Business & Management', 'business', 'Leadership and entrepreneurship.'),
            ('Digital Marketing', 'marketing', 'SEO and social media marketing.'),
            ('Design Skills', 'design', 'UI/UX and graphic design.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.udemy.com/courses/{category}/',
                'link': f'https://www.udemy.com/courses/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'topic': category,
                'source': 'Udemy',
                'data_type': 'course_topic',
                'platform': 'udemy',
                'tags': ['courses', 'e-learning', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
