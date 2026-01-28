"""
Management Command: cleanup_stuck_tasks
========================================

Cleans up stuck agent executions that have been running too long.

Usage:
    python manage.py cleanup_stuck_tasks
    python manage.py cleanup_stuck_tasks --hours 2  # Tasks running > 2 hours
    python manage.py cleanup_stuck_tasks --dry-run  # Preview without changing

Session 855: Initial implementation
"""

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clean up stuck agent executions that have been running too long'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=float,
            default=1.0,
            help='Mark tasks as failed if running longer than this (default: 1 hour)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview stuck tasks without marking them as failed'
        )

    def handle(self, *args, **options):
        from core.models_unified_system import AgentExecution

        hours = options['hours']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(hours=hours)

        self.stdout.write(self.style.SUCCESS(f'\n🧹 CLEANUP STUCK TASKS'))
        self.stdout.write(f'   Threshold: Running > {hours} hour(s)')
        self.stdout.write(f'   Cutoff: {cutoff.isoformat()}')
        if dry_run:
            self.stdout.write(self.style.WARNING('   Mode: DRY RUN (no changes)'))
        self.stdout.write('')

        # Find stuck executions
        stuck = AgentExecution.objects.filter(
            status='running',
            created_at__lt=cutoff
        ).order_by('-created_at')

        count = stuck.count()
        self.stdout.write(f'Found {count} stuck executions:')
        self.stdout.write('')

        for ex in stuck[:50]:
            age = (timezone.now() - ex.created_at).total_seconds() / 60
            agent = ex.agent.name if ex.agent else 'Unknown'
            self.stdout.write(f'  {age:6.0f}m - {agent}: {ex.task[:60]}')

        if count > 50:
            self.stdout.write(f'  ... and {count - 50} more')

        self.stdout.write('')

        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No stuck tasks found!'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would mark {count} executions as failed'))
            return

        # Update them
        updated = stuck.update(
            status='failed',
            error_message=f'Marked as failed by cleanup_stuck_tasks - was running > {hours} hour(s)',
            completed_at=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Marked {updated} executions as failed'))
