"""
Django management command to deploy the massive spider army
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import logging

from intelligence.spiders.spider_army.orchestrator import SpiderArmyOrchestrator
from intelligence.models import SpiderArmyStatus


class Command(BaseCommand):
    help = 'Deploy and manage the massive spider army for intelligence gathering'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['deploy', 'status', 'scale', 'emergency', 'shutdown'],
            default='deploy',
            help='Action to perform with spider army'
        )

        parser.add_argument(
            '--scale-factor',
            type=float,
            default=1.0,
            help='Scaling factor for spider army (deploy action)'
        )

        parser.add_argument(
            '--emergency-spiders',
            nargs='+',
            help='List of spider names for emergency deployment'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        """Handle the spider army management command"""

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if options['verbose'] else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        action = options['action']
        self.stdout.write(f"🕷️ Spider Army Command: {action.upper()}")

        try:
            if action == 'deploy':
                self.deploy_spider_army(options)
            elif action == 'status':
                self.show_army_status(options)
            elif action == 'scale':
                self.scale_spider_army(options)
            elif action == 'emergency':
                self.emergency_deployment(options)
            elif action == 'shutdown':
                self.shutdown_spider_army(options)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Spider army command failed: {e}')
            )
            raise CommandError(f'Spider army operation failed: {e}')

    def deploy_spider_army(self, options):
        """Deploy the complete spider army"""
        self.stdout.write("🚀 Deploying massive spider army...")

        try:
            orchestrator = SpiderArmyOrchestrator()

            # Deploy all spiders
            spider_count = orchestrator.deploy_massive_spider_army()

            # Apply scaling if specified
            scale_factor = options.get('scale_factor', 1.0)
            if scale_factor != 1.0:
                orchestrator.scale_spider_army(scale_factor)
                self.stdout.write(f"⚖️ Applied scale factor: {scale_factor}")

            # Start scheduler
            orchestrator.start_spider_army_scheduler()

            # Get initial status
            status = orchestrator.get_army_status()

            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully deployed {spider_count} spiders!')
            )

            # Store status in database
            self.store_army_status(status)

            # Print summary
            self.print_army_summary(status)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Deployment failed: {e}')
            )
            raise

    def show_army_status(self, options):
        """Show current spider army status"""
        self.stdout.write("📊 Spider Army Status Report")
        self.stdout.write("=" * 50)

        try:
            orchestrator = SpiderArmyOrchestrator()
            status = orchestrator.get_army_status()

            self.print_army_summary(status)

            if options['verbose']:
                self.print_detailed_status(status)

            # Store status snapshot
            self.store_army_status(status)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to get status: {e}')
            )
            raise

    def scale_spider_army(self, options):
        """Scale the spider army"""
        scale_factor = options.get('scale_factor', 1.0)

        if scale_factor <= 0:
            raise CommandError("Scale factor must be positive")

        self.stdout.write(f"⚖️ Scaling spider army by factor: {scale_factor}")

        try:
            orchestrator = SpiderArmyOrchestrator()
            orchestrator.scale_spider_army(scale_factor)

            status = orchestrator.get_army_status()
            self.store_army_status(status)

            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully scaled spider army')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Scaling failed: {e}')
            )
            raise

    def emergency_deployment(self, options):
        """Emergency deployment of specific spiders"""
        emergency_spiders = options.get('emergency_spiders', [])

        if not emergency_spiders:
            raise CommandError("Must specify --emergency-spiders for emergency deployment")

        self.stdout.write(f"🚨 EMERGENCY DEPLOYMENT: {', '.join(emergency_spiders)}")

        try:
            orchestrator = SpiderArmyOrchestrator()
            orchestrator.emergency_spider_deployment(emergency_spiders)

            self.stdout.write(
                self.style.SUCCESS(f'✅ Emergency deployment completed')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Emergency deployment failed: {e}')
            )
            raise

    def shutdown_spider_army(self, options):
        """Shutdown the spider army"""
        self.stdout.write("🛑 Shutting down spider army...")

        try:
            orchestrator = SpiderArmyOrchestrator()
            orchestrator.shutdown_spider_army()

            self.stdout.write(
                self.style.SUCCESS('✅ Spider army shutdown completed')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Shutdown failed: {e}')
            )
            raise

    def print_army_summary(self, status):
        """Print army status summary"""
        overview = status['army_overview']
        performance = status['performance_metrics']

        self.stdout.write(f"🕸️ Total Spiders: {overview['total_spiders_deployed']}")
        self.stdout.write(f"⚡ Active Spiders: {overview['active_spiders']}")
        self.stdout.write(f"😴 Dormant Spiders: {overview['dormant_spiders']}")
        self.stdout.write(f"📊 Army Status: {overview['army_status']}")
        self.stdout.write("")

        self.stdout.write("📈 Performance Metrics:")
        self.stdout.write(f"   Total Runs: {performance['total_runs']}")
        self.stdout.write(f"   Success Rate: {performance['success_rate_percent']}%")
        self.stdout.write(f"   Items Scraped: {performance['total_items_scraped']}")
        self.stdout.write(f"   Data Distributed: {performance['total_data_distributed']}")
        self.stdout.write("")

        # Agent/Advisor feeding stats
        agent_stats = status['agent_feeding_stats']
        advisor_stats = status['advisor_feeding_stats']

        self.stdout.write(f"🤖 Agents Fed: {len(agent_stats)}")
        self.stdout.write(f"🧠 Advisors Fed: {len(advisor_stats)}")

        # Top agents and advisors
        if agent_stats:
            top_agent = max(agent_stats.items(), key=lambda x: x[1])
            self.stdout.write(f"   Top Agent: {top_agent[0]} ({top_agent[1]} spiders)")

        if advisor_stats:
            top_advisor = max(advisor_stats.items(), key=lambda x: x[1])
            self.stdout.write(f"   Top Advisor: {top_advisor[0]} ({top_advisor[1]} spiders)")

    def print_detailed_status(self, status):
        """Print detailed spider status"""
        self.stdout.write("\n🕷️ Individual Spider Status:")
        self.stdout.write("-" * 50)

        spider_breakdown = status['spider_breakdown']

        for spider_name, spider_status in spider_breakdown.items():
            self.stdout.write(f"\n🕸️ {spider_name}:")
            self.stdout.write(f"   Priority: {spider_status['priority']}")
            self.stdout.write(f"   Frequency: {spider_status['frequency_minutes']} minutes")
            self.stdout.write(f"   Runs: {spider_status['total_runs']}")
            self.stdout.write(f"   Success Rate: {spider_status['success_rate']}%")
            self.stdout.write(f"   Items Scraped: {spider_status['items_scraped']}")

            if spider_status['target_agents']:
                self.stdout.write(f"   Target Agents: {', '.join(spider_status['target_agents'])}")

            if spider_status['target_advisors']:
                self.stdout.write(f"   Target Advisors: {', '.join(spider_status['target_advisors'])}")

            if spider_status['last_run']:
                self.stdout.write(f"   Last Run: {spider_status['last_run']}")

            if spider_status['next_run']:
                self.stdout.write(f"   Next Run: {spider_status['next_run']}")

    def store_army_status(self, status):
        """Store army status in database"""
        try:
            overview = status['army_overview']
            performance = status['performance_metrics']

            # Create status snapshot ID
            snapshot_id = f"army_status_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

            # Calculate today's stats (simplified - would need proper time filtering in production)
            spider_army_status = SpiderArmyStatus.objects.create(
                status_snapshot_id=snapshot_id,
                total_spiders_deployed=overview['total_spiders_deployed'],
                active_spiders=overview['active_spiders'],
                dormant_spiders=overview['dormant_spiders'],
                total_runs_today=performance['total_runs'],  # Simplified
                total_items_scraped_today=performance['total_items_scraped'],
                total_data_distributed_today=performance['total_data_distributed'],
                army_success_rate=performance['success_rate_percent'],
                agents_fed_today=len(status['agent_feeding_stats']),
                advisors_fed_today=len(status['advisor_feeding_stats']),
                spider_status_breakdown=status['spider_breakdown']
            )

            # Calculate and display reality score
            reality_score = spider_army_status.calculate_reality_score()
            self.stdout.write(f"\n🎯 REALITY SCORE: {reality_score:.1%}")

            if reality_score >= 0.95:
                self.stdout.write(
                    self.style.SUCCESS("🏆 EXCELLENT! Spider army is at 95%+ reality!")
                )
            elif reality_score >= 0.8:
                self.stdout.write(
                    self.style.SUCCESS("✅ GOOD! Spider army is functional and effective.")
                )
            elif reality_score >= 0.6:
                self.stdout.write(
                    self.style.WARNING("⚠️ MODERATE! Spider army needs optimization.")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ LOW REALITY! Spider army needs major improvements.")
                )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Failed to store status in database: {e}')
            )

    def print_success_tips(self):
        """Print tips for maximizing spider army effectiveness"""
        self.stdout.write("\n💡 Tips for Maximum Effectiveness:")
        self.stdout.write("   1. Monitor high-priority spiders (financial, job opportunities)")
        self.stdout.write("   2. Scale up successful spiders with high revenue generation")
        self.stdout.write("   3. Review and act on intelligence data quickly")
        self.stdout.write("   4. Ensure Redis is running for real-time distribution")
        self.stdout.write("   5. Check agent/advisor integration for data consumption")
        self.stdout.write("   6. Monitor for rate limiting and adjust delays accordingly")
        self.stdout.write("   7. Track revenue generation to measure ROI")
        self.stdout.write("   8. Use emergency deployment for time-sensitive opportunities")