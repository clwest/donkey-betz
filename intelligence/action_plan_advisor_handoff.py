"""
Action Plan to Advisor Handoff System

This module handles the transition from completed Action Plans to Advisor review,
enabling advisors to review plans, select appropriate team members, and initiate execution.

Key Features:
- Automatic advisor matching based on plan domain
- Advisor review and enhancement of plans
- Team formation with specialized agents
- Execution tracking and feedback loop
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# Import existing components
from advisors.registry import advisor_registry, AdvisorDomain, AdvisorConsultation
from agents.registry import agent_registry
from intelligence.action_plan_formatter import ActionPlanFormatter

logger = logging.getLogger(__name__)


class PlanDomain(Enum):
    """Domains for action plans that map to advisor specialties"""
    CONTENT_CREATION = "content_creation"
    DIGITAL_PRODUCTS = "digital_products"
    FREELANCE_SERVICES = "freelance_services"
    SAAS_DEVELOPMENT = "saas_development"
    ECOMMERCE = "ecommerce"
    CONSULTING = "consulting"
    INVESTMENT = "investment"
    REAL_ESTATE = "real_estate"
    EDUCATION = "education"
    MARKETING = "marketing"


@dataclass
class AdvisorReview:
    """Advisor's review and recommendations for an action plan"""
    advisor_id: str
    advisor_name: str
    review_date: datetime

    # Review content
    strengths: List[str]
    improvement_areas: List[str]
    risk_factors: List[str]
    success_probability: float  # 0.0 to 1.0

    # Strategic recommendations
    strategic_adjustments: List[str]
    resource_requirements: Dict[str, Any]
    timeline_adjustment: Optional[str] = None
    budget_estimate: Optional[float] = None

    # Team recommendations
    recommended_agents: List[str] = field(default_factory=list)
    recommended_specialists: List[str] = field(default_factory=list)
    coordination_strategy: str = ""

    # Action items
    immediate_actions: List[str] = field(default_factory=list)
    milestone_checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)


@dataclass
class TeamFormation:
    """Team formation for executing an action plan"""
    team_id: str
    plan_id: str
    advisor_id: str

    # Team composition
    lead_agent: str
    core_agents: List[str]
    specialist_agents: List[str]
    support_agents: List[str]

    # Roles and responsibilities
    agent_roles: Dict[str, str]  # agent_id -> role description
    coordination_model: str  # "hierarchical", "collaborative", "autonomous"

    # Execution strategy
    execution_phases: List[Dict[str, Any]]
    communication_channels: List[str]
    reporting_structure: Dict[str, Any]

    # Performance tracking
    kpis: List[str]
    checkpoints: List[datetime]
    escalation_path: List[str]


