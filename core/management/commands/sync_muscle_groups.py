"""
Session 792: Sync Muscle Groups with All Active Agents

Ensures all active agents (including Persona Agents) are assigned to muscle groups
so the MUSCULAR system can properly track their execution health.

Usage:
    python manage.py sync_muscle_groups
    python manage.py sync_muscle_groups --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Sync muscle groups to include all active agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them'
        )

    def handle(self, *args, **options):
        from core.models_muscular import MuscleGroup
        from core.models_unified_system import Agent

        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("SYNC MUSCLE GROUPS - Session 792"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - No changes will be made\n"))

        # Get all active agents
        all_agents = Agent.objects.filter(is_active=True)
        all_agent_names = set(all_agents.values_list('name', flat=True))
        self.stdout.write(f"\nTotal active agents: {len(all_agent_names)}")

        # Get agents already in muscle groups
        agents_in_groups = set()
        for group in MuscleGroup.objects.all():
            agents_in_groups.update(group.agent_names or [])

        self.stdout.write(f"Agents already in muscle groups: {len(agents_in_groups)}")

        # Find agents not in any group
        orphan_agents = all_agent_names - agents_in_groups
        self.stdout.write(f"Agents NOT in any muscle group: {len(orphan_agents)}")

        if not orphan_agents:
            self.stdout.write(self.style.SUCCESS("\nAll agents are already assigned to muscle groups!"))
            return

        # Categorize orphan agents
        persona_agents = []
        core_agents = []

        for agent_name in orphan_agents:
            agent = all_agents.filter(name=agent_name).first()
            if agent:
                # Persona agents typically have spaces/special formatting
                # Core agents use PascalCase like "ImageAgent"
                if ' ' in agent_name or agent.agent_type == 'persona':
                    persona_agents.append(agent_name)
                else:
                    core_agents.append(agent_name)
            else:
                persona_agents.append(agent_name)  # Default to persona

        self.stdout.write(f"\n  Persona Agents to add: {len(persona_agents)}")
        self.stdout.write(f"  Core Agents to add: {len(core_agents)}")

        if dry_run:
            self.stdout.write("\n[DRY RUN] Would create/update these muscle groups:")
            if persona_agents:
                self.stdout.write(f"  - 'persona_agents' group with {len(persona_agents)} agents")
            if core_agents:
                self.stdout.write(f"  - 'uncategorized_core' group with {len(core_agents)} agents")
            return

        with transaction.atomic():
            # Create or update Persona Agents muscle group
            if persona_agents:
                persona_group, created = MuscleGroup.objects.get_or_create(
                    name='persona_agents',
                    defaults={
                        'display_name': 'Persona Agents',
                        'category': 'persona',
                        'description': 'AI Persona agents that roleplay specialized experts',
                        'is_critical': False,
                        'is_active': True,
                        'target_success_rate': 85.0,
                        'max_daily_executions': 1000,
                        'max_avg_execution_time_ms': 30000,
                        'max_fatigue_level': 80,
                        'agent_names': [],
                    }
                )

                # Add persona agents
                existing_names = set(persona_group.agent_names or [])
                new_names = existing_names | set(persona_agents)
                persona_group.agent_names = list(new_names)
                persona_group.save()

                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(
                    f"\n{action} 'persona_agents' group with {len(new_names)} agents"
                ))

            # Create or update Uncategorized Core group
            if core_agents:
                core_group, created = MuscleGroup.objects.get_or_create(
                    name='uncategorized_core',
                    defaults={
                        'display_name': 'Uncategorized Core Agents',
                        'category': 'core',
                        'description': 'Core agents not assigned to a specific muscle group',
                        'is_critical': False,
                        'is_active': True,
                        'target_success_rate': 90.0,
                        'max_daily_executions': 500,
                        'max_avg_execution_time_ms': 20000,
                        'max_fatigue_level': 70,
                        'agent_names': [],
                    }
                )

                existing_names = set(core_group.agent_names or [])
                new_names = existing_names | set(core_agents)
                core_group.agent_names = list(new_names)
                core_group.save()

                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(
                    f"{action} 'uncategorized_core' group with {len(new_names)} agents"
                ))

        # Verify
        total_in_groups = 0
        self.stdout.write("\n" + "-" * 40)
        self.stdout.write("Updated Muscle Groups:")
        for group in MuscleGroup.objects.all().order_by('category', 'name'):
            count = len(group.agent_names or [])
            total_in_groups += count
            self.stdout.write(f"  {group.display_name}: {count} agents ({group.category})")

        self.stdout.write("-" * 40)
        self.stdout.write(f"Total agents in groups: {total_in_groups}")
        self.stdout.write(f"Total active agents: {len(all_agent_names)}")

        coverage = (total_in_groups / len(all_agent_names) * 100) if all_agent_names else 0
        self.stdout.write(self.style.SUCCESS(f"\nMuscle group coverage: {coverage:.1f}%"))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("MUSCLE GROUPS SYNCED!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("\nRun the MUSCULAR health check to see updated status:")
        self.stdout.write("  curl http://localhost:8000/api/body/muscular/flex/")
