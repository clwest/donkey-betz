"""
Seed Test Scenarios Management Command
=======================================

Session 334: Creates PartnershipProjects from test scenarios for
comprehensive testing of the business research agents.

Usage:
    # Seed all scenarios
    python manage.py seed_test_scenarios

    # Seed specific industry
    python manage.py seed_test_scenarios --industry ai_tech

    # Seed specific scenario
    python manage.py seed_test_scenarios --scenario ai-podcast-tools

    # List available scenarios
    python manage.py seed_test_scenarios --list

    # Clean up (delete test scenario projects)
    python manage.py seed_test_scenarios --cleanup
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from core.testing import (
    TEST_SCENARIOS,
    Industry,
    get_scenario,
    get_scenarios_by_industry,
    get_scenario_summary,
)
from core.models_partnership import PartnershipProject

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed test scenarios as PartnershipProjects for agent testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--industry',
            type=str,
            help='Only seed scenarios for a specific industry (e.g., ai_tech, saas, ecommerce)',
        )
        parser.add_argument(
            '--scenario',
            type=str,
            help='Only seed a specific scenario by ID (e.g., ai-podcast-tools)',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available scenarios without seeding',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Delete all test scenario projects',
        )
        parser.add_argument(
            '--user',
            type=str,
            default='test_scenarios',
            help='Username for the test user (default: test_scenarios)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_scenarios()
            return

        if options['cleanup']:
            self._cleanup_scenarios()
            return

        # Get or create test user
        user = self._get_or_create_user(options['user'])

        # Determine which scenarios to seed
        scenarios = self._get_scenarios_to_seed(options)

        if not scenarios:
            self.stdout.write(self.style.WARNING("No scenarios found to seed."))
            return

        if options['dry_run']:
            self._dry_run(scenarios)
            return

        # Seed the scenarios
        self._seed_scenarios(user, scenarios)

    def _list_scenarios(self):
        """List all available test scenarios."""
        summary = get_scenario_summary()

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📋 AVAILABLE TEST SCENARIOS"))
        self.stdout.write("=" * 80)

        self.stdout.write(f"\nTotal Scenarios: {summary['total_scenarios']}")
        self.stdout.write(f"\nComplexity Breakdown:")
        self.stdout.write(f"  - Low: {summary['complexity_breakdown']['low']}")
        self.stdout.write(f"  - Medium: {summary['complexity_breakdown']['medium']}")
        self.stdout.write(f"  - High: {summary['complexity_breakdown']['high']}")

        self.stdout.write(f"\nIndustries: {', '.join(summary['industries'])}")

        self.stdout.write("\n" + "-" * 80)
        self.stdout.write("SCENARIOS BY INDUSTRY:")
        self.stdout.write("-" * 80)

        current_industry = None
        for s in TEST_SCENARIOS:
            if s.industry != current_industry:
                current_industry = s.industry
                self.stdout.write(f"\n{self.style.HTTP_INFO(s.industry.value.upper())}:")

            self.stdout.write(f"  • {s.id}: {s.name}")
            self.stdout.write(f"    Company: {s.company_name} | Complexity: {s.complexity.value}")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("\nUsage examples:")
        self.stdout.write("  python manage.py seed_test_scenarios")
        self.stdout.write("  python manage.py seed_test_scenarios --industry saas")
        self.stdout.write("  python manage.py seed_test_scenarios --scenario ai-podcast-tools")
        self.stdout.write("")

    def _cleanup_scenarios(self):
        """Delete all test scenario projects."""
        # Find projects created from test scenarios by metadata
        test_projects = PartnershipProject.objects.filter(
            metadata__has_key='test_scenario_id'
        )

        count = test_projects.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No test scenario projects found to delete."))
            return

        self.stdout.write(f"Found {count} test scenario projects.")

        # Confirm deletion
        self.stdout.write(self.style.WARNING(f"About to delete {count} test scenario projects."))

        test_projects.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {count} test scenario projects."))

    def _get_or_create_user(self, username: str) -> User:
        """Get or create the test user."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@testscenarios.local',
                'first_name': 'Test',
                'last_name': 'Scenarios',
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write(f"Created test user: {username}")
        else:
            self.stdout.write(f"Using existing user: {username}")

        return user

    def _get_scenarios_to_seed(self, options) -> list:
        """Determine which scenarios to seed based on options."""
        if options['scenario']:
            scenario = get_scenario(options['scenario'])
            if not scenario:
                raise CommandError(f"Scenario '{options['scenario']}' not found.")
            return [scenario]

        if options['industry']:
            try:
                industry = Industry(options['industry'])
            except ValueError:
                valid = [i.value for i in Industry]
                raise CommandError(f"Invalid industry. Valid options: {', '.join(valid)}")

            scenarios = get_scenarios_by_industry(industry)
            if not scenarios:
                raise CommandError(f"No scenarios found for industry: {options['industry']}")
            return scenarios

        return TEST_SCENARIOS

    def _dry_run(self, scenarios):
        """Show what would be created without creating."""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.WARNING("🔍 DRY RUN - Nothing will be created"))
        self.stdout.write("=" * 80)

        for s in scenarios:
            self.stdout.write(f"\n📁 Would create project: {s.company_name}")
            self.stdout.write(f"   Industry: {s.industry.value}")
            self.stdout.write(f"   Complexity: {s.complexity.value}")
            self.stdout.write(f"   Description: {s.company_description[:60]}...")

        self.stdout.write(f"\n✅ Total: {len(scenarios)} projects would be created.")

    def _seed_scenarios(self, user: User, scenarios: list):
        """Create PartnershipProjects from scenarios."""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("🌱 SEEDING TEST SCENARIOS"))
        self.stdout.write("=" * 80)

        created_count = 0
        updated_count = 0

        for s in scenarios:
            # Check if project already exists (by scenario ID in metadata)
            existing = PartnershipProject.objects.filter(
                metadata__test_scenario_id=s.id
            ).first()

            if existing:
                # Update existing project
                project = existing
                updated_count += 1
                action = "Updated"
            else:
                # Create new project
                project = PartnershipProject(user=user)
                created_count += 1
                action = "Created"

            # Populate project fields
            project.project_name = s.company_name
            project.project_type = self._map_industry_to_project_type(s.industry)
            project.description = s.company_description
            project.goal = s.unique_value_proposition
            project.status = 'planning'
            project.category = s.industry.value

            # Store rich metadata for agents to use
            project.metadata = {
                # Test scenario reference
                'test_scenario_id': s.id,
                'test_scenario_name': s.name,

                # Company info (for agent context)
                'company_info': {
                    'name': s.company_name,
                    'location': s.location,
                    'founded': s.founded_year,
                    'size': s.company_size.value,
                    'business_model': s.business_model,
                    'target_market': s.target_market,
                },

                # Research prompts (for testing)
                'test_queries': {
                    'competitor_analysis': s.competitor_analysis_query,
                    'customer_research': s.customer_research_query,
                    'market_analysis': s.market_analysis_query,
                },

                # Expected results (for validation)
                'expected_results': {
                    'competitors': s.expected_competitors,
                    'pain_points': s.expected_pain_points,
                    'customer_segments': s.expected_customer_segments,
                    'target_subreddits': s.target_subreddits,
                },

                # Additional context
                'current_challenges': s.current_challenges,
                'tags': s.tags,
                'complexity': s.complexity.value,
            }

            project.tags = s.tags

            project.save()

            self.stdout.write(
                f"  {self.style.SUCCESS('✅')} {action}: {s.company_name} "
                f"({s.industry.value})"
            )

        self.stdout.write("\n" + "-" * 80)
        self.stdout.write(self.style.SUCCESS(f"🎉 SEEDING COMPLETE!"))
        self.stdout.write(f"   Created: {created_count} projects")
        self.stdout.write(f"   Updated: {updated_count} projects")
        self.stdout.write(f"   Total: {len(scenarios)} scenarios processed")

        self.stdout.write("\n📊 Next steps:")
        self.stdout.write("   1. Run: python manage.py test_agent_scenarios --list")
        self.stdout.write("   2. Run: python manage.py test_agent_scenarios --scenario ai-podcast-tools")
        self.stdout.write("")

    def _map_industry_to_project_type(self, industry: Industry) -> str:
        """Map industry to PartnershipProject.project_type."""
        mapping = {
            Industry.AI_TECH: 'development',
            Industry.SAAS: 'development',
            Industry.ECOMMERCE: 'marketing',
            Industry.FOOD_BEVERAGE: 'marketing',
            Industry.HEALTHCARE: 'consulting',
            Industry.EDUCATION: 'content_creation',
            Industry.FINANCE: 'consulting',
            Industry.CREATIVE: 'design',
            Industry.MANUFACTURING: 'consulting',
            Industry.REAL_ESTATE: 'consulting',
            Industry.FITNESS: 'marketing',
            Industry.MEDIA: 'content_creation',
            Industry.SUSTAINABILITY: 'research',
            Industry.LEGAL: 'consulting',
            Industry.TRAVEL: 'marketing',
        }
        return mapping.get(industry, 'other')
