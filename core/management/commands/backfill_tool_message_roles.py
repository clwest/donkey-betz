"""Management command: backfill role='tool' for code-worker/claude-code messages."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backfill role='tool' for PAConversationMessage records from code-worker/claude-code."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Count records that would be updated without applying changes.',
        )

    def handle(self, *args, **options):
        try:
            from core.models import PAConversationMessage
        except ImportError:
            self.stderr.write('PAConversationMessage model not found.')
            return

        qs = PAConversationMessage.objects.filter(
            source__in=['code-worker', 'claude-code'],
        ).exclude(role='tool')

        count = qs.count()
        if options['dry_run']:
            self.stdout.write(f'DRY RUN: {count} records would be updated.')
            return

        updated = qs.update(role='tool')
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} records to role='tool'."))
