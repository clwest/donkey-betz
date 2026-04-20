"""
Sync celery.py beat_schedule to database scheduler.
Run with: python manage.py shell < sync_celery_schedules.py

Session 801: Updated to include args parameter for tasks that need it.
"""
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
import re
import json

# Read celery.py
with open('core/celery.py', 'r') as f:
    content = f.read()

# Get existing tasks
existing = set(PeriodicTask.objects.values_list('name', flat=True))
print(f"Existing tasks in DB: {len(existing)}")

# Find task definitions - simplified regex
# Pattern: 'task-name': { 'task': 'module.task', 'schedule': ... }
blocks = re.split(r"\n    '([a-z0-9-]+)':\s*\{", content)

added = 0
skipped = 0
errors = []

for i in range(1, len(blocks), 2):
    if i+1 >= len(blocks):
        break

    name = blocks[i]
    block = blocks[i+1]

    if name in existing:
        skipped += 1
        continue

    # Extract task
    task_match = re.search(r"'task':\s*'([^']+)'", block)
    if not task_match:
        continue
    task = task_match.group(1)

    # Extract schedule
    schedule_match = re.search(r"'schedule':\s*([^,\n]+)", block)
    if not schedule_match:
        continue
    schedule_str = schedule_match.group(1).strip()

    # Session 801: Extract args parameter if present
    args_match = re.search(r"'args':\s*\(([^)]+)\)", block)
    args_json = '[]'
    if args_match:
        # Parse tuple like ('media',) -> ["media"]
        args_str = args_match.group(1).strip()
        # Remove quotes and trailing comma, convert to list
        args_list = [a.strip().strip("'\"") for a in args_str.split(',') if a.strip() and a.strip() != ',']
        args_json = json.dumps(args_list)

    try:
        if 'crontab' in schedule_str:
            # Parse crontab parameters
            minute = '0'
            hour = '*'
            dow = '*'
            dom = '*'
            moy = '*'

            m = re.search(r"minute='?([^'`,\)]+)", schedule_str)
            if m: minute = m.group(1).strip()

            m = re.search(r"hour='?([^'`,\)]+)", schedule_str)
            if m: hour = m.group(1).strip()

            m = re.search(r"day_of_week='?([^'`,\)]+)", schedule_str)
            if m: dow = m.group(1).strip()

            m = re.search(r"day_of_month='?([^'`,\)]+)", schedule_str)
            if m: dom = m.group(1).strip()

            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=dow,
                day_of_month=dom,
                month_of_year=moy,
                timezone='UTC'
            )

            PeriodicTask.objects.create(
                name=name,
                task=task,
                crontab=schedule,
                args=args_json,  # Session 801: Include args
                enabled=True
            )
            added += 1
            args_info = f" args={args_json}" if args_json != '[]' else ""
            print(f"  + {name} (crontab: {minute} {hour} * * {dow}){args_info}")

        elif re.match(r'^\d+\.?\d*$', schedule_str):
            # Interval in seconds
            seconds = int(float(schedule_str))
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=seconds,
                period=IntervalSchedule.SECONDS
            )

            PeriodicTask.objects.create(
                name=name,
                task=task,
                interval=schedule,
                args=args_json,  # Session 801: Include args
                enabled=True
            )
            added += 1
            args_info = f" args={args_json}" if args_json != '[]' else ""
            print(f"  + {name} (every {seconds}s){args_info}")

    except Exception as e:
        errors.append(f"{name}: {str(e)[:80]}")

print(f"\n{'='*50}")
print(f"Added: {added}")
print(f"Skipped (exist): {skipped}")
print(f"Errors: {len(errors)}")
for e in errors[:10]:
    print(f"  ! {e}")
