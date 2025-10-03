"""
Content Monetization Spider - Creator Economy Intelligence
===========================================================

Generic spider for content monetization platforms (Substack, Patreon, Ko-fi, ProductHunt)
Provides intelligence for content creation and monetization agents.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class ContentMonetizationSpider(BaseIntelligenceSpider):
    """Generic content monetization intelligence spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Process content monetization data

        Extracts:
        - Creator profiles
        - Monetization strategies
        - Content types
        - Subscriber/supporter metrics
        """
        try:
            platform = self._detect_platform(target.url)

            if platform == 'substack':
                return await self._process_substack(raw_data, target)
            elif platform == 'patreon':
                return await self._process_patreon(raw_data, target)
            elif platform == 'kofi':
                return await self._process_kofi(raw_data, target)
            elif platform == 'producthunt':
                return await self._process_producthunt(raw_data, target)
            else:
                return await self._process_generic(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing content monetization data: {e}")
            return None

    def _detect_platform(self, url: str) -> str:
        """Detect which platform based on URL"""
        url_lower = url.lower()
        if 'substack' in url_lower:
            return 'substack'
        elif 'patreon' in url_lower:
            return 'patreon'
        elif 'ko-fi' in url_lower or 'kofi' in url_lower:
            return 'kofi'
        elif 'producthunt' in url_lower:
            return 'producthunt'
        return 'generic'

    async def _process_substack(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Substack newsletters"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for newsletter listings
            newsletters = soup.find_all(['div', 'article'], class_=lambda x: x and 'publication' in x.lower())

            for newsletter in newsletters[:20]:
                title_elem = newsletter.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'newsletter',
                        'url': title_elem.get('href', ''),
                        'platform': 'substack'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="content_monetization",
                content={
                    'platform': 'substack',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'monetization_type': 'newsletter_subscriptions',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing Substack data: {e}")
            return None

    async def _process_patreon(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Patreon creators"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for creator listings
            creators = soup.find_all(['div', 'article'], class_=lambda x: x and 'creator' in x.lower())

            for creator in creators[:20]:
                title_elem = creator.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'creator',
                        'url': title_elem.get('href', ''),
                        'platform': 'patreon'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="content_monetization",
                content={
                    'platform': 'patreon',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'monetization_type': 'membership',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing Patreon data: {e}")
            return None

    async def _process_kofi(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Ko-fi creators"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for creator profiles
            profiles = soup.find_all(['div', 'article'], class_=lambda x: x and 'creator' in x.lower())

            for profile in profiles[:20]:
                title_elem = profile.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'creator',
                        'url': title_elem.get('href', ''),
                        'platform': 'kofi'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="content_monetization",
                content={
                    'platform': 'kofi',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'monetization_type': 'tips_donations',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing Ko-fi data: {e}")
            return None

    async def _process_producthunt(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process ProductHunt launches"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for product listings
            products = soup.find_all(['div', 'article'], class_=lambda x: x and 'product' in x.lower())

            for product in products[:20]:
                title_elem = product.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'product',
                        'url': title_elem.get('href', ''),
                        'platform': 'producthunt'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="content_monetization",
                content={
                    'platform': 'producthunt',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'monetization_type': 'product_launch',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing ProductHunt data: {e}")
            return None

    async def _process_generic(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Generic processing for unknown platforms"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            for elem in soup.find_all(['h2', 'h3', 'h4'])[:20]:
                link = elem.find('a')
                items.append({
                    'title': elem.get_text(strip=True),
                    'url': link.get('href', '') if link else '',
                    'type': 'generic',
                    'platform': 'unknown'
                })

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="content_monetization",
                content={
                    'platform': 'generic',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.60,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'monetization_type': 'generic',
                    'priority': 3,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing generic data: {e}")
            return None
