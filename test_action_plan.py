#!/usr/bin/env python
"""
Test script to verify action plan execution works
"""

import requests
import json
import time

# Test data
test_plan = {
    "plan": {
        "steps": [
            "Research content topics",
            "Create content calendar",
            "Write first article",
            "Publish and promote"
        ],
        "timeline": "1-2 weeks",
        "expected_outcome": "Generate first income from content",
        "resources": [
            {"name": "Content Guide", "url": "https://example.com/guide"}
        ]
    },
    "opportunity": {
        "id": "content-writing-001",
        "title": "AI-Assisted Content Writing Test"
    }
}

# Create and execute action plan
print("📋 Creating action plan...")
response = requests.post(
    "http://localhost:8000/api/v1/intelligence/income-builder/execute/",
    json=test_plan
)

if response.status_code == 201:
    data = response.json()
    print(f"✅ Action plan created!")
    print(f"   Plan ID: {data['plan_id']}")
    print(f"   Celery Task: {data['celery_task_id']}")
    print(f"   Status: {data['status']}")

    # Poll for status
    print("\n⏳ Polling for execution status...")
    for i in range(10):
        time.sleep(3)
        status_response = requests.get(
            "http://localhost:8000/api/v1/intelligence/income-builder/execute/"
        )
        if status_response.status_code == 200:
            plans = status_response.json()['plans']
            # Find our plan
            our_plan = next((p for p in plans if p['id'] == data['plan_id']), None)
            if our_plan:
                print(f"   Progress: {our_plan['progress']}% - Status: {our_plan['status']}")
                if our_plan['execution_logs']:
                    print("   Latest log:", our_plan['execution_logs'][-1]['message'])
                if our_plan['status'] == 'completed':
                    print("\n🎉 Action plan completed successfully!")
                    break
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())