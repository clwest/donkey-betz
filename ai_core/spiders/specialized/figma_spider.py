"""
Figma Spider - Design Community & UI/UX Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Uses Figma and UX design RSS feeds for design trends.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FigmaSpider:
    """Figma spider - design community and UI/UX intelligence"""

    name = "figma"

    # Figma and UX design RSS feeds
    RSS_FEEDS = {
        'figma_blog': 'https://www.figma.com/blog/feed/',
        'ux_collective': 'https://uxdesign.cc/feed',
        'ux_planet': 'https://uxplanet.org/feed',
    }

    # Design categories
    CATEGORIES = [
        ('UI Kits', 'ui-kits', 'Design systems and component libraries.'),
        ('Icons', 'icons', 'Icon sets and iconography.'),
        ('Wireframes', 'wireframes', 'Prototypes and mockups.'),
        ('Plugins', 'plugins', 'Figma plugins and tools.'),
        ('Templates', 'templates', 'Design templates and layouts.'),
        ('Tutorials', 'tutorials', 'Design tutorials and guides.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.design_categories = {
            'ui_kits': ['ui kit', 'design system', 'component', 'library', 'kit'],
            'icons': ['icon', 'iconography', 'icon set', 'icon pack'],
            'illustrations': ['illustration', 'vector', 'artwork', 'graphic'],
            'wireframes': ['wireframe', 'prototype', 'mockup', 'layout'],
            'plugins': ['plugin', 'extension', 'tool', 'automation'],
            'templates': ['template', 'landing page', 'dashboard', 'mobile'],
        }
        self.design_trends = {
            'minimalism': ['minimal', 'clean', 'simple', 'whitespace', 'modern'],
            'neumorphism': ['neumorphism', 'soft ui', '3d', 'shadow', 'depth'],
            'glassmorphism': ['glass', 'blur', 'transparent', 'frosted'],
            'dark_mode': ['dark mode', 'dark theme', 'dark ui', 'night mode'],
            'accessibility': ['accessibility', 'a11y', 'inclusive', 'wcag'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch design content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of content dictionaries
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
            logger.warning(f"Error getting Figma categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Figma spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from design RSS feed."""
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

                # Detect design category and trends
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                trends = self._detect_trends(text)
                is_figma = self._is_figma_specific(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': category,
                    'design_category': category,
                    'trends': trends,
                    'is_figma_specific': is_figma,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'design_content',
                    'platform': 'figma',
                    'tags': ['design', 'figma', 'ui', 'ux', category],
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

    def _detect_trends(self, text: str) -> List[str]:
        """Detect design trends from text."""
        trends = []
        for trend, keywords in self.design_trends.items():
            if any(kw in text for kw in keywords):
                trends.append(trend)
        return trends

    def _is_figma_specific(self, text: str) -> bool:
        """Check if content is Figma-specific."""
        figma_keywords = ['figma', 'figjam', 'auto layout', 'variant', 'dev mode']
        return any(kw in text for kw in figma_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Figma category links."""
        return [
            {
                'title': f"Figma: {name}",
                'url': f'https://www.figma.com/community/search?resource_type=mixed&sort_by=popular&query={slug}',
                'link': f'https://www.figma.com/community/search?query={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Figma',
                'data_type': 'design_category',
                'platform': 'figma',
                'tags': ['design', 'figma', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('UI Kits', 'ui-kits', 'Design systems and components.'),
            ('Figma Plugins', 'plugins', 'Productivity and design tools.'),
            ('Wireframes', 'wireframes', 'Prototypes and mockups.'),
            ('Icon Sets', 'icons', 'Icon libraries and packs.'),
            ('Design Templates', 'templates', 'Ready-to-use layouts.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.figma.com/community/{category}',
                'link': f'https://www.figma.com/community/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Figma',
                'data_type': 'design_topic',
                'platform': 'figma',
                'tags': ['design', 'figma', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
