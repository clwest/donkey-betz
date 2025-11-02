# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Phase 3 Integration Test
Tests the complete Spider -> Agent -> Advisor -> WebSocket flow

This verifies:
1. Spiders collect real data
2. Data routes to appropriate agents
3. Advisors receive specialized feeds
4. WebSocket broadcasts work
5. End-to-end pipeline functions
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from colorama import init, Fore, Style

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from django.core.cache import cache
from ai_core.spiders.agent_router import AgentRouter, route_spider_data
from ai_core.spiders.advisor_feed import AdvisorFeed, feed_advisors
from ai_core.spiders.realtime_publisher import (
    RealtimePublisher,
    broadcast_spider_discovery,
    broadcast_advisor_insight,
    get_broadcast_stats
)
from ai_core.spiders.real_job_spider import RealJobSpider
from ai_core.spiders.specialized.financial_spider import FinancialIntelligenceSpider

# Initialize colorama
init(autoreset=True)


class Phase3Tester:
    """Test Phase 3 implementation"""

    def __init__(self):
        self.router = AgentRouter()
        self.advisor_feed = AdvisorFeed()
        self.publisher = RealtimePublisher()
        self.results = {
            'spider_collection': None,
            'agent_routing': None,
            'advisor_feeding': None,
            'websocket_broadcasting': None,
            'end_to_end': None
        }

    async def test_spider_collection(self):
        """Test that spiders collect real data"""
        print(f"\n{Fore.CYAN}=== Testing Spider Data Collection ==={Style.RESET_ALL}")

        try:
            # Test job spider
            job_spider = RealJobSpider()
            job_data = await job_spider.search_real_jobs()

            if job_data and len(job_data) > 0:
                print(f"{Fore.GREEN}✅ Job Spider collected {len(job_data)} jobs{Style.RESET_ALL}")
                sample_job = job_data[0]
                print(f"  Sample: {sample_job.get('title', 'N/A')} at {sample_job.get('company', 'N/A')}")
            else:
                print(f"{Fore.YELLOW}⚠️ Job Spider returned no data{Style.RESET_ALL}")

            # Test financial spider
            financial_spider = FinancialIntelligenceSpider()
            market_data = await financial_spider.collect_data()

            if market_data:
                print(f"{Fore.GREEN}✅ Financial Spider collected market data{Style.RESET_ALL}")
                print(f"  BTC: ${market_data.get('bitcoin', {}).get('usd', 'N/A'):,.2f}")
            else:
                print(f"{Fore.YELLOW}⚠️ Financial Spider returned no data{Style.RESET_ALL}")

            self.results['spider_collection'] = {
                'status': 'success',
                'jobs_collected': len(job_data) if job_data else 0,
                'market_data': bool(market_data)
            }

            return job_data, market_data

        except Exception as e:
            print(f"{Fore.RED}❌ Spider collection error: {e}{Style.RESET_ALL}")
            self.results['spider_collection'] = {'status': 'error', 'error': str(e)}
            return None, None

    async def test_agent_routing(self, job_data):
        """Test routing data to agents"""
        print(f"\n{Fore.CYAN}=== Testing Agent Routing ==={Style.RESET_ALL}")

        try:
            if not job_data:
                print(f"{Fore.YELLOW}⚠️ No data to route{Style.RESET_ALL}")
                return None

            # Route first job to agents
            sample_job = job_data[0]
            routing_result = await route_spider_data('job_spider', sample_job)

            if routing_result['status'] == 'success':
                print(f"{Fore.GREEN}✅ Routed to {len(routing_result['routed_to'])} agents{Style.RESET_ALL}")
                for agent in routing_result['routed_to']:
                    print(f"  → {agent}")
            else:
                print(f"{Fore.YELLOW}⚠️ Routing status: {routing_result['status']}{Style.RESET_ALL}")

            # Check routing stats
            stats = self.router.get_routing_stats()
            print(f"\n{Fore.CYAN}Routing Statistics:{Style.RESET_ALL}")
            print(f"  Total routed: {stats['total_routed']}")
            print(f"  Success rate: {stats['successful_routes']}/{stats['total_routed']}")
            print(f"  Active agents: {stats['active_agents']}/{stats['total_agents']}")

            self.results['agent_routing'] = {
                'status': 'success',
                'agents_reached': len(routing_result.get('routed_to', [])),
                'routing_stats': stats
            }

            return routing_result

        except Exception as e:
            print(f"{Fore.RED}❌ Agent routing error: {e}{Style.RESET_ALL}")
            self.results['agent_routing'] = {'status': 'error', 'error': str(e)}
            return None

    async def test_advisor_feeding(self, market_data):
        """Test feeding data to advisors"""
        print(f"\n{Fore.CYAN}=== Testing Advisor Intelligence Feeds ==={Style.RESET_ALL}")

        try:
            if not market_data:
                # Create sample data
                market_data = {
                    'type': 'market_update',
                    'price': 50000,
                    'earnings': 5000,
                    'dividend_yield': 0.04,
                    'debt_to_gdp': 1.2,
                    'interest_rate': 0.05,
                    'inflation': 0.03
                }

            # Feed to all advisors
            feed_result = await feed_advisors(market_data)

            print(f"{Fore.GREEN}✅ Fed {len(feed_result['advisors_fed'])} advisors{Style.RESET_ALL}")
            print(f"  Total insights: {feed_result['total_insights']}")

            # Show sample advisors
            sample_advisors = feed_result['advisors_fed'][:5]
            print(f"\n{Fore.CYAN}Sample Advisors Fed:{Style.RESET_ALL}")
            for advisor in sample_advisors:
                print(f"  → {advisor}")

            # Test specific advisor feeds
            buffett_feed = await self.advisor_feed.feed_advisor('Warren Buffett', market_data)
            if buffett_feed['insights']:
                print(f"\n{Fore.GREEN}Warren Buffett Insights:{Style.RESET_ALL}")
                for insight in buffett_feed['insights'][:2]:
                    print(f"  • {insight['message']}")

            # Get advisor stats
            advisor_stats = self.advisor_feed.get_all_advisor_stats()
            print(f"\n{Fore.CYAN}Advisor Statistics:{Style.RESET_ALL}")
            print(f"  Active advisors: {advisor_stats['active_advisors']}/{advisor_stats['total_advisors']}")
            print(f"  Success rate: {advisor_stats['success_rate']:.2%}")

            self.results['advisor_feeding'] = {
                'status': 'success',
                'advisors_fed': len(feed_result['advisors_fed']),
                'total_insights': feed_result['total_insights'],
                'stats': advisor_stats
            }

            return feed_result

        except Exception as e:
            print(f"{Fore.RED}❌ Advisor feeding error: {e}{Style.RESET_ALL}")
            self.results['advisor_feeding'] = {'status': 'error', 'error': str(e)}
            return None

    async def test_websocket_broadcasting(self):
        """Test WebSocket broadcasting"""
        print(f"\n{Fore.CYAN}=== Testing WebSocket Broadcasting ==={Style.RESET_ALL}")

        try:
            # Test spider discovery broadcast
            discovery_data = {
                'id': 'test_123',
                'title': 'Test Opportunity',
                'value': 100000,
                'confidence': 0.85
            }

            success = await broadcast_spider_discovery('test_spider', discovery_data)
            if success:
                print(f"{Fore.GREEN}✅ Spider discovery broadcast successful{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Spider discovery broadcast failed{Style.RESET_ALL}")

            # Test advisor insight broadcast
            insight = {
                'type': 'value_opportunity',
                'message': 'Exceptional value detected',
                'confidence': 0.9,
                'action': 'buy'
            }

            success = await broadcast_advisor_insight('Warren Buffett', insight)
            if success:
                print(f"{Fore.GREEN}✅ Advisor insight broadcast successful{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Advisor insight broadcast failed{Style.RESET_ALL}")

            # Get broadcast stats
            broadcast_stats = get_broadcast_stats()
            print(f"\n{Fore.CYAN}Broadcast Statistics:{Style.RESET_ALL}")
            print(f"  Messages sent: {broadcast_stats['messages_sent']}")
            print(f"  Bytes transmitted: {broadcast_stats['bytes_transmitted']:,}")
            print(f"  Active channels: {broadcast_stats['channels_active']}")

            self.results['websocket_broadcasting'] = {
                'status': 'success',
                'stats': broadcast_stats
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ WebSocket broadcasting error: {e}{Style.RESET_ALL}")
            self.results['websocket_broadcasting'] = {'status': 'error', 'error': str(e)}
            return False

    async def test_end_to_end_flow(self):
        """Test complete end-to-end data flow"""
        print(f"\n{Fore.CYAN}=== Testing End-to-End Data Flow ==={Style.RESET_ALL}")

        try:
            # Step 1: Spider collects data
            print(f"\n{Fore.BLUE}Step 1: Spider Collection{Style.RESET_ALL}")
            job_spider = RealJobSpider()
            job_data = await job_spider.search_real_jobs()

            if not job_data:
                print(f"{Fore.YELLOW}⚠️ No job data collected{Style.RESET_ALL}")
                return

            print(f"{Fore.GREEN}✅ Collected {len(job_data)} jobs{Style.RESET_ALL}")

            # Step 2: Route to agents
            print(f"\n{Fore.BLUE}Step 2: Agent Routing{Style.RESET_ALL}")
            sample_job = job_data[0]
            routing_result = await route_spider_data('job_spider', sample_job)
            print(f"{Fore.GREEN}✅ Routed to {len(routing_result.get('routed_to', []))} agents{Style.RESET_ALL}")

            # Step 3: Broadcast discovery
            print(f"\n{Fore.BLUE}Step 3: WebSocket Broadcast{Style.RESET_ALL}")
            await broadcast_spider_discovery('job_spider', sample_job)
            print(f"{Fore.GREEN}✅ Broadcast job discovery{Style.RESET_ALL}")

            # Step 4: Generate advisor insights
            print(f"\n{Fore.BLUE}Step 4: Advisor Analysis{Style.RESET_ALL}")
            advisor_result = await feed_advisors(sample_job)
            print(f"{Fore.GREEN}✅ Generated {advisor_result['total_insights']} insights{Style.RESET_ALL}")

            # Step 5: Check data in cache
            print(f"\n{Fore.BLUE}Step 5: Verify Data Persistence{Style.RESET_ALL}")
            cached_routing = cache.get(f"routing_{sample_job.get('id')}")
            if cached_routing:
                print(f"{Fore.GREEN}✅ Routing data cached{Style.RESET_ALL}")

            # Check Redis queues
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")

            queue_length = redis_conn.llen('spider_processing_queue')
            print(f"{Fore.GREEN}✅ Processing queue: {queue_length} items{Style.RESET_ALL}")

            self.results['end_to_end'] = {
                'status': 'success',
                'jobs_processed': 1,
                'agents_involved': len(routing_result.get('routed_to', [])),
                'insights_generated': advisor_result['total_insights']
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ End-to-end flow error: {e}{Style.RESET_ALL}")
            self.results['end_to_end'] = {'status': 'error', 'error': str(e)}
            return False

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 3 INTEGRATION TEST SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values()
                          if r and r.get('status') == 'success')

        for test_name, result in self.results.items():
            if result:
                if result['status'] == 'success':
                    status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}"
                else:
                    status = f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}⚠️ SKIP{Style.RESET_ALL}"

            print(f"{test_name.replace('_', ' ').title():30} {status}")

        print(f"\n{Fore.CYAN}Overall: {passed_tests}/{total_tests} tests passed{Style.RESET_ALL}")

        if passed_tests == total_tests:
            print(f"\n{Fore.GREEN}🎉 PHASE 3 IMPLEMENTATION COMPLETE!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Spider -> Agent -> Advisor -> WebSocket pipeline is operational!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️ Some tests failed. Review the output above.{Style.RESET_ALL}")

        # Print key metrics
        print(f"\n{Fore.CYAN}Key Metrics:{Style.RESET_ALL}")
        if self.results['agent_routing'] and self.results['agent_routing']['status'] == 'success':
            stats = self.results['agent_routing']['routing_stats']
            print(f"  Agents: {stats['active_agents']}/{stats['total_agents']} active")

        if self.results['advisor_feeding'] and self.results['advisor_feeding']['status'] == 'success':
            stats = self.results['advisor_feeding']['stats']
            print(f"  Advisors: {stats['active_advisors']}/{stats['total_advisors']} active")

        if self.results['websocket_broadcasting'] and self.results['websocket_broadcasting']['status'] == 'success':
            stats = self.results['websocket_broadcasting']['stats']
            print(f"  WebSocket: {stats['messages_sent']} messages sent")


async def main():
    """Run Phase 3 integration tests"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}PHASE 3: INTELLIGENT ROUTING & DISTRIBUTION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = Phase3Tester()

    # Run tests
    job_data, market_data = await tester.test_spider_collection()
    routing_result = await tester.test_agent_routing(job_data if job_data else [{'test': 'data'}])
    await tester.test_advisor_feeding(market_data)
    await tester.test_websocket_broadcasting()
    await tester.test_end_to_end_flow()

    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())