"""
Workspace Pipeline Runner
==========================

Executes a workspace's pipeline stages, dispatching agents via AgentRouter.

Key behaviors:
- Stages with the same parallel_group run concurrently
- Each stage saves a Deliverable with its output
- Previous stage/group outputs flow forward as context
- Per-stage wall-clock timeout prevents hung agents (default 10 min)
- Stages continue after failure

Usage:
    from core.tasks import execute_workspace_pipeline
    execute_workspace_pipeline.delay(str(run.id))
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout, as_completed
from django.utils import timezone

logger = logging.getLogger(__name__)

STAGE_TIMEOUT_SECONDS = int(os.environ.get('PIPELINE_STAGE_TIMEOUT', '600'))


def execute_pipeline_run(run_id: str) -> dict:
    """Execute a PipelineRun — supports parallel stage groups."""
    from core.models_workspace_templates import PipelineRun
    from core.agent_router import AgentRouter

    try:
        run = PipelineRun.objects.select_related('workspace', 'triggered_by').get(id=run_id)
    except PipelineRun.DoesNotExist:
        return {'success': False, 'error': 'PipelineRun not found'}

    workspace = run.workspace
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

    logger.info("Pipeline %s started (%d stages)", run.id, len(run.pipeline_snapshot))

    router = AgentRouter()
    brief = config.workspace_brief if config else {}
    previous_outputs = []  # Accumulates outputs from completed stages

    # Group stages by parallel_group (None = sequential)
    stage_groups = _group_stages(run.pipeline_snapshot)

    discovery_gate_run = False

    for group in stage_groups:
        if len(group) == 1:
            # Sequential stage
            stage_idx, stage = group[0]
            _execute_single_stage(
                run, stage_idx, stage, router, workspace, config, brief, previous_outputs,
            )
        else:
            # Parallel group — run all stages concurrently
            _execute_parallel_group(
                run, group, router, workspace, config, brief, previous_outputs,
            )

            # Quality gate: after discovery parallel group, check topic alignment
            group_name = group[0][1].get('parallel_group', '')
            if group_name == 'discovery' and not discovery_gate_run and brief:
                discovery_gate_run = True
                gate_result = _run_quality_gates(run, brief, previous_outputs)
                if not gate_result['proceed']:
                    logger.warning(
                        "Pipeline %s STOPPED by quality gate: %s",
                        run.id, gate_result['reason'],
                    )
                    run.error_message = f"Quality gate: {gate_result['reason']}"
                    run.status = 'failed'
                    run.finished_at = timezone.now()
                    run.save(update_fields=['status', 'error_message', 'finished_at'])
                    return {
                        'success': False,
                        'run_id': str(run.id),
                        'status': 'failed',
                        'error': gate_result['reason'],
                        'gate_details': gate_result,
                    }

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


def _group_stages(stages):
    """Group stages by parallel_group. Returns list of groups, each a list of (index, stage)."""
    groups = []
    current_group = []
    current_key = '__NONE__'

    for i, stage in enumerate(stages):
        group_key = stage.get('parallel_group')
        if group_key and group_key == current_key:
            current_group.append((i, stage))
        else:
            if current_group:
                groups.append(current_group)
            current_group = [(i, stage)]
            current_key = group_key or f'__SEQ_{i}__'

    if current_group:
        groups.append(current_group)

    return groups


def _execute_single_stage(run, stage_idx, stage, router, workspace, config, brief, previous_outputs):
    """Execute a single pipeline stage."""
    stage_name = stage.get('name', f'Stage {stage_idx+1}')
    agent_name = stage.get('agent')
    is_auto = stage.get('auto', False)
    requires_approval = stage.get('requires_approval', False)

    run.current_stage_index = stage_idx
    _update_stage(run, stage_idx, 'running')

    if not agent_name or not is_auto:
        status = 'awaiting_approval' if requires_approval else 'skipped'
        _update_stage(run, stage_idx, status, output={'reason': 'Manual stage' if not is_auto else 'No agent'})
        return

    result_output = _run_agent_with_timeout(
        run, stage_idx, stage, router, workspace, config, brief, previous_outputs,
    )
    if result_output:
        previous_outputs.append(result_output)


def _execute_parallel_group(run, group, router, workspace, config, brief, previous_outputs):
    """Execute a group of stages in parallel."""
    # Mark all as running
    for stage_idx, stage in group:
        run.current_stage_index = stage_idx
        _update_stage(run, stage_idx, 'running')

    # Filter to auto stages with agents
    runnable = [(idx, s) for idx, s in group if s.get('agent') and s.get('auto', False)]
    manual = [(idx, s) for idx, s in group if not s.get('agent') or not s.get('auto', False)]

    # Mark manual stages
    for idx, s in manual:
        status = 'awaiting_approval' if s.get('requires_approval') else 'skipped'
        _update_stage(run, idx, status, output={'reason': 'Manual stage'})

    if not runnable:
        return

    # Run agents in parallel
    max_workers = min(len(runnable), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {}
        for stage_idx, stage in runnable:
            future = executor.submit(
                _run_agent_with_timeout,
                run, stage_idx, stage, router, workspace, config, brief, previous_outputs,
            )
            future_map[future] = (stage_idx, stage)

        for future in as_completed(future_map):
            stage_idx, stage = future_map[future]
            try:
                result_output = future.result()
                if result_output:
                    previous_outputs.append(result_output)
            except Exception as e:
                _update_stage(run, stage_idx, 'failed', error=str(e)[:500])


def _run_agent_with_timeout(run, stage_idx, stage, router, workspace, config, brief, previous_outputs):
    """Run a single agent with timeout. Returns output dict or None."""
    stage_name = stage.get('name', f'Stage {stage_idx+1}')
    agent_name = stage.get('agent')
    timeout = stage.get('timeout_seconds', STAGE_TIMEOUT_SECONDS)

    # Build task description with brief + all previous outputs
    task_desc = _build_task_description(stage, brief, workspace.name, previous_outputs)

    context = {
        'workspace_id': str(workspace.id),
        'workspace_name': workspace.name,
        'pipeline_run_id': str(run.id),
        'stage_name': stage_name,
        'stage_index': stage_idx,
        'workspace_brief': brief,
    }
    if config:
        context['deliverable_categories'] = config.deliverable_categories

    # Inject previous stage content for agents that read context['content']
    if previous_outputs:
        last = previous_outputs[-1]
        if last.get('full_content'):
            raw = last['full_content']
            # EditorAgent expects content as a dict with title/sections/conclusion
            # Other agents accept a plain string. Provide both formats.
            context['content'] = {
                'title': last.get('stage_name', 'Draft'),
                'sections': [{'heading': 'Content', 'body': raw}],
                'conclusion': '',
            }
            context['content_text'] = raw  # Plain string for agents that prefer it
        context['previous_stage'] = last

        # Session 1103: Find and pass the RESEARCH stage output specifically.
        # previous_outputs[-1] may be Content Strategy, not Deep Research.
        # ContentWriterAgent reads context['research'] — must be evidence content.
        research_content_parts = []
        for prev in previous_outputs:
            agent = prev.get('agent', '')
            content = prev.get('full_content', '')
            if not content:
                continue
            # Research, Topic Mining, and Trend Analysis all contribute evidence
            if agent in ('ResearchAgent', 'TopicMinerAgent', 'TrendAnalysisAgent'):
                research_content_parts.append(content)
        if research_content_parts:
            context['research'] = '\n\n---\n\n'.join(research_content_parts)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(router.route, task=task_desc, agent_name=agent_name, context=context)
            result = future.result(timeout=timeout)

        if result and result.success:
            # Validate output against contract
            from core.services.agent_output_contract import validate_agent_output
            validation = validate_agent_output(result, task_desc)

            if validation['recommendation'] == 'escalate':
                # Output is garbage — don't save as deliverable
                issues = '; '.join(validation['issues'])
                _update_stage(run, stage_idx, 'failed',
                              error=f"Output quality too low ({validation['quality_score']}/100): {issues}")
                logger.warning("Pipeline %s stage %d (%s) REJECTED by contract: %s",
                               run.id, stage_idx, stage_name, issues)
                return None

            content = _extract_content(result)
            summary = content[:300] if content else ''

            # Log warning if output is borderline
            if validation['recommendation'] == 'accept_with_warning':
                logger.warning("Pipeline %s stage %d (%s) accepted with warnings: %s",
                               run.id, stage_idx, stage_name, validation['issues'])

            deliverable_id = _save_stage_deliverable(
                workspace=workspace, stage_name=stage_name, agent_name=agent_name,
                content=content, brief=brief, run_id=str(run.id), user=run.triggered_by,
            )

            output = {
                'stage_name': stage_name,
                'agent': agent_name,
                'summary': summary,
                'deliverable_id': str(deliverable_id) if deliverable_id else None,
                'full_content': content[:2000] if content else '',
                'quality_score': validation['quality_score'],
            }

            _update_stage(run, stage_idx, 'completed', output={
                'message': summary[:500],
                'agent': agent_name,
                'deliverable_id': str(deliverable_id) if deliverable_id else None,
                'quality_score': validation['quality_score'],
            })
            logger.info("Pipeline %s stage %d (%s) completed (quality: %d/100)",
                        run.id, stage_idx, stage_name, validation['quality_score'])
            return output
        else:
            error_msg = str(result.message)[:500] if result and result.message else 'No result'
            _update_stage(run, stage_idx, 'failed', error=error_msg)

    except _FuturesTimeout:
        _update_stage(run, stage_idx, 'failed', error=f'Timed out after {timeout}s')
        logger.error("Pipeline %s stage %d (%s) TIMED OUT", run.id, stage_idx, stage_name)

    except Exception as e:
        _update_stage(run, stage_idx, 'failed', error=str(e)[:500])
        logger.error("Pipeline %s stage %d (%s) error: %s", run.id, stage_idx, stage_name, e)

    return None


def _extract_content(result) -> str:
    """Extract meaningful content from an AgentResult using universal extractor."""
    from core.services.agent_content_extractor import extract_deliverable_content
    return extract_deliverable_content(result)


def _save_stage_deliverable(workspace, stage_name, agent_name, content, brief, run_id, user):
    """Save stage output as a workspace-scoped Deliverable."""
    try:
        from core.models_deliverables import Deliverable
        topic = brief.get('topic', workspace.name) if brief else workspace.name
        deliverable = Deliverable.objects.create(
            title=f"{stage_name}: {topic}"[:255],
            deliverable_type='document',
            category=f'Pipeline — {stage_name}',
            agent_name=agent_name,
            content=content,
            content_format='markdown',
            workspace=workspace,
            user=user,
            is_saved=True,
            metadata={'pipeline_run_id': run_id, 'stage_name': stage_name,
                      'workspace_brief_topic': brief.get('topic', '') if brief else ''},
        )
        return deliverable.id
    except Exception as e:
        logger.error("Failed to save stage deliverable: %s", e)
        return None


def _build_task_description(stage, brief, workspace_name, previous_outputs=None):
    """Build task description from stage + brief + all previous outputs."""
    parts = [stage.get('description', f"Execute {stage.get('name', 'stage')} for {workspace_name}")]

    if brief:
        for key, label in [('topic', 'Topic/Focus'), ('audience', 'Target audience'),
                           ('tone', 'Tone'), ('notes', 'Additional context')]:
            if brief.get(key):
                parts.append(f"{label}: {brief[key]}")
        if brief.get('focus_areas') and isinstance(brief['focus_areas'], list):
            parts.append(f"Focus areas: {', '.join(brief['focus_areas'])}")

    # Thread ALL previous outputs as context (not just the last one)
    if previous_outputs:
        context_parts = []
        for prev in previous_outputs:
            prev_name = prev.get('stage_name', 'Previous')
            prev_content = prev.get('full_content', prev.get('summary', ''))
            if prev_content:
                context_parts.append(f"--- {prev_name} Output ---\n{prev_content[:1500]}")
        if context_parts:
            parts.append("\n\n" + "\n\n".join(context_parts))

    return '. '.join(parts[:6]) + (parts[-1] if len(parts) > 6 else '')


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


def _run_quality_gates(run, brief, previous_outputs):
    """
    Run quality gates after discovery stages.
    Returns {'proceed': bool, 'reason': str, 'details': dict}.
    """
    from core.services.pipeline_quality_gates import check_topic_alignment, check_research_depth

    # Gate 1: Topic Alignment
    alignment = check_topic_alignment(brief, previous_outputs)
    if not alignment['passed']:
        logger.warning(
            "Pipeline %s topic alignment FAILED: score=%s, recommendation=%s",
            run.id, alignment['score'], alignment['recommendation'],
        )

        if alignment['recommendation'] == 'escalate':
            return {
                'proceed': False,
                'reason': alignment['details'],
                'gate': 'topic_alignment',
                'details': alignment,
            }

        # For 'retry' recommendation — log it but let it proceed with a warning
        # (Full retry logic is Phase 2)
        logger.warning(
            "Pipeline %s topic alignment borderline (score=%s) — proceeding with warning",
            run.id, alignment['score'],
        )

    # Gate 2: Research Depth
    depth = check_research_depth(previous_outputs)
    if not depth['passed']:
        logger.warning(
            "Pipeline %s research depth FAILED: %s",
            run.id, depth['details'],
        )
        # Don't hard-stop for depth — log warning and continue
        # (Agents can still produce useful output from shallow research)

    logger.info(
        "Pipeline %s quality gates passed: alignment=%s/100, depth=%s chars",
        run.id, alignment['score'], depth.get('total_content_length', 0),
    )

    return {
        'proceed': True,
        'reason': 'Quality gates passed',
        'alignment': alignment,
        'depth': depth,
    }
