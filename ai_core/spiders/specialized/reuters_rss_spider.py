"""
Reuters RSS Spider - International News Agency
==============================================

Session 343: Phase 1 RSS Expansion
Reuters provides authoritative news via RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ReutersRSSSpider(BaseIntelligenceSpider):
    """Reuters news spider - international news agency coverage"""

    RSS_FEEDS = {
        'top_news': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
        'world': 'https://www.reutersagency.com/feed/?best-topics=world&post_type=best',
        'tech': 'https://www.reutersagency.com/feed/?best-topics=tech&post_type=best',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Reuters"""
        try:
            all_articles = []
            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name}: {e}")
            return {'articles': all_articles, 'source': 'reuters'}
        except Exception as e:
            self.logger.error(f"Error fetching Reuters data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Reuters articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = [self._process_article(a) for a in articles if a]
            processed = [p for p in processed if p]

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='reuters.com',
                data_type='news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'reuters', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 30 + 0.4),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'business', 'world', 'finance'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['news_analyst', 'financial_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing Reuters data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            blob = TextBlob(f"{title} {summary}")
            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'feed_source': article.get('feed_source', ''),
                'sentiment': blob.sentiment.polarity,
            }
        except:
            return None

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['news', 'business', 'finance', 'world', 'markets']
