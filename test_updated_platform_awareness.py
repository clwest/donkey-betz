#!/usr/bin/env python3
"""
Test Updated Platform Awareness
Tests the enhanced platform integration to ensure agents recommend internal tools
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path


def test_enhanced_platform_awareness():
    """Test the enhanced platform awareness with API integration"""
    print("🚀 Testing Enhanced Platform Awareness")
    print("="*60)

    api_base = "http://localhost:8000"

    # Test digital template creation with platform awareness
    test_data = {
        "plan": {
            "steps": [
                "Create professional digital templates for social media marketing",
                "Design brand consistency package with logos and colors",
                "Set up automated sales and distribution system",
                "Create marketing campaign for template launch"
            ],
            "timeline": "2 weeks",
            "expected_outcome": "Platform-aware recommendations test"
        },
        "opportunity": {
            "id": "enhanced_digital_templates_test",
            "title": "Enhanced AI-Generated Digital Templates",
            "description": "Create and sell professional templates using ONLY internal platform capabilities"
        }
    }

    try:
        print("📝 Creating test plan with enhanced platform awareness...")

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
                time.sleep(5)

                # Check for generated files
                output_dir = Path("income_builder_outputs")

                # Look for files related to our test
                test_files = list(output_dir.glob("*Enhanced*"))

                if test_files:
                    print(f"📄 Found {len(test_files)} generated files:")
                    for file in test_files:
                        print(f"   • {file.name}")

                    # Analyze the most recent file
                    latest_file = max(test_files, key=lambda f: f.stat().st_mtime)
                    print(f"\n📖 Analyzing: {latest_file.name}")

                    with open(latest_file, 'r') as f:
                        content = f.read()

                    # Check for platform tool recommendations
                    platform_tools = [
                        'ai content studio',
                        'dall-e',
                        'stable diffusion',
                        'design-agent',
                        'content-creator',
                        'marketing-agent',
                        'revenue engine',
                        'api/v1/',
                        'platform tools',
                        'internal tools',
                        'specialized agents'
                    ]

                    external_tools = [
                        'canva',
                        'gumroad',
                        'etsy',
                        'fiverr',
                        'bubble.io',
                        'product hunt',
                        'mailchimp',
                        'shopify'
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

                    print(f"\n🎯 ANALYSIS RESULTS:")
                    print(f"   Platform tools mentioned: {len(platform_mentions)}")
                    print(f"   External tools mentioned: {len(external_mentions)}")

                    if platform_mentions:
                        print(f"   ✅ Platform tools found: {', '.join(platform_mentions[:5])}")

                    if external_mentions:
                        print(f"   ⚠️ External tools found: {', '.join(external_mentions)}")

                    # Calculate platform awareness score
                    total_mentions = len(platform_mentions) + len(external_mentions)
                    if total_mentions > 0:
                        platform_score = (len(platform_mentions) / total_mentions) * 100
                        print(f"   📊 Platform Awareness Score: {platform_score:.1f}%")

                        if platform_score >= 80:
                            print("   🎉 EXCELLENT: Platform awareness is working!")
                        elif platform_score >= 50:
                            print("   ✅ GOOD: Platform awareness is improving")
                        else:
                            print("   ⚠️ NEEDS WORK: Still mentioning external tools")
                    else:
                        print("   📝 No specific tool mentions found")

                    # Show content snippet
                    print(f"\n📄 Content Preview:")
                    print("-" * 50)
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print("-" * 50)

                else:
                    print("❌ No generated files found")

            return True

        else:
            print(f"❌ Plan creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_enhanced_platform_awareness()
    if success:
        print("\n✅ Enhanced platform awareness test completed")
    else:
        print("\n❌ Enhanced platform awareness test failed")