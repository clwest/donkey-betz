"""
Midjourney Spider - AI Art & Prompt Intelligence
==================================================

Session 534: Simplified to work with spider network interface.
Aggregates AI art and generative AI content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MidjourneySpider:
    """Midjourney spider - AI art and prompt intelligence"""

    name = "midjourney"

    # AI art and generative AI RSS feeds
    RSS_FEEDS = {
        'ai_art_news': 'https://80.lv/feed/',
        'creative_ai': 'https://www.unite.ai/feed/',
        'digital_arts': 'https://www.digitalartsonline.co.uk/rss/',
        'the_verge_ai': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
        'ars_technica_ai': 'https://feeds.arstechnica.com/arstechnica/technology-lab',
    }

    # AI art categories
    CATEGORIES = [
        ('Midjourney', 'midjourney', 'Midjourney AI art generation.'),
        ('Stable Diffusion', 'stable_diffusion', 'Stable Diffusion models.'),
        ('DALL-E', 'dalle', 'OpenAI DALL-E image generation.'),
        ('Prompts', 'prompts', 'AI art prompts and techniques.'),
        ('Tutorials', 'tutorials', 'AI art tutorials and guides.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.art_styles = {
            'photorealistic': ['photorealistic', 'realistic', 'hyperreal', 'lifelike', 'photograph'],
            'fantasy': ['fantasy', 'magical', 'mythical', 'ethereal', 'enchanted'],
            'scifi': ['sci-fi', 'futuristic', 'cyberpunk', 'space', 'dystopian'],
            'anime': ['anime', 'manga', 'japanese', 'chibi', 'kawaii'],
            'abstract': ['abstract', 'surreal', 'conceptual', 'experimental'],
            'painterly': ['painting', 'oil', 'watercolor', 'impressionist', 'brushwork'],
        }
        self.ai_art_keywords = ['ai', 'midjourney', 'stable diffusion', 'dall-e', 'generative',
                                'prompt', 'image generation', 'text to image', 'ai art']

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch AI art and generative AI content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of AI art content dictionaries
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
            logger.warning(f"Error getting AI art categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Midjourney spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from AI art RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect art style and AI relevance
                text = f"{title} {summary}".lower()
                art_style = self._detect_art_style(text)
                is_ai_art = self._is_ai_art_relevant(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'art_style': art_style,
                    'category': art_style,
                    'is_ai_art_relevant': is_ai_art,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'ai_art',
                    'platform': 'midjourney',
                    'tags': ['midjourney', 'ai_art', art_style],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_art_style(self, text: str) -> str:
        """Detect art style from text."""
        for style, keywords in self.art_styles.items():
            if any(kw in text for kw in keywords):
                return style
        return 'general'

    def _is_ai_art_relevant(self, text: str) -> bool:
        """Check if content is AI art relevant."""
        return any(kw in text for kw in self.ai_art_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return AI art category links."""
        return [
            {
                'title': f"AI Art: {name}",
                'url': f'https://www.midjourney.com/explore?tab={slug}',
                'link': f'https://www.midjourney.com/explore?tab={slug}',
                'summary': desc,
                'description': desc,
                'art_style': slug,
                'category': slug,
                'source': 'Midjourney',
                'data_type': 'ai_art_category',
                'platform': 'midjourney',
                'tags': ['midjourney', 'ai_art', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Midjourney Prompts', 'prompts', 'AI art prompt engineering.'),
            ('Stable Diffusion', 'stable_diffusion', 'Open source image generation.'),
            ('DALL-E Art', 'dalle', 'OpenAI image generation.'),
            ('AI Art Styles', 'styles', 'Art style exploration.'),
            ('Generative AI', 'generative', 'Latest in generative AI.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.reddit.com/r/midjourney/search?q={category}',
                'link': f'https://www.reddit.com/r/midjourney/search?q={category}',
                'summary': desc,
                'description': desc,
                'art_style': category,
                'category': category,
                'source': 'Midjourney',
                'data_type': 'ai_art_topic',
                'platform': 'midjourney',
                'tags': ['midjourney', 'ai_art', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
