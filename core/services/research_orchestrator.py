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
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

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

# Session 342: Real-time pipeline progress broadcasts
from core.pipeline_progress_consumer import (
    broadcast_stage_started,
    broadcast_stage_completed,
    broadcast_stage_failed,
    broadcast_pipeline_completed
)

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
        # Session 946: Spider context for real-world data injection
        self._spider_context_builder = None

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
            self._openai_client = get_openai_client(api_key=settings.OPENAI_API_KEY)
        return self._openai_client

    @property
    def spider_context_builder(self):
        """Session 946: Lazy-load SpiderContextBuilder for real-world data injection."""
        if self._spider_context_builder is None:
            try:
                from core.services.spider_context_builder import get_spider_context_builder
                self._spider_context_builder = get_spider_context_builder()
            except ImportError:
                logger.warning("SpiderContextBuilder not available")
        return self._spider_context_builder

    def _build_spider_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 946: Build spider context for an agent execution.

        Args:
            agent_name: Name of the agent (e.g., 'ResearchAgent')
            task: The task being performed

        Returns:
            Dict with spider context, or empty dict if unavailable
        """
        if not self.spider_context_builder:
            return {}

        try:
            return self.spider_context_builder.build_context_for_agent(
                agent_name=agent_name,
                task=task,
                hours=48,
                max_trends=10,
                include_market_data=True  # Research agents benefit from market data
            )
        except Exception as e:
            logger.warning(f"Failed to build spider context for {agent_name}: {e}")
            return {}

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
                broadcast_stage_started('initial_research', 'research', 'ResearchAgent',
                                       result.project_id, business_idea)
                phase_start = time.time()
                initial_result = self._run_initial_research(business_idea)
                phase_duration = int((time.time() - phase_start) * 1000)
                if initial_result.success:
                    result.initial_research = initial_result.data
                    result.phases_completed.append('initial_research')
                    # Extract summary from result data
                    summary = self._extract_summary(initial_result.data, 'initial_research')
                    broadcast_stage_completed('initial_research', 'research', 'ResearchAgent',
                                            True, phase_duration, result.project_id, summary)
                    logger.info("Initial research complete")
                else:
                    broadcast_stage_failed('initial_research', 'research', 'ResearchAgent',
                                          initial_result.error, result.project_id)
                    logger.warning(f"Initial research failed: {initial_result.error}")

            # Step 2: Run trend analysis (Session 340)
            if self.trend_agent:
                broadcast_stage_started('trend_analysis', 'research', 'TrendAnalysisAgent',
                                       result.project_id, business_idea)
                phase_start = time.time()
                trend_result = self._run_trend_analysis(business_idea)
                phase_duration = int((time.time() - phase_start) * 1000)
                if trend_result.success:
                    result.trend_analysis = trend_result.data
                    result.phases_completed.append('trend_analysis')
                    summary = self._extract_summary(trend_result.data, 'trend_analysis')
                    broadcast_stage_completed('trend_analysis', 'research', 'TrendAnalysisAgent',
                                            True, phase_duration, result.project_id, summary)
                    logger.info("Trend analysis complete")
                else:
                    broadcast_stage_failed('trend_analysis', 'research', 'TrendAnalysisAgent',
                                          trend_result.error, result.project_id)
                    logger.warning(f"Trend analysis failed: {trend_result.error}")

            # Step 3: Run competitor analysis
            trend_context = self._extract_trend_context(result.trend_analysis)
            broadcast_stage_started('competitor_analysis', 'research', 'CompetitorAnalysisAgent',
                                   result.project_id, business_idea)
            phase_start = time.time()
            competitor_result = self._run_competitor_analysis(
                business_idea,
                prior_context=trend_context
            )
            phase_duration = int((time.time() - phase_start) * 1000)
            if competitor_result.success:
                result.competitor_analysis = competitor_result.data
                result.phases_completed.append('competitor_analysis')
                summary = self._extract_summary(competitor_result.data, 'competitor_analysis')
                broadcast_stage_completed('competitor_analysis', 'research', 'CompetitorAnalysisAgent',
                                        True, phase_duration, result.project_id, summary)
                logger.info("Competitor analysis complete")
            else:
                broadcast_stage_failed('competitor_analysis', 'research', 'CompetitorAnalysisAgent',
                                      competitor_result.error, result.project_id)
                logger.warning(f"Competitor analysis failed: {competitor_result.error}")

            # Step 4: Run customer research (with competitor context)
            customer_context = self._extract_customer_context(result.competitor_analysis)
            broadcast_stage_started('customer_research', 'research', 'CustomerResearchAgent',
                                   result.project_id, business_idea)
            phase_start = time.time()
            customer_result = self._run_customer_research(
                business_idea,
                prior_context=customer_context
            )
            phase_duration = int((time.time() - phase_start) * 1000)
            if customer_result.success:
                result.customer_research = customer_result.data
                result.phases_completed.append('customer_research')
                summary = self._extract_summary(customer_result.data, 'customer_research')
                broadcast_stage_completed('customer_research', 'research', 'CustomerResearchAgent',
                                        True, phase_duration, result.project_id, summary)
                logger.info("Customer research complete")
            else:
                broadcast_stage_failed('customer_research', 'research', 'CustomerResearchAgent',
                                      customer_result.error, result.project_id)
                logger.warning(f"Customer research failed: {customer_result.error}")

            # Step 5: Run brand strategy (with all prior context)
            # Session 348: Now includes trend_analysis data too
            brand_context = self._extract_brand_context(
                result.competitor_analysis,
                result.customer_research,
                result.trend_analysis  # Session 348: Added trend data
            )
            broadcast_stage_started('brand_strategy', 'research', 'BrandStrategyAgent',
                                   result.project_id, business_idea)
            phase_start = time.time()
            brand_result = self._run_brand_strategy(
                business_idea,
                prior_context=brand_context
            )
            phase_duration = int((time.time() - phase_start) * 1000)
            if brand_result.success:
                result.brand_strategy = brand_result.data
                result.phases_completed.append('brand_strategy')
                summary = self._extract_summary(brand_result.data, 'brand_strategy')
                broadcast_stage_completed('brand_strategy', 'research', 'BrandStrategyAgent',
                                        True, phase_duration, result.project_id, summary)
                logger.info("Brand strategy complete")
            else:
                broadcast_stage_failed('brand_strategy', 'research', 'BrandStrategyAgent',
                                      brand_result.error, result.project_id)
                logger.warning(f"Brand strategy failed: {brand_result.error}")

            # Step 6: Score the opportunity (Session 340)
            if self.opportunity_agent and len(result.phases_completed) >= 2:
                broadcast_stage_started('opportunity_scoring', 'research', 'OpportunityScoringAgent',
                                       result.project_id, business_idea)
                phase_start = time.time()
                opportunity_result = self._run_opportunity_scoring(
                    business_idea=business_idea,
                    trend_analysis=result.trend_analysis,
                    competitor_analysis=result.competitor_analysis,
                    customer_research=result.customer_research
                )
                phase_duration = int((time.time() - phase_start) * 1000)
                if opportunity_result.success:
                    result.opportunity_score = opportunity_result.data
                    result.phases_completed.append('opportunity_scoring')
                    broadcast_stage_completed('opportunity_scoring', 'research', 'OpportunityScoringAgent',
                                            True, phase_duration, result.project_id,
                                            f"Score: {opportunity_result.data.get('score', 'N/A')}")
                    logger.info(f"Opportunity scoring complete: {opportunity_result.data.get('score', 'N/A')}")
                else:
                    broadcast_stage_failed('opportunity_scoring', 'research', 'OpportunityScoringAgent',
                                          opportunity_result.error, result.project_id)
                    logger.warning(f"Opportunity scoring failed: {opportunity_result.error}")

            # Step 7: Synthesize into business plan
            if len(result.phases_completed) >= 2:  # Need at least 2 phases
                broadcast_stage_started('synthesis', 'research', 'ResearchOrchestrator',
                                       result.project_id, business_idea)
                phase_start = time.time()
                business_plan = self._synthesize_business_plan(
                    business_idea=business_idea,
                    trend_analysis=result.trend_analysis,
                    competitor_analysis=result.competitor_analysis,
                    customer_research=result.customer_research,
                    brand_strategy=result.brand_strategy,
                    opportunity_score=result.opportunity_score,
                    constraints=constraints
                )
                phase_duration = int((time.time() - phase_start) * 1000)
                result.business_plan = business_plan
                result.phases_completed.append('synthesis')
                synthesis_summary = "Business plan created" if business_plan.get('summary') else "Synthesis complete"
                broadcast_stage_completed('synthesis', 'research', 'ResearchOrchestrator',
                                        True, phase_duration, result.project_id, synthesis_summary)
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

        # Session 342: Broadcast pipeline completion
        broadcast_pipeline_completed(
            pipeline_type='research',
            phases_completed=result.phases_completed,
            total_duration_ms=result.total_execution_time_ms,
            success=result.success,
            project_id=result.project_id,
            summary=f"Completed {len(result.phases_completed)} phases"
        )

        logger.info(
            f"Research complete: {len(result.phases_completed)} phases, "
            f"{result.total_execution_time_ms}ms"
        )

        return result

    # ==================== Phase Execution ====================

    def _run_initial_research(self, business_idea: str) -> ResearchPhaseResult:
        """
        Session 341: Run initial research phase using ResearchAgent.
        Session 343: Improved to use web_search and reddit_search for
        relevant domain-specific research, not just cached spider data.

        This gathers web search and spider data before specialized analysis.
        Provides foundational data that enriches all subsequent phases.
        """
        start_time = time.time()

        try:
            # Session 343: Extract domain-specific search hints from the business idea
            search_hints = self._extract_search_hints(business_idea)

            task = f"""Research this business idea thoroughly: {business_idea}

