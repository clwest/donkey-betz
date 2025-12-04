"""
Food Spider - Food, Cooking & Restaurant Industry
=================================================

Session 343: Phase 1 RSS Expansion
Aggregates food, cooking, and restaurant industry content.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class FoodSpider(BaseIntelligenceSpider):
    """Food spider - recipes, cooking, and restaurant industry news"""

    RSS_FEEDS = {
        'serious_eats': 'https://www.seriouseats.com/feed.rss',
        'food_network': 'https://www.foodnetwork.com/fnk/feeds/full/',
        'bon_appetit': 'https://www.bonappetit.com/feed/rss',
        'epicurious': 'https://www.epicurious.com/feed/rss',
        'eater': 'https://www.eater.com/rss/index.xml',
        'food52': 'https://food52.com/blog/feed',
        'budget_bytes': 'https://www.budgetbytes.com/feed/',
        'minimalist_baker': 'https://minimalistbaker.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.food_categories = {
            'recipes': ['recipe', 'cook', 'bake', 'prepare', 'ingredient', 'dish'],
            'restaurant': ['restaurant', 'chef', 'dining', 'menu', 'reservation'],
            'healthy': ['healthy', 'vegan', 'vegetarian', 'organic', 'diet', 'nutrition'],
            'budget': ['budget', 'cheap', 'affordable', 'save', 'frugal'],
            'quick_easy': ['quick', 'easy', 'simple', 'minute', 'weeknight'],
            'trends': ['trend', 'popular', 'viral', 'new', 'best'],
            'baking': ['bake', 'bread', 'cake', 'cookie', 'dessert', 'pastry'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from food sources"""
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
            return {'articles': all_articles, 'source': 'food_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching food data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process food articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='food_aggregator',
                data_type='food_content',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'food_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 60 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['food', 'cooking', 'recipes', 'restaurant', 'dining'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['market_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing food data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.food_categories.items():
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
        return ['food', 'cooking', 'recipe', 'restaurant', 'chef', 'dining']
