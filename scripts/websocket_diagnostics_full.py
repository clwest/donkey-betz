#!/usr/bin/env python3
"""
Complete WebSocket Diagnostics for Unified Platform
Tests all 7 main components + critical infrastructure endpoints
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, List, Tuple
import time

# Define all critical WebSocket endpoints
ENDPOINTS = {
    # 7 Main Components
    'income_builder': 'ws://localhost:8000/ws/income-builder/',
    'revenue_dashboard': 'ws://localhost:8000/ws/revenue-dashboard/',
    'decision_command': 'ws://localhost:8000/ws/decision-command/',
    'neural_orchestra': 'ws://localhost:8000/ws/neural-orchestra/',
    'control_center': 'ws://localhost:8000/ws/control-center/',
    'revenue_opportunities': 'ws://localhost:8000/ws/revenue-opportunities/',
    'monetization_hub': 'ws://localhost:8000/ws/monetization-hub/',

    # Infrastructure
    'personal_assistant': 'ws://localhost:8000/ws/assistant/',
    'sports_hub': 'ws://localhost:8000/ws/sports/',
    'ai_nexus': 'ws://localhost:8000/ws/ai-nexus/',

    # Test endpoints
    'echo_test': 'ws://localhost:8000/ws/test/echo/',
    'generic': 'ws://localhost:8000/ws/',
}

class WebSocketDiagnostics:
    def __init__(self):
        self.results = {}
        self.total_tested = 0
        self.successful = 0
        self.failed = 0

    async def test_endpoint(self, name: str, uri: str, timeout: int = 5) -> Dict:
        """Test a single WebSocket endpoint"""
        result = {
            'name': name,
            'uri': uri,
            'connected': False,
            'message_received': False,
            'ping_pong_works': False,
            'error': None,
            'connection_time': None,
            'initial_message': None
        }

        start_time = time.time()

        try:
            async with asyncio.timeout(timeout):
                async with websockets.connect(uri) as websocket:
                    connection_time = time.time() - start_time
                    result['connected'] = True
                    result['connection_time'] = f"{connection_time:.2f}s"

                    # Try to receive initial message
                    try:
                        async with asyncio.timeout(2):
                            initial = await websocket.recv()
                            result['message_received'] = True
                            try:
                                result['initial_message'] = json.loads(initial)
                            except:
                                result['initial_message'] = initial[:100]
                    except asyncio.TimeoutError:
                        result['message_received'] = False

                    # Try ping-pong
                    try:
                        async with asyncio.timeout(2):
                            await websocket.send(json.dumps({"type": "ping"}))
                            pong = await websocket.recv()
                            result['ping_pong_works'] = True
                    except:
                        result['ping_pong_works'] = False

        except asyncio.TimeoutError:
            result['error'] = 'Connection timeout'
        except websockets.exceptions.InvalidStatusCode as e:
            result['error'] = f'HTTP {e.status_code}'
        except Exception as e:
            result['error'] = str(e)

        return result

    async def run_all_tests(self):
        """Run tests on all endpoints"""
        print("🚀 Starting WebSocket Diagnostics...")
        print("=" * 70)

        tasks = []
        for name, uri in ENDPOINTS.items():
            tasks.append(self.test_endpoint(name, uri))

        results = await asyncio.gather(*tasks)

        # Process results
        for result in results:
            self.results[result['name']] = result
            self.total_tested += 1
            if result['connected']:
                self.successful += 1
            else:
                self.failed += 1

        self.print_results()
        self.save_results()

    def print_results(self):
        """Print formatted results"""
        print("\n" + "=" * 70)
        print("📊 WEBSOCKET DIAGNOSTIC RESULTS")
        print("=" * 70)

        # Summary
        success_rate = (self.successful / self.total_tested * 100) if self.total_tested > 0 else 0
        print(f"\n📈 Summary:")
        print(f"   Total Tested: {self.total_tested}")
        print(f"   ✅ Successful: {self.successful}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   Success Rate: {success_rate:.1f}%")

        # Main Components
        print(f"\n🎯 Main Components (7):")
        main_components = [
            'income_builder', 'revenue_dashboard', 'decision_command',
            'neural_orchestra', 'control_center', 'revenue_opportunities',
            'monetization_hub'
        ]

        for name in main_components:
            result = self.results[name]
            self._print_endpoint_result(result)

        # Infrastructure
        print(f"\n🔧 Infrastructure:")
        infra = ['personal_assistant', 'sports_hub', 'ai_nexus', 'echo_test', 'generic']
        for name in infra:
            result = self.results[name]
            self._print_endpoint_result(result)

    def _print_endpoint_result(self, result: Dict):
        """Print a single endpoint result"""
        name = result['name'].replace('_', ' ').title()
        status = "✅" if result['connected'] else "❌"

        print(f"\n   {status} {name}")
        print(f"      URI: {result['uri']}")

        if result['connected']:
            print(f"      Connection Time: {result['connection_time']}")
            print(f"      Initial Message: {'✓' if result['message_received'] else '✗'}")
            print(f"      Ping/Pong: {'✓' if result['ping_pong_works'] else '✗'}")
            if result['initial_message']:
                msg = result['initial_message']
                if isinstance(msg, dict):
                    print(f"      Message Type: {msg.get('type', 'unknown')}")
        else:
            print(f"      Error: {result['error']}")

    def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"websocket_diagnostic_{timestamp}.json"

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tested': self.total_tested,
                'successful': self.successful,
                'failed': self.failed,
                'success_rate': f"{(self.successful / self.total_tested * 100):.1f}%"
            },
            'results': self.results
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Results saved to: {filename}")

    async def check_redis_connections(self):
        """Check active WebSocket connections in Redis"""
        import subprocess

        print("\n" + "=" * 70)
        print("🔍 REDIS WEBSOCKET ANALYSIS")
        print("=" * 70)

        try:
            # Count WebSocket-related keys
            result = subprocess.run(
                ['redis-cli', 'keys', 'websocket:*'],
                capture_output=True,
                text=True
            )
            ws_keys = result.stdout.strip().split('\n') if result.stdout.strip() else []

            result = subprocess.run(
                ['redis-cli', 'keys', 'asgi:*'],
                capture_output=True,
                text=True
            )
            asgi_keys = result.stdout.strip().split('\n') if result.stdout.strip() else []

            result = subprocess.run(
                ['redis-cli', 'keys', 'channel:*'],
                capture_output=True,
                text=True
            )
            channel_keys = result.stdout.strip().split('\n') if result.stdout.strip() else []

            print(f"\n📊 Redis Key Counts:")
            print(f"   websocket:* keys: {len([k for k in ws_keys if k])}")
            print(f"   asgi:* keys: {len([k for k in asgi_keys if k])}")
            print(f"   channel:* keys: {len([k for k in channel_keys if k])}")

            if ws_keys and ws_keys[0]:
                print(f"\n🔑 WebSocket Keys:")
                for key in ws_keys[:10]:
                    if key:
                        print(f"      {key}")

        except Exception as e:
            print(f"   ⚠️  Could not query Redis: {e}")

async def main():
    """Main diagnostic runner"""
    diagnostics = WebSocketDiagnostics()

    # Run WebSocket tests
    await diagnostics.run_all_tests()

    # Check Redis
    await diagnostics.check_redis_connections()

    print("\n" + "=" * 70)
    print("✅ Diagnostics Complete!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
