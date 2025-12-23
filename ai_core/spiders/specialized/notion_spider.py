"""
Notion Spider - Templates & Productivity Tools Intelligence
==============================================================

Session 534: Simplified to work with spider network interface.
Aggregates productivity and workspace content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NotionSpider:
    """Notion spider - templates and productivity tools intelligence"""

    name = "notion"

    # Productivity and workspace RSS feeds
    RSS_FEEDS = {
        'notion_blog': 'https://www.notion.so/blog/rss',
        'productivity_tips': 'https://www.makeuseof.com/feed/',
        'zapier_blog': 'https://zapier.com/blog/feed/',
        'todoist_blog': 'https://blog.todoist.com/feed/',
        'asana_blog': 'https://blog.asana.com/feed/',
    }

    # Productivity categories
    CATEGORIES = [
        ('Project Management', 'project', 'Project and task management.'),
        ('Personal', 'personal', 'Personal productivity and habits.'),
        ('Business', 'business', 'Business workflows and CRM.'),
        ('Content', 'content', 'Content planning and calendars.'),
        ('Education', 'education', 'Learning and note-taking.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.template_types = {
            'project_management': ['project', 'task', 'kanban', 'roadmap', 'sprint', 'agile'],
            'personal': ['journal', 'habit', 'goal', 'life', 'personal', 'tracker'],
            'business': ['crm', 'sales', 'invoice', 'client', 'business', 'meeting'],
            'content': ['content', 'calendar', 'editorial', 'blog', 'social', 'marketing'],
            'education': ['student', 'notes', 'course', 'study', 'research', 'learning'],
            'finance': ['budget', 'finance', 'expense', 'investment', 'tracker'],
        }
        self.productivity_keywords = ['notion', 'template', 'productivity', 'workspace', 'database',
                                      'organize', 'workflow', 'second brain', 'pkm', 'automation']

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch productivity and workspace content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of productivity content dictionaries
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
            logger.warning(f"Error getting productivity categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Notion spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from productivity RSS feed."""
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

                # Detect template type and relevance
                text = f"{title} {summary}".lower()
                template_type = self._detect_template_type(text)
                is_notion_relevant = self._is_productivity_relevant(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'template_type': template_type,
                    'category': template_type,
                    'is_notion_relevant': is_notion_relevant,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'productivity_tools',
                    'platform': 'notion',
                    'tags': ['notion', 'productivity', template_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_template_type(self, text: str) -> str:
        """Detect template type from text."""
        for ttype, keywords in self.template_types.items():
            if any(kw in text for kw in keywords):
                return ttype
        return 'general'

    def _is_productivity_relevant(self, text: str) -> bool:
        """Check if content is productivity-relevant."""
        return any(kw in text for kw in self.productivity_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return productivity category links."""
        return [
            {
                'title': f"Notion: {name}",
                'url': f'https://www.notion.so/templates/{slug}',
                'link': f'https://www.notion.so/templates/{slug}',
                'summary': desc,
                'description': desc,
                'template_type': slug,
                'category': slug,
                'source': 'Notion',
                'data_type': 'productivity_category',
                'platform': 'notion',
                'tags': ['notion', 'productivity', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Project Templates', 'project', 'Project management templates.'),
            ('Personal Productivity', 'personal', 'Personal organization tools.'),
            ('Business Templates', 'business', 'Business workflow templates.'),
            ('Content Planning', 'content', 'Content calendar and planning.'),
            ('Student Templates', 'education', 'Learning and note templates.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.notion.so/templates/{category}',
                'link': f'https://www.notion.so/templates/{category}',
                'summary': desc,
                'description': desc,
                'template_type': category,
                'category': category,
                'source': 'Notion',
                'data_type': 'productivity_topic',
                'platform': 'notion',
                'tags': ['notion', 'productivity', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
