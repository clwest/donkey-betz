"""
Adobe Stock Spider - Stock Content & Creative Trends Intelligence
===================================================================

Session 218: Specialized spider for Adobe Stock and Adobe creative ecosystem.
Focuses on stock images, videos, templates, and creative trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class AdobeStockSpider(BaseIntelligenceSpider):
    """Adobe Stock spider - stock content and creative trends intelligence"""

    RSS_FEEDS = {
        'adobe_blog': 'https://blog.adobe.com/en/publish/rss',
        'adobe_create': 'https://create.adobe.com/feed',
        'psdvault': 'https://www.psd-vault.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.content_types = {
            'photos': ['photo', 'image', 'photography', 'stock photo', 'picture'],
            'vectors': ['vector', 'illustration', 'graphic', 'icon', 'svg'],
            'videos': ['video', 'footage', 'motion', 'clip', 'b-roll'],
            'templates': ['template', 'psd', 'indesign', 'illustrator', 'photoshop'],
            '3d': ['3d', 'model', 'render', 'dimension', 'substance'],
            'audio': ['audio', 'music', 'sound', 'sfx', 'soundtrack'],
        }

        self.creative_tools = {
            'photoshop': ['photoshop', 'ps', 'photo editing', 'retouching'],
            'illustrator': ['illustrator', 'ai', 'vector', 'illustration'],
            'premiere': ['premiere', 'video editing', 'editing', 'cut'],
            'after_effects': ['after effects', 'ae', 'motion graphics', 'vfx'],
            'xd': ['xd', 'ui design', 'ux', 'prototype'],
            'lightroom': ['lightroom', 'lr', 'photo processing', 'raw'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Adobe Stock data"""
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

            return {'items': all_items, 'source': 'adobestock'}

        except Exception as e:
            self.logger.error(f"Error fetching Adobe Stock data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Adobe Stock data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_content_type': self._group_by_type(processed_items),
                'tool_mentions': self._analyze_tools(processed_items),
                'trending_content': self._extract_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='stock.adobe.com',
                data_type='stock_content',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'adobestock',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['adobe', 'stock', 'photos', 'videos', 'templates', 'creative'],
                target_agents=['creative_agent', 'design_agent', 'video_agent'],
                target_advisors=['creative_director', 'design_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Adobe Stock data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify content type
            content_type = 'general'
            for ctype, keywords in self.content_types.items():
                if any(kw in text for kw in keywords):
                    content_type = ctype
                    break

            # Identify mentioned tools
            tools_mentioned = []
            for tool, keywords in self.creative_tools.items():
                if any(kw in text for kw in keywords):
                    tools_mentioned.append(tool)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'content_type': content_type,
                'tools_mentioned': tools_mentioned,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate stock content insights"""
        if not items:
            return {}

        type_counts = {}
        for item in items:
            ctype = item.get('content_type', 'general')
            type_counts[ctype] = type_counts.get(ctype, 0) + 1

        tool_counts = {}
        for item in items:
            for tool in item.get('tools_mentioned', []):
                tool_counts[tool] = tool_counts.get(tool, 0) + 1

        return {
            'total_items': len(items),
            'top_content_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_tools': sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'creative_pulse': 'vibrant' if len(items) > 15 else 'steady',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by content type"""
        groups = {}
        for item in items:
            ctype = item.get('content_type', 'general')
            if ctype not in groups:
                groups[ctype] = []
            groups[ctype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_tools(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze tool mentions"""
        tool_counts = {}
        for item in items:
            for tool in item.get('tools_mentioned', []):
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('content_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['adobe', 'stock', 'photos', 'videos', 'creative cloud', 'photoshop']
