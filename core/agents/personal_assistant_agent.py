"""
Personal Assistant Agent - The Traffic Cop
===========================================

Session 268: Phase 3 - Super Platform Integration
Session 293: Added business research agents + semantic routing

This agent is the main entry point for user requests in the clean architecture.
It receives messages, classifies intent, and delegates to specialized agents.

Unlike WorkflowAgent (which orchestrates multi-step workflows), this agent
handles the TOP-LEVEL routing decision:
- Is this a question? → Answer directly
- Is this a creation request? → Route to appropriate creation agent
- Is this a multi-step workflow? → Route to WorkflowAgent
- Is this an editing request? → Route to appropriate editing agent

Architecture:
    User → PersonalAssistantAgent → AgentRouter → Specialized Agent → Tools

Routing Strategy (Session 293):
    1. Semantic Routing (embeddings) - uses cosine similarity to match query to agents
    2. Keyword Fallback - if semantic confidence is low
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from core.agents.base_agent import BaseAgent, AgentResult, KnowledgeAttribution
from core.agents.routing_config import get_intent_keywords, AGENT_ROUTING_CONFIG

logger = logging.getLogger(__name__)

# Session 454: Import keywords from unified routing config
INTENT_KEYWORDS = get_intent_keywords()

# Session 454: Improved semantic routing with retry logic
_semantic_router = None
_semantic_router_last_attempt = None
_semantic_router_failure_count = 0
SEMANTIC_ROUTER_RETRY_INTERVAL = 300  # 5 minutes between retries
SEMANTIC_ROUTER_MAX_FAILURES = 3  # Give up after 3 consecutive failures

# Session 454: Routing analytics tracking
_routing_analytics = {
    'total_routes': 0,
    'routes_by_agent': {},
    'routes_by_method': {'semantic': 0, 'keyword': 0, 'workflow': 0, 'business_context': 0, 'gpt': 0},
    'question_vs_action': {'question': 0, 'action': 0},
    'recent_routes': [],  # Last 100 routing decisions
}
ROUTING_ANALYTICS_MAX_RECENT = 100


def record_routing_decision(
    task: str,
    selected_agent: str,
    method: str,
    confidence: float,
    is_question: bool,
    alternatives: list = None
):
    """
    Session 454: Record routing decision for analytics.

    Args:
        task: The user's task (truncated)
        selected_agent: Which agent was selected
        method: How the decision was made (semantic, keyword, workflow, etc.)
        confidence: Confidence score of the decision
        is_question: Whether this was classified as a question
        alternatives: Other agents that were considered
    """
    global _routing_analytics

    _routing_analytics['total_routes'] += 1

    # Track by agent
    if selected_agent not in _routing_analytics['routes_by_agent']:
        _routing_analytics['routes_by_agent'][selected_agent] = 0
    _routing_analytics['routes_by_agent'][selected_agent] += 1

    # Track by method
    if method in _routing_analytics['routes_by_method']:
        _routing_analytics['routes_by_method'][method] += 1

    # Track question vs action
    _routing_analytics['question_vs_action']['question' if is_question else 'action'] += 1

    # Store recent decision (circular buffer)
    decision = {
        'timestamp': time.time(),
        'task_preview': task[:100] if task else '',
        'agent': selected_agent,
        'method': method,
        'confidence': confidence,
        'is_question': is_question,
        'alternatives': alternatives[:3] if alternatives else [],
    }
    _routing_analytics['recent_routes'].append(decision)
    if len(_routing_analytics['recent_routes']) > ROUTING_ANALYTICS_MAX_RECENT:
        _routing_analytics['recent_routes'].pop(0)

    # Log for debugging
    logger.info(
        f"ROUTING: '{task[:50]}...' -> {selected_agent} "
        f"(method={method}, confidence={confidence:.2f}, is_question={is_question})"
    )


def get_routing_analytics() -> dict:
    """
    Session 454: Get current routing analytics.

    Returns:
        Dict with routing statistics
    """
    global _routing_analytics

    # Calculate percentages
    total = _routing_analytics['total_routes']
    if total == 0:
        return _routing_analytics

    analytics = _routing_analytics.copy()
    analytics['agent_percentages'] = {
        agent: (count / total * 100)
        for agent, count in _routing_analytics['routes_by_agent'].items()
    }
    analytics['method_percentages'] = {
        method: (count / total * 100)
        for method, count in _routing_analytics['routes_by_method'].items()
    }

    return analytics


def get_semantic_router():
    """
    Lazy-load the semantic routing service with retry logic.

    Session 454: Fixed silent failure by:
    1. Adding retry mechanism with exponential backoff
    2. Logging detailed failure reasons
    3. Allowing recovery from transient failures
    """
    global _semantic_router, _semantic_router_last_attempt, _semantic_router_failure_count

    # Already initialized successfully
    if _semantic_router is not None and _semantic_router is not False:
        return _semantic_router

    # Check if we should retry after previous failure
    if _semantic_router is False:
        if _semantic_router_failure_count >= SEMANTIC_ROUTER_MAX_FAILURES:
            # Too many failures, don't retry forever
            return None

        # Check if enough time has passed for retry
        if _semantic_router_last_attempt:
            elapsed = (time.time() - _semantic_router_last_attempt)
            # Exponential backoff: 5min, 10min, 20min
            retry_interval = SEMANTIC_ROUTER_RETRY_INTERVAL * (2 ** (_semantic_router_failure_count - 1))
            if elapsed < retry_interval:
                return None  # Not time to retry yet

        # Reset for retry
        _semantic_router = None
        logger.info(f"Retrying semantic routing initialization (attempt {_semantic_router_failure_count + 1})")

    # Attempt initialization
    if _semantic_router is None:
        _semantic_router_last_attempt = time.time()
        try:
            from core.services.semantic_routing import SemanticRoutingService
            router = SemanticRoutingService()

            if router.initialize():
                _semantic_router = router
                _semantic_router_failure_count = 0  # Reset on success
                logger.info("Semantic routing service initialized successfully")
            else:
                raise Exception("SemanticRoutingService.initialize() returned False")

        except ImportError as e:
            _semantic_router = False
            _semantic_router_failure_count += 1
            logger.error(f"Semantic routing import failed: {e}")

        except Exception as e:
            _semantic_router = False
            _semantic_router_failure_count += 1
            logger.warning(
                f"Semantic routing initialization failed (attempt {_semantic_router_failure_count}): {e}. "
                f"Will retry in {SEMANTIC_ROUTER_RETRY_INTERVAL * (2 ** (_semantic_router_failure_count - 1))}s"
            )

    return _semantic_router if _semantic_router and _semantic_router is not False else None


# Intent-to-Agent Mapping
INTENT_AGENT_MAP = {
    # Creation intents → Creation agents
    'create_image': 'ImageAgent',
    'create_logo': 'ImageAgent',
    'create_banner': 'ImageAgent',
    'create_illustration': 'ImageAgent',
    'generate_image': 'ImageAgent',

    'create_video': 'VideoAgent',
    'generate_video': 'VideoAgent',
    'animate': 'VideoAgent',
    'animate_image': 'VideoAgent',

    'create_audio': 'AudioAgent',
    'generate_voice': 'AudioAgent',
    'text_to_speech': 'AudioAgent',
    'voiceover': 'AudioAgent',

    'create_3d': 'ThreeDAgent',
    'convert_to_3d': 'ThreeDAgent',
    '3d_model': 'ThreeDAgent',

    # Editing intents → Editing agents
    'upscale': 'ImageEditingAgent',
    'remove_background': 'ImageEditingAgent',
    'edit_image': 'ImageEditingAgent',
    'recolor': 'ImageEditingAgent',
    'variations': 'ImageEditingAgent',

    'trim_video': 'VideoEditingAgent',
    'edit_video': 'VideoEditingAgent',
    'add_text_to_video': 'VideoEditingAgent',
    'video_effects': 'VideoEditingAgent',

    # Research intents → Research agent (for general searches)
    'search': 'ResearchAgent',
    'find': 'ResearchAgent',
    'trending': 'ResearchAgent',
    'analyze_trends': 'ResearchAgent',

    # Business Research intents → Business Research agents (Session 293)
    'market_research': 'CompetitorAnalysisAgent',
    'competitor_analysis': 'CompetitorAnalysisAgent',
    'swot_analysis': 'CompetitorAnalysisAgent',
    'business_research': 'CompetitorAnalysisAgent',
    'startup_research': 'CompetitorAnalysisAgent',
    'customer_research': 'CustomerResearchAgent',
    'customer_personas': 'CustomerResearchAgent',
    'pain_points': 'CustomerResearchAgent',

    # Legal intents → Legal agent (Session 403)
    'legal_question': 'LegalDocDrafterAgent',
    'legal_document': 'LegalDocDrafterAgent',
    'draft_motion': 'LegalDocDrafterAgent',
    'divorce_help': 'LegalDocDrafterAgent',
    'custody_help': 'LegalDocDrafterAgent',
    'court_procedure': 'LegalDocDrafterAgent',

    # Multi-step intents → Workflow agent
    'research_and_create': 'WorkflowAgent',
    'brand_package': 'WorkflowAgent',
    'thumbnail_package': 'WorkflowAgent',
    'workflow': 'WorkflowAgent',
}

# Session 454: INTENT_KEYWORDS now imported from routing_config.py (single source of truth)
# See: core/agents/routing_config.py for the unified agent routing configuration

# Session 414: UI Navigation guidance for platform features
# Maps keywords to helpful navigation instructions
UI_NAVIGATION_GUIDE = {
    # Spider data and data collection
    'spider': {
        'keywords': ['spider', 'spiders', 'crawl', 'crawling', 'data collection', 'web scraping'],
        'guidance': """**Spider Network Access:**
