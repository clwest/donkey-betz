"""
Learning Bridges Django App Configuration

Registers learning bridge signals when Django loads the app.
"""
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class LearningBridgesConfig(AppConfig):
    """Configuration for the learning_bridges app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.learning_bridges'
    verbose_name = 'Learning Bridges'

    def ready(self):
        """
        Called when Django starts. Imports signal handlers to register them.
        """
        try:
            # Import all bridge modules to register their signals
            from . import (
                agent_execution_bridge,
                application_outcome_bridge,
                revenue_attribution_bridge,
                advisor_feedback_bridge,
                collaboration_bridge,
                personalization_bridge,
                sports_betting_bridge,
                spider_data_bridge,
            )

            logger.info("✅ Learning Bridges initialized - all signals registered")
            logger.info("  - Agent Execution Bridge: ✓")
            logger.info("  - Application Outcome Bridge: ✓")
            logger.info("  - Revenue Attribution Bridge: ✓")
            logger.info("  - Advisor Feedback Bridge: ✓")
            logger.info("  - Collaboration Bridge: ✓")
            logger.info("  - Personalization Bridge: ✓")
            logger.info("  - Sports Betting Bridge: ✓")
            logger.info("  - Spider Data Bridge: ✓")

            # Session 477: Connect situation trigger signals
            try:
                from core.signals.trigger_signals import connect_trigger_signals
                connect_trigger_signals()
                logger.info("  - Situation Trigger Signals: ✓")
            except Exception as trigger_error:
                logger.warning(f"  - Situation Trigger Signals: ✗ ({trigger_error})")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Learning Bridges: {e}", exc_info=True)
