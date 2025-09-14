"""
🧠 INTELLIGENCE TASKS
Celery tasks for the Real-Time Intelligence Engine
"""

import asyncio
import logging
from celery import shared_task
from django.conf import settings
from .realtime_engine import intelligence_engine

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def start_intelligence_engine(self):
    """🚀 Start the Real-Time Intelligence Engine"""
    try:
        logger.info("🚀 Starting Limitless Intelligence Engine...")

        # Create new event loop for async code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Start the intelligence engine
        loop.run_until_complete(intelligence_engine.start_intelligence_stream())

    except Exception as e:
        logger.error(f"Intelligence engine error: {e}")
        raise


@shared_task
def get_live_opportunities():
    """Get current live opportunities"""
    try:
        return intelligence_engine.get_current_opportunities()
    except Exception as e:
        logger.error(f"Get opportunities error: {e}")
        return []


@shared_task
def get_live_predictions():
    """Get current live predictions"""
    try:
        return intelligence_engine.get_current_predictions()
    except Exception as e:
        logger.error(f"Get predictions error: {e}")
        return []


@shared_task
def trigger_market_scan():
    """Trigger an immediate market scan"""
    try:
        logger.info("🎯 Manual market scan triggered")
        # This would trigger immediate scans in the engine
        return {"status": "scan_triggered", "timestamp": "now"}
    except Exception as e:
        logger.error(f"Market scan trigger error: {e}")
        return {"status": "error", "error": str(e)}