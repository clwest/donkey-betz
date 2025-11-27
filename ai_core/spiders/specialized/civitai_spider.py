"""
CivitAI Spider - Stable Diffusion Models & LoRA Intelligence
===============================================================

Session 218: Specialized spider for CivitAI community.
Focuses on Stable Diffusion models, LoRAs, embeddings, and AI art resources.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class CivitAISpider(BaseIntelligenceSpider):
    """CivitAI spider - Stable Diffusion models and LoRA intelligence"""

    RSS_FEEDS = {
        'stability_blog': 'https://stability.ai/blog/rss.xml',
        'huggingface_blog': 'https://huggingface.co/blog/feed.xml',
        'the_decoder': 'https://the-decoder.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.model_types = {
            'checkpoint': ['checkpoint', 'base model', 'sdxl', 'sd 1.5', 'sd 2.1'],
            'lora': ['lora', 'lycoris', 'loha', 'locon', 'fine-tune'],
            'embedding': ['embedding', 'textual inversion', 'ti', 'negative embedding'],
            'controlnet': ['controlnet', 'control', 'pose', 'depth', 'canny'],
            'vae': ['vae', 'variational', 'encoder', 'decoder'],
        }

        self.use_cases = {
            'characters': ['character', 'portrait', 'face', 'person', 'anime girl'],
            'landscapes': ['landscape', 'scenery', 'environment', 'nature', 'background'],
            'styles': ['style', 'artistic', 'painterly', 'anime', 'realistic'],
            'objects': ['object', 'product', 'item', 'vehicle', 'architecture'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch CivitAI community data"""
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

            return {'items': all_items, 'source': 'civitai'}

        except Exception as e:
            self.logger.error(f"Error fetching CivitAI data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process CivitAI community data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for SD/model relevant content
            model_items = [i for i in processed_items if i.get('is_model_relevant')]

            insights = self._generate_insights(model_items)

            content = {
                'items': model_items,
                'insights': insights,
                'by_model_type': self._group_by_type(model_items),
                'use_case_analysis': self._analyze_use_cases(model_items),
                'trending_models': self._extract_trending(model_items),
            }

            quality_score = min(1.0, len(model_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='civitai.com',
                data_type='sd_models',
                content=content,
                metadata={
                    'item_count': len(model_items),
                    'source': 'civitai',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['civitai', 'stable diffusion', 'lora', 'models', 'ai art'],
                target_agents=['ai_art_agent', 'model_agent', 'creative_agent'],
                target_advisors=['ai_art_director', 'ml_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing CivitAI data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if model/SD relevant
            model_keywords = ['stable diffusion', 'sd', 'lora', 'checkpoint', 'model',
                            'embedding', 'controlnet', 'diffusion', 'civitai']
            is_model_relevant = any(kw in text for kw in model_keywords)

            # Identify model type
            model_type = 'general'
            for mtype, keywords in self.model_types.items():
                if any(kw in text for kw in keywords):
                    model_type = mtype
                    break

            # Identify use case
            use_case = 'general'
            for uc, keywords in self.use_cases.items():
                if any(kw in text for kw in keywords):
                    use_case = uc
                    break

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'model_type': model_type,
                'use_case': use_case,
                'is_model_relevant': is_model_relevant,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate model intelligence insights"""
        if not items:
            return {}

        type_counts = {}
        for item in items:
            mtype = item.get('model_type', 'general')
            type_counts[mtype] = type_counts.get(mtype, 0) + 1

        use_case_counts = {}
        for item in items:
            uc = item.get('use_case', 'general')
            use_case_counts[uc] = use_case_counts.get(uc, 0) + 1

        return {
            'total_items': len(items),
            'top_model_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_use_cases': sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'model_ecosystem': 'active' if len(items) > 10 else 'steady',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by model type"""
        groups = {}
        for item in items:
            mtype = item.get('model_type', 'general')
            if mtype not in groups:
                groups[mtype] = []
            groups[mtype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_use_cases(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze use case distribution"""
        use_case_counts = {}
        for item in items:
            uc = item.get('use_case', 'general')
            use_case_counts[uc] = use_case_counts.get(uc, 0) + 1
        return dict(sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending model content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('model_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['civitai', 'stable diffusion', 'lora', 'checkpoint', 'embedding', 'model']
