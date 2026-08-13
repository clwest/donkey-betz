"""Diagnostic Celery tasks.

Migrated out of `core.tasks` in Phase 3 of the Wave B refactor. Every
task here keeps the registered Celery name it had in `core.tasks`
(locked by the explicit `name=` kwarg from Phase 1), so beat schedule
entries, PeriodicTask DB rows, and string-dispatched callers continue
to resolve unchanged.

Tasks:

- run_cto_daily_diagnostic / post_cto_daily_diagnostic
- run_coo_daily_diagnostic / post_coo_daily_diagnostic
- run_trend_daily_diagnostic / post_trend_daily_diagnostic
- run_metrics_action_check
- run_diagnostic_pipeline_task

`scheduled_diagnostic_runner.run_diagnostic` resolves the post tasks
via `core.tasks:post_<name>` import path; the re-export block in
`core.tasks` keeps that path working without changes to the runner or
the per-config builders.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=0, soft_time_limit=300, time_limit=600, name="core.tasks.run_cto_daily_diagnostic")
def run_cto_daily_diagnostic(self):
    """Session 1093 — Daily CTOAgent platform reliability diagnostic.

    Computes 24h failure metrics, evaluates threshold gates, and
    (if anomalies detected) dispatches CTOAgent async + enqueues
    `post_cto_daily_diagnostic` to publish the attention item once
    the agent narrative is ready. See module docstring in
    core/tasks_ops.py for full feature flag + threshold reference.
    """
    from core.tasks_ops import _impl_run_cto_daily_diagnostic
    return _impl_run_cto_daily_diagnostic()

@shared_task(bind=True, max_retries=2, default_retry_delay=120, soft_time_limit=180, time_limit=300, name="core.tasks.post_cto_daily_diagnostic")
def post_cto_daily_diagnostic(
    self,
    cto_async_task_id: str = None,
    title: str = '',
    severity: str = 'medium',
    gate: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    structured_payload: Dict[str, Any] = None,
    agent_async_task_id: str = None,
):
    """Session 1093 — Follow-up to run_cto_daily_diagnostic.

    Loads the CTOAgent execution result by task id and posts the
    final attention item via the human attention bridge. Enqueued
    with countdown=240s by run_cto_daily_diagnostic so CTOAgent
    has time to finish (180s LLM timeout).

    Session 1094: accepts generic `agent_async_task_id` kwarg (what the
    refactored runner sends). Legacy `cto_async_task_id` kept for backwards
    compatibility — if both are passed, `agent_async_task_id` wins.
    """
    from core.tasks_ops import _impl_post_cto_daily_diagnostic
    effective_id = agent_async_task_id if agent_async_task_id else cto_async_task_id
    return _impl_post_cto_daily_diagnostic(
        cto_async_task_id=effective_id,
        title=title,
        severity=severity,
        gate=gate or {},
        metrics=metrics or {},
        structured_payload=structured_payload or {},
    )

@shared_task(bind=True, max_retries=0, soft_time_limit=300, time_limit=600, name="core.tasks.run_coo_daily_diagnostic")
def run_coo_daily_diagnostic(self):
    """Session 1094 — Daily COOAgent operations diagnostic.

    Computes 24h operational metrics (deliverable velocity, review
    backlog aging, action-item backlog by urgency, stuck initiatives),
    evaluates threshold gates, and — if anomalies detected — dispatches
    COOAgent async + enqueues `post_coo_daily_diagnostic` to publish
    the attention item once the agent narrative is ready.

    Second consumer of the scheduled_diagnostic_runner primitive.
    Identical orchestration surface to CTO; completely different
    metrics shape.
    """
    from core.services.scheduled_diagnostic_runner import run_diagnostic
    from core.services.diagnostics.coo_daily import build_config
    return run_diagnostic(build_config())

@shared_task(bind=True, max_retries=2, default_retry_delay=120, soft_time_limit=180, time_limit=300, name="core.tasks.post_coo_daily_diagnostic")
def post_coo_daily_diagnostic(
    self,
    agent_async_task_id: str = None,
    title: str = '',
    severity: str = 'medium',
    gate: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    structured_payload: Dict[str, Any] = None,
):
    """Session 1094 — Follow-up to run_coo_daily_diagnostic.

    Loads COOAgent execution result and posts via attention bridge.
    Enqueued with countdown=240s by run_coo_daily_diagnostic.
    """
    from core.services.scheduled_diagnostic_runner import post_diagnostic
    from core.services.diagnostics.coo_daily import build_config
    return post_diagnostic(
        build_config(),
        agent_async_task_id=agent_async_task_id,
        title=title,
        severity=severity,
        gate=gate or {},
        metrics=metrics or {},
        structured_payload=structured_payload or {},
    )

@shared_task(bind=True, max_retries=0, soft_time_limit=300, time_limit=600, name="core.tasks.run_trend_daily_diagnostic")
def run_trend_daily_diagnostic(self):
    """Session 1094 — Daily TrendAnalysisAgent spider-intelligence anomaly diagnostic.

    Third consumer of the scheduled_diagnostic_runner primitive. Metrics
    surface is distributional anomaly (volume deltas, coverage gaps,
    concentration, cluster velocity) — structurally different from CTO
    (execution rollups) and COO (throughput + aging).
    """
    from core.services.scheduled_diagnostic_runner import run_diagnostic
    from core.services.diagnostics.trend_analysis_daily import build_config
    return run_diagnostic(build_config())

@shared_task(bind=True, max_retries=2, default_retry_delay=120, soft_time_limit=180, time_limit=300, name="core.tasks.post_trend_daily_diagnostic")
def post_trend_daily_diagnostic(
    self,
    agent_async_task_id: str = None,
    title: str = '',
    severity: str = 'medium',
    gate: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    structured_payload: Dict[str, Any] = None,
):
    """Session 1094 — Follow-up to run_trend_daily_diagnostic.

    Loads TrendAnalysisAgent result and posts via attention bridge.
    Enqueued with countdown=240s by run_trend_daily_diagnostic.
    """
    from core.services.scheduled_diagnostic_runner import post_diagnostic
    from core.services.diagnostics.trend_analysis_daily import build_config
    return post_diagnostic(
        build_config(),
        agent_async_task_id=agent_async_task_id,
        title=title,
        severity=severity,
        gate=gate or {},
        metrics=metrics or {},
        structured_payload=structured_payload or {},
    )

@shared_task(name="core.tasks.run_metrics_action_check")
def run_metrics_action_check():
    from core.tasks_misc import _impl_run_metrics_action_check
    return _impl_run_metrics_action_check()

@shared_task(bind=True, name="core.tasks.run_diagnostic_pipeline_task")
def run_diagnostic_pipeline_task(self, signature_id: str = None, force: bool = False):
    """
    Session 856: Run the diagnostic pipeline for failure analysis.

    Processes signatures with undiagnosed detections:
    1. Diagnoses root causes using multi-source evidence
    2. Generates prioritized prescriptions (fixes)
    3. Creates remediation Initiatives for tracking

    Args:
        signature_id: Optional specific signature to process
        force: Bypass guardrails (cooldown, threshold)

    Called by Celery Beat every 15 minutes.
    """
    from core.services.diagnostic_pipeline import run_diagnostic_pipeline

    task_id = self.request.id if self.request else 'unknown'
    logger.info(f"🔬 [DIAGNOSTIC] Task {task_id} STARTED")

    try:
        result = run_diagnostic_pipeline(
            signature_id=signature_id,
            force=force
        )

        logger.info(
            f"🔬 [DIAGNOSTIC] Task {task_id} COMPLETED: "
            f"processed={result['signatures_processed']}, "
            f"diagnoses={result['diagnoses_created']}, "
            f"prescriptions={result['prescriptions_created']}, "
            f"initiatives={result['initiatives_created']}"
        )

        return result

    except Exception as e:
        logger.error(f"🔬 [DIAGNOSTIC] Task {task_id} FAILED: {e}", exc_info=True)
        raise

