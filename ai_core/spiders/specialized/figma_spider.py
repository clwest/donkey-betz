"""
Figma Spider - Design Community & UI/UX Intelligence
========================================================

Session 218: Specialized spider for Figma design platform.
Focuses on design community, UI kits, plugins, and design trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class FigmaSpider(BaseIntelligenceSpider):
    """Figma spider - design community and UI/UX intelligence"""

    RSS_FEEDS = {
        'figma_blog': 'https://www.figma.com/blog/feed/',
        'ux_collective': 'https://uxdesign.cc/feed',
        'ux_planet': 'https://uxplanet.org/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.design_categories = {
            'ui_kits': ['ui kit', 'design system', 'component', 'library', 'kit'],
            'icons': ['icon', 'iconography', 'icon set', 'icon pack'],
            'illustrations': ['illustration', 'vector', 'artwork', 'graphic'],
            'wireframes': ['wireframe', 'prototype', 'mockup', 'layout'],
            'plugins': ['plugin', 'extension', 'tool', 'automation'],
            'templates': ['template', 'landing page', 'dashboard', 'mobile'],
        }

        self.design_trends = {
            'minimalism': ['minimal', 'clean', 'simple', 'whitespace', 'modern'],
            'neumorphism': ['neumorphism', 'soft ui', '3d', 'shadow', 'depth'],
            'glassmorphism': ['glass', 'blur', 'transparent', 'frosted'],
            'dark_mode': ['dark mode', 'dark theme', 'dark ui', 'night mode'],
            'accessibility': ['accessibility', 'a11y', 'inclusive', 'wcag'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Figma community data"""
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

            return {'items': all_items, 'source': 'figma'}

        except Exception as e:
            self.logger.error(f"Error fetching Figma data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Figma community data"""
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
                'by_category': self._group_by_category(processed_items),
                'trend_analysis': self._analyze_trends(processed_items),
                'trending_resources': self._extract_trending(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='figma.com',
                data_type='design_community',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'figma',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['figma', 'ui', 'ux', 'design', 'plugins', 'templates'],
                target_agents=['design_agent', 'ui_agent', 'creative_agent'],
                target_advisors=['design_director', 'ux_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Figma data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify design category
            category = 'general'
            for cat, keywords in self.design_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify design trends
            trends = []
            for trend, keywords in self.design_trends.items():
                if any(kw in text for kw in keywords):
                    trends.append(trend)

            # Check if Figma specific
            is_figma_specific = any(word in text for word in ['figma', 'figjam', 'auto layout', 'variant'])

            blob = TextBlob(f"{title}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'category': category,
                'trends': trends,
                'is_figma_specific': is_figma_specific,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate design community insights"""
        if not items:
            return {}

        figma_items = [i for i in items if i.get('is_figma_specific')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        trend_counts = {}
        for item in items:
            for trend in item.get('trends', []):
                trend_counts[trend] = trend_counts.get(trend, 0) + 1

        return {
            'total_items': len(items),
            'figma_specific': len(figma_items),
            'top_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'trending_styles': sorted(trend_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'design_pulse': 'creative' if len(figma_items) > 5 else 'steady',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by design category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_trends(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze design trend distribution"""
        trend_counts = {}
        for item in items:
            for trend in item.get('trends', []):
                trend_counts[trend] = trend_counts.get(trend, 0) + 1
        return dict(sorted(trend_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending design resources"""
        sorted_items = sorted(items, key=lambda x: x.get('sentiment', 0), reverse=True)
        return [{'title': i.get('title'), 'category': i.get('category'), 'link': i.get('link')}
                for i in sorted_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['figma', 'ui', 'ux', 'design', 'plugin', 'template', 'component']
