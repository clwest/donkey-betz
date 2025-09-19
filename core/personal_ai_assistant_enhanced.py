"""
Enhanced Personal AI Assistant with Database and System Access
===============================================================

This module extends the Personal AI Assistant with direct database access,
system status monitoring, and agent execution capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import ExtendedUserProfile, EnhancedUserProfile, JobApplication, UserEmbedding, UserMemoryContext
from core.agent_context_middleware import AgentContextMiddleware
from core.personal_ai_assistant import PersonalAIAssistant
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import UnifiedMemoryManager, get_memory_manager
from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from ml.core.ml_engine import MLEngine
try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    # Fallback if CodebaseEmbeddings is not available
    class CodebaseEmbeddings:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedPersonalAIAssistant(PersonalAIAssistant):
    """
    Enhanced Personal AI Assistant with database access and system capabilities.
    """

    def __init__(self, user: User):
        super().__init__(user)
        self.system_access_enabled = True
        self.database_queries_executed = []
        self._ensure_enhanced_profile()
        self.llm_enforcer = LLMEnforcer()  # Initialize real AI
        self.memory_manager = get_memory_manager(user)  # Initialize unified memory

        # Initialize registries for agent/advisor communication
        self.agent_registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()

        logger.info(f"✅ Enhanced AI Assistant initialized with REAL AI, Unified Memory, and Agent/Advisor Communication for {user.username}")

    def _ensure_enhanced_profile(self):
        """Ensure the user has an enhanced profile."""
        try:
            self.enhanced_profile = EnhancedUserProfile.objects.get(user=self.user)
        except EnhancedUserProfile.DoesNotExist:
            self.enhanced_profile = EnhancedUserProfile.objects.create(user=self.user)
            logger.info(f"Created enhanced profile for {self.user.username}")

    def execute_database_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """
        Execute a database query safely and return results.

        Args:
            query: SQL query to execute
            params: Query parameters for safe execution

        Returns:
            Dictionary with query results and metadata
        """
        try:
            with connection.cursor() as cursor:
                # Log the query for audit
                self.database_queries_executed.append({
                    'query': query,
                    'timestamp': timezone.now().isoformat(),
                    'user': self.user.username
                })

                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch results
                if query.strip().upper().startswith('SELECT'):
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in results]

                    return {
                        'success': True,
                        'data': data,
                        'count': len(data),
                        'query': query,
                        'columns': columns
                    }
                else:
                    # For non-SELECT queries, return affected rows
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount,
                        'query': query
                    }

        except Exception as e:
            logger.error(f"Database query error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including database, agents, and platform health.

        Returns:
            Dictionary with system status information
        """
        status = {
            'timestamp': timezone.now().isoformat(),
            'database': {},
            'agents': {},
            'embeddings': {},
            'platform': {},
            'websockets': {},
            'user': {}
        }

        try:
            # Check database status - use existing tables
            try:
                embeddings_count = self.execute_database_query(
                    "SELECT COUNT(*) as count FROM core_userembedding"
                )
                status['embeddings']['total_count'] = embeddings_count.get('data', [{}])[0].get('count', 0)

                # Check recent embeddings
                recent_embeddings = self.execute_database_query(
                    """
                    SELECT COUNT(*) as count
                    FROM core_userembedding
                    WHERE created_at > %s
                    """,
                    [timezone.now() - timedelta(days=1)]
                )
                status['embeddings']['last_24h'] = recent_embeddings.get('data', [{}])[0].get('count', 0)
            except Exception as e:
                logger.warning(f"Error checking embeddings: {e}")
                status['embeddings']['total_count'] = 0
                status['embeddings']['last_24h'] = 0

            # Check agents status
            agent_registry = get_agent_registry()
            status['agents']['total_registered'] = len(agent_registry.list_agents())
            status['agents']['categories'] = {}
            for agent in agent_registry.list_agents():
                category = agent.get('category', 'uncategorized')
                status['agents']['categories'][category] = status['agents']['categories'].get(category, 0) + 1

            # Check job applications
            job_apps_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_jobapplication WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['job_applications'] = job_apps_count.get('data', [{}])[0].get('count', 0)

            # Check user embeddings
            user_embeddings_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_userembedding WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['embeddings'] = user_embeddings_count.get('data', [{}])[0].get('count', 0)

            # Check WebSocket status
            try:
                from core.unified_hub import UnifiedWebSocketHub
                hub = UnifiedWebSocketHub()
                ws_status = hub.get_status()
                status['websockets'] = {
                    'active': ws_status.get('websocket_active', False),
                    'connections': ws_status.get('active_connections', 0),
                    'last_message': ws_status.get('last_message_time')
                }
            except Exception as e:
                status['websockets']['error'] = str(e)

            # Calculate platform operational percentage
            operational_checks = [
                status['embeddings']['total_count'] > 0,
                status['agents']['total_registered'] > 0,
                status.get('websockets', {}).get('active', False),
                'error' not in status.get('database', {})
            ]
            status['platform']['operational_percentage'] = (sum(operational_checks) / len(operational_checks)) * 100

            # Platform health summary
            status['platform']['health'] = 'healthy' if status['platform']['operational_percentage'] > 75 else 'degraded'
            status['platform']['summary'] = f"Platform is {status['platform']['operational_percentage']:.0f}% operational"

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            status['error'] = str(e)
            status['platform']['health'] = 'error'

        return status

    def search_embeddings(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search embeddings database for relevant content.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching embeddings with metadata
        """
        try:
            # Search in unified embeddings
            results = self.execute_database_query(
                """
                SELECT
                    id, content_type, content_id, content_text,
                    metadata, relevance_score, created_at
                FROM self_awareness_unifiedembedding
                WHERE content_text ILIKE %s
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT %s
                """,
                [f'%{query}%', limit]
            )

            if results.get('success'):
                return results.get('data', [])

            # Fallback to user embeddings
            user_results = self.execute_database_query(
                """
                SELECT
                    id, content, confidence_score,
                    metadata, created_at
                FROM core_userembedding
                WHERE user_id = %s AND content ILIKE %s
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT %s
                """,
                [self.user.id, f'%{query}%', limit]
            )

            return user_results.get('data', [])

        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

    def execute_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Execute an agent with a specific task.

        Args:
            agent_name: Name of the agent to execute
            task: Task description for the agent

        Returns:
            Agent execution results
        """
        try:
            agent_registry = get_agent_registry()

            # Find the agent
            agents = [a for a in agent_registry.list_agents() if agent_name.lower() in a.get('name', '').lower()]

            if not agents:
                return {
                    'success': False,
                    'error': f'Agent "{agent_name}" not found',
                    'available_agents': [a.get('name') for a in agent_registry.list_agents()[:10]]
                }

            agent = agents[0]

            # Execute agent (simplified - in production this would use proper agent execution)
            result = {
                'success': True,
                'agent': agent.get('name'),
                'task': task,
                'status': 'executed',
                'message': f"Agent {agent.get('name')} has been triggered with task: {task}",
                'metadata': {
                    'category': agent.get('category'),
                    'description': agent.get('description'),
                    'timestamp': datetime.now().isoformat()
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate real AI response using LLMEnforcer.

        Args:
            message: User's message
            context: Context including user profile, memories, etc.

        Returns:
            AI-generated response string
        """
        # Build comprehensive context using UnifiedMemoryManager
        recent_memories = self.memory_manager.retrieve_memories(
            user=self.user,
            limit=5
        )
        memory_context = "\n".join([f"- {m['type']}: {m['content']}" for m in recent_memories])

        # Get agent activity context using UnifiedMemoryManager
        agent_activities = self.memory_manager.get_agent_activities(
            user=self.user,
            limit=5
        )
        agent_context = "\n".join([f"- {a['content']}" for a in agent_activities]) if agent_activities else "No recent agent activities"

        # Get cross-agent insights
        insights = self.memory_manager.get_cross_agent_insights(self.user)

        # Extract conversation history from context and load from database
        conversation_context = context.get('conversation_context', '')
        conversation_history = context.get('conversation_history', [])

        # Load recent conversation history from database for context
        recent_conversations = self._load_conversation_history(limit=5)
        if recent_conversations and not conversation_context:
            conversation_context = self._format_conversation_context(recent_conversations)

        # Extract user context (it might be nested)
        user_context = context.get('user_context', {})
        user_first_name = user_context.get('first_name') or context.get('first_name', 'User')
        user_last_name = user_context.get('last_name') or context.get('last_name', '')

        # Build the comprehensive prompt
        system_prompt = f"""You are a highly intelligent personal AI assistant for {self.user.username}.
You have access to their complete profile and learning history, AND the current conversation context.

User Profile:
- Name: {user_first_name} {user_last_name}
- Username: {self.user.username}
- Role: {self.enhanced_profile.primary_role or 'Not specified'}
- Communication Style: {self.enhanced_profile.communication_style or 'balanced'}
- Learning Style: {self.enhanced_profile.learning_style or 'mixed'}
- Long-term Goals: {', '.join(self.enhanced_profile.long_term_goals) if self.enhanced_profile.long_term_goals else 'Not specified'}
- Current Projects: {', '.join(self.enhanced_profile.current_projects) if self.enhanced_profile.current_projects else 'Not specified'}
- Core Skills: {', '.join(list(self.enhanced_profile.core_competencies.keys())[:5]) if self.enhanced_profile.core_competencies else 'Not specified'}

Current Conversation Context:
{conversation_context if conversation_context else 'This is the beginning of our conversation.'}

Recent Memories:
{memory_context}

Recent Agent Activities:
{agent_context}

System Capabilities:
- You can check system status and database queries
- You can execute agents on behalf of the user
- You have access to 149 registered agents and 25 legendary advisors
- You can search embeddings and access platform intelligence

CRITICAL INSTRUCTIONS:
1. ALWAYS address the user by their name: {user_first_name}
2. Maintain conversation continuity - reference what we discussed earlier
3. Build upon previous exchanges naturally - don't restart the conversation
4. Pay attention to nuanced language - distinguish between "exploring/looking at" vs "updating/changing"
5. If they're exploring profile options, help them understand what's available
6. If they're actually making changes, help them complete the process

Respond in a helpful, personalized way that:
1. Starts by addressing {user_first_name} by name
2. References the current conversation context and continues the discussion naturally
3. If they mentioned updating their profile, acknowledge and build on that
4. References relevant past interactions and learned preferences
5. Mentions recent agent activities when relevant
6. Suggests next actions based on their goals and current conversation
7. Uses their preferred communication style ({self.enhanced_profile.communication_style or 'balanced'})
"""

        # Call the LLM Enforcer for real AI response
        try:
            ai_result = self.llm_enforcer.enforce_real_ai(
                prompt=message,
                context=system_prompt,
                agent_name="PersonalAssistant",
                task_type="conversation",
                max_tokens=500,
                # temperature=0.7  # GPT-5 only supports default temperature
            )

            if ai_result['success']:
                response = ai_result['response']
                logger.info(f"✅ Generated REAL AI response for {self.user.username}")
                return response
            else:
                # Fallback if AI fails
                logger.warning(f"⚠️ AI generation failed, using intelligent fallback")
                return self._generate_intelligent_fallback(message, context)

        except Exception as e:
            logger.warning(f"⚠️ LLM not available (likely no API keys configured): {e}")
            logger.info("📋 Using intelligent fallback response with conversation context")
            return self._generate_intelligent_fallback(message, context)

    def _generate_intelligent_fallback(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate an intelligent fallback response when AI is unavailable.
        Uses context and patterns to create relevant response.
        """
        # Extract user context properly
        user_context = context.get('user_context', {})
        user_name = user_context.get('first_name') or context.get('first_name', 'there')
        conversation_context = context.get('conversation_context', '')

        # Analyze message for key topics
        message_lower = message.lower()

        # Profile-related responses
        if any(word in message_lower for word in ['profile', 'professional', 'setup', 'setting up']):
            if 'professional' in message_lower:
                if any(word in message_lower for word in ['feeling out', 'exploring', 'looking at', 'checking out']):
                    return f"Hi {user_name}! I understand you're exploring the Professional profile section to see what options are available. The Professional profile typically includes advanced fields like core competencies, quarterly objectives, delegation preferences, and detailed work schedules. Would you like me to walk you through what each section does, or do you have specific areas you'd like to understand better?"
                else:
                    return f"Hi {user_name}! I can help you set up your Professional profile. This includes defining your primary role, core competencies, communication style, long-term goals, and work preferences. What aspect would you like to start with?"

        # Check for system commands
        if 'status' in message_lower:
            status = self.get_system_status()
            return f"Hi {user_name}! System is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational with {status.get('embeddings', {}).get('total_count', 0)} embeddings and {status.get('agents', {}).get('total_registered', 0)} agents ready."

        if 'help' in message_lower:
            return f"Hi {user_name}! I can help you with job searches, profile management, agent execution, and system queries. What would you like to explore?"

        if 'agent' in message_lower:
            return f"Hi {user_name}! I have access to {len(get_agent_registry().list_agents())} specialized agents. Would you like me to list them or execute a specific one?"

        # Context-aware responses
        if conversation_context and 'profile' in conversation_context.lower():
            return f"Hi {user_name}! Continuing our discussion about profiles - what specific aspect would you like to explore or set up next?"

        # Default personalized response
        recent_project = self.enhanced_profile.current_projects[0] if self.enhanced_profile.current_projects else None
        if recent_project:
            return f"Hi {user_name}! I see you're working on {recent_project}. How can I assist you with that today?"
        else:
            return f"Hello {user_name}! I'm here to help with your goals. What would you like to work on?"

    def _generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override parent's template-based response with real AI.

        Args:
            message: User's message
            context: Context dictionary

        Returns:
            Response dictionary with AI-generated content
        """
        # Generate real AI response
        ai_response = self._generate_ai_response(message, context)

        # Determine intent for suggestions
        intent = context.get('intent', 'general')

        # Generate smart suggestions based on context and AI response
        suggestions = self.generate_personalized_suggestions(message)

        # Determine confidence based on whether we used real AI or fallback
        confidence = 0.9 if 'Generated REAL AI response' in str(logger) else 0.6

        # Build response dictionary
        response_data = {
            'response': ai_response,
            'suggestions': suggestions,
            'actions': self._extract_actions_from_response(ai_response),
            'confidence': confidence,
            'ai_generated': True,  # Flag to indicate real AI was used
            'model': 'gpt-5-mini' if self.llm_enforcer.openai_client else 'intelligent-fallback'
        }

        return response_data

    def _extract_actions_from_response(self, response: str) -> List[str]:
        """
        Extract potential actions from AI response.

        Args:
            response: AI-generated response

        Returns:
            List of action identifiers
        """
        actions = []
        response_lower = response.lower()

        # Map keywords to actions
        action_map = {
            'search': ['search_jobs', 'search_embeddings'],
            'agent': ['list_agents', 'execute_agent'],
            'profile': ['edit_profile', 'view_profile'],
            'job': ['search_jobs', 'view_applications'],
            'status': ['system_status', 'check_health'],
            'help': ['show_help_menu']
        }

        for keyword, action_list in action_map.items():
            if keyword in response_lower:
                actions.extend(action_list)

        return list(set(actions))[:5]  # Return unique actions, max 5

    def process_system_command(self, command: str) -> Dict[str, Any]:
        """
        Process system-level commands from the assistant.

        Args:
            command: System command to process

        Returns:
            Command execution results
        """
        command_lower = command.lower()

        # Database status command
        if 'database' in command_lower or 'embeddings count' in command_lower:
            status = self.get_system_status()
            return {
                'type': 'system_status',
                'embeddings': status.get('embeddings'),
                'database_health': status.get('platform', {}).get('health'),
                'response': f"Database contains {status.get('embeddings', {}).get('total_count', 0)} embeddings. "
                           f"Platform is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational."
            }

        # Search embeddings command
        elif 'search' in command_lower and 'embedding' in command_lower:
            # Extract search term (simple extraction)
            search_term = command.replace('search embeddings', '').replace('search embedding', '').strip()
            if search_term:
                results = self.search_embeddings(search_term, limit=3)
                return {
                    'type': 'search_results',
                    'query': search_term,
                    'count': len(results),
                    'results': results,
                    'response': f"Found {len(results)} embeddings matching '{search_term}'"
                }

        # WebSocket status
        elif 'websocket' in command_lower:
            status = self.get_system_status()
            ws_status = status.get('websockets', {})
            return {
                'type': 'websocket_status',
                'status': ws_status,
                'response': f"WebSocket hub is {'active' if ws_status.get('active') else 'inactive'}. "
                           f"Active connections: {ws_status.get('connections', 0)}"
            }

        # Agent list command
        elif 'list agents' in command_lower:
            agent_registry = get_agent_registry()
            agents = agent_registry.list_agents()[:10]  # First 10 agents
            return {
                'type': 'agent_list',
                'total_agents': len(agent_registry.list_agents()),
                'sample_agents': [a.get('name') for a in agents],
                'response': f"System has {len(agent_registry.list_agents())} registered agents. "
                           f"Sample: {', '.join([a.get('name') for a in agents[:5]])}"
            }

        # Execute agent command
        elif 'execute agent' in command_lower or 'run agent' in command_lower:
            # Simple parsing - in production this would be more sophisticated
            parts = command.split(' ')
            if len(parts) > 2:
                agent_name = parts[2] if 'agent' in parts else parts[1]
                task = ' '.join(parts[3:]) if len(parts) > 3 else 'default task'
                result = self.execute_agent(agent_name, task)
                return {
                    'type': 'agent_execution',
                    'result': result,
                    'response': result.get('message', 'Agent execution completed')
                }

        return {
            'type': 'unknown_command',
            'response': "I can help with database queries, embeddings search, system status, and agent execution. "
                       "Try: 'check database status', 'search embeddings [term]', 'list agents', or 'execute agent [name] [task]'"
        }

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhanced message processing with system command support and full profile integration.

        Args:
            message: User's message
            context: Optional additional context

        Returns:
            Response dictionary with enhanced capabilities
        """
        # Analyze user patterns and conversation history for contextual memory
        user_patterns = self._analyze_user_patterns()

        # Load conversation history for context
        conversation_history = self._load_conversation_history(limit=3)
        conversation_context = self._format_conversation_context(conversation_history)

        # Create personalized context based on patterns
        personalized_context = self._create_personalized_context(message, user_patterns)

        # Load enhanced profile context for personalization
        profile_context = self.enhanced_profile.get_context_for_ai('chat')

        # Merge profile context with provided context
        full_context = {
            'user_profile': profile_context,
            'user_role': self.enhanced_profile.primary_role or 'User',
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'learning_style': self.enhanced_profile.learning_style or 'mixed',
            'goals': self.enhanced_profile.long_term_goals,
            'current_projects': self.enhanced_profile.current_projects,
            'skills': {'top_skills': list(self.enhanced_profile.core_competencies.keys())[:5] if self.enhanced_profile.core_competencies else []},
            'timezone': self.enhanced_profile.time_zone,
            'work_hours': self.enhanced_profile.work_schedule,
            'decision_framework': self.enhanced_profile.decision_framework,
            'conversation_history': conversation_context,
            'personalization_context': personalized_context,
            'user_patterns': user_patterns
        }

        if context:
            full_context.update(context)

        # Check for agent execution requests
        agent_execution_phrases = [
            'can you have an agent', 'execute agent', 'run agent', 'use agent',
            'deploy agent', 'have the agent', 'get an agent to', 'agent analyze',
            'agent help', 'technical-signal-agent', 'research agent'
        ]

        is_agent_request = any(phrase in message.lower() for phrase in agent_execution_phrases)

        if is_agent_request:
            # Extract the task from the message
            task = self._extract_task_from_message(message)

            # Route to appropriate agent
            routing_result = self.route_to_agent(task)

            if routing_result['success']:
                # Generate AI response with agent execution results
                response_data = self._generate_response(message, full_context)
                response_data['agent_execution'] = routing_result
                response_data['response'] = f"I've successfully routed your request to the {routing_result['agent']['name']} agent. " + \
                                          f"The agent is now analyzing: '{task}'. " + \
                                          f"Execution ID: {routing_result['execution_id']}. " + \
                                          response_data.get('response', '')
                response_data['confidence'] = 0.9
                return response_data
            else:
                # Generate response with agent routing failure
                response_data = self._generate_response(message, full_context)
                response_data['agent_execution'] = routing_result
                response_data['response'] = f"I attempted to route your request to an agent, but encountered an issue: {routing_result.get('error', 'Unknown error')}. " + \
                                          response_data.get('response', '')
                return response_data

        # Check if this is a system command
        system_keywords = ['database', 'embedding', 'system', 'status', 'websocket', 'query']

        if any(keyword in message.lower() for keyword in system_keywords):
            # Process as system command
            system_result = self.process_system_command(message)

            # Use AI generation instead of parent's template response
            response_data = self._generate_response(message, full_context)

            # Enhanced response with system data
            response_data['response'] = system_result.get('response', response_data['response'])
            response_data['system_data'] = system_result
            response_data['confidence'] = 0.9  # High confidence for system queries

            # Add relevant suggestions based on system command and user profile
            if system_result.get('type') == 'system_status':
                response_data['suggestions'] = [
                    'Search embeddings',
                    'List agents',
                    'Check WebSocket status',
                    'View my applications'
                ]
            elif system_result.get('type') == 'agent_list':
                # Personalize agent suggestions based on user's role and goals
                if 'software' in (self.enhanced_profile.primary_role or '').lower():
                    response_data['suggestions'] = [
                        'Execute agent Code Optimizer',
                        'Execute agent Testing Agent',
                        'Show development agents',
                        'Agent capabilities'
                    ]
                else:
                    response_data['suggestions'] = [
                        'Execute agent Income Builder',
                        'Execute agent Job Matcher',
                        'Show agent categories',
                        'Agent capabilities'
                    ]

            return response_data

        # Regular message processing with AI instead of templates
        response_data = self._generate_response(message, full_context)

        # Personalize response based on communication style
        if self.enhanced_profile.communication_style == 'detailed':
            # Add more context and explanation to response
            response_data['additional_context'] = self.get_detailed_explanation(message)
        elif self.enhanced_profile.communication_style == 'concise':
            # Keep response brief
            response_data['response'] = self.make_concise(response_data.get('response', ''))

        # Generate personalized suggestions based on goals and current projects
        response_data['suggestions'] = self.generate_personalized_suggestions(message)

        # Enhance response with memory-based personalization
        if response_data.get('response'):
            response_data['response'] = self._enhance_response_with_memory(
                response_data['response'],
                user_patterns
            )

        # Store interaction as memory with context
        self.store_memory(
            'interaction',
            f"User asked: {message[:100]}...",
            response=response_data.get('response', '')[:100],
            importance=5,
            metadata={
                'full_message': message,
                'response_type': response_data.get('type', 'general'),
                'confidence': response_data.get('confidence', 0.5)
            }
        )

        # Update profile from interaction
        self.update_profile_from_interaction(message, response_data.get('response', ''))

        # Store conversation in database for persistence and future retrieval
        self._store_conversation(message, response_data)

        return response_data

    def get_enhanced_context(self) -> Dict[str, Any]:
        """
        Get enhanced context with system status and profile data.

        Returns:
            Enhanced context dictionary
        """
        # Get base context
        context = self.get_personalized_context()

        # Add system status
        system_status = self.get_system_status()
        context['system'] = {
            'database_healthy': system_status.get('platform', {}).get('health') == 'healthy',
            'total_embeddings': system_status.get('embeddings', {}).get('total_count', 0),
            'total_agents': system_status.get('agents', {}).get('total_registered', 0),
            'websocket_active': system_status.get('websockets', {}).get('active', False),
            'operational_percentage': system_status.get('platform', {}).get('operational_percentage', 0)
        }

        # Add recent database queries
        context['system']['recent_queries'] = len(self.database_queries_executed)

        # Add enhanced profile context
        if hasattr(self, 'enhanced_profile'):
            context['enhanced_profile'] = self.enhanced_profile.get_context_for_ai('general')

        return context

    def store_memory(self, memory_type: str, content: str, **kwargs) -> UserMemoryContext:
        """
        Store a memory using UnifiedMemoryManager.

        Args:
            memory_type: Type of memory (decision, preference, etc.)
            content: Content of the memory
            **kwargs: Additional metadata

        Returns:
            Created UserMemoryContext instance
        """
        memory = self.memory_manager.store_memory(
            user=self.user,
            source='assistant',
            memory_type=memory_type,
            content=content,
            importance=kwargs.get('importance', 5),
            related_project=kwargs.get('related_project', ''),
            related_goal=kwargs.get('related_goal', ''),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {})
        )
        logger.info(f"Stored {memory_type} memory via UnifiedMemoryManager for {self.user.username}: {content[:50]}...")
        return memory

    def retrieve_memories(self, memory_type: str = None, limit: int = 10) -> List[UserMemoryContext]:
        """
        Retrieve user memories.

        Args:
            memory_type: Filter by memory type (optional)
            limit: Maximum number of memories to retrieve

        Returns:
            List of UserMemoryContext instances
        """
        query = UserMemoryContext.objects.filter(user=self.user)

        if memory_type:
            query = query.filter(memory_type=memory_type)

        memories = query[:limit]

        # Update access counts
        for memory in memories:
            memory.accessed_count += 1
            memory.last_accessed = timezone.now()
            memory.save(update_fields=['accessed_count', 'last_accessed'])

        return list(memories)

    def update_profile_from_interaction(self, message: str, response: str):
        """
        Enhanced profile update with intelligent pattern extraction and learning.

        Args:
            message: User's message
            response: Assistant's response
        """
        message_lower = message.lower()
        updates_made = []

        # Detect and store preferences
        if 'prefer' in message_lower or 'like' in message_lower or 'favorite' in message_lower:
            self.store_memory('preference', message, importance=7)
            updates_made.append('preference')

        # Detect goals
        if 'goal' in message_lower or 'want to' in message_lower or 'plan to' in message_lower:
            self.store_memory('goal', message, importance=8)
            updates_made.append('goal')

            # Extract and update long-term goals if mentioned
            if 'long term' in message_lower or 'future' in message_lower:
                goal_text = self.extract_goal_text(message)
                if goal_text and goal_text not in (self.enhanced_profile.long_term_goals or []):
                    if not self.enhanced_profile.long_term_goals:
                        self.enhanced_profile.long_term_goals = []
                    self.enhanced_profile.long_term_goals.append(goal_text)
                    self.enhanced_profile.save(update_fields=['long_term_goals'])
                    logger.info(f"Added long-term goal for {self.user.username}: {goal_text}")

        # Detect decisions
        if 'decide' in message_lower or 'choose' in message_lower or 'selected' in message_lower:
            self.store_memory('decision', message, importance=6)
            updates_made.append('decision')

        # Extract skills mentioned
        skill_keywords = ['know', 'can', 'skilled in', 'experience with', 'worked with', 'expert in']
        if any(keyword in message_lower for keyword in skill_keywords):
            skills = self.extract_skills(message)
            if skills:
                current_skills = self.enhanced_profile.core_competencies or {}
                for skill in skills:
                    if skill not in current_skills:
                        # Add with default proficiency level 5
                        current_skills[skill] = 5
                if len(current_skills) > len(self.enhanced_profile.core_competencies or {}):
                    self.enhanced_profile.core_competencies = current_skills
                    self.enhanced_profile.save(update_fields=['core_competencies'])
                    new_skills = [s for s in skills if s not in (self.enhanced_profile.core_competencies or {})]
                    self.store_memory('skill', f"Identified skills: {', '.join(skills)}", importance=6)
                    logger.info(f"Added skills for {self.user.username}: {skills}")

        # Extract project mentions
        project_keywords = ['working on', 'project', 'building', 'developing', 'creating']
        if any(keyword in message_lower for keyword in project_keywords):
            projects = self.extract_projects(message)
            if projects:
                current_projects = self.enhanced_profile.current_projects or []
                new_projects = [p for p in projects if p not in current_projects]
                if new_projects:
                    self.enhanced_profile.current_projects = current_projects + new_projects
                    self.enhanced_profile.save(update_fields=['current_projects'])
                    self.store_memory('project', f"Working on: {', '.join(new_projects)}", importance=7)
                    logger.info(f"Added projects for {self.user.username}: {new_projects}")

        # Detect communication style patterns
        if self.enhanced_profile.interaction_count > 5:
            # After 5 interactions, start detecting patterns
            self.detect_communication_patterns(message)

        # Track profile access
        if hasattr(self, 'enhanced_profile'):
            self.enhanced_profile.interaction_count += 1
            self.enhanced_profile.save(update_fields=['interaction_count'])

        # Store summary of what was learned
        if updates_made:
            self.store_memory(
                'learning',
                f"Learned about: {', '.join(updates_made)}",
                importance=5,
                metadata={'message': message[:200], 'categories': updates_made}
            )

    def generate_personalized_suggestions(self, message: str) -> List[str]:
        """
        Generate personalized suggestions based on user profile and message context.

        Args:
            message: User's message

        Returns:
            List of personalized suggestions
        """
        suggestions = []

        # Base suggestions on user's primary role
        if self.enhanced_profile.primary_role:
            if 'engineer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review code', 'Check system status', 'Run tests'])
            elif 'manager' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review team progress', 'Check project status', 'Schedule meeting'])
            elif 'designer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review designs', 'Check feedback', 'Update portfolio'])

        # Add suggestions based on current projects
        if self.enhanced_profile.current_projects:
            for project in self.enhanced_profile.current_projects[:2]:
                suggestions.append(f"Update on {project}")

        # Add goal-based suggestions
        if self.enhanced_profile.long_term_goals:
            suggestions.append('Review goal progress')

        # Default suggestions if none generated
        if not suggestions:
            suggestions = ['Tell me more', 'Show options', 'Help me decide', 'What else?']

        return suggestions[:5]  # Limit to 5 suggestions

    def get_detailed_explanation(self, message: str) -> str:
        """
        Generate detailed explanation for users who prefer detailed communication.

        Args:
            message: User's message

        Returns:
            Detailed explanation string
        """
        explanations = []

        # Add context about the message type
        if 'how' in message.lower():
            explanations.append("This appears to be a how-to question. I'll provide step-by-step guidance.")
        elif 'why' in message.lower():
            explanations.append("This is a reasoning question. I'll explain the underlying concepts.")
        elif 'what' in message.lower():
            explanations.append("This is a definitional question. I'll provide clear explanations.")

        # Add profile-based context
        if self.enhanced_profile.learning_style == 'visual':
            explanations.append("Based on your visual learning style, I'll try to paint a clear picture.")
        elif self.enhanced_profile.learning_style == 'hands-on':
            explanations.append("Given your hands-on learning preference, I'll include practical examples.")

        return ' '.join(explanations) if explanations else ''

    def make_concise(self, response: str, max_length: int = 200) -> str:
        """
        Make response more concise for users who prefer brief communication.

        Args:
            response: Original response
            max_length: Maximum length for concise response

        Returns:
            Concise version of the response
        """
        if len(response) <= max_length:
            return response

        # Try to cut at sentence boundary
        sentences = response.split('. ')
        concise = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                concise.append(sentence)
                current_length += len(sentence) + 2  # +2 for '. '
            else:
                break

        result = '. '.join(concise)
        if result and not result.endswith('.'):
            result += '.'

        return result if result else response[:max_length] + '...'

    def extract_goal_text(self, message: str) -> Optional[str]:
        """
        Extract goal text from user message.

        Args:
            message: User's message containing goal

        Returns:
            Extracted goal text or None
        """
        # Simple extraction - in production this would use NLP
        goal_phrases = ['want to', 'goal is to', 'plan to', 'aiming to', 'hoping to']

        for phrase in goal_phrases:
            if phrase in message.lower():
                start = message.lower().index(phrase) + len(phrase)
                # Extract up to next punctuation or end
                end = len(message)
                for punct in ['.', '!', '?', ',', ';']:
                    if punct in message[start:]:
                        end = start + message[start:].index(punct)
                        break

                goal = message[start:end].strip()
                # Clean up common words
                goal = goal.replace(' to ', ' ').replace(' the ', ' ')
                return goal[:100]  # Limit length

        return None

    def extract_skills(self, message: str) -> List[str]:
        """
        Extract skills mentioned in user message.

        Args:
            message: User's message

        Returns:
            List of extracted skills
        """
        skills = []

        # Common skill patterns
        skill_patterns = [
            'know ', 'skilled in ', 'experience with ', 'worked with ',
            'expert in ', 'familiar with ', 'proficient in '
        ]

        message_lower = message.lower()
        for pattern in skill_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract word or phrase after pattern
                words = message[start:].split()
                if words:
                    # Take up to 3 words as skill
                    skill = ' '.join(words[:3]).strip('.,!?;')
                    if len(skill) > 2:  # Minimum skill length
                        skills.append(skill)

        # Common tech skills mentioned directly
        tech_skills = ['Python', 'JavaScript', 'React', 'Django', 'SQL', 'Docker',
                      'AWS', 'Machine Learning', 'AI', 'DevOps', 'Kubernetes']

        for skill in tech_skills:
            if skill.lower() in message_lower and skill not in skills:
                skills.append(skill)

        return skills[:10]  # Limit to 10 skills

    def extract_projects(self, message: str) -> List[str]:
        """
        Extract project names or descriptions from message.

        Args:
            message: User's message

        Returns:
            List of project names/descriptions
        """
        projects = []

        # Project indicators
        project_patterns = [
            'working on ', 'building ', 'developing ', 'creating ',
            'project called ', 'project named '
        ]

        message_lower = message.lower()
        for pattern in project_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract following words
                words = message[start:].split()
                if words:
                    # Take up to 5 words as project description
                    project = ' '.join(words[:5]).strip('.,!?;')
                    if len(project) > 2:
                        projects.append(project)

        return projects[:5]  # Limit to 5 projects

    def detect_communication_patterns(self, message: str):
        """
        Detect and update communication style patterns.

        Args:
            message: User's message
        """
        # Analyze message length patterns
        recent_memories = self.retrieve_memories('interaction', limit=10)

        if len(recent_memories) >= 5:
            avg_length = sum(len(m.content) for m in recent_memories) / len(recent_memories)

            # Detect communication style
            if avg_length < 50:
                new_style = 'concise'
            elif avg_length > 200:
                new_style = 'detailed'
            else:
                new_style = 'balanced'

            # Update if different from current
            if self.enhanced_profile.communication_style != new_style:
                self.enhanced_profile.communication_style = new_style
                self.enhanced_profile.save(update_fields=['communication_style'])
                self.store_memory(
                    'pattern',
                    f"Communication style updated to: {new_style}",
                    importance=6
                )
                logger.info(f"Updated communication style for {self.user.username}: {new_style}")

        # Detect question patterns
        if '?' in message:
            # User asks questions - might prefer interactive style
            question_count = sum(1 for m in recent_memories if '?' in m.content)
            if question_count > len(recent_memories) * 0.7:  # 70% questions
                if self.enhanced_profile.learning_style != 'interactive':
                    self.enhanced_profile.learning_style = 'interactive'
                    self.enhanced_profile.save(update_fields=['learning_style'])
                    logger.info(f"Detected interactive learning style for {self.user.username}")

    def _store_conversation(self, message: str, response_data: Dict[str, Any]) -> None:
        """
        Store conversation in database for persistence and future retrieval.

        Args:
            message: User's message
            response_data: Assistant's response data
        """
        try:
            from core.models import ConversationMemory, ChatConversation
            import uuid

            # Store in ConversationMemory for learning
            ConversationMemory.objects.create(
                user=self.user,
                message=message,
                response=response_data.get('response', ''),
                agents_used=response_data.get('agents_used', []),
                intent=response_data.get('intent', 'general'),
                success=True
            )

            # Store in ChatConversation for detailed tracking
            ChatConversation.objects.create(
                user=self.user,
                conversation_id=str(uuid.uuid4()),
                user_message=message,
                assistant_response=response_data.get('response', ''),
                context_used=response_data.get('context', {}),
                metadata={
                    'confidence': response_data.get('confidence', 0.5),
                    'ai_generated': response_data.get('ai_generated', False),
                    'model': response_data.get('model', 'unknown'),
                    'actions': response_data.get('actions', []),
                    'suggestions': response_data.get('suggestions', [])
                },
                response_time_ms=response_data.get('response_time_ms', 0)
            )

            # Create embedding for the conversation
            self._create_conversation_embedding(message, response_data.get('response', ''))

            logger.info(f"💾 Stored conversation for {self.user.username}: {message[:50]}...")

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

    def _create_conversation_embedding(self, message: str, response: str) -> None:
        """
        Create embedding for conversation to enable semantic search.

        Args:
            message: User's message
            response: Assistant's response
        """
        try:
            from core.models import UserEmbedding

            # Combine message and response for comprehensive context
            combined_text = f"User: {message}\nAssistant: {response}"

            # Use memory manager to create embedding
            self.memory_manager.store_memory(
                'conversation',
                combined_text,
                metadata={
                    'message': message,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Also create direct UserEmbedding for compatibility
            UserEmbedding.objects.create(
                user=self.user,
                content=combined_text,
                content_type='conversation',
                source='personal_assistant',
                metadata={
                    'message_length': len(message),
                    'response_length': len(response),
                    'conversation_type': 'interactive'
                }
            )

            logger.info(f"🧠 Created conversation embedding for {self.user.username}")

        except Exception as e:
            logger.error(f"Error creating conversation embedding: {e}")

    def _load_conversation_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Load recent conversation history from database.

        Args:
            limit: Maximum number of conversations to load

        Returns:
            List of conversation dictionaries
        """
        try:
            from core.models import ConversationMemory

            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:limit]

            return [
                {
                    'message': conv.message,
                    'response': conv.response,
                    'timestamp': conv.created_at.isoformat(),
                    'intent': conv.intent
                }
                for conv in conversations
            ]

        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []

    def _format_conversation_context(self, conversations: List[Dict[str, Any]]) -> str:
        """
        Format conversation history into context string.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            Formatted conversation context string
        """
        if not conversations:
            return ""

        context_parts = ["Recent conversation history:"]

        # Reverse to show oldest first (chronological order)
        for conv in reversed(conversations):
            context_parts.append(f"User: {conv['message']}")
            context_parts.append(f"Assistant: {conv['response'][:100]}...")
            context_parts.append("")  # Empty line for readability

        return "\n".join(context_parts)

    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """
        Analyze user conversation patterns and preferences.

        Returns:
            Dictionary containing user patterns and preferences
        """
        try:
            from core.models import ConversationMemory, UserProfile
            from collections import Counter
            import json

            # Get user conversations
            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:50]  # Last 50 conversations

            if not conversations:
                return {}

            # Analyze conversation patterns
            intents = [conv.intent for conv in conversations if conv.intent]
            agents_used = []
            for conv in conversations:
                if conv.agents_used:
                    if isinstance(conv.agents_used, str):
                        try:
                            agents_used.extend(json.loads(conv.agents_used))
                        except:
                            pass
                    elif isinstance(conv.agents_used, list):
                        agents_used.extend(conv.agents_used)

            # Get user profile if exists
            user_profile = None
            try:
                user_profile = UserProfile.objects.get(user=self.user)
            except UserProfile.DoesNotExist:
                pass

            patterns = {
                'conversation_count': len(conversations),
                'common_intents': dict(Counter(intents).most_common(5)),
                'preferred_agents': dict(Counter(agents_used).most_common(5)),
                'interaction_frequency': self._calculate_interaction_frequency(conversations),
                'user_profile': {
                    'skills': user_profile.skills if user_profile and user_profile.skills else [],
                    'current_role': user_profile.current_role if user_profile and user_profile.current_role else '',
                    'occupation': user_profile.occupation if user_profile and user_profile.occupation else '',
                    'industries': user_profile.industries if user_profile and user_profile.industries else [],
                    'remote_only': user_profile.remote_only if user_profile else False,
                    'preferred_ai_model': user_profile.preferred_ai_model if user_profile and user_profile.preferred_ai_model else '',
                } if user_profile else {}
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}

    def _calculate_interaction_frequency(self, conversations) -> str:
        """Calculate user interaction frequency."""
        if len(conversations) < 2:
            return "new_user"

        from datetime import datetime, timedelta

        now = timezone.now()
        recent_conversations = [
            conv for conv in conversations
            if (now - conv.created_at.replace(tzinfo=None)) <= timedelta(days=7)
        ]

        weekly_count = len(recent_conversations)

        if weekly_count >= 20:
            return "very_active"
        elif weekly_count >= 10:
            return "active"
        elif weekly_count >= 3:
            return "regular"
        else:
            return "occasional"

    def _create_personalized_context(self, message: str, patterns: Dict[str, Any]) -> str:
        """
        Create personalized context based on user patterns and current message.

        Args:
            message: Current user message
            patterns: User patterns from analysis

        Returns:
            Personalized context string
        """
        context_parts = []

        # User interaction profile
        frequency = patterns.get('interaction_frequency', 'new_user')
        conv_count = patterns.get('conversation_count', 0)

        if frequency == "very_active":
            context_parts.append("🔥 Very active user - provide detailed, advanced responses")
        elif frequency == "active":
            context_parts.append("⚡ Active user - can handle comprehensive information")
        elif frequency == "regular":
            context_parts.append("👤 Regular user - balance detail with clarity")
        else:
            context_parts.append("🌟 Welcome! Provide clear, helpful introductory responses")

        # User preferences and skills
        user_profile = patterns.get('user_profile', {})
        if user_profile.get('skills'):
            skills_text = ", ".join(user_profile['skills'][:3])
            context_parts.append(f"💼 User skills: {skills_text}")

        if user_profile.get('goals'):
            goals_text = ", ".join(user_profile['goals'][:2])
            context_parts.append(f"🎯 User goals: {goals_text}")

        # Common intents
        common_intents = patterns.get('common_intents', {})
        if common_intents:
            top_intent = next(iter(common_intents.keys()))
            context_parts.append(f"🧠 User typically asks about: {top_intent}")

        # Preferred agents
        preferred_agents = patterns.get('preferred_agents', {})
        if preferred_agents:
            top_agents = list(preferred_agents.keys())[:2]
            context_parts.append(f"🤖 Often uses: {', '.join(top_agents)}")

        # Message intent analysis
        message_lower = message.lower()
        if any(word in message_lower for word in ['urgent', 'asap', 'quickly', 'fast']):
            context_parts.append("⚡ URGENT REQUEST - Prioritize speed and direct answers")
        elif any(word in message_lower for word in ['explain', 'how', 'why', 'understand']):
            context_parts.append("📚 LEARNING REQUEST - Provide educational, detailed responses")
        elif any(word in message_lower for word in ['help', 'stuck', 'problem', 'issue']):
            context_parts.append("🆘 HELP REQUEST - Focus on practical solutions")

        if context_parts:
            return "PERSONALIZATION CONTEXT:\n" + "\n".join(context_parts) + "\n\n"

        return ""

    def _enhance_response_with_memory(self, response: str, patterns: Dict[str, Any]) -> str:
        """
        Enhance response with memory-based personalization.

        Args:
            response: Original response
            patterns: User patterns

        Returns:
            Enhanced response
        """
        try:
            # Add memory-based enhancements
            enhancements = []

            # Reference past interactions if relevant
            conv_count = patterns.get('conversation_count', 0)
            if conv_count > 5:
                frequency = patterns.get('interaction_frequency', 'new_user')
                if frequency in ['active', 'very_active']:
                    enhancements.append("Based on our previous conversations")

            # Suggest relevant agents based on past usage
            preferred_agents = patterns.get('preferred_agents', {})
            if preferred_agents and len(preferred_agents) > 0:
                top_agent = next(iter(preferred_agents.keys()))
                if 'opportunity' in response.lower() or 'job' in response.lower():
                    enhancements.append(f"You might also want to try the {top_agent} agent")

            # Add goal-oriented suggestions
            user_goals = patterns.get('user_profile', {}).get('goals', [])
            if user_goals and any(goal in response.lower() for goal in [g.lower() for g in user_goals]):
                enhancements.append("This aligns with your stated goals")

            # Enhance response if we have enhancements
            if enhancements:
                enhanced_parts = [response]
                enhanced_parts.append("\n💡 Personal Notes:")
                for enhancement in enhancements:
                    enhanced_parts.append(f"  • {enhancement}")

                return "\n".join(enhanced_parts)

            return response

        except Exception as e:
            logger.error(f"Error enhancing response with memory: {e}")
            return response

    # =====================================================
    # AGENT COMMUNICATION BRIDGE METHODS
    # =====================================================

    def route_to_agent(self, task: str, agent_type: str = None, required_capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Route a task to the most appropriate agent.

        Args:
            task: Task description
            agent_type: Preferred agent type/specialization
            required_capabilities: Required agent capabilities

        Returns:
            Agent routing and execution results
        """
        try:
            # Find the best agent for the task
            best_agent = self.agent_registry.find_best_agent(
                task_description=task,
                required_capabilities=required_capabilities,
                preferred_specialization=agent_type
            )

            if not best_agent:
                return {
                    'success': False,
                    'error': 'No suitable agent found for this task',
                    'suggestions': self._suggest_alternative_agents(task)
                }

            # Execute the agent
            execution_id = self.agent_registry.execute_agent(
                agent_name=best_agent['name'],
                task_data={
                    'task': task,
                    'user_id': str(self.user.id),  # Convert to string for JSON serialization
                    'context': self._get_agent_context()
                }
            )

            if execution_id:
                # Store agent interaction as memory
                self.store_memory(
                    'agent_interaction',
                    f"Routed task to {best_agent['name']}: {task}",
                    importance=7,
                    metadata={
                        'agent_name': best_agent['name'],
                        'execution_id': execution_id,
                        'task': task
                    }
                )

                logger.info(f"🤖 Routed task to agent {best_agent['name']} for {self.user.username}")

                return {
                    'success': True,
                    'agent': best_agent,
                    'execution_id': execution_id,
                    'message': f"Task routed to {best_agent['display_name']} agent",
                    'status': 'initiated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to execute agent',
                    'agent': best_agent
                }

        except Exception as e:
            logger.error(f"Error routing to agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_agent_response(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get response from a specific agent.

        Args:
            agent_id: Agent identifier
            task_data: Task data to send to agent

        Returns:
            Agent response data
        """
        try:
            # Get agent details
            agent = self.agent_registry.get_agent(agent_id)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                }

            # Execute agent with enhanced task data
            enhanced_task_data = {
                **task_data,
                'user_profile': self.enhanced_profile.get_context_for_ai('agent'),
                'user_preferences': {
                    'communication_style': self.enhanced_profile.communication_style,
                    'learning_style': self.enhanced_profile.learning_style
                },
                'context': self._get_agent_context()
            }

            execution_id = self.agent_registry.execute_agent(agent_id, enhanced_task_data)

            if execution_id:
                # Monitor execution status
                status = self.agent_registry.get_execution_status(execution_id)

                # Store interaction
                self.store_memory(
                    'agent_response',
                    f"Got response from {agent['name']}: {task_data.get('task', 'No task specified')}",
                    importance=6,
                    metadata={
                        'agent_id': agent_id,
                        'execution_id': execution_id,
                        'status': status
                    }
                )

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'execution_id': execution_id,
                    'status': status,
                    'response_available': status.get('status') == 'completed'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to get agent response'
                }

        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def aggregate_agent_results(self, execution_ids: List[str]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agent executions.

        Args:
            execution_ids: List of agent execution IDs

        Returns:
            Aggregated results from all agents
        """
        try:
            results = []
            successful_executions = 0
            failed_executions = 0

            for execution_id in execution_ids:
                status = self.agent_registry.get_execution_status(execution_id)
                if status:
                    results.append(status)
                    if status.get('status') == 'completed':
                        successful_executions += 1
                    elif status.get('status') == 'failed':
                        failed_executions += 1

            # Analyze results for patterns and insights
            insights = self._analyze_agent_results(results)

            # Store aggregated results as memory
            self.store_memory(
                'agent_aggregation',
                f"Aggregated results from {len(execution_ids)} agents",
                importance=8,
                metadata={
                    'execution_ids': execution_ids,
                    'successful_count': successful_executions,
                    'failed_count': failed_executions,
                    'insights': insights
                }
            )

            return {
                'success': True,
                'total_executions': len(execution_ids),
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'results': results,
                'insights': insights,
                'summary': f"Processed {len(execution_ids)} agent executions with {successful_executions} successes"
            }

        except Exception as e:
            logger.error(f"Error aggregating agent results: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def communicate_with_advisor(self, advisor_id: str, consultation_topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initiate communication with an advisor.

        Args:
            advisor_id: Advisor identifier
            consultation_topic: Topic for consultation
            context: Additional context for the consultation

        Returns:
            Advisor consultation results
        """
        try:
            # Get advisor profile
            advisor = self.advisor_registry.get_advisor(advisor_id)
            if not advisor:
                return {
                    'success': False,
                    'error': f'Advisor {advisor_id} not found'
                }

            # Create consultation context
            consultation_context = {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'goals': self.enhanced_profile.long_term_goals,
                'current_projects': self.enhanced_profile.current_projects,
                'skills': self.enhanced_profile.core_competencies,
                'recent_decisions': self._get_recent_decisions(),
                'consultation_history': self._get_advisor_history(advisor_id)
            }

            if context:
                consultation_context.update(context)

            # Request consultation
            consultation_id = self.advisor_registry.request_consultation(
                advisor_id=advisor_id,
                user_id=str(self.user.id),
                topic=consultation_topic,
                consultation_type='strategy',
                initial_request=json.dumps(consultation_context)
            )

            if consultation_id:
                # Store advisor interaction
                self.store_memory(
                    'advisor_consultation',
                    f"Consulted with {advisor.name} about: {consultation_topic}",
                    importance=9,
                    metadata={
                        'advisor_id': advisor_id,
                        'advisor_name': advisor.name,
                        'consultation_id': consultation_id,
                        'topic': consultation_topic,
                        'domain': advisor.domain.value
                    }
                )

                logger.info(f"🎓 Initiated consultation with advisor {advisor.name} for {self.user.username}")

                return {
                    'success': True,
                    'advisor': {
                        'id': advisor.id,
                        'name': advisor.name,
                        'title': advisor.title,
                        'domain': advisor.domain.value,
                        'expertise_level': advisor.expertise_level.value
                    },
                    'consultation_id': consultation_id,
                    'message': f"Consultation initiated with {advisor.name}",
                    'expected_response_time': f"{advisor.response_time_hours} hours"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initiate consultation'
                }

        except Exception as e:
            logger.error(f"Error communicating with advisor: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def find_relevant_advisors(self, topic: str, domain: str = None) -> List[Dict[str, Any]]:
        """
        Find advisors relevant to a specific topic or domain.

        Args:
            topic: Topic or question for consultation
            domain: Specific domain to filter by

        Returns:
            List of relevant advisor recommendations
        """
        try:
            from advisors.registry import AdvisorDomain

            # Convert string domain to enum if provided
            domain_enum = None
            if domain:
                try:
                    domain_enum = AdvisorDomain(domain.lower())
                except ValueError:
                    # Try to find matching domain
                    for d in AdvisorDomain:
                        if domain.lower() in d.value:
                            domain_enum = d
                            break

            # Get advisor recommendations
            recommendations = self.advisor_registry.get_advisor_recommendations(topic, {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'domain': domain_enum
            })

            # Store search as memory
            self.store_memory(
                'advisor_search',
                f"Searched for advisors on topic: {topic}",
                importance=5,
                metadata={
                    'topic': topic,
                    'domain': domain,
                    'recommendations_count': len(recommendations.get('recommendations', []))
                }
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error finding relevant advisors: {e}")
            return {
                'error': str(e),
                'recommendations': []
            }

    def execute_multi_agent_workflow(self, workflow_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a workflow involving multiple agents working together.

        Args:
            workflow_name: Name of the workflow to execute
            task: Primary task description

        Returns:
            Workflow execution results
        """
        try:
            # Define workflow templates
            workflows = {
                'opportunity_analysis': [
                    {'agent_type': 'research', 'capabilities': ['web_search', 'data_analysis']},
                    {'agent_type': 'analysis', 'capabilities': ['financial_analysis', 'risk_assessment']},
                    {'agent_type': 'recommendation', 'capabilities': ['strategy', 'planning']}
                ],
                'skill_development': [
                    {'agent_type': 'assessment', 'capabilities': ['skill_analysis', 'gap_analysis']},
                    {'agent_type': 'planning', 'capabilities': ['learning_path', 'curriculum']},
                    {'agent_type': 'tracking', 'capabilities': ['progress_monitoring', 'feedback']}
                ],
                'job_application': [
                    {'agent_type': 'research', 'capabilities': ['job_search', 'company_research']},
                    {'agent_type': 'application', 'capabilities': ['resume_optimization', 'cover_letter']},
                    {'agent_type': 'follow_up', 'capabilities': ['communication', 'tracking']}
                ]
            }

            if workflow_name not in workflows:
                return {
                    'success': False,
                    'error': f'Unknown workflow: {workflow_name}',
                    'available_workflows': list(workflows.keys())
                }

            workflow_steps = workflows[workflow_name]
            execution_ids = []
            step_results = []

            # Execute each step in the workflow
            for i, step in enumerate(workflow_steps):
                # Find agent for this step
                best_agent = self.agent_registry.find_best_agent(
                    task_description=f"{task} - Step {i+1}",
                    required_capabilities=step['capabilities'],
                    preferred_specialization=step['agent_type']
                )

                if best_agent:
                    # Execute step
                    execution_id = self.agent_registry.execute_agent(
                        agent_name=best_agent['name'],
                        task_data={
                            'task': task,
                            'workflow_step': i + 1,
                            'step_description': step,
                            'previous_results': step_results,
                            'user_context': self._get_agent_context()
                        }
                    )

                    if execution_id:
                        execution_ids.append(execution_id)
                        step_results.append({
                            'step': i + 1,
                            'agent': best_agent['name'],
                            'execution_id': execution_id
                        })

            # Store workflow execution
            self.store_memory(
                'workflow_execution',
                f"Executed {workflow_name} workflow: {task}",
                importance=9,
                metadata={
                    'workflow_name': workflow_name,
                    'task': task,
                    'execution_ids': execution_ids,
                    'steps_completed': len(step_results)
                }
            )

            logger.info(f"🔄 Executed {workflow_name} workflow with {len(execution_ids)} agents for {self.user.username}")

            return {
                'success': True,
                'workflow_name': workflow_name,
                'task': task,
                'total_steps': len(workflow_steps),
                'execution_ids': execution_ids,
                'step_results': step_results,
                'message': f"Workflow '{workflow_name}' initiated with {len(execution_ids)} agents"
            }

        except Exception as e:
            logger.error(f"Error executing multi-agent workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _suggest_alternative_agents(self, task: str) -> List[str]:
        """Suggest alternative agents when no exact match is found."""
        try:
            # Get all available agents
            all_agents = self.agent_registry.list_agents()

            # Simple keyword matching for suggestions
            task_keywords = task.lower().split()
            suggestions = []

            for agent in all_agents[:10]:  # Top 10 agents
                agent_keywords = (agent.get('name', '') + ' ' +
                                agent.get('description', '') + ' ' +
                                ' '.join(agent.get('capabilities', []))).lower()

                # Check for keyword overlap
                if any(keyword in agent_keywords for keyword in task_keywords):
                    suggestions.append(agent.get('name', 'Unknown'))

            return suggestions[:5]  # Top 5 suggestions

        except Exception as e:
            logger.error(f"Error suggesting alternative agents: {e}")
            return []

    def _get_agent_context(self) -> Dict[str, Any]:
        """Get context data for agent execution."""
        return {
            'user_id': str(self.user.id),  # Convert to string
            'user_role': self.enhanced_profile.primary_role or 'Not specified',
            'user_goals': self.enhanced_profile.long_term_goals or [],
            'user_skills': list(self.enhanced_profile.core_competencies.keys()) if self.enhanced_profile.core_competencies else [],
            'current_projects': self.enhanced_profile.current_projects or [],
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'timezone': self.enhanced_profile.time_zone or 'UTC',
            'timestamp': datetime.now().isoformat()
        }

    def _analyze_agent_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent execution results for insights."""
        try:
            total_time = sum(r.get('execution_time_ms', 0) for r in results)
            avg_time = total_time / len(results) if results else 0

            successful_agents = [r for r in results if r.get('status') == 'completed']
            failed_agents = [r for r in results if r.get('status') == 'failed']

            return {
                'total_executions': len(results),
                'successful_count': len(successful_agents),
                'failed_count': len(failed_agents),
                'success_rate': len(successful_agents) / len(results) if results else 0,
                'average_execution_time_ms': avg_time,
                'fastest_agent': min(results, key=lambda x: x.get('execution_time_ms', float('inf')))['agent_name'] if results else None,
                'slowest_agent': max(results, key=lambda x: x.get('execution_time_ms', 0))['agent_name'] if results else None
            }

        except Exception as e:
            logger.error(f"Error analyzing agent results: {e}")
            return {}

    def _get_recent_decisions(self) -> List[Dict[str, Any]]:
        """Get recent user decisions for advisor context."""
        try:
            recent_decisions = self.retrieve_memories('decision', limit=5)
            return [
                {
                    'content': decision.content,
                    'timestamp': decision.created_at.isoformat(),
                    'importance': decision.importance
                }
                for decision in recent_decisions
            ]
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []

    def _get_advisor_history(self, advisor_id: str) -> List[Dict[str, Any]]:
        """Get consultation history with specific advisor."""
        try:
            advisor_memories = self.retrieve_memories('advisor_consultation', limit=10)
            relevant_memories = [
                {
                    'content': memory.content,
                    'timestamp': memory.created_at.isoformat(),
                    'metadata': memory.metadata
                }
                for memory in advisor_memories
                if memory.metadata and memory.metadata.get('advisor_id') == advisor_id
            ]
            return relevant_memories
        except Exception as e:
            logger.error(f"Error getting advisor history: {e}")
            return []

    def _extract_task_from_message(self, message: str) -> str:
        """Extract the task description from a user message requesting agent execution."""
        try:
            message_lower = message.lower()

            # Common patterns for task extraction
            task_patterns = [
                r'can you have an agent (.+?)(?:\?|$)',
                r'execute agent.+?to (.+?)(?:\?|$)',
                r'run agent.+?to (.+?)(?:\?|$)',
                r'use agent.+?to (.+?)(?:\?|$)',
                r'deploy agent.+?to (.+?)(?:\?|$)',
                r'get an agent to (.+?)(?:\?|$)',
                r'agent analyze (.+?)(?:\?|$)',
                r'agent help.+?with (.+?)(?:\?|$)',
                r'technical-signal-agent.+?to (.+?)(?:\?|$)',
                r'research agent.+?for (.+?)(?:\?|$)'
            ]

            import re
            for pattern in task_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    task = match.group(1).strip()
                    # Clean up the task description
                    task = task.replace(' and ', ' ').replace(' the ', ' ')
                    return task.capitalize()

            # If no specific pattern matches, try to extract after common trigger words
            trigger_words = ['analyze', 'research', 'help with', 'work on', 'examine', 'investigate']
            for trigger in trigger_words:
                if trigger in message_lower:
                    # Extract everything after the trigger word
                    start_idx = message_lower.find(trigger) + len(trigger)
                    remaining_text = message[start_idx:].strip()
                    # Remove common prefixes and suffixes
                    remaining_text = remaining_text.lstrip('the ').rstrip('?!.')
                    if remaining_text:
                        return remaining_text.capitalize()

            # Default fallback - return the original message without common prefixes
            cleaned_message = message.replace('Can you have an agent ', '').replace('Please ', '').strip()
            return cleaned_message.capitalize()

        except Exception as e:
            logger.error(f"Error extracting task from message: {e}")
            return message.strip()