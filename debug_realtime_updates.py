#!/usr/bin/env python
"""
Real-time Update Diagnostics Tool
==================================
Identifies where real-time data updates are failing in the frontend
"""

import asyncio
import json
import websocket
import threading
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

class RealTimeUpdateDiagnostics:
    def __init__(self):
        self.issues_found = []
        self.data_samples = {}
        self.update_counts = {}
        self.last_update_times = {}

    def diagnose_component(self, component: str, ws_url: str):
        """Diagnose real-time updates for a specific component"""
        print(f"\n🔍 Diagnosing {component}...")

        self.update_counts[component] = 0
        self.last_update_times[component] = None
        messages_received = []

        def on_message(ws, message):
            try:
                data = json.loads(message)
                messages_received.append(data)
                self.update_counts[component] += 1
                self.last_update_times[component] = datetime.now()

                # Check message type
                msg_type = data.get('type', 'unknown')
                print(f"  📨 {component}: Received '{msg_type}' message")

                # Analyze data structure
                if component == 'neural_orchestra':
                    if 'agents' in data:
                        agent_count = len(data['agents'])
                        print(f"    → Agents: {agent_count}")
                        if agent_count == 0:
                            self.issues_found.append(f"{component}: No agents in data (expected 149)")
                    else:
                        self.issues_found.append(f"{component}: Missing 'agents' field in {msg_type}")

                    if 'advisors' in data:
                        advisor_count = len(data['advisors'])
                        print(f"    → Advisors: {advisor_count}")
                        if advisor_count == 0:
                            self.issues_found.append(f"{component}: No advisors in data (expected 25)")

                elif component == 'decision_command':
                    if msg_type == 'decision_update':
                        if 'decisions' in data:
                            print(f"    → Decisions: {len(data['decisions'])}")
                        if 'top_opportunities' in data:
                            print(f"    → Opportunities: {len(data['top_opportunities'])}")
                    elif msg_type == 'opportunities_analysis':
                        if 'top_opportunities' in data:
                            opp_count = len(data['top_opportunities'])
                            print(f"    → Top Opportunities: {opp_count}")
                            if opp_count == 0:
                                self.issues_found.append(f"{component}: No opportunities in analysis")

                elif component == 'revenue_dashboard':
                    if 'metrics' in data:
                        metrics = data['metrics']
                        print(f"    → Total Revenue: ${metrics.get('total_revenue', 0):.2f}")
                        print(f"    → Today Revenue: ${metrics.get('today_revenue', 0):.2f}")
                    else:
                        if msg_type not in ['connection_status', 'heartbeat']:
                            self.issues_found.append(f"{component}: Missing 'metrics' in {msg_type}")

                # Store data sample
                if component not in self.data_samples:
                    self.data_samples[component] = []
                self.data_samples[component].append({
                    'type': msg_type,
                    'timestamp': datetime.now().isoformat(),
                    'has_real_data': 'is_real' in data and data['is_real'],
                    'data_keys': list(data.keys())
                })

            except Exception as e:
                self.issues_found.append(f"{component}: Error parsing message - {str(e)}")
                print(f"  ❌ Error: {e}")

        def on_error(ws, error):
            self.issues_found.append(f"{component}: WebSocket error - {str(error)}")
            print(f"  ❌ WebSocket Error: {error}")

        def on_open(ws):
            print(f"  ✅ {component}: Connected")
            # Send initial requests
            ws.send(json.dumps({'type': 'get_data', 'component': component}))

            # Component-specific requests
            if component == 'neural_orchestra':
                ws.send(json.dumps({'type': 'get_orchestra_data'}))
            elif component == 'decision_command':
                ws.send(json.dumps({'action': 'analyze_opportunities'}))
            elif component == 'revenue_dashboard':
                ws.send(json.dumps({'type': 'refresh_metrics'}))

        def on_close(ws, close_status_code, close_msg):
            print(f"  🔌 {component}: Disconnected")

        # Create and run WebSocket
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        # Run in thread for 10 seconds
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        # Wait and check for periodic updates
        print(f"  ⏳ Monitoring for 15 seconds...")
        initial_count = 0
        for i in range(15):
            time.sleep(1)
            current_count = self.update_counts[component]
            if current_count > initial_count:
                print(f"    → Update #{current_count} received")
                initial_count = current_count

        ws.close()

        # Analyze results
        total_updates = self.update_counts[component]
        if total_updates < 2:
            self.issues_found.append(f"{component}: Only {total_updates} updates in 15 seconds (expected periodic updates)")

        return messages_received

    def check_database_data(self):
        """Check if database has actual data"""
        print("\n🗄️ Checking Database Data...")

        try:
            # Check for agents
            response = requests.get('http://localhost:8000/api/agents/registry/stats/')
            if response.status_code == 200:
                data = response.json()
                print(f"  → Active Agents: {data.get('active_agents', 0)}")
                print(f"  → Total Agents: {data.get('total_agents', 0)}")
                if data.get('total_agents', 0) == 0:
                    self.issues_found.append("Database: No agents registered")
            else:
                print(f"  ❌ Failed to get agent stats: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error checking agents: {e}")

        # Check for opportunities
        try:
            response = requests.get('http://localhost:8000/api/opportunities/')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    opp_data = data.get('data', {})
                    job_count = len(opp_data.get('jobs', []))
                    content_count = len(opp_data.get('content', []))
                    print(f"  → Jobs: {job_count}")
                    print(f"  → Content: {content_count}")
                    if job_count == 0 and content_count == 0:
                        self.issues_found.append("Database: No opportunities available")
            else:
                print(f"  ❌ Failed to get opportunities: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error checking opportunities: {e}")

    def generate_report(self):
        """Generate diagnostic report"""
        print("\n" + "="*60)
        print("REAL-TIME UPDATE DIAGNOSTIC REPORT")
        print("="*60)

        # Update frequency analysis
        print("\n📊 Update Frequency:")
        for component, count in self.update_counts.items():
            updates_per_minute = (count / 15) * 60
            status = "✅" if updates_per_minute >= 12 else "⚠️" if updates_per_minute >= 4 else "❌"
            print(f"  {status} {component}: {count} updates ({updates_per_minute:.1f}/min)")

        # Data completeness
        print("\n📦 Data Completeness:")
        for component, samples in self.data_samples.items():
            real_data_count = sum(1 for s in samples if s['has_real_data'])
            total_samples = len(samples)
            percentage = (real_data_count / total_samples * 100) if total_samples > 0 else 0
            status = "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
            print(f"  {status} {component}: {real_data_count}/{total_samples} real data ({percentage:.0f}%)")

            # Show message types received
            message_types = set(s['type'] for s in samples)
            print(f"      Message types: {', '.join(message_types)}")

        # Issues found
        if self.issues_found:
            print("\n❌ Issues Found:")
            for issue in self.issues_found:
                print(f"  • {issue}")
        else:
            print("\n✅ No Issues Found")

        # Recommendations
        print("\n💡 Recommendations:")

        if any("No agents" in issue for issue in self.issues_found):
            print("  1. Run agent registration: python manage.py register_all_agents")

        if any("No opportunities" in issue for issue in self.issues_found):
            print("  2. Run spider deployment: python manage.py deploy_spiders")

        if any("periodic updates" in issue for issue in self.issues_found):
            print("  3. Check unified_hub.py periodic_real_updates() task")

        if any("Missing 'metrics'" in issue for issue in self.issues_found):
            print("  4. Verify get_real_revenue_data() returns correct format")

        if any("No advisors" in issue for issue in self.issues_found):
            print("  5. Initialize advisor registry data")

        print("\n" + "="*60)

def main():
    diagnostics = RealTimeUpdateDiagnostics()

    # Check database first
    diagnostics.check_database_data()

    # Test each component
    components = {
        'neural_orchestra': 'ws://localhost:8000/ws/neural-orchestra/',
        'decision_command': 'ws://localhost:8000/ws/decision-command/',
        'revenue_dashboard': 'ws://localhost:8000/ws/revenue-dashboard/',
        'income_builder': 'ws://localhost:8000/ws/income-builder/',
    }

    for component, url in components.items():
        diagnostics.diagnose_component(component, url)

    # Generate report
    diagnostics.generate_report()

if __name__ == "__main__":
    main()