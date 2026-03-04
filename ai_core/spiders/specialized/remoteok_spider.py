"""
RemoteOK Spider - Remote Jobs Platform Intelligence
====================================================

Session 534: Simplified to work with spider network interface.
Uses RemoteOK API and remote job RSS feeds.
"""

from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RemoteOKSpider:
    """RemoteOK spider - remote tech jobs worldwide"""

    name = "remoteok"

    # RemoteOK provides a JSON API
    API_URL = "https://remoteok.com/api"

    # Remote job RSS feeds (fallback)
    RSS_FEEDS = {
        'weworkremotely': 'https://weworkremotely.com/remote-jobs.rss',
        'remotive': 'https://remotive.com/remote-jobs/feed',
        'remote_co': 'https://remote.co/remote-jobs/feed/',
        'flexjobs': 'https://www.flexjobs.com/rss/all',
    }

    # Job categories
    CATEGORIES = [
        ('Engineering', 'dev', 'Software development and engineering.'),
        ('Design', 'design', 'UI/UX and graphic design.'),
        ('Marketing', 'marketing', 'Digital marketing and growth.'),
        ('Sales', 'sales', 'Sales and business development.'),
        ('Support', 'support', 'Customer support and success.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.tech_categories = {
            'engineering': ['developer', 'engineer', 'programmer', 'backend', 'frontend', 'fullstack'],
            'design': ['designer', 'ui', 'ux', 'graphic', 'product design'],
            'marketing': ['marketing', 'seo', 'growth', 'content', 'social media'],
            'sales': ['sales', 'account', 'business development', 'revenue'],
            'support': ['support', 'customer success', 'help desk', 'service'],
            'devops': ['devops', 'sre', 'infrastructure', 'cloud', 'aws', 'kubernetes'],
            'data': ['data', 'analyst', 'scientist', 'machine learning', 'ai'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch remote jobs from RemoteOK API and RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of remote job dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try RemoteOK API first
        try:
            api_items = self._fetch_remoteok_api()
            for item in api_items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)
        except Exception as e:
            logger.warning(f"Error fetching RemoteOK API: {e}")

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

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"RemoteOK spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_remoteok_api(self) -> List[Dict[str, Any]]:
        """Fetch jobs from RemoteOK JSON API."""
        items = []

        try:
            headers = {'User-Agent': 'DonkeyBetz-Spider/1.0'}
            response = cached_get(self.API_URL, headers=headers, timeout=15)

            if response.status_code == 200:
                jobs = response.json()

                # First item is usually metadata, skip it
                for job in jobs[1:25] if len(jobs) > 1 else []:
                    if not isinstance(job, dict):
                        continue

                    title = job.get('position', '')
                    if not title:
                        continue

                    company = job.get('company', 'Remote Company')
                    salary = self._format_salary(job.get('salary_min'), job.get('salary_max'))
                    tags = job.get('tags', [])
                    category = self._detect_category(f"{title} {' '.join(tags)}".lower())

                    items.append({
                        'title': f"{title} at {company}",
                        'url': job.get('url', f"https://remoteok.com/jobs/{job.get('id', '')}"),
                        'link': job.get('url', f"https://remoteok.com/jobs/{job.get('id', '')}"),
                        'summary': job.get('description', '')[:400] if job.get('description') else '',
                        'description': job.get('description', '')[:400] if job.get('description') else '',
                        'company': company,
                        'company_logo': job.get('company_logo', ''),
                        'salary': salary,
                        'tags': tags[:10],
                        'category': category,
                        'location': job.get('location', 'Worldwide'),
                        'posted_date': job.get('date', ''),
                        'source': 'RemoteOK',
                        'data_type': 'remote_job',
                        'platform': 'remoteok',
                        'remote_type': 'fully_remote',
                        'job_tags': ['remote', 'tech', category] + tags[:3],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error parsing RemoteOK API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch remote jobs from RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect job category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                salary = self._extract_salary(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'salary': salary,
                    'location': 'Remote',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'remote_job',
                    'platform': 'remoteok',
                    'remote_type': 'fully_remote',
                    'tags': ['remote', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect job category from text."""
        for category, keywords in self.tech_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _format_salary(self, min_sal: Any, max_sal: Any) -> str:
        """Format salary range."""
        if min_sal and max_sal:
            return f"${int(min_sal):,} - ${int(max_sal):,}"
        elif min_sal:
            return f"${int(min_sal):,}+"
        elif max_sal:
            return f"Up to ${int(max_sal):,}"
        return ''

    def _extract_salary(self, text: str) -> str:
        """Extract salary from text."""
        patterns = [
            r'\$[\d,]+k?\s*-\s*\$?[\d,]+k?',
            r'\$[\d,]+k?(?:\s*\/\s*(?:year|yr|annual))?',
            r'[\d,]+k?\s*(?:USD|usd)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return ''

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Remote Engineering Jobs', 'dev', 'Software development positions.'),
            ('Remote Design Jobs', 'design', 'UI/UX and graphic design.'),
            ('Remote Marketing Jobs', 'marketing', 'Digital marketing roles.'),
            ('Remote Sales Jobs', 'sales', 'Sales and BD positions.'),
            ('Remote Support Jobs', 'support', 'Customer success roles.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://remoteok.com/remote-{category}-jobs',
                'link': f'https://remoteok.com/remote-{category}-jobs',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'RemoteOK',
                'data_type': 'job_category',
                'platform': 'remoteok',
                'tags': ['remote', 'jobs', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
