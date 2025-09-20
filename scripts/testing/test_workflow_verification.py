#!/usr/bin/env python
"""
COMPLETE WORKFLOW VERIFICATION TEST
====================================
Tests the entire data flow from Income Builder through all components
"""

import asyncio
import json
import logging
from datetime import datetime
import websocket
import threading
import time
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowVerifier:
    def __init__(self):
        self.results = {
            'income_builder': {'connected': False, 'data_received': False, 'data': None},
            'neural_orchestra': {'connected': False, 'data_received': False, 'data': None},
            'decision_command': {'connected': False, 'data_received': False, 'data': None},
            'revenue_dashboard': {'connected': False, 'data_received': False, 'data': None},
            'revenue_opportunities': {'connected': False, 'data_received': False, 'data': None}
        }
        self.ws_connections = {}

    def test_websocket_connection(self, component: str, url: str):
        """Test WebSocket connection and data flow for a component"""
        try:
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    logger.info(f"✅ {component}: Received {data.get('type', 'unknown')} message")
                    self.results[component]['data_received'] = True
                    self.results[component]['data'] = data

                    # Log specific data types
                    if 'opportunities' in data:
                        logger.info(f"  → {len(data.get('opportunities', []))} opportunities")
                    if 'agents' in data:
                        logger.info(f"  → {len(data.get('agents', []))} agents")
                    if 'advisors' in data:
                        logger.info(f"  → {len(data.get('advisors', []))} advisors")
                    if 'metrics' in data:
                        logger.info(f"  → Metrics: {data.get('metrics', {})}")

                except Exception as e:
                    logger.error(f"❌ {component}: Error parsing message: {e}")

            def on_error(ws, error):
                logger.error(f"❌ {component}: WebSocket error: {error}")
                self.results[component]['connected'] = False

            def on_close(ws, close_status_code, close_msg):
                logger.info(f"🔌 {component}: WebSocket closed")
                self.results[component]['connected'] = False

            def on_open(ws):
                logger.info(f"✅ {component}: WebSocket connected")
                self.results[component]['connected'] = True

                # Send initial data request
                ws.send(json.dumps({'type': 'get_data', 'component': component}))

                # Component-specific requests
                if component == 'decision_command':
                    ws.send(json.dumps({'action': 'analyze_opportunities'}))
                elif component == 'income_builder':
                    ws.send(json.dumps({'type': 'get_opportunities'}))
                elif component == 'neural_orchestra':
                    ws.send(json.dumps({'type': 'get_orchestra_data'}))

            # Create WebSocket connection
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            self.ws_connections[component] = ws

            # Run in thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()

        except Exception as e:
            logger.error(f"❌ {component}: Failed to create WebSocket: {e}")
            self.results[component]['connected'] = False

    def test_data_flow(self):
        """Test the complete data flow through all components"""
        logger.info("\n" + "="*60)
        logger.info("TESTING COMPLETE WORKFLOW DATA FLOW")
        logger.info("="*60 + "\n")

        # 1. Test WebSocket connections
        logger.info("📡 Testing WebSocket Connections...")
        components = {
            'income_builder': 'ws://localhost:8000/ws/income-builder/',
            'neural_orchestra': 'ws://localhost:8000/ws/neural-orchestra/',
            'decision_command': 'ws://localhost:8000/ws/decision-command/',
            'revenue_dashboard': 'ws://localhost:8000/ws/revenue-dashboard/',
            'revenue_opportunities': 'ws://localhost:8000/ws/revenue-opportunities/'
        }

        for component, url in components.items():
            self.test_websocket_connection(component, url)

        # Wait for connections to establish
        time.sleep(3)

        # 2. Check connection status
        logger.info("\n📊 Connection Status:")
        for component, status in self.results.items():
            if status['connected']:
                logger.info(f"  ✅ {component}: Connected")
            else:
                logger.info(f"  ❌ {component}: Not connected")

        # 3. Wait for data to flow
        logger.info("\n⏳ Waiting for data flow (10 seconds)...")
        time.sleep(10)

        # 4. Verify data received
        logger.info("\n📈 Data Flow Verification:")
        for component, status in self.results.items():
            if status['data_received']:
                logger.info(f"  ✅ {component}: Data received")
                if status['data']:
                    data_type = status['data'].get('type', 'unknown')
                    logger.info(f"     → Type: {data_type}")
                    if 'is_real' in status['data']:
                        logger.info(f"     → Real data: {status['data']['is_real']}")
            else:
                logger.info(f"  ❌ {component}: No data received")

        # 5. Test specific workflows
        logger.info("\n🔄 Testing Specific Workflows:")
        self.test_income_builder_flow()
        self.test_neural_orchestra_flow()
        self.test_decision_command_flow()

        # 6. Generate summary
        self.generate_summary()

    def test_income_builder_flow(self):
        """Test Income Builder specific workflow"""
        logger.info("\n  → Income Builder Workflow:")

        if self.results['income_builder']['connected']:
            ws = self.ws_connections.get('income_builder')
            if ws:
                # Request opportunity analysis
                ws.send(json.dumps({
                    'type': 'analyze_opportunities',
                    'user_profile': {
                        'skills': ['python', 'writing', 'AI'],
                        'available_hours': 20,
                        'skill_level': 'intermediate'
                    }
                }))
                time.sleep(2)
                logger.info("    ✅ Opportunity analysis requested")
        else:
            logger.info("    ❌ Income Builder not connected")

    def test_neural_orchestra_flow(self):
        """Test Neural Orchestra visualization flow"""
        logger.info("\n  → Neural Orchestra Workflow:")

        if self.results['neural_orchestra']['connected']:
            data = self.results['neural_orchestra'].get('data', {})
            if data:
                agents = data.get('agents', [])
                advisors = data.get('advisors', [])
                connections = data.get('connections', [])
                logger.info(f"    ✅ Agents: {len(agents)}, Advisors: {len(advisors)}, Connections: {len(connections)}")
            else:
                logger.info("    ⚠️  No visualization data")
        else:
            logger.info("    ❌ Neural Orchestra not connected")

    def test_decision_command_flow(self):
        """Test Decision Command decision flow"""
        logger.info("\n  → Decision Command Workflow:")

        if self.results['decision_command']['connected']:
            data = self.results['decision_command'].get('data', {})
            if data:
                opportunities = data.get('top_opportunities', [])
                if opportunities:
                    logger.info(f"    ✅ {len(opportunities)} opportunities available")
                    for opp in opportunities[:3]:
                        logger.info(f"       • {opp.get('title', 'Unknown')}: {opp.get('potential_monthly', 'N/A')}")
                else:
                    logger.info("    ⚠️  No opportunities in data")
            else:
                logger.info("    ⚠️  No decision data")
        else:
            logger.info("    ❌ Decision Command not connected")

    def generate_summary(self):
        """Generate workflow verification summary"""
        logger.info("\n" + "="*60)
        logger.info("WORKFLOW VERIFICATION SUMMARY")
        logger.info("="*60)

        connected_count = sum(1 for r in self.results.values() if r['connected'])
        data_received_count = sum(1 for r in self.results.values() if r['data_received'])

        logger.info(f"\n📊 Overall Results:")
        logger.info(f"  • Components Connected: {connected_count}/5")
        logger.info(f"  • Components Receiving Data: {data_received_count}/5")

        # Data flow chain verification
        logger.info(f"\n🔗 Data Flow Chain:")
        chain = [
            ('Income Builder', self.results['income_builder']['data_received']),
            ('Neural Orchestra', self.results['neural_orchestra']['data_received']),
            ('Decision Command', self.results['decision_command']['data_received']),
            ('Revenue Opportunities', self.results['revenue_opportunities']['data_received']),
            ('Revenue Dashboard', self.results['revenue_dashboard']['data_received'])
        ]

        for component, has_data in chain:
            status = "✅" if has_data else "❌"
            logger.info(f"  {status} {component}")

        # Overall status
        if connected_count == 5 and data_received_count >= 3:
            logger.info("\n✅ WORKFLOW VERIFICATION: PASSED")
            logger.info("The system is operational with data flowing through components.")
        elif connected_count >= 3:
            logger.info("\n⚠️  WORKFLOW VERIFICATION: PARTIAL")
            logger.info("Some components are working but not all data flows are active.")
        else:
            logger.info("\n❌ WORKFLOW VERIFICATION: FAILED")
            logger.info("Critical components are not connected or receiving data.")

        # Close all WebSocket connections
        logger.info("\n🔌 Closing all connections...")
        for ws in self.ws_connections.values():
            if ws:
                ws.close()

def main():
    """Run the workflow verification test"""
    verifier = WorkflowVerifier()
    verifier.test_data_flow()

if __name__ == "__main__":
    main()