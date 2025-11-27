"""
OpenSea Spider - NFT Marketplace Intelligence
==============================================

Session 218: Specialized spider for OpenSea NFT marketplace.
Focuses on NFT trends, collections, and digital art market intelligence.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class OpenSeaSpider(BaseIntelligenceSpider):
    """OpenSea spider - NFT marketplace and digital art intelligence"""

    # NFT/Digital Art RSS feeds
    RSS_FEEDS = {
        'nft_news': 'https://nftnow.com/feed/',
        'decrypt_nft': 'https://decrypt.co/feed',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.nft_categories = {
            'art': ['art', 'artist', 'artwork', 'digital art', 'generative', 'ai art'],
            'pfp': ['pfp', 'profile picture', 'avatar', 'collection', 'ape', 'punk'],
            'gaming': ['gaming', 'game', 'metaverse', 'virtual world', 'play to earn', 'p2e'],
            'music': ['music', 'audio', 'song', 'album', 'sound'],
            'photography': ['photography', 'photo', 'photographer'],
            'collectibles': ['collectible', 'trading card', 'sports', 'memorabilia'],
            'utility': ['utility', 'membership', 'access', 'token-gated'],
        }

        self.market_signals = {
            'bullish': ['floor', 'volume', 'sale', 'sold', 'record', 'million', 'eth'],
            'launch': ['launch', 'mint', 'drop', 'release', 'debut'],
            'partnership': ['partnership', 'collab', 'collaboration', 'brand'],
            'celebrity': ['celebrity', 'famous', 'influencer', 'musician', 'actor'],
        }

        self.platforms = {
            'opensea': ['opensea', 'open sea'],
            'blur': ['blur'],
            'rarible': ['rarible'],
            'foundation': ['foundation'],
            'superrare': ['superrare', 'super rare'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch NFT ecosystem data"""
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
                                'source': feed_name,
                            }
                            if item['title']:
                                all_items.append(item)
                except Exception as e:
                    self.logger.warning(f"Error fetching {feed_name} feed: {e}")

            return {'items': all_items, 'source': 'opensea_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching OpenSea data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process NFT ecosystem data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            # Filter for NFT-relevant content
            nft_items = [i for i in processed_items if i.get('is_nft_relevant')]

            insights = self._generate_nft_insights(nft_items)

            content = {
                'items': nft_items,
                'insights': insights,
                'by_category': self._group_by_category(nft_items),
                'market_activity': self._analyze_market_activity(nft_items),
                'trending_collections': self._extract_trending(nft_items),
                'opportunities': self._identify_opportunities(nft_items),
            }

            quality_score = min(1.0, len(nft_items) / 15 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='opensea.io',
                data_type='nft_marketplace',
                content=content,
                metadata={
                    'item_count': len(nft_items),
                    'source': 'opensea_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['nft', 'digital art', 'collectibles', 'opensea', 'crypto art'],
                target_agents=['nft_agent', 'art_agent', 'investment_agent'],
                target_advisors=['nft_advisor', 'art_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing OpenSea data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Check if NFT-relevant
            nft_keywords = ['nft', 'non-fungible', 'opensea', 'mint', 'collection', 'digital art',
                          'crypto art', 'pfp', 'airdrop', 'floor price', 'blur']
            is_nft_relevant = any(kw in text for kw in nft_keywords)

            # Identify category
            category = 'general'
            for cat, keywords in self.nft_categories.items():
                if any(kw in text for kw in keywords):
                    category = cat
                    break

            # Identify market signals
            signals = []
            for signal, keywords in self.market_signals.items():
                if any(kw in text for kw in keywords):
                    signals.append(signal)

            # Identify platform mentions
            platform = None
            for plat, keywords in self.platforms.items():
                if any(kw in text for kw in keywords):
                    platform = plat
                    break

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
                'signals': signals,
                'platform': platform,
                'is_nft_relevant': is_nft_relevant,
                'is_launch': 'launch' in signals,
                'is_bullish': 'bullish' in signals,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_nft_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate NFT market insights"""
        if not items:
            return {}

        launches = [i for i in items if i.get('is_launch')]
        bullish_items = [i for i in items if i.get('is_bullish')]

        cat_counts = {}
        for item in items:
            cat = item.get('category', 'general')
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        avg_sentiment = sum(i.get('sentiment', 0) for i in items) / len(items) if items else 0

        return {
            'total_items': len(items),
            'new_launches': len(launches),
            'bullish_signals': len(bullish_items),
            'hot_categories': sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_mood': 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral',
        }

    def _group_by_category(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by NFT category"""
        groups = {}
        for item in items:
            cat = item.get('category', 'general')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_market_activity(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze market activity signals"""
        signal_counts = {}
        for item in items:
            for signal in item.get('signals', []):
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
        return dict(sorted(signal_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending collections/items"""
        trending = []
        for item in items:
            if item.get('is_bullish') or item.get('is_launch'):
                trending.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'signals': item.get('signals'),
                    'link': item.get('link'),
                })
        return trending[:5]

    def _identify_opportunities(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify NFT opportunities"""
        opportunities = []
        for item in items:
            if item.get('is_launch') and item.get('sentiment', 0) > 0:
                opportunities.append({
                    'title': item.get('title'),
                    'category': item.get('category'),
                    'platform': item.get('platform'),
                    'link': item.get('link'),
                })
        return opportunities[:5]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['nft', 'opensea', 'digital art', 'collection', 'mint', 'crypto art']
