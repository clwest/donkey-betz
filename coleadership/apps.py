"""
Co-Leadership Django App Configuration - Session 99
"""

from django.apps import AppConfig


class CoLeadershipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coleadership'
    verbose_name = 'AI-Human Co-Leadership'

    def ready(self):
        """Import signals when app is ready"""
        # Import signals here if needed in future
