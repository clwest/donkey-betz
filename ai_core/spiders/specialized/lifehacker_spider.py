"""
Lifehacker Spider - Productivity & Life Tips
============================================

Session 343: Phase 1 Spider Expansion
Lifehacker provides productivity and lifestyle tips via free RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class LifehackerSpider(BaseIntelligenceSpider):
    """Lifehacker spider - productivity tips and life hacks"""

    RSS_FEEDS = {
        'main': 'https://lifehacker.com/rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.topic_categories = {
            'productivity': ['productivity', 'efficiency', 'workflow', 'time management', 'organize'],
            'tech': ['tech', 'app', 'software', 'tool', 'device', 'gadget'],
            'money': ['money', 'finance', 'budget', 'save', 'invest', 'credit', 'debt'],
            'health': ['health', 'fitness', 'exercise', 'diet', 'sleep', 'mental health'],
            'work': ['work', 'career', 'job', 'office', 'remote', 'interview'],
            'home': ['home', 'cleaning', 'cooking', 'diy', 'kitchen', 'garden'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Lifehacker"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:25]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Lifehacker'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'lifehacker'}

        except Exception as e:
            self.logger.error(f"Error fetching Lifehacker data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Lifehacker articles"""
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
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='lifehacker.com',
                data_type='lifestyle',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'lifehacker',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['productivity', 'lifestyle', 'tech', 'money', 'health'],
                target_agents=['research_agent', 'content_strategy_agent'],
                target_advisors=['lifestyle_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing Lifehacker data: {e}")
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
                'tags': article.get('tags', []),
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

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['productivity', 'lifestyle', 'tech', 'money', 'health', 'tips']
