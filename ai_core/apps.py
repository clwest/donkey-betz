"""
AI Core app configuration for Django
"""
import os
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class AICoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'
    verbose_name = 'AI Core System'

    def ready(self):
        """Initialize AI Core services when Django starts"""
        # Only start bridge in main process, not in management commands
        # and not during migrations
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('RUN_MAIN'):
            # Check we're not in a migration or other management command
            import sys
            if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv:
                self._start_spider_bridge()

    def _start_spider_bridge(self):
        """Start the spider intelligence bridge for AI Content agents"""
        try:
            from core.services.spider_intelligence_bridge import start_spider_bridge
            bridge = start_spider_bridge()
            logger.info("Spider Intelligence Bridge started for AI Content agents")
        except Exception as e:
            # Don't fail Django startup if bridge fails
            logger.warning(f"Could not start Spider Intelligence Bridge: {e}")