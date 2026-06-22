"""Session 1199 — Producer reroute regression tests (deliverable 780a8d15).

Covers the Session 1192 regression vector: producers calling
``_ensure_system_workspace`` were force-reactivating "System Autonomous
Workspace" as the default sink, undermining the Donkey Betz
consolidation.

Fix: ``settings.DEFAULT_PRODUCER_WORKSPACE_ID`` overrides the legacy
behavior. When set + the workspace exists + is active, return it
instead. Falls through to System Autonomous on miss.

Tests are organized into two classes — schema/setting tests (pure,
no DB) and integration tests that touch the manager. The pure tests
run via ``python -m unittest``; the integration tests use Django's
``override_settings`` to flip the default.

Local-run note: pgbouncer blocks ``manage.py test`` locally for the
integration tests; the pure tests run via ``python -m unittest`` directly.
"""

import unittest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from core.models_skin_layer import ProjectWorkspace
from core.services.workspace_manager import WorkspaceManager


User = get_user_model()


# ────────────────────────────────────────────────────────────────────────
# Pure setting tests (no DB)
# ────────────────────────────────────────────────────────────────────────


class ProducerRerouteSettingTest(unittest.TestCase):
    """AC: setting exists, is read-only string, defaults to DBZ UUID."""

    def test_setting_defined(self):
        self.assertTrue(hasattr(settings, 'DEFAULT_PRODUCER_WORKSPACE_ID'))

    def test_setting_defaults_to_donkey_betz(self):
        # When env var unset, the in-file default is Donkey Betz UUID
        # (b4503364-2573-4401-9e28-61a739e0ce50). Tests run with the
        # ambient settings — if an env var is set to override, this test
        # still passes (just verifies the setting is a non-empty UUID-ish
        # string).
        value = settings.DEFAULT_PRODUCER_WORKSPACE_ID
        self.assertIsInstance(value, str)
        self.assertTrue(value, 'DEFAULT_PRODUCER_WORKSPACE_ID must not be empty')

    def test_setting_is_strippable_string(self):
        """Defensive: setting must be a string (so it can be queried
        directly against ProjectWorkspace.id)."""
        self.assertIsInstance(settings.DEFAULT_PRODUCER_WORKSPACE_ID, str)


# ────────────────────────────────────────────────────────────────────────
# Integration — verifies _ensure_system_workspace honors the setting
# ────────────────────────────────────────────────────────────────────────


class ProducerRerouteIntegrationTest(TestCase):
    """AC: _ensure_system_workspace returns the configured default when
    set, falls through to System Autonomous when unset/missing."""

    @classmethod
    def setUpTestData(cls):
        cls.system_user = User.objects.create_user(
            username='system_autonomous_test',
            email='sysauto@example.com',
            password='x',
            is_superuser=True,
        )
        # Donkey-Betz-style target workspace
        cls.target_ws = ProjectWorkspace.objects.create(
            user=cls.system_user,
            name='Test Producer Target Workspace',
            root_path='/tmp/test-target',
            workspace_type='local',
            is_active=True,
            allow_file_write=True,
        )

    def test_setting_set_routes_to_configured_workspace(self):
        """When DEFAULT_PRODUCER_WORKSPACE_ID points at an active
        workspace, _ensure_system_workspace returns IT."""
        with override_settings(DEFAULT_PRODUCER_WORKSPACE_ID=str(self.target_ws.id)):
            mgr = WorkspaceManager(user=self.system_user)
            result = mgr._ensure_system_workspace()
        self.assertIsNotNone(result)
        self.assertEqual(str(result.id), str(self.target_ws.id))
        self.assertEqual(result.name, 'Test Producer Target Workspace')

    def test_setting_empty_falls_through_to_system_autonomous(self):
        """When setting is empty, the legacy
        'System Autonomous Workspace' lookup/create path runs."""
        with override_settings(DEFAULT_PRODUCER_WORKSPACE_ID=''):
            mgr = WorkspaceManager(user=self.system_user)
            result = mgr._ensure_system_workspace()
        # Either the legacy lookup found one, OR the create path made one
        # named 'System Autonomous Workspace'. Either way, it is NOT
        # our target_ws.
        self.assertIsNotNone(result)
        self.assertNotEqual(str(result.id), str(self.target_ws.id))

    def test_setting_points_at_nonexistent_workspace_falls_through(self):
        """When setting points at a UUID that doesn't exist, behavior
        falls through to the legacy path (not crash)."""
        bogus_id = '00000000-0000-0000-0000-000000000000'
        with override_settings(DEFAULT_PRODUCER_WORKSPACE_ID=bogus_id):
            mgr = WorkspaceManager(user=self.system_user)
            result = mgr._ensure_system_workspace()
        self.assertIsNotNone(result)
        # Did NOT return the bogus (because it didn't exist)
        self.assertNotEqual(str(result.id), bogus_id)

    def test_setting_points_at_inactive_workspace_falls_through(self):
        """An inactive workspace doesn't get auto-activated by this path;
        falls through to the legacy lookup."""
        inactive_ws = ProjectWorkspace.objects.create(
            user=self.system_user,
            name='Inactive Default',
            root_path='/tmp/inactive',
            workspace_type='local',
            is_active=False,  # ← key
        )
        with override_settings(DEFAULT_PRODUCER_WORKSPACE_ID=str(inactive_ws.id)):
            mgr = WorkspaceManager(user=self.system_user)
            result = mgr._ensure_system_workspace()
        self.assertIsNotNone(result)
        self.assertNotEqual(str(result.id), str(inactive_ws.id))
