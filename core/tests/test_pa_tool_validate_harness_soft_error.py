"""S2909 T1 — harness soft_error classifier regression tests.

Pins the v1 → v2 classifier contract change:

    - ToolResult.ok=False                              → 'error_captured'
    - ToolResult.ok=True + clean response dict         → 'success'
    - ToolResult.ok=True + response {ok: false, ...}   → 'soft_error'
    - ToolResult.ok=True + response {error_code: ...}  → 'soft_error'

Origin: 3-data-point Fold B systemic-drift trigger from S2905-S2908 sweep
batches (87.5% × 2 + 75%). Ratified Chris Option A at S2909 open with
joint Claude+Rigby SIGN on `docs/audits/pa_tools/substrate/S2909_substrate_cleanup_arc_scoping.md`.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

from django.test import SimpleTestCase

from core.management.commands.pa_tool_validate_harness import Command


@dataclass
class _FakeResult:
    """Minimal stand-in for ToolResult sufficient for _run_single_action.

    Real ToolResult carries more fields; the harness classifier reads only
    ``ok``, ``result``, ``error_code``, ``error_message``. Keep the fake
    surface tight so a real-ToolResult refactor doesn't silently drift.
    """
    ok: bool
    result: Any
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class _FakeDispatcher:
    """Dispatcher stub — execute() returns a pre-configured _FakeResult."""

    def __init__(self, result: _FakeResult) -> None:
        self._result = result

    async def execute(self, **_kwargs: Any) -> _FakeResult:
        return self._result


def _run(dispatcher: _FakeDispatcher) -> Dict[str, Any]:
    """Invoke Command._run_single_action with fixed READ_ONLY args."""
    cmd = Command()
    coro = cmd._run_single_action(  # noqa: SLF001 — private-by-convention
        dispatcher=dispatcher,
        tool_name='fake_tool',
        action='fake_action',
        safety_class='READ_ONLY',
        resolution_source='action',
    )
    return asyncio.get_event_loop().run_until_complete(coro)


class SoftErrorClassifierTests(SimpleTestCase):
    """v2 classifier contract."""

    def test_clean_success_stays_success(self) -> None:
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={'action': 'fake_action', 'data': [1, 2, 3]},
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'success')
        self.assertEqual(row['status_code'], 200)

    def test_dispatcher_error_stays_error_captured(self) -> None:
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=False,
            result=None,
            error_code='DISPATCHER_FAIL',
            error_message='dispatcher-layer failure',
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'error_captured')
        self.assertEqual(row['status_code'], 500)
        self.assertIn('error_code=DISPATCHER_FAIL', row['notes'] or '')

    def test_inline_ok_false_reclassifies_to_soft_error(self) -> None:
        """ToolResult.ok=True with inline {ok:false} → soft_error."""
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={
                'action': 'fake_action',
                'ok': False,
                'error': 'inline app-layer failure',
                'error_code': 'INLINE_FAIL',
            },
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'soft_error')
        self.assertEqual(row['status_code'], 200)  # transport still 200
        self.assertIn('inline_error_code=INLINE_FAIL', row['notes'] or '')
        self.assertIn('inline_msg=inline app-layer failure', row['notes'] or '')

    def test_inline_error_code_without_ok_false_reclassifies(self) -> None:
        """Some tools set error_code without setting ok:false — still soft_error."""
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={
                'action': 'fake_action',
                'error_code': 'BRIDGE_UNREACHABLE',
                'error': 'bridge is down',
            },
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'soft_error')

    def test_ok_false_without_error_code_reclassifies(self) -> None:
        """Some tools set ok:false without an explicit error_code."""
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={'action': 'fake_action', 'ok': False},
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'soft_error')

    def test_nested_error_dict_extracts_code(self) -> None:
        """Some tools nest {error: {code: ...}} — capture in notes."""
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={
                'action': 'fake_action',
                'ok': False,
                'error': {'code': 'OBS_DISABLED', 'msg': 'obs not enabled'},
            },
        ))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'soft_error')
        # Nested code uses a distinct label so top-level + nested don't collide.
        self.assertIn('inline_error_nested_code=OBS_DISABLED', row['notes'] or '')
        self.assertIn('inline_msg=obs not enabled', row['notes'] or '')

    def test_non_dict_response_is_not_soft_error(self) -> None:
        """If result.result is not a dict, no inline-envelope check applies."""
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result='some string'))
        row = _run(dispatcher)
        self.assertEqual(row['expected_outcome'], 'success')

    def test_response_shape_keys_still_captured(self) -> None:
        """The response_shape_keys field must still list top-level keys
        regardless of outcome (upstream consumers depend on it).
        """
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={'ok': False, 'error_code': 'X', 'foo': 1, 'bar': 2},
        ))
        row = _run(dispatcher)
        self.assertEqual(
            sorted(row['response_shape_keys']),
            ['bar', 'error_code', 'foo', 'ok'],
        )