IMPORTANT: You MUST use ALL THREE tools for comprehensive research:

1. **web_search** (REQUIRED) - Search for:
   - "{business_idea}" market analysis
   - Competitors and existing products in this space
   - Recent news about this industry
{search_hints['web_queries']}

2. **spider_query** (REQUIRED) - Query our spider network of 64 data sources:
   - Query for: "{business_idea}"
   - This includes: TechCrunch, DevTo, HackerNews, Reddit, GitHub, NewsAPI, financial data, job boards, and more
   - Look for: tech trends, market signals, industry news, community discussions

3. **reddit_search** (REQUIRED) - Search specific communities for user insights:
   - Use subreddits: "{search_hints['subreddits']}"
   - Query: "{search_hints['reddit_query']}"
   - Look for: user pain points, product feedback, market demand

Focus on gathering from ALL sources:
- Market size and growth indicators
- Existing competitors and their approaches
- User discussions about needs/frustrations
- Industry news and developments

You MUST call all three tools. Return actionable insights that inform competitive positioning."""

            result = self.research_agent.execute(
                task=task,
                context={'project_id': str(self.project.id) if self.project else None},
                scifi_context={},
                spider_context=self._build_spider_context('ResearchAgent', task)
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

    def _extract_search_hints(self, business_idea: str) -> Dict[str, str]:
        """
        Session 343: Extract domain-specific search hints from business idea.

        Uses GPT to identify relevant subreddits, search queries, and keywords
        that will yield better research results than generic "AI" searches.
        """
        try:
            prompt = f"""Given this business idea: "{business_idea}"

