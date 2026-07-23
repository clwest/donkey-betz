"""S2903 T1a Phase 2 — regression tests for the metadata seed.

Phase 1 shipped the harness scaffold with 2 records against ``ops_tool``
verified live at S2796. Phase 2 (S2903) extends the seed to:

- ``TOOL_DEFAULTS``: ops_tool + kb_tool + agent_introspection_tool +
  repo_tool (all READ_ONLY per each tool's validation report).
- ``TOOL_ACTION_METADATA``: ops_tool.focus_mode_update WRITE_GATED
  override + 7 session_tool per-action records (3 READ_ONLY read side
  + 4 MUTATION write side).

Test surface:

- Every seeded ``(tool, action)`` pair resolves to the declared safety
  class through ``resolve_safety`` (records-win-over-defaults semantics).
- The Phase 2 fan-out actually produces ~39 dispatchable READ_ONLY
  actions when combined with the schema surface (band, not exact — the
  schema can add/remove actions between sessions).
- Overrides beat defaults (ops_tool.focus_mode_update is WRITE_GATED
  despite the ops_tool TOOL_DEFAULTS being READ_ONLY).
- Mixed-safety fan-out: session_tool has NO tool default (would be a
  contract violation) and produces the expected 3 READ_ONLY /
  4 MUTATION split.

Guard band chosen loose enough to tolerate schema drift; trips only on
metadata regression.
"""
from __future__ import annotations

from django.test import SimpleTestCase

from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
from core.services.tool_action_metadata import (
    TOOL_ACTION_METADATA,
    TOOL_DEFAULTS,
    coverage_stats,
    get_defaults,
    get_metadata,
    resolve_safety,
)


def _schema_actions(name: str) -> list[str]:
    schema = next(
        (s for s in PA_TOOL_SCHEMAS if s.get('name') == name), {}
    )
    props = (schema.get('parameters') or {}).get('properties') or {}
    return list((props.get('action') or {}).get('enum') or [])


class ToolDefaultsSeedTests(SimpleTestCase):
    """Every seeded tool default resolves READ_ONLY for arbitrary actions."""

    PHASE_2_DEFAULT_TOOLS = (
        'ops_tool',
        'kb_tool',
        'agent_introspection_tool',
        'repo_tool',
    )

    def test_phase_2_tool_defaults_registered(self) -> None:
        """All four Phase 2 tool defaults are in ``TOOL_DEFAULTS`` and are
        READ_ONLY. Trips if someone removes the seed or downgrades the
        safety class without a substrate-arc-scoped SIGN.
        """
        for name in self.PHASE_2_DEFAULT_TOOLS:
            with self.subTest(tool=name):
                defaults = get_defaults(name)
                assert defaults is not None, (
                    f'TOOL_DEFAULTS missing entry for {name!r}'
                )
                self.assertEqual(defaults.default_safety_class, 'READ_ONLY')

    def test_tool_default_resolves_for_unclassified_action(self) -> None:
        """An action not in ``TOOL_ACTION_METADATA`` falls back to the
        tool default with ``resolution_source='tool_default'``.
        """
        # Pick a real schema action for a defaulted tool that is NOT
        # per-action overridden. repo_tool has no per-action records.
        actions = _schema_actions('repo_tool')
        self.assertGreater(len(actions), 0, msg='repo_tool schema empty')
        for action in actions:
            with self.subTest(action=action):
                safety, source = resolve_safety('repo_tool', action)
                self.assertEqual(safety, 'READ_ONLY')
                self.assertEqual(source, 'tool_default')


class OpsToolPerActionOverrideTests(SimpleTestCase):
    """ops_tool.focus_mode_update must override the tool default."""

    def test_focus_mode_update_is_write_gated(self) -> None:
        rec = get_metadata('ops_tool', 'focus_mode_update')
        assert rec is not None, 'ops_tool.focus_mode_update override missing'
        self.assertEqual(rec.safety_class, 'WRITE_GATED')

    def test_focus_mode_update_beats_tool_default(self) -> None:
        """Per-action record wins even when TOOL_DEFAULTS[ops_tool] would
        otherwise resolve READ_ONLY.
        """
        safety, source = resolve_safety('ops_tool', 'focus_mode_update')
        self.assertEqual(safety, 'WRITE_GATED')
        self.assertEqual(source, 'action')

    def test_ops_tool_verified_actions_still_resolve_read_only(self) -> None:
        """S2796-verified actions (version + recent_recycles) remain
        READ_ONLY. Not gated by the tool default addition — records win.
        """
        for action in ('version', 'recent_recycles'):
            with self.subTest(action=action):
                safety, source = resolve_safety('ops_tool', action)
                self.assertEqual(safety, 'READ_ONLY')
                self.assertEqual(source, 'action')


