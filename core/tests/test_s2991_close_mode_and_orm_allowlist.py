"""Session 2991 — close_mode taxonomy + DocResearchFinding on orm_inspect_tool.

Two additive changes shipped across two PRs:

- **PR #3647** — additive `close_mode` column on `DocResearchFinding`
  (v2 item #1). Nullable 4-value CharField (`fixed_via_pr`,
  `evidence_delivered`, `deferred_to_arc`, `informational`). Migration
  0399 backfills the 3 S2990 canonical rows only; the existing
  `open/fixed/dismissed` `status` enum is untouched. Rigby SIGN caught
  axis confusion in Claude's original 6-value status-replacement proposal
  — the shipped shape is orthogonal: `status` = lifecycle, `close_mode` =
  closure mechanism.

- **This PR** — `DocResearchFinding` added to `orm_inspect_tool`'s
  `_MODEL_POLICIES` allowlist (v2 item #5). Same S2990 → S2991 tool-gap
  blocker hit twice: Rigby couldn't verify finding state without dropping
  to Claude-side ORM. Two triggers justify closing the gap.
"""
from __future__ import annotations

from django.test import TestCase

from core.models_audit_findings import DocResearchFinding
from core.services.tool_dispatcher import get_tool_dispatcher


def _run(payload):
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers['orm_inspect_tool']
    return handler(
        tool_name='orm_inspect_tool',
        payload=payload,
        user_id=None,
        trace_id='test-s2991-trace',
    )


class CloseModeFieldTests(TestCase):
    """PR #3647: close_mode field is orthogonal to status."""

    def test_close_mode_choices_are_four_values(self):
        values = {c[0] for c in DocResearchFinding.CLOSE_MODE_CHOICES}
        self.assertEqual(
            values,
            {'fixed_via_pr', 'evidence_delivered', 'deferred_to_arc', 'informational'},
        )

    def test_close_mode_defaults_to_null(self):
        f = DocResearchFinding.objects.create(
            doc_path='docs/research/example.md',
            text_hash='hash-null-default',
            text='example bullet',
        )
        self.assertIsNone(f.close_mode)
        # Lifecycle status unchanged by close_mode existence.
        self.assertEqual(f.status, DocResearchFinding.STATUS_OPEN)

    def test_close_mode_accepts_all_four_values(self):
        for close_mode in ('fixed_via_pr', 'evidence_delivered', 'deferred_to_arc', 'informational'):
            f = DocResearchFinding.objects.create(
                doc_path=f'docs/research/{close_mode}.md',
                text_hash=f'hash-{close_mode}',
                text='bullet',
                status=DocResearchFinding.STATUS_FIXED,
                close_mode=close_mode,
            )
            self.assertEqual(f.close_mode, close_mode)


class OrmInspectDocResearchFindingTests(TestCase):
    """This PR: DocResearchFinding reachable via orm_inspect_tool without shell."""

    def setUp(self):
        # Two fixed rows with different close_modes + one open + one dismissed.
        DocResearchFinding.objects.create(
            doc_path='docs/research/a.md', text_hash='h-a', text='a bullet',
            status=DocResearchFinding.STATUS_FIXED, close_mode='fixed_via_pr',
        )
        DocResearchFinding.objects.create(
            doc_path='docs/research/b.md', text_hash='h-b', text='b bullet',
            status=DocResearchFinding.STATUS_FIXED, close_mode='evidence_delivered',
        )
        DocResearchFinding.objects.create(
            doc_path='docs/research/c.md', text_hash='h-c', text='c bullet',
            status=DocResearchFinding.STATUS_OPEN,
        )
        DocResearchFinding.objects.create(
            doc_path='docs/research/d.md', text_hash='h-d', text='d bullet',
            status=DocResearchFinding.STATUS_DISMISSED,
        )

    def test_list_models_includes_doc_research_finding(self):
        result = _run({'action': 'list_models'})
        self.assertTrue(result['ok'])
        names = {m['name'] for m in result['models']}
        self.assertIn('DocResearchFinding', names)

    def test_describe_model_doc_research_finding(self):
        result = _run({'action': 'describe_model', 'model': 'DocResearchFinding'})
        self.assertTrue(result['ok'], msg=result)
        self.assertEqual(result['model'], 'DocResearchFinding')
        self.assertFalse(result['sensitive_model'])
        self.assertIn('text', result['expensive_text_fields'])
        self.assertIn('resolution_note', result['expensive_text_fields'])
        field_names = {f['name'] for f in result['fields']}
        for expected in ('id', 'status', 'close_mode', 'doc_path', 'text_hash', 'confidence'):
            self.assertIn(expected, field_names)

    def test_filter_by_close_mode(self):
        result = _run({
            'action': 'filter',
            'model': 'DocResearchFinding',
            'filter_kwargs': {'close_mode': 'evidence_delivered'},
            'limit': 10,
        })
        self.assertTrue(result['ok'], msg=result)
        self.assertEqual(result['total_matching'], 1)

    def test_count_by_close_mode(self):
        result = _run({
            'action': 'count_by',
            'model': 'DocResearchFinding',
            'field': 'close_mode',
        })
        self.assertTrue(result['ok'], msg=result)
        by_close_mode = {g['value']: g['count'] for g in result['groups']}
        # 1 fixed_via_pr + 1 evidence_delivered + 2 nulls (open + dismissed).
        self.assertEqual(by_close_mode.get('fixed_via_pr'), 1)
        self.assertEqual(by_close_mode.get('evidence_delivered'), 1)

    def test_contains_rejected_on_expensive_text_field(self):
        # Parity: `text` is registered as expensive_text; contains lookups
        # must be rejected the same way as on other allowlisted models.
        result = _run({
            'action': 'filter',
            'model': 'DocResearchFinding',
            'filter_kwargs': {'text__contains': 'bullet'},
        })
        self.assertFalse(result['ok'])
        self.assertIn('expensive text field', result['error'])
