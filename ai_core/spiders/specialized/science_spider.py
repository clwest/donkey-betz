"""
Science Spider - Scientific Research & Discovery
================================================

Session 343: Phase 1 RSS Expansion
Aggregates scientific news from multiple research sources.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ScienceSpider(BaseIntelligenceSpider):
    """Science news spider - research papers, discoveries, and science news"""

    RSS_FEEDS = {
        'science_daily': 'https://www.sciencedaily.com/rss/all.xml',
        'science_mag': 'https://www.science.org/rss/news_current.xml',
        'nature': 'https://www.nature.com/nature.rss',
        'new_scientist': 'https://www.newscientist.com/feed/home/',
        'phys_org': 'https://phys.org/rss-feed/',
        'scientific_american': 'https://www.scientificamerican.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.science_categories = {
            'physics': ['physics', 'quantum', 'particle', 'gravity', 'relativity'],
            'biology': ['biology', 'cell', 'gene', 'dna', 'evolution', 'species'],
            'chemistry': ['chemistry', 'molecule', 'compound', 'reaction', 'element'],
            'astronomy': ['space', 'nasa', 'planet', 'star', 'galaxy', 'black hole', 'mars'],
            'climate': ['climate', 'warming', 'carbon', 'ocean', 'temperature', 'weather'],
            'medicine': ['medicine', 'disease', 'treatment', 'drug', 'cancer', 'virus'],
            'ai_computing': ['ai', 'artificial intelligence', 'robot', 'algorithm', 'computer'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from science sources"""
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
            return {'articles': all_articles, 'source': 'science_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching science data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process science articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            # Categorize by field
            by_field = {}
            for a in processed:
                for cat in a.get('categories', ['general']):
                    by_field.setdefault(cat, []).append(a)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='science_aggregator',
                data_type='science_research',
                content={
                    'articles': processed,
                    'by_field': {k: len(v) for k, v in by_field.items()},
                    'count': len(processed),
                },
                metadata={'source': 'science_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 50 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['science', 'research', 'discovery', 'physics', 'biology', 'medicine'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['science_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing science data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.science_categories.items():
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
        return ['science', 'research', 'study', 'discovery', 'breakthrough']
