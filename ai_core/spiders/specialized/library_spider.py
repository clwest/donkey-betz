"""
Library Spider - Library & Archive Resources
=============================================

Session 343: Phase 1 RSS Expansion
Aggregates library news, digital archives, and research resources.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class LibrarySpider(BaseIntelligenceSpider):
    """Library spider - library news, digital archives, and open access resources"""

    RSS_FEEDS = {
        # Library associations
        'ala_news': 'https://www.ala.org/news/rss',
        'library_journal': 'https://www.libraryjournal.com/feed',
        'american_libraries': 'https://americanlibrariesmagazine.org/feed/',

        # Digital archives and open access
        'internet_archive': 'https://blog.archive.org/feed/',
        'open_culture': 'https://www.openculture.com/feed',
        'project_gutenberg': 'https://www.gutenberg.org/cache/epub/feeds/today.rss',

        # Research & academia
        'arxiv_cs': 'https://rss.arxiv.org/rss/cs',
        'plos_one': 'https://journals.plos.org/plosone/feed/atom',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.library_categories = {
            'digital_archives': ['archive', 'digitization', 'digital collection', 'preservation'],
            'open_access': ['open access', 'free', 'public domain', 'creative commons'],
            'research': ['research', 'study', 'paper', 'journal', 'publication'],
            'technology': ['technology', 'software', 'digital', 'database', 'catalog'],
            'community': ['community', 'program', 'event', 'outreach', 'literacy'],
            'policy': ['policy', 'funding', 'legislation', 'copyright', 'intellectual property'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from library sources"""
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
            return {'articles': all_articles, 'source': 'library_aggregator'}
        except Exception as e:
            self.logger.error(f"Error fetching library data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process library articles"""
        try:
            articles = raw_data.get('articles', [])
            processed = []

            for article in articles:
                p = self._process_article(article)
                if p:
                    processed.append(p)

            # Separate by source type
            archives = [a for a in processed if a.get('source') in ['internet_archive', 'open_culture', 'project_gutenberg']]
            research = [a for a in processed if a.get('source') in ['arxiv_cs', 'plos_one']]
            library_news = [a for a in processed if a.get('source') in ['ala_news', 'library_journal', 'american_libraries']]

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='library_aggregator',
                data_type='library_resources',
                content={
                    'articles': processed,
                    'archives': archives,
                    'research': research,
                    'library_news': library_news,
                    'count': len(processed),
                },
                metadata={'source': 'library_aggregator', 'feeds': list(self.RSS_FEEDS.keys())},
                quality_score=min(1.0, len(processed) / 40 + 0.3),
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['library', 'archives', 'research', 'open access', 'books'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['research_analyst']
            )
        except Exception as e:
            self.logger.error(f"Error processing library data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            categories = []
            for cat, keywords in self.library_categories.items():
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
        return ['library', 'archive', 'books', 'research', 'open access']
