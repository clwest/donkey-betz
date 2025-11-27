"""
Dev.to Spider - Developer Community & Content Intelligence
============================================================

Session 218: Specialized spider for Dev.to developer community.
Focuses on developer articles, tutorials, and tech discussions.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class DevToSpider(BaseIntelligenceSpider):
    """Dev.to spider - developer community and content intelligence"""

    # Dev.to RSS feeds
    RSS_FEEDS = {
        'top': 'https://dev.to/feed',
        'javascript': 'https://dev.to/feed/tag/javascript',
        'python': 'https://dev.to/feed/tag/python',
        'webdev': 'https://dev.to/feed/tag/webdev',
        'beginners': 'https://dev.to/feed/tag/beginners',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.dev_topics = {
            'javascript': ['javascript', 'js', 'typescript', 'node', 'react', 'vue', 'angular'],
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'webdev': ['web development', 'html', 'css', 'frontend', 'backend', 'fullstack'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd', 'aws', 'cloud'],
            'career': ['career', 'job', 'interview', 'resume', 'hiring', 'remote work'],
            'tutorial': ['tutorial', 'how to', 'guide', 'learn', 'beginner'],
            'ai_ml': ['machine learning', 'ai', 'data science', 'neural', 'tensorflow'],
            'productivity': ['productivity', 'tips', 'workflow', 'tools', 'efficiency'],
        }

        self.content_types = {
            'tutorial': ['tutorial', 'how to', 'step by step', 'guide', 'walkthrough'],
            'discussion': ['thoughts on', 'opinion', 'debate', 'unpopular'],
            'showoff': ['built', 'created', 'made', 'launched', 'introducing'],
            'tips': ['tips', 'tricks', 'hacks', 'shortcuts'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Dev.to data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:15]:
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

            return {'items': all_items, 'source': 'devto'}

        except Exception as e:
            self.logger.error(f"Error fetching Dev.to data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Dev.to data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_devto_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_topic': self._group_by_topic(processed_items),
                'tutorials': self._extract_tutorials(processed_items),
                'trending_tags': self._analyze_tags(processed_items),
                'top_authors': self._extract_top_authors(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 30 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='dev.to',
                data_type='developer_community',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'devto',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['developer', 'programming', 'tutorials', 'webdev', 'community'],
                target_agents=['developer_agent', 'learning_agent', 'career_agent'],
                target_advisors=['tech_mentor', 'career_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Dev.to data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()
            tags = item.get('tags', [])

            # Identify dev topic
            topic = 'general'
            for top, keywords in self.dev_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify content type
            content_type = 'article'
            for ctype, keywords in self.content_types.items():
                if any(kw in text for kw in keywords):
                    content_type = ctype
                    break

            # Check for beginner-friendly content
            is_beginner = any(word in text for word in ['beginner', 'getting started', 'introduction', 'basics'])

            # Sentiment
            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'author': item.get('author', ''),
                'tags': tags,
                'topic': topic,
                'content_type': content_type,
                'is_tutorial': content_type == 'tutorial',
                'is_beginner': is_beginner,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_devto_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Dev.to insights"""
        if not items:
            return {}

        tutorials = [i for i in items if i.get('is_tutorial')]
        beginner = [i for i in items if i.get('is_beginner')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'tutorials_count': len(tutorials),
            'beginner_friendly': len(beginner),
            'hot_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'community_focus': 'learning' if len(tutorials) > len(items) // 3 else 'diverse',
        }

    def _group_by_topic(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by dev topic"""
        groups = {}
        for item in items:
            topic = item.get('topic', 'general')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append({
                'title': item.get('title'),
                'author': item.get('author'),
                'link': item.get('link'),
            })
        return groups

    def _extract_tutorials(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tutorial content"""
        tutorials = []
        for item in items:
            if item.get('is_tutorial'):
                tutorials.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'author': item.get('author'),
                    'is_beginner': item.get('is_beginner'),
                    'link': item.get('link'),
                })
        return tutorials[:8]

    def _analyze_tags(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze trending tags"""
        tag_counts = {}
        for item in items:
            for tag in item.get('tags', []):
                tag = tag.lower()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10])

    def _extract_top_authors(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract top authors"""
        author_counts = {}
        for item in items:
            author = item.get('author', 'Unknown')
            if author not in author_counts:
                author_counts[author] = {'count': 0, 'articles': []}
            author_counts[author]['count'] += 1
            if len(author_counts[author]['articles']) < 2:
                author_counts[author]['articles'].append(item.get('title'))

        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1]['count'], reverse=True)
        return [{'name': a[0], **a[1]} for a in sorted_authors[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['dev.to', 'developer', 'programming', 'tutorial', 'webdev', 'javascript']