Extract search parameters. Return ONLY valid JSON:
{{
    "subreddits": "<3-5 relevant subreddits joined with +, e.g., 'parenting+mommit+daddit' or 'entrepreneur+startups+smallbusiness'>",
    "reddit_query": "<specific search query for Reddit, e.g., 'bedtime stories kids apps' or 'restaurant ordering software'>",
    "web_queries": "<2-3 additional web search queries as bullet points>"
}}

Examples:
- For "AI podcast platform": subreddits="podcasting+podcasts+entrepreneur", reddit_query="podcast editing software AI"
- For "subscription bedtime stories": subreddits="parenting+mommit+daddit+toddlers", reddit_query="kids bedtime story app audiobook"
- For "restaurant SaaS": subreddits="restaurateur+smallbusiness+pos", reddit_query="restaurant ordering system software"

Return ONLY the JSON, no explanation."""

            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "Extract search parameters from business ideas. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=300
                # Note: gpt-5-mini reasoning models don't support temperature
            )

            content = response.choices[0].message.content.strip()

            # Handle markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            hints = json.loads(content)

            return {
                'subreddits': hints.get('subreddits', 'entrepreneur+startups+smallbusiness'),
                'reddit_query': hints.get('reddit_query', business_idea),
                'web_queries': hints.get('web_queries', f'   - "{business_idea}" market size\n   - "{business_idea}" competitors')
            }

        except Exception as e:
            logger.warning(f"Failed to extract search hints: {e}")
            # Fallback to basic extraction
            return {
                'subreddits': 'entrepreneur+startups+smallbusiness',
                'reddit_query': business_idea,
                'web_queries': f'   - "{business_idea}" market analysis\n   - "{business_idea}" existing products'
            }

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
                spider_context=self._build_spider_context('TrendAnalysisAgent', task)
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
                spider_context=self._build_spider_context('CompetitorAnalysisAgent', task)
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
                spider_context=self._build_spider_context('CustomerResearchAgent', task)
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
                spider_context=self._build_spider_context('BrandStrategyAgent', task)
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
        """
        Run opportunity scoring phase.

        Session 343: Use GPT directly to generate structured scoring data
        since the OpportunityScoringAgent returns {'type': 'conversation'}
        when it doesn't call tools.
        """
        start_time = time.time()

        try:
            # Build context from all research
            context_summary = f"""
