"""
Remote Code Worker API — submit, monitor, and manage code jobs.

Code jobs are ExecutionRuns configured for the code worker pipeline:
clone repo → implement changes → run tests → push branch → open PR.

Endpoints:
    POST /api/code-jobs/                    — Submit a new code job
    GET  /api/code-jobs/                    — List code jobs
    GET  /api/code-jobs/<id>/               — Job detail + artifacts
    GET  /api/code-jobs/<id>/logs/          — Streaming log chunks
    POST /api/code-jobs/<id>/cancel/        — Cancel a running job

See: docs/designs/remote-code-worker-contract.md
"""

import logging

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import ExecutionRun, Repo, CodeJobLog

logger = logging.getLogger(__name__)


def _serialize_run(run: ExecutionRun) -> dict:
    """Serialize an ExecutionRun as a code job response."""
    elapsed = None
    if run.started_at:
        end = run.completed_at or timezone.now()
        elapsed = round((end - run.started_at).total_seconds(), 1)

    return {
        'job_id': str(run.id),
        'status': run.status,
        'progress': run.progress,
        'current_step': run.current_step,
        'steps_completed': run.steps_completed,
        'steps_total': run.steps_total,

        # Input
        'repo': run.repo.get_repo_slug() if run.repo else run.repo_url,
        'base_branch': run.base_branch,
        'working_branch': run.working_branch,
        'task_prompt': run.plan_summary,
        'conversation_id': run.conversation_id,

        # PR
        'pr_url': run.pr_url,
        'pr_number': run.pr_number,
        'commit_sha': run.commit_sha,

        # Results
        'diff_stats': {
            'files_changed': len(run.changed_files) if run.changed_files else 0,
        },
        'test_result': run.test_summary or {},
        'handoff_summary': run.diff_patch[:2000] if run.diff_patch else '',

        # Error
        'error_message': run.error_message,
        'error_type': run.error_type,
        'failure_reason_code': run.failure_reason_code,

        # Timestamps
        'created_at': run.created_at.isoformat() if run.created_at else None,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
        'elapsed_seconds': elapsed,
        'execution_time_seconds': run.execution_time_seconds,

        # Celery
        'celery_task_id': getattr(run, 'celery_task_id', ''),
    }


# ── Submit code job ──────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_code_job(request):
    """Submit a new code job.

    Request body:
    {
        "repo_slug": "clwest/donkey-betz-platform",
        "ref": "dev",
        "base_branch": "main",
        "task_prompt": "Add endpoint /api/v1/health/extended",
        "acceptance_criteria": ["Tests pass"],
        "test_command": null,
        "lint_command": null,
        "conversation_id": "pa-abc123",
        "max_runtime_seconds": 600
    }
    """
    repo_slug = request.data.get('repo_slug', '')
    task_prompt = request.data.get('task_prompt', '')

    if not repo_slug:
        return Response({'error': 'repo_slug is required'}, status=400)
    if not task_prompt:
        return Response({'error': 'task_prompt is required'}, status=400)

    # Find repo in allowlist
    repo = None
    for r in Repo.objects.filter(is_active=True):
        if r.get_repo_slug() == repo_slug or r.name == repo_slug:
            repo = r
            break

    if not repo:
        return Response(
            {'error': f'Repo "{repo_slug}" is not in the allowlist or is disabled'},
            status=403,
        )

    ref = request.data.get('ref', repo.default_base_branch or 'main')
    base_branch = request.data.get('base_branch', repo.default_base_branch or 'main')
    conversation_id = request.data.get('conversation_id', '')
    acceptance_criteria = request.data.get('acceptance_criteria', [])
    max_runtime = request.data.get('max_runtime_seconds', repo.max_runtime_seconds)

    # Cap runtime
    max_runtime = min(int(max_runtime), 1800)

    # Execution mode: dry_run (no git) or real (full pipeline)
    mode = request.data.get('mode', 'dry_run')
    if mode not in ('dry_run', 'real'):
        return Response({'error': 'mode must be "dry_run" or "real"'}, status=400)

    # Build plan_json to store task details
    plan_json = {
        'version': 'code_worker_v1',
        'mode': mode,
        'title': task_prompt[:200],
        'task_prompt': task_prompt,
        'acceptance_criteria': acceptance_criteria,
        'test_command': request.data.get('test_command', '') or repo.test_command,
        'lint_command': request.data.get('lint_command', '') or repo.lint_command,
        'install_command': repo.install_command,
        'max_runtime_seconds': max_runtime,
        'max_patch_files': repo.max_patch_files,
        'path_filters': repo.path_filters or [],
        'steps': [
            {'id': 'clone', 'description': 'Clone repository'},
            {'id': 'implement', 'description': 'Implement changes'},
            {'id': 'test', 'description': 'Run tests'},
            {'id': 'lint', 'description': 'Run linting'},
            {'id': 'push', 'description': 'Push branch'},
            {'id': 'pr', 'description': 'Create pull request'},
        ],
    }

    run = ExecutionRun.objects.create(
        repo=repo,
        repo_url=repo.repo_url,
        base_branch=base_branch,
        plan_json=plan_json,
        plan_summary=task_prompt[:500],
        steps_total=6,
        conversation_id=conversation_id,
        created_by=request.user,
        status='queued',
    )

    # Generate working branch name
    run.generate_working_branch()

    # Dispatch to Celery code_jobs queue
    try:
        from core.tasks import execute_code_job
        task = execute_code_job.apply_async(
            args=[str(run.id)],
            queue='code_jobs',
        )
        run.celery_task_id = task.id
        run.save(update_fields=['celery_task_id'])
    except Exception as e:
        logger.warning('Could not dispatch code job to Celery: %s', e)
        # Job stays queued — can be picked up later or manually retried

    logger.info('Code job created: %s for repo %s', run.id, repo_slug)

    return Response({
        'job_id': str(run.id),
        'status': 'queued',
        'working_branch': run.working_branch,
        'created_at': run.created_at.isoformat(),
        'celery_task_id': getattr(run, 'celery_task_id', ''),
    }, status=201)


