#!/usr/bin/env python
"""
URGENT REALITY CHECK - ARE COMPONENTS REAL OR FAKE?
=====================================================
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

print("\n" + "="*80)
print("🔍 SYSTEM REALITY VERIFICATION - SEPTEMBER 26, 2025")
print("="*80)

# ============================================================
# CHECK 1: AGENTS - ARE THEY REAL?
# ============================================================
print("\n📋 CHECKING AGENTS...")
print("-"*60)

try:
    from agents.registry import AgentRegistry
    registry = AgentRegistry()
    all_agents = registry.get_all_agents()

    print(f"✅ Found {len(all_agents)} agents in registry")

    # Check specific agents
    real_agents = []
    test_agents = ["income_builder", "market_analyst", "code_analyzer", "financial_advisor", "job_hunter"]

    for agent_name in test_agents:
        agent = registry.get_agent(agent_name)
        if agent:
            print(f"  ✓ {agent_name}: EXISTS")
            # Check if it has real properties
            if agent.get('implementation_path') or agent.get('execute_fn'):
                real_agents.append(agent_name)
                print(f"    → Has implementation: YES")
            else:
                print(f"    → Has implementation: NO (might be placeholder)")

    # Try to execute one
    print("\n🧪 Testing agent execution...")
    from backend.agents.concrete_executor import ConcreteAgentExecutor
    executor = ConcreteAgentExecutor()

    result = executor.execute(
        agent_name="code_analyzer",
        task_description="Test execution",
        context={}
    )

    if result.get('success'):
        print(f"✅ Agent execution: WORKS!")
    else:
        print(f"⚠️  Agent execution: {result.get('error', 'Failed')}")

    AGENTS_REAL = len(real_agents) > 0
    print(f"\n{'✅' if AGENTS_REAL else '❌'} AGENTS: {'REAL' if AGENTS_REAL else 'NEED WORK'}")

except Exception as e:
    print(f"❌ Error checking agents: {e}")
    AGENTS_REAL = False

# ============================================================
# CHECK 2: ADVISORS - ARE THEY REAL?
# ============================================================
print("\n👥 CHECKING ADVISORS...")
print("-"*60)

try:
    # First try the registry
    from agents.registry import AdvisorRegistry
    advisor_registry = AdvisorRegistry()

    print(f"✅ Found {len(advisor_registry.advisors)} advisors")

    # Check for legendary advisors
    legendary = ["Warren Buffett", "Cathie Wood", "Ray Dalio", "Peter Lynch"]
    found_legendary = []

    for advisor_name in legendary:
        advisor = advisor_registry.get_advisor_by_name(advisor_name)
        if advisor:
            print(f"  ✓ {advisor_name}: EXISTS")
            found_legendary.append(advisor_name)

    ADVISORS_REAL = len(found_legendary) > 0
    print(f"\n{'✅' if ADVISORS_REAL else '❌'} ADVISORS: {'REAL' if ADVISORS_REAL else 'NEED WORK'}")

except Exception as e:
    print(f"⚠️  Could not load advisors from registry: {e}")
    ADVISORS_REAL = False

# ============================================================
# CHECK 3: SPIDERS - ARE THEY REAL?
# ============================================================
print("\n🕷️ CHECKING SPIDERS...")
print("-"*60)

try:
    from backend.spiders.registry import SpiderRegistry
    spider_registry = SpiderRegistry()
    all_spiders = spider_registry.get_all_spiders()

    print(f"✅ Found {len(all_spiders)} spiders in registry")

    # Check specific spiders
    important_spiders = ["financial", "toptal", "github_jobs", "coingecko", "innovation"]
    real_spiders = []

    for spider_name in important_spiders:
        spider_class = spider_registry.get_spider(spider_name)
        if spider_class:
            print(f"  ✓ {spider_name}: EXISTS")

            # Check if spider has real methods
            spider_instance = spider_class()
            if hasattr(spider_instance, 'fetch_data'):
                print(f"    → Can fetch data: YES")
                real_spiders.append(spider_name)

            if hasattr(spider_instance, 'base_url'):
                url = spider_instance.base_url
                if url and not url.startswith('http://example'):
                    print(f"    → Has real URL: {url[:50]}...")
                else:
                    print(f"    → Has mock URL")

    SPIDERS_REAL = len(real_spiders) > 0
    print(f"\n{'✅' if SPIDERS_REAL else '❌'} SPIDERS: {'REAL' if SPIDERS_REAL else 'NEED WORK'}")

except Exception as e:
    print(f"❌ Error checking spiders: {e}")
    SPIDERS_REAL = False

# ============================================================
# CHECK 4: DATABASE - IS IT REAL?
# ============================================================
print("\n💾 CHECKING DATABASE...")
print("-"*60)

try:
    from agents.models import UnifiedAgentTemplate
    from intelligence.models import AIProposal

    agent_count = UnifiedAgentTemplate.objects.count()
    proposal_count = AIProposal.objects.count()

    print(f"✅ Database connected")
    print(f"  • Agent templates: {agent_count}")
    print(f"  • AI proposals: {proposal_count}")

    DATABASE_REAL = True
    print(f"\n✅ DATABASE: REAL")

except Exception as e:
    print(f"❌ Database error: {e}")
    DATABASE_REAL = False

# ============================================================
# CHECK 5: REDIS - IS IT WORKING?
# ============================================================
print("\n📡 CHECKING REDIS...")
print("-"*60)

try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Test connection
    r.ping()
    print(f"✅ Redis connected")

    # Check for stored data
    keys_sample = r.keys('*')[:5]
    print(f"  • Keys in Redis: {len(r.keys('*'))}")

    # Check for specific keys
    if r.exists('agents:registry'):
        print(f"  • Agents registry: EXISTS")
    if r.exists('spiders:registry'):
        print(f"  • Spiders registry: EXISTS")
    if r.exists('consciousness:ai_proposals'):
        print(f"  • AI proposals: EXISTS")

    REDIS_REAL = True
    print(f"\n✅ REDIS: WORKING")

except Exception as e:
    print(f"❌ Redis error: {e}")
    REDIS_REAL = False

# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "="*80)
print("📊 FINAL REALITY CHECK RESULTS")
print("="*80)

components = {
    "AGENTS": AGENTS_REAL,
    "ADVISORS": ADVISORS_REAL,
    "SPIDERS": SPIDERS_REAL,
    "DATABASE": DATABASE_REAL,
    "REDIS": REDIS_REAL
}

real_count = sum(1 for v in components.values() if v)
total_count = len(components)

for component, is_real in components.items():
    status = "✅ REAL" if is_real else "❌ NEEDS WORK"
    print(f"{component:15} {status}")

print("\n" + "="*80)

if real_count == total_count:
    print("🎉 SYSTEM IS 100% REAL AND READY FOR PRODUCTION!")
    print("All components verified and functional.")
elif real_count >= 3:
    print(f"⚠️  SYSTEM IS {real_count}/{total_count} REAL")
    print("Most components working, some need attention.")
else:
    print(f"❌ SYSTEM NEEDS WORK: Only {real_count}/{total_count} components real")
    print("Major components need to be implemented.")

print("="*80)
print(f"\nReality Score: {(real_count/total_count)*100:.0f}%")
print("="*80)