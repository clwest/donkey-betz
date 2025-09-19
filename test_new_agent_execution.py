#!/usr/bin/env python3
"""
Test the new synchronous agent execution endpoints.

Tests all new features including:
- Direct synchronous execution (no Celery needed)
- Listing executable agents
- Test execution with pre-configured data
- Batch agent execution
"""

import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{title:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_result(success: bool, message: str):
    """Print a colored result message"""
    color = GREEN if success else RED
    symbol = "✅" if success else "❌"
    print(f"{symbol} {color}{message}{RESET}")


def test_list_executable_agents():
    """Test listing all executable agents"""
    print_header("Testing: List Executable Agents")

    try:
        response = requests.get(f"{BASE_URL}/api/v1/agents/list-executable/")
        data = response.json()

        if data.get('success'):
            agents = data['data']['agents']
            print_result(True, f"Found {len(agents)} executable agents")

            print(f"\n{BOLD}Available Agents:{RESET}")
            for agent in agents:
                ai_badge = "🤖" if agent['is_ai_enforced'] else "⚙️"
                print(f"  {ai_badge} {agent['name']} ({agent['class_name']})")
                if agent.get('doc'):
                    print(f"      {YELLOW}→ {agent['doc'][:100]}{RESET}")

            features = data['data'].get('features', {})
            print(f"\n{BOLD}Executor Features:{RESET}")
            for feature, enabled in features.items():
                status = "✅" if enabled else "❌"
                print(f"  {status} {feature}: {enabled}")

            return True
        else:
            print_result(False, f"Failed: {data.get('error')}")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_execute_single_agent():
    """Test executing a single agent synchronously"""
    print_header("Testing: Single Agent Execution")

    # Test data for content creation
    request_data = {
        "agent_name": "real_content_creator",
        "task_description": "Create a blog post about AI in healthcare",
        "input_data": {
            "topic": "AI Revolutionizing Healthcare in 2025",
            "type": "blog",
            "keywords": ["AI", "healthcare", "medical technology", "diagnosis"],
            "word_count": 300
        }
    }

    try:
        print(f"{YELLOW}Executing agent: {request_data['agent_name']}{RESET}")
        print(f"Task: {request_data['task_description']}")

        response = requests.post(
            f"{BASE_URL}/api/v1/agents/execute-sync/",
            json=request_data
        )

        data = response.json()

        if data.get('success'):
            result = data['data']
            print_result(True, f"Agent executed successfully!")

            # Display execution stats
            print(f"\n{BOLD}Execution Stats:{RESET}")
            print(f"  ⏱️  Execution Time: {result.get('execution_time', 0):.2f} seconds")

            # Display AI usage stats if available
            ai_stats = result.get('ai_stats', {})
            if ai_stats:
                print(f"\n{BOLD}AI Usage:{RESET}")
                print(f"  🔢 Calls Made: {ai_stats.get('calls_made', 0)}")
                print(f"  📊 Tokens Used: {ai_stats.get('tokens_used', 0)}")
                print(f"  💰 Total Cost: {ai_stats.get('total_cost', '$0.00')}")

            # Display partial result
            if result.get('result'):
                output = str(result['result'])[:500]
                print(f"\n{BOLD}Output Preview:{RESET}")
                print(f"{YELLOW}{output}...{RESET}")

            return True
        else:
            print_result(False, f"Execution failed: {data.get('error')}")
            if data.get('traceback'):
                print(f"\n{RED}Traceback:{RESET}")
                print(data['traceback'][:500])
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_agent_with_test_endpoint():
    """Test using the pre-configured test endpoint"""
    print_header("Testing: Pre-configured Test Execution")

    test_types = ['content', 'job', 'income']

    for test_type in test_types:
        print(f"\n{BOLD}Testing {test_type} agent:{RESET}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/agents/test-execution/",
                json={"agent_type": test_type}
            )

            data = response.json()

            if data.get('success'):
                print_result(True, f"{test_type.capitalize()} agent test passed")

                result = data.get('result', {})
                if result.get('ai_stats'):
                    stats = result['ai_stats']
                    print(f"  → AI Calls: {stats.get('calls_made', 0)}, "
                          f"Tokens: {stats.get('tokens_used', 0)}")
            else:
                print_result(False, f"{test_type} test failed: {data.get('error')}")

        except Exception as e:
            print_result(False, f"Error testing {test_type}: {str(e)}")


def test_batch_execution():
    """Test executing multiple agents"""
    print_header("Testing: Batch Agent Execution")

    batch_request = {
        "agents": [
            {
                "agent_name": "intelligent_job_matcher",
                "task_description": "Find Python developer jobs",
                "input_data": {
                    "skills": ["Python", "Django", "AI"],
                    "location": "remote",
                    "experience_level": "mid"
                }
            },
            {
                "agent_name": "zero_capital_income_generator",
                "task_description": "Generate income plan",
                "input_data": {
                    "target_income": 500,
                    "timeframe_days": 14,
                    "skill_level": "beginner"
                }
            }
        ],
        "execution_mode": "parallel"  # Execute in parallel
    }

    try:
        print(f"{YELLOW}Executing {len(batch_request['agents'])} agents in {batch_request['execution_mode']} mode{RESET}")

        response = requests.post(
            f"{BASE_URL}/api/v1/agents/batch-execute/",
            json=batch_request
        )

        data = response.json()

        if data.get('success'):
            batch_data = data['data']
            print_result(True, f"Batch execution completed!")

            print(f"\n{BOLD}Batch Results:{RESET}")
            print(f"  ✅ Successful: {batch_data['successful']}/{batch_data['total_agents']}")
            print(f"  ❌ Failed: {batch_data['failed']}/{batch_data['total_agents']}")

            # Show individual results
            print(f"\n{BOLD}Individual Agent Results:{RESET}")
            for i, result in enumerate(batch_data['results']):
                agent = batch_request['agents'][i]['agent_name']
                status = "✅" if result['success'] else "❌"
                time = result.get('execution_time', 0)
                print(f"  {status} {agent}: {time:.2f}s")

            return True
        else:
            print_result(False, f"Batch execution failed: {data.get('error')}")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_execution_history():
    """Test getting execution history"""
    print_header("Testing: Execution History")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/agents/execution-history/",
            params={"limit": 5}
        )

        data = response.json()

        if data.get('success'):
            history = data['data']['history']
            print_result(True, f"Retrieved {len(history)} execution records")

            if history:
                print(f"\n{BOLD}Recent Executions:{RESET}")
                for record in history:
                    status = "✅" if record['success'] else "❌"
                    agent = record.get('agent', 'Unknown')
                    time = record.get('execution_time', 0)
                    print(f"  {status} {agent}: {time:.2f}s")
                    if record.get('ai_stats'):
                        stats = record['ai_stats']
                        print(f"      → Tokens: {stats.get('tokens_used', 0)}, "
                              f"Cost: {stats.get('total_cost', '$0.00')}")
            else:
                print(f"{YELLOW}No execution history yet{RESET}")

            return True
        else:
            print_result(False, f"Failed to get history: {data.get('error')}")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print_header("AGENT EXECUTION API TEST SUITE")
    print(f"{YELLOW}Testing new synchronous agent execution endpoints{RESET}")
    print(f"API URL: {BASE_URL}")

    # Track results
    results = []

    # Run tests
    tests = [
        ("List Executable Agents", test_list_executable_agents),
        ("Single Agent Execution", test_execute_single_agent),
        ("Pre-configured Tests", test_agent_with_test_endpoint),
        ("Batch Agent Execution", test_batch_execution),
        ("Execution History", test_execution_history)
    ]

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print_result(False, f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"{BOLD}Results: {passed}/{total} tests passed{RESET}")
    print()

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        color = GREEN if success else RED
        print(f"  {color}{status:8} {test_name}{RESET}")

    # Final verdict
    print()
    if passed == total:
        print(f"{GREEN}{BOLD}🎉 ALL TESTS PASSED! Agents are executing successfully!{RESET}")
    elif passed > 0:
        print(f"{YELLOW}{BOLD}⚠️  PARTIAL SUCCESS: {passed}/{total} tests passed{RESET}")
    else:
        print(f"{RED}{BOLD}❌ ALL TESTS FAILED - Check server logs{RESET}")

    print(f"\n{BLUE}Key Achievement: Agents now execute WITHOUT Celery!{RESET}")
    print(f"{BLUE}You can now test agents immediately via the API.{RESET}")


if __name__ == "__main__":
    main()