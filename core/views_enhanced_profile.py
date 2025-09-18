"""
Enhanced User Profile API Views
================================
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.models import EnhancedUserProfile, UserMemoryContext

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def get_enhanced_profile(request):
    """Get or update the user's enhanced profile."""
    try:
        profile, created = EnhancedUserProfile.objects.get_or_create(user=request.user)

        if request.method == 'PUT':
            # Handle profile update
            data = request.data
            logger.info(f"Updating enhanced profile for {request.user.username} with data: {data}")

            # Handle interview completion data structure
            if 'name' in data:
                # Extract first and last name if provided
                name_parts = data['name'].split(' ', 1)
                if len(name_parts) >= 1:
                    request.user.first_name = name_parts[0]
                if len(name_parts) >= 2:
                    request.user.last_name = name_parts[1]
                request.user.save()

            # Map interview data to profile fields
            if 'skills' in data:
                profile.core_competencies = data['skills'] if isinstance(data['skills'], list) else [data['skills']]

            if 'experience_level' in data:
                profile.learning_style = f"Experience level: {data['experience_level']}"

            if 'income_goal' in data:
                profile.long_term_goals = profile.long_term_goals or []
                goal = f"Target income: {data['income_goal']}"
                if goal not in profile.long_term_goals:
                    profile.long_term_goals.append(goal)

            if 'work_preferences' in data:
                profile.preferred_channels = data['work_preferences'] if isinstance(data['work_preferences'], list) else [data['work_preferences']]

            # Handle general profile fields
            field_mappings = {
                'primary_role': 'primary_role',
                'secondary_roles': 'secondary_roles',
                'long_term_goals': 'long_term_goals',
                'current_projects': 'current_projects',
                'quarterly_objectives': 'quarterly_objectives',
                'communication_style': 'communication_style',
                'preferred_channels': 'preferred_channels',
                'optimal_meeting_times': 'optimal_meeting_times',
                'decision_framework': 'decision_framework',
                'delegation_preferences': 'delegation_preferences',
                'work_schedule': 'work_schedule',
                'time_zone': 'time_zone',
                'morning_routine': 'morning_routine',
                'energy_patterns': 'energy_patterns',
                'dietary_preferences': 'dietary_preferences',
                'travel_preferences': 'travel_preferences',
                'personal_values': 'personal_values',
                'stress_indicators': 'stress_indicators',
                'core_competencies': 'core_competencies',
                'learning_style': 'learning_style',
                'current_learning_goals': 'current_learning_goals',
                'knowledge_gaps': 'knowledge_gaps',
                'preferred_learning_resources': 'preferred_learning_resources',
                'certifications': 'certifications',
                'privacy_level': 'privacy_level',
                'sensitive_topics': 'sensitive_topics',
                'data_retention_days': 'data_retention_days',
                'update_frequency': 'update_frequency'
            }

            for data_field, profile_field in field_mappings.items():
                if data_field in data:
                    setattr(profile, profile_field, data[data_field])

            # Save the profile
            profile.save()
            logger.info(f"Successfully saved enhanced profile for {request.user.username}")

            # Return success response
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'completeness': profile.calculate_completeness()
            })

        # GET request - return profile data
        if created:
            logger.info(f"Created new enhanced profile for {request.user.username}")

        # Calculate completeness
        completeness = profile.calculate_completeness()

        return Response({
            'success': True,
            'profile': {
                # Roles & Goals
                'primary_role': profile.primary_role,
                'secondary_roles': profile.secondary_roles,
                'long_term_goals': profile.long_term_goals,
                'current_projects': profile.current_projects,
                'quarterly_objectives': profile.quarterly_objectives,

                # Communication & Decision
                'communication_style': profile.communication_style,
                'preferred_channels': profile.preferred_channels,
                'optimal_meeting_times': profile.optimal_meeting_times,
                'decision_framework': profile.decision_framework,
                'delegation_preferences': profile.delegation_preferences,

                # Personal Preferences
                'work_schedule': profile.work_schedule,
                'time_zone': profile.time_zone,
                'morning_routine': profile.morning_routine,
                'energy_patterns': profile.energy_patterns,
                'dietary_preferences': profile.dietary_preferences,
                'travel_preferences': profile.travel_preferences,
                'personal_values': profile.personal_values,
                'stress_indicators': profile.stress_indicators,

                # Skills & Learning
                'core_competencies': profile.core_competencies,
                'learning_style': profile.learning_style,
                'current_learning_goals': profile.current_learning_goals,
                'knowledge_gaps': profile.knowledge_gaps,
                'preferred_learning_resources': profile.preferred_learning_resources,
                'certifications': profile.certifications,

                # Privacy & Settings
                'privacy_level': profile.privacy_level,
                'sensitive_topics': profile.sensitive_topics,
                'data_retention_days': profile.data_retention_days,
                'update_frequency': profile.update_frequency,

                # Metadata
                'profile_completeness': completeness,
                'interaction_count': profile.interaction_count,
                'should_update': profile.should_update_profile()
            }
        })

    except Exception as e:
        logger.error(f"Error handling enhanced profile request: {e}")
        return Response({
            'error': 'Failed to handle profile request',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_enhanced_profile(request):
    """Update the user's enhanced profile."""
    try:
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=request.user)

        # Update fields based on category
        category = request.data.get('category', 'general')
        fields = request.data.get('fields', {})

        if category == 'roles_goals':
            for field in ['primary_role', 'secondary_roles', 'long_term_goals',
                         'current_projects', 'quarterly_objectives']:
                if field in fields:
                    setattr(profile, field, fields[field])

        elif category == 'communication':
            for field in ['communication_style', 'preferred_channels',
                         'optimal_meeting_times', 'decision_framework',
                         'delegation_preferences']:
                if field in fields:
                    setattr(profile, field, fields[field])

        elif category == 'personal':
            for field in ['work_schedule', 'time_zone', 'morning_routine',
                         'energy_patterns', 'dietary_preferences',
                         'travel_preferences', 'personal_values', 'stress_indicators']:
                if field in fields:
                    setattr(profile, field, fields[field])

        elif category == 'skills':
            for field in ['core_competencies', 'learning_style',
                         'current_learning_goals', 'knowledge_gaps',
                         'preferred_learning_resources', 'certifications']:
                if field in fields:
                    setattr(profile, field, fields[field])

        elif category == 'privacy':
            for field in ['privacy_level', 'sensitive_topics',
                         'data_retention_days', 'update_frequency']:
                if field in fields:
                    setattr(profile, field, fields[field])

        else:  # general - update any field
            for field, value in fields.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)

        # Save and recalculate completeness
        profile.save()
        completeness = profile.calculate_completeness()

        # Also save to session for compatibility with AI job system
        from datetime import datetime as dt
        session_key = f'extended_profile_{request.user.id}'

        # Create comprehensive session data with ALL profile fields
        session_data = {
            # Basic Info
            'full_name': getattr(profile, 'full_name', '') or f"{request.user.first_name} {request.user.last_name}".strip(),
            'professional_summary': getattr(profile, 'professional_summary', ''),
            'skills': getattr(profile, 'skills', []),
            'work_history': getattr(profile, 'work_history', []),
            'years_experience': getattr(profile, 'years_experience', 0),
            'job_preferences': getattr(profile, 'job_preferences', {}),

            # Roles & Goals
            'primary_role': getattr(profile, 'primary_role', ''),
            'secondary_roles': getattr(profile, 'secondary_roles', []),
            'long_term_goals': getattr(profile, 'long_term_goals', []),
            'current_projects': getattr(profile, 'current_projects', []),

            # Communication
            'communication_style': getattr(profile, 'communication_style', ''),
            'preferred_channels': getattr(profile, 'preferred_channels', []),

            # Skills & Learning
            'core_competencies': getattr(profile, 'core_competencies', []),
            'learning_style': getattr(profile, 'learning_style', ''),
            'certifications': getattr(profile, 'certifications', []),

            # Application preferences
            'application_tone': getattr(profile, 'application_tone', 'professional'),

            # Metadata
            'updated_at': dt.now().isoformat(),
            'is_complete': completeness >= 50  # Mark as complete if >50% filled
        }

        # Save to session with force update
        request.session[session_key] = session_data
        request.session.modified = True
        request.session.save()  # Force immediate save

        return Response({
            'success': True,
            'message': f'Profile updated successfully',
            'completeness': completeness
        })

    except Exception as e:
        logger.error(f"Error updating enhanced profile: {e}")
        return Response({
            'error': 'Failed to update profile',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_memories(request):
    """Get user's memory contexts."""
    try:
        memory_type = request.GET.get('type')
        limit = int(request.GET.get('limit', 20))

        memories = UserMemoryContext.objects.filter(user=request.user)

        if memory_type:
            memories = memories.filter(memory_type=memory_type)

        memories = memories[:limit]

        return Response({
            'success': True,
            'memories': [{
                'id': str(memory.id),
                'type': memory.memory_type,
                'content': memory.content,
                'importance': memory.importance,
                'related_project': memory.related_project,
                'related_goal': memory.related_goal,
                'tags': memory.tags,
                'created_at': memory.created_at.isoformat(),
                'accessed_count': memory.accessed_count
            } for memory in memories]
        })

    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        return Response({
            'error': 'Failed to get memories',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_suggestions(request):
    """Get AI-powered suggestions for profile improvement."""
    try:
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=request.user)
        completeness = profile.calculate_completeness()

        suggestions = []

        # Check critical fields
        if not profile.primary_role:
            suggestions.append({
                'category': 'roles_goals',
                'field': 'primary_role',
                'message': 'Add your primary professional role',
                'priority': 'high'
            })

        if not profile.long_term_goals:
            suggestions.append({
                'category': 'roles_goals',
                'field': 'long_term_goals',
                'message': 'Set your long-term career goals',
                'priority': 'high'
            })

        if not profile.core_competencies:
            suggestions.append({
                'category': 'skills',
                'field': 'core_competencies',
                'message': 'Add your core skills and competencies',
                'priority': 'high'
            })

        if not profile.work_schedule:
            suggestions.append({
                'category': 'personal',
                'field': 'work_schedule',
                'message': 'Define your typical work schedule',
                'priority': 'medium'
            })

        if not profile.current_projects:
            suggestions.append({
                'category': 'roles_goals',
                'field': 'current_projects',
                'message': 'Add your current projects',
                'priority': 'medium'
            })

        return Response({
            'success': True,
            'completeness': completeness,
            'suggestions': suggestions[:5]  # Top 5 suggestions
        })

    except Exception as e:
        logger.error(f"Error getting profile suggestions: {e}")
        return Response({
            'error': 'Failed to get suggestions',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)