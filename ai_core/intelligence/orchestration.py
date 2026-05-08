"""
Multi-Agent Workflow Orchestration System

Coordinates complex workflows involving multiple agents working together
to solve sophisticated problems through collaborative intelligence.
"""

# PARTIAL — Session 1113 review (Session 1111 PR-E queue).
# Classification: built with defensive mock fallbacks; disconnected
# from real ML pipeline; no active runtime caller.
# Why: this module imports `from ml_pipeline.pipeline import MLPipeline`
# inside a `try/except ImportError` that falls back to a `MockMLPipeline`
# stub — and the real `ml_pipeline.pipeline` submodule does not exist
# (only `ml_pipeline.enhanced_ml_pipeline.EnhancedMLPipeline` is shipped),
# so this layer is permanently running on the no-op mock. The only
# importer in the entire repo is `archive/scripts/verify_llm_integration.py`,
# which itself lives under `archive/`. The active learning loop
# (`ai_core/intelligence/learning_loop.py`) goes to `EnhancedMLPipeline`,
# not through this orchestrator.
# Decision pending: revive by adding `MLPipeline = EnhancedMLPipeline` to
# `ml_pipeline/__init__.py` (one-line shim, would restore real-code
# behavior) OR mark dormant alongside `monitoring_dashboard.py` and
# `testing_suite.py`. Pair this call with the `ml_pipeline/__init__.py`
# decision — see PR-E in the deeper-review queue.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging

# Conditional imports to avoid Django dependency issues
try:
    from core.agents.registry import agent_registry
except ImportError:
    class MockAgentRegistry:
        def list_agents(self):
            return []
        def get_agent(self, name):
            return None
    agent_registry = MockAgentRegistry()

try:
    from advisors.registry import advisor_registry
except ImportError:
    class MockAdvisorRegistry:
        def list_advisors(self):
            return []
        def get_advisor(self, name):
            return None
    advisor_registry = MockAdvisorRegistry()

try:
    from ml_pipeline.pipeline import MLPipeline
