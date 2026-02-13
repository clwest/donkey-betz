"""
Session 997B: Backfill owner_agent for existing initiatives using PROGRAM_OWNER_MAP.
"""
from django.core.management.base import BaseCommand

from core.services.initiative_integration_service import (
    InitiativeIntegrationService,
    PROGRAM_OWNER_MAP,
)


class Command(BaseCommand):
    help = 'Backfill owner_agent on unowned initiatives using PROGRAM_OWNER_MAP'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would change without saving')

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        dry_run = options['dry_run']
        service = InitiativeIntegrationService()

        unowned = Initiative.objects.filter(
            owner__isnull=True,
            owner_agent__in=['', None],
        ).exclude(status='ARCHIVED')

        total = unowned.count()
        self.stdout.write(f"Found {total} unowned initiatives (excluding archived)")
        self.stdout.write(f"PROGRAM_OWNER_MAP: {PROGRAM_OWNER_MAP}\n")

        assigned = 0
        skipped = 0

        for init in unowned.iterator():
            old_agent = init.owner_agent or ''
            if not dry_run:
                service._auto_assign_owner(init)
                init.refresh_from_db()

            new_agent = init.owner_agent or ''

            if dry_run:
                # Simulate the logic
                program = getattr(init, 'program', '') or ''
                created_by = getattr(init, 'created_by', '') or ''
                if program and program != 'uncategorized' and program in PROGRAM_OWNER_MAP:
                    new_agent = PROGRAM_OWNER_MAP[program]
                elif created_by.lower() not in {'system', 'pa', 'human', 'admin', ''} and not created_by.startswith('HiveMind:'):
                    new_agent = created_by

            if new_agent and new_agent != old_agent:
                assigned += 1
                self.stdout.write(
                    f"  {'[DRY] ' if dry_run else ''}'{init.name[:60]}' "
                    f"(program={init.program}) -> owner_agent={new_agent}"
                )
            else:
                skipped += 1

        prefix = '[DRY RUN] ' if dry_run else ''
        self.stdout.write(self.style.SUCCESS(
            f"\n{prefix}Done: {assigned} assigned, {skipped} skipped (no matching rule)"
        ))
