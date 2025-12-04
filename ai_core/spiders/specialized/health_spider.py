"""
Health Spider - Medical & Health News
=====================================

Session 343: Phase 1 RSS Expansion
Aggregates health news from trusted medical sources.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class HealthSpider(BaseIntelligenceSpider):
    """Health news spider - medical research, wellness, and health news"""

    RSS_FEEDS = {
        'webmd': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
        'medline_plus': 'https://medlineplus.gov/feeds/topic.xml',
        'nih_news': 'https://www.nih.gov/news-events/news-releases/feed',
        'cdc': 'https://tools.cdc.gov/podcasts/feed.asp?feedid=183',
        'medical_news_today': 'https://www.medicalnewstoday.com/rss',
        'healthline': 'https://www.healthline.com/rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.health_categories = {
            'mental_health': ['mental', 'anxiety', 'depression', 'stress', 'therapy', 'psychology'],
            'nutrition': ['nutrition', 'diet', 'vitamin', 'food', 'eating', 'weight'],
            'fitness': ['exercise', 'fitness', 'workout', 'physical activity', 'gym'],
            'disease': ['disease', 'cancer', 'diabetes', 'heart', 'alzheimer', 'infection'],
            'medication': ['drug', 'medication', 'treatment', 'therapy', 'fda', 'vaccine'],
            'wellness': ['wellness', 'sleep', 'lifestyle', 'healthy', 'prevention'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from health sources"""
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
            return {'articles': all_articles, 'source': 'health_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching health data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process health articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            # Categorize by topic
            by_topic = {}
            for a in processed:
                for cat in a.get('categories', ['general']):
                    by_topic.setdefault(cat, []).append(a)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='health_aggregator',
                data_type='health_news',
                content={
                    'articles': processed,
                    'by_topic': {k: len(v) for k, v in by_topic.items()},
                    'count': len(processed),
                },
                metadata={'source': 'health_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 50 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['health', 'medicine', 'wellness', 'nutrition', 'fitness'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['health_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing health data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.health_categories.items():
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
        return ['health', 'medicine', 'wellness', 'disease', 'treatment']
