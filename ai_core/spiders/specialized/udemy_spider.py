"""
Udemy Spider - Online Learning Marketplace Intelligence
=========================================================

Session 218: Specialized spider for Udemy course marketplace.
Focuses on course trends, pricing strategies, and learning demands.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class UdemySpider(BaseIntelligenceSpider):
    """Udemy spider - online course marketplace intelligence"""

    # E-learning industry RSS feeds
    RSS_FEEDS = {
        'elearning_industry': 'https://elearningindustry.com/feed',
        'learning_tech': 'https://www.learningtechnologies.co.uk/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.course_topics = {
            'programming': ['python', 'javascript', 'java', 'programming', 'coding', 'web development'],
            'data_science': ['data science', 'machine learning', 'ai', 'analytics', 'deep learning', 'sql'],
            'business': ['business', 'management', 'project management', 'leadership', 'mba'],
            'marketing': ['digital marketing', 'seo', 'social media', 'content marketing', 'advertising'],
            'design': ['ui/ux', 'graphic design', 'photoshop', 'figma', 'web design'],
            'finance': ['finance', 'accounting', 'investing', 'trading', 'cryptocurrency'],
            'personal_dev': ['productivity', 'communication', 'career', 'public speaking'],
        }

        self.learning_formats = {
            'video': ['video', 'lecture', 'tutorial', 'watch'],
            'interactive': ['interactive', 'hands-on', 'project', 'exercise', 'quiz'],
            'certification': ['certificate', 'certification', 'credential', 'accredited'],
            'bootcamp': ['bootcamp', 'intensive', 'immersive', 'accelerated'],
        }

        self.skill_levels = {
            'beginner': ['beginner', 'introduction', 'fundamentals', 'basics', 'getting started'],
            'intermediate': ['intermediate', 'advanced beginner', 'next level'],
            'advanced': ['advanced', 'expert', 'master', 'professional'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch e-learning industry data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:20]:
                            item = {
                                'title': entry.get('title', ''),
                                'description': entry.get('summary', entry.get('description', ''))[:500],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': feed_name,
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'udemy_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Udemy data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process e-learning data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_learning_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'trending_topics': self._analyze_trending_topics(processed_items),
                'format_trends': self._analyze_formats(processed_items),
                'skill_demand': self._analyze_skill_demand(processed_items),
                'learning_opportunities': self._identify_opportunities(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='udemy.com',
                data_type='learning_marketplace',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'udemy_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['courses', 'e-learning', 'skills', 'training', 'education'],
                target_agents=['education_agent', 'skill_agent', 'career_agent'],
                target_advisors=['learning_advisor', 'skill_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Udemy data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify topic
            topic = 'general'
            for top, keywords in self.course_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify learning format
            formats = []
            for fmt, keywords in self.learning_formats.items():
                if any(kw in text for kw in keywords):
                    formats.append(fmt)

            # Identify skill level
            skill_level = 'all_levels'
            for level, keywords in self.skill_levels.items():
                if any(kw in text for kw in keywords):
                    skill_level = level
                    break

            # Check for trend indicators
            is_trending = any(word in text for word in ['trending', 'popular', 'top', 'best', 'most'])
            is_new = any(word in text for word in ['new', 'latest', 'just released', '2024', '2025'])

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'topic': topic,
                'formats': formats or ['standard'],
                'skill_level': skill_level,
                'is_trending': is_trending,
                'is_new': is_new,
                'sentiment': sentiment,
                'tags': item.get('tags', []),
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_learning_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate learning market insights"""
        if not items:
            return {}

        trending_items = [i for i in items if i.get('is_trending')]
        new_items = [i for i in items if i.get('is_new')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'trending_count': len(trending_items),
            'new_releases': len(new_items),
            'hot_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'learning_pulse': 'high' if len(trending_items) > len(items) // 3 else 'steady',
        }

    def _analyze_trending_topics(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze trending topics"""
        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_formats(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze learning format trends"""
        format_counts = {}
        for item in items:
            for fmt in item.get('formats', []):
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
        return dict(sorted(format_counts.items(), key=lambda x: x[1], reverse=True))

    def _analyze_skill_demand(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze skill level demand"""
        level_counts = {}
        for item in items:
            level = item.get('skill_level', 'all_levels')
            level_counts[level] = level_counts.get(level, 0) + 1
        return level_counts

    def _identify_opportunities(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify learning opportunities"""
        opportunities = []
        for item in items:
            if item.get('is_trending') or item.get('is_new'):
                opportunities.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'skill_level': item.get('skill_level'),
                    'link': item.get('link'),
                })
        return opportunities[:8]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['udemy', 'course', 'learning', 'tutorial', 'training', 'skills']
