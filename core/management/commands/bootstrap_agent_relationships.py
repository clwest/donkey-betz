"""
Session 810: Bootstrap Agent Relationships

Creates initial AgentRelationship entries between agents based on their
categories and complementary skills. This populates the sci-fi "Agent
Relationships" feature on the frontend.

Usage:
    python manage.py bootstrap_agent_relationships           # Create relationships
    python manage.py bootstrap_agent_relationships --dry-run # Preview only
"""

import random
from django.core.management.base import BaseCommand


# Define relationship affinities between agent categories
CATEGORY_AFFINITIES = {
    # Category: [(related_category, relationship_type, strength_range), ...]
    'research': [
        ('content', 'alliance', (0.6, 0.8)),
        ('strategy', 'alliance', (0.5, 0.7)),
        ('development', 'mentorship', (0.4, 0.6)),
    ],
    'content': [
        ('research', 'alliance', (0.6, 0.8)),
        ('media', 'alliance', (0.7, 0.9)),
        ('strategy', 'alliance', (0.5, 0.7)),
        ('podcast', 'mentorship', (0.5, 0.7)),
    ],
    'strategy': [
        ('executive', 'alliance', (0.7, 0.9)),
        ('financial', 'alliance', (0.6, 0.8)),
        ('research', 'alliance', (0.5, 0.7)),
    ],
    'financial': [
        ('predictions', 'alliance', (0.7, 0.9)),
        ('blockchain', 'alliance', (0.6, 0.8)),
        ('strategy', 'alliance', (0.5, 0.7)),
    ],
    'predictions': [
        ('financial', 'alliance', (0.7, 0.9)),
        ('research', 'mentorship', (0.5, 0.7)),
    ],
    'blockchain': [
        ('financial', 'alliance', (0.6, 0.8)),
        ('security', 'alliance', (0.7, 0.9)),
        ('development', 'mentorship', (0.5, 0.7)),
    ],
    'development': [
        ('security', 'alliance', (0.6, 0.8)),
        ('system', 'alliance', (0.7, 0.9)),
    ],
    'security': [
        ('blockchain', 'alliance', (0.7, 0.9)),
        ('development', 'alliance', (0.6, 0.8)),
        ('system', 'mentorship', (0.5, 0.7)),
    ],
    'media': [
        ('content', 'alliance', (0.7, 0.9)),
        ('podcast', 'alliance', (0.6, 0.8)),
    ],
    'podcast': [
        ('content', 'alliance', (0.6, 0.8)),
        ('media', 'alliance', (0.6, 0.8)),
    ],
    'executive': [
        ('strategy', 'alliance', (0.7, 0.9)),
        ('coordination', 'mentorship', (0.6, 0.8)),
    ],
    'narrative': [
        ('content', 'alliance', (0.6, 0.8)),
        ('research', 'alliance', (0.5, 0.7)),
    ],
    'coordination': [
        ('executive', 'alliance', (0.6, 0.8)),
        ('system', 'alliance', (0.5, 0.7)),
    ],
    'system': [
        ('development', 'alliance', (0.7, 0.9)),
        ('security', 'alliance', (0.6, 0.8)),
    ],
    'assistant': [
        ('research', 'alliance', (0.5, 0.7)),
        ('content', 'alliance', (0.5, 0.7)),
    ],
}

# Same category relationships (some rivalry, some mentorship)
SAME_CATEGORY_TYPES = ['alliance', 'rivalry', 'mentorship']


