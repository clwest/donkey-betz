"""Boardroom / governance / pilot Celery tasks.

Migrated out of `core.tasks` in Phase 3 of the Wave B refactor. Every
task here keeps the registered Celery name it had in `core.tasks`
(locked by the explicit `name=` kwarg from Phase 1), so beat schedule
entries, PeriodicTask DB rows, settings.py task-routing config, and
string-dispatched callers all continue to resolve unchanged.

Tasks (governance / pilot lifecycle):

- cleanup_boardroom_junk
- auto_approve_boardroom_items
- cleanup_expired_boardroom_items
- auto_promote_decisions  (DEPRECATED — see ai_promote_decisions)
- auto_approve_low_risk_gates
- auto_promote_low_risk_decisions
- report_pending_review_metrics
- ai_promote_decisions
- auto_complete_pilots
- evaluate_pilots_with_thinking_agent
- evaluate_and_complete_pilots
- execute_pilot_implementations
- process_gates_and_deploy_pilots
- enrich_boardroom_ml_predictions
- process_gate_progression
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="core.tasks.cleanup_boardroom_junk")
def cleanup_boardroom_junk(spider_action_hours: int = 6):
    from core.tasks_ops import _impl_cleanup_boardroom_junk
    return _impl_cleanup_boardroom_junk(spider_action_hours)

@shared_task(name="core.tasks.auto_approve_boardroom_items")
def auto_approve_boardroom_items():
    from core.tasks_ops import _impl_auto_approve_boardroom_items
    return _impl_auto_approve_boardroom_items()

@shared_task(name="core.tasks.cleanup_expired_boardroom_items")
def cleanup_expired_boardroom_items(days_old: int = 7):
    from core.tasks_misc import _impl_cleanup_expired_boardroom_items
    return _impl_cleanup_expired_boardroom_items(days_old)

@shared_task(bind=True, name="core.tasks.auto_promote_decisions")
def auto_promote_decisions(self, quality_threshold: float = 0.6, max_promotions: int = 3):
    """
    Session 362: Automatically promote high-quality decisions to canonical policies.

    DEPRECATED: Session 658 introduced ai_promote_decisions which uses GPT-5-mini
    for intelligent evaluation. This legacy task is kept for backwards compatibility
    but now defers to the AI-powered version.

    Args:
        quality_threshold: Minimum quality_score to be eligible (0.0-1.0)
        max_promotions: Maximum decisions to promote per run

    Returns:
        Stats about promotions made
    """
    # Session 659: This task is deprecated - use ai_promote_decisions instead
    # The AI Decision Promoter (Session 658) uses GPT-5-mini for intelligent evaluation
    # which is more accurate than the rule-based quality_score approach.
    logger.info("🏛️ [AUTO-PROMOTE] DEPRECATED - Use ai_promote_decisions (Session 658) instead")

    return {
        'status': 'deprecated',
        'message': 'This task is deprecated. Use ai_promote_decisions (Session 658) which uses GPT-5-mini for intelligent evaluation.',
        'redirect': 'core.tasks.ai_promote_decisions'
    }

@shared_task(name="core.tasks.auto_approve_low_risk_gates")
def auto_approve_low_risk_gates(
    max_gates: int = 20,
    auto_deploy: bool = False,
    dry_run: bool = False
):
    from core.tasks_ops import _impl_auto_approve_low_risk_gates
    return _impl_auto_approve_low_risk_gates(max_gates, auto_deploy, dry_run)

@shared_task(name="core.tasks.auto_promote_low_risk_decisions")
def auto_promote_low_risk_decisions(dry_run: bool = False):
    from core.tasks_misc import _impl_auto_promote_low_risk_decisions
    return _impl_auto_promote_low_risk_decisions(dry_run)

@shared_task(name="core.tasks.report_pending_review_metrics")
def report_pending_review_metrics():
    from core.tasks_misc import _impl_report_pending_review_metrics
    return _impl_report_pending_review_metrics()

@shared_task(ignore_result=True, name="core.tasks.ai_promote_decisions")
def ai_promote_decisions(batch_size: int = 50):
    from core.tasks_misc import _impl_ai_promote_decisions
    return _impl_ai_promote_decisions(batch_size)

@shared_task(name="core.tasks.auto_complete_pilots")
def auto_complete_pilots():
    from core.tasks_ops import _impl_auto_complete_pilots
    return _impl_auto_complete_pilots()

@shared_task(name="core.tasks.evaluate_pilots_with_thinking_agent")
def evaluate_pilots_with_thinking_agent():
    from core.tasks_ops import _impl_evaluate_pilots_with_thinking_agent
    return _impl_evaluate_pilots_with_thinking_agent()

@shared_task(name='core.tasks.evaluate_and_complete_pilots')
def evaluate_and_complete_pilots():
    from core.tasks_financial import _impl_evaluate_and_complete_pilots
    return _impl_evaluate_and_complete_pilots()

@shared_task(name='core.tasks.execute_pilot_implementations')
def execute_pilot_implementations(batch_size: int = 10):
    from core.tasks_ops import _impl_execute_pilot_implementations
    return _impl_execute_pilot_implementations(batch_size)

@shared_task(name='core.tasks.process_gates_and_deploy_pilots', ignore_result=True)
def process_gates_and_deploy_pilots(batch_size: int = 10, risk_levels: list = None):
    from core.tasks_misc import _impl_process_gates_and_deploy_pilots
    return _impl_process_gates_and_deploy_pilots(batch_size, risk_levels)

@shared_task(name='core.tasks.enrich_boardroom_ml_predictions', ignore_result=True)
def enrich_boardroom_ml_predictions():
    from core.tasks_financial import _impl_enrich_boardroom_ml_predictions
    return _impl_enrich_boardroom_ml_predictions()

@shared_task(name='core.tasks.process_gate_progression')
def process_gate_progression(
    dry_run: bool = False,
    limit: int = 50,
    auto_waive_low_risk: bool = True,
    auto_approve_ready: bool = True,
    start_pilots: bool = True,
):
    from core.tasks_misc import _impl_process_gate_progression
    return _impl_process_gate_progression(dry_run, limit, auto_waive_low_risk, auto_approve_ready, start_pilots)

