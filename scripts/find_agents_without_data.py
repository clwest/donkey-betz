#!/usr/bin/env python
"""Find agents without data and create deployment plan"""

import os
import sys
from collections import defaultdict

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from agents.models import UnifiedAgentTemplate
from core.models_unified_system import UserAgentLearning

def main():
    print('🔍 FINDING AGENTS WITHOUT DATA')
    print('=' * 80)

    # Get all active agents
    all_agents = UnifiedAgentTemplate.objects.filter(is_active=True).order_by('specialization', 'name')
    print(f'\n📊 Total active agents: {all_agents.count()}')

    # Find agents without learning entries
    agents_without_data = []
    agents_with_data = []

    for agent in all_agents:
        has_data = UserAgentLearning.objects.filter(agent_name=agent.name).exists()
        if has_data:
            agents_with_data.append(agent)
        else:
            agents_without_data.append(agent)

    print(f'✅ Agents WITH data: {len(agents_with_data)}')
    print(f'❌ Agents WITHOUT data: {len(agents_without_data)}')

    # Group by specialization
    by_specialization = defaultdict(list)
    for agent in agents_without_data:
        by_specialization[agent.specialization or 'unspecified'].append(agent)

    print(f'\n📋 AGENTS WITHOUT DATA (by specialization):')
    print('=' * 80)

    for spec, agents in sorted(by_specialization.items()):
        print(f'\n🔸 {spec.upper()} ({len(agents)} agents):')
        for agent in agents:
            print(f'   • {agent.name}')

    # Calculate coverage
    coverage_target = int(all_agents.count() * 0.9)
    current_coverage = len(agents_with_data)
    needed = coverage_target - current_coverage

    print(f'\n' + '=' * 80)
    print(f'🎯 COVERAGE ANALYSIS')
    print(f'=' * 80)
    print(f'Goal (90%):  {coverage_target} agents')
    print(f'Current:     {current_coverage} agents ({current_coverage/all_agents.count()*100:.1f}%)')
    print(f'Needed:      {needed} more agents')

    # Suggest deployment strategy
    print(f'\n' + '=' * 80)
    print(f'🚀 DEPLOYMENT STRATEGY')
    print(f'=' * 80)

    # Already deployed spiders
    from persistence.models import SpiderData
    active_spiders = set(SpiderData.objects.values_list('spider_name', flat=True).distinct())
    print(f'\nCurrently deployed spiders ({len(active_spiders)}):')
    for spider in sorted(active_spiders)[:10]:
        print(f'   • {spider}')
    if len(active_spiders) > 10:
        print(f'   ... and {len(active_spiders) - 10} more')

    # Suggest domains needing coverage
    print(f'\nDomains needing coverage:')
    domain_priority = {}
    for spec, agents in sorted(by_specialization.items(), key=lambda x: len(x[1]), reverse=True):
        domain_priority[spec] = len(agents)
        print(f'   • {spec}: {len(agents)} agents')

    print(f'\n' + '=' * 80)
    print(f'✅ Analysis complete! Found {len(agents_without_data)} agents without data')

if __name__ == "__main__":
    main()