class SessionToolFanOutTests(SimpleTestCase):
    """session_tool has NO tool default — mixed safety classes per action."""

    READ_ONLY_ACTIONS = ('health_check', 'list_recent', 'whoami')
    MUTATION_ACTIONS = ('create_fresh', 'retire', 'set_active', 'seed')

    def test_session_tool_has_no_tool_default(self) -> None:
        """session_tool must NOT be in TOOL_DEFAULTS — mixed safety.
        If someone adds a default here it'd silently classify all 7
        actions as one class, hiding the mutation set.
        """
        self.assertIsNone(get_defaults('session_tool'))

    def test_read_side_resolves_read_only(self) -> None:
        for action in self.READ_ONLY_ACTIONS:
            with self.subTest(action=action):
                safety, source = resolve_safety('session_tool', action)
                self.assertEqual(safety, 'READ_ONLY')
                self.assertEqual(source, 'action')

    def test_write_side_resolves_mutation(self) -> None:
        for action in self.MUTATION_ACTIONS:
            with self.subTest(action=action):
                safety, source = resolve_safety('session_tool', action)
                self.assertEqual(safety, 'MUTATION')
                self.assertEqual(source, 'action')


class CoverageStatsTests(SimpleTestCase):
    """Coverage-stats helper reflects the Phase 2 seed shape."""

    def test_coverage_stats_shape(self) -> None:
        stats = coverage_stats()
        self.assertIn('per_action_records', stats)
        self.assertIn('tool_defaults', stats)
        self.assertIn('tools_with_at_least_one_record', stats)

    def test_phase_2_seed_has_meaningful_coverage(self) -> None:
        """Phase 2 seed authored ≥4 tool defaults and ≥10 per-action
        records. Trips if the seed regresses.
        """
        stats = coverage_stats()
        self.assertGreaterEqual(stats['tool_defaults'], 4)
        self.assertGreaterEqual(stats['per_action_records'], 10)


class MutationVerbDefaultLeakTests(SimpleTestCase):
    """Rigby Q3 mitigation (S2903 SIGN): guard against a mutation-verb
    action landing on a tool with a READ_ONLY default and getting silently
    classified as READ_ONLY.

    Failure mode: someone adds an action like ``ops_tool.delete_recycles``
    to the schema. It's not in ``TOOL_ACTION_METADATA``, so ``resolve_safety``
    falls through to ``TOOL_DEFAULTS['ops_tool']`` and returns READ_ONLY.
    The harness then dispatches it as a read — but it's actually a write.

    Guard: for every TOOL_DEFAULTS[tool] whose default is READ_ONLY,
    scan the tool's schema actions. If any action name starts with a
    mutation-verb prefix, it MUST have an explicit override in
    ``TOOL_ACTION_METADATA``.

    Heuristic — not a full auth check. Catches the obvious naming-signal
    regressions; deeper (per-handler AST inspection) is out of scope at MVP.
    """

    # Prefix set derived from observed mutation-action naming in the
    # existing schema surface (session_tool, deliverable_tool, autopilot,
    # workspace_tool, workspace_budget_tool, ops_tool). Not a rigorous set —
    # a signal-catcher for the obvious cases.
    MUTATION_VERB_PREFIXES = (
        'create_', 'delete_', 'update_', 'set_', 'seed', 'retire',
        'save_', 'unsave', 'add_', 'remove_', 'write_', 'append',
        'archive_', 'kill_', 'freeze_', 'unfreeze_', 'approve_',
        'reject_', 'apply_', 'reset_', 'clear_', 'link_', 'unlink_',
        'normalize', 'bulk_',
    )

    def _looks_like_mutation(self, action: str) -> bool:
        for prefix in self.MUTATION_VERB_PREFIXES:
            if action == prefix.rstrip('_') or action.startswith(prefix):
                return True
        return False

    def test_no_mutation_verb_action_defaulted_to_read_only(self) -> None:
        offenders: list[tuple[str, str]] = []
        for tool_name, defaults in TOOL_DEFAULTS.items():
            if defaults.default_safety_class != 'READ_ONLY':
                continue
            for action in _schema_actions(tool_name):
                if not self._looks_like_mutation(action):
                    continue
                if (tool_name, action) in TOOL_ACTION_METADATA:
                    continue  # explicit override present — good
                offenders.append((tool_name, action))
        self.assertEqual(
            offenders, [],
            msg=(
                f'Mutation-verb-named actions defaulting to READ_ONLY '
                f'without an explicit override: {offenders}. '
                f'Add a TOOL_ACTION_METADATA entry with the actual safety '
                f'class OR remove the READ_ONLY tool default.'
            ),
        )


class Phase2DispatchSurfaceTests(SimpleTestCase):
    """The Phase 2 seed should surface ~30+ READ_ONLY dispatchable actions
    when the schema surface is factored in. Band matches 00-START Phase 2
    target of ~30-60 READ_ONLY actions dispatched cleanly.
    """

    def test_phase_2_seed_yields_target_read_only_count(self) -> None:
        read_only = 0
        for schema in PA_TOOL_SCHEMAS:
            name = schema.get('name')
            if not name:
                continue
            for action in _schema_actions(name):
                safety, _source = resolve_safety(name, action)
                if safety == 'READ_ONLY':
                    read_only += 1
        # Loose band: ≥30 covers the Phase 2 target floor. Upper bound not
        # tested — future authoring only adds coverage; regression is a
        # downward drift.
        self.assertGreaterEqual(
            read_only, 30,
            msg=(
                f'Phase 2 seed yields only {read_only} READ_ONLY actions; '
                f'expected ≥30 per 00-START Phase 2 target. '
                f'Did TOOL_DEFAULTS or TOOL_ACTION_METADATA regress?'
            ),
        )
