"""
Test Multi-Agent Collaboration Scenarios

Comprehensive testing of the orchestration system with real scenarios.
"""

import asyncio
import json
from datetime import datetime
import logging

# Import all components
from orchestration import orchestrator
from testing_suite import IntegrationTestSuite, AgentCollaborationTest, PerformanceTest, MLPipelineTest
from monitoring_dashboard import monitoring_dashboard
from learning_loop import learning_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_investment_workflow():
    """Test complete investment research and decision workflow"""
    print("\n" + "="*50)
    print("TEST: Investment Research Workflow")
    print("="*50)

    # Create workflow
    workflow_id = await orchestrator.create_workflow(
        name="Test Investment Research",
        template="research_and_invest"
    )

    print(f"Created workflow: {workflow_id}")

    # Execute with test data
    input_data = {
        "budget": 10000,
        "risk_tolerance": "moderate",
        "sectors": ["technology", "cryptocurrency", "healthcare"],
        "timeframe": "6_months",
        "target_return": 0.15  # 15% target return
    }

    print(f"Input: {json.dumps(input_data, indent=2)}")

    try:
        result = await orchestrator.execute_workflow(workflow_id, input_data)

        print("\n✓ Workflow completed successfully!")
        print(f"Status: {result['status']}")
        print(f"Results keys: {list(result['results'].keys())}")

        # Display key results
        if "market_insights" in result["results"]:
            insights = result["results"]["market_insights"]
            print(f"\nMarket Insights:")
            print(f"  - Confidence: {insights.get('confidence', 0):.1%}")

        if "risk_profile" in result["results"]:
            risk = result["results"]["risk_profile"]
            print(f"\nRisk Assessment:")
            print(f"  - Score: {risk.get('score', 0):.2f}")

        if "trade_execution" in result["results"]:
            print(f"\nTrade Execution: {result['results']['trade_execution']}")

        # Performance metrics
        print(f"\nPerformance Metrics:")
        for step_id, metrics in result["performance"].items():
            print(f"  - {metrics['name']}: {metrics['duration']:.2f}s")

        return True

    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        return False


async def test_sports_betting_workflow():
    """Test sports betting analysis workflow"""
    print("\n" + "="*50)
    print("TEST: Sports Betting Analysis Workflow")
    print("="*50)

    # Create workflow
    workflow_id = await orchestrator.create_workflow(
        name="Test Sports Betting",
        template="sports_betting_analysis"
    )

    print(f"Created workflow: {workflow_id}")

    # Execute with test data
    input_data = {
        "sport": "NBA",
        "games": [
            {"home": "Lakers", "away": "Warriors", "date": "2025-01-15"},
            {"home": "Celtics", "away": "Heat", "date": "2025-01-15"}
        ],
        "bankroll": 1000,
        "betting_style": "value",
        "max_risk": 0.05  # 5% of bankroll max risk
    }

    print(f"Input: {json.dumps(input_data, indent=2)}")

    try:
        result = await orchestrator.execute_workflow(workflow_id, input_data)

        print("\n✓ Workflow completed successfully!")
        print(f"Status: {result['status']}")

        # Display recommendations
        if "betting_recommendation" in result["results"]:
            rec = result["results"]["betting_recommendation"]
            print(f"\nBetting Recommendation:")
            print(f"  - Confidence: {rec.get('confidence', 0):.1%}")
            print(f"  - Expected Value: {rec.get('expected_value', 0):.2f}")

        if "optimal_stake" in result["results"]:
            stake = result["results"]["optimal_stake"]
            print(f"\nOptimal Stake: ${stake}")

        return True

    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        return False


