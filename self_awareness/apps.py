"""
Self-Awareness Django App Configuration
"""

from django.apps import AppConfig


class SelfAwarenessConfig(AppConfig):
    """Configuration for Self-Awareness app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'self_awareness'
    verbose_name = 'Self-Awareness & Intelligence'
    
    def ready(self):
        """Called when Django starts"""
        # Import signal handlers or perform startup tasks
