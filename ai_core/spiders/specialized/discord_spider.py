"""
Discord Spider - Community Intelligence via Discord API
========================================================

Session 534: Simplified to work with spider network interface.
Uses Discord Bot API when configured, falls back to tech community RSS.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class DiscordSpider:
    """Discord spider - community discussions and pain points"""

    name = "discord"

    # Fallback tech community RSS feeds
    RSS_FEEDS = {
        'reddit_tech': 'https://www.reddit.com/r/technology/.rss',
        'reddit_programming': 'https://www.reddit.com/r/programming/.rss',
        'hackernews': 'https://news.ycombinator.com/rss',
    }

    # Community topics
    TOPICS = [
        ('AI Discussion', 'ai', 'AI and machine learning topics.'),
        ('Creator Tools', 'creators', 'Content creator discussions.'),
        ('Dev Community', 'dev', 'Developer community topics.'),
        ('Startups', 'startups', 'Startup and indie hacker discussions.'),
        ('Tech Support', 'support', 'Technical help and troubleshooting.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.bot_token = os.getenv('DISCORD_BOT_TOKEN', '')
        self.base_url = "https://discord.com/api/v10"

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch community discussions from Discord or fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of message/discussion dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Discord API if bot token is available
        if self.bot_token:
            try:
                discord_items = self._fetch_from_discord()
                for item in discord_items:
                    if item.get('url') and item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from Discord API: {e}")

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

        # Add topic links
        try:
            topics = self._get_topic_links()
            all_items.extend(topics)
        except Exception as e:
            logger.warning(f"Error getting community topics: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Discord spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_discord(self) -> List[Dict[str, Any]]:
        """Fetch messages from Discord servers the bot is in."""
        items = []

        try:
            headers = {
                'Authorization': f'Bot {self.bot_token}',
                'Content-Type': 'application/json',
            }

            # Get guilds the bot is in
            guilds_response = cached_get(
                f"{self.base_url}/users/@me/guilds",
                headers=headers,
                timeout=10
            )

            if guilds_response.status_code != 200:
                logger.warning(f"Discord API error: {guilds_response.status_code}")
                return items

            guilds = guilds_response.json()

            for guild in guilds[:3]:  # Limit servers
                guild_id = guild['id']
                guild_name = guild['name']

                # Get channels
                channels_response = cached_get(
                    f"{self.base_url}/guilds/{guild_id}/channels",
                    headers=headers,
                    timeout=10
                )

                if channels_response.status_code != 200:
                    continue

                channels = channels_response.json()
                text_channels = [c for c in channels if c.get('type') == 0]

                for channel in text_channels[:2]:
                    channel_id = channel['id']
                    channel_name = channel['name']

                    try:
                        messages_response = cached_get(
                            f"{self.base_url}/channels/{channel_id}/messages",
                            headers=headers,
                            params={'limit': 20},
                            timeout=10
                        )

                        if messages_response.status_code == 200:
                            messages = messages_response.json()

                            for msg in messages:
                                content = msg.get('content', '')
                                if content and not msg.get('author', {}).get('bot'):
                                    msg_id = msg.get('id', '')
                                    items.append({
                                        'title': content[:100] + ('...' if len(content) > 100 else ''),
                                        'url': f"discord://message/{guild_id}/{channel_id}/{msg_id}",
                                        'link': f"https://discord.com/channels/{guild_id}/{channel_id}/{msg_id}",
                                        'summary': content[:400],
                                        'description': content[:400],
                                        'author': msg.get('author', {}).get('username', ''),
                                        'channel': channel_name,
                                        'guild': guild_name,
                                        'category': self._detect_topic(content.lower()),
                                        'is_question': '?' in content,
                                        'source': f'Discord: {guild_name}',
                                        'data_type': 'discord_message',
                                        'platform': 'discord',
                                        'tags': ['discord', 'community', channel_name],
                                        'timestamp': datetime.now().isoformat(),
                                    })

                    except Exception as e:
                        logger.warning(f"Error fetching messages from {channel_name}: {e}")

        except Exception as e:
            logger.warning(f"Error with Discord API: {e}")

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
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect topic from content
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                is_question = '?' in title or any(w in text for w in ['how do', 'anyone know', 'help'])

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': topic,
                    'is_question': is_question,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'community_discussion',
                    'platform': 'discord',
                    'tags': ['community', 'tech', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect discussion topic from text."""
        topics = {
            'ai': ['ai', 'machine learning', 'gpt', 'chatbot', 'llm'],
            'programming': ['python', 'javascript', 'code', 'programming', 'developer'],
            'support': ['help', 'issue', 'problem', 'bug', 'error'],
            'tools': ['tool', 'app', 'software', 'automation'],
            'startups': ['startup', 'founder', 'business', 'launch'],
        }

        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return community topic exploration links."""
        return [
            {
                'title': f"Community: {name}",
                'url': f'https://discord.com/servers?query={slug}',
                'link': f'https://discord.com/servers?query={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Discord',
                'data_type': 'community_topic',
                'platform': 'discord',
                'tags': ['discord', 'community', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('AI Communities', 'ai', 'AI and machine learning discussions.'),
            ('Developer Chat', 'dev', 'Programming and development.'),
            ('Tech Support', 'support', 'Help and troubleshooting.'),
            ('Startup Talk', 'startups', 'Entrepreneurship discussions.'),
            ('Creator Tools', 'tools', 'Content creation tools.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://discord.com/servers?query={category}',
                'link': f'https://discord.com/servers?query={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Discord',
                'data_type': 'community_topic',
                'platform': 'discord',
                'tags': ['discord', 'community', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
