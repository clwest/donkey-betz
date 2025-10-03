"""
Tech Community Spider - Generic Technical Intelligence
=======================================================

Generic spider for technical community sites (HuggingFace, Kaggle, GitHub, StackOverflow)
Provides basic intelligence gathering for technical agents.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class TechCommunitySpider(BaseIntelligenceSpider):
    """Generic technical community intelligence spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Process technical community data

        Extracts:
        - Projects/models/competitions
        - Descriptions and metadata
        - Tags and categories
        - Popularity metrics
        """
        try:
            platform = self._detect_platform(target.url)

            if platform == 'huggingface':
                return await self._process_huggingface(raw_data, target)
            elif platform == 'kaggle':
                return await self._process_kaggle(raw_data, target)
            elif platform == 'github':
                return await self._process_github(raw_data, target)
            elif platform == 'stackoverflow':
                return await self._process_stackoverflow(raw_data, target)
            else:
                return await self._process_generic(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing tech community data: {e}")
            return None

    def _detect_platform(self, url: str) -> str:
        """Detect which platform based on URL"""
        url_lower = url.lower()
        if 'huggingface' in url_lower:
            return 'huggingface'
        elif 'kaggle' in url_lower:
            return 'kaggle'
        elif 'github' in url_lower:
            return 'github'
        elif 'stackoverflow' in url_lower:
            return 'stackoverflow'
        return 'generic'

    async def _process_huggingface(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process HuggingFace models/datasets"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for model cards, dataset cards, etc.
            cards = soup.find_all(['article', 'div'], class_=lambda x: x and ('model' in x.lower() or 'dataset' in x.lower()))

            for card in cards[:20]:  # Limit to 20 items
                title_elem = card.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'model' if 'model' in str(card.get('class', '')).lower() else 'dataset',
                        'url': title_elem.get('href', ''),
                        'platform': 'huggingface'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="tech_intelligence",
                content={
                    'platform': 'huggingface',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'platform_type': 'ml_models',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing HuggingFace data: {e}")
            return None

    async def _process_kaggle(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Kaggle competitions/datasets"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for competition or dataset listings
            listings = soup.find_all(['div', 'article'], class_=lambda x: x and ('competition' in x.lower() or 'dataset' in x.lower()))

            for listing in listings[:20]:
                title_elem = listing.find(['h2', 'h3', 'h4', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'competition' if 'competition' in target.url else 'dataset',
                        'url': title_elem.get('href', ''),
                        'platform': 'kaggle'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="tech_intelligence",
                content={
                    'platform': 'kaggle',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'platform_type': 'data_science',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing Kaggle data: {e}")
            return None

    async def _process_github(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process GitHub trending/topics"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for repository listings
            repos = soup.find_all(['article', 'div'], class_=lambda x: x and 'repo' in x.lower())

            for repo in repos[:20]:
                title_elem = repo.find(['h2', 'h3', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'repository',
                        'url': title_elem.get('href', ''),
                        'platform': 'github'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="tech_intelligence",
                content={
                    'platform': 'github',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'platform_type': 'code_repositories',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing GitHub data: {e}")
            return None

    async def _process_stackoverflow(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process StackOverflow jobs/questions"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            items = []
            # Look for question or job listings
            listings = soup.find_all(['div', 'article'], class_=lambda x: x and ('question' in x.lower() or 'job' in x.lower()))

            for listing in listings[:20]:
                title_elem = listing.find(['h2', 'h3', 'a'])
                if title_elem:
                    item = {
                        'title': title_elem.get_text(strip=True),
                        'type': 'job' if 'job' in target.url else 'question',
                        'url': title_elem.get('href', ''),
                        'platform': 'stackoverflow'
                    }
                    items.append(item)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="tech_intelligence",
                content={
                    'platform': 'stackoverflow',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.75,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'platform_type': 'developer_community',
                    'priority': 2,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing StackOverflow data: {e}")
            return None

    async def _process_generic(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Generic processing for unknown platforms"""
        try:
            soup = BeautifulSoup(data.get('content', ''), 'html.parser')

            # Extract headings and links as generic content
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
                data_type="tech_intelligence",
                content={
                    'platform': 'generic',
                    'items': items,
                    'total_found': len(items)
                },
                quality_score=0.60,
                timestamp=datetime.now(timezone.utc),
                metadata={
                    'source': target.url,
                    'platform_type': 'generic',
                    'priority': 3,
                    'collection_time': datetime.now(timezone.utc).isoformat()
                },
                target_agents=self.subscribers
            )
        except Exception as e:
            self.logger.error(f"Error processing generic data: {e}")
            return None
