"""
Replicate Spider - AI Model API Intelligence
=============================================

Session 534: Simplified to work with spider network interface.
Uses Replicate API to fetch trending AI models and ML news RSS.
"""

import requests
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ReplicateSpider:
    """Replicate spider - AI model marketplace and API trends"""

    name = "replicate"

    # ML/AI RSS feeds
    RSS_FEEDS = {
        'replicate_blog': 'https://replicate.com/blog/rss.xml',
        'ml_mastery': 'https://machinelearningmastery.com/feed/',
    }

    # Replicate API for trending models
    API_URL = "https://replicate.com/api/models"

    # Model categories
    MODEL_CATEGORIES = [
        ('Text to Image', 'text-to-image', 'Generate images from text prompts.'),
        ('Image to Image', 'image-to-image', 'Transform and edit images.'),
        ('Text to Speech', 'text-to-speech', 'Generate speech from text.'),
        ('Speech to Text', 'speech-to-text', 'Transcribe audio to text.'),
        ('Text to Video', 'text-to-video', 'Generate videos from prompts.'),
        ('Image Upscaling', 'image-upscaling', 'Upscale and enhance images.'),
        ('Object Detection', 'object-detection', 'Detect objects in images.'),
        ('Background Removal', 'background-removal', 'Remove image backgrounds.'),
        ('Language Models', 'language-models', 'Large language models and chatbots.'),
        ('Audio Generation', 'audio-generation', 'Generate music and audio.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch AI models and ML news.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of model and article dictionaries
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

        # Add model category links
        try:
            categories = self._get_model_categories()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting model categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Replicate spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch ML articles from RSS feed."""
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

                # Detect model category
                category = self._detect_category(f"{title} {description}".lower())

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'ml_article',
                    'platform': 'replicate',
                    'tags': ['ai', 'ml', 'models', 'api', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect model category from text."""
        categories = {
            'image-gen': ['stable diffusion', 'dall-e', 'midjourney', 'image generation', 'text to image'],
            'llm': ['llm', 'language model', 'gpt', 'llama', 'claude', 'chat'],
            'audio': ['audio', 'music', 'speech', 'voice', 'tts'],
            'video': ['video', 'animation', 'motion'],
            'vision': ['vision', 'detection', 'segmentation', 'recognition'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'general'

    def _get_model_categories(self) -> List[Dict[str, Any]]:
        """Return Replicate model category links."""
        return [
            {
                'title': f"Replicate: {name}",
                'url': f'https://replicate.com/collections/{slug}',
                'link': f'https://replicate.com/collections/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Replicate',
                'data_type': 'ai_model_category',
                'platform': 'replicate',
                'tags': ['ai', 'ml', 'api', 'replicate', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.MODEL_CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Image Generation Models', 'image-gen', 'Stable Diffusion, FLUX, and image generators.'),
            ('Language Models', 'llm', 'LLMs for text generation and chat.'),
            ('Audio Models', 'audio', 'Text-to-speech and audio generation.'),
            ('Video Models', 'video', 'Video generation and editing models.'),
            ('Vision Models', 'vision', 'Object detection and image understanding.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://replicate.com/explore?category={category}',
                'link': f'https://replicate.com/explore?category={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Replicate',
                'data_type': 'ai_topic',
                'platform': 'replicate',
                'tags': ['ai', 'ml', 'replicate', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
