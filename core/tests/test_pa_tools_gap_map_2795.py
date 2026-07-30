"""S2795 — PA tools gap-map contract tests.

Locks the shape of:

  * ``core.services.pa_tools_gap_map`` — pure logic module.
  * ``python manage.py build_pa_tool_audit`` flag behavior (BC on default;
    additive under ``--include-validation-xref`` / ``--emit-gap-json`` /
    ``--gap-only``).

Contracts locked (14 across 3 classes):

  Gap-map logic:
    1. ``index_validation_docs`` returns zero shape when dir missing.
    2. Substrate stems classified separately from per-tool stems.
    3. "Covered actions" heading parsed correctly when present.
    4. "Covered actions" absence → ``None`` sentinel (unknown coverage).
    5. Full match on schema-action set → ``validated_full``.
    6. Partial match → ``validated_partial``.
    7. No matching doc → ``untested``.
    8. Meta-tools (``run_agent``) → ``meta_no_handler`` regardless of state.
    9. Handler-only agents reachable via run_agent → ``agent_via_run_agent``.

  Schema-quality lint:
   10. Missing description flagged.
   11. Short description flagged.
   12. Action enum absent from description flagged.

  Triage slices:
   13. Slices grouped by handler file with untested_count + est_sessions.

  Command:
   14. Default invocation (no flags) preserves BC — no Category column.

Ratified: S2795 T1 Rigby joint SIGN — SIGN-with-edits; 5 folds
(F1 actionable, F2 mitigatable, F3 actionable, F4 future_trigger,
F5 mitigatable) persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8
(ledger rows 60/61/62/63/64). Chris D-verdict: "Yes".
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from core.services.pa_tools_gap_map import (
    CATEGORY_LABEL,
    COVERED_ACTIONS_HEADING_RE,
    SUBSTRATE_DOC_STEMS,
    build_gap_map,
    build_triage_slices,
    classify_tool,
    evaluate_template_compliance,
    find_matching_doc_stem,
    index_validation_docs,
    lint_schema,
    render_gap_map_markdown,
)


class GapMapLogicTests(SimpleTestCase):
    """Contracts 1-9 — pure gap-map categorization logic."""

    def _make_index(self, tmpdir: Path, docs: dict[str, str | None]) -> dict:
        """Write validation docs then index them.

        ``docs`` is ``{stem: body_or_None}``. ``None`` writes no body,
        used for substrate docs which we don't inspect.
        """
        vdir = tmpdir / 'validation'
        vdir.mkdir(parents=True, exist_ok=True)
        for stem, body in docs.items():
            (vdir / f'{stem}_validation.md').write_text(body or 'stub\n')
        return index_validation_docs(vdir)

    def test_missing_dir_returns_zero_shape(self):
        """Contract 1: no validation docs dir → empty index, no crash."""
        idx = index_validation_docs(Path('/nonexistent/path'))
        self.assertEqual(idx['total_docs'], 0)
        self.assertEqual(idx['substrate_stems'], set())
        self.assertEqual(idx['per_tool_stems'], {})

    def test_substrate_stems_partitioned_from_per_tool(self):
        """Contract 2: substrate docs classified separately.

        Uses ``retry_behavior`` (canonical substrate name from the
        S2728→S2732 campaign) + a hypothetical per-tool ``foo_tool``.
        """
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {
                'retry_behavior': None,
                'foo_tool': '# foo\n',
            })
        self.assertIn('retry_behavior', idx['substrate_stems'])
        self.assertNotIn('retry_behavior', idx['per_tool_stems'])
        self.assertIn('foo_tool', idx['per_tool_stems'])

    def test_covered_actions_heading_parsed(self):
        """Contract 3: `## Covered actions` section extracts action names.

        Backticked identifiers under the heading (until the next `##`) form
        the covered-actions set.
        """
        body = (
            '# foo_tool validation\n\n'
            '## Some other section\n\n'
            'irrelevant `bogus_action`.\n\n'
            '## Covered actions\n\n'
            '- `list`\n- `create`\n- `update`\n\n'
            '## Findings\n\n'
            'later `not_an_action` mentioned here.\n'
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {'foo_tool': body})
        covered = idx['covered_actions_by_stem']['foo_tool']
        self.assertIsNotNone(covered)
        self.assertEqual(covered, {'list', 'create', 'update'})

    def test_covered_actions_absent_returns_none(self):
        """Contract 4: no `## Covered actions` heading → None sentinel."""
        body = '# foo_tool validation\n\n## Findings\nsome text\n'
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {'foo_tool': body})
        self.assertIsNone(idx['covered_actions_by_stem']['foo_tool'])

    def test_classify_validated_full(self):
        """Contract 5: doc + all schema actions covered → validated_full."""
        body = '## Covered actions\n\n- `list`\n- `create`\n'
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {'foo_tool': body})
        category = classify_tool(
            tool_name='foo_tool',
            has_schema=True,
            has_handler=True,
            schema_actions=['list', 'create'],
            docs_index=idx,
        )
        self.assertEqual(category, 'validated_full')

    def test_classify_validated_partial(self):
        """Contract 6: doc + subset of schema actions → validated_partial."""
        body = '## Covered actions\n\n- `list`\n'
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {'foo_tool': body})
        category = classify_tool(
            tool_name='foo_tool',
            has_schema=True,
            has_handler=True,
            schema_actions=['list', 'create', 'update'],
            docs_index=idx,
        )
        self.assertEqual(category, 'validated_partial')

    def test_classify_validated_doc_exists_unknown(self):
        """Contract 4b: doc exists but no checklist → doc_exists_unknown.

        Companion to Contract 4 (which locks the None sentinel at index
        time); this locks the same signal is honored at classify time.
        """
        body = '# foo_tool validation\n\n## Findings\n'
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {'foo_tool': body})
        category = classify_tool(
            tool_name='foo_tool',
            has_schema=True,
            has_handler=True,
            schema_actions=['list'],
            docs_index=idx,
        )
        self.assertEqual(category, 'validated_doc_exists_unknown')

    def test_classify_untested_when_no_matching_doc(self):
        """Contract 7: schema+handler pair with no doc → untested."""
        with tempfile.TemporaryDirectory() as td:
            idx = self._make_index(Path(td), {})
        category = classify_tool(
            tool_name='bar_tool',
            has_schema=True,
            has_handler=True,
            schema_actions=['list'],
            docs_index=idx,
        )
        self.assertEqual(category, 'untested')

    def test_classify_meta_no_handler(self):
        """Contract 8: run_agent → meta_no_handler regardless."""
        idx = {'per_tool_stems': {}, 'covered_actions_by_stem': {}, 'substrate_stems': set(), 'total_docs': 0}
        category = classify_tool(
            tool_name='run_agent',
            has_schema=True,
            has_handler=False,
            schema_actions=[],
            docs_index=idx,
        )
        self.assertEqual(category, 'meta_no_handler')

    def test_classify_agent_via_run_agent(self):
        """Contract 9: handler-only tools reachable via run_agent."""
        idx = {'per_tool_stems': {}, 'covered_actions_by_stem': {}, 'substrate_stems': set(), 'total_docs': 0}
        category = classify_tool(
            tool_name='content_writer_agent',
            has_schema=False,
            has_handler=True,
            schema_actions=[],
            docs_index=idx,
            is_agent_via_run_agent=True,
        )
        self.assertEqual(category, 'agent_via_run_agent')

    # ── S3045 Batch 1 substrate — agent_via_run_agent_validated ─────
    #
    # Rigby T1 SIGN AGREE with 6 A2 sweep dimensions (i)-(vi). These
    # three tests cover the positive branch, the negative control
    # (non-agent handler-only tools cannot promote), and the precedence
    # invariant (meta_no_handler / orphan_schema still short-circuit).

    def test_classify_agent_via_run_agent_validated_when_doc_exists(self):
        """S3045: agent-via-run_agent tool with per-tool validation doc
        classifies as ``agent_via_run_agent_validated`` (positive)."""
        idx = {
            'per_tool_stems': {'thinking_agent': ['thinking_agent_validation.md']},
            'covered_actions_by_stem': {'thinking_agent': None},
            'substrate_stems': set(),
            'total_docs': 1,
        }
        category = classify_tool(
            tool_name='thinking_agent',
            has_schema=False,
            has_handler=True,
            schema_actions=[],
            docs_index=idx,
            is_agent_via_run_agent=True,
        )
        self.assertEqual(category, 'agent_via_run_agent_validated')

    def test_classify_handler_only_dead_not_promoted_by_doc_presence(self):
        """S3045 negative control: handler-only tool NOT reachable via
        run_agent stays ``handler_only_dead`` even if a doc stem matches.
        Prevents accidental promotion of unrelated handler-only tools."""
        idx = {
            'per_tool_stems': {'dead_tool': ['dead_tool_validation.md']},
            'covered_actions_by_stem': {'dead_tool': None},
            'substrate_stems': set(),
            'total_docs': 1,
        }
        category = classify_tool(
            tool_name='dead_tool',
            has_schema=False,
            has_handler=True,
            schema_actions=[],
            docs_index=idx,
            is_agent_via_run_agent=False,
        )
        self.assertEqual(category, 'handler_only_dead')

    def test_classify_agent_via_run_agent_precedence_stable(self):
        """S3045 precedence: meta_no_handler and orphan_schema still
        short-circuit before the new agent_via_run_agent_validated
        branch. Both cases have has_handler=False, so the new branch
        cannot fire regardless of doc presence."""
        idx = {
            'per_tool_stems': {'run_agent': ['run_agent_validation.md']},
            'covered_actions_by_stem': {'run_agent': None},
            'substrate_stems': set(),
            'total_docs': 1,
        }
        # meta_no_handler wins even with a matching doc.
        self.assertEqual(
            classify_tool(
                tool_name='run_agent',
                has_schema=True,
                has_handler=False,
                schema_actions=[],
                docs_index=idx,
                is_agent_via_run_agent=False,
            ),
            'meta_no_handler',
        )
        # orphan_schema (has_schema + not has_handler) wins even if
        # is_agent_via_run_agent were incorrectly True.
        self.assertEqual(
            classify_tool(
                tool_name='some_orphan',
                has_schema=True,
                has_handler=False,
                schema_actions=[],
                docs_index=idx,
                is_agent_via_run_agent=True,
            ),
            'orphan_schema',
        )


class SchemaLintTests(SimpleTestCase):
    """Contracts 10-12 — schema quality lint (F5 mitigation)."""

    def test_missing_description_flagged(self):
        """Contract 10: schema with no description → missing_description."""
        lints = lint_schema({
            'name': 'foo_tool',
            'parameters': {'properties': {'x': {}}, 'required': ['x']},
        })
        self.assertIn('missing_description', lints)

    def test_short_description_flagged(self):
        """Contract 11: description under threshold → short_description."""
        lints = lint_schema({
            'name': 'foo_tool',
            'description': 'tiny.',
            'parameters': {'properties': {'x': {}}, 'required': ['x']},
        })
        self.assertIn('short_description', lints)

    def test_actions_not_mentioned_in_description_flagged(self):
        """Contract 12: action enum absent from description text."""
        lints = lint_schema({
            'name': 'foo_tool',
            'description': 'a' * 200,  # long enough, but no action words
            'parameters': {
                'properties': {
                    'action': {'enum': ['reticulate', 'defenestrate', 'obfuscate', 'coalesce']},
                },
                'required': ['action'],
            },
        })
        self.assertIn('actions_not_mentioned_in_description', lints)

    def test_healthy_schema_no_lints(self):
        """Sanity: a well-shaped schema returns empty lint list."""
        lints = lint_schema({
            'name': 'foo_tool',
            'description': (
                'Well-formed description that clearly mentions the '
                'list, create, and update actions in prose.'
            ),
            'parameters': {
                'properties': {
                    'action': {'enum': ['list', 'create', 'update']},
                },
                'required': ['action'],
            },
        })
        self.assertEqual(lints, [])


class TriageSlicesTests(SimpleTestCase):
    """Contract 13 — F3 mitigation: triage slices grouped by handler file."""

    def test_triage_slices_group_untested_by_handler_file(self):
        rows = [
            {
                'name': f'tool_{i}',
                'category': 'untested',
                'handler_file': 'core/services/td_handlers_content.py',
            }
            for i in range(6)
        ] + [
            {
                'name': f'other_{i}',
                'category': 'validated_full',  # NOT untested, must be excluded
                'handler_file': 'core/services/td_handlers_content.py',
            }
            for i in range(5)
        ] + [
            {
                'name': f'ops_{i}',
                'category': 'untested',
                'handler_file': 'core/services/td_handlers_ops.py',
            }
            for i in range(4)
        ]
        slices = build_triage_slices(rows, max_slices=5, min_untested_per_slice=3)
        # Top slice: content (6 untested).
        self.assertEqual(slices[0]['theme'], 'td_handlers_content')
        self.assertEqual(slices[0]['untested_count'], 6)
        # est_sessions rounds up at 4 per session → 6/4 = 2.
        self.assertEqual(slices[0]['est_sessions'], 2)
        # Second slice: ops (4 untested).
        self.assertEqual(slices[1]['theme'], 'td_handlers_ops')
        self.assertEqual(slices[1]['untested_count'], 4)
        # Groups below min threshold excluded.
        theme_names = {s['theme'] for s in slices}
        self.assertNotIn('other', theme_names)


class CommandBackwardsCompatTests(SimpleTestCase):
    """Contract 14 — default invocation preserves prior output shape."""

    def test_default_render_has_no_category_column(self):
        """No flags → the overview table stays 5-column, not 7-column."""
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('build_pa_tool_audit', '--check', stdout=out)
        rendered = out.getvalue()
        # Default is the 5-column shape.
        self.assertIn('| Tool | Wiring | Actions | Required | Summary |', rendered)
        # And explicitly NOT the 7-column xref shape.
        self.assertNotIn(
            '| Tool | Wiring | Actions | Required | Category | Lint | Summary |',
            rendered,
        )

    def test_xref_render_adds_category_and_lint_columns(self):
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command(
            'build_pa_tool_audit', '--check', '--include-validation-xref',
            stdout=out,
        )
        rendered = out.getvalue()
        self.assertIn(
            '| Tool | Wiring | Actions | Required | Category | Lint | Summary |',
            rendered,
        )
        self.assertIn('## Validation coverage (S2795)', rendered)

    def test_gap_only_render_produces_standalone_artifact(self):
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('build_pa_tool_audit', '--check', '--gap-only', stdout=out)
        rendered = out.getvalue()
        # Standalone gap map has its own title.
        self.assertIn('# PA Tools — Validation Coverage Gap Map', rendered)
        # And the F3-mitigation triage slices section is present.
        self.assertIn(
            '## Triage slices (F3 decision aid — pick, do not queue)',
            rendered,
        )
        # F1 category label used.
        self.assertIn(
            CATEGORY_LABEL['untested'], rendered,
        )


class ConstantsTests(SimpleTestCase):
    """Bonus lock: substrate stem set matches the S2728→S2732 corpus."""

    def test_substrate_stems_include_known_cross_cutting_docs(self):
        # S2728→S2732 shipped these as substrate concerns; the gap map
        # must classify them as substrate, not per-tool coverage.
        for stem in (
            'retry_behavior', 'payload_size_limits', 'celery_worker_lifecycle',
            'worker_cache_behavior', 'pa_use_function_calling_env',
        ):
            self.assertIn(stem, SUBSTRATE_DOC_STEMS)


class FindMatchingDocStemTests(SimpleTestCase):
    """Bonus lock: doc-stem match strategies."""

    def test_exact_match(self):
        self.assertEqual(
            find_matching_doc_stem('deliverable_tool', {'deliverable_tool': Path('/x')}),
            'deliverable_tool',
        )

    def test_tool_suffix_stripped(self):
        # session_tool → session_tool doc via exact match after strip.
        self.assertEqual(
            find_matching_doc_stem(
                'session_tool', {'session_tool': Path('/x')}
            ),
            'session_tool',
        )

    def test_no_match_returns_none(self):
        self.assertIsNone(
            find_matching_doc_stem('missing_tool', {'deliverable_tool': Path('/x')}),
        )


class GapMapIntegrationTest(SimpleTestCase):
    """Bonus: end-to-end build_gap_map + render_gap_map_markdown smoke."""

    def test_render_gap_map_markdown_shape(self):
        rows = [
            {
                'name': 'foo_tool', 'has_schema': True, 'has_handler': True,
                'actions': ['list'], 'description': '', 'required': [],
                'handler_file': 'core/services/td_handlers_core.py',
                'handler_name': '_handle_foo', 'handler_line': 1,
                'param_names': [], 'action_desc': '',
            },
        ]
        idx = {
            'per_tool_stems': {}, 'covered_actions_by_stem': {},
            'substrate_stems': set(), 'total_docs': 0,
        }
        summary = build_gap_map(
            rows=rows, docs_index=idx, schemas_by_name={},
            run_agent_targets=set(),
        )
        md = render_gap_map_markdown(rows=rows, summary=summary, docs_index=idx)
        # Advisory posture line present.
        self.assertIn('NOT a burn-down queue', md)
        # Headline section present.
        self.assertIn('## Headline', md)
        # Per-tool coverage table present.
        self.assertIn('## Per-tool coverage table', md)


# ============================================================================
# T1b (S2904) — Template-compliance lint tests.
#
# Ratchet-and-warn per T1b ship-shape §3. Rigby SIGN A/B/C/D/E/F folds
# reflected in test coverage. Rigby ZO-Q3 (regex loosening), ZO-Q6
# (both variants pass), ZO-Q9 (extra keys allowed) all exercised.
# ============================================================================

# Minimum valid v1 sweep doc used across tests. Trimmed to just enough
# to satisfy every mandatory section + required frontmatter field.
_SWEEP_V1_BODY = """\
# `foo_tool` — Validation Report (S2999)

