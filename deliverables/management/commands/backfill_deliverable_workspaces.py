"""
Management command: backfill_deliverable_workspaces

Sets workspace = <Donkey Betz workspace> for all Deliverables belonging
to the target user where workspace IS NULL.

Idempotent -- running it multiple times is safe.

Usage::

    python manage.py backfill_deliverable_workspaces
    python manage.py backfill_deliverable_workspaces --username admin
    python manage.py backfill_deliverable_workspaces --dry-run
"""
import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

DONKEY_BETZ_WORKSPACE_NAME = 'Donkey Betz'


class Command(BaseCommand):
    help = (
        'Backfill Deliverables with workspace IS NULL, '
        'setting workspace to "Donkey Betz" for the target user.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default=None,
            help='Username to target (defaults to first superuser).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Show what would be updated without making changes.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        dry_run: bool = options['dry_run']

        # Resolve user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" not found.')
        else:
            user = User.objects.filter(is_superuser=True).order_by('pk').first()
            if user is None:
                user = User.objects.order_by('pk').first()
            if user is None:
                raise CommandError('No users found in the database.')

        self.stdout.write(f'Target user: {user.username} (pk={user.pk})')

        # Resolve workspace
        try:
            from workspaces.models import Workspace
        except ImportError as exc:
            raise CommandError(
                'workspaces app is not installed or Workspace model not found.'
            ) from exc

        workspace = (
            Workspace.objects.filter(
                name=DONKEY_BETZ_WORKSPACE_NAME, owner=user
            ).first()
            or Workspace.objects.filter(
                name=DONKEY_BETZ_WORKSPACE_NAME, members=user
            ).first()
            or Workspace.objects.filter(name=DONKEY_BETZ_WORKSPACE_NAME).first()
        )

        if workspace is None:
            raise CommandError(
                f'Workspace named "{DONKEY_BETZ_WORKSPACE_NAME}" not found.'
            )

        self.stdout.write(
            f'Target workspace: "{workspace.name}" (pk={workspace.pk})'
        )

        from deliverables.models import Deliverable

        null_qs = Deliverable.objects.filter(user=user, workspace__isnull=True)
        total_null = null_qs.count()
        total_all = Deliverable.objects.filter(user=user).count()

        self.stdout.write(
            f'Deliverables for user: {total_all} total, '
            f'{total_null} with workspace=NULL'
        )

        if total_null == 0:
            self.stdout.write(
                self.style.SUCCESS('Nothing to backfill -- already up to date.')
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] Would update {total_null} deliverable(s).'
                )
            )
            return

        updated = null_qs.update(workspace=workspace)
        logger.info(
            'backfill_deliverable_workspaces: updated=%d user=%s workspace=%s',
            updated,
            user.pk,
            workspace.pk,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Backfill complete: {updated} deliverable(s) updated '
                f'-> workspace "{workspace.name}".'
            )
        )
