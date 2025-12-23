"""
WeWorkRemotely Spider - Remote Job Intelligence
================================================

Session 534: Simplified to work with spider network interface.
Aggregates remote job opportunities via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class WeWorkRemotelySpider:
    """WeWorkRemotely spider - remote job opportunities"""

    name = "weworkremotely"

    # Remote job RSS feeds
    RSS_FEEDS = {
        'programming': 'https://weworkremotely.com/categories/remote-programming-jobs.rss',
        'design': 'https://weworkremotely.com/categories/remote-design-jobs.rss',
        'devops': 'https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss',
        'management': 'https://weworkremotely.com/categories/remote-management-finance-jobs.rss',
        'customer_support': 'https://weworkremotely.com/categories/remote-customer-support-jobs.rss',
        'sales_marketing': 'https://weworkremotely.com/categories/remote-sales-marketing-jobs.rss',
    }

    # Job categories
    CATEGORIES = [
        ('Programming', 'programming', 'Software development and engineering.'),
        ('Design', 'design', 'UI/UX and graphic design.'),
        ('DevOps', 'devops', 'System administration and cloud.'),
        ('Management', 'management', 'Leadership and management roles.'),
        ('Marketing', 'marketing', 'Sales and digital marketing.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.job_categories = {
            'programming': ['developer', 'engineer', 'programmer', 'software', 'backend', 'frontend', 'fullstack'],
            'design': ['designer', 'ui', 'ux', 'graphic', 'product design', 'visual'],
            'devops': ['devops', 'sysadmin', 'infrastructure', 'cloud', 'aws', 'kubernetes'],
            'data': ['data', 'analyst', 'scientist', 'machine learning', 'ai', 'analytics'],
            'management': ['manager', 'lead', 'director', 'head of', 'vp', 'chief'],
            'marketing': ['marketing', 'growth', 'seo', 'content', 'social media'],
        }
        self.seniority_levels = {
            'senior': ['senior', 'sr.', 'lead', 'principal', 'staff'],
            'mid': ['mid-level', 'intermediate', '3+ years', '5+ years'],
            'junior': ['junior', 'jr.', 'entry', 'associate', 'trainee'],
        }
        self.tech_stacks = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'react', 'vue', 'angular', 'node', 'typescript'],
            'ruby': ['ruby', 'rails', 'ruby on rails'],
            'java': ['java', 'spring', 'kotlin'],
            'go': ['golang', 'go '],
            'mobile': ['ios', 'android', 'swift', 'react native', 'flutter'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch remote job listings from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of job listing dictionaries
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

        logger.info(f"WeWorkRemotely spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch remote job listings from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Extract company from title
                company = self._extract_company(title)

                # Analysis
                text = f"{title} {description}".lower()
                category = self._detect_category(text, feed_name)
                seniority = self._detect_seniority(text)
                tech_stack = self._detect_tech_stack(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'company': company,
                    'category': category,
                    'seniority': seniority,
                    'tech_stack': tech_stack,
                    'is_remote': True,
                    'source': 'WeWorkRemotely',
                    'data_type': 'remote_job',
                    'platform': 'weworkremotely',
                    'tags': ['remote', 'jobs', category] + tech_stack[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _extract_company(self, title: str) -> str:
        """Extract company name from job title."""
        if ':' in title:
            return title.split(':')[0].strip()
        return 'Remote Company'

    def _detect_category(self, text: str, feed_name: str) -> str:
        """Detect job category from text."""
        for category, keywords in self.job_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return feed_name

    def _detect_seniority(self, text: str) -> str:
        """Detect seniority level from text."""
        for level, keywords in self.seniority_levels.items():
            if any(kw in text for kw in keywords):
                return level
        return 'mid'

    def _detect_tech_stack(self, text: str) -> List[str]:
        """Detect tech stack from text."""
        tech_stack = []
        for tech, keywords in self.tech_stacks.items():
            if any(kw in text for kw in keywords):
                tech_stack.append(tech)
        return tech_stack

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return job category links."""
        return [
            {
                'title': f"Remote: {name} Jobs",
                'url': f'https://weworkremotely.com/categories/remote-{slug}-jobs',
                'link': f'https://weworkremotely.com/categories/remote-{slug}-jobs',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'WeWorkRemotely',
                'data_type': 'job_category',
                'platform': 'weworkremotely',
                'tags': ['remote', 'jobs', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Remote Programming Jobs', 'programming', 'Software development roles.'),
            ('Remote Design Jobs', 'design', 'Design and creative roles.'),
            ('Remote DevOps Jobs', 'devops', 'Infrastructure and cloud roles.'),
            ('Remote Management Jobs', 'management', 'Leadership positions.'),
            ('Remote Marketing Jobs', 'marketing', 'Sales and marketing roles.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://weworkremotely.com/categories/remote-{category}-jobs',
                'link': f'https://weworkremotely.com/categories/remote-{category}-jobs',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'WeWorkRemotely',
                'data_type': 'job_topic',
                'platform': 'weworkremotely',
                'tags': ['remote', 'jobs', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
