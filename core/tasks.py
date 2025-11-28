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
                # Check if student already has similar knowledge
                student_has_similar = AgentKnowledgeSource.objects.filter(
                    agent=student,
                    title__icontains=knowledge.title.split()[0] if knowledge.title else '',
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

        # Publish to Redis
        r.publish('agent_learning', json.dumps({
            'type': 'status_update',
            'data': stats
        }))

        # Cache for API access
        r.setex('agent_learning:status', 300, json.dumps(stats))

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

        # Conversation types with their prompts
        conversation_templates = [
            {
                'type': 'knowledge_sharing',
                'starter': "I've been analyzing {topic} and noticed something interesting...",
                'responder': "That's a great observation. In my experience with {specialty}..."
            },
            {
                'type': 'question_answer',
                'starter': "I have a question about {topic} - how do you approach this?",
                'responder': "Based on my expertise in {specialty}, I'd suggest..."
            },
            {
                'type': 'brainstorm',
                'starter': "Let's brainstorm ideas for {topic}. What if we considered...",
                'responder': "Building on that idea, we could also..."
            },
            {
                'type': 'debate',
                'starter': "I think {topic} could be approached differently. Here's my view...",
                'responder': "Interesting perspective. However, from my angle..."
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

                # Create the prompt for the current speaker
                system_prompt = f"""You are {current_speaker.name}, an AI agent specialized in {current_speaker.specialization or 'general knowledge'}.
You are having a professional discussion with {other_speaker.name} about: {topic}

Your knowledge context: {knowledge_item.summary[:500] if knowledge_item.summary else 'No specific context'}

Guidelines:
- Keep responses concise (2-3 sentences)
- Be insightful and add value to the discussion
- Reference your specialization when relevant
- If this is a later message, build on what was said before
- Be collaborative and constructive"""

                # Build message history for context
                history = []
                for prev_msg in messages[-4:]:  # Last 4 messages for context
                    history.append({
                        "role": "user" if prev_msg['agent'] != current_speaker.name else "assistant",
                        "content": f"{prev_msg['agent']}: {prev_msg['content']}"
                    })

                # Generate the message
                if msg_num == 0:
                    user_content = f"Start a {template['type'].replace('_', ' ')} discussion about {topic}. Be the first to speak."
                else:
                    user_content = f"Continue the conversation. The last message was from {other_speaker.name}. Respond appropriately."

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *history,
                            {"role": "user", "content": user_content}
                        ],
                        max_tokens=150,
                        temperature=0.8
                    )

                    content = response.choices[0].message.content.strip()

                    # Clean up the content (remove agent name prefix if present)
                    if content.startswith(f"{current_speaker.name}:"):
                        content = content[len(current_speaker.name)+1:].strip()

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
                    conclusion_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Summarize the key insights from this agent discussion in 1-2 sentences."},
                            {"role": "user", "content": f"Discussion between {initiator.name} and {responder.name} about {topic}:\n\n" +
                                "\n".join([f"{m['agent']}: {m['content']}" for m in messages])}
                        ],
                        max_tokens=100
                    )
                    conclusion = conclusion_response.choices[0].message.content.strip()
                except:
                    conclusion = f"Productive discussion about {topic}"

                conversation.conclude(
                    conclusion,
                    insights=[m['content'] for m in messages if m['type'] == 'insight']
                )
                conversation.quality_score = min(1.0, len(messages) / max_messages * 0.8 + 0.2)
                conversation.save()

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
            started_at__gte=recent_cutoff
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

            for _ in range(dreams_per_agent):
                # Pick a random knowledge item as inspiration
                knowledge = random.choice(list(knowledge_items))
                topic = knowledge.title or knowledge.source_type or "general insights"

                # Pick a random dream type
                template = random.choice(dream_templates)
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
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=200,
                        temperature=0.95  # High temperature for creative dreams
                    )

                    dream_content = response.choices[0].message.content.strip()

                    # Clean up the content
                    # Remove any repeated prefixes
                    for prefix in [template['prefix'], f"{agent.name}:", "Dream:", "Idea:"]:
                        if dream_content.startswith(prefix):
                            dream_content = dream_content[len(prefix):].strip()

                    # Generate a catchy title
                    title_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Generate a short, catchy title (3-7 words) for this creative thought. No quotes or punctuation."},
                            {"role": "user", "content": dream_content}
                        ],
                        max_tokens=20,
                        temperature=0.7
                    )

                    title = title_response.choices[0].message.content.strip().strip('"\'')[:200]

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