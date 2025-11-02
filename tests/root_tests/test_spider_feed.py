# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test Spider Feed Integration
Tests the spider intelligence feed to AI Nexus
"""

import redis
import time
import json
from datetime import datetime

def test_spider_feed():
    """Test publishing spider intelligence to Redis"""
    print("🕷️ Testing Spider Intelligence Feed...")

    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Test connection
    try:
        r.ping()
        print("✅ Redis connection successful")
    except:
        print("❌ Redis connection failed - make sure Redis is running")
        return

    # Check active spiders count
    active_spiders = r.scard('active_spiders')
    if active_spiders == 0:
        # Set the spider count
        for i in range(1790):
            r.sadd('active_spiders', f'spider_{i}')
        print("✅ Added 1,790 spiders to active_spiders set")
    else:
        print(f"✅ Found {active_spiders} active spiders")

    # Test opportunities
    test_opportunities = [
        "🚨 URGENT: Hiring senior Python developer for remote position $150k-$180k with full benefits",
        "📢 New contract opportunity: React/Node.js developer needed for 3-month project at $100/hour",
        "💼 Freelance gig: AI consultant needed for startup, equity + $5k monthly retainer",
        "🎯 Job opening: Full-stack developer at tech startup, $120k + stock options, remote-first",
        "💰 Investment opportunity: Early-stage AI company seeking advisors, 1% equity for advisory role",
        "🔥 Immediate need: Django expert for emergency bug fixes, $150/hour, 20 hours estimated",
        "📊 Consulting role: Data scientist advisor for Fortune 500, $300/hour, 10 hours/month",
        "🚀 Startup opportunity: CTO position at funded startup, $200k + 5% equity",
        "Spider Intelligence: Found 15 new job postings matching your profile on Indeed",
        "Market Update: Tech hiring surge detected - 500+ new developer positions this week"
    ]

    print("\n📡 Publishing test opportunities to spider_updates channel...")

    for i, opportunity in enumerate(test_opportunities, 1):
        # Publish to spider_updates channel
        r.publish('spider_updates', opportunity)
        print(f"  {i}. Published: {opportunity[:60]}...")
        time.sleep(2)  # Wait 2 seconds between messages

    print("\n✅ Test complete! Check AI Nexus interface for spider intelligence")
    print("\n💡 Quick test commands for AI Nexus:")
    print("  /spider status - Check spider network status")
    print("  /analyze [data] - Analyze for revenue opportunities")
    print("  /collaborate [task] - Multi-agent collaboration")
    print("  /system status - Full system status with Redis info")

if __name__ == "__main__":
    test_spider_feed()