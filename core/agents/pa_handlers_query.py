"""
PersonalAssistantAgent PAQueryHandlersMixin — extracted handler methods.
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




class PAQueryHandlersMixin:
    """Mixin providing handler methods for PersonalAssistantAgent."""

    def _query_agent_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Query agent activity, learning, and performance data.
        """
        try:
            from core.models_unified_system import Agent
            from django.db.models import Count, Sum
            from django.utils import timezone
            from datetime import timedelta

            agent_name = arguments.get('agent_name')
            metric_type = arguments.get('metric_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            agents = Agent.objects.all()

            if agent_name:
                agents = agents.filter(name__icontains=agent_name)

            # Get agent stats
            agents_data = []
            for agent in agents[:limit]:
                agent_info = {
                    'name': agent.name,
                    'level': getattr(agent, 'level', 1),
                    'xp': getattr(agent, 'xp', 0),
                    'is_active': getattr(agent, 'is_active', True),
                }

                # Add learning stats if requested
                if metric_type in ['learning', 'all']:
                    agent_info['skills'] = list(getattr(agent, 'skills', []) or [])[:5]
                    agent_info['specialties'] = list(getattr(agent, 'specialties', []) or [])[:5]

                # Add activity stats if requested
                if metric_type in ['activity', 'all']:
                    # Try to get execution count
                    try:
                        from core.models_unified_system import AgentExecution
                        recent = timezone.now() - timedelta(hours=24)
                        exec_count = AgentExecution.objects.filter(
                            agent_name=agent.name,
                            created_at__gte=recent
                        ).count()
                        agent_info['executions_24h'] = exec_count
                    except Exception:
                        agent_info['executions_24h'] = 0

                agents_data.append(agent_info)

            # Sort by XP or activity
            if metric_type == 'learning':
                agents_data.sort(key=lambda x: x.get('xp', 0), reverse=True)
            elif metric_type == 'activity':
                agents_data.sort(key=lambda x: x.get('executions_24h', 0), reverse=True)

            # Build summary
            summary_lines = ["**Agent Status:**\n"]

            if not agents_data:
                summary_lines.append("No agents found matching criteria.")
            else:
                for agent in agents_data[:10]:
                    level = agent.get('level', 1)
                    xp = agent.get('xp', 0)
                    execs = agent.get('executions_24h', 0)
                    status = '🟢' if agent.get('is_active') else '🔴'
                    summary_lines.append(f"{status} **{agent['name']}** - Level {level} ({xp} XP)")
                    if execs > 0:
                        summary_lines.append(f"   📊 {execs} executions in last 24h")

            return {
                'success': True,
                'total_agents': len(agents_data),
                'agents': agents_data,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying agent data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_prediction_markets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Query Kalshi prediction market data.
        """
        try:
            from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

            query = arguments.get('query', '').lower()
            category = arguments.get('category', 'all')
            limit = arguments.get('limit', 10)

            # Fetch markets from Kalshi spider
            spider = KalshiSpider()
            markets = spider.fetch_data(max_results=100)

            # Filter to actual markets (not metadata)
            prediction_markets = [
                m for m in markets
                if m.get('data_type') == 'prediction_market'
            ]

            # Apply filters
            if query:
                prediction_markets = [
                    m for m in prediction_markets
                    if query in m.get('title', '').lower() or query in m.get('subtitle', '').lower()
                ]

            # Category filtering (Kalshi uses category field)
            category_keywords = {
                'politics': ['election', 'president', 'congress', 'senate', 'trump', 'biden'],
                'economics': ['fed', 'rate', 'inflation', 'gdp', 'recession', 'unemployment'],
                'climate': ['temperature', 'weather', 'climate', 'hurricane'],
                'tech': ['ai', 'tech', 'apple', 'google', 'tesla'],
                'sports': ['nfl', 'nba', 'mlb', 'super bowl']
            }

            if category != 'all' and category in category_keywords:
                keywords = category_keywords[category]
                prediction_markets = [
                    m for m in prediction_markets
                    if any(kw in m.get('title', '').lower() for kw in keywords)
                ]

            # Sort by volume (most active markets first)
            prediction_markets.sort(key=lambda m: -(m.get('volume') or 0))

            # Limit results
            prediction_markets = prediction_markets[:limit]

            # Build summary
            summary_lines = [f"**Prediction Markets:**\n"]

            if not prediction_markets:
                summary_lines.append("No markets found matching your query.")
            else:
                for m in prediction_markets[:10]:
                    title = m.get('title', 'Unknown')[:50]
                    yes_prob = m.get('yes_price', 0)
                    volume = m.get('volume', 0)
                    volume_str = f"${volume:,.0f}" if volume else "N/A"

                    # Format probability nicely
                    prob_str = f"{yes_prob:.0%}" if yes_prob else "N/A"

                    summary_lines.append(f"📊 **{title}...**")
                    summary_lines.append(f"   Yes: {prob_str} | Volume: {volume_str}")
                    summary_lines.append("")

            return {
                'success': True,
                'markets': prediction_markets,
                'total_found': len(prediction_markets),
                'query': query,
                'category': category,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying prediction markets: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 578: Phase 3 Tool Handlers
    # =========================================================================

    def _query_arbitrage(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Find sports betting arbitrage opportunities.
        """
        try:
            from core.agents.markets.arbitrage_detector import ArbitrageDetector

            sport = arguments.get('sport', 'all')
            min_profit = arguments.get('min_profit', 0.5)
            limit = arguments.get('limit', 10)

            # Use ArbitrageDetector agent
            detector = ArbitrageDetector()

            # Execute detection
            # Session 739: Pass spider_context to sub-agents for real intelligence
            result = detector.execute(
                task=f"Find arbitrage opportunities for {sport} with minimum {min_profit}% profit",
                context={'sport': sport, 'min_profit': min_profit, 'limit': limit},
                scifi_context=getattr(self, '_current_scifi_context', {}),
                spider_context=getattr(self, '_current_spider_context', {})
            )

            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                result_dict = {'output': str(result)}

            # Extract opportunities from result
            opportunities = result_dict.get('opportunities', [])
            content = result_dict.get('content', '')

            # Build summary
            summary_lines = ["**Arbitrage Opportunities:**\n"]

            if not opportunities and not content:
                summary_lines.append("No arbitrage opportunities found at this time.")
                summary_lines.append("\nArbitrage opportunities are rare - they occur when odds")
                summary_lines.append("across bookmakers create guaranteed profit situations.")
            else:
                if opportunities:
                    for opp in opportunities[:limit]:
                        profit = opp.get('profit_percentage', 0)
                        event = opp.get('event', 'Unknown event')
                        summary_lines.append(f"💰 **{profit:.2f}% profit** - {event[:50]}")
                elif content:
                    summary_lines.append(content[:500])

            return {
                'success': True,
                'sport': sport,
                'min_profit': min_profit,
                'opportunities': opportunities[:limit],
                'raw_result': result_dict,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying arbitrage: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_dreams(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query agent dreams.
        """
        try:
            from core.models_unified_system import AgentDream, Agent

            agent_name = arguments.get('agent_name')
            dream_type = arguments.get('dream_type', 'all')
            limit = arguments.get('limit', 10)

            # Build query
            dreams_query = AgentDream.objects.all()

            if agent_name:
                agent = Agent.objects.filter(name__icontains=agent_name).first()
                if agent:
                    dreams_query = dreams_query.filter(agent=agent)

            if dream_type != 'all':
                dreams_query = dreams_query.filter(dream_type=dream_type)

            # Get recent dreams
            dreams = dreams_query.order_by('-dreamed_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Agent Dreams:**\n"]

            if not dreams:
                summary_lines.append("No dreams found.")
                summary_lines.append("\nDreams are generated when agents have idle time to be creative.")
            else:
                for dream in dreams:
                    results.append({
                        'id': str(dream.id),
                        'agent': dream.agent.name if dream.agent else 'Unknown',
                        'dream_type': dream.dream_type,
                        'title': dream.title if hasattr(dream, 'title') else 'Untitled',
                        'content': dream.content[:200] if dream.content else '',
                        'actionability': getattr(dream, 'actionability_score', 0),
                        'dreamed_at': dream.dreamed_at.isoformat() if dream.dreamed_at else None
                    })

                    emoji = '💡' if getattr(dream, 'actionability_score', 0) > 0.7 else '💭'
                    agent_name_display = dream.agent.name if dream.agent else 'Unknown'
                    title = getattr(dream, 'title', dream.content[:50] if dream.content else 'Untitled')
                    summary_lines.append(f"{emoji} **{agent_name_display}**: {title[:60]}...")

            return {
                'success': True,
                'dreams': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying dreams: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_conversations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Query agent-to-agent conversations.
        """
        try:
            from core.models_unified_system import HiveMindSession, Agent

            topic = arguments.get('topic', '')
            agent_name = arguments.get('agent_name')
            limit = arguments.get('limit', 10)

            # Query HiveMindSession with conversation mode
            conversations_query = HiveMindSession.objects.filter(
                session_mode='conversation'
            )

            if topic:
                conversations_query = conversations_query.filter(conversation_topic__icontains=topic)

            if agent_name:
                agent = Agent.objects.filter(name__icontains=agent_name).first()
                if agent:
                    conversations_query = conversations_query.filter(participant_ids__contains=[str(agent.id)])

            conversations = conversations_query.order_by('-created_at')[:limit]

            # Build results
            results = []
            summary_lines = ["**Agent Conversations:**\n"]

            if not conversations:
                summary_lines.append("No recent conversations found.")
                summary_lines.append("\nConversations happen during agent collaboration and knowledge sharing.")
            else:
                for conv in conversations:
                    participant_ids = getattr(conv, 'participant_ids', []) or []
                    results.append({
                        'id': str(conv.id),
                        'topic': conv.conversation_topic or conv.question or 'Untitled',
                        'participant_ids': participant_ids[:5],
                        'status': conv.status,
                        'created_at': conv.created_at.isoformat(),
                        'synthesis': (conv.synthesis_summary or conv.synthesis or '')[:200]
                    })

                    participant_str = f"{len(participant_ids)} agents" if participant_ids else 'Unknown'
                    topic_display = (conv.conversation_topic or conv.question or 'Untitled')[:40]
                    summary_lines.append(f"💬 **{topic_display}...**")
                    summary_lines.append(f"   Participants: {participant_str}")

            return {
                'success': True,
                'conversations': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error querying conversations: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== SESSION 579: PHASE 5 TOOLS ====================

    def _query_tracked_concerns(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the system's tracked concerns and their resolution status.
        Returns concerns identified by ThinkingAgent with status, severity, and resolution.
        """
        try:
            from core.models_unified_system import TrackedConcern

            status_filter = arguments.get('status', 'all')
            severity_filter = arguments.get('severity', 'all')
            limit = min(arguments.get('limit', 20), 50)  # Cap at 50

            # Build query
            concerns = TrackedConcern.objects.all()

            if status_filter != 'all':
                concerns = concerns.filter(status=status_filter)

            if severity_filter != 'all':
                concerns = concerns.filter(severity=severity_filter)

            # Order by severity (high first), then by updated_at
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            concerns = concerns.order_by('-updated_at')[:limit]

            # Build summary
            status_counts = {
                'in_progress': TrackedConcern.objects.filter(status='in_progress').count(),
                'resolved': TrackedConcern.objects.filter(status='resolved').count(),
                'pending': TrackedConcern.objects.filter(status='pending').count()
            }

            concern_list = []
            for c in concerns:
                status_icon = '✅' if c.status == 'resolved' else '🔄' if c.status == 'in_progress' else '⏳'
                # Get action count (ManyToMany)
                actions_count = c.actions_taken.count()
                concern_list.append({
                    'id': c.id,
                    'status_icon': status_icon,
                    'status': c.status,
                    'severity': c.severity,
                    'category': c.category,
                    'concern': c.concern_text[:200] + ('...' if len(c.concern_text) > 200 else ''),
                    'times_detected': c.times_detected,
                    'verification_metric': c.verification_metric or 'manual',
                    'resolution_notes': c.resolution_notes[:150] if c.resolution_notes else None,
                    'actions_taken_count': actions_count,
                    'updated_at': c.updated_at.isoformat()
                })

            # Build summary message
            summary_lines = [
                f"## Tracked Concerns Overview",
                f"",
                f"**Total:** {sum(status_counts.values())} concerns",
                f"- 🔄 In Progress: {status_counts['in_progress']}",
                f"- ✅ Resolved: {status_counts['resolved']}",
                f"- ⏳ Pending: {status_counts['pending']}",
                f""
            ]

            if status_counts['in_progress'] > 0:
                summary_lines.append("### Active Concerns (In Progress)")
                in_progress = [c for c in concern_list if c['status'] == 'in_progress']
                for c in in_progress[:5]:
                    summary_lines.append(f"- **[{c['severity'].upper()}]** {c['concern'][:80]}...")

            return {
                'success': True,
                'status_counts': status_counts,
                'concerns': concern_list,
                'summary': '\n'.join(summary_lines),
                'filters_applied': {
                    'status': status_filter,
                    'severity': severity_filter,
                    'limit': limit
                }
            }

        except Exception as e:
            logger.error(f"Error querying tracked concerns: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _query_revenue_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query revenue metrics, earnings, and financial performance.
        Returns revenue by source, status, and time period.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Sum, Count, Avg
            from decimal import Decimal
            from core.models_unified_system import Revenue, Opportunity

            time_period = arguments.get('time_period', '30d')
            source_type = arguments.get('source_type')
            status = arguments.get('status', 'all')
            include_opportunities = arguments.get('include_opportunities', True)

            # Calculate cutoff
            now = timezone.now()
            period_map = {
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                '90d': timedelta(days=90),
                'all': timedelta(days=3650)  # ~10 years
            }
            cutoff = now - period_map.get(time_period, timedelta(days=30))

            # Query revenue
            revenue_qs = Revenue.objects.filter(created_at__gte=cutoff)

            if source_type:
                revenue_qs = revenue_qs.filter(source_type__icontains=source_type)

            if status and status != 'all':
                revenue_qs = revenue_qs.filter(status=status)

            # Aggregate metrics
            total_revenue = revenue_qs.aggregate(
                total=Sum('amount'),
                count=Count('id'),
                avg=Avg('amount')
            )

            # By status
            by_status = revenue_qs.values('status').annotate(
                total=Sum('amount'),
                count=Count('id')
            )

            # By source type
            by_source = revenue_qs.values('source_type').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:10]

            # Recent transactions
            recent = revenue_qs.order_by('-created_at')[:5]
            recent_list = [
                {
                    'amount': float(r.amount),
                    'source_type': r.source_type,
                    'status': r.status,
                    'description': r.description[:100] if r.description else '',
                    'created_at': r.created_at.isoformat()
                } for r in recent
            ]

            results = {
                'success': True,
                'time_period': time_period,
                'total_revenue': float(total_revenue['total'] or 0),
                'transaction_count': total_revenue['count'] or 0,
                'average_transaction': float(total_revenue['avg'] or 0),
                'by_status': {s['status']: {'total': float(s['total'] or 0), 'count': s['count']} for s in by_status},
                'by_source': {s['source_type']: {'total': float(s['total'] or 0), 'count': s['count']} for s in by_source},
                'recent_transactions': recent_list
            }

            # Include opportunities if requested
            if include_opportunities:
                opp_qs = Opportunity.objects.filter(
                    created_at__gte=cutoff,
                    status='active'
                )
                potential = opp_qs.aggregate(
                    total=Sum('potential_revenue'),
                    count=Count('id')
                )
                results['opportunities'] = {
                    'potential_revenue': float(potential['total'] or 0),
                    'active_count': potential['count'] or 0
                }

            # Build summary
            summary_lines = [
                f"## Revenue Metrics ({time_period})",
                f"",
                f"**Total Revenue:** ${results['total_revenue']:,.2f}",
                f"**Transactions:** {results['transaction_count']}",
                f"**Average:** ${results['average_transaction']:,.2f}",
                f""
            ]

            if results.get('by_status'):
                summary_lines.append("### By Status")
                for status, data in results['by_status'].items():
                    summary_lines.append(f"- **{status.title()}:** ${data['total']:,.2f} ({data['count']} transactions)")
                summary_lines.append("")

            if results.get('by_source'):
                summary_lines.append("### By Source")
                for source, data in list(results['by_source'].items())[:5]:
                    summary_lines.append(f"- **{source.title()}:** ${data['total']:,.2f}")
                summary_lines.append("")

            if include_opportunities and results.get('opportunities'):
                opp = results['opportunities']
                summary_lines.append("### Pipeline")
                summary_lines.append(f"- **Active Opportunities:** {opp['active_count']}")
                summary_lines.append(f"- **Potential Revenue:** ${opp['potential_revenue']:,.2f}")

            results['summary'] = '\n'.join(summary_lines)

            return results

        except Exception as e:
            logger.error(f"Error querying revenue metrics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 580: Phase 8 Tools - High-Impact Expansion
    # =========================================================================

    def _query_learning_progress(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query agent learning progress, evolution metrics, and training status.
        """
        try:
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count, Avg

            agent_name = arguments.get('agent_name')
            metric_type = arguments.get('metric_type', 'all')
            time_period = arguments.get('time_period', '7d')

            # Calculate cutoff
            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            results = {'success': True, 'time_period': time_period}

            # Get learning stats from AgentLearning model
            if metric_type in ['learning_stats', 'all']:
                from core.models_unified_system import AgentLearning
                learning_qs = AgentLearning.objects.filter(created_at__gte=cutoff)
                if agent_name:
                    # Filter by teacher or student agent
                    from django.db.models import Q
                    learning_qs = learning_qs.filter(
                        Q(teacher_agent__name__icontains=agent_name) |
                        Q(student_agent__name__icontains=agent_name)
                    )

                stats = learning_qs.aggregate(
                    total=Count('id'),
                    avg_effectiveness=Avg('effectiveness_after')
                )
                results['learning_stats'] = {
                    'total_learnings': stats['total'] or 0,
                    'avg_effectiveness': round(float(stats['avg_effectiveness'] or 0), 2)
                }

            # Get evolution metrics
            if metric_type in ['evolution', 'all']:
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True)
                if agent_name:
                    agents = agents.filter(name__icontains=agent_name)

                agent_data = []
                for agent in agents[:10]:
                    agent_data.append({
                        'name': agent.name,
                        'specialization': agent.specialization,
                        'effectiveness_score': agent.effectiveness_score,
                        'total_executions': agent.total_executions
                    })
                results['evolution'] = agent_data

            # Get recent interactions
            if metric_type in ['interactions', 'all']:
                from core.models_unified_system import AgentExecution
                exec_qs = AgentExecution.objects.filter(created_at__gte=cutoff)
                if agent_name:
                    exec_qs = exec_qs.filter(agent__name__icontains=agent_name)

                exec_stats = exec_qs.aggregate(
                    total=Count('id'),
                    avg_time=Avg('execution_time_ms')
                )
                results['interactions'] = {
                    'total_executions': exec_stats['total'] or 0,
                    'avg_execution_time_ms': round(float(exec_stats['avg_time'] or 0), 0)
                }

            # Build summary
            summary_lines = [f"## Learning Progress ({time_period})", ""]
            if results.get('learning_stats'):
                ls = results['learning_stats']
                summary_lines.append(f"**Total Learnings:** {ls['total_learnings']}")
                summary_lines.append(f"**Avg Effectiveness:** {ls['avg_effectiveness']}")
            if results.get('interactions'):
                i = results['interactions']
                summary_lines.append(f"**Executions:** {i['total_executions']}")
            if results.get('evolution'):
                summary_lines.append(f"**Active Agents:** {len(results['evolution'])}")

            results['summary'] = '\n'.join(summary_lines)
            return results

        except Exception as e:
            logger.error(f"Error querying learning progress: {e}")
            return {'success': False, 'error': str(e)}

    def _query_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query system analytics, usage metrics, and performance data.
        """
        try:
            import requests
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count, Sum, Avg

            report_type = arguments.get('report_type', 'overview')
            time_period = arguments.get('time_period', '7d')
            include_trends = arguments.get('include_trends', True)

            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30), '90d': timedelta(days=90)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            results = {'success': True, 'report_type': report_type, 'time_period': time_period}

            if report_type in ['overview', 'all']:
                # Try internal API first
                try:
                    response = requests.get('http://localhost:8000/api/analytics/overview/', timeout=10)
                    if response.status_code == 200:
                        results['overview'] = response.json()
                except:
                    pass

                # Fallback to direct DB queries
                from core.models_unified_system import Agent, AgentExecution

                results['overview'] = results.get('overview', {})
                results['overview'].update({
                    'total_agents': Agent.objects.filter(is_active=True).count(),
                    'executions': AgentExecution.objects.filter(created_at__gte=cutoff).count()
                })

            if report_type in ['agents', 'all']:
                from core.models_unified_system import Agent, AgentExecution
                exec_stats = AgentExecution.objects.filter(created_at__gte=cutoff).values('agent__name').annotate(
                    count=Count('id'),
                    avg_time=Avg('execution_time_ms')
                ).order_by('-count')[:10]

                results['agent_stats'] = [
                    {'agent': s['agent__name'], 'executions': s['count'], 'avg_time_ms': round(s['avg_time'] or 0, 0)}
                    for s in exec_stats
                ]

            if report_type in ['costs', 'all']:
                try:
                    response = requests.get('http://localhost:8000/api/analytics/cost-breakdown/', timeout=10)
                    if response.status_code == 200:
                        results['costs'] = response.json()
                except:
                    results['costs'] = {'message': 'Cost data not available'}

            # Build summary
            summary_lines = [f"## Analytics Report ({time_period})", ""]
            if results.get('overview'):
                o = results['overview']
                summary_lines.append(f"**Agents:** {o.get('total_agents', 'N/A')}")
                summary_lines.append(f"**Executions:** {o.get('executions', 'N/A')}")
                summary_lines.append(f"**Content:** {o.get('content_generated', 'N/A')}")

            results['summary'] = '\n'.join(summary_lines)
            return results

        except Exception as e:
            logger.error(f"Error querying analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _query_legal(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query legal case files, litigation documents, and case context.
        """
        try:
            import requests
            action = arguments.get('action', 'list_cases')
            base_url = 'http://localhost:8000/api/legal'

            if action == 'list_cases':
                try:
                    response = requests.get(f'{base_url}/cases/', timeout=10)
                    if response.status_code == 200:
                        cases = response.json()
                        case_list = cases if isinstance(cases, list) else cases.get('cases', [])
                        return {
                            'success': True,
                            'cases': case_list[:20],
                            'summary': f"Found {len(case_list)} cases"
                        }
                except:
                    pass
                # Fallback
                from core.models_legal import CaseProfile
                cases = CaseProfile.objects.all().order_by('-created_at')[:20]
                return {
                    'success': True,
                    'cases': [{'id': str(c.id), 'case_title': c.case_title, 'case_number': c.case_number, 'status': c.status} for c in cases],
                    'summary': f"Found {CaseProfile.objects.count()} cases"
                }

            elif action == 'get_case':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/cases/{case_id}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'case': response.json()}
                    except:
                        pass
                return {'success': False, 'error': 'Case not found'}

            elif action == 'active_case':
                try:
                    response = requests.get(f'{base_url}/active-case/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'active_case': response.json()}
                except:
                    pass
                return {'success': True, 'active_case': None, 'message': 'No active case'}

            elif action == 'list_case_files':
                try:
                    response = requests.get(f'{base_url}/case-files/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'files': response.json()}
                except:
                    pass
                return {'success': True, 'files': [], 'message': 'No case files'}

            elif action == 'get_context':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/cases/{case_id}/context/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'context': response.json()}
                    except:
                        pass
                return {'success': True, 'context': {'message': 'Context not available'}}

            elif action == 'list_documents':
                case_id = arguments.get('case_id')
                if case_id:
                    try:
                        response = requests.get(f'{base_url}/litigation/{case_id}/documents/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'documents': response.json()}
                    except:
                        pass
                return {'success': True, 'documents': []}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error querying legal: {e}")
            return {'success': False, 'error': str(e)}

    def _query_live_odds(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed live odds from multiple sportsbooks.
        """
        try:
            import requests
            sport = arguments.get('sport', 'nfl')
            market_type = arguments.get('market_type', 'all')
            team = arguments.get('team', '')

            # Try API first
            try:
                params = {'sport': sport}
                if market_type != 'all':
                    params['markets'] = market_type
                response = requests.get(
                    'http://localhost:8000/api/v1/sports/live-odds/',
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    odds_list = data if isinstance(data, list) else data.get('odds', [])

                    # Filter by team if specified
                    if team:
                        team_lower = team.lower()
                        odds_list = [o for o in odds_list if team_lower in str(o).lower()]

                    return {
                        'success': True,
                        'odds': odds_list[:20],
                        'sport': sport,
                        'market_type': market_type,
                        'total': len(odds_list),
                        'summary': f"Found {len(odds_list)} {sport.upper()} odds"
                    }
            except:
                pass

            # Fallback to SportsOddsAnalyst
            result = self.router.route(
                agent_name='SportsOddsAnalyst',
                task=f"Get live {market_type} odds for {sport}" + (f" filtered by {team}" if team else ""),
                context={'sport': sport, 'market_type': market_type, 'team': team}
            )

            return {
                'success': result.success,
                'odds': result.data.get('odds', []) if result.success else [],
                'summary': result.message if result.success else result.error
            }

        except Exception as e:
            logger.error(f"Error querying live odds: {e}")
            return {'success': False, 'error': str(e)}

    def _query_games(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query sports games - today's matchups, trending games, analytics.
        """
        try:
            import requests
            action = arguments.get('action', 'today')
            sport = arguments.get('sport', 'all')
            game_id = arguments.get('game_id', '')
            team = arguments.get('team', '')

            base_url = 'http://localhost:8000/api/v1/sports'

            if action == 'today':
                try:
                    response = requests.get(f'{base_url}/games/', params={'today': 'true', 'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:20],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games today"
                        }
                except:
                    pass

            elif action == 'trending':
                try:
                    response = requests.get(f'{base_url}/games/trending/', params={'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'games': response.json(), 'summary': 'Trending games retrieved'}
                except:
                    pass

            elif action == 'this_week':
                try:
                    response = requests.get(f'{base_url}/games/', params={'this_week': 'true', 'sport': sport}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:30],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games this week"
                        }
                except:
                    pass

            elif action == 'analytics' and game_id:
                try:
                    response = requests.get(f'{base_url}/games/{game_id}/analytics/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'analytics': response.json(), 'summary': 'Game analytics retrieved'}
                except:
                    pass

            elif action == 'search' and team:
                try:
                    response = requests.get(f'{base_url}/games/', params={'search': team}, timeout=10)
                    if response.status_code == 200:
                        games = response.json()
                        game_list = games if isinstance(games, list) else games.get('results', games.get('games', []))
                        return {
                            'success': True,
                            'games': game_list[:20],
                            'total': len(game_list),
                            'summary': f"Found {len(game_list)} games matching '{team}'"
                        }
                except:
                    pass

            # Fallback: use sports summary
            try:
                response = requests.get(f'{base_url}/summary/', timeout=10)
                if response.status_code == 200:
                    return {'success': True, 'data': response.json(), 'summary': 'Sports summary retrieved'}
            except:
                pass

            return {'success': True, 'games': [], 'summary': 'No games data available'}

        except Exception as e:
            logger.error(f"Error querying games: {e}")
            return {'success': False, 'error': str(e)}

    def _query_line_movements(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track betting line movements and identify sharp money.
        """
        try:
            import requests
            action = arguments.get('action', 'movers')
            game_id = arguments.get('game_id', '')
            sport = arguments.get('sport', 'all')
            min_movement = arguments.get('min_movement', 0.5)

            base_url = 'http://localhost:8000/api/v1/betting'

            if action == 'game' and game_id:
                try:
                    response = requests.get(f'{base_url}/line-movement/{game_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'movements': response.json(),
                            'game_id': game_id,
                            'summary': f'Line movement history for game {game_id}'
                        }
                except:
                    pass

            elif action == 'movers':
                try:
                    params = {'min_movement': min_movement}
                    if sport != 'all':
                        params['sport'] = sport
                    response = requests.get(f'{base_url}/movers/', params=params, timeout=10)
                    if response.status_code == 200:
                        movers = response.json()
                        mover_list = movers if isinstance(movers, list) else movers.get('movers', [])
                        return {
                            'success': True,
                            'movers': mover_list[:15],
                            'total': len(mover_list),
                            'summary': f"Found {len(mover_list)} games with significant line movement"
                        }
                except:
                    pass

            elif action == 'sharp':
                try:
                    response = requests.get(f'{base_url}/movers/', params={'sharp': 'true'}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'sharp_action': data,
                            'summary': 'Sharp money indicators retrieved'
                        }
                except:
                    pass

            return {'success': True, 'movements': [], 'summary': 'No line movement data available'}

        except Exception as e:
            logger.error(f"Error querying line movements: {e}")
            return {'success': False, 'error': str(e)}

    def _query_futures(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get futures betting odds for championships, MVPs, etc.
        """
        try:
            import requests
            sport = arguments.get('sport', 'nfl')
            market = arguments.get('market', 'championship')

            try:
                params = {'sport': sport, 'market': market}
                response = requests.get(
                    'http://localhost:8000/api/v1/betting/futures/',
                    params=params,
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    futures = data if isinstance(data, list) else data.get('futures', data.get('odds', []))
                    return {
                        'success': True,
                        'futures': futures[:25],
                        'sport': sport,
                        'market': market,
                        'total': len(futures),
                        'summary': f"Found {len(futures)} {sport.upper()} {market} futures odds"
                    }
            except:
                pass

            # Fallback: delegate to SportsOddsAnalyst
            result = self.router.route(
                agent_name='SportsOddsAnalyst',
                task=f"Get {market} futures odds for {sport}",
                context={'sport': sport, 'market': market, 'futures': True}
            )

            return {
                'success': result.success,
                'futures': result.data.get('futures', []) if result.success else [],
                'summary': result.message if result.success else result.error
            }

        except Exception as e:
            logger.error(f"Error querying futures: {e}")
            return {'success': False, 'error': str(e)}

    def _query_player_props(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get player prop betting odds for specific games.
        """
        try:
            import requests
            event_id = arguments.get('event_id', '')
            player = arguments.get('player', '')
            prop_type = arguments.get('prop_type', 'all')

            # If we have an event_id, use the props endpoint
            if event_id:
                try:
                    response = requests.get(
                        f'http://localhost:8000/api/v1/sports/events/{event_id}/props/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        props = response.json()
                        prop_list = props if isinstance(props, list) else props.get('props', [])

                        # Filter by player if specified
                        if player:
                            player_lower = player.lower()
                            prop_list = [p for p in prop_list if player_lower in str(p).lower()]

                        # Filter by prop type if specified
                        if prop_type != 'all':
                            prop_list = [p for p in prop_list if prop_type.lower() in str(p).lower()]

                        return {
                            'success': True,
                            'props': prop_list[:30],
                            'event_id': event_id,
                            'total': len(prop_list),
                            'summary': f"Found {len(prop_list)} player props"
                        }
                except:
                    pass

            # Fallback: delegate to SportsOddsAnalyst for player search
            if player:
                result = self.router.route(
                    agent_name='SportsOddsAnalyst',
                    task=f"Get {prop_type} props for player {player}",
                    context={'player': player, 'prop_type': prop_type}
                )

                return {
                    'success': result.success,
                    'props': result.data.get('props', []) if result.success else [],
                    'summary': result.message if result.success else result.error
                }

            return {
                'success': True,
                'props': [],
                'summary': 'Provide an event_id or player name to get props'
            }

        except Exception as e:
            logger.error(f"Error querying player props: {e}")
            return {'success': False, 'error': str(e)}

    def _query_betting_recommendations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-generated betting recommendations and picks.
        """
        try:
            import requests
            action = arguments.get('action', 'list')
            sport = arguments.get('sport', 'all')
            min_confidence = arguments.get('min_confidence', 60)
            limit = arguments.get('limit', 10)

            base_url = 'http://localhost:8000/api/v1/sports/recommendations'

            if action == 'list':
                try:
                    params = {'limit': limit}
                    if sport != 'all':
                        params['sport'] = sport
                    if min_confidence > 0:
                        params['min_confidence'] = min_confidence
                    response = requests.get(f'{base_url}/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'recommendations': recs[:limit],
                            'total': len(recs),
                            'summary': f"Found {len(recs)} betting recommendations"
                        }
                except:
                    pass

            elif action == 'generate':
                try:
                    response = requests.post(f'{base_url}/generate/', json={'sport': sport}, timeout=30)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'recommendations': response.json(),
                            'summary': 'New recommendations generated'
                        }
                except:
                    pass

            elif action == 'top_picks':
                try:
                    response = requests.get(f'{base_url}/', params={'ordering': '-confidence', 'limit': 5}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'top_picks': recs[:5],
                            'summary': f"Top {len(recs[:5])} high-confidence picks"
                        }
                except:
                    pass

            elif action == 'history':
                try:
                    response = requests.get(f'{base_url}/', params={'status': 'completed', 'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        recs = data if isinstance(data, list) else data.get('results', data.get('recommendations', []))
                        return {
                            'success': True,
                            'history': recs[:limit],
                            'summary': f"Found {len(recs)} past recommendations"
                        }
                except:
                    pass

            # Fallback: return graceful message when no recommendations available
            return {
                'success': True,
                'recommendations': [],
                'summary': 'No betting recommendations available at this time. Try during active game times.'
            }

        except Exception as e:
            logger.error(f"Error querying betting recommendations: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 11: Notification Tools (Session 582) =====

    def _query_system_health(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Get system health and status information.
        """
        try:
            import requests

            subsystem = arguments.get('subsystem', 'unified')
            base_url = 'http://localhost:8000'

            results = {}

            if subsystem in ['unified', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/health/', timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        results['unified'] = data.get('data', data)
                except:
                    results['unified'] = {'status': 'unknown', 'error': 'API unavailable'}

            if subsystem in ['content_studio', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/content-studio/', timeout=10)
                    if response.status_code == 200:
                        results['content_studio'] = response.json()
                except:
                    results['content_studio'] = {'status': 'unknown'}

            if subsystem in ['narrative_drift', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/narrative-drift/', timeout=10)
                    if response.status_code == 200:
                        results['narrative_drift'] = response.json()
                except:
                    results['narrative_drift'] = {'status': 'unknown'}

            if subsystem in ['market_intelligence', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/market-intelligence/', timeout=10)
                    if response.status_code == 200:
                        results['market_intelligence'] = response.json()
                except:
                    results['market_intelligence'] = {'status': 'unknown'}

            if subsystem in ['ml_scoring', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/monitoring/ml-scoring/', timeout=10)
                    if response.status_code == 200:
                        results['ml_scoring'] = response.json()
                except:
                    results['ml_scoring'] = {'status': 'unknown'}

            if subsystem in ['agents', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/v1/agents/health/', timeout=10)
                    if response.status_code == 200:
                        results['agents'] = response.json()
                    else:
                        raise Exception('API error')
                except:
                    # Fallback: count agents
                    from core.models_unified_system import Agent
                    results['agents'] = {
                        'total': Agent.objects.count(),
                        'active': Agent.objects.filter(is_active=True).count(),
                        'status': 'ok'
                    }

            if subsystem in ['spiders', 'all']:
                try:
                    response = requests.get(f'{base_url}/api/spider-health/summary/', timeout=10)
                    if response.status_code == 200:
                        results['spiders'] = response.json()
                    else:
                        raise Exception('API error')
                except:
                    # Fallback: count spiders
                    from ai_core.spiders.spider_registry import SpiderRegistry
                    registry = SpiderRegistry()
                    results['spiders'] = {
                        'total': registry.get_spider_count(),
                        'status': 'ok'
                    }

            # Generate summary
            healthy_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get('status') != 'error')
            total_count = len(results)

            return {
                'success': True,
                'health': results,
                'subsystems_checked': list(results.keys()),
                'summary': f"Checked {total_count} subsystem(s): {healthy_count} healthy"
            }

        except Exception as e:
            logger.error(f"Error querying system health: {e}")
            return {'success': False, 'error': str(e)}

    def _query_activity_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Get activity streams, ROI metrics, and provenance data.
        """
        try:
            import requests

            metric_type = arguments.get('metric_type', 'activity')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if metric_type == 'activity':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/activity/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        activities = data.get('activities', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'activities': activities[:limit] if isinstance(activities, list) else activities,
                            'summary': f"Found {len(activities) if isinstance(activities, list) else 'multiple'} recent activities"
                        }
                except:
                    pass

                # Fallback: Query recent agent executions
                from core.models_unified_system import AgentExecution
                executions = AgentExecution.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'activities': [
                        {
                            'type': 'agent_execution',
                            'agent': e.agent.name if hasattr(e, 'agent') and e.agent else 'Unknown',
                            'status': e.status,
                            'created_at': e.created_at.isoformat()
                        }
                        for e in executions
                    ],
                    'summary': f"Found {len(executions)} recent agent executions"
                }

            elif metric_type == 'roi':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/roi/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'roi_metrics': data,
                            'summary': 'ROI metrics retrieved'
                        }
                except:
                    pass

                # Fallback: Basic revenue stats
                from core.models_unified_system import Revenue
                from django.db.models import Sum
                total = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
                return {
                    'success': True,
                    'roi_metrics': {
                        'total_revenue': float(total),
                        'currency': 'USD'
                    },
                    'summary': f'Total revenue: ${total:.2f}'
                }

            elif metric_type == 'provenance':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/provenance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'provenance': data,
                            'summary': 'Provenance chain retrieved'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'provenance': [],
                    'message': 'Provenance tracking available via API'
                }

            return {'success': False, 'error': f'Unknown metric type: {metric_type}'}

        except Exception as e:
            logger.error(f"Error querying activity metrics: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 14: Artifact & Review Tools (Session 583) =====

    def _query_learning(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query learning system data, patterns, and insights.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'dashboard')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/learning/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved learning dashboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {'message': 'Dashboard available via API'},
                    'summary': 'Learning dashboard endpoint available'
                }

            elif query_type == 'patterns':
                try:
                    response = requests.get(f'{base_url}/api/learning/patterns/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        patterns = data.get('patterns', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'patterns': patterns,
                            'summary': f"Found {len(patterns) if isinstance(patterns, list) else 'multiple'} patterns"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'patterns': [],
                    'summary': 'No patterns found'
                }

            elif query_type == 'insights':
                try:
                    response = requests.get(f'{base_url}/api/learning/insights/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        insights = data.get('insights', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'insights': insights,
                            'summary': f"Found {len(insights) if isinstance(insights, list) else 'multiple'} insights"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'insights': [],
                    'summary': 'No insights found'
                }

            elif query_type == 'profile':
                try:
                    response = requests.get(f'{base_url}/api/learning/profile/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'profile': response.json(),
                            'summary': 'Retrieved learning profile'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'profile': {'message': 'Profile available via API'},
                    'summary': 'Learning profile endpoint available'
                }

            elif query_type == 'progress':
                try:
                    response = requests.get(f'{base_url}/api/learning/progress/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'progress': response.json(),
                            'summary': 'Retrieved learning progress'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'progress': {'message': 'Progress available via API'},
                    'summary': 'Learning progress endpoint available'
                }

            elif query_type == 'data_flow':
                try:
                    response = requests.get(f'{base_url}/api/learning/data-flow/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'data_flow': response.json(),
                            'summary': 'Retrieved learning data flow'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'data_flow': {'message': 'Data flow available via API'},
                    'summary': 'Learning data flow endpoint available'
                }

            elif query_type == 'feed':
                try:
                    response = requests.get(f'{base_url}/api/learning/feed/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        feed = data.get('feed', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'feed': feed,
                            'summary': f"Found {len(feed) if isinstance(feed, list) else 'multiple'} feed items"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'feed': [],
                    'summary': 'No feed items found'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying learning: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 17: Portfolio & Nexus Tools (Session 583) =====

    def _query_nexus(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query the Nexus unified intelligence system.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'intelligence_data')
            insight_id = arguments.get('insight_id')
            behavior_query = arguments.get('behavior_query', '')
            base_url = 'http://localhost:8000'

            if query_type == 'intelligence_data':
                try:
                    response = requests.get(f'{base_url}/api/nexus/intelligence-data/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'intelligence': response.json(),
                            'summary': 'Retrieved unified intelligence data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'intelligence': {'message': 'Intelligence data available via API'},
                    'summary': 'Nexus intelligence endpoint available'
                }

            elif query_type == 'implement_insight':
                if not insight_id:
                    return {'success': False, 'error': 'insight_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/nexus/implement-insight/',
                        json={'insight_id': insight_id},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Insight implementation started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not implement insight'}

            elif query_type == 'investigate_behavior':
                try:
                    response = requests.post(
                        f'{base_url}/api/nexus/investigate-behavior/',
                        json={'query': behavior_query},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'investigation': response.json(),
                            'summary': 'Behavior investigation complete'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'investigation': {'message': 'Investigation available via API'},
                    'summary': 'Nexus investigation endpoint available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying nexus: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 18: Predictions & Performance Tools (Session 583) =====

    def _query_performance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Query performance metrics, predictions, and pricing optimization.
        """
        try:
            import requests

            query_type = arguments.get('query_type', 'predictions')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if query_type == 'predict':
                try:
                    response = requests.get(f'{base_url}/api/learning/predict/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'prediction': response.json(),
                            'summary': 'Retrieved performance prediction'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'prediction': {'message': 'Performance prediction available via API'},
                    'summary': 'Performance prediction endpoint available'
                }

            elif query_type == 'predictions':
                try:
                    response = requests.get(f'{base_url}/api/learning/predictions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        predictions = data.get('predictions', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'predictions': predictions,
                            'summary': f"Found {len(predictions) if isinstance(predictions, list) else 'multiple'} predictions"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found'
                }

            elif query_type == 'pricing':
                try:
                    response = requests.get(f'{base_url}/api/learning/pricing/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'pricing': response.json(),
                            'summary': 'Retrieved pricing optimization'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'pricing': {'message': 'Pricing optimization available via API'},
                    'summary': 'Pricing optimization endpoint available'
                }

            elif query_type == 'compare':
                try:
                    response = requests.get(f'{base_url}/api/learning/compare/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': 'Retrieved performance comparison'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {'message': 'Performance comparison available via API'},
                    'summary': 'Performance comparison endpoint available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying performance: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 19: Analytics Tools (Session 584) =====

    def _query_workflow_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query workflow execution analytics, performance, and trends.
        Covers 10 endpoints for comprehensive workflow analytics.
        """
        import requests

        query_type = arguments.get('query_type', 'summary')
        workflow_id = arguments.get('workflow_id')
        workflow_ids = arguments.get('workflow_ids', '')
        days = arguments.get('days', 30)
        status_filter = arguments.get('status')
        limit = arguments.get('limit', 100)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'history':
                params = {'days': days, 'limit': limit}
                if workflow_id:
                    params['workflow_id'] = workflow_id
                if status_filter:
                    params['status'] = status_filter
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/history/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'history': data.get('history', []),
                            'total': data.get('total', 0),
                            'days': data.get('days', days),
                            'summary': f"Found {data.get('total', 0)} workflow executions in last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'history': [],
                    'summary': 'No workflow execution history found'
                }

            elif query_type == 'trends':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/trends/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'trends': response.json(),
                            'summary': f'Retrieved workflow trends for last {days} days'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'trends': {'labels': [], 'datasets': []},
                    'summary': 'No workflow trends data available'
                }

            elif query_type == 'success_failure':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/success-failure/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'analysis': data,
                            'summary': f"Success/failure analysis for last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'analysis': {'success_rate': 0, 'total': 0},
                    'summary': 'No success/failure data available'
                }

            elif query_type == 'performance':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/performance/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'metrics': data.get('metrics', []),
                            'total': data.get('total', 0),
                            'summary': f"Performance metrics for {data.get('total', 0)} workflows"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'metrics': [],
                    'summary': 'No performance metrics available'
                }

            elif query_type == 'performance_comparison':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/performance-comparison/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': 'Retrieved performance comparison chart data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {'labels': [], 'datasets': []},
                    'summary': 'No comparison data available'
                }

            elif query_type == 'compare':
                if not workflow_ids:
                    return {'success': False, 'error': 'workflow_ids required for compare'}

                try:
                    response = requests.get(
                        f'{base_url}/api/workflow-analytics/compare/',
                        params={'workflow_ids': workflow_ids, 'days': days},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'comparison': response.json(),
                            'summary': f"Compared workflows: {workflow_ids}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'comparison': {},
                    'summary': 'Workflow comparison not available'
                }

            elif query_type == 'steps':
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required for steps query'}

                try:
                    response = requests.get(
                        f'{base_url}/api/workflow-analytics/steps/{workflow_id}/',
                        params={'days': days},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'step_performance': response.json(),
                            'summary': f"Step performance for workflow {workflow_id}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'step_performance': {'steps': []},
                    'summary': f'No step data for workflow {workflow_id}'
                }

            elif query_type == 'heatmap':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/heatmap/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'heatmap': response.json(),
                            'summary': f"Execution heatmap for last {days} days"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'heatmap': {'data': []},
                    'summary': 'No heatmap data available'
                }

            elif query_type == 'summary':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/summary/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'summary_data': data,
                            'summary': f"Analytics summary: {data.get('total_executions', 0)} executions, {data.get('success_rate', 0):.1f}% success rate"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'summary_data': {},
                    'summary': 'Analytics summary not available'
                }

            elif query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/workflow-analytics/dashboard/', params={'days': days}, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved full analytics dashboard data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {},
                    'summary': 'Dashboard data not available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying workflow analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _query_video_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query video analytics including character performance and lip sync.
        """
        import requests

        query_type = arguments.get('query_type', 'character_performance')
        prediction_id = arguments.get('prediction_id')
        video_url = arguments.get('video_url')
        audio_url = arguments.get('audio_url')

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'character_performance':
                try:
                    response = requests.get(f'{base_url}/api/v1/video/character-performance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'performance': data,
                            'summary': 'Retrieved character performance metrics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No character performance data available'
                }

            elif query_type == 'lip_sync':
                if not video_url or not audio_url:
                    return {'success': False, 'error': 'video_url and audio_url required for lip sync'}

                try:
                    response = requests.post(
                        f'{base_url}/api/video/lip-sync/',
                        json={'video_url': video_url, 'audio_url': audio_url},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        return {
                            'success': True,
                            'job': data,
                            'summary': f"Lip sync job started: {data.get('prediction_id', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': False,
                    'error': 'Failed to start lip sync job'
                }

            elif query_type == 'lip_sync_status':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required for status check'}

                try:
                    response = requests.get(f'{base_url}/api/video/lip-sync/status/{prediction_id}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'status': data,
                            'summary': f"Lip sync status: {data.get('status', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'status': {'status': 'unknown'},
                    'summary': f'Could not retrieve status for {prediction_id}'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying video analytics: {e}")
            return {'success': False, 'error': str(e)}

    def _query_model_analytics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query LLM model performance analytics and preferences.
        """
        import requests

        query_type = arguments.get('query_type', 'performance')
        preferences = arguments.get('preferences', {})

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'performance':
                try:
                    response = requests.get(f'{base_url}/api/v1/analytics/model-performance/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'performance': data,
                            'summary': 'Retrieved model performance analytics'
                        }
                except:
                    pass

                # Try database fallback
                try:
                    from core.models_unified_system import LLMUsage
                    from django.db.models import Avg, Sum, Count
                    from django.utils import timezone
                    from datetime import timedelta

                    thirty_days_ago = timezone.now() - timedelta(days=30)
                    stats = LLMUsage.objects.filter(
                        created_at__gte=thirty_days_ago
                    ).aggregate(
                        total_calls=Count('id'),
                        total_tokens=Sum('total_tokens'),
                        avg_latency=Avg('latency_ms')
                    )

                    return {
                        'success': True,
                        'performance': {
                            'total_calls': stats['total_calls'] or 0,
                            'total_tokens': stats['total_tokens'] or 0,
                            'avg_latency_ms': round(stats['avg_latency'] or 0, 2)
                        },
                        'summary': f"Model usage: {stats['total_calls'] or 0} calls, {stats['total_tokens'] or 0} tokens"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No model performance data available'
                }

            elif query_type == 'preferences':
                try:
                    response = requests.get(f'{base_url}/api/v1/model-preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data,
                            'summary': 'Retrieved model preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {'model': 'gpt-5-mini'},
                    'summary': 'Default model preferences'
                }

            elif query_type == 'set_preferences':
                if not preferences:
                    return {'success': False, 'error': 'preferences object required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/model-preferences/',
                        json=preferences,
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Model preferences updated'
                        }
                except:
                    pass

                return {
                    'success': False,
                    'error': 'Failed to update model preferences'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying model analytics: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 20: Collaboration & Search Tools (Session 584) =====

    def _query_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Query agent collaboration data, performance, and network.
        """
        import requests

        query_type = arguments.get('query_type', 'stats')
        agent_name = arguments.get('agent_name')
        task_type = arguments.get('task_type')
        limit = arguments.get('limit', 20)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'history':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/history/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        history = data.get('history', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'history': history,
                            'summary': f"Found {len(history) if isinstance(history, list) else 'multiple'} collaborations"
                        }
                except:
                    pass

                # Database fallback
                try:
                    from core.models_collaboration import Collaboration
                    collabs = Collaboration.objects.order_by('-created_at')[:limit]
                    history = [{
                        'id': str(c.id),
                        'requester': c.requester,
                        'target_agents': c.target_agents,
                        'status': c.status,
                        'created_at': c.created_at.isoformat()
                    } for c in collabs]
                    return {
                        'success': True,
                        'history': history,
                        'summary': f"Found {len(history)} collaborations"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'history': [],
                    'summary': 'No collaboration history found'
                }

            elif query_type == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Retrieved collaboration stats'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {'total': 0, 'success_rate': 0},
                    'summary': 'No collaboration stats available'
                }

            elif query_type == 'find_collaborator':
                params = {}
                if task_type:
                    params['task_type'] = task_type
                try:
                    response = requests.get(f'{base_url}/api/collaboration/find-collaborator/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'collaborator': data,
                            'summary': f"Best collaborator: {data.get('agent_name', 'unknown')}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'collaborator': {},
                    'summary': 'No collaborator recommendation available'
                }

            elif query_type == 'performance':
                params = {'limit': limit}
                if agent_name:
                    params['agent_name'] = agent_name
                try:
                    response = requests.get(f'{base_url}/api/collaboration/performance/', params=params, timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'performance': response.json(),
                            'summary': 'Retrieved agent performance metrics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performance': {},
                    'summary': 'No performance data available'
                }

            elif query_type == 'top_performers':
                try:
                    response = requests.get(f'{base_url}/api/collaboration/top-performers/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        performers = data.get('performers', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'performers': performers,
                            'summary': f"Top {len(performers) if isinstance(performers, list) else 'multiple'} performers"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'performers': [],
                    'summary': 'No top performers data available'
                }

            elif query_type == 'network':
                try:
                    response = requests.get(f'{base_url}/api/collective/network/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'network': response.json(),
                            'summary': 'Retrieved collaboration network'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'network': {'nodes': [], 'edges': []},
                    'summary': 'No network data available'
                }

            elif query_type == 'monitor':
                try:
                    response = requests.get(f'{base_url}/api/collective/monitor/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'monitor': response.json(),
                            'summary': 'Retrieved collaboration monitor data'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'monitor': {},
                    'summary': 'No monitor data available'
                }

            elif query_type == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/api/dashboard/collaboration/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'dashboard': response.json(),
                            'summary': 'Retrieved collaboration dashboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'dashboard': {},
                    'summary': 'No dashboard data available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying collaboration: {e}")
            return {'success': False, 'error': str(e)}

    def _query_semantic_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Perform semantic search and RAG operations.
        """
        import requests

        query_type = arguments.get('query_type', 'search')
        query = arguments.get('query', '')
        limit = arguments.get('limit', 10)

        base_url = 'http://localhost:8000'

        try:
            if query_type == 'search':
                if not query:
                    return {'success': False, 'error': 'query required for search'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/rag/semantic-search/',
                        json={'query': query, 'limit': limit},
                        timeout=15
                    )
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'results': results,
                            'summary': f"Found {len(results) if isinstance(results, list) else 'multiple'} semantic matches"
                        }
                except:
                    pass

                # Try spider semantic search fallback
                try:
                    from core.services.spider_semantic_search import get_spider_semantic_search_service
                    service = get_spider_semantic_search_service()
                    results = service.semantic_search(query, limit=limit)
                    return {
                        'success': True,
                        'results': results,
                        'summary': f"Found {len(results)} semantic matches via spider search"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'results': [],
                    'summary': 'No semantic search results'
                }

            elif query_type == 'generate':
                if not query:
                    return {'success': False, 'error': 'query required for RAG generation'}

                try:
                    response = requests.post(
                        f'{base_url}/api/v1/rag/generate/',
                        json={'query': query},
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'answer': data.get('answer', data.get('response', '')),
                            'sources': data.get('sources', []),
                            'summary': 'Generated RAG answer'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'answer': '',
                    'sources': [],
                    'summary': 'RAG generation not available'
                }

            elif query_type == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/v1/rag/stats/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'stats': data,
                            'summary': f"Embeddings: {data.get('total_embeddings', 0)}, Documents: {data.get('total_documents', 0)}"
                        }
                except:
                    pass

                # Database fallback
                try:
                    from core.models_unified_system import DocumentEmbedding, RAGDocument
                    embed_count = DocumentEmbedding.objects.count()
                    doc_count = RAGDocument.objects.count()
                    return {
                        'success': True,
                        'stats': {
                            'total_embeddings': embed_count,
                            'total_documents': doc_count
                        },
                        'summary': f"Embeddings: {embed_count}, Documents: {doc_count}"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {},
                    'summary': 'No embeddings stats available'
                }

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 21: Project & Workflow Collaboration Tools (Session 585) =====

    def _query_agent_evolution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query agent evolution, XP, levels, and abilities.
        """
        try:
            import requests
            query_type = arguments.get('query_type', 'overview')
            limit = arguments.get('limit', 10)
            base_url = 'http://localhost:8000/api/agent-evolution'

            if query_type == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'overview': data,
                            'summary': f"Evolution overview retrieved"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentEvolution
                evolutions = AgentEvolution.objects.all()[:limit]
                return {
                    'success': True,
                    'evolutions': [
                        {
                            'agent': e.agent.name if e.agent else 'Unknown',
                            'level': e.current_level,
                            'xp': e.total_xp
                        }
                        for e in evolutions
                    ],
                    'total': AgentEvolution.objects.count(),
                    'summary': f"Found {AgentEvolution.objects.count()} agent evolutions"
                }

            elif query_type == 'agent_detail':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'evolution': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve agent evolution'}

            elif query_type == 'leaderboard':
                try:
                    response = requests.get(f'{base_url}/leaderboard/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        leaders = data if isinstance(data, list) else data.get('leaderboard', [])
                        return {
                            'success': True,
                            'leaderboard': leaders[:limit],
                            'summary': f"Top {min(limit, len(leaders))} agents by XP"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentEvolution
                leaders = AgentEvolution.objects.order_by('-total_xp')[:limit]
                return {
                    'success': True,
                    'leaderboard': [
                        {
                            'rank': i + 1,
                            'agent': e.agent.name if e.agent else 'Unknown',
                            'level': e.current_level,
                            'xp': e.total_xp
                        }
                        for i, e in enumerate(leaders)
                    ],
                    'summary': f"Top {leaders.count()} agents by XP"
                }

            elif query_type == 'abilities':
                try:
                    response = requests.get(f'{base_url}/abilities/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        abilities = data if isinstance(data, list) else data.get('abilities', [])
                        return {
                            'success': True,
                            'abilities': abilities[:20],
                            'total': len(abilities),
                            'summary': f"Found {len(abilities)} available abilities"
                        }
                except:
                    pass
                return {'success': True, 'abilities': [], 'summary': 'No abilities found'}

            elif query_type == 'xp_gains':
                try:
                    response = requests.get(f'{base_url}/xp-gains/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        gains = data if isinstance(data, list) else data.get('xp_gains', [])
                        return {
                            'success': True,
                            'xp_gains': gains[:limit],
                            'summary': f"Found {len(gains)} recent XP gains"
                        }
                except:
                    pass
                return {'success': True, 'xp_gains': [], 'summary': 'No XP gains found'}

            elif query_type == 'award_xp':
                agent_id = arguments.get('agent_id')
                xp_amount = arguments.get('xp_amount', 10)
                reason = arguments.get('reason', 'Manual award')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/award-xp/',
                        json={'xp': xp_amount, 'reason': reason},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': f'Awarded {xp_amount} XP' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'unlock_ability':
                agent_id = arguments.get('agent_id')
                ability_id = arguments.get('ability_id')
                if not agent_id or not ability_id:
                    return {'success': False, 'error': 'agent_id and ability_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/unlock/{ability_id}/',
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Ability unlocked' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying agent evolution: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 23: Voice Marketplace & Agent Relationships Tools (Session 586) =====

    def _query_agent_relationships(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Query agent relationships, alliances, and rivalries."""
        try:
            import requests
            query_type = arguments.get('query_type')
            base_url = 'http://localhost:8000/api/agent-relationships'

            if query_type == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'relationships': data,
                            'summary': f"Agent relationships overview"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import AgentRelationship
                relationships = AgentRelationship.objects.all()[:20]
                return {
                    'success': True,
                    'relationships': [
                        {
                            'id': str(r.id),
                            'agent_from': r.agent_from.name if r.agent_from else 'Unknown',
                            'agent_to': r.agent_to.name if r.agent_to else 'Unknown',
                            'type': r.relationship_type,
                            'strength': r.strength
                        }
                        for r in relationships
                    ],
                    'total': AgentRelationship.objects.count(),
                    'summary': f"Found {relationships.count()} relationships"
                }

            elif query_type == 'agent_detail':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'relationships': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve agent relationships'}

            elif query_type == 'create':
                agent_a_id = arguments.get('agent_a_id')
                agent_b_id = arguments.get('agent_b_id')
                rel_type = arguments.get('relationship_type', 'peer')
                if not agent_a_id or not agent_b_id:
                    return {'success': False, 'error': 'agent_a_id and agent_b_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/create/',
                        json={
                            'agent_a_id': agent_a_id,
                            'agent_b_id': agent_b_id,
                            'relationship_type': rel_type
                        },
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'relationship': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Relationship created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'interact':
                relationship_id = arguments.get('relationship_id')
                if not relationship_id:
                    return {'success': False, 'error': 'relationship_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/relationship/{relationship_id}/interact/',
                        json=arguments,
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Interaction recorded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'events':
                relationship_id = arguments.get('relationship_id')
                if not relationship_id:
                    return {'success': False, 'error': 'relationship_id required'}
                try:
                    response = requests.get(
                        f'{base_url}/relationship/{relationship_id}/events/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'events': response.json()}
                except:
                    pass
                return {'success': True, 'events': []}

            elif query_type == 'auto_generate':
                try:
                    response = requests.post(f'{base_url}/auto-generate/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Relationships auto-generated' if response.status_code == 200 else response.text,
                        'result': response.json() if response.status_code == 200 else None
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_detail':
                alliance_id = arguments.get('alliance_id')
                if not alliance_id:
                    return {'success': False, 'error': 'alliance_id required'}
                try:
                    response = requests.get(f'{base_url}/alliances/{alliance_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'alliance': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Alliance not found'}

            elif query_type == 'alliance_create':
                alliance_name = arguments.get('alliance_name')
                member_ids = arguments.get('member_ids', [])
                if not alliance_name:
                    return {'success': False, 'error': 'alliance_name required'}
                try:
                    response = requests.post(
                        f'{base_url}/alliances/create/',
                        json={'name': alliance_name, 'member_ids': member_ids},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'alliance': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Alliance created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_add':
                alliance_id = arguments.get('alliance_id')
                agent_id = arguments.get('agent_id')
                if not alliance_id or not agent_id:
                    return {'success': False, 'error': 'alliance_id and agent_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/alliances/{alliance_id}/add/',
                        json={'agent_id': agent_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Member added to alliance' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'alliance_disband':
                alliance_id = arguments.get('alliance_id')
                if not alliance_id:
                    return {'success': False, 'error': 'alliance_id required'}
                try:
                    response = requests.post(f'{base_url}/alliances/{alliance_id}/disband/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Alliance disbanded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_detail':
                rivalry_id = arguments.get('rivalry_id')
                if not rivalry_id:
                    return {'success': False, 'error': 'rivalry_id required'}
                try:
                    response = requests.get(f'{base_url}/rivalries/{rivalry_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'rivalry': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Rivalry not found'}

            elif query_type == 'rivalry_create':
                agent_a_id = arguments.get('agent_a_id')
                agent_b_id = arguments.get('agent_b_id')
                if not agent_a_id or not agent_b_id:
                    return {'success': False, 'error': 'agent_a_id and agent_b_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/rivalries/create/',
                        json={'agent_a_id': agent_a_id, 'agent_b_id': agent_b_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'rivalry': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Rivalry created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_compete':
                rivalry_id = arguments.get('rivalry_id')
                winner_id = arguments.get('winner_id')
                if not rivalry_id or not winner_id:
                    return {'success': False, 'error': 'rivalry_id and winner_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/rivalries/{rivalry_id}/compete/',
                        json={'winner_id': winner_id},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Competition recorded' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif query_type == 'rivalry_end':
                rivalry_id = arguments.get('rivalry_id')
                if not rivalry_id:
                    return {'success': False, 'error': 'rivalry_id required'}
                try:
                    response = requests.post(f'{base_url}/rivalries/{rivalry_id}/end/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Rivalry ended' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown query_type: {query_type}'}

        except Exception as e:
            logger.error(f"Error querying agent relationships: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 24: Hive Mind & Time Capsules (Session 587) =====

