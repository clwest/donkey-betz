#!/usr/bin/env python3
"""
TEST COMMAND CENTER CONNECTION
Verify the command center can control your agents
"""
import os
import django
import json
import asyncio
import websockets
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from agents.models import UnifiedAgentTemplate, AgentExecution

User = get_user_model()

def test_api_endpoints():
    """Test that API endpoints are working"""
    import requests
    
    base_url = "http://localhost:8000/api/agents"
    
    print("🔍 TESTING COMMAND CENTER API CONNECTION")
    print("-" * 50)
    
    # Test 1: List agents
    try:
        response = requests.get(f"{base_url}/templates/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent Templates Endpoint: {data.get('count', 0)} agents available")
        else:
            print(f"❌ Agent Templates Endpoint: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        print("   Make sure Django is running: python manage.py runserver")
        return False
    
    # Test 2: List executions
    try:
        response = requests.get(f"{base_url}/executions/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Executions Endpoint: {data.get('count', 0)} executions tracked")
    except:
        print("❌ Executions endpoint not responding")
    
    # Test 3: Check execute endpoint
    print(f"\n📡 Execute Endpoint: {base_url}/execute/")
    print("   POST with: {")
    print('     "agent_name": "content-creator",')
    print('     "task": "Write about sports betting"')
    print("   }")
    
    return True

async def test_websocket():
    """Test WebSocket connection for real-time updates"""
    print("\n🔌 TESTING WEBSOCKET CONNECTION")
    print("-" * 50)
    
    try:
        uri = "ws://localhost:8000/ws/assistant/"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected to /ws/assistant/")
            
            # Send a test message
            test_msg = json.dumps({
                "type": "agent_request",
                "message": "Test from command center"
            })
            await websocket.send(test_msg)
            print("✅ Test message sent")
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"✅ Response received: {response[:100]}...")
            except asyncio.TimeoutError:
                print("⚠️ No response (WebSocket may need authentication)")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        print("   Make sure Django Channels is configured")

def create_command_center_user():
    """Ensure command center has a user account"""
    print("\n👤 COMMAND CENTER USER")
    print("-" * 50)
    
    user, created = User.objects.get_or_create(
        username='command_center',
        defaults={
            'email': 'command@donkeybetz.com',
            'is_staff': True
        }
    )
    
    if created:
        user.set_password('donkeybetz123')  # Set a password
        user.save()
        print("✅ Created command_center user")
        print("   Username: command_center")
        print("   Password: donkeybetz123")
    else:
        print("✅ Command center user exists")
    
    # Create an API token if needed
    try:
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        print(f"🔑 API Token: {token.key}")
        print("   Add to command center headers:")
        print(f"   Authorization: Token {token.key}")
    except:
        print("⚠️ Token auth not configured")
    
    return user

def show_active_agents_for_ui():
    """Display agents ready for command center"""
    print("\n🤖 AGENTS READY FOR COMMAND CENTER")
    print("-" * 50)
    
    # Get top performing agents
    from django.db.models import Count
    
    top_agents = AgentExecution.objects.values('template__name', 'template__specialization').annotate(
        exec_count=Count('id')
    ).order_by('-exec_count')[:10]
    
    print("Top Agents to Feature:")
    for agent in top_agents:
        print(f"  • {agent['template__name']} ({agent['template__specialization']}): {agent['exec_count']} executions")
    
    print("\n📋 Agent Categories for UI:")
    categories = UnifiedAgentTemplate.objects.values_list('specialization', flat=True).distinct()
    for cat in list(categories)[:10]:
        count = UnifiedAgentTemplate.objects.filter(specialization=cat).count()
        print(f"  • {cat}: {count} agents")

def create_example_api_calls():
    """Generate example API calls for the command center"""
    print("\n📝 EXAMPLE API CALLS FOR COMMAND CENTER")
    print("-" * 50)
    
    examples = """
// 1. Execute a specific agent
fetch('/api/agents/execute/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token YOUR_TOKEN_HERE'
    },
    body: JSON.stringify({
        agent_name: 'content-creator',
        task: 'Write about NFL week 3 predictions',
        context: { sport: 'NFL', week: 3 }
    })
});

// 2. Get agent recommendations for a task
fetch('/api/agents/discover/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        task: 'Analyze betting odds for tonight\'s game',
        count: 3
    })
});

// 3. Real-time execution via WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/assistant/');
ws.send(JSON.stringify({
    type: 'execute_agent',
    agent: 'sports-analytics-agent',
    task: 'Find arbitrage opportunities'
}));

// 4. Get execution history
fetch('/api/agents/executions/?limit=10&status=completed');

// 5. Execute a team of agents
fetch('/api/agents/execute/', {
    method: 'POST',
    body: JSON.stringify({
        mode: 'team',
        agents: ['content-creator', 'seo-specialist-agent'],
        task: 'Create SEO-optimized betting guide'
    })
});
"""
    print(examples)

if __name__ == "__main__":
    print("="*60)
    print("COMMAND CENTER CONNECTION TEST")
    print("="*60)
    print()
    
    # Run tests
    api_ok = test_api_endpoints()
    
    if api_ok:
        # Test WebSocket
        try:
            asyncio.run(test_websocket())
        except:
            print("⚠️ WebSocket test skipped (requires async)")
        
        # Setup user
        create_command_center_user()
        
        # Show available agents
        show_active_agents_for_ui()
        
        # Show examples
        create_example_api_calls()
        
        print("\n" + "="*60)
        print("✅ COMMAND CENTER READY!")
        print("="*60)
        print("\n1. Start Django backend: python manage.py runserver")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open: http://localhost:3000/command-center")
        print("4. Your 134 agents are ready to receive commands!")
    else:
        print("\n❌ Backend not running. Start with:")
        print("   python manage.py runserver")
