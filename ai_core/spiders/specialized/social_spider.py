"""
Social Sentiment Spider - Social Media Intelligence
====================================================

Session 534: Simplified to work with spider network interface.
Aggregates social media trends and sentiment via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SocialSentimentSpider:
    """Social sentiment spider - social media trends and sentiment tracking"""

    name = "social"

    # Social media and trends RSS feeds
    RSS_FEEDS = {
        'social_media_today': 'https://www.socialmediatoday.com/rss/all',
        'mashable_social': 'https://mashable.com/feeds/rss/social-media',
        'buffer_blog': 'https://buffer.com/resources/feed/',
        'hootsuite_blog': 'https://blog.hootsuite.com/feed/',
        'sprout_social': 'https://sproutsocial.com/insights/feed/',
    }

    # Platform categories
    CATEGORIES = [
        ('Twitter/X', 'twitter', 'Twitter and X platform news.'),
        ('Instagram', 'instagram', 'Instagram trends and features.'),
        ('TikTok', 'tiktok', 'TikTok viral content and trends.'),
        ('LinkedIn', 'linkedin', 'LinkedIn professional networking.'),
        ('YouTube', 'youtube', 'YouTube creator and video trends.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.platforms = {
            'twitter': ['twitter', 'x', 'tweet', 'elon', 'threads'],
            'instagram': ['instagram', 'reels', 'stories', 'ig', 'meta'],
            'tiktok': ['tiktok', 'viral', 'fyp', 'creator', 'short-form'],
            'linkedin': ['linkedin', 'professional', 'b2b', 'networking', 'career'],
            'youtube': ['youtube', 'video', 'subscriber', 'creator', 'shorts'],
            'facebook': ['facebook', 'meta', 'groups', 'marketplace'],
        }
        self.sentiment_keywords = {
            'bullish': ['trending', 'viral', 'growth', 'engagement', 'popular', 'success'],
            'bearish': ['decline', 'ban', 'controversy', 'outage', 'backlash', 'crisis'],
        }
        self.content_types = {
            'trends': ['trend', 'viral', 'trending', 'popular', 'hashtag'],
            'strategy': ['strategy', 'tips', 'how to', 'guide', 'marketing'],
            'news': ['update', 'feature', 'launch', 'announcement', 'change'],
            'analytics': ['analytics', 'metrics', 'data', 'insights', 'performance'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch social media news and trends from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of social media content dictionaries
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
            logger.warning(f"Error getting platform categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Social spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch social media content from RSS feed."""
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
                platform = self._detect_platform(text)
                content_type = self._detect_content_type(text)
                sentiment = self._analyze_sentiment(text)
                is_trending = self._is_trending(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'platform': platform,
                    'category': platform,
                    'content_type': content_type,
                    'sentiment': sentiment,
                    'is_trending': is_trending,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'social_media',
                    'spider_platform': 'social',
                    'tags': ['social media', platform, content_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_platform(self, text: str) -> str:
        """Detect social media platform from text."""
        for platform, keywords in self.platforms.items():
            if any(kw in text for kw in keywords):
                return platform
        return 'general'

    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        for ctype, keywords in self.content_types.items():
            if any(kw in text for kw in keywords):
                return ctype
        return 'general'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze social media sentiment."""
        bullish_count = sum(1 for word in self.sentiment_keywords['bullish'] if word in text)
        bearish_count = sum(1 for word in self.sentiment_keywords['bearish'] if word in text)

        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        return 'neutral'

    def _is_trending(self, text: str) -> bool:
        """Check if content is about trending topics."""
        trending_keywords = ['trend', 'viral', 'trending', 'popular', 'hot', 'buzz']
        return any(kw in text for kw in trending_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return social platform category links."""
        return [
            {
                'title': f"Social: {name}",
                'url': f'https://www.socialmediatoday.com/topic/{slug}/',
                'link': f'https://www.socialmediatoday.com/topic/{slug}/',
                'summary': desc,
                'description': desc,
                'platform': slug,
                'category': slug,
                'source': 'Social Media Today',
                'data_type': 'platform_category',
                'spider_platform': 'social',
                'tags': ['social media', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Social Media Trends', 'trends', 'Latest viral trends and hashtags.'),
            ('Platform Updates', 'news', 'New features and announcements.'),
            ('Marketing Strategy', 'strategy', 'Social media marketing tips.'),
            ('Analytics & Metrics', 'analytics', 'Engagement and performance data.'),
            ('Creator Economy', 'creator', 'Influencer and creator news.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.socialmediatoday.com/topic/{category}/',
                'link': f'https://www.socialmediatoday.com/topic/{category}/',
                'summary': desc,
                'description': desc,
                'platform': category,
                'category': category,
                'source': 'Social Media Today',
                'data_type': 'social_topic',
                'spider_platform': 'social',
                'tags': ['social media', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
