"""
Session 792: Multi-Project Workspace Manager for SKIN Layer

Manage multiple project workspaces - local directories or GitHub repos.
Agents can work on any registered workspace.

Usage:
    # List all workspaces
    python manage.py manage_workspaces list

    # Add a local project
    python manage.py manage_workspaces add --name="my-saas" --path="/Users/dev/my-saas-app"

    # Add from GitHub (clones to workspace directory)
    python manage.py manage_workspaces add --name="cool-project" --github="https://github.com/user/repo.git"

    # Set active workspace
    python manage.py manage_workspaces activate --name="my-saas"

    # Remove a workspace
    python manage.py manage_workspaces remove --name="old-project"

    # Sync GitHub workspace (git pull)
    python manage.py manage_workspaces sync --name="cool-project"
"""

import os
import subprocess
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Manage multiple project workspaces for the SKIN layer'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')

        # List workspaces
        list_parser = subparsers.add_parser('list', help='List all workspaces')

        # Add workspace
        add_parser = subparsers.add_parser('add', help='Add a new workspace')
        add_parser.add_argument('--name', required=True, help='Workspace name')
        add_parser.add_argument('--path', help='Local path to project')
        add_parser.add_argument('--github', help='GitHub URL to clone')
        add_parser.add_argument('--description', default='', help='Project description')
        add_parser.add_argument('--tech-stack', help='Tech stack as JSON (e.g., \'{"backend": "django"}\')')
        add_parser.add_argument('--activate', action='store_true', help='Set as active workspace')

        # Activate workspace
        activate_parser = subparsers.add_parser('activate', help='Set active workspace')
        activate_parser.add_argument('--name', required=True, help='Workspace name to activate')

        # Remove workspace
        remove_parser = subparsers.add_parser('remove', help='Remove a workspace')
        remove_parser.add_argument('--name', required=True, help='Workspace name to remove')
        remove_parser.add_argument('--delete-files', action='store_true', help='Also delete the files')

        # Sync workspace (git pull)
        sync_parser = subparsers.add_parser('sync', help='Sync GitHub workspace (git pull)')
        sync_parser.add_argument('--name', required=True, help='Workspace name to sync')

        # Info about a workspace
        info_parser = subparsers.add_parser('info', help='Show workspace details')
        info_parser.add_argument('--name', required=True, help='Workspace name')

    def handle(self, *args, **options):
        action = options.get('action')

        if not action:
            self.stdout.write(self.style.ERROR('Please specify an action: list, add, activate, remove, sync, info'))
            return

        if action == 'list':
            self._list_workspaces()
        elif action == 'add':
            self._add_workspace(options)
        elif action == 'activate':
            self._activate_workspace(options['name'])
        elif action == 'remove':
            self._remove_workspace(options['name'], options.get('delete_files', False))
        elif action == 'sync':
            self._sync_workspace(options['name'])
        elif action == 'info':
            self._workspace_info(options['name'])

    def _list_workspaces(self):
        """List all registered workspaces."""
        from core.models_skin_layer import ProjectWorkspace

        workspaces = ProjectWorkspace.objects.all().order_by('-is_active', 'name')

        if not workspaces:
            self.stdout.write(self.style.WARNING('No workspaces registered.'))
            self.stdout.write('Add one with: python manage.py manage_workspaces add --name="project" --path="/path/to/project"')
            return

        self.stdout.write(self.style.NOTICE('\n📂 Registered Workspaces:\n'))
        self.stdout.write(f'{"Name":<25} {"Type":<12} {"Active":<8} {"Path/URL"}')
        self.stdout.write('-' * 80)

        for ws in workspaces:
            active_marker = '✅' if ws.is_active else ''
            path_display = ws.git_remote_url if ws.workspace_type == 'git_remote' else ws.root_path
            self.stdout.write(f'{ws.name:<25} {ws.workspace_type:<12} {active_marker:<8} {path_display}')

        self.stdout.write(f'\nTotal: {workspaces.count()} workspace(s)')

    def _add_workspace(self, options):
        """Add a new workspace - local or from GitHub."""
        from core.models_skin_layer import ProjectWorkspace
        import json

        name = options['name']
        local_path = options.get('path')
        github_url = options.get('github')
        description = options.get('description', '')
        activate = options.get('activate', False)

        # Parse tech stack if provided
        tech_stack = {}
        if options.get('tech_stack'):
            try:
                tech_stack = json.loads(options['tech_stack'])
            except json.JSONDecodeError:
                self.stdout.write(self.style.WARNING('Invalid tech_stack JSON, using empty dict'))

        # Check if workspace already exists
        if ProjectWorkspace.objects.filter(name=name).exists():
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" already exists. Use a different name or remove it first.'))
            return

        # Determine workspace type and path
        if github_url:
            workspace_type = 'git_remote'
            # Clone to a workspace directory
            base_workspace_dir = os.environ.get('WORKSPACE_BASE_DIR', '/app/workspaces')
            if not os.path.exists(base_workspace_dir):
                try:
                    os.makedirs(base_workspace_dir, exist_ok=True)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not create workspace dir: {e}'))
                    base_workspace_dir = '/tmp/workspaces'
                    os.makedirs(base_workspace_dir, exist_ok=True)

            root_path = os.path.join(base_workspace_dir, name)

            # Clone the repo
            self.stdout.write(f'Cloning {github_url} to {root_path}...')
            try:
                result = subprocess.run(
                    ['git', 'clone', github_url, root_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode != 0:
                    self.stdout.write(self.style.ERROR(f'Git clone failed: {result.stderr}'))
                    return
                self.stdout.write(self.style.SUCCESS('Clone successful!'))
            except subprocess.TimeoutExpired:
                self.stdout.write(self.style.ERROR('Git clone timed out'))
                return
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR('Git not found. Cannot clone repository.'))
                return

        elif local_path:
            workspace_type = 'local'
            root_path = os.path.abspath(local_path)

            # Verify path exists
            if not os.path.exists(root_path):
                self.stdout.write(self.style.ERROR(f'Path does not exist: {root_path}'))
                return

        else:
            self.stdout.write(self.style.ERROR('Must specify either --path (local) or --github (remote)'))
            return

        # Get or create system user
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@donkey-betz.com', 'is_active': True}
        )

        # Create the workspace
        workspace = ProjectWorkspace.objects.create(
            user=system_user,
            name=name,
            description=description or f'Workspace: {name}',
            workspace_type=workspace_type,
            root_path=root_path,
            git_remote_url=github_url or '',
            is_active=activate,
            tech_stack=tech_stack
        )

        self.stdout.write(self.style.SUCCESS(f'\n✅ Workspace "{name}" created!'))
        self.stdout.write(f'   ID: {workspace.id}')
        self.stdout.write(f'   Type: {workspace_type}')
        self.stdout.write(f'   Path: {root_path}')
        if github_url:
            self.stdout.write(f'   GitHub: {github_url}')
        self.stdout.write(f'   Active: {workspace.is_active}')

        if activate:
            self.stdout.write(self.style.SUCCESS(f'\n🎯 "{name}" is now the active workspace'))

    def _activate_workspace(self, name):
        """Set a workspace as active."""
        from core.models_skin_layer import ProjectWorkspace

        try:
            workspace = ProjectWorkspace.objects.get(name=name)
        except ProjectWorkspace.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" not found'))
            return

        # Deactivate all others
        ProjectWorkspace.objects.update(is_active=False)

        # Activate this one
        workspace.is_active = True
        workspace.save()

        self.stdout.write(self.style.SUCCESS(f'✅ Workspace "{name}" is now active'))
        self.stdout.write(f'   Path: {workspace.root_path}')

    def _remove_workspace(self, name, delete_files=False):
        """Remove a workspace."""
        from core.models_skin_layer import ProjectWorkspace
        import shutil

        try:
            workspace = ProjectWorkspace.objects.get(name=name)
        except ProjectWorkspace.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" not found'))
            return

        path = workspace.root_path

        # Delete from database
        workspace.delete()
        self.stdout.write(self.style.SUCCESS(f'✅ Workspace "{name}" removed from database'))

        # Optionally delete files
        if delete_files and os.path.exists(path):
            try:
                shutil.rmtree(path)
                self.stdout.write(self.style.SUCCESS(f'   Deleted files at: {path}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   Could not delete files: {e}'))

    def _sync_workspace(self, name):
        """Sync a GitHub workspace (git pull)."""
        from core.models_skin_layer import ProjectWorkspace

        try:
            workspace = ProjectWorkspace.objects.get(name=name)
        except ProjectWorkspace.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" not found'))
            return

        if not workspace.git_remote_url:
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" is not a GitHub workspace'))
            return

        if not os.path.exists(workspace.root_path):
            self.stdout.write(self.style.ERROR(f'Workspace path does not exist: {workspace.root_path}'))
            return

        self.stdout.write(f'Syncing {name}...')
        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=workspace.root_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f'✅ Sync successful'))
                self.stdout.write(result.stdout)
            else:
                self.stdout.write(self.style.ERROR(f'Sync failed: {result.stderr}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Sync error: {e}'))

    def _workspace_info(self, name):
        """Show detailed workspace info."""
        from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation
        from django.utils import timezone
        from datetime import timedelta

        try:
            workspace = ProjectWorkspace.objects.get(name=name)
        except ProjectWorkspace.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Workspace "{name}" not found'))
            return

        past_24h = timezone.now() - timedelta(hours=24)
        ops = WorkspaceOperation.objects.filter(workspace=workspace, created_at__gte=past_24h)
        total_ops = ops.count()
        successful_ops = ops.filter(success=True).count()
        success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 100

        self.stdout.write(self.style.NOTICE(f'\n📂 Workspace: {name}'))
        self.stdout.write(f'   ID: {workspace.id}')
        self.stdout.write(f'   Type: {workspace.workspace_type}')
        self.stdout.write(f'   Path: {workspace.root_path}')
        self.stdout.write(f'   Active: {"✅ Yes" if workspace.is_active else "No"}')
        self.stdout.write(f'   GitHub: {workspace.git_remote_url or "N/A"}')
        self.stdout.write(f'   Description: {workspace.description}')
        self.stdout.write(f'   Tech Stack: {workspace.tech_stack}')
        self.stdout.write(f'\n   Operations (24h): {total_ops}')
        self.stdout.write(f'   Success Rate: {success_rate:.1f}%')
        self.stdout.write(f'   Created: {workspace.created_at}')

        # Check if path exists
        if os.path.exists(workspace.root_path):
            self.stdout.write(self.style.SUCCESS(f'\n   ✅ Path exists and is accessible'))
        else:
            self.stdout.write(self.style.WARNING(f'\n   ⚠️ Path does not exist or is not accessible'))
