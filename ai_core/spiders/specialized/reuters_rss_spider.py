"""
Reuters RSS Spider - International News Agency
===============================================

Session 534: Simplified to work with spider network interface.
Aggregates Reuters and major news wire content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReutersRSSSpider:
    """Reuters RSS spider - international news agency coverage"""

    name = "reuters_rss"

    # News wire RSS feeds
    RSS_FEEDS = {
        'reuters_business': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
        'reuters_world': 'https://www.reutersagency.com/feed/?best-topics=world&post_type=best',
        'reuters_tech': 'https://www.reutersagency.com/feed/?best-topics=tech&post_type=best',
        'ap_news': 'https://rsshub.app/apnews/topics/apf-topnews',
        'bbc_world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'npr_news': 'https://feeds.npr.org/1001/rss.xml',
    }

    # News categories
    CATEGORIES = [
        ('Business', 'business', 'Business and finance news.'),
        ('World', 'world', 'International news coverage.'),
        ('Technology', 'tech', 'Technology news.'),
        ('Politics', 'politics', 'Political news and analysis.'),
        ('Markets', 'markets', 'Financial market updates.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.news_categories = {
            'markets': ['market', 'stock', 'trading', 'wall street', 'nasdaq', 'dow'],
            'economy': ['economy', 'gdp', 'inflation', 'fed', 'central bank', 'rate'],
            'corporate': ['company', 'earnings', 'ceo', 'merger', 'acquisition', 'ipo'],
            'tech': ['tech', 'technology', 'ai', 'software', 'digital', 'cyber'],
            'politics': ['congress', 'government', 'election', 'policy', 'senate'],
            'world': ['international', 'global', 'china', 'europe', 'asia'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news from Reuters and wire service RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of news article dictionaries
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
            logger.warning(f"Error getting news categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Reuters RSS spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch news articles from RSS feed."""
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

                # Detect news category and urgency
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                is_breaking = self._is_breaking(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Reuters'),
                    'category': category,
                    'is_breaking': is_breaking,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'news',
                    'platform': 'reuters_rss',
                    'tags': ['news', 'wire', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect news category from text."""
        for category, keywords in self.news_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _is_breaking(self, text: str) -> bool:
        """Check if news is breaking."""
        breaking_keywords = ['breaking', 'urgent', 'just in', 'flash', 'alert', 'developing']
        return any(kw in text for kw in breaking_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        positive = ['gain', 'rise', 'grow', 'success', 'profit', 'win', 'surge']
        negative = ['fall', 'drop', 'loss', 'fail', 'crash', 'decline', 'crisis']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return news category links."""
        return [
            {
                'title': f"Reuters: {name}",
                'url': f'https://www.reuters.com/{slug}/',
                'link': f'https://www.reuters.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Reuters',
                'data_type': 'news_category',
                'platform': 'reuters_rss',
                'tags': ['news', 'reuters', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Business News', 'business', 'Business and corporate news.'),
            ('World News', 'world', 'International news coverage.'),
            ('Technology News', 'tech', 'Tech industry coverage.'),
            ('Markets', 'markets', 'Financial market updates.'),
            ('Politics', 'politics', 'Political news and analysis.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.reuters.com/{category}/',
                'link': f'https://www.reuters.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Reuters',
                'data_type': 'news_topic',
                'platform': 'reuters_rss',
                'tags': ['news', 'reuters', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
