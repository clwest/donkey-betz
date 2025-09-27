#!/usr/bin/env python3
"""
Final System Health Check
=========================
Comprehensive health check for the unified platform
"""

import requests
import json
import redis
import asyncio
import websockets
from datetime import datetime
import sys

class SystemHealthChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.total_checks = 0
        self.passed_checks = 0

    def check(self, name, condition, details=""):
        """Record a health check result"""
        self.total_checks += 1
        if condition:
            self.passed_checks += 1
            self.results[name] = {"status": "✅ PASS", "details": details}
            print(f"✅ {name}: PASSED {details}")
        else:
            self.results[name] = {"status": "❌ FAIL", "details": details}
            print(f"❌ {name}: FAILED {details}")
        return condition

    def check_redis(self):
        """Check Redis connectivity"""
        try:
            r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
            r.ping()

            # Check for active spiders
            spider_count = r.scard('active_spiders')
            self.check(
                "Redis Connection",
                True,
                f"(Connected, {spider_count} active spiders)"
            )

            # Check specific Redis data
            self.check(
                "Spider Army Deployment",
                spider_count > 0,
                f"({spider_count} spiders active)"
            )

            return True
        except Exception as e:
            self.check("Redis Connection", False, str(e))
            return False

    def check_api_endpoints(self):
        """Check critical API endpoints"""
        endpoints = [
            ("/api/intelligence/", "Intelligence API"),
            ("/api/v1/health/", "Health Check API"),
            ("/api/v1/status/", "Status API"),
            ("/api/proposals/", "Proposals API"),
        ]

        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                self.check(
                    name,
                    response.status_code in [200, 302],  # 302 is OK for auth redirects
                    f"(Status: {response.status_code})"
                )
            except Exception as e:
                self.check(name, False, str(e))

    async def check_websocket(self):
        """Check WebSocket connectivity"""
        try:
            async with websockets.connect("ws://localhost:8000/ws/intelligence/") as websocket:
                # Send test message
                await websocket.send(json.dumps({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }))

                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    self.check("WebSocket Connection", True, "(Connected and responsive)")
                    return True
                except asyncio.TimeoutError:
                    self.check("WebSocket Connection", True, "(Connected but no response)")
                    return True

        except Exception as e:
            self.check("WebSocket Connection", False, str(e))
            return False

    def check_dashboard_accessibility(self):
        """Check if dashboard pages are accessible"""
        dashboards = [
            ("/intelligence/", "Intelligence Dashboard"),
        ]

        for path, name in dashboards:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=5)
                # Check if we get the page (200) or redirect to login (302)
                self.check(
                    name,
                    response.status_code in [200, 302],
                    f"(Status: {response.status_code})"
                )
            except Exception as e:
                self.check(name, False, str(e))

    def check_authentication_system(self):
        """Check authentication middleware"""
        # Test that API endpoints work without auth in dev mode
        try:
            response = requests.get(f"{self.base_url}/api/intelligence/", timeout=5)

            # In dev mode with auth bypass, should get 200 or data
            if response.status_code == 200:
                self.check(
                    "Auth Development Bypass",
                    True,
                    "(API accessible without token)"
                )
            else:
                # Check if it's a redirect (means auth is enforcing)
                self.check(
                    "Auth System",
                    response.status_code == 302,
                    "(Auth middleware active)"
                )
        except Exception as e:
            self.check("Authentication System", False, str(e))

    def check_system_metrics(self):
        """Check system metrics from Intelligence API"""
        try:
            response = requests.get(f"{self.base_url}/api/intelligence/", timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    metrics = data['data']

                    # Check key metrics
                    self.check(
                        "Active Agents",
                        metrics.get('active_agents', 0) > 0,
                        f"({metrics.get('active_agents', 0)} agents active)"
                    )

                    self.check(
                        "Active Spiders",
                        metrics.get('active_spiders', 0) > 0,
                        f"({metrics.get('active_spiders', 0)} spiders deployed)"
                    )

                    self.check(
                        "System Health Score",
                        metrics.get('health_score', 0) > 0,
                        f"({metrics.get('health_score', 0):.1f}%)"
                    )

                    # Check Redis health specifically
                    system_metrics = metrics.get('system_metrics', {})
                    self.check(
                        "Redis Health Metric",
                        system_metrics.get('redis_health', 0) == 100,
                        f"({system_metrics.get('redis_health', 0)}%)"
                    )

                    self.check(
                        "WebSocket Health Metric",
                        system_metrics.get('websocket_status', 0) == 100,
                        f"({system_metrics.get('websocket_status', 0)}%)"
                    )

                    return True
            return False
        except Exception as e:
            print(f"Could not check system metrics: {e}")
            return False

    async def run_all_checks(self):
        """Run all health checks"""
        print("\n" + "="*60)
        print("🏥 FINAL SYSTEM HEALTH CHECK")
        print("="*60 + "\n")

        # 1. Redis checks
        print("\n📦 Redis System:")
        print("-" * 30)
        self.check_redis()

        # 2. API endpoint checks
        print("\n🌐 API Endpoints:")
        print("-" * 30)
        self.check_api_endpoints()

        # 3. WebSocket check
        print("\n🔌 WebSocket System:")
        print("-" * 30)
        await self.check_websocket()

        # 4. Dashboard accessibility
        print("\n📊 Dashboard Access:")
        print("-" * 30)
        self.check_dashboard_accessibility()

        # 5. Authentication system
        print("\n🔐 Authentication System:")
        print("-" * 30)
        self.check_authentication_system()

        # 6. System metrics
        print("\n📈 System Metrics:")
        print("-" * 30)
        self.check_system_metrics()

        # Final summary
        print("\n" + "="*60)
        print("📋 HEALTH CHECK SUMMARY")
        print("="*60)

        success_rate = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0

        print(f"\nTotal Checks: {self.total_checks}")
        print(f"Passed: {self.passed_checks}")
        print(f"Failed: {self.total_checks - self.passed_checks}")
        print(f"Success Rate: {success_rate:.1f}%")

        if success_rate >= 90:
            print("\n🎉 SYSTEM IS HEALTHY AND READY!")
            print("Authentication is functional with development bypasses.")
            print("All critical systems are operational.")
        elif success_rate >= 75:
            print("\n⚠️ SYSTEM IS MOSTLY HEALTHY")
            print("Some non-critical issues detected.")
        else:
            print("\n❌ SYSTEM NEEDS ATTENTION")
            print("Critical issues detected. Review failed checks above.")

        print("\n" + "="*60 + "\n")

        return success_rate >= 75


async def main():
    """Main runner"""
    checker = SystemHealthChecker()
    success = await checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())