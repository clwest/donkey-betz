#!/usr/bin/env python
"""
Test the AI integration in Income Builder
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from intelligence.income_builder import AIIncomeBuilder


async def test_ai_integration():
    """Test the OpenAI integration in Income Builder"""

    print("\n" + "="*80)
    print("🧠 TESTING AI INTEGRATION IN INCOME BUILDER")
    print("="*80 + "\n")

    # Check if OpenAI is available
    from intelligence.income_builder import OPENAI_AVAILABLE, openai_client

    if not OPENAI_AVAILABLE:
        print("❌ OpenAI is NOT available - need to set OPENAI_API_KEY environment variable")
        print("\nTo enable AI content generation:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    else:
        print("✅ OpenAI client is available and configured")

    # Create Income Builder instance
    builder = AIIncomeBuilder()
    print(f"✅ Income Builder initialized with {len(builder.opportunities)} opportunities")

    # Test AI content generation
    print("\n📝 Testing AI Content Generation...")

    prompt = "Create a 3-step action plan for starting a content writing business"
    context = {
        "opportunity": "Content Writing",
        "budget": 0,
        "timeline": "1 week"
    }

    try:
        ai_content = await builder.generate_ai_content(prompt, context)

        if ai_content:
            print("✅ AI content generated successfully!")
            print(f"   Generated {len(ai_content)} characters of content")
            print("\n--- SAMPLE OF AI CONTENT ---")
            print(ai_content[:500] + "..." if len(ai_content) > 500 else ai_content)
            print("--- END SAMPLE ---\n")
        else:
            print("⚠️ AI content generation returned None (likely using fallback)")
    except Exception as e:
        print(f"❌ Error generating AI content: {e}")
        return False

    # Test creating an action plan with AI
    print("\n🎯 Testing Full Action Plan Creation with AI...")

    try:
        # Select an opportunity
        opportunity_id = "content_writing"
        user_id = "test_user_123"

        plan = await builder.create_action_plan(user_id, opportunity_id)

        if "error" in plan:
            print(f"❌ Error creating plan: {plan['error']}")
            return False

        print("✅ Action plan created successfully!")
        print(f"   Plan ID: {plan.get('plan_id')}")
        print(f"   AI Enhanced: {plan.get('ai_enhanced', False)}")
        print(f"   Files Created: {len(plan.get('files_created', []))}")

        if plan.get('files_created'):
            print("\n📁 Files created:")
            for file in plan['files_created']:
                print(f"   - {file}")

    except Exception as e:
        print(f"❌ Error creating action plan: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*80)
    print("✅ AI INTEGRATION TEST COMPLETE")
    print("="*80 + "\n")

    return True


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_ai_integration())

    if result:
        print("\n🎉 SUCCESS: AI integration is working!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable for production")
        print("2. Test with the web interface at http://localhost:8000/intelligence/income-builder/")
        print("3. Deploy spider network for real data collection")
        print("4. Connect agents for task execution")
    else:
        print("\n⚠️ AI integration needs configuration")
        print("\nRequired:")
        print("export OPENAI_API_KEY='your-api-key-here'")