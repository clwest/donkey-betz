# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test script to verify agent execution is working properly
"""
import requests
import json
import time

# API configuration
API_BASE = "http://localhost:8000/api/v1"
AUTH_TOKEN = "<redacted-993f8273-2026-04-20>"

def test_agent_execution():
    """Test executing an agent with proper task description"""
    
    # Prepare the request
    url = f"{API_BASE}/agents/execute/"
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Request data with proper task description
    data = {
        "agent_type": "betting-intelligence-analyzer",
        "agent_name": "Betting Intelligence Analyzer",
        "task": "Analyze the upcoming NFL game between Chiefs and Bills. Provide betting insights including spread analysis, total points prediction, and key factors that might influence the outcome.",
        "parameters": {
            "home_team": "Buffalo Bills",
            "away_team": "Kansas City Chiefs",
            "game_id": "test-game-001",
            "sport": "NFL"
        }
    }
    
    print("🚀 Testing agent execution with proper task description...")
    print(f"📝 Task: {data['task'][:100]}...")
    
    # Execute the agent
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Agent queued successfully!")
        print(f"   Execution ID: {result['execution_id']}")
        print(f"   Agent: {result['agent_name']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        
        # Wait a moment then check execution status
        execution_id = result['execution_id']
        print(f"\n⏳ Waiting 5 seconds for execution to start...")
        time.sleep(5)
        
        # Check execution status
        status_url = f"{API_BASE}/agents/executions/?execution_id={execution_id}"
        status_response = requests.get(status_url, headers=headers)
        
        if status_response.status_code == 200:
            executions = status_response.json().get('results', [])
            if executions:
                execution = executions[0]
                print(f"\n📊 Execution Status:")
                print(f"   Status: {execution['status']}")
                print(f"   Task Description: {execution['task_description'][:100] if execution['task_description'] else 'Empty'}")
                print(f"   Progress: {execution['progress_percentage']}%")
                print(f"   Started At: {execution.get('started_at', 'Not started')}")
                
                # Check if it's actually processing
                if execution['task_description']:
                    print(f"   ✅ Task description properly set!")
                else:
                    print(f"   ❌ Task description is empty - needs investigation")
                    
        return execution_id
    else:
        print(f"❌ Failed to execute agent: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT EXECUTION TEST")
    print("=" * 60)
    
    execution_id = test_agent_execution()
    
    if execution_id:
        print(f"\n💡 Monitor execution at:")
        print(f"   http://localhost:8000/api/v1/agents/executions/{execution_id}/")
        print(f"\n📊 Check Celery Flower for task status:")
        print(f"   http://localhost:5555/")