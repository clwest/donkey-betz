"""
Sellfy Spider - Digital Products & POD Intelligence
======================================================

Session 218: Specialized spider for Sellfy platform.
Focuses on digital products, print-on-demand, and creator selling.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SellfySpider(BaseIntelligenceSpider):
    """Sellfy spider - digital products and POD intelligence"""

    RSS_FEEDS = {
        'ecommerce_fuel': 'https://www.ecommercefuel.com/feed/',
        'practical_ecom': 'https://www.practicalecommerce.com/feed',
        'oberlo_blog': 'https://www.oberlo.com/blog/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.product_types = {
            'digital': ['digital', 'download', 'ebook', 'course', 'pdf'],
            'pod': ['print on demand', 'pod', 't-shirt', 'merch', 'apparel'],
            'subscriptions': ['subscription', 'membership', 'recurring', 'monthly'],
            'music': ['music', 'beats', 'samples', 'audio', 'sound'],
            'video': ['video', 'footage', 'tutorial', 'workshop'],
            'software': ['software', 'plugin', 'extension', 'app', 'tool'],
        }

        self.selling_strategies = {
            'pricing': ['pricing', 'price', 'discount', 'bundle', 'tier'],
            'marketing': ['marketing', 'promotion', 'social', 'email', 'funnel'],
            'conversion': ['conversion', 'checkout', 'cart', 'upsell', 'cross-sell'],
            'branding': ['branding', 'design', 'storefront', 'logo', 'visual'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Sellfy ecosystem data"""
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

            return {'items': all_items, 'source': 'sellfy'}

        except Exception as e:
            self.logger.error(f"Error fetching Sellfy data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Sellfy ecosystem data"""
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
                'by_product_type': self._group_by_type(processed_items),
                'selling_strategies': self._analyze_strategies(processed_items),
                'trending_products': self._extract_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='sellfy.com',
                data_type='digital_selling',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'sellfy',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['sellfy', 'digital products', 'pod', 'ecommerce', 'creator'],
                target_agents=['product_agent', 'ecommerce_agent', 'creator_agent'],
                target_advisors=['ecommerce_advisor', 'creator_monetization_expert']
            )

        except Exception as e:
            self.logger.error(f"Error processing Sellfy data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify product type
            product_type = 'general'
            for ptype, keywords in self.product_types.items():
                if any(kw in text for kw in keywords):
                    product_type = ptype
                    break

            # Identify selling strategies
            strategies = []
            for strategy, keywords in self.selling_strategies.items():
                if any(kw in text for kw in keywords):
                    strategies.append(strategy)

            # Check if creator/seller focused
            is_creator_focused = any(word in text for word in ['creator', 'sell', 'product', 'store', 'shop'])

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'product_type': product_type,
                'strategies': strategies,
                'is_creator_focused': is_creator_focused,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate digital selling insights"""
        if not items:
            return {}

        creator_items = [i for i in items if i.get('is_creator_focused')]

        type_counts = {}
        for item in items:
            ptype = item.get('product_type', 'general')
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

        strategy_counts = {}
        for item in items:
            for strategy in item.get('strategies', []):
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

        return {
            'total_items': len(items),
            'creator_focused': len(creator_items),
            'top_product_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'popular_strategies': sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'seller_pulse': 'active' if len(creator_items) > 5 else 'growing',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by product type"""
        groups = {}
        for item in items:
            ptype = item.get('product_type', 'general')
            if ptype not in groups:
                groups[ptype] = []
            groups[ptype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_strategies(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze selling strategy mentions"""
        strategy_counts = {}
        for item in items:
            for strategy in item.get('strategies', []):
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return dict(sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending products"""
        creator_items = [i for i in items if i.get('is_creator_focused')]
        sorted_items = sorted(creator_items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('product_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['sellfy', 'digital products', 'print on demand', 'ecommerce', 'creator']
