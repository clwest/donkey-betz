#!/usr/bin/env python
"""
Fast Enhanced Routing - Optimized for Speed
=============================================

Direct, efficient routing update to reach 80% target quickly.
"""

import os
import sys
import django
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from persistence.models import SpiderData
from django.db import connection


# Pre-build agent keyword index for fast lookup
def build_agent_index():
    """Build fast lookup index of agent keywords"""
    agents = UnifiedAgentTemplate.objects.filter(is_active=True)
    agent_index = {}

    for agent in agents:
        keywords = set()

        # Extract from name
        name_parts = re.split(r'[-_]', agent.name.lower())
        keywords.update(p for p in name_parts if len(p) > 2)

        # Extract from description if available
        if agent.description:
            desc_words = re.findall(r'\b\w{4,}\b', agent.description.lower())
            stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will',
                          'your', 'their', 'what', 'when', 'which', 'them', 'than',
                          'then', 'into', 'also', 'such', 'only'}
            keywords.update(w for w in desc_words if w not in stop_words)

        agent_index[agent.name] = {
            'keywords': keywords,
            'description': agent.description or ""
        }

    return agent_index


# Spider keywords for matching
SPIDER_KEYWORDS = {
    'patreon': ['content', 'monetization', 'creator', 'revenue', 'subscription', 'writer', 'income', 'product', 'digital', 'social', 'media'],
    'substack': ['content', 'monetization', 'creator', 'newsletter', 'writer', 'revenue', 'subscription', 'income', 'email'],
    'kaggle': ['data', 'ml', 'machine', 'learning', 'analytics', 'research', 'python', 'science', 'analysis', 'model', 'neural', 'competition'],
    'github': ['dev', 'code', 'software', 'programming', 'api', 'technical', 'development', 'engineer', 'repository', 'version', 'control'],
    'huggingface': ['ai', 'ml', 'machine', 'learning', 'nlp', 'research', 'python', 'model', 'neural', 'transformer', 'language'],
    'stackoverflow': ['dev', 'code', 'technical', 'programming', 'software', 'api', 'development', 'engineer', 'question', 'answer'],
    'innovation': ['research', 'trend', 'analysis', 'market', 'startup', 'business', 'innovation', 'tech', 'opportunity', 'venture'],
    'combat_sports': ['betting', 'sports', 'combat', 'ufc', 'mma', 'value', 'odds', 'fight', 'boxing', 'martial', 'prediction'],
    'horse_racing': ['betting', 'sports', 'racing', 'horse', 'value', 'arbitrage', 'odds', 'track', 'prediction'],
    'guru': ['freelance', 'career', 'job', 'income', 'work', 'application', 'employment', 'gig', 'project'],
    'gumroad': ['product', 'digital', 'monetization', 'creator', 'revenue', 'sales', 'income', 'content', 'ecommerce'],
    'remoteok': ['job', 'career', 'remote', 'work', 'freelance', 'income', 'employment', 'tech', 'developer'],
    'medium': ['content', 'writer', 'creator', 'monetization', 'seo', 'blog', 'article', 'writing', 'publish'],
    'coingecko': ['crypto', 'blockchain', 'finance', 'trading', 'market', 'investment', 'bitcoin', 'ethereum', 'coin', 'token'],
    'etherscan': ['crypto', 'blockchain', 'ethereum', 'smart', 'contract', 'defi', 'finance', 'transaction'],
    'seekingalpha': ['stock', 'finance', 'trading', 'investment', 'market', 'equity', 'portfolio', 'analyst'],
}


def fast_match_agents(spider_name, agent_index):
    """Fast agent matching using pre-built index"""
    # Get spider keywords
    spider_kw = []
    for key, keywords in SPIDER_KEYWORDS.items():
        if key in spider_name.lower():
            spider_kw.extend(keywords)

    if not spider_kw:
        spider_kw = re.split(r'[-_]', spider_name.lower())

    # Match against agent index
    matched = []
    for agent_name, agent_data in agent_index.items():
        agent_kw = agent_data['keywords']

        # Check for keyword overlap (including partial matches)
        for sk in spider_kw:
            if len(sk) < 3:
                continue
            for ak in agent_kw:
                # Exact or contains match
                if sk == ak or (len(sk) >= 4 and (sk in ak or ak in sk)):
                    matched.append(agent_name)
                    break
            if agent_name in matched:
                break

    return matched


