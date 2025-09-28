"""
Personal AI Orchestrator
========================

The intelligent layer that connects user profile, preferences, and agents
to provide truly personalized AI assistance.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.cache import cache
from channels.db import database_sync_to_async
from core.models import UserProfile, UserPreferences, ConversationMemory
from agents.registry import agent_registry
from intelligence.income_builder import enhanced_income_builder
from ai_core.intelligence.monetization_engine import monetization_engine

logger = logging.getLogger(__name__)
User = get_user_model()


class PersonalAIOrchestrator:
    """
    Central orchestration layer that:
    1. Accesses user context from profile & preferences
    2. Selects appropriate agents based on user needs
    3. Maintains conversation memory
    4. Coordinates multi-agent workflows
    5. Personalizes all responses based on user data
    """

    def __init__(self):
        self.agent_registry = agent_registry
        self.income_builder = enhanced_income_builder
        self.monetization_engine = monetization_engine
        self.active_orchestrations = {}

    async def process_user_request(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user requests with full personalization
        """
        logger.info(f"Processing request for user {user_id}: {message[:100]}...")

        # 1. Load user context
        user_context = await self.load_user_context(user_id)

        # 2. Retrieve conversation memory
        memory = await self.get_conversation_memory(user_id)

        # 3. Analyze intent and required capabilities
        intent_analysis = await self.analyze_intent(message, user_context, memory)

        # 4. Select and orchestrate agents
        selected_agents = await self.select_agents(intent_analysis, user_context)

        # 5. Execute orchestrated workflow
        result = await self.execute_orchestration(
            user_id=user_id,
            message=message,
            agents=selected_agents,
            context={
                **user_context,
                'memory': memory,
                'intent': intent_analysis,
                **(context or {})
            }
        )

        # 6. Store in conversation memory
        await self.store_conversation_memory(user_id, message, result)

        return result

    @database_sync_to_async
    def load_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Load comprehensive user context from profile and preferences
        """
        try:
            user = User.objects.get(id=user_id)

            # Get user profile
            profile, _ = UserProfile.objects.get_or_create(user=user)

            # Get AI preferences
            preferences, _ = UserPreferences.objects.get_or_create(user=user)

            # Build comprehensive context
            context = {
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username
                },
                'profile': {
                    'skills': profile.skills or [],
                    'experience_years': profile.experience_years,
                    'current_role': profile.current_role,
                    'industries': profile.industries or [],
                    'bio': profile.bio,
                    'location': profile.location,
                    'job_preferences': {
                        'remote_only': profile.remote_only,
                        'contract_work': profile.contract_work,
                        'full_time': profile.full_time,
                        'hourly_rate_min': profile.hourly_rate_min,
                        'salary_min': profile.salary_min,
                    },
                    'urls': {
                        'portfolio': profile.portfolio_url,
                        'linkedin': profile.linkedin_url,
                        'github': profile.github_url,
                    }
                },
                'ai_config': {
                    'default_model': preferences.default_model,
                    'reasoning_level': preferences.reasoning_level,
                    'automation_level': preferences.automation_level,
                    'daily_token_limit': preferences.daily_token_limit,
                    'share_memory': preferences.share_memory_across_agents,
                    'assigned_agents': preferences.assigned_agents or []
                },
                'metadata': {
                    'profile_completion': self.calculate_profile_completion(profile),
                    'account_type': profile.account_type,
                    'credits_remaining': profile.credits_remaining,
                    'last_active': profile.last_active.isoformat() if profile.last_active else None
                }
            }

            logger.info(f"Loaded context for user {user.username} with {len(context['profile']['skills'])} skills")
            return context

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {}
        except Exception as e:
            logger.error(f"Error loading user context: {e}")
            return {}

    async def get_conversation_memory(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent conversation memory for context
        """
        cache_key = f"conversation_memory:{user_id}"
        memory = cache.get(cache_key)

        if memory is None:
            memory = await self._load_memory_from_db(user_id, limit)
            cache.set(cache_key, memory, timeout=3600)  # Cache for 1 hour

        return memory

    @database_sync_to_async
    def _load_memory_from_db(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Load conversation memory from database
        """
        try:
            memories = ConversationMemory.objects.filter(
                user_id=user_id
            ).order_by('-created_at')[:limit]

            return [
                {
                    'message': m.message,
                    'response': m.response,
                    'agents_used': m.agents_used,
                    'timestamp': m.created_at.isoformat()
                }
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
            return []

    async def analyze_intent(self, message: str, user_context: Dict, memory: List) -> Dict[str, Any]:
        """
        Analyze user intent based on message, context, and history
        """
        # Keywords for different intents
        income_keywords = ['job', 'work', 'money', 'income', 'earn', 'salary', 'freelance', 'gig']
        content_keywords = ['write', 'create', 'post', 'blog', 'article', 'content', 'copy']
        learning_keywords = ['learn', 'study', 'course', 'tutorial', 'teach', 'skill']
        analysis_keywords = ['analyze', 'research', 'data', 'insights', 'trends']

        message_lower = message.lower()

        # Check for specific intents
        intents = []
        if any(keyword in message_lower for keyword in income_keywords):
            intents.append('income_generation')
        if any(keyword in message_lower for keyword in content_keywords):
            intents.append('content_creation')
        if any(keyword in message_lower for keyword in learning_keywords):
            intents.append('skill_development')
        if any(keyword in message_lower for keyword in analysis_keywords):
            intents.append('data_analysis')

        # Check user's current context for additional signals
        if user_context.get('profile', {}).get('current_role'):
            if 'developer' in user_context['profile']['current_role'].lower():
                intents.append('technical_assistance')

        # Default to general assistance if no specific intent
        if not intents:
            intents.append('general_assistance')

        return {
            'primary_intent': intents[0] if intents else 'general_assistance',
            'all_intents': intents,
            'confidence': 0.8 if intents else 0.5,
            'requires_agents': len(intents) > 1,
            'user_skills': user_context.get('profile', {}).get('skills', []),
            'automation_level': user_context.get('ai_config', {}).get('automation_level', 'semi-auto')
        }

    async def select_agents(self, intent_analysis: Dict, user_context: Dict) -> List[Dict[str, Any]]:
        """
        Select appropriate agents based on intent and user preferences
        """
        selected_agents = []

        # Get user's assigned agents
        assigned_agents = user_context.get('ai_config', {}).get('assigned_agents', [])

        # Map intents to agent types
        intent_agent_map = {
            'income_generation': ['income_builder', 'job_finder', 'proposal_writer'],
            'content_creation': ['content_creator', 'seo_optimizer', 'social_media_manager'],
            'skill_development': ['learning_assistant', 'course_finder', 'practice_generator'],
            'data_analysis': ['data_analyst', 'trend_spotter', 'report_generator'],
            'technical_assistance': ['code_assistant', 'debugger', 'documentation_writer'],
            'general_assistance': ['personal_assistant', 'task_manager', 'scheduler']
        }

        # Select agents based on intent
        for intent in intent_analysis['all_intents']:
            agent_types = intent_agent_map.get(intent, [])
            for agent_type in agent_types:
                # Check if user has this agent assigned or if it's auto-selected
                if self._should_use_agent(agent_type, assigned_agents, intent_analysis):
                    agent = self.agent_registry.get_agent(agent_type)
                    if agent:
                        selected_agents.append({
                            'type': agent_type,
                            'agent': agent,
                            'priority': 'high' if intent == intent_analysis['primary_intent'] else 'medium'
                        })

        # Always include personal assistant for coordination
        if not any(a['type'] == 'personal_assistant' for a in selected_agents):
            personal_assistant = self.agent_registry.get_agent('personal_assistant')
            if personal_assistant:
                selected_agents.insert(0, {
                    'type': 'personal_assistant',
                    'agent': personal_assistant,
                    'priority': 'high'
                })

        logger.info(f"Selected {len(selected_agents)} agents for intents: {intent_analysis['all_intents']}")
        return selected_agents

    def _should_use_agent(self, agent_type: str, assigned_agents: List, intent_analysis: Dict) -> bool:
        """
        Determine if an agent should be used based on assignment and automation level
        """
        # Check if explicitly assigned
        for assigned in assigned_agents:
            if assigned.get('agentName', '').lower().replace(' ', '_') == agent_type:
                return assigned.get('canExecuteActions', True)

        # Auto-select based on automation level
        automation_level = intent_analysis.get('automation_level', 'semi-auto')
        if automation_level == 'auto':
            return True  # Auto mode uses all relevant agents
        elif automation_level == 'semi-auto':
            return agent_type in ['personal_assistant', 'income_builder']  # Semi uses core agents
        else:
            return False  # Manual mode only uses explicitly assigned

    async def execute_orchestration(self, user_id: str, message: str, agents: List[Dict], context: Dict) -> Dict[str, Any]:
        """
        Execute multi-agent orchestration with coordination
        """
        orchestration_id = f"orch_{user_id}_{datetime.now().timestamp()}"
        self.active_orchestrations[orchestration_id] = {
            'status': 'running',
            'agents': agents,
            'results': []
        }

        try:
            # Execute agents based on priority
            high_priority = [a for a in agents if a['priority'] == 'high']
            medium_priority = [a for a in agents if a['priority'] == 'medium']

            results = []

            # Execute high priority agents first
            for agent_info in high_priority:
                result = await self._execute_single_agent(
                    agent_info['agent'],
                    message,
                    context
                )
                results.append({
                    'agent': agent_info['type'],
                    'result': result
                })

            # Then medium priority if needed
            if medium_priority and context.get('intent', {}).get('requires_agents'):
                for agent_info in medium_priority:
                    result = await self._execute_single_agent(
                        agent_info['agent'],
                        message,
                        context
                    )
                    results.append({
                        'agent': agent_info['type'],
                        'result': result
                    })

            # Synthesize results
            synthesized = await self._synthesize_results(results, context)

            self.active_orchestrations[orchestration_id]['status'] = 'completed'
            self.active_orchestrations[orchestration_id]['results'] = results

            return {
                'success': True,
                'orchestration_id': orchestration_id,
                'agents_used': [a['type'] for a in agents],
                'response': synthesized['response'],
                'data': synthesized.get('data', {}),
                'actions': synthesized.get('actions', []),
                'metadata': {
                    'intent': context.get('intent', {}).get('primary_intent'),
                    'user_skills': context.get('profile', {}).get('skills', []),
                    'personalized': True
                }
            }

        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            self.active_orchestrations[orchestration_id]['status'] = 'failed'
            return {
                'success': False,
                'error': str(e),
                'orchestration_id': orchestration_id
            }

    async def _execute_single_agent(self, agent, message: str, context: Dict) -> Dict[str, Any]:
        """
        Execute a single agent with context
        """
        try:
            # Add user context to agent execution
            agent_context = {
                'user_profile': context.get('profile', {}),
                'user_preferences': context.get('ai_config', {}),
                'conversation_memory': context.get('memory', []),
                'intent': context.get('intent', {})
            }

            # Execute agent
            result = await agent.execute(message, agent_context)
            return result

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {'error': str(e)}

    async def _synthesize_results(self, results: List[Dict], context: Dict) -> Dict[str, Any]:
        """
        Synthesize results from multiple agents into coherent response
        """
        # Collect all responses
        responses = []
        all_data = {}
        all_actions = []

        for result in results:
            if result['result'].get('response'):
                responses.append(result['result']['response'])
            if result['result'].get('data'):
                all_data[result['agent']] = result['result']['data']
            if result['result'].get('actions'):
                all_actions.extend(result['result']['actions'])

        # Create personalized synthesis
        user_name = context.get('user', {}).get('name', 'there')
        primary_intent = context.get('intent', {}).get('primary_intent', 'assistance')

        if primary_intent == 'income_generation':
            synthesized_response = f"Hi {user_name}! Based on your {context.get('profile', {}).get('experience_years', 0)} years of experience and skills in {', '.join(context.get('profile', {}).get('skills', [])[:3])}, I've found opportunities that match your profile. "
        else:
            synthesized_response = f"Hi {user_name}! "

        # Add agent responses
        if responses:
            synthesized_response += " ".join(responses[:2])  # Limit to avoid too long response

        return {
            'response': synthesized_response,
            'data': all_data,
            'actions': all_actions
        }

    @database_sync_to_async
    def store_conversation_memory(self, user_id: str, message: str, result: Dict):
        """
        Store conversation in memory for future personalization
        """
        try:
            user = User.objects.get(id=user_id)
            ConversationMemory.objects.create(
                user=user,
                message=message,
                response=result.get('response', ''),
                agents_used=result.get('agents_used', []),
                intent=result.get('metadata', {}).get('intent', ''),
                success=result.get('success', False)
            )

            # Invalidate cache
            cache_key = f"conversation_memory:{user_id}"
            cache.delete(cache_key)

        except Exception as e:
            logger.error(f"Error storing memory: {e}")

    def calculate_profile_completion(self, profile) -> int:
        """
        Calculate profile completion percentage
        """
        fields = [
            bool(profile.skills),
            profile.experience_years > 0,
            bool(profile.current_role),
            bool(profile.industries),
            bool(profile.bio),
            bool(profile.portfolio_url or profile.linkedin_url or profile.github_url)
        ]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)


# Global orchestrator instance
personal_ai_orchestrator = PersonalAIOrchestrator()