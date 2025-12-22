"""
Personal Assistant Interview WebSocket Consumer
==============================================

Handles real-time interview conversations for building comprehensive user profiles.
"""

import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from datetime import datetime

from .personal_assistant_interviewer import personal_assistant_interviewer, InterviewPhase

logger = logging.getLogger(__name__)
User = get_user_model()


class InterviewConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for Personal Assistant Interview System"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_name = 'personal_interview'
        self.room_group_name = f'interview_{self.room_name}'
        self.user = None

        # Check if user is authenticated
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f"Interview WebSocket connected: {self.channel_name} for user {self.user.username}")

            # Send initial connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection',
                'status': 'connected',
                'message': 'Connected to Personal Assistant Interview System',
                'user': self.user.username
            }))

            # Check if user has an existing interview or completed profile
            await self.check_existing_interview()

        else:
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Interview WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'start_interview':
                # Start new interview
                quick_start = data.get('quick_start', False)
                await self.start_interview(quick_start)

            elif message_type == 'interview_response':
                # Process interview response
                response = data.get('response')
                await self.process_interview_response(response)

            elif message_type == 'skip_question':
                # Skip current question
                await self.skip_current_question()

            elif message_type == 'get_status':
                # Get interview status
                await self.get_interview_status()

            elif message_type == 'resume_interview':
                # Resume existing interview
                await self.resume_interview()

            elif message_type == 'restart_interview':
                # Restart interview from beginning
                quick_start = data.get('quick_start', False)
                await self.restart_interview(quick_start)

            elif message_type == 'get_profile_summary':
                # Get completed profile summary
                await self.get_profile_summary()

            elif message_type == 'update_profile':
                # Update profile with additional information
                profile_data = data.get('profile_data', {})
                await self.update_profile(profile_data)

            elif message_type == 'ping':
                # Respond to ping
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing interview message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def check_existing_interview(self):
        """Check if user has existing interview or completed profile"""
        try:
            # Check for existing interview
            status = await personal_assistant_interviewer.get_interview_status(str(self.user.id))

            if status.get('active'):
                # Send resumable interview status
                await self.send(text_data=json.dumps({
                    'type': 'existing_interview',
                    'can_resume': True,
                    'state': status['state'],
                    'message': 'You have an unfinished interview. Would you like to continue?'
                }))
                return

            # Check if user has completed interview
            profile_exists = await self.check_completed_profile()
            if profile_exists:
                await self.send(text_data=json.dumps({
                    'type': 'profile_exists',
                    'completed': True,
                    'message': 'Welcome back! Your profile is complete. I can help you find personalized opportunities.',
                    'can_restart': True
                }))
            else:
                # New user - show interview options
                await self.send(text_data=json.dumps({
                    'type': 'interview_options',
                    'message': 'Hi! I\'m your personal AI assistant. To provide personalized recommendations, I\'d like to learn about you. Choose your preferred approach:',
                    'options': [
                        {
                            'id': 'full_interview',
                            'title': 'Full Interview (8-10 minutes)',
                            'description': 'Complete profile for perfect opportunity matching',
                            'benefits': ['Personalized recommendations', 'Better job matches', 'Income optimization']
                        },
                        {
                            'id': 'quick_start',
                            'title': 'Quick Start (2 minutes)',
                            'description': 'Basic info to get started immediately',
                            'benefits': ['Instant opportunities', 'Can expand later']
                        }
                    ]
                }))

        except Exception as e:
            logger.error(f"Error checking existing interview: {e}")

    @database_sync_to_async
    def check_completed_profile(self) -> bool:
        """Check if user has a completed interview profile"""
        try:
            from core.models import EnhancedUserProfile
            profile = EnhancedUserProfile.objects.get(user=self.user)
            return profile.interview_completed
        except EnhancedUserProfile.DoesNotExist:
            return False

    async def start_interview(self, quick_start: bool = False):
        """Start a new interview"""
        try:
            result = await personal_assistant_interviewer.start_interview(
                user_id=str(self.user.id),
                quick_start=quick_start
            )

            if result.get('success'):
                await self.send(text_data=json.dumps({
                    'type': 'interview_started',
                    'interview_type': 'quick' if quick_start else 'full',
                    'estimated_time': result.get('estimated_time'),
                    'question': result.get('question'),
                    'state': result.get('state')
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Failed to start interview')
                }))

        except Exception as e:
            logger.error(f"Error starting interview: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to start interview: {str(e)}'
            }))

    async def process_interview_response(self, response):
        """Process user's interview response"""
        try:
            result = await personal_assistant_interviewer.process_response(
                user_id=str(self.user.id),
                response=response
            )

            if result.get('success'):
                if result.get('interview_complete'):
                    # Interview completed - save profile and send summary
                    profile = result.get('profile')
                    await self.save_completed_profile(profile)

                    await self.send(text_data=json.dumps({
                        'type': 'interview_completed',
                        'profile': profile,
                        'message': 'Excellent! Your profile is complete. I now understand your goals and can provide personalized recommendations.',
                        'next_steps': [
                            'Find personalized opportunities',
                            'Get income recommendations',
                            'Start applying to matches'
                        ]
                    }))

                    # Notify other systems about completed profile
                    await self.notify_profile_completion(profile)

                else:
                    # Send next question
                    await self.send(text_data=json.dumps({
                        'type': 'next_question',
                        'question': result.get('question'),
                        'insights': result.get('insights', []),
                        'state': result.get('state')
                    }))

            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Failed to process response')
                }))

        except Exception as e:
            logger.error(f"Error processing interview response: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to process response: {str(e)}'
            }))

    async def skip_current_question(self):
        """Skip the current question and move to next"""
        try:
            # Process empty response to skip
            result = await personal_assistant_interviewer.process_response(
                user_id=str(self.user.id),
                response=""  # Empty response indicates skip
            )

            if result.get('success'):
                await self.send(text_data=json.dumps({
                    'type': 'question_skipped',
                    'question': result.get('question'),
                    'state': result.get('state'),
                    'message': 'Question skipped. Moving to next...'
                }))

        except Exception as e:
            logger.error(f"Error skipping question: {e}")

    async def get_interview_status(self):
        """Get current interview status"""
        try:
            status = await personal_assistant_interviewer.get_interview_status(str(self.user.id))

            await self.send(text_data=json.dumps({
                'type': 'interview_status',
                'status': status
            }))

        except Exception as e:
            logger.error(f"Error getting interview status: {e}")

    async def resume_interview(self):
        """Resume existing interview"""
        try:
            result = await personal_assistant_interviewer.resume_interview(str(self.user.id))

            if result.get('success'):
                await self.send(text_data=json.dumps({
                    'type': 'interview_resumed',
                    'question': result.get('question'),
                    'state': result.get('state'),
                    'message': 'Welcome back! Let\'s continue where we left off.'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result.get('error', 'Could not resume interview')
                }))

        except Exception as e:
            logger.error(f"Error resuming interview: {e}")

    async def restart_interview(self, quick_start: bool = False):
        """Restart interview from beginning"""
        try:
            # Clear existing interview state
            if str(self.user.id) in personal_assistant_interviewer.active_interviews:
                del personal_assistant_interviewer.active_interviews[str(self.user.id)]

            # Start new interview
            await self.start_interview(quick_start)

        except Exception as e:
            logger.error(f"Error restarting interview: {e}")

    @database_sync_to_async
    def save_completed_profile(self, profile_data):
        """Save completed interview profile to database"""
        try:
            from core.models import EnhancedUserProfile
            from decimal import Decimal

            # Get or create enhanced profile
            enhanced_profile, created = EnhancedUserProfile.objects.get_or_create(
                user=self.user,
                defaults={
                    'primary_role': profile_data.get('strongest_skill', 'Professional')[:200]
                }
            )

            # Update with interview data
            enhanced_profile.interview_completed = True
            enhanced_profile.interview_completion_date = datetime.now()
            enhanced_profile.interview_type = profile_data.get('interview_type', 'full')

            # Basic interview data
            if profile_data.get('current_situation'):
                situation_mapping = {
                    'Employed - looking for more income': 'employed_seeking_more',
                    'Unemployed - need income ASAP': 'unemployed_need_asap',
                    'Student - want part-time work': 'student_part_time',
                    'Entrepreneur - scaling my business': 'entrepreneur_scaling',
                    'Retired - exploring opportunities': 'retired_exploring'
                }
                enhanced_profile.current_situation = situation_mapping.get(
                    profile_data['current_situation'], 'other'
                )

            enhanced_profile.available_hours_per_week = profile_data.get('available_hours_per_week', 0)

            if profile_data.get('monthly_income_goal'):
                enhanced_profile.monthly_income_goal = Decimal(str(profile_data['monthly_income_goal']))

            enhanced_profile.strongest_skill = profile_data.get('strongest_skill', '')
            enhanced_profile.skill_example = profile_data.get('skill_example', '')
            enhanced_profile.professional_background = profile_data.get('professional_background', '')
            enhanced_profile.career_motivation = profile_data.get('career_motivation', '')
            enhanced_profile.professional_achievements = profile_data.get('achievements', '')
            enhanced_profile.recent_learning = profile_data.get('learning_activity', '')

            enhanced_profile.work_type_preferences = profile_data.get('work_preferences', [])
            enhanced_profile.things_to_avoid = profile_data.get('things_to_avoid', '')
            enhanced_profile.other_work_preferences = profile_data.get('other_preferences', '')
            enhanced_profile.hidden_talents = profile_data.get('hidden_talents', [])
            enhanced_profile.available_assets = profile_data.get('available_assets', [])
            enhanced_profile.commitment_level = profile_data.get('commitment_level', '')

            if profile_data.get('auto_apply_preference'):
                auto_apply_mapping = {
                    'Yes - Apply automatically to good matches': 'auto_yes',
                    'Yes - But ask me first': 'ask_first',
                    'No - Just show me opportunities': 'no_auto'
                }
                enhanced_profile.auto_apply_preference = auto_apply_mapping.get(
                    profile_data['auto_apply_preference'], 'no_auto'
                )

            # AI insights and recommendations
            enhanced_profile.interview_insights = profile_data.get('ai_insights', [])
            enhanced_profile.profile_strength_score = profile_data.get('profile_strength_score', 0.0)
            enhanced_profile.personalized_recommendations = profile_data.get('recommendations', [])

            # Update skills from interview
            skills_data = profile_data.get('skills_by_category', {})
            if skills_data:
                competencies = {}
                for category, skills in skills_data.items():
                    for skill in skills:
                        if skill != 'None of these':
                            competencies[skill] = 5  # Default proficiency level

                enhanced_profile.core_competencies = competencies

            # Recalculate completeness
            enhanced_profile.calculate_completeness()
            enhanced_profile.save()

            logger.info(f"Saved completed interview profile for user {self.user.username}")

        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            raise

    async def notify_profile_completion(self, profile_data):
        """Notify other platform systems about completed profile"""
        try:
            # Notify the unified platform connector
            from frontend.src.services.UnifiedPlatformConnector import unifiedConnector

            # Send profile completion to income builder and job matching systems
            await self.channel_layer.group_send(
                'income_income_builder',
                {
                    'type': 'profile_completed',
                    'user_id': str(self.user.id),
                    'profile': profile_data
                }
            )

            # Notify personal assistant system
            await self.channel_layer.group_send(
                'personal_assistant',
                {
                    'type': 'profile_ready',
                    'user_id': str(self.user.id),
                    'profile': profile_data,
                    'message': 'Profile completed via interview - ready for personalized assistance'
                }
            )

            logger.info(f"Notified platform systems of profile completion for user {self.user.username}")

        except Exception as e:
            logger.error(f"Error notifying profile completion: {e}")

    async def get_profile_summary(self):
        """Get completed profile summary"""
        try:
            profile_data = await self.load_completed_profile()

            if profile_data:
                await self.send(text_data=json.dumps({
                    'type': 'profile_summary',
                    'profile': profile_data,
                    'recommendations': profile_data.get('personalized_recommendations', [])
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'no_profile',
                    'message': 'No completed profile found. Would you like to start an interview?'
                }))

        except Exception as e:
            logger.error(f"Error getting profile summary: {e}")

    @database_sync_to_async
    def load_completed_profile(self):
        """Load completed profile from database"""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.get(user=self.user)
            if not profile.interview_completed:
                return None

            return {
                'user_id': str(self.user.id),
                'name': profile.user.get_full_name() or profile.user.username,
                'interview_type': profile.interview_type,
                'current_situation': profile.current_situation,
                'available_hours_per_week': profile.available_hours_per_week,
                'monthly_income_goal': float(profile.monthly_income_goal) if profile.monthly_income_goal else 0,
                'strongest_skill': profile.strongest_skill,
                'work_type_preferences': profile.work_type_preferences,
                'commitment_level': profile.commitment_level,
                'profile_strength_score': profile.profile_strength_score,
                'personalized_recommendations': profile.personalized_recommendations,
                'core_competencies': profile.core_competencies,
                'interview_completion_date': profile.interview_completion_date.isoformat() if profile.interview_completion_date else None
            }

        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            return None

    async def update_profile(self, profile_data):
        """Update profile with additional information"""
        try:
            await self.update_database_profile(profile_data)

            await self.send(text_data=json.dumps({
                'type': 'profile_updated',
                'message': 'Profile updated successfully',
                'updated_fields': list(profile_data.keys())
            }))

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to update profile: {str(e)}'
            }))

    @database_sync_to_async
    def update_database_profile(self, profile_data):
        """Update profile in database"""
        try:
            from core.models import EnhancedUserProfile

            profile = EnhancedUserProfile.objects.get(user=self.user)

            # Update allowed fields
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)

            profile.save()

        except Exception as e:
            logger.error(f"Error updating database profile: {e}")
            raise