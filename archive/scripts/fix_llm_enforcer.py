#!/usr/bin/env python3
"""
FIX LLM ENFORCER - Add missing generate_completion method
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.llm_enforcer import LLMEnforcer

# Patch the LLMEnforcer class to add the missing method
def add_generate_completion_method():
    """Add the missing generate_completion method to LLMEnforcer"""
    
    def generate_completion(self, prompt, max_tokens=500, temperature=0.7, agent_name="Agent"):
        """
        Compatibility method for executors expecting generate_completion
        Maps to enforce_real_ai internally
        """
        result = self.enforce_real_ai(
            prompt=prompt,
            agent_name=agent_name,
            max_tokens=max_tokens,
            temperature=temperature,
            task_type="content"
        )
        
        # Return just the response text for compatibility
        if result['success']:
            return result['response']
        else:
            # Return error message or empty string
            return result.get('response', f"Error: {result.get('error', 'Unknown error')}")
    
    # Add the method to the class
    LLMEnforcer.generate_completion = generate_completion
    print("✅ Added generate_completion method to LLMEnforcer")

def test_patched_enforcer():
    """Test the patched enforcer"""
    from core.llm_enforcer import get_llm_enforcer
    
    enforcer = get_llm_enforcer()
    
    # Test the new method
    print("\nTesting generate_completion method...")
    try:
        response = enforcer.generate_completion(
            prompt="Say hello in exactly 5 words",
            max_tokens=20
        )
        print(f"✅ Method works! Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_patched_llm_enforcer_file():
    """Create a patched version of llm_enforcer.py with the method included"""
    
    patch_addition = '''
    def generate_completion(self, prompt, max_tokens=500, temperature=0.7, agent_name="Agent"):
        """
        Compatibility method for executors expecting generate_completion
        Maps to enforce_real_ai internally
        """
        result = self.enforce_real_ai(
            prompt=prompt,
            agent_name=agent_name,
            max_tokens=max_tokens,
            temperature=temperature,
            task_type="content"
        )
        
        # Return just the response text for compatibility
        if result['success']:
            return result['response']
        else:
            # Return error message or empty string
            return result.get('response', f"Error: {result.get('error', 'Unknown error')}")
'''
    
    # Read the original file
    with open('/Users/donkeyking/development/unified-donkey-betz/core/llm_enforcer.py', 'r') as f:
        content = f.read()
    
    # Find where to insert (after enforce_real_ai method)
    # Look for the end of enforce_real_ai method
    insert_marker = "    def get_usage_stats(self)"
    
    if insert_marker in content:
        # Insert the new method before get_usage_stats
        parts = content.split(insert_marker)
        new_content = parts[0] + patch_addition + "\n" + insert_marker + parts[1]
        
        # Save the patched version
        backup_path = '/Users/donkeyking/development/unified-donkey-betz/core/llm_enforcer_backup.py'
        patched_path = '/Users/donkeyking/development/unified-donkey-betz/core/llm_enforcer_patched.py'
        
        # Save backup
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {backup_path}")
        
        # Save patched version
        with open(patched_path, 'w') as f:
            f.write(new_content)
        print(f"✅ Created patched version: {patched_path}")
        
        print("\nTo apply the patch:")
        print("1. cp core/llm_enforcer.py core/llm_enforcer_original.py")
        print("2. cp core/llm_enforcer_patched.py core/llm_enforcer.py")
        print("3. python execute_test_agent.py --check")
        
        return True
    else:
        print("❌ Could not find insertion point in file")
        return False

if __name__ == "__main__":
    print("="*60)
    print("FIXING LLM ENFORCER")
    print("="*60)
    
    # Try runtime patching first
    print("\n1. Runtime Patching:")
    add_generate_completion_method()
    
    # Test it
    print("\n2. Testing Patch:")
    test_patched_enforcer()
    
    # Create patched file
    print("\n3. Creating Patched File:")
    create_patched_llm_enforcer_file()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("""
1. Apply the patch:
   cp core/llm_enforcer.py core/llm_enforcer_original.py
   cp core/llm_enforcer_patched.py core/llm_enforcer.py

2. Test the fix:
   python execute_test_agent.py --check
   
3. Execute an agent:
   python execute_test_agent.py

4. Activate all agents:
   python activate_all_agents.py
    """)
