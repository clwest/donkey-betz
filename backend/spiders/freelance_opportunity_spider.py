"""
Freelance Opportunity Spider
Finds real freelance jobs that can be completed by our AI agents
"""
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FreelanceOpportunity:
    """Structured freelance job opportunity"""
    job_id: str
    platform: str
    title: str
    description: str
    budget: Optional[float]
    budget_type: str  # 'fixed' or 'hourly'
    skills_required: List[str]
    deadline: Optional[str]
    client_rating: Optional[float]
    url: str
    agent_suitability: float  # 0-1 score for how well agents can do this
    recommended_agents: List[str]
    estimated_completion_time: int  # hours
    confidence_score: float


class FreelanceOpportunitySpider:
    """
    Spider that finds freelance jobs suitable for AI agent completion.
    Focuses on: content writing, data analysis, code generation, design work.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.session = None

        # Agent capabilities mapping
        self.agent_capabilities = {
            'content_writing': [
                'content_creator_agent',
                'viral_content_agent',
                'seo_optimizer_agent',
                'copywriting_agent'
            ],
            'data_analysis': [
                'data_analyst_agent',
                'market_research_agent',
                'business_intelligence_agent',
                'report_generator_agent'
            ],
            'programming': [
                'code_generator_agent',
                'api_builder_agent',
                'automation_agent',
                'script_writer_agent'
            ],
            'design': [
                'ui_designer_agent',
                'graphics_creator_agent',
                'presentation_designer_agent'
            ],
            'research': [
                'research_analyst_agent',
                'competitive_analysis_agent',
                'market_research_agent'
            ]
        }

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': 'FreelanceBot/1.0'}
            )

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def find_opportunities(self) -> List[FreelanceOpportunity]:
        """
        Main method to find freelance opportunities.
        In production, this would scrape real platforms.
        """
        opportunities = []

        # For now, generate realistic mock opportunities
        # In production, would scrape: Upwork, Freelancer, Fiverr, etc.
        mock_opportunities = await self._generate_mock_opportunities()

        for opp_data in mock_opportunities:
            opportunity = await self._analyze_opportunity(opp_data)
            if opportunity.agent_suitability >= 0.7:  # Only high-confidence jobs
                opportunities.append(opportunity)
                await self._store_opportunity(opportunity)

        logger.info(f"🎯 Found {len(opportunities)} suitable freelance opportunities")
        return opportunities

    async def _generate_mock_opportunities(self) -> List[Dict]:
        """Generate realistic mock freelance opportunities"""
        return [
            {
                'job_id': 'upw_001',
                'platform': 'Upwork',
                'title': 'Write 10 SEO Blog Posts on AI Tools',
                'description': 'Need 10 high-quality blog posts about AI productivity tools. Each post should be 1500-2000 words, SEO optimized, with examples and screenshots.',
                'budget': 500,
                'budget_type': 'fixed',
                'skills': ['content writing', 'SEO', 'AI knowledge'],
                'deadline': '2025-09-27',
                'client_rating': 4.8,
                'url': 'https://upwork.com/jobs/fake_001'
            },
            {
                'job_id': 'fl_002',
                'platform': 'Freelancer',
                'title': 'Python Script for Data Analysis',
                'description': 'Create Python script to analyze CSV sales data, generate reports with visualizations, and export to PDF.',
                'budget': 300,
                'budget_type': 'fixed',
                'skills': ['Python', 'pandas', 'data visualization'],
                'deadline': '2025-09-25',
                'client_rating': 4.5,
                'url': 'https://freelancer.com/projects/fake_002'
            },
            {
                'job_id': 'fiv_003',
                'platform': 'Fiverr',
                'title': 'Market Research Report on EV Industry',
                'description': 'Comprehensive market research report on electric vehicle industry, including competitor analysis, market trends, and growth projections.',
                'budget': 750,
                'budget_type': 'fixed',
                'skills': ['market research', 'business analysis', 'report writing'],
                'deadline': '2025-09-30',
                'client_rating': 4.9,
                'url': 'https://fiverr.com/gigs/fake_003'
            },
            {
                'job_id': 'upw_004',
                'platform': 'Upwork',
                'title': 'Build REST API with Node.js',
                'description': 'Need REST API for e-commerce platform. Must include user auth, product CRUD, order management, and payment integration.',
                'budget': 1200,
                'budget_type': 'fixed',
                'skills': ['Node.js', 'REST API', 'MongoDB', 'JWT'],
                'deadline': '2025-10-05',
                'client_rating': 4.7,
                'url': 'https://upwork.com/jobs/fake_004'
            },
            {
                'job_id': 'top_005',
                'platform': 'Toptal',
                'title': 'Financial Data Analysis Dashboard',
                'description': 'Create interactive dashboard for financial data analysis with real-time updates and predictive analytics.',
                'budget': 150,
                'budget_type': 'hourly',
                'skills': ['data analysis', 'dashboard creation', 'financial modeling'],
                'deadline': None,
                'client_rating': 5.0,
                'url': 'https://toptal.com/projects/fake_005'
            }
        ]

    async def _analyze_opportunity(self, opp_data: Dict) -> FreelanceOpportunity:
        """
        Analyze opportunity to determine agent suitability.
        Uses AI to understand requirements and match with agent capabilities.
        """
        # Determine which agents can handle this job
        recommended_agents = []
        job_categories = self._categorize_job(opp_data['skills'])

        for category in job_categories:
            if category in self.agent_capabilities:
                recommended_agents.extend(self.agent_capabilities[category])

        # Calculate suitability score
        suitability = self._calculate_suitability(opp_data, recommended_agents)

        # Estimate completion time based on job type
        completion_time = self._estimate_completion_time(opp_data)

        # Calculate confidence score
        confidence = self._calculate_confidence(opp_data, recommended_agents)

        return FreelanceOpportunity(
            job_id=opp_data['job_id'],
            platform=opp_data['platform'],
            title=opp_data['title'],
            description=opp_data['description'],
            budget=opp_data.get('budget'),
            budget_type=opp_data['budget_type'],
            skills_required=opp_data['skills'],
            deadline=opp_data.get('deadline'),
            client_rating=opp_data.get('client_rating'),
            url=opp_data['url'],
            agent_suitability=suitability,
            recommended_agents=list(set(recommended_agents)),
            estimated_completion_time=completion_time,
            confidence_score=confidence
        )

    def _categorize_job(self, skills: List[str]) -> List[str]:
        """Categorize job based on required skills"""
        categories = []
        skills_lower = [s.lower() for s in skills]

        if any(term in ' '.join(skills_lower) for term in ['content', 'writing', 'blog', 'seo', 'article']):
            categories.append('content_writing')

        if any(term in ' '.join(skills_lower) for term in ['data', 'analysis', 'analytics', 'visualization']):
            categories.append('data_analysis')

        if any(term in ' '.join(skills_lower) for term in ['python', 'javascript', 'api', 'node', 'code', 'script']):
            categories.append('programming')

        if any(term in ' '.join(skills_lower) for term in ['design', 'ui', 'ux', 'graphics']):
            categories.append('design')

        if any(term in ' '.join(skills_lower) for term in ['research', 'market', 'competitive', 'report']):
            categories.append('research')

        return categories

    def _calculate_suitability(self, opp_data: Dict, agents: List[str]) -> float:
        """Calculate how suitable this job is for our agents"""
        score = 0.0

        # Have capable agents
        if len(agents) > 0:
            score += 0.3

        # Good budget
        if opp_data.get('budget'):
            if opp_data['budget'] >= 200:
                score += 0.2
            if opp_data['budget'] >= 500:
                score += 0.1

        # Reasonable deadline
        if opp_data.get('deadline'):
            days_to_deadline = self._days_until(opp_data['deadline'])
            if days_to_deadline >= 3:
                score += 0.2
        else:
            score += 0.2  # No deadline is good

        # Good client rating
        if opp_data.get('client_rating', 0) >= 4.5:
            score += 0.1

        # Job type matches our strengths
        job_types = self._categorize_job(opp_data['skills'])
        if 'content_writing' in job_types or 'data_analysis' in job_types:
            score += 0.1

        return min(score, 1.0)

    def _estimate_completion_time(self, opp_data: Dict) -> int:
        """Estimate hours needed to complete the job"""
        base_time = 4  # Base time for any job

        # Adjust based on job type
        if 'content writing' in ' '.join(opp_data['skills']).lower():
            if '10' in opp_data['title'] or 'multiple' in opp_data['description'].lower():
                base_time = 12
            else:
                base_time = 4

        if 'api' in ' '.join(opp_data['skills']).lower():
            base_time = 16

        if 'research' in ' '.join(opp_data['skills']).lower():
            base_time = 8

        return base_time

    def _calculate_confidence(self, opp_data: Dict, agents: List[str]) -> float:
        """Calculate confidence in successful completion"""
        confidence = 0.5  # Base confidence

        # More agents = higher confidence
        if len(agents) >= 3:
            confidence += 0.2
        elif len(agents) >= 1:
            confidence += 0.1

        # Clear requirements = higher confidence
        if len(opp_data['description']) > 100:
            confidence += 0.1

        # Good budget = higher confidence
        if opp_data.get('budget', 0) >= 500:
            confidence += 0.1

        # Platform reputation
        if opp_data['platform'] in ['Upwork', 'Toptal']:
            confidence += 0.1

        return min(confidence, 0.95)

    def _days_until(self, date_str: str) -> int:
        """Calculate days until deadline"""
        try:
            deadline = datetime.strptime(date_str, '%Y-%m-%d')
            delta = deadline - datetime.now()
            return delta.days
        except:
            return 30  # Default to 30 days if parsing fails

    async def _store_opportunity(self, opportunity: FreelanceOpportunity):
        """Store opportunity in Redis for processing"""
        if self.redis_client:
            key = f"freelance:opportunity:{opportunity.job_id}"
            data = {
                'job_id': opportunity.job_id,
                'platform': opportunity.platform,
                'title': opportunity.title,
                'description': opportunity.description,
                'budget': opportunity.budget,
                'budget_type': opportunity.budget_type,
                'skills_required': opportunity.skills_required,
                'deadline': opportunity.deadline,
                'client_rating': opportunity.client_rating,
                'url': opportunity.url,
                'agent_suitability': opportunity.agent_suitability,
                'recommended_agents': opportunity.recommended_agents,
                'estimated_completion_time': opportunity.estimated_completion_time,
                'confidence_score': opportunity.confidence_score,
                'found_at': datetime.now().isoformat(),
                'status': 'new'
            }

            self.redis_client.setex(key, 86400, json.dumps(data))  # 24 hour TTL

            # Add to opportunity queue
            self.redis_client.lpush('freelance:queue:new', opportunity.job_id)

            # Publish notification
            self.redis_client.publish('freelance:new_opportunity', json.dumps({
                'job_id': opportunity.job_id,
                'title': opportunity.title,
                'budget': opportunity.budget,
                'platform': opportunity.platform
            }))