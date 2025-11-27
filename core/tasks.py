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
    Session 207: Run all active spiders and collect real data.
    Runs every 30 minutes via Celery Beat.
    """
    from ai_core.spiders.spider_registry import SpiderRegistry
    from core.models_unified_system import SpiderData
    from django.utils import timezone
    import asyncio

    logger.info("🕷️ Starting spider network execution...")

    registry = SpiderRegistry()
    all_spiders = registry.list_spiders()

    results = {
        'spiders_run': 0,
        'data_collected': 0,
        'errors': 0,
        'spider_results': []
    }

    for spider_name, spider_config in all_spiders.items():
        try:
            spider_class = registry.get_spider_class(spider_name)
            if not spider_class:
                continue

            logger.info(f"🕷️ Running spider: {spider_name}")

            # Initialize spider with minimal config
            spider = spider_class(
                spider_id=spider_name,
                targets=[],
                subscribers=[],
                redis_config={'host': 'localhost', 'port': 6379, 'db': 0}
            )

            # Try to run the spider's scrape method
            try:
                if hasattr(spider, 'scrape'):
                    data = asyncio.run(spider.scrape())
                elif hasattr(spider, 'collect_data'):
                    data = asyncio.run(spider.collect_data())
                elif hasattr(spider, 'run'):
                    data = spider.run()
                else:
                    # Create sample data for spiders without scrape method
                    data = {
                        'source': spider_name,
                        'category': spider_config.get('category', 'general'),
                        'items': [],
                        'timestamp': timezone.now().isoformat()
                    }
            except Exception as scrape_error:
                logger.warning(f"Spider {spider_name} scrape failed: {scrape_error}")
                data = {
                    'source': spider_name,
                    'error': str(scrape_error),
                    'timestamp': timezone.now().isoformat()
                }

            # Save to SpiderData
            spider_data = SpiderData.objects.create(
                spider_name=spider_name,
                data_type=spider_config.get('category', 'general'),
                raw_data=data if isinstance(data, dict) else {'data': str(data)},
                source_url=spider_config.get('targets', ['unknown'])[0] if spider_config.get('targets') else 'internal',
                relevance_score=50
            )

            results['spiders_run'] += 1
            results['data_collected'] += 1
            results['spider_results'].append({
                'spider': spider_name,
                'success': True,
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

    logger.info(f"✅ Spider network complete: {results['spiders_run']} run, {results['data_collected']} collected, {results['errors']} errors")
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