"""
Session 914: Set Founder Intent for Initiatives

Management command to set founder intent on initiatives, enabling auto-progression.

Usage:
    # Set intent for a single initiative
    python manage.py set_founder_intent --initiative-id=<uuid> --speed=fast

    # Set intent for all initiatives at Stage 2+ without intent
    python manage.py set_founder_intent --all-pending --speed=balanced

    # Interactive mode
    python manage.py set_founder_intent --interactive

    # List initiatives awaiting founder intent
    python manage.py set_founder_intent --list
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set founder intent on initiatives to enable auto-progression'

    def add_arguments(self, parser):
        parser.add_argument(
            '--initiative-id',
            type=str,
            help='UUID of specific initiative to update'
        )
        parser.add_argument(
            '--all-pending',
            action='store_true',
            help='Set intent for all initiatives at Stage 2+ without intent'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List initiatives awaiting founder intent'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Interactive mode - prompt for each initiative'
        )
        parser.add_argument(
            '--speed',
            type=str,
            choices=['fast', 'balanced', 'thorough'],
            default='balanced',
            help='Execution speed (default: balanced)'
        )
        parser.add_argument(
            '--risk',
            type=str,
            choices=['low', 'medium', 'high'],
            default='medium',
            help='Risk tolerance (default: medium)'
        )
        parser.add_argument(
            '--engineering-hours',
            type=int,
            help='Max engineering hours budget'
        )
        parser.add_argument(
            '--llm-spend',
            type=float,
            help='Max LLM API spend in dollars'
        )
        parser.add_argument(
            '--stop-rule',
            type=str,
            default='',
            help='What outcome should kill this initiative'
        )
        parser.add_argument(
            '--boardroom',
            action='store_true',
            help='Require explicit Boardroom approval'
        )
        # Session 914.2: Execution Track options
        parser.add_argument(
            '--track',
            type=str,
            choices=['fast_track', 'institutional'],
            help='Execution track (fast_track: Stage 1-2, institutional: Full 5-stage)'
        )
        parser.add_argument(
            '--auto-detect-track',
            action='store_true',
            help='Auto-detect execution track based on content flags'
        )
        parser.add_argument(
            '--content-flags',
            type=str,
            help='Comma-separated content flags (external_data,user_data,public_publishing,legal_compliance,financial,irreversible)'
        )
        parser.add_argument(
            '--approve-stage',
            type=int,
            choices=[2, 3, 4],
            help='Approve a specific stage (institutional track only)'
        )
        parser.add_argument(
            '--complete-compliance',
            action='store_true',
            help='Mark compliance review as complete (institutional track only)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914: Set Founder Intent'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # List mode
        if options['list']:
            self._list_pending_initiatives()
            return

        # Interactive mode
        if options['interactive']:
            self._interactive_mode(options)
            return

        # Single initiative mode
        if options['initiative_id']:
            try:
                initiative = Initiative.objects.get(id=options['initiative_id'])
                self._set_intent(initiative, options)
            except Initiative.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Initiative not found: {options['initiative_id']}"))
            return

        # All pending mode
        if options['all_pending']:
            initiatives = Initiative.objects.filter(
                founder_intent_set=False,
                current_stage__gte=2
            )
            self.stdout.write(f"\nFound {initiatives.count()} initiatives at Stage 2+ without founder intent")

            for init in initiatives:
                self._set_intent(init, options)

            return

        # No mode specified
        self.stdout.write(self.style.WARNING(
            '\nPlease specify one of: --initiative-id, --all-pending, --list, or --interactive'
        ))

    def _list_pending_initiatives(self):
        from core.models_document_registry import Initiative

        # Initiatives at Stage 2+ without intent
        pending = Initiative.objects.filter(
            founder_intent_set=False,
            current_stage__gte=2
        ).order_by('-current_stage', '-updated_at')

        self.stdout.write(f"\n📋 Initiatives awaiting founder intent: {pending.count()}\n")

        for init in pending:
            blocked = init.progression_blocked_reason or 'Unknown'
            track = getattr(init, 'execution_track', 'fast_track') or 'fast_track'
            max_stage = getattr(init, 'max_stage', 5) if hasattr(init, 'max_stage') else (2 if track == 'fast_track' else 5)
            self.stdout.write(f"\n  📌 {init.name[:60]}...")
            self.stdout.write(f"     Stage: {init.current_stage}/{max_stage} ({track})")
            self.stdout.write(f"     Blocked: {blocked}")
            self.stdout.write(f"     ID: {init.id}")

        # Also show initiatives at Stage 1 (can progress without intent)
        stage1 = Initiative.objects.filter(
            founder_intent_set=False,
            current_stage=1
        ).count()

        self.stdout.write(f"\n📋 Initiatives at Stage 1 (can progress without intent): {stage1}")

    def _set_intent(self, initiative, options):
        dry_run = options['dry_run']
        prefix = '[DRY-RUN] ' if dry_run else ''

        self.stdout.write(f"\n{prefix}Setting intent for: {initiative.name[:50]}...")
        self.stdout.write(f"   Speed: {options['speed']}")
        self.stdout.write(f"   Risk: {options['risk']}")
        if options['engineering_hours']:
            self.stdout.write(f"   Budget (hours): {options['engineering_hours']}")
        if options['llm_spend']:
            self.stdout.write(f"   Budget (LLM): ${options['llm_spend']}")
        if options['stop_rule']:
            self.stdout.write(f"   Stop rule: {options['stop_rule'][:50]}...")
        if options['boardroom']:
            self.stdout.write(f"   Requires Boardroom: Yes")

        # Session 914.2: Execution Track options
        if options.get('track'):
            self.stdout.write(f"   Track: {options['track']}")
        if options.get('auto_detect_track'):
            self.stdout.write(f"   Auto-detect track: Yes")
        if options.get('content_flags'):
            self.stdout.write(f"   Content flags: {options['content_flags']}")
        if options.get('approve_stage'):
            self.stdout.write(f"   Approve stage: {options['approve_stage']}")
        if options.get('complete_compliance'):
            self.stdout.write(f"   Complete compliance: Yes")

        if not dry_run:
            # Set founder intent
            initiative.set_founder_intent(
                execution_speed=options['speed'],
                risk_tolerance=options['risk'],
                budget_engineering_hours=options['engineering_hours'],
                budget_llm_spend=options['llm_spend'],
                stop_rule=options['stop_rule'],
                requires_boardroom_approval=options['boardroom'],
                set_by='CLI:set_founder_intent'
            )
            self.stdout.write(self.style.SUCCESS(f"   ✅ Intent set"))

            # Session 914.2: Handle execution track
            if options.get('auto_detect_track'):
                track = initiative.auto_detect_execution_track()
                self.stdout.write(self.style.SUCCESS(f"   ✅ Auto-detected track: {track}"))
                if initiative.content_flags:
                    self.stdout.write(f"      Flags: {initiative.content_flags}")
            elif options.get('track'):
                content_flags = options.get('content_flags', '').split(',') if options.get('content_flags') else None
                initiative.set_execution_track(
                    track=options['track'],
                    content_flags=content_flags,
                    set_by='CLI:set_founder_intent'
                )
                self.stdout.write(self.style.SUCCESS(f"   ✅ Track set: {options['track']}"))

            # Handle stage approval
            if options.get('approve_stage'):
                stage_num = options['approve_stage']
                initiative.approve_stage(stage_num, approved_by='CLI:set_founder_intent')
                self.stdout.write(self.style.SUCCESS(f"   ✅ Stage {stage_num} approved"))

            # Handle compliance review
            if options.get('complete_compliance'):
                initiative.complete_compliance_review(reviewed_by='CLI:set_founder_intent')
                self.stdout.write(self.style.SUCCESS(f"   ✅ Compliance review complete"))
        else:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Would set intent (dry run)"))

    def _interactive_mode(self, options):
        from core.models_document_registry import Initiative

        pending = Initiative.objects.filter(
            founder_intent_set=False,
            current_stage__gte=2
        ).order_by('-current_stage', '-updated_at')

        self.stdout.write(f"\n📋 Found {pending.count()} initiatives needing review\n")

        for init in pending:
            self.stdout.write(f"\n{'=' * 60}")
            self.stdout.write(f"Initiative: {init.name}")
            self.stdout.write(f"Stage: {init.current_stage}/5")
            self.stdout.write(f"Purpose: {init.get_purpose_display()}")
            self.stdout.write(f"Description: {init.description[:200]}...")

            # Session 914.2: Show auto-detected content flags
            flags = init.detect_content_flags() if hasattr(init, 'detect_content_flags') else []
            if flags:
                self.stdout.write(f"Detected Flags: {', '.join(flags)}")
                self.stdout.write(self.style.WARNING("  ⚠️ Recommend Institutional Track"))

            self.stdout.write(f"{'=' * 60}")

            # Get user input
            self.stdout.write("\nOptions:")
            self.stdout.write("  1. Fast Track (Stage 1-2 only, quick experiment)")
            self.stdout.write("  2. Institutional (Full 5-stage, compliance gates)")
            self.stdout.write("  3. Auto-detect Track (based on content)")
            self.stdout.write("  4. Skip (leave without intent)")
            self.stdout.write("  5. Kill (archive this initiative)")
            self.stdout.write("  q. Quit")

            choice = input("\nYour choice [1-5, q]: ").strip().lower()

            if choice == 'q':
                self.stdout.write("\nExiting interactive mode")
                break
            elif choice == '1':
                # Fast Track
                init.set_founder_intent(
                    execution_speed='fast',
                    risk_tolerance='high',
                    set_by='CLI:interactive'
                )
                init.set_execution_track(
                    track='fast_track',
                    set_by='CLI:interactive'
                )
                self.stdout.write(self.style.SUCCESS("✅ Set to Fast Track (Stage 1-2)"))
            elif choice == '2':
                # Institutional Track
                init.set_founder_intent(
                    execution_speed='thorough',
                    risk_tolerance='low',
                    requires_boardroom_approval=True,
                    set_by='CLI:interactive'
                )
                init.set_execution_track(
                    track='institutional',
                    content_flags=flags,
                    set_by='CLI:interactive'
                )
                self.stdout.write(self.style.SUCCESS("✅ Set to Institutional (Full 5-stage)"))
            elif choice == '3':
                # Auto-detect
                init.set_founder_intent(
                    execution_speed='balanced',
                    risk_tolerance='medium',
                    set_by='CLI:interactive'
                )
                track = init.auto_detect_execution_track()
                if track == 'institutional':
                    self.stdout.write(self.style.SUCCESS(f"✅ Auto-detected: Institutional (flags: {init.content_flags})"))
                else:
                    self.stdout.write(self.style.SUCCESS("✅ Auto-detected: Fast Track"))
            elif choice == '4':
                self.stdout.write(self.style.WARNING("⏭️ Skipped"))
            elif choice == '5':
                init.status = 'ARCHIVED'
                init.save()
                self.stdout.write(self.style.WARNING("🗑️ Archived"))
            else:
                self.stdout.write(self.style.ERROR("Invalid choice, skipping"))
