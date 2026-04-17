"""
Session 1098 Fix B-full — DeliverableAppend service.

Public API: ``append_to_deliverable(...)``. Writes content to an existing
Deliverable atomically + idempotently, with race protection against
mid-flight Initiative promotion.

Contract:
- **Idempotent**: repeat calls with the same
  ``(deliverable_id, call_id, chunk_index)`` return the existing
  committed row without re-appending. A caller's Celery retry that
  reuses call_id is a safe no-op.
- **Atomic**: the validation + Deliverable.content append + status flip
  all happen inside a single ``transaction.atomic()`` block with
  ``SELECT FOR UPDATE`` on the Deliverable row. No partial writes.
- **Race-protected**: if ``expected_initiative_id`` is provided and the
  Deliverable's live ``initiative_id`` has changed, the append is
  recorded as ``status='superseded'`` and routed to the workspace
  Unassigned bucket (a fallback Deliverable) instead of being applied
  against a stale link.
- **Infra-fail-safe**: integrity errors from the unique constraint are
  caught and translated to an idempotent return (read + return
  existing row).

Guarded by ``settings.DELIVERABLE_APPEND_ENABLED`` (default False). When
off, the helper raises ``FeatureDisabledError`` so callers can fall back
to ``create_deliverable`` (the existing code path).

See ``docs/plans/SESSION_1098_FIX_B_FULL_TICKET.md`` for the design
review that produced this module (Rigby in ``pa-d19c1674b936``).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────── public types ──────────────────────────── #


class FeatureDisabledError(RuntimeError):
    """Raised when DELIVERABLE_APPEND_ENABLED is not set.

    Callers should fall back to ``deliverable_factory.create_deliverable``
    on this exception. The exception class is preserved so kill-switch
    logic can distinguish 'intentionally off' from 'broken'.
    """


@dataclass
class AppendResult:
    """Structured return from ``append_to_deliverable``."""
    call_id: str
    deliverable_id: str
    append_offset: Optional[int]
    status: str  # committed | superseded | failed
    fallback_deliverable_id: Optional[str] = None
    failure_reason: str = ''


# ─────────────────────────── public API ────────────────────────────── #


def append_to_deliverable(
    *,
    deliverable_id: Union[str, uuid.UUID],
    call_id: Union[str, uuid.UUID],
    content: str,
    agent_name: str,
    execution_id: Optional[Union[str, uuid.UUID]] = None,
    expected_initiative_id: Optional[Union[str, uuid.UUID]] = None,
    chunk_index: int = 0,
    routing_metadata: Optional[Dict[str, Any]] = None,
) -> AppendResult:
    """Append ``content`` to the Deliverable identified by
    ``deliverable_id`` atomically + idempotently.

    Parameters:
        deliverable_id: Target Deliverable UUID.
        call_id: Caller-supplied idempotency key. When the caller is an
            LLM-driven agent, pass the LLMCallEvent.call_id — this aligns
            dedupe with the wrapper's telemetry row.
        content: Bytes to append. Empty string is a no-op that still
            commits a record (caller gets ``status='committed'``,
            ``append_offset`` equal to the current Deliverable length).
        agent_name: For dashboard filtering.
        execution_id: Optional AgentExecution.id for correlation.
        expected_initiative_id: If provided, verified inside the
            transaction. Mismatch → ``status='superseded'``.
        chunk_index: 0-based for streaming multi-chunk writes. Unique
            per (deliverable, call_id).
        routing_metadata: Freeform JSON stored on the row.

    Returns:
        AppendResult with final status + offset + fallback_id (set only
        when superseded).

    Raises:
        FeatureDisabledError if settings.DELIVERABLE_APPEND_ENABLED
            is not truthy. Callers should fall back to create_deliverable.
        Deliverable.DoesNotExist if deliverable_id is unknown (no
            retry semantics for a missing target).
    """
    if not getattr(settings, 'DELIVERABLE_APPEND_ENABLED', False):
        raise FeatureDisabledError(
            'DELIVERABLE_APPEND_ENABLED is False; use create_deliverable '
            'or set the flag to enable B-full append semantics.'
        )

    # Lazy imports — the model modules are imported many places and we
    # want this service to stay importable even if the model hasn't
    # been loaded into the app registry yet (e.g., at Django startup).
    from core.models_deliverables import Deliverable
    from core.models_deliverable_appends import DeliverableAppend

    deliv_uuid = _to_uuid(deliverable_id, 'deliverable_id')
    call_uuid = _to_uuid(call_id, 'call_id')
    exec_uuid = _to_uuid(execution_id, 'execution_id', optional=True)
    expected_init_uuid = _to_uuid(
        expected_initiative_id, 'expected_initiative_id', optional=True,
    )

    # Fast path: if the idempotency row already exists committed, return
    # it without touching the Deliverable. Avoids unnecessary locks for
    # routine retries. The transactional path below still handles the
    # race where two retries land concurrently.
    existing = DeliverableAppend.objects.filter(
        deliverable_id=deliv_uuid,
        call_id=call_uuid,
        chunk_index=chunk_index,
    ).first()
    if existing is not None and existing.status == 'committed':
        logger.info(
            '[deliverable_append] idempotent hit — call_id=%s already '
            'committed for deliverable=%s',
            call_uuid, deliv_uuid,
        )
        return AppendResult(
            call_id=str(call_uuid),
            deliverable_id=str(deliv_uuid),
            append_offset=existing.append_offset,
            status='committed',
        )

    # Transactional path. SELECT FOR UPDATE serializes concurrent
    # writers, and the Deliverable.initiative_id re-read inside the
    # lock detects mid-flight promotion.
    try:
        with transaction.atomic():
            locked = (
                Deliverable.objects
                .select_for_update()
                .filter(id=deliv_uuid)
                .first()
            )
            if locked is None:
                raise Deliverable.DoesNotExist(
                    f'Deliverable {deliv_uuid} not found'
                )

            # Race check: did the Initiative link change since the
            # caller resolved expected_initiative_id?
            if (
                expected_init_uuid is not None
                and str(locked.initiative_id or '') != str(expected_init_uuid)
            ):
                logger.warning(
                    '[deliverable_append] superseded — deliverable=%s '
                    'expected_initiative=%s actual_initiative=%s',
                    deliv_uuid, expected_init_uuid, locked.initiative_id,
                )
                fallback_id = _route_to_fallback(
                    deliverable=locked,
                    call_id=call_uuid,
                    content=content,
                    agent_name=agent_name,
                    execution_id=exec_uuid,
                    expected_initiative_id=expected_init_uuid,
                    chunk_index=chunk_index,
                    routing_metadata=routing_metadata,
                )
                return AppendResult(
                    call_id=str(call_uuid),
                    deliverable_id=str(deliv_uuid),
                    append_offset=None,
                    status='superseded',
                    fallback_deliverable_id=fallback_id,
                    failure_reason=(
                        f'initiative mismatch: expected '
                        f'{expected_init_uuid} got {locked.initiative_id}'
                    ),
                )

            # Insert pending row. Unique constraint makes this
            # idempotent — a concurrent writer that got here first
            # will have committed their row by the time this raises
            # IntegrityError, so we re-read and return it.
            # Wrap the INSERT in a nested savepoint so IntegrityError
            # rolls back only the INSERT — leaving the outer SELECT FOR
            # UPDATE transaction alive so we can do the re-read lookup.
            raced = False
            append = None
            try:
                with transaction.atomic():
                    append = DeliverableAppend.objects.create(
                        call_id=call_uuid,
                        deliverable=locked,
                        expected_initiative_id=expected_init_uuid,
                        execution_id=exec_uuid,
                        agent_name=agent_name,
                        content=content,
                        chunk_index=chunk_index,
                        status='pending',
                        routing_metadata=routing_metadata or {},
                    )
            except IntegrityError:
                raced = True

            if raced:
                # The concurrent winner may still be 'pending' — they
                # hold the row-level lock but haven't committed yet.
                # Fall out of the outer atomic and let the caller
                # retry (or poll by calling append_to_deliverable
                # again — same call_id returns the winner's row once
                # they finalize). For the common case the winner has
                # already committed by the time we get here.
                winner = DeliverableAppend.objects.get(
                    deliverable_id=deliv_uuid,
                    call_id=call_uuid,
                    chunk_index=chunk_index,
                )
                logger.info(
                    '[deliverable_append] lost idempotency race — '
                    'returning winner call_id=%s status=%s',
                    call_uuid, winner.status,
                )
                return AppendResult(
                    call_id=str(call_uuid),
                    deliverable_id=str(deliv_uuid),
                    append_offset=winner.append_offset,
                    status=winner.status,
                )

            # Compute offset + apply the append to Deliverable.content.
            prior = locked.content or ''
            append_offset = len(prior)
            new_content = prior + (content or '')
            locked.content = new_content
            locked.preview_content = new_content[:500]
            locked.save(update_fields=['content', 'preview_content', 'updated_at'])

            # Finalize the append row.
            append.status = 'committed'
            append.append_offset = append_offset
            append.committed_at = timezone.now()
            append.save(update_fields=[
                'status', 'append_offset', 'committed_at',
            ])

            logger.info(
                '[deliverable_append] committed call_id=%s deliverable=%s '
                'offset=%d chunk=%d agent=%s',
                call_uuid, deliv_uuid, append_offset, chunk_index, agent_name,
            )
            return AppendResult(
                call_id=str(call_uuid),
                deliverable_id=str(deliv_uuid),
                append_offset=append_offset,
                status='committed',
            )
    except Deliverable.DoesNotExist:
        raise
    except Exception as exc:
        logger.exception(
            '[deliverable_append] FAILED call_id=%s deliverable=%s: %s',
            call_uuid, deliv_uuid, exc,
        )
        # Best-effort: mark the row as failed if it exists, so dashboards
        # can count failures. Don't raise from the telemetry path.
        try:
            DeliverableAppend.objects.filter(
                deliverable_id=deliv_uuid,
                call_id=call_uuid,
                chunk_index=chunk_index,
            ).update(
                status='failed',
                failure_reason=str(exc)[:500],
            )
        except Exception:
            pass
        raise


# ──────────────────────────── helpers ─────────────────────────────── #


def _to_uuid(
    value: Optional[Union[str, uuid.UUID]],
    field_name: str,
    *,
    optional: bool = False,
) -> Optional[uuid.UUID]:
    if value is None:
        if optional:
            return None
        raise ValueError(f'{field_name} is required')
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{field_name} is not a valid UUID: {value!r}') from exc


def _route_to_fallback(
    *,
    deliverable,
    call_id: uuid.UUID,
    content: str,
    agent_name: str,
    execution_id: Optional[uuid.UUID],
    expected_initiative_id: Optional[uuid.UUID],
    chunk_index: int,
    routing_metadata: Optional[Dict[str, Any]],
) -> Optional[str]:
    """Write a superseded-append record + route content to a fallback
    Deliverable in the workspace Unassigned bucket.

    Returns the fallback Deliverable UUID if created, else None.
    """
    from core.models_deliverable_appends import DeliverableAppend
    from core.services.deliverable_factory import create_deliverable

    # Record the superseded append row (best-effort — unique constraint
    # still enforced so retries dedupe).
    try:
        DeliverableAppend.objects.update_or_create(
            deliverable=deliverable,
            call_id=call_id,
            chunk_index=chunk_index,
            defaults=dict(
                expected_initiative_id=expected_initiative_id,
                execution_id=execution_id,
                agent_name=agent_name,
                content=content,
                status='superseded',
                failure_reason=(
                    f'initiative promotion race: expected '
                    f'{expected_initiative_id} but deliverable now links '
                    f'{deliverable.initiative_id}'
                ),
                routing_metadata=routing_metadata or {},
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception(
            '[deliverable_append] failed to record superseded row: %s', exc,
        )

    # Route the content to a fallback deliverable so the work isn't lost.
    # trigger_source='direct' bypasses the MIN_CONTENT_LENGTH gate —
    # superseded content can be any length (an empty superseded append
    # still needs its audit trail).
    try:
        fallback = create_deliverable(
            title=f'[SUPERSEDED INITIATIVE] {agent_name} output',
            content=content,
            agent_name=agent_name,
            category='Superseded',
            deliverable_type='document',
            workspace_id=str(deliverable.workspace_id) if deliverable.workspace_id else None,
            parent_execution_id=str(execution_id) if execution_id else None,
            metadata={
                'trigger_source': 'direct',
                'superseded_from_deliverable_id': str(deliverable.id),
                'expected_initiative_id': str(expected_initiative_id) if expected_initiative_id else None,
                'actual_initiative_id': str(deliverable.initiative_id) if deliverable.initiative_id else None,
                'call_id': str(call_id),
            },
        )
        return str(fallback.id) if fallback else None
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception(
            '[deliverable_append] fallback deliverable creation failed: %s', exc,
        )
        return None


__all__ = [
    'append_to_deliverable',
    'AppendResult',
    'FeatureDisabledError',
]
