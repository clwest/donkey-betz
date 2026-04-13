"""Regression tests for autonomous-agent workspace resolution.

Covers the fix for the Ironwood Protocol misrouting incident (2026-04-13):
scheduled EditorAgent runs were inheriting Chris's user.is_active workspace
(Ironwood, a game project) as the default destination for content deliverables
because `deliverable_factory._get_active_workspace_id` did not filter on the
new `allow_autonomous_writes` flag.

These tests exercise the real `create_deliverable` factory against the real
`ProjectWorkspace` model — no stubs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.deliverable_factory import (
    _get_active_workspace_id,
    create_deliverable,
)

User = get_user_model()


class AutonomousWorkspaceResolutionTest(TestCase):
    """The factory must never silently write into non-content workspaces."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="chris_test",
            email="chris_test@example.com",
            password="x",
            is_superuser=True,
        )
        # A personal/game workspace marked active — this mirrors Chris with
        # Ironwood selected in the UI.
        self.game_ws = ProjectWorkspace.objects.create(
            user=self.user,
            name="Ironwood Protocol (test)",
            root_path="/tmp/ironwood",
            is_active=True,
            allow_autonomous_writes=False,
        )
        # A content-safe workspace, inactive in the UI but allowed for
        # autonomous writes.
        self.content_ws = ProjectWorkspace.objects.create(
            user=self.user,
            name="Operator Edge — AI Newsletter Studio (test)",
            root_path="/tmp/operator-edge",
            is_active=False,
            allow_autonomous_writes=True,
        )

    def test_get_active_workspace_id_skips_non_autonomous_workspace(self):
        """Even though game_ws is is_active, it should be filtered out."""
        resolved = _get_active_workspace_id(self.user)
        self.assertEqual(resolved, str(self.content_ws.id))
        self.assertNotEqual(resolved, str(self.game_ws.id))

    def test_create_deliverable_routes_to_content_workspace_by_default(self):
        """create_deliverable without explicit workspace_id must land in content_ws."""
        d = create_deliverable(
            title="Edited Content: autonomous test",
            content="body " * 30,
            agent_name="EditorAgent",
            user=self.user,
        )
        self.assertEqual(str(d.workspace_id), str(self.content_ws.id))
        self.assertNotEqual(str(d.workspace_id), str(self.game_ws.id))

    def test_explicit_workspace_id_wins_over_default(self):
        """Explicit workspace_id passed to create_deliverable is always honored."""
        d = create_deliverable(
            title="Edited Content: explicit target",
            content="body " * 30,
            agent_name="EditorAgent",
            user=self.user,
            workspace_id=str(self.game_ws.id),
        )
        # Explicit beats the filter — caller takes responsibility.
        self.assertEqual(str(d.workspace_id), str(self.game_ws.id))

    def test_no_eligible_workspace_creates_unsaved_deliverable(self):
        """If no content-safe workspace exists for the user, the factory
        must create the deliverable without a workspace (not silently pick
        the game workspace)."""
        # Flip the content workspace off.
        self.content_ws.allow_autonomous_writes = False
        self.content_ws.save(update_fields=["allow_autonomous_writes"])

        d = create_deliverable(
            title="Edited Content: no eligible target",
            content="body " * 30,
            agent_name="EditorAgent",
            user=self.user,
        )
        self.assertIsNone(d.workspace_id)
        # Ironwood must NOT have received this
        self.assertEqual(
            Deliverable.objects.filter(workspace_id=self.game_ws.id).count(),
            0,
        )
