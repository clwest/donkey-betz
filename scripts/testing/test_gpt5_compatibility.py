#!/usr/bin/env python3
"""
Test GPT-5-mini Compatibility with Platform Awareness

Tests the updated prompt structure to ensure:
1. GPT-5-mini compatibility (no prompt pattern errors)
2. Platform awareness in AI-generated content
3. Internal tool recommendations over external ones
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path


def test_gpt5_compatibility():
    """Test GPT-5-mini compatibility with updated prompts"""
    print("🚀 Testing GPT-5-mini Compatibility + Platform Awareness")
    print("="*70)

    api_base = "http://localhost:8000"

    # Create a test specifically for design/template work to trigger platform tools
    test_data = {
        "plan": {
            "steps": [
                "Create professional brand identity package with logo and color scheme",
                "Design social media templates for consistent branding",
                "Set up automated content creation workflow",
                "Launch integrated sales system for design services"
            ],
            "timeline": "3 weeks",
            "expected_outcome": "GPT-5-mini compatibility test with platform awareness"
        },
        "opportunity": {
            "id": "gpt5_platform_test",
            "title": "Professional Design Services with Platform Tools",
            "description": "Test GPT-5-mini compatibility while ensuring platform tool recommendations"
        }
    }

    try:
        print("📝 Creating GPT-5-mini compatibility test plan...")

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
                # Wait for processing
                print("⏳ Waiting for plan processing...")
                time.sleep(8)  # Give more time for GPT-5-mini processing

                # Check for generated files
                output_dir = Path("income_builder_outputs")
                test_files = list(output_dir.glob("*Professional_Design_Services*"))

                if test_files:
                    print(f"📄 Found {len(test_files)} generated files:")
                    for file in test_files:
                        print(f"   • {file.name}")

                    # Analyze the most recent .md file (not just JSON)
                    md_files = [f for f in test_files if f.suffix == '.md' and 'step_' in f.name]
                    if md_files:
                        latest_file = max(md_files, key=lambda f: f.stat().st_mtime)
                        print(f"\n📖 Analyzing: {latest_file.name}")

                        with open(latest_file, 'r') as f:
                            content = f.read()

                        # Check for GPT-5-mini errors
                        gpt5_errors = [
                            'gpt-5-mini error',
                            'prompt pattern is not compatible',
                            'try: complete sentences',
                            'avoid single words'
                        ]

                        errors_found = []
                        for error in gpt5_errors:
                            if error.lower() in content.lower():
                                errors_found.append(error)

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
                            'api integration'
                        ]

                        external_tools = [
                            'canva',
                            'gumroad',
                            'etsy',
                            'fiverr',
                            'upwork',
                            'shopify',
                            'mailchimp'
                        ]

                        platform_mentions = []
                        external_mentions = []
                        content_lower = content.lower()

                        for tool in platform_tools:
                            if tool in content_lower:
                                platform_mentions.append(tool)

                        for tool in external_tools:
                            if tool in content_lower:
                                external_mentions.append(tool)

                        print(f"\n🔍 COMPATIBILITY ANALYSIS:")
                        if errors_found:
                            print(f"   ❌ GPT-5-mini Errors: {len(errors_found)}")
                            for error in errors_found:
                                print(f"      • {error}")
                        else:
                            print(f"   ✅ GPT-5-mini Compatibility: PASSED")

                        print(f"\n🎯 PLATFORM AWARENESS ANALYSIS:")
                        print(f"   Platform tools mentioned: {len(platform_mentions)}")
                        print(f"   External tools mentioned: {len(external_mentions)}")

                        if platform_mentions:
                            print(f"   ✅ Platform tools found: {', '.join(platform_mentions[:5])}")

                        if external_mentions:
                            print(f"   ⚠️ External tools found: {', '.join(external_mentions)}")

                        # Calculate scores
                        total_mentions = len(platform_mentions) + len(external_mentions)
                        platform_score = (len(platform_mentions) / total_mentions * 100) if total_mentions > 0 else 0
                        compatibility_score = 100 if not errors_found else 0

                        print(f"\n📊 SCORES:")
                        print(f"   GPT-5-mini Compatibility: {compatibility_score}%")
                        print(f"   Platform Awareness: {platform_score:.1f}%")

                        # Overall assessment
                        if compatibility_score == 100 and platform_score >= 70:
                            print(f"\n🎉 SUCCESS: GPT-5-mini working + Platform awareness active!")
                        elif compatibility_score == 100:
                            print(f"\n✅ PROGRESS: GPT-5-mini working, platform awareness needs improvement")
                        elif platform_score >= 70:
                            print(f"\n⚠️ MIXED: Platform awareness working, GPT-5-mini needs fixes")
                        else:
                            print(f"\n❌ ISSUES: Both compatibility and platform awareness need work")

                        # Show content preview
                        print(f"\n📄 Content Preview (first 800 chars):")
                        print("-" * 60)
                        preview = content[:800].replace('\n\n', '\n')
                        print(preview + "..." if len(content) > 800 else preview)
                        print("-" * 60)

                        return {
                            'compatibility_score': compatibility_score,
                            'platform_score': platform_score,
                            'errors_found': errors_found,
                            'platform_mentions': platform_mentions,
                            'external_mentions': external_mentions
                        }

                    else:
                        print("❌ No .md step files found")
                        return None
                else:
                    print("❌ No generated files found")
                    return None

        else:
            print(f"❌ Plan creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


if __name__ == "__main__":
    result = test_gpt5_compatibility()
    if result:
        print(f"\n🎯 FINAL RESULT:")
        print(f"   Compatibility: {result['compatibility_score']}%")
        print(f"   Platform Awareness: {result['platform_score']:.1f}%")
    else:
        print(f"\n❌ Test completed with issues")