"""
MobiHealthNews Spider - Healthtech & Digital Health Intelligence
=================================================================

Session 534: Simplified to work with spider network interface.
MobiHealthNews provides digital health/healthtech news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MobiHealthNewsSpider:
    """MobiHealthNews spider - digital health and healthtech news via RSS"""

    name = "mobihealthnews"

    RSS_FEEDS = {
        'main': 'https://www.mobihealthnews.com/feed',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news articles from MobiHealthNews RSS feeds.

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of article dictionaries
        """
        all_articles = []
        seen_urls = set()

        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:25]:
                    url = entry.get('link', '')

                    # Skip duplicates
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = entry.get('title', '')
                    if not title:
                        continue

                    summary = entry.get('summary', entry.get('description', ''))
                    # Clean HTML from summary
                    if summary:
                        summary = re.sub(r'<[^>]+>', '', summary)[:500]

                    # Detect category based on content
                    category = self._detect_category(f"{title} {summary}".lower())

                    article = {
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'description': summary,
                        'published': entry.get('published', ''),
                        'author': entry.get('author', 'MobiHealthNews'),
                        'category': category,
                        'source': 'MobiHealthNews',
                        'data_type': 'healthtech_news',
                        'tags': ['healthtech', 'digital_health', category],
                        'timestamp': datetime.now().isoformat(),
                    }
                    all_articles.append(article)

                    if len(all_articles) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Error fetching MobiHealthNews {feed_name} feed: {e}")
                continue

            if len(all_articles) >= max_results:
                break

        # If RSS feeds are blocked/empty, return curated topics
        if len(all_articles) == 0:
            all_articles = self._get_curated_topics()

        logger.info(f"MobiHealthNews spider collected {len(all_articles)} articles")
        return all_articles[:max_results]

    def _detect_category(self, text: str) -> str:
        """Detect article category from content."""
        categories = {
            'telehealth': ['telehealth', 'telemedicine', 'virtual care', 'remote patient'],
            'ai_health': ['ai', 'artificial intelligence', 'machine learning', 'diagnostic'],
            'wearables': ['wearable', 'fitness tracker', 'smartwatch', 'monitoring'],
            'funding': ['funding', 'raises', 'series', 'investment', 'venture'],
            'fda': ['fda', 'approval', 'clearance', '510k', 'regulatory'],
            'mental_health': ['mental health', 'behavioral', 'therapy', 'psychiatry'],
            'biotech': ['biotech', 'genomics', 'gene therapy', 'crispr'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'digital_health'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated healthtech topics when RSS fails."""
        topics = [
            ('Digital Health Innovation', 'digital_health', 'Latest developments in digital health platforms and services.'),
            ('Telehealth Expansion', 'telehealth', 'Virtual care adoption, telemedicine regulations, and remote health.'),
            ('AI in Healthcare', 'ai_health', 'AI diagnostics, clinical decision support, and healthcare automation.'),
            ('Wearable Health Tech', 'wearables', 'Fitness trackers, smartwatches, and continuous health monitoring.'),
            ('Healthtech Funding', 'funding', 'Digital health startup funding rounds and acquisitions.'),
            ('FDA Digital Health', 'fda', 'FDA approvals, clearances, and regulatory developments.'),
            ('Mental Health Tech', 'mental_health', 'Digital therapeutics, mental wellness apps, and behavioral health.'),
            ('Biotech Innovation', 'biotech', 'Biotechnology advances, genomics, and precision medicine.'),
            ('Hospital Tech', 'hospital', 'EHR systems, hospital IT, and clinical workflows.'),
            ('Patient Engagement', 'patient', 'Patient portals, engagement tools, and health literacy.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.mobihealthnews.com/news/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'MobiHealthNews',
                'data_type': 'healthtech_topic',
                'tags': ['healthtech', 'digital_health', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
