"""Session 1248 P2b — deliverable_tool.create status echo + return_detail opt-in.

Closes the verify-then-set_status round-trip documented in
`feedback_deliverable_create_defaults_to_completed.md`:

  Status is ALWAYS echoed at top level (Rigby Q1c delta #1/#2 — canonical
  field name, source of truth). `return_detail=True` triggers a follow-up
  detail fetch embedded under `detail` key with `detail_included: bool`
  (Rigby deltas #3/#4). Detail-fetch failure is soft (warn + flag false;
  create still succeeds).
"""
from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch_deliverable(user_id, payload):
    """Invoke the deliverables handler the same way deliverable_tool routes."""
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload=payload,
        user_id=user_id,
        trace_id='test-1248-p2b',
    )


def _create_payload(**overrides):
    base = {
        'action': 'create',
        'title': 'S1248 P2b verify',
        'content': (
            'Lorem ipsum content '
            'sufficiently long to clear any gate that filters short bodies. ' * 20
        ),
        'category': 'Audit',
    }
    base.update(overrides)
    return base


class DeliverableCreateStatusEchoTests(TestCase):
    """Top-level `status` must be in every successful create response."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
            is_staff=True,
        )

    def test_create_response_always_includes_status(self):
        result = _dispatch_deliverable(self.alice.id, _create_payload())
        self.assertTrue(result.get('ok'), msg=result)
        self.assertIn('status', result, msg=result)
        # The status field must equal the actual DB status, not a wishful
        # echo of any requested status. Verifies Rigby's delta #1.
        obj = Deliverable.objects.get(id=result['id'])
        self.assertEqual(result['status'], obj.status)

    def test_status_field_canonical_name(self):
        """No `created_status` / `to_status` drift — must be `status`."""
        result = _dispatch_deliverable(self.alice.id, _create_payload())
        self.assertNotIn('created_status', result)
        self.assertNotIn('to_status', result)


class DeliverableCreateReturnDetailOptInTests(TestCase):
    """return_detail=True embeds detail dict + detail_included flag."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
            is_staff=True,
        )

    def test_return_detail_false_omits_detail_keys(self):
        result = _dispatch_deliverable(self.alice.id, _create_payload())
        self.assertTrue(result.get('ok'))
        self.assertNotIn('detail', result)
        self.assertNotIn('detail_included', result)

    def test_return_detail_true_embeds_detail_dict(self):
        result = _dispatch_deliverable(
            self.alice.id,
            _create_payload(return_detail=True),
        )
        self.assertTrue(result.get('ok'))
        self.assertTrue(result.get('detail_included'))
        self.assertIn('detail', result)
        detail = result['detail']
        # Detail dict must echo the canonical detail-action shape (id, title,
        # content fields, provenance, status, etc.).
        self.assertEqual(detail['id'], result['id'])
        self.assertEqual(detail['title'], result['title'])
        self.assertIn('content', detail)
        self.assertIn('content_length', detail)
        self.assertIn('status', detail)
        # Top-level status remains source of truth (Rigby delta #3) — must
        # equal detail.status in the happy path.
        self.assertEqual(result['status'], detail['status'])

    def test_return_detail_accepts_string_truthy_values(self):
        for truthy in ('true', 'True', '1', 1):
            with self.subTest(value=truthy):
                result = _dispatch_deliverable(
                    self.alice.id,
                    _create_payload(
                        return_detail=truthy,
                        title=f'P2b truthy {truthy!r}',
                    ),
                )
                self.assertTrue(result.get('detail_included'), msg=result)
                self.assertIn('detail', result)

    def test_detail_fetch_failure_soft_fails(self):
        # Force the embedded detail call to raise — create should still
        # return ok=True with detail_included=False and no `detail` key.
        original = ToolDispatcher._handle_deliverables  # type: ignore[attr-defined]

        def flaky(self, tool_name, payload, user_id, trace_id):
            if payload.get('action') == 'detail':
                raise RuntimeError('synthetic detail failure for test')
            return original(self, tool_name, payload, user_id, trace_id)

        with patch.object(ToolDispatcher, '_handle_deliverables', flaky):
            result = _dispatch_deliverable(
                self.alice.id,
                _create_payload(return_detail=True),
            )
        self.assertTrue(result.get('ok'), msg=result)
        self.assertEqual(result.get('detail_included'), False)
        self.assertNotIn('detail', result)
        # Top-level status still present even when the detail follow-up fails.
        self.assertIn('status', result)

    def test_detail_fetch_returning_error_dict_soft_fails(self):
        original = ToolDispatcher._handle_deliverables  # type: ignore[attr-defined]

        def errored(self, tool_name, payload, user_id, trace_id):
            if payload.get('action') == 'detail':
                return {'error': 'synthetic-not-found', 'action': 'detail'}
            return original(self, tool_name, payload, user_id, trace_id)

        with patch.object(ToolDispatcher, '_handle_deliverables', errored):
            result = _dispatch_deliverable(
                self.alice.id,
                _create_payload(return_detail=True),
            )
        self.assertTrue(result.get('ok'))
        self.assertEqual(result.get('detail_included'), False)
        self.assertNotIn('detail', result)


class DeliverableToolSchemaTests(TestCase):
    """Schema must advertise return_detail to the LLM."""

    def test_return_detail_in_schema_properties(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        deliverable_schema = next(
            s for s in PA_TOOL_SCHEMAS if s.get('name') == 'deliverable_tool'
        )
        props = deliverable_schema['parameters']['properties']
        self.assertIn('return_detail', props)
        self.assertEqual(props['return_detail']['type'], 'boolean')
        # Description should make the BC promise explicit (status always
        # echoed) so the LLM understands when to use this flag.
        self.assertIn('status', props['return_detail']['description'])
