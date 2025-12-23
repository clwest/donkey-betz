"""
Science Spider - Scientific Research & Discovery
=================================================

Session 534: Simplified to work with spider network interface.
Aggregates scientific news from multiple research sources via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ScienceSpider:
    """Science spider - research papers, discoveries, and science news"""

    name = "science"

    # Science news RSS feeds
    RSS_FEEDS = {
        'science_daily': 'https://www.sciencedaily.com/rss/all.xml',
        'science_mag': 'https://www.science.org/rss/news_current.xml',
        'nature': 'https://www.nature.com/nature.rss',
        'new_scientist': 'https://www.newscientist.com/feed/home/',
        'phys_org': 'https://phys.org/rss-feed/',
        'scientific_american': 'https://www.scientificamerican.com/feed/',
    }

    # Science categories
    CATEGORIES = [
        ('Physics', 'physics', 'Quantum, particle physics, and cosmology.'),
        ('Biology', 'biology', 'Life sciences, genetics, and evolution.'),
        ('Chemistry', 'chemistry', 'Molecular science and chemical research.'),
        ('Astronomy', 'astronomy', 'Space exploration and astrophysics.'),
        ('Climate', 'climate', 'Climate science and environmental research.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.science_categories = {
            'physics': ['physics', 'quantum', 'particle', 'gravity', 'relativity', 'atom'],
            'biology': ['biology', 'cell', 'gene', 'dna', 'evolution', 'species', 'organism'],
            'chemistry': ['chemistry', 'molecule', 'compound', 'reaction', 'element', 'bond'],
            'astronomy': ['space', 'nasa', 'planet', 'star', 'galaxy', 'black hole', 'mars', 'moon'],
            'climate': ['climate', 'warming', 'carbon', 'ocean', 'temperature', 'weather', 'ice'],
            'medicine': ['medicine', 'disease', 'treatment', 'drug', 'cancer', 'virus', 'vaccine'],
            'ai_computing': ['ai', 'artificial intelligence', 'robot', 'algorithm', 'computer', 'neural'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch science news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of science article dictionaries
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
            logger.warning(f"Error getting science categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Science spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch science articles from RSS feed."""
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

                # Detect science category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_breakthrough = self._is_breakthrough(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'category': category,
                    'is_breakthrough': is_breakthrough,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'science_news',
                    'platform': 'science',
                    'tags': ['science', 'research', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect science category from text."""
        for category, keywords in self.science_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_breakthrough(self, text: str) -> bool:
        """Check if article describes a breakthrough."""
        breakthrough_keywords = [
            'breakthrough', 'discovery', 'first time', 'revolutionary', 'groundbreaking',
            'new study', 'researchers find', 'scientists discover', 'unprecedented'
        ]
        return any(kw in text for kw in breakthrough_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze article sentiment."""
        positive = ['breakthrough', 'success', 'discovery', 'cure', 'hope', 'advance', 'progress']
        negative = ['threat', 'danger', 'warning', 'concern', 'crisis', 'extinction', 'risk']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return science category links."""
        return [
            {
                'title': f"Science: {name}",
                'url': f'https://www.sciencedaily.com/{slug}/',
                'link': f'https://www.sciencedaily.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'ScienceDaily',
                'data_type': 'science_category',
                'platform': 'science',
                'tags': ['science', 'research', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Physics Research', 'physics', 'Quantum mechanics and particle physics.'),
            ('Life Sciences', 'biology', 'Biology, genetics, and evolution.'),
            ('Space & Astronomy', 'astronomy', 'Space exploration and cosmology.'),
            ('Climate Science', 'climate', 'Climate research and environmental studies.'),
            ('Medical Research', 'medicine', 'Drug discovery and disease research.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.sciencedaily.com/{category}/',
                'link': f'https://www.sciencedaily.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'ScienceDaily',
                'data_type': 'science_topic',
                'platform': 'science',
                'tags': ['science', 'research', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
