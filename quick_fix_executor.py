#!/usr/bin/env python3
"""
QUICK FIX - Update content_executor to use correct LLM method
"""

import os

def fix_content_executor():
    """Fix the content executor to use enforce_real_ai instead of generate_completion"""
    
    executor_path = '/Users/donkeyking/development/unified-donkey-betz/agents/content_executor.py'
    
    # Read the file
    with open(executor_path, 'r') as f:
        content = f.read()
    
    # Check if it's using the wrong method
    if 'self.llm_enforcer.generate_completion' in content:
        print("Found incorrect method call: generate_completion")
        print("Replacing with: enforce_real_ai")
        
        # Replace the method call
        # Old pattern: self.llm_enforcer.generate_completion(prompt=..., max_tokens=..., temperature=...)
        # New pattern: self.llm_enforcer.enforce_real_ai(prompt=..., max_tokens=..., temperature=..., agent_name='content-creator')
        
        fixed_content = content.replace(
            'self.llm_enforcer.generate_completion(',
            "self.llm_enforcer.enforce_real_ai("
        )
        
        # Also need to handle the response format difference
        # enforce_real_ai returns a dict with 'response' key
        # We need to extract just the response text
        
        # Find the lines where we get the response
        lines = fixed_content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if 'llm_response = self.llm_enforcer.enforce_real_ai(' in line:
                # This is the line where we call the method
                new_lines.append(line)
                # Look ahead to add response extraction after the call
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(')'):
                    new_lines.append(lines[j])
                    j += 1
                if j < len(lines):
                    new_lines.append(lines[j])  # Add the closing parenthesis line
                    # Add extraction of response
                    indent = '            '  # Match the indentation
                    new_lines.append(f"{indent}# Extract response from dict")
                    new_lines.append(f"{indent}if isinstance(llm_response, dict) and llm_response.get('success'):")
                    new_lines.append(f"{indent}    llm_response = llm_response.get('response', '')")
                    new_lines.append(f"{indent}elif isinstance(llm_response, dict):")
                    new_lines.append(f"{indent}    llm_response = llm_response.get('error', 'Generation failed')")
                    # Skip the lines we already processed
                    for k in range(j+1, len(lines)):
                        new_lines.append(lines[k])
                    break
            else:
                new_lines.append(line)
        
        # If we didn't find the specific pattern, use simpler replacement
        if len(new_lines) == len(lines):
            new_lines = []
            for line in lines:
                if 'llm_response = self.llm_enforcer.enforce_real_ai(' in line:
                    new_lines.append(line)
                    # Add agent_name parameter if not present
                    if 'agent_name' not in line:
                        new_lines.append("                agent_name='content-creator',")
                else:
                    new_lines.append(line)
            fixed_content = '\n'.join(new_lines)
        else:
            fixed_content = '\n'.join(new_lines)
        
        # Save backup
        backup_path = executor_path.replace('.py', '_backup.py')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Save fixed version
        fixed_path = executor_path.replace('.py', '_fixed.py')
        with open(fixed_path, 'w') as f:
            f.write(fixed_content)
        print(f"✅ Created fixed version: {fixed_path}")
        
        return True
    else:
        print("❌ Method call not found or already fixed")
        # Check if it's already using enforce_real_ai
        if 'self.llm_enforcer.enforce_real_ai' in content:
            print("✅ Already using correct method: enforce_real_ai")
        return False

if __name__ == "__main__":
    print("="*60)
    print("QUICK FIX - CONTENT EXECUTOR")
    print("="*60)
    
    if fix_content_executor():
        print("\n✅ Fix created successfully!")
        print("\nTo apply:")
        print("1. cp agents/content_executor_fixed.py agents/content_executor.py")
        print("2. python execute_test_agent.py --check")
        print("3. python execute_test_agent.py")
    else:
        print("\n⚠️ No changes needed or fix failed")
