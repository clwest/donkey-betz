"""
Session 1074/1075: Executor API — create, monitor, and manage execution runs.

Endpoints:
    POST /api/v1/executor/runs/                  — Create a new run
    GET  /api/v1/executor/runs/list/             — List runs
    GET  /api/v1/executor/runs/<id>/             — Run detail
    GET  /api/v1/executor/runs/<id>/logs/        — Run logs
    GET  /api/v1/executor/runs/<id>/diff/        — Run diff
    POST /api/v1/executor/runs/<id>/cancel/      — Cancel a run
    POST /api/v1/executor/runs/<id>/approve/     — Approve entire run (legacy)
    POST /api/v1/executor/runs/<id>/approve-step/ — Approve a specific step
"""

import logging

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import ExecutionRun, Repo
from core.services.executor_plan import (
    extract_commands_from_plan,
    is_legacy_plan,
    normalize_legacy_plan,
    normalize_plan_v1,
    validate_plan_v1,
)
from core.services.executor_policy import classify_plan

logger = logging.getLogger(__name__)


# ── Create run ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_run(request):
    """Create and optionally start an execution run.

    Accepts PlanV1 format:
    {
        "plan": {"version": "v1", "title": "...", "steps": [...]},
        "conversation_id": "optional-convo-id"
    }

    Also accepts legacy format (auto-normalized to v1):
    {
        "plan": [{"command": "...", "description": "..."}],
        "summary": "...",
        "conversation_id": "optional-convo-id"
    }
    """
    plan_input = request.data.get('plan')
    summary = request.data.get('summary', '')
    conversation_id = request.data.get('conversation_id', '')

    if not plan_input:
        return Response({'error': 'Plan is required'}, status=400)

    # Normalize legacy format to PlanV1
    if is_legacy_plan(plan_input):
        plan = normalize_legacy_plan(plan_input, summary=summary)
    elif isinstance(plan_input, dict):
        plan = plan_input
    else:
        return Response({'error': 'Plan must be a PlanV1 object or a legacy step list'}, status=400)

    # Validate PlanV1
    errors = validate_plan_v1(plan)
    if errors:
        return Response({
            'error': 'Invalid plan',
            'validation_errors': [
                {'field': e.field, 'message': e.message} for e in errors
            ],
        }, status=400)

    # Normalize (fill defaults) and store
    normalized = normalize_plan_v1(plan)
    plan_summary = normalized.get('title', summary)

    # Resolve repo from registry
    repo = _resolve_repo(request)
    if isinstance(repo, Response):
        return repo

    # Run classifier on shell commands (for Tier C blocking only at creation time)
    commands = extract_commands_from_plan(normalized)
    policy = classify_plan(commands)

    if policy['has_blocked']:
        blocked_cmds = [
            commands[i].get('command', '') for i in policy['blocked_steps']
        ]
        return Response({
            'error': 'Plan contains blocked commands (Tier C)',
            'blocked_commands': blocked_cmds,
            'policy': policy,
        }, status=403)

    # Create the run — store normalized plan only
    run = ExecutionRun.objects.create(
        repo=repo,
        repo_url=repo.repo_url,
        base_branch=repo.default_base_branch,
        plan_json=normalized,
        plan_summary=plan_summary,
        steps_total=len(normalized.get('steps', [])),
        conversation_id=conversation_id,
        created_by=request.user,
        blocked_steps=policy['blocked_steps'],
        approval_required_steps=policy['approval_required_steps'],
        status='queued',
    )

    _dispatch_run(run)

    return Response({
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'plan_version': normalized.get('version'),
    }, status=201)


# ── List runs ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_runs(request):
    """List execution runs for the current user."""
    runs = ExecutionRun.objects.filter(created_by=request.user).order_by('-created_at')[:50]
    return Response({
        'success': True,
        'runs': [_serialize_run(r) for r in runs],
    })


# ── Run detail ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_detail(request, run_id):
    """Get full details of an execution run."""
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    data = _serialize_run(run)
    data['plan_json'] = run.plan_json
    data['test_summary'] = run.test_summary
    data['blocked_steps'] = run.blocked_steps
    data['approval_required_steps'] = run.approval_required_steps
    data['approved_steps'] = run.approved_steps
    data['awaiting_approval_step_id'] = run.awaiting_approval_step_id
    data['current_step_index'] = run.current_step_index
    return Response({'success': True, 'run': data})


# ── Run logs ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_logs(request, run_id):
    """Get execution logs for a run."""
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    return Response({
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'log': run.log_text,
    })


