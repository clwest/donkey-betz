"""
Backend app configuration for Django
"""
from django.apps import AppConfig


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    verbose_name = 'Backend System'

    def ready(self):
        """Initialize backend services when Django starts"""
        # Import signal handlers if needed
        pass