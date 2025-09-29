"""
Personal Assistant WebSocket Consumer for AI-powered chat and user profiling
"""

import json
import asyncio
import logging
import random
from datetime import datetime, timedelta
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class PersonalAssistantConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for personal AI assistant interactions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.conversation_history = []
        self.user_profile = {}

    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()

        # Get user if authenticated
        self.user = self.scope.get("user")

        logger.info(f"Personal Assistant WebSocket connected: {self.channel_name}")

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Personal AI Assistant',
            'timestamp': timezone.now().isoformat()
        }))

        # Load user profile if authenticated
        if self.user and self.user.is_authenticated:
            await self.load_user_profile()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"Personal Assistant WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            logger.info(f"Personal Assistant received: {message_type}")

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'get_profile':
                await self.send_profile_data()
            elif message_type == 'update_profile':
                await self.handle_profile_update(data)
            elif message_type == 'get_skills':
                await self.send_skills()
            elif message_type == 'add_skill':
                await self.handle_add_skill(data)
            elif message_type == 'get_goals':
                await self.send_goals()
            elif message_type == 'set_goal':
                await self.handle_set_goal(data)
            elif message_type == 'get_activity':
                await self.send_activity_stats()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'response',
                    'message': f'Received {message_type}',
                    'timestamp': timezone.now().isoformat()
                }))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_chat_message(self, data):
        """Process chat messages and generate AI responses"""
        message = data.get('message', '')
        user_id = data.get('user_id')

        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message,
            'timestamp': timezone.now().isoformat()
        })

        # Generate AI response based on message content
        response = await self.generate_ai_response(message)

        # Add response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': timezone.now().isoformat()
        })

        # Send response
        await self.send(text_data=json.dumps({
            'type': 'chat_response',
            'message': response,
            'timestamp': timezone.now().isoformat()
        }))

        # Check for special commands or intents
        await self.process_intent(message)

    async def generate_ai_response(self, message):
        """Generate AI response based on user message"""
        message_lower = message.lower()

        # Pattern matching for common queries
        if 'opportunity' in message_lower or 'job' in message_lower:
            responses = [
                "I've found 3 new opportunities that match your skills! The highest paying is a Python Developer role at $5,000/month. Would you like me to show you the details?",
                "Based on your profile, I recommend focusing on Full Stack Developer positions. You have a 95% match rate with several open positions. Shall I help you apply?",
                "Great news! A new opportunity just came in that's perfect for you. It's a remote position with flexible hours. Want to know more?"
            ]
        elif 'skill' in message_lower:
            responses = [
                "I see you have Python, Django, and React in your skillset. Would you like me to add any new skills or certifications?",
                "Your current skills give you access to 127 potential opportunities. Adding 'Machine Learning' could increase this to 189. Interested?",
                "Based on market demand, I recommend adding 'AWS' and 'Docker' to your skills. These are requested in 67% of high-paying positions."
            ]
        elif 'goal' in message_lower:
            responses = [
                "Your current goal is to reach $10K monthly revenue. You're at $2,600 - that's 26% of the way there! Let me help you accelerate.",
                "Setting clear goals is important. What revenue target would you like to achieve this month?",
                "I can help you set SMART goals for your career growth. What's your primary objective right now?"
            ]
        elif 'help' in message_lower or 'what can you' in message_lower:
            responses = [
                "I can help you with:\n• Finding opportunities that match your skills\n• Updating your profile and skills\n• Setting and tracking goals\n• Applying to jobs with one click\n• Tracking your revenue and applications\n• Getting personalized career advice\n\nWhat would you like to do first?"
            ]
        elif 'revenue' in message_lower or 'money' in message_lower or 'earning' in message_lower:
            responses = [
                "Your current revenue is $2,600 with 42 active projects. Your average project value is $62. To reach $10K, you need about 120 more projects at this rate, or we can focus on higher-value opportunities.",
                "You're earning well! Your success rate is 89%, which is excellent. Want to see opportunities that could double your revenue?",
                "Based on your earning pattern, you could reach $5K/month by taking on 3 more projects per week. Shall I find some quick wins for you?"
            ]
        elif 'apply' in message_lower:
            responses = [
                "I can help you apply to jobs instantly! Just say 'Quick Apply' when viewing an opportunity, and I'll handle the rest.",
                "Your last application was sent 2 hours ago. Want to apply to more positions? I have 5 that are perfect matches.",
                "Great! I'll prepare your application. Your profile is complete and ready to go. Which opportunity interests you?"
            ]
        else:
            # Generic helpful responses
            responses = [
                "I'm here to help you succeed! What would you like to work on today?",
                "That's interesting! Tell me more about what you're looking for.",
                "I understand. Let me help you with that. What specific information do you need?",
                "Great question! Let me analyze that for you and provide personalized recommendations.",
                "I'm processing your request. How can I make this most helpful for you?"
            ]

        return random.choice(responses)

    async def process_intent(self, message):
        """Process special intents from chat messages"""
        message_lower = message.lower()

        # Check for profile update intent
        if 'update my skills' in message_lower:
            await self.send_skills()

        # Check for goal setting intent
        elif 'set' in message_lower and 'goal' in message_lower:
            await self.send(text_data=json.dumps({
                'type': 'intent_detected',
                'intent': 'set_goal',
                'message': 'Would you like to set a new goal? Please specify your target.',
                'timestamp': timezone.now().isoformat()
            }))

        # Check for opportunity search intent
        elif 'find' in message_lower and ('opportunity' in message_lower or 'job' in message_lower):
            await self.send(text_data=json.dumps({
                'type': 'intent_detected',
                'intent': 'find_opportunities',
                'message': 'Searching for opportunities that match your profile...',
                'timestamp': timezone.now().isoformat()
            }))

    @database_sync_to_async
    def load_user_profile(self):
        """Load user profile from database"""
        if self.user:
            self.user_profile = {
                'id': self.user.id,
                'name': self.user.get_full_name() or self.user.username,
                'email': self.user.email,
                'member_since': self.user.date_joined.isoformat() if hasattr(self.user, 'date_joined') else None
            }

    async def send_profile_data(self):
        """Send user profile data"""
        profile = self.user_profile or {
            'name': 'Guest User',
            'email': 'guest@example.com',
            'skills': ['Python', 'Django', 'React', 'Machine Learning', 'Web Scraping'],
            'goals': ['Reach $10K monthly revenue', 'Complete 500 projects', 'Build passive income'],
            'stats': {
                'applications': 127,
                'opportunities': 342,
                'revenue': 2600,
                'success_rate': 89
            }
        }

        await self.send(text_data=json.dumps({
            'type': 'profile_data',
            'profile': profile,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_profile_update(self, data):
        """Handle profile update request"""
        updates = data.get('updates', {})

        # In production, save to database
        self.user_profile.update(updates)

        await self.send(text_data=json.dumps({
            'type': 'profile_updated',
            'message': 'Profile updated successfully',
            'profile': self.user_profile,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_skills(self):
        """Send user skills"""
        skills = [
            'Python', 'Django', 'React', 'JavaScript',
            'Machine Learning', 'Web Scraping', 'API Development',
            'PostgreSQL', 'Redis', 'Docker'
        ]

        await self.send(text_data=json.dumps({
            'type': 'skills_updated',
            'skills': skills,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_add_skill(self, data):
        """Handle adding a new skill"""
        skill = data.get('skill', '')

        await self.send(text_data=json.dumps({
            'type': 'skill_added',
            'skill': skill,
            'message': f'Added "{skill}" to your skills',
            'timestamp': timezone.now().isoformat()
        }))

    async def send_goals(self):
        """Send user goals"""
        goals = [
            'Reach $10K monthly revenue',
            'Complete 500 projects',
            'Build passive income streams',
            'Master AI technologies'
        ]

        await self.send(text_data=json.dumps({
            'type': 'goals_updated',
            'goals': goals,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_set_goal(self, data):
        """Handle setting a new goal"""
        goal = data.get('goal', '')

        await self.send(text_data=json.dumps({
            'type': 'goal_set',
            'goal': goal,
            'message': f'New goal set: "{goal}"',
            'timestamp': timezone.now().isoformat()
        }))

    async def send_activity_stats(self):
        """Send user activity statistics"""
        stats = {
            'applications': random.randint(100, 150),
            'opportunities': random.randint(300, 400),
            'revenue': random.randint(2000, 3000),
            'projects_completed': random.randint(30, 50),
            'success_rate': random.randint(85, 95),
            'this_week': {
                'applications': random.randint(5, 15),
                'revenue': random.randint(200, 500)
            }
        }

        await self.send(text_data=json.dumps({
            'type': 'activity_stats',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))