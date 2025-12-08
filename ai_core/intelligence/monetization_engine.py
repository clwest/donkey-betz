"""
💰 Unified Monetization Engine
Connects AI Income Builder, Content Studio, and all revenue streams
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RevenueStream(Enum):
    """All available revenue streams"""
    # Content Creation
    BLOG_WRITING = "blog_writing"
    SOCIAL_MEDIA = "social_media"
    VIDEO_SCRIPTS = "video_scripts"
    EBOOKS = "ebooks"

    # AI Services
    PROMPT_ENGINEERING = "prompt_engineering"
    AI_AUTOMATION = "ai_automation"
    AI_TUTORING = "ai_tutoring"

    # Digital Products
    TEMPLATES = "templates"
    COURSES = "courses"
    TOOLS = "tools"

    # Trading/Betting
    SPORTS_BETTING = "sports_betting"
    CRYPTO_TRADING = "crypto_trading"
    OPTIONS_TRADING = "options_trading"

    # Freelancing
    CONSULTING = "consulting"
    DEVELOPMENT = "development"
    DESIGN = "design"


@dataclass
class MonetizationOpportunity:
    """A specific monetization opportunity"""
    id: str
    stream: RevenueStream
    title: str
    description: str
    potential_revenue: float
    time_investment: int  # hours
    success_probability: float
    required_tools: List[str]
    ai_assistance_level: float  # 0-1, how much AI can help
    automation_potential: float  # 0-1, how much can be automated
    current_market_demand: float  # 0-1
    competition_level: float  # 0-1
    profit_margin: float  # percentage
    scalability: float  # 0-1


@dataclass
class RevenueMetrics:
    """Track revenue across all streams"""
    total_revenue: float = 0.0
    monthly_revenue: float = 0.0
    weekly_revenue: float = 0.0
    daily_revenue: float = 0.0

    # By stream
    content_revenue: float = 0.0
    ai_services_revenue: float = 0.0
    digital_products_revenue: float = 0.0
    trading_revenue: float = 0.0
    freelancing_revenue: float = 0.0

    # Projections
    projected_monthly: float = 0.0
    projected_yearly: float = 0.0

    # Performance
    best_performing_stream: str = ""
    worst_performing_stream: str = ""
    growth_rate: float = 0.0


class UnifiedMonetizationEngine:
    """
    Central hub for all monetization activities
    Coordinates between Income Builder, Content Studio, and Trading systems
    """

    def __init__(self):
        self.active_streams: List[RevenueStream] = []
        self.opportunities: List[MonetizationOpportunity] = []
        self.metrics = RevenueMetrics()
        self.automation_tasks = []
        self.logger = logging.getLogger(__name__)

        # Initialize integrations with agent and advisor systems
        self._initialize_integrations()
        self._initialize_opportunities()

    def _initialize_integrations(self):
        """Initialize connections to agent and advisor registries"""
        try:
            # Import and initialize registries
            from core.agents.registry import agent_registry
            from advisors.registry import advisor_registry

            self.agent_registry = agent_registry
            self.advisor_registry = advisor_registry

            # Test connections
            agents = self.agent_registry.list_agents()
            advisors = self.advisor_registry.list_advisors()

            self.logger.info(
                f"Monetization Engine connected to {len(agents)} agents and {len(advisors)} advisors"
            )
            self.integrations_active = True

        except Exception as e:
            self.logger.warning(f"Agent/Advisor integrations not available: {e}")
            self.agent_registry = None
            self.advisor_registry = None
            self.integrations_active = False

    def _initialize_opportunities(self):
        """Initialize all monetization opportunities"""

        # Content Creation Opportunities
        self.opportunities.extend([
            MonetizationOpportunity(
                id="blog_seo",
                stream=RevenueStream.BLOG_WRITING,
                title="SEO Blog Content Factory",
                description="Use AI to generate SEO-optimized blog posts at scale",
                potential_revenue=2000.0,
                time_investment=20,
                success_probability=0.85,
                required_tools=["ChatGPT", "SEMrush", "WordPress"],
                ai_assistance_level=0.9,
                automation_potential=0.8,
                current_market_demand=0.9,
                competition_level=0.6,
                profit_margin=0.85,
                scalability=0.95
            ),

            MonetizationOpportunity(
                id="social_automation",
                stream=RevenueStream.SOCIAL_MEDIA,
                title="Automated Social Media Management",
                description="AI-powered social media content creation and scheduling",
                potential_revenue=1500.0,
                time_investment=15,
                success_probability=0.8,
                required_tools=["Buffer", "Canva", "ChatGPT"],
                ai_assistance_level=0.85,
                automation_potential=0.9,
                current_market_demand=0.85,
                competition_level=0.7,
                profit_margin=0.8,
                scalability=0.9
            ),

            MonetizationOpportunity(
                id="video_scripts_youtube",
                stream=RevenueStream.VIDEO_SCRIPTS,
                title="YouTube Script Writing Service",
                description="Create viral video scripts for content creators",
                potential_revenue=3000.0,
                time_investment=25,
                success_probability=0.75,
                required_tools=["ChatGPT", "VidIQ", "TubeBuddy"],
                ai_assistance_level=0.8,
                automation_potential=0.7,
                current_market_demand=0.95,
                competition_level=0.5,
                profit_margin=0.9,
                scalability=0.85
            ),
        ])

        # AI Services Opportunities
        self.opportunities.extend([
            MonetizationOpportunity(
                id="prompt_marketplace",
                stream=RevenueStream.PROMPT_ENGINEERING,
                title="Premium Prompt Marketplace",
                description="Sell optimized prompts for specific industries",
                potential_revenue=2500.0,
                time_investment=20,
                success_probability=0.85,
                required_tools=["PromptBase", "ChatGPT", "Claude"],
                ai_assistance_level=0.95,
                automation_potential=0.6,
                current_market_demand=0.95,
                competition_level=0.4,
                profit_margin=0.95,
                scalability=1.0
            ),

            MonetizationOpportunity(
                id="workflow_automation",
                stream=RevenueStream.AI_AUTOMATION,
                title="Business Process Automation",
                description="Create AI-powered automation workflows for businesses",
                potential_revenue=5000.0,
                time_investment=30,
                success_probability=0.7,
                required_tools=["Zapier", "Make", "ChatGPT API"],
                ai_assistance_level=0.8,
                automation_potential=0.85,
                current_market_demand=0.9,
                competition_level=0.5,
                profit_margin=0.85,
                scalability=0.95
            ),
        ])

        # Digital Products
        self.opportunities.extend([
            MonetizationOpportunity(
                id="template_store",
                stream=RevenueStream.TEMPLATES,
                title="Digital Template Empire",
                description="Create and sell templates on multiple platforms",
                potential_revenue=1800.0,
                time_investment=15,
                success_probability=0.8,
                required_tools=["Canva", "Gumroad", "Etsy"],
                ai_assistance_level=0.85,
                automation_potential=0.7,
                current_market_demand=0.8,
                competition_level=0.65,
                profit_margin=0.92,
                scalability=1.0
            ),
        ])

        # Trading/Betting (with proper risk management)
        self.opportunities.extend([
            MonetizationOpportunity(
                id="sports_arbitrage",
                stream=RevenueStream.SPORTS_BETTING,
                title="Sports Arbitrage Scanner",
                description="Find and execute risk-free arbitrage opportunities",
                potential_revenue=1000.0,
                time_investment=10,
                success_probability=0.95,  # Arbitrage is guaranteed profit
                required_tools=["Odds API", "Multiple Sportsbooks"],
                ai_assistance_level=0.7,
                automation_potential=0.9,
                current_market_demand=0.7,
                competition_level=0.3,
                profit_margin=0.03,  # Small but guaranteed
                scalability=0.6  # Limited by market inefficiencies
            ),
        ])

    async def analyze_best_opportunities(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze and rank best opportunities for user"""

        scored_opportunities = []

        for opp in self.opportunities:
            score = self._calculate_opportunity_score(opp, user_profile)

            roi = (opp.potential_revenue / max(opp.time_investment, 1)) * opp.profit_margin

            scored_opportunities.append({
                "opportunity": opp,
                "score": score,
                "roi": roi,
                "monthly_potential": opp.potential_revenue,
                "hours_required": opp.time_investment,
                "quick_start": opp.time_investment <= 15,
                "highly_automated": opp.automation_potential >= 0.8,
                "ai_powered": opp.ai_assistance_level >= 0.8
            })

        # Sort by score
        scored_opportunities.sort(key=lambda x: x["score"], reverse=True)

        return scored_opportunities[:5]  # Top 5

    def _calculate_opportunity_score(self, opp: MonetizationOpportunity, user_profile: Dict[str, Any]) -> float:
        """Calculate opportunity score based on multiple factors"""

        score = 0.0

        # Market opportunity
        score += opp.current_market_demand * 0.2
        score += (1 - opp.competition_level) * 0.15

        # Profitability
        score += opp.profit_margin * 0.15
        score += (opp.potential_revenue / 5000) * 0.1  # Normalized to 5k max

        # Ease of execution
        score += opp.ai_assistance_level * 0.15
        score += opp.automation_potential * 0.1
        score += opp.success_probability * 0.1

        # Scalability
        score += opp.scalability * 0.05

        # User fit (if they have limited time, prefer automated)
        if user_profile.get("available_hours", 20) < 20:
            score += opp.automation_potential * 0.1

        # If user has $0, prefer quick-start opportunities
        if user_profile.get("current_balance", 0) == 0:
            if opp.time_investment <= 10:
                score += 0.1

        return min(score, 1.0)

    async def create_monetization_plan(self, selected_streams: List[str]) -> Dict[str, Any]:
        """Create comprehensive monetization plan"""

        plan = {
            "streams": [],
            "total_potential": 0,
            "total_hours": 0,
            "automation_setup": [],
            "week_by_week": [],
            "tools_needed": set(),
            "projected_income": {
                "week_1": 0,
                "month_1": 0,
                "month_3": 0,
                "month_6": 0,
                "year_1": 0
            }
        }

        for stream_id in selected_streams:
            opp = next((o for o in self.opportunities if o.id == stream_id), None)
            if opp:
                plan["streams"].append({
                    "id": opp.id,
                    "title": opp.title,
                    "revenue": opp.potential_revenue,
                    "hours": opp.time_investment
                })

                plan["total_potential"] += opp.potential_revenue
                plan["total_hours"] += opp.time_investment
                plan["tools_needed"].update(opp.required_tools)

                # Add automation tasks
                if opp.automation_potential > 0.7:
                    plan["automation_setup"].append({
                        "stream": opp.title,
                        "automation_level": f"{int(opp.automation_potential * 100)}%",
                        "setup_time": "2-4 hours",
                        "maintenance": "1 hour/week"
                    })

        # Create week-by-week plan
        plan["week_by_week"] = [
            {
                "week": 1,
                "focus": "Setup & Quick Wins",
                "tasks": [
                    "Set up required tools and accounts",
                    "Create first content pieces",
                    "Launch automation workflows",
                    "Apply for first gigs"
                ],
                "expected_revenue": plan["total_potential"] * 0.05
            },
            {
                "week": 2,
                "focus": "Scale & Optimize",
                "tasks": [
                    "Refine automation systems",
                    "Increase output volume",
                    "Gather first testimonials",
                    "Optimize pricing"
                ],
                "expected_revenue": plan["total_potential"] * 0.1
            },
            {
                "week": 3,
                "focus": "Diversify & Grow",
                "tasks": [
                    "Add second revenue stream",
                    "Build recurring client base",
                    "Create passive income products",
                    "Implement upsells"
                ],
                "expected_revenue": plan["total_potential"] * 0.15
            },
            {
                "week": 4,
                "focus": "Systematize & Scale",
                "tasks": [
                    "Document all processes",
                    "Hire virtual assistant if needed",
                    "Launch premium offerings",
                    "Plan next month's growth"
                ],
                "expected_revenue": plan["total_potential"] * 0.25
            }
        ]

        # Calculate projections
        plan["projected_income"]["week_1"] = plan["total_potential"] * 0.05
        plan["projected_income"]["month_1"] = plan["total_potential"] * 0.55
        plan["projected_income"]["month_3"] = plan["total_potential"] * 2.5
        plan["projected_income"]["month_6"] = plan["total_potential"] * 6
        plan["projected_income"]["year_1"] = plan["total_potential"] * 15

        plan["tools_needed"] = list(plan["tools_needed"])

        return plan

    async def track_revenue(self, stream: str, amount: float) -> Dict[str, Any]:
        """Track revenue from a specific stream"""

        # Update metrics
        self.metrics.total_revenue += amount
        self.metrics.daily_revenue += amount

        # Categorize
        if stream in ["blog_writing", "social_media", "video_scripts", "ebooks"]:
            self.metrics.content_revenue += amount
        elif stream in ["prompt_engineering", "ai_automation", "ai_tutoring"]:
            self.metrics.ai_services_revenue += amount
        elif stream in ["templates", "courses", "tools"]:
            self.metrics.digital_products_revenue += amount
        elif stream in ["sports_betting", "crypto_trading", "options_trading"]:
            self.metrics.trading_revenue += amount
        else:
            self.metrics.freelancing_revenue += amount

        # Calculate projections
        self.metrics.projected_monthly = self.metrics.daily_revenue * 30
        self.metrics.projected_yearly = self.metrics.monthly_revenue * 12

        return {
            "stream": stream,
            "amount": amount,
            "total_revenue": self.metrics.total_revenue,
            "daily_revenue": self.metrics.daily_revenue,
            "projected_monthly": self.metrics.projected_monthly
        }

    def get_revenue_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive revenue dashboard"""

        return {
            "current_metrics": {
                "total_revenue": self.metrics.total_revenue,
                "monthly_revenue": self.metrics.monthly_revenue,
                "weekly_revenue": self.metrics.weekly_revenue,
                "daily_revenue": self.metrics.daily_revenue
            },
            "by_category": {
                "content": self.metrics.content_revenue,
                "ai_services": self.metrics.ai_services_revenue,
                "digital_products": self.metrics.digital_products_revenue,
                "trading": self.metrics.trading_revenue,
                "freelancing": self.metrics.freelancing_revenue
            },
            "projections": {
                "monthly": self.metrics.projected_monthly,
                "yearly": self.metrics.projected_yearly
            },
            "active_streams": len(self.active_streams),
            "opportunities_available": len(self.opportunities),
            "best_performer": self.metrics.best_performing_stream,
            "growth_rate": f"{self.metrics.growth_rate:.1f}%"
        }

    async def automate_content_monetization(self) -> Dict[str, Any]:
        """Automate content creation and monetization"""

        automation_plan = {
            "blog_automation": {
                "frequency": "3 posts/day",
                "platforms": ["WordPress", "Medium", "LinkedIn"],
                "monetization": ["AdSense", "Affiliate Links", "Sponsored Content"],
                "estimated_revenue": "$50-200/day"
            },
            "social_automation": {
                "frequency": "10 posts/day across platforms",
                "platforms": ["Twitter/X", "Instagram", "TikTok", "LinkedIn"],
                "monetization": ["Sponsored Posts", "Affiliate Marketing", "Product Placement"],
                "estimated_revenue": "$30-150/day"
            },
            "video_script_automation": {
                "frequency": "5 scripts/day",
                "platforms": ["YouTube", "TikTok", "Instagram Reels"],
                "monetization": ["Direct Sales", "Subscription Service", "Custom Orders"],
                "estimated_revenue": "$100-500/day"
            },
            "template_automation": {
                "frequency": "10 new templates/week",
                "platforms": ["Etsy", "Gumroad", "Creative Market"],
                "monetization": ["Direct Sales", "Bundles", "Subscriptions"],
                "estimated_revenue": "$20-100/day"
            }
        }

        return automation_plan

    async def analyze_opportunity_with_agents(self, opportunity_id: str) -> Dict[str, Any]:
        """Analyze monetization opportunity using agent orchestration"""
        if not self.integrations_active:
            return {"error": "Agent integrations not available"}

        try:
            # Find the opportunity
            opportunity = next(
                (opp for opp in self.opportunities if opp.id == opportunity_id),
                None
            )

            if not opportunity:
                return {"error": "Opportunity not found"}

            # Get relevant agents for analysis
            research_agent = self.agent_registry.find_best_agent(
                task_description=f"market research for {opportunity.title}",
                required_capabilities=["research", "market_analysis"],
                preferred_specialization="research"
            )

            financial_agent = self.agent_registry.find_best_agent(
                task_description="financial analysis and ROI calculation",
                required_capabilities=["financial_analysis", "risk_assessment"],
                preferred_specialization="financial"
            )

            # Get relevant advisors
            business_advisor = self.advisor_registry.find_best_advisor(
                consultation_topic=f"business strategy for {opportunity.stream.value}",
                domain=self.advisor_registry.AdvisorDomain.BUSINESS_STRATEGY
            )

            financial_advisor = self.advisor_registry.find_best_advisor(
                consultation_topic="revenue optimization and monetization strategy",
                domain=self.advisor_registry.AdvisorDomain.FINANCIAL_PLANNING
            )

            # Compile analysis
            analysis = {
                "opportunity": {
                    "id": opportunity.id,
                    "title": opportunity.title,
                    "stream": opportunity.stream.value,
                    "potential_revenue": opportunity.potential_revenue,
                    "success_probability": opportunity.success_probability
                },
                "ai_assistance": {
                    "research_agent": {
                        "name": research_agent.get("name") if research_agent else None,
                        "capabilities": research_agent.get("capabilities", []) if research_agent else []
                    },
                    "financial_agent": {
                        "name": financial_agent.get("name") if financial_agent else None,
                        "capabilities": financial_agent.get("capabilities", []) if financial_agent else []
                    }
                },
                "advisory_support": {
                    "business_advisor": {
                        "name": business_advisor.name if business_advisor else None,
                        "expertise": business_advisor.expertise_level.value if business_advisor else None,
                        "specializations": business_advisor.specializations if business_advisor else []
                    },
                    "financial_advisor": {
                        "name": financial_advisor.name if financial_advisor else None,
                        "expertise": financial_advisor.expertise_level.value if financial_advisor else None,
                        "specializations": financial_advisor.specializations if financial_advisor else []
                    }
                },
                "intelligence_enhancement": {
                    "ai_assistance_level": opportunity.ai_assistance_level,
                    "automation_potential": opportunity.automation_potential,
                    "agent_support_available": research_agent is not None and financial_agent is not None,
                    "advisor_support_available": business_advisor is not None and financial_advisor is not None
                },
                "recommendations": self._generate_opportunity_recommendations(opportunity)
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing opportunity with agents: {e}")
            return {"error": str(e)}

    def _generate_opportunity_recommendations(self, opportunity: MonetizationOpportunity) -> List[str]:
        """Generate AI-powered recommendations for an opportunity"""
        recommendations = []

        # AI assistance recommendations
        if opportunity.ai_assistance_level > 0.8:
            recommendations.append("High AI leverage opportunity - prioritize automation")

        if opportunity.automation_potential > 0.8:
            recommendations.append("Excellent automation potential - build scalable workflows")

        # Market recommendations
        if opportunity.current_market_demand > 0.8 and opportunity.competition_level < 0.6:
            recommendations.append("Strong market opportunity with low competition - move quickly")

        if opportunity.profit_margin > 0.8:
            recommendations.append("High profit margin - focus on premium positioning")

        if opportunity.scalability > 0.8:
            recommendations.append("Highly scalable - prepare for rapid growth infrastructure")

        # Financial recommendations
        roi = (opportunity.potential_revenue - (opportunity.time_investment * 50)) / (opportunity.time_investment * 50)
        if roi > 2.0:
            recommendations.append(f"Excellent ROI potential ({roi:.1f}x) - high priority")

        return recommendations

    async def create_monetization_workflow(self, opportunity_id: str, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent-orchestrated workflow for monetization opportunity"""
        if not self.integrations_active:
            return {"error": "Agent orchestration not available"}

        try:
            opportunity = next(
                (opp for opp in self.opportunities if opp.id == opportunity_id),
                None
            )

            if not opportunity:
                return {"error": "Opportunity not found"}

            # Create multi-agent workflow
            workflow_steps = []

            # Step 1: Market Research
            research_agent = self.agent_registry.find_best_agent(
                task_description="comprehensive market research",
                preferred_specialization="research"
            )

            if research_agent:
                workflow_steps.append({
                    "step": 1,
                    "phase": "Market Research",
                    "agent": research_agent.get("name"),
                    "tasks": [
                        "Analyze current market trends",
                        "Identify target audience",
                        "Research competition",
                        "Validate demand"
                    ],
                    "estimated_time": "2-4 hours",
                    "deliverables": ["Market analysis report", "Target audience profile"]
                })

            # Step 2: Strategy Development
            strategy_agent = self.agent_registry.find_best_agent(
                task_description="business strategy development",
                preferred_specialization="business"
            )

            if strategy_agent:
                workflow_steps.append({
                    "step": 2,
                    "phase": "Strategy Development",
                    "agent": strategy_agent.get("name"),
                    "tasks": [
                        "Develop monetization strategy",
                        "Create pricing model",
                        "Plan execution timeline",
                        "Identify resource requirements"
                    ],
                    "estimated_time": "3-5 hours",
                    "deliverables": ["Strategy document", "Implementation plan"]
                })

            # Step 3: Content Creation
            content_agent = self.agent_registry.find_best_agent(
                task_description="content creation and marketing",
                preferred_specialization="content"
            )

            if content_agent:
                workflow_steps.append({
                    "step": 3,
                    "phase": "Content Creation",
                    "agent": content_agent.get("name"),
                    "tasks": [
                        "Create marketing materials",
                        "Develop content templates",
                        "Design sales materials",
                        "Build automation workflows"
                    ],
                    "estimated_time": "4-8 hours",
                    "deliverables": ["Content library", "Marketing materials", "Automation setup"]
                })

            # Step 4: Implementation
            tech_agent = self.agent_registry.find_best_agent(
                task_description="technical implementation",
                preferred_specialization="technical"
            )

            if tech_agent:
                workflow_steps.append({
                    "step": 4,
                    "phase": "Technical Implementation",
                    "agent": tech_agent.get("name"),
                    "tasks": [
                        "Set up platforms and tools",
                        "Configure automation",
                        "Test workflows",
                        "Deploy systems"
                    ],
                    "estimated_time": "3-6 hours",
                    "deliverables": ["Deployed systems", "Documentation", "Testing results"]
                })

            # Generate workflow metadata
            workflow = {
                "opportunity_id": opportunity_id,
                "opportunity_title": opportunity.title,
                "workflow_steps": workflow_steps,
                "total_estimated_time": sum([
                    int(step.get("estimated_time", "0-0 hours").split("-")[0])
                    for step in workflow_steps
                ]),
                "total_agents_involved": len(workflow_steps),
                "success_probability": opportunity.success_probability,
                "potential_revenue": opportunity.potential_revenue,
                "ai_assistance_level": opportunity.ai_assistance_level,
                "automation_level": opportunity.automation_potential,
                "recommended_start_date": "immediate",
                "priority_level": self._calculate_priority(opportunity)
            }

            return workflow

        except Exception as e:
            self.logger.error(f"Error creating monetization workflow: {e}")
            return {"error": str(e)}

    def _calculate_priority(self, opportunity: MonetizationOpportunity) -> str:
        """Calculate priority level for an opportunity"""
        score = 0
        score += opportunity.success_probability * 30
        score += opportunity.current_market_demand * 25
        score += (1 - opportunity.competition_level) * 20
        score += opportunity.profit_margin * 15
        score += opportunity.ai_assistance_level * 10

        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

    def get_integrated_system_status(self) -> Dict[str, Any]:
        """Get status of all integrated systems"""
        status = {
            "monetization_engine": "active",
            "integrations": {
                "agent_registry": self.integrations_active and self.agent_registry is not None,
                "advisor_registry": self.integrations_active and self.advisor_registry is not None
            },
            "capabilities": {
                "opportunity_analysis": self.integrations_active,
                "agent_orchestration": self.integrations_active,
                "advisor_consultation": self.integrations_active,
                "workflow_automation": self.integrations_active
            }
        }

        if self.integrations_active:
            try:
                agent_stats = self.agent_registry.get_registry_stats()
                advisor_stats = self.advisor_registry.get_registry_stats()

                status["connected_resources"] = {
                    "total_agents": agent_stats.active_agents,
                    "total_advisors": advisor_stats["total_advisors"],
                    "agent_specializations": list(agent_stats.popular_specializations.keys()),
                    "advisor_domains": len(advisor_stats["domain_distribution"])
                }
            except Exception as e:
                status["connection_error"] = str(e)

        return status


