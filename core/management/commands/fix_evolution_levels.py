"""
Session 748: Management command to fix evolution level/ability inconsistencies.

The old learning_loop.py used different XP thresholds, causing:
1. Levels that don't match XP amounts
2. Missing ability unlocks for high-level agents

This command:
1. Recalculates correct level from XP using the model's formula
2. Grants missing abilities based on the corrected level

Usage:
    python manage.py fix_evolution_levels          # Fix all
    python manage.py fix_evolution_levels --dry-run  # Preview
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import AgentEvolution, AgentAbility


class Command(BaseCommand):
    help = 'Fix evolution levels and grant missing abilities based on XP'

    # Ability definitions (same as in model)
    LEVEL_ABILITIES = {
        2: ('enhanced_focus', 'Enhanced Focus', 'Improved task concentration'),
        3: ('parallel_processing', 'Parallel Processing', 'Handle multiple subtasks'),
        4: ('deep_analysis', 'Deep Analysis', 'More thorough research'),
        5: ('creative_spark', 'Creative Spark', 'Generate novel ideas'),
        6: ('mentor_mode', 'Mentor Mode', 'Teach other agents'),
        7: ('time_warp', 'Time Warp', 'Faster execution speed'),
        8: ('pattern_master', 'Pattern Master', 'Recognize complex patterns'),
        9: ('intuition', 'Intuition', 'Make educated guesses'),
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def calculate_level_from_xp(self, xp):
        """Calculate correct level based on XP using model's formula."""
        # Formula: 100 * (1.5 ** (level - 1)) for each level
        level = 1
        cumulative_xp = 0

        for lvl in range(1, 20):
            xp_for_level = int(100 * (1.5 ** (lvl - 1)))
            cumulative_xp += xp_for_level
            if xp >= cumulative_xp:
                level = lvl + 1
            else:
                break

        return level

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        levels_fixed = 0
        abilities_granted = 0

        for evo in AgentEvolution.objects.select_related('agent').prefetch_related('abilities'):
            agent_name = evo.agent.name
            old_level = evo.current_level
            correct_level = self.calculate_level_from_xp(evo.total_xp)

            changes = []

            # Fix level if wrong
            if old_level != correct_level:
                changes.append(f'Level: {old_level} → {correct_level}')
                if not dry_run:
                    evo.current_level = correct_level
                    evo.save(update_fields=['current_level'])
                levels_fixed += 1

            # Grant missing abilities based on CORRECT level
            existing_abilities = set(evo.abilities.values_list('ability_code', flat=True))

            for level, (ability_code, ability_name, description) in self.LEVEL_ABILITIES.items():
                if level <= correct_level and ability_code not in existing_abilities:
                    changes.append(f'+ Ability: {ability_name} (Level {level})')
                    if not dry_run:
                        AgentAbility.objects.create(
                            evolution=evo,
                            ability_code=ability_code,
                            ability_name=ability_name,
                            description=description,
                            is_active=True
                        )
                    abilities_granted += 1

            # Report changes
            if changes:
                self.stdout.write(f'\n{agent_name} (XP: {evo.total_xp}):')
                for change in changes:
                    self.stdout.write(f'  {change}')

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Levels fixed: {levels_fixed}'))
        self.stdout.write(self.style.SUCCESS(f'Abilities granted: {abilities_granted}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - Run without --dry-run to apply changes'))
