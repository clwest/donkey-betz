"""
Creative Market Spider - Design Assets & Fonts Intelligence
=============================================================

Session 218: Specialized spider for Creative Market.
Focuses on design assets, fonts, templates, and creative tools.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class CreativeMarketSpider(BaseIntelligenceSpider):
    """Creative Market spider - design assets and fonts intelligence"""

    RSS_FEEDS = {
        'creative_bloq': 'https://www.creativebloq.com/feed',
        'designmodo': 'https://designmodo.com/feed/',
        'smashing_mag': 'https://www.smashingmagazine.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.asset_types = {
            'fonts': ['font', 'typeface', 'typography', 'lettering', 'type design'],
            'graphics': ['graphic', 'illustration', 'vector', 'clipart', 'artwork'],
            'templates': ['template', 'mockup', 'presentation', 'resume', 'flyer'],
            'photos': ['photo', 'stock photo', 'image', 'photography'],
            'themes': ['theme', 'wordpress', 'website', 'ui kit', 'dashboard'],
            'add_ons': ['add-on', 'plugin', 'extension', 'brush', 'action'],
        }

        self.design_trends = {
            'minimalist': ['minimal', 'clean', 'simple', 'modern', 'flat'],
            'vintage': ['vintage', 'retro', 'classic', 'old school', 'nostalgic'],
            'bold': ['bold', 'vibrant', 'colorful', 'bright', 'striking'],
            'elegant': ['elegant', 'luxury', 'premium', 'sophisticated', 'refined'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Creative Market data"""
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

            return {'items': all_items, 'source': 'creativemarket'}

        except Exception as e:
            self.logger.error(f"Error fetching Creative Market data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Creative Market data"""
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
                'by_type': self._group_by_type(processed_items),
                'trend_analysis': self._analyze_trends(processed_items),
                'font_highlights': self._extract_fonts(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='creativemarket.com',
                data_type='design_assets',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'creativemarket',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['creative market', 'fonts', 'graphics', 'templates', 'design'],
                target_agents=['design_agent', 'creative_agent', 'branding_agent'],
                target_advisors=['design_advisor', 'brand_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Creative Market data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify asset type
            asset_type = 'general'
            for atype, keywords in self.asset_types.items():
                if any(kw in text for kw in keywords):
                    asset_type = atype
                    break

            # Identify design trend
            trend_style = None
            for trend, keywords in self.design_trends.items():
                if any(kw in text for kw in keywords):
                    trend_style = trend
                    break

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'asset_type': asset_type,
                'trend_style': trend_style,
                'is_font': asset_type == 'fonts',
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate design market insights"""
        if not items:
            return {}

        fonts = [i for i in items if i.get('is_font')]

        type_counts = {}
        for item in items:
            atype = item.get('asset_type', 'general')
            type_counts[atype] = type_counts.get(atype, 0) + 1

        trend_counts = {}
        for item in items:
            trend = item.get('trend_style')
            if trend:
                trend_counts[trend] = trend_counts.get(trend, 0) + 1

        return {
            'total_items': len(items),
            'font_content': len(fonts),
            'top_asset_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'trending_styles': sorted(trend_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'design_pulse': 'creative' if len(items) > 10 else 'steady',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by asset type"""
        groups = {}
        for item in items:
            atype = item.get('asset_type', 'general')
            if atype not in groups:
                groups[atype] = []
            groups[atype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_trends(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze design trends"""
        trend_counts = {}
        for item in items:
            trend = item.get('trend_style')
            if trend:
                trend_counts[trend] = trend_counts.get(trend, 0) + 1
        return dict(sorted(trend_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_fonts(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract font-related content"""
        return [{'title': i.get('title'), 'link': i.get('link')}
                for i in items if i.get('is_font')][:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['creative market', 'fonts', 'graphics', 'templates', 'design assets']
