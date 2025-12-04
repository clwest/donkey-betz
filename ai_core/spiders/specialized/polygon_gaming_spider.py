"""
Polygon Gaming Spider - Gaming Industry News
============================================

Session 343: Phase 1 Spider Expansion
Polygon provides gaming industry news via free RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class PolygonGamingSpider(BaseIntelligenceSpider):
    """Polygon gaming spider - video game news and reviews"""

    RSS_FEEDS = {
        'main': 'https://www.polygon.com/rss/index.xml',
        'reviews': 'https://www.polygon.com/rss/reviews/index.xml',
        'features': 'https://www.polygon.com/rss/features/index.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.gaming_categories = {
            'playstation': ['playstation', 'ps5', 'ps4', 'sony', 'dualsense'],
            'xbox': ['xbox', 'microsoft', 'game pass', 'series x', 'series s'],
            'nintendo': ['nintendo', 'switch', 'mario', 'zelda', 'pokemon'],
            'pc': ['pc', 'steam', 'epic', 'valve', 'gog'],
            'mobile': ['mobile', 'ios', 'android', 'apple arcade'],
            'esports': ['esports', 'tournament', 'competitive', 'league', 'championship'],
            'indie': ['indie', 'independent', 'pixel', 'retro'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Polygon"""
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
                                'author': entry.get('author', 'Polygon'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'polygon'}

        except Exception as e:
            self.logger.error(f"Error fetching Polygon data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Polygon articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            content = {
                'articles': processed_articles,
                'analytics': self._generate_analytics(processed_articles),
                'trending_topics': self._extract_trending_topics(processed_articles),
                'platform_breakdown': self._platform_breakdown(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='polygon.com',
                data_type='gaming_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'polygon',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['gaming', 'video games', 'reviews', 'esports'],
                target_agents=['research_agent', 'content_strategy_agent'],
                target_advisors=['gaming_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing Polygon data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            blob = TextBlob(f"{title} {summary}")
            sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'classification': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
            }

            categories = []
            for cat, keywords in self.gaming_categories.items():
                if any(kw in text for kw in keywords):
                    categories.append(cat)

            return {
                'title': title,
                'summary': summary[:500] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'categories': categories or ['general'],
                'tags': article.get('tags', []),
                'feed_source': article.get('feed_source', ''),
                'is_review': article.get('feed_source') == 'reviews',
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _generate_analytics(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate analytics from articles"""
        total = len(articles)
        if total == 0:
            return {}

        return {
            'total_articles': total,
            'reviews_count': sum(1 for a in articles if a.get('is_review')),
            'sentiment_breakdown': {
                'positive': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'positive'),
                'negative': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'negative'),
                'neutral': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'neutral'),
            },
            'category_distribution': self._count_categories(articles),
        }

    def _count_categories(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count articles per category"""
        counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _extract_trending_topics(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics"""
        topic_counts = {}
        for article in articles:
            for cat in article.get('categories', []):
                topic_counts[cat] = topic_counts.get(cat, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'topic': t, 'count': c} for t, c in sorted_topics[:10]]

    def _platform_breakdown(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Break down articles by gaming platform"""
        platforms = {'playstation': 0, 'xbox': 0, 'nintendo': 0, 'pc': 0, 'mobile': 0}
        for article in articles:
            for cat in article.get('categories', []):
                if cat in platforms:
                    platforms[cat] += 1
        return platforms

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['gaming', 'video games', 'playstation', 'xbox', 'nintendo', 'pc gaming']
