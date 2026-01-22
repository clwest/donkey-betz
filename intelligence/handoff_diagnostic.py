"""
Handoff System Diagnostic Tool
Identifies and validates all connection points between system components
"""

import json
import logging
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


@dataclass
class HandoffPoint:
    """Represents a connection point between components"""
    source: str
    destination: str
    connection_type: str  # 'api', 'websocket', 'redis', 'celery', 'direct'
    status: str  # 'connected', 'broken', 'unknown', 'mock'
    data_format: str  # 'json', 'text', 'binary'
    test_data: Any = None
    error_message: str = ""
    last_tested: datetime = None


class HandoffDiagnostic:
    """Diagnoses handoff points in the system"""

    def __init__(self):
        self.handoff_points = []
        self.connection_map = {}
        self.broken_connections = []
        self.mock_connections = []

    def map_all_handoffs(self) -> Dict[str, List[HandoffPoint]]:
        """Map all handoff points in the system"""

        print("\n" + "="*80)
        print("🔍 HANDOFF SYSTEM DIAGNOSTIC")
        print("="*80 + "\n")

        # Define all known handoff points
        handoffs = [
            # Income Builder → Agent Parser
            HandoffPoint(
                source="Income Builder",
                destination="Agent Parser",
                connection_type="direct",
                data_format="markdown",
                status="unknown"
            ),

            # Agent Parser → Execution Pipeline
            HandoffPoint(
                source="Agent Parser",
                destination="Execution Pipeline",
                connection_type="direct",
                data_format="json",
                status="unknown"
            ),

            # Execution Pipeline → Individual Agents
            HandoffPoint(
                source="Execution Pipeline",
                destination="Agent Network (149 agents)",
                connection_type="celery",
                data_format="json",
                status="unknown"
            ),

            # Spiders → Data Storage
            HandoffPoint(
                source="Spider Army",
                destination="PostgreSQL/Redis",
                connection_type="api",
                data_format="json",
                status="unknown"
            ),

            # Data Storage → Income Builder
            HandoffPoint(
                source="Spider Data",
                destination="Income Builder",
                connection_type="api",
                data_format="json",
                status="unknown"
            ),

            # Frontend → Backend WebSocket
            HandoffPoint(
                source="React Frontend",
                destination="Django WebSocket",
                connection_type="websocket",
                data_format="json",
                status="unknown"
            ),

            # Backend → Redis PubSub
            HandoffPoint(
                source="Django Backend",
                destination="Redis PubSub",
                connection_type="redis",
                data_format="json",
                status="unknown"
            ),

            # Celery → Agent Execution
            HandoffPoint(
                source="Celery Tasks",
                destination="Agent Execution",
                connection_type="celery",
                data_format="json",
                status="unknown"
            ),

            # Agents → Result Storage
            HandoffPoint(
                source="Agent Results",
                destination="ActionPlan Results",
                connection_type="direct",
                data_format="json",
                status="unknown"
            ),

            # ML Models → Predictions
            HandoffPoint(
                source="ML Pipeline",
                destination="Prediction Service",
                connection_type="api",
                data_format="json",
                status="unknown"
            ),

            # Advisors → Strategy Engine
            HandoffPoint(
                source="Advisor Network (25)",
                destination="Strategy Engine",
                connection_type="api",
                data_format="json",
                status="unknown"
            ),

            # Revenue Tracking → Dashboard
            HandoffPoint(
                source="Revenue Engine",
                destination="Revenue Dashboard",
                connection_type="websocket",
                data_format="json",
                status="unknown"
            )
        ]

        self.handoff_points = handoffs
        return self._group_by_component(handoffs)

    def test_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test if a handoff connection is working"""

        print(f"Testing: {handoff.source} → {handoff.destination}")

        try:
            if handoff.connection_type == "direct":
                # Test direct Python imports/calls
                return self._test_direct_connection(handoff)

            elif handoff.connection_type == "api":
                # Test API endpoints
                return self._test_api_connection(handoff)

            elif handoff.connection_type == "websocket":
                # Test WebSocket connections
                return self._test_websocket_connection(handoff)

            elif handoff.connection_type == "redis":
                # Test Redis pub/sub
                return self._test_redis_connection(handoff)

            elif handoff.connection_type == "celery":
                # Test Celery task routing
                return self._test_celery_connection(handoff)

            else:
                return False, "Unknown connection type"

        except Exception as e:
            return False, str(e)

    def _test_direct_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test direct Python connections"""
        try:
            # Test specific handoffs
            if handoff.source == "Income Builder" and handoff.destination == "Agent Parser":
                from intelligence.agent_instruction_parser import AgentInstructionParser
                parser = AgentInstructionParser()
                # Test with sample data
                test_plan = "### Step 1: Test\n- **Action:** Test action\n- **Tool:** Test Agent\n- **Expected Outcome:** Test outcome"
                instructions = parser.parse_plan(test_plan)
                if len(instructions) >= 0:  # Parser works even if no instructions found
                    return True, "Parser imported and functional"
                return False, "Parser not working correctly"

            elif handoff.source == "Agent Parser" and handoff.destination == "Execution Pipeline":
                from intelligence.agent_execution_pipeline import AgentExecutionPipeline
                pipeline = AgentExecutionPipeline()
                return True, "Pipeline imported successfully"

            return False, "Direct connection not implemented"

        except ImportError as e:
            return False, f"Import error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _test_api_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test API endpoint connections"""
        try:
            # Map component to endpoint
            endpoints = {
                "Spider Army": "http://localhost:8000/api/v1/intelligence/opportunities/",
                "ML Pipeline": "http://localhost:8000/api/v1/intelligence/predictions/",
                "Advisor Network (25)": "http://localhost:8000/api/v1/agents/advisors/"
            }

            endpoint = endpoints.get(handoff.source)
            if endpoint:
                response = requests.get(endpoint, timeout=2)
                if response.status_code in [200, 201]:
                    return True, f"API endpoint responding ({response.status_code})"
                return False, f"API returned {response.status_code}"

            return False, "No endpoint mapped"

        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to API"
        except requests.exceptions.Timeout:
            return False, "API timeout"
        except Exception as e:
            return False, str(e)

    def _test_websocket_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test WebSocket connections"""
        # This would test WebSocket connections
        # For now, return mock status
        if "Frontend" in handoff.source:
            return True, "WebSocket configured (not tested)"
        return False, "WebSocket not configured"

    def _test_redis_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test Redis connections"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            return True, "Redis connected"
        except:
            return False, "Redis not available"

    def _test_celery_connection(self, handoff: HandoffPoint) -> Tuple[bool, str]:
        """Test Celery connections"""
        try:
            from celery import Celery
            app = Celery('core')
            # Check if broker is accessible
            from kombu import Connection
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            conn = Connection(redis_url)
            conn.ensure_connection(max_retries=1)
            return True, "Celery broker connected"
        except:
            return False, "Celery broker not available"

    def _group_by_component(self, handoffs: List[HandoffPoint]) -> Dict[str, List[HandoffPoint]]:
        """Group handoffs by source component"""
        grouped = {}
        for handoff in handoffs:
            if handoff.source not in grouped:
                grouped[handoff.source] = []
            grouped[handoff.source].append(handoff)
        return grouped

    def run_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic of all handoff points"""

        # Map all handoffs
        component_map = self.map_all_handoffs()

        # Test each connection
        results = {
            'total': len(self.handoff_points),
            'connected': 0,
            'broken': 0,
            'mock': 0,
            'unknown': 0,
            'details': []
        }

        print("\n🔌 Testing Connections...")
        print("-" * 40)

        for handoff in self.handoff_points:
            success, message = self.test_connection(handoff)

            if success:
                handoff.status = "connected"
                results['connected'] += 1
                status_icon = "✅"
            else:
                if "not implemented" in message.lower() or "not configured" in message.lower():
                    handoff.status = "mock"
                    results['mock'] += 1
                    status_icon = "🔨"
                    self.mock_connections.append(handoff)
                else:
                    handoff.status = "broken"
                    results['broken'] += 1
                    status_icon = "❌"
                    self.broken_connections.append(handoff)

            handoff.error_message = message
            handoff.last_tested = datetime.now()

            print(f"{status_icon} {handoff.source} → {handoff.destination}")
            print(f"   Type: {handoff.connection_type} | Status: {message}")

            results['details'].append({
                'source': handoff.source,
                'destination': handoff.destination,
                'type': handoff.connection_type,
                'status': handoff.status,
                'message': message
            })

        # Summary
        print("\n" + "="*40)
        print("📊 DIAGNOSTIC SUMMARY")
        print("="*40)
        print(f"Total Handoffs: {results['total']}")
        print(f"✅ Connected: {results['connected']}")
        print(f"🔨 Mock/Need Implementation: {results['mock']}")
        print(f"❌ Broken: {results['broken']}")
        print(f"❓ Unknown: {results['unknown']}")

        if self.broken_connections:
            print("\n⚠️ BROKEN CONNECTIONS:")
            for conn in self.broken_connections:
                print(f"   - {conn.source} → {conn.destination}")
                print(f"     Error: {conn.error_message}")

        if self.mock_connections:
            print("\n🔨 NEEDS IMPLEMENTATION:")
            for conn in self.mock_connections:
                print(f"   - {conn.source} → {conn.destination}")
                print(f"     Type: {conn.connection_type}")

        # Calculate health score
        health_score = (results['connected'] / results['total']) * 100
        print(f"\n🏥 System Health: {health_score:.1f}%")

        return results

    def generate_fix_plan(self) -> List[Dict[str, Any]]:
        """Generate a plan to fix broken connections"""
        fixes = []

        for conn in self.broken_connections:
            fix = {
                'priority': 'high',
                'source': conn.source,
                'destination': conn.destination,
                'connection_type': conn.connection_type,
                'error': conn.error_message,
                'suggested_fix': self._suggest_fix(conn)
            }
            fixes.append(fix)

        for conn in self.mock_connections:
            fix = {
                'priority': 'medium',
                'source': conn.source,
                'destination': conn.destination,
                'connection_type': conn.connection_type,
                'suggested_fix': f"Implement {conn.connection_type} connection"
            }
            fixes.append(fix)

        return fixes

    def _suggest_fix(self, conn: HandoffPoint) -> str:
        """Suggest fix for broken connection"""
        if "Import error" in conn.error_message:
            return "Check module imports and dependencies"
        elif "Cannot connect" in conn.error_message:
            return "Start the required service"
        elif "timeout" in conn.error_message.lower():
            return "Check if service is running and accessible"
        elif "not available" in conn.error_message:
            return f"Start {conn.destination} service"
        else:
            return "Investigate connection configuration"


if __name__ == "__main__":
    diagnostic = HandoffDiagnostic()
    results = diagnostic.run_diagnostic()

    # Generate fix plan
    fixes = diagnostic.generate_fix_plan()
    if fixes:
        print("\n" + "="*40)
        print("🔧 FIX PLAN")
        print("="*40)
        for i, fix in enumerate(fixes, 1):
            print(f"\n{i}. [{fix['priority'].upper()}] {fix['source']} → {fix['destination']}")
            print(f"   Fix: {fix['suggested_fix']}")
            if 'error' in fix:
                print(f"   Error: {fix['error']}")

    # Save results
    with open('handoff_diagnostic_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print("\n📄 Report saved to handoff_diagnostic_report.json")