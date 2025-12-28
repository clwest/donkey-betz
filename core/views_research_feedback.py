"""
Session 326: Research Feedback API Views

API endpoints for submitting and managing research feedback.
Enables the user feedback loop that trains the agent learning system.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

import json

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def submit_research_feedback(request):
    """
    Submit feedback on research results.

    POST /api/research/feedback/

    Request Body:
    {
        "project_id": "uuid",
        "research_id": "uuid" (optional),
        "feedback_type": "accept" | "reject" | "partial" | "starred",
        "rating": 1-5,
        "reason": "Optional explanation",
        "context": {"section": "competitors", "item": "Jasper AI"}
    }

    Returns:
    {
        "success": true,
        "feedback_id": "uuid",
        "knowledge_impact": {
            "updated_sources": 3,
            "avg_confidence_delta": -0.15
        }
    }
    """
    from core.models_unified_system import (
        ProjectResearchFeedback,
        PartnershipProject,
        BusinessResearchResult,
    )
    from core.services.project_research_bridge import get_project_research_bridge
    from core.tasks import process_research_feedback

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Validate required fields
    project_id = data.get('project_id')
    feedback_type = data.get('feedback_type')

    if not project_id:
        return JsonResponse({'error': 'project_id is required'}, status=400)

    if feedback_type not in ['accept', 'reject', 'partial', 'starred']:
        return JsonResponse({'error': 'Invalid feedback_type'}, status=400)

    # Get project
    try:
        project = PartnershipProject.objects.get(id=project_id)
    except PartnershipProject.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    # Get research if provided
    research = None
    research_id = data.get('research_id')
    if research_id:
        try:
            research = BusinessResearchResult.objects.get(id=research_id)
        except BusinessResearchResult.DoesNotExist:
            return JsonResponse({'error': 'Research not found'}, status=404)

    # Get user (anonymous if not authenticated)
    user = request.user if request.user.is_authenticated else None
    if not user:
        # Create or get anonymous user for feedback
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='anonymous_feedback',
            defaults={'email': 'anonymous@feedback.local'}
        )

    # Create feedback
    feedback = ProjectResearchFeedback.objects.create(
        project=project,
        research=research,
        user=user,
        feedback_type=feedback_type,
        rating=data.get('rating', 3),
        reason=data.get('reason', ''),
        feedback_context=data.get('context', {}),
    )

    # Process feedback asynchronously
    process_research_feedback.delay(str(feedback.id))

    # Get immediate knowledge impact estimate
    bridge = get_project_research_bridge()
    confidence_delta = bridge.FEEDBACK_CONFIDENCE_DELTA.get(feedback_type, 0.0)

    return JsonResponse({
        'success': True,
        'feedback_id': str(feedback.id),
        'feedback_type': feedback_type,
        'knowledge_impact': {
            'estimated_delta': confidence_delta,
            'processing': 'async',
        }
    })


@require_http_methods(["GET"])
def get_research_feedback(request, research_id):
    """
    Get all feedback for a specific research result.

    GET /api/research/{research_id}/feedback/

    Returns:
    {
        "research_id": "uuid",
        "feedback_count": 5,
        "feedback": [
            {
                "id": "uuid",
                "feedback_type": "accept",
                "rating": 4,
                "reason": "Great insights",
                "created_at": "2025-12-03T..."
            }
        ],
        "summary": {
            "accept": 3,
            "reject": 1,
            "starred": 1,
            "avg_rating": 4.2
        }
    }
    """
    from core.models_unified_system import (
        ProjectResearchFeedback,
        BusinessResearchResult,
    )
    from django.db.models import Avg, Count

    try:
        research = BusinessResearchResult.objects.get(id=research_id)
    except BusinessResearchResult.DoesNotExist:
        return JsonResponse({'error': 'Research not found'}, status=404)

    feedback_qs = ProjectResearchFeedback.objects.filter(research=research)

    # Get summary
    summary = feedback_qs.aggregate(
        avg_rating=Avg('rating'),
        total=Count('id'),
    )

    # Get counts by type
    type_counts = feedback_qs.values('feedback_type').annotate(count=Count('id'))
    type_summary = {tc['feedback_type']: tc['count'] for tc in type_counts}

    # Get individual feedback entries
    feedback_list = []
    for fb in feedback_qs.order_by('-created_at')[:20]:
        feedback_list.append({
            'id': str(fb.id),
            'feedback_type': fb.feedback_type,
            'rating': fb.rating,
            'reason': fb.reason,
            'applied': fb.applied_to_knowledge,
            'created_at': fb.created_at.isoformat(),
        })

    return JsonResponse({
        'research_id': str(research_id),
        'feedback_count': summary['total'] or 0,
        'feedback': feedback_list,
        'summary': {
            **type_summary,
            'avg_rating': round(summary['avg_rating'] or 0, 2),
        }
    })


@require_http_methods(["GET"])
def get_project_learning_stats(request, project_id):
    """
    Get learning statistics for a project.

    GET /api/projects/{project_id}/learning/

    Returns:
    {
        "project_id": "uuid",
        "project_name": "AI Podcast Tools",
        "knowledge_generated": 12,
        "avg_confidence": 0.75,
        "feedback_given": 8,
        "acceptance_rate": 0.75,
        "spider_priorities": [
            {"category": "tech", "weight": 2.5},
            {"category": "ai_creative", "weight": 2.0}
        ]
    }
    """
    from core.services.project_research_bridge import get_project_research_bridge
    from core.models_unified_system import (
        PartnershipProject,
        ProjectSpiderPriority,
    )

    try:
        project = PartnershipProject.objects.get(id=project_id)
    except PartnershipProject.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    # Get knowledge stats from bridge
    bridge = get_project_research_bridge()
    stats = bridge.get_project_knowledge_stats(project_id)

    # Get spider priorities
    priorities = ProjectSpiderPriority.objects.filter(
        project=project
    ).select_related('spider_category').order_by('-priority_weight')[:10]

    spider_priorities = []
    for p in priorities:
        spider_priorities.append({
            'category': p.spider_category.slug,
            'category_name': p.spider_category.name,
            'weight': round(p.priority_weight, 2),
            'effectiveness': round(p.effectiveness_score, 2),
            'data_used': p.data_used_count,
            'useful_data': p.useful_data_count,
        })

    stats['spider_priorities'] = spider_priorities

    return JsonResponse(stats)


@csrf_exempt
@require_http_methods(["POST"])
def trigger_knowledge_sync(request):
    """
    Manually trigger knowledge sync for a project.

    POST /api/research/sync/

    Request Body:
    {
        "project_id": "uuid" (optional - sync all if not provided)
    }

    Returns:
    {
        "success": true,
        "processed": 5,
        "knowledge_created": 12
    }
    """
    from core.tasks import sync_project_knowledge
    from core.services.project_research_bridge import get_project_research_bridge

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    project_id = data.get('project_id')

    if project_id:
        # Sync specific project
        from core.models_unified_system import BusinessResearchResult
        bridge = get_project_research_bridge()

        research_results = BusinessResearchResult.objects.filter(
            project_id=project_id
        )

        total_created = 0
        for research in research_results:
            result = bridge.research_to_knowledge(research.id)
            total_created += len(result)

        return JsonResponse({
            'success': True,
            'project_id': project_id,
            'knowledge_created': total_created,
        })
    else:
        # Trigger async sync of all
        sync_project_knowledge.delay()

        return JsonResponse({
            'success': True,
            'message': 'Full knowledge sync triggered',
            'processing': 'async',
        })


@csrf_exempt
@require_http_methods(["POST"])
def trigger_priority_recalculation(request):
    """
    Manually trigger spider priority recalculation.

    POST /api/spiders/recalculate-priorities/

    Request Body:
    {
        "project_id": "uuid" (optional - recalculate all if not provided)
    }

    Returns:
    {
        "success": true,
        "projects_processed": 5,
        "priorities_updated": 20
    }
    """
    from core.tasks import recalculate_spider_priorities, update_project_spider_priorities

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = {}

    project_id = data.get('project_id')

    if project_id:
        # Recalculate for specific project
        update_project_spider_priorities.delay(project_id)

        return JsonResponse({
            'success': True,
            'project_id': project_id,
            'message': 'Priority recalculation triggered',
            'processing': 'async',
        })
    else:
        # Trigger async recalculation of all
        recalculate_spider_priorities.delay()

        return JsonResponse({
            'success': True,
            'message': 'Full priority recalculation triggered',
            'processing': 'async',
        })


@require_http_methods(["GET"])
def get_spider_priorities(request):
    """
    Get current spider category priorities.

    GET /api/spiders/priorities/

    Returns:
    {
        "priorities": {
            "tech": 2.5,
            "ai_creative": 2.0,
            "news": 1.5,
            ...
        },
        "top_categories": [
            {"slug": "tech", "name": "Tech", "weight": 2.5}
        ]
    }
    """
    from core.services.spider_priority_engine import get_spider_priority_engine
    from core.models_unified_system import SpiderCategory

    engine = get_spider_priority_engine()
    priorities = engine.calculate_priorities()

    # Sort by weight
    sorted_priorities = sorted(priorities.items(), key=lambda x: x[1], reverse=True)

    # Get category details
    top_categories = []
    for slug, weight in sorted_priorities[:10]:
        try:
            cat = SpiderCategory.objects.get(slug=slug)
            top_categories.append({
                'slug': slug,
                'name': cat.name,
                'icon': cat.icon,
                'weight': round(weight, 2),
            })
        except SpiderCategory.DoesNotExist:
            top_categories.append({
                'slug': slug,
                'name': slug.replace('_', ' ').title(),
                'weight': round(weight, 2),
            })

    return JsonResponse({
        'priorities': {k: round(v, 2) for k, v in priorities.items()},
        'top_categories': top_categories,
    })
