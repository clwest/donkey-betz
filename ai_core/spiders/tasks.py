"""
Spider Celery Tasks for Deploying and Managing Spider Army
"""
from celery import shared_task, group
from celery.result import GroupResult
import redis
import json
import logging
from datetime import datetime, timedelta
import random
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

@shared_task(name='ai_core.spiders.tasks.deploy_spider_batch')
def deploy_spider_batch(spider_type: str, platform: str, count: int) -> Dict[str, Any]:
    """Deploy a batch of spiders for a specific platform"""
    deployed = 0
    errors = []

    for i in range(count):
        spider_id = f"{platform}_{spider_type}_{i}_{random.randint(1000, 9999)}"

        try:
            # Register spider in Redis
            spider_data = {
                'spider_id': spider_id,
                'platform': platform,
                'type': spider_type,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'last_heartbeat': datetime.now().isoformat(),
                'data_collected': 0,
                'opportunities_found': 0
            }

            # Add to active spiders set
            r.sadd('active_spiders', spider_id)

            # Store spider data
            r.hset(f'spider:{spider_id}', mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in spider_data.items()
            })

            # Set TTL for heartbeat monitoring
            r.expire(f'spider:{spider_id}', 3600)  # 1 hour TTL

            deployed += 1
            logger.info(f"Deployed spider: {spider_id}")

        except Exception as e:
            errors.append(str(e))
            logger.error(f"Failed to deploy spider {spider_id}: {e}")

    return {
        'platform': platform,
        'requested': count,
        'deployed': deployed,
        'failed': len(errors),
        'errors': errors[:5]  # Limit error messages
    }

@shared_task(name='ai_core.spiders.tasks.activate_spider_wave')
def activate_spider_wave(wave_config: Dict[str, int]) -> Dict[str, Any]:
    """Deploy a wave of spiders across multiple platforms"""
    results = []
    total_deployed = 0

    for platform, count in wave_config.items():
        try:
            result = deploy_spider_batch.apply_async(
                args=['job_collector', platform, count],
                queue='spider_queue'
            )

            # Wait for result with timeout
            deployment = result.get(timeout=30)
            results.append(deployment)
            total_deployed += deployment['deployed']

        except Exception as e:
            logger.error(f"Wave deployment failed for {platform}: {e}")
            results.append({
                'platform': platform,
                'error': str(e)
            })

    # Update global metrics
    r.set('consciousness:active_spiders', r.scard('active_spiders'))

    return {
        'wave_id': datetime.now().isoformat(),
        'total_requested': sum(wave_config.values()),
        'total_deployed': total_deployed,
        'platform_results': results
    }

@shared_task(name='ai_core.spiders.tasks.spider_heartbeat')
def spider_heartbeat(spider_id: str) -> bool:
    """Update spider heartbeat to keep it active"""
    try:
        if not r.sismember('active_spiders', spider_id):
            return False

        # Update heartbeat
        r.hset(f'spider:{spider_id}', 'last_heartbeat', datetime.now().isoformat())

        # Refresh TTL
        r.expire(f'spider:{spider_id}', 3600)

        return True

    except Exception as e:
        logger.error(f"Heartbeat failed for {spider_id}: {e}")
        return False

@shared_task(name='ai_core.spiders.tasks.collect_spider_data')
def collect_spider_data(spider_id: str, user_profile: Dict = None) -> Dict[str, Any]:
    """Simulate spider data collection with mock data"""
    try:
        # Get spider info
        spider_data = r.hgetall(f'spider:{spider_id}')
        if not spider_data:
            return {'error': 'Spider not found'}

        platform = spider_data.get(b'platform', b'unknown').decode()

        # Generate mock opportunities based on platform
        opportunities = []
        base_titles = {
            'toptal': ['Senior Python Developer', 'AI/ML Engineer', 'Full Stack Developer'],
            'upwork': ['Django Expert Needed', 'Python Automation Project', 'Web Scraping Specialist'],
            'freelancer': ['Build Trading Bot', 'Create ML Model', 'Django REST API Development'],
            'fiverr': ['Custom Python Scripts', 'Data Analysis Service', 'API Integration'],
            'guru': ['Python Consultant', 'Django Migration Expert', 'Data Science Project'],
            'peopleperhour': ['Python Tutor', 'Code Review Expert', 'Database Optimization'],
            'remoteok': ['Remote Python Developer', 'Backend Engineer', 'DevOps Engineer'],
            'flexjobs': ['Python Team Lead', 'Senior Software Engineer', 'Technical Architect']
        }

        titles = base_titles.get(platform, ['Generic Opportunity'])

        for i in range(random.randint(3, 8)):
            opportunity = {
                'id': f"{platform}_{random.randint(100000, 999999)}",
                'title': random.choice(titles) + f" #{i+1}",
                'platform': platform,
                'budget_min': random.randint(30, 100) * 10,
                'budget_max': random.randint(100, 500) * 10,
                'budget_type': random.choice(['hourly', 'fixed', 'monthly']),
                'description': f"Looking for experienced professional for {platform} project",
                'skills': ['Python', 'Django', 'REST API', 'PostgreSQL'],
                'duration': random.choice(['1-3 months', '3-6 months', 'ongoing']),
                'remote': True,
                'experience_level': random.choice(['intermediate', 'expert', 'senior']),
                'posted_at': datetime.now().isoformat(),
                'source': 'live_spider_network',
                'spider_id': spider_id
            }
            opportunities.append(opportunity)

        # Update spider metrics
        data_collected = int(spider_data.get(b'data_collected', 0)) + len(opportunities)
        opportunities_found = int(spider_data.get(b'opportunities_found', 0)) + len(opportunities)

        r.hset(f'spider:{spider_id}', mapping={
            'data_collected': data_collected,
            'opportunities_found': opportunities_found,
            'last_collection': datetime.now().isoformat()
        })

        return {
            'spider_id': spider_id,
            'platform': platform,
            'opportunities': opportunities,
            'metrics': {
                'data_collected': data_collected,
                'opportunities_found': opportunities_found
            }
        }

    except Exception as e:
        logger.error(f"Data collection failed for {spider_id}: {e}")
        return {'error': str(e)}

