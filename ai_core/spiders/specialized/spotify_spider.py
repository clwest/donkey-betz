"""
Spotify Spider - Music & Podcast Trends Intelligence
=====================================================

Session 534: Simplified to work with spider network interface.
Aggregates music industry and podcast news via RSS feeds.
Uses Spotify API when credentials available, RSS fallback otherwise.
"""

import os
import requests
from ai_core.spiders.web_request_layer import cached_get
import base64
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SpotifySpider:
    """Spotify spider - music trends, new releases, and podcast charts"""

    name = "spotify"

    AUTH_URL = "https://accounts.spotify.com/api/token"
    BASE_URL = "https://api.spotify.com/v1"

    # Music and podcast RSS feeds (fallback when API not available)
    RSS_FEEDS = {
        'billboard': 'https://www.billboard.com/feed/',
        'pitchfork': 'https://pitchfork.com/feed/feed-news/rss',
        'rolling_stone': 'https://www.rollingstone.com/music/music-news/feed/',
        'consequence': 'https://consequence.net/feed/',
        'stereogum': 'https://www.stereogum.com/feed/',
    }

    # Music categories
    CATEGORIES = [
        ('New Releases', 'new_releases', 'Latest album and single releases.'),
        ('Charts', 'charts', 'Billboard and streaming charts.'),
        ('Podcasts', 'podcasts', 'Podcast trends and charts.'),
        ('Artists', 'artists', 'Artist news and interviews.'),
        ('Industry', 'industry', 'Music industry news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        self.access_token = None
        self.music_categories = {
            'releases': ['album', 'single', 'release', 'drop', 'new music', 'debut'],
            'charts': ['chart', 'billboard', 'top', 'streaming', 'spotify charts'],
            'podcasts': ['podcast', 'episode', 'show', 'audio', 'interview'],
            'tours': ['tour', 'concert', 'live', 'festival', 'performance'],
            'awards': ['grammy', 'award', 'nomination', 'winner', 'ceremony'],
            'industry': ['label', 'deal', 'contract', 'streaming', 'royalty'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch music and podcast data. Uses Spotify API if credentials available,
        otherwise falls back to RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of music/podcast content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Spotify API first if credentials available
        if self.client_id and self.client_secret:
            try:
                api_items = self._fetch_spotify_api()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Spotify API error: {e}")

        # Fetch from RSS feeds (always, as supplemental or fallback)
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
            logger.warning(f"Error getting music categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Spotify spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _get_access_token(self) -> Optional[str]:
        """Get Spotify access token using client credentials flow."""
        if not self.client_id or not self.client_secret:
            return None

        try:
            auth_str = f"{self.client_id}:{self.client_secret}"
            auth_bytes = base64.b64encode(auth_str.encode()).decode()

            headers = {
                'Authorization': f'Basic {auth_bytes}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}

            response = requests.post(self.AUTH_URL, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get('access_token')
            else:
                logger.warning(f"Spotify auth failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting Spotify token: {e}")
            return None

    def _fetch_spotify_api(self) -> List[Dict[str, Any]]:
        """Fetch new releases and playlists from Spotify API."""
        items = []

        self.access_token = self._get_access_token()
        if not self.access_token:
            return items

        headers = {'Authorization': f'Bearer {self.access_token}'}

        # Fetch new releases
        try:
            url = f"{self.BASE_URL}/browse/new-releases"
            params = {'limit': 20, 'country': 'US'}

            response = cached_get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                albums = data.get('albums', {}).get('items', [])

                for album in albums:
                    artists = ', '.join([a.get('name', '') for a in album.get('artists', [])])
                    items.append({
                        'title': f"{album.get('name', '')} by {artists}",
                        'url': album.get('external_urls', {}).get('spotify', ''),
                        'link': album.get('external_urls', {}).get('spotify', ''),
                        'summary': f"New {album.get('album_type', 'album')} with {album.get('total_tracks', 0)} tracks",
                        'description': f"Released: {album.get('release_date', '')}",
                        'artists': [a.get('name', '') for a in album.get('artists', [])],
                        'release_date': album.get('release_date', ''),
                        'album_type': album.get('album_type', ''),
                        'total_tracks': album.get('total_tracks', 0),
                        'image_url': album.get('images', [{}])[0].get('url', '') if album.get('images') else '',
                        'category': 'releases',
                        'source': 'Spotify API',
                        'data_type': 'music_release',
                        'platform': 'spotify',
                        'tags': ['spotify', 'music', 'new release', album.get('album_type', '')],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching Spotify new releases: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch music news from RSS feed."""
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
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'music_news',
                    'platform': 'spotify',
                    'tags': ['music', 'entertainment', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect music category from text."""
        for category, keywords in self.music_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze music news sentiment."""
        positive = ['hit', 'success', 'chart', 'platinum', 'award', 'celebrate', 'sold out']
        negative = ['cancel', 'delay', 'controversy', 'lawsuit', 'death', 'tragedy']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return music category links."""
        return [
            {
                'title': f"Music: {name}",
                'url': f'https://open.spotify.com/{slug}',
                'link': f'https://open.spotify.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Spotify',
                'data_type': 'music_category',
                'platform': 'spotify',
                'tags': ['spotify', 'music', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('New Album Releases', 'releases', 'Latest albums and EPs.'),
            ('Top Charts', 'charts', 'Billboard and streaming charts.'),
            ('Popular Podcasts', 'podcasts', 'Trending podcast shows.'),
            ('Artist News', 'artists', 'Music artist updates.'),
            ('Industry Updates', 'industry', 'Music business news.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.billboard.com/{category}/',
                'link': f'https://www.billboard.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Billboard',
                'data_type': 'music_topic',
                'platform': 'spotify',
                'tags': ['music', 'entertainment', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
