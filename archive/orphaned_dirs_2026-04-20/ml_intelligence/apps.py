from django.apps import AppConfig


class MlIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_intelligence'
    verbose_name = 'ML Intelligence'

    def ready(self):
        """Initialize ML Engine when Django starts"""
        try:
            from .ml_service import MLService
            MLService.initialize()
        except ImportError:
            # ML dependencies not installed yet
            pass