"""
Legal News Spider
=================

Session 399: Created to replace JustiaSpider (blocked by Cloudflare).

Fetches legal news from working RSS sources:
- SCOTUSblog - Supreme Court news and analysis
- Google News Legal - Aggregated legal news

All data is publicly accessible via RSS feeds.
"""

import feedparser
import requests
from typing import Dict, List, Any
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class LegalNewsSpider:
    """Spider for fetching legal news from RSS feeds"""

    name = "legal_news"

    RSS_FEEDS = [
        ('SCOTUSblog', 'https://www.scotusblog.com/feed/'),
        ('Google News Legal', 'https://news.google.com/rss/search?q=legal+law+court+ruling&hl=en-US&gl=US&ceid=US:en'),
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })

    def fetch_data(self, max_results: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch legal news from RSS feeds

        Args:
            max_results: Maximum number of articles to fetch

        Returns:
            List of legal news articles
        """
        all_articles = []
        per_feed_limit = max_results // len(self.RSS_FEEDS) + 5

        for feed_name, feed_url in self.RSS_FEEDS:
            try:
                logger.info(f"Fetching legal news from {feed_name}: {feed_url}")

                response = self.session.get(feed_url, timeout=15)
                if response.status_code != 200:
                    logger.warning(f"{feed_name} returned status {response.status_code}")
                    continue

                feed = feedparser.parse(response.content)

                for entry in feed.entries[:per_feed_limit]:
                    # Clean HTML from description
                    description = entry.get('summary', entry.get('description', ''))
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                    all_articles.append({
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'summary': description,
                        'date_published': entry.get('published', datetime.now().strftime('%Y-%m-%d')),
                        'source': feed_name,
                        'data_type': 'legal_news',
                        'tags': self._extract_tags(entry.get('title', ''), description),
                        'timestamp': datetime.now().isoformat(),
                    })

                logger.info(f"Fetched {len(feed.entries[:per_feed_limit])} articles from {feed_name}")

            except Exception as e:
                logger.error(f"Error fetching {feed_name}: {e}")
                continue

        logger.info(f"Total legal news articles fetched: {len(all_articles)}")
        return all_articles[:max_results]

    def _extract_tags(self, title: str, summary: str) -> List[str]:
        """Extract relevant tags from article title and summary"""
        tags = ['legal', 'news']

        text = f"{title} {summary}".lower()

        # Practice areas
        tag_keywords = {
            'supreme_court': ['supreme court', 'scotus', 'justices'],
            'criminal': ['criminal', 'prosecution', 'defendant', 'sentence', 'conviction'],
            'civil': ['civil', 'plaintiff', 'damages', 'lawsuit'],
            'constitutional': ['constitutional', 'amendment', 'rights'],
            'corporate': ['corporate', 'business', 'securities', 'merger'],
            'employment': ['employment', 'labor', 'discrimination', 'workplace'],
            'immigration': ['immigration', 'visa', 'deportation', 'asylum'],
            'environmental': ['environmental', 'epa', 'pollution', 'climate'],
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)

        return tags
