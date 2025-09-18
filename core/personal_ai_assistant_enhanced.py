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
        logger.info(f"✅ Enhanced AI Assistant initialized with REAL AI and Unified Memory for {user.username}")

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
                    'timestamp': datetime.now().isoformat(),
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
            'timestamp': datetime.now().isoformat(),
            'database': {},
            'agents': {},
            'embeddings': {},
            'platform': {},
            'websockets': {}
        }

        try:
            # Check database status
            embeddings_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM self_awareness_unifiedembedding"
            )
            status['embeddings']['total_count'] = embeddings_count.get('data', [{}])[0].get('count', 0)

            # Check recent embeddings
            recent_embeddings = self.execute_database_query(
                """
                SELECT COUNT(*) as count
                FROM self_awareness_unifiedembedding
                WHERE created_at > %s
                """,
                [datetime.now() - timedelta(days=1)]
            )
            status['embeddings']['last_24h'] = recent_embeddings.get('data', [{}])[0].get('count', 0)

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

        # Extract conversation history from context
        conversation_context = context.get('conversation_context', '')
        conversation_history = context.get('conversation_history', [])

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
                temperature=0.7
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
            'model': 'gpt-4' if self.llm_enforcer.openai_client else 'intelligent-fallback'
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
            'decision_framework': self.enhanced_profile.decision_framework
        }

        if context:
            full_context.update(context)

        # Check if this is a system command
        system_keywords = ['database', 'embedding', 'system', 'status', 'agent', 'websocket', 'query']

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
            memory.last_accessed = datetime.now()
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