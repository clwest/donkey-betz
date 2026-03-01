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


@require_http_methods(["POST"])
def workflow_run_dispatch(request, run_id):
    """Re-dispatch a pending workflow run to Celery (diagnostic endpoint)."""
    try:
        from core.models_workflow_run import WorkflowRun
        from core.tasks import run_source_pack_workflow
        from core.celery import app as celery_app

        try:
            run = WorkflowRun.objects.get(id=run_id)
        except WorkflowRun.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not found'}, status=404)

        if run.status not in ('pending', 'failed'):
            return JsonResponse({'success': False, 'error': f'Run is {run.status}, not dispatchable'})

        run.status = 'pending'
        run.error_message = ''
        run.save(update_fields=['status', 'error_message', 'updated_at'])

        # Route to content queue — workflow queue has no consumer (Railway dashboard override)
        queue = request.GET.get('queue', 'content')
        task = run_source_pack_workflow.apply_async(
            kwargs={'run_id': str(run.id)},
            queue=queue,
        )
        run.celery_task_id = str(task.id)
        run.save(update_fields=['celery_task_id', 'updated_at'])

        logger.info(f"[WORKFLOW] Dispatched task={task.id} queue={queue} run={run.id}")

        return JsonResponse({
            'success': True,
            'run_id': str(run.id),
            'task_id': str(task.id),
            'queue': queue,
            'message': f'Dispatched to {queue} queue',
        })

    except Exception as e:
        logger.error(f"[WORKFLOW] Error dispatching run: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def workflow_queue_diagnostic(request):
    """Diagnostic: check Redis queue lengths and Celery worker status.

    ?action=add_consumer  — also add 'workflow' queue consumer to all workers
    """
    try:
        import redis as redis_lib
        from django.conf import settings as django_settings
        from core.celery import app as celery_app

        # Optionally add workflow queue consumer
        add_consumer_result = None
        if request.GET.get('action') == 'add_consumer':
            try:
                add_consumer_result = celery_app.control.add_consumer(
                    'workflow', reply=True, timeout=10,
                )
                logger.info(f"[WORKFLOW] add_consumer result: {add_consumer_result}")
            except Exception as ce:
                add_consumer_result = {'error': str(ce)}
                logger.warning(f"[WORKFLOW] add_consumer failed: {ce}")

        broker_url = django_settings.CELERY_BROKER_URL
        r = redis_lib.from_url(broker_url, socket_connect_timeout=5)

        queues = ['workflow', 'long_running', 'ml', 'default', 'content', 'broadcast', 'pa', 'celery']
        queue_lengths = {}
        for q in queues:
            queue_lengths[q] = r.llen(q)

        # Check active/reserved tasks via inspect
        inspect = celery_app.control.inspect(timeout=5)
        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        registered = inspect.registered() or {}

        active_summary = {}
        for worker, tasks in active.items():
            active_summary[worker] = [
                {'name': t.get('name', '?'), 'id': t.get('id', '?')[:12]}
                for t in (tasks or [])
            ]

        reserved_summary = {}
        for worker, tasks in reserved.items():
            reserved_summary[worker] = [
                {'name': t.get('name', '?'), 'id': t.get('id', '?')[:12]}
                for t in (tasks or [])
            ]

        # Check if run_source_pack_workflow is registered
        has_workflow = {}
        for worker, task_list in registered.items():
            has_workflow[worker] = 'core.tasks.run_source_pack_workflow' in (task_list or [])

        # Check active queues per worker
        active_queues_info = {}
        active_queues = inspect.active_queues() or {}
        for worker, qs in active_queues.items():
            active_queues_info[worker] = [q.get('name', '?') for q in (qs or [])]

        result = {
            'success': True,
            'broker_url': broker_url.split('@')[-1] if '@' in broker_url else broker_url,
            'queue_lengths': queue_lengths,
            'active_tasks': active_summary,
            'reserved_tasks': reserved_summary,
            'workflow_registered': has_workflow,
            'worker_queues': active_queues_info,
        }
        if add_consumer_result is not None:
            result['add_consumer_result'] = add_consumer_result
        return JsonResponse(result)

    except Exception as e:
        logger.error(f"[WORKFLOW] Queue diagnostic error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def workflow_add_consumer(request):
    """Add 'workflow' queue consumer to all workers that have the task registered."""
    try:
        from core.celery import app as celery_app

        result = celery_app.control.add_consumer(
            'workflow',
            reply=True,
            timeout=10,
        )
        logger.info(f"[WORKFLOW] add_consumer result: {result}")

        return JsonResponse({
            'success': True,
            'result': result,
            'message': 'Added workflow queue consumer to all workers',
        })

    except Exception as e:
        logger.error(f"[WORKFLOW] Error adding consumer: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
