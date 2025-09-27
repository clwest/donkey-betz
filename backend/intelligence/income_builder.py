"""
AI Income Builder System - Start from $0

Helps users build income streams using AI, regardless of starting capital.
Focuses on skills, services, and value creation rather than traditional investing.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

# Import real dependencies - INTEGRATION RESTORED
from agents.registry import agent_registry
from advisors.registry import advisor_registry
# from orchestration import orchestrator, WorkflowStep, StepType  # Keep commented until orchestrator is updated
# from ml_pipeline.pipeline import MLPipeline  # Will be replaced with ml.core.ml_engine import

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
    """
    Real ML Pipeline integration with the ML Engine
    Replaces the mock implementation with actual ML predictions
    """

    def __init__(self):
        try:
            # Import the real ML engine
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

            from ml.core.ml_engine import MLEngine
            self.ml_engine = MLEngine()
            self.logger = logging.getLogger(__name__)
            self.logger.info("MLPipeline initialized with real ML Engine")
        except ImportError as e:
            self.logger.warning(f"Could not import ML Engine: {e}. Using fallback predictions.")
            self.ml_engine = None

    async def predict_opportunity_fit(self, user_dict, opp_dict):
        """
        Real ML prediction for opportunity fit using the ML Engine
        Falls back to heuristic if ML engine unavailable
        """
        try:
            if self.ml_engine:
                # Use the real ML engine for predictions
                prediction = self.ml_engine.analyze_user_decision_pattern({
                    'user_profile': user_dict,
                    'opportunity': opp_dict,
                    'domain': opp_dict.get('stream_type', 'GENERAL'),
                    'confidence': 0.7
                })

                # Enhanced prediction with cross-domain analysis
                if hasattr(self.ml_engine, 'detect_cross_domain_opportunity'):
                    market_data = {
                        'user_data': user_dict,
                        'opportunity_data': opp_dict
                    }
                    cross_domain_opps = self.ml_engine.detect_cross_domain_opportunity(market_data)

                    return {
                        "fit_score": prediction,
                        "confidence": 0.85 if prediction > 0.7 else 0.65,
                        "ml_engine": "active",
                        "cross_domain_opportunities": len(cross_domain_opps) if cross_domain_opps else 0,
                        "prediction_factors": {
                            "user_skills_match": self._calculate_skill_match(user_dict, opp_dict),
                            "market_demand": opp_dict.get('market_demand', 0.5),
                            "competition_level": opp_dict.get('competition_level', 0.5),
                            "user_experience": user_dict.get('skill_level', 'beginner')
                        }
                    }
                else:
                    return {
                        "fit_score": prediction,
                        "confidence": 0.8,
                        "ml_engine": "active",
                        "prediction_factors": {
                            "user_skills_match": self._calculate_skill_match(user_dict, opp_dict)
                        }
                    }
            else:
                # Fallback to enhanced heuristic
                return self._heuristic_prediction(user_dict, opp_dict)

        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            return self._heuristic_prediction(user_dict, opp_dict)

    def _calculate_skill_match(self, user_dict, opp_dict):
        """Calculate skill match percentage"""
        user_skills = set(user_dict.get('skills', []))
        required_skills = set(opp_dict.get('required_skills', []))

        if not required_skills:
            return 0.5

        intersection = user_skills & required_skills
        return len(intersection) / len(required_skills)

    def _heuristic_prediction(self, user_dict, opp_dict):
        """Enhanced heuristic prediction as fallback"""
        score = 0.5  # Base score

        # Skill matching
        skill_match = self._calculate_skill_match(user_dict, opp_dict)
        score += skill_match * 0.3

        # Experience level matching
        user_level = user_dict.get('skill_level', 'beginner')
        opp_difficulty = opp_dict.get('difficulty', 'beginner')

        level_scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        user_level_score = level_scores.get(user_level, 1)
        opp_level_score = level_scores.get(opp_difficulty, 1)

        if user_level_score >= opp_level_score:
            score += 0.2

        # Market factors
        score += opp_dict.get('market_demand', 0.5) * 0.15
        score -= opp_dict.get('competition_level', 0.5) * 0.1

        # Investment requirement (bonus for $0 start)
        if opp_dict.get('initial_investment', 0) == 0:
            score += 0.1

        return {
            "fit_score": min(max(score, 0.1), 0.95),  # Clamp between 0.1 and 0.95
            "confidence": 0.7,
            "ml_engine": "fallback_heuristic",
            "prediction_factors": {
                "skill_match": skill_match,
                "experience_match": user_level_score >= opp_level_score,
                "market_demand": opp_dict.get('market_demand', 0.5),
                "competition_level": opp_dict.get('competition_level', 0.5),
                "zero_investment": opp_dict.get('initial_investment', 0) == 0
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

        # Initialize agent and advisor integrations
        self.logger = logging.getLogger(__name__)
        self._initialize_integrations()

    def _initialize_integrations(self):
        """Initialize all system integrations"""
        integration_status = {
            'agent_registry': False,
            'advisor_registry': False,
            'memory_system': False,
            'embeddings': False
        }

        try:
            # Test agent registry connection
            agents = agent_registry.list_agents()
            self.logger.info(f"Connected to agent registry with {len(agents)} agents")
            integration_status['agent_registry'] = True

            # Test advisor registry connection
            advisors = advisor_registry.list_advisors()
            self.logger.info(f"Connected to advisor registry with {len(advisors)} advisors")
            integration_status['advisor_registry'] = True

        except Exception as e:
            self.logger.warning(f"Registry integrations not fully available: {e}")

        # Initialize memory/embeddings system integration
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

            from self_awareness.embeddings import SemanticCodeSearchEngine
            self.embedding_manager = SemanticCodeSearchEngine()
            integration_status['embeddings'] = True
            self.logger.info("Connected to embeddings system")

            # Test memory search capability
            try:
                test_results = self.embedding_manager.search_code(
                    "income generation opportunities", limit=1
                )
                # Memory system is functional even if no results (just means no embeddings yet)
                integration_status['memory_system'] = True
                if test_results:
                    self.logger.info(f"Memory search system operational with {len(test_results)} results")
                else:
                    self.logger.info("Memory search system operational (database needs embeddings)")
            except Exception as search_error:
                self.logger.warning(f"Memory search test failed: {search_error}")
                # Still mark as partially functional if manager exists
                if hasattr(self.embedding_manager, 'search_code'):
                    integration_status['memory_system'] = True

        except Exception as e:
            self.logger.warning(f"Memory/embeddings integration not available: {e}")
            self.embedding_manager = None

        self.integrations_active = any(integration_status.values())
        self.integration_status = integration_status
        self.logger.info(f"Integration status: {integration_status}")

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
        """Analyze user's income potential with agent and advisor integration"""

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

        # Get top recommendations
        top_3 = scored_opportunities[:3]

        # Calculate potential earnings timeline
        earnings_timeline = self._project_earnings(top_3, user_profile)

        # Enhanced analysis with agent and advisor integration
        enhanced_analysis = await self._get_enhanced_analysis(user_profile, top_3)

        base_result = {
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
                for opp in top_3
            ],
            "earnings_projection": earnings_timeline,
            "recommended_path": self._create_income_path(top_3, user_profile),
            "skill_gaps": self._identify_skill_gaps(top_3, user_profile),
            "success_probability": self._calculate_success_probability(top_3, user_profile)
        }

        # Add enhanced analysis if integrations are active
        if enhanced_analysis:
            base_result.update(enhanced_analysis)

        return base_result

    async def find_opportunities(self, user_profile):
        """
        Find real opportunities using spider network integration
        This method connects to the spider orchestrator to get fresh job data
        """
        try:
            # Import spider orchestrator
            from backend.spiders.spider_orchestrator import activate_job_spiders

            self.logger.info("🔍 Finding real opportunities using spider network...")

            # Activate spiders to collect real job data
            spider_result = await activate_job_spiders()

            if spider_result.get('success'):
                real_opportunities = spider_result.get('opportunities', [])
                self.logger.info(f"Retrieved {len(real_opportunities)} real opportunities from spiders")

                # Convert spider opportunities to our opportunity format
                formatted_opportunities = []
                for spider_opp in real_opportunities:
                    formatted_opp = self._convert_spider_opportunity(spider_opp, user_profile)
                    if formatted_opp:
                        formatted_opportunities.append(formatted_opp)

                # Score and rank the real opportunities
                scored_opportunities = []
                for opp in formatted_opportunities:
                    score = await self._score_opportunity(opp, user_profile)
                    scored_opportunities.append({
                        "opportunity": opp,
                        "score": score,
                        "match_reasons": self._get_match_reasons(opp, user_profile),
                        "source": "spider_network",
                        "real_data": True
                    })

                # Sort by score and return top opportunities
                scored_opportunities.sort(key=lambda x: x["score"], reverse=True)

                self.logger.info(f"✅ Found {len(scored_opportunities)} viable opportunities")
                return scored_opportunities[:10]  # Return top 10

            else:
                self.logger.warning("Spider activation failed, falling back to default opportunities")
                return []

        except Exception as e:
            self.logger.error(f"Error finding opportunities with spider network: {e}")
            return []

    def _convert_spider_opportunity(self, spider_opp, user_profile):
        """Convert spider opportunity format to internal opportunity format"""
        try:
            # Create an IncomeOpportunity-like object from spider data
            from datetime import timedelta, datetime

            # Map spider data to our format
            stream_type_mapping = {
                'toptal': IncomeStream.FREELANCE_SERVICES,
                'guru': IncomeStream.FREELANCE_SERVICES,
                'flexjobs': IncomeStream.CONSULTING,  # Use consulting for remote jobs
                'remoteok': IncomeStream.CONSULTING,  # Use consulting for remote jobs
                'peopleperhour': IncomeStream.FREELANCE_SERVICES
            }

            # Calculate monthly potential based on budget type
            if spider_opp.get('budget_type') == 'hourly':
                monthly_potential = spider_opp.get('budget_max', 50) * 40 * 4  # 40 hrs/week
            elif spider_opp.get('budget_type') == 'annual':
                monthly_potential = spider_opp.get('budget_max', 60000) / 12
            else:  # fixed
                monthly_potential = spider_opp.get('budget_max', 1000)

            # Create opportunity object
            opportunity = IncomeOpportunity(
                id=spider_opp.get('id', f"spider_{spider_opp.get('platform')}_{int(datetime.now().timestamp())}"),
                title=spider_opp.get('title', 'Remote Opportunity'),
                description=spider_opp.get('description', 'Real opportunity from spider network'),
                stream_type=stream_type_mapping.get(spider_opp.get('platform'), IncomeStream.FREELANCE_SERVICES),
                initial_investment=0.0,  # All spider opportunities are $0 start
                time_to_first_income="1 week",  # String format as expected
                potential_monthly=f"${int(monthly_potential):,}",  # String format as expected
                required_skills=spider_opp.get('skills', []),
                difficulty=SkillLevel.BEGINNER if spider_opp.get('experience_level') == 'beginner' else SkillLevel.INTERMEDIATE,
                tools_needed=[f"{spider_opp.get('platform', 'Platform')} account", "Professional portfolio"],
                market_demand=0.8,  # Real opportunities have high demand
                competition_level=0.6,  # Moderate competition
                success_rate=0.75,  # Good success rate for real opportunities
                scalability=0.7,  # Good scalability for freelance work
                action_steps=[
                    f"Review opportunity details on {spider_opp.get('platform')}",
                    "Prepare relevant portfolio/samples",
                    "Submit application with tailored proposal",
                    "Follow up within 24-48 hours"
                ],
                resources=[
                    {"name": f"{spider_opp.get('platform', 'Platform')} Profile", "url": f"https://{spider_opp.get('platform', 'platform')}.com"},
                    {"name": "Proposal Templates", "url": "https://example.com/templates"}
                ]
            )

            # Add spider-specific metadata
            opportunity.spider_data = {
                'platform': spider_opp.get('platform'),
                'budget_range': f"${spider_opp.get('budget_min', 0)}-{spider_opp.get('budget_max', 0)}",
                'client_rating': spider_opp.get('client_rating', 0),
                'urgency': spider_opp.get('urgency', 'medium'),
                'posted_at': spider_opp.get('posted_at'),
                'revenue_potential': spider_opp.get('revenue_potential', monthly_potential),
                'original_id': spider_opp.get('id')
            }

            return opportunity

        except Exception as e:
            self.logger.error(f"Error converting spider opportunity: {e}")
            return None

    async def _get_enhanced_analysis(self, user_profile: UserProfile, top_opportunities: List[Dict]) -> Dict[str, Any]:
        """Get enhanced analysis using agent, advisor, and memory systems"""
        if not self.integrations_active:
            return {}

        enhanced_data = {}

        try:
            # Memory-enhanced context search
            memory_context = await self._get_memory_context(user_profile, top_opportunities)
            if memory_context:
                enhanced_data["memory_context"] = memory_context

            # Agent-based analysis
            if self.integration_status.get('agent_registry'):
                research_agent = agent_registry.find_best_agent(
                    task_description="income opportunity research and market analysis",
                    required_capabilities=["research", "market_analysis", "financial_analysis"],
                    preferred_specialization="financial"
                )

                if research_agent:
                    enhanced_data["assigned_research_agent"] = {
                        "name": research_agent.get("name"),
                        "specialization": research_agent.get("specialization"),
                        "capabilities": research_agent.get("capabilities", [])
                    }

            # Advisor recommendations
            if self.integration_status.get('advisor_registry'):
                financial_advisor = advisor_registry.find_best_advisor(
                    consultation_topic="income generation strategy for beginner investor",
                    domain=advisor_registry.AdvisorDomain.FINANCIAL_PLANNING,
                    required_specializations=["wealth_building", "income_generation"]
                )

                if financial_advisor:
                    enhanced_data["recommended_financial_advisor"] = {
                        "name": financial_advisor.name,
                        "title": financial_advisor.title,
                        "expertise_level": financial_advisor.expertise_level.value,
                        "specializations": financial_advisor.specializations,
                        "satisfaction_rating": financial_advisor.satisfaction_rating,
                        "consultation_duration": financial_advisor.typical_engagement_duration
                    }

                # Business strategy advisor for entrepreneurial opportunities
                business_advisor = advisor_registry.find_best_advisor(
                    consultation_topic="startup and business development strategy",
                    domain=advisor_registry.AdvisorDomain.BUSINESS_STRATEGY,
                    required_specializations=["startup_consulting", "growth_strategy"]
                )

                if business_advisor:
                    enhanced_data["recommended_business_advisor"] = {
                        "name": business_advisor.name,
                        "title": business_advisor.title,
                        "expertise_level": business_advisor.expertise_level.value,
                        "specializations": business_advisor.specializations,
                        "satisfaction_rating": business_advisor.satisfaction_rating
                    }

            # System integration status
            enhanced_data["integration_capabilities"] = {
                "agent_orchestration": self.integration_status.get('agent_registry', False),
                "advisor_consultation": self.integration_status.get('advisor_registry', False),
                "memory_context": self.integration_status.get('memory_system', False),
                "embeddings_search": self.integration_status.get('embeddings', False)
            }

            if self.integration_status.get('agent_registry'):
                # Agent orchestration possibilities
                available_agents = agent_registry.list_agents(
                    specialization="financial",
                    active_only=True
                )
                enhanced_data["available_support_agents"] = len(available_agents)

                # Registry statistics
                agent_stats = agent_registry.get_registry_stats()
                advisor_stats = advisor_registry.get_registry_stats() if self.integration_status.get('advisor_registry') else {}

                enhanced_data["platform_intelligence"] = {
                    "total_agents": agent_stats.active_agents,
                    "total_advisors": advisor_stats.get("total_advisors", 0),
                    "specializations_available": list(agent_stats.popular_specializations.keys()),
                    "advisor_domains_available": len(advisor_stats.get("domain_distribution", {}))
                }

            enhanced_data["integration_status"] = "active"

        except Exception as e:
            self.logger.error(f"Enhanced analysis failed: {e}")
            enhanced_data["integration_status"] = "limited"
            enhanced_data["integration_error"] = str(e)

        return enhanced_data

    async def _get_memory_context(self, user_profile: UserProfile, top_opportunities: List[Dict]) -> Dict[str, Any]:
        """Get memory context from embeddings system"""
        if not self.integration_status.get('embeddings') or not self.embedding_manager:
            return {}

        try:
            # Build context query
            skills = ", ".join(user_profile.skills) if user_profile.skills else "general skills"
            interests = ", ".join(user_profile.interests) if user_profile.interests else "general interests"
            opportunity_titles = [opp["opportunity"].title for opp in top_opportunities[:2]]

            context_query = (
                f"income generation for skills: {skills}, "
                f"interests: {interests}, "
                f"opportunities: {', '.join(opportunity_titles)}"
            )

            # Search for relevant context
            search_results = self.embedding_manager.search_code(
                query=context_query,
                limit=5
            )

            if not search_results:
                return {"status": "no_context_found"}

            # Process and structure the context
            relevant_context = []
            for result in search_results:
                if result.get('similarity_score', 0) > 0.7:  # High relevance threshold
                    relevant_context.append({
                        "source": result.get('file_path', 'unknown'),
                        "content_type": result.get('content_type', 'code'),
                        "relevance": result.get('similarity_score', 0),
                        "summary": result.get('content', '')[:200] + "..."
                    })

            return {
                "status": "context_found",
                "query_used": context_query,
                "relevant_contexts": relevant_context[:3],  # Top 3
                "total_matches": len(search_results),
                "high_relevance_matches": len(relevant_context)
            }

        except Exception as e:
            self.logger.error(f"Memory context retrieval failed: {e}")
            return {"status": "error", "error": str(e)}

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

    async def create_action_plan(
        self,
        user_id: str,
        selected_opportunity: str
    ) -> Dict[str, Any]:
        """Create detailed action plan for selected opportunity"""

        # Find the opportunity
        opportunity = next(
            (opp for opp in self.opportunities if opp.id == selected_opportunity),
            None
        )

        if not opportunity:
            return {"error": "Opportunity not found"}

        # Create personalized workflow (mock for now)
        workflow_id = f"workflow_{opportunity.id}_{user_id}"

        return {
            "plan_id": workflow_id,
            "opportunity": opportunity.title,
            "week_by_week": self._create_weekly_plan(opportunity),
            "daily_tasks": self._create_daily_tasks(opportunity),
            "success_metrics": self._define_success_metrics(opportunity),
            "resources": opportunity.resources,
            "workflow_id": workflow_id
        }

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