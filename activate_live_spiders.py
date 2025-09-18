#!/usr/bin/env python3
"""
Live Spider Activation System
==============================
Actually starts the 13 working spiders to collect real data!
"""

import os
import sys
import django
import asyncio
import logging
import signal
from typing import Dict, List
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Import spider components
from backend.spiders.spider_registry import spider_registry
from backend.spiders.base_spider import SpiderTarget

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SpiderActivationSystem:
    """Manages activation and monitoring of live spiders"""

    def __init__(self):
        self.active_spiders = {}
        self.spider_tasks = {}
        self.is_running = False
        self.start_time = None

    async def activate_spider(self, spider_name: str, targets: List[SpiderTarget], subscribers: List[str]):
        """Activate a single spider"""
        try:
            spider_class = spider_registry.get_spider_class(spider_name)
            spider_config = spider_registry.get_spider_config(spider_name)

            # Create spider instance
            spider_id = f"{spider_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

            spider = spider_class(spider_id, targets, subscribers, redis_config)
            self.active_spiders[spider_name] = spider

            # Start spider in background
            task = asyncio.create_task(spider.start())
            self.spider_tasks[spider_name] = task

            logger.info(f"✅ Activated {spider_name} spider with {len(targets)} targets")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to activate {spider_name}: {e}")
            return False

    async def activate_all_spiders(self):
        """Activate all 13 working spiders with real targets"""

        logger.info("🚀 ACTIVATING LIVE SPIDER SYSTEM")
        logger.info("="*50)

        # Define real targets for each spider
        spider_configs = {
            'financial': {
                'targets': [
                    SpiderTarget(url='https://finance.yahoo.com/most-active'),
                    SpiderTarget(url='https://www.bloomberg.com/markets'),
                ],
                'subscribers': ['investment_advisor', 'wealth_builder', 'crypto_trader']
            },
            'innovation': {
                'targets': [
                    SpiderTarget(url='https://news.ycombinator.com/'),
                    SpiderTarget(url='https://www.producthunt.com/'),
                ],
                'subscribers': ['tech_scout', 'startup_advisor', 'research_analyst']
            },
            'social_sentiment': {
                'targets': [
                    SpiderTarget(url='https://www.reddit.com/r/technology/hot.json'),
                    SpiderTarget(url='https://www.reddit.com/r/startups/hot.json'),
                ],
                'subscribers': ['social_media_manager', 'brand_monitor', 'trend_analyst']
            },
            'market_data': {
                'targets': [
                    SpiderTarget(url='https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10'),
                ],
                'subscribers': ['day_trader', 'options_trader', 'crypto_trader']
            },
            'news_harvester': {
                'targets': [
                    SpiderTarget(url='https://newsapi.org/v2/top-headlines?country=us&category=technology'),
                    SpiderTarget(url='https://techcrunch.com/'),
                ],
                'subscribers': ['news_aggregator', 'pr_manager', 'content_curator']
            },
            'toptal': {
                'targets': [
                    SpiderTarget(url='https://www.toptal.com/developers'),
                ],
                'subscribers': ['freelance_finder', 'contract_negotiator', 'job_application_agent']
            },
            'guru': {
                'targets': [
                    SpiderTarget(url='https://www.guru.com/d/freelancers/'),
                ],
                'subscribers': ['freelance_finder', 'gig_economy_expert']
            },
            'peopleperhour': {
                'targets': [
                    SpiderTarget(url='https://www.peopleperhour.com/freelance-jobs'),
                ],
                'subscribers': ['freelance_finder', 'remote_work_specialist']
            },
            'ninetyninedesigns': {
                'targets': [
                    SpiderTarget(url='https://99designs.com/designers'),
                ],
                'subscribers': ['design_project_finder', 'creative_director']
            },
            'flexjobs': {
                'targets': [
                    SpiderTarget(url='https://www.flexjobs.com/remote-jobs'),
                ],
                'subscribers': ['remote_work_specialist', 'career_advisor']
            },
            'remoteok': {
                'targets': [
                    SpiderTarget(url='https://remoteok.io/remote-dev-jobs'),
                ],
                'subscribers': ['remote_work_specialist', 'digital_nomad_guide']
            },
            'medium': {
                'targets': [
                    SpiderTarget(url='https://medium.com/tag/technology'),
                ],
                'subscribers': ['content_creator', 'blog_monetizer', 'writer_assistant']
            },
            'gumroad': {
                'targets': [
                    SpiderTarget(url='https://discover.gumroad.com/'),
                ],
                'subscribers': ['digital_product_creator', 'online_course_builder', 'passive_income_generator']
            }
        }

        # Activate each spider
        self.is_running = True
        self.start_time = datetime.now()

        for spider_name, config in spider_configs.items():
            await self.activate_spider(
                spider_name,
                config['targets'],
                config['subscribers']
            )
            await asyncio.sleep(0.5)  # Stagger activations

        logger.info(f"\n✅ Activated {len(self.active_spiders)} spiders!")
        logger.info("📡 Spiders are now collecting real data...")

    async def monitor_spiders(self):
        """Monitor spider health and performance"""
        while self.is_running:
            await asyncio.sleep(30)  # Check every 30 seconds

            logger.info("\n📊 SPIDER STATUS UPDATE")
            logger.info("="*40)

            for spider_name, spider in self.active_spiders.items():
                metrics = spider.metrics
                logger.info(f"🕷️  {spider_name}:")
                logger.info(f"   📈 Data collected: {metrics.data_points_collected}")
                logger.info(f"   ✅ Success rate: {metrics.successful_requests}/{metrics.successful_requests + metrics.failed_requests}")
                logger.info(f"   ⚡ Avg response: {metrics.avg_response_time:.2f}s")

            # Calculate total stats
            total_data = sum(s.metrics.data_points_collected for s in self.active_spiders.values())
            logger.info(f"\n🎯 TOTAL DATA COLLECTED: {total_data}")

    async def shutdown(self):
        """Gracefully shutdown all spiders"""
        logger.info("\n🛑 Shutting down spider system...")
        self.is_running = False

        # Stop all spiders
        for spider_name, spider in self.active_spiders.items():
            await spider.stop()
            logger.info(f"   Stopped {spider_name}")

        # Cancel all tasks
        for task in self.spider_tasks.values():
            task.cancel()

        logger.info("✅ All spiders stopped successfully")

async def main():
    """Main execution function"""
    system = SpiderActivationSystem()

    # Handle shutdown signals
    def signal_handler(sig, frame):
        logger.info("\n⚠️  Received shutdown signal")
        asyncio.create_task(system.shutdown())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start spiders
        await system.activate_all_spiders()

        # Monitor in background
        monitor_task = asyncio.create_task(system.monitor_spiders())

        # Keep running until shutdown
        while system.is_running:
            await asyncio.sleep(1)

        await monitor_task

    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await system.shutdown()

if __name__ == "__main__":
    print("""
    🕷️  LIVE SPIDER ACTIVATION SYSTEM  🕷️
    =====================================

    This will start 13 real spiders collecting data from:
    • Finance sites (Yahoo, Bloomberg)
    • Tech sites (HackerNews, ProductHunt)
    • Freelance platforms (Toptal, Guru, etc.)
    • Content platforms (Medium, Gumroad)
    • Social platforms (Reddit)

    Press Ctrl+C to stop

    Starting in 3 seconds...
    """)

    asyncio.run(asyncio.sleep(3))
    asyncio.run(main())