except ImportError:
    class MockMLPipeline:
        def __init__(self):
            pass
        def process(self, data):
            return data
    MLPipeline = MockMLPipeline

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    AGENT = "agent"
    ADVISOR = "advisor"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    AGGREGATION = "aggregation"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: StepType = StepType.AGENT
    name: str = ""
    agent_ids: List[str] = field(default_factory=list)
    advisor_ids: List[str] = field(default_factory=list)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_key: str = ""
    condition: Optional[Callable] = None
    max_iterations: int = 1
    parallel_tasks: List['WorkflowStep'] = field(default_factory=list)
    aggregation_strategy: str = "merge"  # merge, vote, consensus, weighted
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowContext:
    """Maintains state throughout workflow execution"""
    workflow_id: str
    started_at: datetime
    current_step: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    ml_insights: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator:
    """Orchestrates multi-agent workflows"""

    def __init__(self):
        self.workflows = {}
        self.active_contexts = {}
        self.ml_pipeline = MLPipeline()
        self.workflow_templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[str, List[WorkflowStep]]:
        """Initialize common workflow templates"""
        return {
            "research_and_invest": [
                WorkflowStep(
                    type=StepType.PARALLEL,
                    name="gather_market_data",
                    parallel_tasks=[
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="analyze_stocks",
                            agent_ids=["stock_analyst", "market_scanner"],
                            output_key="stock_analysis"
                        ),
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="analyze_crypto",
                            agent_ids=["crypto_analyst", "defi_tracker"],
                            output_key="crypto_analysis"
                        ),
                        WorkflowStep(
                            type=StepType.ADVISOR,
                            name="get_expert_opinions",
                            advisor_ids=["warren_buffett", "cathie_wood"],
                            output_key="expert_opinions"
                        )
                    ]
                ),
                WorkflowStep(
                    type=StepType.AGGREGATION,
                    name="synthesize_insights",
                    input_mapping={
                        "stock_data": "stock_analysis",
                        "crypto_data": "crypto_analysis",
                        "expert_views": "expert_opinions"
                    },
                    aggregation_strategy="consensus",
                    output_key="market_insights"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="risk_assessment",
                    agent_ids=["risk_manager", "portfolio_optimizer"],
                    input_mapping={"insights": "market_insights"},
                    output_key="risk_profile"
                ),
                WorkflowStep(
                    type=StepType.CONDITIONAL,
                    name="investment_decision",
                    condition=lambda ctx: ctx.results.get("risk_profile", {}).get("score", 0) > 0.7,
                    agent_ids=["trade_executor"],
                    input_mapping={
                        "insights": "market_insights",
                        "risk": "risk_profile"
                    },
                    output_key="trade_execution"
                )
            ],

            "sports_betting_analysis": [
                WorkflowStep(
                    type=StepType.PARALLEL,
                    name="gather_game_data",
                    parallel_tasks=[
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="statistical_analysis",
                            agent_ids=["sports_statistician", "performance_analyzer"],
                            output_key="stats_analysis"
                        ),
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="odds_comparison",
                            agent_ids=["odds_compiler", "value_finder"],
                            output_key="odds_analysis"
                        ),
                        WorkflowStep(
                            type=StepType.ADVISOR,
                            name="expert_predictions",
                            advisor_ids=["sharp_bettor", "line_movement_expert"],
                            output_key="expert_picks"
                        )
                    ]
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="ml_prediction",
                    agent_ids=["ml_predictor"],
                    input_mapping={
                        "stats": "stats_analysis",
                        "odds": "odds_analysis"
                    },
                    output_key="ml_predictions"
                ),
                WorkflowStep(
                    type=StepType.AGGREGATION,
                    name="consensus_building",
                    input_mapping={
                        "stats": "stats_analysis",
                        "odds": "odds_analysis",
                        "expert": "expert_picks",
                        "ml": "ml_predictions"
                    },
                    aggregation_strategy="weighted",
                    output_key="betting_recommendation"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="kelly_criterion",
                    agent_ids=["kelly_calculator"],
                    input_mapping={"recommendation": "betting_recommendation"},
                    output_key="optimal_stake"
                )
            ],

            "ai_content_generation": [
                WorkflowStep(
                    type=StepType.AGENT,
                    name="topic_research",
                    agent_ids=["researcher", "trend_analyzer"],
                    output_key="research_data"
                ),
                WorkflowStep(
                    type=StepType.PARALLEL,
                    name="content_creation",
                    parallel_tasks=[
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="write_article",
                            agent_ids=["content_writer"],
                            input_mapping={"research": "research_data"},
                            output_key="article_draft"
                        ),
                        WorkflowStep(
                            type=StepType.AGENT,
                            name="create_visuals",
                            agent_ids=["image_generator", "chart_creator"],
                            input_mapping={"research": "research_data"},
                            output_key="visual_content"
                        )
                    ]
                ),
                WorkflowStep(
                    type=StepType.LOOP,
                    name="iterative_refinement",
                    max_iterations=3,
                    agent_ids=["editor", "fact_checker"],
                    input_mapping={
                        "content": "article_draft",
                        "visuals": "visual_content"
                    },
                    condition=lambda ctx: ctx.results.get("quality_score", 0) < 0.9,
                    output_key="refined_content"
                ),
                WorkflowStep(
                    type=StepType.AGENT,
                    name="seo_optimization",
                    agent_ids=["seo_optimizer"],
                    input_mapping={"content": "refined_content"},
                    output_key="final_content"
                )
            ]
        }

    async def create_workflow(
        self,
        name: str,
        steps: Optional[List[WorkflowStep]] = None,
        template: Optional[str] = None
    ) -> str:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())

        if template and template in self.workflow_templates:
            steps = self.workflow_templates[template]
        elif not steps:
            raise ValueError("Either steps or template must be provided")

        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": name,
            "steps": steps,
            "created_at": datetime.now(),
            "status": WorkflowStatus.PENDING
        }

        logger.info(f"Created workflow {workflow_id}: {name}")
        return workflow_id

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        context = WorkflowContext(
            workflow_id=workflow_id,
            started_at=datetime.now(),
            variables=initial_input or {}
        )

        self.active_contexts[workflow_id] = context
        workflow["status"] = WorkflowStatus.RUNNING

        try:
            for step in workflow["steps"]:
                await self._execute_step(step, context)

            workflow["status"] = WorkflowStatus.COMPLETED

            # Apply ML insights
            context.ml_insights = await self.ml_pipeline.analyze_workflow_performance(
                workflow_id=workflow_id,
                context=context
            )

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": context.results,
                "performance": context.performance_metrics,
                "ml_insights": context.ml_insights,
                "errors": context.errors
            }

        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            context.errors.append({
                "step": context.current_step,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise

        finally:
            del self.active_contexts[workflow_id]

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Execute a single workflow step"""
        context.current_step = step.id
        start_time = datetime.now()

        try:
            result = None

            if step.type == StepType.AGENT:
                result = await self._execute_agent_step(step, context)
            elif step.type == StepType.ADVISOR:
                result = await self._execute_advisor_step(step, context)
            elif step.type == StepType.PARALLEL:
                result = await self._execute_parallel_step(step, context)
            elif step.type == StepType.CONDITIONAL:
                result = await self._execute_conditional_step(step, context)
            elif step.type == StepType.LOOP:
                result = await self._execute_loop_step(step, context)
            elif step.type == StepType.AGGREGATION:
                result = await self._execute_aggregation_step(step, context)

            if step.output_key:
                context.results[step.output_key] = result

            # Track performance
            elapsed = (datetime.now() - start_time).total_seconds()
            context.performance_metrics[step.id] = {
                "name": step.name,
                "duration": elapsed,
                "success": True
            }

            return result

        except Exception as e:
            context.performance_metrics[step.id] = {
                "name": step.name,
                "duration": (datetime.now() - start_time).total_seconds(),
                "success": False,
                "error": str(e)
            }
            raise

    async def _execute_agent_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Execute agent-based step"""
        input_data = self._prepare_input(step, context)
        results = []

        for agent_id in step.agent_ids:
            agent = agent_registry.get_agent(agent_id)
            if agent:
                result = await agent.process(input_data)
                results.append(result)

        return results[0] if len(results) == 1 else results

    async def _execute_advisor_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Execute advisor consultation step"""
        input_data = self._prepare_input(step, context)
        advice = []

        for advisor_id in step.advisor_ids:
            advisor = advisor_registry.get_advisor(advisor_id)
            if advisor:
                result = await advisor.provide_advice(input_data)
                advice.append(result)

        return advice

    async def _execute_parallel_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute multiple steps in parallel"""
        tasks = []
        for sub_step in step.parallel_tasks:
            tasks.append(self._execute_step(sub_step, context))

        results = await asyncio.gather(*tasks)

        # Combine results
        combined = {}
        for sub_step, result in zip(step.parallel_tasks, results):
            if sub_step.output_key:
                combined[sub_step.output_key] = result

        return combined

    async def _execute_conditional_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Execute step conditionally"""
        if step.condition and step.condition(context):
            return await self._execute_agent_step(step, context)
        return None

    async def _execute_loop_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Execute step in a loop"""
        results = []
        for i in range(step.max_iterations):
            if step.condition and not step.condition(context):
                break

            result = await self._execute_agent_step(step, context)
            results.append(result)

            # Update context for next iteration
            if step.output_key:
                context.results[f"{step.output_key}_{i}"] = result

        return results

    async def _execute_aggregation_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Any:
        """Aggregate results from previous steps"""
        input_data = self._prepare_input(step, context)

        if step.aggregation_strategy == "merge":
            return self._merge_results(input_data)
        elif step.aggregation_strategy == "vote":
            return self._vote_aggregation(input_data)
        elif step.aggregation_strategy == "consensus":
            return await self._consensus_aggregation(input_data)
        elif step.aggregation_strategy == "weighted":
            return await self._weighted_aggregation(input_data)

        return input_data

    def _prepare_input(
        self,
        step: WorkflowStep,
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """Prepare input data for a step"""
        input_data = {}

        for key, source in step.input_mapping.items():
            if source in context.results:
                input_data[key] = context.results[source]
            elif source in context.variables:
                input_data[key] = context.variables[source]

        return input_data

    def _merge_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple merge of results"""
        merged = {}
        for key, value in data.items():
            if isinstance(value, dict):
                merged.update(value)
            else:
                merged[key] = value
        return merged

    def _vote_aggregation(self, data: Dict[str, Any]) -> Any:
        """Aggregate by voting"""
        votes = {}
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    votes[str(item)] = votes.get(str(item), 0) + 1

        if votes:
            return max(votes, key=votes.get)
        return data

    async def _consensus_aggregation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus from multiple sources"""
        # Use ML to find consensus
        consensus = await self.ml_pipeline.find_consensus(data)
        return {
            "consensus": consensus,
            "confidence": consensus.get("confidence", 0),
            "sources": data
        }

    async def _weighted_aggregation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Weighted aggregation based on historical performance"""
        weights = await self.ml_pipeline.get_source_weights(list(data.keys()))

        weighted_result = {}
        total_weight = sum(weights.values())

        for key, value in data.items():
            weight = weights.get(key, 1.0) / total_weight
            weighted_result[key] = {
                "value": value,
                "weight": weight
            }

        return weighted_result

    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow status"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}

        workflow = self.workflows[workflow_id]
        context = self.active_contexts.get(workflow_id)

        return {
            "id": workflow_id,
            "name": workflow["name"],
            "status": workflow["status"].value,
            "created_at": workflow["created_at"].isoformat(),
            "current_step": context.current_step if context else None,
            "results": context.results if context else {},
            "errors": context.errors if context else []
        }

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self.workflows:
            self.workflows[workflow_id]["status"] = WorkflowStatus.CANCELLED
            if workflow_id in self.active_contexts:
                del self.active_contexts[workflow_id]
            return True
        return False


# Global orchestrator instance
orchestrator = WorkflowOrchestrator()