#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentRegistry

# Test agent discovery for prompting tasks
registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')

# Test finding agents for prompting tasks
test_tasks = [
    "optimize this prompt for better AI responses",
    "improve prompt engineering for my AI system", 
    "help me write better prompts for content generation",
    "analyze and improve my prompt performance"
]

print("Testing agent discovery for prompt-related tasks:")
for task in test_tasks:
    print(f"\nTask: {task}")
    agents = registry.find_agents_for_task(task, limit=3)
    for agent_result in agents:
        print(f"  - {agent_result['agent_name']} (score: {agent_result['score']:.2f})")