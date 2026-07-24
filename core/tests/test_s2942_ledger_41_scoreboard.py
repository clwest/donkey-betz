"""Session 2942 — Ledger #41 promotion: two-metric scoreboard classifier extension.

Extends ``pa_tools_gap_map.index_validation_docs`` + ``build_gap_map``
with parsing of two new opt-in frontmatter fields:

- ``**Execution mode:** live | analyzed``
- ``**Mutation safety:** dry_run_supported | unsafe_no_dry_run``

Missing / out-of-enum values normalize to ``'unknown'`` (no silent
default) per plan §2.1 acceptance.
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase

from core.services.pa_tools_gap_map import (
    EXECUTION_MODES,
    MUTATION_SAFETY_VALUES,
    UNKNOWN_LABEL,
    build_gap_map,
    index_validation_docs,
)


def _write(tmp: Path, stem: str, body: str) -> None:
    vdir = tmp / 'validation'
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / f'{stem}_validation.md').write_text(body)


class IndexingTests(TestCase):
    """Frontmatter parsing under ``index_validation_docs``."""

    def test_both_fields_present_and_valid_are_parsed(self):
        body = (
            '**Tool:** foo_tool\n'
            '**Execution mode:** live\n'
            '**Mutation safety:** dry_run_supported\n'
            '\n---\n\n'
            '# foo_tool\n'
        )
        with tempfile.TemporaryDirectory() as td:
            _write(Path(td), 'foo_tool', body)
            idx = index_validation_docs(Path(td) / 'validation')
        self.assertEqual(idx['execution_mode_by_stem']['foo_tool'], 'live')
        self.assertEqual(idx['mutation_safety_by_stem']['foo_tool'], 'dry_run_supported')

    def test_missing_fields_normalize_to_unknown(self):
        body = (
            '**Tool:** foo_tool\n'
            '\n---\n\n'
            '# foo_tool\n'
        )
        with tempfile.TemporaryDirectory() as td:
            _write(Path(td), 'foo_tool', body)
            idx = index_validation_docs(Path(td) / 'validation')
        self.assertEqual(idx['execution_mode_by_stem']['foo_tool'], UNKNOWN_LABEL)
        self.assertEqual(idx['mutation_safety_by_stem']['foo_tool'], UNKNOWN_LABEL)

    def test_out_of_enum_values_normalize_to_unknown(self):
        body = (
            '**Tool:** foo_tool\n'
            '**Execution mode:** partial\n'
            '**Mutation safety:** maybe\n'
            '\n---\n\n'
            '# foo_tool\n'
        )
        with tempfile.TemporaryDirectory() as td:
            _write(Path(td), 'foo_tool', body)
            idx = index_validation_docs(Path(td) / 'validation')
        self.assertEqual(idx['execution_mode_by_stem']['foo_tool'], UNKNOWN_LABEL)
        self.assertEqual(idx['mutation_safety_by_stem']['foo_tool'], UNKNOWN_LABEL)

    def test_case_insensitive_values_normalize(self):
        body = (
            '**Tool:** foo_tool\n'
            '**Execution mode:** LIVE\n'
            '**Mutation safety:** Dry_Run_Supported\n'
            '\n---\n\n'
            '# foo_tool\n'
        )
        with tempfile.TemporaryDirectory() as td:
            _write(Path(td), 'foo_tool', body)
            idx = index_validation_docs(Path(td) / 'validation')
        self.assertEqual(idx['execution_mode_by_stem']['foo_tool'], 'live')
        self.assertEqual(idx['mutation_safety_by_stem']['foo_tool'], 'dry_run_supported')

    def test_missing_docs_dir_returns_empty_scoreboard_dicts(self):
        idx = index_validation_docs(Path('/nonexistent/path'))
        self.assertEqual(idx['execution_mode_by_stem'], {})
        self.assertEqual(idx['mutation_safety_by_stem'], {})

    def test_enum_constants_shape(self):
        self.assertEqual(EXECUTION_MODES, {'live', 'analyzed'})
        self.assertEqual(MUTATION_SAFETY_VALUES, {'dry_run_supported', 'unsafe_no_dry_run'})
        self.assertEqual(UNKNOWN_LABEL, 'unknown')


class SummaryTests(TestCase):
    """Headline scoreboard emission under ``build_gap_map``."""

    def _summary_for_rows(self, docs: dict[str, str]) -> dict:
        with tempfile.TemporaryDirectory() as td:
            for stem, body in docs.items():
                _write(Path(td), stem, body)
            idx = index_validation_docs(Path(td) / 'validation')
        rows = [
            {
                'name': stem,
                'has_schema': True,
                'has_handler': True,
                'actions': [],
                'handler_source': '',
                'handler_docstring': '',
            }
            for stem in docs
        ]
        return build_gap_map(
            rows=rows,
            schemas_by_name={},
            docs_index=idx,
            run_agent_targets=set(),
        )

    def test_headline_counts_per_execution_mode(self):
        docs = {
            'foo_tool': (
                '**Execution mode:** live\n'
                '**Mutation safety:** dry_run_supported\n'
                '\n---\n# foo\n'
            ),
            'bar_tool': (
                '**Execution mode:** analyzed\n'
                '**Mutation safety:** unsafe_no_dry_run\n'
                '\n---\n# bar\n'
            ),
            'baz_tool': '**Tool:** baz\n\n---\n# baz\n',  # unknown/unknown
        }
        summary = self._summary_for_rows(docs)
        h = summary['headline']
        self.assertEqual(h['per_execution_mode'], {
            'live': 1,
            'analyzed': 1,
            'unknown': 1,
        })
        self.assertEqual(h['per_mutation_safety'], {
            'dry_run_supported': 1,
            'unsafe_no_dry_run': 1,
            'unknown': 1,
        })

    def test_validation_doc_totals_counts_opt_ins(self):
        docs = {
            'foo_tool': (
                '**Execution mode:** live\n'
                '**Mutation safety:** dry_run_supported\n'
                '\n---\n# foo\n'
            ),
            'bar_tool': '**Tool:** bar\n\n---\n# bar\n',
        }
        summary = self._summary_for_rows(docs)
        totals = summary['validation_doc_totals']
        self.assertEqual(totals['per_tool_docs_with_execution_mode'], 1)
        self.assertEqual(totals['per_tool_docs_with_mutation_safety'], 1)

    def test_row_gets_execution_mode_and_mutation_safety_fields(self):
        docs = {
            'foo_tool': (
                '**Execution mode:** live\n'
                '**Mutation safety:** dry_run_supported\n'
                '\n---\n# foo\n'
            ),
        }
        with tempfile.TemporaryDirectory() as td:
            for stem, body in docs.items():
                _write(Path(td), stem, body)
            idx = index_validation_docs(Path(td) / 'validation')
        rows = [{
            'name': 'foo_tool',
            'has_schema': True,
            'has_handler': True,
            'actions': [],
            'handler_source': '',
            'handler_docstring': '',
        }]
        build_gap_map(
            rows=rows,
            schemas_by_name={},
            docs_index=idx,
            run_agent_targets=set(),
        )
        self.assertEqual(rows[0]['execution_mode'], 'live')
        self.assertEqual(rows[0]['mutation_safety'], 'dry_run_supported')

    def test_row_without_matched_doc_is_unknown(self):
        summary = self._summary_for_rows({})
        # Tools with no doc land in `unknown` bucket via the row-level
        # default (see build_gap_map S2942 block).
        h = summary['headline']
        # With no rows we can't assert per-value counts; instead, add a
        # row synthetically to prove the default-when-unmatched path.
        rows = [{
            'name': 'no_doc_tool',
            'has_schema': True,
            'has_handler': True,
            'actions': [],
            'handler_source': '',
            'handler_docstring': '',
        }]
        build_gap_map(
            rows=rows,
            schemas_by_name={},
            docs_index={'per_tool_stems': {}, 'total_docs': 0},
            run_agent_targets=set(),
        )
        self.assertEqual(rows[0]['execution_mode'], UNKNOWN_LABEL)
        self.assertEqual(rows[0]['mutation_safety'], UNKNOWN_LABEL)
