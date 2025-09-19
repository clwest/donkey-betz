#!/usr/bin/env python3
"""
Fix the collaboration error in activate_all_agents.py
"""

import os

def fix_collaboration():
    """Fix the parent_orchestration error"""
    
    file_path = '/Users/donkeyking/development/unified-donkey-betz/activate_all_agents.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find and fix the issue
    old_code = """        # Create parent orchestration
        lead_agent = agents[0]
        parent_exec = AgentExecution.objects.create(
            template=lead_agent,
            user=self.user,
            task_description=f"[ORCHESTRATION] {task}",
            task_type='orchestration',
            status=AgentStatus.RUNNING,
            priority=3
        )
        
        # Create child executions
        for i, agent in enumerate(agents):
            child_exec = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                task_description=f"[PART {i+1}] {task}",
                task_type=agent.specialization,
                parent_orchestration=parent_exec,"""
    
    new_code = """        # Create parent orchestration using AgentOrchestration model
        from agents.models import AgentOrchestration
        lead_agent = agents[0]
        
        # Create the orchestration object
        parent_orch = AgentOrchestration.objects.create(
            name=f"Collaboration: {task[:50]}",
            description=task,
            created_by=self.user,
            orchestration_type='collaboration',
            config={
                'task': task,
                'agents': [a.name for a in agents]
            },
            status='active'
        )
        
        # Create executions for each agent
        for i, agent in enumerate(agents):
            child_exec = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                task_description=f"[PART {i+1}] {task}",
                task_type=agent.specialization,
                parent_orchestration=parent_orch,"""
    
    if old_code.replace(" ", "") in content.replace(" ", ""):
        # Replace the code
        fixed_content = content.replace(old_code, new_code)
        
        # Also need to fix the parent completion
        fixed_content = fixed_content.replace(
            "        # Complete parent\n        parent_exec.status = AgentStatus.COMPLETED\n        parent_exec.save()",
            "        # Complete orchestration\n        parent_orch.status = 'completed'\n        parent_orch.save()"
        )
        
        # Save backup
        backup_path = file_path.replace('.py', '_backup.py')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backed up to: {backup_path}")
        
        # Save fixed version
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print("✅ Fixed collaboration error!")
        return True
    else:
        print("❌ Could not find the code to fix")
        print("Trying simpler fix...")
        
        # Simpler fix - just comment out parent_orchestration line
        if "parent_orchestration=parent_exec," in content:
            fixed_content = content.replace(
                "parent_orchestration=parent_exec,",
                "# parent_orchestration=parent_exec,  # Fixed: removed incorrect assignment"
            )
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            print("✅ Applied simpler fix - commented out problematic line")
            return True
        
        return False

if __name__ == "__main__":
    print("🔧 FIXING COLLABORATION ERROR")
    print("-" * 40)
    
    if fix_collaboration():
        print("\n✅ Fix applied!")
        print("\nRun again:")
        print("python activate_all_agents.py")
    else:
        print("\n❌ Could not apply fix automatically")
        print("\nManual fix:")
        print("Edit activate_all_agents.py")
        print("Comment out or remove: parent_orchestration=parent_exec,")
        print("From line ~306 in execute_collaboration method")
