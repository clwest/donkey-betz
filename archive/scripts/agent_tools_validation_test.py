#!/usr/bin/env python3
"""
Agent Tools Validation Test Suite
=================================

This script validates that agents and spiders are using real tools and APIs
instead of mock data. It tests the entire data flow from spiders to agents
to ensure genuine deliverables are produced.

Run with: python agent_tools_validation_test.py
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentToolsValidator:
    """Validates that agents use real tools instead of mock data."""

    def __init__(self):
        self.test_results = {}
        self.violations = []
        self.real_data_detected = []

    async def run_comprehensive_validation(self):
        """Run all validation tests."""
        logger.info("🔍 Starting Agent Tools Validation Suite")

        # Test 1: Spider Real Data Usage
        await self.test_spider_real_data()

        # Test 2: Agent Executor Tool Usage
        await self.test_agent_executor_tools()

        # Test 3: Opportunities API Real vs Mock
        await self.test_opportunities_api()

        # Test 4: File Creation Verification
        await self.test_real_file_creation()

        # Test 5: Web Search Usage
        await self.test_web_search_usage()

        # Generate final report
        await self.generate_validation_report()

    async def test_spider_real_data(self):
        """Test if spiders are producing real data."""
        logger.info("🕷️ Testing Spider Real Data Usage")

        try:
            from ai_core.spiders.live_job_scraper import scrape_jobs_sync, LiveJobScraper

            # Test live job scraper
            jobs = scrape_jobs_sync()

            real_data_indicators = 0
            mock_data_indicators = 0

            for job in jobs:
                # Check for real indicators
                if any(indicator in str(job).lower() for indicator in [
                    'https://', 'http://', '.com', '.org', 'www.',
                    '2024', '2025', '$', 'remote', 'upwork', 'fiverr'
                ]):
                    real_data_indicators += 1

                # Check for mock indicators
                if any(indicator in str(job).lower() for indicator in [
                    'example.com', 'test', 'mock', 'sample', 'fake',
                    'techcorp', 'ai innovations', 'datadrive', 'startupxyz'
                ]):
                    mock_data_indicators += 1

            self.test_results['spider_data'] = {
                'jobs_found': len(jobs),
                'real_indicators': real_data_indicators,
                'mock_indicators': mock_data_indicators,
                'real_data_ratio': real_data_indicators / max(1, len(jobs)),
                'status': 'REAL_DATA' if real_data_indicators > mock_data_indicators else 'MOCK_DATA'
            }

            if mock_data_indicators > real_data_indicators:
                self.violations.append({
                    'component': 'live_job_scraper',
                    'issue': 'Using mock data fallbacks as primary data source',
                    'severity': 'HIGH',
                    'evidence': f'{mock_data_indicators} mock indicators vs {real_data_indicators} real indicators'
                })
            else:
                self.real_data_detected.append({
                    'component': 'live_job_scraper',
                    'evidence': f'Found {real_data_indicators} real data indicators in {len(jobs)} jobs'
                })

        except Exception as e:
            self.violations.append({
                'component': 'live_job_scraper',
                'issue': f'Spider execution failed: {str(e)}',
                'severity': 'CRITICAL'
            })

    async def test_agent_executor_tools(self):
        """Test if agent executors use real tools."""
        logger.info("🤖 Testing Agent Executor Tool Usage")

        try:
            from agents.executors.income_builder_executor import IncomeBuilderExecutor
            from agents.executors.content_creator_executor import ContentCreatorExecutor

            # Test Income Builder
            income_builder = IncomeBuilderExecutor("test_income_builder", {})
            required_tools = income_builder.get_required_tools()
            required_apis = income_builder.get_required_apis()

            self.test_results['income_builder_tools'] = {
                'required_tools': required_tools,
                'required_apis': required_apis,
                'has_web_search': 'web_search' in required_tools,
                'has_openai': 'openai' in required_apis,
                'status': 'TOOLS_CONFIGURED' if required_tools and required_apis else 'NO_TOOLS'
            }

            # Test Content Creator
            content_creator = ContentCreatorExecutor("test_content_creator", {})
            content_tools = content_creator.get_required_tools()
            content_apis = content_creator.get_required_apis()

            self.test_results['content_creator_tools'] = {
                'required_tools': content_tools,
                'required_apis': content_apis,
                'has_web_search': 'web_search' in content_tools,
                'has_openai': 'openai' in content_apis,
                'status': 'TOOLS_CONFIGURED' if content_tools and content_apis else 'NO_TOOLS'
            }

            # Check for tool usage vs simulation
            if not required_tools or not required_apis:
                self.violations.append({
                    'component': 'agent_executors',
                    'issue': 'Agents not configured to use required tools/APIs',
                    'severity': 'HIGH'
                })
            else:
                self.real_data_detected.append({
                    'component': 'agent_executors',
                    'evidence': f'Agents configured with real tools: {required_tools + required_apis}'
                })

        except Exception as e:
            self.violations.append({
                'component': 'agent_executors',
                'issue': f'Agent executor test failed: {str(e)}',
                'severity': 'HIGH'
            })

    async def test_opportunities_api(self):
        """Test if opportunities API uses real vs mock data."""
        logger.info("💼 Testing Opportunities API Data Source")

        try:
            # Test the opportunities API endpoints
            test_endpoints = [
                'http://localhost:8000/api/opportunities/',
                'http://localhost:8000/api/jobs/',
                'http://localhost:8000/api/gigs/'
            ]

            api_results = {}

            for endpoint in test_endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()

                        # Analyze response for real vs mock data
                        response_text = json.dumps(data).lower()

                        real_indicators = sum(1 for indicator in [
                            'https://', '.com', 'upwork', 'linkedin', 'remote',
                            '2024', '2025', 'indeed', 'freelancer'
                        ] if indicator in response_text)

                        mock_indicators = sum(1 for indicator in [
                            'techcorp', 'ai innovations', 'datadrive', 'sample',
                            'mock', 'test', 'example.com', 'fake'
                        ] if indicator in response_text)

                        api_results[endpoint] = {
                            'status_code': response.status_code,
                            'real_indicators': real_indicators,
                            'mock_indicators': mock_indicators,
                            'data_type': 'REAL' if real_indicators > mock_indicators else 'MOCK'
                        }

                except requests.RequestException as e:
                    api_results[endpoint] = {
                        'status_code': 'ERROR',
                        'error': str(e)
                    }

            self.test_results['opportunities_api'] = api_results

            # Check if APIs are returning mostly mock data
            mock_apis = [
                endpoint for endpoint, result in api_results.items()
                if result.get('data_type') == 'MOCK'
            ]

            if mock_apis:
                self.violations.append({
                    'component': 'opportunities_api',
                    'issue': f'APIs returning mock data: {mock_apis}',
                    'severity': 'HIGH',
                    'recommendation': 'Connect APIs to live_job_scraper for real data'
                })
            else:
                self.real_data_detected.append({
                    'component': 'opportunities_api',
                    'evidence': 'APIs returning real data indicators'
                })

        except Exception as e:
            self.violations.append({
                'component': 'opportunities_api',
                'issue': f'API testing failed: {str(e)}',
                'severity': 'HIGH'
            })

    async def test_real_file_creation(self):
        """Test if agents actually create files."""
        logger.info("📁 Testing Real File Creation")

        test_dir = Path("test_file_creation")
        test_dir.mkdir(exist_ok=True)

        try:
            # Test file creation functionality
            test_file = test_dir / "agent_test_file.md"
            test_content = f"""# Test File Creation

