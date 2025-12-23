"""
TechCrunch Spider - Tech Startup & AI News Intelligence
=======================================================

Session 534: Simplified to work with spider network interface.
Aggregates tech startup, AI, and funding news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TechCrunchSpider:
    """TechCrunch spider - startups, AI, and funding news"""

    name = "techcrunch"

    # TechCrunch and tech news RSS feeds
    RSS_FEEDS = {
        'techcrunch_main': 'https://techcrunch.com/feed/',
        'techcrunch_startups': 'https://techcrunch.com/category/startups/feed/',
        'techcrunch_ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'techcrunch_venture': 'https://techcrunch.com/category/venture/feed/',
        'the_information': 'https://www.theinformation.com/feed',
    }

    # News categories
    CATEGORIES = [
        ('Startups', 'startups', 'Startup news and launches.'),
        ('AI & ML', 'ai', 'Artificial intelligence and machine learning.'),
        ('Venture Capital', 'venture', 'Funding rounds and investments.'),
        ('Big Tech', 'bigtech', 'Google, Apple, Microsoft, Meta, Amazon.'),
        ('Crypto & Web3', 'crypto', 'Blockchain and cryptocurrency.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.tech_categories = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm', 'neural', 'deep learning', 'generative ai'],
            'startups': ['startup', 'founded', 'launch', 'seed', 'series a', 'series b', 'funding', 'unicorn'],
            'big_tech': ['google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook', 'openai', 'anthropic'],
            'crypto_web3': ['crypto', 'blockchain', 'web3', 'nft', 'defi', 'bitcoin', 'ethereum'],
            'fintech': ['fintech', 'payments', 'banking', 'lending', 'insurtech', 'neobank'],
            'saas': ['saas', 'enterprise', 'b2b', 'software', 'cloud'],
            'hardware': ['hardware', 'chip', 'semiconductor', 'device', 'gadget', 'robotics'],
            'defense_tech': ['defense', 'military', 'dod', 'pentagon', 'aerospace'],
            'healthtech': ['healthtech', 'biotech', 'medtech', 'digital health', 'telehealth'],
            'cybersecurity': ['cybersecurity', 'infosec', 'security', 'breach', 'ransomware'],
        }
        self.funding_keywords = {
            'seed': ['seed', 'pre-seed', 'angel'],
            'series_a': ['series a', '$5m', '$10m', '$15m'],
            'series_b': ['series b', '$20m', '$30m', '$50m'],
            'series_c_plus': ['series c', 'series d', 'series e', '$100m', '$200m'],
            'ipo': ['ipo', 'public offering', 'going public'],
            'acquisition': ['acquired', 'acquisition', 'buys', 'purchased'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch tech news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of tech news dictionaries
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
            logger.warning(f"Error getting tech categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"TechCrunch spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch tech news from RSS feed."""
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

                # Analysis
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                funding_stage = self._detect_funding_stage(text)
                sentiment = self._analyze_sentiment(text)
                is_ai_related = 'ai_ml' in categories
                is_funding_news = funding_stage is not None

                # Extract tags from entry if available
                entry_tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    entry_tags = [tag.term for tag in entry.tags[:5]]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'TechCrunch'),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'funding_stage': funding_stage,
                    'sentiment': sentiment,
                    'is_ai_related': is_ai_related,
                    'is_funding_news': is_funding_news,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'tech_news',
                    'platform': 'techcrunch',
                    'tags': ['tech', 'startups', 'news'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect tech categories from text."""
        categories = []
        for category, keywords in self.tech_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories or ['general']

    def _detect_funding_stage(self, text: str) -> str:
        """Detect funding stage from text."""
        for stage, keywords in self.funding_keywords.items():
            if any(kw in text for kw in keywords):
                return stage
        return None

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        positive = ['launch', 'raise', 'grow', 'success', 'partnership', 'innovation', 'breakthrough']
        negative = ['layoff', 'shutdown', 'fail', 'decline', 'lawsuit', 'controversy', 'struggle']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return tech news category links."""
        return [
            {
                'title': f"TechCrunch: {name}",
                'url': f'https://techcrunch.com/category/{slug}/',
                'link': f'https://techcrunch.com/category/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'TechCrunch',
                'data_type': 'tech_category',
                'platform': 'techcrunch',
                'tags': ['tech', 'news', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Startup Funding News', 'startups', 'Latest funding rounds and launches.'),
            ('AI & Machine Learning', 'ai', 'Artificial intelligence developments.'),
            ('Big Tech Updates', 'bigtech', 'FAANG and major tech company news.'),
            ('Venture Capital', 'venture', 'VC trends and investments.'),
            ('Tech Industry Analysis', 'analysis', 'Industry insights and trends.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://techcrunch.com/category/{category}/',
                'link': f'https://techcrunch.com/category/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'TechCrunch',
                'data_type': 'tech_topic',
                'platform': 'techcrunch',
                'tags': ['tech', 'news', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
