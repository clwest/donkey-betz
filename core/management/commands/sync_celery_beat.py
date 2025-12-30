"""
Session 627: Sync Celery Beat Database with celery.py definitions

The system uses DatabaseScheduler which ignores Python config files at runtime.
This command syncs task definitions from core/celery.py to the database.

Usage:
    python manage.py sync_celery_beat              # Dry run - show what would change
    python manage.py sync_celery_beat --apply      # Apply changes
    python manage.py sync_celery_beat --verbose    # Show all tasks, not just changes
"""

import re
from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule


class Command(BaseCommand):
    help = 'Sync Celery Beat database with core/celery.py task definitions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply changes (default is dry run)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show all tasks, not just changes',
        )
        parser.add_argument(
            '--disable-missing',
            action='store_true',
            help='Disable tasks in DB that are not in celery.py',
        )
        parser.add_argument(
            '--create-only',
            action='store_true',
            help='Only create new tasks, do not update existing schedules',
        )

    def handle(self, *args, **options):
        apply_changes = options['apply']
        verbose = options['verbose']
        disable_missing = options['disable_missing']
        create_only = options['create_only']

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('CELERY BEAT SYNC - Session 627'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        if not apply_changes:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes will be made. Use --apply to apply changes.\n'))

        # Parse celery.py
        celery_tasks = self.parse_celery_py()
        self.stdout.write(f'\nTasks defined in core/celery.py: {len(celery_tasks)}')

        # Get database tasks
        db_tasks = {pt.task: pt for pt in PeriodicTask.objects.all()}
        self.stdout.write(f'Tasks in database: {len(db_tasks)}')

        # Find differences
        to_create = []
        to_update = []
        in_sync = []

        for name, config in celery_tasks.items():
            task_path = config['task']
            if task_path not in db_tasks:
                to_create.append((name, config))
            else:
                # Check if schedule matches
                pt = db_tasks[task_path]
                schedule_matches = self.check_schedule_match(pt, config)
                if schedule_matches:
                    in_sync.append((name, task_path))
                else:
                    to_update.append((name, config, pt))

        # Find tasks in DB but not in celery.py
        celery_task_paths = {c['task'] for c in celery_tasks.values()}
        orphaned = [(pt.name, pt) for pt in db_tasks.values()
                    if pt.task not in celery_task_paths and pt.enabled]

        # Report
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS('SYNC REPORT'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}\n'))

        # Tasks to create
        if to_create:
            self.stdout.write(self.style.WARNING(f'Tasks to CREATE ({len(to_create)}):'))
            for name, config in to_create:
                schedule_str = self.format_schedule(config)
                self.stdout.write(f'  + {name}')
                self.stdout.write(f'    Task: {config["task"]}')
                self.stdout.write(f'    Schedule: {schedule_str}')

                if apply_changes:
                    self.create_task(name, config)
                    self.stdout.write(self.style.SUCCESS(f'    ✅ Created'))
            self.stdout.write('')

        # Tasks to update
        if to_update:
            if create_only:
                self.stdout.write(self.style.NOTICE(f'Tasks with different schedules ({len(to_update)}): (skipped due to --create-only)'))
                for name, config, pt in to_update[:5]:
                    old_schedule = str(pt.crontab or pt.interval)
                    new_schedule = self.format_schedule(config)
                    self.stdout.write(f'  ~ {name}: {old_schedule} vs {new_schedule}')
                if len(to_update) > 5:
                    self.stdout.write(f'  ... and {len(to_update) - 5} more')
            else:
                self.stdout.write(self.style.WARNING(f'Tasks to UPDATE ({len(to_update)}):'))
                for name, config, pt in to_update:
                    old_schedule = str(pt.crontab or pt.interval)
                    new_schedule = self.format_schedule(config)
                    self.stdout.write(f'  ~ {name}')
                    self.stdout.write(f'    Old: {old_schedule}')
                    self.stdout.write(f'    New: {new_schedule}')

                    if apply_changes:
                        self.update_task(pt, config)
                        self.stdout.write(self.style.SUCCESS(f'    ✅ Updated'))
            self.stdout.write('')

        # Orphaned tasks
        if orphaned:
            self.stdout.write(self.style.WARNING(f'Tasks in DB but NOT in celery.py ({len(orphaned)}):'))
            for name, pt in orphaned[:20]:  # Show first 20
                self.stdout.write(f'  ? {name}: {pt.task}')
                if disable_missing and apply_changes:
                    pt.enabled = False
                    pt.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✅ Disabled'))
            if len(orphaned) > 20:
                self.stdout.write(f'  ... and {len(orphaned) - 20} more')
            if not disable_missing:
                self.stdout.write(self.style.NOTICE('    (Use --disable-missing to disable these)'))
            self.stdout.write('')

        # In sync
        if verbose and in_sync:
            self.stdout.write(self.style.SUCCESS(f'Tasks already in sync ({len(in_sync)}):'))
            for name, task_path in in_sync:
                self.stdout.write(f'  ✓ {name}')
            self.stdout.write('')

        # Summary
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 70}'))
        self.stdout.write(f'  To create: {len(to_create)}')
        if create_only:
            self.stdout.write(f'  Different: {len(to_update)} (skipped)')
        else:
            self.stdout.write(f'  To update: {len(to_update)}')
        self.stdout.write(f'  Orphaned:  {len(orphaned)}')
        self.stdout.write(f'  In sync:   {len(in_sync)}')

        if apply_changes:
            self.stdout.write(self.style.SUCCESS(f'\n✅ Changes applied successfully!'))
            new_total = PeriodicTask.objects.filter(enabled=True).count()
            self.stdout.write(f'   Total enabled tasks: {new_total}')
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Dry run complete. Use --apply to make changes.'))

    def parse_celery_py(self):
        """Parse core/celery.py and extract task definitions."""
        with open('core/celery.py', 'r') as f:
            content = f.read()

        tasks = {}

        # Find task blocks using regex
        # Pattern matches: 'task-name': { 'task': 'path', 'schedule': ... }
        pattern = r"'([a-z][a-z0-9-]+)'\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}"

        for match in re.finditer(pattern, content, re.DOTALL):
            name = match.group(1)
            block = match.group(2)

            # Extract task path
            task_match = re.search(r"'task'\s*:\s*'([^']+)'", block)
            if not task_match:
                continue
            task_path = task_match.group(1)

            # Extract schedule
            schedule_config = self.parse_schedule(block)
            if not schedule_config:
                continue

            tasks[name] = {
                'task': task_path,
                'schedule': schedule_config,
            }

            # Extract kwargs if present
            kwargs_match = re.search(r"'kwargs'\s*:\s*(\{[^}]+\})", block)
            if kwargs_match:
                tasks[name]['kwargs'] = kwargs_match.group(1)

        return tasks

    def parse_schedule(self, block):
        """Parse schedule from task block."""
        # Check for crontab
        crontab_match = re.search(
            r"'schedule'\s*:\s*crontab\(([^)]+)\)",
            block
        )
        if crontab_match:
            args = crontab_match.group(1)
            return {'type': 'crontab', 'args': self.parse_crontab_args(args)}

        # Check for timedelta/interval
        interval_match = re.search(
            r"'schedule'\s*:\s*timedelta\(([^)]+)\)",
            block
        )
        if interval_match:
            args = interval_match.group(1)
            return {'type': 'interval', 'args': self.parse_interval_args(args)}

        # Check for numeric interval (seconds)
        numeric_match = re.search(
            r"'schedule'\s*:\s*(\d+\.?\d*)",
            block
        )
        if numeric_match:
            seconds = float(numeric_match.group(1))
            return {'type': 'interval', 'args': {'seconds': int(seconds)}}

        return None

    def parse_crontab_args(self, args_str):
        """Parse crontab arguments."""
        result = {
            'minute': '*',
            'hour': '*',
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*',
        }

        # Parse key=value pairs
        for match in re.finditer(r"(\w+)\s*=\s*['\"]?([^,'\"]+)['\"]?", args_str):
            key = match.group(1)
            value = match.group(2).strip()
            if key in result:
                result[key] = value

        return result

    def parse_interval_args(self, args_str):
        """Parse timedelta/interval arguments."""
        result = {}

        for match in re.finditer(r"(\w+)\s*=\s*(\d+)", args_str):
            key = match.group(1)
            value = int(match.group(2))
            result[key] = value

        return result

    def format_schedule(self, config):
        """Format schedule for display."""
        schedule = config['schedule']
        if schedule['type'] == 'crontab':
            args = schedule['args']
            return f"crontab({args['minute']} {args['hour']} {args['day_of_month']} {args['month_of_year']} {args['day_of_week']})"
        else:
            args = schedule['args']
            if 'seconds' in args:
                return f"every {args['seconds']} seconds"
            elif 'minutes' in args:
                return f"every {args['minutes']} minutes"
            elif 'hours' in args:
                return f"every {args['hours']} hours"
            return f"interval({args})"

    def check_schedule_match(self, pt, config):
        """Check if database task schedule matches config."""
        schedule = config['schedule']

        if schedule['type'] == 'crontab' and pt.crontab:
            args = schedule['args']
            return (
                str(pt.crontab.minute) == str(args['minute']) and
                str(pt.crontab.hour) == str(args['hour']) and
                str(pt.crontab.day_of_week) == str(args['day_of_week']) and
                str(pt.crontab.day_of_month) == str(args['day_of_month']) and
                str(pt.crontab.month_of_year) == str(args['month_of_year'])
            )
        elif schedule['type'] == 'interval' and pt.interval:
            args = schedule['args']
            total_seconds = args.get('seconds', 0) + args.get('minutes', 0) * 60 + args.get('hours', 0) * 3600

            if pt.interval.period == IntervalSchedule.SECONDS:
                return pt.interval.every == total_seconds
            elif pt.interval.period == IntervalSchedule.MINUTES:
                return pt.interval.every * 60 == total_seconds
            elif pt.interval.period == IntervalSchedule.HOURS:
                return pt.interval.every * 3600 == total_seconds

        return False

    def create_task(self, name, config):
        """Create a new periodic task."""
        schedule = config['schedule']

        if schedule['type'] == 'crontab':
            args = schedule['args']
            cron = CrontabSchedule.objects.filter(
                minute=args['minute'],
                hour=args['hour'],
                day_of_week=args['day_of_week'],
                day_of_month=args['day_of_month'],
                month_of_year=args['month_of_year'],
            ).first()

            if not cron:
                cron = CrontabSchedule.objects.create(
                    minute=args['minute'],
                    hour=args['hour'],
                    day_of_week=args['day_of_week'],
                    day_of_month=args['day_of_month'],
                    month_of_year=args['month_of_year'],
                )

            PeriodicTask.objects.create(
                name=name,
                task=config['task'],
                crontab=cron,
                enabled=True,
            )
        else:
            args = schedule['args']
            total_seconds = args.get('seconds', 0) + args.get('minutes', 0) * 60 + args.get('hours', 0) * 3600

            # Choose appropriate period
            if total_seconds >= 3600 and total_seconds % 3600 == 0:
                period = IntervalSchedule.HOURS
                every = total_seconds // 3600
            elif total_seconds >= 60 and total_seconds % 60 == 0:
                period = IntervalSchedule.MINUTES
                every = total_seconds // 60
            else:
                period = IntervalSchedule.SECONDS
                every = total_seconds

            interval = IntervalSchedule.objects.filter(
                every=every,
                period=period,
            ).first()

            if not interval:
                interval = IntervalSchedule.objects.create(
                    every=every,
                    period=period,
                )

            PeriodicTask.objects.create(
                name=name,
                task=config['task'],
                interval=interval,
                enabled=True,
            )

    def update_task(self, pt, config):
        """Update an existing periodic task's schedule."""
        schedule = config['schedule']

        if schedule['type'] == 'crontab':
            args = schedule['args']
            cron = CrontabSchedule.objects.filter(
                minute=args['minute'],
                hour=args['hour'],
                day_of_week=args['day_of_week'],
                day_of_month=args['day_of_month'],
                month_of_year=args['month_of_year'],
            ).first()

            if not cron:
                cron = CrontabSchedule.objects.create(
                    minute=args['minute'],
                    hour=args['hour'],
                    day_of_week=args['day_of_week'],
                    day_of_month=args['day_of_month'],
                    month_of_year=args['month_of_year'],
                )

            pt.crontab = cron
            pt.interval = None
            pt.save()
        else:
            args = schedule['args']
            total_seconds = args.get('seconds', 0) + args.get('minutes', 0) * 60 + args.get('hours', 0) * 3600

            if total_seconds >= 3600 and total_seconds % 3600 == 0:
                period = IntervalSchedule.HOURS
                every = total_seconds // 3600
            elif total_seconds >= 60 and total_seconds % 60 == 0:
                period = IntervalSchedule.MINUTES
                every = total_seconds // 60
            else:
                period = IntervalSchedule.SECONDS
                every = total_seconds

            interval = IntervalSchedule.objects.filter(
                every=every,
                period=period,
            ).first()

            if not interval:
                interval = IntervalSchedule.objects.create(
                    every=every,
                    period=period,
                )

            pt.interval = interval
            pt.crontab = None
            pt.save()
