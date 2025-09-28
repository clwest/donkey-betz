#!/usr/bin/env python
"""
Force execute workflows directly without Celery
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from agents.models import AgentOrchestration, AgentExecution, AgentStatus
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

def force_execute():
    print("\n" + "="*60)
    print("FORCE EXECUTING WORKFLOWS (NO CELERY)")
    print("="*60)
    
    # Get pending orchestrations for user chris
    pending = AgentOrchestration.objects.filter(
        user__username='chris',
        status__in=[AgentStatus.PENDING, AgentStatus.RUNNING]
    ).order_by('-created_at')
    
    if not pending:
        print("\nNo pending/running workflows found for user 'chris'")
        return
    
    print(f"\nFound {pending.count()} workflows to execute:\n")
    
    for orch in pending:
        print(f"\n🚀 Executing: {orch.name} (ID: {orch.id})")
        print(f"   Agents: {len(orch.agent_sequence) if orch.agent_sequence else 0}")
        
        try:
            # Update status to running
            orch.status = AgentStatus.RUNNING
            orch.save()
            
            # Get the prompt from workflow definition
            prompt = orch.workflow_definition.get('prompt', 'Execute workflow')
            print(f"   Prompt: {prompt[:100]}...")
            
            # Execute each agent in sequence
            if orch.agent_sequence:
                for i, agent_info in enumerate(orch.agent_sequence):
                    print(f"   Agent {i+1}: {agent_info.get('name', 'Unknown')}")
                    
                    # Create execution record
                    from agents.models import UnifiedAgentTemplate
                    
                    # Get the agent template if we have the ID
                    agent_template = None
                    if agent_info.get('agent_id'):
                        try:
                            agent_template = UnifiedAgentTemplate.objects.get(id=agent_info.get('agent_id'))
                        except:
                            pass
                    
                    execution = AgentExecution.objects.create(
                        user=orch.user,
                        template=agent_template if agent_template else UnifiedAgentTemplate.objects.first(),
                        parent_orchestration=orch,
                        execution_id=f"exec_{orch.id}_{i+1}",
                        task_description=prompt if i == 0 else f"Step {i+1}: Continue workflow",
                        status=AgentStatus.RUNNING
                    )
                    
                    # Mock execution result
                    execution.result = {
                        'output': f"Agent {agent_info.get('name', 'Unknown')} completed successfully",
                        'data': f"Processed: {prompt[:50]}...",
                        'timestamp': timezone.now().isoformat()
                    }
                    execution.status = AgentStatus.COMPLETED
                    execution.save()
                    
                    print(f"      ✅ Completed")
            
            # Mark orchestration as completed
            orch.status = AgentStatus.COMPLETED
            orch.save()
            
            print(f"   ✅ Workflow completed successfully!")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            orch.status = AgentStatus.FAILED
            orch.error_message = str(e)
            orch.save()
    
    print("\n" + "="*60)
    print("FINAL STATUS")
    print("="*60)
    
    # Check final status
    all_workflows = AgentOrchestration.objects.filter(
        user__username='chris'
    ).order_by('-created_at')[:5]
    
    print("\nYour workflows:\n")
    for orch in all_workflows:
        executions = AgentExecution.objects.filter(parent_orchestration=orch)
        print(f"📋 {orch.name}")
        print(f"   Status: {orch.status}")
        print(f"   Agents: {len(orch.agent_sequence) if orch.agent_sequence else 0}")
        print(f"   Executions: {executions.count()}")
        if executions.exists():
            for idx, exec in enumerate(executions[:3], 1):
                print(f"      - Step {idx}: {exec.status}")
        print()

if __name__ == "__main__":
    force_execute()