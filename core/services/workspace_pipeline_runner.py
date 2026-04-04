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

    # Create a content packet to group all deliverables from this run
    packet = None
    try:
        from core.models_deliverables import ContentPacket
        topic = brief.get('topic', workspace.name) if brief else workspace.name
        packet = ContentPacket.objects.create(
            workspace=workspace,
            pipeline_run=run,
            title=f"Newsletter: {topic[:200]}",
            status='draft',
            created_by=run.triggered_by,
        )
        run._packet_id = str(packet.id)  # Stash for stage deliverable linking
        logger.info("Pipeline %s: created content packet %s", run.id, packet.id)
    except Exception as e:
        run._packet_id = None
        logger.warning("Pipeline %s: failed to create content packet: %s", run.id, e)

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

                # Generate Evidence Cards ONCE after discovery gate passes
                # Runs at pipeline level with its own timeout — not inside stage timeout
                try:
                    from core.services.evidence_cardifier import generate_evidence_cards, format_cards_for_writer
                    from concurrent.futures import ThreadPoolExecutor, TimeoutError as _CardTimeout

                    research_text = '\n\n---\n\n'.join(
                        p.get('full_content', '') for p in previous_outputs
                        if p.get('agent') in ('ResearchAgent', 'TopicMinerAgent') and p.get('full_content')
                    )
                    if research_text:
                        with ThreadPoolExecutor(max_workers=1) as card_executor:
                            card_future = card_executor.submit(
                                generate_evidence_cards,
                                research_output=research_text,
                                brief_topic=brief.get('topic', '') if brief else '',
                                brief=brief,
                                max_cards=12,
                            )
                            try:
                                cards = card_future.result(timeout=60)  # 60s max for card generation
                                if cards:
                                    run._evidence_cards = cards
                                    run._evidence_cards_formatted = format_cards_for_writer(
                                        cards, research_summary=research_text[:600],
                                    )
                                    logger.info("Pipeline %s: generated %d Evidence Cards", run.id, len(cards))
                                else:
                                    run._evidence_cards = []
                                    run._evidence_cards_formatted = ''
                            except _CardTimeout:
                                logger.warning("Pipeline %s: Evidence Card generation timed out (60s) — proceeding without cards", run.id)
                                run._evidence_cards = []
                                run._evidence_cards_formatted = ''
                except Exception as e:
                    logger.warning("Pipeline %s: Evidence Card generation failed: %s — proceeding without", run.id, e)
                    run._evidence_cards = []
                    run._evidence_cards_formatted = ''

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

    # GPT-crafted task description — replaces rigid templates with intelligent prompts
    task_desc = _craft_intelligent_prompt(stage, brief, workspace.name, agent_name, previous_outputs)

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
            # Extract actual title from content (first line or heading)
            content_title = ''
            for line in raw.split('\n'):
                line = line.strip().lstrip('#').strip()
                if line and len(line) > 10:
                    content_title = line[:200]
                    break
            content_title = content_title or brief.get('topic', 'Draft') if brief else 'Draft'

            # EditorAgent expects content as a dict with title/sections/conclusion
            # Other agents accept a plain string. Provide both formats.
            context['content'] = {
                'title': content_title,
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
                logger.info(
                    "Pipeline %s: collected %d chars of research from %s for downstream writer",
                    run.id, len(content), agent,
                )
        if research_content_parts:
            combined = '\n\n---\n\n'.join(research_content_parts)
            context['research'] = combined
            logger.info(
                "Pipeline %s: injected %d chars of research into context['research'] (%d sources)",
                run.id, len(combined), len(research_content_parts),
            )

            # Evidence Cards are generated once at the pipeline level (not per-stage)
            # and cached in run._evidence_cards_formatted. See execute_pipeline_run().
            if hasattr(run, '_evidence_cards_formatted') and run._evidence_cards_formatted:
                context['evidence_cards'] = run._evidence_cards
                context['evidence_cards_formatted'] = run._evidence_cards_formatted

        # Collect ALL review feedback (editor verdicts + fact check flags)
        # for the rewrite stage to use
        review_feedback_parts = []
        draft_content = ''
        for prev in previous_outputs:
            prev_agent = prev.get('agent', '')
            prev_name = prev.get('stage_name', '')
            prev_content = prev.get('full_content', '')

            # Capture the original draft for rewrite
            if prev_agent == 'ContentWriterAgent' and prev_content:
                draft_content = prev_content

            # Collect editor and fact check feedback
            if prev_agent in ('EditorAgent', 'ContrarianAgent') and prev_content:
                review_feedback_parts.append(
                    f"=== {prev_name} ({prev_agent}) Feedback ===\n{prev_content}"
                )

        if review_feedback_parts:
            context['review_feedback'] = '\n\n'.join(review_feedback_parts)
            logger.info(
                "Pipeline %s: injected %d review feedback sources for rewrite",
                run.id, len(review_feedback_parts),
            )
        if draft_content:
            context['original_draft'] = draft_content

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
                packet_id=getattr(run, '_packet_id', None),
            )

            output = {
                'stage_name': stage_name,
                'agent': agent_name,
                'summary': summary,
                'deliverable_id': str(deliverable_id) if deliverable_id else None,
                'full_content': content[:8000] if content else '',
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


STAGE_TO_ROLE = {
    'Topic Mining': 'research',
    'Deep Research': 'research',
    'Content Strategy': 'strategy',
    'Write Draft': 'draft',
    'Edit & Polish': 'edit_review',
    'Fact Check': 'fact_check',
    'Final Rewrite': 'rewrite',
    'SEO & Headlines': 'seo',
    'Hooks & Distribution': 'distribution',
}


def _save_stage_deliverable(workspace, stage_name, agent_name, content, brief, run_id, user, packet_id=None):
    """Save stage output as a workspace-scoped Deliverable and link to content packet."""
    try:
        from core.models_deliverables import Deliverable, ContentPacketItem, ContentPacket
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

        # Link to content packet if available
        if packet_id:
            try:
                packet = ContentPacket.objects.get(id=packet_id)
                role = STAGE_TO_ROLE.get(stage_name, 'other')
                order = list(STAGE_TO_ROLE.keys()).index(stage_name) if stage_name in STAGE_TO_ROLE else 99
                is_primary = (role == 'rewrite') or (role == 'draft' and stage_name == 'Write Draft')
                ContentPacketItem.objects.create(
                    packet=packet,
                    deliverable=deliverable,
                    role=role,
                    order=order,
                    is_primary=is_primary,
                )
            except Exception as e:
                logger.warning("Failed to link deliverable to packet: %s", e)

        return deliverable.id
    except Exception as e:
        logger.error("Failed to save stage deliverable: %s", e)
        return None


def _craft_intelligent_prompt(stage, brief, workspace_name, agent_name, previous_outputs=None):
    """
    Use GPT to craft an intelligent, conversational task description for the agent.

    Instead of rigid template assembly ("Topic: X. Audience: Y. Previous output..."),
    GPT writes the actual task prompt — like a creative director briefing a specialist.
    This produces the same quality as WorkflowAgent's GPT-orchestrated prompts while
    keeping the pipeline runner's structure, quality gates, and deliverable saving.

    Falls back to template assembly if the LLM call fails (resilient).
    """
    stage_name = stage.get('name', 'stage')
    stage_description = stage.get('description', f'Execute {stage_name}')

    # Build the context summary for GPT
    brief_block = ''
    if brief:
        brief_parts = []
        if brief.get('topic'):
            brief_parts.append(f"Topic: {brief['topic']}")
        if brief.get('audience'):
            brief_parts.append(f"Target audience: {brief['audience']}")
        if brief.get('tone'):
            brief_parts.append(f"Tone: {brief['tone']}")
        if brief.get('focus_areas') and isinstance(brief['focus_areas'], list):
            brief_parts.append(f"Focus areas: {', '.join(brief['focus_areas'])}")
        if brief.get('distribution_hook'):
            brief_parts.append(f"Distribution angle: {brief['distribution_hook']}")
        if brief.get('notes'):
            brief_parts.append(f"Notes: {brief['notes']}")
        brief_block = '\n'.join(brief_parts)

    previous_block = ''
    if previous_outputs:
        prev_parts = []
        for prev in previous_outputs:
            prev_name = prev.get('stage_name', 'Previous stage')
            prev_agent = prev.get('agent', '')
            prev_content = prev.get('full_content', prev.get('summary', ''))
            quality = prev.get('quality_score', '')
            if prev_content:
                # Give GPT more context than the old 1500 char truncation
                prev_parts.append(
                    f"=== {prev_name} ({prev_agent}) ===\n"
                    f"{prev_content[:4000]}"
                    f"{f' [Quality: {quality}/100]' if quality else ''}"
                )
        previous_block = '\n\n'.join(prev_parts)

    # Detect if this is an editing/polishing/review stage (not a creation stage)
    is_editing_stage = any(kw in stage_name.lower() for kw in ['edit', 'polish', 'review', 'fact check', 'seo', 'headline', 'distribution', 'hook'])

    editing_instruction = ''
    if is_editing_stage and previous_outputs:
        editing_instruction = f"""
CRITICAL: This is an EDITING stage, NOT a writing stage. {agent_name} must work on
the EXISTING content from previous stages — do NOT write new content from scratch.
The content to edit/review is provided in the previous stage outputs below.
Tell {agent_name} to improve, polish, check, or optimize the EXISTING draft."""

    crafting_prompt = f"""You are a creative director briefing a specialist agent for a content pipeline.

Write a detailed, conversational task description for {agent_name} to execute the "{stage_name}" stage.

Stage purpose: {stage_description}
Workspace: {workspace_name}
{editing_instruction}

WORKSPACE BRIEF:
{brief_block or 'No brief provided.'}

{f'PREVIOUS STAGE OUTPUTS:{chr(10)}{previous_block}' if previous_block else 'This is the first stage — no previous outputs.'}

Write 2-4 paragraphs that:
1. Clearly state what {agent_name} should produce
2. Reference specific findings from previous stages (if any)
3. Specify the target audience, tone, and any constraints from the brief
4. Set quality expectations (what "great" looks like for this stage)
5. Include any specific instructions from the brief notes

Write the task as if you're directly briefing the agent. Be specific, not generic.
Do NOT include meta-instructions about "being a creative director" — just write the task itself."""

    try:
        from core.llm_enforcer import LLMEnforcer
        enforcer = LLMEnforcer()
        result = enforcer.enforce_real_ai(
            prompt=crafting_prompt,
            agent_name='PipelinePromptCrafter',
            task_type='content',
            max_tokens=800,
        )
        crafted = result.get('response', '')
        if crafted and len(crafted) > 100:
            logger.info(
                "Pipeline prompt crafted by GPT for %s/%s (%d chars)",
                stage_name, agent_name, len(crafted),
            )
            return crafted
    except Exception as e:
        logger.warning("GPT prompt crafting failed for %s/%s: %s — falling back to template", stage_name, agent_name, e)

    # Fallback: template-based description (old behavior)
    return _build_template_description(stage, brief, workspace_name, previous_outputs)


def _build_template_description(stage, brief, workspace_name, previous_outputs=None):
    """Fallback template-based task description if GPT crafting fails."""
    parts = [stage.get('description', f"Execute {stage.get('name', 'stage')} for {workspace_name}")]

    if brief:
        for key, label in [('topic', 'Topic/Focus'), ('audience', 'Target audience'),
                           ('tone', 'Tone'), ('notes', 'Additional context')]:
            if brief.get(key):
                parts.append(f"{label}: {brief[key]}")
        if brief.get('focus_areas') and isinstance(brief['focus_areas'], list):
            parts.append(f"Focus areas: {', '.join(brief['focus_areas'])}")

    if previous_outputs:
        context_parts = []
        for prev in previous_outputs:
            prev_name = prev.get('stage_name', 'Previous')
            prev_content = prev.get('full_content', prev.get('summary', ''))
            if prev_content:
                context_parts.append(f"--- {prev_name} Output ---\n{prev_content[:3000]}")
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
