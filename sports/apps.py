from django.apps import AppConfig


class SportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sports'
    verbose_name = 'Sports Analytics & Betting Intelligence'
    
    def ready(self):
        """Import signals and register sports agents"""
        import sports.signals