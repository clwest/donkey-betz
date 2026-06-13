"""
Management command to activate spider network and collect data
"""
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models_unified_system import SpiderData
from intelligence.spider_agent_connector import SpiderAgentConnector


class Command(BaseCommand):
    help = 'Activate spider network to collect data and route to agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--simulate',
            action='store_true',
            help='Simulate spider data collection with sample data',
        )
        parser.add_argument(
            '--process',
            action='store_true',
            help='Process existing spider data and route to agents',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of spider data entries to process',
        )

    def handle(self, *args, **options):
        simulate = options['simulate']
        process_only = options['process']
        limit = options['limit']

        if process_only:
            self.stdout.write(self.style.SUCCESS('Processing existing spider data...'))
            self._process_spider_data(limit)
        else:
            self.stdout.write(self.style.SUCCESS('Activating spider network...'))
            if simulate:
                self._simulate_spider_collection()
            else:
                self._activate_real_spiders()

            # Process collected data
            self._process_spider_data(limit)

    def _simulate_spider_collection(self):
        """Simulate spider data collection with sample data"""
        self.stdout.write('Creating simulated spider data...')

        # Define sample opportunities
        opportunities = [
            {
                'spider': 'Job Opportunity Spider',
                'data': {
                    'title': 'Senior Python Developer - Remote',
                    'company': 'TechCorp Inc.',
                    'salary': '$120,000 - $150,000',
                    'location': 'Remote',
                    'description': 'Looking for experienced Python developer with Django expertise',
                    'url': 'https://example.com/job/1',
                    'posted_date': datetime.now().isoformat()
                }
            },
            {
                'spider': 'Freelance Hunter Spider',
                'data': {
                    'title': 'Build AI-powered Dashboard',
                    'client': 'StartupX',
                    'budget': '$5,000 - $10,000',
                    'duration': '2-3 months',
                    'description': 'Need experienced developer to build real-time AI dashboard',
                    'skills': ['Python', 'React', 'WebSocket'],
                    'url': 'https://example.com/freelance/1'
                }
            },
            {
                'spider': 'Market Intelligence Spider',
                'data': {
                    'title': 'AI Market Growing 35% Annually',
                    'source': 'TechNews',
                    'category': 'Market Trends',
                    'insights': ['AI adoption accelerating', 'Enterprise AI spending up 50%'],
                    'impact_score': 8.5,
                    'url': 'https://example.com/market/1'
                }
            },
            {
                'spider': 'Content Discovery Spider',
                'data': {
                    'title': 'Top 10 AI Tools for Developers',
                    'source': 'DevBlog',
                    'category': 'Technology',
                    'tags': ['AI', 'Development', 'Tools'],
                    'engagement_score': 9.2,
                    'url': 'https://example.com/content/1'
                }
            },
            {
                'spider': 'Finance Monitor Spider',
                'data': {
                    'title': 'Tech Stocks Rally on AI Boom',
                    'ticker': 'TECH',
                    'price_change': '+5.3%',
                    'volume': '10M shares',
                    'analysis': 'Strong buy signal based on AI sector growth',
                    'url': 'https://example.com/finance/1'
                }
            },
            {
                'spider': 'Lead Generation Spider',
                'data': {
                    'title': 'Enterprise Client Seeking AI Solutions',
                    'company': 'BigCorp Ltd',
                    'budget': '$50,000+',
                    'needs': ['AI automation', 'Data analytics', 'Real-time processing'],
                    'decision_timeline': '30 days',
                    'url': 'https://example.com/lead/1'
                }
            },
            {
                'spider': 'Investment Tracker Spider',
                'data': {
                    'title': 'AI Startup Raises $10M Series A',
                    'company': 'AIVenture',
                    'valuation': '$50M',
                    'investors': ['VentureCapital', 'AngelFund'],
                    'focus': 'Enterprise AI solutions',
                    'url': 'https://example.com/investment/1'
                }
            },
            {
                'spider': 'Research Paper Spider',
                'data': {
                    'title': 'Novel Approach to Multi-Agent Learning',
                    'authors': ['Dr. Smith', 'Dr. Jones'],
                    'journal': 'AI Research Quarterly',
                    'abstract': 'New method improves agent collaboration by 40%',
                    'citations': 25,
                    'url': 'https://example.com/research/1'
                }
            }
        ]

        # Create spider data entries
        created_count = 0
        for _ in range(20):  # Create 20 entries
            opp = random.choice(opportunities)

            # Add some variation to the data
            spider_data = SpiderData.objects.create(
                spider_name=opp['spider'],
                data_type='opportunity' if 'Job' in opp['spider'] or 'Freelance' in opp['spider'] else 'intelligence',
                raw_data=opp['data'],
                source_url=opp['data'].get('url', 'https://example.com'),
                relevance_score=random.randint(70, 100),
                insights=[f"Insight {i+1}" for i in range(random.randint(1, 3))],
                is_processed=False,
                is_actionable=random.choice([True, False])
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} simulated spider data entries')
        )

    def _activate_real_spiders(self):
        """Activate real spiders from the spider registry"""
        try:
            from ai_core.spiders.job_spider import JobSpider
            from ai_core.spiders.freelance_spider import FreelanceSpider

            self.stdout.write('Activating real spiders...')

            # Try to run job spider
            try:
                job_spider = JobSpider()
                job_data = job_spider.scrape()  # This might need parameters

                for item in job_data:
                    SpiderData.objects.create(
                        spider_name='Job Spider',
                        data_type='opportunity',
                        raw_data=item,
                        source_url=item.get('url', ''),
                        relevance_score=85,
                        is_processed=False,
                        is_actionable=True
                    )

                self.stdout.write(f'Job Spider collected {len(job_data)} items')

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not activate Job Spider: {e}')
                )

            # Try to run freelance spider
            try:
                freelance_spider = FreelanceSpider()
                freelance_data = freelance_spider.find_opportunities()

                for item in freelance_data:
                    SpiderData.objects.create(
                        spider_name='Freelance Spider',
                        data_type='freelance',
                        raw_data=item,
                        source_url=item.get('url', ''),
                        relevance_score=80,
                        is_processed=False,
                        is_actionable=True
                    )

                self.stdout.write(f'Freelance Spider collected {len(freelance_data)} items')

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not activate Freelance Spider: {e}')
                )

        except ImportError as e:
            self.stdout.write(
                self.style.WARNING(f'Spider registry not available, using simulation: {e}')
            )
            self._simulate_spider_collection()

    def _process_spider_data(self, limit):
        """Process spider data and route to agents"""
        connector = SpiderAgentConnector()

        self.stdout.write('Processing spider data and routing to agents...')

        # Get unprocessed spider data
        unprocessed = SpiderData.objects.filter(
            is_processed=False
        ).order_by('-created_at')[:limit]

        if not unprocessed:
            self.stdout.write(
                self.style.WARNING('No unprocessed spider data found')
            )
            return

        processed_count = 0
        agents_notified = set()
        solutions_created = 0

        for spider_data in unprocessed:
            try:
                # Route the data
                result = connector.route_spider_data(spider_data)

                # Mark as processed
                spider_data.is_processed = True
                spider_data.processed_at = timezone.now()
                spider_data.save()

                # Track statistics
                processed_count += 1
                agents_notified.update(result.get('agents_notified', []))
                solutions_created += len(result.get('solutions_created', []))

                self.stdout.write(
                    f"  Processed: {spider_data.spider_name} -> "
                    f"{len(result.get('agents_notified', []))} agents notified"
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing spider data {spider_data.id}: {e}')
                )

        # Display summary
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('Spider Network Activation Summary:'))
        self.stdout.write(f'  Spider data processed: {processed_count}')
        self.stdout.write(f'  Unique agents notified: {len(agents_notified)}')
        self.stdout.write(f'  Solutions created: {solutions_created}')

        # Get routing statistics
        stats = connector.get_routing_statistics()
        self.stdout.write(f'  Success rate: {stats["success_rate"]:.1f}%')
        self.stdout.write(f'  Total spider data: {stats["total_spider_data"]}')
        self.stdout.write(f'  Unprocessed remaining: {stats.get("unprocessed_data", 0)}')

        # List notified agents
        if agents_notified:
            self.stdout.write('\nAgents that received data:')
            for agent in sorted(agents_notified):
                self.stdout.write(f'  - {agent}')

        self.stdout.write(self.style.SUCCESS('\nSpider network activation complete!'))