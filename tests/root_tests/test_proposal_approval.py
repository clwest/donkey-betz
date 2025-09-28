#!/usr/bin/env python
"""Test proposal approval endpoint with authentication"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test credentials
USERNAME = "admin"
PASSWORD = "admin123"

def test_proposal_approval():
    """Test the proposal approval endpoint with authentication"""

    # Create a session to maintain cookies
    session = requests.Session()

    # Step 1: Get CSRF token first
    print("1. Getting CSRF token from login page...")
    login_page = session.get(f"{BASE_URL}/accounts/login/")
    csrf_token = session.cookies.get('csrftoken')

    # Step 2: Login to get session cookie
    print("2. Logging in to get session cookie...")
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }

    login_response = session.post(f"{BASE_URL}/accounts/login/", data=login_data, allow_redirects=False)

    if login_response.status_code in [302, 200]:
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed with status {login_response.status_code}")
        return False

    # Step 3: Get list of proposals
    print("3. Fetching proposals...")
    proposals_response = session.get(f"{BASE_URL}/api/proposals/?status=all")

    if proposals_response.status_code == 200:
        proposals_data = proposals_response.json()
        if proposals_data.get('success') and proposals_data.get('proposals'):
            proposals = proposals_data['proposals']
            print(f"   ✅ Found {len(proposals)} proposals")

            if proposals:
                # Get the first pending proposal
                pending_proposals = [p for p in proposals if p.get('status') == 'pending']
                if pending_proposals:
                    test_proposal = pending_proposals[0]
                    proposal_id = test_proposal['id']
                    print(f"   📋 Testing with proposal: {test_proposal['title']}")

                    # Step 4: Test approval endpoint
                    print(f"4. Testing approval for proposal {proposal_id}...")

                    headers = {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token if csrf_token else ''
                    }

                    approval_data = {
                        'proposal_id': proposal_id
                    }

                    approval_response = session.post(
                        f"{BASE_URL}/api/proposals/approve/",
                        headers=headers,
                        json=approval_data
                    )

                    if approval_response.status_code == 200:
                        result = approval_response.json()
                        if result.get('success'):
                            print("   ✅ Proposal approved successfully!")
                            print(f"      Message: {result.get('message')}")
                            if result.get('execution_result'):
                                print(f"      Execution: {result['execution_result'].get('message')}")
                            return True
                        else:
                            print(f"   ❌ Approval failed: {result.get('error')}")
                    else:
                        print(f"   ❌ HTTP {approval_response.status_code}: {approval_response.text[:200]}")
                else:
                    print("   ⚠️  No pending proposals to test")
            else:
                print("   ⚠️  No proposals available")
        else:
            print(f"   ❌ Failed to get proposals: {proposals_data}")
    else:
        print(f"   ❌ Failed to fetch proposals: HTTP {proposals_response.status_code}")

    return False

if __name__ == "__main__":
    print("🔧 Testing Proposal Approval Endpoint with Authentication")
    print("=" * 60)

    success = test_proposal_approval()

    print("=" * 60)
    if success:
        print("✨ SUCCESS! Proposal approval endpoint is working!")
    else:
        print("⚠️  Test completed with issues. Check the logs above.")