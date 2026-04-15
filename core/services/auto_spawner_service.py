"""
Auto-Spawner Service - Session 872
===================================

Automatic agent/spider spawning based on data sufficiency thresholds.

Based on ChatGPT feedback:
- "They all note '77 is small.' But no one triggers: DataExpansionAgent."
- "That's a missing reflex."

When data is insufficient, this service automatically spawns agents to gather more.
No discussion needed. Just act.

Usage:
    from core.services.auto_spawner_service import AutoSpawnerService

    spawner = AutoSpawnerService()

    # Check if we need more data and auto-spawn if needed
    result = spawner.check_and_spawn(
        data_type='job_listings',
        current_count=77,
        required_count=500,
        context={'topic': 'salary negotiation'}
    )

    if result['spawned']:
        print(f"Auto-spawned: {result['task_ids']}")
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Types of data that can trigger auto-spawning."""
    JOB_LISTINGS = "job_listings"
    SALARY_DATA = "salary_data"
    MARKET_TRENDS = "market_trends"
    COMPETITOR_DATA = "competitor_data"
    USER_FEEDBACK = "user_feedback"
    SPIDER_DATA = "spider_data"
    EXPERIMENT_RESULTS = "experiment_results"


@dataclass
class SpawnThreshold:
    """Configuration for when to auto-spawn."""
    data_type: DataType
    min_required: int              # Minimum data points needed
    optimal: int                   # Optimal data points
    stale_hours: int = 24          # Data older than this is stale
    auto_spawn_enabled: bool = True
    target_agent: str = ""          # Which agent to spawn
    target_spider: str = ""         # Which spider to run
    priority: int = 1               # Task priority


# Default thresholds for common data types
DEFAULT_THRESHOLDS: Dict[str, SpawnThreshold] = {
    'job_listings': SpawnThreshold(
        data_type=DataType.JOB_LISTINGS,
        min_required=100,
        optimal=1000,
        stale_hours=48,
        target_spider='adzuna',
        target_agent='ResearchAgent',
    ),
    'salary_data': SpawnThreshold(
        data_type=DataType.SALARY_DATA,
        min_required=200,
        optimal=2000,
        stale_hours=168,  # 1 week
        target_spider='remoteok',
        target_agent='ResearchAgent',
    ),
    'market_trends': SpawnThreshold(
        data_type=DataType.MARKET_TRENDS,
        min_required=50,
        optimal=500,
        stale_hours=12,
        target_spider='hackernews',
        target_agent='TrendAnalysisAgent',
    ),
    'competitor_data': SpawnThreshold(
        data_type=DataType.COMPETITOR_DATA,
        min_required=10,
        optimal=50,
        stale_hours=72,
        target_spider='crunchbase',
        target_agent='CompetitorAnalysisAgent',
    ),
    'spider_data': SpawnThreshold(
        data_type=DataType.SPIDER_DATA,
        min_required=100,
        optimal=1000,
        stale_hours=24,
        target_spider='',  # All spiders
        target_agent='ResearchAgent',
    ),
}


