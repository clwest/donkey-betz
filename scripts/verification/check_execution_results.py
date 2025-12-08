# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Check execution results in database
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models.agents_registry import AgentOrchestration, AgentExecution
from django.contrib.auth import get_user_model

User = get_user_model()

def check_results():
    print("\n" + "="*60)
    print("CHECKING EXECUTION RESULTS")
    print("="*60)
    
    # Get Chris's completed orchestrations
    orchestrations = AgentOrchestration.objects.filter(
        user__username='chris',
        status='completed'
    ).order_by('-created_at')
    
    print(f"\nFound {orchestrations.count()} completed workflows for chris\n")
    
    for orch in orchestrations:
        print(f"\n📋 WORKFLOW: {orch.name}")
        print(f"   ID: {orch.id}")
        print(f"   Status: {orch.status}")
        print(f"   Created: {orch.created_at}")
        
        # Get executions for this orchestration
        executions = AgentExecution.objects.filter(
            parent_orchestration=orch
        ).order_by('id')
        
        print(f"   Executions: {executions.count()}")
        
        for exec in executions:
            print(f"\n   🤖 AGENT EXECUTION:")
            print(f"      Execution ID: {exec.execution_id}")
            print(f"      Template: {exec.template.name if exec.template else 'None'}")
            print(f"      Status: {exec.status}")
            print(f"      Task: {exec.task_description[:100] if exec.task_description else 'None'}...")
            
            # Check if result exists
            if hasattr(exec, 'result') and exec.result:
                print(f"      Result: {json.dumps(exec.result, indent=8)[:500]}...")
            else:
                print(f"      Result: No result stored")
            
            # Check for other result fields
            if hasattr(exec, 'execution_result') and exec.execution_result:
                print(f"      Execution Result: {exec.execution_result[:200]}...")
            
            if hasattr(exec, 'output') and exec.output:
                print(f"      Output: {exec.output[:200]}...")
        
        print("\n" + "-"*40)

if __name__ == "__main__":
    check_results()