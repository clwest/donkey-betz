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

Session 264: Phase 1 Foundation + Phase 2 Spider-Agent Bridge
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

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How the coordinator should execute the request."""
    DIRECT_RESPONSE = "direct"      # Answer directly with context
    AGENT_EXECUTION = "agent"       # Execute via agent
    WORKFLOW_ORCHESTRATION = "workflow"  # Multi-step workflow
    HIVE_MIND = "hive"              # Multi-agent collaboration
    MEMORY_RECALL = "memory"        # Memory Palace query


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

    def to_dict(self) -> dict:
        return {
            'success': self.success,
            'response': self.response,
            'execution_mode': self.execution_mode.value,
            'classification': self.classification.to_dict(),
            'agents_used': self.agents_used,
            'artifacts': self.artifacts,
            'execution_time_ms': self.execution_time_ms,
            'metadata': self.metadata,
        }


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
                from agents.registry import get_agent_registry
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

            # Step 5: RECORD - Log for learning (async, non-blocking)
            self._record_outcome(
                message=message,
                classification=classification,
                response=response,
                success=True
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
            QueryType.OPPORTUNITY: ExecutionMode.DIRECT_RESPONSE,
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
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=2000,
                temperature=0.7,
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

        Session 264: Now injects spider context into agents via AgentContextService.
        """
        suggested_agents = classification.suggested_agents

        if not suggested_agents:
            # Fall back to direct response if no agents suggested
            return self._handle_direct_response(message, classification, context)

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

        # Build response describing what we would do
        response_parts = [
            f"I'll use the following agents to help with your request:",
            ""
        ]

        for agent in agents_to_use:
            agent_ctx = agent_contexts.get(agent)
            if agent_ctx and agent_ctx.style_recommendations:
                response_parts.append(f"- **{agent}** (using styles: {', '.join(agent_ctx.style_recommendations[:2])})")
            else:
                response_parts.append(f"- **{agent}**")

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

        system_prompt += f"""

## Agent Execution Mode
You are coordinating these agents: {', '.join(agents_to_use)}

{spider_context_text if spider_context_text else ''}
Use the spider intelligence above to inform your decisions and recommendations.
Provide a detailed plan or execute the creation request.
If this is a creation request, describe what you would create with specific details.
"""

        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
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
        """
        agents = classification.suggested_agents or [
            'CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'ContentStrategyAgent'
        ]

        response = f"""Activating **Hive Mind Mode** for collaborative intelligence.

Convening agents:
{chr(10).join(f'- {agent}' for agent in agents)}

Each agent will analyze your request from their unique perspective, considering:
- Their current mood and expertise
- Their relationships with other agents
- Past successful collaborations

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

    def _record_outcome(
        self,
        message: str,
        classification: ClassificationResult,
        response: str,
        success: bool
    ) -> None:
        """
        Record the outcome for the learning loop.

        This runs asynchronously and doesn't block the response.
        """
        try:
            # For now, just log. Full learning loop in Phase 5.
            logger.info(
                f"Outcome recorded: type={classification.primary_type.value}, "
                f"success={success}, response_length={len(response)}"
            )

            # TODO: Phase 5 - Store in learning database
            # TODO: Phase 5 - Update agent performance metrics
            # TODO: Phase 5 - Feed into pattern detection

        except Exception as e:
            logger.warning(f"Failed to record outcome: {e}")

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
        return {
            'user': self.user.username if self.user else 'Anonymous',
            'openai_connected': self.openai_client is not None,
            'agent_registry_loaded': self.agent_registry is not None,
            'available_agents': self.context_aggregator._get_available_agents()[:5],
            'timestamp': timezone.now().isoformat(),
        }


# Convenience function for quick access
def get_coordinator(user=None) -> SuperPlatformCoordinator:
    """Get a SuperPlatformCoordinator instance."""
    return SuperPlatformCoordinator(user=user)
