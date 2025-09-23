#!/usr/bin/env python
"""
Real-Time Learning Monitor
==========================
Shows REAL agent learning progress as it happens
"""

import redis
import json
import time
from datetime import datetime

def monitor_real_learning():
    """
    Monitor and display real learning progress
    """
    r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

    print("=" * 60)
    print("📊 REAL AI AGENT LEARNING MONITOR")
    print("Watching ACTUAL learning with OpenAI API calls")
    print("=" * 60)

    last_learning_count = 0
    last_collaboration_count = 0
    last_content_count = 0

    while True:
        try:
            # Get current metrics
            learning_keys = r.keys("learning:*")
            collaboration_keys = r.keys("collaboration:*")
            content_keys = r.keys("generated_content*")

            # System metrics if available
            metrics = r.hgetall("learning:system:metrics")
            final_metrics = r.hgetall("learning:system:final")

            print(f"\r🧠 Learning Events: {len(learning_keys):3d} | "
                  f"🤝 Collaborations: {len(collaboration_keys):3d} | "
                  f"📝 Content: {len(content_keys):3d} | "
                  f"Time: {datetime.now().strftime('%H:%M:%S')}", end="")

            # Show new activity
            if len(learning_keys) > last_learning_count:
                print(f"\n   ✨ NEW LEARNING: {len(learning_keys) - last_learning_count} agents learned something!")

            if len(collaboration_keys) > last_collaboration_count:
                print(f"\n   🤝 NEW COLLABORATION: Agents working together!")

            if len(content_keys) > last_content_count:
                print(f"\n   📝 NEW CONTENT: Real content generated!")

            # Show detailed metrics if available
            if metrics:
                print(f"\n   📊 API Calls: {metrics.get('total_tokens', 0)} tokens | "
                      f"Cost: {metrics.get('total_cost', '$0.000000')}")

            # Check if complete
            if final_metrics.get('session_complete'):
                print("\n\n" + "=" * 60)
                print("✅ REAL LEARNING SESSION COMPLETE!")
                print(f"   Agents Trained: {final_metrics.get('agents_trained', 0)}")
                print(f"   Total Learnings: {final_metrics.get('total_learnings', 0)}")
                print(f"   Collaborations: {final_metrics.get('total_collaborations', 0)}")
                print(f"   Content Generated: {final_metrics.get('total_content_generated', 0)}")
                print(f"   API Tokens Used: {final_metrics.get('total_tokens_used', 0)}")
                print(f"   Total Cost: {final_metrics.get('total_cost', '$0.000000')}")
                print("=" * 60)
                break

            last_learning_count = len(learning_keys)
            last_collaboration_count = len(collaboration_keys)
            last_content_count = len(content_keys)

            time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_real_learning()