"""
Celery Background Tasks for Unified Donkey Betz Platform
Handles long-running operations like document isolation in the background
"""

from celery import shared_task
import logging
import time
from datetime import datetime
from django.db import transaction
from typing import Dict, Any
import os

logger = logging.getLogger(__name__)

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