"""
Kaggle Spider - ML Competition & Dataset Intelligence
======================================================

Session 534: Simplified to work with spider network interface.
Uses Kaggle API when credentials available, RSS fallback otherwise.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import base64
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class KaggleSpider:
    """Kaggle spider - ML competitions, datasets, and notebooks"""

    name = "kaggle"

    BASE_URL = "https://www.kaggle.com/api/v1"

    # Fallback ML/Data Science RSS feeds
    RSS_FEEDS = {
        'towards_data_science': 'https://towardsdatascience.com/feed',
        'kdnuggets': 'https://www.kdnuggets.com/feed',
        'analytics_vidhya': 'https://www.analyticsvidhya.com/feed/',
    }

    # ML categories
    CATEGORIES = [
        ('Competitions', 'competitions', 'ML competitions with prizes.'),
        ('Datasets', 'datasets', 'Public datasets for ML.'),
        ('Notebooks', 'notebooks', 'Code notebooks and kernels.'),
        ('Discussions', 'discussions', 'Community discussions.'),
        ('Learn', 'learn', 'ML courses and tutorials.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.kaggle_username = os.getenv('KAGGLE_USERNAME', '')
        # Support multiple env var names for API key
        self.kaggle_key = os.getenv('KAGGLE_API_TOKEN', os.getenv('KAGGLE_API_KEY', os.getenv('KAGGLE_KEY', '')))

    def _get_auth_header(self) -> Dict[str, str]:
        """Generate auth header for Kaggle API."""
        if self.kaggle_key:
            if self.kaggle_key.startswith('KGAT_'):
                return {'Authorization': f'Bearer {self.kaggle_key}'}
            elif self.kaggle_username:
                credentials = f"{self.kaggle_username}:{self.kaggle_key}"
                encoded = base64.b64encode(credentials.encode()).decode()
                return {'Authorization': f'Basic {encoded}'}
        return {}

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch ML content from Kaggle API and fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of ML content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try Kaggle API if credentials available
        headers = self._get_auth_header()
        if headers:
            try:
                api_items = self._fetch_from_kaggle_api(headers)
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from Kaggle API: {e}")

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

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Kaggle categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Kaggle spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_kaggle_api(self, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch data from Kaggle API."""
        items = []

        # Fetch competitions
        try:
            response = cached_get(
                f"{self.BASE_URL}/competitions/list",
                headers=headers,
                params={'sortBy': 'recentlyCreated', 'page': 1, 'pageSize': 15},
                timeout=15
            )

            if response.status_code == 200:
                competitions = response.json()
                for comp in competitions[:10]:
                    # Session 767: Handle ref that might be full URL or just slug
                    ref = comp.get('ref', '')
                    if ref.startswith('http'):
                        comp_url = ref
                    elif '/' in ref:
                        # ref like "competitions/name" - just use as path
                        comp_url = f"https://www.kaggle.com/{ref}"
                    else:
                        comp_url = f"https://www.kaggle.com/c/{ref}"
                    items.append({
                        'title': comp.get('title', 'Kaggle Competition'),
                        'url': comp_url,
                        'link': comp_url,
                        'summary': comp.get('description', '')[:300] if comp.get('description') else '',
                        'description': comp.get('description', '')[:300] if comp.get('description') else '',
                        'reward': comp.get('reward', ''),
                        'deadline': comp.get('deadline', ''),
                        'teams_count': comp.get('teamCount', 0),
                        'category': 'competition',
                        'ml_category': comp.get('category', ''),
                        'source': 'Kaggle',
                        'data_type': 'ml_competition',
                        'platform': 'kaggle',
                        'tags': ['kaggle', 'competition', 'ml'],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching Kaggle competitions: {e}")

        # Fetch trending datasets
        try:
            response = cached_get(
                f"{self.BASE_URL}/datasets/list",
                headers=headers,
                params={'sortBy': 'hottest', 'page': 1, 'pageSize': 15},
                timeout=15
            )

            if response.status_code == 200:
                datasets = response.json()
                for ds in datasets[:10]:
                    # Session 767: Handle ref that might be full URL or just slug
                    ref = ds.get('ref', '')
                    if ref.startswith('http'):
                        ds_url = ref
                    elif '/' in ref and not ref.startswith('datasets/'):
                        # ref like "owner/dataset-name"
                        ds_url = f"https://www.kaggle.com/datasets/{ref}"
                    elif ref.startswith('datasets/'):
                        ds_url = f"https://www.kaggle.com/{ref}"
                    else:
                        ds_url = f"https://www.kaggle.com/datasets/{ref}"
                    items.append({
                        'title': ds.get('title', 'Kaggle Dataset'),
                        'url': ds_url,
                        'link': ds_url,
                        'summary': ds.get('subtitle', '')[:300] if ds.get('subtitle') else '',
                        'description': ds.get('subtitle', '')[:300] if ds.get('subtitle') else '',
                        'downloads': ds.get('downloadCount', 0),
                        'votes': ds.get('voteCount', 0),
                        'usability': ds.get('usabilityRating', 0),
                        'owner': ds.get('ownerName', ''),
                        'category': 'dataset',
                        'source': 'Kaggle',
                        'data_type': 'ml_dataset',
                        'platform': 'kaggle',
                        'tags': ['kaggle', 'dataset', 'ml'],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching Kaggle datasets: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch ML content from RSS feed."""
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

                # Detect ML topic
                text = f"{title} {summary}".lower()
                ml_topic = self._detect_ml_topic(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Data Scientist'),
                    'ml_topic': ml_topic,
                    'category': ml_topic,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'ml_content',
                    'platform': 'kaggle',
                    'tags': ['ml', 'data_science', ml_topic],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_ml_topic(self, text: str) -> str:
        """Detect ML topic from text."""
        ml_topics = {
            'nlp': ['nlp', 'natural language', 'text', 'bert', 'transformer', 'llm'],
            'computer_vision': ['vision', 'image', 'cnn', 'detection', 'segmentation'],
            'tabular': ['tabular', 'xgboost', 'lightgbm', 'regression', 'classification'],
            'deep_learning': ['deep learning', 'neural network', 'pytorch', 'tensorflow'],
            'time_series': ['time series', 'forecasting', 'lstm', 'arima'],
            'reinforcement': ['reinforcement', 'rl', 'agent', 'reward'],
        }

        for topic, keywords in ml_topics.items():
            if any(kw in text for kw in keywords):
                return topic
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Kaggle category links."""
        return [
            {
                'title': f"Kaggle: {name}",
                'url': f'https://www.kaggle.com/{slug}',
                'link': f'https://www.kaggle.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Kaggle',
                'data_type': 'kaggle_category',
                'platform': 'kaggle',
                'tags': ['kaggle', 'ml', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('ML Competitions', 'competitions', 'Active ML competitions with prizes.'),
            ('Trending Datasets', 'datasets', 'Popular public datasets.'),
            ('Top Notebooks', 'notebooks', 'Highly-voted code notebooks.'),
            ('ML Courses', 'learn', 'Free ML courses and tutorials.'),
            ('Discussions', 'discussions', 'Community Q&A and discussions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.kaggle.com/{category}',
                'link': f'https://www.kaggle.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Kaggle',
                'data_type': 'kaggle_topic',
                'platform': 'kaggle',
                'tags': ['kaggle', 'ml', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
