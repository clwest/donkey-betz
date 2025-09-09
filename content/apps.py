from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
    verbose_name = 'Content Management System'

    def ready(self):
        """Initialize content system when app starts"""
        import content.signals