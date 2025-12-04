"""
Real Estate Spider - Real Estate & Property News
================================================

Session 343: Phase 1 RSS Expansion
Aggregates real estate and property market news.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class RealEstateSpider(BaseIntelligenceSpider):
    """Real estate spider - property markets, housing, and real estate news"""

    RSS_FEEDS = {
        'realtor_news': 'https://www.realtor.com/news/feed/',
        'zillow': 'https://www.zillow.com/feed/',
        'inman': 'https://www.inman.com/feed/',
        'housingwire': 'https://www.housingwire.com/feed/',
        'curbed': 'https://www.curbed.com/rss/index.xml',
        'biggerpockets': 'https://www.biggerpockets.com/blog/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.real_estate_categories = {
            'buying': ['buy', 'purchase', 'buyer', 'mortgage', 'down payment', 'loan'],
            'selling': ['sell', 'seller', 'listing', 'asking price', 'offer'],
            'renting': ['rent', 'rental', 'tenant', 'landlord', 'lease', 'apartment'],
            'investing': ['invest', 'roi', 'flip', 'rental income', 'portfolio'],
            'market': ['market', 'price', 'appreciation', 'trend', 'forecast'],
            'commercial': ['commercial', 'office', 'retail', 'industrial', 'warehouse'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from real estate sources"""
        try:
            all_articles = []
            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:12]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name}: {e}")
            return {'articles': all_articles, 'source': 'real_estate_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching real estate data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process real estate articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='real_estate_aggregator',
                data_type='real_estate_news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'real_estate_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 50 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['real estate', 'property', 'housing', 'mortgage', 'investing'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['real_estate_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing real estate data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.real_estate_categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            blob = TextBlob(f"{title} {summary}")
            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'source': article.get('source', ''),
                'categories': categories or ['general'],
                'sentiment': blob.sentiment.polarity,
            }
        except:
            return None

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['real estate', 'property', 'housing', 'mortgage', 'home']
