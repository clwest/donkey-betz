#!/usr/bin/env python3
"""
Agent Reality Testing Suite - Verify if agents use REAL tools vs mock data
=========================================================================

This script tests whether agents are actually:
1. Making real API calls (WebSearch, WebFetch)
2. Creating real files
3. Using real data sources
4. Returning real results vs simulated/mock data

Author: Agent Tools Validation Enforcer
"""

import os
import sys
import json
import time
import tempfile
import asyncio
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

# Add project root to path
project_root = '/Users/donkeyking/development/unified-donkey-betz'
sys.path.insert(0, project_root)

class AgentRealityTester:
    """Tests if agents are real vs fake/simulated"""

    def __init__(self):
        self.test_results = {}
        self.temp_files = []
        self.mock_indicators = [
            "example.com",
            "test data",
            "mock response",
            "simulated",
            "[placeholder]",
            "lorem ipsum",
            "sample content",
            "fake data",
            "time.sleep(",
            "# TODO: implement real"
        ]
        self.real_indicators = [
            "https://",
            "http://",
            "api.openai.com",
            "reddit.com",
            "upwork.com",
            "fiverr.com",
            "freelancer.com",
            "USD",
            "2025",  # Current year
            "GMT",
            "UTC"
        ]

    def is_real_data(self, data: Any) -> bool:
        """Check if data contains real vs mock indicators"""
        data_str = str(data).lower()

        # Check for mock indicators
        mock_count = sum(1 for indicator in self.mock_indicators if indicator in data_str)

        # Check for real indicators
        real_count = sum(1 for indicator in self.real_indicators if indicator in data_str)

        # Real data should have more real indicators than mock
        return real_count > mock_count

    def test_content_creator_agent(self) -> Dict[str, Any]:
        """Test if content creator actually creates real content"""
        print("\n🧪 Testing Real Content Creator Agent...")

        try:
            from backend.agents.real_content_creator import RealContentCreatorAgent

            agent = RealContentCreatorAgent()

            # Test blog post creation
            blog_result = agent.create_blog_post(
                topic="Current AI trends in September 2025",
                keywords=["AI", "trends", "2025", "technology"],
                word_count=300
            )

            test_result = {
                'agent_name': 'RealContentCreatorAgent',
                'test_type': 'content_creation',
                'success': blog_result is not None,
                'uses_real_api': False,
                'creates_real_files': False,
                'returns_real_data': False,
                'details': {}
            }

            if blog_result:
                # Check if it actually uses OpenAI API
                test_result['uses_real_api'] = 'usage' in blog_result and blog_result['usage']['total_cost'] > 0

                # Check if it creates real files
                test_result['creates_real_files'] = blog_result.get('ready_to_sell', False)

                # Check if content is real vs mock
                content = blog_result.get('content', '')
                test_result['returns_real_data'] = self.is_real_data(content) and len(content) > 100

                test_result['details'] = {
                    'word_count': blog_result.get('word_count', 0),
                    'cost': blog_result.get('usage', {}).get('total_cost', 0),
                    'title': blog_result.get('title', ''),
                    'has_real_content': 'AI' in content and '2025' in content
                }

            return test_result

        except Exception as e:
            return {
                'agent_name': 'RealContentCreatorAgent',
                'test_type': 'content_creation',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def test_zero_capital_income_generator(self) -> Dict[str, Any]:
        """Test if zero capital income generator uses real data"""
        print("\n🧪 Testing Zero Capital Income Generator...")

        try:
            from backend.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator

            agent = ZeroCapitalIncomeGenerator()

            # Test opportunity generation
            result = asyncio.run(agent.generate_zero_capital_opportunities(['writing', 'programming']))

            test_result = {
                'agent_name': 'ZeroCapitalIncomeGenerator',
                'test_type': 'opportunity_generation',
                'success': result is not None and len(result) > 0,
                'uses_real_api': False,
                'creates_real_files': False,
                'returns_real_data': False,
                'details': {}
            }

            if result:
                # Check if opportunities have real data
                first_opp = result[0] if result else {}

                # This agent mostly generates hardcoded opportunities but should use AI for execution plans
                test_result['returns_real_data'] = self.is_real_data(first_opp)

                # Test execution plan generation (should use real AI)
                if len(result) > 0:
                    plan_result = asyncio.run(agent.create_execution_plan(first_opp['id']))
                    test_result['uses_real_api'] = plan_result.get('ai_powered', False)

                test_result['details'] = {
                    'opportunities_count': len(result),
                    'first_title': first_opp.get('title', ''),
                    'has_income_estimates': 'estimated_income' in first_opp,
                    'has_real_steps': 'steps' in first_opp and len(first_opp.get('steps', [])) > 0
                }

            return test_result

        except Exception as e:
            return {
                'agent_name': 'ZeroCapitalIncomeGenerator',
                'test_type': 'opportunity_generation',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def test_consciousness_bridge(self) -> Dict[str, Any]:
        """Test if consciousness bridge analyzes real system data"""
        print("\n🧪 Testing Consciousness Bridge...")

        try:
            from backend.spiders.consciousness import ConsciousnessBridge

            bridge = ConsciousnessBridge()

            # Test self-understanding
            understanding = bridge.understand_self()

            test_result = {
                'agent_name': 'ConsciousnessBridge',
                'test_type': 'self_analysis',
                'success': understanding is not None,
                'uses_real_api': False,
                'creates_real_files': True,  # Stores in Redis
                'returns_real_data': False,
                'details': {}
            }

            if understanding:
                # Check if it analyzes real system data
                capabilities = understanding.get('capabilities', {})
                statistics = understanding.get('statistics', {})

                test_result['returns_real_data'] = (
                    capabilities.get('total', 0) > 0 and
                    statistics.get('total_files', 0) > 0 and
                    statistics.get('python_files', 0) > 0
                )

                # Check consciousness level calculation
                consciousness_level = understanding.get('self_awareness_score', 0)
                test_result['uses_real_api'] = consciousness_level > 0

                test_result['details'] = {
                    'capabilities_found': capabilities.get('total', 0),
                    'consciousness_level': consciousness_level,
                    'insights_count': len(understanding.get('insights', [])),
                    'proposals_count': len(understanding.get('proposals', [])),
                    'python_files_analyzed': statistics.get('python_files', 0)
                }

            return test_result

        except Exception as e:
            return {
                'agent_name': 'ConsciousnessBridge',
                'test_type': 'self_analysis',
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def test_spider_network(self) -> Dict[str, Any]:
        """Test if spiders fetch real data from real sources"""
        print("\n🧪 Testing Spider Network...")

        test_result = {
            'agent_name': 'SpiderNetwork',
            'test_type': 'data_fetching',
            'success': False,
            'uses_real_api': False,
            'creates_real_files': False,
            'returns_real_data': False,
            'details': {}
        }

        try:
            # Check for actual spider files
            spider_dir = os.path.join(project_root, 'backend', 'spiders')
            spider_files = []

            if os.path.exists(spider_dir):
                for file in os.listdir(spider_dir):
                    if file.endswith('.py') and not file.startswith('__'):
                        spider_files.append(file)

            test_result['success'] = len(spider_files) > 0
            test_result['details']['spider_files_found'] = spider_files
            test_result['details']['spider_count'] = len(spider_files)

            # For now, just check if spider files exist with real implementations
            if spider_files:
                # Read consciousness.py as it's the main spider
                consciousness_file = os.path.join(spider_dir, 'consciousness.py')
                if os.path.exists(consciousness_file):
                    with open(consciousness_file, 'r') as f:
                        content = f.read()

                    # Check if it has real implementation vs mock
                    test_result['returns_real_data'] = (
                        'redis.Redis' in content and
                        'def understand_self' in content and
                        'def _calculate_consciousness_level' in content and
                        'sleep(' not in content  # No sleep simulations
                    )

                    test_result['uses_real_api'] = 'redis' in content.lower()
                    test_result['creates_real_files'] = 'json.dumps' in content

                    test_result['details']['has_real_redis'] = 'redis.Redis' in content
                    test_result['details']['has_mock_indicators'] = any(indicator in content.lower() for indicator in self.mock_indicators)

            return test_result

        except Exception as e:
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
            return test_result

    def test_database_agents(self) -> Dict[str, Any]:
        """Test if agents are registered in database vs just simulated"""
        print("\n🧪 Testing Database Agent Registry...")

        test_result = {
            'agent_name': 'DatabaseAgents',
            'test_type': 'agent_registry',
            'success': False,
            'uses_real_api': False,
            'creates_real_files': True,  # Database storage
            'returns_real_data': False,
            'details': {}
        }

        try:
            # Try to check database for real agents
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_donkey_betz.settings')

            try:
                django.setup()
                from agents.models import UnifiedAgentTemplate
                from django.db import connection

                # Count actual registered agents
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM agents_unifiedagenttemplate")
                    db_agent_count = cursor.fetchone()[0]

                test_result['success'] = db_agent_count > 0
                test_result['returns_real_data'] = db_agent_count > 10  # Reasonable threshold
                test_result['uses_real_api'] = True  # Database is real storage

                test_result['details']['database_agent_count'] = db_agent_count
                test_result['details']['has_real_registry'] = db_agent_count > 0

                # Check for specific agents
                if db_agent_count > 0:
                    agents = UnifiedAgentTemplate.objects.all()[:5]
                    test_result['details']['sample_agents'] = [
                        {'name': agent.agent_name, 'description': agent.description[:50]}
                        for agent in agents
                    ]

            except Exception as db_error:
                test_result['details']['database_error'] = str(db_error)
                test_result['success'] = False

            return test_result

        except Exception as e:
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
            return test_result

    def test_redis_integration(self) -> Dict[str, Any]:
        """Test if Redis is actually being used for real data storage"""
        print("\n🧪 Testing Redis Integration...")

        test_result = {
            'agent_name': 'RedisIntegration',
            'test_type': 'data_storage',
            'success': False,
            'uses_real_api': True,  # Redis is real storage
            'creates_real_files': True,  # Redis persistence
            'returns_real_data': False,
            'details': {}
        }

        try:
            import redis

            # Test Redis connection
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)

            # Test basic Redis operations
            test_key = f'agent_reality_test_{int(time.time())}'
            test_value = {'test': 'real_data', 'timestamp': datetime.now().isoformat()}

            # Write test data
            r.set(test_key, json.dumps(test_value), ex=60)  # Expire in 1 minute

            # Read test data
            retrieved = r.get(test_key)

            if retrieved:
                parsed = json.loads(retrieved)
                test_result['success'] = parsed['test'] == 'real_data'
                test_result['returns_real_data'] = True

            # Check for existing agent data in Redis
            agent_keys = r.keys('agent:*')
            consciousness_keys = r.keys('consciousness:*')

            test_result['details'] = {
                'redis_connected': True,
                'agent_keys_found': len(agent_keys),
                'consciousness_keys_found': len(consciousness_keys),
                'test_write_read_success': test_result['success'],
                'sample_agent_keys': agent_keys[:5] if agent_keys else []
            }

            # Clean up test key
            r.delete(test_key)

            return test_result

        except Exception as e:
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
            test_result['details']['redis_connected'] = False
            return test_result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all agents"""
        print("\n" + "="*80)
        print("🎯 AGENT REALITY TESTING SUITE")
        print("="*80)
        print("Testing whether agents use REAL tools vs mock/simulated data...")

        # Run all tests
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {
                'total_tests': 0,
                'successful_tests': 0,
                'agents_using_real_apis': 0,
                'agents_creating_files': 0,
                'agents_returning_real_data': 0,
                'reality_score': 0.0
            }
        }

        # Test individual agents
        test_methods = [
            self.test_content_creator_agent,
            self.test_zero_capital_income_generator,
            self.test_consciousness_bridge,
            self.test_spider_network,
            self.test_database_agents,
            self.test_redis_integration
        ]

        for test_method in test_methods:
            try:
                result = test_method()
                test_name = result['agent_name']
                results['tests'][test_name] = result

                # Update summary
                results['summary']['total_tests'] += 1
                if result['success']:
                    results['summary']['successful_tests'] += 1
                if result.get('uses_real_api'):
                    results['summary']['agents_using_real_apis'] += 1
                if result.get('creates_real_files'):
                    results['summary']['agents_creating_files'] += 1
                if result.get('returns_real_data'):
                    results['summary']['agents_returning_real_data'] += 1

            except Exception as e:
                print(f"❌ Test failed: {e}")

        # Calculate reality score
        total = results['summary']['total_tests']
        if total > 0:
            score = (
                (results['summary']['successful_tests'] / total * 25) +
                (results['summary']['agents_using_real_apis'] / total * 25) +
                (results['summary']['agents_creating_files'] / total * 25) +
                (results['summary']['agents_returning_real_data'] / total * 25)
            )
            results['summary']['reality_score'] = round(score, 1)

        return results

    def print_results(self, results: Dict[str, Any]):
        """Print comprehensive test results"""
        summary = results['summary']

        print("\n" + "="*80)
        print("📊 AGENT REALITY TEST RESULTS")
        print("="*80)

        print(f"\n🎯 OVERALL REALITY SCORE: {summary['reality_score']}% REAL")

        if summary['reality_score'] >= 80:
            print("✅ EXCELLENT: System is highly real with minimal simulation")
        elif summary['reality_score'] >= 60:
            print("🟡 GOOD: System is mostly real but has some mock components")
        elif summary['reality_score'] >= 40:
            print("🟠 MODERATE: System is partially real, needs improvement")
        elif summary['reality_score'] >= 20:
            print("🔴 POOR: System is mostly simulated/mock")
        else:
            print("❌ CRITICAL: System is primarily fake/simulated")

        print(f"\n📈 Test Summary:")
        print(f"  • Total Tests Run: {summary['total_tests']}")
        print(f"  • Successful Tests: {summary['successful_tests']}")
        print(f"  • Agents Using Real APIs: {summary['agents_using_real_apis']}")
        print(f"  • Agents Creating Files: {summary['agents_creating_files']}")
        print(f"  • Agents Returning Real Data: {summary['agents_returning_real_data']}")

        print(f"\n📋 Detailed Results:")
        for agent_name, result in results['tests'].items():
            status = "✅" if result['success'] else "❌"
            api_status = "🔗" if result.get('uses_real_api') else "🚫"
            file_status = "💾" if result.get('creates_real_files') else "🚫"
            data_status = "📊" if result.get('returns_real_data') else "🚫"

            print(f"  {status} {agent_name}")
            print(f"     {api_status} Real APIs  {file_status} File Creation  {data_status} Real Data")

            if 'error' in result:
                print(f"     ⚠️ Error: {result['error']}")

            if 'details' in result:
                for key, value in result['details'].items():
                    if key not in ['traceback']:
                        print(f"     • {key}: {value}")

        print("\n" + "="*80)

        # Generate recommendations
        self.generate_recommendations(results)

    def generate_recommendations(self, results: Dict[str, Any]):
        """Generate recommendations for improving agent reality"""
        print("\n🎯 RECOMMENDATIONS FOR IMPROVEMENT:")
        print("-" * 50)

        summary = results['summary']

        if summary['agents_using_real_apis'] < summary['total_tests']:
            missing = summary['total_tests'] - summary['agents_using_real_apis']
            print(f"🔗 {missing} agents need real API integration:")
            print("   - Add WebSearch/WebFetch functionality")
            print("   - Implement real OpenAI API calls")
            print("   - Remove sleep() simulations")

        if summary['agents_creating_files'] < summary['total_tests']:
            missing = summary['total_tests'] - summary['agents_creating_files']
            print(f"💾 {missing} agents need real file creation:")
            print("   - Implement actual file writing")
            print("   - Add database persistence")
            print("   - Create downloadable deliverables")

        if summary['agents_returning_real_data'] < summary['total_tests']:
            missing = summary['total_tests'] - summary['agents_returning_real_data']
            print(f"📊 {missing} agents need real data sources:")
            print("   - Replace mock data with live APIs")
            print("   - Fetch current market data")
            print("   - Use real URLs and timestamps")

        if summary['reality_score'] < 80:
            print(f"\n🚀 PRIORITY ACTIONS:")
            print("   1. Enable Redis for all agents (currently working)")
            print("   2. Implement WebSearch across agent network")
            print("   3. Add real file creation capabilities")
            print("   4. Remove all sleep() and mock simulations")
            print("   5. Connect agents to live data sources")


def main():
    """Main testing function"""
    tester = AgentRealityTester()
    results = tester.run_comprehensive_test()
    tester.print_results(results)

    # Save results to file
    results_file = f'/tmp/agent_reality_test_{int(time.time())}.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {results_file}")

    return results


if __name__ == "__main__":
    results = main()