"""
Session 914.5: Daily Priorities Management

Management command to run daily priority scan and manage focus initiatives.

Usage:
    # Run the daily priority scan
    python manage.py daily_priorities --scan

    # View current daily focus initiatives
    python manage.py daily_priorities --list

    # View priority summary
    python manage.py daily_priorities --summary

    # Manually set an initiative as top priority
    python manage.py daily_priorities --set-priority <uuid> --rank=1 --reason="Critical for launch"

    # Clear manual priority
    python manage.py daily_priorities --clear-priority <uuid>
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage daily initiative priorities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scan',
            action='store_true',
            help='Run the daily priority scan'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List current daily focus initiatives'
        )
        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show priority summary'
        )
        parser.add_argument(
            '--set-priority',
            type=str,
            help='Initiative UUID to set as manual priority'
        )
        parser.add_argument(
            '--rank',
            type=int,
            choices=[1, 2, 3, 4, 5],
            default=1,
            help='Priority rank (1=highest, 5=lowest)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for manual priority'
        )
        parser.add_argument(
            '--clear-priority',
            type=str,
            help='Initiative UUID to clear manual priority'
        )
        parser.add_argument(
            '--focus-count',
            type=int,
            default=5,
            help='Number of initiatives to focus on (default 5)'
        )

    def handle(self, *args, **options):
        from core.services.daily_priorities import (
            run_daily_priority_scan,
            get_daily_focus_initiatives,
            get_priority_summary,
            set_manual_priority
        )
        from core.models_document_registry import Initiative

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914.5: Daily Priorities'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # Run scan
        if options['scan']:
            self._run_scan(options['focus_count'])
            return

        # List focus
        if options['list']:
            self._list_focus()
            return

        # Summary
        if options['summary']:
            self._show_summary()
            return

        # Set manual priority
        if options['set_priority']:
            result = set_manual_priority(
                options['set_priority'],
                priority_rank=options['rank'],
                reason=options['reason']
            )
            if result['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Priority set for: {result['initiative_name'][:50]}"
                ))
                self.stdout.write(f"   Rank: {result['priority_rank']}")
                if result['reason']:
                    self.stdout.write(f"   Reason: {result['reason']}")
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {result['error']}"))
            return

        # Clear priority
        if options['clear_priority']:
            try:
                init = Initiative.objects.get(id=options['clear_priority'])
                init.manual_priority_rank = None
                init.manual_priority_reason = ''
                init.save(update_fields=['manual_priority_rank', 'manual_priority_reason'])
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Manual priority cleared for: {init.name[:50]}"
                ))
            except Initiative.DoesNotExist:
                self.stdout.write(self.style.ERROR("\n❌ Initiative not found"))
            return

        # Default: show summary
        self._show_summary()

    def _run_scan(self, focus_count):
        from core.services.daily_priorities import run_daily_priority_scan

        self.stdout.write(f"\n🔍 Running daily priority scan (top {focus_count})...")

        result = run_daily_priority_scan(focus_count=focus_count)

        if result['success']:
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Scan complete: {result['focus_count']} focus initiatives"
            ))
            self.stdout.write(f"   Total scanned: {result['total_scanned']}")
            self.stdout.write(f"   Scan date: {result['scan_date']}")

            self.stdout.write(f"\n🎯 Daily Focus Initiatives:")
            for i, init in enumerate(result['focus_initiatives'], 1):
                score = init['final_score']
                stage = init['current_stage']
                level = init['priority_level']
                self.stdout.write(
                    f"   {i}. [{level.upper()}] {init['name'][:45]}..."
                )
                self.stdout.write(
                    f"      Stage {stage}/5 | Score: {score:.2f}"
                )
        else:
            self.stdout.write(self.style.ERROR(f"\n❌ Scan failed"))

    def _list_focus(self):
        from core.services.daily_priorities import get_daily_focus_initiatives

        focus = get_daily_focus_initiatives()

        self.stdout.write(f"\n🎯 Today's Focus Initiatives ({len(focus)}):\n")

        if not focus:
            self.stdout.write("   No focus initiatives set. Run --scan first.")
            return

        for i, init in enumerate(focus, 1):
            score = init['final_score']
            stage = init['current_stage']
            level = init['priority_level']
            factors = init['factors']

            # Color based on priority
            if level == 'critical':
                style = self.style.ERROR
            elif level == 'high':
                style = self.style.WARNING
            else:
                style = self.style.SUCCESS

            self.stdout.write(style(
                f"   #{i} [{level.upper()}] {init['name'][:45]}..."
            ))
            self.stdout.write(
                f"      Stage {stage}/5 | Score: {score:.2f} (base: {init['base_score']:.2f})"
            )

            # Show factors that boosted/lowered priority
            boosts = []
            if factors['stage'] > 1.0:
                boosts.append(f"stage: +{(factors['stage']-1)*100:.0f}%")
            if factors['freshness'] > 1.0:
                boosts.append(f"fresh: +{(factors['freshness']-1)*100:.0f}%")
            if factors['intent'] > 1.0:
                boosts.append(f"intent: +{(factors['intent']-1)*100:.0f}%")
            if factors['speed'] > 1.0:
                boosts.append(f"fast: +{(factors['speed']-1)*100:.0f}%")

            if boosts:
                self.stdout.write(f"      Boosts: {', '.join(boosts)}")

            self.stdout.write(f"      ID: {init['initiative_id']}")
            self.stdout.write("")

    def _show_summary(self):
        from core.services.daily_priorities import get_priority_summary

        summary = get_priority_summary()

        self.stdout.write(f"\n📊 Priority Summary:")
        self.stdout.write(f"   Total Active: {summary['total_active']}")
        self.stdout.write(f"   Critical Priority: {summary['critical_priority']}")
        self.stdout.write(f"   High Priority: {summary['high_priority']}")
        self.stdout.write(f"   Daily Focus: {summary['daily_focus']}")
        self.stdout.write(f"   Ready for Progression: {summary['ready_for_progression']}")

        if summary['scan_date']:
            self.stdout.write(f"   Last Scan: {summary['scan_date']}")
        else:
            self.stdout.write(self.style.WARNING(
                "   Last Scan: Never (run --scan)"
            ))
