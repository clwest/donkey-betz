"""
🧠 INTELLIGENCE APP CONFIG
Django app configuration for the Real-Time Intelligence Engine
"""

from django.apps import AppConfig


class IntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'intelligence'
    label = 'intelligence'  # Unique label to avoid conflict with ai_core.intelligence
    verbose_name = 'intelligence'

    def ready(self):
        """Initialize the intelligence engine when Django starts"""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Import and initialize the intelligence engine
            logger.info("🧠 Skynet Intelligence Engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize intelligence engine: {e}")