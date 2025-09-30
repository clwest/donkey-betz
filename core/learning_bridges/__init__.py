"""
Learning Bridges - Connect isolated learning systems to unified learning pipeline

All learning bridges are automatically activated via Django signals.
Signal handlers are registered when the app is loaded via apps.py.
"""

# Django app configuration
default_app_config = 'core.learning_bridges.apps.LearningBridgesConfig'

from .base import LearningBridge
from .sports_betting_bridge import SportsBettingLearningBridge

__all__ = [
    'LearningBridge',
    'SportsBettingLearningBridge',
]
