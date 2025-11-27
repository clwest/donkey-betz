"""
AppSumo Spider - Digital Tool Deals & Product Launches Intelligence
======================================================================

Session 218: Specialized spider for AppSumo marketplace.
Focuses on software deals, product launches, and SaaS trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class AppSumoSpider(BaseIntelligenceSpider):
    """AppSumo spider - digital tool deals and product launches intelligence"""

    RSS_FEEDS = {
        'appsumo_blog': 'https://blog.appsumo.com/feed/',
        'product_hunt': 'https://www.producthunt.com/feed',
        'betalist': 'https://betalist.com/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.tool_categories = {
            'marketing': ['marketing', 'seo', 'email', 'social media', 'analytics'],
            'productivity': ['productivity', 'project', 'task', 'automation', 'workflow'],
            'design': ['design', 'graphic', 'video', 'photo', 'creative'],
            'development': ['development', 'code', 'api', 'hosting', 'database'],
            'ai_tools': ['ai', 'gpt', 'chatbot', 'automation', 'machine learning'],
            'business': ['crm', 'sales', 'finance', 'hr', 'operations'],
        }

        self.deal_signals = {
            'lifetime': ['lifetime', 'ltd', 'one-time', 'forever', 'no subscription'],
            'discount': ['discount', 'off', 'deal', 'save', 'limited'],
            'new_launch': ['launch', 'new', 'introducing', 'announcing', 'released'],
            'popular': ['popular', 'trending', 'hot', 'bestseller', 'top'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch AppSumo ecosystem data"""
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

            return {'items': all_items, 'source': 'appsumo'}

        except Exception as e:
            self.logger.error(f"Error fetching AppSumo data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process AppSumo ecosystem data"""
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
                'deal_analysis': self._analyze_deals(processed_items),
                'hot_deals': self._extract_hot_deals(processed_items),
                'new_launches': self._extract_launches(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='appsumo.com',
                data_type='software_deals',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'appsumo',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['appsumo', 'deals', 'software', 'saas', 'lifetime deals'],
                target_agents=['deals_agent', 'product_agent', 'saas_agent'],
                target_advisors=['deal_hunter', 'saas_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing AppSumo data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify tool category
            category = 'general'
            for cat, keywords in self.tool_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify deal signals
            signals = []
            for signal, keywords in self.deal_signals.items():
                if any(kw in text for kw in keywords):
                    signals.append(signal)

            is_lifetime_deal = 'lifetime' in signals
            is_new_launch = 'new_launch' in signals

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'deal_signals': signals,
                'is_lifetime_deal': is_lifetime_deal,
                'is_new_launch': is_new_launch,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate software deals insights"""
        if not items:
            return {}

        lifetime_deals = [i for i in items if i.get('is_lifetime_deal')]
        new_launches = [i for i in items if i.get('is_new_launch')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        signal_counts = {}
        for item in items:
            for signal in item.get('deal_signals', []):
                signal_counts[signal] = signal_counts.get(signal, 0) + 1

        return {
            'total_items': len(items),
            'lifetime_deals': len(lifetime_deals),
            'new_launches': len(new_launches),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'deal_types': signal_counts,
            'market_pulse': 'hot' if len(lifetime_deals) > 3 else 'active',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by tool category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_deals(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze deal signal distribution"""
        signal_counts = {}
        for item in items:
            for signal in item.get('deal_signals', []):
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
        return dict(sorted(signal_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_hot_deals(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract hot lifetime deals"""
        ltd_items = [i for i in items if i.get('is_lifetime_deal')]
        sorted_items = sorted(ltd_items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def _extract_launches(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract new launches"""
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in items if i.get('is_new_launch')][:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['appsumo', 'deal', 'lifetime', 'software', 'saas', 'tool']
