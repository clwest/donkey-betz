"""
Materialize/repair django-celery-beat PeriodicTask rows from the
canonical schedule defined in `core/celery.py`.

**Session 1157 refactor (option A — code-first single source of truth):**

The Celery beat schedule is defined in `core/celery.py` (the
`app.conf.beat_schedule` dict). This command's job is to ensure the
django-celery-beat database (`PeriodicTask` + `IntervalSchedule` +
`CrontabSchedule` tables) holds rows that match that canonical
definition. It does NOT define scheduling semantics of its own.

Historical note: this file previously carried its own ~100-entry
`CRITICAL_TASKS` dict that pre-dated the Session 1077 "minimal mode"
migration in `core/celery.py`. Running the old version would
re-enable ~100 tasks that conserve-mode had intentionally disabled
for API-token budget reasons (context-kit `celery-beat-schedule`
CONFLICT, surfaced Session 1149). The dict has been removed; this
command now reads `app.conf.beat_schedule` directly and is therefore
always in sync with whatever the canonical source declares.

Usage:
    python manage.py add_critical_celery_tasks           # Materialize all
    python manage.py add_critical_celery_tasks --dry-run # Preview only
    python manage.py add_critical_celery_tasks --force   # Overwrite existing
"""

import json
import logging

from celery.schedules import crontab as CrontabSpec
from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
)

logger = logging.getLogger(__name__)


def _coerce_crontab_field(value):
    """Translate a `celery.schedules.crontab` field back to the original
    spec string that `django-celery-beat.CrontabSchedule` expects.

    `celery.schedules.crontab` stores the original input string on
    `_orig_{minute,hour,day_of_week,day_of_month,month_of_year}` —
    that's what `django-celery-beat` itself uses internally when it
    builds the celery-side schedule from a `CrontabSchedule` row. We
    reuse the same attribute so the round-trip is exact.
    """
    return str(value) if value is not None else '*'


def _translate_schedule_entry(name, entry):
    """Translate a single `app.conf.beat_schedule` entry into the
    shape this command's `handle()` expects.

    Returns a dict with:
      - 'task': dotted task path (required)
      - 'queue': queue name (default 'default')
      - 'args': list (default [])
      - 'kwargs': dict (default {})
      - exactly one of:
          - 'interval': seconds (int) — for numeric schedules
          - 'crontab': dict of crontab kwargs — for crontab schedules

    Raises `ValueError` if the entry is missing a task or has an
    unrecognized schedule type.
    """
    task = entry.get('task')
    if not task:
        raise ValueError(f"beat_schedule entry {name!r} missing 'task' key")

    options = entry.get('options', {}) or {}
    out = {
        'task': task,
        'queue': options.get('queue', 'default'),
        'args': list(entry.get('args', [])),
        'kwargs': dict(entry.get('kwargs', {})),
    }

    schedule = entry.get('schedule')
    if schedule is None:
        raise ValueError(f"beat_schedule entry {name!r} missing 'schedule' key")

    if isinstance(schedule, (int, float)):
        out['interval'] = int(schedule)
    elif isinstance(schedule, CrontabSpec):
        out['crontab'] = {
            'minute': _coerce_crontab_field(getattr(schedule, '_orig_minute', '*')),
            'hour': _coerce_crontab_field(getattr(schedule, '_orig_hour', '*')),
            'day_of_week': _coerce_crontab_field(getattr(schedule, '_orig_day_of_week', '*')),
            'day_of_month': _coerce_crontab_field(getattr(schedule, '_orig_day_of_month', '*')),
            'month_of_year': _coerce_crontab_field(getattr(schedule, '_orig_month_of_year', '*')),
        }
    else:
        raise ValueError(
            f"beat_schedule entry {name!r} has unsupported schedule type "
            f"{type(schedule).__name__}; expected int seconds or "
            f"celery.schedules.crontab"
        )

    return out


def _load_canonical_schedule():
    """Read the canonical beat schedule from `core/celery.py`.

    Returns a dict of `{name: translated_entry}` ready for materialize.
    Done as a function (not module-top import) to avoid side effects at
    Django command discovery time.
    """
    from core.celery import app

    translated = {}
    errors = []
    for name, entry in app.conf.beat_schedule.items():
        try:
            translated[name] = _translate_schedule_entry(name, entry)
        except ValueError as e:
            errors.append(str(e))
    return translated, errors


