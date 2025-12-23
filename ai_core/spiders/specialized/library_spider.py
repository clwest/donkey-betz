"""
Library Spider - Library & Archive Resources
=============================================

Session 534: Simplified to work with spider network interface.
Aggregates library news, digital archives, and research resources.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class LibrarySpider:
    """Library spider - library news, digital archives, and open access resources"""

    name = "library"

    # Library and archive RSS feeds
    RSS_FEEDS = {
        'ala_news': 'https://www.ala.org/news/rss',
        'library_journal': 'https://www.libraryjournal.com/feed',
        'american_libraries': 'https://americanlibrariesmagazine.org/feed/',
        'internet_archive': 'https://blog.archive.org/feed/',
        'open_culture': 'https://www.openculture.com/feed',
        'project_gutenberg': 'https://www.gutenberg.org/cache/epub/feeds/today.rss',
        'arxiv_cs': 'https://rss.arxiv.org/rss/cs',
    }

    # Library categories
    CATEGORIES = [
        ('Digital Archives', 'archives', 'Digital preservation and collections.'),
        ('Open Access', 'open_access', 'Free and public domain resources.'),
        ('Research', 'research', 'Academic research and publications.'),
        ('Technology', 'technology', 'Library technology and systems.'),
        ('Community', 'community', 'Library programs and outreach.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.library_categories = {
            'digital_archives': ['archive', 'digitization', 'digital collection', 'preservation'],
            'open_access': ['open access', 'free', 'public domain', 'creative commons'],
            'research': ['research', 'study', 'paper', 'journal', 'publication'],
            'technology': ['technology', 'software', 'digital', 'database', 'catalog'],
            'community': ['community', 'program', 'event', 'outreach', 'literacy'],
            'policy': ['policy', 'funding', 'legislation', 'copyright', 'intellectual property'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch library and archive content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of library content dictionaries
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
            logger.warning(f"Error getting library categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Library spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from library RSS feed."""
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

                # Detect library category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_research = self._is_research_paper(text)
                is_open_access = self._is_open_access(text)

                # Determine source type
                source_type = 'library_news'
                if feed_name in ['internet_archive', 'open_culture', 'project_gutenberg']:
                    source_type = 'digital_archive'
                elif feed_name in ['arxiv_cs']:
                    source_type = 'research'

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'source_type': source_type,
                    'is_research': is_research,
                    'is_open_access': is_open_access,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'library_resources',
                    'platform': 'library',
                    'tags': ['library', 'archives', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect library category from text."""
        for category, keywords in self.library_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_research_paper(self, text: str) -> bool:
        """Check if content is a research paper."""
        research_keywords = ['research', 'study', 'paper', 'arxiv', 'journal', 'findings']
        return any(kw in text for kw in research_keywords)

    def _is_open_access(self, text: str) -> bool:
        """Check if content is open access."""
        open_keywords = ['open access', 'free', 'public domain', 'creative commons', 'open source']
        return any(kw in text for kw in open_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return library category links."""
        return [
            {
                'title': f"Library: {name}",
                'url': f'https://blog.archive.org/category/{slug}/',
                'link': f'https://blog.archive.org/category/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Library',
                'data_type': 'library_category',
                'platform': 'library',
                'tags': ['library', 'archives', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Digital Archives', 'archives', 'Digital preservation projects.'),
            ('Open Access', 'open_access', 'Free and open resources.'),
            ('Research Papers', 'research', 'Academic publications.'),
            ('Library Tech', 'technology', 'Library technology news.'),
            ('Community Programs', 'community', 'Library outreach and events.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://blog.archive.org/category/{category}/',
                'link': f'https://blog.archive.org/category/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Library',
                'data_type': 'library_topic',
                'platform': 'library',
                'tags': ['library', 'archives', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
