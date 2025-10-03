"""
Ultra-Simple Spider Deployment
===============================
Just register spiders in Redis, don't try to actually run them yet.
"""

import os
import sys
import django
import redis
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from ai_core.spiders.spider_registry import spider_registry

def deploy_spiders():
    print("=" * 70)
    print("🕷️  SIMPLE SPIDER DEPLOYMENT (Redis Registration Only)")
    print("=" * 70)

    # Connect to Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Clear previous
    print("\n🧹 Clearing previous spider registrations...")
    for key in redis_client.scan_iter("spider:*"):
        redis_client.delete(key)
    redis_client.delete('active_spiders')

    # Get available spiders
    available_spiders = spider_registry.get_active_spiders()
    print(f"\n📋 Found {len(available_spiders)} spider types available:")
    for name in available_spiders.keys():
        print(f"   • {name}")

    # Simple deployment plan - use what we have
    deployment_plan = {
        'toptal': 100,
        'guru': 100,
        'peopleperhour': 100,
        'ninetyninedesigns': 100,
        'flexjobs': 100,
        'remoteok': 100,
        'financial': 200,
        'market_data': 100,
        'innovation': 150,
        'social_sentiment': 150,
        'news_harvester': 150,
        'medium': 100,
        'gumroad': 100,
    }

    total = sum(deployment_plan.values())
    print(f"\n📊 Deploying {total} spider registrations across {len(deployment_plan)} types\n")

    deployed = 0

    for spider_type, count in deployment_plan.items():
        if spider_type not in available_spiders:
            print(f"  ⚠️  Skipping {spider_type} (not found)")
            continue

        print(f"  📡 Registering {count} x {spider_type}...", end=" ")

        for i in range(count):
            spider_id = f"{spider_type}_{i+1:04d}"

            spider_data = {
                'id': spider_id,
                'type': spider_type,
                'status': 'registered',
                'deployed_at': datetime.utcnow().isoformat(),
                'platform': spider_type
            }

            redis_client.hset(f'spider:{spider_id}', mapping=spider_data)
            redis_client.sadd('active_spiders', spider_id)
            deployed += 1

        print(f"✅")

    print(f"\n" + "=" * 70)
    print(f"✅  Successfully registered {deployed} spiders in Redis")
    print(f"   Total active: {redis_client.scard('active_spiders')}")
    print("=" * 70)

    # Show sample
    print("\n📋 Sample registered spiders:")
    sample_spiders = list(redis_client.smembers('active_spiders'))[:10]
    for spider_id in sample_spiders:
        spider_id = spider_id.decode() if isinstance(spider_id, bytes) else spider_id
        data = redis_client.hgetall(f'spider:{spider_id}')
        if data:
            spider_type = data.get(b'type', b'unknown').decode()
            status = data.get(b'status', b'unknown').decode()
            print(f"   • {spider_id} (type: {spider_type}, status: {status})")

    print(f"\n✨ Spider registrations complete!")
    print(f"💡 Note: Spiders are registered but not actively crawling yet.")
    print(f"   To enable crawling, you would need to start the spider worker processes.")

if __name__ == '__main__':
    deploy_spiders()
