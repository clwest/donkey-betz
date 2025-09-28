#!/usr/bin/env python
"""
Execute pending agent tasks directly (bypassing Celery for now)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from agents.models import AgentExecution
from agents.tasks_enhanced import execute_agent_with_tools
from django.utils import timezone
import time

def execute_pending_agents():
    """Execute all pending agent tasks"""
    
    while True:
        # Get pending executions
        pending = AgentExecution.objects.filter(status='pending').order_by('created_at')
        
        if not pending.exists():
            print("No pending executions. Waiting...")
            time.sleep(5)
            continue
        
        for execution in pending:
            print(f"\n{'='*50}")
            print(f"Executing: {execution.execution_id}")
            print(f"Agent: {execution.template.name if execution.template else 'Unknown'}")
            print(f"Task: {execution.task_description[:100] if execution.task_description else 'No description'}")
            
            try:
                # Execute with enhanced tools
                result = execute_agent_with_tools(execution.execution_id)
                
                print(f"✅ SUCCESS!")
                if result and 'output' in result:
                    print(f"Output preview: {result['output'][:200]}...")
                    
            except Exception as e:
                print(f"❌ FAILED: {e}")
                # Mark as failed
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.completed_at = timezone.now()
                execution.save()
            
            time.sleep(1)  # Small delay between executions

if __name__ == '__main__':
    print("🤖 Agent Executor Started")
    print("This will execute pending agent tasks directly")
    print("Press Ctrl+C to stop\n")
    
    try:
        execute_pending_agents()
    except KeyboardInterrupt:
        print("\n\n✋ Executor stopped")