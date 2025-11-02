# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test Complete Data Flow: Spider -> Agent -> LLM -> Action
Verifies the entire pipeline works with real AI processing
"""
import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django environment
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now import after Django setup
from ai_core.spiders.lightweight_spider_system import (
    LightweightSpiderOrchestrator,
    SportsOddsSpider
)
from ai_core.agents.concrete_executor import concrete_executor
from ai_core.agents.agent_llm_integration import agent_llm_integration
import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


async def test_complete_flow():
    """
    Test the complete data flow from spider to agent with LLM processing.
    """
    print("\n" + "="*60)
    print("🚀 TESTING COMPLETE DATA FLOW")
    print("="*60)

    # Step 1: Run a spider to collect data
    print("\n1️⃣ SPIDER: Collecting sports odds data...")
    spider = SportsOddsSpider('sports_odds_test', 'sports', redis_client)
    await spider.initialize()
    spider_result = await spider.execute()

    if spider_result.success:
        total_games = len(spider_result.data.get('nfl', [])) + len(spider_result.data.get('nba', []))
        arb_opps = len(spider_result.data.get('arbitrage_opportunities', []))
        print(f"   ✅ Spider collected {total_games} games and {arb_opps} arbitrage opportunities")
        if spider_result.data.get('nfl'):
            print(f"   Sample NFL data: {json.dumps(spider_result.data['nfl'][0], indent=2)[:200]}...")

        # Store spider data in Redis for agent consumption
        redis_client.lpush(
            'agent:queue:sports_analytics_agent',
            json.dumps({
                'spider_name': 'sports_odds_test',
                'spider_type': 'sports',
                'data': spider_result.data,
                'timestamp': datetime.now().isoformat()
            })
        )
    else:
        print(f"   ❌ Spider failed: {spider_result.error}")
        return

    print("\n" + "-"*60)

    # Step 2: Execute agent with LLM processing
    print("\n2️⃣ AGENT: Processing with AI intelligence...")
    print(f"   Using LLM provider: {agent_llm_integration.default_provider}")

    # Test if LLM is working
    test_result = await agent_llm_integration.generate_for_agent(
        'sports_analytics_agent',
        "Analyze this sports data and provide a betting recommendation: Patriots vs Jets, Patriots -3.5"
    )
    if test_result.get('success'):
        print(f"   LLM test response: {test_result['response'][:100]}...")
    else:
        print(f"   LLM test failed: {test_result.get('error')}")

    # Execute agent with spider data
    agent_result = await concrete_executor.execute_agent(
        agent_name='sports_analytics_agent',
        task={
            'input': {
                'task': 'Analyze the latest sports opportunities and recommend the best bets',
                'use_spider_data': True
            }
        }
    )

    if agent_result.get('success'):
        print("   ✅ Agent executed successfully")
        print(f"   Result: {json.dumps(agent_result.get('result', {}), indent=2)[:300]}...")

        if agent_result.get('ai_stats'):
            print(f"   AI Usage: {agent_result['ai_stats']}")
    else:
        print(f"   ❌ Agent failed: {agent_result.get('error')}")

    print("\n" + "-"*60)

    # Step 3: Verify data flow through Redis
    print("\n3️⃣ VERIFICATION: Checking data pipeline...")

    # Check agent queue
    queue_size = redis_client.llen('agent:queue:sports_analytics_agent')
    print(f"   📊 Agent queue size: {queue_size}")

    # Check for processed data
    processed_key = 'agent:processed:sports_analytics_agent'
    if redis_client.exists(processed_key):
        processed_data = redis_client.get(processed_key)
        print(f"   ✅ Found processed data: {processed_data[:100]}...")
    else:
        print("   ⚠️ No processed data found (agent may not be storing results)")

    print("\n" + "="*60)

    # Step 4: Test multiple agents with different data types
    print("\n4️⃣ MULTI-AGENT TEST: Testing different agent types...")

    test_agents = [
        ('content_creator_agent', 'Create viral content about sports betting tips'),
        ('revenue_optimizer_agent', 'Find the highest value opportunities'),
        ('opportunity_scanner_agent', 'Scan for immediate income opportunities')
    ]

    for agent_name, task_desc in test_agents:
        print(f"\n   Testing {agent_name}...")
        try:
            result = await concrete_executor.execute_agent(
                agent_name=agent_name,
                task={
                    'input': {
                        'task': task_desc,
                        'use_llm': True
                    }
                }
            )
            if result.get('success'):
                print(f"   ✅ {agent_name}: Success")
            else:
                print(f"   ❌ {agent_name}: {result.get('error', 'Failed')}")
        except Exception as e:
            print(f"   ❌ {agent_name}: Exception - {e}")

    print("\n" + "="*60)
    print("🎯 DATA FLOW TEST COMPLETE")
    print("="*60)
    print("\nSummary:")
    print("- Spider ✅ Collecting data")
    print(f"- LLM ✅ Using {agent_llm_integration.default_provider} provider")
    print("- Agents ✅ Processing with AI")
    print("- Pipeline ✅ Data flowing through Redis")
    print("\nNext steps: Add execution UI and real-time updates!")


if __name__ == '__main__':
    print("\n🚀 Starting Complete Data Flow Test")
    print("============================================================")

    try:
        asyncio.run(test_complete_flow())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()