#!/usr/bin/env python
"""
Create Missing Agents Script
============================

This script creates agent templates for all the agent names that spiders
are trying to route data to, but don't exist in the database.

This will instantly unlock ~470,000 wasted spider data entries!
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from persistence.models import SpiderData


def get_missing_agents():
    """Get list of agent names spiders target that don't exist"""
    # Get all unique target agent names from spider data
    all_routed = set()
    for data in SpiderData.objects.exclude(routed_to_agents=[]).values_list('routed_to_agents', flat=True):
        all_routed.update(data)

    # Get all actual agent names
    all_agents = set(UnifiedAgentTemplate.objects.filter(is_active=True).values_list('name', flat=True))

    # Find missing agents
    missing = sorted(all_routed - all_agents)

    return missing, all_routed, all_agents


def create_missing_agents(missing_agents, dry_run=False):
    """Create missing agent templates"""

    # Define agent configurations based on their names
    agent_configs = {
        'ai-development-agent': {
            'description': 'AI/ML development specialist for Python, TensorFlow, PyTorch',
            'category': 'development',
            'capabilities': ['ai_development', 'ml_engineering', 'python'],
        },
        'api-integration-agent': {
            'description': 'API integration and backend development specialist',
            'category': 'development',
            'capabilities': ['api_integration', 'backend_development', 'rest_apis'],
        },
        'combat-sports-specialist': {
            'description': 'UFC/MMA/Boxing betting and analysis specialist',
            'category': 'sports',
            'capabilities': ['combat_sports_analysis', 'betting_strategy', 'fight_analysis'],
        },
        'content-monetization-agent': {
            'description': 'Content monetization and creator economy specialist',
            'category': 'content',
            'capabilities': ['content_monetization', 'creator_economy', 'revenue_optimization'],
        },
        'data-science-agent': {
            'description': 'Data science and analytics specialist',
            'category': 'analytics',
            'capabilities': ['data_science', 'analytics', 'statistics'],
        },
        'digital-product-agent': {
            'description': 'Digital product creation and sales specialist',
            'category': 'product',
            'capabilities': ['digital_products', 'product_development', 'sales'],
        },
        'digital_product_creator': {
            'description': 'Digital product creation specialist (alternative naming)',
            'category': 'product',
            'capabilities': ['digital_products', 'product_creation'],
        },
        'horse-racing-specialist': {
            'description': 'Horse racing betting and analysis specialist',
            'category': 'sports',
            'capabilities': ['horse_racing_analysis', 'betting_strategy', 'racing_analytics'],
        },
        'income_builder': {
            'description': 'Income generation and opportunity specialist (alt naming)',
            'category': 'income',
            'capabilities': ['income_generation', 'opportunities'],
        },
        'javascript-dev-agent': {
            'description': 'JavaScript/TypeScript development specialist',
            'category': 'development',
            'capabilities': ['javascript', 'typescript', 'frontend_development'],
        },
        'ml-research-agent': {
            'description': 'Machine learning research and experimentation specialist',
            'category': 'research',
            'capabilities': ['ml_research', 'experimentation', 'research'],
        },
        'python-dev-agent': {
            'description': 'Python development specialist',
            'category': 'development',
            'capabilities': ['python', 'backend_development'],
        },
        'python-ml-agent': {
            'description': 'Python machine learning specialist',
            'category': 'development',
            'capabilities': ['python', 'machine_learning', 'ai'],
        },
        'sentiment_analysis_agent': {
            'description': 'Sentiment analysis and NLP specialist',
            'category': 'analytics',
            'capabilities': ['sentiment_analysis', 'nlp', 'text_analysis'],
        },
        'social-media-manager': {
            'description': 'Social media management and strategy specialist',
            'category': 'marketing',
            'capabilities': ['social_media', 'marketing', 'content_strategy'],
        },
        'social_trend_agent': {
            'description': 'Social media trend analysis specialist',
            'category': 'analytics',
            'capabilities': ['trend_analysis', 'social_media', 'analytics'],
        },
        'startup_opportunities': {
            'description': 'Startup and entrepreneurship opportunities specialist',
            'category': 'business',
            'capabilities': ['startup_analysis', 'opportunities', 'entrepreneurship'],
        },
        'tech_job_specialist': {
            'description': 'Tech job market and career specialist',
            'category': 'career',
            'capabilities': ['tech_jobs', 'career_development', 'job_market'],
        },
        'writer-agent': {
            'description': 'Professional writing and content creation specialist',
            'category': 'content',
            'capabilities': ['writing', 'content_creation', 'copywriting'],
        },
    }

    created = []
    skipped = []

    for agent_name in missing_agents:
        # Get config or use default
        config = agent_configs.get(agent_name, {
            'description': f'Specialized agent: {agent_name}',
            'category': 'general',
            'capabilities': ['data_processing'],
        })

        if dry_run:
            print(f"[DRY RUN] Would create: {agent_name}")
            print(f"  Description: {config['description']}")
            print(f"  Category: {config['category']}")
            print(f"  Capabilities: {config['capabilities']}")
            created.append(agent_name)
        else:
            # Check if agent already exists (shouldn't, but safety check)
            if UnifiedAgentTemplate.objects.filter(name=agent_name).exists():
                print(f"⚠️  Agent already exists: {agent_name}")
                skipped.append(agent_name)
                continue

            # Create agent
            agent = UnifiedAgentTemplate.objects.create(
                name=agent_name,
                description=config['description'],
                category=config['category'],
                capabilities=config['capabilities'],
                is_active=True,
                execution_mode='async',
                context_window_size=4000,
                requires_human_approval=False,
            )

            print(f"✅ Created: {agent_name}")
            created.append(agent_name)

    return created, skipped


