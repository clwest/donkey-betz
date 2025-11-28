"""
Session 243: Sync Agent Learning System

This command:
1. Populates AgentKnowledgeSource from SpiderData
2. Creates AgentLearningConnection between complementary agents
3. Enables the agent-to-agent knowledge sharing network

Run with: python manage.py sync_agent_learning
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
from core.models import (
    Agent, SpiderCategory, AgentSpiderConnection,
    AgentKnowledgeSource, AgentLearningConnection
)
from core.models_unified_system import SpiderData


class Command(BaseCommand):
    help = 'Sync agent learning system: populate knowledge from spiders and create agent connections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--knowledge-only',
            action='store_true',
            help='Only sync knowledge from spiders, skip agent connections',
        )
        parser.add_argument(
            '--connections-only',
            action='store_true',
            help='Only create agent connections, skip knowledge sync',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        knowledge_only = options.get('knowledge_only', False)
        connections_only = options.get('connections_only', False)

        self.stdout.write("🧠 AGENT LEARNING SYSTEM SYNC - Session 243")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        if not connections_only:
            # Step 1: Populate knowledge from spider data
            self.stdout.write("\n📚 Step 1: Populating Agent Knowledge from Spider Data...")
            knowledge_created = self.populate_knowledge_from_spiders(dry_run)

        if not knowledge_only:
            # Step 2: Create agent learning connections
            self.stdout.write("\n🔗 Step 2: Creating Agent Learning Connections...")
            connections_created = self.create_agent_learning_connections(dry_run)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ AGENT LEARNING SYNC COMPLETE!"))
        self.stdout.write(f"📚 Knowledge Sources: {AgentKnowledgeSource.objects.count()}")
        self.stdout.write(f"🔗 Agent Learning Connections: {AgentLearningConnection.objects.count()}")
        self.stdout.write(f"🕷️ Spider Data Processed: {SpiderData.objects.filter(is_processed=True).count()}")

    def populate_knowledge_from_spiders(self, dry_run=False):
        """Create AgentKnowledgeSource entries from SpiderData"""

        # Spider name to category mapping
        spider_to_category = {
            'financial': 'financial',
            'market_data': 'financial',
            'coingecko': 'financial',
            'yahoo_finance': 'financial',
            'seekingalpha': 'financial',
            'bloomberg_terminal': 'financial',
            'reuters_eikon': 'financial',
            'etherscan': 'financial',
            'opensea': 'financial',
            'innovation': 'tech',
            'techcrunch': 'tech',
            'theverge': 'tech',
            'wired': 'tech',
            'mit_tech_review': 'tech',
            'axios': 'tech',
            'hackernews': 'tech',
            'devto': 'tech',
            'hashnode': 'tech',
            'news_harvester': 'news',
            'social_sentiment': 'content_creation',
            'medium': 'content_creation',
            'substack': 'content_creation',
            'remoteok': 'freelance',
            'weworkremotely': 'freelance',
            'toptal': 'freelance',
            'guru': 'freelance',
            'ninetyninedesigns': 'freelance',
            'peopleperhour': 'freelance',
            'flexjobs': 'freelance',
            'angellist': 'freelance',
            'dribbble': 'creative_assets',
            'behance': 'creative_assets',
            'envato': 'creative_assets',
            'creativemarket': 'creative_assets',
            'adobestock': 'creative_assets',
            'shutterstock': 'creative_assets',
            'canva': 'creative_assets',
            'huggingface': 'ai_creative',
            'civitai': 'ai_creative',
            'runwayml': 'ai_creative',
            'replicate': 'ai_creative',
            'midjourney': 'ai_creative',
            'gumroad': 'digital_products',
            'etsy': 'digital_products',
            'lemonsqueezy': 'digital_products',
            'sellfy': 'digital_products',
            'appsumo': 'digital_products',
            'producthunt': 'crowdfunding',
            'indiegogo': 'crowdfunding',
            'kickstarter': 'crowdfunding',
            'kaggle': 'research',
            'teachable': 'education',
            'udemy': 'education',
            'skillshare': 'education',
            'patreon': 'content_creation',
            'kofi': 'content_creation',
        }

        # Data type to knowledge type mapping
        data_type_to_knowledge = {
            'trend': 'trend',
            'market': 'market',
            'opportunity': 'opportunity',
            'job': 'opportunity',
            'freelance': 'opportunity',
            'pricing': 'pricing',
            'article': 'content_idea',
            'post': 'content_idea',
            'tool': 'tool_discovery',
            'model': 'tool_discovery',
            'dataset': 'tool_discovery',
            'product': 'market',
            'news': 'trend',
            'sentiment': 'user_behavior',
        }

        # Get all spider data grouped by spider_name
        spider_data_groups = SpiderData.objects.values('spider_name').annotate(
            count=Count('id')
        ).order_by('-count')

        knowledge_created = 0

        for group in spider_data_groups:
            spider_name = group['spider_name']
            count = group['count']

            # Get the category for this spider
            category_slug = spider_to_category.get(spider_name, 'tech')
            try:
                category = SpiderCategory.objects.get(slug=category_slug)
            except SpiderCategory.DoesNotExist:
                category = None

            # Get agents connected to this category
            if category:
                connected_agents = Agent.objects.filter(
                    spider_categories=category,
                    is_active=True
                )
            else:
                connected_agents = Agent.objects.filter(is_active=True)[:3]

            if not connected_agents.exists():
                self.stdout.write(f"  ⚠️  No agents for {spider_name}, skipping")
                continue

            # Get sample data for this spider
            sample_data = SpiderData.objects.filter(spider_name=spider_name).order_by('-created_at')[:50]

            # Determine knowledge type from data_type
            for agent in connected_agents:
                # Group data by data_type to create knowledge entries
                data_by_type = {}
                for data in sample_data:
                    dt = data.data_type
                    if dt not in data_by_type:
                        data_by_type[dt] = []
                    data_by_type[dt].append(data)

                for data_type, data_list in data_by_type.items():
                    knowledge_type = data_type_to_knowledge.get(data_type, 'trend')

                    # Create a summary from the data
                    insights = []
                    for d in data_list[:5]:
                        if d.insights:
                            insights.extend(d.insights[:2] if isinstance(d.insights, list) else [])
                        if d.processed_data:
                            if isinstance(d.processed_data, dict):
                                title = d.processed_data.get('title', '')
                                if title:
                                    insights.append(title[:100])

                    # Create knowledge entry
                    title = f"{spider_name.replace('_', ' ').title()} - {data_type.replace('_', ' ').title()} Intelligence"
                    summary = f"Aggregated {len(data_list)} {data_type} data points from {spider_name}. "
                    if insights:
                        summary += f"Key findings: {', '.join(insights[:3])}"

                    if not dry_run:
                        knowledge, created = AgentKnowledgeSource.objects.get_or_create(
                            agent=agent,
                            title=title,
                            knowledge_type=knowledge_type,
                            defaults={
                                'spider_category': category,
                                'source_spider_names': [spider_name],
                                'summary': summary,
                                'key_insights': insights[:10],
                                'data_points_count': len(data_list),
                                'confidence_score': min(0.3 + (len(data_list) * 0.02), 0.95),
                                'relevance_score': sum(d.relevance_score for d in data_list) / len(data_list) / 100,
                                'freshness_score': 0.9,
                                'is_active': True,
                            }
                        )
                        if created:
                            knowledge_created += 1
                            self.stdout.write(f"  ✅ {agent.name} learned: {title[:50]}...")
                    else:
                        self.stdout.write(f"  📋 Would create: {agent.name} ← {title[:50]}...")
                        knowledge_created += 1

        # Mark spider data as processed
        if not dry_run:
            SpiderData.objects.filter(is_processed=False).update(
                is_processed=True,
                processed_at=timezone.now()
            )

        self.stdout.write(f"\n  📊 Knowledge entries created: {knowledge_created}")
        return knowledge_created

    def create_agent_learning_connections(self, dry_run=False):
        """Create learning connections between complementary agents"""

        # Define agent learning relationships
        # Format: (teacher, student, learning_type, shareable_knowledge_types)
        learning_relationships = [
            # Research teaches everyone about trends
            ('ResearchAgent', 'TrendAnalysisAgent', 'complementary', ['trend', 'market']),
            ('ResearchAgent', 'ContentStrategyAgent', 'complementary', ['trend', 'content_idea']),
            ('ResearchAgent', 'OpportunityScoringAgent', 'complementary', ['opportunity', 'market']),

            # Trend Analysis feeds creative agents
            ('TrendAnalysisAgent', 'ImageAgent', 'pipeline', ['trend', 'content_idea']),
            ('TrendAnalysisAgent', 'VideoAgent', 'pipeline', ['trend', 'content_idea']),
            ('TrendAnalysisAgent', 'ContentStrategyAgent', 'complementary', ['trend']),
            ('TrendAnalysisAgent', 'CreativeDirectorAgent', 'complementary', ['trend']),

            # Creative Director guides all creative agents
            ('CreativeDirectorAgent', 'ImageAgent', 'specialization', ['content_idea', 'trend']),
            ('CreativeDirectorAgent', 'VideoAgent', 'specialization', ['content_idea', 'trend']),
            ('CreativeDirectorAgent', 'AudioAgent', 'specialization', ['content_idea']),
            ('CreativeDirectorAgent', '3DGenerationAgent', 'specialization', ['content_idea']),
            ('CreativeDirectorAgent', 'BrandIdentityAgent', 'specialization', ['content_idea']),

            # Content Strategy orchestrates content creation
            ('ContentStrategyAgent', 'SEOOptimizerAgent', 'pipeline', ['content_idea']),
            ('ContentStrategyAgent', 'SocialMediaAgent', 'pipeline', ['content_idea', 'trend']),
            ('ContentStrategyAgent', 'ImageAgent', 'complementary', ['content_idea']),
            ('ContentStrategyAgent', 'VideoAgent', 'complementary', ['content_idea']),

            # SEO and Social Media share insights
            ('SEOOptimizerAgent', 'ContentStrategyAgent', 'validation', ['trend', 'user_behavior']),
            ('SocialMediaAgent', 'ContentStrategyAgent', 'validation', ['trend', 'user_behavior']),

            # Brand Identity works with visuals
            ('BrandIdentityAgent', 'ImageAgent', 'complementary', ['content_idea']),
            ('BrandIdentityAgent', 'VideoAgent', 'complementary', ['content_idea']),

            # Opportunity scoring informs strategy
            ('OpportunityScoringAgent', 'ContentStrategyAgent', 'pipeline', ['opportunity', 'market']),
            ('OpportunityScoringAgent', 'ResearchAgent', 'validation', ['opportunity']),

            # Image/Video cross-validation
            ('ImageAgent', 'VideoAgent', 'collaborative', ['tool_discovery', 'content_idea']),
            ('VideoAgent', 'ImageAgent', 'collaborative', ['tool_discovery', 'content_idea']),

            # Workflow orchestration learns from all
            ('WorkflowOrchestrationAgent', 'ResearchAgent', 'pipeline', ['trend', 'opportunity']),
            ('WorkflowOrchestrationAgent', 'ImageAgent', 'pipeline', ['content_idea']),
            ('WorkflowOrchestrationAgent', 'VideoAgent', 'pipeline', ['content_idea']),

            # Training agents share learnings
            ('CharacterTrainingAgent', 'TrainedCreationAgent', 'specialization', ['tool_discovery']),
            ('TrainedCreationAgent', 'ImageAgent', 'complementary', ['tool_discovery']),

            # Prompt Engineering teaches everyone
            ('PromptEngineeringAgent', 'ImageAgent', 'specialization', ['tool_discovery']),
            ('PromptEngineeringAgent', 'VideoAgent', 'specialization', ['tool_discovery']),
            ('PromptEngineeringAgent', '3DGenerationAgent', 'specialization', ['tool_discovery']),

            # Executive agents collaborate
            ('CTOAgent', 'COOAgent', 'collaborative', ['market', 'trend']),
            ('COOAgent', 'OpportunityScoringAgent', 'pipeline', ['opportunity', 'pricing']),
            ('CTOAgent', 'ResearchAgent', 'complementary', ['trend', 'tool_discovery']),

            # Creation agent learns from specialists
            ('CreationAgent', 'ImageAgent', 'complementary', ['content_idea']),
            ('CreationAgent', 'ContentStrategyAgent', 'complementary', ['content_idea']),
        ]

        connections_created = 0

        for teacher_name, student_name, learning_type, knowledge_types in learning_relationships:
            try:
                teacher = Agent.objects.get(name=teacher_name)
                student = Agent.objects.get(name=student_name)

                if not dry_run:
                    connection, created = AgentLearningConnection.objects.get_or_create(
                        teacher_agent=teacher,
                        student_agent=student,
                        defaults={
                            'learning_type': learning_type,
                            'shareable_knowledge_types': knowledge_types,
                            'is_active': True,
                            'strength': 0.7 if learning_type == 'specialization' else 0.5,
                        }
                    )
                    if created:
                        connections_created += 1
                        self.stdout.write(
                            f"  ✅ {teacher_name} → {student_name} ({learning_type})"
                        )
                else:
                    self.stdout.write(
                        f"  📋 Would connect: {teacher_name} → {student_name} ({learning_type})"
                    )
                    connections_created += 1

            except Agent.DoesNotExist as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠️  Agent not found: {teacher_name} or {student_name}")
                )

        self.stdout.write(f"\n  🔗 Learning connections created: {connections_created}")
        return connections_created
