"""
Testing Infrastructure for Unified Donkey Betz Platform
========================================================

Session 334: Test scenarios and utilities for pushing business research
agents to their limits with realistic company scenarios.
"""

from .test_scenarios import (
    TEST_SCENARIOS,
    TestScenario,
    Industry,
    Complexity,
    CompanySize,
    get_scenario,
    get_scenarios_by_industry,
    get_scenarios_by_complexity,
    get_scenarios_by_tag,
    get_all_industries,
    get_scenario_summary,
)

from .validators import (
    ValidationResult,
    CompetitorMatch,
    AgentOutputValidator,
    ResearchQualityScorer,
    quick_validate,
)

__all__ = [
    # Test Scenarios
    "TEST_SCENARIOS",
    "TestScenario",
    "Industry",
    "Complexity",
    "CompanySize",
    "get_scenario",
    "get_scenarios_by_industry",
    "get_scenarios_by_complexity",
    "get_scenarios_by_tag",
    "get_all_industries",
    "get_scenario_summary",
    # Validators
    "ValidationResult",
    "CompetitorMatch",
    "AgentOutputValidator",
    "ResearchQualityScorer",
    "quick_validate",
]
