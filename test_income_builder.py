#!/usr/bin/env python
"""Test Income Builder functionality"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import asyncio
from intelligence.income_builder import AIIncomeBuilder

async def test_income_builder():
    """Test the Income Builder with real data"""
    print("=" * 60)
    print("INCOME BUILDER TEST")
    print("=" * 60)

    builder = AIIncomeBuilder()

    # Check connections
    print("\n✓ Checking System Connections:")
    print(f"  - ML Pipeline: {'✅ Available' if builder.ml_pipeline.enhanced_ml_available else '❌ Not available'}")
    print(f"  - Web Search: {'✅ Available' if builder.tools_available.get('web_search') else '❌ Not available'}")
    print(f"  - News API: {'✅ Available' if builder.tools_available.get('news_api') else '❌ Not available'}")
    print(f"  - File Generation: {'✅ Available' if builder.tools_available.get('file_generation') else '❌ Not available'}")

    # Test opportunity analysis
    print("\n✓ Testing Opportunity Analysis...")
    opportunities = await builder.analyze_opportunities({
        'request': 'Find high-paying freelance opportunities in tech'
    })

    print(f"\n✓ Results:")
    print(f"  - Found {len(opportunities)} opportunities")

    if opportunities:
        print("\n✓ First Opportunity Details:")
        opp = opportunities[0]
        print(f"  - Title: {opp.get('title', 'N/A')}")
        print(f"  - Platform: {opp.get('platform', 'N/A')}")
        print(f"  - Budget: ${opp.get('budget', 0):,.2f}")
        print(f"  - Success Probability: {opp.get('success_probability', 0):.1%}")
        print(f"  - Priority: {opp.get('priority', 'N/A')}")

        if 'ml_insights' in opp:
            print("\n✓ ML Insights:")
            insights = opp['ml_insights']
            print(f"  - Revenue Potential: ${insights.get('revenue_potential', 0):,.2f}")
            print(f"  - Risk Level: {insights.get('risk_level', 'N/A')}")
            print(f"  - Recommendation: {insights.get('recommendation', 'N/A')}")

    # Test action plan generation
    if opportunities:
        print("\n✓ Testing Action Plan Generation...")
        plan = await builder.create_action_plan(opportunities[0])
        if plan:
            print(f"  - Action plan created with {len(plan.get('steps', []))} steps")
            if 'steps' in plan and plan['steps']:
                print(f"  - First step: {plan['steps'][0].get('description', 'N/A')}")

    print("\n" + "=" * 60)
    print(f"TEST {'PASSED' if opportunities else 'FAILED'}")
    print("=" * 60)

    return bool(opportunities)

if __name__ == "__main__":
    result = asyncio.run(test_income_builder())
    sys.exit(0 if result else 1)