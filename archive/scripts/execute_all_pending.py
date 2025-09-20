#!/usr/bin/env python
"""
Execute all pending agent executions directly (synchronously)
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

# Get pending executions
pending_executions = AgentExecution.objects.filter(status='pending')

print(f"Found {pending_executions.count()} pending executions")
print("Executing them synchronously...\n")

success_count = 0
failed_count = 0

for execution in pending_executions:
    print(f"Processing: {execution.execution_id}")
    print(f"  Template: {execution.template.name}")
    
    try:
        # Execute directly (not async)
        result = execute_agent(execution.execution_id)
        print(f"  ✅ Completed successfully")
        success_count += 1
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed_count += 1

print(f"\n✅ Execution complete!")
print(f"  Successful: {success_count}")
print(f"  Failed: {failed_count}")

# Final status check
from agents.models import AgentExecution
print(f"\nFinal database status:")
print(f"  Pending: {AgentExecution.objects.filter(status='pending').count()}")
print(f"  Completed: {AgentExecution.objects.filter(status='completed').count()}")
print(f"  Failed: {AgentExecution.objects.filter(status='failed').count()}")