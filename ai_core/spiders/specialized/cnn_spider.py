"""
CNN Spider - Cable News Network RSS Feed
=========================================

Session 534: Simplified to work with spider network interface.
CNN provides news coverage via free RSS feeds.
"""

import feedparser
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CNNSpider:
    """CNN news spider - breaking news via RSS"""

    name = "cnn"

    RSS_FEEDS = {
        'top_stories': 'http://rss.cnn.com/rss/cnn_topstories.rss',
        'world': 'http://rss.cnn.com/rss/cnn_world.rss',
        'us': 'http://rss.cnn.com/rss/cnn_us.rss',
        'business': 'http://rss.cnn.com/rss/money_latest.rss',
        'politics': 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
        'tech': 'http://rss.cnn.com/rss/cnn_tech.rss',
        'health': 'http://rss.cnn.com/rss/cnn_health.rss',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news articles from CNN RSS feeds.

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

                for entry in feed.entries[:10]:
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
                        import re
                        summary = re.sub(r'<[^>]+>', '', summary)[:500]

                    article = {
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'description': summary,
                        'published': entry.get('published', ''),
                        'category': feed_name,
                        'source': 'CNN',
                        'data_type': 'news_article',
                        'tags': ['news', 'cnn', feed_name.replace('_', ' ')],
                        'timestamp': datetime.now().isoformat(),
                    }
                    all_articles.append(article)

                    if len(all_articles) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Error fetching CNN {feed_name} feed: {e}")
                continue

            if len(all_articles) >= max_results:
                break

        logger.info(f"CNN spider collected {len(all_articles)} articles")
        return all_articles[:max_results]
