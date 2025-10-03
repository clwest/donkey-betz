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

        # Join user-specific group for learning insights
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_add(
                f"user_{self.user.id}",
                self.channel_name
            )

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
        # Leave user group
        if self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"user_{self.user.id}",
                self.channel_name
            )

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
        """PHASE 3 FIX: Generate personalized AI response based on user data"""
        message_lower = message.lower()

        # Get user stats for personalization
        user_stats = self.user_profile.get('stats', {}) if self.user_profile else {}
        user_skills = self.user_profile.get('skills', []) if self.user_profile else []
        user_revenue = user_stats.get('revenue', 0)
        user_apps = user_stats.get('applications', 0)

        # Personalized responses based on actual user data
        if 'opportunity' in message_lower or 'job' in message_lower:
            skills_str = ', '.join(user_skills[:3]) if user_skills else 'your skillset'
            response = f"Let me search for opportunities matching {skills_str}. I'll prioritize high-value positions that align with your ${user_revenue:.0f} current revenue goal."

        elif 'skill' in message_lower:
            if user_skills:
                response = f"You currently have {len(user_skills)} skills: {', '.join(user_skills[:5])}. " \
                          f"Would you like to add more skills to unlock additional opportunities?"
            else:
                response = "I see you haven't added any skills yet. Let's build your profile! What are your top 3 skills?"

        elif 'goal' in message_lower:
            response = f"Your current revenue is ${user_revenue:.2f} from {user_apps} applications. " \
                      f"What revenue target would you like to achieve? I can help create a personalized action plan."

        elif 'help' in message_lower or 'what can you' in message_lower:
            response = "I can help you with:\n" \
                      f"• Finding opportunities (you have {user_apps} applications so far)\n" \
                      f"• Managing your {len(user_skills)} skills\n" \
                      "• Setting revenue goals and tracking progress\n" \
                      "• Quick Apply to matched positions\n" \
                      "• Analyzing your success rate and earnings\n\n" \
                      "What would you like to focus on?"

        elif 'revenue' in message_lower or 'money' in message_lower or 'earning' in message_lower:
            success_rate = user_stats.get('success_rate', 0)
            response = f"Your current revenue is ${user_revenue:.2f} from {user_apps} applications " \
                      f"with a {success_rate:.1f}% success rate. " \
                      f"Based on your pattern, I can recommend high-value opportunities to accelerate growth."

        elif 'apply' in message_lower:
            response = f"You've submitted {user_apps} applications so far. " \
                      f"I can help you Quick Apply to perfectly matched positions. " \
                      f"Want to see the latest opportunities?"

        elif 'progress' in message_lower or 'stats' in message_lower or 'status' in message_lower:
            response = f"📊 **Your Progress:**\n" \
                      f"• Applications: {user_apps}\n" \
                      f"• Revenue: ${user_revenue:.2f}\n" \
                      f"• Success Rate: {user_stats.get('success_rate', 0):.1f}%\n" \
                      f"• Skills: {len(user_skills)}\n" \
                      f"• Opportunities Viewed: {user_stats.get('opportunities', 0)}\n\n" \
                      f"You're making great progress! Keep it up!"

        else:
            # Personalized generic response
            name = self.user_profile.get('name', 'there') if self.user_profile else 'there'
            response = f"Hi {name}! I'm here to help you reach your goals. " \
                      f"What would you like to work on today?"

        return response

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

    async def load_user_profile(self):
        """PHASE 3 FIX: Load complete user profile from database"""
        if self.user and self.user.is_authenticated:
            profile_data = await self.get_user_profile_data()
            self.user_profile = profile_data

            # Send profile data to frontend automatically
            await self.send(text_data=json.dumps({
                'type': 'profile_data',
                'profile': profile_data,
                'timestamp': timezone.now().isoformat()
            }))

    @database_sync_to_async
    def get_user_profile_data(self):
        """Get complete user profile with stats from database"""
        from core.models import UserProfile, Revenue
        from django.db.models import Sum, Count

        # Get or create UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={
                'skills': [],
                'experience_years': 0,
            }
        )

        # Get revenue stats
        revenue_stats = Revenue.objects.filter(user=self.user).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        total_revenue = float(revenue_stats['total'] or 0)
        application_count = revenue_stats['count'] or 0

        # Get opportunities count
        try:
            from core.models_engagement_metrics import OpportunityInteraction
            opportunities_count = OpportunityInteraction.objects.filter(
                user=self.user
            ).count()
        except Exception:
            opportunities_count = 0

        # Calculate success rate
        confirmed_revenue = Revenue.objects.filter(
            user=self.user, status='confirmed'
        ).count()
        success_rate = (confirmed_revenue / application_count * 100) if application_count > 0 else 0

        return {
            'id': str(self.user.id),  # Convert UUID to string for JSON serialization
            'name': self.user.get_full_name() or self.user.username,
            'email': self.user.email,
            'member_since': self.user.date_joined.isoformat() if hasattr(self.user, 'date_joined') else None,
            'skills': profile.skills or [],
            'experience_years': profile.experience_years or 0,
            'bio': profile.bio or '',
            'occupation': profile.occupation or '',
            'stats': {
                'applications': application_count,
                'opportunities': opportunities_count,
                'revenue': total_revenue,
                'success_rate': round(success_rate, 1)
            }
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
        """PHASE 3 FIX: Send real user skills from database"""
        skills = await self.get_user_skills()

        await self.send(text_data=json.dumps({
            'type': 'skills_list',
            'skills': skills,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_user_skills(self):
        """Get user skills from database"""
        from core.models import UserProfile

        try:
            profile = UserProfile.objects.get(user=self.user)
            return profile.skills or []
        except UserProfile.DoesNotExist:
            return []

    async def handle_add_skill(self, data):
        """PHASE 3 FIX: Handle adding a new skill to database"""
        skill = data.get('skill', '').strip()

        if skill:
            updated_skills = await self.add_skill_to_profile(skill)

            await self.send(text_data=json.dumps({
                'type': 'skill_added',
                'skill': skill,
                'all_skills': updated_skills,
                'message': f'Added "{skill}" to your skills',
                'timestamp': timezone.now().isoformat()
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Skill name cannot be empty',
                'timestamp': timezone.now().isoformat()
            }))

    @database_sync_to_async
    def add_skill_to_profile(self, skill):
        """Add skill to user profile in database"""
        from core.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={'skills': []}
        )

        if not profile.skills:
            profile.skills = []

        if skill not in profile.skills:
            profile.skills.append(skill)
            profile.save()

        return profile.skills

    async def send_goals(self):
        """PHASE 3 FIX: Send real user goals"""
        goals = await self.get_user_goals()

        await self.send(text_data=json.dumps({
            'type': 'goals_list',
            'goals': goals,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_user_goals(self):
        """Get user goals from database"""
        from core.models import UserProfile

        try:
            profile = UserProfile.objects.get(user=self.user)
            # Assuming goals are stored in a JSON field
            return getattr(profile, 'goals', []) or []
        except UserProfile.DoesNotExist:
            return []

    async def handle_set_goal(self, data):
        """PHASE 3 FIX: Handle setting a new goal in database"""
        goal = data.get('goal', '').strip()

        if goal:
            updated_goals = await self.add_goal_to_profile(goal)

            await self.send(text_data=json.dumps({
                'type': 'goal_set',
                'goal': goal,
                'all_goals': updated_goals,
                'message': f'New goal set: "{goal}"',
                'timestamp': timezone.now().isoformat()
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Goal cannot be empty',
                'timestamp': timezone.now().isoformat()
            }))

    @database_sync_to_async
    def add_goal_to_profile(self, goal):
        """Add goal to user profile in database"""
        from core.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(
            user=self.user,
            defaults={}
        )

        # Check if profile has goals field, if not add it
        if not hasattr(profile, 'goals') or profile.goals is None:
            profile.goals = []

        if goal not in profile.goals:
            profile.goals.append(goal)
            profile.save()

        return profile.goals

    async def send_activity_stats(self):
        """PHASE 3 FIX: Send real activity stats from database"""
        stats = await self.get_activity_stats()

        await self.send(text_data=json.dumps({
            'type': 'activity_stats',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_activity_stats(self):
        """Get real activity statistics from database"""
        from core.models import Revenue
        from django.db.models import Sum, Count
        from datetime import timedelta

        try:
            from core.models_engagement_metrics import OpportunityInteraction
        except ImportError:
            OpportunityInteraction = None

        # Get total stats
        total_revenue_stats = Revenue.objects.filter(user=self.user).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        total_revenue = float(total_revenue_stats['total'] or 0)
        total_apps = total_revenue_stats['count'] or 0

        # Get this week's stats
        one_week_ago = timezone.now() - timedelta(days=7)
        week_revenue_stats = Revenue.objects.filter(
            user=self.user,
            created_at__gte=one_week_ago
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        week_revenue = float(week_revenue_stats['total'] or 0)
        week_apps = week_revenue_stats['count'] or 0

        # Get completed projects
        completed_projects = Revenue.objects.filter(
            user=self.user,
            status='confirmed'
        ).count()

        # Calculate success rate
        success_rate = (completed_projects / total_apps * 100) if total_apps > 0 else 0

        # Get opportunities
        if OpportunityInteraction:
            try:
                opportunities = OpportunityInteraction.objects.filter(user=self.user).count()
            except Exception:
                opportunities = 0
        else:
            opportunities = 0

        return {
            'applications': total_apps,
            'opportunities': opportunities,
            'revenue': total_revenue,
            'projects_completed': completed_projects,
            'success_rate': round(success_rate, 1),
            'this_week': {
                'applications': week_apps,
                'revenue': week_revenue
            }
        }

    # LEARNING ORCHESTRATOR INTEGRATION
    async def learning_insights(self, event):
        """
        Receive learning insights from Learning Orchestrator
        and display to user via Personal Assistant
        """
        message = event.get('message', '')
        optimizations = event.get('optimizations', {})

        # Send learning insights to frontend
        await self.send(text_data=json.dumps({
            'type': 'learning_insights',
            'message': message,
            'optimizations': optimizations,
            'timestamp': timezone.now().isoformat()
        }))

        logger.info(f"📨 Delivered learning insights to user via Personal Assistant")