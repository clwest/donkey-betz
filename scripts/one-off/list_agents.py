#!/usr/bin/env python3
"""
List all registered agents
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate

def list_agents():
    print("=" * 80)
    print("🤖 Registered Agents")
    print("=" * 80)
    print()

    agents = UnifiedAgentTemplate.objects.all().order_by('name')

    print(f"Total agents: {agents.count()}")
    print()

    for agent in agents:
        print(f"   - Name: {agent.name}")
        print(f"     Display Name: {agent.display_name}")
        print(f"     ID: {agent.id}")
        print()

if __name__ == "__main__":
    list_agents()
