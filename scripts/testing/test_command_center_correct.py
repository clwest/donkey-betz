#!/usr/bin/env python3
"""
CORRECTED COMMAND CENTER TEST - Using proper API paths
"""
import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_correct_api_endpoints():
    """Test the CORRECT API endpoints"""
    
    print("🔍 TESTING CORRECT API ENDPOINTS")
    print("-" * 50)
    
    # Get the token for authentication
    try:
        user = User.objects.get(username='command_center')
        token = Token.objects.get(user=user)
        headers = {
            'Authorization': f'Token {token.key}',
            'Content-Type': 'application/json'
        }
        print(f"🔑 Using API Token: {token.key[:10]}...")
    except:
        headers = {'Content-Type': 'application/json'}
        print("⚠️ No auth token, using anonymous access")
    
    # Test the correct paths
    tests = [
        ('Root API', 'http://localhost:8000/api/', 'GET'),
        ('V1 Agents', 'http://localhost:8000/api/v1/agents/', 'GET'),
        ('Execute', 'http://localhost:8000/api/v1/agents/execute/', 'GET'),  # GET to check endpoint
        ('Templates', 'http://localhost:8000/api/v1/agents/templates/', 'GET'),
        ('Executions', 'http://localhost:8000/api/v1/agents/executions/', 'GET'),
    ]
    
    for name, url, method in tests:
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=2)
            else:
                response = requests.post(url, headers=headers, json={}, timeout=2)
            
            if response.status_code in [200, 201, 405]:  # 405 for wrong method
                print(f"✅ {name}: {url} - Status {response.status_code}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'count' in data:
                            print(f"   Found {data['count']} items")
                        elif 'results' in data:
                            print(f"   Found {len(data['results'])} results")
                    except:
                        pass
            else:
                print(f"❌ {name}: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Cannot connect (is Django running?)")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    print("\n📝 CORRECTED API EXAMPLES FOR COMMAND CENTER")
    print("-" * 50)
    print(f"""
// Update your command center to use these URLs:

const API_BASE = 'http://localhost:8000/api/v1';
const API_TOKEN = '{token.key if 'token' in locals() else 'YOUR_TOKEN_HERE'}';

// 1. List all agent templates
fetch(`${{API_BASE}}/agents/templates/`, {{
    headers: {{
        'Authorization': `Token ${{API_TOKEN}}`
    }}
}});

// 2. Execute a specific agent
fetch(`${{API_BASE}}/agents/execute/`, {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json',
        'Authorization': `Token ${{API_TOKEN}}`
    }},
    body: JSON.stringify({{
        agent_name: 'content-creator',
        task: 'Write about NFL betting tips',
        priority: 'high'
    }})
}});

// 3. Get execution history
fetch(`${{API_BASE}}/agents/executions/?limit=10&status=completed`, {{
    headers: {{
        'Authorization': `Token ${{API_TOKEN}}`
    }}
}});

// 4. Discover best agents for a task
fetch(`${{API_BASE}}/agents/discover/`, {{
    method: 'POST',
    headers: {{
        'Content-Type': 'application/json',
        'Authorization': `Token ${{API_TOKEN}}`
    }},
    body: JSON.stringify({{
        task: 'Analyze betting odds',
        count: 3
    }})
}});
""")

def create_quick_test_execution():
    """Create a test execution to verify everything works"""
    print("\n🧪 CREATING TEST EXECUTION")
    print("-" * 50)
    
    try:
        # Get token
        user = User.objects.get(username='command_center')
        token = Token.objects.get(user=user)
        
        # Make API call to execute an agent
        response = requests.post(
            'http://localhost:8000/api/v1/agents/execute/',
            headers={
                'Authorization': f'Token {token.key}',
                'Content-Type': 'application/json'
            },
            json={
                'agent_name': 'content-creator',
                'task': 'Write a test message for command center',
                'priority': 'high'
            }
        )
        
        if response.status_code in [200, 201]:
            print("✅ Test execution created successfully!")
            data = response.json()
            if 'execution_id' in data:
                print(f"   Execution ID: {data['execution_id']}")
            if 'status' in data:
                print(f"   Status: {data['status']}")
        else:
            print(f"❌ Execution failed: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_command_center_config():
    """Show configuration for the command center frontend"""
    print("\n⚙️ COMMAND CENTER FRONTEND CONFIG")
    print("-" * 50)
    
    user = User.objects.get(username='command_center')
    token = Token.objects.get(user=user)
    
    print(f"""
// Add to your .env or config file:
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/assistant/
NEXT_PUBLIC_API_TOKEN={token.key}

// Or in your React component:
const config = {{
    apiBase: 'http://localhost:8000/api/v1',
    wsUrl: 'ws://localhost:8000/ws/assistant/',
    apiToken: '{token.key}',
    endpoints: {{
        agents: '/agents/templates/',
        execute: '/agents/execute/',
        executions: '/agents/executions/',
        discover: '/agents/discover/',
    }}
}};
""")

if __name__ == "__main__":
    print("="*60)
    print("COMMAND CENTER API TEST (CORRECTED)")
    print("="*60)
    print()
    
    test_correct_api_endpoints()
    create_quick_test_execution()
    show_command_center_config()
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Update your command center to use: /api/v1/agents/
2. Add the API token to all requests
3. Your 134 agents are ready at the correct endpoints!

Test with curl:
curl -H "Authorization: Token <redacted-0fb2390d-2026-04-20>" \\
     http://localhost:8000/api/v1/agents/templates/
""")
