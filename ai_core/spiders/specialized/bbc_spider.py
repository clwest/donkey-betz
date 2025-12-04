"""
BBC Spider - BBC World News Intelligence
=========================================

Session 343: Phase 1 Spider Expansion
BBC provides comprehensive international news coverage via free RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class BBCSpider(BaseIntelligenceSpider):
    """BBC news spider - international news coverage"""

    RSS_FEEDS = {
        'top_stories': 'https://feeds.bbci.co.uk/news/rss.xml',
        'world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'business': 'https://feeds.bbci.co.uk/news/business/rss.xml',
        'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
        'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        'entertainment': 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
        'health': 'https://feeds.bbci.co.uk/news/health/rss.xml',
        'us_canada': 'https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        'europe': 'https://feeds.bbci.co.uk/news/world/europe/rss.xml',
        'asia': 'https://feeds.bbci.co.uk/news/world/asia/rss.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.topic_categories = {
            'technology': ['tech', 'software', 'ai', 'computer', 'digital', 'cyber', 'robot'],
            'business': ['economy', 'market', 'company', 'industry', 'trade', 'finance', 'bank'],
            'politics': ['government', 'minister', 'election', 'vote', 'parliament', 'policy'],
            'science': ['research', 'study', 'scientist', 'discovery', 'space', 'climate', 'nasa'],
            'health': ['health', 'medical', 'nhs', 'hospital', 'disease', 'vaccine', 'covid'],
            'international': ['ukraine', 'russia', 'china', 'us', 'eu', 'un', 'nato'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from BBC"""
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
                                'author': 'BBC News',
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'bbc'}

        except Exception as e:
            self.logger.error(f"Error fetching BBC data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process BBC articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            analytics = self._generate_analytics(processed_articles)

            content = {
                'articles': processed_articles,
                'analytics': analytics,
                'trending_topics': self._extract_trending_topics(processed_articles),
                'international_focus': self._extract_international_news(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 50 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='bbc.co.uk',
                data_type='news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'bbc',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['news', 'world', 'business', 'technology', 'health', 'international'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['news_analyst', 'global_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing BBC data: {e}")
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
            for cat, keywords in self.topic_categories.items():
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
                'feed_source': article.get('feed_source', ''),
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

    def _extract_international_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract international news articles"""
        intl_news = []
        for article in articles:
            if 'international' in article.get('categories', []) or article.get('feed_source') in ['world', 'us_canada', 'europe', 'asia']:
                intl_news.append({
                    'title': article.get('title'),
                    'region': article.get('feed_source'),
                    'link': article.get('link'),
                })
        return intl_news[:15]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['news', 'world', 'business', 'technology', 'health', 'international']
