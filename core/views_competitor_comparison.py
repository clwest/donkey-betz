"""
Session G1: Competitor Comparison API Views

POST /api/v1/competitor/compare/generate/  — create + dispatch Celery task
GET  /api/v1/competitor/compare/<uuid>/    — full comparison detail
GET  /api/v1/competitor/compare/           — list comparisons (filters: status, name)
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def generate_comparison_api(request):
    """Create a CompetitorComparison and dispatch the generation task."""
    try:
        from core.models_competitor_comparison import CompetitorComparison
        from core.tasks import generate_competitor_comparison_task

        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        competitor_name = data.get('competitor_name', '').strip()
        if not competitor_name:
            return JsonResponse({'success': False, 'error': 'competitor_name is required'}, status=400)

        source_document_id = data.get('source_document_id')
        focus_areas = data.get('focus_areas')

        comparison = CompetitorComparison.objects.create(
            competitor_name=competitor_name,
            source_document_id=source_document_id,
            generated_by=data.get('generated_by', 'API'),
            user=request.user if request.user.is_authenticated else None,
        )

        task = generate_competitor_comparison_task.delay(
            comparison_id=str(comparison.id),
            source_document_id=str(source_document_id) if source_document_id else None,
            competitor_name=competitor_name,
            focus_areas=focus_areas,
        )

        logger.info(f"[COMPETITOR] Comparison queued: {comparison.id} task={task.id}")

        return JsonResponse({
            'success': True,
            'comparison_id': str(comparison.id),
            'task_id': str(task.id),
            'message': f'Competitor comparison for "{competitor_name}" started',
        })

    except Exception as e:
        logger.error(f"[COMPETITOR] Error generating comparison: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def comparison_detail_api(request, comparison_id):
    """Return full comparison detail by ID."""
    try:
        from core.models_competitor_comparison import CompetitorComparison

        try:
            comparison = CompetitorComparison.objects.get(id=comparison_id)
        except CompetitorComparison.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Comparison not found'}, status=404)

        return JsonResponse({
            'success': True,
            'comparison': {
                'id': str(comparison.id),
                'competitor_name': comparison.competitor_name,
                'status': comparison.status,
                'quality_score': comparison.quality_score,
                'error_message': comparison.error_message,
                'source_document_id': str(comparison.source_document_id) if comparison.source_document_id else None,
                'review': comparison.review_json,
                'comparison_table': comparison.comparison_table_json,
                'gap_backlog': comparison.gap_backlog_json,
                'tools_stack': comparison.tools_stack_json,
                'evidence': comparison.evidence_json,
                'sources': comparison.sources_json,
                'executive_summary': comparison.executive_summary_json,
                'quality_rubric': comparison.quality_rubric_json,
                'summary': comparison.summary,
                'generated_by': comparison.generated_by,
                'created_at': comparison.created_at.isoformat(),
                'completed_at': comparison.completed_at.isoformat() if comparison.completed_at else None,
                'metadata': comparison.metadata,
            },
        })

    except Exception as e:
        logger.error(f"[COMPETITOR] Error fetching comparison: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def comparison_list_api(request):
    """List comparisons with optional status/name filters."""
    try:
        from core.models_competitor_comparison import CompetitorComparison

        qs = CompetitorComparison.objects.all()

        status = request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        name = request.GET.get('name')
        if name:
            qs = qs.filter(competitor_name__icontains=name)

        limit = min(int(request.GET.get('limit', 20)), 100)
        comparisons = list(qs[:limit])

        return JsonResponse({
            'success': True,
            'count': len(comparisons),
            'comparisons': [
                {
                    'id': str(c.id),
                    'competitor_name': c.competitor_name,
                    'status': c.status,
                    'quality_score': c.quality_score,
                    'evidence_count': len(c.evidence_json) if isinstance(c.evidence_json, list) else 0,
                    'summary': c.summary[:300] if c.summary else '',
                    'generated_by': c.generated_by,
                    'created_at': c.created_at.isoformat(),
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                }
                for c in comparisons
            ],
        })

    except Exception as e:
        logger.error(f"[COMPETITOR] Error listing comparisons: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
