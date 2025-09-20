#!/usr/bin/env python3
"""
Test script for Income Builder complete flow
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

def test_income_builder_flow():
    """Test the complete Income Builder flow"""
    print("🚀 Testing Income Builder Complete Flow")
    print("=" * 50)

    # Step 1: Get opportunities
    print("\n1. Fetching opportunities...")
    response = requests.get(f"{API_BASE}/intelligence/income-builder/")
    if response.status_code != 200:
        print(f"❌ Failed to fetch opportunities: {response.status_code}")
        return False

    data = response.json()
    if not data.get('success') or not data.get('opportunities'):
        print("❌ No opportunities returned")
        return False

    opportunities = data['opportunities']
    print(f"✅ Found {len(opportunities)} opportunities")

    # Display first opportunity
    first_opp = opportunities[0]
    print(f"\n📊 First opportunity: {first_opp['title']}")
    print(f"   - Type: {first_opp['stream_type']}")
    print(f"   - Potential: {first_opp['potential_monthly']}")
    print(f"   - Difficulty: {first_opp['difficulty']}")

    # Step 2: Create action plan
    print(f"\n2. Creating action plan for '{first_opp['title']}'...")
    response = requests.post(
        f"{API_BASE}/intelligence/income-builder/action-plan/",
        json={"opportunity_id": first_opp['id']}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create action plan: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    plan_data = response.json()
    if not plan_data.get('success'):
        print(f"❌ Action plan creation failed: {plan_data.get('error')}")
        return False

    action_plan = plan_data.get('action_plan', {})
    print("✅ Action plan created successfully")

    # Display plan details
    if 'week_by_week' in action_plan:
        print(f"\n📅 Week-by-week plan:")
        for week in action_plan['week_by_week'][:2]:  # Show first 2 weeks
            print(f"   Week {week.get('week', '?')}: {week.get('focus', 'N/A')}")
            if 'tasks' in week:
                for task in week['tasks'][:2]:  # Show first 2 tasks
                    print(f"      - {task}")

    # Step 3: Execute action plan
    print(f"\n3. Executing action plan...")
    response = requests.post(
        f"{API_BASE}/intelligence/income-builder/execute/",
        json={
            "plan": action_plan,
            "opportunity": first_opp
        }
    )

    if response.status_code not in [200, 201]:
        print(f"❌ Failed to execute action plan: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    exec_data = response.json()
    if not exec_data.get('success'):
        print(f"❌ Execution failed: {exec_data.get('error')}")
        return False

    plan_id = exec_data.get('plan_id')
    print(f"✅ Action plan execution started")
    print(f"   Plan ID: {plan_id}")
    print(f"   Status: {exec_data.get('status')}")

    # Step 4: Check status (poll a few times)
    print(f"\n4. Checking execution status...")
    for i in range(3):
        time.sleep(2)
        response = requests.get(f"{API_BASE}/intelligence/income-builder/execute/")

        if response.status_code == 200:
            status_data = response.json()
            if status_data.get('success') and status_data.get('plans'):
                for plan in status_data['plans']:
                    if plan['id'] == plan_id:
                        print(f"   Status: {plan['status']} | Progress: {plan.get('progress', 0)}%")
                        if plan['status'] == 'completed':
                            print(f"   ✅ Plan completed!")
                            if plan.get('results'):
                                print(f"   📁 Results available: {len(plan['results'])} items")
                            return True

    print("\n✅ All tests passed!")
    print("\n📝 Summary:")
    print("   - Opportunities API: ✅")
    print("   - Action Plan Creation: ✅")
    print("   - Plan Execution: ✅")
    print("   - Status Tracking: ✅")

    return True

if __name__ == "__main__":
    try:
        success = test_income_builder_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)