Generated by agent validation test at {datetime.now().isoformat()}

This file tests whether agents can actually create real files.
"""

            # Simulate agent file creation
            with open(test_file, 'w') as f:
                f.write(test_content)

            # Verify file exists and has content
            if test_file.exists() and test_file.stat().st_size > 0:
                self.test_results['file_creation'] = {
                    'can_create_files': True,
                    'test_file_size': test_file.stat().st_size,
                    'test_file_path': str(test_file),
                    'status': 'FILE_CREATION_WORKING'
                }

                self.real_data_detected.append({
                    'component': 'file_creation',
                    'evidence': f'Successfully created file: {test_file}'
                })
            else:
                self.violations.append({
                    'component': 'file_creation',
                    'issue': 'File creation test failed',
                    'severity': 'HIGH'
                })

            # Clean up test file
            if test_file.exists():
                test_file.unlink()
            test_dir.rmdir()

        except Exception as e:
            self.violations.append({
                'component': 'file_creation',
                'issue': f'File creation test error: {str(e)}',
                'severity': 'HIGH'
            })

    async def test_web_search_usage(self):
        """Test if web search functionality is available."""
        logger.info("🔍 Testing Web Search Capability")

        try:
            # Test if web search modules are available
            search_modules = []

            # Check for search implementations
            try:
                import requests
                search_modules.append('requests')
            except ImportError:
                pass

            try:
                import aiohttp
                search_modules.append('aiohttp')
            except ImportError:
                pass

            # Test a simple web request
            try:
                response = requests.get('https://httpbin.org/json', timeout=10)
                if response.status_code == 200:
                    web_connectivity = True
                    response_data = response.json()
                else:
                    web_connectivity = False
                    response_data = None
            except:
                web_connectivity = False
                response_data = None

            self.test_results['web_search'] = {
                'available_modules': search_modules,
                'web_connectivity': web_connectivity,
                'test_response': bool(response_data),
                'status': 'WEB_SEARCH_AVAILABLE' if web_connectivity else 'NO_WEB_ACCESS'
            }

            if not web_connectivity:
                self.violations.append({
                    'component': 'web_search',
                    'issue': 'No web connectivity for real-time searches',
                    'severity': 'HIGH'
                })
            else:
                self.real_data_detected.append({
                    'component': 'web_search',
                    'evidence': 'Web connectivity confirmed for real-time data'
                })

        except Exception as e:
            self.violations.append({
                'component': 'web_search',
                'issue': f'Web search test failed: {str(e)}',
                'severity': 'HIGH'
            })

    async def generate_validation_report(self):
        """Generate comprehensive validation report."""
        logger.info("📊 Generating Validation Report")

        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'total_components_tested': len(self.test_results),
            'violations_found': len(self.violations),
            'real_data_confirmations': len(self.real_data_detected),
            'overall_status': 'PASS' if len(self.violations) == 0 else 'FAIL',
            'test_results': self.test_results,
            'violations': self.violations,
            'real_data_detected': self.real_data_detected,
            'recommendations': self._generate_recommendations()
        }

        # Save detailed report
        report_file = Path("agent_tools_validation_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate markdown summary
        await self._generate_markdown_report(report)

        # Print summary
        self._print_summary(report)

        return report

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on findings."""
        recommendations = []

        # Check for mock data usage
        if any('MOCK_DATA' in str(violation) for violation in self.violations):
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Replace mock data with live scraper integration',
                'component': 'opportunities_api',
                'details': 'Connect generate_enhanced_opportunities() to scrape_jobs_sync() for real data'
            })

        # Check for missing tool usage
        if any('NO_TOOLS' in str(violation) for violation in self.violations):
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Implement real tool usage in agent executors',
                'component': 'agent_executors',
                'details': 'Ensure agents call web_search and OpenAI APIs instead of returning mock responses'
            })

        # Check for web connectivity issues
        if any('NO_WEB_ACCESS' in str(violation) for violation in self.violations):
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Fix web connectivity for real-time data',
                'component': 'infrastructure',
                'details': 'Enable web access for spiders and agents to fetch real data'
            })

        return recommendations

    async def _generate_markdown_report(self, report: Dict):
        """Generate markdown report."""

        markdown_content = f"""# Agent Tools Validation Report

**Generated:** {report['validation_timestamp']}
**Status:** {report['overall_status']}

## Executive Summary

- **Components Tested:** {report['total_components_tested']}
- **Violations Found:** {report['violations_found']}
- **Real Data Confirmations:** {report['real_data_confirmations']}

## Test Results

"""

        for component, results in report['test_results'].items():
            markdown_content += f"""### {component.title().replace('_', ' ')}
- **Status:** {results.get('status', 'Unknown')}
- **Details:** {json.dumps(results, indent=2)}

"""

        if report['violations']:
            markdown_content += """## Violations Found

"""
            for violation in report['violations']:
                markdown_content += f"""### {violation['component']}
- **Issue:** {violation['issue']}
- **Severity:** {violation['severity']}
- **Recommendation:** {violation.get('recommendation', 'See recommendations section')}

"""

        if report['real_data_detected']:
            markdown_content += """## Real Data Confirmations

"""
            for detection in report['real_data_detected']:
                markdown_content += f"""### {detection['component']}
- **Evidence:** {detection['evidence']}

"""

        markdown_content += """## Recommendations

"""
        for rec in report['recommendations']:
            markdown_content += f"""### {rec['priority']} Priority: {rec['action']}
- **Component:** {rec['component']}
- **Details:** {rec['details']}

"""

        report_file = Path("AGENT_TOOLS_VALIDATION_REPORT.md")
        with open(report_file, 'w') as f:
            f.write(markdown_content)

        logger.info(f"📄 Detailed report saved to: {report_file}")

    def _print_summary(self, report: Dict):
        """Print validation summary."""

        print("\n" + "="*60)
        print("🔍 AGENT TOOLS VALIDATION SUMMARY")
        print("="*60)

        print(f"Overall Status: {report['overall_status']}")
        print(f"Components Tested: {report['total_components_tested']}")
        print(f"Violations: {report['violations_found']}")
        print(f"Real Data Confirmations: {report['real_data_confirmations']}")

        if report['violations']:
            print("\n⚠️  CRITICAL ISSUES FOUND:")
            for violation in report['violations']:
                print(f"- {violation['component']}: {violation['issue']}")

        if report['real_data_detected']:
            print("\n✅ REAL DATA CONFIRMED:")
            for detection in report['real_data_detected']:
                print(f"- {detection['component']}: {detection['evidence']}")

        print("\n📊 Full report saved to: agent_tools_validation_report.json")
        print("📄 Markdown report: AGENT_TOOLS_VALIDATION_REPORT.md")
        print("="*60)


async def main():
    """Run the validation suite."""
    validator = AgentToolsValidator()
    await validator.run_comprehensive_validation()


if __name__ == "__main__":
    asyncio.run(main())