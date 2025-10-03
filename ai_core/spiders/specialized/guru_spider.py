"""
Guru Intelligence Spider - Freelance Marketplace Data Gathering
==============================================================

Specialized spider for gathering freelance opportunities from Guru.com.
Targets diverse freelance projects across multiple skill categories.

Target Markets:
- Programming & Tech projects
- Design & Creative work
- Writing & Translation
- Administrative & Data entry
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData
from ..revenue_tracker import create_project_revenue


class GuruIntelligenceSpider(BaseIntelligenceSpider):
    """
    Guru.com intelligence gathering spider.

    Specializes in:
    - Programming and development projects
    - Design and creative opportunities
    - Writing and content creation
    - Data entry and administrative tasks
    """

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Guru-specific configuration
        self.categories = [
            'programming-development', 'design-creative', 'writing-translation',
            'administrative-secretarial', 'sales-marketing', 'engineering-architecture',
            'finance-management', 'legal', 'education-training'
        ]

        # Budget ranges for filtering
        self.budget_ranges = {
            'micro': (0, 250),
            'small': (250, 1000),
            'medium': (1000, 5000),
            'large': (5000, 25000),
            'enterprise': (25000, float('inf'))
        }

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Guru data into structured intelligence"""
        try:
            if 'guru.com' in target.url:
                return await self._process_guru_job(raw_data, target)
            else:
                return await self._process_general_job(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing Guru data: {e}")
            return None

    async def _process_guru_job(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Guru job posting"""
        try:
            job_info = {}

            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')

                job_info = {
                    'id': self._extract_job_id(soup, target.url),
                    'title': self._extract_title(soup),
                    'description': self._extract_description(soup),
                    'category': self._extract_category(soup),
                    'subcategory': self._extract_subcategory(soup),
                    'budget': self._extract_budget(soup),
                    'budget_type': self._extract_budget_type(soup),
                    'skills_required': self._extract_skills(soup),
                    'duration': self._extract_duration(soup),
                    'experience_level': self._extract_experience_level(soup),
                    'proposals_count': self._extract_proposals_count(soup),
                    'client_rating': self._extract_client_rating(soup),
                    'client_reviews': self._extract_client_reviews(soup),
                    'posted_date': self._extract_posted_date(soup),
                    'location': self._extract_location(soup),
                    'workload': self._extract_workload(soup),
                    'source': 'guru'
                }

            # Calculate quality score
            quality_score = self._calculate_quality_score(job_info)

            if quality_score < 0.3:  # Filter low-quality jobs
                return None

            # Determine targets
            target_agents, target_advisors = self._determine_targets(job_info)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='freelance_opportunity',
                content=job_info,
                metadata={
                    'platform': 'guru',
                    'category': job_info.get('category'),
                    'budget_tier': self._classify_budget_tier(job_info.get('budget')),
                    'processing_timestamp': datetime.now(timezone.utc).isoformat()
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=self._generate_tags(job_info),
                target_agents=target_agents,
                target_advisors=target_advisors
            )

        except Exception as e:
            self.logger.error(f"Error processing Guru job: {e}")
            return None

    def _extract_job_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract job ID"""
        # Try URL pattern
        id_match = re.search(r'/jobs/(\d+)', url)
        if id_match:
            return f"guru_{id_match.group(1)}"

        # Try data attributes
        job_elem = soup.find(['div', 'article'], {'data-job-id': True})
        if job_elem:
            return f"guru_{job_elem['data-job-id']}"

        # Fallback
        return f"guru_{int(datetime.now().timestamp())}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract job title"""
        title_selectors = [
            'h1.job-title',
            '.job-title h1',
            'h1[data-testid="job-title"]',
            '.title h1',
            'h1'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()

        return "Guru Opportunity"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description"""
        desc_selectors = [
            '.job-description',
            '.description',
            '.job-details',
            '.content .text'
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()[:2000]

        return ""

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract job category"""
        category_selectors = [
            '.category',
            '.job-category',
            '[data-testid="category"]'
        ]

        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                return category_elem.get_text().strip()

        # Extract from URL or breadcrumbs
        breadcrumbs = soup.select('.breadcrumb a, .breadcrumbs a')
        if len(breadcrumbs) > 1:
            return breadcrumbs[1].get_text().strip()

        return "General"

    def _extract_budget(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract budget information"""
        budget_selectors = [
            '.budget',
            '.price',
            '.job-budget',
            '[data-testid="budget"]'
        ]

        for selector in budget_selectors:
            budget_elem = soup.select_one(selector)
            if budget_elem:
                budget_text = budget_elem.get_text().strip()

                # Extract numeric budget
                budget_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', budget_text)
                if budget_match:
                    return budget_match.group()

        return None

    def _extract_budget_type(self, soup: BeautifulSoup) -> str:
        """Extract budget type (fixed, hourly, etc.)"""
        text = soup.get_text().lower()

        if any(keyword in text for keyword in ['hourly', 'per hour', '/hr']):
            return 'hourly'
        elif any(keyword in text for keyword in ['fixed', 'project', 'lump sum']):
            return 'fixed'
        else:
            return 'unknown'

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills"""
        skills = []

        # Try specific skill containers
        skill_containers = soup.select('.skills, .tags, .skill-tags')
        for container in skill_containers:
            skill_items = container.select('.skill, .tag, span')
            for item in skill_items:
                skill = item.get_text().strip()
                if skill and skill not in skills:
                    skills.append(skill)

        return skills[:15]

    def _extract_proposals_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of proposals"""
        text = soup.get_text()

        proposal_patterns = [
            r'(\d+)\s*proposals?',
            r'(\d+)\s*bids?',
            r'(\d+)\s*applications?'
        ]

        for pattern in proposal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _extract_client_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract client rating"""
        rating_selectors = [
            '.rating',
            '.client-rating',
            '[data-testid="rating"]'
        ]

        for selector in rating_selectors:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    return float(rating_match.group(1))

        return None

    def _calculate_quality_score(self, job_info: Dict[str, Any]) -> float:
        """Calculate job quality score"""
        score = 0.5  # Base score

        # Budget-based scoring
        budget = job_info.get('budget', '')
        if budget:
            budget_nums = re.findall(r'\d+', budget.replace(',', ''))
            if budget_nums:
                max_budget = max([int(num) for num in budget_nums])
                if max_budget >= 5000:
                    score += 0.3
                elif max_budget >= 1000:
                    score += 0.2
                elif max_budget >= 500:
                    score += 0.1

        # Client rating bonus
        client_rating = job_info.get('client_rating')
        if client_rating and client_rating >= 4.0:
            score += 0.1

        # Skills complexity bonus
        skills = job_info.get('skills_required', [])
        tech_skills = ['python', 'javascript', 'react', 'node.js', 'ai', 'machine learning']
        if any(skill.lower() in tech_skills for skill in skills):
            score += 0.1

        # Competition factor
        proposals_count = job_info.get('proposals_count', 0)
        if proposals_count:
            if proposals_count < 5:
                score += 0.1  # Low competition
            elif proposals_count > 20:
                score -= 0.1  # High competition

        return min(score, 1.0)

    def _classify_budget_tier(self, budget: Optional[str]) -> str:
        """Classify budget into tiers"""
        if not budget:
            return 'unknown'

        budget_nums = re.findall(r'\d+', budget.replace(',', ''))
        if not budget_nums:
            return 'unknown'

        max_budget = max([int(num) for num in budget_nums])

        for tier, (min_val, max_val) in self.budget_ranges.items():
            if min_val <= max_budget < max_val:
                return tier

        return 'unknown'

    def _determine_targets(self, job_info: Dict[str, Any]) -> tuple:
        """Determine target agents and advisors"""
        # CRITICAL FIX: Use correct agent names with hyphens
        target_agents = ['income-builder', 'job_application_agent', 'career-agent']
        target_advisors = []

        category = job_info.get('category', '').lower()
        skills = [skill.lower() for skill in job_info.get('skills_required', [])]

        # Category-based targeting
        if 'programming' in category or 'development' in category:
            target_agents.append('developer-specialist')

        if 'design' in category or 'creative' in category:
            target_agents.append('design-specialist')

        if 'writing' in category or 'content' in category:
            target_agents.append('content-specialist')

        # Skill-based targeting
        if any(skill in ['ai', 'machine learning', 'data science'] for skill in skills):
            target_agents.append('ai-specialist')
            target_advisors.append('tech_innovator')

        return target_agents, target_advisors

    def _generate_tags(self, job_info: Dict[str, Any]) -> List[str]:
        """Generate relevance tags"""
        tags = ['freelance', 'guru']

        # Add category tags
        category = job_info.get('category')
        if category:
            tags.append(category.lower().replace(' ', '_'))

        # Add skill tags
        skills = job_info.get('skills_required', [])
        for skill in skills[:5]:
            tags.append(skill.lower().replace(' ', '_'))

        # Add budget tier tag
        budget = job_info.get('budget')
        if budget:
            tier = self._classify_budget_tier(budget)
            tags.append(f"budget_{tier}")

        return list(set(tags))

    # Additional helper methods
    def _extract_subcategory(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job subcategory"""
        breadcrumbs = soup.select('.breadcrumb a, .breadcrumbs a')
        if len(breadcrumbs) > 2:
            return breadcrumbs[2].get_text().strip()
        return None

    def _extract_duration(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract project duration"""
        text = soup.get_text()
        duration_patterns = [
            r'Duration:\s*([^.\n]+)',
            r'Timeline:\s*([^.\n]+)',
            r'(\d+\s*(?:days?|weeks?|months?))'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_experience_level(self, soup: BeautifulSoup) -> str:
        """Extract required experience level"""
        text = soup.get_text().lower()

        if any(word in text for word in ['expert', 'senior', 'advanced', '5+ years']):
            return 'expert'
        elif any(word in text for word in ['intermediate', 'mid-level', '2-5 years']):
            return 'intermediate'
        elif any(word in text for word in ['beginner', 'entry', 'junior', 'new']):
            return 'beginner'
        else:
            return 'not_specified'

    def _extract_client_reviews(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of client reviews"""
        text = soup.get_text()
        review_patterns = [
            r'(\d+)\s*reviews?',
            r'(\d+)\s*feedbacks?'
        ]

        for pattern in review_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job posted date"""
        date_selectors = [
            '.posted-date',
            '.date-posted',
            '[data-testid="posted-date"]'
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                return date_elem.get_text().strip()

        # Try extracting from text
        text = soup.get_text()
        date_patterns = [
            r'Posted:\s*([^.\n]+)',
            r'(\d+\s*(?:hours?|days?|weeks?)\s*ago)'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract job location"""
        location_selectors = [
            '.location',
            '.job-location',
            '[data-testid="location"]'
        ]

        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                return location_elem.get_text().strip()

        return None

    def _extract_workload(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract workload information"""
        text = soup.get_text().lower()

        if any(keyword in text for keyword in ['full-time', 'full time', '40 hours']):
            return 'full_time'
        elif any(keyword in text for keyword in ['part-time', 'part time', '20 hours']):
            return 'part_time'
        else:
            return None

    async def _process_general_job(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general job data from non-Guru sources"""
        try:
            job_info = {
                'id': f"general_{int(datetime.now().timestamp())}",
                'title': 'General Job Opportunity',
                'source': 'general',
                'url': target.url,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='job_opportunity',
                content=job_info,
                metadata={'platform': 'general'},
                quality_score=0.3,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['job', 'general'],
                target_agents=['income-builder', 'job_application_agent', 'career-agent'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing general job data: {e}")
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
        Track revenue when a Guru project is won and generates earnings.
        Called when project contracts are awarded and payments are received.

        Args:
            application_id: Unique identifier for this job opportunity
            user_id: User who won the project
            project_title: Title of the project
            contract_value: Total contract value
            client_name: Client/company name
            **kwargs: Additional metadata (budget_type, category, skills, etc.)

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
                self.logger.info(f"💰 Tracked Guru revenue: ${contract_value} for '{project_title}' with {client_name}")

            return record_id

        except Exception as e:
            self.logger.error(f"Error tracking Guru revenue conversion: {e}")
            return None