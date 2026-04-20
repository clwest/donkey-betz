#!/usr/bin/env python
"""
SPIDER ACTIVATION SCRIPT
Activate the real job spiders and start feeding data into the system!
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache

# Import the spider
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_core/spiders'))
from ai_core.spiders.real_job_spider import RealJobSpider


async def activate_spider_and_broadcast():
    """Activate the RealJobSpider and broadcast opportunities"""

    print("\n" + "="*80)
    print("🕷️ ACTIVATING REAL JOB SPIDER - SEARCHING FOR REAL OPPORTUNITIES! 🕷️")
    print("="*80 + "\n")

    # Initialize the spider
    spider = RealJobSpider()
    await spider.initialize()

    # Define search keywords based on common skills
    keywords = [
        'python', 'django', 'ai', 'machine learning',
        'react', 'javascript', 'remote', 'freelance',
        'developer', 'engineer', 'full stack'
    ]

    print(f"🔍 Searching with keywords: {', '.join(keywords)}\n")

    # Search for real opportunities
    opportunities = await spider.search_real_jobs(keywords)

    print(f"\n✅ FOUND {len(opportunities)} REAL OPPORTUNITIES!\n")

    # Store opportunities in cache for quick access
    cache.set('latest_opportunities', opportunities, 3600)  # Cache for 1 hour
    cache.set('opportunity_count', len(opportunities), 3600)
    cache.set('spider_last_run', datetime.now().isoformat(), 3600)

    # Calculate statistics
    sources = {}
    total_salary = 0
    salary_count = 0

    for opp in opportunities:
        # Count by source
        source = opp.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1

        # Calculate average salary
        if opp.get('salary_min'):
            total_salary += (opp.get('salary_min', 0) + opp.get('salary_max', 0)) / 2
            salary_count += 1

    avg_salary = total_salary / salary_count if salary_count > 0 else 0

    # Print statistics
    print("📊 SPIDER STATISTICS:")
    print("-" * 40)
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source:20} : {count:3} opportunities")
    print("-" * 40)
    print(f"  Total Opportunities  : {len(opportunities)}")
    print(f"  Average Salary       : ${avg_salary:,.0f}" if avg_salary > 0 else "  Salary data limited")
    print()

    # Display top 5 opportunities
    print("\n🎯 TOP 5 OPPORTUNITIES FOUND:")
    print("="*80)

    for i, opp in enumerate(opportunities[:5], 1):
        print(f"\n{i}. {opp['title']}")
        print(f"   Company: {opp.get('company', 'Unknown')}")
        print(f"   Location: {opp.get('location', 'Remote')}")
        if opp.get('salary_min'):
            print(f"   Salary: ${opp.get('salary_min', 0):,} - ${opp.get('salary_max', 0):,}")
        print(f"   Source: {opp['source']}")
        print(f"   URL: {opp.get('url', 'N/A')[:60]}...")
        print(f"   Match Score: {opp.get('match_score', 0):.0%}")

    # Send to WebSocket consumers
    channel_layer = get_channel_layer()

    # Broadcast to Revenue Opportunities page
    print("\n📡 BROADCASTING TO WEBSOCKET CONSUMERS...")

    try:
        await channel_layer.group_send(
            'revenue_opportunities',
            {
                'type': 'opportunity_update',
                'opportunities': opportunities[:20],  # Send top 20
                'total_count': len(opportunities),
                'timestamp': datetime.now().isoformat()
            }
        )
        print("✅ Sent to Revenue Opportunities consumer")
    except Exception as e:
        print(f"⚠️ Could not send to Revenue Opportunities: {e}")

    # Broadcast to Income Builder
    try:
        await channel_layer.group_send(
            'income_builder',
            {
                'type': 'new_opportunities',
                'count': len(opportunities),
                'opportunities': opportunities[:10],  # Send top 10
                'timestamp': datetime.now().isoformat()
            }
        )
        print("✅ Sent to Income Builder consumer")
    except Exception as e:
        print(f"⚠️ Could not send to Income Builder: {e}")

    # Update AI Nexus with spider status
    try:
        await channel_layer.group_send(
            'ai_nexus',
            {
                'type': 'spider_status',
                'active_spiders': 1,
                'opportunities_found': len(opportunities),
                'last_crawl': datetime.now().isoformat(),
                'sources': list(sources.keys())
            }
        )
        print("✅ Sent spider status to AI Nexus")
    except Exception as e:
        print(f"⚠️ Could not send to AI Nexus: {e}")

    # Store individual opportunities for quick apply
    print("\n💾 STORING OPPORTUNITIES FOR QUICK APPLY...")
    for idx, opp in enumerate(opportunities[:50]):  # Store top 50
        cache.set(f'opportunity_{idx}', opp, 3600)
    print(f"✅ Stored {min(50, len(opportunities))} opportunities in cache")

    # Create revenue potential calculation
    potential_revenue = 0
    for opp in opportunities[:20]:  # Top 20 opportunities
        if opp.get('salary_min'):
            potential_revenue += (opp.get('salary_min', 0) + opp.get('salary_max', 0)) / 2
        else:
            potential_revenue += 75000  # Default estimate

    print(f"\n💰 POTENTIAL REVENUE FROM TOP 20 OPPORTUNITIES: ${potential_revenue:,.0f}")

    # Update system metrics
    cache.set('spider_metrics', {
        'total_opportunities': len(opportunities),
        'active_spiders': 1,
        'potential_revenue': potential_revenue,
        'average_salary': avg_salary,
        'top_sources': sources,
        'last_update': datetime.now().isoformat()
    }, 3600)

    print("\n" + "="*80)
    print("🎊 SPIDER ACTIVATION COMPLETE! DATA IS NOW FLOWING! 🎊")
    print("="*80)

    print("\n📍 Next Steps:")
    print("1. Check http://localhost:8000/opportunities/ to see real jobs")
    print("2. Check http://localhost:8000/income/ for income opportunities")
    print("3. Check http://localhost:8000/ai-nexus/ for spider status")
    print("4. Try Quick Apply on any opportunity!")

    await spider.close()

    return opportunities


async def schedule_spider_runs():
    """Schedule the spider to run periodically"""
    print("\n⏰ SETTING UP SCHEDULED SPIDER RUNS...")

    while True:
        try:
            # Run the spider
            await activate_spider_and_broadcast()

            # Wait 30 minutes before next run
            print(f"\n⏰ Next spider run in 30 minutes...")
            await asyncio.sleep(1800)  # 30 minutes

        except KeyboardInterrupt:
            print("\n🛑 Spider scheduling stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error in spider run: {e}")
            print("Retrying in 5 minutes...")
            await asyncio.sleep(300)  # 5 minutes retry


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Activate Real Job Spiders')
    parser.add_argument('--schedule', action='store_true',
                       help='Run spider on a schedule (every 30 minutes)')
    parser.add_argument('--once', action='store_true', default=True,
                       help='Run spider once (default)')

    args = parser.parse_args()

    if args.schedule:
        print("🕷️ Starting scheduled spider runs (every 30 minutes)...")
        asyncio.run(schedule_spider_runs())
    else:
        print("🕷️ Running spider once...")
        opportunities = asyncio.run(activate_spider_and_broadcast())

        # Save to file for reference
        output_file = 'spider_results.json'
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'count': len(opportunities),
                'opportunities': opportunities[:50]  # Save top 50
            }, f, indent=2)
        print(f"\n📄 Results saved to {output_file}")


if __name__ == "__main__":
    main()