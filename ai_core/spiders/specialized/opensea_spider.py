"""
OpenSea Spider - NFT Marketplace Intelligence
==============================================

Session 534: Simplified to work with spider network interface.
Uses NFT news RSS feeds and curated collection categories.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class OpenSeaSpider:
    """OpenSea spider - NFT marketplace and digital art trends"""

    name = "opensea"

    # NFT news RSS feeds
    RSS_FEEDS = {
        'nft_now': 'https://nftnow.com/feed/',
        'decrypt': 'https://decrypt.co/feed',
    }

    # NFT categories on OpenSea
    CATEGORIES = [
        # Art
        ('Digital Art', 'art', 'Digital artwork and generative art NFTs.'),
        ('Photography', 'photography', 'Photography NFT collections.'),
        ('AI Art', 'ai-art', 'AI-generated art and neural network creations.'),

        # Collectibles
        ('PFP Collections', 'pfps', 'Profile picture NFT collections.'),
        ('Gaming NFTs', 'gaming', 'In-game items and gaming collectibles.'),
        ('Music NFTs', 'music', 'Music and audio NFTs.'),

        # Virtual Worlds
        ('Virtual Worlds', 'virtual-worlds', 'Metaverse land and virtual real estate.'),
        ('Domain Names', 'domain-names', 'ENS and blockchain domain names.'),

        # Utility
        ('Memberships', 'memberships', 'Token-gated membership NFTs.'),
        ('Sports Collectibles', 'sports-collectibles', 'Sports memorabilia NFTs.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch NFT news and collection categories.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of NFT news and category dictionaries
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
            logger.warning(f"Error getting OpenSea categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"OpenSea spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch NFT news from RSS feed."""
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

                # Detect NFT category
                category = self._detect_category(f"{title} {description}".lower())

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'nft_news',
                    'platform': 'opensea',
                    'tags': ['nft', 'crypto', 'digital-art', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect NFT category from text."""
        categories = {
            'art': ['art', 'artwork', 'artist', 'generative'],
            'pfp': ['pfp', 'avatar', 'profile', 'collection'],
            'gaming': ['game', 'gaming', 'metaverse', 'play'],
            'music': ['music', 'audio', 'song', 'album'],
            'photography': ['photo', 'photography', 'photographer'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'collectibles'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return OpenSea category exploration links."""
        return [
            {
                'title': f"OpenSea: {name}",
                'url': f'https://opensea.io/category/{slug}',
                'link': f'https://opensea.io/category/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'OpenSea',
                'data_type': 'nft_category',
                'platform': 'opensea',
                'tags': ['nft', 'opensea', 'crypto', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Trending NFTs', 'trending', 'Hot and trending NFT collections.'),
            ('New Drops', 'new', 'Recently launched NFT collections.'),
            ('Top Collections', 'top', 'Highest volume NFT collections.'),
            ('Art NFTs', 'art', 'Digital art and generative art.'),
            ('Gaming NFTs', 'gaming', 'Gaming and metaverse NFTs.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://opensea.io/rankings?category={category}',
                'link': f'https://opensea.io/rankings?category={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'OpenSea',
                'data_type': 'nft_topic',
                'platform': 'opensea',
                'tags': ['nft', 'opensea', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
