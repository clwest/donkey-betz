"""
99designs Intelligence Spider - Design Competition Platform
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates design contest and creative industry content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NinetyNineDesignsIntelligenceSpider:
    """99designs intelligence gathering spider - design contests and creative industry"""

    name = "ninetyninedesigns"

    # Design and creative industry RSS feeds
    RSS_FEEDS = {
        'creative_bloq': 'https://www.creativebloq.com/feed',
        'design_week': 'https://www.designweek.co.uk/feed/',
        'smashing_magazine': 'https://www.smashingmagazine.com/feed/',
        'dribbble_blog': 'https://dribbble.com/stories.rss',
        'behance_blog': 'https://www.behance.net/blog/feed',
    }

    # Design categories
    CATEGORIES = [
        ('Logo Design', 'logo', 'Logo and brand identity design.'),
        ('Web Design', 'web', 'Website and UI design.'),
        ('Packaging', 'packaging', 'Product packaging design.'),
        ('Print Design', 'print', 'Print and marketing materials.'),
        ('Illustration', 'illustration', 'Illustration and artwork.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.design_categories = {
            'logo': ['logo', 'brand', 'identity', 'wordmark', 'emblem'],
            'web': ['web', 'website', 'ui', 'ux', 'interface', 'app'],
            'packaging': ['packaging', 'package', 'box', 'label', 'container'],
            'print': ['print', 'brochure', 'flyer', 'poster', 'banner'],
            'illustration': ['illustration', 'drawing', 'artwork', 'character', 'icon'],
            'business_card': ['business card', 'card', 'stationery'],
        }
        self.style_keywords = [
            'modern', 'classic', 'minimalist', 'bold', 'elegant',
            'playful', 'professional', 'corporate', 'creative', 'vintage'
        ]

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch design industry content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of design content dictionaries
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
            logger.warning(f"Error getting design categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"99designs spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from design RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect design category and styles
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                styles = self._detect_styles(text)
                is_contest = self._is_contest_related(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'design_category': category,
                    'category': category,
                    'style_preferences': styles,
                    'is_contest_related': is_contest,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'design_content',
                    'platform': 'ninetyninedesigns',
                    'tags': ['99designs', 'design', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect design category from text."""
        for category, keywords in self.design_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_styles(self, text: str) -> List[str]:
        """Detect design styles from text."""
        styles = []
        for style in self.style_keywords:
            if style in text:
                styles.append(style)
        return styles

    def _is_contest_related(self, text: str) -> bool:
        """Check if content is contest-related."""
        contest_keywords = ['contest', 'competition', 'winner', 'prize', 'entries', 'submit']
        return any(kw in text for kw in contest_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return design category links."""
        return [
            {
                'title': f"99designs: {name}",
                'url': f'https://99designs.com/contests/{slug}',
                'link': f'https://99designs.com/contests/{slug}',
                'summary': desc,
                'description': desc,
                'design_category': slug,
                'category': slug,
                'source': '99designs',
                'data_type': 'design_category',
                'platform': 'ninetyninedesigns',
                'tags': ['99designs', 'design', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Logo Contests', 'logo', 'Logo and branding competitions.'),
            ('Web Design', 'web', 'Website and UI design contests.'),
            ('Packaging Design', 'packaging', 'Product packaging competitions.'),
            ('Print Design', 'print', 'Print material design contests.'),
            ('Illustration', 'illustration', 'Illustration competitions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://99designs.com/contests/{category}',
                'link': f'https://99designs.com/contests/{category}',
                'summary': desc,
                'description': desc,
                'design_category': category,
                'category': category,
                'source': '99designs',
                'data_type': 'design_topic',
                'platform': 'ninetyninedesigns',
                'tags': ['99designs', 'design', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
