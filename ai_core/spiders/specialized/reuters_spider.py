"""
Reuters Spider - Global News & Financial Wire Intelligence
===========================================================

Session 218: Specialized spider for Reuters news wire.
Focuses on breaking news, global markets, and institutional-grade intelligence.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ReutersSpider(BaseIntelligenceSpider):
    """Reuters spider - global news wire and financial intelligence"""

    # Reuters and news wire RSS feeds
    RSS_FEEDS = {
        'reuters_world': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
        'ap_business': 'https://feedx.net/rss/ap-business.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.news_categories = {
            'markets': ['market', 'stock', 'trading', 'wall street', 'nasdaq', 'dow'],
            'economy': ['economy', 'gdp', 'inflation', 'fed', 'central bank', 'rate'],
            'corporate': ['company', 'earnings', 'ceo', 'merger', 'acquisition', 'ipo'],
            'commodities': ['oil', 'gold', 'commodity', 'crude', 'energy', 'opec'],
            'crypto': ['bitcoin', 'crypto', 'blockchain', 'digital currency'],
            'politics': ['congress', 'white house', 'government', 'regulation', 'policy'],
            'global': ['china', 'europe', 'asia', 'emerging market', 'global'],
        }

        self.urgency_levels = {
            'breaking': ['breaking', 'urgent', 'just in', 'flash', 'alert'],
            'update': ['update', 'latest', 'developing', 'new'],
            'analysis': ['analysis', 'insight', 'exclusive', 'special report'],
        }

        self.regions = {
            'us': ['u.s.', 'us', 'america', 'washington', 'new york', 'fed'],
            'europe': ['europe', 'eu', 'uk', 'britain', 'germany', 'france', 'ecb'],
            'asia': ['china', 'japan', 'asia', 'india', 'korea', 'taiwan'],
            'emerging': ['emerging', 'brazil', 'russia', 'mexico', 'turkey'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch news wire data"""
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

            return {'items': all_items, 'source': 'reuters_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Reuters data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process news wire data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_wire_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_category': self._group_by_category(processed_items),
                'by_region': self._analyze_regional_coverage(processed_items),
                'breaking_news': self._extract_breaking(processed_items),
                'market_impact': self._assess_market_impact(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 25 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='reuters.com',
                data_type='news_wire',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'reuters_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'wire', 'breaking', 'global', 'markets'],
                target_agents=['news_agent', 'market_agent', 'global_agent'],
                target_advisors=['news_analyst', 'global_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Reuters data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify news category
            category = 'general'
            for cat, keywords in self.news_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify urgency level
            urgency = 'standard'
            for level, keywords in self.urgency_levels.items():
                if any(kw in text for kw in keywords):
                    urgency = level
                    break

            # Identify region
            region = 'global'
            for reg, keywords in self.regions.items():
                if any(kw in text for kw in keywords):
                    region = reg
                    break

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            # Market impact assessment
            market_keywords = ['surge', 'plunge', 'rally', 'selloff', 'crash', 'soar', 'tumble']
            has_market_impact = any(word in text for word in market_keywords)

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'urgency': urgency,
                'region': region,
                'is_breaking': urgency == 'breaking',
                'has_market_impact': has_market_impact,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_wire_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate news wire insights"""
        if not items:
            return {}

        breaking = [i for i in items if i.get('is_breaking')]
        market_moving = [i for i in items if i.get('has_market_impact')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        region_counts = {}
        for item in items:
            region = item.get('region', 'global')
            region_counts[region] = region_counts.get(region, 0) + 1

        return {
            'total_items': len(items),
            'breaking_count': len(breaking),
            'market_moving_count': len(market_moving),
            'top_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'regional_focus': sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:2],
            'news_tempo': 'fast' if len(breaking) > 3 else 'normal',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by news category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'urgency': item.get('urgency'), 'link': item.get('link')})
        return groups

    def _analyze_regional_coverage(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze regional news coverage"""
        region_counts = {}
        for item in items:
            region = item.get('region', 'global')
            region_counts[region] = region_counts.get(region, 0) + 1
        return dict(sorted(region_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_breaking(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract breaking news"""
        breaking = []
        for item in items:
            if item.get('is_breaking'):
                breaking.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'region': item.get('region'),
                    'link': item.get('link'),
                })
        return breaking[:5]

    def _assess_market_impact(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess market-impacting news"""
        impactful = []
        for item in items:
            if item.get('has_market_impact'):
                impactful.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return impactful[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['reuters', 'news', 'breaking', 'market', 'economy', 'global']
