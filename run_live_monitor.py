#!/usr/bin/env python
"""
Run live system monitoring to generate real activity data
"""

from intelligence.system_activity_verifier import SystemActivityVerifier, LiveActivityMonitor
import threading
import time

def run_continuous_verification():
    """Run verification every 5 seconds to generate fresh data"""
    verifier = SystemActivityVerifier()

    while True:
        try:
            print("🔄 Running system verification...")
            status = verifier.get_complete_system_status()

            # Display what we found
            if status['spider_activity']['external_apis_called']:
                print(f"   ✓ Called APIs: {', '.join(status['spider_activity']['external_apis_called'])}")

            print(f"   📊 Reality Score: {status['reality_score']}%")

            # Store in Redis for dashboard to fetch
            import redis
            r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
            import json
            r.set('system:current:status', json.dumps(status), ex=30)

            time.sleep(5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Starting Live System Monitor")
    print("   This will generate real data for the dashboard")
    print("   Press Ctrl+C to stop\n")

    run_continuous_verification()