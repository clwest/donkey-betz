from django.apps import AppConfig


class PersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'persistence'
    verbose_name = 'Data Persistence Infrastructure'

    def ready(self):
        """Initialize persistence infrastructure when Django starts"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Persistence infrastructure initialized")