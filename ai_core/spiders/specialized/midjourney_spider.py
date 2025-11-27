"""
Midjourney Spider - AI Art & Prompt Intelligence
==================================================

Session 218: Specialized spider for Midjourney AI art community.
Focuses on AI art trends, prompts, techniques, and creative workflows.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class MidjourneySpider(BaseIntelligenceSpider):
    """Midjourney spider - AI art and prompt intelligence"""

    RSS_FEEDS = {
        'ai_art_news': 'https://80.lv/feed/',
        'creative_ai': 'https://www.unite.ai/feed/',
        'digital_arts': 'https://www.digitalartsonline.co.uk/rss/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.art_styles = {
            'photorealistic': ['photorealistic', 'realistic', 'hyperreal', 'lifelike', 'photograph'],
            'fantasy': ['fantasy', 'magical', 'mythical', 'ethereal', 'enchanted'],
            'scifi': ['sci-fi', 'futuristic', 'cyberpunk', 'space', 'dystopian'],
            'anime': ['anime', 'manga', 'japanese', 'chibi', 'kawaii'],
            'abstract': ['abstract', 'surreal', 'conceptual', 'experimental'],
            'painterly': ['painting', 'oil', 'watercolor', 'impressionist', 'brushwork'],
        }

        self.prompt_techniques = {
            'style_reference': ['style of', 'in the style', 'inspired by', 'like'],
            'quality_modifiers': ['4k', '8k', 'detailed', 'high quality', 'masterpiece'],
            'lighting': ['lighting', 'dramatic light', 'golden hour', 'volumetric'],
            'composition': ['composition', 'rule of thirds', 'cinematic', 'wide angle'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Midjourney community data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            item = {
                                'title': entry.get('title', ''),
                                'description': entry.get('summary', entry.get('description', ''))[:500],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': feed_name,
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'midjourney'}

        except Exception as e:
            self.logger.error(f"Error fetching Midjourney data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Midjourney community data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for AI art relevant content
            ai_art_items = [i for i in processed_items if i.get('is_ai_art_relevant')]

            insights = self._generate_insights(ai_art_items)

            content = {
                'items': ai_art_items,
                'insights': insights,
                'by_style': self._group_by_style(ai_art_items),
                'prompt_techniques': self._analyze_techniques(ai_art_items),
                'trending_styles': self._extract_trending(ai_art_items),
            }

            quality_score = min(1.0, len(ai_art_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='midjourney.com',
                data_type='ai_art',
                content=content,
                metadata={
                    'item_count': len(ai_art_items),
                    'source': 'midjourney',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['midjourney', 'ai art', 'prompts', 'generative', 'creative ai'],
                target_agents=['creative_agent', 'ai_art_agent', 'prompt_agent'],
                target_advisors=['ai_art_director', 'creative_technologist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Midjourney data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if AI art relevant
            ai_keywords = ['ai', 'midjourney', 'stable diffusion', 'dall-e', 'generative',
                          'prompt', 'image generation', 'text to image', 'ai art']
            is_ai_art_relevant = any(kw in text for kw in ai_keywords)

            # Identify art style
            art_style = 'general'
            for style, keywords in self.art_styles.items():
                if any(kw in text for kw in keywords):
                    art_style = style
                    break

            # Identify prompt techniques mentioned
            techniques = []
            for technique, keywords in self.prompt_techniques.items():
                if any(kw in text for kw in keywords):
                    techniques.append(technique)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'art_style': art_style,
                'techniques': techniques,
                'is_ai_art_relevant': is_ai_art_relevant,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI art insights"""
        if not items:
            return {}

        style_counts = {}
        for item in items:
            style = item.get('art_style', 'general')
            style_counts[style] = style_counts.get(style, 0) + 1

        technique_counts = {}
        for item in items:
            for tech in item.get('techniques', []):
                technique_counts[tech] = technique_counts.get(tech, 0) + 1

        return {
            'total_items': len(items),
            'trending_styles': sorted(style_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_techniques': sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'ai_art_pulse': 'vibrant' if len(items) > 10 else 'steady',
        }

    def _group_by_style(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by art style"""
        groups = {}
        for item in items:
            style = item.get('art_style', 'general')
            if style not in groups:
                groups[style] = []
            groups[style].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_techniques(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze prompt techniques"""
        technique_counts = {}
        for item in items:
            for tech in item.get('techniques', []):
                technique_counts[tech] = technique_counts.get(tech, 0) + 1
        return dict(sorted(technique_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending AI art content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'style': i.get('art_style'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['midjourney', 'ai art', 'prompt', 'generative', 'text to image']
