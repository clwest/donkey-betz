"""
Research Orchestrator - The Brain of the Autonomous Business Pipeline
======================================================================

Session 338: End-to-End Autonomous Business Idea Pipeline
Session 340: Added TrendAnalysisAgent and OpportunityScoringAgent
Session 341: Added ResearchAgent for initial web/spider data gathering

This orchestrator chains research agents together to create a complete
business intelligence package from a raw business idea.

Flow:
    User: "I have a business idea for an AI podcast"
        ↓
    ResearchOrchestrator.execute_full_research()
        ↓
    1. ResearchAgent → Initial web/spider data gathering (NEW - Session 341)
        ↓ (passes context)
    2. TrendAnalysisAgent → Current market trends and patterns
        ↓ (passes context)
    3. CompetitorAnalysisAgent → Market landscape, competitors, SWOT
        ↓ (passes context)
    4. CustomerResearchAgent → Personas, pain points, opportunities
        ↓ (passes context)
    5. BrandStrategyAgent → Positioning, messaging, visual direction
        ↓
    6. OpportunityScoringAgent → Score the opportunity (0-100)
        ↓
    7. Synthesis → Complete business plan with recommendations
        ↓
    Return: BusinessPlan with all research + actionable next steps + opportunity score

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
    initial_research: Dict[str, Any] = field(default_factory=dict)  # Session 341
    trend_analysis: Dict[str, Any] = field(default_factory=dict)
    competitor_analysis: Dict[str, Any] = field(default_factory=dict)
    customer_research: Dict[str, Any] = field(default_factory=dict)
    brand_strategy: Dict[str, Any] = field(default_factory=dict)
    opportunity_score: Dict[str, Any] = field(default_factory=dict)
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
            'initial_research': self.initial_research,  # Session 341
            'trend_analysis': self.trend_analysis,
            'competitor_analysis': self.competitor_analysis,
            'customer_research': self.customer_research,
            'brand_strategy': self.brand_strategy,
            'opportunity_score': self.opportunity_score,
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
        # Research agents
        self._research_agent = None  # Session 341: General research agent
        self._trend_agent = None
        self._competitor_agent = None
        self._customer_agent = None
        self._brand_agent = None
        self._opportunity_agent = None
        self._openai_client = None

    # ==================== Lazy-Loaded Agents ====================

    @property
    def research_agent(self):
        """Lazy-load ResearchAgent for web/spider search."""
        if self._research_agent is None:
            try:
                from core.agents import ResearchAgent
                self._research_agent = ResearchAgent(user=self.user)
            except ImportError:
                logger.warning("ResearchAgent not available")
        return self._research_agent

    @property
    def trend_agent(self):
        """Lazy-load TrendAnalysisAgent."""
        if self._trend_agent is None:
            try:
                from core.agents.analysis import TrendAnalysisAgent
                self._trend_agent = TrendAnalysisAgent(user=self.user)
            except ImportError:
                logger.warning("TrendAnalysisAgent not available")
        return self._trend_agent

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
    def opportunity_agent(self):
        """Lazy-load OpportunityScoringAgent."""
        if self._opportunity_agent is None:
            try:
                from core.agents.analysis import OpportunityScoringAgent
                self._opportunity_agent = OpportunityScoringAgent(user=self.user)
            except ImportError:
                logger.warning("OpportunityScoringAgent not available")
        return self._opportunity_agent

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

            # Step 1.5: Run initial research (Session 341)
            # ResearchAgent gathers web/spider data before specialized analysis
            if self.research_agent:
                initial_result = self._run_initial_research(business_idea)
                if initial_result.success:
                    result.initial_research = initial_result.data
                    result.phases_completed.append('initial_research')
                    logger.info("Initial research complete")
                else:
                    logger.warning(f"Initial research failed: {initial_result.error}")

            # Step 2: Run trend analysis (Session 340)
            if self.trend_agent:
                trend_result = self._run_trend_analysis(business_idea)
                if trend_result.success:
                    result.trend_analysis = trend_result.data
                    result.phases_completed.append('trend_analysis')
                    logger.info("Trend analysis complete")
                else:
                    logger.warning(f"Trend analysis failed: {trend_result.error}")

            # Step 3: Run competitor analysis
            trend_context = self._extract_trend_context(result.trend_analysis)
            competitor_result = self._run_competitor_analysis(
                business_idea,
                prior_context=trend_context
            )
            if competitor_result.success:
                result.competitor_analysis = competitor_result.data
                result.phases_completed.append('competitor_analysis')
                logger.info("Competitor analysis complete")
            else:
                logger.warning(f"Competitor analysis failed: {competitor_result.error}")

            # Step 4: Run customer research (with competitor context)
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

            # Step 5: Run brand strategy (with all prior context)
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

            # Step 6: Score the opportunity (Session 340)
            if self.opportunity_agent and len(result.phases_completed) >= 2:
                opportunity_result = self._run_opportunity_scoring(
                    business_idea=business_idea,
                    trend_analysis=result.trend_analysis,
                    competitor_analysis=result.competitor_analysis,
                    customer_research=result.customer_research
                )
                if opportunity_result.success:
                    result.opportunity_score = opportunity_result.data
                    result.phases_completed.append('opportunity_scoring')
                    logger.info(f"Opportunity scoring complete: {opportunity_result.data.get('score', 'N/A')}")
                else:
                    logger.warning(f"Opportunity scoring failed: {opportunity_result.error}")

            # Step 7: Synthesize into business plan
            if len(result.phases_completed) >= 2:  # Need at least 2 phases
                business_plan = self._synthesize_business_plan(
                    business_idea=business_idea,
                    trend_analysis=result.trend_analysis,
                    competitor_analysis=result.competitor_analysis,
                    customer_research=result.customer_research,
                    brand_strategy=result.brand_strategy,
                    opportunity_score=result.opportunity_score,
                    constraints=constraints
                )
                result.business_plan = business_plan
                result.phases_completed.append('synthesis')
                logger.info("Business plan synthesis complete")

            # Step 8: Generate next actions
            result.next_actions = self._generate_next_actions(
                business_plan=result.business_plan,
                opportunity_score=result.opportunity_score,
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

    def _run_initial_research(self, business_idea: str) -> ResearchPhaseResult:
        """
        Session 341: Run initial research phase using ResearchAgent.

        This gathers web search and spider data before specialized analysis.
        Provides foundational data that enriches all subsequent phases.
        """
        start_time = time.time()

        try:
            task = f"""Research this business idea thoroughly: {business_idea}

