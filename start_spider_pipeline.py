#!/usr/bin/env python
"""
Start Spider → Agent Pipeline
==============================

Connects spiders to agents for automatic data processing.
Run this to enable automatic opportunity analysis.
"""

import sys
import time
import signal
import redis
from intelligence.spider_agent_router import SpiderAgentRouter, OpportunityDispatcher


def signal_handler(sig, frame):
    print("\n\n🛑 Shutting down spider pipeline...")
    sys.exit(0)


def main():
    print("="*60)
    print("🕷️ → 🤖 SPIDER-AGENT PIPELINE ACTIVATOR")
    print("="*60)
    print()

    # Check Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Redis connected")
    except:
        print("❌ Redis not running. Please start Redis first.")
        sys.exit(1)

    # Check for existing data
    r0 = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    freelance_count = len(r0.keys('freelance:opportunity:*'))

    print(f"📊 Found {freelance_count} freelance opportunities to process")

    if freelance_count == 0:
        print("\n⚠️  No data to process. Run spiders first to collect data:")
        print("   python backend/spider_fleet.py")
        print("\nOr simulate some test data:")
        print("   python seed_test_data.py")
        return

    print("\n🚀 Starting pipeline...")
    print("   - 7 specialized agents ready")
    print("   - Automatic routing enabled")
    print("   - Knowledge sharing active")
    print("\nPress Ctrl+C to stop\n")
    print("-"*60)

    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Start the router
    try:
        router = SpiderAgentRouter()
        router.start_routing()
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")


if __name__ == "__main__":
    main()