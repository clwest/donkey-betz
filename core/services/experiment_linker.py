"""
Experiment Linker Service - Session 873
=======================================

Helper service to auto-link AgentExecution records to running experiments.

The Experiment halt system relies on the `experiment` FK being set on AgentExecution
records to calculate scoped error rates. This service provides functions to:
1. Look up the active experiment for an execution
2. Backfill missing experiment FKs on historical records
3. Provide a post_save signal handler for automatic linking

Usage:
    from core.services.experiment_linker import (
        find_experiment_for_execution,
        link_execution_to_experiment,
        backfill_experiment_fks
    )

    # When creating an AgentExecution:
    experiment = find_experiment_for_execution(context)
    execution = AgentExecution.objects.create(
        ...
        experiment=experiment,
    )

    # Or use the signal (auto-links on save):
    # Already connected in this module
"""

import logging
from typing import Optional
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def find_experiment_for_execution(
    context: dict = None,
    agent_name: str = None,
    created_at=None
) -> Optional['Experiment']:
    """
    Find the most relevant running experiment for an agent execution.

    Looks up experiments based on:
    1. Explicit experiment_id in context (highest priority)
    2. Decision/gate/pilot associations
    3. Most recent running experiment (fallback)

    Args:
        context: Execution context dict (may contain experiment_id, decision_id, etc.)
        agent_name: Name of the agent being executed
        created_at: Timestamp of execution (for scoping to experiments running at that time)

    Returns:
        Experiment instance or None
    """
    try:
        from core.models_pilot_readiness import Experiment

        context = context or {}

        # 1. Check for explicit experiment_id in context
        experiment_id = context.get('experiment_id')
        if experiment_id:
            experiment = Experiment.objects.filter(id=experiment_id, status='running').first()
            if experiment:
                logger.debug(f"Found experiment {experiment.id} via explicit context")
                return experiment

        # 2. Check for decision_id → gate → pilot → experiment chain
        decision_id = context.get('decision_id')
        if decision_id:
            experiment = Experiment.objects.filter(
                pilot__gate__decision_id=decision_id,
                status='running'
            ).first()
            if experiment:
                logger.debug(f"Found experiment {experiment.id} via decision {decision_id}")
                return experiment

        # 3. Check for gate_id → pilot → experiment chain
        gate_id = context.get('gate_id')
        if gate_id:
            experiment = Experiment.objects.filter(
                pilot__gate_id=gate_id,
                status='running'
            ).first()
            if experiment:
                logger.debug(f"Found experiment {experiment.id} via gate {gate_id}")
                return experiment

        # 4. Check for pilot_id → experiment
        pilot_id = context.get('pilot_id')
        if pilot_id:
            experiment = Experiment.objects.filter(
                pilot_id=pilot_id,
                status='running'
            ).first()
            if experiment:
                logger.debug(f"Found experiment {experiment.id} via pilot {pilot_id}")
                return experiment

        # 5. Fallback: Find most recent running experiment
        # (Only use this fallback if there's exactly one running, to avoid false positives)
        running_experiments = Experiment.objects.filter(status='running')
        if running_experiments.count() == 1:
            experiment = running_experiments.first()
            logger.debug(f"Found single running experiment {experiment.id} as fallback")
            return experiment

        # No match found
        return None

    except Exception as e:
        logger.warning(f"Error finding experiment for execution: {e}")
        return None


def link_execution_to_experiment(
    execution,
    context: dict = None
) -> bool:
    """
    Link an AgentExecution to its relevant experiment.

    Args:
        execution: AgentExecution instance
        context: Optional context dict to help find the experiment

    Returns:
        True if linked successfully, False otherwise
    """
    try:
        if execution.experiment:
            return True  # Already linked

        # Try to find experiment
        context = context or {}
        if hasattr(execution, 'input_data') and execution.input_data:
            context.update(execution.input_data)

        experiment = find_experiment_for_execution(
            context=context,
            agent_name=getattr(execution.agent, 'name', None) if hasattr(execution, 'agent') else None,
            created_at=execution.created_at if hasattr(execution, 'created_at') else None
        )

        if experiment:
            execution.experiment = experiment
            execution.save(update_fields=['experiment'])
            logger.info(f"Linked execution {execution.id} to experiment {experiment.id}")
            return True

        return False

    except Exception as e:
        logger.warning(f"Error linking execution to experiment: {e}")
        return False


def backfill_experiment_fks(
    dry_run: bool = True,
    limit: int = 1000,
    hours_back: int = 24
) -> dict:
    """
    Backfill missing experiment FKs on recent AgentExecution records.

    Args:
        dry_run: If True, only report what would be done
        limit: Maximum records to process
        hours_back: Only process records from the last N hours

    Returns:
        Dict with backfill stats
    """
    try:
        from core.models_unified_system import AgentExecution

        cutoff = timezone.now() - timedelta(hours=hours_back)

        # Find executions without experiment FK
        unlinked = AgentExecution.objects.filter(
            experiment__isnull=True,
            created_at__gte=cutoff
        ).select_related('agent')[:limit]

        stats = {
            'total_unlinked': unlinked.count(),
            'linked': 0,
            'skipped': 0,
            'dry_run': dry_run
        }

        for execution in unlinked:
            experiment = find_experiment_for_execution(
                context=execution.input_data or {},
                agent_name=execution.agent.name if execution.agent else None,
                created_at=execution.created_at
            )

            if experiment:
                if not dry_run:
                    execution.experiment = experiment
                    execution.save(update_fields=['experiment'])
                stats['linked'] += 1
            else:
                stats['skipped'] += 1

        logger.info(f"Experiment FK backfill: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error in backfill_experiment_fks: {e}")
        return {'error': str(e)}


# =============================================================================
# Signal Handler for Auto-Linking
# =============================================================================

def auto_link_experiment_on_save(sender, instance, created, **kwargs):
    """
    Post-save signal handler to auto-link AgentExecution to experiment.

    Only attempts linking for newly created records to avoid overhead
    on every update.
    """
    if not created:
        return

    if instance.experiment:
        return  # Already linked

    try:
        link_execution_to_experiment(instance)
    except Exception as e:
        logger.debug(f"Auto-link failed for execution {instance.id}: {e}")


def connect_experiment_linker_signals():
    """
    Connect the auto-link signal to AgentExecution post_save.

    Call this from AppConfig.ready() to enable automatic linking.
    """
    try:
        from django.db.models.signals import post_save
        from core.models_unified_system import AgentExecution

        post_save.connect(
            auto_link_experiment_on_save,
            sender=AgentExecution,
            dispatch_uid='experiment_linker_auto_link'
        )
        logger.info("Experiment linker signals connected")
    except Exception as e:
        logger.warning(f"Could not connect experiment linker signals: {e}")
