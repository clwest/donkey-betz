"""
Hashnode Spider - Developer Blogging & Knowledge Intelligence
===============================================================

Session 534: Simplified to work with spider network interface.
Uses developer blogging RSS feeds for technical content.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HashnodeSpider:
    """Hashnode spider - developer blogging and knowledge intelligence"""

    name = "hashnode"

    # Developer blogging RSS feeds
    RSS_FEEDS = {
        'hashnode_featured': 'https://hashnode.com/rss',
        'dev_to': 'https://dev.to/feed',
        'coding_horror': 'https://blog.codinghorror.com/rss/',
        'css_tricks': 'https://css-tricks.com/feed/',
        'smashing_mag': 'https://www.smashingmagazine.com/feed/',
    }

    # Blog topics
    TOPICS = [
        ('Web Development', 'web_development', 'Frontend and backend web dev.'),
        ('DevOps', 'devops', 'CI/CD, Docker, Kubernetes.'),
        ('Programming', 'programming', 'Coding techniques and best practices.'),
        ('Career', 'career', 'Developer career advice.'),
        ('Open Source', 'open_source', 'Open source contributions.'),
        ('Learning', 'learning', 'Learning resources and roadmaps.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.blog_topics = {
            'web_development': ['web', 'javascript', 'react', 'frontend', 'backend', 'api'],
            'devops': ['devops', 'ci/cd', 'docker', 'kubernetes', 'deployment', 'infrastructure'],
            'programming': ['programming', 'coding', 'algorithm', 'data structure', 'clean code'],
            'career': ['career', 'interview', 'job', 'resume', 'freelance', 'remote'],
            'productivity': ['productivity', 'workflow', 'tools', 'efficiency', 'time management'],
            'open_source': ['open source', 'github', 'contributing', 'community', 'oss'],
            'learning': ['learning', 'study', 'beginner', 'roadmap', 'resources'],
        }
        self.article_types = {
            'tutorial': ['tutorial', 'how to', 'guide', 'step by step', 'walkthrough'],
            'deep_dive': ['deep dive', 'in-depth', 'comprehensive', 'complete guide'],
            'opinion': ['opinion', 'thoughts', 'why i', 'my experience'],
            'comparison': ['vs', 'comparison', 'compared', 'which is better'],
            'list': ['top', 'best', 'list', 'resources', 'tools'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch developer blog content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of blog content dictionaries
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

        # Add topic links
        try:
            topics = self._get_topic_links()
            all_items.extend(topics)
        except Exception as e:
            logger.warning(f"Error getting blog topics: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Hashnode spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from developer blogging RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Extract tags if available
                tags = []
                if hasattr(entry, 'tags'):
                    tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')][:5]

                # Detect topic and article type
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                article_type = self._detect_article_type(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Developer'),
                    'topic': topic,
                    'article_type': article_type,
                    'is_tutorial': article_type == 'tutorial',
                    'is_deep_dive': article_type == 'deep_dive',
                    'entry_tags': tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'developer_blog',
                    'platform': 'hashnode',
                    'tags': ['developer', 'blog', topic] + tags[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect blog topic from text."""
        for topic, keywords in self.blog_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_article_type(self, text: str) -> str:
        """Detect article type from text."""
        for atype, keywords in self.article_types.items():
            if any(kw in text for kw in keywords):
                return atype
        return 'article'

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return blog topic exploration links."""
        return [
            {
                'title': f"Blogs: {name}",
                'url': f'https://hashnode.com/n/{slug}',
                'link': f'https://hashnode.com/n/{slug}',
                'summary': desc,
                'description': desc,
                'topic': slug,
                'category': slug,
                'source': 'Hashnode',
                'data_type': 'blog_topic',
                'platform': 'hashnode',
                'tags': ['developer', 'blog', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Web Development', 'web', 'Frontend and backend development.'),
            ('JavaScript', 'javascript', 'JavaScript tutorials and tips.'),
            ('React', 'react', 'React development content.'),
            ('Python', 'python', 'Python programming.'),
            ('DevOps', 'devops', 'DevOps and infrastructure.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://hashnode.com/n/{category}',
                'link': f'https://hashnode.com/n/{category}',
                'summary': desc,
                'description': desc,
                'topic': category,
                'category': category,
                'source': 'Hashnode',
                'data_type': 'blog_topic',
                'platform': 'hashnode',
                'tags': ['developer', 'blog', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
