#!/usr/bin/env python3
"""
WebSocket Audit Script
====================

Comprehensive testing of all WebSocket endpoints to identify where data
transmission is failing between backend and frontend components.

This script will:
1. Test connection to each WebSocket endpoint
2. Send test messages and wait for responses
3. Analyze response formats and data structures
4. Create detailed audit report with failure points
5. Provide recommendations for fixes
"""

import asyncio
import websockets
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketAuditor:
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.endpoints = [
            # Core component endpoints from frontend analysis
            "/ws/income-builder/",
            "/ws/revenue-dashboard/",
            "/ws/neural-orchestra/",
            "/ws/decision-command/",

            # Alternative endpoint names
            "/ws/revenue/",
            "/ws/decision/",
            "/ws/orchestra/",

            # Bridge endpoints
            "/ws/bridge/income-builder/",
            "/ws/bridge/revenue/",
            "/ws/bridge/decision/",
            "/ws/bridge/orchestra/",

            # Unified hub endpoints
            "/ws/unified-platform/",
            "/ws/platform-orchestrator/",

            # Legacy endpoints that might still work
            "/ws/command-center/",
            "/ws/opportunity-scanner/",
            "/ws/agents/",
            "/ws/dashboard/",
        ]

    async def test_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Test a single WebSocket endpoint"""
        result = {
            "endpoint": endpoint,
            "connection_success": False,
            "response_received": False,
            "data_format": None,
            "error": None,
            "response_time_ms": 0,
            "messages_received": [],
            "test_timestamp": datetime.now().isoformat()
        }

        start_time = time.time()

        try:
            full_url = f"{self.base_url}{endpoint}"
            logger.info(f"Testing connection to: {full_url}")

            # Try to connect with timeout
            async with websockets.connect(
                full_url,
                timeout=10,
                close_timeout=5
            ) as websocket:
                result["connection_success"] = True
                logger.info(f"✅ Connected to {endpoint}")

                # Wait briefly for any initial messages
                try:
                    initial_msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    result["messages_received"].append({
                        "type": "initial",
                        "data": initial_msg,
                        "timestamp": time.time() - start_time
                    })
                    logger.info(f"📨 Received initial message: {initial_msg[:100]}...")
                except asyncio.TimeoutError:
                    logger.info(f"⏱️ No initial message from {endpoint}")

                # Send test messages for each component type
                test_messages = self.get_test_messages(endpoint)

                for test_msg in test_messages:
                    try:
                        logger.info(f"📤 Sending test message: {test_msg}")
                        await websocket.send(json.dumps(test_msg))

                        # Wait for response
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            result["response_received"] = True
                            result["messages_received"].append({
                                "type": "response",
                                "request": test_msg,
                                "data": response,
                                "timestamp": time.time() - start_time
                            })
                            logger.info(f"📨 Received response: {response[:100]}...")

                            # Try to parse JSON response
                            try:
                                parsed = json.loads(response)
                                if result["data_format"] is None:
                                    result["data_format"] = self.analyze_data_format(parsed)
                            except json.JSONDecodeError:
                                logger.warning(f"⚠️ Non-JSON response from {endpoint}")

                        except asyncio.TimeoutError:
                            logger.warning(f"⏱️ No response to test message from {endpoint}")

                    except Exception as e:
                        logger.error(f"❌ Error sending test message to {endpoint}: {e}")

        except websockets.exceptions.ConnectionClosed as e:
            result["error"] = f"Connection closed: {e}"
            logger.error(f"❌ Connection closed for {endpoint}: {e}")

        except websockets.exceptions.InvalidURI as e:
            result["error"] = f"Invalid URI: {e}"
            logger.error(f"❌ Invalid URI for {endpoint}: {e}")

        except OSError as e:
            result["error"] = f"Connection refused: {e}"
            logger.error(f"❌ Connection refused for {endpoint}: {e}")

        except Exception as e:
            result["error"] = f"Unexpected error: {e}"
            logger.error(f"❌ Unexpected error for {endpoint}: {e}")
            traceback.print_exc()

        result["response_time_ms"] = (time.time() - start_time) * 1000
        return result

    def get_test_messages(self, endpoint: str) -> List[Dict[str, Any]]:
        """Get appropriate test messages for each endpoint type"""

        # Base test message that should work for most endpoints
        base_messages = [
            {"type": "ping"},
            {"type": "get_data"},
            {"type": "connection"},
        ]

        # Component-specific test messages based on frontend analysis
        if "income-builder" in endpoint:
            return base_messages + [
                {"type": "get_data", "component": "income_builder"},
                {"action": "get_opportunities"},
                {"type": "opportunities_request"},
            ]

        elif "revenue" in endpoint or "dashboard" in endpoint:
            return base_messages + [
                {"type": "get_data", "component": "revenue_dashboard"},
                {"type": "get_data", "timeframe": "30d"},
                {"type": "refresh_metrics"},
            ]

        elif "neural-orchestra" in endpoint or "orchestra" in endpoint:
            return base_messages + [
                {"type": "get_data", "component": "neural_orchestra"},
                {"type": "get_network_state"},
                {"type": "get_agents"},
            ]

        elif "decision" in endpoint or "command" in endpoint:
            return base_messages + [
                {"type": "get_data", "component": "decision_command"},
                {"action": "analyze_opportunities"},
                {"type": "get_opportunities"},
            ]

        return base_messages

    def analyze_data_format(self, data: Any) -> Dict[str, Any]:
        """Analyze the format and structure of received data"""
        format_info = {
            "is_json": True,
            "has_type_field": False,
            "data_keys": [],
            "nested_structure": False,
            "expected_frontend_format": None
        }

        if isinstance(data, dict):
            format_info["data_keys"] = list(data.keys())
            format_info["has_type_field"] = "type" in data
            format_info["nested_structure"] = any(isinstance(v, (dict, list)) for v in data.values())

            # Check if it matches expected frontend formats
            if "opportunities" in data:
                format_info["expected_frontend_format"] = "income_builder_opportunities"
            elif "metrics" in data:
                format_info["expected_frontend_format"] = "revenue_dashboard_metrics"
            elif "agents" in data:
                format_info["expected_frontend_format"] = "neural_orchestra_data"
            elif "decisions" in data:
                format_info["expected_frontend_format"] = "decision_command_data"

        return format_info

    async def run_full_audit(self) -> Dict[str, Any]:
        """Run complete audit of all WebSocket endpoints"""
        logger.info("🔍 Starting comprehensive WebSocket audit...")

        audit_start = time.time()
        results = []

        # Test all endpoints
        for endpoint in self.endpoints:
            result = await self.test_endpoint(endpoint)
            results.append(result)

            # Small delay between tests
            await asyncio.sleep(1)

        # Analyze results
        audit_summary = self.analyze_audit_results(results)
        audit_summary["total_audit_time_ms"] = (time.time() - audit_start) * 1000
        audit_summary["audit_timestamp"] = datetime.now().isoformat()

        # Save detailed results
        self.results = {
            "summary": audit_summary,
            "detailed_results": results,
            "recommendations": self.generate_recommendations(results)
        }

        return self.results

    def analyze_audit_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audit results and create summary"""
        total_endpoints = len(results)
        successful_connections = sum(1 for r in results if r["connection_success"])
        endpoints_with_responses = sum(1 for r in results if r["response_received"])
        endpoints_with_errors = sum(1 for r in results if r["error"])

        working_endpoints = [r["endpoint"] for r in results if r["connection_success"]]
        broken_endpoints = [r["endpoint"] for r in results if not r["connection_success"]]
        silent_endpoints = [r["endpoint"] for r in results if r["connection_success"] and not r["response_received"]]

        return {
            "total_endpoints_tested": total_endpoints,
            "successful_connections": successful_connections,
            "connection_success_rate": (successful_connections / total_endpoints) * 100,
            "endpoints_with_responses": endpoints_with_responses,
            "response_success_rate": (endpoints_with_responses / total_endpoints) * 100,
            "endpoints_with_errors": endpoints_with_errors,
            "working_endpoints": working_endpoints,
            "broken_endpoints": broken_endpoints,
            "silent_endpoints": silent_endpoints,
            "critical_issues": self.identify_critical_issues(results)
        }

    def identify_critical_issues(self, results: List[Dict[str, Any]]) -> List[str]:
        """Identify critical issues preventing frontend data flow"""
        issues = []

        # Check if core component endpoints are working
        core_endpoints = ["/ws/income-builder/", "/ws/revenue-dashboard/", "/ws/neural-orchestra/", "/ws/decision-command/"]

        for endpoint in core_endpoints:
            endpoint_results = [r for r in results if r["endpoint"] == endpoint]
            if not endpoint_results:
                continue

            result = endpoint_results[0]
            component_name = endpoint.replace("/ws/", "").replace("/", "").replace("-", " ").title()

            if not result["connection_success"]:
                issues.append(f"{component_name} endpoint completely non-functional - frontend will show no data")
            elif not result["response_received"]:
                issues.append(f"{component_name} accepts connections but sends no data - frontend will appear loading forever")
            elif not result["messages_received"]:
                issues.append(f"{component_name} doesn't respond to frontend requests - components will use fallback/mock data")

        # Check for data format issues
        endpoints_with_data = [r for r in results if r["response_received"] and r["messages_received"]]
        if not endpoints_with_data:
            issues.append("No endpoints are sending data - entire frontend will be static")

        return issues

    def generate_recommendations(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific recommendations to fix identified issues"""
        recommendations = []

        # Check each critical component
        component_map = {
            "/ws/income-builder/": "Income Builder",
            "/ws/revenue-dashboard/": "Revenue Dashboard",
            "/ws/neural-orchestra/": "Neural Orchestra",
            "/ws/decision-command/": "Decision Command"
        }

        for endpoint, component_name in component_map.items():
            endpoint_results = [r for r in results if r["endpoint"] == endpoint]
            if not endpoint_results:
                continue

            result = endpoint_results[0]

            if not result["connection_success"]:
                recommendations.append({
                    "priority": "HIGH",
                    "component": component_name,
                    "issue": "WebSocket endpoint not accessible",
                    "fix": f"Verify {endpoint} route is properly configured in routing.py and consumer exists",
                    "technical_details": f"Connection failed with: {result['error']}"
                })
            elif not result["response_received"]:
                recommendations.append({
                    "priority": "HIGH",
                    "component": component_name,
                    "issue": "Endpoint connects but doesn't send data",
                    "fix": f"Implement proper message handling in WebSocket consumer for {endpoint}",
                    "technical_details": "Consumer accepts connections but doesn't respond to frontend requests"
                })
            elif result["data_format"] and not result["data_format"]["expected_frontend_format"]:
                recommendations.append({
                    "priority": "MEDIUM",
                    "component": component_name,
                    "issue": "Data format mismatch between backend and frontend",
                    "fix": "Ensure backend sends data in format expected by frontend component",
                    "technical_details": f"Backend data keys: {result['data_format']['data_keys']}"
                })

        # General recommendations
        working_endpoints = [r["endpoint"] for r in results if r["connection_success"] and r["response_received"]]
        if working_endpoints:
            recommendations.append({
                "priority": "LOW",
                "component": "System",
                "issue": "Some endpoints work, suggesting infrastructure is functional",
                "fix": f"Use working endpoint patterns from: {working_endpoints[0]} as template for broken endpoints",
                "technical_details": "WebSocket infrastructure appears functional"
            })

        return recommendations

    def save_audit_report(self, filepath: str = None):
        """Save comprehensive audit report"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"websocket_audit_report_{timestamp}.json"

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        logger.info(f"📋 Audit report saved to: {filepath}")
        return filepath

    def print_summary(self):
        """Print human-readable audit summary"""
        if not self.results:
            logger.error("No audit results available. Run audit first.")
            return

        summary = self.results["summary"]

        print("\n" + "="*60)
        print("🔍 WEBSOCKET AUDIT SUMMARY")
        print("="*60)
        print(f"📊 Total Endpoints Tested: {summary['total_endpoints_tested']}")
        print(f"✅ Successful Connections: {summary['successful_connections']} ({summary['connection_success_rate']:.1f}%)")
        print(f"📨 Endpoints Sending Data: {summary['endpoints_with_responses']} ({summary['response_success_rate']:.1f}%)")
        print(f"❌ Endpoints with Errors: {summary['endpoints_with_errors']}")

        print(f"\n📡 WORKING ENDPOINTS:")
        for endpoint in summary["working_endpoints"]:
            print(f"  ✅ {endpoint}")

        print(f"\n❌ BROKEN ENDPOINTS:")
        for endpoint in summary["broken_endpoints"]:
            print(f"  ❌ {endpoint}")

        print(f"\n⚠️ SILENT ENDPOINTS (connect but no data):")
        for endpoint in summary["silent_endpoints"]:
            print(f"  ⚠️ {endpoint}")

        print(f"\n🚨 CRITICAL ISSUES:")
        for issue in summary["critical_issues"]:
            print(f"  🚨 {issue}")

        print(f"\n💡 TOP RECOMMENDATIONS:")
        high_priority = [r for r in self.results["recommendations"] if r["priority"] == "HIGH"]
        for rec in high_priority[:3]:
            print(f"  💡 {rec['component']}: {rec['fix']}")

        print("\n" + "="*60)

async def main():
    """Run the WebSocket audit"""
    auditor = WebSocketAuditor()

    print("🔍 Starting comprehensive WebSocket audit...")
    print("This will test all frontend component endpoints and identify data flow issues.\n")

    # Run the audit
    results = await auditor.run_full_audit()

    # Print summary
    auditor.print_summary()

    # Save detailed report
    report_file = auditor.save_audit_report()

    print(f"\n📋 Detailed audit report saved to: {report_file}")
    print("📋 This report contains specific technical recommendations for fixing each broken endpoint.")

    return results

if __name__ == "__main__":
    asyncio.run(main())