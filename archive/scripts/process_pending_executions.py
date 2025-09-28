#!/usr/bin/env python
"""
Process pending agent executions by dispatching them to Celery
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import AgentExecution
from agents.tasks import execute_agent
from django.utils import timezone
from datetime import timedelta

# Get pending executions
pending_executions = AgentExecution.objects.filter(
    status='pending',
    created_at__gte=timezone.now() - timedelta(hours=2)
)

print(f"Found {pending_executions.count()} pending executions")

for execution in pending_executions:
    # Fix empty task descriptions
    if not execution.task_description:
        if execution.input_data:
            home = execution.input_data.get('home_team', 'Team A')
            away = execution.input_data.get('away_team', 'Team B')
            execution.task_description = f"Analyze {away} vs {home} betting opportunity"
            execution.save()
    
    print(f"\nProcessing: {execution.execution_id}")
    print(f"  Template: {execution.template.name}")
    print(f"  Task: {execution.task_description[:50]}")
    
    try:
        # Dispatch to Celery
        task = execute_agent.delay(execution.execution_id)
        print(f"  ✅ Dispatched to Celery with task ID: {task.id}")
    except Exception as e:
        print(f"  ❌ Error dispatching: {e}")

print("\n✅ All pending executions have been dispatched to Celery workers")