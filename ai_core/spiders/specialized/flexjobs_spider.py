"""
FlexJobs Spider - Remote Work & Flexible Jobs Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
Uses remote work RSS feeds and job board data.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FlexJobsIntelligenceSpider:
    """FlexJobs spider - remote work and flexible job opportunities"""

    name = "flexjobs"

    # Remote work RSS feeds
    RSS_FEEDS = {
        'weworkremotely': 'https://weworkremotely.com/remote-jobs.rss',
        'remoteok': 'https://remoteok.com/remote-jobs.rss',
        'remoteco': 'https://remote.co/remote-jobs/feed/',
    }

    # Job categories
    CATEGORIES = [
        ('Technology', 'technology', 'Tech and software development jobs.'),
        ('Marketing', 'marketing', 'Marketing and growth positions.'),
        ('Writing', 'writing', 'Content and copywriting jobs.'),
        ('Design', 'design', 'Design and creative positions.'),
        ('Customer Service', 'customer-service', 'Support and service roles.'),
        ('Data', 'data', 'Data analysis and science jobs.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.job_categories = {
            'technology': ['developer', 'engineer', 'software', 'python', 'javascript', 'devops'],
            'marketing': ['marketing', 'growth', 'seo', 'content', 'social media', 'ppc'],
            'writing': ['writer', 'copywriter', 'editor', 'content', 'blog', 'journalist'],
            'design': ['designer', 'ui', 'ux', 'graphic', 'creative', 'figma'],
            'customer_service': ['customer', 'support', 'service', 'help desk', 'success'],
            'data': ['data', 'analyst', 'scientist', 'sql', 'analytics', 'bi'],
        }
        self.remote_types = {
            'fully_remote': ['fully remote', '100% remote', 'remote only', 'anywhere'],
            'hybrid': ['hybrid', 'part remote', 'flexible'],
            'remote': ['remote', 'work from home', 'wfh', 'telecommute'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch remote job listings from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of job dictionaries
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
            logger.warning(f"Error getting job categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"FlexJobs spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch jobs from remote work RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect job details
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                remote_level = self._detect_remote_level(text)
                salary = self._extract_salary(text)
                company = self._extract_company(title, summary)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'company': company,
                    'category': category,
                    'job_category': category,
                    'remote_level': remote_level,
                    'salary_range': salary,
                    'is_fully_remote': remote_level == 'fully_remote',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'remote_job',
                    'platform': 'flexjobs',
                    'tags': ['jobs', 'remote', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect job category from text."""
        for category, keywords in self.job_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_remote_level(self, text: str) -> str:
        """Detect remote work level from text."""
        for level, keywords in self.remote_types.items():
            if any(kw in text for kw in keywords):
                return level
        return 'remote'

    def _extract_salary(self, text: str) -> str:
        """Extract salary range from text."""
        patterns = [
            r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*(?:per\s+)?(?:year|yr|annual))?',
            r'[\d,]+k\s*-\s*[\d,]+k',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return None

    def _extract_company(self, title: str, summary: str) -> str:
        """Extract company name from title or summary."""
        # Common pattern: "Job Title at Company"
        at_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&]+)', title)
        if at_match:
            return at_match.group(1).strip()

        # Pattern: "Company - Job Title"
        dash_match = re.search(r'^([A-Z][A-Za-z0-9\s&]+)\s*[-–]', title)
        if dash_match:
            return dash_match.group(1).strip()

        return 'Remote Company'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return job category links."""
        return [
            {
                'title': f"Remote Jobs: {name}",
                'url': f'https://weworkremotely.com/categories/remote-{slug}-jobs',
                'link': f'https://weworkremotely.com/categories/remote-{slug}-jobs',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'FlexJobs',
                'data_type': 'job_category',
                'platform': 'flexjobs',
                'tags': ['jobs', 'remote', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Tech Remote Jobs', 'technology', 'Software and development positions.'),
            ('Marketing Remote Jobs', 'marketing', 'Marketing and growth roles.'),
            ('Writing Remote Jobs', 'writing', 'Content and copywriting.'),
            ('Design Remote Jobs', 'design', 'Design and creative work.'),
            ('Customer Service Remote', 'support', 'Support positions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://weworkremotely.com/categories/remote-{category}-jobs',
                'link': f'https://weworkremotely.com/categories/remote-{category}-jobs',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'FlexJobs',
                'data_type': 'job_topic',
                'platform': 'flexjobs',
                'tags': ['jobs', 'remote', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
