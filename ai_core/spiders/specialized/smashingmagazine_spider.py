"""
Smashing Magazine Spider - Web Design & Development
===================================================

Session 534: Simplified to work with spider network interface.
Smashing Magazine provides web design and development content via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SmashingMagazineSpider:
    """Smashing Magazine spider - web design and front-end development"""

    name = "smashingmagazine"

    # Web development RSS feeds
    RSS_FEEDS = {
        'smashing': 'https://www.smashingmagazine.com/feed/',
        'css_tricks': 'https://css-tricks.com/feed/',
        'a_list_apart': 'https://alistapart.com/main/feed/',
        'codrops': 'https://tympanus.net/codrops/feed/',
        'webdesigner_depot': 'https://www.webdesignerdepot.com/feed/',
    }

    # Web development categories
    CATEGORIES = [
        ('CSS', 'css', 'CSS techniques and styling.'),
        ('JavaScript', 'javascript', 'JavaScript frameworks and coding.'),
        ('UX', 'ux', 'User experience and accessibility.'),
        ('Design', 'design', 'UI design and visual layout.'),
        ('Performance', 'performance', 'Web performance optimization.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.web_categories = {
            'css': ['css', 'flexbox', 'grid', 'animation', 'responsive', 'tailwind', 'sass'],
            'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'svelte', 'typescript', 'node'],
            'ux': ['ux', 'user experience', 'usability', 'accessibility', 'a11y', 'research'],
            'design': ['design', 'ui', 'interface', 'layout', 'typography', 'color', 'figma'],
            'performance': ['performance', 'speed', 'optimization', 'core web vitals', 'lazy load', 'lighthouse'],
            'tools': ['webpack', 'vite', 'npm', 'git', 'docker', 'ci/cd', 'testing'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch web development content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of web development content dictionaries
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
            logger.warning(f"Error getting web dev categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"SmashingMagazine spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch web development articles from RSS feed."""
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

                # Detect category and type
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                is_tutorial = self._is_tutorial(text)
                sentiment = self._analyze_sentiment(text)

                # Extract tags from entry if available
                tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    tags = [tag.term for tag in entry.tags[:5]]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Smashing Magazine'),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'is_tutorial': is_tutorial,
                    'sentiment': sentiment,
                    'entry_tags': tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'web_development',
                    'platform': 'smashingmagazine',
                    'tags': ['web development', 'frontend'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect web development categories from text."""
        categories = []
        for category, keywords in self.web_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories or ['general']

    def _is_tutorial(self, text: str) -> bool:
        """Check if article is a tutorial."""
        tutorial_keywords = ['tutorial', 'how to', 'guide', 'step by step', 'complete guide', 'introduction to']
        return any(kw in text for kw in tutorial_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze article sentiment."""
        positive = ['best', 'modern', 'powerful', 'complete', 'essential', 'ultimate', 'amazing']
        negative = ['avoid', 'mistake', 'problem', 'issue', 'deprecated', 'bad']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return web development category links."""
        return [
            {
                'title': f"Smashing: {name}",
                'url': f'https://www.smashingmagazine.com/category/{slug}/',
                'link': f'https://www.smashingmagazine.com/category/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Smashing Magazine',
                'data_type': 'webdev_category',
                'platform': 'smashingmagazine',
                'tags': ['web development', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('CSS Techniques', 'css', 'Modern CSS layouts and styling.'),
            ('JavaScript Frameworks', 'javascript', 'React, Vue, and JS development.'),
            ('UX Design Patterns', 'ux', 'User experience best practices.'),
            ('Web Performance', 'performance', 'Site speed optimization.'),
            ('Design Systems', 'design', 'UI components and design tokens.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.smashingmagazine.com/category/{category}/',
                'link': f'https://www.smashingmagazine.com/category/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Smashing Magazine',
                'data_type': 'webdev_topic',
                'platform': 'smashingmagazine',
                'tags': ['web development', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
