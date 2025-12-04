"""
Travel Spider - Travel & Tourism Industry
=========================================

Session 343: Phase 1 RSS Expansion
Aggregates travel, tourism, and hospitality content.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class TravelSpider(BaseIntelligenceSpider):
    """Travel spider - travel news, destinations, and tourism industry"""

    RSS_FEEDS = {
        'lonely_planet': 'https://www.lonelyplanet.com/news/feed',
        'conde_nast': 'https://www.cntraveler.com/feed/rss',
        'travel_leisure': 'https://www.travelandleisure.com/feeds/all',
        'the_points_guy': 'https://thepointsguy.com/feed/',
        'nomadic_matt': 'https://www.nomadicmatt.com/feed/',
        'afar': 'https://www.afar.com/feed',
        'fodors': 'https://www.fodors.com/feed/',
        'skift': 'https://skift.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.travel_categories = {
            'destinations': ['destination', 'city', 'country', 'beach', 'mountain', 'island'],
            'hotels': ['hotel', 'resort', 'accommodation', 'stay', 'airbnb', 'hostel'],
            'flights': ['flight', 'airline', 'airport', 'miles', 'points', 'booking'],
            'budget': ['budget', 'cheap', 'affordable', 'deal', 'save', 'hack'],
            'luxury': ['luxury', 'premium', 'first class', 'exclusive', 'boutique'],
            'adventure': ['adventure', 'hiking', 'outdoor', 'trek', 'safari'],
            'business': ['business travel', 'corporate', 'industry', 'tourism'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from travel sources"""
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
            return {'articles': all_articles, 'source': 'travel_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching travel data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process travel articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='travel_aggregator',
                data_type='travel_content',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'travel_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 60 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['travel', 'tourism', 'destinations', 'hotels', 'flights'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['market_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing travel data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.travel_categories.items():
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
        return ['travel', 'tourism', 'destination', 'hotel', 'flight', 'vacation']
