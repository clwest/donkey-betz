"""
Canva Spider - Design Platform & Templates Intelligence
==========================================================

Session 218: Specialized spider for Canva design platform.
Focuses on design templates, brand kits, and design education.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class CanvaSpider(BaseIntelligenceSpider):
    """Canva spider - design platform and templates intelligence"""

    RSS_FEEDS = {
        'canva_design_school': 'https://www.canva.com/designschool/feed/',
        'design_shack': 'https://designshack.net/feed/',
        'speckyboy': 'https://speckyboy.com/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.template_types = {
            'social_media': ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok', 'social'],
            'presentations': ['presentation', 'slides', 'pitch deck', 'keynote', 'powerpoint'],
            'marketing': ['flyer', 'poster', 'brochure', 'banner', 'ad', 'marketing'],
            'documents': ['resume', 'letterhead', 'invoice', 'proposal', 'report'],
            'videos': ['video', 'animation', 'intro', 'outro', 'reel'],
            'brand': ['logo', 'brand kit', 'brand guide', 'identity', 'branding'],
        }

        self.design_skills = {
            'beginner': ['beginner', 'basic', 'simple', 'easy', 'start'],
            'intermediate': ['intermediate', 'improve', 'better', 'enhance'],
            'advanced': ['advanced', 'pro', 'professional', 'expert', 'master'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Canva data"""
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

            return {'items': all_items, 'source': 'canva'}

        except Exception as e:
            self.logger.error(f"Error fetching Canva data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Canva data"""
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
                'by_template_type': self._group_by_type(processed_items),
                'skill_level_content': self._analyze_skill_levels(processed_items),
                'design_tutorials': self._extract_tutorials(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='canva.com',
                data_type='design_platform',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'canva',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['canva', 'design', 'templates', 'social media', 'branding'],
                target_agents=['design_agent', 'social_media_agent', 'marketing_agent'],
                target_advisors=['design_educator', 'brand_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Canva data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify template type
            template_type = 'general'
            for ttype, keywords in self.template_types.items():
                if any(kw in text for kw in keywords):
                    template_type = ttype
                    break

            # Identify skill level
            skill_level = 'all_levels'
            for level, keywords in self.design_skills.items():
                if any(kw in text for kw in keywords):
                    skill_level = level
                    break

            # Check if it's a tutorial
            is_tutorial = any(word in text for word in ['how to', 'tutorial', 'guide', 'step', 'learn'])

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'template_type': template_type,
                'skill_level': skill_level,
                'is_tutorial': is_tutorial,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate design platform insights"""
        if not items:
            return {}

        tutorials = [i for i in items if i.get('is_tutorial')]

        type_counts = {}
        for item in items:
            ttype = item.get('template_type', 'general')
            type_counts[ttype] = type_counts.get(ttype, 0) + 1

        level_counts = {}
        for item in items:
            level = item.get('skill_level', 'all_levels')
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            'total_items': len(items),
            'tutorials_count': len(tutorials),
            'top_template_types': sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'skill_distribution': level_counts,
            'learning_focus': 'educational' if len(tutorials) > len(items) // 3 else 'mixed',
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

    def _analyze_skill_levels(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze skill level distribution"""
        level_counts = {}
        for item in items:
            level = item.get('skill_level', 'all_levels')
            level_counts[level] = level_counts.get(level, 0) + 1
        return level_counts

    def _extract_tutorials(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tutorial content"""
        return [{'title': i.get('title'), 'type': i.get('template_type'), 'level': i.get('skill_level'), 'link': i.get('link')}
                for i in items if i.get('is_tutorial')][:8]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['canva', 'design', 'templates', 'social media', 'graphic design', 'brand']
