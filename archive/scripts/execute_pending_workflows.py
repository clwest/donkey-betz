#!/usr/bin/env python
"""
Script to manually execute pending workflows
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from agents.models import AgentOrchestration, AgentStatus
from agents.tasks import execute_orchestration
from django.contrib.auth import get_user_model

User = get_user_model()

def execute_pending():
    print("\n" + "="*60)
    print("EXECUTING PENDING WORKFLOWS")
    print("="*60)
    
    # Get pending orchestrations for user chris
    pending = AgentOrchestration.objects.filter(
        user__username='chris',
        status=AgentStatus.PENDING
    ).order_by('-created_at')
    
    if not pending:
        print("\nNo pending workflows found for user 'chris'")
        return
    
    print(f"\nFound {pending.count()} pending workflows for chris:\n")
    
    for orch in pending:
        print(f"Executing: {orch.name} (ID: {orch.id})")
        print(f"  Agents: {len(orch.agent_sequence) if orch.agent_sequence else 0}")
        
        try:
            # Try Celery first
            result = execute_orchestration.delay(str(orch.id))
            print(f"  ✅ Queued for Celery execution (Task ID: {result.id})")
        except Exception as e:
            print(f"  ⚠️  Celery failed: {e}")
            print(f"  🔄 Executing synchronously...")
            
            # Execute synchronously as fallback
            try:
                # Call the task directly (without .delay())
                result = execute_orchestration(str(orch.id))
                print(f"  ✅ Executed successfully!")
            except Exception as sync_error:
                print(f"  ❌ Execution failed: {sync_error}")
        
        print("-" * 40)
    
    print("\n" + "="*60)
    print("CHECKING UPDATED STATUS")
    print("="*60)
    
    # Check updated status
    updated = AgentOrchestration.objects.filter(
        user__username='chris'
    ).order_by('-created_at')[:5]
    
    print("\nLatest workflow statuses:\n")
    for orch in updated:
        print(f"- {orch.name}: {orch.status}")
        if hasattr(orch, 'completed_at') and orch.completed_at:
            print(f"  Completed: {orch.completed_at}")

if __name__ == "__main__":
    execute_pending()