def main():
    print("=" * 80)
    print("FAST ENHANCED ROUTING - Reach 80% Target")
    print("=" * 80)

    # Build agent index
    print("\n📊 Building agent index...")
    agent_index = build_agent_index()
    print(f"   Indexed {len(agent_index)} agents")

    # Get current state
    print("\n📊 Analyzing current state...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT unnest(routed_to_agents) as agent_name
            FROM persistence_spiderdata
            WHERE routed_to_agents IS NOT NULL AND routed_to_agents != '{}'
        """)
        current_agents_with_data = {row[0] for row in cursor.fetchall()}

    total_agents = len(agent_index)
    current_count = len(current_agents_with_data)
    print(f"   Current: {current_count} / {total_agents} agents ({current_count/total_agents*100:.1f}%)")

    # Get existing routing for all spiders in one query (OPTIMIZED)
    print("\n🚀 Fetching existing routing...")
    existing_routing = {}
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT ON (spider_name) spider_name, routed_to_agents
            FROM persistence_spiderdata
            ORDER BY spider_name, id DESC
        """)
        for row in cursor.fetchall():
            spider_name = row[0]
            agents = set(row[1]) if row[1] else set()
            existing_routing[spider_name] = agents

    print(f"   Found {len(existing_routing)} spider types")

    # Build new routing table
    print("\n🚀 Building enhanced routing table...")
    routing_updates = {}
    all_matched = set()

    for spider_name in existing_routing.keys():
        # Get existing agents
        existing = existing_routing.get(spider_name, set())

        # Get new matches
        new_matches = set(fast_match_agents(spider_name, agent_index))

        # Combine
        combined = existing | new_matches

        if combined:
            routing_updates[spider_name] = list(combined)
            all_matched.update(combined)

    # Calculate improvement
    new_agents = all_matched - current_agents_with_data
    final_count = len(all_matched)

    print(f"\n✅ Routing Analysis Complete:")
    print(f"   Current agents with data:  {current_count} / {total_agents} ({current_count/total_agents*100:.1f}%)")
    print(f"   After enhanced routing:    {final_count} / {total_agents} ({final_count/total_agents*100:.1f}%)")
    print(f"   New agents unlocked:       {len(new_agents)}")
    print(f"   Target:                    142 / {total_agents} (80.0%)")

    if final_count >= 142:
        print(f"\n🎉 SUCCESS! Will exceed 80% target!")
    else:
        print(f"\n📊 Progress: Still {142 - final_count} agents short of 80% target")

    # Show sample of new agents
    if new_agents:
        print(f"\n📋 Sample newly matched agents:")
        for agent_name in sorted(new_agents)[:15]:
            print(f"   - {agent_name}")
        if len(new_agents) > 15:
            print(f"   ... and {len(new_agents) - 15} more")

    # Apply updates
    response = input("\nApply enhanced routing? (yes/no): ").strip().lower()

    if response == 'yes':
        print("\n🚀 Applying routing updates...")

        from django.db import transaction

        updated_count = 0
        with transaction.atomic():
            for spider_name, agents in routing_updates.items():
                result = SpiderData.objects.filter(spider_name=spider_name).update(
                    routed_to_agents=agents
                )
                updated_count += result

        print(f"\n✅ Complete!")
        print(f"   Updated {updated_count:,} spider data entries")
        print(f"   Modified {len(routing_updates)} spider types")

        # Verify
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT unnest(routed_to_agents) as agent_name
                FROM persistence_spiderdata
                WHERE routed_to_agents IS NOT NULL AND routed_to_agents != '{}'
            """)
            final_agents = {row[0] for row in cursor.fetchall()}

        final_count = len(final_agents)
        print(f"\n📊 Final State:")
        print(f"   Agents with data: {final_count} / {total_agents} ({final_count/total_agents*100:.1f}%)")

        if final_count >= 142:
            print(f"\n🎉 SUCCESS! Reached 80%+ target!")
            print(f"   Improvement: {current_count} → {final_count} (+{final_count - current_count} agents)")
        else:
            print(f"\n📈 Progress: {current_count} → {final_count} (+{final_count - current_count} agents)")
            print(f"   Still need: {142 - final_count} more agents for 80% target")

    else:
        print("\n❌ Cancelled")


if __name__ == '__main__':
    main()
