"""
Skillshare Spider - Creative Learning & Project-Based Education Intelligence
=============================================================================

Session 218: Specialized spider for Skillshare creative learning platform.
Focuses on creative skills, project-based learning, and creator opportunities.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SkillshareSpider(BaseIntelligenceSpider):
    """Skillshare spider - creative learning and project-based education"""

    # Creative education RSS feeds
    RSS_FEEDS = {
        'creative_bloq': 'https://www.creativebloq.com/feed',
        'design_shack': 'https://designshack.net/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.creative_categories = {
            'illustration': ['illustration', 'drawing', 'sketch', 'digital art', 'character design'],
            'graphic_design': ['graphic design', 'logo', 'branding', 'typography', 'layout'],
            'ui_ux': ['ui', 'ux', 'user interface', 'user experience', 'product design', 'figma'],
            'photography': ['photography', 'photo editing', 'lightroom', 'photoshop', 'camera'],
            'video': ['video editing', 'filmmaking', 'animation', 'motion graphics', 'after effects'],
            'writing': ['creative writing', 'copywriting', 'storytelling', 'content', 'blogging'],
            'crafts': ['crafts', 'diy', 'handmade', 'pottery', 'knitting', 'calligraphy'],
            'music': ['music', 'audio', 'podcast', 'sound design', 'music production'],
        }

        self.skill_aspects = {
            'tools': ['photoshop', 'illustrator', 'figma', 'procreate', 'premiere', 'after effects'],
            'techniques': ['technique', 'how to', 'tips', 'tutorial', 'guide', 'masterclass'],
            'business': ['freelance', 'client', 'pricing', 'portfolio', 'career'],
            'trends': ['trend', 'style', 'modern', '2024', '2025', 'new'],
        }

        self.project_types = {
            'hands_on': ['project', 'create', 'make', 'build', 'design your own'],
            'challenge': ['challenge', 'exercise', 'practice', 'assignment'],
            'portfolio': ['portfolio', 'showcase', 'professional', 'client-ready'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch creative learning data"""
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

            return {'items': all_items, 'source': 'skillshare_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Skillshare data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process creative learning data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_creative_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_category': self._group_by_category(processed_items),
                'tool_trends': self._analyze_tools(processed_items),
                'project_ideas': self._extract_project_ideas(processed_items),
                'skill_opportunities': self._identify_skill_opportunities(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='skillshare.com',
                data_type='creative_learning',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'skillshare_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['creative', 'design', 'skills', 'learning', 'projects'],
                target_agents=['creative_agent', 'skill_agent', 'education_agent'],
                target_advisors=['creative_advisor', 'skill_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Skillshare data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify creative category
            category = 'general_creative'
            for cat, keywords in self.creative_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify skill aspects
            aspects = []
            for aspect, keywords in self.skill_aspects.items():
                if any(kw in text for kw in keywords):
                    aspects.append(aspect)

            # Identify project type
            project_type = None
            for ptype, keywords in self.project_types.items():
                if any(kw in text for kw in keywords):
                    project_type = ptype
                    break

            # Check for tutorial/guide content
            is_tutorial = any(word in text for word in ['tutorial', 'how to', 'guide', 'learn', 'step by step'])
            is_inspiration = any(word in text for word in ['inspiration', 'ideas', 'examples', 'showcase', 'gallery'])

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
                'aspects': aspects or ['general'],
                'project_type': project_type,
                'is_tutorial': is_tutorial,
                'is_inspiration': is_inspiration,
                'sentiment': sentiment,
                'tags': item.get('tags', []),
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_creative_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate creative learning insights"""
        if not items:
            return {}

        tutorials = [i for i in items if i.get('is_tutorial')]
        inspiration = [i for i in items if i.get('is_inspiration')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general_creative')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            'total_items': len(items),
            'tutorials_count': len(tutorials),
            'inspiration_count': len(inspiration),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'creative_pulse': 'vibrant' if len(items) > 15 else 'steady',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by creative category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general_creative')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_tools(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze tool mentions"""
        tool_counts = {}
        for item in items:
            if 'tools' in item.get('aspects', []):
                text = f"{item.get('title', '')} {item.get('description', '')}".lower()
                for tool in self.skill_aspects['tools']:
                    if tool in text:
                        tool_counts[tool] = tool_counts.get(tool, 0) + 1
        return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_project_ideas(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract project ideas"""
        projects = []
        for item in items:
            if item.get('project_type') or item.get('is_tutorial'):
                projects.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'project_type': item.get('project_type'),
                    'link': item.get('link'),
                })
        return projects[:8]

    def _identify_skill_opportunities(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify skill learning opportunities"""
        opportunities = []
        for item in items:
            if item.get('is_tutorial') and item.get('sentiment', 0) > 0:
                opportunities.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'aspects': item.get('aspects'),
                    'link': item.get('link'),
                })
        return opportunities[:6]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['skillshare', 'creative', 'design', 'illustration', 'tutorial', 'project']
