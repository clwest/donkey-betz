"""
Session 906: Trigger Stage 2 (Prototype Plan) document generation for initiatives.

Usage:
    # Dry run - show what would be triggered
    python manage.py trigger_stage2_generation

    # Actually trigger generation (limit 5)
    python manage.py trigger_stage2_generation --run --limit=5

    # Generate for all initiatives at Stage 2
    python manage.py trigger_stage2_generation --run --limit=100
"""

from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Trigger Stage 2 (Prototype Plan) document generation for initiatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--run',
            action='store_true',
            help='Actually trigger generation (default is dry run)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Maximum number of initiatives to process (default: 5)',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage
        from core.tasks import generate_initiative_stage_document

        run = options['run']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(
            f"{'TRIGGERING' if run else 'DRY RUN'}: Stage 2 document generation (limit: {limit})"
        ))

        # Get initiatives at Stage 2
        initiatives_at_stage2 = Initiative.objects.filter(current_stage=2).order_by('-created_at')
        self.stdout.write(f"Total initiatives at Stage 2: {initiatives_at_stage2.count()}")

        # Find those without Stage 2 documents
        needing_docs = []
        for init in initiatives_at_stage2:
            try:
                stage2 = InitiativeStage.objects.get(initiative=init, stage=2)
                if not stage2.document:
                    needing_docs.append(init)
            except InitiativeStage.DoesNotExist:
                needing_docs.append(init)

            if len(needing_docs) >= limit:
                break

        self.stdout.write(f"Found {len(needing_docs)} initiatives needing Stage 2 documents")

        triggered_count = 0
        error_count = 0

        for init in needing_docs:
            if run:
                try:
                    task = generate_initiative_stage_document.delay(str(init.id), 2)
                    triggered_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"TRIGGERED: {init.name[:50]} | Task: {task.id}"
                    ))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f"ERROR: {init.name[:50]} - {e}"
                    ))
            else:
                self.stdout.write(
                    f"WOULD TRIGGER: {init.name[:50]}"
                )
                triggered_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n{'TRIGGERED' if run else 'WOULD TRIGGER'}: {triggered_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"ERRORS: {error_count}"))
