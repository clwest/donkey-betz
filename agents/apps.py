from django.apps import AppConfig


class AgentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "agents"

    def ready(self):
        """Import signal handlers when app is ready"""
        import agents.signals  # noqa
