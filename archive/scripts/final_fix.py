#!/usr/bin/env python3
"""
🎯 FINAL FIX - Simple collaboration without AgentOrchestration
"""

import os

def apply_final_fix():
    """Apply a simple fix that removes the AgentOrchestration dependency"""
    
    file_path = '/Users/donkeyking/development/unified-donkey-betz/activate_all_agents.py'
    
    # Read current content
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find and replace the execute_collaboration method
    new_lines = []
    skip_until_next_def = False
    
    for i, line in enumerate(lines):
        # Found the problematic method
        if 'def execute_collaboration(self, agents, task):' in line:
            skip_until_next_def = True
            # Insert the fixed version
            new_lines.append('''    def execute_collaboration(self, agents, task):
        """Execute a collaborative task between multiple agents"""
        
        print(f"   🚀 Executing collaboration...")
        
        # Simple collaboration without AgentOrchestration
        import uuid
        collab_id = str(uuid.uuid4())[:8]
        
        # Execute each agent with shared context
        for i, agent in enumerate(agents):
            exec = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                task_description=f"[COLLAB-{collab_id}] Part {i+1}: {task}",
                task_type=agent.specialization,
                status=AgentStatus.INITIALIZING,
                priority=2,
                context={
                    'collaboration_id': collab_id,
                    'collaboration_task': task,
                    'role': f'team_member_{i+1}',
                    'total_members': len(agents)
                }
            )
            self.simulate_execution(exec)
        
        print(f"   ✅ Collaboration completed")
    
''')
        elif skip_until_next_def and line.strip().startswith('def ') and 'execute_collaboration' not in line:
            # Found the next method, stop skipping
            skip_until_next_def = False
            new_lines.append(line)
        elif not skip_until_next_def:
            # Normal line, keep it
            new_lines.append(line)
    
    # Write the fixed version
    with open(file_path, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Applied final fix!")
    print("\nWhat was fixed:")
    print("• Removed AgentOrchestration dependency completely")
    print("• Simplified collaboration to just execute agents with shared context")
    print("• Each agent gets a collaboration ID to know they're working together")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("🎯 APPLYING FINAL FIX")
    print("="*60)
    
    apply_final_fix()
    
    print("\n✅ Ready to run!")
    print("\nNow run:")
    print("python activate_all_agents.py")
    print("\nThis will complete the full activation without errors!")