Use your web search and spider network tools to gather:
1. Current market information and industry landscape
2. Recent news and developments in this space
3. Existing solutions and products
4. Community discussions (Reddit, forums)
5. Relevant data from tech, jobs, and creative sources

Compile a comprehensive summary of findings that will inform:
- Trend analysis
- Competitor identification
- Customer research
- Brand positioning

Be thorough but focused on actionable insights."""

            result = self.research_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='initial_research',
                agent_name='ResearchAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='initial_research',
                agent_name='ResearchAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_trend_analysis(self, business_idea: str) -> ResearchPhaseResult:
        """Run trend analysis phase using TrendAnalysisAgent."""
        start_time = time.time()

        try:
            # Detect industry/sector from business idea
            task = f"""Analyze current market trends relevant to this business idea: {business_idea}

Focus on:
- What are the hot trends in this space?
- What technologies are gaining traction?
- What are consumers/businesses looking for?
- Any timing considerations (seasonal, economic, etc.)?
"""

            result = self.trend_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='trend_analysis',
                agent_name='TrendAnalysisAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='trend_analysis',
                agent_name='TrendAnalysisAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _run_competitor_analysis(
        self,
        business_idea: str,
        prior_context: str = ""
    ) -> ResearchPhaseResult:
        """Run competitor analysis phase."""
        start_time = time.time()

        try:
            task = f"Analyze competitors for: {business_idea}"
            if prior_context:
                task += f"\n\nContext from trend analysis:\n{prior_context}"

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

    def _run_opportunity_scoring(
        self,
        business_idea: str,
        trend_analysis: Dict[str, Any],
        competitor_analysis: Dict[str, Any],
        customer_research: Dict[str, Any]
    ) -> ResearchPhaseResult:
        """Run opportunity scoring phase using OpportunityScoringAgent."""
        start_time = time.time()

        try:
            # Build context from all research
            context_summary = f"""
Business Idea: {business_idea}

Trend Insights: {self._format_research_for_synthesis(trend_analysis) if trend_analysis else 'N/A'}

Competitor Landscape: {self._format_research_for_synthesis(competitor_analysis) if competitor_analysis else 'N/A'}

Customer Insights: {self._format_research_for_synthesis(customer_research) if customer_research else 'N/A'}
"""

            task = f"""Score this business opportunity based on the research conducted.

{context_summary}