class Command(BaseCommand):
    help = (
        'Materialize/repair django-celery-beat PeriodicTask rows from '
        'the canonical schedule in core/celery.py. This command does '
        'not define schedule semantics — it reads them.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be added/updated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing PeriodicTask rows that already match by name',
        )

    def get_or_create_interval(self, seconds):
        """Get or create an interval schedule."""
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=seconds,
            period=IntervalSchedule.SECONDS,
        )
        return interval

    def get_or_create_crontab(self, crontab_args):
        """Get or create a crontab schedule (handles duplicate entries)."""
        defaults = {
            'minute': '*',
            'hour': '*',
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*',
        }
        defaults.update(crontab_args)

        existing = CrontabSchedule.objects.filter(**defaults).first()
        if existing:
            return existing
        return CrontabSchedule.objects.create(**defaults)

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(
            "Materialize Celery Beat schedule from core/celery.py "
            "(canonical source)"
        )
        self.stdout.write(f"{'=' * 60}\n")

        canonical, translate_errors = _load_canonical_schedule()
        if translate_errors:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠ {len(translate_errors)} entry(s) in core/celery.py "
                    f"could not be translated; they will be skipped:"
                )
            )
            for msg in translate_errors:
                self.stdout.write(f"      - {msg}")
            self.stdout.write("")

        existing = set(PeriodicTask.objects.values_list('name', flat=True))
        self.stdout.write(f"Existing PeriodicTask rows in database: {len(existing)}")
        self.stdout.write(
            f"Canonical schedule entries in core/celery.py: {len(canonical)}"
        )

        created = 0
        updated = 0
        skipped = 0
        errors = []

        for name, config in canonical.items():
            task_name = config['task']
            queue = config['queue']

            if name in existing and not force:
                skipped += 1
                continue

            if dry_run:
                action = "Would update" if name in existing else "Would create"
                self.stdout.write(f"  [DRY RUN] {action}: {name}")
                continue

            try:
                if 'interval' in config:
                    interval = self.get_or_create_interval(config['interval'])
                    task, task_created = PeriodicTask.objects.update_or_create(
                        name=name,
                        defaults={
                            'task': task_name,
                            'interval': interval,
                            'crontab': None,
                            'args': json.dumps(config['args']),
                            'kwargs': json.dumps(config['kwargs']),
                            'queue': queue,
                            'enabled': True,
                        },
                    )
                else:
                    crontab = self.get_or_create_crontab(config['crontab'])
                    task, task_created = PeriodicTask.objects.update_or_create(
                        name=name,
                        defaults={
                            'task': task_name,
                            'crontab': crontab,
                            'interval': None,
                            'args': json.dumps(config['args']),
                            'kwargs': json.dumps(config['kwargs']),
                            'queue': queue,
                            'enabled': True,
                        },
                    )

                if task_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {name}"))
                else:
                    updated += 1
                    self.stdout.write(f"  ↻ Updated: {name}")

            except Exception as e:
                logger.exception(
                    "[CELERY_SYNC] Failed to materialize beat entry %s", name
                )
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ Error with {name}: {type(e).__name__}: {e}"
                    )
                )
                errors.append(f"{name}: {type(e).__name__}: {e}")

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write("SUMMARY")
        self.stdout.write(f"{'=' * 60}")

        if dry_run:
            to_create = len(canonical) - skipped
            self.stdout.write(
                f"Would create/update: {to_create} task(s) "
                f"(use --force to overwrite already-present rows)"
            )
            self.stdout.write(f"Would skip (already exist): {skipped} task(s)")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created: {created} task(s)"))
            self.stdout.write(f"Updated: {updated} task(s)")
            self.stdout.write(f"Skipped (already exist): {skipped} task(s)")

            final_count = PeriodicTask.objects.filter(enabled=True).count()
            self.stdout.write(
                f"\nTotal enabled PeriodicTask rows in database: {final_count}"
            )
            if errors:
                raise CommandError(
                    f"Failed to materialize {len(errors)} task(s); "
                    f"see logs for tracebacks"
                )
