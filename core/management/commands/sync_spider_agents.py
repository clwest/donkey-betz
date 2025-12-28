"""
Session 242: Sync Spider-Agent Connections

This command:
1. Creates SpiderCategory entries for all known spider categories
2. Connects agents to appropriate spider categories based on their specialization
3. Creates initial knowledge sources from spider data

Run with: python manage.py sync_spider_agents
"""

from django.core.management.base import BaseCommand
from core.models import Agent, SpiderCategory, AgentSpiderConnection, AgentKnowledgeSource


class Command(BaseCommand):
    help = 'Sync spider categories and connect them to appropriate agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        self.stdout.write("🕷️ SPIDER-AGENT CONNECTION SYNC - Session 242")
        self.stdout.write("=" * 60)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made\n"))

        # Step 1: Create spider categories
        self.stdout.write("\n📁 Step 1: Creating Spider Categories...")
        categories_created = self.create_spider_categories(dry_run)

        # Step 2: Connect agents to spider categories
        self.stdout.write("\n🔗 Step 2: Connecting Agents to Spider Categories...")
        connections_created = self.connect_agents_to_spiders(dry_run)

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ SYNC COMPLETE!"))
        self.stdout.write(f"📁 Spider Categories: {SpiderCategory.objects.count()}")
        self.stdout.write(f"🔗 Agent-Spider Connections: {AgentSpiderConnection.objects.count()}")
        self.stdout.write(f"🧠 Knowledge Sources: {AgentKnowledgeSource.objects.count()}")

    def create_spider_categories(self, dry_run=False):
        """Create spider category entries matching our registered spiders"""

        # These categories match what's in the spider_agent_connector routing table
        categories = [
            {
                'slug': 'tech',
                'name': 'Tech News & Innovation',
                'description': 'Technology news, startups, innovation trends from TechCrunch, Wired, HackerNews, etc.',
                'icon': '💻',
            },
            {
                'slug': 'financial',
                'name': 'Financial Markets',
                'description': 'Stock markets, crypto, forex from CoinGecko, Yahoo Finance, SeekingAlpha, etc.',
                'icon': '💰',
            },
            {
                'slug': 'freelance',
                'name': 'Freelance & Jobs',
                'description': 'Freelance opportunities from Upwork, Toptal, RemoteOK, WeWorkRemotely, etc.',
                'icon': '💼',
            },
            {
                'slug': 'creative_assets',
                'name': 'Creative Assets & Design',
                'description': 'Design trends, assets from Dribbble, Behance, CreativeMarket, Envato, etc.',
                'icon': '🎨',
            },
            {
                'slug': 'ai_creative',
                'name': 'AI & Creative Tools',
                'description': 'AI tools, models from HuggingFace, Civitai, RunwayML, Replicate, etc.',
                'icon': '🤖',
            },
            {
                'slug': 'digital_products',
                'name': 'Digital Products & E-commerce',
                'description': 'Digital products from Gumroad, Etsy, LemonSqueezy, AppSumo, etc.',
                'icon': '🛒',
            },
            {
                'slug': 'content_creation',
                'name': 'Content Creation',
                'description': 'Content platforms like Medium, Substack, YouTube trends, etc.',
                'icon': '📝',
            },
            {
                'slug': 'education',
                'name': 'Online Education',
                'description': 'Online courses from Udemy, Skillshare, Teachable, etc.',
                'icon': '📚',
            },
            {
                'slug': 'crowdfunding',
                'name': 'Crowdfunding & Startups',
                'description': 'Crowdfunding campaigns from Kickstarter, Indiegogo, ProductHunt, etc.',
                'icon': '🚀',
            },
            {
                'slug': 'news',
                'name': 'General News',
                'description': 'General news and updates from various sources',
                'icon': '📰',
            },
            {
                'slug': 'research',
                'name': 'Research & Academia',
                'description': 'Research papers, datasets from arXiv, Kaggle, etc.',
                'icon': '🔬',
            },
            {
                'slug': 'legal',
                'name': 'Legal Information',
                'description': 'Legal resources from CourtListener, Justia, FindLaw, etc.',
                'icon': '⚖️',
            },
        ]

        created_count = 0
        for cat_data in categories:
            if not dry_run:
                category, created = SpiderCategory.objects.get_or_create(
                    slug=cat_data['slug'],
                    defaults={
                        'name': cat_data['name'],
                        'description': cat_data['description'],
                        'icon': cat_data['icon'],
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f"  ✅ Created: {cat_data['name']}")
                else:
                    self.stdout.write(f"  ⏭️  Exists: {cat_data['name']}")
            else:
                self.stdout.write(f"  📋 Would create: {cat_data['name']}")
                created_count += 1

        return created_count

    def connect_agents_to_spiders(self, dry_run=False):
        """Connect agents to spider categories based on their specialization"""

        # Agent -> Spider Category mappings based on agent capabilities
        agent_spider_mappings = {
            # Research & Analysis agents get broad access
            'ResearchAgent': ['tech', 'financial', 'news', 'research', 'crowdfunding'],
            'TrendAnalysisAgent': ['tech', 'creative_assets', 'ai_creative', 'content_creation'],

            # Content/Creative agents
            'ImageAgent': ['creative_assets', 'ai_creative'],
            'VideoAgent': ['creative_assets', 'ai_creative', 'content_creation'],
            'AudioAgent': ['content_creation', 'ai_creative'],
            '3DGenerationAgent': ['creative_assets', 'ai_creative'],

            # Strategy agents
            'ContentStrategyAgent': ['content_creation', 'creative_assets', 'tech', 'crowdfunding'],
            'SEOOptimizerAgent': ['content_creation', 'tech', 'digital_products'],
            'BrandIdentityAgent': ['creative_assets', 'digital_products'],
            'SocialMediaAgent': ['content_creation', 'creative_assets', 'tech'],
            'CreativeDirectorAgent': ['creative_assets', 'ai_creative', 'content_creation'],

            # Opportunity & Revenue agents
            'OpportunityScoringAgent': ['freelance', 'financial', 'digital_products', 'crowdfunding'],

            # Workflow agents get wide access
            'WorkflowOrchestrationAgent': ['tech', 'creative_assets', 'ai_creative', 'content_creation'],

            # Training agents
            'CharacterTrainingAgent': ['creative_assets', 'ai_creative'],
            'TrainedCreationAgent': ['creative_assets', 'ai_creative'],

            # Executive agents
            'CTOAgent': ['tech', 'ai_creative', 'research'],
            'COOAgent': ['financial', 'freelance', 'digital_products'],
            'MeetingCoordinatorAgent': ['tech', 'news'],

            # General agents
            'CreationAgent': ['creative_assets', 'content_creation'],
            'PromptEngineeringAgent': ['ai_creative', 'creative_assets'],
        }

        connections_created = 0

        for agent_name, category_slugs in agent_spider_mappings.items():
            try:
                agent = Agent.objects.get(name=agent_name)

                for i, slug in enumerate(category_slugs):
                    try:
                        category = SpiderCategory.objects.get(slug=slug)

                        if not dry_run:
                            connection, created = AgentSpiderConnection.objects.get_or_create(
                                agent=agent,
                                spider_category=category,
                                defaults={
                                    'is_primary': i == 0,  # First category is primary
                                    'priority': i + 1,  # Lower priority number = higher priority
                                }
                            )
                            if created:
                                connections_created += 1
                                self.stdout.write(f"  ✅ {agent_name} ← {category.name}")
                        else:
                            self.stdout.write(f"  📋 Would connect: {agent_name} ← {category.name}")
                            connections_created += 1

                    except SpiderCategory.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"  ⚠️  Category not found: {slug}"))

            except Agent.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Agent not found: {agent_name}"))

        return connections_created
