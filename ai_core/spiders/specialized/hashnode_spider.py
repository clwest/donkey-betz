"""
Hashnode Spider - Developer Blogging & Knowledge Intelligence
===============================================================

Session 218: Specialized spider for Hashnode developer blogging platform.
Focuses on developer blogs, technical writing, and knowledge sharing.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class HashnodeSpider(BaseIntelligenceSpider):
    """Hashnode spider - developer blogging and knowledge intelligence"""

    # Developer blogging RSS feeds
    RSS_FEEDS = {
        'hashnode_featured': 'https://hashnode.com/rss',
        'coding_horror': 'https://blog.codinghorror.com/rss/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.blog_topics = {
            'web_development': ['web', 'javascript', 'react', 'frontend', 'backend', 'api'],
            'devops': ['devops', 'ci/cd', 'docker', 'kubernetes', 'deployment', 'infrastructure'],
            'programming': ['programming', 'coding', 'algorithm', 'data structure', 'clean code'],
            'career': ['career', 'interview', 'job', 'resume', 'freelance', 'remote'],
            'productivity': ['productivity', 'workflow', 'tools', 'efficiency', 'time management'],
            'open_source': ['open source', 'github', 'contributing', 'community', 'oss'],
            'learning': ['learning', 'study', 'beginner', 'roadmap', 'resources'],
        }

        self.article_types = {
            'tutorial': ['tutorial', 'how to', 'guide', 'step by step', 'walkthrough'],
            'deep_dive': ['deep dive', 'in-depth', 'comprehensive', 'complete guide'],
            'opinion': ['opinion', 'thoughts', 'why i', 'my experience'],
            'comparison': ['vs', 'comparison', 'compared', 'which is better'],
            'list': ['top', 'best', 'list', 'resources', 'tools'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch developer blogging data"""
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
                                'author': entry.get('author', 'Developer'),
                                'tags': [tag.term for tag in entry.get('tags', [])] if hasattr(entry, 'tags') else [],
                                'source': feed_name,
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'hashnode'}

        except Exception as e:
            self.logger.error(f"Error fetching Hashnode data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process developer blogging data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_blog_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_topic': self._group_by_topic(processed_items),
                'deep_dives': self._extract_deep_dives(processed_items),
                'tutorials': self._extract_tutorials(processed_items),
                'trending_topics': self._analyze_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='hashnode.com',
                data_type='developer_blogs',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'hashnode',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['developer', 'blog', 'tutorials', 'knowledge', 'technical writing'],
                target_agents=['developer_agent', 'learning_agent', 'content_agent'],
                target_advisors=['tech_mentor', 'content_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Hashnode data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify blog topic
            topic = 'general'
            for top, keywords in self.blog_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify article type
            article_type = 'article'
            for atype, keywords in self.article_types.items():
                if any(kw in text for kw in keywords):
                    article_type = atype
                    break

            # Sentiment
            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'author': item.get('author', ''),
                'tags': item.get('tags', []),
                'topic': topic,
                'article_type': article_type,
                'is_tutorial': article_type == 'tutorial',
                'is_deep_dive': article_type == 'deep_dive',
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_blog_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate blogging insights"""
        if not items:
            return {}

        tutorials = [i for i in items if i.get('is_tutorial')]
        deep_dives = [i for i in items if i.get('is_deep_dive')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'tutorials_count': len(tutorials),
            'deep_dives_count': len(deep_dives),
            'hot_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'content_quality': 'high' if len(deep_dives) > len(items) // 4 else 'mixed',
        }

    def _group_by_topic(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by blog topic"""
        groups = {}
        for item in items:
            topic = item.get('topic', 'general')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append({
                'title': item.get('title'),
                'author': item.get('author'),
                'article_type': item.get('article_type'),
                'link': item.get('link'),
            })
        return groups

    def _extract_deep_dives(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract deep dive articles"""
        deep_dives = []
        for item in items:
            if item.get('is_deep_dive'):
                deep_dives.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'author': item.get('author'),
                    'link': item.get('link'),
                })
        return deep_dives[:5]

    def _extract_tutorials(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tutorial articles"""
        tutorials = []
        for item in items:
            if item.get('is_tutorial'):
                tutorials.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'author': item.get('author'),
                    'link': item.get('link'),
                })
        return tutorials[:8]

    def _analyze_trending(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze trending topics"""
        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['hashnode', 'developer', 'blog', 'tutorial', 'technical', 'programming']
