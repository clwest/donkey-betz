"""
Teachable Spider - Online Course & Creator Economy Intelligence
================================================================

Session 534: Simplified to work with spider network interface.
Aggregates online course and creator economy content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TeachableSpider:
    """Teachable spider - online course and creator economy intelligence"""

    name = "teachable"

    # Online course and creator economy RSS feeds
    RSS_FEEDS = {
        'teachable_blog': 'https://teachable.com/blog/feed',
        'thinkific_blog': 'https://www.thinkific.com/blog/feed/',
        'kajabi_blog': 'https://kajabi.com/blog/rss.xml',
        'podia_blog': 'https://www.podia.com/articles/feed',
        'creatoreconomy': 'https://newsletter.creatoreconomy.so/feed',
    }

    # Course categories
    CATEGORIES = [
        ('Business Courses', 'business', 'Entrepreneurship and business education.'),
        ('Tech & Coding', 'tech', 'Programming and technical skills.'),
        ('Creative Skills', 'creative', 'Design, video, and artistic courses.'),
        ('Personal Development', 'personal', 'Productivity and mindset courses.'),
        ('Marketing', 'marketing', 'Digital marketing and growth.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.course_categories = {
            'business': ['business', 'entrepreneurship', 'marketing', 'sales', 'startup'],
            'tech': ['programming', 'coding', 'web development', 'software', 'tech', 'ai', 'data'],
            'creative': ['design', 'photography', 'video', 'music', 'art', 'writing'],
            'health': ['health', 'fitness', 'nutrition', 'wellness', 'yoga', 'meditation'],
            'personal': ['productivity', 'mindset', 'leadership', 'communication', 'personal'],
            'finance': ['investing', 'trading', 'money', 'finance', 'wealth', 'crypto'],
        }
        self.monetization_models = {
            'one_time': ['one-time', 'single payment', 'lifetime access'],
            'subscription': ['membership', 'subscription', 'monthly', 'recurring'],
            'cohort': ['cohort', 'live', 'bootcamp', 'group coaching'],
            'freemium': ['free', 'freemium', 'lead magnet', 'free course'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch online course and creator economy content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of course/creator content dictionaries
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

        logger.info(f"Teachable spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch creator economy content from RSS feed."""
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
                category = self._detect_category(text)
                monetization = self._detect_monetization(text)
                is_success_story = self._is_success_story(text)
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
                    'monetization_model': monetization,
                    'is_success_story': is_success_story,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creator_economy',
                    'platform': 'teachable',
                    'tags': ['courses', 'creator economy', 'online learning', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect course category from text."""
        for category, keywords in self.course_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_monetization(self, text: str) -> str:
        """Detect monetization model from text."""
        for model, keywords in self.monetization_models.items():
            if any(kw in text for kw in keywords):
                return model
        return 'unknown'

    def _is_success_story(self, text: str) -> bool:
        """Check if content is a success story."""
        success_keywords = ['revenue', 'income', 'earnings', 'sales', '$', 'students', 'enrollments', 'launch']
        return any(kw in text for kw in success_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['success', 'grow', 'launch', 'revenue', 'students', 'amazing', 'best']
        negative = ['fail', 'mistake', 'avoid', 'problem', 'struggle', 'difficult']

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
                'title': f"Teachable: {name}",
                'url': f'https://teachable.com/blog/category/{slug}',
                'link': f'https://teachable.com/blog/category/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Teachable',
                'data_type': 'course_category',
                'platform': 'teachable',
                'tags': ['courses', 'online learning', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Course Creation Guide', 'creation', 'How to create online courses.'),
            ('Marketing Your Course', 'marketing', 'Promote and sell your courses.'),
            ('Building Community', 'community', 'Engage and retain students.'),
            ('Pricing Strategies', 'pricing', 'How to price your courses.'),
            ('Creator Success Stories', 'success', 'Inspiring creator journeys.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://teachable.com/blog/{category}',
                'link': f'https://teachable.com/blog/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Teachable',
                'data_type': 'course_topic',
                'platform': 'teachable',
                'tags': ['courses', 'online learning', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
