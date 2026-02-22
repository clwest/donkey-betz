"""
Sync PeriodicTask queue fields to match CELERY_TASK_ROUTES.

When sync_celery_beat creates PeriodicTask records it never sets the `queue`
field.  Tasks created before routing rules were added retain stale queue values
(usually 'default' or NULL) that override or bypass the router, causing heavy
tasks to land on the 200 MB celery-worker instead of their intended queues.

This command reads CELERY_TASK_ROUTES, resolves the intended queue for each
enabled PeriodicTask, and updates any that differ.

Usage:
    python manage.py sync_task_queues              # Dry run
    python manage.py sync_task_queues --apply      # Apply changes
    python manage.py sync_task_queues --verbose    # Show all tasks
"""

from django.conf import settings
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = 'Sync PeriodicTask.queue fields to match CELERY_TASK_ROUTES'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply changes (default is dry run)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show all tasks including already-correct ones',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        verbose = options['verbose']

        routes = getattr(settings, 'CELERY_TASK_ROUTES', {})
        # Separate glob patterns (e.g. 'content.*') from explicit task routes
        glob_routes = {}
        explicit_routes = {}
        for key, val in routes.items():
            if '*' in key:
                # 'content.*' -> prefix 'content.'
                glob_routes[key.replace('.*', '.')] = val['queue']
            else:
                explicit_routes[key] = val['queue']

        mode = 'APPLY' if apply else 'DRY RUN'
        self.stdout.write(f'\n{"=" * 60}')
        self.stdout.write(f'sync_task_queues [{mode}]')
        self.stdout.write(f'{"=" * 60}')

        updated = 0
        correct = 0
        unmatched = 0

        for pt in PeriodicTask.objects.filter(enabled=True).order_by('task'):
            task_name = pt.task
            db_queue = pt.queue or ''

            # Resolve intended queue: explicit routes first, then globs
            intended = explicit_routes.get(task_name)
            if intended is None:
                for prefix, queue in glob_routes.items():
                    if task_name.startswith(prefix):
                        intended = queue
                        break

            if intended is None:
                unmatched += 1
                if verbose:
                    self.stdout.write(f'  [skip] {task_name}  (no route)')
                continue

            if db_queue == intended:
                correct += 1
                if verbose:
                    self.stdout.write(f'  [ok]   {task_name}  queue={intended}')
                continue

            updated += 1
            label = db_queue or 'NULL'
            self.stdout.write(f'  {label:20s} -> {intended:15s} | {task_name}')
            if apply:
                pt.queue = intended
                pt.save(update_fields=['queue'])

        self.stdout.write(f'\n{"=" * 60}')
        self.stdout.write(
            f'Updated: {updated}  |  Already correct: {correct}  |  '
            f'No route (skipped): {unmatched}'
        )
        if not apply and updated:
            self.stdout.write('Run with --apply to persist changes.')
        self.stdout.write(f'{"=" * 60}\n')
