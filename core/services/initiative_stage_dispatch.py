"""Central enqueue helper for ``generate_initiative_stage_document``.

Introduced as the S2981 follow-up (spec deliverable
``2a196415-19cf-4bda-87b5-1c4233a5cd9d``) after a Celery task failed with
``Initiative.DoesNotExist``: a ResearchAgent binding directive injected an
initiative_id that no longer resolved, the task was enqueued anyway, and the
only trail was the Celery failure with no persisted link back to the caller.

This module gives every stage-doc enqueue two things:

1. **Enqueue-time validation.** Missing or unresolvable ``initiative_id`` is
   rejected before the task hits the broker. The caller gets a typed dict
   ``{success: False, reason: 'initiative_not_found', ...}`` instead of a
   silently-failing async task.
2. **Durable provenance.** Every valid enqueue writes an ``AgentExecution``
   row owned by the synthetic ``InitiativeStageDispatch`` agent capturing:
   ``task_name``, ``celery_task_id``, ``initiative_id``, ``stage_id``,
   ``source_execution_id``, ``trace_id``, and ``triggered_by``. That row is
   queryable via ORM and lets ``mark_task_outcome`` reconcile the row's
   status when the Celery task finishes or fails.

The task implementation calls back into ``mark_task_outcome`` from its
success + failure branches so a Celery FAILURE never leaves a stale
``in_progress`` provenance row behind.
"""

from __future__ import annotations

import logging
import uuid as _uuid
from typing import Any, Dict, Optional

from django.core.exceptions import ValidationError
from django.utils import timezone

logger = logging.getLogger(__name__)

DISPATCH_TASK_NAME = 'core.tasks.generate_initiative_stage_document'
DISPATCH_AGENT_NAME = 'InitiativeStageDispatch'
_PROVENANCE_SOURCE = 'initiative_stage_dispatch_queue'


def _resolve_stage_id(initiative, stage_num: int) -> Optional[str]:
    try:
        from core.models_document_registry import InitiativeStage
        stage = InitiativeStage.objects.filter(
            initiative=initiative, stage=stage_num
        ).first()
        return str(stage.id) if stage else None
    except Exception:
        return None


def _coerce_trace_uuid(trace_id: Any) -> Optional[_uuid.UUID]:
    if trace_id in (None, '', 0):
        return None
    if isinstance(trace_id, _uuid.UUID):
        return trace_id
    try:
        return _uuid.UUID(str(trace_id))
    except (ValueError, TypeError, AttributeError):
        return None


def _create_queue_provenance(
    *,
    initiative,
    stage_num: int,
    stage_id: Optional[str],
    source_execution_id: Optional[str],
    trace_id: Any,
    triggered_by: Optional[str],
) -> Optional[str]:
    """Persist an ``AgentExecution`` row marking the enqueue event.

    Best-effort. Returns the row id on success, ``None`` on failure — never
    raises, because provenance must not be able to block a real enqueue.
    """
    try:
        from core.models_unified_system import Agent, AgentExecution
        agent, _ = Agent.objects.get_or_create(
            name=DISPATCH_AGENT_NAME,
            defaults={
                'agent_type': 'system',
                'description': (
                    'Provenance receipts for generate_initiative_stage_document '
                    'enqueue events (S2981 follow-up).'
                ),
                'specialization': '',
                'is_active': True,
            },
        )
        input_data: Dict[str, Any] = {
            'source': _PROVENANCE_SOURCE,
            'execution_kind': 'stage_doc_enqueue',
            'task_name': DISPATCH_TASK_NAME,
            'initiative_id': str(initiative.id),
            'stage_num': stage_num,
            'stage_id': stage_id,
            'source_execution_id': source_execution_id,
            'triggered_by': triggered_by or 'unknown',
        }
        row = AgentExecution.objects.create(
            agent=agent,
            user=None,
            task=(
                f'Stage-doc enqueue: initiative={initiative.id} '
                f'stage={stage_num}'
            )[:500],
            status='pending',
            owner_agent=DISPATCH_AGENT_NAME,
            parent_object_type='initiative',
            parent_object_id=initiative.id,
            input_data=input_data,
            output_data={},
            trace_id=_coerce_trace_uuid(trace_id),
        )
        return str(row.id)
    except Exception as exc:
        logger.warning(
            "[STAGE-DISPATCH] Failed to persist queue provenance "
            "(%s: %s) — continuing without durable receipt",
            type(exc).__name__, exc,
        )
        return None


def _finalize_queue_provenance(
    provenance_id: Optional[str],
    *,
    celery_task_id: Optional[str],
    status: str,
    error: Optional[str] = None,
) -> None:
    """Stamp the queue-provenance row after ``.delay()`` returns.

    Silent on failure — provenance is best-effort.
    """
    if not provenance_id:
        return
    try:
        from core.models_unified_system import AgentExecution
        exec_row = AgentExecution.objects.filter(id=provenance_id).first()
        if not exec_row:
            return
        exec_row.status = status
        if celery_task_id and not exec_row.celery_task_id:
            exec_row.celery_task_id = celery_task_id
        merged_input = dict(exec_row.input_data or {})
        if celery_task_id:
            merged_input['celery_task_id'] = celery_task_id
        exec_row.input_data = merged_input
        if error:
            exec_row.error_message = str(error)[:2000]
        if status in ('completed', 'failed', 'cancelled'):
            exec_row.completed_at = timezone.now()
        exec_row.save(update_fields=[
            'status', 'celery_task_id', 'input_data',
            'error_message', 'completed_at',
        ])
    except Exception as exc:
        logger.debug(
            "[STAGE-DISPATCH] Failed to finalize queue provenance %s: %s",
            provenance_id, exc,
        )


