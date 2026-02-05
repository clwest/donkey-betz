"""
Unified Personal Assistant
=========================

Combines neural intelligence, agent orchestration, and personal learning
into a single, coherent assistant that remembers which agents work best.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model

# Core imports
from core.models import ExtendedUserProfile
from core.agent_context_middleware import AgentContextMiddleware
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import get_memory_manager
from core.models_agent_memory import AgentExecutionMemory, AgentRecommendation, AgentPerformanceStats

# Agent and AI imports
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from core.personal_assistant_agent_integration import personal_assistant_agent_integration

# AI Provider imports
from content.ai_providers import AIProviderManager
from mythology.services import MythologyPreventionService
from core.services.spider_intelligence import SpiderIntelligenceService

# Session 352: Pipeline Visualizer integration
from core.pipeline_progress_consumer import (
    broadcast_stage_started,
    broadcast_stage_completed,
    broadcast_stage_failed
)

logger = logging.getLogger(__name__)
User = get_user_model()


class UnifiedPersonalAssistant:
    """
    The One True Assistant™ - combines all the best features:
    - Neural intelligence with agent orchestration
    - Personal learning and memory
    - Agent performance tracking
    - Reality-aware responses
    """

    def __init__(self, user: User):
        self.user = user
        self.profile = self._get_or_create_profile()

        # Core components (lazy-loaded to avoid serialization issues)
        self._context_middleware = None
        self._agent_registry = None
        self._advisor_registry = None
        self._llm_enforcer = None
        self._memory_manager = None
        self._ai_provider = None
        self._mythology_service = None
        self._spider_intelligence = None

        # Session state
        self.session_context = {}
        self.conversation_history = []

        logger.info(f"✅ Unified Personal Assistant initialized for {user.username}")

    def _get_or_create_profile(self) -> ExtendedUserProfile:
        """Get or create extended user profile."""
        profile, created = ExtendedUserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'full_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                'metadata': {'unified_assistant': {'initialized': datetime.now().isoformat()}}
            }
        )
        if created:
            logger.info(f"Created new extended profile for {self.user.username}")
        return profile

    # Lazy loading properties to avoid serialization issues
    @property
    def context_middleware(self):
        if not self._context_middleware:
            self._context_middleware = AgentContextMiddleware()
        return self._context_middleware

    @property
    def agent_registry(self):
        if not self._agent_registry:
            self._agent_registry = get_agent_registry()
        return self._agent_registry

    @property
    def advisor_registry(self):
        if not self._advisor_registry:
            self._advisor_registry = get_advisor_registry()
        return self._advisor_registry

    @property
    def llm_enforcer(self):
        if not self._llm_enforcer:
            self._llm_enforcer = LLMEnforcer()
        return self._llm_enforcer

    @property
    def memory_manager(self):
        if not self._memory_manager:
            self._memory_manager = get_memory_manager(self.user)
        return self._memory_manager

    @property
    def ai_provider(self):
        if not self._ai_provider:
            self._ai_provider = AIProviderManager()
        return self._ai_provider

    @property
    def mythology_service(self):
        if not self._mythology_service:
            self._mythology_service = MythologyPreventionService()
        return self._mythology_service

    @property
    def spider_intelligence(self):
        if not self._spider_intelligence:
            self._spider_intelligence = SpiderIntelligenceService()
        return self._spider_intelligence

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user message with full intelligence:
        1. Analyze intent and check for agent needs
        2. Route to appropriate agents if needed
        3. Remember agent performance
        4. Provide intelligent response with recommendations
        """
        try:
            # Get comprehensive context
            user_context = self.get_personalized_context()
            full_context = {**user_context, **(context or {})}

            # Check if this should be routed to agents
            if personal_assistant_agent_integration.should_route_to_agents(message):
                return self._handle_agent_routing(message, full_context)
            else:
                return self._handle_direct_response(message, full_context)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response(str(e))

    def _handle_agent_routing(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages that should be routed to agents."""
        try:
            # Get agent recommendations based on past performance
            recommendations = self.get_agent_recommendations(message)

            # Check if user is asking for a specific agent or if we should recommend
            if self._is_agent_request(message):
                return self._execute_requested_agent(message, context)
            else:
                return self._suggest_agents_with_memory(message, recommendations, context)

        except Exception as e:
            logger.error(f"Error in agent routing: {e}")
            return self._handle_direct_response(message, context)

    def _handle_direct_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle messages with direct AI response, enhanced with spider intelligence."""
        try:
            # Get AI response using the working AI provider pattern
            from content.ai_providers import AIProviderManager
            ai_provider = AIProviderManager()

            # Get available agents information
            try:
                agents = self.agent_registry.list_agents()
                agent_count = len(agents)
                agent_names = [agent.get('name', 'Unknown') for agent in agents[:10]]  # First 10 agent names

                agent_context = f"""
IMPORTANT: You have access to {agent_count} specialized AI agents including: {', '.join(agent_names)}, and many more.

When users ask about agents, you should:
1. Tell them you have access to {agent_count} specialized agents
2. List some examples: {', '.join(agent_names[:5])}
3. Offer to execute specific agents or provide recommendations
4. Mention you track which agents work best for different tasks
"""
            except Exception as e:
                logger.error(f"Error accessing agent registry: {e}")
                agent_context = "You have access to a large number of specialized AI agents for various tasks."

            # Get platform component knowledge
            platform_context = self._get_platform_component_knowledge()

            # Session 262: Get spider intelligence for real-time data
            spider_context = ""
            spider_insights = None
            try:
                spider_insights = self.spider_intelligence.get_insights_for_prompt(message)
                if spider_insights and (spider_insights.get('relevant_trends') or spider_insights.get('related_discussions')):
                    spider_context = self._format_spider_context(spider_insights)
                    logger.info(f"🕷️ Spider intelligence retrieved: {len(spider_insights.get('relevant_trends', []))} trends, "
                               f"{len(spider_insights.get('related_discussions', []))} discussions")
            except Exception as e:
                logger.warning(f"Spider intelligence unavailable: {e}")
                spider_context = ""

            # Session 324: Get canonical policies from Boardroom Decisions
            policy_context = ""
            try:
                from core.services.policy_context import get_policy_context_service
                policy_service = get_policy_context_service()
                policy_context = policy_service.get_policies_for_agent('PersonalAssistant')
                if policy_context:
                    logger.info(f"🏛️ Canonical policies injected into Personal Assistant")
            except Exception as e:
                logger.debug(f"Could not get policy context: {e}")

            # Session 939: Get boardroom context for proactive awareness
            boardroom_context = self._get_boardroom_context()
            boardroom_context_text = boardroom_context.get('context_text', '')
            if boardroom_context.get('total_pending', 0) > 0:
                logger.info(f"🏛️ Boardroom context: {boardroom_context.get('total_pending')} pending items "
                           f"({boardroom_context.get('critical_count', 0)} critical)")

            # Session 554: Get comprehensive agent intelligence using IntelligenceQueryService
            agent_knowledge_context = ""
            intelligence_summary = None
            try:
                from core.services.intelligence_query import intelligence_service

                # Search full knowledge base for relevant entries
                intelligence_summary = intelligence_service.get_intelligence_summary(message)

                if intelligence_summary and intelligence_summary.get('has_data'):
                    knowledge_parts = ["\n== AGENT COLLECTIVE INTELLIGENCE =="]

                    # Add attribution
                    attribution = intelligence_summary.get('attribution', '')
                    if attribution:
                        knowledge_parts.append(attribution)

                    # Add relevant knowledge entries
                    knowledge_data = intelligence_summary.get('knowledge', {})
                    if knowledge_data.get('entries'):
                        knowledge_parts.append("\nRelevant knowledge from agent network:")
                        for entry in knowledge_data['entries'][:5]:
                            title = entry.get('title', '')[:80]
                            agent = entry.get('agent__name', 'Unknown')
                            confidence = entry.get('confidence_score', 0)
                            knowledge_parts.append(f"- [{agent}] {title} (confidence: {confidence:.0%})")

                    # Add expert agents
                    experts_data = intelligence_summary.get('experts', {})
                    if experts_data.get('experts'):
                        expert_names = [e['agent_name'] for e in experts_data['experts'][:3]]
                        knowledge_parts.append(f"\nExpert agents on this topic: {', '.join(expert_names)}")

                    # Add recent insights
                    insights_data = intelligence_summary.get('insights', {})
                    if insights_data.get('dreams'):
                        knowledge_parts.append("\nRecent agent insights:")
                        for dream in insights_data['dreams'][:2]:
                            title = dream.get('title', '')[:60]
                            agent = dream.get('agent__name', 'Unknown')
                            knowledge_parts.append(f"- 💭 {agent} dreamed: {title}")

                    agent_knowledge_context = '\n'.join(knowledge_parts)
                    logger.info(
                        f"🧠 Session 554: Injected intelligence from "
                        f"{knowledge_data.get('total_count', 0)} knowledge entries, "
                        f"{len(experts_data.get('experts', []))} experts"
                    )
            except Exception as e:
                logger.warning(f"Could not get agent intelligence: {e}")
                # Fallback to basic query
                try:
                    from core.models import KnowledgeTransfer
                    from django.utils import timezone
                    from datetime import timedelta

                    recent_transfers = KnowledgeTransfer.objects.filter(
                        was_useful=True,
                        created_at__gte=timezone.now() - timedelta(days=7)
                    ).select_related('connection__teacher_agent').order_by('-created_at')[:5]

                    if recent_transfers:
                        knowledge_parts = ["\n== AGENT COLLECTIVE KNOWLEDGE =="]
                        knowledge_parts.append("Recent insights from the agent network:")
                        for transfer in recent_transfers:
                            summary = transfer.transfer_summary[:100] if transfer.transfer_summary else ''
                            if summary:
                                knowledge_parts.append(f"- {transfer.connection.teacher_agent.name}: {summary}")
                        agent_knowledge_context = '\n'.join(knowledge_parts)
                        logger.info(f"🧠 Fallback: Injected {len(recent_transfers)} agent knowledge insights")
                except Exception as fallback_e:
                    logger.debug(f"Fallback knowledge also failed: {fallback_e}")

            # Check if user is asking about platform components
            message_lower = message.lower()
            is_platform_question = any(component in message_lower for component in [
                'neural orchestra', 'revenue dashboard', 'decision command',
                'income builder', 'control center', 'monetization hub'
            ])

            if is_platform_question:
                enhanced_prompt = f"""You are a unified personal assistant for {self.user.username or 'the user'}.

The user is asking about their ACTUAL platform components. Here is the specific information:

{platform_context}

User question: {message}

CRITICAL: Answer about THEIR specific platform component, not generic concepts. For example, if they ask about "Neural Orchestra", explain THEIR real-time AI collaboration visualization system, not music AI."""
                logger.info(f"🎯 Platform question detected! Using specialized prompt for: {message}")
            else:
                logger.info(f"💬 General question detected: {message}")
                # Build enhanced prompt with spider intelligence
                enhanced_prompt = f"""You are a unified personal assistant for {self.user.username or 'the user'}.

{agent_context}

Context: {context.get('page', 'unknown')} page
Task type: {self._detect_task_type(message)}
"""
                # Add spider intelligence if available
                if spider_context:
                    enhanced_prompt += f"""
REAL-TIME INTELLIGENCE FROM SPIDER NETWORK:
{spider_context}

Use this real-time data to provide informed, data-driven responses. Reference specific sources when relevant.
"""

                # Session 324: Add canonical policies if available
                if policy_context:
                    enhanced_prompt += f"""
{policy_context}
"""

                # Session 324: Add agent knowledge if available
                if agent_knowledge_context:
                    enhanced_prompt += f"""
{agent_knowledge_context}
"""

                # Session 939: Add boardroom context for proactive awareness
                if boardroom_context_text:
                    enhanced_prompt += f"""
{boardroom_context_text}
"""

                enhanced_prompt += f"""
User message: {message}

Provide a helpful, personalized response. If this seems like it needs an agent, mention that you can recommend agents based on past performance."""

            response = ai_provider.generate_content(
                provider='openai',
                model='gpt-5-mini',
                system_prompt=enhanced_prompt,
                user_prompt=message,
                config={'max_tokens': 500, 'temperature': 0.7}
            )

            # Learn from this interaction
            self._learn_from_interaction(message, response, context)

            # Build response with spider metadata
            result = {
                'response': response.content if response.success else 'I encountered an issue generating a response.',
                'suggestions': self._generate_contextual_suggestions(message, context),
                'actions': self._determine_available_actions(context),
                'confidence': 0.8 if response.success else 0.3,
                'ai_generated': True,
                'model': response.model_used,
                'agent_suggestions': self.get_agent_recommendations(message)[:3],  # Top 3 relevant agents
                'metadata': {
                    'intent': self._detect_intent(message),
                    'context_used': True,
                    'learning_applied': True,
                    'tokens_used': response.token_usage.get('total_tokens', 0) if response.token_usage else 0,
                    'generation_time_ms': response.generation_time_ms,
                    'spider_intelligence_used': bool(spider_context)
                }
            }

            # Add spider data to response if available
            if spider_insights:
                result['spider_data'] = {
                    'trends_found': len(spider_insights.get('relevant_trends', [])),
                    'discussions_found': len(spider_insights.get('related_discussions', [])),
                    'sources': list(set(
                        [t.get('source', 'unknown') for t in spider_insights.get('relevant_trends', [])] +
                        [d.get('source', 'unknown') for d in spider_insights.get('related_discussions', [])]
                    ))
                }

            # Session 554: Add intelligence data to response
            if intelligence_summary and intelligence_summary.get('has_data'):
                knowledge_data = intelligence_summary.get('knowledge', {})
                experts_data = intelligence_summary.get('experts', {})
                result['intelligence_data'] = {
                    'knowledge_entries': knowledge_data.get('total_count', 0),
                    'agents_referenced': len(knowledge_data.get('agent_breakdown', {})),
                    'expert_agents': [e['agent_name'] for e in experts_data.get('experts', [])[:3]],
                    'attribution': intelligence_summary.get('attribution', ''),
                    'has_intelligence': True
                }
                result['metadata']['intelligence_used'] = True

            # Session 939: Add boardroom data to response
            if boardroom_context.get('total_pending', 0) > 0:
                result['boardroom_data'] = {
                    'total_pending': boardroom_context.get('total_pending', 0),
                    'attention_items': boardroom_context.get('attention_count', 0),
                    'draft_decisions': boardroom_context.get('decision_count', 0),
                    'critical_count': boardroom_context.get('critical_count', 0),
                    'high_urgency_count': boardroom_context.get('high_count', 0),
                    'attention_by_type': boardroom_context.get('attention_by_type', {}),
                    'decisions_by_type': boardroom_context.get('decisions_by_type', {}),
                }
                result['metadata']['boardroom_context_used'] = True

            return result

        except Exception as e:
            logger.error(f"Error in direct response: {e}")
            return self._create_error_response(str(e))

    def _format_spider_context(self, spider_insights: Dict[str, Any]) -> str:
        """Format spider intelligence data into a readable context string."""
        parts = []

        # Format trending topics (these are keywords/tags, not articles)
        trends = spider_insights.get('relevant_trends', [])
        if trends:
            topic_list = []
            for trend in trends[:10]:
                # Handle both dict format and simple string format
                if isinstance(trend, dict):
                    topic = trend.get('topic', '')
                    count = trend.get('count', trend.get('mentions', 0))
                    if topic:
                        topic_list.append(f"{topic} ({count})" if count else topic)
                elif isinstance(trend, str):
                    topic_list.append(trend)

            if topic_list:
                parts.append(f"📈 TRENDING TOPICS: {', '.join(topic_list)}")

        # Format related discussions/articles (these have full titles and URLs)
        discussions = spider_insights.get('related_discussions', [])
        if discussions:
            parts.append("\n📰 RECENT ARTICLES & DISCUSSIONS:")
            for i, disc in enumerate(discussions[:5], 1):
                title = disc.get('title', '')
                if not title:
                    continue  # Skip items without titles
                source = disc.get('source', 'Unknown')
                url = disc.get('url', '')
                description = disc.get('description', '')
                parts.append(f"  {i}. [{source}] {title}")
                if url:
                    parts.append(f"     URL: {url}")
                if description:
                    parts.append(f"     Summary: {description[:150]}...")

        # Format related content from search (these are direct matches)
        related_content = spider_insights.get('related_content', [])
        if related_content:
            parts.append("\n🔍 DIRECTLY RELEVANT CONTENT:")
            for i, content in enumerate(related_content[:3], 1):
                title = content.get('title', '')
                if not title:
                    continue
                source = content.get('source', 'Unknown')
                url = content.get('url', '')
                parts.append(f"  {i}. [{source}] {title}")
                if url:
                    parts.append(f"     URL: {url}")

        # Format job market data if present
        job_market = spider_insights.get('job_market', {})
        if job_market and job_market.get('total', 0) > 0:
            parts.append(f"\n💼 JOB MARKET: {job_market['total']} remote jobs found")
            sample_jobs = job_market.get('sample_jobs', [])
            for job in sample_jobs[:3]:
                title = job.get('title', '')
                company = job.get('company', 'Unknown')
                parts.append(f"  • {title} at {company}")

        # Format market data if present
        market_data = spider_insights.get('market_data', {})
        if market_data and market_data.get('crypto'):
            parts.append("\n💰 CRYPTO MARKET:")
            for crypto in market_data['crypto'][:3]:
                symbol = crypto.get('symbol', '')
                price = crypto.get('price', 'N/A')
                change = crypto.get('change_24h', 0)
                if symbol and price:
                    parts.append(f"  • {symbol}: ${price} ({change:+.1f}%)" if isinstance(change, (int, float)) else f"  • {symbol}: ${price}")

        # Format suggestions if any
        suggestions = spider_insights.get('suggestions', [])
        if suggestions:
            parts.append("\n💡 CONTEXT:")
            for suggestion in suggestions[:3]:
                parts.append(f"  • {suggestion}")

        return "\n".join(parts) if parts else ""

    def get_agent_recommendations(self, message: str) -> List[Dict[str, Any]]:
        """
        Get agent recommendations based on past performance and current message.
        This is the magic - remembering which agents worked for similar tasks.
        """
        try:
            # Detect task type from message
            task_type = self._detect_task_type(message)

            # Get user's historical preferences
            user_recs = AgentRecommendation.objects.filter(
                user=self.user,
                task_type=task_type
            ).order_by('-confidence_score')[:3]

            recommendations = []
            for rec in user_recs:
                recommendations.append({
                    'agent_name': rec.recommended_agent,
                    'confidence': rec.confidence_score,
                    'success_rate': rec.avg_success_rate,
                    'past_success': rec.best_outcome_description,
                    'total_uses': rec.total_executions,
                    'reason': f"Previously achieved {rec.avg_success_rate:.1%} success rate for {task_type}"
                })

            # If no user history, get global best performers
            if not recommendations:
                global_stats = AgentPerformanceStats.objects.filter(
                    task_type_stats__has_key=task_type
                ).order_by('-avg_success_rate')[:3]

                for stat in global_stats:
                    task_stats = stat.task_type_stats.get(task_type, {})
                    recommendations.append({
                        'agent_name': stat.agent_name,
                        'confidence': task_stats.get('success_rate', 0.5),
                        'success_rate': task_stats.get('success_rate', 0.5),
                        'reason': f"Top performer for {task_type} globally",
                        'total_uses': task_stats.get('executions', 0)
                    })

            return recommendations

        except Exception as e:
            logger.error(f"Error getting agent recommendations: {e}")
            return []

    def execute_agent_with_memory(self, agent_name: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent and record the performance for future recommendations.

        Session 352: Now broadcasts to Pipeline Visualizer for real-time UI updates!
        """
        start_time = datetime.now()

        # Session 352: Map agent names to pipeline stage types
        agent_to_stage = {
            'image_generation_agent': 'image',
            'video_generation_agent': 'video',
            'audio_generation_agent': 'audio',
            '3d_generation_agent': '3d',
            'research_agent': 'initial_research',
            'trend_analysis_agent': 'trend_analysis',
            'competitor_analysis_agent': 'competitor_analysis',
            'customer_research_agent': 'customer_research',
            'brand_identity_agent': 'brand_strategy',
            'seo_optimizer_agent': 'seo',
            'content_strategy_agent': 'content_audit',
            'workflow_orchestration_agent': 'creative_direction',
            'prompt_engineering_agent': 'brief',
        }

        # Determine stage and pipeline type
        stage = agent_to_stage.get(agent_name, agent_name.replace('_agent', ''))
        pipeline_type = 'creative' if stage in ['image', 'video', 'audio', '3d', 'editing', 'brief', 'creative_direction', 'seo'] else 'research'

        try:
            # Session 352: Broadcast stage STARTED to Pipeline Visualizer
            broadcast_stage_started(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                project_id=context.get('project_id'),
                business_idea=task[:100] if task else None
            )
            logger.info(f"🚀 [Pipeline] Started: {agent_name} ({stage})")

            # Execute agent through the integration system (handle async)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    personal_assistant_agent_integration.execute_through_agents(
                        message=task,
                        selected_agents=[agent_name]
                    )
                )
            finally:
                loop.close()

            execution_time = (datetime.now() - start_time).total_seconds()
            execution_time_ms = int(execution_time * 1000)

            # Determine success score based on result
            success_score = self._calculate_success_score(result)

            # Session 352: Broadcast stage COMPLETED to Pipeline Visualizer
            broadcast_stage_completed(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                success=success_score >= 0.5,
                duration_ms=execution_time_ms,
                project_id=context.get('project_id'),
                summary=result.get('summary', f'{agent_name} completed')[:200]
            )
            logger.info(f"✅ [Pipeline] Completed: {agent_name} in {execution_time:.1f}s (score: {success_score:.2f})")

            # Record this execution for future recommendations
            AgentExecutionMemory.objects.create(
                user=self.user,
                agent_name=agent_name,
                task_type=self._detect_task_type(task),
                task_description=task,
                original_prompt=task,
                success_score=success_score,
                execution_time_seconds=execution_time,
                outcome_description=result.get('summary', 'Agent execution completed'),
                outcome_metrics=result.get('metrics', {}),
                page_context=context.get('page', ''),
                conversation_id=context.get('conversation_id', '')
            )

            # Update recommendations cache
            self._update_agent_recommendations(agent_name, self._detect_task_type(task), success_score)

            # Enhanced response with memory context
            enhanced_result = {
                **result,
                'agent_performance': {
                    'execution_time': execution_time,
                    'success_score': success_score,
                    'will_remember': True
                },
                'learning_note': f"I'll remember that {agent_name} worked well for this type of task."
            }

            return enhanced_result

        except Exception as e:
            logger.error(f"Error executing agent with memory: {e}")

            # Session 352: Broadcast stage FAILED to Pipeline Visualizer
            broadcast_stage_failed(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                error=str(e)[:200],
                project_id=context.get('project_id')
            )
            logger.warning(f"❌ [Pipeline] Failed: {agent_name} - {str(e)[:100]}")

            # Still record the failure for learning
            AgentExecutionMemory.objects.create(
                user=self.user,
                agent_name=agent_name,
                task_type=self._detect_task_type(task),
                task_description=task,
                original_prompt=task,
                success_score=0.0,
                execution_time_seconds=(datetime.now() - start_time).total_seconds(),
                outcome_description=f"Execution failed: {str(e)}",
                outcome_metrics={}
            )

            return {
                'success': False,
                'error': str(e),
                'agent_name': agent_name,
                'learning_note': "I'll remember this didn't work and try a different approach next time."
            }

    def get_personalized_context(self) -> Dict[str, Any]:
        """Get comprehensive personalized context including agent memories."""
        base_context = self.context_middleware.get_user_context(self.user)

        # Add agent memory context
        recent_successes = AgentExecutionMemory.objects.filter(
            user=self.user,
            success_score__gte=0.7
        ).order_by('-execution_date')[:5]

        successful_agents = {}
        for memory in recent_successes:
            task_type = memory.task_type
            if task_type not in successful_agents:
                successful_agents[task_type] = []
            successful_agents[task_type].append({
                'agent': memory.agent_name,
                'outcome': memory.outcome_description,
                'score': memory.success_score
            })

        return {
            **base_context,
            'agent_memory': {
                'successful_agents': successful_agents,
                'total_agent_uses': AgentExecutionMemory.objects.filter(user=self.user).count(),
                'favorite_agents': self._get_favorite_agents()
            }
        }

    def _get_favorite_agents(self) -> List[Dict[str, Any]]:
        """Get user's most successful agents."""
        from django.db.models import Avg, Count

        favorites = AgentExecutionMemory.objects.filter(
            user=self.user
        ).values('agent_name').annotate(
            avg_score=Avg('success_score'),
            usage_count=Count('id')
        ).filter(
            usage_count__gte=2,  # At least 2 uses
            avg_score__gte=0.6   # At least 60% success
        ).order_by('-avg_score', '-usage_count')[:5]

        return list(favorites)

    # Helper methods
    def _detect_task_type(self, message: str) -> str:
        """Detect the type of task from the message."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['blog', 'article', 'write', 'content']):
            return 'content_writing'
        elif any(word in message_lower for word in ['analyze', 'data', 'report', 'metrics']):
            return 'data_analysis'
        elif any(word in message_lower for word in ['research', 'find', 'search', 'investigate']):
            return 'research'
        elif any(word in message_lower for word in ['social', 'tweet', 'post', 'marketing']):
            return 'social_media'
        elif any(word in message_lower for word in ['design', 'image', 'visual', 'graphics']):
            return 'design'
        else:
            return 'general'

    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['execute', 'run', 'use agent']):
            return 'agent_execution'
        elif any(word in message_lower for word in ['recommend', 'suggest', 'which agent']):
            return 'agent_recommendation'
        elif any(word in message_lower for word in ['help', 'how', 'what', 'explain']):
            return 'help'
        else:
            return 'general'

    def _calculate_success_score(self, result: Dict[str, Any]) -> float:
        """Calculate success score from agent execution result."""
        if not result.get('success', True):
            return 0.0

        # Start with base score
        score = 0.7

        # Boost based on specific indicators
        if result.get('quality_score'):
            score = max(score, result['quality_score'])

        if result.get('user_satisfaction'):
            score = max(score, result['user_satisfaction'])

        # Boost for successful metrics
        metrics = result.get('metrics', {})
        if metrics.get('views', 0) > 1000:
            score += 0.1
        if metrics.get('engagement_rate', 0) > 0.05:
            score += 0.1

        return min(score, 1.0)

    def _create_error_response(self, error: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'response': f"I encountered an issue: {error}. Let me try a different approach.",
            'success': False,
            'error': error,
            'suggestions': ['Try again', 'Use a different approach', 'Ask for help'],
            'confidence': 0.3
        }

    def _is_agent_request(self, message: str) -> bool:
        """Check if user is specifically requesting an agent."""
        message_lower = message.lower()
        return any(phrase in message_lower for phrase in [
            'execute agent', 'run agent', 'use agent', 'agent for'
        ])

    def _execute_requested_agent(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specifically requested agent."""
        # Extract agent name from message (simplified)
        # In production, this would use NLP to extract agent name
        agent_name = "Content Writer"  # Default for now
        return self.execute_agent_with_memory(agent_name, message, context)

    def _suggest_agents_with_memory(self, message: str, recommendations: List[Dict], context: Dict) -> Dict[str, Any]:
        """Suggest agents based on memory and past performance."""
        if not recommendations:
            return {
                'response': "I'd be happy to help, but I don't have enough history to recommend the best agent for this task yet. Would you like me to suggest some general agents that might work?",
                'suggestions': ['Show all agents', 'Try Content Writer', 'Try Data Analyst'],
                'confidence': 0.5
            }

        top_agent = recommendations[0]
        return {
            'response': f"Based on your past results, I recommend the **{top_agent['agent_name']}** for this task. It has a {top_agent['success_rate']:.1%} success rate for similar work. {top_agent.get('past_success', 'It has worked well before.')} Should I execute it?",
            'agent_recommendations': recommendations[:3],
            'suggestions': [
                f"Execute {top_agent['agent_name']}",
                "Show other options",
                "Tell me more about this agent",
                "Do it yourself instead"
            ],
            'confidence': top_agent['confidence'],
            'actions': ['execute_agent', 'show_alternatives']
        }

    def _generate_contextual_suggestions(self, message: str, context: Dict) -> List[str]:
        """Generate contextual suggestions based on message and context."""
        suggestions = []

        # Add page-specific suggestions
        page = context.get('page', '')
        if '/profile' in page:
            suggestions.extend(['Update my profile', 'Find job matches', 'Show my skills'])
        elif '/dashboard' in page:
            suggestions.extend(['Show my stats', 'Recent activity', 'Revenue insights'])

        # Add general suggestions
        suggestions.extend(['Get agent recommendations', 'Help me decide', 'Tell me more'])

        return suggestions[:4]  # Limit to 4

    def _determine_available_actions(self, context: Dict) -> List[str]:
        """Determine available actions based on context."""
        actions = ['help', 'show_options']

        # Add context-specific actions
        if context.get('page', '').startswith('/profile'):
            actions.extend(['edit_profile', 'view_profile'])

        return actions

    def _learn_from_interaction(self, message: str, response: Dict, context: Dict):
        """Learn from user interactions for better future responses."""
        try:
            # Store interaction pattern in memory manager
            if hasattr(self, '_memory_manager') and self._memory_manager:
                self.memory_manager.store_interaction_pattern({
                    'user_message': message,
                    'response_type': 'direct',
                    'context': context.get('page', ''),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")

    def _update_agent_recommendations(self, agent_name: str, task_type: str, success_score: float):
        """Update cached agent recommendations based on new execution."""
        try:
            # Update or create recommendation
            rec, created = AgentRecommendation.objects.get_or_create(
                user=self.user,
                task_type=task_type,
                recommended_agent=agent_name,
                defaults={
                    'confidence_score': success_score,
                    'avg_success_rate': success_score,
                    'total_executions': 1,
                    'best_outcome_description': 'Recent execution completed'
                }
            )

            if not created:
                # Update existing recommendation
                total_execs = rec.total_executions + 1
                new_avg = ((rec.avg_success_rate * rec.total_executions) + success_score) / total_execs

                rec.avg_success_rate = new_avg
                rec.total_executions = total_execs
                rec.confidence_score = min(new_avg + (total_execs * 0.01), 1.0)  # Boost confidence with usage

                if success_score > rec.avg_success_rate:
                    rec.best_outcome_description = f"Recent high-performing execution (score: {success_score:.1f})"

                rec.save()

        except Exception as e:
            logger.error(f"Error updating recommendations: {e}")

    def _get_platform_component_knowledge(self) -> str:
        """Get comprehensive knowledge about the user's platform components."""
        return """
The user has a unified AI platform with these specific components:

🎭 NEURAL ORCHESTRA - Their real-time AI collaboration visualization system that:
- Shows all 149 specialized agents in an interactive network graph with D3.js
- Displays 25 legendary advisors (Warren Buffett, Cathie Wood, Ray Dalio, etc.)
- Visualizes live connections, consultations, and collaborations between agents/advisors
- Tracks workflow orchestration with progress indicators
- Shows system health metrics, revenue tracking, ML learning loop stats
- Provides action plan execution with "Start Execution" buttons
- Uses WebSocket for real-time updates across 800x400 interactive visualizations
- Has 3 view modes: Network, Workflow, Performance

💰 REVENUE DASHBOARD - Revenue tracking and monetization analytics
💼 DECISION COMMAND - Opportunity analysis and decision support system
🏗️ INCOME BUILDER - AI-powered income opportunity generation
🎯 CONTROL CENTER - System monitoring and management interface
📊 MONETIZATION HUB - Revenue optimization and financial management

The Neural Orchestra is NOT a music AI - it's their sophisticated mission control center for coordinating their entire AI ecosystem, showing which agents are working on what, how they collaborate with advisors, and what revenue opportunities are being generated in real-time.

When users ask about ANY of these components, explain their ACTUAL platform features, not generic explanations.
"""

    def _get_boardroom_context(self) -> Dict[str, Any]:
        """
        Session 939: Get boardroom context for PA awareness.
        Returns stats about pending decisions and attention items.
        """
        try:
            from core.models_human_interface import HumanAttentionItem
            from core.models_unified_system import AgentDecisionSummary
            from django.db.models import Count

            # Get attention item stats
            attention_items = HumanAttentionItem.objects.filter(
                user=self.user,
                status='pending'
            )
            attention_count = attention_items.count()
            attention_by_urgency = dict(
                attention_items.values('urgency')
                .annotate(count=Count('id'))
                .values_list('urgency', 'count')
            )
            attention_by_type = dict(
                attention_items.values('item_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
                .values_list('item_type', 'count')
            )

            # Get decision stats
            decisions = AgentDecisionSummary.objects.filter(status='draft')
            decision_count = decisions.count()
            decisions_by_type = dict(
                decisions.values('decision_type')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
                .values_list('decision_type', 'count')
            )

            # Build context
            total_pending = attention_count + decision_count
            critical_count = attention_by_urgency.get('critical', 0)
            high_count = attention_by_urgency.get('high', 0)

            context_parts = []
            if total_pending > 0:
                context_parts.append(f"\n== BOARDROOM STATUS ==")
                context_parts.append(f"You have {total_pending} items awaiting your attention in the Boardroom:")

                if attention_count > 0:
                    context_parts.append(f"- {attention_count} attention items (reviews, alerts, opportunities)")
                    if critical_count > 0:
                        context_parts.append(f"  ⚠️ {critical_count} CRITICAL urgency!")
                    if high_count > 0:
                        context_parts.append(f"  ⚡ {high_count} high urgency")

                if decision_count > 0:
                    context_parts.append(f"- {decision_count} draft decisions from agent conversations")
                    top_types = [f"{count} {dtype}" for dtype, count in list(decisions_by_type.items())[:3]]
                    if top_types:
                        context_parts.append(f"  Types: {', '.join(top_types)}")

                context_parts.append("\nYou should proactively mention these pending items when relevant, especially if there are critical or high-urgency items. Offer to help the user review them.")

            return {
                'context_text': '\n'.join(context_parts) if context_parts else '',
                'total_pending': total_pending,
                'attention_count': attention_count,
                'decision_count': decision_count,
                'critical_count': critical_count,
                'high_count': high_count,
                'attention_by_type': attention_by_type,
                'decisions_by_type': decisions_by_type,
            }

        except Exception as e:
            logger.warning(f"Could not get boardroom context: {e}")
            return {
                'context_text': '',
                'total_pending': 0,
                'attention_count': 0,
                'decision_count': 0,
                'critical_count': 0,
                'high_count': 0,
                'attention_by_type': {},
                'decisions_by_type': {},
            }