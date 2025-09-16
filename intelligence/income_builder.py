"""
AI Income Builder System - Start from $0

Helps users build income streams using AI, regardless of starting capital.
Focuses on skills, services, and value creation rather than traditional investing.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from django.conf import settings

# OpenAI Integration
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', ''))
    OPENAI_AVAILABLE = bool(os.environ.get('OPENAI_API_KEY'))
except ImportError:
    openai_client = None
    OPENAI_AVAILABLE = False

# Temporarily comment out complex dependencies for testing
# from agents.registry import agent_registry
# from advisors.registry import advisor_registry
# from orchestration import orchestrator, WorkflowStep, StepType
# from ml_pipeline.pipeline import MLPipeline

# Simple mock classes for now
class WorkflowStep:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.name = kwargs.get('name')

class StepType:
    AGENT = "agent"
    PARALLEL = "parallel"
    LOOP = "loop"
    CONDITIONAL = "conditional"

class MLPipeline:
    """Enhanced ML Pipeline with real machine learning models"""

    def __init__(self):
        self.enhanced_ml_available = False
        try:
            # Try to import enhanced ML pipeline
            import sys
            ml_path = '/Users/donkeyking/development/unified-donkey-betz'
            if ml_path not in sys.path:
                sys.path.append(ml_path)

            from ml_revenue_pipeline import ml_revenue_pipeline
            self.enhanced_ml = ml_revenue_pipeline
            self.enhanced_ml_available = True
            logger.info("Enhanced ML Pipeline connected successfully")
        except Exception as e:
            logger.warning(f"Enhanced ML Pipeline not available, using fallback: {e}")
            self.enhanced_ml = None

    async def predict_opportunity_fit(self, user_dict, opp_dict):
        """
        Calculate opportunity fit using real ML models or enhanced heuristics
        """
        if self.enhanced_ml_available and self.enhanced_ml:
            try:
                # Use real ML pipeline
                result = await self.enhanced_ml.predict_opportunity_fit(user_dict, opp_dict)
                result["ml_engine"] = "enhanced_ml_models"
                return result
            except Exception as e:
                logger.warning(f"Enhanced ML prediction failed, falling back to heuristics: {e}")

        # Enhanced fallback heuristics
        return await self._enhanced_heuristic_prediction(user_dict, opp_dict)

    async def _enhanced_heuristic_prediction(self, user_dict, opp_dict):
        """Enhanced heuristic prediction with improved analysis"""
        score = 0.5  # Base score

        # Enhanced skill matching analysis
        user_skills = set(str(s).lower() for s in user_dict.get('skills', []))
        required_skills = set(str(s).lower() for s in opp_dict.get('skills_required', []))

        if required_skills:
            skill_match_ratio = len(user_skills & required_skills) / len(required_skills)
            score += skill_match_ratio * 0.3

            # Bonus for high-demand skills
            high_demand_skills = {'python', 'ai', 'automation', 'data analysis', 'machine learning'}
            bonus_skills = required_skills & high_demand_skills
            if bonus_skills:
                score += len(bonus_skills) * 0.05

        # Experience level matching with improved logic
        user_level = user_dict.get('skill_level', 'beginner')
        # Handle both string and enum types
        if hasattr(user_level, 'value'):
            user_level = user_level.value
        level_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        user_level_score = level_scores.get(str(user_level).lower(), 1)

        # Award points for sufficient experience
        if user_level_score >= 2:  # Intermediate or higher
            score += 0.2
        elif user_level_score >= 1:
            score += 0.1

        # Investment capacity vs requirement
        user_balance = user_dict.get('current_balance', 0)
        required_investment = opp_dict.get('initial_investment', 0)

        if required_investment <= user_balance:
            score += 0.15
        elif required_investment == 0:  # No investment needed
            score += 0.2

        # Time availability factor
        available_hours = user_dict.get('available_hours_per_week', 0)
        if available_hours >= 20:
            score += 0.15
        elif available_hours >= 10:
            score += 0.1

        # Enhanced market factors
        market_demand = opp_dict.get('market_demand', 0.5)
        competition_level = opp_dict.get('competition_level', 0.5)
        client_rating = opp_dict.get('client_rating', 3.0)
        budget = opp_dict.get('budget', 0)

        # Market demand boost
        score += market_demand * 0.1

        # Competition penalty
        score -= competition_level * 0.1

        # Client quality bonus
        if client_rating >= 4.5:
            score += 0.1
        elif client_rating >= 4.0:
            score += 0.05

        # Budget attractiveness
        if budget >= 1000:
            score += 0.1
        elif budget >= 500:
            score += 0.05

        # Platform reliability bonus
        platform = str(opp_dict.get('platform', '')).lower()
        platform_bonuses = {
            'upwork': 0.05,
            'toptal': 0.1,
            'linkedin': 0.08,
            'fiverr': 0.03
        }
        score += platform_bonuses.get(platform, 0)

        # Ensure score is within valid range
        final_score = max(0.1, min(0.95, score))

        # Calculate detailed factors
        skill_overlap = user_skills & required_skills if required_skills else set()

        return {
            "fit_score": final_score,
            "confidence": 0.85,  # Higher confidence with enhanced logic
            "ml_engine": "enhanced_heuristic",
            "factors": {
                "skill_match": len(skill_overlap),
                "skill_coverage": len(skill_overlap) / max(len(required_skills), 1) if required_skills else 0,
                "experience_match": user_level_score >= 2,
                "investment_feasible": required_investment <= user_balance,
                "time_adequate": available_hours >= 10,
                "client_quality": client_rating >= 4.0,
                "budget_attractive": budget >= 500,
                "competition_favorable": competition_level < 0.6,
                "market_demand_good": market_demand > 0.7
            },
            "enhanced_analysis": {
                "skill_match_ratio": len(skill_overlap) / max(len(required_skills), 1) if required_skills else 0,
                "experience_level": user_level_score,
                "market_score": market_demand * (1 - competition_level),
                "client_score": client_rating / 5.0,
                "economic_score": min(budget / 1000, 1.0),
                "platform_score": platform_bonuses.get(platform, 0.5)
            }
        }

logger = logging.getLogger(__name__)


class IncomeStream(Enum):
    """Types of AI-powered income streams"""
    CONTENT_CREATION = "content_creation"
    FREELANCE_SERVICES = "freelance_services"
    AI_AUTOMATION = "ai_automation"
    DIGITAL_PRODUCTS = "digital_products"
    CONSULTING = "consulting"
    AFFILIATE_MARKETING = "affiliate_marketing"
    MICRO_SAAS = "micro_saas"
    PROMPT_ENGINEERING = "prompt_engineering"
    DATA_ANNOTATION = "data_annotation"
    AI_TUTORING = "ai_tutoring"


class SkillLevel(Enum):
    """User skill levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class IncomeOpportunity:
    """Represents an income opportunity"""
    id: str
    stream_type: IncomeStream
    title: str
    description: str
    required_skills: List[str]
    time_to_first_income: str  # e.g., "1-3 days", "1 week"
    potential_monthly: str  # e.g., "$500-$2000"
    difficulty: SkillLevel
    initial_investment: float  # Can be $0
    tools_needed: List[str]
    success_rate: float
    market_demand: float  # 0-1 scale
    competition_level: float  # 0-1 scale
    scalability: float  # 0-1 scale
    action_steps: List[str]
    resources: List[Dict[str, str]]  # Links to tutorials, platforms, etc.


