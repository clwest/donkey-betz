"""
Super Platform Coordinator - The Unified Brain

This is the central orchestrator that unifies all platform components into
a single, coherent intelligence system. It replaces the fragmented dual-assistant
architecture with a unified entry point.

The Coordinator:
1. CLASSIFIES user input to understand intent
2. AGGREGATES relevant context from all sources
3. BUILDS dynamic prompts tailored to the request
4. ROUTES to the appropriate execution path
5. EXECUTES using agents, spiders, or direct response
6. RECORDS outcomes for learning

Session 264: Phase 1 Foundation + Phase 2 Spider-Agent Bridge + Phase 3 Sci-Fi Integration
Session 268: Phase 3 - Clean Agent Architecture Integration (USE_CLEAN_AGENT_ARCHITECTURE flag)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from django.utils import timezone
from django.conf import settings

from .query_classifier import QueryClassifier, QueryType, ClassificationResult
from .prompt_builder import DynamicPromptBuilder, PromptContext
from .context_aggregator import ContextAggregator, AggregatedContext
from .agent_context_service import get_agent_context_service
from .scifi_integration import get_scifi_integration_service
from .revenue_integration import get_revenue_integration_service
from .learning_loop import get_learning_loop_service  # Session 265 Phase 5

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How the coordinator should execute the request."""
    DIRECT_RESPONSE = "direct"      # Answer directly with context
    AGENT_EXECUTION = "agent"       # Execute via agent
    WORKFLOW_ORCHESTRATION = "workflow"  # Multi-step workflow
    HIVE_MIND = "hive"              # Multi-agent collaboration
    MEMORY_RECALL = "memory"        # Memory Palace query
    OPPORTUNITY = "opportunity"     # Revenue/opportunity handling (Phase 4)


@dataclass
class CoordinatorResult:
    """Result from the coordinator."""
    success: bool
    response: str
    execution_mode: ExecutionMode
    classification: ClassificationResult
    context_used: Dict[str, Any]
    agents_used: List[str] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    project_created: Optional[Dict[str, Any]] = None  # Session 519: Auto-project creation

    def to_dict(self) -> dict:
        result = {
            'success': self.success,
            'response': self.response,
            'execution_mode': self.execution_mode.value,
            'classification': self.classification.to_dict(),
            'agents_used': self.agents_used,
            'artifacts': self.artifacts,
            'execution_time_ms': self.execution_time_ms,
            'metadata': self.metadata,
        }
        # Session 519: Include project_created if present
        if self.project_created:
            result['project_created'] = self.project_created
        return result


