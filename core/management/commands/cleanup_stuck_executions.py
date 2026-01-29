"""
Session 866: Cleanup Stuck Agent Executions

Marks AgentExecution records that have been stuck in 'in_progress' status
for too long as 'failed'. This prevents the UI from showing stale "Running"
tasks that will never complete.

Usage:
    python manage.py cleanup_stuck_executions           # Dry run (default)
    python manage.py cleanup_stuck_executions --apply   # Actually apply changes
    python manage.py cleanup_stuck_executions --hours 2 # Custom threshold (default 1)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Mark stuck in_progress AgentExecutions as failed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually apply the changes (default is dry run)',
        )
        parser.add_argument(
            '--hours',
            type=float,
            default=1.0,
            help='Hours threshold - executions older than this are considered stuck (default: 1)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import AgentExecution

        apply = options['apply']
        hours = options['hours']
        cutoff = timezone.now() - timedelta(hours=hours)

        # Find stuck executions
        stuck = AgentExecution.objects.filter(
            status='in_progress',
            created_at__lt=cutoff
        ).order_by('-created_at')

        count = stuck.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                f'No stuck executions found (older than {hours} hours)'
            ))
            return

        self.stdout.write(f'Found {count} stuck AgentExecutions (in_progress > {hours}h)')
        self.stdout.write('')

        # Show what will be updated
        for ex in stuck[:20]:
            age = timezone.now() - ex.created_at
            agent = ex.agent.name if ex.agent else 'Unknown'
            task_preview = (ex.task[:50] + '...') if ex.task and len(ex.task) > 50 else (ex.task or 'no task')
            self.stdout.write(f'  {agent}: {age.total_seconds()/3600:.1f}h ago')
            self.stdout.write(f'    {task_preview}')

        if count > 20:
            self.stdout.write(f'  ... and {count - 20} more')

        self.stdout.write('')

        if apply:
            # Update all stuck executions
            updated = stuck.update(
                status='failed',
                error_message='Marked as failed by cleanup_stuck_executions: execution timed out',
                completed_at=timezone.now()
            )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully marked {updated} executions as failed'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'DRY RUN: Would mark {count} executions as failed'
            ))
            self.stdout.write('Run with --apply to actually apply changes')
