"""
ML Automation Scheduler
Automated scheduling for data collection and model training
"""

import os
import logging
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
from dataclasses import dataclass
import json

# Django integration
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.cache import cache
from django.utils import timezone

# Local imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.training_data_collector import TrainingDataCollector, TrainingDataConfig
from training.training_pipeline import MLTrainingPipeline, TrainingConfig

@dataclass
class SchedulerConfig:
    """ML Scheduler configuration"""
    data_collection_interval_hours: int = 1
    model_training_interval_hours: int = 24
    health_check_interval_minutes: int = 15
    cleanup_interval_days: int = 7
    max_concurrent_tasks: int = 3
    enable_auto_training: bool = True
    min_data_points_for_training: int = 1000

class MLScheduler:
    """
    Automated ML Pipeline Scheduler
    Manages data collection, training, and maintenance tasks
    """

    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.tasks = {}
        self.scheduler_thread = None

        # Initialize components
        self.data_collector = TrainingDataCollector(TrainingDataConfig())
        self.training_pipeline = MLTrainingPipeline(TrainingConfig())

        self.setup_schedule()

    def setup_schedule(self):
        """Set up scheduled tasks"""
        self.logger.info("🕐 Setting up ML automation schedule...")

        # Data collection every hour
        schedule.every(self.config.data_collection_interval_hours).hours.do(
            self._schedule_data_collection
        )

        # Model training daily (if auto-training enabled)
        if self.config.enable_auto_training:
            schedule.every(self.config.model_training_interval_hours).hours.do(
                self._schedule_model_training
            )

        # Health checks every 15 minutes
        schedule.every(self.config.health_check_interval_minutes).minutes.do(
            self._schedule_health_check
        )

        # Cleanup weekly
        schedule.every(self.config.cleanup_interval_days).days.do(
            self._schedule_cleanup
        )

        # Performance monitoring hourly
        schedule.every().hour.do(self._schedule_performance_monitoring)

        # Manual triggers for specific times
        schedule.every().day.at("02:00").do(self._schedule_full_training)  # 2 AM daily
        schedule.every().sunday.at("01:00").do(self._schedule_deep_cleanup)  # Sunday 1 AM

        self.logger.info("✅ ML automation schedule configured")

    def start(self):
        """Start the scheduler"""
        if self.running:
            self.logger.warning("Scheduler already running")
            return

        self.running = True
        self.logger.info("🚀 Starting ML automation scheduler...")

        # Start scheduler in separate thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        # Initial health check
        asyncio.run(self._perform_health_check())

        self.logger.info("✅ ML scheduler started successfully")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        self.logger.info("🛑 ML scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    # Scheduled task methods
    def _schedule_data_collection(self):
        """Schedule data collection task"""
        if not self._can_run_task("data_collection"):
            return

        self.logger.info("📊 Scheduling data collection...")
        asyncio.run(self._run_data_collection())

    def _schedule_model_training(self):
        """Schedule model training task"""
        if not self._can_run_task("model_training"):
            return

        # Check if we have enough data
        status = self.data_collector.get_collection_status()
        if status["data_points_count"] < self.config.min_data_points_for_training:
            self.logger.info(f"Insufficient data for training: {status['data_points_count']} points")
            return

        self.logger.info("🤖 Scheduling model training...")
        asyncio.run(self._run_model_training())

    def _schedule_health_check(self):
        """Schedule health check"""
        asyncio.run(self._perform_health_check())

    def _schedule_cleanup(self):
        """Schedule cleanup task"""
        self.logger.info("🧹 Scheduling cleanup...")
        asyncio.run(self._run_cleanup())

    def _schedule_performance_monitoring(self):
        """Schedule performance monitoring"""
        asyncio.run(self._monitor_performance())

    def _schedule_full_training(self):
        """Schedule full model retraining"""
        if not self._can_run_task("full_training"):
            return

        self.logger.info("🔄 Scheduling full model retraining...")
        asyncio.run(self._run_full_training())

    def _schedule_deep_cleanup(self):
        """Schedule deep cleanup"""
        self.logger.info("🧽 Scheduling deep cleanup...")
        asyncio.run(self._run_deep_cleanup())

    # Task execution methods
    async def _run_data_collection(self):
        """Execute data collection"""
        try:
            self.tasks["data_collection"] = {
                "status": "running",
                "start_time": datetime.now(),
                "progress": 0
            }

            await self.data_collector.collect_all_training_data()

            self.tasks["data_collection"]["status"] = "completed"
            self.tasks["data_collection"]["end_time"] = datetime.now()

            self.logger.info("✅ Data collection completed successfully")

            # Cache status
            cache.set("ml_last_data_collection", datetime.now().isoformat(), timeout=86400)

        except Exception as e:
            self.logger.error(f"❌ Data collection failed: {e}")
            self.tasks["data_collection"]["status"] = "failed"
            self.tasks["data_collection"]["error"] = str(e)

    async def _run_model_training(self):
        """Execute model training"""
        try:
            self.tasks["model_training"] = {
                "status": "running",
                "start_time": datetime.now(),
                "progress": 0
            }

            results = await self.training_pipeline.train_all_models()

            self.tasks["model_training"]["status"] = "completed"
            self.tasks["model_training"]["end_time"] = datetime.now()
            self.tasks["model_training"]["results"] = [
                {
                    "model": r.model_name,
                    "accuracy": r.accuracy,
                    "f1_score": r.f1_score
                } for r in results
            ]

            self.logger.info(f"✅ Model training completed: {len(results)} models")

            # Cache status
            cache.set("ml_last_training", datetime.now().isoformat(), timeout=86400)
            cache.set("ml_training_results", len(results), timeout=86400)

        except Exception as e:
            self.logger.error(f"❌ Model training failed: {e}")
            self.tasks["model_training"]["status"] = "failed"
            self.tasks["model_training"]["error"] = str(e)

    async def _run_full_training(self):
        """Execute full model retraining"""
        try:
            self.logger.info("🔄 Starting full model retraining...")

            # First collect fresh data
            await self._run_data_collection()

            # Wait a bit for data processing
            await asyncio.sleep(30)

            # Then retrain all models
            await self._run_model_training()

            self.logger.info("✅ Full retraining completed")

        except Exception as e:
            self.logger.error(f"❌ Full retraining failed: {e}")

    async def _perform_health_check(self):
        """Perform system health check"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "data_collector": "healthy",
                "training_pipeline": "healthy",
                "storage": "healthy",
                "memory": "healthy",
                "disk_space": "healthy"
            }

            # Check data collector
            collector_status = self.data_collector.get_collection_status()
            if collector_status["data_points_count"] == 0:
                health_status["data_collector"] = "warning"

            # Check model registry
            model_registry = self.training_pipeline.get_model_registry()
            if model_registry["total_models"] == 0:
                health_status["training_pipeline"] = "warning"

            # Check disk space
            data_dir = Path("ml/data")
            if data_dir.exists():
                total_size_mb = sum(f.stat().st_size for f in data_dir.rglob("*") if f.is_file()) / (1024 * 1024)
                if total_size_mb > 1000:  # 1GB threshold
                    health_status["disk_space"] = "warning"

            # Cache health status
            cache.set("ml_health_status", health_status, timeout=1800)  # 30 minutes

            # Log warnings
            warnings = [k for k, v in health_status.items() if v == "warning"]
            if warnings:
                self.logger.warning(f"Health check warnings: {warnings}")

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")

    async def _run_cleanup(self):
        """Execute cleanup tasks"""
        try:
            self.logger.info("🧹 Running ML cleanup...")

            # Clean old data files
            await self.data_collector.cleanup_old_data()

            # Clean old training reports
            model_dir = Path("ml/models")
            if model_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=30)
                for report_file in model_dir.glob("training_report_*.json"):
                    file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        report_file.unlink()
                        self.logger.info(f"Deleted old report: {report_file}")

            # Clear old cache entries
            cache.delete_many([
                "ml_opportunities_*",
                "user_confidence_*"
            ])

            self.logger.info("✅ Cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")

    async def _run_deep_cleanup(self):
        """Execute deep cleanup tasks"""
        try:
            self.logger.info("🧽 Running deep cleanup...")

            # Run regular cleanup first
            await self._run_cleanup()

            # Additional deep cleanup tasks
            # Clean temporary files
            temp_dirs = ["ml/temp", "ml/cache", "/tmp/ml_*"]
            for temp_pattern in temp_dirs:
                temp_path = Path(temp_pattern)
                if temp_path.exists() and temp_path.is_dir():
                    for file in temp_path.rglob("*"):
                        if file.is_file():
                            file.unlink()

            # Optimize database connections
            from django.db import connection
            connection.close()

            self.logger.info("✅ Deep cleanup completed")

        except Exception as e:
            self.logger.error(f"❌ Deep cleanup failed: {e}")

    async def _monitor_performance(self):
        """Monitor ML system performance"""
        try:
            performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "data_collection_rate": 0,
                "model_accuracy_avg": 0,
                "training_success_rate": 0,
                "system_load": 0
            }

            # Calculate data collection rate
            status = self.data_collector.get_collection_status()
            performance_metrics["data_collection_rate"] = status.get("data_points_count", 0)

            # Get recent training results
            recent_reports = list(Path("ml/models").glob("training_report_*.json"))
            if recent_reports:
                latest_report = max(recent_reports, key=lambda x: x.stat().st_mtime)
                with open(latest_report, 'r') as f:
                    report = json.load(f)
                    performance_metrics["model_accuracy_avg"] = report.get("average_accuracy", 0)
                    total_models = report.get("total_models_trained", 0)
                    successful_models = report.get("successful_models", 0)
                    if total_models > 0:
                        performance_metrics["training_success_rate"] = successful_models / total_models

            # Cache performance metrics
            cache.set("ml_performance_metrics", performance_metrics, timeout=3600)

        except Exception as e:
            self.logger.error(f"Performance monitoring failed: {e}")

    # Utility methods
    def _can_run_task(self, task_name: str) -> bool:
        """Check if task can run (not already running)"""
        if task_name in self.tasks:
            current_task = self.tasks[task_name]
            if current_task.get("status") == "running":
                return False

        # Check concurrent task limit
        running_tasks = sum(1 for task in self.tasks.values() if task.get("status") == "running")
        return running_tasks < self.config.max_concurrent_tasks

    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        status = {
            "running": self.running,
            "last_health_check": cache.get("ml_health_status", {}),
            "last_data_collection": cache.get("ml_last_data_collection"),
            "last_training": cache.get("ml_last_training"),
            "active_tasks": {
                name: task for name, task in self.tasks.items()
                if task.get("status") == "running"
            },
            "completed_tasks_today": len([
                task for task in self.tasks.values()
                if task.get("status") == "completed" and
                task.get("end_time", datetime.min).date() == datetime.now().date()
            ]),
            "next_scheduled": self._get_next_scheduled_tasks()
        }

        return status

    def _get_next_scheduled_tasks(self) -> List[Dict[str, str]]:
        """Get next scheduled tasks"""
        # This would return information about upcoming scheduled tasks
        # For demonstration, returning placeholder
        return [
            {
                "task": "data_collection",
                "next_run": (datetime.now() + timedelta(hours=1)).isoformat()
            },
            {
                "task": "model_training",
                "next_run": (datetime.now() + timedelta(hours=24)).isoformat()
            }
        ]

    def trigger_manual_task(self, task_name: str) -> bool:
        """Manually trigger a specific task"""
        if not self._can_run_task(task_name):
            return False

        task_methods = {
            "data_collection": self._run_data_collection,
            "model_training": self._run_model_training,
            "full_training": self._run_full_training,
            "cleanup": self._run_cleanup,
            "health_check": self._perform_health_check
        }

        if task_name not in task_methods:
            return False

        self.logger.info(f"🔧 Manually triggering task: {task_name}")

        # Run task in background
        asyncio.create_task(task_methods[task_name]())
        return True

# Global scheduler instance
_scheduler_instance = None

def get_ml_scheduler() -> MLScheduler:
    """Get global ML scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        config = SchedulerConfig()
        _scheduler_instance = MLScheduler(config)
    return _scheduler_instance

def start_ml_automation():
    """Start ML automation (called from Django app ready)"""
    scheduler = get_ml_scheduler()
    scheduler.start()

def stop_ml_automation():
    """Stop ML automation"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None

# Command line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ML Automation Scheduler")
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    parser.add_argument("--stop", action="store_true", help="Stop the scheduler")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")
    parser.add_argument("--trigger", type=str, help="Manually trigger a task")

    args = parser.parse_args()

    config = SchedulerConfig()
    scheduler = MLScheduler(config)

    if args.start:
        scheduler.start()
        print("✅ ML Scheduler started")
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
            print("🛑 ML Scheduler stopped")

    elif args.stop:
        scheduler.stop()
        print("🛑 ML Scheduler stopped")

    elif args.status:
        status = scheduler.get_scheduler_status()
        print("📊 ML Scheduler Status:")
        print(json.dumps(status, indent=2, default=str))

    elif args.trigger:
        success = scheduler.trigger_manual_task(args.trigger)
        if success:
            print(f"✅ Triggered task: {args.trigger}")
        else:
            print(f"❌ Failed to trigger task: {args.trigger}")

    else:
        parser.print_help()