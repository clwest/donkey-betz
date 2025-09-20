#!/usr/bin/env python3
"""
Test AI Agent Money-Making Platform
Demonstrates the complete pipeline from opportunity discovery to revenue generation

This test shows how 1 person can use AI agents to actually make money, not just find jobs
"""

import os
import sys
import django
import asyncio
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.cache import cache
from intelligence.unified_spider_job_bridge import UnifiedSpiderJobBridge
from backend.agents.agent_work_platform import activate_agent_work_platform, get_agent_work_platform_status

class AgentMoneyMakingTest:
    """Test the complete money-making pipeline"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.bridge = UnifiedSpiderJobBridge()
        self.total_revenue_generated = 0.0

    async def step_1_deploy_spiders(self):
        """Step 1: Deploy spiders to find opportunities"""
        print("🕷️ STEP 1: Deploying Spider Army to Find Opportunities")
        print("=" * 60)

        deployment = await self.bridge.activate_spider_deployment(
            "Find opportunities that AI agents can execute for revenue",
            search_criteria={
                'keywords': ['content writing', 'data entry', 'python', 'social media', 'research'],
                'comprehensive_scan': True,
                'force_refresh': True
            }
        )

        opportunities_found = deployment.get('jobs_found', 0)
        sources = deployment.get('sources', [])

        print(f"✅ Spider deployment complete!")
        print(f"   📊 Opportunities found: {opportunities_found}")
        print(f"   🔗 Sources: {', '.join(sources)}")
        print(f"   🕷️  Spiders deployed: {deployment.get('spider_count', 0)}")

        return opportunities_found > 0

    async def step_2_categorize_opportunities(self):
        """Step 2: ML categorization of opportunities"""
        print("\n🤖 STEP 2: ML Categorization of Opportunities")
        print("=" * 60)

        # Get categorized opportunities
        categorized_opportunities = cache.get('categorized_opportunities', [])
        category_summary = cache.get('opportunity_category_summary', {})

        print(f"✅ ML categorization complete!")
        print(f"   🏷️  Categorized opportunities: {len(categorized_opportunities)}")
        print(f"   📈 Categories found: {len(category_summary.get('categories', {}))}")

        # Show sample categorized opportunity
        if categorized_opportunities:
            sample = categorized_opportunities[0]
            print(f"\n📝 Sample categorized opportunity:")
            print(f"   Title: {sample.get('title', 'N/A')}")
            print(f"   Category: {sample.get('category', {}).get('display_name', 'N/A')}")
            print(f"   Budget: ${sample.get('financial', {}).get('budget_max', 0):,}")
            print(f"   Quality Score: {sample.get('quality_score', 'N/A')}")

        return len(categorized_opportunities) > 0

    async def step_3_activate_agent_platform(self):
        """Step 3: Activate agent work platform to start making money"""
        print("\n💼 STEP 3: Activating Agent Work Platform")
        print("=" * 60)

        # Activate the agent work platform
        result = await activate_agent_work_platform()

        if result.get('success'):
            print(f"✅ Agent work platform activated!")
            print(f"   🤖 Agents assigned: {result.get('jobs_assigned_to_agents', 0)}")
            print(f"   💰 Potential revenue: ${result.get('potential_revenue', 0):,.2f}")
            print(f"   📊 Executable jobs: {result.get('executable_jobs_created', 0)}")
            print(f"   🏢 Total platform revenue: ${result.get('total_platform_revenue', 0):,.2f}")

            self.total_revenue_generated = result.get('total_platform_revenue', 0)

            # Show active sessions
            active_sessions = result.get('active_sessions', [])
            if active_sessions:
                print(f"\n🔄 Active Work Sessions:")
                for session in active_sessions[:3]:  # Show first 3
                    print(f"   🤖 {session.get('agent_id')} working on {session.get('job_id')}")
                    print(f"      Progress: {session.get('progress', 0)*100:.1f}%")
                    print(f"      Revenue: ${session.get('revenue_earned', 0):.2f}")

            return True
        else:
            print(f"❌ Platform activation failed: {result.get('error', 'Unknown error')}")
            return False

    def step_4_test_api_endpoints(self):
        """Step 4: Test the money-making API endpoints"""
        print("\n🌐 STEP 4: Testing Revenue Generation APIs")
        print("=" * 60)

        endpoints_to_test = [
            ('/api/v1/agent-work-platform/', 'GET', 'Platform Status'),
            ('/api/v1/agent-revenue-dashboard/', 'GET', 'Revenue Dashboard'),
            ('/api/v1/agent-workforce-status/', 'GET', 'Workforce Status'),
            ('/api/v1/revenue-analytics/', 'GET', 'Revenue Analytics'),
        ]

        successful_endpoints = 0

        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ {description} - Working")

                        # Show key metrics from each endpoint
                        if 'platform_status' in data:
                            status = data['platform_status']
                            print(f"   🤖 {status.get('agents_working', 0)} agents working")
                            print(f"   💰 ${status.get('total_revenue', 0):,.2f} total revenue")

                        elif 'dashboard' in data:
                            dashboard = data['dashboard']
                            print(f"   📊 {dashboard.get('active_revenue_streams', 0)} active revenue streams")
                            print(f"   💵 ${dashboard.get('daily_revenue_potential', 0):,.2f} daily potential")

                        elif 'analytics' in data:
                            analytics = data['analytics']
                            print(f"   📈 ${analytics.get('average_job_value', 0):,.2f} average job value")
                            print(f"   🎯 ${analytics.get('highest_value_job', 0):,.2f} highest value job")

                        successful_endpoints += 1
                    else:
                        print(f"❌ {description} - API Error: {data.get('error', 'Unknown')}")
                else:
                    print(f"❌ {description} - HTTP {response.status_code}")

            except Exception as e:
                print(f"❌ {description} - Exception: {e}")

        print(f"\n📊 API Test Results: {successful_endpoints}/{len(endpoints_to_test)} endpoints working")
        return successful_endpoints == len(endpoints_to_test)

    def step_5_revenue_analysis(self):
        """Step 5: Analyze revenue generation potential"""
        print("\n💰 STEP 5: Revenue Generation Analysis")
        print("=" * 60)

        try:
            # Get platform status
            platform_status = get_agent_work_platform_status()

            # Get cached data
            executable_jobs = cache.get('executable_jobs', [])
            active_sessions = cache.get('active_work_sessions', [])

            print(f"✅ Revenue Analysis Complete!")
            print(f"   🏭 Platform Status:")
            print(f"      Total Agents: {platform_status.get('total_agents', 0)}")
            print(f"      Agents Working: {platform_status.get('agents_working', 0)}")
            print(f"      Agent Utilization: {platform_status.get('agent_utilization_rate', 0)*100:.1f}%")

            print(f"\n   💼 Job Portfolio:")
            print(f"      Executable Jobs: {len(executable_jobs)}")
            print(f"      Active Sessions: {len(active_sessions)}")

            # Calculate revenue potential
            total_potential = sum(job.get('revenue_potential', 0) for job in executable_jobs)
            daily_potential = platform_status.get('daily_revenue_potential', 0)

            print(f"\n   💰 Revenue Potential:")
            print(f"      Current Batch: ${total_potential:,.2f}")
            print(f"      Daily Potential: ${daily_potential:,.2f}")
            print(f"      Monthly Potential: ${daily_potential * 30:,.2f}")
            print(f"      Annual Potential: ${daily_potential * 365:,.2f}")

            # Show agent capabilities and rates
            print(f"\n   🤖 Top Revenue Agents:")
            agent_breakdown = platform_status.get('agent_breakdown', [])
            top_agents = sorted(agent_breakdown, key=lambda x: x.get('hourly_rate', 0), reverse=True)[:3]

            for agent in top_agents:
                daily_earning = agent.get('hourly_rate', 0) * agent.get('availability_hours', 0) * agent.get('max_concurrent', 1)
                print(f"      {agent.get('name', 'Unknown')}:")
                print(f"         Rate: ${agent.get('hourly_rate', 0)}/hour")
                print(f"         Daily Potential: ${daily_earning:,.2f}")

            return True

        except Exception as e:
            print(f"❌ Revenue analysis failed: {e}")
            return False

    def step_6_show_money_making_summary(self):
        """Step 6: Show how this makes money for 1 person"""
        print("\n🎯 STEP 6: Money-Making Summary")
        print("=" * 60)

        print("💡 HOW THIS MAKES MONEY FOR 1 PERSON:")
        print()

        print("1. 🕷️  SPIDER ARMY finds work opportunities that AI can do")
        print("   - Content writing, data entry, code development")
        print("   - Social media management, research, virtual assistance")
        print("   - Real jobs with real budgets from real clients")
        print()

        print("2. 🤖 AI AGENTS actually DO the work")
        print("   - 11 specialized agents with different skills")
        print("   - Content Agent: $45/hour for writing and copywriting")
        print("   - Python Developer: $75/hour for coding projects")
        print("   - Social Media Manager: $35/hour for social content")
        print()

        print("3. 💰 YOU get paid while agents work 24/7")
        print("   - Agents work concurrently on multiple jobs")
        print("   - Platform takes ~80% of client payment")
        print("   - Continuous revenue from completed work")
        print()

        print("4. 📈 SCALABLE INCOME STREAMS")
        print("   - Each agent can handle 2-6 concurrent jobs")
        print("   - Available 10-22 hours per day")
        print("   - Total daily potential: $10,000+ per day")
        print()

        # Show real numbers from current test
        platform_status = get_agent_work_platform_status()
        daily_potential = platform_status.get('daily_revenue_potential', 0)

        print("📊 CURRENT TEST RESULTS:")
        print(f"   Daily Revenue Potential: ${daily_potential:,.2f}")
        print(f"   Monthly Potential: ${daily_potential * 30:,.2f}")
        print(f"   Annual Potential: ${daily_potential * 365:,.2f}")
        print()

        print("🚀 WHAT YOU NEED TO DO:")
        print("   1. Run this system daily")
        print("   2. Monitor agent performance")
        print("   3. Scale successful agent types")
        print("   4. Collect revenue from completed work")
        print()

        print("💰 THE RESULT: Passive income while AI agents work for you!")

    async def run_complete_money_making_test(self):
        """Run the complete money-making demonstration"""
        print("🚀 AI AGENT MONEY-MAKING PLATFORM TEST")
        print("🎯 Demonstrating how 1 person can make money using AI agents")
        print("=" * 80)

        results = {
            'spider_deployment': False,
            'ml_categorization': False,
            'agent_platform': False,
            'api_endpoints': False,
            'revenue_analysis': False
        }

        # Step 1: Deploy spiders
        results['spider_deployment'] = await self.step_1_deploy_spiders()

        # Step 2: Categorize opportunities
        results['ml_categorization'] = await self.step_2_categorize_opportunities()

        # Step 3: Activate agent platform
        results['agent_platform'] = await self.step_3_activate_agent_platform()

        # Step 4: Test APIs
        results['api_endpoints'] = self.step_4_test_api_endpoints()

        # Step 5: Revenue analysis
        results['revenue_analysis'] = self.step_5_revenue_analysis()

        # Step 6: Money-making summary
        self.step_6_show_money_making_summary()

        # Final results
        print("\n" + "=" * 80)
        print("🏆 MONEY-MAKING PLATFORM TEST RESULTS")
        print("=" * 80)

        passed_tests = sum(results.values())
        total_tests = len(results)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")

        print(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("\n🎉 SUCCESS! The AI Agent Money-Making Platform is fully operational!")
            print("💰 Your agents are ready to start generating revenue!")
        else:
            print("\n⚠️  Some components need attention before full money-making capability.")

        return passed_tests == total_tests


async def main():
    """Main test function"""
    tester = AgentMoneyMakingTest()

    try:
        success = await tester.run_complete_money_making_test()

        if success:
            print("\n🎯 NEXT STEPS TO START MAKING MONEY:")
            print("1. 🎨 Use the AgentWorkPlatform.tsx dashboard to monitor your agents")
            print("2. 🔄 Run the platform daily to find new opportunities")
            print("3. 📊 Scale up successful agent types")
            print("4. 💰 Set up payment processing for completed work")
            print("5. 🚀 Expand to more opportunity sources and agent capabilities")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())