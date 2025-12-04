"""
Research Orchestrator - The Brain of the Autonomous Business Pipeline
======================================================================

Session 338: End-to-End Autonomous Business Idea Pipeline

This orchestrator chains research agents together to create a complete
business intelligence package from a raw business idea.

Flow:
    User: "I have a business idea for an AI podcast"
        ↓
    ResearchOrchestrator.execute_full_research()
        ↓
    1. CompetitorAnalysisAgent → Market landscape, competitors, SWOT
        ↓ (passes context)
    2. CustomerResearchAgent → Personas, pain points, opportunities
        ↓ (passes context)
    3. BrandStrategyAgent → Positioning, messaging, visual direction
        ↓
    4. Synthesis → Complete business plan with recommendations
        ↓
    Return: BusinessPlan with all research + actionable next steps

Usage:
    from core.services.research_orchestrator import ResearchOrchestrator

    orchestrator = ResearchOrchestrator(user=request.user)
    result = orchestrator.execute_full_research(
        business_idea="AI-powered podcast platform",
        constraints={"budget": "$5k", "timeline": "3 months"}
    )
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class ResearchPhaseResult:
    """Result from a single research phase."""
    phase: str
    agent_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0


@dataclass
class FullResearchResult:
    """Complete result from full research orchestration."""
    success: bool
    project_id: Optional[str] = None
    business_idea: str = ""
    phases_completed: List[str] = field(default_factory=list)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    customer_research: Dict[str, Any] = field(default_factory=dict)
    brand_strategy: Dict[str, Any] = field(default_factory=dict)
    business_plan: Dict[str, Any] = field(default_factory=dict)
    next_actions: List[str] = field(default_factory=list)
    total_execution_time_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'project_id': self.project_id,
            'business_idea': self.business_idea,
            'phases_completed': self.phases_completed,
            'competitor_analysis': self.competitor_analysis,
            'customer_research': self.customer_research,
            'brand_strategy': self.brand_strategy,
            'business_plan': self.business_plan,
            'next_actions': self.next_actions,
            'total_execution_time_ms': self.total_execution_time_ms,
            'error': self.error,
        }


class ResearchOrchestrator:
    """
    Orchestrates the complete business research pipeline.

    This is the brain that:
    1. Takes a raw business idea
    2. Creates a project to track the research
    3. Runs all research agents in sequence (with context passing)
    4. Synthesizes into a complete business plan
    5. Returns actionable next steps

    Attributes:
        user: Django User object
        project: PartnershipProject being researched
    """

    def __init__(self, user=None):
        """
        Initialize the orchestrator.

        Args:
            user: Django User object for tracking
        """
        self.user = user
        self.project = None
        self._competitor_agent = None
        self._customer_agent = None
        self._brand_agent = None
        self._openai_client = None

    # ==================== Lazy-Loaded Agents ====================

    @property
    def competitor_agent(self):
        """Lazy-load CompetitorAnalysisAgent."""
        if self._competitor_agent is None:
            from core.agents.business import CompetitorAnalysisAgent
            self._competitor_agent = CompetitorAnalysisAgent(user=self.user)
        return self._competitor_agent

    @property
    def customer_agent(self):
        """Lazy-load CustomerResearchAgent."""
        if self._customer_agent is None:
            from core.agents.business import CustomerResearchAgent
            self._customer_agent = CustomerResearchAgent(user=self.user)
        return self._customer_agent

    @property
    def brand_agent(self):
        """Lazy-load BrandStrategyAgent."""
        if self._brand_agent is None:
            from core.agents.business import BrandStrategyAgent
            self._brand_agent = BrandStrategyAgent(user=self.user)
        return self._brand_agent

    @property
    def openai_client(self):
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            from django.conf import settings
            from openai import OpenAI
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    # ==================== Main Entry Point ====================

    def execute_full_research(
        self,
        business_idea: str,
        constraints: Dict[str, Any] = None,
        create_project: bool = True
    ) -> FullResearchResult:
        """
        Execute the complete research pipeline for a business idea.

        This is the main entry point that:
        1. Creates a project (if requested)
        2. Runs competitor analysis
        3. Runs customer research (with competitor context)
        4. Runs brand strategy (with all prior context)
        5. Synthesizes into business plan
        6. Returns complete result with next actions

        Args:
            business_idea: The raw business idea from the user
            constraints: Optional dict with budget, timeline, etc.
            create_project: Whether to create a PartnershipProject

        Returns:
            FullResearchResult with all research and recommendations
        """
        start_time = time.time()
        constraints = constraints or {}

        logger.info(f"Starting full research for: {business_idea[:50]}...")

        result = FullResearchResult(
            success=False,
            business_idea=business_idea
        )

        try:
            # Step 1: Create project if requested
            if create_project:
                self.project = self._create_project(business_idea, constraints)
                result.project_id = str(self.project.id)
                logger.info(f"Created project: {self.project.id}")

            # Step 2: Run competitor analysis
            competitor_result = self._run_competitor_analysis(business_idea)
            if competitor_result.success:
                result.competitor_analysis = competitor_result.data
                result.phases_completed.append('competitor_analysis')
                logger.info("Competitor analysis complete")
            else:
                logger.warning(f"Competitor analysis failed: {competitor_result.error}")

            # Step 3: Run customer research (with competitor context)
            customer_context = self._extract_customer_context(result.competitor_analysis)
            customer_result = self._run_customer_research(
                business_idea,
                prior_context=customer_context
            )
            if customer_result.success:
                result.customer_research = customer_result.data
                result.phases_completed.append('customer_research')
                logger.info("Customer research complete")
            else:
                logger.warning(f"Customer research failed: {customer_result.error}")

            # Step 4: Run brand strategy (with all prior context)
            brand_context = self._extract_brand_context(
                result.competitor_analysis,
                result.customer_research
            )
            brand_result = self._run_brand_strategy(
                business_idea,
                prior_context=brand_context
            )
            if brand_result.success:
                result.brand_strategy = brand_result.data
                result.phases_completed.append('brand_strategy')
                logger.info("Brand strategy complete")
            else:
                logger.warning(f"Brand strategy failed: {brand_result.error}")

            # Step 5: Synthesize into business plan
            if len(result.phases_completed) >= 2:  # Need at least 2 phases
                business_plan = self._synthesize_business_plan(
                    business_idea=business_idea,
                    competitor_analysis=result.competitor_analysis,
                    customer_research=result.customer_research,
                    brand_strategy=result.brand_strategy,
                    constraints=constraints
                )
                result.business_plan = business_plan
                result.phases_completed.append('synthesis')
                logger.info("Business plan synthesis complete")

            # Step 6: Generate next actions
            result.next_actions = self._generate_next_actions(
                business_plan=result.business_plan,
                constraints=constraints
            )

            # Mark success if we completed key phases
            result.success = len(result.phases_completed) >= 3

            # Update project with research results
            if self.project and result.success:
                self._update_project_with_research(result)

        except Exception as e:
            logger.error(f"Research orchestration failed: {e}")
            result.error = str(e)

        result.total_execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Research complete: {len(result.phases_completed)} phases, "
            f"{result.total_execution_time_ms}ms"
        )

        return result

    # ==================== Phase Execution ====================

    def _run_competitor_analysis(self, business_idea: str) -> ResearchPhaseResult:
        """Run competitor analysis phase."""
        start_time = time.time()

        try:
            task = f"Analyze competitors for: {business_idea}"

            result = self.competitor_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='competitor_analysis',
                agent_name='CompetitorAnalysisAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='competitor_analysis',
                agent_name='CompetitorAnalysisAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_customer_research(
        self,
        business_idea: str,
        prior_context: str = ""
    ) -> ResearchPhaseResult:
        """Run customer research phase."""
        start_time = time.time()

        try:
            task = f"Research target customers for: {business_idea}"
            if prior_context:
                task += f"\n\nContext from competitor analysis:\n{prior_context}"

            result = self.customer_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='customer_research',
                agent_name='CustomerResearchAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='customer_research',
                agent_name='CustomerResearchAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_brand_strategy(
        self,
        business_idea: str,
        prior_context: str = ""
    ) -> ResearchPhaseResult:
        """Run brand strategy phase."""
        start_time = time.time()

        try:
            task = f"Create brand strategy for: {business_idea}"
            if prior_context:
                task += f"\n\nContext from prior research:\n{prior_context}"

            result = self.brand_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='brand_strategy',
                agent_name='BrandStrategyAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='brand_strategy',
                agent_name='BrandStrategyAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Context Extraction ====================

    def _extract_customer_context(self, competitor_data: Dict[str, Any]) -> str:
        """Extract relevant context for customer research from competitor analysis."""
        if not competitor_data:
            return ""

        analysis = competitor_data.get('analysis', {})
        if isinstance(analysis, str):
            # Just use first 500 chars of text analysis
            return analysis[:500]

        # Extract key points for context
        context_parts = []

        if 'market_overview' in analysis:
            context_parts.append(f"Market: {analysis['market_overview'][:200]}")

        if 'competitors' in analysis:
            competitors = analysis['competitors']
            if isinstance(competitors, list):
                names = [c.get('name', '') for c in competitors[:5] if c.get('name')]
                if names:
                    context_parts.append(f"Key competitors: {', '.join(names)}")

        return "\n".join(context_parts)

    def _extract_brand_context(
        self,
        competitor_data: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> str:
        """Extract relevant context for brand strategy from prior research."""
        context_parts = []

        # From competitor analysis
        if competitor_data:
            analysis = competitor_data.get('analysis', '')
            if isinstance(analysis, str) and analysis:
                context_parts.append(f"Competitor landscape: {analysis[:300]}")

        # From customer research
        if customer_data:
            analysis = customer_data.get('analysis', '')
            if isinstance(analysis, str) and analysis:
                context_parts.append(f"Customer insights: {analysis[:300]}")

        return "\n\n".join(context_parts)

    # ==================== Synthesis ====================

    def _synthesize_business_plan(
        self,
        business_idea: str,
        competitor_analysis: Dict[str, Any],
        customer_research: Dict[str, Any],
        brand_strategy: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize all research into a cohesive business plan.

        This uses GPT to:
        1. Combine insights from all research phases
        2. Identify the strongest market opportunity
        3. Create an actionable go-to-market strategy
        4. Generate specific recommendations
        """
        # Build synthesis prompt
        prompt = f"""You are a business strategist synthesizing research into an actionable business plan.

BUSINESS IDEA: {business_idea}

CONSTRAINTS:
{json.dumps(constraints, indent=2) if constraints else "None specified"}

COMPETITOR ANALYSIS:
{self._format_research_for_synthesis(competitor_analysis)}

CUSTOMER RESEARCH:
{self._format_research_for_synthesis(customer_research)}

BRAND STRATEGY:
{self._format_research_for_synthesis(brand_strategy)}

Based on ALL of this research, create a comprehensive but concise business plan with:

1. **EXECUTIVE SUMMARY** (2-3 sentences)
   - What is this business?
   - Why will it succeed?

2. **MARKET OPPORTUNITY** (3-4 bullets)
   - Size of opportunity
   - Key gaps identified
   - Timing factors

3. **TARGET CUSTOMER** (3-4 bullets)
   - Primary persona
   - Key pain points to solve
   - How they currently solve the problem

4. **COMPETITIVE POSITIONING** (3-4 bullets)
   - How to differentiate
   - Key advantages
   - Potential moats

5. **GO-TO-MARKET STRATEGY** (4-5 bullets)
   - Launch approach
   - Initial channels
   - Pricing strategy
   - First 90 days priorities

6. **KEY RISKS & MITIGATIONS** (2-3 bullets)
   - Biggest risks
   - How to address them

7. **SUCCESS METRICS** (3-4 bullets)
   - What to measure
   - Target numbers for first 6 months

Return this as a structured analysis. Be specific and actionable, not generic."""

        try:
            # Session 338: Use gpt-5-mini for cost efficiency
            # Reasoning models need max_completion_tokens (not max_tokens)
            # and allocate tokens for internal reasoning + visible output
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=6000,  # High enough for reasoning + output
            )

            synthesis_text = response.choices[0].message.content

            return {
                'summary': synthesis_text,
                'generated_at': time.time(),
                'sources': {
                    'competitor_analysis': bool(competitor_analysis),
                    'customer_research': bool(customer_research),
                    'brand_strategy': bool(brand_strategy)
                }
            }

        except Exception as e:
            logger.error(f"Business plan synthesis failed: {e}")
            return {
                'error': str(e),
                'fallback': 'Unable to synthesize business plan'
            }

    def _format_research_for_synthesis(self, research_data: Dict[str, Any]) -> str:
        """Format research data for the synthesis prompt."""
        if not research_data:
            return "No data available"

        analysis = research_data.get('analysis', '')
        if isinstance(analysis, str):
            return analysis[:1500]  # Limit length
        elif isinstance(analysis, dict):
            return json.dumps(analysis, indent=2)[:1500]
        else:
            return str(research_data)[:1500]

    # ==================== Next Actions ====================

    def _generate_next_actions(
        self,
        business_plan: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate specific next actions based on the business plan."""
        actions = []

        # Default actions regardless of plan
        actions.append("Review the business plan and validate key assumptions")
        actions.append("Create logo and brand assets using the brand strategy")
        actions.append("Set up landing page to test market interest")

        # Budget-specific actions
        budget = constraints.get('budget', '').lower() if constraints else ''
        if '$' in budget or 'k' in budget:
            actions.append("Create detailed budget allocation for first phase")

        # Timeline-specific actions
        timeline = constraints.get('timeline', '').lower() if constraints else ''
        if 'month' in timeline or 'week' in timeline:
            actions.append("Create project timeline with milestones")

        # If we have a business plan, add specific actions
        if business_plan and 'summary' in business_plan:
            actions.append("Begin customer discovery interviews (target: 10 conversations)")
            actions.append("Create MVP feature list based on customer pain points")

        return actions[:6]  # Limit to 6 actions

    # ==================== Project Management ====================

    def _create_project(
        self,
        business_idea: str,
        constraints: Dict[str, Any]
    ) -> 'PartnershipProject':
        """Create a PartnershipProject to track this research."""
        from core.models_partnership import PartnershipProject

        # Generate project name from idea
        project_name = business_idea[:100]
        if len(business_idea) > 100:
            project_name = business_idea[:97] + "..."

        project = PartnershipProject.objects.create(
            user=self.user,
            project_name=project_name,
            project_type='research',
            description=f"Business research for: {business_idea}",
            status='planning',
            metadata={
                'source': 'research_orchestrator',
                'constraints': constraints,
                'created_via': 'autonomous_pipeline'
            }
        )

        return project

    def _update_project_with_research(self, result: FullResearchResult):
        """Update the project with completed research."""
        if not self.project:
            return

        try:
            # Update metadata with research results
            self.project.metadata = self.project.metadata or {}
            self.project.metadata['research_completed'] = True
            self.project.metadata['phases_completed'] = result.phases_completed
            self.project.metadata['business_plan'] = result.business_plan
            self.project.metadata['next_actions'] = result.next_actions
            self.project.metadata['research_time_ms'] = result.total_execution_time_ms

            # Update status
            self.project.status = 'in_progress'

            # Add AI contribution
            self.project.add_ai_contribution(
                agent_name='ResearchOrchestrator',
                task='Complete business research pipeline',
                time_saved_hours=2.0,  # Estimate: 2 hours of manual research
                output_summary=f"Completed {len(result.phases_completed)} research phases"
            )

            self.project.save()

        except Exception as e:
            logger.warning(f"Failed to update project with research: {e}")


# ==================== Convenience Function ====================

def get_research_orchestrator(user=None) -> ResearchOrchestrator:
    """Get a ResearchOrchestrator instance."""
    return ResearchOrchestrator(user=user)
