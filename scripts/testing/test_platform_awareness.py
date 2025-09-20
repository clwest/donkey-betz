#!/usr/bin/env python3
"""
Test Platform Awareness in Income Builder

This script tests whether the Income Builder now recommends internal platform
tools instead of external ones after the platform awareness injection.
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path


class PlatformAwarenessTest:
    """Test platform awareness in Income Builder recommendations"""

    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.test_results = {}

    def test_digital_templates_recommendation(self):
        """Test recommendations for digital template creation"""
        print("🎨 Testing Digital Template Creation Recommendations...")

        try:
            # Create a plan for digital template business
            api_url = f"{self.api_base}/api/v1/intelligence/income-builder/execute/"

            test_data = {
                "plan": {
                    "steps": [
                        "Create professional digital templates for social media",
                        "Design brand consistency templates",
                        "Set up sales and distribution channels",
                        "Create marketing materials"
                    ],
                    "timeline": "2 weeks",
                    "expected_outcome": "Platform awareness test for design tools"
                },
                "opportunity": {
                    "id": "digital_templates_platform_test",
                    "title": "AI-Generated Digital Templates",
                    "description": "Create and sell professional digital templates using platform capabilities"
                }
            }

            response = requests.post(api_url, json=test_data, timeout=30)

            if response.status_code in [200, 201]:
                data = response.json()
                plan_id = data.get('plan_id')

                if plan_id:
                    print(f"✅ Plan created: {plan_id}")

                    # Wait a bit for processing
                    time.sleep(3)

                    # Get the plan results
                    results = self.get_plan_results(plan_id)

                    # Analyze for platform vs external tool recommendations
                    analysis = self.analyze_tool_recommendations(results)

                    self.test_results['digital_templates'] = {
                        'status': 'SUCCESS',
                        'plan_id': plan_id,
                        'analysis': analysis,
                        'raw_results': results
                    }

                    return analysis
                else:
                    print("❌ No plan ID returned")
                    return None
            else:
                print(f"❌ API failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error: {e}")
            self.test_results['digital_templates'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return None

    def test_content_creation_recommendation(self):
        """Test recommendations for content creation business"""
        print("✍️ Testing Content Creation Recommendations...")

        try:
            # Create a plan for content creation business
            api_url = f"{self.api_base}/api/v1/intelligence/income-builder/execute/"

            test_data = {
                "plan": {
                    "steps": [
                        "Create blog content writing service",
                        "Design marketing materials",
                        "Set up client acquisition system",
                        "Create content templates and workflows"
                    ],
                    "timeline": "2 weeks",
                    "expected_outcome": "Platform awareness test for content tools"
                },
                "opportunity": {
                    "id": "content_creation_platform_test",
                    "title": "AI-Powered Content Writing Service",
                    "description": "Create a content writing service using platform AI capabilities"
                }
            }

            response = requests.post(api_url, json=test_data, timeout=30)

            if response.status_code in [200, 201]:
                data = response.json()
                plan_id = data.get('plan_id')

                if plan_id:
                    print(f"✅ Plan created: {plan_id}")

                    # Wait a bit for processing
                    time.sleep(3)

                    # Get the plan results
                    results = self.get_plan_results(plan_id)

                    # Analyze for platform vs external tool recommendations
                    analysis = self.analyze_tool_recommendations(results)

                    self.test_results['content_creation'] = {
                        'status': 'SUCCESS',
                        'plan_id': plan_id,
                        'analysis': analysis,
                        'raw_results': results
                    }

                    return analysis
                else:
                    print("❌ No plan ID returned")
                    return None
            else:
                print(f"❌ API failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error: {e}")
            self.test_results['content_creation'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            return None

    def get_plan_results(self, plan_id):
        """Get results from a completed plan"""
        print(f"📊 Getting results for plan {plan_id}...")

        try:
            # Poll the plans endpoint to get results
            api_url = f"{self.api_base}/api/v1/intelligence/income-builder/"

            response = requests.get(api_url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                plans = data.get('plans', [])

                # Find our plan
                for plan in plans:
                    if plan.get('id') == plan_id:
                        return plan

                print(f"⚠️ Plan {plan_id} not found in {len(plans)} plans")
                return None
            else:
                print(f"❌ Failed to get plans: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error getting plan results: {e}")
            return None

    def analyze_tool_recommendations(self, plan_data):
        """Analyze plan data for platform vs external tool recommendations"""
        if not plan_data:
            return {
                'platform_tools_mentioned': 0,
                'external_tools_mentioned': 0,
                'platform_awareness_score': 0,
                'recommendations': []
            }

        # Convert plan data to text for analysis
        plan_text = json.dumps(plan_data, indent=2).lower()

        # Platform tools to look for
        platform_tools = [
            'ai content studio',
            'dall·e',
            'dall-e',
            'stable diffusion',
            'design-agent',
            'content-creator agent',
            'content-creator',
            'marketing-agent',
            'coding-agent',
            'image/video pipeline',
            'revenue engine',
            'ml analytics',
            'specialized agents',
            '102 agents',
            'platform capabilities',
            'internal tools',
            'unified platform'
        ]

        # External tools to avoid
        external_tools = [
            'canva',
            'gumroad',
            'etsy',
            'fiverr',
            'upwork',
            'freelancer',
            'mailchimp',
            'wordpress',
            'squarespace',
            'shopify',
            'google analytics'
        ]

        platform_mentions = []
        external_mentions = []

        # Check for platform tool mentions
        for tool in platform_tools:
            if tool in plan_text:
                platform_mentions.append(tool)

        # Check for external tool mentions
        for tool in external_tools:
            if tool in plan_text:
                external_mentions.append(tool)

        # Calculate platform awareness score
        total_mentions = len(platform_mentions) + len(external_mentions)
        platform_score = (len(platform_mentions) / total_mentions * 100) if total_mentions > 0 else 0

        analysis = {
            'platform_tools_mentioned': len(platform_mentions),
            'external_tools_mentioned': len(external_mentions),
            'platform_awareness_score': platform_score,
            'platform_mentions': platform_mentions,
            'external_mentions': external_mentions,
            'recommendations': self.extract_recommendations(plan_data)
        }

        print(f"📈 Platform Awareness Score: {platform_score:.1f}%")
        print(f"🔧 Platform tools mentioned: {len(platform_mentions)}")
        print(f"🌐 External tools mentioned: {len(external_mentions)}")

        return analysis

    def extract_recommendations(self, plan_data):
        """Extract key recommendations from plan data"""
        recommendations = []

        if not plan_data:
            return recommendations

        # Look for recommendations in various fields
        for key, value in plan_data.items():
            if isinstance(value, str) and any(keyword in value.lower() for keyword in ['recommend', 'use', 'tool', 'platform']):
                recommendations.append(f"{key}: {value}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and any(keyword in item.lower() for keyword in ['recommend', 'use', 'tool', 'platform']):
                        recommendations.append(f"{key}: {item}")

        return recommendations[:10]  # Limit to top 10

    def generate_report(self):
        """Generate comprehensive platform awareness report"""
        print("\n" + "="*80)
        print("🧠 PLATFORM AWARENESS TEST REPORT")
        print("="*80)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r.get('status') == 'SUCCESS')

        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print()

        overall_platform_score = 0
        overall_external_mentions = 0

        for test_name, result in self.test_results.items():
            print(f"📋 {test_name.replace('_', ' ').title()}:")

            if result.get('status') == 'SUCCESS':
                analysis = result.get('analysis', {})
                platform_score = analysis.get('platform_awareness_score', 0)
                platform_mentions = analysis.get('platform_tools_mentioned', 0)
                external_mentions = analysis.get('external_tools_mentioned', 0)

                print(f"   ✅ Platform Awareness Score: {platform_score:.1f}%")
                print(f"   🔧 Platform Tools: {platform_mentions}")
                print(f"   🌐 External Tools: {external_mentions}")

                overall_platform_score += platform_score
                overall_external_mentions += external_mentions

                # Show specific mentions
                if analysis.get('platform_mentions'):
                    print(f"   Platform mentions: {', '.join(analysis['platform_mentions'][:3])}")
                if analysis.get('external_mentions'):
                    print(f"   External mentions: {', '.join(analysis['external_mentions'][:3])}")

            elif result.get('error'):
                print(f"   ❌ Error: {result['error']}")

            print()

        # Overall assessment
        avg_platform_score = overall_platform_score / successful_tests if successful_tests > 0 else 0

        print("🎯 OVERALL ASSESSMENT:")
        print(f"   Average Platform Awareness Score: {avg_platform_score:.1f}%")
        print(f"   Total External Tool Mentions: {overall_external_mentions}")

        if avg_platform_score >= 80:
            print("   🎉 EXCELLENT: Platform awareness is working well!")
        elif avg_platform_score >= 50:
            print("   ⚠️ GOOD: Platform awareness is partially working.")
        else:
            print("   ❌ POOR: Platform awareness needs improvement.")

        # Save report
        report_file = Path("income_builder_outputs") / f"platform_awareness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump({
                'test_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'avg_platform_score': avg_platform_score,
                    'total_external_mentions': overall_external_mentions
                },
                'test_results': self.test_results
            }, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")

    def run_all_tests(self):
        """Run all platform awareness tests"""
        print("🚀 Starting Platform Awareness Tests")
        print("="*60)

        self.test_digital_templates_recommendation()
        print()
        self.test_content_creation_recommendation()

        self.generate_report()


if __name__ == "__main__":
    tester = PlatformAwarenessTest()
    tester.run_all_tests()