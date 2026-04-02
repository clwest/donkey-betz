"""
Workspace Pipeline Runner
==========================

Executes a workspace's pipeline stages sequentially, dispatching
each stage's agent via AgentRouter and tracking progress in PipelineRun.

Features:
- Per-stage wall-clock timeout (default 10 min) prevents hung agents
  from blocking the entire pipeline
- Stages continue after failure — one bad stage doesn't cancel the rest
- Real-time stage_results updates for frontend polling

Usage (via Celery task):
    from core.tasks import execute_workspace_pipeline
    execute_workspace_pipeline.delay(str(run.id))
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout
from django.utils import timezone

logger = logging.getLogger(__name__)

# Default per-stage timeout in seconds (env-configurable)
STAGE_TIMEOUT_SECONDS = int(os.environ.get('PIPELINE_STAGE_TIMEOUT', '600'))  # 10 min


def execute_pipeline_run(run_id: str) -> dict:
    """
    Execute an existing PipelineRun.

    Reads the pipeline stages from the run's snapshot, executes each
    auto stage via AgentRouter with a per-stage timeout, and updates
    stage_results in real-time. Continues past failures.
    """
    from core.models_workspace_templates import PipelineRun
    from core.agent_router import AgentRouter

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

    for i, stage in enumerate(run.pipeline_snapshot):
        stage_name = stage.get('name', f'Stage {i+1}')
        agent_name = stage.get('agent')
        is_auto = stage.get('auto', False)
        requires_approval = stage.get('requires_approval', False)

        run.current_stage_index = i
        _update_stage(run, i, 'running')

        # No agent or manual stage
        if not agent_name or not is_auto:
            status = 'awaiting_approval' if requires_approval else 'skipped'
            _update_stage(run, i, status, output={'reason': 'Manual stage' if not is_auto else 'No agent'})
            continue

        # Build task description from workspace brief
        brief = config.workspace_brief if config else {}
        task_desc = _build_task_description(stage, brief, workspace.name)

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

        # Execute agent with wall-clock timeout
        timeout = stage.get('timeout_seconds', STAGE_TIMEOUT_SECONDS)
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    router.route,
                    task=task_desc,
                    agent_name=agent_name,
                    context=context,
                )
                result = future.result(timeout=timeout)

            if result and result.success:
                _update_stage(run, i, 'completed', output={
                    'message': str(result.message)[:500] if result.message else '',
                    'agent': agent_name,
                })
                logger.info("Pipeline %s stage %d (%s) completed", run.id, i, stage_name)
            else:
                error_msg = str(result.message)[:500] if result and result.message else 'Agent returned no result'
                _update_stage(run, i, 'failed', error=error_msg)
                logger.warning("Pipeline %s stage %d (%s) failed: %s", run.id, i, stage_name, error_msg)

        except _FuturesTimeout:
            _update_stage(run, i, 'failed', error=f'Stage timed out after {timeout}s')
            logger.error("Pipeline %s stage %d (%s) TIMED OUT after %ds", run.id, i, stage_name, timeout)

        except Exception as e:
            _update_stage(run, i, 'failed', error=str(e)[:500])
            logger.error("Pipeline %s stage %d (%s) error: %s", run.id, i, stage_name, e)

        # Always continue to next stage — don't abort on failure

    # Finalize
    statuses = [s.get('status') for s in run.stage_results]
    completed_count = sum(1 for s in statuses if s == 'completed')
    failed_count = sum(1 for s in statuses if s == 'failed')

    if failed_count > 0 and completed_count == 0:
        run.status = 'failed'
    else:
        run.status = 'completed'

    run.finished_at = timezone.now()
    run.save(update_fields=['status', 'finished_at', 'current_stage_index'])

    logger.info(
        "Pipeline %s finished: %d/%d completed, %d failed",
        run.id, completed_count, len(statuses), failed_count,
    )

    return {
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'progress_pct': run.progress_pct,
        'stages': run.stage_results,
        'duration_seconds': run.duration_seconds,
    }


def _build_task_description(stage: dict, brief: dict, workspace_name: str) -> str:
    """Build a rich task description from the stage config + workspace brief."""
    parts = [stage.get('description', f"Execute {stage.get('name', 'stage')} for {workspace_name}")]
    if brief.get('topic'):
        parts.append(f"Topic/Focus: {brief['topic']}")
    if brief.get('audience'):
        parts.append(f"Target audience: {brief['audience']}")
    if brief.get('tone'):
        parts.append(f"Tone: {brief['tone']}")
    if brief.get('focus_areas'):
        areas = brief['focus_areas']
        if isinstance(areas, list):
            parts.append(f"Focus areas: {', '.join(areas)}")
    if brief.get('notes'):
        parts.append(f"Additional context: {brief['notes']}")
    return '. '.join(parts)


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
