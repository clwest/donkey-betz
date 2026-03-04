"""
GitHub Spider - Developer Trends & Open Source Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
Uses GitHub API for trending repos and developer trends.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class GitHubSpider:
    """GitHub spider - trending repos, topics, and developer activity"""

    name = "github"

    BASE_URL = "https://api.github.com"

    # Fallback RSS feeds for developer news
    RSS_FEEDS = {
        'github_blog': 'https://github.blog/feed/',
        'hackernews': 'https://news.ycombinator.com/rss',
        'lobsters': 'https://lobste.rs/rss',
    }

    # Topics of interest
    TOPICS = [
        ('Artificial Intelligence', 'artificial-intelligence', 'AI and machine learning projects.'),
        ('Machine Learning', 'machine-learning', 'ML libraries and frameworks.'),
        ('LLM', 'llm', 'Large language model projects.'),
        ('Python', 'python', 'Python libraries and tools.'),
        ('TypeScript', 'typescript', 'TypeScript projects.'),
        ('Rust', 'rust', 'Rust programming projects.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.token = os.getenv('GITHUB_TOKEN', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch trending GitHub repos and developer content.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of repo/content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try GitHub API if token is available
        if self.token:
            try:
                api_items = self._fetch_from_github_api()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from GitHub API: {e}")

        # Fetch from fallback RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add topic links
        try:
            topics = self._get_topic_links()
            all_items.extend(topics)
        except Exception as e:
            logger.warning(f"Error getting GitHub topics: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"GitHub spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_github_api(self) -> List[Dict[str, Any]]:
        """Fetch trending repos from GitHub API."""
        items = []

        try:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {self.token}',
                'User-Agent': 'DonkeyBetz-Spider/1.0'
            }

            # Search for trending repos
            search_queries = [
                'stars:>1000 pushed:>2024-01-01',
                'topic:ai stars:>100',
            ]

            for query in search_queries[:2]:
                try:
                    response = cached_get(
                        f"{self.BASE_URL}/search/repositories",
                        headers=headers,
                        params={
                            'q': query,
                            'sort': 'stars',
                            'order': 'desc',
                            'per_page': 15
                        },
                        timeout=15
                    )

                    if response.status_code == 200:
                        data = response.json()
                        repos = data.get('items', [])

                        for repo in repos:
                            language = repo.get('language', 'Unknown') or 'Unknown'
                            stars = repo.get('stargazers_count', 0)

                            items.append({
                                'title': f"{repo.get('full_name', '')} ⭐ {stars:,}",
                                'url': repo.get('html_url', ''),
                                'link': repo.get('html_url', ''),
                                'summary': repo.get('description', '') or 'No description',
                                'description': repo.get('description', '') or 'No description',
                                'stars': stars,
                                'forks': repo.get('forks_count', 0),
                                'language': language,
                                'topics': repo.get('topics', []),
                                'author': repo.get('owner', {}).get('login', ''),
                                'category': self._detect_category(language, repo.get('topics', [])),
                                'source': 'GitHub',
                                'data_type': 'github_repo',
                                'platform': 'github',
                                'tags': ['github', 'opensource', language.lower()] + repo.get('topics', [])[:3],
                                'timestamp': datetime.now().isoformat(),
                            })

                    elif response.status_code == 403:
                        logger.warning("GitHub rate limit hit")
                        break

                except Exception as e:
                    logger.warning(f"Error searching GitHub: {e}")

        except Exception as e:
            logger.warning(f"Error with GitHub API: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch developer content from RSS feed."""
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

                # Detect category from content
                text = f"{title} {summary}".lower()
                category = self._detect_topic(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'developer_content',
                    'platform': 'github',
                    'tags': ['developer', 'opensource', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, language: str, topics: List[str]) -> str:
        """Detect repo category from language and topics."""
        lang_lower = language.lower()
        topics_str = ' '.join(topics).lower()

        if 'ai' in topics_str or 'machine-learning' in topics_str or 'llm' in topics_str:
            return 'ai_ml'
        elif lang_lower in ['python', 'jupyter notebook']:
            return 'python'
        elif lang_lower in ['javascript', 'typescript']:
            return 'javascript'
        elif lang_lower == 'rust':
            return 'rust'
        elif lang_lower == 'go':
            return 'golang'
        return 'general'

    def _detect_topic(self, text: str) -> str:
        """Detect topic from text."""
        topics = {
            'ai_ml': ['ai', 'machine learning', 'llm', 'gpt', 'neural'],
            'python': ['python', 'django', 'flask', 'pandas'],
            'javascript': ['javascript', 'react', 'vue', 'node', 'typescript'],
            'rust': ['rust', 'cargo'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'devops'],
        }

        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return GitHub topic exploration links."""
        return [
            {
                'title': f"GitHub: {name}",
                'url': f'https://github.com/topics/{slug}',
                'link': f'https://github.com/topics/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'GitHub',
                'data_type': 'github_topic',
                'platform': 'github',
                'tags': ['github', 'topic', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Trending Repos', 'trending', 'Popular repositories this week.'),
            ('AI Projects', 'artificial-intelligence', 'AI and machine learning.'),
            ('Python Libraries', 'python', 'Python projects and tools.'),
            ('Web Development', 'web', 'Frontend and backend projects.'),
            ('Open Source', 'opensource', 'Open source contributions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://github.com/topics/{category}',
                'link': f'https://github.com/topics/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'GitHub',
                'data_type': 'github_topic',
                'platform': 'github',
                'tags': ['github', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
