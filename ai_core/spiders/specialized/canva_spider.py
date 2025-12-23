"""
Canva Spider - Design Platform & Templates Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Uses design RSS feeds for templates, tutorials, and design education.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CanvaSpider:
    """Canva spider - design platform and templates intelligence"""

    name = "canva"

    # Design education RSS feeds
    RSS_FEEDS = {
        'canva_design_school': 'https://www.canva.com/designschool/feed/',
        'design_shack': 'https://designshack.net/feed/',
        'speckyboy': 'https://speckyboy.com/feed/',
    }

    # Template type categories
    CATEGORIES = [
        ('Social Media', 'social-media', 'Social media templates and tips.'),
        ('Presentations', 'presentations', 'Slide deck and presentation design.'),
        ('Marketing', 'marketing', 'Marketing materials and graphics.'),
        ('Documents', 'documents', 'Business document templates.'),
        ('Videos', 'videos', 'Video and animation templates.'),
        ('Branding', 'branding', 'Brand kit and identity design.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.template_types = {
            'social_media': ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'social'],
            'presentations': ['presentation', 'slides', 'pitch deck', 'keynote', 'powerpoint'],
            'marketing': ['flyer', 'poster', 'brochure', 'banner', 'ad', 'marketing'],
            'documents': ['resume', 'letterhead', 'invoice', 'proposal', 'report'],
            'videos': ['video', 'animation', 'intro', 'outro', 'reel'],
            'branding': ['logo', 'brand kit', 'brand guide', 'identity', 'branding'],
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
            logger.warning(f"Error getting Canva categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Canva spider collected {len(all_items)} items")
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

                # Detect template type and if it's a tutorial
                text = f"{title} {summary}".lower()
                template_type = self._detect_template_type(text)
                is_tutorial = self._is_tutorial(text)
                skill_level = self._detect_skill_level(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': template_type,
                    'template_type': template_type,
                    'skill_level': skill_level,
                    'is_tutorial': is_tutorial,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'design_content',
                    'platform': 'canva',
                    'tags': ['design', 'canva', 'templates', template_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_template_type(self, text: str) -> str:
        """Detect template type from text."""
        for ttype, keywords in self.template_types.items():
            if any(kw in text for kw in keywords):
                return ttype
        return 'general'

    def _is_tutorial(self, text: str) -> bool:
        """Check if content is a tutorial."""
        tutorial_words = ['how to', 'tutorial', 'guide', 'step', 'learn', 'tips']
        return any(word in text for word in tutorial_words)

    def _detect_skill_level(self, text: str) -> str:
        """Detect skill level from text."""
        if any(w in text for w in ['beginner', 'basic', 'simple', 'easy', 'start']):
            return 'beginner'
        if any(w in text for w in ['advanced', 'pro', 'professional', 'expert']):
            return 'advanced'
        return 'intermediate'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Canva category links."""
        return [
            {
                'title': f"Canva: {name}",
                'url': f'https://www.canva.com/templates/?query={slug}',
                'link': f'https://www.canva.com/templates/?query={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Canva',
                'data_type': 'design_category',
                'platform': 'canva',
                'tags': ['design', 'canva', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Social Media Templates', 'social-media', 'Instagram, Facebook, TikTok templates.'),
            ('Presentation Design', 'presentations', 'Pitch decks and slides.'),
            ('Marketing Materials', 'marketing', 'Flyers, posters, and ads.'),
            ('Brand Identity', 'branding', 'Logo and brand kit design.'),
            ('Design Tutorials', 'tutorials', 'Learn design skills.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.canva.com/designschool/{category}/',
                'link': f'https://www.canva.com/designschool/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Canva',
                'data_type': 'design_topic',
                'platform': 'canva',
                'tags': ['design', 'canva', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
