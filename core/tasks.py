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
                spider_class = registry.get_spider(spider_name)
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
@shared_task
def collect_spider_data():
    """Collect spider data every 15 minutes - called by Celery Beat"""
    from core.models_unified_system import SpiderData
    from intelligence.spider_agent_connector import SpiderAgentConnector
    import random
    from django.utils import timezone

    logger.info("Starting automated spider data collection...")

    # Simulate spider data collection
    spider_types = [
        'Job Opportunity Spider',
        'Finance Monitor Spider',
        'Content Discovery Spider',
        'Market Intelligence Spider',
        'Lead Generation Spider',
        'Research Paper Spider',
        'Investment Tracker Spider'
    ]

    data_types = [
        'job_posting', 'market_data', 'content_opportunity',
        'research_paper', 'lead', 'financial_metric', 'investment'
    ]

    # Create 5-10 new spider data items
    num_items = random.randint(5, 10)
    created_items = []

    for i in range(num_items):
        spider_name = random.choice(spider_types)
        data_type = random.choice(data_types)

        spider_data = SpiderData.objects.create(
            spider_name=spider_name,
            data_type=data_type,
            raw_data={
                'title': f'Auto-collected {data_type} #{SpiderData.objects.count() + i}',
                'description': f'Automated collection from {spider_name}',
                'value': random.randint(100, 10000),
                'timestamp': timezone.now().isoformat()
            },
            source_url=f'https://example.com/{data_type}/{i}'
        )
        created_items.append(spider_data)

    # Process the spider data through agents
    try:
        connector = SpiderAgentConnector()
        for item in created_items:
            try:
                connector.process_spider_data(item)
            except Exception as e:
                logger.error(f"Error processing spider data {item.id}: {e}")
    except Exception as e:
        logger.error(f"Error initializing connector: {e}")

    logger.info(f"Collected and processed {len(created_items)} spider data items")
    return f"Collected {len(created_items)} items"

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
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from ai_core.spiders.real_data_collector import collect_spider_data_sync, SPIDER_TARGET_URLS
    from core.models_unified_system import SpiderData
    from django.utils import timezone

    logger.info("🕷️ Starting spider network execution with REAL data collection...")

    registry = SpiderRegistry()
    all_spiders = registry.list_spiders()

    results = {
        'spiders_run': 0,
        'data_collected': 0,
        'items_collected': 0,
        'errors': 0,
        'spider_results': []
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

        except Exception as e:
            logger.error(f"❌ Spider {spider_name} failed: {e}")
            results['errors'] += 1
            results['spider_results'].append({
                'spider': spider_name,
                'success': False,
                'error': str(e)
            })

    logger.info(f"✅ Spider network complete: {results['spiders_run']} run, {results['items_collected']} items collected, {results['errors']} errors")
    return results


@shared_task
def backfill_spider_embeddings(batch_size: int = 100):
    """
    Session 293: Generate embeddings for SpiderData entries that don't have them.

    Runs every 10 minutes via Celery Beat to gradually build embedding coverage.
    Uses the SpiderSemanticSearch service.
    """
    logger.info("🧠 Starting spider embedding backfill...")

    try:
        from core.services.spider_semantic_search import get_spider_semantic_search

        search = get_spider_semantic_search()
        stats = search.backfill_embeddings(batch_size=batch_size, hours=168)  # Last 7 days

        logger.info(
            f"✅ Embedding backfill complete: "
            f"{stats['processed']} processed, {stats['succeeded']} succeeded, "
            f"{stats['failed']} failed, {stats['skipped']} skipped"
        )

        # Get current coverage stats
        coverage = search.get_embedding_stats()
        logger.info(f"📊 Embedding coverage: {coverage['coverage_percent']:.1f}% ({coverage['with_embedding']}/{coverage['total_entries']})")

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
    """
    from core.models_unified_system import SpiderData
    from django.utils import timezone

    logger.info(f"🕷️ On-demand execution: {spider_name}")

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

        logger.info(f"✅ Spider {spider_name} executed successfully, saved as SpiderData {spider_data.id}")
        return {
            'success': True,
            'spider_name': spider_name,
            'data_id': str(spider_data.id),
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
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
        from agents.opportunity_scoring_agent import OpportunityScoringAgent

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
            teacher_knowledge = AgentKnowledgeSource.objects.filter(
                agent=teacher,
                is_active=True,
                knowledge_type__in=connection.shareable_knowledge_types or ['trend', 'market', 'opportunity']
            ).order_by('-confidence_score', '-last_updated_at')[:5]

            for knowledge in teacher_knowledge:
                # Session 322: Check if student already has this exact knowledge
                # Use first 30 chars of title for better matching (was just first word which was too crude)
                title_prefix = knowledge.title[:30] if knowledge.title else ''
                student_has_similar = AgentKnowledgeSource.objects.filter(
                    agent=student,
                    title__icontains=title_prefix,
                    knowledge_type=knowledge.knowledge_type
                ).exists()

                if not student_has_similar:
                    # Create knowledge transfer record
                    usefulness = random.uniform(0.6, 1.0)  # Simulate usefulness

                    transfer = KnowledgeTransfer.objects.create(
                        connection=connection,
                        source_knowledge=knowledge,
                        transfer_summary=f"{teacher.name} shared '{knowledge.title[:50]}' with {student.name}",
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
                        title=f"[Learned] {knowledge.title}",
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
                f"Key Insights: {', '.join(item.key_insights) if item.key_insights else 'No insights'}",
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
                f"Key Insights: {', '.join(synthesis.key_insights) if synthesis.key_insights else 'No insights'}",
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
        # Get agents that have knowledge
        agents_with_knowledge = Agent.objects.filter(
            is_active=True,
            knowledge_sources__isnull=False
        ).distinct()[:20]

        if agents_with_knowledge.count() < 2:
            logger.warning("💬 [CONVERSATIONS] Need at least 2 agents with knowledge")
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
            # Pick two random agents with learning connections
            agents_list = list(agents_with_knowledge)
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

            # Get a knowledge item to discuss
            initiator_knowledge = AgentKnowledgeSource.objects.filter(
                agent=initiator
            ).order_by('-last_updated_at')[:10]

            if not initiator_knowledge.exists():
                continue

            knowledge_item = random.choice(list(initiator_knowledge))
            topic = knowledge_item.title or "recent insights"

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

                # Create the prompt for the current speaker
                system_prompt = f"""You are {current_speaker.name}, an AI agent specialized in {current_speaker.specialization or 'general knowledge'}.
You are having a {template['type'].replace('_', ' ')} with {other_speaker.name} about: {topic}

Your knowledge context: {knowledge_item.summary[:500] if knowledge_item.summary else 'No specific context'}

{behavior_guide}

Conversation dynamic: {dynamic}

Guidelines:
- Keep responses concise (2-3 sentences)
- Be authentic to YOUR expertise - don't just defer to theirs
- If you see a problem with their approach, say so
- Ask probing questions, don't just accept statements
- Real experts disagree sometimes - that's healthy
{policy_context}
{spider_context}"""

                # Build message history for context
                history = []
                for prev_msg in messages[-4:]:  # Last 4 messages for context
                    history.append({
                        "role": "user" if prev_msg['agent'] != current_speaker.name else "assistant",
                        "content": f"{prev_msg['agent']}: {prev_msg['content']}"
                    })

                # Generate the message with dynamic-appropriate prompts
                if msg_num == 0:
                    user_content = f"Start a {template['type'].replace('_', ' ')} about {topic}. Be the first to speak and set the tone."
                else:
                    last_msg = messages[-1]['content'] if messages else ''
                    if tension == 'high':
                        user_content = f"Respond to {other_speaker.name}. Challenge their point or defend your position. Don't just agree - push back if you see issues."
                    else:
                        user_content = f"Respond to {other_speaker.name}. Build on the discussion but don't hesitate to question or offer alternative perspectives."

                try:
                    # Use chat.completions for gpt-5-mini with high max_completion_tokens
                    # GPT-5 reasoning models use tokens for internal reasoning first,
                    # so we need ~500+ tokens to ensure room for reasoning + actual output
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        max_completion_tokens=800,  # Higher for GPT-5 reasoning models
                    )

                    content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    # Clean up the content (remove agent name prefix if present)
                    if content.startswith(f"{current_speaker.name}:"):
                        content = content[len(current_speaker.name)+1:].strip()

                    # Session 321: Skip empty messages - don't save if content is empty
                    if not content:
                        logger.warning(f"💬 [CONVERSATIONS] Empty content from {current_speaker.name}, skipping message {msg_num + 1}")
                        # Still swap speakers to continue conversation
                        current_speaker, other_speaker = other_speaker, current_speaker
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
                    # GPT-5 reasoning models need higher token limits for reasoning + output
                    conclusion_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Summarize the key insights from this agent discussion in 1-2 sentences."},
                            {"role": "user", "content": f"Discussion between {initiator.name} and {responder.name} about {topic}:\n\n" +
                                "\n".join([f"{m['agent']}: {m['content']}" for m in messages])}
                        ],
                        max_completion_tokens=400,
                    )
                    conclusion = conclusion_response.choices[0].message.content.strip() if conclusion_response.choices[0].message.content else f"Productive discussion about {topic}"
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
    from core.models_unified_system import (
        PartnershipProject, BusinessResearchResult
    )
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
        project_context_parts = [f"Project: {project.project_name or project.name}"]
        if project.business_type:
            project_context_parts.append(f"Business Type: {project.business_type}")
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
            except:
                conclusion = f"Productive discussion about {topic}"

            conversation.conclude(
                conclusion,
                insights=[m['content'] for m in messages if m['type'] == 'insight']
            )
            conversation.quality_score = min(1.0, len(messages) / max_messages * 0.8 + 0.2)
            conversation.message_count = len(messages)
            conversation.save()

        # Broadcast update via WebSocket
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

        # Find idle agents with knowledge (so they have something to dream about)
        idle_agents = Agent.objects.filter(
            is_active=True,
            knowledge_sources__isnull=False
        ).exclude(
            id__in=recently_active_ids
        ).distinct()[:max_dreamers]

        if not idle_agents.exists():
            logger.info("💭 [DREAMS] No idle agents with knowledge found")
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
            # Get agent's recent knowledge for inspiration
            knowledge_items = AgentKnowledgeSource.objects.filter(
                agent=agent
            ).order_by('-last_updated_at')[:10]

            if not knowledge_items.exists():
                continue

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
                # Pick a random knowledge item as inspiration
                # Session 249: Prefer topics that users have reacted positively to
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
                system_prompt = f"""You are {agent.name}, an AI agent specialized in {agent.specialization or 'creative thinking'}.
You are in a relaxed, creative state - dreaming up new ideas while idle.

Your background knowledge: {knowledge.summary[:500] if knowledge.summary else 'Various insights and learnings'}

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
                    # Need 1000+ tokens to ensure room for both (like Session 315 fix)
                    response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_completion_tokens=1000,  # Higher for GPT-5 reasoning (Session 317)
                    )

                    dream_content = response.choices[0].message.content.strip() if response.choices[0].message.content else ""

                    # Clean up the content
                    # Remove any repeated prefixes
                    for prefix in [template['prefix'], f"{agent.name}:", "Dream:", "Idea:"]:
                        if dream_content.startswith(prefix):
                            dream_content = dream_content[len(prefix):].strip()

                    # Session 317: Generate catchy title with adequate tokens for reasoning
                    title_response = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=[
                            {"role": "system", "content": "Generate a short, catchy title (3-7 words) for this creative thought. No quotes or punctuation."},
                            {"role": "user", "content": dream_content if dream_content else "Creative thinking session"}
                        ],
                        max_completion_tokens=500,  # Higher for GPT-5 reasoning (Session 317)
                    )

                    title = title_response.choices[0].message.content.strip().strip('"\'')[:200] if title_response.choices[0].message.content else "Creative Thought"

                    # Create the dream
                    AgentDream.objects.create(
                        agent=agent,
                        title=title,
                        content=dream_content,
                        dream_type=dream_type,
                        inspiration_source=topic[:200],
                        related_topics=[topic, agent.specialization or 'general'],
                        vividness_score=random.uniform(0.6, 1.0),
                        creativity_score=random.uniform(0.6, 1.0)
                    )

                    stats['dreams_generated'] += 1
                    logger.debug(f"💭 [DREAMS] {agent.name} dreamed: {title}")

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
                'agent_avatar': dream.agent.avatar_url if dream.agent else None,
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
