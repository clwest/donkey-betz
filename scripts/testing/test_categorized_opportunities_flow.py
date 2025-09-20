#!/usr/bin/env python3
"""
Test Categorized Opportunities End-to-End Flow
Tests the complete ML categorization pipeline from spider deployment to frontend display
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
from ml_pipeline.opportunity_categorizer import get_opportunity_categorizer

class CategorizedOpportunitiesFlowTest:
    """Test the complete categorized opportunities flow"""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.bridge = UnifiedSpiderJobBridge()
        self.test_results = {
            'spider_deployment': False,
            'ml_categorization': False,
            'api_endpoints': False,
            'cache_persistence': False,
            'frontend_ready': False
        }

    async def test_spider_deployment(self):
        """Test 1: Spider deployment and job collection"""
        print("🕷️ Testing spider deployment...")

        try:
            # Deploy spiders with categorization
            deployment = await self.bridge.activate_spider_deployment(
                "Test categorized opportunities flow",
                search_criteria={
                    'keywords': ['python', 'ai', 'remote', 'freelance'],
                    'comprehensive_scan': True,
                    'force_refresh': True
                }
            )

            jobs_found = deployment.get('jobs_found', 0)
            categorized_jobs = deployment.get('categorized_jobs', 0)

            print(f"   ✅ Spider deployment successful!")
            print(f"   📊 Jobs found: {jobs_found}")
            print(f"   🏷️  Categorized jobs: {categorized_jobs}")
            print(f"   🔗 Sources: {deployment.get('sources', [])}")

            self.test_results['spider_deployment'] = jobs_found > 0
            return deployment

        except Exception as e:
            print(f"   ❌ Spider deployment failed: {e}")
            return None

    async def test_ml_categorization(self):
        """Test 2: ML categorization system"""
        print("🤖 Testing ML categorization...")

        try:
            # Get categorizer
            categorizer = get_opportunity_categorizer()

            # Test sample opportunity
            sample_opportunity = {
                'title': 'Python Developer - Remote',
                'description': 'Looking for experienced Python developer to work on AI projects',
                'company': 'Tech Startup',
                'salary': '$80k-120k',
                'location': 'Remote'
            }

            # Categorize single opportunity (await the coroutine)
            categorized = await categorizer.categorize_opportunity(sample_opportunity)

            print(f"   ✅ ML categorization successful!")
            print(f"   🏷️  Category: {categorized.get('category', {}).get('display_name', 'Unknown')}")
            print(f"   💰 Financial info: {categorized.get('financial', {})}")
            print(f"   ⭐ Quality score: {categorized.get('quality_score', 0)}")

            self.test_results['ml_categorization'] = True
            return categorized

        except Exception as e:
            print(f"   ❌ ML categorization failed: {e}")
            return None

    def test_api_endpoints(self):
        """Test 3: API endpoints"""
        print("🌐 Testing API endpoints...")

        endpoints = [
            '/api/v1/categorized-opportunities/',
            '/api/v1/category-stats/'
        ]

        results = {}

        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    results[endpoint] = {
                        'status': 'success',
                        'data': data
                    }
                    print(f"   ✅ {endpoint} - Success")

                    if endpoint == '/api/v1/categorized-opportunities/':
                        opportunities_count = len(data.get('opportunities', []))
                        print(f"      📊 Opportunities returned: {opportunities_count}")

                    elif endpoint == '/api/v1/category-stats/':
                        categories_count = len(data.get('summary', {}).get('categories', {}))
                        print(f"      🏷️  Categories available: {categories_count}")

                else:
                    results[endpoint] = {
                        'status': 'error',
                        'code': response.status_code,
                        'message': response.text[:200]
                    }
                    print(f"   ❌ {endpoint} - Failed ({response.status_code})")

            except Exception as e:
                results[endpoint] = {
                    'status': 'exception',
                    'error': str(e)
                }
                print(f"   ❌ {endpoint} - Exception: {e}")

        # Test POST endpoint
        try:
            url = f"{self.base_url}/api/v1/categorized-opportunities/"
            response = requests.post(url,
                json={'search_criteria': {'keywords': ['test'], 'force_refresh': True}},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ POST categorized-opportunities - Success")
                print(f"      🕷️  Spiders deployed: {data.get('spiders_deployed', 0)}")
            else:
                print(f"   ❌ POST categorized-opportunities - Failed ({response.status_code})")

        except Exception as e:
            print(f"   ❌ POST categorized-opportunities - Exception: {e}")

        self.test_results['api_endpoints'] = any(
            r.get('status') == 'success' for r in results.values()
        )

        return results

    def test_cache_persistence(self):
        """Test 4: Cache persistence"""
        print("💾 Testing cache persistence...")

        try:
            # Check categorized opportunities cache
            categorized_opportunities = cache.get('categorized_opportunities', [])
            category_summary = cache.get('opportunity_category_summary', {})
            unified_jobs = cache.get('unified_live_jobs', [])

            print(f"   ✅ Cache access successful!")
            print(f"   📊 Categorized opportunities: {len(categorized_opportunities)}")
            print(f"   🏷️  Category summary: {len(category_summary.get('categories', {}))}")
            print(f"   💼 Unified jobs: {len(unified_jobs)}")

            # Show sample categorized opportunity
            if categorized_opportunities:
                sample = categorized_opportunities[0]
                print(f"   📝 Sample opportunity:")
                print(f"      Title: {sample.get('title', 'N/A')}")
                print(f"      Category: {sample.get('category', {}).get('display_name', 'N/A')}")
                print(f"      Quality: {sample.get('quality_score', 'N/A')}")

            self.test_results['cache_persistence'] = len(categorized_opportunities) > 0
            return True

        except Exception as e:
            print(f"   ❌ Cache persistence failed: {e}")
            return False

    def test_frontend_readiness(self):
        """Test 5: Frontend component readiness"""
        print("🎨 Testing frontend readiness...")

        try:
            # Check if CategorizedOpportunityHub component exists
            component_path = "/Users/donkeyking/development/unified-donkey-betz/frontend/src/components/CategorizedOpportunityHub.tsx"

            if os.path.exists(component_path):
                print(f"   ✅ CategorizedOpportunityHub component exists")

                # Check component content
                with open(component_path, 'r') as f:
                    content = f.read()

                required_features = [
                    'categorized-opportunities',  # API endpoint
                    'useState',  # React hooks
                    'useEffect',  # React hooks
                    'Card',  # UI components
                    'Badge',  # UI components
                ]

                feature_checks = {}
                for feature in required_features:
                    feature_checks[feature] = feature in content
                    status = "✅" if feature_checks[feature] else "❌"
                    print(f"      {status} {feature}")

                self.test_results['frontend_ready'] = all(feature_checks.values())
                return True
            else:
                print(f"   ❌ CategorizedOpportunityHub component not found")
                return False

        except Exception as e:
            print(f"   ❌ Frontend readiness check failed: {e}")
            return False

    async def run_complete_test(self):
        """Run the complete end-to-end test"""
        print("🚀 Starting Categorized Opportunities End-to-End Test")
        print("=" * 60)

        # Test 1: Spider deployment
        deployment = await self.test_spider_deployment()
        print()

        # Test 2: ML categorization
        await self.test_ml_categorization()
        print()

        # Test 3: API endpoints
        self.test_api_endpoints()
        print()

        # Test 4: Cache persistence
        self.test_cache_persistence()
        print()

        # Test 5: Frontend readiness
        self.test_frontend_readiness()
        print()

        # Final results
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())

        for test_name, passed in self.test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")

        print()
        print(f"Overall Result: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Categorized opportunities flow is working!")
        else:
            print("⚠️  Some tests failed. Review the output above for details.")

        return passed_tests == total_tests


async def main():
    """Main test function"""
    tester = CategorizedOpportunitiesFlowTest()

    try:
        success = await tester.run_complete_test()

        if success:
            print("\n🎯 NEXT STEPS:")
            print("1. Add CategorizedOpportunityHub to your React router")
            print("2. Test the frontend component with real data")
            print("3. Configure category filters and sorting preferences")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())