Provide:
1. Overall opportunity score (0-100)
2. Key strengths
3. Key risks
4. Market timing assessment
5. Recommendation (pursue/refine/pivot)
"""

            result = self.opportunity_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context={}
            )

            return ResearchPhaseResult(
                phase='opportunity_scoring',
                agent_name='OpportunityScoringAgent',
                success=result.success,
                data=result.data if result.success else {},
                error=result.error,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            return ResearchPhaseResult(
                phase='opportunity_scoring',
                agent_name='OpportunityScoringAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Context Extraction ====================

    def _extract_trend_context(self, trend_data: Dict[str, Any]) -> str:
        """Extract relevant context from trend analysis for competitor research."""
        if not trend_data:
            return ""

        analysis = trend_data.get('analysis', '')
        if isinstance(analysis, str):
            return analysis[:500]

        # Extract key points
        context_parts = []
        if isinstance(analysis, dict):
            if 'trends' in analysis:
                trends = analysis['trends']
                if isinstance(trends, list):
                    trend_names = [t.get('name', '') for t in trends[:5] if t.get('name')]
                    if trend_names:
                        context_parts.append(f"Key trends: {', '.join(trend_names)}")

            if 'timing' in analysis:
                context_parts.append(f"Timing factors: {analysis['timing'][:200]}")

        return "\n".join(context_parts) if context_parts else str(trend_data)[:500]

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
        trend_analysis: Dict[str, Any],
        competitor_analysis: Dict[str, Any],
        customer_research: Dict[str, Any],
        brand_strategy: Dict[str, Any],
        opportunity_score: Dict[str, Any],
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

MARKET TRENDS:
{self._format_research_for_synthesis(trend_analysis) if trend_analysis else "Not available"}

COMPETITOR ANALYSIS:
{self._format_research_for_synthesis(competitor_analysis)}

CUSTOMER RESEARCH:
{self._format_research_for_synthesis(customer_research)}

BRAND STRATEGY:
{self._format_research_for_synthesis(brand_strategy)}

OPPORTUNITY SCORE:
{self._format_research_for_synthesis(opportunity_score) if opportunity_score else "Not available"}

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
        opportunity_score: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate specific next actions based on the business plan and opportunity score."""
        actions = []

        # Check opportunity score for recommendation-based actions
        score = 0
        recommendation = ""
        if opportunity_score:
            score_data = opportunity_score.get('analysis', opportunity_score)
            if isinstance(score_data, dict):
                score = score_data.get('score', 0)
                recommendation = score_data.get('recommendation', '')
            elif isinstance(score_data, str):
                # Try to extract score from text
                if 'score' in score_data.lower():
                    recommendation = score_data

        # High score actions (80+)
        if score >= 80:
            actions.append("PRIORITY: Move fast - this is a strong opportunity")
            actions.append("Create logo and brand assets immediately")
            actions.append("Set up landing page to capture early interest")
        # Medium score actions (50-79)
        elif score >= 50:
            actions.append("Review the business plan and validate key assumptions")
            actions.append("Create logo and brand assets using the brand strategy")
            actions.append("Set up landing page to test market interest")
        # Low score actions (<50)
        else:
            actions.append("Review opportunity score risks before proceeding")
            actions.append("Consider pivoting based on research insights")
            actions.append("Conduct additional customer discovery to validate assumptions")

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
            self.project.metadata['initial_research'] = result.initial_research  # Session 341
            self.project.metadata['trend_analysis'] = result.trend_analysis
            self.project.metadata['competitor_analysis'] = result.competitor_analysis
            self.project.metadata['customer_research'] = result.customer_research
            self.project.metadata['brand_strategy'] = result.brand_strategy
            self.project.metadata['opportunity_score'] = result.opportunity_score
            self.project.metadata['business_plan'] = result.business_plan
            self.project.metadata['next_actions'] = result.next_actions
            self.project.metadata['research_time_ms'] = result.total_execution_time_ms

            # Update status
            self.project.status = 'in_progress'

            # Calculate time saved based on phases
            time_saved = 2.0 + (len(result.phases_completed) * 0.5)

            # Add AI contribution
            self.project.add_ai_contribution(
                agent_name='ResearchOrchestrator',
                task='Complete business research pipeline',
                time_saved_hours=time_saved,
                output_summary=f"Completed {len(result.phases_completed)} research phases"
            )

            self.project.save()

        except Exception as e:
            logger.warning(f"Failed to update project with research: {e}")


# ==================== Convenience Function ====================

def get_research_orchestrator(user=None) -> ResearchOrchestrator:
    """Get a ResearchOrchestrator instance."""
    return ResearchOrchestrator(user=user)
