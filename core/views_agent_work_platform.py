"""
API Views for Agent Work Platform
Where agents actually execute jobs and generate revenue
"""

import json
import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views import View
from backend.agents.agent_work_platform import activate_agent_work_platform, get_agent_work_platform_status
import asyncio

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AgentWorkPlatformView(View):
    """Main API for agent work platform"""

    async def get(self, request):
        """Get platform status and metrics"""
        try:
            status = get_agent_work_platform_status()

            # Get cached work sessions and revenue data
            active_sessions = cache.get('active_work_sessions', [])
            total_revenue = cache.get('platform_total_revenue', 0.0)
            executable_jobs = cache.get('executable_jobs', [])

            return JsonResponse({
                'success': True,
                'platform_status': status,
                'active_work_sessions': active_sessions,
                'total_revenue': total_revenue,
                'executable_jobs_count': len(executable_jobs),
                'message': 'Agent work platform status retrieved successfully'
            })

        except Exception as e:
            logger.error(f"Error getting agent work platform status: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    async def post(self, request):
        """Activate the agent work platform to start making money"""
        try:
            # Parse request data
            data = json.loads(request.body) if request.body else {}

            logger.info("🚀 Activating Agent Work Platform...")

            # Activate the platform
            result = await activate_agent_work_platform()

            if result.get('success'):
                logger.info(f"✅ Platform activated successfully!")
                logger.info(f"   💰 Potential revenue: ${result.get('potential_revenue', 0):,.2f}")
                logger.info(f"   🤖 Agents working: {result.get('agents_working', 0)}")

                return JsonResponse({
                    'success': True,
                    'platform_activation': result,
                    'message': f"Platform activated! {result.get('jobs_assigned_to_agents', 0)} agents now working on jobs"
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Platform activation failed'),
                    'platform_activation': result
                }, status=500)

        except Exception as e:
            logger.error(f"Error activating agent work platform: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def agent_revenue_dashboard(request):
    """Get revenue dashboard data"""
    try:
        # Get revenue data from cache
        total_revenue = cache.get('platform_total_revenue', 0.0)
        active_sessions = cache.get('active_work_sessions', [])
        executable_jobs = cache.get('executable_jobs', [])

        # Calculate metrics
        revenue_by_agent = {}
        revenue_by_capability = {}

        for session in active_sessions:
            agent_id = session.get('agent_id', 'unknown')
            revenue = session.get('revenue_earned', 0.0)

            if agent_id not in revenue_by_agent:
                revenue_by_agent[agent_id] = 0.0
            revenue_by_agent[agent_id] += revenue

        # Calculate potential revenue by job type
        for job in executable_jobs:
            capabilities = job.get('required_capabilities', [])
            revenue_potential = job.get('revenue_potential', 0.0)

            for capability in capabilities:
                if capability not in revenue_by_capability:
                    revenue_by_capability[capability] = 0.0
                revenue_by_capability[capability] += revenue_potential

        # Top earning opportunities
        top_opportunities = sorted(
            executable_jobs,
            key=lambda x: x.get('revenue_potential', 0),
            reverse=True
        )[:5]

        dashboard_data = {
            'total_revenue': total_revenue,
            'active_revenue_streams': len(active_sessions),
            'total_executable_jobs': len(executable_jobs),
            'revenue_by_agent': revenue_by_agent,
            'revenue_by_capability': revenue_by_capability,
            'top_opportunities': top_opportunities,
            'daily_revenue_potential': sum(job.get('revenue_potential', 0) for job in executable_jobs),
            'active_work_sessions': len(active_sessions)
        }

        return JsonResponse({
            'success': True,
            'dashboard': dashboard_data,
            'message': 'Revenue dashboard data retrieved successfully'
        })

    except Exception as e:
        logger.error(f"Error getting revenue dashboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def agent_workforce_status(request):
    """Get detailed workforce status"""
    try:
        status = get_agent_work_platform_status()

        # Get additional metrics
        active_sessions = cache.get('active_work_sessions', [])

        # Calculate session progress
        total_progress = 0.0
        sessions_with_progress = 0

        for session in active_sessions:
            progress = session.get('progress', 0.0)
            if progress > 0:
                total_progress += progress
                sessions_with_progress += 1

        average_progress = (total_progress / sessions_with_progress) if sessions_with_progress > 0 else 0.0

        workforce_data = {
            'agent_status': status,
            'active_sessions_count': len(active_sessions),
            'average_job_progress': average_progress,
            'sessions_in_progress': [
                {
                    'session_id': session.get('session_id'),
                    'agent_id': session.get('agent_id'),
                    'job_id': session.get('job_id'),
                    'progress': session.get('progress', 0.0),
                    'status': session.get('status'),
                    'revenue_earned': session.get('revenue_earned', 0.0),
                    'estimated_completion': session.get('estimated_completion')
                }
                for session in active_sessions
            ]
        }

        return JsonResponse({
            'success': True,
            'workforce': workforce_data,
            'message': 'Workforce status retrieved successfully'
        })

    except Exception as e:
        logger.error(f"Error getting workforce status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def assign_specific_job(request):
    """Manually assign a specific job to an agent"""
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        preferred_agent = data.get('agent_id')  # Optional

        executable_jobs = cache.get('executable_jobs', [])

        # Find the job
        target_job = None
        for job in executable_jobs:
            if job.get('opportunity_id') == job_id:
                target_job = job
                break

        if not target_job:
            return JsonResponse({
                'success': False,
                'error': f'Job {job_id} not found'
            }, status=404)

        if target_job.get('status') != 'available':
            return JsonResponse({
                'success': False,
                'error': f'Job {job_id} is not available (status: {target_job.get("status")})'
            }, status=400)

        # TODO: Implement manual job assignment logic
        # For now, return success message
        return JsonResponse({
            'success': True,
            'message': f'Job {job_id} assignment initiated',
            'job': target_job
        })

    except Exception as e:
        logger.error(f"Error assigning specific job: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def revenue_analytics(request):
    """Get detailed revenue analytics"""
    try:
        # Get all revenue data
        total_revenue = cache.get('platform_total_revenue', 0.0)
        active_sessions = cache.get('active_work_sessions', [])
        executable_jobs = cache.get('executable_jobs', [])

        # Calculate analytics
        analytics = {
            'current_revenue': total_revenue,
            'potential_revenue': sum(job.get('revenue_potential', 0) for job in executable_jobs),
            'revenue_in_progress': sum(session.get('revenue_earned', 0) for session in active_sessions),
            'average_job_value': 0.0,
            'highest_value_job': 0.0,
            'revenue_by_complexity': {
                'beginner': 0.0,
                'intermediate': 0.0,
                'advanced': 0.0
            },
            'jobs_by_status': {
                'available': 0,
                'assigned': 0,
                'in_progress': 0,
                'completed': 0
            }
        }

        if executable_jobs:
            analytics['average_job_value'] = sum(job.get('revenue_potential', 0) for job in executable_jobs) / len(executable_jobs)
            analytics['highest_value_job'] = max(job.get('revenue_potential', 0) for job in executable_jobs)

            # Revenue by complexity
            for job in executable_jobs:
                complexity = job.get('complexity_level', 'intermediate')
                revenue = job.get('revenue_potential', 0.0)
                if complexity in analytics['revenue_by_complexity']:
                    analytics['revenue_by_complexity'][complexity] += revenue

            # Jobs by status
            for job in executable_jobs:
                status = job.get('status', 'available')
                if status in analytics['jobs_by_status']:
                    analytics['jobs_by_status'][status] += 1

        return JsonResponse({
            'success': True,
            'analytics': analytics,
            'message': 'Revenue analytics retrieved successfully'
        })

    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Async view wrapper
async def async_agent_work_platform_view(request):
    """Async wrapper for agent work platform view"""
    view = AgentWorkPlatformView()
    if request.method == 'GET':
        return await view.get(request)
    elif request.method == 'POST':
        return await view.post(request)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)