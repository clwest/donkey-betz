"""Experiment lifecycle / KPI Celery tasks.

Migrated out of `core.tasks` in Phase 3 of the Wave B refactor. Every
task here keeps the registered Celery name it had in `core.tasks`
(locked by the explicit `name=` kwarg from Phase 1), so PeriodicTask DB
rows, settings.py task-routing config, and string-dispatched callers
(`core/management/commands/add_critical_celery_tasks.py`, the
`0328_schedule_experiment_cleanup_tasks` migration) continue to resolve
unchanged.

Tasks (experiment lifecycle / KPI tracking):

- cleanup_halted_experiments
- cleanup_stale_running_experiments
- reconcile_experiment_status_outcome
- monitor_running_experiments
- update_experiment_kpis
- check_kpi_alerts
- send_weekly_kpi_summary

Private helpers moved with the tasks:

- _send_kpi_update_discord_notification (only caller: update_experiment_kpis)

Helpers intentionally LEFT in core.tasks (external callers import them
from core.tasks, out of scope for this PR):

- _gather_experiment_metrics              (used by core.tasks_ops)
- _send_halt_discord_notification         (used by core.tasks_ops)
- _simulate_kpi_progress                  (used by core.tasks_financial)
- _extract_experiment_learning            (used by core.tasks_financial)
- _calculate_kpi_delta                    (used by _extract_experiment_learning)
- _execute_experiment_implementation      (used by core.tasks_initiatives)
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.db import models  # referenced in reconcile_experiment_status_outcome's dead `if False` branch

logger = logging.getLogger(__name__)


@shared_task(name="core.tasks.cleanup_halted_experiments")
def cleanup_halted_experiments(days_old: int = 7):
    from core.tasks_ops import _impl_cleanup_halted_experiments
    return _impl_cleanup_halted_experiments(days_old)

@shared_task(name="core.tasks.cleanup_stale_running_experiments")
def cleanup_stale_running_experiments(
    hours_old: int = 72,
    dry_run: bool = False,
    max_per_run: int = 200,
):
    """
    Session 1103c: auto-halt Experiments stuck in status='running' with
    outcome_classification='pending' for longer than `hours_old`.

    Discovery context: the gate_progression_pipeline auto-creates an
    Experiment with status='running' every time a decision is promoted.
    The ONLY path that transitions running→success is
    auto_kpi_tracking's target-met check, which requires a live KPI
    value being fed into the experiment. Discussion-category decisions
    (auto-generated from AgentConversation topics) don't have a
    trackable KPI, so their experiments sat in 'running' state
    indefinitely. On local inspection, 131 experiments were stuck,
    with the oldest at 74 days old.

    This task completes any Experiment older than `hours_old` that
    never received a KPI update as status='inconclusive' /
    outcome='learn' so they stop polluting the pilot-stats view
    and the running/pending split reflects reality.

    Args:
        hours_old: Age threshold in hours (default 72h = 3 days).
            Experiments created more recently than this are left alone.
        dry_run: If True, log what would be completed without touching
            the DB.
        max_per_run: Safety cap (Rigby's request) — never complete more
            than this many experiments per invocation. Prevents
            accidental mass-mutation if the threshold query blows up.
            Default 200. Set to 0 or negative to disable the cap.
    """
    from django.utils import timezone as _tz
    from datetime import timedelta
    from core.models_pilot_readiness import Experiment

    cutoff = _tz.now() - timedelta(hours=hours_old)
    stale = Experiment.objects.filter(
        status='running',
        outcome_classification='pending',
        created_at__lt=cutoff,
    ).order_by('created_at')  # oldest first — clear the backlog predictably
    total = stale.count()
    if total == 0:
        logger.info(
            "[cleanup_stale_running_experiments] nothing to do (hours_old=%d)",
            hours_old,
        )
        return {'found': 0, 'completed': 0, 'dry_run': dry_run}

    logger.warning(
        "[cleanup_stale_running_experiments] found %d experiments "
        "running+pending > %dh old (dry_run=%s, max_per_run=%d)",
        total, hours_old, dry_run, max_per_run,
    )
    if dry_run:
        return {
            'found': total,
            'completed': 0,
            'dry_run': True,
            'max_per_run': max_per_run,
        }

    # Safety cap — slice the queryset so we process at most max_per_run
    # rows per invocation. If the backlog is larger, the next beat tick
    # will pick up where we left off.
    if max_per_run > 0:
        stale = stale[:max_per_run]

    completed = 0
    errors = 0
    for exp in stale.iterator(chunk_size=50):
        age_h = (_tz.now() - exp.created_at).total_seconds() / 3600
        try:
            exp.complete(
                status='inconclusive',
                result_summary=(
                    f'Auto-halted by cleanup_stale_running_experiments '
                    f'after {age_h:.0f}h with no KPI updates — treated '
                    f'as inconclusive/learn.'
                ),
                outcome_classification='learn',
            )
            completed += 1
        except Exception as e:
            errors += 1
            logger.error(
                "[cleanup_stale_running_experiments] failed to complete "
                "experiment %s (%s: %s)",
                exp.id, type(e).__name__, e,
            )

    remaining = max(0, total - completed)
    logger.warning(
        "[cleanup_stale_running_experiments] completed=%d errors=%d "
        "(of %d stale, %d remaining for next tick)",
        completed, errors, total, remaining,
    )
    return {
        'found': total,
        'completed': completed,
        'errors': errors,
        'remaining': remaining,
        'max_per_run': max_per_run,
        'dry_run': False,
    }

@shared_task(name="core.tasks.reconcile_experiment_status_outcome")
def reconcile_experiment_status_outcome(dry_run: bool = False):
    """
    Session 1103c: reconcile Experiment.status with Experiment.outcome_classification.

    On inspection we found experiments where outcome_classification had
    been set to 'pass'/'learn'/'fail' but status was still 'running'.
    This makes pilots_tool stats look alarming ("n running, n pending")
    when in reality the experiment already finished and just never got
    its status flipped. Likely a missing .save(update_fields=['status'])
    somewhere in the auto_kpi_tracking or halt path.

    Mapping (from Experiment._determine_outcome_classification):
        - outcome='pass'  → status='success'
        - outcome='learn' → status='inconclusive'
        - outcome='fail'  → status='failure'

    This task is idempotent; running it repeatedly is safe.
    """
    from core.models_pilot_readiness import Experiment

    OUTCOME_TO_STATUS = {
        'pass': 'success',
        'learn': 'inconclusive',
        'fail': 'failure',
    }

    fixed = 0
    errors = 0
    by_outcome = {}
    mismatched = Experiment.objects.filter(
        status='running',
    ).exclude(outcome_classification='pending')

    total = mismatched.count()
    if total == 0:
        logger.info(
            "[reconcile_experiment_status_outcome] nothing to do"
        )
        return {'found': 0, 'fixed': 0, 'dry_run': dry_run}

    logger.warning(
        "[reconcile_experiment_status_outcome] found %d experiments "
        "with status=running but outcome != pending (dry_run=%s)",
        total, dry_run,
    )
    if dry_run:
        for row in mismatched.values('outcome_classification').annotate(
            c=models.Count('id') if False else None,
        ):
            pass  # dry_run just reports the total; skip breakdown
        return {'found': total, 'fixed': 0, 'dry_run': True}

    for exp in mismatched.iterator(chunk_size=100):
        outcome = exp.outcome_classification
        new_status = OUTCOME_TO_STATUS.get(outcome)
        if not new_status:
            continue
        try:
            exp.status = new_status
            if not exp.ended_at:
                from django.utils import timezone as _tz
                exp.ended_at = _tz.now()
                exp.save(update_fields=['status', 'ended_at'])
            else:
                exp.save(update_fields=['status'])
            fixed += 1
            by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
        except Exception as e:
            errors += 1
            logger.error(
                "[reconcile_experiment_status_outcome] failed to fix "
                "experiment %s (%s: %s)",
                exp.id, type(e).__name__, e,
            )

    logger.warning(
        "[reconcile_experiment_status_outcome] fixed=%d errors=%d "
        "by_outcome=%s",
        fixed, errors, by_outcome,
    )
    return {
        'found': total,
        'fixed': fixed,
        'errors': errors,
        'by_outcome': by_outcome,
        'dry_run': False,
    }

@shared_task(bind=True, name='core.tasks.monitor_running_experiments')
def monitor_running_experiments(self):
    from core.tasks_ops import _impl_monitor_running_experiments
    return _impl_monitor_running_experiments(self)

@shared_task(name="core.tasks.update_experiment_kpis")
def update_experiment_kpis():
    """
    Session 609: Automatically update KPIs for all running experiments.

    Runs on a schedule to:
    1. Connect experiments to their data sources (spiders, agents, decisions)
    2. Calculate current KPI values
    3. Update experiment current_value fields
    4. Create KPI snapshots for trend visualization

    Returns:
        Dict with update statistics
    """
    logger.info("📊 [SESSION 609] Starting automatic KPI update...")

    try:
        from core.services.auto_kpi_tracking import update_all_experiment_kpis

        results = update_all_experiment_kpis()

        summary = results.get('summary', {})
        logger.info(
            f"📊 [SESSION 609] KPI update complete - "
            f"Updated: {summary.get('updated_count', 0)}, "
            f"Skipped: {summary.get('skipped_count', 0)}, "
            f"Errors: {summary.get('error_count', 0)}"
        )

        # Send Discord notification if updates were made
        if summary.get('updated_count', 0) > 0:
            _send_kpi_update_discord_notification(results)

        return results

    except Exception as e:
        logger.error(f"📊 [SESSION 609] KPI update failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

def _send_kpi_update_discord_notification(results):
    """
    Session 609: Send Discord notification after KPI updates.
    """
    try:
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()
        summary = results.get('summary', {})
        updated = results.get('updated', [])

        message = f"**📊 Auto KPI Update Complete**\n\n"
        message += f"**Updated:** {summary.get('updated_count', 0)} experiments\n"
        message += f"**Snapshots:** {results.get('snapshots_created', 0)} created\n\n"

        if updated:
            message += "**Changes:**\n"
            for exp in updated[:5]:  # Show first 5
                message += f"• {exp['name'][:30]}: {exp['old_value']} → {exp['new_value']}\n"
            if len(updated) > 5:
                message += f"• _...and {len(updated) - 5} more_\n"

        discord.send_to_channel('system-status', message)

    except Exception as e:
        logger.debug(f"Discord KPI notification failed: {e}")

@shared_task(name="core.tasks.check_kpi_alerts")
def check_kpi_alerts():
    """
    Session 611: Check all running experiments for KPI alert conditions.

    Runs on a schedule to detect:
    1. Significant KPI drops (>20% decline)
    2. Trend reversals (was improving, now declining)
    3. Stalled experiments (no progress)
    4. Off-track experiments (behind expected pace)
    5. Target exceeded (positive!)

    Sends Discord notifications for critical/warning alerts.

    Returns:
        Dict with alerts generated and summary
    """
    logger.info("🚨 [SESSION 611] Checking KPI alerts...")

    try:
        from core.services.kpi_alerts import check_kpi_alerts as do_check, send_kpi_alerts_to_discord

        # Check for alerts
        results = do_check()

        summary = results.get('summary', {})
        logger.info(
            f"🚨 [SESSION 611] Alert check complete - "
            f"Critical: {summary.get('critical', 0)}, "
            f"Warning: {summary.get('warning', 0)}, "
            f"Info: {summary.get('info', 0)}"
        )

        # Send Discord notifications for critical/warning alerts
        alerts = results.get('alerts', [])
        critical_warnings = [a for a in alerts if a['severity'] in ('critical', 'warning')]

        if critical_warnings:
            discord_result = send_kpi_alerts_to_discord(alerts)
            logger.info(f"🚨 [SESSION 611] Discord notifications sent: {discord_result.get('sent', 0)}")

        return results

    except Exception as e:
        logger.error(f"🚨 [SESSION 611] KPI alert check failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

@shared_task(name="core.tasks.send_weekly_kpi_summary")
def send_weekly_kpi_summary():
    from core.tasks_misc import _impl_send_weekly_kpi_summary
    return _impl_send_weekly_kpi_summary()

