"""
Session 790: Sync Persona Agent Learning

This command connects persona agents (from load_all_agents_advisors.py)
to the learning system by:
1. Creating AgentKnowledgeSource entries based on their domain
2. Creating learning connections between complementary persona agents
3. Enabling persona agents to participate in the knowledge network

Run with: python manage.py sync_persona_learning

On Railway:
    railway run python manage.py sync_persona_learning
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Agent, AgentKnowledgeSource, AgentLearningConnection, SpiderCategory
from core.services.persona_agent_context import (
    get_persona_context_builder,
    PERSONA_SPIDER_MAPPINGS
)

logger = logging.getLogger(__name__)


# Define learning relationships between persona agent types
# Format: (teacher_type, student_type, learning_type)
PERSONA_LEARNING_RELATIONSHIPS = [
    # Income agents teach career agents about monetization
    ('income', 'career', 'complementary'),
    ('income', 'job_search', 'complementary'),
    ('income', 'finance', 'pipeline'),

    # Finance agents share with investment and business
    ('finance', 'investment', 'specialization'),
    ('finance', 'business', 'complementary'),
    ('investment', 'finance', 'validation'),

    # Career and job search collaborate
    ('career', 'job_search', 'collaborative'),
    ('job_search', 'career', 'collaborative'),

    # Content and marketing work together
    ('content', 'marketing', 'pipeline'),
    ('marketing', 'content', 'validation'),
    ('marketing', 'social_media', 'specialization'),
    ('social_media', 'marketing', 'validation'),

    # AI/ML teaches development and automation
    ('ai_ml', 'development', 'complementary'),
    ('ai_ml', 'automation', 'specialization'),
    ('development', 'ai_ml', 'collaborative'),

    # Business strategy flows
    ('business', 'startup', 'specialization'),
    ('startup', 'business', 'validation'),
    ('business', 'consulting', 'complementary'),

    # Creative and content work together
    ('creative', 'content', 'complementary'),
    ('creative', 'video', 'specialization'),
    ('writing', 'content', 'specialization'),

    # Research feeds into analytics and business
    ('research', 'analytics', 'pipeline'),
    ('analytics', 'business', 'complementary'),
    ('analytics', 'market', 'specialization'),

    # Crypto and finance
    ('crypto', 'finance', 'complementary'),
    ('crypto', 'investment', 'complementary'),
]


class Command(BaseCommand):
    help = 'Sync persona agents with the learning system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )
        parser.add_argument(
            '--knowledge-only',
            action='store_true',
            help='Only create knowledge sources, skip learning connections',
        )
        parser.add_argument(
            '--connections-only',
            action='store_true',
            help='Only create learning connections, skip knowledge sources',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        knowledge_only = options.get('knowledge_only', False)
        connections_only = options.get('connections_only', False)

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("PERSONA AGENT LEARNING SYNC - Session 790"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        # Get persona context builder
        builder = get_persona_context_builder()

        # Get all agents
        all_agents = Agent.objects.filter(is_active=True)
        persona_agents = [a for a in all_agents if builder.is_persona_agent(a)]

        self.stdout.write(f"\nTotal agents: {all_agents.count()}")
        self.stdout.write(f"Persona agents: {len(persona_agents)}")
        self.stdout.write(f"Core agents: {all_agents.count() - len(persona_agents)}\n")

        if not connections_only:
            # Step 1: Create knowledge sources for persona agents
            self.stdout.write(self.style.NOTICE("\n📚 Step 1: Creating Knowledge Sources for Persona Agents..."))
            knowledge_created = self.create_knowledge_sources(persona_agents, builder, dry_run)
            self.stdout.write(f"  Knowledge sources created: {knowledge_created}")

        if not knowledge_only:
            # Step 2: Create learning connections between persona agents
            self.stdout.write(self.style.NOTICE("\n🔗 Step 2: Creating Learning Connections..."))
            connections_created = self.create_learning_connections(persona_agents, dry_run)
            self.stdout.write(f"  Learning connections created: {connections_created}")

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ PERSONA LEARNING SYNC COMPLETE!"))
        self.stdout.write(f"📚 Total Knowledge Sources: {AgentKnowledgeSource.objects.count()}")
        self.stdout.write(f"🔗 Total Learning Connections: {AgentLearningConnection.objects.count()}")
        self.stdout.write("=" * 60)

    def create_knowledge_sources(self, persona_agents, builder, dry_run=False):
        """Create AgentKnowledgeSource entries for persona agents."""
        created_count = 0

        for agent in persona_agents:
            # Get knowledge summary for this agent
            summary_data = builder.get_knowledge_summary_for_agent(agent)

            if not summary_data or summary_data.get('data_count', 0) == 0:
                self.stdout.write(f"  ⏭️  {agent.name}: No spider data available")
                continue

            # Get or create spider category for this agent
            agent_type = agent.agent_type or 'general'
            try:
                category = SpiderCategory.objects.filter(slug=agent_type).first()
            except Exception:
                category = None

            # Create knowledge source
            title = f"{agent.name} - Domain Intelligence"
            knowledge_type = 'trend'  # Default type for persona agent knowledge

            if not dry_run:
                knowledge, created = AgentKnowledgeSource.objects.get_or_create(
                    agent=agent,
                    title=title,
                    knowledge_type=knowledge_type,
                    defaults={
                        'spider_category': category,
                        'source_spider_names': summary_data.get('spiders', []),
                        'summary': summary_data.get('summary', ''),
                        'key_insights': summary_data.get('key_insights', []),
                        'data_points_count': summary_data.get('data_count', 0),
                        'confidence_score': 0.7,
                        'relevance_score': 0.8,
                        'freshness_score': 0.9,
                        'is_active': True,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"  ✅ {agent.name}: Created knowledge source")
                else:
                    # Update existing
                    knowledge.summary = summary_data.get('summary', knowledge.summary)
                    knowledge.key_insights = summary_data.get('key_insights', knowledge.key_insights)
                    knowledge.data_points_count = summary_data.get('data_count', knowledge.data_points_count)
                    knowledge.freshness_score = 1.0
                    knowledge.save()
                    self.stdout.write(f"  🔄 {agent.name}: Updated knowledge source")
            else:
                self.stdout.write(f"  📋 Would create: {title}")
                created_count += 1

        return created_count

    def create_learning_connections(self, persona_agents, dry_run=False):
        """Create learning connections between persona agents based on their types."""
        created_count = 0

        # Group agents by type
        agents_by_type = {}
        for agent in persona_agents:
            agent_type = agent.agent_type or 'general'
            if agent_type not in agents_by_type:
                agents_by_type[agent_type] = []
            agents_by_type[agent_type].append(agent)

        self.stdout.write(f"\n  Agent types found: {list(agents_by_type.keys())}")

        # Create connections based on relationships
        for teacher_type, student_type, learning_type in PERSONA_LEARNING_RELATIONSHIPS:
            teachers = agents_by_type.get(teacher_type, [])
            students = agents_by_type.get(student_type, [])

            if not teachers or not students:
                continue

            # Connect a sample of teachers to students (not all-to-all)
            # Pick up to 3 teachers and 3 students to avoid explosion
            for teacher in teachers[:3]:
                for student in students[:3]:
                    if teacher.id == student.id:
                        continue

                    # Determine shareable knowledge types based on teacher's domain
                    mapping = PERSONA_SPIDER_MAPPINGS.get(teacher_type, {})
                    shareable_types = ['trend', 'market', 'opportunity']
                    if 'finance' in teacher_type or 'investment' in teacher_type:
                        shareable_types = ['market', 'pricing', 'opportunity']
                    elif 'content' in teacher_type or 'marketing' in teacher_type:
                        shareable_types = ['trend', 'content_idea', 'user_behavior']

                    if not dry_run:
                        connection, created = AgentLearningConnection.objects.get_or_create(
                            teacher_agent=teacher,
                            student_agent=student,
                            defaults={
                                'learning_type': learning_type,
                                'shareable_knowledge_types': shareable_types,
                                'is_active': True,
                                'strength': 0.6,
                            }
                        )
                        if created:
                            created_count += 1
                            self.stdout.write(
                                f"  ✅ {teacher.name} → {student.name} ({learning_type})"
                            )
                    else:
                        self.stdout.write(
                            f"  📋 Would connect: {teacher.name} → {student.name} ({learning_type})"
                        )
                        created_count += 1

        return created_count
