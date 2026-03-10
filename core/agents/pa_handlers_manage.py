"""
PersonalAssistantAgent PAManageHandlersMixin — extracted handler methods.
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




class PAManageHandlersMixin:
    """Mixin providing handler methods for PersonalAssistantAgent."""

    def _manage_content_channel(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Control autonomous content channels.
        """
        try:
            from core.models_autonomous_studio import ContentChannel, ChannelStatus

            action = arguments.get('action', 'list')
            channel_id = arguments.get('channel_id')

            if action == 'list':
                # List all channels
                channels = ContentChannel.objects.all().order_by('-created_at')[:20]

                if not channels:
                    return {
                        'success': True,
                        'channels': [],
                        'summary': "**Content Channels:**\n\nNo content channels configured yet."
                    }

                channel_data = []
                summary_lines = ["**Content Channels:**\n"]

                for ch in channels:
                    status_emoji = {
                        'active': '🟢',
                        'paused': '⏸️',
                        'completed': '✅',
                        'failed': '❌'
                    }.get(ch.status, '❓')

                    channel_data.append({
                        'id': ch.id,
                        'name': ch.name,
                        'status': ch.status,
                        'platform': ch.platform,
                        'frequency': ch.frequency,
                        'episodes_count': ch.episodes.count() if hasattr(ch, 'episodes') else 0
                    })

                    summary_lines.append(f"{status_emoji} **{ch.name}** (ID: {ch.id})")
                    summary_lines.append(f"   Platform: {ch.platform} | Frequency: {ch.frequency}")

                return {
                    'success': True,
                    'channels': channel_data,
                    'total': len(channel_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'status':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for status'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                return {
                    'success': True,
                    'channel': {
                        'id': channel.id,
                        'name': channel.name,
                        'status': channel.status,
                        'platform': channel.platform,
                        'frequency': channel.frequency,
                        'created_at': channel.created_at.isoformat(),
                        'last_run': channel.last_run.isoformat() if channel.last_run else None,
                        'next_run': channel.next_run.isoformat() if channel.next_run else None
                    },
                    'summary': f"**Channel: {channel.name}**\n\nStatus: {channel.status}\nPlatform: {channel.platform}\nFrequency: {channel.frequency}"
                }

            elif action == 'pause':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for pause'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                channel.status = ChannelStatus.PAUSED
                channel.save()

                return {
                    'success': True,
                    'channel_id': channel_id,
                    'name': channel.name,
                    'new_status': 'paused',
                    'summary': f"⏸️ **Channel Paused:**\n\n{channel.name} has been paused."
                }

            elif action == 'resume':
                if not channel_id:
                    return {'success': False, 'error': 'channel_id required for resume'}

                channel = ContentChannel.objects.filter(id=channel_id).first()
                if not channel:
                    return {'success': False, 'error': f'Channel {channel_id} not found'}

                channel.status = ChannelStatus.ACTIVE
                channel.save()

                return {
                    'success': True,
                    'channel_id': channel_id,
                    'name': channel.name,
                    'new_status': 'active',
                    'summary': f"▶️ **Channel Resumed:**\n\n{channel.name} is now active."
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing content channel: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_bankroll(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Query and manage betting bankroll.
        """
        try:
            from core.models_bankroll import Bankroll, Wager

            action = arguments.get('action', 'status')
            limit = arguments.get('limit', 10)

            # Try to get user's bankroll
            bankroll = None
            if self.user:
                bankroll = Bankroll.objects.filter(user=self.user).first()

            if not bankroll:
                # Return demo/sample data if no bankroll exists
                return {
                    'success': True,
                    'has_bankroll': False,
                    'summary': "**Bankroll Status:**\n\nNo bankroll configured yet.\n\nTo set up your bankroll, visit the Betting Dashboard in AI Studio."
                }

            if action == 'status':
                summary_lines = ["**Bankroll Status:**\n"]
                summary_lines.append(f"💰 **Balance:** ${bankroll.current_balance:,.2f}")
                summary_lines.append(f"📈 **Initial:** ${bankroll.initial_balance:,.2f}")
                summary_lines.append(f"📊 **P/L:** ${bankroll.profit_loss:+,.2f}")
                summary_lines.append(f"🎯 **Win Rate:** {bankroll.win_rate:.1f}%")
                summary_lines.append(f"📉 **ROI:** {bankroll.roi:.1f}%")
                summary_lines.append(f"\n**Record:** {bankroll.total_won}W - {bankroll.total_lost}L - {bankroll.total_pushed}P")
                summary_lines.append(f"**Pending:** {bankroll.total_pending} wagers")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'bankroll': {
                        'current_balance': float(bankroll.current_balance),
                        'initial_balance': float(bankroll.initial_balance),
                        'profit_loss': float(bankroll.profit_loss),
                        'win_rate': float(bankroll.win_rate),
                        'roi': float(bankroll.roi),
                        'total_won': bankroll.total_won,
                        'total_lost': bankroll.total_lost,
                        'total_pending': bankroll.total_pending
                    },
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'history':
                wagers = Wager.objects.filter(bankroll=bankroll).order_by('-placed_at')[:limit]

                summary_lines = ["**Recent Wagers:**\n"]
                wager_data = []

                for w in wagers:
                    status_emoji = {
                        'pending': '⏳',
                        'won': '✅',
                        'lost': '❌',
                        'pushed': '➖'
                    }.get(w.status, '❓')

                    wager_data.append({
                        'id': w.id,
                        'event': w.event_description,
                        'amount': float(w.amount),
                        'odds': float(w.odds),
                        'status': w.status,
                        'profit': float(w.profit) if w.profit else 0
                    })

                    summary_lines.append(f"{status_emoji} ${w.amount:.2f} @ {w.odds:+.0f} - {w.event_description[:40]}...")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'wagers': wager_data,
                    'total': len(wager_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'pending':
                pending = Wager.objects.filter(bankroll=bankroll, status='pending').order_by('-placed_at')

                summary_lines = ["**Pending Wagers:**\n"]
                pending_data = []

                for w in pending:
                    pending_data.append({
                        'id': w.id,
                        'event': w.event_description,
                        'amount': float(w.amount),
                        'odds': float(w.odds),
                        'potential_profit': float(w.potential_profit)
                    })
                    summary_lines.append(f"⏳ ${w.amount:.2f} @ {w.odds:+.0f} - {w.event_description[:40]}...")

                if not pending_data:
                    summary_lines.append("No pending wagers.")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'pending_wagers': pending_data,
                    'total': len(pending_data),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'stats':
                summary_lines = ["**Betting Statistics:**\n"]
                summary_lines.append(f"📊 **Total Wagers:** {bankroll.total_wagers}")
                summary_lines.append(f"💵 **Total Wagered:** ${bankroll.total_wagered:,.2f}")
                summary_lines.append(f"💰 **Total Profit:** ${bankroll.total_profit:+,.2f}")
                summary_lines.append(f"\n🔥 **Current Streak:** {bankroll.current_streak:+d}")
                summary_lines.append(f"📈 **Best Streak:** {bankroll.best_streak}")
                summary_lines.append(f"📉 **Worst Streak:** {bankroll.worst_streak}")
                summary_lines.append(f"\n🏆 **Highest Balance:** ${bankroll.highest_balance:,.2f}")
                summary_lines.append(f"📉 **Lowest Balance:** ${bankroll.lowest_balance:,.2f}")

                return {
                    'success': True,
                    'has_bankroll': True,
                    'stats': {
                        'total_wagers': bankroll.total_wagers,
                        'total_wagered': float(bankroll.total_wagered),
                        'total_profit': float(bankroll.total_profit),
                        'current_streak': bankroll.current_streak,
                        'best_streak': bankroll.best_streak,
                        'worst_streak': bankroll.worst_streak
                    },
                    'summary': '\n'.join(summary_lines)
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing bankroll: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_situations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Manage autonomous situations.
        """
        try:
            from core.models_autonomous_situations import AutonomousSituationSession

            action = arguments.get('action', 'list')
            situation_type = arguments.get('situation_type')
            limit = arguments.get('limit', 10)

            if action == 'list':
                # Get unique situation types with their latest sessions
                from django.db.models import Max, Count

                sessions = AutonomousSituationSession.objects.values('situation_type').annotate(
                    last_run=Max('started_at'),
                    count=Count('id')
                ).order_by('-last_run')[:limit]

                summary_lines = ["**Autonomous Situations:**\n"]
                situations = []

                situation_emojis = {
                    'design_trends': '🎨',
                    'job_matching': '💼',
                    'content_studio': '📺',
                    'stock_market': '📈',
                    'blockchain': '⛓️',
                    'market_intelligence': '🔍',
                    'narrative_drift': '📊',
                    'crypto_sentiment': '🪙',
                }

                for s in sessions:
                    situations.append({
                        'type': s['situation_type'],
                        'last_run': s['last_run'].isoformat() if s['last_run'] else None,
                        'total_sessions': s['count']
                    })

                    emoji = situation_emojis.get(s['situation_type'], '🔄')
                    summary_lines.append(f"{emoji} **{s['situation_type']}** ({s['count']} sessions)")

                if not sessions:
                    summary_lines.append("No autonomous situations have run yet.")

                return {
                    'success': True,
                    'situations': situations,
                    'total': len(situations),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'history':
                # Get recent sessions
                sessions_query = AutonomousSituationSession.objects.all()

                if situation_type:
                    sessions_query = sessions_query.filter(situation_type=situation_type)

                sessions = sessions_query.order_by('-started_at')[:limit]

                summary_lines = ["**Situation History:**\n"]
                history = []

                for s in sessions:
                    history.append({
                        'id': str(s.id),
                        'type': s.situation_type,
                        'started_at': s.started_at.isoformat(),
                        'status': getattr(s, 'status', 'completed')
                    })

                    summary_lines.append(f"🔄 {s.situation_type} - {s.started_at.strftime('%Y-%m-%d %H:%M')}")

                return {
                    'success': True,
                    'history': history,
                    'total': len(history),
                    'summary': '\n'.join(summary_lines)
                }

            elif action == 'status':
                # Get current status of all situations
                from django.utils import timezone
                from datetime import timedelta

                recent = timezone.now() - timedelta(hours=24)
                recent_sessions = AutonomousSituationSession.objects.filter(
                    started_at__gte=recent
                ).values('situation_type').annotate(
                    count=models.Count('id')
                )

                summary_lines = ["**Situation Status (24h):**\n"]

                if recent_sessions:
                    for s in recent_sessions:
                        summary_lines.append(f"✅ {s['situation_type']}: {s['count']} runs")
                else:
                    summary_lines.append("No situations have run in the last 24 hours.")

                return {
                    'success': True,
                    'recent_activity': list(recent_sessions),
                    'summary': '\n'.join(summary_lines)
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing situations: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _manage_proactive_alerts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage proactive alerts, notifications, and automations.
        """
        try:
            import requests
            action = arguments.get('action', 'list_alerts')
            base_url = 'http://localhost:8000/api/proactive'

            if action == 'list_alerts':
                try:
                    response = requests.get(f'{base_url}/alerts/', timeout=10)
                    if response.status_code == 200:
                        alerts = response.json()
                        return {
                            'success': True,
                            'alerts': alerts[:20] if isinstance(alerts, list) else alerts.get('alerts', [])[:20],
                            'summary': f"Found {len(alerts) if isinstance(alerts, list) else len(alerts.get('alerts', []))} alerts"
                        }
                except:
                    pass
                return {'success': True, 'alerts': [], 'summary': 'No alerts configured'}

            elif action == 'list_notifications':
                try:
                    response = requests.get(f'{base_url}/notifications/', timeout=10)
                    if response.status_code == 200:
                        notifications = response.json()
                        return {
                            'success': True,
                            'notifications': notifications[:20] if isinstance(notifications, list) else notifications.get('notifications', [])[:20],
                            'summary': f"Found notifications"
                        }
                except:
                    pass
                return {'success': True, 'notifications': [], 'summary': 'No notifications'}

            elif action == 'list_automations':
                try:
                    response = requests.get(f'{base_url}/automations/', timeout=10)
                    if response.status_code == 200:
                        automations = response.json()
                        return {
                            'success': True,
                            'automations': automations[:20] if isinstance(automations, list) else automations.get('automations', [])[:20],
                            'summary': f"Found automations"
                        }
                except:
                    pass
                return {'success': True, 'automations': [], 'summary': 'No automations configured'}

            elif action == 'create_alert':
                alert_data = {
                    'alert_type': arguments.get('alert_type', 'custom'),
                    'condition': arguments.get('condition', ''),
                    'is_active': True
                }
                response = requests.post(f'{base_url}/alerts/create/', json=alert_data, timeout=10)
                return {
                    'success': response.status_code == 200 or response.status_code == 201,
                    'message': 'Alert created' if response.status_code in [200, 201] else response.text
                }

            elif action == 'toggle_alert':
                alert_id = arguments.get('alert_id')
                if alert_id:
                    response = requests.post(f'{base_url}/alerts/{alert_id}/toggle/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Alert toggled' if response.status_code == 200 else response.text
                    }

            elif action == 'run_check':
                response = requests.post(f'{base_url}/check/', timeout=30)
                return {
                    'success': response.status_code == 200,
                    'message': 'Proactive check completed' if response.status_code == 200 else response.text,
                    'data': response.json() if response.status_code == 200 else {}
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing proactive alerts: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_team(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent teams, roles, and team workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_teams')
            base_url = 'http://localhost:8000/api/teams'

            if action == 'list_teams':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        teams = response.json()
                        team_list = teams if isinstance(teams, list) else teams.get('teams', [])
                        return {
                            'success': True,
                            'teams': team_list[:20],
                            'total': len(team_list),
                            'summary': f"Found {len(team_list)} teams"
                        }
                except:
                    pass
                # Fallback - query Team model directly
                from core.models_unified_system import AgentTeam
                teams = AgentTeam.objects.all()[:20]
                return {
                    'success': True,
                    'teams': [{'id': str(t.id), 'name': t.name} for t in teams],
                    'total': AgentTeam.objects.count(),
                    'summary': f"Found {AgentTeam.objects.count()} teams"
                }

            elif action == 'team_stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                from core.models_unified_system import AgentTeam
                return {'success': True, 'stats': {'total_teams': AgentTeam.objects.count()}}

            elif action == 'list_roles':
                try:
                    response = requests.get(f'{base_url}/roles/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'roles': response.json()}
                except:
                    pass
                return {'success': True, 'roles': ['lead', 'member', 'specialist', 'coordinator']}

            elif action == 'get_team':
                team_id = arguments.get('team_id')
                if team_id:
                    response = requests.get(f'{base_url}/{team_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'team': response.json()}

            elif action == 'create_team':
                team_name = arguments.get('team_name', 'New Team')
                response = requests.post(f'{base_url}/create/', json={'name': team_name}, timeout=10)
                return {
                    'success': response.status_code in [200, 201],
                    'message': f'Team "{team_name}" created' if response.status_code in [200, 201] else response.text
                }

            elif action == 'add_member':
                team_id = arguments.get('team_id')
                agent_id = arguments.get('agent_id')
                role = arguments.get('role', 'member')
                if team_id and agent_id:
                    response = requests.post(
                        f'{base_url}/{team_id}/members/',
                        json={'agent_id': agent_id, 'role': role},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Member added' if response.status_code == 200 else response.text
                    }

            return {'success': False, 'error': f'Unknown action or missing params: {action}'}

        except Exception as e:
            logger.error(f"Error managing team: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_distribution(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage content distribution across platforms.
        """
        try:
            import requests
            action = arguments.get('action', 'list_platforms')
            base_url = 'http://localhost:8000/api/distribution'

            if action == 'list_platforms':
                try:
                    response = requests.get(f'{base_url}/platforms/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'platforms': response.json()}
                except:
                    pass
                # Fallback - return default platforms
                return {
                    'success': True,
                    'platforms': ['twitter', 'linkedin', 'facebook', 'instagram', 'youtube', 'tiktok'],
                    'summary': 'Available platforms (default list)'
                }

            elif action == 'list_distributions':
                try:
                    response = requests.get(f'{base_url}/content/', timeout=10)
                    if response.status_code == 200:
                        dist = response.json()
                        return {
                            'success': True,
                            'distributions': dist[:20] if isinstance(dist, list) else dist.get('distributions', [])[:20],
                            'summary': f"Found distributions"
                        }
                except:
                    pass
                return {'success': True, 'distributions': [], 'summary': 'No distributions found'}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                return {'success': True, 'stats': {'message': 'Stats not available'}}

            elif action == 'create_distribution':
                content_id = arguments.get('content_id')
                platform = arguments.get('platform', 'all')
                if content_id:
                    response = requests.post(
                        f'{base_url}/content/create/',
                        json={'content_id': content_id, 'platform': platform},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Distribution created' if response.status_code in [200, 201] else response.text
                    }

            elif action == 'schedule':
                content_id = arguments.get('content_id')
                scheduled_time = arguments.get('scheduled_time')
                platform = arguments.get('platform', 'all')
                if content_id and scheduled_time:
                    response = requests.post(
                        f'{base_url}/schedule/',
                        json={'content_id': content_id, 'platform': platform, 'scheduled_time': scheduled_time},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Scheduled for {scheduled_time}' if response.status_code in [200, 201] else response.text
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing distribution: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_memory_palace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent memory palace and memory organization.
        """
        try:
            import requests
            from django.db.models import Count

            action = arguments.get('action', 'overview')
            agent_name = arguments.get('agent_name')
            query = arguments.get('query', '')
            limit = min(arguments.get('limit', 10), 50)
            base_url = 'http://localhost:8000/api/memory-palace'

            if action == 'overview':
                # Get memory palace overview
                from core.models_unified_system import AgentMemory, Agent
                memory_stats = AgentMemory.objects.values('memory_type').annotate(count=Count('id')).order_by('-count')
                total_memories = AgentMemory.objects.count()

                return {
                    'success': True,
                    'overview': {
                        'total_memories': total_memories,
                        'by_type': {s['memory_type']: s['count'] for s in memory_stats}
                    },
                    'summary': f"Memory Palace: {total_memories} memories across {len(memory_stats)} types"
                }

            elif action == 'search':
                if query:
                    from core.models_unified_system import AgentMemory
                    # Session 810: Defer embedding fields to reduce egress costs
                    memories = AgentMemory.objects.defer('embedding').filter(content__icontains=query).order_by('-created_at')[:limit]
                    return {
                        'success': True,
                        'results': [
                            {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'type': m.memory_type}
                            for m in memories
                        ],
                        'summary': f"Found {len(memories)} memories matching '{query}'"
                    }

            elif action == 'recent':
                from core.models_unified_system import AgentMemory
                # Session 810: Defer embedding fields to reduce egress costs
                memories = AgentMemory.objects.defer('embedding').all().order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'memories': [
                        {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'type': m.memory_type, 'created': str(m.created_at)}
                        for m in memories
                    ],
                    'summary': f"Last {len(memories)} memories"
                }

            elif action == 'important':
                from core.models_unified_system import AgentMemory
                # Session 810: Defer embedding fields to reduce egress costs
                memories = AgentMemory.objects.defer('embedding').filter(importance__gte=0.7).order_by('-importance', '-created_at')[:limit]
                return {
                    'success': True,
                    'memories': [
                        {'agent': m.agent.name if m.agent else 'Unknown', 'content': m.content[:200], 'importance': m.importance}
                        for m in memories
                    ],
                    'summary': f"Found {len(memories)} high-importance memories"
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing memory palace: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent collaborations and partnerships.
        """
        try:
            import requests
            from django.utils import timezone
            from datetime import timedelta
            from django.db.models import Count

            action = arguments.get('action', 'stats')
            time_period = arguments.get('time_period', '7d')
            base_url = 'http://localhost:8000/api/collaboration'

            now = timezone.now()
            period_map = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}
            cutoff = now - period_map.get(time_period, timedelta(days=7))

            if action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass

                # Fallback to direct query
                from core.models_unified_system import Collaboration
                collab_count = Collaboration.objects.filter(created_at__gte=cutoff).count()
                return {
                    'success': True,
                    'stats': {'collaborations': collab_count, 'period': time_period},
                    'summary': f"**Collaborations ({time_period}):** {collab_count}"
                }

            elif action == 'history':
                from core.models_unified_system import Collaboration
                collabs = Collaboration.objects.filter(created_at__gte=cutoff).order_by('-created_at')[:20]
                return {
                    'success': True,
                    'history': [
                        {
                            'id': str(c.id),
                            'lead_agent': c.lead_agent.name if c.lead_agent else 'Unknown',
                            'objective': c.objective[:100] if c.objective else '',
                            'status': c.status,
                            'created': str(c.created_at)
                        }
                        for c in collabs
                    ],
                    'summary': f"Found {len(collabs)} collaborations"
                }

            elif action == 'active':
                from core.models_unified_system import Collaboration
                active = Collaboration.objects.filter(status='active').order_by('-created_at')[:20]
                return {
                    'success': True,
                    'active': [
                        {'id': str(c.id), 'lead_agent': c.lead_agent.name if c.lead_agent else 'Unknown', 'objective': c.objective[:50]}
                        for c in active
                    ],
                    'summary': f"Found {len(active)} active collaborations"
                }

            elif action == 'network':
                try:
                    response = requests.get(f'{base_url}/network/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'network': response.json()}
                except:
                    return {'success': True, 'network': {'message': 'Network visualization not available via API'}}

            elif action == 'start':
                agent_names = arguments.get('agent_names', [])
                if len(agent_names) >= 2:
                    response = requests.post(
                        f'{base_url}/request/',
                        json={'initiator': agent_names[0], 'collaborator': agent_names[1]},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Collaboration started' if response.status_code in [200, 201] else response.text
                    }

            elif action == 'performance':
                try:
                    response = requests.get(f'{base_url}/performance/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'performance': response.json()}
                except:
                    pass

                from core.models_unified_system import Collaboration
                perf = Collaboration.objects.filter(
                    created_at__gte=cutoff,
                    status='completed'
                ).count()
                return {
                    'success': True,
                    'performance': {'completed': perf, 'period': time_period},
                    'summary': f"**Completed collaborations ({time_period}):** {perf}"
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing collaboration: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Session 580: Phase 9 Tools - Deep System Coverage
    # =========================================================================

    def _manage_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage partnership projects - list, create, update, export.
        """
        try:
            import requests
            action = arguments.get('action', 'list')
            base_url = 'http://localhost:8000/api/projects'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        projects = response.json()
                        project_list = projects if isinstance(projects, list) else projects.get('projects', [])
                        return {
                            'success': True,
                            'projects': project_list[:20],
                            'total': len(project_list),
                            'summary': f"Found {len(project_list)} projects"
                        }
                except:
                    pass
                # Fallback to direct query
                from core.models_partnership import PartnershipProject
                projects = PartnershipProject.objects.all().order_by('-created_at')[:20]
                return {
                    'success': True,
                    'projects': [{'id': str(p.id), 'name': p.name, 'status': p.status} for p in projects],
                    'total': PartnershipProject.objects.count(),
                    'summary': f"Found {PartnershipProject.objects.count()} projects"
                }

            elif action == 'get':
                project_id = arguments.get('project_id')
                if project_id:
                    try:
                        response = requests.get(f'{base_url}/{project_id}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'project': response.json()}
                    except:
                        pass
                    from core.models_partnership import PartnershipProject
                    try:
                        p = PartnershipProject.objects.get(id=project_id)
                        return {'success': True, 'project': {'id': str(p.id), 'name': p.name, 'description': p.description, 'status': p.status}}
                    except:
                        return {'success': False, 'error': 'Project not found'}

            elif action == 'create':
                name = arguments.get('name', 'New Project')
                description = arguments.get('description', '')
                try:
                    response = requests.post(f'{base_url}/create/', json={'name': name, 'description': description}, timeout=10)
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Project "{name}" created' if response.status_code in [200, 201] else response.text
                    }
                except:
                    return {'success': False, 'error': 'Could not create project'}

            elif action == 'get_intelligence':
                project_id = arguments.get('project_id')
                if project_id:
                    try:
                        response = requests.get(f'{base_url}/{project_id}/intelligence/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'intelligence': response.json()}
                    except:
                        pass
                return {'success': True, 'intelligence': {'message': 'Intelligence not available'}}

            elif action == 'export_pdf':
                project_id = arguments.get('project_id')
                if project_id:
                    return {
                        'success': True,
                        'message': f'PDF export available at /api/projects/{project_id}/export-comprehensive-pdf/',
                        'export_url': f'/api/projects/{project_id}/export-comprehensive-pdf/'
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing project: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_agent_training(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage agent training, capabilities, and templates.
        """
        try:
            import requests
            from django.db.models import Avg
            action = arguments.get('action', 'list_agents')
            base_url = 'http://localhost:8000/api/training'

            if action == 'list_agents':
                try:
                    response = requests.get(f'{base_url}/agents/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'agents': response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True).order_by('name')[:20]
                return {
                    'success': True,
                    'agents': [{'name': a.name, 'type': a.agent_type, 'effectiveness': a.effectiveness_score} for a in agents],
                    'summary': f"Found {Agent.objects.filter(is_active=True).count()} trainable agents"
                }

            elif action == 'get_agent':
                agent_name = arguments.get('agent_name')
                if agent_name:
                    try:
                        response = requests.get(f'{base_url}/agents/{agent_name}/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'agent': response.json()}
                    except:
                        pass
                    from core.models_unified_system import Agent
                    try:
                        a = Agent.objects.get(name__iexact=agent_name)
                        return {'success': True, 'agent': {'name': a.name, 'type': a.agent_type, 'capabilities': a.capabilities}}
                    except:
                        return {'success': False, 'error': 'Agent not found'}

            elif action == 'list_capabilities':
                try:
                    response = requests.get(f'{base_url}/capabilities/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'capabilities': response.json()}
                except:
                    pass
                return {'success': True, 'capabilities': ['research', 'writing', 'analysis', 'creation', 'editing']}

            elif action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'templates': response.json()}
                except:
                    pass
                return {'success': True, 'templates': []}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/stats/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'stats': response.json()}
                except:
                    pass
                from core.models_unified_system import Agent
                return {
                    'success': True,
                    'stats': {
                        'total_agents': Agent.objects.filter(is_active=True).count(),
                        'avg_effectiveness': round(Agent.objects.filter(is_active=True).aggregate(avg=Avg('effectiveness_score'))['avg'] or 0, 1)
                    }
                }

            elif action == 'history':
                try:
                    response = requests.get(f'{base_url}/history/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'history': response.json()}
                except:
                    pass
                return {'success': True, 'history': []}

            elif action == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'dashboard': response.json()}
                except:
                    pass
                return {'success': True, 'dashboard': {'message': 'Dashboard data not available'}}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing agent training: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_workflow_templates(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage workflow templates and active workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_templates')
            base_url = 'http://localhost:8000/api/teams/workflows'

            if action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'templates': response.json()}
                except:
                    pass
                # Fallback - return default workflow templates
                return {
                    'success': True,
                    'templates': [
                        {'name': 'research_and_write', 'description': 'Research a topic and write content'},
                        {'name': 'analyze_and_report', 'description': 'Analyze data and generate report'},
                        {'name': 'create_and_distribute', 'description': 'Create content and distribute to platforms'}
                    ],
                    'summary': 'Available workflow templates'
                }

            elif action == 'list_active':
                try:
                    response = requests.get(f'{base_url}/active/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'active_workflows': response.json()}
                except:
                    pass
                return {'success': True, 'active_workflows': [], 'message': 'No active workflows'}

            elif action == 'get_status':
                workflow_id = arguments.get('workflow_id')
                if workflow_id:
                    try:
                        response = requests.get(f'{base_url}/{workflow_id}/status/', timeout=10)
                        if response.status_code == 200:
                            return {'success': True, 'status': response.json()}
                    except:
                        pass
                return {'success': False, 'error': 'Workflow not found'}

            elif action == 'create_from_template':
                template_name = arguments.get('template_name')
                if template_name:
                    return {
                        'success': True,
                        'message': f'Use execute_workflow tool with template: {template_name}',
                        'hint': 'The execute_workflow tool can run workflows based on templates'
                    }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing workflow templates: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_notifications(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage proactive notifications.
        """
        try:
            import requests
            from django.utils import timezone

            action = arguments.get('action', 'list')
            notification_id = arguments.get('notification_id')
            unread_only = arguments.get('unread_only', False)
            limit = arguments.get('limit', 20)
            preferences = arguments.get('preferences', {})

            base_url = 'http://localhost:8000/api/proactive/notifications'

            if action == 'list':
                params = {'limit': limit}
                if unread_only:
                    params['unread'] = 'true'
                try:
                    response = requests.get(f'{base_url}/', params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'notifications': data.get('notifications', []),
                            'total': data.get('total', 0),
                            'unread_count': data.get('unread_count', 0),
                            'summary': f"Found {data.get('total', 0)} notifications ({data.get('unread_count', 0)} unread)"
                        }
                except:
                    pass

                # Fallback: Query database directly
                from core.models_unified_system import ProactiveNotification
                notifications = ProactiveNotification.objects.all()
                if unread_only:
                    notifications = notifications.filter(is_read=False, is_dismissed=False)
                notifications = notifications.order_by('-created_at')[:limit]
                total = ProactiveNotification.objects.count()
                unread = ProactiveNotification.objects.filter(is_read=False, is_dismissed=False).count()

                return {
                    'success': True,
                    'notifications': [
                        {
                            'id': str(n.id),
                            'type': n.notification_type,
                            'priority': n.priority,
                            'title': n.title,
                            'message': n.message,
                            'is_read': n.is_read,
                            'created_at': n.created_at.isoformat()
                        }
                        for n in notifications
                    ],
                    'total': total,
                    'unread_count': unread,
                    'summary': f"Found {total} notifications ({unread} unread)"
                }

            elif action == 'counts':
                try:
                    response = requests.get(f'{base_url}/', params={'limit': 1}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'total': data.get('total', 0),
                            'unread_count': data.get('unread_count', 0),
                            'summary': f"{data.get('unread_count', 0)} unread of {data.get('total', 0)} total"
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                total = ProactiveNotification.objects.count()
                unread = ProactiveNotification.objects.filter(is_read=False, is_dismissed=False).count()
                return {
                    'success': True,
                    'total': total,
                    'unread_count': unread,
                    'summary': f"{unread} unread of {total} total"
                }

            elif action == 'read':
                if not notification_id:
                    return {'success': False, 'error': 'notification_id required for read action'}
                try:
                    response = requests.post(f'{base_url}/{notification_id}/read/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'notification_id': notification_id,
                            'message': 'Notification marked as read'
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                try:
                    notification = ProactiveNotification.objects.get(id=notification_id)
                    notification.is_read = True
                    notification.read_at = timezone.now()
                    notification.save()
                    return {
                        'success': True,
                        'notification_id': notification_id,
                        'message': 'Notification marked as read'
                    }
                except ProactiveNotification.DoesNotExist:
                    return {'success': False, 'error': 'Notification not found'}

            elif action == 'dismiss':
                if not notification_id:
                    return {'success': False, 'error': 'notification_id required for dismiss action'}
                try:
                    response = requests.post(f'{base_url}/{notification_id}/dismiss/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'notification_id': notification_id,
                            'message': 'Notification dismissed'
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                try:
                    notification = ProactiveNotification.objects.get(id=notification_id)
                    notification.is_dismissed = True
                    notification.dismissed_at = timezone.now()
                    notification.save()
                    return {
                        'success': True,
                        'notification_id': notification_id,
                        'message': 'Notification dismissed'
                    }
                except ProactiveNotification.DoesNotExist:
                    return {'success': False, 'error': 'Notification not found'}

            elif action == 'read_all':
                try:
                    response = requests.post(f'{base_url}/read-all/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'updated_count': data.get('updated_count', 0),
                            'message': f"Marked {data.get('updated_count', 0)} notifications as read"
                        }
                except:
                    pass

                from core.models_unified_system import ProactiveNotification
                updated = ProactiveNotification.objects.filter(is_read=False).update(
                    is_read=True, read_at=timezone.now()
                )
                return {
                    'success': True,
                    'updated_count': updated,
                    'message': f'Marked {updated} notifications as read'
                }

            elif action == 'preferences':
                try:
                    if preferences:
                        response = requests.put(f'{base_url}/preferences/', json=preferences, timeout=10)
                    else:
                        response = requests.get(f'{base_url}/preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data.get('preferences', data),
                            'message': 'Preferences updated' if preferences else 'Current preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {'email_enabled': True, 'push_enabled': True, 'digest_frequency': 'realtime'},
                    'message': 'Default preferences (API unavailable)'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing notifications: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_push_notifications(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage Web Push notification settings.
        """
        try:
            import requests

            action = arguments.get('action', 'status')
            preferences = arguments.get('preferences', {})

            base_url = 'http://localhost:8000/api/v1/push'

            if action == 'status':
                try:
                    response = requests.get(f'{base_url}/status/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'subscribed': data.get('subscribed', False),
                            'subscription_count': data.get('subscription_count', 0),
                            'summary': 'Push notifications enabled' if data.get('subscribed') else 'Not subscribed to push notifications'
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_push_notifications import PushSubscription
                count = PushSubscription.objects.filter(is_active=True).count()
                return {
                    'success': True,
                    'subscribed': count > 0,
                    'subscription_count': count,
                    'summary': f'{count} active push subscription(s)' if count else 'No active push subscriptions'
                }

            elif action == 'preferences':
                try:
                    if preferences:
                        response = requests.put(f'{base_url}/preferences/', json=preferences, timeout=10)
                    else:
                        response = requests.get(f'{base_url}/preferences/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'preferences': data.get('preferences', data),
                            'message': 'Preferences updated' if preferences else 'Current push preferences'
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_push_notifications import NotificationPreference
                try:
                    pref = NotificationPreference.objects.first()
                    if pref:
                        return {
                            'success': True,
                            'preferences': {
                                'notifications_enabled': pref.notifications_enabled,
                                'arb_alerts_enabled': pref.arb_alerts_enabled,
                                'arb_min_profit_pct': float(pref.arb_min_profit_pct)
                            },
                            'message': 'Current push preferences'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'preferences': {
                        'notifications_enabled': True,
                        'arb_alerts_enabled': True,
                        'arb_min_profit_pct': 1.0
                    },
                    'message': 'Default preferences'
                }

            elif action == 'test':
                try:
                    response = requests.post(f'{base_url}/test/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'sent': data.get('sent', False),
                            'message': 'Test notification sent' if data.get('sent') else 'No active subscription to send to'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'sent': False,
                    'message': 'Test notification requires active browser subscription'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing push notifications: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 12: Export & Scheduler Tools (Session 582) =====

    def _manage_exports(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Export data in various formats.
        """
        try:
            import requests

            export_type = arguments.get('export_type', 'project')
            format = arguments.get('format', 'pdf')
            resource_id = arguments.get('resource_id')
            options = arguments.get('options', {})

            base_url = 'http://localhost:8000'

            if export_type == 'project':
                if not resource_id:
                    # List recent projects instead
                    from core.models_partnership import PartnershipProject
                    projects = PartnershipProject.objects.order_by('-created_at')[:5]
                    return {
                        'success': True,
                        'message': 'Provide a project_id to export. Recent projects:',
                        'projects': [
                            {'id': str(p.id), 'name': p.name, 'created': p.created_at.isoformat()}
                            for p in projects
                        ]
                    }

                format_map = {'pdf': 'pdf', 'zip': 'zip', 'csv': 'csv'}
                fmt = format_map.get(format, 'pdf')
                url = f'{base_url}/api/creative-projects/{resource_id}/export/{fmt}/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': fmt,
                    'message': f'Export URL ready: {url}'
                }

            elif export_type == 'research':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for research export'}
                url = f'{base_url}/api/projects/{resource_id}/export-research-pdf/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': 'pdf',
                    'message': f'Research PDF export URL: {url}'
                }

            elif export_type == 'content':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for content export'}
                url = f'{base_url}/api/projects/{resource_id}/export-content/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'markdown',
                    'message': f'Content export URL: {url}'
                }

            elif export_type == 'revenue':
                try:
                    params = {}
                    if options.get('date_range'):
                        params['date_range'] = options['date_range']
                    response = requests.get(f'{base_url}/api/distribution/revenue/export/', params=params, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'revenue_data': data,
                            'format': 'json',
                            'summary': f"Revenue export complete"
                        }
                except:
                    pass

                # Fallback: return export URL
                return {
                    'success': True,
                    'export_url': f'{base_url}/api/distribution/revenue/export/',
                    'format': 'json',
                    'message': 'Revenue export endpoint ready'
                }

            elif export_type == 'legal':
                url = f'{base_url}/api/legal/export-section/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'pdf',
                    'message': 'Legal document export URL ready'
                }

            elif export_type == 'portfolio':
                if not resource_id:
                    return {'success': False, 'error': 'resource_id (project_id) required for portfolio export'}
                url = f'{base_url}/api/v1/portfolio/projects/{resource_id}/export/'
                return {
                    'success': True,
                    'export_url': url,
                    'format': format or 'zip',
                    'message': f'Portfolio export URL: {url}'
                }

            return {'success': False, 'error': f'Unknown export type: {export_type}'}

        except Exception as e:
            logger.error(f"Error managing exports: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_scheduler(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 582: Manage scheduled tasks and distributions.
        """
        try:
            import requests
            from django.utils import timezone

            action = arguments.get('action', 'list')
            distribution_id = arguments.get('distribution_id')
            workflow_id = arguments.get('workflow_id')
            new_time = arguments.get('new_time')
            schedule_type = arguments.get('schedule_type', 'all')

            base_url = 'http://localhost:8000'

            if action == 'list':
                results = {'distributions': [], 'workflows': [], 'celery_schedules': []}

                if schedule_type in ['distributions', 'all']:
                    try:
                        response = requests.get(f'{base_url}/api/distribution/scheduled/', timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            results['distributions'] = data if isinstance(data, list) else data.get('results', [])
                    except:
                        from core.models_unified_system import ContentDistribution
                        dists = ContentDistribution.objects.filter(
                            status='scheduled',
                            scheduled_time__gte=timezone.now()
                        ).order_by('scheduled_time')[:10]
                        results['distributions'] = [
                            {
                                'id': str(d.id),
                                'platform': d.platform,
                                'scheduled_time': d.scheduled_time.isoformat(),
                                'status': d.status
                            }
                            for d in dists
                        ]

                if schedule_type in ['workflows', 'all']:
                    try:
                        from core.models_workflow import WorkflowExecution
                        workflows = WorkflowExecution.objects.filter(
                            status='scheduled'
                        ).order_by('-created_at')[:10]
                        results['workflows'] = [
                            {
                                'id': str(w.id),
                                'workflow_name': w.workflow.name if hasattr(w, 'workflow') else 'Unknown',
                                'status': w.status,
                                'created_at': w.created_at.isoformat()
                            }
                            for w in workflows
                        ]
                    except:
                        results['workflows'] = []

                total = len(results['distributions']) + len(results['workflows'])
                return {
                    'success': True,
                    'scheduled_items': results,
                    'total': total,
                    'summary': f"Found {len(results['distributions'])} scheduled distributions, {len(results['workflows'])} scheduled workflows"
                }

            elif action == 'cancel':
                if not distribution_id:
                    return {'success': False, 'error': 'distribution_id required for cancel action'}
                try:
                    response = requests.post(f'{base_url}/api/distribution/{distribution_id}/cancel/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'distribution_id': distribution_id,
                            'message': 'Distribution cancelled'
                        }
                except:
                    pass

                from core.models_unified_system import ContentDistribution
                try:
                    dist = ContentDistribution.objects.get(id=distribution_id)
                    dist.status = 'cancelled'
                    dist.save()
                    return {
                        'success': True,
                        'distribution_id': distribution_id,
                        'message': 'Distribution cancelled'
                    }
                except ContentDistribution.DoesNotExist:
                    return {'success': False, 'error': 'Distribution not found'}

            elif action == 'reschedule':
                if not distribution_id:
                    return {'success': False, 'error': 'distribution_id required for reschedule action'}
                if not new_time:
                    return {'success': False, 'error': 'new_time required for reschedule action'}

                try:
                    response = requests.post(
                        f'{base_url}/api/distribution/{distribution_id}/reschedule/',
                        json={'scheduled_time': new_time},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'distribution_id': distribution_id,
                            'new_time': new_time,
                            'message': f'Distribution rescheduled to {new_time}'
                        }
                except:
                    pass

                from core.models_unified_system import ContentDistribution
                from dateutil.parser import parse
                try:
                    dist = ContentDistribution.objects.get(id=distribution_id)
                    dist.scheduled_time = parse(new_time)
                    dist.save()
                    return {
                        'success': True,
                        'distribution_id': distribution_id,
                        'new_time': new_time,
                        'message': f'Distribution rescheduled to {new_time}'
                    }
                except ContentDistribution.DoesNotExist:
                    return {'success': False, 'error': 'Distribution not found'}

            elif action == 'celery_schedules':
                try:
                    response = requests.get(f'{base_url}/api/monitoring/schedules/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        schedules = data.get('schedules', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'celery_schedules': schedules[:20] if isinstance(schedules, list) else schedules,
                            'summary': f"Found {len(schedules) if isinstance(schedules, list) else 'multiple'} Celery beat schedules"
                        }
                except:
                    pass

                # Fallback: return basic schedule info
                from core.celery import app
                try:
                    schedules = list(app.conf.beat_schedule.keys())[:20]
                    return {
                        'success': True,
                        'celery_schedules': schedules,
                        'total': len(app.conf.beat_schedule),
                        'summary': f"Found {len(app.conf.beat_schedule)} Celery beat schedules"
                    }
                except:
                    return {
                        'success': True,
                        'celery_schedules': [],
                        'message': 'Unable to retrieve Celery schedules'
                    }

            elif action == 'schedule_workflow':
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required for schedule_workflow action'}

                try:
                    response = requests.post(
                        f'{base_url}/api/workflows/{workflow_id}/schedule/',
                        json={'scheduled_time': new_time} if new_time else {},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'workflow_id': workflow_id,
                            'message': 'Workflow scheduled successfully'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'workflow_id': workflow_id,
                    'schedule_url': f'{base_url}/api/workflows/{workflow_id}/schedule/',
                    'message': 'Use the schedule URL to schedule this workflow'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing scheduler: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 13: Monitoring Tools (Session 582) =====

    def _manage_artifacts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-generated artifacts and their execution.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            artifact_id = arguments.get('artifact_id')
            decision = arguments.get('decision')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/artifacts/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        artifacts = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'artifacts': artifacts[:limit] if isinstance(artifacts, list) else artifacts,
                            'summary': f"Found {len(artifacts) if isinstance(artifacts, list) else 'multiple'} artifacts"
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_artifacts import Artifact
                artifacts = Artifact.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'artifacts': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'artifact_type': a.artifact_type,
                            'status': a.status,
                            'created_at': a.created_at.isoformat()
                        }
                        for a in artifacts
                    ],
                    'summary': f"Found {len(artifacts)} artifacts"
                }

            elif action == 'pending':
                try:
                    response = requests.get(f'{base_url}/api/artifacts/pending/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'pending_artifacts': data.get('results', data),
                            'summary': 'Retrieved pending artifacts for review'
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                pending = Artifact.objects.filter(status='pending').order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'pending_artifacts': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'artifact_type': a.artifact_type,
                            'created_at': a.created_at.isoformat()
                        }
                        for a in pending
                    ],
                    'summary': f"Found {len(pending)} pending artifacts"
                }

            elif action == 'get':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.get(f'{base_url}/api/artifacts/{artifact_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'artifact': response.json(),
                            'summary': 'Retrieved artifact details'
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                try:
                    artifact = Artifact.objects.get(id=artifact_id)
                    return {
                        'success': True,
                        'artifact': {
                            'id': str(artifact.id),
                            'name': artifact.name,
                            'artifact_type': artifact.artifact_type,
                            'content': artifact.content if hasattr(artifact, 'content') else None,
                            'status': artifact.status,
                            'created_at': artifact.created_at.isoformat()
                        },
                        'summary': f"Retrieved artifact: {artifact.name}"
                    }
                except Artifact.DoesNotExist:
                    return {'success': False, 'error': 'Artifact not found'}

            elif action == 'decide':
                if not artifact_id or not decision:
                    return {'success': False, 'error': 'artifact_id and decision required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/artifacts/{artifact_id}/decide/',
                        json={'decision': decision, 'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Artifact {decision}d successfully"
                        }
                except:
                    pass

                from core.models_artifacts import Artifact
                try:
                    artifact = Artifact.objects.get(id=artifact_id)
                    artifact.status = 'approved' if decision == 'approve' else 'rejected'
                    artifact.save()
                    return {
                        'success': True,
                        'result': {'status': artifact.status},
                        'summary': f"Artifact {decision}d: {artifact.name}"
                    }
                except Artifact.DoesNotExist:
                    return {'success': False, 'error': 'Artifact not found'}

            elif action == 'execute':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/artifacts/{artifact_id}/execute/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'execution': response.json(),
                            'summary': 'Artifact execution started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not execute artifact via API'}

            elif action == 'executions':
                try:
                    response = requests.get(f'{base_url}/api/artifact-executions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'executions': data.get('results', data),
                            'summary': 'Retrieved artifact executions'
                        }
                except:
                    pass

                from core.models_artifacts import ArtifactExecution
                executions = ArtifactExecution.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'executions': [
                        {
                            'id': str(e.id),
                            'artifact_id': str(e.artifact_id) if hasattr(e, 'artifact_id') else None,
                            'status': e.status,
                            'created_at': e.created_at.isoformat()
                        }
                        for e in executions
                    ],
                    'summary': f"Found {len(executions)} executions"
                }

            elif action == 'execution_status':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id (execution_id) required'}

                try:
                    response = requests.get(f'{base_url}/api/artifact-executions/{artifact_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'execution': response.json(),
                            'summary': 'Retrieved execution status'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Execution not found'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing artifacts: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_reviews(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage Chief of Staff review documents (Pro/Con analysis).
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            review_id = arguments.get('review_id')
            artifact_id = arguments.get('artifact_id')
            question = arguments.get('question', '')
            decision = arguments.get('decision')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/review-documents/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        reviews = data.get('results', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'reviews': reviews[:limit] if isinstance(reviews, list) else reviews,
                            'summary': f"Found {len(reviews) if isinstance(reviews, list) else 'multiple'} review documents"
                        }
                except:
                    pass

                # Fallback: Query database
                from core.models_conversation_artifacts import ReviewDocument
                reviews = ReviewDocument.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'reviews': [
                        {
                            'id': str(r.id),
                            'artifact_id': str(r.artifact_id) if hasattr(r, 'artifact_id') else None,
                            'status': r.status,
                            'created_at': r.created_at.isoformat()
                        }
                        for r in reviews
                    ],
                    'summary': f"Found {len(reviews)} review documents"
                }

            elif action == 'get':
                if not review_id:
                    return {'success': False, 'error': 'review_id required'}

                try:
                    response = requests.get(f'{base_url}/api/review-documents/{review_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'review': response.json(),
                            'summary': 'Retrieved review document'
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                try:
                    review = ReviewDocument.objects.get(id=review_id)
                    return {
                        'success': True,
                        'review': {
                            'id': str(review.id),
                            'status': review.status,
                            'pro_arguments': review.pro_arguments if hasattr(review, 'pro_arguments') else None,
                            'con_arguments': review.con_arguments if hasattr(review, 'con_arguments') else None,
                            'created_at': review.created_at.isoformat()
                        },
                        'summary': 'Retrieved review document'
                    }
                except ReviewDocument.DoesNotExist:
                    return {'success': False, 'error': 'Review document not found'}

            elif action == 'ask_pro':
                if not review_id or not question:
                    return {'success': False, 'error': 'review_id and question required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/ask-pro/',
                        json={'question': question},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'pro_response': response.json(),
                            'summary': 'Pro side responded to question'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not get Pro response'}

            elif action == 'ask_con':
                if not review_id or not question:
                    return {'success': False, 'error': 'review_id and question required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/ask-con/',
                        json={'question': question},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'con_response': response.json(),
                            'summary': 'Con side responded to question'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not get Con response'}

            elif action == 'decide':
                if not review_id or not decision:
                    return {'success': False, 'error': 'review_id and decision required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/{review_id}/decide/',
                        json={'decision': decision, 'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Review decision: {decision}"
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                try:
                    review = ReviewDocument.objects.get(id=review_id)
                    review.status = 'approved' if decision == 'approve' else 'rejected'
                    review.decision_reason = reason
                    review.save()
                    return {
                        'success': True,
                        'result': {'status': review.status},
                        'summary': f"Review decision recorded: {decision}"
                    }
                except ReviewDocument.DoesNotExist:
                    return {'success': False, 'error': 'Review document not found'}

            elif action == 'generate':
                if not artifact_id:
                    return {'success': False, 'error': 'artifact_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/review-documents/generate/',
                        json={'artifact_id': artifact_id},
                        timeout=60
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'review': response.json(),
                            'summary': 'Review document generated'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not generate review document'}

            elif action == 'trigger_auto':
                try:
                    response = requests.post(f'{base_url}/api/review-documents/trigger-auto-review/', timeout=30)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Auto-review triggered'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not trigger auto-review'}

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/review-documents/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Review statistics retrieved'
                        }
                except:
                    pass

                from core.models_conversation_artifacts import ReviewDocument
                from django.db.models import Count
                stats = ReviewDocument.objects.values('status').annotate(count=Count('id'))
                return {
                    'success': True,
                    'stats': {s['status']: s['count'] for s in stats},
                    'summary': 'Review statistics from database'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing reviews: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 15: Journey & Proposal Tools (Session 583) =====

    def _manage_journeys(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage learning journeys and progress tracking.
        """
        try:
            import requests

            action = arguments.get('action', 'active')
            journey_id = arguments.get('journey_id')
            step_id = arguments.get('step_id')
            journey_type = arguments.get('journey_type', 'default')
            base_url = 'http://localhost:8000'

            if action == 'active':
                try:
                    response = requests.get(f'{base_url}/api/journey/active/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        journeys = data.get('journeys', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'journeys': journeys,
                            'summary': f"Found {len(journeys) if isinstance(journeys, list) else 'multiple'} active journeys"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'journeys': [],
                    'summary': 'No active journeys found'
                }

            elif action == 'start':
                try:
                    response = requests.post(
                        f'{base_url}/api/journey/start/',
                        json={'journey_type': journey_type},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'journey': response.json(),
                            'summary': f"Started {journey_type} journey"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not start journey'}

            elif action == 'status':
                if not journey_id:
                    return {'success': False, 'error': 'journey_id required'}

                try:
                    response = requests.get(f'{base_url}/api/journey/{journey_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'status': response.json(),
                            'summary': 'Retrieved journey status'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Journey not found'}

            elif action == 'step_start':
                if not journey_id or step_id is None:
                    return {'success': False, 'error': 'journey_id and step_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/journey/{journey_id}/step/{step_id}/start/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'step': response.json(),
                            'summary': f"Started step {step_id}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not start step'}

            elif action == 'step_complete':
                if not journey_id or step_id is None:
                    return {'success': False, 'error': 'journey_id and step_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/journey/{journey_id}/step/{step_id}/complete/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'step': response.json(),
                            'summary': f"Completed step {step_id}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not complete step'}

            elif action == 'reset':
                if not journey_id:
                    return {'success': False, 'error': 'journey_id required'}

                try:
                    response = requests.post(f'{base_url}/api/journey/{journey_id}/reset/', timeout=10)
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Journey reset successfully'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not reset journey'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing journeys: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_proposals(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-generated proposals and their execution.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            proposal_id = arguments.get('proposal_id')
            reason = arguments.get('reason', '')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/proposals/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        proposals = data.get('results', data.get('proposals', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'proposals': proposals[:limit] if isinstance(proposals, list) else proposals,
                            'summary': f"Found {len(proposals) if isinstance(proposals, list) else 'multiple'} proposals"
                        }
                except:
                    pass

                # Fallback: Try to get proposals from database
                try:
                    from core.models_proposals import Proposal
                    proposals = Proposal.objects.order_by('-created_at')[:limit]
                    return {
                        'success': True,
                        'proposals': [
                            {
                                'id': str(p.id),
                                'title': p.title if hasattr(p, 'title') else str(p),
                                'status': p.status if hasattr(p, 'status') else 'unknown',
                                'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None
                            }
                            for p in proposals
                        ],
                        'summary': f"Found {len(proposals)} proposals"
                    }
                except:
                    return {
                        'success': True,
                        'proposals': [],
                        'summary': 'No proposals found'
                    }

            elif action == 'stats':
                try:
                    response = requests.get(f'{base_url}/api/proposals/stats/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'stats': response.json(),
                            'summary': 'Retrieved proposal statistics'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'stats': {'message': 'Stats available via API'},
                    'summary': 'Proposal stats endpoint available'
                }

            elif action == 'approve':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/approve/',
                        json={'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal approved'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not approve proposal'}

            elif action == 'reject':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/reject/',
                        json={'reason': reason},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal rejected'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not reject proposal'}

            elif action == 'execute':
                if not proposal_id:
                    return {'success': False, 'error': 'proposal_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/proposals/{proposal_id}/execute/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Proposal execution started'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not execute proposal'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing proposals: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 16: Solutions & Learning Tools (Session 583) =====

    def _manage_solutions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage AI-discovered solutions and their application.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            solution_id = arguments.get('solution_id')
            limit = arguments.get('limit', 20)
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/solutions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        solutions = data.get('results', data.get('solutions', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'solutions': solutions[:limit] if isinstance(solutions, list) else solutions,
                            'summary': f"Found {len(solutions) if isinstance(solutions, list) else 'multiple'} solutions"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'solutions': [],
                    'summary': 'No solutions found'
                }

            elif action == 'get':
                if not solution_id:
                    return {'success': False, 'error': 'solution_id required'}

                try:
                    response = requests.get(f'{base_url}/api/solutions/{solution_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'solution': response.json(),
                            'summary': 'Retrieved solution details'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Solution not found'}

            elif action == 'apply':
                if not solution_id:
                    return {'success': False, 'error': 'solution_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/solutions/{solution_id}/apply/',
                        timeout=30
                    )
                    if response.status_code in [200, 201, 202]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Solution applied successfully'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not apply solution'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing solutions: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_portfolio(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage creative portfolio items.
        """
        try:
            import requests

            action = arguments.get('action', 'list')
            item_type = arguments.get('item_type')
            item_id = arguments.get('item_id')
            item_ids = arguments.get('item_ids', [])
            base_url = 'http://localhost:8000'

            if action == 'list':
                try:
                    response = requests.get(f'{base_url}/api/portfolio/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', data.get('portfolio', data)) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'portfolio': items,
                            'summary': f"Found {len(items) if isinstance(items, list) else 'multiple'} portfolio items"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'portfolio': [],
                    'summary': 'No portfolio items found'
                }

            elif action == 'delete':
                if not item_type or not item_id:
                    return {'success': False, 'error': 'item_type and item_id required'}

                try:
                    response = requests.delete(
                        f'{base_url}/api/portfolio/{item_type}/{item_id}/delete/',
                        timeout=10
                    )
                    if response.status_code in [200, 204]:
                        return {
                            'success': True,
                            'result': {'deleted': True},
                            'summary': f"Deleted {item_type} item"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not delete item'}

            elif action == 'bulk_delete':
                if not item_ids:
                    return {'success': False, 'error': 'item_ids required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/portfolio/bulk-delete/',
                        json={'item_ids': item_ids},
                        timeout=10
                    )
                    if response.status_code in [200, 204]:
                        return {
                            'success': True,
                            'result': response.json() if response.content else {'deleted': len(item_ids)},
                            'summary': f"Bulk deleted {len(item_ids)} items"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not bulk delete items'}

            elif action == 'check_broken':
                try:
                    response = requests.get(f'{base_url}/api/portfolio/check-broken/', timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        broken = data.get('broken', data.get('broken_links', []))
                        return {
                            'success': True,
                            'broken_links': broken,
                            'summary': f"Found {len(broken) if isinstance(broken, list) else 0} broken links"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'broken_links': [],
                    'summary': 'No broken links found'
                }

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing portfolio: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_predictions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 583: Manage agent predictions (prophecies) and their verification.
        """
        try:
            import requests

            action = arguments.get('action', 'overview')
            agent_id = arguments.get('agent_id')
            prediction_id = arguments.get('prediction_id')
            outcome = arguments.get('outcome')
            base_url = 'http://localhost:8000'

            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/api/predictions/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'predictions': data,
                            'summary': 'Retrieved predictions overview'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found'
                }

            elif action == 'agent':
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}

                try:
                    response = requests.get(f'{base_url}/api/predictions/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'predictions': data,
                            'summary': f"Retrieved predictions for agent {agent_id}"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'predictions': [],
                    'summary': 'No predictions found for agent'
                }

            elif action == 'detail':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required'}

                try:
                    response = requests.get(f'{base_url}/api/predictions/{prediction_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'prediction': response.json(),
                            'summary': 'Retrieved prediction details'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Prediction not found'}

            elif action == 'verify':
                if not prediction_id or not outcome:
                    return {'success': False, 'error': 'prediction_id and outcome required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/{prediction_id}/verify/',
                        json={'outcome': outcome},
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': f"Prediction verified as {outcome}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not verify prediction'}

            elif action == 'upvote':
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required'}

                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/{prediction_id}/upvote/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Prediction upvoted'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not upvote prediction'}

            elif action == 'leaderboard':
                try:
                    response = requests.get(f'{base_url}/api/predictions/leaderboard/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'leaderboard': response.json(),
                            'summary': 'Retrieved prediction leaderboard'
                        }
                except:
                    pass

                return {
                    'success': True,
                    'leaderboard': [],
                    'summary': 'No leaderboard data found'
                }

            elif action == 'generate':
                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/generate-from-dreams/',
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Generated predictions from dreams'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not generate predictions'}

            elif action == 'expire':
                try:
                    response = requests.post(
                        f'{base_url}/api/predictions/expire-old/',
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {
                            'success': True,
                            'result': response.json(),
                            'summary': 'Expired old predictions'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not expire predictions'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing predictions: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_favorites(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 584: Manage favorites and batch operations for images, videos, workflows.
        """
        import requests

        action = arguments.get('action', 'list_images')
        item_id = arguments.get('item_id')
        item_ids = arguments.get('item_ids', [])

        base_url = 'http://localhost:8000'

        try:
            if action == 'list_images':
                try:
                    from core.models_unified_system import GeneratedImage
                    favorites = GeneratedImage.objects.filter(is_favorite=True).order_by('-created_at')[:50]
                    images = [{
                        'id': str(img.id),
                        'prompt': img.prompt[:100] if img.prompt else '',
                        'created_at': img.created_at.isoformat()
                    } for img in favorites]
                    return {
                        'success': True,
                        'favorites': images,
                        'summary': f"Found {len(images)} favorite images"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite images found'
                }

            elif action == 'list_videos':
                try:
                    from core.models_unified_system import GeneratedVideo
                    favorites = GeneratedVideo.objects.filter(is_favorite=True).order_by('-created_at')[:50]
                    videos = [{
                        'id': str(v.id),
                        'prompt': v.prompt[:100] if v.prompt else '',
                        'created_at': v.created_at.isoformat()
                    } for v in favorites]
                    return {
                        'success': True,
                        'favorites': videos,
                        'summary': f"Found {len(videos)} favorite videos"
                    }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite videos found'
                }

            elif action == 'list_workflows':
                try:
                    response = requests.get(f'{base_url}/api/workflows/favorites/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        favorites = data.get('favorites', data) if isinstance(data, dict) else data
                        return {
                            'success': True,
                            'favorites': favorites,
                            'summary': f"Found {len(favorites) if isinstance(favorites, list) else 'multiple'} favorite workflows"
                        }
                except:
                    pass

                return {
                    'success': True,
                    'favorites': [],
                    'summary': 'No favorite workflows found'
                }

            elif action == 'toggle_image':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/images/{item_id}/favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Image favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle image favorite'}

            elif action == 'toggle_video':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/v1/video/history/{item_id}/favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Video favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle video favorite'}

            elif action == 'toggle_workflow':
                if not item_id:
                    return {'success': False, 'error': 'item_id required'}

                try:
                    response = requests.post(f'{base_url}/api/workflows/history/{item_id}/toggle-favorite/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'success': True,
                            'is_favorite': data.get('is_favorite'),
                            'summary': f"Workflow favorite toggled: {data.get('is_favorite')}"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to toggle workflow favorite'}

            elif action == 'batch_download':
                if not item_ids:
                    return {'success': False, 'error': 'item_ids required for batch download'}

                try:
                    response = requests.post(
                        f'{base_url}/api/images/batch-download/',
                        json={'image_ids': item_ids},
                        timeout=30
                    )
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'download_url': response.headers.get('Content-Disposition', 'download ready'),
                            'summary': f"Batch download prepared for {len(item_ids)} images"
                        }
                except:
                    pass

                return {'success': False, 'error': 'Failed to prepare batch download'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing favorites: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_project_collaboration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage shared projects and collaborators.
        """
        try:
            import requests
            action = arguments.get('action', 'list_projects')
            base_url = 'http://localhost:8000/api/projects/shared'

            if action == 'list_projects':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        projects = response.json()
                        project_list = projects if isinstance(projects, list) else projects.get('projects', [])
                        return {
                            'success': True,
                            'projects': project_list[:20],
                            'total': len(project_list),
                            'summary': f"Found {len(project_list)} shared projects"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback - query SharedProject model directly
                from core.models_unified_system import SharedProject
                projects = SharedProject.objects.all()[:20]
                return {
                    'success': True,
                    'projects': [{'id': str(p.id), 'name': p.name if hasattr(p, 'name') else str(p)} for p in projects],
                    'total': SharedProject.objects.count(),
                    'summary': f"Found {SharedProject.objects.count()} shared projects"
                }

            elif action == 'get_project':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'project': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not retrieve project'}

            elif action == 'invite':
                project_id = arguments.get('project_id')
                user_email = arguments.get('user_email')
                role = arguments.get('role', 'editor')
                if not project_id or not user_email:
                    return {'success': False, 'error': 'project_id and user_email required'}
                try:
                    response = requests.post(
                        f'{base_url}/{project_id}/invite/',
                        json={'email': user_email, 'role': role},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Invitation sent to {user_email}' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list_invitations':
                try:
                    response = requests.get(f'{base_url}/invitations/', timeout=10)
                    if response.status_code == 200:
                        invitations = response.json()
                        inv_list = invitations if isinstance(invitations, list) else invitations.get('invitations', [])
                        return {
                            'success': True,
                            'invitations': inv_list,
                            'total': len(inv_list),
                            'summary': f"Found {len(inv_list)} pending invitations"
                        }
                except:
                    pass
                return {'success': True, 'invitations': [], 'summary': 'No invitations found'}

            elif action == 'accept_invitation':
                invitation_id = arguments.get('invitation_id')
                if not invitation_id:
                    return {'success': False, 'error': 'invitation_id required'}
                try:
                    response = requests.post(f'{base_url}/invitations/{invitation_id}/accept/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Invitation accepted' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'decline_invitation':
                invitation_id = arguments.get('invitation_id')
                if not invitation_id:
                    return {'success': False, 'error': 'invitation_id required'}
                try:
                    response = requests.post(f'{base_url}/invitations/{invitation_id}/decline/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Invitation declined' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list_collaborators':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/collaborators/', timeout=10)
                    if response.status_code == 200:
                        collaborators = response.json()
                        collab_list = collaborators if isinstance(collaborators, list) else collaborators.get('collaborators', [])
                        return {
                            'success': True,
                            'collaborators': collab_list,
                            'total': len(collab_list),
                            'summary': f"Found {len(collab_list)} collaborators"
                        }
                except:
                    pass
                return {'success': True, 'collaborators': [], 'summary': 'No collaborators found'}

            elif action == 'remove_collaborator':
                project_id = arguments.get('project_id')
                user_id = arguments.get('user_id')
                if not project_id or not user_id:
                    return {'success': False, 'error': 'project_id and user_id required'}
                try:
                    response = requests.delete(f'{base_url}/{project_id}/collaborators/{user_id}/', timeout=10)
                    return {
                        'success': response.status_code in [200, 204],
                        'message': 'Collaborator removed' if response.status_code in [200, 204] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'get_activity':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/activity/', timeout=10)
                    if response.status_code == 200:
                        activity = response.json()
                        activity_list = activity if isinstance(activity, list) else activity.get('activity', [])
                        return {
                            'success': True,
                            'activity': activity_list[:20],
                            'summary': f"Found {len(activity_list)} activity items"
                        }
                except:
                    pass
                return {'success': True, 'activity': [], 'summary': 'No activity found'}

            elif action == 'get_comments':
                project_id = arguments.get('project_id')
                if not project_id:
                    return {'success': False, 'error': 'project_id required'}
                try:
                    response = requests.get(f'{base_url}/{project_id}/comments/', timeout=10)
                    if response.status_code == 200:
                        comments = response.json()
                        comment_list = comments if isinstance(comments, list) else comments.get('comments', [])
                        return {
                            'success': True,
                            'comments': comment_list[:20],
                            'summary': f"Found {len(comment_list)} comments"
                        }
                except:
                    pass
                return {'success': True, 'comments': [], 'summary': 'No comments found'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing project collaboration: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_workflow_sharing(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Share and collaborate on workflows.
        """
        try:
            import requests
            action = arguments.get('action', 'list_shared')
            base_url = 'http://localhost:8000/api/v1/workflows'

            if action == 'list_shared':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        workflows = response.json()
                        wf_list = workflows if isinstance(workflows, list) else workflows.get('workflows', [])
                        # Filter to shared workflows if possible
                        shared = [w for w in wf_list if w.get('is_shared', True)]
                        return {
                            'success': True,
                            'workflows': shared[:20],
                            'total': len(shared),
                            'summary': f"Found {len(shared)} shared workflows"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import PublishedWorkflow
                workflows = PublishedWorkflow.objects.all()[:20]
                return {
                    'success': True,
                    'workflows': [{'id': str(w.id), 'name': w.name if hasattr(w, 'name') else str(w)} for w in workflows],
                    'total': PublishedWorkflow.objects.count(),
                    'summary': f"Found {PublishedWorkflow.objects.count()} shared workflows"
                }

            elif action == 'share':
                workflow_id = arguments.get('workflow_id')
                user_email = arguments.get('user_email')
                permissions = arguments.get('permissions', 'view')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/{workflow_id}/share/',
                        json={'email': user_email, 'permissions': permissions},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Workflow shared with {user_email}' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'collaborate':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/collaborate/',
                        json={'workflow_id': workflow_id},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'collaboration': response.json()}
                except:
                    pass

                # Try alternate endpoint
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/', timeout=10)
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'workflow': response.json(),
                            'message': 'Workflow ready for collaboration'
                        }
                except:
                    pass

                return {'success': False, 'error': 'Could not initiate collaboration'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing workflow sharing: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 22: Team Workflows & Agent Evolution Tools (Session 585) =====

    def _manage_team_workflows(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage team workflows - create, start, execute, and monitor.
        """
        try:
            import requests
            action = arguments.get('action', 'list_active')
            base_url = 'http://localhost:8000/api/teams/workflows'

            if action == 'list_active':
                try:
                    response = requests.get(f'{base_url}/active/', timeout=10)
                    if response.status_code == 200:
                        workflows = response.json()
                        wf_list = workflows if isinstance(workflows, list) else workflows.get('workflows', [])
                        return {
                            'success': True,
                            'workflows': wf_list[:20],
                            'total': len(wf_list),
                            'summary': f"Found {len(wf_list)} active team workflows"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_unified_system import TeamWorkflow
                workflows = TeamWorkflow.objects.filter(status='active')[:20]
                return {
                    'success': True,
                    'workflows': [{'id': str(w.id), 'name': w.name} for w in workflows],
                    'total': workflows.count(),
                    'summary': f"Found {workflows.count()} active team workflows"
                }

            elif action == 'list_templates':
                try:
                    response = requests.get(f'{base_url}/templates/', timeout=10)
                    if response.status_code == 200:
                        templates = response.json()
                        tmpl_list = templates if isinstance(templates, list) else templates.get('templates', [])
                        return {
                            'success': True,
                            'templates': tmpl_list[:20],
                            'total': len(tmpl_list),
                            'summary': f"Found {len(tmpl_list)} workflow templates"
                        }
                except:
                    pass
                return {'success': True, 'templates': [], 'summary': 'No templates found'}

            elif action == 'create':
                name = arguments.get('name', 'New Workflow')
                steps = arguments.get('steps', [])
                try:
                    response = requests.post(
                        f'{base_url}/',
                        json={'name': name, 'steps': steps},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': f'Workflow "{name}" created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'start':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/start/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Workflow started' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'status':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'status': response.json()}
                except:
                    pass

                # Try getting workflow detail
                try:
                    response = requests.get(f'{base_url}/{workflow_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'workflow': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Could not get workflow status'}

            elif action == 'execute':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/execute/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'result': response.json() if response.status_code == 200 else None,
                        'message': 'Workflow executed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'run_full':
                workflow_id = arguments.get('workflow_id')
                if not workflow_id:
                    return {'success': False, 'error': 'workflow_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/run/', timeout=60)
                    return {
                        'success': response.status_code == 200,
                        'result': response.json() if response.status_code == 200 else None,
                        'message': 'Full workflow run completed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'execute_step':
                workflow_id = arguments.get('workflow_id')
                step_id = arguments.get('step_id')
                if not workflow_id or not step_id:
                    return {'success': False, 'error': 'workflow_id and step_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/steps/{step_id}/execute/', timeout=30)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Step executed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'complete_step':
                workflow_id = arguments.get('workflow_id')
                step_id = arguments.get('step_id')
                if not workflow_id or not step_id:
                    return {'success': False, 'error': 'workflow_id and step_id required'}
                try:
                    response = requests.post(f'{base_url}/{workflow_id}/steps/{step_id}/complete/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Step completed' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing team workflows: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_voice_marketplace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Manage voice cloning and TTS marketplace."""
        try:
            import requests
            action = arguments.get('action')
            base_url = 'http://localhost:8000/api/voice-marketplace'

            if action == 'browse':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        voices = data if isinstance(data, list) else data.get('voices', [])
                        return {
                            'success': True,
                            'voices': voices[:20],
                            'total': len(voices),
                            'summary': f"Found {len(voices)} voices in marketplace"
                        }
                except Exception as e:
                    logger.debug(f"API call failed: {e}")

                # Fallback
                from core.models_voice_marketplace import Voice
                voices = Voice.objects.filter(is_published=True)[:20]
                return {
                    'success': True,
                    'voices': [
                        {
                            'id': str(v.id),
                            'name': v.name,
                            'description': v.description[:100] if v.description else '',
                            'price': float(v.price_per_use) if hasattr(v, 'price_per_use') else 0
                        }
                        for v in voices
                    ],
                    'total': Voice.objects.filter(is_published=True).count(),
                    'summary': f"Found {voices.count()} published voices"
                }

            elif action == 'my_voices':
                try:
                    response = requests.get(f'{base_url}/my-voices/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'voices': response.json()}
                except:
                    pass
                return {'success': True, 'voices': [], 'message': 'No voices found'}

            elif action == 'earnings':
                try:
                    response = requests.get(f'{base_url}/earnings/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'earnings': response.json()}
                except:
                    pass
                return {'success': True, 'earnings': {'total': 0, 'pending': 0}}

            elif action == 'transactions':
                try:
                    response = requests.get(f'{base_url}/transactions/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'transactions': response.json()}
                except:
                    pass
                return {'success': True, 'transactions': []}

            elif action == 'detail':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.get(f'{base_url}/{voice_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'voice': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Voice not found'}

            elif action == 'create':
                elevenlabs_id = arguments.get('elevenlabs_voice_id')
                name = arguments.get('name')
                if not elevenlabs_id or not name:
                    return {'success': False, 'error': 'elevenlabs_voice_id and name required'}
                try:
                    response = requests.post(
                        f'{base_url}/create/',
                        json={'elevenlabs_voice_id': elevenlabs_id, 'name': name},
                        timeout=30
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'voice': response.json() if response.status_code in [200, 201] else None,
                        'message': 'Voice created' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'clone_start':
                try:
                    response = requests.post(f'{base_url}/clone/start/', json=arguments, timeout=30)
                    return {
                        'success': response.status_code in [200, 201],
                        'request': response.json() if response.status_code in [200, 201] else None
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'clone_status':
                request_id = arguments.get('request_id')
                if not request_id:
                    return {'success': False, 'error': 'request_id required'}
                try:
                    response = requests.get(f'{base_url}/clone/{request_id}/status/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'status': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Clone request not found'}

            elif action == 'publish':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/publish/',
                        json={'price': arguments.get('price', 0)},
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice published' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'unpublish':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.post(f'{base_url}/{voice_id}/unpublish/', timeout=10)
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice unpublished' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'generate':
                voice_id = arguments.get('voice_id')
                text = arguments.get('text')
                if not voice_id or not text:
                    return {'success': False, 'error': 'voice_id and text required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/generate/',
                        json={'text': text},
                        timeout=60
                    )
                    return {
                        'success': response.status_code == 200,
                        'audio_url': response.json().get('audio_url') if response.status_code == 200 else None,
                        'message': 'Speech generated' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'preview':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                try:
                    response = requests.get(f'{base_url}/{voice_id}/preview/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'preview': response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Preview not available'}

            elif action == 'add_review':
                voice_id = arguments.get('voice_id')
                rating = arguments.get('rating')
                review_text = arguments.get('review_text', '')
                if not voice_id or not rating:
                    return {'success': False, 'error': 'voice_id and rating required'}
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/reviews/',
                        json={'rating': rating, 'text': review_text},
                        timeout=10
                    )
                    return {
                        'success': response.status_code in [200, 201],
                        'message': 'Review added' if response.status_code in [200, 201] else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'update':
                voice_id = arguments.get('voice_id')
                if not voice_id:
                    return {'success': False, 'error': 'voice_id required'}
                update_data = {}
                if arguments.get('name'):
                    update_data['name'] = arguments['name']
                if arguments.get('description'):
                    update_data['description'] = arguments['description']
                try:
                    response = requests.post(
                        f'{base_url}/{voice_id}/update/',
                        json=update_data,
                        timeout=10
                    )
                    return {
                        'success': response.status_code == 200,
                        'message': 'Voice updated' if response.status_code == 200 else response.text
                    }
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing voice marketplace: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_hive_mind(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage Hive Mind sessions - multi-agent collective intelligence.
        """
        action = arguments.get('action', 'list')
        base_url = 'http://localhost:8000/api/hive-mind'

        try:
            if action == 'start':
                question = arguments.get('question')
                if not question:
                    return {'success': False, 'error': 'question required to start Hive Mind session'}

                context = arguments.get('context', '')
                max_agents = min(arguments.get('max_agents', 8), 12)

                try:
                    response = requests.post(
                        f'{base_url}/start/',
                        json={
                            'question': question,
                            'context': context,
                            'max_agents': max_agents
                        },
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        data = response.json()
                        return {
                            'success': True,
                            'session_id': data.get('session_id'),
                            'status': data.get('status'),
                            'participants': data.get('participants', []),
                            'participant_count': data.get('participant_count', 0),
                            'message': data.get('message', 'Hive Mind session started')
                        }
                    return {'success': False, 'error': response.text}
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'status':
                session_id = arguments.get('session_id')
                if not session_id:
                    return {'success': False, 'error': 'session_id required'}

                try:
                    response = requests.get(f'{base_url}/session/{session_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                    return {'success': False, 'error': 'Session not found'}
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            elif action == 'list':
                limit = arguments.get('limit', 10)
                try:
                    response = requests.get(f'{base_url}/sessions/', params={'limit': limit}, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models import HiveMindSession
                sessions = HiveMindSession.objects.order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'sessions': [
                        {
                            'id': str(s.id),
                            'question': s.question[:100] if s.question else '',
                            'status': s.status,
                            'participant_count': len(s.participant_ids) if s.participant_ids else 0,
                            'created_at': s.created_at.isoformat() if s.created_at else None
                        }
                        for s in sessions
                    ],
                    'total': sessions.count()
                }

            elif action == 'agents':
                try:
                    response = requests.get(f'{base_url}/agents/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import Agent
                agents = Agent.objects.filter(is_active=True).order_by('name')[:20]
                return {
                    'success': True,
                    'agents': [
                        {
                            'id': str(a.id),
                            'name': a.name,
                            'specialization': a.specialization or ''
                        }
                        for a in agents
                    ]
                }

            elif action == 'preview':
                question = arguments.get('question')
                if not question:
                    return {'success': False, 'error': 'question required for preview'}

                try:
                    response = requests.post(
                        f'{base_url}/preview/',
                        json={'question': question, 'max_agents': arguments.get('max_agents', 8)},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Preview not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing Hive Mind: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_time_capsules(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage agent time capsules - messages from agents to their future selves.
        """
        action = arguments.get('action', 'overview')
        base_url = 'http://localhost:8000/api/time-capsules'

        try:
            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                total = TimeCapsule.objects.count()
                revealed = TimeCapsule.objects.filter(status='revealed').count()
                ready = TimeCapsule.objects.filter(
                    status='sealed',
                    reveal_at__lte=timezone.now()
                ).count()
                recent = TimeCapsule.objects.order_by('-created_at')[:5]
                return {
                    'success': True,
                    'stats': {
                        'total': total,
                        'revealed': revealed,
                        'sealed': total - revealed,
                        'ready_to_reveal': ready
                    },
                    'recent': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'trigger': c.trigger or '',
                            'status': c.status,
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None,
                            'created_at': c.created_at.isoformat()
                        }
                        for c in recent
                    ]
                }

            elif action == 'list_agent':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                capsules = TimeCapsule.objects.filter(agent_id=agent_id).order_by('-created_at')[:10]
                return {
                    'success': True,
                    'capsules': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'trigger': c.trigger or '',
                            'status': c.status,
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None
                        }
                        for c in capsules
                    ]
                }

            elif action == 'create':
                agent_id = arguments.get('agent_id')
                message = arguments.get('message')
                if not agent_id or not message:
                    return {'success': False, 'error': 'agent_id and message required'}

                capsule_type = arguments.get('capsule_type', 'reflection')
                reveal_days = arguments.get('reveal_days', 7)

                try:
                    response = requests.post(
                        f'{base_url}/agent/{agent_id}/',
                        json={
                            'message': message,
                            'capsule_type': capsule_type,
                            'reveal_days': reveal_days
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct creation
                from core.models_unified_system import TimeCapsule, Agent
                from django.utils import timezone
                from datetime import timedelta
                try:
                    agent = Agent.objects.get(id=agent_id)
                    capsule = TimeCapsule.objects.create(
                        agent=agent,
                        title='Time Capsule Message',
                        message=message,
                        trigger=capsule_type,  # Uses 'trigger' field
                        status='sealed',
                        reveal_at=timezone.now() + timedelta(days=reveal_days)
                    )
                    return {
                        'success': True,
                        'capsule_id': str(capsule.id),
                        'reveal_at': capsule.reveal_at.isoformat(),
                        'message': f'Time capsule created for {agent.name}'
                    }
                except Agent.DoesNotExist:
                    return {'success': False, 'error': 'Agent not found'}

            elif action == 'detail':
                capsule_id = arguments.get('capsule_id')
                if not capsule_id:
                    return {'success': False, 'error': 'capsule_id required'}
                try:
                    response = requests.get(f'{base_url}/{capsule_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                try:
                    capsule = TimeCapsule.objects.select_related('agent').get(id=capsule_id)
                    is_revealed = capsule.status == 'revealed'
                    return {
                        'success': True,
                        'capsule': {
                            'id': str(capsule.id),
                            'title': capsule.title or '',
                            'agent_name': capsule.agent.name if capsule.agent else 'Unknown',
                            'trigger': capsule.trigger or '',
                            'message': capsule.message if is_revealed else '[SEALED]',
                            'status': capsule.status,
                            'reveal_at': capsule.reveal_at.isoformat() if capsule.reveal_at else None,
                            'created_at': capsule.created_at.isoformat()
                        }
                    }
                except TimeCapsule.DoesNotExist:
                    return {'success': False, 'error': 'Capsule not found'}

            elif action == 'reveal':
                capsule_id = arguments.get('capsule_id')
                if not capsule_id:
                    return {'success': False, 'error': 'capsule_id required'}
                try:
                    response = requests.post(f'{base_url}/{capsule_id}/reveal/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                try:
                    capsule = TimeCapsule.objects.get(id=capsule_id)
                    if capsule.status == 'revealed':
                        return {'success': False, 'error': 'Capsule already revealed'}
                    if capsule.reveal_at and capsule.reveal_at > timezone.now():
                        return {'success': False, 'error': f'Capsule not ready until {capsule.reveal_at}'}
                    capsule.status = 'revealed'
                    capsule.revealed_at = timezone.now()
                    capsule.save()
                    return {
                        'success': True,
                        'message': capsule.message,
                        'revealed_at': capsule.revealed_at.isoformat()
                    }
                except TimeCapsule.DoesNotExist:
                    return {'success': False, 'error': 'Capsule not found'}

            elif action == 'react':
                capsule_id = arguments.get('capsule_id')
                reaction = arguments.get('reaction')
                if not capsule_id or not reaction:
                    return {'success': False, 'error': 'capsule_id and reaction required'}
                try:
                    response = requests.post(
                        f'{base_url}/{capsule_id}/react/',
                        json={'reaction': reaction},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add reaction'}

            elif action == 'ready':
                try:
                    response = requests.get(f'{base_url}/ready-to-reveal/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import TimeCapsule
                from django.utils import timezone
                capsules = TimeCapsule.objects.filter(
                    status='sealed',
                    reveal_at__lte=timezone.now()
                ).select_related('agent').order_by('reveal_at')[:10]
                return {
                    'success': True,
                    'ready_capsules': [
                        {
                            'id': str(c.id),
                            'title': c.title or '',
                            'agent_name': c.agent.name if c.agent else 'Unknown',
                            'trigger': c.trigger or '',
                            'reveal_at': c.reveal_at.isoformat() if c.reveal_at else None
                        }
                        for c in capsules
                    ],
                    'count': capsules.count()
                }

            elif action == 'generate':
                try:
                    response = requests.post(f'{base_url}/generate/', timeout=30)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Auto-generation not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing time capsules: {e}")
            return {'success': False, 'error': str(e)}

    # ===== Phase 25: A/B Testing & Memory Clusters (Session 587) =====

    def _manage_ab_testing(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage A/B testing experiments.
        """
        action = arguments.get('action', 'dashboard')
        base_url = 'http://localhost:8000/api/ab-testing'

        try:
            if action == 'dashboard':
                try:
                    response = requests.get(f'{base_url}/dashboard/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import ABTest
                tests = ABTest.objects.all()
                status_counts = {
                    'draft': tests.filter(status='draft').count(),
                    'running': tests.filter(status='running').count(),
                    'paused': tests.filter(status='paused').count(),
                    'completed': tests.filter(status='completed').count(),
                }
                return {
                    'success': True,
                    'status_counts': status_counts,
                    'total_tests': sum(status_counts.values())
                }

            elif action == 'list':
                status_filter = arguments.get('status')
                try:
                    params = {'status': status_filter} if status_filter else {}
                    response = requests.get(f'{base_url}/tests/', params=params, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                tests = ABTest.objects.all()
                if status_filter:
                    tests = tests.filter(status=status_filter)
                tests = tests.order_by('-created_at')[:20]
                return {
                    'success': True,
                    'tests': [
                        {
                            'id': str(t.id),
                            'name': t.name,
                            'test_type': t.test_type,
                            'status': t.status,
                            'created_at': t.created_at.isoformat()
                        }
                        for t in tests
                    ]
                }

            elif action == 'create':
                name = arguments.get('name')
                test_type = arguments.get('test_type')
                if not name or not test_type:
                    return {'success': False, 'error': 'name and test_type required'}

                try:
                    response = requests.post(
                        f'{base_url}/tests/create/',
                        json={
                            'name': name,
                            'test_type': test_type,
                            'hypothesis': arguments.get('hypothesis', ''),
                            'description': arguments.get('description', '')
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                test = ABTest.objects.create(
                    name=name,
                    test_type=test_type,
                    hypothesis=arguments.get('hypothesis', ''),
                    description=arguments.get('description', ''),
                    status='draft'
                )
                return {
                    'success': True,
                    'test_id': str(test.id),
                    'message': f'A/B test "{name}" created'
                }

            elif action == 'detail':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.get(f'{base_url}/tests/{test_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                try:
                    test = ABTest.objects.get(id=test_id)
                    return {
                        'success': True,
                        'test': {
                            'id': str(test.id),
                            'name': test.name,
                            'test_type': test.test_type,
                            'status': test.status,
                            'hypothesis': test.hypothesis,
                            'created_at': test.created_at.isoformat()
                        }
                    }
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'start':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/start/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                from django.utils import timezone
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'running'
                    test.start_date = timezone.now()
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" started'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'pause':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/pause/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'paused'
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" paused'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'complete':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.post(f'{base_url}/tests/{test_id}/complete/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import ABTest
                from django.utils import timezone
                try:
                    test = ABTest.objects.get(id=test_id)
                    test.status = 'completed'
                    test.end_date = timezone.now()
                    test.save()
                    return {'success': True, 'message': f'Test "{test.name}" completed'}
                except ABTest.DoesNotExist:
                    return {'success': False, 'error': 'Test not found'}

            elif action == 'results':
                test_id = arguments.get('test_id')
                if not test_id:
                    return {'success': False, 'error': 'test_id required'}
                try:
                    response = requests.get(f'{base_url}/tests/{test_id}/results/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Results not available'}

            elif action == 'add_variant':
                test_id = arguments.get('test_id')
                variant_name = arguments.get('variant_name')
                if not test_id or not variant_name:
                    return {'success': False, 'error': 'test_id and variant_name required'}
                try:
                    response = requests.post(
                        f'{base_url}/tests/{test_id}/variants/',
                        json={
                            'name': variant_name,
                            'config': arguments.get('variant_config', {})
                        },
                        timeout=10
                    )
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add variant'}

            elif action == 'record_event':
                variant_id = arguments.get('variant_id')
                event_type = arguments.get('event_type')
                if not variant_id or not event_type:
                    return {'success': False, 'error': 'variant_id and event_type required'}
                try:
                    response = requests.post(
                        f'{base_url}/variants/{variant_id}/event/',
                        json={'event_type': event_type},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to record event'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing A/B testing: {e}")
            return {'success': False, 'error': str(e)}

    def _manage_memory_clusters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 587: Manage agent memory clusters - semantic grouping of memories.
        """
        action = arguments.get('action', 'overview')
        base_url = 'http://localhost:8000/api/memory-clusters'

        try:
            if action == 'overview':
                try:
                    response = requests.get(f'{base_url}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback to direct DB query
                from core.models_unified_system import MemoryCluster
                total_clusters = MemoryCluster.objects.count()
                clusters_by_agent = {}
                for cluster in MemoryCluster.objects.select_related('agent').all()[:50]:
                    agent_name = cluster.agent.name if cluster.agent else 'Cross-Agent'
                    if agent_name not in clusters_by_agent:
                        clusters_by_agent[agent_name] = 0
                    clusters_by_agent[agent_name] += 1
                return {
                    'success': True,
                    'stats': {
                        'total_clusters': total_clusters,
                        'agents_with_clusters': len(clusters_by_agent)
                    },
                    'clusters_by_agent': clusters_by_agent
                }

            elif action == 'list_agent':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/agent/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import MemoryCluster
                clusters = MemoryCluster.objects.filter(agent_id=agent_id).order_by('-created_at')[:20]
                return {
                    'success': True,
                    'clusters': [
                        {
                            'id': str(c.id),
                            'name': c.name,
                            'description': c.description or '',
                            'memory_count': c.memories.count(),
                            'coherence_score': c.coherence_score,
                            'created_at': c.created_at.isoformat()
                        }
                        for c in clusters
                    ]
                }

            elif action == 'generate':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.post(f'{base_url}/agent/{agent_id}/', timeout=60)
                    if response.status_code in [200, 201]:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Cluster generation not available'}

            elif action == 'detail':
                cluster_id = arguments.get('cluster_id')
                if not cluster_id:
                    return {'success': False, 'error': 'cluster_id required'}
                try:
                    response = requests.get(f'{base_url}/cluster/{cluster_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                # Fallback
                from core.models_unified_system import MemoryCluster
                try:
                    cluster = MemoryCluster.objects.select_related('agent').get(id=cluster_id)
                    return {
                        'success': True,
                        'cluster': {
                            'id': str(cluster.id),
                            'name': cluster.name,
                            'description': cluster.description or '',
                            'agent_name': cluster.agent.name if cluster.agent else 'Cross-Agent',
                            'memory_count': cluster.memories.count(),
                            'coherence_score': cluster.coherence_score,
                            'keywords': cluster.keywords or [],
                            'created_at': cluster.created_at.isoformat()
                        }
                    }
                except MemoryCluster.DoesNotExist:
                    return {'success': False, 'error': 'Cluster not found'}

            elif action == 'add_memory':
                cluster_id = arguments.get('cluster_id')
                memory_id = arguments.get('memory_id')
                if not cluster_id or not memory_id:
                    return {'success': False, 'error': 'cluster_id and memory_id required'}
                try:
                    response = requests.post(
                        f'{base_url}/cluster/{cluster_id}/add-memory/',
                        json={'memory_id': memory_id},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Failed to add memory to cluster'}

            elif action == 'remove_memory':
                cluster_id = arguments.get('cluster_id')
                memory_id = arguments.get('memory_id')
                if not cluster_id or not memory_id:
                    return {'success': False, 'error': 'cluster_id and memory_id required'}
                try:
                    response = requests.delete(
                        f'{base_url}/cluster/{cluster_id}/memory/{memory_id}/',
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'message': 'Memory removed from cluster'}
                except:
                    pass
                return {'success': False, 'error': 'Failed to remove memory from cluster'}

            elif action == 'evolution':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required'}
                try:
                    response = requests.get(f'{base_url}/evolution/{agent_id}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Evolution data not available'}

            elif action == 'find_similar':
                query = arguments.get('query')
                if not query:
                    return {'success': False, 'error': 'query required'}
                try:
                    response = requests.post(
                        f'{base_url}/find-similar/',
                        json={'query': query},
                        timeout=15
                    )
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Similar cluster search not available'}

            elif action == 'visualization':
                agent_id = arguments.get('agent_id')
                url = f'{base_url}/visualization/{agent_id}/' if agent_id else f'{base_url}/visualization/'
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Visualization data not available'}

            elif action == 'generate_all':
                try:
                    response = requests.post(f'{base_url}/generate-all/', timeout=120)
                    if response.status_code == 200:
                        return {'success': True, **response.json()}
                except:
                    pass
                return {'success': False, 'error': 'Cluster generation for all agents not available'}

            return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error managing memory clusters: {e}")
            return {'success': False, 'error': str(e)}
