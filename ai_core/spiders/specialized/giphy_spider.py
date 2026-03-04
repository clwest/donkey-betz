"""
Giphy Spider - GIF & Meme Trends Intelligence
==============================================

Session 534: Simplified to work with spider network interface.
Uses Giphy API for trending GIFs and meme culture.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class GiphySpider:
    """Giphy spider - trending GIFs, stickers, and meme culture"""

    name = "giphy"

    BASE_URL = "https://api.giphy.com/v1"

    # Fallback meme/culture RSS feeds
    RSS_FEEDS = {
        'know_your_meme': 'https://knowyourmeme.com/newsfeed.rss',
        'reddit_memes': 'https://www.reddit.com/r/memes/.rss',
    }

    # GIF categories
    CATEGORIES = [
        ('Trending', 'trending', 'Trending GIFs right now.'),
        ('Reactions', 'reactions', 'Reaction GIFs for conversations.'),
        ('Memes', 'memes', 'Popular meme content.'),
        ('Stickers', 'stickers', 'Animated stickers.'),
        ('Entertainment', 'entertainment', 'Movies, TV, and pop culture.'),
        ('Sports', 'sports', 'Sports highlights and celebrations.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.api_key = os.getenv('GIPHY_API_KEY', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch trending GIFs from Giphy and fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of GIF/meme dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Giphy API if key is available
        if self.api_key:
            try:
                api_items = self._fetch_from_giphy()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from Giphy API: {e}")

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

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Giphy categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Giphy spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_giphy(self) -> List[Dict[str, Any]]:
        """Fetch trending GIFs from Giphy API."""
        items = []

        try:
            # Fetch trending GIFs
            response = cached_get(
                f"{self.BASE_URL}/gifs/trending",
                params={
                    'api_key': self.api_key,
                    'limit': 20,
                    'rating': 'pg-13'
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                gifs = data.get('data', [])

                for gif in gifs:
                    items.append({
                        'title': gif.get('title', 'Trending GIF'),
                        'url': gif.get('url', ''),
                        'link': gif.get('url', ''),
                        'summary': f"Trending GIF by @{gif.get('username', 'giphy')}",
                        'description': gif.get('title', ''),
                        'gif_id': gif.get('id', ''),
                        'embed_url': gif.get('embed_url', ''),
                        'preview_url': gif.get('images', {}).get('preview_gif', {}).get('url', ''),
                        'original_url': gif.get('images', {}).get('original', {}).get('url', ''),
                        'username': gif.get('username', ''),
                        'rating': gif.get('rating', 'pg'),
                        'category': 'trending',
                        'content_type': 'gif',
                        'source': 'Giphy',
                        'data_type': 'gif',
                        'platform': 'giphy',
                        'tags': ['gif', 'trending', 'meme'],
                        'timestamp': datetime.now().isoformat(),
                    })

            # Fetch trending stickers
            response = cached_get(
                f"{self.BASE_URL}/stickers/trending",
                params={
                    'api_key': self.api_key,
                    'limit': 10,
                    'rating': 'pg-13'
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                stickers = data.get('data', [])

                for sticker in stickers:
                    items.append({
                        'title': sticker.get('title', 'Trending Sticker'),
                        'url': sticker.get('url', ''),
                        'link': sticker.get('url', ''),
                        'summary': f"Trending sticker by @{sticker.get('username', 'giphy')}",
                        'description': sticker.get('title', ''),
                        'gif_id': sticker.get('id', ''),
                        'embed_url': sticker.get('embed_url', ''),
                        'preview_url': sticker.get('images', {}).get('preview_gif', {}).get('url', ''),
                        'username': sticker.get('username', ''),
                        'rating': sticker.get('rating', 'pg'),
                        'category': 'stickers',
                        'content_type': 'sticker',
                        'source': 'Giphy',
                        'data_type': 'sticker',
                        'platform': 'giphy',
                        'tags': ['sticker', 'trending', 'animated'],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error with Giphy API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch meme content from RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:300]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': 'memes',
                    'content_type': 'meme',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'meme_content',
                    'platform': 'giphy',
                    'tags': ['meme', 'culture', 'viral'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Giphy category links."""
        return [
            {
                'title': f"Giphy: {name}",
                'url': f'https://giphy.com/explore/{slug}',
                'link': f'https://giphy.com/explore/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Giphy',
                'data_type': 'gif_category',
                'platform': 'giphy',
                'tags': ['gif', 'giphy', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Trending GIFs', 'trending', 'Most popular GIFs now.'),
            ('Reaction GIFs', 'reactions', 'Express yourself with reactions.'),
            ('Meme GIFs', 'memes', 'Popular meme content.'),
            ('Stickers', 'stickers', 'Animated stickers.'),
            ('Entertainment', 'entertainment', 'Pop culture GIFs.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://giphy.com/explore/{category}',
                'link': f'https://giphy.com/explore/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Giphy',
                'data_type': 'gif_topic',
                'platform': 'giphy',
                'tags': ['gif', 'giphy', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
