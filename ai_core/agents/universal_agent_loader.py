"""
Universal Agent Loader - Connects all 151 agents to the executor
================================================================

This module bridges the gap between database-stored agent templates
and the concrete executor, enabling all 151 agents to be executed.

Enhanced with Bluesky social intelligence learning capabilities for
dynamic agent knowledge updates and real-time market intelligence.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from agents.models import UnifiedAgentTemplate
from agents.registry import agent_registry
from asgiref.sync import sync_to_async
# Note: UniversalLLMExecutor not used directly, we create dynamic classes instead
from ai_core.agents.ai_enforced_base import AIEnforcedAgent

logger = logging.getLogger(__name__)


def get_all_agent_classes() -> Dict[str, type]:
    """
    Load all 151 agents from the database and create executable classes.

    Returns:
        Dictionary mapping agent names to executable agent classes
    """
    agent_classes = {}

    try:
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            is_async = True
        except RuntimeError:
            is_async = False

        if is_async:
            # We're in async context, need to use sync_to_async
            logger.warning("Async context detected, switching to sync mode for DB queries")
            return get_all_agent_classes_sync()

        # Get all agent templates from database (sync context)
        templates = UnifiedAgentTemplate.objects.all()
        logger.info(f"Loading {templates.count()} agents from database")

        for template in templates:
            # Create a dynamic agent class for each template
            agent_name = template.name.replace('-', '_')

            # Create agent configuration from template
            agent_config = {
                'id': str(template.id),
                'name': template.name,
                'type': template.specialization,
                'capabilities': template.capabilities or [],
                'description': template.description,
                'configuration': template.llm_config or {},
                'is_active': template.is_active,
                'system_prompt': template.system_prompt,
                'domain_tags': template.domain_tags or [],
                'tool_integrations': template.tool_integrations or {}
            }

            # Create a dynamic class that uses UniversalLLMAgent
            # Use a factory function to avoid closure issues
            def create_dynamic_agent_class(template_copy, config_copy, agent_name_copy):
                class DynamicAgent(AIEnforcedAgent):
                    """Dynamically created agent from template"""

                    def __init__(self, user=None):
                        # Store template configuration
                        self.template = template_copy
                        self.config = config_copy

                        # Initialize as AI-enforced agent
                        super().__init__(agent_name=agent_name_copy, user=user)

                        # Store capabilities
                        self.capabilities = config_copy.get('capabilities', [])
                        self.specialization = config_copy.get('type', 'general')

                        logger.info(f"Initialized {agent_name_copy} with specialization: {self.specialization}")

                    async def execute(self, **kwargs):
                        """Execute agent task using AI with tool integration"""
                        # Build context from template
                        context = {
                            'agent_type': self.specialization,
                            'capabilities': self.capabilities,
                            'configuration': self.config.get('configuration', {}),
                            'user_input': kwargs
                        }

                        # Import platform context
                        try:
                            from ai_core.agents.platform_context import PLATFORM_CONTEXT
                        except ImportError:
                            PLATFORM_CONTEXT = ""

                        # Generate prompt based on specialization
                        task = kwargs.get('task', 'Complete the requested task')

                        # ========== TOOL INTEGRATION ==========
                        # Get tool configuration from template
                        tool_config = self.config.get('tool_integrations', {})
                        tool_context = []
                        tools_used = []

                        logger.info(f"🔧 Tool integration check for {self.config['name']}: {json.dumps(tool_config, indent=2)}")

                        # Web Search Tool
                        if tool_config.get('web_search', {}).get('enabled'):
                            logger.info(f"🔍 Web search enabled for {self.config['name']}")
                            try:
                                from core.tools import ToolRegistry
                                web_search = ToolRegistry.get_tool('web_search')
                                if web_search:
                                    max_results = tool_config['web_search'].get('max_results', 5)
                                    # Execute web search with task as query
                                    search_result = web_search.execute(query=task[:200], max_results=max_results)
                                    if search_result.get('success') and search_result.get('data'):
                                        tool_context.append(f"WEB SEARCH RESULTS:\n{json.dumps(search_result['data'], indent=2)}")
                                        tools_used.append('web_search')
                                        logger.info(f"Agent {self.config['name']} used web_search: {len(search_result['data'])} results")
                            except Exception as e:
                                logger.warning(f"Web search failed for {self.config['name']}: {e}")

                        # Spider Data Access
                        if tool_config.get('data_access', {}).get('spider_data'):
                            try:
                                from persistence.models import SpiderData
                                # Get recent spider data relevant to this agent's specialization
                                relevant_data = SpiderData.objects.filter(
                                    routed_to_agents__contains=[self.config['name']]
                                ).order_by('-created_at')[:10]

                                if relevant_data.exists():
                                    spider_summary = []
                                    for data in relevant_data:
                                        spider_summary.append({
                                            'spider': data.spider_name,
                                            'data': data.data,
                                            'timestamp': data.created_at.isoformat()
                                        })
                                    tool_context.append(f"SPIDER NETWORK DATA:\n{json.dumps(spider_summary, indent=2, default=str)}")
                                    tools_used.append('spider_data')
                                    logger.info(f"Agent {self.config['name']} accessed spider data: {len(spider_summary)} entries")
                            except Exception as e:
                                logger.warning(f"Spider data access failed for {self.config['name']}: {e}")

                        # Learning Context Access
                        if tool_config.get('data_access', {}).get('learning_context'):
                            try:
                                from core.models_unified_system import LearningInsight
                                # Get relevant learning insights
                                insights = LearningInsight.objects.filter(
                                    insight_type__in=['success_pattern', 'failure_pattern', 'cross_domain']
                                ).order_by('-created_at')[:5]

                                if insights.exists():
                                    learning_summary = []
                                    for insight in insights:
                                        learning_summary.append({
                                            'type': insight.insight_type,
                                            'source': insight.source_domain,
                                            'pattern': insight.pattern_data,
                                            'confidence': float(insight.confidence_score)
                                        })
                                    tool_context.append(f"LEARNING INSIGHTS:\n{json.dumps(learning_summary, indent=2)}")
                                    tools_used.append('learning_context')
                                    logger.info(f"Agent {self.config['name']} accessed learning context: {len(learning_summary)} insights")
                            except Exception as e:
                                logger.warning(f"Learning context access failed for {self.config['name']}: {e}")

                        # Use system prompt from template if available, otherwise use generic prompt
                        system_prompt = self.config.get('system_prompt', '').strip()

                        # Build tool context section
                        tool_context_section = ""
                        if tool_context:
                            tool_context_section = "\n\n".join(["ENHANCED DATA FROM TOOLS:"] + tool_context)

                        if system_prompt:
                            # Use the database system prompt
                            prompt = f"""
                        {system_prompt}

                        PLATFORM KNOWLEDGE:
                        {PLATFORM_CONTEXT}

                        Your capabilities include: {', '.join(self.capabilities) if self.capabilities else 'general task execution'}

                        {tool_context_section}

                        Task: {task}

                        Additional context: {json.dumps(kwargs, default=str)}

                        IMPORTANT: After completing your analysis using all information above, provide your final output below. Be specific, actionable, and complete.

                        FINAL OUTPUT:
                        """
                        else:
                            # Fallback to generic prompt
                            prompt = f"""
                        You are a specialized {self.specialization} agent named {self.config['name']}.

                        PLATFORM KNOWLEDGE:
                        {PLATFORM_CONTEXT}

                        Your capabilities include: {', '.join(self.capabilities) if self.capabilities else 'general task execution'}

                        {tool_context_section}

                        Task: {task}

                        Additional context: {json.dumps(kwargs, default=str)}

                        After analyzing the task and using your specialized knowledge, provide your complete response below:

                        FINAL RESPONSE:
                        """

                        # Use AI to generate response
                        # Get max_tokens from agent config, default to 3000 for GPT-5-mini reasoning models
                        max_tokens = self.config.get('configuration', {}).get('max_completion_tokens', 3000)

                        response = super().generate_ai_text(
                            prompt=prompt,
                            context=json.dumps(context, default=str),
                            task_type=self.specialization,
                            max_tokens=max_tokens
                        )

                        # Track AI usage if method exists
                        if hasattr(self, 'track_ai_usage'):
                            self.track_ai_usage('execute', prompt, response)

                        return {
                            'success': True,
                            'agent': self.config['name'],
                            'specialization': self.specialization,
                            'output': response,
                            'ai_used': True,
                            'tools_used': tools_used,
                            'tool_enhanced': len(tools_used) > 0,
                            'timestamp': datetime.now().isoformat()
                        }

                return DynamicAgent

            # Create the agent class using the factory
            DynamicAgent = create_dynamic_agent_class(template, agent_config, agent_name)

            # Set class name dynamically
            DynamicAgent.__name__ = f"{agent_name.title().replace('_', '')}Agent"
            DynamicAgent.__qualname__ = DynamicAgent.__name__

            # Add to registry
            agent_classes[agent_name] = DynamicAgent

        logger.info(f"✅ Successfully loaded {len(agent_classes)} agent classes")

        # Also include any hardcoded agents that might exist
        try:
            from ai_core.agents.real_content_creator import RealContentCreatorAgent
            agent_classes['real_content_creator'] = RealContentCreatorAgent
            logger.info("Added RealContentCreatorAgent")
        except ImportError:
            pass

        try:
            from ai_core.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
            agent_classes['zero_capital_income_generator'] = ZeroCapitalIncomeGenerator
            logger.info("Added ZeroCapitalIncomeGenerator")
        except ImportError:
            pass

        try:
            from ai_core.agents.content_marketplace_agent import ContentMarketplaceAgent
            agent_classes['content_marketplace_agent'] = ContentMarketplaceAgent
            logger.info("Added ContentMarketplaceAgent")
        except ImportError as e:
            logger.warning(f"Could not add ContentMarketplaceAgent: {e}")

        # ✅ CRITICAL FIX: Add orphaned revenue-generating agents
        orphaned_agents = [
            ('ultimate_money_machine', 'UltimateMoneyMachine'),
            ('affiliate_marketing_empire', 'AffiliateMarketingEmpire'),
            ('autonomous_revenue_system', 'AutonomousRevenueSystem'),
            ('real_client_acquisition', 'RealClientAcquisition'),
            ('real_payment_processor', 'RealPaymentProcessor'),
            ('automated_job_bot', 'AutomatedJobBot'),
            ('intelligent_job_matcher', 'IntelligentJobMatcher'),
            ('job_application_agent', 'JobApplicationAgent'),
            ('freelance_job_analyzer', 'FreelanceJobAnalyzer'),
            ('real_work_delivery_engine', 'RealWorkDeliveryEngine'),
            ('real_job_executor', 'RealJobExecutor'),
        ]

        for module_name, class_name in orphaned_agents:
            try:
                module = __import__(f'ai_core.agents.{module_name}', fromlist=[class_name])
                agent_class = getattr(module, class_name)
                agent_classes[module_name] = agent_class
                logger.info(f"✅ Added orphaned agent: {class_name}")
            except (ImportError, AttributeError) as e:
                logger.debug(f"Skipped {module_name}: {e}")

        return agent_classes

    except Exception as e:
        logger.error(f"Failed to load agent classes: {e}")
        return agent_classes


def get_all_agent_classes_sync() -> Dict[str, type]:
    """
    Sync version of get_all_agent_classes for use in async contexts.
    This forces the database queries to run in a thread pool.
    """
    import threading
    from django.db import connection

    # Force this to run in a new thread to avoid async context issues
    result_container = {}
    exception_container = {}

    def load_agents_sync():
        try:
            # Close any existing connections to ensure clean state
            connection.close()

            agent_classes = {}

            # Get all agent templates from database (now in sync context)
            templates = UnifiedAgentTemplate.objects.all()
            count = templates.count()
            logger.info(f"Loading {count} agents from database (sync mode)")

            for template in templates:
                # Create a dynamic agent class for each template
                agent_name = template.name.replace('-', '_')

                # Create agent configuration from template
                agent_config = {
                    'id': str(template.id),
                    'name': template.name,
                    'type': template.specialization,
                    'capabilities': template.capabilities or [],
                    'description': template.description,
                    'configuration': template.llm_config or {},
                    'is_active': template.is_active,
                    'system_prompt': template.system_prompt,
                    'domain_tags': template.domain_tags or [],
                    'tool_integrations': template.tool_integrations or {}
                }

                # Create a dynamic class that uses UniversalLLMAgent
                # Use a factory function to avoid closure issues
                def create_sync_dynamic_agent_class(template_copy, config_copy, agent_name_copy):
                    class DynamicAgent(AIEnforcedAgent):
                        """Dynamically created agent from template"""

                        def __init__(self, user=None):
                            # Store template configuration
                            self.template = template_copy
                            self.config = config_copy

                            # Initialize as AI-enforced agent
                            super().__init__(agent_name=agent_name_copy, user=user)

                            # Store capabilities
                            self.capabilities = config_copy.get('capabilities', [])
                            self.specialization = config_copy.get('type', 'general')

                            logger.debug(f"Initialized {agent_name_copy} with specialization: {self.specialization}")

                        async def execute(self, **kwargs):
                            """Execute agent task using AI with tool integration"""
                            # Build context from template
                            context = {
                                'agent_type': self.specialization,
                                'capabilities': self.capabilities,
                                'configuration': self.config.get('configuration', {}),
                                'user_input': kwargs
                            }

                            # Generate prompt based on specialization
                            task = kwargs.get('task', 'Complete the requested task')

                            # ========== TOOL INTEGRATION (SYNC VERSION) ==========
                            tool_config = self.config.get('tool_integrations', {})
                            tool_context = []
                            tools_used = []

                            logger.info(f"🔧 [SYNC] Tool check for {self.config['name']}: {json.dumps(tool_config, indent=2)}")

                            # Web Search Tool
                            if tool_config.get('web_search', {}).get('enabled'):
                                logger.info(f"🔍 [SYNC] Web search enabled for {self.config['name']}")
                                try:
                                    from core.tools import ToolRegistry
                                    web_search = ToolRegistry.get_tool('web_search')
                                    if web_search:
                                        max_results = tool_config['web_search'].get('max_results', 5)
                                        search_result = web_search.execute(query=task[:200], max_results=max_results)
                                        if search_result.get('success') and search_result.get('data'):
                                            tool_context.append(f"WEB SEARCH RESULTS:\n{json.dumps(search_result['data'], indent=2)}")
                                            tools_used.append('web_search')
                                            logger.info(f"Agent {self.config['name']} used web_search: {len(search_result['data'])} results")
                                except Exception as e:
                                    logger.warning(f"Web search failed for {self.config['name']}: {e}")

                            # Build tool context section
                            tool_context_section = ""
                            if tool_context:
                                tool_context_section = "\n\n".join(["ENHANCED DATA FROM TOOLS:"] + tool_context)

                            prompt = f"""
                            You are a specialized {self.specialization} agent with the following capabilities:
                            {', '.join(self.capabilities)}

                            {tool_context_section}

                            Task: {task}

                            Additional context: {json.dumps(kwargs, default=str)}

                            After analyzing the task and using your specialized knowledge, provide your complete response below:

                            FINAL RESPONSE:
                            """

                            # Use AI to generate response
                            # GPT-5-mini reasoning models need more tokens (reasoning + output)
                            response = super().generate_ai_text(
                                prompt=prompt,
                                context=json.dumps(context, default=str),
                                task_type=self.specialization,
                                max_tokens=3000  # Enough for reasoning tokens + actual output
                            )

                            # Track AI usage if method exists
                            if hasattr(self, 'track_ai_usage'):
                                self.track_ai_usage('execute', prompt, response)

                            return {
                                'success': True,
                                'agent': self.config['name'],
                                'specialization': self.specialization,
                                'output': response,
                                'ai_used': True,
                                'tools_used': tools_used,
                                'tool_enhanced': len(tools_used) > 0,
                                'timestamp': datetime.now().isoformat()
                            }

                    return DynamicAgent

                # Create the agent class using the factory
                DynamicAgent = create_sync_dynamic_agent_class(template, agent_config, agent_name)

                # Set class name dynamically
                DynamicAgent.__name__ = f"{agent_name.title().replace('_', '')}Agent"
                DynamicAgent.__qualname__ = DynamicAgent.__name__

                # Add to registry
                agent_classes[agent_name] = DynamicAgent

            logger.info(f"✅ Successfully loaded {len(agent_classes)} agent classes (sync mode)")

            # Also include any hardcoded agents that might exist
            try:
                from ai_core.agents.real_content_creator import RealContentCreatorAgent
                agent_classes['real_content_creator'] = RealContentCreatorAgent
                logger.info("Added RealContentCreatorAgent")
            except ImportError:
                pass

            try:
                from ai_core.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
                agent_classes['zero_capital_income_generator'] = ZeroCapitalIncomeGenerator
                logger.info("Added ZeroCapitalIncomeGenerator")
            except ImportError:
                pass

            try:
                from ai_core.agents.content_marketplace_agent import ContentMarketplaceAgent
                agent_classes['content_marketplace_agent'] = ContentMarketplaceAgent
                logger.info("Added ContentMarketplaceAgent")
            except ImportError as e:
                logger.warning(f"Could not add ContentMarketplaceAgent: {e}")

            # ✅ CRITICAL FIX: Add orphaned revenue-generating agents (sync version)
            orphaned_agents = [
                ('ultimate_money_machine', 'UltimateMoneyMachine'),
                ('affiliate_marketing_empire', 'AffiliateMarketingEmpire'),
                ('autonomous_revenue_system', 'AutonomousRevenueSystem'),
                ('real_client_acquisition', 'RealClientAcquisition'),
                ('real_payment_processor', 'RealPaymentProcessor'),
                ('automated_job_bot', 'AutomatedJobBot'),
                ('intelligent_job_matcher', 'IntelligentJobMatcher'),
                ('job_application_agent', 'JobApplicationAgent'),
                ('freelance_job_analyzer', 'FreelanceJobAnalyzer'),
                ('real_work_delivery_engine', 'RealWorkDeliveryEngine'),
                ('real_job_executor', 'RealJobExecutor'),
            ]

            for module_name, class_name in orphaned_agents:
                try:
                    module = __import__(f'ai_core.agents.{module_name}', fromlist=[class_name])
                    agent_class = getattr(module, class_name)
                    agent_classes[module_name] = agent_class
                    logger.info(f"✅ Added orphaned agent: {class_name}")
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Skipped {module_name}: {e}")

            result_container['agent_classes'] = agent_classes

        except Exception as e:
            logger.error(f"Failed to load agent classes in sync mode: {e}")
            exception_container['error'] = str(e)
            result_container['agent_classes'] = {}

    # Run in thread to avoid async context issues
    thread = threading.Thread(target=load_agents_sync)
    thread.start()
    thread.join(timeout=30)  # 30 second timeout

    if thread.is_alive():
        logger.error("Agent loading timed out after 30 seconds")
        return {}

    if 'error' in exception_container:
        logger.error(f"Agent loading failed: {exception_container['error']}")
        return {}

    return result_container.get('agent_classes', {})


# Required imports for dynamic execution
import json
from datetime import datetime


# ================================================================
# BLUESKY LEARNING ENHANCEMENT FOR AGENTS
# ================================================================

class SocialIntelligenceEnhancer:
    """
    Enhances agents with Bluesky and Reddit social intelligence learning capabilities.
    Provides real-time community insights, expert opinions, and market intelligence.
    """

    def __init__(self):
        self.bluesky_enabled = False
        self.reddit_enabled = False
        self.bluesky_handler = None
        self.bluesky_collector = None
        self.bluesky_learning_bridge = None
        self.reddit_handler = None
        self.reddit_learning_bridge = None

        # Initialize social media integrations
        self._initialize_bluesky_integration()
        self._initialize_reddit_integration()

    def _initialize_bluesky_integration(self):
        """Initialize Bluesky integration for agent learning"""
        try:
            from ..spiders.bluesky_handler import bluesky_handler, bluesky_collector
            from ..intelligence.bluesky_learning_bridge import bluesky_learning_bridge

            self.bluesky_handler = bluesky_handler
            self.bluesky_collector = bluesky_collector
            self.bluesky_learning_bridge = bluesky_learning_bridge
            self.bluesky_enabled = True

            logger.info("🦋 Bluesky agent enhancement enabled")

        except ImportError as e:
            logger.warning(f"Bluesky integration not available for agents: {e}")
            self.bluesky_enabled = False

    def _initialize_reddit_integration(self):
        """Initialize Reddit integration for agent learning"""
        try:
            from ..spiders.reddit_handler import RedditHandler
            from ..intelligence.reddit_learning_bridge import get_reddit_learning_bridge

            self.reddit_handler = RedditHandler()
            self.reddit_learning_bridge = get_reddit_learning_bridge()
            self.reddit_enabled = True

            logger.info("🔴 Reddit agent enhancement enabled")

        except ImportError as e:
            logger.warning(f"Reddit integration not available for agents: {e}")
            self.reddit_enabled = False

    async def enhance_agent_with_social_intelligence(self, agent_instance, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance an agent with combined Bluesky and Reddit intelligence

        Args:
            agent_instance: The agent to enhance
            context: Optional context with task details

        Returns:
            Combined enhancement data from both platforms
        """
        combined_data = {
            'agent': getattr(agent_instance, 'agent_name', 'unknown'),
            'specialization': getattr(agent_instance, 'specialization', 'general'),
            'timestamp': datetime.now().isoformat(),
            'bluesky_intelligence': {},
            'reddit_intelligence': {},
            'combined_insights': [],
            'consensus_recommendations': [],
            'multi_platform_trends': []
        }

        # Get Bluesky intelligence
        if self.bluesky_enabled:
            bluesky_data = await self.enhance_agent_with_bluesky_intelligence(agent_instance, context)
            combined_data['bluesky_intelligence'] = bluesky_data

        # Get Reddit intelligence
        if self.reddit_enabled:
            reddit_data = await self.enhance_agent_with_reddit_intelligence(agent_instance, context)
            combined_data['reddit_intelligence'] = reddit_data

        # Combine insights from both platforms
        all_insights = []

        if 'insights' in combined_data['bluesky_intelligence']:
            for insight in combined_data['bluesky_intelligence']['insights']:
                insight['source'] = 'bluesky'
                all_insights.append(insight)

        if 'insights' in combined_data['reddit_intelligence']:
            for insight in combined_data['reddit_intelligence']['insights']:
                insight['source'] = 'reddit'
                all_insights.append(insight)

        # Sort by confidence/relevance
        all_insights.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        combined_data['combined_insights'] = all_insights[:20]

        # Merge recommendations
        recommendations = []

        if 'recommendations' in combined_data['bluesky_intelligence']:
            for rec in combined_data['bluesky_intelligence']['recommendations']:
                recommendations.append({'source': 'bluesky', 'recommendation': rec})

        if 'recommendations' in combined_data['reddit_intelligence']:
            for rec in combined_data['reddit_intelligence']['recommendations']:
                recommendations.append({'source': 'reddit', 'recommendation': rec})

        combined_data['consensus_recommendations'] = recommendations[:15]

        # Identify cross-platform trends
        bluesky_topics = combined_data['bluesky_intelligence'].get('trending_keywords', [])
        reddit_topics = [t.get('keywords', []) for t in combined_data['reddit_intelligence'].get('trending_topics', [])]
        reddit_topics = sum(reddit_topics, [])  # Flatten list

        # Find common trends
        common_trends = list(set(bluesky_topics) & set(reddit_topics))
        combined_data['multi_platform_trends'] = {
            'bluesky_only': list(set(bluesky_topics) - set(reddit_topics))[:5],
            'reddit_only': list(set(reddit_topics) - set(bluesky_topics))[:5],
            'consensus_trends': common_trends[:5]
        }

        # Update agent's learning context
        if hasattr(agent_instance, 'learning_context'):
            agent_instance.learning_context.update({
                'last_social_update': datetime.now().isoformat(),
                'platforms_used': ['bluesky', 'reddit'],
                'key_insights': combined_data['combined_insights'][:10],
                'active_trends': combined_data['multi_platform_trends']['consensus_trends']
            })

        return combined_data

    async def enhance_agent_with_reddit_intelligence(self, agent_instance, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance an agent with real-time Reddit intelligence

        Args:
            agent_instance: The agent to enhance
            context: Optional context with task details

        Returns:
            Enhanced intelligence data from Reddit
        """
        if not self.reddit_enabled:
            return {"error": "Reddit integration not available"}

        try:
            # Get agent specialization
            specialization = getattr(agent_instance, 'specialization', 'general')
            agent_name = getattr(agent_instance, 'agent_name', 'unknown')

            # Get Reddit insights for this agent
            reddit_insights = await self.reddit_learning_bridge.get_insights_for_agent(
                agent_name,
                specialization
            )

            # Get trending topics relevant to agent
            trending_topics = await self.reddit_learning_bridge.get_trending_topics()

            # Build community consensus on agent's domain
            consensus = None
            if context and 'query' in context:
                consensus = await self.reddit_learning_bridge.get_community_consensus(
                    context['query']
                )

            # Structure the enhancement data
            enhancement_data = {
                'source': 'reddit',
                'agent': agent_name,
                'specialization': specialization,
                'insights': [insight.to_dict() for insight in reddit_insights[:10]],
                'trending_topics': [topic.to_dict() for topic in trending_topics[:5]],
                'community_consensus': consensus.to_dict() if consensus else None,
                'subreddits_monitored': self._get_relevant_subreddits(specialization),
                'enhancement_timestamp': datetime.now().isoformat()
            }

            # Extract actionable recommendations
            recommendations = []
            for insight in reddit_insights[:5]:
                if insight.actionable_advice:
                    recommendations.extend(insight.actionable_advice[:2])

            enhancement_data['recommendations'] = recommendations[:10]

            return enhancement_data

        except Exception as e:
            logger.error(f"Error enhancing agent with Reddit: {e}")
            return {"error": str(e)}

    def _get_relevant_subreddits(self, specialization: str) -> List[str]:
        """Get relevant subreddits for agent specialization"""
        subreddit_mapping = {
            'programming': ['programming', 'learnprogramming', 'webdev'],
            'ai': ['MachineLearning', 'artificial', 'LocalLLaMA'],
            'investing': ['investing', 'stocks', 'ValueInvesting'],
            'business': ['Entrepreneur', 'startups', 'smallbusiness'],
            'crypto': ['CryptoCurrency', 'Bitcoin', 'ethereum'],
            'career': ['cscareerquestions', 'careerguidance', 'jobs'],
            'data': ['datascience', 'bigdata', 'dataengineering']
        }

        # Find matching subreddits
        for key, subreddits in subreddit_mapping.items():
            if key in specialization.lower():
                return subreddits

        # Default subreddits
        return ['technology', 'Futurology', 'tech']

    async def enhance_agent_with_bluesky_intelligence(self, agent_instance, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance an agent with real-time Bluesky intelligence

        Args:
            agent_instance: The agent instance to enhance
            context: Additional context for intelligence gathering

        Returns:
            Enhancement data with insights and learning updates
        """
        if not self.bluesky_enabled:
            return {'error': 'Bluesky integration not available'}

        try:
            # Determine agent specialization and keywords
            specialization = getattr(agent_instance, 'specialization', 'general')
            capabilities = getattr(agent_instance, 'capabilities', [])

            # Generate relevant keywords based on agent type
            keywords = self._generate_agent_keywords(specialization, capabilities, context)

            # Collect Bluesky intelligence
            intelligence = await self.bluesky_collector.collect_intelligence(
                keywords=keywords,
                max_posts_per_keyword=8
            )

            # Extract agent-specific insights
            agent_insights = await self._extract_agent_specific_insights(
                agent_instance, intelligence, context
            )

            # Get market sentiment for agent's domain
            market_sentiment = self._analyze_agent_market_sentiment(
                intelligence, specialization
            )

            # Get expert insights relevant to agent
            expert_insights = await self._get_relevant_expert_insights(
                specialization, keywords
            )

            # Update agent's learning context
            if hasattr(agent_instance, 'learning_context'):
                agent_instance.learning_context.update({
                    'last_bluesky_update': datetime.now().isoformat(),
                    'market_sentiment': market_sentiment,
                    'key_insights': agent_insights[:5],
                    'expert_opinions': expert_insights[:3]
                })

            enhancement_data = {
                'agent_name': getattr(agent_instance, 'agent_name', 'unknown'),
                'specialization': specialization,
                'timestamp': datetime.now().isoformat(),
                'intelligence_summary': {
                    'total_posts_analyzed': len(intelligence.get('posts', [])),
                    'high_quality_insights': len(agent_insights),
                    'market_sentiment_score': market_sentiment.get('overall_sentiment', 0),
                    'expert_insights_count': len(expert_insights)
                },
                'actionable_insights': agent_insights,
                'market_context': market_sentiment,
                'expert_guidance': expert_insights,
                'learning_updates': self._generate_agent_learning_updates(
                    agent_instance, intelligence, agent_insights
                )
            }

            logger.info(f"🦋 Enhanced {getattr(agent_instance, 'agent_name', 'agent')} with {len(agent_insights)} Bluesky insights")

            return enhancement_data

        except Exception as e:
            logger.error(f"Error enhancing agent with Bluesky: {e}")
            return {'error': str(e)}

    def _generate_agent_keywords(self, specialization: str, capabilities: List[str], context: Dict = None) -> List[str]:
        """Generate relevant keywords for an agent's Bluesky intelligence gathering"""
        base_keywords = []

        # Keywords based on specialization
        specialization_keywords = {
            'content_creator': ['content creation', 'writing', 'social media', 'marketing'],
            'job_matcher': ['jobs', 'hiring', 'career', 'employment', 'remote work'],
            'financial_advisor': ['finance', 'investment', 'market', 'trading', 'economy'],
            'tech_consultant': ['technology', 'software', 'programming', 'AI', 'development'],
            'business_analyst': ['business', 'strategy', 'analysis', 'startup', 'growth'],
            'market_researcher': ['market research', 'trends', 'consumer behavior', 'data'],
            'general': ['business', 'technology', 'innovation', 'trends']
        }

        base_keywords.extend(specialization_keywords.get(specialization, ['business', 'technology']))

        # Add capability-based keywords
        for capability in capabilities:
            if 'content' in capability.lower():
                base_keywords.append('content marketing')
            elif 'analysis' in capability.lower():
                base_keywords.append('data analysis')
            elif 'automation' in capability.lower():
                base_keywords.append('automation')

        # Add context-based keywords
        if context:
            if 'industry' in context:
                base_keywords.append(context['industry'])
            if 'topic' in context:
                base_keywords.append(context['topic'])

        return list(set(base_keywords[:6]))  # Remove duplicates, limit to 6

    async def _extract_agent_specific_insights(self, agent_instance, intelligence: Dict, context: Dict) -> List[Dict]:
        """Extract insights specifically relevant to the agent"""
        agent_insights = []
        posts = intelligence.get('posts', [])

        specialization = getattr(agent_instance, 'specialization', 'general')

        for post in posts:
            # Calculate relevance to agent
            relevance_score = self._calculate_agent_post_relevance(post, specialization, context)

            if relevance_score > 0.6:  # High relevance threshold
                insight = {
                    'content': post['text'],
                    'relevance_score': relevance_score,
                    'engagement': post['metrics']['engagement'],
                    'author': post['author']['handle'],
                    'timestamp': post['created_at'],
                    'actionable_elements': self._extract_actionable_elements(post['text']),
                    'key_topics': self._extract_key_topics(post['text'], specialization)
                }
                agent_insights.append(insight)

        # Sort by relevance and engagement
        agent_insights.sort(
            key=lambda x: (x['relevance_score'] * 0.7 + (x['engagement'] / 100) * 0.3),
            reverse=True
        )

        return agent_insights[:10]  # Return top 10 insights

    def _calculate_agent_post_relevance(self, post: Dict, specialization: str, context: Dict) -> float:
        """Calculate how relevant a post is to a specific agent"""
        text_lower = post['text'].lower()
        relevance_score = 0.0

        # Specialization-specific relevance keywords
        relevance_keywords = {
            'content_creator': ['content', 'writing', 'creator', 'audience', 'engagement', 'viral'],
            'job_matcher': ['jobs', 'hiring', 'career', 'salary', 'skills', 'interview'],
            'financial_advisor': ['investment', 'portfolio', 'market', 'returns', 'risk', 'finance'],
            'tech_consultant': ['technology', 'software', 'AI', 'programming', 'development', 'tech stack'],
            'business_analyst': ['business', 'strategy', 'revenue', 'growth', 'analysis', 'metrics'],
            'general': ['business', 'opportunity', 'growth', 'strategy', 'market']
        }

        keywords = relevance_keywords.get(specialization, relevance_keywords['general'])

        # Calculate keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
        relevance_score += keyword_matches * 0.15

        # Engagement boost
        engagement = post['metrics']['engagement']
        relevance_score += min(0.3, engagement / 100)

        # Content quality (length and structure)
        if len(post['text']) > 100:
            relevance_score += 0.1
        if len(post['text']) > 200:
            relevance_score += 0.1

        # Context relevance
        if context:
            for key, value in context.items():
                if str(value).lower() in text_lower:
                    relevance_score += 0.2

        return min(1.0, relevance_score)

    def _analyze_agent_market_sentiment(self, intelligence: Dict, specialization: str) -> Dict:
        """Analyze market sentiment specific to the agent's domain"""
        sentiment_data = {
            'overall_sentiment': 0.0,
            'confidence': 0.0,
            'trend_direction': 'neutral',
            'key_concerns': [],
            'opportunities': []
        }

        try:
            from textblob import TextBlob

            posts = intelligence.get('posts', [])
            if not posts:
                return sentiment_data

            total_sentiment = 0
            sentiment_count = 0

            for post in posts:
                # Analyze sentiment
                blob = TextBlob(post['text'])
                sentiment = blob.sentiment.polarity

                # Weight by engagement and relevance
                weight = 1 + (post['metrics']['engagement'] / 50)
                weighted_sentiment = sentiment * weight

                total_sentiment += weighted_sentiment
                sentiment_count += weight

                # Extract concerns and opportunities
                text_lower = post['text'].lower()
                if sentiment < -0.2 and post['metrics']['engagement'] > 10:
                    sentiment_data['key_concerns'].append(post['text'][:80] + '...')
                elif sentiment > 0.2 and post['metrics']['engagement'] > 10:
                    sentiment_data['opportunities'].append(post['text'][:80] + '...')

            if sentiment_count > 0:
                avg_sentiment = total_sentiment / sentiment_count
                sentiment_data['overall_sentiment'] = avg_sentiment
                sentiment_data['confidence'] = min(1.0, sentiment_count / 30)

                # Determine trend direction
                if avg_sentiment > 0.2:
                    sentiment_data['trend_direction'] = 'positive'
                elif avg_sentiment < -0.2:
                    sentiment_data['trend_direction'] = 'negative'

        except ImportError:
            logger.warning("TextBlob not available for sentiment analysis")

        return sentiment_data

    async def _get_relevant_expert_insights(self, specialization: str, keywords: List[str]) -> List[Dict]:
        """Get expert insights relevant to the agent's specialization"""
        expert_insights = []

        # Map specializations to relevant experts
        expert_mapping = {
            'content_creator': ['dhh.bsky.social', 'pmarca.bsky.social'],
            'job_matcher': ['sama.bsky.social', 'pmarca.bsky.social'],
            'financial_advisor': ['naval.bsky.social', 'pmarca.bsky.social'],
            'tech_consultant': ['karpathy.ai', 'dhh.bsky.social'],
            'business_analyst': ['pmarca.bsky.social', 'sama.bsky.social']
        }

        relevant_experts = expert_mapping.get(specialization, ['pmarca.bsky.social', 'sama.bsky.social'])

        try:
            for expert in relevant_experts:
                posts = await self.bluesky_handler.get_author_feed(expert, limit=5)

                for post in posts:
                    # Check if post is relevant to keywords
                    text_lower = post['text'].lower()
                    keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)

                    if keyword_matches > 0 and post['metrics']['engagement'] > 5:
                        expert_insights.append({
                            'expert': expert,
                            'content': post['text'],
                            'engagement': post['metrics']['engagement'],
                            'timestamp': post['created_at'],
                            'relevance_keywords': [k for k in keywords if k.lower() in text_lower]
                        })

        except Exception as e:
            logger.warning(f"Error getting expert insights: {e}")

        return expert_insights[:5]  # Top 5 expert insights

    def _generate_agent_learning_updates(self, agent_instance, intelligence: Dict, insights: List[Dict]) -> List[str]:
        """Generate learning updates for the agent"""
        learning_updates = []

        try:
            # Extract key learning points from high-quality insights
            for insight in insights[:3]:  # Top 3 insights
                if insight['engagement'] > 15:
                    key_topics = insight.get('key_topics', [])
                    for topic in key_topics:
                        learning_updates.append(f"New trend identified: {topic}")

                # Extract actionable learnings
                actionable = insight.get('actionable_elements', [])
                for action in actionable:
                    learning_updates.append(f"Actionable insight: {action}")

            # Market trend learnings
            market_sentiment = self._analyze_agent_market_sentiment(intelligence,
                getattr(agent_instance, 'specialization', 'general'))

            if market_sentiment['trend_direction'] != 'neutral':
                learning_updates.append(
                    f"Market trend: {market_sentiment['trend_direction']} sentiment detected"
                )

        except Exception as e:
            logger.warning(f"Error generating learning updates: {e}")

        return learning_updates[:7]  # Limit to 7 learning updates

    def _extract_actionable_elements(self, text: str) -> List[str]:
        """Extract actionable elements from text"""
        import re

        actionable_patterns = [
            r'you should (.+?)(?:\.|!|$)',
            r'try (.+?)(?:\.|!|$)',
            r'consider (.+?)(?:\.|!|$)',
            r'recommend (.+?)(?:\.|!|$)'
        ]

        actionables = []
        for pattern in actionable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            actionables.extend([match.strip() for match in matches if len(match.strip()) > 8])

        return actionables[:3]

    def _extract_key_topics(self, text: str, specialization: str) -> List[str]:
        """Extract key topics from text relevant to specialization"""
        # Simplified topic extraction
        words = text.lower().split()

        # Specialization-specific important words
        important_words_by_spec = {
            'content_creator': ['content', 'audience', 'engagement', 'brand', 'storytelling'],
            'job_matcher': ['skills', 'career', 'interview', 'salary', 'remote'],
            'financial_advisor': ['investment', 'portfolio', 'risk', 'returns', 'market'],
            'tech_consultant': ['technology', 'software', 'development', 'architecture', 'scalability']
        }

        spec_words = important_words_by_spec.get(specialization, [])

        # Find relevant words in text
        topics = []
        for word in spec_words:
            if word in text.lower():
                topics.append(word)

        return topics[:3]


# Global enhancer instance (supports both Bluesky and Reddit)
social_intelligence_enhancer = SocialIntelligenceEnhancer()

# Legacy alias for backward compatibility
bluesky_agent_enhancer = social_intelligence_enhancer


async def enhance_agent_with_bluesky(agent_instance, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Public interface to enhance an agent with Bluesky intelligence

    Args:
        agent_instance: The agent to enhance
        context: Optional context for intelligence gathering

    Returns:
        Enhancement data with insights and learning updates
    """
    return await bluesky_agent_enhancer.enhance_agent_with_bluesky_intelligence(
        agent_instance, context
    )


def is_bluesky_learning_enabled() -> bool:
    """Check if Bluesky learning is enabled for agents"""
    return bluesky_agent_enhancer.bluesky_enabled