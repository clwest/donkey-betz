#!/usr/bin/env python
"""
Test agent execution with correct field names
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
import uuid

print("\n" + "="*60)
print("AGENT FIELD NAME VERIFICATION")
print("="*60)

# Get a sample agent
agent = UnifiedAgentTemplate.objects.filter(name__icontains='odds').first()

if agent:
    print(f"\n✅ Agent: {agent.name}")
    print(f"   Provider field: llm_provider = '{agent.llm_provider}'")
    print(f"   Model field: llm_model = '{agent.llm_model}'")
    
    # Show all relevant fields
    print("\n📋 All agent fields:")
    for field in agent._meta.fields:
        if any(x in field.name for x in ['provider', 'model', 'llm']):
            value = getattr(agent, field.name, None)
            print(f"   {field.name}: {value}")
    
    # Test creating an execution
    print("\n🧪 Testing execution creation...")
    execution = AgentExecution.objects.create(
        execution_id=f"test_{uuid.uuid4().hex[:8]}",
        template=agent,
        task_description="Test: Calculate odds for Alabama -16.5",
        task_type='test',
        status='pending'
    )
    print(f"✅ Created execution: {execution.execution_id}")
    
    # Clean up
    execution.delete()
    print("🧹 Cleaned up test execution")
    
    print("\n✨ SUCCESS: Agent model is using correct field names!")
    print("   - Use 'llm_provider' not 'provider'")
    print("   - Use 'llm_model' not 'model'")
else:
    print("❌ No agents found")

print("\n" + "="*60 + "\n")
