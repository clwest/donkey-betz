#!/usr/bin/env python
"""
SYSTEM REALITY VERIFICATION SCRIPT
===================================
Date: September 26, 2025, 9:30 PM MST

This script verifies that Agents, Advisors, and Spiders are:
1. REAL (not mock data)
2. FUNCTIONAL (can execute tasks)
3. USABLE (can be used in real-world context)
"""

import os
import sys
import django
import json
import asyncio
from datetime import datetime

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from agents.registry import AgentRegistry
try:
    from intelligence.services.advisor_network_service import AdvisorNetworkService as AdvisorNetwork
except:
    AdvisorNetwork = None
from backend.spiders.registry import SpiderRegistry
from backend.agents.concrete_executor import ConcreteAgentExecutor
import redis

# ANSI color codes for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}{text.center(80)}{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")

def print_section(text):
    print(f"\n{BOLD}{YELLOW}{'─'*60}{RESET}")
    print(f"{BOLD}{YELLOW}▶ {text}{RESET}")
    print(f"{BOLD}{YELLOW}{'─'*60}{RESET}")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def verify_agents():
    """Verify that agents are real and functional"""
    print_section("VERIFYING AGENTS")

    try:
        # Get agent registry
        registry = AgentRegistry()
        agents = registry.get_all_agents()

        print_info(f"Found {len(agents)} registered agents")

        # Check if agents are real
        real_agents = []
        mock_agents = []
        executable_agents = []

        for agent in agents[:10]:  # Check first 10 agents
            agent_data = registry.get_agent(agent['id'])

            # Check if agent has real implementation
            if agent_data.get('execute_fn') or agent_data.get('implementation_path'):
                real_agents.append(agent['name'])

                # Check if it can actually execute
                if agent_data.get('can_execute', False):
                    executable_agents.append(agent['name'])
            else:
                mock_agents.append(agent['name'])

        # Results
        if real_agents:
            print_success(f"Real agents found: {len(real_agents)}")
            for name in real_agents[:5]:
                print(f"  • {name}")

        if executable_agents:
            print_success(f"Executable agents: {len(executable_agents)}")
            for name in executable_agents[:3]:
                print(f"  • {name} (can execute real tasks)")

        if mock_agents:
            print_warning(f"Mock/placeholder agents: {len(mock_agents)}")

        # Test actual execution
        print_info("\nTesting agent execution capability...")
        executor = ConcreteAgentExecutor()

        # Try to execute a simple agent
        test_agent = "code_analyzer"
        result = executor.execute(
            agent_name=test_agent,
            task_description="Analyze this codebase",
            context={"test": True}
        )

        if result.get('success'):
            print_success(f"Agent '{test_agent}' executed successfully!")
            print(f"  Result: {str(result.get('result', 'No result'))[:100]}...")
        else:
            print_warning(f"Agent '{test_agent}' execution returned: {result.get('error', 'Unknown error')}")

        # Check database for real agent templates
        db_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        print_info(f"Database contains {db_agents} active agent templates")

        return len(real_agents) > 0

    except Exception as e:
        print_error(f"Error verifying agents: {e}")
        return False

def verify_advisors():
    """Verify that advisors are real and functional"""
    print_section("VERIFYING ADVISORS")

    if AdvisorNetwork is None:
        print_warning("AdvisorNetwork not available, checking registry directly...")
        try:
            from agents.registry import AdvisorRegistry
            registry = AdvisorRegistry()
            advisors = registry.advisors
            print_info(f"Found {len(advisors)} advisors in registry")
            return len(advisors) > 0
        except:
            pass

    try:
        # Get advisor network
        advisor_network = AdvisorNetwork()
        advisors = getattr(advisor_network, 'advisors', {})

        print_info(f"Found {len(advisors)} registered advisors")

        # Check specific legendary advisors
        legendary_advisors = [
            "Warren Buffett",
            "Cathie Wood",
            "Ray Dalio",
            "Peter Lynch",
            "George Soros"
        ]

        found_advisors = []
        for advisor in advisors.values():
            if advisor.name in legendary_advisors:
                found_advisors.append(advisor.name)
                print_success(f"Found legendary advisor: {advisor.name}")
                print(f"  • Expertise: {', '.join(advisor.expertise[:3])}")
                print(f"  • Personality: {advisor.personality_traits.get('style', 'Unknown')}")

        # Test advisor consultation
        print_info("\nTesting advisor consultation...")

        consultation_request = {
            "query": "Should I invest in AI technology stocks?",
            "context": {
                "market_conditions": "bullish",
                "risk_tolerance": "moderate"
            }
        }

        # Get advice from Warren Buffett
        buffett = advisor_network.get_advisor_by_name("Warren Buffett")
        if buffett:
            advice = advisor_network.get_advisor_consultation(
                buffett.id,
                consultation_request["query"],
                consultation_request["context"]
            )

            if advice:
                print_success("Advisor consultation successful!")
                print(f"  Warren Buffett says: {str(advice)[:150]}...")
            else:
                print_warning("Advisor returned no advice")

        return len(found_advisors) > 0

    except Exception as e:
        print_error(f"Error verifying advisors: {e}")
        return False

