#!/usr/bin/env python3
"""
Test a single spider to verify data collection
"""

import os
import sys
import django
import asyncio
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from ai_core.spiders.specialized.market_spider import MarketDataSpider
from ai_core.spiders.base_spider import SpiderTarget, IntelligenceData
import redis

async def test_single_spider():
    """Test the Market Data Spider with CoinGecko API"""

    print("🧪 TESTING SINGLE SPIDER: Market Data")
    print("="*50)

    # Create Redis client to monitor data
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe('intelligence:general:market_data')

    # Create spider with a simple target
    targets = [
        SpiderTarget(
            url='https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true',
            rate_limit=0.5  # 1 request per 2 seconds
        )
    ]

    subscribers = ['crypto_trader', 'day_trader']
    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}

    spider = MarketDataSpider('test_market_spider', targets, subscribers, redis_config)

    print("✅ Spider created")
    print(f"📡 Target: {targets[0].url}")
    print(f"👥 Subscribers: {subscribers}")

    # Start spider in background
    spider_task = asyncio.create_task(spider.start())

    # Monitor for data
    print("\n🔍 Monitoring for data (30 seconds)...")
    print("-"*40)

    collected_data = []
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < 30:
        # Check Redis for messages
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            data = json.loads(message['data'])
            collected_data.append(data)
            print(f"\n✅ DATA RECEIVED!")
            print(f"   Type: {data.get('data_type')}")
            print(f"   Content: {json.dumps(data.get('content', {}), indent=2)[:200]}...")
            print(f"   Quality Score: {data.get('quality_score')}")
            print(f"   Timestamp: {data.get('timestamp')}")

        # Check spider metrics
        if hasattr(spider, 'metrics'):
            metrics = spider.metrics
            if metrics.data_points_collected > 0:
                print(f"\n📊 Spider Metrics Update:")
                print(f"   Data collected: {metrics.data_points_collected}")
                print(f"   Successful requests: {metrics.successful_requests}")
                print(f"   Failed requests: {metrics.failed_requests}")

        await asyncio.sleep(1)

    # Stop spider
    await spider.stop()
    spider_task.cancel()

    print("\n" + "="*50)
    print("📈 TEST RESULTS:")
    print(f"   Total data collected: {len(collected_data)}")
    print(f"   Spider metrics: {spider.metrics.data_points_collected} data points")

    if collected_data:
        print("\n✅ SUCCESS! Spider is collecting real data!")
    else:
        print("\n⚠️  No data collected. Checking what went wrong...")
        print(f"   Failed requests: {spider.metrics.failed_requests}")
        print(f"   Rate limit hits: {spider.metrics.rate_limit_hits}")

    return len(collected_data) > 0

if __name__ == "__main__":
    print("🕷️  SINGLE SPIDER TEST")
    print("="*50)

    success = asyncio.run(test_single_spider())

    if success:
        print("\n🎉 Spider system is working! Ready to deploy all 13 spiders.")
    else:
        print("\n❌ Spider test failed. Need to debug the issue.")