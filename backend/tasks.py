"""
Celery Tasks for Automated Spider Scheduling and Data Collection
"""

from celery import shared_task
from celery.schedules import crontab
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import asyncio
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@shared_task
def collect_real_opportunities():
    """
    Main task to collect real opportunities from all spider sources.
    Runs every 15 minutes to keep data fresh.
    """
    logger.info("🕷️ Starting scheduled spider collection...")

    try:
        # Import spider modules
        from backend.spiders.live_job_scraper import scrape_jobs_sync
        from intelligence.job_income_bridge import JobIncomeBridge
        from intelligence.models import OpportunityActionPlan

        # Collect jobs from live sources
        jobs = scrape_jobs_sync()

        if jobs:
            # Cache the jobs
            cache.set('live_jobs', jobs, 3600)  # Cache for 1 hour
            logger.info(f"✅ Collected {len(jobs)} real jobs from spiders")

            # Sync to Income Builder
            JobIncomeBridge.sync_to_income_builder(jobs)

            # Store top opportunities in database for persistence
            for job in jobs[:20]:  # Store top 20
                OpportunityActionPlan.objects.update_or_create(
                    opportunity_id=f"spider_{job.get('id', '')}",
                    defaults={
                        'platform': job.get('source', 'spider'),
                        'opportunity_data': job,
                        'success_score': job.get('aiScore', 0.75),
                        'ml_confidence': job.get('aiScore', 0.75),
                        'revenue_potential': _extract_salary_amount(job.get('salary', '$3000')),
                        'status': 'identified',
                        'created_at': timezone.now()
                    }
                )

            return {'success': True, 'jobs_collected': len(jobs)}
        else:
            logger.warning("⚠️ No jobs collected from spiders")
            return {'success': False, 'jobs_collected': 0}

    except Exception as e:
        logger.error(f"❌ Spider collection failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def refresh_ai_content_opportunities():
    """
    Generate fresh AI-powered income opportunities.
    Runs every 30 minutes.
    """
    logger.info("🚀 Generating AI content opportunities...")

    try:
        from backend.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator

        generator = ZeroCapitalIncomeGenerator()
        opportunities = asyncio.run(generator.generate_zero_capital_opportunities())

        # Cache AI opportunities
        cache.set('ai_opportunities', opportunities, 3600)
        logger.info(f"✅ Generated {len(opportunities)} AI opportunities")

        return {'success': True, 'opportunities_generated': len(opportunities)}

    except Exception as e:
        logger.error(f"❌ AI opportunity generation failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def sync_revenue_metrics():
    """
    Sync revenue metrics across all components.
    Runs every hour.
    """
    logger.info("💰 Syncing revenue metrics...")

    try:
        from intelligence.models import RevenueMetrics, EarningRecord
        from django.db.models import Sum

        today = timezone.now().date()

        # Update today's metrics
        RevenueMetrics.update_metrics_for_date(today)

        # Calculate total earnings
        total_earnings = EarningRecord.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Broadcast to all connected WebSocket clients
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "hub_revenue_dashboard_updates",
            {
                "type": "broadcast.update",
                "data": {
                    "type": "revenue_sync",
                    "total_revenue": float(total_earnings),
                    "timestamp": timezone.now().isoformat()
                }
            }
        )

        logger.info(f"✅ Revenue metrics synced: ${total_earnings}")
        return {'success': True, 'total_revenue': float(total_earnings)}

    except Exception as e:
        logger.error(f"❌ Revenue sync failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def clean_stale_data():
    """
    Clean up stale data from cache and database.
    Runs daily at 2 AM.
    """
    logger.info("🧹 Cleaning stale data...")

    try:
        from intelligence.models import OpportunityActionPlan, ActionPlan

        # Remove opportunities older than 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        old_opportunities = OpportunityActionPlan.objects.filter(
            created_at__lt=seven_days_ago,
            status__in=['identified', 'analyzing']
        )
        count = old_opportunities.count()
        old_opportunities.delete()

        logger.info(f"✅ Cleaned {count} stale opportunities")

        # Clear old cache entries
        cache.delete_many([
            'stale_jobs',
            'old_opportunities',
            'expired_metrics'
        ])

        return {'success': True, 'items_cleaned': count}

    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def warm_up_spider_network():
    """
    Warm up spider network to ensure fast response times.
    Runs every 4 hours.
    """
    logger.info("🔥 Warming up spider network...")

    try:
        from backend.spiders.spider_registry import get_spider_registry

        registry = get_spider_registry()
        active_spiders = registry.get_active_spiders()

        # Initialize each spider
        for spider_class in active_spiders:
            spider = spider_class()
            spider.initialize()

        logger.info(f"✅ Warmed up {len(active_spiders)} spiders")
        return {'success': True, 'spiders_warmed': len(active_spiders)}

    except Exception as e:
        logger.error(f"❌ Spider warmup failed: {e}")
        return {'success': False, 'error': str(e)}


def _extract_salary_amount(salary_str: str) -> float:
    """Extract numeric amount from salary string"""
    import re

    # Remove currency symbols and commas
    clean_str = salary_str.replace('$', '').replace(',', '')

    # Find first number
    numbers = re.findall(r'\d+', clean_str)
    if numbers:
        return float(numbers[0])
    return 0.0


# Celery Beat Schedule Configuration
CELERYBEAT_SCHEDULE = {
    'collect-real-opportunities': {
        'task': 'backend.tasks.collect_real_opportunities',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # Expire after 15 minutes if not executed
        }
    },
    'refresh-ai-opportunities': {
        'task': 'backend.tasks.refresh_ai_content_opportunities',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    'sync-revenue-metrics': {
        'task': 'backend.tasks.sync_revenue_metrics',
        'schedule': crontab(minute=0),  # Every hour
        'options': {
            'expires': 3600,
        }
    },
    'clean-stale-data': {
        'task': 'backend.tasks.clean_stale_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {
            'expires': 7200,
        }
    },
    'warm-up-spiders': {
        'task': 'backend.tasks.warm_up_spider_network',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {
            'expires': 14400,
        }
    },
}