"""S2902 T1a Phase 1 — Fold A regression: harness in-class filter.

T1c §11 Fold A: the harness must exclude ``run_agent`` (the meta-tool that
rewrites ``tool_name`` at ``unified_pa_entrypoint.py:2236``) AND the 44
schema-less ``agent_via_run_agent`` handlers. Without this filter, the
``run_agent`` rewrite boundary would leak into the validation queue and the
harness would try to double-count agent tools by their rewritten names.

This test pins the behavior at HEAD `7891ee9c` gap-map baseline (per T1c
§7.0 Fold C mitigation) — the exact counts flex as new tools land, but the
filter invariants (no run_agent, no schema-less handlers, no schema-less
orphans) hold regardless of count drift.
"""
from __future__ import annotations

from django.test import SimpleTestCase

from core.management.commands.pa_tool_validate_harness import Command
from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
from core.services.tool_dispatcher import ToolDispatcher


class InClassFilterTests(SimpleTestCase):
    """Fold A boundary: what does + does NOT enter the harness surface."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.schema_by_name = {
            s.get('name', ''): s
            for s in PA_TOOL_SCHEMAS
            if s.get('name')
        }
        dispatcher = ToolDispatcher()
        cls.handler_names = set(dispatcher._tool_handlers.keys())  # noqa: SLF001
        cls.in_class = Command._compute_in_class(
            schema_by_name=cls.schema_by_name,
            handler_names=cls.handler_names,
        )

    def test_run_agent_never_in_class(self) -> None:
        """``run_agent`` is the meta-tool — it MUST NOT enter the queue."""
        self.assertNotIn('run_agent', self.in_class)

    def test_no_schema_less_handlers_in_class(self) -> None:
        """The 44 agent_via_run_agent handlers have no schema; they're
        reachable only via ``run_agent(agent_name=…)`` — the harness must
        skip them so we don't double-count via the rewrite boundary.
        """
        schema_less_handlers = self.handler_names - set(self.schema_by_name.keys())
        # Every schema-less handler MUST be absent from in-class.
        for name in schema_less_handlers:
            self.assertNotIn(
                name, self.in_class,
                msg=(
                    f'schema-less handler {name!r} leaked into in-class set — '
                    f'Fold A filter is broken; run_agent rewrite would double-count'
                ),
            )

    def test_no_orphan_schemas_in_class(self) -> None:
        """Schemas without handlers can't dispatch — must be excluded."""
        orphan_schemas = set(self.schema_by_name.keys()) - self.handler_names
        for name in orphan_schemas:
            self.assertNotIn(name, self.in_class)

    def test_in_class_intersection_shape(self) -> None:
        """In-class = (schema ∩ handler) − {run_agent} — no other subtractions."""
        expected = (
            set(self.schema_by_name.keys()) & self.handler_names
        ) - {'run_agent'}
        self.assertEqual(self.in_class, expected)

    def test_in_class_count_within_baseline_band(self) -> None:
        """At S2902 T1a open, T1c §9 declared 96 in-class tools (94 untested
        + 2 promoted at gap-map HEAD ``7891ee9c``). Count drift is expected
        as tools land/retire; this test guards the ORDER of magnitude, not
        the exact number.
        """
        # Loose band: 80–130. Trips only if the filter breaks or a mass
        # tool addition/removal lands without updating the substrate arc.
        self.assertGreaterEqual(len(self.in_class), 80)
        self.assertLessEqual(len(self.in_class), 130)


class ExclusionReasonTests(SimpleTestCase):
    """Human-readable reasons when someone asks about an excluded tool."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.schema_by_name = {
            s.get('name', ''): s
            for s in PA_TOOL_SCHEMAS
            if s.get('name')
        }
        cls.handler_names = set(ToolDispatcher()._tool_handlers.keys())  # noqa: SLF001

    def test_run_agent_exclusion_reason_names_meta_tool(self) -> None:
        reason = Command._exclusion_reason(
            'run_agent',
            schema_by_name=self.schema_by_name,
            handler_names=self.handler_names,
        )
        self.assertIn('meta-tool', reason)
        self.assertIn('Fold A', reason)

    def test_schema_less_handler_exclusion_reason(self) -> None:
        """Pick any known schema-less handler and check the reason string."""
        schema_less = self.handler_names - set(self.schema_by_name.keys())
        if not schema_less:
            self.skipTest('no schema-less handlers registered')
        sample = next(iter(schema_less))
        reason = Command._exclusion_reason(
            sample,
            schema_by_name=self.schema_by_name,
            handler_names=self.handler_names,
        )
        self.assertIn('handler-only', reason)
        self.assertIn('run_agent', reason)

    def test_unknown_tool_exclusion_reason(self) -> None:
        reason = Command._exclusion_reason(
            'nonexistent_tool_xyz',
            schema_by_name=self.schema_by_name,
            handler_names=self.handler_names,
        )
        self.assertIn('unknown', reason)