class SuperPlatformCoordinator:
    """
    The brain of the Super Platform.

    This coordinator unifies all platform components into a single,
    coherent intelligence system. Every user interaction flows through
    here, and the coordinator determines the optimal path to fulfill
    the request.

    Architecture:
    ```
    User Input
        │
        ▼
    ┌─────────────────────────────────────────┐
    │         SUPER PLATFORM COORDINATOR       │
    │                                          │
    │  ┌──────────┐  ┌──────────┐  ┌────────┐ │
    │  │ Classify │→ │ Aggregate│→ │ Route  │ │
    │  └──────────┘  └──────────┘  └────────┘ │
    │                                    │     │
    │        ┌───────────────────────────┘     │
    │        ▼                                 │
    │  ┌─────────────────────────────────────┐ │
    │  │           EXECUTION LAYER           │ │
    │  │                                     │ │
    │  │  Direct │ Agent │ Workflow │ Hive  │ │
    │  └─────────────────────────────────────┘ │
    │                    │                     │
    │                    ▼                     │
    │  ┌─────────────────────────────────────┐ │
    │  │           LEARNING LOOP             │ │
    │  │  Record outcome → Update systems    │ │
    │  └─────────────────────────────────────┘ │
    └─────────────────────────────────────────┘
        │
        ▼
    Response + Artifacts
    ```
    """

    def __init__(self, user=None):
        """
        Initialize the Super Platform Coordinator.

        Args:
            user: Optional Django user for personalization
        """
        self.user = user
        self.classifier = QueryClassifier()
        self.prompt_builder = DynamicPromptBuilder()
        self.context_aggregator = ContextAggregator(user)

        # Lazy-loaded components
        self._openai_client = None
        self._agent_registry = None
        self._workflow_agent = None
        self._agent_context_service = None  # Session 264: Spider-Agent Bridge
        self._scifi_service = None  # Session 264: Sci-Fi Integration
        self._revenue_service = None  # Session 264: Revenue Pipeline
        self._learning_service = None  # Session 265: Learning Loop
        self._agent_router = None  # Session 268: Clean Agent Architecture
        self._personal_assistant = None  # Session 268: Clean Agent Architecture

    @property
    def openai_client(self):
        """Lazy load OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        return self._openai_client

    @property
    def agent_registry(self):
        """Lazy load agent registry."""
        if self._agent_registry is None:
            try:
                from core.agents.registry import get_agent_registry
                self._agent_registry = get_agent_registry()
            except Exception as e:
                logger.warning(f"Could not load agent registry: {e}")
        return self._agent_registry

    @property
    def agent_context_service(self):
        """Session 264: Lazy load agent context service for spider-agent bridge."""
        if self._agent_context_service is None:
            try:
                self._agent_context_service = get_agent_context_service()
            except Exception as e:
                logger.warning(f"Could not load agent context service: {e}")
        return self._agent_context_service

    @property
    def scifi_service(self):
        """Session 264: Lazy load sci-fi integration service."""
        if self._scifi_service is None:
            try:
                self._scifi_service = get_scifi_integration_service()
            except Exception as e:
                logger.warning(f"Could not load sci-fi service: {e}")
        return self._scifi_service

    @property
    def revenue_service(self):
        """Session 264 Phase 4: Lazy load revenue integration service."""
        if self._revenue_service is None:
            try:
                self._revenue_service = get_revenue_integration_service(self.user)
            except Exception as e:
                logger.warning(f"Could not load revenue service: {e}")
        return self._revenue_service

    @property
    def learning_service(self):
        """Session 265 Phase 5: Lazy load learning loop service."""
        if self._learning_service is None:
            try:
                self._learning_service = get_learning_loop_service(self.user)
            except Exception as e:
                logger.warning(f"Could not load learning service: {e}")
        return self._learning_service

    @property
    def agent_router(self):
        """Session 268: Lazy load AgentRouter for clean architecture."""
        if self._agent_router is None:
            try:
                from core.agent_router import AgentRouter
                self._agent_router = AgentRouter(user=self.user)
            except Exception as e:
                logger.warning(f"Could not load agent router: {e}")
        return self._agent_router

    @property
    def personal_assistant(self):
        """Session 268: Lazy load PersonalAssistantAgent for clean architecture."""
        if self._personal_assistant is None:
            try:
                from core.agents.personal_assistant_agent import PersonalAssistantAgent
                self._personal_assistant = PersonalAssistantAgent(user=self.user)
            except Exception as e:
                logger.warning(f"Could not load personal assistant: {e}")
        return self._personal_assistant

    @property
    def use_clean_architecture(self) -> bool:
        """Check if clean agent architecture is enabled."""
        return getattr(settings, 'USE_CLEAN_AGENT_ARCHITECTURE', False)

    def process(self, message: str, mode: str = 'interactive') -> CoordinatorResult:
        """
        Process a user message through the unified intelligence system.

        This is the main entry point for all user interactions.

        Args:
            message: The user's input message
            mode: Execution mode ('interactive', 'autonomous', 'hive')

        Returns:
            CoordinatorResult with response and metadata
        """
        start_time = datetime.now()

        # Session 268: Use clean agent architecture if enabled
        if self.use_clean_architecture:
            return self._process_with_clean_architecture(message, start_time)

        try:
            # Step 1: CLASSIFY - Understand what the user wants
            classification = self.classifier.classify(message)
            logger.info(
                f"Classified as {classification.primary_type.value} "
                f"(confidence: {classification.confidence:.2f})"
            )

            # Step 2: AGGREGATE - Gather relevant context
            context = self.context_aggregator.aggregate(classification, message)
            logger.info(f"Aggregated context from: {context.sources_used}")

            # Step 3: ROUTE - Determine execution path
            execution_mode = self._determine_execution_mode(classification)
            logger.info(f"Routing to: {execution_mode.value}")

            # Step 4: EXECUTE - Run the appropriate handler
            response, artifacts, agents_used = self._execute(
                message=message,
                classification=classification,
                context=context,
                execution_mode=execution_mode
            )

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Step 5: RECORD - Log for learning (Session 265 Phase 5)
            self._record_outcome(
                message=message,
                classification=classification,
                response=response,
                success=True,
                agents_used=agents_used,
                execution_time_ms=int(execution_time),
                execution_mode=execution_mode.value
            )

            return CoordinatorResult(
                success=True,
                response=response,
                execution_mode=execution_mode,
                classification=classification,
                context_used=context.to_dict(),
                agents_used=agents_used,
                artifacts=artifacts,
                execution_time_ms=execution_time,
                metadata={
                    'sources_used': context.sources_used,
                    'spider_data_used': bool(context.spider_data),
                    'memory_used': bool(context.memories),
                    'mood_influenced': bool(context.agent_mood),
                }
            )

        except Exception as e:
            logger.error(f"Coordinator error: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return CoordinatorResult(
                success=False,
                response=f"I encountered an error processing your request: {str(e)}",
                execution_mode=ExecutionMode.DIRECT_RESPONSE,
                classification=ClassificationResult(
                    primary_type=QueryType.CONVERSATION,
                    confidence=0.0,
                    secondary_types=[],
                    detected_keywords=[],
                    detected_entities={},
                    suggested_agents=[],
                    requires_spider_data=False,
                    requires_memory=False,
                    requires_mood_check=False,
                    is_urgent=False,
                ),
                context_used={},
                execution_time_ms=execution_time,
                metadata={'error': str(e)}
            )

    def _determine_execution_mode(self, classification: ClassificationResult) -> ExecutionMode:
        """Determine the optimal execution mode based on classification."""
        query_type = classification.primary_type

        mode_mapping = {
            QueryType.QUESTION: ExecutionMode.DIRECT_RESPONSE,
            QueryType.CREATION: ExecutionMode.AGENT_EXECUTION,
            QueryType.WORKFLOW: ExecutionMode.WORKFLOW_ORCHESTRATION,
            QueryType.ANALYSIS: ExecutionMode.AGENT_EXECUTION,
            QueryType.MEMORY: ExecutionMode.MEMORY_RECALL,
            QueryType.COLLABORATION: ExecutionMode.HIVE_MIND,
            QueryType.OPPORTUNITY: ExecutionMode.OPPORTUNITY,  # Session 264 Phase 4
            QueryType.SYSTEM: ExecutionMode.DIRECT_RESPONSE,
            QueryType.CONVERSATION: ExecutionMode.DIRECT_RESPONSE,
        }

        return mode_mapping.get(query_type, ExecutionMode.DIRECT_RESPONSE)

    def _execute(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext,
        execution_mode: ExecutionMode
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Execute the request using the appropriate handler.

        Returns:
            Tuple of (response_text, artifacts, agents_used)
        """
        handlers = {
            ExecutionMode.DIRECT_RESPONSE: self._handle_direct_response,
            ExecutionMode.AGENT_EXECUTION: self._handle_agent_execution,
            ExecutionMode.WORKFLOW_ORCHESTRATION: self._handle_workflow,
            ExecutionMode.HIVE_MIND: self._handle_hive_mind,
            ExecutionMode.MEMORY_RECALL: self._handle_memory_recall,
            ExecutionMode.OPPORTUNITY: self._handle_opportunity,  # Session 264 Phase 4
        }

        handler = handlers.get(execution_mode, self._handle_direct_response)
        return handler(message, classification, context)

    def _handle_direct_response(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle queries that need a direct response using GPT.

        This is the primary path for questions, system info, and conversation.
        """
        # Build the dynamic prompt
        prompt_context = PromptContext(
            classification=classification,
            spider_data=context.spider_data,
            memories=context.memories,
            agent_mood=context.agent_mood,
            user_preferences=context.user_preferences,
            available_agents=context.available_agents,
            intelligence_context=context.intelligence_context,  # Session 565
        )

        system_prompt = self.prompt_builder.build(prompt_context)

        # Call GPT
        if not self.openai_client:
            return (
                "I'm having trouble connecting to my AI core. Please try again.",
                [],
                []
            )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_completion_tokens=2000,
                reasoning_effort="medium",
            )

            response_text = response.choices[0].message.content
            return (response_text, [], [])

        except Exception as e:
            logger.error(f"GPT call failed: {e}")
            return (
                f"I encountered an error generating a response: {str(e)}",
                [],
                []
            )

    def _handle_agent_execution(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle requests that need agent execution (creation, analysis).

        Session 264: Now injects spider context and sci-fi context into agents.
        """
        suggested_agents = classification.suggested_agents

        if not suggested_agents:
            # Fall back to direct response if no agents suggested
            return self._handle_direct_response(message, classification, context)

        # Session 265 Phase 5: Use learning service for adaptive agent selection
        if self.learning_service:
            try:
                suggested_agents = self.learning_service.recommend_agents(
                    query_type=classification.primary_type.value,
                    default_agents=suggested_agents,
                    limit=3
                )
                logger.info(f"Learning-optimized agents: {suggested_agents}")
            except Exception as e:
                logger.debug(f"Could not get learning recommendations: {e}")

        agents_to_use = suggested_agents[:3]  # Limit to top 3

        # Session 264: Get spider context for each agent
        agent_contexts = {}
        if self.agent_context_service:
            for agent_name in agents_to_use:
                try:
                    agent_ctx = self.agent_context_service.get_context_for_agent(
                        agent_name=agent_name,
                        task=message,
                        user=self.user
                    )
                    agent_contexts[agent_name] = agent_ctx
                    logger.info(
                        f"Injected spider context for {agent_name}: "
                        f"{len(agent_ctx.trends)} trends, {len(agent_ctx.style_recommendations)} styles"
                    )
                except Exception as e:
                    logger.warning(f"Could not get spider context for {agent_name}: {e}")

        # Session 264 Phase 3: Get sci-fi context for each agent
        scifi_contexts = {}
        if self.scifi_service:
            for agent_name in agents_to_use:
                try:
                    scifi_ctx = self.scifi_service.get_scifi_context(
                        agent_name=agent_name,
                        task=message,
                        user=self.user
                    )
                    scifi_contexts[agent_name] = scifi_ctx
                    logger.info(
                        f"Injected sci-fi context for {agent_name}: "
                        f"mood={scifi_ctx.mood.mood_type if scifi_ctx.mood else 'none'}, "
                        f"level={scifi_ctx.evolution.level if scifi_ctx.evolution else 1}"
                    )
                except Exception as e:
                    logger.warning(f"Could not get sci-fi context for {agent_name}: {e}")

            # Calculate collaboration bonus for the team
            if len(agents_to_use) > 1:
                collab_bonus, collab_details = self.scifi_service.get_collaboration_bonus(agents_to_use)
                logger.info(f"Team collaboration bonus: {collab_bonus:.2f}x - {collab_details}")

        # Build response describing what we would do
        response_parts = [
            f"I'll use the following agents to help with your request:",
            ""
        ]

        for agent in agents_to_use:
            agent_ctx = agent_contexts.get(agent)
            scifi_ctx = scifi_contexts.get(agent)

            agent_info = f"- **{agent}**"

            # Add sci-fi personality info
            extras = []
            if scifi_ctx:
                if scifi_ctx.mood:
                    extras.append(f"mood: {scifi_ctx.mood.mood_type}")
                if scifi_ctx.evolution:
                    extras.append(f"level {scifi_ctx.evolution.level}")

            if agent_ctx and agent_ctx.style_recommendations:
                extras.append(f"styles: {', '.join(agent_ctx.style_recommendations[:2])}")

            if extras:
                agent_info += f" ({', '.join(extras)})"

            response_parts.append(agent_info)

        # Add spider context if available - from aggregated context or agent-specific
        trends_to_show = []
        if context.spider_data.get('trends'):
            trends_to_show = context.spider_data['trends'][:3]
        elif agent_contexts and agents_to_use:
            first_agent_ctx = agent_contexts.get(agents_to_use[0])
            if first_agent_ctx and first_agent_ctx.trends:
                trends_to_show = first_agent_ctx.trends[:3]

        if trends_to_show:
            response_parts.extend([
                "",
                "Current trending context I'll consider:",
            ])
            for trend in trends_to_show:
                title = trend.get('title', trend.get('topic', str(trend))) if isinstance(trend, dict) else str(trend)
                response_parts.append(f"- {title[:80]}")

        # For now, fall back to GPT response with agent context
        prompt_context = PromptContext(
            classification=classification,
            spider_data=context.spider_data,
            memories=context.memories,
            agent_mood=context.agent_mood,
            user_preferences=context.user_preferences,
            available_agents=context.available_agents,
            intelligence_context=context.intelligence_context,  # Session 565
        )

        system_prompt = self.prompt_builder.build(prompt_context)

        # Add agent execution context with spider intelligence
        spider_context_text = ""
        if agent_contexts:
            for agent_name, agent_ctx in agent_contexts.items():
                if agent_ctx.style_recommendations or agent_ctx.trends:
                    spider_context_text += f"\n### {agent_name} Spider Intelligence:\n"
                    if agent_ctx.style_recommendations:
                        spider_context_text += f"- Recommended styles: {', '.join(agent_ctx.style_recommendations[:3])}\n"
                    if agent_ctx.trends:
                        trend_names = [t.get('topic', str(t))[:30] for t in agent_ctx.trends[:3] if isinstance(t, dict)]
                        if trend_names:
                            spider_context_text += f"- Current trends: {', '.join(trend_names)}\n"

        # Session 264 Phase 3: Add sci-fi context to prompt
        scifi_context_text = ""
        if scifi_contexts:
            for agent_name, scifi_ctx in scifi_contexts.items():
                scifi_context_text += f"\n### {agent_name} Personality:\n"
                if scifi_ctx.mood:
                    scifi_context_text += f"- Mood: {scifi_ctx.mood.mood_type} - {scifi_ctx.mood.description}\n"
                    scifi_context_text += f"- Style tendency: {scifi_ctx.mood.style_modifier}\n"
                if scifi_ctx.evolution:
                    scifi_context_text += f"- Level: {scifi_ctx.evolution.level} ({scifi_ctx.evolution.title})\n"
                    if scifi_ctx.evolution.specializations:
                        scifi_context_text += f"- Specializations: {', '.join(scifi_ctx.evolution.specializations[:3])}\n"
                if scifi_ctx.relationships and scifi_ctx.relationships.allies:
                    scifi_context_text += f"- Works well with: {', '.join(scifi_ctx.relationships.allies[:3])}\n"

        system_prompt += f"""

## Agent Execution Mode
You are coordinating these agents: {', '.join(agents_to_use)}

{spider_context_text if spider_context_text else ''}
{scifi_context_text if scifi_context_text else ''}
Use the spider intelligence and agent personalities above to inform your decisions.
Let each agent's mood and experience level influence their recommendations.
Provide a detailed plan or execute the creation request.
If this is a creation request, describe what you would create with specific details.
"""

        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5.2",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_completion_tokens=2000,
                    reasoning_effort="medium",
                )
                response_text = response.choices[0].message.content
            else:
                response_text = "\n".join(response_parts)

            return (response_text, [], agents_to_use)

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return ("\n".join(response_parts), [], agents_to_use)

    def _handle_workflow(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle workflow orchestration requests.
        """
        # Identify the workflow type from the message
        workflow_keywords = {
            'brand': 'brand_identity_package',
            'thumbnail': 'youtube_thumbnail_package',
            'logo': 'research_and_create_logos',
            'product': 'product_photography_kit',
            'video thumbnail': 'video_thumbnail_series',
        }

        detected_workflow = None
        message_lower = message.lower()

        for keyword, workflow_name in workflow_keywords.items():
            if keyword in message_lower:
                detected_workflow = workflow_name
                break

        if detected_workflow:
            response = f"""I'll orchestrate the **{detected_workflow.replace('_', ' ').title()}** workflow for you.

This workflow will:
1. Research current trends and best practices
2. Generate multiple variations
3. Optimize for your target platform
4. Deliver a complete package

The WorkflowOrchestrationAgent is coordinating this multi-step process.

Would you like me to proceed? Please provide any specific requirements:
- Style preferences?
- Color scheme?
- Target audience?
- Platform (YouTube, Instagram, etc.)?"""
        else:
            response = """I can run these workflows for you:

- **research_and_create_logos** - Research + generate logos
- **youtube_thumbnail_package** - Research + thumbnails
- **brand_identity_package** - Complete brand kit
- **product_photography_kit** - Product photos
- **video_thumbnail_series** - Consistent thumbnail series

Which workflow would you like to run? Just describe what you need."""

        return (response, [], ['WorkflowOrchestrationAgent'])

    def _handle_hive_mind(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle Hive Mind collaboration requests.

        Session 264 Phase 3: Now includes actual sci-fi context for agents.
        """
        agents = classification.suggested_agents or [
            'CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'ContentStrategyAgent'
        ]

        # Session 264 Phase 3: Get actual sci-fi context for each agent
        agent_details = []
        collab_info = ""

        if self.scifi_service:
            for agent in agents:
                try:
                    scifi_ctx = self.scifi_service.get_scifi_context(agent, message, self.user)
                    mood = scifi_ctx.mood.mood_type if scifi_ctx.mood else "focused"
                    level = scifi_ctx.evolution.level if scifi_ctx.evolution else 1
                    title = scifi_ctx.evolution.title if scifi_ctx.evolution else "Agent"
                    agent_details.append(f"- **{agent}** ({title}, Level {level}, {mood})")
                except Exception:
                    agent_details.append(f"- **{agent}**")

            # Calculate team synergy
            collab_bonus, collab_details = self.scifi_service.get_collaboration_bonus(agents)
            synergies = collab_details.get('synergies', [])
            conflicts = collab_details.get('conflicts', [])

            if synergies:
                collab_info += f"\n**Team Synergies:** {', '.join(synergies[:3])}"
            if conflicts:
                collab_info += f"\n**Team Tensions:** {', '.join(conflicts[:2])}"
            collab_info += f"\n**Overall Team Bonus:** {collab_bonus:.1f}x"
        else:
            agent_details = [f"- {agent}" for agent in agents]

        response = f"""Activating **Hive Mind Mode** for collaborative intelligence.

Convening agents:
{chr(10).join(agent_details)}

Each agent will analyze your request from their unique perspective, considering:
- Their current mood and expertise
- Their relationships with other agents
- Past successful collaborations
{collab_info}

The collective will synthesize insights into a unified recommendation.

Processing: "{message[:100]}..."

*Hive Mind session initiated. Agents are deliberating...*"""

        return (response, [], agents)

    def _handle_memory_recall(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle Memory Palace recall requests.
        """
        memories = context.memories

        if memories:
            response_parts = ["Searching the Memory Palace...\n"]
            response_parts.append("I found these relevant memories:\n")

            for i, memory in enumerate(memories[:5], 1):
                content = memory.get('content', memory.get('summary', 'Memory record'))
                agent = memory.get('agent', 'System')
                created = memory.get('created_at', 'Unknown time')
                response_parts.append(f"{i}. **{agent}**: {content[:150]}...")
                response_parts.append(f"   _{created}_\n")

            response = "\n".join(response_parts)
        else:
            response = """I searched the Memory Palace but couldn't find relevant memories for your query.

This could mean:
- This is a new topic we haven't discussed before
- The memories may have been from a different context

Would you like to tell me more about what you're looking for?"""

        return (response, [], ['MemoryPalace'])

    def _handle_opportunity(
        self,
        message: str,
        classification: ClassificationResult,
        context: AggregatedContext
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Handle opportunity and revenue queries.

        Session 264 Phase 4: Revenue Pipeline integration.
        """
        if not self.revenue_service:
            return self._handle_direct_response(message, classification, context)

        try:
            message_lower = message.lower()

            # Determine what kind of opportunity query
            if any(kw in message_lower for kw in ['revenue', 'earnings', 'money', 'income']):
                # Revenue summary request
                summary = self.revenue_service.get_revenue_summary(days=30)
                response = self._format_revenue_summary(summary)
                return (response, [summary.to_dict()], ['RevenueIntegrationService'])

            elif any(kw in message_lower for kw in ['forecast', 'predict', 'projection']):
                # Revenue forecast
                forecast = self.revenue_service.get_revenue_forecast(days=30)
                response = self._format_revenue_forecast(forecast)
                return (response, [forecast], ['RevenueIntegrationService'])

            else:
                # Opportunity discovery (default)
                opportunities = self.revenue_service.discover_opportunities(
                    hours=48,
                    min_score=50,
                    limit=10
                )
                response = self._format_opportunities(opportunities)
                artifacts = [o.to_dict() for o in opportunities]
                return (response, artifacts, ['OpportunityScoringAgent', 'RevenueIntegrationService'])

        except Exception as e:
            logger.error(f"Error handling opportunity query: {e}")
            return self._handle_direct_response(message, classification, context)

    def _format_revenue_summary(self, summary) -> str:
        """Format revenue summary for display."""
        parts = [
            "## Revenue Summary (Last 30 Days)\n",
            f"**Total Revenue:** ${summary.total_revenue:.2f}",
            f"**Completed:** ${summary.completed_revenue:.2f}",
            f"**Pending:** ${summary.pending_revenue:.2f}",
            f"**Opportunities:** {summary.opportunity_count}",
            f"**Conversion Rate:** {summary.conversion_rate:.1f}%",
        ]

        if summary.top_sources:
            parts.append("\n**Top Revenue Sources:**")
            for source in summary.top_sources[:3]:
                parts.append(f"- {source.get('source_type', 'Unknown')}: ${source.get('total', 0):.2f}")

        if summary.top_agents:
            parts.append("\n**Top Contributing Agents:**")
            for agent in summary.top_agents[:3]:
                parts.append(f"- {agent.get('agent', 'Unknown')}: ${agent.get('total', 0):.2f}")

        return "\n".join(parts)

    def _format_revenue_forecast(self, forecast: Dict) -> str:
        """Format revenue forecast for display."""
        parts = [
            f"## Revenue Forecast ({forecast.get('forecast_period_days', 30)} Days)\n",
            f"**Predicted Revenue:** ${forecast.get('predicted_revenue', 0):.2f}",
            f"**High Confidence:** ${forecast.get('high_confidence_revenue', 0):.2f}",
            f"**Low Confidence:** ${forecast.get('low_confidence_revenue', 0):.2f}",
            "",
            f"**Active Opportunities:** {forecast.get('opportunity_count', 0)}",
            f"**High-Value Opportunities:** {forecast.get('high_value_opportunities', 0)}",
        ]

        historical = forecast.get('historical_comparison', {})
        if historical:
            parts.append(f"\n**Previous Period:** ${historical.get('previous_period', 0):.2f}")

        return "\n".join(parts)

    def _format_opportunities(self, opportunities) -> str:
        """Format opportunities list for display."""
        if not opportunities:
            return """No high-value opportunities found in the last 48 hours.

Try:
- Expanding your search criteria
- Checking back later as spiders collect more data
- Asking me to analyze a specific trend or topic"""

        parts = [
            f"## Top {len(opportunities)} Opportunities\n",
        ]

        for i, opp in enumerate(opportunities[:5], 1):
            # Status indicators
            indicators = []
            if opp.auto_apply_eligible:
                indicators.append("🚀 Auto-apply ready")
            if opp.overall_score >= 80:
                indicators.append("🔥 High value")
            if opp.time_sensitivity >= 80:
                indicators.append("⏰ Urgent")

            parts.append(f"### {i}. {opp.title[:60]}")
            parts.append(f"**Score:** {opp.overall_score}/100 | **Est. Revenue:** ${opp.potential_revenue}")
            if indicators:
                parts.append(" | ".join(indicators))

            if opp.suggested_actions:
                parts.append(f"**Actions:** {', '.join(opp.suggested_actions[:2])}")

            if opp.spider_insights.get('hot_skills_matched'):
                parts.append(f"**Hot Skills:** {', '.join(opp.spider_insights['hot_skills_matched'][:3])}")

            parts.append("")

        if len(opportunities) > 5:
            parts.append(f"*...and {len(opportunities) - 5} more opportunities*")

        return "\n".join(parts)

    def _record_outcome(
        self,
        message: str,
        classification: ClassificationResult,
        response: str,
        success: bool,
        agents_used: List[str] = None,
        execution_time_ms: int = 0,
        execution_mode: str = 'direct'
    ) -> None:
        """
        Record the outcome for the learning loop.

        Session 265 Phase 5: Full learning loop integration.
        """
        try:
            # Log for debugging
            logger.info(
                f"Outcome recorded: type={classification.primary_type.value}, "
                f"success={success}, response_length={len(response)}"
            )

            # Session 265: Record to learning loop service
            if self.learning_service:
                self.learning_service.record_outcome(
                    query_type=classification.primary_type.value,
                    query_text=message,
                    execution_mode=execution_mode,
                    agents_used=agents_used or [],
                    response=response,
                    execution_time_ms=execution_time_ms,
                    success=success,
                    classification_confidence=classification.confidence,
                    spider_data_used=classification.requires_spider_data,
                    scifi_context_used=classification.requires_mood_check,
                    metadata={
                        'secondary_types': [t.value for t in classification.secondary_types],
                        'detected_entities': classification.detected_entities,
                    }
                )

        except Exception as e:
            logger.warning(f"Failed to record outcome: {e}")

    def _process_with_clean_architecture(
        self,
        message: str,
        start_time: datetime
    ) -> CoordinatorResult:
        """
        Session 268: Process using the clean agent architecture.

        This uses the PersonalAssistantAgent as the entry point, which then
        routes to specialized agents via the AgentRouter.

        Architecture:
            User → PersonalAssistantAgent → AgentRouter → Specialized Agent → Tools
        """
        try:
            if not self.personal_assistant:
                logger.warning("PersonalAssistantAgent not available, falling back to legacy")
                return self._process_legacy(message, start_time)

            # Aggregate context for the agent
            classification = self.classifier.classify(message)
            context = self.context_aggregator.aggregate(classification, message)

            logger.info(
                f"[Clean Architecture] Processing: {message[:50]}... "
                f"(classified as {classification.primary_type.value})"
            )

            # Get spider context
            spider_context = {}
            if context.spider_data:
                spider_context = {
                    'relevant_trends': context.spider_data.get('trends', []),
                    'market_data': context.spider_data.get('market', {}),
                    'creative_trends': context.spider_data.get('creative', {}),
                }
                # Session 483: Debug logging
                logger.info(f"🕷️ [Session 483] Coordinator built spider_context with {len(spider_context.get('relevant_trends', []))} relevant_trends")
            else:
                logger.info(f"🕷️ [Session 483] Coordinator: context.spider_data is empty/None")

            # Get sci-fi context
            scifi_context = {}
            if self.scifi_service:
                try:
                    scifi_ctx = self.scifi_service.get_scifi_context(
                        agent_name='PersonalAssistantAgent',
                        task=message,
                        user=self.user
                    )
                    scifi_context = scifi_ctx.to_dict() if hasattr(scifi_ctx, 'to_dict') else {}
                except Exception as e:
                    logger.warning(f"Could not get sci-fi context: {e}")

            # Session 565: Get intelligence context for enriching PA responses
            intelligence_context = context.intelligence_context or {}
            if intelligence_context:
                logger.info(
                    f"🧠 [Session 565] Passing intelligence context to PA: "
                    f"{intelligence_context.get('metadata', {}).get('knowledge_count', 0)} knowledge, "
                    f"{intelligence_context.get('metadata', {}).get('experts_count', 0)} experts"
                )

            # Execute through PersonalAssistantAgent
            result = self.personal_assistant.execute(
                task=message,
                context={
                    'classification': classification.to_dict(),
                    'sources_used': context.sources_used,
                    'intelligence_context': intelligence_context,  # Session 565
                },
                scifi_context=scifi_context,
                spider_context=spider_context,
                intelligence_context=intelligence_context  # Session 565
            )

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Build the response
            agents_used = []
            artifacts = []
            project_created = None  # Session 519: Track auto-created projects

            if result.data:
                # Track which agent was used
                if result.data.get('delegated_to'):
                    agents_used.append(result.data['delegated_to'])

                # Session 271: Extract artifacts from agent_result
                agent_result = result.data.get('agent_result', {})

                # Handle images from ImageAgent
                # Session 272: ImageAgent returns image_url/image_id keys
                if agent_result.get('images'):
                    for img in agent_result['images']:
                        artifacts.append({
                            'type': 'image',
                            'url': img.get('image_url') or img.get('url'),
                            'id': img.get('image_id') or img.get('id'),
                            'prompt': img.get('prompt', '')
                        })

                # Handle videos from VideoAgent
                if agent_result.get('video_url') or agent_result.get('task_id'):
                    artifacts.append({
                        'type': 'video',
                        'url': agent_result.get('video_url'),
                        'id': agent_result.get('task_id'),
                        'status': agent_result.get('status', 'processing')
                    })

                # Handle audio from AudioAgent
                if agent_result.get('audio_url'):
                    artifacts.append({
                        'type': 'audio',
                        'url': agent_result.get('audio_url'),
                        'id': agent_result.get('audio_id')
                    })

                # Handle 3D from ThreeDAgent
                if agent_result.get('model_url'):
                    artifacts.append({
                        'type': '3d',
                        'url': agent_result.get('model_url'),
                        'format': agent_result.get('format', 'glb')
                    })

                # Handle research results from ResearchAgent
                if agent_result.get('results'):
                    artifacts.append({
                        'type': 'research',
                        'data': agent_result.get('results'),
                        'summary': agent_result.get('summary', '')
                    })

                # Session 496: Handle written content from ContentWriterAgent
                # ContentWriterAgent returns content/content_type inside agent_result
                if agent_result.get('content') and agent_result.get('content_type'):
                    content_data = agent_result.get('content', {})
                    full_text = content_data.get('full_text', '') if isinstance(content_data, dict) else str(content_data)
                    artifacts.append({
                        'type': 'written_content',
                        'content_type': agent_result.get('content_type'),
                        'data': content_data,
                        'full_text': full_text
                    })

                    # Session 519: Auto-create project from written content
                    if self.user and not project_created:
                        project_created = self._auto_create_project_from_content(
                            content_type=agent_result.get('content_type'),
                            content_data=content_data,
                            user_message=message
                        )

            # Session 271: Build a better response message
            response_message = result.message
            if not response_message and artifacts:
                artifact_types = [a['type'] for a in artifacts]
                response_message = f"Generated {len(artifacts)} artifact(s): {', '.join(set(artifact_types))}"
            elif not response_message:
                response_message = str(result.data) if result.data else "Request processed"

            # Session 401: Include knowledge attribution if available
            knowledge_attribution_data = None
            if result.knowledge_attribution:
                knowledge_attribution_data = result.knowledge_attribution.to_dict()

            # Session 565: Extract intelligence metadata for UI display
            intel_ctx = context.intelligence_context or {}
            intel_metadata = intel_ctx.get('metadata', {})
            intelligence_summary = None
            if intel_ctx and not intel_ctx.get('error'):
                total_sources = (
                    intel_metadata.get('knowledge_count', 0) +
                    intel_metadata.get('experts_count', 0) +
                    intel_metadata.get('dreams_count', 0) +
                    intel_metadata.get('policies_count', 0) +
                    intel_metadata.get('trends_count', 0)
                )
                if total_sources > 0:
                    intelligence_summary = {
                        'knowledge_count': intel_metadata.get('knowledge_count', 0),
                        'experts_count': intel_metadata.get('experts_count', 0),
                        'dreams_count': intel_metadata.get('dreams_count', 0),
                        'policies_count': intel_metadata.get('policies_count', 0),
                        'trends_count': intel_metadata.get('trends_count', 0),
                        'intent': intel_metadata.get('intent', 'unknown'),
                        'attribution': intel_ctx.get('attribution', ''),
                        'experts': [e.get('agent_name', '') for e in intel_ctx.get('experts', [])[:5]],
                        'spider_sources': intel_metadata.get('spider_sources', [])[:5],
                    }
                    logger.info(
                        f"🧠 [Session 565] Intelligence summary for response: "
                        f"{total_sources} total sources"
                    )

            return CoordinatorResult(
                success=result.success,
                response=response_message,
                execution_mode=ExecutionMode.AGENT_EXECUTION if agents_used else ExecutionMode.DIRECT_RESPONSE,
                classification=classification,
                context_used=context.to_dict(),
                agents_used=agents_used,
                artifacts=artifacts,
                execution_time_ms=execution_time,
                metadata={
                    'clean_architecture': True,
                    'decisions_made': result.decisions_made,
                    'tool_calls': result.tool_calls,
                    'agent_result': result.data.get('agent_result', {}) if result.data else {},
                    'knowledge_attribution': knowledge_attribution_data,  # Session 401
                    'intelligence_context': intelligence_summary,  # Session 565
                },
                project_created=project_created,  # Session 519: Auto-project creation
            )

        except Exception as e:
            logger.error(f"Clean architecture processing failed: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return CoordinatorResult(
                success=False,
                response=f"Error processing with clean architecture: {str(e)}",
                execution_mode=ExecutionMode.DIRECT_RESPONSE,
                classification=ClassificationResult(
                    primary_type=QueryType.CONVERSATION,
                    confidence=0.0,
                    secondary_types=[],
                    detected_keywords=[],
                    detected_entities={},
                    suggested_agents=[],
                    requires_spider_data=False,
                    requires_memory=False,
                    requires_mood_check=False,
                    is_urgent=False,
                ),
                context_used={},
                execution_time_ms=execution_time,
                metadata={'error': str(e), 'clean_architecture': True}
            )

    def _process_legacy(self, message: str, start_time: datetime) -> CoordinatorResult:
        """Fallback to legacy processing if clean architecture fails."""
        # This wraps the original process logic
        try:
            classification = self.classifier.classify(message)
            context = self.context_aggregator.aggregate(classification, message)
            execution_mode = self._determine_execution_mode(classification)
            response, artifacts, agents_used = self._execute(
                message=message,
                classification=classification,
                context=context,
                execution_mode=execution_mode
            )
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return CoordinatorResult(
                success=True,
                response=response,
                execution_mode=execution_mode,
                classification=classification,
                context_used=context.to_dict(),
                agents_used=agents_used,
                artifacts=artifacts,
                execution_time_ms=execution_time,
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return CoordinatorResult(
                success=False,
                response=f"Error: {str(e)}",
                execution_mode=ExecutionMode.DIRECT_RESPONSE,
                classification=ClassificationResult(
                    primary_type=QueryType.CONVERSATION,
                    confidence=0.0,
                    secondary_types=[],
                    detected_keywords=[],
                    detected_entities={},
                    suggested_agents=[],
                    requires_spider_data=False,
                    requires_memory=False,
                    requires_mood_check=False,
                    is_urgent=False,
                ),
                context_used={},
                execution_time_ms=execution_time,
            )

    def _auto_create_project_from_content(
        self,
        content_type: str,
        content_data: Dict[str, Any],
        user_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Session 519: Auto-create a PartnershipProject from generated content.

        When ContentWriterAgent generates content (blog posts, scripts, etc.),
        automatically organize it into a project for tracking and management.

        Args:
            content_type: Type of content (blog_post, podcast_script, etc.)
            content_data: The generated content data dict
            user_message: Original user message (for project naming)

        Returns:
            Dict with project_id, project_name, project_url if created, None otherwise
        """
        from core.models_partnership import PartnershipProject

        if not content_data:
            return None

        # Extract title from content
        project_name = content_data.get('title', '')[:100] if isinstance(content_data, dict) else ''

        # Fallback to extracting from message
        if not project_name:
            project_name = user_message[:100] if len(user_message) <= 100 else user_message[:97] + '...'

        # Map content type to project type
        project_type_map = {
            'blog_post': 'content_creation',
            'podcast_script': 'audio_production',
            'video_script': 'video_production',
            'article': 'content_creation',
            'newsletter': 'marketing',
            'social_thread': 'marketing'
        }
        project_type = project_type_map.get(content_type, 'content_creation')

        # Build description from content
        description = f"Auto-generated from assistant: {user_message[:200]}"
        if isinstance(content_data, dict):
            if content_data.get('meta_description'):
                description = content_data['meta_description']
            elif content_data.get('intro'):
                description = content_data['intro'][:500]

        # Build project metadata
        project_metadata = {
            'created_from': 'super_platform_coordinator',
            'original_message': user_message[:500],
            'created_at': datetime.now().isoformat(),
            'content_type': content_type,
            'written_content': [{
                'type': 'written_content',
                'content_type': content_type,
                'title': project_name,
                'data': content_data
            }]
        }

        try:
            project = PartnershipProject.objects.create(
                user=self.user,
                project_name=project_name,
                project_type=project_type,
                description=description[:1000],
                status='in_progress',
                ai_contribution_percent=95,
                human_contribution_percent=5,
                metadata=project_metadata,
                ai_contributions=[{
                    'agent': 'ContentWriterAgent',
                    'task': user_message[:200],
                    'timestamp': datetime.now().isoformat(),
                    'output': f'Generated {content_type}',
                }],
                workflow_steps=[{
                    'step': 'Content Generation',
                    'status': 'completed',
                    'description': f'Generated {content_type} via SuperPlatformCoordinator'
                }]
            )

            logger.info(f"📁 [Session 519] Created project '{project.project_name}' (ID: {project.id})")

            return {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'project_type': project_type,
                'project_url': f'/ai-studio/?tab=projects&project_id={project.id}'
            }

        except Exception as e:
            logger.error(f"❌ [Session 519] Failed to create project: {e}")
            return None

    # Convenience methods
    def ask(self, question: str) -> str:
        """Quick method for asking questions."""
        result = self.process(question)
        return result.response

    def create(self, prompt: str) -> CoordinatorResult:
        """Quick method for creation requests."""
        return self.process(f"Create {prompt}")

    def analyze(self, topic: str) -> CoordinatorResult:
        """Quick method for analysis requests."""
        return self.process(f"Analyze {topic}")

    def get_status(self) -> Dict[str, Any]:
        """Get current coordinator status."""
        # Session 271: Add clean architecture info
        clean_agents = []
        if self.use_clean_architecture and self.agent_router:
            for name, agent_class in self.agent_router.AGENT_MAP.items():
                # Session 642: Handle tools that might be a property
                tools = getattr(agent_class, 'tools', [])
                # If tools is a property, call it; if it's not a list/tuple, use empty list
                if isinstance(tools, property):
                    tools = []
                elif not isinstance(tools, (list, tuple)):
                    tools = []
                clean_agents.append({
                    'name': name,
                    'tool_count': len(tools),
                    'description': getattr(agent_class, 'system_prompt', '')[:100] + '...'
                })

        return {
            'user': self.user.username if self.user else 'Anonymous',
            'openai_connected': self.openai_client is not None,
            'agent_registry_loaded': self.agent_registry is not None,
            'available_agents': self.context_aggregator._get_available_agents()[:5],
            'timestamp': timezone.now().isoformat(),
            # Session 271: Clean architecture info
            'clean_architecture': {
                'enabled': self.use_clean_architecture,
                'agents': clean_agents,
                'total_agents': len(clean_agents),
            }
        }


# Convenience function for quick access
def get_coordinator(user=None) -> SuperPlatformCoordinator:
    """Get a SuperPlatformCoordinator instance."""
    return SuperPlatformCoordinator(user=user)
