"""
Wired Spider - Tech Culture & Future Trends Intelligence
========================================================

Session 218: Specialized spider for Wired magazine.
Focuses on tech culture, future trends, and in-depth tech stories.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class WiredSpider(BaseIntelligenceSpider):
    """Wired magazine spider - tech culture, trends, and deep stories"""

    # RSS Feed URLs
    RSS_FEEDS = {
        'main': 'https://www.wired.com/feed/rss',
        'business': 'https://www.wired.com/feed/category/business/latest/rss',
        'gear': 'https://www.wired.com/feed/category/gear/latest/rss',
        'science': 'https://www.wired.com/feed/category/science/latest/rss',
        'security': 'https://www.wired.com/feed/category/security/latest/rss',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.topic_categories = {
            'ai_future': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'future of ai', 'machine learning'],
            'cybersecurity': ['security', 'hacker', 'breach', 'privacy', 'encryption', 'cyberattack', 'ransomware'],
            'culture': ['culture', 'social media', 'internet', 'digital life', 'online', 'community'],
            'gadgets': ['gadget', 'device', 'gear', 'review', 'best', 'wired recommends'],
            'science': ['science', 'physics', 'biology', 'space', 'climate', 'discovery'],
            'business': ['business', 'startup', 'company', 'silicon valley', 'tech industry', 'ceo'],
            'transportation': ['car', 'ev', 'tesla', 'autonomous', 'transportation', 'self-driving'],
            'environment': ['climate', 'sustainability', 'environment', 'renewable', 'green'],
        }

        self.story_types = {
            'longform': ['deep dive', 'investigation', 'inside', 'exclusive', 'the untold'],
            'review': ['review', 'hands-on', 'tested', 'wired recommends', 'best'],
            'analysis': ['why', 'how', 'what it means', 'explained', 'the future of'],
            'news': ['breaking', 'announces', 'launches', 'just', 'new'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch RSS feeds from Wired"""
        try:
            all_articles = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:12]:
                            # Extract content
                            content = ''
                            if hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].get('value', '')
                            elif hasattr(entry, 'summary'):
                                content = entry.summary
                            elif hasattr(entry, 'description'):
                                content = entry.description

                            article = {
                                'title': entry.get('title', ''),
                                'summary': content[:500] if content else '',
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'author': entry.get('author', 'Wired'),
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                                'feed_source': feed_name,
                            }
                            if article['title']:
                                all_articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'articles': all_articles, 'source': 'wired'}

        except Exception as e:
            self.logger.error(f"Error fetching Wired data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Wired articles"""
        try:
            articles = raw_data.get('articles', [])
            processed_articles = []

            for article in articles:
                processed = self._process_article(article)
                if processed:
                    processed_articles.append(processed)

            # Generate culture & trends insights
            insights = self._generate_culture_insights(processed_articles)

            content = {
                'articles': processed_articles,
                'insights': insights,
                'longform_stories': self._extract_longform(processed_articles),
                'topic_coverage': self._analyze_topic_coverage(processed_articles),
                'security_alerts': self._extract_security_news(processed_articles),
                'gear_reviews': self._extract_gear_reviews(processed_articles),
                'future_trends': self._identify_future_trends(processed_articles),
            }

            quality_score = min(1.0, len(processed_articles) / 25 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='wired.com',
                data_type='tech_culture',
                content=content,
                metadata={
                    'article_count': len(processed_articles),
                    'source': 'wired',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                    'longform_count': len([a for a in processed_articles if a.get('story_type') == 'longform']),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['tech_culture', 'trends', 'security', 'gadgets', 'future'],
                target_agents=['research_agent', 'trend_analysis_agent', 'culture_agent'],
                target_advisors=['culture_analyst', 'security_advisor', 'trend_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Wired data: {e}")
            return None

    def _process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual article"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}".lower()

            # Sentiment analysis
            blob = TextBlob(f"{title} {summary}")
            sentiment = {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity,
                'tone': 'positive' if blob.sentiment.polarity > 0.15 else 'critical' if blob.sentiment.polarity < -0.15 else 'neutral'
            }

            # Identify topics
            topics = []
            for topic, keywords in self.topic_categories.items():
                if any(kw in text for kw in keywords):
                    topics.append(topic)

            # Determine story type
            story_type = 'news'
            for stype, keywords in self.story_types.items():
                if any(kw in text for kw in keywords):
                    story_type = stype
                    break

            # Check for specific content types
            is_security_related = 'cybersecurity' in topics
            is_review = story_type == 'review' or 'gear' in article.get('feed_source', '')
            is_longform = story_type == 'longform'
            is_future_focused = any(word in text for word in ['future', 'will', 'next', 'coming', '2025', '2026'])

            return {
                'title': title,
                'summary': summary[:400] if summary else '',
                'link': article.get('link', ''),
                'published': article.get('published', ''),
                'author': article.get('author', ''),
                'sentiment': sentiment,
                'topics': topics or ['general'],
                'story_type': story_type,
                'is_security_related': is_security_related,
                'is_review': is_review,
                'is_longform': is_longform,
                'is_future_focused': is_future_focused,
                'tags': article.get('tags', []),
                'feed_source': article.get('feed_source', ''),
            }

        except Exception as e:
            self.logger.warning(f"Error processing article: {e}")
            return None

    def _generate_culture_insights(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate tech culture insights"""
        if not articles:
            return {}

        longform = [a for a in articles if a.get('is_longform')]
        security = [a for a in articles if a.get('is_security_related')]
        future = [a for a in articles if a.get('is_future_focused')]

        # Count topics
        topic_counts = {}
        for article in articles:
            for topic in article.get('topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        hot_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_articles': len(articles),
            'longform_count': len(longform),
            'security_coverage': len(security),
            'future_focused': len(future),
            'hot_topics': [t[0] for t in hot_topics],
            'content_mood': self._assess_content_mood(articles),
            'trend_direction': 'future-looking' if len(future) > len(articles) // 3 else 'present-focused',
        }

    def _assess_content_mood(self, articles: List[Dict[str, Any]]) -> str:
        """Assess the overall content mood"""
        if not articles:
            return 'neutral'

        positive = sum(1 for a in articles if a.get('sentiment', {}).get('tone') == 'positive')
        critical = sum(1 for a in articles if a.get('sentiment', {}).get('tone') == 'critical')

        if positive > critical * 1.5:
            return 'optimistic'
        elif critical > positive * 1.5:
            return 'critical'
        return 'balanced'

    def _extract_longform(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract longform stories"""
        longform = []
        for article in articles:
            if article.get('is_longform') or article.get('story_type') == 'longform':
                longform.append({
                    'title': article.get('title'),
                    'topics': article.get('topics'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return longform[:5]

    def _analyze_topic_coverage(self, articles: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze coverage by topic"""
        coverage = {}

        for article in articles:
            for topic in article.get('topics', ['general']):
                if topic not in coverage:
                    coverage[topic] = {'count': 0, 'sentiment_sum': 0, 'articles': []}
                coverage[topic]['count'] += 1
                coverage[topic]['sentiment_sum'] += article.get('sentiment', {}).get('polarity', 0)
                if len(coverage[topic]['articles']) < 2:
                    coverage[topic]['articles'].append(article.get('title'))

        # Calculate averages
        for topic in coverage:
            if coverage[topic]['count'] > 0:
                coverage[topic]['avg_sentiment'] = round(coverage[topic]['sentiment_sum'] / coverage[topic]['count'], 2)
            del coverage[topic]['sentiment_sum']

        return coverage

    def _extract_security_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract security-related news"""
        security = []
        for article in articles:
            if article.get('is_security_related'):
                security.append({
                    'title': article.get('title'),
                    'summary': article.get('summary', '')[:200],
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return security[:5]

    def _extract_gear_reviews(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract gear/product reviews"""
        reviews = []
        for article in articles:
            if article.get('is_review'):
                reviews.append({
                    'title': article.get('title'),
                    'topics': article.get('topics'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return reviews[:8]

    def _identify_future_trends(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify future-focused trends"""
        trends = []
        for article in articles:
            if article.get('is_future_focused'):
                trends.append({
                    'title': article.get('title'),
                    'topics': article.get('topics'),
                    'sentiment': article.get('sentiment', {}).get('tone'),
                    'link': article.get('link'),
                })
        return trends[:8]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['tech', 'culture', 'future', 'security', 'gadget', 'innovation']
