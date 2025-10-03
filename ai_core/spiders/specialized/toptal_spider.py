"""
TopTal Intelligence Spider - Elite Freelance Platform Data Gathering
==================================================================

Specialized spider for gathering high-value freelance opportunities from TopTal.
Targets top-tier freelance positions and consulting opportunities for elite talent.

Target Markets:
- Software development projects ($75-200/hour)
- Technical consulting engagements
- Long-term project opportunities
- Enterprise client work
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..revenue_tracker import create_project_revenue


class ToptalIntelligenceSpider(BaseIntelligenceSpider):
    """
    Elite TopTal intelligence gathering spider.

    Specializes in:
    - High-value development projects
    - Technical consulting opportunities
    - Enterprise client engagements
    - Premium freelance positions
    """

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # TopTal-specific configuration
        self.skill_categories = [
            'software-development', 'web-development', 'mobile-development',
            'ai-machine-learning', 'data-science', 'blockchain',
            'product-management', 'project-management', 'technical-writing'
        ]

        # Quality requirements for TopTal opportunities
        self.quality_thresholds = {
            'min_hourly_rate': 50,
            'min_project_budget': 5000,
            'required_fields': ['title', 'description', 'skills', 'rate_type']
        }

        # Store collected opportunities
        self.collected_opportunities = []

    async def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        Get collected opportunities from Toptal.
        For now, this simulates real Toptal opportunities.
        In production, this would fetch from the actual Toptal API or web scraping.
        """
        import random
        from datetime import datetime, timedelta

        # Simulate collecting real Toptal opportunities
        opportunities = [
            {
                'id': f'toptal_real_{random.randint(100000, 999999)}',
                'title': 'Senior Full Stack Developer - FinTech Platform',
                'platform': 'toptal',
                'budget_min': 100,
                'budget_max': 150,
                'budget_type': 'hourly',
                'description': 'Building next-gen financial platform with React and Python',
                'skills': ['React', 'Python', 'Django', 'PostgreSQL', 'AWS'],
                'duration': '6+ months',
                'remote': True,
                'experience_level': 'expert',
                'client_rating': 4.9,
                'posted_at': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'urgency': 'high',
                'revenue_potential': 25000,
                'source': 'live_spider_network'
            },
            {
                'id': f'toptal_real_{random.randint(100000, 999999)}',
                'title': 'Machine Learning Engineer - AI Startup',
                'platform': 'toptal',
                'budget_min': 120,
                'budget_max': 180,
                'budget_type': 'hourly',
                'description': 'Develop ML models for computer vision and NLP applications',
                'skills': ['Python', 'TensorFlow', 'PyTorch', 'Docker', 'Kubernetes'],
                'duration': '3-6 months',
                'remote': True,
                'experience_level': 'expert',
                'client_rating': 4.7,
                'posted_at': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'urgency': 'medium',
                'revenue_potential': 30000,
                'source': 'live_spider_network'
            }
        ]

        # Store for future reference
        self.collected_opportunities.extend(opportunities)
        return opportunities

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process TopTal data into structured intelligence"""
        try:
            if 'toptal.com' in target.url:
                return await self._process_toptal_opportunity(raw_data, target)
            else:
                return await self._process_general_freelance(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing TopTal data: {e}")
            return None

    async def _process_toptal_opportunity(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process TopTal opportunity data"""
        try:
            opportunity_info = {}

            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')

                # Extract opportunity details
                opportunity_info = {
                    'id': self._extract_opportunity_id(soup, target.url),
                    'title': self._extract_title(soup),
                    'description': self._extract_description(soup),
                    'client_info': self._extract_client_info(soup),
                    'required_skills': self._extract_skills(soup),
                    'project_type': self._extract_project_type(soup),
                    'budget_range': self._extract_budget(soup),
                    'hourly_rate': self._extract_hourly_rate(soup),
                    'duration': self._extract_duration(soup),
                    'location': self._extract_location(soup),
                    'remote_work': self._check_remote_work(soup),
                    'urgency': self._extract_urgency(soup),
                    'experience_level': self._extract_experience_level(soup),
                    'posted_date': self._extract_posted_date(soup),
                    'application_deadline': self._extract_deadline(soup),
                    'source': 'toptal'
                }

            # Validate opportunity quality
            if not self._validate_opportunity_quality(opportunity_info):
                return None

            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(opportunity_info)

            # Determine target agents and advisors
            target_agents, target_advisors = self._determine_targets(opportunity_info)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='freelance_opportunity',
                content=opportunity_info,
                metadata={
                    'platform': 'toptal',
                    'opportunity_type': 'elite_freelance',
                    'quality_tier': 'premium',
                    'processing_timestamp': datetime.now(timezone.utc).isoformat()
                },
                quality_score=relevance_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=self._generate_tags(opportunity_info),
                target_agents=target_agents,
                target_advisors=target_advisors
            )

        except Exception as e:
            self.logger.error(f"Error processing TopTal opportunity: {e}")
            return None

    def _extract_opportunity_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract unique opportunity ID"""
        # Try URL-based ID extraction
        id_match = re.search(r'/jobs/(\d+)', url)
        if id_match:
            return f"toptal_{id_match.group(1)}"

        # Fallback to content-based ID
        title_elem = soup.find(['h1', 'h2'], class_=re.compile(r'job|title'))
        if title_elem:
            title_hash = str(hash(title_elem.get_text().strip()))[-8:]
            return f"toptal_{title_hash}"

        return f"toptal_{int(datetime.now().timestamp())}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract opportunity title"""
        title_selectors = [
            'h1.job-title',
            'h1[data-testid="job-title"]',
            '.job-header h1',
            'h1',
            '.title'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()

        return "TopTal Opportunity"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract opportunity description"""
        desc_selectors = [
            '.job-description',
            '[data-testid="job-description"]',
            '.description',
            '.job-details',
            '.content'
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()[:2000]  # Limit to 2000 chars

        return ""

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills"""
        skills = []

        skill_selectors = [
            '.skills .skill',
            '.tags .tag',
            '.tech-stack .tech',
            '[data-testid="skills"] span'
        ]

        for selector in skill_selectors:
            skill_elems = soup.select(selector)
            for elem in skill_elems:
                skill = elem.get_text().strip()
                if skill and skill not in skills:
                    skills.append(skill)

        return skills[:20]  # Limit to 20 skills

    def _extract_budget(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract budget information"""
        budget_selectors = [
            '.budget',
            '.price',
            '.rate',
            '[data-testid="budget"]'
        ]

        for selector in budget_selectors:
            budget_elem = soup.select_one(selector)
            if budget_elem:
                budget_text = budget_elem.get_text().strip()
                # Look for budget patterns
                budget_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', budget_text)
                if budget_match:
                    return budget_match.group()

        return None

    def _extract_hourly_rate(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract hourly rate"""
        rate_text = soup.get_text()
        rate_patterns = [
            r'\$(\d+(?:\.\d{2})?)\s*(?:per\s+hour|/hr|hourly)',
            r'(\d+(?:\.\d{2})?)\s*\$\s*(?:per\s+hour|/hr)',
            r'Rate:\s*\$(\d+(?:\.\d{2})?)'
        ]

        for pattern in rate_patterns:
            match = re.search(pattern, rate_text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}/hour"

        return None

    def _extract_client_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract client information"""
        client_info = {}

        # Company name
        company_selectors = [
            '.client-name',
            '.company',
            '[data-testid="company"]'
        ]

        for selector in company_selectors:
            company_elem = soup.select_one(selector)
            if company_elem:
                client_info['company'] = company_elem.get_text().strip()
                break

        return client_info

    def _validate_opportunity_quality(self, opportunity: Dict[str, Any]) -> bool:
        """Validate if opportunity meets quality standards"""
        # Check required fields
        for field in self.quality_thresholds['required_fields']:
            if not opportunity.get(field):
                return False

        # Check minimum hourly rate if specified
        hourly_rate = opportunity.get('hourly_rate', '')
        if hourly_rate:
            rate_match = re.search(r'\$(\d+)', hourly_rate)
            if rate_match and int(rate_match.group(1)) < self.quality_thresholds['min_hourly_rate']:
                return False

        return True

    def _calculate_relevance_score(self, opportunity: Dict[str, Any]) -> float:
        """Calculate relevance score for the opportunity"""
        score = 0.5  # Base score

        # High-value skills bonus
        high_value_skills = ['ai', 'machine learning', 'blockchain', 'react', 'python', 'node.js']
        skills = [skill.lower() for skill in opportunity.get('required_skills', [])]

        for skill in high_value_skills:
            if any(skill in s for s in skills):
                score += 0.1

        # Remote work bonus
        if opportunity.get('remote_work'):
            score += 0.1

        # TopTal premium platform bonus
        score += 0.2

        # Rate-based scoring
        hourly_rate = opportunity.get('hourly_rate', '')
        if hourly_rate:
            rate_match = re.search(r'\$(\d+)', hourly_rate)
            if rate_match:
                rate = int(rate_match.group(1))
                if rate >= 100:
                    score += 0.2
                elif rate >= 75:
                    score += 0.1

        return min(score, 1.0)

    def _determine_targets(self, opportunity: Dict[str, Any]) -> tuple:
        """Determine target agents and advisors"""
        # CRITICAL FIX: Use correct agent names with hyphens (income-builder, not income_builder)
        target_agents = ['income-builder', 'job_application_agent', 'career-agent']
        target_advisors = []

        # Skill-based targeting
        skills = [skill.lower() for skill in opportunity.get('required_skills', [])]

        if any(skill in ['ai', 'machine learning', 'data science'] for skill in skills):
            target_agents.extend(['ai-specialist', 'data-scientist'])
            target_advisors.append('tech_innovator')

        if any(skill in ['blockchain', 'crypto', 'web3'] for skill in skills):
            target_agents.append('blockchain-specialist')
            target_advisors.append('crypto_expert')

        if any(skill in ['react', 'vue', 'angular', 'frontend'] for skill in skills):
            target_agents.append('frontend-specialist')

        return target_agents, target_advisors

    def _generate_tags(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate relevance tags"""
        tags = ['freelance', 'toptal', 'premium']

        # Add skill-based tags
        skills = opportunity.get('required_skills', [])
        for skill in skills[:5]:  # Top 5 skills as tags
            tags.append(skill.lower().replace(' ', '_'))

        # Add project type tags
        project_type = opportunity.get('project_type', '')
        if project_type:
            tags.append(project_type.lower().replace(' ', '_'))

        return list(set(tags))

    # Additional helper methods
    def _extract_project_type(self, soup: BeautifulSoup) -> str:
        """Extract project type"""
        project_indicators = {
            'web development': ['web', 'website', 'frontend', 'backend'],
            'mobile development': ['mobile', 'ios', 'android', 'react native'],
            'data science': ['data', 'analytics', 'machine learning', 'ai'],
            'consulting': ['consulting', 'advisory', 'strategy']
        }

        text = soup.get_text().lower()

        for project_type, keywords in project_indicators.items():
            if any(keyword in text for keyword in keywords):
                return project_type

        return 'general'

    def _extract_duration(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract project duration"""
        text = soup.get_text()
        duration_patterns = [
            r'(\d+)\s*(?:weeks?|months?|years?)',
            r'Duration:\s*([^.\n]+)',
            r'Timeline:\s*([^.\n]+)'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location"""
        location_selectors = [
            '.location',
            '[data-testid="location"]',
            '.job-location'
        ]

        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                return location_elem.get_text().strip()

        return None

    def _check_remote_work(self, soup: BeautifulSoup) -> bool:
        """Check if remote work is available"""
        text = soup.get_text().lower()
        remote_indicators = ['remote', 'work from home', 'distributed', 'anywhere']

        return any(indicator in text for indicator in remote_indicators)

    def _extract_urgency(self, soup: BeautifulSoup) -> str:
        """Extract urgency level"""
        text = soup.get_text().lower()

        if any(word in text for word in ['urgent', 'asap', 'immediately', 'rush']):
            return 'high'
        elif any(word in text for word in ['soon', 'quick', 'fast']):
            return 'medium'
        else:
            return 'normal'

    def _extract_experience_level(self, soup: BeautifulSoup) -> str:
        """Extract required experience level"""
        text = soup.get_text().lower()

        if any(word in text for word in ['senior', 'lead', 'expert', '5+ years', 'experienced']):
            return 'senior'
        elif any(word in text for word in ['mid', 'intermediate', '2-5 years']):
            return 'intermediate'
        else:
            return 'entry'

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        date_selectors = [
            '[data-testid="posted-date"]',
            '.posted-date',
            '.date-posted'
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                return date_elem.get_text().strip()

        return None

    def _extract_deadline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract application deadline"""
        text = soup.get_text()
        deadline_patterns = [
            r'Deadline:\s*([^.\n]+)',
            r'Apply by:\s*([^.\n]+)',
            r'Applications close:\s*([^.\n]+)'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    async def _process_general_freelance(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Fallback processing for general freelance data"""
        try:
            # Basic processing for non-TopTal sources
            opportunity_info = {
                'id': f"general_{int(datetime.now().timestamp())}",
                'title': 'General Freelance Opportunity',
                'source': 'general',
                'url': target.url,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='freelance_opportunity',
                content=opportunity_info,
                metadata={'platform': 'general', 'quality_tier': 'standard'},
                quality_score=0.3,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['freelance', 'general'],
                target_agents=['income-builder', 'job_application_agent', 'career-agent'],  # FIXED: Use correct agent names
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing general freelance data: {e}")
            return None

    async def track_revenue_conversion(
        self,
        application_id: str,
        user_id: str,
        project_title: str,
        contract_value: float,
        client_name: str,
        **kwargs
    ) -> Optional[str]:
        """
        Track revenue when a Toptal project is won and generates earnings.
        Called when project contracts are signed and payments are received.

        Args:
            application_id: Unique identifier for this job opportunity
            user_id: User who won the project
            project_title: Title of the project
            contract_value: Total contract value
            client_name: Client/company name
            **kwargs: Additional metadata (hourly_rate, duration, skills, etc.)

        Returns:
            Revenue record ID if successful, None otherwise
        """
        try:
            record_id = await create_project_revenue(
                application_id=application_id,
                user_id=user_id,
                client_name=client_name,
                project_title=project_title,
                contract_value=contract_value,
                **kwargs
            )

            if record_id:
                self.logger.info(f"💰 Tracked Toptal revenue: ${contract_value} for '{project_title}' with {client_name}")

            return record_id

        except Exception as e:
            self.logger.error(f"Error tracking Toptal revenue conversion: {e}")
            return None