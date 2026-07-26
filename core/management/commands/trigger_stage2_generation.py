"""
Session 906: Trigger Stage 2 (Prototype Plan) document generation for initiatives.

Usage:
    # Dry run - show what would be triggered
    python manage.py trigger_stage2_generation

    # Trigger async via Celery (limit 5)
    python manage.py trigger_stage2_generation --run --limit=5

    # Run synchronously (no Celery, for Railway run)
    python manage.py trigger_stage2_generation --run --sync --limit=5
"""

from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Trigger Stage 2 (Prototype Plan) document generation for initiatives'

    def add_arguments(self, parser):
        parser.add_argument(
            '--run',
            action='store_true',
            help='Actually trigger generation (default is dry run)',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Run synchronously instead of via Celery (use with railway run)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Maximum number of initiatives to process (default: 5)',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage

        run = options['run']
        sync = options['sync']
        limit = options['limit']

        mode = 'SYNC' if sync else 'ASYNC (Celery)'
        self.stdout.write(self.style.NOTICE(
            f"{'RUNNING' if run else 'DRY RUN'} [{mode}]: Stage 2 generation (limit: {limit})"
        ))

        # Get initiatives at Stage 2
        initiatives_at_stage2 = Initiative.objects.filter(current_stage=2).order_by('-created_at')
        self.stdout.write(f"Total initiatives at Stage 2: {initiatives_at_stage2.count()}")

        # Find those without Stage 2 documents
        needing_docs = []
        for init in initiatives_at_stage2:
            try:
                stage2 = InitiativeStage.objects.get(initiative=init, stage=2)
                if not stage2.document:
                    needing_docs.append(init)
            except InitiativeStage.DoesNotExist:
                needing_docs.append(init)

            if len(needing_docs) >= limit:
                break

        self.stdout.write(f"Found {len(needing_docs)} initiatives needing Stage 2 documents")

        success_count = 0
        error_count = 0

        for init in needing_docs:
            if run:
                if sync:
                    # Run synchronously (no Celery)
                    result = self._generate_stage_document_sync(init)
                    if result.get('success'):
                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ GENERATED: {init.name[:50]} | Doc: {result.get('document_id', 'N/A')[:8]}"
                        ))
                    else:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"❌ ERROR: {init.name[:50]} - {result.get('error', 'Unknown')}"
                        ))
                else:
                    # Run async via Celery
                    # S2981 follow-up: enqueue via helper for provenance + validation.
                    try:
                        from core.services.initiative_stage_dispatch import (
                            queue_stage_document_generation,
                        )
                        outcome = queue_stage_document_generation(
                            str(init.id), 2,
                            triggered_by='trigger_stage2_generation.management_command',
                        )
                        if outcome['success']:
                            success_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f"📤 QUEUED: {init.name[:50]} | Task: {outcome['task_id']}"
                            ))
                        else:
                            error_count += 1
                            self.stdout.write(self.style.WARNING(
                                f"⚠ REFUSED: {init.name[:50]} - "
                                f"reason={outcome['reason']} error={outcome['error']}"
                            ))
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"❌ ERROR: {init.name[:50]} - {e}"
                        ))
            else:
                self.stdout.write(f"WOULD PROCESS: {init.name[:50]}")
                success_count += 1

        action = 'GENERATED' if sync else 'QUEUED'
        self.stdout.write(self.style.SUCCESS(f"\n{action if run else 'WOULD PROCESS'}: {success_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"ERRORS: {error_count}"))

    def _generate_stage_document_sync(self, initiative):
        """
        Generate a Stage 2 document synchronously (no Celery).
        This is a simplified version of the Celery task for use with railway run.
        """
        from core.models_document_registry import InitiativeStage
        from core.models_unified_system import SelfBlog
        from core.models import Agent
        from core.agent_router import AgentRouter

        stage_num = 2

        # Get or create stage record
        stage, created = InitiativeStage.objects.get_or_create(
            initiative=initiative,
            stage=stage_num,
            defaults={'status': 'PENDING'}
        )

        if stage.document:
            return {
                'success': False,
                'error': f'Stage {stage_num} already has document',
                'document_id': str(stage.document.id)
            }

        # Build context from Stage 1
        previous_context = []
        try:
            stage1 = InitiativeStage.objects.get(initiative=initiative, stage=1)
            if stage1.document:
                doc_content = stage1.document.full_text or ''
                previous_context.append(f"## Stage 1: Research Brief\n{doc_content[:2000]}")
        except InitiativeStage.DoesNotExist:
            pass

        context_text = "\n\n".join(previous_context) if previous_context else "No previous stage documents."

        # Build the generation prompt
        prompt = f"""Generate a Prototype Plan document for this initiative.

## Initiative
**Name:** {initiative.name}
**Description:** {initiative.description or 'No description provided'}

## Previous Stage Context
{context_text}

## Your Task
Create a comprehensive Prototype Plan document that builds on the research brief.
Include:
- Architecture Overview
- Implementation Approach
- Key Components
- Risk Assessment
- Timeline/Milestones
"""

        try:
            # Get the agent
            # Session 912: Use ContentWriterAgent instead of ThinkingAgent
            # ThinkingAgent ignores the task and returns system diagnostics
            agent_model = Agent.objects.filter(name='ContentWriterAgent').first()
            if not agent_model:
                # Fallback to any content-related agent
                agent_model = Agent.objects.filter(name__icontains='Content').first()
            if not agent_model:
                return {'success': False, 'error': 'ContentWriterAgent not found'}

            # Execute the agent
            router = AgentRouter()
            result = router.route(
                agent_name=agent_model.name,
                task=prompt,
                context={'initiative_id': str(initiative.id), 'stage': stage_num}
            )

            if not result or not result.message:
                return {'success': False, 'error': 'Agent returned empty response'}

            document_content = result.message

            # Create the document
            document = SelfBlog.objects.create(
                title=f"{initiative.name} - Stage 2: Prototype Plan",
                intro=document_content[:500],
                full_text=document_content,
                category='prototype_plan',
                content_type='internal',
                status='draft',
                initiative=initiative,
                initiative_stage=stage,
            )

            # Link document to stage
            stage.document = document
            stage.status = 'DRAFT'
            stage.save()

            return {
                'success': True,
                'document_id': str(document.id),
                'stage': stage_num,
                'initiative_id': str(initiative.id),
                'initiative_name': initiative.name
            }

        except Exception as e:
            logger.error(f"Error generating Stage {stage_num}: {e}")
            return {'success': False, 'error': str(e)}
