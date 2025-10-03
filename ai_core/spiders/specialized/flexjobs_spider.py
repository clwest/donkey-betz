"""
FlexJobs Intelligence Spider - Remote Work Platform
==================================================

Specialized spider for gathering remote work opportunities from FlexJobs.
Focuses on flexible and remote positions across various industries.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..revenue_tracker import create_project_revenue


class FlexJobsIntelligenceSpider(BaseIntelligenceSpider):
    """FlexJobs remote work intelligence gathering spider."""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.job_types = ['remote', 'part-time', 'freelance', 'flexible']
        self.categories = ['technology', 'marketing', 'writing', 'design', 'customer-service']

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process FlexJobs data into structured intelligence"""
        try:
            if 'flexjobs.com' in target.url:
                return await self._process_flexjobs_opportunity(raw_data, target)
            else:
                return await self._process_general_remote_job(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing FlexJobs data: {e}")
            return None

    async def _process_flexjobs_opportunity(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process FlexJobs opportunity"""
        try:
            if 'content' not in data:
                return None

            soup = BeautifulSoup(data['content'], 'html.parser')

            job_info = {
                'id': self._extract_job_id(soup, target.url),
                'title': self._extract_title(soup),
                'company': self._extract_company(soup),
                'description': self._extract_description(soup),
                'job_type': self._extract_job_type(soup),
                'salary_range': self._extract_salary(soup),
                'location': self._extract_location(soup),
                'remote_level': self._extract_remote_level(soup),
                'skills': self._extract_skills(soup),
                'posted_date': self._extract_posted_date(soup),
                'source': 'flexjobs'
            }

            quality_score = self._calculate_quality_score(job_info)
            if quality_score < 0.4:
                return None

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='remote_job_opportunity',
                content=job_info,
                metadata={
                    'platform': 'flexjobs',
                    'job_type': job_info.get('job_type'),
                    'remote_level': job_info.get('remote_level'),
                    'processing_timestamp': datetime.now(timezone.utc).isoformat()
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['remote_work', 'flexjobs', 'flexible'] + job_info.get('skills', [])[:5],
                target_agents=['income_builder', 'remote_work_specialist'],
                target_advisors=['future_of_work_expert']
            )

        except Exception as e:
            self.logger.error(f"Error processing FlexJobs opportunity: {e}")
            return None

    def _extract_job_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract job ID"""
        id_match = re.search(r'/jobs/(\d+)', url)
        return f"flexjobs_{id_match.group(1)}" if id_match else f"flexjobs_{int(datetime.now().timestamp())}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title"""
        for selector in ['h1.job-title', '.job-header h1', 'h1']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "FlexJobs Opportunity"

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name"""
        for selector in ['.company-name', '.employer', '.company']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Unknown Company"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description"""
        for selector in ['.job-description', '.description']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()[:2000]
        return ""

    def _extract_job_type(self, soup: BeautifulSoup) -> str:
        """Extract job type"""
        text = soup.get_text().lower()
        for job_type in self.job_types:
            if job_type in text:
                return job_type
        return 'flexible'

    def _extract_salary(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract salary range"""
        text = soup.get_text()
        salary_patterns = [
            r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?(?:\s*per\s+year)?',
            r'[\d,]+\s*-\s*[\d,]+\s*USD'
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
        return None

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location"""
        for selector in ['.location', '.job-location']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return "Remote"

    def _extract_remote_level(self, soup: BeautifulSoup) -> str:
        """Extract remote work level"""
        text = soup.get_text().lower()
        if 'fully remote' in text or '100% remote' in text:
            return 'fully_remote'
        elif 'hybrid' in text:
            return 'hybrid'
        elif 'remote' in text:
            return 'remote'
        return 'flexible'

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills"""
        skills = []
        for container in soup.select('.skills, .requirements'):
            for item in container.select('li, span, .skill'):
                skill = item.get_text().strip()
                if skill and len(skill) < 50:
                    skills.append(skill)
        return skills[:10]

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        for selector in ['.posted-date', '.date-posted']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()
        return None

    def _calculate_quality_score(self, job_info: Dict[str, Any]) -> float:
        """Calculate job quality score"""
        score = 0.5

        if job_info.get('salary_range'):
            score += 0.2

        if job_info.get('remote_level') == 'fully_remote':
            score += 0.2

        if len(job_info.get('skills', [])) >= 3:
            score += 0.1

        return min(score, 1.0)

    async def _process_general_remote_job(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general remote job data"""
        try:
            job_info = {
                'id': f"general_{int(datetime.now().timestamp())}",
                'title': 'General Remote Job',
                'source': 'general',
                'url': target.url
            }

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='remote_job_opportunity',
                content=job_info,
                metadata={'platform': 'general'},
                quality_score=0.3,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['remote_work', 'general'],
                target_agents=['income-builder', 'job_application_agent', 'career-agent'],
                target_advisors=[]
            )
        except Exception as e:
            self.logger.error(f"Error processing general remote job: {e}")
            return None

    async def track_revenue_conversion(
        self,
        application_id: str,
        user_id: str,
        job_title: str,
        contract_value: float,
        employer_name: str,
        **kwargs
    ) -> Optional[str]:
        """
        Track revenue when a FlexJobs position is secured and generates earnings.
        Called when job offers are accepted and employment begins.

        Args:
            application_id: Unique identifier for this job opportunity
            user_id: User who was hired
            job_title: Title of the position
            contract_value: Total compensation (salary, hourly * estimated hours, etc.)
            employer_name: Employer/company name
            **kwargs: Additional metadata (job_type, remote_level, duration, etc.)

        Returns:
            Revenue record ID if successful, None otherwise
        """
        try:
            record_id = await create_project_revenue(
                application_id=application_id,
                user_id=user_id,
                client_name=employer_name,
                project_title=job_title,
                contract_value=contract_value,
                **kwargs
            )

            if record_id:
                self.logger.info(f"💰 Tracked FlexJobs revenue: ${contract_value} for '{job_title}' with {employer_name}")

            return record_id

        except Exception as e:
            self.logger.error(f"Error tracking FlexJobs revenue conversion: {e}")
            return None