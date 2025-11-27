"""
Etherscan Spider - Ethereum Blockchain Intelligence
====================================================

Session 218: Specialized spider for Etherscan blockchain data.
Focuses on Ethereum transactions, smart contracts, and DeFi activity.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import feedparser
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class EtherscanSpider(BaseIntelligenceSpider):
    """Etherscan spider - Ethereum blockchain and DeFi intelligence"""

    # Ethereum/Crypto RSS feeds
    RSS_FEEDS = {
        'ethereum_blog': 'https://blog.ethereum.org/feed.xml',
        'defi_pulse': 'https://defipulse.com/blog/feed/',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.blockchain_topics = {
            'defi': ['defi', 'decentralized finance', 'liquidity', 'yield', 'farming', 'lending', 'borrowing'],
            'nft': ['nft', 'non-fungible', 'collectible', 'opensea', 'art', 'pfp'],
            'smart_contracts': ['smart contract', 'solidity', 'vyper', 'evm', 'bytecode'],
            'layer2': ['layer 2', 'l2', 'rollup', 'optimism', 'arbitrum', 'zk', 'polygon'],
            'staking': ['staking', 'validator', 'pos', 'proof of stake', 'eth2', 'beacon'],
            'dao': ['dao', 'governance', 'voting', 'proposal', 'treasury'],
        }

        self.activity_types = {
            'launch': ['launch', 'deploy', 'release', 'mainnet', 'live'],
            'upgrade': ['upgrade', 'update', 'fork', 'eip', 'improvement'],
            'security': ['hack', 'exploit', 'vulnerability', 'audit', 'security'],
            'funding': ['raise', 'funding', 'investment', 'grant', 'treasury'],
        }

        self.protocols = {
            'lending': ['aave', 'compound', 'maker', 'lending'],
            'dex': ['uniswap', 'sushiswap', 'curve', 'dex', 'swap'],
            'derivatives': ['dydx', 'gmx', 'perpetual', 'futures', 'options'],
            'bridges': ['bridge', 'wormhole', 'multichain', 'cross-chain'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch Ethereum ecosystem data"""
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

            return {'items': all_items, 'source': 'etherscan_ecosystem'}

        except Exception as e:
            self.logger.error(f"Error fetching Etherscan data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Ethereum ecosystem data"""
        try:
            items = raw_data.get('items', [])
            processed_items = []

            for item in items:
                processed = self._process_item(item)
                if processed:
                    processed_items.append(processed)

            insights = self._generate_blockchain_insights(processed_items)

            content = {
                'items': processed_items,
                'insights': insights,
                'by_topic': self._group_by_topic(processed_items),
                'protocol_activity': self._analyze_protocols(processed_items),
                'security_alerts': self._extract_security_items(processed_items),
                'defi_trends': self._analyze_defi_trends(processed_items),
            }

            quality_score = min(1.0, len(processed_items) / 20 + 0.35)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='etherscan.io',
                data_type='blockchain_intelligence',
                content=content,
                metadata={
                    'item_count': len(processed_items),
                    'source': 'etherscan_ecosystem',
                    'feeds_scraped': list(self.RSS_FEEDS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['ethereum', 'blockchain', 'defi', 'crypto', 'smart contracts'],
                target_agents=['crypto_agent', 'defi_agent', 'investment_agent'],
                target_advisors=['crypto_advisor', 'defi_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Etherscan data: {e}")
            return None

    def _process_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual item"""
        try:
            title = item.get('title', '')
            description = item.get('description', '')
            text = f"{title} {description}".lower()

            # Identify topic
            topic = 'general'
            for top, keywords in self.blockchain_topics.items():
                if any(kw in text for kw in keywords):
                    topic = top
                    break

            # Identify activity type
            activity = 'news'
            for act, keywords in self.activity_types.items():
                if any(kw in text for kw in keywords):
                    activity = act
                    break

            # Identify protocol mentions
            protocol_type = None
            for ptype, keywords in self.protocols.items():
                if any(kw in text for kw in keywords):
                    protocol_type = ptype
                    break

            # Check for important flags
            is_security_related = activity == 'security'
            is_upgrade = activity == 'upgrade'
            is_launch = activity == 'launch'

            # Sentiment
            blob = TextBlob(f"{title} {description}")
            sentiment = blob.sentiment.polarity

            return {
                'title': title,
                'description': description[:300],
                'link': item.get('link', ''),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'topic': topic,
                'activity': activity,
                'protocol_type': protocol_type,
                'is_security_related': is_security_related,
                'is_upgrade': is_upgrade,
                'is_launch': is_launch,
                'sentiment': sentiment,
            }

        except Exception as e:
            self.logger.warning(f"Error processing item: {e}")
            return None

    def _generate_blockchain_insights(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate blockchain ecosystem insights"""
        if not items:
            return {}

        security_items = [i for i in items if i.get('is_security_related')]
        launches = [i for i in items if i.get('is_launch')]
        upgrades = [i for i in items if i.get('is_upgrade')]

        topic_counts = {}
        for item in items:
            topic = item.get('topic', 'general')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        avg_sentiment = sum(i.get('sentiment', 0) for i in items) / len(items) if items else 0

        return {
            'total_items': len(items),
            'security_alerts': len(security_items),
            'new_launches': len(launches),
            'upgrades': len(upgrades),
            'hot_topics': sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'market_sentiment': 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral',
        }

    def _group_by_topic(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group items by blockchain topic"""
        groups = {}
        for item in items:
            topic = item.get('topic', 'general')
            if topic not in groups:
                groups[topic] = []
            groups[topic].append({'title': item.get('title'), 'link': item.get('link')})
        return groups

    def _analyze_protocols(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze protocol type mentions"""
        protocol_counts = {}
        for item in items:
            ptype = item.get('protocol_type')
            if ptype:
                protocol_counts[ptype] = protocol_counts.get(ptype, 0) + 1
        return dict(sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_security_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract security-related items"""
        security = []
        for item in items:
            if item.get('is_security_related'):
                security.append({
                    'title': item.get('title'),
                    'topic': item.get('topic'),
                    'sentiment': item.get('sentiment'),
                    'link': item.get('link'),
                })
        return security[:5]

    def _analyze_defi_trends(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze DeFi-specific trends"""
        defi_items = [i for i in items if i.get('topic') == 'defi']
        return [{
            'title': item.get('title'),
            'protocol_type': item.get('protocol_type'),
            'activity': item.get('activity'),
            'link': item.get('link'),
        } for item in defi_items[:5]]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['ethereum', 'eth', 'defi', 'smart contract', 'blockchain', 'crypto']