class AutoSpawnerService:
    """
    Service for automatic agent/spider spawning based on data needs.

    This is the "reflex" that ChatGPT identified as missing.
    When data is insufficient, we don't discuss - we spawn.
    """

    def __init__(self):
        self.thresholds = DEFAULT_THRESHOLDS.copy()
        self.spawn_history: List[Dict[str, Any]] = []

    def check_and_spawn(
        self,
        data_type: str,
        current_count: int,
        required_count: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Check data sufficiency and auto-spawn if needed.

        Args:
            data_type: Type of data (e.g., 'job_listings', 'salary_data')
            current_count: How many data points we have now
            required_count: Override the default minimum (optional)
            context: Additional context for the spawn task
            force: Force spawn even if data seems sufficient

        Returns:
            Dict with:
                - spawned: bool - whether we spawned anything
                - reason: str - why we spawned (or didn't)
                - task_ids: List[str] - IDs of spawned tasks
                - deficit: int - how many data points we need
        """
        context = context or {}

        # Get threshold config
        threshold = self.thresholds.get(data_type)
        if not threshold:
            # Use generic threshold
            threshold = SpawnThreshold(
                data_type=DataType.SPIDER_DATA,
                min_required=required_count or 100,
                optimal=required_count * 10 if required_count else 1000,
                stale_hours=24,
                target_agent='ResearchAgent',
            )

        # Override min if specified
        min_required = required_count or threshold.min_required

        # Check if we need to spawn
        if current_count >= min_required and not force:
            return {
                'spawned': False,
                'reason': f'Data sufficient: {current_count}/{min_required}',
                'task_ids': [],
                'deficit': 0,
            }

        # Calculate deficit
        deficit = max(0, threshold.optimal - current_count)

        # Auto-spawn is a reflex - no discussion
        logger.info(
            f"AUTO-SPAWN REFLEX: {data_type} has {current_count}/{min_required}, "
            f"spawning to gather {deficit} more"
        )

        # Spawn the appropriate agent/spider
        task_ids = self._spawn_data_gatherers(
            threshold=threshold,
            deficit=deficit,
            context=context,
        )

        # Record spawn
        spawn_record = {
            'timestamp': datetime.now().isoformat(),
            'data_type': data_type,
            'current_count': current_count,
            'required_count': min_required,
            'deficit': deficit,
            'task_ids': task_ids,
            'context': context,
        }
        self.spawn_history.append(spawn_record)

        # Session 1103c: was always returning spawned=True even when
        # task_ids was empty (because _spawn_data_gatherers caught
        # its own exceptions internally and returned []). The
        # autonomous reflex orchestrator believed the spawn
        # succeeded and never retried/escalated, so the system
        # could silently stay data-starved while reporting
        # "remediation fired." Now spawned reflects reality.
        spawned_ok = len(task_ids) > 0
        if not spawned_ok:
            logger.error(
                "auto_spawner_service: spawn reflex for %s deficit=%d "
                "produced 0 task_ids — _spawn_data_gatherers swallowed "
                "all spawn attempts. Returning spawned=False so the "
                "orchestrator can retry/escalate.",
                data_type, deficit,
            )
        return {
            'spawned': spawned_ok,
            'reason': (
                f'Insufficient data: {current_count}/{min_required}, '
                f'spawned {len(task_ids)} tasks'
                if spawned_ok
                else f'Spawn reflex FAILED: {current_count}/{min_required}, '
                     f'_spawn_data_gatherers returned 0 task_ids'
            ),
            'task_ids': task_ids,
            'deficit': deficit,
        }

    def _spawn_data_gatherers(
        self,
        threshold: SpawnThreshold,
        deficit: int,
        context: Dict[str, Any]
    ) -> List[str]:
        """Spawn agents and/or spiders to gather data."""
        task_ids = []

        try:
            # Try to spawn spider first
            if threshold.target_spider:
                spider_task_id = self._spawn_spider(
                    spider_name=threshold.target_spider,
                    target_count=deficit,
                    context=context,
                )
                if spider_task_id:
                    task_ids.append(spider_task_id)

            # Then spawn agent for analysis
            if threshold.target_agent:
                agent_task_id = self._spawn_agent(
                    agent_name=threshold.target_agent,
                    task_description=self._build_task_description(threshold, deficit, context),
                    context=context,
                )
                if agent_task_id:
                    task_ids.append(agent_task_id)

        except Exception as e:
            logger.error(f"Failed to spawn data gatherers: {e}")

        return task_ids

    def _spawn_spider(
        self,
        spider_name: str,
        target_count: int,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Spawn a spider to gather data."""
        try:
            from core.tasks import run_spider_with_priority

            # Queue spider with high priority
            task = run_spider_with_priority.delay(
                spider_name=spider_name,
                priority='high',
                context={
                    'auto_spawned': True,
                    'target_count': target_count,
                    **context,
                }
            )

            logger.info(f"Auto-spawned spider: {spider_name} (task {task.id})")
            return task.id

        except ImportError:
            logger.warning("run_spider_with_priority not available, using fallback")
            return self._spawn_spider_fallback(spider_name, target_count, context)
        except Exception as e:
            logger.error(f"Failed to spawn spider {spider_name}: {e}")
            return None

    def _spawn_spider_fallback(
        self,
        spider_name: str,
        target_count: int,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Fallback spider spawning using basic task."""
        try:
            from core.tasks import run_single_spider

            task = run_single_spider.delay(spider_name)
            logger.info(f"Auto-spawned spider (fallback): {spider_name} (task {task.id})")
            return task.id

        except Exception as e:
            logger.error(f"Fallback spider spawn failed: {e}")
            return None

    def _spawn_agent(
        self,
        agent_name: str,
        task_description: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """Spawn an agent to process/analyze data."""
        try:
            from core.tasks import queue_agent_task

            task = queue_agent_task.delay(
                agent_name=agent_name,
                task_description=task_description,
                context={
                    'auto_spawned': True,
                    'spawn_reason': 'data_insufficiency',
                    **context,
                }
            )

            logger.info(f"Auto-spawned agent: {agent_name} (task {task.id})")
            return task.id

        except ImportError:
            logger.warning("queue_agent_task not available")
            return None
        except Exception as e:
            logger.error(f"Failed to spawn agent {agent_name}: {e}")
            return None

    def _build_task_description(
        self,
        threshold: SpawnThreshold,
        deficit: int,
        context: Dict[str, Any]
    ) -> str:
        """Build task description for spawned agent."""
        topic = context.get('topic', 'data analysis')
        data_type = threshold.data_type.value

        return (
            f"[AUTO-SPAWNED] Gather and analyze {data_type} data.\n"
            f"Current data insufficient - need {deficit} more data points.\n"
            f"Topic: {topic}\n"
            f"Priority: HIGH - this was auto-triggered due to data gap.\n"
            f"Target: At least {threshold.optimal} data points total."
        )

    def check_staleness(
        self,
        data_type: str,
        last_updated: datetime
    ) -> Dict[str, Any]:
        """
        Check if data is stale and needs refresh.

        Args:
            data_type: Type of data
            last_updated: When the data was last updated

        Returns:
            Dict with is_stale, hours_old, and recommendation
        """
        threshold = self.thresholds.get(data_type, DEFAULT_THRESHOLDS.get('spider_data'))
        if not threshold:
            threshold = SpawnThreshold(
                data_type=DataType.SPIDER_DATA,
                min_required=100,
                optimal=1000,
                stale_hours=24,
            )

        hours_old = (datetime.now() - last_updated).total_seconds() / 3600
        is_stale = hours_old > threshold.stale_hours

        return {
            'is_stale': is_stale,
            'hours_old': round(hours_old, 1),
            'stale_threshold': threshold.stale_hours,
            'recommendation': 'refresh_data' if is_stale else 'data_fresh',
        }

    def get_spawn_stats(self) -> Dict[str, Any]:
        """Get statistics about auto-spawning."""
        if not self.spawn_history:
            return {
                'total_spawns': 0,
                'spawns_by_type': {},
                'total_tasks_created': 0,
            }

        spawns_by_type: Dict[str, int] = {}
        total_tasks = 0

        for record in self.spawn_history:
            data_type = record.get('data_type', 'unknown')
            spawns_by_type[data_type] = spawns_by_type.get(data_type, 0) + 1
            total_tasks += len(record.get('task_ids', []))

        return {
            'total_spawns': len(self.spawn_history),
            'spawns_by_type': spawns_by_type,
            'total_tasks_created': total_tasks,
            'last_spawn': self.spawn_history[-1] if self.spawn_history else None,
        }


# Convenience function for quick checks
def auto_spawn_if_needed(
    data_type: str,
    current_count: int,
    required_count: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Quick check and spawn if data is insufficient.

    This is the "reflex" function - call it whenever you have data
    and want to ensure it's sufficient.

    Args:
        data_type: Type of data
        current_count: Current data count
        required_count: Optional minimum required
        context: Additional context

    Returns:
        Spawn result dict
    """
    spawner = AutoSpawnerService()
    return spawner.check_and_spawn(
        data_type=data_type,
        current_count=current_count,
        required_count=required_count,
        context=context,
    )


# Decorator for automatic data sufficiency checks
def ensure_sufficient_data(
    data_type: str,
    count_extractor,  # Callable that gets count from result
    min_required: int = 100
):
    """
    Decorator that auto-spawns when function returns insufficient data.

    Usage:
        @ensure_sufficient_data('job_listings', lambda r: len(r.get('listings', [])), 500)
        def get_job_listings(query):
            # ... get listings ...
            return {'listings': [...]}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Extract count
            try:
                count = count_extractor(result)
            except Exception:
                count = 0

            # Check and spawn if needed
            if count < min_required:
                context = {
                    'source_function': func.__name__,
                    'args': str(args)[:200],
                }
                spawn_result = auto_spawn_if_needed(
                    data_type=data_type,
                    current_count=count,
                    required_count=min_required,
                    context=context,
                )

                # Attach spawn info to result
                if isinstance(result, dict):
                    result['_auto_spawn'] = spawn_result

            return result
        return wrapper
    return decorator
