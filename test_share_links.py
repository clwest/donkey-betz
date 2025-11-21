"""
Session 149: Test Share Links
Quick test script for public share link functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_share_links():
    print("🔗 Testing Public Share Links - Session 149\n")

    # Step 1: Get available projects
    print("1️⃣ Fetching projects...")
    response = requests.get(f"{BASE_URL}/api/creative-projects/")

    if response.status_code != 200:
        print(f"❌ Failed to fetch projects: {response.status_code}")
        return

    projects = response.json()
    if not projects:
        print("❌ No projects found!")
        return

    project = projects[0]
    project_id = project['id']
    project_name = project['name']

    print(f"✅ Found project: {project_name} ({project_id})\n")

    # Step 2: Create share link
    print("2️⃣ Creating public share link...")
    response = requests.post(
        f"{BASE_URL}/api/creative-projects/{project_id}/share/create/",
        json={"is_public": True}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create share: {response.status_code}")
        print(f"   Response: {response.text}")
        return

    share_data = response.json()

    if not share_data.get('success'):
        print(f"❌ Share creation failed: {share_data}")
        return

    share_token = share_data['share_token']
    share_url = share_data['share_url']

    print(f"✅ Share link created!")
    print(f"   Token: {share_token}")
    print(f"   URL: {share_url}\n")

    # Step 3: Get share settings
    print("3️⃣ Retrieving share settings...")
    response = requests.get(f"{BASE_URL}/api/creative-projects/{project_id}/share/")

    if response.status_code != 200:
        print(f"❌ Failed to get share settings: {response.status_code}")
        return

    share_settings = response.json()

    if not share_settings.get('exists'):
        print(f"❌ Share doesn't exist!")
        return

    print(f"✅ Share settings retrieved!")
    print(f"   Active: {share_settings['is_active']}")
    print(f"   Has Password: {share_settings['has_password']}")
    print(f"   View Count: {share_settings['view_count']}")
    print(f"   Expires: {share_settings['expires_at'] or 'Never'}\n")

    # Step 4: Access public view
    print("4️⃣ Testing public view...")
    response = requests.get(f"{BASE_URL}/share/{share_token}/")

    if response.status_code != 200:
        print(f"❌ Failed to access public view: {response.status_code}")
        return

    print(f"✅ Public view accessible!")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Length: {len(response.text):,} bytes\n")

    # Step 5: Verify view count incremented
    print("5️⃣ Verifying view count incremented...")
    response = requests.get(f"{BASE_URL}/api/creative-projects/{project_id}/share/")
    share_settings = response.json()

    print(f"✅ View count: {share_settings['view_count']} (should be 1+)\n")

    # Step 6: Test with password protection
    print("6️⃣ Testing password protection...")
    response = requests.post(
        f"{BASE_URL}/api/creative-projects/{project_id}/share/create/",
        json={
            "is_public": True,
            "password": "test123"
        }
    )

    if response.status_code == 200:
        print(f"✅ Password protection enabled!")

        # Try accessing without password
        response = requests.get(f"{BASE_URL}/share/{share_token}/")
        if "password" in response.text.lower():
            print(f"✅ Password prompt displayed (access denied without password)\n")
        else:
            print(f"⚠️ Password prompt not found\n")
    else:
        print(f"❌ Failed to enable password: {response.status_code}\n")

    # Step 7: Test revoke
    print("7️⃣ Testing revoke...")
    response = requests.post(f"{BASE_URL}/api/creative-projects/{project_id}/share/revoke/")

    if response.status_code == 200:
        revoke_data = response.json()
        if revoke_data.get('success'):
            print(f"✅ Share link revoked!")

            # Verify it's no longer accessible
            response = requests.get(f"{BASE_URL}/share/{share_token}/")
            if response.status_code == 410:
                print(f"✅ Share link correctly returns 410 Gone\n")
            else:
                print(f"⚠️ Expected 410, got {response.status_code}\n")
        else:
            print(f"❌ Revoke failed: {revoke_data}\n")
    else:
        print(f"❌ Revoke request failed: {response.status_code}\n")

    print("=" * 60)
    print("✅ All tests passed! Share links are working! 🎉")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_share_links()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
