"""
PeoplePerHour Spider - UK Freelance Platform Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates UK/European freelance opportunities via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PeoplePerHourSpider:
    """PeoplePerHour spider - UK and European freelance market opportunities"""

    name = "peopleperhour"

    # Freelance job RSS feeds (UK-focused)
    RSS_FEEDS = {
        'freelancer_uk': 'https://www.freelancer.co.uk/rss.xml',
        'upwork_blog': 'https://www.upwork.com/blog/feed/',
        'remote_co': 'https://remote.co/remote-jobs/feed/',
        'workingnotworking': 'https://workingnotworking.com/feed',
        'creative_pool': 'https://creativepool.com/rss/jobs',
    }

    # Freelance categories
    CATEGORIES = [
        ('Technology', 'technology', 'Development and tech projects.'),
        ('Design', 'design', 'Graphic and web design.'),
        ('Writing', 'writing', 'Content and copywriting.'),
        ('Marketing', 'marketing', 'Digital marketing and SEO.'),
        ('Business', 'business', 'Business consulting and admin.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.service_categories = {
            'technology': ['developer', 'programmer', 'software', 'web', 'app', 'api', 'database'],
            'design': ['design', 'graphic', 'ui', 'ux', 'logo', 'branding', 'illustration'],
            'writing': ['writer', 'content', 'copywriter', 'blog', 'article', 'editor'],
            'marketing': ['marketing', 'seo', 'social media', 'ads', 'ppc', 'email'],
            'business': ['admin', 'virtual assistant', 'data entry', 'bookkeeping', 'consulting'],
            'video': ['video', 'animation', 'motion', 'editor', 'youtube'],
            'translation': ['translation', 'translator', 'language', 'localization'],
        }
        self.supported_currencies = ['£', '€', '$', 'GBP', 'EUR', 'USD']

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch freelance opportunities from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of freelance opportunity dictionaries
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
            logger.warning(f"Error getting freelance categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"PeoplePerHour spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch freelance opportunities from RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect service category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                budget = self._extract_budget(text)
                is_remote = self._check_remote(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'budget': budget,
                    'currency': self._detect_currency(text),
                    'is_remote': is_remote,
                    'region': 'uk_europe',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'freelance_opportunity',
                    'platform': 'peopleperhour',
                    'tags': ['freelance', 'uk', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect service category from text."""
        for category, keywords in self.service_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _extract_budget(self, text: str) -> str:
        """Extract budget from text."""
        budget_patterns = [
            r'[£€$][\d,]+(?:\s*-\s*[£€$]?[\d,]+)?',
            r'[\d,]+\s*(?:GBP|EUR|USD)',
            r'(?:budget|rate)[:.]?\s*[£€$]?[\d,]+',
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return ''

    def _detect_currency(self, text: str) -> str:
        """Detect currency from text."""
        if '£' in text or 'GBP' in text.upper():
            return 'GBP'
        elif '€' in text or 'EUR' in text.upper():
            return 'EUR'
        elif '$' in text or 'USD' in text.upper():
            return 'USD'
        return 'GBP'  # Default for UK platform

    def _check_remote(self, text: str) -> bool:
        """Check if remote work is available."""
        remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere', 'distributed']
        return any(kw in text for kw in remote_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return freelance category links."""
        return [
            {
                'title': f"PPH: {name}",
                'url': f'https://www.peopleperhour.com/hire-freelancers/{slug}',
                'link': f'https://www.peopleperhour.com/hire-freelancers/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'PeoplePerHour',
                'data_type': 'freelance_category',
                'platform': 'peopleperhour',
                'tags': ['freelance', 'uk', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Web Development', 'technology', 'Web and app development projects.'),
            ('Graphic Design', 'design', 'Logo, branding, and design work.'),
            ('Content Writing', 'writing', 'Blog posts and copywriting.'),
            ('Digital Marketing', 'marketing', 'SEO and social media marketing.'),
            ('Virtual Assistant', 'business', 'Admin and business support.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.peopleperhour.com/hire-freelancers/{category}',
                'link': f'https://www.peopleperhour.com/hire-freelancers/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'PeoplePerHour',
                'data_type': 'freelance_topic',
                'platform': 'peopleperhour',
                'tags': ['freelance', 'uk', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
