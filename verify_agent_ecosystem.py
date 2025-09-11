#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentRegistry
from core.agent_integration import AgentRouter
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== AGENT ECOSYSTEM VERIFICATION ===\n")

# 1. Check total agent count
total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
print(f"1. Total Active Agents: {total_agents}")

# 2. Check agent specializations
specializations = UnifiedAgentTemplate.objects.filter(is_active=True).values_list('specialization', flat=True).distinct()
print(f"2. Specializations Available: {len(specializations)}")
for spec in sorted(specializations):
    count = UnifiedAgentTemplate.objects.filter(is_active=True, specialization=spec).count()
    print(f"   - {spec}: {count} agents")

# 3. Check key agents exist
key_agents = [
    "Intelligent Prompting Agent",
    "Personal Assistant Agent", 
    "Memory System Agent",
    "Agent Orchestra Coordinator",
    "Business Agent",
    "Content Agent",
    "Sports Analytics Expert",
    "Financial Agent"
]

print(f"\n3. Key Agents Verification:")
for agent_name in key_agents:
    try:
        agent = UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
        print(f"   ✓ {agent_name} - Found (specialization: {agent.specialization})")
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"   ✗ {agent_name} - NOT FOUND")

# 4. Test agent registry
print(f"\n4. Agent Registry Test:")
try:
    registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')
    print(f"   ✓ Registry found with {registry.active_agents} active agents")
    
    # Test routing for different task types
    test_user = User.objects.first()
    if test_user:
        router = AgentRouter(test_user)
        
        test_cases = [
            ("optimize my prompt for better AI responses", "Intelligent Prompting Agent"),
            ("create a business plan for my startup", "Business Agent"),
            ("analyze sports betting opportunities", "Sports Analytics Expert"),
            ("write a blog post about technology", "Content Agent"),
            ("help me manage my personal tasks", "Personal Assistant Agent")
        ]
        
        print(f"\n5. Routing Test Cases:")
        for query, expected_agent in test_cases:
            agents = registry.find_agents_for_task(query, limit=1)
            if agents:
                found_agent = agents[0]['agent_name']
                score = agents[0]['score']
                status = "✓" if expected_agent.lower() in found_agent.lower() else "~"
                print(f"   {status} '{query}' -> {found_agent} (score: {score:.2f})")
            else:
                print(f"   ✗ '{query}' -> No agents found")
                
except AgentRegistry.DoesNotExist:
    print(f"   ✗ Agent registry not found")

# 6. Check LLM provider distribution
print(f"\n6. LLM Provider Distribution:")
providers = UnifiedAgentTemplate.objects.filter(is_active=True).values_list('llm_provider', flat=True)
provider_counts = {}
for provider in providers:
    provider_counts[provider] = provider_counts.get(provider, 0) + 1

for provider, count in sorted(provider_counts.items()):
    print(f"   - {provider}: {count} agents")

print(f"\n=== ECOSYSTEM HEALTH SUMMARY ===")
print(f"Total Agents: {total_agents}")
print(f"Specializations: {len(specializations)}")
print(f"LLM Providers: {len(provider_counts)}")
print(f"Registry Status: {'✓ Active' if 'registry' in locals() else '✗ Missing'}")

if total_agents >= 36:
    print(f"✓ Agent ecosystem meets the 36+ requirement")
else:
    print(f"✗ Agent ecosystem has {total_agents} agents, below 36+ requirement")