# ── List code jobs ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_code_jobs(request):
    """List code jobs for the authenticated user.

    Query params:
        status: filter by status
        repo: filter by repo slug
        limit: max results (default 20, max 100)
        offset: pagination offset
    """
    qs = ExecutionRun.objects.filter(
        created_by=request.user,
        plan_json__version='code_worker_v1',
    ).select_related('repo').order_by('-created_at')

    status = request.query_params.get('status')
    if status and status not in ('all', '*'):
        qs = qs.filter(status=status)

    repo_filter = request.query_params.get('repo')
    if repo_filter:
        qs = qs.filter(repo__name__icontains=repo_filter)

    limit = min(int(request.query_params.get('limit', 20)), 100)
    offset = int(request.query_params.get('offset', 0))

    runs = qs[offset:offset + limit]
    total = qs.count()

    return Response({
        'jobs': [_serialize_run(r) for r in runs],
        'total': total,
        'limit': limit,
        'offset': offset,
    })


# ── Job detail ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def code_job_detail(request, job_id):
    """Get detailed status and artifacts for a code job."""
    try:
        run = ExecutionRun.objects.select_related('repo').get(
            id=job_id,
            created_by=request.user,
        )
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)

    return Response(_serialize_run(run))


# ── Job logs ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def code_job_logs(request, job_id):
    """Get log chunks for a code job, with cursor-based pagination.

    Query params:
        after_sequence: return logs after this sequence number (default 0)
        limit: max log lines (default 50, max 200)
    """
    try:
        run = ExecutionRun.objects.get(id=job_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)

    after_seq = int(request.query_params.get('after_sequence', 0))
    limit = min(int(request.query_params.get('limit', 50)), 200)

    logs = CodeJobLog.objects.filter(
        run=run,
        sequence__gt=after_seq,
    ).order_by('sequence')[:limit]

    log_list = [
        {
            'sequence': log.sequence,
            'ts': log.timestamp.isoformat(),
            'level': log.level,
            'step': log.step,
            'msg': log.message,
        }
        for log in logs
    ]

    has_more = CodeJobLog.objects.filter(
        run=run,
        sequence__gt=(log_list[-1]['sequence'] if log_list else after_seq),
    ).exists()

    return Response({
        'job_id': str(run.id),
        'log_lines': log_list,
        'has_more': has_more,
        'next_sequence': log_list[-1]['sequence'] if log_list else after_seq,
    })


# ── Cancel job ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_code_job(request, job_id):
    """Cancel a running code job."""
    try:
        run = ExecutionRun.objects.get(id=job_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)

    if run.is_terminal:
        return Response({
            'error': f'Job is already in terminal state: {run.status}',
        }, status=409)

    # Revoke Celery task if possible
    celery_task_id = getattr(run, 'celery_task_id', '')
    if celery_task_id:
        try:
            from core.celery import app
            app.control.revoke(celery_task_id, terminate=True)
        except Exception as e:
            logger.warning('Could not revoke Celery task %s: %s', celery_task_id, e)

    run.cancel()
    logger.info('Code job cancelled: %s', run.id)

    return Response({
        'job_id': str(run.id),
        'status': 'canceled',
    })
