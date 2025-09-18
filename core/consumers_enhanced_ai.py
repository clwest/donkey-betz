"""
Enhanced AI Assistant WebSocket Consumer with Full Personalization
"""

import json
import logging
import asyncio
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from datetime import datetime

from core.personal_ai_orchestrator import personal_ai_orchestrator
from core.models import UserProfile, UserPreferences

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedAIAssistantConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for the enhanced AI Assistant with full personalization
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'ai_assistant'
        self.room_group_name = f'assistant_{self.room_name}'
        self.user = None
        self.user_context = None

        # Check if user is authenticated
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"Enhanced AI WebSocket connected: {self.channel_name} for user {self.user.username}")

            # Load user context immediately
            self.user_context = await personal_ai_orchestrator.load_user_context(str(self.user.id))

            # Send initial greeting with personalization
            await self.send_personalized_greeting()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Enhanced AI WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')

            if message_type == 'message':
                await self.handle_message(data.get('message'))
            elif message_type == 'update_context':
                await self.update_user_context()
            elif message_type == 'get_suggestions':
                await self.send_personalized_suggestions()
            elif message_type == 'execute_action':
                await self.execute_action(data.get('action'))
            elif message_type == 'get_agents':
                await self.send_available_agents()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_message(self, message: str):
        """Process user message with full orchestration"""
        if not message:
            return

        # Send typing indicator
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'status': True
        }))

        try:
            # Process with orchestrator
            result = await personal_ai_orchestrator.process_user_request(
                user_id=str(self.user.id),
                message=message,
                context={
                    'channel_name': self.channel_name,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Send orchestrated response
            await self.send(text_data=json.dumps({
                'type': 'response',
                'message': result['response'],
                'agents_used': result.get('agents_used', []),
                'data': result.get('data', {}),
                'actions': result.get('actions', []),
                'metadata': result.get('metadata', {}),
                'success': result.get('success', True)
            }))

            # Send any follow-up actions
            if result.get('actions'):
                await self.send_action_suggestions(result['actions'])

        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f"I encountered an error: {str(e)}"
            }))

        finally:
            # Stop typing indicator
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'status': False
            }))

    async def send_personalized_greeting(self):
        """Send personalized greeting based on user context"""
        if not self.user_context:
            greeting = "Hello! I'm your AI Assistant. How can I help you today?"
        else:
            user_name = self.user_context['user'].get('name', 'there')
            skills = self.user_context['profile'].get('skills', [])
            role = self.user_context['profile'].get('current_role', '')
            completion = self.user_context['metadata'].get('profile_completion', 0)

            if completion < 50:
                greeting = f"Hi {user_name}! I'm your AI Assistant. I notice your profile is {completion}% complete. Would you like to tell me more about yourself so I can provide better personalized assistance?"
            elif skills:
                greeting = f"Welcome back {user_name}! With your skills in {', '.join(skills[:2])}, I'm ready to help you find opportunities, create content, or assist with your projects. What would you like to work on today?"
            elif role:
                greeting = f"Hi {user_name}! As a {role}, I can help you with industry-specific opportunities and tasks. What can I assist you with?"
            else:
                greeting = f"Hello {user_name}! I'm your personalized AI Assistant. How can I help you today?"

        await self.send(text_data=json.dumps({
            'type': 'greeting',
            'message': greeting,
            'user_context': {
                'profile_completion': self.user_context['metadata'].get('profile_completion', 0),
                'skills_count': len(self.user_context['profile'].get('skills', [])),
                'has_interview': self.user_context['metadata'].get('profile_completion', 0) > 70
            }
        }))

    async def send_personalized_suggestions(self):
        """Send personalized action suggestions based on user profile"""
        suggestions = []

        if self.user_context:
            profile = self.user_context['profile']
            ai_config = self.user_context['ai_config']

            # Skill-based suggestions
            if 'Python' in profile.get('skills', []):
                suggestions.append({
                    'type': 'opportunity',
                    'title': 'Python Developer Opportunities',
                    'action': 'Find Python freelance projects',
                    'icon': 'code'
                })

            # Experience-based suggestions
            if profile.get('experience_years', 0) > 5:
                suggestions.append({
                    'type': 'consulting',
                    'title': 'Consulting Opportunities',
                    'action': f'Find consulting gigs in {profile.get("current_role", "your field")}',
                    'icon': 'briefcase'
                })

            # Preference-based suggestions
            if profile.get('job_preferences', {}).get('remote_only'):
                suggestions.append({
                    'type': 'remote',
                    'title': 'Remote Work Opportunities',
                    'action': 'Search for remote positions',
                    'icon': 'home'
                })

            # AI automation suggestions
            if ai_config.get('automation_level') == 'auto':
                suggestions.append({
                    'type': 'automation',
                    'title': 'Automated Job Applications',
                    'action': 'Set up auto-apply for matching jobs',
                    'icon': 'robot'
                })

        # Default suggestions if no profile
        if not suggestions:
            suggestions = [
                {
                    'type': 'profile',
                    'title': 'Complete Your Profile',
                    'action': 'Start interview to personalize assistance',
                    'icon': 'user'
                },
                {
                    'type': 'explore',
                    'title': 'Explore Opportunities',
                    'action': 'Browse available income opportunities',
                    'icon': 'search'
                }
            ]

        await self.send(text_data=json.dumps({
            'type': 'suggestions',
            'suggestions': suggestions
        }))

    async def send_action_suggestions(self, actions: list):
        """Send actionable suggestions from orchestration results"""
        await self.send(text_data=json.dumps({
            'type': 'actions',
            'actions': actions,
            'message': 'Here are some actions I can help you with:'
        }))

    async def execute_action(self, action: Dict[str, Any]):
        """Execute a specific action"""
        action_type = action.get('type')

        if action_type == 'apply_job':
            job_id = action.get('job_id')
            # Execute job application logic
            await self.send(text_data=json.dumps({
                'type': 'action_result',
                'action': action_type,
                'success': True,
                'message': f'Started application process for job {job_id}'
            }))

        elif action_type == 'generate_content':
            content_type = action.get('content_type')
            # Execute content generation
            await self.send(text_data=json.dumps({
                'type': 'action_result',
                'action': action_type,
                'success': True,
                'message': f'Generating {content_type} content...'
            }))

    async def send_available_agents(self):
        """Send list of available agents based on user's configuration"""
        agents = []

        if self.user_context:
            assigned_agents = self.user_context['ai_config'].get('assigned_agents', [])

            for agent in assigned_agents:
                agents.append({
                    'name': agent.get('agentName'),
                    'type': agent.get('agentType'),
                    'active': agent.get('canExecuteActions', True),
                    'tasksCompleted': agent.get('tasksCompleted', 0),
                    'successRate': agent.get('successRate', 0)
                })

        # Add default agents if none assigned
        if not agents:
            agents = [
                {
                    'name': 'Personal Assistant',
                    'type': 'personal_assistant',
                    'active': True,
                    'tasksCompleted': 0,
                    'successRate': 0
                },
                {
                    'name': 'Income Builder',
                    'type': 'income_builder',
                    'active': True,
                    'tasksCompleted': 0,
                    'successRate': 0
                }
            ]

        await self.send(text_data=json.dumps({
            'type': 'agents',
            'agents': agents,
            'total': len(agents)
        }))

    async def update_user_context(self):
        """Refresh user context from database"""
        if self.user:
            self.user_context = await personal_ai_orchestrator.load_user_context(str(self.user.id))

            await self.send(text_data=json.dumps({
                'type': 'context_updated',
                'profile_completion': self.user_context['metadata'].get('profile_completion', 0),
                'skills': len(self.user_context['profile'].get('skills', [])),
                'message': 'User context refreshed successfully'
            }))

    # Group message handlers
    async def chat_message(self, event):
        """Handle messages sent to the group"""
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'message': message
        }))

    async def system_notification(self, event):
        """Handle system notifications"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))