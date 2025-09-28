#!/usr/bin/env python3
"""
Platform Awareness Injection Script

This script updates all agent system prompts to include platform awareness,
ensuring they recommend internal tools over external ones.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from agents.platform_capabilities import get_platform_awareness_prompt, get_brief_platform_prompt

def inject_platform_awareness():
    """Inject platform awareness into all agent system prompts"""

    # Get platform awareness content
    full_awareness = get_platform_awareness_prompt()
    brief_awareness = get_brief_platform_prompt()

    # Get all active agents
    agents = UnifiedAgentTemplate.objects.filter(is_active=True)

    print(f"🎯 Updating {agents.count()} active agents with platform awareness...")

    updated_count = 0
    skipped_count = 0

    for agent in agents:
        # Check if already has platform awareness
        if "PLATFORM CAPABILITIES" in agent.system_prompt or "PLATFORM TOOLS AVAILABLE" in agent.system_prompt:
            print(f"⏭️  Skipping {agent.name} - already has platform awareness")
            skipped_count += 1
            continue

        # Determine which version to use based on current prompt length
        current_length = len(agent.system_prompt)

        if current_length < 500:
            # Short prompt - use brief version
            awareness_content = brief_awareness
            print(f"📝 Updating {agent.name} with brief platform awareness (current: {current_length} chars)")
        else:
            # Longer prompt - use full version
            awareness_content = full_awareness
            print(f"📝 Updating {agent.name} with full platform awareness (current: {current_length} chars)")

        # Append platform awareness to existing prompt
        updated_prompt = f"{agent.system_prompt}\n\n{awareness_content}"

        # Update the agent
        agent.system_prompt = updated_prompt
        agent.save()

        updated_count += 1
        print(f"✅ Updated {agent.name} (new length: {len(updated_prompt)} chars)")

    print(f"\n🎉 Platform awareness injection complete!")
    print(f"📊 Summary:")
    print(f"   • Updated: {updated_count} agents")
    print(f"   • Skipped: {skipped_count} agents")
    print(f"   • Total: {agents.count()} agents")

    return updated_count, skipped_count

def show_sample_update():
    """Show a sample of what the updated prompt looks like"""

    agent = UnifiedAgentTemplate.objects.filter(is_active=True, name='business-agent').first()
    if not agent:
        agent = UnifiedAgentTemplate.objects.filter(is_active=True).first()

    if agent:
        print(f"\n📋 Sample updated prompt for '{agent.name}':")
        print("=" * 80)
        print(agent.system_prompt[:1000] + "..." if len(agent.system_prompt) > 1000 else agent.system_prompt)
        print("=" * 80)

if __name__ == "__main__":
    print("🚀 Platform Awareness Injection Tool")
    print("=" * 50)

    # Check if we should show sample first
    if "--sample" in sys.argv:
        show_sample_update()
        sys.exit(0)

    # Confirm before proceeding
    if "--force" not in sys.argv:
        response = input("\n🤔 This will update all agent system prompts. Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Aborted by user")
            sys.exit(1)

    # Perform the injection
    try:
        updated, skipped = inject_platform_awareness()

        print(f"\n🎯 Next steps:")
        print(f"1. Test Income Builder to verify internal tool recommendations")
        print(f"2. Monitor agent responses for platform integration")
        print(f"3. Check token usage impact on AI costs")

    except Exception as e:
        print(f"❌ Error during injection: {e}")
        sys.exit(1)