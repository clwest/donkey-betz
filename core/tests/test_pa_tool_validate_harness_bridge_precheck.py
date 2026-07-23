"""S2909 T2 — bridge availability precheck regression tests.

Pins the v2 bridge-preflight contract:

    - action with no bridge metadata           → dispatches normally
    - action with bridge + probe reachable     → dispatches normally
    - action with bridge + probe unreachable   → 'skipped_bridge_unreachable'
                                                  BEFORE dispatch
    - _probe_bridge caches per-invocation      → one probe per bridge per run

Probe discipline per Rigby T2 SIGN Q4 fold #1: probes reuse the SAME client
the tool uses (never re-derive URLs) — tests monkeypatch those clients.

Origin: S2909 substrate cleanup arc T2 (bridge availability precheck),
Chris Option A ratified, joint Claude+Rigby SIGN.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional
from unittest import mock

from django.test import SimpleTestCase

from core.management.commands.pa_tool_validate_harness import Command


@dataclass
class _FakeResult:
    ok: bool
    result: Any
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class _FakeDispatcher:
    def __init__(self, result: _FakeResult) -> None:
        self._result = result
        self.dispatch_count = 0

    async def execute(self, **_kwargs: Any) -> _FakeResult:
        self.dispatch_count += 1
        return self._result


def _run(
    cmd: Command,
    dispatcher: _FakeDispatcher,
    *,
    tool_name: str = 'fake_tool',
    action: str = 'fake_action',
    bridge: Optional[str] = None,
) -> Dict[str, Any]:
    coro = cmd._run_single_action(  # noqa: SLF001
        dispatcher=dispatcher,
        tool_name=tool_name,
        action=action,
        safety_class='READ_ONLY',
        resolution_source='action',
        bridge=bridge,
    )
    return asyncio.get_event_loop().run_until_complete(coro)


class BridgePrecheckTests(SimpleTestCase):

    def test_no_bridge_metadata_dispatches_normally(self) -> None:
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        row = _run(cmd, dispatcher, bridge=None)
        self.assertEqual(row['expected_outcome'], 'success')
        self.assertEqual(dispatcher.dispatch_count, 1)

    def test_obs_bridge_disabled_skips_before_dispatch(self) -> None:
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.views_obs._obs_enabled', return_value=False,
        ):
            row = _run(cmd, dispatcher, bridge='obs')
        self.assertEqual(row['expected_outcome'], 'skipped_bridge_unreachable')
        self.assertEqual(dispatcher.dispatch_count, 0)
        self.assertIn('bridge=obs', row['notes'] or '')
        self.assertIn('OBS_ENABLED env not set', row['notes'] or '')

    def test_obs_bridge_reachable_dispatches(self) -> None:
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.views_obs._obs_enabled', return_value=True,
        ), mock.patch(
            'core.views_obs._obs_bridge_request',
            return_value=(200, {'ok': True}, 42),
        ):
            row = _run(cmd, dispatcher, bridge='obs')
        self.assertEqual(row['expected_outcome'], 'success')
        self.assertEqual(dispatcher.dispatch_count, 1)

    def test_resolve_node_offline_skips_before_dispatch(self) -> None:
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.agents.resolve_agent.ResolveNodeClient.health_check',
            return_value={'status': 'offline', 'error': 'connection refused'},
        ):
            row = _run(cmd, dispatcher, bridge='resolve_node')
        self.assertEqual(row['expected_outcome'], 'skipped_bridge_unreachable')
        self.assertEqual(dispatcher.dispatch_count, 0)
        self.assertIn('bridge=resolve_node', row['notes'] or '')
        self.assertIn('offline', row['notes'] or '')
        self.assertIn('connection refused', row['notes'] or '')

    def test_resolve_node_reachable_dispatches(self) -> None:
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.agents.resolve_agent.ResolveNodeClient.health_check',
            return_value={'status': 'ok', 'version': '1.0'},
        ):
            row = _run(cmd, dispatcher, bridge='resolve_node')
        self.assertEqual(row['expected_outcome'], 'success')
        self.assertEqual(dispatcher.dispatch_count, 1)

    def test_probe_cached_across_invocations_in_same_run(self) -> None:
        """One probe per bridge per Command instance."""
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.agents.resolve_agent.ResolveNodeClient.health_check',
            return_value={'status': 'offline'},
        ) as probe:
            _run(cmd, dispatcher, bridge='resolve_node', action='a1')
            _run(cmd, dispatcher, bridge='resolve_node', action='a2')
            _run(cmd, dispatcher, bridge='resolve_node', action='a3')
        # Probe should be called exactly once even for 3 dispatches.
        self.assertEqual(probe.call_count, 1)

    def test_unknown_bridge_name_does_not_block(self) -> None:
        """Metadata typo shouldn't accidentally short-circuit real tools."""
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        row = _run(cmd, dispatcher, bridge='typo_bridge_name')
        self.assertEqual(row['expected_outcome'], 'success')
        self.assertEqual(dispatcher.dispatch_count, 1)

    def test_bridge_unreachable_notes_include_reason(self) -> None:
        """Notes must include bridge= label + probe reason for triage."""
        cmd = Command()
        dispatcher = _FakeDispatcher(_FakeResult(ok=True, result={'ok': True}))
        with mock.patch(
            'core.views_obs._obs_enabled', return_value=False,
        ):
            row = _run(cmd, dispatcher, bridge='obs')
        # Format: 'bridge=<name>; <probe reason>'
        self.assertRegex(row['notes'] or '', r'^bridge=obs;\s+')

    def test_reachable_semantics_network_only(self) -> None:
        """HTTP 5xx from bridge is still reachable — application-layer errors
        surface as soft_error on the dispatched call, not bridge_unreachable."""
        cmd = Command()
        # Bridge is up (HTTP 500 counts as reachable per Q4 fold #3);
        # dispatcher returns transport-success + inline error envelope.
        dispatcher = _FakeDispatcher(_FakeResult(
            ok=True,
            result={'ok': False, 'error_code': 'INTERNAL', 'error': 'DB failed'},
        ))
        with mock.patch(
            'core.agents.resolve_agent.ResolveNodeClient.health_check',
            return_value={'status': 'error'},  # HTTP 4xx/5xx, but reachable
        ):
            row = _run(cmd, dispatcher, bridge='resolve_node')
        # Reached dispatch; classified as soft_error (not bridge_unreachable).
        self.assertEqual(row['expected_outcome'], 'soft_error')
        self.assertEqual(dispatcher.dispatch_count, 1)
