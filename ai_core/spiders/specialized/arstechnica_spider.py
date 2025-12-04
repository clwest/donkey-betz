"""
Ars Technica Spider - In-depth Technology News
==============================================

Session 343: Phase 1 Spider Expansion
Ars Technica provides detailed tech analysis via free RSS feeds.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ArsTechnicaSpider(BaseIntelligenceSpider):
    """Ars Technica spider - in-depth technology news and analysis"""

    RSS_FEEDS = {
        'main': 'https://feeds.arstechnica.com/arstechnica/index',
        'tech_policy': 'https://feeds.arstechnica.com/arstechnica/tech-policy',
        'gadgets': 'https://feeds.arstechnica.com/arstechnica/gadgets',
        'science': 'https://feeds.arstechnica.com/arstechnica/science',
        'gaming': 'https://feeds.arstechnica.com/arstechnica/gaming',
        'cars': 'https://feeds.arstechnica.com/arstechnica/cars',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.tech_categories = {
            'ai_ml': ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm', 'neural'],
            'security': ['security', 'hack', 'vulnerability', 'malware', 'breach', 'ransomware'],
            'hardware': ['cpu', 'gpu', 'chip', 'processor', 'nvidia', 'amd', 'intel', 'apple silicon'],
            'software': ['software', 'app', 'update', 'release', 'bug', 'patch'],
            'gaming': ['game', 'gaming', 'playstation', 'xbox', 'nintendo', 'steam'],
            'space': ['nasa', 'spacex', 'rocket', 'satellite', 'mars', 'moon', 'orbit'],
            'ev': ['ev', 'electric vehicle', 'tesla', 'battery', 'charging'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Ars Technica"""
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
                                'author': entry.get('author', 'Ars Technica'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'arstechnica'}

        except Exception as e:
            self.logger.error(f"Error fetching Ars Technica data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Ars Technica articles"""
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

            quality_score = min(1.0, len(processed_articles) / 40 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='arstechnica.com',
                data_type='tech_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'arstechnica',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['tech', 'security', 'hardware', 'science', 'gaming'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['tech_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Ars Technica data: {e}")
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
            for cat, keywords in self.tech_categories.items():
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

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['tech', 'security', 'hardware', 'gaming', 'science', 'policy']
