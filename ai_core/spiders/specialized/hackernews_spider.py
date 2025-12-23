"""
Hacker News Spider - Tech Community & Startup Intelligence
===========================================================

Session 534: Simplified to work with spider network interface.
Uses Hacker News RSS feeds for tech discussions and startup news.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HackerNewsSpider:
    """Hacker News spider - tech community and startup intelligence"""

    name = "hackernews"

    # HN RSS feeds
    RSS_FEEDS = {
        'front_page': 'https://hnrss.org/frontpage',
        'best': 'https://hnrss.org/best',
        'newest': 'https://hnrss.org/newest?count=30',
        'show_hn': 'https://hnrss.org/show',
        'ask_hn': 'https://hnrss.org/ask',
    }

    # Topic categories
    TOPICS = [
        ('AI & ML', 'ai_ml', 'Artificial intelligence and machine learning.'),
        ('Startups', 'startups', 'Startup news and YC companies.'),
        ('Programming', 'programming', 'Programming discussions.'),
        ('Web Dev', 'webdev', 'Web development topics.'),
        ('DevOps', 'devops', 'DevOps and infrastructure.'),
        ('Security', 'security', 'Security and privacy.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.tech_topics = {
            'programming': ['programming', 'code', 'software', 'developer', 'algorithm', 'api'],
            'ai_ml': ['ai', 'machine learning', 'gpt', 'llm', 'neural', 'openai', 'anthropic'],
            'startups': ['startup', 'yc', 'founder', 'funding', 'launch', 'vc', 'seed'],
            'webdev': ['web', 'javascript', 'react', 'frontend', 'backend', 'css', 'html'],
            'devops': ['devops', 'kubernetes', 'docker', 'aws', 'cloud', 'infrastructure'],
            'security': ['security', 'hack', 'vulnerability', 'privacy', 'encryption'],
            'career': ['hiring', 'job', 'career', 'salary', 'interview', 'remote'],
            'open_source': ['open source', 'github', 'oss', 'linux', 'mit license'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Hacker News content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of HN content dictionaries
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
            logger.warning(f"Error getting HN topics: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Hacker News spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch stories from HN RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Extract points and comments from description
                points = 0
                comments = 0
                if summary:
                    points_match = re.search(r'(\d+)\s*points?', summary.lower())
                    if points_match:
                        points = int(points_match.group(1))
                    comments_match = re.search(r'(\d+)\s*comments?', summary.lower())
                    if comments_match:
                        comments = int(comments_match.group(1))

                # Detect topic and content type
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                content_type = self._detect_content_type(text, feed_name)
                is_hot = points > 100 or comments > 50

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'points': points,
                    'comments': comments,
                    'topic': topic,
                    'content_type': content_type,
                    'is_hot': is_hot,
                    'is_show_hn': 'show hn' in text,
                    'is_ask_hn': 'ask hn' in text,
                    'source': 'Hacker News',
                    'feed_type': feed_name,
                    'data_type': 'tech_community',
                    'platform': 'hackernews',
                    'tags': ['hackernews', 'tech', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect tech topic from text."""
        for topic, keywords in self.tech_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_content_type(self, text: str, feed_name: str) -> str:
        """Detect content type from text and feed."""
        if 'show_hn' in feed_name or 'show hn' in text:
            return 'show_hn'
        elif 'ask_hn' in feed_name or 'ask hn' in text:
            return 'ask_hn'
        elif any(word in text for word in ['why', 'how', 'what do you think']):
            return 'discussion'
        return 'news'

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return HN topic exploration links."""
        return [
            {
                'title': f"HN: {name}",
                'url': f'https://news.ycombinator.com/',
                'link': f'https://news.ycombinator.com/',
                'summary': desc,
                'description': desc,
                'topic': slug,
                'category': slug,
                'source': 'Hacker News',
                'data_type': 'hn_topic',
                'platform': 'hackernews',
                'tags': ['hackernews', 'tech', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('HN Front Page', 'frontpage', 'Top stories from Hacker News.'),
            ('Show HN', 'show', 'New projects and launches.'),
            ('Ask HN', 'ask', 'Community questions.'),
            ('Best Stories', 'best', 'Highest-rated submissions.'),
            ('New Stories', 'new', 'Latest submissions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://news.ycombinator.com/{category}',
                'link': f'https://news.ycombinator.com/{category}',
                'summary': desc,
                'description': desc,
                'topic': category,
                'category': category,
                'source': 'Hacker News',
                'data_type': 'hn_topic',
                'platform': 'hackernews',
                'tags': ['hackernews', 'tech', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