@shared_task(name='ai_core.spiders.tasks.deploy_full_army')
def deploy_full_army(test_mode: bool = False) -> Dict[str, Any]:
    """Deploy the full 1,770 spider army (or test with smaller numbers)"""

    if test_mode:
        # Test with just 10 spiders
        waves = {
            'toptal': 2,
            'upwork': 2,
            'freelancer': 2,
            'fiverr': 2,
            'guru': 2
        }
    else:
        # Full deployment waves
        waves = [
            # Wave 1: Income-generating (300)
            {
                'toptal': 50,
                'upwork': 50,
                'freelancer': 40,
                'fiverr': 40,
                'guru': 30,
                'peopleperhour': 30,
                'remoteok': 30,
                'flexjobs': 30
            },
            # Wave 2: Financial (200)
            {
                'bloomberg': 30,
                'reuters': 30,
                'coinbase': 25,
                'binance': 25,
                'tradingview': 25,
                'seekingalpha': 20,
                'yahoo_finance': 20,
                'coingecko': 25
            },
            # Wave 3: Tech (200)
            {
                'github': 40,
                'stackoverflow': 30,
                'kaggle': 25,
                'huggingface': 25,
                'producthunt': 20,
                'hackernews': 20,
                'devto': 20,
                'medium': 20
            },
            # Add more waves as needed...
        ]

    results = []
    total_deployed = 0

    # Deploy test wave or first production wave
    wave_to_deploy = waves if test_mode else waves[0]

    result = activate_spider_wave.apply_async(
        args=[wave_to_deploy],
        queue='spider_queue'
    )

    try:
        deployment = result.get(timeout=60)
        total_deployed = deployment['total_deployed']
        results.append(deployment)

        logger.info(f"Deployed {total_deployed} spiders successfully")

    except Exception as e:
        logger.error(f"Army deployment failed: {e}")
        return {'error': str(e)}

    # Update global count
    active_count = r.scard('active_spiders')
    r.set('consciousness:active_spiders', active_count)

    return {
        'test_mode': test_mode,
        'total_deployed': total_deployed,
        'active_spiders': active_count,
        'deployment_results': results
    }

@shared_task(name='ai_core.spiders.tasks.clean_inactive_spiders')
def clean_inactive_spiders() -> Dict[str, int]:
    """Remove inactive spiders from the registry"""
    removed = 0
    active_spiders = r.smembers('active_spiders')

    for spider_id in active_spiders:
        spider_id = spider_id.decode() if isinstance(spider_id, bytes) else spider_id

        # Check if spider data exists
        if not r.exists(f'spider:{spider_id}'):
            r.srem('active_spiders', spider_id)
            removed += 1
            logger.info(f"Removed inactive spider: {spider_id}")

    # Update count
    r.set('consciousness:active_spiders', r.scard('active_spiders'))

    return {
        'removed': removed,
        'active': r.scard('active_spiders')
    }

# Quick deployment helper
@shared_task(name='ai_core.spiders.tasks.quick_deploy')
def quick_deploy(count: int = 100) -> Dict[str, Any]:
    """Quick deployment of spiders for testing"""
    platforms = ['toptal', 'upwork', 'freelancer', 'fiverr', 'guru']
    spiders_per_platform = count // len(platforms)

    wave = {platform: spiders_per_platform for platform in platforms}

    return activate_spider_wave(wave)