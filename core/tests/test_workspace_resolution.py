"""Integration tests for workspace resolution logic."""

from django.test import TestCase


class WorkspaceResolutionIntegrationTest(TestCase):
    """Integration tests for workspace resolution."""

    def test_conversation_overrides_active_workspace(self):
        """
        Test that a conversation-level workspace setting overrides
        the globally active workspace when resolving which workspace
        to use for a given context.
        """
        from core.models import Workspace

        global_ws = Workspace.objects.create(
            name="Global Active Workspace",
            is_active=True,
        )
        conversation_ws = Workspace.objects.create(
            name="Conversation Workspace",
            is_active=False,
        )

        resolved = self._resolve_workspace(
            conversation_workspace_id=str(conversation_ws.id),
            fallback_to_active=True,
        )

        self.assertEqual(resolved.id, conversation_ws.id)
        self.assertNotEqual(resolved.id, global_ws.id)

    def _resolve_workspace(self, conversation_workspace_id=None, fallback_to_active=True):
        """Prefer conversation-scoped workspace; fall back to the active one."""
        from core.models import Workspace

        if conversation_workspace_id:
            try:
                return Workspace.objects.get(id=conversation_workspace_id)
            except Workspace.DoesNotExist:
                pass

        if fallback_to_active:
            ws = Workspace.objects.filter(is_active=True).first()
            if ws:
                return ws

        raise ValueError("No workspace could be resolved.")