def queue_stage_document_generation(
    initiative_id: Any,
    stage_num: int,
    *,
    source_execution_id: Optional[str] = None,
    trace_id: Any = None,
    triggered_by: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate + enqueue ``generate_initiative_stage_document`` with provenance.

    Returns a typed dict::

        {
          'success': bool,
          'task_id': str | None,
          'provenance_execution_id': str | None,
          'initiative_id': str,
          'stage_num': int,
          'error': str | None,        # non-empty on failure
          'reason': str | None,       # short reason code on failure
        }

    The Celery task is not enqueued if ``initiative_id`` is missing,
    unparseable, or not present in the ``Initiative`` table. Callers should
    inspect ``result['success']`` and either surface the error to the user
    or log it, but MUST NOT retry blindly — a missing initiative_id is a
    caller bug, not a transient failure.
    """
    result: Dict[str, Any] = {
        'success': False,
        'task_id': None,
        'provenance_execution_id': None,
        'initiative_id': str(initiative_id) if initiative_id is not None else '',
        'stage_num': stage_num,
        'error': None,
        'reason': None,
    }

    if not initiative_id:
        result.update(
            error='initiative_id missing',
            reason='missing_initiative_id',
        )
        logger.warning(
            "[STAGE-DISPATCH] Refusing enqueue: initiative_id missing "
            "(stage=%s triggered_by=%s source_execution=%s trace=%s)",
            stage_num, triggered_by, source_execution_id, trace_id,
        )
        return result

    if not isinstance(stage_num, int) or not (1 <= stage_num <= 5):
        result.update(
            error=f'stage_num must be int in [1,5], got {stage_num!r}',
            reason='invalid_stage_num',
        )
        logger.warning(
            "[STAGE-DISPATCH] Refusing enqueue: invalid stage_num=%r "
            "for initiative=%s (triggered_by=%s)",
            stage_num, initiative_id, triggered_by,
        )
        return result

    from core.models_document_registry import Initiative
    try:
        initiative = Initiative.objects.get(id=initiative_id)
    except (Initiative.DoesNotExist, ValidationError, ValueError, TypeError) as exc:
        result.update(
            error=f'{type(exc).__name__}: {exc}',
            reason='initiative_not_found',
        )
        logger.warning(
            "[STAGE-DISPATCH] Refusing enqueue: initiative %s not found "
            "(stage=%s triggered_by=%s source_execution=%s trace=%s) — %s",
            initiative_id, stage_num, triggered_by,
            source_execution_id, trace_id, exc,
        )
        return result

    stage_id = _resolve_stage_id(initiative, stage_num)
    provenance_id = _create_queue_provenance(
        initiative=initiative,
        stage_num=stage_num,
        stage_id=stage_id,
        source_execution_id=source_execution_id,
        trace_id=trace_id,
        triggered_by=triggered_by,
    )
    result['provenance_execution_id'] = provenance_id

    try:
        from core.tasks import generate_initiative_stage_document
        async_result = generate_initiative_stage_document.delay(
            str(initiative.id), stage_num,
        )
        task_id = getattr(async_result, 'id', None)
        task_id = str(task_id) if task_id is not None else None
        result.update(success=True, task_id=task_id)
        logger.info(
            "[STAGE-DISPATCH] Enqueued %s initiative=%s stage=%s "
            "task_id=%s provenance=%s trace=%s triggered_by=%s "
            "source_execution=%s stage_id=%s",
            DISPATCH_TASK_NAME, initiative.id, stage_num, task_id,
            provenance_id, trace_id, triggered_by, source_execution_id,
            stage_id,
        )
        _finalize_queue_provenance(
            provenance_id, celery_task_id=task_id, status='in_progress',
        )
        return result
    except Exception as exc:
        result.update(
            error=f'enqueue failed: {type(exc).__name__}: {exc}',
            reason='enqueue_error',
        )
        logger.error(
            "[STAGE-DISPATCH] Enqueue failed for initiative=%s stage=%s: %s",
            initiative.id, stage_num, exc,
        )
        _finalize_queue_provenance(
            provenance_id, celery_task_id=None, status='failed',
            error=str(exc),
        )
        return result


def mark_task_outcome(
    *,
    celery_task_id: Optional[str],
    status: str,
    error: Optional[str] = None,
) -> int:
    """Reconcile the queue provenance row when the Celery task finishes.

    Called from the task implementation's success + failure branches so a
    Celery FAILURE never leaves a stale ``in_progress`` row (or, worse, a
    "completed" AgentExecution that maps to a Celery failure by ID).

    Matches queue-provenance rows on ``celery_task_id`` — that's the field
    ``_finalize_queue_provenance`` stamped at enqueue time and the field
    the ``AgentExecution.pre_save`` signal auto-stamps for any row created
    inside a Celery task context. Only touches rows still in ``pending`` /
    ``in_progress`` to avoid clobbering downstream state.

    Returns the count of rows updated. Silent on failure.
    """
    if not celery_task_id:
        return 0
    updated = 0
    try:
        from core.models_unified_system import AgentExecution
        rows = AgentExecution.objects.filter(
            celery_task_id=str(celery_task_id),
            status__in=['pending', 'in_progress'],
        )
        for row in rows:
            row.status = status
            if error:
                row.error_message = str(error)[:2000]
            if status in ('completed', 'failed', 'cancelled'):
                row.completed_at = timezone.now()
            row.save(update_fields=[
                'status', 'error_message', 'completed_at',
            ])
            updated += 1
    except Exception as exc:
        logger.debug(
            "[STAGE-DISPATCH] mark_task_outcome swallow (%s: %s)",
            type(exc).__name__, exc,
        )
    return updated
