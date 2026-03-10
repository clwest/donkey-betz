"""
PersonalAssistantAgent PAFetchHandlersMixin — extracted handler methods.
"""

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
from typing import Dict, Any, Optional, Tuple

from core.agents.base_agent import BaseAgent, AgentResult, KnowledgeAttribution
from core.agents.routing_config import get_intent_keywords, AGENT_ROUTING_CONFIG
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_assistant_request_with_ml(request_data: dict) -> dict:
    """Analyze assistant request data using ML models (Text for intent classification)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=request_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'intent_classification': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML assistant request analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

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




class PAFetchHandlersMixin:
    """Mixin providing handler methods for PersonalAssistantAgent."""

    def _fetch_fresh_trends_for_question(self, task: str) -> Dict[str, Any]:
        """
        Session 454: Fetch fresh spider trends for trend questions.
        Session 495: UPGRADED - Now uses SmartTrendingService for dynamic topic matching.

        Works for ANY topic without hardcoded if/elif chains!
        Examples:
            - "What's trending in startups?" -> Routes to startups, business spiders
            - "What's trending in AI?" -> Routes to ai_ml, tech spiders
            - "What's trending in healthcare?" -> Routes to healthtech spiders
            - "What's trending in crypto?" -> Routes to financial, blockchain spiders
        """
        try:
            from core.services.smart_trending_service import get_smart_trending_service

            service = get_smart_trending_service()

            # Session 495: Dynamic topic extraction and category mapping
            result = service.get_trending_for_query(
                query=task,
                hours=72,
                article_limit=15,
                use_cache=True
            )

            logger.info(f"🕷️ [Session 495] SmartTrending: topic='{result.get('topic')}', "
                       f"categories={result.get('categories')}, "
                       f"articles={len(result.get('articles', []))}, "
                       f"cache_hit={result.get('cache_hit', False)}")

            return {
                'trends': result.get('trends', []),
                'articles': result.get('articles', []),
                'topic_filter': result.get('topic'),  # For compatibility
                'categories': result.get('categories', []),  # New: matched categories
                'cache_hit': result.get('cache_hit', False)
            }

        except Exception as e:
            logger.warning(f"Error fetching fresh trends (falling back to legacy): {e}")
            # Fallback to legacy method if SmartTrendingService fails
            return self._fetch_fresh_trends_legacy(task)

    def _fetch_fresh_trends_legacy(self, task: str) -> Dict[str, Any]:
        """Legacy fallback method using SpiderIntelligenceService."""
        try:
            from core.services.spider_intelligence import SpiderIntelligenceService

            service = SpiderIntelligenceService()
            trends = service.get_trending_topics(hours=72, limit=10)
            tech_data = service.get_tech_trends(hours=72, limit=15, topic_filter=None)

            articles = []
            if isinstance(tech_data, dict):
                articles = tech_data.get('discussions', []) or tech_data.get('projects', [])
            elif isinstance(tech_data, list):
                articles = tech_data

            return {
                'trends': trends if isinstance(trends, list) else [],
                'articles': articles,
                'topic_filter': None
            }
        except Exception as e:
            logger.warning(f"Legacy trend fetch also failed: {e}")
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
            # Session 565: Include platform intelligence context
            intel_ctx = getattr(self, '_intelligence_context', None) or {}
            full_prompt, attribution = self._build_prompt_with_attribution(
                task, scifi_context, spider_context, intel_ctx
            )

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
            # Session 757: Return rich conversation data for Memory Palace display
            response_content = gpt_response.get('content', '')
            return AgentResult(
                success=True,
                message=response_content,
                data={
                    'type': 'conversation',
                    'content_type': 'assistant_response',
                    'response': response_content,
                    'query': task,
                },
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
        """Execute tool call - supports multiple PA tools."""

        # Session 575: Handle get_sports_data tool
        if tool_name == "get_sports_data":
            return self._get_sports_data(arguments)

        # Session 576: Handle system status tools
        if tool_name == "get_system_status":
            return self._get_system_status(arguments)

        if tool_name == "promote_boardroom_decision":
            return self._promote_boardroom_decision(arguments)

        if tool_name == "reject_boardroom_decision":
            return self._reject_boardroom_decision(arguments)

        if tool_name == "query_agent_data":
            return self._query_agent_data(arguments)

        if tool_name == "get_spider_intelligence":
            return self._get_spider_intelligence(arguments)

        # Session 577: Phase 2 Tools
        if tool_name == "execute_spider":
            return self._execute_spider(arguments)

        if tool_name == "create_content":
            return self._create_content(arguments)

        if tool_name == "manage_content_channel":
            return self._manage_content_channel(arguments)

        if tool_name == "query_prediction_markets":
            return self._query_prediction_markets(arguments)

        # Session 578: Phase 3 Tools
        if tool_name == "execute_workflow":
            return self._execute_workflow(arguments)

        if tool_name == "query_arbitrage":
            return self._query_arbitrage(arguments)

        if tool_name == "manage_bankroll":
            return self._manage_bankroll(arguments)

        if tool_name == "search_knowledge":
            return self._search_knowledge(arguments)

        # Session 579: Phase 4 Tools
        if tool_name == "create_boardroom_decision":
            return self._create_boardroom_decision(arguments)

        # Session 944: List boardroom decisions
        if tool_name == "list_boardroom_decisions":
            return self._list_boardroom_decisions(arguments)

        if tool_name == "query_dreams":
            return self._query_dreams(arguments)

        if tool_name == "manage_situations":
            return self._manage_situations(arguments)

        if tool_name == "query_conversations":
            return self._query_conversations(arguments)

        # Session 579: Phase 5 Tools
        if tool_name == "get_opportunity_pipeline":
            return self._get_opportunity_pipeline(arguments)

        if tool_name == "create_project":
            return self._create_project(arguments)

        if tool_name == "trigger_agent_conversation":
            return self._trigger_agent_conversation(arguments)

        if tool_name == "schedule_content":
            return self._schedule_content(arguments)

        if tool_name == "analyze_project_intelligence":
            return self._analyze_project_intelligence(arguments)

        # Session 579: ThinkingAgent/System Insights tools
        if tool_name == "query_tracked_concerns":
            return self._query_tracked_concerns(arguments)

        if tool_name == "get_system_insights":
            return self._get_system_insights(arguments)

        # Session 579: Phase 7 tools
        if tool_name == "get_advisor_consultation":
            return self._get_advisor_consultation(arguments)

        if tool_name == "query_revenue_metrics":
            return self._query_revenue_metrics(arguments)

        # Session 580: Phase 8 tools
        if tool_name == "manage_proactive_alerts":
            return self._manage_proactive_alerts(arguments)

        if tool_name == "query_learning_progress":
            return self._query_learning_progress(arguments)

        if tool_name == "manage_team":
            return self._manage_team(arguments)

        if tool_name == "generate_video":
            return self._generate_video(arguments)

        if tool_name == "manage_distribution":
            return self._manage_distribution(arguments)

        if tool_name == "query_analytics":
            return self._query_analytics(arguments)

        if tool_name == "time_travel_memory":
            return self._time_travel_memory(arguments)

        if tool_name == "manage_memory_palace":
            return self._manage_memory_palace(arguments)

        if tool_name == "run_diagnostics":
            return self._run_diagnostics(arguments)

        if tool_name == "manage_collaboration":
            return self._manage_collaboration(arguments)

        # Session 580: Phase 9 tools
        if tool_name == "manage_project":
            return self._manage_project(arguments)

        if tool_name == "query_legal":
            return self._query_legal(arguments)

        if tool_name == "manage_agent_training":
            return self._manage_agent_training(arguments)

        if tool_name == "manage_workflow_templates":
            return self._manage_workflow_templates(arguments)

        if tool_name == "generate_image":
            return self._generate_image(arguments)

        # Session 581: Phase 10 - Betting/Sports tools
        if tool_name == "query_live_odds":
            return self._query_live_odds(arguments)

        if tool_name == "query_games":
            return self._query_games(arguments)

        if tool_name == "query_line_movements":
            return self._query_line_movements(arguments)

        if tool_name == "query_futures":
            return self._query_futures(arguments)

        if tool_name == "query_player_props":
            return self._query_player_props(arguments)

        if tool_name == "query_betting_recommendations":
            return self._query_betting_recommendations(arguments)

        # Phase 11: Notification Tools (Session 582)
        if tool_name == "manage_notifications":
            return self._manage_notifications(arguments)

        if tool_name == "manage_push_notifications":
            return self._manage_push_notifications(arguments)

        # Phase 12: Export & Scheduler Tools (Session 582)
        if tool_name == "manage_exports":
            return self._manage_exports(arguments)

        if tool_name == "manage_scheduler":
            return self._manage_scheduler(arguments)

        # Phase 13: Monitoring Tools (Session 582)
        if tool_name == "query_system_health":
            return self._query_system_health(arguments)

        if tool_name == "query_activity_metrics":
            return self._query_activity_metrics(arguments)

        # ===== Phase 14: Artifact & Review Tools (Session 583) =====
        if tool_name == "manage_artifacts":
            return self._manage_artifacts(arguments)

        if tool_name == "manage_reviews":
            return self._manage_reviews(arguments)

        # ===== Phase 15: Journey & Proposal Tools (Session 583) =====
        if tool_name == "manage_journeys":
            return self._manage_journeys(arguments)

        if tool_name == "manage_proposals":
            return self._manage_proposals(arguments)

        # ===== Phase 16: Solutions & Learning Tools (Session 583) =====
        if tool_name == "manage_solutions":
            return self._manage_solutions(arguments)

        if tool_name == "query_learning":
            return self._query_learning(arguments)

        # ===== Phase 17: Portfolio & Nexus Tools (Session 583) =====
        if tool_name == "manage_portfolio":
            return self._manage_portfolio(arguments)

        if tool_name == "query_nexus":
            return self._query_nexus(arguments)

        # ===== Phase 18: Predictions & Performance Tools (Session 583) =====
        if tool_name == "manage_predictions":
            return self._manage_predictions(arguments)

        if tool_name == "query_performance":
            return self._query_performance(arguments)

        # ===== Phase 19: Analytics Tools (Session 584) =====
        if tool_name == "query_workflow_analytics":
            return self._query_workflow_analytics(arguments)

        if tool_name == "query_video_analytics":
            return self._query_video_analytics(arguments)

        if tool_name == "query_model_analytics":
            return self._query_model_analytics(arguments)

        # ===== Phase 20: Collaboration & Search Tools (Session 584) =====
        if tool_name == "query_collaboration":
            return self._query_collaboration(arguments)

        if tool_name == "manage_favorites":
            return self._manage_favorites(arguments)

        if tool_name == "query_semantic_search":
            return self._query_semantic_search(arguments)

        # ===== Phase 21: Project & Workflow Collaboration Tools (Session 585) =====
        if tool_name == "manage_project_collaboration":
            return self._manage_project_collaboration(arguments)

        if tool_name == "manage_workflow_sharing":
            return self._manage_workflow_sharing(arguments)

        # ===== Phase 22: Team Workflows & Agent Evolution Tools (Session 585) =====
        if tool_name == "manage_team_workflows":
            return self._manage_team_workflows(arguments)

        if tool_name == "query_agent_evolution":
            return self._query_agent_evolution(arguments)

        # ===== Phase 23: Voice Marketplace & Agent Relationships Tools (Session 586) =====
        if tool_name == "manage_voice_marketplace":
            return self._manage_voice_marketplace(arguments)

        if tool_name == "query_agent_relationships":
            return self._query_agent_relationships(arguments)

        # ===== Phase 24: Hive Mind & Time Capsules Tools (Session 587) =====
        if tool_name == "manage_hive_mind":
            return self._manage_hive_mind(arguments)

        if tool_name == "manage_time_capsules":
            return self._manage_time_capsules(arguments)

        # ===== Phase 25: A/B Testing & Memory Clusters Tools (Session 587) =====
        if tool_name == "manage_ab_testing":
            return self._manage_ab_testing(arguments)

        if tool_name == "manage_memory_clusters":
            return self._manage_memory_clusters(arguments)

        if tool_name == "delegate_to_agent":
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

        return super()._execute_tool_call(tool_name, arguments)

    def _get_sports_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 575: Query internal sports API for live scores and odds.
        This uses data already in the system - no external API calls needed.
        """
        import requests

        sport = arguments.get('sport', 'nfl')
        team_filter = arguments.get('team', '').lower()

        # Map short sport names to API keys
        sport_map = {
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'mlb': 'baseball_mlb',
            'nhl': 'icehockey_nhl',
            'ncaaf': 'americanfootball_ncaaf',
            'ncaab': 'basketball_ncaab',
            'soccer': 'soccer_epl',
            'ufc': 'mma_mixed_martial_arts',
        }
        sport_key = sport_map.get(sport.lower(), 'americanfootball_nfl')

        try:
            # Call internal API
            response = requests.get(
                f'http://localhost:8000/api/v1/sports/live-odds-scores/',
                params={'sport': sport_key},
                timeout=10
            )

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Sports API returned {response.status_code}'
                }

            data = response.json()

            # Format games for easy reading
            games = []
            for game in data.get('odds', []):
                home = game.get('home_team', '')
                away = game.get('away_team', '')
                live = game.get('live', {})

                # Filter by team if specified
                if team_filter and team_filter not in home.lower() and team_filter not in away.lower():
                    continue

                game_info = {
                    'matchup': f"{away} @ {home}",
                    'home_team': home,
                    'away_team': away,
                    'home_score': live.get('home_score', 0),
                    'away_score': live.get('away_score', 0),
                    'status': live.get('status_detail', 'Scheduled'),
                    'is_live': live.get('is_live', False),
                    'is_final': live.get('is_final', False),
                }

                # Add simple score string
                if live.get('is_live') or live.get('is_final'):
                    game_info['score'] = f"{away} {live.get('away_score', 0)}, {home} {live.get('home_score', 0)}"
                else:
                    game_info['score'] = 'Not started'

                games.append(game_info)

            # Build summary
            live_games = [g for g in games if g['is_live']]
            final_games = [g for g in games if g['is_final']]
            upcoming_games = [g for g in games if not g['is_live'] and not g['is_final']]

            return {
                'success': True,
                'sport': sport.upper(),
                'total_games': len(games),
                'live_count': len(live_games),
                'final_count': len(final_games),
                'upcoming_count': len(upcoming_games),
                'games': games,
                'summary': self._format_scores_summary(games, sport)
            }

        except Exception as e:
            logger.error(f"Error fetching sports data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query SystemStateAggregator for attention items.
        Returns pending decisions, failed cycles, stale concerns, etc.
        """
        try:
            from core.services.system_state_aggregator import SystemStateAggregator

            category = arguments.get('category', 'all')
            max_items = arguments.get('max_items', 10)

            aggregator = SystemStateAggregator()
            items = aggregator.get_attention_items(max_per_section=max_items)

            # Convert to dicts for JSON serialization
            items_data = [item.to_dict() for item in items]

            # Filter by category if specified
            if category != 'all':
                category_map = {
                    'decisions': ['decision', 'boardroom'],
                    'health': ['health', 'alert', 'failed'],
                    'content': ['overdue', 'channel', 'content'],
                    'urgent': None  # Special case - filter by priority
                }

                if category == 'urgent':
                    items_data = [i for i in items_data if i.get('priority', 0) >= 80]
                elif category in category_map:
                    keywords = category_map[category]
                    items_data = [i for i in items_data
                                  if any(kw in i.get('category', '').lower() for kw in keywords)]

            # Build summary
            summary_lines = ["**System Status:**\n"]

            if not items_data:
                summary_lines.append("✅ No items need immediate attention.")
            else:
                # Group by section
                by_section = {}
                for item in items_data[:max_items]:
                    section = item.get('section', 'other')
                    if section not in by_section:
                        by_section[section] = []
                    by_section[section].append(item)

                section_icons = {
                    'command_center': '🎯',
                    'autonomous': '🤖',
                    'research': '🔬',
                    'boardroom': '🏛️'
                }

                for section, section_items in by_section.items():
                    icon = section_icons.get(section, '📋')
                    summary_lines.append(f"\n{icon} **{section.replace('_', ' ').title()}:**")
                    for item in section_items[:5]:
                        priority_icon = '🔴' if item.get('priority', 0) >= 80 else '🟡' if item.get('priority', 0) >= 60 else '🟢'
                        summary_lines.append(f"  {priority_icon} {item.get('title', 'Unknown')}")
                        if item.get('id'):
                            summary_lines.append(f"     ID: {item.get('id')}")

            return {
                'success': True,
                'total_items': len(items_data),
                'urgent_count': len([i for i in items_data if i.get('priority', 0) >= 80]),
                'items': items_data[:max_items],
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_spider_intelligence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query spider network for trending topics and fresh data.
        """
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count

            category = arguments.get('category', 'all')
            hours = arguments.get('hours', 24)
            limit = arguments.get('limit', 10)

            # Time filter
            since = timezone.now() - timedelta(hours=hours)

            # Build query
            query = SpiderData.objects.filter(created_at__gte=since)

            # Category mapping
            category_map = {
                'tech': ['hackernews', 'techcrunch', 'devto', 'github', 'producthunt'],
                'finance': ['coingecko', 'yahoo_finance', 'polygon_finance', 'kalshi'],
                'sports': ['theodds', 'espn'],
                'news': ['cnn', 'bbc', 'npr', 'reuters', 'axios'],
                'legal': ['courtlistener', 'findlaw', 'colorado_family_law'],
                'entertainment': ['variety', 'polygon_gaming', 'spotify']
            }

            if category != 'all' and category in category_map:
                spiders = category_map[category]
                query = query.filter(spider_name__in=spiders)

            # Get spider stats
            spider_stats = query.values('spider_name').annotate(
                count=Count('id')
            ).order_by('-count')[:limit]

            # Get recent items
            recent_items = query.order_by('-created_at')[:limit]

            items_data = []
            for item in recent_items:
                items_data.append({
                    'spider': item.spider_name,
                    'title': getattr(item, 'title', '')[:100] if hasattr(item, 'title') else '',
                    'category': getattr(item, 'category', 'general'),
                    'collected_at': item.created_at.isoformat() if item.created_at else None
                })

            # Build summary
            summary_lines = [f"**Spider Intelligence ({hours}h):**\n"]

            if not spider_stats:
                summary_lines.append("No recent spider data found.")
            else:
                summary_lines.append("📊 **Data by Spider:**")
                for stat in spider_stats[:10]:
                    summary_lines.append(f"  • {stat['spider_name']}: {stat['count']} items")

                if items_data:
                    summary_lines.append("\n📰 **Recent Items:**")
                    for item in items_data[:5]:
                        title = item.get('title', 'Untitled')[:50]
                        spider = item.get('spider', 'unknown')
                        summary_lines.append(f"  • [{spider}] {title}...")

            total_items = query.count()

            return {
                'success': True,
                'category': category,
                'hours': hours,
                'total_items': total_items,
                'spider_stats': list(spider_stats),
                'recent_items': items_data,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting spider intelligence: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 577: Phase 2 Tool Handlers
    # =========================================================================

    def _get_opportunity_pipeline(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query the opportunity pipeline.
        """
        try:
            from core.models_unified_system import Opportunity
            from django.utils import timezone
            from datetime import timedelta

            status = arguments.get('status', 'all')
            min_score = arguments.get('min_score', 0)
            opportunity_type = arguments.get('opportunity_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            opps_query = Opportunity.objects.all()

            if status != 'all':
                opps_query = opps_query.filter(status=status)

            if min_score > 0:
                opps_query = opps_query.filter(overall_score__gte=min_score)

            if opportunity_type != 'all':
                opps_query = opps_query.filter(opportunity_type=opportunity_type)

            # Order by score descending, recent first
            opps = opps_query.order_by('-overall_score', '-created_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Opportunity Pipeline:**\n"]
            total_revenue = 0

            if not opps:
                summary_lines.append("No opportunities found matching criteria.")
                summary_lines.append("\nOpportunities are discovered by spiders and scored by agents.")
            else:
                for opp in opps:
                    score = getattr(opp, 'overall_score', 0) or 0
                    revenue = getattr(opp, 'potential_revenue', 0) or 0
                    total_revenue += revenue

                    results.append({
                        'id': str(opp.id),
                        'title': opp.title[:100] if opp.title else 'Untitled',
                        'type': getattr(opp, 'opportunity_type', 'unknown'),
                        'source': getattr(opp, 'source', 'unknown'),
                        'score': score,
                        'status': getattr(opp, 'status', 'new'),
                        'estimated_revenue': revenue,
                        'created_at': opp.created_at.isoformat() if hasattr(opp, 'created_at') and opp.created_at else None
                    })

                    # Score emoji
                    if score >= 80:
                        emoji = '🔥'
                    elif score >= 60:
                        emoji = '⭐'
                    else:
                        emoji = '📋'

                    title_short = opp.title[:45] if opp.title else 'Untitled'
                    summary_lines.append(f"{emoji} **{title_short}...** (Score: {score})")

                summary_lines.append(f"\n📊 Total: {len(results)} opportunities")
                if total_revenue > 0:
                    summary_lines.append(f"💰 Est. Revenue: ${total_revenue:,.0f}")

            return {
                'success': True,
                'opportunities': results,
                'total_count': len(results),
                'total_estimated_revenue': total_revenue,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying opportunity pipeline: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_system_insights(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the latest System Insights reports from the ThinkingAgent.
        Returns the most recent report(s) with patterns, concerns, and opportunities.
        """
        try:
            from django.utils import timezone
            from core.models_unified_system import SelfBlog

            limit = min(arguments.get('limit', 1), 5)  # Cap at 5

            # Get System Insights reports
            reports = SelfBlog.objects.filter(
                title__icontains='System Insights'
            ).order_by('-created_at')[:limit]

            if not reports.exists():
                return {
                    'success': True,
                    'reports': [],
                    'summary': "No System Insights reports found. The ThinkingAgent may not have run yet."
                }

            report_list = []
            for r in reports:
                hours_ago = (timezone.now() - r.created_at).total_seconds() / 3600
                report_list.append({
                    'id': r.id,
                    'title': r.title,
                    'created_at': r.created_at.isoformat(),
                    'hours_ago': round(hours_ago, 1),
                    'content': r.full_text[:3000] if r.full_text else 'No content',  # Truncate for response
                    'stats_snapshot': r.stats_snapshot if hasattr(r, 'stats_snapshot') else None
                })

            # Summary for the most recent report
            latest = report_list[0]
            summary_lines = [
                f"## Latest System Insights",
                f"",
                f"**Generated:** {latest['hours_ago']} hours ago",
                f"",
                f"---",
                f""
            ]

            # Include the full content of the latest report
            if latest['content']:
                summary_lines.append(latest['content'][:2500])

            return {
                'success': True,
                'reports': report_list,
                'total_reports': SelfBlog.objects.filter(title__icontains='System Insights').count(),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting system insights: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: Phase 7 Tools - Advisors and Revenue
    # =========================================================================

    def _get_advisor_consultation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the legendary advisors for insights and wisdom.
        Returns advisor information and their recent insights.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from core.models_unified_system import Advisor, AdvisorInsight

            advisor_name = arguments.get('advisor_name')
            category = arguments.get('category', 'all')
            topic = arguments.get('topic')
            limit = min(arguments.get('limit', 10), 25)

            # Get advisors
            advisors = Advisor.objects.filter(is_active=True)

            if advisor_name:
                advisors = advisors.filter(name__icontains=advisor_name)

            if category and category != 'all':
                advisors = advisors.filter(category__icontains=category)

            advisors = advisors.order_by('-influence_score')[:limit]

            if not advisors.exists():
                return {
                    'success': True,
                    'advisors': [],
                    'summary': "No advisors found matching your criteria."
                }

            advisor_list = []
            for a in advisors:
                # Get recent insights from this advisor
                insights = AdvisorInsight.objects.filter(advisor=a).order_by('-created_at')[:3]

                advisor_info = {
                    'id': str(a.id),
                    'name': a.name,
                    'title': a.title,
                    'category': a.category,
                    'expertise': a.expertise[:200] if a.expertise else '',
                    'influence_score': a.influence_score,
                    'total_consultations': a.total_consultations,
                    'wisdom': a.wisdom if a.wisdom else {},
                    'recent_insights': [
                        {
                            'content': i.content[:200],
                            'category': i.category,
                            'confidence': i.confidence,
                            'is_actionable': i.is_actionable
                        } for i in insights
                    ]
                }
                advisor_list.append(advisor_info)

            # Build summary
            summary_lines = [
                f"## Advisor Consultation",
                f"",
                f"**Found:** {len(advisor_list)} advisor(s)",
                f""
            ]

            for a in advisor_list[:5]:
                summary_lines.append(f"### {a['name']}")
                summary_lines.append(f"*{a['title']}* (Influence: {a['influence_score']}/100)")
                summary_lines.append(f"")
                # Handle wisdom - might be string or dict
                wisdom = a.get('wisdom', {})
                if isinstance(wisdom, dict) and wisdom.get('philosophy'):
                    summary_lines.append(f"**Philosophy:** {wisdom['philosophy'][:150]}...")
                elif isinstance(wisdom, str) and wisdom:
                    summary_lines.append(f"**Philosophy:** {wisdom[:150]}...")
                if a['recent_insights']:
                    summary_lines.append(f"**Recent Insight:** {a['recent_insights'][0]['content'][:150]}...")
                summary_lines.append(f"")

            return {
                'success': True,
                'advisors': advisor_list,
                'total_advisors': Advisor.objects.filter(is_active=True).count(),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error getting advisor consultation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

