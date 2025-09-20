#!/usr/bin/env python3
"""
🔧 FIX COLLABORATION ERROR - Remove or simplify the orchestration parent
"""

import os

def fix_collaboration_error():
    """Fix the AgentOrchestration field mismatch"""
    
    file_path = '/Users/donkeyking/development/unified-donkey-betz/activate_all_agents.py'
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Create a simpler solution - just remove the parent orchestration
    old_collaboration_code = '''    def execute_collaboration(self, agents, task):
        """Execute a collaborative task between multiple agents"""
        
        print(f"   🚀 Executing collaboration...")
        
        # Create parent orchestration using AgentOrchestration model
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
                parent_orchestration=parent_orch,
                status=AgentStatus.INITIALIZING,
                priority=2,
                collaboration_context={
                    'role': f'team_member_{i+1}',
                    'parent_id': str(parent_orch.id)
                }
            )
            
            self.simulate_execution(child_exec)
        
        # Complete orchestration
        parent_orch.status = 'completed'
        parent_orch.save()'''
    
    # Simplified version without parent orchestration
    new_collaboration_code = '''    def execute_collaboration(self, agents, task):
        """Execute a collaborative task between multiple agents"""
        
        print(f"   🚀 Executing collaboration...")
        
        # Create a shared collaboration ID
        import uuid
        collaboration_id = str(uuid.uuid4())[:8]
        
        # Create executions for each agent with shared context
        for i, agent in enumerate(agents):
            child_exec = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                task_description=f"[COLLAB {collaboration_id}] {task}",
                task_type=agent.specialization,
                status=AgentStatus.INITIALIZING,
                priority=2,
                context={
                    'collaboration': True,
                    'collaboration_id': collaboration_id,
                    'role': f'team_member_{i+1}',
                    'task': task,
                    'team_size': len(agents)
                }
            )
            
            self.simulate_execution(child_exec)'''
    
    # Replace the code
    if 'def execute_collaboration' in content:
        # Find the method and replace it
        lines = content.split('\n')
        new_lines = []
        in_method = False
        indent_count = 0
        
        for i, line in enumerate(lines):
            if 'def execute_collaboration(self, agents, task):' in line:
                in_method = True
                # Add the new method
                for new_line in new_collaboration_code.split('\n'):
                    new_lines.append(new_line)
                # Skip to end of old method
                continue
            
            if in_method:
                # Check if we've reached the next method
                if line.strip().startswith('def ') and 'execute_collaboration' not in line:
                    in_method = False
                    new_lines.append(line)
                # Skip lines from old method
            else:
                new_lines.append(line)
        
        fixed_content = '\n'.join(new_lines)
        
        # Save backup
        backup_path = file_path.replace('.py', '_backup2.py')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backed up to: {backup_path}")
        
        # Save fixed version
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print("✅ Fixed collaboration error!")
        
        return True
    else:
        print("❌ Could not find execute_collaboration method")
        return False

if __name__ == "__main__":
    print("🔧 FIXING COLLABORATION ERROR (SIMPLIFIED)")
    print("-" * 40)
    
    if fix_collaboration_error():
        print("\n✅ Fix applied!")
        print("\nThe fix:")
        print("• Removed AgentOrchestration dependency")
        print("• Using shared collaboration_id instead")
        print("• Agents can still work together")
        print("\nRun again:")
        print("python activate_all_agents.py")
    else:
        print("\n❌ Could not apply fix")
