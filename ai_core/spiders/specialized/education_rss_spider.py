"""
Education Spider - Educational News & Resources
===============================================

Session 343: Phase 1 RSS Expansion
Aggregates education news from multiple sources.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class EducationRSSSpider(BaseIntelligenceSpider):
    """Education news spider - K-12, higher ed, and edtech news"""

    RSS_FEEDS = {
        'ed_week': 'https://www.edweek.org/feed',
        'inside_higher_ed': 'https://www.insidehighered.com/rss/feed',
        'edsurge': 'https://www.edsurge.com/rss',
        'the_74': 'https://www.the74million.org/feed/',
        'chronicle': 'https://www.chronicle.com/section/News/6/rss',
        'edutopia': 'https://www.edutopia.org/rss.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.education_categories = {
            'k12': ['k-12', 'elementary', 'middle school', 'high school', 'students', 'teachers'],
            'higher_ed': ['college', 'university', 'higher education', 'degree', 'campus'],
            'edtech': ['edtech', 'online learning', 'e-learning', 'digital', 'platform'],
            'policy': ['policy', 'legislation', 'funding', 'budget', 'government'],
            'curriculum': ['curriculum', 'stem', 'math', 'reading', 'science', 'arts'],
            'special_ed': ['special education', 'disability', 'accommodations', 'iep'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from education sources"""
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
            return {'articles': all_articles, 'source': 'education_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching education data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process education articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='education_aggregator',
                data_type='education_news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'education_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 50 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['education', 'schools', 'learning', 'edtech', 'teaching'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['education_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing education data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.education_categories.items():
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
        return ['education', 'school', 'learning', 'teaching', 'students']
