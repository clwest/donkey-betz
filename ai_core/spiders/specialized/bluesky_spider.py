"""
BlueSky Spider - Social Media Intelligence (Twitter/X Alternative)
===================================================================

Session 534: Simplified to work with spider network interface.
Uses BlueSky API when credentials available, falls back to social RSS feeds.
"""

import os
import requests
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BlueSkySpider:
    """BlueSky spider - social media sentiment and discussions"""

    name = "bluesky"

    # Fallback social/tech RSS feeds
    RSS_FEEDS = {
        'ycombinator': 'https://news.ycombinator.com/rss',
        'lobsters': 'https://lobste.rs/rss',
        'techmeme': 'https://www.techmeme.com/feed.xml',
    }

    # Social topic categories
    TOPICS = [
        ('AI Tools', 'ai-tools', 'AI and automation discussions.'),
        ('Creator Economy', 'creators', 'Content creator topics.'),
        ('Startups', 'startups', 'Startup ecosystem discussions.'),
        ('Tech Industry', 'tech', 'Technology industry news.'),
        ('Open Source', 'opensource', 'Open source projects.'),
        ('Web Development', 'webdev', 'Web development topics.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.identifier = os.getenv('BLUESKY_IDENTIFIER', '')
        self.password = os.getenv('BLUESKY_PASSWORD', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch social discussions from BlueSky or fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of post/discussion dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try BlueSky API if credentials available
        if self.identifier and self.password:
            try:
                api_items = self._fetch_from_bluesky()
                for item in api_items:
                    if item.get('url') and item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching BlueSky API: {e}")

        # Fetch from fallback RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add topic exploration links
        try:
            topics = self._get_topic_links()
            all_items.extend(topics)
        except Exception as e:
            logger.warning(f"Error getting social topics: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"BlueSky spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_bluesky(self) -> List[Dict[str, Any]]:
        """Fetch posts from BlueSky API."""
        items = []

        try:
            # Authenticate
            auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
            auth_response = requests.post(auth_url, json={
                "identifier": self.identifier,
                "password": self.password
            }, timeout=10)

            if auth_response.status_code != 200:
                logger.warning("BlueSky authentication failed")
                return items

            auth_data = auth_response.json()
            access_token = auth_data.get('accessJwt')
            headers = {'Authorization': f'Bearer {access_token}'}

            # Search for relevant posts
            search_terms = ['AI tools', 'content creator', 'stable diffusion', 'startup']

            for term in search_terms[:3]:
                try:
                    search_url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
                    params = {'q': term, 'limit': 15}

                    response = cached_get(search_url, headers=headers, params=params, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        for post in data.get('posts', []):
                            record = post.get('record', {})
                            author = post.get('author', {})

                            items.append({
                                'title': record.get('text', '')[:100],
                                'url': post.get('uri', ''),
                                'link': f"https://bsky.app/profile/{author.get('handle', '')}/post/{post.get('uri', '').split('/')[-1]}",
                                'summary': record.get('text', ''),
                                'description': record.get('text', ''),
                                'author': author.get('handle', ''),
                                'published': record.get('createdAt', ''),
                                'likes': post.get('likeCount', 0),
                                'reposts': post.get('repostCount', 0),
                                'category': term.replace(' ', '-').lower(),
                                'source': 'BlueSky',
                                'data_type': 'social_post',
                                'platform': 'bluesky',
                                'tags': ['social', 'bluesky', 'discussion', term.split()[0].lower()],
                                'timestamp': datetime.now().isoformat(),
                            })
                except Exception as e:
                    logger.warning(f"Error searching BlueSky for '{term}': {e}")

        except Exception as e:
            logger.warning(f"Error with BlueSky API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch discussions from RSS feed."""
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
                    description = re.sub(r'<[^>]+>', '', description)[:400]

                # Detect topic from content
                text = f"{title} {description}".lower()
                topic = self._detect_topic(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': topic,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'social_discussion',
                    'platform': 'bluesky',
                    'tags': ['social', 'tech', 'discussion', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect discussion topic from text."""
        topics = {
            'ai': ['ai', 'machine learning', 'gpt', 'llm', 'artificial intelligence'],
            'creator': ['creator', 'content', 'youtube', 'podcast', 'newsletter'],
            'startup': ['startup', 'founder', 'funding', 'vc', 'venture'],
            'webdev': ['javascript', 'react', 'web', 'frontend', 'backend'],
            'opensource': ['open source', 'github', 'linux', 'oss'],
        }

        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'tech'

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return BlueSky topic exploration links."""
        return [
            {
                'title': f"BlueSky: {name}",
                'url': f'https://bsky.app/search?q={slug}',
                'link': f'https://bsky.app/search?q={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'BlueSky',
                'data_type': 'social_topic',
                'platform': 'bluesky',
                'tags': ['social', 'bluesky', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('AI Discussions', 'ai', 'AI and automation conversations.'),
            ('Tech News', 'tech', 'Technology industry discussions.'),
            ('Startups', 'startups', 'Startup ecosystem topics.'),
            ('Creator Economy', 'creators', 'Content creator discussions.'),
            ('Open Source', 'opensource', 'Open source projects.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://bsky.app/search?q={category}',
                'link': f'https://bsky.app/search?q={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'BlueSky',
                'data_type': 'social_topic',
                'platform': 'bluesky',
                'tags': ['social', 'bluesky', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