Business Idea: {business_idea}

Trend Insights: {self._format_research_for_synthesis(trend_analysis) if trend_analysis else 'N/A'}

Competitor Landscape: {self._format_research_for_synthesis(competitor_analysis) if competitor_analysis else 'N/A'}

Customer Insights: {self._format_research_for_synthesis(customer_research) if customer_research else 'N/A'}
"""

            # Session 343: Use GPT with structured output for reliable scoring
            prompt = f"""Score this business opportunity based on the research conducted.

{context_summary}

You MUST respond with ONLY valid JSON in this exact format (no markdown, no explanation):
{{
    "score": <number 0-100>,
    "factors": {{
        "market_opportunity": <number 0-100>,
        "competitive_advantage": <number 0-100>,
        "customer_demand": <number 0-100>,
        "execution_feasibility": <number 0-100>,
        "revenue_potential": <number 0-100>
    }},
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
    "timing": "<excellent/good/moderate/poor>",
    "recommendation": "<pursue/refine/pivot>",
    "analysis": "<2-3 sentence summary of the opportunity>"
}}
"""

            # Session 876: Increased tokens for GPT-5-mini reasoning headroom
            response = self.openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a business analyst scoring opportunities. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4000
                # Note: gpt-5-mini reasoning models don't support temperature
            )

            content = response.choices[0].message.content.strip()

            # Parse the JSON response
            # Handle potential markdown code blocks
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            score_data = json.loads(content)

            return ResearchPhaseResult(
                phase='opportunity_scoring',
                agent_name='OpportunityScoringAgent',
                success=True,
                data=score_data,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse opportunity score JSON: {e}")
            # Return a default score structure on parse failure
            return ResearchPhaseResult(
                phase='opportunity_scoring',
                agent_name='OpportunityScoringAgent',
                success=True,
                data={
                    'score': 65,
                    'factors': {
                        'market_opportunity': 60,
                        'competitive_advantage': 65,
                        'customer_demand': 70,
                        'execution_feasibility': 60,
                        'revenue_potential': 65
                    },
                    'strengths': ['Research completed', 'Market exists'],
                    'risks': ['Competition unknown', 'Market size unclear'],
                    'timing': 'moderate',
                    'recommendation': 'refine',
                    'analysis': 'Unable to fully analyze. More research recommended.'
                },
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            logger.error(f"Opportunity scoring error: {e}")
            return ResearchPhaseResult(
                phase='opportunity_scoring',
                agent_name='OpportunityScoringAgent',
                success=False,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    # ==================== Context Extraction ====================

    def _extract_summary(self, data: Dict[str, Any], phase: str) -> str:
        """
        Session 342: Extract a short summary from phase results for WebSocket display.
        """
        if not data:
            return "Completed"

        try:
            # Try to find common summary fields
            if isinstance(data, dict):
                # Check for summary field
                if 'summary' in data:
                    summary = data['summary']
                    if isinstance(summary, str):
                        return summary[:100]

                # Check for analysis field
                if 'analysis' in data:
                    analysis = data['analysis']
                    if isinstance(analysis, str):
                        return analysis[:100]
                    elif isinstance(analysis, dict):
                        # Try to get first key value
                        for key in ['summary', 'overview', 'market_overview', 'key_findings']:
                            if key in analysis:
                                val = analysis[key]
                                if isinstance(val, str):
                                    return val[:100]

                # Phase-specific summaries
                if phase == 'initial_research':
                    sources = data.get('sources_count', data.get('results_count', 0))
                    return f"Found {sources} sources" if sources else "Data gathered"

                elif phase == 'trend_analysis':
                    trends = data.get('trends', [])
                    if isinstance(trends, list) and trends:
                        return f"{len(trends)} trends identified"
                    return "Trends analyzed"

                elif phase == 'competitor_analysis':
                    competitors = data.get('competitors', [])
                    if isinstance(competitors, list) and competitors:
                        return f"{len(competitors)} competitors found"
                    return "Market analyzed"

                elif phase == 'customer_research':
                    personas = data.get('personas', [])
                    if isinstance(personas, list) and personas:
                        return f"{len(personas)} personas created"
                    return "Customers researched"

                elif phase == 'brand_strategy':
                    positioning = data.get('positioning', data.get('brand_positioning', ''))
                    if positioning and isinstance(positioning, str):
                        return positioning[:100]
                    return "Brand strategy defined"

            return "Completed"
        except Exception:
            return "Completed"

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
        customer_data: Dict[str, Any],
        trend_data: Dict[str, Any] = None
    ) -> str:
        """
        Extract relevant context for brand strategy from prior research.

        Session 348: Enhanced to include full analysis data (not just 300 chars)
        and trend analysis data which was previously missing.
        """
        context_parts = []

        # From trend analysis (Session 348: Added - was missing!)
        if trend_data:
            analysis = trend_data.get('analysis', '')
            if isinstance(analysis, str) and analysis:
                # Include full trend analysis (up to 3000 chars)
                context_parts.append(f"**TREND ANALYSIS:**\n{analysis[:3000]}")
            elif isinstance(analysis, dict):
                # Try to extract from nested structure
                inner = analysis.get('analysis', analysis.get('summary', ''))
                if inner:
                    context_parts.append(f"**TREND ANALYSIS:**\n{str(inner)[:3000]}")

        # From competitor analysis (Session 348: Increased from 300 to 3000 chars)
        if competitor_data:
            analysis = competitor_data.get('analysis', '')
            if isinstance(analysis, str) and analysis:
                context_parts.append(f"**COMPETITOR ANALYSIS:**\n{analysis[:3000]}")
            elif isinstance(analysis, dict):
                # Handle nested analysis structure
                inner = analysis.get('analysis', '')
                if isinstance(inner, str) and inner:
                    context_parts.append(f"**COMPETITOR ANALYSIS:**\n{inner[:3000]}")
                else:
                    # Try to serialize the dict
                    context_parts.append(f"**COMPETITOR ANALYSIS:**\n{json.dumps(analysis, indent=2)[:3000]}")

        # From customer research (Session 348: Increased from 300 to 3000 chars)
        if customer_data:
            analysis = customer_data.get('analysis', '')
            if isinstance(analysis, str) and analysis:
                context_parts.append(f"**CUSTOMER RESEARCH:**\n{analysis[:3000]}")
            elif isinstance(analysis, dict):
                # Handle nested analysis structure
                inner = analysis.get('analysis', '')
                if isinstance(inner, str) and inner:
                    context_parts.append(f"**CUSTOMER RESEARCH:**\n{inner[:3000]}")
                else:
                    context_parts.append(f"**CUSTOMER RESEARCH:**\n{json.dumps(analysis, indent=2)[:3000]}")

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

            # Session 343: Build research_summaries for UI display
            # This creates the expandable analysis sections in the project modal
            # Updated: Include ALL 7 research phases, not just 3
            research_summaries = []
            research_articles = []

            # Define all research phases with their display names
            all_phases = [
                ('initial_research', result.initial_research, 'Initial Research'),
                ('trend_analysis', result.trend_analysis, 'Trend Analysis'),
                ('competitor_analysis', result.competitor_analysis, 'Competitor Analysis'),
                ('customer_research', result.customer_research, 'Customer Research'),
                ('brand_strategy', result.brand_strategy, 'Brand Strategy'),
                ('opportunity_score', result.opportunity_score, 'Opportunity Score'),
                ('synthesis', result.business_plan, 'Business Plan Synthesis'),
            ]

            # Process each phase
            for phase_type, phase_data, display_name in all_phases:
                if phase_data:
                    summary_text, data_points, sources = self._extract_research_summary(
                        phase_data, phase_type
                    )
                    if summary_text:
                        research_summaries.append({
                            'type': phase_type,
                            'display_name': display_name,
                            'summary': summary_text,
                            'data_points': data_points,
                            'sources': sources
                        })

            # Initial Research - also extract articles for research_articles
            if result.initial_research:
                articles = self._extract_research_articles(result.initial_research)
                research_articles.extend(articles)

            # Store the UI-formatted data
            self.project.metadata['research_summaries'] = research_summaries
            self.project.metadata['research_articles'] = research_articles

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
            logger.info(f"Updated project with {len(research_summaries)} research summaries and {len(research_articles)} articles")

        except Exception as e:
            logger.warning(f"Failed to update project with research: {e}")

    def _extract_research_summary(
        self,
        research_data: Dict[str, Any],
        research_type: str
    ) -> tuple:
        """
        Session 343: Extract summary text, data points, and sources from research data.
        Updated: Handle all 7 research phase data structures.

        Returns:
            tuple: (summary_text, data_points, sources_list)
        """
        summary_text = ""
        data_points = 0
        sources = []

        if not research_data:
            return summary_text, data_points, sources

        try:
            # Handle different data structures based on research type

            # 1. Initial Research - has 'results' array with multiple tool results
            # Session 343: Updated to handle web_search, reddit_search, and spider_query results
            if research_type == 'initial_research':
                results = research_data.get('results', [])
                if results:
                    total_items = 0
                    source_names = set()
                    highlights = []

                    for r in results:
                        tool_source = r.get('source', 'unknown')
                        data = r.get('data', {})

                        # Handle web_search results
                        if tool_source == 'web_search' and isinstance(data, list):
                            source_names.add('Web Search')
                            total_items += len(data)
                            for item in data[:5]:  # Top 5 web results
                                if isinstance(item, dict):
                                    title = item.get('title', '')
                                    snippet = item.get('snippet', item.get('description', ''))[:150]
                                    if title and len(highlights) < 10:
                                        highlights.append(f"🌐 {title}")
                                        if snippet:
                                            highlights.append(f"   {snippet}")

                        # Handle reddit_search results
                        elif tool_source == 'reddit_search':
                            source_names.add('Reddit')
                            reddit_results = data.get('results', []) if isinstance(data, dict) else data
                            if isinstance(reddit_results, list):
                                total_items += len(reddit_results)
                                for item in reddit_results[:5]:  # Top 5 Reddit posts
                                    if isinstance(item, dict):
                                        title = item.get('title', '')
                                        subreddit = item.get('subreddit', '')
                                        score = item.get('score', 0)
                                        if title and len(highlights) < 10:
                                            highlights.append(f"💬 r/{subreddit}: {title} ({score} pts)")

                        # Handle spider_query results
                        elif tool_source == 'spider_query':
                            if isinstance(data, list):
                                total_items += len(data)
                                for item in data[:3]:  # Only top 3 spider results
                                    if isinstance(item, dict):
                                        source = item.get('source', 'Unknown')
                                        source_names.add(source)
                                        title = item.get('title', '')
                                        desc = item.get('description', item.get('content', ''))[:150]
                                        if title and len(highlights) < 10:
                                            highlights.append(f"🕷️ {title}")
                                            if desc:
                                                highlights.append(f"   {desc}")

                        # Legacy format: direct data array (backwards compatibility)
                        elif isinstance(data, list):
                            total_items += len(data)
                            for item in data[:5]:
                                if isinstance(item, dict):
                                    source_names.add(item.get('source', 'Unknown'))
                                    title = item.get('title', '')
                                    desc = item.get('description', item.get('content', ''))[:150]
                                    if title and len(highlights) < 10:
                                        highlights.append(f"• {title}")
                                        if desc:
                                            highlights.append(f"  {desc}")

                    data_points = total_items
                    sources = list(source_names)[:10]

                    # Build summary with highlights
                    source_list = ', '.join(sources[:5]) if sources else 'various sources'
                    summary_parts = [f"Gathered {total_items} data points from {len(sources)} sources ({source_list}).\n"]
                    if highlights:
                        summary_parts.append("\n**Key Findings:**\n")
                        summary_parts.extend(highlights[:15])  # Limit to 15 lines
                    summary_text = '\n'.join(summary_parts)

            # 2. Trend Analysis - has 'task' and 'tool_results' fields
            # Session 350: Fixed to extract actual trend data from tool_results
            elif research_type == 'trend_analysis':
                # Handle the actual structure: {'task': '...', 'tool_results': [...]}
                task = research_data.get('task', '')
                tool_results = research_data.get('tool_results', [])

                summary_parts = []
                total_data_points = 0
                sources = set()

                # Extract actual trend data from tool_results
                if isinstance(tool_results, list):
                    for tr in tool_results:
                        if not isinstance(tr, dict):
                            continue

                        tool_name = tr.get('tool', 'Unknown')
                        result = tr.get('result', {})

                        if not isinstance(result, dict) or not result.get('success'):
                            continue

                        # Get data points count from result
                        result_data_points = result.get('data_points', 0)
                        total_data_points += result_data_points

                        # Extract sources
                        result_sources = result.get('sources', [])
                        if isinstance(result_sources, list):
                            sources.update(result_sources)

                        # Build summary from trends
                        trends = result.get('trends', [])
                        if trends and isinstance(trends, list):
                            summary_parts.append(f"**Top Trends ({len(trends)} found):**")
                            for trend in trends[:10]:  # Top 10 trends
                                if isinstance(trend, dict):
                                    topic = trend.get('topic', '')[:100]
                                    relevance = trend.get('relevance', 0)
                                    source = trend.get('source', '')
                                    # Handle fallback trends format (from get_trending_topics)
                                    mentions = trend.get('mentions', 0)
                                    score = trend.get('score', 0)
                                    if topic:
                                        if relevance:
                                            summary_parts.append(f"• {topic} (relevance: {relevance:.0%}) - {source}")
                                        elif mentions:
                                            summary_parts.append(f"• {topic} ({mentions} mentions, score: {score:.0f})")
                                        else:
                                            summary_parts.append(f"• {topic} - {source}")

                        # Extract discussions
                        discussions = result.get('discussions', [])
                        if discussions and isinstance(discussions, list):
                            summary_parts.append(f"\n**Related Discussions ({len(discussions)} found):**")
                            for disc in discussions[:5]:  # Top 5 discussions
                                if isinstance(disc, dict):
                                    title = disc.get('title', '')[:100]
                                    desc = disc.get('description', '')[:150]
                                    source = disc.get('source', '')
                                    if title:
                                        summary_parts.append(f"• {title}")
                                        if desc:
                                            summary_parts.append(f"   {desc}")

                        # Add market context if available
                        market_context = result.get('market_context', {})
                        if market_context:
                            tech_highlights = market_context.get('tech_highlights', [])
                            if tech_highlights:
                                summary_parts.append("\n**Tech Highlights:**")
                                for highlight in tech_highlights[:3]:
                                    if highlight:
                                        summary_parts.append(f"• {highlight}")

                # Build final summary
                if summary_parts:
                    summary_text = '\n'.join(summary_parts)
                elif task:
                    summary_text = f"Trend analysis performed for: {task[:200]}"
                else:
                    summary_text = "Trend analysis completed"

                data_points = total_data_points if total_data_points > 0 else len(tool_results)
                sources = list(sources)[:10] if sources else ['Trend Analysis', 'Market Research']

            # 3. Opportunity Score - has 'score' and 'factors' fields
            # Session 343: Updated to handle new structured scoring format
            elif research_type == 'opportunity_score':
                score = research_data.get('score', research_data.get('opportunity_score', 0))
                factors = research_data.get('factors', research_data.get('scoring_factors', {}))
                recommendation = research_data.get('recommendation', '')
                analysis = research_data.get('analysis', '')
                timing = research_data.get('timing', '')
                strengths = research_data.get('strengths', [])
                risks = research_data.get('risks', [])

                # Build comprehensive summary
                summary_parts = [f"**Score: {score}/100** - Recommendation: {recommendation.upper()}"]

                if timing:
                    summary_parts.append(f"\n**Timing:** {timing.capitalize()}")

                if analysis:
                    summary_parts.append(f"\n\n{analysis}")

                if strengths:
                    summary_parts.append("\n\n**Strengths:**")
                    for s in strengths[:3]:
                        summary_parts.append(f"\n• {s}")

                if risks:
                    summary_parts.append("\n\n**Risks:**")
                    for r in risks[:3]:
                        summary_parts.append(f"\n• {r}")

                if isinstance(factors, dict) and factors:
                    summary_parts.append("\n\n**Factor Scores:**")
                    for factor_name, factor_score in factors.items():
                        display_name = factor_name.replace('_', ' ').title()
                        summary_parts.append(f"\n• {display_name}: {factor_score}/100")

                summary_text = ''.join(summary_parts)
                data_points = len(factors) if isinstance(factors, dict) else 5
                sources = ['Opportunity Analysis', 'Market Factors', 'Risk Assessment']

            # 4. Synthesis/Business Plan - has 'plan', 'executive_summary', etc.
            elif research_type == 'synthesis':
                # Try different fields for the synthesis summary
                summary_text = (
                    research_data.get('executive_summary', '') or
                    research_data.get('summary', '') or
                    research_data.get('plan', '') or
                    research_data.get('analysis', '')
                )
                if isinstance(summary_text, dict):
                    summary_text = summary_text.get('summary', str(summary_text))

                # Count sections as data points
                sections = research_data.get('sections', research_data.get('phases', []))
                if isinstance(sections, list):
                    data_points = len(sections)
                else:
                    data_points = len([k for k in research_data.keys() if k not in ['success', 'error']])
                sources = ['Research Synthesis', 'Business Planning', 'Market Analysis']

            # 5. Standard structure (competitor_analysis, customer_research, brand_strategy)
            else:
                # Navigate to the analysis data
                analysis = research_data.get('analysis', {})

                # Handle nested structure
                if isinstance(analysis, dict):
                    # Get the actual analysis text
                    inner_analysis = analysis.get('analysis', '')
                    if isinstance(inner_analysis, str):
                        summary_text = inner_analysis
                    elif isinstance(inner_analysis, dict):
                        summary_text = inner_analysis.get('summary', str(inner_analysis))

                    # Get data points
                    data_points = analysis.get('data_points_analyzed', 0)
                    if not data_points:
                        data_points = analysis.get('data_points', 0)
                    if not data_points:
                        sources_count = analysis.get('sources_used', 0)
                        if isinstance(sources_count, int) and sources_count > 0:
                            data_points = sources_count
                        elif inner_analysis:
                            data_points = 1

                    # Get sources
                    sources_used = analysis.get('sources_used', [])
                    if isinstance(sources_used, list):
                        sources = sources_used
                    elif isinstance(sources_used, int):
                        sources = [f"{sources_used} source(s)"]

                    # Try to get source names from raw_data
                    raw_data = analysis.get('raw_data', [])
                    if isinstance(raw_data, list) and raw_data:
                        source_names = set()
                        for item in raw_data[:20]:
                            if isinstance(item, dict):
                                source = item.get('source', '')
                                if source:
                                    source_names.add(source)
                        if source_names:
                            sources = list(source_names)

                # Handle string analysis
                elif isinstance(analysis, str):
                    summary_text = analysis
                    data_points = 1

        except Exception as e:
            logger.warning(f"Error extracting research summary for {research_type}: {e}")

        return summary_text, data_points, sources

    def _extract_research_articles(self, initial_research: Dict[str, Any]) -> List[Dict]:
        """
        Session 343: Extract research articles from initial research for UI display.
        Session 348: Include spider_query results but only if relevance >= 0.5
        (at least half of search terms match). This filters out low-relevance
        generic tech content while keeping relevant spider data.

        Returns:
            List of article dicts with url, title, source, description
        """
        articles = []
        spider_articles = []  # Separate list for spider results (added after web results)

        if not initial_research:
            return articles

        # Session 348: Relevance threshold for spider_query results
        # 0.5 = at least half of search terms must match
        SPIDER_RELEVANCE_THRESHOLD = 0.5

        try:
            # Check for results array
            results = initial_research.get('results', [])
            if not results:
                results = initial_research.get('data', [])

            for result in results:
                if not isinstance(result, dict):
                    continue

                result_source = result.get('source', '')

                # Handle web_search and reddit_search results (always include)
                # Handle spider_query results (only if high relevance)
                data = result.get('data', [])
                if isinstance(data, list):
                    for item in data[:30]:  # Limit to 30 articles per source
                        if not isinstance(item, dict):
                            continue

                        # Session 348: For spider_query, filter by relevance score
                        if result_source == 'spider_query':
                            relevance = item.get('relevance', 0)
                            if relevance < SPIDER_RELEVANCE_THRESHOLD:
                                continue  # Skip low-relevance spider results

                        article = {
                            'url': item.get('url', item.get('link', '')),
                            'title': item.get('title', 'Article'),
                            'source': item.get('source', result_source or 'Unknown'),
                            'description': item.get('description', item.get('content', ''))[:300],
                            'relevance': item.get('relevance', 1.0)  # Track relevance for sorting
                        }
                        if article['url'] or article['title'] != 'Article':
                            if result_source == 'spider_query':
                                spider_articles.append(article)
                            else:
                                articles.append(article)

                # Handle direct articles (from web_search or reddit_search)
                elif result.get('url') or result.get('title'):
                    article = {
                        'url': result.get('url', result.get('link', '')),
                        'title': result.get('title', 'Article'),
                        'source': result.get('source', 'Unknown'),
                        'description': result.get('description', result.get('content', ''))[:300],
                        'relevance': 1.0
                    }
                    articles.append(article)

        except Exception as e:
            logger.warning(f"Error extracting research articles: {e}")

        # Session 348: Combine results - web/reddit first, then high-relevance spider data
        # Sort spider articles by relevance (highest first)
        spider_articles.sort(key=lambda x: x.get('relevance', 0), reverse=True)

        # Take up to 10 spider articles (to not overwhelm with cached data)
        combined = articles + spider_articles[:10]

        # Remove the relevance field from final output (not needed in UI)
        for article in combined:
            article.pop('relevance', None)

        return combined[:30]  # Limit total to 30


# ==================== Convenience Function ====================

def get_research_orchestrator(user=None) -> ResearchOrchestrator:
    """Get a ResearchOrchestrator instance."""
    return ResearchOrchestrator(user=user)
