"""
AngelList Spider - Startup Job & Investment Intelligence
=========================================================

Session 534: Simplified to work with spider network interface.
Uses startup ecosystem RSS feeds (YC, TechStartups) for startup news.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AngelListSpider:
    """AngelList/Wellfound spider - startup jobs and ecosystem intelligence"""

    name = "angellist"

    # Startup ecosystem RSS feeds
    RSS_FEEDS = {
        'ycombinator': 'https://news.ycombinator.com/rss',
        'techstartups': 'https://techstartups.com/feed/',
        'eu_startups': 'https://www.eu-startups.com/feed/',
    }

    # Startup job categories on Wellfound
    CATEGORIES = [
        ('Engineering', 'role/engineering', 'Software engineering roles at startups.'),
        ('Product', 'role/product', 'Product management positions.'),
        ('Design', 'role/design', 'UI/UX design at startups.'),
        ('Marketing', 'role/marketing', 'Growth and marketing roles.'),
        ('Sales', 'role/sales', 'Sales and business development.'),
        ('Operations', 'role/operations', 'Operations and finance.'),
        ('Remote Startups', 'remote', 'Remote-first startup jobs.'),
        ('Early Stage', 'stage/seed', 'Seed and early stage startups.'),
        ('AI Startups', 'ai-machine-learning', 'AI/ML focused startups.'),
        ('Fintech', 'fintech', 'Financial technology startups.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch startup ecosystem news and job categories.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of startup news and category dictionaries
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

        # Add startup job category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Wellfound categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"AngelList spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch startup news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Detect startup-related content
                text = f"{title} {description}".lower()
                is_startup = self._is_startup_relevant(text)
                industry = self._detect_industry(text)
                stage = self._detect_stage(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': industry,
                    'stage': stage,
                    'is_startup_relevant': is_startup,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'startup_news',
                    'platform': 'angellist',
                    'tags': ['startup', 'venture', 'tech', industry],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _is_startup_relevant(self, text: str) -> bool:
        """Check if content is startup-relevant."""
        keywords = ['startup', 'founder', 'funding', 'series', 'raise', 'venture',
                    'yc', 'launch', 'seed', 'angel', 'investor', 'valuation']
        return any(kw in text for kw in keywords)

    def _detect_industry(self, text: str) -> str:
        """Detect startup industry from text."""
        industries = {
            'ai_ml': ['ai', 'machine learning', 'artificial intelligence', 'llm', 'gpt'],
            'fintech': ['fintech', 'payments', 'banking', 'crypto', 'defi'],
            'healthtech': ['healthtech', 'health', 'medical', 'biotech'],
            'saas': ['saas', 'b2b', 'enterprise', 'software'],
            'ecommerce': ['ecommerce', 'marketplace', 'retail'],
            'edtech': ['edtech', 'education', 'learning'],
            'climate': ['climate', 'cleantech', 'sustainability'],
        }

        for ind, keywords in industries.items():
            if any(kw in text for kw in keywords):
                return ind
        return 'general'

    def _detect_stage(self, text: str) -> str:
        """Detect startup stage from text."""
        stages = {
            'seed': ['seed', 'pre-seed', 'angel', 'bootstrapped'],
            'early': ['series a', 'series b', 'early stage'],
            'growth': ['series c', 'series d', 'late stage'],
            'public': ['ipo', 'public', 'nasdaq', 'nyse'],
        }

        for stage, keywords in stages.items():
            if any(kw in text for kw in keywords):
                return stage
        return 'unknown'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Wellfound (AngelList) job category links."""
        return [
            {
                'title': f"Wellfound: {name}",
                'url': f'https://wellfound.com/{slug}',
                'link': f'https://wellfound.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug.split('/')[-1] if '/' in slug else slug,
                'source': 'Wellfound',
                'data_type': 'startup_job_category',
                'platform': 'angellist',
                'tags': ['startup', 'jobs', 'wellfound', slug.split('/')[-1]],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Startup Jobs', 'jobs', 'Jobs at venture-backed startups.'),
            ('Remote Startups', 'remote', 'Remote-first startup positions.'),
            ('AI/ML Startups', 'ai', 'Artificial intelligence startups.'),
            ('Funded Startups', 'funded', 'Recently funded companies.'),
            ('YC Companies', 'yc', 'Y Combinator backed startups.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://wellfound.com/discover/{category}',
                'link': f'https://wellfound.com/discover/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Wellfound',
                'data_type': 'startup_topic',
                'platform': 'angellist',
                'tags': ['startup', 'wellfound', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
