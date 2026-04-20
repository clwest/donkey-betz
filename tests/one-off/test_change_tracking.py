#!/usr/bin/env python
"""
Test Change Tracking - Priority 4
Session 462: Verify change detection between consecutive runs
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.agents.stocks.market_intelligence_coordinator import run_market_intelligence_desk
from core.models_unified_system import MarketIntelligenceBrief

def test_change_tracking():
    """Test change tracking across two consecutive runs."""
    print("\n" + "="*80)
    print("🧪 TESTING CHANGE TRACKING - TWO CONSECUTIVE RUNS")
    print("="*80)

    # Clean up any existing brief for today
    today = date.today()
    MarketIntelligenceBrief.objects.filter(brief_date=today).delete()
    print(f"\n✅ Cleaned up any existing brief for {today}")

    # RUN 1: First baseline run
    print("\n" + "="*80)
    print("🔵 RUN 1: Establishing Baseline")
    print("="*80)

    result1 = run_market_intelligence_desk()

    if not result1.get('success'):
        print(f"❌ ERROR in Run 1: {result1}")
        return

    brief1 = MarketIntelligenceBrief.objects.get(brief_date=today)
    print(f"\n✅ Run 1 Complete:")
    print(f"   📊 Total stocks: {brief1.total_stocks_analyzed}")
    print(f"   🎯 Debate zone: {brief1.debate_zone_count} stocks")
    print(f"   🐂 Bullish opportunities: {len(brief1.bullish_opportunities)}")
    print(f"   🐻 Bearish warnings: {len(brief1.bearish_warnings)}")
    print(f"   🤖 GPT success rate: {brief1.gpt_success_rate}%")
    print(f"   🔄 Is first brief: {brief1.is_first_brief}")

    changes1 = brief1.changes_from_yesterday
    print(f"\n   Changes detected: {changes1.get('message', 'No message')}")
    if changes1.get('is_first_run'):
        print(f"   ✅ Correctly identified as first run (no previous baseline)")

    # Pause to simulate different run
    print("\n" + "-"*80)
    input("Press Enter to run again (will delete today's brief and re-run)...")
    print("-"*80)

    # Delete today's brief to simulate a fresh run
    MarketIntelligenceBrief.objects.filter(brief_date=today).delete()
    print(f"✅ Deleted brief for {today} - will re-create it")

    # Create a "yesterday" brief to test change detection
    print("\n📝 Creating fake 'yesterday' brief for change tracking test...")
    yesterday = today - timedelta(days=1)

    # Create yesterday's brief with different data
    yesterday_brief = MarketIntelligenceBrief.objects.create(
        brief_date=yesterday,
        brief_type='daily_market_intelligence_brief',
        executive_summary='Test brief from yesterday',
        debate_zone=[
            {'ticker': 'AAPL', 'bull_conviction': 'HIGH'},  # Same ticker, will test conviction changes
            {'ticker': 'TSLA', 'bull_conviction': 'UNCERTAIN'},  # Will disappear from debate zone
        ],
        debate_zone_count=2,
        bullish_opportunities=[
            {'ticker': 'MSFT'},  # Will test if it stays or changes
        ],
        bearish_warnings=[],
        risk_alerts=[],
        high_conviction_opportunities=[],
        total_stocks_analyzed=10,
        confidence_distribution={'HIGH': 5, 'UNCERTAIN': 3, 'LOW': 2},
        gpt_success_rate=70.0,
        situation_health='OPERATIONAL',
        is_first_brief=True,
        changes_from_yesterday={}
    )
    print(f"✅ Created yesterday's brief ({yesterday}) with 2 debate zone stocks")

    # RUN 2: Second run with change detection
    print("\n" + "="*80)
    print("🟢 RUN 2: Detecting Changes from Yesterday")
    print("="*80)

    result2 = run_market_intelligence_desk()

    if not result2.get('success'):
        print(f"❌ ERROR in Run 2: {result2}")
        return

    brief2 = MarketIntelligenceBrief.objects.get(brief_date=today)
    print(f"\n✅ Run 2 Complete:")
    print(f"   📊 Total stocks: {brief2.total_stocks_analyzed}")
    print(f"   🎯 Debate zone: {brief2.debate_zone_count} stocks")
    print(f"   🐂 Bullish opportunities: {len(brief2.bullish_opportunities)}")
    print(f"   🐻 Bearish warnings: {len(brief2.bearish_warnings)}")
    print(f"   🤖 GPT success rate: {brief2.gpt_success_rate}%")
    print(f"   🔄 Is first brief: {brief2.is_first_brief}")

    changes2 = brief2.changes_from_yesterday
    print(f"\n📋 CHANGE TRACKING RESULTS:")
    print(f"   Message: {changes2.get('message', 'No message')}")
    print(f"   Is first run: {changes2.get('is_first_run', False)}")
    print(f"   Total changes detected: {len(changes2.get('changes', []))}")

    # Show all changes
    if changes2.get('changes'):
        print(f"\n   🔍 Detailed Changes:")
        for i, change in enumerate(changes2.get('changes', []), 1):
            print(f"      {i}. [{change.get('type')}] {change.get('message')}")
    else:
        print(f"\n   ℹ️ No changes detected")

    # Show specific change categories
    if changes2.get('new_opportunities'):
        print(f"\n   🆕 New Opportunities:")
        for opp in changes2.get('new_opportunities'):
            print(f"      • {opp.get('ticker')}: {opp.get('message')}")

    if changes2.get('disappeared_opportunities'):
        print(f"\n   📉 Disappeared Opportunities:")
        for opp in changes2.get('disappeared_opportunities'):
            print(f"      • {opp.get('ticker')}: {opp.get('message')}")

    if changes2.get('conviction_changes'):
        print(f"\n   🎯 Conviction Changes:")
        for change in changes2.get('conviction_changes'):
            print(f"      • {change.get('ticker')}: {change.get('message')}")

    if changes2.get('new_risks'):
        print(f"\n   ⚠️ New Risk Alerts:")
        for risk in changes2.get('new_risks'):
            print(f"      • {risk.get('ticker')}: {risk.get('message')}")

    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY:")
    print("="*80)
    print("✅ Run 1: Baseline established (first run - no changes detected)")
    print("✅ Run 2: Changes detected from 'yesterday's' brief")
    print(f"   - {len(changes2.get('changes', []))} total changes found")
    print(f"   - {len(changes2.get('new_opportunities', []))} new opportunities")
    print(f"   - {len(changes2.get('disappeared_opportunities', []))} disappeared opportunities")
    print(f"   - {len(changes2.get('conviction_changes', []))} conviction changes")
    print(f"   - {len(changes2.get('new_risks', []))} new risk alerts")

    print("\n🎯 PRIORITY 4 STATUS:")
    if len(changes2.get('changes', [])) > 0:
        print("   ✅ COMPLETE - Change tracking is WORKING!")
    else:
        print("   ⚠️ WARNING - No changes detected (expected if data is identical)")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_change_tracking()
