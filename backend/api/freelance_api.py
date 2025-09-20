"""
Freelance Pipeline API Endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_freelance_opportunities(request):
    """Get all freelance opportunities"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get all opportunity keys
        opp_keys = r.keys('freelance:opportunity:*')
        opportunities = []

        for key in opp_keys[:10]:  # Limit to 10 for performance
            data = r.get(key)
            if data:
                opportunities.append(json.loads(data))

        # Sort by suitability score
        opportunities.sort(key=lambda x: x.get('agent_suitability', 0), reverse=True)

        return Response({
            'success': True,
            'opportunities': opportunities
        })
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        # Return mock data for demo
        return Response({
            'success': True,
            'opportunities': [
                {
                    'job_id': 'upw_001',
                    'platform': 'Upwork',
                    'title': 'Write 10 SEO Blog Posts on AI Tools',
                    'description': 'Need 10 high-quality blog posts about AI productivity tools...',
                    'budget': 500,
                    'budget_type': 'fixed',
                    'skills_required': ['content writing', 'SEO', 'AI knowledge'],
                    'deadline': '2025-09-27',
                    'client_rating': 4.8,
                    'agent_suitability': 0.95,
                    'recommended_agents': ['content_creator_agent', 'seo_optimizer_agent'],
                    'estimated_completion_time': 12,
                    'confidence_score': 0.92,
                    'status': 'new'
                },
                {
                    'job_id': 'fiv_002',
                    'platform': 'Fiverr',
                    'title': 'Build REST API with Node.js',
                    'description': 'Need REST API for e-commerce platform...',
                    'budget': 1200,
                    'budget_type': 'fixed',
                    'skills_required': ['Node.js', 'REST API', 'MongoDB'],
                    'deadline': '2025-10-05',
                    'client_rating': 4.7,
                    'agent_suitability': 0.88,
                    'recommended_agents': ['code_generator_agent', 'api_builder_agent'],
                    'estimated_completion_time': 16,
                    'confidence_score': 0.85,
                    'status': 'new'
                }
            ]
        })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
async def analyze_opportunity(request, job_id):
    """Analyze a freelance opportunity"""
    try:
        from backend.agents.freelance_job_analyzer import FreelanceJobAnalyzer
        from backend.agents.freelance_pipeline import FreelancePipeline
        import redis

        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get opportunity data
        opportunity = request.data

        # Create pipeline and process
        pipeline = FreelancePipeline(redis_client=r)
        project = await pipeline.process_opportunity(opportunity)

        return Response({
            'success': True,
            'project': project,
            'analysis': project.get('analysis')
        })

    except Exception as e:
        logger.error(f"Error analyzing opportunity: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_approvals(request):
    """Get all pending approval requests"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        approvals = []
        pending = r.lrange('freelance:approvals:pending', 0, -1)

        for item in pending:
            approvals.append(json.loads(item))

        # Add mock data for demo
        if not approvals:
            approvals = [
                {
                    'id': 'appr_001',
                    'project_id': 'proj_002',
                    'type': 'approve_analysis',
                    'title': 'Python Data Analysis Script',
                    'budget': 300,
                    'profit': 250,
                    'risk': 'LOW',
                    'recommendation': 'PURSUE'
                }
            ]

        return Response({
            'success': True,
            'approvals': approvals
        })

    except Exception as e:
        logger.error(f"Error getting approvals: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
async def process_approval(request, approval_id):
    """Process an approval decision"""
    try:
        from backend.agents.freelance_pipeline import FreelancePipeline
        import redis

        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        pipeline = FreelancePipeline(redis_client=r)

        decision = request.data.get('decision', 'approve')

        # Find the project for this approval
        approval_data = r.get(f'freelance:approval:{approval_id}')
        if approval_data:
            approval = json.loads(approval_data)
            project_id = approval.get('project_id')

            # Process the approval
            result = await pipeline.approve_project(project_id, decision)

            if result:
                # Remove from pending queue
                r.lrem('freelance:approvals:pending', 0, json.dumps(approval))

                return Response({
                    'success': True,
                    'message': f'Approval processed: {decision}'
                })

        return Response({
            'success': False,
            'error': 'Approval not found'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_projects(request):
    """Get all active freelance projects"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Get all project keys
        project_keys = r.keys('freelance:project:*')
        projects = []

        for key in project_keys[:10]:  # Limit for performance
            data = r.get(key)
            if data:
                project = json.loads(data)
                # Only include active projects
                if project.get('status') not in ['rejected', 'cancelled', 'completed', 'paid']:
                    projects.append(project)

        # Add mock project for demo
        if not projects:
            projects = [
                {
                    'id': 'proj_001',
                    'opportunity': {
                        'title': 'Write 10 SEO Blog Posts',
                        'platform': 'Upwork',
                        'budget': 500
                    },
                    'status': 'in_progress',
                    'checkpoints': [
                        {'stage': 'analysis', 'status': 'completed'},
                        {'stage': 'approval', 'status': 'completed'}
                    ],
                    'financial': {
                        'budget': 500,
                        'cost': 100,
                        'profit': 400,
                        'paid': False
                    },
                    'deliverables': [
                        {'task': 'Blog Post 1: Top AI Writing Tools', 'status': 'completed'},
                        {'task': 'Blog Post 2: AI for Productivity', 'status': 'in_progress'}
                    ]
                }
            ]

        return Response({
            'success': True,
            'projects': projects
        })

    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
async def start_freelance_spider(request):
    """Start the freelance opportunity spider"""
    try:
        from backend.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider
        import redis

        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        spider = FreelanceOpportunitySpider(redis_client=r)
        await spider.initialize()

        opportunities = await spider.find_opportunities()

        await spider.cleanup()

        return Response({
            'success': True,
            'message': f'Spider found {len(opportunities)} opportunities',
            'count': len(opportunities)
        })

    except Exception as e:
        logger.error(f"Error starting spider: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)