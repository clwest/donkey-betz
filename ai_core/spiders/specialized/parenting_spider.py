"""
Parenting Spider - Parenting & Family Resources
===============================================

Session 343: Phase 1 RSS Expansion
Aggregates parenting, family, and childcare content.
Highly relevant for family-focused business ideas.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ParentingSpider(BaseIntelligenceSpider):
    """Parenting spider - family, childcare, and parenting resources"""

    RSS_FEEDS = {
        'parents_magazine': 'https://www.parents.com/syndication/rss/',
        'babycenter': 'https://www.babycenter.com/rss',
        'scary_mommy': 'https://www.scarymommy.com/feed/',
        'fatherly': 'https://www.fatherly.com/feed/',
        'motherly': 'https://www.mother.ly/feed/',
        'romper': 'https://www.romper.com/rss',
        'today_parents': 'https://www.today.com/parents/rss',
        'family_education': 'https://www.familyeducation.com/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.parenting_categories = {
            'babies': ['baby', 'infant', 'newborn', 'nursing', 'breastfeeding', 'formula'],
            'toddlers': ['toddler', 'potty', 'tantrum', 'walking', 'talking'],
            'kids': ['kids', 'children', 'school', 'homework', 'activities'],
            'teens': ['teen', 'teenager', 'adolescent', 'puberty', 'high school'],
            'sleep': ['sleep', 'bedtime', 'nap', 'night', 'dream', 'routine'],
            'education': ['learning', 'reading', 'education', 'school', 'preschool'],
            'health': ['health', 'pediatric', 'vaccine', 'illness', 'doctor'],
            'activities': ['play', 'game', 'activity', 'craft', 'toy', 'outdoor'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from parenting sources"""
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
            return {'articles': all_articles, 'source': 'parenting_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching parenting data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process parenting articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            # Group by age category
            by_age = {}
            for a in processed:
                for cat in a.get('categories', ['general']):
                    by_age.setdefault(cat, []).append(a)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='parenting_aggregator',
                data_type='parenting_content',
                content={
                    'articles': processed,
                    'by_category': {k: len(v) for k, v in by_age.items()},
                    'count': len(processed),
                },
                metadata={'source': 'parenting_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 60 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['parenting', 'family', 'children', 'kids', 'babies', 'education'],
                target_agents=['research_agent', 'customer_research_agent'],
                target_advisors=['market_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing parenting data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.parenting_categories.items():
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
        return ['parenting', 'family', 'children', 'kids', 'baby', 'mom', 'dad']
