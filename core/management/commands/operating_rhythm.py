"""
Session 914.7: Operating Rhythm Management

Management command for daily/weekly operating rhythm.

Usage:
    # Set today's top 3 priorities
    python manage.py operating_rhythm --set-priorities "Launch podcast" "Fix auth bugs" "Content quality"

    # View current priorities
    python manage.py operating_rhythm --status

    # Generate weekly Ship/Learn/Kill report
    python manage.py operating_rhythm --weekly-report

    # Submit weekly feedback (becomes training signal)
    python manage.py operating_rhythm --feedback "Focus on user-facing features, fewer infrastructure changes"

    # Map an initiative to a priority
    python manage.py operating_rhythm --map-initiative <uuid> --priority=1
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage operating rhythm (daily priorities, weekly reports)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-priorities',
            nargs='+',
            type=str,
            help='Set today\'s top 3 priorities (space-separated)'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current operating rhythm status'
        )
        parser.add_argument(
            '--weekly-report',
            action='store_true',
            help='Generate weekly Ship/Learn/Kill report'
        )
        parser.add_argument(
            '--feedback',
            type=str,
            help='Submit weekly feedback (becomes training signal)'
        )
        parser.add_argument(
            '--map-initiative',
            type=str,
            help='Initiative UUID to map to a priority'
        )
        parser.add_argument(
            '--priority',
            type=int,
            choices=[1, 2, 3],
            default=1,
            help='Priority number to map to (1, 2, or 3)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show recent feedback history'
        )

    def handle(self, *args, **options):
        from core.services.operating_rhythm import (
            set_daily_priorities,
            get_daily_priorities,
            generate_weekly_report,
            submit_weekly_feedback,
            map_initiative_to_priority,
            get_rhythm_status
        )

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914.7: Operating Rhythm'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # Set priorities
        if options['set_priorities']:
            priorities = options['set_priorities'][:3]  # Take max 3
            result = set_daily_priorities(priorities)

            if result['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Daily priorities set for {result['date']}:"
                ))
                for i, p in enumerate(result['priorities'], 1):
                    self.stdout.write(f"   #{i}: {p}")
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {result['error']}"))
            return

        # Weekly report
        if options['weekly_report']:
            self._show_weekly_report()
            return

        # Submit feedback
        if options['feedback']:
            result = submit_weekly_feedback(options['feedback'])
            if result['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Weekly feedback submitted!"
                ))
                self.stdout.write(f"   Week of: {result['week_of']}")
                self.stdout.write(f"   Length: {result['feedback_length']} chars")
                self.stdout.write(f"   Learning created: {result['learning_created']}")
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {result['error']}"))
            return

        # Map initiative
        if options['map_initiative']:
            result = map_initiative_to_priority(
                options['map_initiative'],
                options['priority'] - 1  # Convert 1-based to 0-based
            )
            if result['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Initiative mapped to priority #{options['priority']}!"
                ))
                self.stdout.write(f"   Initiative: {result['initiative_name'][:50]}")
                self.stdout.write(f"   Priority: {result['priority_text']}")
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ {result['error']}"))
            return

        # Show history
        if options['history']:
            self._show_history()
            return

        # Default: show status
        self._show_status()

    def _show_status(self):
        from core.services.operating_rhythm import get_rhythm_status

        status = get_rhythm_status()
        daily = status['daily_priorities']
        summary = status['initiative_summary']

        self.stdout.write(f"\n📅 Daily Priorities:")
        if daily['priorities']:
            for i, p in enumerate(daily['priorities'], 1):
                self.stdout.write(f"   #{i}: {p}")
            self.stdout.write(f"   Set for: {daily['date']}")
            if not daily['is_current']:
                self.stdout.write(self.style.WARNING("   ⚠️ STALE - priorities are from yesterday"))
        else:
            self.stdout.write(self.style.WARNING("   No priorities set for today"))

        self.stdout.write(f"\n📊 Initiative Summary:")
        self.stdout.write(f"   Total Active: {summary['total_active']}")
        self.stdout.write(f"   With Founder Intent: {summary['with_intent']}")
        self.stdout.write(f"   In Daily Focus: {summary['in_daily_focus']}")

        if status['last_weekly_feedback']:
            self.stdout.write(f"\n📝 Last Weekly Feedback: {status['last_weekly_feedback'][:10]}")
        else:
            self.stdout.write(self.style.WARNING("\n📝 No weekly feedback submitted yet"))

        if status['recommendations']:
            self.stdout.write(f"\n💡 Recommendations:")
            for rec in status['recommendations']:
                self.stdout.write(self.style.WARNING(f"   • {rec}"))

    def _show_weekly_report(self):
        from core.services.operating_rhythm import generate_weekly_report

        report = generate_weekly_report()

        self.stdout.write(f"\n📊 Weekly Report: {report['week_start']} to {report['week_end']}")
        self.stdout.write("=" * 50)

        # Summary
        s = report['summary']
        self.stdout.write(f"\n📈 Summary:")
        self.stdout.write(f"   Shipped: {s['shipped_count']} initiatives progressed")
        self.stdout.write(f"   Deliverables Created: {s['deliverables_created']}")
        self.stdout.write(f"   Learnings: {s['learned_count']}")
        self.stdout.write(f"   Blocked: {s['blocked_count']}")
        self.stdout.write(f"   Kill Candidates: {s['kill_candidates_count']}")
        self.stdout.write(f"   Needs Decision: {s['needs_decision_count']}")

        # Shipped
        if report['shipped']:
            self.stdout.write(self.style.SUCCESS(f"\n🚢 SHIPPED ({len(report['shipped'])}):"))
            for item in report['shipped'][:5]:
                self.stdout.write(
                    f"   • {item['name'][:50]} (Stage {item['stage']}, {item['track']})"
                )
            if len(report['shipped']) > 5:
                self.stdout.write(f"   ... and {len(report['shipped']) - 5} more")

        # Learned
        if report['learned']:
            self.stdout.write(self.style.HTTP_INFO(f"\n📚 LEARNED ({len(report['learned'])}):"))
            for item in report['learned'][:3]:
                self.stdout.write(f"   • {item['experiment'][:40]}")
                if item['key_insight']:
                    self.stdout.write(f"     → {item['key_insight'][:80]}...")

        # Blocked
        if report['blocked']:
            self.stdout.write(self.style.WARNING(f"\n🚧 BLOCKED ({len(report['blocked'])}):"))
            for item in report['blocked'][:5]:
                self.stdout.write(
                    f"   • {item['name'][:45]} ({item['days_stuck']}d stuck)"
                )
                self.stdout.write(f"     Reason: {item['blocked_reason'][:60]}")

        # Kill Candidates
        if report['kill_candidates']:
            self.stdout.write(self.style.ERROR(f"\n💀 KILL CANDIDATES ({len(report['kill_candidates'])}):"))
            for item in report['kill_candidates'][:5]:
                self.stdout.write(
                    f"   • {item['name'][:45]} ({item['days_stale']}d stale)"
                )

        # Needs Decision
        if report['needs_decision']:
            self.stdout.write(self.style.WARNING(f"\n⏳ NEEDS YOUR DECISION ({len(report['needs_decision'])}):"))
            for item in report['needs_decision'][:5]:
                self.stdout.write(f"   • {item['name'][:45]}")
                self.stdout.write(f"     Waiting for: {item['waiting_for']}")

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("Submit feedback with: --feedback \"Your feedback here\"")

    def _show_history(self):
        from core.models_unified_system import FounderFeedback

        self.stdout.write(f"\n📜 Recent Founder Feedback:\n")

        recent = FounderFeedback.objects.order_by('-created_at')[:10]

        if not recent:
            self.stdout.write("   No feedback history found.")
            return

        for fb in recent:
            date_str = fb.created_at.strftime("%Y-%m-%d %H:%M")
            type_display = fb.get_feedback_type_display()

            self.stdout.write(f"   [{date_str}] {type_display}")

            content = fb.content
            if fb.feedback_type == 'daily_priorities':
                priorities = content.get('priorities', [])
                for i, p in enumerate(priorities, 1):
                    self.stdout.write(f"      #{i}: {p}")
            elif fb.feedback_type == 'weekly_feedback':
                feedback_text = content.get('feedback', '')[:100]
                self.stdout.write(f"      {feedback_text}...")

            self.stdout.write("")
