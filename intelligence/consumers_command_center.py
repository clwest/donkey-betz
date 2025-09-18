"""
WebSocket Consumer for Unified Command Center
Real-time command processing and state synchronization
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

from persistence.models import UnifiedUser, UserMemoryContext
from agents.models import Agent
from core.unified_memory_manager import UnifiedMemoryManager
from backend.agents.orchestrator import AgentOrchestrator
from intelligence.income_builder import AIIncomeBuilder
from content.ai_providers import MultiAIProvider

logger = logging.getLogger(__name__)


class CommandCenterConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time command center operations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.user_id = None
        self.room_group_name = None
        self.memory_manager = None
        self.agent_orchestrator = None
        self.income_builder = None
        self.ai_provider = None

    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Get user from scope
            self.user = self.scope.get('user')
            if not self.user or not self.user.is_authenticated:
                await self.close()
                return

            self.user_id = self.user.id
            self.room_group_name = f'command_center_{self.user_id}'

            # Initialize managers
            self.memory_manager = UnifiedMemoryManager()
            self.agent_orchestrator = AgentOrchestrator()
            self.income_builder = AIIncomeBuilder()
            self.ai_provider = MultiAIProvider()

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Send initial connection success
            await self.send(json.dumps({
                'type': 'CONNECTION_SUCCESS',
                'message': 'Command Center connected',
                'user_id': self.user_id,
                'timestamp': datetime.now().isoformat()
            }))

            # Load and send initial state
            await self.send_initial_state()

            logger.info(f"Command Center WebSocket connected for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            if self.room_group_name:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

            logger.info(f"Command Center WebSocket disconnected for user {self.user_id}")

        except Exception as e:
            logger.error(f"Error in WebSocket disconnection: {str(e)}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            command_type = data.get('type')
            payload = data.get('payload', {})

            logger.info(f"Received command: {command_type} from user {self.user_id}")

            # Route commands to handlers
            handlers = {
                'PROFILE_UPDATE': self.handle_profile_update,
                'AI_CONFIG': self.handle_ai_config,
                'AGENT_CONTROL': self.handle_agent_control,
                'OPPORTUNITY_ACTION': self.handle_opportunity_action,
                'EXECUTE_COMMAND': self.handle_execute_command,
                'GET_STATE': self.send_initial_state,
                'REFRESH_AGENTS': self.handle_refresh_agents,
                'ANALYZE_PROFILE': self.handle_analyze_profile,
            }

            handler = handlers.get(command_type)
            if handler:
                await handler(payload)
            else:
                await self.send_error(f"Unknown command type: {command_type}")

        except json.JSONDecodeError as e:
            await self.send_error(f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send_error(f"Error processing command: {str(e)}")

    async def handle_profile_update(self, payload: Dict[str, Any]):
        """Handle profile update commands"""
        try:
            # Update user profile in database
            user = await self.get_user()

            # Update fields
            if 'skills' in payload:
                user.skills = payload['skills']
            if 'experienceYears' in payload:
                user.experience_years = payload['experienceYears']
            if 'currentRole' in payload:
                user.current_role = payload['currentRole']
            if 'industries' in payload:
                user.industries = payload['industries']
            if 'jobPreferences' in payload:
                prefs = payload['jobPreferences']
                user.prefer_remote = prefs.get('remote', True)
                user.prefer_contract = prefs.get('contract', True)
                user.prefer_full_time = prefs.get('fullTime', False)
                user.hourly_rate_min = prefs.get('hourlyRateMin', 100)
                user.salary_min = prefs.get('salaryMin', 120000)

            await database_sync_to_async(user.save)()

            # Store in memory
            await self.store_memory(
                memory_type='profile_update',
                content=f"Profile updated: {json.dumps(payload)}",
                metadata={'changes': payload}
            )

            # Notify all agents of profile change
            await self.notify_agents_profile_change(payload)

            # Send success response
            await self.send(json.dumps({
                'type': 'PROFILE_UPDATED',
                'payload': payload,
                'message': 'Profile updated successfully',
                'timestamp': datetime.now().isoformat()
            }))

            # Trigger opportunity refresh
            await self.trigger_opportunity_refresh()

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            await self.send_error(f"Failed to update profile: {str(e)}")

    async def handle_ai_config(self, payload: Dict[str, Any]):
        """Handle AI configuration updates"""
        try:
            user = await self.get_user()

            # Update AI settings
            if 'defaultModel' in payload:
                user.default_model = payload['defaultModel']
            if 'reasoningLevel' in payload:
                user.reasoning_level = payload['reasoningLevel']
            if 'automationLevel' in payload:
                user.automation_level = payload['automationLevel']
            if 'dailyTokenLimit' in payload:
                user.daily_token_limit = payload['dailyTokenLimit']
            if 'monthlySpendingLimit' in payload:
                user.monthly_spending_limit = payload['monthlySpendingLimit']

            await database_sync_to_async(user.save)()

            # Update agent configurations
            await self.update_agent_configs(payload)

            # Send success response
            await self.send(json.dumps({
                'type': 'AI_CONFIG_UPDATED',
                'payload': payload,
                'message': 'AI configuration updated',
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error updating AI config: {str(e)}")
            await self.send_error(f"Failed to update AI configuration: {str(e)}")

    async def handle_agent_control(self, payload: Dict[str, Any]):
        """Handle agent control commands (start, stop, configure)"""
        try:
            agent_id = payload.get('agent_id')
            action = payload.get('action')
            params = payload.get('params', {})

            if not agent_id or not action:
                await self.send_error("Agent ID and action required")
                return

            result = None

            if action == 'start':
                result = await self.start_agent(agent_id, params)
            elif action == 'stop':
                result = await self.stop_agent(agent_id)
            elif action == 'configure':
                result = await self.configure_agent(agent_id, params)
            else:
                await self.send_error(f"Unknown agent action: {action}")
                return

            # Send response
            await self.send(json.dumps({
                'type': 'AGENT_STATUS',
                'payload': {
                    'agent_id': agent_id,
                    'action': action,
                    'result': result,
                    'status': 'success'
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error controlling agent: {str(e)}")
            await self.send_error(f"Failed to control agent: {str(e)}")

    async def handle_opportunity_action(self, payload: Dict[str, Any]):
        """Handle opportunity-related actions (save, apply, dismiss)"""
        try:
            opportunity_id = payload.get('opportunity_id')
            action = payload.get('action')
            user_context = payload.get('user_context', {})

            if not opportunity_id or not action:
                await self.send_error("Opportunity ID and action required")
                return

            result = None

            if action == 'save':
                result = await self.save_opportunity(opportunity_id, user_context)
            elif action == 'apply':
                result = await self.apply_to_opportunity(opportunity_id, user_context)
            elif action == 'quick_apply':
                result = await self.quick_apply(opportunity_id, user_context)
            elif action == 'dismiss':
                result = await self.dismiss_opportunity(opportunity_id)
            else:
                await self.send_error(f"Unknown opportunity action: {action}")
                return

            # Store action in memory
            await self.store_memory(
                memory_type='opportunity_action',
                content=f"User {action} opportunity {opportunity_id}",
                metadata={
                    'opportunity_id': opportunity_id,
                    'action': action,
                    'result': result
                }
            )

            # Send response
            await self.send(json.dumps({
                'type': 'OPPORTUNITY_ACTION_COMPLETE',
                'payload': {
                    'opportunity_id': opportunity_id,
                    'action': action,
                    'result': result
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error handling opportunity action: {str(e)}")
            await self.send_error(f"Failed to {action} opportunity: {str(e)}")

    async def handle_execute_command(self, payload: Dict[str, Any]):
        """Execute natural language commands"""
        try:
            command_text = payload.get('command', '')
            context = payload.get('context', {})

            if not command_text:
                await self.send_error("Command text required")
                return

            # Process command with AI
            result = await self.process_ai_command(command_text, context)

            # Store command execution
            await self.store_memory(
                memory_type='command_execution',
                content=command_text,
                metadata={
                    'result': result,
                    'context': context
                }
            )

            # Send response
            await self.send(json.dumps({
                'type': 'COMMAND_RESULT',
                'payload': {
                    'command': command_text,
                    'result': result,
                    'success': result.get('success', False)
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            await self.send_error(f"Failed to execute command: {str(e)}")

    async def handle_analyze_profile(self, payload: Dict[str, Any]):
        """Analyze user profile and provide recommendations"""
        try:
            user = await self.get_user()

            # Perform profile analysis
            analysis = {
                'completeness': await self.calculate_profile_completion(user),
                'missing_fields': await self.get_missing_fields(user),
                'recommendations': await self.get_recommendations(user),
                'strengths': await self.analyze_strengths(user),
                'suggested_agents': await self.suggest_agents(user)
            }

            # Send analysis results
            await self.send(json.dumps({
                'type': 'PROFILE_ANALYSIS',
                'payload': analysis,
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error analyzing profile: {str(e)}")
            await self.send_error(f"Failed to analyze profile: {str(e)}")

    async def handle_refresh_agents(self, payload: Dict[str, Any]):
        """Refresh agent status and information"""
        try:
            user = await self.get_user()
            assigned_agents = getattr(user, 'assigned_agents', [])

            # Get agent details
            agents_data = []
            for agent_name in assigned_agents:
                agent = await self.get_agent_info(agent_name)
                if agent:
                    agents_data.append(agent)

            # Send updated agent list
            await self.send(json.dumps({
                'type': 'AGENTS_REFRESHED',
                'payload': {
                    'agents': agents_data,
                    'total': len(agents_data)
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error refreshing agents: {str(e)}")
            await self.send_error(f"Failed to refresh agents: {str(e)}")

    # Helper methods

    async def send_initial_state(self):
        """Send initial state data to client"""
        try:
            user = await self.get_user()

            # Gather initial state
            profile_data = await self.get_profile_data(user)
            ai_config = await self.get_ai_config(user)
            agents = await self.get_assigned_agents(user)
            recent_memories = await self.get_recent_memories(user)

            # Send state
            await self.send(json.dumps({
                'type': 'INITIAL_STATE',
                'payload': {
                    'profile': profile_data,
                    'aiConfig': ai_config,
                    'agents': agents,
                    'recentActivities': recent_memories
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending initial state: {str(e)}")

    async def notify_agents_profile_change(self, changes: Dict):
        """Notify all assigned agents of profile changes"""
        try:
            user = await self.get_user()
            assigned_agents = getattr(user, 'assigned_agents', [])

            for agent_name in assigned_agents:
                # Send notification to agent
                await self.channel_layer.group_send(
                    f'agent_{agent_name}',
                    {
                        'type': 'profile_update',
                        'user_id': self.user_id,
                        'changes': changes
                    }
                )

            logger.info(f"Notified {len(assigned_agents)} agents of profile changes")

        except Exception as e:
            logger.error(f"Error notifying agents: {str(e)}")

    async def trigger_opportunity_refresh(self):
        """Trigger opportunity refresh based on updated profile"""
        try:
            user = await self.get_user()

            # Use Income Builder to find new opportunities
            opportunities = await sync_to_async(self.income_builder.analyze_opportunities)(
                user_skills=getattr(user, 'skills', []),
                min_rate=getattr(user, 'hourly_rate_min', 100),
                remote_only=getattr(user, 'prefer_remote', True)
            )

            # Send new opportunities
            await self.send(json.dumps({
                'type': 'OPPORTUNITIES_REFRESHED',
                'payload': {
                    'opportunities': opportunities[:5],  # Top 5
                    'total': len(opportunities)
                },
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error refreshing opportunities: {str(e)}")

    async def process_ai_command(self, command: str, context: Dict) -> Dict:
        """Process natural language command with AI"""
        try:
            user = await self.get_user()

            # Build prompt with context
            prompt = f"""
            Process this command from user {user.username}:

            Command: {command}

            User Context:
            - Skills: {getattr(user, 'skills', [])}
            - Experience: {getattr(user, 'experience_years', 0)} years
            - Looking for: Remote={getattr(user, 'prefer_remote', True)},
                          Min Rate=${getattr(user, 'hourly_rate_min', 100)}/hr

            Additional Context: {json.dumps(context)}

            Provide a helpful, actionable response.
            """

            # Get AI response
            response = await sync_to_async(self.ai_provider.chat_completion)(
                model=getattr(user, 'default_model', 'gpt-5-mini'),
                messages=[{'role': 'user', 'content': prompt}]
            )

            return {
                'success': True,
                'response': response.get('content', ''),
                'tokens_used': response.get('usage', {}).get('total_tokens', 0)
            }

        except Exception as e:
            logger.error(f"Error in AI command processing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send(json.dumps({
            'type': 'ERROR',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }))

    # Database helper methods

    @database_sync_to_async
    def get_user(self):
        """Get user from database"""
        return UnifiedUser.objects.get(id=self.user_id)

    @database_sync_to_async
    def get_profile_data(self, user):
        """Get user profile data"""
        return {
            'username': user.username,
            'email': user.email,
            'skills': getattr(user, 'skills', []),
            'experienceYears': getattr(user, 'experience_years', 0),
            'currentRole': getattr(user, 'current_role', ''),
            'industries': getattr(user, 'industries', []),
            'completionPercentage': self.calculate_completion_sync(user)
        }

    @database_sync_to_async
    def get_ai_config(self, user):
        """Get user AI configuration"""
        return {
            'defaultModel': getattr(user, 'default_model', 'gpt-5-mini'),
            'reasoningLevel': getattr(user, 'reasoning_level', 'medium'),
            'automationLevel': getattr(user, 'automation_level', 'semi-auto'),
            'dailyTokenLimit': getattr(user, 'daily_token_limit', 100000),
            'monthlySpendingLimit': float(getattr(user, 'monthly_spending_limit', 50.00))
        }

    @database_sync_to_async
    def get_assigned_agents(self, user):
        """Get user's assigned agents"""
        assigned_names = getattr(user, 'assigned_agents', ['income_builder', 'career_advisor'])
        agents = Agent.objects.filter(name__in=assigned_names)

        return [{
            'agentName': agent.name,
            'agentType': agent.category,
            'tasksCompleted': getattr(agent, 'tasks_completed', 0),
            'successRate': getattr(agent, 'success_rate', 0.85)
        } for agent in agents]

    @database_sync_to_async
    def get_recent_memories(self, user):
        """Get recent user memories/activities"""
        memories = UserMemoryContext.objects.filter(
            user=user
        ).order_by('-created_at')[:10]

        return [{
            'type': m.memory_type,
            'content': m.content[:100],
            'timestamp': m.created_at.isoformat()
        } for m in memories]

    @database_sync_to_async
    def store_memory(self, memory_type: str, content: str, metadata: Dict = None):
        """Store memory in database"""
        user = UnifiedUser.objects.get(id=self.user_id)
        return UserMemoryContext.objects.create(
            user=user,
            source='command_center',
            memory_type=memory_type,
            content=content,
            metadata=metadata or {}
        )

    def calculate_completion_sync(self, user) -> int:
        """Calculate profile completion percentage (sync version)"""
        fields = [
            bool(getattr(user, 'skills', [])),
            bool(getattr(user, 'experience_years', 0)),
            bool(getattr(user, 'current_role', '')),
            bool(getattr(user, 'industries', [])),
            bool(getattr(user, 'resume_id', None))
        ]
        return int((sum(fields) / len(fields)) * 100)

    # Stub methods for opportunity actions
    async def save_opportunity(self, opp_id: str, context: Dict) -> Dict:
        """Save opportunity for later"""
        # Implementation would save to database
        return {'saved': True, 'opportunity_id': opp_id}

    async def apply_to_opportunity(self, opp_id: str, context: Dict) -> Dict:
        """Apply to opportunity"""
        # Implementation would submit application
        return {'applied': True, 'opportunity_id': opp_id}

    async def quick_apply(self, opp_id: str, context: Dict) -> Dict:
        """Quick apply with saved resume"""
        # Implementation would use stored resume
        return {'quick_applied': True, 'opportunity_id': opp_id}

    async def dismiss_opportunity(self, opp_id: str) -> Dict:
        """Dismiss opportunity"""
        # Implementation would mark as dismissed
        return {'dismissed': True, 'opportunity_id': opp_id}