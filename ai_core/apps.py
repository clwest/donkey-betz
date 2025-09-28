"""
AI Core app configuration for Django
"""
from django.apps import AppConfig


class AICoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'
    verbose_name = 'AI Core System'

    def ready(self):
        """Initialize AI Core services when Django starts"""
        # Import signal handlers if needed
        pass