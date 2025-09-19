#!/usr/bin/env python3
"""
SIMPLE TEST - Is the data there or not?
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution

print("\nSIMPLE DATABASE CHECK:")
print("=" * 40)

# Just count what's there
agents = UnifiedAgentTemplate.objects.count()
active_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
executions = AgentExecution.objects.count()

print(f"Total agents in database: {agents}")
print(f"Active agents: {active_agents}")
print(f"Total executions: {executions}")

# If there are agents, show one
if agents > 0:
    first_agent = UnifiedAgentTemplate.objects.first()
    print(f"\nFirst agent: {first_agent.name}")
    print(f"Is active: {first_agent.is_active}")

print("=" * 40)

if agents == 0:
    print("❌ NO DATA IN DATABASE")
    print("Run: python populate_real_data_simple.py")
else:
    print("✅ DATA EXISTS")
    print(f"You have {agents} agents and {executions} executions")