- Click the **🕷️ Intelligence** tab in the left sidebar
- Use the **Data Feed** sub-tab to see all collected data
- Use the **Knowledge** sub-tab to see what agents have learned
- Use the **Timeline** sub-tab to see recent spider activity
- Spiders run automatically every hour via Celery tasks"""
    },
    # Agent conversations
    'conversations': {
        'keywords': ['conversations', 'agent chat', 'agents talking', 'agent discussions', 'what are agents saying', 'agent dialogue'],
        'guidance': """**Agent Conversations Access:**
- Click the **🤖 Social** tab in the left sidebar
- The **Conversations** sub-tab shows real-time agent-to-agent discussions
- Agents automatically converse every 2 hours about creative topics
- You can see what they're learning from each other!"""
    },
    # Agent dreams
    'dreams': {
        'keywords': ['dreams', 'agent dreams', 'dreaming', 'what agents dream', 'creative dreams'],
        'guidance': """**Agent Dreams Access:**
- Click the **🤖 Social** tab in the left sidebar
- Use the **Dreams** sub-tab to see agent creative dreams
- Dreams are generated when agents are idle (every 4 hours)
- Dreams reveal unique insights and creative ideas from each agent"""
    },
    # Boardroom/decisions
    'boardroom': {
        'keywords': ['boardroom', 'decisions', 'board meeting', 'agent decisions', 'policy', 'policies', 'canonical'],
        'guidance': """**Boardroom & Decisions Access:**
- Click the **📊 Decisions** tab in the left sidebar
- **Pending Decisions** shows proposals awaiting your review
- **Active Policies** shows decisions you've approved
- **History** shows past decisions and outcomes
- Agents can propose policies based on their learnings!"""
    },
    # Evolution/growth
    'evolution': {
        'keywords': ['evolution', 'agent levels', 'xp', 'experience', 'agent growth', 'leveling'],
        'guidance': """**Agent Evolution Access:**
- Click the **📈 Growth** tab in the left sidebar
- See agent levels, XP, and progression
- Agents level up by completing tasks and learning
- Higher-level agents have enhanced capabilities"""
    },
    # Hive mind
    'hivemind': {
        'keywords': ['hive mind', 'collective', 'collective intelligence', 'shared learning', 'knowledge sharing'],
        'guidance': """**Collective Intelligence Access:**
- Click the **🧠 Hive Mind** tab in the left sidebar
- See shared knowledge across all agents
- Watch real-time knowledge transfer between agents
- View the knowledge graph of agent learnings"""
    },
}


