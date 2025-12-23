"""
Guru Spider - Freelance Marketplace Intelligence
=================================================

Session 534: Simplified to work with spider network interface.
Aggregates freelance job content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class GuruIntelligenceSpider:
    """Guru spider - freelance job opportunities from various platforms"""

    name = "guru"

    # Freelance job RSS feeds (general freelance, not just Guru.com)
    RSS_FEEDS = {
        'freelancer_rss': 'https://www.freelancer.com/rss.xml',
        'indeed_remote': 'https://www.indeed.com/rss?q=remote+freelance',
    }

    # Job categories
    CATEGORIES = [
        ('Development', 'development', 'Software and web development.'),
        ('Design', 'design', 'Graphic and UI/UX design.'),
        ('Writing', 'writing', 'Content and copywriting.'),
        ('Marketing', 'marketing', 'Digital marketing and SEO.'),
        ('Data', 'data', 'Data analysis and science.'),
        ('Admin', 'admin', 'Administrative and support.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.job_categories = {
            'development': ['developer', 'programmer', 'software', 'python', 'javascript', 'react', 'node'],
            'design': ['designer', 'ui', 'ux', 'graphic', 'figma', 'photoshop', 'illustrator'],
            'writing': ['writer', 'copywriter', 'content', 'editor', 'blog', 'article'],
            'marketing': ['marketing', 'seo', 'social media', 'ads', 'ppc', 'growth'],
            'data': ['data', 'analyst', 'sql', 'excel', 'analytics', 'scientist'],
            'admin': ['admin', 'assistant', 'data entry', 'support', 'customer service'],
        }
        self.budget_ranges = {
            'micro': (0, 250),
            'small': (250, 1000),
            'medium': (1000, 5000),
            'large': (5000, 25000),
            'enterprise': (25000, float('inf'))
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch freelance job listings from RSS feeds.

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

        logger.info(f"Guru spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch jobs from freelance RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:600]

                # Detect job details
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                budget = self._extract_budget(text)
                budget_tier = self._classify_budget_tier(budget)
                skills = self._extract_skills(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'job_category': category,
                    'budget': budget,
                    'budget_tier': budget_tier,
                    'skills_required': skills,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'freelance_job',
                    'platform': 'guru',
                    'tags': ['freelance', 'jobs', category] + skills[:3],
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

    def _extract_budget(self, text: str) -> Optional[str]:
        """Extract budget from text."""
        patterns = [
            r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?',
            r'[\d,]+\s*-\s*[\d,]+\s*(?:usd|dollars?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return None

    def _classify_budget_tier(self, budget: Optional[str]) -> str:
        """Classify budget into tiers."""
        if not budget:
            return 'unknown'

        budget_nums = re.findall(r'\d+', budget.replace(',', ''))
        if not budget_nums:
            return 'unknown'

        max_budget = max([int(num) for num in budget_nums])

        for tier, (min_val, max_val) in self.budget_ranges.items():
            if min_val <= max_budget < max_val:
                return tier

        return 'unknown'

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        all_skills = [
            'python', 'javascript', 'react', 'node', 'django', 'flask',
            'html', 'css', 'sql', 'mongodb', 'aws', 'docker',
            'figma', 'photoshop', 'illustrator', 'ui', 'ux',
            'seo', 'marketing', 'content', 'copywriting', 'excel'
        ]
        found = []
        for skill in all_skills:
            if skill in text:
                found.append(skill)
        return found[:10]

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return job category links."""
        return [
            {
                'title': f"Freelance: {name}",
                'url': f'https://www.guru.com/d/jobs/c/{slug}/',
                'link': f'https://www.guru.com/d/jobs/c/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Guru',
                'data_type': 'job_category',
                'platform': 'guru',
                'tags': ['freelance', 'jobs', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Development Jobs', 'development', 'Software and web development freelance.'),
            ('Design Jobs', 'design', 'Graphic and UI/UX design gigs.'),
            ('Writing Jobs', 'writing', 'Content and copywriting projects.'),
            ('Marketing Jobs', 'marketing', 'Digital marketing freelance.'),
            ('Data Jobs', 'data', 'Data analysis opportunities.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.guru.com/d/jobs/c/{category}/',
                'link': f'https://www.guru.com/d/jobs/c/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Guru',
                'data_type': 'job_topic',
                'platform': 'guru',
                'tags': ['freelance', 'jobs', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
