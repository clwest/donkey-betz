"""
Replicate Spider - AI Model Marketplace & API Intelligence
=============================================================

Session 218: Specialized spider for Replicate AI model platform.
Focuses on AI model marketplace, APIs, and ML deployment trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ReplicateSpider(BaseIntelligenceSpider):
    """Replicate spider - AI model marketplace and API intelligence"""

    RSS_FEEDS = {
        'replicate_blog': 'https://replicate.com/blog/rss.xml',
        'towards_data_science': 'https://towardsdatascience.com/feed',
        'ml_mastery': 'https://machinelearningmastery.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.model_categories = {
            'image_gen': ['image generation', 'text to image', 'stable diffusion', 'dall-e', 'flux'],
            'video': ['video', 'animation', 'motion', 'video generation'],
            'audio': ['audio', 'music', 'speech', 'voice', 'tts', 'stt'],
            'language': ['llm', 'language model', 'text', 'chat', 'gpt', 'llama'],
            'vision': ['vision', 'image recognition', 'object detection', 'segmentation'],
            'multimodal': ['multimodal', 'vision language', 'clip', 'blip'],
        }

        self.deployment_topics = {
            'api': ['api', 'endpoint', 'inference', 'prediction', 'request'],
            'scaling': ['scale', 'performance', 'latency', 'throughput', 'optimization'],
            'pricing': ['pricing', 'cost', 'credits', 'billing', 'usage'],
            'integration': ['integration', 'sdk', 'library', 'wrapper', 'client'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Replicate platform data"""
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

            return {'items': all_items, 'source': 'replicate'}

        except Exception as e:
            self.logger.error(f"Error fetching Replicate data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Replicate platform data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for AI model relevant content
            model_items = [i for i in processed_items if i.get('is_model_relevant')]

            insights = self._generate_insights(model_items)

            content = {
                'items': model_items,
                'insights': insights,
                'by_category': self._group_by_category(model_items),
                'deployment_topics': self._analyze_deployment(model_items),
                'trending_models': self._extract_trending(model_items),
            }

            quality_score = min(1.0, len(model_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='replicate.com',
                data_type='ai_models',
                content=content,
                metadata={
                    'item_count': len(model_items),
                    'source': 'replicate',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['replicate', 'ai models', 'api', 'ml deployment', 'inference'],
                target_agents=['ml_agent', 'api_agent', 'integration_agent'],
                target_advisors=['ml_architect', 'api_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Replicate data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if AI model relevant
            model_keywords = ['replicate', 'model', 'api', 'inference', 'ml', 'ai',
                            'deployment', 'prediction', 'machine learning']
            is_model_relevant = any(kw in text for kw in model_keywords)

            # Identify model category
            category = 'general'
            for cat, keywords in self.model_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify deployment topics
            topics = []
            for topic, keywords in self.deployment_topics.items():
                if any(kw in text for kw in keywords):
                    topics.append(topic)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'deployment_topics': topics,
                'is_model_relevant': is_model_relevant,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI model marketplace insights"""
        if not items:
            return {}

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        topic_counts = {}
        for item in items:
            for topic in item.get('deployment_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'top_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'deployment_focus': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'ecosystem_health': 'thriving' if len(items) > 10 else 'growing',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by model category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_deployment(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze deployment topic mentions"""
        topic_counts = {}
        for item in items:
            for topic in item.get('deployment_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending model content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['replicate', 'ai model', 'api', 'inference', 'ml deployment']
