"""
Fix Initiative Stages - Backfill Missing Stage Approvals
=========================================================

Session 884: Fixes initiatives where current_stage > 1 but prior stages
are still PENDING. This happens when tasks complete out of order or
when initiatives were created with stages that skip earlier ones.

Usage:
    # Preview what would be fixed
    python manage.py fix_initiative_stages --dry-run

    # Fix all initiatives with inconsistent stages
    python manage.py fix_initiative_stages

    # Fix a specific initiative
    python manage.py fix_initiative_stages --id=<uuid>
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fix initiatives with inconsistent stage completion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview without making changes'
        )
        parser.add_argument(
            '--id',
            type=str,
            default=None,
            help='Fix a specific initiative by ID'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage

        dry_run = options['dry_run']
        specific_id = options['id']

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("FIX INITIATIVE STAGES - Session 884"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - No changes will be made\n"))

        # Find initiatives with inconsistent stages
        if specific_id:
            initiatives = Initiative.objects.filter(id=specific_id)
        else:
            # Find initiatives where current_stage > 1 (potentially have skipped stages)
            initiatives = Initiative.objects.filter(
                current_stage__gt=1,
                status='ACTIVE'
            ).prefetch_related('stages')

        self.stdout.write(f"\nFound {initiatives.count()} initiatives to check\n")

        fixed_count = 0
        stages_backfilled = 0

        for initiative in initiatives:
            current_stage = initiative.current_stage
            existing_stages = {s.stage: s for s in initiative.stages.all()}

            issues = []
            fixes_needed = []

            # Check all stages before current_stage
            for stage_num in range(1, current_stage):
                stage = existing_stages.get(stage_num)

                if not stage:
                    issues.append(f"Stage {stage_num}: MISSING")
                    fixes_needed.append(('create', stage_num))
                elif stage.status in ['PENDING', 'DRAFT', 'IN_REVIEW']:
                    issues.append(f"Stage {stage_num}: {stage.status} (should be APPROVED)")
                    fixes_needed.append(('approve', stage_num, stage))

            if not fixes_needed:
                continue

            self.stdout.write(f"\n{'─' * 50}")
            self.stdout.write(f"Initiative: {initiative.name[:60]}...")
            self.stdout.write(f"  ID: {initiative.id}")
            self.stdout.write(f"  Current Stage: {current_stage}")
            self.stdout.write(f"  Issues: {len(issues)}")
            for issue in issues:
                self.stdout.write(f"    - {issue}")

            if dry_run:
                self.stdout.write(self.style.WARNING(f"  [DRY RUN] Would fix {len(fixes_needed)} stages"))
                fixed_count += 1
                stages_backfilled += len(fixes_needed)
                continue

            # Apply fixes
            # Session 916: Respect invariants - only approve stages with documents
            for fix in fixes_needed:
                if fix[0] == 'create':
                    stage_num = fix[1]
                    # Session 916: Create in DRAFT, not APPROVED (no document = no approval)
                    InitiativeStage.objects.create(
                        initiative=initiative,
                        stage=stage_num,
                        status='DRAFT',  # Changed from APPROVED - needs document first
                        notes=f'Created in DRAFT by fix_initiative_stages at {timezone.now().isoformat()}',
                    )
                    self.stdout.write(self.style.WARNING(f"    ⚠ Created Stage {stage_num} as DRAFT (needs document)"))
                    stages_backfilled += 1

                elif fix[0] == 'approve':
                    stage_num, stage = fix[1], fix[2]
                    # Session 916: Use approve() method which enforces document requirement
                    if stage.document:
                        stage.approve(
                            approved_by='fix_command',
                            notes=f'Approved by fix_initiative_stages command at {timezone.now().isoformat()}',
                            checks_passed={'has_document': True, 'fix_command': True}
                        )
                        self.stdout.write(self.style.SUCCESS(f"    ✓ Approved Stage {stage_num}"))
                    else:
                        # Cannot approve without document - set to DRAFT instead
                        stage.status = 'DRAFT'
                        stage.notes = f"{stage.notes}\n\n[Set to DRAFT by fix command - needs document]"
                        stage.save()
                        self.stdout.write(self.style.WARNING(f"    ⚠ Stage {stage_num} set to DRAFT (no document)"))
                    stages_backfilled += 1

            fixed_count += 1

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.SUCCESS("FIX COMPLETE"))
        self.stdout.write(f"  Initiatives {'would be ' if dry_run else ''}fixed: {fixed_count}")
        self.stdout.write(f"  Stages {'would be ' if dry_run else ''}backfilled: {stages_backfilled}")

        if not dry_run and fixed_count > 0:
            self.stdout.write(self.style.NOTICE(
                f"\n✅ Fixed {fixed_count} initiatives with {stages_backfilled} stages backfilled"
            ))
