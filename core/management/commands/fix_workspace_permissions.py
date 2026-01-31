"""
Management command to fix workspace permissions.

Session 889: Fix "System Autonomous Workspace" which has root_path=/app/workspace
that is not writable on Railway, causing 80% of workspace operations to fail.

Usage:
    python manage.py fix_workspace_permissions --list
    python manage.py fix_workspace_permissions --fix
"""

from django.core.management.base import BaseCommand
from core.models_skin_layer import ProjectWorkspace


class Command(BaseCommand):
    help = 'Fix workspace permissions and paths'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all workspaces'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix problematic workspaces'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_workspaces()
        elif options['fix']:
            self.fix_workspaces()
        else:
            self.stdout.write("Use --list to see workspaces or --fix to fix them")

    def list_workspaces(self):
        workspaces = ProjectWorkspace.objects.all()
        self.stdout.write(f"\nFound {workspaces.count()} workspaces:\n")

        for ws in workspaces:
            status = "OK" if ws.is_active and '/tmp/' in str(ws.root_path) else "ISSUE"
            self.stdout.write(f"  [{status}] {ws.name}")
            self.stdout.write(f"       ID: {ws.id}")
            self.stdout.write(f"       Path: {ws.root_path}")
            self.stdout.write(f"       Active: {ws.is_active}")
            self.stdout.write(f"       Allow Write: {ws.allow_file_write}")
            self.stdout.write("")

    def fix_workspaces(self):
        # Find workspaces with problematic paths
        bad_workspaces = ProjectWorkspace.objects.filter(
            root_path__startswith='/app/workspace'
        )

        fixed = 0
        for ws in bad_workspaces:
            self.stdout.write(f"\nFixing: {ws.name} ({ws.id})")
            self.stdout.write(f"  Old path: {ws.root_path}")

            # Disable the workspace and file writes
            ws.is_active = False
            ws.allow_file_write = False
            ws.save(update_fields=['is_active', 'allow_file_write'])

            self.stdout.write(f"  -> Disabled (is_active=False, allow_file_write=False)")
            fixed += 1

        if fixed > 0:
            self.stdout.write(self.style.SUCCESS(f"\nFixed {fixed} workspace(s)"))
        else:
            self.stdout.write("No workspaces needed fixing")
