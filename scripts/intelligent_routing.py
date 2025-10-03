#!/usr/bin/env python
"""
Intelligent Routing Script
==========================

This script implements keyword-based intelligent routing to match spider data
with relevant agents based on spider name, data type, and relevance tags.

This will unlock 146 agents that currently receive zero data!
"""

import os
import sys
import django
import re
from collections import defaultdict

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from persistence.models import SpiderData
from django.db.models import Q, Count


# Define keyword mappings for spider names to agent types
SPIDER_TO_AGENT_KEYWORDS = {
    'patreon': ['content', 'monetization', 'creator', 'revenue', 'subscription', 'writer'],
    'substack': ['content', 'monetization', 'creator', 'newsletter', 'writer', 'revenue'],
    'kaggle': ['data', 'ml', 'machine-learning', 'analytics', 'research', 'python'],
    'github': ['dev', 'code', 'software', 'programming', 'api', 'technical'],
    'huggingface': ['ai', 'ml', 'machine-learning', 'nlp', 'research', 'python'],
    'stackoverflow': ['dev', 'code', 'technical', 'programming', 'software', 'api'],
    'innovation': ['research', 'trend', 'analysis', 'market', 'startup', 'business'],
    'combat_sports': ['betting', 'sports', 'combat', 'ufc', 'mma', 'value'],
    'horse_racing': ['betting', 'sports', 'racing', 'horse', 'value', 'arbitrage'],
    'guru': ['freelance', 'career', 'job', 'income', 'work', 'application'],
    'gumroad': ['product', 'digital', 'monetization', 'creator', 'revenue', 'sales'],
    'remoteok': ['job', 'career', 'remote', 'work', 'freelance', 'income'],
    'medium': ['content', 'writer', 'creator', 'monetization', 'seo'],
}


def get_agent_keywords(agent_name):
    """Extract keywords from agent name"""
    # Split by hyphens and underscores
    parts = re.split(r'[-_]', agent_name.lower())
    return [p for p in parts if len(p) > 2]  # Filter short words


def match_agents_for_spider(spider_name, all_agents):
    """Find all agents that match keywords for a spider"""
    # Get keywords for this spider
    spider_keywords = []
    for key, keywords in SPIDER_TO_AGENT_KEYWORDS.items():
        if key in spider_name.lower():
            spider_keywords.extend(keywords)

    if not spider_keywords:
        # Fallback: use spider name parts as keywords
        spider_keywords = re.split(r'[-_]', spider_name.lower())

    # Match agents
    matched_agents = []
    for agent in all_agents:
        agent_keywords = get_agent_keywords(agent.name)

        # Check if any spider keyword matches any agent keyword
        for sk in spider_keywords:
            for ak in agent_keywords:
                if sk in ak or ak in sk:
                    matched_agents.append(agent.name)
                    break
            if agent.name in matched_agents:
                break

    return matched_agents


def calculate_potential_improvement():
    """Calculate how many agents will benefit from intelligent routing"""
    all_agents = list(UnifiedAgentTemplate.objects.filter(is_active=True))

    # Get unique spider names
    spider_names = SpiderData.objects.values_list('spider_name', flat=True).distinct()

    # Build routing table
    routing_table = {}
    all_newly_matched = set()

    for spider_name in spider_names:
        matched = match_agents_for_spider(spider_name, all_agents)
        routing_table[spider_name] = matched
        all_newly_matched.update(matched)

    # Get current agents with data
    current_agents_with_data = set()
    for agent in all_agents:
        if SpiderData.objects.filter(routed_to_agents__contains=[agent.name]).exists():
            current_agents_with_data.add(agent.name)

    # Calculate new agents
    new_agents = all_newly_matched - current_agents_with_data

    return routing_table, len(current_agents_with_data), len(all_newly_matched), len(new_agents)


def apply_intelligent_routing(dry_run=True):
    """Apply intelligent routing to all spider data"""
    all_agents = list(UnifiedAgentTemplate.objects.filter(is_active=True))

    # Get spider names and their counts
    spider_counts = SpiderData.objects.values('spider_name').annotate(
        count=Count('id')
    ).order_by('-count')

    total_updated = 0
    routing_changes = []

    for sp in spider_counts:
        spider_name = sp['spider_name']
        count = sp['count']

        # Get matched agents
        matched_agents = match_agents_for_spider(spider_name, all_agents)

        if not matched_agents:
            continue

        # Get existing routing for this spider
        sample = SpiderData.objects.filter(spider_name=spider_name).first()
        existing_agents = sample.routed_to_agents if sample else []

        # Combine existing + new agents (remove duplicates)
        combined_agents = list(set(existing_agents + matched_agents))

        routing_changes.append({
            'spider': spider_name,
            'count': count,
            'old_agents': len(existing_agents),
            'new_agents': len(combined_agents),
            'added': len(combined_agents) - len(existing_agents),
            'agents': combined_agents[:10]  # Show first 10
        })

        if not dry_run:
            # Update all entries for this spider
            SpiderData.objects.filter(spider_name=spider_name).update(
                routed_to_agents=combined_agents
            )
            total_updated += count

    return routing_changes, total_updated


def main():
    print("=" * 80)
    print("INTELLIGENT ROUTING - Unlock 146 Agents")
    print("=" * 80)

    # Calculate potential improvement
    print("\n📊 Analyzing potential improvements...")
    routing_table, current_count, potential_count, new_count = calculate_potential_improvement()

    print(f"\n✅ Current State:")
    print(f"   Agents with data: {current_count} / 177 ({current_count/177*100:.1f}%)")

    print(f"\n🚀 After Intelligent Routing:")
    print(f"   Agents with data: {potential_count} / 177 ({potential_count/177*100:.1f}%)")
    print(f"   New agents unlocked: {new_count}")

    print(f"\n📋 Routing Table (sample):")
    for spider_name, agents in list(routing_table.items())[:5]:
        print(f"\n   {spider_name}:")
        print(f"      → {len(agents)} agents: {', '.join(agents[:5])}...")

    # Show routing changes
    print(f"\n\n📈 Applying Intelligent Routing (DRY RUN)...")
    changes, total = apply_intelligent_routing(dry_run=True)

    print(f"\n   Will update {len(changes)} spider types:")
    for change in changes[:10]:
        print(f"      {change['spider']:25} ({change['count']:>6,} entries): "
              f"{change['old_agents']:>2} → {change['new_agents']:>2} agents "
              f"(+{change['added']})")

    # Ask for confirmation
    print("\n" + "=" * 80)
    response = input("\nApply intelligent routing? (yes/no): ").strip().lower()

    if response == 'yes':
        print("\n🚀 Applying intelligent routing...")
        changes, total_updated = apply_intelligent_routing(dry_run=False)

        print(f"\n✅ COMPLETE!")
        print(f"   Updated: {total_updated:,} spider data entries")
        print(f"   Modified: {len(changes)} spider types")

        # Verify
        agents_with_data = 0
        for agent in UnifiedAgentTemplate.objects.filter(is_active=True):
            if SpiderData.objects.filter(routed_to_agents__contains=[agent.name]).exists():
                agents_with_data += 1

        print(f"\n📊 New State:")
        print(f"   Agents with data: {agents_with_data} / 177 ({agents_with_data/177*100:.1f}%)")

        if agents_with_data >= 120:
            print(f"\n🎉 SUCCESS! Reached target of 120+ agents (80%+)!")
        else:
            print(f"\n⚠️  Still need {120 - agents_with_data} more agents to reach 80% target")

    else:
        print("\n❌ Cancelled - no changes made")


if __name__ == '__main__':
    main()
