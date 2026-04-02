"""
Workspace Pipeline Runner
==========================

Executes a workspace's pipeline stages sequentially, dispatching
each stage's agent via AgentRouter and tracking progress in PipelineRun.

Key behaviors:
- Each stage saves a Deliverable to the workspace with its output
- Previous stage output is passed as context to the next stage
- Per-stage wall-clock timeout prevents hung agents (default 10 min)
- Stages continue after failure — one bad stage doesn't cancel the rest

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
    """Execute an existing PipelineRun with deliverable creation and output threading."""
    from core.models_workspace_templates import PipelineRun
    from core.agent_router import AgentRouter

    try:
        run = PipelineRun.objects.select_related('workspace', 'triggered_by').get(id=run_id)
    except PipelineRun.DoesNotExist:
        return {'success': False, 'error': 'PipelineRun not found'}

    workspace = run.workspace
    config = getattr(workspace, 'config', None)

    # Check governance mode
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
    brief = config.workspace_brief if config else {}

    # Track outputs from previous stages so they flow forward
    previous_stage_output = None  # {stage_name, summary, deliverable_id}

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

        # Build task description with brief + previous stage context
        task_desc = _build_task_description(stage, brief, workspace.name, previous_stage_output)

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
        if previous_stage_output:
            context['previous_stage'] = previous_stage_output
            # Some agents (e.g., EditorAgent) expect 'content' directly in context
            if previous_stage_output.get('full_content'):
                context['content'] = previous_stage_output['full_content']

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
                # Extract the content from the agent result
                content = _extract_content(result)
                summary = content[:300] if content else ''

                # Save a deliverable with the stage output
                deliverable_id = _save_stage_deliverable(
                    workspace=workspace,
                    stage_name=stage_name,
                    agent_name=agent_name,
                    content=content,
                    brief=brief,
                    run_id=str(run.id),
                    user=run.triggered_by,
                )

                # Thread output forward to next stage
                previous_stage_output = {
                    'stage_name': stage_name,
                    'agent': agent_name,
                    'summary': summary,
                    'deliverable_id': str(deliverable_id) if deliverable_id else None,
                    'full_content': content[:2000] if content else '',  # Cap for context size
                }

                _update_stage(run, i, 'completed', output={
                    'message': summary[:500],
                    'agent': agent_name,
                    'deliverable_id': str(deliverable_id) if deliverable_id else None,
                })
                logger.info("Pipeline %s stage %d (%s) completed, deliverable=%s", run.id, i, stage_name, deliverable_id)
            else:
                error_msg = str(result.message)[:500] if result and result.message else 'Agent returned no result'
                _update_stage(run, i, 'failed', error=error_msg)
                # Don't update previous_stage_output — next stage gets the last successful one

        except _FuturesTimeout:
            _update_stage(run, i, 'failed', error=f'Stage timed out after {timeout}s')
            logger.error("Pipeline %s stage %d (%s) TIMED OUT after %ds", run.id, i, stage_name, timeout)

        except Exception as e:
            _update_stage(run, i, 'failed', error=str(e)[:500])
            logger.error("Pipeline %s stage %d (%s) error: %s", run.id, i, stage_name, e)

    # Finalize
    statuses = [s.get('status') for s in run.stage_results]
    completed_count = sum(1 for s in statuses if s == 'completed')
    failed_count = sum(1 for s in statuses if s == 'failed')

    run.status = 'failed' if (failed_count > 0 and completed_count == 0) else 'completed'
    run.finished_at = timezone.now()
    run.save(update_fields=['status', 'finished_at', 'current_stage_index'])

    logger.info("Pipeline %s finished: %d/%d completed, %d failed", run.id, completed_count, len(statuses), failed_count)

    return {
        'success': True,
        'run_id': str(run.id),
        'status': run.status,
        'progress_pct': run.progress_pct,
        'stages': run.stage_results,
        'duration_seconds': run.duration_seconds,
    }


def _extract_content(result) -> str:
    """Extract the actual content from an AgentResult."""
    # AgentResult.data may have full_text or content
    if result.data:
        if isinstance(result.data, dict):
            # ContentWriterAgent stores content in data['content']['full_text']
            content = result.data.get('content', {})
            if isinstance(content, dict):
                full_text = content.get('full_text', '')
                if full_text:
                    return full_text
            # Other agents may put content directly in data
            for key in ('full_text', 'text', 'output', 'report', 'findings', 'outline'):
                if key in result.data and isinstance(result.data[key], str):
                    return result.data[key]
    # Fall back to message
    return str(result.message) if result.message else ''


def _save_stage_deliverable(workspace, stage_name, agent_name, content, brief, run_id, user):
    """Save the stage output as a workspace-scoped Deliverable."""
    try:
        from core.models_deliverables import Deliverable

        topic = brief.get('topic', workspace.name) if brief else workspace.name
        title = f"{stage_name}: {topic}"

        deliverable = Deliverable.objects.create(
            title=title[:255],
            deliverable_type='document',
            category=f'Pipeline — {stage_name}',
            agent_name=agent_name,
            content=content,
            content_format='markdown',
            workspace=workspace,
            user=user,
            is_saved=True,
            metadata={
                'pipeline_run_id': run_id,
                'stage_name': stage_name,
                'workspace_brief_topic': brief.get('topic', '') if brief else '',
            },
        )
        return deliverable.id
    except Exception as e:
        logger.error("Failed to save stage deliverable: %s", e)
        return None


def _build_task_description(stage, brief, workspace_name, previous_output=None):
    """Build a rich task description from stage config + brief + previous stage output."""
    parts = [stage.get('description', f"Execute {stage.get('name', 'stage')} for {workspace_name}")]

    if brief:
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

    # Thread previous stage output as input
    if previous_output:
        prev_name = previous_output.get('stage_name', 'Previous stage')
        prev_content = previous_output.get('full_content', previous_output.get('summary', ''))
        if prev_content:
            parts.append(f"\n\n--- {prev_name} Output ---\n{prev_content}")

    return '. '.join(parts[:6]) + ('\n\n' + parts[-1] if len(parts) > 6 and previous_output else '')


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