class PersonalAssistantAgent(BaseAgent):
    """
    The main entry point agent that routes requests to specialized agents.

    This agent:
    1. Analyzes the user's message to understand intent
    2. Determines if it's a question (answer directly) or action request (delegate)
    3. Routes to the appropriate specialized agent via AgentRouter
    4. Synthesizes and returns the response

    It is the "traffic cop" of the clean architecture.
    """

    name = "PersonalAssistantAgent"

    system_prompt = """You are the Personal Assistant, the main interface for the AI Studio.

Your job is to understand what the user wants and route their request appropriately.

For QUESTIONS (what is, how does, explain, tell me about):
- Answer directly using your knowledge and any provided context

For CREATION requests (create, make, generate, design):
- Identify what type of content they want
- Delegate to the appropriate agent using delegate_to_agent

For EDITING requests (upscale, remove background, trim, edit):
- Identify the editing operation needed
- Delegate to the appropriate editing agent

For RESEARCH requests (search, find, trending, analyze):
- For general trending/news: use ResearchAgent
- For BUSINESS/MARKET/STARTUP research: use CompetitorAnalysisAgent (SWOT, competitors)
- For CUSTOMER research: use CustomerResearchAgent (personas, pain points)

For LEGAL requests (divorce, custody, court, motion):
- Delegate to LegalDocDrafterAgent for Colorado family law questions
- This agent provides GENERAL LEGAL INFORMATION ONLY, not legal advice
- Always recommend consulting a licensed attorney

For COMPLEX MULTI-STEP requests (research and create, brand package):
- Delegate to WorkflowAgent for orchestration

When delegating, provide:
1. The agent name (ImageAgent, VideoAgent, etc.)
2. A clear task description
3. Any relevant context (count, style, references)

Available agents:
- ImageAgent: Create images (logos, banners, illustrations)
- VideoAgent: Create videos (text-to-video, animations)
- AudioAgent: Create audio (TTS, voiceovers)
- ThreeDAgent: Create 3D models
- ImageEditingAgent: Edit images (upscale, remove bg, recolor)
- VideoEditingAgent: Edit videos (trim, effects, text)
- ResearchAgent: Search web and spider network (general trending)
- CompetitorAnalysisAgent: Business/market/startup research, SWOT, competitor analysis
- CustomerResearchAgent: Customer personas, pain points, sentiment
- LegalDocDrafterAgent: Colorado family law info, motion templates, court procedures (NOT legal advice)
- WorkflowAgent: Multi-step workflows"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate a task to a specialized agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": """Which agent to delegate to:
- Creation: ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- Editing: ImageEditingAgent, VideoEditingAgent
- Research: ResearchAgent (web/spider search), CompetitorAnalysisAgent (market/SWOT), CustomerResearchAgent (personas)
- Strategy: BrandIdentityAgent (brand colors/style), ContentStrategyAgent (content planning), SEOOptimizerAgent (keywords/hashtags), SocialMediaAgent (platform strategy)
- Executive: CTOAgent (technical planning), COOAgent (operations), CreativeDirectorAgent (creative guidance)
- Analysis: TrendAnalysisAgent (market trends), OpportunityScoringAgent (opportunity scoring)
- Training: CharacterTrainingAgent (LoRA training), TrainedCreationAgent (use trained models)
- Legal: LegalDocDrafterAgent (divorce/custody/motions)
- Orchestration: WorkflowAgent (multi-step workflows)""",
                            "enum": [
                                # Creation agents
                                "ImageAgent",
                                "VideoAgent",
                                "AudioAgent",
                                "ThreeDAgent",
                                # Editing agents
                                "ImageEditingAgent",
                                "VideoEditingAgent",
                                # Research agents
                                "ResearchAgent",
                                "CompetitorAnalysisAgent",
                                "CustomerResearchAgent",
                                # Strategy agents (Session 411)
                                "BrandIdentityAgent",
                                "ContentStrategyAgent",
                                "SEOOptimizerAgent",
                                "SocialMediaAgent",
                                # Executive agents (Session 411)
                                "CTOAgent",
                                "COOAgent",
                                "CreativeDirectorAgent",
                                # Analysis agents (Session 411)
                                "TrendAnalysisAgent",
                                "OpportunityScoringAgent",
                                # Training agents (Session 411)
                                "CharacterTrainingAgent",
                                "TrainedCreationAgent",
                                # Legal agent
                                "LegalDocDrafterAgent",
                                # Orchestration
                                "WorkflowAgent"
                            ]
                        },
                        "task": {
                            "type": "string",
                            "description": "The task to perform, in natural language"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (count, style, reference_ids, etc.)"
                        }
                    },
                    "required": ["agent_name", "task"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._router = None

    @property
    def router(self):
        """Lazy-load AgentRouter."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Process a user message and route to appropriate agent or respond directly.
        """
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("personal_assistant", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # First, check if this is a simple question
                is_question, question_type = self._is_question(task)

                self.record_decision(
                    decision_type="intent_analysis",
                    action=f"Classified as {'question' if is_question else 'action request'}",
                    reasoning=f"Task: {task[:100]}",
                    confidence=0.85 if is_question else 0.9
                )

                if is_question:
                    # Answer directly without delegation
                    # Session 454: Pass question_type to enable enhanced handling
                    # Session 454: Track routing analytics
                    record_routing_decision(
                        task=task,
                        selected_agent='PersonalAssistantAgent',
                        method='direct_answer',
                        confidence=0.85,
                        is_question=True,
                        alternatives=[]
                    )
                    return self._answer_question(task, scifi_context, spider_context, start_time, question_type)

                # It's an action request - determine which agent to use
                suggested_agent = self._detect_agent(task)

                if suggested_agent:
                    self.record_decision(
                        decision_type="agent_selection",
                        action=f"Routing to {suggested_agent}",
                        reasoning=f"Keywords matched for {suggested_agent}",
                        alternatives=list(INTENT_KEYWORDS.keys()),
                        confidence=0.9
                    )

                    # Session 454: Track routing analytics
                    # Determine routing method from the detect_agent decision
                    routing_method = 'keyword'  # Default to keyword
                    if hasattr(self, '_last_routing_method'):
                        routing_method = self._last_routing_method or 'keyword'
                    record_routing_decision(
                        task=task,
                        selected_agent=suggested_agent,
                        method=routing_method,
                        confidence=0.9,
                        is_question=False,
                        alternatives=list(INTENT_KEYWORDS.keys())[:5]
                    )

                    # Session 401: Get knowledge attribution before delegation
                    relevant_knowledge = self._get_relevant_knowledge_for_task(task)
                    attribution = self._build_knowledge_attribution(relevant_knowledge)

                    # Delegate to the agent
                    result = self.router.route(
                        agent_name=suggested_agent,
                        task=task,
                        context=context
                    )

                    tool_calls_made.append({
                        'tool': 'delegate_to_agent',
                        'agent': suggested_agent,
                        'task': task,
                        'result': result.to_dict()
                    })

                    self.mark_decision_outcome(
                        success=result.success,
                        result_summary=result.message[:100] if result.message else str(result.data)[:100]
                    )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 401: Merge attribution from delegated agent if available
                    if result.knowledge_attribution:
                        attribution = KnowledgeAttribution(
                            spider_sources=list(set(attribution.spider_sources + result.knowledge_attribution.spider_sources)),
                            knowledge_items=attribution.knowledge_items + result.knowledge_attribution.knowledge_items,
                            confidence_score=(attribution.confidence_score + result.knowledge_attribution.confidence_score) / 2 if attribution.confidence_score else result.knowledge_attribution.confidence_score,
                            data_freshness_hours=min(attribution.data_freshness_hours, result.knowledge_attribution.data_freshness_hours) if attribution.data_freshness_hours else result.knowledge_attribution.data_freshness_hours,
                            total_sources=attribution.total_sources + result.knowledge_attribution.total_sources
                        )

                    return AgentResult(
                        success=result.success,
                        message=result.message,
                        data={
                            'delegated_to': suggested_agent,
                            'agent_result': result.data,
                            'original_task': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made,
                        knowledge_attribution=attribution  # Session 401
                    )

                else:
                    # Couldn't determine agent - use GPT to decide
                    # Session 454: Track GPT fallback routing
                    record_routing_decision(
                        task=task,
                        selected_agent='GPT_FALLBACK',
                        method='gpt',
                        confidence=0.5,
                        is_question=False,
                        alternatives=[]
                    )
                    return self._gpt_route(task, context, scifi_context, spider_context, start_time)

            except Exception as e:
                logger.error(f"PersonalAssistantAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _is_question(self, task: str) -> Tuple[bool, str]:
        """
        Determine if the task is a question (requiring direct answer) vs action request.

        Session 454: MAJOR FIX - Distinguish informational questions from action requests.
        - "What's trending in AI?" → Answer directly with spider data (informational)
        - "Research AI trends for my report" → Route to ResearchAgent (action request)

        Returns:
            Tuple of (is_question, question_type)
            - question_type can be: 'knowledge_question', 'trend_question', 'direct_question', ''
        """
        task_lower = task.lower().strip()

        # Session 454: Check for ACTION indicators first
        # If the user wants us to DO something, it's not a question
        action_indicators = [
            'create', 'make', 'generate', 'design', 'build', 'produce',
            'research for', 'research and', 'analyze for', 'prepare',
            'write a', 'draft a', 'compile', 'put together'
        ]
        has_action_intent = any(indicator in task_lower for indicator in action_indicators)

        # Session 454: Trend/news QUESTIONS can be answered directly
        # These use spider data but don't require agent routing
        trend_indicators = [
            'trending', 'trends', 'news', 'latest',
            'what\'s hot', "what's hot", 'whats hot', 'popular',
            'current events', 'happening', 'going on', 'hot in', 'hot right now'
        ]

        # Question starters that indicate informational intent
        question_starters = [
            'what is', 'what are', 'what does', 'what do', "what's",
            'how do', 'how does', 'how can', 'how should',
            'why is', 'why does', 'why do',
            'when is', 'when does', 'when do',
            'where is', 'where does', 'where do',
            'who is', 'who does', 'who can',
            'which is', 'which are',
            'can you explain', 'explain',
            'tell me about', 'describe',
            'is it', 'are there', 'do you', 'does it',
        ]

        is_question_format = (
            any(task_lower.startswith(starter) for starter in question_starters) or
            task_lower.endswith('?')
        )

        # Session 454: INFORMATIONAL trend questions - answer directly with spider data
        # "What's trending in AI?" - question format + trend topic = answer directly
        # "Research AI trends for my report" - action intent = route to agent
        has_trend_topic = any(indicator in task_lower for indicator in trend_indicators)

        if has_trend_topic and is_question_format and not has_action_intent:
            # This is an informational question about trends
            # We'll answer directly using spider context (injected in _answer_question)
            logger.info(f"Detected trend question (answering directly): {task[:50]}")
            return True, 'trend_question'

        # Session 454: Market/business research REQUESTS should still go to agents
        # "What's the market for AI tools?" vs "Research the market for AI tools"
        business_action_indicators = [
            'research the market', 'analyze the market', 'competitor analysis',
            'market research', 'business research', 'industry analysis'
        ]
        if any(indicator in task_lower for indicator in business_action_indicators):
            # These are action requests, not questions
            return False, ''

        # Standard question detection
        for starter in question_starters:
            if task_lower.startswith(starter):
                return True, 'knowledge_question'

        # Check for question mark at end
        if task_lower.endswith('?'):
            # But exclude action questions like "can you create a logo?"
            if not has_action_intent:
                return True, 'direct_question'

        return False, ''

    def _detect_agent(self, task: str) -> Optional[str]:
        """
        Detect which agent should handle this task.

        Session 293: Uses a two-tier approach:
        1. Semantic routing (embeddings) - higher accuracy for natural language
        2. Keyword fallback - for cases where semantic routing fails or low confidence

        Session 454: Enhanced business context detection to suggest research workflows.

        Returns:
            Agent name or None if can't determine
        """
        task_lower = task.lower()

        # =========================================================================
        # TIER 0: Workflow patterns (highest priority - must check before semantic)
        # =========================================================================
        workflow_patterns = [
            'research and create', 'research then create',
            'brand identity package', 'brand package',
            'thumbnail package', 'complete package',
        ]
        for pattern in workflow_patterns:
            if pattern in task_lower:
                self._last_routing_method = 'workflow'  # Session 454: Track method
                return 'WorkflowAgent'

        # Check for multi-step patterns (research + creation = workflow)
        has_research = any(w in task_lower for w in ['research', 'analyze', 'find'])
        has_creation = any(w in task_lower for w in ['create', 'make', 'generate', 'design'])
        if has_research and has_creation:
            self._last_routing_method = 'workflow'  # Session 454: Track method
            return 'WorkflowAgent'

        # =========================================================================
        # Session 454: SMART BUSINESS CONTEXT DETECTION
        # =========================================================================
        # Detect when user has business context (startup, business, market)
        # AND wants to create something - suggest research-first workflow
        business_context_indicators = [
            'for my startup', 'for my business', 'for my company',
            'startup', 'business idea', 'new business', 'my company',
            'launching', 'going to market', 'go to market',
            'brand new', 'new venture', 'entrepreneur'
        ]
        has_business_context = any(indicator in task_lower for indicator in business_context_indicators)

        if has_business_context and has_creation:
            # Session 454: Business + creation = suggest research-first workflow
            # "Create a logo for my startup" → WorkflowAgent (research + create)
            # This ensures users get market-informed designs, not generic ones
            logger.info(f"Business context + creation detected: routing to WorkflowAgent for research-first approach")
            self.record_decision(
                decision_type="business_workflow_suggestion",
                action="Routing to WorkflowAgent for research-first approach",
                reasoning=f"Detected business context ({[i for i in business_context_indicators if i in task_lower]}) + creation intent",
                confidence=0.85
            )
            self._last_routing_method = 'business_context'  # Session 454: Track method
            return 'WorkflowAgent'

        # =========================================================================
        # TIER 1: Semantic Routing (embeddings-based)
        # =========================================================================
        semantic_router = get_semantic_router()
        if semantic_router:
            try:
                result = semantic_router.route_query(task)

                # Log semantic routing result
                logger.info(
                    f"Semantic routing: {result.agent_name} "
                    f"(confidence={result.confidence:.3f}, method={result.method})"
                )

                # High confidence semantic match - use it
                # But apply business research guard for creation intent
                SEMANTIC_CONFIDENCE_THRESHOLD = 0.45

                if result.confidence >= SEMANTIC_CONFIDENCE_THRESHOLD:
                    selected_agent = result.agent_name

                    # Session 293: Business Research agents ONLY when NO creation intent
                    # "Create a logo for my startup" should go to ImageAgent, not CompetitorAnalysisAgent
                    if has_creation and selected_agent in ('CompetitorAnalysisAgent', 'CustomerResearchAgent'):
                        # Fall through to keyword matching which handles this correctly
                        logger.info(f"Semantic chose {selected_agent} but creation intent detected, using keyword fallback")
                    else:
                        self.record_decision(
                            decision_type="semantic_routing",
                            action=f"Semantic routing selected {selected_agent}",
                            reasoning=f"Confidence: {result.confidence:.3f}, Top matches: {result.all_matches[:3]}",
                            confidence=result.confidence
                        )
                        self._last_routing_method = 'semantic'  # Session 454: Track method
                        return selected_agent

            except Exception as e:
                logger.warning(f"Semantic routing failed, using keyword fallback: {e}")

        # =========================================================================
        # TIER 2: Keyword Fallback
        # =========================================================================

        # Session 293: Business Research agents ONLY when NO creation intent
        # "Research AI market for my startup" -> CompetitorAnalysisAgent
        # "Create a logo for my startup" -> ImageAgent (has creation intent)
        if not has_creation:
            business_research_checks = [
                ('CompetitorAnalysisAgent', [
                    'for my startup', 'startup idea', 'business idea', 'market research',
                    'competitor analysis', 'competitive landscape', 'swot analysis',
                    'analyze competitors', 'research the market', 'market for my',
                    'research market', 'industry analysis'
                ]),
                ('CustomerResearchAgent', [
                    'customer personas', 'build personas', 'pain points', 'customer research',
                    'who are my customers', 'target audience', 'customer sentiment'
                ]),
            ]
            for agent, keywords in business_research_checks:
                for kw in keywords:
                    if kw in task_lower:
                        self._last_routing_method = 'keyword'  # Session 454: Track method
                        return agent

        # Priority keywords that override other matches
        # Ordered from most specific to least specific
        # These indicate strong intent for a specific agent
        priority_checks = [
            # Session 403: Legal terms FIRST (before 'motion' triggers VideoAgent)
            ('LegalDocDrafterAgent', [
                'divorce', 'custody', 'child support', 'parenting time', 'court',
                'attorney', 'lawyer', 'legal', 'family law', 'pro se',
                'file motion', 'draft motion', 'motion to', 'jdf', 'parental responsibilities',
                'separation', 'decree', 'modification', 'enforcement',
                # Session 404: Added keywords for denied motion analysis
                'denied', 'denied motion', 'motion denied', 'rejected', 'dismissal',
                'rewrite', 'refile', 'magistrate', 'ruling', 'contempt', 'affidavit',
            ]),
            # Most specific compound terms first
            ('AudioAgent', ['voiceover', 'text to speech', 'tts', 'narration']),
            # Video editing terms (must check before generic 'video')
            ('VideoEditingAgent', ['trim video', 'cut video', 'edit video', 'slow motion', 'speed up video', 'trim', 'concatenate']),
            ('ImageEditingAgent', ['upscale', 'remove background', 'recolor', 'variations', 'edit image']),
            ('ThreeDAgent', ['3d', 'three-dimensional', 'convert to 3d']),
            # Then single keywords that are strong indicators
            ('AudioAgent', ['voice', 'speech', 'audio']),
            ('VideoAgent', ['animate', 'animation', 'video']),
        ]

        # Check priority keywords first (in order)
        for agent, keywords in priority_checks:
            for kw in keywords:
                if kw in task_lower:
                    self._last_routing_method = 'keyword'  # Session 454: Track method
                    return agent

        # Check each agent's keywords with scoring
        # Session 293: Exclude business research agents if there's creation intent
        business_research_agents = {'CompetitorAnalysisAgent', 'CustomerResearchAgent'}
        scores = {}
        for agent, keywords in INTENT_KEYWORDS.items():
            # Skip business research agents when user wants to CREATE something
            if has_creation and agent in business_research_agents:
                continue
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > 0:
                scores[agent] = score

        if scores:
            # Session 454: Enhanced tie-breaking for keyword scoring
            # When multiple agents have same score, use these criteria:
            # 1. Agent priority from routing_config (higher = better)
            # 2. Creation agents preferred for creation requests
            # 3. Alphabetical as final fallback

            max_score = max(scores.values())
            tied_agents = [agent for agent, score in scores.items() if score == max_score]

            if len(tied_agents) == 1:
                selected_agent = tied_agents[0]
            else:
                # Tie-breaking needed
                logger.info(f"Tie between {tied_agents} (score={max_score}), applying tie-breakers")

                # Get priorities from routing config
                agent_priorities = {}
                for agent in tied_agents:
                    config = AGENT_ROUTING_CONFIG.get(agent, {})
                    agent_priorities[agent] = config.get('priority', 0)

                # Sort by: priority (desc), then prefer creation agents for creation, then alphabetical
                def tie_break_key(agent):
                    priority = agent_priorities.get(agent, 0)
                    # Boost creation agents if this is a creation request
                    creation_boost = 100 if has_creation and agent in ['ImageAgent', 'VideoAgent', 'AudioAgent', 'ThreeDAgent'] else 0
                    # Negative priority for descending sort (higher priority first)
                    return (-priority - creation_boost, agent)

                tied_agents.sort(key=tie_break_key)
                selected_agent = tied_agents[0]
                logger.info(f"Tie-breaker selected: {selected_agent}")

            self._last_routing_method = 'keyword'  # Session 454: Track method
            return selected_agent

        # Fallback: check for generic creation words
        if any(word in task_lower for word in ['create', 'make', 'generate', 'design']):
            # Default to ImageAgent for generic creation
            self._last_routing_method = 'keyword'  # Session 454: Track method
            return 'ImageAgent'

        self._last_routing_method = None  # Session 454: Track method
        return None

    def _check_ui_navigation(self, task: str) -> Optional[str]:
        """
        Session 414: Check if user is asking about UI navigation.

        Returns guidance string if matched, None otherwise.
        """
        task_lower = task.lower()

        for category, info in UI_NAVIGATION_GUIDE.items():
            for keyword in info['keywords']:
                if keyword in task_lower:
                    return info['guidance']

        return None

    def _answer_question(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float,
        question_type: str = 'knowledge_question'
    ) -> AgentResult:
        """
        Answer a question directly using GPT.

        Session 401: Enhanced with knowledge attribution to show users
        what intelligence sources influenced the response.
        Session 414: Added UI navigation guidance for platform features.
        Session 454: Enhanced trend question handling with fresh spider data.
        """
        try:
            # Session 414: Check for UI navigation questions first
            # This provides instant, helpful guidance without GPT call
            ui_guidance = self._check_ui_navigation(task)
            if ui_guidance:
                return AgentResult(
                    success=True,
                    message=ui_guidance,
                    data={'type': 'ui_navigation', 'question': task},
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    decisions_made=1
                )

            # Session 454: For trend questions, fetch FRESH spider data
            # This ensures "What's trending in AI?" gets current intelligence
            enhanced_spider_context = spider_context.copy() if spider_context else {}

            if question_type == 'trend_question':
                try:
                    fresh_trends = self._fetch_fresh_trends_for_question(task)
                    if fresh_trends:
                        enhanced_spider_context['relevant_trends'] = fresh_trends.get('trends', [])
                        enhanced_spider_context['trend_articles'] = fresh_trends.get('articles', [])
                        logger.info(f"Injected {len(fresh_trends.get('trends', []))} fresh trends for question")
                except Exception as e:
                    logger.warning(f"Failed to fetch fresh trends: {e}")

            # Session 401: Build prompt with attribution to track what knowledge is used
            prompt, attribution = self._build_prompt_with_attribution(task, scifi_context, enhanced_spider_context)

            # Session 454: Enhanced instruction for trend questions
            if question_type == 'trend_question' and enhanced_spider_context.get('trend_articles'):
                articles = enhanced_spider_context['trend_articles'][:10]
                prompt += "\n\n## Recent Articles for Context"
                for article in articles:
                    title = article.get('title', '')[:80]
                    source = article.get('source', 'unknown')
                    url = article.get('url', '')
                    prompt += f"\n- [{source}] {title}"
                    if url:
                        prompt += f" ({url})"

            # Append instruction to answer directly
            prompt += "\n\nAnswer this question directly without delegating to an agent."
            if question_type == 'trend_question':
                prompt += " Use the trend data and articles provided above to give a current, relevant answer."

            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": task}
                ],
                max_completion_tokens=1500,
                reasoning_effort="medium",
            )

            answer = response.choices[0].message.content

            return AgentResult(
                success=True,
                message=answer,
                data={
                    'type': 'direct_answer',
                    'question': task,
                    'question_type': question_type  # Session 454
                },
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                decisions_made=self._tt_decision_count,
                knowledge_attribution=attribution  # Session 401: Include attribution
            )

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _fetch_fresh_trends_for_question(self, task: str) -> Dict[str, Any]:
        """
        Session 454: Fetch fresh spider trends for trend questions.

        Extracts topic from question and queries spider intelligence.
        """
        try:
            from core.services.spider_intelligence import SpiderIntelligenceService

            service = SpiderIntelligenceService()

            # Extract topic filter from question
            task_lower = task.lower()
            topic_filter = None

            # Session 272 topic filters
            if any(kw in task_lower for kw in ['ai', 'machine learning', 'llm', 'gpt', 'neural', 'deep learning']):
                topic_filter = 'ai'
            elif any(kw in task_lower for kw in ['web', 'javascript', 'react', 'frontend', 'backend', 'css']):
                topic_filter = 'web'
            elif any(kw in task_lower for kw in ['security', 'cyber', 'hack', 'privacy', 'encrypt']):
                topic_filter = 'security'
            elif any(kw in task_lower for kw in ['cloud', 'aws', 'docker', 'kubernetes', 'devops']):
                topic_filter = 'cloud'
            elif any(kw in task_lower for kw in ['design', 'ui', 'ux', 'figma', 'typography']):
                topic_filter = 'design'

            # Get trending topics
            trends = service.get_trending_topics(hours=72, limit=10)

            # Get recent articles with optional topic filter
            articles = service.get_tech_trends(
                hours=72,
                limit=15,
                topic_filter=topic_filter
            )

            return {
                'trends': trends if isinstance(trends, list) else [],
                'articles': articles if isinstance(articles, list) else [],
                'topic_filter': topic_filter
            }

        except Exception as e:
            logger.warning(f"Error fetching fresh trends: {e}")
            return {'trends': [], 'articles': [], 'topic_filter': None}

    def _gpt_route(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float
    ) -> AgentResult:
        """
        Use GPT to decide which agent to route to.

        Session 401: Enhanced with knowledge attribution.
        """
        try:
            # Session 401: Build prompt with attribution
            full_prompt, attribution = self._build_prompt_with_attribution(task, scifi_context, spider_context)

            gpt_response = self._call_openai(full_prompt)

            if gpt_response.get('tool_calls'):
                # GPT decided to delegate
                for tool_call in gpt_response['tool_calls']:
                    if tool_call['name'] == 'delegate_to_agent':
                        agent_name = tool_call['arguments'].get('agent_name')
                        subtask = tool_call['arguments'].get('task', task)
                        subtask_context = tool_call['arguments'].get('context', context)

                        self.record_decision(
                            decision_type="gpt_routing",
                            action=f"GPT routed to {agent_name}",
                            reasoning=f"GPT analysis determined {agent_name} is best",
                            confidence=0.85
                        )

                        # Execute delegation
                        result = self.router.route(
                            agent_name=agent_name,
                            task=subtask,
                            context=subtask_context
                        )

                        # Session 401: Merge attribution from delegated agent if available
                        merged_attribution = attribution
                        if result.knowledge_attribution:
                            # Combine sources from both
                            merged_attribution = KnowledgeAttribution(
                                spider_sources=list(set(attribution.spider_sources + result.knowledge_attribution.spider_sources)),
                                knowledge_items=attribution.knowledge_items + result.knowledge_attribution.knowledge_items,
                                confidence_score=(attribution.confidence_score + result.knowledge_attribution.confidence_score) / 2,
                                data_freshness_hours=min(attribution.data_freshness_hours, result.knowledge_attribution.data_freshness_hours),
                                total_sources=attribution.total_sources + result.knowledge_attribution.total_sources
                            )

                        return AgentResult(
                            success=result.success,
                            message=result.message,
                            data={
                                'delegated_to': agent_name,
                                'agent_result': result.data,
                                'original_task': task
                            },
                            agent_name=self.name,
                            execution_time_ms=int((time.time() - start_time) * 1000),
                            decisions_made=self._tt_decision_count,
                            knowledge_attribution=merged_attribution  # Session 401
                        )

            # GPT responded without delegation
            return AgentResult(
                success=True,
                message=gpt_response.get('content', ''),
                data={'type': 'conversation'},
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                knowledge_attribution=attribution  # Session 401
            )

        except Exception as e:
            logger.error(f"GPT routing failed: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool call - only delegate_to_agent is supported."""
        if tool_name != "delegate_to_agent":
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

        agent_name = arguments.get('agent_name')
        task = arguments.get('task', '')
        context = arguments.get('context', {})

        try:
            result = self.router.route(agent_name, task, context)
            return result.to_dict()
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
