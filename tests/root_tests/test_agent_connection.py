#!/usr/bin/env python
"""Test agent connection fixes"""

import os
import django
import sys
import asyncio

# Add project to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.command_center_ai import CommandCenterAI

async def test_agent_connections():
    """Test various agent connection scenarios"""
    print("Testing Agent Connections...")

    # Initialize command center
    command_center = CommandCenterAI()

    # Test different connection requests
    test_cases = [
        "Connect me with market_analyzer",  # Should map to market-research-specialist
        "Connect me with revenue",          # Should map to revenue-activation-orchestrator
        "Connect me with business-agent",   # Direct name
        "Connect me with content",          # Should map to content-creator
    ]

    for test_case in test_cases:
        print(f"\n📝 Testing: '{test_case}'")
        print("-" * 50)

        try:
            response = await command_center.process_natural_command(
                test_case,
                user_id="test_user"
            )

            if "✅ **Connected to" in response:
                print("✅ SUCCESS - Agent connected!")
                # Extract agent name from response
                import re
                match = re.search(r'Connected to (.+?)\*\*', response)
                if match:
                    print(f"   Connected to: {match.group(1)}")
            elif "❌ Could not connect" in response:
                print("❌ FAILED - Could not connect")
                # Extract available agents
                if "Available agents include:" in response:
                    lines = response.split('\n')
                    for line in lines:
                        if line.startswith('• '):
                            print(f"   Available: {line}")
            else:
                print("⚠️ UNEXPECTED RESPONSE")
                print(f"   Response: {response[:200]}...")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 50)
    print("Test Complete!")

    # Test deploy command
    print("\n📦 Testing Deploy Command...")
    deploy_response = await command_center.process_natural_command(
        "/deploy agents revenue",
        user_id="test_user"
    )

    if "deployed" in deploy_response.lower():
        print("✅ Deploy command working!")
    else:
        print("⚠️ Deploy command may have issues")

if __name__ == "__main__":
    asyncio.run(test_agent_connections())