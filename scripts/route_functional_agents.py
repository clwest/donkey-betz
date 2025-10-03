#!/usr/bin/env python
"""
Route Functional Agents to Appropriate Spiders
===============================================

Manually route the 27 functional agents without data to appropriate spiders.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import SpiderData
from django.db import transaction


# Define manual routing rules for functional agents
MANUAL_ROUTING = {
    # Design/Creative agents → design spiders
    'creative-design-agent': ['dribbble', 'behance', 'gumroad', 'medium'],
    'ui/ux-designer': ['dribbble', 'behance', 'producthunt'],
    'brand-guidelines-agent': ['dribbble', 'behance', 'medium'],
    'image-video-pipeline': ['dribbble', 'behance'],

    # Communication/Content agents → content spiders
    'communication-agent': ['medium', 'substack', 'patreon', 'github'],
    'consistency-specialist-creative-agent': ['medium', 'substack', 'gumroad'],

    # Infrastructure agents → tech spiders
    'cache-optimizer': ['github', 'stackoverflow', 'hackernews'],
    'token-budget-manager': ['huggingface', 'github', 'kaggle'],
    'token-budget-agent': ['huggingface', 'github', 'kaggle'],
    'monitoring-dashboard': ['github', 'stackoverflow', 'devto'],
    'memory-isolation-agent': ['github', 'stackoverflow', 'huggingface'],
    'makefile-builder': ['github', 'stackoverflow'],
    'os-specialist-agent': ['github', 'stackoverflow', 'hackernews'],

    # Orchestration agents → general tech/business spiders
    'empire-builder-orchestrator': ['innovation', 'github', 'kaggle', 'producthunt'],
    'task-delegation-orchestrator': ['github', 'stackoverflow', 'innovation'],
    'system-unification-architect': ['github', 'stackoverflow', 'innovation'],
    'intelligent-prompting-integrator': ['huggingface', 'github', 'kaggle'],
    'limitless-system-implementation-orchestrator': ['github', 'huggingface', 'innovation'],
    'core-agents-enablement-coordinator': ['github', 'stackoverflow', 'innovation'],

    # Specialized agents
    'correlation-hunter': ['kaggle', 'huggingface', 'innovation'],
    'narrative-predictor-agent': ['medium', 'substack', 'kaggle'],
    'glossary-anchor-curator': ['huggingface', 'github', 'stackoverflow'],
    'ucwsf-deploy-agent': ['github', 'stackoverflow'],
}


def apply_manual_routing():
    """Apply manual routing for functional agents"""
    print("=" * 80)
    print("ROUTING FUNCTIONAL AGENTS TO APPROPRIATE SPIDERS")
    print("=" * 80)

    updates_made = []

    with transaction.atomic():
        for agent_name, spider_names in MANUAL_ROUTING.items():
            agents_added = 0
            entries_updated = 0

            for spider_name in spider_names:
                # Get existing routing for this spider
                entries = SpiderData.objects.filter(spider_name=spider_name)

                if not entries.exists():
                    print(f"  ⚠️  Spider '{spider_name}' has no data (skipping)")
                    continue

                # Get current agents
                sample = entries.first()
                current_agents = sample.routed_to_agents or []

                # Add agent if not already present
                if agent_name not in current_agents:
                    new_agents = current_agents + [agent_name]
                    result = entries.update(routed_to_agents=new_agents)
                    entries_updated += result
                    agents_added += 1

            if agents_added > 0:
                updates_made.append({
                    'agent': agent_name,
                    'spiders': agents_added,
                    'entries': entries_updated
                })

    return updates_made


def main():
    print(f"\nPlanning to route {len(MANUAL_ROUTING)} functional agents...")
    print("\nAgent → Spider Mapping:")

    for agent, spiders in MANUAL_ROUTING.items():
        print(f"\n  {agent}")
        print(f"    → {', '.join(spiders)}")

    response = input("\n\nApply manual routing? (yes/no): ").strip().lower()

    if response == 'yes':
        print("\n🚀 Applying manual routing...\n")
        updates = apply_manual_routing()

        print("\n" + "=" * 80)
        print("✅ COMPLETE!")
        print("=" * 80)

        total_entries = sum(u['entries'] for u in updates)

        for update in updates:
            print(f"\n  {update['agent']}")
            print(f"    Added to {update['spiders']} spider types ({update['entries']:,} entries)")

        print(f"\n📊 Summary:")
        print(f"  Agents routed: {len(updates)}")
        print(f"  Entries updated: {total_entries:,}")

        # Verify final coverage
        from agents.models import UnifiedAgentTemplate
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT unnest(routed_to_agents) as agent_name
                FROM persistence_spiderdata
                WHERE routed_to_agents IS NOT NULL AND routed_to_agents != '{}'
            """)
            agents_with_data = {row[0] for row in cursor.fetchall()}

        total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        coverage = len(agents_with_data) / total_agents * 100

        print(f"\n📈 New Coverage:")
        print(f"  Agents with data: {len(agents_with_data)} / {total_agents} ({coverage:.1f}%)")
        print(f"  Target: 142 / 177 (80.0%)")

        if len(agents_with_data) >= 142:
            print(f"\n🎉 SUCCESS! Reached 80%+ target!")
        else:
            print(f"\n  Gap: {142 - len(agents_with_data)} agents to 80%")

    else:
        print("\n❌ Cancelled")


if __name__ == '__main__':
    main()
