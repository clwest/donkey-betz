"""Session 1228 PR-B — Tier 3 silent-truncation safety tests.

Validates the falsy-or-default pattern applied to ~33 sites with
``int(payload.get('X', N))`` for time-bucket, window, and semantic-width
params across td_handlers_ops/core/content/agents/codejobs. The LLM
autofill of ``0`` must fall through to the documented default instead
of silently truncating results (or, for `max_runtime_seconds`, silently
forcing a 0-second timeout).

Memory rule: ``feedback_llm_autofills_boolean_params_with_false``
(extended to cover int=0 autofill in Session 1227 PR2 root cause).
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.tool_dispatcher import ToolDispatcher


def _dispatch_autopilot(payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_autopilot(  # type: ignore[attr-defined]
        tool_name='autopilot_tool',
        payload=payload,
        user_id=None,
        trace_id='test-pr-b-autopilot',
    )


# ────────────────────────────────────────────────────────────────────
# Autopilot ops — days / hours autofill protection (the largest cluster)
# ────────────────────────────────────────────────────────────────────


class AutopilotDaysHoursAutofillTests(SimpleTestCase):
    """Downstream engines receive the documented default when the payload
    autofills the int param with 0."""

    def test_security_secrets_scan_autofilled_days_zero_uses_default(self):
        with patch(
            'core.services.ops_autopilot.intelligence.SecurityEngine.get_secrets_scan',
            return_value={'scanned': 0},
        ) as mocked:
            _dispatch_autopilot({'action': 'security_secrets_scan', 'days': 0})
            mocked.assert_called_once_with(days=7)

    def test_security_secrets_scan_explicit_days_passes_through(self):
        with patch(
            'core.services.ops_autopilot.intelligence.SecurityEngine.get_secrets_scan',
            return_value={'scanned': 0},
        ) as mocked:
            _dispatch_autopilot({'action': 'security_secrets_scan', 'days': 30})
            mocked.assert_called_once_with(days=30)

    def test_integrity_quality_report_autofilled_hours_zero_uses_default(self):
        with patch(
            'core.services.ops_autopilot.intelligence.DataIntegrityEngine.get_quality_report',
            return_value={},
        ) as mocked:
            _dispatch_autopilot({'action': 'integrity_quality_report', 'hours': 0})
            mocked.assert_called_once_with(hours=24)

    def test_integrity_null_spike_scan_autofilled_hours_zero_uses_default(self):
        with patch(
            'core.services.ops_autopilot.intelligence.DataIntegrityEngine.get_null_spike_scan',
            return_value={},
        ) as mocked:
            _dispatch_autopilot({'action': 'integrity_null_spike_scan', 'hours': 0})
            mocked.assert_called_once_with(hours=24)

    def test_value_events_report_autofilled_days_zero_uses_default(self):
        with patch(
            'core.services.ops_autopilot.intelligence.ValueRealizationEngine.get_value_events_report',
            return_value={},
        ) as mocked:
            _dispatch_autopilot({'action': 'value_events_report', 'days': 0})
            mocked.assert_called_once_with(days=7)

    def test_value_outcome_rates_autofilled_days_zero_uses_default(self):
        with patch(
            'core.services.ops_autopilot.intelligence.ValueRealizationEngine.get_outcome_rates',
            return_value={},
        ) as mocked:
            _dispatch_autopilot({'action': 'value_outcome_rates', 'days': 0})
            mocked.assert_called_once_with(days=30)


# ────────────────────────────────────────────────────────────────────
# Source-level sweep guard — catches accidental reverts + unswept sites
# ────────────────────────────────────────────────────────────────────


class FalsyOrDefaultPatternSourceTests(SimpleTestCase):
    """Scan the handler files for the bad pattern PR-B was supposed to
    eliminate. Catches accidental reverts in a future refactor without
    needing a full integration test for each of the ~33 sites.

    Allowed exceptions documented inline."""

    EDITED_FILES = (
        'core/services/td_handlers_ops.py',
        'core/services/td_handlers_core.py',
        'core/services/td_handlers_content.py',
        'core/services/td_handlers_agents.py',
        'core/services/td_handlers_codejobs.py',
    )

    # Params Rigby's Session 1228 triage explicitly deferred (pure
    # pagination — autofilled 0 produces "empty page", which is
    # observable rather than silent-wrong).
    DEFERRED_PARAMS = frozenset({
        'limit',           # pagination
        'offset',          # pagination
        'k',               # RAG fetch-k (already uses `or default`)
        'after_sequence',  # 0 is a legitimate "start at beginning"
        'start_line',      # 0 is a legitimate "start of file"
        'content_offset',  # default 0 — autofilled 0 is identical
        'content_limit',   # default 0 (no cap) — autofilled 0 is identical
        'max_items',       # gateway-only, has its own pagination semantics
        'after_seconds',   # has its own default constant indirection
        'priority_rank',   # patched via different surface
        'duration_minutes',  # patched via different surface
    })

    def test_no_unswept_int_payload_get_with_default(self):
        """Every ``int(payload.get('X', N))`` site should now read
        ``int(payload.get('X') or N)``. Exceptions are listed in
        DEFERRED_PARAMS.

        The regex requires the closing `))` immediately following the
        default literal — `int(payload.get('x', N) or M)` is the
        already-defensive shape (Session 1227 PR2 / Session 1228 PR-B
        canonical) and is NOT flagged."""
        import re
        # Match int(payload.get('X', N)) — i.e., the bad shape where
        # ints autofilled to 0 win over the default. Won't match
        # int(payload.get('X', N) or M) because that has `) or M)` between
        # the default literal and the int() close.
        BAD = re.compile(r"int\(payload\.get\('(?P<p>[a-z_]+)',\s*[^)]+\)\)")
        unswept = []
        for path in self.EDITED_FILES:
            with open(path, 'r') as f:
                src = f.read()
            for m in BAD.finditer(src):
                pname = m.group('p')
                if pname in self.DEFERRED_PARAMS:
                    continue
                start = src.rfind('\n', 0, m.start()) + 1
                end = src.find('\n', m.end())
                lineno = src.count(chr(10), 0, m.start()) + 1
                unswept.append(f"  {path}:{lineno}  {src[start:end].strip()}")
        if unswept:
            self.fail(
                'PR-B sweep missed sites (param not in DEFERRED_PARAMS):\n'
                + '\n'.join(unswept)
            )

    def test_pr_b_marker_present_in_each_edited_file(self):
        """Sanity: each edited file should contain the PR-B comment marker."""
        for path in self.EDITED_FILES:
            with open(path, 'r') as f:
                src = f.read()
            self.assertIn(
                'Session 1228 PR-B autofill safety',
                src,
                f'{path} missing the PR-B comment marker — edit may not have landed',
            )


# ────────────────────────────────────────────────────────────────────
# Direct micro-tests of the core fix expression
# ────────────────────────────────────────────────────────────────────


class FalsyOrDefaultExpressionTests(SimpleTestCase):
    """The core int(payload.get('x') or N) expression in isolation."""

    def test_autofilled_zero_returns_default(self):
        payload = {'x': 0}
        self.assertEqual(int(payload.get('x') or 7), 7)

    def test_missing_key_returns_default(self):
        payload = {}
        self.assertEqual(int(payload.get('x') or 7), 7)

    def test_none_value_returns_default(self):
        payload = {'x': None}
        self.assertEqual(int(payload.get('x') or 7), 7)

    def test_explicit_nonzero_int_passes_through(self):
        payload = {'x': 30}
        self.assertEqual(int(payload.get('x') or 7), 30)

    def test_explicit_string_int_coerces(self):
        payload = {'x': '30'}
        self.assertEqual(int(payload.get('x') or 7), 30)

    def test_empty_string_returns_default(self):
        payload = {'x': ''}
        self.assertEqual(int(payload.get('x') or 7), 7)
