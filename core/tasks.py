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


@shared_task
def run_spider_by_category(category: str):
    """
    Run spiders for a specific category.

    Session 265 Phase 6: Used by autonomy engine for spider dispatch.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry

    try:
        registry = SpiderRegistry()
        spiders = registry.get_spiders_by_category(category)

        results = []
        for spider_name in spiders[:3]:  # Limit to 3 spiders per category
            try:
                spider_class = registry.get_spider_class(spider_name)
                if spider_class:
                    spider = spider_class()
                    data = spider.fetch()
                    results.append({
                        'spider': spider_name,
                        'items': len(data) if data else 0,
                    })
            except Exception as spider_error:
                logger.debug(f"Spider {spider_name} failed: {spider_error}")

        logger.info(f"Ran {len(results)} spiders for category {category}")
        return {'category': category, 'results': results}

    except Exception as e:
        logger.error(f"Spider dispatch failed for {category}: {e}")
        return {'error': str(e)}

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


@shared_task
def run_spider_network():
    """
    Session 207/221: Run all active spiders and collect REAL data.
    Runs every 30 minutes via Celery Beat.

    Session 221 Enhancement: Uses real_data_collector for actual web scraping.
    Session 423: Added Discord notifications for spider activity.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from ai_core.spiders.real_data_collector import collect_spider_data_sync, SPIDER_TARGET_URLS
    from core.models_unified_system import SpiderData
    from django.utils import timezone

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
        try:
            logger.info(f"🕷️ Running spider: {spider_name}")

            # Session 221: Use real data collector for spiders with configured URLs
            if spider_name in SPIDER_TARGET_URLS:
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
                        # Try spider methods
                        if hasattr(spider, 'scrape'):
                            import asyncio
                            data = asyncio.run(spider.scrape())
                        elif hasattr(spider, 'collect_data'):
                            import asyncio
                            data = asyncio.run(spider.collect_data())
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

        except Exception as e:
            logger.error(f"❌ Spider {spider_name} failed: {e}")
            results['errors'] += 1
            results['spider_results'].append({
                'spider': spider_name,
                'success': False,
                'error': str(e)
            })

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
def execute_single_spider(spider_name: str):
    """
    Session 207: Execute a single spider on-demand.
    Called by the Execute button in the Spider Dashboard.

    Uses lightweight synchronous data collection to avoid macOS fork/async issues.
    Does NOT import SpiderRegistry to avoid aiohttp/fork segfaults.
    Session 423: Added Discord notifications for individual spider runs.
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
    elif spider_name in ['courtlistener', 'justia', 'findlaw', 'lii']:
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
    """Process distribution to Gumroad."""
    account = distribution.platform_account

    if not account.access_token:
        return {'success': False, 'error': 'No Gumroad access token. Please reconnect.'}

    try:
        import requests as http_requests

        product_data = {
            'access_token': account.access_token,
            'name': distribution.title,
            'description': distribution.description or distribution.title,
            'price': int(float(distribution.price or 9.99) * 100),  # Cents
        }

        response = http_requests.post(
            'https://api.gumroad.com/v2/products',
            data=product_data
        )

        if response.status_code in [200, 201]:
            result = response.json()
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
                'error': f'Gumroad API error: {response.status_code}'
            }

    except Exception as e:
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
        Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer
    )

    logger.info("🧠 [LEARNING] Starting autonomous agent learning cycle...")

    try:
        # Get active learning connections
        connections = AgentLearningConnection.objects.filter(
            is_active=True
        ).select_related('teacher_agent', 'student_agent').order_by('?')[:10]  # Random 10

        transfers_made = 0
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

                # Knowledge is new - proceed with transfer
                # Session 350: Strip existing [Learned] prefixes to prevent accumulation
                import re
                clean_title = re.sub(r'^\[Learned\]\s*', '', knowledge.title).strip()
                # Also strip from beginning multiple times in case of nested
                while clean_title.startswith('[Learned]'):
                    clean_title = clean_title[9:].strip()

                # Create knowledge transfer record
                usefulness = random.uniform(0.6, 1.0)  # Simulate usefulness

                transfer = KnowledgeTransfer.objects.create(
                    connection=connection,
                    source_knowledge=knowledge,
                    transfer_summary=f"{teacher.name} shared '{clean_title[:50]}' with {student.name}",
                    key_points=knowledge.key_insights[:3] if knowledge.key_insights else [],
                    was_useful=usefulness > 0.7,
                    usefulness_score=usefulness,
                    was_applied=random.random() > 0.3,  # 70% chance of being applied
                )

                # Create new knowledge for student (adapted from teacher's)
                new_knowledge = AgentKnowledgeSource.objects.create(
                    agent=student,
                    knowledge_type=knowledge.knowledge_type,
                    spider_category=knowledge.spider_category,
                    source_spider_names=knowledge.source_spider_names + [f'learned_from_{teacher.name}'],
                    title=f"[Learned] {clean_title}",
                    summary=f"Learned from {teacher.name}: {knowledge.summary[:200]}",
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

        logger.info(
            f"🧠 [LEARNING] Cycle complete: {transfers_made} knowledge transfers made "
            f"across {len(connections)} connections"
        )

        return {
            'status': 'success',
            'transfers_made': transfers_made,
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
            knowledge_item = None
            if initiator_knowledge.exists():
                knowledge_item = random.choice(list(initiator_knowledge))
                topic = knowledge_item.title or "recent insights"
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
            topic = knowledge_item.title or "recent insights"

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
                    topic = knowledge.title or knowledge.source_type or "general insights"
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
