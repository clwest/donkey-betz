#!/usr/bin/env python3
"""
Test Spider-Agent Bridge System
===============================

This script tests the complete spider-to-agent data pipeline to ensure:
1. Spiders are properly activated and collecting data
2. Agents are receiving and processing spider intelligence
3. Data routing is working correctly
4. Performance metrics are being collected
5. The unified assistant can access real-time intelligence

Usage:
    python test_spider_agent_bridge.py
    python test_spider_agent_bridge.py --quick
    python test_spider_agent_bridge.py --agent content_marketplace_agent
    python test_spider_agent_bridge.py --spider toptal
"""

import asyncio
import json
import logging
import sys
import os
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_donkey_betz.settings')

import django
django.setup()

# Now we can import our modules
from ai_core.spiders.spider_connector_orchestrator import (
    get_spider_connector_orchestrator,
    SpiderConnectorOrchestrator
)
from ai_core.agents.content_marketplace_agent import ContentMarketplaceAgent
from ai_core.agents.spider_data_mixin import enable_spider_data_for_agent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpiderAgentBridgeTest:
    """Comprehensive test suite for the spider-agent bridge system"""

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.orchestrator = get_spider_connector_orchestrator(self.redis_config)
        self.test_results = {
            'spider_activation': {},
            'agent_connection': {},
            'data_flow': {},
            'performance': {},
            'integration': {}
        }

    async def run_comprehensive_test(self, quick_mode: bool = False):
        """Run comprehensive test of the spider-agent bridge"""
        print("\n" + "="*70)
        print("🕷️ SPIDER-AGENT BRIDGE COMPREHENSIVE TEST")
        print("="*70)

        try:
            # Phase 1: Test Spider Activation
            print("\n🕷️ Phase 1: Testing Spider Activation...")
            await self._test_spider_activation(quick_mode)

            # Phase 2: Test Agent Connection
            print("\n🤖 Phase 2: Testing Agent Connection...")
            await self._test_agent_connection()

            # Phase 3: Test Data Flow
            print("\n📡 Phase 3: Testing Data Flow...")
            await self._test_data_flow(quick_mode)

            # Phase 4: Test Performance
            print("\n📊 Phase 4: Testing Performance Metrics...")
            await self._test_performance_metrics()

            # Phase 5: Test Integration
            print("\n🔗 Phase 5: Testing Integration...")
            await self._test_integration()

            # Generate final report
            await self._generate_test_report()

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            print(f"\n❌ Test suite failed: {e}")

    async def _test_spider_activation(self, quick_mode: bool):
        """Test spider activation capabilities"""
        print("  Testing spider activation system...")

        try:
            # Test 1: Get orchestration status
            status = self.orchestrator.get_orchestration_status()
            spider_network = status['spider_network']

            print(f"  📊 Configured spiders: {spider_network['total_configured']}")
            print(f"  📊 Activated spiders: {spider_network['total_activated']}")

            self.test_results['spider_activation']['configured_count'] = spider_network['total_configured']
            self.test_results['spider_activation']['activated_count'] = spider_network['total_activated']

            # Test 2: Activate specific spiders
            if quick_mode:
                test_spiders = ['financial', 'toptal', 'gumroad']
            else:
                test_spiders = ['financial', 'innovation', 'toptal', 'guru', 'medium', 'gumroad']

            print(f"  🎯 Testing activation of {len(test_spiders)} spiders...")

            activation_result = await self.orchestrator.activate_targeted_spiders(test_spiders)

            if activation_result['success']:
                print(f"  ✅ Successfully activated {activation_result['activated']}/{activation_result['total_requested']} spiders")

                for result in activation_result['results']:
                    status_emoji = "✅" if result['status'] == 'activated' else "⚠️"
                    print(f"    {status_emoji} {result['spider']}: {result['status']}")

                self.test_results['spider_activation']['test_activation'] = {
                    'success': True,
                    'activated': activation_result['activated'],
                    'requested': activation_result['total_requested']
                }
            else:
                print(f"  ❌ Spider activation failed: {activation_result.get('error', 'Unknown error')}")
                self.test_results['spider_activation']['test_activation'] = {
                    'success': False,
                    'error': activation_result.get('error')
                }

        except Exception as e:
            logger.error(f"Spider activation test failed: {e}")
            self.test_results['spider_activation']['error'] = str(e)

    async def _test_agent_connection(self):
        """Test agent connection capabilities"""
        print("  Testing agent connection system...")

        try:
            # Test 1: Create and test ContentMarketplaceAgent
            print("  🤖 Testing ContentMarketplaceAgent integration...")

            agent = ContentMarketplaceAgent()

            # Check if spider data is enabled
            spider_enabled = agent.spider_data_enabled
            print(f"    Spider data enabled: {spider_enabled}")

            if spider_enabled:
                # Get spider data metrics
                metrics = agent.get_spider_data_metrics()
                print(f"    Agent metrics: {metrics['agent_metrics']}")

                # Get marketplace intelligence summary
                intel_summary = agent.get_marketplace_intelligence_summary()
                print(f"    Intelligence items: {intel_summary['total_intelligence_items']}")

                self.test_results['agent_connection']['content_marketplace_agent'] = {
                    'spider_enabled': spider_enabled,
                    'metrics': metrics,
                    'intelligence_summary': intel_summary
                }
            else:
                print("    ⚠️ Spider data not enabled for agent")

            # Test 2: Test mixin integration with a generic agent
            print("  🔧 Testing spider data mixin integration...")

            class TestAgent:
                def __init__(self):
                    self.name = "test_agent"

            test_agent = TestAgent()

            # Enable spider data for the test agent
            mixin_success = enable_spider_data_for_agent(
                test_agent,
                agent_id='test_agent_mixin',
                agent_type='specialized',
                quality_threshold=0.7
            )

            print(f"    Mixin integration: {'✅ Success' if mixin_success else '❌ Failed'}")

            self.test_results['agent_connection']['mixin_integration'] = {
                'success': mixin_success
            }

        except Exception as e:
            logger.error(f"Agent connection test failed: {e}")
            self.test_results['agent_connection']['error'] = str(e)

    async def _test_data_flow(self, quick_mode: bool):
        """Test data flow between spiders and agents"""
        print("  Testing data flow system...")

        try:
            # Test 1: Check orchestration status
            status = self.orchestrator.get_orchestration_status()
            metrics = status['performance_metrics']

            print(f"    Total data flows: {metrics['total_data_flows']}")
            print(f"    Flow rate: {metrics['data_flow_rate_per_minute']:.1f}/min")
            print(f"    Connection health: {metrics['avg_connection_health']:.1f}%")

            self.test_results['data_flow']['metrics'] = metrics

            # Test 2: Check data routing
            routing = status['data_routing']
            spider_to_agent = routing['spider_to_agent_mappings']
            agent_to_spider = routing['agent_to_spider_mappings']

            print(f"    Spider->Agent mappings: {len(spider_to_agent)}")
            print(f"    Agent->Spider mappings: {len(agent_to_spider)}")

            # Show some sample mappings
            sample_mappings = list(spider_to_agent.items())[:3]
            for spider, agents in sample_mappings:
                print(f"      {spider} → {len(agents)} agents")

            self.test_results['data_flow']['routing'] = {
                'spider_to_agent_count': len(spider_to_agent),
                'agent_to_spider_count': len(agent_to_spider),
                'sample_mappings': dict(sample_mappings)
            }

            # Test 3: Simulate data flow (if not quick mode)
            if not quick_mode:
                print("  🔄 Simulating data flow test...")
                await self._simulate_data_flow_test()

        except Exception as e:
            logger.error(f"Data flow test failed: {e}")
            self.test_results['data_flow']['error'] = str(e)

    async def _simulate_data_flow_test(self):
        """Simulate data flow to test the pipeline"""
        try:
            # Create a test agent to receive data
            test_agent = ContentMarketplaceAgent()

            # Wait a short time for connections to establish
            await asyncio.sleep(5)

            # Check if the agent received any data
            intel_summary = test_agent.get_marketplace_intelligence_summary()
            received_data = intel_summary['total_intelligence_items']

            print(f"    Data received by test agent: {received_data} items")

            if received_data > 0:
                print("    ✅ Data flow test successful")
                self.test_results['data_flow']['simulation'] = {
                    'success': True,
                    'data_received': received_data
                }
            else:
                print("    ⚠️ No data received during test period")
                self.test_results['data_flow']['simulation'] = {
                    'success': False,
                    'data_received': 0
                }

            await test_agent.close()

        except Exception as e:
            logger.error(f"Data flow simulation failed: {e}")
            self.test_results['data_flow']['simulation'] = {
                'success': False,
                'error': str(e)
            }

    async def _test_performance_metrics(self):
        """Test performance monitoring and metrics collection"""
        print("  Testing performance metrics system...")

        try:
            # Get current metrics
            status = self.orchestrator.get_orchestration_status()
            metrics = status['performance_metrics']

            # Calculate performance scores
            connection_health = metrics['avg_connection_health']
            system_uptime = metrics['system_uptime_percentage']

            performance_score = (connection_health + system_uptime) / 2

            print(f"    Connection health: {connection_health:.1f}%")
            print(f"    System uptime: {system_uptime:.1f}%")
            print(f"    Overall performance score: {performance_score:.1f}%")

            # Determine performance level
            if performance_score >= 90:
                performance_level = "Excellent"
                performance_emoji = "🟢"
            elif performance_score >= 75:
                performance_level = "Good"
                performance_emoji = "🟡"
            elif performance_score >= 60:
                performance_level = "Fair"
                performance_emoji = "🟠"
            else:
                performance_level = "Poor"
                performance_emoji = "🔴"

            print(f"    Performance level: {performance_emoji} {performance_level}")

            self.test_results['performance'] = {
                'connection_health': connection_health,
                'system_uptime': system_uptime,
                'performance_score': performance_score,
                'performance_level': performance_level,
                'metrics': metrics
            }

        except Exception as e:
            logger.error(f"Performance metrics test failed: {e}")
            self.test_results['performance']['error'] = str(e)

    async def _test_integration(self):
        """Test integration with the unified assistant system"""
        print("  Testing unified assistant integration...")

        try:
            # Test 1: Check if spiders are providing actionable intelligence
            status = self.orchestrator.get_orchestration_status()
            active_spiders = status['spider_network']['active_spiders']

            print(f"    Active spiders available to assistant: {len(active_spiders)}")

            # Test 2: Verify agent integration
            connected_agents = status['agent_network']['connected_agents']
            print(f"    Agents connected for intelligence: {len(connected_agents)}")

            # Test 3: Check data freshness
            last_update = status['performance_metrics']['last_updated']
            print(f"    Last data update: {last_update}")

            # Test 4: Integration health check
            integration_health = "Good" if len(active_spiders) > 0 and len(connected_agents) > 0 else "Poor"
            print(f"    Integration health: {integration_health}")

            self.test_results['integration'] = {
                'active_spiders': len(active_spiders),
                'connected_agents': len(connected_agents),
                'last_update': last_update,
                'health': integration_health,
                'spider_list': active_spiders,
                'agent_list': connected_agents
            }

        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            self.test_results['integration']['error'] = str(e)

    async def _generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("📊 SPIDER-AGENT BRIDGE TEST REPORT")
        print("="*70)

        # Overall summary
        total_tests = 5
        passed_tests = 0

        for category, results in self.test_results.items():
            if 'error' not in results:
                passed_tests += 1

        success_rate = (passed_tests / total_tests) * 100

        print(f"\n🎯 Test Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success rate: {success_rate:.1f}%")

        # Detailed results
        print(f"\n📋 Detailed Results:")

        # Spider activation results
        spider_results = self.test_results.get('spider_activation', {})
        if 'error' not in spider_results:
            configured = spider_results.get('configured_count', 0)
            activated = spider_results.get('activated_count', 0)
            print(f"   🕷️ Spider Activation: ✅ ({activated}/{configured} spiders)")
        else:
            print(f"   🕷️ Spider Activation: ❌ ({spider_results['error']})")

        # Agent connection results
        agent_results = self.test_results.get('agent_connection', {})
        if 'error' not in agent_results:
            print(f"   🤖 Agent Connection: ✅")
        else:
            print(f"   🤖 Agent Connection: ❌ ({agent_results['error']})")

        # Data flow results
        flow_results = self.test_results.get('data_flow', {})
        if 'error' not in flow_results:
            flow_rate = flow_results.get('metrics', {}).get('data_flow_rate_per_minute', 0)
            print(f"   📡 Data Flow: ✅ ({flow_rate:.1f} msgs/min)")
        else:
            print(f"   📡 Data Flow: ❌ ({flow_results['error']})")

        # Performance results
        perf_results = self.test_results.get('performance', {})
        if 'error' not in perf_results:
            score = perf_results.get('performance_score', 0)
            level = perf_results.get('performance_level', 'Unknown')
            print(f"   📊 Performance: ✅ ({score:.1f}% - {level})")
        else:
            print(f"   📊 Performance: ❌ ({perf_results['error']})")

        # Integration results
        integration_results = self.test_results.get('integration', {})
        if 'error' not in integration_results:
            health = integration_results.get('health', 'Unknown')
            spiders = integration_results.get('active_spiders', 0)
            agents = integration_results.get('connected_agents', 0)
            print(f"   🔗 Integration: ✅ ({spiders} spiders, {agents} agents, {health})")
        else:
            print(f"   🔗 Integration: ❌ ({integration_results['error']})")

        # Save detailed report
        report_file = '/tmp/spider_agent_bridge_test_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'test_timestamp': datetime.now(timezone.utc).isoformat(),
                'success_rate': success_rate,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'results': self.test_results
            }, f, indent=2)

        print(f"\n📁 Detailed report saved: {report_file}")

        # Final verdict
        if success_rate >= 80:
            print(f"\n🎉 OVERALL RESULT: ✅ SUCCESS ({success_rate:.1f}%)")
            print("   The Spider-Agent Bridge is working correctly!")
        else:
            print(f"\n⚠️ OVERALL RESULT: ❌ ISSUES DETECTED ({success_rate:.1f}%)")
            print("   Some components need attention.")

        print("="*70)

    async def test_specific_spider(self, spider_name: str):
        """Test a specific spider activation"""
        print(f"\n🎯 Testing specific spider: {spider_name}")

        try:
            result = await self.orchestrator.activate_targeted_spiders([spider_name])

            if result['success'] and result['activated'] > 0:
                print(f"✅ Spider {spider_name} activated successfully")
            else:
                print(f"❌ Failed to activate spider {spider_name}")
                for spider_result in result['results']:
                    print(f"   {spider_result['spider']}: {spider_result['status']} - {spider_result['message']}")

        except Exception as e:
            print(f"❌ Error testing spider {spider_name}: {e}")

    async def test_specific_agent(self, agent_name: str):
        """Test a specific agent connection"""
        print(f"\n🎯 Testing specific agent: {agent_name}")

        try:
            if agent_name == 'content_marketplace_agent':
                agent = ContentMarketplaceAgent()
                print(f"✅ Agent {agent_name} created successfully")

                # Check spider data status
                if agent.spider_data_enabled:
                    print("✅ Spider data integration enabled")

                    # Get metrics
                    metrics = agent.get_spider_data_metrics()
                    print(f"   Received data: {metrics['agent_metrics']['total_received']}")
                    print(f"   Processed data: {metrics['agent_metrics']['total_processed']}")

                    # Get intelligence summary
                    summary = agent.get_marketplace_intelligence_summary()
                    print(f"   Intelligence items: {summary['total_intelligence_items']}")
                else:
                    print("❌ Spider data integration not enabled")

                await agent.close()
            else:
                print(f"⚠️ Test not implemented for agent: {agent_name}")

        except Exception as e:
            print(f"❌ Error testing agent {agent_name}: {e}")


async def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test Spider-Agent Bridge System')
    parser.add_argument('--quick', action='store_true', help='Run quick test mode')
    parser.add_argument('--spider', type=str, help='Test specific spider')
    parser.add_argument('--agent', type=str, help='Test specific agent')
    parser.add_argument('--redis-host', type=str, default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-db', type=int, default=0, help='Redis database')

    args = parser.parse_args()

    # Redis configuration
    redis_config = {
        'host': args.redis_host,
        'port': args.redis_port,
        'db': args.redis_db
    }

    # Create test instance
    test_suite = SpiderAgentBridgeTest(redis_config)

    try:
        if args.spider:
            await test_suite.test_specific_spider(args.spider)
        elif args.agent:
            await test_suite.test_specific_agent(args.agent)
        else:
            await test_suite.run_comprehensive_test(args.quick)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())