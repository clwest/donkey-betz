# Session 862: Generate Synthetic User Profiles for Testing
# Creates diverse test personas to validate agent recommendations

from django.core.management.base import BaseCommand
from django.db import transaction

from core.services.synthetic_user_generator import (
    SyntheticUserGenerator,
    generate_test_personas,
    get_persona_summary,
)
from core.models_synthetic_users import SyntheticUserProfile


class Command(BaseCommand):
    help = 'Generate synthetic user profiles for testing agent recommendations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate one profile for each archetype',
        )
        parser.add_argument(
            '--archetype',
            type=str,
            help='Generate a profile for a specific archetype',
        )
        parser.add_argument(
            '--variations',
            type=int,
            default=0,
            help='Number of variations to generate per archetype',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available archetypes',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current synthetic user status',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all synthetic users before generating',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without saving',
        )

    def handle(self, *args, **options):
        generator = SyntheticUserGenerator()

        # List archetypes
        if options['list']:
            self.stdout.write(self.style.SUCCESS('\n=== Available Persona Archetypes ===\n'))
            summary = get_persona_summary()
            for key, info in summary['archetypes'].items():
                self.stdout.write(f"  {self.style.WARNING(key)}")
                self.stdout.write(f"    {info['description']}")
                self.stdout.write(f"    Tests: {', '.join(info['tests'][:3])}...")
                self.stdout.write('')
            self.stdout.write(f"\nTotal: {summary['total_archetypes']} archetypes\n")
            return

        # Show status
        if options['status']:
            total = SyntheticUserProfile.objects.count()
            active = SyntheticUserProfile.objects.filter(is_active=True).count()
            by_archetype = {}
            for profile in SyntheticUserProfile.objects.all():
                by_archetype[profile.archetype] = by_archetype.get(profile.archetype, 0) + 1

            self.stdout.write(self.style.SUCCESS('\n=== Synthetic User Status ===\n'))
            self.stdout.write(f"  Total profiles: {total}")
            self.stdout.write(f"  Active: {active}")
            self.stdout.write(f"  Inactive: {total - active}")
            self.stdout.write('\n  By Archetype:')
            for archetype, count in sorted(by_archetype.items()):
                self.stdout.write(f"    {archetype}: {count}")
            self.stdout.write('')
            return

        # Clear existing
        if options['clear']:
            count = SyntheticUserProfile.objects.count()
            if not options['dry_run']:
                SyntheticUserProfile.objects.all().delete()
                self.stdout.write(self.style.WARNING(f'Cleared {count} existing synthetic users'))
            else:
                self.stdout.write(self.style.WARNING(f'Would clear {count} existing synthetic users'))

        # Generate all archetypes
        if options['all']:
            self.stdout.write(self.style.SUCCESS('\n=== Generating All Archetypes ===\n'))

            with transaction.atomic():
                profiles = []
                for archetype_key in generator.get_available_archetypes():
                    profile = generator.generate_profile(archetype_key)

                    if not options['dry_run']:
                        profile.save()

                    profiles.append(profile)
                    self.stdout.write(f"  Created: {self.style.SUCCESS(profile.name)}")
                    self.stdout.write(f"    Archetype: {profile.archetype}")
                    self.stdout.write(f"    Goal: {profile.primary_goal}")
                    self.stdout.write(f"    Skills: {', '.join(profile.skills[:3])}...")
                    self.stdout.write('')

                    # Generate variations if requested
                    if options['variations'] > 0:
                        variations = generator.generate_variations(
                            archetype_key,
                            count=options['variations'],
                            save=not options['dry_run']
                        )
                        for v in variations:
                            self.stdout.write(f"    + Variation: {v.name}")
                        profiles.extend(variations)

            self.stdout.write(self.style.SUCCESS(f'\nGenerated {len(profiles)} synthetic users'))
            if options['dry_run']:
                self.stdout.write(self.style.WARNING('(Dry run - nothing saved)'))
            return

        # Generate specific archetype
        if options['archetype']:
            archetype_key = options['archetype']

            if archetype_key not in generator.get_available_archetypes():
                self.stdout.write(self.style.ERROR(f'Unknown archetype: {archetype_key}'))
                self.stdout.write(f'Available: {", ".join(generator.get_available_archetypes())}')
                return

            self.stdout.write(self.style.SUCCESS(f'\n=== Generating {archetype_key} ===\n'))

            profile = generator.generate_profile(archetype_key)

            if not options['dry_run']:
                profile.save()

            self._print_profile_details(profile)

            # Generate variations if requested
            if options['variations'] > 0:
                self.stdout.write(f'\n=== Generating {options["variations"]} Variations ===\n')
                variations = generator.generate_variations(
                    archetype_key,
                    count=options['variations'],
                    save=not options['dry_run']
                )
                for v in variations:
                    self.stdout.write(f"  + {v.name}")

            if options['dry_run']:
                self.stdout.write(self.style.WARNING('\n(Dry run - nothing saved)'))
            return

        # Default: show help
        self.stdout.write(self.style.WARNING('\nNo action specified. Use one of:'))
        self.stdout.write('  --all          Generate all archetypes')
        self.stdout.write('  --archetype X  Generate specific archetype')
        self.stdout.write('  --list         List available archetypes')
        self.stdout.write('  --status       Show current synthetic user status')
        self.stdout.write('  --clear        Clear all synthetic users')
        self.stdout.write('  --variations N Generate N variations per archetype')
        self.stdout.write('  --dry-run      Preview without saving')

    def _print_profile_details(self, profile):
        """Print detailed profile information."""
        self.stdout.write(f"  Name: {self.style.SUCCESS(profile.name)}")
        self.stdout.write(f"  Archetype: {profile.archetype}")
        self.stdout.write(f"  Description: {profile.description}")
        self.stdout.write('')
        self.stdout.write(f"  Demographics:")
        self.stdout.write(f"    Age: {profile.age_bracket}")
        self.stdout.write(f"    Location: {profile.location}")
        self.stdout.write(f"    Income: {profile.income_bracket}")
        self.stdout.write('')
        self.stdout.write(f"  Career:")
        self.stdout.write(f"    Occupation: {profile.occupation}")
        self.stdout.write(f"    Experience: {profile.experience_years} years")
        self.stdout.write(f"    Skills: {', '.join(profile.skills)}")
        self.stdout.write(f"    Industries: {', '.join(profile.industries)}")
        self.stdout.write('')
        self.stdout.write(f"  Goals:")
        self.stdout.write(f"    Primary: {profile.primary_goal}")
        self.stdout.write(f"    Timeline: {profile.timeline}")
        if profile.income_target:
            self.stdout.write(f"    Income Target: ${profile.income_target:,}")
        self.stdout.write('')
        self.stdout.write(f"  Behavioral:")
        self.stdout.write(f"    Engagement: {profile.engagement_level}")
        self.stdout.write(f"    Decision Style: {profile.decision_style}")
        self.stdout.write(f"    Tech Comfort: {profile.tech_comfort}")
        self.stdout.write('')
        self.stdout.write(f"  Expected Recommendations: {', '.join(profile.expected_recommendations)}")
        self.stdout.write(f"  Expected Agents: {', '.join(profile.expected_agents[:3])}...")
