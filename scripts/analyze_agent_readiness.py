#!/usr/bin/env python
"""
Agent Readiness Analysis
========================
Analyze which agents are fully configured and ready for spider data vs which need setup
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from collections import defaultdict


def analyze_agent_readiness():
    """Analyze all agents for readiness"""

    agents = UnifiedAgentTemplate.objects.filter(is_active=True).order_by('name')

    ready_agents = []
    partial_agents = []
    missing_config = []

    categories = defaultdict(list)

    for agent in agents:
        # Check configuration
        has_prompt = bool(agent.system_prompt and len(agent.system_prompt) > 50)
        has_capabilities = bool(agent.capabilities and len(agent.capabilities) > 0)
        has_description = bool(agent.description and len(agent.description) > 20)
        metrics = agent.performance_metrics or {}
        reality_score = metrics.get('reality_score', 0)

        agent_info = {
            'name': agent.name,
            'description': agent.description[:100] if agent.description else 'No description',
            'has_prompt': has_prompt,
            'has_capabilities': has_capabilities,
            'has_description': has_description,
            'reality_score': reality_score,
            'config_score': sum([has_prompt, has_capabilities, has_description]) / 3
        }

        # Categorize
        if has_prompt and has_capabilities and has_description:
            ready_agents.append(agent_info)
        elif has_prompt or has_capabilities:
            partial_agents.append(agent_info)
        else:
            missing_config.append(agent_info)

        # Categorize by type
        name_lower = agent.name.lower()
        desc_lower = (agent.description or '').lower()

        if any(kw in name_lower or kw in desc_lower for kw in ['income', 'freelance', 'gig', 'career', 'job']):
            categories['Income/Freelance'].append(agent_info)
        if any(kw in name_lower or kw in desc_lower for kw in ['content', 'writer', 'medium', 'creator', 'blog']):
            categories['Content'].append(agent_info)
        if any(kw in name_lower or kw in desc_lower for kw in ['sports', 'betting', 'odds', 'nfl', 'nba']):
            categories['Sports'].append(agent_info)
        if any(kw in name_lower or kw in desc_lower for kw in ['financial', 'trading', 'investment', 'crypto', 'stock']):
            categories['Financial'].append(agent_info)
        if any(kw in name_lower or kw in desc_lower for kw in ['developer', 'python', 'javascript', 'data', 'ml']):
            categories['Technical'].append(agent_info)
        if any(kw in name_lower or kw in desc_lower for kw in ['marketing', 'seo', 'social', 'brand']):
            categories['Marketing'].append(agent_info)

    # Print report
    print("=" * 100)
    print("🤖 AGENT READINESS ANALYSIS")
    print("=" * 100)
    print(f"\n📊 Total Active Agents: {agents.count()}")
    print(f"   ✅ Fully Ready: {len(ready_agents)} ({len(ready_agents)/agents.count()*100:.1f}%)")
    print(f"   ⚠️  Partial Config: {len(partial_agents)} ({len(partial_agents)/agents.count()*100:.1f}%)")
    print(f"   ❌ Missing Config: {len(missing_config)} ({len(missing_config)/agents.count()*100:.1f}%)")

    print(f"\n{'='*100}")
    print("✅ READY AGENTS (Fully Configured - Can Learn Immediately)")
    print("=" * 100)
    for agent in ready_agents:
        print(f"  {agent['name']:<40} Reality: {agent['reality_score']:.1%} | ✓ Prompt ✓ Capabilities ✓ Description")

    print(f"\n{'='*100}")
    print("⚠️  PARTIAL AGENTS (Some Configuration - Need Minor Setup)")
    print("=" * 100)
    for agent in partial_agents:
        status = []
        if agent['has_prompt']: status.append('✓ Prompt')
        else: status.append('✗ Prompt')
        if agent['has_capabilities']: status.append('✓ Capabilities')
        else: status.append('✗ Capabilities')
        if agent['has_description']: status.append('✓ Description')
        else: status.append('✗ Description')

        print(f"  {agent['name']:<40} {' '.join(status)}")

    print(f"\n{'='*100}")
    print("❌ MISSING CONFIG AGENTS (Need Full Setup)")
    print("=" * 100)
    for agent in missing_config:
        print(f"  {agent['name']:<40} ✗ Prompt ✗ Capabilities ✗ Description")

    print(f"\n{'='*100}")
    print("📋 AGENTS BY CATEGORY (Readiness Summary)")
    print("=" * 100)
    for category, agents_list in sorted(categories.items()):
        ready_count = sum(1 for a in agents_list if a['config_score'] == 1.0)
        partial_count = sum(1 for a in agents_list if 0 < a['config_score'] < 1.0)
        missing_count = sum(1 for a in agents_list if a['config_score'] == 0)

        print(f"\n{category} ({len(agents_list)} total):")
        print(f"  ✅ Ready: {ready_count} | ⚠️ Partial: {partial_count} | ❌ Missing: {missing_count}")

        # Show ready agents in this category
        ready_in_cat = [a for a in agents_list if a['config_score'] == 1.0]
        if ready_in_cat:
            print(f"  Ready to learn:")
            for agent in ready_in_cat[:5]:
                print(f"    • {agent['name']}")
            if len(ready_in_cat) > 5:
                print(f"    ... and {len(ready_in_cat) - 5} more")

    print(f"\n{'='*100}")
    print("🎯 DEPLOYMENT RECOMMENDATIONS")
    print("=" * 100)
    print(f"\n1. IMMEDIATE DEPLOYMENT ({len(ready_agents)} ready agents)")
    print("   Deploy spiders for these fully-configured agents NOW")

    print(f"\n2. QUICK SETUP NEEDED ({len(partial_agents)} partial agents)")
    print("   Add missing prompts/capabilities, then deploy")

    print(f"\n3. FULL SETUP NEEDED ({len(missing_config)} agents)")
    print("   These need complete configuration before deployment")

    # Spider-Agent matching recommendations
    print(f"\n{'='*100}")
    print("🕷️ SPIDER → AGENT DEPLOYMENT PLAN")
    print("=" * 100)

    spider_agent_map = {
        'Income Spiders (Guru, Toptal, RemoteOK)': [a['name'] for a in categories.get('Income/Freelance', []) if a['config_score'] == 1.0],
        'Content Spiders (Medium, Gumroad)': [a['name'] for a in categories.get('Content', []) if a['config_score'] == 1.0],
        'Sports Spiders (Social Sentiment)': [a['name'] for a in categories.get('Sports', []) if a['config_score'] == 1.0],
        'Financial Spiders (Market Data)': [a['name'] for a in categories.get('Financial', []) if a['config_score'] == 1.0],
    }

    for spider_type, agent_list in spider_agent_map.items():
        if agent_list:
            print(f"\n{spider_type}:")
            print(f"  Ready agents: {len(agent_list)}")
            for agent in agent_list[:3]:
                print(f"    → {agent}")
            if len(agent_list) > 3:
                print(f"    ... and {len(agent_list) - 3} more")
        else:
            print(f"\n{spider_type}:")
            print("  ⚠️  No fully ready agents - setup needed before deployment")

    print("\n" + "=" * 100)
    print("✅ Analysis complete! Use this to decide which spiders to deploy.")
    print("=" * 100)

    return {
        'ready': ready_agents,
        'partial': partial_agents,
        'missing': missing_config,
        'categories': dict(categories)
    }


if __name__ == '__main__':
    analyze_agent_readiness()
