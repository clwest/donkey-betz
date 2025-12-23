"""
Indie Hackers Spider - Maker & Founder Community Intelligence
==============================================================

Session 534: Simplified to work with spider network interface.
Aggregates maker/founder discussions via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class IndieHackersSpider:
    """Indie Hackers spider - maker/founder discussions and pain points"""

    name = "indiehackers"

    # Indie Hackers and maker RSS feeds
    RSS_FEEDS = {
        'indiehackers': 'https://www.indiehackers.com/feed.xml',
        'product_hunt': 'https://www.producthunt.com/feed',
        'bootstrapped_fm': 'https://bootstrapped.fm/feed/',
        'microconf': 'https://www.microconf.com/feed/',
    }

    # Community categories
    CATEGORIES = [
        ('SaaS', 'saas', 'SaaS products and tools.'),
        ('Marketing', 'marketing', 'Marketing and growth tactics.'),
        ('Revenue', 'revenue', 'Revenue milestones and strategies.'),
        ('Launch', 'launch', 'Product launches and validation.'),
        ('Growth', 'growth', 'Growth hacking and scaling.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.maker_topics = {
            'saas': ['saas', 'subscription', 'mrr', 'arr', 'recurring', 'churn'],
            'marketing': ['marketing', 'seo', 'content', 'social', 'ads', 'growth'],
            'revenue': ['revenue', 'profit', 'income', 'monetize', 'pricing', 'sales'],
            'launch': ['launch', 'product hunt', 'mvp', 'beta', 'validate', 'ship'],
            'growth': ['growth', 'scale', 'users', 'customers', 'traction', 'viral'],
            'pain_point': ['struggle', 'problem', 'issue', 'frustrat', 'difficult', 'challenge'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch maker/founder content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of maker content dictionaries
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
            logger.warning(f"Error getting maker categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Indie Hackers spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from maker RSS feed."""
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

                # Detect maker topic
                text = f"{title} {summary}".lower()
                topic = self._detect_topic(text)
                is_pain_point = self._is_pain_point(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Indie Hacker'),
                    'topic': topic,
                    'category': topic,
                    'is_pain_point': is_pain_point,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'maker_content',
                    'platform': 'indiehackers',
                    'tags': ['indiehackers', 'makers', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect maker topic from text."""
        for topic, keywords in self.maker_topics.items():
            if topic != 'pain_point' and any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _is_pain_point(self, text: str) -> bool:
        """Check if content discusses a pain point."""
        return any(kw in text for kw in self.maker_topics['pain_point'])

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return maker category links."""
        return [
            {
                'title': f"Makers: {name}",
                'url': f'https://www.indiehackers.com/groups/{slug}',
                'link': f'https://www.indiehackers.com/groups/{slug}',
                'summary': desc,
                'description': desc,
                'topic': slug,
                'category': slug,
                'source': 'Indie Hackers',
                'data_type': 'maker_category',
                'platform': 'indiehackers',
                'tags': ['indiehackers', 'makers', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('SaaS Discussions', 'saas', 'Building and growing SaaS.'),
            ('Marketing Tips', 'marketing', 'Growth and marketing strategies.'),
            ('Revenue Milestones', 'revenue', 'Revenue stories and advice.'),
            ('Product Launches', 'launch', 'Launch strategies and validation.'),
            ('Growth Tactics', 'growth', 'Scaling and user acquisition.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.indiehackers.com/groups/{category}',
                'link': f'https://www.indiehackers.com/groups/{category}',
                'summary': desc,
                'description': desc,
                'topic': category,
                'category': category,
                'source': 'Indie Hackers',
                'data_type': 'maker_topic',
                'platform': 'indiehackers',
                'tags': ['indiehackers', 'makers', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
