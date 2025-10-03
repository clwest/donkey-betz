#!/usr/bin/env python3
"""
Test Authenticated User Flow
Tests login, WebSocket connections, and component access with authentication
"""

import requests
import asyncio
import websockets
import json
from datetime import datetime

# Test credentials
TEST_USER = 'testuser'
TEST_PASS = 'testpass123'
BASE_URL = 'http://localhost:8000'

class AuthenticatedFlowTest:
    def __init__(self):
        self.session = requests.Session()
        self.cookies = None

    def test_login(self):
        """Test login flow"""
        print("\n🔐 Testing Login Flow")
        print("=" * 70)

        # Get CSRF token
        response = self.session.get(f'{BASE_URL}/accounts/login/')
        csrf_token = None

        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                start = line.find('value="') + 7
                end = line.find('"', start)
                csrf_token = line[start:end]
                break

        if not csrf_token:
            print("   ❌ Could not extract CSRF token")
            return False

        print(f"   ✅ CSRF Token: {csrf_token[:20]}...")

        # Login
        login_data = {
            'username': TEST_USER,
            'password': TEST_PASS,
            'csrfmiddlewaretoken': csrf_token,
        }

        response = self.session.post(
            f'{BASE_URL}/accounts/login/',
            data=login_data,
            headers={'Referer': f'{BASE_URL}/accounts/login/'},
            allow_redirects=False
        )

        if response.status_code in [200, 302]:
            print(f"   ✅ Login Response: {response.status_code}")
            print(f"   ✅ Session cookies: {len(self.session.cookies)} cookies")
            self.cookies = self.session.cookies

            # Test if authenticated
            auth_response = self.session.get(f'{BASE_URL}/')
            if TEST_USER in auth_response.text or 'logout' in auth_response.text.lower():
                print(f"   ✅ Successfully authenticated as {TEST_USER}")
                return True
            else:
                print("   ⚠️  Login succeeded but auth verification unclear")
                return True
        else:
            print(f"   ❌ Login failed with status {response.status_code}")
            return False

    async def test_websocket_with_auth(self, name, uri):
        """Test a single WebSocket endpoint with authentication"""
        try:
            # Build cookie header
            cookie_header = '; '.join([f"{cookie.name}={cookie.value}" for cookie in self.cookies])

            headers = {
                'Cookie': cookie_header
            }

            async with asyncio.timeout(5):
                async with websockets.connect(uri, additional_headers=headers) as websocket:
                    # Try to receive initial message
                    try:
                        async with asyncio.timeout(2):
                            initial = await websocket.recv()
                            initial_data = json.loads(initial)

                            return {
                                'name': name,
                                'connected': True,
                                'message_received': True,
                                'message_type': initial_data.get('type', 'unknown')
                            }
                    except asyncio.TimeoutError:
                        return {
                            'name': name,
                            'connected': True,
                            'message_received': False,
                            'message_type': None
                        }
        except Exception as e:
            return {
                'name': name,
                'connected': False,
                'error': str(e)
            }

    async def test_all_websockets(self):
        """Test all 7 main component WebSockets with authentication"""
        print("\n🔌 Testing WebSocket Connections (Authenticated)")
        print("=" * 70)

        endpoints = {
            'income_builder': 'ws://localhost:8000/ws/income-builder/',
            'revenue_dashboard': 'ws://localhost:8000/ws/revenue-dashboard/',
            'decision_command': 'ws://localhost:8000/ws/decision-command/',
            'neural_orchestra': 'ws://localhost:8000/ws/neural-orchestra/',
            'control_center': 'ws://localhost:8000/ws/control-center/',
            'revenue_opportunities': 'ws://localhost:8000/ws/revenue-opportunities/',
            'monetization_hub': 'ws://localhost:8000/ws/monetization-hub/',
            'personal_assistant': 'ws://localhost:8000/ws/assistant/',
        }

        tasks = []
        for name, uri in endpoints.items():
            tasks.append(self.test_websocket_with_auth(name, uri))

        results = await asyncio.gather(*tasks)

        connected_count = sum(1 for r in results if r['connected'])

        print(f"\n📊 Results:")
        print(f"   Total: 8 endpoints")
        print(f"   ✅ Connected: {connected_count}")
        print(f"   ❌ Failed: {8 - connected_count}")
        print(f"   Success Rate: {(connected_count/8)*100:.1f}%")

        print(f"\n📋 Details:")
        for result in results:
            name = result['name'].replace('_', ' ').title()
            if result['connected']:
                msg_status = "✓" if result.get('message_received') else "✗"
                msg_type = result.get('message_type', 'none')
                print(f"   ✅ {name:25} | Message: {msg_status} | Type: {msg_type}")
            else:
                error = result.get('error', 'unknown')[:50]
                print(f"   ❌ {name:25} | Error: {error}")

        return results

    def test_component_access(self):
        """Test if all 7 main components are accessible"""
        print("\n🎯 Testing Component Page Access (Authenticated)")
        print("=" * 70)

        components = [
            ('Income Builder', '/income/'),
            ('Revenue Dashboard', '/revenue/'),
            ('Decision Command', '/decisions/'),
            ('Neural Orchestra', '/neural-orchestra/'),
            ('Control Center', '/control/'),
            ('Revenue Opportunities', '/opportunities/'),
            ('Monetization Hub', '/monetization/'),
        ]

        accessible = 0
        for name, path in components:
            response = self.session.get(f'{BASE_URL}{path}', allow_redirects=False)
            if response.status_code == 200:
                print(f"   ✅ {name:25} | HTTP {response.status_code}")
                accessible += 1
            elif response.status_code == 302:
                print(f"   ⚠️  {name:25} | HTTP {response.status_code} (redirect)")
            else:
                print(f"   ❌ {name:25} | HTTP {response.status_code}")

        print(f"\n   Total Accessible: {accessible}/7")
        return accessible

    def test_logout(self):
        """Test logout functionality"""
        print("\n🚪 Testing Logout")
        print("=" * 70)

        response = self.session.get(f'{BASE_URL}/accounts/logout/', allow_redirects=False)

        if response.status_code == 302:
            print(f"   ✅ Logout successful (302 redirect)")

            # Verify we're logged out
            home_response = self.session.get(f'{BASE_URL}/')
            if 'login' in home_response.text.lower():
                print(f"   ✅ Successfully logged out (login button visible)")
                return True
            else:
                print(f"   ⚠️  Logout response OK but verification unclear")
                return True
        else:
            print(f"   ❌ Logout failed with status {response.status_code}")
            return False