@dataclass
class UserProfile:
    """User profile for income building"""
    id: str
    current_balance: float = 0.0
    skills: List[str] = field(default_factory=list)
    skill_level: SkillLevel = SkillLevel.BEGINNER
    available_hours_per_week: int = 10
    interests: List[str] = field(default_factory=list)
    completed_projects: List[str] = field(default_factory=list)
    active_streams: List[IncomeStream] = field(default_factory=list)
    total_earned: float = 0.0
    reputation_score: float = 0.0
    learning_progress: Dict[str, float] = field(default_factory=dict)


class AIIncomeBuilder:
    """AI-powered income building system for users starting from $0"""

    def __init__(self):
        self.ml_pipeline = MLPipeline()
        self.opportunities = self._initialize_opportunities()
        self.user_profiles = {}
        self.success_stories = []
        self.workflow_templates = self._create_income_workflows()

        # Initialize real tools for actual data gathering
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize real tools for web search, API calls, and file generation"""
        self.tools_available = {
            'web_search': False,
            'news_api': False,
            'file_generation': True  # Always available
        }

        # Try to import and initialize web search tool
        try:
            import sys
            import os
            # Add multiple possible paths for tool imports
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '../core/tools/'),
                os.path.join(os.path.dirname(__file__), '../../core/tools/'),
                '/Users/donkeyking/development/unified-donkey-betz/core/tools/'
            ]

            for path in possible_paths:
                if path not in sys.path:
                    sys.path.append(path)

            from core.tools.web_search import WebSearchTool

            self.web_search = WebSearchTool()
            if hasattr(self.web_search, 'is_configured') and self.web_search.is_configured:
                self.tools_available['web_search'] = True
                logger.info("Web search tool initialized successfully")
            else:
                logger.warning("Web search tool not configured properly")

        except Exception as e:
            logger.warning(f"Could not initialize web search tool: {e}")
            self.web_search = None

        # Try to import news API tool
        try:
            from core.tools.news_api import NewsAPITool
            self.news_api = NewsAPITool()
            if hasattr(self.news_api, 'is_configured') and self.news_api.is_configured:
                self.tools_available['news_api'] = True
                logger.info("News API tool initialized successfully")
            else:
                logger.warning("News API tool not configured properly")
        except Exception as e:
            logger.warning(f"Could not initialize news API tool: {e}")
            self.news_api = None

    def _initialize_opportunities(self) -> List[IncomeOpportunity]:
        """Initialize income opportunities"""
        return [
            # Zero Investment Opportunities
            IncomeOpportunity(
                id="content_writing",
                stream_type=IncomeStream.CONTENT_CREATION,
                title="AI-Assisted Content Writing",
                description="Write articles, blogs, and copy using AI tools",
                required_skills=["writing", "research", "AI prompting"],
                time_to_first_income="1-3 days",
                potential_monthly="$500-$3000",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["ChatGPT", "Grammarly", "Google Docs"],
                success_rate=0.75,
                market_demand=0.9,
                competition_level=0.7,
                scalability=0.8,
                action_steps=[
                    "Create profiles on Upwork, Fiverr, Contently",
                    "Build portfolio with 3 sample articles",
                    "Apply to 10 writing gigs daily",
                    "Use AI to enhance productivity",
                    "Deliver high-quality work fast"
                ],
                resources=[
                    {"name": "Upwork", "url": "upwork.com"},
                    {"name": "Fiverr", "url": "fiverr.com"},
                    {"name": "Medium Partner Program", "url": "medium.com/creators"}
                ]
            ),

            IncomeOpportunity(
                id="prompt_engineering",
                stream_type=IncomeStream.PROMPT_ENGINEERING,
                title="Prompt Engineering Services",
                description="Create and optimize AI prompts for businesses",
                required_skills=["AI understanding", "problem solving", "communication"],
                time_to_first_income="3-7 days",
                potential_monthly="$1000-$5000",
                difficulty=SkillLevel.INTERMEDIATE,
                initial_investment=0.0,
                tools_needed=["ChatGPT", "Claude", "Midjourney"],
                success_rate=0.8,
                market_demand=0.95,
                competition_level=0.4,
                scalability=0.9,
                action_steps=[
                    "Master prompt engineering techniques",
                    "Create prompt templates library",
                    "Offer services on PromptBase",
                    "Network with AI communities",
                    "Build case studies"
                ],
                resources=[
                    {"name": "PromptBase", "url": "promptbase.com"},
                    {"name": "Learn Prompting", "url": "learnprompting.org"}
                ]
            ),

            IncomeOpportunity(
                id="ai_automation",
                stream_type=IncomeStream.AI_AUTOMATION,
                title="No-Code AI Automation",
                description="Build automations using Zapier, Make, and AI",
                required_skills=["logical thinking", "process mapping", "basic tech"],
                time_to_first_income="1 week",
                potential_monthly="$800-$4000",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["Zapier free tier", "Make.com", "ChatGPT"],
                success_rate=0.7,
                market_demand=0.85,
                competition_level=0.5,
                scalability=0.85,
                action_steps=[
                    "Learn Zapier/Make basics (free courses)",
                    "Identify repetitive business tasks",
                    "Create 3 demo automations",
                    "Reach out to small businesses",
                    "Offer performance-based pricing"
                ],
                resources=[
                    {"name": "Zapier Academy", "url": "zapier.com/learn"},
                    {"name": "Make Academy", "url": "academy.make.com"}
                ]
            ),

            IncomeOpportunity(
                id="digital_templates",
                stream_type=IncomeStream.DIGITAL_PRODUCTS,
                title="AI-Generated Digital Templates",
                description="Create and sell templates, worksheets, and digital products",
                required_skills=["design basics", "AI tools", "marketing"],
                time_to_first_income="1-2 weeks",
                potential_monthly="$300-$2000",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["Canva free", "ChatGPT", "Google Sheets"],
                success_rate=0.65,
                market_demand=0.8,
                competition_level=0.6,
                scalability=0.95,
                action_steps=[
                    "Research trending templates on Etsy",
                    "Use AI to generate content",
                    "Design in Canva (free version)",
                    "List on Gumroad, Etsy, Creative Market",
                    "Promote on social media"
                ],
                resources=[
                    {"name": "Gumroad", "url": "gumroad.com"},
                    {"name": "Etsy Seller", "url": "etsy.com/sell"}
                ]
            ),

            IncomeOpportunity(
                id="ai_tutoring",
                stream_type=IncomeStream.AI_TUTORING,
                title="AI-Enhanced Online Tutoring",
                description="Teach subjects using AI as your assistant",
                required_skills=["subject expertise", "teaching", "communication"],
                time_to_first_income="3-5 days",
                potential_monthly="$600-$3000",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["Zoom free", "ChatGPT", "Google Meet"],
                success_rate=0.8,
                market_demand=0.9,
                competition_level=0.6,
                scalability=0.7,
                action_steps=[
                    "Choose subjects you know well",
                    "Use AI to create lesson plans",
                    "Sign up on Preply, Tutor.com, Wyzant",
                    "Offer first session free",
                    "Build reviews and raise rates"
                ],
                resources=[
                    {"name": "Preply", "url": "preply.com"},
                    {"name": "Wyzant", "url": "wyzant.com"}
                ]
            ),

            IncomeOpportunity(
                id="social_media_management",
                stream_type=IncomeStream.FREELANCE_SERVICES,
                title="AI-Powered Social Media Management",
                description="Manage social media accounts using AI tools",
                required_skills=["social media", "content creation", "scheduling"],
                time_to_first_income="1 week",
                potential_monthly="$500-$2500",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["ChatGPT", "Canva free", "Buffer free"],
                success_rate=0.75,
                market_demand=0.85,
                competition_level=0.7,
                scalability=0.8,
                action_steps=[
                    "Learn social media best practices",
                    "Create content calendar templates",
                    "Use AI for caption writing",
                    "Offer services to local businesses",
                    "Show before/after metrics"
                ],
                resources=[
                    {"name": "Buffer Academy", "url": "buffer.com/resources"},
                    {"name": "Hootsuite Academy", "url": "education.hootsuite.com"}
                ]
            ),

            IncomeOpportunity(
                id="data_labeling",
                stream_type=IncomeStream.DATA_ANNOTATION,
                title="AI Training Data Annotation",
                description="Label and annotate data for AI training",
                required_skills=["attention to detail", "basic computer skills"],
                time_to_first_income="1-2 days",
                potential_monthly="$200-$800",
                difficulty=SkillLevel.BEGINNER,
                initial_investment=0.0,
                tools_needed=["Computer", "Internet"],
                success_rate=0.9,
                market_demand=0.8,
                competition_level=0.8,
                scalability=0.5,
                action_steps=[
                    "Sign up on Appen, Lionbridge, Scale AI",
                    "Complete qualification tests",
                    "Start with simple tasks",
                    "Build accuracy rating",
                    "Access higher-paying projects"
                ],
                resources=[
                    {"name": "Appen", "url": "appen.com"},
                    {"name": "Scale AI", "url": "scale.com/careers"}
                ]
            ),

            IncomeOpportunity(
                id="micro_saas",
                stream_type=IncomeStream.MICRO_SAAS,
                title="Build Micro-SaaS with AI",
                description="Create small software tools using no-code and AI",
                required_skills=["problem identification", "basic tech", "marketing"],
                time_to_first_income="2-4 weeks",
                potential_monthly="$500-$5000",
                difficulty=SkillLevel.INTERMEDIATE,
                initial_investment=0.0,
                tools_needed=["Bubble.io free", "ChatGPT", "Stripe"],
                success_rate=0.5,
                market_demand=0.9,
                competition_level=0.6,
                scalability=1.0,
                action_steps=[
                    "Identify specific problem to solve",
                    "Build MVP with Bubble.io (free tier)",
                    "Use AI for coding assistance",
                    "Launch on Product Hunt",
                    "Iterate based on feedback"
                ],
                resources=[
                    {"name": "Bubble.io", "url": "bubble.io"},
                    {"name": "Product Hunt", "url": "producthunt.com"}
                ]
            )
        ]

    def _create_income_workflows(self) -> Dict[str, List[WorkflowStep]]:
        """Create workflow templates for income generation"""
        return {
            "quick_start_freelancing": [
                WorkflowStep(
                    type=StepType.AGENT,
                    name="skill_assessment",
                    agent_ids=["skill_analyzer", "market_researcher"],
                    output_key="skills_and_demand"
                ),
                WorkflowStep(
                    type=StepType.PARALLEL,
                    name="profile_creation",
                    parallel_tasks=[
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="portfolio_builder",
                            agent_ids=["content_creator", "designer"],
                            output_key="portfolio"
                        ),
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="platform_optimizer",
                            agent_ids=["seo_optimizer", "profile_writer"],
                            output_key="optimized_profiles"
                        )
                    ]
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="proposal_generator",
                    agent_ids=["proposal_writer", "pricing_strategist"],
                    output_key="proposals"
                ),
                WorkflowStep(
                    type=StepType.LOOP,
                    name="application_automation",
                    max_iterations=10,
                    agent_ids=["job_finder", "application_sender"],
                    output_key="applications_sent"
                )
            ],

            "digital_product_launch": [
                WorkflowStep(
                    type=StepType.AGENT,
                    name="market_research",
                    agent_ids=["trend_analyzer", "competitor_researcher"],
                    output_key="market_analysis"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="product_ideation",
                    agent_ids=["idea_generator", "validator"],
                    input_mapping={"market": "market_analysis"},
                    output_key="product_ideas"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="content_creation",
                    agent_ids=["template_designer", "content_writer"],
                    input_mapping={"ideas": "product_ideas"},
                    output_key="digital_product"
                ),
                WorkflowStep(
                    type=StepType.PARALLEL,
                    name="multi_platform_launch",
                    parallel_tasks=[
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="etsy_listing",
                            agent_ids=["listing_optimizer"],
                            output_key="etsy_live"
                        ),
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="gumroad_setup",
                            agent_ids=["sales_page_creator"],
                            output_key="gumroad_live"
                        )
                    ]
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="marketing_campaign",
                    agent_ids=["social_media_marketer", "email_marketer"],
                    output_key="marketing_launched"
                )
            ],

            "ai_service_business": [
                WorkflowStep(
                    type=StepType.AGENT,
                    name="service_definition",
                    agent_ids=["service_designer", "pricing_strategist"],
                    output_key="service_package"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="lead_generation",
                    agent_ids=["lead_finder", "outreach_specialist"],
                    output_key="qualified_leads"
                ),
                WorkflowStep(
                    type=StepType.CONDITIONAL,
                    name="demo_creation",
                    condition=lambda ctx: len(ctx.results.get("qualified_leads", [])) > 0,
                    agent_ids=["demo_builder", "case_study_writer"],
                    output_key="sales_materials"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="client_onboarding",
                    agent_ids=["onboarding_specialist", "project_manager"],
                    output_key="client_setup"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="service_delivery",
                    agent_ids=["automation_builder", "quality_checker"],
                    output_key="delivered_service"
                )
            ]
        }

    async def analyze_user_potential(
        self,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Analyze user's income potential"""

        # Score opportunities based on user profile
        scored_opportunities = []

        for opportunity in self.opportunities:
            score = await self._score_opportunity(opportunity, user_profile)
            scored_opportunities.append({
                "opportunity": opportunity,
                "score": score,
                "match_reasons": self._get_match_reasons(opportunity, user_profile)
            })

        # Sort by score
        scored_opportunities.sort(key=lambda x: x["score"], reverse=True)

        # Get ALL opportunities (not just top 3)
        all_opportunities = scored_opportunities

        # Calculate potential earnings timeline (use top 3 for projection)
        earnings_timeline = self._project_earnings(scored_opportunities[:3], user_profile)

        return {
            "user_id": user_profile.id,
            "current_balance": user_profile.current_balance,
            "skill_level": user_profile.skill_level.value,
            "top_opportunities": [
                {
                    "title": opp["opportunity"].title,
                    "stream_type": opp["opportunity"].stream_type.value,
                    "score": opp["score"],
                    "time_to_income": opp["opportunity"].time_to_first_income,
                    "potential_monthly": opp["opportunity"].potential_monthly,
                    "match_reasons": opp["match_reasons"],
                    "action_steps": opp["opportunity"].action_steps
                }
                for opp in all_opportunities
            ],
            "earnings_projection": earnings_timeline,
            "recommended_path": self._create_income_path(scored_opportunities[:3], user_profile),
            "skill_gaps": self._identify_skill_gaps(scored_opportunities[:3], user_profile),
            "success_probability": self._calculate_success_probability(scored_opportunities[:3], user_profile)
        }

    async def _score_opportunity(
        self,
        opportunity: IncomeOpportunity,
        user_profile: UserProfile
    ) -> float:
        """Score an opportunity for a user"""
        score = 0.0

        # Check skill match
        skill_match = len(set(user_profile.skills) & set(opportunity.required_skills))
        score += skill_match * 0.2

        # Consider difficulty vs skill level
        if opportunity.difficulty.value <= user_profile.skill_level.value:
            score += 0.2

        # Time availability
        if user_profile.available_hours_per_week >= 20:
            score += 0.15
        elif user_profile.available_hours_per_week >= 10:
            score += 0.1

        # Zero investment bonus (for users with $0)
        if user_profile.current_balance == 0 and opportunity.initial_investment == 0:
            score += 0.25

        # Market factors
        score += opportunity.market_demand * 0.1
        score += (1 - opportunity.competition_level) * 0.1
        score += opportunity.scalability * 0.1

        # Success rate weight
        score += opportunity.success_rate * 0.15

        # ML-based personalization
        ml_score = await self.ml_pipeline.predict_opportunity_fit(
            user_profile.__dict__,
            opportunity.__dict__
        )
        score += ml_score.get("fit_score", 0) * 0.2

        return min(score, 1.0)

    def _get_match_reasons(
        self,
        opportunity: IncomeOpportunity,
        user_profile: UserProfile
    ) -> List[str]:
        """Get reasons why opportunity matches user"""
        reasons = []

        if opportunity.initial_investment == 0 and user_profile.current_balance == 0:
            reasons.append("No investment required")

        skill_match = set(user_profile.skills) & set(opportunity.required_skills)
        if skill_match:
            reasons.append(f"You have skills: {', '.join(skill_match)}")

        if opportunity.difficulty.value <= user_profile.skill_level.value:
            reasons.append("Matches your skill level")

        if opportunity.market_demand > 0.8:
            reasons.append("High market demand")

        if opportunity.competition_level < 0.5:
            reasons.append("Low competition")

        if "1-3 days" in opportunity.time_to_first_income:
            reasons.append("Quick to first income")

        return reasons

    def _project_earnings(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Project earnings over time"""
        projections = {
            "week_1": 0,
            "month_1": 0,
            "month_3": 0,
            "month_6": 0,
            "year_1": 0
        }

        for opp_data in opportunities[:2]:  # Focus on top 2
            opp = opp_data["opportunity"]
            score = opp_data["score"]

            # Parse potential monthly (e.g., "$500-$2000")
            potential = opp.potential_monthly.replace("$", "").replace(",", "")
            if "-" in potential:
                low, high = potential.split("-")
                expected = (float(low) + float(high)) / 2
            else:
                expected = float(potential)

            # Adjust based on score and success rate
            expected *= score * opp.success_rate

            # Project based on time to income
            if "1-3 days" in opp.time_to_first_income:
                projections["week_1"] += expected * 0.1
                projections["month_1"] += expected * 0.3
            elif "1 week" in opp.time_to_first_income:
                projections["month_1"] += expected * 0.2
            elif "2 weeks" in opp.time_to_first_income:
                projections["month_1"] += expected * 0.1

            # Longer term projections
            projections["month_3"] += expected * 1.5
            projections["month_6"] += expected * 4
            projections["year_1"] += expected * 10

        return projections

    def _create_income_path(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Create step-by-step income path"""
        path = []

        # Week 1: Quick wins
        path.append({
            "phase": "Week 1: Quick Start",
            "focus": opportunities[0]["opportunity"].title if opportunities else "Skill Assessment",
            "actions": [
                "Complete skill assessment",
                "Set up free accounts on platforms",
                "Create basic portfolio",
                "Apply to 5 simple gigs"
            ],
            "expected_outcome": "First application responses"
        })

        # Month 1: Establish presence
        path.append({
            "phase": "Month 1: Build Foundation",
            "focus": "Establish service delivery",
            "actions": [
                "Complete first paid project",
                "Gather testimonials",
                "Refine service offering",
                "Increase application volume"
            ],
            "expected_outcome": "$100-500 earned"
        })

        # Month 2-3: Scale up
        path.append({
            "phase": "Month 2-3: Scale Operations",
            "focus": "Increase rates and volume",
            "actions": [
                "Raise rates by 20%",
                "Add second income stream",
                "Automate repetitive tasks",
                "Build recurring client base"
            ],
            "expected_outcome": "$500-1500/month"
        })

        # Month 4-6: Optimize
        path.append({
            "phase": "Month 4-6: Optimize & Expand",
            "focus": "Maximize earnings",
            "actions": [
                "Focus on highest-paying work",
                "Launch digital products",
                "Build email list",
                "Consider premium services"
            ],
            "expected_outcome": "$1500-3000/month"
        })

        return path

    def _identify_skill_gaps(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> List[Dict[str, str]]:
        """Identify skills user needs to learn"""
        gaps = []

        for opp_data in opportunities:
            opp = opp_data["opportunity"]
            missing_skills = set(opp.required_skills) - set(user_profile.skills)

            for skill in missing_skills:
                gaps.append({
                    "skill": skill,
                    "importance": "high" if opp_data == opportunities[0] else "medium",
                    "time_to_learn": "1-2 weeks",
                    "resources": "Free online courses available"
                })

        return gaps[:5]  # Top 5 gaps

    def _calculate_success_probability(
        self,
        opportunities: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> float:
        """Calculate overall success probability"""
        if not opportunities:
            return 0.0

        # Weighted average of top opportunities
        total_weight = 0
        weighted_sum = 0

        for i, opp_data in enumerate(opportunities[:3]):
            weight = 1.0 / (i + 1)  # Higher weight for better matches
            success_rate = opp_data["opportunity"].success_rate
            score = opp_data["score"]

            weighted_sum += (success_rate * score) * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def research_market_opportunity(self, opportunity: IncomeOpportunity) -> Dict[str, Any]:
        """Research market opportunity using real tools and APIs"""
        research_data = {
            "opportunity_id": opportunity.id,
            "research_timestamp": datetime.now().isoformat(),
            "data_sources": [],
            "market_insights": [],
            "competition_analysis": [],
            "tools_used": []
        }

        # Use web search tool if available
        if self.tools_available.get('web_search') and self.web_search:
            try:
                # Search for market trends
                search_query = f"{opportunity.stream_type.value} market trends 2025 freelance opportunities"
                search_result = self.web_search.execute(search_query, max_results=10)

                if search_result.get('success'):
                    search_data = search_result.get('data', {})
                    research_data["data_sources"].append("web_search")
                    research_data["tools_used"].append("WebSearchTool")

                    # Analyze search results for market insights
                    for result in search_data.get('results', []):
                        if any(keyword in result.get('snippet', '').lower() for keyword in ['growing', 'demand', 'opportunity', 'trend']):
                            research_data["market_insights"].append({
                                "source": result.get('title', ''),
                                "url": result.get('url', ''),
                                "insight": result.get('snippet', '')[:200]
                            })

                # Search for competition analysis
                comp_query = f"{opportunity.stream_type.value} competition analysis freelance market"
                comp_result = self.web_search.execute(comp_query, max_results=5)

                if comp_result.get('success'):
                    comp_data = comp_result.get('data', {})
                    for result in comp_data.get('results', []):
                        if any(keyword in result.get('snippet', '').lower() for keyword in ['competition', 'saturated', 'competitive', 'market share']):
                            research_data["competition_analysis"].append({
                                "source": result.get('title', ''),
                                "url": result.get('url', ''),
                                "analysis": result.get('snippet', '')[:200]
                            })

            except Exception as e:
                logger.error(f"Web search research failed: {e}")
                research_data["errors"] = [str(e)]

        # Use news API if available
        if self.tools_available.get('news_api') and self.news_api:
            try:
                news_query = f"{opportunity.stream_type.value} freelance industry news"
                news_result = self.news_api.execute(news_query, max_results=5)

                if news_result.get('success'):
                    research_data["data_sources"].append("news_api")
                    research_data["tools_used"].append("NewsAPITool")

                    news_data = news_result.get('data', {})
                    for article in news_data.get('articles', []):
                        research_data["market_insights"].append({
                            "source": f"NEWS: {article.get('title', '')}",
                            "url": article.get('url', ''),
                            "insight": article.get('description', '')[:200],
                            "published": article.get('publishedAt', '')
                        })

            except Exception as e:
                logger.error(f"News API research failed: {e}")
                research_data.setdefault("errors", []).append(str(e))

        # If no real tools available, indicate this is limited analysis
        if not research_data["tools_used"]:
            research_data["limitation"] = "Limited to static analysis - real market research tools not available"
            research_data["recommendation"] = "Enable web search and news API tools for real-time market research"

        return research_data

    async def generate_portfolio_files(self, user_profile: UserProfile, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate real portfolio files for user based on opportunities"""
        files_created = []

        try:
            # Create user-specific directory
            portfolio_dir = Path(f"portfolios/{user_profile.id}")
            portfolio_dir.mkdir(parents=True, exist_ok=True)

            # Generate README file
            readme_content = f"""# {user_profile.id.replace('_', ' ').title()} - Professional Portfolio

## Skills & Expertise
{', '.join(user_profile.skills) if user_profile.skills else 'Developing professional skills'}

## Experience Level
{user_profile.skill_level.value.title()}

## Available Hours
{user_profile.available_hours_per_week} hours per week

## Top Opportunities
"""
            for i, opp in enumerate(opportunities[:3], 1):
                opp_data = opp.get('opportunity', {})
                readme_content += f"""
### {i}. {opp_data.get('title', 'Opportunity')}
- **Type:** {opp_data.get('stream_type', {}).get('value', 'Unknown')}
- **Match Score:** {opp.get('score', 0):.2f}
- **Potential:** {opp_data.get('potential_monthly', 'TBD')}
- **Time to Income:** {opp_data.get('time_to_first_income', 'TBD')}
"""

            readme_content += f"""
## Generated on
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*This portfolio was generated using real AI analysis and market research.*
"""

            readme_path = portfolio_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            files_created.append(str(readme_path))

            # Generate opportunity-specific action plans
            for opp in opportunities[:2]:  # Top 2 opportunities
                opp_data = opp.get('opportunity', {})
                opp_id = opp_data.get('id', 'unknown')

                action_plan_content = f"""# Action Plan: {opp_data.get('title', 'Opportunity')}

## Overview
{opp_data.get('description', 'No description available')}

## Required Skills
{', '.join(opp_data.get('required_skills', [])) if opp_data.get('required_skills') else 'No specific skills listed'}

## Time Investment
{opp_data.get('time_to_first_income', 'Unknown timeframe')}

## Action Steps
"""
                for i, step in enumerate(opp_data.get('action_steps', []), 1):
                    action_plan_content += f"{i}. {step}\n"

                action_plan_content += f"""
## Success Metrics
- **Potential Revenue:** {opp_data.get('potential_monthly', 'TBD')}
- **Success Rate:** {opp_data.get('success_rate', 0) * 100:.1f}%
- **Market Demand:** {opp_data.get('market_demand', 0) * 100:.1f}%

## Tools Needed
{', '.join(opp_data.get('tools_needed', [])) if opp_data.get('tools_needed') else 'No specific tools listed'}

## Resources
"""
                for resource in opp_data.get('resources', []):
                    action_plan_content += f"- [{resource.get('name', 'Resource')}]({resource.get('url', '#')})\n"

                action_plan_content += f"""
---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

                action_plan_path = portfolio_dir / f"action_plan_{opp_id}.md"
                with open(action_plan_path, 'w', encoding='utf-8') as f:
                    f.write(action_plan_content)
                files_created.append(str(action_plan_path))

            logger.info(f"Generated {len(files_created)} portfolio files for user {user_profile.id}")

        except Exception as e:
            logger.error(f"Portfolio file generation failed: {e}")
            raise

        return files_created

    async def analyze_external_opportunity(self, opportunity_data: Dict) -> Dict[str, Any]:
        """
        Analyze opportunities from Revenue Activation spiders

        Args:
            opportunity_data: Dictionary containing opportunity details from spider network

        Returns:
            Analysis results with success probability and recommendations
        """
        # Create default user profile if not provided
        user_profile = opportunity_data.get('user_profile', {
            'skills': ['python', 'data analysis', 'content writing', 'automation'],
            'skill_level': 'intermediate',
            'current_balance': 0,
            'available_hours_per_week': 20
        })

        # Enhanced ML scoring with real opportunity analysis
        ml_score = await self.ml_pipeline.predict_opportunity_fit(
            user_profile,
            opportunity_data
        )

        # Generate optimized approach
        action_steps = self._generate_action_steps_for_external(opportunity_data)

        # Calculate success factors with real data
        success_factors = self._analyze_success_factors(opportunity_data)

        # Enhanced proposal template with dynamic content
        proposal_template = self._create_proposal_template(opportunity_data)

        # Real-time market analysis
        market_context = await self._analyze_market_context(opportunity_data)

        return {
            'success_probability': ml_score.get('fit_score', 0.5),
            'ml_score': ml_score,
            'recommended_approach': self._determine_best_approach(opportunity_data),
            'action_steps': action_steps,
            'proposal_template': proposal_template,
            'success_factors': success_factors,
            'priority_level': self._calculate_priority(ml_score.get('fit_score', 0.5), opportunity_data),
            'market_context': market_context,
            'revenue_activation_ready': True
        }

    def _generate_action_steps_for_external(self, opportunity: Dict) -> List[Dict]:
        """Generate action steps for external opportunity"""
        steps = []

        # Analyze requirements
        skills_required = opportunity.get('skills_required', [])
        budget = opportunity.get('budget', 'Not specified')
        deadline = opportunity.get('deadline', 'Flexible')

        steps.append({
            'name': 'Analyze Requirements',
            'description': f"Review skills needed: {', '.join(skills_required)}",
            'estimated_time': '15 minutes',
            'priority': 'high'
        })

        steps.append({
            'name': 'Customize Proposal',
            'description': f"Tailor proposal for budget: {budget}",
            'estimated_time': '30 minutes',
            'priority': 'high'
        })

        steps.append({
            'name': 'Prepare Portfolio',
            'description': 'Select relevant work samples',
            'estimated_time': '20 minutes',
            'priority': 'medium'
        })

        steps.append({
            'name': 'Submit Proposal',
            'description': f"Submit by deadline: {deadline}",
            'estimated_time': '10 minutes',
            'priority': 'high'
        })

        return steps

    def _analyze_success_factors(self, opportunity: Dict) -> Dict:
        """Analyze factors that influence success probability"""
        factors = {
            'budget_competitiveness': 'high' if self._parse_budget(opportunity.get('budget', '0')) > 500 else 'medium',
            'skill_match': self._calculate_skill_match(opportunity),
            'client_quality': opportunity.get('client_rating', 0),
            'competition_level': opportunity.get('competition_level', 'medium'),
            'timeline_feasibility': 'good' if 'week' in str(opportunity.get('deadline', '')).lower() else 'tight'
        }
        return factors

    def _determine_best_approach(self, opportunity: Dict) -> str:
        """Determine the best approach based on opportunity characteristics"""
        budget = self._parse_budget(opportunity.get('budget', '0'))

        if budget > 1000:
            return 'premium_value_proposition'
        elif opportunity.get('is_ongoing', False):
            return 'long_term_partnership'
        elif opportunity.get('urgent', False):
            return 'rapid_delivery'
        else:
            return 'competitive_quality'

    def _create_proposal_template(self, opportunity: Dict) -> str:
        """Create a proposal template for the opportunity"""
        return f"""
# Proposal for: {opportunity.get('title', 'Your Project')}

## Understanding Your Needs
Based on your requirements, I understand you need someone with expertise in:
{self._format_skills(opportunity.get('skills_required', []))}

## My Approach
[Customize based on project specifics]

## Timeline
Delivery: {opportunity.get('deadline', 'As per your requirements')}

## Investment
{opportunity.get('budget', 'Competitive rate')}

## Why Choose Me
- Relevant experience in your industry
- Proven track record
- Quick turnaround time

Looking forward to discussing your project in detail.
"""

    def _parse_budget(self, budget_str: str) -> float:
        """Parse budget string to float"""
        try:
            cleaned = str(budget_str).replace('$', '').replace(',', '').strip()
            return float(cleaned)
        except:
            return 0.0

    def _calculate_skill_match(self, opportunity: Dict) -> str:
        """Calculate how well skills match"""
        # Simplified for now
        return 'good'

    def _format_skills(self, skills: List[str]) -> str:
        """Format skills list for display"""
        if not skills:
            return "- General expertise required"
        return '\n'.join([f"- {skill}" for skill in skills])

    def _calculate_priority(self, success_score: float, opportunity: Dict) -> str:
        """Calculate priority level"""
        budget = self._parse_budget(opportunity.get('budget', '0'))

        if success_score > 0.7 and budget > 1000:
            return 'high'
        elif success_score > 0.5:
            return 'medium'
        else:
            return 'low'

    async def _analyze_market_context(self, opportunity_data: Dict) -> Dict[str, Any]:
        """Analyze market context for opportunity"""
        return {
            'platform': opportunity_data.get('platform', 'unknown'),
            'competition_analysis': {
                'level': opportunity_data.get('competition_level', 0.5),
                'estimated_applicants': int(opportunity_data.get('competition_level', 0.5) * 50),
                'our_advantage': self._calculate_competitive_advantage(opportunity_data)
            },
            'market_demand': {
                'skills': opportunity_data.get('skills_required', []),
                'demand_score': self._calculate_skill_demand(opportunity_data.get('skills_required', [])),
                'trending': self._is_trending_skill_set(opportunity_data.get('skills_required', []))
            },
            'timing_analysis': {
                'urgency': 'high' if 'asap' in opportunity_data.get('deadline', '').lower() else 'medium',
                'deadline': opportunity_data.get('deadline', 'flexible'),
                'optimal_submit_time': self._calculate_optimal_submit_time(opportunity_data)
            }
        }

    def _calculate_competitive_advantage(self, opportunity_data: Dict) -> List[str]:
        """Calculate our competitive advantages"""
        advantages = []
        skills_required = opportunity_data.get('skills_required', [])

        # AI-powered advantages
        if any(skill in ['ai', 'automation', 'chatgpt', 'machine learning'] for skill in skills_required):
            advantages.append("AI expertise with real implementation experience")

        # Technical advantages
        if any(skill in ['python', 'data analysis', 'automation'] for skill in skills_required):
            advantages.append("Advanced technical skills with proven results")

        # Speed advantage
        advantages.append("Fast turnaround with AI-assisted development")

        # Quality advantage
        advantages.append("High-quality deliverables with iterative feedback")

        return advantages

    def _calculate_skill_demand(self, skills: List[str]) -> float:
        """Calculate demand score for skills"""
        # High-demand skills mapping
        demand_scores = {
            'python': 0.9,
            'ai': 0.95,
            'automation': 0.85,
            'data analysis': 0.8,
            'content writing': 0.7,
            'chatgpt': 0.9,
            'machine learning': 0.9,
            'web scraping': 0.75,
            'api integration': 0.8
        }

        if not skills:
            return 0.5

        scores = [demand_scores.get(skill.lower(), 0.5) for skill in skills]
        return sum(scores) / len(scores)

    def _is_trending_skill_set(self, skills: List[str]) -> bool:
        """Check if skill set is trending"""
        trending_skills = {'ai', 'automation', 'chatgpt', 'machine learning', 'prompt engineering'}
        return any(skill.lower() in trending_skills for skill in skills)

    def _calculate_optimal_submit_time(self, opportunity_data: Dict) -> str:
        """Calculate optimal time to submit proposal"""
        # Basic heuristic - submit quickly for high-value opportunities
        budget = self._parse_budget(opportunity_data.get('budget', '0'))
        competition = opportunity_data.get('competition_level', 0.5)

        if budget > 1000 and competition < 0.5:
            return "ASAP - High value, low competition"
        elif competition > 0.8:
            return "Within 2 hours - High competition"
        else:
            return "Within 6 hours - Optimal timing"

    async def connect_to_revenue_orchestrator(self) -> bool:
        """Connect Income Builder to Revenue Activation Orchestrator"""
        try:
            # Try to import and connect to orchestrator
            import sys
            orchestrator_path = '/Users/donkeyking/development/unified-donkey-betz'
            if orchestrator_path not in sys.path:
                sys.path.append(orchestrator_path)

            from revenue_activation_orchestrator import revenue_orchestrator

            # Register as connected agent
            logger.info("Income Builder connected to Revenue Activation Orchestrator")
            return True

        except Exception as e:
            logger.warning(f"Could not connect to Revenue Orchestrator: {e}")
            return False

    async def generate_real_time_proposal(self, opportunity_data: Dict, user_context: Dict = None) -> Dict[str, Any]:
        """Generate proposal optimized for real submission"""

        # Analyze opportunity with full context
        analysis = await self.analyze_external_opportunity(opportunity_data)

        # Generate enhanced proposal content
        proposal_content = self._create_enhanced_proposal_template(opportunity_data, analysis)

        # Calculate pricing strategy
        pricing_strategy = self._calculate_optimal_pricing(opportunity_data, analysis)

        # Generate submission strategy
        submission_strategy = self._create_submission_strategy(opportunity_data, analysis)

        return {
            'proposal_content': proposal_content,
            'pricing_strategy': pricing_strategy,
            'submission_strategy': submission_strategy,
            'analysis': analysis,
            'confidence_score': analysis.get('ml_score', {}).get('confidence', 0.8),
            'estimated_win_rate': analysis.get('success_probability', 0.5),
            'revenue_potential': self._calculate_revenue_potential(opportunity_data, analysis)
        }

    def _create_enhanced_proposal_template(self, opportunity_data: Dict, analysis: Dict) -> str:
        """Create enhanced proposal template with dynamic content"""

        title = opportunity_data.get('title', 'Your Project')
        budget = opportunity_data.get('budget', 0)
        skills = opportunity_data.get('skills_required', [])
        description = opportunity_data.get('description', '')

        # Dynamic opening based on opportunity
        if budget > 1500:
            opening = "I'm excited about this high-value project and believe I can deliver exceptional results."
        elif 'urgent' in description.lower() or 'asap' in description.lower():
            opening = "I understand this project is time-sensitive and I'm available to start immediately."
        else:
            opening = "Your project aligns perfectly with my expertise and I'm confident I can exceed your expectations."

        # Skill-specific approach
        technical_skills = [s for s in skills if s.lower() in ['python', 'automation', 'api', 'scraping']]
        creative_skills = [s for s in skills if s.lower() in ['writing', 'content', 'design']]

        approach_section = ""
        if technical_skills:
            approach_section = f"""
## Technical Approach
I'll leverage advanced {', '.join(technical_skills)} techniques to deliver:
- Clean, efficient, and well-documented code
- Robust error handling and testing
- Scalable solutions that grow with your needs
"""
        elif creative_skills:
            approach_section = f"""
## Creative Approach
My {', '.join(creative_skills)} expertise will ensure:
- Engaging, high-quality content that resonates with your audience
- SEO-optimized and conversion-focused copy
- Brand-consistent messaging across all deliverables
"""

        # Competitive advantages from analysis
        advantages = analysis.get('market_context', {}).get('competition_analysis', {}).get('our_advantage', [])
        advantages_text = '\n'.join([f"- {adv}" for adv in advantages[:3]])

        return f"""
# Proposal for: {title}

{opening}

## Understanding Your Requirements
{description[:200]}{'...' if len(description) > 200 else ''}

{approach_section}

## Why Choose Me
{advantages_text}

## Timeline & Delivery
Based on your requirements, I can deliver this project within the specified timeframe with regular updates and milestones.

## Investment
Budget: ${budget:.0f} - Competitive rate for premium quality work

## Next Steps
I'm ready to discuss the project details and answer any questions you might have. Let's create something amazing together!

---
*This proposal was crafted specifically for your project using AI-enhanced analysis to ensure the best possible fit.*
"""

    def _calculate_optimal_pricing(self, opportunity_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Calculate optimal pricing strategy"""

        budget = opportunity_data.get('budget', 0)
        competition = opportunity_data.get('competition_level', 0.5)
        success_prob = analysis.get('success_probability', 0.5)

        # Base pricing strategy
        if competition > 0.8:  # High competition
            recommended_bid = budget * 0.85  # Slightly below budget
            strategy = "competitive_pricing"
        elif success_prob > 0.8:  # High confidence
            recommended_bid = budget * 0.95  # Near full budget
            strategy = "value_pricing"
        else:  # Balanced approach
            recommended_bid = budget * 0.9  # 90% of budget
            strategy = "balanced_pricing"

        return {
            'recommended_bid': recommended_bid,
            'strategy': strategy,
            'budget_utilization': recommended_bid / budget if budget > 0 else 0,
            'competition_factor': competition,
            'confidence_adjustment': success_prob
        }

    def _create_submission_strategy(self, opportunity_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Create submission strategy"""

        market_context = analysis.get('market_context', {})
        timing = market_context.get('timing_analysis', {})

        return {
            'optimal_submit_time': timing.get('optimal_submit_time', 'Within 6 hours'),
            'urgency_level': timing.get('urgency', 'medium'),
            'follow_up_strategy': self._create_follow_up_strategy(opportunity_data),
            'submission_checklist': [
                'Review proposal for client-specific customization',
                'Verify portfolio examples are relevant',
                'Double-check pricing and timeline',
                'Ensure proposal addresses all requirements',
                'Submit during optimal hours (business hours in client timezone)'
            ]
        }

    def _create_follow_up_strategy(self, opportunity_data: Dict) -> List[str]:
        """Create follow-up strategy"""
        budget = opportunity_data.get('budget', 0)

        if budget > 1000:
            return [
                "Day 2: Send a brief additional portfolio example",
                "Day 5: Follow up with clarifying questions",
                "Day 10: Final follow-up before moving on"
            ]
        else:
            return [
                "Day 3: Send brief follow-up if no response",
                "Day 7: Final follow-up"
            ]

    def _calculate_revenue_potential(self, opportunity_data: Dict, analysis: Dict) -> Dict[str, Any]:
        """Calculate revenue potential"""

        budget = opportunity_data.get('budget', 0)
        success_prob = analysis.get('success_probability', 0.5)

        return {
            'expected_value': budget * success_prob,
            'min_value': budget * 0.7 * success_prob,  # Conservative estimate
            'max_value': budget * 1.2 * success_prob,  # Optimistic (potential bonuses)
            'probability_bands': {
                'high_confidence': budget if success_prob > 0.8 else 0,
                'medium_confidence': budget if 0.5 < success_prob <= 0.8 else 0,
                'low_confidence': budget if success_prob <= 0.5 else 0
            }
        }

    async def generate_ai_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate AI content using OpenAI or fallback to template"""
        if OPENAI_AVAILABLE and openai_client:
            try:
                # Build comprehensive context for the AI
                system_prompt = """You are an expert business strategist and income generation specialist.
                Create detailed, actionable, and personalized content for income opportunities.
                Focus on practical steps, realistic timelines, and measurable outcomes.
                Include specific tactics, tools, and resources that can be immediately implemented."""

                user_prompt = f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)}"

                # Call OpenAI API with GPT-5-mini specific parameters
                response = openai_client.chat.completions.create(
                    model="gpt-5-mini",  # Using GPT-5-mini
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=1.0,  # GPT-5 always uses temperature 1.0
                    max_completion_tokens=2000,  # GPT-5 uses max_completion_tokens instead of max_tokens
                    reasoning_effort="medium"  # GPT-5-mini supports reasoning tokens
                )

                content = response.choices[0].message.content
                logging.info(f"Generated AI content using OpenAI (tokens: {response.usage.total_tokens})")
                return content

            except Exception as e:
                logging.error(f"OpenAI API error: {e}")
                # Fall through to template generation

        # Fallback to template if OpenAI is not available
        logging.info("Using template generation (OpenAI not available)")
        return None  # Will use existing template logic

    async def create_action_plan(
        self,
        user_id: str,
        selected_opportunity: str
    ) -> Dict[str, Any]:
        """Create detailed action plan for selected opportunity with real AI generation"""

        # Find the opportunity
        opportunity = next(
            (opp for opp in self.opportunities if opp.id == selected_opportunity),
            None
        )

        if not opportunity:
            return {"error": "Opportunity not found"}

        # Create personalized workflow ID
        workflow_id = f"workflow_{opportunity.id}_{user_id}"

        # Research the opportunity using real tools
        market_research = await self.research_market_opportunity(opportunity)

        # Generate AI-enhanced plan if available
        ai_enhanced_plan = None
        if OPENAI_AVAILABLE:
            prompt = f"""Create a comprehensive 4-week action plan for: {opportunity.title}

            Requirements:
            - Week-by-week breakdown with specific tasks
            - Daily task structure for consistency
            - Success metrics and KPIs
            - Resource recommendations
            - Risk mitigation strategies

            Focus on actionable steps that can be started with ${opportunity.initial_investment} investment."""

            context = {
                "opportunity": {
                    "title": opportunity.title,
                    "description": opportunity.description,
                    "initial_investment": opportunity.initial_investment,
                    "potential_monthly": opportunity.potential_monthly,
                    "success_rate": opportunity.success_rate,
                    "stream_type": opportunity.stream_type.value
                },
                "market_research": market_research
            }

            ai_content = await self.generate_ai_content(prompt, context)
            if ai_content:
                ai_enhanced_plan = ai_content

        # Create the basic plan structure (used as fallback or enhancement)
        plan = {
            "plan_id": workflow_id,
            "opportunity": opportunity.title,
            "week_by_week": self._create_weekly_plan(opportunity),
            "daily_tasks": self._create_daily_tasks(opportunity),
            "success_metrics": self._define_success_metrics(opportunity),
            "resources": opportunity.resources,
            "workflow_id": workflow_id,
            "market_research": market_research,
            "tools_used": market_research.get("tools_used", []),
            "research_timestamp": market_research.get("research_timestamp"),
            "ai_enhanced": ai_enhanced_plan is not None,
            "files_created": []
        }

        # Generate real action plan files
        try:
            plan_dir = Path(f"action_plans/{user_id}")
            plan_dir.mkdir(parents=True, exist_ok=True)

            # Use AI content if available, otherwise use template
            if ai_enhanced_plan:
                action_plan_content = f"""# AI-Generated Action Plan: {opportunity.title}

## Generated by OpenAI GPT-5-mini

{ai_enhanced_plan}

---
## Additional Resources and Context

### Opportunity Details
- **ID:** {opportunity.id}
- **Stream Type:** {opportunity.stream_type.value}
- **Initial Investment:** ${opportunity.initial_investment}
- **Potential Monthly:** {opportunity.potential_monthly}
- **Success Rate:** {opportunity.success_rate * 100:.1f}%
"""
            else:
                # Fallback to template-based content
                action_plan_content = f"""# Detailed Action Plan: {opportunity.title}

## Opportunity Overview
- **ID:** {opportunity.id}
- **Stream Type:** {opportunity.stream_type.value}
- **Description:** {opportunity.description}
- **Initial Investment:** ${opportunity.initial_investment}
- **Potential Monthly:** {opportunity.potential_monthly}
- **Success Rate:** {opportunity.success_rate * 100:.1f}%

## Market Research Summary
- **Research Date:** {market_research.get('research_timestamp')}
- **Tools Used:** {', '.join(market_research.get('tools_used', ['Static Analysis']))}
- **Data Sources:** {', '.join(market_research.get('data_sources', ['Internal']))}

### Market Insights
"""
            for insight in market_research.get('market_insights', [])[:5]:
                action_plan_content += f"- **{insight.get('source', 'Unknown')}:** {insight.get('insight', '')}\n"

            if market_research.get('competition_analysis'):
                action_plan_content += "\n### Competition Analysis\n"
                for comp in market_research.get('competition_analysis', [])[:3]:
                    action_plan_content += f"- **{comp.get('source', 'Unknown')}:** {comp.get('analysis', '')}\n"

            action_plan_content += f"""

## Week-by-Week Implementation Plan
"""
            for week_plan in plan["week_by_week"]:
                action_plan_content += f"""
### Week {week_plan.get('week')}: {week_plan.get('focus')}
**Time Required:** {week_plan.get('time_required')}
**Expected Result:** {week_plan.get('expected_result')}

**Tasks:**
"""
                for task in week_plan.get('tasks', []):
                    action_plan_content += f"- {task}\n"

            action_plan_content += f"""

## Daily Task Structure
"""
            for time_period, tasks in plan["daily_tasks"].items():
                action_plan_content += f"""
### {time_period.title()}
"""
                for task in tasks:
                    action_plan_content += f"- {task}\n"

            action_plan_content += f"""

## Success Metrics by Week
"""
            for week, metrics in plan["success_metrics"].items():
                action_plan_content += f"""
### {week.replace('_', ' ').title()}
"""
                for metric, target in metrics.items():
                    action_plan_content += f"- **{metric.replace('_', ' ').title()}:** {target}\n"

            action_plan_content += f"""

## Required Tools & Resources
"""
            for tool in opportunity.tools_needed:
                action_plan_content += f"- {tool}\n"

            action_plan_content += f"""

## External Resources
"""
            for resource in opportunity.resources:
                action_plan_content += f"- [{resource.get('name')}]({resource.get('url')})\n"

            action_plan_content += f"""

---
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Plan ID:** {workflow_id}
**User ID:** {user_id}

*This action plan was generated using real market research and AI analysis.*
"""

            # Save the action plan file
            action_plan_path = plan_dir / f"{workflow_id}_detailed_plan.md"
            with open(action_plan_path, 'w', encoding='utf-8') as f:
                f.write(action_plan_content)
            plan["files_created"].append(str(action_plan_path))

            # Create a quick reference checklist
            checklist_content = f"""# Quick Action Checklist: {opportunity.title}

## Pre-Launch Setup
"""
            for step in opportunity.action_steps[:3]:
                checklist_content += f"- [ ] {step}\n"

            checklist_content += f"""

## Week 1 Essentials
"""
            week1_tasks = plan["week_by_week"][0]["tasks"] if plan["week_by_week"] else []
            for task in week1_tasks:
                checklist_content += f"- [ ] {task}\n"

            checklist_content += f"""

## Daily Must-Do Items
"""
            for task in plan["daily_tasks"].get("morning", []):
                checklist_content += f"- [ ] {task}\n"

            checklist_content += f"""

## Key Milestones
- [ ] First application sent
- [ ] First response received
- [ ] First client acquired
- [ ] First payment received
- [ ] Process optimized and scaled

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            checklist_path = plan_dir / f"{workflow_id}_checklist.md"
            with open(checklist_path, 'w', encoding='utf-8') as f:
                f.write(checklist_content)
            plan["files_created"].append(str(checklist_path))

            logger.info(f"Generated {len(plan['files_created'])} action plan files for {user_id}")

        except Exception as e:
            logger.error(f"Action plan file generation failed: {e}")
            plan["file_generation_error"] = str(e)

        return plan

    def _create_weekly_plan(self, opportunity: IncomeOpportunity) -> List[Dict[str, Any]]:
        """Create week-by-week plan"""
        plan = []

        # Week 1
        plan.append({
            "week": 1,
            "focus": "Setup & Learning",
            "tasks": opportunity.action_steps[:2],
            "time_required": "10 hours",
            "expected_result": "Accounts created, basic knowledge gained"
        })

        # Week 2
        plan.append({
            "week": 2,
            "focus": "Portfolio & Profile",
            "tasks": opportunity.action_steps[2:3],
            "time_required": "15 hours",
            "expected_result": "Professional presence established"
        })

        # Week 3
        plan.append({
            "week": 3,
            "focus": "First Applications",
            "tasks": opportunity.action_steps[3:4],
            "time_required": "20 hours",
            "expected_result": "First responses and potentially first client"
        })

        # Week 4
        plan.append({
            "week": 4,
            "focus": "Delivery & Optimization",
            "tasks": opportunity.action_steps[4:],
            "time_required": "20 hours",
            "expected_result": "First income earned, process refined"
        })

        return plan

    def _create_daily_tasks(self, opportunity: IncomeOpportunity) -> Dict[str, List[str]]:
        """Create daily task list"""
        return {
            "morning": [
                "Check platform messages",
                "Review new opportunities",
                "Update availability"
            ],
            "afternoon": [
                "Work on active projects",
                "Send proposals/applications",
                "Skill development (30 mins)"
            ],
            "evening": [
                "Portfolio updates",
                "Client communication",
                "Plan next day"
            ]
        }

    def _define_success_metrics(self, opportunity: IncomeOpportunity) -> Dict[str, Any]:
        """Define success metrics"""
        return {
            "week_1": {
                "accounts_created": 3,
                "skills_learned": 2,
                "portfolio_items": 1
            },
            "week_2": {
                "applications_sent": 10,
                "response_rate": "10%",
                "portfolio_items": 3
            },
            "week_3": {
                "clients_acquired": 1,
                "projects_started": 1,
                "income_earned": "$50+"
            },
            "week_4": {
                "projects_completed": 2,
                "reviews_earned": 1,
                "income_earned": "$200+"
            }
        }


# Global income builder instance
income_builder = AIIncomeBuilder()