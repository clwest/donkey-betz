"""
Django management command to start the live learning demonstration
"""

from django.core.management.base import BaseCommand
# Session 727: Migrated to core/services/live_learning_orchestrator.py
from core.services.live_learning_orchestrator import LiveLearningOrchestrator
import asyncio


class Command(BaseCommand):
    help = 'Start the live learning demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-type',
            type=str,
            default='ecommerce',
            help='Type of project to generate (ecommerce, saas, marketplace)'
        )
        parser.add_argument(
            '--agents',
            type=str,
            nargs='+',
            default=['Business Agent', 'ML Recommendation Engine', 'Database Architect'],
            help='List of agents to use in the demo'
        )
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='Number of learning iterations'
        )

    def handle(self, *args, **options):
        project_type = options['project_type']
        agents = options['agents']
        iterations = options['iterations']

        self.stdout.write(self.style.SUCCESS(
            f'🚀 Starting live learning demo:\n'
            f'   Project: {project_type}\n'
            f'   Agents: {", ".join(agents)}\n'
            f'   Iterations: {iterations}\n'
        ))

        orchestrator = LiveLearningOrchestrator()

        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(
                orchestrator.start_learning_loop(
                    project_type=project_type,
                    agents=agents
                )
            )
            self.stdout.write(self.style.SUCCESS('✅ Learning demo completed successfully!'))

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n⚠️ Learning demo interrupted'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

        finally:
            loop.close()