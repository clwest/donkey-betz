"""
PeoplePerHour Intelligence Spider - UK-Based Freelance Platform
==============================================================

Specialized spider for gathering freelance opportunities from PeoplePerHour.
Focuses on UK and European freelance markets with hourly-based projects.

Target Markets:
- Technology & Programming
- Design & Creative
- Writing & Translation
- Marketing & SEO
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class PeoplePerHourIntelligenceSpider(BaseIntelligenceSpider):
    """
    PeoplePerHour intelligence gathering spider.

    Specializes in:
    - Hourly-based freelance projects
    - UK and European market opportunities
    - Small to medium-sized projects
    - Quick turnaround tasks
    """

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # PeoplePerHour-specific configuration
        self.service_categories = [
            'technology', 'design', 'writing', 'marketing', 'business',
            'music-audio', 'video', 'photography', 'translation', 'admin'
        ]

        # Currency support (£, €, $)
        self.supported_currencies = ['£', '€', '$', 'GBP', 'EUR', 'USD']

        # Quality thresholds
        self.min_hourly_rate = 10  # Minimum hourly rate in GBP
        self.min_project_value = 50  # Minimum project value

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process PeoplePerHour data into structured intelligence"""
        try:
            if 'peopleperhour.com' in target.url:
                return await self._process_pph_project(raw_data, target)
            else:
                return await self._process_general_project(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing PeoplePerHour data: {e}")
            return None

    async def _process_pph_project(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process PeoplePerHour project data"""
        try:
            project_info = {}

            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')

                project_info = {
                    'id': self._extract_project_id(soup, target.url),
                    'title': self._extract_title(soup),
                    'description': self._extract_description(soup),
                    'category': self._extract_category(soup),
                    'budget': self._extract_budget(soup),
                    'currency': self._extract_currency(soup),
                    'hourly_rate': self._extract_hourly_rate(soup),
                    'project_type': self._extract_project_type(soup),
                    'skills_required': self._extract_skills(soup),
                    'duration': self._extract_duration(soup),
                    'urgency': self._extract_urgency(soup),
                    'client_info': self._extract_client_info(soup),
                    'proposals_count': self._extract_proposals_count(soup),
                    'location': self._extract_location(soup),
                    'remote_work': self._check_remote_work(soup),
                    'posted_date': self._extract_posted_date(soup),
                    'deadline': self._extract_deadline(soup),
                    'source': 'peopleperhour'
                }

            # Validate and score
            if not self._validate_project_quality(project_info):
                return None

            quality_score = self._calculate_quality_score(project_info)
            target_agents, target_advisors = self._determine_targets(project_info)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='freelance_opportunity',
                content=project_info,
                metadata={
                    'platform': 'peopleperhour',
                    'region': 'uk_europe',
                    'currency': project_info.get('currency', 'GBP'),
                    'project_tier': self._classify_project_tier(project_info),
                    'processing_timestamp': datetime.now(timezone.utc).isoformat()
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=self._generate_tags(project_info),
                target_agents=target_agents,
                target_advisors=target_advisors
            )

        except Exception as e:
            self.logger.error(f"Error processing PeoplePerHour project: {e}")
            return None

    def _extract_project_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract project ID"""
        # Try URL pattern
        id_match = re.search(r'/project/(\d+)', url)
        if id_match:
            return f"pph_{id_match.group(1)}"

        # Try data attributes
        project_elem = soup.find(['div', 'article'], {'data-project-id': True})
        if project_elem:
            return f"pph_{project_elem['data-project-id']}"

        # Fallback
        return f"pph_{int(datetime.now().timestamp())}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract project title"""
        title_selectors = [
            'h1.project-title',
            '.project-header h1',
            'h1[data-testid="project-title"]',
            '.title h1',
            'h1'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()

        return "PeoplePerHour Project"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract project description"""
        desc_selectors = [
            '.project-description',
            '.description',
            '.project-details',
            '.brief',
            '.content'
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()[:2000]

        return ""

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract project category"""
        category_selectors = [
            '.category',
            '.project-category',
            '[data-testid="category"]',
            '.breadcrumb a:last-child'
        ]

        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                return category_elem.get_text().strip()

        return "General"

    def _extract_budget(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract budget information"""
        budget_selectors = [
            '.budget',
            '.price',
            '.project-budget',
            '[data-testid="budget"]'
        ]

        for selector in budget_selectors:
            budget_elem = soup.select_one(selector)
            if budget_elem:
                budget_text = budget_elem.get_text().strip()

                # Extract budget with currency symbols
                budget_patterns = [
                    r'[£€$][\d,]+(?:\s*-\s*[£€$][\d,]+)?',
                    r'[\d,]+\s*[£€$]',
                    r'GBP\s*[\d,]+',
                    r'EUR\s*[\d,]+',
                    r'USD\s*[\d,]+'
                ]

                for pattern in budget_patterns:
                    budget_match = re.search(pattern, budget_text)
                    if budget_match:
                        return budget_match.group()

        return None

    def _extract_currency(self, soup: BeautifulSoup) -> str:
        """Extract currency"""
        text = soup.get_text()

        # Check for currency symbols and codes
        if '£' in text or 'GBP' in text:
            return 'GBP'
        elif '€' in text or 'EUR' in text:
            return 'EUR'
        elif '$' in text or 'USD' in text:
            return 'USD'
        else:
            return 'GBP'  # Default for PeoplePerHour

    def _extract_hourly_rate(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract hourly rate"""
        text = soup.get_text()

        # Patterns for hourly rates
        rate_patterns = [
            r'[£€$](\d+(?:\.\d{2})?)\s*(?:per\s+hour|/hr|hourly)',
            r'(\d+(?:\.\d{2})?)\s*[£€$]\s*(?:per\s+hour|/hr)',
            r'Hourly:\s*[£€$](\d+(?:\.\d{2})?)'
        ]

        for pattern in rate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                currency = self._extract_currency(soup)
                return f"{currency_symbol(currency)}{match.group(1)}/hour"

        return None

    def _extract_project_type(self, soup: BeautifulSoup) -> str:
        """Extract project type"""
        text = soup.get_text().lower()

        if any(keyword in text for keyword in ['hourly', 'per hour', 'ongoing']):
            return 'hourly'
        elif any(keyword in text for keyword in ['fixed', 'project', 'one-time']):
            return 'fixed'
        else:
            return 'unknown'

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills"""
        skills = []

        # Try specific skill containers
        skill_containers = soup.select('.skills, .tags, .skill-list')
        for container in skill_containers:
            skill_items = container.select('.skill, .tag, span, li')
            for item in skill_items:
                skill = item.get_text().strip()
                if skill and len(skill) < 50 and skill not in skills:
                    skills.append(skill)

        return skills[:20]

    def _extract_client_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract client information"""
        client_info = {}

        # Client name/company
        client_selectors = [
            '.client-name',
            '.employer',
            '.company-name'
        ]

        for selector in client_selectors:
            client_elem = soup.select_one(selector)
            if client_elem:
                client_info['name'] = client_elem.get_text().strip()
                break

        # Client rating
        rating_elem = soup.select_one('.client-rating, .rating')
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                client_info['rating'] = float(rating_match.group(1))

        return client_info

    def _extract_proposals_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of proposals"""
        text = soup.get_text()

        proposal_patterns = [
            r'(\d+)\s*proposals?',
            r'(\d+)\s*bids?',
            r'(\d+)\s*freelancers? applied'
        ]

        for pattern in proposal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _validate_project_quality(self, project_info: Dict[str, Any]) -> bool:
        """Validate project quality"""
        # Must have title and description
        if not project_info.get('title') or not project_info.get('description'):
            return False

        # Check minimum budget/rate
        budget = project_info.get('budget', '')
        hourly_rate = project_info.get('hourly_rate', '')

        if budget:
            budget_value = self._extract_numeric_value(budget)
            if budget_value and budget_value < self.min_project_value:
                return False

        if hourly_rate:
            rate_value = self._extract_numeric_value(hourly_rate)
            if rate_value and rate_value < self.min_hourly_rate:
                return False

        return True

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from budget/rate text"""
        if not text:
            return None

        # Remove currency symbols and extract numbers
        clean_text = re.sub(r'[£€$,]', '', text)
        number_match = re.search(r'(\d+(?:\.\d{2})?)', clean_text)

        if number_match:
            return float(number_match.group(1))

        return None

    def _calculate_quality_score(self, project_info: Dict[str, Any]) -> float:
        """Calculate project quality score"""
        score = 0.5  # Base score

        # Budget-based scoring
        budget = project_info.get('budget', '')
        if budget:
            budget_value = self._extract_numeric_value(budget)
            if budget_value:
                if budget_value >= 1000:
                    score += 0.3
                elif budget_value >= 500:
                    score += 0.2
                elif budget_value >= 200:
                    score += 0.1

        # Skills complexity
        skills = project_info.get('skills_required', [])
        tech_skills = ['javascript', 'python', 'react', 'node.js', 'ai', 'blockchain']
        if any(skill.lower() in tech_skills for skill in skills):
            score += 0.15

        # Client rating bonus
        client_info = project_info.get('client_info', {})
        client_rating = client_info.get('rating')
        if client_rating and client_rating >= 4.0:
            score += 0.1

        # Competition factor
        proposals_count = project_info.get('proposals_count', 0)
        if proposals_count:
            if proposals_count < 5:
                score += 0.1
            elif proposals_count > 15:
                score -= 0.1

        # UK/European market bonus
        location = project_info.get('location', '').lower()
        if any(country in location for country in ['uk', 'united kingdom', 'europe', 'germany', 'france']):
            score += 0.05

        return min(score, 1.0)

    def _classify_project_tier(self, project_info: Dict[str, Any]) -> str:
        """Classify project tier"""
        budget = project_info.get('budget', '')
        if not budget:
            return 'unknown'

        budget_value = self._extract_numeric_value(budget)
        if not budget_value:
            return 'unknown'

        if budget_value >= 2000:
            return 'premium'
        elif budget_value >= 500:
            return 'standard'
        else:
            return 'basic'

    def _determine_targets(self, project_info: Dict[str, Any]) -> tuple:
        """Determine target agents and advisors"""
        target_agents = ['income_builder', 'freelance_specialist', 'uk_market_specialist']
        target_advisors = []

        category = project_info.get('category', '').lower()
        skills = [skill.lower() for skill in project_info.get('skills_required', [])]

        # Category-based targeting
        if 'technology' in category or 'programming' in category:
            target_agents.append('developer_specialist')

        if 'design' in category:
            target_agents.append('design_specialist')

        if 'marketing' in category:
            target_agents.append('marketing_specialist')

        # Skill-based targeting
        if any(skill in ['ai', 'machine learning'] for skill in skills):
            target_advisors.append('tech_innovator')

        return target_agents, target_advisors

    def _generate_tags(self, project_info: Dict[str, Any]) -> List[str]:
        """Generate relevance tags"""
        tags = ['freelance', 'peopleperhour', 'uk_market']

        # Add category tags
        category = project_info.get('category')
        if category:
            tags.append(category.lower().replace(' ', '_'))

        # Add skill tags
        skills = project_info.get('skills_required', [])
        for skill in skills[:5]:
            tags.append(skill.lower().replace(' ', '_'))

        # Add project type
        project_type = project_info.get('project_type')
        if project_type:
            tags.append(project_type)

        # Add currency tag
        currency = project_info.get('currency')
        if currency:
            tags.append(currency.lower())

        return list(set(tags))

    # Additional helper methods
    def _extract_duration(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract project duration"""
        text = soup.get_text()
        duration_patterns = [
            r'Duration:\s*([^.\n]+)',
            r'Timeline:\s*([^.\n]+)',
            r'(\d+\s*(?:hours?|days?|weeks?|months?))'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_urgency(self, soup: BeautifulSoup) -> str:
        """Extract urgency level"""
        text = soup.get_text().lower()

        if any(word in text for word in ['urgent', 'asap', 'immediately']):
            return 'high'
        elif any(word in text for word in ['soon', 'quick']):
            return 'medium'
        else:
            return 'normal'

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract project location"""
        location_selectors = [
            '.location',
            '.project-location',
            '[data-testid="location"]'
        ]

        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                return location_elem.get_text().strip()

        return None

    def _check_remote_work(self, soup: BeautifulSoup) -> bool:
        """Check if remote work is available"""
        text = soup.get_text().lower()
        remote_indicators = ['remote', 'work from home', 'online', 'anywhere']

        return any(indicator in text for indicator in remote_indicators)

    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        date_selectors = [
            '.posted-date',
            '.date-posted',
            '[data-testid="posted-date"]'
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                return date_elem.get_text().strip()

        return None

    def _extract_deadline(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract deadline"""
        text = soup.get_text()
        deadline_patterns = [
            r'Deadline:\s*([^.\n]+)',
            r'Due:\s*([^.\n]+)'
        ]

        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    async def _process_general_project(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general project data"""
        try:
            project_info = {
                'id': f"general_{int(datetime.now().timestamp())}",
                'title': 'General Project Opportunity',
                'source': 'general',
                'url': target.url
            }

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='project_opportunity',
                content=project_info,
                metadata={'platform': 'general'},
                quality_score=0.3,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['project', 'general'],
                target_agents=['income_builder'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing general project data: {e}")
            return None


def currency_symbol(currency_code: str) -> str:
    """Get currency symbol from code"""
    symbols = {
        'GBP': '£',
        'EUR': '€',
        'USD': '$'
    }
    return symbols.get(currency_code, currency_code)