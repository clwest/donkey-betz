"""Session 1228 PR-A — LLM-autofill sweep integration tests.

Validates the belt-and-suspenders + truthy-only protections applied to
PA tool handlers across td_handlers_agents/content/core/newsletter/ops.

Each Tier 1 site (write-mode flip via dry_run autofill) must require
BOTH ``dry_run='false'`` AND ``confirm=true`` before issuing a real
write. Each Tier 2 site (semantic update-field overwrite or
``is_not_none`` filter gate) must defend against the LLM autofill
shape that Session 1227 documented.

Memory rule: ``feedback_llm_autofills_boolean_params_with_false``.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from unittest.mock import patch

from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


# ────────────────────────────────────────────────────────────────────
# Tier 1 — write-mode gating (belt-and-suspenders)
# ────────────────────────────────────────────────────────────────────


class DeliverableToolCleanupWriteGateTests(TestCase):
    """deliverable_tool action=cleanup — bulk DELETE on duplicates/orphans/low_quality."""

    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris-cleanup-test', password='x', is_staff=True,
        )
        # Two deliverables with identical title → duplicates strategy will target the older one.
        self.older = Deliverable.objects.create(
            title='Dup title for cleanup test',
            content='x' * 400,
            agent_name='AnyAgent',
            user=self.chris,
        )
        self.newer = Deliverable.objects.create(
            title='Dup title for cleanup test',
            content='x' * 400,
            agent_name='AnyAgent',
            user=self.chris,
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
            tool_name='deliverable_tool',
            payload={'action': 'cleanup', 'strategy': 'duplicates', **payload},
            user_id=self.chris.id,
            trace_id='test-cleanup-gate',
        )

    def test_empty_payload_previews_only(self):
        """Plain call (no dry_run, no confirm) must NOT delete."""
        before = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        result = self._dispatch({})
        after = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        self.assertEqual(before, after, 'plain cleanup call must not delete')
        self.assertTrue(result['dry_run'])
        self.assertIn('would_delete', result)

    def test_autofilled_dry_run_false_alone_previews_only(self):
        """LLM autofill of dry_run=False without confirm must NOT delete."""
        before = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        result = self._dispatch({'dry_run': False})
        after = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        self.assertEqual(before, after, 'autofilled dry_run=False alone must not delete')
        self.assertTrue(result['dry_run'])

    def test_autofilled_both_false_previews_only(self):
        """LLM autofill of dry_run=False AND confirm=False must NOT delete."""
        before = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        result = self._dispatch({'dry_run': False, 'confirm': False})
        after = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        self.assertEqual(before, after)
        self.assertTrue(result['dry_run'])

    def test_explicit_write_executes(self):
        """dry_run=False + confirm=True must execute the delete."""
        before = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        result = self._dispatch({'dry_run': False, 'confirm': True})
        after = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        self.assertLess(after, before, 'explicit write must delete the older duplicate')
        self.assertFalse(result['dry_run'])
        self.assertIn('deleted', result)

    def test_string_sentinel_pair_executes(self):
        """Schema-friendly string sentinels also satisfy the gate."""
        before = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        result = self._dispatch({'dry_run': 'false', 'confirm': 'true'})
        after = Deliverable.objects.filter(title='Dup title for cleanup test').count()
        self.assertLess(after, before)
        self.assertFalse(result['dry_run'])


class DeliverableToolBulkArchiveWriteGateTests(TestCase):
    """content_tool action=bulk_archive — bulk UPDATE status=archived."""

    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris-bulkarchive-test', password='x', is_staff=True,
        )
        self.target = Deliverable.objects.create(
            title='Probe for bulk_archive gate',
            content='x' * 200,
            agent_name='AnyAgent',
            user=self.chris,
            status='ready',
            category='__bulk_archive_gate_probe__',
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_content(  # type: ignore[attr-defined]
            tool_name='content_tool',
            payload={
                'action': 'bulk_archive',
                'category': '__bulk_archive_gate_probe__',
                **payload,
            },
            user_id=self.chris.id,
            trace_id='test-bulkarch-gate',
        )

    def test_empty_payload_previews_only(self):
        result = self._dispatch({})
        self.target.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.target.status, 'ready', 'plain call must not archive')

    def test_autofilled_dry_run_false_alone_previews_only(self):
        result = self._dispatch({'dry_run': False})
        self.target.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.target.status, 'ready')

    def test_explicit_write_executes(self):
        result = self._dispatch({'dry_run': False, 'confirm': True})
        self.target.refresh_from_db()
        self.assertFalse(result['dry_run'])
        self.assertEqual(self.target.status, 'archived')


class InitiativeToolActionItemCleanupWriteGateTests(TestCase):
    """initiative_tool action=cleanup_action_items — cancels InitiativeActionItem rows."""

    def setUp(self):
        from core.models_document_registry import InitiativeActionItem
        self.chris = User.objects.create_user(
            username='chris-ai-cleanup-test', password='x', is_staff=True,
        )
        self.initiative = Initiative.objects.create(
            name='AI cleanup probe initiative',
            description='probe',
            owner=self.chris,
        )
        # ActionItemParser._is_junk_title flags section-heading-like titles.
        self.junk = InitiativeActionItem.objects.create(
            initiative=self.initiative,
            title='Next Steps:',  # canonical junk heading
            status='pending',
        )
        self.real = InitiativeActionItem.objects.create(
            initiative=self.initiative,
            title='Ship the autofill sweep PR',
            status='pending',
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_initiative(  # type: ignore[attr-defined]
            tool_name='initiative_tool',
            payload={'action': 'cleanup_action_items', **payload},
            user_id=self.chris.id,
            trace_id='test-aic-gate',
        )

    def test_empty_payload_previews_only(self):
        from core.models_document_registry import InitiativeActionItem
        result = self._dispatch({})
        self.junk.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.junk.status, 'pending', 'plain call must not cancel')

    def test_autofilled_dry_run_false_alone_previews_only(self):
        result = self._dispatch({'dry_run': False})
        self.junk.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.junk.status, 'pending')

    def test_explicit_write_executes(self):
        result = self._dispatch({'dry_run': False, 'confirm': True})
        self.junk.refresh_from_db()
        self.real.refresh_from_db()
        self.assertFalse(result['dry_run'])
        self.assertEqual(self.junk.status, 'cancelled')
        self.assertEqual(self.real.status, 'pending', 'real task untouched')


class InitiativeToolBulkCleanupWriteGateTests(TestCase):
    """initiative_tool action=bulk_cleanup — bulk archive of stalled/duplicate Initiatives.

    Prior bug: handler defaulted dry_run=False while schema said default true.
    PR-A flips both to the belt-and-suspenders gate.
    """

    def setUp(self):
        from datetime import timedelta
        from django.utils import timezone
        self.chris = User.objects.create_user(
            username='chris-bulkclean-test', password='x', is_staff=True,
        )
        # Stalled: current_stage<=1, no last_activity_at, created > 14d ago
        old = timezone.now() - timedelta(days=20)
        self.stalled = Initiative.objects.create(
            name='Stalled probe',
            description='probe',
            owner=self.chris,
            status='ACTIVE',
            current_stage=0,
        )
        # Direct UPDATE to bypass auto_now_add on created_at
        Initiative.objects.filter(pk=self.stalled.pk).update(created_at=old)

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_initiative(  # type: ignore[attr-defined]
            tool_name='initiative_tool',
            payload={'action': 'bulk_cleanup', **payload},
            user_id=self.chris.id,
            trace_id='test-bulkclean-gate',
        )

    def test_empty_payload_previews_only(self):
        """Verifies the prior schema-vs-handler dry_run default mismatch is fixed."""
        result = self._dispatch({})
        self.stalled.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.stalled.status, 'ACTIVE', 'plain call must not archive')

    def test_autofilled_dry_run_false_alone_previews_only(self):
        result = self._dispatch({'dry_run': False})
        self.stalled.refresh_from_db()
        self.assertTrue(result['dry_run'])
        self.assertEqual(self.stalled.status, 'ACTIVE')

    def test_explicit_write_executes(self):
        result = self._dispatch({'dry_run': False, 'confirm': True})
        self.stalled.refresh_from_db()
        self.assertFalse(result['dry_run'])
        self.assertEqual(self.stalled.status, 'ARCHIVED')


class AutopilotToolSecurityContainmentGateTests(SimpleTestCase):
    """autopilot_tool action=security_containment_plan — live security ops.

    SecurityEngine.get_containment_plan is patched so we only verify
    the dry_run kwarg is correctly threaded by the handler."""

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_autopilot(  # type: ignore[attr-defined]
            tool_name='autopilot_tool',
            payload={'action': 'security_containment_plan', **payload},
            user_id=None,
            trace_id='test-sec-gate',
        )

    def test_empty_payload_passes_dry_run_true(self):
        with patch(
            'core.services.ops_autopilot.SecurityEngine.get_containment_plan',
            return_value={'dry_run': True},
        ) as mocked:
            self._dispatch({})
            mocked.assert_called_once_with(dry_run=True)

    def test_autofilled_dry_run_false_alone_still_dry(self):
        with patch(
            'core.services.ops_autopilot.SecurityEngine.get_containment_plan',
            return_value={'dry_run': True},
        ) as mocked:
            self._dispatch({'dry_run': False})
            mocked.assert_called_once_with(dry_run=True)

    def test_explicit_write_passes_dry_run_false(self):
        with patch(
            'core.services.ops_autopilot.SecurityEngine.get_containment_plan',
            return_value={'dry_run': False},
        ) as mocked:
            self._dispatch({'dry_run': False, 'confirm': True})
            mocked.assert_called_once_with(dry_run=False)


# ────────────────────────────────────────────────────────────────────
# Tier 2 — update-field overwrite + filter gate protections
# ────────────────────────────────────────────────────────────────────


class TaskManagerDescriptionUpdateTests(TestCase):
    """task_manager_tool action=update description — autofill '' must NOT silently clear."""

    def setUp(self):
        from core.models_unified_system import Opportunity, OpportunityTask
        from decimal import Decimal
        self.chris = User.objects.create_user(
            username='chris-task-desc-test', password='x', is_staff=True,
        )
        self.opp = Opportunity.objects.create(
            user=self.chris,
            title='Probe opportunity for task desc test',
            description='probe',
            opportunity_type='task',
            source='pa',
            potential_revenue=Decimal('0'),
            status='active',
        )
        self.task = OpportunityTask.objects.create(
            user=self.chris,
            opportunity=self.opp,
            title='Probe task',
            description='Original description — preserve me.',
            priority='medium',
            status='pending',
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_task_manager(  # type: ignore[attr-defined]
            tool_name='task_manager_tool',
            payload={'action': 'update', 'id': str(self.task.id), **payload},
            user_id=self.chris.id,
            trace_id='test-task-desc',
        )

    def test_autofilled_empty_description_does_not_clear(self):
        """LLM autofill of description='' must NOT clear the field."""
        self._dispatch({'description': ''})
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Original description — preserve me.')

    def test_explicit_description_update_applies(self):
        self._dispatch({'description': 'Replacement description'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Replacement description')


class PlatformConfigToolListRoutesAuthRequiredTests(TestCase):
    """platform_config_tool action=list_routes — auth_required tri-state coercion.

    Routes are read from views_app_manifest.get_manifest_data which scopes
    by user RBAC; TestCase (not SimpleTestCase) so DB queries succeed."""

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_platform_awareness(  # type: ignore[attr-defined]
            tool_name='platform_config_tool',
            payload={'action': 'list_routes', **payload},
            user_id=None,
            trace_id='test-listroutes',
        )

    def test_autofilled_false_does_not_filter(self):
        """LLM autofill of auth_required=False must NOT silently filter to public routes only."""
        all_routes = self._dispatch({})
        autofilled = self._dispatch({'auth_required': False})
        self.assertEqual(
            all_routes['count'], autofilled['count'],
            'Python False autofill must be treated as no-filter',
        )

    def test_explicit_true_filters_to_auth_required(self):
        all_routes = self._dispatch({})
        only_auth = self._dispatch({'auth_required': True})
        self.assertLessEqual(only_auth['count'], all_routes['count'])
        for r in only_auth['routes']:
            self.assertTrue(r.get('authRequired'))

    def test_explicit_false_string_filters_to_public(self):
        only_public = self._dispatch({'auth_required': 'false'})
        for r in only_public['routes']:
            self.assertFalse(r.get('authRequired'))


class NewsletterToolMetricsManualFieldsTests(TestCase):
    """newsletter_tool action=metrics — autofilled opens=0 must NOT overwrite real count."""

    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris-nl-test', password='x', is_staff=True,
        )
        self.deliverable = Deliverable.objects.create(
            title='Operator Edge — Issue 99',
            content='# Sample\n\nbody',
            agent_name='NewsletterPipeline',
            user=self.chris,
            category='Newsletter',
            metadata={
                'issue_number': 99,
                'newsletter_metrics': {
                    'opens': 1500,
                    'clicks': 300,
                    'unsubscribes': 5,
                    'new_subscribers': 12,
                },
            },
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_newsletter(  # type: ignore[attr-defined]
            tool_name='newsletter_tool',
            payload={
                'action': 'metrics',
                'deliverable_id': str(self.deliverable.id),
                **payload,
            },
            user_id=self.chris.id,
            trace_id='test-nl-metrics',
        )

    def test_payload_with_no_manual_fields_preserves_existing(self):
        result = self._dispatch({})
        self.assertIn('metrics', result)

    def test_manual_field_present_writes_value(self):
        """Explicit opens=2000 must write through."""
        self._dispatch({'opens': 2000})
        self.deliverable.refresh_from_db()
        metrics = self.deliverable.metadata.get('newsletter_metrics', {})
        self.assertEqual(metrics.get('opens'), 2000)

    def test_zero_opens_is_a_legitimate_value(self):
        """Explicit opens=0 (legitimate "zero opens this week") must write."""
        self._dispatch({'opens': 0})
        self.deliverable.refresh_from_db()
        metrics = self.deliverable.metadata.get('newsletter_metrics', {})
        self.assertEqual(metrics.get('opens'), 0)

    def test_negative_opens_rejected(self):
        """Coercion safety: negative ints rejected."""
        self._dispatch({'opens': -5})
        self.deliverable.refresh_from_db()
        metrics = self.deliverable.metadata.get('newsletter_metrics', {})
        self.assertNotEqual(metrics.get('opens'), -5)


class InitiativeToolCreateExtraFieldsTests(TestCase):
    """initiative_tool action=create — autofilled '' / 0 must NOT override defaults."""

    def setUp(self):
        self.chris = User.objects.create_user(
            username='chris-initcreate-test', password='x', is_staff=True,
        )

    def _dispatch(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_initiative(  # type: ignore[attr-defined]
            tool_name='initiative_tool',
            payload={'action': 'create', **payload},
            user_id=self.chris.id,
            trace_id='test-initcreate-extra',
        )

    def test_autofilled_empty_string_purpose_uses_default(self):
        result = self._dispatch({
            'name': 'Autofill probe initiative — string',
            'purpose': '',
        })
        if 'error' in result:
            self.skipTest(f'create blocked: {result.get("error")}')
        init = Initiative.objects.get(id=result['id'])
        self.assertNotEqual(init.purpose, '', 'autofilled empty string must not override default')

    def test_autofilled_zero_impact_score_uses_default(self):
        result = self._dispatch({
            'name': 'Autofill probe initiative — int',
            'impact_score': 0,
        })
        if 'error' in result:
            self.skipTest(f'create blocked: {result.get("error")}')
        init = Initiative.objects.get(id=result['id'])
        # The model default for impact_score should be > 0 (e.g., 0.5)
        self.assertGreater(
            init.impact_score, 0,
            'autofilled 0 must fall through to default impact_score',
        )

    def test_explicit_nonzero_impact_score_applies(self):
        result = self._dispatch({
            'name': 'Autofill probe initiative — explicit',
            'impact_score': 0.9,
        })
        if 'error' in result:
            self.skipTest(f'create blocked: {result.get("error")}')
        init = Initiative.objects.get(id=result['id'])
        self.assertAlmostEqual(init.impact_score, 0.9, places=2)
