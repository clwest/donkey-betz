"""
Teachable Spider - Online Course & Creator Economy Intelligence
================================================================

Session 218: Specialized spider for Teachable and online course ecosystem.
Focuses on course creation trends, pricing, and creator opportunities.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class TeachableSpider(BaseIntelligenceSpider):
    """Teachable spider - online course and creator economy intelligence"""

    # Course creation and creator economy RSS feeds
    RSS_FEEDS = {
        'teachable_blog': 'https://teachable.com/blog/feed',
        'coursecreator': 'https://www.onlinecoursehow.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.course_categories = {
            'business': ['business', 'entrepreneurship', 'marketing', 'sales', 'startup'],
            'tech': ['programming', 'coding', 'web development', 'software', 'tech', 'ai', 'data'],
            'creative': ['design', 'photography', 'video', 'music', 'art', 'writing'],
            'health': ['health', 'fitness', 'nutrition', 'wellness', 'yoga', 'meditation'],
            'personal_development': ['productivity', 'mindset', 'leadership', 'communication', 'personal'],
            'finance': ['investing', 'trading', 'money', 'finance', 'wealth', 'crypto'],
        }

        self.monetization_models = {
            'one_time': ['one-time', 'single payment', 'lifetime access'],
            'subscription': ['membership', 'subscription', 'monthly', 'recurring'],
            'cohort': ['cohort', 'live', 'bootcamp', 'group coaching'],
            'freemium': ['free', 'freemium', 'lead magnet', 'free course'],
        }

        self.success_indicators = {
            'revenue': ['revenue', 'income', 'earnings', 'sales', '$', 'money'],
            'students': ['students', 'enrollments', 'members', 'learners'],
            'launch': ['launch', 'launched', 'releasing', 'new course'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch course creation ecosystem data"""
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

            return {'items': all_items, 'source': 'teachable_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Teachable data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process course creation data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_creator_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_category': self._group_by_category(processed_items),
                'monetization_trends': self._analyze_monetization(processed_items),
                'success_stories': self._extract_success_stories(processed_items),
                'launch_opportunities': self._identify_opportunities(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='teachable.com',
                data_type='course_creation',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'teachable_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['courses', 'education', 'creator', 'monetization', 'online learning'],
                target_agents=['education_agent', 'income_agent', 'content_agent'],
                target_advisors=['creator_advisor', 'monetization_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Teachable data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify category
            category = 'general'
            for cat, keywords in self.course_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify monetization model mentions
            monetization = []
            for model, keywords in self.monetization_models.items():
                if any(kw in text for kw in keywords):
                    monetization.append(model)

            # Check for success indicators
            has_revenue_mention = any(kw in text for kw in self.success_indicators['revenue'])
            has_student_mention = any(kw in text for kw in self.success_indicators['students'])
            is_launch_related = any(kw in text for kw in self.success_indicators['launch'])

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'monetization_mentions': monetization,
                'has_revenue_mention': has_revenue_mention,
                'has_student_mention': has_student_mention,
                'is_launch_related': is_launch_related,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_creator_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate creator economy insights"""
        if not items:
            return {}

        revenue_items = [i for i in items if i.get('has_revenue_mention')]
        launch_items = [i for i in items if i.get('is_launch_related')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            'total_items': len(items),
            'revenue_focused': len(revenue_items),
            'launch_related': len(launch_items),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'creator_sentiment': 'bullish' if sum(i.get('sentiment', 0) for i in items) / len(items) > 0.1 else 'neutral',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by course category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_monetization(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze monetization model mentions"""
        model_counts = {}
        for item in items:
            for model in item.get('monetization_mentions', []):
                model_counts[model] = model_counts.get(model, 0) + 1
        return dict(sorted(model_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_success_stories(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract success story content"""
        stories = []
        for item in items:
            if item.get('has_revenue_mention') or item.get('has_student_mention'):
                stories.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return stories[:5]

    def _identify_opportunities(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify course creation opportunities"""
        opportunities = []
        for item in items:
            if item.get('is_launch_related') and item.get('sentiment', 0) > 0:
                opportunities.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'monetization': item.get('monetization_mentions'),
                    'link': item.get('link'),
                })
        return opportunities[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['course', 'teachable', 'online learning', 'creator', 'education']
