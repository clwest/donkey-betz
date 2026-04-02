"""
Workspace Pipeline Runner
==========================

Executes a workspace's pipeline stages sequentially, dispatching
each stage's agent via AgentRouter and tracking progress in PipelineRun.

Usage (via Celery task):
    from core.tasks import execute_workspace_pipeline
    execute_workspace_pipeline.delay(str(run.id))
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def execute_pipeline_run(run_id: str) -> dict:
    """
    Execute an existing PipelineRun.

    Reads the pipeline stages from the run's snapshot, executes each
    auto stage via AgentRouter, and updates stage_results in real-time.
    """
    from core.models_workspace_templates import PipelineRun
    from core.agent_router import AgentRouter
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        run = PipelineRun.objects.select_related('workspace', 'triggered_by').get(id=run_id)
    except PipelineRun.DoesNotExist:
        return {'success': False, 'error': 'PipelineRun not found'}

    workspace = run.workspace

    # Check governance mode
    config = getattr(workspace, 'config', None)
    if config:
        gov_mode = config.effective_governance_mode
        if gov_mode in ('freeze', 'safe_mode'):
            run.status = 'cancelled'
            run.error_message = f'Blocked by governance mode: {gov_mode}'
            run.finished_at = timezone.now()
            run.save(update_fields=['status', 'error_message', 'finished_at'])
            return {'success': False, 'error': run.error_message}

    run.status = 'running'
    run.started_at = timezone.now()
    run.save(update_fields=['status', 'started_at'])

    logger.info(
        "Pipeline run %s started for workspace %s (%d stages)",
        run.id, workspace.name, len(run.pipeline_snapshot),
    )

    router = AgentRouter()
    user = run.triggered_by

    for i, stage in enumerate(run.pipeline_snapshot):
        stage_name = stage.get('name', f'Stage {i+1}')
        agent_name = stage.get('agent')
        is_auto = stage.get('auto', False)
        requires_approval = stage.get('requires_approval', False)

        run.current_stage_index = i
        _update_stage(run, i, 'running')

        # No agent or manual stage → skip/await
        if not agent_name or not is_auto:
            status = 'awaiting_approval' if requires_approval else 'skipped'
            _update_stage(run, i, status, output={'reason': 'Manual stage' if not is_auto else 'No agent'})
            continue

        # Execute agent
        try:
            # Build a rich task description using the workspace brief
            brief = config.workspace_brief if config else {}
            task_parts = [stage.get('description', f'Execute {stage_name}')]
            if brief.get('topic'):
                task_parts.append(f"Topic/Focus: {brief['topic']}")
            if brief.get('audience'):
                task_parts.append(f"Target audience: {brief['audience']}")
            if brief.get('tone'):
                task_parts.append(f"Tone: {brief['tone']}")
            if brief.get('focus_areas'):
                task_parts.append(f"Focus areas: {', '.join(brief['focus_areas'])}")
            if brief.get('notes'):
                task_parts.append(f"Additional context: {brief['notes']}")
            task_desc = '. '.join(task_parts)

            context = {
                'workspace_id': str(workspace.id),
                'workspace_name': workspace.name,
                'pipeline_run_id': str(run.id),
                'stage_name': stage_name,
                'stage_index': i,
                'workspace_brief': brief,
            }
            if config:
                context['deliverable_categories'] = config.deliverable_categories

            result = router.route(
                task=task_desc,
                agent_name=agent_name,
                context=context,
            )

            if result and result.success:
                _update_stage(run, i, 'completed', output={
                    'message': str(result.message)[:500] if result.message else '',
                    'agent': agent_name,
                })
            else:
                error_msg = str(result.message)[:500] if result and result.message else 'No result'
                _update_stage(run, i, 'failed', error=error_msg)

        except Exception as e:
            _update_stage(run, i, 'failed', error=str(e)[:500])
            logger.error("Pipeline run %s stage %d error: %s", run.id, i, e)

    # Finalize
    statuses = [s.get('status') for s in run.stage_results]
    if any(s == 'failed' for s in statuses):
        run.status = 'completed'  # partial success
    else:
        run.status = 'completed'

    run.finished_at = timezone.now()
    run.save(update_fields=['status', 'finished_at', 'current_stage_index'])

    completed = sum(1 for s in statuses if s == 'completed')
    logger.info("Pipeline run %s finished: %d/%d stages completed", run.id, completed, len(statuses))

    return {
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'progress_pct': run.progress_pct,
        'stages': run.stage_results,
        'duration_seconds': run.duration_seconds,
    }


def _update_stage(run, index, status, output=None, error=None):
    """Update stage status in PipelineRun.stage_results JSON."""
    if index >= len(run.stage_results):
        return
    stage = run.stage_results[index]
    stage['status'] = status
    now = timezone.now().isoformat()
    if status == 'running':
        stage['started_at'] = now
    if status in ('completed', 'failed', 'skipped', 'awaiting_approval'):
        stage['finished_at'] = now
    if output:
        stage['output'] = output
    if error:
        stage['error'] = error
    run.save(update_fields=['stage_results', 'current_stage_index'])