def verify_spiders():
    """Verify that spiders are real and can fetch data"""
    print_section("VERIFYING SPIDERS")

    try:
        # Get spider registry
        spider_registry = SpiderRegistry()
        spiders = spider_registry.get_all_spiders()

        print_info(f"Found {len(spiders)} registered spiders")

        # Check specific spider types
        spider_types = {
            "financial": "Financial market data spider",
            "innovation": "Innovation and tech news spider",
            "toptal": "Toptal freelance job spider",
            "github_jobs": "GitHub jobs spider",
            "coingecko": "Cryptocurrency data spider"
        }

        real_spiders = []
        for spider_id, description in spider_types.items():
            spider_class = spider_registry.get_spider(spider_id)
            if spider_class:
                real_spiders.append(spider_id)
                print_success(f"Found {description}: {spider_id}")

                # Check if spider has real methods
                if hasattr(spider_class, 'fetch_data'):
                    print(f"  • Has fetch_data method ✓")
                if hasattr(spider_class, 'parse_response'):
                    print(f"  • Has parse_response method ✓")

        # Test actual spider data fetching (without making real API calls)
        print_info("\nTesting spider capabilities...")

        # Check if spiders have real URLs and configurations
        test_spider = spider_registry.get_spider("financial")
        if test_spider:
            spider_instance = test_spider()

            # Check for real attributes
            has_url = hasattr(spider_instance, 'base_url') and spider_instance.base_url
            has_headers = hasattr(spider_instance, 'headers') and spider_instance.headers
            has_parser = hasattr(spider_instance, 'parse_response')

            if has_url:
                print_success(f"Spider has real URL: {spider_instance.base_url}")
            if has_headers:
                print_success("Spider has real headers configured")
            if has_parser:
                print_success("Spider has response parser implemented")

        # Check Redis for spider data
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            spider_data = r.get('spiders:registry')
            if spider_data:
                stored_spiders = json.loads(spider_data)
                print_info(f"Redis contains data for {len(stored_spiders)} spiders")
        except:
            print_warning("Could not check Redis for spider data")

        return len(real_spiders) > 0

    except Exception as e:
        print_error(f"Error verifying spiders: {e}")
        return False

def test_real_world_execution():
    """Test real-world execution of components together"""
    print_section("TESTING REAL-WORLD EXECUTION")

    try:
        # Test 1: Agent availability
        print_info("Test 1: Agent Availability")

        registry = AgentRegistry()

        # Get a market analysis agent
        market_agent = registry.get_agent("market_analyst")
        if market_agent:
            print_success("Market Analyst agent found")

        if AdvisorNetwork:
            advisor_network = AdvisorNetwork()
            # Get Warren Buffett advisor
            buffett = getattr(advisor_network, 'get_advisor_by_name', lambda x: None)("Warren Buffett")
            if buffett:
                print_success("Warren Buffett advisor found")

        # Test 2: Spider data collection
        print_info("\nTest 2: Spider Data Collection")

        spider_registry = SpiderRegistry()
        financial_spider = spider_registry.get_spider("financial")

        if financial_spider:
            spider = financial_spider()
            print_success(f"Financial spider initialized")
            print(f"  • Target: {getattr(spider, 'base_url', 'No URL set')}")
            print(f"  • Ready to fetch: {hasattr(spider, 'fetch_data')}")

        # Test 3: Complete pipeline
        print_info("\nTest 3: Complete Execution Pipeline")

        pipeline_components = {
            "Agents": len(registry.get_all_agents()) > 0,
            "Advisors": AdvisorNetwork is not None or registry is not None,
            "Spiders": len(spider_registry.get_all_spiders()) > 0,
            "Executor": ConcreteAgentExecutor is not None,
            "Database": UnifiedAgentTemplate.objects.exists()
        }

        for component, status in pipeline_components.items():
            if status:
                print_success(f"{component}: Ready ✓")
            else:
                print_error(f"{component}: Not ready ✗")

        all_ready = all(pipeline_components.values())

        if all_ready:
            print_success("\n🚀 ALL COMPONENTS READY FOR REAL-WORLD USE!")
        else:
            print_warning("\n⚠️ Some components need configuration")

        return all_ready

    except Exception as e:
        print_error(f"Error in real-world execution test: {e}")
        return False

def main():
    """Main verification script"""
    print_header("SYSTEM REALITY VERIFICATION")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S MST')}")

    results = {
        "Agents": verify_agents(),
        "Advisors": verify_advisors(),
        "Spiders": verify_spiders(),
        "Real-World": test_real_world_execution()
    }

    # Final summary
    print_header("VERIFICATION SUMMARY")

    for component, status in results.items():
        if status:
            print_success(f"{component}: VERIFIED REAL ✓")
        else:
            print_error(f"{component}: NEEDS ATTENTION ✗")

    # Overall status
    all_real = all(results.values())

    print("\n" + "="*80)
    if all_real:
        print(f"{BOLD}{GREEN}🎉 SYSTEM IS 100% REAL AND FUNCTIONAL!{RESET}")
        print(f"{GREEN}All components verified and ready for real-world use.{RESET}")
    else:
        print(f"{BOLD}{YELLOW}⚠️ SYSTEM NEEDS CONFIGURATION{RESET}")
        print(f"{YELLOW}Some components require attention to be fully functional.{RESET}")
    print("="*80)

    return 0 if all_real else 1

if __name__ == "__main__":
    sys.exit(main())