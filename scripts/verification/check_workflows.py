# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Quick script to check workflow orchestrations in the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models.agents_registry import AgentOrchestration, AgentTaskExecution, AgentStatus
from django.contrib.auth import get_user_model

User = get_user_model()

def check_workflows():
    print("\n" + "="*60)
    print("WORKFLOW ORCHESTRATIONS IN DATABASE")
    print("="*60)
    
    # Get all orchestrations
    orchestrations = AgentOrchestration.objects.all().order_by('-created_at')
    
    if not orchestrations:
        print("\nNo orchestrations found in database!")
    else:
        print(f"\nFound {orchestrations.count()} orchestrations:\n")
        
        for orch in orchestrations[:10]:  # Show last 10
            print(f"ID: {orch.id}")
            print(f"  Name: {orch.name}")
            print(f"  User: {orch.user.username if orch.user else 'None'}")
            print(f"  Status: {orch.status}")
            print(f"  Created: {orch.created_at}")
            print(f"  Agents: {len(orch.agent_sequence) if orch.agent_sequence else 0}")
            
            # Check for executions
            executions = AgentTaskExecution.objects.filter(parent_orchestration=orch)
            if executions:
                print(f"  Executions: {executions.count()}")
                for exec in executions[:3]:
                    agent_name = getattr(exec, 'agent_name', None) or exec.agent_template.name if hasattr(exec, 'agent_template') else 'Unknown'
                    print(f"    - {agent_name}: {exec.status}")
            else:
                print(f"  Executions: None")
            print("-" * 40)
    
    print("\n" + "="*60)
    print("RECENT AGENT EXECUTIONS")
    print("="*60)
    
    recent_execs = AgentTaskExecution.objects.all().order_by('-created_at')[:10]
    if recent_execs:
        print(f"\nLast {len(recent_execs)} executions:\n")
        for exec in recent_execs:
            print(f"- {exec.agent_name} ({exec.status}) - {exec.created_at}")
            if exec.parent_orchestration:
                print(f"  Part of: {exec.parent_orchestration.name}")
    else:
        print("\nNo executions found!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    check_workflows()