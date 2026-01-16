"""
Orchestration Checkpoint Manager
================================

Session 764: Manages checkpoint data for execution resume capability.
"""

import logging
from typing import Dict, Any, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages checkpoints for orchestration executions.

    Checkpoints allow resuming failed or interrupted workflows
    from the last successful step.
    """

    def save_checkpoint(
        self,
        execution,
        step_number: int,
        step_output: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> None:
        """Save checkpoint after successful step."""
        execution.save_checkpoint(step_number, step_output, context)
        logger.debug(f"Checkpoint saved for execution {execution.id} at step {step_number}")

    def load_checkpoint(self, execution) -> Dict[str, Any]:
        """Load checkpoint data from execution."""
        return {
            'current_step': execution.current_step,
            'step_outputs': execution.checkpoint_data.get('step_outputs', {}),
            'accumulated_context': execution.checkpoint_data.get('accumulated_context', {}),
            'retry_counts': execution.checkpoint_data.get('retry_counts', {}),
            'last_checkpoint_at': execution.checkpoint_data.get('last_checkpoint_at'),
        }

    def get_resume_point(self, execution) -> int:
        """Get the step number to resume from."""
        return execution.current_step + 1

    def clear_checkpoint(self, execution) -> None:
        """Clear checkpoint data (e.g., after successful completion)."""
        execution.checkpoint_data = {}
        execution.save(update_fields=['checkpoint_data', 'updated_at'])


# Singleton instance
checkpoint_manager = CheckpointManager()