class ActionPlanAdvisorHandoff:
    """
    Manages the handoff of completed Action Plans to Advisors for review
    and team formation.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.advisor_registry = advisor_registry
        self.agent_registry = agent_registry
        self.formatter = ActionPlanFormatter()

        # Domain to Advisor mapping
        self.domain_advisor_map = self._initialize_domain_mapping()

        # Active reviews and teams
        self.active_reviews: Dict[str, AdvisorReview] = {}
        self.active_teams: Dict[str, TeamFormation] = {}

    def _initialize_domain_mapping(self) -> Dict[PlanDomain, List[str]]:
        """Map plan domains to appropriate advisors"""
        return {
            PlanDomain.CONTENT_CREATION: [
                "gary_vaynerchuk_advisor", "mr_beast_advisor", "startup_guru"
            ],
            PlanDomain.DIGITAL_PRODUCTS: [
                "tech_architect", "ai_strategist", "startup_guru"
            ],
            PlanDomain.FREELANCE_SERVICES: [
                "business_strategist", "career_coach", "startup_guru"
            ],
            PlanDomain.SAAS_DEVELOPMENT: [
                "tech_architect", "ai_strategist", "sam_altman_advisor"
            ],
            PlanDomain.ECOMMERCE: [
                "gary_vaynerchuk_advisor", "grant_cardone_advisor", "business_strategist"
            ],
            PlanDomain.CONSULTING: [
                "business_strategist", "career_coach", "chris_voss_advisor"
            ],
            PlanDomain.INVESTMENT: [
                "warren_buffett_advisor", "financial_strategist", "crypto_expert"
            ],
            PlanDomain.REAL_ESTATE: [
                "real_estate_mogul", "financial_strategist", "grant_cardone_advisor"
            ],
            PlanDomain.EDUCATION: [
                "sal_khan_advisor", "career_coach", "mr_beast_advisor"
            ],
            PlanDomain.MARKETING: [
                "gary_vaynerchuk_advisor", "mr_beast_advisor", "grant_cardone_advisor"
            ]
        }

    async def handoff_to_advisor(self, action_plan: Dict[str, Any]) -> Tuple[str, AdvisorReview]:
        """
        Hand off a completed action plan to the most appropriate advisor

        Args:
            action_plan: The completed action plan data

        Returns:
            Tuple of (advisor_id, AdvisorReview)
        """
        # Determine plan domain
        plan_domain = self._identify_plan_domain(action_plan)

        # Select best advisor
        advisor_id = await self._select_best_advisor(plan_domain, action_plan)

        # Create advisor review
        review = await self._create_advisor_review(advisor_id, action_plan)

        # Store review
        plan_id = action_plan.get('id', 'unknown')
        self.active_reviews[plan_id] = review

        self.logger.info(f"Action Plan {plan_id} handed off to Advisor {advisor_id}")

        return advisor_id, review

    def _identify_plan_domain(self, action_plan: Dict[str, Any]) -> PlanDomain:
        """Identify the domain of an action plan based on its content"""
        opportunity_title = action_plan.get('opportunity_title', '').lower()

        # Domain keywords mapping
        domain_keywords = {
            PlanDomain.CONTENT_CREATION: ['content', 'writing', 'blog', 'article', 'copywriting'],
            PlanDomain.DIGITAL_PRODUCTS: ['digital', 'template', 'ebook', 'course', 'download'],
            PlanDomain.FREELANCE_SERVICES: ['freelance', 'service', 'consulting', 'contractor'],
            PlanDomain.SAAS_DEVELOPMENT: ['saas', 'software', 'app', 'platform', 'api'],
            PlanDomain.ECOMMERCE: ['ecommerce', 'shop', 'store', 'product', 'selling'],
            PlanDomain.CONSULTING: ['consulting', 'advisor', 'coach', 'mentor'],
            PlanDomain.INVESTMENT: ['investment', 'trading', 'stocks', 'crypto', 'portfolio'],
            PlanDomain.REAL_ESTATE: ['real estate', 'property', 'rental', 'reit'],
            PlanDomain.EDUCATION: ['education', 'teaching', 'tutorial', 'training'],
            PlanDomain.MARKETING: ['marketing', 'promotion', 'advertising', 'social media']
        }

        # Score each domain
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in opportunity_title)
            if score > 0:
                domain_scores[domain] = score

        # Return highest scoring domain or default to consulting
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return PlanDomain.CONSULTING

    async def _select_best_advisor(self, plan_domain: PlanDomain, action_plan: Dict[str, Any]) -> str:
        """
        Select the best advisor for a given plan domain

        Uses availability, expertise level, and success rate to choose
        """
        potential_advisors = self.domain_advisor_map.get(plan_domain, [])

        if not potential_advisors:
            # Default to business strategist if no specific mapping
            return "business_strategist"

        # Score each potential advisor
        advisor_scores = []
        for advisor_id in potential_advisors:
            advisor = self.advisor_registry.advisors.get(advisor_id)
            if not advisor:
                continue

            score = 0
            # Expertise level scoring
            if advisor.expertise_level.value == "legend":
                score += 40
            elif advisor.expertise_level.value == "master":
                score += 30
            elif advisor.expertise_level.value == "expert":
                score += 20
            else:
                score += 10

            # Success rate scoring
            score += advisor.success_rate * 30

            # Availability scoring (lower response time is better)
            if advisor.response_time_hours <= 1:
                score += 20
            elif advisor.response_time_hours <= 6:
                score += 15
            elif advisor.response_time_hours <= 24:
                score += 10
            else:
                score += 5

            # Satisfaction rating scoring
            score += advisor.satisfaction_rating * 10

            advisor_scores.append((advisor_id, score))

        # Return highest scoring advisor
        if advisor_scores:
            advisor_scores.sort(key=lambda x: x[1], reverse=True)
            return advisor_scores[0][0]

        return potential_advisors[0]

    async def _create_advisor_review(self, advisor_id: str, action_plan: Dict[str, Any]) -> AdvisorReview:
        """
        Create an advisor review for an action plan

        This simulates the advisor's analysis and recommendations
        """
        advisor = self.advisor_registry.advisors.get(advisor_id)
        if not advisor:
            raise ValueError(f"Advisor {advisor_id} not found")

        opportunity_title = action_plan.get('opportunity_title', 'Unknown')

        # Create review based on advisor's expertise
        review = AdvisorReview(
            advisor_id=advisor_id,
            advisor_name=advisor.name,
            review_date=datetime.now(),

            # Analyze strengths
            strengths=[
                f"Well-structured approach to {opportunity_title}",
                "Clear milestone definitions",
                "Realistic timeline with buffer periods",
                "Good use of platform tools and automation",
                "Strong market research foundation"
            ],

            # Identify improvement areas
            improvement_areas=[
                "Consider adding contingency plans for key risks",
                "Expand customer acquisition strategies",
                "Include more specific financial projections",
                "Add competitive differentiation strategy"
            ],

            # Risk assessment
            risk_factors=[
                "Market saturation in some segments",
                "Initial customer acquisition costs",
                "Time to profitability may vary",
                "Competition from established players"
            ],

            # Success probability based on advisor's expertise and plan complexity
            success_probability=self._calculate_success_probability(advisor, action_plan),

            # Strategic recommendations
            strategic_adjustments=[
                f"Focus on niche within {opportunity_title} for faster traction",
                "Implement A/B testing from day one",
                "Build email list before launch",
                "Create strategic partnerships early",
                "Develop unique value proposition"
            ],

            # Resource requirements
            resource_requirements={
                "time_commitment": "20-30 hours/week initially",
                "financial_investment": "$500-2000 for tools and marketing",
                "skills_needed": ["marketing", "sales", "product development"],
                "tools_required": ["AI Content Studio", "Revenue Engine", "Analytics Platform"]
            },

            # Timeline adjustment
            timeline_adjustment="Consider extending Phase 1 by one week for market validation",

            # Budget estimate based on plan complexity
            budget_estimate=self._calculate_budget(action_plan),

            # Team recommendations
            recommended_agents=self._select_agents_for_plan(action_plan),
            recommended_specialists=["market-analyst", "content-creator", "seo-optimizer"],
            coordination_strategy="Weekly sync meetings with milestone reviews",

            # Action items
            immediate_actions=[
                "Validate target market assumptions",
                "Set up tracking and analytics",
                "Create MVP or proof of concept",
                "Identify first 10 potential customers",
                "Establish pricing strategy"
            ],

            # Success metrics
            success_metrics=[
                "First paying customer within 2 weeks",
                "$1000 MRR within 30 days",
                "50% customer retention after 60 days",
                "20% month-over-month growth",
                "Net Promoter Score > 8"
            ]
        )

        return review

    def _calculate_success_probability(self, advisor: Advisor, action_plan: Dict[str, Any]) -> float:
        """Calculate success probability based on advisor expertise and plan complexity"""
        import random

        # Base probability from advisor expertise
        base_prob = 0.7 if advisor.expertise_level.value in ["master", "legend"] else 0.6

        # Adjust based on plan complexity
        opportunity = action_plan.get('opportunity_title', '').lower()
        if 'ai' in opportunity or 'freelance' in opportunity:
            base_prob += 0.1  # Higher success for trending areas
        elif 'crypto' in opportunity or 'trading' in opportunity:
            base_prob -= 0.15  # Lower success for high-risk areas

        # Add some variation based on advisor
        advisor_adjustment = {
            "Warren Buffett": 0.05,  # Conservative, higher success
            "Cathie Wood": -0.05,  # Higher risk, lower initial success
            "Ray Dalio": 0.1,  # Systematic approach
            "Peter Lynch": 0.08,  # Good at picking winners
            "George Soros": -0.1,  # High risk/reward
        }.get(advisor.name, 0)

        # Add small random variation
        random_factor = random.uniform(-0.05, 0.05)

        final_prob = base_prob + advisor_adjustment + random_factor
        return max(0.45, min(0.95, final_prob))  # Clamp between 45% and 95%

    def _calculate_budget(self, action_plan: Dict[str, Any]) -> float:
        """Calculate budget based on action plan scope"""
        import random

        opportunity = action_plan.get('opportunity_title', '').lower()

        # Base budget varies by opportunity type
        if 'content' in opportunity or 'writing' in opportunity:
            base_budget = 500  # Low budget for content
        elif 'ecommerce' in opportunity or 'shop' in opportunity:
            base_budget = 2500  # Higher for e-commerce
        elif 'software' in opportunity or 'app' in opportunity:
            base_budget = 3000  # Highest for software
        elif 'trading' in opportunity or 'crypto' in opportunity:
            base_budget = 5000  # Capital needed for trading
        else:
            base_budget = 1500  # Default

        # Add variation
        variation = random.uniform(0.8, 1.2)

        return round(base_budget * variation, -2)  # Round to nearest 100

    def _select_agents_for_plan(self, action_plan: Dict[str, Any]) -> List[str]:
        """Select appropriate agents based on the action plan requirements"""
        opportunity = action_plan.get('opportunity_title', '').lower()

        # Base agents that are always useful
        core_agents = ["orchestrator", "income-builder", "revenue-tracker"]

        # Add specialized agents based on opportunity type
        if 'content' in opportunity or 'writing' in opportunity:
            core_agents.extend(["content-creator", "seo-optimizer", "publisher"])

        if 'digital' in opportunity or 'template' in opportunity:
            core_agents.extend(["designer", "template-builder", "asset-manager"])

        if 'saas' in opportunity or 'software' in opportunity:
            core_agents.extend(["developer", "api-builder", "testing-agent"])

        if 'marketing' in opportunity or 'social' in opportunity:
            core_agents.extend(["social-media-manager", "ad-optimizer", "analytics-agent"])

        if 'investment' in opportunity or 'trading' in opportunity:
            core_agents.extend(["market-analyst", "risk-assessor", "portfolio-manager"])

        # Limit to 10 agents for manageability
        return list(set(core_agents))[:10]

    async def form_execution_team(self, plan_id: str, advisor_review: AdvisorReview) -> TeamFormation:
        """
        Form an execution team based on the advisor's review

        Args:
            plan_id: The action plan ID
            advisor_review: The advisor's review and recommendations

        Returns:
            TeamFormation object with complete team structure
        """
        team_id = f"team_{plan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Select lead agent (usually the orchestrator or most senior agent)
        lead_agent = "orchestrator" if "orchestrator" in advisor_review.recommended_agents else advisor_review.recommended_agents[0]

        # Categorize agents
        core_agents = advisor_review.recommended_agents[:5]  # Top 5 as core
        specialist_agents = advisor_review.recommended_specialists[:3]  # Top 3 specialists
        support_agents = ["monitor", "reporter", "coordinator"]  # Standard support

        # Define roles
        agent_roles = {
            lead_agent: "Team lead - coordinates all activities and reports to advisor",
        }

        for agent in core_agents:
            if agent != lead_agent:
                agent_roles[agent] = f"Core team - executes primary {agent} responsibilities"

        for agent in specialist_agents:
            agent_roles[agent] = f"Specialist - provides expert {agent} services as needed"

        for agent in support_agents:
            agent_roles[agent] = f"Support - handles {agent} functions"

        # Create execution phases
        execution_phases = [
            {
                "phase": 1,
                "name": "Foundation",
                "duration": "1 week",
                "agents": core_agents[:3],
                "deliverables": ["Market research", "Initial setup", "Brand creation"]
            },
            {
                "phase": 2,
                "name": "Launch",
                "duration": "1 week",
                "agents": core_agents,
                "deliverables": ["Product/service launch", "First customers", "Feedback collection"]
            },
            {
                "phase": 3,
                "name": "Scale",
                "duration": "2 weeks",
                "agents": core_agents + specialist_agents,
                "deliverables": ["Growth optimization", "Process automation", "Team expansion"]
            }
        ]

        # Create team formation
        team = TeamFormation(
            team_id=team_id,
            plan_id=plan_id,
            advisor_id=advisor_review.advisor_id,

            # Team composition
            lead_agent=lead_agent,
            core_agents=core_agents,
            specialist_agents=specialist_agents,
            support_agents=support_agents,

            # Roles
            agent_roles=agent_roles,
            coordination_model="collaborative",  # Could be hierarchical or autonomous

            # Execution strategy
            execution_phases=execution_phases,
            communication_channels=["team_channel", "advisor_channel", "user_channel"],
            reporting_structure={
                "daily_standups": True,
                "weekly_reviews": True,
                "advisor_checkpoints": advisor_review.milestone_checkpoints,
                "escalation_threshold": "blocking_issues"
            },

            # Performance tracking
            kpis=advisor_review.success_metrics,
            checkpoints=[datetime.now() + timedelta(days=7*i) for i in range(1, 5)],
            escalation_path=[lead_agent, advisor_review.advisor_id, "platform_admin"]
        )

        # Store team
        self.active_teams[team_id] = team

        self.logger.info(f"Team {team_id} formed with {len(core_agents)} core agents led by {lead_agent}")

        return team

    async def execute_with_team(self, team: TeamFormation, action_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Begin execution of an action plan with the formed team

        Args:
            team: The formed team
            action_plan: The action plan to execute

        Returns:
            Execution status and initial results
        """
        execution_status = {
            "team_id": team.team_id,
            "plan_id": team.plan_id,
            "status": "initiated",
            "start_time": datetime.now().isoformat(),
            "team_size": len(team.core_agents) + len(team.specialist_agents) + len(team.support_agents),
            "phases": len(team.execution_phases),
            "current_phase": 1,
            "agents_activated": [],
            "initial_tasks": []
        }

        # Activate lead agent
        # Check if agent exists in registry using list_agents method
        all_agents = self.agent_registry.list_agents()
        agent_ids = [agent.get('id', '') for agent in all_agents]

        if team.lead_agent in agent_ids:
            execution_status["agents_activated"].append(team.lead_agent)
            execution_status["initial_tasks"].append({
                "agent": team.lead_agent,
                "task": "Initialize team coordination and establish communication channels",
                "status": "assigned"
            })

        # Activate phase 1 agents
        phase_1_agents = team.execution_phases[0]["agents"] if team.execution_phases else []
        for agent in phase_1_agents:
            if agent in agent_ids:
                execution_status["agents_activated"].append(agent)
                execution_status["initial_tasks"].append({
                    "agent": agent,
                    "task": f"Begin phase 1 activities for {action_plan.get('opportunity_title', 'project')}",
                    "status": "assigned"
                })

        # Log execution start
        self.logger.info(f"Execution started for plan {team.plan_id} with team {team.team_id}")

        return execution_status

    async def get_advisor_for_domain(self, domain: str) -> Optional[str]:
        """
        Get the best advisor for a specific domain

        Args:
            domain: The domain string

        Returns:
            Advisor ID or None
        """
        try:
            plan_domain = PlanDomain(domain.lower())
            advisors = self.domain_advisor_map.get(plan_domain, [])
            return advisors[0] if advisors else None
        except ValueError:
            # Domain not recognized, return default
            return "business_strategist"


# Create singleton instance
action_plan_advisor_handoff = ActionPlanAdvisorHandoff()