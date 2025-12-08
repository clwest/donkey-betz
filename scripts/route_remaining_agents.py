#!/usr/bin/env python
"""
Route Remaining Agents to Existing Spider Data
=================================================

Connect 20 agents to existing spider data to reach 90% coverage.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from persistence.models import SpiderData

# Define routing rules: agent_name -> spider_names
ROUTING_RULES = {
    # Sports Analytics (3 agents) -> Use sports data
    'arbitrage-bet-finder': ['horse_racing', 'combat_sports'],
    'live-betting-specialist': ['horse_racing', 'combat_sports'],
    'value-bet-identifier': ['horse_racing', 'combat_sports'],

    # Marketing (3 agents) -> Use content spiders
    'audience-growth-strategist': ['substack', 'patreon', 'medium'],
    'conversion-rate-optimizer': ['gumroad', 'producthunt'],
    'seo-content-optimizer': ['medium', 'hashnode', 'devto'],

    # Creative (4 agents) -> Use design/content spiders
    'image-video-pipeline': ['behance', 'dribbble'],
    'brand-guidelines-agent': ['behance', 'dribbble'],
    'creative-design-agent': ['behance', 'dribbble'],
    'consistency-specialist-creative-agent': ['medium', 'substack'],

    # Technical (2 agents) -> Use tech spiders
    'api-integration-architect': ['stackoverflow', 'github', 'hackernews'],
    'performance-optimization-specialist': ['stackoverflow', 'github'],

    # Implementation (2 agents) -> Use tech spiders
    'devops-automation-engineer': ['github', 'stackoverflow', 'hackernews'],
    'ucwsf-deploy-agent': ['github'],

    # Business (1 agent) -> Use monetization spiders
    'affiliate-revenue-optimizer': ['gumroad', 'patreon', 'kofi'],

    # Risk (1 agent) -> Use sports data
    'bankroll-management-advisor': ['horse_racing', 'combat_sports'],

    # Design (1 agent) -> Use design spiders
    'ui/ux-designer': ['behance', 'dribbble'],

    # Orchestration (3 agents) -> Use documentation/system data
    'limitless-system-implementation-orchestrator': ['documentation_ingestor'],
    'system-unification-architect': ['documentation_ingestor'],
    'intelligent-prompting-integrator': ['documentation_ingestor'],
}

def main():
    print('🔗 ROUTING AGENTS TO EXISTING SPIDER DATA')
    print('=' * 80)

    total_routed = 0
    total_entries = 0

    for agent_name, spider_names in ROUTING_RULES.items():
        print(f'\n📍 Routing: {agent_name}')

        for spider_name in spider_names:
            # Find spider data entries
            entries = SpiderData.objects.filter(spider_name=spider_name)
            count = entries.count()

            if count == 0:
                print(f'   ⚠️  {spider_name}: No data found')
                continue

            # Add agent to routed_to_agents for each entry
            updated = 0
            for entry in entries.iterator(chunk_size=100):
                if entry.routed_to_agents is None:
                    entry.routed_to_agents = []

                if agent_name not in entry.routed_to_agents:
                    entry.routed_to_agents.append(agent_name)
                    entry.save(update_fields=['routed_to_agents'])
                    updated += 1

            print(f'   ✅ {spider_name}: {updated} entries updated')
            total_entries += updated

        total_routed += 1

    print(f'\n' + '=' * 80)
    print(f'✅ ROUTING COMPLETE')
    print(f'=' * 80)
    print(f'   Agents routed: {total_routed}')
    print(f'   Entries updated: {total_entries:,}')

    # Verify coverage
    print(f'\n🔍 VERIFYING COVERAGE:')
    all_routed_agents = set()
    for entry in SpiderData.objects.exclude(routed_to_agents__isnull=True).exclude(routed_to_agents=[]).iterator(chunk_size=1000):
        if entry.routed_to_agents:
            all_routed_agents.update(entry.routed_to_agents)

    from core.models.agents_registry import UnifiedAgentTemplate
    total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()

    print(f'   Agents with data: {len(all_routed_agents)}/{total_agents}')
    print(f'   Coverage: {len(all_routed_agents)/total_agents*100:.1f}%')

    if len(all_routed_agents) >= int(total_agents * 0.9):
        print(f'\n🎉 90% COVERAGE ACHIEVED!')
    else:
        print(f'\n📈 Need {int(total_agents * 0.9) - len(all_routed_agents)} more for 90%')

if __name__ == "__main__":
    main()
