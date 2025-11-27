"""
Bloomberg Spider - Professional Finance & Markets Intelligence
===============================================================

Session 218: Specialized spider for Bloomberg-style financial news.
Focuses on markets, economics, and professional finance insights.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class BloombergSpider(BaseIntelligenceSpider):
    """Bloomberg spider - professional finance and markets intelligence"""

    # Professional finance RSS feeds (Bloomberg alternatives)
    RSS_FEEDS = {
        'financial_times': 'https://www.ft.com/rss/home',
        'wsj_markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        'reuters_business': 'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.market_topics = {
            'equities': ['stock', 'equity', 'shares', 'nasdaq', 'nyse', 's&p 500', 'dow jones'],
            'fixed_income': ['bond', 'treasury', 'yield', 'fixed income', 'credit', 'debt'],
            'forex': ['forex', 'currency', 'dollar', 'euro', 'yen', 'fx', 'exchange rate'],
            'commodities': ['oil', 'gold', 'commodity', 'crude', 'copper', 'silver'],
            'crypto': ['bitcoin', 'crypto', 'ethereum', 'digital asset'],
        }

        self.economic_indicators = {
            'monetary': ['fed', 'central bank', 'interest rate', 'rate hike', 'rate cut', 'monetary policy'],
            'inflation': ['inflation', 'cpi', 'pce', 'price', 'deflation'],
            'employment': ['jobs', 'employment', 'unemployment', 'payroll', 'labor'],
            'gdp': ['gdp', 'growth', 'recession', 'expansion', 'economic'],
        }

        self.news_types = {
            'breaking': ['breaking', 'just in', 'alert', 'urgent'],
            'analysis': ['analysis', 'outlook', 'forecast', 'opinion'],
            'data': ['report', 'data', 'numbers', 'statistics', 'figures'],
            'corporate': ['earnings', 'merger', 'acquisition', 'm&a', 'ipo', 'deal'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch professional finance data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
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

            return {'items': all_items, 'source': 'bloomberg_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Bloomberg data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process professional finance data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_market_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'market_coverage': self._analyze_market_coverage(processed_items),
                'economic_focus': self._analyze_economic_focus(processed_items),
                'breaking_news': self._extract_breaking(processed_items),
                'market_movers': self._identify_market_movers(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 25 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='bloomberg.com',
                data_type='professional_finance',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'bloomberg_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['markets', 'finance', 'economics', 'professional', 'trading'],
                target_agents=['market_agent', 'trading_agent', 'macro_agent'],
                target_advisors=['market_strategist', 'chief_economist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Bloomberg data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify market topic
            market_topic = 'general'
            for topic, keywords in self.market_topics.items():
                if any(kw in text for kw in keywords):
                    market_topic = topic
                    break

            # Identify economic indicator
            economic_indicator = None
            for indicator, keywords in self.economic_indicators.items():
                if any(kw in text for kw in keywords):
                    economic_indicator = indicator
                    break

            # Identify news type
            news_type = 'news'
            for ntype, keywords in self.news_types.items():
                if any(kw in text for kw in keywords):
                    news_type = ntype
                    break

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            # Market impact assessment
            high_impact_words = ['surge', 'plunge', 'crash', 'soar', 'tumble', 'record', 'historic']
            is_high_impact = any(word in text for word in high_impact_words)

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'market_topic': market_topic,
                'economic_indicator': economic_indicator,
                'news_type': news_type,
                'is_breaking': news_type == 'breaking',
                'is_high_impact': is_high_impact,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_market_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market insights"""
        if not items:
            return {}

        breaking = [i for i in items if i.get('is_breaking')]
        high_impact = [i for i in items if i.get('is_high_impact')]

        topic_counts = {}
        for item in items:
            topic = item.get('market_topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        avg_sentiment = sum(i.get('sentiment', 0) for i in items) / len(items) if items else 0

        return {
            'total_items': len(items),
            'breaking_news': len(breaking),
            'high_impact_stories': len(high_impact),
            'market_focus': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_mood': 'risk-on' if avg_sentiment > 0.1 else 'risk-off' if avg_sentiment < -0.1 else 'neutral',
        }

    def _analyze_market_coverage(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze market topic coverage"""
        topic_counts = {}
        for item in items:
            topic = item.get('market_topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_economic_focus(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze economic indicator focus"""
        indicator_counts = {}
        for item in items:
            indicator = item.get('economic_indicator')
            if indicator:
                indicator_counts[indicator] = indicator_counts.get(indicator, 0) + 1
        return dict(sorted(indicator_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_breaking(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract breaking news"""
        breaking = []
        for item in items:
            if item.get('is_breaking') or item.get('is_high_impact'):
                breaking.append({
                    'title': item.get('title'),
                    'market_topic': item.get('market_topic'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return breaking[:5]

    def _identify_market_movers(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify market-moving stories"""
        movers = []
        for item in items:
            if item.get('is_high_impact'):
                movers.append({
                    'title': item.get('title'),
                    'market_topic': item.get('market_topic'),
                    'economic_indicator': item.get('economic_indicator'),
                    'link': item.get('link'),
                })
        return movers[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['market', 'stocks', 'bonds', 'fed', 'economy', 'trading', 'finance']
