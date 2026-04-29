"""Learning loop / pattern mining Celery tasks.

Migrated out of `core.tasks` in Phase 3 of the Wave B refactor. Every
task here keeps the registered Celery name it had in `core.tasks`
(locked by the explicit `name=` kwarg from Phase 1), so beat schedule
entries (`cleanup-learning-readback`, `decay-learning-patterns`),
PeriodicTask DB rows (11 enabled), settings.py task-routing config,
the `add_critical_celery_tasks` management-cmd string dispatcher, and
Python imports (`bootstrap_learning_system`, `views_projects_api`,
`warmup_body_systems`) all continue to resolve unchanged.

Tasks (learning loop / pattern mining / project learning):

- run_learning_loop_cycle
- summarize_learning_readback
- cleanup_learning_readback_events
- decay_learning_patterns
- update_learning_profiles
- run_daily_learning_pipeline
- run_agent_learning_cycle
- update_agent_effectiveness_from_learning
- broadcast_learning_status
- embed_daily_agent_learning
- run_project_learning_cycle
- run_single_project_learning
- mine_learning_patterns
- check_learning_loop_slo  (registered: core.check_learning_loop_slo — non-standard prefix)

Notes:

- `run_daily_learning_pipeline` dispatches two stay-behind tasks
  (`core.tasks.discover_success_patterns`, `core.tasks.generate_user_insights`)
  via `current_app.send_task(...)` registered-name dispatch. This
  decouples this module from the Python location of those tasks
  (which are themselves future migration candidates) and matches the
  codebase's established cross-module dispatch idiom.
- `update_learning_profiles.delay()` is left as a Python attribute
  call because that task lives in this module after the move.
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="core.tasks.run_learning_loop_cycle")
def run_learning_loop_cycle(lookback_days: int = 7):
    """
    Session 945: Run the learning loop cycle to extract patterns from execution data.

    Analyzes ToolCallRecord and DecisionRecord data to extract actionable learnings
    that are then persisted to LearningPattern for injection into agent prompts.

    Args:
        lookback_days: How many days of data to analyze

    Returns:
        Dict with cycle statistics
    """
    from core.services.learning_loop_orchestrator import LearningLoopOrchestrator

    logger.info(f"🧠 [LEARNING-LOOP] Starting learning cycle (lookback={lookback_days}d)...")

    try:
        orchestrator = LearningLoopOrchestrator(lookback_days=lookback_days)
        result = orchestrator.run_learning_cycle()

        logger.info(
            f"🧠 [LEARNING-LOOP] Complete - "
            f"extracted {result['learnings_extracted']} learnings, "
            f"persisted {result['patterns_persisted']} patterns"
        )

        return result

    except Exception as e:
        logger.error(f"🧠 [LEARNING-LOOP] Failed: {e}", exc_info=True)
        raise

@shared_task(ignore_result=True, name="core.tasks.summarize_learning_readback")
def summarize_learning_readback():
    """Summarize learning readback telemetry — logs how often the feedback loop is closing."""
    from django.utils import timezone
    from datetime import timedelta
    from core.models.learning_readback import LearningReadbackEvent

    cutoff = timezone.now() - timedelta(hours=24)
    qs = LearningReadbackEvent.objects.filter(created_at__gte=cutoff)
    total = qs.count()
    consulted = qs.filter(learning_consulted=True).count()
    used = qs.filter(learning_used=True).count()
    tool_ok_count = qs.filter(tool_ok=True).count()

    logger.info(
        f"[LEARNING-READBACK] 24h summary: {total} routing decisions, "
        f"{consulted} consulted learning ({consulted*100//max(total,1)}%), "
        f"{used} influenced by learning ({used*100//max(total,1)}%), "
        f"{tool_ok_count} tool successes"
    )
    return {'total': total, 'consulted': consulted, 'used': used, 'tool_ok': tool_ok_count}

@shared_task(ignore_result=True, name="core.tasks.cleanup_learning_readback_events")
def cleanup_learning_readback_events(retention_days: int = 30):
    """Delete LearningReadbackEvent rows older than retention_days."""
    from django.utils import timezone
    from datetime import timedelta
    from core.models.learning_readback import LearningReadbackEvent

    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted, _ = LearningReadbackEvent.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"[LEARNING-READBACK] Cleanup: deleted {deleted} events older than {retention_days}d")
    return {'deleted': deleted}

@shared_task(name="core.tasks.decay_learning_patterns")
def decay_learning_patterns():
    """Session 1085: Weekly decay of stale/ineffective learning patterns."""
    from core.services.learning_pattern_engine import LearningPatternEngine
    engine = LearningPatternEngine()
    result = engine.decay_stale_patterns(inactive_days=30, decay_factor=0.9)
    return result

@shared_task(name="core.tasks.update_learning_profiles")
def update_learning_profiles():
    from core.tasks_misc import _impl_update_learning_profiles
    return _impl_update_learning_profiles()

@shared_task(name="core.tasks.run_daily_learning_pipeline")
def run_daily_learning_pipeline():
    """
    Run the complete daily learning pipeline.
    Called by Celery Beat scheduler.
    """
    logger.info("🚀 [LEARNING] Starting daily learning pipeline...")

    try:
        from celery import current_app
        results = {
            'patterns': None,
            'insights': None,
            'profiles': None,
        }

        # Step 1: Discover patterns
        logger.info("🚀 [LEARNING] Step 1: Discovering patterns...")
        results['patterns'] = current_app.send_task(
            'core.tasks.discover_success_patterns',
        ).get(timeout=300)

        # Step 2: Generate insights
        logger.info("🚀 [LEARNING] Step 2: Generating insights...")
        results['insights'] = current_app.send_task(
            'core.tasks.generate_user_insights',
        ).get(timeout=300)

        # Step 3: Update profiles
        logger.info("🚀 [LEARNING] Step 3: Updating profiles...")
        results['profiles'] = update_learning_profiles.delay().get(timeout=300)

        logger.info(f"🚀 [LEARNING] Daily pipeline complete: {results}")
        return {'status': 'completed', 'results': results}

    except Exception as e:
        logger.exception(f"🚀 [LEARNING] Daily pipeline failed: {e}")
        return {'status': 'failed', 'error': str(e)}

@shared_task(name="core.tasks.run_agent_learning_cycle")
def run_agent_learning_cycle():
    from core.tasks_agents import _impl_run_agent_learning_cycle
    return _impl_run_agent_learning_cycle()

@shared_task(name="core.tasks.update_agent_effectiveness_from_learning")
def update_agent_effectiveness_from_learning():
    from core.tasks_misc import _impl_update_agent_effectiveness_from_learning
    return _impl_update_agent_effectiveness_from_learning()

@shared_task(name="core.tasks.broadcast_learning_status")
def broadcast_learning_status():
    from core.tasks_agents import _impl_broadcast_learning_status
    return _impl_broadcast_learning_status()

@shared_task(name="core.tasks.embed_daily_agent_learning")
def embed_daily_agent_learning():
    from core.tasks_agents import _impl_embed_daily_agent_learning
    return _impl_embed_daily_agent_learning()

@shared_task(name="core.tasks.run_project_learning_cycle")
def run_project_learning_cycle():
    """
    Celery Beat task: Check all projects with learning enabled
    and run research updates for those due.

    Session 354: Project Learning Loop
    Runs daily at 6 AM to check for due projects.
    """
    from core.models_partnership import PartnershipProject
    from django.utils import timezone

    logger.info("🧠 [SESSION 354] Starting project learning cycle check...")

    try:
        # Find projects with learning enabled that are due
        due_projects = PartnershipProject.objects.filter(
            learning_enabled=True,
            next_learning_run__lte=timezone.now()
        )

        if not due_projects.exists():
            logger.info("🧠 [SESSION 354] No projects due for learning")
            return {'projects_queued': 0, 'results': []}

        results = []
        for project in due_projects:
            try:
                result = run_single_project_learning.delay(str(project.id))
                results.append({
                    'project_id': str(project.id),
                    'project_name': project.project_name,
                    'task_id': result.id
                })
                logger.info(f"🧠 [SESSION 354] Queued learning for: {project.project_name}")
            except Exception as e:
                logger.error(f"🧠 [SESSION 354] Failed to queue learning for {project.id}: {e}")

        logger.info(f"🧠 [SESSION 354] Queued {len(results)} projects for learning")
        return {
            'projects_queued': len(results),
            'results': results
        }

    except Exception as e:
        logger.exception(f"🧠 [SESSION 354] Learning cycle check failed: {e}")
        return {'error': str(e)}

@shared_task(name="core.tasks.run_single_project_learning")
def run_single_project_learning(project_id: str):
    from core.tasks_ops import _impl_run_single_project_learning
    return _impl_run_single_project_learning(project_id)

@shared_task(name='core.tasks.mine_learning_patterns')
def mine_learning_patterns(days_back: int = 30):
    """
    Session 767: Mine AgentLearning records to discover patterns.

    Analyzes agent learning data to create LearningPattern records for:
    1. spider_effectiveness - Which spider data helps which agents
    2. agent_collaboration - Which teacher-student pairs work best
    3. learning_type_impact - Which learning types produce best gains
    4. top_teacher - Most effective teaching agents

    These patterns are then injected into agent prompts to improve performance.

    Args:
        days_back: How many days of data to analyze (default 30)

    Returns:
        Mining statistics
    """
    from core.services.learning_pattern_engine import get_learning_pattern_engine

    logger.info(f"🔍 [PATTERN MINING] Starting pattern mining (last {days_back} days)...")

    try:
        engine = get_learning_pattern_engine()
        result = engine.mine_patterns(days_back=days_back)

        logger.info(
            f"🔍 [PATTERN MINING] Complete: "
            f"{result.get('patterns_created', 0)} created, "
            f"{result.get('patterns_updated', 0)} updated, "
            f"{result.get('total_active_patterns', 0)} total active"
        )

        return {
            'success': True,
            **result
        }

    except Exception as e:
        logger.error(f"🔍 [PATTERN MINING] Failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}

@shared_task(name='core.check_learning_loop_slo', ignore_result=True)
def check_learning_loop_slo():
    """Daily SLO check: learning loop usage_rate should be >= 5% over 24h.

    Logs warning if usage drops to 0 (regression catch).
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*), "
            "COUNT(*) FILTER (WHERE learning_used = true), "
            "COUNT(*) FILTER (WHERE prompt_injection_applied = true) "
            "FROM core_learningreadbackevent "
            "WHERE created_at > NOW() - INTERVAL '24 hours'"
        )
        row = cursor.fetchone()
        total, used, pij = row[0], row[1], row[2]

    if total == 0:
        logger.warning("[LEARNING_SLO] No readback events in last 24h — PA may be down")
        return {'status': 'no_events', 'total': 0}

    usage_rate = round(used / total * 100, 1)
    pij_rate = round(pij / total * 100, 1)

    if used == 0:
        logger.warning(
            f"[LEARNING_SLO] REGRESSION: used_true=0 in last 24h "
            f"(total={total}, prompt_injection={pij}). "
            f"Learning loop may be broken again."
        )
    elif usage_rate < 5.0:
        logger.info(
            f"[LEARNING_SLO] Below target: usage_rate={usage_rate}% "
            f"(target>=5%, total={total}, used={used}, pij={pij})"
        )
    else:
        logger.info(
            f"[LEARNING_SLO] OK: usage_rate={usage_rate}%, "
            f"pij_rate={pij_rate}% (total={total})"
        )

    return {
        'status': 'regression' if used == 0 else ('below_target' if usage_rate < 5.0 else 'ok'),
        'total': total,
        'used': used,
        'prompt_injection': pij,
        'usage_rate': usage_rate,
    }

