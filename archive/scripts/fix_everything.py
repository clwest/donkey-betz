#!/usr/bin/env python3
"""
🔧 COMPLETE FIX SCRIPT
Automatically fixes the LLM Enforcer issue and tests the solution
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from core.llm_enforcer import LLMEnforcer, get_llm_enforcer
from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate, AgentExecution, AgentStatus

User = get_user_model()


def patch_llm_enforcer():
    """Add the missing generate_completion method to LLMEnforcer"""
    
    print("\n🔧 PATCHING LLM ENFORCER")
    print("-" * 40)
    
    # Check if method already exists
    if hasattr(LLMEnforcer, 'generate_completion'):
        print("✅ generate_completion method already exists!")
        return True
    
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
    
    return True


def test_llm_enforcer():
    """Test that the LLM Enforcer works correctly"""
    
    print("\n🧪 TESTING LLM ENFORCER")
    print("-" * 40)
    
    enforcer = get_llm_enforcer()
    
    # Test 1: Check if clients are initialized
    stats = enforcer.get_usage_stats()
    print(f"OpenAI Available: {stats['openai_available']}")
    print(f"Anthropic Available: {stats['anthropic_available']}")
    
    if not stats['openai_available'] and not stats['anthropic_available']:
        print("❌ No LLM providers available! Check your API keys.")
        return False
    
    # Test 2: Test enforce_real_ai method
    print("\nTesting enforce_real_ai...")
    try:
        result = enforcer.enforce_real_ai(
            prompt="Respond with exactly: 'LLM Test Success'",
            agent_name="test_agent",
            max_tokens=20
        )
        if result['success']:
            print(f"✅ enforce_real_ai works: {result['response'][:50]}")
        else:
            print(f"❌ enforce_real_ai failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Error calling enforce_real_ai: {e}")
        return False
    
    # Test 3: Test generate_completion method (after patching)
    print("\nTesting generate_completion...")
    try:
        response = enforcer.generate_completion(
            prompt="Respond with exactly: 'Method Test Success'",
            max_tokens=20
        )
        print(f"✅ generate_completion works: {response[:50]}")
        return True
    except AttributeError as e:
        print(f"❌ generate_completion not found: {e}")
        print("   Attempting to patch...")
        if patch_llm_enforcer():
            # Try again after patching
            try:
                response = enforcer.generate_completion(
                    prompt="Respond with exactly: 'Method Test Success'",
                    max_tokens=20
                )
                print(f"✅ generate_completion works after patch: {response[:50]}")
                return True
            except Exception as e2:
                print(f"❌ Still failed after patch: {e2}")
                return False
        return False
    except Exception as e:
        print(f"❌ Error calling generate_completion: {e}")
        return False


def test_agent_execution():
    """Test actual agent execution with the fixed LLM"""
    
    print("\n🤖 TESTING AGENT EXECUTION")
    print("-" * 40)
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='fix_test_user',
        defaults={'email': 'fix@donkeybetz.com'}
    )
    
    # Find content creator agent
    try:
        agent = UnifiedAgentTemplate.objects.get(name='content-creator')
    except:
        # Try alternative names
        agent = UnifiedAgentTemplate.objects.filter(
            specialization__icontains='content'
        ).first()
    
    if not agent:
        print("❌ No content agent found")
        return False
    
    print(f"Using agent: {agent.name}")
    
    # Create execution
    execution = AgentExecution.objects.create(
        template=agent,
        user=user,
        task_description="Write a test message in exactly 10 words",
        task_type='content_creation',
        status=AgentStatus.INITIALIZING
    )
    
    print(f"Created execution: {execution.execution_id}")
    
    # Try to execute with the content executor
    try:
        from agents.content_executor import DonkeyBetzContentExecutor
        executor = DonkeyBetzContentExecutor()
        
        # Patch the executor's LLM enforcer if needed
        if not hasattr(executor.llm_enforcer, 'generate_completion'):
            print("   Patching executor's LLM enforcer...")
            patch_llm_enforcer()
            # Reinitialize executor to get patched enforcer
            executor = DonkeyBetzContentExecutor()
        
        result = executor.execute_content_creation(
            str(execution.id),
            {'task': 'Write a test message', 'content_type': 'test'}
        )
        
        if result.get('success'):
            print(f"✅ Execution succeeded!")
            print(f"   Content: {result.get('content', '')[:100]}")
            
            # Check if result was saved
            execution.refresh_from_db()
            if execution.result or execution.output_data:
                print("✅ Results saved to database!")
            else:
                print("⚠️ Execution succeeded but results not saved")
            
            return True
        else:
            print(f"❌ Execution failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Execution error: {e}")
        import traceback
        traceback.print_exc()
        return False


def apply_permanent_fix():
    """Apply permanent fix to the LLM Enforcer file"""
    
    print("\n📝 APPLYING PERMANENT FIX")
    print("-" * 40)
    
    file_path = '/Users/donkeyking/development/unified-donkey-betz/core/llm_enforcer.py'
    
    # Read current content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if generate_completion already exists
    if 'def generate_completion' in content:
        print("✅ generate_completion method already in file")
        return True
    
    # Add the method after enforce_real_ai
    method_code = '''
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
            return result.get('response', f"Error: {result.get('error', 'Unknown error')}")
'''
    
    # Find insertion point (before get_usage_stats)
    marker = "    def get_usage_stats(self)"
    if marker in content:
        parts = content.split(marker)
        new_content = parts[0] + method_code + "\n" + marker + parts[1]
        
        # Backup original
        backup_path = file_path.replace('.py', '_original.py')
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✅ Backed up to: {backup_path}")
        
        # Write fixed version
        with open(file_path, 'w') as f:
            f.write(new_content)
        print("✅ Applied permanent fix to llm_enforcer.py")
        
        return True
    else:
        print("❌ Could not find insertion point")
        return False


def main():
    """Main execution flow"""
    
    print("="*60)
    print("🔧 LLM ENFORCER FIX SCRIPT")
    print("="*60)
    
    # Step 1: Apply runtime patch
    patch_success = patch_llm_enforcer()
    
    # Step 2: Test LLM Enforcer
    test_success = test_llm_enforcer()
    
    if not test_success:
        print("\n❌ LLM Enforcer tests failed!")
        print("Check your API keys in .env file:")
        print("  OPENAI_API_KEY=sk-...")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return False
    
    # Step 3: Test agent execution
    exec_success = test_agent_execution()
    
    # Step 4: Apply permanent fix if everything works
    if test_success and exec_success:
        print("\n✅ All tests passed!")
        
        response = input("\nApply permanent fix to llm_enforcer.py? (y/n): ")
        if response.lower() == 'y':
            apply_permanent_fix()
    
    # Final summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    print(f"✅ Runtime Patch: {'Success' if patch_success else 'Failed'}")
    print(f"✅ LLM Tests: {'Passed' if test_success else 'Failed'}")
    print(f"✅ Agent Execution: {'Working' if exec_success else 'Failed'}")
    
    if test_success and exec_success:
        print("\n🎉 SYSTEM FIXED! You can now:")
        print("1. Execute individual agents: python execute_test_agent.py")
        print("2. Activate all agents: python activate_all_agents.py")
    else:
        print("\n⚠️ Some issues remain. Check the errors above.")
    
    return test_success and exec_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
