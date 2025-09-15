#!/usr/bin/env python3
"""
End-to-End Test for Decision Command Feature

This test verifies that the complete Decision Command workflow works:
1. WebSocket connection
2. Analyze opportunities
3. Select opportunity
4. Create action plan
5. HTTP API endpoints
"""

import asyncio
import websockets
import json
import requests
import time
import sys

class DecisionCommandTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.ws_url = f"ws://localhost:8000/ws/income-builder/"
        self.test_results = []

    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })

    async def test_websocket_connection(self):
        """Test WebSocket connection and basic functionality"""
        try:
            async with websockets.connect(self.ws_url) as ws:
                # Test connection message
                initial_msg = await asyncio.wait_for(ws.recv(), timeout=5)
                initial_data = json.loads(initial_msg)

                if initial_data.get('type') == 'connection':
                    self.log_test("WebSocket Connection", True, "Connected successfully")
                else:
                    self.log_test("WebSocket Connection", False, f"Unexpected initial message: {initial_data}")
                    return False

                return ws
        except Exception as e:
            self.log_test("WebSocket Connection", False, str(e))
            return None

    async def test_analyze_opportunities(self, ws):
        """Test analyze opportunities functionality"""
        try:
            # Send analyze opportunities request
            test_profile = {
                "type": "analyze_opportunities",
                "profile": {
                    "id": "test_user",
                    "current_balance": 500.0,
                    "skills": ["writing", "ai", "python", "marketing"],
                    "skill_level": "intermediate",
                    "available_hours": 25
                }
            }

            await ws.send(json.dumps(test_profile))

            # Get response with longer timeout for AI processing
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            response_data = json.loads(response)

            if response_data.get('type') == 'opportunities_analysis':
                opportunities = response_data.get('top_opportunities', [])
                if len(opportunities) > 0:
                    self.log_test("Analyze Opportunities", True,
                                f"Found {len(opportunities)} opportunities")
                    return opportunities
                else:
                    self.log_test("Analyze Opportunities", False,
                                "No opportunities returned")
                    return []
            else:
                self.log_test("Analyze Opportunities", False,
                            f"Unexpected response type: {response_data.get('type')}")
                return []

        except asyncio.TimeoutError:
            self.log_test("Analyze Opportunities", False, "Timeout waiting for AI response (30s)")
            return []
        except websockets.exceptions.ConnectionClosed as e:
            self.log_test("Analyze Opportunities", False, f"WebSocket connection closed: {e}")
            return []
        except Exception as e:
            self.log_test("Analyze Opportunities", False, f"Unexpected error: {str(e)}")
            return []

    async def test_select_opportunity(self, ws, opportunities):
        """Test opportunity selection"""
        if not opportunities:
            self.log_test("Select Opportunity", False, "No opportunities to select")
            return None

        try:
            # Select first opportunity
            first_opp = opportunities[0]
            select_msg = {
                "type": "select_opportunity",
                "opportunity_id": first_opp.get('id', 'content_writing')
            }

            await ws.send(json.dumps(select_msg))

            # Get response
            response = await asyncio.wait_for(ws.recv(), timeout=15)
            response_data = json.loads(response)

            if response_data.get('type') == 'action_plan':
                plan = response_data.get('plan')
                if plan:
                    self.log_test("Select Opportunity", True,
                                f"Generated action plan for: {first_opp.get('title', 'Unknown')}")
                    return plan
                else:
                    self.log_test("Select Opportunity", False, "No plan in response")
                    return None
            else:
                self.log_test("Select Opportunity", False,
                            f"Unexpected response type: {response_data.get('type')}")
                return None

        except Exception as e:
            self.log_test("Select Opportunity", False, str(e))
            return None

    def test_http_endpoints(self):
        """Test HTTP API endpoints"""
        # Test opportunities endpoint
        try:
            response = requests.get(f"{self.base_url}/api/v1/intelligence/income-builder/",
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('opportunities'):
                    self.log_test("HTTP Opportunities Endpoint", True,
                                f"Retrieved {len(data['opportunities'])} opportunities")
                else:
                    self.log_test("HTTP Opportunities Endpoint", False,
                                "Invalid response format")
            else:
                self.log_test("HTTP Opportunities Endpoint", False,
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("HTTP Opportunities Endpoint", False, str(e))

        # Test action plan endpoint
        try:
            plan_data = {"opportunity_id": "content_writing"}
            response = requests.post(f"{self.base_url}/api/v1/intelligence/income-builder/action-plan/",
                                   json=plan_data, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("HTTP Action Plan Endpoint", True,
                                "Action plan created successfully")
                else:
                    self.log_test("HTTP Action Plan Endpoint", False,
                                f"API returned error: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("HTTP Action Plan Endpoint", False,
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("HTTP Action Plan Endpoint", False, str(e))

    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 DECISION COMMAND END-TO-END TEST")
        print("=" * 50)

        # Test WebSocket connection
        ws = await self.test_websocket_connection()
        if not ws:
            print("❌ Cannot continue tests without WebSocket connection")
            return False

        try:
            # Test analyze opportunities
            opportunities = await self.test_analyze_opportunities(ws)

            # Test opportunity selection
            if opportunities:
                plan = await self.test_select_opportunity(ws, opportunities)

        except Exception as e:
            print(f"❌ WebSocket tests failed: {e}")

        finally:
            # Close WebSocket
            if ws:
                await ws.close()

        # Test HTTP endpoints
        print("\n🌐 Testing HTTP endpoints...")
        self.test_http_endpoints()

        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)

        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")

        print(f"\n🎯 Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Decision Command is fully operational!")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

async def main():
    tester = DecisionCommandTester()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)