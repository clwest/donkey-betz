"""
Session 914.4: Initiative Rate Limit Management

Management command to view and manage daily progression rate limits.

Usage:
    # View current rate limit status
    python manage.py initiative_rate_limit --status

    # Reset daily count (admin override)
    python manage.py initiative_rate_limit --reset

    # Set custom limit for today (via cache)
    python manage.py initiative_rate_limit --set-limit=60

    # View progression history
    python manage.py initiative_rate_limit --history
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'View and manage initiative progression rate limits'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current rate limit status'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset daily progression count'
        )
        parser.add_argument(
            '--set-limit',
            type=int,
            help='Set custom daily limit (temporary, via cache)'
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Show recent progression history'
        )

    def handle(self, *args, **options):
        from core.services.initiative_auto_progression import (
            get_daily_progression_stats,
            reset_daily_progression_count,
            get_daily_progression_limit,
            RATE_LIMIT_CACHE_KEY
        )
        from django.core.cache import cache

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 914.4: Initiative Rate Limits'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # Status (default if no option specified)
        if options['status'] or not any([options['reset'], options['set_limit'], options['history']]):
            self._show_status()
            return

        # Reset
        if options['reset']:
            result = reset_daily_progression_count()
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Daily count reset (was {result['previous_count']})"
            ))
            self._show_status()
            return

        # Set limit
        if options['set_limit']:
            new_limit = options['set_limit']
            cache.set('initiative_progression_custom_limit', new_limit, 86400)
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Custom limit set to {new_limit} for today"
            ))
            self._show_status()
            return

        # History
        if options['history']:
            self._show_history()
            return

    def _show_status(self):
        from core.services.initiative_auto_progression import (
            get_daily_progression_stats,
            get_daily_progression_limit
        )

        stats = get_daily_progression_stats()

        self.stdout.write(f"\n📊 Rate Limit Status:")
        self.stdout.write(f"   Date: {stats['date']}")
        self.stdout.write(f"   Progressions Today: {stats['count']}")
        self.stdout.write(f"   Daily Limit: {stats['limit']}")
        self.stdout.write(f"   Remaining: {stats['remaining']}")
        self.stdout.write(f"   Usage: {stats['percentage_used']:.1f}%")

        if stats['is_limited']:
            self.stdout.write(self.style.ERROR(f"   Status: 🚫 RATE LIMITED"))
        elif stats['percentage_used'] >= 80:
            self.stdout.write(self.style.WARNING(f"   Status: ⚠️ APPROACHING LIMIT"))
        else:
            self.stdout.write(self.style.SUCCESS(f"   Status: ✅ WITHIN LIMITS"))

        # Progress bar
        bar_width = 40
        filled = int(bar_width * stats['percentage_used'] / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        self.stdout.write(f"\n   [{bar}] {stats['percentage_used']:.0f}%")

    def _show_history(self):
        from core.models_document_registry import InitiativeStage
        from django.utils import timezone
        from datetime import timedelta

        self.stdout.write(f"\n📜 Recent Progressions (last 24h):")

        cutoff = timezone.now() - timedelta(hours=24)

        # Get recently approved stages
        recent = InitiativeStage.objects.filter(
            status='APPROVED',
            approved_at__gte=cutoff
        ).select_related('initiative').order_by('-approved_at')[:20]

        if not recent:
            self.stdout.write("   No progressions in the last 24 hours")
            return

        for stage in recent:
            time_str = stage.approved_at.strftime('%H:%M') if stage.approved_at else 'N/A'
            self.stdout.write(
                f"   {time_str} | Stage {stage.stage} | {stage.initiative.name[:40]}..."
            )

        # Group by hour
        self.stdout.write(f"\n📈 Progressions by Hour:")
        hourly = {}
        for stage in recent:
            if stage.approved_at:
                hour = stage.approved_at.strftime('%Y-%m-%d %H:00')
                hourly[hour] = hourly.get(hour, 0) + 1

        for hour, count in sorted(hourly.items(), reverse=True)[:12]:
            bar = '█' * count
            self.stdout.write(f"   {hour}: {bar} ({count})")
