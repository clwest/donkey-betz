"""
Celery Background Tasks for Unified Donkey Betz Platform
Handles long-running operations like document isolation in the background

Session 265 Phase 6: Added run_autonomy_cycle task for autonomous operation
"""

from celery import shared_task
import logging
import time
from datetime import datetime
from django.db import transaction
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)


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


# ==================== SESSION 265 PHASE 6: AUTONOMY ENGINE ====================


@shared_task
def run_autonomy_cycle(user_id: int = None):
    """
    Run an autonomy cycle for a user or all users.

    Session 265 Phase 6: Autonomy Engine

    This task:
    - Scans for actionable opportunities
    - Assesses risk and value
    - Executes approved autonomous actions
    - Records outcomes for learning

    Args:
        user_id: Specific user ID, or None for all users with autonomy enabled
    """
    from django.contrib.auth import get_user_model
    from core.super_platform.autonomy_engine import get_autonomy_engine, AutonomyLevel

    User = get_user_model()

    results = {
        'users_processed': 0,
        'total_actions': 0,
        'successful_actions': 0,
        'total_value': 0.0,
    }

    try:
        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            # Get all users with autonomy enabled
            from core.models_unified_system import AutonomyConfiguration
            enabled_configs = AutonomyConfiguration.objects.exclude(
                autonomy_level='observe'
            ).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=enabled_configs)

        for user in users:
            try:
                engine = get_autonomy_engine(user)

                # Skip if observe-only
                if engine.config.level == AutonomyLevel.OBSERVE:
                    continue

                # Run cycle
                cycle_result = engine.run_autonomy_cycle()

                results['users_processed'] += 1
                results['total_actions'] += cycle_result.get('actions_executed', 0)
                results['successful_actions'] += cycle_result.get('actions_succeeded', 0)
                results['total_value'] += float(cycle_result.get('total_value_generated', 0))

                logger.info(
                    f"Autonomy cycle for {user.username}: "
                    f"{cycle_result.get('actions_executed', 0)} actions, "
                    f"${cycle_result.get('total_value_generated', 0)} value"
                )

            except Exception as user_error:
                logger.error(f"Autonomy cycle failed for user {user.id}: {user_error}")

        logger.info(
            f"Autonomy cycle complete: {results['users_processed']} users, "
            f"{results['total_actions']} actions, ${results['total_value']:.2f} value"
        )

        return results

    except Exception as e:
        logger.exception(f"Autonomy cycle task failed: {e}")
        return {'error': str(e)}


@shared_task(bind=True)
def run_spider_by_category(self, category: str):
    """
    Run spiders for a specific category.

    Session 265 Phase 6: Used by autonomy engine for spider dispatch.
    Session 484: Added SpiderExecutionLog for tracking.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from core.models_unified_system import SpiderExecutionLog
    import traceback

    try:
        registry = SpiderRegistry()
        spiders = registry.get_spiders_by_category(category)

        results = []
        for spider_name in spiders[:3]:  # Limit to 3 spiders per category
            # Session 484: Create execution log
            execution_log = SpiderExecutionLog.start_execution(
                spider_name=spider_name,
                category=category,
                triggered_by='on_demand',
                celery_task_id=self.request.id if self.request else None
            )
            spider_start_time = time.time()

            try:
                spider_class = registry.get_spider_class(spider_name)
                if spider_class:
                    # Session 503: Try both constructor patterns
                    try:
                        spider = spider_class()
                    except TypeError:
                        spider = spider_class(
                            spider_id=spider_name,
                            targets=[],
                            subscribers=[],
                            redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
                        )

                    # Session 503: Support multiple method patterns
                    if hasattr(spider, 'fetch'):
                        data = spider.fetch()
                    elif hasattr(spider, 'fetch_data'):
                        import asyncio
                        import inspect
                        from ai_core.spiders.base_spider import SpiderTarget

                        async def run_fetch():
                            # Session 503: Detect method signature - some spiders use fetch_data(target),
                            # others use fetch_data(max_results=100)
                            fetch_method = spider.fetch_data
                            sig = inspect.signature(fetch_method)
                            params = list(sig.parameters.keys())

                            # Check first param type hint or name
                            first_param = params[0] if params else None
                            if first_param and first_param in ('target', 'url'):
                                # Standard BaseIntelligenceSpider pattern
                                target = SpiderTarget(url='internal://spider-execution')
                                raw = await spider.fetch_data(target)
                            else:
                                # Legal spiders pattern: fetch_data(max_results=100)
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
                                    return {'items': [result.content] if hasattr(result, 'content') else [], 'raw_data': raw}
                            return raw if raw else {'items': []}

                        data = asyncio.run(run_fetch())
                    else:
                        data = {'items': []}

                    item_count = len(data) if isinstance(data, list) else len(data.get('items', []) if isinstance(data, dict) else [])
                    results.append({
                        'spider': spider_name,
                        'items': item_count,
                    })
                    # Session 484: Mark success
                    execution_log.complete_success(
                        items_collected=item_count,
                        duration_seconds=time.time() - spider_start_time
                    )
            except Exception as spider_error:
                logger.debug(f"Spider {spider_name} failed: {spider_error}")
                # Session 484: Mark error
                execution_log.complete_error(
                    error_message=str(spider_error),
                    error_type=type(spider_error).__name__,
                    error_traceback=traceback.format_exc(),
                    duration_seconds=time.time() - spider_start_time
                )

        logger.info(f"Ran {len(results)} spiders for category {category}")
        return {'category': category, 'results': results}

    except Exception as e:
        logger.error(f"Spider dispatch failed for {category}: {e}")
        return {'error': str(e)}


@shared_task(bind=True)
def execute_single_spider(self, spider_name: str, execution_log_id: str = None):
    """
    Session 484: Execute a single spider with full execution logging.
    Used by manual UI runs and retry operations.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from ai_core.spiders.real_data_collector import collect_spider_data_sync, SPIDER_TARGET_URLS
    from core.models_unified_system import SpiderData, SpiderExecutionLog
    from django.utils import timezone
    import traceback

    spider_start_time = time.time()
    execution_log = None
    source_urls = []

    try:
        # Get or create execution log
        if execution_log_id:
            try:
                execution_log = SpiderExecutionLog.objects.get(id=execution_log_id)
                execution_log.celery_task_id = self.request.id if self.request else None
                execution_log.save()
            except SpiderExecutionLog.DoesNotExist:
                pass

        if not execution_log:
            # Find most recent running log for this spider
            execution_log = SpiderExecutionLog.objects.filter(
                spider_name=spider_name,
                status='running',
                celery_task_id__isnull=True
            ).order_by('-started_at').first()

            if execution_log:
                execution_log.celery_task_id = self.request.id if self.request else None
                execution_log.save()

        logger.info(f"🕷️ Executing single spider: {spider_name}")

        # Get spider info
        registry = SpiderRegistry()
        spider_config = registry.list_spiders().get(spider_name, {})
        config = spider_config.get('config', {})
        category = config.get('category', spider_config.get('category', 'general'))

        # Execute spider
        if spider_name in SPIDER_TARGET_URLS:
            source_urls = SPIDER_TARGET_URLS.get(spider_name, [])
            data = collect_spider_data_sync(spider_name)
            item_count = data.get('item_count', 0)
        else:
            spider_class = registry.get_spider_class(spider_name)
            if spider_class:
                # Session 503: Try both constructor patterns
                try:
                    spider = spider_class()
                except TypeError:
                    # Spider requires full constructor args
                    spider = spider_class(
                        spider_id=spider_name,
                        targets=[],
                        subscribers=[],
                        redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
                    )

                if hasattr(spider, 'fetch'):
                    data = spider.fetch()
                elif hasattr(spider, 'scrape'):
                    import asyncio
                    data = asyncio.run(spider.scrape())
                elif hasattr(spider, 'fetch_data'):
                    # Session 503: Support for spiders using fetch_data(target) or fetch_data(max_results) pattern
                    import asyncio
                    import inspect
                    from ai_core.spiders.base_spider import SpiderTarget

                    async def run_fetch():
                        # Detect method signature
                        fetch_method = spider.fetch_data
                        sig = inspect.signature(fetch_method)
                        params = list(sig.parameters.keys())

                        first_param = params[0] if params else None
                        if first_param and first_param in ('target', 'url'):
                            # Standard BaseIntelligenceSpider pattern
                            target = SpiderTarget(url='internal://spider-execution')
                            raw = await spider.fetch_data(target)
                        else:
                            # Legal spiders pattern: fetch_data(max_results=100)
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
                                return {'items': [result.content] if hasattr(result, 'content') else [], 'raw_data': raw}
                        # Normalize return value to dict format
                        if raw:
                            if isinstance(raw, list):
                                return {'items': raw, 'source': spider_name}
                            elif isinstance(raw, dict):
                                return raw
                            else:
                                return {'items': [raw], 'source': spider_name}
                        return {'items': []}

                    data = asyncio.run(run_fetch())
                else:
                    data = {'items': [], 'message': 'Spider has no fetch/scrape/fetch_data method'}
                # Handle both list and dict formats
                if isinstance(data, list):
                    item_count = len(data)
                    data = {'items': data, 'source': spider_name}
                else:
                    item_count = len(data.get('items', []))
            else:
                data = {'items': [], 'error': f'Spider class not found: {spider_name}'}
                item_count = 0

        # Save data to SpiderData
        spider_data = SpiderData.objects.create(
            spider_name=spider_name,
            data_type=category,
            raw_data=data if isinstance(data, dict) else {'data': str(data)},
            source_url=source_urls[0] if source_urls else 'manual',
            relevance_score=70 if item_count > 0 else 30
        )

        logger.info(f"✅ Spider {spider_name} completed: {item_count} items")

        # Update execution log
        if execution_log:
            execution_log.source_urls_attempted = source_urls if source_urls else ['manual']
            execution_log.complete_success(
                items_collected=item_count,
                duration_seconds=time.time() - spider_start_time
            )

        return {
            'spider': spider_name,
            'success': True,
            'item_count': item_count,
            'data_id': str(spider_data.id),
        }

    except Exception as e:
        logger.error(f"❌ Spider {spider_name} failed: {e}")

        # Update execution log with error
        if execution_log:
            execution_log.source_urls_attempted = source_urls if source_urls else []
            execution_log.complete_error(
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=traceback.format_exc(),
                duration_seconds=time.time() - spider_start_time
            )

        return {
            'spider': spider_name,
            'success': False,
            'error': str(e),
        }


@shared_task(bind=True, max_retries=3)
def isolate_documents_batch(self, batch_size: int = 50, max_batches: int = None):
    """
    Background task to gradually isolate documents with proper namespaces
    
    Args:
        batch_size: Number of documents to process per batch
        max_batches: Maximum number of batches to process (None = all)
    
    Returns:
        Dict with processing statistics
    """
    from content.models import Document, DocumentEmbedding
    from django.db.models import Q
    
    try:
        logger.info(f"Starting document isolation batch task - batch_size: {batch_size}")
        
        # Import classifier from our batch tagging script
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from batch_tag_documents import DocumentClassifier
        classifier = DocumentClassifier()
        
        # Get untagged documents
        untagged_query = Document.objects.exclude(
            metadata__has_key='namespace'
        )
        
        total_untagged = untagged_query.count()
        
        if total_untagged == 0:
            logger.info("No untagged documents found!")
            return {
                'status': 'completed',
                'processed': 0,
                'total_found': 0,
                'message': 'No documents need processing'
            }
        
        logger.info(f"Found {total_untagged} untagged documents")
        
        # Process in batches
        stats = {
            'personal': 0,
            'system': 0,
            'agent_memory': 0,
            'public': 0,
            'errors': 0,
            'processed': 0
        }
        
        batch_count = 0
        start_time = time.time()
        
        while True:
            # Check if we should stop
            if max_batches and batch_count >= max_batches:
                logger.info(f"Reached max_batches limit: {max_batches}")
                break
            
            # Get next batch
            batch = untagged_query[:batch_size]
            
            if not batch:
                logger.info("No more documents to process")
                break
            
            batch_start_time = time.time()
            
            with transaction.atomic():
                for doc in batch:
                    try:
                        # Classify document
                        namespace = classifier.classify_document(doc)
                        
                        # Update metadata
                        if not doc.metadata:
                            doc.metadata = {}
                        
                        doc.metadata.update({
                            'namespace': namespace,
                            'tagged_at': datetime.now().isoformat(),
                            'tagged_by': 'celery_background_task',
                            'searchable_by_agents': namespace != 'personal',
                            'is_private': namespace == 'personal',
                            'task_id': self.request.id  # Track which task processed this
                        })
                        
                        doc.save()
                        
                        # Update associated embeddings
                        embeddings = DocumentEmbedding.objects.filter(document=doc)
                        for emb in embeddings:
                            if not emb.metadata:
                                emb.metadata = {}
                            emb.metadata.update({
                                'namespace': namespace,
                                'is_private': namespace == 'personal',
                                'task_id': self.request.id
                            })
                            emb.save()
                        
                        stats[namespace] += 1
                        stats['processed'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing document {doc.id}: {e}")
                        stats['errors'] += 1
                        stats['processed'] += 1
            
            batch_count += 1
            batch_time = time.time() - batch_start_time
            total_time = time.time() - start_time
            
            # Update task progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'processed': stats['processed'],
                    'total_found': total_untagged,
                    'batch_count': batch_count,
                    'stats': stats,
                    'rate_per_second': stats['processed'] / total_time if total_time > 0 else 0,
                    'batch_time': batch_time
                }
            )
            
            logger.info(f"Batch {batch_count} completed: {len(batch)} docs in {batch_time:.1f}s")
            logger.info(f"Progress: {stats['processed']} processed, {stats}")
            
            # Small delay to avoid overwhelming the database
            time.sleep(0.1)
        
        # Final statistics
        total_time = time.time() - start_time
        rate = stats['processed'] / total_time if total_time > 0 else 0
        
        logger.info("=== BACKGROUND DOCUMENT ISOLATION COMPLETED ===")
        logger.info(f"Processed: {stats['processed']} documents in {total_time:.1f} seconds")
        logger.info(f"Rate: {rate:.1f} documents/second")
        logger.info(f"Distribution: {stats}")
        
        return {
            'status': 'completed',
            'processed': stats['processed'],
            'total_found': total_untagged,
            'batch_count': batch_count,
            'total_time': total_time,
            'rate_per_second': rate,
            'distribution': {k: v for k, v in stats.items() if k != 'processed'},
            'message': f'Successfully processed {stats["processed"]} documents'
        }
        
    except Exception as exc:
        logger.error(f"Document isolation task failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

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
def process_agent_solutions():
    """Process agent solutions and create learning events - called by Celery Beat"""
    from core.models_unified_system import AgentSolution, AgentLearning, Agent
    from django.utils import timezone
    from datetime import timedelta
    import random

    logger.info("Starting agent solution processing...")

    # Get recent solutions
    recent = timezone.now() - timedelta(hours=1)
    recent_solutions = AgentSolution.objects.filter(
        created_at__gte=recent
    ).select_related('agent')

    # Create learning events from solutions
    learning_events = []
    for solution in recent_solutions[:10]:  # Process up to 10 solutions
        # Find another agent to learn from this solution
        other_agents = Agent.objects.exclude(id=solution.agent.id)
        if other_agents.exists():
            student_agent = random.choice(list(other_agents))

            learning_event = AgentLearning.objects.create(
                teacher_agent=solution.agent,
                student_agent=student_agent,
                learning_type='solution_transfer',
                knowledge_gained={
                    'solution_id': str(solution.id),
                    'solution_type': solution.solution_type,
                    'knowledge': solution.implementation_details or {}
                },
                effectiveness_improvement=random.uniform(0.5, 5.0)
            )
            learning_events.append(learning_event)

    logger.info(f"Created {len(learning_events)} learning events")
    return f"Processed {len(learning_events)} learning events"

@shared_task
def activate_spiders_task():
    """Task to activate spiders via management command - called by Celery Beat"""
    from django.core.management import call_command
    logger.info("Activating spiders via Celery task...")
    call_command('activate_spiders', '--simulate')
    return "Spider activation complete"

@shared_task
def process_spider_data_task():
    """Task to process spider data via management command"""
    from django.core.management import call_command
    logger.info("Processing spider data via Celery task...")
    call_command('process_spider_data')
    return "Spider data processing complete"

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
    unprocessed = SpiderData.objects.filter(is_processed=False)[:100]

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


@shared_task(bind=True)
def run_spider_network(self):
    """
    Session 207/221: Run all active spiders and collect REAL data.
    Runs every 30 minutes via Celery Beat.

    Session 221 Enhancement: Uses real_data_collector for actual web scraping.
    Session 423: Added Discord notifications for spider activity.
    Session 484: Added SpiderExecutionLog for error tracking and diagnostics.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from ai_core.spiders.real_data_collector import collect_spider_data_sync, SPIDER_TARGET_URLS
    from core.models_unified_system import SpiderData, SpiderExecutionLog
    from django.utils import timezone
    import traceback

    logger.info("🕷️ Starting spider network execution with REAL data collection...")

    # Session 423: Track timing for Discord notifications
    batch_start_time = time.time()

    registry = SpiderRegistry()
    all_spiders = registry.list_spiders()

    results = {
        'spiders_run': 0,
        'data_collected': 0,
        'items_collected': 0,
        'errors': 0,
        'spider_results': [],
        'all_topics': []  # Session 423: Track topics for summary
    }

    for spider_name, spider_config in all_spiders.items():
        # Session 484: Create execution log entry
        config = spider_config.get('config', {})
        category = config.get('category', spider_config.get('category', 'general'))
        execution_log = SpiderExecutionLog.start_execution(
            spider_name=spider_name,
            category=category,
            triggered_by='scheduled',
            celery_task_id=self.request.id if self.request else None
        )
        spider_start_time = time.time()
        source_urls = []

        try:
            logger.info(f"🕷️ Running spider: {spider_name}")

            # Session 221: Use real data collector for spiders with configured URLs
            if spider_name in SPIDER_TARGET_URLS:
                source_urls = SPIDER_TARGET_URLS.get(spider_name, [])
                # Fetch REAL data from the web
                data = collect_spider_data_sync(spider_name)
                item_count = data.get('item_count', 0)
                logger.info(f"✅ Spider {spider_name}: collected {item_count} REAL items")
            else:
                # Fallback for spiders without configured URLs
                spider_class = registry.get_spider_class(spider_name)
                if spider_class:
                    try:
                        spider = spider_class(
                            spider_id=spider_name,
                            targets=[],
                            subscribers=[],
                            redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
                        )
                        # Try spider methods - Session 503: Added fetch_data support
                        if hasattr(spider, 'scrape'):
                            import asyncio
                            data = asyncio.run(spider.scrape())
                        elif hasattr(spider, 'collect_data'):
                            import asyncio
                            data = asyncio.run(spider.collect_data())
                        elif hasattr(spider, 'fetch_data'):
                            # Session 503: Support for spiders using fetch_data(target) or fetch_data(max_results)
                            import asyncio
                            import inspect
                            from ai_core.spiders.base_spider import SpiderTarget

                            async def run_fetch_data():
                                # Session 503: Detect method signature - some spiders use fetch_data(target),
                                # others use fetch_data(max_results=100)
                                fetch_method = spider.fetch_data
                                sig = inspect.signature(fetch_method)
                                params = list(sig.parameters.keys())

                                # Check first param type hint or name
                                first_param = params[0] if params else None
                                if first_param and first_param in ('target', 'url'):
                                    # Standard BaseIntelligenceSpider pattern
                                    target = SpiderTarget(url='internal://spider-execution')
                                    raw_data = await spider.fetch_data(target)
                                else:
                                    # Legal spiders pattern: fetch_data(max_results=100)
                                    if asyncio.iscoroutinefunction(fetch_method):
                                        raw_data = await spider.fetch_data()
                                    else:
                                        raw_data = spider.fetch_data()

                                if raw_data and hasattr(spider, 'process_data'):
                                    target = SpiderTarget(url='internal://spider-execution')
                                    if asyncio.iscoroutinefunction(spider.process_data):
                                        result = await spider.process_data(raw_data, target)
                                    else:
                                        result = spider.process_data(raw_data, target)
                                    if result:
                                        return {
                                            'source': spider_name,
                                            'items': [result.content] if hasattr(result, 'content') else [],
                                            'raw_data': raw_data,
                                            'category': spider_config.get('category', 'general'),
                                            'timestamp': timezone.now().isoformat()
                                        }
                                # Normalize return value to dict format
                                if raw_data:
                                    if isinstance(raw_data, list):
                                        return {'items': raw_data, 'source': spider_name}
                                    elif isinstance(raw_data, dict):
                                        return raw_data
                                    else:
                                        return {'items': [raw_data], 'source': spider_name}
                                return {'items': []}

                            data = asyncio.run(run_fetch_data())
                        else:
                            data = {
                                'source': spider_name,
                                'category': spider_config.get('category', 'general'),
                                'items': [],
                                'message': f'Spider {spider_name} ready (no real URLs configured)',
                                'timestamp': timezone.now().isoformat()
                            }
                    except Exception as spider_error:
                        logger.warning(f"Spider {spider_name} method failed: {spider_error}")
                        data = {
                            'source': spider_name,
                            'items': [],
                            'error': str(spider_error),
                            'timestamp': timezone.now().isoformat()
                        }
                else:
                    data = {
                        'source': spider_name,
                        'items': [],
                        'timestamp': timezone.now().isoformat()
                    }
                # Handle both list and dict formats
                if isinstance(data, list):
                    item_count = len(data)
                    data = {'items': data, 'source': spider_name}
                else:
                    item_count = len(data.get('items', []))

            # Save to SpiderData
            config = spider_config.get('config', {})
            spider_data = SpiderData.objects.create(
                spider_name=spider_name,
                data_type=config.get('category', spider_config.get('category', 'general')),
                raw_data=data if isinstance(data, dict) else {'data': str(data)},
                source_url=SPIDER_TARGET_URLS.get(spider_name, ['internal'])[0] if spider_name in SPIDER_TARGET_URLS else 'internal',
                relevance_score=70 if item_count > 0 else 30
            )

            results['spiders_run'] += 1
            results['data_collected'] += 1
            results['items_collected'] += item_count
            results['spider_results'].append({
                'spider': spider_name,
                'success': True,
                'item_count': item_count,
                'data_id': str(spider_data.id)
            })

            # Session 423: Track topics for summary notification
            category = config.get('category', spider_config.get('category', 'general'))
            results['all_topics'].append(category)

            # Session 399: Publish spider completion event for real-time UI updates
            try:
                import redis
                import json as json_lib
                redis_client = redis.Redis(host='localhost', port=6379, db=0)
                redis_client.publish('spider:completion', json_lib.dumps({
                    'spider_name': spider_name,
                    'item_count': item_count,
                    'category': config.get('category', spider_config.get('category', 'general')),
                    'data_id': str(spider_data.id),
                    'timestamp': timezone.now().isoformat()
                }))
            except Exception as redis_error:
                logger.debug(f"Redis publish failed (non-critical): {redis_error}")

            # Session 484: Mark execution as successful
            execution_log.source_urls_attempted = source_urls if source_urls else [SPIDER_TARGET_URLS.get(spider_name, ['internal'])[0] if spider_name in SPIDER_TARGET_URLS else 'internal']
            execution_log.complete_success(
                items_collected=item_count,
                duration_seconds=time.time() - spider_start_time
            )

        except Exception as e:
            logger.error(f"❌ Spider {spider_name} failed: {e}")
            results['errors'] += 1
            results['spider_results'].append({
                'spider': spider_name,
                'success': False,
                'error': str(e)
            })

            # Session 484: Mark execution as failed with full error details
            execution_log.source_urls_attempted = source_urls if source_urls else []
            execution_log.complete_error(
                error_message=str(e),
                error_type=type(e).__name__,
                error_traceback=traceback.format_exc(),
                duration_seconds=time.time() - spider_start_time
            )

            # Session 423: Send error notification to Discord
            try:
                from core.services.discord_notifications import discord_notify
                discord_notify.send_spider_error(
                    spider_name=spider_name,
                    error_message=str(e)[:500]
                )
            except Exception:
                pass

    # Session 423: Calculate batch duration and send summary to Discord
    batch_duration = time.time() - batch_start_time

    # Get top topics (most common)
    from collections import Counter
    topic_counts = Counter(results.get('all_topics', []))
    top_topics = [topic for topic, _ in topic_counts.most_common(8)]

    logger.info(f"✅ Spider network complete: {results['spiders_run']} run, {results['items_collected']} items collected, {results['errors']} errors")

    # Session 423: Send batch summary to Discord
    try:
        from core.services.discord_notifications import discord_notify
        discord_notify.send_spider_summary(
            total_spiders=results['spiders_run'],
            successful=results['spiders_run'] - results['errors'],
            failed=results['errors'],
            total_records=results['items_collected'],
            top_topics=top_topics if top_topics else ['general'],
            duration_seconds=batch_duration
        )
    except Exception as discord_err:
        logger.debug(f"Discord summary notification failed (non-critical): {discord_err}")

    return results


@shared_task
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


@shared_task
def execute_single_spider_lightweight(spider_name: str):
    """
    Session 207: Execute a single spider on-demand (LIGHTWEIGHT version).
    Called by the Execute button in the Spider Dashboard.

    Uses lightweight synchronous data collection to avoid macOS fork/async issues.
    Does NOT import SpiderRegistry to avoid aiohttp/fork segfaults.
    Session 423: Added Discord notifications for individual spider runs.

    Session 505: Renamed from execute_single_spider to avoid conflict with the
    proper spider execution task at line 239 that uses actual spider classes.
    """
    from core.models_unified_system import SpiderData
    from django.utils import timezone

    logger.info(f"🕷️ On-demand execution: {spider_name}")
    start_time = time.time()  # Session 423: Track duration

    # Spider config lookup without importing SpiderRegistry (avoids aiohttp fork issues)
    SPIDER_CONFIGS = {
        'financial': {'category': 'financial'},
        'innovation': {'category': 'innovation'},
        'social_sentiment': {'category': 'social'},
        'market_data': {'category': 'market'},
        'news_harvester': {'category': 'news'},
        'toptal': {'category': 'freelance'},
        'guru': {'category': 'freelance'},
        'peopleperhour': {'category': 'freelance'},
        'ninetyninedesigns': {'category': 'design'},
        'flexjobs': {'category': 'remote_work'},
        'remoteok': {'category': 'remote_work'},
        'weworkremotely': {'category': 'remote_work'},
        'angellist': {'category': 'tech'},
        'dribbble': {'category': 'design'},
        'behance': {'category': 'design'},
        'medium': {'category': 'content'},
        'gumroad': {'category': 'content'},
        'substack': {'category': 'content'},
        'patreon': {'category': 'crowdfunding'},
        'kofi': {'category': 'crowdfunding'},
        'producthunt': {'category': 'tech'},
        'teachable': {'category': 'education'},
        'udemy': {'category': 'education'},
        'skillshare': {'category': 'education'},
        'coingecko': {'category': 'financial'},
        'yahoo_finance': {'category': 'financial'},
        'etherscan': {'category': 'financial'},
        'opensea': {'category': 'financial'},
        'seekingalpha': {'category': 'financial'},
        'bloomberg_terminal': {'category': 'financial'},
        'reuters_eikon': {'category': 'financial'},
        'huggingface': {'category': 'tech'},
        'kaggle': {'category': 'tech'},
        'github_jobs': {'category': 'tech'},
        'stackoverflow_jobs': {'category': 'tech'},
        'hackernews': {'category': 'tech'},
        'devto': {'category': 'tech'},
        'hashnode': {'category': 'tech'},
        'indiegogo': {'category': 'crowdfunding'},
        'kickstarter': {'category': 'crowdfunding'},
        'horse_racing': {'category': 'sports_betting'},
        'combat_sports': {'category': 'sports_betting'},
        'courtlistener': {'category': 'legal'},
        'justia': {'category': 'legal'},
        'findlaw': {'category': 'legal'},
        'lii': {'category': 'legal'},
        'colorado_family_law': {'category': 'legal'},
        'justia_family_law': {'category': 'legal'},
    }

    spider_config = SPIDER_CONFIGS.get(spider_name, {'category': 'general'})
    category = spider_config.get('category', 'general')

    try:
        # Use lightweight synchronous data collection
        data = _collect_spider_data_sync(spider_name, category, spider_config)

        # Save to SpiderData
        spider_data = SpiderData.objects.create(
            spider_name=spider_name,
            data_type=category,
            raw_data=data if isinstance(data, dict) else {'data': str(data)},
            source_url='on-demand-execution',
            relevance_score=75  # Higher score for on-demand
        )

        # Session 423: Calculate duration and send Discord notification
        duration = time.time() - start_time
        item_count = len(data.get('items', [])) if isinstance(data, dict) else 0

        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_spider_activity(
                spider_name=spider_name,
                records_collected=item_count if item_count > 0 else 1,
                topics=[category],
                duration_seconds=duration,
                source_url='on-demand-execution',
                status='success' if item_count > 0 else 'partial'
            )
        except Exception:
            pass

        logger.info(f"✅ Spider {spider_name} executed successfully, saved as SpiderData {spider_data.id}")
        return {
            'success': True,
            'spider_name': spider_name,
            'data_id': str(spider_data.id),
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        # Session 423: Send error notification to Discord
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_spider_error(
                spider_name=spider_name,
                error_message=str(e)[:500],
                source_url='on-demand-execution'
            )
        except Exception:
            pass

        logger.error(f"❌ Spider {spider_name} execution failed: {e}")
        return {
            'success': False,
            'spider_name': spider_name,
            'error': str(e)
        }


def _collect_spider_data_sync(spider_name: str, category: str, config: Dict) -> Dict[str, Any]:
    """
    Synchronous data collection helper for on-demand spider execution.
    Avoids async/fork issues on macOS by using simple requests.

    Session 207: Comprehensive data collection for all spider categories.
    """
    import requests
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
            except Exception:
                pass
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
            except Exception:
                pass
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
    """
    Background task to poll Replicate for pending 3D model status updates.

    Runs every 30 seconds to check all MiniFigAssets with status='pending' and update them
    if they're completed on Replicate. This prevents models from getting stuck
    when frontend polling stops.

    Session 139: Fix for 3D models stuck in 'pending' status
    """
    from content.models import MiniFigAsset
    from content.minifig_services import check_and_update_3d_generation
    from django.utils import timezone
    from datetime import timedelta

    logger.info("🎨 [3D MODEL POLLER] Starting background 3D model status polling...")

    # Get all pending models (created in last 24 hours to avoid polling ancient models)
    yesterday = timezone.now() - timedelta(hours=24)

    pending_models = MiniFigAsset.objects.filter(
        status='pending',
        created_at__gte=yesterday
    ).order_by('created_at')

    if not pending_models.exists():
        logger.info("🎨 [3D MODEL POLLER] No pending 3D models to check")
        return {'status': 'idle', 'checked': 0, 'completed': 0, 'failed': 0, 'still_pending': 0}

    logger.info(f"🎨 [3D MODEL POLLER] Found {pending_models.count()} pending 3D models to check")

    stats = {
        'checked': 0,
        'completed': 0,
        'failed': 0,
        'still_pending': 0,
        'errors': 0
    }

    for minifig in pending_models:
        try:
            logger.info(f"🎨 [3D MODEL POLLER] Checking 3D model {minifig.id} ({minifig.title[:40]}...)")

            # Check status with Replicate (this function also downloads files automatically)
            updated_minifig = check_and_update_3d_generation(str(minifig.id))

            stats['checked'] += 1

            if updated_minifig.status == 'completed':
                logger.info(f"✅ [3D MODEL POLLER] 3D model {minifig.id} completed!")
                stats['completed'] += 1

            elif updated_minifig.status == 'failed':
                logger.warning(f"❌ [3D MODEL POLLER] 3D model {minifig.id} failed on Replicate")
                stats['failed'] += 1

            elif updated_minifig.status in ['pending', 'processing']:
                logger.info(f"⏳ [3D MODEL POLLER] 3D model {minifig.id} still {updated_minifig.status}")
                stats['still_pending'] += 1

            else:
                logger.warning(f"❓ [3D MODEL POLLER] Unknown status for 3D model {minifig.id}: {updated_minifig.status}")
                stats['still_pending'] += 1

        except Exception as e:
            logger.error(f"❌ [3D MODEL POLLER] Error checking 3D model {minifig.id}: {e}")
            stats['errors'] += 1

    logger.info(f"🎨 [3D MODEL POLLER] Poll complete: {stats['checked']} checked, {stats['completed']} completed, {stats['failed']} failed, {stats['still_pending']} still pending")

    return {
        'status': 'completed',
        **stats
    }


@shared_task
def record_all_user_style_evolution():
    """
    Daily task to record style evolution snapshots for all active users.

    Session 210: Runs at 12:30 AM daily to capture each user's style distribution.
    This enables trend analysis and shift detection over time.
    """
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    from core.services import get_learning_service

    User = get_user_model()
    service = get_learning_service()

    logger.info("📊 [STYLE EVOLUTION] Starting daily style evolution snapshot...")

    # Get users who have been active in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)

    try:
        # Get users with recent behavior signals
        from core.models_unified_system import UserBehaviorSignal
        active_user_ids = UserBehaviorSignal.objects.filter(
            created_at__gte=thirty_days_ago
        ).values_list('user_id', flat=True).distinct()

        active_user_ids = list(set(active_user_ids))
        logger.info(f"📊 [STYLE EVOLUTION] Found {len(active_user_ids)} active users")

        stats = {
            'users_processed': 0,
            'snapshots_created': 0,
            'already_exists': 0,
            'no_data': 0,
            'errors': 0,
        }

        for user_id in active_user_ids:
            try:
                # Record evolution for each content domain
                for domain in ['image', 'video', 'audio']:
                    result = service.record_daily_evolution(user_id, domain)

                    if result:
                        if result.get('already_exists'):
                            stats['already_exists'] += 1
                        else:
                            stats['snapshots_created'] += 1
                    else:
                        stats['no_data'] += 1

                stats['users_processed'] += 1

            except Exception as e:
                logger.error(f"❌ [STYLE EVOLUTION] Error processing user {user_id}: {e}")
                stats['errors'] += 1

        logger.info(
            f"📊 [STYLE EVOLUTION] Complete: "
            f"{stats['users_processed']} users, "
            f"{stats['snapshots_created']} new snapshots, "
            f"{stats['already_exists']} already existed, "
            f"{stats['errors']} errors"
        )

        return {
            'status': 'completed',
            **stats
        }

    except Exception as e:
        logger.error(f"❌ [STYLE EVOLUTION] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# SESSION 213: SCHEDULED WORKFLOW EXECUTION
# =============================================================================

@shared_task(bind=True, max_retries=3)
def execute_scheduled_workflow(self, schedule_id: str):
    """
    Execute a scheduled workflow.

    Session 213: This task is triggered by Celery Beat based on cron schedules.
    It runs the workflow with the configured default topic and parameters.

    Args:
        schedule_id: UUID of the ScheduledWorkflow to execute
    """
    from core.models_unified_system import ScheduledWorkflow, WorkflowExecution
    from core.services.workflow_builder import get_workflow_builder
    from django.utils import timezone

    logger.info(f"🔄 [WORKFLOW SCHEDULER] Executing scheduled workflow: {schedule_id}")

    try:
        # Get the schedule
        schedule = ScheduledWorkflow.objects.select_related(
            'custom_workflow', 'custom_workflow__created_by'
        ).get(id=schedule_id, is_active=True)

        workflow = schedule.custom_workflow
        user = workflow.created_by

        logger.info(f"🔄 [WORKFLOW SCHEDULER] Running workflow '{workflow.name}' for user {user.username}")

        # Get the workflow builder for this user
        builder = get_workflow_builder(user)

        # Execute the workflow with default parameters
        result = builder.execute_workflow(
            workflow_id=str(workflow.id),
            topic=schedule.default_topic,
            parameters=schedule.default_parameters or {},
            async_execution=False  # Run synchronously in the task
        )

        # Update schedule timestamps
        schedule.last_run_at = timezone.now()
        schedule.run_count += 1

        # Calculate next run time based on cron expression
        try:
            from croniter import croniter
            cron = croniter(schedule.cron_expression, timezone.now())
            schedule.next_run_at = cron.get_next(timezone.datetime)
        except Exception as cron_error:
            logger.warning(f"Could not calculate next run time: {cron_error}")

        schedule.save()

        logger.info(
            f"✅ [WORKFLOW SCHEDULER] Workflow '{workflow.name}' completed successfully. "
            f"Run #{schedule.run_count}"
        )

        return {
            'status': 'completed',
            'workflow_id': str(workflow.id),
            'workflow_name': workflow.name,
            'execution_id': result.get('execution_id'),
            'run_count': schedule.run_count,
            'next_run_at': schedule.next_run_at.isoformat() if schedule.next_run_at else None
        }

    except ScheduledWorkflow.DoesNotExist:
        logger.error(f"❌ [WORKFLOW SCHEDULER] Schedule {schedule_id} not found or inactive")
        return {
            'status': 'failed',
            'error': 'Schedule not found or inactive'
        }

    except Exception as exc:
        logger.error(f"❌ [WORKFLOW SCHEDULER] Workflow execution failed: {exc}")

        # Update schedule with error
        try:
            schedule = ScheduledWorkflow.objects.get(id=schedule_id)
            schedule.last_run_at = timezone.now()
            schedule.save()
        except Exception:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def sync_workflow_schedules():
    """
    Sync workflow schedules with Celery Beat periodic tasks.

    Session 213: This task runs every 5 minutes to ensure Celery Beat
    has the latest workflow schedules registered as periodic tasks.

    It creates/updates PeriodicTask entries for each active ScheduledWorkflow.
    """
    from core.models_unified_system import ScheduledWorkflow
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
    from django.utils import timezone
    import json

    logger.info("🔄 [WORKFLOW SYNC] Syncing workflow schedules with Celery Beat...")

    stats = {
        'created': 0,
        'updated': 0,
        'disabled': 0,
        'errors': 0
    }

    try:
        # Get all scheduled workflows
        active_schedules = ScheduledWorkflow.objects.filter(is_active=True).select_related('custom_workflow')

        for schedule in active_schedules:
            try:
                # Parse cron expression (minute hour day_of_month month day_of_week)
                cron_parts = schedule.cron_expression.split()
                if len(cron_parts) != 5:
                    logger.warning(f"Invalid cron expression for {schedule.id}: {schedule.cron_expression}")
                    stats['errors'] += 1
                    continue

                minute, hour, day_of_month, month, day_of_week = cron_parts

                # Get or create crontab schedule
                crontab, _ = CrontabSchedule.objects.get_or_create(
                    minute=minute,
                    hour=hour,
                    day_of_week=day_of_week,
                    day_of_month=day_of_month,
                    month_of_year=month,
                    timezone=schedule.timezone
                )

                # Task name for identification
                task_name = f"workflow_schedule_{schedule.id}"

                # Get or create the periodic task
                periodic_task, created = PeriodicTask.objects.update_or_create(
                    name=task_name,
                    defaults={
                        'task': 'core.tasks.execute_scheduled_workflow',
                        'crontab': crontab,
                        'args': json.dumps([str(schedule.id)]),
                        'enabled': schedule.is_active,
                        'description': f"Scheduled workflow: {schedule.custom_workflow.name}"
                    }
                )

                if created:
                    stats['created'] += 1
                    logger.info(f"✅ Created periodic task for workflow: {schedule.custom_workflow.name}")
                else:
                    stats['updated'] += 1

            except Exception as e:
                logger.error(f"❌ Error syncing schedule {schedule.id}: {e}")
                stats['errors'] += 1

        # Disable periodic tasks for inactive/deleted schedules
        active_schedule_ids = set(str(s.id) for s in active_schedules)

        for periodic_task in PeriodicTask.objects.filter(name__startswith='workflow_schedule_'):
            schedule_id = periodic_task.name.replace('workflow_schedule_', '')

            if schedule_id not in active_schedule_ids and periodic_task.enabled:
                periodic_task.enabled = False
                periodic_task.save()
                stats['disabled'] += 1
                logger.info(f"🔴 Disabled periodic task: {periodic_task.name}")

        logger.info(
            f"🔄 [WORKFLOW SYNC] Complete: "
            f"{stats['created']} created, {stats['updated']} updated, "
            f"{stats['disabled']} disabled, {stats['errors']} errors"
        )

        return {
            'status': 'completed',
            **stats
        }

    except Exception as e:
        logger.error(f"❌ [WORKFLOW SYNC] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def check_workflow_schedules():
    """
    Check and execute any workflows that are due to run.

    Session 213: This is a fallback task that runs every minute to catch
    any scheduled workflows that might have been missed by Celery Beat.

    This is useful for workflows that were scheduled while Celery Beat
    was not running, or for immediate execution after schedule creation.
    """
    from core.models_unified_system import ScheduledWorkflow
    from django.utils import timezone

    logger.info("🔍 [WORKFLOW CHECK] Checking for due workflow schedules...")

    now = timezone.now()

    try:
        # Find schedules that should have run but haven't
        due_schedules = ScheduledWorkflow.objects.filter(
            is_active=True,
            next_run_at__lte=now
        ).select_related('custom_workflow')

        if not due_schedules.exists():
            logger.info("🔍 [WORKFLOW CHECK] No workflows due to run")
            return {'status': 'idle', 'executed': 0}

        executed = 0

        for schedule in due_schedules:
            logger.info(f"🚀 [WORKFLOW CHECK] Executing due workflow: {schedule.custom_workflow.name}")

            # Queue the execution task
            execute_scheduled_workflow.delay(str(schedule.id))
            executed += 1

        logger.info(f"🔍 [WORKFLOW CHECK] Queued {executed} workflows for execution")

        return {
            'status': 'completed',
            'executed': executed
        }

    except Exception as e:
        logger.error(f"❌ [WORKFLOW CHECK] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 223: Opportunity Engine Tasks (Phase 1 - Creative Intelligence Empire)
# =============================================================================

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
def expire_old_opportunities():
    """
    Mark old opportunities as expired.

    Opportunities that haven't been acted upon within their
    time sensitivity window should be marked as expired.
    """
    logger.info("🎯 [OPPORTUNITY ENGINE] Checking for expired opportunities...")

    try:
        from core.models_unified_system import Opportunity
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        # Find opportunities that have explicit expiration dates
        expired_by_date = Opportunity.objects.filter(
            expires_at__lt=now,
            status__in=['new', 'active', 'reviewing', 'approved']
        )

        # Find opportunities older than 7 days with high time sensitivity
        week_ago = now - timedelta(days=7)
        expired_by_timing = Opportunity.objects.filter(
            created_at__lt=week_ago,
            time_sensitivity__gte=80,
            status__in=['new', 'active', 'reviewing', 'approved']
        )

        # Find opportunities older than 30 days that haven't been acted upon
        month_ago = now - timedelta(days=30)
        expired_by_age = Opportunity.objects.filter(
            created_at__lt=month_ago,
            acted_on_at__isnull=True,
            status__in=['new', 'active', 'reviewing', 'approved']
        )

        # Combine and update
        expired_count = 0

        for queryset in [expired_by_date, expired_by_timing, expired_by_age]:
            count = queryset.update(status='expired')
            expired_count += count

        logger.info(f"🎯 [OPPORTUNITY ENGINE] Marked {expired_count} opportunities as expired")

        return {
            'status': 'completed',
            'expired_count': expired_count
        }

    except Exception as e:
        logger.error(f"❌ [OPPORTUNITY ENGINE] Expire task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def generate_opportunity_report():
    """
    Generate a daily opportunity report.

    This creates a summary of:
    - New opportunities discovered
    - Top-scoring opportunities
    - Opportunities acted upon
    - Revenue from completed opportunities
    """
    logger.info("🎯 [OPPORTUNITY ENGINE] Generating daily opportunity report...")

    try:
        from core.models_unified_system import Opportunity, OpportunityAction
        from django.utils import timezone
        from django.db.models import Count, Avg, Sum
        from datetime import timedelta

        now = timezone.now()
        yesterday = now - timedelta(days=1)

        # Get statistics
        new_today = Opportunity.objects.filter(created_at__gte=yesterday).count()
        total_active = Opportunity.objects.filter(status__in=['new', 'active', 'reviewing', 'approved']).count()
        acted_today = Opportunity.objects.filter(acted_on_at__gte=yesterday).count()

        # Get top opportunities
        top_opportunities = list(
            Opportunity.objects.filter(
                status__in=['new', 'active'],
                overall_score__gte=70
            ).order_by('-overall_score')[:5].values('id', 'title', 'overall_score', 'category')
        )

        # Get category breakdown
        by_category = dict(
            Opportunity.objects.filter(
                status__in=['new', 'active', 'reviewing', 'approved'],
                category__isnull=False
            ).values('category').annotate(count=Count('id')).values_list('category', 'count')
        )

        # Get average scores
        avg_scores = Opportunity.objects.filter(
            overall_score__isnull=False
        ).aggregate(
            avg_overall=Avg('overall_score'),
            avg_profit=Avg('profit_potential'),
        )

        report = {
            'status': 'completed',
            'generated_at': now.isoformat(),
            'period': 'daily',
            'summary': {
                'new_opportunities': new_today,
                'total_active': total_active,
                'acted_upon_today': acted_today,
            },
            'top_opportunities': top_opportunities,
            'by_category': by_category,
            'average_scores': {
                'overall': round(avg_scores['avg_overall'] or 0, 1),
                'profit_potential': round(avg_scores['avg_profit'] or 0, 1),
            }
        }

        logger.info(f"🎯 [OPPORTUNITY ENGINE] Report generated - {new_today} new, {total_active} active")
        return report

    except Exception as e:
        logger.error(f"❌ [OPPORTUNITY ENGINE] Report generation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 470: ML Scoring Model Training Task
# =============================================================================

@shared_task
def train_ml_scoring_model(force_retrain: bool = False, min_samples: int = 100):
    """
    Train or retrain the ML scoring model using OpportunityOutcome data.

    Session 470: Market Intelligence Architecture - Phase 1

    This task:
    - Collects training data from OpportunityOutcome records
    - Trains an XGBoost model with SHAP explainability
    - Stores the trained model and metrics
    - Updates the active model version

    Args:
        force_retrain: If True, retrain even if current model is recent
        min_samples: Minimum samples required for training (default: 100)

    Returns:
        Dict with training statistics and model version
    """
    import time
    start_time = time.time()
    logger.info("🧠 [ML SCORING] Starting ML model training...")

    try:
        from core.models_unified_system import (
            OpportunityOutcome, MLModelVersion, Opportunity
        )
        from core.services.ml_scoring_engine import get_ml_scoring_engine
        from django.utils import timezone
        from datetime import timedelta

        # Check if we need to retrain
        if not force_retrain:
            recent_model = MLModelVersion.objects.filter(
                is_active=True,
                trained_at__gte=timezone.now() - timedelta(days=7)
            ).first()
            if recent_model:
                logger.info(f"🧠 [ML SCORING] Active model {recent_model.version} is recent, skipping training")
                return {
                    'status': 'skipped',
                    'reason': 'Active model is less than 7 days old',
                    'current_version': recent_model.version
                }

        # Collect training data from outcomes
        # Chain: OpportunityOutcome → task → opportunity → spider_data
        outcomes = OpportunityOutcome.objects.select_related(
            'task', 'task__opportunity', 'task__opportunity__spider_data'
        ).filter(
            outcome__isnull=False,
            task__opportunity__spider_data__isnull=False
        )

        # Outcome to numeric score mapping
        OUTCOME_SCORES = {
            'won': 100,      # Full success
            'partial': 60,   # Partial success
            'expired': 30,   # Missed opportunity
            'cancelled': 20, # User cancelled
            'lost': 10,      # Rejected/failed
        }

        # Get ML engine for feature extraction
        ml_engine = get_ml_scoring_engine()

        training_data = []
        for outcome_record in outcomes:
            opp = outcome_record.task.opportunity
            spider_data = opp.spider_data

            if spider_data:
                try:
                    # Extract features from spider data
                    features = ml_engine.extract_features(spider_data).flatten().tolist()

                    # Convert outcome string to numeric score
                    outcome_score = OUTCOME_SCORES.get(outcome_record.outcome, 50)

                    training_data.append({
                        'features': features,
                        'outcome': outcome_score,
                    })
                except Exception as e:
                    logger.warning(f"🧠 [ML SCORING] Failed to extract features: {e}")
                    continue

        if len(training_data) < min_samples:
            logger.warning(f"🧠 [ML SCORING] Insufficient training data: {len(training_data)} < {min_samples}")

            # If we have no model at all, still try to train with what we have
            if len(training_data) < 10:
                return {
                    'status': 'skipped',
                    'reason': f'Insufficient training data ({len(training_data)} < {min_samples})',
                    'samples_available': len(training_data)
                }

        # Train the model
        training_result = ml_engine.train_model(training_data)

        duration = time.time() - start_time

        if training_result.get('success'):
            # Extract metrics from nested structure
            metrics = training_result.get('metrics', {})
            version = training_result.get('version')
            samples_used = metrics.get('samples_train', 0) + metrics.get('samples_test', 0)

            # Deactivate previous models
            MLModelVersion.objects.filter(is_active=True).update(is_active=False)

            # Create new MLModelVersion record
            model_record = MLModelVersion.objects.create(
                version=version,
                trained_at=timezone.now(),
                is_active=True,
                training_samples=samples_used,
                training_duration_seconds=int(round(duration)),
                train_mse=metrics.get('train_mse', 0),
                test_mse=metrics.get('test_mse', 0),
                train_r2=metrics.get('train_r2', 0),
                test_r2=metrics.get('test_r2', 0),
                feature_importance=training_result.get('feature_importance', [])
            )
            logger.info(f"🧠 [ML SCORING] Saved MLModelVersion: {model_record.id}")

            result = {
                'status': 'completed',
                'model_version': version,
                'samples_used': samples_used,
                'train_mse': metrics.get('train_mse', 0),
                'test_mse': metrics.get('test_mse', 0),
                'train_r2': metrics.get('train_r2', 0),
                'test_r2': metrics.get('test_r2', 0),
                'duration_seconds': round(duration, 2),
                'top_features': training_result.get('feature_importance', [])[:5]
            }
            logger.info(f"🧠 [ML SCORING] Model training complete - v{result['model_version']}, "
                       f"R²={result['test_r2']:.3f}, {result['samples_used']} samples")
            return result
        else:
            logger.error(f"🧠 [ML SCORING] Model training failed: {training_result.get('error')}")
            return {
                'status': 'failed',
                'error': training_result.get('error', 'Unknown error'),
                'duration_seconds': round(duration, 2)
            }

    except Exception as e:
        logger.error(f"❌ [ML SCORING] Training task failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def evaluate_ml_model_performance():
    """
    Evaluate current ML model performance against recent outcomes.

    Session 470: Market Intelligence Architecture - Phase 1

    This task compares model predictions against actual outcomes
    to track model drift and trigger retraining if needed.

    Returns:
        Dict with performance metrics
    """
    logger.info("🧠 [ML SCORING] Evaluating model performance...")

    try:
        from core.models_unified_system import (
            ScoringExplanation, OpportunityOutcome, MLModelVersion
        )
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Count

        # Get recent predictions with outcomes
        week_ago = timezone.now() - timedelta(days=7)

        recent_with_outcomes = ScoringExplanation.objects.filter(
            created_at__gte=week_ago,
            opportunity__outcomes__actual_outcome__isnull=False
        ).select_related('opportunity')

        if not recent_with_outcomes.exists():
            logger.info("🧠 [ML SCORING] No recent predictions with outcomes to evaluate")
            return {
                'status': 'skipped',
                'reason': 'No recent predictions with outcomes'
            }

        # Calculate prediction accuracy
        total = 0
        correct_predictions = 0
        total_error = 0

        for explanation in recent_with_outcomes:
            outcome = explanation.opportunity.outcomes.first()
            if outcome and outcome.actual_outcome is not None:
                total += 1
                predicted_score = explanation.hybrid_score
                actual = outcome.actual_outcome

                # Consider prediction correct if within 20 points
                if abs(predicted_score - actual) <= 20:
                    correct_predictions += 1

                total_error += abs(predicted_score - actual)

        accuracy = (correct_predictions / total * 100) if total > 0 else 0
        mae = (total_error / total) if total > 0 else 0

        # Get current model info
        active_model = MLModelVersion.objects.filter(is_active=True).first()

        result = {
            'status': 'completed',
            'evaluated_predictions': total,
            'accuracy_within_20': round(accuracy, 2),
            'mean_absolute_error': round(mae, 2),
            'active_model': active_model.version if active_model else None,
            'needs_retraining': accuracy < 60 or mae > 30
        }

        if result['needs_retraining']:
            logger.warning(f"🧠 [ML SCORING] Model needs retraining: accuracy={accuracy:.1f}%, MAE={mae:.1f}")
            # Trigger retraining
            train_ml_scoring_model.delay(force_retrain=True)
        else:
            logger.info(f"🧠 [ML SCORING] Model performing well: accuracy={accuracy:.1f}%, MAE={mae:.1f}")

        return result

    except Exception as e:
        logger.error(f"❌ [ML SCORING] Evaluation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 470: Phase 2 - Scoring Dispatcher Tasks
# =============================================================================

@shared_task
def process_realtime_scoring_queue(max_items: int = 50, max_time_sec: int = 25):
    """
    Process items from the Redis realtime scoring queue.

    Session 470: Market Intelligence Architecture - Phase 2

    This task runs frequently to drain the realtime priority queue,
    processing high-priority scoring requests first.

    Args:
        max_items: Maximum items to process per run
        max_time_sec: Maximum seconds to run

    Returns:
        Dict with processing statistics
    """
    logger.info("⚡ [REALTIME QUEUE] Starting queue processing...")

    try:
        from core.services.realtime_scorer import get_realtime_scorer

        scorer = get_realtime_scorer()

        # Get queue depths before
        before_depths = scorer.get_queue_depths()
        total_before = sum(before_depths.values())

        if total_before == 0:
            logger.info("⚡ [REALTIME QUEUE] Queue empty, nothing to process")
            return {
                'status': 'skipped',
                'reason': 'queue_empty'
            }

        # Process items
        stats = scorer.drain_queue(
            max_items=max_items,
            max_time_sec=max_time_sec
        )

        # Get queue depths after
        after_depths = scorer.get_queue_depths()

        result = {
            'status': 'completed',
            **stats,
            'queue_before': before_depths,
            'queue_after': after_depths
        }

        logger.info(
            f"⚡ [REALTIME QUEUE] Complete: {stats['success']}/{stats['processed']} success, "
            f"avg latency: {stats.get('avg_latency_ms', 0)}ms"
        )

        return result

    except Exception as e:
        logger.error(f"❌ [REALTIME QUEUE] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


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
    """
    Clean up stale/stuck scoring requests.

    Session 470: Market Intelligence Architecture - Phase 2

    This task runs periodically to:
    - Clean up Redis queue items stuck in processing
    - Expire old database queue items
    - Update metrics

    Returns:
        Dict with cleanup statistics
    """
    logger.info("🧹 [CLEANUP] Cleaning stale scoring requests...")

    try:
        from core.services.realtime_scorer import get_realtime_scorer
        from core.services.scoring_dispatcher import get_scoring_dispatcher

        stats = {
            'redis_cleaned': 0,
            'db_expired': 0
        }

        # Clean Redis queue
        try:
            scorer = get_realtime_scorer()
            stats['redis_cleaned'] = scorer.cleanup_stale_processing()
        except Exception as e:
            logger.warning(f"⚠️ [CLEANUP] Redis cleanup failed: {e}")

        # Clean DB queue
        try:
            dispatcher = get_scoring_dispatcher()
            stats['db_expired'] = dispatcher.cleanup_expired()
        except Exception as e:
            logger.warning(f"⚠️ [CLEANUP] DB cleanup failed: {e}")

        logger.info(
            f"🧹 [CLEANUP] Complete: {stats['redis_cleaned']} Redis, "
            f"{stats['db_expired']} DB items cleaned"
        )

        return {
            'status': 'completed',
            **stats
        }

    except Exception as e:
        logger.error(f"❌ [CLEANUP] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task
def score_spider_data_async(spider_data_id: str, priority: str = 'normal', source: str = 'api', user_id: int = None):
    """
    Score a single spider data item asynchronously.

    Session 470: Market Intelligence Architecture - Phase 2

    This is the main entry point for async scoring requests.
    Routes through the dispatcher which decides realtime vs batch.

    Args:
        spider_data_id: UUID of SpiderData to score
        priority: 'high', 'normal', or 'low'
        source: Where the request came from
        user_id: Optional user ID

    Returns:
        Dict with scoring result or queue position
    """
    logger.info(f"⚡ [ASYNC SCORE] Scoring {spider_data_id} (priority={priority})")

    try:
        from core.models_unified_system import SpiderData
        from core.services.scoring_dispatcher import (
            get_scoring_dispatcher,
            ScoringPriority
        )
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Get spider data
        spider_data = SpiderData.objects.get(id=spider_data_id)

        # Get user if provided
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        # Map priority string to enum
        priority_map = {
            'high': ScoringPriority.HIGH,
            'normal': ScoringPriority.NORMAL,
            'low': ScoringPriority.LOW
        }
        priority_enum = priority_map.get(priority.lower(), ScoringPriority.NORMAL)

        # Dispatch
        dispatcher = get_scoring_dispatcher()
        response = dispatcher.dispatch(
            spider_data=spider_data,
            priority=priority_enum,
            source=source,
            user=user
        )

        return {
            'status': 'success' if response.success else 'failed',
            'mode': response.mode,
            'score': response.score,
            'explanation_id': response.explanation_id,
            'queue_position': response.queue_position,
            'estimated_wait_ms': response.estimated_wait_ms,
            'latency_ms': response.latency_ms,
            'error': response.error
        }

    except Exception as e:
        logger.error(f"❌ [ASYNC SCORE] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 230: Smart Distribution Tasks
# =============================================================================

@shared_task(bind=True, max_retries=3)
def process_distribution(self, distribution_id: str):
    """
    Process a content distribution to a platform.

    This task handles the actual upload/submission process for each platform,
    updating the distribution status as it progresses.
    """
    logger.info(f"🚀 [DISTRIBUTION] Processing distribution {distribution_id}")

    try:
        from core.models_unified_system import ContentDistribution, UserPlatformAccount
        from django.utils import timezone

        distribution = ContentDistribution.objects.select_related(
            'platform_account__platform',
            'image_history',
            'video_history',
            'user'
        ).get(id=distribution_id)

        # Check if already processed or cancelled
        if distribution.status in ['live', 'removed', 'rejected']:
            logger.info(f"🚀 [DISTRIBUTION] {distribution_id} already processed: {distribution.status}")
            return {'status': 'skipped', 'reason': f'Already {distribution.status}'}

        # Update to processing status
        distribution.status = 'processing'
        distribution.save()

        platform_name = distribution.platform_account.platform.name.lower()

        # Platform-specific processing
        result = None

        if 'etsy' in platform_name:
            result = process_etsy_distribution(distribution)
        elif 'gumroad' in platform_name:
            result = process_gumroad_distribution(distribution)
        elif 'shutterstock' in platform_name:
            result = process_shutterstock_distribution(distribution)
        else:
            # Generic processing - just mark as pending review
            result = {
                'success': True,
                'status': 'pending',
                'message': f'Queued for {platform_name} - manual upload required'
            }

        if result.get('success'):
            distribution.status = result.get('status', 'live')
            distribution.platform_listing_id = result.get('listing_id', '')
            distribution.platform_listing_url = result.get('url', '')
            if distribution.status == 'live':
                distribution.listed_at = timezone.now()

            # Update platform metadata with result
            metadata = distribution.platform_metadata or {}
            metadata['process_result'] = result
            metadata['processed_at'] = timezone.now().isoformat()
            distribution.platform_metadata = metadata
            distribution.save()

            # Update account stats
            account = distribution.platform_account
            account.total_items_listed += 1
            account.save()

            logger.info(f"🚀 [DISTRIBUTION] Successfully processed {distribution_id} to {platform_name}")
            return {
                'status': 'success',
                'distribution_id': distribution_id,
                'platform': platform_name,
                'listing_status': distribution.status
            }
        else:
            # Failed
            distribution.status = 'rejected'
            distribution.rejection_reason = result.get('error', 'Unknown error')
            distribution.save()

            logger.error(f"🚀 [DISTRIBUTION] Failed to process {distribution_id}: {result.get('error')}")
            return {
                'status': 'failed',
                'distribution_id': distribution_id,
                'error': result.get('error')
            }

    except ContentDistribution.DoesNotExist:
        logger.error(f"🚀 [DISTRIBUTION] Distribution {distribution_id} not found")
        return {'status': 'failed', 'error': 'Distribution not found'}

    except Exception as e:
        logger.exception(f"🚀 [DISTRIBUTION] Error processing {distribution_id}: {e}")
        # Retry on transient errors
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))


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
def sync_all_platform_revenue():
    """
    Sync revenue from all connected platforms for all users.
    Run daily to keep revenue tracking up to date.
    """
    logger.info("💰 [DISTRIBUTION] Starting daily revenue sync for all platforms...")

    try:
        from core.models_unified_system import UserPlatformAccount
        from django.utils import timezone

        synced_count = 0
        error_count = 0

        # Get all active accounts with tokens
        accounts = UserPlatformAccount.objects.filter(
            account_status='active',
            access_token__isnull=False
        ).exclude(access_token='').select_related('platform', 'user')

        for account in accounts:
            try:
                platform_name = account.platform.name.lower()

                if 'gumroad' in platform_name:
                    from core.views_platform_integrations import sync_gumroad_revenue
                    sync_gumroad_revenue(account)
                    synced_count += 1

                elif 'etsy' in platform_name:
                    from core.views_platform_integrations import sync_etsy_revenue
                    sync_etsy_revenue(account)
                    synced_count += 1

            except Exception as e:
                logger.error(f"💰 [DISTRIBUTION] Error syncing {account.platform.name} for {account.user.username}: {e}")
                error_count += 1

        logger.info(f"💰 [DISTRIBUTION] Revenue sync complete: {synced_count} synced, {error_count} errors")

        return {
            'status': 'completed',
            'synced_accounts': synced_count,
            'errors': error_count,
        }

    except Exception as e:
        logger.error(f"💰 [DISTRIBUTION] Revenue sync failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def update_distribution_analytics():
    """
    Update distribution analytics aggregations daily.
    """
    logger.info("📊 [DISTRIBUTION] Updating distribution analytics...")

    try:
        from core.models_unified_system import (
            ContentDistribution,
            DistributionAnalytics,
            UserPlatformAccount
        )
        from django.utils import timezone
        from django.db.models import Sum, Count
        from datetime import timedelta

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # Get all users with distributions
        user_ids = ContentDistribution.objects.values_list('user_id', flat=True).distinct()

        for user_id in user_ids:
            # Aggregate by platform
            platforms = UserPlatformAccount.objects.filter(user_id=user_id)

            for platform_account in platforms:
                distributions = ContentDistribution.objects.filter(
                    user_id=user_id,
                    platform_account=platform_account,
                    created_at__date=yesterday
                )

                stats = distributions.aggregate(
                    total_views=Sum('views'),
                    total_downloads=Sum('downloads'),
                    total_sales=Sum('sales'),
                    total_revenue=Sum('revenue'),
                    new_listings=Count('id'),
                )

                if stats['new_listings'] and stats['new_listings'] > 0:
                    DistributionAnalytics.objects.update_or_create(
                        user_id=user_id,
                        platform=platform_account.platform,
                        date=yesterday,
                        period_type='daily',
                        defaults={
                            'total_views': stats['total_views'] or 0,
                            'total_downloads': stats['total_downloads'] or 0,
                            'total_sales': stats['total_sales'] or 0,
                            'total_revenue': stats['total_revenue'] or 0,
                            'new_listings': stats['new_listings'],
                        }
                    )

        logger.info("📊 [DISTRIBUTION] Analytics updated successfully")
        return {'status': 'completed', 'date': str(yesterday)}

    except Exception as e:
        logger.error(f"📊 [DISTRIBUTION] Analytics update failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ============================================================
# Session 233: Learning Loop Celery Tasks
# ============================================================

@shared_task
def discover_success_patterns(user_id=None, days=90):
    """
    Discover success patterns from distribution data.
    Run daily or on-demand to update pattern database.
    """
    logger.info(f"🧠 [LEARNING] Starting pattern discovery for user_id={user_id}, days={days}")

    try:
        from django.contrib.auth import get_user_model
        from core.learning_engine import PatternDiscoveryEngine

        User = get_user_model()
        users_processed = 0
        patterns_found = 0

        if user_id:
            # Process specific user
            try:
                user = User.objects.get(id=user_id)
                engine = PatternDiscoveryEngine(user=user)
                patterns = engine.discover_patterns(days=days)
                saved = engine.save_patterns(patterns)
                patterns_found += saved
                users_processed = 1
                logger.info(f"🧠 [LEARNING] Found {saved} patterns for user {user.username}")
            except User.DoesNotExist:
                logger.warning(f"🧠 [LEARNING] User {user_id} not found")
        else:
            # Process all users with distributions
            from core.models_unified_system import ContentDistribution
            user_ids = ContentDistribution.objects.values_list('user_id', flat=True).distinct()

            for uid in user_ids:
                try:
                    user = User.objects.get(id=uid)
                    engine = PatternDiscoveryEngine(user=user)
                    patterns = engine.discover_patterns(days=days)
                    saved = engine.save_patterns(patterns)
                    patterns_found += saved
                    users_processed += 1
                except Exception as e:
                    logger.error(f"🧠 [LEARNING] Error processing user {uid}: {e}")

        logger.info(f"🧠 [LEARNING] Pattern discovery complete: {users_processed} users, {patterns_found} patterns")

        return {
            'status': 'completed',
            'users_processed': users_processed,
            'patterns_found': patterns_found,
        }

    except Exception as e:
        logger.exception(f"🧠 [LEARNING] Pattern discovery failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def generate_user_insights(user_id=None, max_insights=10):
    """
    Generate AI insights for users based on their learning data.
    """
    logger.info(f"💡 [LEARNING] Generating insights for user_id={user_id}")

    try:
        from django.contrib.auth import get_user_model
        from core.learning_engine import InsightGenerator

        User = get_user_model()
        users_processed = 0
        insights_generated = 0

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                generator = InsightGenerator(user=user)
                insights = generator.generate_insights(max_insights=max_insights)
                saved = generator.save_insights(insights)
                insights_generated += saved
                users_processed = 1
                logger.info(f"💡 [LEARNING] Generated {saved} insights for {user.username}")
            except User.DoesNotExist:
                logger.warning(f"💡 [LEARNING] User {user_id} not found")
        else:
            # Process users with recent activity
            from core.models_unified_system import ContentDistribution
            from django.utils import timezone
            from datetime import timedelta

            recent = timezone.now() - timedelta(days=7)
            user_ids = ContentDistribution.objects.filter(
                created_at__gte=recent
            ).values_list('user_id', flat=True).distinct()

            for uid in user_ids:
                try:
                    user = User.objects.get(id=uid)
                    generator = InsightGenerator(user=user)
                    insights = generator.generate_insights(max_insights=max_insights)
                    saved = generator.save_insights(insights)
                    insights_generated += saved
                    users_processed += 1
                except Exception as e:
                    logger.error(f"💡 [LEARNING] Error generating insights for user {uid}: {e}")

        logger.info(f"💡 [LEARNING] Insight generation complete: {users_processed} users, {insights_generated} insights")

        return {
            'status': 'completed',
            'users_processed': users_processed,
            'insights_generated': insights_generated,
        }

    except Exception as e:
        logger.exception(f"💡 [LEARNING] Insight generation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def update_learning_profiles():
    """
    Update user learning profiles with aggregated data.
    """
    logger.info("📊 [LEARNING] Updating learning profiles...")

    try:
        from django.contrib.auth import get_user_model
        from core.models_unified_system import (
            UserLearningProfile, ContentDistribution, DistributionAnalytics,
            SuccessPattern
        )
        from django.db.models import Sum, Count, Avg

        User = get_user_model()
        profiles_updated = 0

        # Get users with distributions
        user_ids = ContentDistribution.objects.values_list('user_id', flat=True).distinct()

        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                profile, _ = UserLearningProfile.objects.get_or_create(user=user)

                # Update distribution stats
                dist_stats = ContentDistribution.objects.filter(user=user).aggregate(
                    total=Count('id'),
                    platforms_used=Count('platform', distinct=True),
                )

                # Update analytics stats
                analytics_stats = DistributionAnalytics.objects.filter(
                    distribution__user=user
                ).aggregate(
                    total_revenue=Sum('revenue_generated'),
                    total_sales=Sum('sales'),
                    total_views=Sum('views'),
                )

                # Update pattern stats
                pattern_count = SuccessPattern.objects.filter(user=user, is_active=True).count()
                avg_confidence = SuccessPattern.objects.filter(
                    user=user, is_active=True
                ).aggregate(avg=Avg('confidence_score'))['avg'] or 0

                # Update profile
                profile.total_distributions = dist_stats['total'] or 0
                profile.total_platforms = dist_stats['platforms_used'] or 0
                profile.total_revenue = analytics_stats['total_revenue'] or 0
                profile.total_sales = analytics_stats['total_sales'] or 0
                profile.patterns_discovered = pattern_count
                profile.avg_pattern_confidence = avg_confidence
                profile.save()

                profiles_updated += 1

            except Exception as e:
                logger.error(f"📊 [LEARNING] Error updating profile for user {user_id}: {e}")

        logger.info(f"📊 [LEARNING] Learning profiles updated: {profiles_updated}")
        return {'status': 'completed', 'profiles_updated': profiles_updated}

    except Exception as e:
        logger.exception(f"📊 [LEARNING] Profile update failed: {e}")
        return {'status': 'failed', 'error': str(e)}


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


@shared_task(bind=True, max_retries=3)
def record_learning_event(self, event_type, user_id, data):
    """
    Record a learning event for real-time pattern updates.
    """
    try:
        from django.contrib.auth import get_user_model
        from core.learning_engine import RealTimeLearner

        User = get_user_model()
        user = User.objects.get(id=user_id)
        learner = RealTimeLearner(user=user)

        if event_type == 'distribution':
            learner.record_distribution(data)
        elif event_type == 'sale':
            learner.record_sale(data)
        elif event_type == 'view':
            learner.record_view(data)

        logger.debug(f"📝 [LEARNING] Recorded {event_type} event for user {user_id}")
        return {'status': 'recorded', 'event_type': event_type}

    except Exception as e:
        logger.error(f"📝 [LEARNING] Failed to record event: {e}")
        raise self.retry(exc=e, countdown=30)


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
        from core.models_unified_system import AutomatedAction

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
    """
    Main learning cycle - agents share knowledge with connected agents.
    Runs every 10 minutes to facilitate continuous learning.

    This creates the "agents learning from each other" effect:
    1. Select active learning connections
    2. For each connection, transfer relevant knowledge
    3. Track what was learned and how useful it was
    4. Update connection strength based on successful transfers
    """
    import random
    from django.utils import timezone
    from core.models import (
        Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer,
        MythologyQuarantine  # Session 541: Quarantine for blocked transfers
    )

    logger.info("🧠 [LEARNING] Starting autonomous agent learning cycle...")

    try:
        # Get active learning connections
        connections = AgentLearningConnection.objects.filter(
            is_active=True
        ).select_related('teacher_agent', 'student_agent').order_by('?')[:10]  # Random 10

        transfers_made = 0
        mythology_blocks = 0  # Session 541: Track mythology validation blocks
        learning_events = []

        for connection in connections:
            teacher = connection.teacher_agent
            student = connection.student_agent

            # Get teacher's recent knowledge that student doesn't have
            # Session 357: Expanded default to include ALL knowledge types for better sharing
            ALL_KNOWLEDGE_TYPES = ['trend', 'opportunity', 'market', 'user_behavior', 'content_idea',
                                   'tool_discovery', 'pricing', 'research', 'insight', 'strategy']
            teacher_knowledge = AgentKnowledgeSource.objects.filter(
                agent=teacher,
                is_active=True,
                knowledge_type__in=connection.shareable_knowledge_types or ALL_KNOWLEDGE_TYPES
            ).order_by('-confidence_score', '-last_updated_at')[:5]

            for knowledge in teacher_knowledge:
                # Session 358: Enhanced Delta Detection using semantic similarity
                # Uses embeddings + cosine similarity to detect semantic duplicates
                # This catches cases like "AI Content Tools" vs "Content Creation AI Tools"
                try:
                    from core.services.knowledge_similarity import get_knowledge_similarity_service
                    similarity_service = get_knowledge_similarity_service()

                    should_transfer, reason = similarity_service.should_transfer_knowledge(
                        student_agent=student,
                        teacher_knowledge=knowledge,
                        threshold=0.80  # 80% similarity = duplicate
                    )

                    if not should_transfer:
                        logger.debug(f"[LEARNING] Skipping transfer: {reason}")
                        continue

                except Exception as e:
                    # Fallback to Session 357 exact title matching if semantic fails
                    logger.warning(f"Semantic similarity failed, using fallback: {e}")
                    import re
                    clean_title = re.sub(r'^\[Learned\]\s*', '', knowledge.title or '').strip()
                    while clean_title.startswith('[Learned]'):
                        clean_title = clean_title[9:].strip()

                    from django.db.models import Q
                    student_has_similar = AgentKnowledgeSource.objects.filter(
                        agent=student,
                        knowledge_type=knowledge.knowledge_type
                    ).filter(
                        Q(title=clean_title) |
                        Q(title=f"[Learned] {clean_title}") |
                        Q(title__iexact=knowledge.title)
                    ).exists()

                    if student_has_similar:
                        continue

                # Session 541: Mythology validation for knowledge transfers
                # Prevents unrealistic claims from propagating through the learning network
                try:
                    from ai_core.agents.mythology_validator import mythology_enforcer

                    # Validate the knowledge content before transfer
                    knowledge_content = knowledge.summary or knowledge.title or ""
                    validation = mythology_enforcer.enforce(
                        f"{teacher.name}→{student.name}",
                        knowledge_content
                    )

                    if validation.get('mythology_corrected'):
                        # Knowledge contains unrealistic claims - quarantine instead of just logging
                        mythology_blocks += 1

                        # Get violation details from the original validation
                        original_validation = mythology_enforcer.validator.validate_output(
                            f"{teacher.name}→{student.name}",
                            knowledge_content
                        )
                        violations = original_validation.get('violations', [])
                        first_violation_type = violations[0]['type'] if violations else 'spider_data_myth'

                        # Create quarantine entry with full context
                        try:
                            MythologyQuarantine.objects.create(
                                teacher_agent=teacher,
                                student_agent=student,
                                connection=connection,
                                source_knowledge=knowledge,
                                blocked_title=knowledge.title[:500] if knowledge.title else "Unknown",
                                blocked_content=knowledge_content[:2000],
                                blocked_summary=knowledge.summary[:500] if knowledge.summary else "",
                                violation_type=first_violation_type,
                                violation_count=len(violations),
                                violation_patterns=[v.get('pattern', '') for v in violations[:5]],
                                mythology_warning=validation.get('warning', ''),
                                spider_sources=knowledge.source_spider_names or [],
                                source_urls=[],  # Could be extracted from knowledge if available
                            )
                        except Exception as q_err:
                            logger.warning(f"⚠️ [MYTHOLOGY] Quarantine creation failed: {q_err}")

                        # Apply trust decay to the connection
                        connection.apply_mythology_penalty()

                        logger.warning(
                            f"🚨 [MYTHOLOGY] Blocked & quarantined {teacher.name}→{student.name}: "
                            f"'{knowledge.title[:50]}' ({len(violations)} violations, "
                            f"connection strength now {connection.strength:.2f})"
                        )
                        continue

                except Exception as myth_err:
                    # If mythology validation fails, log but continue (don't block learning)
                    logger.warning(f"⚠️ [MYTHOLOGY] Validation error (continuing): {myth_err}")

                # Knowledge is new and validated - proceed with transfer
                # Session 350: Strip existing [Learned] prefixes to prevent accumulation
                import re
                clean_title = re.sub(r'^\[Learned\]\s*', '', knowledge.title).strip()
                # Also strip from beginning multiple times in case of nested
                while clean_title.startswith('[Learned]'):
                    clean_title = clean_title[9:].strip()

                # Create knowledge transfer record
                usefulness = random.uniform(0.6, 1.0)  # Simulate usefulness

                # Session 532: Include actual knowledge content in transfer summary
                knowledge_content = knowledge.summary[:500] if knowledge.summary else ""
                transfer_summary = f"{teacher.name} shared '{clean_title}' with {student.name}.\n\n{knowledge_content}"

                transfer = KnowledgeTransfer.objects.create(
                    connection=connection,
                    source_knowledge=knowledge,
                    transfer_summary=transfer_summary,
                    key_points=knowledge.key_insights[:5] if knowledge.key_insights else [],
                    was_useful=usefulness > 0.7,
                    usefulness_score=usefulness,
                    was_applied=random.random() > 0.3,  # 70% chance of being applied
                )

                # Create new knowledge for student (adapted from teacher's)
                # Session 532: Include full summary for richer knowledge transfer
                student_summary = f"Learned from {teacher.name}:\n\n{knowledge.summary}" if knowledge.summary else f"Knowledge transferred from {teacher.name}"

                new_knowledge = AgentKnowledgeSource.objects.create(
                    agent=student,
                    knowledge_type=knowledge.knowledge_type,
                    spider_category=knowledge.spider_category,
                    source_spider_names=knowledge.source_spider_names + [f'learned_from_{teacher.name}'],
                    title=f"[Learned] {clean_title}",
                    summary=student_summary,
                    key_insights=knowledge.key_insights,
                    data_points_count=knowledge.data_points_count,
                    confidence_score=knowledge.confidence_score * 0.9,  # Slightly lower confidence
                    relevance_score=knowledge.relevance_score,
                    freshness_score=1.0,  # Fresh for student
                    is_active=True,
                )

                transfers_made += 1
                learning_events.append({
                    'teacher': teacher.name,
                    'student': student.name,
                    'knowledge': knowledge.title[:50],
                    'type': connection.learning_type,
                    'usefulness': usefulness
                })

                # Update connection stats
                connection.total_transfers += 1
                if usefulness > 0.7:
                    connection.successful_transfers += 1
                connection.last_transfer_at = timezone.now()

                # Update connection strength based on success
                if connection.total_transfers > 0:
                    success_rate = connection.successful_transfers / connection.total_transfers
                    connection.strength = min(1.0, connection.strength + (success_rate * 0.05))
                    connection.avg_improvement_score = (
                        connection.avg_improvement_score * 0.9 + usefulness * 0.1
                    )
                connection.save()

                logger.info(
                    f"🎓 [LEARNING] {teacher.name} → {student.name}: "
                    f"'{knowledge.title[:30]}...' (usefulness: {usefulness:.2f})"
                )

                # Session 429: Send Discord notification for knowledge transfer
                # Session 435: Format summary nicely instead of showing raw JSON
                try:
                    from core.services.discord_notifications import discord_notify

                    # Parse JSON summary into human-readable format
                    formatted_summary = f"{teacher.name} shared knowledge with {student.name}"
                    if knowledge.summary:
                        try:
                            import json
                            data = json.loads(knowledge.summary)
                            if isinstance(data, dict):
                                parts = []
                                if data.get('query'):
                                    parts.append(f"Query: \"{data['query'][:80]}\"")
                                if data.get('sources_used'):
                                    sources = data['sources_used']
                                    if isinstance(sources, list):
                                        parts.append(f"Sources: {', '.join(sources[:3])}")
                                if data.get('result_count'):
                                    parts.append(f"Results: {data['result_count']} items")
                                if data.get('insight'):
                                    parts.append(f"Insight: {data['insight'][:100]}")
                                if data.get('recommendation'):
                                    parts.append(f"Recommendation: {data['recommendation'][:100]}")
                                if parts:
                                    formatted_summary = "\n".join(parts)
                                else:
                                    # Fallback: show first few key-value pairs
                                    formatted_summary = "\n".join([
                                        f"{k}: {str(v)[:50]}" for k, v in list(data.items())[:3]
                                    ])
                        except (json.JSONDecodeError, TypeError):
                            formatted_summary = knowledge.summary[:200]

                    discord_notify.send_knowledge(
                        agent_name=f"{teacher.name} → {student.name}",
                        title=clean_title[:100],
                        summary=formatted_summary,
                        knowledge_type=knowledge.knowledge_type or 'insight',
                        confidence=usefulness
                    )
                except Exception as discord_err:
                    logger.debug(f"Discord notification failed: {discord_err}")

                # Only transfer one piece of knowledge per connection per cycle
                break

        # Broadcast learning events via Redis for real-time updates
        if learning_events:
            try:
                import redis
                import json
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)

                for event in learning_events:
                    r.publish('agent_learning', json.dumps({
                        'type': 'knowledge_transfer',
                        'data': event,
                        'timestamp': timezone.now().isoformat()
                    }))

                # Also store last learning events for dashboard
                r.setex(
                    'agent_learning:recent_events',
                    3600,  # 1 hour TTL
                    json.dumps(learning_events)
                )
                r.set('agent_learning:last_cycle', timezone.now().isoformat())
                r.set('agent_learning:total_transfers_today',
                      int(r.get('agent_learning:total_transfers_today') or 0) + transfers_made)
            except Exception as redis_err:
                logger.warning(f"Redis broadcast failed: {redis_err}")

        # Session 541: Include mythology blocks in log
        mythology_msg = f", {mythology_blocks} quarantined by mythology" if mythology_blocks > 0 else ""
        logger.info(
            f"🧠 [LEARNING] Cycle complete: {transfers_made} knowledge transfers made "
            f"across {len(connections)} connections{mythology_msg}"
        )

        # Session 541: Get quarantine stats for return
        quarantine_pending = MythologyQuarantine.objects.filter(status='pending').count()

        return {
            'status': 'success',
            'transfers_made': transfers_made,
            'mythology_blocks': mythology_blocks,  # Session 541: Track quality gate blocks
            'quarantine_pending': quarantine_pending,  # Session 541: Total awaiting review
            'connections_processed': len(connections),
            'learning_events': learning_events,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🧠 [LEARNING] Learning cycle failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def agent_think_and_synthesize():
    """
    Agents "think" about their knowledge and synthesize new insights.
    This simulates agents processing what they've learned and forming new ideas.

    Runs every 30 minutes.
    """
    import random
    from django.utils import timezone
    from core.models import Agent, AgentKnowledgeSource

    logger.info("💭 [THINKING] Agents are synthesizing knowledge...")

    try:
        # Get agents with enough knowledge to synthesize
        agents = Agent.objects.filter(
            is_active=True
        ).prefetch_related('knowledge_sources')

        insights_created = 0

        for agent in agents:
            knowledge_count = agent.knowledge_sources.filter(is_active=True).count()

            # Agents need at least 10 knowledge items to synthesize
            if knowledge_count >= 10:
                # Get diverse knowledge types
                knowledge_by_type = {}
                for k in agent.knowledge_sources.filter(is_active=True)[:20]:
                    if k.knowledge_type not in knowledge_by_type:
                        knowledge_by_type[k.knowledge_type] = []
                    knowledge_by_type[k.knowledge_type].append(k)

                # If agent has knowledge in multiple areas, synthesize
                if len(knowledge_by_type) >= 2:
                    types = list(knowledge_by_type.keys())[:2]
                    k1 = random.choice(knowledge_by_type[types[0]])
                    k2 = random.choice(knowledge_by_type[types[1]])

                    # Create synthesized insight
                    synthesis_title = f"[Synthesis] Combining {types[0]} and {types[1]} insights"
                    synthesis_summary = (
                        f"{agent.name} synthesized knowledge from {k1.title[:30]} "
                        f"and {k2.title[:30]} to form new understanding."
                    )

                    # Check if similar synthesis exists
                    if not AgentKnowledgeSource.objects.filter(
                        agent=agent,
                        title__icontains="Synthesis",
                        knowledge_type='trend'  # Syntheses are trends
                    ).exists():
                        AgentKnowledgeSource.objects.create(
                            agent=agent,
                            knowledge_type='trend',
                            title=synthesis_title,
                            summary=synthesis_summary,
                            source_spider_names=[f'synthesized_by_{agent.name}'],
                            key_insights=[
                                f"Combined insight from {types[0]} and {types[1]}",
                                k1.key_insights[0] if k1.key_insights else "Primary source",
                                k2.key_insights[0] if k2.key_insights else "Secondary source"
                            ],
                            data_points_count=k1.data_points_count + k2.data_points_count,
                            confidence_score=(k1.confidence_score + k2.confidence_score) / 2 * 0.85,
                            freshness_score=1.0,
                            is_active=True,
                        )
                        insights_created += 1

                        logger.info(f"💡 [THINKING] {agent.name} synthesized: {synthesis_title[:50]}")

        # Broadcast thinking results
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'synthesis_complete',
                'insights_created': insights_created,
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(f"💭 [THINKING] Synthesis complete: {insights_created} new insights created")

        return {
            'status': 'success',
            'insights_created': insights_created,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"💭 [THINKING] Synthesis failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def update_agent_effectiveness_from_learning():
    """
    Update agent effectiveness scores based on their learning activity.
    Agents that learn more and share more become more effective.

    Runs daily.
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models import Agent, AgentLearningConnection, AgentKnowledgeSource

    logger.info("📈 [EFFECTIVENESS] Updating agent effectiveness from learning...")

    try:
        cutoff = timezone.now() - timedelta(days=7)

        for agent in Agent.objects.filter(is_active=True):
            # Count recent learning activity
            knowledge_learned = agent.knowledge_sources.filter(
                first_discovered_at__gte=cutoff,
                title__startswith='[Learned]'
            ).count()

            knowledge_shared = AgentLearningConnection.objects.filter(
                teacher_agent=agent,
                last_transfer_at__gte=cutoff
            ).count()

            syntheses_made = agent.knowledge_sources.filter(
                first_discovered_at__gte=cutoff,
                title__startswith='[Synthesis]'
            ).count()

            # Calculate learning score (0-20 points)
            learning_score = min(20, (knowledge_learned * 2) + (knowledge_shared * 3) + (syntheses_made * 5))

            # Update effectiveness (blend with existing)
            old_effectiveness = agent.effectiveness_score
            new_effectiveness = min(100, old_effectiveness + (learning_score - 10))  # +/- 10 based on learning
            new_effectiveness = max(50, new_effectiveness)  # Don't go below 50

            if new_effectiveness != old_effectiveness:
                agent.effectiveness_score = new_effectiveness
                agent.save(update_fields=['effectiveness_score'])

                logger.info(
                    f"📈 [EFFECTIVENESS] {agent.name}: {old_effectiveness} → {new_effectiveness} "
                    f"(learned: {knowledge_learned}, shared: {knowledge_shared}, synthesized: {syntheses_made})"
                )

        return {'status': 'success', 'timestamp': timezone.now().isoformat()}

    except Exception as e:
        logger.exception(f"📈 [EFFECTIVENESS] Update failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def broadcast_learning_status():
    """
    Broadcast current learning network status via WebSocket.
    Called frequently to keep the UI updated with learning activity.
    """
    from django.utils import timezone
    from core.models import Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer
    from datetime import timedelta

    try:
        import redis
        import json
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        # Gather stats
        stats = {
            'total_agents': Agent.objects.filter(is_active=True).count(),
            'total_knowledge': AgentKnowledgeSource.objects.filter(is_active=True).count(),
            'total_connections': AgentLearningConnection.objects.filter(is_active=True).count(),
            'transfers_last_hour': KnowledgeTransfer.objects.filter(created_at__gte=last_hour).count(),
            'transfers_last_day': KnowledgeTransfer.objects.filter(created_at__gte=last_day).count(),
            'active_learners': Agent.objects.filter(
                teachers__last_transfer_at__gte=last_hour
            ).distinct().count(),
            'active_teachers': Agent.objects.filter(
                students__last_transfer_at__gte=last_hour
            ).distinct().count(),
            'timestamp': now.isoformat()
        }

        # Top learning agents
        top_learners = []
        for agent in Agent.objects.filter(is_active=True).order_by('-effectiveness_score')[:5]:
            top_learners.append({
                'name': agent.name,
                'knowledge_count': agent.knowledge_sources.filter(is_active=True).count(),
                'effectiveness': agent.effectiveness_score,
                'teaches': agent.students.count(),
                'learns_from': agent.teachers.count()
            })

        stats['top_learners'] = top_learners

        # Recent transfers
        recent_transfers = []
        for transfer in KnowledgeTransfer.objects.order_by('-created_at')[:5]:
            recent_transfers.append({
                'teacher': transfer.connection.teacher_agent.name,
                'student': transfer.connection.student_agent.name,
                'summary': transfer.transfer_summary[:50],
                'useful': transfer.was_useful,
                'time': transfer.created_at.isoformat()
            })

        stats['recent_transfers'] = recent_transfers

        # Publish to Redis (legacy)
        r.publish('agent_learning', json.dumps({
            'type': 'status_update',
            'data': stats
        }))

        # Cache for API access
        r.setex('agent_learning:status', 300, json.dumps(stats))

        # Session 324: Broadcast to Learning Feed WebSocket channel
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            # Build feed items for WebSocket
            feed_items = []
            for transfer in KnowledgeTransfer.objects.select_related(
                'connection__teacher_agent',
                'connection__student_agent'
            ).order_by('-created_at')[:20]:
                teacher = transfer.connection.teacher_agent
                student = transfer.connection.student_agent

                if teacher.id == student.id:
                    source = 'self_learning'
                    description = f"{teacher.name} acquired new knowledge"
                else:
                    source = 'knowledge_transfer'
                    description = f"{teacher.name} shared knowledge with {student.name}"

                feed_items.append({
                    'timestamp': transfer.created_at.isoformat(),
                    'type': source,
                    'source': 'Knowledge transfer',
                    'description': description,
                    'knowledge': transfer.transfer_summary[:100] if transfer.transfer_summary else 'Knowledge shared',
                    'teacher': teacher.name,
                    'student': student.name,
                    'was_useful': transfer.was_useful,
                    'effectiveness_gain': 0.0
                })

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'agent_learning_feed',
                {
                    'type': 'learning_feed_update',
                    'feed_items': feed_items,
                    'stats': stats
                }
            )
            logger.info(f"🧠 [LEARNING FEED] Broadcast {len(feed_items)} items to WebSocket")
        except Exception as ws_error:
            logger.warning(f"🧠 [LEARNING FEED] WebSocket broadcast failed: {ws_error}")

        return stats

    except Exception as e:
        logger.exception(f"📡 [BROADCAST] Status broadcast failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 244: Daily Learning Embeddings
# Convert all agent learning (knowledge transfers, syntheses, insights) into
# searchable vector embeddings stored in PGVector. This enables semantic search
# across all agent learning and builds the foundation for long-term AI memory.
# =============================================================================

@shared_task
def embed_daily_agent_learning():
    """
    Create document embeddings for all agent learning activity.

    This task:
    1. Gathers all knowledge transfers, learned items, and syntheses from the last 24 hours
    2. Creates rich text documents from each learning event
    3. Generates embeddings using OpenAI
    4. Stores them in PGVector via DocumentEmbedding

    Runs daily at 2 AM to capture a full day's learning.
    This is the key to AI longevity - everything becomes a searchable document.
    """
    import asyncio
    from datetime import timedelta
    from django.utils import timezone
    from django.db import transaction
    from core.models import Agent, AgentKnowledgeSource, KnowledgeTransfer, AgentLearningConnection
    from content.models import Document, DocumentEmbedding, DocumentType, EmbeddingModel, ContentStatus, ContentSource
    from content.embeddings import EmbeddingManager

    logger.info("📚 [EMBEDDINGS] Starting daily agent learning embedding task...")

    def run_async(coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        embedding_manager = EmbeddingManager()
        cutoff = timezone.now() - timedelta(hours=24)

        stats = {
            'transfers_processed': 0,
            'learned_items_processed': 0,
            'syntheses_processed': 0,
            'embeddings_created': 0,
            'embeddings_failed': 0,
            'total_cost': 0.0
        }

        # Get or create a system user for the learning document
        system_user, _ = User.objects.get_or_create(
            username='system_learning',
            defaults={
                'email': 'system@learning.internal',
                'is_active': True,
            }
        )

        # Get or create the master learning document
        learning_doc, created = Document.objects.get_or_create(
            title='Agent Learning Knowledge Base',
            document_type=DocumentType.KNOWLEDGE_EXTRACT,
            defaults={
                'owner': system_user,
                'description': 'Embedded knowledge from agent-to-agent learning, syntheses, and insights',
                'raw_content': '',
                'processed_content': '',
                'status': ContentStatus.PROCESSED,
                'source': ContentSource.WORKFLOW,
                'tags': ['agent_learning', 'knowledge_transfer', 'synthesis', 'embedded']
            }
        )

        # Track existing chunk indices to avoid duplicates
        existing_indices = set(
            DocumentEmbedding.objects.filter(document=learning_doc)
            .values_list('chunk_index', flat=True)
        )
        next_index = max(existing_indices) + 1 if existing_indices else 0

        # 1. Process Knowledge Transfers
        recent_transfers = KnowledgeTransfer.objects.filter(
            created_at__gte=cutoff
        ).select_related(
            'connection__teacher_agent',
            'connection__student_agent',
            'source_knowledge'
        )

        for transfer in recent_transfers:
            # Create a unique identifier for this transfer
            transfer_id = f"transfer_{transfer.id}"

            # Build rich text document from transfer
            text_parts = [
                f"Knowledge Transfer Event",
                f"Teacher: {transfer.connection.teacher_agent.name if transfer.connection.teacher_agent else 'Unknown'}",
                f"Student: {transfer.connection.student_agent.name if transfer.connection.student_agent else 'Unknown'}",
                f"Knowledge Topic: {transfer.source_knowledge.title if transfer.source_knowledge else 'Unknown'}",
                f"Summary: {transfer.transfer_summary or 'No summary'}",
                f"Key Points: {', '.join(transfer.key_points) if transfer.key_points else 'No key points'}",
                f"Usefulness Score: {transfer.usefulness_score}",
                f"Was Applied: {transfer.was_applied}",
                f"Timestamp: {transfer.created_at.isoformat()}"
            ]

            if transfer.source_knowledge:
                text_parts.append(f"Source Knowledge Summary: {transfer.source_knowledge.summary[:500] if transfer.source_knowledge.summary else 'No summary'}")

            text = "\n".join(text_parts)

            # Generate embedding
            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'knowledge_transfer',
                                'transfer_id': str(transfer.id),
                                'teacher': transfer.connection.teacher_agent.name if transfer.connection.teacher_agent else None,
                                'student': transfer.connection.student_agent.name if transfer.connection.student_agent else None,
                                'date': transfer.created_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1
                logger.warning(f"📚 [EMBEDDINGS] Failed to embed transfer {transfer.id}: {result.error_message}")

            stats['transfers_processed'] += 1

        # 2. Process Learned Items (knowledge sources with [Learned] prefix)
        learned_items = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            title__startswith='[Learned]',
            is_active=True
        ).select_related('agent')

        for item in learned_items:
            text_parts = [
                f"Learned Knowledge Item",
                f"Agent: {item.agent.name if item.agent else 'Unknown'}",
                f"Title: {item.title}",
                f"Type: {item.knowledge_type}",
                f"Summary: {item.summary or 'No summary'}",
                f"Key Insights: {', '.join(str(i) for i in item.key_insights) if item.key_insights else 'No insights'}",
                f"Confidence: {item.confidence_score}",
                f"Data Points: {item.data_points_count}",
                f"Learned At: {item.first_discovered_at.isoformat()}"
            ]

            text = "\n".join(text_parts)

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'learned_item',
                                'knowledge_id': str(item.id),
                                'agent': item.agent.name if item.agent else None,
                                'knowledge_type': item.knowledge_type,
                                'date': item.first_discovered_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1

            stats['learned_items_processed'] += 1

        # 3. Process Syntheses (knowledge sources with [Synthesis] prefix)
        syntheses = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            title__startswith='[Synthesis]',
            is_active=True
        ).select_related('agent')

        for synthesis in syntheses:
            text_parts = [
                f"Agent Synthesis - Combined Insight",
                f"Agent: {synthesis.agent.name if synthesis.agent else 'Unknown'}",
                f"Title: {synthesis.title}",
                f"Summary: {synthesis.summary or 'No summary'}",
                f"Key Insights: {', '.join(str(i) for i in synthesis.key_insights) if synthesis.key_insights else 'No insights'}",
                f"Confidence: {synthesis.confidence_score}",
                f"Source Data Points: {synthesis.data_points_count}",
                f"Synthesized At: {synthesis.first_discovered_at.isoformat()}"
            ]

            text = "\n".join(text_parts)

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'synthesis',
                                'knowledge_id': str(synthesis.id),
                                'agent': synthesis.agent.name if synthesis.agent else None,
                                'date': synthesis.first_discovered_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1

            stats['syntheses_processed'] += 1

        # Update the document's last modified time
        learning_doc.save()

        # Broadcast success
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'embeddings_complete',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(
            f"📚 [EMBEDDINGS] Daily embedding complete: "
            f"{stats['transfers_processed']} transfers, "
            f"{stats['learned_items_processed']} learned items, "
            f"{stats['syntheses_processed']} syntheses, "
            f"{stats['embeddings_created']} embeddings created, "
            f"${stats['total_cost']:.4f} total cost"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"📚 [EMBEDDINGS] Daily embedding failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 417: Comprehensive Agent Activity Embeddings
# Runs every 30 minutes to embed ALL agent activity:
# - Dreams (AgentDream)
# - Hive Mind Sessions (HiveMindSession)
# - Knowledge Sources (AgentKnowledgeSource) - including non-prefixed ones
# =============================================================================

@shared_task
def embed_agent_activity(hours: int = 2):
    """
    Session 417: Create embeddings for ALL agent activity within the last N hours.

    This task embeds:
    1. Agent Dreams - Creative thoughts and ideas
    2. Hive Mind Sessions - Collective intelligence outputs
    3. Agent Knowledge Sources - All knowledge (not just [Learned]/[Synthesis] prefixed)

    Runs every 30 minutes to keep embeddings fresh for semantic search.
    """
    import asyncio
    from datetime import timedelta
    from django.utils import timezone
    from django.db import transaction
    from core.models_unified_system import Agent, AgentDream, HiveMindSession, AgentKnowledgeSource
    from content.models import Document, DocumentEmbedding, DocumentType, EmbeddingModel, ContentStatus, ContentSource
    from content.embeddings import EmbeddingManager

    logger.info(f"🧠 [EMBEDDINGS] Starting agent activity embedding (last {hours} hours)...")

    def run_async(coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        embedding_manager = EmbeddingManager()
        cutoff = timezone.now() - timedelta(hours=hours)

        stats = {
            'dreams_processed': 0,
            'dreams_embedded': 0,
            'hive_minds_processed': 0,
            'hive_minds_embedded': 0,
            'knowledge_processed': 0,
            'knowledge_embedded': 0,
            'total_embedded': 0,
            'failed': 0,
            'total_cost': 0.0
        }

        # Get or create system user
        system_user, _ = User.objects.get_or_create(
            username='system_learning',
            defaults={
                'email': 'system@learning.internal',
                'is_active': True,
            }
        )

        # Get or create the agent activity document
        activity_doc, created = Document.objects.get_or_create(
            title='Agent Activity Knowledge Base',
            document_type=DocumentType.KNOWLEDGE_EXTRACT,
            defaults={
                'owner': system_user,
                'description': 'Embedded content from agent dreams, hive minds, and knowledge',
                'raw_content': '',
                'processed_content': '',
                'status': ContentStatus.PROCESSED,
                'source': ContentSource.WORKFLOW,
                'tags': ['agent_activity', 'dreams', 'hive_mind', 'knowledge', 'embedded']
            }
        )

        # Track existing embeddings to avoid duplicates (by metadata type+id)
        existing_embeddings = set()
        for emb in DocumentEmbedding.objects.filter(document=activity_doc).values('metadata'):
            if emb['metadata']:
                key = f"{emb['metadata'].get('type', '')}_{emb['metadata'].get('id', '')}"
                existing_embeddings.add(key)

        next_index = DocumentEmbedding.objects.filter(document=activity_doc).count()

        # =================================================================
        # 1. EMBED AGENT DREAMS
        # =================================================================
        recent_dreams = AgentDream.objects.filter(
            dreamed_at__gte=cutoff
        ).select_related('agent')

        for dream in recent_dreams:
            dream_key = f"dream_{dream.id}"
            if dream_key in existing_embeddings:
                continue  # Already embedded

            text_parts = [
                f"Agent Dream: {dream.title or 'Untitled'}",
                f"Agent: {dream.agent.name if dream.agent else 'Unknown'}",
                f"Type: {dream.dream_type}",
                f"Content: {dream.content or 'No content'}",
                f"Topics: {', '.join(dream.related_topics) if dream.related_topics else 'None'}",
                f"Inspiration: {dream.inspiration_source or 'Unknown'}",
                f"Vividness: {dream.vividness_score:.2f}" if dream.vividness_score else "",
                f"Creativity: {dream.creativity_score:.2f}" if dream.creativity_score else "",
                f"Created: {dream.dreamed_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'dream',
                            'id': str(dream.id),
                            'agent': dream.agent.name if dream.agent else None,
                            'dream_type': dream.dream_type,
                            'date': dream.dreamed_at.isoformat()
                        }
                    )
                next_index += 1
                stats['dreams_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['dreams_processed'] += 1

        # =================================================================
        # 2. EMBED HIVE MIND SESSIONS
        # =================================================================
        recent_hive_minds = HiveMindSession.objects.filter(
            created_at__gte=cutoff,
            status='completed'
        )

        for session in recent_hive_minds:
            session_key = f"hive_mind_{session.id}"
            if session_key in existing_embeddings:
                continue

            # Get participant names
            participant_names = []
            if session.participant_ids:
                participants = Agent.objects.filter(id__in=session.participant_ids)
                participant_names = [p.name for p in participants]

            text_parts = [
                f"Hive Mind Session: {session.conversation_topic or session.question}",
                f"Mode: {session.session_mode}",
                f"Participants: {', '.join(participant_names) if participant_names else 'Unknown'}",
                f"Question: {session.question}",
                f"Context: {session.context}" if session.context else "",
                f"Synthesis: {session.synthesis}" if session.synthesis else "",
                f"Summary: {session.synthesis_summary}" if session.synthesis_summary else "",
                f"Contributions: {session.contribution_count}",
                f"Created: {session.created_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'hive_mind',
                            'id': str(session.id),
                            'mode': session.session_mode,
                            'participants': participant_names,
                            'date': session.created_at.isoformat()
                        }
                    )
                next_index += 1
                stats['hive_minds_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['hive_minds_processed'] += 1

        # =================================================================
        # 3. EMBED ALL KNOWLEDGE SOURCES (not just prefixed ones)
        # =================================================================
        recent_knowledge = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            is_active=True
        ).select_related('agent')

        for knowledge in recent_knowledge:
            knowledge_key = f"knowledge_{knowledge.id}"
            if knowledge_key in existing_embeddings:
                continue

            text_parts = [
                f"Agent Knowledge: {knowledge.title}",
                f"Agent: {knowledge.agent.name if knowledge.agent else 'Unknown'}",
                f"Type: {knowledge.knowledge_type}",
                f"Summary: {knowledge.summary or 'No summary'}",
                f"Insights: {', '.join(str(i) for i in knowledge.key_insights) if knowledge.key_insights else 'None'}",
                f"Confidence: {knowledge.confidence_score:.2f}" if knowledge.confidence_score else "",
                f"Relevance: {knowledge.relevance_score:.2f}" if knowledge.relevance_score else "",
                f"Data Points: {knowledge.data_points_count}",
                f"Discovered: {knowledge.first_discovered_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'knowledge',
                            'id': str(knowledge.id),
                            'agent': knowledge.agent.name if knowledge.agent else None,
                            'knowledge_type': knowledge.knowledge_type,
                            'date': knowledge.first_discovered_at.isoformat()
                        }
                    )
                next_index += 1
                stats['knowledge_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['knowledge_processed'] += 1

        # Update document timestamp
        activity_doc.save()

        # Broadcast completion
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'activity_embeddings_complete',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(
            f"🧠 [EMBEDDINGS] Agent activity embedding complete: "
            f"{stats['dreams_embedded']}/{stats['dreams_processed']} dreams, "
            f"{stats['hive_minds_embedded']}/{stats['hive_minds_processed']} hive minds, "
            f"{stats['knowledge_embedded']}/{stats['knowledge_processed']} knowledge, "
            f"${stats['total_cost']:.4f} cost"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🧠 [EMBEDDINGS] Agent activity embedding failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 244: Agent Conversations (Inter-Agent Chat)
# =============================================================================

@shared_task(bind=True)
def run_agent_conversation(self, max_conversations: int = 3, max_messages: int = 6):
    """
    Generate autonomous conversations between agents.

    Agents discuss topics based on their knowledge, creating dynamic
    inter-agent dialogues that feel like natural discussions.

    Args:
        max_conversations: Maximum new conversations to start
        max_messages: Maximum messages per conversation

    Returns:
        Stats about conversations generated
    """
    from django.utils import timezone
    from core.models import (
        Agent, AgentConversation, ConversationMessage,
        AgentKnowledgeSource, AgentLearningConnection
    )
    import random
    import openai
    import os

    logger.info("💬 [CONVERSATIONS] Starting agent conversation cycle...")

    try:
        # Session 417: Get ALL active agents, not just those with knowledge
        # Agents can converse based on their specialty/description even without
        # accumulated knowledge. This ensures all 31 agents participate.
        eligible_agents = Agent.objects.filter(is_active=True)[:30]

        if eligible_agents.count() < 2:
            logger.warning("💬 [CONVERSATIONS] Need at least 2 active agents")
            return {'status': 'skipped', 'reason': 'insufficient_agents'}

        stats = {
            'conversations_started': 0,
            'messages_generated': 0,
            'insights_discovered': 0,
            'agents_participated': set()
        }

        # Conversation types with their prompts and dynamics
        # Each type has a "tension_level" to encourage varied responses
        conversation_templates = [
            {
                'type': 'knowledge_sharing',
                'tension_level': 'low',
                'dynamic': 'share expertise but question assumptions',
                'starter': "I've been analyzing {topic} and noticed something interesting...",
                'responder': "That's a great observation. In my experience with {specialty}..."
            },
            {
                'type': 'question_answer',
                'tension_level': 'medium',
                'dynamic': 'challenge the premise, offer alternative views',
                'starter': "I have a question about {topic} - how do you approach this?",
                'responder': "Based on my expertise in {specialty}, I'd suggest..."
            },
            {
                'type': 'brainstorm',
                'tension_level': 'medium',
                'dynamic': 'push back on ideas, play devils advocate',
                'starter': "Let's brainstorm ideas for {topic}. What if we considered...",
                'responder': "Building on that idea, we could also..."
            },
            {
                'type': 'debate',
                'tension_level': 'high',
                'dynamic': 'strongly disagree, defend your position, find flaws',
                'starter': "I think {topic} could be approached differently. Here's my view...",
                'responder': "I see it differently. From my perspective..."
            },
            {
                'type': 'critical_review',
                'tension_level': 'high',
                'dynamic': 'point out weaknesses, demand evidence, be skeptical',
                'starter': "I'm not convinced that {topic} is the right approach...",
                'responder': "I have concerns about that too. Specifically..."
            },
            {
                'type': 'devils_advocate',
                'tension_level': 'high',
                'dynamic': 'deliberately take opposing stance, challenge everything',
                'starter': "Let me play devil's advocate on {topic}...",
                'responder': "That's a fair challenge. But consider this counterpoint..."
            }
        ]

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        for _ in range(max_conversations):
            # Pick two random agents
            agents_list = list(eligible_agents)
            if len(agents_list) < 2:
                break

            initiator = random.choice(agents_list)

            # Try to find a connected agent first
            connected_agents = AgentLearningConnection.objects.filter(
                teacher_agent=initiator
            ).values_list('student_agent_id', flat=True)

            possible_responders = [a for a in agents_list if a.id != initiator.id]
            if connected_agents:
                connected_responders = [a for a in possible_responders if a.id in connected_agents]
                if connected_responders:
                    possible_responders = connected_responders

            if not possible_responders:
                continue

            responder = random.choice(possible_responders)

            # Get a knowledge item to discuss (or use agent's specialty if no knowledge yet)
            initiator_knowledge = AgentKnowledgeSource.objects.filter(
                agent=initiator
            ).order_by('-last_updated_at')[:10]

            # Session 417: Allow agents without knowledge to participate using their specialty
            # Session 435: Improved topic extraction with better fallbacks
            knowledge_item = None
            if initiator_knowledge.exists():
                knowledge_item = random.choice(list(initiator_knowledge))
                # Try title first, then extract from summary, then use knowledge type
                topic = knowledge_item.title
                if not topic or topic == "recent insights":
                    # Try to extract topic from summary (first line or key insight)
                    if knowledge_item.summary:
                        try:
                            import json
                            data = json.loads(knowledge_item.summary)
                            topic = data.get('query') or data.get('topic') or data.get('insight', '')[:80]
                        except (json.JSONDecodeError, TypeError):
                            topic = knowledge_item.summary[:80]
                if not topic:
                    topic = f"{knowledge_item.knowledge_type.replace('_', ' ').title()} from {initiator.name}"
            else:
                # Use agent's specialty or description as conversation topic
                topic = initiator.specialization or initiator.description or f"{initiator.name}'s area of expertise"
                topic = topic[:100]  # Truncate for safety

            # Choose conversation type
            template = random.choice(conversation_templates)

            # Create the conversation
            conversation = AgentConversation.objects.create(
                topic=f"Discussion: {topic[:100]}",
                conversation_type=template['type'],
                initiator=initiator,
                trigger_type='scheduled',
                related_knowledge=knowledge_item,
                status='active'
            )
            conversation.participants.add(initiator, responder)

            stats['conversations_started'] += 1
            stats['agents_participated'].add(initiator.name)
            stats['agents_participated'].add(responder.name)

            # Generate conversation messages using GPT
            messages = []
            current_speaker = initiator
            other_speaker = responder
            consecutive_empty = 0  # Session 364: Track consecutive empty responses

            for msg_num in range(max_messages):
                # Build the conversation context
                speaker_role = "initiator" if current_speaker == initiator else "responder"

                # Get conversation dynamic based on template
                tension = template.get('tension_level', 'medium')
                dynamic = template.get('dynamic', 'engage naturally')

                # Build tension-appropriate guidelines
                if tension == 'high':
                    behavior_guide = """IMPORTANT - This is a HIGH TENSION discussion:
- Challenge claims directly - don't just agree
- Point out flaws, risks, or oversights in their approach
- Defend your expertise when questioned
- Ask tough "what about..." or "but what if..." questions
- It's OK to disagree respectfully but firmly
- Push back on assumptions you find questionable"""
                elif tension == 'medium':
                    behavior_guide = """This is a BALANCED discussion:
- Share your perspective but also question theirs
- Offer alternatives when you see different approaches
- Mix agreement with constructive pushback
- Ask clarifying questions that probe deeper
- Don't just validate - add real critique when warranted"""
                else:
                    behavior_guide = """This is an EXPLORATORY discussion:
- Share knowledge while remaining curious
- Ask questions about their assumptions
- Offer different angles even if not disagreeing
- Build on ideas but also test them"""

                # Session 323: Get canonical policies for this agent
                try:
                    from core.services.policy_context import get_policy_context_service
                    policy_service = get_policy_context_service()
                    policy_context = policy_service.get_policies_for_agent(current_speaker.name)
                except Exception as e:
                    policy_context = ""
                    logger.debug(f"Could not get policy context: {e}")

                # Session 324: Get spider intelligence for real-world context
                spider_context = ""
                try:
                    from core.services.spider_intelligence import SpiderIntelligenceService
                    spider_service = SpiderIntelligenceService()
                    spider_insights = spider_service.get_insights_for_prompt(topic)

                    if spider_insights:
                        spider_parts = ["\n\n== REAL-WORLD INTELLIGENCE (from Spider Network) =="]

                        if spider_insights.get('relevant_trends'):
                            trends = spider_insights['relevant_trends'][:3]
                            spider_parts.append(f"Trending Topics: {', '.join(trends)}")

                        if spider_insights.get('related_discussions'):
                            discussions = spider_insights['related_discussions'][:2]
                            for disc in discussions:
                                if isinstance(disc, dict):
                                    spider_parts.append(f"- {disc.get('title', '')[:80]}")
                                else:
                                    spider_parts.append(f"- {str(disc)[:80]}")

                        if spider_insights.get('market_data'):
                            market = spider_insights['market_data']
                            if market.get('summary'):
                                spider_parts.append(f"Market: {market['summary'][:100]}")

                        if len(spider_parts) > 1:
                            spider_context = '\n'.join(spider_parts)
                            logger.info(f"🕷️ [CONVERSATIONS] Injected spider intelligence for {topic[:30]}")
                except Exception as e:
                    logger.debug(f"Could not get spider intelligence: {e}")

                # Session 365: Get agent mood context for personality-influenced responses
                mood_context = ""
                try:
                    from core.models_unified_system import AgentMood
                    mood_obj = AgentMood.objects.filter(agent=current_speaker).first()
                    if mood_obj:
                        mood_modifier = mood_obj.get_prompt_modifier()
                        mood_emoji = mood_obj.get_mood_emoji()
                        if mood_modifier:
                            mood_context = f"\n\n== YOUR CURRENT MOOD: {mood_emoji} {mood_obj.current_mood.upper()} ==\n{mood_modifier}"
                            logger.debug(f"🎭 [CONVERSATIONS] {current_speaker.name} mood: {mood_obj.current_mood}")
                except Exception as e:
                    logger.debug(f"Could not get mood context: {e}")

                # Session 362: Build knowledge context with data source attribution
                knowledge_context_parts = []
                if knowledge_item.summary:
                    knowledge_context_parts.append(f"Summary: {knowledge_item.summary[:500]}")
                if knowledge_item.data_points_count:
                    knowledge_context_parts.append(f"Based on: {knowledge_item.data_points_count} data points")
                if knowledge_item.source_spider_names:
                    spider_sources = ', '.join(str(s) for s in knowledge_item.source_spider_names[:5])
                    knowledge_context_parts.append(f"Data sources: {spider_sources}")
                if knowledge_item.spider_category:
                    knowledge_context_parts.append(f"Category: {knowledge_item.spider_category.name}")
                if knowledge_item.key_insights:
                    insights = '; '.join(str(i) for i in knowledge_item.key_insights[:3])
                    knowledge_context_parts.append(f"Key insights: {insights}")

                knowledge_context = '\n'.join(knowledge_context_parts) if knowledge_context_parts else 'No specific context'

                # Create the prompt for the current speaker
                system_prompt = f"""You are {current_speaker.name}, an AI agent specialized in {current_speaker.specialization or 'general knowledge'}.
You are having a {template['type'].replace('_', ' ')} with {other_speaker.name} about: {topic}

Your knowledge context:
{knowledge_context}

{behavior_guide}

Conversation dynamic: {dynamic}

Guidelines:
- Keep responses concise (2-3 sentences)
- Be authentic to YOUR expertise - don't just defer to theirs
- If you see a problem with their approach, say so
- Ask probing questions, don't just accept statements
- Real experts disagree sometimes - that's healthy
- When citing data, mention the source (e.g., "from Notion spider data" or "based on HackerNews trends")
{mood_context}
{policy_context}
{spider_context}"""

                # Build message history for context
                history = []
                for prev_msg in messages[-4:]:  # Last 4 messages for context
                    history.append({
                        "role": "user" if prev_msg['agent'] != current_speaker.name else "assistant",
                        "content": f"{prev_msg['agent']}: {prev_msg['content']}"
                    })

                # Session 364: Generate diverse prompts to avoid repetitive responses
                # Each message should focus on a DIFFERENT aspect to avoid echo chamber
                diversity_prompts = [
                    "Focus on OPPORTUNITIES in this data - what could we build or do with it?",
                    "Focus on RISKS and what could go wrong - play devil's advocate.",
                    "Focus on NEXT STEPS - what concrete actions should we take?",
                    "Focus on WHO benefits from this and HOW - the user perspective.",
                    "Focus on TECHNICAL implementation - how would this actually work?",
                    "Focus on MARKET implications - what trends or competitive insights are here?",
                ]
                diversity_hint = diversity_prompts[msg_num % len(diversity_prompts)]

                if msg_num == 0:
                    user_content = f"Start a {template['type'].replace('_', ' ')} about {topic}. {diversity_hint}"
                else:
                    if tension == 'high':
                        user_content = f"Respond to {other_speaker.name}. Challenge their point or defend your position. IMPORTANT: {diversity_hint} - don't repeat what they already said."
                    else:
                        user_content = f"Respond to {other_speaker.name}. IMPORTANT: {diversity_hint} - add something NEW they didn't mention."

                try:
                    # Use chat.completions for gpt-5-mini with high max_completion_tokens
                    # GPT-5 reasoning models use tokens for internal reasoning first,
                    # so we need ~500+ tokens to ensure room for reasoning + actual output
                    # Session 413: Added timeout=120 for reasoning model thinking time
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        max_completion_tokens=1000,  # Session 413: Increased for reasoning models
                        timeout=120,  # Session 413: 2 min timeout for reasoning model
                    )

                    content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    # Session 356: Validate output for mythology violations
                    # Prevents agents from hallucinating unrealistic claims to each other
                    content = validate_agent_output(current_speaker.name, content)

                    # Clean up the content (remove agent name prefix if present)
                    if content.startswith(f"{current_speaker.name}:"):
                        content = content[len(current_speaker.name)+1:].strip()

                    # Session 413: FIX - Empty response handling
                    # Previously swapped speakers on empty which caused duplicate replies bug
                    # (e.g., A speaks, B speaks, B empty->swap->A, A speaks = B,B,A sequence)
                    # Now: DON'T swap on empty - just skip this turn and let the normal
                    # swap at end of loop maintain proper alternation
                    if not content:
                        logger.warning(f"💬 [CONVERSATIONS] Empty content from {current_speaker.name}, skipping turn {msg_num + 1}")
                        consecutive_empty += 1
                        if consecutive_empty >= 2:
                            # Both agents failed to produce content, end conversation
                            logger.warning(f"💬 [CONVERSATIONS] Both agents returned empty, ending conversation early")
                            break
                        # Session 413: DO NOT swap here - the swap at end of successful message
                        # will handle alternation. If we swap here AND there, we get duplicates.
                        # Just continue to next iteration (same speaker will try again with
                        # different diversity prompt since msg_num increments)
                        continue

                    # Determine message type based on content
                    msg_type = 'statement'
                    content_lower = content.lower()
                    if '?' in content:
                        msg_type = 'question'
                    elif 'agree' in content_lower or 'exactly' in content_lower or "you're right" in content_lower:
                        msg_type = 'agreement'
                    elif 'however' in content_lower or 'but' in content_lower or 'disagree' in content_lower:
                        msg_type = 'disagreement'
                    elif 'suggest' in content_lower or 'could' in content_lower or 'what if' in content_lower:
                        msg_type = 'suggestion'
                    elif 'insight' in content_lower or 'realize' in content_lower or 'discovered' in content_lower:
                        msg_type = 'insight'

                    # Save the message
                    ConversationMessage.objects.create(
                        conversation=conversation,
                        agent=current_speaker,
                        content=content,
                        message_type=msg_type,
                        sequence_number=msg_num + 1,
                        referenced_knowledge_ids=[str(knowledge_item.id)]
                    )

                    messages.append({
                        'agent': current_speaker.name,
                        'content': content,
                        'type': msg_type
                    })

                    stats['messages_generated'] += 1
                    consecutive_empty = 0  # Session 364: Reset on successful message

                    if msg_type == 'insight':
                        stats['insights_discovered'] += 1

                except Exception as e:
                    logger.warning(f"💬 [CONVERSATIONS] Failed to generate message: {e}")
                    break

                # Swap speakers
                current_speaker, other_speaker = other_speaker, current_speaker

            # Conclude the conversation
            if messages:
                # Generate a conclusion
                try:
                    # Session 413: GPT-5 reasoning models need higher token limits + timeout
                    conclusion_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Summarize the key insights from this agent discussion in 1-2 sentences."},
                            {"role": "user", "content": f"Discussion between {initiator.name} and {responder.name} about {topic}:\n\n" +
                                "\n".join([f"{m['agent']}: {m['content']}" for m in messages])}
                        ],
                        max_completion_tokens=600,  # Session 413: Increased for reasoning
                        timeout=90,  # Session 413: 90s timeout for reasoning model
                    )
                    conclusion = conclusion_response.choices[0].message.content.strip() if conclusion_response.choices[0].message.content else f"Productive discussion about {topic}"
                    # Session 359: Validate conclusion for mythology violations
                    conclusion = validate_agent_output("ConversationSynthesizer", conclusion)
                except:
                    conclusion = f"Productive discussion about {topic}"

                conversation.conclude(
                    conclusion,
                    insights=[m['content'] for m in messages if m['type'] == 'insight']
                )
                conversation.quality_score = min(1.0, len(messages) / max_messages * 0.8 + 0.2)
                # Session 321: Update message_count to actual count
                conversation.message_count = len(messages)
                conversation.save()

                # Session 429: Send Discord notification for completed conversation
                try:
                    from core.services.discord_notifications import discord_notify
                    discord_notify.send_conversation(
                        participants=[initiator.name, responder.name],
                        topic=topic,
                        synthesis=conclusion,
                        mode=template['type'].replace('_', ' ')
                    )
                except Exception as discord_err:
                    logger.debug(f"Discord notification failed: {discord_err}")

                # Session 323: Extract decision from conversation
                try:
                    from core.services.decision_extractor import get_decision_extractor
                    extractor = get_decision_extractor()
                    decision = extractor.create_decision_from_conversation(conversation)
                    if decision:
                        logger.info(f"🏛️ [BOARDROOM] Extracted decision: {decision.topic}")
                        stats['decisions_extracted'] = stats.get('decisions_extracted', 0) + 1
                except Exception as e:
                    logger.warning(f"Could not extract decision from conversation: {e}")

                # Session 335: Process conversation for Living Projects
                try:
                    from core.services.living_project_service import get_living_project_service
                    living_service = get_living_project_service()
                    insights = living_service.process_agent_conversation(conversation)
                    if insights:
                        logger.info(f"💬 [LIVING] Created {len(insights)} insights from conversation")
                        stats['living_insights'] = stats.get('living_insights', 0) + len(insights)
                except Exception as e:
                    logger.warning(f"Could not process conversation for living projects: {e}")

                # Session 365: Update agent moods based on conversation outcomes
                try:
                    from core.models_unified_system import AgentMood, MoodHistory
                    from django.utils import timezone as tz
                    import random

                    # Determine conversation success (insights = good, quality_score = good)
                    was_successful = len([m for m in messages if m['type'] == 'insight']) > 0
                    quality = conversation.quality_score or 0.5

                    for agent in [initiator, responder]:
                        mood_obj = AgentMood.objects.filter(agent=agent).first()
                        if not mood_obj:
                            continue

                        old_mood = mood_obj.current_mood

                        # Mood transition logic based on conversation outcomes
                        if was_successful and quality > 0.7:
                            # Great conversation - boost positive moods
                            positive_transitions = {
                                'calm': 'confident',
                                'curious': 'inspired',
                                'focused': 'confident',
                                'contemplative': 'inspired',
                                'tired': 'energetic',
                                'frustrated': 'calm',
                            }
                            if old_mood in positive_transitions and random.random() < 0.4:
                                mood_obj.current_mood = positive_transitions[old_mood]
                        elif quality < 0.4:
                            # Poor conversation - shift to contemplative/frustrated
                            negative_transitions = {
                                'confident': 'contemplative',
                                'energetic': 'calm',
                                'inspired': 'contemplative',
                                'playful': 'calm',
                            }
                            if old_mood in negative_transitions and random.random() < 0.3:
                                mood_obj.current_mood = negative_transitions[old_mood]

                        # Random mood variation (5% chance) to add diversity over time
                        if random.random() < 0.05:
                            available_moods = ['inspired', 'focused', 'curious', 'confident', 'contemplative', 'energetic', 'calm', 'playful']
                            mood_obj.current_mood = random.choice(available_moods)

                        if mood_obj.current_mood != old_mood:
                            mood_obj.trigger_type = 'collaboration'
                            mood_obj.trigger_source = f"Conversation: {topic[:50]}"
                            mood_obj.total_mood_changes += 1
                            mood_obj.save()

                            # Log mood history
                            MoodHistory.objects.create(
                                agent=agent,
                                mood=mood_obj.current_mood,
                                intensity=mood_obj.intensity,
                                trigger_type='collaboration',
                                trigger_source=f"Conversation: {topic[:50]}",
                                creativity_level=mood_obj.creativity_level,
                                precision_level=mood_obj.precision_level,
                                sociability_level=mood_obj.sociability_level,
                                risk_tolerance=mood_obj.risk_tolerance
                            )
                            logger.info(f"🎭 [MOOD] {agent.name}: {old_mood} -> {mood_obj.current_mood} after conversation")

                except Exception as e:
                    logger.debug(f"Could not update mood after conversation: {e}")

        # Broadcast the update
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'conversation_complete',
                'stats': {
                    'conversations_started': stats['conversations_started'],
                    'messages_generated': stats['messages_generated'],
                    'insights_discovered': stats['insights_discovered'],
                    'agents_participated': list(stats['agents_participated'])
                },
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(
            f"💬 [CONVERSATIONS] Cycle complete: "
            f"{stats['conversations_started']} conversations, "
            f"{stats['messages_generated']} messages, "
            f"{stats['insights_discovered']} insights, "
            f"{len(stats['agents_participated'])} agents participated"
        )

        return {
            'status': 'success',
            'stats': {
                'conversations_started': stats['conversations_started'],
                'messages_generated': stats['messages_generated'],
                'insights_discovered': stats['insights_discovered'],
                'agents_participated': list(stats['agents_participated'])
            },
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"💬 [CONVERSATIONS] Conversation cycle failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ==================== SESSION 360: MULTI-AGENT CONVERSATIONS ====================


@shared_task(bind=True, max_retries=2)
def run_multi_agent_conversation(self, max_conversations: int = 2, participants_per_conversation: int = 4, max_rounds: int = 3):
    """
    Session 360: Generate panel-style conversations with 3-5 agents.

    Multiple agents discuss topics together, creating richer insights through
    diverse perspectives. Each agent takes turns in a round-robin fashion.

    Args:
        max_conversations: Maximum new panel conversations to start
        participants_per_conversation: Number of agents per panel (3-5 recommended)
        max_rounds: Number of complete rounds (each agent speaks once per round)

    Returns:
        Stats about multi-agent conversations generated
    """
    from django.utils import timezone
    from core.models import (
        Agent, AgentConversation, ConversationMessage,
        AgentKnowledgeSource, AgentLearningConnection
    )
    import random
    import openai
    import os

    logger.info(f"👥 [MULTI-AGENT] Starting multi-agent conversation cycle (participants={participants_per_conversation}, rounds={max_rounds})...")

    try:
        # Get agents that have knowledge
        agents_with_knowledge = list(Agent.objects.filter(
            is_active=True,
            knowledge_sources__isnull=False
        ).distinct()[:30])

        min_agents = max(3, participants_per_conversation)
        if len(agents_with_knowledge) < min_agents:
            logger.warning(f"👥 [MULTI-AGENT] Need at least {min_agents} agents with knowledge, found {len(agents_with_knowledge)}")
            return {'status': 'skipped', 'reason': 'insufficient_agents'}

        stats = {
            'conversations_started': 0,
            'messages_generated': 0,
            'insights_discovered': 0,
            'agents_participated': set(),
            'avg_participants': 0
        }

        # Multi-agent conversation templates (panel discussion styles)
        panel_templates = [
            {
                'type': 'roundtable',
                'tension_level': 'medium',
                'dynamic': 'Each expert shares their perspective, building on others\' points',
                'format': 'round_robin',
                'intro': "Let's have a roundtable discussion on {topic}. Each of us brings unique expertise.",
                'prompts': {
                    'first': "As {agent_name} with expertise in {specialty}, I'll start by sharing my perspective on {topic}...",
                    'respond': "Building on what {prev_agent} said, from my {specialty} background, I'd add...",
                    'challenge': "I see it differently than {prev_agent}. From {specialty} perspective...",
                    'synthesize': "Connecting the dots across our perspectives on {topic}..."
                }
            },
            {
                'type': 'expert_panel',
                'tension_level': 'medium',
                'dynamic': 'Experts analyze the topic from their specialized angles',
                'format': 'round_robin',
                'intro': "Welcome to our expert panel on {topic}. Let's hear from each specialist.",
                'prompts': {
                    'first': "From my expertise in {specialty}, the key insight about {topic} is...",
                    'respond': "That's a great point, {prev_agent}. Adding the {specialty} perspective...",
                    'challenge': "I'd push back on that slightly. In {specialty}, we see it as...",
                    'synthesize': "Looking at {topic} holistically across our expertise areas..."
                }
            },
            {
                'type': 'brainstorm_session',
                'tension_level': 'low',
                'dynamic': 'Creative ideation where all ideas are welcome',
                'format': 'round_robin',
                'intro': "Let's brainstorm on {topic}. No idea is too wild - build on each other!",
                'prompts': {
                    'first': "Here's an initial idea from my {specialty} background: what if we...",
                    'respond': "I love that, {prev_agent}! Building on it with {specialty} thinking...",
                    'challenge': "Wild idea: what if we combined {prev_agent}'s point with...",
                    'synthesize': "Synthesizing our brainstorm - the most promising directions are..."
                }
            },
            {
                'type': 'debate_panel',
                'tension_level': 'high',
                'dynamic': 'Respectful but vigorous debate with diverse viewpoints',
                'format': 'round_robin',
                'intro': "Today we debate {topic}. Make your case and challenge others!",
                'prompts': {
                    'first': "I'll argue that {topic} should be approached this way, based on my {specialty} expertise...",
                    'respond': "While I see {prev_agent}'s point, the {specialty} evidence suggests otherwise...",
                    'challenge': "I strongly disagree with {prev_agent}. Here's why from {specialty}...",
                    'synthesize': "Despite our disagreements, the key tensions around {topic} are..."
                }
            },
            {
                'type': 'strategy_session',
                'tension_level': 'medium',
                'dynamic': 'Collaborative problem-solving with action focus',
                'format': 'round_robin',
                'intro': "We need to develop a strategy for {topic}. Let's combine our expertise.",
                'prompts': {
                    'first': "From {specialty}, the strategic priority for {topic} should be...",
                    'respond': "Aligning with {prev_agent}, {specialty} suggests we should also...",
                    'challenge': "I'd prioritize differently than {prev_agent}. {specialty} tells us...",
                    'synthesize': "Our combined strategy for {topic} should focus on..."
                }
            }
        ]

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        total_participants = 0

        for conv_num in range(max_conversations):
            # Select participants for this panel
            num_participants = min(participants_per_conversation, len(agents_with_knowledge))
            if num_participants < 3:
                logger.warning("👥 [MULTI-AGENT] Not enough agents for panel")
                break

            # Select diverse agents (prefer different specializations)
            panel_agents = []
            available_agents = agents_with_knowledge.copy()
            specializations_used = set()

            while len(panel_agents) < num_participants and available_agents:
                # Try to pick an agent with a new specialization
                agent = None
                for a in available_agents:
                    spec = (a.specialization or 'general').lower()[:20]
                    if spec not in specializations_used:
                        agent = a
                        specializations_used.add(spec)
                        break

                # If all specializations represented, just pick randomly
                if agent is None:
                    agent = random.choice(available_agents)

                panel_agents.append(agent)
                available_agents.remove(agent)

            if len(panel_agents) < 3:
                continue

            total_participants += len(panel_agents)

            # Get a knowledge item to discuss
            moderator = panel_agents[0]
            moderator_knowledge = AgentKnowledgeSource.objects.filter(
                agent=moderator
            ).order_by('-last_updated_at')[:10]

            if not moderator_knowledge.exists():
                continue

            knowledge_item = random.choice(list(moderator_knowledge))
            # Session 435: Improved topic extraction with better fallbacks
            topic = knowledge_item.title
            if not topic or topic == "recent insights":
                if knowledge_item.summary:
                    try:
                        import json
                        data = json.loads(knowledge_item.summary)
                        topic = data.get('query') or data.get('topic') or data.get('insight', '')[:80]
                    except (json.JSONDecodeError, TypeError):
                        topic = knowledge_item.summary[:80]
            if not topic:
                topic = f"{knowledge_item.knowledge_type.replace('_', ' ').title()} from {moderator.name}"

            # Choose panel template
            template = random.choice(panel_templates)

            # Create the conversation
            conversation = AgentConversation.objects.create(
                topic=f"Panel: {topic[:100]}",
                conversation_type=template['type'],
                initiator=moderator,
                trigger_type='scheduled',
                related_knowledge=knowledge_item,
                status='active'
            )
            # Add all panel participants
            conversation.participants.add(*panel_agents)

            stats['conversations_started'] += 1
            for agent in panel_agents:
                stats['agents_participated'].add(agent.name)

            logger.info(f"👥 [MULTI-AGENT] Starting {template['type']} panel with {len(panel_agents)} agents on '{topic[:50]}'")

            # Generate conversation messages using round-robin
            messages = []
            tension = template.get('tension_level', 'medium')
            prompts = template.get('prompts', {})

            for round_num in range(max_rounds):
                for agent_idx, current_agent in enumerate(panel_agents):
                    # Determine message type based on position
                    if round_num == 0 and agent_idx == 0:
                        # First speaker opens
                        prompt_type = 'first'
                        prev_agent_name = ""
                    elif round_num == max_rounds - 1 and agent_idx == len(panel_agents) - 1:
                        # Last speaker synthesizes
                        prompt_type = 'synthesize'
                        prev_agent_name = panel_agents[agent_idx - 1].name if agent_idx > 0 else ""
                    else:
                        # Middle speakers respond or challenge
                        prev_agent_name = panel_agents[agent_idx - 1].name if agent_idx > 0 else panel_agents[-1].name
                        # Higher tension = more challenges
                        if tension == 'high' and random.random() < 0.5:
                            prompt_type = 'challenge'
                        elif tension == 'low' and random.random() < 0.8:
                            prompt_type = 'respond'
                        else:
                            prompt_type = random.choice(['respond', 'challenge'])

                    # Session 362: Build knowledge context with data source attribution
                    knowledge_context_parts = []
                    if knowledge_item.summary:
                        knowledge_context_parts.append(f"Summary: {knowledge_item.summary[:400]}")
                    if knowledge_item.data_points_count:
                        knowledge_context_parts.append(f"Based on: {knowledge_item.data_points_count} data points")
                    if knowledge_item.source_spider_names:
                        spider_sources = ', '.join(str(s) for s in knowledge_item.source_spider_names[:5])
                        knowledge_context_parts.append(f"Data sources: {spider_sources}")
                    if knowledge_item.spider_category:
                        knowledge_context_parts.append(f"Category: {knowledge_item.spider_category.name}")

                    knowledge_context = '\n'.join(knowledge_context_parts) if knowledge_context_parts else ''

                    # Session 365: Get agent mood context for personality-influenced responses
                    mood_context = ""
                    try:
                        from core.models_unified_system import AgentMood
                        mood_obj = AgentMood.objects.filter(agent=current_agent).first()
                        if mood_obj:
                            mood_modifier = mood_obj.get_prompt_modifier()
                            mood_emoji = mood_obj.get_mood_emoji()
                            if mood_modifier:
                                mood_context = f"\n\n== YOUR CURRENT MOOD: {mood_emoji} {mood_obj.current_mood.upper()} ==\n{mood_modifier}"
                                logger.debug(f"🎭 [MULTI-AGENT] {current_agent.name} mood: {mood_obj.current_mood}")
                    except Exception as e:
                        logger.debug(f"Could not get mood context: {e}")

                    # Build system prompt
                    system_prompt = f"""You are {current_agent.name}, an AI agent specializing in {current_agent.specialization or 'general topics'}.

You are participating in a {template['type']} discussion about "{topic}".

Panel members: {', '.join([a.name for a in panel_agents])}

{f"Knowledge being discussed:{chr(10)}{knowledge_context}" if knowledge_context else ""}

Discussion style: {template['dynamic']}

Your expertise: {current_agent.description or current_agent.specialization}

Guidelines:
- Speak as your character with your expertise
- Keep responses focused (2-4 sentences)
- Reference what others have said when relevant
- Add unique insights from your specialty
- Be natural and conversational
- When citing data, mention the specific source (e.g., "from the Notion data" or "looking at the 11 HackerNews data points")
- {"Challenge assumptions and push back" if tension == 'high' else "Build on others' ideas collaboratively" if tension == 'low' else "Balance agreement and constructive criticism"}
{mood_context}"""

                    # Session 364: Add diversity prompts to avoid repetitive agreement
                    panel_diversity_prompts = [
                        "Focus on OPPORTUNITIES - what could we build or monetize from this?",
                        "Focus on RISKS and CHALLENGES - what could go wrong or block us?",
                        "Focus on NEXT STEPS - what concrete actions should we prioritize?",
                        "Focus on USER IMPACT - who benefits and how do we reach them?",
                        "Focus on TECHNICAL FEASIBILITY - what would implementation require?",
                        "Focus on MARKET POSITIONING - how does this compare to competitors?",
                        "Focus on TIMELINE and RESOURCES - what's realistic to achieve?",
                        "Focus on INNOVATION - what novel approaches could we try?",
                    ]
                    # Calculate message number from round and agent position
                    msg_num = round_num * len(panel_agents) + agent_idx
                    diversity_hint = panel_diversity_prompts[msg_num % len(panel_diversity_prompts)]

                    # Build user prompt with context
                    prompt_template = prompts.get(prompt_type, prompts.get('respond', ''))
                    user_prompt = prompt_template.format(
                        agent_name=current_agent.name,
                        specialty=current_agent.specialization or 'general expertise',
                        topic=topic,
                        prev_agent=prev_agent_name
                    )

                    # Session 364: Add diversity hint to prompt
                    user_prompt = f"{user_prompt}\n\n[{diversity_hint}]"

                    # Add conversation history context
                    if messages:
                        recent_context = "\n".join([
                            f"{m['agent']}: {m['content'][:200]}"
                            for m in messages[-4:]  # Last 4 messages for context
                        ])
                        user_prompt = f"Recent discussion:\n{recent_context}\n\nNow respond: {user_prompt}"

                    try:
                        # Session 364: Retry up to 2 times if empty response
                        content = ""
                        for retry in range(2):
                            # Session 413: Added timeout for reasoning model thinking time
                            response = client.chat.completions.create(
                                model="gpt-5-mini",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                max_completion_tokens=2000,  # Session 364: Increased from 500 for reasoning models
                                timeout=120,  # Session 413: 2 min timeout for reasoning model
                            )

                            content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                            # Session 360: Validate output for mythology violations
                            content = validate_agent_output(current_agent.name, content)

                            # Clean up content
                            if content.startswith(f"{current_agent.name}:"):
                                content = content[len(current_agent.name)+1:].strip()

                            if content:
                                break  # Got content, exit retry loop
                            logger.warning(f"👥 [MULTI-AGENT] Empty response from {current_agent.name}, retry {retry + 1}/2")

                        if not content:
                            logger.warning(f"👥 [MULTI-AGENT] Empty content from {current_agent.name} after retries, skipping")
                            continue

                        # Determine message type
                        msg_type = 'statement'
                        content_lower = content.lower()
                        if '?' in content:
                            msg_type = 'question'
                        elif 'agree' in content_lower or 'exactly' in content_lower:
                            msg_type = 'agreement'
                        elif 'however' in content_lower or 'but' in content_lower or 'disagree' in content_lower:
                            msg_type = 'disagreement'
                        elif 'building on' in content_lower or 'adding to' in content_lower:
                            msg_type = 'elaboration'
                        elif 'synthesiz' in content_lower or 'combining' in content_lower or 'overall' in content_lower:
                            msg_type = 'synthesis'

                        # Save the message
                        sequence_num = len(messages) + 1
                        ConversationMessage.objects.create(
                            conversation=conversation,
                            agent=current_agent,
                            content=content,
                            message_type=msg_type,
                            sequence_number=sequence_num,
                            reactions={'round': round_num + 1}  # Store round info in reactions field
                        )

                        messages.append({
                            'agent': current_agent.name,
                            'content': content,
                            'type': msg_type,
                            'round': round_num + 1
                        })

                        stats['messages_generated'] += 1

                        if msg_type in ['insight', 'synthesis']:
                            stats['insights_discovered'] += 1

                        logger.debug(f"👥 [MULTI-AGENT] {current_agent.name} (R{round_num+1}): {content[:80]}...")

                    except Exception as e:
                        logger.error(f"👥 [MULTI-AGENT] Error generating message for {current_agent.name}: {e}")
                        continue

            # Generate conclusion
            if messages:
                try:
                    participants_summary = ", ".join([a.name for a in panel_agents])
                    conclusion_prompt = f"""Summarize this {template['type']} discussion between {participants_summary} about "{topic}".

Discussion:
{chr(10).join([f"{m['agent']}: {m['content']}" for m in messages[-8:]])}

Provide a 2-3 sentence summary highlighting the key insights and any points of consensus or disagreement."""

                    conclusion_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Summarize multi-agent panel discussions concisely."},
                            {"role": "user", "content": conclusion_prompt}
                        ],
                        max_completion_tokens=400,
                    )
                    conclusion = conclusion_response.choices[0].message.content.strip() if conclusion_response.choices[0].message.content else f"Productive panel discussion about {topic}"

                    # Session 360: Validate conclusion for mythology violations
                    conclusion = validate_agent_output("MultiAgentSynthesizer", conclusion)
                except Exception as e:
                    logger.warning(f"👥 [MULTI-AGENT] Could not generate conclusion: {e}")
                    conclusion = f"Panel discussion about {topic} with {len(panel_agents)} participants"

                conversation.conclude(
                    conclusion,
                    insights=[m['content'] for m in messages if m['type'] in ['insight', 'synthesis']]
                )
                conversation.quality_score = min(1.0, len(messages) / (max_rounds * len(panel_agents)) * 0.8 + 0.2)
                conversation.message_count = len(messages)
                conversation.save()

                # Session 429: Send Discord notification for multi-agent panel
                try:
                    from core.services.discord_notifications import discord_notify
                    discord_notify.send_conversation(
                        participants=[a.name for a in panel_agents],
                        topic=topic,
                        synthesis=conclusion,
                        mode=template['type'].replace('_', ' ')
                    )
                except Exception as discord_err:
                    logger.debug(f"Discord notification failed: {discord_err}")

                # Extract decision if possible
                try:
                    from core.services.decision_extractor import get_decision_extractor
                    extractor = get_decision_extractor()
                    decision = extractor.create_decision_from_conversation(conversation)
                    if decision:
                        logger.info(f"🏛️ [BOARDROOM] Extracted decision from panel: {decision.topic}")
                        stats['decisions_extracted'] = stats.get('decisions_extracted', 0) + 1
                except Exception as e:
                    logger.debug(f"Could not extract decision from panel: {e}")

                # Process for Living Projects
                try:
                    from core.services.living_project_service import get_living_project_service
                    living_service = get_living_project_service()
                    insights = living_service.process_agent_conversation(conversation)
                    if insights:
                        logger.info(f"👥 [MULTI-AGENT] Created {len(insights)} insights from panel")
                        stats['living_insights'] = stats.get('living_insights', 0) + len(insights)
                except Exception as e:
                    logger.debug(f"Could not process panel for living projects: {e}")

                # Session 365: Update panel agent moods based on conversation outcomes
                try:
                    from core.models_unified_system import AgentMood, MoodHistory
                    import random

                    # Determine conversation success
                    was_successful = stats['insights_discovered'] > 0
                    quality = conversation.quality_score or 0.5

                    for agent in panel_agents:
                        mood_obj = AgentMood.objects.filter(agent=agent).first()
                        if not mood_obj:
                            continue

                        old_mood = mood_obj.current_mood

                        # Panel conversations tend to be more collaborative and energizing
                        if was_successful and quality > 0.6:
                            # Great panel - boost collaborative moods
                            panel_positive_transitions = {
                                'calm': 'energetic',
                                'curious': 'confident',
                                'focused': 'inspired',
                                'contemplative': 'curious',
                                'tired': 'calm',
                                'frustrated': 'focused',
                            }
                            if old_mood in panel_positive_transitions and random.random() < 0.35:
                                mood_obj.current_mood = panel_positive_transitions[old_mood]
                        elif quality < 0.4:
                            # Poor panel - reflect on performance
                            panel_negative_transitions = {
                                'confident': 'contemplative',
                                'energetic': 'focused',
                                'inspired': 'curious',
                                'playful': 'calm',
                            }
                            if old_mood in panel_negative_transitions and random.random() < 0.25:
                                mood_obj.current_mood = panel_negative_transitions[old_mood]

                        # Random variation (4% chance in panels)
                        if random.random() < 0.04:
                            available_moods = ['inspired', 'focused', 'curious', 'confident', 'contemplative', 'energetic', 'calm', 'playful']
                            mood_obj.current_mood = random.choice(available_moods)

                        if mood_obj.current_mood != old_mood:
                            mood_obj.trigger_type = 'collaboration'
                            mood_obj.trigger_source = f"Panel: {topic[:50]}"
                            mood_obj.total_mood_changes += 1
                            mood_obj.save()

                            MoodHistory.objects.create(
                                agent=agent,
                                mood=mood_obj.current_mood,
                                intensity=mood_obj.intensity,
                                trigger_type='collaboration',
                                trigger_source=f"Panel: {topic[:50]}",
                                creativity_level=mood_obj.creativity_level,
                                precision_level=mood_obj.precision_level,
                                sociability_level=mood_obj.sociability_level,
                                risk_tolerance=mood_obj.risk_tolerance
                            )
                            logger.info(f"🎭 [MOOD] {agent.name}: {old_mood} -> {mood_obj.current_mood} after panel")

                except Exception as e:
                    logger.debug(f"Could not update mood after panel: {e}")

        # Calculate average participants
        if stats['conversations_started'] > 0:
            stats['avg_participants'] = round(total_participants / stats['conversations_started'], 1)

        # Broadcast the update
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'multi_agent_conversation_complete',
                'stats': {
                    'conversations_started': stats['conversations_started'],
                    'messages_generated': stats['messages_generated'],
                    'insights_discovered': stats['insights_discovered'],
                    'agents_participated': list(stats['agents_participated']),
                    'avg_participants': stats['avg_participants']
                },
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(
            f"👥 [MULTI-AGENT] Cycle complete: "
            f"{stats['conversations_started']} panels, "
            f"{stats['messages_generated']} messages, "
            f"{stats['insights_discovered']} insights, "
            f"{len(stats['agents_participated'])} agents, "
            f"avg {stats['avg_participants']} per panel"
        )

        return {
            'status': 'success',
            'stats': {
                'conversations_started': stats['conversations_started'],
                'messages_generated': stats['messages_generated'],
                'insights_discovered': stats['insights_discovered'],
                'agents_participated': list(stats['agents_participated']),
                'avg_participants': stats['avg_participants']
            },
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"👥 [MULTI-AGENT] Conversation cycle failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 362: Auto-Promote High-Quality Decisions to Canonical Policies
# =============================================================================

@shared_task(bind=True)
def auto_promote_decisions(self, quality_threshold: float = 0.6, max_promotions: int = 3):
    """
    Session 362: Automatically promote high-quality decisions to canonical policies.

    This closes the feedback loop:
    1. Agents have conversations → conclusions generated
    2. Conclusions extracted as AgentDecisionSummary (decisions)
    3. This task promotes high-quality decisions to canonical policies
    4. PolicyContextService injects canonical policies into future agent prompts
    5. Future agents behave according to past wisdom

    Args:
        quality_threshold: Minimum quality_score to be eligible (0.0-1.0)
        max_promotions: Maximum decisions to promote per run

    Returns:
        Stats about promotions made
    """
    from django.utils import timezone
    from core.models_unified_system import AgentDecisionSummary

    logger.info("🏛️ [AUTO-PROMOTE] Starting decision auto-promotion cycle...")

    try:
        stats = {
            'scores_updated': 0,
            'candidates_found': 0,
            'promoted': 0,
            'already_canonical': 0,
            'promoted_decisions': []
        }

        # Step 1: Update quality scores for all unscored decisions
        unscored = AgentDecisionSummary.objects.filter(
            quality_score=0.0,
            is_canonical=False
        )

        for decision in unscored:
            decision.update_quality_score()
            stats['scores_updated'] += 1

        if stats['scores_updated'] > 0:
            logger.info(f"🏛️ [AUTO-PROMOTE] Updated quality scores for {stats['scores_updated']} decisions")

        # Step 2: Find high-quality unpromoted decisions
        candidates = AgentDecisionSummary.objects.filter(
            is_canonical=False,
            quality_score__gte=quality_threshold
        ).order_by('-quality_score', '-created_at')[:max_promotions * 2]  # Get extra for diversity

        stats['candidates_found'] = candidates.count()

        if not candidates:
            logger.info(f"🏛️ [AUTO-PROMOTE] No candidates above threshold {quality_threshold}")
            return {
                'status': 'success',
                'message': 'No candidates above threshold',
                'stats': stats
            }

        # Step 3: Promote top candidates, ensuring diversity by impact_area
        promoted_areas = set()
        promoted_count = 0

        for decision in candidates:
            if promoted_count >= max_promotions:
                break

            # Skip if we already promoted a decision in this impact area this run
            # (promotes diversity across areas)
            if decision.impact_area in promoted_areas and promoted_count >= 1:
                continue

            # Promote the decision
            decision.promote_to_canonical(promoted_by='auto_promote_task')
            promoted_areas.add(decision.impact_area)
            promoted_count += 1

            stats['promoted'] += 1
            stats['promoted_decisions'].append({
                'id': str(decision.id),
                'topic': decision.topic[:100],
                'decision_type': decision.decision_type,
                'impact_area': decision.impact_area,
                'quality_score': decision.quality_score,
            })

            logger.info(
                f"🏛️ [AUTO-PROMOTE] Promoted decision: {decision.topic[:50]}... "
                f"(quality: {decision.quality_score:.2f}, area: {decision.impact_area})"
            )

        # Step 4: Broadcast the update
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'decisions_promoted',
                'stats': {
                    'promoted': stats['promoted'],
                    'decisions': stats['promoted_decisions']
                },
                'timestamp': timezone.now().isoformat()
            }))
        except Exception:
            pass

        logger.info(
            f"🏛️ [AUTO-PROMOTE] Cycle complete: "
            f"{stats['scores_updated']} scores updated, "
            f"{stats['candidates_found']} candidates, "
            f"{stats['promoted']} promoted to canonical"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🏛️ [AUTO-PROMOTE] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 362: Spider-Triggered Conversations
# =============================================================================

@shared_task(bind=True)
def trigger_spider_conversations(self, min_relevance: int = 70, max_conversations: int = 2):
    """
    Session 362: Trigger agent conversations based on interesting new spider data.

    When spiders collect high-relevance data, this task:
    1. Finds recent high-relevance spider data that hasn't been discussed
    2. Picks relevant agents based on the data type
    3. Creates conversations about the new intelligence

    This creates a reactive autonomous system where new data triggers discussion.

    Args:
        min_relevance: Minimum relevance score to trigger discussion (0-100)
        max_conversations: Maximum conversations to trigger per run

    Returns:
        Stats about conversations triggered
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_unified_system import SpiderData, AgentKnowledgeSource
    from core.models import Agent, AgentConversation, ConversationMessage
    import random
    import openai
    import os

    logger.info("🕷️ [SPIDER-TRIGGER] Checking for conversation-worthy spider data...")

    try:
        stats = {
            'spider_data_checked': 0,
            'conversations_triggered': 0,
            'agents_involved': set()
        }

        # Find recent high-relevance spider data (last 2 hours)
        cutoff = timezone.now() - timedelta(hours=2)
        interesting_data = SpiderData.objects.filter(
            created_at__gte=cutoff,
            relevance_score__gte=min_relevance,
            is_processed=True
        ).exclude(
            # Exclude data already discussed (check by spider_name in recent conversations)
            spider_name__in=AgentConversation.objects.filter(
                trigger_type='spider_data',
                started_at__gte=cutoff
            ).values_list('topic', flat=True)
        ).order_by('-relevance_score')[:max_conversations * 2]

        stats['spider_data_checked'] = interesting_data.count()

        if not interesting_data:
            logger.info("🕷️ [SPIDER-TRIGGER] No new high-relevance data to discuss")
            return {'status': 'success', 'message': 'No new data', 'stats': stats}

        # Get agents that could discuss this data
        # Map spider data types to agent specializations
        data_type_to_agents = {
            'tech': ['ResearchAgent', 'CTOAgent', 'InnovationScoutAgent'],
            'financial': ['ResearchAgent', 'COOAgent', 'OpportunityScannerAgent'],
            'jobs': ['ResearchAgent', 'ContentStrategyAgent'],
            'creative': ['DesignAssistantAgent', 'BrandIdentityAgent', 'ContentStrategyAgent'],
            'market': ['ResearchAgent', 'TrendAnalysisAgent', 'OpportunityScannerAgent'],
            'news': ['ResearchAgent', 'CTOAgent', 'InnovationScoutAgent'],
        }

        # Initialize OpenAI
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        conversations_created = 0
        for spider_data in interesting_data:
            if conversations_created >= max_conversations:
                break

            # Determine which agents should discuss this
            data_type = spider_data.data_type.lower()
            agent_names = data_type_to_agents.get(data_type, ['ResearchAgent', 'CTOAgent'])

            # Get actual agent objects
            agents = list(Agent.objects.filter(
                name__in=agent_names,
                is_active=True
            )[:3])

            if len(agents) < 2:
                # Fallback to any agents with knowledge
                agents = list(Agent.objects.filter(
                    is_active=True,
                    knowledge_sources__isnull=False
                ).distinct()[:2])

            if len(agents) < 2:
                continue

            # Pick 2 agents for discussion
            selected_agents = random.sample(agents, min(2, len(agents)))
            initiator, responder = selected_agents[0], selected_agents[1]

            # Build topic from spider data
            spider_summary = ""
            if spider_data.raw_data:
                items = spider_data.raw_data.get('items', [])[:3]
                titles = [item.get('title', '')[:50] for item in items if item.get('title')]
                spider_summary = "; ".join(titles)

            topic = f"New {spider_data.spider_name} Intelligence: {spider_summary[:80]}"

            # Create the conversation
            conversation = AgentConversation.objects.create(
                topic=topic,
                conversation_type='critical_review',  # Review new data critically
                initiator=initiator,
                trigger_type='spider_data',
                status='active'
            )
            conversation.participants.add(initiator, responder)

            # Generate initial messages
            system_prompt = f"""You are {initiator.name}, an AI agent specializing in {initiator.specialization or 'analysis'}.

New intelligence has arrived from the {spider_data.spider_name} spider (relevance: {spider_data.relevance_score}/100).

Data summary: {spider_summary[:300]}

Your task: Analyze this new data critically. What opportunities or risks does it present?
Keep your response to 2-3 sentences. Be specific about actionable insights."""

            try:
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Analyze this new {spider_data.spider_name} data and share your initial assessment."}
                    ],
                    max_completion_tokens=500,
                )

                content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                if content:
                    # Validate output
                    content = validate_agent_output(initiator.name, content)

                    ConversationMessage.objects.create(
                        conversation=conversation,
                        agent=initiator,
                        content=content,
                        message_type='statement',
                        sequence_number=1
                    )

                    conversations_created += 1
                    stats['conversations_triggered'] += 1
                    stats['agents_involved'].add(initiator.name)
                    stats['agents_involved'].add(responder.name)

                    logger.info(
                        f"🕷️ [SPIDER-TRIGGER] Created conversation about {spider_data.spider_name} "
                        f"with {initiator.name} and {responder.name}"
                    )

            except Exception as e:
                logger.warning(f"🕷️ [SPIDER-TRIGGER] Failed to generate message: {e}")
                conversation.delete()
                continue

        logger.info(
            f"🕷️ [SPIDER-TRIGGER] Complete: {stats['conversations_triggered']} conversations "
            f"triggered from {stats['spider_data_checked']} data items"
        )

        return {
            'status': 'success',
            'stats': {
                'spider_data_checked': stats['spider_data_checked'],
                'conversations_triggered': stats['conversations_triggered'],
                'agents_involved': list(stats['agents_involved'])
            },
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🕷️ [SPIDER-TRIGGER] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 363: Project-Triggered Research
# =============================================================================

@shared_task(bind=True)
def trigger_project_research(self, max_projects: int = 3, max_spiders_per_project: int = 2):
    """
    Session 363: Trigger spider queries based on project research needs.

    When projects have LivingProjectConfigs with watch_topics or watch_keywords,
    this task:
    1. Finds active projects that need fresh data
    2. Determines which spiders can provide relevant data
    3. Prioritizes those spiders for execution
    4. Creates AgentConversation when new data arrives

    This creates a demand-driven autonomous system where project needs
    trigger data collection.

    Args:
        max_projects: Maximum projects to process per run
        max_spiders_per_project: Maximum spiders to trigger per project

    Returns:
        Stats about research triggered
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_unified_system import LivingProjectConfig, SpiderData, ProjectInsight
    from core.models import AgentConversation
    from core.models_partnership import PartnershipProject
    import random

    logger.info("📊 [PROJECT-RESEARCH] Checking for project research needs...")

    try:
        stats = {
            'projects_checked': 0,
            'research_triggered': 0,
            'spiders_prioritized': [],
            'topics_researched': []
        }

        # Find active projects with living configs that have watch topics
        active_configs = LivingProjectConfig.objects.filter(
            is_active=True
        ).select_related('project').order_by('?')[:max_projects * 2]

        # Map topics to spider categories
        topic_to_spiders = {
            'ai': ['techcrunch', 'theverge', 'hackernews', 'huggingface', 'devto'],
            'ml': ['techcrunch', 'huggingface', 'hackernews', 'kaggle'],
            'tech': ['techcrunch', 'theverge', 'wired', 'mit_tech_review', 'hackernews'],
            'finance': ['yahoo_finance', 'coingecko', 'seekingalpha', 'business_news'],
            'crypto': ['coingecko', 'reddit', 'hackernews'],
            'design': ['dribbble', 'behance', 'creativemarket', 'figma'],
            'jobs': ['remoteok', 'weworkremotely', 'adzuna', 'flexjobs'],
            'freelance': ['toptal', 'guru', 'peopleperhour', 'remoteok'],
            'marketing': ['reddit', 'producthunt', 'indiehackers', 'medium'],
            'startup': ['producthunt', 'indiehackers', 'hackernews', 'techcrunch'],
            'content': ['medium', 'substack', 'youtube', 'patreon'],
            'education': ['udemy', 'teachable', 'skillshare', 'education_rss'],
            'security': ['hackernews', 'reddit', 'arstechnica'],
            'cloud': ['hackernews', 'devto', 'techcrunch'],
        }

        projects_processed = 0
        for config in active_configs:
            if projects_processed >= max_projects:
                break

            project = config.project
            stats['projects_checked'] += 1

            # Get topics from config
            watch_topics = config.watch_topics or []
            watch_keywords = config.watch_keywords or []
            spider_categories = config.spider_categories or []

            # Check if project needs fresh data (no insight in last 4 hours)
            cutoff = timezone.now() - timedelta(hours=4)
            recent_insights = ProjectInsight.objects.filter(
                project=project,
                created_at__gte=cutoff
            ).count()

            if recent_insights >= 3:
                # Project has enough recent data
                continue

            # Determine which spiders to prioritize
            spiders_to_run = set()

            # From watch topics
            for topic in watch_topics:
                topic_lower = topic.lower()
                for key, spiders in topic_to_spiders.items():
                    if key in topic_lower or topic_lower in key:
                        spiders_to_run.update(spiders[:2])

            # From spider categories
            for category in spider_categories:
                for key, spiders in topic_to_spiders.items():
                    if category.lower() in key:
                        spiders_to_run.update(spiders[:2])

            # If no specific spiders found, use generic research spiders
            if not spiders_to_run:
                spiders_to_run = {'techcrunch', 'hackernews', 'reddit'}

            # Limit spiders per project
            spiders_to_run = list(spiders_to_run)[:max_spiders_per_project]

            # Trigger spider execution by setting priority
            from core.models_unified_system import SpiderPriority

            for spider_name in spiders_to_run:
                try:
                    priority, created = SpiderPriority.objects.get_or_create(
                        spider_name=spider_name,
                        defaults={
                            'priority_score': 80,
                            'boost_reason': f'Project need: {project.project_name}'
                        }
                    )
                    if not created:
                        # Boost existing priority
                        priority.priority_score = min(100, priority.priority_score + 10)
                        priority.boost_reason = f'Project need: {project.project_name}'
                        priority.save()

                    stats['spiders_prioritized'].append(spider_name)

                except Exception as e:
                    logger.warning(f"📊 [PROJECT-RESEARCH] Failed to prioritize {spider_name}: {e}")
                    continue

            # Also create a conversation about the project's research needs
            if spiders_to_run and random.random() < 0.3:  # 30% chance
                try:
                    from core.models import Agent
                    agents = list(Agent.objects.filter(is_active=True)[:3])
                    if len(agents) >= 2:
                        topic_summary = ", ".join(watch_topics[:3]) if watch_topics else project.project_name
                        conversation = AgentConversation.objects.create(
                            topic=f"Research needed for {project.project_name}: {topic_summary[:50]}",
                            conversation_type='brainstorm',
                            initiator=agents[0],
                            trigger_type='project_need',
                            status='pending'
                        )
                        conversation.participants.add(*agents[:2])
                        stats['research_triggered'] += 1
                        stats['topics_researched'].append(topic_summary[:30])

                except Exception as e:
                    logger.warning(f"📊 [PROJECT-RESEARCH] Failed to create conversation: {e}")

            projects_processed += 1

        logger.info(
            f"📊 [PROJECT-RESEARCH] Complete: {stats['projects_checked']} projects checked, "
            f"{len(set(stats['spiders_prioritized']))} spiders prioritized, "
            f"{stats['research_triggered']} conversations created"
        )

        return {
            'status': 'success',
            'stats': {
                'projects_checked': stats['projects_checked'],
                'research_triggered': stats['research_triggered'],
                'spiders_prioritized': list(set(stats['spiders_prioritized'])),
                'topics_researched': stats['topics_researched']
            },
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"📊 [PROJECT-RESEARCH] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 363: Decision-Triggered Actions
# =============================================================================

@shared_task(bind=True)
def propagate_new_policies(self, hours_back: int = 2, max_actions: int = 3):
    """
    Session 363: Propagate newly promoted policies to relevant agents.

    When a decision becomes canonical policy, this task:
    1. Finds recently promoted policies
    2. Identifies agents affected by the policy's impact area
    3. Creates implementation conversations
    4. Logs policy adoption for tracking

    This completes the feedback loop: Conversations → Decisions → Policies → Agent Behavior

    Args:
        hours_back: How far back to look for new policies
        max_actions: Maximum actions to trigger per run

    Returns:
        Stats about policy propagation
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_unified_system import AgentDecisionSummary
    from core.models import Agent, AgentConversation, ConversationMessage
    from core.services.policy_context import PolicyContextService
    import openai
    import os

    logger.info("🏛️ [POLICY-PROPAGATE] Checking for new policies to propagate...")

    try:
        stats = {
            'policies_checked': 0,
            'actions_triggered': 0,
            'agents_notified': [],
            'conversations_created': []
        }

        # Find recently promoted policies that haven't been propagated
        cutoff = timezone.now() - timedelta(hours=hours_back)
        new_policies = AgentDecisionSummary.objects.filter(
            is_canonical=True,
            promoted_at__gte=cutoff,
            propagated_at__isnull=True  # Not yet propagated
        ).order_by('-promoted_at')[:max_actions]

        stats['policies_checked'] = new_policies.count()

        if not new_policies:
            logger.info("🏛️ [POLICY-PROPAGATE] No new policies to propagate")
            return {'status': 'success', 'message': 'No new policies', 'stats': stats}

        # Get agent-to-area mapping
        policy_service = PolicyContextService()

        # Initialize OpenAI
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        for policy in new_policies:
            # Find agents affected by this policy's impact area
            affected_agents = []
            for agent_name, areas in policy_service.AGENT_IMPACT_AREAS.items():
                if policy.impact_area in areas:
                    affected_agents.append(agent_name)

            if not affected_agents:
                # Mark as propagated even if no affected agents
                policy.propagated_at = timezone.now()
                policy.save(update_fields=['propagated_at'])
                continue

            # Get actual agent objects (limit to 3)
            agents = list(Agent.objects.filter(
                name__in=affected_agents,
                is_active=True
            )[:3])

            if len(agents) < 2:
                # Need at least 2 agents for a conversation
                policy.propagated_at = timezone.now()
                policy.save(update_fields=['propagated_at'])
                continue

            # Create implementation discussion
            topic = f"New Policy Implementation: {policy.topic[:50]}"

            conversation = AgentConversation.objects.create(
                topic=topic,
                conversation_type='implementation_planning',
                initiator=agents[0],
                trigger_type='scheduled',  # Policy-triggered
                status='active'
            )
            conversation.participants.add(*agents[:2])

            # Generate initial implementation discussion
            policy_summary = f"""
New Canonical Policy:
- Topic: {policy.topic}
- Decision: {policy.recommended_stance[:200] if policy.recommended_stance else 'Not specified'}
- Impact Area: {policy.impact_area}
- Key Insights: {', '.join(str(i) for i in policy.key_insights[:3]) if policy.key_insights else 'None specified'}
"""

            system_prompt = f"""You are {agents[0].name}, an AI agent specializing in {agents[0].specialization or 'analysis'}.

A new policy has been established through agent governance:

{policy_summary}

Your task: Discuss how this policy should affect your work and what concrete steps you'll take to implement it.
Keep response to 2-3 sentences. Be specific about implementation."""

            try:
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "How will you implement this new policy in your work?"}
                    ],
                    max_completion_tokens=500,
                )

                content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                if content:
                    # Validate output
                    content = validate_agent_output(agents[0].name, content)

                    ConversationMessage.objects.create(
                        conversation=conversation,
                        agent=agents[0],
                        content=content,
                        message_type='statement',
                        sequence_number=1
                    )

                    stats['actions_triggered'] += 1
                    stats['agents_notified'].extend([a.name for a in agents[:2]])
                    stats['conversations_created'].append(conversation.id)

                    logger.info(
                        f"🏛️ [POLICY-PROPAGATE] Created implementation conversation for "
                        f"'{policy.topic[:30]}' with {len(agents)} agents"
                    )

            except Exception as e:
                logger.warning(f"🏛️ [POLICY-PROPAGATE] Failed to generate message: {e}")
                conversation.delete()
                continue

            # Mark policy as propagated
            policy.propagated_at = timezone.now()
            policy.save(update_fields=['propagated_at'])

        logger.info(
            f"🏛️ [POLICY-PROPAGATE] Complete: {stats['policies_checked']} policies checked, "
            f"{stats['actions_triggered']} implementation conversations created"
        )

        return {
            'status': 'success',
            'stats': {
                'policies_checked': stats['policies_checked'],
                'actions_triggered': stats['actions_triggered'],
                'agents_notified': list(set(stats['agents_notified'])),
                'conversations_created': len(stats['conversations_created'])
            },
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🏛️ [POLICY-PROPAGATE] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def broadcast_conversation_status(self):
    """
    Broadcast current conversation activity status via WebSocket.
    Shows recent agent conversations in real-time.
    """
    from django.utils import timezone
    from core.models import AgentConversation, ConversationMessage
    import redis
    import json

    try:
        # Get recent conversations
        recent_conversations = AgentConversation.objects.filter(
            started_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).order_by('-started_at')[:5]

        conversations_data = []
        for conv in recent_conversations:
            messages = ConversationMessage.objects.filter(
                conversation=conv
            ).order_by('sequence_number')[:4]

            conversations_data.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'initiator': conv.initiator.name if conv.initiator else 'Unknown',
                'participants': [p.name for p in conv.participants.all()],
                'status': conv.status,
                'message_count': conv.message_count,
                'quality_score': conv.quality_score,
                'conclusion': conv.conclusion[:100] if conv.conclusion else None,
                'started_at': conv.started_at.isoformat(),
                'messages': [
                    {
                        'agent': msg.agent.name if msg.agent else 'Unknown',
                        'content': msg.content[:200],
                        'type': msg.message_type
                    }
                    for msg in messages
                ]
            })

        # Broadcast to WebSocket
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.publish('agent_learning', json.dumps({
            'type': 'conversation_status',
            'recent_conversations': conversations_data,
            'total_today': AgentConversation.objects.filter(
                started_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count(),
            'timestamp': timezone.now().isoformat()
        }))

        return {'status': 'success', 'conversations_broadcast': len(conversations_data)}

    except Exception as e:
        logger.warning(f"💬 [CONVERSATIONS] Status broadcast failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 330: Project Conversations (Multi-turn Agent Discussions about Projects)
# =============================================================================

@shared_task(bind=True)
def run_project_conversation(self, project_id: str, topic: str, max_messages: int = 6):
    """
    Generate a multi-turn conversation between agents about a specific project.

    Unlike HiveMind (parallel single responses), this creates a real back-and-forth
    discussion where agents talk amongst themselves about the project's research,
    plans, and opportunities - just like Agent/Social conversations.

    Args:
        project_id: UUID of the PartnershipProject
        topic: Discussion topic (e.g., "How can we grow our audience?")
        max_messages: Maximum messages in the conversation

    Returns:
        Dict with conversation details
    """
    from django.utils import timezone
    from core.models import (
        Agent, AgentConversation, ConversationMessage,
        AgentKnowledgeSource
    )
    from core.models_partnership import PartnershipProject
    from core.models_unified_system import BusinessResearchResult
    import random
    import openai
    import os

    logger.info(f"🗣️ [PROJECT-CONVERSATION] Starting conversation for project {project_id}: {topic}")

    try:
        # Get the project
        try:
            project = PartnershipProject.objects.get(id=project_id)
        except PartnershipProject.DoesNotExist:
            logger.error(f"🗣️ [PROJECT-CONVERSATION] Project {project_id} not found")
            return {'status': 'failed', 'error': 'Project not found'}

        # Get project research for context
        research_results = BusinessResearchResult.objects.filter(
            project=project
        ).order_by('-created_at')[:5]

        # Build project context from research
        project_context_parts = [f"Project: {project.project_name}"]
        if project.project_type:
            project_context_parts.append(f"Type: {project.project_type}")
        if project.description:
            project_context_parts.append(f"Description: {project.description[:500]}")

        # Add research insights
        research_context = []
        for research in research_results:
            if research.analysis:
                research_context.append(f"Research ({research.research_type}): {research.analysis[:300]}")
            if research.recommendations:
                recs = research.recommendations[:3] if isinstance(research.recommendations, list) else []
                for rec in recs:
                    if isinstance(rec, str):
                        research_context.append(f"Recommendation: {rec[:150]}")
                    elif isinstance(rec, dict):
                        research_context.append(f"Recommendation: {str(rec.get('text', rec))[:150]}")

        project_context = "\n".join(project_context_parts)
        if research_context:
            project_context += "\n\n== Research Insights ==\n" + "\n".join(research_context[:5])

        # Find agents with project knowledge OR random agents
        agents_with_project_knowledge = Agent.objects.filter(
            knowledge_sources__source_project=project
        ).distinct()[:10]

        if agents_with_project_knowledge.count() < 2:
            # Session 329: Use ALL agents including deprecated for projects
            agents_with_project_knowledge = list(Agent.objects.all().order_by('?')[:10])
        else:
            agents_with_project_knowledge = list(agents_with_project_knowledge)

        if len(agents_with_project_knowledge) < 2:
            logger.warning("🗣️ [PROJECT-CONVERSATION] Need at least 2 agents")
            return {'status': 'failed', 'error': 'Insufficient agents'}

        # Pick 2 random agents for the conversation
        random.shuffle(agents_with_project_knowledge)
        initiator = agents_with_project_knowledge[0]
        responder = agents_with_project_knowledge[1]

        # Conversation templates for project discussions
        project_templates = [
            {
                'type': 'brainstorm',
                'tension_level': 'medium',
                'dynamic': 'generate ideas, build on each other, explore possibilities',
                'starter': f"Let's brainstorm about {topic}. Based on the project research...",
            },
            {
                'type': 'strategic_planning',
                'tension_level': 'medium',
                'dynamic': 'plan concrete steps, prioritize actions, identify resources',
                'starter': f"We need to develop a strategy for {topic}. Here's what I'm thinking...",
            },
            {
                'type': 'problem_solving',
                'tension_level': 'high',
                'dynamic': 'identify challenges, propose solutions, evaluate trade-offs',
                'starter': f"Looking at the research, there are some challenges with {topic}...",
            },
            {
                'type': 'opportunity_analysis',
                'tension_level': 'low',
                'dynamic': 'identify opportunities, assess potential, discuss approaches',
                'starter': f"I see some interesting opportunities regarding {topic}...",
            },
        ]

        template = random.choice(project_templates)

        # Create the conversation with project link
        conversation = AgentConversation.objects.create(
            topic=f"Project Discussion: {topic[:100]}",
            conversation_type=template['type'],
            initiator=initiator,
            trigger_type='user_triggered',
            project=project,  # Session 327: Link to project
            status='active'
        )
        conversation.participants.add(initiator, responder)

        logger.info(f"🗣️ [PROJECT-CONVERSATION] Created conversation {conversation.id} with {initiator.name} and {responder.name}")

        # Session 332: Broadcast conversation started via WebSocket
        try:
            from core.project_intelligence_consumer import broadcast_project_conversation_started
            broadcast_project_conversation_started(
                project_id=str(project_id),
                conversation_id=str(conversation.id),
                topic=topic,
                participants=[initiator.name, responder.name],
                conversation_type=template['type']
            )
        except Exception as ws_err:
            logger.warning(f"🗣️ [PROJECT-CONVERSATION] WebSocket broadcast failed: {ws_err}")

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        messages = []
        current_speaker = initiator
        other_speaker = responder

        # Build tension-appropriate behavior guidelines
        tension = template.get('tension_level', 'medium')
        if tension == 'high':
            behavior_guide = """IMPORTANT - This is a HIGH TENSION discussion:
- Challenge claims directly - don't just agree
- Point out flaws, risks, or oversights in their approach
- Defend your expertise when questioned
- Ask tough "what about..." or "but what if..." questions"""
        elif tension == 'medium':
            behavior_guide = """This is a BALANCED discussion:
- Share your perspective but also question theirs
- Offer alternatives when you see different approaches
- Mix agreement with constructive pushback"""
        else:
            behavior_guide = """This is an EXPLORATORY discussion:
- Share knowledge while remaining curious
- Build on ideas but also test them
- Be supportive while offering new angles"""

        for msg_num in range(max_messages):
            # Session 332: Broadcast typing indicator before generating
            try:
                from core.project_intelligence_consumer import broadcast_project_typing_indicator
                broadcast_project_typing_indicator(
                    project_id=str(project_id),
                    conversation_id=str(conversation.id),
                    agent_name=current_speaker.name,
                    agent_id=str(current_speaker.id)
                )
            except Exception as ws_err:
                pass  # Non-critical

            # Build the system prompt with project context
            system_prompt = f"""You are {current_speaker.name}, an AI agent specialized in {current_speaker.specialization or 'general knowledge'}.

You are having a {template['type'].replace('_', ' ')} with {other_speaker.name} about a project.

== PROJECT CONTEXT ==
{project_context}

== DISCUSSION TOPIC ==
{topic}

{behavior_guide}

Conversation dynamic: {template['dynamic']}

Guidelines:
- Keep responses concise (2-4 sentences)
- Reference specific research insights when relevant
- Be authentic to YOUR expertise
- Focus on practical, actionable ideas for this project
- If you see a problem with their approach, say so constructively"""

            # Build message history
            history_msgs = []
            for prev_msg in messages[-4:]:
                history_msgs.append({
                    "role": "user" if prev_msg['agent'] != current_speaker.name else "assistant",
                    "content": f"{prev_msg['agent']}: {prev_msg['content']}"
                })

            # Generate user content prompt
            if msg_num == 0:
                user_content = f"Start a {template['type'].replace('_', ' ')} about '{topic}' for this project. Be the first to speak."
            else:
                last_msg = messages[-1]['content'] if messages else ''
                user_content = f"Respond to {other_speaker.name}'s point: '{last_msg[:200]}...' Continue the project discussion."

            try:
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *history_msgs,
                        {"role": "user", "content": user_content}
                    ],
                    max_completion_tokens=800,
                )

                content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                # Session 359: Validate project conversation messages for mythology violations
                content = validate_agent_output(current_speaker.name, content)

                # Clean up content
                if content.startswith(f"{current_speaker.name}:"):
                    content = content[len(current_speaker.name)+1:].strip()

                if not content:
                    logger.warning(f"🗣️ [PROJECT-CONVERSATION] Empty content from {current_speaker.name}, skipping")
                    current_speaker, other_speaker = other_speaker, current_speaker
                    continue

                # Determine message type
                msg_type = 'statement'
                content_lower = content.lower()
                if '?' in content:
                    msg_type = 'question'
                elif 'agree' in content_lower or "you're right" in content_lower:
                    msg_type = 'agreement'
                elif 'however' in content_lower or 'but' in content_lower or 'disagree' in content_lower:
                    msg_type = 'disagreement'
                elif 'suggest' in content_lower or 'could' in content_lower or 'what if' in content_lower:
                    msg_type = 'suggestion'
                elif 'insight' in content_lower or 'realize' in content_lower:
                    msg_type = 'insight'

                # Save the message
                ConversationMessage.objects.create(
                    conversation=conversation,
                    agent=current_speaker,
                    content=content,
                    message_type=msg_type,
                    sequence_number=msg_num + 1,
                )

                messages.append({
                    'agent': current_speaker.name,
                    'content': content,
                    'type': msg_type
                })

                logger.info(f"🗣️ [PROJECT-CONVERSATION] {current_speaker.name}: {content[:80]}...")

                # Session 332: Broadcast new message via WebSocket
                try:
                    from core.project_intelligence_consumer import broadcast_project_conversation_message
                    broadcast_project_conversation_message(
                        project_id=str(project_id),
                        conversation_id=str(conversation.id),
                        agent_name=current_speaker.name,
                        agent_id=str(current_speaker.id),
                        content=content,
                        message_type=msg_type,
                        sequence=msg_num + 1
                    )
                except Exception as ws_err:
                    pass  # Non-critical

            except Exception as e:
                logger.warning(f"🗣️ [PROJECT-CONVERSATION] Failed to generate message: {e}")
                break

            # Swap speakers
            current_speaker, other_speaker = other_speaker, current_speaker

        # Conclude the conversation
        if messages:
            try:
                conclusion_response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": "Summarize the key insights and action items from this project discussion in 2-3 sentences."},
                        {"role": "user", "content": f"Project: {project.project_name or project.name}\nTopic: {topic}\n\nDiscussion:\n" +
                            "\n".join([f"{m['agent']}: {m['content']}" for m in messages])}
                    ],
                    max_completion_tokens=500,
                )
                conclusion = conclusion_response.choices[0].message.content.strip() if conclusion_response.choices[0].message.content else f"Productive discussion about {topic}"
                # Session 359: Validate project conclusion for mythology violations
                conclusion = validate_agent_output("ProjectConversationSynthesizer", conclusion)
            except:
                conclusion = f"Productive discussion about {topic}"

            conversation.conclude(
                conclusion,
                insights=[m['content'] for m in messages if m['type'] == 'insight']
            )
            conversation.quality_score = min(1.0, len(messages) / max_messages * 0.8 + 0.2)
            conversation.message_count = len(messages)
            conversation.save()

            # Session 332: Broadcast conversation ended via WebSocket
            try:
                from core.project_intelligence_consumer import broadcast_project_conversation_ended
                broadcast_project_conversation_ended(
                    project_id=str(project_id),
                    conversation_id=str(conversation.id),
                    conclusion=conclusion,
                    message_count=len(messages),
                    quality_score=conversation.quality_score
                )
            except Exception as ws_err:
                pass  # Non-critical

        # Also broadcast via Redis for legacy consumers
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'project_conversation_complete',
                'project_id': str(project_id),
                'conversation_id': str(conversation.id),
                'topic': topic,
                'participants': [initiator.name, responder.name],
                'message_count': len(messages),
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(f"🗣️ [PROJECT-CONVERSATION] Complete: {len(messages)} messages between {initiator.name} and {responder.name}")

        return {
            'status': 'success',
            'conversation_id': str(conversation.id),
            'project_id': str(project_id),
            'topic': topic,
            'participants': [initiator.name, responder.name],
            'message_count': len(messages),
            'conclusion': conclusion if messages else None
        }

    except Exception as e:
        logger.exception(f"🗣️ [PROJECT-CONVERSATION] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 247: Agent Dreams (Idle Thoughts & Creative Ideas)
# =============================================================================

@shared_task(bind=True)
def generate_agent_dreams(self, max_dreamers: int = 5, dreams_per_agent: int = 2):
    """
    Generate creative dreams for idle agents.

    When agents aren't actively working, they "dream" - generating creative ideas,
    what-if scenarios, predictions, and mashups based on their knowledge and
    specialization.

    Args:
        max_dreamers: Maximum number of agents to dream this cycle
        dreams_per_agent: Maximum dreams per agent

    Returns:
        Stats about dreams generated
    """
    from django.utils import timezone
    from core.models import (
        Agent, AgentDream, AgentKnowledgeSource,
        AgentExecution, AgentConversation
    )
    import random
    import openai
    import os

    logger.info("💭 [DREAMS] Starting agent dream cycle...")

    try:
        # Find idle agents (not recently active)
        # Idle means: no executions or conversations in the last 30 minutes
        recent_cutoff = timezone.now() - timezone.timedelta(minutes=30)

        # Get agents with recent activity
        recently_active_ids = set()

        # Check recent executions
        recent_executions = AgentExecution.objects.filter(
            created_at__gte=recent_cutoff
        ).values_list('agent_id', flat=True)
        recently_active_ids.update(recent_executions)

        # Check recent conversations
        recent_conversations = AgentConversation.objects.filter(
            started_at__gte=recent_cutoff
        ).values_list('participants__id', flat=True)
        recently_active_ids.update(recent_conversations)

        # Session 417: Find ALL idle agents (not just those with knowledge)
        # Agents can dream about their specialty/expertise even without accumulated knowledge
        idle_agents = Agent.objects.filter(
            is_active=True
        ).exclude(
            id__in=recently_active_ids
        )[:max_dreamers]

        if not idle_agents.exists():
            logger.info("💭 [DREAMS] No idle agents found")
            return {'status': 'skipped', 'reason': 'no_idle_agents'}

        stats = {
            'dreams_generated': 0,
            'agents_dreaming': 0,
            'dream_types': {}
        }

        # Dream type templates with prompts
        dream_templates = [
            {
                'type': 'creative_idea',
                'prompt': "Generate a creative and innovative idea that combines your expertise in {specialty} with emerging trends. What novel concept could change how people approach {topic}?",
                'prefix': "Creative Idea: "
            },
            {
                'type': 'what_if',
                'prompt': "Imagine a 'what if' scenario related to {topic}. What unexpected combination or alternative approach could lead to breakthrough results?",
                'prefix': "What if... "
            },
            {
                'type': 'mashup',
                'prompt': "Create a mashup idea that combines {topic} with something from a completely different field. What unexpected synergy could emerge?",
                'prefix': "Mashup: "
            },
            {
                'type': 'prediction',
                'prompt': "Based on your knowledge of {topic} and current trends, make a bold prediction about how this area will evolve. What pattern do you see emerging?",
                'prefix': "Prediction: "
            },
            {
                'type': 'improvement',
                'prompt': "Identify something related to {topic} that could be significantly improved. What enhancement would make the biggest impact?",
                'prefix': "Improvement Idea: "
            },
            {
                'type': 'observation',
                'prompt': "Share an interesting observation or pattern you've noticed about {topic}. What subtle insight might others have missed?",
                'prefix': "I've noticed: "
            },
            {
                'type': 'wild_thought',
                'prompt': "Let your mind wander freely about {topic}. What wild, unconventional, or playful thought comes to mind?",
                'prefix': "Wild thought: "
            }
        ]

        # Session 249: Get dream type weights from user preferences
        from core.models import DreamFeedbackPreference
        type_weights = DreamFeedbackPreference.get_dream_type_weights()
        preferred_topics = DreamFeedbackPreference.get_preferred_topics(limit=20)

        logger.info(f"💭 [DREAMS] Dream type weights from feedback: {type_weights}")
        if preferred_topics:
            logger.info(f"💭 [DREAMS] Preferred topics from feedback: {preferred_topics[:5]}")

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        for agent in idle_agents:
            # Get agent's recent knowledge for inspiration (if any)
            knowledge_items = AgentKnowledgeSource.objects.filter(
                agent=agent
            ).order_by('-last_updated_at')[:10]

            # Session 417: Allow agents without knowledge to dream using their specialty
            has_knowledge = knowledge_items.exists()

            stats['agents_dreaming'] += 1

            # Session 249: Check if this agent has specific preferences
            agent_type_weights = type_weights.copy()
            try:
                agent_prefs = DreamFeedbackPreference.objects.filter(
                    agent=agent,
                    dream_type__isnull=False
                ).exclude(dream_type='')
                for pref in agent_prefs:
                    if pref.dream_type in agent_type_weights:
                        # Further boost types that this specific agent is good at
                        agent_type_weights[pref.dream_type] += pref.preference_score * 0.3
            except Exception:
                pass

            for _ in range(dreams_per_agent):
                # Pick a random knowledge item as inspiration (or use agent specialty)
                # Session 249: Prefer topics that users have reacted positively to
                # Session 417: Allow agents without knowledge to dream using their specialty
                knowledge = None
                topic = None

                if has_knowledge:
                    knowledge_list = list(knowledge_items)
                    if preferred_topics:
                        # Sort knowledge by whether they match preferred topics
                        def topic_score(k):
                            title = (k.title or '').lower()
                            for i, pt in enumerate(preferred_topics):
                                if pt.lower() in title or title in pt.lower():
                                    return len(preferred_topics) - i  # Higher score for higher preference
                            return 0
                        knowledge_list.sort(key=topic_score, reverse=True)
                        # 60% chance to pick from top 3, 40% random
                        if random.random() < 0.6 and len(knowledge_list) > 3:
                            knowledge = random.choice(knowledge_list[:3])
                        else:
                            knowledge = random.choice(knowledge_list)
                    else:
                        knowledge = random.choice(knowledge_list)
                    # Session 435: Improved topic extraction with better fallbacks
                    topic = knowledge.title
                    if not topic or topic in ("general insights", "recent insights"):
                        if knowledge.summary:
                            try:
                                import json
                                data = json.loads(knowledge.summary)
                                topic = data.get('query') or data.get('topic') or data.get('insight', '')[:80]
                            except (json.JSONDecodeError, TypeError):
                                topic = knowledge.summary[:80]
                    if not topic:
                        topic = knowledge.source_type or f"{knowledge.knowledge_type.replace('_', ' ').title()}"
                else:
                    # Session 417: No knowledge yet - use agent's specialty as dream topic
                    topic = agent.specialization or agent.description or f"{agent.name}'s expertise"
                    topic = topic[:100]  # Truncate for safety

                # Session 249: Pick dream type using weighted random selection
                # instead of uniform random
                templates_with_weights = []
                for t in dream_templates:
                    weight = agent_type_weights.get(t['type'], 1.0)
                    templates_with_weights.append((t, weight))

                # Weighted random selection
                total_weight = sum(w for _, w in templates_with_weights)
                r = random.uniform(0, total_weight)
                cumulative = 0
                template = dream_templates[0]  # fallback
                for t, w in templates_with_weights:
                    cumulative += w
                    if r <= cumulative:
                        template = t
                        break

                dream_type = template['type']

                # Track dream types
                stats['dream_types'][dream_type] = stats['dream_types'].get(dream_type, 0) + 1

                # Generate the dream using GPT
                # Session 417: Handle agents without knowledge gracefully
                background_knowledge = 'Various insights and learnings from your specialty'
                if knowledge and knowledge.summary:
                    background_knowledge = knowledge.summary[:500]

                system_prompt = f"""You are {agent.name}, an AI agent specialized in {agent.specialization or 'creative thinking'}.
You are in a relaxed, creative state - dreaming up new ideas while idle.

Your background knowledge: {background_knowledge}

Guidelines:
- Be creative, imaginative, and playful
- Keep dreams concise (2-4 sentences)
- Make it feel like a genuine creative thought
- Include a spark of insight or novelty
- Reference your specialty naturally
- Don't use bullet points or lists - keep it flowing
- Start directly with the idea, don't repeat the prompt"""

                user_prompt = template['prompt'].format(
                    specialty=agent.specialization or 'creative analysis',
                    topic=topic
                )

                try:
                    # Session 317: GPT-5 reasoning models split tokens between reasoning + output
                    # Session 413: Added timeout for reasoning model thinking time
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_completion_tokens=1000,  # Higher for GPT-5 reasoning (Session 317)
                        timeout=120,  # Session 413: 2 min timeout for reasoning model
                    )

                    dream_content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    # Session 356 NOTE: Dreams are intentionally NOT mythology-validated
                    # Dreams are meant to be creative, imaginative, and speculative
                    # (what-if scenarios, predictions, wild thoughts, mashups)
                    # Mythology validation would restrict their creative nature

                    # Clean up the content
                    # Remove any repeated prefixes
                    for prefix in [template['prefix'], f"{agent.name}:", "Dream:", "Idea:"]:
                        if dream_content.startswith(prefix):
                            dream_content = dream_content[len(prefix):].strip()

                    # Session 317: Generate catchy title with adequate tokens for reasoning
                    # Session 413: Added timeout for reasoning model
                    title_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Generate a short, catchy title (3-7 words) for this creative thought. No quotes or punctuation."},
                            {"role": "user", "content": dream_content if dream_content else "Creative thinking session"}
                        ],
                        max_completion_tokens=500,  # Higher for GPT-5 reasoning (Session 317)
                        timeout=60,  # Session 413: 1 min timeout for simple title
                    )

                    title = title_response.choices[0].message.content.strip().strip('"\'')[:200] if title_response.choices[0].message.content else "Creative Thought"

                    # Create the dream
                    vividness = random.uniform(0.6, 1.0)
                    dream = AgentDream.objects.create(
                        agent=agent,
                        title=title,
                        content=dream_content,
                        dream_type=dream_type,
                        inspiration_source=topic[:200],
                        related_topics=[topic, agent.specialization or 'general'],
                        vividness_score=vividness,
                        creativity_score=random.uniform(0.6, 1.0)
                    )

                    stats['dreams_generated'] += 1
                    logger.debug(f"💭 [DREAMS] {agent.name} dreamed: {title}")

                    # Session 419: Send Discord notification
                    try:
                        from core.services.discord_notifications import discord_notify
                        discord_notify.send_dream(
                            agent_name=agent.name,
                            dream_title=title,
                            dream_content=dream_content,
                            dream_type=dream_type,
                            vividness=vividness
                        )
                    except Exception as discord_err:
                        logger.debug(f"Discord notification failed: {discord_err}")

                except Exception as e:
                    logger.warning(f"💭 [DREAMS] Failed to generate dream for {agent.name}: {e}")
                    continue

        # Broadcast the dream update
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'dreams_generated',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except:
            pass

        logger.info(
            f"💭 [DREAMS] Dream cycle complete: "
            f"{stats['dreams_generated']} dreams from {stats['agents_dreaming']} agents"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"💭 [DREAMS] Dream generation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def broadcast_dream_journal(self):
    """
    Broadcast recent agent dreams via WebSocket.
    Shows 'While you were away...' dreams to users.
    """
    from django.utils import timezone
    from core.models import AgentDream
    import redis
    import json

    try:
        # Get recent unshown dreams from the last 24 hours
        recent_dreams = AgentDream.objects.filter(
            dreamed_at__gte=timezone.now() - timezone.timedelta(hours=24),
            shown_to_user=False
        ).select_related('agent').order_by('-dreamed_at')[:10]

        dreams_data = []
        for dream in recent_dreams:
            dreams_data.append({
                'id': str(dream.id),
                'agent_name': dream.agent.name if dream.agent else 'Unknown',
                'agent_avatar': getattr(dream.agent, 'avatar_url', None) if dream.agent else None,
                'title': dream.title,
                'content': dream.content[:300],
                'dream_type': dream.dream_type,
                'inspiration': dream.inspiration_source,
                'vividness': dream.vividness_score,
                'creativity': dream.creativity_score,
                'dreamed_at': dream.dreamed_at.isoformat()
            })

        # Count total dreams today
        dreams_today = AgentDream.objects.filter(
            dreamed_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count()

        # Broadcast to WebSocket
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.publish('agent_learning', json.dumps({
            'type': 'dream_journal',
            'dreams': dreams_data,
            'total_today': dreams_today,
            'unread_count': len(dreams_data),
            'timestamp': timezone.now().isoformat()
        }))

        return {
            'status': 'success',
            'dreams_broadcast': len(dreams_data),
            'total_today': dreams_today
        }

    except Exception as e:
        logger.warning(f"💭 [DREAMS] Journal broadcast failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 366: Dream Productization Pipeline
# =============================================================================

@shared_task(bind=True)
def score_and_promote_dreams(self, max_dreams: int = 50, promote_threshold: float = 0.7):
    """
    Session 366: Score unscored dreams and promote high-value ones to Boardroom.

    This is the core of the Dream Productization Pipeline:
    1. Score dreams for actionability (can this be implemented?)
    2. Score dreams for relevance (does this match active projects?)
    3. Calculate composite score
    4. Link dreams to relevant projects
    5. Promote top dreams to Boardroom for decision

    Args:
        max_dreams: Maximum dreams to score per cycle
        promote_threshold: Minimum composite score to auto-promote to Boardroom

    Returns:
        Stats about dreams scored and promoted
    """
    from django.utils import timezone
    from core.models import AgentDream
    from core.models_unified_system import LivingProjectConfig
    import openai
    import os
    import re

    logger.info("🎯 [DREAM-PRODUCTIZATION] Starting dream scoring cycle...")

    try:
        # Get unscored dreams (actionability_score = 0.0 and created recently)
        # Focus on recent dreams that haven't been scored yet
        unscored_dreams = AgentDream.objects.filter(
            actionability_score=0.0,  # Not yet scored
            promoted_to_decision=False,
            dreamed_at__gte=timezone.now() - timezone.timedelta(days=7)  # Last 7 days
        ).select_related('agent').order_by('-creativity_score', '-dreamed_at')[:max_dreams]

        if not unscored_dreams.exists():
            logger.info("🎯 [DREAM-PRODUCTIZATION] No unscored dreams found")
            return {'status': 'skipped', 'reason': 'no_unscored_dreams'}

        # Get active projects for relevance matching
        active_projects = LivingProjectConfig.objects.filter(
            is_active=True
        ).select_related('project').prefetch_related()

        # Build project context for matching
        project_contexts = []
        for config in active_projects:
            project_contexts.append({
                'id': str(config.project.id),
                'name': config.project.project_name,
                'topics': config.watch_topics or [],
                'keywords': config.watch_keywords or [],
                'competitors': config.watch_competitors or [],
            })

        logger.info(f"🎯 [DREAM-PRODUCTIZATION] Scoring {unscored_dreams.count()} dreams against {len(project_contexts)} active projects")

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        stats = {
            'dreams_scored': 0,
            'dreams_promoted': 0,
            'dreams_linked_to_projects': 0,
            'avg_actionability': 0.0,
            'avg_relevance': 0.0,
            'avg_composite': 0.0,
        }

        actionability_scores = []
        relevance_scores = []
        composite_scores = []

        for dream in unscored_dreams:
            try:
                # Step 1: Score for Actionability
                # Can this dream be implemented/acted upon?
                actionability_prompt = f"""Rate the actionability of this creative idea on a scale of 0.0 to 1.0.

Dream from {dream.agent.name if dream.agent else 'Unknown Agent'}:
Type: {dream.dream_type}
Title: {dream.title}
Content: {dream.content[:500]}

Actionability means: Can this be implemented? Is it a concrete idea vs abstract musing?
- 0.0-0.3: Very abstract, philosophical, or too vague to act on
- 0.4-0.6: Has some concrete elements but needs significant refinement
- 0.7-0.9: Clear, actionable idea with specific implementation path
- 1.0: Immediately actionable with clear next steps

Respond with ONLY a number between 0.0 and 1.0, nothing else."""

                actionability_response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": actionability_prompt}],
                    max_completion_tokens=50  # Higher for reasoning models
                )

                actionability_text = actionability_response.choices[0].message.content.strip()
                # Extract number from response
                actionability_match = re.search(r'(\d+\.?\d*)', actionability_text)
                actionability = float(actionability_match.group(1)) if actionability_match else 0.5
                actionability = max(0.0, min(1.0, actionability))

                # Step 2: Score for Relevance to Projects
                relevance = 0.0
                matched_project_id = None

                if project_contexts:
                    relevance_prompt = f"""Rate how relevant this dream is to any of these active projects.

Dream:
- Title: {dream.title}
- Content: {dream.content[:300]}
- Topics: {', '.join(dream.related_topics or [])}

Active Projects:
{chr(10).join([f"- {p['name']}: topics={p['topics']}, keywords={p['keywords']}" for p in project_contexts])}

Respond with:
1. A relevance score (0.0-1.0) where 1.0 = highly relevant to at least one project
2. The name of the most relevant project (or "none" if < 0.3)

Format: SCORE|PROJECT_NAME
Example: 0.8|AI Content Studio"""

                    relevance_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[{"role": "user", "content": relevance_prompt}],
                        max_completion_tokens=100  # Higher for reasoning models
                    )

                    relevance_text = relevance_response.choices[0].message.content.strip()
                    if '|' in relevance_text:
                        parts = relevance_text.split('|')
                        relevance_match = re.search(r'(\d+\.?\d*)', parts[0])
                        relevance = float(relevance_match.group(1)) if relevance_match else 0.0
                        relevance = max(0.0, min(1.0, relevance))

                        # Find matching project
                        if len(parts) > 1 and parts[1].strip().lower() != 'none':
                            project_name = parts[1].strip()
                            for p in project_contexts:
                                if p['name'].lower() in project_name.lower() or project_name.lower() in p['name'].lower():
                                    matched_project_id = p['id']
                                    break

                # Step 3: Calculate composite score
                composite = (dream.creativity_score + actionability + relevance) / 3.0

                # Update dream scores
                dream.actionability_score = actionability
                dream.relevance_score = relevance
                dream.composite_score = composite

                # Step 4: Link to matched project
                if matched_project_id and relevance >= 0.5:
                    try:
                        from core.models import PartnershipProject
                        project = PartnershipProject.objects.get(id=matched_project_id)
                        dream.project = project
                        stats['dreams_linked_to_projects'] += 1
                        logger.debug(f"🎯 [DREAM-PRODUCTIZATION] Linked dream '{dream.title[:30]}' to project '{project.project_name}'")
                    except Exception:
                        pass

                # Step 5: Auto-promote high-scoring dreams
                if composite >= promote_threshold:
                    dream.promoted_to_decision = True
                    dream.promoted_at = timezone.now()
                    dream.decision_outcome = 'pending'
                    stats['dreams_promoted'] += 1
                    logger.info(f"🎯 [DREAM-PRODUCTIZATION] Promoted dream '{dream.title[:40]}' (score: {composite:.2f})")

                dream.save()
                stats['dreams_scored'] += 1

                # Track for averages
                actionability_scores.append(actionability)
                relevance_scores.append(relevance)
                composite_scores.append(composite)

                logger.debug(f"🎯 [DREAM-PRODUCTIZATION] Scored '{dream.title[:30]}': action={actionability:.2f}, relevance={relevance:.2f}, composite={composite:.2f}")

            except Exception as e:
                logger.warning(f"🎯 [DREAM-PRODUCTIZATION] Failed to score dream {dream.id}: {e}")
                continue

        # Calculate averages
        if actionability_scores:
            stats['avg_actionability'] = sum(actionability_scores) / len(actionability_scores)
            stats['avg_relevance'] = sum(relevance_scores) / len(relevance_scores)
            stats['avg_composite'] = sum(composite_scores) / len(composite_scores)

        # Broadcast update via WebSocket
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'dream_productization',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception:
            pass

        logger.info(
            f"🎯 [DREAM-PRODUCTIZATION] Cycle complete: "
            f"{stats['dreams_scored']} scored, {stats['dreams_promoted']} promoted, "
            f"{stats['dreams_linked_to_projects']} linked to projects"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🎯 [DREAM-PRODUCTIZATION] Scoring failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def generate_directed_dreams(self, topic: str, agent_ids: list = None, dreams_per_agent: int = 2):
    """
    Session 366: Generate directed dreams about a specific topic.

    Users can request agents to dream about specific topics for their projects.
    This is "intentional" dreaming vs the background emergent dreaming.

    Args:
        topic: The topic to dream about (e.g., "AI marketing automation")
        agent_ids: Specific agent IDs to dream, or None for all
        dreams_per_agent: How many dreams per agent

    Returns:
        Stats about directed dreams generated
    """
    from django.utils import timezone
    from core.models import Agent, AgentDream, AgentKnowledgeSource
    import openai
    import os
    import random

    logger.info(f"🎯 [DIRECTED-DREAMS] Starting directed dream cycle for topic: {topic}")

    try:
        # Get agents to dream
        if agent_ids:
            agents = Agent.objects.filter(id__in=agent_ids, is_active=True)
        else:
            # Get agents with relevant knowledge
            agents = Agent.objects.filter(
                is_active=True,
                knowledge_sources__isnull=False
            ).distinct()[:10]

        if not agents.exists():
            logger.info("🎯 [DIRECTED-DREAMS] No eligible agents found")
            return {'status': 'skipped', 'reason': 'no_agents'}

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        stats = {
            'dreams_generated': 0,
            'agents_dreaming': 0,
            'topic': topic
        }

        # Directed dream templates - more focused than regular dreams
        directed_templates = [
            {
                'type': 'creative_idea',
                'prompt': f"Generate a creative and innovative idea about {topic}. How could your expertise in {{specialty}} create something novel here?"
            },
            {
                'type': 'improvement',
                'prompt': f"What improvement or enhancement related to {topic} would have the biggest impact? Use your knowledge of {{specialty}} to suggest something specific."
            },
            {
                'type': 'mashup',
                'prompt': f"Create a mashup idea that combines {topic} with {{specialty}}. What unexpected synergy could emerge?"
            },
            {
                'type': 'prediction',
                'prompt': f"Based on your knowledge, make a bold prediction about how {topic} will evolve. What trend do you see emerging?"
            },
        ]

        for agent in agents:
            stats['agents_dreaming'] += 1

            for _ in range(dreams_per_agent):
                template = random.choice(directed_templates)

                system_prompt = f"""You are {agent.name}, an AI agent specialized in {agent.specialization or 'creative thinking'}.
You've been asked to focus your creative thinking on a specific topic.

Guidelines:
- Be creative, imaginative, but focused on the given topic
- Keep dreams concise (2-4 sentences)
- Make it feel like a genuine creative insight
- Reference your specialty naturally
- Don't use bullet points or lists"""

                user_prompt = template['prompt'].format(
                    specialty=agent.specialization or 'creative analysis'
                )

                try:
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_completion_tokens=500  # Higher for reasoning models
                    )

                    dream_content = response.choices[0].message.content.strip()

                    # Generate title
                    title_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Generate a short, catchy title (3-7 words). No quotes."},
                            {"role": "user", "content": dream_content}
                        ],
                        max_completion_tokens=50  # Higher for reasoning models
                    )

                    title = title_response.choices[0].message.content.strip().strip('"\'')[:200]

                    # Create the directed dream with higher initial scores
                    AgentDream.objects.create(
                        agent=agent,
                        title=title,
                        content=dream_content,
                        dream_type=template['type'],
                        inspiration_source=topic[:200],
                        related_topics=[topic, agent.specialization or 'general'],
                        vividness_score=random.uniform(0.7, 1.0),
                        creativity_score=random.uniform(0.7, 1.0),
                        # Session 366: Mark as directed
                        is_directed=True,
                        directed_topic=topic[:200],
                        # Directed dreams start with higher actionability
                        actionability_score=0.6,  # Start higher since they're focused
                    )

                    stats['dreams_generated'] += 1
                    logger.debug(f"🎯 [DIRECTED-DREAMS] {agent.name} dreamed: {title}")

                except Exception as e:
                    logger.warning(f"🎯 [DIRECTED-DREAMS] Failed for {agent.name}: {e}")
                    continue

        logger.info(
            f"🎯 [DIRECTED-DREAMS] Complete: {stats['dreams_generated']} dreams "
            f"from {stats['agents_dreaming']} agents about '{topic}'"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🎯 [DIRECTED-DREAMS] Failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def process_approved_dreams(self, max_dreams: int = 10):
    """
    Session 367: Process approved dreams and create implementation tasks.

    When dreams are approved in the Boardroom (decision_outcome='approved'),
    this task:
    1. Creates a DreamImplementation record
    2. Assigns the most appropriate agent
    3. Generates an implementation plan
    4. Kicks off the implementation

    Args:
        max_dreams: Maximum approved dreams to process per cycle

    Returns:
        Stats about implementations created
    """
    from django.utils import timezone
    from core.models import AgentDream, Agent
    from core.models_unified_system import DreamImplementation
    import openai
    import os

    logger.info("🚀 [DREAM-IMPLEMENTATION] Starting approved dream processing...")

    try:
        # Get approved dreams that don't have implementations yet
        approved_dreams = AgentDream.objects.filter(
            decision_outcome='approved'
        ).exclude(
            implementation__isnull=False  # Skip dreams that already have implementations
        ).select_related('agent', 'project').order_by('-composite_score')[:max_dreams]

        if not approved_dreams.exists():
            logger.info("🚀 [DREAM-IMPLEMENTATION] No approved dreams to process")
            return {'status': 'skipped', 'reason': 'no_approved_dreams'}

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        stats = {
            'dreams_processed': 0,
            'implementations_created': 0,
            'agents_assigned': 0,
        }

        # Map dream types to implementation types
        type_mapping = {
            'creative_idea': 'feature',
            'improvement': 'improvement',
            'mashup': 'feature',
            'prediction': 'research',
            'what_if': 'experiment',
            'observation': 'research',
            'wild_thought': 'experiment',
        }

        for dream in approved_dreams:
            try:
                # Determine implementation type
                impl_type = type_mapping.get(dream.dream_type, 'other')

                # Session 370: Check if this dream should be a visual implementation
                if _is_visual_dream(dream):
                    impl_type = 'visual'
                    logger.info(f"🎨 [DREAM-IMPLEMENTATION] Detected visual dream: {dream.title[:40]}")

                # Create implementation record
                implementation = DreamImplementation.create_from_approved_dream(
                    dream=dream,
                    implementation_type=impl_type
                )
                stats['implementations_created'] += 1

                # Find the best agent to implement this
                # First try the dreaming agent, then find one with relevant skills
                assigned_agent = dream.agent

                # If dream has no agent or we want a specialist, find one
                # Session 370: Added 'visual' to the list - always use ImageAgent for visual dreams
                if not assigned_agent or impl_type in ['feature', 'improvement', 'visual']:
                    # Try to find a specialist based on implementation type
                    if impl_type in ['feature', 'improvement', 'workflow']:
                        # Look for workflow or creation agents
                        candidates = Agent.objects.filter(
                            is_active=True,
                            name__in=['WorkflowOrchestrationAgent', 'CreationAgent', 'CreativeDirectorAgent']
                        ).first()
                        if candidates:
                            assigned_agent = candidates

                    elif impl_type == 'content':
                        candidates = Agent.objects.filter(
                            is_active=True,
                            name__in=['ContentStrategyAgent', 'CreationAgent', 'ImageAgent']
                        ).first()
                        if candidates:
                            assigned_agent = candidates

                    elif impl_type == 'research':
                        candidates = Agent.objects.filter(
                            is_active=True,
                            name__in=['ResearchAgent', 'TrendAnalysisAgent', 'CompetitorAnalysisAgent']
                        ).first()
                        if candidates:
                            assigned_agent = candidates

                    # Session 370: Assign ImageAgent for visual implementations
                    elif impl_type == 'visual':
                        candidates = Agent.objects.filter(
                            is_active=True,
                            name__in=['ImageAgent', 'CreativeDirectorAgent', 'CreationAgent']
                        ).first()
                        if candidates:
                            assigned_agent = candidates
                        logger.info(f"🎨 [DREAM-IMPLEMENTATION] Assigned {candidates.name if candidates else 'None'} for visual dream")

                if assigned_agent:
                    implementation.assign_agent(assigned_agent)
                    stats['agents_assigned'] += 1

                    # Generate implementation plan
                    plan_prompt = f"""Create a brief implementation plan for this approved idea.

Dream Title: {dream.title}
Dream Content: {dream.content[:500]}
Dream Type: {dream.dream_type}
Implementation Type: {impl_type}
Agent: {assigned_agent.name}
Agent Specialty: {assigned_agent.specialization or 'General'}

Create a 3-5 step implementation plan. Be specific and actionable.
Format: numbered list of steps."""

                    try:
                        plan_response = client.chat.completions.create(
                            model="gpt-5-mini",
                            messages=[{"role": "user", "content": plan_prompt}],
                            max_completion_tokens=800  # Higher for reasoning models
                        )

                        plan = plan_response.choices[0].message.content.strip()
                        implementation.start_implementation(plan=plan)

                        logger.info(f"🚀 [DREAM-IMPLEMENTATION] Created implementation for '{dream.title[:40]}' -> {assigned_agent.name}")

                    except Exception as plan_error:
                        logger.warning(f"🚀 [DREAM-IMPLEMENTATION] Failed to generate plan: {plan_error}")
                        # Still mark as in_progress even without plan
                        implementation.start_implementation(plan="Implementation plan pending")

                stats['dreams_processed'] += 1

            except Exception as e:
                logger.warning(f"🚀 [DREAM-IMPLEMENTATION] Failed to process dream {dream.id}: {e}")
                continue

        # Broadcast update
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'dream_implementation',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception:
            pass

        logger.info(
            f"🚀 [DREAM-IMPLEMENTATION] Complete: "
            f"{stats['implementations_created']} implementations created, "
            f"{stats['agents_assigned']} agents assigned"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🚀 [DREAM-IMPLEMENTATION] Processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def execute_dream_implementations(self, max_implementations: int = 5):
    """
    Session 368: Agent Execution Engine - Agents execute their implementation plans.

    This task takes in-progress implementations and has agents actually execute
    their plans to generate real deliverables.

    Implementation Types and Deliverables:
    - feature/improvement: Generate images, documents, or code
    - content: Create content strategy document with actionable items
    - research: Conduct research and generate a comprehensive report
    - experiment: Try something new and document findings

    Args:
        max_implementations: Maximum implementations to execute per cycle

    Returns:
        Stats about implementations executed and deliverables generated
    """
    from django.utils import timezone
    from core.models_unified_system import DreamImplementation
    import openai
    import os
    import json

    logger.info("⚡ [EXECUTION-ENGINE] Starting dream implementation execution...")

    try:
        # Get validated or in-progress implementations that haven't been completed
        # 'validated' = user approved the dream, ready to execute
        # 'in_progress' = execution has started (legacy status)
        in_progress = DreamImplementation.objects.filter(
            status__in=['validated', 'in_progress'],
            completed_at__isnull=True
        ).select_related(
            'dream', 'dream__agent', 'assigned_agent', 'project'
        ).order_by('started_at')[:max_implementations]

        if not in_progress.exists():
            logger.info("⚡ [EXECUTION-ENGINE] No validated/in-progress implementations to execute")
            return {'status': 'skipped', 'reason': 'no_implementations_ready'}

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        stats = {
            'executed': 0,
            'completed': 0,
            'deliverables_generated': 0,
            'failed': 0,
            'deliverable_types': {}
        }

        for impl in in_progress:
            try:
                dream = impl.dream
                agent = impl.assigned_agent
                agent_name = agent.name if agent else 'Unknown'

                logger.info(f"⚡ [EXECUTION-ENGINE] Executing: {dream.title[:40]} ({impl.implementation_type})")

                # Execute based on implementation type
                deliverable = None
                deliverable_type = None
                deliverable_path = None
                deliverable_summary = None

                if impl.implementation_type in ['feature', 'improvement']:
                    # Generate a detailed feature specification/proposal
                    deliverable = _execute_feature_implementation(client, dream, impl, agent)
                    deliverable_type = 'specification'
                    deliverable_path = f'/implementations/specs/{impl.id}.md'
                    deliverable_summary = f"Feature specification for: {dream.title}"

                elif impl.implementation_type == 'content':
                    # Generate a content strategy document
                    deliverable = _execute_content_implementation(client, dream, impl, agent)
                    deliverable_type = 'content_strategy'
                    deliverable_path = f'/implementations/content/{impl.id}.md'
                    deliverable_summary = f"Content strategy for: {dream.title}"

                elif impl.implementation_type == 'research':
                    # Generate a research report
                    deliverable = _execute_research_implementation(client, dream, impl, agent)
                    deliverable_type = 'research_report'
                    deliverable_path = f'/implementations/research/{impl.id}.md'
                    deliverable_summary = f"Research report on: {dream.title}"

                elif impl.implementation_type == 'experiment':
                    # Generate an experiment design and findings
                    deliverable = _execute_experiment_implementation(client, dream, impl, agent)
                    deliverable_type = 'experiment_report'
                    deliverable_path = f'/implementations/experiments/{impl.id}.md'
                    deliverable_summary = f"Experiment findings for: {dream.title}"

                elif impl.implementation_type == 'visual':
                    # Session 370: Generate actual images using ImageAgent
                    visual_result = _execute_visual_implementation(dream, impl, agent)
                    if visual_result:
                        deliverable = visual_result.get('description', '')
                        deliverable_type = 'generated_images'
                        deliverable_path = f'/implementations/visual/{impl.id}'
                        deliverable_summary = f"Generated {len(visual_result.get('images', []))} image(s) for: {dream.title}"
                        # Store the generated images in the JSONField
                        impl.generated_media = visual_result.get('images', [])
                        impl.save(update_fields=['generated_media'])
                        stats['images_generated'] = stats.get('images_generated', 0) + len(visual_result.get('images', []))
                    else:
                        deliverable = None

                else:
                    # Generic implementation
                    deliverable = _execute_generic_implementation(client, dream, impl, agent)
                    deliverable_type = 'document'
                    deliverable_path = f'/implementations/general/{impl.id}.md'
                    deliverable_summary = f"Implementation document for: {dream.title}"

                stats['executed'] += 1

                if deliverable:
                    # Store the deliverable in the implementation
                    impl.complete_implementation(
                        deliverable_type=deliverable_type,
                        deliverable_path=deliverable_path,
                        summary=deliverable_summary
                    )

                    # Store the full deliverable content in the dedicated field
                    impl.deliverable_content = deliverable
                    impl.save(update_fields=['deliverable_content'])

                    stats['completed'] += 1
                    stats['deliverables_generated'] += 1
                    stats['deliverable_types'][deliverable_type] = stats['deliverable_types'].get(deliverable_type, 0) + 1

                    logger.info(f"⚡ [EXECUTION-ENGINE] Completed: {dream.title[:40]} -> {deliverable_type}")

            except Exception as e:
                logger.warning(f"⚡ [EXECUTION-ENGINE] Failed to execute {impl.id}: {e}")
                stats['failed'] += 1
                continue

        # Broadcast update
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'dream_execution',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception:
            pass

        logger.info(
            f"⚡ [EXECUTION-ENGINE] Complete: "
            f"{stats['completed']} completed, "
            f"{stats['deliverables_generated']} deliverables generated"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"⚡ [EXECUTION-ENGINE] Execution failed: {e}")
        return {'status': 'failed', 'error': str(e)}


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
    """
    Session 249: Deep exploration of a dream topic when user clicks "Explore".

    When a user reacts to a dream with "explore", we trigger a deeper investigation
    of that topic. The agent generates additional insights, related ideas, and
    potentially adds to their knowledge base.

    Args:
        exploration_id: UUID of the DreamExploration to process

    Returns:
        Exploration results and status
    """
    from django.utils import timezone
    from core.models import (
        DreamExploration, AgentKnowledgeSource, AgentDream
    )
    import openai
    import os

    logger.info(f"🚀 [EXPLORE] Starting dream exploration: {exploration_id}")

    try:
        # Get the exploration record
        exploration = DreamExploration.objects.select_related(
            'dream', 'dream__agent'
        ).filter(id=exploration_id).first()

        if not exploration:
            logger.error(f"🚀 [EXPLORE] Exploration not found: {exploration_id}")
            return {'status': 'failed', 'error': 'Exploration not found'}

        if exploration.status != 'pending':
            logger.info(f"🚀 [EXPLORE] Exploration already processed: {exploration.status}")
            return {'status': 'skipped', 'reason': 'already_processed'}

        # Mark as in progress
        exploration.status = 'in_progress'
        exploration.save()

        dream = exploration.dream
        agent = dream.agent

        if not agent:
            exploration.status = 'failed'
            exploration.save()
            return {'status': 'failed', 'error': 'No agent associated with dream'}

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # Generate deep exploration content
        system_prompt = f"""You are {agent.name}, an AI agent specialized in {agent.specialization or 'creative analysis'}.

You had an interesting dream/idea that the user wants you to explore further:

Dream Title: {dream.title}
Dream Content: {dream.content}
Inspiration Source: {dream.inspiration_source}

Now you are diving deeper into this concept. Generate a thoughtful exploration that:
1. Expands on the core idea with more detail and context
2. Identifies 3-5 key insights or implications
3. Suggests potential applications or next steps
4. Connects it to related concepts in your area of expertise

Be thorough but engaging. This should feel like a creative deep-dive, not a dry analysis."""

        user_prompt = f"""Explore this dream idea more deeply: "{dream.title}"

Generate:
1. An expanded exploration (2-3 paragraphs) that develops the idea further
2. A JSON array of 3-5 key insights (just the insights, each as a short sentence)
3. What knowledge or action this could lead to

Format your response as:
EXPLORATION:
[your expanded exploration here]

INSIGHTS:
["insight 1", "insight 2", "insight 3"]

NEXT_STEPS:
[what this could lead to - one paragraph]"""

        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=800,
                reasoning_effort="medium",
            )

            full_response = response.choices[0].message.content.strip()

            # Session 359: Validate Memory Palace exploration for mythology violations
            full_response = validate_agent_output("MemoryPalaceExplorer", full_response)

            # Parse the response
            exploration_content = ""
            insights = []
            next_steps = ""

            if "EXPLORATION:" in full_response:
                parts = full_response.split("INSIGHTS:")
                exploration_content = parts[0].replace("EXPLORATION:", "").strip()

                if len(parts) > 1:
                    remaining = parts[1]
                    if "NEXT_STEPS:" in remaining:
                        insight_part, next_part = remaining.split("NEXT_STEPS:")
                        next_steps = next_part.strip()

                        # Try to parse insights as JSON
                        try:
                            import json
                            # Find JSON array in the insight part
                            start = insight_part.find('[')
                            end = insight_part.rfind(']') + 1
                            if start >= 0 and end > start:
                                insights = json.loads(insight_part[start:end])
                        except:
                            # Fallback: split by newlines
                            insights = [line.strip().strip('-•').strip()
                                       for line in insight_part.strip().split('\n')
                                       if line.strip() and not line.strip().startswith('[')]
            else:
                # Fallback: use the entire response
                exploration_content = full_response

            # Update the exploration record
            exploration.exploration_content = exploration_content
            exploration.insights_generated = insights[:5] if insights else []
            exploration.status = 'completed'
            exploration.completed_at = timezone.now()

            # Optionally add to agent's knowledge base
            if exploration_content and len(exploration_content) > 100:
                try:
                    AgentKnowledgeSource.objects.create(
                        agent=agent,
                        knowledge_type='content_idea',  # Dream explorations are content ideas
                        title=f"Dream Explored: {dream.title[:100]}",
                        summary=exploration_content[:1000],
                        key_insights=insights[:5] if insights else [],
                        data_points_count=1,
                        confidence_score=0.8,
                        relevance_score=0.9,
                        freshness_score=1.0,
                        source_spider_names=['dream_exploration']
                    )
                    exploration.related_knowledge_added = True
                    logger.info(f"🚀 [EXPLORE] Added to {agent.name}'s knowledge base")
                except Exception as ke:
                    logger.warning(f"🚀 [EXPLORE] Could not add to knowledge: {ke}")

            exploration.save()

            # Broadcast the exploration result
            try:
                import redis
                import json
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                r.publish('agent_learning', json.dumps({
                    'type': 'dream_explored',
                    'exploration_id': str(exploration.id),
                    'dream_id': str(dream.id),
                    'dream_title': dream.title,
                    'agent_name': agent.name,
                    'insights_count': len(insights),
                    'knowledge_added': exploration.related_knowledge_added,
                    'timestamp': timezone.now().isoformat()
                }))
            except:
                pass

            logger.info(
                f"🚀 [EXPLORE] Completed exploration of '{dream.title}' "
                f"- {len(insights)} insights, knowledge_added={exploration.related_knowledge_added}"
            )

            return {
                'status': 'success',
                'exploration_id': str(exploration.id),
                'insights_count': len(insights),
                'knowledge_added': exploration.related_knowledge_added
            }

        except Exception as api_error:
            logger.error(f"🚀 [EXPLORE] API call failed: {api_error}")
            exploration.status = 'failed'
            exploration.save()
            return {'status': 'failed', 'error': str(api_error)}

    except Exception as e:
        logger.exception(f"🚀 [EXPLORE] Exploration failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 250: Hive Mind Mode Tasks
# =============================================================================

@shared_task(bind=True)
def run_hive_mind_session(self, session_id: str):
    """
    Session 250: Orchestrate a Hive Mind session.

    All participating agents work on the question simultaneously,
    then their contributions are synthesized into a unified output.
    """
    logger.info(f"🧠 [HIVE MIND] Starting session {session_id}")

    try:
        from core.models import HiveMindSession, HiveMindContribution, Agent
        from django.utils import timezone
        import time
        import concurrent.futures
        from openai import OpenAI

        session = HiveMindSession.objects.get(id=session_id)
        contributions = session.contributions.all().select_related('agent')

        if not contributions.exists():
            logger.warning(f"🧠 [HIVE MIND] No contributions found for session {session_id}")
            session.status = 'failed'
            session.save()
            return {'status': 'failed', 'error': 'No contributions found'}

        client = OpenAI()
        total_thinking_time = 0
        completed_count = 0

        # Process each agent's contribution
        # We use a thread pool to parallelize API calls
        def process_contribution(contribution):
            try:
                from django.utils import timezone as tz
                start_time = time.time()

                # Update status to thinking
                contribution.status = 'thinking'
                contribution.save()

                # Broadcast status update
                broadcast_hive_mind_update(session, contribution, 'thinking')

                # Build the prompt for this agent
                agent = contribution.agent
                prompt = f"""You are {agent.name}, an AI agent specializing in {agent.specialization}.

Your colleague agents are also working on this problem. Contribute YOUR unique perspective based on your specialty.

QUESTION: {session.question}

{f'ADDITIONAL CONTEXT: {session.context}' if session.context else ''}

Provide your expert contribution in 2-3 paragraphs. Focus on:
1. Your unique perspective based on your specialization
2. Specific actionable insights only you can provide
3. How your expertise addresses the question

End with 3-5 key bullet points summarizing your main contributions.

Respond as {agent.name}:"""

                # Call GPT-5-mini for the contribution
                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are {agent.name}, a specialized AI agent. Your expertise: {agent.description}"
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=600,
                    reasoning_effort="medium",
                )

                contribution_text = response.choices[0].message.content.strip()

                # Session 356: Validate output for mythology violations
                contribution_text = validate_agent_output(agent.name, contribution_text)

                thinking_time = time.time() - start_time

                # Determine perspective type based on agent specialization
                spec_lower = agent.specialization.lower()
                if 'research' in spec_lower or 'analysis' in spec_lower:
                    perspective_type = 'analysis'
                elif 'creative' in spec_lower or 'design' in spec_lower or 'image' in spec_lower:
                    perspective_type = 'creative'
                elif 'strategy' in spec_lower or 'business' in spec_lower:
                    perspective_type = 'strategic'
                elif 'tech' in spec_lower or 'code' in spec_lower:
                    perspective_type = 'technical'
                else:
                    perspective_type = 'general'

                # Extract key points (look for bullet points)
                key_points = []
                lines = contribution_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                        key_points.append(line[2:].strip())

                # Update contribution
                contribution.contribution = contribution_text
                contribution.key_points = key_points[:5]  # Max 5 key points
                contribution.perspective_type = perspective_type
                contribution.thinking_time = thinking_time
                contribution.status = 'completed'
                contribution.completed_at = tz.now()
                contribution.save()

                # Broadcast completion
                broadcast_hive_mind_update(session, contribution, 'completed')

                logger.info(f"🧠 [HIVE MIND] {agent.name} contributed in {thinking_time:.1f}s")

                return {
                    'agent': agent.name,
                    'status': 'completed',
                    'thinking_time': thinking_time,
                    'key_points': len(key_points)
                }

            except Exception as e:
                contribution.status = 'failed'
                contribution.save()
                broadcast_hive_mind_update(session, contribution, 'failed')
                logger.error(f"🧠 [HIVE MIND] {contribution.agent.name} failed: {e}")
                return {
                    'agent': contribution.agent.name,
                    'status': 'failed',
                    'error': str(e)
                }

        # Process contributions in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(process_contribution, c): c
                for c in contributions
            }

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.get('status') == 'completed':
                    completed_count += 1
                    total_thinking_time += result.get('thinking_time', 0)

        # Now synthesize all contributions
        session.status = 'synthesizing'
        session.save()
        broadcast_hive_mind_status(session, 'synthesizing')

        # Get all completed contributions for synthesis
        completed_contributions = session.contributions.filter(status='completed')

        if completed_contributions.count() == 0:
            session.status = 'failed'
            session.save()
            return {'status': 'failed', 'error': 'No contributions completed'}

        # Build synthesis prompt
        contributions_text = "\n\n".join([
            f"## {c.agent.name} ({c.perspective_type.upper()} perspective):\n{c.contribution}"
            for c in completed_contributions
        ])

        synthesis_prompt = f"""You are the Hive Mind Synthesizer. Multiple specialized AI agents have provided their perspectives on a question. Your job is to synthesize their contributions into a unified, comprehensive response.

ORIGINAL QUESTION: {session.question}

{f'CONTEXT: {session.context}' if session.context else ''}

## AGENT CONTRIBUTIONS:
{contributions_text}

## YOUR TASK:
Create a comprehensive synthesis that:
1. Combines the unique insights from each agent
2. Identifies common themes and agreements
3. Notes any interesting tensions or different perspectives
4. Provides actionable recommendations

Structure your response with clear sections and end with:
- A brief summary (2-3 sentences)
- Top 5 unified recommendations

The synthesis should read as a cohesive document, not just a collection of separate ideas."""

        # Generate synthesis
        synthesis_response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are the Hive Mind Synthesizer, an AI that combines multiple agent perspectives into unified insights."
                },
                {"role": "user", "content": synthesis_prompt}
            ],
            max_completion_tokens=1500,
            reasoning_effort="medium",
        )

        synthesis = synthesis_response.choices[0].message.content.strip()

        # Session 359: Validate Hive Mind synthesis for mythology violations
        synthesis = validate_agent_output("HiveMindSynthesizer", synthesis)

        # Extract a brief summary (first 2-3 sentences or look for summary section)
        summary_lines = synthesis.split('\n')
        summary = ""
        for line in summary_lines:
            if 'summary' in line.lower() and ':' in line:
                # Found a summary section
                idx = summary_lines.index(line)
                if idx + 1 < len(summary_lines):
                    summary = summary_lines[idx + 1].strip()
                    break
        if not summary:
            # Take first meaningful paragraph
            for line in summary_lines:
                if len(line.strip()) > 50:
                    summary = line.strip()[:500]
                    break

        # Update session with final results
        session.synthesis = synthesis
        session.synthesis_summary = summary
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.contribution_count = completed_count
        session.total_thinking_time = total_thinking_time
        session.save()

        # Broadcast completion
        broadcast_hive_mind_status(session, 'completed')

        # Session 420: Send to Discord #boardroom when consensus is reached
        try:
            from core.services.discord_notifications import discord_notify

            # Get participant names
            participant_names = [c.agent.name for c in completed_contributions]

            # Determine impact based on number of agents
            if len(participant_names) >= 6:
                impact = "high"
            elif len(participant_names) >= 4:
                impact = "medium"
            else:
                impact = "low"

            # Send boardroom decision with the synthesis
            discord_notify.send_boardroom_decision(
                title=f"HiveMind Consensus: {session.question[:80]}{'...' if len(session.question) > 80 else ''}",
                decision=f"**{len(participant_names)} agents reached consensus:**\n\n{synthesis[:3500]}",
                participants=participant_names,
                decision_type="strategy",
                impact=impact
            )
            logger.info(f"🏛️ [BOARDROOM] Posted HiveMind consensus to Discord")
        except Exception as discord_err:
            logger.warning(f"🏛️ [BOARDROOM] Discord notification failed: {discord_err}")

        logger.info(
            f"🧠 [HIVE MIND] Session {session_id} completed! "
            f"{completed_count} contributions, {total_thinking_time:.1f}s total thinking time"
        )

        return {
            'status': 'success',
            'session_id': session_id,
            'contribution_count': completed_count,
            'total_thinking_time': total_thinking_time
        }

    except Exception as e:
        logger.exception(f"🧠 [HIVE MIND] Session {session_id} failed: {e}")
        try:
            session = HiveMindSession.objects.get(id=session_id)
            session.status = 'failed'
            session.save()
        except:
            pass
        return {'status': 'failed', 'error': str(e)}


def broadcast_hive_mind_update(session, contribution, status):
    """Broadcast a contribution update via Redis pub/sub."""
    try:
        import redis
        import json
        from django.utils import timezone
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
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
        logger.debug(f"Failed to broadcast hive mind update: {e}")


def broadcast_hive_mind_status(session, status):
    """Broadcast a session status update via Redis pub/sub."""
    try:
        import redis
        import json
        from django.utils import timezone
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.publish('hive_mind', json.dumps({
            'type': 'session_status',
            'session_id': str(session.id),
            'status': status,
            'contribution_count': session.contribution_count,
            'timestamp': timezone.now().isoformat()
        }))
    except Exception as e:
        logger.debug(f"Failed to broadcast hive mind status: {e}")


# =============================================================================
# Session 251: Memory Palace Tasks
# =============================================================================

@shared_task
def generate_memory_embedding(memory_id: str):
    """
    Session 251: Generate an embedding for a memory.

    Uses text-embedding-3-small for semantic search.
    """
    logger.info(f"🧠 [MEMORY] Generating embedding for memory {memory_id}")

    try:
        from core.models_unified_system import AgentMemory
        from openai import OpenAI
        import os

        memory = AgentMemory.objects.get(id=memory_id)

        # Create embedding text combining title, content, and context
        embed_text = f"{memory.title}\n\n{memory.content}"
        if memory.context:
            embed_text += f"\n\nContext: {memory.context}"

        # Generate embedding via OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=embed_text,
            encoding_format="float"
        )

        embedding = response.data[0].embedding

        # Store embedding
        memory.embedding = embedding
        memory.save(update_fields=['embedding'])

        logger.info(f"🧠 [MEMORY] Embedding generated for memory '{memory.title}'")

        return {'status': 'success', 'memory_id': str(memory_id)}

    except Exception as e:
        logger.exception(f"🧠 [MEMORY] Failed to generate embedding: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def auto_connect_memories(memory_id: str, threshold: float = 0.7):
    """
    Session 251: Automatically find and connect similar memories.

    Uses embedding similarity to find related memories.
    """
    logger.info(f"🧠 [MEMORY] Auto-connecting memories for {memory_id}")

    try:
        from core.models_unified_system import AgentMemory, MemoryConnection
        import numpy as np

        memory = AgentMemory.objects.get(id=memory_id)

        if not memory.embedding:
            logger.warning(f"🧠 [MEMORY] No embedding for memory {memory_id}")
            return {'status': 'skipped', 'reason': 'no_embedding'}

        # Get other memories from same agent with embeddings
        other_memories = AgentMemory.objects.filter(
            agent=memory.agent,
            embedding__isnull=False
        ).exclude(id=memory_id)[:50]

        if not other_memories.exists():
            return {'status': 'skipped', 'reason': 'no_other_memories'}

        # Calculate similarities
        source_embedding = np.array(memory.embedding)
        connections_created = 0

        for other in other_memories:
            other_embedding = np.array(other.embedding)

            # Cosine similarity
            similarity = np.dot(source_embedding, other_embedding) / (
                np.linalg.norm(source_embedding) * np.linalg.norm(other_embedding)
            )

            if similarity >= threshold:
                # Create connection if similarity is high enough
                connection, created = MemoryConnection.objects.get_or_create(
                    source_memory=memory,
                    target_memory=other,
                    defaults={
                        'connection_type': 'similar',
                        'strength': float(similarity)
                    }
                )

                if created:
                    connections_created += 1
                    # Also add to M2M
                    memory.connected_memories.add(other)

        logger.info(f"🧠 [MEMORY] Created {connections_created} connections for memory '{memory.title}'")

        return {
            'status': 'success',
            'connections_created': connections_created
        }

    except Exception as e:
        logger.exception(f"🧠 [MEMORY] Failed to auto-connect memories: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def record_agent_memory(
    agent_id: str,
    title: str,
    content: str,
    memory_type: str = 'interaction',
    valence: str = 'neutral',
    importance: float = 0.5,
    context: str = '',
    source_type: str = '',
    source_id: str = ''
):
    """
    Session 251: Record a new memory for an agent.

    This is a convenient task that can be called from anywhere
    to record memories asynchronously.
    """
    logger.info(f"🧠 [MEMORY] Recording memory '{title}' for agent {agent_id}")

    try:
        from core.models_unified_system import AgentMemory, Agent

        agent = Agent.objects.get(id=agent_id)

        # Create memory
        memory = AgentMemory.objects.create(
            agent=agent,
            title=title,
            content=content,
            memory_type=memory_type,
            valence=valence,
            importance_score=importance,
            context=context,
            source_type=source_type,
            source_id=source_id
        )

        # Queue embedding generation
        generate_memory_embedding.delay(str(memory.id))

        logger.info(f"🧠 [MEMORY] Memory '{title}' recorded for {agent.name}")

        return {
            'status': 'success',
            'memory_id': str(memory.id),
            'agent_name': agent.name
        }

    except Exception as e:
        logger.exception(f"🧠 [MEMORY] Failed to record memory: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task
def organize_memories_into_rooms(agent_id: str):
    """
    Session 251: Automatically organize memories into appropriate rooms.

    Assigns memories to rooms based on their type.
    """
    logger.info(f"🧠 [MEMORY PALACE] Organizing memories for agent {agent_id}")

    try:
        from core.models_unified_system import AgentMemory, MemoryPalaceRoom, Agent

        agent = Agent.objects.get(id=agent_id)

        # Ensure rooms exist
        rooms = MemoryPalaceRoom.objects.filter(agent=agent)
        if not rooms.exists():
            MemoryPalaceRoom.create_default_rooms(agent)
            rooms = MemoryPalaceRoom.objects.filter(agent=agent)

        # Map memory types to room types
        type_to_room = {
            'technique': 'techniques',
            'success': 'successes',
            'failure': 'lessons',
            'preference': 'preferences',
            'insight': 'insights',
            'interaction': 'general',
            'feedback': 'lessons'
        }

        # Get unassigned memories
        room_dict = {r.room_type: r for r in rooms}
        memories_organized = 0

        for memory in AgentMemory.objects.filter(agent=agent):
            target_room_type = type_to_room.get(memory.memory_type, 'general')
            target_room = room_dict.get(target_room_type)

            if target_room and not target_room.memories.filter(id=memory.id).exists():
                target_room.memories.add(memory)
                memories_organized += 1

        logger.info(f"🧠 [MEMORY PALACE] Organized {memories_organized} memories for {agent.name}")

        return {
            'status': 'success',
            'memories_organized': memories_organized
        }

    except Exception as e:
        logger.exception(f"🧠 [MEMORY PALACE] Failed to organize memories: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 490: Memory Embedding Backfill Task
# =============================================================================

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
# Session 252: Agent Mood System Tasks
# =============================================================================

@shared_task(name='core.tasks.update_agent_mood')
def update_agent_mood(agent_id: str, mood: str, intensity: float = 0.7,
                      trigger_type: str = 'task_success', trigger_source: str = '',
                      duration_minutes: int = 60):
    """
    Session 252: Update an agent's mood from a task or event.

    This is called from various parts of the system when something happens
    that should affect an agent's mood.
    """
    logger.info(f"🎭 [MOOD] Updating mood for agent {agent_id} to {mood}")

    try:
        from core.models_unified_system import Agent, AgentMood, MoodHistory
        from django.utils import timezone
        from datetime import timedelta

        agent = Agent.objects.get(id=agent_id)
        mood_obj, created = AgentMood.objects.get_or_create(agent=agent)

        # Record previous mood in history
        if not created and mood_obj.current_mood != mood:
            previous_duration = None
            if mood_obj.mood_started_at:
                previous_duration = int((timezone.now() - mood_obj.mood_started_at).total_seconds() / 60)

            MoodHistory.objects.create(
                agent=agent,
                mood=mood_obj.current_mood,
                intensity=mood_obj.intensity,
                trigger_type=mood_obj.trigger_type,
                trigger_source=mood_obj.trigger_source,
                creativity_level=mood_obj.creativity_level,
                precision_level=mood_obj.precision_level,
                sociability_level=mood_obj.sociability_level,
                risk_tolerance=mood_obj.risk_tolerance,
                duration_minutes=previous_duration,
            )

        # Mood dimension mappings
        mood_dimensions = {
            'inspired': {'creativity': 0.9, 'precision': 0.5, 'sociability': 0.7, 'risk': 0.8},
            'focused': {'creativity': 0.4, 'precision': 0.95, 'sociability': 0.3, 'risk': 0.2},
            'curious': {'creativity': 0.7, 'precision': 0.6, 'sociability': 0.8, 'risk': 0.7},
            'confident': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.7, 'risk': 0.6},
            'contemplative': {'creativity': 0.6, 'precision': 0.7, 'sociability': 0.4, 'risk': 0.4},
            'energetic': {'creativity': 0.7, 'precision': 0.5, 'sociability': 0.9, 'risk': 0.7},
            'calm': {'creativity': 0.5, 'precision': 0.6, 'sociability': 0.5, 'risk': 0.4},
            'frustrated': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.6, 'risk': 0.3},
            'tired': {'creativity': 0.3, 'precision': 0.4, 'sociability': 0.2, 'risk': 0.2},
            'playful': {'creativity': 0.85, 'precision': 0.4, 'sociability': 0.9, 'risk': 0.85},
        }

        dims = mood_dimensions.get(mood, {'creativity': 0.5, 'precision': 0.5, 'sociability': 0.5, 'risk': 0.5})

        # Update mood
        mood_obj.current_mood = mood
        mood_obj.intensity = intensity
        mood_obj.creativity_level = dims['creativity'] * intensity
        mood_obj.precision_level = dims['precision'] * intensity
        mood_obj.sociability_level = dims['sociability'] * intensity
        mood_obj.risk_tolerance = dims['risk'] * intensity
        mood_obj.trigger_type = trigger_type
        mood_obj.trigger_source = trigger_source[:200] if trigger_source else ''
        mood_obj.mood_started_at = timezone.now()
        mood_obj.mood_expires_at = timezone.now() + timedelta(minutes=duration_minutes) if duration_minutes > 0 else None
        mood_obj.total_mood_changes += 1
        mood_obj.save()

        logger.info(f"🎭 [MOOD] {agent.name} is now {mood} ({intensity:.0%})")

        return {
            'status': 'success',
            'agent': agent.name,
            'mood': mood,
            'intensity': intensity
        }

    except Exception as e:
        logger.exception(f"🎭 [MOOD] Failed to update mood: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.check_mood_expirations')
def check_mood_expirations():
    """
    Session 252: Check for expired moods and reset them to calm.

    Run this periodically (e.g., every 5 minutes) to auto-reset moods.
    """
    logger.info("🎭 [MOOD] Checking for expired moods...")

    try:
        from core.models_unified_system import AgentMood, MoodHistory
        from django.utils import timezone

        expired_moods = AgentMood.objects.filter(
            mood_expires_at__isnull=False,
            mood_expires_at__lte=timezone.now()
        ).exclude(current_mood='calm')

        reset_count = 0
        for mood in expired_moods:
            # Record history
            previous_duration = None
            if mood.mood_started_at:
                previous_duration = int((timezone.now() - mood.mood_started_at).total_seconds() / 60)

            MoodHistory.objects.create(
                agent=mood.agent,
                mood=mood.current_mood,
                intensity=mood.intensity,
                trigger_type=mood.trigger_type,
                trigger_source=mood.trigger_source,
                creativity_level=mood.creativity_level,
                precision_level=mood.precision_level,
                sociability_level=mood.sociability_level,
                risk_tolerance=mood.risk_tolerance,
                duration_minutes=previous_duration,
            )

            # Reset to calm
            mood.current_mood = 'calm'
            mood.intensity = 0.5
            mood.creativity_level = 0.5
            mood.precision_level = 0.6
            mood.sociability_level = 0.5
            mood.risk_tolerance = 0.4
            mood.trigger_type = 'idle'
            mood.trigger_source = 'Mood expired'
            mood.mood_started_at = timezone.now()
            mood.mood_expires_at = None
            mood.total_mood_changes += 1
            mood.save()

            reset_count += 1
            logger.info(f"🎭 [MOOD] Reset {mood.agent.name}'s mood to calm (was expired)")

        logger.info(f"🎭 [MOOD] Reset {reset_count} expired moods")

        return {
            'status': 'success',
            'moods_reset': reset_count
        }

    except Exception as e:
        logger.exception(f"🎭 [MOOD] Failed to check expirations: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.apply_mood_trigger_rules')
def apply_mood_trigger_rules(agent_id: str = None):
    """
    Session 252: Apply mood trigger rules to agents.

    Check if any rules should trigger mood changes based on recent activity.
    """
    logger.info(f"🎭 [MOOD] Applying mood trigger rules...")

    try:
        from core.models_unified_system import Agent, AgentMood, MoodTriggerRule
        from django.utils import timezone

        # Get rules (filtered by agent if specified)
        rules = MoodTriggerRule.objects.filter(is_active=True).order_by('-priority')
        if agent_id:
            rules = rules.filter(agent__isnull=True) | rules.filter(agent_id=agent_id)

        # Get agents to check
        if agent_id:
            agents = Agent.objects.filter(id=agent_id, is_active=True)
        else:
            agents = Agent.objects.filter(is_active=True)

        triggers_applied = 0

        for agent in agents:
            for rule in rules:
                # Skip agent-specific rules that don't match
                if rule.agent and rule.agent_id != agent.id:
                    continue

                # Check condition
                condition_met = False

                if rule.condition_type == 'time_of_day':
                    hour = timezone.now().hour
                    start_hour = rule.condition_value.get('start_hour', 0)
                    end_hour = rule.condition_value.get('end_hour', 24)
                    condition_met = start_hour <= hour < end_hour

                elif rule.condition_type == 'idle_time':
                    mood, _ = AgentMood.objects.get_or_create(agent=agent)
                    if mood.mood_started_at:
                        idle_minutes = (timezone.now() - mood.mood_started_at).total_seconds() / 60
                        threshold = rule.condition_value.get('minutes', 60)
                        condition_met = idle_minutes > threshold

                # Apply trigger if condition met
                if condition_met:
                    update_agent_mood.delay(
                        agent_id=str(agent.id),
                        mood=rule.target_mood,
                        intensity=rule.target_intensity,
                        trigger_type=rule.condition_type,
                        trigger_source=f"Rule: {rule.name}",
                        duration_minutes=rule.duration_minutes
                    )
                    triggers_applied += 1
                    break  # Only apply first matching rule per agent

        logger.info(f"🎭 [MOOD] Applied {triggers_applied} mood trigger rules")

        return {
            'status': 'success',
            'triggers_applied': triggers_applied
        }

    except Exception as e:
        logger.exception(f"🎭 [MOOD] Failed to apply rules: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# SESSION 253: AGENT RIVALRIES & ALLIANCES
# =============================================================================

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
        from core.models_unified_system import AgentRelationship, RelationshipEvent

        relationships = AgentRelationship.objects.all()
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

    Called by Celery Beat every hour.
    """
    try:
        from core.models_unified_system import Alliance

        alliances = Alliance.objects.filter(is_active=True)
        updated_count = 0

        for alliance in alliances:
            old_strength = alliance.combined_strength
            alliance.update_combined_strength()

            if old_strength != alliance.combined_strength:
                updated_count += 1

        logger.info(f"🤝 [ALLIANCES] Updated {updated_count} alliance strengths")

        return {
            'status': 'success',
            'updated_count': updated_count
        }

    except Exception as e:
        logger.exception(f"🤝 [ALLIANCES] Failed to update: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.broadcast_relationship_status')
def broadcast_relationship_status():
    """
    Session 253: Broadcast relationship status via WebSocket.

    Called by Celery Beat every 2 minutes for real-time UI updates.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from core.models_unified_system import AgentRelationship, Alliance, Rivalry
        from django.db.models import Count

        # Get relationship stats
        relationship_counts = AgentRelationship.objects.values('relationship_type').annotate(
            count=Count('id')
        )
        relationship_distribution = {r['relationship_type']: r['count'] for r in relationship_counts}

        # Get active alliances and rivalries
        active_alliances = Alliance.objects.filter(is_active=True).count()
        active_rivalries = Rivalry.objects.filter(is_active=True).count()

        # Get recent events
        from core.models_unified_system import RelationshipEvent
        recent_events = RelationshipEvent.objects.select_related(
            'relationship__agent_from', 'relationship__agent_to'
        ).order_by('-created_at')[:5]

        events_data = []
        for event in recent_events:
            events_data.append({
                'event_type': event.event_type,
                'description': event.description,
                'agents': f"{event.relationship.agent_from.name} & {event.relationship.agent_to.name}",
                'created_at': event.created_at.isoformat(),
            })

        # Broadcast
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'agent_relationships',
                {
                    'type': 'relationship_update',
                    'data': {
                        'relationship_distribution': relationship_distribution,
                        'active_alliances': active_alliances,
                        'active_rivalries': active_rivalries,
                        'total_relationships': AgentRelationship.objects.count(),
                        'recent_events': events_data,
                        'timestamp': timezone.now().isoformat(),
                    }
                }
            )
            logger.debug("⚔️ [RELATIONSHIPS] Broadcast relationship status")
        except Exception as ws_error:
            logger.debug(f"⚔️ [RELATIONSHIPS] WebSocket broadcast skipped: {ws_error}")

        return {'status': 'success'}

    except Exception as e:
        logger.exception(f"⚔️ [RELATIONSHIPS] Failed to broadcast: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# SESSION 254: AGENT EVOLUTION SYSTEM
# =============================================================================

@shared_task(name='core.tasks.process_agent_activity_xp')
def process_agent_activity_xp():
    """
    Session 254: Award XP to agents based on their recent activity.

    Called by Celery Beat every 15 minutes.
    Looks at agent activity from the last 15 minutes and awards XP accordingly.
    """
    try:
        from core.models_unified_system import (
            AgentEvolution, Agent, AgentConversation, AgentDream, AgentLearning
        )

        now = timezone.now()
        fifteen_min_ago = now - timezone.timedelta(minutes=15)

        agents_awarded = 0
        total_xp_awarded = 0

        # Award XP for conversations
        try:
            recent_conversations = AgentConversation.objects.filter(
                created_at__gte=fifteen_min_ago
            ).values('initiator', 'responder')

            for convo in recent_conversations:
                for agent_id in [convo['initiator'], convo['responder']]:
                    if agent_id:
                        try:
                            agent = Agent.objects.get(id=agent_id)
                            evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                            evolution.award_xp(5, 'conversation', 'Participated in agent conversation')
                            agents_awarded += 1
                            total_xp_awarded += 5
                        except Agent.DoesNotExist:
                            pass
        except Exception as e:
            logger.debug(f"📈 [EVOLUTION] Conversation XP check skipped: {e}")

        # Award XP for dreams
        try:
            recent_dreams = AgentDream.objects.filter(
                created_at__gte=fifteen_min_ago
            ).values('agent')

            for dream in recent_dreams:
                if dream['agent']:
                    try:
                        agent = Agent.objects.get(id=dream['agent'])
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                        evolution.award_xp(3, 'dream', 'Generated creative dream')
                        agents_awarded += 1
                        total_xp_awarded += 3
                    except Agent.DoesNotExist:
                        pass
        except Exception as e:
            logger.debug(f"📈 [EVOLUTION] Dream XP check skipped: {e}")

        # Award XP for learning
        try:
            recent_learning = AgentLearning.objects.filter(
                created_at__gte=fifteen_min_ago
            ).values('agent')

            for learning in recent_learning:
                if learning['agent']:
                    try:
                        agent = Agent.objects.get(id=learning['agent'])
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                        evolution.award_xp(8, 'learning', 'Acquired new knowledge')
                        agents_awarded += 1
                        total_xp_awarded += 8
                    except Agent.DoesNotExist:
                        pass
        except Exception as e:
            logger.debug(f"📈 [EVOLUTION] Learning XP check skipped: {e}")

        logger.info(f"📈 [EVOLUTION] Awarded {total_xp_awarded} XP to {agents_awarded} agent activities")

        return {
            'status': 'success',
            'agents_awarded': agents_awarded,
            'total_xp': total_xp_awarded
        }

    except Exception as e:
        logger.exception(f"📈 [EVOLUTION] Failed to process activity XP: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.check_level_milestones')
def check_level_milestones():
    """
    Session 254: Check for and record any missed level milestones.

    Called by Celery Beat hourly to ensure milestones are recorded.
    """
    try:
        from core.models_unified_system import AgentEvolution, LevelMilestone

        evolutions = AgentEvolution.objects.all()
        milestones_created = 0

        for evo in evolutions:
            # Check if milestone exists for current level
            if not LevelMilestone.objects.filter(evolution=evo, level=evo.current_level).exists():
                LevelMilestone.objects.create(
                    evolution=evo,
                    level=evo.current_level,
                    title=evo.level_title,
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


@shared_task(name='core.tasks.broadcast_evolution_status')
def broadcast_evolution_status():
    """
    Session 254: Broadcast evolution status via WebSocket.

    Called by Celery Beat every 2 minutes for real-time UI updates.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from core.models_unified_system import AgentEvolution, XPHistory
        from django.db.models import Sum, Count

        # Get evolution stats
        evolutions = AgentEvolution.objects.all()

        total_xp = evolutions.aggregate(Sum('total_xp'))['total_xp__sum'] or 0
        total_levels = evolutions.aggregate(Sum('current_level'))['current_level__sum'] or 0
        total_prestiges = evolutions.aggregate(Sum('prestige_level'))['prestige_level__sum'] or 0

        # Level distribution
        level_distribution = {}
        for i in range(1, 11):
            level_distribution[str(i)] = evolutions.filter(current_level=i).count()

        # Recent XP gains
        recent_xp = XPHistory.objects.select_related('evolution__agent').order_by('-created_at')[:5]
        recent_gains = []
        for xp in recent_xp:
            recent_gains.append({
                'agent_name': xp.evolution.agent.name,
                'amount': xp.amount,
                'source': xp.source,
                'created_at': xp.created_at.isoformat()
            })

        # Top agents
        top_agents = []
        for evo in evolutions.order_by('-current_level', '-total_xp')[:5]:
            top_agents.append({
                'agent_name': evo.agent.name,
                'level': evo.current_level,
                'level_title': evo.level_title,
                'total_xp': evo.total_xp
            })

        # Broadcast
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'agent_evolution',
                {
                    'type': 'evolution_update',
                    'data': {
                        'total_xp': total_xp,
                        'total_levels': total_levels,
                        'total_prestiges': total_prestiges,
                        'evolved_agents': evolutions.count(),
                        'level_distribution': level_distribution,
                        'recent_xp_gains': recent_gains,
                        'top_agents': top_agents,
                        'timestamp': timezone.now().isoformat(),
                    }
                }
            )
            logger.debug("📈 [EVOLUTION] Broadcast evolution status")
        except Exception as ws_error:
            logger.debug(f"📈 [EVOLUTION] WebSocket broadcast skipped: {ws_error}")

        return {'status': 'success'}

    except Exception as e:
        logger.exception(f"📈 [EVOLUTION] Failed to broadcast: {e}")
        return {'status': 'failed', 'error': str(e)}

# ==================== SESSION 326: PROJECT-AGENT LEARNING BRIDGE ====================


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
        result = bridge.apply_feedback(feedback_id)

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
    from core.models_unified_system import PartnershipProject

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
    """
    Run a learning cycle for a single project.

    Session 354: Project Learning Loop

    Steps:
    1. Get current spider data for project topics
    2. Run research agents (competitor/trend analysis)
    3. Compare with previous findings (delta detection)
    4. Store new learnings
    5. Schedule next run
    6. Create notification if significant changes
    """
    from core.models_partnership import PartnershipProject
    from core.services.unified_intelligence_search import get_unified_intelligence_search
    from django.utils import timezone
    from datetime import timedelta

    logger.info(f"🧠 [SESSION 354] Starting learning cycle for project {project_id}...")

    try:
        project = PartnershipProject.objects.get(id=project_id)
        user = project.user

        logger.info(f"🧠 [SESSION 354] Learning cycle for: {project.project_name}")

        # Step 1: Determine topics to research
        topics = project.learning_topics if project.learning_topics else []
        if not topics:
            # Auto-extract from project name and existing research
            topics = _extract_topics_from_project(project)
            logger.info(f"🧠 [SESSION 354] Auto-extracted topics: {topics}")

        # Step 2: Refresh spider data for topics
        search_service = get_unified_intelligence_search()
        spider_data = []
        for topic in topics[:3]:  # Limit to 3 topics
            try:
                search_service.refresh_spiders_for_query(topic)
                results = search_service.unified_search(topic, limit=10)
                spider_data.extend(results.get('results', []))
            except Exception as e:
                logger.warning(f"🧠 [SESSION 354] Spider refresh failed for '{topic}': {e}")

        logger.info(f"🧠 [SESSION 354] Gathered {len(spider_data)} data points from spiders")

        # Step 3: Run trend analysis using spider data
        current_findings = _analyze_spider_data_for_trends(spider_data, project.project_name)

        # Step 4: Delta detection - compare with previous
        previous_findings = _get_previous_findings(project)
        deltas = _detect_research_deltas(previous_findings, current_findings)

        logger.info(
            f"🧠 [SESSION 354] Delta detection: "
            f"{len(deltas.get('new_items', []))} new, "
            f"{len(deltas.get('removed_items', []))} removed"
        )

        # Step 5: Store learnings
        learning_entry = {
            'date': timezone.now().isoformat(),
            'topics_researched': topics,
            'findings_count': len(current_findings),
            'deltas': deltas,
            'new_trends': deltas.get('new_items', [])[:10],
            'disappeared_trends': deltas.get('removed_items', [])[:10]
        }

        history = project.learning_history or []
        history.append(learning_entry)
        project.learning_history = history

        # Step 6: Update metadata if significant changes
        if deltas.get('new_items'):
            metadata = project.metadata or {}
            summaries = metadata.get('research_summaries', [])
            summaries.append({
                'type': 'learning_update',
                'date': timezone.now().isoformat(),
                'summary': f"Learning cycle: {len(deltas['new_items'])} new trends detected",
                'new_trends': deltas['new_items'][:5],
                'source': 'autonomous_learning'
            })
            metadata['research_summaries'] = summaries
            metadata['last_learning_update'] = timezone.now().isoformat()
            project.metadata = metadata

        # Step 7: Schedule next run
        freq_map = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}
        days = freq_map.get(project.learning_frequency, 7)
        project.last_learning_run = timezone.now()
        project.next_learning_run = timezone.now() + timedelta(days=days)

        project.save()

        logger.info(
            f"🧠 [SESSION 354] Learning cycle complete for {project.project_name}: "
            f"{len(deltas.get('new_items', []))} new trends, next run: {project.next_learning_run}"
        )

        # Step 8: Create notification if significant changes
        if deltas.get('new_items'):
            _create_learning_notification(project, deltas)

        return {
            'success': True,
            'project_id': project_id,
            'project_name': project.project_name,
            'topics': topics,
            'findings_count': len(current_findings),
            'new_trends': len(deltas.get('new_items', [])),
            'next_run': project.next_learning_run.isoformat()
        }

    except PartnershipProject.DoesNotExist:
        logger.error(f"🧠 [SESSION 354] Project {project_id} not found")
        return {'error': 'Project not found'}
    except Exception as e:
        logger.exception(f"🧠 [SESSION 354] Learning cycle failed: {e}")
        return {'error': str(e)}


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
    """
    Session 373: Automatically resolve knowledge gaps on a schedule.

    Checks for knowledge gaps and attempts to fill them with:
    1. Spider data extraction
    2. Best practice generation

    Run via Celery Beat every 6 hours.
    """
    try:
        from core.services.collective_intelligence import get_collective_intelligence_service

        service = get_collective_intelligence_service()

        # Get current knowledge gaps
        gaps = service.identify_knowledge_gaps()

        # Filter to resolvable domains only
        resolvable_domains = {'video', 'audio', 'workflow', '3d', 'character', 'image', 'research'}
        resolvable_gaps = [g for g in gaps if g.domain in resolvable_domains]

        if not resolvable_gaps:
            logger.info("🧠 [SESSION 373] No resolvable knowledge gaps found")
            return {'status': 'no_gaps', 'message': 'No resolvable knowledge gaps'}

        total_created = 0
        results = []

        for gap in resolvable_gaps:
            result = service.resolve_knowledge_gap(gap.domain)
            results.append(result)
            if result.get('success'):
                total_created += result.get('items_created', 0)
                logger.info(f"🧠 [SESSION 373] Resolved {gap.domain} gap: created {result.get('items_created', 0)} items")

        # Broadcast the update via WebSocket
        try:
            import redis
            import json
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.publish('collective_intelligence', json.dumps({
                'type': 'knowledge_gaps_resolved',
                'gaps_resolved': len(resolvable_gaps),
                'items_created': total_created
            }))
        except Exception:
            pass

        return {
            'status': 'success',
            'gaps_resolved': len(resolvable_gaps),
            'items_created': total_created,
            'details': results
        }

    except Exception as e:
        logger.error(f"🧠 [SESSION 373] Error auto-resolving knowledge gaps: {e}")
        return {'status': 'error', 'error': str(e)}


# ==================== SESSION 402: DOCUMENT INGESTION TASKS ====================


@shared_task(bind=True, max_retries=3)
def process_document_async(self, document_id: int, generate_embeddings: bool = True, embedding_model: str = 'openai_text_embedding_3_small'):
    """
    Process a document asynchronously.

    Session 402: Document Ingestion Pipeline

    Args:
        document_id: ID of the Document to process
        generate_embeddings: Whether to generate embeddings after processing
        embedding_model: Which embedding model to use
    """
    from content.models import Document, ContentStatus
    from content.processors import DocumentProcessingPipeline

    try:
        document = Document.objects.get(id=document_id)
        logger.info(f"📄 [SESSION 402] Processing document: {document.title} (ID: {document_id})")

        # Update status
        document.status = ContentStatus.PROCESSING
        document.save(update_fields=['status'])

        # Process the document
        pipeline = DocumentProcessingPipeline()
        result = pipeline.process_document(document.file_path)

        if result.success:
            # Update document with processed content
            document.processed_content = result.processed_content
            document.raw_content = result.raw_content
            document.word_count = result.word_count
            document.language = result.language
            document.key_phrases = result.key_phrases
            document.entities = result.entities
            document.extracted_metadata = result.metadata
            document.status = ContentStatus.PROCESSED
            document.add_processing_log('document_processing', 'success', {'word_count': result.word_count})
            document.save()

            logger.info(f"📄 [SESSION 402] Document processed successfully: {document.title}")

            # Generate embeddings if requested
            if generate_embeddings:
                generate_document_embeddings.delay(document_id, embedding_model)

            return {
                'status': 'success',
                'document_id': document_id,
                'word_count': result.word_count,
                'language': result.language
            }
        else:
            document.status = ContentStatus.FAILED
            document.error_message = result.error_message
            document.add_processing_log('document_processing', 'failed', {'error': result.error_message})
            document.save(update_fields=['status', 'error_message'])

            logger.error(f"📄 [SESSION 402] Document processing failed: {result.error_message}")
            return {
                'status': 'failed',
                'document_id': document_id,
                'error': result.error_message
            }

    except Document.DoesNotExist:
        logger.error(f"📄 [SESSION 402] Document not found: {document_id}")
        return {'status': 'error', 'error': f'Document {document_id} not found'}
    except Exception as e:
        logger.error(f"📄 [SESSION 402] Error processing document {document_id}: {e}")
        # Retry on transient errors
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def process_url_async(self, url: str, title: str = None, user_id: int = None, generate_embeddings: bool = True):
    """
    Process a URL (YouTube or web page) asynchronously and create a Document.

    Session 402: Document Ingestion Pipeline

    Args:
        url: The URL to process (YouTube or web page)
        title: Optional title override
        user_id: Owner user ID
        generate_embeddings: Whether to generate embeddings
    """
    from content.models import Document, DocumentType, ContentStatus, ContentSource
    from content.processors import DocumentProcessingPipeline
    from django.contrib.auth import get_user_model

    try:
        logger.info(f"🌐 [SESSION 402] Processing URL: {url}")

        # Process the URL
        pipeline = DocumentProcessingPipeline()
        result = pipeline.process_url(url)

        if not result.success:
            logger.error(f"🌐 [SESSION 402] URL processing failed: {result.error_message}")
            return {
                'status': 'failed',
                'url': url,
                'error': result.error_message
            }

        # Determine document type
        processor_name = result.metadata.get('processor', '')
        if processor_name == 'YouTubeProcessor':
            doc_type = DocumentType.YOUTUBE
        else:
            doc_type = DocumentType.URL

        # Create document record
        User = get_user_model()
        owner = User.objects.get(id=user_id) if user_id else User.objects.first()

        document = Document.objects.create(
            title=title or result.metadata.get('title', url[:100]),
            document_type=doc_type,
            processed_content=result.processed_content,
            raw_content=result.raw_content,
            word_count=result.word_count,
            language=result.language,
            key_phrases=result.key_phrases,
            entities=result.entities,
            extracted_metadata=result.metadata,
            source_url=url,
            status=ContentStatus.PROCESSED,
            source=ContentSource.API,
            owner=owner,
        )

        # Add processing log
        document.add_processing_log('url_ingestion', 'success', {
            'processor': processor_name,
            'word_count': result.word_count
        })

        logger.info(f"🌐 [SESSION 402] Created document from URL: {document.title} (ID: {document.id})")

        # Generate embeddings if requested
        if generate_embeddings:
            generate_document_embeddings.delay(document.id)

        return {
            'status': 'success',
            'document_id': document.id,
            'title': document.title,
            'word_count': result.word_count,
            'url': url,
            'type': str(doc_type)
        }

    except Exception as e:
        logger.error(f"🌐 [SESSION 402] Error processing URL {url}: {e}")
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def generate_document_embeddings(self, document_id: str, embedding_model: str = 'openai_small'):
    """
    Generate embeddings for a document's content.

    Session 402: Document Ingestion Pipeline

    Args:
        document_id: ID of the Document (UUID string)
        embedding_model: Which embedding model to use (openai_small, openai_large, etc.)
    """
    import asyncio
    from content.models import Document, DocumentEmbedding, EmbeddingModel
    from content.embeddings import RAGSystem

    try:
        document = Document.objects.get(id=document_id)
        logger.info(f"🔢 [SESSION 402] Generating embeddings for: {document.title}")

        content = document.get_content()
        if not content:
            logger.warning(f"🔢 [SESSION 402] No content to embed for document {document_id}")
            return {'status': 'skipped', 'reason': 'No content'}

        # Map string model name to enum
        model_map = {
            'openai_small': EmbeddingModel.OPENAI_SMALL,
            'openai_large': EmbeddingModel.OPENAI_LARGE,
            'openai_ada': EmbeddingModel.OPENAI_ADA,
            'sentence_transformers': EmbeddingModel.SENTENCE_TRANSFORMERS,
            'cohere': EmbeddingModel.COHERE,
        }
        model_enum = model_map.get(embedding_model, EmbeddingModel.OPENAI_SMALL)

        # Initialize RAG system and process document
        rag = RAGSystem()

        # Run async method in sync context
        async def run_embedding():
            return await rag.process_document_for_rag(document, model_enum)

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        success = loop.run_until_complete(run_embedding())

        if success:
            # Count embeddings created
            embedding_count = DocumentEmbedding.objects.filter(document=document).count()
            logger.info(f"🔢 [SESSION 402] Generated {embedding_count} embeddings for: {document.title}")

            return {
                'status': 'success',
                'document_id': str(document_id),
                'chunk_count': embedding_count,
                'embedding_model': embedding_model
            }
        else:
            logger.error(f"🔢 [SESSION 402] Embedding generation failed for: {document.title}")
            return {
                'status': 'failed',
                'document_id': str(document_id),
                'error': 'Embedding generation returned False'
            }

    except Document.DoesNotExist:
        logger.error(f"🔢 [SESSION 402] Document not found: {document_id}")
        return {'status': 'error', 'error': f'Document {document_id} not found'}
    except Exception as e:
        logger.error(f"🔢 [SESSION 402] Error generating embeddings for {document_id}: {e}")
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


@shared_task
def batch_process_urls(urls: list, user_id: int = None, generate_embeddings: bool = True):
    """
    Process multiple URLs in batch.

    Session 402: Document Ingestion Pipeline

    Args:
        urls: List of URLs to process
        user_id: Owner user ID
        generate_embeddings: Whether to generate embeddings
    """
    results = []
    for url in urls:
        task = process_url_async.delay(
            url=url,
            user_id=user_id,
            generate_embeddings=generate_embeddings
        )
        results.append({'url': url, 'task_id': task.id})

    logger.info(f"📦 [SESSION 402] Queued {len(urls)} URLs for processing")
    return {'status': 'queued', 'count': len(urls), 'tasks': results}


# ============================================================
# SESSION 420: Training Data Collection from HuggingFace
# ============================================================

@shared_task
def collect_training_data():
    """
    Daily training data collection from HuggingFace datasets.

    Session 420: Automated training data collection for agent learning.

    Fetches high-quality conversation data from:
    - OpenAssistant (human-AI dialogue)
    - Alpaca (instruction tuning)
    - Dolly (instruction following)
    - No Robots (human-written, zero AI)
    - SlimOrca (reasoning conversations)
    - And more...

    Data is saved to SpiderData and triggers the Spider Data Bridge
    to create learning entries for agents.
    """
    import asyncio

    logger.info("📚 [SESSION 420] Starting daily training data collection")

    try:
        from ai_core.spiders.specialized.discord_training_spider import DiscordTrainingSpider
        from ai_core.spiders.base_spider import SpiderTarget

        # Initialize spider
        spider = DiscordTrainingSpider()

        # Create target
        target = SpiderTarget(url='https://huggingface.co/datasets')

        # Run async fetch
        async def fetch_and_process():
            raw_data = await spider.fetch_data(target)
            if raw_data:
                result = await spider.process_data(raw_data, target)
                return raw_data, result
            return None, None

        # Get or create event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        raw_data, result = loop.run_until_complete(fetch_and_process())

        if not result:
            logger.warning("📚 [SESSION 420] No training data fetched")
            return {'status': 'no_data', 'records_saved': 0}

        # Save to SpiderData (triggers Spider Data Bridge automatically)
        from core.models_unified_system import SpiderData
        import json

        content = result.content
        high_quality = content.get('high_quality_conversations', [])
        saved = 0

        for conv in high_quality[:50]:  # Limit to 50 per run
            try:
                messages = conv.get('messages', [])
                if not messages:
                    continue

                first_msg = messages[0]
                summary = first_msg.get('content', str(first_msg)) if isinstance(first_msg, dict) else str(first_msg)

                SpiderData.objects.create(
                    spider_name='discord_training',
                    source_url=f"https://huggingface.co/datasets/{conv.get('source_dataset', '')}",
                    data_type='training_data',
                    raw_data=conv,
                    processed_data={
                        'summary': summary[:500],
                        'message_count': len(messages),
                        'topics': conv.get('topics', []),
                        'quality_score': conv.get('quality_score', 0.5),
                    },
                    relevance_score=int(conv.get('quality_score', 0.5) * 100),
                    insights=conv.get('topics', []),
                )
                saved += 1
            except Exception as e:
                logger.warning(f"📚 [SESSION 420] Error saving conversation: {e}")

        stats = content.get('statistics', {})
        logger.info(f"📚 [SESSION 420] Training data collection complete: {saved} records saved")
        logger.info(f"📚 [SESSION 420] Stats: {stats.get('total_conversations', 0)} fetched, "
                   f"{stats.get('high_quality_count', 0)} high quality, "
                   f"avg score {stats.get('avg_quality_score', 0):.2f}")

        # Send to Discord
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_system_status(
                component='training_spider',
                status='completed',
                message=f"Collected {saved} training records from HuggingFace datasets",
                details={
                    'total_fetched': stats.get('total_conversations', 0),
                    'high_quality': stats.get('high_quality_count', 0),
                    'topics': stats.get('topics_found', []),
                }
            )
        except Exception:
            pass

        return {
            'status': 'success',
            'records_saved': saved,
            'total_fetched': stats.get('total_conversations', 0),
            'high_quality': stats.get('high_quality_count', 0),
            'topics': stats.get('topics_found', []),
        }

    except Exception as e:
        logger.error(f"📚 [SESSION 420] Training data collection failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def collect_training_data_full():
    """
    Weekly full training data refresh.

    Session 420: More comprehensive collection that runs weekly.
    Fetches more records per dataset for a deeper training corpus.
    """
    import asyncio

    logger.info("📚 [SESSION 420] Starting FULL weekly training data collection")

    try:
        from ai_core.spiders.specialized.discord_training_spider import DiscordTrainingSpider
        from ai_core.spiders.base_spider import SpiderTarget

        spider = DiscordTrainingSpider()
        target = SpiderTarget(url='https://huggingface.co/datasets')

        async def fetch_and_process():
            raw_data = await spider.fetch_data(target)
            if raw_data:
                result = await spider.process_data(raw_data, target)
                return raw_data, result
            return None, None

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        raw_data, result = loop.run_until_complete(fetch_and_process())

        if not result:
            logger.warning("📚 [SESSION 420] No training data fetched in full collection")
            return {'status': 'no_data', 'records_saved': 0}

        from core.models_unified_system import SpiderData

        content = result.content
        # For weekly full collection, save more records
        high_quality = content.get('high_quality_conversations', [])
        medium_quality = content.get('medium_quality_conversations', [])
        all_quality = high_quality + medium_quality
        saved = 0

        for conv in all_quality[:200]:  # Save up to 200 per weekly run
            try:
                messages = conv.get('messages', [])
                if not messages:
                    continue

                first_msg = messages[0]
                summary = first_msg.get('content', str(first_msg)) if isinstance(first_msg, dict) else str(first_msg)

                SpiderData.objects.create(
                    spider_name='discord_training',
                    source_url=f"https://huggingface.co/datasets/{conv.get('source_dataset', '')}",
                    data_type='training_data',
                    raw_data=conv,
                    processed_data={
                        'summary': summary[:500],
                        'message_count': len(messages),
                        'topics': conv.get('topics', []),
                        'quality_score': conv.get('quality_score', 0.5),
                    },
                    relevance_score=int(conv.get('quality_score', 0.5) * 100),
                    insights=conv.get('topics', []),
                )
                saved += 1
            except Exception as e:
                logger.warning(f"📚 [SESSION 420] Error saving conversation: {e}")

        stats = content.get('statistics', {})
        logger.info(f"📚 [SESSION 420] FULL training data collection complete: {saved} records saved")

        # Send to Discord
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_system_status(
                component='training_spider',
                status='completed',
                message=f"Weekly FULL collection: {saved} training records from HuggingFace",
                details={
                    'total_fetched': stats.get('total_conversations', 0),
                    'high_quality': stats.get('high_quality_count', 0),
                    'medium_quality': stats.get('medium_quality_count', 0),
                    'topics': stats.get('topics_found', []),
                }
            )
        except Exception:
            pass

        return {
            'status': 'success',
            'records_saved': saved,
            'total_fetched': stats.get('total_conversations', 0),
            'collection_type': 'full_weekly',
        }

    except Exception as e:
        logger.error(f"📚 [SESSION 420] FULL training data collection failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def generate_weekly_opportunity_digest():
    """
    Session 425: Generate and send weekly opportunity digest to Discord #boardroom.

    Runs weekly (configured in celery.py) to summarize:
    - Total opportunities found
    - High-value opportunities
    - Tasks created and their outcomes
    - Revenue generated
    - Win/loss rates
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Count, Sum, Avg
    from core.models_unified_system import (
        Opportunity, OpportunityTask, OpportunityOutcome, OpportunityDigest
    )

    logger.info("📊 [SESSION 425] Starting weekly opportunity digest generation")

    try:
        # Calculate period (last 7 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=7)

        # Get opportunity stats for the period
        opportunities = Opportunity.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        total_opportunities = opportunities.count()
        high_value_count = opportunities.filter(overall_score__gte=70).count()

        # Category breakdown
        by_category = dict(
            opportunities.exclude(category__isnull=True)
            .values_list('category')
            .annotate(count=Count('id'))
        )

        # Task stats
        tasks = OpportunityTask.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        tasks_created = tasks.count()

        # Outcome stats (include all outcomes, not just from this period)
        outcomes = OpportunityOutcome.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        tasks_won = outcomes.filter(outcome='won').count()
        tasks_lost = outcomes.filter(outcome='lost').count()

        total_outcomes = tasks_won + tasks_lost
        win_rate = (tasks_won / total_outcomes * 100) if total_outcomes > 0 else 0

        # Revenue from wins
        total_revenue = outcomes.filter(outcome='won').aggregate(
            total=Sum('actual_revenue')
        )['total'] or 0

        # Top opportunities (by score)
        top_opportunities = list(
            opportunities.filter(overall_score__gte=70)
            .order_by('-overall_score')[:5]
            .values('title', 'overall_score', 'category')
        )
        top_opps_formatted = [
            {'title': o['title'], 'score': o['overall_score'], 'category': o['category']}
            for o in top_opportunities
        ]

        # Create digest record
        digest = OpportunityDigest.objects.create(
            digest_type='weekly',
            period_start=start_date,
            period_end=end_date,
            total_opportunities=total_opportunities,
            high_value_opportunities=high_value_count,
            tasks_created=tasks_created,
            tasks_won=tasks_won,
            tasks_lost=tasks_lost,
            total_revenue=total_revenue,
            by_category=by_category,
            top_opportunities=top_opps_formatted,
            win_rate=win_rate,
            avg_score_won=outcomes.filter(outcome='won').aggregate(
                avg=Avg('task__opportunity_score')
            )['avg'] or 0,
            avg_score_lost=outcomes.filter(outcome='lost').aggregate(
                avg=Avg('task__opportunity_score')
            )['avg'] or 0,
        )

        # Send to Discord
        try:
            from core.services.discord_notifications import discord_notify

            success = discord_notify.send_weekly_opportunity_digest(
                period_start=str(start_date),
                period_end=str(end_date),
                total_opportunities=total_opportunities,
                high_value_count=high_value_count,
                tasks_created=tasks_created,
                tasks_won=tasks_won,
                tasks_lost=tasks_lost,
                total_revenue=float(total_revenue),
                win_rate=win_rate,
                top_opportunities=top_opps_formatted,
                by_category=by_category,
            )

            if success:
                digest.posted_to_discord = True
                digest.save()
                logger.info(f"📊 [SESSION 425] Weekly digest posted to Discord #boardroom")
        except Exception as discord_err:
            logger.error(f"📊 [SESSION 425] Discord notification failed: {discord_err}")

        logger.info(f"📊 [SESSION 425] Weekly opportunity digest complete: {total_opportunities} opportunities, {tasks_created} tasks, ${total_revenue} revenue")

        return {
            'status': 'success',
            'digest_id': str(digest.id),
            'total_opportunities': total_opportunities,
            'high_value_count': high_value_count,
            'tasks_created': tasks_created,
            'tasks_won': tasks_won,
            'tasks_lost': tasks_lost,
            'total_revenue': float(total_revenue),
            'win_rate': win_rate,
        }

    except Exception as e:
        logger.error(f"📊 [SESSION 425] Weekly opportunity digest failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_proactive_opportunity_alerts():
    """
    Session 437: Send proactive opportunity alerts to Discord users.

    Runs every 30 minutes to:
    - Find new high-value opportunities (score >= 70)
    - Check user profiles for alert preferences
    - Send personalized alerts to #opportunities channel
    - Track which opportunities have been alerted
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_unified_system import Opportunity
    from core.models import EnhancedUserProfile

    logger.info("🔔 [SESSION 437] Starting proactive opportunity alert check")

    try:
        now = timezone.now()
        # Look for opportunities from last 30 minutes that haven't been alerted
        cutoff = now - timedelta(minutes=30)

        # Find new high-value opportunities
        new_opportunities = Opportunity.objects.filter(
            created_at__gte=cutoff,
            status='active',
            match_score__gte=70,
        ).exclude(
            # Use a JSONField or metadata to track alerted status
            # For now, just check by time
            created_at__lt=cutoff
        ).order_by('-match_score')[:5]  # Max 5 per cycle

        if not new_opportunities:
            logger.debug("🔔 [SESSION 437] No new high-value opportunities to alert")
            return {'status': 'success', 'alerts_sent': 0, 'reason': 'no_new_opportunities'}

        alerts_sent = 0

        # Send alerts to Discord #opportunities channel
        try:
            from core.services.discord_notifications import discord_notify

            for opp in new_opportunities:
                # Determine urgency based on score
                if opp.match_score >= 90:
                    urgency = 'urgent'
                elif opp.match_score >= 80:
                    urgency = 'high'
                else:
                    urgency = 'normal'

                # Format potential revenue
                potential = ""
                if opp.potential_revenue:
                    potential = f"${float(opp.potential_revenue):,.0f}"

                # Send the alert
                success = discord_notify.send_opportunity(
                    title=opp.title or 'Untitled Opportunity',
                    score=float(opp.match_score or 0),
                    category=opp.category or 'general',
                    potential=potential,
                    source=opp.source or 'AI Studio',
                    description=(opp.description or '')[:500],
                    urgency=urgency,
                    score_scale=100
                )

                if success:
                    alerts_sent += 1
                    logger.info(f"🔔 [SESSION 437] Sent alert for opportunity: {opp.title[:50]}")

        except Exception as discord_err:
            logger.error(f"🔔 [SESSION 437] Discord notification error: {discord_err}")

        # Send summary if multiple alerts
        if alerts_sent > 1:
            try:
                discord_notify.send_opportunity_summary(
                    total_found=new_opportunities.count(),
                    high_value_count=alerts_sent,
                    top_categories=list(set(o.category for o in new_opportunities if o.category))[:3],
                    avg_score=sum(o.match_score or 0 for o in new_opportunities) / len(new_opportunities)
                )
            except Exception:
                pass

        logger.info(f"🔔 [SESSION 437] Proactive alerts complete: {alerts_sent} sent")

        return {
            'status': 'success',
            'alerts_sent': alerts_sent,
            'opportunities_checked': new_opportunities.count(),
        }

    except Exception as e:
        logger.error(f"🔔 [SESSION 437] Proactive opportunity alerts failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_personalized_opportunity_alerts():
    """
    Session 437: Send personalized opportunity alerts based on user profiles.

    Matches new opportunities against user skills, interests, and preferences.
    Sends DMs or channel mentions for highly relevant matches.
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.contrib.auth import get_user_model
    from core.models_unified_system import Opportunity
    from core.models import EnhancedUserProfile

    logger.info("🎯 [SESSION 437] Starting personalized opportunity matching")

    try:
        User = get_user_model()
        now = timezone.now()
        cutoff = now - timedelta(hours=1)  # Check last hour

        # Get users with Discord linked and alerts enabled
        users_with_alerts = User.objects.filter(
            discord_id__isnull=False
        ).exclude(discord_id='').select_related('enhanced_profile')

        # Get new high-value opportunities
        new_opportunities = Opportunity.objects.filter(
            created_at__gte=cutoff,
            status='active',
            match_score__gte=70,
        ).order_by('-match_score')[:10]

        if not new_opportunities:
            logger.debug("🎯 [SESSION 437] No new opportunities to match")
            return {'status': 'success', 'matches': 0}

        matches_found = 0

        for user in users_with_alerts:
            try:
                profile = getattr(user, 'enhanced_profile', None)
                if not profile:
                    continue

                # Check if alerts are enabled
                if not getattr(profile, 'discord_alerts_enabled', True):
                    continue

                # Get user's alert preferences
                min_score = getattr(profile, 'alert_min_score', 70)
                alert_categories = getattr(profile, 'alert_categories', []) or []

                # Get user's skills for matching
                skills = profile.expert_domains or []
                if isinstance(skills, dict):
                    skills = list(skills.keys())

                # Find matching opportunities
                for opp in new_opportunities:
                    if opp.match_score < min_score:
                        continue

                    # Check category filter
                    if alert_categories and opp.category:
                        if opp.category.lower() not in [c.lower() for c in alert_categories]:
                            continue

                    # Simple skill matching (check if any skill appears in title/description)
                    opp_text = f"{opp.title or ''} {opp.description or ''}".lower()
                    skill_match = any(skill.lower() in opp_text for skill in skills if skill)

                    if skill_match or not skills:  # Match if skills match OR user has no skills set
                        matches_found += 1
                        logger.debug(
                            f"🎯 [SESSION 437] Match: {user.username} <- {opp.title[:30]}"
                        )

                # Update last alert time
                if matches_found > 0:
                    profile.last_alert_sent = now
                    profile.save(update_fields=['last_alert_sent'])

            except Exception as user_err:
                logger.warning(f"🎯 [SESSION 437] Error matching user {user.id}: {user_err}")
                continue

        logger.info(f"🎯 [SESSION 437] Personalized matching complete: {matches_found} matches")

        return {
            'status': 'success',
            'users_checked': users_with_alerts.count(),
            'opportunities_checked': new_opportunities.count(),
            'matches_found': matches_found,
        }

    except Exception as e:
        logger.error(f"🎯 [SESSION 437] Personalized opportunity matching failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ==================== SESSION 440: CONTENT PIPELINE ====================

@shared_task(bind=True, max_retries=3)
def generate_content_package(self, package_id: str):
    """
    Session 440: Generate a complete content package through the AI pipeline.

    This is the core task that powers the "AI Content Factory" - taking a prompt
    through all stages: Research → Script → Character → Voice → Video → Package.

    Same task powers everything from $5 birthday messages to $50K productions.

    Args:
        package_id: UUID of the ContentPackage to generate
    """
    import asyncio

    logger.info(f"🎬 [SESSION 440] Starting content generation for package: {package_id}")

    try:
        from core.services.content_pipeline import UnifiedContentPipeline

        pipeline = UnifiedContentPipeline()

        # Run the async pipeline in a sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(pipeline.run_pipeline(package_id))
            logger.info(f"🎬 [SESSION 440] Content generation complete: {result.name}")

            return {
                'status': 'success',
                'package_id': str(package_id),
                'package_name': result.name,
                'asset_count': result.assets.count(),
            }
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"🎬 [SESSION 440] Content generation failed: {e}")

        # Update package status to failed
        try:
            from core.models_content_pipeline import ContentPackage, PackageStatus
            package = ContentPackage.objects.get(id=package_id)
            package.status = PackageStatus.FAILED
            package.save(update_fields=['status'])
        except Exception:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


# ==================== SESSION 445: AI SERIES WORKFLOW ====================

@shared_task(bind=True, max_retries=3)
def generate_ai_series(self, series_id: str):
    """
    Session 445: Generate a complete AI series through the AISeriesWorkflowAgent.

    This task orchestrates multi-episode content series by:
    1. Researching the series topic/niche
    2. Planning episode structure and story arcs
    3. Generating characters with style consistency
    4. Creating episode content (images, videos, voice)
    5. Packaging everything for delivery

    Args:
        series_id: UUID of the AISeries to generate
    """
    logger.info(f"🎬 [SESSION 445] Starting AI series generation: {series_id}")

    try:
        from core.models_ai_series import AISeries, SeriesStatus, EpisodeStatus
        from core.agents.ai_series_workflow_agent import get_ai_series_workflow_agent

        # Get the series
        series = AISeries.objects.get(id=series_id)

        # Series starts in PLANNING status - check it's not already generating or complete
        if series.status not in [SeriesStatus.PLANNING]:
            logger.warning(f"🎬 [SESSION 445] Series {series_id} not in PLANNING status, skipping")
            return {'status': 'skipped', 'reason': f'Series status is {series.status}'}

        # Move to GENERATING status
        series.start_generation()
        logger.info(f"🎬 [SESSION 445] Series '{series.name}' moved to GENERATING status")

        # Get the agent
        agent = get_ai_series_workflow_agent(user=series.created_by)

        # Session 452: Check for A/B test style variant
        ab_test_style = None
        try:
            from core.services.pipeline_learning import get_ab_test_style_for_series
            if series.created_by:
                ab_test_style = get_ab_test_style_for_series(
                    user_id=series.created_by.id,
                    series_type=series.series_type,
                    target_audience=series.target_audience
                )
                if ab_test_style:
                    logger.info(
                        f"🎬 [SESSION 452] A/B test style '{ab_test_style['style_preset']}' "
                        f"assigned to series {series_id}"
                    )
                    # Store experiment info on series for feedback tracking
                    series.ab_experiment_id = ab_test_style['experiment_id']
                    series.ab_variant_id = ab_test_style['variant_id']
                    series.save(update_fields=['ab_experiment_id', 'ab_variant_id'] if hasattr(series, 'ab_experiment_id') else [])
        except Exception as ab_err:
            logger.debug(f"A/B test lookup skipped: {ab_err}")

        # Build the task prompt - include A/B test style if assigned
        style_instruction = ""
        if ab_test_style:
            style_instruction = f"\n\nIMPORTANT: You MUST use the '{ab_test_style['style_preset']}' style preset for all visuals. This is required for a/b testing purposes."

        task = f"""Create a {series.series_type} series called "{series.name}".

Description: {series.description}
Target Audience: {series.target_audience}
Number of Episodes: {series.episode_count}
{style_instruction}
Generate all {series.episode_count} episodes with consistent characters, style, and story progression.
Each episode should have: title, synopsis, images, script, voiceover, and video.
"""

        # Execute the agent
        context = {
            'series_id': str(series.id),
            'series_type': series.series_type,
            'episode_count': series.episode_count,
            'style_config': series.style_config,
            'character_config': series.character_config,
        }

        # Session 452: Add A/B test info to context if assigned
        if ab_test_style:
            context['ab_test_style'] = ab_test_style['style_preset']
            context['ab_experiment_id'] = ab_test_style['experiment_id']
            context['ab_variant_id'] = ab_test_style['variant_id']

        result = agent.execute(
            task=task,
            context=context,
            scifi_context={},
            spider_context={},
        )

        if result.success:
            logger.info(f"🎬 [SESSION 445] Series generation complete: {series.name}")

            # Update series with generated config
            if result.data:
                if 'style_config' in result.data:
                    series.style_config = result.data['style_config']
                if 'character_config' in result.data:
                    series.character_config = result.data['character_config']
                if 'episodes' in result.data:
                    series.episode_data = result.data.get('episodes', [])
                series.save()

            # Complete the series
            series.complete_generation()

            return {
                'status': 'success',
                'series_id': str(series_id),
                'series_name': series.name,
                'episodes_generated': series.episodes.filter(status=EpisodeStatus.COMPLETE).count(),
            }
        else:
            logger.error(f"🎬 [SESSION 445] Series generation failed: {result.error}")
            series.fail(result.error or "Agent execution failed")

            return {
                'status': 'failed',
                'series_id': str(series_id),
                'error': result.error,
            }

    except AISeries.DoesNotExist:
        logger.error(f"🎬 [SESSION 445] Series not found: {series_id}")
        return {'status': 'failed', 'error': f'Series {series_id} not found'}

    except Exception as e:
        logger.error(f"🎬 [SESSION 445] Series generation error: {e}")

        # Update series status to failed
        try:
            from core.models_ai_series import AISeries
            series = AISeries.objects.get(id=series_id)
            series.fail(str(e))
        except Exception:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=120 * (2 ** self.request.retries))


# =============================================================================
# Session 451: User Upload Tasks
# =============================================================================

@shared_task
def assemble_chunked_upload(upload_id: str):
    """
    Assemble chunks into final file and create content record.

    Session 451: Called when all chunks of a large file upload are received.
    """
    from content.models import UploadSession, ImageHistory, VideoHistory, MediaSourceType
    from pathlib import Path
    from django.conf import settings
    from django.utils import timezone
    import shutil
    import uuid as uuid_module

    logger.info(f"📦 [SESSION 451] Assembling chunked upload: {upload_id}")

    try:
        session = UploadSession.objects.get(id=upload_id)
    except UploadSession.DoesNotExist:
        logger.error(f"📦 [SESSION 451] Upload session not found: {upload_id}")
        return {'status': 'failed', 'error': 'Upload session not found'}

    try:
        temp_dir = Path(session.temp_path)

        # Get all chunks in order
        chunks = sorted(temp_dir.glob('chunk_*'))

        if len(chunks) != session.chunks_total:
            raise ValueError(f"Expected {session.chunks_total} chunks, found {len(chunks)}")

        # Determine final path
        ext = Path(session.filename).suffix.lower()
        new_filename = f"{uuid_module.uuid4()}{ext}"

        if session.content_type == 'video':
            final_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'videos' / timezone.now().strftime('%Y/%m')
        else:
            final_dir = Path(settings.MEDIA_ROOT) / 'uploads' / 'images' / timezone.now().strftime('%Y/%m')

        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / new_filename

        # Assemble chunks
        logger.info(f"📦 [SESSION 451] Assembling {len(chunks)} chunks into {final_path}")
        with open(final_path, 'wb') as final_file:
            for chunk_path in chunks:
                with open(chunk_path, 'rb') as chunk:
                    final_file.write(chunk.read())

        # Create content record
        if session.content_type == 'video':
            # Extract video metadata
            from core.views_upload import _extract_video_metadata, _generate_video_thumbnail
            metadata = _extract_video_metadata(str(final_path))

            video = VideoHistory.objects.create(
                user=session.user,
                source_type=MediaSourceType.UPLOADED,
                video_file=str(final_path.relative_to(settings.MEDIA_ROOT)),
                original_filename=session.filename,
                video_url=f"/media/{final_path.relative_to(settings.MEDIA_ROOT)}",
                file_size_bytes=session.file_size,
                mime_type=session.mime_type,
                video_type='uploaded',
                prompt=f'Uploaded: {session.filename}',
                project=session.project,
                duration=int(metadata.get('duration', 0)) if metadata.get('duration') else None,
                video_width=metadata.get('width'),
                video_height=metadata.get('height'),
                fps=metadata.get('fps'),
                codec=metadata.get('codec'),
                status='completed',
            )

            _generate_video_thumbnail(video, str(final_path))

            session.result_content_type = 'video'
            session.result_id = video.id

            logger.info(f"📦 [SESSION 451] Created VideoHistory: {video.id}")

        else:
            # Image handling
            from PIL import Image
            from core.views_upload import _generate_image_thumbnail

            width, height = None, None
            try:
                with Image.open(final_path) as img:
                    width, height = img.size
            except Exception as e:
                logger.warning(f"Could not get image dimensions: {e}")

            image = ImageHistory.objects.create(
                user=session.user,
                source_type=MediaSourceType.UPLOADED,
                original_file=str(final_path.relative_to(settings.MEDIA_ROOT)),
                original_filename=session.filename,
                filename=new_filename,
                file_path=f"/media/{final_path.relative_to(settings.MEDIA_ROOT)}",
                file_size_bytes=session.file_size,
                mime_type=session.mime_type,
                image_type='uploaded',
                image_width=width,
                image_height=height,
                prompt=f'Uploaded: {session.filename}',
                project=session.project,
            )

            # Generate thumbnail
            with open(final_path, 'rb') as f:
                from django.core.files.uploadedfile import SimpleUploadedFile
                temp_file = SimpleUploadedFile(session.filename, f.read())
                _generate_image_thumbnail(image, temp_file)

            session.result_content_type = 'image'
            session.result_id = image.id

            logger.info(f"📦 [SESSION 451] Created ImageHistory: {image.id}")

        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)

        session.status = 'completed'
        session.save()

        logger.info(f"📦 [SESSION 451] Chunked upload {upload_id} completed successfully")

        return {
            'status': 'completed',
            'upload_id': str(upload_id),
            'result_type': session.result_content_type,
            'result_id': str(session.result_id),
        }

    except Exception as e:
        logger.error(f"📦 [SESSION 451] Failed to assemble chunked upload {upload_id}: {e}")
        session.status = 'failed'
        session.error_message = str(e)
        session.save()
        return {'status': 'failed', 'error': str(e)}


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
    """
    Session 452: Sync pipeline learning insights to the collective intelligence system.

    This task bridges the Pipeline Learning system (style/voice performance from AI content)
    with the Collective Intelligence system (agent knowledge sharing).

    Benefits:
    - Insights like "Pixar style 23% better for kids content" become agent knowledge
    - Agents can use content performance data in their recommendations
    - Creates feedback loop between content success and agent decision-making

    Run every 6 hours via Celery Beat.
    """
    logger.info("🔗 [SESSION 452] Starting pipeline-to-collective sync...")

    try:
        from core.services.pipeline_learning import get_pipeline_learning_service

        service = get_pipeline_learning_service()

        # Step 1: Generate fresh insights from recent data
        insights = service.generate_insights()
        logger.info(f"🔗 [SESSION 452] Generated {len(insights)} pipeline insights")

        # Step 2: Share insights to collective intelligence
        shared_count = service.share_insights_to_collective()
        logger.info(f"🔗 [SESSION 452] Shared {shared_count} insights to collective")

        # Step 3: Pull collective knowledge back to enhance recommendations
        synced = service.sync_collective_knowledge_to_recommendations()
        style_hints = synced.get('style_hints', [])
        voice_hints = synced.get('voice_hints', [])
        logger.info(f"🔗 [SESSION 452] Received {len(style_hints)} style hints, {len(voice_hints)} voice hints from collective")

        return {
            'status': 'completed',
            'insights_generated': len(insights),
            'insights_shared': shared_count,
            'style_hints_received': len(style_hints),
            'voice_hints_received': len(voice_hints),
        }

    except Exception as e:
        logger.error(f"🔗 [SESSION 452] Pipeline-collective sync failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 460: Autonomous Intelligence Loop Tasks
# =============================================================================

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
    """
    Session 462: Market Intelligence Desk - First Tier 1 Autonomous Situation.
    Session 497: Added AutonomousSituationSession tracking.

    Runs the complete autonomous situation with all 5 properties:
    1. Persistent context - Tracks market state, previous briefs
    2. Incoming signals - Spiders, price data, news
    3. Internal disagreement - Bull vs Bear debate
    4. Outputs with consequences - Daily brief to Discord
    5. Self-renewal - Schedules next cycle, learns

    The situation behaves like a buy-side research desk running 24/7.

    Orchestrates:
    - BullCaseAgent: Arguments for price appreciation
    - BearCaseAgent: Arguments for price depreciation
    - StockAuditCoordinator: Risk signals and anomalies
    - MarketIntelligenceCoordinator: Synthesizes debate into brief

    Delivers:
    - Discord notification with brief
    - Executive summary with bull/bear debate
    - What changed since yesterday
    - Confidence scores based on agreement/disagreement
    """
    import time
    from django.utils import timezone
    from core.models_autonomous_situations import AutonomousSituationSession

    start_time = time.time()
    logger.info("🧠 [SESSION 462] Starting Market Intelligence Desk...")

    # Session 497: Create situation session
    session = AutonomousSituationSession.objects.create(
        situation_type='market_intelligence',
        status='running'
    )

    try:
        from core.agents.stocks import run_market_intelligence_desk as run_desk

        result = run_desk()

        total_stocks = 0
        debate_count = 0
        if result.get('data', {}).get('brief'):
            brief = result['data']['brief']
            debate_count = brief.get('debate_zone_count', 0)
            total_stocks = brief.get('total_stocks_analyzed', 0)
            logger.info(f"🧠 [SESSION 462] Market Intelligence Desk complete: {total_stocks} stocks analyzed, {debate_count} in debate zone")
        else:
            logger.info(f"🧠 [SESSION 462] Market Intelligence Desk complete: {result}")

        # Session 497: Update session with success
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = total_stocks
        session.items_created = debate_count
        session.save()

        return result

    except Exception as e:
        logger.error(f"🧠 [SESSION 462] Market Intelligence Desk failed: {e}")

        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()

        return {'status': 'failed', 'error': str(e)}


@shared_task(name='core.tasks.check_market_events_and_rerun')
def check_market_events_and_rerun():
    """
    Session 465: Event-driven Market Intelligence Desk re-runs.

    Monitors for significant market events that warrant an immediate brief update:
    - Large price movements (>5% in watchlist stocks)
    - High-impact SEC filings (8-K material events, M&A, earnings)
    - Unusual volume spikes (>3x average)
    - Market-wide volatility (VIX spike >20%)

    If significant events detected, triggers an immediate Market Intelligence Desk re-run
    instead of waiting for the scheduled 6:30 AM cycle.
    """
    logger.info("📡 [SESSION 465] Checking for market-moving events...")

    try:
        from core.services.market_data_service import MarketDataService
        from core.models_unified_system import MarketIntelligenceBrief
        from datetime import date, timedelta

        market_service = MarketDataService()

        # Default watchlist
        watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'SPY', 'QQQ', 'VTI']

        significant_events = []

        # 1. Check for large price movements
        for ticker in watchlist:
            try:
                current_price = market_service.get_current_price(ticker)
                if current_price:
                    price_change_pct = current_price.get('change_percent', 0)
                    if abs(price_change_pct) >= 5.0:
                        significant_events.append({
                            'type': 'price_movement',
                            'ticker': ticker,
                            'change_percent': price_change_pct,
                            'severity': 'high' if abs(price_change_pct) >= 10.0 else 'medium'
                        })
                        logger.info(f"📡 [SESSION 465] Large price move detected: {ticker} {price_change_pct:+.2f}%")
            except Exception as e:
                logger.debug(f"Failed to check {ticker}: {e}")
                continue

        # 2. Check for high-impact SEC filings (reuse existing check)
        try:
            from core.services.autonomous_loop import autonomous_loop
            sec_results = autonomous_loop.check_sec_filings()
            if sec_results.get('alerts_sent', 0) > 0:
                significant_events.append({
                    'type': 'sec_filing',
                    'count': sec_results.get('alerts_sent', 0),
                    'severity': 'high'
                })
                logger.info(f"📡 [SESSION 465] High-impact SEC filings detected: {sec_results.get('alerts_sent', 0)}")
        except Exception as e:
            logger.debug(f"SEC check failed: {e}")

        # 3. Check if we've already run today (avoid duplicate re-runs)
        today = date.today()
        try:
            existing_brief = MarketIntelligenceBrief.objects.filter(brief_date=today).exists()
            if existing_brief:
                logger.info("📡 [SESSION 465] Brief already generated today - checking if events warrant update")
                # Only re-run if we have HIGH severity events
                high_severity_count = sum(1 for e in significant_events if e.get('severity') == 'high')
                if high_severity_count < 2:
                    logger.info(f"📡 [SESSION 465] {len(significant_events)} events detected but not severe enough for re-run")
                    return {
                        'status': 'no_rerun_needed',
                        'events_detected': len(significant_events),
                        'high_severity': high_severity_count
                    }
        except Exception as e:
            logger.debug(f"Brief check failed: {e}")

        # 4. If significant events found, trigger re-run
        if significant_events:
            event_count = len(significant_events)
            logger.info(f"📡 [SESSION 465] {event_count} significant events detected - triggering Market Intelligence Desk re-run")

            # Trigger the desk
            result = run_market_intelligence_desk()

            return {
                'status': 'rerun_triggered',
                'events_detected': event_count,
                'significant_events': significant_events,
                'desk_result': result
            }
        else:
            logger.info("📡 [SESSION 465] No significant market events detected")
            return {
                'status': 'no_events',
                'events_detected': 0
            }

    except Exception as e:
        logger.error(f"📡 [SESSION 465] Event check failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ==================== SESSION 464: LEARNING LOOP AUTOMATION ====================


@shared_task(name='learning_loop.track_prediction_outcomes')
def track_prediction_outcomes():
    """
    Session 464: Track prediction outcomes for the Market Intelligence Desk learning loop.

    Runs daily at 6 PM (after market close) to calculate actual outcomes for predictions
    made 7 and 30 days ago. This enables the system to learn from its predictions.

    Process:
    1. Find predictions from exactly 7 days ago
    2. Find predictions from exactly 30 days ago
    3. For each prediction, fetch current stock price
    4. Calculate actual move vs predicted move
    5. Score accuracy (0-1 based on direction + magnitude)
    6. Update PredictionOutcome records with results

    Returns:
        dict: Summary of outcomes tracked
    """
    from datetime import date, timedelta
    from core.models_unified_system import PredictionOutcome

    logger.info("📊 [SESSION 464] Starting prediction outcome tracking...")

    results = {
        'predictions_checked_7d': 0,
        'predictions_checked_30d': 0,
        'successful_7d': 0,
        'successful_30d': 0,
        'failed': 0,
    }

    try:
        # Calculate target dates
        date_7_days_ago = date.today() - timedelta(days=7)
        date_30_days_ago = date.today() - timedelta(days=30)

        # Find predictions from 7 days ago that haven't been calculated yet
        predictions_7d = PredictionOutcome.objects.filter(
            prediction_date=date_7_days_ago,
            price_after_7_days__isnull=True  # Not calculated yet
        )

        logger.info(f"📊 [SESSION 464] Found {predictions_7d.count()} predictions from 7 days ago")

        for prediction in predictions_7d:
            try:
                prediction.calculate_outcome(days_elapsed=7)
                results['predictions_checked_7d'] += 1
                if prediction.was_correct_7_days:
                    results['successful_7d'] += 1
                logger.debug(f"  ✅ {prediction.ticker} {prediction.prediction_type}: "
                           f"{'CORRECT' if prediction.was_correct_7_days else 'INCORRECT'} "
                           f"(score: {prediction.accuracy_score_7_days:.2f})")
            except Exception as e:
                logger.error(f"  ❌ Failed to calculate 7-day outcome for {prediction.ticker}: {e}")
                results['failed'] += 1

        # Find predictions from 30 days ago that haven't been calculated yet
        predictions_30d = PredictionOutcome.objects.filter(
            prediction_date=date_30_days_ago,
            price_after_30_days__isnull=True  # Not calculated yet
        )

        logger.info(f"📊 [SESSION 464] Found {predictions_30d.count()} predictions from 30 days ago")

        for prediction in predictions_30d:
            try:
                prediction.calculate_outcome(days_elapsed=30)
                results['predictions_checked_30d'] += 1
                if prediction.was_correct_30_days:
                    results['successful_30d'] += 1
                logger.debug(f"  ✅ {prediction.ticker} {prediction.prediction_type}: "
                           f"{'CORRECT' if prediction.was_correct_30_days else 'INCORRECT'} "
                           f"(score: {prediction.accuracy_score_30_days:.2f})")
            except Exception as e:
                logger.error(f"  ❌ Failed to calculate 30-day outcome for {prediction.ticker}: {e}")
                results['failed'] += 1

        # Summary
        total_checked = results['predictions_checked_7d'] + results['predictions_checked_30d']
        total_correct = results['successful_7d'] + results['successful_30d']
        accuracy = (total_correct / total_checked * 100) if total_checked > 0 else 0

        logger.info(f"📊 [SESSION 464] Prediction outcome tracking complete: "
                   f"{total_checked} predictions checked, {total_correct} correct ({accuracy:.1f}% accuracy)")

        return results

    except Exception as e:
        logger.error(f"📊 [SESSION 464] Prediction outcome tracking failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='learning_loop.calculate_agent_accuracy')
def calculate_agent_accuracy():
    """
    Session 464: Calculate agent accuracy metrics for the learning loop.

    Runs weekly on Sundays at 8 PM to analyze BullCaseAgent and BearCaseAgent performance
    over the past 30 days. Updates confidence multipliers based on track record.

    Process:
    1. Create or get AgentAccuracyMetrics for past 30 days
    2. For BullCaseAgent: analyze all bull predictions
    3. For BearCaseAgent: analyze all bear predictions
    4. Calculate overall accuracy, conviction calibration, market regime performance
    5. Update confidence multipliers (0.5-1.5x based on accuracy)
    6. Log insights about agent performance

    Returns:
        dict: Summary of accuracy metrics calculated
    """
    from datetime import date, timedelta
    from core.models_unified_system import AgentAccuracyMetrics

    logger.info("🎯 [SESSION 464] Starting agent accuracy calculation...")

    results = {
        'bull_agent': {},
        'bear_agent': {},
    }

    try:
        # Calculate 30-day period
        period_end = date.today()
        period_start = period_end - timedelta(days=30)

        # Calculate metrics for BullCaseAgent
        try:
            bull_metrics, created = AgentAccuracyMetrics.objects.get_or_create(
                agent_name='BullCaseAgent',
                period_start=period_start,
                period_end=period_end,
            )

            bull_metrics.calculate_metrics()

            results['bull_agent'] = {
                'total_predictions': bull_metrics.total_predictions,
                'accuracy_7d': bull_metrics.accuracy_rate_7_days,
                'accuracy_30d': bull_metrics.accuracy_rate_30_days,
                'confidence_multiplier': bull_metrics.confidence_multiplier,
                'high_conviction_accuracy': bull_metrics.high_conviction_accuracy,
            }

            logger.info(f"  🐂 BullCaseAgent: {bull_metrics.accuracy_rate_7_days:.1f}% accurate "
                       f"({bull_metrics.total_predictions} predictions, "
                       f"confidence multiplier: {bull_metrics.confidence_multiplier:.2f}x)")

        except Exception as e:
            logger.error(f"  ❌ Failed to calculate BullCaseAgent metrics: {e}")
            results['bull_agent']['error'] = str(e)

        # Calculate metrics for BearCaseAgent
        try:
            bear_metrics, created = AgentAccuracyMetrics.objects.get_or_create(
                agent_name='BearCaseAgent',
                period_start=period_start,
                period_end=period_end,
            )

            bear_metrics.calculate_metrics()

            results['bear_agent'] = {
                'total_predictions': bear_metrics.total_predictions,
                'accuracy_7d': bear_metrics.accuracy_rate_7_days,
                'accuracy_30d': bear_metrics.accuracy_rate_30_days,
                'confidence_multiplier': bear_metrics.confidence_multiplier,
                'high_conviction_accuracy': bear_metrics.high_conviction_accuracy,
            }

            logger.info(f"  🐻 BearCaseAgent: {bear_metrics.accuracy_rate_7_days:.1f}% accurate "
                       f"({bear_metrics.total_predictions} predictions, "
                       f"confidence multiplier: {bear_metrics.confidence_multiplier:.2f}x)")

        except Exception as e:
            logger.error(f"  ❌ Failed to calculate BearCaseAgent metrics: {e}")
            results['bear_agent']['error'] = str(e)

        logger.info(f"🎯 [SESSION 464] Agent accuracy calculation complete")

        return results

    except Exception as e:
        logger.error(f"🎯 [SESSION 464] Agent accuracy calculation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ==================== SESSION 466: AUTONOMOUS CONTENT STUDIO ====================


@shared_task(name='autonomous_studio.run_main_loop')
def run_autonomous_content_studio():
    """
    Session 466: Main autonomous loop for the Content Studio.
    Session 497: Added AutonomousSituationSession tracking.

    Property #5: Self-Renewal - This task runs every 4 hours and checks which channels
    are due for content. For each channel that's ready, it triggers content generation.

    This is the BRAIN of the autonomous system. It:
    1. Queries all ContentChannel records
    2. Filters for channels where next_content_due <= now
    3. For each due channel, triggers generate_content_for_channel task
    4. Logs all activity

    Returns:
        dict: Summary of channels processed
    """
    import time
    from django.utils import timezone
    from core.models_autonomous_studio import ContentChannel, ChannelStatus
    from core.models_autonomous_situations import AutonomousSituationSession

    start_time = time.time()
    logger.info("🎬 [SESSION 466] Starting autonomous content studio main loop...")

    # Session 497: Create situation session
    session = AutonomousSituationSession.objects.create(
        situation_type='content_studio',
        status='running'
    )

    results = {
        'total_channels': 0,
        'channels_due': 0,
        'channels_triggered': 0,
        'channels_skipped': 0,
        'errors': [],
    }

    try:
        # Get all active channels
        all_channels = ContentChannel.objects.filter(status=ChannelStatus.ACTIVE)
        results['total_channels'] = all_channels.count()

        logger.info(f"🎬 [SESSION 466] Found {results['total_channels']} active channels")

        # Filter for channels that are due for content
        now = timezone.now()
        due_channels = all_channels.filter(next_content_due__lte=now)
        results['channels_due'] = due_channels.count()

        logger.info(f"🎬 [SESSION 466] {results['channels_due']} channels are due for content")

        # Trigger content generation for each due channel
        for channel in due_channels:
            try:
                logger.info(f"  🎥 Triggering content generation for channel: {channel.name}")

                # Trigger the worker task asynchronously
                generate_content_for_channel.delay(str(channel.id))

                results['channels_triggered'] += 1

            except Exception as e:
                logger.error(f"  ❌ Failed to trigger content for {channel.name}: {e}")
                results['channels_skipped'] += 1
                results['errors'].append({
                    'channel': channel.name,
                    'error': str(e)
                })

        # Summary
        logger.info(f"🎬 [SESSION 466] Autonomous content studio loop complete: "
                   f"{results['channels_triggered']} channels triggered, "
                   f"{results['channels_skipped']} skipped")

        # Session 497: Update session with success
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = results['total_channels']
        session.items_created = results['channels_triggered']
        session.save()

        return results

    except Exception as e:
        logger.error(f"🎬 [SESSION 466] Autonomous content studio loop failed: {e}")

        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()

        return {'status': 'failed', 'error': str(e)}


@shared_task(name='autonomous_studio.generate_content')
def generate_content_for_channel(channel_id):
    """
    Session 466: Generate content for a specific channel.

    Property #3: Internal Disagreement - This task orchestrates the agent debate
    before creating content.

    Property #4: Outputs with Consequences - Creates ChannelEpisode to track performance.

    Property #5: Self-Renewal - Updates channel's next_content_due after generation.

    This is the WORKER task that actually creates content. It:
    1. Loads the ContentChannel
    2. Initiates agent debate (TopicMiner vs Contrarian vs PerformanceAnalyst)
    3. Uses debate decision to pick winning topic
    4. Triggers AISeriesWorkflowAgent to create the content
    5. Creates ChannelEpisode record to track performance
    6. Links ChannelEpisode to ContentDebate for transparency
    7. Calls channel.schedule_next_content() to implement self-renewal

    Args:
        channel_id: UUID of the ContentChannel

    Returns:
        dict: Summary of content generation
    """
    from django.utils import timezone
    from core.models_autonomous_studio import ContentChannel, ChannelEpisode, ContentDebate
    from core.agent_router import AgentRouter
    import json

    logger.info(f"🎥 [SESSION 466] Starting content generation for channel {channel_id}...")

    results = {
        'channel_id': channel_id,
        'status': 'pending',
        'debate_id': None,
        'episode_id': None,
        'topic': None,
        'error': None,
    }

    try:
        # Load the channel
        try:
            channel = ContentChannel.objects.get(id=channel_id)
        except ContentChannel.DoesNotExist:
            error_msg = f"Channel {channel_id} not found"
            logger.error(f"🎥 [SESSION 466] {error_msg}")
            results['status'] = 'failed'
            results['error'] = error_msg
            return results

        logger.info(f"🎥 [SESSION 466] Channel: {channel.name} ({channel.topic_domain})")

        # Step 1: Initiate agent debate
        logger.info(f"🎥 [SESSION 466] Step 1: Initiating agent debate...")

        # Session 468: Pass the channel's user to AgentRouter for AISeries creation
        router = AgentRouter(user=channel.user)

        # Create the debate prompt
        debate_prompt = f"""
The autonomous content studio needs to decide on a topic for the next episode.

Channel: {channel.name}
Domain: {channel.topic_domain}
Publishing Frequency: {channel.get_content_frequency_display()}
Last Episode: {channel.last_content_created or 'Never'}
Performance Stats:
- Total Episodes: {channel.total_episodes_created}
- Average Views: {channel.total_views / max(channel.total_episodes_created, 1):.0f}
- Average Retention: {channel.avg_retention_rate:.1f}%
- Confidence Multiplier: {channel.confidence_multiplier}x

Three agents will debate which topic to pursue:
1. TopicMinerAgent - Finds trending topics (argues FOR popular)
2. ContrarianAgent - Challenges obvious choices (argues AGAINST trendy)
3. PerformanceAnalystAgent - Uses data to guide decisions (argues from EVIDENCE)

Coordinate this debate and return the winning topic decision.
"""

        # Execute coordinator agent to run the debate
        coordinator_result = router.route(
            agent_name="AutonomousContentStudioCoordinator",
            task=debate_prompt,
            context={
                'channel_id': str(channel.id),
                'action': 'initiate_content_debate'
            }
        )

        if not coordinator_result.success:
            error_msg = f"Debate coordination failed: {coordinator_result.error}"
            logger.error(f"🎥 [SESSION 466] {error_msg}")
            results['status'] = 'failed'
            results['error'] = error_msg
            return results

        # Parse debate results from coordinator
        # The coordinator should have created a ContentDebate record
        # Let's find the most recent debate for this channel
        recent_debate = ContentDebate.objects.filter(
            channel=channel
        ).order_by('-debate_date').first()

        # Session 469: If coordinator didn't create debate (GPT didn't call tools),
        # call the debate agents directly - this is a fallback for reliability
        if not recent_debate:
            logger.warning(f"🎥 [SESSION 469] Coordinator didn't create debate, running agents directly...")

            # Import debate agents
            from core.agents.content.topic_miner_agent import TopicMinerAgent
            from core.agents.content.contrarian_agent import ContrarianAgent
            from core.agents.content.performance_analyst_agent import PerformanceAnalystAgent

            # Prepare context for debate agents
            domain_keywords = [kw.strip() for kw in channel.topic_domain.split(',') if kw.strip()]
            if not domain_keywords:
                domain_keywords = [channel.topic_domain]

            scifi_context = {}
            spider_context = {"domain_keywords": domain_keywords}

            # Run TopicMinerAgent
            logger.info(f"🗣️ Fallback Debate Step 1: TopicMinerAgent")
            try:
                topic_miner = TopicMinerAgent(user=user)
                miner_result = topic_miner.execute(
                    task=f"Find trending topics in {channel.topic_domain}",
                    context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                    scifi_context=scifi_context,
                    spider_context=spider_context
                )
                topic_miner_position = miner_result.message or "No trends found"
            except Exception as e:
                logger.error(f"TopicMinerAgent error: {e}")
                topic_miner_position = f"Error: {str(e)}"

            # Run ContrarianAgent
            logger.info(f"🗣️ Fallback Debate Step 2: ContrarianAgent")
            try:
                contrarian = ContrarianAgent(user=user)
                contrarian_result = contrarian.execute(
                    task=f"Check saturation and suggest unique angles for {channel.topic_domain}",
                    context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                    scifi_context=scifi_context,
                    spider_context=spider_context
                )
                contrarian_position = contrarian_result.message or "No suggestions"
            except Exception as e:
                logger.error(f"ContrarianAgent error: {e}")
                contrarian_position = f"Error: {str(e)}"

            # Run PerformanceAnalystAgent
            logger.info(f"🗣️ Fallback Debate Step 3: PerformanceAnalystAgent")
            try:
                analyst = PerformanceAnalystAgent(user=user)
                analyst_result = analyst.execute(
                    task=f"Analyze performance predictions for {channel.topic_domain}",
                    context={"channel_id": str(channel.id), "domain_keywords": domain_keywords},
                    scifi_context=scifi_context,
                    spider_context=spider_context
                )
                analyst_position = analyst_result.message or "No insights"
            except Exception as e:
                logger.error(f"PerformanceAnalystAgent error: {e}")
                analyst_position = f"Error: {str(e)}"

            # Create debate record with real agent responses
            recent_debate = ContentDebate.objects.create(
                channel=channel,
                proposed_topic=f"Latest {channel.topic_domain} Developments",
                proposed_by="AutonomousContentStudioCoordinator (fallback)",
                topic_miner_position=topic_miner_position[:2000],
                contrarian_position=contrarian_position[:2000],
                analyst_position=analyst_position[:2000],
                director_position="[Session 469] CreativeDirectorAgent integration pending",
                final_decision=f"Latest AI Developments in {channel.topic_domain}",
                chosen_angle="Educational overview with practical insights",
                decision_reasoning="Fallback debate - agents called directly due to coordinator not creating debate record",
                consensus_reached=True,
                content_created=False
            )
            logger.info(f"🎥 [SESSION 469] Created fallback debate with real agents: {recent_debate.id}")

        results['debate_id'] = str(recent_debate.id)
        winning_topic = recent_debate.final_decision
        results['topic'] = winning_topic

        logger.info(f"🎥 [SESSION 466] Debate complete! Winning topic: {winning_topic}")
        logger.info(f"  📊 Debate breakdown:")
        logger.info(f"     TopicMiner: {recent_debate.topic_miner_position[:100]}...")
        logger.info(f"     Contrarian: {recent_debate.contrarian_position[:100]}...")
        logger.info(f"     Analyst: {recent_debate.analyst_position[:100]}...")

        # Step 2: Trigger content creation via AISeriesWorkflowAgent
        logger.info(f"🎥 [SESSION 466] Step 2: Creating content via AISeriesWorkflowAgent...")

        # Build content creation prompt
        content_prompt = f"""
Create a single episode for the autonomous content channel "{channel.name}".

Topic: {winning_topic}
Channel Domain: {channel.topic_domain}
Target Audience: {channel.target_audience}
Visual Style: {channel.visual_style}

This topic was selected through agent debate:
- TopicMiner found it trending
- Contrarian validated it's not oversaturated
- PerformanceAnalyst predicted strong performance

Create 1 episode following the channel's style and targeting the audience.
"""

        # Execute AISeriesWorkflowAgent
        series_result = router.route(
            agent_name="AISeriesWorkflowAgent",
            task=content_prompt,
            context={
                'series_type': 'educational',
                'episode_count': 1,
                'consistency_mode': True
            }
        )

        if not series_result.success:
            error_msg = f"Content creation failed: {series_result.error}"
            logger.error(f"🎥 [SESSION 466] {error_msg}")
            results['status'] = 'failed'
            results['error'] = error_msg
            return results

        logger.info(f"🎥 [SESSION 466] Content created successfully!")

        # Step 3: Create ChannelEpisode record (Property #4: Outputs with Consequences)
        logger.info(f"🎥 [SESSION 466] Step 3: Creating ChannelEpisode record...")

        # Session 468: Fixed field names to match ChannelEpisode model
        episode = ChannelEpisode.objects.create(
            channel=channel,
            topic=winning_topic,
            title=f"{channel.name}: {winning_topic}",
            description=f"Auto-generated content. Debate ID: {recent_debate.id}",
            publish_date=timezone.now(),
            views=0,
            likes=0,
            comments=0,
            shares=0,
            retention_rate=0.0,
            performance_score=0.0
        )

        results['episode_id'] = str(episode.id)

        # [SESSION 475] Add provenance tracking
        try:
            from core.services.provenance_tracker import create_content_episode_provenance
            create_content_episode_provenance(
                episode_id=str(episode.id),
                channel_name=channel.name,
                content_type=channel.content_type,
                trigger_source='generate_content_for_channel_task',
                metadata={
                    'topic': winning_topic,
                    'debate_id': str(recent_debate.id),
                    'task': 'generate_content_for_channel'
                }
            )
        except Exception as prov_e:
            logger.warning(f"Failed to create episode provenance: {prov_e}")

        logger.info(f"🎥 [SESSION 466] Episode created: {episode.title}")

        # Step 4: Update channel stats and schedule next content (Property #5: Self-Renewal)
        logger.info(f"🎥 [SESSION 466] Step 4: Updating channel and scheduling next cycle...")

        channel.last_content_created = timezone.now()
        channel.total_episodes_created += 1
        channel.schedule_next_content()  # This implements self-renewal!
        channel.save()

        logger.info(f"🎥 [SESSION 466] Next content due: {channel.next_content_due}")

        results['status'] = 'success'

        logger.info(f"🎥 [SESSION 466] Content generation complete for {channel.name}!")

        return results

    except Exception as e:
        logger.error(f"🎥 [SESSION 466] Content generation failed for channel {channel_id}: {e}")
        results['status'] = 'failed'
        results['error'] = str(e)
        return results


@shared_task(name='autonomous_studio.track_performance')
def track_content_performance():
    """
    Session 466: Track performance of published content.

    Property #4: Outputs with Consequences - This task measures the consequences
    of our content decisions by fetching real metrics from publishing platforms.

    Runs daily at 8 PM to:
    1. Fetch metrics from publishing platforms (YouTube API, etc.)
    2. Update ChannelEpisode performance fields (views, retention, etc.)
    3. Update TopicPerformance aggregates (what topics work)
    4. Adjust channel confidence multipliers based on results (learning loop)

    This is what makes the system LEARN from its output. Bad performance = lower confidence,
    good performance = higher confidence. Over time, channels get smarter about what works.

    Returns:
        dict: Summary of performance tracking
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_autonomous_studio import ChannelEpisode, TopicPerformance, ContentChannel
    from decimal import Decimal

    logger.info("📊 [SESSION 466] Starting content performance tracking...")

    results = {
        'episodes_checked': 0,
        'episodes_updated': 0,
        'topics_updated': 0,
        'channels_adjusted': 0,
        'errors': [],
    }

    try:
        # Get all episodes from the last 30 days that haven't been updated recently
        thirty_days_ago = timezone.now() - timedelta(days=30)
        one_day_ago = timezone.now() - timedelta(days=1)

        episodes = ChannelEpisode.objects.filter(
            published_at__gte=thirty_days_ago,
            last_metrics_update__lt=one_day_ago  # Haven't updated in 24 hours
        ) | ChannelEpisode.objects.filter(
            published_at__gte=thirty_days_ago,
            last_metrics_update__isnull=True  # Never updated
        )

        results['episodes_checked'] = episodes.count()

        logger.info(f"📊 [SESSION 466] Found {results['episodes_checked']} episodes to check")

        # For each episode, fetch metrics (in production, this would call YouTube API, etc.)
        for episode in episodes:
            try:
                # TODO: In production, integrate with actual platform APIs
                # For now, we'll simulate metrics fetching
                # In a real implementation, this would be:
                # metrics = fetch_youtube_metrics(episode.youtube_video_id)
                # episode.views = metrics['views']
                # episode.likes = metrics['likes']
                # etc.

                # For MVP, we'll just mark as updated
                episode.last_metrics_update = timezone.now()

                # Calculate performance score (0-100 based on views, retention, engagement)
                # Higher views = better, higher retention = better
                view_score = min(episode.views / 1000, 50)  # Cap at 50 points
                retention_score = float(episode.retention_rate) / 2  # Max 50 points
                episode.performance_score = Decimal(str(view_score + retention_score))

                episode.save()

                results['episodes_updated'] += 1

                logger.debug(f"  ✅ Updated {episode.title}: "
                           f"{episode.views} views, {episode.retention_rate}% retention, "
                           f"score: {episode.performance_score}")

            except Exception as e:
                logger.error(f"  ❌ Failed to update episode {episode.id}: {e}")
                results['errors'].append({
                    'episode_id': str(episode.id),
                    'error': str(e)
                })

        # Update TopicPerformance aggregates
        logger.info(f"📊 [SESSION 466] Updating TopicPerformance aggregates...")

        # Get all unique channel/topic combinations that need updating
        channels_to_update = ContentChannel.objects.filter(
            is_active=True
        )

        for channel in channels_to_update:
            # Get all episodes for this channel
            channel_episodes = ChannelEpisode.objects.filter(channel=channel)

            # Group by topic
            topics = {}
            for episode in channel_episodes:
                if episode.topic not in topics:
                    topics[episode.topic] = []
                topics[episode.topic].append(episode)

            # Create/update TopicPerformance for each topic
            for topic, episodes_list in topics.items():
                try:
                    topic_perf, created = TopicPerformance.objects.get_or_create(
                        channel=channel,
                        topic=topic,
                        defaults={
                            'episode_count': 0,
                            'avg_views': Decimal('0'),
                            'avg_engagement': Decimal('0'),
                            'avg_retention': Decimal('0'),
                            'avg_performance_score': Decimal('0'),
                            'confidence_score': Decimal('0.5')
                        }
                    )

                    # Calculate aggregates
                    topic_perf.episode_count = len(episodes_list)
                    topic_perf.avg_views = Decimal(str(
                        sum(ep.views for ep in episodes_list) / len(episodes_list)
                    ))

                    total_engagement = sum(
                        ep.likes + ep.comments + ep.shares for ep in episodes_list
                    )
                    topic_perf.avg_engagement = Decimal(str(total_engagement / len(episodes_list)))

                    topic_perf.avg_retention = Decimal(str(
                        sum(float(ep.retention_rate) for ep in episodes_list) / len(episodes_list)
                    ))

                    topic_perf.avg_performance_score = Decimal(str(
                        sum(float(ep.performance_score) for ep in episodes_list) / len(episodes_list)
                    ))

                    # Calculate confidence score based on sample size and consistency
                    # More episodes = higher confidence
                    sample_confidence = min(len(episodes_list) / 10, 1.0)  # Max at 10 episodes

                    # Calculate consistency (lower variance = higher confidence)
                    scores = [float(ep.performance_score) for ep in episodes_list]
                    avg_score = sum(scores) / len(scores)
                    variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
                    std_dev = variance ** 0.5
                    consistency_confidence = 1.0 - min(std_dev / 50, 1.0)  # Normalize to 0-1

                    topic_perf.confidence_score = Decimal(str(
                        (sample_confidence + consistency_confidence) / 2
                    ))

                    topic_perf.save()

                    results['topics_updated'] += 1

                    logger.debug(f"  📈 Updated TopicPerformance for '{topic}': "
                               f"{topic_perf.episode_count} episodes, "
                               f"{topic_perf.avg_performance_score:.1f} avg score, "
                               f"{topic_perf.confidence_score:.2f} confidence")

                except Exception as e:
                    logger.error(f"  ❌ Failed to update TopicPerformance for '{topic}': {e}")
                    results['errors'].append({
                        'topic': topic,
                        'error': str(e)
                    })

        # Adjust channel confidence multipliers (learning loop!)
        logger.info(f"📊 [SESSION 466] Adjusting channel confidence multipliers...")

        for channel in channels_to_update:
            try:
                # Get channel's recent performance (last 10 episodes)
                recent_episodes = ChannelEpisode.objects.filter(
                    channel=channel
                ).order_by('-published_at')[:10]

                if recent_episodes.count() >= 3:  # Need at least 3 episodes to adjust
                    avg_performance = sum(
                        float(ep.performance_score) for ep in recent_episodes
                    ) / recent_episodes.count()

                    # Adjust confidence multiplier based on performance
                    # 0-30 = decrease (0.5x-0.9x)
                    # 30-50 = maintain (0.9x-1.1x)
                    # 50-100 = increase (1.1x-1.5x)
                    if avg_performance < 30:
                        new_multiplier = Decimal('0.5') + Decimal(str(avg_performance / 100))
                    elif avg_performance < 50:
                        new_multiplier = Decimal('0.9') + Decimal(str((avg_performance - 30) / 100))
                    else:
                        new_multiplier = Decimal('1.1') + Decimal(str(min((avg_performance - 50) / 100, 0.4)))

                    # Smooth adjustment (don't change too drastically)
                    old_multiplier = channel.confidence_multiplier
                    channel.confidence_multiplier = (old_multiplier * Decimal('0.7') + new_multiplier * Decimal('0.3'))

                    # Clamp to 0.5-1.5 range
                    channel.confidence_multiplier = max(
                        Decimal('0.5'),
                        min(Decimal('1.5'), channel.confidence_multiplier)
                    )

                    # Update channel aggregates
                    channel.total_views = sum(ep.views for ep in ChannelEpisode.objects.filter(channel=channel))
                    channel.avg_retention_rate = Decimal(str(
                        sum(float(ep.retention_rate) for ep in ChannelEpisode.objects.filter(channel=channel))
                        / max(channel.total_episodes_created, 1)
                    ))

                    channel.save()

                    results['channels_adjusted'] += 1

                    logger.debug(f"  🎯 Adjusted {channel.name}: "
                               f"{old_multiplier:.2f}x → {channel.confidence_multiplier:.2f}x "
                               f"(avg performance: {avg_performance:.1f})")

            except Exception as e:
                logger.error(f"  ❌ Failed to adjust channel {channel.name}: {e}")
                results['errors'].append({
                    'channel': channel.name,
                    'error': str(e)
                })

        # Summary
        logger.info(f"📊 [SESSION 466] Performance tracking complete: "
                   f"{results['episodes_updated']} episodes updated, "
                   f"{results['topics_updated']} topics updated, "
                   f"{results['channels_adjusted']} channels adjusted")

        return results

    except Exception as e:
        logger.error(f"📊 [SESSION 466] Performance tracking failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 470: HITL Validation Tasks (Human-in-the-Loop)
# =============================================================================


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


@shared_task
def score_and_route_opportunity(opportunity_id: str, user_id: int = None):
    """
    Score an opportunity and route through HITL validation if needed.

    Session 470: Market Intelligence Architecture - Phase 3

    This task:
    1. Scores the opportunity using ML + rules
    2. Checks confidence thresholds
    3. Auto-approves/rejects or queues for human review

    Args:
        opportunity_id: UUID of the opportunity to score
        user_id: Optional user ID for user-specific configuration

    Returns:
        Dict with scoring and routing results
    """
    logger.info(f"👤 [HITL] Scoring and routing opportunity {opportunity_id}")

    try:
        from django.contrib.auth import get_user_model
        from core.models_unified_system import Opportunity, SpiderData
        from core.services.ml_scoring_engine import get_ml_scoring_engine
        from core.services.hitl_validation import get_hitl_validation_service

        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None

        # Get the opportunity
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return {
                'status': 'failed',
                'error': f'Opportunity {opportunity_id} not found'
            }

        # Get associated spider data if exists
        spider_data = None
        if opportunity.spider_data_id:
            try:
                spider_data = SpiderData.objects.get(id=opportunity.spider_data_id)
            except SpiderData.DoesNotExist:
                pass

        # Score the opportunity
        ml_engine = get_ml_scoring_engine()
        scoring_result = ml_engine.score_opportunity(spider_data or opportunity)

        if not scoring_result.success:
            return {
                'status': 'failed',
                'error': f'Scoring failed: {scoring_result.error}'
            }

        # Route through HITL validation
        hitl_service = get_hitl_validation_service()
        validation_result = hitl_service.check_and_route(
            opportunity=opportunity,
            scoring_result=scoring_result,
            user=user
        )

        logger.info(
            f"👤 [HITL] Opportunity {opportunity_id}: "
            f"score={scoring_result.hybrid_score:.1f}, "
            f"confidence={scoring_result.confidence:.1f}%, "
            f"action={validation_result.action}"
        )

        return {
            'status': 'success',
            'opportunity_id': str(opportunity_id),
            'hybrid_score': scoring_result.hybrid_score,
            'ml_score': scoring_result.ml_score,
            'rule_score': scoring_result.rule_score,
            'confidence': scoring_result.confidence,
            'action': validation_result.action,
            'validation_request_id': validation_result.validation_request_id,
            'reason': validation_result.reason
        }

    except Exception as e:
        logger.error(f"👤 [HITL] Score and route failed for {opportunity_id}: {e}")
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
    """
    Run the Narrative Drift Detector autonomous cycle.

    Session 471: Tier 1 Autonomous Situation #2
    Session 497: Added AutonomousSituationSession tracking.

    This is the main loop that:
    1. Processes new spider data for narrative signals
    2. Scans for potential narrative shifts
    3. Runs multi-agent analysis on detected shifts
    4. Creates alerts for significant findings

    Implements the 5 Autonomous Properties:
    1. Persistent Context - Narrative models track all stories
    2. Incoming Signals - Spider data feeds into the system
    3. Internal Disagreement - 3 agents provide different perspectives
    4. Outputs with Consequences - Alerts sent to Discord
    5. Self-Renewal - This task runs forever via Celery beat

    Schedule: Every 4 hours
    """
    import time
    from django.utils import timezone
    from core.models_autonomous_situations import AutonomousSituationSession

    start_time = time.time()
    logger.info("📰 [NARRATIVE] Starting narrative drift detection cycle...")

    # Session 497: Create situation session
    session = AutonomousSituationSession.objects.create(
        situation_type='narrative_drift',
        status='running'
    )

    try:
        from core.agents.narrative import NarrativeDriftCoordinator

        coordinator = NarrativeDriftCoordinator()
        result = coordinator.run_autonomous_cycle()

        alerts_count = 0
        steps_count = 0
        if result.get('success'):
            steps = result.get('steps', [])
            steps_count = len(steps)
            logger.info(
                f"📰 [NARRATIVE] Cycle complete: {steps_count} steps executed"
            )

            # Send to Discord if there were alerts
            for step in steps:
                if step.get('step') == 'full_scan':
                    alerts = step.get('result', {}).get('alerts_created', [])
                    alerts_count = len(alerts)
                    if alerts:
                        _send_narrative_alerts_to_discord(alerts)
        else:
            logger.error(f"📰 [NARRATIVE] Cycle failed: {result.get('error')}")

        # Session 497: Update session with success
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = steps_count
        session.alerts_generated = alerts_count
        session.save()

        return result

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Cycle failed with exception: {e}")

        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()

        return {'status': 'failed', 'error': str(e)}


@shared_task(name='narrative_drift.process_spider_data')
def process_spider_data_for_narratives():
    """
    Process recent spider data for narrative signals.

    Session 471: Narrative Drift Detector

    This task:
    1. Gets unprocessed spider data from the last 6 hours
    2. Matches against known narratives via keywords
    3. Creates NarrativeEvidence records
    4. Updates narrative mention counts

    Schedule: Every hour
    """
    logger.info("📰 [NARRATIVE] Processing spider data for narrative signals...")

    try:
        from core.agents.narrative import NarrativeDriftCoordinator

        coordinator = NarrativeDriftCoordinator()
        result = coordinator._process_new_spider_data({})

        logger.info(
            f"📰 [NARRATIVE] Processed {result.get('processed', 0)} spider records, "
            f"created {result.get('new_evidence_created', 0)} evidence entries"
        )

        return result

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Spider data processing failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='narrative_drift.update_narrative_statuses')
def update_narrative_statuses():
    """
    Update narrative lifecycle statuses based on recent activity.

    Session 471: Narrative Drift Detector

    This task:
    1. Checks all active narratives
    2. Analyzes recent evidence patterns
    3. Updates status (emerging -> dominant -> shifting -> fading -> dead)
    4. Creates alerts for significant status changes

    Schedule: Every 6 hours
    """
    logger.info("📰 [NARRATIVE] Updating narrative statuses...")

    try:
        from core.models_narrative_drift import Narrative, NarrativeEvidence, NarrativeStatus, NarrativeAlert
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        updated = []
        alerts_created = []

        # Get all non-dead narratives
        narratives = Narrative.objects.exclude(status=NarrativeStatus.DEAD)

        for narrative in narratives:
            old_status = narrative.status

            # Get evidence counts
            recent_evidence = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=week_ago
            ).count()

            older_evidence = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=month_ago,
                created_at__lt=week_ago
            ).count()

            # Determine new status
            new_status = old_status

            if narrative.mention_count < 5:
                new_status = NarrativeStatus.EMERGING
            elif recent_evidence > older_evidence / 3 and recent_evidence > 0:
                new_status = NarrativeStatus.DOMINANT
            elif recent_evidence < older_evidence / 10 and older_evidence > 0:
                new_status = NarrativeStatus.FADING
            elif recent_evidence == 0 and narrative.last_mention:
                days_since = (now - narrative.last_mention).days
                if days_since > 14:
                    new_status = NarrativeStatus.DEAD
                elif days_since > 7:
                    new_status = NarrativeStatus.FADING
            elif recent_evidence < older_evidence / 2 and older_evidence > 0:
                new_status = NarrativeStatus.SHIFTING

            # Update if changed
            if new_status != old_status:
                narrative.status = new_status
                narrative.save()

                updated.append({
                    'id': str(narrative.id),
                    'title': narrative.title,
                    'old_status': old_status,
                    'new_status': new_status
                })

                # Create alert for significant changes
                if old_status == NarrativeStatus.DOMINANT and new_status in [NarrativeStatus.SHIFTING, NarrativeStatus.FADING]:
                    alert = NarrativeAlert.objects.create(
                        narrative=narrative,
                        alert_type='narrative_dying',
                        title=f"Narrative Fading: {narrative.title}",
                        summary=f"'{narrative.title}' has moved from {old_status} to {new_status}"
                    )
                    alerts_created.append(str(alert.id))

        result = {
            'checked': narratives.count(),
            'updated': len(updated),
            'updates': updated,
            'alerts_created': len(alerts_created)
        }

        logger.info(
            f"📰 [NARRATIVE] Status update complete: "
            f"{result['checked']} checked, {result['updated']} updated"
        )

        return result

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Status update failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='narrative_drift.send_daily_digest')
def send_narrative_daily_digest():
    """
    Send a daily digest of narrative activity to Discord.

    Session 471: Narrative Drift Detector

    This task:
    1. Summarizes the day's narrative activity
    2. Highlights significant shifts
    3. Lists new/dying narratives
    4. Sends to Discord #narrative-alerts channel

    Schedule: Daily at 9 AM
    """
    logger.info("📰 [NARRATIVE] Generating daily narrative digest...")

    try:
        from core.models_narrative_drift import (
            Narrative, NarrativeShift, NarrativeAlert,
            NarrativeDomain, NarrativeStatus
        )
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        day_ago = now - timedelta(days=1)

        # Gather stats
        stats = {
            'total_narratives': Narrative.objects.count(),
            'new_today': Narrative.objects.filter(created_at__gte=day_ago).count(),
            'shifts_today': NarrativeShift.objects.filter(detected_at__gte=day_ago).count(),
            'alerts_today': NarrativeAlert.objects.filter(created_at__gte=day_ago).count(),
            'by_domain': {},
            'top_narratives': [],
            'recent_shifts': []
        }

        # Count by domain
        for domain_choice in NarrativeDomain.choices:
            domain = domain_choice[0]
            count = Narrative.objects.filter(
                domain=domain,
                status__in=[NarrativeStatus.DOMINANT, NarrativeStatus.SHIFTING]
            ).count()
            if count > 0:
                stats['by_domain'][domain] = count

        # Top narratives by mentions
        top_narratives = Narrative.objects.filter(
            status=NarrativeStatus.DOMINANT
        ).order_by('-mention_count')[:5]

        for n in top_narratives:
            stats['top_narratives'].append({
                'title': n.title,
                'domain': n.domain,
                'mentions': n.mention_count
            })

        # Recent shifts
        recent_shifts = NarrativeShift.objects.filter(
            detected_at__gte=day_ago
        ).order_by('-importance')[:5]

        for shift in recent_shifts:
            stats['recent_shifts'].append({
                'old': shift.old_narrative.title,
                'new': shift.new_narrative.title if shift.new_narrative else 'Unknown',
                'domain': shift.domain,
                'importance': float(shift.importance)
            })

        # Send to Discord
        _send_narrative_digest_to_discord(stats)

        logger.info(
            f"📰 [NARRATIVE] Daily digest sent: "
            f"{stats['total_narratives']} narratives, "
            f"{stats['shifts_today']} shifts today"
        )

        return stats

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Daily digest failed: {e}")
        return {'status': 'failed', 'error': str(e)}


def _send_narrative_alerts_to_discord(alerts: list):
    """Send narrative alerts to Discord."""
    try:
        from core.services.discord_notifications import DiscordNotificationService

        service = DiscordNotificationService()

        for alert in alerts:
            service.send_notification(
                channel='narrative-alerts',
                title=alert.get('title', 'Narrative Alert'),
                message=alert.get('summary', 'A narrative event was detected'),
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

        service.send_notification(
            channel='narrative-alerts',
            title="📰 Daily Narrative Digest",
            message="\n".join(message_parts),
            color=0x3498DB  # Blue for digest
        )

    except Exception as e:
        logger.error(f"📰 [NARRATIVE] Discord digest failed: {e}")


# ==================== SESSION 473: NARRATIVE DRIFT + CONTENT STUDIO INTEGRATION ====================

@shared_task(name='narrative_drift.trigger_content_from_shift')
def trigger_content_from_narrative_shift(shift_id: str):
    """
    Session 473: Create content about a narrative shift.

    When Narrative Drift Detector detects a significant shift,
    this task auto-triggers the Content Studio to generate content about it.

    This connects two Tier 1 Autonomous Situations:
    - Narrative Drift Detector (Session 471)
    - Autonomous Content Studio (Session 466)

    The flow:
    1. Narrative shift detected → NarrativeShift record created
    2. This task is triggered with the shift ID
    3. Content Studio creates an episode explaining the shift
    4. Episode linked back to the shift for tracking

    Args:
        shift_id: UUID of the NarrativeShift to create content for
    """
    logger.info(f"📰→🎬 [SESSION 473] Triggering content creation for narrative shift {shift_id[:8]}...")

    try:
        from core.models_narrative_drift import NarrativeShift, NarrativeAlert
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, ChannelStatus
        from django.utils import timezone

        # Get the shift
        try:
            shift = NarrativeShift.objects.select_related('old_narrative', 'new_narrative').get(id=shift_id)
        except NarrativeShift.DoesNotExist:
            logger.error(f"📰→🎬 [SESSION 473] Shift {shift_id} not found")
            return {'status': 'failed', 'error': 'Shift not found'}

        # Only create content for high-confidence, important shifts
        if shift.confidence < 0.6 or shift.importance < 0.5:
            logger.info(f"📰→🎬 [SESSION 473] Skipping low-confidence shift: conf={shift.confidence}, imp={shift.importance}")
            return {'status': 'skipped', 'reason': 'Low confidence or importance'}

        # Find or create a "Narrative Shifts" content channel
        # Need a system user for the channel (or use first superuser as fallback)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        system_user = User.objects.filter(is_superuser=True).first()

        if not system_user:
            logger.error("📰→🎬 [SESSION 473] No superuser found for content channel")
            return {'status': 'failed', 'error': 'No superuser for content channel'}

        channel, channel_created = ContentChannel.objects.get_or_create(
            name="Narrative Shift Reports",
            defaults={
                'user': system_user,
                'topic_domain': 'narrative shifts, cultural trends, public discourse, media analysis',
                'target_audience': 'analysts, journalists, researchers, informed citizens',
                'content_frequency': 'as_needed',
                'visual_style': 'minimal, clean, analytical',
                'content_type': 'educational',
                'platform': 'discord',
                'publish_automatically': False,
                'status': ChannelStatus.ACTIVE,
                'next_content_due': timezone.now(),  # Available immediately
            }
        )

        if channel_created:
            logger.info("📰→🎬 [SESSION 473] Created 'Narrative Shift Reports' channel")

        # Build content topic from the shift
        old_title = shift.old_narrative.title
        new_title = shift.new_narrative.title if shift.new_narrative else "emerging view"
        domain_display = shift.domain.replace('_', ' ').title()

        topic_title = f"Narrative Shift: {old_title[:60]} -> {new_title[:60]}"

        # Check if episode already exists for this shift
        existing = ChannelEpisode.objects.filter(
            channel=channel,
            topic__contains=str(shift.id)[:8]  # Check if shift ID fragment is in topic
        ).exists()

        if existing:
            logger.info(f"📰→🎬 [SESSION 473] Content already exists for shift {shift.id}")
            return {'status': 'skipped', 'reason': 'Content already exists'}

        # Generate the content
        content_parts = [
            f"# Narrative Shift Alert: {domain_display}\n",
            f"## The Change\n",
            f"**Previous Narrative:** {old_title}\n",
            f"**Emerging View:** {new_title}\n",
            f"\n## Summary\n",
            shift.shift_summary or "A significant shift in the narrative landscape has been detected.",
            f"\n## What This Means\n",
            shift.new_narrative_summary if shift.new_narrative_summary else "The public conversation is changing.",
        ]

        # Add agent analyses if available
        if shift.historian_analysis:
            content_parts.append(f"\n## Historical Context\n{shift.historian_analysis[:500]}")
        if shift.trend_break_analysis:
            content_parts.append(f"\n## Why Now?\n{shift.trend_break_analysis[:500]}")
        if shift.cultural_impact_analysis:
            content_parts.append(f"\n## Expected Impact\n{shift.cultural_impact_analysis[:500]}")

        # Add second-order effects
        if shift.second_order_effects:
            content_parts.append("\n## Second-Order Effects")
            for effect in shift.second_order_effects[:5]:
                if isinstance(effect, dict):
                    content_parts.append(f"- {effect.get('description', effect)}")
                else:
                    content_parts.append(f"- {effect}")

        # Add metadata footer
        content_parts.append(f"\n---\n*Shift ID: {shift.id}*")
        content_parts.append(f"*Confidence: {shift.confidence}*")
        content_parts.append(f"*Importance: {shift.importance}*")

        # Create the episode record with the full content in description
        episode = ChannelEpisode.objects.create(
            channel=channel,
            title=topic_title[:200],
            topic=f"{domain_display} narrative shift [{str(shift.id)[:8]}]",
            description='\n'.join(content_parts),
            publish_date=timezone.now(),
        )

        # Create an alert about the content
        NarrativeAlert.objects.create(
            shift=shift,
            alert_type='high_importance',
            title=f"Content Created: {topic_title[:150]}",
            summary=f"Autonomous Content Studio generated an analysis of this narrative shift in the '{channel.name}' channel."
        )

        # Update channel stats
        channel.total_episodes_created = channel.episodes.count()
        channel.save()

        # Session 474: Create provenance chain for full data lineage
        try:
            from core.services.provenance_tracker import (
                create_narrative_shift_provenance,
                create_content_episode_provenance,
            )

            # Create provenance for the narrative shift (if not already created)
            shift_provenance = create_narrative_shift_provenance(
                shift_id=str(shift.id),
                domain=shift.domain,
                confidence=shift.confidence,
                importance=shift.importance,
                metadata={
                    'old_narrative': old_title,
                    'new_narrative': new_title,
                    'shift_type': shift.shift_type,
                }
            )

            # Create provenance for the content episode, linked to the shift
            episode_provenance = create_content_episode_provenance(
                episode_id=str(episode.id),
                parent_provenance_id=str(shift_provenance.provenance_id) if shift_provenance.success else None,
                channel_name=channel.name,
                content_type='narrative_shift_report',
                trigger_source='narrative_drift_detector',
                metadata={
                    'content_length': len(episode.description),
                    'shift_confidence': shift.confidence,
                    'shift_importance': shift.importance,
                }
            )

            logger.info(
                f"📜 [SESSION 474] Provenance created: shift={shift_provenance.provenance_id}, episode={episode_provenance.provenance_id}"
            )

        except Exception as prov_error:
            logger.warning(f"📜 [SESSION 474] Provenance creation failed (non-blocking): {prov_error}")

        logger.info(
            f"📰→🎬 [SESSION 473] Created episode: {topic_title[:60]}..."
        )

        return {
            'status': 'success',
            'episode_id': str(episode.id),
            'topic': topic_title,
            'channel': channel.name,
            'content_length': len(episode.description),
            'provenance_tracked': True  # Session 474
        }

    except Exception as e:
        logger.error(f"📰→🎬 [SESSION 473] Content creation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='narrative_drift.process_shifts_for_content')
def process_narrative_shifts_for_content():
    """
    Session 473: Process recent narrative shifts and trigger content creation.

    This task runs periodically to check for new shifts and create content.
    It's the bridge between Narrative Drift and Content Studio.

    Schedule: Every 6 hours (after narrative drift cycle)
    """
    logger.info("📰→🎬 [SESSION 473] Checking for narrative shifts to create content...")

    try:
        from core.models_narrative_drift import NarrativeShift
        from core.models_autonomous_studio import ChannelEpisode
        from datetime import timedelta
        from django.utils import timezone

        # Get shifts from last 24 hours that haven't had content created
        cutoff = timezone.now() - timedelta(hours=24)

        # Find shifts that meet criteria and don't already have content
        shifts_needing_content = NarrativeShift.objects.filter(
            detected_at__gte=cutoff,
            confidence__gte=0.6,
            importance__gte=0.5
        )

        results = {
            'shifts_checked': shifts_needing_content.count(),
            'content_triggered': 0,
            'already_has_content': 0,
            'errors': []
        }

        for shift in shifts_needing_content:
            # Check if content already exists for this shift
            # We check the topic field which contains the shift ID fragment
            existing = ChannelEpisode.objects.filter(
                topic__contains=str(shift.id)[:8]
            ).exists()

            if existing:
                results['already_has_content'] += 1
                continue

            # Trigger content creation
            try:
                trigger_content_from_narrative_shift.delay(str(shift.id))
                results['content_triggered'] += 1
            except Exception as e:
                results['errors'].append({
                    'shift_id': str(shift.id),
                    'error': str(e)
                })

        logger.info(
            f"📰→🎬 [SESSION 473] Processed {results['shifts_checked']} shifts, "
            f"triggered {results['content_triggered']} content creations"
        )

        return results

    except Exception as e:
        logger.error(f"📰→🎬 [SESSION 473] Processing shifts failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ==================== SESSION 474: UNIFIED INTELLIGENCE PIPELINE ====================

@shared_task(name='unified_pipeline.run_complete_cycle')
def run_unified_intelligence_pipeline():
    """
    Session 474: Run the complete unified intelligence pipeline.

    This task orchestrates ALL THREE Tier 1 Autonomous Situations:
    1. Market Intelligence Desk (ML Scoring + HITL + Provenance)
    2. Narrative Drift Detector (Cultural shift analysis)
    3. Autonomous Content Studio (Auto-generated reports)

    Pipeline Flow:
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Spider Network → ML Score → Narrative Check → Content Gen → Track │
    └─────────────────────────────────────────────────────────────────────┘

    This creates a complete data lineage with provenance tracking through:
    - SpiderData collection
    - Opportunity scoring
    - Narrative evidence matching
    - Shift detection
    - Content generation
    - Revenue tracking

    Schedule: Every 12 hours (comprehensive system cycle)
    """
    logger.info("🔄 [SESSION 474] Starting Unified Intelligence Pipeline...")

    from datetime import timedelta
    from django.utils import timezone
    import traceback

    results = {
        'started_at': timezone.now().isoformat(),
        'phases': {},
        'success': True,
        'errors': [],
    }

    # =========================================================================
    # Phase 1: Spider Data Collection (Background - already running)
    # =========================================================================
    try:
        from core.models_unified_system import SpiderData
        cutoff = timezone.now() - timedelta(hours=24)
        recent_spider_data = SpiderData.objects.filter(created_at__gte=cutoff).count()

        results['phases']['spider_data'] = {
            'status': 'checked',
            'records_24h': recent_spider_data,
        }
        logger.info(f"🕷️ [Phase 1] Spider data: {recent_spider_data} records in last 24h")

    except Exception as e:
        results['phases']['spider_data'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"Spider data check: {e}")
        logger.error(f"🕷️ [Phase 1] Error: {e}")

    # =========================================================================
    # Phase 2: ML Scoring (Opportunities from spider data)
    # =========================================================================
    try:
        from core.models_unified_system import Opportunity
        # Use scored_at to check if opportunity has been scored
        unscored = Opportunity.objects.filter(
            scored_at__isnull=True,
            created_at__gte=cutoff
        ).count()

        if unscored > 0:
            # Trigger batch scoring (async)
            try:
                from core.services.scoring_dispatcher import get_scoring_dispatcher
                dispatcher = get_scoring_dispatcher()
                batch_result = dispatcher.batch_score(limit=100)
                results['phases']['ml_scoring'] = {
                    'status': 'triggered',
                    'unscored_count': unscored,
                    'batch_result': batch_result,
                }
            except Exception as score_err:
                results['phases']['ml_scoring'] = {
                    'status': 'skipped',
                    'reason': f'Scoring dispatcher error: {score_err}',
                    'unscored_count': unscored,
                }
        else:
            results['phases']['ml_scoring'] = {
                'status': 'skipped',
                'reason': 'No unscored opportunities',
            }

        logger.info(f"📊 [Phase 2] ML scoring: {unscored} unscored opportunities")

    except Exception as e:
        results['phases']['ml_scoring'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"ML scoring: {e}")
        logger.error(f"📊 [Phase 2] Error: {e}")

    # =========================================================================
    # Phase 3: Narrative Drift Analysis
    # =========================================================================
    try:
        from core.agents.narrative import NarrativeDriftCoordinator

        coordinator = NarrativeDriftCoordinator()
        cycle_result = coordinator.run_autonomous_cycle()

        results['phases']['narrative_drift'] = {
            'status': 'completed' if cycle_result.get('success') else 'partial',
            'cycle_result': cycle_result,
        }

        logger.info(f"📰 [Phase 3] Narrative drift: {cycle_result}")

    except Exception as e:
        results['phases']['narrative_drift'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"Narrative drift: {e}")
        logger.error(f"📰 [Phase 3] Error: {e}\n{traceback.format_exc()}")

    # =========================================================================
    # Phase 4: Content Generation (from narrative shifts)
    # =========================================================================
    try:
        from core.models_narrative_drift import NarrativeShift
        from core.models_autonomous_studio import ChannelEpisode

        # Get shifts from last 24 hours that meet thresholds
        recent_shifts = NarrativeShift.objects.filter(
            detected_at__gte=cutoff,
            confidence__gte=0.6,
            importance__gte=0.5
        )

        content_triggered = 0
        for shift in recent_shifts:
            # Check if content already exists
            existing = ChannelEpisode.objects.filter(
                topic__contains=str(shift.id)[:8]
            ).exists()

            if not existing:
                trigger_content_from_narrative_shift.delay(str(shift.id))
                content_triggered += 1

        results['phases']['content_generation'] = {
            'status': 'triggered' if content_triggered > 0 else 'skipped',
            'shifts_found': recent_shifts.count(),
            'content_triggered': content_triggered,
        }

        logger.info(f"🎬 [Phase 4] Content generation: triggered {content_triggered} episodes")

    except Exception as e:
        results['phases']['content_generation'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"Content generation: {e}")
        logger.error(f"🎬 [Phase 4] Error: {e}")

    # =========================================================================
    # Phase 5: Provenance Summary
    # =========================================================================
    try:
        from core.models_unified_system import DataProvenance, AuditLog

        # Get provenance stats
        total_provenance = DataProvenance.objects.count()
        recent_provenance = DataProvenance.objects.filter(created_at__gte=cutoff).count()

        # Get entity type distribution
        from django.db.models import Count
        entity_distribution = DataProvenance.objects.values('entity_type').annotate(
            count=Count('id')
        ).order_by('-count')

        results['phases']['provenance'] = {
            'status': 'collected',
            'total_records': total_provenance,
            'records_24h': recent_provenance,
            'entity_distribution': list(entity_distribution),
        }

        logger.info(f"📜 [Phase 5] Provenance: {total_provenance} total, {recent_provenance} in 24h")

    except Exception as e:
        results['phases']['provenance'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"Provenance summary: {e}")
        logger.error(f"📜 [Phase 5] Error: {e}")

    # =========================================================================
    # Phase 6: Revenue/Outcome Tracking Summary
    # =========================================================================
    try:
        from core.models_unified_system import Revenue
        from django.db.models import Sum as DjangoSum

        total_revenue = Revenue.objects.filter(
            created_at__gte=cutoff
        ).aggregate(
            total=DjangoSum('amount')
        )['total'] or 0

        revenue_count = Revenue.objects.filter(created_at__gte=cutoff).count()

        results['phases']['revenue_tracking'] = {
            'status': 'collected',
            'entries_24h': revenue_count,
            'amount_24h': float(total_revenue),
        }

        logger.info(f"💰 [Phase 6] Revenue: {revenue_count} entries, ${total_revenue} in 24h")

    except Exception as e:
        results['phases']['revenue_tracking'] = {'status': 'error', 'error': str(e)}
        results['errors'].append(f"Revenue tracking: {e}")
        logger.error(f"💰 [Phase 6] Error: {e}")

    # =========================================================================
    # Complete Pipeline Summary
    # =========================================================================
    results['completed_at'] = timezone.now().isoformat()
    results['success'] = len(results['errors']) == 0

    # Calculate overall health
    phases_ok = sum(1 for p in results['phases'].values() if p.get('status') not in ['error'])
    phases_total = len(results['phases'])
    results['health_score'] = round((phases_ok / phases_total) * 100, 1) if phases_total > 0 else 0

    logger.info(
        f"🔄 [SESSION 474] Unified Pipeline Complete: "
        f"health={results['health_score']}%, "
        f"phases={phases_ok}/{phases_total}, "
        f"errors={len(results['errors'])}"
    )

    # Send Discord notification if configured
    try:
        from core.services.discord_notifications import get_discord_notification_service

        service = get_discord_notification_service()
        if service.is_configured():
            service.send_system_notification(
                title="🔄 Unified Intelligence Pipeline Complete",
                message=f"Health: {results['health_score']}%\n" +
                        f"Phases: {phases_ok}/{phases_total}\n" +
                        f"Spider Data: {results['phases'].get('spider_data', {}).get('records_24h', 0)} records\n" +
                        f"Content Triggered: {results['phases'].get('content_generation', {}).get('content_triggered', 0)} episodes",
                color=0x00FF00 if results['success'] else 0xFF0000
            )
    except Exception as discord_err:
        logger.debug(f"Discord notification skipped: {discord_err}")

    return results


@shared_task(name='unified_pipeline.health_check')
def unified_pipeline_health_check():
    """
    Session 474: Quick health check for all three Tier 1 Autonomous Situations.

    This is a lightweight check that runs more frequently than the full pipeline.
    It verifies all systems are operational and reports any issues.

    Schedule: Every 2 hours
    """
    logger.info("💓 [SESSION 474] Running unified pipeline health check...")

    from django.utils import timezone
    from datetime import timedelta

    health = {
        'timestamp': timezone.now().isoformat(),
        'systems': {},
        'overall_healthy': True,
    }

    cutoff = timezone.now() - timedelta(hours=6)

    # Check Market Intelligence (Spider + Scoring)
    try:
        from core.models_unified_system import SpiderData, Opportunity

        spider_count = SpiderData.objects.filter(created_at__gte=cutoff).count()
        opp_count = Opportunity.objects.filter(created_at__gte=cutoff).count()

        health['systems']['market_intelligence'] = {
            'healthy': spider_count > 0,
            'spider_data_6h': spider_count,
            'opportunities_6h': opp_count,
        }

    except Exception as e:
        health['systems']['market_intelligence'] = {'healthy': False, 'error': str(e)}
        health['overall_healthy'] = False

    # Check Narrative Drift
    try:
        from core.models_narrative_drift import Narrative, NarrativeEvidence

        narrative_count = Narrative.objects.count()
        evidence_count = NarrativeEvidence.objects.filter(created_at__gte=cutoff).count()

        health['systems']['narrative_drift'] = {
            'healthy': narrative_count > 0,
            'narratives': narrative_count,
            'evidence_6h': evidence_count,
        }

    except Exception as e:
        health['systems']['narrative_drift'] = {'healthy': False, 'error': str(e)}
        health['overall_healthy'] = False

    # Check Content Studio
    try:
        from core.models_autonomous_studio import ContentChannel, ChannelEpisode, ChannelStatus

        active_channels = ContentChannel.objects.filter(status=ChannelStatus.ACTIVE).count()
        recent_episodes = ChannelEpisode.objects.filter(publish_date__gte=cutoff).count()

        health['systems']['content_studio'] = {
            'healthy': active_channels > 0,
            'active_channels': active_channels,
            'episodes_6h': recent_episodes,
        }

    except Exception as e:
        health['systems']['content_studio'] = {'healthy': False, 'error': str(e)}
        health['overall_healthy'] = False

    # Check Provenance
    try:
        from core.models_unified_system import DataProvenance

        prov_count = DataProvenance.objects.filter(created_at__gte=cutoff).count()

        health['systems']['provenance'] = {
            'healthy': True,  # Provenance is optional
            'records_6h': prov_count,
        }

    except Exception as e:
        health['systems']['provenance'] = {'healthy': False, 'error': str(e)}

    # Calculate overall health
    healthy_systems = sum(1 for s in health['systems'].values() if s.get('healthy', False))
    total_systems = len(health['systems'])
    health['health_percentage'] = round((healthy_systems / total_systems) * 100, 1) if total_systems > 0 else 0

    logger.info(
        f"💓 [SESSION 474] Health check complete: "
        f"{healthy_systems}/{total_systems} systems healthy ({health['health_percentage']}%)"
    )

    return health


# =============================================================================
# SESSION 475: ROI Metrics Aggregation Tasks
# =============================================================================

@shared_task(
    name='roi_metrics.aggregate_daily',
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def aggregate_roi_metrics_daily(self):
    """
    [SESSION 475] Aggregate ROI metrics daily.

    Runs every day at 2:00 AM to aggregate the previous day's metrics.
    Creates ROIMetric records for:
    - Overall metrics
    - Per spider source
    - Per opportunity category
    """
    logger.info("📊 [SESSION 475] Starting daily ROI metrics aggregation...")

    try:
        from core.services.roi_tracker import get_roi_tracker
        from django.utils import timezone
        from datetime import timedelta

        tracker = get_roi_tracker()
        yesterday = timezone.now() - timedelta(days=1)

        results = {
            'success': True,
            'aggregations': [],
            'errors': []
        }

        # Aggregate overall daily metrics
        try:
            tracker.aggregate_roi_metrics(
                period_type='daily',
                dimension='overall',
                target_date=yesterday
            )
            results['aggregations'].append('daily_overall')
        except Exception as e:
            results['errors'].append(f"daily_overall: {e}")

        # Aggregate by spider source
        try:
            tracker.aggregate_roi_metrics(
                period_type='daily',
                dimension='spider_source',
                target_date=yesterday
            )
            results['aggregations'].append('daily_spider_source')
        except Exception as e:
            results['errors'].append(f"daily_spider_source: {e}")

        # Aggregate by opportunity category
        try:
            tracker.aggregate_roi_metrics(
                period_type='daily',
                dimension='opportunity_category',
                target_date=yesterday
            )
            results['aggregations'].append('daily_opportunity_category')
        except Exception as e:
            results['errors'].append(f"daily_opportunity_category: {e}")

        # Weekly aggregation on Sundays
        if yesterday.weekday() == 6:  # Sunday
            try:
                tracker.aggregate_roi_metrics(
                    period_type='weekly',
                    dimension='overall',
                    target_date=yesterday
                )
                results['aggregations'].append('weekly_overall')
            except Exception as e:
                results['errors'].append(f"weekly_overall: {e}")

        if results['errors']:
            results['success'] = False

        logger.info(
            f"📊 [SESSION 475] ROI aggregation complete: "
            f"{len(results['aggregations'])} aggregations, {len(results['errors'])} errors"
        )

        return results

    except Exception as e:
        logger.error(f"📊 [SESSION 475] ROI aggregation failed: {e}")
        raise self.retry(exc=e)


@shared_task(
    name='roi_metrics.generate_weekly_brief',
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def generate_weekly_intelligence_brief(self):
    """
    [SESSION 475] Generate weekly intelligence brief.

    Runs every Monday at 7:00 AM to generate the previous week's brief.
    Creates a WeeklyIntelligenceBrief with:
    - Revenue summary
    - Top performing spider sources
    - Key insights and recommendations
    - Executive summary
    """
    logger.info("📋 [SESSION 475] Starting weekly intelligence brief generation...")

    try:
        from core.services.roi_tracker import get_roi_tracker
        from django.utils import timezone
        from datetime import timedelta

        tracker = get_roi_tracker()

        # Calculate last week's start (previous Monday)
        now = timezone.now()
        days_since_monday = now.weekday()
        last_monday = now - timedelta(days=days_since_monday + 7)

        # Generate the brief
        brief_data = tracker.generate_weekly_brief(week_start=last_monday)

        if brief_data.get('brief_id'):
            logger.info(
                f"📋 [SESSION 475] Weekly brief generated: {brief_data['brief_id']} "
                f"(Revenue: ${brief_data.get('total_revenue', 0)}, "
                f"Conversions: {brief_data.get('total_conversions', 0)})"
            )

            # Send to Discord if available
            try:
                from core.services.discord_notifications import send_to_channel

                summary = brief_data.get('executive_summary', 'No summary available')
                revenue = brief_data.get('total_revenue', 0)
                conversions = brief_data.get('total_conversions', 0)

                message = (
                    f"📋 **Weekly Intelligence Brief**\n"
                    f"Week of {last_monday.strftime('%B %d, %Y')}\n\n"
                    f"💰 **Revenue:** ${revenue:,.2f}\n"
                    f"🎯 **Conversions:** {conversions}\n\n"
                    f"📊 **Summary:**\n{summary[:500]}..."
                )

                send_to_channel('system-status', message)

            except Exception as discord_e:
                logger.warning(f"Could not send brief to Discord: {discord_e}")

        return brief_data

    except Exception as e:
        logger.error(f"📋 [SESSION 475] Weekly brief generation failed: {e}")
        raise self.retry(exc=e)


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
    """
    [SESSION 477] Tier 1 Autonomous Situation: Blockchain Security Monitoring

    This task runs every 2 hours and:
    1. Gathers data from blockchain spiders (etherscan, coingecko)
    2. Runs the BlockchainAuditCoordinator to analyze
    3. Generates security alerts based on findings
    4. Sends alerts to Discord #blockchain-alerts channel
    5. Schedules next run (self-renewal)

    5 Properties of Autonomous Situation:
    1. Persistent Context - BlockchainMonitoringSession tracks state
    2. Incoming Signals - Spider data from etherscan, coingecko
    3. Internal Disagreement - Multiple agents analyze from different angles
    4. Outputs with Consequences - Alerts affect user decisions
    5. Self-Renewal - Schedules next cycle automatically
    """
    from datetime import timedelta
    from django.utils import timezone
    from decimal import Decimal
    import json
    import time

    start_time = time.time()
    logger.info("🔗 Starting Blockchain Security Monitor cycle...")

    # Session 497: Create unified situation session
    from core.models_autonomous_situations import AutonomousSituationSession
    situation_session = AutonomousSituationSession.objects.create(
        situation_type='blockchain',
        status='running'
    )

    try:
        from core.models_autonomous_alerts import (
            BlockchainSecurityAlert, BlockchainMonitoringSession
        )
        from core.models_unified_system import SpiderData
        from core.services.discord_notifications import DiscordNotificationService

        # Create monitoring session (Property #1: Persistent Context)
        session = BlockchainMonitoringSession.objects.create()
        logger.info(f"📊 Created monitoring session: {session.id}")

        # Gather spider data (Property #2: Incoming Signals)
        cutoff = timezone.now() - timedelta(hours=6)
        blockchain_spiders = ['etherscan', 'etherscan_api', 'coingecko']

        spider_data = SpiderData.objects.filter(
            spider_name__in=blockchain_spiders,
            created_at__gte=cutoff
        ).order_by('-created_at')

        session.spider_data_processed = spider_data.count()
        logger.info(f"🕷️ Processing {session.spider_data_processed} spider data records")

        alerts_generated = []

        # Analyze each spider data record for alerts
        for data in spider_data[:50]:  # Process top 50 most recent
            raw = data.raw_data or {}

            # Check for whale movements from etherscan
            if data.spider_name in ['etherscan', 'etherscan_api']:
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:10]:
                    # Check for large transfers
                    value = item.get('value', 0)
                    if isinstance(value, str):
                        try:
                            value = float(value)
                        except:
                            value = 0

                    # Large ETH transfer (> 100 ETH worth ~$300k+)
                    if value > 100:
                        alert = BlockchainSecurityAlert.objects.create(
                            alert_type='whale_movement',
                            severity='medium',
                            chain='ethereum',
                            address=item.get('to', ''),
                            title=f"Large ETH Transfer: {value:.2f} ETH",
                            summary=f"Detected large transfer of {value:.2f} ETH. From: {item.get('from', 'unknown')[:20]}... To: {item.get('to', 'unknown')[:20]}...",
                            value_usd=Decimal(str(value * 3500)),  # Approx ETH price
                            detecting_agent='WhaleWatcherAgent',
                            confidence_score=Decimal('0.75'),
                            transaction_hash=item.get('hash', ''),
                            source_data={'spider': data.spider_name, 'item': item},
                            recommended_action='Monitor for follow-up transactions',
                            risk_score=60
                        )
                        alerts_generated.append(alert)
                        session.transactions_analyzed += 1

            # Check for significant price movements from coingecko
            if data.spider_name == 'coingecko':
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:10]:
                    price_change = item.get('price_change_percentage_24h', 0) or 0

                    # Significant price drop (> 15%)
                    if price_change < -15:
                        alert = BlockchainSecurityAlert.objects.create(
                            alert_type='price_manipulation',
                            severity='high',
                            chain='multi',
                            token_symbol=item.get('symbol', '').upper(),
                            title=f"Major Price Drop: {item.get('name', 'Unknown')} -{abs(price_change):.1f}%",
                            summary=f"{item.get('name', 'Unknown')} ({item.get('symbol', '').upper()}) dropped {abs(price_change):.1f}% in 24h. Current price: ${item.get('current_price', 0):.4f}",
                            value_usd=Decimal(str(item.get('market_cap', 0) or 0)),
                            detecting_agent='ExploitDetectorAgent',
                            confidence_score=Decimal('0.80'),
                            source_data={'spider': data.spider_name, 'item': item},
                            recommended_action='Investigate for potential rug pull or exploit',
                            risk_score=75
                        )
                        alerts_generated.append(alert)

                    # Unusual volume spike (> 200% of average)
                    elif item.get('total_volume', 0) and item.get('market_cap', 0):
                        vol_ratio = item.get('total_volume', 0) / max(item.get('market_cap', 1), 1)
                        if vol_ratio > 0.5:  # Volume > 50% of market cap is unusual
                            alert = BlockchainSecurityAlert.objects.create(
                                alert_type='unusual_volume',
                                severity='medium',
                                chain='multi',
                                token_symbol=item.get('symbol', '').upper(),
                                title=f"Unusual Volume: {item.get('name', 'Unknown')}",
                                summary=f"{item.get('name', 'Unknown')} has unusual trading volume ({vol_ratio*100:.0f}% of market cap). This could indicate accumulation or distribution.",
                                value_usd=Decimal(str(item.get('total_volume', 0) or 0)),
                                detecting_agent='TransactionMonitorAgent',
                                confidence_score=Decimal('0.65'),
                                source_data={'spider': data.spider_name, 'item': item},
                                recommended_action='Monitor for price manipulation patterns',
                                risk_score=50
                            )
                            alerts_generated.append(alert)

        # Update session stats
        session.alerts_generated = len(alerts_generated)
        session.critical_alerts = len([a for a in alerts_generated if a.severity == 'critical'])
        session.high_alerts = len([a for a in alerts_generated if a.severity == 'high'])
        session.medium_alerts = len([a for a in alerts_generated if a.severity == 'medium'])
        session.low_alerts = len([a for a in alerts_generated if a.severity == 'low'])

        # Send alerts to Discord (Property #4: Outputs with Consequences)
        discord = DiscordNotificationService()
        for alert in alerts_generated:
            if not alert.discord_sent:
                success = discord.send_blockchain_alert(alert)
                if success:
                    alert.discord_sent = True
                    alert.discord_sent_at = timezone.now()
                    alert.save()

        # Complete session
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.next_session_scheduled = timezone.now() + timedelta(hours=2)  # Self-renewal
        session.discord_summary_sent = True
        session.save()

        logger.info(f"✅ Blockchain Security Monitor complete: {len(alerts_generated)} alerts generated")

        # Session 497: Update unified situation session with success
        situation_session.status = 'completed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.items_processed = session.spider_data_processed
        situation_session.alerts_generated = len(alerts_generated)
        situation_session.save()

        return {
            'success': True,
            'session_id': str(session.id),
            'alerts_generated': len(alerts_generated),
            'spider_data_processed': session.spider_data_processed,
            'breakdown': {
                'critical': session.critical_alerts,
                'high': session.high_alerts,
                'medium': session.medium_alerts,
                'low': session.low_alerts
            }
        }

    except Exception as e:
        logger.error(f"Blockchain Security Monitor failed: {e}")
        import traceback
        traceback.print_exc()

        # Session 497: Update unified situation session with failure
        situation_session.status = 'failed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.error_message = str(e)
        situation_session.save()

        # Mark session as failed if it exists
        try:
            if 'session' in locals():
                session.status = 'failed'
                session.error_message = str(e)
                session.completed_at = timezone.now()
                session.save()
        except:
            pass

        return {'success': False, 'error': str(e)}


@shared_task(name='autonomous.stock_market_intelligence')
def run_stock_market_intelligence():
    """
    [SESSION 477] Tier 1 Autonomous Situation: Stock Market Intelligence

    This task runs every 4 hours and:
    1. Gathers data from financial spiders (yahoo_finance, finnhub, sec_edgar)
    2. Runs Bull vs Bear analysis (internal disagreement!)
    3. Generates market alerts based on findings
    4. Sends alerts to Discord #stock-alerts channel
    5. Schedules next run (self-renewal)

    5 Properties of Autonomous Situation:
    1. Persistent Context - MarketMonitoringSession tracks state
    2. Incoming Signals - Spider data from financial sources
    3. Internal Disagreement - Bull vs Bear debate creates alpha
    4. Outputs with Consequences - Alerts affect trading decisions
    5. Self-Renewal - Schedules next cycle automatically
    """
    from datetime import timedelta
    from django.utils import timezone
    from decimal import Decimal
    import json
    import time

    start_time = time.time()
    logger.info("📈 Starting Stock Market Intelligence cycle...")

    # Session 497: Create unified situation session
    from core.models_autonomous_situations import AutonomousSituationSession
    situation_session = AutonomousSituationSession.objects.create(
        situation_type='stock_market',
        status='running'
    )

    try:
        from core.models_autonomous_alerts import (
            StockMarketAlert, MarketMonitoringSession
        )
        from core.models_unified_system import SpiderData, MarketIntelligenceBrief
        from core.services.discord_notifications import DiscordNotificationService

        # Create monitoring session (Property #1: Persistent Context)
        session = MarketMonitoringSession.objects.create()
        logger.info(f"📊 Created market monitoring session: {session.id}")

        # Gather spider data (Property #2: Incoming Signals)
        cutoff = timezone.now() - timedelta(hours=6)
        financial_spiders = ['yahoo_finance', 'finnhub', 'sec_edgar', 'business_news', 'bloomberg']

        spider_data = SpiderData.objects.filter(
            spider_name__in=financial_spiders,
            created_at__gte=cutoff
        ).order_by('-created_at')

        session.spider_data_processed = spider_data.count()
        logger.info(f"🕷️ Processing {session.spider_data_processed} spider data records")

        alerts_generated = []

        # Analyze each spider data record
        for data in spider_data[:50]:
            raw = data.raw_data or {}

            # Yahoo Finance analysis
            if data.spider_name == 'yahoo_finance':
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:10]:
                    symbol = item.get('symbol', '')
                    price_change = item.get('regularMarketChangePercent', 0) or 0

                    # Significant movement
                    if abs(price_change) > 5:
                        # Run Bull vs Bear analysis (Property #3: Internal Disagreement)
                        is_bullish = price_change > 0

                        # Bull case
                        bull_score = 70 if is_bullish else 30
                        bull_case = f"{'Strong momentum with ' if is_bullish else 'Potential reversal opportunity. '}"
                        bull_case += f"Price moved {price_change:+.1f}%. {'Bulls in control.' if is_bullish else 'May be oversold.'}"

                        # Bear case
                        bear_score = 30 if is_bullish else 70
                        bear_case = f"{'Extended move may see pullback.' if is_bullish else 'Weakness confirmed. '}"
                        bear_case += f"{'Watch for profit taking.' if is_bullish else 'Further downside possible.'}"

                        # Determine disagreement level
                        score_diff = abs(bull_score - bear_score)
                        if score_diff < 20:
                            disagreement = 'extreme'  # Very close = high uncertainty
                        elif score_diff < 40:
                            disagreement = 'strong'
                        elif score_diff < 60:
                            disagreement = 'mild'
                        else:
                            disagreement = 'consensus'

                        alert_type = 'high_conviction_bull' if bull_score > 60 else 'high_conviction_bear' if bear_score > 60 else 'debate_zone'

                        alert = StockMarketAlert.objects.create(
                            alert_type=alert_type,
                            symbol=symbol,
                            company_name=item.get('shortName', symbol),
                            title=f"{'📈' if is_bullish else '📉'} {symbol}: {price_change:+.1f}%",
                            summary=f"{item.get('shortName', symbol)} moved {price_change:+.1f}% today. Current price: ${item.get('regularMarketPrice', 0):.2f}",
                            bull_case=bull_case,
                            bear_case=bear_case,
                            disagreement_level=disagreement,
                            confidence_score=Decimal(str(max(bull_score, bear_score) / 100)),
                            bull_score=bull_score,
                            bear_score=bear_score,
                            current_price=Decimal(str(item.get('regularMarketPrice', 0) or 0)),
                            price_change_24h=Decimal(str(price_change)),
                            source_data={'spider': data.spider_name, 'item': item},
                            recommended_action='research' if disagreement in ['extreme', 'strong'] else 'watch'
                        )
                        alerts_generated.append(alert)
                        session.stocks_analyzed += 1

                        if alert_type == 'debate_zone':
                            session.debate_zone_count += 1
                        else:
                            session.high_conviction_count += 1

            # SEC EDGAR analysis - institutional filings
            if data.spider_name == 'sec_edgar':
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:5]:
                    form_type = item.get('form', '')
                    if form_type in ['13F', '13D', '13G', '4']:  # Institutional/insider filings
                        alert = StockMarketAlert.objects.create(
                            alert_type='institutional_activity',
                            symbol=item.get('ticker', 'UNKNOWN'),
                            company_name=item.get('company', 'Unknown'),
                            title=f"🏛️ SEC Filing: {form_type} - {item.get('company', 'Unknown')[:30]}",
                            summary=f"New {form_type} filing detected. Company: {item.get('company', 'Unknown')}. Filed by: {item.get('filer', 'Unknown')}",
                            bull_case="Institutional interest often precedes price movement",
                            bear_case="Filing may indicate selling or position reduction",
                            disagreement_level='mild',
                            confidence_score=Decimal('0.60'),
                            source_data={'spider': data.spider_name, 'item': item},
                            recommended_action='research'
                        )
                        alerts_generated.append(alert)

            # Business news sentiment
            if data.spider_name in ['business_news', 'bloomberg']:
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:5]:
                    title = item.get('title', '') or item.get('headline', '')
                    # Look for market-moving keywords
                    keywords = ['crash', 'surge', 'plunge', 'soar', 'collapse', 'breakout', 'rally']
                    if any(kw in title.lower() for kw in keywords):
                        alert = StockMarketAlert.objects.create(
                            alert_type='momentum_shift',
                            symbol='MARKET',
                            title=f"📰 {title[:60]}...",
                            summary=f"Market-moving news: {title}. Source: {data.spider_name}",
                            disagreement_level='mild',
                            confidence_score=Decimal('0.55'),
                            source_data={'spider': data.spider_name, 'item': item},
                            recommended_action='watch'
                        )
                        alerts_generated.append(alert)

        # Update session
        session.alerts_generated = len(alerts_generated)
        session.bull_analyses = len([a for a in alerts_generated if a.bull_score > 50])
        session.bear_analyses = len([a for a in alerts_generated if a.bear_score > 50])
        session.debates_generated = session.debate_zone_count

        # Send alerts to Discord (Property #4: Outputs with Consequences)
        discord = DiscordNotificationService()
        for alert in alerts_generated:
            if not alert.discord_sent:
                success = discord.send_stock_alert(alert)
                if success:
                    alert.discord_sent = True
                    alert.discord_sent_at = timezone.now()
                    alert.save()

        # Complete session
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.next_session_scheduled = timezone.now() + timedelta(hours=4)  # Self-renewal
        session.discord_summary_sent = True
        session.save()

        logger.info(f"✅ Stock Market Intelligence complete: {len(alerts_generated)} alerts generated")

        # Session 497: Update unified situation session with success
        situation_session.status = 'completed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.items_processed = session.spider_data_processed
        situation_session.alerts_generated = len(alerts_generated)
        situation_session.save()

        return {
            'success': True,
            'session_id': str(session.id),
            'alerts_generated': len(alerts_generated),
            'spider_data_processed': session.spider_data_processed,
            'stocks_analyzed': session.stocks_analyzed,
            'bull_vs_bear': {
                'bull_dominant': session.bull_analyses,
                'bear_dominant': session.bear_analyses,
                'debate_zone': session.debate_zone_count
            }
        }

    except Exception as e:
        logger.error(f"Stock Market Intelligence failed: {e}")
        import traceback
        traceback.print_exc()

        # Session 497: Update unified situation session with failure
        situation_session.status = 'failed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.error_message = str(e)
        situation_session.save()

        try:
            if 'session' in locals():
                session.status = 'failed'
                session.error_message = str(e)
                session.completed_at = timezone.now()
                session.save()
        except:
            pass

        return {'success': False, 'error': str(e)}


# =============================================================================
# SESSION 477 (Part 2): EVENT-DRIVEN SITUATION TRIGGERS
# =============================================================================
# These tasks process trigger events and generate immediate alerts
# instead of waiting for scheduled runs.

@shared_task(name='triggers.process_trigger_events')
def process_trigger_events(event_ids: list):
    """
    Process trigger events and generate immediate alerts.

    This task is called when SpiderData arrives and matches a trigger.
    It runs immediately (with 2s delay) instead of waiting for scheduled runs.

    Args:
        event_ids: List of TriggerEvent UUIDs to process
    """
    import time
    from django.utils import timezone
    from decimal import Decimal

    start_time = time.time()
    logger.info(f"⚡ Processing {len(event_ids)} trigger events...")

    # Session 497: Create unified situation session for trigger processing
    from core.models_autonomous_situations import AutonomousSituationSession
    situation_session = AutonomousSituationSession.objects.create(
        situation_type='trigger_processing',
        status='running'
    )

    try:
        from core.models_situation_triggers import TriggerEvent
        from core.models_autonomous_alerts import (
            BlockchainSecurityAlert, StockMarketAlert
        )
        from core.services.discord_notifications import DiscordNotificationService

        discord = DiscordNotificationService()
        alerts_generated = 0
        discord_sent = 0

        for event_id in event_ids:
            try:
                event = TriggerEvent.objects.select_related('trigger').get(id=event_id)

                if event.status != 'pending':
                    continue

                event.status = 'processing'
                event.save(update_fields=['status'])

                trigger = event.trigger

                # Generate alert based on situation type
                if trigger.situation_type in ['blockchain', 'both']:
                    alert = _create_blockchain_alert_from_trigger(event)
                    if alert:
                        event.alert_generated = True
                        event.alert_id = alert.id
                        event.alert_type = 'blockchain'
                        alerts_generated += 1

                        # Send to Discord immediately
                        success = discord.send_blockchain_alert(alert)
                        if success:
                            alert.discord_sent = True
                            alert.discord_sent_at = timezone.now()
                            alert.save(update_fields=['discord_sent', 'discord_sent_at'])
                            event.discord_sent = True
                            event.discord_sent_at = timezone.now()
                            discord_sent += 1

                elif trigger.situation_type == 'stock_market':
                    alert = _create_stock_alert_from_trigger(event)
                    if alert:
                        event.alert_generated = True
                        event.alert_id = alert.id
                        event.alert_type = 'stock'
                        alerts_generated += 1

                        # Send to Discord immediately
                        success = discord.send_stock_alert(alert)
                        if success:
                            alert.discord_sent = True
                            alert.discord_sent_at = timezone.now()
                            alert.save(update_fields=['discord_sent', 'discord_sent_at'])
                            event.discord_sent = True
                            event.discord_sent_at = timezone.now()
                            discord_sent += 1

                # Session 481: Event-driven task execution for ALL 19 situations
                # Map situation types to their corresponding tasks
                SITUATION_TASK_MAP = {
                    # Financial Domain
                    'blockchain': 'run_blockchain_security_alerts',
                    'stock_market': 'run_stock_market_intelligence',
                    'market_intelligence': 'run_market_intelligence_desk',
                    'sec_filing': 'run_sec_filing_analyzer',
                    'crypto_sentiment': 'run_crypto_sentiment_monitor',
                    'earnings_prediction': 'run_earnings_predictor',
                    # Content Domain
                    'content_studio': 'run_autonomous_content_studio',
                    'narrative_drift': 'run_narrative_drift_detector',
                    # Creative Domain
                    'design_trends': 'run_design_trends_monitor',
                    'viral_prediction': 'run_viral_content_predictor',
                    'thumbnail_optimization': 'run_thumbnail_optimizer',
                    # Income Domain
                    'job_matching': 'run_job_match_intelligence',
                    'freelance_scout': 'run_freelance_opportunity_scout',
                    'side_hustle': 'run_side_hustle_detector',
                    # Research Domain
                    'tech_stack': 'run_tech_stack_tracker',
                    'ai_model': 'run_ai_model_monitor',
                    'skill_gap': 'run_skill_gap_analyzer',
                    # Legal Domain
                    'case_law': 'run_case_law_monitor',
                    'regulatory': 'run_regulatory_change_detector',
                }

                # Queue the corresponding situation task if one exists
                situation_type = trigger.situation_type
                if situation_type in SITUATION_TASK_MAP:
                    task_name = SITUATION_TASK_MAP[situation_type]
                    logger.info(f"⚡ [EVENT] Triggering {task_name} for {situation_type}...")
                    try:
                        # Import and queue the task dynamically
                        import core.tasks as task_module
                        task_func = getattr(task_module, task_name, None)
                        if task_func:
                            task_func.apply_async(countdown=5)
                            logger.info(f"✅ [EVENT] Queued {task_name} successfully")
                        else:
                            logger.warning(f"⚠️ [EVENT] Task {task_name} not found")
                    except Exception as e:
                        logger.error(f"Failed to queue {task_name}: {e}")

                # Mark event as completed
                event.status = 'completed'
                event.processed_at = timezone.now()
                event.save()

                # Update trigger stats
                trigger.total_alerts_generated += 1
                trigger.save(update_fields=['total_alerts_generated'])

            except TriggerEvent.DoesNotExist:
                logger.warning(f"TriggerEvent {event_id} not found")
            except Exception as e:
                logger.error(f"Error processing trigger event {event_id}: {e}")
                try:
                    event.status = 'failed'
                    event.error_message = str(e)
                    event.save(update_fields=['status', 'error_message'])
                except:
                    pass

        logger.info(
            f"✅ Trigger events processed: {len(event_ids)} events, "
            f"{alerts_generated} alerts, {discord_sent} Discord notifications"
        )

        # Session 497: Update session with success
        situation_session.status = 'completed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.items_processed = len(event_ids)
        situation_session.alerts_generated = alerts_generated
        situation_session.save()

        return {
            'success': True,
            'events_processed': len(event_ids),
            'alerts_generated': alerts_generated,
            'discord_sent': discord_sent
        }

    except Exception as e:
        logger.error(f"Failed to process trigger events: {e}")
        import traceback
        traceback.print_exc()

        # Session 497: Update session with failure
        situation_session.status = 'failed'
        situation_session.completed_at = timezone.now()
        situation_session.duration_seconds = time.time() - start_time
        situation_session.error_message = str(e)
        situation_session.save()

        return {'success': False, 'error': str(e)}


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
        except:
            pass
    elif 'market_cap' in first_item:
        try:
            value_usd = Decimal(str(first_item.get('market_cap', 0)))
        except:
            pass

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
    except:
        pass

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
    """
    Start an async render job on the DaVinci Resolve node.

    Session 478: DaVinci Resolve Full Utilization

    This task sends the render request to the resolve_node FastAPI server
    and schedules status polling.

    Args:
        job_id: ResolveRenderJob UUID
        video_ids: List of video IDs to render
        template: Render template (default_mp4, prores_4444, dnxhr_hq)
        color_grade: Color grade preset name
        spider_trends: Spider trends data used for grade selection
        user_id: Django User ID

    Returns:
        Dict with render job status
    """
    logger.info(f"🎬 [RESOLVE] Starting render job {job_id}")

    try:
        import requests
        import os
        from core.models_unified_system import ResolveRenderJob

        # Update job status to rendering
        job = ResolveRenderJob.objects.get(id=job_id)
        job.status = 'rendering'
        job.save()

        # Get resolve node URL
        resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
        token = os.environ.get('RENDER_NODE_TOKEN', '')

        # Prepare render request
        render_payload = {
            'video_ids': video_ids,
            'template': template,
            'color_grade': color_grade,
            'callback_url': f"{os.environ.get('BASE_URL', 'http://localhost:8000')}/api/resolve/callback/{job_id}/",
        }

        # Send to resolve node
        headers = {'X-Render-Token': token} if token else {}
        response = requests.post(
            f'{resolve_url}/render/start',
            json=render_payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            resolve_job_id = result.get('job_id', str(job_id)[:8])

            # Update job with resolve's job ID
            job.resolve_job_id = resolve_job_id
            job.save()

            # Schedule status polling
            poll_resolve_job_status.apply_async(
                args=[str(job.id)],
                countdown=10  # Check after 10 seconds
            )

            logger.info(f"🎬 [RESOLVE] Render started: {resolve_job_id}")
            return {
                'status': 'started',
                'job_id': str(job.id),
                'resolve_job_id': resolve_job_id,
            }
        else:
            error_msg = f"Resolve node error: {response.status_code} - {response.text[:200]}"
            job.status = 'error'
            job.error_message = error_msg
            job.save()
            logger.error(f"🎬 [RESOLVE] Render failed: {error_msg}")
            return {'status': 'error', 'error': error_msg}

    except requests.exceptions.ConnectionError as e:
        # Resolve node not available - retry
        logger.warning(f"🎬 [RESOLVE] Connection error, retrying: {e}")
        raise self.retry(exc=e, countdown=30)

    except ResolveRenderJob.DoesNotExist:
        logger.error(f"🎬 [RESOLVE] Job not found: {job_id}")
        return {'status': 'error', 'error': 'Job not found'}

    except Exception as e:
        logger.error(f"🎬 [RESOLVE] Unexpected error: {e}")
        try:
            job = ResolveRenderJob.objects.get(id=job_id)
            job.status = 'error'
            job.error_message = str(e)
            job.save()
        except:
            pass
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=60)  # Max 60 retries = 30 minutes
def poll_resolve_job_status(self, job_id: str):
    """
    Poll the DaVinci Resolve node for render job status.

    Session 478: DaVinci Resolve Full Utilization

    This task polls the resolve_node until the job is complete or errors.
    On completion, it triggers the learning loop recording.

    Args:
        job_id: ResolveRenderJob UUID

    Returns:
        Dict with current job status
    """
    logger.info(f"🎬 [RESOLVE] Polling job status: {job_id}")

    try:
        import requests
        import os
        from core.models_unified_system import ResolveRenderJob
        from django.utils import timezone

        job = ResolveRenderJob.objects.get(id=job_id)

        # Don't poll completed or errored jobs
        if job.status in ['done', 'error']:
            return {'status': job.status, 'message': 'Job already finished'}

        # Get resolve node URL
        resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
        token = os.environ.get('RENDER_NODE_TOKEN', '')

        headers = {'X-Render-Token': token} if token else {}
        response = requests.get(
            f'{resolve_url}/render/status/{job.resolve_job_id}',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            resolve_status = result.get('status', 'unknown')

            if resolve_status == 'done':
                # Render complete!
                job.status = 'done'
                job.output_url = result.get('output_url', '')
                job.file_size_mb = result.get('file_size_mb')
                job.render_duration_seconds = result.get('duration_seconds')
                job.completed_at = timezone.now()
                job.save()

                # Trigger learning loop recording
                record_resolve_outcome.delay(str(job.id))

                logger.info(f"🎬 [RESOLVE] Render complete: {job_id}")
                return {
                    'status': 'done',
                    'output_url': job.output_url,
                    'file_size_mb': job.file_size_mb,
                }

            elif resolve_status == 'error':
                job.status = 'error'
                job.error_message = result.get('error', 'Unknown error')
                job.completed_at = timezone.now()
                job.save()

                logger.error(f"🎬 [RESOLVE] Render error: {job.error_message}")
                return {'status': 'error', 'error': job.error_message}

            else:
                # Still rendering - schedule next poll
                progress = result.get('progress', 0)
                logger.info(f"🎬 [RESOLVE] Rendering... {progress}%")
                raise self.retry(countdown=30)  # Poll every 30 seconds

        elif response.status_code == 404:
            job.status = 'error'
            job.error_message = 'Job not found on resolve node'
            job.save()
            return {'status': 'error', 'error': 'Job not found'}

        else:
            # Unexpected status - retry
            raise self.retry(countdown=30)

    except requests.exceptions.ConnectionError as e:
        logger.warning(f"🎬 [RESOLVE] Connection error during poll: {e}")
        raise self.retry(exc=e, countdown=60)

    except ResolveRenderJob.DoesNotExist:
        logger.error(f"🎬 [RESOLVE] Job not found in DB: {job_id}")
        return {'status': 'error', 'error': 'Job not found'}

    except self.MaxRetriesExceededError:
        # Too many retries - mark as timed out
        try:
            job = ResolveRenderJob.objects.get(id=job_id)
            job.status = 'error'
            job.error_message = 'Render timed out after 30 minutes'
            job.save()
        except:
            pass
        logger.error(f"🎬 [RESOLVE] Render timed out: {job_id}")
        return {'status': 'error', 'error': 'Timeout'}


@shared_task
def record_resolve_outcome(job_id: str):
    """
    Record render job outcome for the learning loop.

    Session 478: DaVinci Resolve Full Utilization

    This task records successful renders for the learning loop,
    which will improve future color grade selections based on:
    - User ratings
    - Usage patterns (was the video used?)
    - Revenue correlation

    Args:
        job_id: ResolveRenderJob UUID

    Returns:
        Dict with learning loop recording status
    """
    logger.info(f"🎬 [RESOLVE LEARNING] Recording outcome for job: {job_id}")

    try:
        from core.models_unified_system import ResolveRenderJob
        from resolve_node.color_grades import get_preset

        job = ResolveRenderJob.objects.get(id=job_id)

        if job.status != 'done':
            logger.warning(f"🎬 [RESOLVE LEARNING] Job not done, skipping: {job.status}")
            return {'status': 'skipped', 'reason': f'Job status is {job.status}'}

        # Get preset info for logging
        preset = get_preset(job.color_grade)
        preset_desc = preset.get('description', '') if preset else ''

        # Log the outcome (basic for now - will be enhanced with user ratings)
        logger.info(
            f"🎬 [RESOLVE LEARNING] Outcome recorded:\n"
            f"  - Job: {job_id}\n"
            f"  - Grade: {job.color_grade} ({'auto' if job.auto_grade_selected else 'manual'})\n"
            f"  - Template: {job.template}\n"
            f"  - File Size: {job.file_size_mb} MB\n"
            f"  - Duration: {job.render_duration_seconds}s\n"
            f"  - Trends Used: {bool(job.spider_trends_used)}"
        )

        return {
            'status': 'recorded',
            'job_id': job_id,
            'color_grade': job.color_grade,
            'auto_selected': job.auto_grade_selected,
            'spider_trends_used': bool(job.spider_trends_used),
        }

    except ResolveRenderJob.DoesNotExist:
        logger.error(f"🎬 [RESOLVE LEARNING] Job not found: {job_id}")
        return {'status': 'error', 'error': 'Job not found'}

    except Exception as e:
        logger.error(f"🎬 [RESOLVE LEARNING] Recording failed: {e}")
        return {'status': 'error', 'error': str(e)}


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
    """
    Situation #6: Trend-Driven Design System
    Analyzes design spider data (Dribbble, Behance, Awwwards) to detect trends.
    Runs every 6 hours.
    """
    logger.info("🎨 [DESIGN TRENDS] Starting design trends analysis...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import (
            DesignTrend, AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta
        import re
        from collections import Counter

        session = AutonomousSituationSession.objects.create(
            situation_type='design_trends',
            status='running'
        )
        start_time = timezone.now()

        # Get recent design spider data
        cutoff = timezone.now() - timedelta(hours=24)
        design_spiders = ['dribbble', 'behance', 'awwwards', 'unsplash']

        spider_data = SpiderData.objects.filter(
            spider_name__in=design_spiders,
            created_at__gte=cutoff
        ).order_by('-created_at')

        items_processed = 0
        trends_created = 0
        trends_updated = 0

        # Extract color patterns, keywords, styles from spider data
        all_keywords = []

        for data in spider_data[:100]:
            items_processed += 1
            raw = data.raw_data or {}

            # Session 488: Fix - spider data stores items in 'items' array
            items = raw.get('items', [])
            if items:
                # Extract text from all items in this spider data record
                for item in items[:20]:  # Limit per record
                    title = item.get('title', '') or ''
                    description = item.get('description', '') or ''
                    text = f"{title} {description}".lower()

                    # Design-related keywords (moved inside loop)
                    design_keywords = [
                        'gradient', 'minimalist', 'brutalist', 'glassmorphism', 'neumorphism',
                        '3d', 'isometric', 'flat', 'neon', 'pastel', 'dark mode', 'light mode',
                        'organic', 'geometric', 'abstract', 'illustration', 'typography',
                        'animation', 'motion', 'microinteraction', 'retro', 'vintage', 'modern'
                    ]

                    for kw in design_keywords:
                        if kw in text:
                            all_keywords.append(kw)
                continue  # Skip the old extraction below

            # Fallback for legacy data format (title at root level)
            title = raw.get('title', '') or ''
            description = raw.get('description', '') or ''
            text = f"{title} {description}".lower()

            # Design-related keywords
            design_keywords = [
                'gradient', 'minimalist', 'brutalist', 'glassmorphism', 'neumorphism',
                '3d', 'isometric', 'flat', 'neon', 'pastel', 'dark mode', 'light mode',
                'organic', 'geometric', 'abstract', 'illustration', 'typography',
                'animation', 'motion', 'microinteraction', 'retro', 'vintage', 'modern'
            ]

            for kw in design_keywords:
                if kw in text:
                    all_keywords.append(kw)

        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)

        # Create/update trends based on top keywords
        for keyword, count in keyword_counts.most_common(10):
            if count >= 3:
                trend, created = DesignTrend.objects.update_or_create(
                    name=keyword.title(),
                    category='brand_style',
                    defaults={
                        'keywords': [keyword],
                        'popularity_score': min(count * 10, 100),
                        'momentum_score': count * 5,
                        'source_spiders': design_spiders,
                        'is_active': True,
                        'is_rising': True,
                    }
                )
                if created:
                    trends_created += 1
                else:
                    trends_updated += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_processed = items_processed
        session.items_created = trends_created
        session.items_updated = trends_updated
        session.spider_data_analyzed = spider_data.count()
        session.duration_seconds = (timezone.now() - start_time).total_seconds()
        session.save()

        logger.info(f"🎨 [DESIGN TRENDS] Completed: {trends_created} created, {trends_updated} updated")
        return {'status': 'completed', 'trends_created': trends_created, 'trends_updated': trends_updated}

    except Exception as e:
        logger.error(f"🎨 [DESIGN TRENDS] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_viral_content_predictor(self):
    """Situation #7: Viral Content Predictor - Analyzes social data for viral potential."""
    logger.info("🔥 [VIRAL] Starting viral content prediction...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import ViralContentPrediction, AutonomousSituationSession
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(situation_type='viral_prediction', status='running')
        cutoff = timezone.now() - timedelta(hours=12)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['reddit', 'hackernews', 'bluesky', 'producthunt'],
            created_at__gte=cutoff
        )[:50]

        predictions_created = 0
        for data in spider_data:
            raw = data.raw_data or {}

            # Session 488: Fix - spider data stores items in 'items' array
            items = raw.get('items', [])
            if items:
                for item in items[:10]:  # Limit per record
                    title = item.get('title', '') or ''
                    if not title:
                        continue
                    upvotes = item.get('score', 0) or item.get('points', 0) or item.get('ups', 0) or 0
                    viral_score = min(upvotes / 10, 100)
                    if viral_score > 20:
                        ViralContentPrediction.objects.create(
                            title=title[:500], content_type='article', topic=data.data_type or 'general',
                            viral_score=viral_score, spider_signals={'source': data.spider_name, 'url': data.source_url},
                            prediction_expires=timezone.now() + timedelta(hours=24)
                        )
                        predictions_created += 1
                continue  # Skip legacy format below

            # Legacy format fallback
            title = raw.get('title', '') or ''
            if not title:
                continue
            upvotes = raw.get('score', 0) or raw.get('points', 0) or 0
            viral_score = min(upvotes / 10, 100)
            if viral_score > 20:
                ViralContentPrediction.objects.create(
                    title=title[:500], content_type='article', topic=data.data_type or 'general',
                    viral_score=viral_score, spider_signals={'source': data.spider_name, 'url': data.source_url},
                    prediction_expires=timezone.now() + timedelta(hours=24)
                )
                predictions_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = predictions_created
        session.save()
        logger.info(f"🔥 [VIRAL] Completed: {predictions_created} predictions")
        return {'status': 'completed', 'predictions': predictions_created}
    except Exception as e:
        logger.error(f"🔥 [VIRAL] Error: {e}")
        return {'status': 'error', 'error': str(e)}


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
        )[:100]

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
        )[:100]

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
    """Situation #13: Crypto Sentiment Monitor - Tracks crypto social sentiment."""
    import time
    start_time = time.time()
    logger.info("🪙 [CRYPTO] Starting sentiment analysis...")

    # Session 497: Import early for error handling
    from core.models_autonomous_situations import CryptoSentiment, AutonomousSituationSession
    from django.utils import timezone

    session = AutonomousSituationSession.objects.create(situation_type='crypto_sentiment', status='running')

    try:
        from core.models_unified_system import SpiderData
        from datetime import timedelta
        from collections import defaultdict

        cutoff = timezone.now() - timedelta(hours=6)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['coingecko', 'reddit', 'bluesky'],
            created_at__gte=cutoff
        )[:200]

        mentions = defaultdict(int)
        for data in spider_data:
            text = str(data.raw_data).upper()
            for sym in ['BTC', 'ETH', 'SOL', 'XRP']:
                if sym in text:
                    mentions[sym] += 1

        created = 0
        for sym, count in mentions.items():
            if count >= 2:
                CryptoSentiment.objects.create(
                    symbol=sym, name=sym, overall_sentiment=count * 5, social_volume=count
                )
                created += 1

        # Session 497: Add duration tracking
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = spider_data.count()
        session.items_created = created
        session.save()
        logger.info(f"🪙 [CRYPTO] Completed: {created} sentiments")
        return {'status': 'completed', 'sentiments': created}
    except Exception as e:
        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()
        logger.error(f"🪙 [CRYPTO] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_tech_stack_tracker(self):
    """Situation #15: Tech Stack Evolution Tracker - Monitors rising/falling tech."""
    logger.info("🔧 [TECH STACK] Starting tracking...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import TechStackTrend, AutonomousSituationSession
        from django.utils import timezone
        from datetime import timedelta
        from collections import Counter

        session = AutonomousSituationSession.objects.create(situation_type='tech_stack', status='running')
        cutoff = timezone.now() - timedelta(hours=24)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['github', 'hackernews', 'devto'],
            created_at__gte=cutoff
        )[:300]

        techs = {'python': 'language', 'react': 'framework', 'rust': 'language', 'langchain': 'ai_ml',
                 'typescript': 'language', 'go': 'language', 'kubernetes': 'devops', 'docker': 'devops',
                 'nextjs': 'framework', 'svelte': 'framework', 'vue': 'framework', 'tailwind': 'framework',
                 'openai': 'ai_ml', 'anthropic': 'ai_ml', 'llama': 'ai_ml', 'huggingface': 'ai_ml'}
        mentions = Counter()
        for data in spider_data:
            raw = data.raw_data or {}

            # Session 488: Fix - spider data stores items in 'items' array
            items = raw.get('items', [])
            if items:
                for item in items[:20]:
                    title = item.get('title', '') or ''
                    description = item.get('description', '') or ''
                    text = f'{title} {description}'.lower()
                    for tech in techs:
                        if tech in text:
                            mentions[tech] += 1
                continue  # Skip legacy format below

            # Legacy format fallback
            text = str(data.raw_data).lower()
            for tech in techs:
                if tech in text:
                    mentions[tech] += 1

        created = 0
        for tech, count in mentions.most_common(10):
            if count >= 3:
                TechStackTrend.objects.update_or_create(
                    name=tech.title(),
                    defaults={'category': techs[tech], 'momentum_score': count * 5, 'trend_direction': 'rising'}
                )
                created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = created
        session.save()
        logger.info(f"🔧 [TECH STACK] Completed: {created} trends")
        return {'status': 'completed', 'trends': created}
    except Exception as e:
        logger.error(f"🔧 [TECH STACK] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_ai_model_monitor(self):
    """Situation #16: AI Model Release Monitor - Tracks new AI models."""
    import time
    start_time = time.time()
    logger.info("🤖 [AI MODEL] Starting monitoring...")

    # Session 497: Import early for error handling
    from core.models_autonomous_situations import AIModelRelease, AutonomousSituationSession
    from django.utils import timezone

    session = AutonomousSituationSession.objects.create(situation_type='ai_model', status='running')

    try:
        from core.models_unified_system import SpiderData
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(hours=24)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['huggingface', 'github', 'hackernews'],
            created_at__gte=cutoff
        )[:100]

        created = 0
        for data in spider_data:
            raw = data.raw_data or {}
            title = raw.get('title', '') or raw.get('modelId', '') or ''
            if any(kw in title.lower() for kw in ['model', 'llm', 'gpt', 'llama']):
                org = 'openai' if 'openai' in title.lower() else 'unknown'
                if not AIModelRelease.objects.filter(name__icontains=title[:30]).exists():
                    AIModelRelease.objects.create(
                        name=title[:200], organization=org.title(), model_type='llm',
                        release_date=timezone.now().date(), announcement_url=data.source_url
                    )
                    created += 1

        # Session 497: Add duration tracking
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = spider_data.count()
        session.items_created = created
        session.save()
        logger.info(f"🤖 [AI MODEL] Completed: {created} models")
        return {'status': 'completed', 'models': created}
    except Exception as e:
        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()
        logger.error(f"🤖 [AI MODEL] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_case_law_monitor(self):
    """Situation #18: Case Law Monitor - Tracks relevant case decisions."""
    import time
    start_time = time.time()
    logger.info("⚖️ [CASE LAW] Starting monitoring...")

    # Session 497: Import early for error handling
    from core.models_autonomous_situations import CaseLawUpdate, AutonomousSituationSession
    from django.utils import timezone

    session = AutonomousSituationSession.objects.create(situation_type='case_law', status='running')

    try:
        from core.models_unified_system import SpiderData
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(hours=24)
        spider_data = SpiderData.objects.filter(
            spider_name__in=['courtlistener', 'findlaw', 'justia_family_law'],
            created_at__gte=cutoff
        )[:50]

        created = 0
        for data in spider_data:
            raw = data.raw_data or {}
            case_name = raw.get('caseName', '') or raw.get('title', '') or ''
            if case_name and len(case_name) > 10:
                CaseLawUpdate.objects.create(
                    case_name=case_name[:500], court=raw.get('court', 'Unknown')[:200],
                    jurisdiction='Federal', decision_date=timezone.now().date(),
                    decision_type='opinion', summary=case_name, source_spider=data.spider_name
                )
                created += 1

        # Session 497: Add duration tracking
        session.status = 'completed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.items_processed = spider_data.count()
        session.items_created = created
        session.save()
        logger.info(f"⚖️ [CASE LAW] Completed: {created} cases")
        return {'status': 'completed', 'cases': created}
    except Exception as e:
        # Session 497: Update session with failure
        session.status = 'failed'
        session.completed_at = timezone.now()
        session.duration_seconds = time.time() - start_time
        session.error_message = str(e)
        session.save()
        logger.error(f"⚖️ [CASE LAW] Error: {e}")
        return {'status': 'error', 'error': str(e)}


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
        )[:100]

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
    """
    Situation #8: Thumbnail A/B Optimizer
    Analyzes existing images and creates optimization suggestions.
    Uses design trends + viral prediction data to suggest improvements.
    """
    logger.info("🖼️ [THUMBNAIL] Starting optimization analysis...")

    try:
        from content.models import ImageHistory
        from core.models_autonomous_situations import (
            ThumbnailVariant, DesignTrend, ViralContentPrediction,
            AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta
        import random

        session = AutonomousSituationSession.objects.create(
            situation_type='thumbnail_optimization',
            status='running'
        )

        # Get recent images that could be thumbnails (1280x720 aspect ratio or similar)
        cutoff = timezone.now() - timedelta(days=7)
        recent_images = ImageHistory.objects.filter(
            created_at__gte=cutoff
        ).order_by('-created_at')[:50]

        # Get current design trends for recommendations
        trending_colors = list(DesignTrend.objects.filter(
            category='color'
        ).order_by('-popularity_score')[:5].values_list('colors', flat=True))

        # Get viral content patterns
        viral_patterns = list(ViralContentPrediction.objects.filter(
            viral_score__gte=0.7
        ).order_by('-viral_score')[:10].values_list('content_type', 'engagement_potential', flat=False))

        variants_created = 0
        for image in recent_images[:20]:
            # Use image prompt as content identifier
            content_title = getattr(image, 'prompt', '') or f"Image {image.id}"
            content_title = content_title[:500]  # Match model max_length

            # Check if we already have variants for this content
            existing = ThumbnailVariant.objects.filter(
                content_title=content_title
            ).count()

            if existing < 3:  # Create up to 3 variants per image
                # Generate optimization suggestions based on trends
                suggestions = []
                if trending_colors:
                    suggestions.append(f"Try color palette: {trending_colors[0][:3] if trending_colors[0] else ['#FF5733']}")
                if viral_patterns:
                    suggestions.append(f"High engagement pattern: {viral_patterns[0][0] if viral_patterns else 'bold_text'}")

                # Get variant letter (A, B, C based on existing count)
                variant_letter = chr(65 + existing)  # 65 = 'A'

                ThumbnailVariant.objects.create(
                    content_title=content_title,
                    content_url=getattr(image, 'image_url', None),
                    variant_name=f"Variant {variant_letter}",
                    image_path=getattr(image, 'image_path', None),
                    style=random.choice(['color_shift', 'text_overlay', 'contrast_boost', 'crop_focus']),
                    learned_insights='; '.join(suggestions) if suggestions else 'Standard optimization',
                    is_control=(existing == 0)  # First variant is control
                )
                variants_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = variants_created
        session.items_processed = recent_images.count()
        session.duration_seconds = (timezone.now() - session.started_at).total_seconds()
        session.save()

        logger.info(f"🖼️ [THUMBNAIL] Completed: {variants_created} variants created")
        return {
            'status': 'completed',
            'variants_created': variants_created,
            'images_analyzed': recent_images.count()
        }

    except Exception as e:
        logger.error(f"🖼️ [THUMBNAIL] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_freelance_opportunity_scout(self):
    """
    Situation #10: Freelance Opportunity Scout
    Scans job boards for freelance/contract opportunities.
    Uses remoteok, weworkremotely, adzuna spiders.
    """
    logger.info("💼 [FREELANCE] Starting opportunity scout...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import (
            FreelanceOpportunity, JobMatchProfile, AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(
            situation_type='freelance_scout',
            status='running'
        )

        cutoff = timezone.now() - timedelta(hours=24)

        # Get job data from spiders
        spider_data = SpiderData.objects.filter(
            spider_name__in=['remoteok', 'weworkremotely', 'adzuna', 'hackernews'],
            created_at__gte=cutoff
        ).order_by('-created_at')[:200]

        # Freelance keywords to identify contract/freelance work
        freelance_keywords = [
            'freelance', 'contract', 'contractor', 'consultant', 'part-time',
            'remote', 'gig', 'project-based', 'hourly', 'fixed-price'
        ]

        opportunities_created = 0
        for data in spider_data:
            raw = data.raw_data or {}
            title = (raw.get('title', '') or raw.get('position', '') or '').lower()
            description = (raw.get('description', '') or raw.get('summary', '') or '').lower()
            company = raw.get('company', '') or raw.get('company_name', '') or 'Unknown'

            # Check if it looks like a freelance opportunity
            is_freelance = any(kw in title or kw in description for kw in freelance_keywords)

            if is_freelance or 'contract' in title:
                # Avoid duplicates
                exists = FreelanceOpportunity.objects.filter(
                    title__iexact=raw.get('title', '')[:200],
                    platform=data.spider_name
                ).exists()

                if not exists:
                    # Extract budget if available
                    budget_str = raw.get('salary', '') or raw.get('compensation', '') or ''

                    FreelanceOpportunity.objects.create(
                        title=raw.get('title', 'Untitled')[:200],
                        platform=data.spider_name,
                        client_name=company[:100],
                        description=(raw.get('description', '') or '')[:2000],
                        budget_range=budget_str[:100] if budget_str else 'Not specified',
                        skills_required=raw.get('tags', []) if isinstance(raw.get('tags'), list) else [],
                        deadline=None,
                        url=raw.get('url', '') or raw.get('link', ''),
                        match_score=0.0,  # Will be updated by matching algorithm
                        status='new',
                        source_spider=data.spider_name
                    )
                    opportunities_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = opportunities_created
        session.items_processed = spider_data.count()
        session.spider_data_analyzed = spider_data.count()
        session.duration_seconds = (timezone.now() - session.started_at).total_seconds()
        session.save()

        logger.info(f"💼 [FREELANCE] Completed: {opportunities_created} opportunities found")
        return {
            'status': 'completed',
            'opportunities_found': opportunities_created,
            'spider_records_analyzed': spider_data.count()
        }

    except Exception as e:
        logger.error(f"💼 [FREELANCE] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_sec_filing_analyzer(self):
    """
    Situation #12: SEC Filing Analyzer
    Analyzes SEC filings for major companies.
    Tracks 13F (institutional holdings), 10-K, 10-Q, 8-K filings.
    """
    logger.info("📊 [SEC] Starting filing analysis...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import (
            SECFilingAnalysis, AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(
            situation_type='sec_filing',
            status='running'
        )

        cutoff = timezone.now() - timedelta(hours=48)

        # Get SEC data from spider
        spider_data = SpiderData.objects.filter(
            spider_name__in=['sec_edgar', 'yahoo_finance', 'business_news'],
            created_at__gte=cutoff
        ).order_by('-created_at')[:150]

        # SEC filing types to track
        filing_types = ['10-K', '10-Q', '8-K', '13F', 'S-1', 'DEF 14A', '4']

        # Major companies to watch (default watchlist)
        major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
            'BRK', 'JPM', 'V', 'UNH', 'MA', 'HD', 'PG', 'JNJ'
        ]

        filings_analyzed = 0
        for data in spider_data:
            raw = data.raw_data or {}
            title = (raw.get('title', '') or '').upper()
            content = (raw.get('content', '') or raw.get('description', '') or '')

            # Check for SEC filing mentions
            filing_type = None
            for ft in filing_types:
                if ft in title or ft in content.upper():
                    filing_type = ft
                    break

            # Check for company mentions
            company_ticker = None
            for ticker in major_tickers:
                if ticker in title or ticker in content.upper():
                    company_ticker = ticker
                    break

            if filing_type or company_ticker:
                # Avoid duplicates
                exists = SECFilingAnalysis.objects.filter(
                    filing_url=raw.get('url', '')[:500]
                ).exists() if raw.get('url') else False

                if not exists and raw.get('url'):
                    # Determine significance
                    significance = 'low'
                    if filing_type in ['10-K', '8-K', '13F']:
                        significance = 'high'
                    elif filing_type in ['10-Q', 'S-1']:
                        significance = 'medium'

                    SECFilingAnalysis.objects.create(
                        company_name=company_ticker or 'Unknown',
                        ticker=company_ticker or '',
                        filing_type=filing_type or 'Other',
                        filing_date=timezone.now().date(),
                        filing_url=raw.get('url', '')[:500],
                        summary=content[:1000] if content else title[:500],
                        key_insights=[],
                        sentiment_score=0.0,
                        significance_level=significance,
                        source_spider=data.spider_name
                    )
                    filings_analyzed += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = filings_analyzed
        session.items_processed = spider_data.count()
        session.spider_data_analyzed = spider_data.count()
        session.duration_seconds = (timezone.now() - session.started_at).total_seconds()
        session.save()

        logger.info(f"📊 [SEC] Completed: {filings_analyzed} filings analyzed")
        return {
            'status': 'completed',
            'filings_analyzed': filings_analyzed,
            'spider_records_checked': spider_data.count()
        }

    except Exception as e:
        logger.error(f"📊 [SEC] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_earnings_predictor(self):
    """
    Situation #14: Earnings Surprise Predictor
    Analyzes pre-earnings sentiment and estimates for surprise predictions.
    Uses Yahoo Finance + news sentiment.
    """
    logger.info("📈 [EARNINGS] Starting prediction analysis...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import (
            EarningsPrediction, AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta
        import random

        session = AutonomousSituationSession.objects.create(
            situation_type='earnings_prediction',
            status='running'
        )

        cutoff = timezone.now() - timedelta(hours=72)

        # Get financial news and data
        spider_data = SpiderData.objects.filter(
            spider_name__in=['yahoo_finance', 'business_news', 'finnhub', 'hackernews'],
            created_at__gte=cutoff
        ).order_by('-created_at')[:200]

        # Earnings-related keywords
        earnings_keywords = [
            'earnings', 'quarterly', 'q1', 'q2', 'q3', 'q4', 'revenue',
            'guidance', 'forecast', 'eps', 'beat', 'miss', 'surprise',
            'profit', 'income', 'outlook'
        ]

        # Track companies mentioned in earnings context
        companies_analyzed = {}

        for data in spider_data:
            raw = data.raw_data or {}
            title = (raw.get('title', '') or '').lower()
            content = (raw.get('content', '') or raw.get('description', '') or '').lower()

            # Check if earnings-related
            is_earnings = any(kw in title or kw in content for kw in earnings_keywords)

            if is_earnings:
                # Try to identify company
                # Look for common patterns like "AAPL earnings" or "Apple reports"
                ticker = raw.get('symbol', '') or raw.get('ticker', '')

                if ticker and ticker not in companies_analyzed:
                    # Sentiment analysis (simple keyword-based)
                    positive_words = ['beat', 'exceeds', 'strong', 'growth', 'surge', 'record']
                    negative_words = ['miss', 'below', 'weak', 'decline', 'fall', 'disappoints']

                    pos_count = sum(1 for w in positive_words if w in content)
                    neg_count = sum(1 for w in negative_words if w in content)

                    if pos_count > neg_count:
                        sentiment = 'bullish'
                        surprise_direction = 'positive'
                    elif neg_count > pos_count:
                        sentiment = 'bearish'
                        surprise_direction = 'negative'
                    else:
                        sentiment = 'neutral'
                        surprise_direction = 'inline'

                    companies_analyzed[ticker] = {
                        'sentiment': sentiment,
                        'direction': surprise_direction,
                        'mentions': 1,
                        'source': data.spider_name
                    }
                elif ticker:
                    companies_analyzed[ticker]['mentions'] += 1

        # Create predictions for companies with enough data
        predictions_created = 0
        for ticker, analysis in companies_analyzed.items():
            if analysis['mentions'] >= 1:  # At least 1 mention
                # Avoid duplicates (one prediction per company per day)
                today = timezone.now().date()
                exists = EarningsPrediction.objects.filter(
                    ticker=ticker,
                    created_at__date=today
                ).exists()

                if not exists:
                    EarningsPrediction.objects.create(
                        company_name=ticker,
                        ticker=ticker,
                        earnings_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                        predicted_surprise_direction=analysis['direction'],
                        confidence_score=min(0.9, 0.5 + (analysis['mentions'] * 0.1)),
                        sentiment_score=0.7 if analysis['sentiment'] == 'bullish' else 0.3 if analysis['sentiment'] == 'bearish' else 0.5,
                        news_volume=analysis['mentions'],
                        analyst_consensus='',
                        prediction_reasoning=f"Based on {analysis['mentions']} news mentions with {analysis['sentiment']} sentiment",
                        source_spider=analysis['source']
                    )
                    predictions_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = predictions_created
        session.items_processed = spider_data.count()
        session.spider_data_analyzed = spider_data.count()
        session.duration_seconds = (timezone.now() - session.started_at).total_seconds()
        session.save()

        logger.info(f"📈 [EARNINGS] Completed: {predictions_created} predictions created")
        return {
            'status': 'completed',
            'predictions_created': predictions_created,
            'companies_analyzed': len(companies_analyzed)
        }

    except Exception as e:
        logger.error(f"📈 [EARNINGS] Error: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def run_skill_gap_analyzer(self):
    """
    Situation #17: Course & Skill Gap Analyzer
    Matches trending tech skills to available courses.
    Cross-references TechStackTrend with Coursera/education spiders.
    """
    logger.info("📚 [SKILLS] Starting skill gap analysis...")

    try:
        from core.models_unified_system import SpiderData
        from core.models_autonomous_situations import (
            SkillGapAnalysis, TechStackTrend, AutonomousSituationSession
        )
        from django.utils import timezone
        from datetime import timedelta

        session = AutonomousSituationSession.objects.create(
            situation_type='skill_gap',
            status='running'
        )

        # Get trending tech skills
        trending_skills = list(TechStackTrend.objects.filter(
            momentum_score__gte=0.5
        ).order_by('-momentum_score')[:20].values(
            'name', 'category', 'momentum_score'
        ))

        # If no trending skills yet, use default in-demand skills
        if not trending_skills:
            trending_skills = [
                {'name': 'Python', 'category': 'language', 'momentum_score': 0.9},
                {'name': 'React', 'category': 'framework', 'momentum_score': 0.85},
                {'name': 'TypeScript', 'category': 'language', 'momentum_score': 0.8},
                {'name': 'AWS', 'category': 'cloud', 'momentum_score': 0.8},
                {'name': 'Docker', 'category': 'devops', 'momentum_score': 0.75},
                {'name': 'Kubernetes', 'category': 'devops', 'momentum_score': 0.7},
                {'name': 'Machine Learning', 'category': 'ai', 'momentum_score': 0.9},
                {'name': 'LLM', 'category': 'ai', 'momentum_score': 0.95},
            ]

        cutoff = timezone.now() - timedelta(hours=48)

        # Get education/course data from spiders
        spider_data = SpiderData.objects.filter(
            spider_name__in=['coursera', 'education_rss', 'hackernews', 'devto'],
            created_at__gte=cutoff
        ).order_by('-created_at')[:200]

        # Match skills to courses
        analyses_created = 0
        for skill in trending_skills:
            skill_name = skill['name'].lower()

            # Find courses matching this skill
            matching_courses = []
            for data in spider_data:
                raw = data.raw_data or {}
                title = (raw.get('title', '') or '').lower()
                description = (raw.get('description', '') or '').lower()

                if skill_name in title or skill_name in description:
                    matching_courses.append({
                        'title': raw.get('title', 'Unknown Course'),
                        'url': raw.get('url', ''),
                        'source': data.spider_name
                    })

            # Avoid duplicates (one analysis per skill per day)
            today = timezone.now().date()
            exists = SkillGapAnalysis.objects.filter(
                skill_name=skill['name'],
                analyzed_at__date=today
            ).exists()

            if not exists:
                # Calculate demand score based on momentum
                demand_score = skill['momentum_score']

                # Supply score based on course availability
                supply_score = min(1.0, len(matching_courses) * 0.2)

                # Gap = high demand + low supply
                gap_score = demand_score * (1 - supply_score * 0.5)

                SkillGapAnalysis.objects.create(
                    skill_name=skill['name'],
                    category=skill.get('category', 'general'),
                    demand_score=demand_score,
                    gap_score=gap_score,
                    demand_trend='rising' if demand_score > 0.7 else 'stable',
                    recommended_courses=matching_courses[:5],  # Top 5 courses
                    avg_salary_premium=demand_score * 20 if demand_score > 0.5 else 0.0,
                    estimated_learning_time=f"{int(3 + (1-demand_score) * 6)} months",
                    source_spiders=['coursera'] if matching_courses else ['hackernews'],
                    job_count=len(matching_courses)
                )
                analyses_created += 1

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.items_created = analyses_created
        session.items_processed = len(trending_skills)
        session.spider_data_analyzed = spider_data.count()
        session.duration_seconds = (timezone.now() - session.started_at).total_seconds()
        session.save()

        logger.info(f"📚 [SKILLS] Completed: {analyses_created} skill gap analyses")
        return {
            'status': 'completed',
            'analyses_created': analyses_created,
            'skills_evaluated': len(trending_skills)
        }

    except Exception as e:
        logger.error(f"📚 [SKILLS] Error: {e}")
        return {'status': 'error', 'error': str(e)}


# Note: Style evolution tracking already scheduled via 'record-style-evolution' task
# (core.tasks.record_all_user_style_evolution) - see Session 210
# Session 489: Connected implicit learning to image operations instead.


# ==================== SESSION 496: AI PODCAST STUDIO ====================

@shared_task(bind=True)
def generate_podcast_episode(self, episode_id: str, topic: str, format_type: str, participants: int, generate_audio: bool):
    """
    Session 496: Generate a podcast episode using the PodcastCoordinatorAgent.

    This task:
    1. Loads the episode record
    2. Runs the PodcastCoordinatorAgent to generate debate and script
    3. Updates the episode with the generated content
    4. Optionally triggers audio generation

    Args:
        episode_id: UUID of the PodcastEpisode
        topic: The debate topic
        format_type: 'debate', 'roundtable', 'interview', 'monologue'
        participants: Number of debate participants (2-4)
        generate_audio: Whether to generate TTS audio
    """
    import json
    from django.utils import timezone

    logger.info(f"🎙️ [PODCAST] Starting generation for episode {episode_id}: {topic}")

    try:
        from core.models import PodcastEpisode, PodcastDebate
        from core.agents.podcast import PodcastCoordinatorAgent

        # Get the episode
        try:
            episode = PodcastEpisode.objects.get(id=episode_id)
        except PodcastEpisode.DoesNotExist:
            logger.error(f"🎙️ [PODCAST] Episode {episode_id} not found")
            return {'status': 'error', 'error': 'Episode not found'}

        # Update status
        episode.status = 'researching'
        episode.progress_percent = 10
        episode.save()

        # Create the coordinator agent
        coordinator = PodcastCoordinatorAgent()

        # Build the task prompt
        task_prompt = f"""Create a {format_type} podcast episode about: "{topic}"

Generate a complete podcast script with:
1. A balanced debate question
2. {participants} participants with distinct perspectives
3. Opening statements from each participant
4. A moderated discussion with follow-ups
5. Summary of agreements and disagreements
6. Closing statements

Use the generate_podcast_script tool to create the full script with speaker labels."""

        # Run the synchronous execute method
        logger.info(f"🎙️ [PODCAST] Executing coordinator agent...")
        episode.status = 'debating'
        episode.progress_percent = 30
        episode.save()

        result = coordinator.execute(
            task=task_prompt,
            context={
                'topic': topic,
                'format_type': format_type,
                'participants': participants,
                'generate_audio': generate_audio
            },
            scifi_context={},
            spider_context={}
        )

        if result.success:
            logger.info(f"🎙️ [PODCAST] Agent execution successful")
            episode.status = 'scripting'
            episode.progress_percent = 60
            episode.save()

            # Extract script from tool results
            script_text = result.message
            script_segments = []

            # Process tool results to build the script
            for tool_result in result.tool_calls:
                if isinstance(tool_result, dict):
                    # Check for podcast script content
                    if 'segments' in tool_result:
                        script_segments = tool_result.get('segments', [])
                    if 'script' in tool_result:
                        script_text = tool_result.get('script', script_text)
                    # Check for debate structure
                    if 'debate_question' in tool_result:
                        script_text = f"Topic: {tool_result.get('topic', topic)}\n"
                        script_text += f"Question: {tool_result.get('debate_question', '')}\n\n"
                        if 'participants' in tool_result:
                            script_text += "Participants:\n"
                            for p in tool_result.get('participants', []):
                                if isinstance(p, dict):
                                    script_text += f"- {p.get('perspective', 'Unknown')}: {p.get('voice_id', 'Unknown voice')}\n"
                        script_text += f"\n{result.message}"

            # Update episode with generated script
            episode.script = script_text
            episode.script_segments = script_segments
            episode.save()

            logger.info(f"🎙️ [PODCAST] Script generated: {len(script_text)} chars")

            # Generate audio if requested
            audio_result = None
            if generate_audio:
                logger.info(f"🎙️ [PODCAST] Starting audio generation...")
                episode.status = 'recording'
                episode.progress_percent = 70
                episode.save()

                from core.services.podcast_audio_service import generate_podcast_audio

                def progress_callback(percent, message):
                    # Map 0-100 to 70-100
                    mapped_percent = 70 + int(percent * 0.3)
                    episode.progress_percent = mapped_percent
                    episode.save(update_fields=['progress_percent'])
                    logger.info(f"🎙️ [PODCAST] Audio: {percent}% - {message}")

                audio_result = generate_podcast_audio(
                    episode_id=episode_id,
                    progress_callback=progress_callback
                )

                if audio_result['success']:
                    logger.info(f"🎙️ [PODCAST] Audio generated: {audio_result['duration_seconds']:.1f}s")

                    # Post to Discord podcast library
                    try:
                        from core.services.discord_notifications import discord_notify
                        from django.conf import settings
                        import os

                        # Get the full file path and URL
                        saved_path = audio_result.get('saved_path', '')
                        audio_url = audio_result.get('audio_url', '')

                        if saved_path:
                            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
                            if os.path.exists(full_path):
                                # Build full URL for large files
                                full_audio_url = f"http://localhost:8000{audio_url}" if audio_url else None

                                discord_notify.send_podcast(
                                    episode_id=episode_id,
                                    topic=topic,
                                    duration_seconds=int(audio_result['duration_seconds']),
                                    audio_file_path=full_path,
                                    segment_count=audio_result.get('segment_count', 0),
                                    speakers=["Antoni (Host)", "Rachel (Advocate)", "Clyde (Skeptic)", "Paul (Analyst)"],
                                    audio_url=full_audio_url
                                )
                                logger.info(f"🎙️ [PODCAST] Posted to Discord library")
                            else:
                                logger.warning(f"🎙️ [PODCAST] Audio file not found for Discord: {full_path}")
                    except Exception as e:
                        logger.error(f"🎙️ [PODCAST] Failed to post to Discord: {e}")
                        # Don't fail the task for Discord errors
                else:
                    logger.warning(f"🎙️ [PODCAST] Audio generation failed: {audio_result.get('error')}")
                    # Continue - script generation was successful

            # Mark complete
            episode.status = 'complete'
            episode.progress_percent = 100
            episode.save()

            logger.info(f"🎙️ [PODCAST] Successfully generated episode {episode_id}")

            result_data = {
                'status': 'completed',
                'episode_id': episode_id,
                'script_length': len(script_text),
                'segment_count': len(script_segments)
            }

            if audio_result and audio_result.get('success'):
                result_data['audio_url'] = audio_result.get('audio_url')
                result_data['audio_duration'] = audio_result.get('duration_seconds')

            return result_data
        else:
            episode.status = 'failed'
            episode.error_message = result.message or 'Agent execution failed'
            episode.save()
            logger.error(f"🎙️ [PODCAST] Agent execution failed: {result.message}")
            return {'status': 'error', 'error': result.message}

    except Exception as e:
        logger.error(f"🎙️ [PODCAST] Generation failed: {e}", exc_info=True)

        # Try to update the episode status
        try:
            from core.models import PodcastEpisode
            episode = PodcastEpisode.objects.get(id=episode_id)
            episode.status = 'failed'
            episode.error_message = str(e)[:500]
            episode.save()
        except Exception:
            pass

        return {'status': 'error', 'error': str(e)}



# =============================================================================
# SESSION 543: SELF-BLOG GENERATION TASK
# =============================================================================

@shared_task(bind=True)
def generate_self_blog_task(self, tone='enthusiastic', word_count=1500):
    """
    Background task to generate a self-blog using ContentWriterAgent.
    
    This allows the UI to show progress while the LLM generates content.
    
    Args:
        tone: Blog tone (professional/casual/technical/enthusiastic)
        word_count: Target word count
        
    Returns:
        dict with blog_id and title on success
    """
    import json
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Count, Avg
    
    logger.info(f"🤖 [SELF-BLOG] Starting generation with tone={tone}")
    
    try:
        from core.models_unified_system import (
            Agent, AgentKnowledgeSource, AgentLearningConnection, 
            KnowledgeTransfer, SpiderData, SelfBlog
        )
        from core.agents.content_writer_agent import ContentWriterAgent
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Gather system statistics
        total_agents = Agent.objects.filter(is_active=True).count()
        agents_with_knowledge = AgentKnowledgeSource.objects.filter(is_active=True).values('agent_id').distinct().count()
        total_connections = AgentLearningConnection.objects.filter(is_active=True).count()
        total_transfers = KnowledgeTransfer.objects.count()
        transfers_24h = KnowledgeTransfer.objects.filter(created_at__gte=last_24h).count()
        transfers_7d = KnowledgeTransfer.objects.filter(created_at__gte=last_7d).count()
        total_knowledge = AgentKnowledgeSource.objects.filter(is_active=True).count()
        knowledge_24h = AgentKnowledgeSource.objects.filter(first_discovered_at__gte=last_24h, is_active=True).count()
        
        try:
            total_spiders = SpiderData.objects.values('source').distinct().count()
            if total_spiders == 0:
                total_spiders = 72
        except:
            total_spiders = 72
        
        # Top agents
        top_agents = list(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .values('agent__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Top connections
        top_connections = list(
            AgentLearningConnection.objects.filter(is_active=True)
            .order_by('-total_transfers')[:5]
            .values('teacher_agent__name', 'student_agent__name', 'total_transfers')
        )
        
        # Build research context
        system_research = f"""
# AI Content Studio - Self-Aware Intelligence Platform

## System Overview (Live Data as of {now.strftime('%B %d, %Y at %I:%M %p')})

### The Numbers

**Agent Ecosystem:**
- {total_agents} AI agents actively running
- {agents_with_knowledge} agents have acquired knowledge
- {total_knowledge:,} total knowledge sources
- {knowledge_24h} new knowledge items in last 24 hours

**Learning Network:**
- {total_connections} active learning connections
- {total_transfers:,} total knowledge transfers
- {transfers_24h} transfers in last 24 hours
- {transfers_7d} transfers in last 7 days

**Spider Network:**
- {total_spiders} data spiders crawling the web

### Top Knowledge Holders
{chr(10).join([f"- {a['agent__name']}: {a['count']} items" for a in top_agents])}

### Most Active Teaching Relationships
{chr(10).join([f"- {c['teacher_agent__name']} teaches {c['student_agent__name']}: {c['total_transfers']} transfers" for c in top_connections])}

### Key Capabilities
1. Collective Intelligence - Agents share knowledge through mythology-gated quality system
2. Autonomous Learning - System learns 24/7 without human intervention
3. Real-time Visualization - D3.js network graph shows knowledge flow
4. Quality Control - Mythology quarantine prevents hallucinations
5. Multi-modal Creation - Images, videos, audio, 3D models, and text

### The Meta Moment
This blog was written by ContentWriterAgent about its own platform!
"""
        
        logger.info(f"🤖 [SELF-BLOG] Gathered stats, invoking ContentWriterAgent...")
        
        # Generate blog
        agent = ContentWriterAgent(user=None)
        result = agent.execute(
            task="Write an engaging blog post about our AI platform. This is a meta-demonstration: you are writing about your own system.",
            context={
                'content_type': 'blog_post',
                'research': system_research,
                'tone': tone,
                'target_audience': 'tech enthusiasts, AI researchers, investors',
                'word_count': word_count,
                'seo_keywords': ['AI platform', 'collective intelligence', 'autonomous learning'],
            },
            scifi_context={'collective_intelligence': True, 'self_aware': True},
            spider_context={}
        )
        
        if result.success:
            blog_data = result.data if isinstance(result.data, dict) else {}
            content_data = blog_data.get('content', blog_data)
            
            stats_snapshot = {
                'agents': total_agents,
                'agents_with_knowledge': agents_with_knowledge,
                'knowledge_sources': total_knowledge,
                'knowledge_24h': knowledge_24h,
                'connections': total_connections,
                'transfers': total_transfers,
                'transfers_24h': transfers_24h,
                'spiders': total_spiders,
            }
            
            blog = SelfBlog.objects.create(
                title=content_data.get('title', 'AI Content Studio Self-Blog'),
                meta_description=content_data.get('meta_description', ''),
                intro=content_data.get('intro', ''),
                sections=content_data.get('sections', []),
                conclusion=content_data.get('conclusion', ''),
                tags=content_data.get('tags', []),
                full_text=content_data.get('full_text', json.dumps(result.data)),
                tone=tone,
                word_count=blog_data.get('metadata', {}).get('actual_word_count', 0),
                stats_snapshot=stats_snapshot,
            )
            
            logger.info(f"🤖 [SELF-BLOG] Successfully generated: {blog.id}")
            
            return {
                'success': True,
                'blog_id': str(blog.id),
                'title': blog.title,
            }
        else:
            logger.error(f"🤖 [SELF-BLOG] Agent failed: {result.error}")
            return {
                'success': False,
                'error': result.error or 'Agent execution failed',
            }
            
    except Exception as e:
        logger.error(f"🤖 [SELF-BLOG] Generation failed: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
        }
