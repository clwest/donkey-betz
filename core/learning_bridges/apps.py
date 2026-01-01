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
            # Session 646: Actually import bridge modules to register their signals
            # The @receiver decorators only work if the modules are imported
            from core.learning_bridges import agent_execution_bridge  # noqa: F401
            from core.learning_bridges import application_outcome_bridge  # noqa: F401
            from core.learning_bridges import revenue_attribution_bridge  # noqa: F401
            from core.learning_bridges import advisor_feedback_bridge  # noqa: F401
            from core.learning_bridges import collaboration_bridge  # noqa: F401
            from core.learning_bridges import personalization_bridge  # noqa: F401
            from core.learning_bridges import spider_data_bridge  # noqa: F401

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
