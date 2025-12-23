"""
Medium Intelligence Spider - Content Monetization Platform
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates content creation and writing platform news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MediumIntelligenceSpider:
    """Medium content monetization intelligence spider."""

    name = "medium"

    # Medium and writing platform RSS feeds
    RSS_FEEDS = {
        'medium_top': 'https://medium.com/feed/topic/technology',
        'medium_startup': 'https://medium.com/feed/topic/startup',
        'medium_programming': 'https://medium.com/feed/topic/programming',
        'better_programming': 'https://medium.com/feed/better-programming',
        'towards_data_science': 'https://towardsdatascience.com/feed',
        'the_writing_cooperative': 'https://writingcooperative.com/feed',
    }

    # Content categories
    CATEGORIES = [
        ('Technology', 'technology', 'Tech and programming content.'),
        ('Business', 'business', 'Business and startup content.'),
        ('Writing', 'writing', 'Writing tips and advice.'),
        ('Monetization', 'monetization', 'Content monetization strategies.'),
        ('Self Improvement', 'self', 'Personal development content.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.content_categories = {
            'technology': ['tech', 'software', 'programming', 'code', 'developer', 'ai'],
            'business': ['business', 'startup', 'entrepreneur', 'marketing', 'growth'],
            'writing': ['writing', 'content', 'blogging', 'storytelling', 'author'],
            'monetization': ['monetization', 'income', 'earnings', 'revenue', 'partner program'],
            'self_improvement': ['productivity', 'habits', 'mindset', 'success', 'motivation'],
            'design': ['design', 'ux', 'ui', 'product', 'creativity'],
        }
        self.monetization_signals = {
            'partner_program': ['member-only', 'partner program', 'earnings', 'paywall'],
            'high_engagement': ['viral', 'trending', 'popular', 'curated', 'featured'],
            'publication': ['publication', 'editor', 'submit', 'contribute'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch content creation and writing platform content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of content creation dictionaries
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
            logger.warning(f"Error getting content categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Medium spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from content platform RSS feed."""
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

                # Detect content category and monetization signals
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_monetizable = self._is_monetizable(text)
                has_high_engagement = self._has_high_engagement(text)

                # Extract author
                author = entry.get('author', 'Medium Writer')

                # Extract tags from feed entry
                entry_tags = []
                if hasattr(entry, 'tags'):
                    entry_tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')][:5]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': author,
                    'category': category,
                    'content_category': category,
                    'is_monetizable': is_monetizable,
                    'has_high_engagement': has_high_engagement,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'content_monetization',
                    'platform': 'medium',
                    'tags': ['medium', 'content', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect content category from text."""
        for category, keywords in self.content_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_monetizable(self, text: str) -> bool:
        """Check if content has monetization signals."""
        return any(kw in text for kw in self.monetization_signals['partner_program'])

    def _has_high_engagement(self, text: str) -> bool:
        """Check if content shows high engagement signals."""
        return any(kw in text for kw in self.monetization_signals['high_engagement'])

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return content category links."""
        return [
            {
                'title': f"Medium: {name}",
                'url': f'https://medium.com/topic/{slug}',
                'link': f'https://medium.com/topic/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Medium',
                'data_type': 'content_category',
                'platform': 'medium',
                'tags': ['medium', 'content', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Tech Writing', 'technology', 'Technology and programming content.'),
            ('Startup Stories', 'business', 'Business and entrepreneurship.'),
            ('Writing Tips', 'writing', 'Writing and content creation advice.'),
            ('Monetization', 'monetization', 'Content monetization strategies.'),
            ('Personal Development', 'self', 'Self-improvement content.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://medium.com/topic/{category}',
                'link': f'https://medium.com/topic/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Medium',
                'data_type': 'content_topic',
                'platform': 'medium',
                'tags': ['medium', 'content', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
