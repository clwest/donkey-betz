#!/usr/bin/env python3
"""
AGENT EXECUTION TEST SCRIPT
Execute agents and verify they produce results
"""
import os
import sys
import django
import json
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone

from agents.models import UnifiedAgentTemplate, AgentExecution, AgentStatus
from agents.tasks import execute_agent
from core.llm_enforcer import LLMEnforcer
from django.contrib.auth import get_user_model

User = get_user_model()

def execute_single_agent(agent_name, task_description, input_data=None):
    """Execute a single agent and monitor its progress"""
    
    print(f"\n{'='*60}")
    print(f"EXECUTING: {agent_name}")
    print(f"{'='*60}")
    
    try:
        # Get the agent template
        agent = UnifiedAgentTemplate.objects.get(name=agent_name)
        print(f"✅ Found agent: {agent.name}")
        print(f"   Specialization: {agent.specialization}")
        print(f"   Capabilities: {agent.capabilities}")
        
        # Get or create a test user
        user = User.objects.filter(username='test_user').first()
        if not user:
            user = User.objects.create_user(
                username='test_user',
                email='test@donkeybetz.com'
            )
            print(f"✅ Created test user")
        
        # Create an execution
        execution = AgentExecution.objects.create(
            template=agent,
            user=user,
            task_description=task_description,
            task_type=agent.specialization,
            input_data=input_data or {},
            status=AgentStatus.INITIALIZING,
            priority=1,
            context={
                'test_execution': True,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        print(f"✅ Created execution: {execution.execution_id}")
        
        # Try to execute synchronously first (for testing)
        print(f"⏳ Executing agent...")
        
        # Check if we have the content executor for this agent
        if agent.name == 'donkey-betz-content-creator' or agent.specialization == 'content_creation':
            from agents.content_executor import DonkeyBetzContentExecutor
            executor = DonkeyBetzContentExecutor()
            
            print("📝 Using DonkeyBetzContentExecutor")
            result = executor.execute_content_creation(
                str(execution.id),
                {
                    'task': task_description,
                    'content_type': 'blog_post',
                    'target_audience': 'sports betting enthusiasts',
                    'tone': 'engaging and informative',
                    **input_data
                }
            )
            
            print("✅ Execution completed!")
            print(f"Result: {json.dumps(result, indent=2)[:500]}...")
            
        else:
            # Try the universal executor
            from agents.universal_llm_executor import UniversalLLMExecutor
            executor = UniversalLLMExecutor()
            
            print("🤖 Using UniversalLLMExecutor")
            result = executor.execute(
                execution_id=str(execution.id),
                agent_template=agent,
                task_data={
                    'task': task_description,
                    **input_data
                }
            )
            
            print("✅ Execution completed!")
            print(f"Result: {json.dumps(result, indent=2)[:500]}...")
        
        # Refresh execution from database
        execution.refresh_from_db()
        
        # Show final status
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   Status: {execution.status}")
        print(f"   Progress: {execution.progress_percentage}%")
        print(f"   Result: {execution.result}")
        print(f"   Output Data: {execution.output_data}")
        print(f"   LLM Response: {execution.llm_response[:200] if execution.llm_response else 'None'}...")
        print(f"   Errors: {execution.error_message}")
        
        return execution
        
    except UnifiedAgentTemplate.DoesNotExist:
        print(f"❌ Agent '{agent_name}' not found!")
        print("Available agents:")
        for agent in UnifiedAgentTemplate.objects.all()[:10]:
            print(f"  - {agent.name} ({agent.specialization})")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def execute_multiple_agents():
    """Test multiple different agents"""
    
    test_cases = [
        {
            'agent': 'content-creator',
            'task': 'Write a blog post about the future of AI in sports betting',
            'data': {'word_count': 500}
        },
        {
            'agent': 'business-agent',
            'task': 'Analyze the market opportunity for a sports betting platform',
            'data': {'focus': 'competitive analysis'}
        },
        {
            'agent': 'seo-specialist-agent',
            'task': 'Generate SEO keywords for a sports betting website',
            'data': {'target_market': 'USA', 'sport': 'NFL'}
        }
    ]
    
    results = []
    for test in test_cases:
        try:
            execution = execute_single_agent(
                test['agent'],
                test['task'],
                test['data']
            )
            results.append(execution)
            time.sleep(2)  # Pause between executions
        except Exception as e:
            print(f"Failed to execute {test['agent']}: {e}")
    
    return results


def check_execution_infrastructure():
    """Check if all execution components are properly configured"""
    
    print("\n" + "="*60)
    print("INFRASTRUCTURE CHECK")
    print("="*60)
    
    # Check LLM Enforcer
    try:
        llm = LLMEnforcer()
        print("✅ LLM Enforcer initialized")
        
        # Test a simple LLM call
        response = llm.generate_completion(
            prompt="Say 'Hello, Donkey Betz!' in 5 words or less",
            max_tokens=20
        )
        print(f"   Test response: {response}")
    except Exception as e:
        print(f"❌ LLM Enforcer error: {e}")
    
    # Check executors
    executors = [
        'content_executor.DonkeyBetzContentExecutor',
        'universal_llm_executor.UniversalLLMExecutor',
    ]
    
    for executor_path in executors:
        try:
            module, class_name = executor_path.rsplit('.', 1)
            exec(f"from agents.{module} import {class_name}")
            print(f"✅ {executor_path} available")
        except Exception as e:
            print(f"❌ {executor_path} not available: {e}")
    
    # Check Celery (if configured)
    try:
        from celery import current_app
        stats = current_app.control.inspect().stats()
        if stats:
            print(f"✅ Celery workers available: {list(stats.keys())}")
        else:
            print("⚠️ No Celery workers running (synchronous execution only)")
    except Exception as e:
        print(f"⚠️ Celery not configured: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Execute and test agents')
    parser.add_argument('--agent', type=str, help='Specific agent to execute')
    parser.add_argument('--task', type=str, default='Generate a test response', help='Task description')
    parser.add_argument('--check', action='store_true', help='Check infrastructure only')
    parser.add_argument('--multi', action='store_true', help='Execute multiple agents')
    
    args = parser.parse_args()
    
    if args.check:
        check_execution_infrastructure()
    elif args.multi:
        execute_multiple_agents()
    elif args.agent:
        execute_single_agent(args.agent, args.task)
    else:
        # Default: execute content creator
        execute_single_agent(
            'donkey-betz-content-creator',
            'Write an engaging introduction to Donkey Betz platform',
            {'tone': 'exciting', 'length': 'short'}
        )
