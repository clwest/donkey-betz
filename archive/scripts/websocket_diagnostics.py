#!/usr/bin/env python3
"""
WebSocket Connection Diagnostics Tool
Systematically tests all WebSocket endpoints to identify data flow failures
"""

import asyncio
import websockets
import json
import sys
import time
from datetime import datetime

# Backend WebSocket endpoints to test
ENDPOINTS = [
    # Intelligence Module (Income Builder & Revenue)
    "ws://localhost:8000/ws/income-builder/",
    "ws://localhost:8000/ws/revenue-income/",

    # Decision Command Center
    "ws://localhost:8000/ws/decision/",
    "ws://localhost:8000/ws/decisions/",
    "ws://localhost:8000/ws/command-center/",

    # Neural Orchestra
    "ws://localhost:8000/ws/orchestra/",
    "ws://localhost:8000/ws/agents/",
    "ws://localhost:8000/ws/agents/execution/",
    "ws://localhost:8000/ws/agents/orchestration/",

    # Core system endpoints
    "ws://localhost:8000/ws/dashboard/",
    "ws://localhost:8000/ws/notifications/",
    "ws://localhost:8000/ws/test/echo/",
]

class WebSocketTester:
    def __init__(self):
        self.results = {}

    async def test_endpoint(self, url, timeout=10):
        """Test a single WebSocket endpoint"""
        result = {
            'url': url,
            'connected': False,
            'can_send': False,
            'receives_data': False,
            'error': None,
            'response_data': None,
            'connection_time': None,
        }

        start_time = time.time()

        try:
            print(f"Testing {url}...")

            # Try to connect
            async with websockets.connect(url, timeout=timeout) as websocket:
                connection_time = time.time() - start_time
                result['connected'] = True
                result['connection_time'] = connection_time
                print(f"  ✅ Connected in {connection_time:.2f}s")

                # Test sending a message
                test_messages = [
                    # Generic ping
                    {"type": "ping", "timestamp": datetime.now().isoformat()},

                    # Endpoint-specific messages
                    {"type": "get_status"} if "income-builder" in url else None,
                    {"action": "analyze_opportunities", "profile": {"current_balance": 0}} if "decision" in url else None,
                    {"type": "get_network_state"} if "orchestra" in url else None,
                    {"type": "echo", "message": "test"} if "test" in url else None,
                ]

                # Filter out None messages
                test_messages = [msg for msg in test_messages if msg is not None]

                for message in test_messages:
                    try:
                        await websocket.send(json.dumps(message))
                        result['can_send'] = True
                        print(f"  ✅ Sent message: {message['type']}")

                        # Wait for response
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5)
                            result['receives_data'] = True
                            result['response_data'] = response
                            print(f"  ✅ Received response: {response[:100]}...")
                            break  # Success with first message
                        except asyncio.TimeoutError:
                            print(f"  ⚠️ No response to {message['type']} within 5s")
                            continue

                    except Exception as e:
                        print(f"  ❌ Failed to send {message['type']}: {e}")
                        continue

                # If no response from any message, try waiting for spontaneous data
                if not result['receives_data']:
                    print("  ⏳ Waiting for spontaneous data...")
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=3)
                        result['receives_data'] = True
                        result['response_data'] = response
                        print(f"  ✅ Received spontaneous data: {response[:100]}...")
                    except asyncio.TimeoutError:
                        print("  ⚠️ No spontaneous data received")

        except websockets.exceptions.ConnectionClosed as e:
            result['error'] = f"Connection closed: {e}"
            print(f"  ❌ Connection closed: {e}")

        except websockets.exceptions.InvalidURI as e:
            result['error'] = f"Invalid URI: {e}"
            print(f"  ❌ Invalid URI: {e}")

        except websockets.exceptions.InvalidStatusCode as e:
            result['error'] = f"Invalid status code: {e}"
            print(f"  ❌ Invalid status code: {e}")

        except ConnectionRefusedError as e:
            result['error'] = f"Connection refused: {e}"
            print(f"  ❌ Connection refused - server not running?")

        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
            print(f"  ❌ Unexpected error: {e}")

        return result

    async def test_all_endpoints(self):
        """Test all endpoints in parallel"""
        print(f"🔍 Testing {len(ENDPOINTS)} WebSocket endpoints...\n")

        tasks = [self.test_endpoint(url) for url in ENDPOINTS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Store results
        for result in results:
            if isinstance(result, Exception):
                print(f"Task failed: {result}")
                continue
            self.results[result['url']] = result

    def generate_report(self):
        """Generate detailed diagnostic report"""
        print("\n" + "="*80)
        print("🔍 WEBSOCKET DIAGNOSTIC REPORT")
        print("="*80)

        total = len(self.results)
        connected = sum(1 for r in self.results.values() if r['connected'])
        can_send = sum(1 for r in self.results.values() if r['can_send'])
        receives_data = sum(1 for r in self.results.values() if r['receives_data'])

        print(f"\n📊 SUMMARY:")
        print(f"  Total endpoints tested: {total}")
        print(f"  Successfully connected: {connected}/{total} ({connected/total*100:.1f}%)")
        print(f"  Can send messages: {can_send}/{total} ({can_send/total*100:.1f}%)")
        print(f"  Receives data: {receives_data}/{total} ({receives_data/total*100:.1f}%)")

        print(f"\n✅ WORKING ENDPOINTS:")
        working = [r for r in self.results.values() if r['connected'] and r['receives_data']]
        if working:
            for result in working:
                print(f"  • {result['url']} - Full bidirectional communication")
        else:
            print("  None! 🚨 No endpoints have full data flow")

        print(f"\n⚠️ PARTIALLY WORKING ENDPOINTS:")
        partial = [r for r in self.results.values() if r['connected'] and not r['receives_data']]
        if partial:
            for result in partial:
                status = "connects" + (", sends" if result['can_send'] else ", can't send") + ", no responses"
                print(f"  • {result['url']} - {status}")
        else:
            print("  None")

        print(f"\n❌ BROKEN ENDPOINTS:")
        broken = [r for r in self.results.values() if not r['connected']]
        if broken:
            for result in broken:
                print(f"  • {result['url']} - {result['error']}")
        else:
            print("  None")

        print(f"\n🔧 RECOMMENDED FIXES:")

        if not working:
            print("  ⚡ CRITICAL: No endpoints provide data updates!")
            print("     - Frontend components will show no live data")
            print("     - Need to implement WebSocket data providers")

        if broken:
            print(f"  🔌 {len(broken)} endpoints completely unreachable:")
            print("     - Check if Django server is running on port 8000")
            print("     - Verify WebSocket routing configuration")
            print("     - Check consumer implementations exist")

        if partial:
            print(f"  📡 {len(partial)} endpoints connect but don't send data:")
            print("     - Consumers may not be implementing message handlers")
            print("     - Backend may not be sending periodic updates")
            print("     - Need to add real data streaming logic")

        # Component-specific analysis
        print(f"\n🧩 COMPONENT IMPACT ANALYSIS:")

        component_endpoints = {
            "Income Builder": ["ws://localhost:8000/ws/income-builder/"],
            "Revenue Dashboard": ["ws://localhost:8000/ws/revenue-income/"],
            "Decision Command": ["ws://localhost:8000/ws/decision/", "ws://localhost:8000/ws/decisions/"],
            "Neural Orchestra": ["ws://localhost:8000/ws/orchestra/", "ws://localhost:8000/ws/agents/"],
        }

        for component, endpoints in component_endpoints.items():
            component_working = any(
                self.results.get(ep, {}).get('receives_data', False)
                for ep in endpoints
            )
            status = "✅ WORKING" if component_working else "❌ NO DATA FLOW"
            print(f"  • {component}: {status}")

            if not component_working:
                for ep in endpoints:
                    result = self.results.get(ep, {})
                    if result.get('connected') and not result.get('receives_data'):
                        print(f"    - {ep}: connects but no data")
                    elif not result.get('connected'):
                        print(f"    - {ep}: connection failed - {result.get('error', 'unknown')}")

        return {
            'total': total,
            'connected': connected,
            'working': len(working),
            'partial': len(partial),
            'broken': len(broken),
            'component_status': {
                component: any(
                    self.results.get(ep, {}).get('receives_data', False)
                    for ep in endpoints
                )
                for component, endpoints in component_endpoints.items()
            }
        }

async def main():
    tester = WebSocketTester()
    await tester.test_all_endpoints()
    summary = tester.generate_report()

    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"websocket_diagnostic_report_{timestamp}.json"

    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'detailed_results': tester.results
        }, f, indent=2)

    print(f"\n📄 Detailed results saved to: {report_file}")

    # Exit with error code if major issues found
    if summary['working'] == 0:
        print("\n🚨 CRITICAL: No WebSocket endpoints provide data flow!")
        print("   Frontend components will not receive real-time updates.")
        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Diagnostic failed: {e}")
        sys.exit(1)