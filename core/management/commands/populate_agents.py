"""
Session 790: Populate Core Agents in Database

This command populates all 74 core agents from AGENT_MAP into the database
without running any LLM calls. Required for Railway production deployments
where the database starts fresh.

Usage:
    python manage.py populate_agents

    # On Railway:
    railway run python manage.py populate_agents
"""

from django.core.management.base import BaseCommand
from core.agent_router import AgentRouter
from core.models_unified_system import Agent


class Command(BaseCommand):
    help = 'Populate all core agents from AGENT_MAP into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("POPULATING CORE AGENTS - Session 790"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        router = AgentRouter()
        agent_names = sorted(router.AGENT_MAP.keys())

        self.stdout.write(f"\nFound {len(agent_names)} agents in AGENT_MAP\n")

        created_count = 0
        existing_count = 0
        error_count = 0

        for name in agent_names:
            try:
                # Instantiate the agent class to get metadata
                agent_class = router.AGENT_MAP[name]

                # Get description from class
                description = ""
                if hasattr(agent_class, 'SYSTEM_PROMPT'):
                    description = agent_class.SYSTEM_PROMPT[:500]
                elif hasattr(agent_class, '__doc__') and agent_class.__doc__:
                    description = agent_class.__doc__[:500]

                # Get specialization if available
                specialization = ""
                if hasattr(agent_class, 'SPECIALIZATION'):
                    specialization = agent_class.SPECIALIZATION
                elif hasattr(agent_class, 'SPECIALTY'):
                    specialization = agent_class.SPECIALTY

                # Create or get agent in database
                agent, created = Agent.objects.get_or_create(
                    name=name,
                    defaults={
                        'agent_type': 'core',
                        'description': description,
                        'specialization': specialization,
                        'is_active': True,
                        'effectiveness_score': 85,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  + Created: {name}"))
                else:
                    existing_count += 1
                    self.stdout.write(f"  = Exists:  {name}")

            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"  ! Error:   {name} - {str(e)[:50]}"))

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"COMPLETE: {created_count} created, {existing_count} existing, {error_count} errors"))
        self.stdout.write(f"Total agents in database: {Agent.objects.count()}")
        self.stdout.write("=" * 60)

        # Remind about next steps
        if created_count > 0:
            self.stdout.write("\nNext steps:")
            self.stdout.write("  1. Run: python manage.py sync_agent_learning")
            self.stdout.write("  2. Run: python manage.py sync_orchestrations")
