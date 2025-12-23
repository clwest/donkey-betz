"""
Dribbble Spider - Design Portfolio & Trends Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Dribbble provides design inspiration via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class DribbbleSpider:
    """Dribbble spider - design portfolios and trends via RSS"""

    name = "dribbble"

    RSS_FEEDS = {
        'popular': 'https://dribbble.com/shots/popular.rss',
        'recent': 'https://dribbble.com/shots/recent.rss',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch design shots from Dribbble RSS feeds.

        Args:
            max_results: Maximum number of shots to fetch

        Returns:
            List of shot dictionaries
        """
        all_shots = []
        seen_urls = set()

        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:30]:
                    url = entry.get('link', '')

                    # Skip duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = entry.get('title', '')
                    if not title:
                        continue

                    # Get description and clean HTML
                    description = entry.get('summary', entry.get('description', ''))
                    if description:
                        description = re.sub(r'<[^>]+>', '', description)[:500]

                    # Extract image URL from content if available
                    image_url = ''
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].get('value', '')
                        if 'src="' in content:
                            start = content.find('src="') + 5
                            end = content.find('"', start)
                            if end > start:
                                image_url = content[start:end]

                    # Detect design category
                    category = self._detect_category(f"{title} {description}".lower())

                    shot = {
                        'title': title,
                        'url': url,
                        'link': url,
                        'summary': description,
                        'description': description,
                        'published': entry.get('published', ''),
                        'author': entry.get('author', 'Designer'),
                        'image_url': image_url,
                        'category': category,
                        'feed_source': feed_name,
                        'source': 'Dribbble',
                        'data_type': 'design_shot',
                        'is_popular': feed_name == 'popular',
                        'tags': ['design', 'creative', category, feed_name],
                        'timestamp': datetime.now().isoformat(),
                    }
                    all_shots.append(shot)

                    if len(all_shots) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Error fetching Dribbble {feed_name} feed: {e}")
                continue

            if len(all_shots) >= max_results:
                break

        # If RSS feeds fail, return curated design topics
        if len(all_shots) == 0:
            all_shots = self._get_curated_topics()

        logger.info(f"Dribbble spider collected {len(all_shots)} shots")
        return all_shots[:max_results]

    def _detect_category(self, text: str) -> str:
        """Detect design category from text."""
        categories = {
            'ui_ux': ['ui', 'ux', 'interface', 'dashboard', 'app design', 'mobile'],
            'branding': ['logo', 'brand', 'identity', 'logotype'],
            'illustration': ['illustration', 'character', 'drawing', 'artwork'],
            'web_design': ['website', 'landing page', 'homepage', 'web design'],
            'motion': ['animation', 'motion', 'animated', 'gif'],
            'typography': ['typography', 'type', 'font', 'lettering'],
            'icon': ['icon', 'iconography', 'icon set'],
            '3d': ['3d', 'render', 'blender', 'cinema4d'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'design'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated design topics when RSS fails."""
        topics = [
            ('UI/UX Design Trends', 'ui_ux', 'Latest user interface and experience design patterns.'),
            ('Logo & Branding', 'branding', 'Brand identity, logos, and visual branding work.'),
            ('Illustration Art', 'illustration', 'Digital illustrations, character design, and artwork.'),
            ('Web Design Inspiration', 'web_design', 'Website designs, landing pages, and web layouts.'),
            ('Motion Design', 'motion', 'Animations, motion graphics, and interactive designs.'),
            ('Typography Art', 'typography', 'Type design, lettering, and typographic compositions.'),
            ('Icon Design', 'icon', 'Icon sets, iconography, and symbol design.'),
            ('3D Design', '3d', '3D renders, modeling, and dimensional artwork.'),
            ('Mobile App Design', 'ui_ux', 'iOS and Android app interface designs.'),
            ('Dashboard Design', 'ui_ux', 'Admin panels, analytics dashboards, and data visualization.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://dribbble.com/tags/{category}',
                'link': f'https://dribbble.com/tags/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Dribbble',
                'data_type': 'design_topic',
                'tags': ['design', 'creative', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
