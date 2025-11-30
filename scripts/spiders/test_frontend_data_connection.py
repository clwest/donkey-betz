# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test Frontend Data Connection
============================
Verify that the frontend can actually get real data from our systems
"""

import sys
import os
import json
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from api_unified_learning_dashboard import dashboard_api

def test_frontend_data_flow():
    """Test all the data the frontend needs"""
    print("🔍 Testing Frontend Data Connection")
    print("=" * 60)

    # Test 1: Learning Overview
    print("1. Testing Learning Overview Data...")
    learning_data = dashboard_api.get_learning_overview()
    print(f"   ✅ Total Learnings: {learning_data['totalLearnings']}")
    print(f"   ✅ Code Solutions: {learning_data['codeSolutions']}")
    print(f"   ✅ Market Intelligence: {learning_data['marketIntelligence']}")
    print(f"   ✅ Intelligence Level: {learning_data['intelligenceLevel']}%")

    # Test 2: Collaboration Data
    print("\n2. Testing Collaboration Data...")
    collab_data = dashboard_api.get_collaboration_data()
    print(f"   ✅ Active Agents: {collab_data['activeAgents']}")
    print(f"   ✅ Teaching Sessions: {collab_data['teachingSessions']}")
    print(f"   ✅ Collaboration Score: {collab_data['collaborationScore']}%")
    print(f"   ✅ Recent Collaborations: {len(collab_data['recentCollaborations'])}")

    # Test 3: Cost Data
    print("\n3. Testing Cost Data...")
    cost_data = dashboard_api.get_cost_metrics()
    print(f"   ✅ Total Cost: ${cost_data['totalCost']:.2f}")
    print(f"   ✅ Learning Cost: ${cost_data['learningCost']:.2f}")
    print(f"   ✅ Cost per Learning: ${cost_data['costPerLearning']:.3f}")

    # Test 4: System Health
    print("\n4. Testing System Health...")
    health_data = dashboard_api.get_system_health()
    print(f"   ✅ Redis Keys: {health_data['redisKeys']}")
    print(f"   ✅ Spider Opportunities: {health_data['spiderOpportunities']}")
    print(f"   ✅ Active Connections: {health_data['activeConnections']}")

    # Test 5: Learning Feed
    print("\n5. Testing Learning Feed...")
    feed_data = dashboard_api.get_learning_feed()
    print(f"   ✅ Feed Items: {len(feed_data)}")
    if feed_data:
        print(f"   ✅ Latest: {feed_data[0]['content'][:50]}...")

    # Test 6: All Dashboard Data (what frontend would call)
    print("\n6. Testing Complete Dashboard Data API...")
    all_data = dashboard_api.get_all_dashboard_data()
    print(f"   ✅ All data keys: {list(all_data.keys())}")
    print(f"   ✅ Timestamp: {all_data['timestamp']}")

    print("\n🎉 Frontend Data Connection Test Complete!")
    print("=" * 60)

    # Return data for inspection
    return all_data

def create_test_api_endpoint():
    """Create a simple API endpoint to test frontend connection"""
    print("\n🔧 Creating Test API Endpoint...")

    test_endpoint_code = '''
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api_unified_learning_dashboard import dashboard_api

@csrf_exempt
@require_http_methods(["GET"])
def test_dashboard_data(request):
    """Test endpoint for frontend data"""
    try:
        data = dashboard_api.get_all_dashboard_data()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def test_learning_data(request):
    """Test endpoint for learning data only"""
    try:
        data = dashboard_api.get_learning_overview()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
'''

    # Write the test endpoints file
    with open('/Users/donkeyking/development/unified-donkey-betz/test_api_endpoints.py', 'w') as f:
        f.write(test_endpoint_code)

    print("   ✅ Created test_api_endpoints.py")
    print("   ✅ Add these to your URLs to test frontend connection")

def simulate_frontend_api_calls():
    """Simulate what the frontend JavaScript would do"""
    print("\n📱 Simulating Frontend API Calls...")

    # Simulate the fetch calls the frontend makes
    endpoints = [
        '/api/dashboard/learning',
        '/api/dashboard/collaboration',
        '/api/dashboard/costs',
        '/api/dashboard/health',
        '/api/dashboard/feed'
    ]

    for endpoint in endpoints:
        print(f"   🔗 Frontend would call: {endpoint}")

        # Simulate the data that endpoint should return
        if 'learning' in endpoint:
            data = dashboard_api.get_learning_overview()
        elif 'collaboration' in endpoint:
            data = dashboard_api.get_collaboration_data()
        elif 'costs' in endpoint:
            data = dashboard_api.get_cost_metrics()
        elif 'health' in endpoint:
            data = dashboard_api.get_system_health()
        elif 'feed' in endpoint:
            data = dashboard_api.get_learning_feed()

        print(f"   ✅ Would return: {len(str(data))} characters of data")

    print("   ⚠️  Frontend currently has fallback data because these endpoints don't exist yet!")

if __name__ == "__main__":
    # Run all tests
    data = test_frontend_data_flow()
    create_test_api_endpoint()
    simulate_frontend_api_calls()

    print("\n🎯 DIAGNOSIS:")
    print("1. Data is available ✅")
    print("2. API endpoints need to be created ❌")
    print("3. Frontend is using fallback data ⚠️")
    print("\nNext: Create Django API endpoints for the frontend to call!")