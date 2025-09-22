#!/usr/bin/env python3
"""
Run the Freelance Opportunity Spider to find real gigs
"""
import sys
import os
import django
import asyncio
import redis

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.spiders.freelance_opportunity_spider import FreelanceOpportunitySpider

async def main():
    print("🕷️ Starting Freelance Opportunity Spider...")

    # Initialize Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Create spider instance
    spider = FreelanceOpportunitySpider(redis_client=r)

    print("🔍 Hunting for freelance opportunities...")

    # Initialize spider
    await spider.initialize()

    # Run spider with REAL DATA from live APIs!
    opportunities = await spider.find_opportunities(use_real_data=True)

    if opportunities:
        print(f"✅ Found {len(opportunities)} opportunities!")

        # The spider already stores them, but let's show what we found
        for opp in opportunities:
            print(f"  - {opp.title} (${opp.budget} on {opp.platform})")
    else:
        print("❌ No opportunities found.")

    print("\n✨ Spider complete! Check the Freelance Pipeline in the UI.")

if __name__ == "__main__":
    asyncio.run(main())