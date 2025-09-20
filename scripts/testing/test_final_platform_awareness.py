#!/usr/bin/env python3
"""
Final Platform Awareness Test with GPT-4o-mini

This is the definitive test to verify:
1. AI content generation works (no more GPT-5-mini errors)
2. Platform awareness is properly injected
3. Internal tools are recommended over external ones
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path


def test_final_platform_awareness():
    """Final test with fresh data using GPT-4o-mini"""
    print("🎯 FINAL PLATFORM AWARENESS TEST")
    print("="*70)

    api_base = "http://localhost:8000"

    # Create a completely new test opportunity
    test_data = {
        "plan": {
            "steps": [
                "Create custom graphic design templates using AI tools",
                "Build automated content workflow for clients",
                "Set up payment system for design services",
                "Launch marketing campaign for design business"
            ],
            "timeline": "4 weeks",
            "expected_outcome": "Final test of platform-aware AI generation with GPT-4o-mini"
        },
        "opportunity": {
            "id": "final_platform_test_2025",
            "title": "AI-Powered Creative Design Studio",
            "description": "Test complete platform integration with working AI model"
        }
    }

    try:
        print("🚀 Creating final platform awareness test...")

        response = requests.post(
            f"{api_base}/api/v1/intelligence/income-builder/execute/",
            json=test_data,
            timeout=30
        )

        if response.status_code in [200, 201]:
            data = response.json()
            plan_id = data.get('plan_id')
            print(f"✅ Plan created: {plan_id}")

            if plan_id:
                # Wait longer for complete processing
                print("⏳ Waiting for complete AI generation...")
                time.sleep(15)

                # Check for generated files
                output_dir = Path("income_builder_outputs")
                test_files = list(output_dir.glob("*AI-Powered_Creative_Design_Studio*"))

                if test_files:
                    print(f"📄 Found {len(test_files)} generated files:")
                    for file in test_files:
                        print(f"   • {file.name}")

                    # Find the most recent complete plan or step file with actual content
                    content_files = [f for f in test_files if f.suffix == '.md' and 'Complete_Plan' in f.name]

                    if not content_files:
                        content_files = [f for f in test_files if f.suffix == '.md' and 'step_' in f.name]

                    if content_files:
                        latest_file = max(content_files, key=lambda f: f.stat().st_mtime)
                        print(f"\n📖 Analyzing: {latest_file.name}")

                        with open(latest_file, 'r') as f:
                            content = f.read()

                        # Check for AI generation success vs errors
                        ai_errors = [
                            'gpt-5-mini error',
                            'gpt-4o-mini error',
                            'prompt pattern is not compatible',
                            'this prompt pattern is not compatible'
                        ]

                        errors_found = []
                        for error in ai_errors:
                            if error.lower() in content.lower():
                                errors_found.append(error)

                        # Look for actual AI-generated content markers
                        ai_success_markers = [
                            'ai-generated content:',
                            'step 1:',
                            'step 2:',
                            'to create',
                            'you can',
                            'start by',
                            'first,',
                            'next,'
                        ]

                        success_markers_found = []
                        content_lower = content.lower()
                        for marker in ai_success_markers:
                            if marker in content_lower:
                                success_markers_found.append(marker)

                        # Check for platform tool mentions
                        platform_tools = [
                            'ai content studio',
                            'dall-e',
                            'stable diffusion',
                            'design-agent',
                            'content-creator',
                            'marketing-agent',
                            'revenue engine',
                            'platform tools',
                            'internal platform',
                            'specialized agents',
                            'our platform',
                            'api integration'
                        ]

                        external_tools = [
                            'canva',
                            'gumroad',
                            'etsy',
                            'fiverr',
                            'upwork',
                            'shopify',
                            'mailchimp',
                            'freelancer.com'
                        ]

                        platform_mentions = []
                        external_mentions = []

                        for tool in platform_tools:
                            if tool in content_lower:
                                platform_mentions.append(tool)

                        for tool in external_tools:
                            if tool in content_lower:
                                external_mentions.append(tool)

                        # Calculate scores
                        ai_working = len(errors_found) == 0 and len(success_markers_found) > 0
                        ai_score = 100 if ai_working else 0

                        total_mentions = len(platform_mentions) + len(external_mentions)
                        platform_score = (len(platform_mentions) / total_mentions * 100) if total_mentions > 0 else 0

                        print(f"\n🤖 AI GENERATION ANALYSIS:")
                        if ai_working:
                            print(f"   ✅ AI Generation: WORKING ({len(success_markers_found)} success markers)")
                        else:
                            print(f"   ❌ AI Generation: FAILED ({len(errors_found)} errors found)")
                            for error in errors_found:
                                print(f"      • {error}")

                        print(f"\n🎯 PLATFORM AWARENESS ANALYSIS:")
                        print(f"   Platform tools mentioned: {len(platform_mentions)}")
                        print(f"   External tools mentioned: {len(external_mentions)}")

                        if platform_mentions:
                            print(f"   ✅ Platform tools: {', '.join(platform_mentions[:5])}")

                        if external_mentions:
                            print(f"   ⚠️ External tools: {', '.join(external_mentions)}")

                        print(f"\n📊 FINAL SCORES:")
                        print(f"   AI Generation Success: {ai_score}%")
                        print(f"   Platform Awareness: {platform_score:.1f}%")

                        # Overall assessment
                        if ai_score == 100 and platform_score >= 80:
                            print(f"\n🎉 COMPLETE SUCCESS!")
                            print(f"   ✅ AI generation working perfectly")
                            print(f"   ✅ Platform awareness active")
                            print(f"   ✅ Income Builder transformation complete!")
                        elif ai_score == 100 and platform_score >= 50:
                            print(f"\n✅ MAJOR SUCCESS!")
                            print(f"   ✅ AI generation working")
                            print(f"   🔧 Platform awareness needs minor tweaks")
                        elif ai_score == 100:
                            print(f"\n✅ AI WORKING!")
                            print(f"   ✅ AI generation fixed")
                            print(f"   ⚠️ Platform awareness needs improvement")
                        else:
                            print(f"\n⚠️ ISSUES REMAIN")
                            print(f"   ❌ AI generation still has problems")

                        # Show content preview
                        print(f"\n📄 Content Preview:")
                        print("-" * 60)
                        preview = content[:1000].replace('\n\n', '\n')
                        print(preview + "..." if len(content) > 1000 else preview)
                        print("-" * 60)

                        return {
                            'ai_score': ai_score,
                            'platform_score': platform_score,
                            'errors_found': errors_found,
                            'platform_mentions': platform_mentions,
                            'external_mentions': external_mentions,
                            'file_analyzed': latest_file.name
                        }

                    else:
                        print("❌ No content files found")
                        return None
                else:
                    print("❌ No generated files found")
                    return None

        else:
            print(f"❌ Plan creation failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


if __name__ == "__main__":
    result = test_final_platform_awareness()
    if result:
        print(f"\n🏆 FINAL RESULTS:")
        print(f"   AI Generation: {result['ai_score']}%")
        print(f"   Platform Awareness: {result['platform_score']:.1f}%")
        print(f"   File: {result['file_analyzed']}")

        # Calculate starting balance impact
        if result['ai_score'] == 100 and result['platform_score'] >= 80:
            print(f"\n💰 COST IMPACT:")
            print(f"   Starting Balance: $39.26")
            print(f"   Platform transformation: COMPLETE")
            print(f"   Income Builder now showcases internal tools! 🎯")
    else:
        print(f"\n❌ Final test failed - check system status")