"""
Session 748: Normalize all evolution data to be consistent.

The data model:
- total_xp: Cumulative XP earned (never resets)
- lifetime_xp: Same as total_xp (redundant, kept for prestige tracking)
- xp_to_next_level: XP needed to reach next level from current level
- current_level: Calculated from cumulative XP

This command fixes all inconsistencies by:
1. Using the HIGHER of total_xp/lifetime_xp as the true cumulative XP
2. Recalculating correct level from cumulative XP
3. Setting xp_to_next_level correctly for that level
4. Syncing lifetime_xp = total_xp

Usage:
    python manage.py normalize_evolution_data
    python manage.py normalize_evolution_data --dry-run
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import AgentEvolution, AgentAbility


class Command(BaseCommand):
    help = 'Normalize evolution data - fix levels, XP, and xp_to_next_level'

    # Ability definitions
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

    def get_xp_for_level(self, level):
        """XP required for a single level."""
        return int(100 * (1.5 ** (level - 1)))

    def get_cumulative_xp_for_level(self, level):
        """Cumulative XP required to REACH a level."""
        return sum(self.get_xp_for_level(lvl) for lvl in range(1, level))

    def calculate_level_from_xp(self, cumulative_xp):
        """Calculate level from cumulative XP."""
        level = 1
        xp_remaining = cumulative_xp
        while True:
            xp_needed = self.get_xp_for_level(level)
            if xp_remaining >= xp_needed:
                xp_remaining -= xp_needed
                level += 1
            else:
                break
            if level > 20:  # Safety cap
                break
        return level

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        fixed = 0
        abilities_granted = 0

        for evo in AgentEvolution.objects.select_related('agent').prefetch_related('abilities'):
            agent_name = evo.agent.name
            changes = []

            # Step 1: Determine true cumulative XP (take the higher value)
            true_xp = max(evo.total_xp, evo.lifetime_xp)

            if evo.total_xp != true_xp:
                changes.append(f'total_xp: {evo.total_xp} → {true_xp}')
            if evo.lifetime_xp != true_xp:
                changes.append(f'lifetime_xp: {evo.lifetime_xp} → {true_xp}')

            # Step 2: Calculate correct level
            correct_level = self.calculate_level_from_xp(true_xp)
            if evo.current_level != correct_level:
                changes.append(f'level: {evo.current_level} → {correct_level}')

            # Step 3: Calculate correct xp_to_next_level
            correct_xp_to_next = self.get_xp_for_level(correct_level)
            if evo.xp_to_next_level != correct_xp_to_next:
                changes.append(f'xp_to_next_level: {evo.xp_to_next_level} → {correct_xp_to_next}')

            # Step 4: Grant missing abilities
            existing_abilities = set(evo.abilities.values_list('ability_code', flat=True))
            abilities_to_grant = []
            for level, (ability_code, ability_name, description) in self.LEVEL_ABILITIES.items():
                if level <= correct_level and ability_code not in existing_abilities:
                    abilities_to_grant.append((ability_code, ability_name, description, level))
                    changes.append(f'+ Ability: {ability_name} (Level {level})')

            # Apply changes
            if changes:
                self.stdout.write(f'\n{agent_name}:')
                for change in changes:
                    self.stdout.write(f'  {change}')

                if not dry_run:
                    evo.total_xp = true_xp
                    evo.lifetime_xp = true_xp
                    evo.current_level = correct_level
                    evo.xp_to_next_level = correct_xp_to_next
                    evo.save()

                    for ability_code, ability_name, description, _ in abilities_to_grant:
                        AgentAbility.objects.create(
                            evolution=evo,
                            ability_code=ability_code,
                            ability_name=ability_name,
                            description=description,
                            is_active=True
                        )
                        abilities_granted += 1

                fixed += 1

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'Agents normalized: {fixed}'))
        self.stdout.write(self.style.SUCCESS(f'Abilities granted: {abilities_granted}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - Run without --dry-run to apply changes'))
        else:
            self.stdout.write(self.style.SUCCESS('\nData normalized successfully!'))
