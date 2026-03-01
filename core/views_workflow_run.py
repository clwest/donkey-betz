"""
WorkflowRun REST API Views

GET /api/v1/workflows/runs/               — list runs (filters: status, workflow_key)
GET /api/v1/workflows/runs/<uuid:run_id>/ — full detail with events
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def workflow_run_list(request):
    """List workflow runs with optional filters."""
    try:
        from core.models_workflow_run import WorkflowRun

        qs = WorkflowRun.objects.all()

        status = request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        workflow_key = request.GET.get('workflow_key')
        if workflow_key:
            qs = qs.filter(workflow_key=workflow_key)

        limit = min(int(request.GET.get('limit', 20)), 100)
        runs = list(qs[:limit])

        return JsonResponse({
            'success': True,
            'count': len(runs),
            'runs': [
                {
                    'id': str(r.id),
                    'workflow_key': r.workflow_key,
                    'status': r.status,
                    'stage': r.stage,
                    'percent': r.percent,
                    'stage_detail': r.stage_detail,
                    'competitor_name': (r.input_json or {}).get('competitor_name', ''),
                    'created_at': r.created_at.isoformat(),
                    'started_at': r.started_at.isoformat() if r.started_at else None,
                    'completed_at': r.completed_at.isoformat() if r.completed_at else None,
                }
                for r in runs
            ],
        })

    except Exception as e:
        logger.error(f"[WORKFLOW] Error listing runs: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def workflow_run_detail(request, run_id):
    """Return full workflow run detail including events."""
    try:
        from core.models_workflow_run import WorkflowRun

        try:
            run = WorkflowRun.objects.get(id=run_id)
        except WorkflowRun.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Workflow run not found'}, status=404)

        return JsonResponse({
            'success': True,
            'run': {
                'id': str(run.id),
                'workflow_key': run.workflow_key,
                'status': run.status,
                'stage': run.stage,
                'percent': run.percent,
                'stage_detail': run.stage_detail,
                'input': run.input_json,
                'output': run.output_json,
                'events': run.events_json,
                'error_message': run.error_message,
                'celery_task_id': run.celery_task_id,
                'created_at': run.created_at.isoformat(),
                'started_at': run.started_at.isoformat() if run.started_at else None,
                'completed_at': run.completed_at.isoformat() if run.completed_at else None,
                'metadata': run.metadata,
            },
        })

    except Exception as e:
        logger.error(f"[WORKFLOW] Error fetching run detail: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
