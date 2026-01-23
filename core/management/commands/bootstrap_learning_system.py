"""
Session 790: Bootstrap Learning System

Seeds the learning system with initial data for fresh deployments:
1. Creates sample AgentExecution records
2. Triggers the learning cycle to generate AgentLearning records
3. Creates initial KnowledgeTransfer records
4. Mines patterns from the seeded data
5. Updates agent effectiveness scores

Run with: python manage.py bootstrap_learning_system

On Railway:
    railway run python manage.py bootstrap_learning_system
"""

import logging
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Bootstrap the learning system with seed data for fresh deployments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )
        parser.add_argument(
            '--executions',
            type=int,
            default=50,
            help='Number of seed executions to create (default: 50)',
        )
        parser.add_argument(
            '--skip-mining',
            action='store_true',
            help='Skip the pattern mining step',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        num_executions = options.get('executions', 50)
        skip_mining = options.get('skip_mining', False)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("LEARNING SYSTEM BOOTSTRAP - Session 790"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        # Step 1: Check current state
        self.stdout.write(self.style.NOTICE("\n📊 Step 1: Checking current state..."))
        stats = self._check_current_state()

        for key, value in stats.items():
            self.stdout.write(f"  {key}: {value}")

        # Step 2: Seed agent executions
        self.stdout.write(self.style.NOTICE(f"\n🚀 Step 2: Seeding {num_executions} agent executions..."))
        executions_created = self._seed_executions(num_executions, dry_run)
        self.stdout.write(f"  Created: {executions_created} executions")

        # Step 3: Run learning cycle
        self.stdout.write(self.style.NOTICE("\n🧠 Step 3: Running learning cycle..."))
        learning_result = self._run_learning_cycle(dry_run)
        self.stdout.write(f"  Result: {learning_result}")

        # Step 4: Create knowledge transfers
        self.stdout.write(self.style.NOTICE("\n📚 Step 4: Creating knowledge transfers..."))
        transfers_created = self._seed_knowledge_transfers(dry_run)
        self.stdout.write(f"  Created: {transfers_created} transfers")

        # Step 5: Mine patterns
        if not skip_mining:
            self.stdout.write(self.style.NOTICE("\n🔍 Step 5: Mining learning patterns..."))
            patterns_result = self._mine_patterns(dry_run)
            self.stdout.write(f"  Result: {patterns_result}")
        else:
            self.stdout.write(self.style.WARNING("\n⏭️ Step 5: Skipping pattern mining"))

        # Step 6: Update effectiveness scores
        self.stdout.write(self.style.NOTICE("\n📈 Step 6: Updating agent effectiveness..."))
        effectiveness_result = self._update_effectiveness(dry_run)
        self.stdout.write(f"  Result: {effectiveness_result}")

        # Final summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ BOOTSTRAP COMPLETE!"))

        final_stats = self._check_current_state()
        self.stdout.write("\n📊 Final State:")
        for key, value in final_stats.items():
            self.stdout.write(f"  {key}: {value}")
        self.stdout.write("=" * 60)

    def _check_current_state(self) -> dict:
        """Check current learning system state."""
        from core.models_unified_system import (
            Agent, AgentExecution, AgentLearning,
            KnowledgeTransfer, LearningPattern
        )

        return {
            'Agents': Agent.objects.filter(is_active=True).count(),
            'AgentExecutions': AgentExecution.objects.count(),
            'AgentLearning': AgentLearning.objects.count(),
            'KnowledgeTransfers': KnowledgeTransfer.objects.count(),
            'LearningPatterns': LearningPattern.objects.filter(is_active=True).count(),
        }

    def _seed_executions(self, count: int, dry_run: bool) -> int:
        """Seed agent execution records."""
        if dry_run:
            return count

        from core.models_unified_system import Agent, AgentExecution
        import uuid

        agents = list(Agent.objects.filter(is_active=True)[:20])
        if not agents:
            self.stdout.write(self.style.WARNING("  No agents found!"))
            return 0

        created = 0
        now = timezone.now()

        # Sample tasks for variety
        sample_tasks = [
            "Analyze market trends for tech sector",
            "Research competitor pricing strategies",
            "Generate content strategy recommendations",
            "Identify investment opportunities",
            "Review job market trends",
            "Analyze social media engagement patterns",
            "Create SEO optimization plan",
            "Evaluate startup funding landscape",
            "Monitor cryptocurrency market movements",
            "Assess risk factors for portfolio",
        ]

        for i in range(count):
            agent = random.choice(agents)
            task = random.choice(sample_tasks)

            # Most executions succeed
            success = random.random() > 0.1
            status = 'completed' if success else 'failed'

            execution = AgentExecution.objects.create(
                id=uuid.uuid4(),
                agent=agent,
                task=task[:500],
                status=status,
                execution_time_ms=random.randint(500, 15000),
                tokens_used=random.randint(100, 2000),
                cost=random.uniform(0.001, 0.05),
                input_data={
                    'spider_data_used': random.randint(0, 10),
                    'advisor_consulted': random.choice([True, False]),
                    'seeded': True,
                },
                output_data={
                    'result': f'Completed analysis for {task[:50]}',
                    'confidence': random.uniform(0.7, 0.95),
                    'success': success,
                    'seeded': True,
                },
                error_message='' if success else 'Simulated failure for testing',
                completed_at=now if success else None,
            )
            created += 1

        return created

    def _run_learning_cycle(self, dry_run: bool) -> str:
        """Run the agent learning cycle."""
        if dry_run:
            return "Would run learning cycle"

        try:
            from core.tasks import run_agent_learning_cycle
            result = run_agent_learning_cycle()
            return f"Success: {result}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    def _seed_knowledge_transfers(self, dry_run: bool) -> int:
        """Seed knowledge transfer records between agents."""
        if dry_run:
            return 20

        from core.models_unified_system import Agent, KnowledgeTransfer, AgentLearningConnection

        # Get existing learning connections
        connections = AgentLearningConnection.objects.filter(is_active=True)[:30]

        if not connections:
            self.stdout.write(self.style.WARNING("  No learning connections found!"))
            return 0

        created = 0
        now = timezone.now()

        for conn in connections:
            # Create a transfer record
            try:
                transfer, was_created = KnowledgeTransfer.objects.get_or_create(
                    teacher_agent=conn.teacher_agent,
                    student_agent=conn.student_agent,
                    knowledge_type=conn.learning_type or 'collaborative',
                    defaults={
                        'content': f"Knowledge transfer from {conn.teacher_agent.name} to {conn.student_agent.name}",
                        'effectiveness_score': random.uniform(0.6, 0.95),
                        'transfer_date': now - timedelta(days=random.randint(0, 7)),
                        'is_applied': True,
                    }
                )
                if was_created:
                    created += 1
            except Exception as e:
                self.stdout.write(f"  Skip: {str(e)[:50]}")
                continue

        return created

    def _mine_patterns(self, dry_run: bool) -> str:
        """Mine learning patterns from seeded data."""
        if dry_run:
            return "Would mine patterns"

        try:
            from core.tasks import mine_learning_patterns
            result = mine_learning_patterns(days_back=30)
            return f"Created: {result.get('patterns_created', 0)}, Updated: {result.get('patterns_updated', 0)}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    def _update_effectiveness(self, dry_run: bool) -> str:
        """Update agent effectiveness scores."""
        if dry_run:
            return "Would update effectiveness"

        try:
            from core.tasks import update_agent_effectiveness_from_learning
            result = update_agent_effectiveness_from_learning()
            return f"Updated: {result}"
        except Exception as e:
            return f"Error: {str(e)[:100]}"
