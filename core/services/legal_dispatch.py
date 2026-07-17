"""Shared legal-drafting dispatch helper (S2803 Phase 3.0).

One function drives every drafting dispatch — the UI `POST /api/legal/draft/`
endpoint AND Rigby PA's `_handle_legal_agent`. Both routes:
  1. Require disclaimer_acknowledged=True (raises DisclaimerRequired otherwise)
  2. Dispatch draft_legal_document_task.delay(...)
  3. Write a LegalDocumentDispatchLog row (compliance evidence)

Rigby Phase 3.0 SIGN Fold 2 mitigation: prevents disclaimer-bypass through
the PA path + unifies audit surface.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DisclaimerRequired(Exception):
    """Raised when a caller attempts drafting without acknowledging the disclaimer."""


def dispatch_legal_draft(
    *,
    user,
    task_description: str,
    disclaimer_acknowledged: bool,
    ip_address: Optional[str] = None,
    user_agent: str = '',
    client_session_pin: str = '',
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Dispatch a legal drafting task and record the compliance audit row.

    Raises:
        DisclaimerRequired: caller did not set disclaimer_acknowledged=True.

    Returns:
        {'task_id': str, 'dispatch_log_id': str} on success.
        {'success': False, 'error': str} on Celery broker failure.
    """
    if not disclaimer_acknowledged:
        raise DisclaimerRequired(
            'disclaimer_acknowledged=True is required. This tool provides general '
            'legal information, not legal advice.'
        )

    from core.models_legal_audit import LegalDocumentDispatchLog
    from core.tasks import draft_legal_document_task

    user_id = getattr(user, 'id', None)
    try:
        task = draft_legal_document_task.delay(
            task_description=task_description,
            context=context or {},
            user_id=user_id,
        )
    except Exception as exc:
        logger.error(f"[LEGAL_DISPATCH] Celery dispatch failed: {exc}")
        return {
            'success': False,
            'error': f'Task queue unavailable: {type(exc).__name__}. Please try again.',
        }

    dispatch_log = LegalDocumentDispatchLog.objects.create(
        user=user,
        task_id=str(task.id),
        task_description=task_description,
        ip_address=ip_address,
        user_agent=(user_agent or '')[:500],
        client_session_pin=(client_session_pin or '')[:64],
        disclaimer_acknowledged=True,
        status='dispatched',
    )

    return {
        'task_id': str(task.id),
        'dispatch_log_id': str(dispatch_log.id),
    }
