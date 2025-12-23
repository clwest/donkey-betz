"""
Etsy Spider - Digital Products & Printables Intelligence
=========================================================

Session 534: Simplified to work with spider network interface.
Uses Etsy blog RSS and curated digital product categories.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class EtsySpider:
    """Etsy spider - digital downloads and printables trends"""

    name = "etsy"

    # Related RSS feeds
    RSS_FEEDS = {
        'etsy_blog': 'https://blog.etsy.com/en/feed/',
        'creative_market': 'https://creativemarket.com/blog/feed',
    }

    # Digital product categories
    CATEGORIES = [
        # Printables
        ('Wall Art Printables', 'printable-wall-art', 'Digital art prints for home decor.'),
        ('Planner Printables', 'planner-printable', 'Digital planners and organizers.'),
        ('Party Invitations', 'digital-invitation', 'Printable party and wedding invites.'),
        ('Stickers & Labels', 'printable-stickers', 'Digital stickers for planners.'),

        # Templates
        ('Resume Templates', 'resume-template', 'Professional resume designs.'),
        ('Social Media Templates', 'social-media-template', 'Instagram and Pinterest templates.'),
        ('Canva Templates', 'canva-template', 'Editable Canva designs.'),
        ('Business Card Templates', 'business-card-template', 'Printable business cards.'),

        # Graphics
        ('SVG Cut Files', 'svg-files', 'SVG files for Cricut and crafting.'),
        ('Clipart', 'clipart-digital', 'Digital illustrations and clipart.'),
        ('Fonts', 'digital-fonts', 'Commercial use fonts.'),
        ('Patterns', 'digital-pattern', 'Sewing and craft patterns.'),

        # Educational
        ('Worksheets', 'printable-worksheet', 'Educational worksheets for kids.'),
        ('Coloring Pages', 'coloring-pages-digital', 'Printable coloring pages.'),
        ('Flashcards', 'flashcards-printable', 'Educational flashcards.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch digital product trends from Etsy ecosystem.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of product/category dictionaries
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
            logger.warning(f"Error getting Etsy categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Etsy spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feed."""
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

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': 'blog',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creative_article',
                    'platform': 'etsy',
                    'tags': ['digital-products', 'etsy', 'creative', 'passive-income'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Etsy category exploration links."""
        return [
            {
                'title': f"Etsy: {name}",
                'url': f'https://www.etsy.com/search?q={slug}',
                'link': f'https://www.etsy.com/search?q={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Etsy',
                'data_type': 'product_category',
                'platform': 'etsy',
                'tags': ['digital-products', 'etsy', 'printables', slug.split('-')[0]],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Digital Downloads', 'digital-download', 'Instant download products.'),
            ('Printable Art', 'printable-art', 'Wall art and home decor prints.'),
            ('Planners & Journals', 'digital-planner', 'Digital planning products.'),
            ('SVG Files', 'svg-files', 'Cut files for Cricut and crafting.'),
            ('Templates', 'digital-template', 'Editable templates for business.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.etsy.com/search?q={category}',
                'link': f'https://www.etsy.com/search?q={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Etsy',
                'data_type': 'product_topic',
                'platform': 'etsy',
                'tags': ['digital-products', 'etsy', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
