"""
RunwayML Spider - AI Video & Creative Tools Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates AI video generation and creative tools news via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RunwayMLSpider:
    """RunwayML spider - AI video and creative tools intelligence"""

    name = "runwayml"

    # AI video and creative tools RSS feeds
    RSS_FEEDS = {
        'runway_blog': 'https://runwayml.com/blog/rss.xml',
        'venturebeat_ai': 'https://venturebeat.com/category/ai/feed/',
        'the_verge_ai': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
        'techcrunch_ai': 'https://techcrunch.com/category/artificial-intelligence/feed/',
        'wired_ai': 'https://www.wired.com/feed/tag/ai/latest/rss',
    }

    # AI video categories
    CATEGORIES = [
        ('Video Generation', 'video-gen', 'Text to video and video AI.'),
        ('Image Generation', 'image-gen', 'AI image creation tools.'),
        ('Motion & Animation', 'motion', 'Motion design and animation AI.'),
        ('Audio & Music', 'audio', 'AI audio and music generation.'),
        ('Creative Tools', 'creative', 'AI-powered creative workflows.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.creative_tools = {
            'video_gen': ['video generation', 'gen-2', 'gen-3', 'text to video', 'sora', 'pika', 'kling'],
            'image_gen': ['image generation', 'stable diffusion', 'dall-e', 'midjourney', 'flux'],
            'motion': ['motion', 'animation', 'motion brush', 'camera control', 'animate'],
            'audio': ['audio', 'music generation', 'suno', 'udio', 'voice', 'tts'],
            'editing': ['editing', 'inpainting', 'outpainting', 'remove background', 'upscale'],
        }
        self.use_cases = {
            'filmmaking': ['film', 'movie', 'cinema', 'director', 'cinematography', 'vfx'],
            'advertising': ['ad', 'commercial', 'marketing', 'brand', 'campaign'],
            'social': ['social', 'tiktok', 'reels', 'shorts', 'content creator', 'influencer'],
            'music': ['music video', 'visualizer', 'artist', 'album'],
            'gaming': ['game', 'gaming', 'trailer', 'cutscene'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch AI video and creative tools news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of AI creative news dictionaries
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
            logger.warning(f"Error getting AI video categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"RunwayML spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch AI video/creative news from RSS feed."""
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

                # Check relevance to AI video/creative
                if not self._is_ai_creative_relevant(text):
                    continue

                tool_type = self._detect_tool_type(text)
                use_case = self._detect_use_case(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'tool_type': tool_type,
                    'use_case': use_case,
                    'category': tool_type,
                    'sentiment': sentiment,
                    'is_ai_video': 'video' in tool_type,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'ai_creative_news',
                    'platform': 'runwayml',
                    'tags': ['ai', 'creative', tool_type, use_case],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _is_ai_creative_relevant(self, text: str) -> bool:
        """Check if content is relevant to AI creative tools."""
        relevance_keywords = [
            'runway', 'gen-2', 'gen-3', 'sora', 'pika', 'kling',
            'video generation', 'text to video', 'ai video',
            'stable diffusion', 'midjourney', 'dall-e', 'flux',
            'creative ai', 'generative ai', 'ai art', 'ai image',
            'motion', 'animation ai', 'music ai', 'suno', 'udio'
        ]
        return any(kw in text for kw in relevance_keywords)

    def _detect_tool_type(self, text: str) -> str:
        """Detect creative tool type from text."""
        for tool_type, keywords in self.creative_tools.items():
            if any(kw in text for kw in keywords):
                return tool_type
        return 'general'

    def _detect_use_case(self, text: str) -> str:
        """Detect use case from text."""
        for use_case, keywords in self.use_cases.items():
            if any(kw in text for kw in keywords):
                return use_case
        return 'general'

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze article sentiment."""
        positive = ['amazing', 'breakthrough', 'revolutionary', 'impressive', 'best', 'stunning']
        negative = ['disappointing', 'failed', 'concern', 'problem', 'controversy', 'lawsuit']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return AI video category links."""
        return [
            {
                'title': f"AI Creative: {name}",
                'url': f'https://runwayml.com/{slug}',
                'link': f'https://runwayml.com/{slug}',
                'summary': desc,
                'description': desc,
                'tool_type': slug,
                'category': slug,
                'source': 'RunwayML',
                'data_type': 'ai_creative_category',
                'platform': 'runwayml',
                'tags': ['ai', 'creative', 'runwayml', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Gen-3 Alpha', 'video_gen', 'Runway Gen-3 video generation.'),
            ('Sora & Competitors', 'video_gen', 'OpenAI Sora and alternatives.'),
            ('Stable Diffusion', 'image_gen', 'Latest SD models and techniques.'),
            ('AI Music', 'audio', 'Suno, Udio, and music AI.'),
            ('Motion Design AI', 'motion', 'AI-powered motion and animation.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://runwayml.com/ai-tools/{category}',
                'link': f'https://runwayml.com/ai-tools/{category}',
                'summary': desc,
                'description': desc,
                'tool_type': category,
                'category': category,
                'source': 'RunwayML',
                'data_type': 'ai_creative_topic',
                'platform': 'runwayml',
                'tags': ['ai', 'creative', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
