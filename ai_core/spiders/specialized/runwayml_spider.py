"""
Runway ML Spider - AI Video & Creative Tools Intelligence
============================================================

Session 218: Specialized spider for Runway ML platform.
Focuses on AI video generation, creative tools, and motion design.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class RunwayMLSpider(BaseIntelligenceSpider):
    """Runway ML spider - AI video and creative tools intelligence"""

    RSS_FEEDS = {
        'runway_research': 'https://research.runwayml.com/feed',
        'venturebeat_ai': 'https://venturebeat.com/category/ai/feed/',
        'the_verge_ai': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.creative_tools = {
            'video_gen': ['video generation', 'gen-2', 'gen-3', 'text to video', 'video ai'],
            'image_edit': ['image editing', 'inpainting', 'outpainting', 'remove background'],
            'motion': ['motion', 'animation', 'motion brush', 'camera control'],
            'audio': ['audio', 'music generation', 'sound', 'voice'],
            'effects': ['effects', 'vfx', 'green screen', 'compositing'],
        }

        self.use_cases = {
            'filmmaking': ['film', 'movie', 'cinema', 'director', 'cinematography'],
            'advertising': ['ad', 'commercial', 'marketing', 'brand', 'campaign'],
            'social_content': ['social', 'tiktok', 'reels', 'shorts', 'content creator'],
            'music_video': ['music video', 'mv', 'artist', 'visualizer'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Runway ML data"""
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

            return {'items': all_items, 'source': 'runwayml'}

        except Exception as e:
            self.logger.error(f"Error fetching Runway ML data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Runway ML data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for AI video/creative tools relevant content
            ai_video_items = [i for i in processed_items if i.get('is_ai_video_relevant')]

            insights = self._generate_insights(ai_video_items)

            content = {
                'items': ai_video_items,
                'insights': insights,
                'by_tool_type': self._group_by_tool(ai_video_items),
                'use_case_analysis': self._analyze_use_cases(ai_video_items),
                'trending_features': self._extract_trending(ai_video_items),
            }

            quality_score = min(1.0, len(ai_video_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='runwayml.com',
                data_type='ai_video',
                content=content,
                metadata={
                    'item_count': len(ai_video_items),
                    'source': 'runwayml',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['runway', 'ai video', 'gen-2', 'creative tools', 'motion'],
                target_agents=['video_agent', 'creative_agent', 'motion_agent'],
                target_advisors=['video_director', 'creative_technologist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Runway ML data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if AI video relevant
            ai_video_keywords = ['runway', 'video generation', 'gen-2', 'gen-3', 'ai video',
                                'text to video', 'motion', 'creative ai', 'sora', 'pika']
            is_ai_video_relevant = any(kw in text for kw in ai_video_keywords)

            # Identify tool type
            tool_type = 'general'
            for tool, keywords in self.creative_tools.items():
                if any(kw in text for kw in keywords):
                    tool_type = tool
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
                'tool_type': tool_type,
                'use_case': use_case,
                'is_ai_video_relevant': is_ai_video_relevant,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI video insights"""
        if not items:
            return {}

        tool_counts = {}
        for item in items:
            tool = item.get('tool_type', 'general')
            tool_counts[tool] = tool_counts.get(tool, 0) + 1

        use_case_counts = {}
        for item in items:
            uc = item.get('use_case', 'general')
            use_case_counts[uc] = use_case_counts.get(uc, 0) + 1

        return {
            'total_items': len(items),
            'top_tools': sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_use_cases': sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'ai_video_pulse': 'innovative' if len(items) > 10 else 'growing',
        }

    def _group_by_tool(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by tool type"""
        groups = {}
        for item in items:
            tool = item.get('tool_type', 'general')
            if tool not in groups:
                groups[tool] = []
            groups[tool].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_use_cases(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze use case distribution"""
        use_case_counts = {}
        for item in items:
            uc = item.get('use_case', 'general')
            use_case_counts[uc] = use_case_counts.get(uc, 0) + 1
        return dict(sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending AI video content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'tool': i.get('tool_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['runway', 'ai video', 'gen-2', 'text to video', 'creative tools']