**Tool:** `foo_tool`
**Schema:** `core/services/pa_tool_schemas.py:1`
**Handler:** `core/services/td_handlers_core.py:1` (`_handle_foo`)
**Register site:** `core/services/tool_dispatcher.py:1`
**Session:** S2999
**HEAD at validation:** `deadbeef1` (2026-07-22)
**Ship shape:** Doc-only.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2999 T1 SIGN AGREE.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use
purpose text

## Covered actions
- `list`

## 3. Schema notes
schema notes

## 4. Golden-path examples
examples

## 5. Failure / empty-state / pagination notes
failure notes

## 6. Evidence
evidence

## Related
related
"""

_PROTOCOL_V1_BODY = """\
# `bar_tool` — Validation Report

**Tool:** `bar_tool`
**Schema:** `core/services/pa_tool_schemas.py:1`
**Main handler:** `core/services/td_handlers_core.py:1` (`_handle_bar`)
**Register site:** `core/services/tool_dispatcher.py:1`
**Session validated:** S2999
**HEAD at validation:** `deadbeef2`
**Report status:** VERIFIED
**Rigby cross-check:** deferred
**Downstream service:** `core/services/bar_service.py`
**Reviewer:** Claude
**Template variant:** protocol
**Template version:** v1

---

## 1. Intended purpose (per schema description)
purpose

