"""
Session 915: Backfill Stage Documents for Initiatives

This command finds initiatives that are missing stage documents and triggers
document generation for them.

Usage:
    # Dry run - see what would be generated
    python manage.py backfill_stage_documents --dry-run

    # Generate Stage 1 documents for initiatives missing them
    python manage.py backfill_stage_documents --stage=1

    # Limit to specific number
    python manage.py backfill_stage_documents --stage=1 --limit=10
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Backfill missing stage documents for initiatives"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without actually generating',
        )
        parser.add_argument(
            '--stage',
            type=int,
            default=1,
            help='Stage number to backfill (default: 1)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of initiatives to process (default: 50)',
        )
        parser.add_argument(
            '--initiative-id',
            type=str,
            help='Process a specific initiative by UUID',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage
        from core.tasks import generate_initiative_stage_document

        dry_run = options['dry_run']
        stage_num = options['stage']
        limit = options['limit']
        initiative_id = options.get('initiative_id')

        self.stdout.write(self.style.WARNING(
            f"\n{'=' * 60}\n"
            f"Session 915: Backfill Stage {stage_num} Documents\n"
            f"{'=' * 60}\n"
        ))

        if initiative_id:
            # Process specific initiative
            try:
                initiative = Initiative.objects.get(id=initiative_id)
                initiatives = [initiative]
                self.stdout.write(f"Processing specific initiative: {initiative.name[:50]}...")
            except Initiative.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Initiative {initiative_id} not found"))
                return
        else:
            # Find initiatives with missing stage documents
            # Get initiatives where the stage exists but has no document
            initiatives_with_missing_docs = []

            # Get all initiatives
            all_initiatives = Initiative.objects.filter(
                current_stage__gte=stage_num
            ).order_by('-created_at')[:limit * 2]  # Get extra to filter

            for initiative in all_initiatives:
                stage = InitiativeStage.objects.filter(
                    initiative=initiative,
                    stage=stage_num
                ).first()

                if stage and not stage.document:
                    initiatives_with_missing_docs.append(initiative)

                if len(initiatives_with_missing_docs) >= limit:
                    break

            initiatives = initiatives_with_missing_docs

        self.stdout.write(f"Found {len(initiatives)} initiatives missing Stage {stage_num} documents\n")

        if not initiatives:
            self.stdout.write(self.style.SUCCESS("No initiatives need backfilling!"))
            return

        triggered = 0
        errors = 0

        for initiative in initiatives:
            stage = InitiativeStage.objects.filter(
                initiative=initiative,
                stage=stage_num
            ).first()

            if not stage:
                self.stdout.write(f"  ⚠️  {initiative.name[:40]}: No Stage {stage_num} record")
                continue

            if stage.document:
                self.stdout.write(f"  ✅ {initiative.name[:40]}: Already has document")
                continue

            if dry_run:
                self.stdout.write(f"  📝 Would generate: {initiative.name[:50]}...")
                triggered += 1
            else:
                try:
                    task = generate_initiative_stage_document.delay(
                        str(initiative.id),
                        stage_num
                    )
                    self.stdout.write(f"  🚀 Triggered: {initiative.name[:40]}... (task {task.id})")
                    triggered += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ❌ Error: {initiative.name[:40]}: {e}"))
                    errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n{'=' * 60}\n"
            f"Summary:\n"
            f"  {'Would trigger' if dry_run else 'Triggered'}: {triggered}\n"
            f"  Errors: {errors}\n"
            f"{'=' * 60}\n"
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nThis was a dry run. Run without --dry-run to actually generate documents."
            ))
