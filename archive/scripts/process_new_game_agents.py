#!/usr/bin/env python
"""
Process pending agent executions for the new game
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import AgentExecution
from agents.tasks import execute_agent
from django.utils import timezone
from datetime import timedelta

# Get pending executions for Wisconsin vs Alabama
pending_executions = AgentExecution.objects.filter(
    status='pending',
    created_at__gte=timezone.now() - timedelta(minutes=15)
)

print(f"Found {pending_executions.count()} pending executions")

# Fix task descriptions and execute
for execution in pending_executions:
    # Fix empty task descriptions
    if not execution.task_description:
        home = execution.input_data.get('home_team', 'Team A')
        away = execution.input_data.get('away_team', 'Team B')
        agent_name = execution.template.name if execution.template else 'agent'
        
        execution.task_description = f"Analyze NCAAF game: {away} @ {home} - {agent_name.replace('-', ' ').title()} analysis for betting opportunities"
        execution.save()
        print(f"\nFixed task for: {execution.execution_id}")
    
    print(f"Processing: {execution.execution_id}")
    print(f"  Template: {execution.template.name if execution.template else 'Unknown'}")
    print(f"  Task: {execution.task_description[:60]}")
    
    try:
        # Execute the agent
        result = execute_agent(execution.execution_id)
        if result and 'output' in result:
            print(f"  ✅ Completed - Output length: {len(result['output'])}")
        else:
            print(f"  ⚠️ Completed but no output")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n✅ Processing complete!")

# Check final status
from agents.models import AgentExecution
print(f"\nFinal status:")
print(f"  Pending: {AgentExecution.objects.filter(status='pending').count()}")
print(f"  Running: {AgentExecution.objects.filter(status='running').count()}")
print(f"  Completed: {AgentExecution.objects.filter(status='completed').count()}")