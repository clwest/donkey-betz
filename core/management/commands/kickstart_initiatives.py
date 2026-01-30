"""
Kickstart Stuck Initiatives
============================

Session 884: Dispatches Stage 1 tasks for Initiatives that are stuck at 0%.

Many Initiatives were created by the old system but never had tasks dispatched.
This command finds them and kicks off their Stage 1 work.

Usage:
    # Preview what would be kickstarted
    python manage.py kickstart_initiatives --dry-run

    # Kickstart all stuck initiatives
    python manage.py kickstart_initiatives

    # Limit to N initiatives
    python manage.py kickstart_initiatives --limit=10

    # Kickstart a specific initiative
    python manage.py kickstart_initiatives --id=<uuid>
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Kickstart stuck Initiatives by dispatching Stage 1 tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview without making changes'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of initiatives to process'
        )
        parser.add_argument(
            '--id',
            type=str,
            default=None,
            help='Kickstart a specific initiative by ID'
        )
        parser.add_argument(
            '--include-completed',
            action='store_true',
            help='Include initiatives that might have some progress'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage
        from core.services.conversation_initiative_pipeline import (
            CONTENT_TYPE_STAGES,
            _dispatch_next_stage_tasks,
        )
        from core.tasks import execute_initiative_stage_task

        dry_run = options['dry_run']
        limit = options['limit']
        specific_id = options['id']
        include_completed = options['include_completed']

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("KICKSTART STUCK INITIATIVES - Session 884"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - No tasks will be dispatched\n"))

        # Find stuck initiatives
        if specific_id:
            initiatives = Initiative.objects.filter(id=specific_id)
        else:
            # Find initiatives at Stage 1 with status ACTIVE
            initiatives = Initiative.objects.filter(
                status='ACTIVE',
                current_stage=1,
            )

            if not include_completed:
                # Only get those with 0% progress (no documents)
                initiatives = [
                    i for i in initiatives
                    if i.stages_with_work == 0
                ]
            else:
                initiatives = list(initiatives)

        if limit:
            initiatives = initiatives[:limit]

        self.stdout.write(f"\nFound {len(initiatives)} stuck initiatives\n")

        if not initiatives:
            self.stdout.write(self.style.SUCCESS("No stuck initiatives to process!"))
            return

        kickstarted = 0
        errors = []

        for initiative in initiatives:
            self.stdout.write(f"\n{'─' * 50}")
            self.stdout.write(f"Initiative: {initiative.name[:60]}...")
            self.stdout.write(f"  ID: {initiative.id}")
            self.stdout.write(f"  Stage: {initiative.current_stage}/5")
            self.stdout.write(f"  Progress: {initiative.completion_percentage}%")

            # Get topic from initiative
            topic = initiative.parent_topic or initiative.name

            # Determine content type (default to 'strategy' for most)
            content_type = self._detect_content_type(topic)
            self.stdout.write(f"  Content Type: {content_type}")

            # Get stage 1 tasks
            stage_config = CONTENT_TYPE_STAGES.get(content_type, CONTENT_TYPE_STAGES['document'])
            stage_1_info = stage_config.get(1, {'name': 'Stage 1', 'tasks': []})
            tasks = stage_1_info.get('tasks', []) if isinstance(stage_1_info, dict) else []

            self.stdout.write(f"  Tasks to dispatch: {len(tasks)}")

            if dry_run:
                for task_config in tasks:
                    task_desc = task_config['task_template'].format(topic=topic[:50])
                    self.stdout.write(f"    [DRY RUN] Would dispatch: {task_config['agent']} - {task_desc[:50]}...")
                continue

            # Actually dispatch tasks
            try:
                # Ensure Stage 1 exists
                stage_1, created = InitiativeStage.objects.get_or_create(
                    initiative=initiative,
                    stage=1,
                    defaults={
                        'status': 'DRAFT',
                        'notes': f'Auto-kickstarted at {timezone.now().isoformat()}',
                    }
                )

                if stage_1.status == 'PENDING':
                    stage_1.status = 'DRAFT'
                    stage_1.save()

                # Dispatch tasks
                task_count = 0
                for task_config in tasks:
                    agent_name = task_config['agent']
                    task_template = task_config['task_template']
                    task_description = task_template.format(topic=topic)

                    try:
                        execute_initiative_stage_task.delay(
                            initiative_id=str(initiative.id),
                            stage_num=1,
                            agent_name=agent_name,
                            task=task_description,
                            context={
                                'source': 'kickstart_initiatives_command',
                                'topic': topic,
                            }
                        )
                        task_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"    ✓ Dispatched: {agent_name}")
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"    ✗ Failed: {agent_name} - {e}")
                        )

                if task_count > 0:
                    kickstarted += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  → Kickstarted with {task_count} tasks")
                    )

            except Exception as e:
                errors.append(f"{initiative.name[:30]}: {e}")
                self.stdout.write(self.style.ERROR(f"  ✗ Error: {e}"))

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.SUCCESS(f"KICKSTART COMPLETE"))
        self.stdout.write(f"  Initiatives processed: {len(initiatives)}")
        self.stdout.write(f"  Successfully kickstarted: {kickstarted}")
        self.stdout.write(f"  Errors: {len(errors)}")

        if errors:
            self.stdout.write(self.style.ERROR("\nErrors:"))
            for error in errors[:10]:
                self.stdout.write(f"  - {error}")

        if not dry_run and kickstarted > 0:
            self.stdout.write(self.style.NOTICE(
                f"\n📋 Check Celery logs for task execution"
            ))
            self.stdout.write(self.style.NOTICE(
                f"📊 Initiatives will progress as tasks complete"
            ))

    def _detect_content_type(self, topic: str) -> str:
        """Detect content type from topic text."""
        topic_lower = topic.lower()

        if any(kw in topic_lower for kw in ['persona', 'customer', 'user', 'buyer']):
            return 'strategy'
        elif any(kw in topic_lower for kw in ['plan', 'roadmap', 'timeline', 'milestone']):
            return 'plan'
        elif any(kw in topic_lower for kw in ['research', 'study', 'analysis', 'audit']):
            return 'research'
        elif any(kw in topic_lower for kw in ['content', 'blog', 'article', 'post']):
            return 'document'
        else:
            return 'strategy'  # Default