# ── Run diff ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def run_diff(request, run_id):
    """Get the git diff produced by a run."""
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    return Response({
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'diff': run.diff_patch,
        'changed_files': run.changed_files,
    })


# ── Cancel run ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_run(request, run_id):
    """Cancel a queued or running execution."""
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    if run.status in ('succeeded', 'failed', 'canceled'):
        return Response({'error': f'Cannot cancel run in {run.status} state'}, status=400)

    run.cancel()
    return Response({'success': True, 'run_id': str(run.id), 'status': 'canceled'})


# ── Approve run (legacy — blanket approval) ──────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_run(request, run_id):
    """Approve all pending steps and re-queue the run (legacy endpoint)."""
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    if run.status != 'awaiting_approval':
        return Response({'error': f'Run is not awaiting approval (status: {run.status})'}, status=400)

    run.approve(request.user)
    _dispatch_run(run)

    return Response({'success': True, 'run_id': str(run.id), 'status': run.status})


# ── Approve step ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_step(request, run_id):
    """Approve a specific step and re-queue the run.

    Body: {"step_id": "s3"}
    """
    try:
        run = ExecutionRun.objects.get(id=run_id, created_by=request.user)
    except ExecutionRun.DoesNotExist:
        return Response({'error': 'Run not found'}, status=404)

    if run.status != 'awaiting_approval':
        return Response(
            {'error': f'Run is not awaiting approval (status: {run.status})'},
            status=400,
        )

    step_id = request.data.get('step_id', '')
    if not step_id:
        return Response({'error': 'step_id is required'}, status=400)

    # Validate step_id exists in the plan
    plan = run.plan_json or {}
    step_ids = [s.get('id') for s in plan.get('steps', [])]
    if step_id not in step_ids:
        return Response({'error': f'Step {step_id!r} not found in plan'}, status=404)

    # Idempotent: if already approved, just re-dispatch
    approved = run.approved_steps or []
    if step_id in approved and run.status == 'awaiting_approval':
        run.status = 'queued'
        run.awaiting_approval_step_id = ''
        run.save(update_fields=['status', 'awaiting_approval_step_id'])
    else:
        run.approve_step(request.user, step_id)

    _dispatch_run(run)

    return Response({
        'success': True,
        'run_id': str(run.id),
        'step_id': step_id,
        'status': run.status,
        'approved_steps': run.approved_steps,
    })


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_repo(request):
    """Resolve the target Repo from the registry."""
    if settings.EXECUTOR_SINGLE_REPO_MODE:
        default_name = getattr(settings, 'EXECUTOR_DEFAULT_REPO_NAME', 'donkey-betz-platform')
        try:
            return Repo.objects.get(name=default_name, is_active=True)
        except Repo.DoesNotExist:
            return Response(
                {'error': f'Default repo "{default_name}" not found in registry'},
                status=500,
            )

    repo_id = request.data.get('repo_id')
    if not repo_id:
        return Response({'error': 'repo_id is required in multi-repo mode'}, status=400)
    try:
        return Repo.objects.get(id=repo_id, is_active=True)
    except Repo.DoesNotExist:
        return Response({'error': 'Repo not found or inactive'}, status=404)


def _serialize_run(run) -> dict:
    repo_data = None
    if run.repo_id:
        repo_data = {
            'id': str(run.repo.id),
            'name': run.repo.name,
            'repo_url': run.repo.repo_url,
        }

    return {
        'id': str(run.id),
        'status': run.status,
        'plan_summary': run.plan_summary,
        'repo': repo_data,
        'repo_url': run.repo_url,
        'base_branch': run.base_branch,
        'working_branch': run.working_branch,
        'steps_completed': run.steps_completed,
        'steps_total': run.steps_total,
        'current_step': run.current_step,
        'current_step_index': run.current_step_index,
        'awaiting_approval_step_id': run.awaiting_approval_step_id,
        'error_message': run.error_message,
        'execution_time_seconds': run.execution_time_seconds,
        'changed_files': run.changed_files,
        'conversation_id': run.conversation_id,
        'created_at': run.created_at.isoformat() if run.created_at else None,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'completed_at': run.completed_at.isoformat() if run.completed_at else None,
    }


def _dispatch_run(run) -> None:
    """Dispatch run execution to Celery."""
    from core.tasks_executor import execute_run_task
    execute_run_task.delay(str(run.id))
    logger.info(f'[Executor] Dispatched run {run.id} to Celery')
