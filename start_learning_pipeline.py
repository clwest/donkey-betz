#!/usr/bin/env python3
"""
Start Complete Learning Pipeline
================================

This script starts the complete spider-to-learning-loop pipeline:

1. Initializes all components
2. Connects data flows
3. Starts monitoring
4. Provides management interface

Usage:
    python start_learning_pipeline.py [--test] [--debug]

Options:
    --test      Run in test mode with mock data
    --debug     Enable debug logging
    --monitor   Start with monitoring dashboard
"""

import asyncio
import argparse
import logging
import signal
import sys
import os
from datetime import datetime, timezone

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Pipeline components
from backend.intelligence.unified_learning_pipeline import get_unified_pipeline
from backend.intelligence.learning_metrics_dashboard import get_metrics_dashboard

logger = logging.getLogger(__name__)


class LearningPipelineManager:
    """Manager for the complete learning pipeline"""

    def __init__(self, test_mode=False, debug_mode=False, monitor_mode=True):
        self.test_mode = test_mode
        self.debug_mode = debug_mode
        self.monitor_mode = monitor_mode
        self.pipeline = None
        self.metrics_dashboard = None
        self.running = False

        # Setup logging
        self._setup_logging()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.debug_mode else logging.INFO

        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('learning_pipeline.log')
            ]
        )

        # Reduce noise from some verbose libraries
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False

    async def start_pipeline(self):
        """Start the complete learning pipeline"""
        try:
            logger.info("🚀 Starting Unified Learning Pipeline...")
            logger.info(f"Mode: {'TEST' if self.test_mode else 'PRODUCTION'}")
            logger.info(f"Debug: {'ON' if self.debug_mode else 'OFF'}")
            logger.info(f"Monitoring: {'ON' if self.monitor_mode else 'OFF'}")

            # Initialize pipeline
            logger.info("📦 Initializing pipeline components...")
            self.pipeline = get_unified_pipeline()

            # Start pipeline (this initializes all components)
            pipeline_status = await self.pipeline.initialize()

            if pipeline_status.get('error'):
                logger.error(f"❌ Pipeline initialization failed: {pipeline_status['error']}")
                return False

            logger.info("✅ Pipeline components initialized")

            # Start metrics dashboard if enabled
            if self.monitor_mode:
                logger.info("📊 Starting metrics dashboard...")
                self.metrics_dashboard = get_metrics_dashboard()
                await self.metrics_dashboard.initialize()
                logger.info("✅ Metrics dashboard started")

            # Show startup summary
            await self._show_startup_summary()

            # Start main loop
            self.running = True
            await self._main_loop()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to start pipeline: {e}")
            return False

    async def _show_startup_summary(self):
        """Show pipeline startup summary"""
        try:
            logger.info("📊 PIPELINE STARTUP SUMMARY")
            logger.info("=" * 50)

            # Get pipeline status
            status = await self.pipeline.get_pipeline_status()
            logger.info(f"Overall Status: {status.overall_status}")
            logger.info(f"Components Active:")
            logger.info(f"  🕷️  Spider Orchestrator: {'✅' if status.spider_orchestrator_active else '❌'}")
            logger.info(f"  🔄 Transformation Pipeline: {'✅' if status.transformation_pipeline_active else '❌'}")
            logger.info(f"  🧠 Learning Engine: {'✅' if status.learning_engine_active else '❌'}")
            logger.info(f"  🔁 Learning Loop: {'✅' if status.learning_loop_active else '❌'}")
            logger.info(f"  🔗 Redis Connected: {'✅' if status.redis_connected else '❌'}")

            # Get metrics if available
            if self.metrics_dashboard:
                dashboard_data = await self.metrics_dashboard.get_learning_dashboard()
                if 'error' not in dashboard_data:
                    logger.info(f"Agents Tracked: {dashboard_data.get('agent_count', 0)}")

                    if 'pipeline_health' in dashboard_data:
                        health_score = dashboard_data['pipeline_health'].get('overall_health_score', 0)
                        logger.info(f"Health Score: {health_score:.2f}/1.0")

            logger.info("=" * 50)

            # Test mode specific actions
            if self.test_mode:
                logger.info("🧪 TEST MODE: Triggering initial data sweep...")
                await self.pipeline.trigger_full_pipeline_sweep()

        except Exception as e:
            logger.error(f"Error showing startup summary: {e}")

    async def _main_loop(self):
        """Main pipeline monitoring loop"""
        logger.info("🔄 Starting main monitoring loop...")

        status_interval = 300  # 5 minutes
        last_status_time = 0

        while self.running:
            try:
                current_time = asyncio.get_event_loop().time()

                # Periodic status updates
                if current_time - last_status_time > status_interval:
                    await self._log_status_update()
                    last_status_time = current_time

                # Check for user commands (in production, this could be extended)
                if self.test_mode:
                    # In test mode, run for a limited time then exit
                    await asyncio.sleep(30)
                    logger.info("🧪 Test mode completed, shutting down...")
                    break

                await asyncio.sleep(10)  # Main loop interval

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait longer on errors

        logger.info("🔄 Main loop finished")

    async def _log_status_update(self):
        """Log periodic status updates"""
        try:
            # Get pipeline metrics
            if self.pipeline:
                metrics = await self.pipeline.get_pipeline_metrics()

                if 'error' not in metrics:
                    logger.info("📊 PIPELINE STATUS UPDATE")
                    logger.info(f"Uptime: {metrics['system_info'].get('uptime_seconds', 0):.0f} seconds")

                    # Component metrics
                    components = metrics.get('component_metrics', {})

                    if 'spider_orchestrator' in components:
                        spider_stats = components['spider_orchestrator']
                        logger.info(f"Spiders: {spider_stats.get('total_spiders', 0)} active")

                    if 'transformation_pipeline' in components:
                        transform_stats = components['transformation_pipeline']
                        logger.info(f"Signals Generated: {transform_stats.get('signals_generated', 0)}")

                    if 'learning_engine' in components:
                        learning_stats = components['learning_engine']
                        logger.info(f"Learning Updates: {learning_stats.get('total_learning_updates', 0)}")

            # Get dashboard metrics
            if self.metrics_dashboard:
                dashboard_data = await self.metrics_dashboard.get_learning_dashboard()

                if 'error' not in dashboard_data and 'pipeline_health' in dashboard_data:
                    health_score = dashboard_data['pipeline_health'].get('overall_health_score', 0)
                    logger.info(f"Health Score: {health_score:.2f}/1.0")

        except Exception as e:
            logger.error(f"Error in status update: {e}")

    async def shutdown_pipeline(self):
        """Gracefully shutdown the pipeline"""
        logger.info("🔄 Shutting down learning pipeline...")

        try:
            # Stop metrics dashboard
            if self.metrics_dashboard:
                logger.info("📊 Stopping metrics dashboard...")
                await self.metrics_dashboard.cleanup()

            # Stop main pipeline
            if self.pipeline:
                logger.info("🔄 Stopping pipeline components...")
                await self.pipeline.cleanup()

            logger.info("✅ Pipeline shutdown completed")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    async def run(self):
        """Run the complete pipeline"""
        success = False

        try:
            success = await self.start_pipeline()

        except KeyboardInterrupt:
            logger.info("Pipeline interrupted by user")

        except Exception as e:
            logger.error(f"Pipeline error: {e}")

        finally:
            await self.shutdown_pipeline()

        return success


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Start the Unified Learning Pipeline')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-monitor', action='store_true', help='Disable monitoring dashboard')

    args = parser.parse_args()

    # Create pipeline manager
    manager = LearningPipelineManager(
        test_mode=args.test,
        debug_mode=args.debug,
        monitor_mode=not args.no_monitor
    )

    # Run pipeline
    success = await manager.run()

    return 0 if success else 1


if __name__ == "__main__":
    # Print banner
    print("=" * 80)
    print("UNIFIED DONKEY BETZ - LEARNING PIPELINE")
    print("Spider-to-Agent Continuous Learning System")
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)

    # Run the pipeline
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        sys.exit(1)