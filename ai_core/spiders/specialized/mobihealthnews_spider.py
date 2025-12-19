"""
MobiHealthNews Spider - Healthtech & Digital Health Intelligence
=================================================================

Session 495: Added for healthtech sector coverage.
Covers digital health, biotech, medtech, FDA, clinical trials, telehealth.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class MobiHealthNewsSpider(BaseIntelligenceSpider):
    """MobiHealthNews spider - digital health and healthtech news"""

    RSS_FEEDS = {
        'main': 'https://www.mobihealthnews.com/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.categories = {
            'digital_health': ['digital health', 'health tech', 'healthtech', 'mhealth', 'mobile health'],
            'telehealth': ['telehealth', 'telemedicine', 'virtual care', 'remote patient', 'video visit'],
            'ai_health': ['ai', 'artificial intelligence', 'machine learning', 'diagnostic', 'clinical decision'],
            'wearables': ['wearable', 'fitness tracker', 'smartwatch', 'continuous monitoring', 'sensor'],
            'biotech': ['biotech', 'biotechnology', 'genomics', 'gene therapy', 'crispr'],
            'medtech': ['medtech', 'medical device', 'fda approval', 'fda clearance', '510k'],
            'funding': ['funding', 'raises', 'series', 'investment', 'venture', 'ipo'],
            'clinical': ['clinical trial', 'fda', 'clinical study', 'regulatory', 'approval'],
            'mental_health': ['mental health', 'behavioral health', 'therapy', 'psychiatry', 'wellness'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from MobiHealthNews"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:25]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'MobiHealthNews'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'mobihealthnews'}

        except Exception as e:
            self.logger.error(f"Error fetching MobiHealthNews data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process MobiHealthNews articles"""
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
                'digital_health_news': [a for a in processed_articles if 'digital_health' in a.get('categories', [])],
                'telehealth_updates': [a for a in processed_articles if 'telehealth' in a.get('categories', [])],
                'ai_health_news': [a for a in processed_articles if 'ai_health' in a.get('categories', [])],
                'funding_rounds': [a for a in processed_articles if 'funding' in a.get('categories', [])],
                'fda_news': [a for a in processed_articles if 'clinical' in a.get('categories', [])],
                'trending_topics': self._extract_trending_topics(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 20 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='mobihealthnews.com',
                data_type='healthtech_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'mobihealthnews',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['healthtech', 'digital health', 'biotech', 'medtech', 'telehealth', 'FDA'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['health_strategist', 'biotech_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing MobiHealthNews data: {e}")
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
            for cat, keywords in self.categories.items():
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
                'feed_source': article.get('feed_source', 'main'),
                'is_funding_news': 'funding' in categories,
                'is_fda_news': 'clinical' in categories,
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
            'funding_news_count': sum(1 for a in articles if a.get('is_funding_news')),
            'fda_news_count': sum(1 for a in articles if a.get('is_fda_news')),
            'category_distribution': self._count_categories(articles),
            'sentiment_breakdown': {
                'positive': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'positive'),
                'negative': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'negative'),
                'neutral': sum(1 for a in articles if a.get('sentiment', {}).get('classification') == 'neutral'),
            },
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

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['healthtech', 'digital health', 'telehealth', 'biotech', 'medtech', 'fda', 'clinical']
