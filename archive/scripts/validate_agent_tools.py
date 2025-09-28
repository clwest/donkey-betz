#!/usr/bin/env python3
"""
Agent Tool Usage Validation Suite

This script validates that agents are using real tools and producing real deliverables
instead of simulating work with sleep delays, hardcoded responses, or fake files.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentValidationSuite:
    """Comprehensive agent validation suite"""

    def __init__(self):
        self.test_results = {}
        self.violations_found = []
        self.fixes_applied = []

    async def validate_income_builder(self) -> Dict[str, Any]:
        """Validate Income Builder agent for real tool usage"""
        print("🧪 Validating Income Builder Agent...")

        try:
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz/intelligence/')
            from income_builder import AIIncomeBuilder, UserProfile, SkillLevel

            builder = AIIncomeBuilder()
            results = {
                "agent": "Income Builder",
                "ml_pipeline_test": None,
                "file_generation_test": None,
                "tool_integration_test": None,
                "market_research_test": None,
                "overall_score": 0
            }

            # Test 1: ML Pipeline Variability
            print("  Testing ML Pipeline...")
            user1 = {'skills': [], 'current_balance': 0, 'skill_level': 'beginner'}
            user2 = {'skills': ['writing', 'ai', 'marketing'], 'current_balance': 5000, 'skill_level': 'expert'}
            opp = {'stream_type': 'content_creation', 'required_skills': ['writing'], 'market_demand': 0.8}

            score1 = await builder.ml_pipeline.predict_opportunity_fit(user1, opp)
            score2 = await builder.ml_pipeline.predict_opportunity_fit(user2, opp)

            if score1['fit_score'] != score2['fit_score']:
                results["ml_pipeline_test"] = {
                    "status": "PASS",
                    "message": "ML Pipeline produces variable outputs",
                    "scores": [score1['fit_score'], score2['fit_score']],
                    "engine": score1.get('ml_engine', 'unknown')
                }
                results["overall_score"] += 25
            else:
                results["ml_pipeline_test"] = {
                    "status": "FAIL",
                    "message": "ML Pipeline returns hardcoded values",
                    "scores": [score1['fit_score'], score2['fit_score']]
                }
                self.violations_found.append("Income Builder: Hardcoded ML scores")

            # Test 2: File Generation
            print("  Testing File Generation...")
            user_profile = UserProfile(
                id='validation_test_user',
                skills=['writing', 'research'],
                skill_level=SkillLevel.INTERMEDIATE,
                current_balance=100.0,
                available_hours_per_week=25
            )

            action_plan = await builder.create_action_plan('validation_test_user', 'content_writing')

            if 'files_created' in action_plan:
                files = action_plan['files_created']
                real_files = []

                for file_path in files:
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        if size > 100:  # Must have substantial content
                            real_files.append((file_path, size))

                if real_files:
                    results["file_generation_test"] = {
                        "status": "PASS",
                        "message": f"Created {len(real_files)} real files",
                        "files": [{"path": f, "size": s} for f, s in real_files]
                    }
                    results["overall_score"] += 25

                    # Verify file content is real
                    for file_path, _ in real_files[:1]:
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                            if "Generated:" in content and "2025" in content:
                                results["overall_score"] += 10  # Bonus for real timestamps
                        except Exception:
                            pass
                else:
                    results["file_generation_test"] = {
                        "status": "FAIL",
                        "message": "No real files created",
                        "files_claimed": files
                    }
                    self.violations_found.append("Income Builder: Fake file generation")
            else:
                results["file_generation_test"] = {
                    "status": "FAIL",
                    "message": "No file generation attempted"
                }
                self.violations_found.append("Income Builder: No file generation")

            # Test 3: Tool Integration
            print("  Testing Tool Integration...")
            tools_available = getattr(builder, 'tools_available', {})
            if tools_available:
                active_tools = [k for k, v in tools_available.items() if v]
                if active_tools:
                    results["tool_integration_test"] = {
                        "status": "PASS",
                        "message": f"Tools initialized: {active_tools}",
                        "tools": tools_available
                    }
                    results["overall_score"] += 20
                else:
                    results["tool_integration_test"] = {
                        "status": "PARTIAL",
                        "message": "Tools configured but not active",
                        "tools": tools_available
                    }
                    results["overall_score"] += 10
            else:
                results["tool_integration_test"] = {
                    "status": "FAIL",
                    "message": "No tool integration found"
                }
                self.violations_found.append("Income Builder: No tool integration")

            # Test 4: Market Research Capability
            print("  Testing Market Research...")
            if hasattr(builder, 'research_market_opportunity'):
                # Test with first opportunity
                opportunity = builder.opportunities[0] if builder.opportunities else None
                if opportunity:
                    research = await builder.research_market_opportunity(opportunity)
                    if research.get('tools_used'):
                        results["market_research_test"] = {
                            "status": "PASS",
                            "message": f"Real tools used: {research['tools_used']}",
                            "data_sources": research.get('data_sources', [])
                        }
                        results["overall_score"] += 20
                    else:
                        results["market_research_test"] = {
                            "status": "LIMITED",
                            "message": "Market research method exists but no tools used",
                            "limitation": research.get('limitation', 'Unknown')
                        }
                        results["overall_score"] += 10
                else:
                    results["market_research_test"] = {
                        "status": "FAIL",
                        "message": "No opportunities to research"
                    }
            else:
                results["market_research_test"] = {
                    "status": "FAIL",
                    "message": "No market research capability"
                }
                self.violations_found.append("Income Builder: No market research")

            return results

        except Exception as e:
            logger.error(f"Income Builder validation failed: {e}")
            return {
                "agent": "Income Builder",
                "status": "ERROR",
                "error": str(e),
                "overall_score": 0
            }

    def validate_hardcoded_patterns(self) -> Dict[str, Any]:
        """Scan for hardcoded patterns in agent files"""
        print("🔍 Scanning for hardcoded patterns...")

        patterns_to_check = [
            ("time.sleep", "Sleep delay simulation"),
            ("return {\"fit_score\": 0.75}", "Hardcoded ML score"),
            ("mock", "Mock data usage"),
            ("example.com", "Fake URL usage"),
            ("lorem ipsum", "Placeholder text")
        ]

        violations = []
        agent_files = [
            '/Users/donkeyking/development/unified-donkey-betz/intelligence/income_builder.py',
            '/Users/donkeyking/development/unified-donkey-betz/ai_core/intelligence/income_builder.py',
            '/Users/donkeyking/development/unified-donkey-betz/ai_core/intelligence/monetization_engine.py'
        ]

        for file_path in agent_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    for pattern, description in patterns_to_check:
                        if pattern in content:
                            violations.append({
                                "file": file_path,
                                "pattern": pattern,
                                "description": description
                            })
                except Exception as e:
                    logger.error(f"Error scanning {file_path}: {e}")

        return {
            "test": "Hardcoded Pattern Scan",
            "violations_found": len(violations),
            "violations": violations,
            "status": "PASS" if len(violations) == 0 else "FAIL"
        }

    def check_real_file_outputs(self) -> Dict[str, Any]:
        """Check if agents create real files vs return fake paths"""
        print("📁 Checking for real file outputs...")

        output_dirs = [
            '/Users/donkeyking/development/unified-donkey-betz/portfolios',
            '/Users/donkeyking/development/unified-donkey-betz/action_plans'
        ]

        real_files = []
        for dir_path in output_dirs:
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        if size > 50:  # Must have real content
                            real_files.append({
                                "path": file_path,
                                "size": size,
                                "created": os.path.getctime(file_path)
                            })

        return {
            "test": "Real File Output Check",
            "real_files_found": len(real_files),
            "files": real_files[:10],  # Show first 10
            "status": "PASS" if len(real_files) > 0 else "FAIL"
        }

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation tests"""
        print("🚀 Starting Comprehensive Agent Validation Suite")
        print("=" * 60)

        results = {
            "validation_timestamp": str(asyncio.get_event_loop().time()),
            "tests_run": [],
            "overall_score": 0,
            "violations_found": [],
            "recommendations": []
        }

        # Test 1: Income Builder Agent
        income_builder_results = await self.validate_income_builder()
        results["tests_run"].append(income_builder_results)
        results["overall_score"] += income_builder_results.get("overall_score", 0)

        # Test 2: Hardcoded Pattern Scan
        pattern_results = self.validate_hardcoded_patterns()
        results["tests_run"].append(pattern_results)
        if pattern_results["status"] == "PASS":
            results["overall_score"] += 20

        # Test 3: Real File Output Check
        file_results = self.check_real_file_outputs()
        results["tests_run"].append(file_results)
        if file_results["status"] == "PASS":
            results["overall_score"] += 15

        # Compile violations and recommendations
        results["violations_found"] = self.violations_found

        if results["overall_score"] >= 80:
            results["status"] = "EXCELLENT"
            results["recommendations"] = ["System is performing well with real tool usage"]
        elif results["overall_score"] >= 60:
            results["status"] = "GOOD"
            results["recommendations"] = [
                "Minor improvements needed",
                "Enable more real tools for better performance"
            ]
        elif results["overall_score"] >= 40:
            results["status"] = "NEEDS_IMPROVEMENT"
            results["recommendations"] = [
                "Significant violations found",
                "Remove remaining hardcoded responses",
                "Implement more real tool integration"
            ]
        else:
            results["status"] = "CRITICAL"
            results["recommendations"] = [
                "Major violations detected",
                "System requires immediate fixes",
                "Replace all simulation code with real implementations"
            ]

        return results

    def print_validation_report(self, results: Dict[str, Any]):
        """Print a formatted validation report"""
        print("\n" + "=" * 60)
        print("🎯 AGENT TOOL VALIDATION REPORT")
        print("=" * 60)

        status = results.get("status", "UNKNOWN")
        score = results.get("overall_score", 0)

        status_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡",
            "NEEDS_IMPROVEMENT": "🟠",
            "CRITICAL": "🔴"
        }.get(status, "⚪")

        print(f"\n{status_emoji} Overall Status: {status}")
        print(f"📊 Overall Score: {score}/100")

        print(f"\n📋 Tests Run: {len(results.get('tests_run', []))}")
        for test in results.get('tests_run', []):
            test_name = test.get('agent', test.get('test', 'Unknown Test'))
            test_score = test.get('overall_score', 0)
            print(f"  • {test_name}: {test_score} points")

        violations = results.get('violations_found', [])
        if violations:
            print(f"\n⚠️ Violations Found ({len(violations)}):")
            for violation in violations:
                print(f"  • {violation}")

        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")

        print("\n" + "=" * 60)


async def main():
    """Main validation function"""
    validator = AgentValidationSuite()
    results = await validator.run_comprehensive_validation()
    validator.print_validation_report(results)

    # Save results to file
    import json
    results_file = "/Users/donkeyking/development/unified-donkey-betz/validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    return results


if __name__ == "__main__":
    asyncio.run(main())