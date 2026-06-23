"""
Universal Receipt Contract (URC) v0.1 — shared envelope helpers.

Session 1209 — spec deliverable 6f09233c-c984-4303-87c4-e67b94390030
on Initiative 29154d73-… (Platform Capability Audit). Q1-Q5 locked on
conversation pa-61c7b47d201d4591.

This module is the single source of truth for the URC envelope. It is
imported by every writeback callsite that persists AgentExecution
output_data:

  - core/tasks_agents.py::_impl_execute_agent_task (PR #2473)
  - core/agent_router.py::_complete_execution (Session 1209 follow-up)

The original Phase A implementation inlined the helpers in
tasks_agents.py. Session 1209's fleet smoke surfaced that
WorkflowAgent's sub-dispatches go through the synchronous router path
(agent_router._complete_execution), which never saw the URC envelope.
Extracting the helpers here lets both writeback paths emit the same
contract without duplicating logic.

Design contract:
- Pure functions. No Django imports. No DB access. No I/O.
- Input shapes are primitive (str/bool/int/dict). Callers extract
  these from their result objects before calling.
- enrich_output_data() mutates the base dict in place AND returns it
  (caller convenience — chain or assign).
- Precedence: skipped > timeout > error > contract_violation > success
  (Q5 lock: defensive — non-empty error string forces 'error' even
  when success=True).
"""

import re as _re
from typing import Any, Dict, Optional, Tuple


_URC_UUID_PATTERN = _re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)
_URC_LONG_HEX_PATTERN = _re.compile(r'[0-9a-f]{16,}')
_URC_RECEIPT_VALID_STATUSES = frozenset({'ok', 'skipped', 'error'})


def _is_skipped(success: bool, data: Any) -> bool:
    """Q1 lock: agent reports success with explicit skip marker in data."""
    return (
        success is True
        and isinstance(data, dict)
        and data.get('skipped') is True
    )


def _is_timeout(success: bool, error: Optional[str]) -> bool:
    """Q2 lock: string-match the wall-clock-timeout pattern set in tasks_agents.py."""
    return (
        success is False
        and bool(error)
        and 'wall-clock timeout' in error
    )


def _receipt_violation_reason(payload: Any) -> Optional[str]:
    """Q3 lock: v0 minimal receipt schema check.

    Returns None when the payload satisfies the receipt schema, else a
    short reason string suitable for warning metadata.
    """
    if not isinstance(payload, dict):
        return 'not_dict'
    if 'status' not in payload:
        return 'missing_status'
    if payload['status'] not in _URC_RECEIPT_VALID_STATUSES:
        return 'invalid_status'
    if payload['status'] == 'error':
        msg = payload.get('message')
        if not (isinstance(msg, str) and msg.strip()):
            return 'error_missing_message'
    return None


def _normalize_error_signature(error_string: Optional[str]) -> Optional[str]:
    """Q4 lock: string-only normalize. First line, strip UUIDs/long hex, ≤80 chars."""
    if not error_string:
        return None
    s = str(error_string).split('\n', 1)[0]
    s = _URC_UUID_PATTERN.sub('{id}', s)
    s = _URC_LONG_HEX_PATTERN.sub('{hex}', s)
    s = s.strip()
    if len(s) > 80:
        s = s[:80]
    return s or None


def compute_run_status(
    success: bool,
    error: Optional[str],
    data: Any,
    input_context: Optional[Dict[str, Any]],
) -> Tuple[str, Optional[str]]:
    """Q5 lock (Rigby tweak): defensive error path fires whenever error is non-empty.

    Precedence: skipped > timeout > error > contract_violation > success.
    Returns (status, violation_reason_or_None).
    """
    if _is_skipped(success, data):
        return ('skipped', None)
    if _is_timeout(success, error):
        return ('timeout', None)
    if (not success) or bool(error):
        return ('error', None)
    if isinstance(input_context, dict) and input_context.get('mode') == 'receipt_only':
        reason = _receipt_violation_reason(data)
        if reason is not None:
            return ('contract_violation', reason)
    return ('success', None)


def enrich_output_data(
    base_output: Optional[Dict[str, Any]],
    *,
    agent_name: str,
    success: bool,
    error: Optional[str],
    message: Optional[str],
    data: Any,
    execution_time_ms: Optional[int],
    input_context: Optional[Dict[str, Any]],
    started_at_iso: Optional[str] = None,
    completed_at_iso: Optional[str] = None,
    deliverable_id: Optional[str] = None,
    attempts_used: Optional[int] = None,
) -> Dict[str, Any]:
    """Layer URC v0.1 envelope onto ``base_output``; mutates and returns it.

    Existing keys in ``base_output`` (legacy + canonical shapes) are
    preserved. URC keys are written additively. The ``warnings`` key is
    initialized to an empty list if missing, then a structured
    RECEIPT_CONTRACT_VIOLATION entry is appended when applicable.

    Required by callers:
      - agent_name, success, error, data: needed to compute run_status
        and error fields
      - execution_time_ms: mirrored as latency_ms (may be None)
      - input_context: read for the receipt_only mode predicate
      - completed_at_iso: should be set by caller (timezone.now().isoformat())

    Optional:
      - message: fallback for error_signature when error is empty
      - started_at_iso: emitted only when set; absent key is the
        documented "agent never called start_execution()" case
      - deliverable_id: mirrored into artifacts as {type:'deliverable', id}
      - attempts_used: mirrored to top-level when set (PR #2471 convention)
    """
    if base_output is None:
        base_output = {}
    # warnings list contract: always present, always a list
    if not isinstance(base_output.get('warnings'), list):
        base_output['warnings'] = []
    status, violation_reason = compute_run_status(success, error, data, input_context)
    if status == 'contract_violation' and violation_reason:
        base_output['warnings'].append({
            'type': 'RECEIPT_CONTRACT_VIOLATION',
            'message': f'receipt_only mode: {violation_reason}',
            'meta': {'predicate': violation_reason},
        })
    if status == 'contract_violation':
        err_msg = f'receipt_only mode: {violation_reason}'
        err_sig_input = f'RECEIPT_CONTRACT_VIOLATION: {violation_reason}'
    elif status in ('error', 'timeout'):
        err_msg = error or message or None
        err_sig_input = error or message
    else:  # success or skipped
        err_msg = None
        err_sig_input = None
    base_output['agent_name'] = agent_name
    base_output['run_status'] = status
    base_output['latency_ms'] = execution_time_ms
    base_output['error_signature'] = _normalize_error_signature(err_sig_input)
    base_output['error_message'] = err_msg
    artifacts = []
    if deliverable_id:
        artifacts.append({'type': 'deliverable', 'id': deliverable_id})
    base_output['artifacts'] = artifacts
    if started_at_iso:
        base_output['started_at'] = started_at_iso
    if completed_at_iso is not None:
        base_output['completed_at'] = completed_at_iso
    if deliverable_id and 'deliverable_id' not in base_output:
        base_output['deliverable_id'] = deliverable_id
    if attempts_used is not None and 'attempts_used' not in base_output:
        base_output['attempts_used'] = attempts_used
    return base_output
