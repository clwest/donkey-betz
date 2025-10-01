"""
AI Core Intelligence App Configuration
Provides learning models and business logic for the AI system
"""
from django.apps import AppConfig


class AiCoreIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core.intelligence'
    label = 'ai_intelligence'  # Unique label to avoid conflict with 'intelligence' app
    verbose_name = 'AI Core Intelligence & Learning System'
