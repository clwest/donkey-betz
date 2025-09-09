#!/usr/bin/env python
"""
Test script to verify agent execution is working properly.
"""

import os
import sys
import django
import json
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent

User = get_user_model()


def test_agent_execution():
    """Test the complete agent execution pipeline"""
    
    print("\n" + "="*60)
    print("AGENT EXECUTION TEST")
    print("="*60)
    
    # 1. Check if we have any agents
    agents = UnifiedAgentTemplate.objects.filter(is_active=True)
    print(f"\n✓ Found {agents.count()} active agents")
    
    if not agents.exists():
        print("❌ No agents found! Creating a test agent...")
        
        # Create a test agent
        test_agent = UnifiedAgentTemplate.objects.create(
            name="test-agent",
            display_name="Test Agent",
            description="A test agent for verification",
            specialization="research",
            capabilities=["test", "verification"],
            required_tools=[],
            system_prompt="You are a helpful test agent. Respond concisely.",
            llm_provider="openai",
            llm_model="gpt-4",
            llm_config={"temperature": 0.7, "max_tokens": 500},
            is_active=True,
            is_public=True
        )
        print(f"✓ Created test agent: {test_agent.name}")
        agent = test_agent
    else:
        agent = agents.first()
        print(f"✓ Using agent: {agent.name} ({agent.display_name})")
    
    # 2. Create a test user if needed
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.create_superuser(
            username='test_admin',
            email='test@example.com',
            password='test123'
        )
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    
    # 3. Create an execution
    import uuid
    execution_id = f"test_exec_{uuid.uuid4().hex[:8]}"
    
    print(f"\n📝 Creating execution: {execution_id}")
    execution = AgentExecution.objects.create(
        template=agent,
        user=user,
        execution_id=execution_id,
        task_description="Test task: What is 2+2?",
        task_type="test",
        context={"test": True},
        input_data={"question": "What is 2+2?"},
        priority="normal"
    )
    print(f"✓ Execution created with status: {execution.status}")
    
    # 4. Try to execute directly (synchronously for testing)
    print("\n🚀 Executing agent task...")
    
    try:
        # Try async execution first
        result = execute_agent.delay(execution_id=execution.execution_id)
        print(f"✓ Task queued with ID: {result.id}")
        
        # Wait for completion (max 30 seconds)
        print("\n⏳ Waiting for execution to complete...")
        max_wait = 30
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            execution.refresh_from_db()
            
            if execution.status in ['completed', 'failed']:
                break
                
            print(f"   Status: {execution.status} | Progress: {execution.progress_percentage}% | Step: {execution.current_step}")
            time.sleep(2)
        
    except Exception as e:
        print(f"⚠️  Async execution failed, trying synchronous: {e}")
        
        # Try synchronous execution as fallback
        try:
            result = execute_agent(execution_id=execution.execution_id)
            print(f"✓ Synchronous execution completed")
        except Exception as sync_error:
            print(f"❌ Synchronous execution also failed: {sync_error}")
            return False
    
    # 5. Check final status
    execution.refresh_from_db()
    print(f"\n📊 Final Status: {execution.status}")
    
    if execution.status == 'completed':
        print("✅ EXECUTION SUCCESSFUL!")
        if execution.result:
            print(f"\n📤 Result:")
            print(json.dumps(execution.result, indent=2))
        return True
        
    elif execution.status == 'failed':
        print("❌ EXECUTION FAILED!")
        if execution.error_message:
            print(f"Error: {execution.error_message}")
        return False
        
    else:
        print(f"⚠️  EXECUTION INCOMPLETE - Status: {execution.status}")
        return False


def check_celery_status():
    """Check if Celery is running"""
    print("\n🔍 Checking Celery status...")
    
    try:
        from celery import current_app
        from kombu import Connection
        
        # Check broker connection
        broker_url = current_app.conf.broker_url
        print(f"   Broker URL: {broker_url}")
        
        try:
            with Connection(broker_url) as conn:
                conn.ensure_connection(max_retries=1)
                print("   ✓ Broker connection: OK")
        except Exception as e:
            print(f"   ❌ Broker connection: FAILED - {e}")
            return False
        
        # Check if workers are running
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print(f"   ✓ Active workers: {len(stats)}")
            for worker, info in stats.items():
                print(f"      - {worker}")
        else:
            print("   ⚠️  No active workers found")
            print("   Run 'make celery-worker' in another terminal")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Celery check failed: {e}")
        return False


def main():
    """Main test function"""
    
    # Check Celery first
    celery_ok = check_celery_status()
    
    if not celery_ok:
        print("\n⚠️  Celery is not running properly!")
        print("Please start Celery worker with: make celery-worker")
        print("Continuing with direct execution test...\n")
    
    # Run the test
    success = test_agent_execution()
    
    print("\n" + "="*60)
    if success:
        print("✅ AGENT EXECUTION SYSTEM IS WORKING!")
    else:
        print("❌ AGENT EXECUTION SYSTEM HAS ISSUES")
        print("\nTroubleshooting:")
        print("1. Check if Redis is running: redis-cli ping")
        print("2. Start Celery worker: make celery-worker")
        print("3. Check API keys in .env file")
        print("4. Check logs for detailed errors")
    print("="*60 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())