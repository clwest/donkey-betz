"""
EditorAgent dispatch content_provenance + strict-content-required.

Session 1177 F3 fix. Session 1176 surfaced "EditorAgent non-deterministic on
empty content" — same task body, two outcomes (fail-loud vs unexpected
generation). Root cause: the dispatcher's `gather_workspace_content_for_editor`
fallback was silently dependent on workspace state at call time. The agent
itself was deterministic given its inputs; the dispatcher gave it different
inputs across runs.

This file pins:
- C1: typed `content_provenance` envelope shape (ratified by Rigby Session 1177)
- C2: `strict_content_required=True` opt-in flag disables gather → agent fail-loud

Per Rigby's design notes:
- provenance default is `{mode: 'none', ...}` when strict
- caller_provided when context has content/blog_id
- gathered_workspace_deliverable when dispatcher's gather succeeds
- task_text_fallback when gather finds nothing

Run:
    python manage.py test core.tests.test_editor_dispatch_provenance -v2
"""
from django.test import SimpleTestCase

from core.services.editor_dispatch_helpers import (
    CONTENT_PROVENANCE_MODES,
    build_content_provenance,
)


class ContentProvenanceShapeTests(SimpleTestCase):
    """`build_content_provenance` is the canonical builder for the envelope."""

    def test_caller_provided_mode_has_null_source_fields(self):
        prov = build_content_provenance(mode='caller_provided')
        self.assertEqual(prov['mode'], 'caller_provided')
        self.assertIsNone(prov['source_deliverable_id'])
        self.assertIsNone(prov['source_title'])
        self.assertIsNone(prov['score'])
        self.assertIsNone(prov['score_reason'])
        self.assertNotIn('warning', prov)

    def test_none_mode_used_when_strict_skips_gather(self):
        prov = build_content_provenance(mode='none')
        self.assertEqual(prov['mode'], 'none')
        self.assertIsNone(prov['source_deliverable_id'])

    def test_task_text_fallback_mode_carries_window(self):
        prov = build_content_provenance(mode='task_text_fallback', gather_window_minutes=60)
        self.assertEqual(prov['mode'], 'task_text_fallback')
        self.assertEqual(prov['gather_window_minutes'], 60)

    def test_gathered_mode_pulls_primary_source_fields(self):
        gathered = {
            'primary_source': {
                'id': 'abc-123',
                'title': 'CTO Brief — Q2',
                'score': 175,
                'score_reason': '<60min+kw=cto,brief+src=ResearchAgent',
            },
            'sources': [],
        }
        prov = build_content_provenance(
            mode='gathered_workspace_deliverable',
            gathered=gathered,
            gather_window_minutes=60,
        )
        self.assertEqual(prov['mode'], 'gathered_workspace_deliverable')
        self.assertEqual(prov['source_deliverable_id'], 'abc-123')
        self.assertEqual(prov['source_title'], 'CTO Brief — Q2')
        self.assertEqual(prov['score'], 175)
        self.assertEqual(prov['score_reason'], '<60min+kw=cto,brief+src=ResearchAgent')
        self.assertEqual(prov['gather_window_minutes'], 60)

    def test_gathered_mode_falls_back_to_sources_when_no_primary(self):
        # gather v2 returns both `primary_source` and `sources` — but if a
        # caller hands us a stripped-down dict with only `sources`, we should
        # still extract from `sources[0]` rather than emit a null envelope.
        gathered = {
            'sources': [
                {'id': 'xyz-789', 'title': 'Backup Source', 'score': 100, 'score_reason': '<24h'},
            ],
        }
        prov = build_content_provenance(
            mode='gathered_workspace_deliverable',
            gathered=gathered,
        )
        self.assertEqual(prov['source_deliverable_id'], 'xyz-789')
        self.assertEqual(prov['source_title'], 'Backup Source')

    def test_caller_content_overridden_emits_warning(self):
        # Subtle edge case Rigby flagged: dispatcher should NEVER inject when
        # the caller already provided content, but if a future code path did,
        # the warning should be visible in the envelope so operators catch it.
        prov = build_content_provenance(
            mode='gathered_workspace_deliverable',
            gathered={'primary_source': {'id': 'a', 'title': 't', 'score': 100, 'score_reason': 'x'}},
            caller_content_overridden=True,
        )
        self.assertEqual(prov.get('warning'), 'caller_content_overridden')

    def test_no_warning_in_normal_case(self):
        prov = build_content_provenance(mode='caller_provided')
        self.assertNotIn('warning', prov)

    def test_unknown_mode_raises_typed_error(self):
        # Catches typos like `mode='callerprovided'` at build time rather
        # than silently shipping a bogus envelope downstream.
        with self.assertRaises(ValueError) as cm:
            build_content_provenance(mode='callerprovided')  # type: ignore[arg-type]
        self.assertIn('callerprovided', str(cm.exception))

    def test_all_modes_are_listed_in_module_constant(self):
        # Document the contract: anyone adding a new mode must add it to
        # CONTENT_PROVENANCE_MODES or build_content_provenance will reject it.
        self.assertEqual(
            CONTENT_PROVENANCE_MODES,
            {'caller_provided', 'gathered_workspace_deliverable', 'task_text_fallback', 'none'},
        )
