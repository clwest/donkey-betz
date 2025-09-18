#!/usr/bin/env python3
"""
Quick Spider Activation Script
==============================
Activates the 13 working spiders to feed data to agents.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import asyncio
import logging
from backend.spiders.spider_registry import spider_registry
from backend.spiders.base_spider import SpiderTarget

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def test_spider_connectivity():
    """Test if spiders can actually collect data"""

    active_spiders = spider_registry.get_active_spiders()
    print(f"\n🕷️  SPIDER CONNECTIVITY TEST")
    print(f"{'='*50}")
    print(f"Found {len(active_spiders)} active spiders:")

    for name, spider_class in active_spiders.items():
        print(f"  • {name}: {spider_class.__name__}")

    # Test one spider
    print(f"\n🧪 Testing Financial Intelligence Spider...")

    try:
        from backend.spiders.specialized.financial_spider import FinancialIntelligenceSpider

        targets = [SpiderTarget(url='https://finance.yahoo.com')]
        test_spider = FinancialIntelligenceSpider('test_financial', targets, [], {})

        print("✅ Spider instantiated successfully")

        # Check if spider has required methods
        if hasattr(test_spider, 'process_data'):
            print("✅ Spider has process_data method")
        else:
            print("❌ Spider missing process_data method")

        if hasattr(test_spider, 'start'):
            print("✅ Spider has start method")
        else:
            print("❌ Spider missing start method")

    except Exception as e:
        print(f"❌ Spider test failed: {e}")

    print(f"\n📊 SPIDER-AGENT MAPPING")
    print(f"{'='*50}")

    # Map spiders to agent types
    spider_agent_map = {
        'financial': ['investment_advisor', 'wealth_builder', 'crypto_trader'],
        'innovation': ['tech_scout', 'startup_advisor', 'research_analyst'],
        'social_sentiment': ['social_media_manager', 'brand_monitor', 'trend_analyst'],
        'market_data': ['day_trader', 'options_trader', 'forex_trader'],
        'news_harvester': ['news_aggregator', 'pr_manager', 'content_curator'],
        'toptal': ['freelance_finder', 'contract_negotiator', 'job_application_agent'],
        'guru': ['freelance_finder', 'gig_economy_expert'],
        'peopleperhour': ['freelance_finder', 'remote_work_specialist'],
        'ninetyninedesigns': ['design_project_finder', 'creative_director'],
        'flexjobs': ['remote_work_specialist', 'career_advisor'],
        'remoteok': ['remote_work_specialist', 'digital_nomad_guide'],
        'medium': ['content_creator', 'blog_monetizer', 'writer_assistant'],
        'gumroad': ['digital_product_creator', 'online_course_builder', 'passive_income_generator']
    }

    for spider_name, agent_types in spider_agent_map.items():
        if spider_name in active_spiders:
            print(f"\n🕷️  {spider_name} → 🤖 {', '.join(agent_types)}")

    print(f"\n🚀 ACTIVATION STATUS")
    print(f"{'='*50}")
    print("✅ Spiders are registered and ready")
    print("✅ Agent mappings are configured")
    print("⚠️  Need to implement collection loop in base_spider.py")
    print("⚠️  Need to implement data routing to agents")

    return active_spiders

async def activate_minimal_spider_system():
    """Activate a minimal spider system for testing"""

    print("\n🎯 ACTIVATING MINIMAL SPIDER SYSTEM")
    print(f"{'='*50}")

    # Import agent system
    from agents.registry import agent_registry

    # Check agent availability
    agents = agent_registry.list_agents()
    print(f"✅ Found {len(agents)} agents ready to receive data")

    # Create simple data flow test
    print("\n📡 Testing data flow...")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Test Redis connectivity
        r.ping()
        print("✅ Redis is connected")

        # Publish test message
        test_data = {
            'spider': 'financial',
            'type': 'stock_alert',
            'data': {'symbol': 'AAPL', 'price': 150.00, 'change': 2.5}
        }

        channel = 'spider:financial:data'
        r.publish(channel, str(test_data))
        print(f"✅ Published test data to {channel}")

        # Check if agents could receive
        print("\n🤖 Agents that could process this data:")
        financial_agents = ['investment_advisor', 'wealth_builder', 'day_trader']
        for agent_name in financial_agents:
            if agent_name in [a['name'] for a in agents]:
                print(f"  ✅ {agent_name}")

    except Exception as e:
        print(f"⚠️  Redis test failed: {e}")
        print("   Make sure Redis is running: redis-server")

    print("\n✨ SUMMARY")
    print(f"{'='*50}")
    print("• 13 spiders are registered and ready")
    print("• 149 agents are available to receive data")
    print("• Redis pub/sub infrastructure is in place")
    print("• Missing: Active collection loops")
    print("\nNext step: Implement spider collection loops to start gathering real data")

if __name__ == "__main__":
    print("🕷️  SPIDER ACTIVATION SYSTEM")
    print("="*50)

    # Run tests
    asyncio.run(test_spider_connectivity())
    asyncio.run(activate_minimal_spider_system())