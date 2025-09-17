"""
RemoteOK Intelligence Spider - Remote Jobs Platform
===================================================

Specialized spider for gathering remote job opportunities from RemoteOK.
Focuses on tech and startup remote positions worldwide.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class RemoteOKIntelligenceSpider(BaseIntelligenceSpider):
    """RemoteOK remote jobs intelligence gathering spider."""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.tech_categories = ['engineering', 'design', 'marketing', 'sales', 'support', 'management']
        self.salary_ranges = {'junior': (30000, 70000), 'mid': (70000, 120000), 'senior': (120000, 200000)}

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process RemoteOK data"""
        try:
            if 'remoteok.io' in target.url:
                return await self._process_remoteok_job(raw_data, target)
            return await self._process_general_tech_job(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing RemoteOK data: {e}")
            return None

    async def _process_remoteok_job(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process RemoteOK job posting"""
        if 'content' not in data:
            return None

        soup = BeautifulSoup(data['content'], 'html.parser')

        job_info = {
            'id': f"remoteok_{int(datetime.now().timestamp())}",
            'title': self._extract_title(soup),
            'company': self._extract_company(soup),
            'description': self._extract_description(soup),
            'salary': self._extract_salary(soup),
            'tags': self._extract_tags(soup),
            'location': 'Worldwide',
            'apply_url': self._extract_apply_url(soup),
            'posted_date': self._extract_posted_date(soup),
            'source': 'remoteok'
        }

        quality_score = 0.7  # RemoteOK generally has quality jobs
        if job_info.get('salary'):
            quality_score += 0.2

        return IntelligenceData(
            spider_id=self.spider_id,
            source_url=target.url,
            data_type='remote_tech_job',
            content=job_info,
            metadata={
                'platform': 'remoteok',
                'job_category': 'tech',
                'salary_disclosed': bool(job_info.get('salary')),
                'processing_timestamp': datetime.now(timezone.utc).isoformat()
            },
            quality_score=quality_score,
            timestamp=datetime.now(timezone.utc),
            relevance_tags=['remote_work', 'tech_jobs', 'startup'] + job_info.get('tags', [])[:5],
            target_agents=['income_builder', 'tech_job_specialist', 'startup_opportunities'],
            target_advisors=['startup_guru', 'tech_innovator']
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title"""
        for selector in ['h2', 'h1', '.job-title']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "RemoteOK Tech Job"

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name"""
        for selector in ['.company', '.employer', 'h3']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Tech Startup"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description"""
        for selector in ['.markdown', '.description', 'p']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()[:2000]
        return ""

    def _extract_salary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract salary"""
        text = soup.get_text()
        salary_patterns = [
            r'\$[\d,]+k?(?:\s*-\s*\$[\d,]+k?)?',
            r'[\d,]+k?\s*USD'
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract job tags/skills"""
        tags = []
        for elem in soup.select('.tag, .skill, .label'):
            tag = elem.get_text().strip()
            if tag and len(tag) < 30:
                tags.append(tag)
        return tags[:15]

    def _extract_apply_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract application URL"""
        for elem in soup.select('a[href*="apply"], a[href*="jobs"]'):
            return elem.get('href')
        return None

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        for selector in ['.time', '.date', '.posted']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return None

    async def _process_general_tech_job(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general tech job"""
        job_info = {
            'id': f"general_tech_{int(datetime.now().timestamp())}",
            'title': 'General Tech Job',
            'source': 'general',
            'url': target.url
        }

        return IntelligenceData(
            spider_id=self.spider_id,
            source_url=target.url,
            data_type='tech_job_opportunity',
            content=job_info,
            metadata={'platform': 'general'},
            quality_score=0.4,
            timestamp=datetime.now(timezone.utc),
            relevance_tags=['tech_jobs', 'general'],
            target_agents=['income_builder'],
            target_advisors=[]
        )