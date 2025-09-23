#!/usr/bin/env python
"""
Auto-Update Agent Data
======================
Continuously monitors Redis for new agent activities and updates the dashboard data
"""

import time
import json
import redis
from datetime import datetime
from update_agent_network_data import update_agent_network_data

def monitor_agent_activity():
    """
    Monitor for new agent activity and update dashboard data
    """
    print("🚀 Starting Agent Network Auto-Updater...")
    print("📊 Monitoring Redis for new agent activities...")

    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
    last_update_count = 0

    while True:
        try:
            # Check current agent teaching count
            current_count = r.llen("agent_teaching")

            if current_count != last_update_count:
                print(f"\n🔔 New activity detected! Teaching sessions: {current_count}")
                print("🔄 Updating dashboard data...")

                # Update the data
                update_agent_network_data()

                last_update_count = current_count
                print(f"✅ Dashboard updated at {datetime.now().strftime('%H:%M:%S')}")

            # Wait 10 seconds before checking again
            time.sleep(10)

        except KeyboardInterrupt:
            print("\n👋 Auto-updater stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    monitor_agent_activity()