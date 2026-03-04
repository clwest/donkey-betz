"""
Adzuna Spider - Global Job Market Intelligence
===============================================

Session 534: Simplified to work with spider network interface.
Uses Adzuna API for job listings or falls back to job-related RSS feeds.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AdzunaSpider:
    """Adzuna spider - global job market intelligence and salary data"""

    name = "adzuna"

    BASE_URL = 'https://api.adzuna.com/v1/api'

    # Fallback job news RSS feeds
    RSS_FEEDS = {
        'indeed_blog': 'https://www.indeed.com/lead/feed',
        'linkedin_blog': 'https://blog.linkedin.com/feed/',
    }

    # Job categories
    JOB_CATEGORIES = [
        ('IT Jobs', 'it-jobs', 'Software development and tech roles.'),
        ('Remote Jobs', 'remote', 'Work from home opportunities.'),
        ('Creative Jobs', 'creative-design-jobs', 'Design and creative roles.'),
        ('Marketing Jobs', 'marketing-jobs', 'Marketing and advertising.'),
        ('Engineering Jobs', 'engineering-jobs', 'Engineering positions.'),
        ('Data Science', 'data-science', 'Data and analytics roles.'),
        ('Finance Jobs', 'finance-jobs', 'Finance and accounting.'),
        ('Sales Jobs', 'sales-jobs', 'Sales and business development.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.app_id = os.getenv('ADZUNA_APP_ID', '')
        self.app_key = os.getenv('ADZUNA_APP_KEY', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch job listings from Adzuna API or fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of job and category dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Adzuna API first
        if self.app_id and self.app_key:
            try:
                api_items = self._fetch_from_api()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching Adzuna API: {e}")

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

        # Add job category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting job categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Adzuna spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_api(self) -> List[Dict[str, Any]]:
        """Fetch jobs from Adzuna API."""
        items = []

        try:
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': 20,
                'what': 'remote developer',
                'content-type': 'application/json',
            }

            url = f"{self.BASE_URL}/jobs/us/search/1"
            response = cached_get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for job in data.get('results', [])[:20]:
                    title = job.get('title', '')
                    description = job.get('description', '')[:500] if job.get('description') else ''

                    items.append({
                        'title': title,
                        'url': job.get('redirect_url', ''),
                        'link': job.get('redirect_url', ''),
                        'summary': description,
                        'description': description,
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'salary_min': job.get('salary_min', 0),
                        'salary_max': job.get('salary_max', 0),
                        'category': job.get('category', {}).get('label', 'general'),
                        'source': 'Adzuna API',
                        'data_type': 'job_listing',
                        'platform': 'adzuna',
                        'tags': ['jobs', 'adzuna', 'remote', 'hiring'],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error calling Adzuna API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch job news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': 'job_news',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'job_article',
                    'platform': 'adzuna',
                    'tags': ['jobs', 'career', 'hiring', 'employment'],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Adzuna job category links."""
        return [
            {
                'title': f"Adzuna: {name}",
                'url': f'https://www.adzuna.com/search?q={slug}',
                'link': f'https://www.adzuna.com/search?q={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Adzuna',
                'data_type': 'job_category',
                'platform': 'adzuna',
                'tags': ['jobs', 'adzuna', 'career', slug.split('-')[0]],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.JOB_CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Remote Tech Jobs', 'remote-tech', 'Work from home technology roles.'),
            ('Software Developer Jobs', 'developer', 'Programming and development.'),
            ('Data Science Jobs', 'data-science', 'Analytics and ML positions.'),
            ('Design Jobs', 'design', 'UI/UX and graphic design.'),
            ('Marketing Jobs', 'marketing', 'Digital marketing roles.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.adzuna.com/search?q={category}',
                'link': f'https://www.adzuna.com/search?q={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Adzuna',
                'data_type': 'job_topic',
                'platform': 'adzuna',
                'tags': ['jobs', 'adzuna', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
