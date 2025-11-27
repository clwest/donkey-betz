"""
Indiegogo Spider - Crowdfunding & Innovation Intelligence
==========================================================

Session 218: Specialized spider for Indiegogo crowdfunding platform.
Focuses on innovative products, crowdfunding campaigns, and startup trends.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class IndiegogoSpider(BaseIntelligenceSpider):
    """Indiegogo spider - crowdfunding and innovation intelligence"""

    # Crowdfunding and innovation RSS feeds
    RSS_FEEDS = {
        'crowdfund_insider': 'https://www.crowdfundinsider.com/feed/',
        'techcrunch_startups': 'https://techcrunch.com/category/startups/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.campaign_categories = {
            'tech_gadgets': ['gadget', 'device', 'smart', 'wearable', 'electronic', 'tech'],
            'audio': ['speaker', 'headphone', 'earbuds', 'audio', 'music', 'sound'],
            'home': ['home', 'kitchen', 'furniture', 'household', 'living'],
            'outdoor': ['outdoor', 'camping', 'travel', 'adventure', 'gear'],
            'health': ['health', 'fitness', 'wellness', 'medical', 'tracker'],
            'sustainable': ['sustainable', 'eco', 'green', 'environment', 'solar'],
            'creative': ['art', 'design', 'creative', 'photography', 'film'],
            'gaming': ['game', 'gaming', 'console', 'controller', 'esports'],
        }

        self.funding_signals = {
            'successful': ['funded', 'success', 'goal reached', 'backed', 'raised'],
            'launching': ['launching', 'coming soon', 'pre-launch', 'live now'],
            'trending': ['trending', 'popular', 'hot', 'viral', 'featured'],
        }

        self.innovation_indicators = {
            'breakthrough': ['first', 'revolutionary', 'breakthrough', 'patent', 'innovative'],
            'improvement': ['better', 'improved', 'upgraded', 'enhanced', 'new version'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch crowdfunding data"""
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

            return {'items': all_items, 'source': 'indiegogo_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Indiegogo data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process crowdfunding data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for crowdfunding-relevant content
            crowdfund_items = [i for i in processed_items if i.get('is_crowdfunding_relevant')]

            insights = self._generate_crowdfunding_insights(crowdfund_items)

            content = {
                'items': crowdfund_items,
                'insights': insights,
                'by_category': self._group_by_category(crowdfund_items),
                'trending_campaigns': self._extract_trending(crowdfund_items),
                'innovation_highlights': self._extract_innovations(crowdfund_items),
                'successful_campaigns': self._extract_successful(crowdfund_items),
            }

            quality_score = min(1.0, len(crowdfund_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='indiegogo.com',
                data_type='crowdfunding',
                content=content,
                metadata={
                    'item_count': len(crowdfund_items),
                    'source': 'indiegogo_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['crowdfunding', 'innovation', 'startups', 'products', 'campaigns'],
                target_agents=['innovation_agent', 'product_agent', 'investment_agent'],
                target_advisors=['product_strategist', 'innovation_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Indiegogo data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if crowdfunding-relevant
            crowdfund_keywords = ['crowdfunding', 'campaign', 'backer', 'pledge', 'indiegogo',
                                'kickstarter', 'funded', 'launch', 'product', 'startup']
            is_crowdfunding_relevant = any(kw in text for kw in crowdfund_keywords)

            # Identify category
            category = 'general'
            for cat, keywords in self.campaign_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify funding signals
            signals = []
            for signal, keywords in self.funding_signals.items():
                if any(kw in text for kw in keywords):
                    signals.append(signal)

            # Check for innovation indicators
            is_breakthrough = any(kw in text for kw in self.innovation_indicators['breakthrough'])
            is_improvement = any(kw in text for kw in self.innovation_indicators['improvement'])

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
                'funding_signals': signals,
                'is_crowdfunding_relevant': is_crowdfunding_relevant,
                'is_trending': 'trending' in signals,
                'is_successful': 'successful' in signals,
                'is_breakthrough': is_breakthrough,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_crowdfunding_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate crowdfunding insights"""
        if not items:
            return {}

        trending = [i for i in items if i.get('is_trending')]
        successful = [i for i in items if i.get('is_successful')]
        breakthroughs = [i for i in items if i.get('is_breakthrough')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        return {
            'total_items': len(items),
            'trending_count': len(trending),
            'successful_count': len(successful),
            'breakthroughs': len(breakthroughs),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'innovation_pulse': 'high' if len(breakthroughs) > 2 else 'steady',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending campaigns"""
        trending = []
        for item in items:
            if item.get('is_trending'):
                trending.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return trending[:5]

    def _extract_innovations(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract innovation highlights"""
        innovations = []
        for item in items:
            if item.get('is_breakthrough'):
                innovations.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return innovations[:5]

    def _extract_successful(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract successful campaigns"""
        successful = []
        for item in items:
            if item.get('is_successful'):
                successful.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'link': item.get('link'),
                })
        return successful[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['indiegogo', 'crowdfunding', 'campaign', 'backer', 'innovation', 'product']
