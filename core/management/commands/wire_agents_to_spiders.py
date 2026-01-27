"""
Session 845: Wire ALL agents to appropriate spider data sources.
Creates AgentSpiderConnection records for agents missing connections.
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Wire all agents to appropriate spider categories for data integration'

    # Map agent keywords to spider category slugs
    AGENT_CATEGORY_MAPPING = {
        # Tech/Development agents
        'developer': ['tech', 'hackernews', 'devto'],
        'devops': ['tech', 'hackernews'],
        'code': ['tech', 'hackernews', 'devto'],
        'fullstack': ['tech', 'hackernews', 'devto'],
        'testing': ['tech'],
        'automation': ['tech', 'ai_creative'],
        'pipeline': ['tech'],
        'machine learning': ['tech', 'ai_creative', 'research'],
        'deep learning': ['tech', 'ai_creative', 'research'],
        'computer vision': ['tech', 'ai_creative'],
        'natural language': ['tech', 'ai_creative'],
        'data scientist': ['tech', 'research'],
        'smart contract': ['financial', 'tech'],
        'blockchain': ['financial', 'tech'],
        'robotic': ['tech', 'innovation'],

        # AI/Creative agents
        'image': ['ai_creative', 'creative_assets'],
        'video': ['ai_creative', 'creative_assets', 'content_creation'],
        'audio': ['ai_creative', 'content_creation'],
        '3d': ['ai_creative', 'creative_assets'],
        'ai': ['ai_creative', 'tech', 'innovation'],
        'creative director': ['ai_creative', 'creative_assets', 'content_creation'],
        'brand': ['creative_assets', 'content_creation'],
        'design': ['creative_assets', 'ai_creative'],
        'logo': ['creative_assets'],
        'typography': ['creative_assets'],
        'color': ['creative_assets'],
        'infographic': ['creative_assets', 'content_creation'],
        'motion graphics': ['creative_assets', 'ai_creative'],
        'ui/ux': ['creative_assets', 'tech'],

        # Content creation agents
        'content': ['content_creation', 'tech'],
        'writer': ['content_creation'],
        'blog': ['content_creation'],
        'newsletter': ['content_creation'],
        'podcast': ['content_creation'],
        'social media': ['content_creation'],
        'seo': ['content_creation', 'tech'],
        'copywriter': ['content_creation'],
        'video script': ['content_creation'],
        'white paper': ['content_creation', 'research'],
        'case study': ['content_creation'],
        'localization': ['content_creation'],
        'repurpos': ['content_creation'],

        # Financial/Markets agents
        'stock': ['financial'],
        'finance': ['financial'],
        'investment': ['financial'],
        'portfolio': ['financial'],
        'market': ['financial', 'news'],
        'trading': ['financial'],
        'whale': ['financial'],
        'arbitrage': ['financial', 'sports_betting'],
        'odds': ['sports_betting', 'financial'],
        'betting': ['sports_betting'],
        'prediction market': ['sports_betting', 'financial'],
        'prediction': ['sports_betting', 'financial'],
        'bookmaker': ['sports_betting'],
        'bull': ['financial'],
        'bear': ['financial'],
        'signal': ['financial'],
        'anomaly': ['financial'],
        'movement': ['financial'],
        'transaction': ['financial'],
        'institutional': ['financial'],
        'exploit': ['financial', 'tech'],
        'crypto': ['financial'],
        'defi': ['financial'],
        'budget': ['financial'],
        'debt': ['financial'],
        'tax': ['financial'],
        'credit': ['financial'],
        'savings': ['financial'],
        'retirement': ['financial'],
        'insurance': ['financial'],
        'expense': ['financial'],

        # Job/Career agents
        'job': ['freelance', 'news'],
        'career': ['freelance'],
        'resume': ['freelance'],
        'interview': ['freelance'],
        'linkedin': ['freelance', 'content_creation'],
        'recruiter': ['freelance'],
        'freelance': ['freelance'],
        'remote': ['freelance'],
        'gig': ['freelance'],
        'application': ['freelance'],
        'salary': ['freelance'],
        'employment': ['freelance'],
        'hiring': ['freelance'],
        'startup': ['freelance', 'crowdfunding', 'innovation'],
        'executive': ['freelance', 'news'],

        # Marketing agents
        'marketing': ['content_creation', 'digital_products'],
        'campaign': ['content_creation', 'digital_products'],
        'conversion': ['digital_products'],
        'growth': ['digital_products', 'crowdfunding'],
        'ppc': ['digital_products'],
        'email': ['content_creation', 'digital_products'],
        'influencer': ['content_creation'],
        'affiliate': ['digital_products'],
        'e-commerce': ['digital_products'],
        'analytics': ['digital_products', 'tech'],

        # Research/Analysis agents
        'research': ['research', 'news'],
        'analysis': ['research', 'news'],
        'trend': ['research', 'news', 'financial'],
        'competitive': ['research'],
        'sentiment': ['research', 'news'],
        'statistical': ['research'],
        'predictive': ['research', 'financial'],
        'survey': ['research'],
        'medical': ['research'],
        'patent': ['research', 'legal'],

        # Legal agents
        'legal': ['legal'],
        'contract': ['legal'],
        'compliance': ['legal'],
        'patent': ['legal', 'research'],

        # News/General agents
        'news': ['news', 'tech'],
        'intelligence': ['news', 'research'],
        'customer': ['research', 'digital_products'],

        # Income/Business agents
        'income': ['freelance', 'digital_products'],
        'revenue': ['digital_products', 'financial'],
        'business': ['crowdfunding', 'news'],
        'partnership': ['crowdfunding'],
        'consulting': ['freelance'],
        'subscription': ['digital_products'],
        'digital product': ['digital_products'],
        'passive': ['digital_products'],
        'royalty': ['digital_products'],
        'teaching': ['education'],
        'grant': ['crowdfunding', 'research'],

        # Education agents
        'education': ['education'],
        'skill': ['education', 'freelance'],
        'learning': ['education'],
        'training': ['education'],

        # System/Orchestration agents (broader connections)
        'orchestrat': ['tech', 'ai_creative'],
        'coordinator': ['tech', 'ai_creative'],
        'workflow': ['tech'],
        'system': ['tech'],
        'thinking': ['ai_creative', 'research'],
        'personal assistant': ['ai_creative', 'freelance', 'news'],
        'moderator': ['content_creation'],
        'resolve': ['tech'],
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate connections even for agents that already have them',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import Agent, SpiderCategory, AgentSpiderConnection

        dry_run = options.get('dry_run', False)
        force = options.get('force', False)

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("🕷️  SESSION 845: WIRING ALL AGENTS TO SPIDER DATA SOURCES")
        self.stdout.write("=" * 80)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n⚠️  DRY RUN MODE - No changes will be made\n"))

        # Step 1: Ensure all required SpiderCategories exist
        categories_created = self._ensure_spider_categories(dry_run)

        # Step 2: Get all agents and their current connection status
        if force:
            agents = Agent.objects.all()
        else:
            agents = Agent.objects.filter(spider_connections__isnull=True)

        total_agents = agents.count()
        all_agents_count = Agent.objects.count()

        self.stdout.write(f"\n📊 Agent Status:")
        self.stdout.write(f"   Total agents in system: {all_agents_count}")
        self.stdout.write(f"   Agents to wire: {total_agents}")

        if total_agents == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ All agents are already connected to spider categories!"))
            return

        # Step 3: Wire each agent to appropriate categories
        connections_created = 0
        agents_wired = 0
        connection_details = []

        categories = {cat.slug: cat for cat in SpiderCategory.objects.all()}

        for agent in agents:
            agent_categories = self._determine_categories_for_agent(agent)

            if not agent_categories:
                # Default fallback categories
                agent_categories = ['tech', 'news']

            agent_connections = []
            for i, cat_slug in enumerate(agent_categories):
                if cat_slug in categories:
                    is_primary = (i == 0)
                    priority = i + 1

                    if not dry_run:
                        conn, created = AgentSpiderConnection.objects.get_or_create(
                            agent=agent,
                            spider_category=categories[cat_slug],
                            defaults={
                                'is_primary': is_primary,
                                'priority': priority,
                            }
                        )
                        if created:
                            connections_created += 1
                            agent_connections.append(cat_slug)
                    else:
                        connections_created += 1
                        agent_connections.append(cat_slug)

            if agent_connections or dry_run:
                agents_wired += 1
                connection_details.append({
                    'agent': agent.name,
                    'categories': agent_categories[:3]  # Show first 3
                })

        # Step 4: Show results
        self.stdout.write("\n" + "-" * 80)
        self.stdout.write("📋 CONNECTION SUMMARY")
        self.stdout.write("-" * 80)

        # Show a sample of connections
        self.stdout.write("\n🔗 Sample Connections (first 20):")
        for detail in connection_details[:20]:
            cats = ', '.join(detail['categories'])
            self.stdout.write(f"   • {detail['agent'][:40]:<40} → [{cats}]")

        if len(connection_details) > 20:
            self.stdout.write(f"   ... and {len(connection_details) - 20} more agents")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("📊 FINAL STATISTICS")
        self.stdout.write("=" * 80)
        self.stdout.write(f"   Categories created: {categories_created}")
        self.stdout.write(f"   Agents wired: {agents_wired}")
        self.stdout.write(f"   Connections created: {connections_created}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\n⚠️  DRY RUN - Run without --dry-run to apply changes"))
        else:
            # Verify final count
            total_connected = Agent.objects.filter(spider_connections__isnull=False).distinct().count()
            total_connections = AgentSpiderConnection.objects.count()
            self.stdout.write(f"\n✅ Post-wiring status:")
            self.stdout.write(f"   Agents with connections: {total_connected}/{all_agents_count}")
            self.stdout.write(f"   Total AgentSpiderConnections: {total_connections}")

    def _ensure_spider_categories(self, dry_run=False):
        """Ensure all required spider categories exist."""
        from core.models_unified_system import SpiderCategory

        required_categories = [
            ('sports_betting', 'Sports Betting & Prediction Markets', '🎲', 'Sports odds, betting lines, prediction markets (Kalshi, TheOdds)'),
            ('tech', 'Tech News & Innovation', '💻', 'Technology news and updates'),
            ('financial', 'Financial Markets', '📈', 'Stock market, crypto, financial data'),
            ('news', 'General News', '📰', 'General news and current events'),
            ('ai_creative', 'AI & Creative Tools', '🤖', 'AI tools and creative technology'),
            ('content_creation', 'Content Creation', '✍️', 'Content creation and publishing'),
            ('creative_assets', 'Creative Assets & Design', '🎨', 'Design resources and creative assets'),
            ('crowdfunding', 'Crowdfunding & Startups', '🚀', 'Startup and crowdfunding platforms'),
            ('digital_products', 'Digital Products & E-commerce', '🛒', 'E-commerce and digital products'),
            ('freelance', 'Freelance & Jobs', '💼', 'Job postings and freelance opportunities'),
            ('research', 'Research & Academia', '🔬', 'Academic and research resources'),
            ('legal', 'Legal Information', '⚖️', 'Legal resources and information'),
            ('education', 'Online Education', '📚', 'Educational resources and courses'),
            ('hackernews', 'Hackernews', '🟠', 'Hacker News tech discussions'),
            ('devto', 'Devto', '👩‍💻', 'Dev.to developer community'),
            ('innovation', 'Innovation', '💡', 'Innovation and emerging tech'),
        ]

        created_count = 0
        for slug, name, icon, description in required_categories:
            if dry_run:
                exists = SpiderCategory.objects.filter(slug=slug).exists()
                if not exists:
                    self.stdout.write(f"   Would create category: {name} ({slug})")
                    created_count += 1
            else:
                cat, created = SpiderCategory.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'icon': icon,
                        'description': description,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Created category: {name}"))
                    created_count += 1

        return created_count

    def _determine_categories_for_agent(self, agent):
        """Determine which spider categories an agent should connect to."""
        name_lower = agent.name.lower()
        matched_categories = set()

        # Check each keyword mapping
        for keyword, categories in self.AGENT_CATEGORY_MAPPING.items():
            if keyword in name_lower:
                matched_categories.update(categories)

        # Return as sorted list (most specific categories first)
        priority_order = [
            'sports_betting', 'financial', 'tech', 'ai_creative', 'content_creation',
            'creative_assets', 'freelance', 'legal', 'research', 'education',
            'crowdfunding', 'digital_products', 'news', 'hackernews', 'devto', 'innovation'
        ]

        sorted_categories = []
        for cat in priority_order:
            if cat in matched_categories:
                sorted_categories.append(cat)

        return sorted_categories[:5]  # Max 5 categories per agent
