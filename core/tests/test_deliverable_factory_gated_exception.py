"""Session 1169 — Layer C Phase 1 factory contract tests.

Closes Session 1168 carryover item 1 (Phase 1).

Verifies that:
1. ``create_deliverable`` default contract still returns ``None`` on
   gate reject (preserves the 27 existing production caller sites
   unchanged — they get migrated in Phase 2 batches).
2. ``raise_on_gated=True`` opts the caller in to typed rejection.
3. The raised ``DeliverableGatedError`` carries ``reason``,
   ``reason_code``, ``title``, and ``agent_name`` attributes.
4. Each gate (smoke pattern, min length, media stub) produces the
   correct ``reason_code`` so PA dispatcher / future surfaces can
   build structured error responses.

Run::

    python manage.py test core.tests.test_deliverable_factory_gated_exception -v2
"""
from __future__ import annotations

from django.test import TestCase

from core.services.deliverable_factory import (
    DeliverableGatedError,
    _should_create_deliverable,
    create_deliverable,
)


class GateReasonCodeTests(TestCase):
    """The gate helper now returns a 3-tuple. Lock the reason_codes."""

    def test_pass_returns_passed_reason_code(self):
        should, reason, code = _should_create_deliverable(
            title='Real title',
            content='x' * 400,
            agent_name='SomeAgent',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertTrue(should)
        self.assertEqual(code, 'passed')

    def test_gate_1_media_stub(self):
        should, reason, code = _should_create_deliverable(
            title='Generated image',
            content='Generated 1 image(s)',
            agent_name='ImageAgent',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_1_media_stub')

    def test_gate_2_smoke_pattern(self):
        should, reason, code = _should_create_deliverable(
            title='Smoke test deliverable',
            content='x' * 400,
            agent_name='SomeAgent',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_2_smoke_pattern')

    def test_gate_3_min_length(self):
        # No allowlisted trigger_source + short content
        should, reason, code = _should_create_deliverable(
            title='Real title',
            content='too short',
            agent_name='SomeAgent',
            metadata=None,
        )
        self.assertFalse(should)
        self.assertEqual(code, 'gate_3_min_length')


class DefaultContractTests(TestCase):
    """create_deliverable(...) default — returns None on gate reject."""

    def test_default_returns_none_on_smoke_pattern(self):
        """Legacy contract preserved for the 27 production callers
        that haven't migrated to raise_on_gated=True yet (Phase 2)."""
        result = create_deliverable(
            title='Smoke test default contract',
            content='x' * 400,
            agent_name='SomeAgent',
            metadata={'trigger_source': 'pa_tool'},
        )
        self.assertIsNone(result)

    def test_default_returns_none_on_short_content(self):
        result = create_deliverable(
            title='Real title default contract',
            content='too short',
            agent_name='SomeAgent',
        )
        self.assertIsNone(result)


class RaiseOnGatedTests(TestCase):
    """create_deliverable(raise_on_gated=True) — typed exception path."""

    def test_smoke_pattern_raises_with_gate_2_code(self):
        with self.assertRaises(DeliverableGatedError) as cm:
            create_deliverable(
                title='Smoke test raising contract',
                content='x' * 400,
                agent_name='SomeAgent',
                metadata={'trigger_source': 'pa_tool'},
                raise_on_gated=True,
            )
        e = cm.exception
        self.assertEqual(e.reason_code, 'gate_2_smoke_pattern')
        self.assertIn('smoke test pattern', e.reason)
        self.assertEqual(e.agent_name, 'SomeAgent')

    def test_short_content_raises_with_gate_3_code(self):
        with self.assertRaises(DeliverableGatedError) as cm:
            create_deliverable(
                title='Real title raising contract',
                content='too short',
                agent_name='SomeAgent',
                raise_on_gated=True,
            )
        e = cm.exception
        self.assertEqual(e.reason_code, 'gate_3_min_length')
        self.assertIn('below minimum', e.reason)

    def test_media_stub_raises_with_gate_1_code(self):
        with self.assertRaises(DeliverableGatedError) as cm:
            create_deliverable(
                title='Generated image',
                content='Generated 1 image(s)',
                agent_name='ImageAgent',
                metadata={'trigger_source': 'pa_tool'},
                raise_on_gated=True,
            )
        e = cm.exception
        self.assertEqual(e.reason_code, 'gate_1_media_stub')
        self.assertEqual(e.agent_name, 'ImageAgent')

    def test_passing_input_does_not_raise(self):
        """Sanity: raise_on_gated=True doesn't break the happy path.
        Substantial content + non-smoke title + valid trigger_source
        should still produce a real Deliverable."""
        result = create_deliverable(
            title='Substantial real deliverable',
            content='Real substantial content. ' * 30,
            agent_name='SomeAgent',
            metadata={'trigger_source': 'pa_tool'},
            raise_on_gated=True,
        )
        self.assertIsNotNone(result)
        # Real Deliverable instance — has .id and .title
        self.assertIsNotNone(result.id)
        self.assertIn('Substantial', result.title)


class ExceptionAttributeTests(TestCase):
    """DeliverableGatedError attribute contract."""

    def test_str_contains_all_fields(self):
        e = DeliverableGatedError(
            reason='because',
            reason_code='gate_2_smoke_pattern',
            title='Some title',
            agent_name='SomeAgent',
        )
        s = str(e)
        self.assertIn('because', s)
        self.assertIn('gate_2_smoke_pattern', s)
        self.assertIn('Some title', s)
        self.assertIn('SomeAgent', s)

    def test_defaults_when_minimal_construction(self):
        """Caller can build with just reason — useful for callers that
        want to wrap their own errors as typed-gated."""
        e = DeliverableGatedError(reason='probed')
        self.assertEqual(e.reason, 'probed')
        self.assertEqual(e.reason_code, 'unknown_gate')
        self.assertEqual(e.title, '')
        self.assertEqual(e.agent_name, '')

    def test_title_truncated_at_120_chars(self):
        long_title = 'A' * 500
        e = DeliverableGatedError(reason='probed', title=long_title)
        self.assertEqual(len(e.title), 120)
