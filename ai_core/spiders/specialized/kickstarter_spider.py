"""
Kickstarter Spider - Creative Crowdfunding Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Aggregates crowdfunding content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class KickstarterSpider:
    """Kickstarter spider - creative crowdfunding and project intelligence"""

    name = "kickstarter"

    # Kickstarter and crowdfunding RSS feeds
    RSS_FEEDS = {
        'kickstarter_blog': 'https://www.kickstarter.com/blog.atom',
        'product_hunt': 'https://www.producthunt.com/feed',
        'indiegogo_blog': 'https://entrepreneur.indiegogo.com/feed/',
    }

    # Project categories
    CATEGORIES = [
        ('Games', 'games', 'Board games and video games.'),
        ('Technology', 'technology', 'Tech gadgets and devices.'),
        ('Design', 'design', 'Product design and fashion.'),
        ('Film', 'film', 'Movies and documentaries.'),
        ('Music', 'music', 'Albums and music projects.'),
        ('Publishing', 'publishing', 'Books and comics.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.project_categories = {
            'games': ['game', 'board game', 'video game', 'tabletop', 'rpg', 'card game'],
            'technology': ['tech', 'gadget', 'device', 'app', 'software', 'hardware'],
            'design': ['design', 'product', 'furniture', 'fashion', 'accessory'],
            'film': ['film', 'movie', 'documentary', 'animation', 'short film'],
            'music': ['music', 'album', 'vinyl', 'instrument', 'concert'],
            'publishing': ['book', 'comic', 'magazine', 'zine', 'publishing'],
            'art': ['art', 'illustration', 'painting', 'sculpture', 'photography'],
            'food': ['food', 'drink', 'restaurant', 'cookbook', 'beverage'],
        }
        self.campaign_signals = {
            'launching': ['launching', 'live now', 'just launched', 'new campaign'],
            'funded': ['funded', 'reached goal', 'successful', 'backed'],
            'ending_soon': ['ending soon', 'final hours', 'last chance', 'ends'],
            'staff_pick': ['staff pick', 'featured', 'project we love'],
            'trending': ['popular', 'trending', 'viral', 'hot', 'top'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch crowdfunding content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of crowdfunding content dictionaries
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
            logger.warning(f"Error getting crowdfunding categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Kickstarter spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from crowdfunding RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect category and signals
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                signals = self._detect_signals(text)
                is_staff_pick = 'staff_pick' in signals
                is_funded = 'funded' in signals
                is_trending = 'trending' in signals

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'project_category': category,
                    'signals': signals,
                    'is_staff_pick': is_staff_pick,
                    'is_funded': is_funded,
                    'is_trending': is_trending,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'crowdfunding',
                    'platform': 'kickstarter',
                    'tags': ['kickstarter', 'crowdfunding', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect project category from text."""
        for category, keywords in self.project_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_signals(self, text: str) -> List[str]:
        """Detect campaign signals from text."""
        signals = []
        for signal, keywords in self.campaign_signals.items():
            if any(kw in text for kw in keywords):
                signals.append(signal)
        return signals

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return crowdfunding category links."""
        return [
            {
                'title': f"Kickstarter: {name}",
                'url': f'https://www.kickstarter.com/discover/categories/{slug}',
                'link': f'https://www.kickstarter.com/discover/categories/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Kickstarter',
                'data_type': 'crowdfunding_category',
                'platform': 'kickstarter',
                'tags': ['kickstarter', 'crowdfunding', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Trending Projects', 'trending', 'Most popular campaigns.'),
            ('Staff Picks', 'staff_picks', 'Kickstarter staff picks.'),
            ('New & Noteworthy', 'new', 'Recently launched projects.'),
            ('Most Funded', 'most_funded', 'Successfully funded projects.'),
            ('Ending Soon', 'ending_soon', 'Campaigns ending soon.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.kickstarter.com/discover/{category}',
                'link': f'https://www.kickstarter.com/discover/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Kickstarter',
                'data_type': 'crowdfunding_topic',
                'platform': 'kickstarter',
                'tags': ['kickstarter', 'crowdfunding', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
