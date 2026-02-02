"""
Session 914.3: Check and Manage Initiative Semantic Drift

Management command to check semantic drift on initiatives and manage overrides.

Usage:
    # Check drift for a single initiative
    python manage.py check_initiative_drift --initiative-id=<uuid>

    # Check drift for all initiatives with documents
    python manage.py check_initiative_drift --all

    # List initiatives with drift issues
    python manage.py check_initiative_drift --list-flagged

    # Override drift for a stage (allow progression)
    python manage.py check_initiative_drift --initiative-id=<uuid> --stage=2 --override --reason="Intentional pivot"

    # Set drift threshold for initiative
    python manage.py check_initiative_drift --initiative-id=<uuid> --set-threshold=strict
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and manage semantic drift on initiatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--initiative-id',
            type=str,
            help='UUID of specific initiative to check'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Check all initiatives with stage documents'
        )
        parser.add_argument(
            '--list-flagged',
            action='store_true',
            help='List initiatives flagged for drift'
        )
        parser.add_argument(
            '--stage',
            type=int,
            choices=[1, 2, 3, 4, 5],
            help='Specific stage to check or override'
        )
        parser.add_argument(
            '--override',
            action='store_true',
            help='Override drift flag to allow progression'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for drift override'
        )
        parser.add_argument(
            '--set-threshold',
            type=str,
            choices=['strict', 'balanced', 'relaxed', 'disabled'],
            help='Set drift threshold for initiative'
        )
        parser.add_argument(
            '--disable-drift',
            action='store_true',
            help='Disable drift checking for initiative'
        )
        parser.add_argument(
            '--enable-drift',
            action='store_true',
            help='Enable drift checking for initiative'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914.3: Semantic Drift Check'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # List flagged
        if options['list_flagged']:
            self._list_flagged()
            return

        # All initiatives
        if options['all']:
            self._check_all(options)
            return

        # Single initiative
        if options['initiative_id']:
            try:
                initiative = Initiative.objects.get(id=options['initiative_id'])
                self._process_initiative(initiative, options)
            except Initiative.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Initiative not found: {options['initiative_id']}"))
            return

        # No mode specified
        self.stdout.write(self.style.WARNING(
            '\nPlease specify one of: --initiative-id, --all, or --list-flagged'
        ))

    def _list_flagged(self):
        from core.models_document_registry import InitiativeStage

        flagged = InitiativeStage.objects.filter(
            drift_flagged=True,
            drift_override=False
        ).select_related('initiative').order_by('-drift_checked_at')

        self.stdout.write(f"\n🚨 Stages flagged for drift: {flagged.count()}\n")

        for stage in flagged:
            self.stdout.write(f"\n  📌 {stage.initiative.name[:50]}...")
            self.stdout.write(f"     Stage: {stage.stage} ({stage.stage_name})")
            self.stdout.write(f"     Drift Score: {stage.drift_score:.0%}" if stage.drift_score else "     Drift Score: N/A")
            self.stdout.write(f"     Similarity: {stage.similarity_score:.0%}" if stage.similarity_score else "     Similarity: N/A")
            self.stdout.write(f"     Checked: {stage.drift_checked_at}")
            self.stdout.write(f"     Initiative ID: {stage.initiative.id}")

    def _check_all(self, options):
        from core.models_document_registry import Initiative

        initiatives = Initiative.objects.filter(
            stages__document__isnull=False
        ).distinct().order_by('-updated_at')[:50]

        self.stdout.write(f"\nChecking drift for {initiatives.count()} initiatives...\n")

        drift_count = 0
        for init in initiatives:
            result = self._check_initiative_drift(init, options)
            if result.get('stages_with_drift', 0) > 0:
                drift_count += 1

        self.stdout.write(f"\n📊 Summary: {drift_count} initiatives have drift issues")

    def _process_initiative(self, initiative, options):
        dry_run = options['dry_run']
        prefix = '[DRY-RUN] ' if dry_run else ''

        self.stdout.write(f"\n{prefix}Initiative: {initiative.name[:60]}...")
        self.stdout.write(f"   Current Stage: {initiative.current_stage}/5")
        self.stdout.write(f"   Drift Threshold: {initiative.drift_threshold if hasattr(initiative, 'drift_threshold') else 'balanced'}")
        self.stdout.write(f"   Drift Enabled: {initiative.drift_check_enabled if hasattr(initiative, 'drift_check_enabled') else True}")

        # Set threshold
        if options.get('set_threshold'):
            if not dry_run:
                initiative.drift_threshold = options['set_threshold']
                initiative.save(update_fields=['drift_threshold'])
            self.stdout.write(self.style.SUCCESS(f"   ✅ Threshold set to: {options['set_threshold']}"))

        # Enable/disable drift
        if options.get('disable_drift'):
            if not dry_run:
                initiative.drift_check_enabled = False
                initiative.save(update_fields=['drift_check_enabled'])
            self.stdout.write(self.style.WARNING(f"   ⚠️ Drift checking disabled"))

        if options.get('enable_drift'):
            if not dry_run:
                initiative.drift_check_enabled = True
                initiative.save(update_fields=['drift_check_enabled'])
            self.stdout.write(self.style.SUCCESS(f"   ✅ Drift checking enabled"))

        # Override specific stage
        if options.get('override') and options.get('stage'):
            self._override_stage(initiative, options)
            return

        # Check drift
        self._check_initiative_drift(initiative, options)

    def _check_initiative_drift(self, initiative, options):
        from core.services.semantic_drift_detector import get_drift_detector
        from core.models_document_registry import InitiativeStage

        detector = get_drift_detector()
        result = detector.check_initiative_drift(str(initiative.id))

        if not result.get('success'):
            self.stdout.write(self.style.ERROR(f"   ❌ {result.get('error')}"))
            return result

        self.stdout.write(f"\n   📊 Drift Analysis:")
        self.stdout.write(f"      Stages Checked: {result.get('stages_checked', 0)}")
        self.stdout.write(f"      Stages with Drift: {result.get('stages_with_drift', 0)}")
        self.stdout.write(f"      Overall Alignment: {result.get('overall_alignment', 0):.0%}")

        for stage_result in result.get('stage_results', []):
            stage_num = stage_result.get('stage')
            has_drift = stage_result.get('has_drift')
            similarity = stage_result.get('similarity_score', 0)

            if has_drift:
                self.stdout.write(self.style.WARNING(
                    f"      Stage {stage_num}: ⚠️ DRIFT (similarity: {similarity:.0%})"
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"      Stage {stage_num}: ✅ Aligned (similarity: {similarity:.0%})"
                ))

        return result

    def _override_stage(self, initiative, options):
        from core.models_document_registry import InitiativeStage

        stage_num = options['stage']
        reason = options.get('reason', '')
        dry_run = options['dry_run']

        try:
            stage = InitiativeStage.objects.get(
                initiative=initiative,
                stage=stage_num
            )
        except InitiativeStage.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"   ❌ Stage {stage_num} not found"))
            return

        if not dry_run:
            stage.drift_override = True
            stage.drift_override_by = 'CLI:check_initiative_drift'
            stage.drift_override_reason = reason
            stage.save(update_fields=['drift_override', 'drift_override_by', 'drift_override_reason'])

        self.stdout.write(self.style.SUCCESS(f"   ✅ Stage {stage_num} drift overridden"))
        if reason:
            self.stdout.write(f"      Reason: {reason}")
