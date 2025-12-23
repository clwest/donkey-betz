"""
Toptal Spider - Elite Freelance Intelligence
=============================================

Session 534: Simplified to work with spider network interface.
Uses Toptal blog RSS for industry insights and curated skill categories.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ToptalSpider:
    """Toptal spider - elite freelance opportunities and tech insights"""

    name = "toptal"

    # Toptal blog RSS feeds
    RSS_FEEDS = {
        'engineering': 'https://www.toptal.com/blog/engineering.rss',
        'developers': 'https://www.toptal.com/developers/blog.rss',
        'finance': 'https://www.toptal.com/finance/blog.rss',
        'design': 'https://www.toptal.com/designers/blog.rss',
    }

    # High-value skill categories
    SKILL_CATEGORIES = [
        # Development
        ('Full Stack Development', 'developers/full-stack', 'End-to-end web application development.'),
        ('React Development', 'developers/react', 'React.js frontend development.'),
        ('Node.js Development', 'developers/nodejs', 'Server-side JavaScript development.'),
        ('Python Development', 'developers/python', 'Python backend and data engineering.'),
        ('Mobile Development', 'developers/mobile', 'iOS and Android app development.'),

        # Data & AI
        ('Machine Learning', 'developers/machine-learning', 'ML models and AI solutions.'),
        ('Data Science', 'developers/data-science', 'Data analysis and modeling.'),
        ('Blockchain', 'developers/blockchain', 'Web3 and blockchain development.'),

        # Design
        ('UI/UX Design', 'designers/ui', 'User interface and experience design.'),
        ('Product Design', 'designers/product', 'End-to-end product design.'),
        ('Brand Design', 'designers/brand', 'Brand identity and visual design.'),

        # Finance
        ('Financial Modeling', 'finance/financial-modeling', 'Financial analysis and modeling.'),
        ('CFO Services', 'finance/interim-cfos', 'Fractional CFO consulting.'),

        # Project Management
        ('Product Management', 'project-managers/product', 'Product strategy and execution.'),
        ('Agile Coaching', 'project-managers/agile', 'Agile transformation consulting.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Toptal blog articles and skill categories.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of article and category dictionaries
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
                logger.warning(f"Error fetching Toptal {feed_name} feed: {e}")

        # Add skill category links
        try:
            categories = self._get_skill_categories()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Toptal categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Toptal spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from Toptal blog RSS."""
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
                    'author': entry.get('author', 'Toptal'),
                    'category': feed_name,
                    'source': 'Toptal Blog',
                    'data_type': 'tech_article',
                    'platform': 'toptal',
                    'tags': ['freelance', 'toptal', 'elite', feed_name],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing Toptal RSS: {e}")

        return items

    def _get_skill_categories(self) -> List[Dict[str, Any]]:
        """Return Toptal skill category links."""
        return [
            {
                'title': f"Toptal: {name}",
                'url': f'https://www.toptal.com/{slug}',
                'link': f'https://www.toptal.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug.split('/')[0] if '/' in slug else slug,
                'source': 'Toptal',
                'data_type': 'freelance_category',
                'platform': 'toptal',
                'tags': ['freelance', 'toptal', 'elite', slug.split('/')[0]],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SKILL_CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Elite Software Developers', 'developers', 'Top 3% of software engineering talent.'),
            ('Expert Designers', 'designers', 'Top 3% of design professionals.'),
            ('Finance Experts', 'finance', 'Top 3% of finance talent.'),
            ('Project Managers', 'project-managers', 'Top 3% of project management.'),
            ('Tech Insights Blog', 'blog', 'Technical articles and industry insights.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.toptal.com/{category}',
                'link': f'https://www.toptal.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Toptal',
                'data_type': 'freelance_topic',
                'platform': 'toptal',
                'tags': ['freelance', 'toptal', 'elite', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
