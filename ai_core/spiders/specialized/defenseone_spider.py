"""
Defense One Spider - Defense Tech & Government Contract Intelligence
=====================================================================

Session 495: Added for defense tech sector coverage.
Covers defense startups, government contracts, Pentagon, DoD, aerospace.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class DefenseOneSpider(BaseIntelligenceSpider):
    """Defense One spider - defense tech, government, and aerospace news"""

    RSS_FEEDS = {
        'main': 'https://www.defenseone.com/rss/all/',
        'technology': 'https://www.defenseone.com/rss/technology/',
        'business': 'https://www.defenseone.com/rss/business/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.categories = {
            'defense_tech': ['defense tech', 'military technology', 'weapons', 'drones', 'autonomous', 'ai military'],
            'contracts': ['contract', 'award', 'procurement', 'rfp', 'bid', 'pentagon contract'],
            'cybersecurity': ['cyber', 'cybersecurity', 'hack', 'breach', 'cyber command', 'nsa'],
            'aerospace': ['aerospace', 'space', 'satellite', 'rocket', 'spacecraft', 'launch'],
            'ai_defense': ['ai', 'artificial intelligence', 'machine learning', 'autonomous systems'],
            'dod': ['pentagon', 'dod', 'department of defense', 'military', 'army', 'navy', 'air force'],
            'startups': ['startup', 'venture', 'funding', 'raises', 'series'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Defense One"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', entry.get('description', '')),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Defense One'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'defenseone'}

        except Exception as e:
            self.logger.error(f"Error fetching Defense One data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Defense One articles"""
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
                'defense_tech_news': [a for a in processed_articles if 'defense_tech' in a.get('categories', [])],
                'contract_awards': [a for a in processed_articles if 'contracts' in a.get('categories', [])],
                'cyber_news': [a for a in processed_articles if 'cybersecurity' in a.get('categories', [])],
                'startup_mentions': [a for a in processed_articles if 'startups' in a.get('categories', [])],
                'trending_topics': self._extract_trending_topics(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='defenseone.com',
                data_type='defense_tech_news',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'defenseone',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['defense', 'military', 'government', 'aerospace', 'cybersecurity', 'contracts'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['defense_analyst', 'government_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Defense One data: {e}")
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
                'is_defense_tech': 'defense_tech' in categories,
                'is_contract_news': 'contracts' in categories,
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
            'defense_tech_count': sum(1 for a in articles if a.get('is_defense_tech')),
            'contract_news_count': sum(1 for a in articles if a.get('is_contract_news')),
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
        return ['defense', 'military', 'pentagon', 'contract', 'aerospace', 'cyber', 'dod']
