"""
Government Spider - Government News & Data
==========================================

Session 343: Phase 1 RSS Expansion
Aggregates government news and public data feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class GovernmentSpider(BaseIntelligenceSpider):
    """Government news spider - federal agencies, policy, and public data"""

    RSS_FEEDS = {
        # Federal agencies
        'whitehouse': 'https://www.whitehouse.gov/feed/',
        'usa_gov': 'https://www.usa.gov/rss/updates.xml',
        'federal_register': 'https://www.federalregister.gov/documents/current.rss',

        # Economic data
        'bls': 'https://www.bls.gov/feed/bls_latest.rss',
        'census': 'https://www.census.gov/economic-indicators/indicator.xml',

        # Regulatory
        'sec_news': 'https://www.sec.gov/news/pressreleases.rss',
        'ftc': 'https://www.ftc.gov/news-events/rss/press-releases.xml',
        'fda': 'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds',

        # Small business
        'sba': 'https://www.sba.gov/feeds/sba-news',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.gov_categories = {
            'economic': ['economic', 'employment', 'jobs', 'unemployment', 'gdp', 'inflation'],
            'regulatory': ['regulation', 'rule', 'compliance', 'enforcement', 'fine', 'penalty'],
            'policy': ['policy', 'legislation', 'bill', 'law', 'act', 'executive order'],
            'small_business': ['small business', 'entrepreneur', 'sba', 'loan', 'grant'],
            'trade': ['trade', 'tariff', 'import', 'export', 'commerce'],
            'consumer': ['consumer', 'protection', 'safety', 'recall', 'warning'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from government sources"""
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
            return {'articles': all_articles, 'source': 'government_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching government data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process government articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='government_aggregator',
                data_type='government_news',
                content={'articles': processed, 'count': len(processed)},
                metadata={'source': 'government_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 50 + 0.4),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['government', 'policy', 'regulation', 'economic', 'federal'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['policy_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing government data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.gov_categories.items():
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
        return ['government', 'federal', 'policy', 'regulation', 'economic']
