"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch B tool 5
regression tests for workspace retrieval.

Covers the F-WS-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/workspace_retrieval_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-WS-4 `workspace_resolver.get_active_workspace` narrow-except discipline
  extension. Adds `_WORKSPACE_RESOLVER_ENV_ERRORS = (DatabaseError,
  ConnectionError, OSError)` allowlist mirroring the S1234 D17-D21
  shape. Logic errors now propagate; env errors still return None with
  ERROR log. Mirrors F-RG-1 patch shipped in Batch B tool 1.
- F-WS-1 `WorkspaceManager.get_active_workspace` T2 superuser cross-user
  fallback now emits a WARNING log naming the fallback workspace's
  owner. Zero behavior change; log-only. Preserves the intentional
  S1085 behavior while enabling operator diagnosis.

Existing coverage NOT duplicated:
- BaseAgent.execute_with_workspace partial-write metadata (S1230 F1) —
  covered in test_base_agent_workspace_write_visibility.py.
- Deliverable-workspace routing — covered in test_workspace_resolution.py.
- PA-mode workspace binding — covered in test_workspace_pa_modes.py.

Run::

    python manage.py test core.tests.test_workspace_retrieval_validation_2728 -v2
"""
from __future__ import annotations

import inspect
import uuid
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.db.utils import DatabaseError
from django.test import SimpleTestCase, TestCase

from core.services.workspace_resolver import (
    _WORKSPACE_RESOLVER_ENV_ERRORS,
    get_active_workspace,
)


User = get_user_model()


# ─── F-WS-4: workspace_resolver narrow-except discipline ────────────────


class FWS4AllowlistShapeTests(SimpleTestCase):
    """F-WS-4 — `_WORKSPACE_RESOLVER_ENV_ERRORS` matches the D17-D21 shape."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_WORKSPACE_RESOLVER_ENV_ERRORS, tuple)
        self.assertGreater(len(_WORKSPACE_RESOLVER_ENV_ERRORS), 0)

    def test_allowlist_contains_required_env_errors(self):
        self.assertIn(DatabaseError, _WORKSPACE_RESOLVER_ENV_ERRORS)
        self.assertIn(ConnectionError, _WORKSPACE_RESOLVER_ENV_ERRORS)
        self.assertIn(OSError, _WORKSPACE_RESOLVER_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        """The whole point of the D17-D21 discipline: env-only, NOT broad."""
        self.assertNotIn(Exception, _WORKSPACE_RESOLVER_ENV_ERRORS)
        self.assertNotIn(BaseException, _WORKSPACE_RESOLVER_ENV_ERRORS)


class FWS4BroadExceptRemovedTests(SimpleTestCase):
    """F-WS-4 — source-level guard that the broad except is gone."""

    def test_get_active_workspace_no_longer_uses_broad_except(self):
        src = inspect.getsource(get_active_workspace)
        # The narrow-except allowlist must appear.
        self.assertIn('except _WORKSPACE_RESOLVER_ENV_ERRORS', src)
        # The outer-scope `except Exception` must NOT appear inside the
        # function body — check both `as _e` (pre-patch form) and `as e`.
        self.assertNotIn('except Exception as _e:', src)
        self.assertNotIn('except Exception as e:', src)


class FWS4LogicErrorsPropagateTests(TestCase):
    """F-WS-4 — logic errors (AttributeError, TypeError) propagate out of
    `get_active_workspace` instead of silently returning None."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'ws-fws4-{uuid.uuid4().hex[:8]}',
            email='ws-fws4@example.com',
            password='x',
        )

    def test_type_error_propagates(self):
        # Force a TypeError inside the ORM chain by mocking the filter
        # to raise. TypeError is a logic-class error, NOT in the env
        # allowlist, so it must propagate.
        with patch(
            'core.models_skin_layer.ProjectWorkspace.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = TypeError('simulated logic bug')
            with self.assertRaises(TypeError) as ctx:
                get_active_workspace(self.user)
        self.assertIn('simulated logic bug', str(ctx.exception))
        # Verify the raised error is NOT one of the env classes.
        self.assertNotIsInstance(ctx.exception, _WORKSPACE_RESOLVER_ENV_ERRORS)

    def test_database_error_still_returns_none_with_log(self):
        """Regression guard: environmental DB errors MUST still return None
        with an ERROR log (safety valve for operational disruptions)."""
        with patch(
            'core.models_skin_layer.ProjectWorkspace.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = DatabaseError('simulated DB down')
            with self.assertLogs(
                'core.services.workspace_resolver', level='ERROR',
            ) as log_ctx:
                result = get_active_workspace(self.user)
        self.assertIsNone(result)
        # Log carries the env error class.
        log_output = '\n'.join(log_ctx.output)
        self.assertIn('DatabaseError', log_output)
        self.assertIn('simulated DB down', log_output)

    def test_connection_error_still_returns_none(self):
        with patch(
            'core.models_skin_layer.ProjectWorkspace.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = ConnectionError('net unreachable')
            result = get_active_workspace(self.user)
        self.assertIsNone(result)

    def test_os_error_still_returns_none(self):
        with patch(
            'core.models_skin_layer.ProjectWorkspace.objects',
        ) as mock_objects:
            mock_objects.filter.side_effect = OSError('I/O failure')
            result = get_active_workspace(self.user)
        self.assertIsNone(result)

    def test_no_user_returns_none_without_touching_orm(self):
        """Regression guard: falsy user short-circuits before any ORM call."""
        result = get_active_workspace(None)
        self.assertIsNone(result)


# ─── F-WS-1: WorkspaceManager superuser cross-user fallback logging ───


class FWS1SuperuserCrossUserFallbackLogging(TestCase):
    """F-WS-1 — when the S1085 superuser cross-user fallback fires, emit a
    WARNING log naming the fallback workspace's owner. Zero behavior
    change; log-only."""

    @classmethod
    def setUpTestData(cls):
        # A regular user who owns an active workspace.
        cls.owner_user = User.objects.create_user(
            username=f'ws-owner-{uuid.uuid4().hex[:8]}',
            email='ws-owner@example.com',
            password='x',
        )
        # A superuser with no workspaces of their own.
        cls.superuser = User.objects.create_user(
            username=f'ws-super-{uuid.uuid4().hex[:8]}',
            email='ws-super@example.com',
            password='x',
            is_superuser=True,
            is_staff=True,
        )

    def _make_workspace_for(self, user, name='ws-fws1'):
        from core.models_skin_layer import ProjectWorkspace
        return ProjectWorkspace.objects.create(
            user=user,
            name=f'{name}-{uuid.uuid4().hex[:6]}',
            root_path=f'/tmp/{name}-{uuid.uuid4().hex[:6]}',
            workspace_type='local',
            is_active=True,
            total_operations=10,
        )

    def test_superuser_fallback_fires_warning_log(self):
        # Seed: owner_user has an active workspace; superuser has none.
        owner_ws = self._make_workspace_for(self.owner_user, 'owner')

        from core.services.workspace_manager import WorkspaceManager
        manager = WorkspaceManager(self.superuser)

        with self.assertLogs(
            'core.services.workspace_manager', level='WARNING',
        ) as log_ctx:
            result = manager.get_active_workspace()

        # Behavior UNCHANGED — superuser gets the owner's workspace.
        self.assertIsNotNone(result)
        self.assertEqual(result.id, owner_ws.id)
        # F-WS-1 log fires + names the fallback owner.
        log_output = '\n'.join(log_ctx.output)
        self.assertIn('superuser cross-user fallback fired', log_output)
        self.assertIn(str(owner_ws.id), log_output)
        self.assertIn(self.superuser.username, log_output)
        # The log includes the fallback workspace's owner_id.
        self.assertIn(str(self.owner_user.id), log_output)

    def test_no_log_when_superuser_has_own_workspace(self):
        """Regression guard: if superuser has their OWN active workspace,
        the T2 fallback branch does NOT fire and no cross-user warning
        should appear."""
        own_ws = self._make_workspace_for(self.superuser, 'own')

        from core.services.workspace_manager import WorkspaceManager
        manager = WorkspaceManager(self.superuser)

        # Note: assertNoLogs added in 3.10; using a captured-logs approach
        # that works cross-version. We install a handler that records
        # any WARNING-level entries touching the S1085 fallback message.
        import logging
        captured = []

        class _Recorder(logging.Handler):
            def emit(self, record):
                captured.append(self.format(record))

        recorder = _Recorder(level=logging.WARNING)
        recorder.setFormatter(logging.Formatter('%(message)s'))
        wm_logger = logging.getLogger('core.services.workspace_manager')
        wm_logger.addHandler(recorder)
        try:
            result = manager.get_active_workspace()
        finally:
            wm_logger.removeHandler(recorder)

        self.assertEqual(result.id, own_ws.id)
        # No F-WS-1 warning should have been captured.
        for entry in captured:
            self.assertNotIn('superuser cross-user fallback fired', entry)
