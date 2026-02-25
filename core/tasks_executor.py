"""
Session 1074: Executor Celery task — dispatches ExecutorDriver in a worker.

This runs in the long_running queue since execution may take up to 30 minutes.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='core.tasks_executor.execute_run_task',
    bind=True,
    queue='long_running',
    max_retries=0,
    soft_time_limit=1900,   # Just over 30min default
    time_limit=2000,
    ignore_result=True,
)
def execute_run_task(self, run_id: str) -> None:
    """Execute a single run via the ExecutorDriver."""
    from core.models import ExecutionRun
    from core.services.executor_driver import ExecutorDriver

    logger.info('[Executor] Starting run %s', run_id)

    try:
        run = ExecutionRun.objects.get(id=run_id)
    except ExecutionRun.DoesNotExist:
        logger.error('[Executor] Run %s not found', run_id)
        return

    if run.status not in ('queued',):
        logger.warning('[Executor] Run %s has status %s, skipping', run_id, run.status)
        return

    driver = ExecutorDriver(run)
    driver.execute()

    # Post lifecycle event to collaboration protocol
    _post_lifecycle_event(run)

    logger.info('[Executor] Run %s finished with status %s', run_id, run.status)


def _post_lifecycle_event(run) -> None:
    """Post structured status message to the linked conversation."""
    if not run.conversation_id or not run.created_by:
        return

    try:
        from core.services.collaboration_protocol import post_structured_message

        if run.status == 'succeeded':
            post_structured_message(
                user=run.created_by,
                conversation_id=run.conversation_id,
                msg_type='RESULT',
                title=f'Executor run succeeded',
                body=(
                    f'{run.plan_summary}\n\n'
                    f'Steps: {run.steps_completed}/{run.steps_total}\n'
                    f'Changed files: {len(run.changed_files or [])}\n'
                    f'Time: {run.execution_time_seconds:.1f}s'
                    if run.execution_time_seconds else
                    f'{run.plan_summary}\n\nSteps: {run.steps_completed}/{run.steps_total}'
                ),
                source='pa',
                metadata={
                    'run_id': str(run.id),
                    'working_branch': run.working_branch,
                    'changed_files': run.changed_files or [],
                },
            )
        elif run.status == 'failed':
            post_structured_message(
                user=run.created_by,
                conversation_id=run.conversation_id,
                msg_type='ERROR',
                title=f'Executor run failed',
                body=f'{run.plan_summary}\n\nError: {run.error_message}',
                source='pa',
                metadata={
                    'run_id': str(run.id),
                    'steps_completed': run.steps_completed,
                    'steps_total': run.steps_total,
                },
            )
        elif run.status == 'awaiting_approval':
            post_structured_message(
                user=run.created_by,
                conversation_id=run.conversation_id,
                msg_type='QUESTION',
                title=f'Executor run needs approval',
                body=(
                    f'{run.plan_summary}\n\n'
                    f'Steps requiring approval: {run.approval_required_steps}'
                ),
                source='pa',
                metadata={
                    'run_id': str(run.id),
                },
            )
    except Exception:
        logger.exception('[Executor] Failed to post lifecycle event for run %s', run.id)
