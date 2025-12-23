"""
Ars Technica Spider - In-depth Technology News
==============================================

Session 534: Simplified to work with spider network interface.
Uses Ars Technica RSS feeds for detailed tech analysis and news.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ArsTechnicaSpider:
    """Ars Technica spider - in-depth technology news and analysis"""

    name = "arstechnica"

    # Ars Technica RSS feeds by section
    RSS_FEEDS = {
        'main': 'https://feeds.arstechnica.com/arstechnica/index',
        'tech_policy': 'https://feeds.arstechnica.com/arstechnica/tech-policy',
        'gadgets': 'https://feeds.arstechnica.com/arstechnica/gadgets',
        'science': 'https://feeds.arstechnica.com/arstechnica/science',
        'gaming': 'https://feeds.arstechnica.com/arstechnica/gaming',
        'cars': 'https://feeds.arstechnica.com/arstechnica/cars',
    }

    # Section categories
    SECTIONS = [
        ('Technology', 'technology', 'Latest tech news and analysis.'),
        ('Science', 'science', 'Scientific discoveries and research.'),
        ('Gaming', 'gaming', 'Video games and gaming culture.'),
        ('Tech Policy', 'tech-policy', 'Law, policy, and digital rights.'),
        ('Gadgets', 'gadgets', 'Hardware reviews and news.'),
        ('Cars', 'cars', 'Automotive and EV coverage.'),
        ('AI', 'ai', 'Artificial intelligence coverage.'),
        ('Security', 'security', 'Cybersecurity news and analysis.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch tech news from Ars Technica RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of article dictionaries
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

        # Add section links
        try:
            sections = self._get_section_links()
            all_items.extend(sections)
        except Exception as e:
            logger.warning(f"Error getting Ars Technica sections: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Ars Technica spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from Ars Technica RSS feed."""
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

                # Detect category from content
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                # Get article tags
                tags = [tag.term for tag in entry.get('tags', [])] if entry.get('tags') else []

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Ars Technica'),
                    'category': category,
                    'section': feed_name,
                    'article_tags': tags[:5],
                    'source': 'Ars Technica',
                    'data_type': 'tech_article',
                    'platform': 'arstechnica',
                    'tags': ['tech', 'news', 'analysis', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect article category from text."""
        categories = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm', 'neural'],
            'security': ['security', 'hack', 'vulnerability', 'malware', 'breach', 'ransomware'],
            'hardware': ['cpu', 'gpu', 'chip', 'processor', 'nvidia', 'amd', 'intel', 'apple silicon'],
            'software': ['software', 'app', 'update', 'release', 'windows', 'macos', 'linux'],
            'gaming': ['game', 'gaming', 'playstation', 'xbox', 'nintendo', 'steam'],
            'space': ['nasa', 'spacex', 'rocket', 'satellite', 'mars', 'moon', 'orbit'],
            'ev': ['ev', 'electric vehicle', 'tesla', 'battery', 'charging'],
            'policy': ['policy', 'regulation', 'law', 'congress', 'eu', 'privacy'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'general'

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return Ars Technica section links."""
        return [
            {
                'title': f"Ars Technica: {name}",
                'url': f'https://arstechnica.com/{slug}/',
                'link': f'https://arstechnica.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Ars Technica',
                'data_type': 'tech_section',
                'platform': 'arstechnica',
                'tags': ['tech', 'news', 'arstechnica', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('AI & Machine Learning', 'ai', 'Artificial intelligence news.'),
            ('Cybersecurity', 'security', 'Security threats and analysis.'),
            ('Hardware', 'gadgets', 'Tech hardware and reviews.'),
            ('Science', 'science', 'Scientific discoveries.'),
            ('Gaming', 'gaming', 'Video game news and reviews.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://arstechnica.com/{category}/',
                'link': f'https://arstechnica.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Ars Technica',
                'data_type': 'tech_topic',
                'platform': 'arstechnica',
                'tags': ['tech', 'arstechnica', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
