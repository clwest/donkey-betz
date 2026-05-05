"""Regression tests for Rigby workspace mode and workspace tool safety."""

import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_assistant_profile import AssistantProfile
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher
from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint

User = get_user_model()


class WorkspaceModeResolutionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='rigby-mode-test',
            email='rigby-mode-test@example.com',
            password='x',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='Mode Test Workspace',
            root_path='/tmp/mode-test-workspace',
            is_active=True,
        )

    def _make_pa(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        pa.user = self.user
        return pa

    def test_profile_workspace_enables_workspace_mode(self):
        AssistantProfile.objects.create(user=self.user, workspace=self.workspace)

        scope = async_to_sync(self._make_pa()._resolve_workspace_scope)({})

        self.assertEqual(scope['assistant_mode'], 'workspace')
        self.assertEqual(scope['workspace_source'], 'profile')
        self.assertEqual(scope['workspace_id'], str(self.workspace.id))

    def test_request_workspace_id_overrides_profile_scope(self):
        other_workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='Requested Workspace',
            root_path='/tmp/requested-workspace',
            is_active=False,
        )
        AssistantProfile.objects.create(user=self.user, workspace=self.workspace)

        scope = async_to_sync(self._make_pa()._resolve_workspace_scope)({
            'workspace_id': str(other_workspace.id),
        })

        self.assertEqual(scope['assistant_mode'], 'workspace')
        self.assertEqual(scope['workspace_source'], 'request')
        self.assertEqual(scope['workspace_id'], str(other_workspace.id))

    def test_global_mode_without_workspace_scope(self):
        global_user = User.objects.create_user(
            username='rigby-global-test',
            email='rigby-global-test@example.com',
            password='x',
        )
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        pa.user = global_user

        scope = async_to_sync(pa._resolve_workspace_scope)({})

        self.assertEqual(scope['assistant_mode'], 'global')
        self.assertIsNone(scope['workspace_id'])
        self.assertIsNone(scope['workspace_source'])


class WorkspaceToolActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='workspace-tool-test',
            email='workspace-tool-test@example.com',
            password='x',
        )
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)

        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='Tool Workspace',
            root_path=self.tempdir.name,
            is_active=True,
        )

        self.dispatcher = ToolDispatcher()
        self.handler = self.dispatcher._tool_handlers['workspace_tool']

    def test_read_action_reads_inside_root_and_blocks_escape(self):
        inside = Path(self.tempdir.name) / 'notes.txt'
        inside.write_text('hello workspace', encoding='utf-8')

        ok = self.handler(
            'workspace_tool',
            {'action': 'read', 'path': 'notes.txt'},
            self.user.id,
            'read-ok',
        )
        self.assertTrue(ok['success'])
        self.assertEqual(ok['content'], 'hello workspace')
        self.assertEqual(ok['workspace']['id'], str(self.workspace.id))

        bad = self.handler(
            'workspace_tool',
            {'action': 'read', 'path': '../escape.txt'},
            self.user.id,
            'read-bad',
        )
        self.assertFalse(bad['success'])
        self.assertIn('Path escapes workspace root', bad['error'])

    def test_write_action_blocks_path_escape(self):
        outside_path = Path(self.tempdir.name).parent / f'escape-{self.workspace.id}.txt'
        if outside_path.exists():
            outside_path.unlink()

        result = self.handler(
            'workspace_tool',
            {
                'action': 'write',
                'path': f'../{outside_path.name}',
                'content': 'should not write',
            },
            self.user.id,
            'write-bad',
        )

        self.assertFalse(result['success'])
        self.assertIn('Path escapes workspace root', result['error'])
        self.assertFalse(outside_path.exists())

    @patch('core.services.workspace_manager.get_workspace_manager')
    def test_git_status_action_uses_manager(self, mock_get_workspace_manager):
        fake_manager = SimpleNamespace(
            get_active_workspace=lambda: self.workspace,
            git_status=lambda workspace: {
                'branch': 'main',
                'dirty': False,
                'ahead': 0,
                'behind': 0,
            },
        )
        mock_get_workspace_manager.return_value = fake_manager

        result = self.handler(
            'workspace_tool',
            {'action': 'git_status'},
            self.user.id,
            'git-status',
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['workspace']['id'], str(self.workspace.id))
        self.assertEqual(result['git_status']['branch'], 'main')
