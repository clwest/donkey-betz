"""
Kickstarter Spider - Creative Crowdfunding & Project Intelligence
===================================================================

Session 218: Specialized spider for Kickstarter crowdfunding platform.
Focuses on creative projects, innovative products, and backer trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class KickstarterSpider(BaseIntelligenceSpider):
    """Kickstarter spider - creative crowdfunding and project intelligence"""

    # Kickstarter and crowdfunding RSS feeds
    RSS_FEEDS = {
        'kickstarter_blog': 'https://www.kickstarter.com/blog.atom',
        'product_hunt': 'https://www.producthunt.com/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.project_categories = {
            'games': ['game', 'board game', 'video game', 'tabletop', 'rpg', 'card game'],
            'technology': ['tech', 'gadget', 'device', 'app', 'software', 'hardware'],
            'design': ['design', 'product', 'furniture', 'fashion', 'accessory'],
            'film': ['film', 'movie', 'documentary', 'animation', 'short film'],
            'music': ['music', 'album', 'vinyl', 'instrument', 'concert'],
            'publishing': ['book', 'comic', 'magazine', 'zine', 'publishing'],
            'art': ['art', 'illustration', 'painting', 'sculpture', 'photography'],
            'food': ['food', 'drink', 'restaurant', 'cookbook', 'beverage'],
        }

        self.campaign_stages = {
            'launching': ['launching', 'live now', 'just launched', 'new campaign'],
            'funded': ['funded', 'reached goal', 'successful', 'backed'],
            'ending_soon': ['ending soon', 'final hours', 'last chance', 'ends'],
            'staff_pick': ['staff pick', 'featured', 'project we love'],
        }

        self.backer_signals = {
            'popular': ['popular', 'trending', 'viral', 'hot', 'top'],
            'milestone': ['milestone', 'stretch goal', 'unlocked', 'achievement'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Kickstarter data"""
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

            return {'items': all_items, 'source': 'kickstarter_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Kickstarter data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Kickstarter data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_kickstarter_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_category': self._group_by_category(processed_items),
                'staff_picks': self._extract_staff_picks(processed_items),
                'trending_projects': self._extract_trending(processed_items),
                'successful_campaigns': self._extract_successful(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='kickstarter.com',
                data_type='creative_crowdfunding',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'kickstarter_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['kickstarter', 'crowdfunding', 'creative', 'projects', 'innovation'],
                target_agents=['creative_agent', 'product_agent', 'innovation_agent'],
                target_advisors=['creative_strategist', 'product_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Kickstarter data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify project category
            category = 'general'
            for cat, keywords in self.project_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify campaign stage
            stage = 'active'
            for stg, keywords in self.campaign_stages.items():
                if any(kw in text for kw in keywords):
                    stage = stg
                    break

            # Check for backer signals
            signals = []
            for signal, keywords in self.backer_signals.items():
                if any(kw in text for kw in keywords):
                    signals.append(signal)

            # Special flags
            is_staff_pick = stage == 'staff_pick'
            is_funded = stage == 'funded'
            is_trending = 'popular' in signals

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
                'stage': stage,
                'signals': signals,
                'is_staff_pick': is_staff_pick,
                'is_funded': is_funded,
                'is_trending': is_trending,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_kickstarter_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Kickstarter insights"""
        if not items:
            return {}

        staff_picks = [i for i in items if i.get('is_staff_pick')]
        funded = [i for i in items if i.get('is_funded')]
        trending = [i for i in items if i.get('is_trending')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            'total_items': len(items),
            'staff_picks': len(staff_picks),
            'funded_projects': len(funded),
            'trending_count': len(trending),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'creative_pulse': 'vibrant' if len(staff_picks) > 2 else 'steady',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by project category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({
                'title': item.get('title'),
                'stage': item.get('stage'),
                'link': item.get('link'),
            })
        return groups

    def _extract_staff_picks(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract staff pick projects"""
        picks = []
        for item in items:
            if item.get('is_staff_pick'):
                picks.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return picks[:5]

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending projects"""
        trending = []
        for item in items:
            if item.get('is_trending'):
                trending.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return trending[:5]

    def _extract_successful(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract successful campaigns"""
        successful = []
        for item in items:
            if item.get('is_funded'):
                successful.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return successful[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['kickstarter', 'crowdfunding', 'campaign', 'backer', 'creative', 'project']
