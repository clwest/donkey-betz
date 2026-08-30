"""
Spider Army Orchestrator
Massive coordination system for deploying and managing thousands of spiders
"""

import logging
import json
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os

# Add Django setup
sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()



@dataclass
class SpiderConfig:
    """Configuration for individual spider deployment"""
    spider_name: str
    spider_class: str
    target_agents: List[str]
    target_advisors: List[str]
    priority: int = 5  # 1-10, 10 being highest
    frequency_minutes: int = 60  # How often to run
    concurrent_requests: int = 16
    download_delay: float = 1.0
    custom_settings: Dict[str, Any] = None


@dataclass
class SpiderMetrics:
    """Spider performance metrics"""
    spider_name: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    items_scraped: int = 0
    data_distributed: int = 0
    agents_fed: int = 0
    avg_execution_time: float = 0.0
    last_run_time: Optional[datetime] = None
    next_scheduled_run: Optional[datetime] = None


class SpiderArmyOrchestrator:
    """
    Supreme orchestrator for the massive spider army
    Manages deployment, scheduling, monitoring, and data distribution
    """

    def __init__(self):
        self.logger = logging.getLogger('spider_army.orchestrator')
        self.redis_client = self.setup_redis()
        self.spider_configs = {}
        self.spider_metrics = {}
        self.active_spiders = {}

        # Setup Scrapy settings
        self.settings = get_project_settings()
        self.setup_scrapy_settings()

        self.logger.info("🕷️ Spider Army Orchestrator initialized")

    def setup_redis(self) -> redis.Redis:
        """Setup Redis connection for coordination"""
        try:
            from django.conf import settings
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            client.ping()
            self.logger.info("✅ Redis connection established")
            return client
        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
            raise

    def setup_scrapy_settings(self):
        """Configure Scrapy settings for the spider army"""
        self.settings.set('ROBOTSTXT_OBEY', True)
        self.settings.set('CONCURRENT_REQUESTS', 32)
        self.settings.set('CONCURRENT_REQUESTS_PER_DOMAIN', 16)
        self.settings.set('DOWNLOAD_DELAY', 1)
        self.settings.set('RANDOMIZE_DOWNLOAD_DELAY', 0.5)
        self.settings.set('AUTOTHROTTLE_ENABLED', True)
        self.settings.set('AUTOTHROTTLE_START_DELAY', 1)
        self.settings.set('AUTOTHROTTLE_MAX_DELAY', 60)
        self.settings.set('HTTPCACHE_ENABLED', True)
        self.settings.set('HTTPCACHE_EXPIRATION_SECS', 3600)

        # User agents rotation
        self.settings.set('USER_AGENT', 'spider_army (+http://www.donkeybetz.com)')

    def deploy_massive_spider_army(self):
        """Deploy the complete spider army with all specialized spiders"""

        self.logger.info("🚀 Deploying MASSIVE spider army...")

        # Job hunting spiders for income builders
        job_spider_configs = [
            SpiderConfig(
                spider_name='upwork_opportunities',
                spider_class='intelligence.spiders.spider_army.spiders.job_hunter_spider.UpworkOpportunitiesSpider',
                target_agents=['income_builder', 'freelance_scout_agent', 'opportunity_analyzer'],
                target_advisors=[],
                priority=8,
                frequency_minutes=30
            ),
            SpiderConfig(
                spider_name='freelancer_opportunities',
                spider_class='intelligence.spiders.spider_army.spiders.job_hunter_spider.FreelancerOpportunitiesSpider',
                target_agents=['income_builder', 'freelance_scout_agent'],
                target_advisors=[],
                priority=7,
                frequency_minutes=45
            ),
            SpiderConfig(
                spider_name='fiverr_gig_analyzer',
                spider_class='intelligence.spiders.spider_army.spiders.job_hunter_spider.FiverrGigAnalyzerSpider',
                target_agents=['income_builder', 'gig_optimizer'],
                target_advisors=[],
                priority=6,
                frequency_minutes=60
            ),
            SpiderConfig(
                spider_name='indeed_jobs',
                spider_class='intelligence.spiders.spider_army.spiders.job_hunter_spider.IndeedJobSpider',
                target_agents=['career_development_agent', 'job_market_analyzer'],
                target_advisors=[],
                priority=7,
                frequency_minutes=30
            )
        ]

        # Financial intelligence spiders for advisors
        financial_spider_configs = [
            SpiderConfig(
                spider_name='stock_news',
                spider_class='intelligence.spiders.spider_army.spiders.financial_spider.StockNewsSpider',
                target_agents=['financial_analysis_agent', 'market_research_agent'],
                target_advisors=['warren_buffett', 'cathie_wood', 'ray_dalio'],
                priority=9,
                frequency_minutes=15
            ),
            SpiderConfig(
                spider_name='crypto_intelligence',
                spider_class='intelligence.spiders.spider_army.spiders.financial_spider.CryptoIntelligenceSpider',
                target_agents=['crypto_trader', 'blockchain_analyst'],
                target_advisors=['cathie_wood', 'michael_saylor'],
                priority=8,
                frequency_minutes=20
            ),
            SpiderConfig(
                spider_name='market_data',
                spider_class='intelligence.spiders.spider_army.spiders.financial_spider.MarketDataSpider',
                target_agents=['trading_agent_1', 'trading_agent_2', 'trading_agent_3'],
                target_advisors=['ray_dalio', 'paul_tudor_jones'],
                priority=10,
                frequency_minutes=5  # Very frequent for real-time trading
            ),
            SpiderConfig(
                spider_name='sec_filings',
                spider_class='intelligence.spiders.spider_army.spiders.financial_spider.SECFilingsSpider',
                target_agents=['value_investing_agent', 'fundamental_analyst'],
                target_advisors=['warren_buffett', 'charlie_munger'],
                priority=8,
                frequency_minutes=240  # 4 hours - SEC filings don't change often
            )
        ]

        # Content monetization spiders
        content_spider_configs = [
            SpiderConfig(
                spider_name='youtube_analyzer',
                spider_class='intelligence.spiders.spider_army.spiders.content_monetization_spider.YouTubeChannelAnalyzerSpider',
                target_agents=['content_creator_agent', 'viral_content_analyzer'],
                target_advisors=[],
                priority=7,
                frequency_minutes=60
            ),
            SpiderConfig(
                spider_name='substack_analyzer',
                spider_class='intelligence.spiders.spider_army.spiders.content_monetization_spider.SubstackNewsletterSpider',
                target_agents=['newsletter_creator', 'subscription_optimizer'],
                target_advisors=[],
                priority=6,
                frequency_minutes=120
            ),
            SpiderConfig(
                spider_name='twitter_trends',
                spider_class='intelligence.spiders.spider_army.spiders.content_monetization_spider.TwitterInfluencerSpider',
                target_agents=['social_media_agent', 'trend_analyzer'],
                target_advisors=[],
                priority=5,
                frequency_minutes=30
            )
        ]

        # Advisor-specific intelligence spiders
        advisor_spider_configs = [
            SpiderConfig(
                spider_name='berkshire_intelligence',
                spider_class='intelligence.spiders.spider_army.spiders.advisor_intelligence_spider.BerkshireHathawaySpider',
                target_agents=['berkshire_analyzer', 'value_investing_agent'],
                target_advisors=['warren_buffett', 'charlie_munger'],
                priority=10,
                frequency_minutes=60
            ),
            SpiderConfig(
                spider_name='cathie_wood_innovation',
                spider_class='intelligence.spiders.spider_army.spiders.advisor_intelligence_spider.CathieWoodInnovationSpider',
                target_agents=['innovation_scout', 'disruptive_tech_analyzer'],
                target_advisors=['cathie_wood', 'marc_andreessen'],
                priority=9,
                frequency_minutes=45
            ),
            SpiderConfig(
                spider_name='ray_dalio_macro',
                spider_class='intelligence.spiders.spider_army.spiders.advisor_intelligence_spider.RayDalioMacroSpider',
                target_agents=['macro_analyst', 'economic_cycle_tracker'],
                target_advisors=['ray_dalio', 'paul_tudor_jones'],
                priority=9,
                frequency_minutes=30
            ),
            SpiderConfig(
                spider_name='peter_thiel_startups',
                spider_class='intelligence.spiders.spider_army.spiders.advisor_intelligence_spider.PeterThielStartupSpider',
                target_agents=['startup_analyzer', 'venture_scout'],
                target_advisors=['peter_thiel', 'paul_graham'],
                priority=8,
                frequency_minutes=90
            )
        ]

        # Combine all spider configurations
        all_configs = (
            job_spider_configs +
            financial_spider_configs +
            content_spider_configs +
            advisor_spider_configs
        )

        # Register all spider configurations
        for config in all_configs:
            self.register_spider(config)

        self.logger.info(f"🕸️ Deployed {len(all_configs)} specialized spiders to the army!")

        return len(all_configs)

    def register_spider(self, config: SpiderConfig):
        """Register a spider configuration"""
        self.spider_configs[config.spider_name] = config
        self.spider_metrics[config.spider_name] = SpiderMetrics(
            spider_name=config.spider_name
        )

        # Store in Redis for persistence
        redis_key = f"spider_config:{config.spider_name}"
        self.redis_client.setex(
            redis_key,
            86400 * 7,  # 7 days TTL
            json.dumps(asdict(config), default=str)
        )

        self.logger.info(f"📋 Registered spider: {config.spider_name}")

    def start_spider_army_scheduler(self):
        """Start the spider army scheduler"""
        self.logger.info("⏰ Starting spider army scheduler...")

        # Schedule all spiders based on their frequency
        for spider_name, config in self.spider_configs.items():
            self.schedule_spider(spider_name, config)

        self.logger.info("🎯 All spiders scheduled!")

    def schedule_spider(self, spider_name: str, config: SpiderConfig):
        """Schedule a spider to run at specified intervals"""
        def run_spider():
            try:
                self.logger.info(f"🕷️ Launching spider: {spider_name}")

                # Update metrics
                metrics = self.spider_metrics[spider_name]
                metrics.total_runs += 1
                metrics.last_run_time = datetime.now()
                metrics.next_scheduled_run = datetime.now() + timedelta(minutes=config.frequency_minutes)

                # Launch spider
                self.launch_single_spider(config)

                metrics.successful_runs += 1

            except Exception as e:
                self.logger.error(f"❌ Spider {spider_name} failed: {e}")
                metrics.failed_runs += 1

            # Store updated metrics
            self.store_spider_metrics(spider_name, metrics)

            # Schedule next run
            self.schedule_next_run(spider_name, config)

        # Initial run after a small delay to stagger startup
        import threading
        timer = threading.Timer(config.priority, run_spider)  # Use priority as initial delay
        timer.start()

    def schedule_next_run(self, spider_name: str, config: SpiderConfig):
        """Schedule the next run of a spider"""
        import threading

        def delayed_run():
            self.schedule_spider(spider_name, config)

        # Schedule next run based on frequency
        delay_seconds = config.frequency_minutes * 60
        timer = threading.Timer(delay_seconds, delayed_run)
        timer.start()

    def launch_single_spider(self, config: SpiderConfig):
        """Launch a single spider"""
        try:
            # Import spider class dynamically
            module_path, class_name = config.spider_class.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            spider_class = getattr(module, class_name)

            # Create spider settings
            spider_settings = self.settings.copy()
            spider_settings.set('CONCURRENT_REQUESTS', config.concurrent_requests)
            spider_settings.set('DOWNLOAD_DELAY', config.download_delay)

            if config.custom_settings:
                for key, value in config.custom_settings.items():
                    spider_settings.set(key, value)

            # Create and run spider
            process = CrawlerProcess(spider_settings)
            process.crawl(spider_class)
            process.start()

        except Exception as e:
            self.logger.error(f"❌ Failed to launch spider {config.spider_name}: {e}")
            raise

    def store_spider_metrics(self, spider_name: str, metrics: SpiderMetrics):
        """Store spider metrics in Redis"""
        redis_key = f"spider_metrics:{spider_name}"
        self.redis_client.setex(
            redis_key,
            86400 * 30,  # 30 days TTL
            json.dumps(asdict(metrics), default=str)
        )

    def get_army_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the spider army"""
        total_spiders = len(self.spider_configs)
        active_spiders = len([m for m in self.spider_metrics.values() if m.last_run_time])

        total_runs = sum(m.total_runs for m in self.spider_metrics.values())
        successful_runs = sum(m.successful_runs for m in self.spider_metrics.values())
        failed_runs = sum(m.failed_runs for m in self.spider_metrics.values())
        total_items = sum(m.items_scraped for m in self.spider_metrics.values())
        total_distributed = sum(m.data_distributed for m in self.spider_metrics.values())

        success_rate = (successful_runs / max(1, total_runs)) * 100

        status = {
            'army_overview': {
                'total_spiders_deployed': total_spiders,
                'active_spiders': active_spiders,
                'dormant_spiders': total_spiders - active_spiders,
                'army_status': 'OPERATIONAL' if active_spiders > 0 else 'STANDBY'
            },
            'performance_metrics': {
                'total_runs': total_runs,
                'successful_runs': successful_runs,
                'failed_runs': failed_runs,
                'success_rate_percent': round(success_rate, 2),
                'total_items_scraped': total_items,
                'total_data_distributed': total_distributed
            },
            'spider_breakdown': {},
            'agent_feeding_stats': self.get_agent_feeding_stats(),
            'advisor_feeding_stats': self.get_advisor_feeding_stats(),
            'last_updated': datetime.now().isoformat()
        }

        # Add individual spider status
        for spider_name, metrics in self.spider_metrics.items():
            config = self.spider_configs[spider_name]
            status['spider_breakdown'][spider_name] = {
                'priority': config.priority,
                'frequency_minutes': config.frequency_minutes,
                'target_agents': config.target_agents,
                'target_advisors': config.target_advisors,
                'total_runs': metrics.total_runs,
                'success_rate': round((metrics.successful_runs / max(1, metrics.total_runs)) * 100, 2),
                'items_scraped': metrics.items_scraped,
                'last_run': metrics.last_run_time.isoformat() if metrics.last_run_time else None,
                'next_run': metrics.next_scheduled_run.isoformat() if metrics.next_scheduled_run else None
            }

        return status

    def get_agent_feeding_stats(self) -> Dict[str, int]:
        """Get statistics on which agents are being fed data"""
        agent_feeds = {}

        for config in self.spider_configs.values():
            for agent in config.target_agents:
                agent_feeds[agent] = agent_feeds.get(agent, 0) + 1

        return agent_feeds

    def get_advisor_feeding_stats(self) -> Dict[str, int]:
        """Get statistics on which advisors are being fed data"""
        advisor_feeds = {}

        for config in self.spider_configs.values():
            for advisor in config.target_advisors:
                advisor_feeds[advisor] = advisor_feeds.get(advisor, 0) + 1

        return advisor_feeds

    def emergency_spider_deployment(self, priority_spiders: List[str]):
        """Emergency deployment of specific high-priority spiders"""
        self.logger.warning(f"🚨 EMERGENCY SPIDER DEPLOYMENT: {priority_spiders}")

        for spider_name in priority_spiders:
            if spider_name in self.spider_configs:
                config = self.spider_configs[spider_name]
                config.priority = 10  # Max priority
                config.frequency_minutes = 5  # Very frequent

                # Launch immediately
                try:
                    self.launch_single_spider(config)
                    self.logger.info(f"🚀 Emergency launch successful: {spider_name}")
                except Exception as e:
                    self.logger.error(f"💥 Emergency launch failed for {spider_name}: {e}")

    def scale_spider_army(self, scale_factor: float):
        """Scale the entire spider army up or down"""
        self.logger.info(f"⚖️ Scaling spider army by factor: {scale_factor}")

        for config in self.spider_configs.values():
            # Adjust frequency (lower is more frequent)
            new_frequency = max(5, int(config.frequency_minutes / scale_factor))
            config.frequency_minutes = new_frequency

            # Adjust concurrent requests
            new_concurrent = max(1, int(config.concurrent_requests * scale_factor))
            config.concurrent_requests = new_concurrent

            self.logger.debug(f"📈 Scaled {config.spider_name}: freq={new_frequency}min, concurrent={new_concurrent}")

    def shutdown_spider_army(self):
        """Gracefully shutdown the spider army"""
        self.logger.info("🛑 Shutting down spider army...")

        # Stop all active spiders
        for spider_name in self.active_spiders:
            try:
                # Implementation would depend on how spiders are tracked
                self.logger.info(f"🔌 Stopping spider: {spider_name}")
            except Exception as e:
                self.logger.error(f"❌ Error stopping {spider_name}: {e}")

        # Store final metrics
        for spider_name, metrics in self.spider_metrics.items():
            self.store_spider_metrics(spider_name, metrics)

        self.logger.info("✅ Spider army shutdown complete")


# Convenience functions for external use
def deploy_spider_army():
    """Deploy the complete spider army"""
    orchestrator = SpiderArmyOrchestrator()
    spider_count = orchestrator.deploy_massive_spider_army()
    orchestrator.start_spider_army_scheduler()
    return orchestrator, spider_count


def get_army_status():
    """Get current spider army status"""
    orchestrator = SpiderArmyOrchestrator()
    return orchestrator.get_army_status()


if __name__ == "__main__":
    # Direct execution for testing
    orchestrator, count = deploy_spider_army()
    print(f"🕷️ Deployed {count} spiders!")

    # Print status after a short delay
    import time
    time.sleep(10)
    status = orchestrator.get_army_status()
    print("🕸️ Army Status:")
    print(json.dumps(status, indent=2))