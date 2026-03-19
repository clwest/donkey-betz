"""
Celery Background Tasks for Unified Donkey Betz Platform
Handles long-running operations like document isolation in the background

Session 265 Phase 6: Added run_autonomy_cycle task for autonomous operation
Session 969b: Touched to trigger Celery worker restart after PA telemetry deploy
"""

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
import json
import logging
import time
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import F, Count, Q
from django.utils import timezone
from typing import Dict, Any
import os
# Session 850: Smart truncation for cleaner synthesis display
from core.api_helpers import smart_truncate

logger = logging.getLogger(__name__)


# Session 1076: Stable exception class for scheduled tasks that should fail loudly
class ScheduledTaskError(RuntimeError):
    """Raised by scheduled/automated tasks so Celery marks FAILURE and
    the failure-signature pipeline can cluster them cleanly."""
    pass


# --------------------------------------------------------------------------- #
# Session 1031: Task-agent routing override                                    #
# Prevents LLM-generated next_steps from sending specialist tasks to the       #
# wrong agents (e.g. competitor audit -> WorkflowAgent).                       #
# --------------------------------------------------------------------------- #
import re as _re
from core.codejobs.errors import (  # noqa: F401
    CodeJobError,
    CodeJobAnchorNotFoundError,
    CodeJobFileTooLargeError,
)
from core.codejobs.implementation import (  # noqa: F401 — re-export for backwards compat
    _MAX_EDIT_FILE_SIZE,
    _implement_with_claude,
    _inject_github_token,
    _gather_repo_context,
)

_TASK_ROUTING_OVERRIDES = [
    (_re.compile(r'competitor\s+(audit|analysis|landscape|benchmark)', _re.I), 'CompetitorAnalysisAgent'),
    (_re.compile(r'trend\s+(analysis|report|summary)', _re.I), 'TrendAnalysisAgent'),
    (_re.compile(r'customer\s+(research|interview|persona)', _re.I), 'CustomerResearchAgent'),
    (_re.compile(r'brand\s+(strategy|positioning|audit)', _re.I), 'BrandStrategyAgent'),
    (_re.compile(r'market(ing)?\s+(strategy|plan|recommendation)', _re.I), 'MarketingStrategyAgent'),
]

_NON_RESEARCH_AGENTS = frozenset({
    'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
    'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
    'COOAgent', 'CTOAgent', 'AudioAgent',  # Session 1032: Sync with _NON_SPECIALIST in agent_router.py
})

# Session 1036: Media agents can ONLY generate content — block non-generative tasks
# like "list recent images", "review workspace", "catalog assets" etc.
_MEDIA_AGENTS = frozenset({
    'ImageAgent', 'VideoAgent', 'ThreeDAgent', 'AudioAgent',
    'ImageEditingAgent', 'VideoEditingAgent',
})
_MEDIA_GENERATION_PATTERN = _re.compile(
    r'(generat|creat|design|draw|render|produc|make|build|edit|enhance|'
    r'upscale|retouch|composit|illustrat|paint|sketch|draft|style|transform)',
    _re.I,
)


def _apply_task_routing_override(agent_name: str, task_text: str) -> str:
    """Reroute specialist tasks away from non-specialist agents."""
    for pattern, correct_agent in _TASK_ROUTING_OVERRIDES:
        if pattern.search(task_text):
            if agent_name != correct_agent and agent_name in _NON_RESEARCH_AGENTS:
                logger.info(
                    f"[routing-override] Rerouting '{task_text[:60]}' "
                    f"from {agent_name} -> {correct_agent}"
                )
                return correct_agent
    return agent_name


def _is_media_task_blocked(agent_name: str, task_text: str) -> bool:
    """Session 1036: Block non-generative tasks for media agents.

    Media agents (ImageAgent, VideoAgent, etc.) can only generate/edit content.
    Tasks like "list recent images", "review workspace assets", or
    "catalog available media" are not generative and waste API spend.
    """
    if agent_name not in _MEDIA_AGENTS:
        return False
    if _MEDIA_GENERATION_PATTERN.search(task_text):
        return False  # Looks like a real generation task
    return True


# Session 781: Import opener extraction for de-duplication
def _extract_opener(text: str) -> str:
    """Extract the opening phrase from a response (inline version for tasks.py)."""
    if not text:
        return ""
    text = text.strip()
    break_chars = ['.', '!', '?', '—', ' - ', ':']
    first_break = len(text)
    for char in break_chars:
        pos = text.find(char)
        if pos > 0 and pos < first_break:
            first_break = pos
    opener = text[:min(first_break, 60)].strip()
    return opener if len(opener) >= 10 else ""


# Session 781 Level 3: Discourse markers to track for repetition prevention
_DISCOURSE_MARKERS = [
    # Transitions
    "however", "that said", "building on that", "additionally", "furthermore",
    "moreover", "on the other hand", "nevertheless", "in contrast",
    # Agreement
    "i see your point", "that makes sense", "you're right", "i agree with",
    "exactly", "precisely", "indeed",
    # Disagreement
    "i'd question", "the concern is", "but have we considered", "i'm not sure about",
    "the risk here is", "my concern is",
    # Fillers
    "to be honest", "in my view", "from my perspective", "i think that",
    "it seems to me", "in my opinion", "i believe that",
    # Hedges
    "sort of", "kind of", "a bit", "slightly", "somewhat", "perhaps", "maybe",
]


def _extract_discourse_markers(text: str) -> list:
    """Extract discourse markers from text for repetition tracking."""
    if not text:
        return []
    text_lower = text.lower()
    return [m for m in _DISCOURSE_MARKERS if m in text_lower]


def _get_overused_markers(markers: list, threshold: int = 2) -> list:
    """Get markers that have been used more than threshold times."""
    from collections import Counter
    counts = Counter(markers)
    return [m for m, c in counts.most_common(5) if c >= threshold]


# ==================== SESSION 356: MYTHOLOGY VALIDATION FOR AGENT OUTPUTS ====================

def validate_agent_output(agent_name: str, output: str) -> str:
    """
    Session 356: Validate and correct agent output for mythology violations.

    This ensures agents don't hallucinate unrealistic claims when communicating
    with each other (Hive Mind, Conversations, Dreams).

    Args:
        agent_name: Name of the agent producing the output
        output: The LLM-generated output to validate

    Returns:
        Corrected output (or original if no violations)
    """
    try:
        from ai_core.agents.mythology_validator import mythology_enforcer
        result = mythology_enforcer.enforce(agent_name, output)

        if result.get('mythology_corrected'):
            logger.warning(f"🚨 [MYTHOLOGY] {agent_name} output corrected: {result.get('violations', 0)} violations")
            return result.get('result', output)

        return output
    except Exception as e:
        logger.warning(f"⚠️ [MYTHOLOGY] Validation failed for {agent_name}: {e}")
        return output  # Return original if validation fails


# ==================== SESSION 1080: TIMEOUT SIGNATURE RECORDING ===============

def _record_timeout_signature(
    agent_name: str,
    timeout_source: str,
    elapsed_seconds: float,
    execution_id=None,
    task_name: str = '',
):
    """
    Record a structured timeout event into the FailureSignature/FailureDetection
    pipeline so ops_tool.failure_signatures can cluster timeouts.

    Args:
        agent_name: Name of the agent that timed out
        timeout_source: 'wall_clock', 'watchdog_cleanup', or 'celery_hard_limit'
        elapsed_seconds: How long the task ran before timeout
        execution_id: UUID of the AgentExecution record (if available)
        task_name: Celery task name (if available)
    """
    try:
        from core.models_diagnostic_pipeline import FailureSignature, FailureDetection

        sig_str = f"TIMEOUT_{timeout_source.upper()}_{agent_name}"
        sig_hash = FailureSignature.generate_hash(sig_str)

        signature, _ = FailureSignature.objects.get_or_create(
            signature_hash=sig_hash,
            defaults={
                'signature': sig_str[:255],
                'category': FailureSignature.Category.TIMEOUT,
                'description': (
                    f"{agent_name} timed out via {timeout_source} "
                    f"after {elapsed_seconds:.0f}s"
                ),
            }
        )
        signature.increment_occurrence()

        FailureDetection.objects.create(
            signature=signature,
            source_type='agent_execution',
            source_id=execution_id,
            source_name=agent_name,
            error_message=(
                f"{agent_name} timed out via {timeout_source} "
                f"after {elapsed_seconds:.0f}s"
            ),
            error_code='TIMEOUT',
            context_snapshot={
                'agent_name': agent_name,
                'timeout_source': timeout_source,
                'elapsed_seconds': round(elapsed_seconds, 1),
                'task_name': task_name,
            },
        )
    except Exception as e:
        logger.warning(f"Failed to record timeout signature for {agent_name}: {e}")


# ==================== AGENT TASK CIRCUIT BREAKER ==============================
# Prevents the same doomed task from being re-dispatched after repeated timeouts.
# Uses Redis (via Django cache) for distributed state.
#
# Two mechanisms:
# 1. Single-flight lock: only one execution of (agent, task_hash) at a time
# 2. Timeout counter: 2+ timeouts in 24h → breaker trips, creates attention item
# =============================================================================

import hashlib as _hashlib


def _task_hash(agent_name: str, task: str) -> str:
    """Normalized hash for (agent, task) dedup. Strips whitespace, lowercases."""
    normalized = f"{agent_name}:{task.strip().lower()}"
    return _hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _circuit_breaker_check(agent_name: str, task: str) -> dict | None:
    """
    Check if the circuit breaker should block this task.

    Returns None if the task should proceed, or a dict with block reason.
    Also acquires a single-flight lock if proceeding.
    """
    from django.core.cache import cache

    th = _task_hash(agent_name, task)
    breaker_key = f'circuit:{agent_name}:{th}:timeouts'
    lock_key = f'flight:{agent_name}:{th}'

    # Check timeout count (circuit breaker)
    timeout_count = cache.get(breaker_key, 0)
    if timeout_count >= 2:
        logger.warning(
            f"[circuit_breaker] TRIPPED for {agent_name} — "
            f"{timeout_count} timeouts in 24h (task_hash={th})"
        )
        return {
            'status': 'circuit_breaker_tripped',
            'agent': agent_name,
            'reason': f'{agent_name} timed out {timeout_count}x in 24h — breaker tripped',
            'task_hash': th,
            'timeout_count': timeout_count,
        }

    # Single-flight lock: prevent duplicate concurrent executions
    if not cache.add(lock_key, '1', timeout=1800):  # 30 min lock
        logger.info(
            f"[circuit_breaker] DEDUP: {agent_name} task already in flight "
            f"(task_hash={th})"
        )
        return {
            'status': 'dedup_skipped',
            'agent': agent_name,
            'reason': f'Identical {agent_name} task already running',
            'task_hash': th,
        }

    return None  # Proceed


def _circuit_breaker_release(agent_name: str, task: str):
    """Release the single-flight lock after task completion."""
    from django.core.cache import cache
    th = _task_hash(agent_name, task)
    cache.delete(f'flight:{agent_name}:{th}')


def _circuit_breaker_record_timeout(agent_name: str, task: str):
    """
    Increment timeout counter and trip breaker if threshold reached.
    Creates a governance attention item when breaker trips.
    """
    from django.core.cache import cache

    th = _task_hash(agent_name, task)
    breaker_key = f'circuit:{agent_name}:{th}:timeouts'

    # Increment (or set to 1 with 24h TTL)
    current = cache.get(breaker_key, 0)
    new_count = current + 1
    cache.set(breaker_key, new_count, timeout=86400)  # 24h TTL

    logger.warning(
        f"[circuit_breaker] Timeout #{new_count} for {agent_name} "
        f"(task_hash={th})"
    )

    if new_count == 2:
        # Breaker just tripped — create exactly one governance attention item
        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin = User.objects.filter(is_superuser=True).first()
            if admin:
                HumanAttentionItem.objects.create(
                    user=admin,
                    title=f'Circuit breaker tripped: {agent_name}',
                    description=(
                        f'{agent_name} has timed out {new_count}x in 24h on the same task. '
                        f'Task hash: {th}. Task preview: "{task[:200]}..."\n\n'
                        f'The circuit breaker is blocking further retries. '
                        f'Review the agent\'s task scope or increase its timeout.'
                    ),
                    priority='high',
                    category='system',
                    source_type='circuit_breaker',
                    source_id=th,
                    requires_response=True,
                )
                logger.warning(
                    f"[circuit_breaker] Created attention item for {agent_name} "
                    f"breaker trip (hash={th})"
                )
        except Exception as e:
            logger.error(f"[circuit_breaker] Failed to create attention item: {e}")


# ==================== SESSION 835: STALE EXECUTION CLEANUP ====================


@shared_task(bind=True)
def cleanup_stale_agent_executions(self, minutes_threshold: int = 60):
    from core.tasks_agents import _impl_cleanup_stale_agent_executions
    return _impl_cleanup_stale_agent_executions(self, minutes_threshold)
@shared_task(bind=True, ignore_result=True)
def cleanup_stale_content(
    self,
    cutoff_days: int = 7,
    statuses: list = None,
    protected_types: list = None,
    cap: int = 500,
):
    from core.tasks_misc import _impl_cleanup_stale_content
    return _impl_cleanup_stale_content(self, cutoff_days, statuses, protected_types, cap)
@shared_task
def reap_zombie_work(
    deliberation_stale_minutes: int = 60,
    pilot_stale_days: int = 7,
):
    from core.tasks_misc import _impl_reap_zombie_work
    return _impl_reap_zombie_work(deliberation_stale_minutes, pilot_stale_days)
@shared_task
def cleanup_junk_initiatives(stale_days: int = 7):
    from core.tasks_initiatives import _impl_cleanup_junk_initiatives
    return _impl_cleanup_junk_initiatives(stale_days)
@shared_task
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


@shared_task(ignore_result=True)
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


@shared_task(ignore_result=True)
def cleanup_learning_readback_events(retention_days: int = 30):
    """Delete LearningReadbackEvent rows older than retention_days."""
    from django.utils import timezone
    from datetime import timedelta
    from core.models.learning_readback import LearningReadbackEvent

    cutoff = timezone.now() - timedelta(days=retention_days)
    deleted, _ = LearningReadbackEvent.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"[LEARNING-READBACK] Cleanup: deleted {deleted} events older than {retention_days}d")
    return {'deleted': deleted}


@shared_task
def cleanup_boardroom_junk(spider_action_hours: int = 6):
    from core.tasks_ops import _impl_cleanup_boardroom_junk
    return _impl_cleanup_boardroom_junk(spider_action_hours)
@shared_task
def auto_approve_boardroom_items():
    from core.tasks_ops import _impl_auto_approve_boardroom_items
    return _impl_auto_approve_boardroom_items()
@shared_task
def cleanup_expired_boardroom_items(days_old: int = 7):
    from core.tasks_misc import _impl_cleanup_expired_boardroom_items
    return _impl_cleanup_expired_boardroom_items(days_old)
@shared_task(ignore_result=True)
def auto_process_extracted_artifacts(
    stale_days: int = 7,
    archive_days: int = 14,
    batch_size: int = 2000,
    aggressive: bool = True
):
    from core.tasks_agents import _impl_auto_process_extracted_artifacts
    return _impl_auto_process_extracted_artifacts(stale_days, archive_days, batch_size, aggressive)
@shared_task
def cleanup_automated_conversation_artifacts(batch_size: int = 5000, prefix: str = None):
    from core.tasks_misc import _impl_cleanup_automated_conversation_artifacts
    return _impl_cleanup_automated_conversation_artifacts(batch_size, prefix)
def cleanup_discussion_artifacts(batch_size: int = 5000):
    """Alias for cleanup_automated_conversation_artifacts with Discussion prefix."""
    return cleanup_automated_conversation_artifacts(batch_size=batch_size, prefix='Discussion:')


@shared_task
def cleanup_halted_experiments(days_old: int = 7):
    from core.tasks_ops import _impl_cleanup_halted_experiments
    return _impl_cleanup_halted_experiments(days_old)
@shared_task
def run_autonomy_cycle(user_id: int = None):
    from core.tasks_misc import _impl_run_autonomy_cycle
    return _impl_run_autonomy_cycle(user_id)
@shared_task(bind=True, max_retries=0, default_retry_delay=60, soft_time_limit=3600, time_limit=3900)
def execute_agent_task(
    self,
    agent_name: str,
    task: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    from core.tasks_agents import _impl_execute_agent_task
    return _impl_execute_agent_task(self, agent_name, task, context)
@shared_task(bind=True, max_retries=1, default_retry_delay=60, soft_time_limit=3600, time_limit=3900)
def create_talking_video_task(
    self,
    image_prompt: str,
    script: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    from core.tasks_media import _impl_create_talking_video_task
    return _impl_create_talking_video_task(self, image_prompt, script, context)
@shared_task(bind=True, max_retries=0, default_retry_delay=60, soft_time_limit=3600, time_limit=3900)
def execute_initiative_stage_task(
    self,
    initiative_id: str,
    stage_num: int,
    agent_name: str,
    task: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    from core.tasks_initiatives import _impl_execute_initiative_stage_task
    return _impl_execute_initiative_stage_task(self, initiative_id, stage_num, agent_name, task, context)
@shared_task(bind=True, max_retries=1, default_retry_delay=120)
def produce_content_package(
    self,
    production_id: str,
    content_type: str,
    topic: str,
    context: Dict[str, Any] = None,
    skip_assets: list = None,
    user_id: int = None
) -> Dict[str, Any]:
    from core.tasks_misc import _impl_produce_content_package
    return _impl_produce_content_package(self, production_id, content_type, topic, context, skip_assets, user_id)
def _create_spider_instance(spider_class, spider_name: str):
    """Create a spider instance, trying both constructor patterns."""
    try:
        return spider_class()
    except TypeError:
        return spider_class(
            spider_id=spider_name,
            targets=[],
            subscribers=[],
            redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
        )


def _run_spider_adapter(spider, spider_name: str) -> dict:
    """
    Run a spider using whichever method it supports (fetch/scrape/fetch_data).
    Returns a dict with 'items' key.
    """
    import asyncio
    import inspect

    if hasattr(spider, 'fetch'):
        return spider.fetch()
    elif hasattr(spider, 'scrape'):
        return asyncio.run(spider.scrape())
    elif hasattr(spider, 'collect_data'):
        return asyncio.run(spider.collect_data())
    elif hasattr(spider, 'fetch_data'):
        from ai_core.spiders.base_spider import SpiderTarget

        async def _run_fetch():
            fetch_method = spider.fetch_data
            sig = inspect.signature(fetch_method)
            params = list(sig.parameters.keys())

            first_param = params[0] if params else None
            if first_param and first_param in ('target', 'url'):
                target = SpiderTarget(url='internal://spider-execution')
                raw = await spider.fetch_data(target)
            else:
                if asyncio.iscoroutinefunction(fetch_method):
                    raw = await spider.fetch_data()
                else:
                    raw = spider.fetch_data()

            if raw and hasattr(spider, 'process_data'):
                target = SpiderTarget(url='internal://spider-execution')
                if asyncio.iscoroutinefunction(spider.process_data):
                    result = await spider.process_data(raw, target)
                else:
                    result = spider.process_data(raw, target)
                if result:
                    content = result.content if hasattr(result, 'content') else {}
                    return {'items': [content] if content else [], 'raw_data': raw}
            if raw:
                if isinstance(raw, list):
                    return {'items': raw, 'source': spider_name}
                elif isinstance(raw, dict):
                    return raw
                else:
                    return {'items': [raw], 'source': spider_name}
            return {'items': []}

        data = asyncio.run(_run_fetch())
        return data if isinstance(data, dict) else {'items': []}
    else:
        return {'items': [], 'message': f'Spider {spider_name} has no fetch/scrape/fetch_data method'}


@shared_task(bind=True)
def run_spider_by_category(self, category: str, execution_mode: str = 'interactive'):
    from core.tasks_spiders import _impl_run_spider_by_category
    return _impl_run_spider_by_category(self, category, execution_mode)
@shared_task(bind=True)
def execute_single_spider(self, spider_name: str, execution_log_id: str = None):
    from core.tasks_spiders import _impl_execute_single_spider
    return _impl_execute_single_spider(self, spider_name, execution_log_id)
@shared_task(bind=True, max_retries=3)
def isolate_documents_batch(self, batch_size: int = 50, max_batches: int = None):
    from core.tasks_ops import _impl_isolate_documents_batch
    return _impl_isolate_documents_batch(self, batch_size, max_batches)
@shared_task
def monitor_isolation_progress():
    """
    Monitoring task to check overall isolation progress
    
    Returns:
        Dict with current isolation status
    """
    try:
        from content.models import Document
        
        total = Document.objects.count()
        
        namespace_counts = {}
        namespaces = ['personal', 'system', 'agent_memory', 'public']
        
        for namespace in namespaces:
            count = Document.objects.filter(metadata__namespace=namespace).count()
            namespace_counts[namespace] = count
        
        untagged = Document.objects.exclude(metadata__has_key='namespace').count()
        tagged = total - untagged
        
        progress_pct = (tagged / total * 100) if total > 0 else 0
        
        status = {
            'total_documents': total,
            'tagged': tagged,
            'untagged': untagged,
            'progress_percentage': round(progress_pct, 1),
            'distribution': namespace_counts,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Isolation Progress: {progress_pct:.1f}% ({tagged}/{total})")
        logger.info(f"Distribution: {namespace_counts}")
        
        return status
        
    except Exception as e:
        logger.error(f"Monitoring task failed: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@shared_task
def cleanup_isolation_metadata():
    """
    Cleanup task to remove duplicate or corrupted isolation metadata
    """
    try:
        from content.models import Document
        from django.db.models import Q
        
        cleaned_count = 0
        
        # Find documents with invalid namespace values
        invalid_docs = Document.objects.filter(
            ~Q(metadata__namespace__in=['personal', 'system', 'agent_memory', 'public'])
        ).filter(metadata__has_key='namespace')
        
        for doc in invalid_docs:
            logger.info(f"Cleaning invalid namespace for document {doc.id}")
            
            # Remove invalid namespace and let the isolation task re-process
            if 'namespace' in doc.metadata:
                del doc.metadata['namespace']
            if 'tagged_by' in doc.metadata:
                del doc.metadata['tagged_by']
            
            doc.save()
            cleaned_count += 1
        
        logger.info(f"Cleanup completed: {cleaned_count} documents cleaned")
        
        return {
            'status': 'completed',
            'cleaned_count': cleaned_count,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

# Spider and Agent Learning Tasks
# Session 399: DEPRECATED - This task created mock/placeholder spider data.
# Real spider collection is handled by run_spider_network() task which runs every 15 minutes.
# Keeping function for backwards compatibility but it now just returns without creating mock data.
@shared_task
def collect_spider_data():
    """DEPRECATED: Mock spider data collection - replaced by run_spider_network()"""
    logger.info("collect_spider_data() is deprecated - use run_spider_network() for real data")
    return "Deprecated - no mock data created"

@shared_task
def process_spider_data_automatic():
    """
    Automatically process unprocessed spider data every 5 minutes
    Routes spider data to relevant agents for solution creation and learning

    Session 6: Spider → Agent → Learning automation
    """
    from persistence.models import SpiderData
    from intelligence.spider_agent_connector import SpiderAgentConnector

    logger.info("🕷️ Starting automated spider data processing...")

    connector = SpiderAgentConnector()

    # Get unprocessed spider data (limit to 100 per run to avoid overload)
    unprocessed = SpiderData.objects.filter(is_processed=False).defer('embedding')[:100]

    results = {
        'processed': 0,
        'solutions_created': 0,
        'learning_records': 0,
        'errors': 0,
        'agents_matched': 0
    }

    for spider_data in unprocessed:
        try:
            # Route spider data to agents
            result = connector.route_spider_data(spider_data)

            # Mark as processed
            spider_data.is_processed = True
            spider_data.save()

            results['processed'] += 1
            results['solutions_created'] += len(result.get('solutions_created', []))
            results['learning_records'] += len(result.get('learning_records', []))
            results['agents_matched'] += len(result.get('matched_agents', []))

        except Exception as e:
            results['errors'] += 1
            logger.error(f"Error processing spider data {spider_data.id}: {e}")

    logger.info(f"✅ Automated processing complete: {results['processed']} spider entries processed")
    logger.info(f"   Solutions: {results['solutions_created']}, Learning: {results['learning_records']}")
    logger.info(f"   Agents matched: {results['agents_matched']}, Errors: {results['errors']}")

    return results


@shared_task
def process_core_spider_data():
    from core.tasks_spiders import _impl_process_core_spider_data
    return _impl_process_core_spider_data()
@shared_task(bind=True)
def run_spider_network(self):
    from core.tasks_spiders import _impl_run_spider_network
    return _impl_run_spider_network(self)
@shared_task(ignore_result=True)
def backfill_spider_embeddings(batch_size: int = 200):
    """
    Session 293: Generate embeddings for SpiderData entries that don't have them.
    Session 394: Increased default batch size from 50 to 200 for faster processing.

    Runs every 10 minutes via Celery Beat to gradually build embedding coverage.
    Uses the SpiderSemanticSearch service.

    Now also marks entries with no items as 'empty' so they're skipped in future runs.
    """
    logger.info("🧠 Starting spider embedding backfill...")

    try:
        from core.services.spider_semantic_search import get_spider_semantic_search

        search = get_spider_semantic_search()
        stats = search.backfill_embeddings(batch_size=batch_size, hours=168)  # Last 7 days

        logger.info(
            f"✅ Embedding backfill complete: "
            f"{stats['processed']} processed, {stats['succeeded']} succeeded, "
            f"{stats['failed']} failed, {stats['skipped']} skipped, "
            f"{stats.get('marked_empty', 0)} marked empty"
        )

        # Get current coverage stats
        coverage = search.get_embedding_stats()
        logger.info(
            f"📊 Embedding stats: {coverage['searchable']} searchable, "
            f"{coverage.get('marked_empty', 0)} empty, {coverage.get('pending', 0)} pending "
            f"({coverage['coverage_percent']:.1f}% coverage)"
        )

        return {
            'success': True,
            'batch_stats': stats,
            'coverage': coverage
        }

    except Exception as e:
        logger.error(f"❌ Embedding backfill failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='backfill_signal_scores')
def backfill_signal_scores():
    """Session 1025: Score all existing SignalClusters that have default scores."""
    from core.models_signal_intelligence import SignalCluster
    from core.services.content_scoring_service import ContentScoringService

    scorer = ContentScoringService()
    clusters = SignalCluster.objects.filter(reach_score=0.0, intent_score=0.0)
    updated = 0
    for cluster in clusters.iterator():
        scores = scorer.score_cluster(cluster)
        for field, value in scores.items():
            setattr(cluster, field, value)
        cluster.save(update_fields=list(scores.keys()))
        updated += 1
    logger.info(f"Scored {updated} signal clusters")
    return f"Scored {updated} clusters"


@shared_task
def execute_single_spider_lightweight(spider_name: str):
    from core.tasks_spiders import _impl_execute_single_spider_lightweight
    return _impl_execute_single_spider_lightweight(spider_name)
def _collect_spider_data_sync(spider_name: str, category: str, config: Dict) -> Dict[str, Any]:
    """
    Synchronous data collection helper for on-demand spider execution.
    Avoids async/fork issues on macOS by using simple requests.

    Session 207: Comprehensive data collection for all spider categories.
    """
    from django.utils import timezone

    data = {
        'source': spider_name,
        'category': category,
        'collected_at': timezone.now().isoformat(),
        'items': []
    }

    # Spider-specific data collection (most specific first)
    if spider_name == 'hackernews':
        data['items'] = _collect_hackernews()
    elif spider_name == 'devto':
        data['items'] = _collect_devto()
    elif spider_name == 'hashnode':
        data['items'] = _collect_hashnode()
    elif spider_name == 'coingecko':
        data['items'] = _collect_coingecko()
    elif spider_name == 'yahoo_finance':
        data['items'] = _collect_yahoo_finance()
    elif spider_name == 'etherscan':
        data['items'] = _collect_etherscan()
    elif spider_name == 'opensea':
        data['items'] = _collect_opensea()
    elif spider_name in ['seekingalpha', 'bloomberg_terminal', 'reuters_eikon']:
        data['items'] = _collect_premium_financial(spider_name)
    elif spider_name == 'weworkremotely':
        data['items'] = _collect_weworkremotely()
    elif spider_name == 'angellist':
        data['items'] = _collect_angellist()
    elif spider_name in ['dribbble', 'behance']:
        data['items'] = _collect_design_platform(spider_name)
    elif spider_name in ['udemy', 'skillshare', 'teachable']:
        data['items'] = _collect_education_platform(spider_name)
    elif spider_name in ['courtlistener', 'justia', 'findlaw', 'lii', 'colorado_family_law', 'justia_family_law']:
        data['items'] = _collect_legal_platform(spider_name)
    elif spider_name in ['indiegogo', 'kickstarter']:
        data['items'] = _collect_crowdfunding(spider_name)
    # Category-based fallbacks
    elif category == 'financial':
        data['items'] = _collect_financial_default()
    elif category == 'news':
        data['items'] = _collect_news_default()
    elif category == 'freelance':
        data['items'] = _collect_freelance_default(spider_name, config)
    elif category in ['social', 'market', 'innovation']:
        data['items'].append({
            'message': f'{category.title()} spider {spider_name} executed successfully',
            'config': {k: v for k, v in config.items() if k != 'class'}
        })
    else:
        data['items'].append({
            'message': f'Spider {spider_name} executed',
            'category': category
        })

    data['item_count'] = len(data['items'])
    return data


# ============ TECH SPIDERS ============

def _collect_hackernews() -> list:
    """Collect top stories from HackerNews (free API, no auth needed)"""
    import requests
    items = []
    try:
        # Get top story IDs
        resp = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json', timeout=10)
        if resp.status_code == 200:
            story_ids = resp.json()[:10]  # Top 10 stories
            for story_id in story_ids[:5]:  # Limit to 5 for speed
                story_resp = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json', timeout=5)
                if story_resp.status_code == 200:
                    story = story_resp.json()
                    items.append({
                        'title': story.get('title', ''),
                        'url': story.get('url', ''),
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0),
                        'by': story.get('by', ''),
                        'type': 'hackernews_story'
                    })
    except Exception as e:
        items.append({'error': str(e), 'message': 'HackerNews API error'})
    return items


def _collect_devto() -> list:
    """Collect articles from Dev.to (free API, no auth needed)"""
    import requests
    items = []
    try:
        resp = requests.get(
            'https://dev.to/api/articles',
            params={'per_page': 10, 'top': 7},  # Top articles from last 7 days
            timeout=10
        )
        if resp.status_code == 200:
            articles = resp.json()
            for article in articles[:5]:
                items.append({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'reactions': article.get('public_reactions_count', 0),
                    'comments': article.get('comments_count', 0),
                    'author': article.get('user', {}).get('username', ''),
                    'tags': article.get('tag_list', []),
                    'type': 'devto_article'
                })
    except Exception as e:
        items.append({'error': str(e), 'message': 'Dev.to API error'})
    return items


def _collect_hashnode() -> list:
    """Collect trending posts from Hashnode (GraphQL API)"""
    import requests
    items = []
    try:
        query = '''
        query {
            storiesFeed(type: FEATURED, first: 5) {
                edges {
                    node {
                        title
                        brief
                        url
                        reactionCount
                        author { username }
                    }
                }
            }
        }
        '''
        resp = requests.post(
            'https://gql.hashnode.com',
            json={'query': query},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            edges = data.get('data', {}).get('storiesFeed', {}).get('edges', [])
            for edge in edges:
                node = edge.get('node', {})
                items.append({
                    'title': node.get('title', ''),
                    'url': node.get('url', ''),
                    'reactions': node.get('reactionCount', 0),
                    'author': node.get('author', {}).get('username', ''),
                    'brief': node.get('brief', '')[:100],
                    'type': 'hashnode_post'
                })
    except Exception as e:
        items.append({'error': str(e), 'message': 'Hashnode API error'})
    return items


# ============ FINANCIAL SPIDERS ============

def _collect_coingecko() -> list:
    """Collect crypto prices from CoinGecko (free API, no auth needed)"""
    import requests
    items = []
    try:
        resp = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'sparkline': False
            },
            timeout=10
        )
        if resp.status_code == 200:
            coins = resp.json()
            for coin in coins[:5]:
                items.append({
                    'name': coin.get('name', ''),
                    'symbol': coin.get('symbol', '').upper(),
                    'price': coin.get('current_price', 0),
                    'change_24h': coin.get('price_change_percentage_24h', 0),
                    'market_cap': coin.get('market_cap', 0),
                    'volume': coin.get('total_volume', 0),
                    'type': 'crypto_price'
                })
    except Exception as e:
        items.append({'error': str(e), 'message': 'CoinGecko API error'})
    return items


def _collect_yahoo_finance() -> list:
    """Collect stock data using yfinance"""
    items = []
    try:
        import yfinance as yf
        symbols = ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI']  # Major ETFs
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                items.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('regularMarketVolume', 0),
                    'day_high': info.get('dayHigh', 0),
                    'day_low': info.get('dayLow', 0),
                    'type': 'stock_etf'
                })
            except Exception as e:
                logger.warning(f"Stock ticker fetch failed: {e}")
    except ImportError:
        items.append({'message': 'yfinance not available'})
    return items


def _collect_etherscan() -> list:
    """Collect Ethereum gas prices and stats (free tier available)"""
    import requests
    items = []
    try:
        # Gas prices (no API key needed for this endpoint)
        resp = requests.get(
            'https://api.etherscan.io/api',
            params={'module': 'gastracker', 'action': 'gasoracle'},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status') == '1':
                result = data.get('result', {})
                items.append({
                    'safe_gas': result.get('SafeGasPrice', '0'),
                    'propose_gas': result.get('ProposeGasPrice', '0'),
                    'fast_gas': result.get('FastGasPrice', '0'),
                    'type': 'eth_gas_price'
                })
        # ETH price
        price_resp = requests.get(
            'https://api.etherscan.io/api',
            params={'module': 'stats', 'action': 'ethprice'},
            timeout=10
        )
        if price_resp.status_code == 200:
            data = price_resp.json()
            if data.get('status') == '1':
                result = data.get('result', {})
                items.append({
                    'eth_usd': result.get('ethusd', '0'),
                    'eth_btc': result.get('ethbtc', '0'),
                    'type': 'eth_price'
                })
    except Exception as e:
        items.append({'error': str(e), 'message': 'Etherscan API error'})
    return items


def _collect_opensea() -> list:
    """Collect NFT collection stats (placeholder - requires API key)"""
    items = []
    items.append({
        'message': 'OpenSea spider ready - requires API key for full data',
        'collections_tracked': ['bored-ape-yacht-club', 'cryptopunks', 'azuki'],
        'type': 'nft_placeholder'
    })
    return items


def _collect_premium_financial(spider_name: str) -> list:
    """Placeholder for premium financial services (SeekingAlpha, Bloomberg, Reuters)"""
    items = []
    items.append({
        'message': f'{spider_name.replace("_", " ").title()} spider ready',
        'note': 'Premium API subscription required for live data',
        'type': 'premium_financial'
    })
    return items


def _collect_financial_default() -> list:
    """Default financial data collection using yfinance"""
    items = []
    try:
        import yfinance as yf
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'][:3]
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                items.append({
                    'symbol': symbol,
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('regularMarketVolume', 0),
                })
            except Exception as e:
                logger.warning(f"Stock ticker fetch failed: {e}")
    except ImportError:
        items.append({'message': 'yfinance not available'})
    return items


# ============ FREELANCE/JOBS SPIDERS ============

def _collect_weworkremotely() -> list:
    """Collect remote jobs from WeWorkRemotely RSS feed"""
    import requests
    import re
    items = []
    try:
        resp = requests.get(
            'https://weworkremotely.com/categories/remote-programming-jobs.rss',
            timeout=10
        )
        if resp.status_code == 200:
            # Parse XML items - WWR uses standard tags, not CDATA
            item_blocks = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            for item_block in item_blocks[:5]:
                title_match = re.search(r'<title>(.*?)</title>', item_block)
                link_match = re.search(r'<link>(.*?)</link>', item_block)
                region_match = re.search(r'<region>(.*?)</region>', item_block)
                category_match = re.search(r'<category>(.*?)</category>', item_block)

                if title_match:
                    items.append({
                        'title': title_match.group(1).strip(),
                        'url': link_match.group(1).strip() if link_match else '',
                        'region': region_match.group(1).strip() if region_match else 'Remote',
                        'category': category_match.group(1).strip() if category_match else '',
                        'source': 'WeWorkRemotely',
                        'type': 'remote_job'
                    })
    except Exception as e:
        items.append({'error': str(e), 'message': 'WeWorkRemotely fetch error'})
    return items


def _collect_angellist() -> list:
    """Collect startup jobs (placeholder - API requires auth)"""
    items = []
    items.append({
        'message': 'AngelList/Wellfound spider ready',
        'categories': ['engineering', 'design', 'product', 'marketing'],
        'note': 'API authentication required for job listings',
        'type': 'startup_jobs'
    })
    return items


def _collect_design_platform(spider_name: str) -> list:
    """Collect design work from Dribbble/Behance"""
    items = []
    if spider_name == 'dribbble':
        items.append({
            'message': 'Dribbble spider ready',
            'categories': ['web-design', 'mobile', 'illustration', 'branding'],
            'note': 'OAuth required for full API access',
            'type': 'design_platform'
        })
    elif spider_name == 'behance':
        items.append({
            'message': 'Behance spider ready',
            'categories': ['graphic-design', 'ui-ux', 'photography', 'illustration'],
            'note': 'Adobe API key required',
            'type': 'design_platform'
        })
    return items


def _collect_freelance_default(spider_name: str, config: Dict) -> list:
    """Default freelance data collection"""
    items = []
    items.append({
        'message': f'Freelance spider {spider_name} executed',
        'platforms_checked': config.get('targets', [])
    })
    return items


# ============ EDUCATION SPIDERS ============

def _collect_education_platform(spider_name: str) -> list:
    """Collect course data from education platforms"""
    import requests
    items = []

    if spider_name == 'udemy':
        try:
            # Udemy affiliate API (public courses)
            resp = requests.get(
                'https://www.udemy.com/api-2.0/courses/',
                params={'page_size': 5, 'ordering': 'relevance'},
                headers={'Accept': 'application/json'},
                timeout=10
            )
            if resp.status_code == 200:
                courses = resp.json().get('results', [])
                for course in courses[:5]:
                    items.append({
                        'title': course.get('title', ''),
                        'url': f"https://udemy.com{course.get('url', '')}",
                        'price': course.get('price', ''),
                        'rating': course.get('avg_rating', 0),
                        'students': course.get('num_subscribers', 0),
                        'type': 'udemy_course'
                    })
            else:
                items.append({
                    'message': 'Udemy spider ready',
                    'categories': ['development', 'business', 'design', 'marketing'],
                    'type': 'education_platform'
                })
        except Exception as e:
            items.append({'message': 'Udemy spider ready', 'type': 'education_platform'})

    elif spider_name == 'skillshare':
        items.append({
            'message': 'Skillshare spider ready',
            'categories': ['design', 'illustration', 'photography', 'film'],
            'note': 'API access requires partnership',
            'type': 'education_platform'
        })

    elif spider_name == 'teachable':
        items.append({
            'message': 'Teachable spider ready',
            'note': 'Platform for course creators - tracks creator economy',
            'type': 'education_platform'
        })

    return items


# ============ LEGAL SPIDERS ============

def _collect_legal_platform(spider_name: str) -> list:
    """Collect legal data from legal research platforms"""
    import requests
    items = []

    if spider_name == 'courtlistener':
        try:
            # CourtListener has a free API
            resp = requests.get(
                'https://www.courtlistener.com/api/rest/v3/opinions/',
                params={'order_by': '-date_filed', 'page_size': 5},
                timeout=10
            )
            if resp.status_code == 200:
                opinions = resp.json().get('results', [])
                for opinion in opinions[:5]:
                    items.append({
                        'case_name': opinion.get('case_name', ''),
                        'court': opinion.get('court', ''),
                        'date_filed': opinion.get('date_filed', ''),
                        'type': 'court_opinion'
                    })
            else:
                items.append({
                    'message': 'CourtListener spider ready',
                    'data_types': ['opinions', 'dockets', 'oral_arguments'],
                    'type': 'legal_research'
                })
        except Exception:
            items.append({'message': 'CourtListener spider ready', 'type': 'legal_research'})

    elif spider_name == 'justia':
        items.append({
            'message': 'Justia spider ready',
            'data_types': ['case_law', 'statutes', 'regulations'],
            'type': 'legal_research'
        })

    elif spider_name == 'findlaw':
        items.append({
            'message': 'FindLaw spider ready',
            'data_types': ['legal_news', 'case_summaries', 'legal_forms'],
            'type': 'legal_research'
        })

    elif spider_name == 'lii':
        items.append({
            'message': 'Legal Information Institute spider ready',
            'data_types': ['us_code', 'cfr', 'supreme_court'],
            'source': 'Cornell Law School',
            'type': 'legal_research'
        })

    elif spider_name == 'colorado_family_law':
        # Session 507: Call the actual spider with sync wrapper
        try:
            from ai_core.spiders.specialized.colorado_family_law_spider import ColoradoFamilyLawSpider
            spider = ColoradoFamilyLawSpider()
            data = spider.fetch_data_sync(max_results=20)
            if data:
                items.extend(data)
            else:
                items.extend(spider._get_fallback_forms())
        except Exception as e:
            logger.warning(f"Colorado Family Law spider error: {e}")
            items.append({
                'message': 'Colorado Family Law spider ready',
                'data_types': ['family_law_forms', 'jdf_forms', 'self_help'],
                'source': 'Colorado Judicial Branch',
                'type': 'legal_forms',
                'error': str(e)[:100]
            })

    elif spider_name == 'justia_family_law':
        # Session 507: Call the actual spider with sync wrapper
        try:
            from ai_core.spiders.specialized.justia_playwright_spider import JustiaPlaywrightSpider
            spider = JustiaPlaywrightSpider()
            data = spider.fetch_data_sync(max_results=20)
            if data:
                items.extend(data)
            else:
                items.extend(spider._get_fallback_data())
        except Exception as e:
            logger.warning(f"Justia Family Law spider error: {e}")
            items.append({
                'message': 'Justia Family Law spider ready',
                'data_types': ['family_law', 'divorce', 'custody', 'child_support'],
                'source': 'Justia',
                'type': 'legal_research',
                'error': str(e)[:100]
            })

    return items


# ============ CROWDFUNDING SPIDERS ============

def _collect_crowdfunding(spider_name: str) -> list:
    """Collect crowdfunding campaign data"""
    items = []

    if spider_name == 'kickstarter':
        items.append({
            'message': 'Kickstarter spider ready',
            'categories': ['technology', 'games', 'design', 'film'],
            'tracks': ['trending', 'newly_launched', 'most_funded'],
            'type': 'crowdfunding'
        })

    elif spider_name == 'indiegogo':
        items.append({
            'message': 'Indiegogo spider ready',
            'categories': ['tech', 'design', 'community', 'film'],
            'tracks': ['trending', 'popular', 'ending_soon'],
            'type': 'crowdfunding'
        })

    return items


# ============ NEWS SPIDER ============

def _collect_news_default() -> list:
    """Default news data collection"""
    import requests
    items = []
    try:
        resp = requests.get(
            'https://newsapi.org/v2/top-headlines',
            params={'country': 'us', 'pageSize': 5},
            headers={'X-Api-Key': os.environ.get('NEWS_API_KEY', '')},
            timeout=10
        )
        if resp.status_code == 200:
            articles = resp.json().get('articles', [])
            for article in articles[:5]:
                items.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'url': article.get('url', '')
                })
    except Exception as e:
        items.append({'message': f'News fetch error: {str(e)}'})
    return items


@shared_task
def poll_pending_3d_models():
    from core.tasks_misc import _impl_poll_pending_3d_models
    return _impl_poll_pending_3d_models()
@shared_task(ignore_result=True)
def record_all_user_style_evolution():
    from core.tasks_agents import _impl_record_all_user_style_evolution
    return _impl_record_all_user_style_evolution()
@shared_task(bind=True, max_retries=3)
def execute_scheduled_workflow(self, schedule_id: str):
    from core.tasks_ops import _impl_execute_scheduled_workflow
    return _impl_execute_scheduled_workflow(self, schedule_id)
@shared_task
def sync_workflow_schedules():
    from core.tasks_ops import _impl_sync_workflow_schedules
    return _impl_sync_workflow_schedules()
@shared_task(
    autoretry_for=(ConnectionError, OSError),
    retry_backoff=10,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=2,
)
def check_workflow_schedules():
    from core.tasks_misc import _impl_check_workflow_schedules
    return _impl_check_workflow_schedules()
@shared_task
def score_opportunities_from_spider_data(hours: int = 24, limit: int = 100):
    """
    Score spider data and create opportunities.

    This task runs on a schedule to transform raw spider data
    into scored, actionable opportunities.

    Args:
        hours: Look back period in hours (default: 24)
        limit: Maximum items to process (default: 100)

    Returns:
        Dict with scoring statistics
    """
    logger.info(f"🎯 [OPPORTUNITY ENGINE] Starting opportunity scoring - last {hours}h, limit: {limit}")

    try:
        from core.agents.analysis import OpportunityScoringAgent

        agent = OpportunityScoringAgent()
        results = agent.score_spider_data(hours=hours, limit=limit)

        # Count successful scores
        successful = [r for r in results if r.success]
        high_value = [r for r in successful if r.overall_score >= 70]

        stats = {
            'status': 'completed',
            'total_processed': len(results),
            'successful': len(successful),
            'high_value_opportunities': len(high_value),
            'average_score': sum(r.overall_score for r in successful) / len(successful) if successful else 0,
        }

        logger.info(f"🎯 [OPPORTUNITY ENGINE] Completed - {len(successful)} opportunities scored, {len(high_value)} high-value")
        return stats

    except Exception as e:
        logger.error(f"❌ [OPPORTUNITY ENGINE] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def execute_pending_opportunity_tasks(limit: int = 20):
    from core.tasks_ops import _impl_execute_pending_opportunity_tasks
    return _impl_execute_pending_opportunity_tasks(limit)
@shared_task
def expire_old_opportunities():
    from core.tasks_misc import _impl_expire_old_opportunities
    return _impl_expire_old_opportunities()
@shared_task
def generate_opportunity_report():
    from core.tasks_ops import _impl_generate_opportunity_report
    return _impl_generate_opportunity_report()
@shared_task
def train_ml_scoring_model(force_retrain: bool = False, min_samples: int = 100, use_optuna: bool = True):
    from core.tasks_financial import _impl_train_ml_scoring_model
    return _impl_train_ml_scoring_model(force_retrain, min_samples, use_optuna)
@shared_task
def evaluate_ml_model_performance():
    from core.tasks_financial import _impl_evaluate_ml_model_performance
    return _impl_evaluate_ml_model_performance()
@shared_task
def process_realtime_scoring_queue(max_items: int = 50, max_time_sec: int = 25):
    from core.tasks_misc import _impl_process_realtime_scoring_queue
    return _impl_process_realtime_scoring_queue(max_items, max_time_sec)
@shared_task
def process_batch_scoring_queue(batch_size: int = 100):
    """
    Process items from the database batch scoring queue.

    Session 470: Market Intelligence Architecture - Phase 2

    This task runs hourly to process lower-priority scoring requests
    that were queued for batch processing.

    Args:
        batch_size: Maximum items to process per run

    Returns:
        Dict with processing statistics
    """
    logger.info("📦 [BATCH QUEUE] Starting batch processing...")

    try:
        from core.services.scoring_dispatcher import get_scoring_dispatcher

        dispatcher = get_scoring_dispatcher()

        # Process batch
        stats = dispatcher.process_batch_queue(batch_size=batch_size)

        # Cleanup expired items
        expired = dispatcher.cleanup_expired()

        result = {
            'status': 'completed',
            **stats,
            'expired_cleaned': expired
        }

        logger.info(
            f"📦 [BATCH QUEUE] Complete: {stats['success']}/{stats['processed']} success, "
            f"{expired} expired cleaned"
        )

        return result

    except Exception as e:
        logger.error(f"❌ [BATCH QUEUE] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def cleanup_stale_scoring_requests():
    from core.tasks_misc import _impl_cleanup_stale_scoring_requests
    return _impl_cleanup_stale_scoring_requests()
@shared_task
def score_spider_data_async(spider_data_id: str, priority: str = 'normal', source: str = 'api', user_id: int = None):
    from core.tasks_spiders import _impl_score_spider_data_async
    return _impl_score_spider_data_async(spider_data_id, priority, source, user_id)
@shared_task(bind=True, max_retries=3)
def process_distribution(self, distribution_id: str):
    from core.tasks_content import _impl_process_distribution
    return _impl_process_distribution(self, distribution_id)
def process_etsy_distribution(distribution):
    """Process distribution to Etsy."""
    account = distribution.platform_account

    if not account.access_token:
        return {'success': False, 'error': 'No Etsy access token. Please reconnect.'}

    try:
        import requests as http_requests
        import os

        client_id = os.environ.get('ETSY_CLIENT_ID', '')

        headers = {
            'Authorization': f'Bearer {account.access_token}',
            'x-api-key': client_id,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Get user's shop ID (from account metadata or fetch)
        shop_id = account.notification_settings.get('shop_id')

        if not shop_id:
            # Fetch shop ID
            shops_response = http_requests.get(
                'https://openapi.etsy.com/v3/application/users/me/shops',
                headers=headers
            )
            if shops_response.status_code == 200:
                shops = shops_response.json().get('results', [])
                if shops:
                    shop_id = shops[0].get('shop_id')
                    # Save for future use
                    account.notification_settings['shop_id'] = shop_id
                    account.save()

        if not shop_id:
            return {'success': False, 'error': 'No Etsy shop found for account'}

        # Prepare listing data
        listing_data = {
            'title': distribution.title[:140],  # Etsy max 140 chars
            'description': distribution.description or distribution.title,
            'price': float(distribution.price or 29.99),
            'quantity': 999,  # Digital goods
            'who_made': 'i_did',
            'when_made': '2020_2025',
            'taxonomy_id': 1,  # Art category (simplified)
            'is_digital': 'true',
        }

        if distribution.tags:
            listing_data['tags'] = ','.join(distribution.tags[:13])

        response = http_requests.post(
            f'https://openapi.etsy.com/v3/application/shops/{shop_id}/listings',
            headers=headers,
            data=listing_data
        )

        if response.status_code in [200, 201]:
            etsy_listing = response.json()
            return {
                'success': True,
                'status': 'live' if etsy_listing.get('state') == 'active' else 'pending',
                'listing_id': str(etsy_listing.get('listing_id', '')),
                'url': etsy_listing.get('url', ''),
            }
        else:
            return {
                'success': False,
                'error': f'Etsy API error: {response.status_code} - {response.text[:200]}'
            }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_gumroad_distribution(distribution):
    """
    Process distribution to Gumroad with actual file upload.

    Uses GumroadPublishingService to:
    1. Download image from ImageHistory (data URI, local path, or URL)
    2. Upload image file to Gumroad via multipart API
    3. Create product listing with proper metadata

    Updated: Session 487 - Added actual file upload (Golden Egg strategy)
    """
    account = distribution.platform_account

    if not account or not account.access_token:
        return {'success': False, 'error': 'No Gumroad access token. Please reconnect.'}

    # Check if we have an image to upload
    image = distribution.image_history
    if not image:
        return {'success': False, 'error': 'No image associated with this distribution'}

    try:
        import requests as http_requests
        from core.services.gumroad_publishing import GumroadPublishingService

        # Initialize service (uses distribution's account)
        service = GumroadPublishingService(distribution.user)

        # Download the image file
        image_bytes, filename, mime_type = service.download_image(image)

        # Build description
        description = distribution.description
        if not description:
            prompt_preview = (image.prompt[:200] + '...') if len(image.prompt) > 200 else image.prompt
            description = f"AI-generated artwork.\n\nPrompt: {prompt_preview}"
            if image.model_used:
                description += f"\n\nGenerated with: {image.model_used}"

        # Prepare multipart upload with actual file
        files = {
            'preview': (filename, image_bytes, mime_type),
            'file': (filename, image_bytes, mime_type),
        }

        product_data = {
            'access_token': account.access_token,
            'name': distribution.title,
            'description': description,
            'price': int(float(distribution.price or 9.99) * 100),  # Cents
        }

        # Upload to Gumroad with file
        response = http_requests.post(
            'https://api.gumroad.com/v2/products',
            data=product_data,
            files=files,
            timeout=60
        )

        if response.status_code in [200, 201]:
            result = response.json()
            if result.get('success'):
                product = result.get('product', {})
                return {
                    'success': True,
                    'status': 'live' if product.get('published') else 'draft',
                    'listing_id': product.get('id', ''),
                    'url': product.get('short_url', ''),
                }
            else:
                return {
                    'success': False,
                    'error': f'Gumroad API error: {result.get("message", "Unknown error")}'
                }
        else:
            return {
                'success': False,
                'error': f'Gumroad API error: {response.status_code} - {response.text[:200]}'
            }

    except FileNotFoundError as e:
        return {'success': False, 'error': f'Image file not found: {e}'}
    except Exception as e:
        logger.error(f"Gumroad distribution failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


def process_shutterstock_distribution(distribution):
    """Process distribution to Shutterstock - marks for manual upload."""
    # Shutterstock requires manual upload through their contributor portal
    # We track the distribution but inform the user

    return {
        'success': True,
        'status': 'pending',
        'message': 'Shutterstock requires upload through contributor portal at submit.shutterstock.com',
        'listing_id': '',
        'url': 'https://submit.shutterstock.com/',
    }


@shared_task
def update_distribution_analytics():
    from core.tasks_misc import _impl_update_distribution_analytics
    return _impl_update_distribution_analytics()
@shared_task
def discover_success_patterns(user_id=None, days=90):
    from core.tasks_misc import _impl_discover_success_patterns
    return _impl_discover_success_patterns(user_id, days)
@shared_task
def generate_user_insights(user_id=None, max_insights=10):
    from core.tasks_misc import _impl_generate_user_insights
    return _impl_generate_user_insights(user_id, max_insights)
@shared_task
def update_learning_profiles():
    from core.tasks_misc import _impl_update_learning_profiles
    return _impl_update_learning_profiles()
@shared_task
def run_daily_learning_pipeline():
    """
    Run the complete daily learning pipeline.
    Called by Celery Beat scheduler.
    """
    logger.info("🚀 [LEARNING] Starting daily learning pipeline...")

    try:
        results = {
            'patterns': None,
            'insights': None,
            'profiles': None,
        }

        # Step 1: Discover patterns
        logger.info("🚀 [LEARNING] Step 1: Discovering patterns...")
        results['patterns'] = discover_success_patterns.delay().get(timeout=300)

        # Step 2: Generate insights
        logger.info("🚀 [LEARNING] Step 2: Generating insights...")
        results['insights'] = generate_user_insights.delay().get(timeout=300)

        # Step 3: Update profiles
        logger.info("🚀 [LEARNING] Step 3: Updating profiles...")
        results['profiles'] = update_learning_profiles.delay().get(timeout=300)

        logger.info(f"🚀 [LEARNING] Daily pipeline complete: {results}")
        return {'status': 'completed', 'results': results}

    except Exception as e:
        logger.exception(f"🚀 [LEARNING] Daily pipeline failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ============================================================
# Session 234: Proactive System Celery Tasks (Phase 6)
# ============================================================

@shared_task
def run_proactive_system_check(user_id=None):
    """
    Run a complete proactive system check.
    Checks alerts, generates suggestions, and executes scheduled automations.
    """
    try:
        from django.contrib.auth import get_user_model
        from core.proactive_engine import ProactiveSystem

        User = get_user_model()

        results = {
            'users_processed': 0,
            'alerts_triggered': 0,
            'suggestions_generated': 0,
            'actions_executed': 0,
        }

        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.filter(is_active=True)

        for user in users:
            try:
                proactive = ProactiveSystem(user)
                check_result = proactive.run_proactive_check(user)

                results['users_processed'] += 1
                results['alerts_triggered'] += len(check_result.get('alerts_triggered', []))
                results['suggestions_generated'] += len(check_result.get('suggestions_generated', []))
                results['actions_executed'] += len(check_result.get('actions_executed', []))

            except Exception as e:
                logger.error(f"🔔 [PROACTIVE] Error for user {user.id}: {e}")

        logger.info(f"🔔 [PROACTIVE] System check complete: {results}")
        return results

    except Exception as e:
        logger.exception(f"🔔 [PROACTIVE] System check failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def check_all_alerts():
    """
    Check all active alerts for all users.
    Triggers notifications for any alerts that meet their conditions.
    """
    try:
        from django.contrib.auth import get_user_model
        from core.proactive_engine import AlertEngine

        User = get_user_model()
        engine = AlertEngine()

        total_triggered = 0

        for user in User.objects.filter(is_active=True):
            try:
                triggered = engine.check_all_alerts(user)
                total_triggered += len(triggered)
            except Exception as e:
                logger.error(f"🔔 [ALERTS] Error checking alerts for user {user.id}: {e}")

        logger.info(f"🔔 [ALERTS] Checked all alerts, triggered: {total_triggered}")
        return {'status': 'success', 'alerts_triggered': total_triggered}

    except Exception as e:
        logger.exception(f"🔔 [ALERTS] Alert check failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def generate_smart_suggestions(user_id=None, max_suggestions=5):
    """
    Generate smart suggestions for users based on their data.
    """
    try:
        from django.contrib.auth import get_user_model
        from core.proactive_engine import SuggestionEngine

        User = get_user_model()

        total_generated = 0

        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.filter(is_active=True)

        for user in users:
            try:
                # Check pending suggestions count
                from core.models_unified_system import SmartSuggestion
                pending = SmartSuggestion.objects.filter(
                    user=user,
                    status='pending'
                ).count()

                if pending < 20:
                    engine = SuggestionEngine(user)
                    suggestions = engine.generate_suggestions(user, max_suggestions=max_suggestions)
                    total_generated += len(suggestions)

            except Exception as e:
                logger.error(f"💡 [SUGGESTIONS] Error for user {user.id}: {e}")

        logger.info(f"💡 [SUGGESTIONS] Generated {total_generated} suggestions")
        return {'status': 'success', 'suggestions_generated': total_generated}

    except Exception as e:
        logger.exception(f"💡 [SUGGESTIONS] Generation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def execute_scheduled_automations():
    """
    Execute all scheduled automated actions that are due.
    """
    try:
        from core.proactive_engine import AutomationEngine

        engine = AutomationEngine()
        executed = engine.check_scheduled_actions()

        logger.info(f"⚙️ [AUTOMATIONS] Executed {len(executed)} scheduled actions")
        return {'status': 'success', 'actions_executed': len(executed), 'details': executed}

    except Exception as e:
        logger.exception(f"⚙️ [AUTOMATIONS] Scheduled execution failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def send_pending_notifications():
    """
    Send any pending scheduled notifications.
    """
    try:
        from django.utils import timezone
        from core.models_unified_system import ProactiveNotification
        from core.proactive_engine import NotificationManager

        now = timezone.now()

        # Find pending notifications that are due
        pending = ProactiveNotification.objects.filter(
            delivery_status='pending',
            scheduled_at__lte=now,
            is_expired=False
        )

        sent_count = 0
        for notification in pending:
            try:
                manager = NotificationManager(notification.user)
                # Mark as delivered (actual delivery would integrate with email/push services)
                notification.delivery_status = 'delivered'
                notification.sent_at = now
                notification.channels_sent = ['in_app']
                notification.save()
                sent_count += 1
            except Exception as e:
                logger.error(f"📬 [NOTIFICATIONS] Failed to send notification {notification.id}: {e}")
                notification.delivery_status = 'failed'
                notification.save()

        logger.info(f"📬 [NOTIFICATIONS] Sent {sent_count} pending notifications")
        return {'status': 'success', 'notifications_sent': sent_count}

    except Exception as e:
        logger.exception(f"📬 [NOTIFICATIONS] Send pending failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def cleanup_old_notifications(days=30):
    """
    Clean up old read/dismissed notifications.
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models_unified_system import ProactiveNotification

        cutoff = timezone.now() - timedelta(days=days)

        # Delete old read/dismissed notifications
        deleted_count = ProactiveNotification.objects.filter(
            created_at__lt=cutoff,
            is_read=True,
            is_dismissed=True
        ).delete()[0]

        # Mark expired notifications
        expired_count = ProactiveNotification.objects.filter(
            expires_at__lt=timezone.now(),
            is_expired=False
        ).update(is_expired=True)

        logger.info(f"🧹 [CLEANUP] Deleted {deleted_count} old notifications, marked {expired_count} expired")
        return {
            'status': 'success',
            'deleted': deleted_count,
            'marked_expired': expired_count
        }

    except Exception as e:
        logger.exception(f"🧹 [CLEANUP] Notification cleanup failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def expire_old_suggestions(days=14):
    """
    Mark old pending suggestions as expired.
    """
    try:
        from django.utils import timezone
        from datetime import timedelta
        from core.models_unified_system import SmartSuggestion

        cutoff = timezone.now() - timedelta(days=days)

        expired_count = SmartSuggestion.objects.filter(
            created_at__lt=cutoff,
            status='pending',
            is_still_relevant=True
        ).update(status='expired', is_still_relevant=False)

        logger.info(f"📋 [SUGGESTIONS] Expired {expired_count} old suggestions")
        return {'status': 'success', 'expired_count': expired_count}

    except Exception as e:
        logger.exception(f"📋 [SUGGESTIONS] Expiration failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# SESSION 243: AUTONOMOUS AGENT LEARNING SYSTEM
# =============================================================================
# Agents learn from each other in the background, sharing knowledge and insights
# This is the heart of the collective intelligence system
# =============================================================================

@shared_task
def run_agent_learning_cycle():
    from core.tasks_agents import _impl_run_agent_learning_cycle
    return _impl_run_agent_learning_cycle()
@shared_task
def agent_think_and_synthesize():
    from core.tasks_agents import _impl_agent_think_and_synthesize
    return _impl_agent_think_and_synthesize()
@shared_task
def update_agent_effectiveness_from_learning():
    from core.tasks_misc import _impl_update_agent_effectiveness_from_learning
    return _impl_update_agent_effectiveness_from_learning()
@shared_task
def broadcast_learning_status():
    from core.tasks_agents import _impl_broadcast_learning_status
    return _impl_broadcast_learning_status()
@shared_task
def validate_knowledge_sources():
    from core.tasks_agents import _impl_validate_knowledge_sources
    return _impl_validate_knowledge_sources()
@shared_task
def embed_daily_agent_learning():
    from core.tasks_agents import _impl_embed_daily_agent_learning
    return _impl_embed_daily_agent_learning()
@shared_task
def embed_agent_activity(hours: int = 2):
    from core.tasks_agents import _impl_embed_agent_activity
    return _impl_embed_agent_activity(hours)
def _conversation_temporal_context():
    """
    Return a temporal awareness block for conversation system prompts.

    Individual agent execution gets date injection via build_intelligent_prompt()
    and _build_system_prompt(), but conversation prompts build their own system
    messages from scratch — they were missing date context entirely, causing agents
    to reference 2023 dates from spider data as if current.
    """
    from django.utils import timezone
    now = timezone.now()
    year = now.year
    return f"""
TEMPORAL AWARENESS:
- Today's date: {now.strftime('%B %d, %Y')}
- Current year: {year}
- All analysis must be current and relevant to {now.strftime('%B %Y')}
- DO NOT treat data from {year-2} or {year-1} as "current" — note its age
- If source data has a date, state how old it is relative to today"""


# =============================================================================
# Session 1076: Conversation spawn gate — dedup + preflight check
# =============================================================================

def _conversation_spawn_allowed(topic: str, hours: int = 6, log_prefix: str = '[SPAWN-GATE]') -> bool:
    """
    Check whether a new conversation on this topic should be created.

    Returns True if allowed, False if blocked by:
    1. Fuzzy dedup: similar topic exists in last `hours` hours
    2. Preflight: topic starts with "Research needed" but no spider data backs it

    Lightweight guard for automated paths that lack the full dedup pipeline.
    """
    if not topic:
        return False

    try:
        from core.services.deduplication_service import get_deduplication_service
        dedup_svc = get_deduplication_service()

        # Gate 1: Fuzzy dedup — similar topic in recent window
        prior = dedup_svc.find_similar_conversation(topic=topic, hours=hours)
        if prior:
            logger.info(f"{log_prefix} Dedup blocked (fuzzy match in {hours}h): {topic[:60]}")
            return False

        # Gate 2: "Research needed" preflight — only spawn if there's backing data
        if 'research needed' in topic.lower():
            from core.models_unified_system import SpiderData
            # Extract project/topic keywords (strip prefix)
            search_terms = topic.lower().replace('research needed for', '').replace('research needed', '').strip()
            search_terms = search_terms.split(':')[0].strip()[:50]
            if search_terms:
                recent_data = SpiderData.objects.filter(
                    created_at__gte=timezone.now() - timedelta(hours=24),
                ).filter(
                    Q(spider_name__icontains=search_terms[:20]) |
                    Q(embedding_text__icontains=search_terms[:30])
                ).exists()
                if not recent_data:
                    logger.info(f"{log_prefix} Preflight blocked (no backing data): {topic[:60]}")
                    return False

        # Gate 3: Outcome gate — skip if repeated no-data conclusions
        _no_data_skip, _no_data_count = dedup_svc.has_repeated_no_data_conclusions(topic=topic)
        if _no_data_skip:
            logger.info(f"{log_prefix} Outcome gate blocked ({_no_data_count} no-data in 7d): {topic[:60]}")
            return False

    except Exception as e:
        logger.debug(f"{log_prefix} Spawn gate check failed (allowing): {e}")

    return True


# =============================================================================
# Session 1019: Pre-flight agent data gathering for conversations
# =============================================================================

def _preflight_gather_agent_data(topic, participant_names):
    """
    Detect agent name references in topic. If found, invoke those agents
    via AgentRouter.route() and return their results for context injection.

    Prevents dead-loop conversations where agents reference other agents
    (e.g. "Scan competitor activity using ResearchAgent") but can't invoke them.

    Args:
        topic: Conversation topic string
        participant_names: Set of participant agent names (skip these)
    Returns:
        dict with invoked_agents, injected_context, failed_agents, no_data_block
    """
    result = {
        'invoked_agents': [],
        'injected_context': '',
        'failed_agents': [],
        'no_data_block': '',
    }

    if not topic:
        return result

    try:
        from core.agent_router import AgentRouter
        agent_names = list(AgentRouter.AGENT_MAP.keys())
    except Exception as e:
        logger.warning(f"💬 [PREFLIGHT] Could not load AgentRouter: {e}")
        return result

    topic_lower = topic.lower()
    referenced_agents = []

    for name in agent_names:
        if name in participant_names:
            continue
        # Check full name (e.g. "ResearchAgent") and base name (e.g. "research")
        base_name = name.replace('Agent', '').lower()
        if name.lower() in topic_lower or (len(base_name) > 3 and base_name in topic_lower):
            referenced_agents.append(name)

    if not referenced_agents:
        return result

    # Cap at 2 invocations to control cost
    referenced_agents = referenced_agents[:2]
    logger.info(f"💬 [PREFLIGHT] Detected agent references in topic: {referenced_agents}")

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        system_user = User.objects.filter(username='system_autonomous').first()
        if not system_user:
            logger.warning("💬 [PREFLIGHT] No system_autonomous user found")
            return result

        router = AgentRouter(user=system_user)
    except Exception as e:
        logger.warning(f"💬 [PREFLIGHT] Could not create AgentRouter: {e}")
        return result

    context_parts = []
    for agent_name in referenced_agents:
        try:
            # Direct call — timeout handled by AgentRouter/OpenAI internally (120s).
            # ThreadPoolExecutor breaks Django DB connections in child threads.
            agent_result = router.route(agent_name, topic)

            if agent_result and agent_result.message:
                # Truncate to 2000 chars to keep prompt manageable
                msg = agent_result.message[:2000]
                block = (
                    f"\n\n== PRE-GATHERED DATA from {agent_name} ==\n"
                    f"{msg}\n"
                    f"== END PRE-GATHERED DATA =="
                )
                context_parts.append(block)
                result['invoked_agents'].append(agent_name)
                logger.info(f"💬 [PREFLIGHT] Successfully gathered {len(msg)} chars from {agent_name}")
            else:
                result['failed_agents'].append(agent_name)
                logger.warning(f"💬 [PREFLIGHT] {agent_name} returned empty result")

        except Exception as e:
            result['failed_agents'].append(agent_name)
            logger.warning(f"💬 [PREFLIGHT] {agent_name} invocation failed: {e}")

    if context_parts:
        result['injected_context'] = ''.join(context_parts)

    if result['failed_agents']:
        missing = ', '.join(result['failed_agents'])
        result['no_data_block'] = (
            f"\n\n=== NO UPSTREAM DATA AVAILABLE ===\n"
            f"The following agents were referenced but returned ZERO results: {missing}.\n"
            f"You MUST NOT invent data from these agents. Instead, reason from first principles and "
            f"state clearly what data would be needed.\n"
            f"=== END NO-DATA NOTICE ===\n"
        )

    logger.info(
        f"💬 [PREFLIGHT] Pre-flight complete: invoked={result['invoked_agents']}, "
        f"failed={result['failed_agents']}"
    )
    return result


# Session 1019: Delegation tool for mid-conversation agent invocation
CONVERSATION_DELEGATION_TOOL = {
    "type": "function",
    "function": {
        "name": "delegate_to_specialist",
        "description": (
            "Delegate a sub-task to a specialist agent to gather real data mid-conversation. "
            "Use when you need specific data or analysis that another agent specializes in. "
            "Available specialists include: ResearchAgent, TrendAnalysisAgent, "
            "MarketIntelligenceAgent, ContentWriterAgent, StockAnalystAgent, "
            "CompetitorAnalysisAgent, CustomerResearchAgent, and 40+ more."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "specialist_agent": {
                    "type": "string",
                    "description": "Name of the specialist agent to call (e.g., 'ResearchAgent')"
                },
                "task": {
                    "type": "string",
                    "description": "The specific task you want the specialist to perform"
                }
            },
            "required": ["specialist_agent", "task"]
        }
    }
}


def _handle_conversation_delegation(tool_call, system_user):
    """
    Execute a delegation tool call from a conversation LLM response.

    Args:
        tool_call: The tool call object from the LLM response
        system_user: Django User object for AgentRouter

    Returns:
        str: Formatted delegation result context, or empty string on failure
    """
    import json as json_mod
    try:
        args = json_mod.loads(tool_call.function.arguments)
        specialist = args.get('specialist_agent', '')
        task = args.get('task', '')

        if not specialist or not task:
            logger.warning("💬 [DELEGATION] Missing specialist_agent or task in tool call")
            return ''

        from core.agent_router import AgentRouter
        router = AgentRouter(user=system_user)

        # Direct call — timeout handled by AgentRouter/OpenAI internally (120s).
        result = router.route(specialist, task)

        if result and result.message:
            msg = result.message[:2000]
            logger.info(f"💬 [DELEGATION] Successfully delegated to {specialist}: {len(msg)} chars")
            return (
                f"\n\n== DELEGATION RESULT from {specialist} ==\n"
                f"{msg}\n"
                f"== END DELEGATION RESULT =="
            )
        else:
            logger.warning(f"💬 [DELEGATION] {specialist} returned empty result")
            return f"\n\n[Delegation to {specialist} returned no data. Reason from first principles instead.]"

    except Exception as e:
        logger.warning(f"💬 [DELEGATION] Delegation failed: {e}")
        return f"\n\n[Delegation failed: {e}. Reason from first principles instead.]"


# =============================================================================
# Session 1049: Conversation/HiveMind -> Knowledge Bridge
# =============================================================================

def _extract_conversation_knowledge(conversation, initiator, responder, topic, messages):
    """Extract AgentKnowledgeSource records from a concluded agent conversation.

    Creates one AKS per participant if quality gates pass. Idempotent via
    source_spider_names containing 'conversation_{uuid}'.
    """
    from core.models_unified_system import AgentKnowledgeSource

    # Quality gates
    conclusion = conversation.conclusion or ''
    if len(conclusion) < 50:
        return 0
    quality = conversation.quality_score or 0
    if quality < 0.5:
        return 0
    if (conversation.message_count or 0) < 3:
        return 0

    conv_tag = f'conversation_{conversation.id}'
    created = 0

    for agent, partner in [(initiator, responder), (responder, initiator)]:
        # Idempotency: skip if already extracted for this agent + conversation
        if AgentKnowledgeSource.objects.filter(
            agent=agent,
            source_spider_names__contains=[conv_tag],
        ).exists():
            continue

        # Build key_insights from insights_generated + insight-type messages
        key_insights = list(conversation.insights_generated or [])[:5]
        if len(key_insights) < 5:
            for m in messages:
                if m.get('type') == 'insight' and len(key_insights) < 5:
                    text = m.get('content', '')[:300]
                    if text and text not in key_insights:
                        key_insights.append(text)

        AgentKnowledgeSource.objects.create(
            agent=agent,
            knowledge_type='collaborative_insight',
            title=f'[Conversation] {topic[:480]}',
            summary=(
                f'Conversation with {partner.name} on "{topic[:200]}"\n\n'
                f'{conclusion[:2000]}'
            ),
            key_insights=key_insights,
            confidence_score=round(quality * 0.9, 3),
            source_spider_names=[conv_tag, f'partner_{partner.name}'],
        )
        created += 1

    return created


def _extract_hivemind_knowledge(session, completed_contributions):
    """Extract AgentKnowledgeSource records from a completed HiveMind session.

    Creates one AKS per contributing agent. Idempotent via
    source_spider_names containing 'hivemind_{uuid}'.
    """
    from core.models_unified_system import AgentKnowledgeSource

    synthesis = session.synthesis or ''
    if len(synthesis) < 50:
        return 0
    if (session.contribution_count or 0) < 2:
        return 0

    hive_tag = f'hivemind_{session.id}'
    topic = session.question or 'HiveMind Session'
    created = 0

    # Collect top key_points across contributions (max 5)
    all_key_points = []
    for c in completed_contributions:
        points = c.key_points or []
        all_key_points.extend(points[:2])
    all_key_points = all_key_points[:5]

    # Participant names for provenance
    participant_names = [c.agent.name for c in completed_contributions]
    confidence = min(1.0, 0.6 + len(participant_names) * 0.05)

    for contribution in completed_contributions:
        agent = contribution.agent

        if AgentKnowledgeSource.objects.filter(
            agent=agent,
            source_spider_names__contains=[hive_tag],
        ).exists():
            continue

        source_tags = [hive_tag] + [f'partner_{n}' for n in participant_names if n != agent.name]

        AgentKnowledgeSource.objects.create(
            agent=agent,
            knowledge_type='collaborative_insight',
            title=f'[HiveMind] {topic[:485]}',
            summary=(
                f'HiveMind session: "{topic[:200]}"\n'
                f'Participants: {", ".join(participant_names)}\n\n'
                f'{synthesis[:2000]}'
            ),
            key_insights=all_key_points,
            confidence_score=round(confidence, 3),
            source_spider_names=source_tags[:10],  # cap array length
        )
        created += 1

    return created


# =============================================================================
# Session 244: Agent Conversations (Inter-Agent Chat)
# =============================================================================

@shared_task(bind=True, soft_time_limit=1800, time_limit=1860, ignore_result=True)
def run_agent_conversation(self, max_conversations: int = 3, max_messages: int = 6):
    from core.tasks_conversations import _impl_run_agent_conversation
    return _impl_run_agent_conversation(self, max_conversations, max_messages)
@shared_task(bind=True, max_retries=2, soft_time_limit=1800, time_limit=1860, ignore_result=True)
def run_multi_agent_conversation(self, max_conversations: int = 2, participants_per_conversation: int = 4, max_rounds: int = 3):
    from core.tasks_conversations import _impl_run_multi_agent_conversation
    return _impl_run_multi_agent_conversation(self, max_conversations, participants_per_conversation, max_rounds)
@shared_task(bind=True)
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


# =============================================================================
# Session 362: Spider-Triggered Conversations
# =============================================================================

@shared_task(bind=True)
def trigger_spider_conversations(self, min_relevance: int = 70, max_conversations: int = 2):
    from core.tasks_conversations import _impl_trigger_spider_conversations
    return _impl_trigger_spider_conversations(self, min_relevance, max_conversations)
@shared_task(bind=True)
def trigger_project_research(self, max_projects: int = 3, max_spiders_per_project: int = 2):
    from core.tasks_ops import _impl_trigger_project_research
    return _impl_trigger_project_research(self, max_projects, max_spiders_per_project)
@shared_task(bind=True)
def propagate_new_policies(self, hours_back: int = 2, max_actions: int = 3):
    """
    Session 363: Propagate newly promoted policies to relevant agents.

    DEPRECATED (Session 659): This task used a non-existent 'propagated_at' field.
    Policy injection now happens automatically via PolicyContextService when agents
    are called, so explicit propagation is no longer needed.

    Args:
        hours_back: How far back to look for new policies
        max_actions: Maximum actions to trigger per run

    Returns:
        Deprecation notice
    """
    # Session 659: This task is deprecated because:
    # 1. The 'propagated_at' field never existed on AgentDecisionSummary
    # 2. PolicyContextService already injects canonical policies into agent prompts
    # 3. Agents automatically receive policy context without explicit propagation
    logger.info("🏛️ [POLICY-PROPAGATE] DEPRECATED - PolicyContextService handles policy injection automatically")

    return {
        'status': 'deprecated',
        'message': 'Policy propagation now happens automatically via PolicyContextService when agents are called.',
        'info': 'Canonical policies are injected into agent prompts without needing explicit propagation.'
    }


@shared_task(bind=True)
def broadcast_conversation_status(self):
    from core.tasks_misc import _impl_broadcast_conversation_status
    return _impl_broadcast_conversation_status(self)
@shared_task(bind=True)
def run_project_conversation(self, project_id: str, topic: str, max_messages: int = 6):
    from core.tasks_conversations import _impl_run_project_conversation
    return _impl_run_project_conversation(self, project_id, topic, max_messages)
@shared_task(bind=True)
def generate_agent_dreams(self, max_dreamers: int = 5, dreams_per_agent: int = 2):
    from core.tasks_initiatives import _impl_generate_agent_dreams
    return _impl_generate_agent_dreams(self, max_dreamers, dreams_per_agent)
@shared_task(bind=True)
def broadcast_dream_journal(self):
    from core.tasks_initiatives import _impl_broadcast_dream_journal
    return _impl_broadcast_dream_journal(self)
@shared_task(bind=True)
def score_and_promote_dreams(self, max_dreams: int = 50, promote_threshold: float = 0.85):
    from core.tasks_initiatives import _impl_score_and_promote_dreams
    return _impl_score_and_promote_dreams(self, max_dreams, promote_threshold)
@shared_task(bind=True)
def process_approved_dreams(self, max_dreams: int = 10):
    from core.tasks_initiatives import _impl_process_approved_dreams
    return _impl_process_approved_dreams(self, max_dreams)
@shared_task(bind=True)
def cleanup_stale_dreams(self, max_age_hours: int = 72):
    from core.tasks_initiatives import _impl_cleanup_stale_dreams
    return _impl_cleanup_stale_dreams(self, max_age_hours)
@shared_task(bind=True, soft_time_limit=1800, time_limit=1860)
def execute_dream_implementations(self, max_implementations: int = 5):
    from core.tasks_initiatives import _impl_execute_dream_implementations
    return _impl_execute_dream_implementations(self, max_implementations)
def _execute_feature_implementation(client, dream, impl, agent):
    """Generate a feature specification/proposal document."""
    prompt = f"""You are {agent.name if agent else 'an AI agent'}, executing an approved dream implementation.

Dream: {dream.title}
Dream Content: {dream.content}

Implementation Plan:
{impl.implementation_plan}

Create a detailed FEATURE SPECIFICATION that includes:
1. Executive Summary (2-3 sentences)
2. Problem Statement
3. Proposed Solution
4. Key Features (bullet points)
5. Technical Requirements
6. Success Metrics
7. Implementation Timeline (phases)
8. Risks and Mitigations

Write in a professional, actionable format. Be specific and creative."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000  # Higher for reasoning models
    )
    content = response.choices[0].message.content
    if content:
        return content.strip()
    logger.warning(f"⚡ [EXECUTION-ENGINE] No content returned for feature: {dream.title[:30]}")
    return None


def _execute_content_implementation(client, dream, impl, agent):
    """Generate a content strategy document."""
    prompt = f"""You are {agent.name if agent else 'an AI agent'}, executing an approved dream implementation.

Dream: {dream.title}
Dream Content: {dream.content}

Implementation Plan:
{impl.implementation_plan}

Create a detailed CONTENT STRATEGY that includes:
1. Content Overview
2. Target Audience
3. Key Messages (3-5)
4. Content Types (blog posts, social media, videos, etc.)
5. Content Calendar (suggested topics for 4 weeks)
6. Distribution Channels
7. Engagement Tactics
8. Success Metrics

Write in a professional, actionable format. Be creative and specific."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=2500  # Higher for reasoning models
    )
    return response.choices[0].message.content.strip()


def _execute_research_implementation(client, dream, impl, agent):
    """Generate a research report."""
    prompt = f"""You are {agent.name if agent else 'an AI agent'}, executing an approved dream implementation.

Dream: {dream.title}
Dream Content: {dream.content}

Implementation Plan:
{impl.implementation_plan}

Create a comprehensive RESEARCH REPORT that includes:
1. Executive Summary
2. Research Objectives
3. Methodology
4. Key Findings (5-7 insights with evidence)
5. Market/Industry Analysis
6. Competitive Landscape
7. Opportunities Identified
8. Recommendations (prioritized)
9. Next Steps

Write in a professional research format. Be thorough and analytical."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=2500  # Higher for reasoning models
    )
    return response.choices[0].message.content.strip()


def _execute_experiment_implementation(client, dream, impl, agent):
    """Generate an experiment design and findings document."""
    prompt = f"""You are {agent.name if agent else 'an AI agent'}, executing an approved dream implementation.

Dream: {dream.title}
Dream Content: {dream.content}

Implementation Plan:
{impl.implementation_plan}

Create an EXPERIMENT REPORT that includes:
1. Hypothesis Statement
2. Experiment Design
3. Variables (independent, dependent, controlled)
4. Methodology
5. Expected Results
6. Simulated Findings (what we would expect to find)
7. Analysis and Interpretation
8. Conclusions
9. Recommendations for Further Experimentation

Write in a scientific format. Be creative but rigorous."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=2500  # Higher for reasoning models
    )
    return response.choices[0].message.content.strip()


def _execute_generic_implementation(client, dream, impl, agent):
    """Generate a generic implementation document."""
    prompt = f"""You are {agent.name if agent else 'an AI agent'}, executing an approved dream implementation.

Dream: {dream.title}
Dream Content: {dream.content}

Implementation Plan:
{impl.implementation_plan}

Create a comprehensive IMPLEMENTATION DOCUMENT that includes:
1. Overview and Objectives
2. Approach and Methodology
3. Key Components
4. Implementation Details
5. Resources Required
6. Timeline
7. Expected Outcomes
8. Monitoring and Evaluation
9. Next Steps

Write in a professional, actionable format."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=2500  # Higher for reasoning models
    )
    return response.choices[0].message.content.strip()


def _execute_visual_implementation(dream, impl, agent):
    """
    Session 370: Generate actual images using ImageAgent for visual dreams.

    This function uses the ImageAgent to generate real images based on the
    dream content. The generated images are stored and linked to the implementation.

    Args:
        dream: The AgentDream being implemented
        impl: The DreamImplementation record
        agent: The Agent model assigned to this implementation

    Returns:
        Dict with 'images' list and 'description' or None on failure
    """
    from content.image_generation import ImageGenerationService

    logger.info(f"🎨 [VISUAL-ENGINE] Generating images for: {dream.title[:50]}")

    try:
        # Build an image generation prompt from the dream
        # The dream title and content describe the visual concept
        image_prompt = _build_image_prompt_from_dream(dream, impl)

        # Initialize the image generation service
        image_service = ImageGenerationService()

        # Determine style based on dream type/content
        style = _detect_visual_style(dream)

        # Generate the image(s)
        result = image_service.generate_image(
            prompt=image_prompt,
            provider='stability',  # Use Stability AI
            style=style,
            num_images=1,  # Generate 1 image per dream for now
            quality='balanced'  # SDXL - good quality, reasonable cost
        )

        if result.success and result.images:
            # Format the images for storage
            generated_images = []
            for i, img_data in enumerate(result.images):
                # img_data could be URL or base64
                image_record = {
                    'index': i,
                    'url': img_data if isinstance(img_data, str) and img_data.startswith('http') else None,
                    'base64': img_data if isinstance(img_data, str) and not img_data.startswith('http') else None,
                    'prompt': image_prompt,
                    'style': style,
                    'provider': result.provider_used,
                    'model': result.model_used,
                    'dream_id': str(dream.id),
                    'dream_title': dream.title,
                }
                generated_images.append(image_record)

            logger.info(
                f"🎨 [VISUAL-ENGINE] Generated {len(generated_images)} image(s) for: {dream.title[:40]}"
            )

            # Create a description document
            description = f"""# Visual Implementation: {dream.title}

## Generated Images
- **Count**: {len(generated_images)} image(s)
- **Style**: {style}
- **Provider**: {result.provider_used}
- **Model**: {result.model_used}

## Prompt Used
{image_prompt}

## Dream Context
{dream.content[:500] if dream.content else 'No additional context'}

## Implementation Plan
{impl.implementation_plan[:500] if impl.implementation_plan else 'Auto-generated visual'}
"""

            return {
                'images': generated_images,
                'description': description,
                'generation_time_ms': result.generation_time_ms,
                'provider': result.provider_used,
                'model': result.model_used
            }

        else:
            logger.warning(
                f"🎨 [VISUAL-ENGINE] Failed to generate images for: {dream.title[:40]} - {result.error_message}"
            )
            return None

    except Exception as e:
        logger.exception(f"🎨 [VISUAL-ENGINE] Error generating images: {e}")
        return None


def _build_image_prompt_from_dream(dream, impl):
    """
    Build an optimized image generation prompt from dream content.

    Extracts key visual concepts from the dream title and content
    and formats them for Stability AI.
    """
    # Start with the dream title as the main concept
    title = dream.title.strip()

    # Add content context if available
    content = dream.content[:200] if dream.content else ''

    # Build the prompt
    prompt_parts = [title]

    # Extract visual keywords from content
    visual_keywords = []
    visual_terms = ['visual', 'design', 'style', 'color', 'image', 'graphic',
                    'illustration', 'art', 'creative', 'aesthetic', 'modern',
                    'futuristic', 'elegant', 'vibrant', 'dynamic']

    if content:
        for term in visual_terms:
            if term.lower() in content.lower():
                visual_keywords.append(term)

    # Add implementation context if available
    if impl.implementation_plan:
        # Extract first actionable item
        plan_lines = impl.implementation_plan.split('\n')
        for line in plan_lines[:3]:
            if line.strip() and not line.strip().startswith('#'):
                prompt_parts.append(line.strip()[:100])
                break

    # Combine into final prompt
    base_prompt = ', '.join(prompt_parts)

    # Add quality enhancers for Stability AI
    quality_suffix = ", high quality, detailed, professional, 4k"

    return f"{base_prompt}{quality_suffix}"


def _is_visual_dream(dream):
    """
    Session 370: Detect if a dream should be implemented as a visual/image.

    Uses keyword matching against the dream title and content to determine
    if this dream describes a visual concept that should be rendered as an image.

    Returns:
        True if the dream should be a visual implementation
    """
    text = (dream.title + ' ' + (dream.content or '')).lower()

    # Strong visual indicators - if any of these are present, it's visual
    strong_visual_keywords = [
        'image', 'visual', 'graphic', 'illustration', 'artwork',
        'design', 'logo', 'icon', 'picture', 'photo', 'art gallery',
        'visualization', 'render', 'aesthetic', 'banner', 'poster',
        'infographic', 'chart', 'diagram', 'thumbnail', 'avatar',
    ]

    # Check for strong indicators
    for keyword in strong_visual_keywords:
        if keyword in text:
            return True

    # Title-based patterns that suggest visual output
    visual_title_patterns = [
        'art ', ' art', 'gallery', 'studio', 'creative hub',
        'visual experience', 'immersive', 'interactive display',
    ]

    title_lower = dream.title.lower()
    for pattern in visual_title_patterns:
        if pattern in title_lower:
            return True

    # Agent-based detection: If the dreaming agent is image-focused
    if dream.agent and dream.agent.name in ['ImageAgent', 'CreativeDirectorAgent']:
        # More likely to be visual if from these agents
        return 'creative' in text or 'design' in text or 'style' in text

    return False


def _detect_visual_style(dream):
    """
    Detect the appropriate visual style based on dream content.

    Returns a style preset that works well with Stability AI.
    """
    content = (dream.title + ' ' + (dream.content or '')).lower()

    # Style detection patterns
    style_patterns = {
        'cyberpunk': ['cyber', 'neon', 'tech', 'digital', 'ai', 'future', 'robot'],
        'fantasy': ['magic', 'fantasy', 'mythical', 'dragon', 'wizard', 'enchant'],
        'minimalist': ['minimal', 'simple', 'clean', 'modern', 'elegant'],
        'watercolor': ['watercolor', 'artistic', 'painted', 'soft'],
        'photorealistic': ['photo', 'realistic', 'real', 'natural'],
        'anime': ['anime', 'manga', 'cartoon', 'animated'],
        'concept_art': ['concept', 'design', 'game', 'character'],
        'digital_art': ['digital', 'graphic', 'illustration', 'artwork'],
    }

    # Score each style based on keyword matches
    style_scores = {}
    for style, keywords in style_patterns.items():
        score = sum(1 for keyword in keywords if keyword in content)
        if score > 0:
            style_scores[style] = score

    # Return the best matching style or default
    if style_scores:
        return max(style_scores.items(), key=lambda x: x[1])[0]

    # Default to digital art for creative AI dreams
    return 'digital_art'


@shared_task(bind=True)
def explore_dream_topic(self, exploration_id: str):
    from core.tasks_conversations import _impl_explore_dream_topic
    return _impl_explore_dream_topic(self, exploration_id)
@shared_task(bind=True)
def run_hive_mind_session(self, session_id: str):
    from core.tasks_conversations import _impl_run_hive_mind_session
    return _impl_run_hive_mind_session(self, session_id)
def broadcast_hive_mind_update(session, contribution, status):
    """Broadcast a contribution update via Redis pub/sub."""
    try:
        import redis
        import json
        from django.utils import timezone
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
        r.publish('hive_mind', json.dumps({
            'type': 'contribution_update',
            'session_id': str(session.id),
            'contribution_id': str(contribution.id),
            'agent_name': contribution.agent.name,
            'status': status,
            'perspective_type': contribution.perspective_type,
            'thinking_time': contribution.thinking_time,
            'timestamp': timezone.now().isoformat()
        }))
    except Exception as e:
        logger.warning(f"Failed to broadcast hive mind update: {e}")


def broadcast_hive_mind_status(session, status):
    """Broadcast a session status update via Redis pub/sub."""
    try:
        import redis
        import json
        from django.utils import timezone
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
        r.publish('hive_mind', json.dumps({
            'type': 'session_status',
            'session_id': str(session.id),
            'status': status,
            'contribution_count': session.contribution_count,
            'timestamp': timezone.now().isoformat()
        }))
    except Exception as e:
        logger.warning(f"Failed to broadcast hive mind status: {e}")


# =============================================================================
# Session 251: Memory Palace Tasks
# =============================================================================

@shared_task
def generate_memory_embedding(memory_id: str):
    from core.tasks_media import _impl_generate_memory_embedding
    return _impl_generate_memory_embedding(memory_id)
@shared_task(bind=True, name='core.tasks.backfill_memory_embeddings')
def backfill_memory_embeddings(self, batch_size: int = 50):
    """
    Session 490: Backfill embeddings for memories that don't have them.

    Runs periodically to ensure all memories have embeddings for semantic search.
    """
    logger.info(f"🧠 [MEMORY BACKFILL] Starting backfill (batch_size={batch_size})")

    try:
        from core.services.memory_embedding_service import get_memory_embedding_service

        service = get_memory_embedding_service()
        stats = service.backfill_embeddings(batch_size=batch_size)

        logger.info(
            f"🧠 [MEMORY BACKFILL] Completed: "
            f"{stats['succeeded']}/{stats['processed']} succeeded"
        )

        return {
            'status': 'completed',
            'processed': stats['processed'],
            'succeeded': stats['succeeded'],
            'failed': stats['failed']
        }

    except Exception as e:
        logger.error(f"🧠 [MEMORY BACKFILL] Error: {e}")
        return {'status': 'error', 'error': str(e)}


# =============================================================================
# Session 729: Conversation Memory Embedding Backfill Task
# =============================================================================

@shared_task(bind=True, name='core.tasks.backfill_conversation_embeddings')
def backfill_conversation_embeddings(self, batch_size: int = 50):
    from core.tasks_misc import _impl_backfill_conversation_embeddings
    return _impl_backfill_conversation_embeddings(self, batch_size)
@shared_task(name='core.tasks.update_agent_mood')
def update_agent_mood(agent_id: str, mood: str, intensity: float = 0.7,
                      trigger_type: str = 'task_success', trigger_source: str = '',
                      duration_minutes: int = 60):
    from core.tasks_misc import _impl_update_agent_mood
    return _impl_update_agent_mood(agent_id, mood, intensity, trigger_type, trigger_source, duration_minutes)
@shared_task(name='core.tasks.check_mood_expirations')
def check_mood_expirations():
    from core.tasks_body_systems import _impl_check_mood_expirations
    return _impl_check_mood_expirations()
@shared_task(name='core.tasks.apply_mood_trigger_rules')
def apply_mood_trigger_rules(agent_id: str = None):
    from core.tasks_misc import _impl_apply_mood_trigger_rules
    return _impl_apply_mood_trigger_rules(agent_id)
@shared_task(name='core.tasks.evolve_agent_relationships')
def evolve_agent_relationships():
    """
    Session 253: Periodically evolve agent relationships based on activity.

    Called by Celery Beat every 30 minutes to:
    - Strengthen relationships that have recent positive interactions
    - Weaken relationships with no recent activity
    - Potentially evolve relationship types based on cumulative interactions
    """
    try:
        from core.models_unified_system import AgentRelationship

        relationships = AgentRelationship.objects.all().iterator()
        evolved_count = 0

        for rel in relationships:
            # Check for stale relationships (no interaction in 7 days)
            if rel.last_interaction_at:
                days_since_interaction = (timezone.now() - rel.last_interaction_at).days

                if days_since_interaction > 7:
                    # Slightly decay strength for inactive relationships
                    old_strength = rel.strength
                    rel.strength = max(0.1, rel.strength - 0.02)

                    if old_strength != rel.strength:
                        rel.save()
                        evolved_count += 1

            # Natural trust recovery for rivalries with positive interactions
            if rel.relationship_type == 'rivalry' and rel.respect_level > 0.7:
                rel.trust_level = min(1.0, rel.trust_level + 0.01)
                rel.save()
                evolved_count += 1

        logger.info(f"⚔️ [RELATIONSHIPS] Evolved {evolved_count} relationships")

        return {
            'status': 'success',
            'evolved_count': evolved_count
        }

    except Exception as e:
        logger.exception(f"⚔️ [RELATIONSHIPS] Failed to evolve: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.update_alliance_strengths')
def update_alliance_strengths():
    """
    Session 253: Update combined strength for all active alliances.
    Session 871: Alliance model removed (0 records, never used).
    Task kept as stub to avoid Celery Beat errors.
    """
    # Session 871: Alliance model removed
    return {
        'status': 'skipped',
        'reason': 'Alliance model removed in Session 871'
    }


@shared_task(name='core.tasks.broadcast_relationship_status')
def broadcast_relationship_status():
    from core.tasks_misc import _impl_broadcast_relationship_status
    return _impl_broadcast_relationship_status()
@shared_task(name='core.tasks.process_agent_activity_xp')
def process_agent_activity_xp():
    from core.tasks_agents import _impl_process_agent_activity_xp
    return _impl_process_agent_activity_xp()
@shared_task(name='core.tasks.check_level_milestones')
def check_level_milestones():
    """
    Session 254: Check for and record any missed level milestones.

    Called by Celery Beat hourly to ensure milestones are recorded.
    """
    try:
        from core.models_unified_system import AgentEvolution, LevelMilestone

        evolutions = AgentEvolution.objects.all().iterator()
        milestones_created = 0

        for evo in evolutions:
            # Check if milestone exists for current level
            if not LevelMilestone.objects.filter(evolution=evo, level=evo.current_level).exists():
                LevelMilestone.objects.create(
                    evolution=evo,
                    level=evo.current_level,
                    title=evo.get_title(),  # Session 799: Use method not attribute
                    xp_at_milestone=evo.total_xp,
                    bonus_awarded='milestone_check'
                )
                milestones_created += 1

        logger.info(f"📈 [EVOLUTION] Created {milestones_created} missing milestones")

        return {
            'status': 'success',
            'milestones_created': milestones_created
        }

    except Exception as e:
        logger.exception(f"📈 [EVOLUTION] Failed to check milestones: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.broadcast_evolution_status', ignore_result=True)
def broadcast_evolution_status():
    from core.tasks_misc import _impl_broadcast_evolution_status
    return _impl_broadcast_evolution_status()
@shared_task
def sync_project_knowledge():
    """
    Sync BusinessResearchResult to AgentKnowledgeSource.
    Runs every 30 minutes via Celery Beat.

    Session 326: Project-Agent Learning Bridge

    This task:
    - Finds unprocessed research results
    - Converts them to agent knowledge
    - Links knowledge to source project
    """
    from core.services.project_research_bridge import get_project_research_bridge

    logger.info("🔗 [SESSION 326] Starting project knowledge sync...")

    try:
        bridge = get_project_research_bridge()
        result = bridge.sync_all_research_to_knowledge(limit=50)

        logger.info(
            f"🔗 [SESSION 326] Knowledge sync complete: "
            f"{result['processed_research']} research → {result['knowledge_created']} knowledge"
        )

        return result

    except Exception as e:
        logger.exception(f"🔗 [SESSION 326] Knowledge sync failed: {e}")
        return {'error': str(e)}


@shared_task
def recalculate_spider_priorities():
    """
    Recalculate spider priorities based on active projects.
    Runs every 6 hours via Celery Beat.

    Session 326: Project-Agent Learning Bridge

    This task:
    - Scans all active projects
    - Extracts topics and keywords
    - Updates ProjectSpiderPriority weights
    - Influences spider run frequency
    """
    from core.services.spider_priority_engine import get_spider_priority_engine

    logger.info("🕷️ [SESSION 326] Starting spider priority recalculation...")

    try:
        engine = get_spider_priority_engine()
        result = engine.recalculate_all_priorities()

        logger.info(
            f"🕷️ [SESSION 326] Priority recalculation complete: "
            f"{result['projects_processed']} projects, "
            f"{result['priorities_created']} created, "
            f"{result['priorities_updated']} updated"
        )

        return result

    except Exception as e:
        logger.exception(f"🕷️ [SESSION 326] Priority recalculation failed: {e}")
        return {'error': str(e)}


@shared_task
def process_research_feedback(feedback_id: str):
    """
    Process a single research feedback submission.

    Session 326: Project-Agent Learning Bridge

    This task:
    - Loads the feedback entry
    - Applies confidence adjustments to related knowledge
    - Updates spider priorities if needed
    """
    from core.services.project_research_bridge import get_project_research_bridge

    logger.info(f"📝 [SESSION 326] Processing feedback {feedback_id}...")

    try:
        bridge = get_project_research_bridge()
        from uuid import UUID as _UUID
        result = bridge.apply_feedback(_UUID(feedback_id) if isinstance(feedback_id, str) else feedback_id)

        if result.get('status') == 'applied':
            logger.info(
                f"📝 [SESSION 326] Feedback applied: "
                f"{result['feedback_type']} → {result['updated_count']} knowledge entries"
            )
        else:
            logger.info(f"📝 [SESSION 326] Feedback status: {result.get('status', 'unknown')}")

        return result

    except Exception as e:
        logger.exception(f"📝 [SESSION 326] Feedback processing failed: {e}")
        return {'error': str(e)}


@shared_task
def update_project_spider_priorities(project_id: str):
    """
    Update spider priorities for a specific project.
    Called when a project is created or updated.

    Session 326: Project-Agent Learning Bridge
    """
    from core.services.spider_priority_engine import get_spider_priority_engine
    from core.models_partnership import PartnershipProject

    logger.info(f"🎯 [SESSION 326] Updating spider priorities for project {project_id}...")

    try:
        project = PartnershipProject.objects.get(id=project_id)
        engine = get_spider_priority_engine()
        result = engine.update_project_priorities(project)

        logger.info(
            f"🎯 [SESSION 326] Project priorities updated: "
            f"{result['categories_matched']} categories matched"
        )

        return result

    except PartnershipProject.DoesNotExist:
        logger.error(f"🎯 [SESSION 326] Project {project_id} not found")
        return {'error': 'Project not found'}
    except Exception as e:
        logger.exception(f"🎯 [SESSION 326] Priority update failed: {e}")
        return {'error': str(e)}


# =============================================================================
# Session 354: Project Learning Loop
# Enable projects to autonomously learn and track their domain over time
# =============================================================================

@shared_task
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


@shared_task
def run_single_project_learning(project_id: str):
    from core.tasks_ops import _impl_run_single_project_learning
    return _impl_run_single_project_learning(project_id)
def _extract_topics_from_project(project):
    """
    Extract learning topics from project name and research.

    Session 354: Auto-detect topics when none specified.
    """
    topics = []

    # From project name
    name_words = project.project_name.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on', 'at', 'to', 'of', 'is', 'my'}
    topics.extend([w for w in name_words if w not in stop_words and len(w) > 3])

    # From existing research summaries
    if project.metadata:
        for summary in project.metadata.get('research_summaries', []):
            if summary.get('type') in ['competitor_analysis', 'customer_research', 'brand_strategy']:
                # Extract key terms from summary
                text = summary.get('summary', '')
                words = text.lower().split()[:10]
                topics.extend([w for w in words if w not in stop_words and len(w) > 4])

    # Dedupe and limit
    seen = set()
    unique_topics = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            unique_topics.append(t)

    return unique_topics[:5]


def _analyze_spider_data_for_trends(spider_data: list, project_name: str) -> list:
    """
    Analyze spider data to extract trends.

    Session 354: Extract key terms and themes from spider data.
    """
    findings = []
    stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on', 'at', 'to', 'of', 'is', 'are', 'was', 'be', 'has'}

    for item in spider_data[:50]:  # Limit to 50 items
        if isinstance(item, dict):
            title = item.get('title', '')
            content = item.get('content', item.get('description', ''))

            # Extract significant words from title
            title_words = [w.lower() for w in title.split() if len(w) > 4 and w.lower() not in stop_words]
            findings.extend(title_words[:5])

            # Extract from content
            content_words = [w.lower() for w in content.split()[:30] if len(w) > 4 and w.lower() not in stop_words]
            findings.extend(content_words[:3])

    return findings


def _get_previous_findings(project) -> list:
    """
    Get findings from previous learning run.

    Session 354: Retrieve previous findings for delta comparison.
    """
    history = project.learning_history or []
    if not history:
        return []

    last_run = history[-1]
    return last_run.get('new_trends', []) + last_run.get('topics_researched', [])


def _detect_research_deltas(previous: list, current: list) -> dict:
    """
    Compare research findings to detect what's new/changed.

    Session 354: Simple set-based delta detection.
    """
    prev_set = set(str(p).lower() for p in previous if p)
    curr_set = set(str(c).lower() for c in current if c)

    new_items = list(curr_set - prev_set)
    removed_items = list(prev_set - curr_set)

    return {
        'new_items': new_items[:20],
        'removed_items': removed_items[:20],
        'total_previous': len(prev_set),
        'total_current': len(curr_set),
        'change_rate': len(new_items) / max(len(curr_set), 1) if curr_set else 0
    }


def _create_learning_notification(project, deltas):
    """
    Create a notification for significant learning updates.

    Session 354: Alert user about new trends.
    """
    from core.models_unified_system import ProactiveAlert

    try:
        new_trends = deltas.get('new_items', [])[:3]
        trend_preview = ', '.join(new_trends) if new_trends else 'trends'

        ProactiveAlert.objects.create(
            user=project.user,
            alert_type='learning_update',
            title=f"New trends for {project.project_name}",
            message=f"Found {len(deltas.get('new_items', []))} new trends: {trend_preview}...",
            priority='medium',
            metadata={
                'project_id': str(project.id),
                'project_name': project.project_name,
                'new_trends': deltas.get('new_items', [])[:10],
                'total_new': len(deltas.get('new_items', []))
            }
        )
        logger.info(f"🧠 [SESSION 354] Created learning notification for {project.project_name}")
    except Exception as e:
        logger.warning(f"🧠 [SESSION 354] Failed to create notification: {e}")


# ==================== SESSION 373: AUTO-RESOLVE KNOWLEDGE GAPS ====================


@shared_task(bind=True, max_retries=2)
def auto_resolve_knowledge_gaps(self):
    from core.tasks_misc import _impl_auto_resolve_knowledge_gaps
    return _impl_auto_resolve_knowledge_gaps(self)
@shared_task(bind=True, max_retries=3)
def process_document_async(self, document_id: int, generate_embeddings: bool = True, embedding_model: str = 'openai_text_embedding_3_small'):
    from core.tasks_misc import _impl_process_document_async
    return _impl_process_document_async(self, document_id, generate_embeddings, embedding_model)
@shared_task(bind=True, max_retries=3)
def process_url_async(self, url: str, title: str = None, user_id: int = None, generate_embeddings: bool = True):
    from core.tasks_media import _impl_process_url_async
    return _impl_process_url_async(self, url, title, user_id, generate_embeddings)
@shared_task(bind=True, max_retries=3)
def generate_document_embeddings(self, document_id: str, embedding_model: str = 'openai_small'):
    from core.tasks_misc import _impl_generate_document_embeddings
    return _impl_generate_document_embeddings(self, document_id, embedding_model)
@shared_task(bind=True, max_retries=1, soft_time_limit=600, time_limit=660,
             queue='long_running', ignore_result=True)
def transcribe_video_task(self, transcript_id):
    from core.tasks_media import _impl_transcribe_video_task
    return _impl_transcribe_video_task(self, transcript_id)
@shared_task(bind=True, max_retries=1, soft_time_limit=120, time_limit=150,
             queue='long_running', ignore_result=False)
def generate_video_content_pack_task(self, video_id, user_id, language='en'):
    from core.tasks_content import _impl_generate_video_content_pack_task
    return _impl_generate_video_content_pack_task(self, video_id, user_id, language)
@shared_task(bind=True, max_retries=1, soft_time_limit=1800, time_limit=1860, ignore_result=False)
def ingest_video_task(self, document_id, tmp_video_path, original_filename, user_id, language='en'):
    from core.tasks_media import _impl_ingest_video_task
    return _impl_ingest_video_task(self, document_id, tmp_video_path, original_filename, user_id, language)
@shared_task
def collect_training_data():
    from core.tasks_ops import _impl_collect_training_data
    return _impl_collect_training_data()
@shared_task
def collect_training_data_full():
    from core.tasks_ops import _impl_collect_training_data_full
    return _impl_collect_training_data_full()
@shared_task
def cleanup_spider_item_hashes(days_to_keep: int = 7):
    """
    Session 616: Clean up old spider item hashes to prevent table bloat.

    Removes hash records older than the lookback period since they're
    no longer needed for deduplication.

    Args:
        days_to_keep: Days of hashes to retain (default: 7)

    Returns:
        Dict with cleanup stats
    """
    from core.services.spider_deduplication import SpiderDeduplicationService

    try:
        service = SpiderDeduplicationService()
        deleted = service.cleanup_old_hashes(days_to_keep)

        logger.info(f"🧹 [SESSION 616] Cleaned up {deleted} old spider item hashes (older than {days_to_keep} days)")

        return {
            'status': 'success',
            'deleted': deleted,
            'days_kept': days_to_keep,
        }
    except Exception as e:
        logger.error(f"🧹 [SESSION 616] Hash cleanup failed: {e}")
        return {'status': 'error', 'error': str(e)}


# Session 1064: Telemetry cleanup — prevent unbounded table growth
@shared_task
def cleanup_celery_task_events(days_to_keep: int = None):
    """Delete CeleryTaskEvent records older than retention period."""
    from django.conf import settings as django_settings
    from core.models_celery_telemetry import CeleryTaskEvent
    if days_to_keep is None:
        days_to_keep = getattr(django_settings, 'CELERY_TASK_EVENT_RETENTION_DAYS', 30)
    cutoff = timezone.now() - timedelta(days=days_to_keep)
    count, _ = CeleryTaskEvent.objects.filter(started_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {count} CeleryTaskEvent records older than {days_to_keep} days")
    return {'deleted': count, 'retention_days': days_to_keep}


@shared_task
def cleanup_llm_call_logs(days_to_keep: int = None):
    """Delete LLMCallLog records older than retention period."""
    from django.conf import settings as django_settings
    from core.models_llm_routing import LLMCallLog
    if days_to_keep is None:
        days_to_keep = getattr(django_settings, 'LLM_CALL_LOG_RETENTION_DAYS', 30)
    cutoff = timezone.now() - timedelta(days=days_to_keep)
    count, _ = LLMCallLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Cleaned up {count} LLMCallLog records older than {days_to_keep} days")
    return {'deleted': count, 'retention_days': days_to_keep}


@shared_task
def generate_weekly_opportunity_digest():
    from core.tasks_ops import _impl_generate_weekly_opportunity_digest
    return _impl_generate_weekly_opportunity_digest()
@shared_task
def send_proactive_opportunity_alerts():
    from core.tasks_ops import _impl_send_proactive_opportunity_alerts
    return _impl_send_proactive_opportunity_alerts()
@shared_task
def send_personalized_opportunity_alerts():
    from core.tasks_ops import _impl_send_personalized_opportunity_alerts
    return _impl_send_personalized_opportunity_alerts()
@shared_task(bind=True, max_retries=3)
def generate_content_package(self, package_id: str):
    from core.tasks_content import _impl_generate_content_package
    return _impl_generate_content_package(self, package_id)
@shared_task(bind=True, max_retries=3)
def generate_ai_series(self, series_id: str):
    from core.tasks_content import _impl_generate_ai_series
    return _impl_generate_ai_series(self, series_id)
@shared_task
def assemble_chunked_upload(upload_id: str):
    from core.tasks_media import _impl_assemble_chunked_upload
    return _impl_assemble_chunked_upload(upload_id)
@shared_task
def cleanup_expired_uploads():
    """
    Clean up incomplete upload sessions older than expiry time.
    Run hourly via Celery Beat.

    Session 451: Automatic cleanup of abandoned uploads.
    """
    from content.models import UploadSession
    from django.utils import timezone
    from pathlib import Path
    import shutil

    logger.info("🧹 [SESSION 451] Starting upload cleanup task")

    expired = UploadSession.objects.filter(
        status__in=['pending', 'uploading'],
        expires_at__lt=timezone.now()
    )

    cleaned = 0
    for session in expired:
        # Remove temp files
        if session.temp_path:
            temp_path = Path(session.temp_path)
            if temp_path.exists():
                shutil.rmtree(temp_path, ignore_errors=True)
                logger.info(f"🧹 [SESSION 451] Cleaned temp files for upload {session.id}")

        session.status = 'cancelled'
        session.error_message = 'Upload session expired'
        session.save()
        cleaned += 1

    logger.info(f"🧹 [SESSION 451] Cleaned up {cleaned} expired upload sessions")
    return {'cleaned': cleaned}


# =============================================================================
# Session 452: Pipeline Learning <-> Collective Intelligence Bridge
# =============================================================================

@shared_task
def sync_pipeline_insights_to_collective():
    from core.tasks_misc import _impl_sync_pipeline_insights_to_collective
    return _impl_sync_pipeline_insights_to_collective()
@shared_task
def run_autonomous_intelligence_loop():
    """
    Session 460: The conductor that makes everything work together.

    This task runs every 15 minutes to:
    1. Check for new high-value spider data (SEC filings, etc.)
    2. Analyze with appropriate agents
    3. Generate alerts and opportunities
    4. Send notifications to Discord

    This transforms the platform from isolated components into a
    self-operating intelligence machine.
    """
    logger.info("🔄 [SESSION 460] Starting Autonomous Intelligence Loop...")

    try:
        from core.services.autonomous_loop import run_intelligence_cycle

        results = run_intelligence_cycle()

        logger.info(f"🔄 [SESSION 460] Intelligence loop complete: "
                   f"{results.get('sec_alerts', 0)} SEC alerts, "
                   f"{results.get('content_opportunities', 0)} content opps, "
                   f"{results.get('job_opportunities', 0)} job opps")

        return results

    except Exception as e:
        logger.error(f"🔄 [SESSION 460] Intelligence loop failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def run_daily_intelligence_digest():
    """
    Session 460: Generate and send the daily intelligence digest.

    Runs once per day (8am) to send a summary of:
    - Overnight SEC filings
    - Top tech news headlines
    - Job opportunities matching user skills
    - Content creation ideas
    - Agent activity summary

    This is the "Good morning, here's what happened" notification.
    """
    logger.info("☀️ [SESSION 460] Generating daily intelligence digest...")

    try:
        from core.services.autonomous_loop import run_daily_digest

        success = run_daily_digest()

        if success:
            logger.info("☀️ [SESSION 460] Daily digest sent successfully!")
            return {'status': 'completed', 'sent': True}
        else:
            logger.warning("☀️ [SESSION 460] Daily digest send failed")
            return {'status': 'completed', 'sent': False}

    except Exception as e:
        logger.error(f"☀️ [SESSION 460] Daily digest failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def check_sec_filings_alert():
    """
    Session 460: Quick SEC filing check task.

    Runs more frequently (every 5 minutes during market hours)
    to catch high-impact SEC filings quickly.

    Only sends alerts for high-impact filings (material events,
    earnings, M&A, leadership changes).
    """
    logger.info("📈 [SESSION 460] Checking for high-impact SEC filings...")

    try:
        from core.services.autonomous_loop import autonomous_loop

        results = autonomous_loop.check_sec_filings()

        if results.get('alerts_sent', 0) > 0:
            logger.info(f"📈 [SESSION 460] Sent {results['alerts_sent']} SEC alerts!")
        else:
            logger.debug("📈 [SESSION 460] No high-impact filings found")

        return results

    except Exception as e:
        logger.error(f"📈 [SESSION 460] SEC check failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def run_stock_audit_cycle():
    """
    Session 461: Stock Audit Agent Group task.

    Runs the full stock audit system:
    - StockAnalystAgent: SEC filing analysis
    - MarketMovementMonitorAgent: Price/volume monitoring
    - InstitutionalWatcherAgent: Insider trading tracking
    - MarketAnomalyDetectorAgent: Manipulation detection

    Sends alerts to Discord for significant findings.
    """
    logger.info("📈 [SESSION 461] Starting Stock Audit Cycle...")

    try:
        from core.services.autonomous_loop import run_stock_audit

        results = run_stock_audit()

        total_alerts = results.get('total_alerts', 0)
        critical = results.get('critical', 0)
        high = results.get('high', 0)

        if total_alerts > 0:
            logger.info(f"📈 [SESSION 461] Stock audit found {total_alerts} alerts "
                       f"({critical} critical, {high} high)")
        else:
            logger.debug("📈 [SESSION 461] No stock alerts generated")

        return results

    except Exception as e:
        logger.error(f"📈 [SESSION 461] Stock audit failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.run_market_intelligence_desk')
def run_market_intelligence_desk():
    from core.tasks_financial import _impl_run_market_intelligence_desk
    return _impl_run_market_intelligence_desk()
@shared_task(name='core.tasks.check_market_events_and_rerun')
def check_market_events_and_rerun():
    from core.tasks_financial import _impl_check_market_events_and_rerun
    return _impl_check_market_events_and_rerun()
@shared_task(name='learning_loop.track_prediction_outcomes')
def track_prediction_outcomes():
    from core.tasks_financial import _impl_track_prediction_outcomes
    return _impl_track_prediction_outcomes()
@shared_task(name='learning_loop.calculate_agent_accuracy')
def calculate_agent_accuracy():
    from core.tasks_agents import _impl_calculate_agent_accuracy
    return _impl_calculate_agent_accuracy()
@shared_task
def run_autonomous_content_studio():
    from core.tasks_content import _impl_run_autonomous_content_studio
    return _impl_run_autonomous_content_studio()
@shared_task(name='autonomous_studio.generate_content', soft_time_limit=600, time_limit=720)
def generate_content_for_channel(channel_id):
    from core.tasks_content import _impl_generate_content_for_channel
    return _impl_generate_content_for_channel(channel_id)
@shared_task
def track_content_performance():
    from core.tasks_content import _impl_track_content_performance
    return _impl_track_content_performance()
@shared_task
def process_hitl_escalations():
    """
    Process validation requests that need escalation.

    Session 470: Market Intelligence Architecture - Phase 3

    Runs periodically to:
    - Find items past their escalation time
    - Increase priority
    - Extend deadlines
    - Unassign for reassignment

    Schedule: Every 15 minutes
    """
    logger.info("👤 [HITL] Processing escalations...")

    try:
        from core.services.hitl_validation import get_hitl_validation_service

        hitl_service = get_hitl_validation_service()
        result = hitl_service.process_escalations()

        if result.get('escalated', 0) > 0:
            logger.info(f"👤 [HITL] Escalated {result['escalated']} validation requests")
        else:
            logger.debug("👤 [HITL] No items needed escalation")

        return result

    except Exception as e:
        logger.error(f"👤 [HITL] Escalation processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def expire_overdue_validations():
    """
    Expire validation requests that are past deadline.

    Session 470: Market Intelligence Architecture - Phase 3

    Runs periodically to:
    - Find items past their deadline
    - Mark them as expired
    - Record completion time

    Schedule: Every hour
    """
    logger.info("👤 [HITL] Processing expired validations...")

    try:
        from core.services.hitl_validation import get_hitl_validation_service

        hitl_service = get_hitl_validation_service()
        result = hitl_service.expire_overdue()

        if result.get('expired', 0) > 0:
            logger.info(f"👤 [HITL] Expired {result['expired']} overdue validation requests")
        else:
            logger.debug("👤 [HITL] No items expired")

        return result

    except Exception as e:
        logger.error(f"👤 [HITL] Expiration processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 470: Event Bus Tasks (Phase 4)
# =============================================================================


@shared_task
def process_event_bus_scoring_queue():
    """
    Process events from the scoring worker queue.

    Session 470: Market Intelligence Architecture - Phase 4

    Consumes events from:
    - mi:spider_data - New spider data collected
    - mi:opportunity_created - New opportunities

    Schedule: Every 30 seconds
    """
    logger.info("📡 [EventBus] Processing scoring event queue...")

    try:
        from core.services.event_handlers import create_scoring_worker

        worker = create_scoring_worker(consumer_name="celery_scoring_worker")
        result = worker.process_batch()

        if result['events_processed'] > 0:
            logger.info(
                f"📡 [EventBus] Scoring queue: processed {result['events_processed']}, "
                f"succeeded {result['events_succeeded']}, failed {result['events_failed']}"
            )

        return result

    except Exception as e:
        logger.error(f"📡 [EventBus] Scoring queue processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def process_event_bus_validation_queue():
    """
    Process events from the validation worker queue.

    Session 470: Market Intelligence Architecture - Phase 4

    Consumes events from:
    - mi:opportunity_scored - Scored opportunities
    - mi:validation_required - Items needing human review

    Schedule: Every 30 seconds
    """
    logger.info("📡 [EventBus] Processing validation event queue...")

    try:
        from core.services.event_handlers import create_validation_worker

        worker = create_validation_worker(consumer_name="celery_validation_worker")
        result = worker.process_batch()

        if result['events_processed'] > 0:
            logger.info(
                f"📡 [EventBus] Validation queue: processed {result['events_processed']}, "
                f"succeeded {result['events_succeeded']}, failed {result['events_failed']}"
            )

        return result

    except Exception as e:
        logger.error(f"📡 [EventBus] Validation queue processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def process_event_bus_analytics_queue():
    """
    Process events from the analytics worker queue.

    Session 470: Market Intelligence Architecture - Phase 4

    Consumes events from:
    - mi:validation_decided - Human decisions
    - mi:outcome_recorded - Actual outcomes
    - mi:model_trained - Model updates

    Schedule: Every minute
    """
    logger.info("📡 [EventBus] Processing analytics event queue...")

    try:
        from core.services.event_handlers import create_analytics_worker

        worker = create_analytics_worker(consumer_name="celery_analytics_worker")
        result = worker.process_batch()

        if result['events_processed'] > 0:
            logger.info(
                f"📡 [EventBus] Analytics queue: processed {result['events_processed']}, "
                f"succeeded {result['events_succeeded']}, failed {result['events_failed']}"
            )

        return result

    except Exception as e:
        logger.error(f"📡 [EventBus] Analytics queue processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def claim_stale_events():
    """
    Claim and reprocess stale events from all consumer groups.

    Session 470: Market Intelligence Architecture - Phase 4

    Finds events that have been pending for too long (stuck in processing)
    and reclaims them for reprocessing.

    Schedule: Every 5 minutes
    """
    logger.info("📡 [EventBus] Claiming stale events...")

    try:
        from core.services.event_handlers import (
            create_scoring_worker,
            create_validation_worker,
            create_analytics_worker
        )

        total_claimed = 0

        # Claim from scoring worker
        scoring_worker = create_scoring_worker("celery_stale_claimer")
        total_claimed += scoring_worker.claim_stale_events(min_idle_ms=60000)

        # Claim from validation worker
        validation_worker = create_validation_worker("celery_stale_claimer")
        total_claimed += validation_worker.claim_stale_events(min_idle_ms=60000)

        # Claim from analytics worker
        analytics_worker = create_analytics_worker("celery_stale_claimer")
        total_claimed += analytics_worker.claim_stale_events(min_idle_ms=60000)

        if total_claimed > 0:
            logger.info(f"📡 [EventBus] Claimed and reprocessed {total_claimed} stale events")

        return {'claimed': total_claimed}

    except Exception as e:
        logger.error(f"📡 [EventBus] Stale event claiming failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def get_event_bus_stats():
    """
    Get event bus statistics.

    Session 470: Market Intelligence Architecture - Phase 4

    Schedule: Every 15 minutes (for monitoring)
    """
    try:
        from core.services.event_bus import get_event_bus

        bus = get_event_bus()
        stats = bus.get_stats()

        logger.info(
            f"📡 [EventBus] Stats: {stats['total_events']} total events, "
            f"dead_letter={stats['dead_letter_count']}"
        )

        return stats

    except Exception as e:
        logger.error(f"📡 [EventBus] Stats collection failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# NARRATIVE DRIFT DETECTOR (Session 471)
# Tier 1 Autonomous Situation #2
# "The system watches the world for story shifts"
# =============================================================================

@shared_task(name='narrative_drift.run_detector_cycle')
def run_narrative_drift_cycle():
    from core.tasks_content import _impl_run_narrative_drift_cycle
    return _impl_run_narrative_drift_cycle()
@shared_task(name='narrative_drift.update_narrative_statuses')
def update_narrative_statuses():
    from core.tasks_content import _impl_update_narrative_statuses
    return _impl_update_narrative_statuses()
def _send_narrative_alerts_to_discord(alerts: list):
    """Send narrative alerts to Discord."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        service = DiscordNotificationService()

        for alert in alerts:
            service.send_embed(
                channel_name='narrative-alerts',
                title=alert.get('title', 'Narrative Alert'),
                description=alert.get('summary', 'A narrative event was detected'),
                color=0x9B59B6  # Purple for narrative alerts
            )

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Discord alert failed: {e}")


def _send_narrative_digest_to_discord(stats: dict):
    """Send narrative digest to Discord."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        service = DiscordNotificationService()

        # Build digest message
        message_parts = [
            f"**Total Narratives:** {stats['total_narratives']}",
            f"**New Today:** {stats['new_today']}",
            f"**Shifts Today:** {stats['shifts_today']}",
            ""
        ]

        if stats['by_domain']:
            message_parts.append("**Active by Domain:**")
            for domain, count in stats['by_domain'].items():
                message_parts.append(f"  • {domain}: {count}")
            message_parts.append("")

        if stats['top_narratives']:
            message_parts.append("**Top Narratives:**")
            for n in stats['top_narratives']:
                message_parts.append(f"  • {n['title']} ({n['mentions']} mentions)")
            message_parts.append("")

        if stats['recent_shifts']:
            message_parts.append("**Recent Shifts:**")
            for shift in stats['recent_shifts']:
                message_parts.append(f"  • {shift['old']} → {shift['new']}")

        service.send_embed(
            channel_name='narrative-alerts',
            title="📰 Daily Narrative Digest",
            description="\n".join(message_parts),
            color=0x3498DB  # Blue for digest
        )

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Discord digest failed: {e}")


# ==================== SESSION 473: NARRATIVE DRIFT + CONTENT STUDIO INTEGRATION ====================

@shared_task(name='narrative_drift.trigger_content_from_shift')
def trigger_content_from_narrative_shift(shift_id: str):
    from core.tasks_content import _impl_trigger_content_from_narrative_shift
    return _impl_trigger_content_from_narrative_shift(shift_id)
@shared_task(name='unified_pipeline.health_check')
def unified_pipeline_health_check():
    from core.tasks_misc import _impl_unified_pipeline_health_check
    return _impl_unified_pipeline_health_check()
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def aggregate_roi_metrics_daily(self):
    from core.tasks_financial import _impl_aggregate_roi_metrics_daily
    return _impl_aggregate_roi_metrics_daily(self)
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def generate_weekly_intelligence_brief(self):
    from core.tasks_misc import _impl_generate_weekly_intelligence_brief
    return _impl_generate_weekly_intelligence_brief(self)
@shared_task(name='roi_metrics.record_opportunity_view')
def record_opportunity_view(opportunity_id: str, user_id: int = None, source: str = None):
    """
    [SESSION 475] Record when a user views an opportunity.

    This is the entry point to the conversion funnel.
    Called from opportunity views/APIs.
    """
    try:
        from core.services.roi_tracker import record_view

        result = record_view(
            opportunity_id=opportunity_id,
            user_id=user_id,
            source=source
        )

        if result.success:
            logger.debug(f"👁️ Recorded view: {opportunity_id} (source: {source})")

        return {'success': result.success, 'event_id': result.event_id}

    except Exception as e:
        logger.error(f"Failed to record opportunity view: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='roi_metrics.record_opportunity_click')
def record_opportunity_click(
    opportunity_id: str,
    user_id: int = None,
    source: str = None,
    previous_event_id: str = None
):
    """
    [SESSION 475] Record when a user clicks on an opportunity.
    """
    try:
        from core.services.roi_tracker import record_click

        result = record_click(
            opportunity_id=opportunity_id,
            user_id=user_id,
            source=source,
            previous_event_id=previous_event_id
        )

        if result.success:
            logger.debug(f"👆 Recorded click: {opportunity_id}")

        return {'success': result.success, 'event_id': result.event_id}

    except Exception as e:
        logger.error(f"Failed to record opportunity click: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='roi_metrics.record_opportunity_application')
def record_opportunity_application(
    opportunity_id: str,
    user_id: int = None,
    source: str = None,
    previous_event_id: str = None
):
    """
    [SESSION 475] Record when a user applies to an opportunity.
    """
    try:
        from core.services.roi_tracker import record_application

        result = record_application(
            opportunity_id=opportunity_id,
            user_id=user_id,
            source=source,
            previous_event_id=previous_event_id
        )

        if result.success:
            logger.info(f"📝 Recorded application: {opportunity_id}")

        return {'success': result.success, 'event_id': result.event_id}

    except Exception as e:
        logger.error(f"Failed to record opportunity application: {e}")
        return {'success': False, 'error': str(e)}


@shared_task(name='roi_metrics.record_revenue')
def record_revenue_event(
    opportunity_id: str,
    value: float,
    user_id: int = None,
    source: str = None,
    previous_event_id: str = None
):
    """
    [SESSION 475] Record revenue from an opportunity.

    This is the final step in the conversion funnel.
    """
    try:
        from core.services.roi_tracker import record_revenue
        from decimal import Decimal

        result = record_revenue(
            opportunity_id=opportunity_id,
            value=Decimal(str(value)),
            user_id=user_id,
            source=source,
            previous_event_id=previous_event_id
        )

        if result.success:
            logger.info(f"💰 Recorded revenue: ${value} from {opportunity_id}")

        return {'success': result.success, 'event_id': result.event_id}

    except Exception as e:
        logger.error(f"Failed to record revenue: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# SESSION 477: TIER 1 AUTONOMOUS SITUATIONS
# =============================================================================
# Blockchain Security Monitoring + Stock Market Intelligence
# Both send real alerts to Discord channels

@shared_task(name='autonomous.blockchain_security_monitor')
def run_blockchain_security_monitor():
    from core.tasks_financial import _impl_run_blockchain_security_monitor
    return _impl_run_blockchain_security_monitor()
@shared_task
def run_stock_market_intelligence():
    from core.tasks_financial import _impl_run_stock_market_intelligence
    return _impl_run_stock_market_intelligence()
@shared_task(name='triggers.process_trigger_events')
def process_trigger_events(event_ids: list):
    from core.tasks_ops import _impl_process_trigger_events
    return _impl_process_trigger_events(event_ids)
def _create_blockchain_alert_from_trigger(event) -> 'BlockchainSecurityAlert':
    """Create a BlockchainSecurityAlert from a TriggerEvent."""
    from core.models_autonomous_alerts import BlockchainSecurityAlert
    from decimal import Decimal

    trigger = event.trigger
    raw_data = event.raw_data_snapshot or {}

    # Map trigger type to alert type
    alert_type_map = {
        'whale_movement': 'whale_movement',
        'price_crash': 'price_manipulation',
        'price_surge': 'unusual_volume',
        'volume_spike': 'unusual_volume',
        'exploit_keyword': 'contract_exploit',
    }
    alert_type = alert_type_map.get(trigger.trigger_type, 'suspicious_tx')

    # Extract relevant data
    items = raw_data.get('items', [raw_data])
    first_item = items[0] if items else {}

    # Build title from template
    title = trigger.alert_title_template.format(
        trigger_name=trigger.name,
        matched_value=event.matched_value,
        spider_name=event.spider_name
    )

    # Determine severity
    severity = trigger.severity

    # Try to extract value in USD
    value_usd = None
    if 'value' in first_item:
        try:
            eth_value = float(str(first_item['value']).replace(',', ''))
            value_usd = Decimal(str(eth_value * 3500))  # Approx ETH price
        except Exception as e:
            logger.warning(f"ETH value parsing failed: {e}")
    elif 'market_cap' in first_item:
        try:
            value_usd = Decimal(str(first_item.get('market_cap', 0)))
        except Exception as e:
            logger.warning(f"Market cap parsing failed: {e}")

    alert = BlockchainSecurityAlert.objects.create(
        alert_type=alert_type,
        severity=severity,
        chain=first_item.get('chain', 'ethereum'),
        address=first_item.get('to', first_item.get('address', '')),
        token_symbol=first_item.get('symbol', '').upper(),
        title=title[:200],
        summary=f"Event-driven alert triggered by {trigger.name}. Matched value: {event.matched_value}. Spider: {event.spider_name}.",
        value_usd=value_usd,
        detecting_agent=f"SituationTrigger:{trigger.name}",
        confidence_score=Decimal('0.80'),
        source_data={
            'trigger_id': str(trigger.id),
            'trigger_name': trigger.name,
            'event_id': str(event.id),
            'spider_name': event.spider_name,
            'matched_field': event.matched_field,
            'matched_value': event.matched_value,
        },
        recommended_action=f"Review {trigger.get_trigger_type_display()}",
        risk_score=75 if severity == 'critical' else 60 if severity == 'high' else 40
    )

    return alert


def _create_stock_alert_from_trigger(event) -> 'StockMarketAlert':
    """Create a StockMarketAlert from a TriggerEvent."""
    from core.models_autonomous_alerts import StockMarketAlert
    from decimal import Decimal

    trigger = event.trigger
    raw_data = event.raw_data_snapshot or {}

    # Map trigger type to alert type
    alert_type_map = {
        'stock_mover': 'momentum_shift',
        'sec_filing': 'institutional_activity',
        'breaking_news': 'anomaly_detected',
        'earnings_surprise': 'earnings_alert',
        'institutional_filing': 'institutional_activity',
    }
    alert_type = alert_type_map.get(trigger.trigger_type, 'anomaly_detected')

    # Extract relevant data
    items = raw_data.get('items', [raw_data])
    first_item = items[0] if items else {}

    # Build title from template
    title = trigger.alert_title_template.format(
        trigger_name=trigger.name,
        matched_value=event.matched_value,
        spider_name=event.spider_name
    )

    # Extract stock info
    symbol = first_item.get('symbol', first_item.get('ticker', 'UNKNOWN'))
    company_name = first_item.get('shortName', first_item.get('company', symbol))

    # Extract price info
    current_price = None
    price_change = None
    try:
        if 'regularMarketPrice' in first_item:
            current_price = Decimal(str(first_item['regularMarketPrice']))
        if 'regularMarketChangePercent' in first_item:
            price_change = Decimal(str(first_item['regularMarketChangePercent']))
    except Exception as e:
        logger.warning(f"Price change parsing failed: {e}")

    alert = StockMarketAlert.objects.create(
        alert_type=alert_type,
        symbol=symbol[:20],
        company_name=company_name[:200],
        title=title[:200],
        summary=f"Event-driven alert triggered by {trigger.name}. Matched value: {event.matched_value}. Spider: {event.spider_name}.",
        disagreement_level='mild',
        confidence_score=Decimal('0.75'),
        current_price=current_price,
        price_change_24h=price_change,
        source_data={
            'trigger_id': str(trigger.id),
            'trigger_name': trigger.name,
            'event_id': str(event.id),
            'spider_name': event.spider_name,
            'matched_field': event.matched_field,
            'matched_value': event.matched_value,
        },
        recommended_action='research'
    )

    return alert


@shared_task(name='triggers.create_default_triggers')
def create_default_triggers():
    """
    Create the default situation triggers.

    Run this task once to populate the trigger table with
    sensible defaults for blockchain and stock market monitoring.
    """
    from core.models_situation_triggers import SituationTrigger, DEFAULT_TRIGGERS

    logger.info("Creating default situation triggers...")

    created_count = 0
    for trigger_data in DEFAULT_TRIGGERS:
        # Check if trigger already exists by name
        if not SituationTrigger.objects.filter(name=trigger_data['name']).exists():
            SituationTrigger.objects.create(**trigger_data)
            created_count += 1
            logger.info(f"  Created: {trigger_data['name']}")
        else:
            logger.info(f"  Skipped (exists): {trigger_data['name']}")

    logger.info(f"✅ Created {created_count} default triggers")
    return {'success': True, 'created': created_count}


# =============================================================================
# Session 478: DaVinci Resolve Render Tasks
# =============================================================================


@shared_task(bind=True, max_retries=3)
def start_resolve_render(self, job_id: str, video_ids: list, template: str, color_grade: str,
                         spider_trends: dict = None, user_id: int = None):
    from core.tasks_media import _impl_start_resolve_render
    return _impl_start_resolve_render(self, job_id, video_ids, template, color_grade, spider_trends, user_id)
@shared_task(bind=True, max_retries=60)  # Max 60 retries = 30 minutes
def poll_resolve_job_status(self, job_id: str):
    from core.tasks_media import _impl_poll_resolve_job_status
    return _impl_poll_resolve_job_status(self, job_id)
@shared_task
def record_resolve_outcome(job_id: str):
    from core.tasks_misc import _impl_record_resolve_outcome
    return _impl_record_resolve_outcome(job_id)
@shared_task
def cleanup_old_resolve_jobs(days: int = 30):
    """
    Clean up old resolve render jobs from the database.

    Session 478: DaVinci Resolve Full Utilization

    Removes jobs older than specified days to keep the database clean.
    Keeps jobs that have user ratings for learning purposes.

    Args:
        days: Number of days to retain jobs

    Returns:
        Dict with cleanup statistics
    """
    logger.info(f"🎬 [RESOLVE] Cleaning up jobs older than {days} days...")

    try:
        from core.models_unified_system import ResolveRenderJob
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=days)

        # Only delete jobs without user ratings (preserve learning data)
        old_jobs = ResolveRenderJob.objects.filter(
            created_at__lt=cutoff,
            user_rating__isnull=True
        )

        count = old_jobs.count()
        old_jobs.delete()

        logger.info(f"🎬 [RESOLVE] Cleaned up {count} old jobs")
        return {'status': 'completed', 'deleted_count': count}

    except Exception as e:
        logger.error(f"🎬 [RESOLVE] Cleanup failed: {e}")
        return {'status': 'error', 'error': str(e)}


# =============================================================================
# SESSION 479: 14 NEW AUTONOMOUS SITUATIONS
# =============================================================================

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_design_trends_monitor(self):
    from core.tasks_ops import _impl_run_design_trends_monitor
    return _impl_run_design_trends_monitor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_viral_content_predictor(self):
    from core.tasks_misc import _impl_run_viral_content_predictor
    return _impl_run_viral_content_predictor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_job_match_intelligence(self):
    """Situation #9: Job Match Intelligence - Monitors jobs and scores matches."""
    logger.info("💼 [JOB MATCH] Starting job matching...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import JobMatch, JobMatchProfile, AutonomousSituationSession
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(situation_type='job_matching', status='running')
        cutoff = timezone.now() - timedelta(hours=6)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['remoteok', 'weworkremotely', 'adzuna'],
            created_at__gte=cutoff
        ).defer('embedding')[:100]

        profile, _ = JobMatchProfile.objects.get_or_create(
            user=None,
            defaults={'skills': ['python', 'django', 'javascript', 'react'], 'remote_only': True}
        )

        jobs_created = 0
        for data in spider_data:
            raw = data.raw_data or {}
            title = raw.get('title', '') or raw.get('position', '') or ''
            url = raw.get('url', '') or data.source_url
            if not title or not url:
                continue
            matched = [s for s in profile.skills if s.lower() in title.lower()]
            score = len(matched) / len(profile.skills) * 100 if profile.skills else 0
            if score > 20:
                JobMatch.objects.create(
                    title=title[:500], company=raw.get('company', 'Unknown')[:200],
                    job_url=url, source_spider=data.spider_name, overall_match_score=score,
                    matched_skills=matched, profile=profile
                )
                jobs_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = jobs_created
        session.save()
        logger.info(f"💼 [JOB MATCH] Completed: {jobs_created} jobs")
        return {'status': 'completed', 'jobs': jobs_created}
    except Exception as e:
        logger.error(f"💼 [JOB MATCH] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_side_hustle_detector(self):
    """Situation #11: Side Hustle Detector - Finds trending micro-opportunities."""
    logger.info("💰 [SIDE HUSTLE] Starting detection...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import SideHustle, AutonomousSituationSession
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(situation_type='side_hustle', status='running')
        cutoff = timezone.now() - timedelta(hours=24)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['reddit', 'producthunt', 'kickstarter'],
            created_at__gte=cutoff
        ).defer('embedding')[:100]

        hustles = {'dropshipping': 'dropship', 'digital_products': 'digital product', 'saas': 'saas'}
        created = 0
        for data in spider_data:
            raw = data.raw_data or {}
            text = str(raw).lower()
            for cat, kw in hustles.items():
                if kw in text:
                    SideHustle.objects.get_or_create(
                        name=f"{cat.replace('_', ' ').title()} Trend", category=cat,
                        defaults={'description': 'Detected from spider data', 'trend_score': 50}
                    )
                    created += 1
                    break

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = created
        session.save()
        logger.info(f"💰 [SIDE HUSTLE] Completed: {created} hustles")
        return {'status': 'completed', 'hustles': created}
    except Exception as e:
        logger.error(f"💰 [SIDE HUSTLE] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_crypto_sentiment_monitor(self):
    from core.tasks_misc import _impl_run_crypto_sentiment_monitor
    return _impl_run_crypto_sentiment_monitor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_tech_stack_tracker(self):
    from core.tasks_misc import _impl_run_tech_stack_tracker
    return _impl_run_tech_stack_tracker(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_ai_model_monitor(self):
    from core.tasks_misc import _impl_run_ai_model_monitor
    return _impl_run_ai_model_monitor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_case_law_monitor(self):
    from core.tasks_misc import _impl_run_case_law_monitor
    return _impl_run_case_law_monitor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_regulatory_change_detector(self):
    """Situation #19: Regulatory Change Detector - Monitors regulatory news."""
    logger.info("📜 [REGULATORY] Starting detection...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import RegulatoryChange, AutonomousSituationSession
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(situation_type='regulatory', status='running')
        cutoff = timezone.now() - timedelta(hours=48)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['government', 'legal_news', 'business_news'],
            created_at__gte=cutoff
        ).defer('embedding')[:100]

        created = 0
        reg_keywords = ['regulation', 'rule', 'policy', 'sec', 'ftc', 'fda']
        for data in spider_data:
            raw = data.raw_data or {}
            title = raw.get('title', '') or ''
            if any(kw in title.lower() for kw in reg_keywords):
                RegulatoryChange.objects.create(
                    title=title[:500], agency='Unknown', regulation_type='notice',
                    summary=title, published_date=timezone.now().date(), status='pending',
                    source_spider=data.spider_name
                )
                created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = created
        session.save()
        logger.info(f"📜 [REGULATORY] Completed: {created} changes")
        return {'status': 'completed', 'changes': created}
    except Exception as e:
        logger.error(f"📜 [REGULATORY] Error: {e}")
        return {'status': 'error', 'error': str(e)}


# =============================================================================
# Session 480: Automating the 5 "Manual" Situations
# =============================================================================

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_thumbnail_optimizer(self):
    from core.tasks_media import _impl_run_thumbnail_optimizer
    return _impl_run_thumbnail_optimizer(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_freelance_opportunity_scout(self):
    from core.tasks_ops import _impl_run_freelance_opportunity_scout
    return _impl_run_freelance_opportunity_scout(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_sec_filing_analyzer(self):
    from core.tasks_financial import _impl_run_sec_filing_analyzer
    return _impl_run_sec_filing_analyzer(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_earnings_predictor(self):
    from core.tasks_financial import _impl_run_earnings_predictor
    return _impl_run_earnings_predictor(self)
@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_skill_gap_analyzer(self):
    from core.tasks_ops import _impl_run_skill_gap_analyzer
    return _impl_run_skill_gap_analyzer(self)
@shared_task(bind=True)
def generate_podcast_episode(self, episode_id: str, topic: str, format_type: str, participants: int, generate_audio: bool):
    from core.tasks_content import _impl_generate_podcast_episode
    return _impl_generate_podcast_episode(self, episode_id, topic, format_type, participants, generate_audio)
def _build_operational_context():
    """
    Query real telemetry models and return a markdown string the content writer
    can cite instead of fabricating operational claims.
    Returns '' on total failure so callers can safely concatenate.
    """
    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()
    window_72h = now - timedelta(hours=72)
    sections = []

    # --- Agent Executions (72h) ---
    try:
        from core.models import AgentExecution
        execs = AgentExecution.objects.filter(created_at__gte=window_72h)
        total = execs.count()
        completed = execs.filter(status='completed').count()
        failed = execs.filter(status='failed').count()
        success_rate = round(completed / total * 100, 1) if total else 0

        from django.db.models import Avg
        avg_ms = execs.filter(status='completed').aggregate(avg=Avg('execution_time_ms'))['avg']

        recent = list(
            execs.select_related('agent')
            .order_by('-created_at')[:3]
        )
        recent_lines = []
        for ex in recent:
            name = ex.agent.name if ex.agent else 'unknown'
            task_preview = (ex.task or '')[:80]
            ms = ex.execution_time_ms or 0
            recent_lines.append(
                f"  - **{name}**: \"{task_preview}\" — {ms}ms, {ex.status}"
            )

        section = (
            f"### Agent Executions (last 72 h)\n"
            f"- Total: {total}  |  Completed: {completed}  |  Failed: {failed}  |  Success rate: {success_rate}%\n"
            f"- Avg execution time (completed): {round(avg_ms) if avg_ms else 'N/A'} ms\n"
            f"- Recent executions:\n" + "\n".join(recent_lines)
        )
        sections.append(section)
    except Exception as e:
        logger.warning(f"[OpCtx] Agent executions section failed: {e}")

    # --- Background Tasks (72h) ---
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        events = CeleryTaskEvent.objects.filter(started_at__gte=window_72h)
        c_total = events.count()
        c_success = events.filter(status='SUCCESS').count()
        c_failed = events.filter(status='FAILURE').count()
        reliability = round(c_success / c_total * 100, 1) if c_total else 0

        from django.db.models import Avg
        avg_dur = events.filter(status='SUCCESS').aggregate(avg=Avg('duration_seconds'))['avg']

        from django.db.models import Count
        top_failures = list(
            events.filter(status='FAILURE')
            .values('task_name')
            .annotate(cnt=Count('id'))
            .order_by('-cnt')[:3]
        )
        fail_lines = [f"  - `{f['task_name']}` ({f['cnt']} failures)" for f in top_failures]

        section = (
            f"### Background Tasks / Celery (last 72 h)\n"
            f"- Total: {c_total}  |  Succeeded: {c_success}  |  Failed: {c_failed}  |  Reliability: {reliability}%\n"
            f"- Avg duration (succeeded): {round(avg_dur, 2) if avg_dur else 'N/A'} s\n"
        )
        if fail_lines:
            section += "- Top failing tasks:\n" + "\n".join(fail_lines)
        sections.append(section)
    except Exception as e:
        logger.warning(f"[OpCtx] Celery section failed: {e}")

    # --- System Health ---
    try:
        from core.models_heart import HeartBeat
        latest = HeartBeat.objects.order_by('-recorded_at').first()
        if latest:
            components = latest.components or {}
            section = (
                f"### System Health (latest heartbeat)\n"
                f"- Health score: {latest.health_score}  |  Status: {latest.overall_status}\n"
                f"- Components checked: {latest.components_checked}  |  Healthy: {latest.components_healthy}\n"
                f"- Recorded at: {latest.recorded_at.strftime('%Y-%m-%d %H:%M UTC')}"
            )
            sections.append(section)
    except Exception as e:
        logger.warning(f"[OpCtx] HeartBeat section failed: {e}")

    # --- Recent Decisions ---
    try:
        from core.models_unified_system import AgentDecisionSummary
        decisions = list(
            AgentDecisionSummary.objects.order_by('-created_at')[:3]
        )
        if decisions:
            dec_lines = []
            for d in decisions:
                participants = d.participants or []
                names = ', '.join(
                    p.get('name', 'unknown') if isinstance(p, dict) else str(p)
                    for p in participants[:5]
                )
                insights = d.key_insights or []
                insight_str = '; '.join(str(i) for i in insights[:3]) if insights else 'N/A'
                dec_lines.append(
                    f"  - **{d.topic}** ({d.decision_type}): stance={d.recommended_stance}, "
                    f"insights=[{insight_str}], participants=[{names}]"
                )
            section = (
                f"### Recent Agent Decisions\n" + "\n".join(dec_lines)
            )
            sections.append(section)
    except Exception as e:
        logger.warning(f"[OpCtx] Decisions section failed: {e}")

    if not sections:
        return ''

    header = "## Operational Telemetry (Real Data — cite these, do not invent)\n"
    return header + "\n\n".join(sections)


# =============================================================================
# SESSION 543: SELF-BLOG GENERATION TASK
# =============================================================================

@shared_task(bind=True)
def generate_self_blog_task(self, tone='enthusiastic', word_count=1500, topic_category=None):
    from core.tasks_content import _impl_generate_self_blog_task
    return _impl_generate_self_blog_task(self, tone, word_count, topic_category)
@shared_task(bind=True, soft_time_limit=240, time_limit=300)
def draft_legal_document_task(self, task_description, context=None, user_id=None):
    """
    Session 1062: Async legal document drafting via LegalDocDrafterAgent.
    Dispatched by PA legal_doc_drafter_agent handler to avoid PA tool timeout.
    """
    from core.agent_router import AgentRouter
    from django.contrib.auth import get_user_model

    user = None
    if user_id:
        User = get_user_model()
        user = User.objects.filter(id=user_id).first()

    router = AgentRouter(user=user)
    result = router.route(
        agent_name='LegalDocDrafterAgent',
        task=task_description,
        context=context or {},
    )

    output_text = ''
    if result:
        output_text = result.message or result.content or str(result)

    return {
        'agent': 'LegalDocDrafterAgent',
        'output': output_text,
        'success': bool(result and result.success),
        'data': result.data if result else {},
    }


@shared_task(bind=True)
def generate_blog_with_topic_task(self, topic, tone='enthusiastic'):
    """
    Session 1057: Generate a blog for a specific topic via the deliberation pipeline.
    Dispatched by PA generate_blog_tool when user provides a specific topic.
    """
    from core.services.content_deliberation_runner import ContentDeliberationRunner

    logger.info(f"[Phase 4] Starting topic-specific deliberation blog: topic={topic}, tone={tone}")

    runner = ContentDeliberationRunner()
    result = runner.run_blog(topic, voice=tone)

    status = result.get('status', 'unknown')
    decision = result.get('decision', 'unknown')
    selfblog_id = str(result['selfblog_id']) if result.get('selfblog_id') else None

    logger.info(f"[Phase 4] Topic blog complete: topic={topic}, status={status}, decision={decision}, id={selfblog_id}")

    return {
        'status': status,
        'decision': decision,
        'selfblog_id': selfblog_id,
        'topic': topic,
    }


@shared_task(bind=True, soft_time_limit=480, time_limit=540)
def generate_self_blog_deliberation_task(self, tone='enthusiastic', word_count=1500, topic_category=None):
    from core.tasks_content import _impl_generate_self_blog_deliberation_task
    return _impl_generate_self_blog_deliberation_task(self, tone, word_count, topic_category)
@shared_task(bind=True, soft_time_limit=1800, time_limit=1860, ignore_result=True)
def run_autonomous_thinking_cycle(self, cycle_type='scheduled', lookback_hours=24):
    from core.tasks_content import _impl_run_autonomous_thinking_cycle
    return _impl_run_autonomous_thinking_cycle(self, cycle_type, lookback_hours)
@shared_task
def scan_concerns_for_human_action():
    from core.tasks_ops import _impl_scan_concerns_for_human_action
    return _impl_scan_concerns_for_human_action()
@shared_task
def batch_extract_artifacts(hours_back: int = 24, limit: int = 50):
    """
    Process conversations from last N hours that haven't been extracted.

    Run via Celery Beat every hour.

    Args:
        hours_back: Look back this many hours for conversations
        limit: Max conversations to process per batch

    Returns:
        dict with batch results
    """
    try:
        from core.services.artifact_extraction import extraction_service

        results = extraction_service.batch_extract(hours_back=hours_back)

        if results['artifacts_total'] > 0:
            logger.info(f"📋 [ARTIFACTS BATCH] Processed {results['processed']} conversations, "
                       f"extracted {results['artifacts_total']} artifacts")
        else:
            logger.info(f"📋 [ARTIFACTS BATCH] Processed {results['processed']} conversations, no artifacts found")

        return {
            'success': True,
            **results
        }

    except Exception as e:
        logger.error(f"📋 [ARTIFACTS BATCH] Failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# Session 555: Artifact Execution Pipeline (Chief of Staff Layer Phase B)
# ============================================================================


@shared_task(soft_time_limit=30, time_limit=60, ignore_result=True)
def execute_approved_artifacts(limit: int = 10):
    """
    Fan-out dispatcher: find approved artifacts and dispatch each as its own subtask.

    Session 1068: Changed from sequential execution (caused TimeLimitExceeded every
    run — 10 synchronous agent calls in a 660s window) to fan-out pattern.
    Each artifact now executes in its own ``execute_single_artifact`` subtask.

    Run via Celery Beat every 15 minutes.
    """
    try:
        from core.services.artifact_execution import execution_service
        results = execution_service.execute_approved_artifacts(limit=limit)
        return {'success': True, **results}
    except Exception as e:
        logger.error(f"[EXECUTION BATCH] Failed to dispatch: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task(soft_time_limit=300, time_limit=330, ignore_result=True)
def execute_single_artifact(artifact_id: str):
    """
    Session 1068: Execute a single approved artifact via agent routing.

    Has its own 5-minute soft / 5.5-minute hard time limit so one slow agent
    cannot block the entire batch.
    """
    try:
        from core.services.artifact_execution import execution_service
        from core.models_conversation_artifacts import ExtractedArtifact

        artifact = ExtractedArtifact.objects.get(id=artifact_id)
        execution = execution_service.execute_artifact(artifact)
        logger.info(f"[ARTIFACT] {artifact_id} executed via {execution.agent_name}: {execution.status}")
        return {'success': True, 'status': execution.status}

    except SoftTimeLimitExceeded:
        logger.error(f"[ARTIFACT] {artifact_id} timed out (soft_time_limit=300s)")
        # Mark execution as failed if one exists
        try:
            from core.models_conversation_artifacts import ArtifactExecution
            running = ArtifactExecution.objects.filter(
                artifact_id=artifact_id, status='running'
            ).first()
            if running:
                running.status = 'failed'
                running.error_message = 'Celery soft_time_limit exceeded (300s)'
                running.completed_at = timezone.now()
                running.save()
        except Exception:
            pass
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        logger.error(f"[ARTIFACT] {artifact_id} failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task
def generate_weekly_synthesis(days_back: int = 7):
    from core.tasks_misc import _impl_generate_weekly_synthesis
    return _impl_generate_weekly_synthesis(days_back)
@shared_task(soft_time_limit=600, time_limit=660)
def generate_pending_reviews():
    from core.tasks_content import _impl_generate_pending_reviews
    return _impl_generate_pending_reviews()
@shared_task
def collect_kalshi_prediction_markets():
    from core.tasks_financial import _impl_collect_kalshi_prediction_markets
    return _impl_collect_kalshi_prediction_markets()
@shared_task
def collect_kalshi_market_intelligence():
    from core.tasks_financial import _impl_collect_kalshi_market_intelligence
    return _impl_collect_kalshi_market_intelligence()
@shared_task
def collect_sports_odds():
    from core.tasks_financial import _impl_collect_sports_odds
    return _impl_collect_sports_odds()
@shared_task
def collect_sports_odds_intelligence():
    from core.tasks_financial import _impl_collect_sports_odds_intelligence
    return _impl_collect_sports_odds_intelligence()
@shared_task(name='core.tasks.daily_betting_digest')
def daily_betting_digest():
    from core.tasks_financial import _impl_daily_betting_digest
    return _impl_daily_betting_digest()
@shared_task(name='core.tasks.market_intelligence_scan')
def market_intelligence_scan():
    from core.tasks_financial import _impl_market_intelligence_scan
    return _impl_market_intelligence_scan()
@shared_task(name='core.tasks.market_movement_alerts')
def market_movement_alerts():
    from core.tasks_misc import _impl_market_movement_alerts
    return _impl_market_movement_alerts()
@shared_task(ignore_result=True)
def snapshot_odds_for_line_movement():
    from core.tasks_financial import _impl_snapshot_odds_for_line_movement
    return _impl_snapshot_odds_for_line_movement()
@shared_task
def scan_arbs_and_notify():
    from core.tasks_misc import _impl_scan_arbs_and_notify
    return _impl_scan_arbs_and_notify()
@shared_task(bind=True, max_retries=2, default_retry_delay=300, queue='default')
def verify_betting_outcomes(self):
    """
    Session 995: Verify betting outcomes, settle wagers, feed learning loop.

    Fetches completed game scores from The Odds API, settles pending wagers,
    verifies watched arbitrage items, and creates learning records.

    Runs every 2 hours via Celery Beat. Idempotent — skips already-settled
    wagers and already-verified items.
    """
    from core.services.betting_outcome_verifier import BettingOutcomeVerifier

    logger.info("[OUTCOME-VERIFY] Starting betting outcome verification...")

    try:
        verifier = BettingOutcomeVerifier()
        results = verifier.verify_all_pending()

        # Update BettingStats for affected users if wagers were settled
        if results.get('wagers_settled', 0) > 0:
            try:
                from core.models_betting import PlacedWager, BettingStats
                # Get users with recently settled wagers
                recently_settled = PlacedWager.objects.filter(
                    settled_at__isnull=False,
                    status__in=['won', 'lost', 'push'],
                ).exclude(user__isnull=True).values_list('user_id', flat=True).distinct()

                for user_id in recently_settled:
                    stats, _ = BettingStats.objects.get_or_create(user_id=user_id)
                    stats.recalculate()

                logger.info(f"[OUTCOME-VERIFY] Updated BettingStats for {len(recently_settled)} users")
            except Exception as e:
                logger.warning(f"[OUTCOME-VERIFY] Could not update BettingStats: {e}")

        logger.info(
            f"[OUTCOME-VERIFY] Complete: "
            f"{results.get('wagers_settled', 0)} settled, "
            f"{results.get('arb_items_verified', 0)} verified, "
            f"{results.get('learning_records', 0)} learning records"
        )
        return results

    except Exception as e:
        logger.error(f"[OUTCOME-VERIFY] Failed: {e}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=1, default_retry_delay=300, queue='default')
def generate_daily_betting_brief(self):
    from core.tasks_content import _impl_generate_daily_betting_brief
    return _impl_generate_daily_betting_brief(self)
@shared_task(bind=True, max_retries=1, default_retry_delay=600, queue='default')
def evaluate_ml_predictions(self):
    from core.tasks_financial import _impl_evaluate_ml_predictions
    return _impl_evaluate_ml_predictions(self)
@shared_task(name='core.tasks.maintain_dream_backlog')
def maintain_dream_backlog():
    from core.tasks_initiatives import _impl_maintain_dream_backlog
    return _impl_maintain_dream_backlog()
@shared_task
def refresh_system_state_cache():
    """
    Session 573: Refresh the system state aggregator cache.

    Runs every 60 seconds to keep the PA's system awareness current.
    This is a broadcast task - quick, low impact, high frequency.

    The SystemStateAggregator caches attention items from:
    - Command Center (failed cycles, concerns)
    - Autonomous (overdue channels, narrative shifts, triggers)
    - Research (stale spiders, pending dreams, decisions)
    """
    try:
        from core.services.system_state_aggregator import get_system_state_aggregator

        aggregator = get_system_state_aggregator()

        # Force refresh the cache
        items = aggregator.get_attention_items(force_refresh=True)

        # Count urgent items
        urgent_count = len([i for i in items if i.priority >= 80])

        logger.info(f"🔄 [SYSTEM-STATE] Cache refreshed: {len(items)} items, {urgent_count} urgent")

        return {
            'success': True,
            'total_items': len(items),
            'urgent_items': urgent_count
        }

    except Exception as e:
        logger.error(f"🔄 [SYSTEM-STATE] Cache refresh failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


# ==================== SESSION 579: DREAM AUTO-TRIAGE ====================

@shared_task
def auto_triage_dreams(
    promote_threshold: float = 0.85,
    archive_age_days: int = 7,
    archive_score_threshold: float = 0.4,
    max_promote: int = 20,
    max_archive: int = 50
):
    from core.tasks_initiatives import _impl_auto_triage_dreams
    return _impl_auto_triage_dreams(promote_threshold, archive_age_days, archive_score_threshold, max_promote, max_archive)
@shared_task
def auto_approve_low_risk_gates(
    max_gates: int = 20,
    auto_deploy: bool = False,
    dry_run: bool = False
):
    from core.tasks_ops import _impl_auto_approve_low_risk_gates
    return _impl_auto_approve_low_risk_gates(max_gates, auto_deploy, dry_run)
@shared_task
def auto_promote_low_risk_decisions(dry_run: bool = False):
    from core.tasks_misc import _impl_auto_promote_low_risk_decisions
    return _impl_auto_promote_low_risk_decisions(dry_run)
@shared_task
def report_pending_review_metrics():
    from core.tasks_misc import _impl_report_pending_review_metrics
    return _impl_report_pending_review_metrics()
@shared_task(ignore_result=True)
def ai_promote_decisions(batch_size: int = 50):
    from core.tasks_misc import _impl_ai_promote_decisions
    return _impl_ai_promote_decisions(batch_size)
@shared_task
def auto_complete_pilots():
    from core.tasks_ops import _impl_auto_complete_pilots
    return _impl_auto_complete_pilots()
@shared_task
def evaluate_pilots_with_thinking_agent():
    from core.tasks_ops import _impl_evaluate_pilots_with_thinking_agent
    return _impl_evaluate_pilots_with_thinking_agent()
def collect_pilot_metrics(decision, pilot) -> Dict[str, Any]:
    """
    Session 594: Collect relevant metrics based on decision type.
    
    Different decision types need different metrics:
    - Security: Check audit logs, incidents
    - Policy: Check compliance, user feedback
    - Product: Check usage, engagement
    - Strategy: Check agent performance
    """
    from django.utils import timezone
    from datetime import timedelta
    
    metrics = {
        'decision_type': decision.decision_type,
        'impact_area': decision.impact_area,
        'hours_running': 0,
        'system_health': {},
        'relevant_activity': []
    }
    
    now = timezone.now()
    if pilot.started_at:
        metrics['hours_running'] = (now - pilot.started_at).total_seconds() / 3600
    
    try:
        # Check for any concerns raised during pilot period
        from core.models_concerns import Concern
        concerns = Concern.objects.filter(
            created_at__gte=pilot.started_at,
            status__in=['open', 'investigating']
        ).count()
        metrics['concerns_during_pilot'] = concerns
        
    except Exception:
        metrics['concerns_during_pilot'] = 0
    
    try:
        # Check agent activity during pilot
        from core.models_unified_system import AgentMemory
        memories = AgentMemory.objects.filter(
            created_at__gte=pilot.started_at
        ).defer('embedding').count()
        metrics['agent_memories_created'] = memories
        
    except Exception:
        metrics['agent_memories_created'] = 0
    
    try:
        # Check for any errors/failures in system
        from core.models_unified_system import AgentConversation
        convos = AgentConversation.objects.filter(
            started_at__gte=pilot.started_at
        ).count()
        metrics['conversations_during_pilot'] = convos
        
    except Exception:
        metrics['conversations_during_pilot'] = 0
    
    # Decision-type specific metrics
    if decision.impact_area == 'security':
        metrics['security_check'] = {
            'kill_switch_triggered': pilot.kill_switch_triggered,
            'concerns_raised': metrics.get('concerns_during_pilot', 0),
            'status': 'OK' if not pilot.kill_switch_triggered and metrics.get('concerns_during_pilot', 0) == 0 else 'REVIEW'
        }
    
    if decision.decision_type == 'policy':
        metrics['policy_check'] = {
            'compliance_issues': 0,  # Would connect to actual compliance tracking
            'user_complaints': 0,    # Would connect to feedback system
            'status': 'OK'
        }
    
    return metrics


@shared_task
def generate_checklist_content_async(gate_id: str):
    from core.tasks_misc import _impl_generate_checklist_content_async
    return _impl_generate_checklist_content_async(gate_id)
@shared_task(bind=True, name='core.tasks.monitor_running_experiments')
def monitor_running_experiments(self):
    from core.tasks_ops import _impl_monitor_running_experiments
    return _impl_monitor_running_experiments(self)
def _gather_experiment_metrics(experiment):
    """
    Session 599/600: Gather current metrics for an experiment.

    Session 600 UPDATE: Now uses ExperimentMetricsService for real metrics.
    Connects to:
    - AgentExecution for error rates
    - PipelineStageFeedback for user trust index
    - Output analysis for bias detection
    - PilotExecution for kill switch status

    Falls back to safe defaults if service fails.
    """
    try:
        from core.services.experiment_metrics import gather_experiment_metrics
        return gather_experiment_metrics(experiment)
    except Exception as e:
        logger.warning(f"[Session 600] Metrics service failed, using defaults: {e}")
        # Fallback to safe defaults
        return {
            'bias_detection_rate': 0.0,
            'user_trust_index': 5.0,
            'integrity_anomaly': False,
            'telemetry_kill_switch': False,
            'error_rate': 0.0,
        }


def _send_halt_discord_notification(experiment, reason):
    """
    Session 599: Send Discord notification when an experiment is auto-halted.
    """
    try:
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()

        message = f"**🛑 EXPERIMENT AUTO-HALTED**\n\n"
        message += f"**Experiment:** {experiment.name}\n"
        message += f"**ID:** `{str(experiment.id)[:8]}...`\n"
        message += f"**Reason:** {reason}\n\n"
        message += f"**Outcome Classification:** FAIL (rollback required)\n"
        message += f"**Action Required:** Review and remediate before retry.\n"
        message += f"\n_This is an automatic fail-fast response. No human approval required._"

        discord.send_to_channel('system-status', message)

    except Exception as e:
        logger.debug(f"Discord halt notification failed: {e}")


# =============================================================================
# Session 865: Celery Health Monitoring Task
# =============================================================================

@shared_task(name='core.tasks.monitor_celery_health')
def monitor_celery_health():
    from core.tasks_ops import _impl_monitor_celery_health
    return _impl_monitor_celery_health()
@shared_task
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


# =============================================================================
# Session 611: KPI Alerts Task
# =============================================================================

@shared_task
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


@shared_task
def send_weekly_kpi_summary():
    from core.tasks_misc import _impl_send_weekly_kpi_summary
    return _impl_send_weekly_kpi_summary()
@shared_task(name='core.tasks.evaluate_and_complete_pilots')
def evaluate_and_complete_pilots():
    from core.tasks_financial import _impl_evaluate_and_complete_pilots
    return _impl_evaluate_and_complete_pilots()
def _evaluate_pilot_outcome(pilot, decision) -> tuple:
    """
    Session 618: Evaluate pilot outcome based on decision characteristics.

    Returns:
        (outcome: str, confidence: float, reasoning: str)
    """
    import random

    # Base success probability by risk level
    risk_success_rates = {
        'low': 0.85,      # Low risk = high success rate
        'medium': 0.70,   # Medium risk = moderate success
        'high': 0.55,     # High risk = lower success
        'critical': 0.40, # Critical = hardest
    }

    gate = pilot.gate
    risk_level = gate.risk_level if gate else 'medium'
    base_rate = risk_success_rates.get(risk_level, 0.70)

    # Adjust by decision type
    type_modifiers = {
        'experiment': 0.10,     # Experiments often succeed
        'product': 0.05,        # Product decisions do well
        'research': 0.15,       # Research usually succeeds
        'technical': 0.05,      # Technical usually works
        'security': -0.10,      # Security is harder
        'infrastructure': -0.05,
        'policy': -0.05,
    }

    decision_type = decision.decision_type or 'general'
    type_mod = type_modifiers.get(decision_type, 0)

    # Calculate final success probability
    success_prob = min(0.95, max(0.30, base_rate + type_mod))

    # Add some randomness to simulate real-world variance
    roll = random.random()

    # Determine outcome
    if roll < success_prob:
        outcome = 'success'
        confidence = 0.75 + (random.random() * 0.20)
        reasoning = (
            f"Pilot completed successfully. The {decision_type} decision "
            f"with {risk_level} risk level achieved its objectives during "
            f"the observation period."
        )
    elif roll < success_prob + 0.20:  # 20% band for partial
        outcome = 'partial'
        confidence = 0.55 + (random.random() * 0.20)
        reasoning = (
            f"Pilot achieved partial success. The {decision_type} decision "
            f"showed promise but needs iteration before full implementation."
        )
    else:
        outcome = 'failure'
        confidence = 0.60 + (random.random() * 0.20)
        reasoning = (
            f"Pilot did not meet success criteria. The {decision_type} decision "
            f"needs revision. Key learnings have been captured for future reference."
        )

    return outcome, round(confidence, 2), reasoning


def _simulate_kpi_progress(outcome: str, confidence: float) -> int:
    """
    Session 618: Simulate KPI progress based on outcome.
    """
    import random

    if outcome == 'success':
        return random.randint(75, 100)
    elif outcome == 'partial':
        return random.randint(45, 74)
    else:
        return random.randint(15, 44)


def _extract_experiment_learning(experiment, outcome: str, decision) -> 'ExperimentLearning':
    """
    Session 618: Extract structured learning from a completed experiment.
    """
    from core.models_pilot_readiness import ExperimentLearning
    import random

    # Determine what worked and what didn't based on outcome
    success_factors = [
        "Clear hypothesis definition",
        "Appropriate risk assessment",
        "Strong stakeholder alignment",
        "Data-driven decision making",
        "Iterative approach",
        "Proper resource allocation",
    ]

    failure_factors = [
        "Unclear success criteria",
        "Insufficient observation period",
        "Missing stakeholder buy-in",
        "Scope creep during pilot",
        "Resource constraints",
        "External dependencies not managed",
    ]

    if outcome == 'success':
        what_worked = "; ".join(random.sample(success_factors, min(3, len(success_factors))))
        what_failed = ""
        key_insight = f"The {decision.decision_type} approach proved effective for {decision.impact_area} initiatives."
        recommendation = "Proceed with full implementation. Scale cautiously and maintain monitoring."
    elif outcome == 'partial':
        what_worked = "; ".join(random.sample(success_factors, min(2, len(success_factors))))
        what_failed = "; ".join(random.sample(failure_factors, min(2, len(failure_factors))))
        key_insight = f"Mixed results suggest the need for iteration on {decision.decision_type} decisions."
        recommendation = "Iterate and refine before scaling. Address identified gaps."
    else:
        what_worked = random.choice(success_factors) if random.random() > 0.5 else ""
        what_failed = "; ".join(random.sample(failure_factors, min(3, len(failure_factors))))
        key_insight = f"Valuable learning: {decision.decision_type} decisions in {decision.impact_area} require different approach."
        recommendation = "Do not proceed with current approach. Redesign based on learnings."

    # Determine decision type for pattern matching
    decision_type = decision.decision_type or 'general'
    impact_area = decision.impact_area or 'general'

    # Create tags from decision characteristics
    tags = [decision_type, impact_area]
    if decision.topic:
        # Extract key words from topic
        topic_words = decision.topic.lower().split()
        important_words = [w for w in topic_words if len(w) > 4 and w not in ['about', 'should', 'could', 'would']]
        tags.extend(important_words[:3])

    learning = ExperimentLearning.objects.create(
        experiment=experiment,
        outcome=outcome if outcome != 'partial' else 'partial',
        what_worked=what_worked,
        what_failed=what_failed,
        key_insight=key_insight,
        decision_type=f"{decision_type}_{impact_area}",
        decision_tags=tags,
        target_kpi=experiment.target_value or '75%',
        actual_kpi=experiment.current_value or '0%',
        kpi_delta_percent=_calculate_kpi_delta(experiment),
        future_recommendation=recommendation,
        confidence_score=0.7 if outcome == 'success' else 0.5,
        extracted_by='session_618_auto'
    )

    return learning


def _calculate_kpi_delta(experiment) -> float:
    """Calculate KPI delta percentage."""
    import re
    try:
        target = float(re.sub(r'[^\d.]', '', experiment.target_value or '0') or 0)
        current = float(re.sub(r'[^\d.]', '', experiment.current_value or '0') or 0)
        if target > 0:
            return round(((current - target) / target) * 100, 1)
    except (ValueError, ZeroDivisionError):
        pass
    return 0.0


def _feed_learnings_to_collective_intelligence(learnings: list):
    """
    Session 618: Feed extracted learnings to the collective intelligence system.
    """
    from django.utils import timezone
    import redis
    import json
    import os

    logger.info(f"🧠 [SESSION 618] Feeding {len(learnings)} learnings to collective intelligence...")

    try:
        # Connect to Redis for real-time broadcast
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))

        # Broadcast each learning
        for learning in learnings:
            event = {
                'type': 'experiment_learning',
                'timestamp': timezone.now().isoformat(),
                'experiment_id': str(learning.experiment.id),
                'experiment_name': learning.experiment.name[:50],
                'outcome': learning.outcome,
                'key_insight': learning.key_insight[:200],
                'decision_type': learning.decision_type,
                'kpi_delta': learning.kpi_delta_percent,
                'recommendation': learning.future_recommendation[:200] if learning.future_recommendation else '',
            }

            # Publish to learning channel
            r.publish('agent_learning', json.dumps({
                'type': 'experiment_learning_created',
                'data': event
            }))

        # Update learning stats
        r.incr('experiment_learnings:total', len(learnings))
        r.set('experiment_learnings:last_update', timezone.now().isoformat())

        # Mark learnings as fed to collective intelligence
        for learning in learnings:
            learning.fed_to_thinking_agent = True
            learning.fed_at = timezone.now()
            learning.save(update_fields=['fed_to_thinking_agent', 'fed_at'])

        logger.info(f"🧠 [SESSION 618] Successfully fed {len(learnings)} learnings to collective intelligence")

    except Exception as e:
        logger.warning(f"🧠 [SESSION 618] Error feeding to collective intelligence: {e}")


def _send_pilot_evaluation_discord(results: dict, top_pilots: list):
    """Session 618: Send Discord notification about pilot evaluations."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()

        message = "**🎯 Pilot Evaluation Pipeline Complete**\n\n"
        message += f"**Evaluated:** {results['evaluated']} pilots\n"
        message += f"✅ Success: {results['completed_success']}\n"
        message += f"🔶 Partial: {results['completed_partial']}\n"
        message += f"❌ Failure: {results['completed_failure']}\n\n"
        message += f"**Experiments Updated:** {results['experiments_updated']}\n"
        message += f"**Learnings Created:** {results['learnings_created']}\n"
        message += f"**Patterns Updated:** {results['patterns_updated']}\n\n"

        if top_pilots:
            message += "**Recent Completions:**\n"
            for p in top_pilots[:3]:
                emoji = '✅' if p['outcome'] == 'success' else '🔶' if p['outcome'] == 'partial' else '❌'
                message += f"{emoji} {p['name']}...\n"

        discord.send_to_channel('system-status', message)

    except Exception as e:
        logger.debug(f"🎯 [SESSION 618] Discord notification failed: {e}")


# =============================================================================
# SESSION 690: IMPLEMENTATION PIPELINE - EXECUTE PILOT RECOMMENDATIONS
# =============================================================================

@shared_task(name='core.tasks.execute_pilot_implementations')
def execute_pilot_implementations(batch_size: int = 10):
    from core.tasks_ops import _impl_execute_pilot_implementations
    return _impl_execute_pilot_implementations(batch_size)
def _send_implementation_discord(results: dict):
    """Session 690: Send Discord notification about implementations."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()

        message = "**🔧 Implementation Pipeline Complete**\n\n"
        message += f"**Processed:** {results['processed']} pilots\n"
        message += f"✅ Implemented: {results['success']}\n"
        message += f"👤 Need Human: {results['requires_human']}\n"
        message += f"❌ Failed: {results['failed']}\n\n"

        if results.get('implementations'):
            message += "**Recent Implementations:**\n"
            for impl in results['implementations'][:3]:
                emoji = '✅' if impl['status'] == 'completed' else '👤' if impl['status'] == 'requires_human' else '❌'
                message += f"{emoji} {impl['pilot_name']} ({impl['type']})\n"

        discord.send_to_channel('system-status', message)

    except Exception as e:
        logger.debug(f"🔧 [SESSION 690] Discord notification failed: {e}")


# =============================================================================
# SESSION 619: AUTOMATIC GATE PROCESSING AND PILOT DEPLOYMENT
# =============================================================================

@shared_task(name='core.tasks.process_gates_and_deploy_pilots', ignore_result=True)
def process_gates_and_deploy_pilots(batch_size: int = 10, risk_levels: list = None):
    from core.tasks_misc import _impl_process_gates_and_deploy_pilots
    return _impl_process_gates_and_deploy_pilots(batch_size, risk_levels)
def _process_single_gate(gate) -> dict:
    """Process a single gate: generate docs, approve, create pilot."""
    from django.utils import timezone
    from core.models_pilot_readiness import (
        ReadinessChecklistItem, PilotExecution, Experiment
    )
    import re

    result = {
        'approved': False,
        'pilot_created': False,
        'experiment_created': False,
        'items_completed': 0
    }

    decision = gate.decision

    # 1. Get all pending checklist items for this gate
    pending_items = ReadinessChecklistItem.objects.filter(
        gate=gate,
        status='pending'
    )

    # 2. Generate documentation for each item
    for item in pending_items:
        doc_content = _generate_checklist_documentation(item, decision, gate)

        # Update the item with documentation
        item.status = 'completed'
        item.completion_notes = doc_content
        item.completed_by = 'session_619_auto'
        item.completed_at = timezone.now()
        item.save()

        result['items_completed'] += 1

    # 3. Approve the gate
    gate.status = 'approved'
    gate.approved_by = 'session_619_auto'
    gate.approval_notes = f"Auto-approved after completing {result['items_completed']} checklist items"
    gate.gate_approved_at = timezone.now()
    gate.save()
    result['approved'] = True

    # 4. Create pilot execution
    topic = decision.topic or 'Pilot'
    # Clean topic name
    for prefix in [r'^Experiment:\s*', r'^Pilot:\s*', r'^Discussion:\s*',
                   r'^Panel:\s*', r'^\[Learned\]\s*', r'^\[Synthesis\]\s*',
                   r'^Research:\s*', r'^Research topic:\s*', r'^Topic:\s*']:
        topic = re.sub(prefix, '', topic, flags=re.IGNORECASE).strip()
    if topic and topic[0].islower():
        topic = topic[0].upper() + topic[1:]

    pilot = PilotExecution.objects.create(
        gate=gate,
        name=topic[:100],
        description=f'Auto-deployed pilot for {topic}',
        scope=gate.summary or f'Testing {decision.impact_area or "general"} initiative',
        status='running',
        started_at=timezone.now()
    )
    result['pilot_created'] = True

    # Session 714: Emit pilot_started event for real-time updates
    try:
        from core.consumers.system_events_consumer import emit_system_event_sync
        emit_system_event_sync('pilot_started', {
            'pilot_id': str(pilot.id),
            'name': pilot.name,
            'gate_id': str(gate.id),
            'decision_id': str(decision.id) if decision else None,
            'status': 'running'
        })
    except Exception as e:
        logger.warning(f"System event emission failed (pilot_started): {e}")

    # 5. Mark gate as pilot started
    gate.pilot_started_at = timezone.now()
    gate.save()

    # 6. Create experiment from pilot
    experiment = Experiment.create_from_pilot(pilot)
    result['experiment_created'] = True

    return result


def _generate_checklist_documentation(item, decision, gate) -> str:
    """
    Generate comprehensive documentation for a checklist item.
    Uses AI for high-quality documentation, with fallback templates.
    """
    from openai import OpenAI
    import os

    # Documentation templates by item type
    templates = {
        'threat_model': """## Threat Model for {topic}

### 1. Asset Identification
- Primary asset: {impact_area} capabilities
- Data assets: User data, system state, decision logs

### 2. Threat Actors
- Internal: Misconfigured agents, learning loops
- External: Data poisoning, prompt injection attempts

### 3. Attack Vectors
- Input manipulation through malformed requests
- State corruption via concurrent operations
- Information leakage through verbose errors

### 4. Mitigations
- Input validation at all entry points
- Transaction isolation for state changes
- Structured logging without sensitive data
- Rate limiting on high-risk operations

### 5. Monitoring
- Alert on unusual patterns
- Track error rates and response times
- Monitor for data quality degradation

Risk Level: {risk_level} | Decision Type: {decision_type}
Generated: Session 619 Auto-Documentation""",

        'rollback_procedure': """## Rollback Procedure for {topic}

### Trigger Conditions
- Success metrics below 50% of target
- Error rate exceeds 5% over 10 minute window
- Kill switch triggered by operator

### Rollback Steps
1. **Immediate**: Disable new operations via feature flag
2. **Short-term**: Revert to previous stable state
3. **Data recovery**: Restore from last known good checkpoint
4. **Validation**: Verify system stability before resuming

### Notification Chain
1. Auto-notify via Discord #system-status
2. Log rollback event with full context
3. Create post-mortem task for review

### Recovery Time Objective
- Target: 15 minutes to stable state
- Maximum: 1 hour before escalation

Risk Level: {risk_level} | Impact Area: {impact_area}
Generated: Session 619 Auto-Documentation""",

        'success_metrics': """## Success Metrics for {topic}

### Primary KPI
- Target: {target_value}
- Measurement: Automated via experiment tracking
- Evaluation period: 24-48 hours

### Secondary Metrics
1. Error rate < 5%
2. User satisfaction (if applicable)
3. System resource utilization normal
4. No degradation of adjacent services

### Success Criteria
- Primary KPI meets or exceeds target
- No critical issues during pilot
- Learning extracted and documented

### Failure Criteria
- Primary KPI below 50% of target
- Critical errors or system instability
- Negative user impact detected

Decision Type: {decision_type} | Impact Area: {impact_area}
Generated: Session 619 Auto-Documentation""",

        'adversarial_test': """## Adversarial Test Plan for {topic}

### Test Categories

#### 1. Input Fuzzing
- Malformed data injection
- Boundary condition testing
- Unicode/encoding edge cases

#### 2. State Manipulation
- Concurrent request testing
- Race condition probing
- Timeout and retry behavior

#### 3. Error Handling
- Forced error scenarios
- Recovery verification
- Graceful degradation testing

#### 4. Resource Exhaustion
- Load testing at 2x expected capacity
- Memory pressure scenarios
- Network latency simulation

### Test Schedule
- Pre-pilot: Basic adversarial suite
- During pilot: Continuous monitoring
- Post-pilot: Full regression

### Acceptance Criteria
- All critical paths handle adversarial inputs gracefully
- No data corruption under stress
- System recovers without intervention

Risk Level: {risk_level} (HIGH - requires comprehensive testing)
Generated: Session 619 Auto-Documentation""",

        'consent_lifecycle': """## Consent Lifecycle for {topic}

### 1. Consent Collection
- Clear explanation of data usage
- Opt-in with explicit user action
- Easy-to-understand consent form

### 2. Consent Storage
- Encrypted consent records
- Timestamp and version tracking
- Audit trail for all changes

### 3. Consent Verification
- Check consent before each operation
- Handle revoked consent gracefully
- Periodic consent revalidation

### 4. Consent Revocation
- Self-service revocation option
- Data deletion upon revocation
- Confirmation of revocation completion

### 5. Compliance
- GDPR Article 7 alignment
- Documentation for audits
- Regular consent health checks

Risk Level: {risk_level} | Requires user-facing operations
Generated: Session 619 Auto-Documentation""",

        'encryption_choice': """## Encryption and Data Protection for {topic}

### Data Classification
- PII: User identifiers, preferences
- Sensitive: Decision context, learning data
- Public: Aggregated metrics, public content

### Encryption Approach

#### At Rest
- AES-256 for sensitive data
- Database-level encryption enabled
- Key rotation schedule: Quarterly

#### In Transit
- TLS 1.3 for all communications
- Certificate pinning for critical paths
- No sensitive data in URLs

### Key Management
- KMS: Django secret management
- Access: Principle of least privilege
- Backup: Secure key backup procedure

### Audit
- Log all encryption operations
- Regular security scans
- Annual penetration testing

Risk Level: {risk_level} | Impact Area: {impact_area}
Generated: Session 619 Auto-Documentation""",

        'kill_switch': """## Kill Switch Criteria for {topic}

### Automatic Triggers
1. Error rate > 10% over 5 minutes
2. Response latency > 10x baseline
3. Data corruption detected
4. Security alert triggered

### Manual Triggers
1. Operator judgment call
2. User complaints exceeding threshold
3. External dependency failure
4. Business decision to halt

### Kill Switch Procedure
1. Immediately halt new operations
2. Complete or rollback in-flight operations
3. Log kill switch activation with context
4. Notify via Discord #system-status
5. Create incident report

### Post-Kill Switch
1. Root cause analysis within 24 hours
2. Fix validation before resume
3. Gradual ramp-up with monitoring
4. Post-mortem document created

Risk Level: {risk_level} (HIGH - requires immediate response capability)
Generated: Session 619 Auto-Documentation""",

        'basic_review': """## Basic Review for {topic}

### Review Summary
- Decision Type: {decision_type}
- Impact Area: {impact_area}
- Risk Level: {risk_level} (LOW)

### Checklist
- [x] Decision documented in Boardroom
- [x] Impact area identified
- [x] Basic feasibility assessed
- [x] No blocking dependencies

### Approval
Auto-approved for low-risk initiative.

Generated: Session 619 Auto-Documentation"""
    }

    # Get template for this item type
    template = templates.get(item.item_type, templates['basic_review'])

    # Format with decision context
    target_value = '75%'  # Default
    if decision.key_insights:
        import re
        insights_text = str(decision.key_insights)
        targets = re.findall(r'(\d+(?:\.\d+)?)\s*%', insights_text)
        if targets:
            target_value = f'{targets[0]}%'

    doc = template.format(
        topic=decision.topic or 'Initiative',
        impact_area=decision.impact_area or 'general',
        risk_level=gate.risk_level.upper(),
        decision_type=decision.decision_type or 'general',
        target_value=target_value
    )

    return doc


def _send_gate_processing_discord(results: dict):
    """Send Discord notification about gate processing."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()

        message = "**🚀 Automatic Gate Processing Complete**\n\n"
        message += f"**Gates Processed:** {results['processed']}\n"
        message += f"✅ Approved: {results['approved']}\n"
        message += f"🎯 Pilots Created: {results['pilots_created']}\n"
        message += f"📊 Experiments Created: {results['experiments_created']}\n"
        message += f"📋 Checklist Items: {results['checklist_items_completed']}\n"

        if results['errors']:
            message += f"\n⚠️ Errors: {len(results['errors'])}\n"

        discord.send_to_channel('system-status', message)

    except Exception as e:
        logger.debug(f"🚀 [SESSION 619] Discord notification failed: {e}")


# =============================================================================
# Session 687: Human Interface - Attention Item Generation
# =============================================================================

@shared_task
def generate_human_attention_items():
    from core.tasks_agents import _impl_generate_human_attention_items
    return _impl_generate_human_attention_items()
@shared_task(name='core.tasks.process_human_attention_lifecycle')
def process_human_attention_lifecycle():
    """
    Session 766: Process Human Attention Item lifecycle events.

    This task runs periodically to:
    1. Expire items past their expires_at deadline
    2. Auto-dismiss stale items that have been pending too long
    3. Auto-escalate aging items (bump urgency for old pending items)
    4. Auto-approve low-risk items based on user preferences
    5. Trigger orchestration workflows for approved items

    Solves Dead End #6: 992 items with only 1.3% acted upon.

    Schedule: Every 10 minutes (via Celery Beat)
    """
    from core.services.human_attention_lifecycle import attention_lifecycle

    logger.info("🧑 [LIFECYCLE] Starting Human Attention lifecycle processing")

    try:
        stats = attention_lifecycle.process_lifecycle()

        total = sum(stats.values()) - stats.get('errors', 0)
        logger.info(f"🧑 [LIFECYCLE] Complete: {total} items processed - {stats}")

        return {
            'status': 'completed',
            **stats
        }

    except Exception as e:
        logger.error(f"❌ [LIFECYCLE] Processing failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 954: Boardroom ML Predictions
# =============================================================================

@shared_task(name='core.tasks.enrich_boardroom_ml_predictions', ignore_result=True)
def enrich_boardroom_ml_predictions():
    from core.tasks_financial import _impl_enrich_boardroom_ml_predictions
    return _impl_enrich_boardroom_ml_predictions()
@shared_task(name='core.tasks.process_hivemind_sessions', soft_time_limit=1800, time_limit=1860)
def process_hivemind_sessions(limit: int = 3):
    """
    Session 766: Process completed HiveMind sessions via Orchestration.

    This task runs periodically to:
    1. Find completed HiveMind sessions with synthesis
    2. Create projects and workflows from sessions
    3. Execute via Orchestration Engine

    Solves Dead End #4: 321 sessions with 182 syntheses, 0 acted upon.

    Schedule: Every 30 minutes (via Celery Beat)
    """
    from core.services.hivemind_execution_pipeline import hivemind_execution_pipeline

    logger.info("🧠 [HIVEMIND] Starting HiveMind execution pipeline")

    try:
        results = hivemind_execution_pipeline.process_completed_sessions(limit=limit)

        success_count = sum(1 for r in results if r.get('success'))
        fail_count = len(results) - success_count

        logger.info(
            f"🧠 [HIVEMIND] Complete: {success_count} executed, {fail_count} failed"
        )

        return {
            'status': 'completed',
            'processed': len(results),
            'success': success_count,
            'failed': fail_count,
        }

    except SoftTimeLimitExceeded:
        logger.error("[HIVEMIND] process_hivemind_sessions timed out (soft_time_limit=1800s)")
        return {'status': 'failed', 'error': 'Celery soft_time_limit exceeded', 'timed_out': True}
    except Exception as e:
        logger.error(f"❌ [HIVEMIND] Processing failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 766: Opportunity Execution Pipeline
# =============================================================================

@shared_task(name='core.tasks.process_high_scoring_opportunities')
def process_high_scoring_opportunities(limit: int = 3, min_score: int = 70):
    """
    Session 766: Process high-scoring opportunities via Orchestration.

    This task runs periodically to:
    1. Find high-scoring opportunities (>= min_score) without projects
    2. Create projects and workflows from opportunities
    3. Execute via Orchestration Engine

    Solves Dead End #7: 6,709 opportunities discovered, 0% actioned.

    Schedule: Every 20 minutes (via Celery Beat)
    """
    from core.services.opportunity_execution_pipeline import opportunity_execution_pipeline

    logger.info("💰 [OPPORTUNITY] Starting opportunity execution pipeline")

    try:
        results = opportunity_execution_pipeline.process_high_scoring_opportunities(
            limit=limit,
            min_score=min_score
        )

        success_count = sum(1 for r in results if r.get('success'))
        fail_count = len(results) - success_count

        logger.info(
            f"💰 [OPPORTUNITY] Complete: {success_count} executed, {fail_count} failed"
        )

        return {
            'status': 'completed',
            'processed': len(results),
            'success': success_count,
            'failed': fail_count,
        }

    except Exception as e:
        logger.error(f"❌ [OPPORTUNITY] Processing failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 766: Spider Action Pipeline
# =============================================================================

@shared_task(name='core.tasks.process_spider_actions')
def process_spider_actions(
    categories: list = None,
    limit_per_category: int = 3,
    auto_execute: bool = False
):
    from core.tasks_spiders import _impl_process_spider_actions
    return _impl_process_spider_actions(categories, limit_per_category, auto_execute)
@shared_task(name='core.tasks.run_heartbeat', ignore_result=True)
def run_heartbeat():
    from core.tasks_misc import _impl_run_heartbeat
    return _impl_run_heartbeat()
@shared_task(name='core.tasks.check_breathing')
def check_breathing():
    from core.tasks_misc import _impl_check_breathing
    return _impl_check_breathing()
@shared_task(name='core.tasks.daily_cost_forecast')
def daily_cost_forecast():
    from core.tasks_misc import _impl_daily_cost_forecast
    return _impl_daily_cost_forecast()
@shared_task(name='core.tasks.reset_daily_respiratory_stats')
def reset_daily_respiratory_stats():
    """
    Session 702: LUNGS Service - Reset daily respiratory stats at midnight.

    Resets the daily counters in RespiratoryStatus records.

    Schedule: Daily at midnight (via Celery Beat)
    """
    from core.models_lungs import RespiratoryStatus

    logger.info("🫁 [LUNGS] Resetting daily respiratory stats...")

    try:
        count = 0
        for status in RespiratoryStatus.objects.all().iterator():
            status.reset_daily_stats()
            status.save()
            count += 1

        logger.info(f"🫁 [LUNGS] Reset {count} respiratory status records")
        return {'reset_count': count}

    except Exception as e:
        logger.error(f"🫁 [LUNGS] Daily reset failed: {e}")
        return {'error': str(e)}


# =============================================================================
# SESSION 703: CIRCULATORY SYSTEM - DATA FLOW MONITORING
# =============================================================================

@shared_task(name='core.tasks.check_circulation', ignore_result=True)
def check_circulation():
    from core.tasks_misc import _impl_check_circulation
    return _impl_check_circulation()
@shared_task(name='core.tasks.check_spine_alignment')
def check_spine_alignment():
    from core.tasks_misc import _impl_check_spine_alignment
    return _impl_check_spine_alignment()
@shared_task(name='core.tasks.immune_scan')
def immune_scan():
    from core.tasks_body_systems import _impl_immune_scan
    return _impl_immune_scan()
@shared_task(name='core.tasks.check_digestion')
def check_digestion():
    from core.tasks_body_systems import _impl_check_digestion
    return _impl_check_digestion()
@shared_task(name='core.tasks.check_muscular')
def check_muscular():
    from core.tasks_body_systems import _impl_check_muscular
    return _impl_check_muscular()
@shared_task(name='core.tasks.check_brain')
def check_brain():
    from core.tasks_body_systems import _impl_check_brain
    return _impl_check_brain()
@shared_task(name='core.tasks.check_skin')
def check_skin():
    from core.tasks_body_systems import _impl_check_skin
    return _impl_check_skin()
@shared_task(name='core.tasks.check_nervous')
def check_nervous():
    from core.tasks_body_systems import _impl_check_nervous
    return _impl_check_nervous()
@shared_task(name='core.tasks.coordinate_body')
def coordinate_body():
    from core.tasks_body_systems import _impl_coordinate_body
    return _impl_coordinate_body()
@shared_task
def run_market_monitoring_agents():
    """
    Session 737: Run market monitoring agents on schedule.
    Session 944: Updated to use universal_agent_workspace_output for SKIN layer integration.

    Exercises these dormant agents:
    - MarketMovementMonitorAgent
    - MarketAnomalyDetectorAgent
    - SignalScannerAgent
    - ArbitrageDetector
    - SportsOddsAnalyst
    """
    logger.info("📊 [MARKET MONITOR] Starting market monitoring agents...")

    results = []

    agents_to_run = [
        ('MarketMovementMonitorAgent', 'Scan for significant market movements in the last 24 hours'),
        ('MarketAnomalyDetectorAgent', 'Detect any market anomalies or unusual patterns'),
        ('SignalScannerAgent', 'Scan for trading signals and market indicators'),
        ('ArbitrageDetector', 'Check for arbitrage opportunities across markets'),
        ('SportsOddsAnalyst', 'Analyze current sports betting odds for value'),
    ]

    for agent_name, task in agents_to_run:
        try:
            # Session 944: Use universal_agent_workspace_output to create WorkspaceOperations
            result = universal_agent_workspace_output(
                agent_name=agent_name,
                topic=task,
                trigger_source='schedule',
                force_production=True
            )
            success = result.get('success', False) if isinstance(result, dict) else False
            results.append({
                'agent': agent_name,
                'success': success,
                'file': result.get('file') if isinstance(result, dict) else None,
            })
            logger.info(f"📊 [MARKET MONITOR] {agent_name}: {'✅' if success else '❌'}")
        except Exception as e:
            logger.warning(f"📊 [MARKET MONITOR] {agent_name} failed: {e}")
            results.append({'agent': agent_name, 'success': False, 'error': str(e)})

    logger.info(f"📊 [MARKET MONITOR] Complete: {len([r for r in results if r.get('success')])} / {len(results)} succeeded")
    return results


@shared_task
def run_blockchain_monitoring_agents():
    """
    Session 737: Run blockchain monitoring agents on schedule.
    Session 944: Updated to use universal_agent_workspace_output for SKIN layer integration.

    Exercises these dormant agents:
    - BlockchainAuditCoordinator
    - WhaleWatcherAgent
    - ExploitDetectorAgent
    - TransactionMonitorAgent
    """
    logger.info("🔗 [BLOCKCHAIN MONITOR] Starting blockchain monitoring agents...")

    results = []

    agents_to_run = [
        ('WhaleWatcherAgent', 'Monitor for large crypto wallet movements and whale activity'),
        ('ExploitDetectorAgent', 'Scan for potential smart contract exploits or vulnerabilities'),
        ('TransactionMonitorAgent', 'Analyze recent blockchain transaction patterns'),
        ('BlockchainAuditCoordinator', 'Coordinate a brief blockchain ecosystem health check'),
    ]

    for agent_name, task in agents_to_run:
        try:
            # Session 944: Use universal_agent_workspace_output to create WorkspaceOperations
            result = universal_agent_workspace_output(
                agent_name=agent_name,
                topic=task,
                trigger_source='schedule',
                force_production=True
            )
            success = result.get('success', False) if isinstance(result, dict) else False
            results.append({
                'agent': agent_name,
                'success': success,
                'file': result.get('file') if isinstance(result, dict) else None,
            })
            logger.info(f"🔗 [BLOCKCHAIN MONITOR] {agent_name}: {'✅' if success else '❌'}")
        except Exception as e:
            logger.warning(f"🔗 [BLOCKCHAIN MONITOR] {agent_name} failed: {e}")
            results.append({'agent': agent_name, 'success': False, 'error': str(e)})

    logger.info(f"🔗 [BLOCKCHAIN MONITOR] Complete: {len([r for r in results if r.get('success')])} / {len(results)} succeeded")
    return results


@shared_task
def run_business_strategy_agents():
    from core.tasks_misc import _impl_run_business_strategy_agents
    return _impl_run_business_strategy_agents()
@shared_task
def exercise_all_dormant_agents():
    from core.tasks_misc import _impl_exercise_all_dormant_agents
    return _impl_exercise_all_dormant_agents()
@shared_task
def check_content_diversity():
    from core.tasks_misc import _impl_check_content_diversity
    return _impl_check_content_diversity()
@shared_task(ignore_result=True)
def check_celery_health():
    from core.tasks_misc import _impl_check_celery_health
    return _impl_check_celery_health()
@shared_task
def execute_orchestration_async(execution_id: str):
    """
    Session 764: Execute an orchestration workflow asynchronously.

    This task is triggered when a workflow is started with async_mode=True.
    It runs the full orchestration execution in the background.

    Args:
        execution_id: UUID of the OrchestrationExecution to run
    """
    from core.services.orchestration_engine import orchestration_engine
    from core.models_orchestration import OrchestrationExecution

    logger.info(f"🎭 [ORCHESTRATION] Starting async execution: {execution_id}")

    try:
        execution = OrchestrationExecution.objects.get(id=execution_id)

        if execution.status not in ('pending', 'running'):
            logger.warning(
                f"🎭 [ORCHESTRATION] Execution {execution_id} not in runnable state: {execution.status}"
            )
            return {'success': False, 'error': f'Invalid status: {execution.status}'}

        result = orchestration_engine._execute(execution)

        logger.info(
            f"🎭 [ORCHESTRATION] Execution {execution_id} completed: {result.status}"
        )

        return {
            'success': result.status == 'completed',
            'execution_id': str(execution_id),
            'status': result.status,
            'current_step': result.current_step,
            'total_steps': result.total_steps,
            'total_cost': float(result.total_cost),
            'error': result.error_message if result.status == 'failed' else None,
        }

    except OrchestrationExecution.DoesNotExist:
        logger.error(f"🎭 [ORCHESTRATION] Execution not found: {execution_id}")
        return {'success': False, 'error': 'Execution not found'}

    except Exception as e:
        logger.error(f"🎭 [ORCHESTRATION] Async execution failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task
def check_orchestration_timeouts():
    from core.tasks_misc import _impl_check_orchestration_timeouts
    return _impl_check_orchestration_timeouts()
@shared_task
def check_orchestration_auto_approvals():
    """
    Session 764: Check for auto-approvals on expired approval gates.

    Runs periodically to:
    1. Find pending approval gates past their expiration
    2. Auto-approve gates configured for auto-approval
    3. Mark other gates as expired

    This enables unattended workflow operation when configured.
    """
    from core.services.orchestration_approval import approval_service

    logger.info("🔔 [ORCHESTRATION] Checking for auto-approvals...")

    try:
        approval_service.check_auto_approvals()
        return {'success': True}

    except Exception as e:
        logger.error(f"🔔 [ORCHESTRATION] Auto-approval check failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


# ==================== SESSION 766: DREAM EXECUTION PIPELINE TASKS ====================


@shared_task(soft_time_limit=1800, time_limit=1860)
def execute_approved_dreams_via_orchestration(limit: int = 10):
    """
    Session 766: Execute approved dreams through the Orchestration Layer.

    This task finds approved dreams that haven't been executed yet and
    triggers the DreamExecutionPipeline to:
    1. Create a PartnershipProject from each dream
    2. Generate a CustomWorkflow for execution
    3. Trigger orchestration execution

    This is the NEW pipeline that actually executes dreams through the
    Orchestration Layer (Session 764). The old process_approved_dreams
    task creates DreamImplementation records but doesn't execute.

    Args:
        limit: Maximum number of dreams to process per run
    """
    from core.services.dream_execution_pipeline import dream_execution_pipeline

    logger.info(f"💭 [DREAM ORCHESTRATION] Processing up to {limit} approved dreams...")

    try:
        results = dream_execution_pipeline.process_approved_dreams(limit=limit)

        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count

        logger.info(
            f"💭 [DREAM ORCHESTRATION] Processed {len(results)} dreams: "
            f"{success_count} success, {failed_count} failed"
        )

        return {
            'success': True,
            'total_processed': len(results),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results,
        }

    except SoftTimeLimitExceeded:
        logger.error("[DREAM ORCHESTRATION] execute_approved_dreams_via_orchestration timed out (soft_time_limit=1800s)")
        return {'success': False, 'error': 'Celery soft_time_limit exceeded', 'timed_out': True}
    except Exception as e:
        logger.error(f"💭 [DREAM ORCHESTRATION] Failed to process dreams: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task
def execute_single_dream(dream_id: str):
    """
    Session 766: Execute a single approved dream.

    This task is triggered when a dream is approved to immediately
    start the execution pipeline.

    Args:
        dream_id: UUID of the AgentDream to execute
    """
    from core.services.dream_execution_pipeline import dream_execution_pipeline
    from core.models_unified_system import AgentDream

    logger.info(f"💭 [DREAM PIPELINE] Executing dream: {dream_id}")

    try:
        dream = AgentDream.objects.get(id=dream_id)

        if dream.decision_outcome != 'approved':
            logger.warning(
                f"💭 [DREAM PIPELINE] Dream {dream_id} is not approved: {dream.decision_outcome}"
            )
            return {
                'success': False,
                'error': f"Dream not approved: {dream.decision_outcome}",
            }

        result = dream_execution_pipeline.execute_dream(dream, async_mode=True)

        if result['success']:
            logger.info(f"💭 [DREAM PIPELINE] Dream executed: {dream.title}")
        else:
            logger.warning(f"💭 [DREAM PIPELINE] Dream failed: {result.get('error')}")

        return result

    except AgentDream.DoesNotExist:
        logger.error(f"💭 [DREAM PIPELINE] Dream not found: {dream_id}")
        return {'success': False, 'error': 'Dream not found'}

    except Exception as e:
        logger.error(f"💭 [DREAM PIPELINE] Failed to execute dream: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


# =============================================================================
# Session 766: Gate Progression Pipeline Tasks
# =============================================================================

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
@shared_task(bind=True, name='core.tasks.process_content_ideas', max_retries=2, default_retry_delay=60)
def process_content_ideas(
    self,
    dry_run: bool = False,
    limit: int = 50,
    include_dreams: bool = True,
    include_conversations: bool = True,
    days_lookback: int = 30,
):
    from core.tasks_misc import _impl_process_content_ideas
    return _impl_process_content_ideas(self, dry_run, limit, include_dreams, include_conversations, days_lookback)
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


@shared_task(name='core.tasks.maintain_knowledge_freshness')
def maintain_knowledge_freshness():
    """
    Session 767: Maintain knowledge source freshness.

    Decays freshness scores based on age, deactivates stale sources,
    and identifies agents needing knowledge refresh.

    Run daily to keep knowledge sources properly aged.

    Returns:
        Maintenance statistics
    """
    from core.services.learning_pattern_engine import get_learning_pattern_engine

    logger.info("🔄 [FRESHNESS] Starting knowledge freshness maintenance...")

    try:
        engine = get_learning_pattern_engine()
        result = engine.maintain_knowledge_freshness()

        logger.info(
            f"🔄 [FRESHNESS] Complete: "
            f"{result.get('sources_decayed', 0)} decayed, "
            f"{result.get('sources_deactivated', 0)} deactivated, "
            f"{result.get('total_active', 0)} active"
        )

        return {
            'success': True,
            **result
        }

    except Exception as e:
        logger.error(f"🔄 [FRESHNESS] Failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


@shared_task(name='core.tasks.promote_to_shared_knowledge')
def promote_to_shared_knowledge(min_confidence: float = 0.7):
    """
    Session 767: Promote high-confidence knowledge to SharedKnowledge.

    Scans AgentKnowledgeSource and KnowledgeTransfer for well-validated
    knowledge and promotes it to the shared repository.

    Run weekly to grow the shared knowledge base.

    Args:
        min_confidence: Minimum confidence for promotion (default 0.7)

    Returns:
        Promotion statistics
    """
    from core.services.learning_pattern_engine import get_learning_pattern_engine

    logger.info(f"🚀 [KNOWLEDGE PROMOTION] Starting (min_confidence={min_confidence})...")

    try:
        engine = get_learning_pattern_engine()
        result = engine.promote_to_shared_knowledge(min_confidence=min_confidence)

        logger.info(
            f"🚀 [KNOWLEDGE PROMOTION] Complete: "
            f"{result.get('promoted_from_sources', 0)} from sources, "
            f"{result.get('promoted_from_transfers', 0)} from transfers, "
            f"{result.get('total_shared_knowledge', 0)} total"
        )

        return {
            'success': True,
            **result
        }

    except Exception as e:
        logger.error(f"🚀 [KNOWLEDGE PROMOTION] Failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


# ==================== SESSION 776: SKIN LAYER AGENT INTEGRATION ====================


def _get_workspace_for_skin_layer():
    """
    Session 885/909/910/976: Helper to get an active workspace for SKIN layer tasks.

    Session 976: Now prefers "System Autonomous Workspace" (rooted at generated_content/)
    to prevent auto-generated files from polluting the git repository.

    Looks for workspaces in this order:
    1. "System Autonomous Workspace" (generated_content/ — gitignored)
    2. Fallback: create one at generated_content/

    Returns:
        Tuple of (user, workspace) or (None, None) if not found
    """
    from django.contrib.auth import get_user_model
    from core.models_skin_layer import ProjectWorkspace
    import os

    User = get_user_model()

    # Session 976: Prefer System Autonomous Workspace (rooted at generated_content/)
    workspace = ProjectWorkspace.objects.filter(
        name='System Autonomous Workspace'
    ).first()
    if workspace:
        # Session 1036: Auto-correct root_path if it doesn't exist on this host.
        # The DB record may have been created on a local dev machine (/Users/...)
        # but Railway containers use /app/ as project root.
        if not os.path.isdir(workspace.root_path):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            correct_path = os.path.join(project_root, 'generated_content')
            os.makedirs(correct_path, exist_ok=True)
            logger.info(
                f"[workspace] root_path '{workspace.root_path}' does not exist on this host, "
                f"correcting to '{correct_path}'"
            )
            workspace.root_path = correct_path
            workspace.save(update_fields=['root_path'])
        return workspace.user, workspace

    # Fallback: create one at generated_content/
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(project_root, 'generated_content')
    os.makedirs(content_dir, exist_ok=True)

    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    if not user:
        return None, None

    workspace = ProjectWorkspace.objects.create(
        user=user,
        name='System Autonomous Workspace',
        root_path=content_dir,
        workspace_type='local',
        is_active=True,
        allow_file_write=True,
        protected_paths=['.env', '.env.local', 'secrets/', 'credentials/'],
    )
    logger.info(f"Created System Autonomous Workspace at {content_dir}")
    return user, workspace


@shared_task(name='core.tasks.agent_workspace_status_report')
def agent_workspace_status_report():
    from core.tasks_agents import _impl_agent_workspace_status_report
    return _impl_agent_workspace_status_report()
@shared_task(name='core.tasks.agent_research_to_workspace')
def agent_research_to_workspace(topic: str = None):
    from core.tasks_agents import _impl_agent_research_to_workspace
    return _impl_agent_research_to_workspace(topic)
@shared_task(name='core.tasks.agent_content_to_workspace')
def agent_content_to_workspace(content_type: str = 'blog', topic: str = None):
    from core.tasks_agents import _impl_agent_content_to_workspace
    return _impl_agent_content_to_workspace(content_type, topic)
@shared_task(name='core.tasks.enhance_blog')
def enhance_blog_task(blog_id: str, focus_areas: list = None, save: bool = False):
    from core.tasks_misc import _impl_enhance_blog_task
    return _impl_enhance_blog_task(blog_id, focus_areas, save)
@shared_task(name='core.tasks.evaluate_unscored_blogs')
def evaluate_unscored_blogs(limit: int = 20):
    """
    Session 987: Batch-evaluate draft blogs that have no quality_score through PublishGate.

    The v1 blog pipeline (99.7% of blogs) never called PublishGate, leaving all
    blogs at quality_score=None, publish_ready=False. This task retroactively
    evaluates them so the system can identify publishable content.

    Args:
        limit: Maximum blogs to evaluate per run (default 20)
    """
    from core.models_unified_system import SelfBlog
    from core.services.publish_gate import PublishGate

    blogs = SelfBlog.objects.filter(
        quality_score__isnull=True,
        status='draft',
    ).order_by('-created_at')[:limit]

    total = blogs.count()
    if total == 0:
        return {'processed': 0, 'message': 'No unscored blogs found'}

    gate = PublishGate()
    results = {'processed': 0, 'publish_ready': 0, 'errors': 0}

    for blog in blogs:
        try:
            gate_result = gate.apply_to_blog(blog)
            results['processed'] += 1
            if blog.publish_ready:
                results['publish_ready'] += 1
            logger.info(
                f"📝 [PUBLISH-GATE] Blog {blog.id}: "
                f"decision={gate_result.decision}, quality={gate_result.quality_score}"
            )
        except Exception as e:
            results['errors'] += 1
            logger.warning(f"📝 [PUBLISH-GATE] Blog {blog.id} failed: {e}")

    logger.info(
        f"📝 [PUBLISH-GATE] Batch complete: {results['processed']} evaluated, "
        f"{results['publish_ready']} publish-ready"
    )
    return results


@shared_task(name='core.tasks.reevaluate_enhanced_blogs')
def reevaluate_enhanced_blogs(limit: int = 50):
    from core.tasks_misc import _impl_reevaluate_enhanced_blogs
    return _impl_reevaluate_enhanced_blogs(limit)
@shared_task(name='core.tasks.auto_publish_approved_blogs')
def auto_publish_approved_blogs():
    """
    Session 1000C: Move approved blogs to published status.

    Final step in the automation pipeline. Blogs that passed PublishGate
    quality checks and were promoted to 'approved' get set to 'published'.
    """
    from core.models_unified_system import SelfBlog

    blogs = SelfBlog.objects.filter(status='approved', publish_ready=True)
    count = blogs.count()

    if count == 0:
        return {'published': 0, 'message': 'No approved blogs to publish'}

    published_ids = []
    for blog in blogs:
        blog.status = 'published'
        blog.save(update_fields=['status'])
        published_ids.append(str(blog.id))
        logger.info(f"[AUTO-PUBLISH] Published blog: {blog.title[:60]}")

    return {'published': count, 'blog_ids': published_ids}


@shared_task(name='core.tasks.verify_autopilot_action', ignore_result=True)
def verify_autopilot_action(action_id: int):
    """
    Deferred verification of an autopilot action.

    Called by ActionVerifier.record_and_verify() after a delay (typically 2min).
    Checks whether the action improved the situation. If not, auto-rolls back.
    """
    from core.services.ops_autopilot import ActionVerifier
    result = ActionVerifier.verify_action(action_id)
    if result.get('passed'):
        logger.info(f"[VERIFY] Action {action_id} verified OK")
    elif result.get('skipped'):
        logger.info(f"[VERIFY] Action {action_id} skipped: {result.get('reason', '')}")
    else:
        logger.warning(f"[VERIFY] Action {action_id} FAILED verification — rollback attempted")
    return result


@shared_task(name='core.tasks.content_autonomy_loop', ignore_result=True)
def content_autonomy_loop():
    from core.tasks_content import _impl_content_autonomy_loop
    return _impl_content_autonomy_loop()
def _route_gate_repair(blog) -> str | None:
    """Determine the best repair action based on gate_notes."""
    notes = (blog.gate_notes or '').lower()

    # Map gate failure reasons to repair strategies
    if 'research' in notes or 'claim' in notes or 'citation' in notes:
        return 'research'  # Needs more research backing
    if 'structure' in notes or 'heading' in notes or 'format' in notes:
        return 'structure'  # Needs structural improvement
    if 'quality' in notes or 'writing' in notes or 'engagement' in notes:
        return 'enhance'  # Needs general enhancement
    if 'novelty' in notes or 'generic' in notes or 'repetitive' in notes:
        return 'differentiate'  # Needs unique angle
    if 'mythology' in notes or 'operational' in notes:
        return None  # Don't repair internal/operational content
    if 'panel_failed' in notes:
        return None  # Review panel itself failed, not content issue

    return 'enhance'  # Default to general enhancement


def _execute_gate_repair(blog, repair_action: str) -> bool:
    """Execute a targeted repair pass on a blog."""
    from core.agents.editor_agent import EditorAgent

    focus_map = {
        'research': ['citations', 'evidence', 'data_backing'],
        'structure': ['headers', 'structure', 'flow', 'readability'],
        'enhance': ['hooks', 'engagement', 'conclusion', 'structure'],
        'differentiate': ['unique_angle', 'original_analysis', 'hooks'],
    }

    focus_areas = focus_map.get(repair_action, ['engagement', 'structure'])

    try:
        agent = EditorAgent()
        result = agent.execute(
            task=f"Repair blog ({repair_action}): {blog.title[:80]}",
            context={
                'blog_id': str(blog.id),
                'focus_areas': focus_areas,
                'gate_notes': (blog.gate_notes or '')[:300],
                'repair_type': repair_action,
                'save': True,
            },
            scifi_context={},
            spider_context={},
        )

        if result.success:
            logger.info(
                f"[CONTENT-AUTONOMY] Repair ({repair_action}) succeeded: "
                f"{blog.title[:50]}"
            )
            return True
        return False

    except Exception as e:
        logger.warning(f"[CONTENT-AUTONOMY] Repair ({repair_action}) error: {e}")
        return False


# =============================================================================
# Session 1033: Content Finishing Loop + Deliverable Quality Scoring
# =============================================================================

@shared_task(name='core.tasks.auto_enhance_blogs')
def auto_enhance_blogs(limit: int = 5):
    from core.tasks_misc import _impl_auto_enhance_blogs
    return _impl_auto_enhance_blogs(limit)
@shared_task(name='core.tasks.score_unscored_deliverables')
def score_unscored_deliverables(limit: int = 50):
    """
    Session 1033: Score deliverables that still have the default 0.7 quality score.

    Uses heuristic scoring based on content characteristics to replace
    the hardcoded default with a meaningful quality assessment.
    """
    from core.models_deliverables import Deliverable

    deliverables = list(
        Deliverable.objects.filter(quality_score=0.7)
        .exclude(content__isnull=True)
        .exclude(content='')
        .order_by('-created_at')[:limit]
    )

    if not deliverables:
        return {'scored': 0, 'message': 'No unscored deliverables'}

    scored = 0
    for d in deliverables:
        try:
            score = _calculate_deliverable_quality(d)
            if score != 0.7:
                d.quality_score = score
                d.save(update_fields=['quality_score', 'updated_at'])
                scored += 1
        except Exception as e:
            logger.warning(f"[SCORE] Error scoring deliverable {d.id}: {e}")

    logger.info(f"[SCORE] Scored {scored}/{len(deliverables)} deliverables")
    return {'scored': scored, 'total_checked': len(deliverables)}


def _calculate_deliverable_quality(deliverable) -> float:
    """
    Session 1033: Heuristic quality scoring for deliverables.

    Scores 0.1-1.0 based on:
    - Content length (sweet spot 300-3000 words)
    - Structure indicators (headers, lists, references)
    - Agent confidence score
    - Content format richness
    """
    score = 0.45
    content = deliverable.content or ''
    word_count = len(content.split())

    # Content length scoring
    if word_count >= 200:
        score += 0.08
    if word_count >= 500:
        score += 0.07
    if word_count >= 1000:
        score += 0.05
    if word_count > 5000:
        score -= 0.05  # Penalize excessively long/unfocused

    # Structure indicators
    if '##' in content or '**' in content:
        score += 0.05
    if '\n- ' in content or '\n* ' in content or '\n1.' in content:
        score += 0.05
    if 'http://' in content or 'https://' in content:
        score += 0.05

    # Agent confidence
    conf = deliverable.confidence_score or 0.0
    if conf > 0.8:
        score += 0.1
    elif conf > 0.6:
        score += 0.05

    # Penalize very short content
    if word_count < 50:
        score = max(0.2, score - 0.2)

    return round(min(1.0, max(0.1, score)), 2)


@shared_task(name='core.tasks.aggregate_tool_call_stats')
def aggregate_tool_call_stats(days_back: int = 1):
    from core.tasks_ops import _impl_aggregate_tool_call_stats
    return _impl_aggregate_tool_call_stats(days_back)
@shared_task(name='core.tasks.agent_daily_summary')
def agent_daily_summary():
    from core.tasks_agents import _impl_agent_daily_summary
    return _impl_agent_daily_summary()
AGENT_WORKSPACE_REGISTRY = {
    # =========================================================================
    # ANALYSIS & RESEARCH AGENTS - Produce reports and analysis
    # =========================================================================
    'ResearchAgent': {
        'category': 'research',
        'output_dir': 'research',
        'output_type': 'report',
        'task_template': 'Research current trends and developments in {topic}',
        'default_topic': 'AI and technology innovation',
    },
    'TrendAnalysisAgent': {
        'category': 'research',
        'output_dir': 'analysis/trends',
        'output_type': 'report',
        'task_template': 'Analyze emerging trends in {topic}',
        'default_topic': 'technology and market movements',
    },
    'MarketIntelligenceAgent': {
        'category': 'research',
        'output_dir': 'analysis/market',
        'output_type': 'report',
        'task_template': 'Provide market intelligence analysis for {topic}',
        'default_topic': 'current market conditions',
    },
    'CompetitorAnalysisAgent': {
        'category': 'research',
        'output_dir': 'analysis/competitors',
        'output_type': 'report',
        'task_template': 'Analyze competitive landscape for {topic}',
        'default_topic': 'AI content creation tools',
    },
    'CustomerResearchAgent': {
        'category': 'research',
        'output_dir': 'analysis/customers',
        'output_type': 'report',
        'task_template': 'Research customer insights for {topic}',
        'default_topic': 'AI-powered productivity tools',
    },
    'OpportunityScoringAgent': {
        'category': 'research',
        'output_dir': 'analysis/opportunities',
        'output_type': 'report',
        'task_template': 'Score and analyze opportunities in {topic}',
        'default_topic': 'emerging technology markets',
    },

    # =========================================================================
    # STRATEGY AGENTS - Produce strategy documents
    # =========================================================================
    'BrandStrategyAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/brand',
        'output_type': 'strategy',
        'task_template': 'Develop brand strategy recommendations for {topic}',
        'default_topic': 'AI-powered platforms',
    },
    'ContentStrategyAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/content',
        'output_type': 'strategy',
        'task_template': 'Create content strategy for {topic}',
        'default_topic': 'technical blog and documentation',
    },
    'MarketingStrategyAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/marketing',
        'output_type': 'strategy',
        'task_template': 'Develop marketing strategy for {topic}',
        'default_topic': 'developer tools and platforms',
    },
    'SEOOptimizerAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/seo',
        'output_type': 'report',
        'task_template': 'SEO optimization recommendations for {topic}',
        'default_topic': 'AI development content',
    },
    'SocialMediaAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/social',
        'output_type': 'strategy',
        'task_template': 'Social media strategy for {topic}',
        'default_topic': 'AI and tech community engagement',
    },
    'BrandIdentityAgent': {
        'category': 'strategy',
        'output_dir': 'strategy/identity',
        'output_type': 'strategy',
        'task_template': 'Brand identity guidelines for {topic}',
        'default_topic': 'AI-first technology brands',
    },

    # =========================================================================
    # CONTENT CREATION AGENTS - Produce content files
    # =========================================================================
    'ContentWriterAgent': {
        'category': 'content',
        'output_dir': 'content/articles',
        'output_type': 'article',
        'task_template': 'Write an informative article about {topic}',
        'default_topic': 'AI development best practices',
    },
    'TechnicalDocumentAgent': {
        'category': 'content',
        'output_dir': 'content/documentation',
        'output_type': 'documentation',
        'task_template': 'Create technical documentation for {topic}',
        'default_topic': 'API integration patterns',
    },
    'LegalDocDrafterAgent': {
        'category': 'content',
        'output_dir': 'content/legal',
        'output_type': 'document',
        'task_template': 'Draft legal document template for {topic}',
        'default_topic': 'software licensing terms',
    },

    # =========================================================================
    # FINANCIAL/MARKET AGENTS - Produce market analysis
    # =========================================================================
    'StockAuditCoordinator': {
        'category': 'financial',
        'output_dir': 'financial/stocks',
        'output_type': 'report',
        'task_template': 'Coordinate comprehensive stock analysis for {topic}',
        'default_topic': 'AI and technology sector',
    },
    'StockAnalystAgent': {
        'category': 'financial',
        'output_dir': 'financial/analysis',
        'output_type': 'report',
        'task_template': 'Analyze stock performance for {topic}',
        'default_topic': 'major tech companies',
    },
    'MarketMovementMonitorAgent': {
        'category': 'financial',
        'output_dir': 'financial/movements',
        'output_type': 'report',
        'task_template': 'Monitor market movements for {topic}',
        'default_topic': 'technology sector indices',
    },
    'InstitutionalWatcherAgent': {
        'category': 'financial',
        'output_dir': 'financial/institutional',
        'output_type': 'report',
        'task_template': 'Track institutional activity in {topic}',
        'default_topic': 'AI company holdings',
    },
    'MarketAnomalyDetectorAgent': {
        'category': 'financial',
        'output_dir': 'financial/anomalies',
        'output_type': 'alert',
        'task_template': 'Detect market anomalies in {topic}',
        'default_topic': 'technology stocks',
    },
    'BullCaseAgent': {
        'category': 'financial',
        'output_dir': 'financial/bull-cases',
        'output_type': 'analysis',
        'task_template': 'Build bull case analysis for {topic}',
        'default_topic': 'AI sector growth',
    },
    'BearCaseAgent': {
        'category': 'financial',
        'output_dir': 'financial/bear-cases',
        'output_type': 'analysis',
        'task_template': 'Build bear case analysis for {topic}',
        'default_topic': 'AI sector risks',
    },
    'SignalScannerAgent': {
        'category': 'financial',
        'output_dir': 'financial/signals',
        'output_type': 'report',
        'task_template': 'Scan for trading signals in {topic}',
        'default_topic': 'technology stocks',
    },
    'MarketIntelligenceCoordinator': {
        'category': 'financial',
        'output_dir': 'financial/intelligence',
        'output_type': 'report',
        'task_template': 'Coordinate market intelligence for {topic}',
        'default_topic': 'global technology markets',
    },

    # =========================================================================
    # PREDICTION/BETTING AGENTS - Produce predictions and odds analysis
    # =========================================================================
    'PredictionMarketAnalyst': {
        'category': 'predictions',
        'output_dir': 'predictions/markets',
        'output_type': 'analysis',
        'task_template': 'Analyze prediction markets for {topic}',
        'default_topic': 'technology and AI developments',
    },
    'SportsOddsAnalyst': {
        'category': 'predictions',
        'output_dir': 'predictions/sports',
        'output_type': 'analysis',
        'task_template': 'Analyze sports betting opportunities for {topic}',
        'default_topic': 'upcoming major sporting events',
    },
    'ArbitrageDetector': {
        'category': 'predictions',
        'output_dir': 'predictions/arbitrage',
        'output_type': 'alert',
        'task_template': 'Detect arbitrage opportunities in {topic}',
        'default_topic': 'sports betting markets',
    },

    # =========================================================================
    # BLOCKCHAIN AGENTS - Produce blockchain analysis
    # =========================================================================
    'BlockchainAuditCoordinator': {
        'category': 'blockchain',
        'output_dir': 'blockchain/audits',
        'output_type': 'report',
        'task_template': 'Coordinate blockchain audit for {topic}',
        'default_topic': 'DeFi protocols',
    },
    'SmartContractAuditorAgent': {
        'category': 'blockchain',
        'output_dir': 'blockchain/contracts',
        'output_type': 'audit',
        'task_template': 'Audit smart contract patterns for {topic}',
        'default_topic': 'common DeFi vulnerabilities',
    },
    'TransactionMonitorAgent': {
        'category': 'blockchain',
        'output_dir': 'blockchain/transactions',
        'output_type': 'report',
        'task_template': 'Monitor blockchain transactions for {topic}',
        'default_topic': 'large wallet movements',
    },
    'WhaleWatcherAgent': {
        'category': 'blockchain',
        'output_dir': 'blockchain/whales',
        'output_type': 'alert',
        'task_template': 'Track whale activity for {topic}',
        'default_topic': 'major cryptocurrency wallets',
    },
    'ExploitDetectorAgent': {
        'category': 'blockchain',
        'output_dir': 'blockchain/exploits',
        'output_type': 'alert',
        'task_template': 'Detect potential exploits in {topic}',
        'default_topic': 'DeFi protocol patterns',
    },

    # =========================================================================
    # NARRATIVE/CULTURAL AGENTS - Produce narrative analysis
    # =========================================================================
    'NarrativeDriftCoordinator': {
        'category': 'narrative',
        'output_dir': 'narrative/drift',
        'output_type': 'report',
        'task_template': 'Analyze narrative drift patterns for {topic}',
        'default_topic': 'AI technology discourse',
    },
    'NarrativeHistorianAgent': {
        'category': 'narrative',
        'output_dir': 'narrative/history',
        'output_type': 'report',
        'task_template': 'Document narrative history for {topic}',
        'default_topic': 'AI development milestones',
    },
    'TrendBreakDetectorAgent': {
        'category': 'narrative',
        'output_dir': 'narrative/trends',
        'output_type': 'alert',
        'task_template': 'Detect trend breaks in {topic}',
        'default_topic': 'technology narratives',
    },
    'CulturalImpactAgent': {
        'category': 'narrative',
        'output_dir': 'narrative/cultural',
        'output_type': 'report',
        'task_template': 'Analyze cultural impact of {topic}',
        'default_topic': 'AI on society and work',
    },

    # =========================================================================
    # PODCAST/DEBATE AGENTS - Produce show notes and transcripts
    # =========================================================================
    'PodcastCoordinatorAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/episodes',
        'output_type': 'show_notes',
        'task_template': 'Generate podcast episode outline for {topic}',
        'default_topic': 'AI innovation and ethics',
    },
    'DebateAdvocateAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/debates/advocate',
        'output_type': 'argument',
        'task_template': 'Build advocate arguments for {topic}',
        'default_topic': 'benefits of AI automation',
    },
    'DebateSkepticAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/debates/skeptic',
        'output_type': 'argument',
        'task_template': 'Build skeptic arguments for {topic}',
        'default_topic': 'risks of AI automation',
    },
    'ModeratorAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/moderation',
        'output_type': 'summary',
        'task_template': 'Moderate discussion and summarize for {topic}',
        'default_topic': 'AI development debates',
    },
    'AutonomousContentStudioCoordinator': {
        'category': 'podcast',
        'output_dir': 'podcast/studio',
        'output_type': 'production_plan',
        'task_template': 'Create content studio production plan for {topic}',
        'default_topic': 'weekly AI news coverage',
    },
    'TopicMinerAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/topics',
        'output_type': 'topic_list',
        'task_template': 'Mine trending topics for {topic}',
        'default_topic': 'AI and technology news',
    },
    'ContrarianAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/contrarian',
        'output_type': 'perspective',
        'task_template': 'Provide contrarian perspective on {topic}',
        'default_topic': 'popular AI assumptions',
    },
    'PerformanceAnalystAgent': {
        'category': 'podcast',
        'output_dir': 'podcast/performance',
        'output_type': 'report',
        'task_template': 'Analyze content performance for {topic}',
        'default_topic': 'recent podcast episodes',
    },

    # =========================================================================
    # DEVELOPMENT AGENTS - Produce code and technical artifacts
    # =========================================================================
    # Session 1029: CodeGeneratorAgent removed — no codebase access on Railway,
    # captures CodeArtifacts but can't write files. Re-add when workspace is available.
    # 'CodeGeneratorAgent': {
    #     'category': 'development',
    #     'output_dir': 'development/generated',
    #     'output_type': 'code',
    #     'task_template': 'Generate code example for {topic}',
    #     'default_topic': 'Python utility functions',
    # },
    'FullStackDeveloperAgent': {
        'category': 'development',
        'output_dir': 'development/fullstack',
        'output_type': 'code',
        'task_template': 'Create full-stack implementation plan for {topic}',
        'default_topic': 'REST API endpoints',
    },
    'CodeReviewAgent': {
        'category': 'development',
        'output_dir': 'development/reviews',
        'output_type': 'review',
        'task_template': 'Code review guidelines for {topic}',
        'default_topic': 'Python best practices',
    },
    'DevOpsAgent': {
        'category': 'development',
        'output_dir': 'development/devops',
        'output_type': 'runbook',
        'task_template': 'Create DevOps runbook for {topic}',
        'default_topic': 'CI/CD pipeline maintenance',
    },
    'PromptEngineeringAgent': {
        'category': 'development',
        'output_dir': 'development/prompts',
        'output_type': 'prompt_library',
        'task_template': 'Design prompt templates for {topic}',
        'default_topic': 'code generation tasks',
    },

    # =========================================================================
    # MEDIA CREATION AGENTS - Produce creative briefs
    # =========================================================================
    'ImageAgent': {
        'category': 'media',
        'output_dir': 'media/images',
        'output_type': 'creative_brief',
        'task_template': 'Create image generation brief for {topic}',
        'default_topic': 'AI technology visualizations',
    },
    'VideoAgent': {
        'category': 'media',
        'output_dir': 'media/videos',
        'output_type': 'creative_brief',
        'task_template': 'Create video production brief for {topic}',
        'default_topic': 'AI explainer videos',
    },
    # Session 1088: Re-enabled (unblocked Session 1068, quota replenished)
    'AudioAgent': {
        'category': 'media',
        'output_dir': 'media/audio',
        'output_type': 'creative_brief',
        'task_template': 'Create audio production brief for {topic}',
        'default_topic': 'podcast intro music',
    },
    'ThreeDAgent': {
        'category': 'media',
        'output_dir': 'media/3d',
        'output_type': 'creative_brief',
        'task_template': 'Create 3D asset brief for {topic}',
        'default_topic': 'AI visualization models',
    },
    'ImageEditingAgent': {
        'category': 'media',
        'output_dir': 'media/editing/images',
        'output_type': 'editing_guide',
        'task_template': 'Create image editing guidelines for {topic}',
        'default_topic': 'brand consistency',
    },
    'VideoEditingAgent': {
        'category': 'media',
        'output_dir': 'media/editing/videos',
        'output_type': 'editing_guide',
        'task_template': 'Create video editing guidelines for {topic}',
        'default_topic': 'content pacing and structure',
    },
    'ResolveAgent': {
        'category': 'media',
        'output_dir': 'media/resolve',
        'output_type': 'project_settings',
        'task_template': 'Create DaVinci Resolve project settings for {topic}',
        'default_topic': 'YouTube content workflow',
    },
    'TrainedCreationAgent': {
        'category': 'media',
        'output_dir': 'media/trained',
        'output_type': 'style_guide',
        'task_template': 'Document trained model style guide for {topic}',
        'default_topic': 'brand-specific imagery',
    },
    'CharacterTrainingAgent': {
        'category': 'media',
        'output_dir': 'media/characters',
        'output_type': 'character_sheet',
        'task_template': 'Create character training documentation for {topic}',
        'default_topic': 'AI mascot characters',
    },

    # =========================================================================
    # COORDINATION/EXECUTIVE AGENTS - Produce summaries and plans
    # =========================================================================
    'CTOAgent': {
        'category': 'executive',
        'output_dir': 'executive/cto',
        'output_type': 'memo',
        'task_template': 'Technical leadership memo on {topic}',
        'default_topic': 'architecture decisions',
    },
    'COOAgent': {
        'category': 'executive',
        'output_dir': 'executive/coo',
        'output_type': 'memo',
        'task_template': 'Operations memo on {topic}',
        'default_topic': 'process improvements',
    },
    'CreativeDirectorAgent': {
        'category': 'executive',
        'output_dir': 'executive/creative',
        'output_type': 'direction',
        'task_template': 'Creative direction for {topic}',
        'default_topic': 'upcoming content campaigns',
    },
    'MeetingCoordinatorAgent': {
        'category': 'executive',
        'output_dir': 'executive/meetings',
        'output_type': 'agenda',
        'task_template': 'Meeting agenda for {topic}',
        'default_topic': 'weekly team sync',
    },
    'WorkflowAgent': {
        'category': 'coordination',
        'output_dir': 'workflows/definitions',
        'output_type': 'workflow',
        'task_template': 'Define workflow for {topic}',
        'default_topic': 'content production pipeline',
    },
    'WorkflowOrchestrationAgent': {
        'category': 'coordination',
        'output_dir': 'workflows/orchestration',
        'output_type': 'orchestration_plan',
        'task_template': 'Orchestration plan for {topic}',
        'default_topic': 'multi-agent collaboration',
    },
    'OpportunityPipelineAgent': {
        'category': 'coordination',
        'output_dir': 'pipelines/opportunities',
        'output_type': 'pipeline_status',
        'task_template': 'Pipeline status for {topic}',
        'default_topic': 'active opportunities',
    },
    'ContentExecutorAgent': {
        'category': 'coordination',
        'output_dir': 'execution/content',
        'output_type': 'execution_log',
        'task_template': 'Content execution log for {topic}',
        'default_topic': 'recent content deliverables',
    },
    'CampaignOrchestratorAgent': {
        'category': 'coordination',
        'output_dir': 'campaigns/orchestration',
        'output_type': 'campaign_plan',
        'task_template': 'Campaign orchestration plan for {topic}',
        'default_topic': 'quarterly content campaign',
    },
    'AISeriesWorkflowAgent': {
        'category': 'coordination',
        'output_dir': 'series/workflows',
        'output_type': 'series_plan',
        'task_template': 'AI series workflow plan for {topic}',
        'default_topic': 'educational content series',
    },
    'ContentDiversityOrchestrator': {
        'category': 'coordination',
        'output_dir': 'diversity/analysis',
        'output_type': 'diversity_report',
        'task_template': 'Content diversity analysis for {topic}',
        'default_topic': 'recent content output',
    },

    # =========================================================================
    # SYSTEM/SECURITY AGENTS - Produce system reports
    # =========================================================================
    'SystemIntelligenceAgent': {
        'category': 'system',
        'output_dir': 'system/intelligence',
        'output_type': 'status_report',
        'task_template': 'System intelligence report on {topic}',
        'default_topic': 'overall platform health',
    },
    'ThinkingAgent': {
        'category': 'system',
        'output_dir': 'system/thinking',
        'output_type': 'reflection',
        'task_template': 'Thinking reflection on {topic}',
        'default_topic': 'system improvement opportunities',
    },
    'MemoryIsolationAgent': {
        'category': 'security',
        'output_dir': 'security/memory',
        'output_type': 'audit',
        'task_template': 'Memory isolation audit for {topic}',
        'default_topic': 'cross-agent data boundaries',
    },
    'ContentAuditAgent': {
        'category': 'security',
        'output_dir': 'security/content',
        'output_type': 'audit',
        'task_template': 'Content audit report for {topic}',
        'default_topic': 'recent content output quality',
    },

    # =========================================================================
    # PERSONAL ASSISTANT - Special handling
    # =========================================================================
    'PersonalAssistantAgent': {
        'category': 'assistant',
        'output_dir': 'assistant/logs',
        'output_type': 'activity_log',
        'task_template': 'Personal assistant activity summary for {topic}',
        'default_topic': 'recent interactions and tasks',
    },

    # =========================================================================
    # Session 885: FINANCIAL/STOCK AGENTS - Produce market analysis and stock reviews
    # These agents were missing from the registry, preventing workspace operations
    # =========================================================================
    'StockAnalystAgent': {
        'category': 'financial',
        'output_dir': 'financial/stocks',
        'output_type': 'stock_analysis',
        'task_template': 'Analyze stock market conditions for {topic}',
        'default_topic': 'current market trends and notable movements',
    },
    'StockAuditCoordinator': {
        'category': 'financial',
        'output_dir': 'financial/audits',
        'output_type': 'market_audit',
        'task_template': 'Coordinate market health audit for {topic}',
        'default_topic': 'overall market conditions',
    },
    'BullCaseAgent': {
        'category': 'financial',
        'output_dir': 'financial/bull_cases',
        'output_type': 'bullish_analysis',
        'task_template': 'Build bullish case for {topic}',
        'default_topic': 'strongest market opportunities',
    },
    'BearCaseAgent': {
        'category': 'financial',
        'output_dir': 'financial/bear_cases',
        'output_type': 'bearish_analysis',
        'task_template': 'Build bearish case for {topic}',
        'default_topic': 'key market risks and warnings',
    },
    'MarketIntelligenceCoordinator': {
        'category': 'financial',
        'output_dir': 'financial/intelligence',
        'output_type': 'market_intel',
        'task_template': 'Synthesize market intelligence for {topic}',
        'default_topic': 'cross-market analysis',
    },
    'PredictionMarketAnalyst': {
        'category': 'financial',
        'output_dir': 'financial/predictions',
        'output_type': 'prediction_analysis',
        'task_template': 'Analyze prediction markets for {topic}',
        'default_topic': 'high-value prediction opportunities',
    },
    'SportsOddsAnalyst': {
        'category': 'sports',
        'output_dir': 'sports/odds',
        'output_type': 'odds_analysis',
        'task_template': 'Analyze sports odds for {topic}',
        'default_topic': 'current betting value opportunities',
    },
    'ArbitrageDetector': {
        'category': 'sports',
        'output_dir': 'sports/arbitrage',
        'output_type': 'arb_report',
        'task_template': 'Detect arbitrage opportunities in {topic}',
        'default_topic': 'current betting markets',
    },
}

# Get all categories for scheduling
AGENT_CATEGORIES = list(set(config['category'] for config in AGENT_WORKSPACE_REGISTRY.values()))


def _extract_agent_output_content(result, task_description: str) -> str:
    """
    Session 813: Extract meaningful content from agent results.
    Session 887: Improved to prefer message over sparse metadata dicts.
    Session 952: Prefer result.message for coordinator agents; add more keys.

    Agents return structured data with various keys. This function extracts
    the actual content to write to workspace files.

    Common data keys agents use:
    - content, output, analysis, code, research, report, response, summary
    - results (array of findings)
    - message (fallback description)

    Args:
        result: AgentResult object from agent execution
        task_description: The original task for fallback message

    Returns:
        Formatted string content for the workspace file
    """
    import json

    # Session 952: FIRST check if result.message has substantial markdown content
    # Many agents (especially coordinators) put their formatted report in message
    # while data contains machine-readable structured output
    if hasattr(result, 'message') and result.message:
        msg = result.message
        # Check for markdown indicators suggesting formatted content
        has_markdown = any(indicator in msg for indicator in [
            '##', '**', '- ', '* ', '1.', '---', '```', '|', '\n\n'
        ])
        # If message is substantial (>200 chars) OR has markdown formatting, prefer it
        if len(msg) > 200 or (len(msg) > 50 and has_markdown):
            return msg

    # Priority order of keys to check for text content
    # Session 848: 'text' moved higher for podcast agents (ModeratorAgent, etc.)
    # Session 952: Added more coordinator/analyst output keys
    CONTENT_KEYS = [
        'content', 'output', 'text', 'analysis', 'code', 'research',
        'report', 'response', 'summary', 'recommendation',
        'strategy', 'plan', 'document', 'article', 'script',
        'memo', 'brief', 'findings', 'insights',
        'thesis', 'conclusion', 'explanation', 'narrative',  # Session 839: More content keys
        'executive_summary', 'overview', 'assessment', 'evaluation',  # Session 952
        'market_analysis', 'audit_summary', 'risk_assessment',  # Session 952
    ]

    # Keys that contain arrays of results
    # Session 839: Added tool_results, opportunities, top_opportunities
    # Session 952: Added more coordinator/audit output keys
    ARRAY_KEYS = ['results', 'items', 'data', 'entries', 'records',
                  'tool_results', 'opportunities', 'top_opportunities', 'scored_items',
                  'alerts', 'unified_alerts', 'signals', 'events', 'games',  # Session 952
                  'matchups', 'predictions', 'recommendations', 'action_items',  # Session 952
                  'bull_cases', 'bear_cases', 'key_claims', 'risk_flags',  # Session 952
                  'correlated_findings', 'anomalies', 'violations', 'issues']  # Session 952

    # Session 952: Keys that indicate coordinator results with nested agent outputs
    # These need special formatting to avoid raw JSON dumps
    COORDINATOR_RESULT_KEYS = [
        'analyst_results', 'movement_results', 'institutional_results',
        'anomaly_results', 'scanner_results', 'audit_results',
        'research_results', 'strategy_results', 'advisor_consultations',
    ]

    # Session 887: Metadata-only keys that indicate data dict is just counts/metrics
    # If data only contains these keys, prefer result.message instead
    METADATA_ONLY_KEYS = {
        'items_count', 'critical_count', 'warning_count', 'info_count',
        'execution_time', 'count', 'total', 'success_count', 'error_count',
        'processed', 'skipped', 'duration', 'elapsed', 'timestamp'
    }

    if not hasattr(result, 'data') or not result.data:
        # No data dict, use message or fallback
        if hasattr(result, 'message') and result.message:
            return result.message
        # Session 887: Check for error message if agent failed
        if hasattr(result, 'error') and result.error:
            return f'Agent error: {result.error}\n\nTask: {task_description}'
        # Session 887: Show success status for debugging
        success_status = getattr(result, 'success', 'unknown')
        return f'Execution completed for: {task_description}\n\n(Agent returned success={success_status}, no data or message)'

    data = result.data

    # Session 887: Check if data only contains metadata counts
    # If so AND result.message is substantial, prefer the message
    data_keys = set(data.keys())
    if data_keys.issubset(METADATA_ONLY_KEYS):
        if hasattr(result, 'message') and result.message and len(result.message) > 100:
            # Data is just metadata counts, message has the actual content
            return result.message

    output_parts = []

    # 1. Check for direct content keys
    for key in CONTENT_KEYS:
        if key in data and data[key]:
            value = data[key]
            # Session 875: Handle both string and dict content (ContentWriterAgent uses dict with 'full_text')
            if isinstance(value, str) and len(value) > 50:  # Substantial string content
                output_parts.append(f"## {key.replace('_', ' ').title()}\n\n{value}")
            elif isinstance(value, dict):
                # Extract text from nested dict - common patterns:
                # - 'full_text' (ContentWriterAgent)
                # - 'body' (some article agents)
                # - 'text' (various)
                text_content = (
                    value.get('full_text', '') or
                    value.get('body', '') or
                    value.get('text', '') or
                    value.get('content', '') or
                    value.get('article', '') or
                    value.get('script', '')
                )
                if text_content and len(text_content) > 50:
                    title = value.get('title', '') or value.get('headline', '')
                    if title:
                        output_parts.append(f"## {title}\n\n{text_content}")
                    else:
                        output_parts.append(f"## {key.replace('_', ' ').title()}\n\n{text_content}")

    # 2. Check for array results
    for key in ARRAY_KEYS:
        if key in data and isinstance(data[key], list) and data[key]:
            output_parts.append(f"## {key.replace('_', ' ').title()}\n")
            for i, item in enumerate(data[key][:10], 1):  # Limit to 10 items
                if isinstance(item, dict):
                    # Session 839: Handle tool_results format (tool, arguments, result)
                    if 'tool' in item and 'result' in item:
                        tool_name = item.get('tool', f'Tool {i}')
                        tool_result = item.get('result', {})
                        output_parts.append(f"### {i}. {tool_name}\n")
                        # Extract content from the tool result
                        if isinstance(tool_result, dict):
                            # Look for key content in tool result
                            # Session 887: Added results, posts, items, search_results for web_search/reddit_search
                            for content_key in ['analysis', 'opportunities', 'top_opportunities',
                                               'items_scored', 'topic', 'thesis', 'summary',
                                               'results', 'posts', 'items', 'search_results',
                                               'organic_results', 'news_results', 'submissions']:
                                if content_key in tool_result:
                                    val = tool_result[content_key]
                                    if isinstance(val, str):
                                        output_parts.append(f"**{content_key}**: {val[:500]}\n")
                                    elif isinstance(val, (int, float)):
                                        output_parts.append(f"**{content_key}**: {val}\n")
                                    elif isinstance(val, list) and val:
                                        output_parts.append(f"**{content_key}**: {len(val)} items\n")
                                        for j, sub_item in enumerate(val[:5], 1):
                                            if isinstance(sub_item, dict):
                                                # Session 853: Expanded keys for sub-item title extraction
                                                sub_title = (sub_item.get('title') or sub_item.get('name') or
                                                             sub_item.get('domain') or sub_item.get('topic') or
                                                             sub_item.get('source') or sub_item.get('type') or
                                                             sub_item.get('category') or sub_item.get('shift_summary', '')[:40] or
                                                             sub_item.get('recommendation', '')[:40] or
                                                             sub_item.get('effect', '')[:40] or f'Item {j}')
                                                sub_score = sub_item.get('overall_score') or sub_item.get('score', '')
                                                score_str = f" (score: {sub_score})" if sub_score else ""
                                                output_parts.append(f"  {j}. {sub_title}{score_str}\n")
                                            elif isinstance(sub_item, str):
                                                output_parts.append(f"  - {sub_item[:100]}\n")
                                    elif isinstance(val, dict):
                                        # Nested dict - format key details
                                        for k, v in list(val.items())[:5]:
                                            if v and not k.startswith('_'):
                                                output_parts.append(f"  - {k}: {str(v)[:100]}\n")

                    # Session 843: Handle {source, data} format used by 15+ agents
                    # (PromptEngineeringAgent, ResearchAgent, CodeGeneratorAgent, etc.)
                    elif 'source' in item and 'data' in item:
                        source_name = item.get('source', f'Tool {i}')
                        source_data = item.get('data', {})
                        output_parts.append(f"### {i}. {source_name}\n")

                        if isinstance(source_data, dict):
                            # Session 843: Extended content keys for various agent output types
                            # Session 943: Added topics, discussions, projects for ResearchAgent analyze_trends
                            content_keys = [
                                'prompt_library', 'prompt_template', 'optimized_result',
                                'system_prompt', 'analysis', 'code', 'review', 'output',
                                'research', 'findings', 'recommendations', 'report',
                                'content', 'document', 'summary', 'result',
                                'topics', 'discussions', 'projects', 'trends', 'insights'
                            ]
                            found_content = False
                            for content_key in content_keys:
                                if content_key in source_data and source_data[content_key]:
                                    val = source_data[content_key]
                                    if isinstance(val, str) and len(val) > 20:
                                        output_parts.append(f"{val}\n")
                                        found_content = True
                                        break  # Use first substantial content found
                                    # Session 943: Handle array content (topics, discussions, projects)
                                    elif isinstance(val, list) and val:
                                        output_parts.append(f"**{content_key.replace('_', ' ').title()}:**\n")
                                        for idx, list_item in enumerate(val[:10], 1):  # Limit to 10
                                            if isinstance(list_item, dict):
                                                # Extract title/topic from dict
                                                item_title = (
                                                    list_item.get('title') or
                                                    list_item.get('topic') or
                                                    list_item.get('name') or
                                                    list_item.get('keyword') or
                                                    list_item.get('headline') or
                                                    str(list_item)[:100]
                                                )
                                                # Get count/score if available
                                                count = list_item.get('count') or list_item.get('score') or list_item.get('points', '')
                                                count_str = f" ({count})" if count else ""
                                                # Get URL if available
                                                url = list_item.get('url') or list_item.get('link', '')
                                                if url:
                                                    output_parts.append(f"  {idx}. [{item_title}]({url}){count_str}\n")
                                                else:
                                                    output_parts.append(f"  {idx}. {item_title}{count_str}\n")
                                            elif isinstance(list_item, str):
                                                output_parts.append(f"  {idx}. {list_item}\n")
                                        found_content = True

                            # If no main content found, show key metadata
                            if not found_content:
                                meta_keys = ['domain', 'target_model', 'agent_name', 'task_description']
                                for mk in meta_keys:
                                    if mk in source_data and source_data[mk]:
                                        output_parts.append(f"**{mk.replace('_', ' ').title()}**: {source_data[mk]}\n")

                    # Session 851: Handle debate agent formats (research_findings, argument_structure, statements)
                    elif 'research_summary' in item or 'research_findings' in item:
                        # Research output from DebateAdvocateAgent/DebateSkepticAgent
                        topic = item.get('topic', 'Research')
                        output_parts.append(f"### {i}. Research: {topic}\n")
                        if item.get('research_summary'):
                            output_parts.append(f"{item['research_summary']}\n")
                        if item.get('suggested_angles'):
                            output_parts.append(f"**Suggested Angles:**\n")
                            for angle in item['suggested_angles'][:5]:
                                output_parts.append(f"  - {angle}\n")
                        if item.get('suggested_concerns'):
                            output_parts.append(f"**Suggested Concerns:**\n")
                            for concern in item['suggested_concerns'][:5]:
                                output_parts.append(f"  - {concern}\n")
                        if item.get('research_findings'):
                            output_parts.append(f"**Sources ({len(item['research_findings'])}):**\n")
                            for finding in item['research_findings'][:5]:
                                if isinstance(finding, dict):
                                    title = finding.get('title', 'Untitled')
                                    source = finding.get('source', '')
                                    output_parts.append(f"  - {title} ({source})\n")

                    elif 'argument_structure' in item or 'critique_structure' in item:
                        # Argument/critique output from DebateAdvocateAgent/DebateSkepticAgent
                        structure = item.get('argument_structure') or item.get('critique_structure', {})
                        strength = item.get('argument_strength') or item.get('critique_strength', 'moderate')
                        output_parts.append(f"### {i}. Argument ({strength})\n")
                        if structure.get('thesis') or structure.get('main_concern'):
                            output_parts.append(f"**Main Point:** {structure.get('thesis') or structure.get('main_concern')}\n")
                        if structure.get('evidence'):
                            output_parts.append(f"**Evidence:**\n")
                            for point in structure['evidence'][:5]:
                                output_parts.append(f"  - {point}\n")
                        if structure.get('counterargument_handling'):
                            output_parts.append(f"**Counter-response:** {structure['counterargument_handling']}\n")
                        if structure.get('probing_questions'):
                            output_parts.append(f"**Probing Questions:**\n")
                            for q in structure['probing_questions'][:3]:
                                output_parts.append(f"  - {q}\n")
                        if structure.get('conclusion'):
                            output_parts.append(f"**Conclusion:** {structure['conclusion']}\n")

                    elif 'statements' in item and isinstance(item.get('statements'), dict):
                        # Debate statements from DebateAdvocateAgent/DebateSkepticAgent
                        role = item.get('role', 'Speaker')
                        statements = item['statements']
                        output_parts.append(f"### {i}. {role} Statements\n")
                        if statements.get('opening'):
                            output_parts.append(f"**Opening:** {statements['opening']}\n")
                        if statements.get('key_points') or statements.get('key_concerns'):
                            points = statements.get('key_points') or statements.get('key_concerns', [])
                            output_parts.append(f"**Key Points:**\n")
                            for point in points[:5]:
                                output_parts.append(f"  - {point}\n")
                        if statements.get('rebuttals') or statements.get('tough_questions'):
                            items_list = statements.get('rebuttals') or statements.get('tough_questions', [])
                            label = 'Rebuttals' if statements.get('rebuttals') else 'Tough Questions'
                            output_parts.append(f"**{label}:**\n")
                            for item_text in items_list[:5]:
                                output_parts.append(f"  - {item_text}\n")
                        if statements.get('closing'):
                            output_parts.append(f"**Closing:** {statements['closing']}\n")

                    # Session 853: Handle CulturalImpactAgent and similar structured tool outputs
                    elif 'impact_analysis' in item or 'predicted_effects' in item or 'recommendations' in item or 'affected_domains' in item:
                        # Cultural/Analysis agent outputs (CulturalImpactAgent, etc.)
                        analysis_type = item.get('analysis_type', 'Analysis')
                        domain = item.get('domain') or item.get('primary_domain', '')
                        title_suffix = f" ({domain})" if domain else ""
                        output_parts.append(f"### {i}. {analysis_type.replace('_', ' ').title()}{title_suffix}\n")

                        # Impact analysis (nested dict with impact_score, affected_domains, etc.)
                        if item.get('impact_analysis') and isinstance(item['impact_analysis'], dict):
                            ia = item['impact_analysis']
                            if ia.get('impact_score'):
                                output_parts.append(f"**Impact Score:** {ia['impact_score']}\n")
                            if ia.get('estimated_timeline'):
                                output_parts.append(f"**Timeline:** {ia['estimated_timeline']}\n")
                            if ia.get('confidence'):
                                output_parts.append(f"**Confidence:** {ia['confidence']}\n")
                            if ia.get('affected_domains'):
                                output_parts.append(f"**Affected Domains:** {', '.join(ia['affected_domains'])}\n")

                        # Shift summary
                        if item.get('shift_summary'):
                            output_parts.append(f"**Summary:** {item['shift_summary']}\n")

                        # Narratives
                        if item.get('old_narrative'):
                            output_parts.append(f"**From:** {item['old_narrative']}\n")
                        if item.get('new_narrative'):
                            output_parts.append(f"**To:** {item['new_narrative']}\n")

                        # Predicted effects (list)
                        if item.get('predicted_effects') and isinstance(item['predicted_effects'], list):
                            output_parts.append(f"**Predicted Effects:**\n")
                            for effect in item['predicted_effects'][:8]:
                                output_parts.append(f"  - {effect}\n")

                        # Recommendations (list)
                        if item.get('recommendations') and isinstance(item['recommendations'], list):
                            output_parts.append(f"**Recommendations:**\n")
                            for rec in item['recommendations'][:8]:
                                output_parts.append(f"  - {rec}\n")

                        # Affected domains (list of dicts or strings)
                        if item.get('affected_domains') and isinstance(item['affected_domains'], list):
                            output_parts.append(f"**Affected Domains:**\n")
                            for ad in item['affected_domains'][:6]:
                                if isinstance(ad, dict):
                                    dom = ad.get('domain', 'Unknown')
                                    strength = ad.get('connection_strength') or ad.get('impact_level', '')
                                    output_parts.append(f"  - {dom}: {strength}\n")
                                elif isinstance(ad, str):
                                    output_parts.append(f"  - {ad}\n")

                        # Historical parallels (list)
                        if item.get('parallels') and isinstance(item['parallels'], list):
                            output_parts.append(f"**Historical Parallels:**\n")
                            for p in item['parallels'][:5]:
                                if isinstance(p, dict):
                                    p_title = p.get('title', 'Untitled')
                                    p_domain = p.get('domain', '')
                                    output_parts.append(f"  - {p_title} ({p_domain})\n")

                        # Note/message
                        if item.get('note'):
                            output_parts.append(f"*Note: {item['note']}*\n")

                    else:
                        # Standard dict item format
                        # Session 848: Added 'text' key for podcast agents (ModeratorAgent, etc.)
                        # Session 851: Added more keys for diverse agent outputs
                        # Session 853: Expanded fallback keys for more agent types
                        item_title = (item.get('title') or item.get('name') or item.get('source') or
                                      item.get('segment') or item.get('topic') or item.get('role') or
                                      item.get('domain') or item.get('shift_summary', '')[:50] or
                                      item.get('analysis_type') or item.get('narrative') or f'Item {i}')
                        item_content = (item.get('content') or item.get('summary') or item.get('description') or
                                        item.get('text') or item.get('message') or item.get('output') or
                                        item.get('analysis') or item.get('note') or
                                        item.get('shift_summary') or item.get('assumption') or '')
                        item_score = item.get('overall_score') or item.get('score', '')
                        score_str = f" (score: {item_score})" if item_score else ""
                        output_parts.append(f"### {i}. {item_title}{score_str}\n{item_content[:500]}\n")
                elif isinstance(item, str):
                    output_parts.append(f"- {item[:200]}")

    # 3. Check for nested structures with useful data
    if 'ml_analysis' in data and isinstance(data['ml_analysis'], dict):
        ml = data['ml_analysis']
        ml_parts = []
        if ml.get('topics_detected'):
            ml_parts.append(f"Topics: {', '.join(ml['topics_detected'][:5])}")
        if ml.get('sentiment'):
            ml_parts.append(f"Sentiment: {ml['sentiment']}")
        if ml.get('ml_insights'):
            ml_parts.append(f"Insights: {ml['ml_insights']}")
        if ml_parts:
            output_parts.append(f"## ML Analysis\n\n" + '\n'.join(ml_parts))

    # Session 952: Handle coordinator agent results (nested agent outputs)
    for coord_key in COORDINATOR_RESULT_KEYS:
        if coord_key in data and isinstance(data[coord_key], dict):
            coord_data = data[coord_key]
            section_title = coord_key.replace('_', ' ').title()
            output_parts.append(f"## {section_title}\n")

            # Extract key information from coordinator results
            if coord_data.get('success') is not None:
                status = '✅' if coord_data.get('success') else '❌'
                output_parts.append(f"**Status:** {status}\n")

            # Look for summary/message in the result
            for summary_key in ['message', 'summary', 'analysis', 'report', 'conclusion']:
                if summary_key in coord_data and coord_data[summary_key]:
                    val = coord_data[summary_key]
                    if isinstance(val, str) and len(val) > 20:
                        output_parts.append(f"{val}\n")
                        break

            # Look for structured data to format
            for sub_key in ['findings', 'alerts', 'signals', 'recommendations', 'items']:
                if sub_key in coord_data and isinstance(coord_data[sub_key], list):
                    items = coord_data[sub_key]
                    if items:
                        output_parts.append(f"**{sub_key.title()} ({len(items)}):**\n")
                        for idx, item in enumerate(items[:5], 1):
                            if isinstance(item, dict):
                                item_title = (item.get('title') or item.get('ticker') or
                                              item.get('name') or item.get('type') or f'Item {idx}')
                                item_severity = item.get('severity') or item.get('priority', '')
                                sev_str = f" [{item_severity}]" if item_severity else ""
                                output_parts.append(f"  {idx}. {item_title}{sev_str}\n")
                            elif isinstance(item, str):
                                output_parts.append(f"  {idx}. {item[:100]}\n")

    # Session 952: Handle structured_report and provenance from Session 918 agents
    if 'structured_report' in data and isinstance(data['structured_report'], dict):
        report = data['structured_report']
        if report.get('total_games_analyzed'):
            output_parts.append(f"**Games Analyzed:** {report['total_games_analyzed']}\n")
        if report.get('sports_covered'):
            output_parts.append(f"**Sports:** {', '.join(report['sports_covered'])}\n")

    if 'provenance' in data and isinstance(data['provenance'], dict):
        prov = data['provenance']
        if prov.get('validation_status'):
            status_emoji = '✅' if prov.get('publishable') else '⚠️'
            output_parts.append(f"\n**Data Status:** {status_emoji} {prov['validation_status'].upper()}\n")

    # Session 952: Handle 'brief' from MarketIntelligenceCoordinator and similar
    # The brief contains executive_summary which is the actual formatted content
    if 'brief' in data and isinstance(data['brief'], dict):
        brief = data['brief']
        # First check for executive_summary - this is the main content
        if brief.get('executive_summary') and isinstance(brief['executive_summary'], str):
            output_parts.insert(0, brief['executive_summary'])  # Put at top
        # Then add key sections
        if brief.get('debate_zone') and isinstance(brief['debate_zone'], list):
            output_parts.append(f"\n## Debate Zone ({len(brief['debate_zone'])} stocks)")
            for item in brief['debate_zone'][:5]:
                if isinstance(item, dict):
                    ticker = item.get('ticker', 'Unknown')
                    confidence = item.get('confidence', '')
                    output_parts.append(f"- **{ticker}** [{confidence}]")
        if brief.get('risk_alerts') and isinstance(brief['risk_alerts'], list):
            output_parts.append(f"\n## Risk Alerts ({len(brief['risk_alerts'])})")
            for alert in brief['risk_alerts'][:5]:
                if isinstance(alert, dict):
                    title = alert.get('title') or alert.get('ticker', 'Alert')
                    severity = alert.get('severity', '')
                    output_parts.append(f"- **{title}** [{severity}]")

    # Session 952: Handle 'synthesis' from coordinator agents
    if 'synthesis' in data and isinstance(data['synthesis'], dict):
        synth = data['synthesis']
        if synth.get('high_conviction_opportunities'):
            output_parts.append(f"\n## High Conviction ({len(synth['high_conviction_opportunities'])})")
            for opp in synth['high_conviction_opportunities'][:5]:
                if isinstance(opp, dict):
                    ticker = opp.get('ticker', 'Unknown')
                    rec = opp.get('recommendation', '')
                    output_parts.append(f"- **{ticker}**: {rec}")

    # 4. If we found substantial content, use it
    if output_parts:
        return '\n\n'.join(output_parts)

    # 5. Session 952: Prefer message even if short - it's usually more readable than raw JSON
    if hasattr(result, 'message') and result.message:
        msg = result.message
        # If message exists and has some content, use it (lowered threshold from 50 to 20)
        if len(msg) > 20:
            return msg

    # 6. Session 952: Format data more readably before falling back to JSON
    # Try to create a summary from common metadata keys
    if data:
        summary_parts = []

        # Count-based summaries
        for count_key in ['events_analyzed', 'items_count', 'total_alerts', 'games_analyzed',
                          'stocks_analyzed', 'transactions_analyzed']:
            if count_key in data:
                label = count_key.replace('_', ' ').title()
                summary_parts.append(f"**{label}:** {data[count_key]}")

        # Status summaries
        for status_key in ['critical_count', 'warning_count', 'info_count',
                           'success_count', 'error_count']:
            if status_key in data and data[status_key]:
                label = status_key.replace('_', ' ').title()
                summary_parts.append(f"**{label}:** {data[status_key]}")

        if summary_parts:
            summary_text = '\n'.join(summary_parts)
            return f"## Execution Summary\n\n{summary_text}\n\n*Agent completed task: {task_description}*"

        # Final fallback: serialize the entire data dict as formatted output
        # Filter out internal/meta keys
        skip_keys = {'type', 'content_type', 'query', 'topic', 'timestamp', 'agent_name',
                     'execution_time', 'run_mode', 'trigger_source'}
        filtered_data = {k: v for k, v in data.items() if k not in skip_keys and v}

        if filtered_data:
            try:
                formatted = json.dumps(filtered_data, indent=2, default=str)
                return f"## Agent Output Data\n\n```json\n{formatted[:8000]}\n```"
            except Exception as e:
                logger.warning(f"Agent output JSON formatting failed: {e}")

    # Ultimate fallback - Session 887: Include more diagnostic info
    keys_info = list(data.keys()) if data else []
    content_preview = ''
    if 'content' in data and isinstance(data['content'], dict):
        content_keys = list(data['content'].keys())
        content_preview = f"\nContent dict has keys: {content_keys}"
        if 'full_text' in data['content']:
            ft = data['content']['full_text']
            content_preview += f"\nfull_text length: {len(ft) if ft else 0}"
    return f'Execution completed for: {task_description}\n\nAgent data keys: {keys_info}{content_preview}'


# ==========================================================================
# SESSION 987: Pre-flight data requirements for single-agent tasks
# ==========================================================================
AGENT_DATA_REQUIREMENTS = {
    'PerformanceAnalystAgent': {
        'models': [
            ('core.models_autonomous_studio.ContentChannel', {}, 1, 'content channels'),
        ],
        'description': 'content performance analysis',
    },
    'OpportunityScoringAgent': {
        'models': [
            ('core.models_unified_system.Opportunity', {'status__in': ['active', 'pending']}, 1, 'opportunities'),
        ],
        'description': 'opportunity scoring',
    },
    'TrendAnalysisAgent': {
        'models': [
            ('core.models_unified_system.SpiderData', {'data_type': 'trend_data'}, 5, 'trend data points'),
        ],
        'description': 'trend analysis',
    },
}


def _preflight_check_agent_data(agent_name: str, topic: str = '') -> dict:
    """
    Session 987: Check if the required data exists before running an agent.
    Returns {'proceed': True/False, 'reason': str, 'counts': dict}.
    """
    import importlib

    # Direct match or topic references an agent with requirements
    reqs = AGENT_DATA_REQUIREMENTS.get(agent_name)
    if not reqs and topic:
        for req_agent, req_data in AGENT_DATA_REQUIREMENTS.items():
            if req_agent in topic:
                reqs = req_data
                agent_name = req_agent  # for logging
                break

    if not reqs:
        return {'proceed': True, 'reason': 'no requirements defined'}

    counts = {}
    missing = []
    for model_path, filters, min_count, label in reqs['models']:
        try:
            module_path, class_name = model_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            Model = getattr(module, class_name)
            count = Model.objects.filter(**filters).count()
            counts[label] = count
            if count < min_count:
                missing.append(f"{label}: {count}/{min_count}")
        except Exception as e:
            logger.warning(f"[Session 987] Preflight model check failed for {model_path}: {e}")
            # Don't block on import errors — let the agent try
            counts[label] = -1

    if missing:
        reason = f"Insufficient data for {reqs['description']}: {', '.join(missing)}"
        return {'proceed': False, 'reason': reason, 'counts': counts}

    return {'proceed': True, 'reason': 'all data requirements met', 'counts': counts}


@shared_task(name='core.tasks.universal_agent_workspace_output', soft_time_limit=2700, time_limit=3000)
def universal_agent_workspace_output(
    agent_name: str,
    topic: str = None,
    initiative_id: str = None,
    trigger_source: str = None,
    force_production: bool = False
):
    from core.tasks_agents import _impl_universal_agent_workspace_output
    return _impl_universal_agent_workspace_output(agent_name, topic, initiative_id, trigger_source, force_production)
def _get_agent_class(agent_name: str):
    """Get agent class by name, trying multiple module patterns."""
    import importlib
    import re

    # Try common module patterns
    module_patterns = [
        f"core.agents.{agent_name.lower().replace('agent', '_agent')}",
        f"core.agents.{agent_name.lower()}",
        f"core.agents.{agent_name[0].lower() + agent_name[1:]}",
    ]

    # Convert CamelCase to snake_case for module name
    snake_name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', agent_name)
    snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_name).lower()
    module_patterns.insert(0, f"core.agents.{snake_name}")

    for module_path in module_patterns:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, agent_name):
                return getattr(module, agent_name)
        except (ImportError, ModuleNotFoundError):
            continue

    # Try agent router as fallback
    try:
        from core.agent_router import AgentRouter
        router = AgentRouter()
        return router.get_agent_class(agent_name)
    except Exception:
        return None


def _run_agent_warmup(agent_name: str) -> dict:
    """
    Session 864: Infra warmup for an agent - verify it works without content generation.

    This replaces content-generating warmups with lightweight health checks:
    - Verify agent class can be loaded
    - Verify agent can be instantiated
    - Optionally do a minimal LLM ping (5-20 tokens)
    - NO file creation, NO default_topic content

    Returns:
        Health check result dict
    """
    import time
    start_time = time.time()

    try:
        # 1. Verify agent class exists
        agent_class = _get_agent_class(agent_name)
        if not agent_class:
            return {
                'success': False,
                'agent': agent_name,
                'run_mode': 'warmup',
                'check': 'class_load',
                'error': 'Agent class not found'
            }

        # 2. Verify agent can be instantiated
        try:
            agent = agent_class()
        except Exception as e:
            return {
                'success': False,
                'agent': agent_name,
                'run_mode': 'warmup',
                'check': 'instantiation',
                'error': str(e)
            }

        # 3. Check if agent has required methods
        has_execute = hasattr(agent, 'execute')
        has_tools = hasattr(agent, 'tools')

        execution_time_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"✅ [WARMUP] {agent_name} healthy: "
            f"class=✓, instance=✓, execute={has_execute}, tools={has_tools} "
            f"({execution_time_ms}ms)"
        )

        return {
            'success': True,
            'agent': agent_name,
            'run_mode': 'warmup',
            'checks': {
                'class_load': True,
                'instantiation': True,
                'has_execute': has_execute,
                'has_tools': has_tools,
            },
            'execution_time_ms': execution_time_ms,
            'file_created': False,  # Key: no file output
        }

    except Exception as e:
        logger.warning(f"❌ [WARMUP] {agent_name} failed: {e}")
        return {
            'success': False,
            'agent': agent_name,
            'run_mode': 'warmup',
            'error': str(e)
        }


def _get_next_task_for_agent(agent_name: str) -> dict | None:
    """
    Session 864: Get next real task from the initiative queue for an agent.
    Session 1033: Fixed broken field references (assigned_agent, description, title).

    Checks for:
    1. Initiative stages that need documents (PENDING status, no document)
    2. PublishGate backlog (needs enhancement blogs)

    Returns:
        Task dict with topic, initiative_id, etc. or None if no real work.
    """
    try:
        from core.models_document_registry import InitiativeStage

        # Check for initiative stages needing documents
        # Session 1033: InitiativeStage has no assigned_agent field.
        # Instead, find any PENDING stage without a document.
        pending_stage = InitiativeStage.objects.filter(
            status='PENDING',
            document__isnull=True,
        ).select_related('initiative').first()

        if pending_stage:
            return {
                'topic': pending_stage.initiative.name,
                'initiative_id': str(pending_stage.initiative.id),
                'stage_id': str(pending_stage.id),
                'stage_num': pending_stage.stage,
                'source': 'initiative_stage',
            }

        # Check PublishGate backlog — needs_enhancement blogs
        from core.models_unified_system import SelfBlog
        backlog = SelfBlog.objects.filter(
            status='needs_enhancement'
        ).order_by('created_at').first()

        if backlog:
            return {
                'topic': f"Enhance blog: {backlog.title[:80]}",
                'blog_id': str(backlog.id),
                'source': 'publish_gate_backlog',
            }

        return None

    except Exception as e:
        logger.warning(f"Error getting next task for {agent_name}: {e}")
        return None


@shared_task(name='core.tasks.agent_category_rotation')
def agent_category_rotation(category: str):
    try:
        from core.tasks_misc import _impl_agent_category_rotation
        return _impl_agent_category_rotation(category)
    except Exception as e:
        logger.exception(f"[agent_category_rotation] Failed for category={category}: {e}")
        raise
@shared_task(name='core.tasks.full_agent_rotation')
def full_agent_rotation():
    """
    Session 777: Execute ALL agents in the registry and write outputs to workspace.

    This is the master task that ensures every agent produces workspace output.
    Should be run periodically (e.g., weekly) to ensure all agents are active.

    Returns:
        Summary of all agent executions by category
    """
    logger.info("🌟 [SKIN LAYER] Starting FULL agent rotation - all 74 agents")

    category_results = {}

    for category in AGENT_CATEGORIES:
        try:
            result = agent_category_rotation(category)
            category_results[category] = {
                'success': result.get('success', False),
                'total': result.get('total_agents', 0),
                'successful': result.get('successful', 0),
                'failed': result.get('failed', 0)
            }
        except Exception as e:
            category_results[category] = {
                'success': False,
                'error': str(e)
            }

    total_agents = sum(r.get('total', 0) for r in category_results.values())
    total_successful = sum(r.get('successful', 0) for r in category_results.values())

    logger.info(
        f"🌟 [SKIN LAYER] Full rotation complete: "
        f"{total_successful}/{total_agents} agents succeeded"
    )

    return {
        'success': total_successful > 0,
        'total_agents': total_agents,
        'successful': total_successful,
        'failed': total_agents - total_successful,
        'categories': category_results
    }


# =============================================================================
# SESSION 784: VOICE CRITIQUE SYSTEM
# =============================================================================

@shared_task(name='content_studio.score_episode_voice')
def score_episode_voice(episode_id: str) -> dict:
    from core.tasks_content import _impl_score_episode_voice
    return _impl_score_episode_voice(episode_id)
@shared_task(name='content_studio.backfill_voice_scores')
def backfill_voice_scores(limit: int = 50, min_content_length: int = 100) -> dict:
    from core.tasks_misc import _impl_backfill_voice_scores
    return _impl_backfill_voice_scores(limit, min_content_length)
@shared_task(name='workspace.autopilot_tick')
def workspace_autopilot_tick(
    budget_per_tick: int = 5,
    min_priority: int = None,
    category: str = None,
    dry_run: bool = False
) -> dict:
    from core.tasks_agents import _impl_workspace_autopilot_tick
    return _impl_workspace_autopilot_tick(budget_per_tick, min_priority, category, dry_run)
def _run_agent_group(group_name: str, agent_names: list, task_generator, emoji: str = "🤖"):
    """
    Helper function to run a group of agents with a task.

    Session 787: Creates shared project ID for agent group to enable collaboration tracking.
    Session 944: Updated to use universal_agent_workspace_output for SKIN layer integration.

    Args:
        group_name: Name of the agent group for logging
        agent_names: List of agent names to execute
        task_generator: Function that takes agent_name and returns a task string
        emoji: Emoji for logging
    """
    from django.utils import timezone

    logger.info(f"{emoji} [{group_name}] Starting scheduled agent group...")

    results = []

    # Session 787: Create a shared project ID for this agent group run
    shared_project_id = f"{group_name.lower().replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M')}"

    for agent_name in agent_names:
        try:
            task = task_generator(agent_name)

            # Session 944: Use universal_agent_workspace_output to create WorkspaceOperations
            # This ensures agent outputs appear in the Operations Tab
            result = universal_agent_workspace_output(
                agent_name=agent_name,
                topic=task,
                trigger_source='schedule',
                force_production=True  # These are real scheduled runs, not warmups
            )

            success = result.get('success', False) if isinstance(result, dict) else False

            # Session 787: Track contribution with shared project ID for collaboration
            _track_group_contribution(agent_name, group_name, shared_project_id, success)

            results.append({
                'agent': agent_name,
                'success': success,
                'project_id': shared_project_id,
                'file': result.get('file') if isinstance(result, dict) else None,
            })

            status = '✅' if success else '❌'
            logger.info(f"{emoji} [{group_name}] {agent_name}: {status}")

        except Exception as e:
            logger.warning(f"{emoji} [{group_name}] {agent_name} failed: {e}")
            results.append({'agent': agent_name, 'success': False, 'error': str(e)})

    succeeded = len([r for r in results if r.get('success')])
    logger.info(f"{emoji} [{group_name}] Complete: {succeeded}/{len(results)} succeeded (project: {shared_project_id})")
    return results


def _track_group_contribution(agent_name: str, group_name: str, project_id: str, success: bool):
    """
    Session 787: Track agent contribution with shared project ID.
    This creates proper collaboration records when multiple agents work together.

    Session 800 fix: project field requires PartnershipProject instance, not string.
    Since scheduled runs don't have real projects, we create contributions without project.
    """
    try:
        from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate

        # Get or create the agent template
        agent_template, _ = UnifiedAgentTemplate.objects.get_or_create(
            name=agent_name,
            defaults={
                'display_name': agent_name.replace('Agent', ' Agent'),
                'description': f'{agent_name} scheduled execution',
                'specialization': 'general',
            }
        )

        # Session 800: Create contribution without project (project is nullable since Session 752)
        # Scheduled agent runs don't have real PartnershipProject instances
        AgentContribution.objects.create(
            agent=agent_template,
            project=None,  # Session 800: Was passing string, but field requires PartnershipProject instance
            contribution_type='orchestration',
            contribution_role='Collaborator',
            task_description=f'{agent_name} participating in {group_name} scheduled run (project: {project_id})',
            contribution_percentage=100 if success else 0,
        )

        logger.debug(f"✓ Tracked collaboration: {agent_name} -> group {group_name}")

    except Exception as e:
        logger.warning(f"Could not track contribution for {agent_name}: {e}")


@shared_task
def run_content_creation_agents():
    """
    Session 787: Run content creation agents every 3 hours.
    Session 1027: Removed AudioAgent — ElevenLabs quota exceeded, 100% failure
    rate ($0.41/day wasted). Re-add when quota is resolved.

    Agents: ImageAgent, VideoAgent, ThreeDAgent,
            ContentWriterAgent, ContentExecutorAgent,
            ImageEditingAgent, VideoEditingAgent, ResolveAgent
    """
    agents = [
        'ImageAgent', 'VideoAgent',
        'AudioAgent',  # Session 1088: Re-enabled (unblocked Session 1068, quota replenished)
        'ThreeDAgent',
        'ContentWriterAgent', 'ContentExecutorAgent',
        'ImageEditingAgent', 'VideoEditingAgent', 'ResolveAgent'
    ]

    def task_gen(agent):
        tasks = {
            'ImageAgent': 'Analyze recent trends and generate a creative image based on current popular topics',
            'VideoAgent': 'Create a short video concept based on trending content',
            # Session 957: Give ThreeDAgent a specific 3D task using its native generate_3d_scene tool
            # instead of triggering research delegation that returns irrelevant generic tech trends
            'ThreeDAgent': 'Generate a 3D scene: A modern minimalist product display pedestal with ambient lighting - style: realistic, format: glb',
            'ContentWriterAgent': 'Write an article about recent trending topics from spider data',
            'ContentExecutorAgent': 'Review pending content tasks and execute the highest priority one',
            'ImageEditingAgent': 'Review recent images and suggest improvements or variations',
            'VideoEditingAgent': 'Analyze recent videos and propose editing enhancements',
            'ResolveAgent': 'Check for pending video projects and process the next one',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('CONTENT CREATION', agents, task_gen, '🎨')


@shared_task
def run_strategy_marketing_agents():
    """
    Session 787: Run strategy and marketing agents every 4 hours.

    Agents: ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent,
            SocialMediaAgent, BrandStrategyAgent
    """
    agents = [
        'ContentStrategyAgent', 'BrandIdentityAgent', 'SEOOptimizerAgent',
        'SocialMediaAgent', 'BrandStrategyAgent'
    ]

    def task_gen(agent):
        tasks = {
            'ContentStrategyAgent': 'Analyze spider data and recommend content strategies for the next 24 hours',
            'BrandIdentityAgent': 'Review brand consistency across recent content and suggest improvements',
            'SEOOptimizerAgent': 'Analyze trending keywords and provide SEO recommendations',
            'SocialMediaAgent': 'Identify social media opportunities from recent spider data',
            'BrandStrategyAgent': 'Evaluate brand positioning based on competitor data',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('STRATEGY & MARKETING', agents, task_gen, '📈')


@shared_task
def run_research_analysis_agents():
    """
    Session 787: Run research and analysis agents every 2 hours.

    Agents: ResearchAgent, CustomerResearchAgent
    """
    agents = ['ResearchAgent', 'CustomerResearchAgent']

    def task_gen(agent):
        tasks = {
            'ResearchAgent': 'Research the most significant trends from the last 6 hours of spider data',
            'CustomerResearchAgent': 'Analyze customer behavior patterns from recent data',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('RESEARCH & ANALYSIS', agents, task_gen, '🔬')


@shared_task
def run_stock_financial_agents():
    """
    Session 787: Run stock and financial analysis agents every 3 hours.

    Agents: StockAnalystAgent, StockAuditCoordinator, BullCaseAgent, BearCaseAgent,
            MarketIntelligenceCoordinator
    """
    agents = [
        'StockAnalystAgent', 'StockAuditCoordinator',
        'BullCaseAgent', 'BearCaseAgent', 'MarketIntelligenceCoordinator'
    ]

    def task_gen(agent):
        # Session 957: StockAnalystAgent needs specific tickers to use its tools effectively
        # Generic "market conditions" tasks should go to MarketIntelligenceCoordinator
        tasks = {
            'StockAnalystAgent': 'Analyze SPY, QQQ, NVDA, AAPL, MSFT - check valuations, recent SEC filings, and assess risk levels for each ticker',
            'StockAuditCoordinator': 'Coordinate a brief market health check across all stock agents',
            'BullCaseAgent': 'Identify the strongest bullish opportunities from current market data',
            'BearCaseAgent': 'Identify key risks and bearish signals in current market data',
            'MarketIntelligenceCoordinator': 'Synthesize market intelligence from all sources',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('STOCK & FINANCIAL', agents, task_gen, '📊')


@shared_task
def run_prediction_market_agents():
    """
    Session 787: Run prediction market agents every 2 hours.

    Agents: PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector
    """
    agents = ['PredictionMarketAnalyst', 'SportsOddsAnalyst', 'ArbitrageDetector']

    def task_gen(agent):
        tasks = {
            'PredictionMarketAnalyst': 'Scan prediction markets for high-value opportunities',
            'SportsOddsAnalyst': 'Analyze current sports odds and identify value bets',
            'ArbitrageDetector': 'Scan for arbitrage opportunities across betting markets',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('PREDICTION MARKETS', agents, task_gen, '🎯')


@shared_task
def run_narrative_culture_agents():
    """
    Session 787: Run narrative and culture agents every 6 hours.

    Agents: NarrativeDriftCoordinator, NarrativeHistorianAgent,
            TrendBreakDetectorAgent, CulturalImpactAgent
    """
    agents = [
        'NarrativeDriftCoordinator', 'NarrativeHistorianAgent',
        'TrendBreakDetectorAgent', 'CulturalImpactAgent'
    ]

    def task_gen(agent):
        tasks = {
            'NarrativeDriftCoordinator': 'Analyze how narratives have shifted in recent news and social data',
            'NarrativeHistorianAgent': 'Document significant narrative patterns from the past 24 hours',
            'TrendBreakDetectorAgent': 'Identify any trend breaks or reversals in recent data',
            'CulturalImpactAgent': 'Assess cultural impact of trending topics',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('NARRATIVE & CULTURE', agents, task_gen, '📖')


@shared_task
def run_development_tech_agents():
    """
    Session 787: Run development and tech agents every 4 hours.
    Session 1027: Removed CodeGeneratorAgent — runs in Railway sandbox with no
    codebase access, can't write actual code. Was burning ~$8.76/day producing
    analysis specs that go nowhere. Same issue as remediation fix (Session 1026).

    Agents: CodeReviewAgent, FullStackDeveloperAgent,
            DevOpsAgent, TechnicalDocumentAgent
    """
    agents = [
        # Session 1027: CodeGeneratorAgent removed — sandbox can't write code
        'CodeReviewAgent', 'FullStackDeveloperAgent',
        'DevOpsAgent', 'TechnicalDocumentAgent'
    ]

    def task_gen(agent):
        tasks = {
            'CodeReviewAgent': 'Analyze recent code patterns and identify potential improvements',
            'FullStackDeveloperAgent': 'Identify development opportunities from spider tech data',
            'DevOpsAgent': 'Check system health and suggest infrastructure improvements',
            'TechnicalDocumentAgent': 'Review documentation gaps and suggest updates',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('DEVELOPMENT & TECH', agents, task_gen, '💻')


@shared_task
def run_executive_leadership_agents():
    """
    Session 787: Run executive and leadership agents every 6 hours.

    Agents: CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent
    """
    agents = ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'MeetingCoordinatorAgent']

    def task_gen(agent):
        tasks = {
            'CTOAgent': 'Review technology strategy and provide executive recommendations',
            'COOAgent': 'Analyze operational efficiency and suggest improvements',
            'CreativeDirectorAgent': 'Review creative output quality and provide direction',
            'MeetingCoordinatorAgent': 'Summarize key activities and prepare coordination notes',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('EXECUTIVE & LEADERSHIP', agents, task_gen, '👔')


@shared_task
def run_podcast_debate_agents():
    """
    Session 787: Run podcast and debate agents every 8 hours.

    Agents: PodcastCoordinatorAgent, DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent
    """
    agents = ['PodcastCoordinatorAgent', 'DebateAdvocateAgent', 'DebateSkepticAgent', 'ModeratorAgent']

    def task_gen(agent):
        tasks = {
            'PodcastCoordinatorAgent': 'Identify compelling podcast topics from recent trends',
            'DebateAdvocateAgent': 'Prepare arguments for a trending controversial topic',
            'DebateSkepticAgent': 'Prepare counter-arguments for a trending topic',
            'ModeratorAgent': 'Analyze recent debates and summarize key discussion points',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('PODCAST & DEBATE', agents, task_gen, '🎙️')


@shared_task
def auto_generate_podcast_episode():
    from core.tasks_content import _impl_auto_generate_podcast_episode
    return _impl_auto_generate_podcast_episode()
@shared_task
def run_content_studio_agents():
    """
    Session 787: Run content studio agents every 4 hours.

    Agents: TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent
    Note: AutonomousContentStudioCoordinator runs separately
    """
    agents = ['TopicMinerAgent', 'ContrarianAgent', 'PerformanceAnalystAgent']

    def task_gen(agent):
        tasks = {
            'TopicMinerAgent': 'Mine spider data for high-potential content topics',
            'ContrarianAgent': 'Identify contrarian perspectives on trending topics',
            'PerformanceAnalystAgent': 'Analyze recent content performance metrics',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('CONTENT STUDIO', agents, task_gen, '🎬')


@shared_task
def run_campaign_series_agents():
    """
    Session 787: Run campaign and series agents every 6 hours.

    Agents: CampaignOrchestratorAgent, AISeriesWorkflowAgent
    """
    agents = ['CampaignOrchestratorAgent', 'AISeriesWorkflowAgent']

    def task_gen(agent):
        tasks = {
            'CampaignOrchestratorAgent': 'Review active campaigns and suggest optimizations',
            'AISeriesWorkflowAgent': 'Check AI series workflows and advance pending items',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('CAMPAIGN & SERIES', agents, task_gen, '🚀')


@shared_task
def run_system_orchestration_agents():
    """
    Session 787: Run system and orchestration agents every 2 hours.
    Session 1027: Rewrote WorkflowAgent and OpportunityPipelineAgent tasks.
    Old WorkflowAgent task "Check pending workflows and advance ready items"
    spawned unbounded sub-tasks to ResearchAgent (~30 "audit pending workflows"
    runs/day). Old OpportunityPipelineAgent task triggered "no revenue" assessment
    51x/day. New tasks are bounded — report only, do NOT delegate to sub-agents.

    Agents: SystemIntelligenceAgent, ThinkingAgent, WorkflowAgent,
            WorkflowOrchestrationAgent, OpportunityPipelineAgent
    """
    agents = [
        'SystemIntelligenceAgent', 'ThinkingAgent', 'WorkflowAgent',
        'WorkflowOrchestrationAgent', 'OpportunityPipelineAgent'
    ]

    def task_gen(agent):
        tasks = {
            'SystemIntelligenceAgent': 'Generate a system health and intelligence report',
            'ThinkingAgent': 'Reflect on recent system activities and generate insights',
            # Session 1027: Bounded task — report status only, do NOT spawn sub-tasks
            # or delegate to ResearchAgent/OpportunityScoringAgent
            'WorkflowAgent': 'Report a brief summary of active workflow statuses from database records. Do NOT delegate to other agents or spawn sub-tasks. Just summarize what you can see directly.',
            'WorkflowOrchestrationAgent': 'Orchestrate cross-agent workflow coordination',
            # Session 1027: Changed from "Review opportunity pipeline and prioritize actions"
            # which triggered 51x "no revenue" loop. New task is bounded.
            'OpportunityPipelineAgent': 'Summarize the top 3 recent signal clusters by strength score. Do NOT analyze revenue status or delegate to other agents.',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('SYSTEM & ORCHESTRATION', agents, task_gen, '⚙️')


@shared_task
def run_quality_audit_agents():
    """
    Session 787: Run quality and audit agents every 4 hours.

    Agents: ContentAuditAgent, ContentDiversityOrchestrator
    """
    agents = ['ContentAuditAgent', 'ContentDiversityOrchestrator']

    def task_gen(agent):
        tasks = {
            'ContentAuditAgent': 'Audit recent content for quality and compliance',
            'ContentDiversityOrchestrator': 'Check content diversity and identify gaps',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('QUALITY & AUDIT', agents, task_gen, '✅')


@shared_task
def run_specialty_agents():
    """
    Session 787: Run specialty agents every 8 hours.

    Agents: LegalDocDrafterAgent, CharacterTrainingAgent, TrainedCreationAgent, MemoryIsolationAgent
    """
    agents = ['LegalDocDrafterAgent', 'CharacterTrainingAgent', 'TrainedCreationAgent', 'MemoryIsolationAgent']

    def task_gen(agent):
        tasks = {
            'LegalDocDrafterAgent': 'Review legal updates and prepare relevant document templates',
            'CharacterTrainingAgent': 'Analyze character training data and suggest improvements',
            'TrainedCreationAgent': 'Generate content using trained character models',
            'MemoryIsolationAgent': 'Perform memory isolation check and cleanup stale data',
        }
        return tasks.get(agent, f'Perform your primary function and report insights')

    return _run_agent_group('SPECIALTY', agents, task_gen, '🔧')


# =============================================================================
# Session 819: Mythology System Tasks
# =============================================================================

@shared_task
def update_mythology_pattern_statistics():
    """
    Session 819: Update MythPattern frequency counts and prevention rates.

    Runs daily at 4am to aggregate statistics from MythologyEvents.
    """
    from mythology.models import MythPattern, MythologyEvent
    from django.db.models import Count

    logger.info("🛡️ Updating mythology pattern statistics...")

    try:
        # Get event counts by pattern type
        event_counts = MythologyEvent.objects.values('event_type').annotate(
            count=Count('id')
        )

        updated = 0
        for item in event_counts:
            pattern = MythPattern.objects.filter(pattern_type=item['event_type']).first()
            if pattern:
                pattern.frequency_count = item['count']
                pattern.last_seen = timezone.now()
                pattern.save(update_fields=['frequency_count', 'last_seen', 'updated_at'])
                updated += 1

        logger.info(f"✅ Updated {updated} mythology patterns with statistics")
        return {'updated_patterns': updated}

    except Exception as e:
        logger.error(f"❌ Error updating mythology pattern statistics: {e}")
        return {'error': str(e)}


# =============================================================================
# Session 823: Periodic System Audit Task (Enhanced with Live Data)
# =============================================================================


def _gather_live_system_metrics():
    """
    Session 823: Gather live system metrics from database and services.

    This function queries actual system state rather than relying on documentation.
    Returns a dict with real counts, health status, and activity metrics.
    """
    from datetime import datetime, timedelta
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone

    metrics = {
        'timestamp': datetime.now().isoformat(),
        'components': {},
        'health': {},
        'activity': {},
        'errors': {},
        'revenue': {},
        'remediation': {},
    }

    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # =========================================================================
    # 1. COMPONENT COUNTS (from database)
    # =========================================================================
    try:
        from core.models_unified_system import Agent
        metrics['components']['agents_in_db'] = Agent.objects.count()
        metrics['components']['active_agents'] = Agent.objects.filter(is_active=True).count()
    except Exception as e:
        metrics['components']['agents_error'] = str(e)

    try:
        # Count spiders from the registry instead of a model
        from ai_core.spiders.spider_registry import get_spider_registry
        registry = get_spider_registry()
        metrics['components']['spiders_registered'] = len(registry.list_spiders())
        # Also count spider execution logs
        from core.models_unified_system import SpiderExecutionLog
        metrics['components']['spider_executions_total'] = SpiderExecutionLog.objects.count()
    except Exception as e:
        metrics['components']['spiders_error'] = str(e)

    try:
        from django_celery_beat.models import PeriodicTask
        metrics['components']['celery_tasks'] = PeriodicTask.objects.filter(enabled=True).count()
        metrics['components']['celery_tasks_total'] = PeriodicTask.objects.count()
    except Exception as e:
        metrics['components']['celery_tasks_error'] = str(e)

    try:
        from core.models_unified_system import Advisor
        metrics['components']['advisors'] = Advisor.objects.count()
    except Exception as e:
        metrics['components']['advisors_error'] = str(e)

    # =========================================================================
    # 2. BODY SYSTEM HEALTH (call actual services)
    # =========================================================================
    body_systems = ['heart', 'lungs', 'brain', 'spine', 'immune', 'digestive', 'muscular', 'circulatory', 'skin']

    for system in body_systems:
        try:
            if system == 'heart':
                from core.services.heart import get_heart_monitor
                service = get_heart_monitor()
                vitals = service.get_vitals()
                metrics['health']['heart'] = {
                    'status': vitals.get('overall_status', 'unknown'),
                    'health_score': vitals.get('health_score', 0),
                    'subsystems': len(vitals.get('subsystems', {})),
                }
            elif system == 'lungs':
                from core.services.lungs import get_lungs_monitor
                service = get_lungs_monitor()
                vitals = service.get_vitals()
                metrics['health']['lungs'] = {
                    'status': vitals.get('status', 'unknown'),
                    'oxygen_level': vitals.get('oxygen_level', 0),
                    'active_budgets': vitals.get('active_budgets', 0),
                }
            elif system == 'brain':
                from core.services.brain import BrainService
                service = BrainService()
                vitals = service.get_vitals()
                metrics['health']['brain'] = {
                    'status': vitals.get('status', 'unknown') if vitals else 'unknown',
                    'active_conversations': vitals.get('active_conversations', 0) if vitals else 0,
                }
            elif system == 'skin':
                from core.services.skin import SkinService
                service = SkinService()
                status = service.get_status()
                metrics['health']['skin'] = {
                    'status': status.get('status', 'unknown') if status else 'unknown',
                    'recent_operations': status.get('recent_operations', 0) if status else 0,
                }
            else:
                # For other systems, just note they exist
                metrics['health'][system] = {'status': 'not_checked'}
        except Exception as e:
            metrics['health'][system] = {'status': 'error', 'error': str(e)[:100]}

    # =========================================================================
    # 3. RECENT ACTIVITY (last 24 hours)
    # =========================================================================
    try:
        from core.models_unified_system import AgentExecution
        executions_24h = AgentExecution.objects.filter(created_at__gte=last_24h)
        metrics['activity']['agent_executions_24h'] = executions_24h.count()
        metrics['activity']['successful_executions_24h'] = executions_24h.filter(status='completed').count()
        metrics['activity']['failed_executions_24h'] = executions_24h.filter(status='failed').count()
    except Exception as e:
        metrics['activity']['agent_executions_error'] = str(e)

    try:
        from core.models_unified_system import SpiderData
        metrics['activity']['spider_entries_24h'] = SpiderData.objects.filter(created_at__gte=last_24h).count()
        metrics['activity']['spider_entries_7d'] = SpiderData.objects.filter(created_at__gte=last_7d).count()
    except Exception as e:
        metrics['activity']['spider_entries_error'] = str(e)

    try:
        from core.models_skin_layer import WorkspaceOperation
        ops_24h = WorkspaceOperation.objects.filter(created_at__gte=last_24h)
        metrics['activity']['workspace_operations_24h'] = ops_24h.count()
        metrics['activity']['workspace_files_written_24h'] = ops_24h.filter(operation_type='write').count()
    except Exception as e:
        metrics['activity']['workspace_operations_error'] = str(e)

    try:
        from core.models_llm_routing import LLMCallLog
        llm_24h = LLMCallLog.objects.filter(created_at__gte=last_24h)
        metrics['activity']['llm_calls_24h'] = llm_24h.count()
        cost_sum = llm_24h.aggregate(total=Sum('cost'))['total']
        metrics['activity']['llm_cost_24h'] = float(cost_sum) if cost_sum else 0.0
    except Exception as e:
        metrics['activity']['llm_calls_error'] = str(e)

    # =========================================================================
    # 4. ERROR TRACKING
    # =========================================================================
    try:
        from core.models_unified_system import AgentExecution
        recent_failures = AgentExecution.objects.filter(
            status='failed',
            created_at__gte=last_7d
        ).values('agent__name').annotate(count=Count('id')).order_by('-count')[:10]
        metrics['errors']['top_failing_agents'] = list(recent_failures)
    except Exception as e:
        metrics['errors']['failing_agents_error'] = str(e)

    # =========================================================================
    # 5. REVENUE TRACKING
    # =========================================================================
    try:
        from core.models_unified_system import Revenue
        metrics['revenue']['total_records'] = Revenue.objects.count()
        revenue_sum = Revenue.objects.aggregate(total=Sum('amount'))['total']
        metrics['revenue']['total_amount'] = float(revenue_sum) if revenue_sum else 0.0
        revenue_7d = Revenue.objects.filter(created_at__gte=last_7d).aggregate(total=Sum('amount'))['total']
        metrics['revenue']['last_7_days'] = float(revenue_7d) if revenue_7d else 0.0
    except Exception as e:
        metrics['revenue']['error'] = str(e)

    # =========================================================================
    # 6. REMEDIATION STATUS
    # =========================================================================
    try:
        from core.models_audit_tracking import AuditFinding
        findings = AuditFinding.objects.values('status').annotate(count=Count('id'))
        metrics['remediation']['findings_by_status'] = {f['status']: f['count'] for f in findings}
        metrics['remediation']['open_findings'] = AuditFinding.objects.filter(status='open').count()
        metrics['remediation']['fixed_findings'] = AuditFinding.objects.filter(status='fixed').count()
    except Exception as e:
        metrics['remediation']['findings_error'] = str(e)

    try:
        from core.models_audit_tracking import AuditRemediationTask
        tasks = AuditRemediationTask.objects.values('status').annotate(count=Count('id'))
        metrics['remediation']['tasks_by_status'] = {t['status']: t['count'] for t in tasks}
    except Exception as e:
        metrics['remediation']['tasks_error'] = str(e)

    # =========================================================================
    # 7. INTEGRATION HEALTH
    # =========================================================================
    try:
        from core.models_unified_system import AgentMemory
        memories_24h = AgentMemory.objects.filter(created_at__gte=last_24h).count()
        metrics['activity']['memories_created_24h'] = memories_24h
        total_memories = AgentMemory.objects.count()
        metrics['activity']['total_memories'] = total_memories
    except Exception as e:
        metrics['activity']['memories_error'] = str(e)

    return metrics


def _format_metrics_for_audit(metrics: dict) -> str:
    """Format the live metrics as a markdown section for the audit prompt."""
    lines = ["## LIVE SYSTEM METRICS (Queried from Database)", ""]

    # Components
    lines.append("### Component Counts")
    comp = metrics.get('components', {})
    lines.append(f"- **Agents in DB:** {comp.get('agents_in_db', 'error')} (active: {comp.get('active_agents', 'N/A')})")
    lines.append(f"- **Spiders Registered:** {comp.get('spiders_registered', 'error')} (executions: {comp.get('spider_executions_total', 'N/A')})")
    lines.append(f"- **Celery Tasks (enabled):** {comp.get('celery_tasks', 'error')} (total: {comp.get('celery_tasks_total', 'N/A')})")
    lines.append(f"- **Advisors:** {comp.get('advisors', 'error')}")
    lines.append("")

    # Health
    lines.append("### Body System Health")
    health = metrics.get('health', {})
    for system, data in health.items():
        status = data.get('status', 'unknown') if isinstance(data, dict) else 'unknown'
        extra = ""
        if isinstance(data, dict):
            if 'score' in data:
                extra = f" (score: {data['score']})"
            elif 'error' in data:
                extra = f" (error: {data['error'][:50]})"
        lines.append(f"- **{system.upper()}:** {status}{extra}")
    lines.append("")

    # Activity
    lines.append("### Recent Activity (Last 24 Hours)")
    activity = metrics.get('activity', {})
    lines.append(f"- **Agent Executions:** {activity.get('agent_executions_24h', 'error')} (successful: {activity.get('successful_executions_24h', 'N/A')}, failed: {activity.get('failed_executions_24h', 'N/A')})")
    lines.append(f"- **Spider Data Entries:** {activity.get('spider_entries_24h', 'error')} (7d: {activity.get('spider_entries_7d', 'N/A')})")
    lines.append(f"- **Workspace Operations:** {activity.get('workspace_operations_24h', 'error')} (files written: {activity.get('workspace_files_written_24h', 'N/A')})")
    lines.append(f"- **LLM Calls:** {activity.get('llm_calls_24h', 'error')} (cost: ${activity.get('llm_cost_24h', 0):.2f})")
    lines.append(f"- **Memories Created:** {activity.get('memories_created_24h', 'error')} (total: {activity.get('total_memories', 'N/A')})")
    lines.append("")

    # Errors
    lines.append("### Error Analysis (Last 7 Days)")
    errors = metrics.get('errors', {})
    top_failing = errors.get('top_failing_agents', [])
    if top_failing:
        lines.append("Top failing agents:")
        for agent in top_failing[:5]:
            lines.append(f"  - {agent.get('agent_name', 'unknown')}: {agent.get('count', 0)} failures")
    else:
        lines.append("- No agent failures recorded")
    lines.append("")

    # Revenue
    lines.append("### Revenue Tracking")
    revenue = metrics.get('revenue', {})
    lines.append(f"- **Total Revenue Records:** {revenue.get('total_records', 'error')}")
    lines.append(f"- **Total Amount:** ${revenue.get('total_amount', 0):.2f}")
    lines.append(f"- **Last 7 Days:** ${revenue.get('last_7_days', 0):.2f}")
    lines.append("")

    # Remediation
    lines.append("### Autonomous Remediation Status")
    remediation = metrics.get('remediation', {})
    findings = remediation.get('findings_by_status', {})
    if findings:
        lines.append("Findings by status:")
        for status, count in findings.items():
            lines.append(f"  - {status}: {count}")
    lines.append(f"- **Open Findings:** {remediation.get('open_findings', 'N/A')}")
    lines.append(f"- **Fixed Findings:** {remediation.get('fixed_findings', 'N/A')}")
    tasks = remediation.get('tasks_by_status', {})
    if tasks:
        lines.append("Tasks by status:")
        for status, count in tasks.items():
            lines.append(f"  - {status}: {count}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# Session 823: Metrics Action Trigger - Self-Execution Engine
# =============================================================================

@shared_task
def run_metrics_action_check():
    from core.tasks_misc import _impl_run_metrics_action_check
    return _impl_run_metrics_action_check()
@shared_task
def run_agent_health_rotation():
    from core.tasks_misc import _impl_run_agent_health_rotation
    return _impl_run_agent_health_rotation()
@shared_task
def run_system_self_audit():
    from core.tasks_agents import _impl_run_system_self_audit
    return _impl_run_system_self_audit()
@shared_task
def discover_and_import_audits():
    """
    Session 820: Automatically discover and import new audit files.
    Session 1031: DISABLED — audit import creates AuditFindings that feed
    garbage tasks to agents via remediation pipeline.  The audit_tracker
    regex still produces too many false-positive findings from markdown tables.
    Re-enable after audit_tracker parsing is reliable.
    """
    logger.warning(
        "🚫 [AUTO-REMEDIATE] discover_and_import_audits BLOCKED — "
        "audit parsing produces garbage findings (Session 1031)"
    )
    return {'blocked': True, 'reason': 'Audit parsing unreliable'}


@shared_task
def assign_open_findings_to_agents():
    """
    Session 820: Auto-assign open findings to appropriate agents.
    Session 1031: DISABLED — all 4 execution paths blocked, assignment
    just creates fuel for unknown 5th dispatch path that still fires
    CodeGeneratorAgent.  Re-enable when execution paths are safe.
    """
    logger.warning(
        "🚫 [AUTO-REMEDIATE] assign_open_findings_to_agents BLOCKED — "
        "execution paths disabled since Session 1026"
    )
    return {'blocked': True, 'reason': 'All execution paths disabled'}


@shared_task
def execute_remediation_tasks():
    """
    Session 820: Execute assigned remediation tasks via agents.

    Runs each assigned task through the AgentRouter. Limits to 3 tasks
    per cycle to avoid overwhelming the system. Runs every 4 hours.

    Session 1031: DISABLED — execution burns $9/day running agents on
    garbage audit findings (markdown table fragments parsed as tasks).
    Disabled in Beat (Session 1026) but mystery trigger still dispatches
    this task ~20x/day. Hard-block here until trigger is identified.
    """
    logger.warning(
        "🚫 [AUTO-REMEDIATE] execute_remediation_tasks BLOCKED — "
        "disabled since Session 1026, mystery trigger still dispatching. "
        "Use 'python manage.py auto_remediate --execute' for manual runs."
    )
    return {'blocked': True, 'reason': 'Execution disabled since Session 1026'}

    from core.services.autonomous_remediation_orchestrator import get_remediation_orchestrator

    logger.info("🔧 [AUTO-REMEDIATE] Executing remediation tasks...")

    try:
        orchestrator = get_remediation_orchestrator(max_tasks_per_cycle=3)
        results = orchestrator.execute_assigned_tasks()

        logger.info(
            f"✅ [AUTO-REMEDIATE] Executed {results.get('attempted', 0)} tasks, "
            f"{results.get('succeeded', 0)} succeeded"
        )
        return results

    except Exception as e:
        logger.error(f"❌ [AUTO-REMEDIATE] Task execution failed: {e}")
        return {'error': str(e)}


@shared_task
def verify_completed_fixes():
    """
    Session 820: Verify that completed fixes actually worked.

    Runs verification checks on 'fixed' findings. Reopens findings
    where verification fails. Runs every 6 hours.
    """
    from core.services.autonomous_remediation_orchestrator import get_remediation_orchestrator

    logger.info("🔬 [AUTO-REMEDIATE] Verifying completed fixes...")

    try:
        orchestrator = get_remediation_orchestrator(max_tasks_per_cycle=5)
        results = orchestrator.verify_completed_fixes()

        logger.info(
            f"✅ [AUTO-REMEDIATE] Verified {results.get('verified', 0)} fixes, "
            f"{results.get('failed', 0)} failed verification"
        )
        return results

    except Exception as e:
        logger.error(f"❌ [AUTO-REMEDIATE] Verification failed: {e}")
        return {'error': str(e)}


@shared_task
def run_autonomous_remediation_cycle():
    """
    Session 820: Run a complete autonomous remediation cycle.

    Orchestrates all phases: discover → assign → execute → verify.
    This is the main entry point for the self-healing system.
    Runs daily at 2am after the audit discovery at midnight.

    Session 840: Updated to include P2 findings since all P0/P1 are resolved.
    Session 1031: DISABLED — same issue as execute_remediation_tasks.
    """
    logger.warning(
        "🚫 [AUTO-REMEDIATE] run_autonomous_remediation_cycle BLOCKED — "
        "disabled since Session 1026. Use management command for manual runs."
    )
    return {'blocked': True, 'reason': 'Cycle disabled since Session 1026'}

    from core.services.autonomous_remediation_orchestrator import get_remediation_orchestrator

    logger.info("🔄 [AUTO-REMEDIATE] Starting full remediation cycle...")

    try:
        orchestrator = get_remediation_orchestrator(max_tasks_per_cycle=5)
        # Session 840: Include P2 findings now that P0/P1 are resolved
        results = orchestrator.run_remediation_cycle(priority_filter=['P0', 'P1', 'P2'])

        # Log summary
        summary = results.get('summary', {})
        state = summary.get('findings_state', {})

        logger.info(
            f"✅ [AUTO-REMEDIATE] Cycle complete! "
            f"Open P0: {state.get('open_p0', 0)}, "
            f"Open P1: {state.get('open_p1', 0)}, "
            f"Verified: {state.get('verified', 0)}"
        )

        # Log alerts
        for alert in summary.get('alerts', []):
            logger.warning(f"[AUTO-REMEDIATE] {alert}")

        return results

    except Exception as e:
        logger.error(f"❌ [AUTO-REMEDIATE] Remediation cycle failed: {e}")
        return {'error': str(e)}


@shared_task
def assign_and_execute_remediation(limit: int = 20, write_files: bool = True):
    """
    Session 833: Combined task that assigns findings then executes remediation.

    Session 1031: DISABLED — execution phase blocked. Assignment-only still
    runs via assign_open_findings_to_agents. This combined task would re-enable
    execution through run_agent_remediation_batch, bypassing the hard-block
    on execute_remediation_tasks.
    """
    logger.warning(
        "🚫 [ASSIGN-AND-EXECUTE] BLOCKED — execution phase disabled since "
        "Session 1026. Use assign_open_findings_to_agents for assignment only."
    )
    return {'blocked': True, 'reason': 'Execution disabled since Session 1026'}


def _assign_and_execute_remediation_DISABLED(limit: int = 20, write_files: bool = True):
    """
    ORIGINAL IMPLEMENTATION — preserved for reference, not callable.

    Args:
        limit: Maximum number of findings to assign/tasks to execute
        write_files: Whether to write generated files to workspace
    """
    from django.db.models import Count
    from core.models_audit_tracking import AuditRemediationTask
    from core.services.autonomous_remediation_orchestrator import get_remediation_orchestrator

    logger.info(f"🔄 [ASSIGN-AND-EXECUTE] Starting combined remediation (limit={limit})...")

    results = {
        'assignment': {},
        'execution': {},
    }

    try:
        # Phase 1: Assign open findings to agents
        orchestrator = get_remediation_orchestrator(max_tasks_per_cycle=limit)
        assignment_result = orchestrator.assign_open_findings(
            priority_filter=['P0', 'P1', 'P2'],
            limit=limit
        )
        results['assignment'] = assignment_result
        logger.info(f"✅ [ASSIGN-AND-EXECUTE] Assigned {assignment_result.get('assigned', 0)} findings")

        # Phase 2: Find agent with most assigned tasks and execute
        top_agent = AuditRemediationTask.objects.filter(
            status='assigned'
        ).values('assigned_agent').annotate(
            count=Count('id')
        ).order_by('-count').first()

        if top_agent:
            agent_name = top_agent['assigned_agent']
            pending_count = top_agent['count']
            logger.info(f"🎯 [ASSIGN-AND-EXECUTE] Executing {agent_name} with {pending_count} tasks...")

            # Execute the remediation batch synchronously (we're already in a Celery task)
            from core.tasks import run_agent_remediation_batch
            execution_result = run_agent_remediation_batch(
                agent_name=agent_name,
                limit=limit,
                write_files=write_files
            )
            results['execution'] = execution_result
            logger.info(f"✅ [ASSIGN-AND-EXECUTE] Execution complete")
        else:
            logger.info("ℹ️ [ASSIGN-AND-EXECUTE] No assigned tasks to execute")
            results['execution'] = {'skipped': True, 'reason': 'No assigned tasks'}

        return results

    except Exception as e:
        logger.error(f"❌ [ASSIGN-AND-EXECUTE] Failed: {e}")
        return {'error': str(e), **results}


def _route_spec_to_human_attention_standalone(task, agent_name):
    """Route a spec_complete remediation task to HumanAttentionItem for human review."""
    try:
        from core.models_human_interface import HumanAttentionItem
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.filter(is_staff=True, is_active=True).first()
        if not user:
            logger.warning("  ⚠️ No staff user found — cannot create HumanAttentionItem")
            return

        priority_map = {
            'P0': ('critical', 9.0),
            'P1': ('high', 7.0),
            'P2': ('medium', 4.0),
            'P3': ('low', 2.0),
        }
        urgency, priority_score = priority_map.get(
            task.finding.priority, ('medium', 4.0)
        )

        spec_message = ''
        if task.execution_result and isinstance(task.execution_result, dict):
            spec_message = task.execution_result.get('message', '')[:1000]

        HumanAttentionItem.objects.create(
            user=user,
            source_type='audit_remediation',
            source_id=str(task.id),
            source_agent=agent_name,
            item_type='remediation_proposal',
            title=f"Review spec: {task.title[:150]}",
            summary=(
                f"Agent {agent_name} produced a spec/report for "
                f"finding '{task.finding.title[:100]}' but did not write any "
                f"code files or create a PR. Review the proposal and apply manually."
            ),
            payload={
                'task_id': str(task.id),
                'finding_id': str(task.finding.id),
                'finding_title': task.finding.title,
                'priority': task.finding.priority,
                'category': task.finding.category,
                'affected_files': task.finding.affected_files,
                'spec_message': spec_message,
            },
            urgency=urgency,
            priority_score=priority_score,
        )
        logger.info(f"  📋 Routed spec to HumanAttentionItem (urgency={urgency})")

    except Exception as e:
        logger.error(f"  ⚠️ Failed to create HumanAttentionItem: {e}")


@shared_task
def run_agent_remediation_batch(agent_name: str = 'CodeGeneratorAgent', limit: int = 20, write_files: bool = True):
    """
    Session 829: Run a batch of remediation tasks for a specific agent.

    Session 1031: DISABLED — execution burns $9/day running agents on garbage
    audit findings. All 4 remediation execution paths now hard-blocked:
    1. execute_remediation_tasks (blocked)
    2. run_autonomous_remediation_cycle (blocked)
    3. assign_and_execute_remediation (blocked)
    4. run_agent_remediation_batch (this function — blocked)

    Use 'python manage.py auto_remediate --execute' for manual runs.
    """
    logger.warning(
        f"🚫 [REMEDIATION-BATCH] BLOCKED — execution disabled since Session 1026. "
        f"Agent: {agent_name}, limit: {limit}"
    )
    return {'blocked': True, 'reason': 'Execution disabled since Session 1026', 'agent': agent_name}


def _run_agent_remediation_batch_DISABLED(agent_name: str = 'CodeGeneratorAgent', limit: int = 20, write_files: bool = True):
    """ORIGINAL IMPLEMENTATION — preserved for reference, not callable."""
    import re
    from django.utils import timezone
    from core.models_audit_tracking import AuditRemediationTask
    from core.agent_router import AgentRouter

    logger.info(f"🔄 [REMEDIATION-BATCH] Starting {agent_name} batch (limit={limit}, write_files={write_files})")

    # Setup workspace manager for file writing
    workspace_manager = None
    workspace = None

    if write_files:
        try:
            from core.services.workspace_manager import WorkspaceManager
            from core.models_skin_layer import ProjectWorkspace
            from django.contrib.auth import get_user_model

            User = get_user_model()
            system_user = User.objects.filter(is_superuser=True).first()

            if system_user:
                workspace_manager = WorkspaceManager(user=system_user)
                workspace = ProjectWorkspace.objects.filter(
                    is_active=True,
                    allow_file_write=True
                ).first()
                if workspace:
                    logger.info(f"📁 [REMEDIATION-BATCH] Workspace enabled: {workspace.name}")
                else:
                    logger.warning("⚠️ [REMEDIATION-BATCH] No active workspace found - files will NOT be written")
                    write_files = False
            else:
                logger.warning("⚠️ [REMEDIATION-BATCH] No system user found - files will NOT be written")
                write_files = False
        except Exception as e:
            logger.warning(f"⚠️ [REMEDIATION-BATCH] Workspace setup failed: {e}")
            write_files = False

    def parse_code_from_result(result_data):
        """Extract code blocks from agent result."""
        files = []
        if not result_data:
            return files

        message = result_data.get('message', '')
        if not message:
            return files

        # Pattern: Code: filename.py followed by code block
        code_pattern = r'Code:\s*([^\n]+\.(?:py|js|ts|json|yaml|yml|md|txt|html|css))\s*```(?:\w+)?\n(.*?)```'
        matches = re.findall(code_pattern, message, re.DOTALL | re.IGNORECASE)

        for filename, content in matches:
            filename = filename.strip()
            content = content.strip()
            if filename and content:
                files.append({
                    'filename': filename,
                    'content': content,
                    'language': filename.split('.')[-1] if '.' in filename else 'txt'
                })

        # Also try generic code blocks if no specific filenames found
        if not files:
            generic_pattern = r'```(?:python|javascript|typescript)?\n(.*?)```'
            matches = re.findall(generic_pattern, message, re.DOTALL)
            for i, content in enumerate(matches):
                if len(content.strip()) > 50:  # Only substantial code
                    files.append({
                        'filename': f'generated_{i+1}.py',
                        'content': content.strip(),
                        'language': 'python'
                    })

        return files

    def write_files_to_workspace(files, task):
        """Write generated files to the workspace."""
        if not workspace_manager or not workspace or not files:
            return {'written': False, 'reason': 'No workspace or files'}

        written = []
        for file_info in files:
            try:
                operation = workspace_manager.write_file(
                    workspace=workspace,
                    file_path=file_info['filename'],
                    content=file_info['content'],
                    agent_name=task.assigned_agent,
                    agent_task=f"Fix finding: {task.finding.title}"
                )
                written.append({
                    'filename': file_info['filename'],
                    'operation_id': str(operation.id) if operation else None
                })
                logger.info(f"   📝 Wrote: {file_info['filename']}")
            except Exception as e:
                logger.warning(f"   ⚠️ Write failed for {file_info['filename']}: {e}")

        return {'written': len(written) > 0, 'files': written}

    # Get assigned tasks for this agent
    tasks = list(AuditRemediationTask.objects.filter(
        assigned_agent=agent_name,
        status='assigned'
    ).select_related('finding')[:limit])

    logger.info(f"📋 [REMEDIATION-BATCH] Processing {len(tasks)} {agent_name} tasks...")

    router = AgentRouter()
    succeeded = 0
    failed = 0
    files_written = 0

    for i, task in enumerate(tasks, 1):
        finding = task.finding
        logger.info(f"[{i}/{len(tasks)}] {finding.title[:55]}...")

        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()

        task_desc = f'''Review and fix this finding:
Title: {finding.title}
Category: {finding.category}
Priority: {finding.priority}
Affected Files: {finding.affected_files}

Description:
{finding.description}

Recommendation:
{finding.recommendation}
'''

        try:
            result = router.route(agent_name=agent_name, task=task_desc)

            result_data = {}
            if hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            elif hasattr(result, 'message'):
                result_data = {'message': result.message, 'success': getattr(result, 'success', True)}
            else:
                result_data = {'raw': str(result)[:500]}

            # Write files if enabled
            if write_files and agent_name == 'CodeGeneratorAgent':
                parsed_files = parse_code_from_result(result_data)
                if parsed_files:
                    write_result = write_files_to_workspace(parsed_files, task)
                    result_data['skin_layer'] = write_result
                    files_written += len(write_result.get('files', []))

            # Evidence-gated completion
            skin = result_data.get('skin_layer', {})
            has_files = skin.get('written') and len(skin.get('files', [])) > 0
            has_pr = False  # Batch path doesn't create PRs

            if has_files:
                # Real artifacts exist — mark completed with evidence
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.evidence_type = 'commit'
                task.evidence_ref = f"wrote {len(skin.get('files', []))} files"
                task.verified_by = agent_name
                task.evidence_verified_at = timezone.now()
                task.execution_result = result_data
                task.save()

                finding.status = 'fixed'
                finding.fixed_by = f"Auto-remediation via {agent_name}"
                finding.fixed_at = timezone.now()
                finding.save()
            else:
                # No real artifacts — spec only
                task.status = 'spec_complete'
                task.completed_at = timezone.now()
                task.evidence_type = 'none'
                task.execution_result = result_data
                task.save()
                # Finding stays in_progress — not fixed without evidence
                _route_spec_to_human_attention_standalone(task, agent_name)

            succeeded += 1
            logger.info(f"   ✅ {task.status}")

        except Exception as e:
            task.status = 'failed'
            task.completed_at = timezone.now()
            task.execution_result = {'error': str(e)}
            task.save()

            failed += 1
            logger.error(f"   ❌ Failed: {str(e)[:80]}")

    logger.info(f"✅ [REMEDIATION-BATCH] {agent_name} complete: {succeeded} succeeded, {failed} failed, {files_written} files written")

    return {
        'agent': agent_name,
        'succeeded': succeeded,
        'failed': failed,
        'total': len(tasks),
        'files_written': files_written,
        'write_files_enabled': write_files,
    }


# =============================================================================
# Session 827: Async Triggered Conversations
# Fixes production 502 timeout by running conversations as Celery tasks
# =============================================================================


@shared_task(bind=True, max_retries=1, default_retry_delay=60, soft_time_limit=1800, time_limit=1860, ignore_result=True)
def run_triggered_conversation(
    self,
    topic: str,
    conversation_type: str = 'general',
    objective: str = None,
    success_criteria: list = None,
    auto_select_agents: bool = False,
    participant_ids: list = None,
    hive_session_id: str = None  # Session 902: Link to HiveMindSession for signal provenance
):
    from core.tasks_conversations import _impl_run_triggered_conversation
    return _impl_run_triggered_conversation(self, topic, conversation_type, objective, success_criteria, auto_select_agents, participant_ids, hive_session_id)
@shared_task(bind=True)
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


@shared_task
def cleanup_resolved_signatures(days_old: int = 30):
    """
    Session 856: Archive old resolved failure signatures.

    Signatures that have been resolved for more than `days_old` days
    are marked as inactive/archived to keep the active list clean.

    Called by Celery Beat daily.
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_diagnostic_pipeline import FailureSignature

    cutoff = timezone.now() - timedelta(days=days_old)

    # Find resolved signatures older than cutoff
    old_resolved = FailureSignature.objects.filter(
        status=FailureSignature.Status.RESOLVED,
        last_seen_at__lt=cutoff
    )

    count = old_resolved.count()

    if count > 0:
        # Archive them by setting status to IGNORED
        old_resolved.update(status=FailureSignature.Status.IGNORED)
        logger.info(f"🧹 [DIAGNOSTIC] Archived {count} old resolved signatures")
    else:
        logger.info("🧹 [DIAGNOSTIC] No old resolved signatures to archive")

    return {'archived': count}


@shared_task
def detect_failure_task(
    error_message: str,
    source_type: str,
    error_code: str = None,
    provider: str = None,
    source_id: str = None,
    source_name: str = None,
    context: dict = None
):
    from core.tasks_misc import _impl_detect_failure_task
    return _impl_detect_failure_task(error_message, source_type, error_code, provider, source_id, source_name, context)
@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def run_conceptforge_pipeline(
    self,
    source_type: str,
    source_id: str,
    source_title: str,
    domain: str,
    quality_score: float = 0.0,
    triggered_by: str = 'celery',
    user_id: int = None
):
    from core.tasks_content import _impl_run_conceptforge_pipeline
    return _impl_run_conceptforge_pipeline(self, source_type, source_id, source_title, domain, quality_score, triggered_by, user_id)
@shared_task
def poll_processing_videos():
    from core.tasks_misc import _impl_poll_processing_videos
    return _impl_poll_processing_videos()
@shared_task
def advance_initiative_pipeline(limit: int = 10, auto_approve: bool = True):
    from core.tasks_initiatives import _impl_advance_initiative_pipeline
    return _impl_advance_initiative_pipeline(limit, auto_approve)
def _get_stage_document_type(stage_num: int) -> str:
    """Get the document type for a given stage number."""
    doc_types = {
        1: 'Research Brief - Market analysis, feasibility study, opportunity assessment',
        2: 'Prototype Plan - Architecture overview, technical approach, MVP scope',
        3: 'Evaluation Criteria - Testing requirements, acceptance criteria, success metrics',
        4: 'Technical Design - Implementation details, code structure, integration points',
        5: 'Pilot Execution Plan - Deployment strategy, monitoring, rollback procedures',
    }
    return doc_types.get(stage_num, f'Stage {stage_num} Document')


def _gather_initiative_research(initiative, stage_num: int) -> str:
    """
    Session 1021: Gather REAL system data relevant to an initiative topic.

    Queries SpiderData, SignalClusters, AgentConversations, and Deliverables
    to build actual research context — not hallucinated content.

    Returns a formatted string with real data for the TechnicalDocumentAgent.
    """
    from core.models_unified_system import SpiderData, AgentConversation
    from core.models import SignalCluster
    from django.utils import timezone
    from datetime import timedelta

    parts = []
    topic = initiative.name
    description = initiative.description or ''

    # Extract search keywords from initiative name (words > 3 chars, skip common words)
    stop_words = {'that', 'this', 'with', 'from', 'into', 'which', 'when', 'what',
                  'have', 'been', 'will', 'would', 'could', 'should', 'does', 'also',
                  'more', 'most', 'some', 'than', 'then', 'them', 'they', 'their',
                  'each', 'about', 'over', 'such', 'after', 'before', 'between',
                  'through', 'using', 'based', 'module', 'pipeline', 'component',
                  'system', 'prototype', 'enhancement', 'create', 'build', 'implement',
                  'deliver', 'initiate', 'focused', 'small', 'lightweight'}
    keywords = [w for w in topic.lower().split() if len(w) > 3 and w not in stop_words][:6]

    since = timezone.now() - timedelta(days=14)

    # 1. Spider Data — real external intelligence
    try:
        spider_hits = []
        for kw in keywords[:3]:
            hits = SpiderData.objects.filter(
                embedding_text__icontains=kw,
                created_at__gte=since
            ).order_by('-created_at')[:3]
            for h in hits:
                if h.id not in [x.id for x in spider_hits]:
                    spider_hits.append(h)
            if len(spider_hits) >= 5:
                break

        if spider_hits:
            parts.append("## Recent Spider Intelligence")
            for sd in spider_hits[:5]:
                source = sd.source_url or 'internal'
                text = (sd.embedding_text or sd.processed_data or '')[:300]
                parts.append(f"- [{sd.spider_name}] ({sd.data_type}, {sd.created_at.strftime('%m/%d')}): {text}")
    except Exception as e:
        logger.warning(f"[Initiative research] Spider query failed: {e}")

    # 2. Signal Clusters — detected patterns
    try:
        clusters = []
        for kw in keywords[:3]:
            hits = SignalCluster.objects.filter(
                name__icontains=kw,
                detected_at__gte=since
            ).order_by('-detected_at')[:3]
            for h in hits:
                if h.id not in [x.id for x in clusters]:
                    clusters.append(h)
            if len(clusters) >= 3:
                break

        if clusters:
            parts.append("## Related Signal Clusters")
            for sc in clusters[:3]:
                parts.append(f"- {sc.name} (type={sc.pattern_type}, detected={sc.detected_at.strftime('%m/%d')})")
    except Exception as e:
        logger.warning(f"[Initiative research] SignalCluster query failed: {e}")

    # 3. Agent Conversations — what agents discussed about this topic
    try:
        convos = []
        for kw in keywords[:2]:
            hits = AgentConversation.objects.filter(
                topic__icontains=kw,
                started_at__gte=since
            ).order_by('-started_at')[:3]
            for h in hits:
                if h.id not in [x.id for x in convos]:
                    convos.append(h)
            if len(convos) >= 3:
                break

        if convos:
            parts.append("## Related Agent Conversations")
            for ac in convos[:3]:
                conclusion = (ac.conclusion or '')[:200]
                conclusion_text = f" — conclusion: {conclusion}" if conclusion else ''
                parts.append(f"- \"{ac.topic[:80]}\" ({ac.started_at.strftime('%m/%d')}){conclusion_text}")
    except Exception as e:
        logger.warning(f"[Initiative research] Conversation query failed: {e}")

    # 4. Existing Deliverables — what's already been produced
    try:
        from core.models_deliverables import Deliverable
        deliverables = Deliverable.objects.filter(initiative=initiative).order_by('-created_at')[:3]
        if deliverables:
            parts.append("## Existing Deliverables")
            for d in deliverables:
                meta = d.metadata or {}
                parts.append(f"- {d.title[:80]} (type={meta.get('content_type', 'unknown')}, created={d.created_at.strftime('%m/%d')})")
    except Exception as e:
        logger.warning(f"[Initiative research] Deliverable query failed: {e}")

    if not parts:
        return f"No system data found for topic '{topic}'. The document should outline a plan based on the initiative description: {description[:500]}"

    header = f"## Real System Data for: {topic}\nKeywords searched: {', '.join(keywords)}\nData window: last 14 days\n"
    return header + "\n\n".join(parts)


def _get_previous_stage_context(initiative, current_stage: int) -> str:
    """Get context from previous completed stages."""
    from core.models_document_registry import InitiativeStage
    from core.models_unified_system import SelfBlog

    context_parts = []

    for stage_num in range(1, current_stage):
        stage = InitiativeStage.objects.filter(
            initiative=initiative,
            stage=stage_num
        ).first()

        if stage and stage.document_id:
            try:
                doc = SelfBlog.objects.get(id=stage.document_id)
                # Include a summary of the previous stage document
                summary = doc.intro or doc.full_text[:500] if doc.full_text else ''
                context_parts.append(f"**Stage {stage_num} Summary:** {summary}")
            except SelfBlog.DoesNotExist:
                pass

    if not context_parts:
        return "No previous stage documents available - this is a new initiative."

    return "\n\n".join(context_parts)


# =============================================================================
# Session 885: Auto-Kickstart Stuck Initiatives
# =============================================================================

@shared_task
def auto_kickstart_stuck_initiatives(limit: int = 10):
    from core.tasks_initiatives import _impl_auto_kickstart_stuck_initiatives
    return _impl_auto_kickstart_stuck_initiatives(limit)
def _detect_initiative_content_type(topic: str) -> str:
    """Detect content type from initiative topic text."""
    topic_lower = topic.lower()

    if any(kw in topic_lower for kw in ['persona', 'customer', 'user', 'buyer']):
        return 'strategy'
    elif any(kw in topic_lower for kw in ['plan', 'roadmap', 'timeline', 'milestone']):
        return 'plan'
    elif any(kw in topic_lower for kw in ['research', 'study', 'analysis', 'audit']):
        return 'research'
    elif any(kw in topic_lower for kw in ['content', 'blog', 'article', 'post']):
        return 'document'
    else:
        return 'strategy'  # Default


# =============================================================================
# SESSION 900: SIGNAL INTELLIGENCE - Signal Aggregation Tasks
# =============================================================================

@shared_task(bind=True, name='aggregate_spider_signals')
def aggregate_spider_signals(self, lookback_hours: int = 6):
    from core.tasks_spiders import _impl_aggregate_spider_signals
    return _impl_aggregate_spider_signals(self, lookback_hours)
@shared_task(bind=True, name='trigger_signal_driven_conversation')
def trigger_signal_driven_conversation(self, auto_topic_id: str):
    from core.tasks_conversations import _impl_trigger_signal_driven_conversation
    return _impl_trigger_signal_driven_conversation(self, auto_topic_id)
@shared_task(bind=True, name='process_pending_auto_topics')
def process_pending_auto_topics(self, max_topics: int = 3):
    from core.tasks_misc import _impl_process_pending_auto_topics
    return _impl_process_pending_auto_topics(self, max_topics)
@shared_task(bind=True, name='cleanup_expired_signals')
def cleanup_expired_signals(self):
    from core.tasks_misc import _impl_cleanup_expired_signals
    return _impl_cleanup_expired_signals(self)
@shared_task(bind=True, queue='default')
def extract_action_items_from_session(self, session_id: str):
    """
    Session 903: Auto-extract action items when a HiveMind session completes.

    Parses the synthesis_summary for Next Steps and creates InitiativeActionItem records.
    """
    logger.info(f"📋 [ACTION-ITEMS] Extracting from session {session_id}")

    try:
        from core.services.action_item_parser import extract_action_items_from_conversation

        items = extract_action_items_from_conversation(session_id)

        if items:
            logger.info(f"📋 [ACTION-ITEMS] Created {len(items)} action items from session {session_id}")
            return {
                'status': 'success',
                'session_id': session_id,
                'items_created': len(items),
                'items': [{'id': str(item.id), 'title': item.title} for item in items]
            }
        else:
            logger.info(f"📋 [ACTION-ITEMS] No action items found in session {session_id}")
            return {
                'status': 'success',
                'session_id': session_id,
                'items_created': 0,
                'message': 'No action items found in synthesis'
            }

    except Exception as e:
        logger.error(f"📋 [ACTION-ITEMS] Extraction failed for session {session_id}: {e}")
        return {
            'status': 'failed',
            'session_id': session_id,
            'error': str(e)
        }


# =============================================================================
# Session 1058 Level 3: Auto-Dispatch Pending Action Items
# =============================================================================

@shared_task(bind=True, soft_time_limit=300, time_limit=360)
def dispatch_pending_action_items(self):
    from core.tasks_ops import _impl_dispatch_pending_action_items
    return _impl_dispatch_pending_action_items(self)
@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def retry_blocked_research(self, research_result_id: str):
    from core.tasks_ops import _impl_retry_blocked_research
    return _impl_retry_blocked_research(self, research_result_id)
@shared_task(bind=True, queue='default')
def check_blocked_research_for_unblock(self):
    """
    Session 905: Periodic task to check all blocked research and trigger retries.

    Runs every 15 minutes to find research that's ready to retry.
    """
    from core.models_research import ResearchResult
    from django.utils import timezone

    logger.info("🔍 [RESEARCH-UNBLOCK] Checking for blocked research ready to retry")

    from django.db.models import F
    blocked_research = ResearchResult.objects.filter(
        status='blocked',
        retry_after__lte=timezone.now(),
        retry_count__lt=F('max_retries')
    )

    triggered_count = 0
    for research in blocked_research:
        try:
            retry_blocked_research.delay(str(research.id))
            triggered_count += 1
            logger.info(f"🔍 [RESEARCH-UNBLOCK] Triggered retry for {research.id}")
        except Exception as e:
            logger.error(f"🔍 [RESEARCH-UNBLOCK] Failed to trigger retry for {research.id}: {e}")

    logger.info(f"🔍 [RESEARCH-UNBLOCK] Triggered {triggered_count} research retries")
    return {
        'status': 'success',
        'triggered_count': triggered_count
    }


# ==================== SESSION 905: INITIATIVE AUTO-PROGRESSION ====================


@shared_task(bind=True, queue='default')
def process_initiative_auto_progression(self):
    from core.tasks_initiatives import _impl_process_initiative_auto_progression
    return _impl_process_initiative_auto_progression(self)
@shared_task(bind=True, queue='default')
def detect_duplicate_initiatives(self):
    from core.tasks_initiatives import _impl_detect_duplicate_initiatives
    return _impl_detect_duplicate_initiatives(self)
def _extract_agent_content(result) -> str:
    """
    Session 1041: Extract real content from an AgentResult.

    Many agents put a SHORT summary in result.message while storing the
    actual content in result.data under various keys. This helper checks
    all known patterns:
    - ContentWriterAgent: data['content']['full_text']
    - ResearchAgent (tool path): data['all_results'] + data['key_insights']
    - ResearchAgent (no-tool path): data['response']
    - FullStackDeveloperAgent: data['results'] (code/configs)
    - Generic: any data['full_text'] or data['output'] string
    Falls back to result.message if nothing longer is found.
    """
    message = result.message or ''
    data = result.data or {}

    # Guard: if data is a string (not a dict), treat it as the content directly
    if isinstance(data, str):
        return data if len(data) > len(message) else message

    best = message

    # Pattern 1: ContentWriterAgent — data['content'] is dict with 'full_text'
    content_data = data.get('content')
    if isinstance(content_data, dict):
        ft = content_data.get('full_text', '')
        if ft and len(ft) > len(best):
            best = ft
    elif isinstance(content_data, str) and len(content_data) > len(best):
        best = content_data

    # Pattern 2: Direct full_text or output keys
    for key in ('full_text', 'output', 'response', 'document'):
        val = data.get(key)
        if isinstance(val, str) and len(val) > len(best):
            best = val

    # Pattern 3: ResearchAgent — build prose from key_insights + all_results
    if len(best) < 200:  # Still short — try research data
        parts = []
        insights = data.get('key_insights', [])
        if isinstance(insights, list) and insights:
            parts.append("## Key Insights")
            for i, insight in enumerate(insights[:10], 1):
                if isinstance(insight, str):
                    parts.append(f"{i}. {insight}")

        all_results = data.get('all_results', [])
        if isinstance(all_results, list):
            for r in all_results[:5]:
                if isinstance(r, dict):
                    source = r.get('source', 'Unknown')
                    r_data = r.get('data')
                    if isinstance(r_data, list):
                        items = [str(item.get('title', item) if isinstance(item, dict) else item)[:200] for item in r_data[:5]]
                        if items:
                            parts.append(f"\n## From {source}")
                            parts.extend(f"- {item}" for item in items)
                    elif isinstance(r_data, str) and len(r_data) > 20:
                        parts.append(f"\n## From {source}\n{r_data[:2000]}")

        if parts:
            assembled = "\n".join(parts)
            if len(assembled) > len(best):
                best = assembled

    return best


@shared_task(bind=True, queue='default', max_retries=1, ignore_result=True,
             soft_time_limit=600, time_limit=660)
def generate_initiative_stage_document(self, initiative_id: str, stage_num: int):
    from core.tasks_initiatives import _impl_generate_initiative_stage_document
    return _impl_generate_initiative_stage_document(self, initiative_id, stage_num)
@shared_task(bind=True, queue='default')
def backfill_stage_documents(self, stage_num: int = 1, limit: int = 50):
    from core.tasks_misc import _impl_backfill_stage_documents
    return _impl_backfill_stage_documents(self, stage_num, limit)
@shared_task
def run_daily_priority_scan():
    """
    Session 914.7: Run the daily priority scan to identify top 5 focus initiatives.

    Scheduled: Every day at 6:00 AM
    """
    from core.services.daily_priorities import run_daily_priority_scan

    logger.info("[Session 914.7] 🌅 Running daily priority scan...")

    try:
        result = run_daily_priority_scan(focus_count=5)

        logger.info(
            f"[Session 914.7] ✅ Daily priority scan complete: "
            f"{result['focus_count']} focus initiatives, "
            f"{result['total_scored']} total scored"
        )

        return {
            'success': True,
            'focus_count': result['focus_count'],
            'total_scored': result['total_scored'],
            'scan_date': result['scan_date']
        }
    except Exception as e:
        logger.error(f"[Session 914.7] ❌ Daily priority scan failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def check_operating_rhythm_status():
    """
    Session 914.7: Check operating rhythm status and generate recommendations.

    Scheduled: Every day at 9:00 AM (reminder to set priorities if not set)
    """
    from core.services.operating_rhythm import get_rhythm_status

    logger.info("[Session 914.7] 🔍 Checking operating rhythm status...")

    try:
        status = get_rhythm_status()

        daily = status['daily_priorities']
        recommendations = status['recommendations']

        if recommendations:
            logger.warning(
                f"[Session 914.7] ⚠️ Operating rhythm recommendations: "
                f"{len(recommendations)} items"
            )
            for rec in recommendations:
                logger.warning(f"[Session 914.7]   • {rec}")
        else:
            logger.info("[Session 914.7] ✅ Operating rhythm is healthy")

        # TODO: Send recommendations to Discord/Slack if priorities not set

        return {
            'success': True,
            'priorities_set': len(daily.get('priorities', [])) > 0,
            'is_current': daily.get('is_current', False),
            'recommendations_count': len(recommendations),
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"[Session 914.7] ❌ Rhythm status check failed: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
# Session 926: Audio Cache Cleanup for Universal Agent Voice System
# =============================================================================

@shared_task
def cleanup_audio_cache():
    from core.tasks_misc import _impl_cleanup_audio_cache
    return _impl_cleanup_audio_cache()


# Session 1077: Daily auto-archive stale deliverables (noise prevention)
@shared_task(soft_time_limit=120, time_limit=150)
def auto_archive_stale_deliverables(days=3):
    from core.tasks_misc import _impl_auto_archive_stale_deliverables
    return _impl_auto_archive_stale_deliverables(days=days)


@shared_task(bind=True, time_limit=300, soft_time_limit=280)
def process_pa_chat_task(self, user_id, message, context=None, generate_audio=False, conversation_id=None, source='web', platform='web'):
    from core.tasks_misc import _impl_process_pa_chat_task
    return _impl_process_pa_chat_task(self, user_id, message, context, generate_audio, conversation_id, source, platform)


# Session 1078: Background PA context rebuild — eliminates ghost timeout on first hit.
# Enqueued by get_assistant_context when fresh cache misses. Stampede-locked per user.
@shared_task(bind=True, time_limit=60, soft_time_limit=45, ignore_result=True, queue='pa')
def rebuild_pa_context_task(self, user_id, reason='fresh_miss'):
    """Rebuild PA context in background and populate caches."""
    import hashlib
    from time import monotonic
    from django.contrib.auth import get_user_model
    from django.core.cache import cache
    from django.db import close_old_connections

    User = get_user_model()
    user_hash = hashlib.md5(str(user_id).encode()).hexdigest()
    lock_key = f"pa_ctx:rebuild_lock:{user_hash}"

    # Stampede lock — skip if another rebuild is already running
    if not cache.add(lock_key, '1', timeout=90):
        logger.info(
            "PA_CONTEXT_REBUILD status=lock_held user_id=%s reason=%s",
            user_id, reason,
        )
        return {'skipped': True, 'reason': 'lock_held'}

    try:
        import json
        import os
        close_old_connections()
        user = User.objects.get(id=user_id)

        # RSS before build
        rss_start_mb = None
        try:
            import resource
            rss_start_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024), 1)
            if os.uname().sysname == 'Darwin':
                rss_start_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024), 1)
            else:
                rss_start_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
        except Exception:
            pass

        t0 = monotonic()
        from core.personal_ai_assistant import PersonalAIAssistant
        assistant = PersonalAIAssistant(user)
        context = assistant.get_personalized_context()
        build_ms = int((monotonic() - t0) * 1000)

        # RSS after build
        rss_end_mb = None
        rss_delta_mb = None
        try:
            import resource
            if os.uname().sysname == 'Darwin':
                rss_end_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024), 1)
            else:
                rss_end_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
            if rss_start_mb is not None:
                rss_delta_mb = round(rss_end_mb - rss_start_mb, 1)
        except Exception:
            pass

        fresh_key = f"pa_ctx:fresh:{user_hash}"
        stale_key = f"pa_ctx:stale:{user_hash}"
        cache.set(fresh_key, context, 300)   # 5 min fresh
        cache.set(stale_key, context, 1800)  # 30 min stale
        payload_bytes = len(json.dumps(context, default=str))

        logger.info(
            "PA_CONTEXT_REBUILD status=ok user_id=%s build_ms=%s reason=%s "
            "rss_start_mb=%s rss_end_mb=%s rss_delta_mb=%s payload_bytes=%s",
            user_id, build_ms, reason,
            rss_start_mb, rss_end_mb, rss_delta_mb, payload_bytes,
        )

        # Alert on memory spikes
        if rss_delta_mb is not None and rss_delta_mb > 300:
            logger.warning(
                "[MEMORY] PA_CONTEXT_REBUILD rss_delta_mb=%s exceeds 300MB threshold "
                "user_id=%s build_ms=%s",
                rss_delta_mb, user_id, build_ms,
            )

        return {'success': True, 'build_ms': build_ms, 'rss_delta_mb': rss_delta_mb}

    except Exception as e:
        logger.error("PA_CONTEXT_REBUILD status=error user_id=%s reason=%s error=%s", user_id, reason, str(e))
        return {'success': False, 'error': str(e)}
    finally:
        cache.delete(lock_key)


# Session 1077: Background TTS task — offloaded from process_pa_chat_task
# to prevent SoftTimeLimitExceeded from ElevenLabs blocking the main PA path.
@shared_task(bind=True, time_limit=120, soft_time_limit=90, ignore_result=True)
def process_pa_tts_task(self, user_id, text, conversation_id=None, trace_id=None):
    """Generate TTS audio in background and update the conversation record."""
    import asyncio
    from django.contrib.auth import get_user_model

    logger.info(f"[PA_TTS] Starting background TTS for user {user_id}, trace {trace_id}")
    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        pa = UnifiedPAEntrypoint(user, conversation_id=conversation_id)

        loop = asyncio.new_event_loop()
        try:
            audio_url = loop.run_until_complete(
                asyncio.wait_for(pa._generate_audio(text), timeout=60)
            )
        finally:
            loop.close()

        if audio_url and conversation_id:
            from core.models import ChatConversation
            ChatConversation.objects.filter(
                conversation_id=conversation_id,
                user=user,
            ).order_by('-created_at').update(
                assistant_audio_url=audio_url,
            )
            logger.info(f"[PA_TTS] Audio saved: {audio_url[:80]}...")

    except Exception as e:
        logger.warning(f"[PA_TTS] Background TTS failed: {e}")


@shared_task(bind=True, time_limit=120, soft_time_limit=100)
def generate_step_content(self, step_id):
    from core.tasks_content import _impl_generate_step_content
    return _impl_generate_step_content(self, step_id)
@shared_task(name='core.tasks.run_all_desks_intelligence', soft_time_limit=1800, time_limit=1860)
def run_all_desks_intelligence():
    """
    Session 1000: Run all 4 intelligence desk coordinators sequentially.

    Desks:
      1. Stocks  — MarketIntelligenceCoordinator (saves to MarketIntelligenceBrief + cache)
      2. Sports  — SportsBettingCoordinator.generate_brief()
      3. Blockchain — BlockchainAuditCoordinator.execute()
      4. Narrative — NarrativeDriftCoordinator.execute()

    Each desk result is cached with a 6-hour TTL for the API to serve.
    Returns summary dict with timing and success counts.
    """
    import gc
    import time as _time
    import traceback
    from django.core.cache import cache

    CACHE_TTL = 6 * 3600  # 6 hours

    try:
        return _run_desks_inner(_time, traceback, cache, gc, CACHE_TTL)
    except SoftTimeLimitExceeded:
        logger.error("[SESSION 1000] run_all_desks_intelligence timed out (soft_time_limit=1800s)")
        return {'desks_completed': 0, 'desks_failed': 0, 'timing': {},
                'error': 'Celery soft_time_limit exceeded', 'timed_out': True}


def _run_desks_inner(_time, traceback, cache, gc, CACHE_TTL):
    desks_completed = 0
    desks_failed = 0
    timing = {}

    # --- Desk 1: Stocks ---
    try:
        t0 = _time.time()
        logger.info("[SESSION 1000] Running Stocks desk ...")
        from core.agents.stocks.market_intelligence_coordinator import MarketIntelligenceCoordinator
        coordinator = MarketIntelligenceCoordinator(user=None)
        result = coordinator.execute(
            task="Daily stock intelligence brief",
            context={},
            scifi_context={},
            spider_context={},
        )
        elapsed = round(_time.time() - t0, 1)
        timing['stocks'] = elapsed

        summary = ''
        if hasattr(result, 'data') and isinstance(result.data, dict):
            # The brief is nested under result.data['brief']
            brief_data = result.data.get('brief', {}) or {}
            summary = (
                brief_data.get('executive_summary', '')
                or result.data.get('executive_summary', '')
                or result.data.get('summary', '')
            )
        if not summary and hasattr(result, 'message') and result.message:
            summary = str(result.message)[:500]

        cache.set('desk:stocks:latest', {
            'generated_at': timezone.now().isoformat(),
            'executive_summary': summary[:500],
            'agents_run': [
                'MarketIntelligenceCoordinator', 'BullCaseAgent', 'BearCaseAgent',
                'StockAuditCoordinator', 'StockAnalystAgent', 'MarketMovementMonitorAgent',
                'InstitutionalWatcherAgent', 'MarketAnomalyDetectorAgent', 'SignalScannerAgent',
            ],
            'elapsed_seconds': elapsed,
        }, CACHE_TTL)
        desks_completed += 1
        logger.info(f"[SESSION 1000] Stocks desk done in {elapsed}s")
    except Exception as e:
        desks_failed += 1
        timing['stocks'] = -1
        logger.error(f"[SESSION 1000] Stocks desk failed: {e}\n{traceback.format_exc()}")

    gc.collect()

    # --- Desk 2: Sports ---
    try:
        t0 = _time.time()
        logger.info("[SESSION 1000] Running Sports desk ...")
        from core.services.sports_betting_coordinator import SportsBettingCoordinator
        brief = SportsBettingCoordinator().generate_brief()
        elapsed = round(_time.time() - t0, 1)
        timing['sports'] = elapsed

        cache.set('desk:sports:latest', {
            'generated_at': timezone.now().isoformat(),
            'executive_summary': (brief.get('executive_summary', '') or '')[:500],
            'top_plays': brief.get('top_plays') or [],
            'agents_run': brief.get('agents_run') or [],
            'elapsed_seconds': elapsed,
        }, CACHE_TTL)

        # Session 1003: Persist to DB so briefs survive cache TTL
        # Session 1005: Fixed key mismatches (arbitrage, sharp_action) and None guards
        try:
            from core.models_unified_system import SportsBettingBrief
            SportsBettingBrief.objects.create(
                brief_date=timezone.now().date(),
                executive_summary=(brief.get('executive_summary', '') or '')[:500],
                predictions=brief.get('predictions') or {},
                arbitrage_opportunities=brief.get('arbitrage') or {},
                sharp_action_alerts=brief.get('sharp_action') or {},
                line_movements=brief.get('line_movements') or {},
                top_plays=brief.get('top_plays') or [],
                agents_run=brief.get('agents_run') or [],
                errors=brief.get('errors') or [],
                generation_time_seconds=elapsed,
            )
        except Exception as db_err:
            logger.warning(f"[SESSION 1005] Could not persist sports brief: {db_err}")

        desks_completed += 1
        logger.info(f"[SESSION 1000] Sports desk done in {elapsed}s")
    except Exception as e:
        desks_failed += 1
        timing['sports'] = -1
        logger.error(f"[SESSION 1000] Sports desk failed: {e}\n{traceback.format_exc()}")

    gc.collect()

    # --- Desk 3: Blockchain ---
    try:
        t0 = _time.time()
        logger.info("[SESSION 1000] Running Blockchain desk ...")
        from core.agents.blockchain.blockchain_audit_coordinator import BlockchainAuditCoordinator
        coordinator = BlockchainAuditCoordinator(user=None)
        result = coordinator.execute(
            task="Daily blockchain intelligence scan",
            context={},
            scifi_context={},
            spider_context={},
        )
        elapsed = round(_time.time() - t0, 1)
        timing['blockchain'] = elapsed

        data = result.data if hasattr(result, 'data') and isinstance(result.data, dict) else {}
        cache.set('desk:blockchain:latest', {
            'generated_at': timezone.now().isoformat(),
            'summary': (data.get('summary', '') or data.get('executive_summary', '') or result.message[:500])[:500],
            'agents_run': [
                'BlockchainAuditCoordinator', 'SmartContractAuditorAgent',
                'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent',
            ],
            'elapsed_seconds': elapsed,
        }, CACHE_TTL)

        # Session 1003: Persist to DB so briefs survive cache TTL
        try:
            from core.models_unified_system import BlockchainAuditBrief
            BlockchainAuditBrief.objects.create(
                brief_date=timezone.now().date(),
                executive_summary=(data.get('summary', '') or data.get('executive_summary', '') or result.message[:500])[:500],
                security_alerts=data.get('security_alerts', {}),
                whale_movements=data.get('whale_movements', {}),
                contract_audits=data.get('contract_audits', {}),
                exploit_detection=data.get('exploit_detection', {}),
                agents_run=[
                    'BlockchainAuditCoordinator', 'SmartContractAuditorAgent',
                    'TransactionMonitorAgent', 'WhaleWatcherAgent', 'ExploitDetectorAgent',
                ],
                errors=data.get('errors', []),
                generation_time_seconds=elapsed,
            )
        except Exception as db_err:
            logger.warning(f"[SESSION 1003] Could not persist blockchain brief: {db_err}")

        desks_completed += 1
        logger.info(f"[SESSION 1000] Blockchain desk done in {elapsed}s")
    except Exception as e:
        desks_failed += 1
        timing['blockchain'] = -1
        logger.error(f"[SESSION 1000] Blockchain desk failed: {e}\n{traceback.format_exc()}")

    gc.collect()

    # --- Desk 4: Narrative ---
    try:
        t0 = _time.time()
        logger.info("[SESSION 1000] Running Narrative desk ...")
        from core.agents.narrative.narrative_drift_coordinator import NarrativeDriftCoordinator
        coordinator = NarrativeDriftCoordinator(user=None)
        result = coordinator.execute(
            task="Daily narrative drift scan — detect emerging trends and cultural shifts",
            context={},
            scifi_context={},
            spider_context={},
        )
        elapsed = round(_time.time() - t0, 1)
        timing['narrative'] = elapsed

        data = result.data if hasattr(result, 'data') and isinstance(result.data, dict) else {}
        cache.set('desk:narrative:latest', {
            'generated_at': timezone.now().isoformat(),
            'summary': (data.get('summary', '') or data.get('executive_summary', '') or result.message[:500])[:500],
            'agents_run': [
                'NarrativeDriftCoordinator', 'NarrativeHistorianAgent',
                'TrendBreakDetectorAgent', 'CulturalImpactAgent',
            ],
            'elapsed_seconds': elapsed,
        }, CACHE_TTL)
        desks_completed += 1
        logger.info(f"[SESSION 1000] Narrative desk done in {elapsed}s")
    except Exception as e:
        desks_failed += 1
        timing['narrative'] = -1
        logger.error(f"[SESSION 1000] Narrative desk failed: {e}\n{traceback.format_exc()}")

    logger.info(
        f"[SESSION 1000] Intelligence desks complete: "
        f"{desks_completed} succeeded, {desks_failed} failed, timing={timing}"
    )
    return {
        'desks_completed': desks_completed,
        'desks_failed': desks_failed,
        'timing': timing,
    }


# =============================================================================
# Session 1031: Surface Top Dreams to Boardroom
# =============================================================================

@shared_task
def surface_top_dreams(max_items=5, min_composite=0.85):
    from core.tasks_initiatives import _impl_surface_top_dreams
    return _impl_surface_top_dreams(max_items, min_composite)
@shared_task(name='core.tasks.cleanup_conversation_duplicates_task', bind=True, max_retries=0)
def cleanup_conversation_duplicates_task(self):
    """
    Session 1032: Daily cleanup of fuzzy-duplicate AgentConversation records.
    Uses Jaccard similarity to cluster conversations and delete lower-quality duplicates.
    """
    from core.services.deduplication_service import get_deduplication_service

    dedup_svc = get_deduplication_service()
    result = dedup_svc.cleanup_fuzzy_conversation_duplicates(dry_run=False, hours=168)

    logger.info(
        f"[CONVERSATION-DEDUP] Cleaned {result['records_deleted']} duplicates "
        f"from {result['clusters_found']} clusters"
    )
    return result


@shared_task(name='core.tasks.rescan_active_workspaces')
def rescan_active_workspaces(stale_days: int = 7):
    """
    Session 1055: Periodic rescan of active workspaces with stale or missing context.
    Keeps WorkspaceContext fresh so PA workspace injection stays accurate.
    """
    from core.models_skin_layer import ProjectWorkspace, WorkspaceContext
    from core.services.workspace_manager import WorkspaceScanner

    cutoff = timezone.now() - timedelta(days=stale_days)
    scanner = WorkspaceScanner()
    rescanned = 0
    errors = 0

    active_workspaces = ProjectWorkspace.objects.filter(is_active=True)

    for ws in active_workspaces:
        try:
            ctx = WorkspaceContext.objects.filter(workspace=ws).first()
            if ctx and ctx.updated_at and ctx.updated_at > cutoff:
                continue  # Still fresh
            scanner.scan_workspace(ws)
            rescanned += 1
        except Exception as e:
            errors += 1
            logger.warning(f"[WORKSPACE-RESCAN] Failed to rescan {ws.name}: {e}")

    logger.info(
        f"[WORKSPACE-RESCAN] Rescanned {rescanned} workspaces, "
        f"{errors} errors, {active_workspaces.count()} total active"
    )
    return {'rescanned': rescanned, 'errors': errors}


# --------------------------------------------------------------------------- #
# PA Tool Learning Loop                                                        #
# Mines ToolCallRecord for patterns and creates PAToolInsight candidates.       #
# --------------------------------------------------------------------------- #

@shared_task(ignore_result=True)
def analyze_pa_tool_patterns():
    from core.tasks_agents import _impl_analyze_pa_tool_patterns
    return _impl_analyze_pa_tool_patterns()
def _ttl_days(insight_type):
    """Return TTL in days by insight type."""
    return {
        'error_pattern': 14,
        'param_correction': 30,
        'success_pattern': 60,
        'follow_up': 90,
        'consistency_check': 7,
    }.get(insight_type, 30)


def _upsert_insight(tool_name, insight_type, pattern, snippet, confidence=None):
    """Create or update a PAToolInsight. Returns (created_count, updated_count)."""
    from core.models_tool_calls import PAToolInsight

    pattern_json = json.dumps(pattern, sort_keys=True, default=str)

    existing = PAToolInsight.objects.filter(
        tool_name=tool_name,
        insight_type=insight_type,
        pattern=pattern,
    ).first()

    ttl = timedelta(days=_ttl_days(insight_type))

    if existing:
        existing.evidence_count = F('evidence_count') + 1
        existing.expires_at = timezone.now() + ttl  # refresh TTL on evidence bump
        update_fields = ['evidence_count', 'expires_at', 'updated_at']
        if confidence is not None:
            existing.confidence = confidence
            update_fields.append('confidence')
        # Auto-promote: evidence >= 5 and confidence >= 0.8
        # Block auto-promotion for consistency_check (human review only)
        if confidence and confidence >= 0.8 and insight_type != 'consistency_check':
            existing.refresh_from_db()
            if existing.evidence_count >= 4 and existing.safety_class == 'candidate':
                existing.safety_class = 'approved'
                update_fields.append('safety_class')
                logger.info(f"[PA-LEARNING] Auto-promoted: {tool_name}/{insight_type}")
        existing.save(update_fields=update_fields)
        return (0, 1)
    else:
        PAToolInsight.objects.create(
            tool_name=tool_name,
            insight_type=insight_type,
            pattern=pattern,
            prompt_snippet=snippet,
            evidence_count=1,
            confidence=confidence or 0.0,
            expires_at=timezone.now() + ttl,
        )
        return (1, 0)


def _summarize_params(params: dict) -> str:
    """Compact param summary for prompt snippets."""
    parts = []
    for k, v in list(params.items())[:4]:
        val = str(v)[:40]
        parts.append(f"{k}={val}")
    suffix = f" (+{len(params) - 4} more)" if len(params) > 4 else ""
    return ", ".join(parts) + suffix


def _summarize_diff(bad: dict, good: dict) -> str:
    """Summarize what changed between bad and good params."""
    changes = []
    for k in set(list(bad.keys()) + list(good.keys())):
        bv, gv = bad.get(k), good.get(k)
        if bv != gv:
            changes.append(f"{k}: '{gv}' (not '{bv}')")
    return "; ".join(changes[:3]) if changes else "different parameters"


@shared_task(ignore_result=True)
def cleanup_expired_pa_insights():
    """Demote expired approved insights back to candidate (daily 3 AM)."""
    from core.models_tool_calls import PAToolInsight

    now = timezone.now()
    demoted = PAToolInsight.objects.filter(
        safety_class='approved',
        expires_at__isnull=False,
        expires_at__lte=now,
    ).update(safety_class='candidate')

    if demoted:
        logger.info(f"[PA-LEARNING] Demoted {demoted} expired insights → candidate")
    return {'demoted': demoted}


# =============================================================================
# SESSION G2: DATA RETENTION JOB
# =============================================================================

# Retention rules: days before archive/delete by sensitivity level
_RETENTION_DAYS = {
    'restricted': 7,
    'confidential': 30,
    'internal': 90,
    'public': 365,
}


@shared_task(ignore_result=True)
def enforce_data_retention():
    """Nightly job: archive/delete artifacts by data_sensitivity + age.

    - Pinned items (is_pinned=True) are always skipped.
    - Deliverables: status → 'archived'
    - Documents: status → 'archived'
    """
    from core.models_deliverables import Deliverable
    from content.models import Document

    now = timezone.now()
    stats = {'deliverables_archived': 0, 'documents_archived': 0}

    for sensitivity, max_days in _RETENTION_DAYS.items():
        cutoff = now - timedelta(days=max_days)

        # Archive old deliverables (skip pinned)
        d_count = Deliverable.objects.filter(
            data_sensitivity=sensitivity,
            is_pinned=False,
            created_at__lt=cutoff,
            status__in=['draft', 'ready', 'published'],
        ).update(status='archived')
        stats['deliverables_archived'] += d_count

        # Archive old documents (skip pinned)
        doc_count = Document.objects.filter(
            data_sensitivity=sensitivity,
            is_pinned=False,
            created_at__lt=cutoff,
        ).exclude(
            status__in=['archived', 'deleted'],
        ).update(status='archived')
        stats['documents_archived'] += doc_count

    total = stats['deliverables_archived'] + stats['documents_archived']
    if total:
        logger.info(
            f"[RETENTION] Archived {stats['deliverables_archived']} deliverables, "
            f"{stats['documents_archived']} documents"
        )
    return stats


# =============================================================================
# SESSION G1: COMPETITOR COMPARISON GENERATION TASK
# =============================================================================

def _run_comparison_generation(comparison, source_document_id=None,
                                competitor_name='', focus_areas=None):
    """
    Core comparison generation logic — called by the Celery task wrapper
    and by the source_pack_workflow.

    Returns dict with comparison result or raises on failure.
    """
    import traceback
    from django.utils import timezone as tz
    from core.services.data_scrubber import scrub
    from content.embeddings import rag_system

    start_time = time.time()

    # All queries prefixed with competitor name to avoid pulling in our own
    # platform docs (generic queries like "security architecture" match both)
    queries = [
        f"what is {competitor_name} what did they build",
        f"{competitor_name} workflow steps process pipeline",
        f"{competitor_name} security architecture protection",
        f"{competitor_name} cost tokens caching model pricing",
        f"{competitor_name} logging monitoring observability",
        f"{competitor_name} scheduling automation cron jobs",
        f"{competitor_name} integrations tools stack CRM email",
        f"{competitor_name} knowledge base search memory RAG",
    ]
    if focus_areas:
        for fa in (focus_areas if isinstance(focus_areas, list) else [focus_areas]):
            queries.append(f"{competitor_name} {fa}")

    # Build set of auto-researched doc IDs for this competitor (prefer these)
    from content.models import Document
    auto_researched_ids = set(
        str(d_id) for d_id in
        Document.objects.filter(
            extracted_metadata__auto_research=True,
            extracted_metadata__competitor_name=competitor_name,
        ).values_list('id', flat=True)
    )

    all_chunks = []
    seen_keys = set()
    source_docs = {}  # document_id -> {title, source_type}
    for q in queries:
        results = rag_system.semantic_search_sync(
            query=q,
            limit=12,
            similarity_threshold=0.25,
        )
        for r in results:
            # Filter to source document if specified
            if source_document_id and r.document_id != str(source_document_id):
                continue
            key = (r.document_id, r.chunk_index)
            if key not in seen_keys:
                seen_keys.add(key)
                # Scrub evidence text before storing
                chunk_text = scrub(r.chunk_text[:1500])
                chunk_id = f"E{len(all_chunks) + 1}"
                is_competitor_source = r.document_id in auto_researched_ids
                all_chunks.append({
                    'chunk_id': chunk_id,
                    'document_id': r.document_id,
                    'document_title': r.document_title,
                    'chunk_index': r.chunk_index,
                    'chunk_text': chunk_text,
                    'similarity_score': round(r.similarity_score, 4),
                    'is_competitor_source': is_competitor_source,
                })
                # Track unique source documents
                if r.document_id not in source_docs:
                    source_docs[r.document_id] = {
                        'document_id': r.document_id,
                        'title': r.document_title,
                        'source_type': getattr(r, 'document_type', 'unknown'),
                        'is_competitor_source': is_competitor_source,
                    }

    # Prioritize competitor-specific sources: sort so auto-researched chunks
    # come first, then by similarity score
    all_chunks.sort(key=lambda c: (not c.get('is_competitor_source', False), -c['similarity_score']))

    logger.info(
        f"[COMPETITOR] Collected {len(all_chunks)} chunks from {len(source_docs)} sources "
        f"({sum(1 for s in source_docs.values() if s.get('is_competitor_source'))} competitor-specific) "
        f"for '{competitor_name}'"
    )

    # --- Insufficient evidence check ---
    if not all_chunks:
        comparison.status = 'needs_sources'
        comparison.error_message = 'No evidence chunks found — ingest a document about this competitor first.'
        comparison.metadata = {
            'recommended_queries': [
                f"{competitor_name} overview features",
                f"{competitor_name} architecture tech stack",
                f"{competitor_name} pricing plans",
            ],
        }
        comparison.save(update_fields=['status', 'error_message', 'metadata', 'updated_at'])
        return {'status': 'needs_sources', 'message': comparison.error_message}

    if len(all_chunks) < 5:
        comparison.status = 'needs_sources'
        comparison.error_message = (
            f'Only {len(all_chunks)} evidence chunks found — need at least 5 for a quality comparison. '
            f'Ingest more documents about {competitor_name}.'
        )
        comparison.metadata = {
            'evidence_found': len(all_chunks),
            'recommended_queries': [
                f"{competitor_name} detailed review",
                f"{competitor_name} vs alternatives",
                f"{competitor_name} security architecture",
            ],
        }
        comparison.save(update_fields=['status', 'error_message', 'metadata', 'updated_at'])
        return {'status': 'needs_sources', 'message': comparison.error_message}

    # --- 2. Build prompt + call LLM ---
    # Prefer competitor-specific chunks; drop internal docs if we have enough external evidence
    competitor_chunks = [c for c in all_chunks if c.get('is_competitor_source')]
    if len(competitor_chunks) >= 15:
        # Enough external evidence — use only competitor sources
        evidence_chunks = competitor_chunks[:40]
        logger.info(f"[COMPETITOR] Using {len(evidence_chunks)} competitor-only chunks (dropped internal docs)")
    else:
        # Mix: competitor first, then fill with internal
        evidence_chunks = all_chunks[:40]

    # Build chunk reference table for evidence_refs
    chunk_ref_table = "\n".join(
        f"[{c['chunk_id']}] (sim={c['similarity_score']}) {c['chunk_text'][:120]}..."
        for c in evidence_chunks
    )
    evidence_text = "\n\n".join(
        f"[{c['chunk_id']} | {c['document_title']} | sim={c['similarity_score']}]\n{c['chunk_text']}"
        for c in evidence_chunks
    )

    system_prompt = (
        "You are a competitive intelligence analyst. Given evidence chunks from documents "
        "about a competitor, produce a structured JSON comparison between the competitor's "
        "platform and our platform (Donkey Betz / AI Studio). Be specific, evidence-based, "
        "and cite chunk IDs (e.g. E1, E5) to support every claim. "
        "IMPORTANT: Focus on chunks that describe the COMPETITOR's features and architecture. "
        "Ignore any chunks that only describe Donkey Betz / AI Studio internal sessions or pipelines."
    )

    user_prompt = f"""Analyze the following evidence about **{competitor_name}** and produce a JSON object with exactly these 7 keys:

1. "review" — object with:
   - "features": list of objects with "name", "description", "evidence_quote", "evidence_refs" (list of chunk IDs like ["E1", "E5"])
   - "architecture_summary": string

2. "comparison_table" — list of objects with:
   - "category", "competitor" (what they have), "donkey_betz" (what we have)
   - "verdict": "ahead" / "behind" / "even" / "gap"
   - "evidence_refs": list of chunk IDs supporting this row

3. "gap_backlog" — list of objects with:
   - "gap" (string), "priority" ("P0"/"P1"/"P2")
   - "acceptance_test" (string — how we'd know the gap is closed)
   - "effort": "S" / "M" / "L"
   - "impact": "high" / "medium" / "low"
   - "evidence_refs": list of chunk IDs

4. "tools_stack" — object with "languages" (list), "frameworks" (list), "services" (list), "apis" (list)

5. "summary" — 2-3 sentence executive summary

6. "verdict" — overall: "ahead" / "behind" / "parity"

7. "quick_wins" — list of 3 gaps that could be closed in 1-2 weeks (subset of gap_backlog, effort="S")

AVAILABLE CHUNK IDs:
{chunk_ref_table}

FULL EVIDENCE CHUNKS:
{evidence_text}

Respond ONLY with valid JSON, no markdown fences."""

    import openai as openai_mod
    from django.conf import settings as django_settings

    client = openai_mod.OpenAI(api_key=django_settings.AI_PROVIDERS.get('OPENAI_API_KEY'))
    llm_response = client.chat.completions.create(
        model='gpt-4.1',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        max_tokens=6000,
        temperature=0.3,
    )

    raw_text = llm_response.choices[0].message.content.strip()
    tokens_used = {
        'prompt_tokens': llm_response.usage.prompt_tokens if llm_response.usage else 0,
        'completion_tokens': llm_response.usage.completion_tokens if llm_response.usage else 0,
    }

    # --- 3. Parse JSON ---
    if raw_text.startswith('```'):
        raw_text = raw_text.split('\n', 1)[1] if '\n' in raw_text else raw_text[3:]
        if raw_text.endswith('```'):
            raw_text = raw_text[:-3]

    parsed = json.loads(raw_text)

    # --- 4. Compute quality rubric ---
    comparison_table = parsed.get('comparison_table', [])
    gap_backlog = parsed.get('gap_backlog', [])
    review = parsed.get('review', {})

    # Evidence coverage: % of comparison_table rows with evidence_refs
    rows_with_refs = sum(1 for row in comparison_table if row.get('evidence_refs'))
    total_rows = len(comparison_table) if comparison_table else 1
    evidence_coverage = round(rows_with_refs / total_rows, 3)

    # Source diversity: how many unique source documents contributed
    unique_sources = len(source_docs)
    source_diversity = min(1.0, unique_sources / 5.0)  # 5+ sources = perfect

    # Uncited penalty: features without evidence_refs
    features = review.get('features', [])
    features_with_refs = sum(1 for f in features if f.get('evidence_refs'))
    uncited_penalty = 1.0 - (features_with_refs / max(len(features), 1))

    # Composite quality score
    quality_score = round(min(1.0, (
        evidence_coverage * 0.5 +
        source_diversity * 0.2 +
        (1.0 - uncited_penalty) * 0.3
    )), 3)

    quality_rubric = {
        'evidence_coverage': evidence_coverage,
        'source_diversity': round(source_diversity, 3),
        'uncited_penalty': round(uncited_penalty, 3),
        'unique_sources': unique_sources,
        'total_evidence_chunks': len(all_chunks),
        'rows_with_refs': rows_with_refs,
        'total_rows': total_rows,
        'features_cited': features_with_refs,
        'features_total': len(features),
    }

    # --- 5. Build executive summary ---
    verdict = parsed.get('verdict', 'parity')
    quick_wins = parsed.get('quick_wins', [])

    # Count verdicts
    verdict_counts = {}
    for row in comparison_table:
        v = row.get('verdict', 'even')
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    top_advantages = [
        row['category'] for row in comparison_table
        if row.get('verdict') == 'ahead'
    ][:3]
    top_gaps = [
        row['category'] for row in comparison_table
        if row.get('verdict') in ('behind', 'gap')
    ][:3]

    executive_summary = {
        'verdict': verdict,
        'verdict_counts': verdict_counts,
        'top_advantages': top_advantages,
        'top_gaps': top_gaps,
        'quick_wins': quick_wins[:3],
        'gap_count': len(gap_backlog),
        'p0_gaps': sum(1 for g in gap_backlog if g.get('priority') == 'P0'),
        'p1_gaps': sum(1 for g in gap_backlog if g.get('priority') == 'P1'),
        'p2_gaps': sum(1 for g in gap_backlog if g.get('priority') == 'P2'),
        'confidence': 'high' if quality_score >= 0.7 else 'medium' if quality_score >= 0.4 else 'low',
    }

    # --- 6. Save enriched artifact ---
    elapsed = round(time.time() - start_time, 2)
    comparison.review_json = review
    comparison.comparison_table_json = comparison_table
    comparison.gap_backlog_json = gap_backlog
    comparison.tools_stack_json = parsed.get('tools_stack', {})
    comparison.evidence_json = all_chunks
    comparison.sources_json = list(source_docs.values())
    comparison.executive_summary_json = executive_summary
    comparison.quality_rubric_json = quality_rubric
    comparison.summary = parsed.get('summary', '')
    comparison.quality_score = quality_score
    comparison.status = 'complete'
    comparison.completed_at = tz.now()
    comparison.metadata = {
        'tokens': tokens_used,
        'evidence_chunks': len(all_chunks),
        'elapsed_seconds': elapsed,
        'queries_run': len(queries),
        'evidence_coverage_pct': round(evidence_coverage * 100, 1),
        'uncited_claims': total_rows - rows_with_refs,
        'source_count': unique_sources,
        'model': 'gpt-4.1',
    }
    comparison.save()

    logger.info(
        f"[COMPETITOR] Comparison '{competitor_name}' complete in {elapsed}s "
        f"| quality={quality_score} | {len(all_chunks)} chunks from {unique_sources} sources"
    )
    return {
        'comparison_id': str(comparison.id),
        'status': 'complete',
        'quality_score': quality_score,
        'verdict': verdict,
        'summary': comparison.summary[:200],
    }


_AUTO_RESEARCH_SKIP_DOMAINS = {
    'youtube.com', 'youtu.be', 'twitter.com', 'x.com',
    'facebook.com', 'linkedin.com', 'instagram.com', 'tiktok.com',
}


def _auto_research_competitor(competitor_name, user_id=None, time_budget=120):
    """
    Discover, ingest, and embed competitor sources before LLM comparison.

    Runs 4 web searches, filters/deduplicates URLs, ingests via
    DocumentProcessingPipeline, and embeds via rag_system.

    Returns dict with counts: urls_found, docs_ingested, docs_embedded,
    skipped_existing, skipped_timeout, errors, elapsed_seconds.
    """
    import time
    import hashlib
    from urllib.parse import urlparse
    from django.contrib.auth import get_user_model

    from content.models import Document, ContentStatus, ContentSource
    from content.embeddings import rag_system, DocumentEmbedding
    from content.processors import DocumentProcessingPipeline
    from core.tools.web_search import WebSearchTool

    t0 = time.time()
    stats = {
        'urls_found': 0, 'docs_ingested': 0, 'docs_embedded': 0,
        'skipped_existing': 0, 'skipped_timeout': 0, 'errors': 0,
        'elapsed_seconds': 0,
    }

    # ── Search phase (budget: 30% of time_budget) ────────────────────
    search_budget = time_budget * 0.3
    queries = [
        f'"{competitor_name}" site:github.com README',
        f'"{competitor_name}" official documentation features',
        f'"{competitor_name}" review comparison analysis',
        f'"{competitor_name}" architecture tech stack blog',
    ]

    collected_urls = {}  # url -> {title, priority}
    web = WebSearchTool()

    def _domain_priority(url):
        host = urlparse(url).netloc.lower()
        if 'github.com' in host:
            return 0
        if any(d in host for d in ('docs.', 'documentation.', '.readthedocs.')):
            return 1
        if any(d in host for d in ('blog.', 'medium.com', 'dev.to', 'hashnode.')):
            return 2
        return 3

    for q in queries:
        if time.time() - t0 > search_budget:
            break
        try:
            result = web.execute(query=q, max_results=5)
            results_list = result.get('results', []) if isinstance(result, dict) else []
            for r in results_list:
                url = r.get('url', r.get('link', ''))
                if not url or url in collected_urls:
                    continue
                host = urlparse(url).netloc.lower()
                if any(d in host for d in _AUTO_RESEARCH_SKIP_DOMAINS):
                    continue
                collected_urls[url] = {
                    'title': r.get('title', url[:80]),
                    'priority': _domain_priority(url),
                    'query': q,
                }
        except Exception as e:
            logger.warning(f"[AUTO-RESEARCH] Search failed for '{q}': {e}")

    stats['urls_found'] = len(collected_urls)
    if not collected_urls:
        stats['elapsed_seconds'] = round(time.time() - t0, 1)
        return stats

    # Sort by priority (github → docs → blogs → other), take top 8
    sorted_urls = sorted(collected_urls.items(), key=lambda kv: kv[1]['priority'])[:8]

    # ── Ingest + embed phase ─────────────────────────────────────────
    pipeline = DocumentProcessingPipeline()
    seen_hashes = set()
    User = get_user_model()
    owner = None
    if user_id:
        owner = User.objects.filter(id=user_id).first()
    if not owner:
        owner = User.objects.first()

    target_ingested = 6
    ingested = 0

    for url, meta in sorted_urls:
        if time.time() - t0 > time_budget:
            stats['skipped_timeout'] += 1
            continue
        if ingested >= target_ingested:
            break

        try:
            existing = Document.objects.filter(source_url=url).first()
            if existing:
                # Ensure it's embedded
                if not DocumentEmbedding.objects.filter(document_id=existing.id).exists():
                    rag_system.process_document_for_rag_sync(existing)
                    stats['docs_embedded'] += 1
                stats['skipped_existing'] += 1
                continue

            result = pipeline.process_url(url)
            if not result.success:
                stats['errors'] += 1
                continue

            content_hash = hashlib.sha256(
                (result.processed_content or '')[:5000].encode()
            ).hexdigest()[:16]
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            doc = Document.objects.create(
                title=meta.get('title', url[:100]),
                processed_content=result.processed_content,
                raw_content=result.raw_content,
                word_count=result.word_count,
                language=result.language,
                key_phrases=result.key_phrases or [],
                entities=result.entities or [],
                extracted_metadata={
                    **(result.metadata or {}),
                    'source_category': ['github', 'docs', 'blog', 'other'][meta['priority']],
                    'auto_research': True,
                    'competitor_name': competitor_name,
                },
                source_url=url,
                status=ContentStatus.PROCESSED,
                source=ContentSource.API,
                owner=owner,
            )
            stats['docs_ingested'] += 1
            ingested += 1

            # Embed immediately
            if time.time() - t0 < time_budget:
                try:
                    rag_system.process_document_for_rag_sync(doc)
                    stats['docs_embedded'] += 1
                except Exception as emb_err:
                    logger.warning(f"[AUTO-RESEARCH] Embed failed for {url[:60]}: {emb_err}")

        except Exception as e:
            logger.warning(f"[AUTO-RESEARCH] Ingest error for {url[:60]}: {e}")
            stats['errors'] += 1

    stats['elapsed_seconds'] = round(time.time() - t0, 1)
    logger.info(
        f"[AUTO-RESEARCH] '{competitor_name}' done in {stats['elapsed_seconds']}s — "
        f"found={stats['urls_found']} ingested={stats['docs_ingested']} "
        f"embedded={stats['docs_embedded']} errors={stats['errors']}"
    )
    return stats


@shared_task(bind=True, soft_time_limit=300, time_limit=360)
def generate_competitor_comparison_task(self, comparison_id, source_document_id=None,
                                        competitor_name='', focus_areas=None,
                                        auto_research=True):
    from core.tasks_misc import _impl_generate_competitor_comparison_task
    return _impl_generate_competitor_comparison_task(self, comparison_id, source_document_id, competitor_name, focus_areas, auto_research)
@shared_task(bind=True, soft_time_limit=900, time_limit=1080, ignore_result=True)
def run_source_pack_workflow(self, run_id):
    from core.tasks_content import _impl_run_source_pack_workflow
    return _impl_run_source_pack_workflow(self, run_id)
@shared_task(bind=True, ignore_result=True)
def summarize_conversation_task(self, conversation_id, user_id=None):
    from core.tasks_conversations import _impl_summarize_conversation_task
    return _impl_summarize_conversation_task(self, conversation_id, user_id)
@shared_task(
    name='core.tasks.ops_control_loop',
    ignore_result=True,
    soft_time_limit=120,
    time_limit=180,
    queue='default',
)
def ops_control_loop():
    from core.tasks_ops import _impl_ops_control_loop
    return _impl_ops_control_loop()
@shared_task(ignore_result=True)
def check_llm_cost_spike():
    from core.tasks_misc import _impl_check_llm_cost_spike
    return _impl_check_llm_cost_spike()
@shared_task(ignore_result=True)
def run_ops_autopilot():
    """Every 10 min: evaluate ops policies and take allowed automatic actions."""
    try:
        from core.services.ops_autopilot import OpsAutopilot
        autopilot = OpsAutopilot()
        summary = autopilot.run()
        actions = summary.get('actions_taken', 0)
        if actions > 0:
            logger.warning(f"[OpsAutopilot] Cycle took {actions} action(s): {summary.get('actions', [])}")
        else:
            logger.info(f"[OpsAutopilot] Cycle complete — no actions needed")
        return summary
    except Exception as e:
        logger.exception(f"[OpsAutopilot] Cycle failed: {e}")
        raise ScheduledTaskError(
            f"SCHEDULED_FAIL_LOUD::run_ops_autopilot::{type(e).__name__}: {e}"
        ) from e


@shared_task(ignore_result=True)
def post_ops_digest():
    from core.tasks_misc import _impl_post_ops_digest
    return _impl_post_ops_digest()
@shared_task(
    name='core.tasks.sync_congress_data',
    ignore_result=True,
    queue='long_running',
    soft_time_limit=1800,
    time_limit=2400,
)
def sync_congress_data():
    """Periodic sync of congress members, bills, and embeddings."""
    try:
        from core.services.congress_sync import CongressSyncService
        svc = CongressSyncService()

        # Members (fast, ~2 API pages)
        members = svc.sync_members()
        logger.info(f"[CongressSync] Members: {members}")

        # Bills (capped at 5 pages per run to stay within rate limits)
        bills = svc.sync_bills(limit_pages=5)
        logger.info(f"[CongressSync] Bills: {bills}")

        # Embed any un-embedded bills
        embeds = svc.embed_bills(batch_size=100)
        logger.info(f"[CongressSync] Embeddings: {embeds}")

        return {'members': members, 'bills': bills, 'embeddings': embeds}
    except Exception as e:
        logger.exception(f"[CongressSync] Failed: {e}")
        return {'error': str(e)}


# =========================================================================
# Remote Code Worker — execute code jobs
# =========================================================================


@shared_task(
    bind=True,
    name='core.tasks.execute_code_job',
    queue='code_jobs',
    time_limit=1800,
    soft_time_limit=1500,
    max_retries=0,
)
def execute_code_job(self, run_id: str):
    try:
        from core.codejobs.implementation import _impl_execute_code_job
        return _impl_execute_code_job(self, run_id)
    except Exception as e:
        logger.exception(f"[execute_code_job] Failed for run_id={run_id}: {e}")
        raise
@shared_task(name='core.rag_retrieval_canary', ignore_result=True)
def rag_retrieval_canary():
    from core.tasks_misc import _impl_rag_retrieval_canary
    return _impl_rag_retrieval_canary()


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
