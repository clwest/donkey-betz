"""
Management command to register all sports-specific agents
"""

from django.core.management.base import BaseCommand
from sports.agents import SportsAgentRegistry


class Command(BaseCommand):
    help = 'Register all sports-specific agents in the unified agent orchestration system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-registration of existing agents',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Registering sports-specific agents...')
        
        try:
            registered_count = SportsAgentRegistry.register_all_agents()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully registered {registered_count} sports agents'
                )
            )
            
            # List registered agents
            self.stdout.write('\nRegistered agents:')
            from sports.agents import SPORTS_AGENT_CLASSES
            for agent_class in SPORTS_AGENT_CLASSES:
                agent = agent_class()
                self.stdout.write(f'  - {agent.display_name} ({agent.name})')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to register sports agents: {e}')
            )
            raise