def record_earnings(user, amount, source):
    """
    Record real earnings from actual income generation
    This function tracks when users actually earn money through the platform
    """
    try:
        from django.utils import timezone
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        # Import models
        from intelligence.models import RevenueMetrics
        from core.models import UnifiedUser

        # Ensure user is a UnifiedUser instance
        if isinstance(user, str):
            user = UnifiedUser.objects.get(username=user)

        # Create or update revenue metrics for today
        today = timezone.now().date()
        revenue_metric, created = RevenueMetrics.objects.get_or_create(
            date=today,
            defaults={
                'revenue_generated': 0.0,
                'opportunities_identified': 0,
                'conversions': 0,
                'conversion_rate': 0.0
            }
        )

        # Add the earnings
        revenue_metric.revenue_generated += float(amount)
        revenue_metric.conversions += 1

        # Update conversion rate (simple calculation)
        if revenue_metric.opportunities_identified > 0:
            revenue_metric.conversion_rate = revenue_metric.conversions / revenue_metric.opportunities_identified

        revenue_metric.save()

        logger.info(f"💰 REAL EARNINGS RECORDED: ${amount} from {source} for user {user.username}")

        # Broadcast to Revenue Dashboard via WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                # Get total earnings for user
                from django.db import models
                total_earnings = RevenueMetrics.objects.filter(
                    date__gte=timezone.now().date() - timedelta(days=30)
                ).aggregate(
                    total=models.Sum('revenue_generated')
                )['total'] or 0

                # Send to user-specific revenue channel
                async_to_sync(channel_layer.group_send)(
                    f'user_{user.id}_revenue',
                    {
                        'type': 'revenue_update',
                        'data': {
                            'amount': float(amount),
                            'total': float(total_earnings),
                            'source': source,
                            'timestamp': timezone.now().isoformat(),
                            'user': user.username,
                            'real_earnings': True
                        }
                    }
                )

                # Also send to general revenue monitoring
                async_to_sync(channel_layer.group_send)(
                    'revenue_monitoring',
                    {
                        'type': 'earnings_notification',
                        'data': {
                            'amount': float(amount),
                            'source': source,
                            'user': user.username,
                            'timestamp': timezone.now().isoformat()
                        }
                    }
                )

                logger.info(f"📡 Revenue update broadcasted to dashboard")

            except Exception as ws_error:
                logger.warning(f"Could not broadcast revenue update: {ws_error}")

        return {
            'success': True,
            'earnings_recorded': float(amount),
            'total_earnings': float(revenue_metric.revenue_generated),
            'source': source,
            'date': today.isoformat()
        }

    except Exception as e:
        logger.error(f"Error recording earnings: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def record_potential_earnings(source, amount, application_id=None, opportunity_id=None):
    """
    Record potential earnings from job applications and opportunities
    This tracks revenue opportunities even before they convert to actual earnings
    """
    try:
        from django.utils import timezone
        from intelligence.models import RevenueMetrics
        from django import models

        # Get or create today's revenue metrics
        today = timezone.now().date()
        revenue_metric, created = RevenueMetrics.objects.get_or_create(
            date=today,
            defaults={
                'revenue_generated': 0.0,
                'opportunities_identified': 0,
                'conversions': 0,
                'conversion_rate': 0.0
            }
        )

        # Increment opportunities identified
        revenue_metric.opportunities_identified += 1

        # Update conversion rate
        if revenue_metric.opportunities_identified > 0:
            revenue_metric.conversion_rate = revenue_metric.conversions / revenue_metric.opportunities_identified

        revenue_metric.save()

        # Store the potential earnings details (could extend model to track this)
        logger.info(f"📈 POTENTIAL EARNINGS TRACKED: ${amount} from {source}")

        # Broadcast potential earnings to dashboard
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    'revenue_monitoring',
                    {
                        'type': 'potential_earnings_update',
                        'data': {
                            'potential_amount': float(amount),
                            'source': source,
                            'application_id': application_id,
                            'opportunity_id': opportunity_id,
                            'timestamp': timezone.now().isoformat(),
                            'total_opportunities_today': revenue_metric.opportunities_identified
                        }
                    }
                )
        except Exception as ws_error:
            logger.warning(f"Could not broadcast potential earnings: {ws_error}")

        return {
            'success': True,
            'potential_earnings': float(amount),
            'opportunities_tracked': revenue_metric.opportunities_identified,
            'source': source
        }

    except Exception as e:
        logger.error(f"Error recording potential earnings: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# Global monetization engine instance
monetization_engine = UnifiedMonetizationEngine()