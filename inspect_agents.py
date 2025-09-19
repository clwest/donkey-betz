#!/usr/bin/env python3
"""
AGENT SYSTEM INSPECTION
Let's see what these agents actually DO
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution

print("=" * 60)
print("AGENT SYSTEM ANALYSIS")
print("=" * 60)

# 1. What agents do you have?
print("\n📋 AGENT INVENTORY:")
print("-" * 40)
agents = UnifiedAgentTemplate.objects.all()[:5]  # First 5
for agent in agents:
    print(f"\nAgent: {agent.name}")
    print(f"  Specialization: {agent.specialization}")
    print(f"  Description: {agent.description[:100]}..." if agent.description else "  No description")
    print(f"  Capabilities: {agent.capabilities}")
    print(f"  Required tools: {agent.required_tools}")

# 2. What executions have happened?
print("\n\n📊 EXECUTION HISTORY:")
print("-" * 40)
executions = AgentExecution.objects.all()[:5]  # Last 5
if executions:
    # First, let's see what fields are actually available
    if executions.first():
        available_fields = [f.name for f in executions.first()._meta.fields]
        print(f"Available fields on AgentExecution: {available_fields}")
    
    for exec in executions:
        print(f"\nExecution ID: {exec.id}")
        
        # Safely check for agent template field (could be 'template' or 'agent_template')
        if hasattr(exec, 'template'):
            print(f"  Agent: {exec.template.name if exec.template else 'None'}")
        elif hasattr(exec, 'agent_template'):
            print(f"  Agent: {exec.agent_template.name if exec.agent_template else 'None'}")
        else:
            print("  Agent: Field not found")
        
        # Safely check for status
        if hasattr(exec, 'status'):
            print(f"  Status: {exec.status}")
        
        # Safely check for created_at
        if hasattr(exec, 'created_at'):
            print(f"  Created: {exec.created_at}")
        
        # Check for various possible result fields
        if hasattr(exec, 'result'):
            print(f"  Result: {str(exec.result)[:100]}...")
        elif hasattr(exec, 'output'):
            print(f"  Output: {str(exec.output)[:100]}...")
        elif hasattr(exec, 'response'):
            print(f"  Response: {str(exec.response)[:100]}...")
else:
    print("No executions found")

# 3. How do you execute an agent?
print("\n\n🔧 EXECUTION METHODS:")
print("-" * 40)

# Check for execute methods
agent = UnifiedAgentTemplate.objects.first()
if agent:
    methods = [m for m in dir(agent) if 'execute' in m.lower()]
    print(f"Agent methods with 'execute': {methods}")
    
    # Check for manager methods
    manager_methods = [m for m in dir(UnifiedAgentTemplate.objects) if 'execute' in m.lower()]
    print(f"Manager methods with 'execute': {manager_methods}")

# 4. Check the actual execution model
print("\n\n🔍 EXECUTION MODEL FIELDS:")
print("-" * 40)
if AgentExecution.objects.exists():
    exec_fields = [f.name for f in AgentExecution._meta.fields]
    print(f"AgentExecution fields: {exec_fields}")

# 5. System Statistics
print("\n\n📦 SYSTEM STATISTICS:")
print("-" * 40)
total_agents = UnifiedAgentTemplate.objects.count()
total_executions = AgentExecution.objects.count()
print(f"Total agents: {total_agents}")
print(f"Total executions: {total_executions}")

# Check execution statuses if they exist
if AgentExecution.objects.exists() and hasattr(AgentExecution.objects.first(), 'status'):
    from django.db.models import Count
    status_counts = AgentExecution.objects.values('status').annotate(count=Count('status'))
    print("\nExecution status breakdown:")
    for status in status_counts:
        print(f"  {status['status']}: {status['count']}")

# Recent executions
recent_execs = AgentExecution.objects.order_by('-created_at')[:3] if hasattr(AgentExecution, 'created_at') else []
if recent_execs:
    print("\nMost recent executions:")
    for exec in recent_execs:
        agent_name = exec.template.name if hasattr(exec, 'template') and exec.template else 'Unknown'
        print(f"  - {agent_name} at {exec.created_at}")

print("\n" + "=" * 60)
print("KEY QUESTIONS:")
print("=" * 60)
print("1. Do agents have an execute() method?")
print("2. Are there any API endpoints to trigger execution?")
print("3. Are executions supposed to be triggered by events?")
print("4. Is there a scheduler/celery task for agents?")
