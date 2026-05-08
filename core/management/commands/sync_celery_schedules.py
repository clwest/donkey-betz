"""
Session 810: Sync Celery Beat Schedules from celery.py to Database

This command addresses the critical issue where settings.py CELERY_BEAT_SCHEDULE
completely overrides celery.py's app.conf.beat_schedule when using DatabaseScheduler.

The problem: 187 tasks defined in celery.py were NOT running because they weren't
in settings.py. This includes ALL body system health checks, agent rotations,
autonomous situations, dream processing, learning pipelines, and more.

Usage:
    python manage.py sync_celery_schedules           # Sync all missing tasks
    python manage.py sync_celery_schedules --dry-run # Preview changes
    python manage.py sync_celery_schedules --list    # List missing tasks
    python manage.py sync_celery_schedules --source=celery  # Read from celery.py directly
"""

import json
import os
import re
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from celery.schedules import crontab

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync Celery Beat schedules from celery.py to DatabaseScheduler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all missing tasks'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing tasks with celery.py versions'
        )
        parser.add_argument(
            '--source',
            choices=['celery', 'settings', 'both'],
            default='celery',
            help='Source of schedules: celery (raw file), settings (Django), both'
        )

    def _parse_celery_py_schedules(self):
        """Parse beat_schedule directly from celery.py file (bypass config override)"""
        import ast

        celery_path = os.path.join(os.path.dirname(__file__), '..', '..', 'celery.py')
        celery_path = os.path.abspath(celery_path)

        with open(celery_path, 'r') as f:
            content = f.read()

        # Find app.conf.beat_schedule = { ... }
        # We need to extract just the task names and their configs
        schedules = {}

        # Pattern to find task entries: 'task-name': { 'task': '...'
        pattern = r"'([^']+)':\s*\{\s*'task':\s*'([^']+)'"

        matches = re.findall(pattern, content)
        for name, task in matches:
            # Skip if not in beat_schedule section (check context)
            schedules[name] = {'task': task, 'name': name}

        # Now extract schedule details for each task
        for name in list(schedules.keys()):
            # Find the full config block for this task
            task_pattern = rf"'{re.escape(name)}':\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}}"
            match = re.search(task_pattern, content)
            if match:
                config_text = match.group(1)

                # Parse schedule
                if "'schedule': crontab(" in config_text:
                    cron_match = re.search(r"crontab\(([^)]+)\)", config_text)
                    if cron_match:
                        schedules[name]['schedule_type'] = 'crontab'
                        schedules[name]['crontab_args'] = cron_match.group(1)
                elif "'schedule':" in config_text:
                    # Interval schedule (seconds)
                    interval_match = re.search(r"'schedule':\s*([\d.]+)", config_text)
                    if interval_match:
                        schedules[name]['schedule_type'] = 'interval'
                        schedules[name]['interval_seconds'] = float(interval_match.group(1))

                # Parse args
                args_match = re.search(r"'args':\s*\(([^)]*)\)", config_text)
                if args_match:
                    schedules[name]['args'] = args_match.group(1)

                # Parse kwargs
                kwargs_match = re.search(r"'kwargs':\s*\{([^}]*)\}", config_text)
                if kwargs_match:
                    schedules[name]['kwargs'] = kwargs_match.group(1)

        return schedules

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        list_only = options['list']
        force = options['force']
        source = options['source']

        # Get schedules based on source
        if source in ('celery', 'both'):
            celery_schedule = self._parse_celery_py_schedules()
            self.stdout.write(f"Parsed {len(celery_schedule)} tasks from celery.py file")
        else:
            from core.celery import app
            celery_schedule = app.conf.beat_schedule or {}

        # Get existing tasks from database
        existing_tasks = set(PeriodicTask.objects.values_list('name', flat=True))

        # Find missing tasks
        missing_tasks = {
            name: config
            for name, config in celery_schedule.items()
            if name not in existing_tasks
        }

        if list_only:
            self.stdout.write(f"\n=== CELERY BEAT SCHEDULE SYNC STATUS ===\n")
            self.stdout.write(f"Tasks in celery.py: {len(celery_schedule)}")
            self.stdout.write(f"Tasks in database: {len(existing_tasks)}")
            self.stdout.write(f"Missing from database: {len(missing_tasks)}")

            if missing_tasks:
                self.stdout.write(f"\n=== Missing Tasks (to be synced) ===")
                for name in sorted(missing_tasks.keys()):
                    config = missing_tasks[name]
                    task = config.get('task', 'unknown')
                    self.stdout.write(f"  - {name}: {task}")
            return

        if not missing_tasks and not force:
            self.stdout.write(self.style.SUCCESS(
                "All tasks already synced! No action needed."
            ))
            return

        self.stdout.write(f"\n=== Syncing {len(missing_tasks)} tasks to database ===\n")

        created = 0
        updated = 0
        errors = []

        for name, config in missing_tasks.items():
            task_name = config.get('task')
            schedule = config.get('schedule')

            if not task_name:
                errors.append(f"{name}: No task defined")
                continue

            try:
                # Determine schedule type
                schedule_obj = None

                if isinstance(schedule, (int, float)):
                    # Interval schedule (seconds)
                    if dry_run:
                        self.stdout.write(f"  [DRY RUN] {name}: interval every {schedule}s")
                    else:
                        interval, _ = IntervalSchedule.objects.get_or_create(
                            every=int(schedule),
                            period=IntervalSchedule.SECONDS
                        )
                        task, task_created = PeriodicTask.objects.update_or_create(
                            name=name,
                            defaults={
                                'task': task_name,
                                'interval': interval,
                                'crontab': None,
                                'args': json.dumps(config.get('args', [])),
                                'kwargs': json.dumps(config.get('kwargs', {})),
                                'enabled': True,
                            }
                        )
                        if task_created:
                            created += 1
                            self.stdout.write(f"  ✓ Created {name}")
                        else:
                            updated += 1
                            self.stdout.write(f"  ↻ Updated {name}")

                elif hasattr(schedule, 'minute'):
                    # Crontab schedule
                    minute = schedule._orig_minute if hasattr(schedule, '_orig_minute') else str(schedule.minute) if hasattr(schedule.minute, '__iter__') else str(schedule.minute)
                    hour = schedule._orig_hour if hasattr(schedule, '_orig_hour') else str(schedule.hour) if hasattr(schedule.hour, '__iter__') else str(schedule.hour)
                    day_of_week = schedule._orig_day_of_week if hasattr(schedule, '_orig_day_of_week') else str(schedule.day_of_week) if hasattr(schedule.day_of_week, '__iter__') else str(schedule.day_of_week)
                    day_of_month = schedule._orig_day_of_month if hasattr(schedule, '_orig_day_of_month') else str(schedule.day_of_month) if hasattr(schedule.day_of_month, '__iter__') else str(schedule.day_of_month)
                    month_of_year = schedule._orig_month_of_year if hasattr(schedule, '_orig_month_of_year') else str(schedule.month_of_year) if hasattr(schedule.month_of_year, '__iter__') else str(schedule.month_of_year)

                    # Convert set representations to crontab strings
                    def set_to_crontab(val):
                        if isinstance(val, set):
                            return ','.join(str(v) for v in sorted(val))
                        return str(val).replace('{', '').replace('}', '').replace(' ', '')

                    minute = set_to_crontab(minute)
                    hour = set_to_crontab(hour)
                    day_of_week = set_to_crontab(day_of_week)
                    day_of_month = set_to_crontab(day_of_month)
                    month_of_year = set_to_crontab(month_of_year)

                    if dry_run:
                        self.stdout.write(f"  [DRY RUN] {name}: crontab {minute} {hour} * * {day_of_week}")
                    else:
                        crontab, _ = CrontabSchedule.objects.get_or_create(
                            minute=minute,
                            hour=hour,
                            day_of_week=day_of_week,
                            day_of_month=day_of_month,
                            month_of_year=month_of_year,
                        )
                        task, task_created = PeriodicTask.objects.update_or_create(
                            name=name,
                            defaults={
                                'task': task_name,
                                'crontab': crontab,
                                'interval': None,
                                'args': json.dumps(config.get('args', [])),
                                'kwargs': json.dumps(config.get('kwargs', {})),
                                'enabled': True,
                            }
                        )
                        if task_created:
                            created += 1
                            self.stdout.write(f"  ✓ Created {name}")
                        else:
                            updated += 1
                            self.stdout.write(f"  ↻ Updated {name}")
                else:
                    errors.append(f"{name}: Unknown schedule type: {type(schedule)}")

            except Exception as e:
                logger.exception("[CELERY_SYNC] Failed to sync %s", name)
                errors.append(f"{name}: {type(e).__name__}: {str(e)}")

        # Summary
        self.stdout.write(f"\n=== Summary ===")
        if dry_run:
            self.stdout.write(f"Would create: {len(missing_tasks)} tasks")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created: {created} tasks"))
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated} tasks"))

        if errors:
            self.stdout.write(self.style.WARNING(f"\nErrors ({len(errors)}):"))
            for error in errors:
                self.stdout.write(self.style.WARNING(f"  - {error}"))
            if not dry_run:
                raise CommandError(
                    f"Failed to sync {len(errors)} Celery schedule(s); "
                    f"see logs for tracebacks"
                )

        # Final count
        if not dry_run:
            final_count = PeriodicTask.objects.filter(enabled=True).count()
            self.stdout.write(f"\nTotal active tasks in database: {final_count}")
