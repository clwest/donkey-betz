"""
Personal Assistant Profile Connector
====================================
Connects the Personal Assistant interview system with user profiles,
ensuring all interview data is properly saved and used for personalization.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import transaction
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)
User = get_user_model()


class PersonalAssistantProfileConnector:
    """
    Bridges the gap between Personal Assistant interviews and user profiles.
    Ensures every user interaction updates their profile for better personalization.
    """

    @database_sync_to_async
    def get_or_create_profile(self, user_id: str) -> Dict[str, Any]:
        """Get or create extended user profile"""
        from core.models import ExtendedUserProfile

        try:
            user = User.objects.get(id=user_id)
            profile, created = ExtendedUserProfile.objects.get_or_create(user=user)

            if created:
                logger.info(f"✅ Created new ExtendedUserProfile for user {user.username}")

            return {
                'success': True,
                'profile': profile,
                'created': created,
                'interview_completed': profile.interview_completed if hasattr(profile, 'interview_completed') else False
            }
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            logger.error(f"Error getting/creating profile: {str(e)}")
            return {'success': False, 'error': str(e)}

    @database_sync_to_async
    def update_profile_from_interview(self, user_id: str, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile with data collected from interview

        This is where the magic happens - transforming interview responses
        into a rich user profile for personalized experiences.
        """
        from core.models import ExtendedUserProfile

        try:
            user = User.objects.get(id=user_id)
            profile = ExtendedUserProfile.objects.get(user=user)

            with transaction.atomic():
                # Extract and save basic information
                if 'full_name' in interview_data:
                    profile.full_name = interview_data['full_name']

                if 'phone' in interview_data:
                    profile.phone = interview_data['phone']

                if 'location' in interview_data:
                    profile.location = interview_data['location']

                if 'bio' in interview_data:
                    profile.bio = interview_data['bio']

                # Save professional information
                if 'current_title' in interview_data:
                    profile.current_title = interview_data['current_title']

                if 'years_experience' in interview_data:
                    profile.years_experience = interview_data['years_experience']

                # Save skills (as JSON)
                if 'skills' in interview_data:
                    skills_list = interview_data['skills']
                    if isinstance(skills_list, list):
                        profile.skills = json.dumps(skills_list)
                    else:
                        profile.skills = json.dumps([skills_list])

                # Save experience history (as JSON)
                if 'experience' in interview_data:
                    profile.experience = json.dumps(interview_data['experience'])

                # Save education (as JSON)
                if 'education' in interview_data:
                    profile.education = json.dumps(interview_data['education'])

                # Save goals and preferences
                if 'goals' in interview_data:
                    profile.goals = json.dumps(interview_data['goals'])

                if 'preferences' in interview_data:
                    profile.preferences = json.dumps(interview_data['preferences'])

                # Income and work preferences
                if 'desired_income' in interview_data:
                    profile.desired_income = interview_data['desired_income']

                if 'work_preference' in interview_data:
                    profile.work_preference = interview_data['work_preference']

                if 'availability' in interview_data:
                    profile.availability = interview_data['availability']

                # Hidden skills discovered
                if 'hidden_skills' in interview_data:
                    existing_skills = json.loads(profile.skills) if profile.skills else []
                    all_skills = list(set(existing_skills + interview_data['hidden_skills']))
                    profile.skills = json.dumps(all_skills)

                # Mark interview as completed
                if hasattr(profile, 'interview_completed'):
                    profile.interview_completed = True
                    profile.interview_completed_at = datetime.now()

                # Calculate and update profile completeness
                completeness = self._calculate_completeness(profile)
                if hasattr(profile, 'profile_completeness'):
                    profile.profile_completeness = completeness

                profile.save()

                logger.info(f"✅ Updated profile for user {user.username} - Completeness: {completeness}%")

                return {
                    'success': True,
                    'profile_id': str(profile.id),
                    'completeness': completeness,
                    'message': f'Profile updated successfully! {completeness}% complete.'
                }

        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            return {'success': False, 'error': 'User not found'}
        except ExtendedUserProfile.DoesNotExist:
            logger.error(f"Profile for user {user_id} not found")
            return {'success': False, 'error': 'Profile not found'}
        except Exception as e:
            logger.error(f"Error updating profile from interview: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _calculate_completeness(self, profile) -> int:
        """Calculate profile completeness percentage"""
        fields = [
            'full_name', 'phone', 'location', 'bio',
            'current_title', 'years_experience', 'skills',
            'experience', 'education', 'goals', 'preferences',
            'desired_income', 'work_preference', 'availability'
        ]

        completed = 0
        for field in fields:
            if hasattr(profile, field):
                value = getattr(profile, field)
                if value and value != '[]' and value != '{}':
                    completed += 1

        return int((completed / len(fields)) * 100)

    @database_sync_to_async
    def get_profile_context_for_ai(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile context for AI agents to use in personalization

        This provides all agents with rich context about the user.
        """
        from core.models import ExtendedUserProfile

        try:
            user = User.objects.get(id=user_id)
            profile = ExtendedUserProfile.objects.get(user=user)

            context = {
                'user_id': str(user.id),
                'username': user.username,
                'full_name': profile.full_name or '',
                'location': profile.location or '',
                'bio': profile.bio or '',
                'current_title': profile.current_title or '',
                'years_experience': profile.years_experience or 0,
                'skills': json.loads(profile.skills) if profile.skills else [],
                'experience': json.loads(profile.experience) if profile.experience else [],
                'education': json.loads(profile.education) if profile.education else [],
                'goals': json.loads(profile.goals) if profile.goals else [],
                'preferences': json.loads(profile.preferences) if profile.preferences else {},
                'desired_income': profile.desired_income or 0,
                'work_preference': profile.work_preference or '',
                'availability': profile.availability or '',
                'interview_completed': profile.interview_completed if hasattr(profile, 'interview_completed') else False,
                'profile_completeness': self._calculate_completeness(profile)
            }

            return {
                'success': True,
                'context': context
            }

        except (User.DoesNotExist, ExtendedUserProfile.DoesNotExist):
            return {
                'success': False,
                'context': {},
                'error': 'Profile not found'
            }
        except Exception as e:
            logger.error(f"Error getting profile context: {str(e)}")
            return {
                'success': False,
                'context': {},
                'error': str(e)
            }

    @database_sync_to_async
    def should_start_interview(self, user_id: str) -> bool:
        """
        Determine if user should be prompted for interview

        Returns True if:
        - User has no profile
        - Profile is less than 30% complete
        - Interview was never completed
        """
        from core.models import ExtendedUserProfile

        try:
            user = User.objects.get(id=user_id)
            profile, created = ExtendedUserProfile.objects.get_or_create(user=user)

            if created:
                return True

            # Check if interview was completed
            if hasattr(profile, 'interview_completed') and profile.interview_completed:
                return False

            # Check profile completeness
            completeness = self._calculate_completeness(profile)
            if completeness < 30:
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking interview need: {str(e)}")
            return False

    async def connect_interview_to_income_builder(self, user_id: str) -> Dict[str, Any]:
        """
        Connect interview data to Income Builder for personalized opportunities
        """
        context_result = await self.get_profile_context_for_ai(user_id)

        if context_result.get('success'):
            context = context_result['context']

            # Notify Income Builder about updated profile
            from intelligence.income_builder import AIIncomeBuilder
            income_builder = AIIncomeBuilder()

            # Update income builder with user context
            await income_builder.update_user_context(user_id, context)

            logger.info(f"✅ Connected profile to Income Builder for user {user_id}")

            return {
                'success': True,
                'message': 'Profile connected to Income Builder'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to get profile context'
            }


# Singleton instance
profile_connector = PersonalAssistantProfileConnector()