async def test_content_generation_workflow():
    """Test AI content generation workflow"""
    print("\n" + "="*50)
    print("TEST: AI Content Generation Workflow")
    print("="*50)

    # Create workflow
    workflow_id = await orchestrator.create_workflow(
        name="Test Content Generation",
        template="ai_content_generation"
    )

    print(f"Created workflow: {workflow_id}")

    # Execute with test data
    input_data = {
        "topic": "The Future of AI in Healthcare",
        "target_audience": "healthcare professionals",
        "content_type": "article",
        "word_count": 2000,
        "tone": "professional",
        "include_visuals": True
    }

    print(f"Input: {json.dumps(input_data, indent=2)}")

    try:
        result = await orchestrator.execute_workflow(workflow_id, input_data)

        print("\n✓ Workflow completed successfully!")
        print(f"Status: {result['status']}")

        # Display content metrics
        if "final_content" in result["results"]:
            content = result["results"]["final_content"]
            print(f"\nContent Generated:")
            print(f"  - Quality Score: {content.get('quality_score', 0):.1%}")
            print(f"  - SEO Score: {content.get('seo_score', 0)}/100")

        return True

    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        return False


async def test_parallel_execution():
    """Test parallel workflow execution"""
    print("\n" + "="*50)
    print("TEST: Parallel Workflow Execution")
    print("="*50)

    # Create multiple workflows
    workflows = []
    for i in range(3):
        workflow_id = await orchestrator.create_workflow(
            name=f"Parallel Test {i}",
            template="research_and_invest"
        )
        workflows.append(workflow_id)

    print(f"Created {len(workflows)} workflows")

    # Execute in parallel
    tasks = []
    for workflow_id in workflows:
        task = orchestrator.execute_workflow(
            workflow_id,
            {"budget": 1000, "risk_tolerance": "low"}
        )
        tasks.append(task)

    print("Executing workflows in parallel...")
    start_time = datetime.now()

    try:
        results = await asyncio.gather(*tasks)
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✓ All workflows completed in {duration:.2f}s")
        print(f"Success rate: {sum(1 for r in results if r['status'] == 'completed')} / {len(results)}")

        return True

    except Exception as e:
        print(f"✗ Parallel execution failed: {e}")
        return False


async def test_monitoring_integration():
    """Test monitoring dashboard integration"""
    print("\n" + "="*50)
    print("TEST: Monitoring Dashboard Integration")
    print("="*50)

    # Start monitoring
    monitoring_task = asyncio.create_task(monitoring_dashboard.start_monitoring())

    # Give monitoring time to initialize
    await asyncio.sleep(2)

    print("Monitoring started")

    # Run a workflow to generate metrics
    workflow_id = await orchestrator.create_workflow(
        name="Monitoring Test",
        template="research_and_invest"
    )

    await orchestrator.execute_workflow(
        workflow_id,
        {"budget": 5000, "risk_tolerance": "high"}
    )

    # Get dashboard data
    dashboard_data = monitoring_dashboard.get_dashboard_data()

    print("\nDashboard Summary:")
    print(f"  - Total Agents: {dashboard_data['summary']['total_agents']}")
    print(f"  - Active Workflows: {dashboard_data['summary']['active_workflows']}")
    print(f"  - Total Alerts: {dashboard_data['summary']['total_alerts']}")

    # Check system metrics
    if "system" in dashboard_data:
        print("\nSystem Health:")
        for metric, data in dashboard_data["system"].items():
            if isinstance(data, dict) and "current" in data:
                print(f"  - {metric}: {data['current']:.1f}%")

    # Stop monitoring
    await monitoring_dashboard.stop_monitoring()
    monitoring_task.cancel()

    return True


async def test_learning_loop():
    """Test learning loop with feedback"""
    print("\n" + "="*50)
    print("TEST: Learning Loop with Feedback")
    print("="*50)

    # Start learning loop
    learning_task = asyncio.create_task(learning_loop.start_learning())

    # Give learning loop time to initialize
    await asyncio.sleep(2)

    print("Learning loop started")

    # Submit user feedback
    feedback_result = await learning_loop.submit_user_feedback(
        target="investment_analyst",
        rating=0.8,
        message="Good recommendations but could be faster",
        category="performance"
    )

    print(f"Feedback submitted: {feedback_result['feedback_id']}")

    # Submit critical feedback
    critical_feedback = await learning_loop.submit_user_feedback(
        target="workflow_orchestrator",
        rating=0.2,
        message="Workflow failed with timeout error",
        category="error"
    )

    print(f"Critical feedback submitted: {critical_feedback['feedback_id']}")

    # Get learning status
    status = learning_loop.get_learning_status()

    print("\nLearning Status:")
    print(f"  - Active: {status['active']}")
    print(f"  - Feedback Collected: {status['feedback_collected']}")
    print(f"  - Insights Generated: {status['insights_generated']}")
    print(f"  - Optimizations Pending: {status['optimizations_pending']}")

    # Stop learning loop
    await learning_loop.stop_learning()
    learning_task.cancel()

    return True


