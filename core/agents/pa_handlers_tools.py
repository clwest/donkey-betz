"""
PersonalAssistantAgent PAToolHandlersMixin — extracted handler methods.
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




class PAToolHandlersMixin:
    """Mixin providing handler methods for PersonalAssistantAgent."""

    def _analyze_project_intelligence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Get deep intelligence for a project.
        """
        try:
            from core.models_partnership import PartnershipProject
            from core.models_unified_system import (
                AgentKnowledgeSource, HiveMindSession, AgentDream, SpiderData
            )
            from django.utils import timezone
            from datetime import timedelta

            project_name = arguments.get('project_name', '').strip()
            if not project_name:
                return {
                    'success': False,
                    'error': 'Project name is required'
                }

            include_sections = arguments.get('include_sections', ['learnings', 'conversations', 'dreams', 'spider_data', 'recommendations'])
            time_period = arguments.get('time_period', '7d')

            # Find the project
            project = PartnershipProject.objects.filter(
                project_name__icontains=project_name
            ).first()

            if not project:
                return {
                    'success': False,
                    'error': f'Project "{project_name}" not found'
                }

            # Time filter
            time_map = {
                '24h': timedelta(hours=24),
                '7d': timedelta(days=7),
                '30d': timedelta(days=30),
                'all': timedelta(days=365*10)
            }
            cutoff = timezone.now() - time_map.get(time_period, timedelta(days=7))

            results = {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'status': project.status,
                'sections': {}
            }
            summary_lines = [f"**Project Intelligence: {project.project_name}**\n"]

            # Learnings
            if 'learnings' in include_sections:
                learnings = AgentKnowledgeSource.objects.filter(
                    project=project,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:10]

                results['sections']['learnings'] = {
                    'count': learnings.count(),
                    'items': [{'title': l.title[:50], 'agent': l.source_agent.name if l.source_agent else 'Unknown'} for l in learnings[:5]]
                }
                summary_lines.append(f"📚 **Learnings:** {learnings.count()} knowledge items")

            # Conversations
            if 'conversations' in include_sections:
                conversations = HiveMindSession.objects.filter(
                    project=project,
                    created_at__gte=cutoff
                ).order_by('-created_at')[:10]

                results['sections']['conversations'] = {
                    'count': conversations.count(),
                    'items': [{'topic': c.conversation_topic or c.question or 'Untitled', 'status': c.status} for c in conversations[:5]]
                }
                summary_lines.append(f"💬 **Conversations:** {conversations.count()} agent discussions")

            # Dreams
            if 'dreams' in include_sections:
                dreams = AgentDream.objects.filter(
                    project=project,
                    dreamed_at__gte=cutoff
                ).order_by('-composite_score')[:10]

                results['sections']['dreams'] = {
                    'count': dreams.count(),
                    'items': [{'title': d.title[:50], 'score': float(d.composite_score)} for d in dreams[:5]]
                }
                summary_lines.append(f"💭 **Dreams:** {dreams.count()} creative ideas")

            # Spider data
            if 'spider_data' in include_sections:
                # Check for project-related spider data via tags or topics
                project_keywords = project.project_name.lower().split()
                spider_count = SpiderData.objects.filter(
                    created_at__gte=cutoff
                ).count()  # Simplified - would need proper project linking

                results['sections']['spider_data'] = {
                    'count': spider_count,
                    'note': 'Spider data related to project topics'
                }
                summary_lines.append(f"🕷️ **Spider Data:** {spider_count} recent items")

            # Recommendations
            if 'recommendations' in include_sections:
                recommendations = []
                if results['sections'].get('dreams', {}).get('count', 0) > 5:
                    recommendations.append("Consider reviewing high-score dreams for actionable ideas")
                if results['sections'].get('conversations', {}).get('count', 0) < 3:
                    recommendations.append("Trigger more agent conversations to generate insights")
                if results['sections'].get('learnings', {}).get('count', 0) > 20:
                    recommendations.append("Rich knowledge base - consider synthesizing key learnings")

                results['sections']['recommendations'] = recommendations
                if recommendations:
                    summary_lines.append(f"\n💡 **Recommendations:**")
                    for rec in recommendations[:3]:
                        summary_lines.append(f"  - {rec}")

            results['summary'] = '\n'.join(summary_lines)

            return {
                'success': True,
                **results
            }

        except Exception as e:
            logger.error(f"Error analyzing project intelligence: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: ThinkingAgent/System Insights Tools
    # =========================================================================

    def _create_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Create a new boardroom decision for review.
        """
        try:
            from core.models_unified_system import AgentDecisionSummary
            import uuid

            title = arguments.get('title', '')
            description = arguments.get('description', '')
            decision_type = arguments.get('decision_type', 'policy')
            priority = arguments.get('priority', 'medium')

            if not title or not description:
                return {
                    'success': False,
                    'error': 'Both title and description are required'
                }

            # Create the decision
            decision = AgentDecisionSummary.objects.create(
                decision_id=f"decision_{uuid.uuid4()}",
                title=title[:200],
                summary=description,
                decision_type=decision_type,
                priority=priority,
                status='pending',
                source='personal_assistant'
            )

            return {
                'success': True,
                'decision_id': decision.decision_id,
                'title': title,
                'decision_type': decision_type,
                'priority': priority,
                'summary': f"**Boardroom Decision Created:**\n\n📋 **{title}**\n\nType: {decision_type}\nPriority: {priority}\nStatus: Pending\n\nID: {decision.decision_id}\n\nThe decision is now available in the Boardroom for review and promotion."
            }

        except Exception as e:
            logger.error(f"Error creating boardroom decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Trigger content creation by routing to appropriate agent.
        """
        try:
            content_type = arguments.get('content_type', 'image')
            prompt = arguments.get('prompt', '')
            style = arguments.get('style', '')

            if not prompt:
                return {
                    'success': False,
                    'error': 'Please provide a prompt describing what to create'
                }

            # Map content type to agent
            agent_map = {
                'image': 'ImageAgent',
                'video': 'VideoAgent',
                'blog_post': 'ContentWriterAgent',
                'social_post': 'SocialMediaAgent',
                'logo': 'BrandIdentityAgent'
            }

            agent_name = agent_map.get(content_type)
            if not agent_name:
                return {
                    'success': False,
                    'error': f"Unknown content type: {content_type}"
                }

            # Build task with style if provided
            task = prompt
            if style:
                task = f"{prompt} (Style: {style})"

            # Route to agent
            try:
                result = self.router.route(agent_name, task, {
                    'content_type': content_type,
                    'style': style,
                    'prompt': prompt
                })

                return {
                    'success': True,
                    'agent': agent_name,
                    'content_type': content_type,
                    'result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                    'summary': f"**Content Creation Started:**\n\n🎨 Agent: {agent_name}\n📝 Type: {content_type}\n💭 Prompt: {prompt[:100]}..."
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Agent routing failed: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Error creating content: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Create a new project.
        """
        try:
            from core.models_partnership import PartnershipProject
            from django.utils import timezone

            name = arguments.get('name', '').strip()
            if not name:
                return {
                    'success': False,
                    'error': 'Project name is required'
                }

            description = arguments.get('description', '')
            category = arguments.get('category', 'general')
            goal = arguments.get('goal', '')
            tags = arguments.get('tags', [])

            # Create the project
            project = PartnershipProject.objects.create(
                user=self.user,
                project_name=name,
                project_type=category,
                description=description,
                goal=goal,
                status='planning',
                category=category,
                tags=tags if isinstance(tags, list) else [],
                ai_contribution_percent=50,
                human_contribution_percent=50
            )

            logger.info(f"✅ PA created project: {project.project_name}")

            return {
                'success': True,
                'project_id': str(project.id),
                'project_name': project.project_name,
                'summary': f"**Project Created!**\n\n📁 **{project.project_name}**\n- Category: {category}\n- Status: planning\n- Goal: {goal[:100] if goal else 'Not specified'}\n\nYou can now assign agents and start work on this project."
            }

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_spider(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 577: Run a specific spider on demand to fetch fresh data.
        """
        try:
            from ai_core.spiders.spider_registry import SpiderRegistry
            import asyncio
            import inspect

            spider_name = arguments.get('spider_name')
            category = arguments.get('category')
            max_results = arguments.get('max_results', 20)

            registry = SpiderRegistry()

            # Category to spider mapping
            category_spiders = {
                'tech': ['hackernews', 'techcrunch', 'devto', 'github', 'producthunt'],
                'finance': ['coingecko', 'yahoo_finance', 'polygon_finance', 'finnhub'],
                'news': ['cnn', 'bbc', 'npr', 'reuters_rss', 'axios'],
                'legal': ['courtlistener', 'findlaw', 'colorado_family_law'],
                'entertainment': ['variety', 'polygon_gaming', 'spotify'],
                'jobs': ['remoteok', 'weworkremotely', 'adzuna'],
                'crypto': ['coingecko', 'etherscan_api']
            }

            # Determine which spiders to run
            if spider_name:
                spiders_to_run = [spider_name]
            elif category and category in category_spiders:
                spiders_to_run = category_spiders[category]
            else:
                return {
                    'success': False,
                    'error': 'Please provide either spider_name or category'
                }

            results = []
            errors = []

            for name in spiders_to_run:
                spider_class = registry.get_spider_class(name)
                if not spider_class or spider_class.__name__ == 'BaseIntelligenceSpider':
                    errors.append(f"Spider '{name}' not found")
                    continue

                try:
                    spider = spider_class()

                    # Run fetch_data
                    if hasattr(spider, 'fetch_data'):
                        fetch_method = spider.fetch_data

                        if asyncio.iscoroutinefunction(fetch_method):
                            # Async spider
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                data = loop.run_until_complete(fetch_method(max_results=max_results))
                            finally:
                                loop.close()
                        else:
                            # Sync spider
                            data = fetch_method(max_results=max_results)

                        if data:
                            item_count = len(data) if isinstance(data, list) else 1
                            results.append({
                                'spider': name,
                                'items_fetched': item_count,
                                'sample': data[:3] if isinstance(data, list) else data
                            })
                    else:
                        errors.append(f"Spider '{name}' has no fetch_data method")

                except Exception as e:
                    errors.append(f"Spider '{name}' error: {str(e)[:100]}")

            # Build summary
            total_items = sum(r['items_fetched'] for r in results)
            summary_lines = [f"**Spider Execution Results:**\n"]

            if results:
                summary_lines.append(f"✅ Fetched {total_items} items from {len(results)} spiders:")
                for r in results:
                    summary_lines.append(f"  • {r['spider']}: {r['items_fetched']} items")
            else:
                summary_lines.append("❌ No data fetched")

            if errors:
                summary_lines.append(f"\n⚠️ Errors ({len(errors)}):")
                for e in errors[:3]:
                    summary_lines.append(f"  • {e}")

            return {
                'success': len(results) > 0,
                'spiders_run': len(spiders_to_run),
                'successful': len(results),
                'total_items': total_items,
                'results': results,
                'errors': errors,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error executing spider: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _execute_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Execute a multi-step workflow using WorkflowAgent.
        """
        try:
            from core.agents.workflow_agent import WorkflowAgent

            workflow_description = arguments.get('workflow_description', '')
            workflow_type = arguments.get('workflow_type', 'custom')

            if not workflow_description:
                return {
                    'success': False,
                    'error': 'Please provide a workflow_description'
                }

            # Create workflow agent and execute
            workflow_agent = WorkflowAgent(user=self.user)

            # Build context
            context = {
                'workflow_type': workflow_type,
                'requested_by': 'PersonalAssistant'
            }

            # Execute workflow
            # Session 739: Pass spider_context to sub-agents for real intelligence
            result = workflow_agent.execute(
                task=workflow_description,
                context=context,
                scifi_context=getattr(self, '_current_scifi_context', {}),
                spider_context=getattr(self, '_current_spider_context', {})
            )

            # Build summary
            if hasattr(result, 'to_dict'):
                result_dict = result.to_dict()
            else:
                result_dict = {'output': str(result)}

            return {
                'success': True,
                'workflow_type': workflow_type,
                'description': workflow_description,
                'result': result_dict,
                'summary': f"**Workflow Executed:**\n\n🔄 Type: {workflow_type}\n📝 Task: {workflow_description[:100]}...\n\n{result_dict.get('content', result_dict.get('output', 'Completed'))[:500]}"
            }

        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _format_scores_summary(self, games: list, sport: str) -> str:
        """Format games into a readable summary."""
        lines = [f"**{sport.upper()} Scores:**\n"]

        live = [g for g in games if g['is_live']]
        final = [g for g in games if g['is_final']]
        upcoming = [g for g in games if not g['is_live'] and not g['is_final']]

        if live:
            lines.append("🔴 **LIVE:**")
            for g in live:
                lines.append(f"  {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']} ({g['status']})")

        if final:
            lines.append("\n✅ **FINAL:**")
            for g in final[:5]:  # Limit to 5
                winner = g['away_team'] if g['away_score'] > g['home_score'] else g['home_team']
                lines.append(f"  {g['away_team']} {g['away_score']} @ {g['home_team']} {g['home_score']} - {winner} wins")

        if upcoming and not live and not final:
            lines.append("\n📅 **UPCOMING:**")
            for g in upcoming[:5]:
                lines.append(f"  {g['matchup']} - {g['status']}")

        return '\n'.join(lines)

    # =========================================================================
    # Session 576: System Status & Intelligence Tools
    # =========================================================================

    def _generate_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate images using AI image agents.
        """
        try:
            prompt = arguments.get('prompt', '')
            style = arguments.get('style', 'realistic')
            size = arguments.get('size', '1024x1024')
            image_type = arguments.get('image_type', 'general')

            if not prompt:
                return {'success': False, 'error': 'Prompt is required'}

            # Delegate to ImageAgent
            result = self.router.route(
                agent_name='ImageAgent',
                task=f"Create a {image_type} image: {prompt}. Style: {style}, Size: {size}",
                context={
                    'prompt': prompt,
                    'style': style,
                    'size': size,
                    'image_type': image_type
                }
            )

            return {
                'success': result.success,
                'message': result.message if result.success else result.error,
                'data': result.data if result.success else {},
                'summary': f"Image generation {'started' if result.success else 'failed'}: {prompt[:50]}..."
            }

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # Session 581: Phase 10 - Betting/Sports Tools
    # =========================================================================

    def _generate_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate videos using AI video agents.
        """
        try:
            prompt = arguments.get('prompt', '')
            video_type = arguments.get('video_type', 'text_to_video')
            duration = arguments.get('duration', 30)
            style = arguments.get('style', 'cinematic')
            aspect_ratio = arguments.get('aspect_ratio', '16:9')

            if not prompt:
                return {'success': False, 'error': 'Prompt is required'}

            # Delegate to VideoAgent
            result = self.router.route(
                agent_name='VideoAgent',
                task=f"Create a {video_type} video: {prompt}. Style: {style}, Duration: {duration}s, Aspect: {aspect_ratio}",
                context={
                    'video_type': video_type,
                    'duration': duration,
                    'style': style,
                    'aspect_ratio': aspect_ratio
                }
            )

            return {
                'success': result.success,
                'message': result.message if result.success else result.error,
                'data': result.data if result.success else {},
                'summary': f"Video generation {'started' if result.success else 'failed'}: {prompt[:50]}..."
            }

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return {'success': False, 'error': str(e)}

    def _is_question(self, task: str) -> Tuple[bool, str]:
        """
        Determine if the task is a question (requiring direct answer) vs action request.

        Session 454: MAJOR FIX - Distinguish informational questions from action requests.
        - "What's trending in AI?" → Answer directly with spider data (informational)
        - "Research AI trends for my report" → Route to ResearchAgent (action request)

        Session 574: Added follow-up detection for "complete the tasks you suggested" patterns.

        Returns:
            Tuple of (is_question, question_type)
            - question_type can be: 'knowledge_question', 'trend_question', 'direct_question', 'followup_request', ''
        """
        task_lower = task.lower().strip()

        # Session 574: FOLLOW-UP detection - Split into INFORMATIONAL vs ACTION
        # INFORMATIONAL follow-ups = answer directly (explain the tasks)
        # ACTION follow-ups = route to agents (actually DO the tasks)

        # INFORMATIONAL patterns - user wants info about previous response
        info_followup_indicators = [
            'what were those', 'what are those', 'tell me more about',
            'explain those', 'describe those', 'which tasks',
            'what tasks', 'what items', 'list those',
        ]
        if any(indicator in task_lower for indicator in info_followup_indicators):
            logger.info(f"Detected INFO follow-up (answering directly): {task[:50]}")
            return True, 'followup_request'

        # ACTION follow-up patterns - these should route to WorkflowAgent!
        # We detect them here but return False so they go through _detect_agent()
        action_followup_indicators = [
            'complete the tasks', 'complete those tasks', 'complete all tasks',
            'complete the checklist', 'complete this checklist', 'complete that checklist',
            'do the tasks', 'do those tasks', 'do what you suggested',
            'work on those', 'work on the tasks', 'work on those items',
            'proceed with', 'go ahead and', 'yes do it', 'yes, do it',
            'address those', 'handle those', 'take care of those',
            'complete them', 'do them', 'finish them', 'execute',
            'you recommended', 'since you suggested', 'as you suggested',
            'lets use', "let's use", 'i choose', 'i pick', 'i select',
            # Session 574: Triage/planning patterns
            'triage these', 'triage the', 'triage those', 'triage ',
            'action plan', 'create a plan', 'draft a plan', 'make a plan',
            'prioritize these', 'prioritize those', 'prioritize the',
            'owners and timelines', 'assign owners', 'with owners',
            # Session 574: Draft/create for items patterns
            'draft the', 'create the', 'write the', 'prepare the',
            'for those items', 'for those research', 'for the items',
            'decision briefs', 'action items', 'those three', 'those five',
            'the three', 'the five', 'all three', 'all five',
        ]
        if any(indicator in task_lower for indicator in action_followup_indicators):
            # This is an ACTION request - let it flow to _detect_agent() for WorkflowAgent routing
            logger.info(f"Detected ACTION follow-up (routing to agents): {task[:50]}")
            return False, ''  # NOT a question - route to agents!

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

        # Session 459: SEC/financial queries need to route to ResearchAgent FIRST
        # (before trend_question check, since "latest" is a trend indicator)
        sec_indicators = ['sec filing', 'sec filings', '10-k', '10k', '10-q', '10q', '8-k', '8k', 'edgar', 'company filing']
        if any(indicator in task_lower for indicator in sec_indicators):
            # SEC queries need to go to ResearchAgent to use the SEC spider
            logger.info(f"Routing SEC query to ResearchAgent: {task[:50]}")
            return False, ''

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

    def _list_boardroom_decisions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 944: List boardroom decisions with pagination support.
        Returns actual items from AgentDecisionSummary.
        """
        try:
            from core.models_unified_system import AgentDecisionSummary

            status_filter = arguments.get('status', 'draft')
            decision_type = arguments.get('decision_type', 'all')
            limit = min(arguments.get('limit', 50), 100)  # Cap at 100
            offset = arguments.get('offset', 0)

            # Build query
            query = AgentDecisionSummary.objects.all()

            # Filter by status
            if status_filter == 'draft':
                query = query.filter(status='draft')
            elif status_filter == 'review':
                query = query.filter(status='review')
            # 'all' shows both draft and review

            # Filter by decision type
            if decision_type and decision_type != 'all':
                query = query.filter(decision_type=decision_type)

            # Get total count
            total_count = query.count()

            # Get paginated results
            decisions = query.order_by('-created_at')[offset:offset + limit]

            # Build items list
            items = []
            for d in decisions:
                items.append({
                    'id': str(d.id),
                    'topic': d.topic,
                    'decision_type': d.decision_type,
                    'impact_area': d.impact_area,
                    'status': d.status,
                    'recommended_stance': d.recommended_stance[:200] if d.recommended_stance else '',
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                })

            # Build summary
            summary_lines = [f"**Boardroom Decisions** ({total_count} total)\n"]

            if not items:
                summary_lines.append("No decisions found matching criteria.")
            else:
                # Group by type for display
                by_type = {}
                for item in items:
                    t = item['decision_type']
                    if t not in by_type:
                        by_type[t] = []
                    by_type[t].append(item)

                type_icons = {
                    'product': '🎯',
                    'experiment': '🧪',
                    'pipeline': '⚡',
                    'policy': '📜',
                    'architecture': '🏗️',
                    'guideline': '📋',
                }

                for dtype, dtype_items in by_type.items():
                    icon = type_icons.get(dtype, '📌')
                    summary_lines.append(f"\n{icon} **{dtype.title()}** ({len(dtype_items)}):")
                    for item in dtype_items[:10]:  # Show up to 10 per type in summary
                        summary_lines.append(f"  • {item['topic'][:60]}")
                        summary_lines.append(f"    ID: {item['id'][:8]}...")

                if total_count > offset + limit:
                    summary_lines.append(f"\n... and {total_count - offset - limit} more. Use offset={offset + limit} for next page.")

            return {
                'success': True,
                'total_count': total_count,
                'returned_count': len(items),
                'offset': offset,
                'limit': limit,
                'items': items,
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error listing boardroom decisions: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _promote_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Approve a pending boardroom decision.
        Wraps /api/boardroom/decisions/{id}/promote/
        """
        import requests

        decision_id = arguments.get('decision_id')

        if not decision_id:
            return {
                'success': False,
                'error': 'decision_id is required'
            }

        try:
            # Call internal API
            response = requests.post(
                f'http://localhost:8000/api/boardroom/decisions/{decision_id}/promote/',
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', f'Decision {decision_id} approved'),
                    'decision_id': decision_id
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f'Decision {decision_id} not found'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned {response.status_code}: {response.text}'
                }

        except Exception as e:
            logger.error(f"Error promoting decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _reject_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 576: Reject a pending boardroom decision.
        Wraps /api/boardroom/decisions/{id}/reject/
        """
        import requests

        decision_id = arguments.get('decision_id')
        reason = arguments.get('reason', '')

        if not decision_id:
            return {
                'success': False,
                'error': 'decision_id is required'
            }

        if not reason:
            return {
                'success': False,
                'error': 'reason is required for rejection'
            }

        try:
            # Call internal API
            response = requests.post(
                f'http://localhost:8000/api/boardroom/decisions/{decision_id}/reject/',
                json={'reason': reason},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', f'Decision {decision_id} rejected'),
                    'decision_id': decision_id,
                    'reason': reason
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': f'Decision {decision_id} not found'
                }
            else:
                return {
                    'success': False,
                    'error': f'API returned {response.status_code}: {response.text}'
                }

        except Exception as e:
            logger.error(f"Error rejecting decision: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _run_diagnostics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run system diagnostics and health checks.
        """
        try:
            import requests
            diagnostic_type = arguments.get('diagnostic_type', 'quick')
            include_details = arguments.get('include_details', False)

            results = {'success': True, 'diagnostic_type': diagnostic_type, 'checks': {}}

            # Quick health check
            if diagnostic_type in ['quick', 'full']:
                try:
                    response = requests.get('http://localhost:8000/health/ping/', timeout=5)
                    results['checks']['web_server'] = {'status': 'healthy' if response.status_code == 200 else 'unhealthy'}
                except:
                    results['checks']['web_server'] = {'status': 'unreachable'}

            # Database check
            if diagnostic_type in ['database', 'full']:
                try:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                    results['checks']['database'] = {'status': 'healthy'}
                except Exception as e:
                    results['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}

            # Agent check
            if diagnostic_type in ['agents', 'full']:
                from core.models_unified_system import Agent
                active_agents = Agent.objects.filter(is_active=True).count()
                results['checks']['agents'] = {'status': 'healthy', 'active_count': active_agents}

            # Spider check
            if diagnostic_type in ['spiders', 'full']:
                try:
                    response = requests.get('http://localhost:8000/api/diagnostics/test-spiders/', timeout=30)
                    if response.status_code == 200:
                        results['checks']['spiders'] = response.json()
                    else:
                        # Fallback
                        from ai_core.spiders.spider_registry import SpiderRegistry
                        results['checks']['spiders'] = {'status': 'available', 'count': len(SpiderRegistry._spiders)}
                except:
                    from ai_core.spiders.spider_registry import SpiderRegistry
                    results['checks']['spiders'] = {'status': 'available', 'count': len(SpiderRegistry._spiders)}

            # Celery check
            if diagnostic_type in ['celery', 'full']:
                try:
                    from core.celery import app
                    inspect = app.control.inspect()
                    active = inspect.active()
                    results['checks']['celery'] = {
                        'status': 'healthy' if active else 'no_workers',
                        'workers': len(active) if active else 0
                    }
                except Exception as e:
                    results['checks']['celery'] = {'status': 'error', 'error': str(e)}

            # Services check
            if diagnostic_type in ['services', 'full']:
                services_ok = 0
                services_list = ['redis', 'postgres']
                for svc in services_list:
                    try:
                        if svc == 'redis':
                            import redis
                            r = redis.Redis()
                            r.ping()
                            services_ok += 1
                    except:
                        pass
                results['checks']['services'] = {'healthy': services_ok, 'total': len(services_list)}

            # Build summary
            healthy_count = sum(1 for c in results['checks'].values() if c.get('status') == 'healthy')
            total_checks = len(results['checks'])
            results['summary'] = f"## Diagnostics ({diagnostic_type})\n\n**Health:** {healthy_count}/{total_checks} checks passed"

            for name, check in results['checks'].items():
                status_icon = "✅" if check.get('status') == 'healthy' else "❌"
                results['summary'] += f"\n- {status_icon} **{name}:** {check.get('status', 'unknown')}"

            return results

        except Exception as e:
            logger.error(f"Error running diagnostics: {e}")
            return {'success': False, 'error': str(e)}

    def _schedule_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Schedule content for distribution.
        """
        try:
            from core.models_unified_system import ContentDistribution
            from django.utils import timezone
            from django.utils.dateparse import parse_datetime

            title = arguments.get('title', '').strip()
            content = arguments.get('content', '').strip()

            if not title:
                return {
                    'success': False,
                    'error': 'Content title is required'
                }

            if not content:
                return {
                    'success': False,
                    'error': 'Content body is required'
                }

            platforms = arguments.get('platforms', ['twitter'])
            schedule_time_str = arguments.get('schedule_time')
            tags = arguments.get('tags', [])

            # Parse schedule time if provided
            schedule_time = None
            if schedule_time_str:
                schedule_time = parse_datetime(schedule_time_str)

            created_distributions = []
            summary_lines = ["**Content Scheduled:**\n"]

            for platform in platforms:
                try:
                    dist = ContentDistribution.objects.create(
                        user=self.user,
                        title=title,
                        description=content,
                        content_type='post',
                        tags=tags if isinstance(tags, list) else [],
                        platform_listing_id=None,  # Will be set when actually published
                    )
                    created_distributions.append({
                        'id': str(dist.id),
                        'platform': platform,
                        'scheduled_for': schedule_time.isoformat() if schedule_time else 'immediate'
                    })

                    time_str = schedule_time.strftime('%Y-%m-%d %H:%M') if schedule_time else 'Now'
                    summary_lines.append(f"📤 **{platform.title()}** - {time_str}")

                except Exception as platform_error:
                    logger.warning(f"Failed to schedule for {platform}: {platform_error}")

            if not created_distributions:
                return {
                    'success': False,
                    'error': 'Failed to schedule content for any platform'
                }

            summary_lines.append(f"\n📝 Title: {title[:50]}...")
            if tags:
                summary_lines.append(f"🏷️ Tags: {', '.join(tags[:5])}")

            return {
                'success': True,
                'distributions': created_distributions,
                'count': len(created_distributions),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error scheduling content: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _search_knowledge(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 578: Search the collective knowledge base.
        """
        try:
            from core.models_unified_system import AgentKnowledgeSource
            from django.db.models import Q

            query = arguments.get('query', '')
            knowledge_type = arguments.get('knowledge_type', 'all')
            limit = arguments.get('limit', 10)

            if not query:
                return {
                    'success': False,
                    'error': 'Please provide a search query'
                }

            # Build search query
            search_filter = Q(title__icontains=query) | Q(summary__icontains=query)

            knowledge_query = AgentKnowledgeSource.objects.filter(
                search_filter,
                is_active=True
            )

            # Filter by knowledge type
            if knowledge_type != 'all':
                knowledge_query = knowledge_query.filter(knowledge_type=knowledge_type)

            # Order by relevance (confidence + freshness)
            knowledge_items = knowledge_query.order_by('-confidence_score', '-freshness_score')[:limit]

            # Build results
            results = []
            summary_lines = [f"**Knowledge Search: '{query}'**\n"]

            if not knowledge_items:
                summary_lines.append("No matching knowledge found.")
                summary_lines.append("\nTry a different search term or check agent learning dashboard.")
            else:
                summary_lines.append(f"Found {knowledge_items.count()} results:\n")

                for item in knowledge_items:
                    results.append({
                        'id': str(item.id),
                        'title': item.title,
                        'type': item.knowledge_type,
                        'agent': item.agent.name if item.agent else 'Unknown',
                        'summary': item.summary[:200],
                        'confidence': item.confidence_score,
                        'freshness': item.freshness_score
                    })

                    confidence_emoji = '🟢' if item.confidence_score > 0.7 else '🟡' if item.confidence_score > 0.4 else '🔴'
                    summary_lines.append(f"{confidence_emoji} **{item.title[:50]}...**")
                    summary_lines.append(f"   Type: {item.knowledge_type} | Agent: {item.agent.name if item.agent else 'Unknown'}")
                    summary_lines.append(f"   {item.summary[:100]}...")
                    summary_lines.append("")

            return {
                'success': True,
                'query': query,
                'knowledge_type': knowledge_type,
                'results': results,
                'total_found': len(results),
                'summary': '\n'.join(summary_lines)
            }

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # =========================================================================
    # Session 579: Phase 4 Tool Handlers
    # =========================================================================

    def _time_travel_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Access agent memory time-travel capabilities.
        """
        try:
            import requests
            action = arguments.get('action', 'list_snapshots')
            agent_name = arguments.get('agent_name')
            base_url = 'http://localhost:8000/api/time-travel'

            if action == 'list_snapshots':
                url = f'{base_url}/snapshots/'
                if agent_name:
                    url += f'?agent={agent_name}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    snapshots = response.json()
                    return {
                        'success': True,
                        'snapshots': snapshots[:20] if isinstance(snapshots, list) else snapshots.get('snapshots', [])[:20],
                        'summary': f"Found memory snapshots"
                    }

            elif action == 'get_snapshot':
                snapshot_date = arguments.get('snapshot_date')
                if agent_name and snapshot_date:
                    response = requests.get(f'{base_url}/snapshots/{agent_name}/{snapshot_date}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'snapshot': response.json()}

            elif action == 'timeline':
                if agent_name:
                    response = requests.get(f'{base_url}/timeline/{agent_name}/', timeout=10)
                    if response.status_code == 200:
                        return {'success': True, 'timeline': response.json()}

            elif action == 'compare':
                compare_dates = arguments.get('compare_dates', [])
                if agent_name and len(compare_dates) >= 2:
                    response = requests.post(
                        f'{base_url}/compare/',
                        json={'agent': agent_name, 'date1': compare_dates[0], 'date2': compare_dates[1]},
                        timeout=10
                    )
                    if response.status_code == 200:
                        return {'success': True, 'comparison': response.json()}

            # Fallback to direct model access
            from core.models_unified_system import AgentMemory
            # Session 810: Defer embedding fields to reduce egress costs
            memories = AgentMemory.objects.defer('embedding').all().order_by('-created_at')[:20]
            return {
                'success': True,
                'snapshots': [
                    {'agent': m.agent.name if m.agent else 'Unknown', 'created': str(m.created_at), 'type': m.memory_type}
                    for m in memories
                ],
                'summary': f"Found {len(memories)} memory records"
            }

        except Exception as e:
            logger.error(f"Error accessing time travel memory: {e}")
            return {'success': False, 'error': str(e)}

    def _trigger_agent_conversation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 579: Trigger an agent-to-agent conversation.
        """
        try:
            from core.models_unified_system import HiveMindSession, Agent
            from core.tasks import run_multi_agent_conversation
            from django.utils import timezone
            import random

            topic = arguments.get('topic', '').strip()
            if not topic:
                return {
                    'success': False,
                    'error': 'Topic is required for agent conversation'
                }

            agent_names = arguments.get('agent_names', [])
            max_rounds = arguments.get('max_rounds', 3)
            conversation_type = arguments.get('conversation_type', 'discussion')

            # If no agents specified, pick relevant ones
            if not agent_names:
                # Get active agents and pick 3-4 randomly
                active_agents = Agent.objects.filter(
                    is_active=True
                ).exclude(
                    name__in=['PersonalAssistantAgent', 'ThinkingAgent']
                ).order_by('?')[:4]
                agent_names = [a.name for a in active_agents]

            if len(agent_names) < 2:
                return {
                    'success': False,
                    'error': 'Need at least 2 agents for a conversation'
                }

            # Create HiveMindSession for the conversation
            session = HiveMindSession.objects.create(
                session_mode='conversation',
                question=topic,
                conversation_topic=topic,
                context={
                    'conversation_type': conversation_type,
                    'max_rounds': max_rounds,
                    'triggered_by': 'personal_assistant'
                },
                status='active',
                participant_ids=[str(a.id) for a in Agent.objects.filter(name__in=agent_names)]
            )

            # Trigger the conversation task asynchronously
            try:
                run_multi_agent_conversation.delay(
                    max_conversations=1,
                    participants_per_conversation=len(agent_names),
                    max_rounds=max_rounds
                )
            except Exception as task_error:
                logger.warning(f"Could not trigger async conversation: {task_error}")

            return {
                'success': True,
                'session_id': str(session.id),
                'topic': topic,
                'participants': agent_names,
                'summary': f"**Agent Conversation Started!**\n\n💬 Topic: {topic}\n👥 Participants: {', '.join(agent_names[:4])}\n🔄 Type: {conversation_type}\n\nAgents are now discussing this topic. Check back soon for insights!"
            }

        except Exception as e:
            logger.error(f"Error triggering agent conversation: {e}")
            return {
                'success': False,
                'error': str(e)
            }

