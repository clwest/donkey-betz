"""
Base class for all learning bridges
Provides common functionality and structure for connecting system events to learning mechanisms
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class LearningBridge(ABC):
    """
    Abstract base class for learning bridges

    All learning bridges should inherit from this class and implement:
    - process_event(): Main event processing logic
    - _extract_patterns(): Pattern extraction from event
    - _update_learning(): Update learning records
    - _generate_insights(): Generate actionable insights
    """

    def __init__(self, bridge_name: str):
        self.bridge_name = bridge_name
        self.logger = logging.getLogger(f"learning_bridge.{bridge_name}")
        self.event_count = 0
        self.success_count = 0
        self.error_count = 0

    @abstractmethod
    def process_event(self, event_data: Any) -> Dict:
        """
        Process an event and update learning

        Args:
            event_data: Event data (model instance, dict, etc.)

        Returns:
            Dict with processing results and insights
        """

    @abstractmethod
    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract patterns from event data"""

    @abstractmethod
    def _update_learning(self, patterns: Dict) -> None:
        """Update learning records based on patterns"""

    @abstractmethod
    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Generate actionable insights"""

    def log_event(self, message: str, level: str = 'info'):
        """Log event with bridge context"""
        log_method = getattr(self.logger, level)
        log_method(f"[{self.bridge_name}] {message}")
        self.event_count += 1

    def log_success(self, message: str):
        """Log successful processing"""
        self.logger.info(f"✅ [{self.bridge_name}] {message}")
        self.success_count += 1

    def log_error(self, message: str, exc_info: bool = True):
        """Log error"""
        self.logger.error(f"❌ [{self.bridge_name}] {message}", exc_info=exc_info)
        self.error_count += 1

    def get_statistics(self) -> Dict:
        """Get bridge statistics"""
        return {
            'bridge_name': self.bridge_name,
            'events_processed': self.event_count,
            'successes': self.success_count,
            'errors': self.error_count,
            'success_rate': self.success_count / max(self.event_count, 1)
        }
