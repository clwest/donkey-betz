"""
Notion Spider - Templates & Productivity Tools Intelligence
==============================================================

Session 218: Specialized spider for Notion ecosystem.
Focuses on templates, productivity tools, and workspace trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class NotionSpider(BaseIntelligenceSpider):
    """Notion spider - templates and productivity tools intelligence"""

    RSS_FEEDS = {
        'notion_blog': 'https://www.notion.so/blog/rss',
        'productivity_tips': 'https://www.makeuseof.com/feed/',
        'tool_finder': 'https://www.toolfinder.co/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.template_types = {
            'project_management': ['project', 'task', 'kanban', 'roadmap', 'sprint'],
            'personal': ['journal', 'habit', 'goal', 'life', 'personal'],
            'business': ['crm', 'sales', 'invoice', 'client', 'business'],
            'content': ['content', 'calendar', 'editorial', 'blog', 'social'],
            'education': ['student', 'notes', 'course', 'study', 'research'],
            'finance': ['budget', 'finance', 'expense', 'investment', 'tracker'],
        }

        self.productivity_topics = {
            'organization': ['organize', 'structure', 'system', 'workflow', 'process'],
            'automation': ['automation', 'api', 'integration', 'zapier', 'connect'],
            'collaboration': ['team', 'share', 'collaborate', 'workspace', 'together'],
            'database': ['database', 'relation', 'property', 'view', 'filter'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Notion ecosystem data"""
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

            return {'items': all_items, 'source': 'notion'}

        except Exception as e:
            self.logger.error(f"Error fetching Notion data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Notion ecosystem data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for Notion/productivity relevant content
            notion_items = [i for i in processed_items if i.get('is_notion_relevant')]

            insights = self._generate_insights(notion_items)

            content = {
                'items': notion_items,
                'insights': insights,
                'by_template_type': self._group_by_type(notion_items),
                'productivity_focus': self._analyze_productivity(notion_items),
                'trending_templates': self._extract_trending(notion_items),
            }

            quality_score = min(1.0, len(notion_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='notion.so',
                data_type='productivity_tools',
                content=content,
                metadata={
                    'item_count': len(notion_items),
                    'source': 'notion',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['notion', 'templates', 'productivity', 'workspace', 'organization'],
                target_agents=['productivity_agent', 'template_agent', 'organization_agent'],
                target_advisors=['productivity_expert', 'workspace_designer']
            )

        except Exception as e:
            self.logger.error(f"Error processing Notion data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if Notion/productivity relevant
            notion_keywords = ['notion', 'template', 'productivity', 'workspace', 'database',
                              'organize', 'workflow', 'second brain', 'pkm']
            is_notion_relevant = any(kw in text for kw in notion_keywords)

            # Identify template type
            template_type = 'general'
            for ttype, keywords in self.template_types.items():
                if any(kw in text for kw in keywords):
                    template_type = ttype
                    break

            # Identify productivity topics
            topics = []
            for topic, keywords in self.productivity_topics.items():
                if any(kw in text for kw in keywords):
                    topics.append(topic)

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'template_type': template_type,
                'productivity_topics': topics,
                'is_notion_relevant': is_notion_relevant,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate productivity tools insights"""
        if not items:
            return {}

        type_counts = {}
        for item in items:
            ttype = item.get('template_type', 'general')
            type_counts[ttype] = type_counts.get(ttype, 0) + 1

        topic_counts = {}
        for item in items:
            for topic in item.get('productivity_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return {
            'total_items': len(items),
            'top_template_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'productivity_focus': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'productivity_pulse': 'organized' if len(items) > 10 else 'growing',
        }

    def _group_by_type(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by template type"""
        groups = {}
        for item in items:
            ttype = item.get('template_type', 'general')
            if ttype not in groups:
                groups[ttype] = []
            groups[ttype].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_productivity(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze productivity topic distribution"""
        topic_counts = {}
        for item in items:
            for topic in item.get('productivity_topics', []):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        return dict(sorted(topic_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending templates/tools"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'type': i.get('template_type'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['notion', 'template', 'productivity', 'workspace', 'database', 'organize']
