"""
Business News Spider - Business & Finance News
==============================================

Session 343: Phase 1 RSS Expansion
Aggregates business news from major financial publications.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class BusinessNewsSpider(BaseIntelligenceSpider):
    """Business news spider - finance, markets, and business news"""

    RSS_FEEDS = {
        'harvard_business': 'https://hbr.org/resources/xml/rss/feed.xml',
        'forbes': 'https://www.forbes.com/innovation/feed/',
        'entrepreneur': 'https://www.entrepreneur.com/latest.rss',
        'inc': 'https://www.inc.com/rss/',
        'fast_company': 'https://www.fastcompany.com/latest/rss',
        'business_insider': 'https://www.businessinsider.com/rss',
        'marketwatch': 'https://www.marketwatch.com/rss/',
        'yahoo_finance': 'https://finance.yahoo.com/rss/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.business_categories = {
            'startups': ['startup', 'founder', 'entrepreneur', 'seed', 'venture', 'launch'],
            'markets': ['stock', 'market', 'trading', 'investor', 'shares', 'dow', 'nasdaq'],
            'tech_business': ['tech', 'ai', 'software', 'saas', 'cloud', 'digital'],
            'leadership': ['ceo', 'leadership', 'management', 'executive', 'strategy'],
            'small_business': ['small business', 'smb', 'growth', 'revenue', 'profit'],
            'economy': ['economy', 'inflation', 'fed', 'interest rate', 'gdp', 'recession'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from business sources"""
        try:
            all_articles = []
            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:10]:
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
            return {'articles': all_articles, 'source': 'business_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching business data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process business articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='business_aggregator',
                data_type='business_news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'business_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 60 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['business', 'finance', 'startups', 'markets', 'entrepreneurship'],
                target_agents=['research_agent', 'trend_analysis_agent', 'competitor_analysis_agent'],
                target_advisors=['business_analyst', 'financial_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing business data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.business_categories.items():
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
        return ['business', 'finance', 'startup', 'market', 'entrepreneur']
