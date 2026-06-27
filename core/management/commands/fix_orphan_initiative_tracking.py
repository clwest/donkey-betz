"""
Session 906: Fix orphan initiatives that lack proper tracking records.

Problem: Initiatives auto-created from blocked research before Session 906
don't have HiveMindSession or AgentTaskExecution records, causing the UI to show:
- Agents: 0
- Messages: 0
- Origin & Trigger: empty

This script retroactively creates tracking records for these orphan initiatives.

Usage:
    # Dry run - show what would be fixed
    python manage.py fix_orphan_initiative_tracking

    # Actually fix them
    python manage.py fix_orphan_initiative_tracking --fix

    # Limit to specific initiatives
    python manage.py fix_orphan_initiative_tracking --fix --limit=50
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
import logging
import uuid

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix orphan initiatives by creating HiveMindSession and AgentTaskExecution tracking records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually create tracking records (default is dry run)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum number of initiatives to process (default: 500)',
        )
        parser.add_argument(
            '--initiative-id',
            type=str,
            help='Fix a specific initiative by ID',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative, InitiativeStage
        from core.models_unified_system import HiveMindSession, HiveMindContribution, Agent
        from core.models.agents_registry.models import AgentTaskExecution, UnifiedAgentTemplate

        fix = options['fix']
        limit = options['limit']
        initiative_id = options.get('initiative_id')

        self.stdout.write(self.style.NOTICE(
            f"{'FIXING' if fix else 'DRY RUN'}: Finding orphan initiatives (limit: {limit})"
        ))

        # Get ResearchAgent from both models
        # Agent model for HiveMindContribution
        agent_model = Agent.objects.filter(name__icontains='Research').first()
        # UnifiedAgentTemplate for AgentTaskExecution
        agent_template = UnifiedAgentTemplate.objects.filter(name__icontains='Research').first()

        if not agent_template:
            self.stdout.write(self.style.ERROR("ResearchAgent template not found!"))
            return

        self.stdout.write(f"Using agent template: {agent_template.name} ({agent_template.id})")
        if agent_model:
            self.stdout.write(f"Using agent model: {agent_model.name} ({agent_model.id})")

        # Find orphan initiatives (those without linked HiveMindSessions)
        # An initiative is "orphan" if:
        # 1. It has "Auto-created" in description OR created_by='ResearchAgent'
        # 2. No HiveMindSession references it in metadata

        if initiative_id:
            initiatives = Initiative.objects.filter(id=initiative_id)
        else:
            initiatives = Initiative.objects.filter(
                Q(description__icontains='Auto-created') |
                Q(created_by='ResearchAgent')
            ).order_by('-created_at')[:limit]

        self.stdout.write(f"Found {initiatives.count()} potentially orphan initiatives")

        # Get existing sessions that have initiative_id in metadata or synthesis
        existing_session_initiative_ids = set()
        for session in HiveMindSession.objects.filter(session_mode='autonomous'):
            # Check if synthesis mentions an initiative
            if session.synthesis:
                existing_session_initiative_ids.add(str(session.id))

        fixed_count = 0
        skipped_count = 0
        error_count = 0

        for init in initiatives:
            # Check if this initiative already has tracking
            has_tracking = HiveMindSession.objects.filter(
                Q(synthesis__icontains=str(init.id)[:8]) |
                Q(conversation_topic__icontains=init.name[:50])
            ).exists()

            # Also check AgentTaskExecution
            has_execution = AgentTaskExecution.objects.filter(
                metadata__initiative_id=str(init.id)
            ).exists()

            if has_tracking and has_execution:
                self.stdout.write(f"SKIP: {init.name[:50]} - already has full tracking")
                skipped_count += 1
                continue

            # Partial tracking - may need to add missing pieces
            needs_session = not has_tracking
            needs_execution = not has_execution

            if fix:
                try:
                    session = None
                    session_id = None

                    # Create HiveMindSession if needed
                    if needs_session:
                        session = HiveMindSession.objects.create(
                            session_mode='autonomous',
                            question=f"Research: {init.name[:200]}",
                            context=init.description[:1000] if init.description else '',
                            conversation_topic=init.name[:200],
                            conversation_type='analytical',
                            objective=f"Investigate: {init.name[:150]}",
                            success_criteria=['Data gathered', 'Research completed'],
                            auto_selected_agents=True,
                            status='completed',
                            participant_ids=[str(agent_template.id)],
                            synthesis=f"[Session 906 Backfill] Initiative auto-created. ID: {init.id}. {init.description[:300] if init.description else 'No description.'}",
                            synthesis_summary=f"Auto-created initiative: {init.name[:100]}",
                            contribution_count=1,
                        )
                        session_id = str(session.id)

                        # Create HiveMindContribution (only if Agent model exists)
                        if agent_model:
                            HiveMindContribution.objects.create(
                                session=session,
                                agent=agent_model,
                                contribution=f"[Backfilled] Initiated research on '{init.name[:100]}'. Status: {init.status}. Current stage: {init.current_stage}.",
                                key_points=[
                                    f"Topic: {init.name[:100]}",
                                    f"Stage: {init.current_stage}",
                                    "Auto-created initiative",
                                ],
                                perspective_type='research',
                                confidence_score=0.5,
                            )
                    else:
                        # Find existing session for metadata
                        existing_session = HiveMindSession.objects.filter(
                            conversation_topic__icontains=init.name[:50]
                        ).first()
                        if existing_session:
                            session_id = str(existing_session.id)

                    # Create AgentTaskExecution if needed
                    if needs_execution:
                        AgentTaskExecution.objects.create(
                            template=agent_template,
                            execution_id=f"backfill-{uuid.uuid4().hex[:8]}",
                            task_description=f"Research: {init.name[:200]}",
                            task_type='research',
                            context={
                                'initiative_id': str(init.id),
                                'topic': init.name[:200],
                                'backfilled': True,
                            },
                            status='completed',
                            progress_percentage=100,
                            current_step='Completed',
                            steps_completed=[
                                'Initiative created',
                                'Research initiated',
                                f'Stage {init.current_stage} reached',
                            ],
                            result={
                                'success': True,
                                'initiative_id': str(init.id),
                                'backfilled': True,
                            },
                            metadata={
                                'initiative_id': str(init.id),
                                'hive_session_id': session_id,
                                'backfilled': True,
                                'session': 906,
                            },
                        )

                    fixed_count += 1
                    what_fixed = []
                    if needs_session:
                        what_fixed.append('session')
                    if needs_execution:
                        what_fixed.append('execution')
                    self.stdout.write(self.style.SUCCESS(
                        f"FIXED: {init.name[:50]} | Added: {', '.join(what_fixed)}"
                    ))

                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f"ERROR: {init.name[:50]} - {e}"
                    ))
            else:
                # Dry run
                self.stdout.write(f"WOULD FIX: {init.name[:50]} | Stage {init.current_stage}")
                fixed_count += 1

        self.stdout.write(self.style.NOTICE(f"\n--- Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"{'Fixed' if fix else 'Would fix'}: {fixed_count}"))
        self.stdout.write(f"Skipped (already have tracking): {skipped_count}")
        if error_count:
            self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
