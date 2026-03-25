from io import StringIO
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


def _make_workspace(pk='ws-1', name='Donkey Betz', owner=None):
    ws = MagicMock()
    ws.pk = pk
    ws.id = pk
    ws.name = name
    ws.owner = owner
    return ws


class DeliverableWorkspaceStampTest(TestCase):
    """Verify workspace_id is persisted when provided on creation."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secret')

    def test_workspace_id_saved_when_provided(self):
        """
        perform_create should call serializer.save(workspace=<ws>) when
        a valid workspace_id is supplied in request.data.
        """
        from deliverables.views import DeliverableViewSet
        from deliverables.serializers import DeliverableSerializer

        ws = _make_workspace(pk='ws-42', name='Donkey Betz', owner=self.user)

        view = DeliverableViewSet()
        view.request = MagicMock()
        view.request.user = self.user
        view.request.data = {'title': 'Test deliverable', 'workspace_id': 'ws-42'}
        view.request.META = {}

        serializer = MagicMock(spec=DeliverableSerializer)
        serializer.instance = MagicMock(pk=99)

        with patch('deliverables.views.DeliverableViewSet._validate_workspace_access', return_value=True):
            with patch('deliverables.views.Workspace') as MockWorkspace:
                MockWorkspace.objects.get.return_value = ws
                view.perform_create(serializer)

        serializer.save.assert_called_once_with(user=self.user, workspace=ws)

    def test_no_workspace_id_saves_with_none(self):
        """
        When no workspace_id is given, serializer.save is called with workspace=None.
        """
        from deliverables.views import DeliverableViewSet
        from deliverables.serializers import DeliverableSerializer

        view = DeliverableViewSet()
        view.request = MagicMock()
        view.request.user = self.user
        view.request.data = {'title': 'No workspace'}
        view.request.META = {}

        serializer = MagicMock(spec=DeliverableSerializer)
        serializer.instance = MagicMock(pk=100)

        view.perform_create(serializer)

        serializer.save.assert_called_once_with(user=self.user, workspace=None)

    def test_invalid_workspace_raises_permission_denied(self):
        """perform_create raises PermissionDenied for inaccessible workspace."""
        from rest_framework.exceptions import PermissionDenied
        from deliverables.views import DeliverableViewSet
        from deliverables.serializers import DeliverableSerializer

        view = DeliverableViewSet()
        view.request = MagicMock()
        view.request.user = self.user
        view.request.data = {'title': 'Bad workspace', 'workspace_id': 'ws-forbidden'}
        view.request.META = {}

        serializer = MagicMock(spec=DeliverableSerializer)

        with patch('deliverables.views.DeliverableViewSet._validate_workspace_access', return_value=False):
            with self.assertRaises(PermissionDenied):
                view.perform_create(serializer)


class BackfillCommandTest(TestCase):
    """Tests for backfill_deliverable_workspaces management command."""

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin', password='admin', email='admin@example.com'
        )

    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Workspace')
    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Deliverable')
    def test_backfill_updates_null_workspace_deliverables(self, MockDeliverable, MockWorkspace):
        """Running the command updates NULL-workspace deliverables."""
        from django.core.management import call_command

        ws = _make_workspace(pk='ws-donkey', name='Donkey Betz', owner=self.user)

        # Workspace lookup chain
        MockWorkspace.objects.filter.return_value.first.return_value = ws

        null_qs = MagicMock()
        null_qs.count.return_value = 2
        null_qs.update.return_value = 2

        all_qs = MagicMock()
        all_qs.count.return_value = 3

        def _filter_side_effect(**kwargs):
            if kwargs.get('workspace__isnull'):
                return null_qs
            return all_qs

        MockDeliverable.objects.filter.side_effect = _filter_side_effect

        out = StringIO()
        call_command('backfill_deliverable_workspaces', username='admin', stdout=out)

        output = out.getvalue()
        self.assertIn('2', output)
        null_qs.update.assert_called_once_with(workspace=ws)

    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Workspace')
    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Deliverable')
    def test_backfill_dry_run_does_not_update(self, MockDeliverable, MockWorkspace):
        """--dry-run must not call .update()."""
        from django.core.management import call_command

        ws = _make_workspace(pk='ws-donkey', name='Donkey Betz', owner=self.user)
        MockWorkspace.objects.filter.return_value.first.return_value = ws

        null_qs = MagicMock()
        null_qs.count.return_value = 5

        all_qs = MagicMock()
        all_qs.count.return_value = 5

        def _filter_side_effect(**kwargs):
            if kwargs.get('workspace__isnull'):
                return null_qs
            return all_qs

        MockDeliverable.objects.filter.side_effect = _filter_side_effect

        out = StringIO()
        call_command('backfill_deliverable_workspaces', username='admin', dry_run=True, stdout=out)

        null_qs.update.assert_not_called()
        self.assertIn('DRY RUN', out.getvalue())

    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Workspace')
    @patch('deliverables.management.commands.backfill_deliverable_workspaces.Deliverable')
    def test_backfill_idempotent_when_nothing_to_update(self, MockDeliverable, MockWorkspace):
        """Command exits cleanly when there are no NULL-workspace deliverables."""
        from django.core.management import call_command

        ws = _make_workspace(pk='ws-donkey', name='Donkey Betz', owner=self.user)
        MockWorkspace.objects.filter.return_value.first.return_value = ws

        null_qs = MagicMock()
        null_qs.count.return_value = 0

        all_qs = MagicMock()
        all_qs.count.return_value = 3

        def _filter_side_effect(**kwargs):
            if kwargs.get('workspace__isnull'):
                return null_qs
            return all_qs

        MockDeliverable.objects.filter.side_effect = _filter_side_effect

        out = StringIO()
        call_command('backfill_deliverable_workspaces', username='admin', stdout=out)

        null_qs.update.assert_not_called()
        self.assertIn('already up to date', out.getvalue())
