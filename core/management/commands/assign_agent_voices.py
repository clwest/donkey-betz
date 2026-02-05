"""
Assign Agent Voices - Session 926
=================================

Management command to assign ElevenLabs voices to all agents
based on their category/specialization.

Usage:
    python manage.py assign_agent_voices          # Dry run
    python manage.py assign_agent_voices --apply  # Apply changes
    python manage.py assign_agent_voices --force  # Overwrite existing voices
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import Agent
from core.services.elevenlabs_tts_service import VOICE_IDS, AGENT_VOICE_MAP


class Command(BaseCommand):
    help = 'Assign TTS voices to agents based on their category/specialization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply the voice assignments (default is dry run)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing voice assignments'
        )
        parser.add_argument(
            '--agent',
            type=str,
            help='Assign voice to a specific agent by name'
        )

    def handle(self, *args, **options):
        apply = options['apply']
        force = options['force']
        specific_agent = options.get('agent')

        self.stdout.write(self.style.MIGRATE_HEADING('\nAgent Voice Assignment'))
        self.stdout.write('=' * 60)

        if not apply:
            self.stdout.write(self.style.WARNING('DRY RUN - Use --apply to make changes\n'))

        # Get agents to process
        if specific_agent:
            agents = Agent.objects.filter(name__icontains=specific_agent)
            if not agents.exists():
                self.stdout.write(self.style.ERROR(f'No agents found matching: {specific_agent}'))
                return
        else:
            agents = Agent.objects.all()

        self.stdout.write(f'\nProcessing {agents.count()} agents...\n')

        # Statistics
        assigned = 0
        skipped = 0
        overwritten = 0

        # Voice usage counter for reporting
        voice_usage = {name: 0 for name in VOICE_IDS.keys()}

        for agent in agents:
            # Determine the appropriate voice
            voice_name = self._get_voice_for_agent(agent)
            voice_id = VOICE_IDS.get(voice_name, VOICE_IDS['Rachel'])

            # Check current assignment
            current_voice = agent.voice_id

            if current_voice and not force:
                self.stdout.write(f'  SKIP {agent.name}: already has voice "{current_voice}"')
                skipped += 1
                # Count for stats
                for name, vid in VOICE_IDS.items():
                    if vid == current_voice or name == current_voice:
                        voice_usage[name] += 1
                        break
                continue

            # Determine action
            if current_voice:
                action = 'OVERWRITE'
                overwritten += 1
            else:
                action = 'ASSIGN'
                assigned += 1

            voice_usage[voice_name] += 1

            # Report the assignment
            category = agent.category.slug if agent.category else 'uncategorized'
            self.stdout.write(
                f'  {action} {agent.name} ({category}) -> {voice_name} ({voice_id[:12]}...)'
            )

            # Apply if requested
            if apply:
                agent.voice_id = voice_id
                agent.save(update_fields=['voice_id'])

        # Print summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.MIGRATE_HEADING('Summary'))
        self.stdout.write(f'  Assigned: {assigned}')
        self.stdout.write(f'  Skipped (already assigned): {skipped}')
        self.stdout.write(f'  Overwritten: {overwritten}')
        self.stdout.write(f'  Total: {assigned + skipped + overwritten}')

        # Voice distribution
        self.stdout.write('\n' + self.style.MIGRATE_HEADING('Voice Distribution'))
        for voice_name, count in sorted(voice_usage.items(), key=lambda x: -x[1]):
            if count > 0:
                bar = '*' * min(count, 30)
                self.stdout.write(f'  {voice_name:12} {count:3} {bar}')

        if not apply:
            self.stdout.write('\n' + self.style.WARNING('DRY RUN - Use --apply to make changes'))
        else:
            self.stdout.write('\n' + self.style.SUCCESS('Voice assignments applied successfully!'))

    def _get_voice_for_agent(self, agent: Agent) -> str:
        """
        Determine the best voice for an agent based on name and category.
        """
        name_lower = agent.name.lower()

        # Check agent name patterns
        for keyword, voice in AGENT_VOICE_MAP.items():
            if keyword in name_lower:
                return voice

        # Check category
        if agent.category:
            cat_lower = agent.category.slug.lower()
            if cat_lower in AGENT_VOICE_MAP:
                return AGENT_VOICE_MAP[cat_lower]

        # Check specialization
        if agent.specialization:
            spec_lower = agent.specialization.lower()
            for keyword, voice in AGENT_VOICE_MAP.items():
                if keyword in spec_lower:
                    return voice

        # Default
        return 'Rachel'
