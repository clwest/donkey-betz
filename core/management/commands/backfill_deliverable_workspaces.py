"""
Backfill workspace_id on Deliverables — sets NULL workspace deliverables
to the specified workspace (default: "Donkey Betz").

Idempotent — safe to run multiple times. Only updates rows where
workspace_id IS NULL.

Usage:
    python manage.py backfill_deliverable_workspaces --dry-run
    python manage.py backfill_deliverable_workspaces
    python manage.py backfill_deliverable_workspaces --workspace "Donkey Betz"
    python manage.py backfill_deliverable_workspaces --username Donkeyking
    python manage.py backfill_deliverable_workspaces --include-archived
"""

import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace

logger = logging.getLogger(__name__)

DEFAULT_WORKSPACE_NAME = 'Donkey Betz'


class Command(BaseCommand):
    help = 'Backfill workspace_id on Deliverables where it is NULL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--workspace',
            default=DEFAULT_WORKSPACE_NAME,
            help=f'Workspace name to assign (default: "{DEFAULT_WORKSPACE_NAME}")',
        )
        parser.add_argument(
            '--username',
            default=None,
            help='Only backfill deliverables owned by this user (default: all users)',
        )
        parser.add_argument(
            '--include-archived',
            action='store_true',
            default=False,
            help='Also backfill archived deliverables (default: skip archived)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        workspace_name = options['workspace']
        username = options['username']
        include_archived = options['include_archived']
        dry_run = options['dry_run']

        # Resolve workspace
        workspace = ProjectWorkspace.objects.filter(name=workspace_name).first()
        if not workspace:
            available = list(
                ProjectWorkspace.objects.values_list('name', flat=True)[:20]
            )
            raise CommandError(
                f'Workspace "{workspace_name}" not found. '
                f'Available: {available}'
            )
        self.stdout.write(f'Target workspace: "{workspace.name}" (id={workspace.id})')

        # Build queryset
        qs = Deliverable.objects.filter(workspace__isnull=True)

        if not include_archived:
            qs = qs.exclude(status='archived')

        if username:
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" not found')
            qs = qs.filter(user=user)
            self.stdout.write(f'Filtering to user: {user.username} (id={user.id})')

        count = qs.count()
        total = Deliverable.objects.count()
        self.stdout.write(
            f'Found {count} deliverables with workspace=NULL '
            f'(out of {total} total)'
        )

        if count == 0:
            self.stdout.write(self.style.SUCCESS('Nothing to backfill.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[DRY RUN] Would update {count} deliverable(s) '
                f'-> workspace "{workspace.name}"'
            ))
            # Show a sample
            sample = qs.order_by('-created_at')[:5]
            for d in sample:
                self.stdout.write(
                    f'  {d.id} | {d.status} | {d.title[:60]}'
                )
            if count > 5:
                self.stdout.write(f'  ... and {count - 5} more')
            return

        updated = qs.update(workspace=workspace)
        logger.info(
            'backfill_deliverable_workspaces: updated=%d workspace=%s',
            updated, workspace.id,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Backfill complete: {updated} deliverable(s) '
            f'-> workspace "{workspace.name}"'
        ))

        # Verify
        remaining = Deliverable.objects.filter(workspace__isnull=True)
        if not include_archived:
            remaining = remaining.exclude(status='archived')
        self.stdout.write(
            f'Remaining with workspace=NULL: {remaining.count()}'
        )
