"""
Smashing Magazine Spider - Web Design & Development
===================================================

Session 343: Phase 1 Spider Expansion
Smashing Magazine provides web design and development content via free RSS.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SmashingMagazineSpider(BaseIntelligenceSpider):
    """Smashing Magazine spider - web design and front-end development"""

    RSS_FEEDS = {
        'main': 'https://www.smashingmagazine.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.web_categories = {
            'css': ['css', 'flexbox', 'grid', 'animation', 'responsive', 'tailwind'],
            'javascript': ['javascript', 'js', 'react', 'vue', 'angular', 'svelte', 'typescript'],
            'ux': ['ux', 'user experience', 'usability', 'accessibility', 'a11y'],
            'design': ['design', 'ui', 'interface', 'layout', 'typography', 'color'],
            'performance': ['performance', 'speed', 'optimization', 'core web vitals', 'lazy load'],
            'tools': ['webpack', 'vite', 'npm', 'git', 'figma', 'sketch'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Smashing Magazine"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Smashing Magazine'),
                                'tags': [tag.term for tag in entry.get('tags', [])],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'smashingmagazine'}

        except Exception as e:
            self.logger.error(f"Error fetching Smashing Magazine data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Smashing Magazine articles"""
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
                'tech_stack_trends': self._extract_tech_trends(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 20 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='smashingmagazine.com',
                data_type='web_development',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'smashingmagazine',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['web development', 'css', 'javascript', 'design', 'ux'],
                target_agents=['research_agent', 'trend_analysis_agent'],
                target_advisors=['web_dev_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Smashing Magazine data: {e}")
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
            for cat, keywords in self.web_categories.items():
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
            for tag in article.get('tags', []):
                topic_counts[tag] = topic_counts.get(tag, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'topic': t, 'count': c} for t, c in sorted_topics[:10]]

    def _extract_tech_trends(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract technology stack trends"""
        tech_counts = {cat: 0 for cat in self.web_categories.keys()}
        for article in articles:
            for cat in article.get('categories', []):
                if cat in tech_counts:
                    tech_counts[cat] += 1
        return tech_counts

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['web development', 'css', 'javascript', 'react', 'design', 'ux']
