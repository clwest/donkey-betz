"""
ConvertKit Spider - Creator Economy & Email Marketing Intelligence
=====================================================================

Session 218: Specialized spider for ConvertKit creator platform.
Focuses on creator economy, email marketing, and audience building.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ConvertKitSpider(BaseIntelligenceSpider):
    """ConvertKit spider - creator economy and email marketing intelligence"""

    RSS_FEEDS = {
        'convertkit_blog': 'https://convertkit.com/blog/feed',
        'creator_science': 'https://creatorscience.com/feed/',
        'newsletter_crew': 'https://newslettercrew.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.creator_topics = {
            'email': ['email', 'newsletter', 'subscriber', 'list', 'broadcast'],
            'audience': ['audience', 'community', 'followers', 'fans', 'grow'],
            'monetization': ['monetization', 'revenue', 'income', 'paid', 'sponsorship'],
            'content': ['content', 'blog', 'podcast', 'video', 'course'],
            'automation': ['automation', 'sequence', 'funnel', 'workflow', 'drip'],
            'landing_pages': ['landing page', 'opt-in', 'lead magnet', 'freebie', 'form'],
        }

        self.creator_types = {
            'writer': ['writer', 'author', 'blogger', 'newsletter', 'substack'],
            'podcaster': ['podcast', 'audio', 'episode', 'interview', 'host'],
            'educator': ['educator', 'teacher', 'course', 'coach', 'mentor'],
            'artist': ['artist', 'creator', 'maker', 'designer', 'illustrator'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch ConvertKit ecosystem data"""
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
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'convertkit'}

        except Exception as e:
            self.logger.error(f"Error fetching ConvertKit data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process ConvertKit ecosystem data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_topic': self._group_by_topic(processed_items),
                'creator_types': self._analyze_creator_types(processed_items),
                'trending_strategies': self._extract_strategies(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='convertkit.com',
                data_type='creator_economy',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'convertkit',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['convertkit', 'email marketing', 'creator economy', 'newsletter', 'audience'],
                target_agents=['creator_agent', 'marketing_agent', 'newsletter_agent'],
                target_advisors=['creator_economy_advisor', 'email_marketing_expert']
            )

        except Exception as e:
            self.logger.error(f"Error processing ConvertKit data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify creator topic
            topic = 'general'
            for top, keywords in self.creator_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify creator type focus
            creator_type = None
            for ctype, keywords in self.creator_types.items():
                if any(kw in text for kw in keywords):
                    creator_type = ctype
                    break

            # Check if email/newsletter focused
            is_email_focused = any(word in text for word in ['email', 'newsletter', 'subscriber', 'list'])

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'topic': topic,
                'creator_type': creator_type,
                'is_email_focused': is_email_focused,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate creator economy insights"""
        if not items:
            return {}

        email_items = [i for i in items if i.get('is_email_focused')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        type_counts = {}
        for item in items:
            ctype = item.get('creator_type')
            if ctype:
                type_counts[ctype] = type_counts.get(ctype, 0) + 1

        return {
            'total_items': len(items),
            'email_focused': len(email_items),
            'top_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'creator_types': type_counts,
            'creator_pulse': 'thriving' if len(email_items) > 5 else 'growing',
        }

    def _group_by_topic(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by creator topic"""
        groups = {}
        for item in items:
            topic = item.get('topic', 'general')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_creator_types(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze creator type distribution"""
        type_counts = {}
        for item in items:
            ctype = item.get('creator_type')
            if ctype:
                type_counts[ctype] = type_counts.get(ctype, 0) + 1
        return dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_strategies(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending creator strategies"""
        email_items = [i for i in items if i.get('is_email_focused')]
        sorted_items = sorted(email_items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'topic': i.get('topic'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['convertkit', 'email', 'newsletter', 'creator', 'subscriber', 'audience']
