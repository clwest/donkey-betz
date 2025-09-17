"""
99designs Intelligence Spider - Design Competition Platform
==========================================================

Specialized spider for gathering design competition opportunities from 99designs.
Focuses on graphic design contests, logo competitions, and creative projects.

Target Markets:
- Logo design competitions
- Web design contests
- Print design projects
- Packaging design
- Business card design
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class NinetyNineDesignsIntelligenceSpider(BaseIntelligenceSpider):
    """
    99designs intelligence gathering spider.

    Specializes in:
    - Logo design competitions
    - Web design contests
    - Print and marketing material design
    - Packaging and product design
    - Brand identity projects
    """

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # 99designs-specific configuration
        self.design_categories = [
            'logo-design', 'web-page-design', 'business-card-design',
            'book-cover-design', 'app-design', 'packaging-design',
            'banner-ad-design', 'illustration', 'print-design',
            'powerpoint-design', 'product-design'
        ]

        # Prize tier classifications
        self.prize_tiers = {
            'bronze': (0, 299),
            'silver': (300, 599),
            'gold': (600, 999),
            'platinum': (1000, 2499),
            'diamond': (2500, float('inf'))
        }

        # Quality thresholds
        self.min_prize_amount = 100  # Minimum contest prize
        self.quality_indicators = [
            'guaranteed', 'featured', 'private', 'urgent'
        ]

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process 99designs data into structured intelligence"""
        try:
            if '99designs.com' in target.url:
                return await self._process_design_contest(raw_data, target)
            else:
                return await self._process_general_design(raw_data, target)

        except Exception as e:
            self.logger.error(f"Error processing 99designs data: {e}")
            return None

    async def _process_design_contest(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process 99designs contest data"""
        try:
            contest_info = {}

            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')

                contest_info = {
                    'id': self._extract_contest_id(soup, target.url),
                    'title': self._extract_title(soup),
                    'description': self._extract_description(soup),
                    'brief': self._extract_design_brief(soup),
                    'category': self._extract_category(soup),
                    'subcategory': self._extract_subcategory(soup),
                    'prize_amount': self._extract_prize_amount(soup),
                    'currency': self._extract_currency(soup),
                    'contest_type': self._extract_contest_type(soup),
                    'duration': self._extract_duration(soup),
                    'entries_count': self._extract_entries_count(soup),
                    'designers_count': self._extract_designers_count(soup),
                    'client_info': self._extract_client_info(soup),
                    'requirements': self._extract_requirements(soup),
                    'style_preferences': self._extract_style_preferences(soup),
                    'target_audience': self._extract_target_audience(soup),
                    'industry': self._extract_industry(soup),
                    'contest_level': self._extract_contest_level(soup),
                    'time_left': self._extract_time_left(soup),
                    'guarantee_status': self._check_guarantee_status(soup),
                    'featured_status': self._check_featured_status(soup),
                    'private_contest': self._check_private_status(soup),
                    'source': '99designs'
                }

            # Validate and score
            if not self._validate_contest_quality(contest_info):
                return None

            quality_score = self._calculate_quality_score(contest_info)
            target_agents, target_advisors = self._determine_targets(contest_info)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='design_contest',
                content=contest_info,
                metadata={
                    'platform': '99designs',
                    'contest_type': 'design_competition',
                    'prize_tier': self._classify_prize_tier(contest_info.get('prize_amount')),
                    'category': contest_info.get('category'),
                    'processing_timestamp': datetime.now(timezone.utc).isoformat()
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=self._generate_tags(contest_info),
                target_agents=target_agents,
                target_advisors=target_advisors
            )

        except Exception as e:
            self.logger.error(f"Error processing 99designs contest: {e}")
            return None

    def _extract_contest_id(self, soup: BeautifulSoup, url: str) -> str:
        """Extract contest ID"""
        # Try URL pattern
        id_match = re.search(r'/contests/(\d+)', url)
        if id_match:
            return f"99d_{id_match.group(1)}"

        # Try data attributes
        contest_elem = soup.find(['div', 'article'], {'data-contest-id': True})
        if contest_elem:
            return f"99d_{contest_elem['data-contest-id']}"

        # Fallback
        return f"99d_{int(datetime.now().timestamp())}"

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract contest title"""
        title_selectors = [
            'h1.contest-title',
            '.contest-header h1',
            'h1[data-testid="contest-title"]',
            '.title h1',
            'h1'
        ]

        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()

        return "99designs Contest"

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract contest description"""
        desc_selectors = [
            '.contest-description',
            '.description',
            '.brief-description',
            '.contest-brief'
        ]

        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                return desc_elem.get_text().strip()[:2000]

        return ""

    def _extract_design_brief(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract detailed design brief"""
        brief = {}

        # Company/project name
        company_elem = soup.select_one('.company-name, .project-name')
        if company_elem:
            brief['company_name'] = company_elem.get_text().strip()

        # What they do
        business_elem = soup.select_one('.business-description, .what-do')
        if business_elem:
            brief['business_description'] = business_elem.get_text().strip()

        # Design requirements
        requirements_elem = soup.select_one('.design-requirements, .requirements')
        if requirements_elem:
            brief['requirements'] = requirements_elem.get_text().strip()

        return brief

    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract contest category"""
        category_selectors = [
            '.category',
            '.contest-category',
            '[data-testid="category"]',
            '.breadcrumb a:last-child'
        ]

        for selector in category_selectors:
            category_elem = soup.select_one(selector)
            if category_elem:
                return category_elem.get_text().strip()

        # Try to infer from URL
        url_category = None
        for category in self.design_categories:
            if category in soup.get_text().lower():
                url_category = category.replace('-', ' ').title()
                break

        return url_category or "Design"

    def _extract_prize_amount(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract contest prize amount"""
        prize_selectors = [
            '.prize',
            '.contest-prize',
            '.award-amount',
            '[data-testid="prize"]'
        ]

        for selector in prize_selectors:
            prize_elem = soup.select_one(selector)
            if prize_elem:
                prize_text = prize_elem.get_text().strip()

                # Extract numeric value
                prize_match = re.search(r'[\$]?(\d+(?:,\d{3})*)', prize_text)
                if prize_match:
                    return int(prize_match.group(1).replace(',', ''))

        return None

    def _extract_currency(self, soup: BeautifulSoup) -> str:
        """Extract currency"""
        text = soup.get_text()

        if '$' in text or 'USD' in text:
            return 'USD'
        elif '€' in text or 'EUR' in text:
            return 'EUR'
        elif '£' in text or 'GBP' in text:
            return 'GBP'
        else:
            return 'USD'  # Default

    def _extract_contest_type(self, soup: BeautifulSoup) -> str:
        """Extract contest type"""
        text = soup.get_text().lower()

        if 'logo' in text:
            return 'logo_design'
        elif 'web' in text:
            return 'web_design'
        elif 'business card' in text:
            return 'business_card'
        elif 'packaging' in text:
            return 'packaging'
        elif 'book cover' in text:
            return 'book_cover'
        else:
            return 'general_design'

    def _extract_duration(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contest duration"""
        text = soup.get_text()

        duration_patterns = [
            r'(\d+)\s*days?\s*left',
            r'Contest ends in\s*(\d+)\s*days?',
            r'(\d+)\s*days?\s*remaining'
        ]

        for pattern in duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)} days"

        return None

    def _extract_entries_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of entries"""
        text = soup.get_text()

        entry_patterns = [
            r'(\d+)\s*entries?',
            r'(\d+)\s*designs?',
            r'(\d+)\s*submissions?'
        ]

        for pattern in entry_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _extract_designers_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of participating designers"""
        text = soup.get_text()

        designer_patterns = [
            r'(\d+)\s*designers?',
            r'(\d+)\s*participants?'
        ]

        for pattern in designer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _extract_client_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract client information"""
        client_info = {}

        # Client name
        client_selectors = [
            '.client-name',
            '.contest-holder',
            '.user-name'
        ]

        for selector in client_selectors:
            client_elem = soup.select_one(selector)
            if client_elem:
                client_info['name'] = client_elem.get_text().strip()
                break

        # Client rating/level
        rating_elem = soup.select_one('.client-rating, .user-level')
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                client_info['rating'] = float(rating_match.group(1))

        return client_info

    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """Extract design requirements"""
        requirements = []

        # Look for requirement lists
        req_lists = soup.select('.requirements ul, .specs ul, .checklist ul')
        for req_list in req_lists:
            items = req_list.select('li')
            for item in items:
                req_text = item.get_text().strip()
                if req_text and req_text not in requirements:
                    requirements.append(req_text)

        return requirements[:10]  # Limit to 10 requirements

    def _extract_style_preferences(self, soup: BeautifulSoup) -> List[str]:
        """Extract style preferences"""
        styles = []

        style_keywords = [
            'modern', 'classic', 'minimalist', 'bold', 'elegant',
            'playful', 'professional', 'corporate', 'creative', 'vintage'
        ]

        text = soup.get_text().lower()

        for keyword in style_keywords:
            if keyword in text:
                styles.append(keyword)

        return styles

    def _extract_target_audience(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract target audience information"""
        audience_indicators = [
            'target audience', 'customers', 'clients', 'users'
        ]

        text = soup.get_text().lower()

        for indicator in audience_indicators:
            if indicator in text:
                # Try to extract the sentence containing audience info
                sentences = text.split('.')
                for sentence in sentences:
                    if indicator in sentence:
                        return sentence.strip()[:200]

        return None

    def _extract_industry(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract industry/sector"""
        industries = [
            'technology', 'healthcare', 'finance', 'education', 'retail',
            'restaurant', 'construction', 'real estate', 'consulting',
            'entertainment', 'sports', 'nonprofit'
        ]

        text = soup.get_text().lower()

        for industry in industries:
            if industry in text:
                return industry

        return None

    def _validate_contest_quality(self, contest_info: Dict[str, Any]) -> bool:
        """Validate contest quality"""
        # Must have title and prize
        if not contest_info.get('title'):
            return False

        # Check minimum prize amount
        prize_amount = contest_info.get('prize_amount')
        if not prize_amount or prize_amount < self.min_prize_amount:
            return False

        return True

    def _calculate_quality_score(self, contest_info: Dict[str, Any]) -> float:
        """Calculate contest quality score"""
        score = 0.5  # Base score

        # Prize-based scoring
        prize_amount = contest_info.get('prize_amount', 0)
        if prize_amount >= 1000:
            score += 0.3
        elif prize_amount >= 500:
            score += 0.2
        elif prize_amount >= 300:
            score += 0.1

        # Contest type bonus
        contest_type = contest_info.get('contest_type', '')
        high_value_types = ['logo_design', 'web_design', 'packaging']
        if contest_type in high_value_types:
            score += 0.1

        # Competition level (fewer entries = better opportunity)
        entries_count = contest_info.get('entries_count', 0)
        if entries_count:
            if entries_count < 20:
                score += 0.15
            elif entries_count < 50:
                score += 0.1
            elif entries_count > 100:
                score -= 0.1

        # Quality indicators
        if contest_info.get('guarantee_status'):
            score += 0.1
        if contest_info.get('featured_status'):
            score += 0.05
        if contest_info.get('private_contest'):
            score += 0.05

        # Client rating bonus
        client_info = contest_info.get('client_info', {})
        client_rating = client_info.get('rating')
        if client_rating and client_rating >= 4.0:
            score += 0.1

        return min(score, 1.0)

    def _classify_prize_tier(self, prize_amount: Optional[int]) -> str:
        """Classify prize into tiers"""
        if not prize_amount:
            return 'unknown'

        for tier, (min_val, max_val) in self.prize_tiers.items():
            if min_val <= prize_amount < max_val:
                return tier

        return 'unknown'

    def _determine_targets(self, contest_info: Dict[str, Any]) -> tuple:
        """Determine target agents and advisors"""
        target_agents = ['income_builder', 'design_specialist', 'creative_freelancer']
        target_advisors = []

        category = contest_info.get('category', '').lower()
        contest_type = contest_info.get('contest_type', '')

        # Category-based targeting
        if 'logo' in category or contest_type == 'logo_design':
            target_agents.append('logo_designer')

        if 'web' in category or contest_type == 'web_design':
            target_agents.extend(['web_designer', 'ui_ux_specialist'])

        if 'app' in category:
            target_agents.append('app_designer')

        # High-value contests get advisor attention
        prize_amount = contest_info.get('prize_amount', 0)
        if prize_amount >= 1000:
            target_advisors.append('creative_strategist')

        return target_agents, target_advisors

    def _generate_tags(self, contest_info: Dict[str, Any]) -> List[str]:
        """Generate relevance tags"""
        tags = ['design', '99designs', 'contest', 'creative']

        # Add category tags
        category = contest_info.get('category')
        if category:
            tags.append(category.lower().replace(' ', '_'))

        # Add contest type
        contest_type = contest_info.get('contest_type')
        if contest_type:
            tags.append(contest_type)

        # Add prize tier
        prize_amount = contest_info.get('prize_amount')
        if prize_amount:
            tier = self._classify_prize_tier(prize_amount)
            tags.append(f"prize_{tier}")

        # Add style preferences
        styles = contest_info.get('style_preferences', [])
        for style in styles[:3]:
            tags.append(f"style_{style}")

        # Add industry
        industry = contest_info.get('industry')
        if industry:
            tags.append(f"industry_{industry}")

        return list(set(tags))

    # Additional helper methods
    def _extract_subcategory(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contest subcategory"""
        breadcrumbs = soup.select('.breadcrumb a, .breadcrumbs a')
        if len(breadcrumbs) > 2:
            return breadcrumbs[-2].get_text().strip()
        return None

    def _extract_contest_level(self, soup: BeautifulSoup) -> str:
        """Extract contest level/tier"""
        text = soup.get_text().lower()

        if any(word in text for word in ['bronze', 'starter']):
            return 'bronze'
        elif any(word in text for word in ['silver', 'standard']):
            return 'silver'
        elif any(word in text for word in ['gold', 'premium']):
            return 'gold'
        elif any(word in text for word in ['platinum', 'pro']):
            return 'platinum'
        else:
            return 'standard'

    def _extract_time_left(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract time left in contest"""
        text = soup.get_text()

        time_patterns = [
            r'(\d+)\s*days?\s*left',
            r'(\d+)\s*hours?\s*left',
            r'Contest ends in\s*([^.\n]+)'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _check_guarantee_status(self, soup: BeautifulSoup) -> bool:
        """Check if contest is guaranteed"""
        text = soup.get_text().lower()
        return 'guaranteed' in text

    def _check_featured_status(self, soup: BeautifulSoup) -> bool:
        """Check if contest is featured"""
        text = soup.get_text().lower()
        return 'featured' in text

    def _check_private_status(self, soup: BeautifulSoup) -> bool:
        """Check if contest is private"""
        text = soup.get_text().lower()
        return 'private' in text

    async def _process_general_design(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general design opportunity"""
        try:
            design_info = {
                'id': f"general_{int(datetime.now().timestamp())}",
                'title': 'General Design Opportunity',
                'source': 'general',
                'url': target.url
            }

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type='design_opportunity',
                content=design_info,
                metadata={'platform': 'general'},
                quality_score=0.3,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['design', 'general'],
                target_agents=['income_builder'],
                target_advisors=[]
            )

        except Exception as e:
            self.logger.error(f"Error processing general design data: {e}")
            return None