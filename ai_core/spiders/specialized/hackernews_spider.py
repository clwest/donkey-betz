"""
Hacker News Spider - Tech Community & Startup Intelligence
===========================================================

Session 218: Specialized spider for Hacker News (Y Combinator).
Focuses on tech discussions, startup news, and developer trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class HackerNewsSpider(BaseIntelligenceSpider):
    """Hacker News spider - tech community and startup intelligence"""

    # HN RSS feeds
    RSS_FEEDS = {
        'front_page': 'https://hnrss.org/frontpage',
        'best': 'https://hnrss.org/best',
        'newest': 'https://hnrss.org/newest?count=30',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.tech_topics = {
            'programming': ['programming', 'code', 'software', 'developer', 'algorithm', 'api'],
            'ai_ml': ['ai', 'machine learning', 'gpt', 'llm', 'neural', 'openai', 'anthropic'],
            'startups': ['startup', 'yc', 'founder', 'funding', 'launch', 'vc', 'seed'],
            'webdev': ['web', 'javascript', 'react', 'frontend', 'backend', 'css', 'html'],
            'devops': ['devops', 'kubernetes', 'docker', 'aws', 'cloud', 'infrastructure'],
            'security': ['security', 'hack', 'vulnerability', 'privacy', 'encryption'],
            'career': ['hiring', 'job', 'career', 'salary', 'interview', 'remote'],
            'open_source': ['open source', 'github', 'oss', 'linux', 'mit license'],
        }

        self.content_types = {
            'show_hn': ['show hn', 'launch'],
            'ask_hn': ['ask hn', 'question'],
            'news': ['announces', 'releases', 'launches'],
            'discussion': ['why', 'how', 'what', 'opinion'],
        }

        self.engagement_signals = {
            'high_engagement': ['comments', 'points', 'upvotes'],
            'controversial': ['debate', 'disagree', 'unpopular'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Hacker News data"""
        try:
            all_items = []

            for feed_name, feed_url in self.RSS_FEEDS.items():
                try:
                    feed = feedparser.parse(feed_url)
                    if feed.entries:
                        for entry in feed.entries[:25]:
                            # Extract points and comments from description
                            description = entry.get('summary', entry.get('description', ''))
                            points = 0
                            comments = 0

                            # HN RSS includes points and comments in description
                            if 'points' in description.lower():
                                try:
                                    import re
                                    points_match = re.search(r'(\d+)\s*points?', description.lower())
                                    if points_match:
                                        points = int(points_match.group(1))
                                    comments_match = re.search(r'(\d+)\s*comments?', description.lower())
                                    if comments_match:
                                        comments = int(comments_match.group(1))
                                except:
                                    pass

                            item = {
                                'title': entry.get('title', ''),
                                'description': description[:500],
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': feed_name,
                                'points': points,
                                'comments': comments,
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'hackernews'}

        except Exception as e:
            self.logger.error(f"Error fetching Hacker News data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Hacker News data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_hn_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_topic': self._group_by_topic(processed_items),
                'trending_topics': self._analyze_trending(processed_items),
                'show_hn': self._extract_show_hn(processed_items),
                'hot_discussions': self._extract_hot_discussions(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 30 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='news.ycombinator.com',
                data_type='tech_community',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'hackernews',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['tech', 'startups', 'programming', 'ycombinator', 'developers'],
                target_agents=['tech_agent', 'startup_agent', 'developer_agent'],
                target_advisors=['tech_advisor', 'startup_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Hacker News data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify tech topic
            topic = 'general'
            for top, keywords in self.tech_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify content type
            content_type = 'news'
            if 'show hn' in text:
                content_type = 'show_hn'
            elif 'ask hn' in text:
                content_type = 'ask_hn'
            elif any(word in text for word in ['why', 'how', 'what do you think']):
                content_type = 'discussion'

            # Calculate engagement level
            points = item.get('points', 0)
            comments = item.get('comments', 0)
            is_hot = points > 100 or comments > 50
            is_trending = points > 50 or comments > 20

            # Sentiment
            blob = TextBlob(title)
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'topic': topic,
                'content_type': content_type,
                'points': points,
                'comments': comments,
                'is_hot': is_hot,
                'is_trending': is_trending,
                'is_show_hn': content_type == 'show_hn',
                'is_ask_hn': content_type == 'ask_hn',
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_hn_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Hacker News insights"""
        if not items:
            return {}

        hot_items = [i for i in items if i.get('is_hot')]
        show_hn = [i for i in items if i.get('is_show_hn')]
        ask_hn = [i for i in items if i.get('is_ask_hn')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        total_points = sum(i.get('points', 0) for i in items)
        total_comments = sum(i.get('comments', 0) for i in items)

        return {
            'total_items': len(items),
            'hot_stories': len(hot_items),
            'show_hn_count': len(show_hn),
            'ask_hn_count': len(ask_hn),
            'total_engagement': total_points + total_comments,
            'hot_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'community_mood': 'active' if len(hot_items) > 5 else 'normal',
        }

    def _group_by_topic(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by tech topic"""
        groups = {}
        for item in items:
            topic = item.get('topic', 'general')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append({
                'title': item.get('title'),
                'points': item.get('points'),
                'comments': item.get('comments'),
                'link': item.get('link'),
            })
        return groups

    def _analyze_trending(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze trending topics"""
        topic_counts = {}
        for item in items:
            if item.get('is_trending'):
                topic = item.get('topic', 'general')
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_show_hn(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract Show HN posts"""
        show_hn = []
        for item in items:
            if item.get('is_show_hn'):
                show_hn.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'points': item.get('points'),
                    'link': item.get('link'),
                })
        return sorted(show_hn, key=lambda x: x.get('points', 0), reverse=True)[:5]

    def _extract_hot_discussions(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract hot discussions"""
        hot = []
        for item in items:
            if item.get('is_hot') or item.get('comments', 0) > 30:
                hot.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'comments': item.get('comments'),
                    'link': item.get('link'),
                })
        return sorted(hot, key=lambda x: x.get('comments', 0), reverse=True)[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['hacker news', 'hn', 'startup', 'programming', 'tech', 'developer']
