"""
Rendering App Configuration - Session 105
"""

from django.apps import AppConfig


class RenderingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rendering'
    verbose_name = 'Render Jobs & DaVinci Integration'