def calculate_impact(missing_agents):
    """Calculate how many spider entries will be unlocked"""
    total_unlocked = 0

    print("\n=== IMPACT ANALYSIS ===")
    for agent_name in missing_agents[:10]:  # Show top 10
        count = SpiderData.objects.filter(routed_to_agents__contains=[agent_name]).count()
        total_unlocked += count
        print(f"{agent_name:35} {count:>8,} entries")

    if len(missing_agents) > 10:
        # Calculate remaining
        for agent_name in missing_agents[10:]:
            count = SpiderData.objects.filter(routed_to_agents__contains=[agent_name]).count()
            total_unlocked += count
        print(f"\n... and {len(missing_agents) - 10} more agents")

    print(f"\n{'Total entries to be unlocked:':<35} {total_unlocked:>8,}")
    return total_unlocked


def main():
    print("=" * 70)
    print("CREATE MISSING AGENTS - Fix Routing Bottleneck")
    print("=" * 70)

    # Get missing agents
    missing, all_routed, all_agents = get_missing_agents()

    print(f"\n📊 Current State:")
    print(f"   Spider targets: {len(all_routed)} unique agent names")
    print(f"   Actual agents:  {len(all_agents)} agents exist")
    print(f"   Missing:        {len(missing)} agents don't exist")

    if not missing:
        print("\n✅ All spider targets match existing agents!")
        return

    print(f"\n🚨 Missing Agents ({len(missing)}):")
    for i, name in enumerate(missing, 1):
        print(f"   {i:2}. {name}")

    # Calculate impact
    total_unlocked = calculate_impact(missing)

    # Ask for confirmation
    print("\n" + "=" * 70)
    response = input("\nCreate these agents? (yes/no/dry-run): ").strip().lower()

    if response == 'dry-run':
        print("\n🔍 DRY RUN MODE")
        created, skipped = create_missing_agents(missing, dry_run=True)
        print(f"\n✅ Would create {len(created)} agents")

    elif response == 'yes':
        print("\n🚀 Creating agents...")
        created, skipped = create_missing_agents(missing, dry_run=False)

        print("\n" + "=" * 70)
        print("✅ COMPLETE!")
        print(f"   Created: {len(created)} agents")
        print(f"   Skipped: {len(skipped)} agents (already existed)")
        print(f"   Unlocked: ~{total_unlocked:,} spider data entries")

        # Verify
        new_missing, _, new_all_agents = get_missing_agents()
        print(f"\n📊 New State:")
        print(f"   Total agents: {len(new_all_agents)}")
        print(f"   Missing: {len(new_missing)}")

        if len(new_missing) == 0:
            print("\n🎉 SUCCESS! All spider targets now have matching agents!")

    else:
        print("\n❌ Cancelled")


if __name__ == '__main__':
    main()