async def test_agent_collaboration():
    """Test direct agent collaboration"""
    print("\n" + "="*50)
    print("TEST: Agent Collaboration")
    print("="*50)

    collab_test = AgentCollaborationTest()

    # Test agent communication
    comm_result = await collab_test.test_agent_communication()
    print(f"Agent Communication: {'✓' if comm_result['passed'] else '✗'}")

    # Test advisor consultation
    advisor_result = await collab_test.test_advisor_consultation()
    print(f"Advisor Consultation: {'✓' if advisor_result['passed'] else '✗'}")

    # Test parallel processing
    parallel_result = await collab_test.test_parallel_processing()
    print(f"Parallel Processing: {'✓' if parallel_result['passed'] else '✗'}")

    return all([
        comm_result['passed'],
        advisor_result['passed'],
        parallel_result['passed']
    ])


async def test_performance():
    """Test system performance"""
    print("\n" + "="*50)
    print("TEST: Performance Testing")
    print("="*50)

    perf_test = PerformanceTest()

    # Test throughput
    print("Testing throughput with 20 requests...")
    throughput_result = await perf_test.test_throughput(20)

    print(f"\nThroughput Results:")
    print(f"  - Requests/sec: {throughput_result['metrics']['requests_per_second']:.2f}")
    print(f"  - Success Rate: {throughput_result['metrics']['success_rate']:.1%}")

    # Test memory usage
    memory_result = await perf_test.test_memory_usage()

    print(f"\nMemory Usage:")
    print(f"  - Initial: {memory_result['initial_memory_mb']:.1f} MB")
    print(f"  - Final: {memory_result['final_memory_mb']:.1f} MB")
    print(f"  - Increase: {memory_result['memory_increase_mb']:.1f} MB")

    return throughput_result['metrics']['success_rate'] > 0.8


async def run_all_scenario_tests():
    """Run all test scenarios"""
    print("\n" + "="*50)
    print("MULTI-AGENT COLLABORATION TEST SUITE")
    print("="*50)
    print("Testing Priority 5: Orchestration Workflows & Testing")

    test_results = {}

    # Run all tests
    tests = [
        ("Investment Workflow", test_investment_workflow),
        ("Sports Betting Workflow", test_sports_betting_workflow),
        ("Content Generation Workflow", test_content_generation_workflow),
        ("Parallel Execution", test_parallel_execution),
        ("Monitoring Integration", test_monitoring_integration),
        ("Learning Loop", test_learning_loop),
        ("Agent Collaboration", test_agent_collaboration),
        ("Performance", test_performance)
    ]

    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results[test_name] = result
            print(f"\n{test_name}: {'✓ PASSED' if result else '✗ FAILED'}")
        except Exception as e:
            test_results[test_name] = False
            print(f"\n{test_name}: ✗ FAILED with error: {e}")

    # Summary
    print("\n" + "="*50)
    print("TEST SUITE SUMMARY")
    print("="*50)

    passed = sum(1 for r in test_results.values() if r)
    total = len(test_results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total:.1%}")

    for test_name, result in test_results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")

    # Save results
    with open("test_results_scenarios.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": test_results,
            "passed": passed,
            "total": total,
            "success_rate": passed/total
        }, f, indent=2)

    print("\nResults saved to test_results_scenarios.json")

    return passed == total


if __name__ == "__main__":
    # Run the complete test suite
    success = asyncio.run(run_all_scenario_tests())

    if success:
        print("\n🎉 ALL TESTS PASSED! The Multi-Agent Orchestration System is fully operational!")
    else:
        print("\n⚠️ Some tests failed. Please review the results and fix any issues.")