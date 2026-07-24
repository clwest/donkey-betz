"""S2938 Ledger #5 — schema-vs-handler consistency lint contract tests.

Locks the shape of ``core.services.pa_tools_gap_map.lint_schema_vs_handler``
— the parse-based drift detector shipped as substrate promotion of the
Ledger #5 systemic detection pattern (3-cycle threshold at S2935/S2936/
S2937).

Ratified: S2938 T0 Rigby joint SIGN AGREE (Q1/Q2/Q3/ZO all AGREE with
Q3 refinement: broaden negative-claim patterns to include "does not
dispatch" / "doesn't dispatch" / "side-effect free" and broaden dispatch
evidence to catch curated service-layer functions like
``rigby_mission_delegation.delegate_work_item``). Chris D-verdict at
S2938 T1.

Contracts locked (11 across 3 classes):

  Action-count drift:
    1. Docstring "four actions" + 5-enum → flags.
    2. Docstring "5 action" (digit + singular) + 3-enum → flags.
    3. Docstring omits action-count claim → silent (opt-in evidence).
    4. Docstring correct + enum matches → silent.
    5. Schema with no ``action`` enum → silent.

  Negative-claim drift:
    6. "No agent dispatch" + handler has ``.apply_async(`` → flags.
    7. "No agent dispatch" + handler has ``rigby_mission_delegation``
       import (Q3 curated service-layer detection) → flags.
    8. "read-only" + handler has ``.save(`` → flags.
    9. "always live" + handler has ``getattr(settings,`` → flags.
   10. Negative claim + no contradicting evidence → silent.

  Integration:
   11. ``build_gap_map`` merges ``lint_schema`` + ``lint_schema_vs_handler``
       output into ``row['lints']``.
"""
from __future__ import annotations

from typing import Any

from django.test import SimpleTestCase

from core.services.pa_tools_gap_map import (
    build_gap_map,
    lint_schema_vs_handler,
)


def _schema(actions: list[str] | None = None, description: str = 'x' * 60) -> dict[str, Any]:
    """Minimal well-formed schema for lint tests.

    Long ``description`` avoids tripping the pre-existing
    ``short_description`` lint from ``lint_schema``.
    """
    parameters: dict[str, Any] = {'properties': {}, 'required': ['action']}
    if actions is not None:
        parameters['properties']['action'] = {'enum': list(actions)}
    return {'description': description, 'parameters': parameters}


class ActionCountDriftTests(SimpleTestCase):
    """Contracts 1-5 — docstring vs enum action-count consistency."""

    def test_number_word_disagrees_with_enum(self):
        """Contract 1: "four actions" + 5-enum → flags."""
        schema = _schema(['a', 'b', 'c', 'd', 'e'])
        docstring = 'Surface: my_tool with four actions:\n- a\n- b\n- c\n- d\n- e\n'
        lints = lint_schema_vs_handler(schema, 'pass\n', docstring)
        self.assertIn('handler_drift_action_count', lints)

    def test_digit_singular_disagrees_with_enum(self):
        """Contract 2: "5 action" (digit + singular) + 3-enum → flags."""
        schema = _schema(['x', 'y', 'z'])
        docstring = 'Exposes 5 action for callers.\n'
        lints = lint_schema_vs_handler(schema, 'pass\n', docstring)
        self.assertIn('handler_drift_action_count', lints)

    def test_no_count_claim_is_silent(self):
        """Contract 3: docstring omits count → silent (opt-in evidence)."""
        schema = _schema(['a', 'b', 'c'])
        docstring = 'Read-only surface that returns a summary.\n'
        lints = lint_schema_vs_handler(schema, 'pass\n', docstring)
        self.assertNotIn('handler_drift_action_count', lints)

    def test_correct_count_is_silent(self):
        """Contract 4: docstring correct + enum matches → silent."""
        schema = _schema(['a', 'b', 'c'])
        docstring = 'Surface: my_tool with three actions.\n'
        lints = lint_schema_vs_handler(schema, 'pass\n', docstring)
        self.assertNotIn('handler_drift_action_count', lints)

    def test_no_action_enum_is_silent(self):
        """Contract 5: schema with no ``action`` enum → silent."""
        schema = _schema(actions=None)
        docstring = 'Surface: my_tool with four actions.\n'
        lints = lint_schema_vs_handler(schema, 'pass\n', docstring)
        self.assertNotIn('handler_drift_action_count', lints)


