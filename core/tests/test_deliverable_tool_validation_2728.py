"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch A tool 1
regression tests for `deliverable_tool`.

Covers the F-D-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/deliverable_tool_validation.md` (findings)
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` (campaign)

Findings covered:
- F-D-2 / F-D-4: action inference surfaces original_action + inferred_action
- F-D-3: unknown action returns typed error envelope, not silent pass-through
- F-D-5: list with limit > 50 surfaces limit_capped/requested_limit/effective_limit/hard_max
- F-D-6: create default status is 'ready' (not 'completed'); explicit status
  honored within whitelist; status='completed' rejected with typed error
- F-D-7: update status='completed' returns typed error pointing to
  content_tool.content_complete
- F-D-8: update response includes status field
- F-D-20: list response items include updated_at
- F-D-21: detail response provenance block includes source + agent_name

Run::

    python manage.py test core.tests.test_deliverable_tool_validation_2728 -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_factory import create_deliverable
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


def _make_content(length=500):
    """Build a content string of the desired length (default 500 chars — over
    the factory's 300-char gate for pa_tool trigger_source)."""
    base = "This is validation content for Session 2728 regression tests. "
    return (base * ((length // len(base)) + 1))[:length]


class DeliverableToolValidation2728Base(TestCase):
    """Shared setup — a PA-like superuser + workspace + one existing deliverable
    for update/append/detail tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'pa-service-2728-{uuid.uuid4().hex[:8]}',
            email='pa-2728@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name='validation-2728-ws',
        )
        cls.existing = create_deliverable(
            title='Session 2728 baseline deliverable',
            content=_make_content(500),
            agent_name='rigby',
            category='Validation',
            deliverable_type='document',
            user=cls.user,
            workspace_id=str(cls.workspace.id),
            trace_id='trace-2728-baseline',
            tags=['validation-2728'],
            content_format='markdown',
            metadata={
                'source': 'pa_deliverables_tool',
                'trigger_source': 'pa_tool',
                'trace_id': 'trace-2728-baseline',
            },
            status='ready',
            raise_on_gated=True,
        )

    def _dispatch(self, payload):
        """Call deliverable_tool via the ToolDispatcher (matches PA path)."""
        dispatcher = ToolDispatcher()
        # Direct handler for synchronous test execution (skip async loop).
        # Mirrors what the PA dispatch does inside the agentic loop.
        return dispatcher._handle_deliverable_direct(  # type: ignore[attr-defined]
            'deliverable_tool',
            payload,
            self.user.id,
            'trace-2728-test',
        )


class FD6CreateDefaultStatus(DeliverableToolValidation2728Base):
    """F-D-6 — create default status must be 'ready' (not 'completed');
    explicit status honored; 'completed' rejected with typed error."""

    def test_create_no_status_defaults_to_ready(self):
        result = self._dispatch({
            'action': 'create',
            'title': 'F-D-6 no status',
            'content': _make_content(500),
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('status'), 'ready')

    def test_create_explicit_draft_honored(self):
        result = self._dispatch({
            'action': 'create',
            'title': 'F-D-6 explicit draft',
            'content': _make_content(500),
            'status': 'draft',
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('status'), 'draft')

    def test_create_explicit_published_honored(self):
        result = self._dispatch({
            'action': 'create',
            'title': 'F-D-6 explicit published',
            'content': _make_content(500),
            'status': 'published',
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('status'), 'published')

    def test_create_completed_returns_typed_error(self):
        result = self._dispatch({
            'action': 'create',
            'title': 'F-D-6 completed rejected',
            'content': _make_content(500),
            'status': 'completed',
            'workspace_id': str(self.workspace.id),
        })
        self.assertFalse(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('error_code'), 'status_completed_not_allowed_on_create')
        self.assertIn('content_tool.content_complete', result.get('message', ''))
        self.assertIn('set_status', result.get('message', ''))

    def test_create_unknown_status_falls_back_to_ready(self):
        # Any string not in the whitelist falls back to 'ready' with a
        # WARNING log; the row still lands as 'ready'.
        result = self._dispatch({
            'action': 'create',
            'title': 'F-D-6 unknown status',
            'content': _make_content(500),
            'status': 'wibble',
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('status'), 'ready')


class FD7UpdateStatusCompleted(DeliverableToolValidation2728Base):
    """F-D-7 — update with status='completed' returns typed error pointing at
    content_tool.content_complete / set_status."""

    def test_update_status_completed_returns_typed_error(self):
        result = self._dispatch({
            'action': 'update',
            'id': str(self.existing.id),
            'status': 'completed',
        })
        self.assertFalse(result.get('ok'), msg=repr(result))
        self.assertEqual(result.get('error_code'), 'status_completed_not_allowed_on_update')
        self.assertIn('content_tool.content_complete', result.get('message', ''))
        self.assertIn('set_status', result.get('message', ''))
        # Row's status must NOT have been mutated.
        self.existing.refresh_from_db()
        self.assertEqual(self.existing.status, 'ready')

    def test_update_status_draft_still_works(self):
        # Regression guard: the typed-error gate only fires on 'completed'.
        # Other whitelisted transitions must still land as before.
        result = self._dispatch({
            'action': 'update',
            'id': str(self.existing.id),
            'status': 'draft',
        })
        self.assertNotEqual(result.get('error_code'), 'status_completed_not_allowed_on_update')
        self.assertIn('status', result.get('updated_fields', []))
        self.existing.refresh_from_db()
        self.assertEqual(self.existing.status, 'draft')


class FD5ListLimitCap(DeliverableToolValidation2728Base):
    """F-D-5 — list with requested limit > 50 surfaces limit_capped envelope."""

    def test_list_within_cap_no_capped_signal(self):
        result = self._dispatch({
            'action': 'list',
            'limit': 20,
            'workspace_id': str(self.workspace.id),
        })
        self.assertNotIn('limit_capped', result)

    def test_list_over_cap_surfaces_signal(self):
        result = self._dispatch({
            'action': 'list',
            'limit': 200,
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('requested_limit'), 200)
        self.assertEqual(result.get('effective_limit'), 50)
        self.assertEqual(result.get('hard_max'), 50)
        self.assertLessEqual(result.get('limit'), 50)

    def test_search_over_cap_surfaces_signal(self):
        # Search action shares the same cap; ensures F-D-5 is applied there too.
        result = self._dispatch({
            'action': 'search',
            'query': 'validation',
            'limit': 500,
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('limit_capped'))
        self.assertEqual(result.get('hard_max'), 50)


class FD8UpdateResponseStatus(DeliverableToolValidation2728Base):
    """F-D-8 — update response must include the persisted status field."""

    def test_update_response_includes_status(self):
        result = self._dispatch({
            'action': 'update',
            'id': str(self.existing.id),
            'title': 'F-D-8 renamed',
        })
        self.assertIn('status', result)
        self.assertEqual(result.get('status'), self.existing.status)


class FD20ListUpdatedAt(DeliverableToolValidation2728Base):
    """F-D-20 — list response items include updated_at."""

    def test_list_items_include_updated_at(self):
        result = self._dispatch({
            'action': 'list',
            'workspace_id': str(self.workspace.id),
        })
        items = result.get('items', [])
        self.assertGreater(len(items), 0, msg="No items in list — setup failure?")
        for item in items:
            self.assertIn('updated_at', item)


class FD21ProvenanceSurface(DeliverableToolValidation2728Base):
    """F-D-21 — detail response provenance block includes source + agent_name."""

    def test_detail_provenance_includes_source(self):
        result = self._dispatch({
            'action': 'detail',
            'id': str(self.existing.id),
        })
        provenance = result.get('provenance') or {}
        # Baseline deliverable was created with metadata.source='pa_deliverables_tool'.
        self.assertEqual(provenance.get('source'), 'pa_deliverables_tool')
        # Agent name is canonicalized to 'Rigby' by the factory's alias map
        # (feedback_deliverable_workspace + deliverable_factory canonicalization).
        self.assertEqual(provenance.get('agent_name'), 'Rigby')
        self.assertEqual(provenance.get('trigger_source'), 'pa_tool')


class FD3UnknownAction(DeliverableToolValidation2728Base):
    """F-D-3 — unknown actions return a typed error envelope from layer 1."""

    def test_unknown_action_returns_typed_error(self):
        result = self._dispatch({
            'action': 'wibble_the_thing',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result.get('error_code'), 'unknown_deliverable_action')
        self.assertIn('wibble_the_thing', result.get('message', ''))
        # Response echoes the invalid action for diagnosis.
        self.assertEqual(result.get('action'), 'wibble_the_thing')
        # Layer 1 always tags gateway.
        self.assertEqual(result.get('gateway'), 'deliverable_tool')


class FD2InferenceEnvelope(DeliverableToolValidation2728Base):
    """F-D-2 / F-D-4 — action inference at layer 1 surfaces original_action +
    inferred_action + action_inferred + action_inferred_reason."""

    def test_list_with_title_and_content_infers_create(self):
        result = self._dispatch({
            'action': 'list',
            'title': 'F-D-2 inferred create',
            'content': _make_content(500),
            'workspace_id': str(self.workspace.id),
        })
        self.assertTrue(result.get('action_inferred'))
        self.assertEqual(result.get('original_action'), 'list')
        self.assertEqual(result.get('inferred_action'), 'create')
        self.assertIn('title+content', result.get('action_inferred_reason', ''))
        # The underlying create must still have executed.
        self.assertTrue(result.get('ok'))

    def test_list_with_id_and_content_infers_append(self):
        result = self._dispatch({
            'action': 'list',
            'id': str(self.existing.id),
            'content': 'F-D-2 appended text.',
        })
        self.assertTrue(result.get('action_inferred'))
        self.assertEqual(result.get('original_action'), 'list')
        self.assertEqual(result.get('inferred_action'), 'append')
        self.assertIn('id+content', result.get('action_inferred_reason', ''))

    def test_normal_action_no_inference_envelope(self):
        # Regression guard: if action is explicit and unambiguous, inference
        # fields must NOT appear.
        result = self._dispatch({
            'action': 'list',
            'workspace_id': str(self.workspace.id),
        })
        self.assertNotIn('action_inferred', result)
        self.assertNotIn('original_action', result)
        self.assertNotIn('inferred_action', result)
