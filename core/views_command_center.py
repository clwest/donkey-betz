"""
Unified Command Center API Views
Handles profile management, AI configuration, and command execution
"""

import json
import logging
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import ValidationError

from persistence.models import UnifiedUser, UserMemoryContext
from agents.models import Agent
from core.unified_memory_manager import UnifiedMemoryManager
from backend.agents.orchestrator import AgentOrchestrator
from content.ai_providers import MultiAIProvider

logger = logging.getLogger(__name__)


class ProfileExtendedView(View):
    """Extended profile management with skills, preferences, and documents"""

    @method_decorator(login_required)
    def get(self, request):
        """Get complete user profile including extensions"""
        try:
            user = request.user
            profile_data = {
                'username': user.username,
                'email': user.email,
                'skills': getattr(user, 'skills', []),
                'experienceYears': getattr(user, 'experience_years', 0),
                'currentRole': getattr(user, 'current_role', ''),
                'industries': getattr(user, 'industries', []),
                'jobPreferences': {
                    'remote': getattr(user, 'prefer_remote', True),
                    'contract': getattr(user, 'prefer_contract', True),
                    'fullTime': getattr(user, 'prefer_full_time', False),
                    'hourlyRateMin': getattr(user, 'hourly_rate_min', 100),
                    'salaryMin': getattr(user, 'salary_min', 120000),
                },
                'resumeId': getattr(user, 'resume_id', None),
                'portfolioUrl': getattr(user, 'portfolio_url', ''),
                'linkedinUrl': getattr(user, 'linkedin_url', ''),
                'githubUrl': getattr(user, 'github_url', ''),
                'completionPercentage': self._calculate_completion(user),
            }

            return JsonResponse(profile_data)

        except Exception as e:
            logger.error(f"Error fetching profile: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def put(self, request):
        """Update user profile"""
        try:
            user = request.user
            data = json.loads(request.body)

            # Update user fields
            with transaction.atomic():
                # Update basic fields
                if 'skills' in data:
                    user.skills = data['skills']
                if 'experienceYears' in data:
                    user.experience_years = data['experienceYears']
                if 'currentRole' in data:
                    user.current_role = data['currentRole']
                if 'industries' in data:
                    user.industries = data['industries']

                # Update preferences
                if 'jobPreferences' in data:
                    prefs = data['jobPreferences']
                    user.prefer_remote = prefs.get('remote', True)
                    user.prefer_contract = prefs.get('contract', True)
                    user.prefer_full_time = prefs.get('fullTime', False)
                    user.hourly_rate_min = prefs.get('hourlyRateMin', 100)
                    user.salary_min = prefs.get('salaryMin', 120000)

                # Update links
                if 'portfolioUrl' in data:
                    user.portfolio_url = data['portfolioUrl']
                if 'linkedinUrl' in data:
                    user.linkedin_url = data['linkedinUrl']
                if 'githubUrl' in data:
                    user.github_url = data['githubUrl']

                user.save()

                # Store in memory for AI context
                memory_manager = UnifiedMemoryManager()
                memory_manager.store_memory(
                    user=user,
                    source='profile_update',
                    memory_type='profile_change',
                    content=f"User updated profile: {json.dumps(data)}",
                    metadata={'changes': data}
                )

            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully',
                'completionPercentage': self._calculate_completion(user)
            })

        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def _calculate_completion(self, user) -> int:
        """Calculate profile completion percentage"""
        fields = [
            bool(getattr(user, 'skills', [])),
            bool(getattr(user, 'experience_years', 0)),
            bool(getattr(user, 'current_role', '')),
            bool(getattr(user, 'industries', [])),
            bool(getattr(user, 'resume_id', None)),
            bool(getattr(user, 'portfolio_url', '')),
            bool(getattr(user, 'linkedin_url', '')),
        ]
        return int((sum(fields) / len(fields)) * 100)