class NegativeClaimDriftTests(SimpleTestCase):
    """Contracts 6-10 — docstring negative claim vs source evidence."""

    def test_no_agent_dispatch_vs_apply_async(self):
        """Contract 6: "No agent dispatch" + ``.apply_async(`` → flags."""
        schema = _schema(['a'])
        docstring = 'Guardrails:\n- No agent dispatch.\n'
        source = 'from foo import bar\nbar.apply_async(args=[1])\n'
        lints = lint_schema_vs_handler(schema, source, docstring)
        self.assertIn('handler_drift_negative_claim_dispatch', lints)

    def test_no_agent_dispatch_vs_service_layer_delegate(self):
        """Contract 7: Q3 curated service-layer detection — the Ledger
        #39 case shape (docstring claims no dispatch, handler calls
        ``rigby_mission_delegation`` service which async-dispatches
        internally)."""
        schema = _schema(['a', 'b'])
        docstring = 'Guardrails:\n- No agent dispatch.\n'
        source = (
            'from core.services.rigby_mission_delegation import delegate_work_item\n'
            'result = delegate_work_item(item)\n'
        )
        lints = lint_schema_vs_handler(schema, source, docstring)
        self.assertIn('handler_drift_negative_claim_dispatch', lints)

    def test_read_only_vs_save_call(self):
        """Contract 8: "read-only" + handler has ``.save(`` → flags."""
        schema = _schema(['a'])
        docstring = 'Pure read-only surface for observers.\n'
        source = 'item.save(update_fields=["status"])\n'
        lints = lint_schema_vs_handler(schema, source, docstring)
        self.assertIn('handler_drift_negative_claim_mutation', lints)

    def test_always_live_vs_settings_read(self):
        """Contract 9: "always live" + settings read → flags."""
        schema = _schema(['a'])
        docstring = 'Always live — no gating.\n'
        source = 'from django.conf import settings\nif settings.FOO:\n    pass\n'
        lints = lint_schema_vs_handler(schema, source, docstring)
        self.assertIn('handler_drift_negative_claim_feature_flag', lints)

    def test_negative_claim_without_evidence_is_silent(self):
        """Contract 10: docstring negative claim + no contradicting
        source evidence → silent (the honest case)."""
        schema = _schema(['a'])
        docstring = (
            'Guardrails:\n- No agent dispatch.\n- No state mutation.\n'
            '- No feature flag.\n'
        )
        source = 'return {"ok": True, "sections": []}\n'
        lints = lint_schema_vs_handler(schema, source, docstring)
        self.assertNotIn('handler_drift_negative_claim_dispatch', lints)
        self.assertNotIn('handler_drift_negative_claim_mutation', lints)
        self.assertNotIn('handler_drift_negative_claim_feature_flag', lints)


class BuildGapMapIntegrationTests(SimpleTestCase):
    """Contract 11 — build_gap_map merges schema-vs-handler lints in."""

    def test_row_lints_include_schema_vs_handler_output(self):
        rows: list[dict[str, Any]] = [{
            'name': 'my_tool',
            'has_schema': True,
            'has_handler': True,
            'actions': ['a', 'b', 'c', 'd', 'e'],
            'handler_file': 'core/services/td_handlers_x.py',
            'handler_source': 'return {"ok": True}\n',
            'handler_docstring': 'Surface: my_tool with four actions.\n',
        }]
        schema = _schema(['a', 'b', 'c', 'd', 'e'])
        schemas_by_name = {'my_tool': schema}
        docs_index: dict[str, Any] = {
            'per_tool_stems': {},
            'covered_actions_by_stem': {},
            'template_version_by_stem': {},
            'template_variant_by_stem': {},
            'frontmatter_fields_by_stem': {},
            'heading_titles_by_stem': {},
            'substrate_stems': set(),
            'total_docs': 0,
        }
        build_gap_map(rows, docs_index, schemas_by_name, run_agent_targets=set())
        self.assertIn('handler_drift_action_count', rows[0]['lints'])
