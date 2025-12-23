"""
Tech Community Spider - Developer & Tech Community Intelligence
================================================================

Session 534: Simplified to work with spider network interface.
Aggregates developer community news and trends via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TechCommunitySpider:
    """Tech community spider - developer forums, tech news, and community trends"""

    name = "tech_community"

    # Developer and tech community RSS feeds
    RSS_FEEDS = {
        'dev_to': 'https://dev.to/feed',
        'hashnode': 'https://hashnode.com/feed',
        'freecodecamp': 'https://www.freecodecamp.org/news/rss/',
        'lobsters': 'https://lobste.rs/rss',
        'slashdot': 'https://rss.slashdot.org/Slashdot/slashdotMain',
    }

    # Tech community categories
    CATEGORIES = [
        ('Web Development', 'webdev', 'Frontend and backend web development.'),
        ('DevOps', 'devops', 'CI/CD, containers, and infrastructure.'),
        ('Data Science', 'datascience', 'ML, AI, and data engineering.'),
        ('Mobile', 'mobile', 'iOS, Android, and cross-platform.'),
        ('Career', 'career', 'Developer career and job advice.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.tech_topics = {
            'webdev': ['javascript', 'react', 'vue', 'node', 'css', 'html', 'frontend', 'backend', 'fullstack'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'aws', 'cloud', 'terraform', 'devops', 'infrastructure'],
            'datascience': ['python', 'machine learning', 'ai', 'data', 'ml', 'neural', 'tensorflow', 'pytorch'],
            'mobile': ['ios', 'android', 'swift', 'kotlin', 'react native', 'flutter', 'mobile'],
            'career': ['career', 'job', 'interview', 'salary', 'remote', 'freelance', 'hiring'],
            'security': ['security', 'cybersecurity', 'hacking', 'vulnerability', 'encryption'],
        }
        self.content_types = {
            'tutorial': ['tutorial', 'how to', 'guide', 'learn', 'step by step'],
            'news': ['release', 'launch', 'announce', 'update', 'new'],
            'discussion': ['opinion', 'thoughts', 'debate', 'why', 'should'],
            'showcase': ['built', 'created', 'project', 'portfolio', 'show'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch tech community content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of tech community content dictionaries
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

        logger.info(f"Tech community spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch tech community content from RSS feed."""
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

                # Analysis
                text = f"{title} {description}".lower()
                topic = self._detect_topic(text)
                content_type = self._detect_content_type(text)
                engagement = self._estimate_engagement(entry)
                sentiment = self._analyze_sentiment(text)

                # Extract tags from entry if available
                tags = []
                if hasattr(entry, 'tags') and entry.tags:
                    tags = [tag.term for tag in entry.tags[:5]]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'topic': topic,
                    'category': topic,
                    'content_type': content_type,
                    'engagement': engagement,
                    'sentiment': sentiment,
                    'entry_tags': tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'tech_community',
                    'platform': 'tech_community',
                    'tags': ['tech', 'developer', 'community', topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_topic(self, text: str) -> str:
        """Detect tech topic from text."""
        for topic, keywords in self.tech_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        for ctype, keywords in self.content_types.items():
            if any(kw in text for kw in keywords):
                return ctype
        return 'article'

    def _estimate_engagement(self, entry: Any) -> str:
        """Estimate engagement level from entry metadata."""
        # Simple heuristic based on available metadata
        if hasattr(entry, 'slash_comments'):
            comments = int(entry.slash_comments) if entry.slash_comments else 0
            if comments > 50:
                return 'high'
            elif comments > 10:
                return 'medium'
        return 'normal'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['awesome', 'amazing', 'love', 'great', 'best', 'powerful', 'useful']
        negative = ['bad', 'problem', 'issue', 'hate', 'worst', 'deprecated', 'avoid']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return tech community category links."""
        return [
            {
                'title': f"Tech: {name}",
                'url': f'https://dev.to/t/{slug}',
                'link': f'https://dev.to/t/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'topic': slug,
                'source': 'Dev.to',
                'data_type': 'tech_category',
                'platform': 'tech_community',
                'tags': ['tech', 'developer', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Web Development Trends', 'webdev', 'Frontend and backend trends.'),
            ('DevOps Best Practices', 'devops', 'CI/CD and infrastructure.'),
            ('AI & Machine Learning', 'datascience', 'ML and data science.'),
            ('Developer Career Tips', 'career', 'Job hunting and career growth.'),
            ('Open Source Projects', 'opensource', 'Community projects and contributions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://dev.to/t/{category}',
                'link': f'https://dev.to/t/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'topic': category,
                'source': 'Dev.to',
                'data_type': 'tech_topic',
                'platform': 'tech_community',
                'tags': ['tech', 'developer', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
