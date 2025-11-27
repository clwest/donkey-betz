"""
Etsy Spider - Digital Downloads & Printables Intelligence
============================================================

Session 218: Specialized spider for Etsy digital products marketplace.
Focuses on digital downloads, printables, templates, and creator trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class EtsySpider(BaseIntelligenceSpider):
    """Etsy spider - digital downloads and printables intelligence"""

    RSS_FEEDS = {
        'etsy_blog': 'https://blog.etsy.com/en/feed/',
        'creative_market_blog': 'https://creativemarket.com/blog/feed',
        'printable_tips': 'https://www.printaura.com/blog/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.product_types = {
            'printables': ['printable', 'print at home', 'digital print', 'wall art', 'poster'],
            'planners': ['planner', 'calendar', 'organizer', 'tracker', 'checklist'],
            'invitations': ['invitation', 'invite', 'wedding', 'party', 'announcement'],
            'graphics': ['clipart', 'svg', 'png', 'graphic', 'illustration'],
            'templates': ['template', 'canva template', 'resume', 'social media'],
            'patterns': ['pattern', 'sewing', 'crochet', 'knitting', 'embroidery'],
        }

        self.seller_topics = {
            'marketing': ['marketing', 'seo', 'tags', 'keywords', 'visibility'],
            'pricing': ['pricing', 'profit', 'cost', 'margin', 'passive income'],
            'trends': ['trending', 'seasonal', 'holiday', 'popular', 'bestseller'],
            'tools': ['tools', 'software', 'automation', 'canva', 'photoshop'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Etsy digital products data"""
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

            return {'items': all_items, 'source': 'etsy'}

        except Exception as e:
            self.logger.error(f"Error fetching Etsy data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Etsy digital products data"""
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
                'seller_insights': self._analyze_seller_topics(processed_items),
                'trending_products': self._extract_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='etsy.com',
                data_type='digital_products',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'etsy',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['etsy', 'digital downloads', 'printables', 'templates', 'passive income'],
                target_agents=['product_agent', 'creative_agent', 'seller_agent'],
                target_advisors=['ecommerce_advisor', 'passive_income_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Etsy data: {e}")
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

            # Identify seller topics
            topics = []
            for topic, keywords in self.seller_topics.items():
                if any(kw in text for kw in keywords):
                    topics.append(topic)

            # Check if digital product focused
            is_digital = any(word in text for word in ['digital', 'download', 'printable', 'instant', 'pdf'])

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'product_type': product_type,
                'seller_topics': topics,
                'is_digital': is_digital,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate digital products insights"""
        if not items:
            return {}

        digital_items = [i for i in items if i.get('is_digital')]

        type_counts = {}
        for item in items:
            ptype = item.get('product_type', 'general')
            type_counts[ptype] = type_counts.get(ptype, 0) + 1

        topic_counts = {}
        for item in items:
            for topic in item.get('seller_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'digital_focused': len(digital_items),
            'top_product_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'seller_focus': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_pulse': 'active' if len(digital_items) > 5 else 'steady',
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

    def _analyze_seller_topics(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze seller topic mentions"""
        topic_counts = {}
        for item in items:
            for topic in item.get('seller_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending products"""
        digital_items = [i for i in items if i.get('is_digital')]
        sorted_items = sorted(digital_items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('product_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['etsy', 'digital download', 'printable', 'template', 'passive income']
