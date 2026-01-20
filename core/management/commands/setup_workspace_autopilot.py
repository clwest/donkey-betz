"""
Session 785: Setup Workspace Autopilot

Management command to:
1. Create the PeriodicTask for workspace_autopilot_tick in Celery Beat DB
2. Seed default WorkspaceTriggerConfig rules

Usage:
    python manage.py setup_workspace_autopilot
    python manage.py setup_workspace_autopilot --interval=300  # Every 5 minutes
    python manage.py setup_workspace_autopilot --seed-configs  # Also seed default configs
    python manage.py setup_workspace_autopilot --dry-run  # Preview without changes
"""

import json
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Setup the Workspace Autopilot conductor task in Celery Beat database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,  # 5 minutes
            help='Interval in seconds between conductor ticks (default: 300 = 5 minutes)'
        )
        parser.add_argument(
            '--budget',
            type=int,
            default=5,
            help='Maximum triggers to process per tick (default: 5)'
        )
        parser.add_argument(
            '--seed-configs',
            action='store_true',
            help='Also seed default WorkspaceTriggerConfig rules'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without making changes'
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable the autopilot task instead of enabling it'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        budget = options['budget']
        seed_configs = options['seed_configs']
        dry_run = options['dry_run']
        disable = options['disable']

        self.stdout.write(self.style.NOTICE(
            f"🤖 [WORKSPACE AUTOPILOT SETUP] Starting..."
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # 1. Create or update the PeriodicTask
        self._setup_periodic_task(interval, budget, dry_run, disable)

        # 2. Optionally seed default configs
        if seed_configs:
            self._seed_trigger_configs(dry_run)

        self.stdout.write(self.style.SUCCESS(
            f"\n🤖 [WORKSPACE AUTOPILOT SETUP] Complete!"
        ))

    def _setup_periodic_task(self, interval: int, budget: int, dry_run: bool, disable: bool):
        """Create or update the PeriodicTask for workspace_autopilot_tick."""
        from django_celery_beat.models import PeriodicTask, IntervalSchedule

        self.stdout.write(self.style.NOTICE(
            f"\n📅 Setting up PeriodicTask (interval: {interval}s, budget: {budget})"
        ))

        # Create or get the interval schedule
        if not dry_run:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=interval,
                period=IntervalSchedule.SECONDS
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"   ✓ Created IntervalSchedule: every {interval} seconds"
                ))
            else:
                self.stdout.write(f"   • Using existing IntervalSchedule: every {interval} seconds")
        else:
            self.stdout.write(f"   [DRY RUN] Would create IntervalSchedule: every {interval} seconds")
            schedule = None

        # Task name and kwargs
        task_name = 'workspace.autopilot_tick'
        task_kwargs = json.dumps({
            'budget_per_tick': budget,
            'min_priority': None,
            'category': None,
            'dry_run': False
        })

        # Create or update the PeriodicTask
        if not dry_run:
            task, created = PeriodicTask.objects.update_or_create(
                name='Workspace Autopilot Conductor',
                defaults={
                    'task': task_name,
                    'interval': schedule,
                    'kwargs': task_kwargs,
                    'enabled': not disable,
                    'description': (
                        'Session 785: Hybrid workspace autopilot conductor. '
                        'Drains the WorkspaceTrigger queue, routing work items to agents. '
                        f'Processes up to {budget} triggers per tick.'
                    )
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"   ✓ Created PeriodicTask: 'Workspace Autopilot Conductor'"
                ))
            else:
                self.stdout.write(f"   ✓ Updated PeriodicTask: 'Workspace Autopilot Conductor'")

            status = "DISABLED" if disable else "ENABLED"
            self.stdout.write(self.style.SUCCESS(f"   ✓ Task status: {status}"))
        else:
            action = "disable" if disable else "enable"
            self.stdout.write(
                f"   [DRY RUN] Would {action} PeriodicTask: 'Workspace Autopilot Conductor'\n"
                f"   [DRY RUN] Task: {task_name}\n"
                f"   [DRY RUN] Kwargs: {task_kwargs}"
            )

    def _seed_trigger_configs(self, dry_run: bool):
        """Seed default WorkspaceTriggerConfig rules."""
        from core.models_skin_layer import WorkspaceTriggerConfig, DEFAULT_WORKSPACE_TRIGGER_CONFIGS

        self.stdout.write(self.style.NOTICE(
            f"\n🌱 Seeding {len(DEFAULT_WORKSPACE_TRIGGER_CONFIGS)} default WorkspaceTriggerConfig rules"
        ))

        created_count = 0
        skipped_count = 0

        for config_data in DEFAULT_WORKSPACE_TRIGGER_CONFIGS:
            name = config_data['name']

            if not dry_run:
                # Check if already exists
                existing = WorkspaceTriggerConfig.objects.filter(name=name).first()
                if existing:
                    self.stdout.write(f"   • Skipping '{name}' (already exists)")
                    skipped_count += 1
                    continue

                # Create new config
                WorkspaceTriggerConfig.objects.create(**config_data)
                self.stdout.write(self.style.SUCCESS(f"   ✓ Created '{name}'"))
                created_count += 1
            else:
                self.stdout.write(f"   [DRY RUN] Would create '{name}'")
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n   Summary: {created_count} created, {skipped_count} skipped"
        ))
