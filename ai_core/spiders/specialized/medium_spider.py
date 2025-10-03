"""
Medium Intelligence Spider - Content Monetization Platform
==========================================================

Specialized spider for gathering content monetization opportunities from Medium.
Focuses on Medium Partner Program and writing opportunities.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..revenue_tracker import create_project_revenue


class MediumIntelligenceSpider(BaseIntelligenceSpider):
    """Medium content monetization intelligence spider."""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.content_categories = ['technology', 'business', 'startup', 'ai', 'programming', 'design', 'marketing']
        self.monetization_metrics = ['views', 'reads', 'claps', 'followers', 'earnings']

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Medium data"""
        try:
            if 'medium.com' in target.url:
                return await self._process_medium_opportunity(raw_data, target)
            return await self._process_general_content(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing Medium data: {e}")
            return None

    async def _process_medium_opportunity(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Medium content opportunity"""
        if 'content' not in data:
            return None

        soup = BeautifulSoup(data['content'], 'html.parser')

        content_info = {
            'id': f"medium_{int(datetime.now().timestamp())}",
            'title': self._extract_title(soup),
            'author': self._extract_author(soup),
            'publication': self._extract_publication(soup),
            'tags': self._extract_tags(soup),
            'read_time': self._extract_read_time(soup),
            'claps': self._extract_claps(soup),
            'responses': self._extract_responses(soup),
            'published_date': self._extract_published_date(soup),
            'partner_program': self._check_partner_program(soup),
            'monetization_potential': self._assess_monetization_potential(soup),
            'source': 'medium'
        }

        quality_score = self._calculate_content_quality_score(content_info)

        return IntelligenceData(
            spider_id=self.spider_id,
            source_url=target.url,
            data_type='content_monetization_opportunity',
            content=content_info,
            metadata={
                'platform': 'medium',
                'content_type': 'article',
                'monetization_enabled': content_info.get('partner_program', False),
                'processing_timestamp': datetime.now(timezone.utc).isoformat()
            },
            quality_score=quality_score,
            timestamp=datetime.now(timezone.utc),
            relevance_tags=['content_creation', 'medium', 'writing'] + content_info.get('tags', [])[:5],
            target_agents=['income_builder', 'content_creator', 'medium_writer'],
            target_advisors=['content_strategist', 'creator_economy_expert']
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        for selector in ['h1', '[data-testid="storyTitle"]', '.graf--title']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Medium Article"

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract author name"""
        for selector in ['[data-testid="authorName"]', '.author-name', '.u-accentColor--textNormal']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Unknown Author"

    def _extract_publication(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication name"""
        for selector in ['[data-testid="publicationName"]', '.publication-name']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return None

    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract article tags"""
        tags = []
        for elem in soup.select('[data-testid="tag"]', '.tag'):
            tag = elem.get_text().strip()
            if tag and len(tag) < 50:
                tags.append(tag)
        return tags[:10]

    def _extract_read_time(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract read time"""
        for selector in ['[data-testid="readTime"]', '.reading-time']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return None

    def _extract_claps(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract clap count"""
        text = soup.get_text()
        clap_match = re.search(r'(\d+(?:,\d{3})*)\s*claps?', text, re.IGNORECASE)
        if clap_match:
            return int(clap_match.group(1).replace(',', ''))
        return None

    def _extract_responses(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract response count"""
        text = soup.get_text()
        response_match = re.search(r'(\d+)\s*responses?', text, re.IGNORECASE)
        if response_match:
            return int(response_match.group(1))
        return None

    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract published date"""
        for selector in ['[data-testid="publishedDate"]', '.published-date', 'time']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return None

    def _check_partner_program(self, soup: BeautifulSoup) -> bool:
        """Check if article is in Partner Program"""
        text = soup.get_text().lower()
        return any(indicator in text for indicator in ['member-only', 'partner program', 'earnings'])

    def _assess_monetization_potential(self, soup: BeautifulSoup) -> str:
        """Assess monetization potential"""
        claps = self._extract_claps(soup) or 0
        responses = self._extract_responses(soup) or 0

        if claps > 1000 or responses > 50:
            return 'high'
        elif claps > 100 or responses > 10:
            return 'medium'
        else:
            return 'low'

    def _calculate_content_quality_score(self, content_info: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        score = 0.5

        if content_info.get('partner_program'):
            score += 0.3

        claps = content_info.get('claps', 0)
        if claps > 500:
            score += 0.2
        elif claps > 100:
            score += 0.1

        if content_info.get('publication'):
            score += 0.1

        return min(score, 1.0)

    async def _process_general_content(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general content opportunity"""
        content_info = {
            'id': f"general_content_{int(datetime.now().timestamp())}",
            'title': 'General Content Opportunity',
            'source': 'general',
            'url': target.url
        }

        return IntelligenceData(
            spider_id=self.spider_id,
            source_url=target.url,
            data_type='content_opportunity',
            content=content_info,
            metadata={'platform': 'general'},
            quality_score=0.3,
            timestamp=datetime.now(timezone.utc),
            relevance_tags=['content_creation', 'general'],
            target_agents=['income_builder'],
            target_advisors=[]
        )

    async def track_revenue_conversion(
        self,
        application_id: str,
        user_id: str,
        content_title: str,
        revenue_amount: float,
        client_name: str = "Medium Partner Program",
        **kwargs
    ) -> Optional[str]:
        """
        Track revenue when Medium content generates earnings.
        Called when content monetization occurs.

        Args:
            application_id: Unique identifier for this content opportunity
            user_id: User who created the content
            content_title: Title of the content that generated revenue
            revenue_amount: Amount earned from the content
            client_name: Platform or client name (defaults to Medium)
            **kwargs: Additional metadata (tags, satisfaction_score, etc.)

        Returns:
            Revenue record ID if successful, None otherwise
        """
        try:
            record_id = await create_project_revenue(
                application_id=application_id,
                user_id=user_id,
                client_name=client_name,
                project_title=content_title,
                contract_value=revenue_amount,
                **kwargs
            )

            if record_id:
                self.logger.info(f"💰 Tracked Medium revenue: ${revenue_amount} for '{content_title}'")

            return record_id

        except Exception as e:
            self.logger.error(f"Error tracking Medium revenue conversion: {e}")
            return None