## 2. Rigby's belief (per schema)
belief

## 3. Schema claim (verbatim capture)
schema

## 4. Handler behavior (traced)
handler

## Findings
findings

## Verdict
verdict
"""


class T1bCoveredActionsRegexTests(SimpleTestCase):
    """T1b — Rigby SIGN D-2 loosened regex acceptance/rejection."""

    def test_accepts_bare_heading(self):
        self.assertIsNotNone(
            COVERED_ACTIONS_HEADING_RE.search('## Covered actions\n')
        )

    def test_accepts_numbered_with_period(self):
        self.assertIsNotNone(
            COVERED_ACTIONS_HEADING_RE.search('## 2. Covered actions\n')
        )

    def test_accepts_numbered_with_paren(self):
        self.assertIsNotNone(
            COVERED_ACTIONS_HEADING_RE.search('## 2) Covered actions\n')
        )

    def test_accepts_numbered_with_em_dash(self):
        self.assertIsNotNone(
            COVERED_ACTIONS_HEADING_RE.search('## 2 — Covered actions\n')
        )

    def test_rejects_word_order_reversal(self):
        """Rigby SIGN E test requirement — false positive rejection."""
        self.assertIsNone(
            COVERED_ACTIONS_HEADING_RE.search('## Actions covered\n')
        )


class T1bTemplateComplianceTests(SimpleTestCase):
    """T1b — evaluate_template_compliance verdicts across all doc states."""

    def _index_with(self, tmpdir: Path, docs: dict) -> dict:
        vdir = tmpdir / 'validation'
        vdir.mkdir(parents=True, exist_ok=True)
        for stem, body in docs.items():
            (vdir / f'{stem}_validation.md').write_text(body)
        return index_validation_docs(vdir)

    def test_legacy_doc_no_marker_warns(self):
        """No `Template version:` marker → warn (advisory)."""
        legacy_body = (
            '# `foo_tool` — Validation Report\n\n'
            '**Tool:** `foo_tool`\n\n---\n\n## 1. Purpose\ntext\n'
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': legacy_body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'warn')
        self.assertEqual(result['missing'], [])

    def test_v1_sweep_doc_passes(self):
        """v1 sweep doc with all mandatory sections + fields → pass."""
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': _SWEEP_V1_BODY})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'pass', msg=result['missing'])
        self.assertEqual(result['variant'], 'sweep')

    def test_v1_sweep_missing_covered_actions_fails(self):
        """v1 sweep missing `## Covered actions` → fail w/ correct tag."""
        body = _SWEEP_V1_BODY.replace(
            '## Covered actions\n- `list`\n\n', ''
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'fail')
        self.assertIn('template_v1_missing_covered_actions', result['missing'])

    def test_v1_protocol_doc_passes_with_alias_frontmatter(self):
        """v1 protocol doc using alias fields (Main handler, Rigby cross-check)
        → pass. Rigby SIGN B edit (alias tolerance, presence-not-exact)."""
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'bar_tool': _PROTOCOL_V1_BODY})
        result = evaluate_template_compliance('bar_tool', idx)
        self.assertEqual(result['verdict'], 'pass', msg=result['missing'])
        self.assertEqual(result['variant'], 'protocol')

    def test_invalid_template_version_value_fails(self):
        """`Template version: 1` (non-v-prefixed) → fail. Rigby SIGN C edit."""
        body = _SWEEP_V1_BODY.replace(
            '**Template version:** v1', '**Template version:** 1'
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'fail')
        self.assertIn('template_version_invalid', result['missing'])

    def test_invalid_template_variant_value_fails(self):
        """`Template variant: xyz` (unknown) → fail."""
        body = _SWEEP_V1_BODY.replace(
            '**Template variant:** sweep', '**Template variant:** xyz'
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'fail')
        self.assertIn('template_variant_invalid', result['missing'])

    def test_missing_required_frontmatter_field_fails(self):
        """v1 doc missing a required frontmatter field → fail w/ tag."""
        body = _SWEEP_V1_BODY.replace(
            '**Register site:** `core/services/tool_dispatcher.py:1`\n', ''
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'fail')
        self.assertIn(
            'template_v1_missing_frontmatter_register_site',
            result['missing'],
        )

    def test_extra_frontmatter_keys_do_not_break_pass(self):
        """Rigby ZO-Q9: extra frontmatter keys allowed (presence-not-exact)."""
        body = _SWEEP_V1_BODY.replace(
            '**Template version:** v1\n',
            '**Template version:** v1\n**Random extra key:** whatever\n',
        )
        with tempfile.TemporaryDirectory() as td:
            idx = self._index_with(Path(td), {'foo_tool': body})
        result = evaluate_template_compliance('foo_tool', idx)
        self.assertEqual(result['verdict'], 'pass', msg=result['missing'])


class T1bTemplateFileExclusionTests(SimpleTestCase):
    """T1b Rigby SIGN D-1 blocking mitigation — `_`-prefix filter."""

    def test_underscore_prefixed_file_excluded_from_index(self):
        """`_TEMPLATE_per_tool_validation.md` MUST NOT be indexed."""
        with tempfile.TemporaryDirectory() as td:
            vdir = Path(td) / 'validation'
            vdir.mkdir(parents=True)
            (vdir / '_TEMPLATE_per_tool_validation.md').write_text(
                _SWEEP_V1_BODY
            )
            (vdir / 'real_tool_validation.md').write_text(_SWEEP_V1_BODY)
            idx = index_validation_docs(vdir)
        self.assertIn('real_tool', idx['per_tool_stems'])
        self.assertNotIn('_TEMPLATE_per_tool', idx['per_tool_stems'])
        # Total count reflects the filter too.
        self.assertEqual(idx['total_docs'], 1)


class T1bLegacyStillWarnsInBuildGapMapTests(SimpleTestCase):
    """T1b Rigby ZO-Q6 same-PR requirement — legacy docs remain warn-only
    but still index correctly through the full build_gap_map flow."""

    def test_legacy_doc_shows_warn_in_gap_map(self):
        legacy_body = (
            '# `legacy_tool` — Validation Report\n\n'
            '**Tool:** `legacy_tool`\n\n---\n\n'
            '## 1. Purpose\ntext\n\n## Covered actions\n- `list`\n'
        )
        with tempfile.TemporaryDirectory() as td:
            vdir = Path(td) / 'validation'
            vdir.mkdir(parents=True)
            (vdir / 'legacy_tool_validation.md').write_text(legacy_body)
            idx = index_validation_docs(vdir)
        rows = [
            {
                'name': 'legacy_tool', 'has_schema': True, 'has_handler': True,
                'actions': ['list'], 'description': 'legacy',
                'required': [], 'handler_file': 'core/services/x.py',
                'handler_name': '_h', 'handler_line': 1,
                'param_names': [], 'action_desc': '',
            },
        ]
        summary = build_gap_map(
            rows=rows, docs_index=idx, schemas_by_name={},
            run_agent_targets=set(),
        )
        self.assertEqual(rows[0]['template_compliance'], 'warn')
        self.assertEqual(rows[0]['template_missing'], [])
        # Summary counter reflects the warn.
        per_tc = summary['headline']['per_template_compliance']
        self.assertEqual(per_tc.get('warn', 0), 1)

    def test_v1_doc_shows_pass_in_gap_map(self):
        with tempfile.TemporaryDirectory() as td:
            vdir = Path(td) / 'validation'
            vdir.mkdir(parents=True)
            (vdir / 'foo_tool_validation.md').write_text(_SWEEP_V1_BODY)
            idx = index_validation_docs(vdir)
        rows = [
            {
                'name': 'foo_tool', 'has_schema': True, 'has_handler': True,
                'actions': ['list'], 'description': 'foo',
                'required': [], 'handler_file': 'core/services/x.py',
                'handler_name': '_h', 'handler_line': 1,
                'param_names': [], 'action_desc': '',
            },
        ]
        summary = build_gap_map(
            rows=rows, docs_index=idx, schemas_by_name={},
            run_agent_targets=set(),
        )
        self.assertEqual(rows[0]['template_compliance'], 'pass')
        per_tc = summary['headline']['per_template_compliance']
        self.assertEqual(per_tc.get('pass', 0), 1)
