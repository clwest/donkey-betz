#!/usr/bin/env python
"""
Overnight Autonomous Learning Test
===================================
Runs spiders and agents continuously to test autonomous learning system.
Completely local - NO public deployment.

This script:
1. Deploys spiders to collect real data
2. Executes agents periodically to trigger learning
3. Monitors learning record creation
4. Logs everything for morning review
5. Runs safely overnight (can be stopped anytime)

Usage:
    python scripts/overnight_learning_test.py --duration 480  # 8 hours
"""

import os
import sys
import django
import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models_unified_system import AgentExecution, UserAgentLearning, Agent
from persistence.models import SpiderData
from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator
from ai_core.agents.concrete_executor import execute_agent_sync

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('overnight_learning_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

User = get_user_model()

class OvernightLearningTest:
    """Orchestrates overnight autonomous learning test"""

    def __init__(self, user, duration_minutes=480):
        self.user = user
        self.duration_minutes = duration_minutes
        self.start_time = timezone.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.stats = {
            'spider_data_collected': 0,
            'agents_executed': 0,
            'learning_records_created': 0,
            'execution_records_created': 0,
            'errors': 0
        }

        # Agents to execute (diverse set for varied learning)
        # NOTE: These names match UnifiedAgentTemplate names after hyphen->underscore conversion
        self.test_agents = [
            'business_agent',
            'content_creator',
            'seo_specialist_agent',
            'market_research_specialist',
            'rag_research_assistant',
            'technical_signal_agent',
            'ai_development_agent',
            'ai_specialist',
            'image_video_pipeline',
            'consistency_specialist_creative_agent'
        ]

        # Spider types to deploy
        self.spider_types = [
            'guru',
            'toptal',
            'remoteok',
            'flexjobs',
            'peopleperhour',
            'medium',
            'gumroad',
            'financial',
            'social_sentiment',
            'market_data'
        ]

    async def deploy_spiders_batch(self):
        """Deploy a batch of spiders"""
        try:
            logger.info(f"🕷️  Deploying {len(self.spider_types)} spider types...")

            # Use spider registry directly for more reliable deployment
            from ai_core.spiders.spider_registry import spider_registry
            from ai_core.spiders.base_spider import SpiderTarget

            # Deploy spiders using registry
            for spider_type in self.spider_types:
                try:
                    # Get spider class from registry
                    spider_class = spider_registry.get_spider_class(spider_type)

                    if not spider_class:
                        logger.warning(f"  ⚠️  {spider_type} not found in registry")
                        continue

                    # Create and run 3 spiders of this type
                    for i in range(3):
                        try:
                            # Create spider with proper initialization parameters
                            spider_id = f"{spider_type}_{i}_{int(timezone.now().timestamp())}"

                            # Create default targets for the spider
                            targets = [
                                SpiderTarget(
                                    url=f"https://example.com/{spider_type}",
                                    rate_limit=1.0,
                                    priority=1,
                                    retry_count=3,
                                    timeout=30
                                )
                            ]

                            # Create subscribers list (empty for now, spiders will use DB storage)
                            subscribers = []

                            # Redis config (minimal for now)
                            redis_config = {
                                'host': 'localhost',
                                'port': 6379,
                                'db': 0
                            }

                            # Instantiate spider with required parameters
                            spider = spider_class(
                                spider_id=spider_id,
                                targets=targets,
                                subscribers=subscribers,
                                redis_config=redis_config
                            )

                            # Run spider with timeout
                            spider_task = asyncio.create_task(
                                asyncio.wait_for(
                                    spider.crawl(max_items=50),
                                    timeout=300  # 5 minutes
                                )
                            )

                            # Collect results
                            results = await spider_task
                            if results and len(results) > 0:
                                self.stats['spider_data_collected'] += len(results)

                        except asyncio.TimeoutError:
                            logger.warning(f"  ⏱️  {spider_type}[{i}] timed out")
                        except Exception as spider_error:
                            logger.debug(f"  ⚠️  {spider_type}[{i}] error: {spider_error}")

                    logger.info(f"  ✅ {spider_type}: deployed 3 spiders")

                except Exception as e:
                    logger.error(f"  ❌ {spider_type} failed: {e}")
                    self.stats['errors'] += 1

            logger.info(f"✅ Spider deployment complete. Total items: {self.stats['spider_data_collected']}")

        except Exception as e:
            logger.error(f"Spider deployment failed: {e}")
            self.stats['errors'] += 1

    async def execute_agent_batch(self):
        """Execute a batch of agents to trigger learning"""
        try:
            logger.info(f"🤖 Executing {len(self.test_agents)} agents...")

            tasks = [
                "Analyze current market trends and opportunities",
                "Generate insights from recent data",
                "Identify patterns in collected information",
                "Evaluate strategic opportunities",
                "Research emerging trends",
                "Optimize current strategies",
                "Assess performance metrics",
                "Identify improvement areas",
                "Generate recommendations",
                "Analyze competitive landscape"
            ]

            for i, agent_name in enumerate(self.test_agents):
                try:
                    task = tasks[i % len(tasks)]

                    logger.info(f"  🔄 Executing {agent_name}...")

                    # Execute in thread pool to avoid async context issues
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        execute_agent_sync,
                        agent_name,
                        task,
                        None,  # context
                        self.user
                    )

                    # execute_agent_sync returns raw result on success, {"success": False} on failure
                    # Check if result is a failure dict
                    if isinstance(result, dict) and result.get('success') is False:
                        logger.warning(f"  ⚠️  {agent_name} execution failed: {result.get('error')}")
                        self.stats['errors'] += 1
                    else:
                        # Success: result is either dict without success key, or other data type
                        self.stats['agents_executed'] += 1
                        logger.info(f"  ✅ {agent_name} completed successfully")

                    # Small delay between executions
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"  ❌ {agent_name} error: {e}")
                    self.stats['errors'] += 1

            logger.info(f"✅ Agent execution batch complete. Total executed: {self.stats['agents_executed']}")

        except Exception as e:
            logger.error(f"Agent execution batch failed: {e}")
            self.stats['errors'] += 1

    async def check_learning_progress(self):
        """Check and log learning progress"""
        try:
            # Run database queries in thread pool to avoid async context issues
            loop = asyncio.get_event_loop()

            def get_counts():
                execution_count = AgentExecution.objects.filter(user=self.user).count()
                learning_count = UserAgentLearning.objects.filter(user=self.user).count()
                spider_count = SpiderData.objects.count()
                recent_learning = list(UserAgentLearning.objects.filter(
                    user=self.user
                ).order_by('-created_at')[:5])
                return execution_count, learning_count, spider_count, recent_learning

            execution_count, learning_count, spider_count, recent_learning = await loop.run_in_executor(
                None, get_counts
            )

            self.stats['execution_records_created'] = execution_count
            self.stats['learning_records_created'] = learning_count
            self.stats['spider_data_collected'] = spider_count

            logger.info("📊 Learning Progress:")
            logger.info(f"  AgentExecution records: {execution_count}")
            logger.info(f"  UserAgentLearning records: {learning_count}")
            logger.info(f"  SpiderData records: {spider_count}")

            if recent_learning:
                logger.info("  Recent learning:")
                for l in recent_learning:
                    logger.info(f"    - {l.agent_name}: {l.learning_domain} (confidence: {l.confidence_score:.2f})")

        except Exception as e:
            logger.error(f"Progress check failed: {e}")

    async def run(self):
        """Run the overnight test"""
        logger.info("=" * 80)
        logger.info("🌙 OVERNIGHT AUTONOMOUS LEARNING TEST STARTED")
        logger.info("=" * 80)
        logger.info(f"User: {self.user.username}")
        logger.info(f"Duration: {self.duration_minutes} minutes ({self.duration_minutes/60:.1f} hours)")
        logger.info(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        # Initial progress check
        logger.info("\n📊 Initial State:")
        await self.check_learning_progress()

        cycle = 0

        try:
            while timezone.now() < self.end_time:
                cycle += 1
                logger.info(f"\n{'=' * 80}")
                logger.info(f"🔄 CYCLE {cycle} - {timezone.now().strftime('%H:%M:%S')}")
                logger.info(f"{'=' * 80}")

                # Phase 1: Deploy spiders (every cycle)
                logger.info("\n📍 Phase 1: Spider Deployment")
                await self.deploy_spiders_batch()

                # Phase 2: Execute agents (every cycle)
                logger.info("\n📍 Phase 2: Agent Execution")
                await self.execute_agent_batch()

                # Phase 3: Check progress
                logger.info("\n📍 Phase 3: Progress Check")
                await self.check_learning_progress()

                # Calculate time remaining
                time_remaining = (self.end_time - timezone.now()).total_seconds() / 60
                logger.info(f"\n⏱️  Time remaining: {time_remaining:.1f} minutes")

                # Wait before next cycle (30 minutes)
                if timezone.now() < self.end_time:
                    wait_minutes = min(30, time_remaining)
                    logger.info(f"😴 Sleeping for {wait_minutes:.1f} minutes until next cycle...")
                    await asyncio.sleep(wait_minutes * 60)

        except KeyboardInterrupt:
            logger.info("\n⚠️  Test interrupted by user")

        except Exception as e:
            logger.error(f"\n❌ Test failed: {e}", exc_info=True)

        finally:
            # Final report
            logger.info("\n" + "=" * 80)
            logger.info("🌅 OVERNIGHT TEST COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Duration: {(timezone.now() - self.start_time).total_seconds() / 3600:.1f} hours")
            logger.info(f"Cycles completed: {cycle}")
            logger.info("\n📊 Final Statistics:")
            logger.info(f"  Spider data collected: {self.stats['spider_data_collected']}")
            logger.info(f"  Agents executed: {self.stats['agents_executed']}")
            logger.info(f"  Execution records: {self.stats['execution_records_created']}")
            logger.info(f"  Learning records: {self.stats['learning_records_created']}")
            logger.info(f"  Errors: {self.stats['errors']}")

            # Save final report
            report_path = f"overnight_test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump({
                    'start_time': self.start_time.isoformat(),
                    'end_time': timezone.now().isoformat(),
                    'duration_minutes': self.duration_minutes,
                    'cycles': cycle,
                    'stats': self.stats
                }, f, indent=2)

            logger.info(f"\n📄 Report saved to: {report_path}")
            logger.info("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run overnight autonomous learning test')
    parser.add_argument('--duration', type=int, default=480,
                       help='Test duration in minutes (default: 480 = 8 hours)')
    parser.add_argument('--user', type=str, default='chris',
                       help='Username to run test for (default: chris)')

    args = parser.parse_args()

    try:
        user = User.objects.get(username=args.user)
    except User.DoesNotExist:
        logger.error(f"User '{args.user}' not found")
        return

    # Run the test
    test = OvernightLearningTest(user, args.duration)
    asyncio.run(test.run())


if __name__ == '__main__':
    main()
