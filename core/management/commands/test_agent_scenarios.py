"""
Test Agent Scenarios Management Command
========================================

Session 334: Run business research agents against test scenarios and
score/validate the results.

Usage:
    # List available test scenarios
    python manage.py test_agent_scenarios --list

    # Run all tests
    python manage.py test_agent_scenarios

    # Run specific scenario
    python manage.py test_agent_scenarios --scenario ai-podcast-tools

    # Run specific agent only
    python manage.py test_agent_scenarios --agent competitor

    # Run with verbose output
    python manage.py test_agent_scenarios --verbose

    # Generate report
    python manage.py test_agent_scenarios --report
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from core.testing import (
    TEST_SCENARIOS,
    TestScenario,
    get_scenario,
)
from core.models_partnership import PartnershipProject
from core.models_unified_system import BusinessResearchResult

User = get_user_model()


@dataclass
class TestResult:
    """Result of a single agent test run."""
    scenario_id: str
    scenario_name: str
    agent_name: str
    success: bool
    execution_time_ms: int
    data_points_found: int
    competitors_found: List[str]
    competitors_expected: List[str]
    competitors_matched: int
    pain_points_found: List[str]
    score: float  # 0-100
    errors: List[str] = field(default_factory=list)
    raw_result: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuiteResult:
    """Result of running all tests."""
    total_tests: int
    passed: int
    failed: int
    avg_score: float
    avg_execution_time_ms: float
    results: List[TestResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class Command(BaseCommand):
    help = 'Run business research agents against test scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available test scenarios',
        )
        parser.add_argument(
            '--scenario',
            type=str,
            help='Run a specific scenario by ID',
        )
        parser.add_argument(
            '--agent',
            type=str,
            choices=['competitor', 'customer', 'both'],
            default='both',
            help='Which agent to test (default: both)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each test',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate a detailed JSON report',
        )
        parser.add_argument(
            '--report-file',
            type=str,
            default='agent_test_report.json',
            help='Report file path (default: agent_test_report.json)',
        )
        parser.add_argument(
            '--user',
            type=str,
            default='test_scenarios',
            help='Username for test execution (default: test_scenarios)',
        )
        parser.add_argument(
            '--max-scenarios',
            type=int,
            default=0,
            help='Maximum scenarios to test (0 = all)',
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_scenarios()
            return

        # Get test user
        try:
            user = User.objects.get(username=options['user'])
        except User.DoesNotExist:
            raise CommandError(
                f"User '{options['user']}' not found. "
                "Run 'python manage.py seed_test_scenarios' first."
            )

        # Determine scenarios to test
        scenarios = self._get_scenarios(options)

        if not scenarios:
            self.stdout.write(self.style.WARNING("No scenarios to test."))
            return

        # Run tests
        suite_result = self._run_tests(user, scenarios, options)

        # Output results
        self._output_results(suite_result, options)

        # Generate report if requested
        if options['report']:
            self._generate_report(suite_result, options['report_file'])

    def _list_scenarios(self):
        """List test scenarios with their test status."""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📋 TEST SCENARIOS"))
        self.stdout.write("=" * 80)

        # Check which scenarios have been seeded
        seeded_ids = set(
            PartnershipProject.objects.filter(
                metadata__has_key='test_scenario_id'
            ).values_list('metadata__test_scenario_id', flat=True)
        )

        # Check which have research results
        researched_ids = set()
        for project in PartnershipProject.objects.filter(metadata__has_key='test_scenario_id'):
            scenario_id = project.metadata.get('test_scenario_id')
            if BusinessResearchResult.objects.filter(project=project).exists():
                researched_ids.add(scenario_id)

        for s in TEST_SCENARIOS:
            status = []
            if s.id in seeded_ids:
                status.append("🌱 Seeded")
            else:
                status.append("⚪ Not seeded")

            if s.id in researched_ids:
                status.append("📊 Has research")

            status_str = " | ".join(status)

            self.stdout.write(f"\n{s.id}")
            self.stdout.write(f"  Name: {s.name}")
            self.stdout.write(f"  Company: {s.company_name}")
            self.stdout.write(f"  Industry: {s.industry.value} | Complexity: {s.complexity.value}")
            self.stdout.write(f"  Status: {status_str}")

        self.stdout.write("\n" + "=" * 80)

    def _get_scenarios(self, options) -> List[TestScenario]:
        """Get scenarios to test."""
        if options['scenario']:
            scenario = get_scenario(options['scenario'])
            if not scenario:
                raise CommandError(f"Scenario '{options['scenario']}' not found.")
            return [scenario]

        scenarios = TEST_SCENARIOS.copy()

        if options['max_scenarios'] > 0:
            scenarios = scenarios[:options['max_scenarios']]

        return scenarios

    def _run_tests(
        self,
        user: User,
        scenarios: List[TestScenario],
        options: dict
    ) -> TestSuiteResult:
        """Run tests against all scenarios."""
        suite_result = TestSuiteResult(
            total_tests=0,
            passed=0,
            failed=0,
            avg_score=0.0,
            avg_execution_time_ms=0.0,
        )

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("🧪 RUNNING AGENT TESTS"))
        self.stdout.write("=" * 80)

        agents_to_test = []
        if options['agent'] in ['competitor', 'both']:
            agents_to_test.append('competitor')
        if options['agent'] in ['customer', 'both']:
            agents_to_test.append('customer')

        total_scores = []
        total_times = []

        for scenario in scenarios:
            self.stdout.write(f"\n📁 Scenario: {scenario.name}")
            self.stdout.write(f"   Company: {scenario.company_name}")

            # Get or find the project for this scenario
            project = PartnershipProject.objects.filter(
                metadata__test_scenario_id=scenario.id
            ).first()

            if not project:
                self.stdout.write(self.style.WARNING(
                    f"   ⚠️ Project not seeded. Run 'seed_test_scenarios' first."
                ))
                continue

            for agent_type in agents_to_test:
                suite_result.total_tests += 1

                result = self._run_single_test(
                    user=user,
                    scenario=scenario,
                    project=project,
                    agent_type=agent_type,
                    verbose=options['verbose'],
                )

                suite_result.results.append(result)

                if result.success and result.score >= 50:
                    suite_result.passed += 1
                    status = self.style.SUCCESS("✅ PASS")
                else:
                    suite_result.failed += 1
                    status = self.style.ERROR("❌ FAIL")

                total_scores.append(result.score)
                total_times.append(result.execution_time_ms)

                self.stdout.write(
                    f"   {agent_type.capitalize()} Agent: {status} "
                    f"(Score: {result.score:.1f}%, Time: {result.execution_time_ms}ms)"
                )

                if options['verbose'] and result.errors:
                    for error in result.errors:
                        self.stdout.write(f"      ⚠️ {error}")

        suite_result.avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
        suite_result.avg_execution_time_ms = sum(total_times) / len(total_times) if total_times else 0
        suite_result.completed_at = datetime.now()

        return suite_result

    def _run_single_test(
        self,
        user: User,
        scenario: TestScenario,
        project: PartnershipProject,
        agent_type: str,
        verbose: bool,
    ) -> TestResult:
        """Run a single agent test."""
        result = TestResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            agent_name=f"{agent_type}_analysis",
            success=False,
            execution_time_ms=0,
            data_points_found=0,
            competitors_found=[],
            competitors_expected=scenario.expected_competitors,
            competitors_matched=0,
            pain_points_found=[],
            score=0.0,
        )

        try:
            start_time = time.time()

            # Get the appropriate query
            if agent_type == 'competitor':
                query = scenario.competitor_analysis_query
                agent_result = self._run_competitor_agent(user, project, query)
            else:  # customer
                query = scenario.customer_research_query
                agent_result = self._run_customer_agent(user, project, query)

            execution_time = int((time.time() - start_time) * 1000)
            result.execution_time_ms = execution_time

            if agent_result.get('success'):
                result.success = True
                result.raw_result = agent_result

                # Extract and score results
                data = agent_result.get('data', {})
                analysis = data.get('analysis', {})

                # Count data points
                result.data_points_found = analysis.get('data_points_analyzed', 0)

                # For competitor analysis, try to extract competitor names
                if agent_type == 'competitor':
                    result.competitors_found = self._extract_competitors(analysis)
                    result.competitors_matched = len(
                        set(result.competitors_found) &
                        set(scenario.expected_competitors)
                    )

                # Calculate score
                result.score = self._calculate_score(result, scenario, agent_type)

            else:
                result.errors.append(agent_result.get('error', 'Unknown error'))

        except Exception as e:
            result.errors.append(str(e))

        return result

    def _run_competitor_agent(
        self,
        user: User,
        project: PartnershipProject,
        query: str
    ) -> Dict[str, Any]:
        """Run the CompetitorAnalysisAgent."""
        try:
            from core.agents.business.competitor_analysis_agent import CompetitorAnalysisAgent

            agent = CompetitorAnalysisAgent(user=user)

            # Execute the agent
            result = agent.execute(
                task=query,
                context={'project_id': str(project.id)},
                scifi_context={},
                spider_context={},
            )

            return {
                'success': result.success,
                'data': result.data,
                'error': result.error,
                'execution_time_ms': result.execution_time_ms,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def _run_customer_agent(
        self,
        user: User,
        project: PartnershipProject,
        query: str
    ) -> Dict[str, Any]:
        """Run the CustomerResearchAgent."""
        try:
            from core.agents.business.customer_research_agent import CustomerResearchAgent

            agent = CustomerResearchAgent(user=user)

            # Execute the agent
            result = agent.execute(
                task=query,
                context={'project_id': str(project.id)},
                scifi_context={},
                spider_context={},
            )

            return {
                'success': result.success,
                'data': result.data,
                'error': result.error,
                'execution_time_ms': result.execution_time_ms,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }

    def _extract_competitors(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract competitor names from analysis result."""
        competitors = []

        # Try to get from structured data
        if isinstance(analysis, dict):
            # Check raw_data for competitor mentions
            raw_data = analysis.get('raw_data', [])
            for item in raw_data:
                if isinstance(item, dict):
                    title = item.get('title', '').lower()
                    # Simple extraction - look for known patterns
                    for competitor in ['descript', 'jasper', 'copy.ai', 'freshbooks']:
                        if competitor in title:
                            competitors.append(competitor.title())

        return list(set(competitors))

    def _calculate_score(
        self,
        result: TestResult,
        scenario: TestScenario,
        agent_type: str
    ) -> float:
        """Calculate a score for the test result."""
        score = 0.0

        # Base score for successful execution
        if result.success:
            score += 30.0

        # Score for data points found
        if result.data_points_found >= 10:
            score += 25.0
        elif result.data_points_found >= 5:
            score += 15.0
        elif result.data_points_found > 0:
            score += 5.0

        # Score for execution time (fast is good)
        if result.execution_time_ms < 5000:
            score += 15.0
        elif result.execution_time_ms < 15000:
            score += 10.0
        elif result.execution_time_ms < 30000:
            score += 5.0

        # Score for competitor matching (competitor analysis only)
        if agent_type == 'competitor':
            expected_count = len(scenario.expected_competitors)
            if expected_count > 0:
                match_ratio = result.competitors_matched / expected_count
                score += match_ratio * 30.0

        # Customer research gets points for finding any data
        if agent_type == 'customer':
            if result.data_points_found >= 20:
                score += 30.0
            elif result.data_points_found >= 10:
                score += 20.0
            elif result.data_points_found > 0:
                score += 10.0

        return min(score, 100.0)

    def _output_results(self, suite_result: TestSuiteResult, options: dict):
        """Output the test results summary."""
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 TEST RESULTS SUMMARY"))
        self.stdout.write("=" * 80)

        self.stdout.write(f"\nTotal Tests: {suite_result.total_tests}")
        self.stdout.write(
            f"Passed: {self.style.SUCCESS(str(suite_result.passed))} | "
            f"Failed: {self.style.ERROR(str(suite_result.failed))}"
        )
        self.stdout.write(f"Average Score: {suite_result.avg_score:.1f}%")
        self.stdout.write(f"Average Execution Time: {suite_result.avg_execution_time_ms:.0f}ms")

        # Pass rate
        if suite_result.total_tests > 0:
            pass_rate = (suite_result.passed / suite_result.total_tests) * 100
            if pass_rate >= 80:
                rate_style = self.style.SUCCESS
            elif pass_rate >= 50:
                rate_style = self.style.WARNING
            else:
                rate_style = self.style.ERROR

            self.stdout.write(f"Pass Rate: {rate_style(f'{pass_rate:.1f}%')}")

        self.stdout.write("")

    def _generate_report(self, suite_result: TestSuiteResult, report_file: str):
        """Generate a detailed JSON report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_tests': suite_result.total_tests,
                'passed': suite_result.passed,
                'failed': suite_result.failed,
                'pass_rate': (suite_result.passed / suite_result.total_tests * 100)
                             if suite_result.total_tests > 0 else 0,
                'avg_score': suite_result.avg_score,
                'avg_execution_time_ms': suite_result.avg_execution_time_ms,
            },
            'results': [
                {
                    'scenario_id': r.scenario_id,
                    'scenario_name': r.scenario_name,
                    'agent_name': r.agent_name,
                    'success': r.success,
                    'execution_time_ms': r.execution_time_ms,
                    'data_points_found': r.data_points_found,
                    'score': r.score,
                    'errors': r.errors,
                    'competitors_found': r.competitors_found,
                    'competitors_expected': r.competitors_expected,
                    'competitors_matched': r.competitors_matched,
                }
                for r in suite_result.results
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"📄 Report saved to: {report_file}"))