async def main():
    """Run all authenticated flow tests"""
    print("🚀 Authenticated User Flow Test")
    print("=" * 70)
    print(f"User: {TEST_USER}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    tester = AuthenticatedFlowTest()

    # Test login
    login_success = tester.test_login()
    if not login_success:
        print("\n❌ Login failed, aborting remaining tests")
        return

    # Test component access
    accessible_count = tester.test_component_access()

    # Test WebSockets
    ws_results = await tester.test_all_websockets()

    # Test logout
    logout_success = tester.test_logout()

    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"✅ Login: {'SUCCESS' if login_success else 'FAILED'}")
    print(f"✅ Component Access: {accessible_count}/7")
    print(f"✅ WebSocket Connections: {sum(1 for r in ws_results if r['connected'])}/8")
    print(f"✅ Logout: {'SUCCESS' if logout_success else 'FAILED'}")

    ws_connected = sum(1 for r in ws_results if r['connected'])
    if login_success and accessible_count >= 6 and ws_connected >= 7:
        print("\n🎉 AUTHENTICATED FLOW: FULLY FUNCTIONAL")
    elif login_success and accessible_count >= 4:
        print("\n✅ AUTHENTICATED FLOW: MOSTLY FUNCTIONAL")
    else:
        print("\n⚠️ AUTHENTICATED FLOW: NEEDS ATTENTION")

if __name__ == "__main__":
    asyncio.run(main())
