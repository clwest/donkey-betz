"""
Celery Tasks for Creative Pipelines

Session 109 - Creative Pipelines v1
"""

import logging
from celery import shared_task
from .services import run_pipeline

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=0)
def run_pipeline_task(self, run_id: str):
    """
    Async task to execute a pipeline run.

    Args:
        run_id: UUID of the CreativePipelineRun to execute

    This task is fire-and-forget with no retries.
    All error handling is done within run_pipeline().
    """
    logger.info(f"Starting pipeline execution task for run {run_id}")

    try:
        run_pipeline(run_id)
        logger.info(f"Pipeline execution task completed for run {run_id}")
    except Exception as e:
        logger.error(f"Pipeline execution task failed for run {run_id}: {e}", exc_info=True)
        # Don't raise - error is already logged in the run record
