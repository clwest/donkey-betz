"""
S2977 follow-up regression: `work_tool.initiative_create` must populate
`owner_id` from the acting user, else the DB NOT NULL constraint on
`Initiative.owner` (I-0302 Phase 3 A1) fires an IntegrityError.

Root cause pre-fix: `InitiativeIntegrationService.get_or_create_initiative`
called `Initiative.objects.create(...)` without an owner, and the PA
handler (`td_handlers_content._handle_initiative` action='create')
never forwarded `user_id` down.

Fix: new `owner_user_id` kwarg on the service, resolved via `user_id` →
canonical primary superuser (mirrors migration 0381 backfill logic).

Run::

    python manage.py test core.tests.test_s2977_initiative_create_owner -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_document_registry import Initiative
from core.services.initiative_integration_service import (
    InitiativeIntegrationService,
)


User = get_user_model()


class GetOrCreateInitiativeOwnerTests(TestCase):
    """Direct tests of the service layer."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(
            username=f'user-a-{uuid.uuid4().hex[:8]}',
            email='a@example.com',
            password='x',
            is_superuser=False,
        )
        cls.superuser = User.objects.create_user(
            username=f'super-{uuid.uuid4().hex[:8]}',
            email='super@example.com',
            password='x',
            is_superuser=True,
        )

    def test_owner_user_id_explicit_wins(self):
        """When owner_user_id is passed, it's used verbatim."""
        svc = InitiativeIntegrationService()
        initiative, created = svc.get_or_create_initiative(
            topic=f'S2977 explicit owner {uuid.uuid4().hex[:6]}',
            description='explicit owner path',
            owner_user_id=self.user_a.pk,
            bypass_circuit_breaker=True,
        )
        self.assertTrue(created)
        self.assertEqual(initiative.owner_id, self.user_a.pk)

    def test_owner_falls_back_to_canonical_superuser(self):
        """When owner_user_id is None, falls back to earliest-pk superuser
        (matches migration 0381 backfill semantics for pre-prod single-tenant)."""
        svc = InitiativeIntegrationService()
        initiative, created = svc.get_or_create_initiative(
            topic=f'S2977 fallback owner {uuid.uuid4().hex[:6]}',
            description='fallback owner path',
            owner_user_id=None,
            bypass_circuit_breaker=True,
        )
        self.assertTrue(created)
        self.assertEqual(initiative.owner_id, self.superuser.pk)

    def test_hard_fail_when_no_owner_resolvable(self):
        """When neither explicit user_id nor a superuser exists, raise
        RuntimeError rather than crash on the DB NOT NULL constraint.

        Mocks the User manager rather than deleting superusers so this test
        stays hermetic — a cascade delete would try to touch tables from
        other apps that may not be in the test DB (e.g. learning_bridges).
        """
        from unittest.mock import patch

        svc = InitiativeIntegrationService()
        with patch('django.contrib.auth.get_user_model') as mock_get:
            mock_get.return_value.objects.filter.return_value.order_by.return_value.first.return_value = None
            with self.assertRaises(RuntimeError) as cm:
                svc.get_or_create_initiative(
                    topic=f'S2977 no owner {uuid.uuid4().hex[:6]}',
                    description='must raise, not IntegrityError',
                    owner_user_id=None,
                    bypass_circuit_breaker=True,
                )
        self.assertIn('NOT NULL', str(cm.exception))

    def test_existing_initiative_returns_without_owner_write(self):
        """get_or_create is idempotent: pre-existing rows return unchanged
        regardless of owner_user_id (existing owner preserved)."""
        svc = InitiativeIntegrationService()
        original, _ = svc.get_or_create_initiative(
            topic=f'S2977 idempotent {uuid.uuid4().hex[:6]}',
            owner_user_id=self.user_a.pk,
            bypass_circuit_breaker=True,
        )
        # Second call with a DIFFERENT owner_user_id must not mutate the
        # existing row.
        second, created = svc.get_or_create_initiative(
            topic=original.name,
            owner_user_id=self.superuser.pk,
            bypass_circuit_breaker=True,
        )
        self.assertFalse(created)
        self.assertEqual(second.pk, original.pk)
        second.refresh_from_db()
        self.assertEqual(second.owner_id, self.user_a.pk)


class WorkToolInitiativeCreateOwnerTests(TestCase):
    """End-to-end via the PA tool dispatcher path (work_tool.initiative_create
    → _handle_work → _handle_initiative → get_or_create_initiative)."""

    @classmethod
    def setUpTestData(cls):
        cls.acting_user = User.objects.create_user(
            username=f'acting-{uuid.uuid4().hex[:8]}',
            email='acting@example.com',
            password='x',
            is_superuser=True,
        )

    def test_pa_handler_forwards_user_id_to_service(self):
        """`_handle_initiative` action='create' must pass user_id through as
        owner_user_id so the created Initiative has owner_id set."""
        from core.services.tool_dispatcher import ToolDispatcher

        dispatcher = ToolDispatcher()
        result = dispatcher._handle_initiative(
            tool_name='initiative_tool',
            payload={
                'action': 'create',
                'name': f'S2977 PA create {uuid.uuid4().hex[:6]}',
                'description': 'created via PA handler test',
            },
            user_id=self.acting_user.pk,
            trace_id='s2977-test',
        )

        self.assertEqual(result.get('action'), 'create')
        self.assertTrue(result.get('created'))
        self.assertNotIn('error', result)

        # The created initiative must own owner_id from acting user.
        init = Initiative.objects.get(id=result['id'])
        self.assertEqual(init.owner_id, self.acting_user.pk)
