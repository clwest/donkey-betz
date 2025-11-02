# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
WebSocket Stability Test
========================
Tests WebSocket connection stability under load
"""

import asyncio
import websockets
import json
import time
import statistics
from datetime import datetime

class WebSocketStabilityTest:
    def __init__(self):
        self.url = "ws://localhost:8000/ws/intelligence/"
        self.connection_times = []
        self.message_times = []
        self.errors = []
        self.successes = 0

    async def test_single_connection(self):
        """Test a single WebSocket connection"""
        try:
            start = time.time()
            async with websockets.connect(self.url) as websocket:
                connect_time = time.time() - start
                self.connection_times.append(connect_time)

                # Send test message
                msg_start = time.time()
                await websocket.send(json.dumps({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }))

                # Wait for response (with timeout)
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5.0
                    )
                    msg_time = time.time() - msg_start
                    self.message_times.append(msg_time)
                    self.successes += 1
                    return True
                except asyncio.TimeoutError:
                    self.errors.append("Response timeout")
                    return False

        except Exception as e:
            self.errors.append(str(e))
            return False

    async def test_concurrent_connections(self, num_connections=10):
        """Test multiple concurrent connections"""
        print(f"\n🔧 Testing {num_connections} concurrent WebSocket connections...")

        tasks = []
        for i in range(num_connections):
            tasks.append(self.test_single_connection())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if r is True)
        print(f"✅ Successful connections: {successful}/{num_connections}")

        return successful == num_connections

    async def test_rapid_reconnections(self, num_reconnections=5):
        """Test rapid connection/disconnection cycles"""
        print(f"\n🔄 Testing {num_reconnections} rapid reconnections...")

        for i in range(num_reconnections):
            success = await self.test_single_connection()
            if success:
                print(f"  Reconnection {i+1}/{num_reconnections}: ✅")
            else:
                print(f"  Reconnection {i+1}/{num_reconnections}: ❌")
            await asyncio.sleep(0.5)  # Brief pause between reconnections

        return len(self.errors) == 0

    async def test_sustained_load(self, duration_seconds=10, connections_per_second=2):
        """Test sustained WebSocket load"""
        print(f"\n⚡ Testing sustained load for {duration_seconds} seconds...")
        print(f"   ({connections_per_second} connections per second)")

        start_time = time.time()
        connection_count = 0

        while time.time() - start_time < duration_seconds:
            # Create connections at specified rate
            for _ in range(connections_per_second):
                asyncio.create_task(self.test_single_connection())
                connection_count += 1

            await asyncio.sleep(1.0)

        # Wait for remaining connections to complete
        await asyncio.sleep(2.0)

        print(f"   Total connections attempted: {connection_count}")
        print(f"   Successful connections: {self.successes}")

        success_rate = (self.successes / connection_count * 100) if connection_count > 0 else 0
        return success_rate > 80  # 80% success rate threshold

    def print_statistics(self):
        """Print test statistics"""
        print("\n📊 WebSocket Performance Statistics:")
        print("=" * 50)

        if self.connection_times:
            print(f"Connection Times:")
            print(f"  Average: {statistics.mean(self.connection_times)*1000:.2f}ms")
            print(f"  Min: {min(self.connection_times)*1000:.2f}ms")
            print(f"  Max: {max(self.connection_times)*1000:.2f}ms")
            if len(self.connection_times) > 1:
                print(f"  StdDev: {statistics.stdev(self.connection_times)*1000:.2f}ms")

        if self.message_times:
            print(f"\nMessage Round-Trip Times:")
            print(f"  Average: {statistics.mean(self.message_times)*1000:.2f}ms")
            print(f"  Min: {min(self.message_times)*1000:.2f}ms")
            print(f"  Max: {max(self.message_times)*1000:.2f}ms")
            if len(self.message_times) > 1:
                print(f"  StdDev: {statistics.stdev(self.message_times)*1000:.2f}ms")

        print(f"\nTotal Successful Connections: {self.successes}")
        print(f"Total Errors: {len(self.errors)}")

        if self.errors:
            print("\nError Summary:")
            error_counts = {}
            for error in self.errors:
                error_type = error.split(':')[0] if ':' in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1

            for error_type, count in error_counts.items():
                print(f"  {error_type}: {count}")

    async def run_all_tests(self):
        """Run all WebSocket stability tests"""
        print("\n🚀 Starting WebSocket Stability Tests")
        print("=" * 50)

        all_passed = True

        # Test 1: Concurrent connections
        passed = await self.test_concurrent_connections(10)
        all_passed = all_passed and passed

        # Test 2: Rapid reconnections
        passed = await self.test_rapid_reconnections(5)
        all_passed = all_passed and passed

        # Test 3: Sustained load
        passed = await self.test_sustained_load(10, 2)
        all_passed = all_passed and passed

        # Print statistics
        self.print_statistics()

        # Final verdict
        print("\n" + "=" * 50)
        if all_passed:
            print("✅ ALL WEBSOCKET STABILITY TESTS PASSED!")
            print("WebSockets are stable and ready for production.")
        else:
            print("⚠️ Some WebSocket stability tests failed.")
            print("Review the statistics above for details.")

        return all_passed


async def main():
    """Main test runner"""
    tester = WebSocketStabilityTest()
    success = await tester.run_all_tests()

    # Return exit code
    import sys
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())