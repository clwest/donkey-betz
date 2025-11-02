"""
Learning Journey API Views
Manages user learning paths with progress tracking and step completion
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import json
import uuid
import logging

from core.models_unified_system import (
    Agent, AgentSolution, AgentLearning, SpiderData
)

logger = logging.getLogger(__name__)

# In-memory storage for learning journeys (would be a model in production)
ACTIVE_JOURNEYS = {}


class LearningJourney:
    """Represents a user's learning journey with steps and progress"""

    def __init__(self, user_id, goals, skills):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.goals = goals
        self.skills = skills
        self.created_at = datetime.now()
        self.current_step = 0
        self.completed_steps = []
        self.status = 'active'

        # Generate personalized steps based on user profile
        self.steps = self._generate_steps()

    def _generate_steps(self):
        """Generate personalized learning steps"""
        steps = []

        # Step 1: Assessment
        steps.append({
            'id': 1,
            'title': 'Initial Assessment',
            'description': 'Evaluate current knowledge level',
            'type': 'assessment',
            'status': 'pending',
            'estimated_time': 15,
            'tasks': [
                'Complete skill assessment quiz',
                'Review your learning goals',
                'Set learning pace preferences'
            ],
            'resources': [],
            'started_at': None,
            'completed_at': None
        })

        # Step 2: Foundation
        steps.append({
            'id': 2,
            'title': 'Build Foundation',
            'description': 'Master fundamental concepts',
            'type': 'learning',
            'status': 'locked',
            'estimated_time': 60,
            'tasks': [
                'Study core concepts',
                'Complete interactive tutorials',
                'Review agent-generated solutions'
            ],
            'resources': [],
            'started_at': None,
            'completed_at': None
        })

        # Step 3: Practice
        steps.append({
            'id': 3,
            'title': 'Hands-on Practice',
            'description': 'Apply knowledge through exercises',
            'type': 'practice',
            'status': 'locked',
            'estimated_time': 90,
            'tasks': [
                'Complete coding challenges',
                'Build mini-projects',
                'Get feedback from AI agents'
            ],
            'resources': [],
            'started_at': None,
            'completed_at': None
        })

        # Step 4: Real Application
        steps.append({
            'id': 4,
            'title': 'Real-World Application',
            'description': 'Work on actual projects',
            'type': 'project',
            'status': 'locked',
            'estimated_time': 120,
            'tasks': [
                'Select a real project',
                'Apply learned solutions',
                'Track implementation progress'
            ],
            'resources': [],
            'started_at': None,
            'completed_at': None
        })

        # Step 5: Mastery
        steps.append({
            'id': 5,
            'title': 'Achieve Mastery',
            'description': 'Advanced topics and specialization',
            'type': 'mastery',
            'status': 'locked',
            'estimated_time': 180,
            'tasks': [
                'Explore advanced concepts',
                'Create your own solutions',
                'Mentor others in the community'
            ],
            'resources': [],
            'started_at': None,
            'completed_at': None
        })

        return steps

    def start_step(self, step_id):
        """Start a specific step in the journey"""
        for step in self.steps:
            if step['id'] == step_id:
                if step['status'] == 'locked':
                    return {'success': False, 'error': 'Step is locked'}

                step['status'] = 'in_progress'
                step['started_at'] = datetime.now().isoformat()
                self.current_step = step_id

                # Assign relevant solutions and agents
                self._assign_resources(step)

                return {'success': True, 'step': step}

        return {'success': False, 'error': 'Step not found'}

    def complete_step(self, step_id, results=None):
        """Mark a step as completed"""
        for i, step in enumerate(self.steps):
            if step['id'] == step_id:
                if step['status'] != 'in_progress':
                    return {'success': False, 'error': 'Step not in progress'}

                step['status'] = 'completed'
                step['completed_at'] = datetime.now().isoformat()
                step['results'] = results or {}

                self.completed_steps.append(step_id)

                # Unlock next step
                if i + 1 < len(self.steps):
                    self.steps[i + 1]['status'] = 'pending'

                # Check if journey is complete
                if len(self.completed_steps) == len(self.steps):
                    self.status = 'completed'

                return {'success': True, 'step': step, 'journey_complete': self.status == 'completed'}

        return {'success': False, 'error': 'Step not found'}

    def _assign_resources(self, step):
        """Assign relevant solutions and agents to a step"""
        try:
            # Get relevant solutions based on step type
            if step['type'] == 'learning':
                solutions = AgentSolution.objects.filter(
                    solution_type__in=['tutorial', 'explanation', 'guide']
                ).order_by('-success_rate')[:5]
            elif step['type'] == 'practice':
                solutions = AgentSolution.objects.filter(
                    solution_type__in=['exercise', 'challenge', 'practice']
                ).order_by('-times_used')[:5]
            elif step['type'] == 'project':
                solutions = AgentSolution.objects.filter(
                    solution_type__in=['project', 'implementation', 'application']
                ).order_by('-success_rate')[:3]
            else:
                solutions = AgentSolution.objects.order_by('?')[:3]

            step['resources'] = [
                {
                    'type': 'solution',
                    'id': str(sol.id),
                    'title': sol.title,
                    'description': sol.description[:100]
                }
                for sol in solutions
            ]

            # Add relevant agents
            agents = Agent.objects.filter(is_active=True).order_by('?')[:2]
            for agent in agents:
                step['resources'].append({
                    'type': 'agent',
                    'id': str(agent.id),
                    'name': agent.name,
                    'specialty': agent.specialization
                })

        except Exception as e:
            logger.error(f"Error assigning resources: {e}")

    def get_progress(self):
        """Calculate overall progress percentage"""
        return {
            'completed': len(self.completed_steps),
            'total': len(self.steps),
            'percentage': (len(self.completed_steps) / len(self.steps)) * 100,
            'current_step': self.current_step,
            'time_spent': self._calculate_time_spent(),
            'estimated_remaining': self._estimate_remaining_time()
        }

    def _calculate_time_spent(self):
        """Calculate total time spent on journey"""
        total_minutes = 0
        for step in self.steps:
            if step['started_at'] and step['completed_at']:
                start = datetime.fromisoformat(step['started_at'])
                end = datetime.fromisoformat(step['completed_at'])
                total_minutes += (end - start).total_seconds() / 60
        return int(total_minutes)

    def _estimate_remaining_time(self):
        """Estimate remaining time to complete journey"""
        remaining = 0
        for step in self.steps:
            if step['status'] in ['pending', 'locked']:
                remaining += step['estimated_time']
        return remaining

    def to_dict(self):
        """Convert journey to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'current_step': self.current_step,
            'steps': self.steps,
            'progress': self.get_progress(),
            'created_at': self.created_at.isoformat(),
            'goals': self.goals,
            'skills': self.skills
        }


@require_http_methods(["POST"])
@csrf_exempt
def start_learning_journey(request):
    """Start a new learning journey for the user"""
    try:
        data = json.loads(request.body or b"{}")
        user_id = data.get('user_id', 'default_user')
        goals = data.get('goals', [])
        skills = data.get('skills', [])

        # Create new journey
        journey = LearningJourney(user_id, goals, skills)
        ACTIVE_JOURNEYS[journey.id] = journey

        # Start first step automatically
        journey.start_step(1)

        return JsonResponse({
            'success': True,
            'journey': journey.to_dict(),
            'message': 'Learning journey started! Begin with your initial assessment.'
        })

    except Exception as e:
        logger.error(f"Error starting journey: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_journey_status(request, journey_id):
    """Get current status of a learning journey"""
    try:
        if journey_id not in ACTIVE_JOURNEYS:
            return JsonResponse({
                'success': False,
                'error': 'Journey not found'
            }, status=404)

        journey = ACTIVE_JOURNEYS[journey_id]
        return JsonResponse({
            'success': True,
            'journey': journey.to_dict()
        })

    except Exception as e:
        logger.error(f"Error getting journey status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def start_journey_step(request, journey_id, step_id):
    """Start a specific step in the journey"""
    try:
        if journey_id not in ACTIVE_JOURNEYS:
            return JsonResponse({
                'success': False,
                'error': 'Journey not found'
            }, status=404)

        journey = ACTIVE_JOURNEYS[journey_id]
        result = journey.start_step(int(step_id))

        if result['success']:
            return JsonResponse({
                'success': True,
                'step': result['step'],
                'message': f"Started: {result['step']['title']}"
            })
        else:
            return JsonResponse(result, status=400)

    except Exception as e:
        logger.error(f"Error starting step: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def complete_journey_step(request, journey_id, step_id):
    """Mark a step as completed"""
    try:
        if journey_id not in ACTIVE_JOURNEYS:
            return JsonResponse({
                'success': False,
                'error': 'Journey not found'
            }, status=404)

        data = json.loads(request.body or b"{}")
        results = data.get('results', {})

        journey = ACTIVE_JOURNEYS[journey_id]
        result = journey.complete_step(int(step_id), results)

        if result['success']:
            message = "Journey completed! 🎉" if result.get('journey_complete') else f"Completed: {result['step']['title']}"

            return JsonResponse({
                'success': True,
                'step': result['step'],
                'journey_complete': result.get('journey_complete', False),
                'progress': journey.get_progress(),
                'message': message
            })
        else:
            return JsonResponse(result, status=400)

    except Exception as e:
        logger.error(f"Error completing step: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_active_journeys(request):
    """Get all active learning journeys for a user"""
    try:
        user_id = request.GET.get('user_id', 'default_user')

        user_journeys = [
            journey.to_dict()
            for journey in ACTIVE_JOURNEYS.values()
            if journey.user_id == user_id
        ]

        return JsonResponse({
            'success': True,
            'journeys': user_journeys,
            'count': len(user_journeys)
        })

    except Exception as e:
        logger.error(f"Error getting active journeys: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def reset_journey(request, journey_id):
    """Reset a learning journey to start over"""
    try:
        if journey_id not in ACTIVE_JOURNEYS:
            return JsonResponse({
                'success': False,
                'error': 'Journey not found'
            }, status=404)

        old_journey = ACTIVE_JOURNEYS[journey_id]

        # Create new journey with same goals/skills
        new_journey = LearningJourney(
            old_journey.user_id,
            old_journey.goals,
            old_journey.skills
        )

        # Replace old journey
        del ACTIVE_JOURNEYS[journey_id]
        ACTIVE_JOURNEYS[new_journey.id] = new_journey

        # Start first step
        new_journey.start_step(1)

        return JsonResponse({
            'success': True,
            'journey': new_journey.to_dict(),
            'message': 'Journey reset successfully! Starting fresh.'
        })

    except Exception as e:
        logger.error(f"Error resetting journey: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)