class Command(BaseCommand):
    help = 'Bootstrap agent relationships between agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing relationships before creating new ones'
        )

    def handle(self, *args, **options):
        from core.models_unified_system import Agent, AgentRelationship

        dry_run = options['dry_run']
        clear = options['clear']

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SESSION 810: Bootstrap Agent Relationships")
        self.stdout.write(f"{'='*60}\n")

        if clear and not dry_run:
            deleted = AgentRelationship.objects.all().delete()
            self.stdout.write(f"Cleared {deleted[0]} existing relationships")

        # Get all active agents grouped by category
        agents = Agent.objects.filter(is_active=True)
        self.stdout.write(f"Total active agents: {agents.count()}")

        # Group agents by category (use category name as string)
        agents_by_category = {}
        for agent in agents:
            # Get category name as lowercase string
            if agent.category:
                cat = agent.category.name.lower() if hasattr(agent.category, 'name') else str(agent.category).lower()
            else:
                cat = 'general'

            # Normalize category names to match our affinity keys
            cat_mapping = {
                'income generation': 'financial',
                'job search': 'research',
                'career development': 'strategy',
                'data analytics': 'research',
                'automation & efficiency': 'system',
                'business strategy': 'strategy',
                'marketing & growth': 'content',
                'financial management': 'financial',
                'ai & machine learning': 'development',
                'content creation': 'content',
                'creative & design': 'media',
                'consulting & advisory': 'executive',
                'research & analysis': 'research',
                'investment strategy': 'financial',
                'creative': 'media',
                'software development': 'development',
            }
            cat = cat_mapping.get(cat, cat)

            if cat not in agents_by_category:
                agents_by_category[cat] = []
            agents_by_category[cat].append(agent)

        self.stdout.write(f"Categories found: {list(agents_by_category.keys())}")

        created = 0
        skipped = 0

        # Create cross-category relationships
        for category, affinities in CATEGORY_AFFINITIES.items():
            if category not in agents_by_category:
                continue

            for related_category, rel_type, strength_range in affinities:
                if related_category not in agents_by_category:
                    continue

                # Create relationships between agents in these categories
                for agent_from in agents_by_category[category]:
                    for agent_to in agents_by_category[related_category]:
                        if agent_from == agent_to:
                            continue

                        # Check if relationship already exists
                        exists = AgentRelationship.objects.filter(
                            agent_from=agent_from,
                            agent_to=agent_to
                        ).exists()

                        if exists:
                            skipped += 1
                            continue

                        strength = random.uniform(*strength_range)

                        if dry_run:
                            self.stdout.write(
                                f"  [DRY RUN] {agent_from.name} -> {agent_to.name}: "
                                f"{rel_type} ({strength:.2f})"
                            )
                        else:
                            AgentRelationship.objects.create(
                                agent_from=agent_from,
                                agent_to=agent_to,
                                relationship_type=rel_type,
                                strength=strength,
                                trust_level=random.uniform(0.4, 0.8),
                                respect_level=random.uniform(0.5, 0.9),
                            )

                        created += 1

        # Create some same-category relationships
        for category, agents_list in agents_by_category.items():
            if len(agents_list) < 2:
                continue

            # Create a few relationships within the same category
            for i, agent_from in enumerate(agents_list):
                # Connect to 1-2 other agents in same category
                others = [a for a in agents_list if a != agent_from]
                sample_size = min(2, len(others))
                targets = random.sample(others, sample_size)

                for agent_to in targets:
                    exists = AgentRelationship.objects.filter(
                        agent_from=agent_from,
                        agent_to=agent_to
                    ).exists()

                    if exists:
                        skipped += 1
                        continue

                    rel_type = random.choice(SAME_CATEGORY_TYPES)
                    strength = random.uniform(0.4, 0.8)

                    if dry_run:
                        self.stdout.write(
                            f"  [DRY RUN] {agent_from.name} -> {agent_to.name}: "
                            f"{rel_type} ({strength:.2f}) [same category]"
                        )
                    else:
                        AgentRelationship.objects.create(
                            agent_from=agent_from,
                            agent_to=agent_to,
                            relationship_type=rel_type,
                            strength=strength,
                            trust_level=random.uniform(0.5, 0.9),
                            respect_level=random.uniform(0.5, 0.9),
                        )

                    created += 1

        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SUMMARY")
        self.stdout.write(f"{'='*60}")

        if dry_run:
            self.stdout.write(f"Would create: {created} relationships")
            self.stdout.write(f"Would skip (already exist): {skipped}")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created: {created} relationships"))
            self.stdout.write(f"Skipped (already exist): {skipped}")

            total = AgentRelationship.objects.count()
            self.stdout.write(f"\nTotal relationships in database: {total}")

            # Show breakdown by type
            from django.db.models import Count
            breakdown = AgentRelationship.objects.values('relationship_type').annotate(
                count=Count('id')
            )
            self.stdout.write("\nBy type:")
            for item in breakdown:
                self.stdout.write(f"  {item['relationship_type']}: {item['count']}")