class AIConfigurationView(View):
    """AI configuration management for user-specific settings"""

    @method_decorator(login_required)
    def get(self, request):
        """Get user's AI configuration"""
        try:
            user = request.user
            config = {
                'defaultModel': getattr(user, 'default_model', 'gpt-5-mini'),
                'reasoningLevel': getattr(user, 'reasoning_level', 'medium'),
                'automationLevel': getattr(user, 'automation_level', 'semi-auto'),
                'dailyTokenLimit': getattr(user, 'daily_token_limit', 100000),
                'monthlySpendingLimit': float(getattr(user, 'monthly_spending_limit', 50.00)),
                'memoryRetentionDays': getattr(user, 'memory_retention_days', 90),
                'shareMemoryAcrossAgents': getattr(user, 'share_memory_across_agents', True),
            }

            return JsonResponse(config)

        except Exception as e:
            logger.error(f"Error fetching AI config: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Update user's AI configuration"""
        try:
            user = request.user
            data = json.loads(request.body)

            with transaction.atomic():
                # Update AI settings
                if 'defaultModel' in data:
                    user.default_model = data['defaultModel']
                if 'reasoningLevel' in data:
                    user.reasoning_level = data['reasoningLevel']
                if 'automationLevel' in data:
                    user.automation_level = data['automationLevel']
                if 'dailyTokenLimit' in data:
                    user.daily_token_limit = data['dailyTokenLimit']
                if 'monthlySpendingLimit' in data:
                    user.monthly_spending_limit = Decimal(str(data['monthlySpendingLimit']))
                if 'memoryRetentionDays' in data:
                    user.memory_retention_days = data['memoryRetentionDays']
                if 'shareMemoryAcrossAgents' in data:
                    user.share_memory_across_agents = data['shareMemoryAcrossAgents']

                user.save()

                # Update agent configurations
                self._update_agent_configs(user, data)

                # Store configuration change in memory
                memory_manager = UnifiedMemoryManager()
                memory_manager.store_memory(
                    user=user,
                    source='ai_config',
                    memory_type='configuration',
                    content=f"AI configuration updated: {json.dumps(data)}",
                    metadata={'config': data}
                )

            return JsonResponse({
                'status': 'success',
                'message': 'AI configuration updated successfully'
            })

        except Exception as e:
            logger.error(f"Error updating AI config: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    def _update_agent_configs(self, user, config):
        """Update configurations for user's assigned agents"""
        try:
            # Get user's assigned agents
            assigned_agents = getattr(user, 'assigned_agents', [])
            if assigned_agents:
                Agent.objects.filter(
                    name__in=assigned_agents
                ).update(
                    llm_model=config.get('defaultModel', 'gpt-5-mini'),
                    updated_at=datetime.now()
                )
        except Exception as e:
            logger.error(f"Error updating agent configs: {str(e)}")


class AgentAssignmentView(View):
    """Manage user's agent assignments"""

    @method_decorator(login_required)
    def get(self, request):
        """Get user's assigned agents"""
        try:
            user = request.user
            assigned_agent_names = getattr(user, 'assigned_agents', [
                'income_builder',
                'career_advisor',
                'skill_matcher'
            ])

            # Get agent details
            agents = Agent.objects.filter(name__in=assigned_agent_names)

            agent_data = []
            for agent in agents:
                agent_data.append({
                    'agentName': agent.name,
                    'agentType': agent.category,
                    'customModel': agent.llm_model,
                    'canExecuteActions': getattr(agent, 'can_execute_actions', False),
                    'dailyActionLimit': getattr(agent, 'daily_action_limit', 10),
                    'tasksCompleted': getattr(agent, 'tasks_completed', 0),
                    'successRate': getattr(agent, 'success_rate', 0.85),
                    'lastActive': agent.updated_at.isoformat() if agent.updated_at else None,
                })

            return JsonResponse(agent_data, safe=False)

        except Exception as e:
            logger.error(f"Error fetching agents: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Assign an agent to user"""
        try:
            user = request.user
            data = json.loads(request.body)
            agent_name = data.get('agent_name')

            if not agent_name:
                return JsonResponse({'error': 'Agent name required'}, status=400)

            # Get current assignments
            assigned_agents = getattr(user, 'assigned_agents', [])
            if agent_name not in assigned_agents:
                assigned_agents.append(agent_name)
                user.assigned_agents = assigned_agents
                user.save()

            # Log assignment
            logger.info(f"Assigned agent {agent_name} to user {user.username}")

            return JsonResponse({
                'status': 'success',
                'message': f'Agent {agent_name} assigned successfully'
            })

        except Exception as e:
            logger.error(f"Error assigning agent: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def delete(self, request, agent_name):
        """Remove agent assignment"""
        try:
            user = request.user

            # Get current assignments
            assigned_agents = getattr(user, 'assigned_agents', [])
            if agent_name in assigned_agents:
                assigned_agents.remove(agent_name)
                user.assigned_agents = assigned_agents
                user.save()

            logger.info(f"Removed agent {agent_name} from user {user.username}")

            return JsonResponse({
                'status': 'success',
                'message': f'Agent {agent_name} removed successfully'
            })

        except Exception as e:
            logger.error(f"Error removing agent: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class CommandExecutionView(View):
    """Execute user commands through the unified system"""

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Execute a command with user context"""
        try:
            user = request.user
            data = json.loads(request.body)

            command_input = data.get('input', '')
            context = data.get('context', {})

            if not command_input:
                return JsonResponse({'error': 'Command input required'}, status=400)

            # Process command
            result = self._process_command(user, command_input, context)

            # Log command execution
            self._log_command(user, command_input, result)

            return JsonResponse({
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'data': result.get('data', {}),
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Command failed: {str(e)}',
                'error': str(e)
            }, status=500)

    def _process_command(self, user, command_input: str, context: Dict) -> Dict:
        """Process user command and return result"""
        try:
            # Determine command type
            command_lower = command_input.lower()

            if 'find' in command_lower and ('job' in command_lower or 'opportunit' in command_lower):
                return self._find_opportunities(user, command_input, context)

            elif 'analyze' in command_lower and 'profile' in command_lower:
                return self._analyze_profile(user)

            elif 'optimize' in command_lower and 'agent' in command_lower:
                return self._optimize_agents(user)

            elif 'generate' in command_lower and 'report' in command_lower:
                return self._generate_report(user, command_input)

            else:
                # Use AI to process general commands
                return self._ai_process_command(user, command_input, context)

        except Exception as e:
            logger.error(f"Command processing error: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to process command: {str(e)}'
            }

    def _find_opportunities(self, user, command: str, context: Dict) -> Dict:
        """Find opportunities based on user profile and command"""
        try:
            # Use agent orchestrator to find opportunities
            orchestrator = AgentOrchestrator()

            # Get user's skills and preferences
            skills = getattr(user, 'skills', [])
            hourly_min = getattr(user, 'hourly_rate_min', 100)

            # Execute opportunity search
            opportunities = orchestrator.find_opportunities(
                skills=skills,
                min_rate=hourly_min,
                additional_criteria=command
            )

            return {
                'success': True,
                'message': f'Found {len(opportunities)} matching opportunities',
                'data': {
                    'opportunities': opportunities[:10],  # Limit to 10
                    'total': len(opportunities)
                }
            }

        except Exception as e:
            logger.error(f"Error finding opportunities: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to find opportunities'
            }

    def _analyze_profile(self, user) -> Dict:
        """Analyze user profile completeness and provide recommendations"""
        try:
            analysis = {
                'completeness': self._calculate_profile_score(user),
                'missing_fields': self._get_missing_fields(user),
                'recommendations': self._get_profile_recommendations(user),
                'strengths': self._analyze_strengths(user)
            }

            return {
                'success': True,
                'message': 'Profile analysis complete',
                'data': analysis
            }

        except Exception as e:
            logger.error(f"Error analyzing profile: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to analyze profile'
            }

    def _optimize_agents(self, user) -> Dict:
        """Optimize agent assignments based on user profile"""
        try:
            skills = getattr(user, 'skills', [])
            current_role = getattr(user, 'current_role', '')

            # Recommend agents based on profile
            recommended_agents = []

            if 'python' in [s.lower() for s in skills]:
                recommended_agents.append('python_specialist')
            if 'javascript' in [s.lower() for s in skills]:
                recommended_agents.append('frontend_expert')
            if current_role and 'senior' in current_role.lower():
                recommended_agents.append('senior_advisor')
            if getattr(user, 'prefer_contract', False):
                recommended_agents.append('contract_negotiator')

            # Always include core agents
            core_agents = ['income_builder', 'career_advisor', 'skill_matcher']
            recommended_agents.extend(core_agents)

            # Update user's agents
            user.assigned_agents = list(set(recommended_agents))
            user.save()

            return {
                'success': True,
                'message': f'Optimized to {len(recommended_agents)} agents',
                'data': {
                    'assigned_agents': recommended_agents,
                    'recommendations': 'Agents optimized based on your skills and preferences'
                }
            }

        except Exception as e:
            logger.error(f"Error optimizing agents: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to optimize agents'
            }

    def _generate_report(self, user, command: str) -> Dict:
        """Generate various reports based on command"""
        try:
            report_type = 'general'
            if 'income' in command.lower():
                report_type = 'income'
            elif 'activity' in command.lower():
                report_type = 'activity'

            report_data = {
                'user': user.username,
                'generated_at': datetime.now().isoformat(),
                'type': report_type
            }

            if report_type == 'income':
                # Get income data from memory
                memories = UserMemoryContext.objects.filter(
                    user=user,
                    memory_type='earning'
                ).order_by('-created_at')[:30]

                total_earnings = sum([
                    m.metadata.get('amount', 0) for m in memories
                    if m.metadata
                ])

                report_data['earnings'] = {
                    'total': total_earnings,
                    'period': '30 days',
                    'transactions': len(memories)
                }

            return {
                'success': True,
                'message': f'{report_type.title()} report generated',
                'data': report_data
            }

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to generate report'
            }

    def _ai_process_command(self, user, command: str, context: Dict) -> Dict:
        """Use AI to process general commands"""
        try:
            # Initialize AI provider
            ai_provider = MultiAIProvider()

            # Build prompt with user context
            prompt = f"""
            Process this user command with their context:

            Command: {command}

            User Context:
            - Skills: {getattr(user, 'skills', [])}
            - Experience: {getattr(user, 'experience_years', 0)} years
            - Preferences: Remote={getattr(user, 'prefer_remote', True)},
                         Min Rate=${getattr(user, 'hourly_rate_min', 100)}/hr

            Provide a helpful response and any actions taken.
            """

            # Get AI response
            response = ai_provider.chat_completion(
                model=getattr(user, 'default_model', 'gpt-5-mini'),
                messages=[{'role': 'user', 'content': prompt}]
            )

            return {
                'success': True,
                'message': 'Command processed',
                'data': {
                    'response': response.get('content', ''),
                    'tokens_used': response.get('usage', {}).get('total_tokens', 0)
                }
            }

        except Exception as e:
            logger.error(f"Error in AI processing: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to process command with AI'
            }

    def _log_command(self, user, command: str, result: Dict):
        """Log command execution for audit and learning"""
        try:
            memory_manager = UnifiedMemoryManager()
            memory_manager.store_memory(
                user=user,
                source='command_center',
                memory_type='command_execution',
                content=command,
                metadata={
                    'result': result,
                    'success': result.get('success', False),
                    'timestamp': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error logging command: {str(e)}")

    def _calculate_profile_score(self, user) -> int:
        """Calculate overall profile score"""
        scores = {
            'skills': len(getattr(user, 'skills', [])) * 5,
            'experience': min(getattr(user, 'experience_years', 0) * 3, 30),
            'links': sum([
                bool(getattr(user, 'portfolio_url', '')),
                bool(getattr(user, 'linkedin_url', '')),
                bool(getattr(user, 'github_url', ''))
            ]) * 10,
            'preferences': 20 if hasattr(user, 'hourly_rate_min') else 0,
            'resume': 20 if getattr(user, 'resume_id', None) else 0
        }
        return min(sum(scores.values()), 100)

    def _get_missing_fields(self, user) -> List[str]:
        """Get list of missing profile fields"""
        missing = []

        if not getattr(user, 'skills', []):
            missing.append('Skills')
        if not getattr(user, 'experience_years', 0):
            missing.append('Experience')
        if not getattr(user, 'current_role', ''):
            missing.append('Current Role')
        if not getattr(user, 'resume_id', None):
            missing.append('Resume')
        if not getattr(user, 'linkedin_url', ''):
            missing.append('LinkedIn')

        return missing

    def _get_profile_recommendations(self, user) -> List[str]:
        """Get profile improvement recommendations"""
        recommendations = []

        skills_count = len(getattr(user, 'skills', []))
        if skills_count < 5:
            recommendations.append(f"Add {5 - skills_count} more skills to improve matching")

        if not getattr(user, 'resume_id', None):
            recommendations.append("Upload your resume for Quick Apply feature")

        if not getattr(user, 'portfolio_url', ''):
            recommendations.append("Add portfolio URL to showcase your work")

        return recommendations

    def _analyze_strengths(self, user) -> List[str]:
        """Analyze user strengths from profile"""
        strengths = []

        if len(getattr(user, 'skills', [])) > 5:
            strengths.append("Diverse skill set")

        if getattr(user, 'experience_years', 0) > 5:
            strengths.append("Experienced professional")

        if getattr(user, 'github_url', ''):
            strengths.append("Active open source contributor")

        return strengths


# URL Configuration
urlpatterns = [
    path('api/profile/extended/', ProfileExtendedView.as_view(), name='profile_extended'),
    path('api/ai/configuration/', AIConfigurationView.as_view(), name='ai_configuration'),
    path('api/agents/assigned/', AgentAssignmentView.as_view(), name='agents_assigned'),
    path('api/agents/assign/', AgentAssignmentView.as_view(), name='agent_assign'),
    path('api/agents/<str:agent_name>/', AgentAssignmentView.as_view(), name='agent_remove'),
    path('api/commands/execute/', CommandExecutionView.as_view(), name='command_execute'),
]