"""
Dev.to Spider - Developer Community & Content Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
Uses Dev.to RSS feeds for developer articles and tutorials.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class DevToSpider:
    """Dev.to spider - developer community and content intelligence"""

    name = "devto"

    # Dev.to RSS feeds by tag
    RSS_FEEDS = {
        'top': 'https://dev.to/feed',
        'javascript': 'https://dev.to/feed/tag/javascript',
        'python': 'https://dev.to/feed/tag/python',
        'webdev': 'https://dev.to/feed/tag/webdev',
        'beginners': 'https://dev.to/feed/tag/beginners',
    }

    # Developer topic categories
    CATEGORIES = [
        ('JavaScript', 'javascript', 'JavaScript and TypeScript content.'),
        ('Python', 'python', 'Python programming tutorials.'),
        ('Web Development', 'webdev', 'Frontend and backend development.'),
        ('DevOps', 'devops', 'CI/CD, Docker, Kubernetes.'),
        ('AI & ML', 'ai', 'Machine learning and data science.'),
        ('Career', 'career', 'Developer career advice.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.dev_topics = {
            'javascript': ['javascript', 'js', 'typescript', 'node', 'react', 'vue', 'angular'],
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'webdev': ['web development', 'html', 'css', 'frontend', 'backend', 'fullstack'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws', 'cloud'],
            'career': ['career', 'job', 'interview', 'resume', 'hiring', 'remote work'],
            'ai_ml': ['machine learning', 'ai', 'data science', 'neural', 'tensorflow'],
        }
        self.content_types = {
            'tutorial': ['tutorial', 'how to', 'step by step', 'guide', 'walkthrough'],
            'discussion': ['thoughts on', 'opinion', 'debate', 'unpopular'],
            'showoff': ['built', 'created', 'made', 'launched', 'introducing'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch developer content from Dev.to RSS feeds.

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

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Dev.to categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Dev.to spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from Dev.to RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Get tags if available
                tags = []
                if hasattr(entry, 'tags'):
                    tags = [tag.term for tag in entry.tags][:5]

                # Detect dev topic and content type
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                content_type = self._detect_content_type(text)
                is_beginner = self._is_beginner_friendly(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Developer'),
                    'category': topic,
                    'dev_topic': topic,
                    'content_type': content_type,
                    'is_tutorial': content_type == 'tutorial',
                    'is_beginner': is_beginner,
                    'article_tags': tags,
                    'source': 'Dev.to',
                    'data_type': 'developer_article',
                    'platform': 'devto',
                    'tags': ['developer', 'programming', topic] + tags[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect developer topic from text."""
        for topic, keywords in self.dev_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        for ctype, keywords in self.content_types.items():
            if any(kw in text for kw in keywords):
                return ctype
        return 'article'

    def _is_beginner_friendly(self, text: str) -> bool:
        """Check if content is beginner-friendly."""
        beginner_words = ['beginner', 'getting started', 'introduction', 'basics', 'first']
        return any(word in text for word in beginner_words)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Dev.to category links."""
        return [
            {
                'title': f"Dev.to: {name}",
                'url': f'https://dev.to/t/{slug}',
                'link': f'https://dev.to/t/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Dev.to',
                'data_type': 'developer_category',
                'platform': 'devto',
                'tags': ['developer', 'programming', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('JavaScript Tutorials', 'javascript', 'JS and TypeScript content.'),
            ('Python Programming', 'python', 'Python tutorials and guides.'),
            ('Web Development', 'webdev', 'Frontend and backend tips.'),
            ('Beginner Guides', 'beginners', 'Content for new developers.'),
            ('Career Advice', 'career', 'Developer career resources.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://dev.to/t/{category}',
                'link': f'https://dev.to/t/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Dev.to',
                'data_type': 'developer_topic',
                'platform': 'devto',
                'tags': ['developer', 'programming', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
