"""
Shutterstock Spider - Stock Media & Licensing Intelligence
=============================================================

Session 218: Specialized spider for Shutterstock stock media platform.
Focuses on stock photos, videos, music, and licensing trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ShutterstockSpider(BaseIntelligenceSpider):
    """Shutterstock spider - stock media and licensing intelligence"""

    RSS_FEEDS = {
        'shutterstock_blog': 'https://www.shutterstock.com/blog/feed',
        'stock_media_news': 'https://petapixel.com/feed/',
        'photography_life': 'https://photographylife.com/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.media_types = {
            'photos': ['photo', 'image', 'photography', 'stock photo', 'picture'],
            'videos': ['video', 'footage', 'stock video', 'clip', '4k', 'hd'],
            'music': ['music', 'audio', 'soundtrack', 'royalty-free', 'track'],
            'editorial': ['editorial', 'news', 'event', 'celebrity', 'sports'],
            'vectors': ['vector', 'illustration', 'icon', 'graphic', 'eps'],
        }

        self.use_cases = {
            'commercial': ['commercial', 'advertising', 'marketing', 'brand', 'business'],
            'social_media': ['social media', 'instagram', 'facebook', 'tiktok', 'youtube'],
            'web': ['website', 'blog', 'web design', 'landing page', 'banner'],
            'print': ['print', 'brochure', 'flyer', 'poster', 'magazine'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Shutterstock data"""
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

            return {'items': all_items, 'source': 'shutterstock'}

        except Exception as e:
            self.logger.error(f"Error fetching Shutterstock data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Shutterstock data"""
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
                'by_media_type': self._group_by_type(processed_items),
                'use_case_analysis': self._analyze_use_cases(processed_items),
                'trending_media': self._extract_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='shutterstock.com',
                data_type='stock_media',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'shutterstock',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['shutterstock', 'stock', 'photos', 'videos', 'music', 'licensing'],
                target_agents=['creative_agent', 'marketing_agent', 'content_agent'],
                target_advisors=['creative_director', 'marketing_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Shutterstock data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify media type
            media_type = 'general'
            for mtype, keywords in self.media_types.items():
                if any(kw in text for kw in keywords):
                    media_type = mtype
                    break

            # Identify use cases
            use_cases = []
            for use_case, keywords in self.use_cases.items():
                if any(kw in text for kw in keywords):
                    use_cases.append(use_case)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'media_type': media_type,
                'use_cases': use_cases,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate stock media insights"""
        if not items:
            return {}

        type_counts = {}
        for item in items:
            mtype = item.get('media_type', 'general')
            type_counts[mtype] = type_counts.get(mtype, 0) + 1

        use_case_counts = {}
        for item in items:
            for uc in item.get('use_cases', []):
                use_case_counts[uc] = use_case_counts.get(uc, 0) + 1

        return {
            'total_items': len(items),
            'top_media_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_use_cases': sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_activity': 'high' if len(items) > 15 else 'moderate',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by media type"""
        groups = {}
        for item in items:
            mtype = item.get('media_type', 'general')
            if mtype not in groups:
                groups[mtype] = []
            groups[mtype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_use_cases(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze use case mentions"""
        use_case_counts = {}
        for item in items:
            for uc in item.get('use_cases', []):
                use_case_counts[uc] = use_case_counts.get(uc, 0) + 1
        return dict(sorted(use_case_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending media content"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('media_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['shutterstock', 'stock', 'photos', 'videos', 'royalty-free', 'licensing']
