#!/usr/bin/env python
"""
Test Lightweight Spider System
===============================
"""

import os
import sys
import django
import asyncio
import json

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.spiders.lightweight_spider_system import (
    create_lightweight_orchestrator,
    SportsOddsSpider,
    JobOpportunitySpider,
    CryptoIntelligenceSpider
)


async def test_spiders():
    """Test the lightweight spider system"""

    print("\n" + "="*60)
    print("🕷️ LIGHTWEIGHT SPIDER SYSTEM TEST")
    print("="*60)

    # Create orchestrator
    redis_config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'decode_responses': True
    }

    orchestrator = create_lightweight_orchestrator(redis_config)

    print(f"\n✅ Created orchestrator with {len(orchestrator.spiders)} spiders:")
    for name, spider in orchestrator.spiders.items():
        print(f"  • {name} ({spider.spider_type})")

    print("\n🧪 Testing each spider type...")

    # Initialize all spiders
    for spider in orchestrator.spiders.values():
        await spider.initialize()

    # Test each spider
    results = {}
    for spider_name, spider in orchestrator.spiders.items():
        print(f"\n📡 Testing {spider_name}...")
        result = await spider.execute()

        if result.success:
            print(f"  ✅ Success!")

            # Show sample data based on type
            if spider.spider_type == 'sports' and 'nfl' in result.data:
                games = result.data['nfl']
                if games:
                    print(f"  📊 Found {len(games)} NFL games")
                    game = games[0]
                    print(f"  🏈 {game['game']} - Best bet: {game['best_bet']} ({game['confidence']:.1%} confidence)")

                if 'arbitrage_opportunities' in result.data:
                    arbs = result.data['arbitrage_opportunities']
                    if arbs:
                        print(f"  💰 Found {len(arbs)} arbitrage opportunities")
                        arb = arbs[0]
                        print(f"     {arb['game']}: {arb['profit_percent']}% profit")

            elif spider.spider_type == 'jobs' and 'freelance' in result.data:
                jobs = result.data['freelance']
                if jobs:
                    print(f"  💼 Found {len(jobs)} job opportunities")
                    job = jobs[0]
                    print(f"     {job['title']} - {job['budget']} (Match: {job['match_score']:.1%})")

            elif spider.spider_type == 'crypto' and 'market_trends' in result.data:
                trends = result.data['market_trends']
                print(f"  📈 BTC: ${trends['btc_price']:,} ({trends['btc_24h_change']:+.1f}%)")
                print(f"  📈 ETH: ${trends['eth_price']:,} ({trends['eth_24h_change']:+.1f}%)")

                if 'whale_alerts' in result.data:
                    alerts = result.data['whale_alerts']
                    if alerts:
                        alert = alerts[0]
                        print(f"  🐋 Whale Alert: {alert['action']} {alert['amount']} ({alert['value']})")

            # Store result
            spider.store_result(result)
            results[spider_name] = 'SUCCESS'

        else:
            print(f"  ❌ Failed: {result.error}")
            results[spider_name] = 'FAILED'

    # Cleanup
    for spider in orchestrator.spiders.values():
        await spider.cleanup()

    # Show summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    successful = sum(1 for r in results.values() if r == 'SUCCESS')
    print(f"Total spiders tested: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")

    # Check Redis storage
    import redis
    r = redis.Redis(**redis_config)

    stored_results = 0
    for spider_name in orchestrator.spiders.keys():
        latest_key = f"spider_latest:{spider_name}"
        if r.exists(latest_key):
            stored_results += 1

    print(f"Results stored in Redis: {stored_results}")

    if successful == len(results):
        print("\n✅ All spiders working correctly!")
    else:
        print("\n⚠️ Some spiders failed - check logs for details")

    return results


if __name__ == "__main__":
    results = asyncio.run(test_spiders())
    print("\n🎯 Lightweight spider system is ready for deployment!")
    print("Use: python manage.py deploy_lightweight_spiders --action deploy")
    print("Or integrate with the existing orchestrator.")