"""
SeekingAlpha Spider - Investment Analysis Intelligence
=======================================================

Session 218: Specialized spider for SeekingAlpha investment platform.
Focuses on stock analysis, market commentary, and investment insights.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SeekingAlphaSpider(BaseIntelligenceSpider):
    """SeekingAlpha spider - investment analysis and market insights"""

    # Investment analysis RSS feeds
    RSS_FEEDS = {
        'marketwatch': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
        'investing': 'https://www.investing.com/rss/news.rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.investment_categories = {
            'stocks': ['stock', 'equity', 'shares', 'nasdaq', 'nyse', 's&p', 'dow'],
            'etf': ['etf', 'fund', 'index fund', 'vanguard', 'ishares', 'spdr'],
            'dividends': ['dividend', 'yield', 'payout', 'income', 'reit'],
            'growth': ['growth', 'tech stocks', 'momentum', 'high growth'],
            'value': ['value', 'undervalued', 'bargain', 'pe ratio', 'cheap'],
            'options': ['options', 'calls', 'puts', 'derivatives', 'volatility'],
            'macro': ['fed', 'interest rate', 'inflation', 'gdp', 'economy', 'recession'],
        }

        self.analysis_types = {
            'bullish': ['buy', 'bullish', 'upgrade', 'outperform', 'overweight', 'strong buy'],
            'bearish': ['sell', 'bearish', 'downgrade', 'underperform', 'underweight'],
            'neutral': ['hold', 'neutral', 'equal weight', 'market perform'],
            'earnings': ['earnings', 'revenue', 'profit', 'beat', 'miss', 'guidance'],
        }

        self.sectors = {
            'tech': ['technology', 'tech', 'software', 'saas', 'cloud', 'semiconductor'],
            'healthcare': ['healthcare', 'biotech', 'pharma', 'medical', 'drug'],
            'finance': ['bank', 'financial', 'insurance', 'fintech'],
            'energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind'],
            'consumer': ['retail', 'consumer', 'e-commerce', 'restaurant'],
            'industrial': ['industrial', 'manufacturing', 'aerospace', 'defense'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch investment analysis data"""
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

            return {'items': all_items, 'source': 'seekingalpha_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching SeekingAlpha data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process investment analysis data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_investment_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_category': self._group_by_category(processed_items),
                'sector_analysis': self._analyze_sectors(processed_items),
                'bullish_picks': self._extract_bullish(processed_items),
                'earnings_news': self._extract_earnings(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 25 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='seekingalpha.com',
                data_type='investment_analysis',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'seekingalpha_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['stocks', 'investing', 'analysis', 'market', 'finance'],
                target_agents=['investment_agent', 'stock_agent', 'wealth_agent'],
                target_advisors=['investment_advisor', 'portfolio_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing SeekingAlpha data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify investment category
            category = 'general'
            for cat, keywords in self.investment_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify analysis type
            analysis = 'neutral'
            for atype, keywords in self.analysis_types.items():
                if any(kw in text for kw in keywords):
                    analysis = atype
                    break

            # Identify sector
            sector = None
            for sec, keywords in self.sectors.items():
                if any(kw in text for kw in keywords):
                    sector = sec
                    break

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'analysis_type': analysis,
                'sector': sector,
                'is_bullish': analysis == 'bullish',
                'is_bearish': analysis == 'bearish',
                'is_earnings': analysis == 'earnings',
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_investment_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate investment insights"""
        if not items:
            return {}

        bullish = [i for i in items if i.get('is_bullish')]
        bearish = [i for i in items if i.get('is_bearish')]
        earnings = [i for i in items if i.get('is_earnings')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        avg_sentiment = sum(i.get('sentiment', 0) for i in items) / len(items) if items else 0

        return {
            'total_items': len(items),
            'bullish_count': len(bullish),
            'bearish_count': len(bearish),
            'earnings_news': len(earnings),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_sentiment': 'bullish' if len(bullish) > len(bearish) * 1.5 else 'bearish' if len(bearish) > len(bullish) * 1.5 else 'mixed',
            'avg_sentiment': round(avg_sentiment, 2),
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by investment category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'analysis': item.get('analysis_type'), 'link': item.get('link')})
        return groups

    def _analyze_sectors(self, items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze sector coverage"""
        sectors = {}
        for item in items:
            sector = item.get('sector')
            if sector:
                if sector not in sectors:
                    sectors[sector] = {'count': 0, 'bullish': 0, 'bearish': 0}
                sectors[sector]['count'] += 1
                if item.get('is_bullish'):
                    sectors[sector]['bullish'] += 1
                if item.get('is_bearish'):
                    sectors[sector]['bearish'] += 1
        return sectors

    def _extract_bullish(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract bullish picks"""
        bullish = []
        for item in items:
            if item.get('is_bullish'):
                bullish.append({
                    'title': item.get('title'),
                    'sector': item.get('sector'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return bullish[:5]

    def _extract_earnings(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract earnings news"""
        earnings = []
        for item in items:
            if item.get('is_earnings'):
                earnings.append({
                    'title': item.get('title'),
                    'sector': item.get('sector'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return earnings[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['stock', 'invest', 'market', 'buy', 'sell', 'earnings', 'dividend']
