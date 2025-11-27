"""
Envato Spider - Creative Assets Marketplace Intelligence
==========================================================

Session 218: Specialized spider for Envato marketplace (ThemeForest, CodeCanyon, etc).
Focuses on templates, themes, graphics, and digital asset trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class EnvatoSpider(BaseIntelligenceSpider):
    """Envato spider - creative assets marketplace intelligence"""

    # Envato and design marketplace RSS feeds
    RSS_FEEDS = {
        'envato_blog': 'https://envato.com/blog/feed/',
        'tutsplus': 'https://tutsplus.com/posts.atom',
        'webdesigner_depot': 'https://www.webdesignerdepot.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.asset_categories = {
            'themes': ['theme', 'template', 'wordpress', 'html', 'landing page'],
            'graphics': ['graphic', 'vector', 'illustration', 'icon', 'logo'],
            'code': ['plugin', 'script', 'code', 'javascript', 'php'],
            'video': ['video', 'motion', 'after effects', 'premiere', 'animation'],
            'audio': ['audio', 'music', 'sound effect', 'podcast', 'sfx'],
            'photos': ['photo', 'stock', 'image', 'photography', 'mockup'],
            '3d': ['3d', 'model', 'render', 'blender', 'cinema 4d'],
        }

        self.trend_signals = {
            'trending': ['trending', 'popular', 'best seller', 'top rated', 'featured'],
            'new': ['new', 'just added', 'fresh', 'latest', 'released'],
            'sale': ['sale', 'discount', 'deal', 'offer', 'bundle'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Envato marketplace data"""
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

            return {'items': all_items, 'source': 'envato'}

        except Exception as e:
            self.logger.error(f"Error fetching Envato data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Envato marketplace data"""
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
                'by_category': self._group_by_category(processed_items),
                'trending_assets': self._extract_trending(processed_items),
                'new_releases': self._extract_new(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='envato.com',
                data_type='creative_assets',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'envato',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['envato', 'templates', 'themes', 'graphics', 'digital assets'],
                target_agents=['creative_agent', 'design_agent', 'content_agent'],
                target_advisors=['creative_strategist', 'design_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Envato data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify asset category
            category = 'general'
            for cat, keywords in self.asset_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Check trend signals
            signals = []
            for signal, keywords in self.trend_signals.items():
                if any(kw in text for kw in keywords):
                    signals.append(signal)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'signals': signals,
                'is_trending': 'trending' in signals,
                'is_new': 'new' in signals,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate marketplace insights"""
        if not items:
            return {}

        trending = [i for i in items if i.get('is_trending')]
        new_items = [i for i in items if i.get('is_new')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            'total_items': len(items),
            'trending_count': len(trending),
            'new_releases': len(new_items),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_pulse': 'active' if len(trending) > 3 else 'steady',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by asset category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending assets"""
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in items if i.get('is_trending')][:5]

    def _extract_new(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract new releases"""
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in items if i.get('is_new')][:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['envato', 'themeforest', 'codecanyon', 'template', 'theme', 'graphics']
