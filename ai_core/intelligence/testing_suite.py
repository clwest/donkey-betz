"""
End-to-End Testing Suite for the Unified Intelligence Platform

Comprehensive testing of multi-agent collaboration, advisor consultations,
ML pipeline integration, and workflow orchestration.
"""

# BROKEN-BUT-UNREACHABLE — Session 1113 review (Session 1111 PR-C queue).
# Classification: import-broken module, no active runtime caller.
# Why: top-of-file `from orchestration import orchestrator` references a
# bare top-level `orchestration` package that does not exist in this
# repo (actual path is `ai_core.intelligence.orchestration`), so any
# import of this module fails with ModuleNotFoundError before any code
# can run. Also imports `from ml_pipeline.pipeline import MLPipeline`,
# which is a missing submodule — see `ml_pipeline/__init__.py` note.
# No active importer found.
# Decision pending: archive once the deeper-review queue confirms no
# revival path. Sits in the same family as `orchestration.py` and
# `monitoring_dashboard.py` — treat consistently.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
import random
import numpy as np
from dataclasses import dataclass
import logging

from orchestration import orchestrator
from core.agents.registry import agent_registry
from advisors.registry import advisor_registry
from ml_pipeline.pipeline import MLPipeline

logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Defines a test scenario"""
    name: str
    description: str
    workflow_template: str
    input_data: Dict[str, Any]
    expected_outputs: List[str]
    success_criteria: Dict[str, Any]
    timeout: int = 60


class IntegrationTestSuite:
    """Comprehensive integration testing"""

    def __init__(self):
        self.test_results = []
        self.ml_pipeline = MLPipeline()
        self.test_scenarios = self._initialize_scenarios()

    def _initialize_scenarios(self) -> List[TestScenario]:
        """Initialize test scenarios"""
        return [
            TestScenario(
                name="Investment Research Flow",
                description="Test complete investment research and decision workflow",
                workflow_template="research_and_invest",
                input_data={
                    "budget": 10000,
                    "risk_tolerance": "moderate",
                    "sectors": ["tech", "crypto", "healthcare"],
                    "timeframe": "6_months"
                },
                expected_outputs=[
                    "stock_analysis",
                    "crypto_analysis",
                    "expert_opinions",
                    "market_insights",
                    "risk_profile",
                    "trade_execution"
                ],
                success_criteria={
                    "all_steps_completed": True,
                    "risk_score_range": (0.3, 0.8),
                    "confidence_threshold": 0.7,
                    "advisor_consensus": 0.6
                }
            ),

            TestScenario(
                name="Sports Betting Analysis",
                description="Test sports betting prediction and recommendation",
                workflow_template="sports_betting_analysis",
                input_data={
                    "sport": "NBA",
                    "games": ["LAL_vs_GSW", "BOS_vs_MIA"],
                    "bankroll": 1000,
                    "betting_style": "value"
                },
                expected_outputs=[
                    "stats_analysis",
                    "odds_analysis",
                    "expert_picks",
                    "ml_predictions",
                    "betting_recommendation",
                    "optimal_stake"
                ],
                success_criteria={
                    "all_steps_completed": True,
                    "expected_value_positive": True,
                    "kelly_fraction_range": (0.01, 0.05),
                    "confidence_threshold": 0.65
                }
            ),

            TestScenario(
                name="AI Content Generation",
                description="Test content creation with iterative refinement",
                workflow_template="ai_content_generation",
                input_data={
                    "topic": "AI in Healthcare",
                    "target_audience": "professionals",
                    "content_type": "article",
                    "word_count": 2000
                },
                expected_outputs=[
                    "research_data",
                    "article_draft",
                    "visual_content",
                    "refined_content",
                    "final_content"
                ],
                success_criteria={
                    "all_steps_completed": True,
                    "quality_score_threshold": 0.9,
                    "fact_check_passed": True,
                    "seo_score_minimum": 85
                }
            )
        ]

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("Starting comprehensive integration test suite")

        results = {
            "start_time": datetime.now().isoformat(),
            "scenarios": [],
            "overall_success": True,
            "performance_metrics": {},
            "ml_insights": {}
        }

        for scenario in self.test_scenarios:
            scenario_result = await self.run_scenario(scenario)
            results["scenarios"].append(scenario_result)

            if not scenario_result["success"]:
                results["overall_success"] = False

        # Aggregate performance metrics
        results["performance_metrics"] = self._calculate_performance_metrics(results["scenarios"])

        # Get ML insights on test results
        results["ml_insights"] = await self.ml_pipeline.analyze_test_results(results)

        results["end_time"] = datetime.now().isoformat()

        return results

    async def run_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """Run a single test scenario"""
        logger.info(f"Running scenario: {scenario.name}")

        result = {
            "name": scenario.name,
            "description": scenario.description,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "errors": [],
            "performance": {},
            "validations": {}
        }

        try:
            # Create and execute workflow
            workflow_id = await orchestrator.create_workflow(
                name=f"Test: {scenario.name}",
                template=scenario.workflow_template
            )

            # Execute with timeout
            workflow_result = await asyncio.wait_for(
                orchestrator.execute_workflow(workflow_id, scenario.input_data),
                timeout=scenario.timeout
            )

            # Validate outputs
            result["validations"] = self._validate_outputs(
                workflow_result,
                scenario.expected_outputs,
                scenario.success_criteria
            )

            # Check success criteria
            result["success"] = all(result["validations"].values())

            # Extract performance metrics
            result["performance"] = workflow_result.get("performance", {})

            # Store ML insights
            result["ml_insights"] = workflow_result.get("ml_insights", {})

        except asyncio.TimeoutError:
            result["errors"].append(f"Scenario timed out after {scenario.timeout} seconds")
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Scenario {scenario.name} failed: {e}")

        result["end_time"] = datetime.now().isoformat()

        return result

    def _validate_outputs(
        self,
        workflow_result: Dict[str, Any],
        expected_outputs: List[str],
        success_criteria: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate workflow outputs against expectations"""
        validations = {}

        # Check all expected outputs exist
        results = workflow_result.get("results", {})
        for output_key in expected_outputs:
            validations[f"output_{output_key}"] = output_key in results

        # Check success criteria
        if success_criteria.get("all_steps_completed"):
            validations["all_steps"] = workflow_result.get("status") == "completed"

        if "risk_score_range" in success_criteria:
            risk_profile = results.get("risk_profile", {})
            risk_score = risk_profile.get("score", 0)
            min_risk, max_risk = success_criteria["risk_score_range"]
            validations["risk_score"] = min_risk <= risk_score <= max_risk

        if "confidence_threshold" in success_criteria:
            insights = results.get("market_insights", {})
            confidence = insights.get("confidence", 0)
            validations["confidence"] = confidence >= success_criteria["confidence_threshold"]

        if "expected_value_positive" in success_criteria:
            recommendation = results.get("betting_recommendation", {})
            ev = recommendation.get("expected_value", 0)
            validations["positive_ev"] = ev > 0

        if "quality_score_threshold" in success_criteria:
            content = results.get("final_content", {})
            quality = content.get("quality_score", 0)
            validations["quality"] = quality >= success_criteria["quality_score_threshold"]

        return validations

    def _calculate_performance_metrics(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate aggregate performance metrics"""
        metrics = {
            "total_scenarios": len(scenarios),
            "successful_scenarios": sum(1 for s in scenarios if s["success"]),
            "failed_scenarios": sum(1 for s in scenarios if not s["success"]),
            "average_duration": 0,
            "step_performance": {}
        }

        durations = []
        for scenario in scenarios:
            if "start_time" in scenario and "end_time" in scenario:
                start = datetime.fromisoformat(scenario["start_time"])
                end = datetime.fromisoformat(scenario["end_time"])
                durations.append((end - start).total_seconds())

        if durations:
            metrics["average_duration"] = np.mean(durations)
            metrics["min_duration"] = np.min(durations)
            metrics["max_duration"] = np.max(durations)

        return metrics


class AgentCollaborationTest:
    """Test multi-agent collaboration scenarios"""

    async def test_agent_communication(self) -> Dict[str, Any]:
        """Test agent-to-agent communication"""
        results = {
            "test": "agent_communication",
            "passed": False,
            "details": {}
        }

        try:
            # Test simple agent chain
            agent1 = agent_registry.get_agent("researcher")
            agent2 = agent_registry.get_agent("content_writer")

            # Agent 1 generates data
            research_data = await agent1.process({"topic": "AI trends"})

            # Agent 2 uses Agent 1's output
            content = await agent2.process({"research": research_data})

            results["passed"] = content is not None
            results["details"] = {
                "research_generated": bool(research_data),
                "content_created": bool(content)
            }

        except Exception as e:
            results["error"] = str(e)

        return results

    async def test_advisor_consultation(self) -> Dict[str, Any]:
        """Test agent-advisor consultation"""
        results = {
            "test": "advisor_consultation",
            "passed": False,
            "details": {}
        }

        try:
            agent = agent_registry.get_agent("investment_analyst")
            advisor = advisor_registry.get_advisor("warren_buffett")

            # Agent requests advisor input
            market_data = {"sector": "tech", "budget": 10000}
            agent_analysis = await agent.process(market_data)

            # Get advisor perspective
            advisor_advice = await advisor.provide_advice({
                "analysis": agent_analysis,
                "context": market_data
            })

            results["passed"] = advisor_advice is not None
            results["details"] = {
                "agent_analysis": bool(agent_analysis),
                "advisor_responded": bool(advisor_advice),
                "advice_quality": advisor_advice.get("confidence", 0) if advisor_advice else 0
            }

        except Exception as e:
            results["error"] = str(e)

        return results

    async def test_parallel_processing(self) -> Dict[str, Any]:
        """Test parallel agent execution"""
        results = {
            "test": "parallel_processing",
            "passed": False,
            "details": {}
        }

        try:
            agents = [
                agent_registry.get_agent("stock_analyst"),
                agent_registry.get_agent("crypto_analyst"),
                agent_registry.get_agent("forex_trader")
            ]

            # Run agents in parallel
            tasks = [
                agent.process({"market": "analyze"})
                for agent in agents if agent
            ]

            start_time = datetime.now()
            parallel_results = await asyncio.gather(*tasks)
            duration = (datetime.now() - start_time).total_seconds()

            results["passed"] = all(r is not None for r in parallel_results)
            results["details"] = {
                "agents_executed": len(parallel_results),
                "execution_time": duration,
                "all_completed": all(r is not None for r in parallel_results)
            }

        except Exception as e:
            results["error"] = str(e)

        return results


class PerformanceTest:
    """Performance and load testing"""

    async def test_throughput(self, num_requests: int = 100) -> Dict[str, Any]:
        """Test system throughput"""
        results = {
            "test": "throughput",
            "num_requests": num_requests,
            "metrics": {}
        }

        tasks = []
        for i in range(num_requests):
            # Randomly select workflow type
            template = random.choice(["research_and_invest", "sports_betting_analysis"])
            tasks.append(self._single_request(template, i))

        start_time = datetime.now()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = (datetime.now() - start_time).total_seconds()

        successful = sum(1 for r in responses if not isinstance(r, Exception))
        failed = num_requests - successful

        results["metrics"] = {
            "total_duration": total_duration,
            "requests_per_second": num_requests / total_duration,
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": successful / num_requests
        }

        return results

    async def _single_request(self, template: str, request_id: int) -> Dict[str, Any]:
        """Execute a single test request"""
        try:
            workflow_id = await orchestrator.create_workflow(
                name=f"Load test {request_id}",
                template=template
            )

            result = await orchestrator.execute_workflow(
                workflow_id,
                {"test_id": request_id}
            )

            return {"success": True, "workflow_id": workflow_id}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage under load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run workflows
        for i in range(10):
            workflow_id = await orchestrator.create_workflow(
                name=f"Memory test {i}",
                template="research_and_invest"
            )
            await orchestrator.execute_workflow(workflow_id)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        return {
            "test": "memory_usage",
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "acceptable": memory_increase < 100  # Less than 100MB increase
        }


class MLPipelineTest:
    """Test ML pipeline integration"""

    async def test_pattern_recognition(self) -> Dict[str, Any]:
        """Test pattern recognition in workflows"""
        ml_pipeline = MLPipeline()

        # Generate test patterns
        test_data = {
            "workflow_patterns": [
                {"type": "investment", "success": True, "confidence": 0.8},
                {"type": "investment", "success": True, "confidence": 0.85},
                {"type": "investment", "success": False, "confidence": 0.3},
                {"type": "betting", "success": True, "confidence": 0.7},
                {"type": "betting", "success": True, "confidence": 0.75}
            ]
        }

        patterns = await ml_pipeline.identify_patterns(test_data)

        return {
            "test": "pattern_recognition",
            "patterns_found": len(patterns),
            "insights": patterns,
            "passed": len(patterns) > 0
        }

    async def test_performance_prediction(self) -> Dict[str, Any]:
        """Test ML performance predictions"""
        ml_pipeline = MLPipeline()

        historical_data = {
            "agent_performance": [
                {"agent_id": "stock_analyst", "accuracy": 0.75, "speed": 2.3},
                {"agent_id": "stock_analyst", "accuracy": 0.78, "speed": 2.1},
                {"agent_id": "crypto_analyst", "accuracy": 0.82, "speed": 1.8}
            ]
        }

        predictions = await ml_pipeline.predict_performance(
            agent_id="stock_analyst",
            historical_data=historical_data
        )

        return {
            "test": "performance_prediction",
            "predictions": predictions,
            "confidence": predictions.get("confidence", 0),
            "passed": predictions.get("confidence", 0) > 0.6
        }


# Test runner
async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*50)
    print("UNIFIED INTELLIGENCE PLATFORM - TEST SUITE")
    print("="*50)

    # Integration tests
    print("\n[1/4] Running Integration Tests...")
    integration_suite = IntegrationTestSuite()
    integration_results = await integration_suite.run_all_tests()
    print(f"✓ Integration Tests: {integration_results['overall_success']}")

    # Collaboration tests
    print("\n[2/4] Running Collaboration Tests...")
    collab_test = AgentCollaborationTest()
    collab_results = {
        "communication": await collab_test.test_agent_communication(),
        "consultation": await collab_test.test_advisor_consultation(),
        "parallel": await collab_test.test_parallel_processing()
    }
    print(f"✓ Collaboration Tests: {all(r['passed'] for r in collab_results.values())}")

    # Performance tests
    print("\n[3/4] Running Performance Tests...")
    perf_test = PerformanceTest()
    perf_results = {
        "throughput": await perf_test.test_throughput(50),
        "memory": await perf_test.test_memory_usage()
    }
    print(f"✓ Performance Tests: Throughput={perf_results['throughput']['metrics']['requests_per_second']:.2f} req/s")

    # ML Pipeline tests
    print("\n[4/4] Running ML Pipeline Tests...")
    ml_test = MLPipelineTest()
    ml_results = {
        "patterns": await ml_test.test_pattern_recognition(),
        "predictions": await ml_test.test_performance_prediction()
    }
    print(f"✓ ML Tests: {all(r['passed'] for r in ml_results.values())}")

    # Summary
    print("\n" + "="*50)
    print("TEST SUITE COMPLETED")
    print("="*50)

    return {
        "integration": integration_results,
        "collaboration": collab_results,
        "performance": perf_results,
        "ml_pipeline": ml_results,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Run the test suite
    results = asyncio.run(run_all_tests())

    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\nTest results saved to test_results.json")