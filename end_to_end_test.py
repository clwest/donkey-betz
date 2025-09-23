#!/usr/bin/env python3
"""
End-to-End Testing System for AI Project Builder
Shows real code generation, execution, and dynamic updates
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/Users/donkeyking/development/unified-donkey-betz/ai_generated_projects")

class EndToEndTestRunner:
    def __init__(self):
        self.test_results = []
        self.projects = ["ecommerce", "content_factory", "trading_bot", "predictive_analytics"]

    def run_command(self, cmd: str, description: str):
        """Run a command and capture output"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {description}")
        print(f"📋 Command: {cmd}")
        print(f"{'='*60}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd="/Users/donkeyking/development/unified-donkey-betz"
            )

            if result.stdout:
                print(result.stdout)

            if result.returncode == 0:
                print(f"✅ SUCCESS: {description}")
                self.test_results.append({"test": description, "status": "PASSED"})
            else:
                print(f"❌ FAILED: {description}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                self.test_results.append({"test": description, "status": "FAILED", "error": result.stderr})

            return result.returncode == 0

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            self.test_results.append({"test": description, "status": "ERROR", "error": str(e)})
            return False

    def test_project_switching(self):
        """Test switching between different projects"""
        print("\n" + "="*70)
        print("📊 TESTING PROJECT SWITCHING")
        print("="*70)

        for project in self.projects[:2]:  # Test first two projects
            self.run_command(
                f"python dynamic_project_builder.py switch {project}",
                f"Switch to {project} project"
            )
            time.sleep(2)

    def test_code_generation_uniqueness(self):
        """Test that code generated is unique each time"""
        print("\n" + "="*70)
        print("🔄 TESTING CODE GENERATION UNIQUENESS")
        print("="*70)

        # Generate same module twice and compare
        print("\n📝 First generation:")
        self.run_command(
            "python dynamic_project_builder.py build cart_recovery",
            "Generate cart_recovery module (1st time)"
        )

        # Save first version
        first_file = BASE_DIR / "ecommerce" / "cart_recovery.py"
        if first_file.exists():
            with open(first_file) as f:
                first_content = f.read()
                first_lines = len(first_content.split('\n'))
                print(f"📄 First version: {first_lines} lines")

        time.sleep(2)

        print("\n📝 Second generation:")
        self.run_command(
            "python dynamic_project_builder.py build cart_recovery",
            "Generate cart_recovery module (2nd time)"
        )

        # Compare with second version
        if first_file.exists():
            with open(first_file) as f:
                second_content = f.read()
                second_lines = len(second_content.split('\n'))
                print(f"📄 Second version: {second_lines} lines")

                if first_content != second_content:
                    print("✅ Code is UNIQUE each generation!")
                    # Show differences
                    print("\n🔍 Key differences found:")
                    # Extract build IDs
                    import re
                    first_build = re.search(r'Build ID: (\w+)', first_content)
                    second_build = re.search(r'Build ID: (\w+)', second_content)
                    if first_build and second_build:
                        print(f"  Build ID 1: {first_build.group(1)}")
                        print(f"  Build ID 2: {second_build.group(1)}")
                else:
                    print("⚠️ Code is identical (should be unique)")

    def test_code_execution(self):
        """Test that generated code actually runs"""
        print("\n" + "="*70)
        print("🚀 TESTING CODE EXECUTION")
        print("="*70)

        test_modules = [
            ("ecommerce", "cart_recovery"),
            ("content_factory", "content_generator"),
            ("trading_bot", "market_analyzer")
        ]

        for project, module in test_modules:
            # Switch to project
            self.run_command(
                f"python dynamic_project_builder.py switch {project}",
                f"Switch to {project}"
            )

            # Build module
            self.run_command(
                f"python dynamic_project_builder.py build {module}",
                f"Build {module} in {project}"
            )

            # Execute directly
            module_path = BASE_DIR / project / f"{module}.py"
            if module_path.exists():
                self.run_command(
                    f"python {module_path}",
                    f"Execute {module}.py directly"
                )

    def test_continuous_mode(self):
        """Test continuous build mode"""
        print("\n" + "="*70)
        print("⏰ TESTING CONTINUOUS MODE (10 seconds)")
        print("="*70)

        # Start continuous mode in background
        process = subprocess.Popen(
            ["python", "dynamic_project_builder.py", "continuous", "3"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/donkeyking/development/unified-donkey-betz"
        )

        print("🔄 Running continuous builds...")

        # Let it run for 10 seconds
        time.sleep(10)

        # Stop the process
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)

        if stdout:
            lines = stdout.split('\n')
            build_count = len([l for l in lines if "Building:" in l])
            print(f"\n✅ Completed {build_count} builds in continuous mode")

    def test_status_tracking(self):
        """Test that status is properly tracked"""
        print("\n" + "="*70)
        print("📈 TESTING STATUS TRACKING")
        print("="*70)

        # Generate some builds
        for _ in range(3):
            self.run_command(
                "python dynamic_project_builder.py build",
                "Generate build"
            )
            time.sleep(1)

        # Check status
        status_file = BASE_DIR / "dynamic_build_status.json"
        if status_file.exists():
            with open(status_file) as f:
                status = json.load(f)

            print("\n📊 Build Status:")
            print(f"  Timestamp: {status.get('timestamp', 'N/A')}")
            print(f"  Active Project: {status.get('active_project', 'N/A')}")
            print(f"  Iteration Count: {status.get('iteration', 0)}")

            print("\n📁 Project Progress:")
            for key, proj in status.get('projects', {}).items():
                print(f"  {proj['name']}: {proj['progress']:.1f}%")

    def generate_summary_report(self):
        """Generate a summary report of all tests"""
        print("\n" + "="*70)
        print("📊 END-TO-END TEST SUMMARY REPORT")
        print("="*70)

        total_tests = len(self.test_results)
        passed = sum(1 for t in self.test_results if t["status"] == "PASSED")
        failed = sum(1 for t in self.test_results if t["status"] == "FAILED")
        errors = sum(1 for t in self.test_results if t["status"] == "ERROR")

        print(f"\n🧪 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Errors: {errors}")

        if passed == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is working perfectly!")
        else:
            print("\n⚠️ Some tests failed. Review the output above for details.")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors
            },
            "details": self.test_results
        }

        report_path = BASE_DIR / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_path}")

    def run_all_tests(self):
        """Run all end-to-end tests"""
        print("🚀 STARTING END-TO-END TESTING SUITE")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)

        # Run test suites
        self.test_project_switching()
        self.test_code_generation_uniqueness()
        self.test_code_execution()
        self.test_status_tracking()

        # Optional: test continuous mode (takes time)
        if "--continuous" in sys.argv:
            self.test_continuous_mode()

        # Generate summary
        self.generate_summary_report()

        print(f"\n⏰ Completed at: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)

if __name__ == "__main__":
    runner = EndToEndTestRunner()
    runner.run_all_tests()