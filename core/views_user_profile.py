"""
User Profile and AI Configuration API Views
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models import UserProfile, UserPreferences
from core.permissions_role import IsOperatorRole  # S3052 PR 4 A2 fold: operator gate

User = get_user_model()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_extended(request):
    """Get or update extended user profile"""
    user = request.user

    if request.method == 'GET':
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'bio': '',
                'skills': [],
                'experience_years': 0,
                'current_role': '',
                'industries': [],
                'hourly_rate_min': 50,
                'salary_min': 50000,
                'remote_only': True,
                'contract_work': True,
                'full_time': True,
                'portfolio_url': '',
                'linkedin_url': '',
                'github_url': '',
            }
        )

        return Response({
            'success': True,
            'data': {
                'username': user.username,
                'email': user.email,
                'skills': profile.skills if isinstance(profile.skills, list) else [],
                'experienceYears': profile.experience_years,
                'currentRole': profile.current_role,
                'industries': profile.industries if isinstance(profile.industries, list) else [],
                'jobPreferences': {
                    'remote': profile.remote_only,
                    'contract': profile.contract_work,
                    'fullTime': profile.full_time,
                    'hourlyRateMin': profile.hourly_rate_min,
                    'salaryMin': profile.salary_min,
                },
                'resumeId': profile.resume_id if hasattr(profile, 'resume_id') else None,
                'portfolioUrl': profile.portfolio_url,
                'linkedinUrl': profile.linkedin_url,
                'githubUrl': profile.github_url,
                'completionPercentage': calculate_profile_completion(profile),
            }
        })

    elif request.method == 'POST':
        # Update profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        data = request.data

        # Update fields
        if 'skills' in data:
            profile.skills = data['skills']
        if 'experienceYears' in data:
            profile.experience_years = data['experienceYears']
        if 'currentRole' in data:
            profile.current_role = data['currentRole']
        if 'industries' in data:
            profile.industries = data['industries']
        if 'portfolioUrl' in data:
            profile.portfolio_url = data['portfolioUrl']
        if 'linkedinUrl' in data:
            profile.linkedin_url = data['linkedinUrl']
        if 'githubUrl' in data:
            profile.github_url = data['githubUrl']

        # Update job preferences
        if 'jobPreferences' in data:
            prefs = data['jobPreferences']
            if 'remote' in prefs:
                profile.remote_only = prefs['remote']
            if 'contract' in prefs:
                profile.contract_work = prefs['contract']
            if 'fullTime' in prefs:
                profile.full_time = prefs['fullTime']
            if 'hourlyRateMin' in prefs:
                profile.hourly_rate_min = prefs['hourlyRateMin']
            if 'salaryMin' in prefs:
                profile.salary_min = prefs['salaryMin']

        profile.save()

        return Response({
            'success': True,
            'message': 'Profile updated successfully'
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ai_configuration(request):
    """Get or update AI configuration for user"""
    user = request.user

    if request.method == 'GET':
        # Get or create user preferences
        prefs, created = UserPreferences.objects.get_or_create(
            user=user,
            defaults={
                'default_model': 'gpt-5',
                'reasoning_level': 'medium',
                'automation_level': 'semi-auto',
                'daily_token_limit': 100000,
                'monthly_spending_limit': 500.0,
                'memory_retention_days': 30,
                'share_memory_across_agents': True,
            }
        )

        return Response({
            'success': True,
            'data': {
                'defaultModel': prefs.default_model,
                'reasoningLevel': prefs.reasoning_level,
                'automationLevel': prefs.automation_level,
                'dailyTokenLimit': prefs.daily_token_limit,
                'monthlySpendingLimit': prefs.monthly_spending_limit,
                'memoryRetentionDays': prefs.memory_retention_days,
                'shareMemoryAcrossAgents': prefs.share_memory_across_agents,
            }
        })

    elif request.method == 'POST':
        # Update preferences
        prefs, created = UserPreferences.objects.get_or_create(user=user)
        data = request.data

        if 'defaultModel' in data:
            prefs.default_model = data['defaultModel']
        if 'reasoningLevel' in data:
            prefs.reasoning_level = data['reasoningLevel']
        if 'automationLevel' in data:
            prefs.automation_level = data['automationLevel']
        if 'dailyTokenLimit' in data:
            prefs.daily_token_limit = data['dailyTokenLimit']
        if 'monthlySpendingLimit' in data:
            prefs.monthly_spending_limit = data['monthlySpendingLimit']
        if 'memoryRetentionDays' in data:
            prefs.memory_retention_days = data['memoryRetentionDays']
        if 'shareMemoryAcrossAgents' in data:
            prefs.share_memory_across_agents = data['shareMemoryAcrossAgents']

        prefs.save()

        return Response({
            'success': True,
            'message': 'AI configuration updated successfully'
        })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsOperatorRole])  # S3052 PR 4 A2 fold: agents API is operator-only
def agents_assigned(request):
    """Get or update assigned agents for user"""
    user = request.user

    if request.method == 'GET':
        # Get assigned agents from user preferences
        prefs, created = UserPreferences.objects.get_or_create(user=user)

        # Default agents if none assigned
        default_agents = [
            {
                'agentName': 'Income Builder',
                'agentType': 'income_generation',
                'customModel': None,
                'canExecuteActions': True,
                'dailyActionLimit': 100,
                'tasksCompleted': 0,
                'successRate': 0,
                'lastActive': None,
            },
            {
                'agentName': 'Content Creator',
                'agentType': 'content_creation',
                'customModel': None,
                'canExecuteActions': True,
                'dailyActionLimit': 50,
                'tasksCompleted': 0,
                'successRate': 0,
                'lastActive': None,
            },
            {
                'agentName': 'Job Finder',
                'agentType': 'job_search',
                'customModel': None,
                'canExecuteActions': True,
                'dailyActionLimit': 200,
                'tasksCompleted': 0,
                'successRate': 0,
                'lastActive': None,
            }
        ]

        # Get assigned agents from preferences or use defaults
        assigned_agents = prefs.assigned_agents if hasattr(prefs, 'assigned_agents') and prefs.assigned_agents else default_agents

        return Response({
            'success': True,
            'data': assigned_agents
        })

    elif request.method == 'POST':
        # Update assigned agents
        prefs, created = UserPreferences.objects.get_or_create(user=user)
        prefs.assigned_agents = request.data.get('agents', [])
        prefs.save()

        return Response({
            'success': True,
            'message': 'Assigned agents updated successfully'
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_command(request):
    """Execute a command from the command center"""
    command = request.data.get('command', {})
    command_type = command.get('type')

    # Process different command types
    if command_type == 'agent.execute':
        agent_name = command.get('agent')
        task = command.get('task')
        return Response({
            'success': True,
            'message': f'Executing task with {agent_name}',
            'data': {
                'taskId': 'task_' + str(hash(task))[:8],
                'status': 'processing'
            }
        })

    elif command_type == 'profile.update':
        field = command.get('field')
        value = command.get('value')
        return Response({
            'success': True,
            'message': f'Profile field {field} updated',
        })

    elif command_type == 'ai.configure':
        setting = command.get('setting')
        value = command.get('value')
        return Response({
            'success': True,
            'message': f'AI setting {setting} updated to {value}',
        })

    else:
        return Response({
            'success': False,
            'message': f'Unknown command type: {command_type}',
        }, status=status.HTTP_400_BAD_REQUEST)


def calculate_profile_completion(profile):
    """Calculate profile completion percentage"""
    fields = [
        bool(profile.skills),
        profile.experience_years > 0,
        bool(profile.current_role),
        bool(profile.industries),
        bool(profile.portfolio_url or profile.linkedin_url or profile.github_url),
    ]
    completed = sum(1 for f in fields if f)
    return int((completed / len(fields)) * 100)