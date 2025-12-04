"""
CNN Spider - Cable News Network Intelligence
=============================================

Session 343: Phase 1 RSS Expansion
CNN provides news coverage via free RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class CNNSpider(BaseIntelligenceSpider):
    """CNN news spider - breaking news and analysis"""

    RSS_FEEDS = {
        'top_stories': 'http://rss.cnn.com/rss/cnn_topstories.rss',
        'world': 'http://rss.cnn.com/rss/cnn_world.rss',
        'us': 'http://rss.cnn.com/rss/cnn_us.rss',
        'business': 'http://rss.cnn.com/rss/money_latest.rss',
        'politics': 'http://rss.cnn.com/rss/cnn_allpolitics.rss',
        'tech': 'http://rss.cnn.com/rss/cnn_tech.rss',
        'health': 'http://rss.cnn.com/rss/cnn_health.rss',
        'entertainment': 'http://rss.cnn.com/rss/cnn_showbiz.rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from CNN"""
        try:
            all_articles = []
            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:10]:
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
            return {'articles': all_articles, 'source': 'cnn'}
        except Exception as e:
            self.logger.error(f"Error fetching CNN data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process CNN articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = [self._process_article(a) for a in articles if a]
            processed = [p for p in processed if p]

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='cnn.com',
                data_type='news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'cnn', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 40 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'politics', 'business', 'world'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['news_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing CNN data: {e}")
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
        return ['news', 'politics', 'business', 'breaking']
