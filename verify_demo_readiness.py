#!/usr/bin/env python
"""
Demo Readiness Verifier
=======================
Checks that all components are ready for the AI Career Survival Platform demo
"""

import os
import redis
import json
from datetime import datetime
from pathlib import Path

class DemoReadinessChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.redis_connections = {}

        # Try to connect to Redis databases
        for db in [0, 2, 3, 4]:
            try:
                self.redis_connections[db] = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=db,
                    decode_responses=True
                )
                self.redis_connections[db].ping()
            except:
                self.redis_connections[db] = None

    def check(self, condition, description, details=""):
        """Run a single check and report results"""
        if condition:
            print(f"✅ {description}")
            if details:
                print(f"   {details}")
            self.checks_passed += 1
            return True
        else:
            print(f"❌ {description}")
            if details:
                print(f"   {details}")
            self.checks_failed += 1
            return False

    def check_files(self):
        """Check all required files exist"""
        print("\n📁 FILE SYSTEM CHECKS")
        print("-" * 40)

        required_files = {
            "Dashboards": [
                "learning_metrics_dashboard.html",
                "ai_career_survival_dashboard.html"
            ],
            "Phase Scripts": [
                "ai_career_survival/intelligence_gathering.py",
                "ai_career_survival/pattern_recognition.py",
                "ai_career_survival/expert_agents.py",
                "ai_career_survival/course_creation.py"
            ],
            "Core Systems": [
                "intelligence/problem_solver.py",
                "intelligence/spider_agent_router.py",
                "intelligence/knowledge_sharing.py",
                "intelligence/solution_storage.py"
            ],
            "Documentation": [
                "PLATFORM_COMPLETE_REVIEW.md",
                "DEMO_SCRIPT_AND_SHOWCASE.md"
            ]
        }

        for category, files in required_files.items():
            print(f"\n{category}:")
            for file in files:
                path = Path(file)
                self.check(
                    path.exists(),
                    f"{file}",
                    f"Size: {path.stat().st_size} bytes" if path.exists() else "File not found"
                )

    def check_redis_data(self):
        """Check Redis has required data"""
        print("\n💾 REDIS DATA CHECKS")
        print("-" * 40)

        if not any(self.redis_connections.values()):
            self.check(False, "Redis connection", "Cannot connect to Redis")
            return

        # Check DB 2 (Learning System)
        if r := self.redis_connections.get(2):
            solutions = len(r.keys("solution:*"))
            knowledge = len(r.keys("knowledge:*"))

            self.check(
                solutions > 0,
                f"Learning Solutions (DB 2)",
                f"Found {solutions} stored solutions"
            )

            self.check(
                knowledge > 0,
                f"Shared Knowledge (DB 2)",
                f"Found {knowledge} knowledge items"
            )

        # Check DB 4 (Career Platform)
        if r := self.redis_connections.get(4):
            phases = []
            for phase in range(1, 6):
                if r.exists(f"intelligence:complete:phase{phase}") or \
                   r.exists(f"patterns:complete:phase{phase}"):
                    phases.append(phase)

            self.check(
                len(phases) > 0,
                f"Career Platform Data (DB 4)",
                f"Phases with data: {phases if phases else 'None'}"
            )

    def check_processes(self):
        """Check if monitoring processes can be started"""
        print("\n⚙️ PROCESS CHECKS")
        print("-" * 40)

        scripts = [
            "run_live_monitor.py",
            "live_learning_simulator.py"
        ]

        for script in scripts:
            path = Path(script)
            self.check(
                path.exists() and path.stat().st_size > 0,
                f"{script}",
                "Ready to run" if path.exists() else "Script not found"
            )

    def check_demo_flow(self):
        """Verify the complete demo flow is ready"""
        print("\n🎬 DEMO FLOW CHECKS")
        print("-" * 40)

        # Check if we can import the phase modules
        phases_ready = []

        try:
            from ai_career_survival import intelligence_gathering
            phases_ready.append("Phase 1: Intelligence Gathering")
        except:
            pass

        try:
            from ai_career_survival import pattern_recognition
            phases_ready.append("Phase 2: Pattern Recognition")
        except:
            pass

        try:
            from ai_career_survival import expert_agents
            phases_ready.append("Phase 3: Expert Agents")
        except:
            pass

        try:
            from ai_career_survival import course_creation
            phases_ready.append("Phase 4: Course Creation")
        except:
            pass

        self.check(
            len(phases_ready) == 4,
            "All 4 phases importable",
            f"Ready: {', '.join([p.split(':')[0] for p in phases_ready])}"
        )

    def generate_quickstart(self):
        """Generate quickstart commands for demo"""
        print("\n🚀 DEMO QUICKSTART COMMANDS")
        print("-" * 40)

        print("\n# Step 1: Open Dashboards")
        print("open file:///Users/donkeyking/development/unified-donkey-betz/learning_metrics_dashboard.html")
        print("open file:///Users/donkeyking/development/unified-donkey-betz/ai_career_survival_dashboard.html")

        print("\n# Step 2: Start Monitor (optional)")
        print("python run_live_monitor.py &")

        print("\n# Step 3: Run Demo Phases")
        print("python ai_career_survival/intelligence_gathering.py")
        print("# Wait for completion...")
        print("python ai_career_survival/pattern_recognition.py")
        print("# Wait for completion...")
        print("python ai_career_survival/expert_agents.py")
        print("# Wait for completion...")
        print("python ai_career_survival/course_creation.py")

        print("\n# Step 4: Verify Results")
        print("redis-cli -n 4 GET 'monetization:projections' | python -m json.tool")

    def run_all_checks(self):
        """Run all verification checks"""
        print("=" * 50)
        print("🎯 AI CAREER SURVIVAL PLATFORM - DEMO READINESS")
        print("=" * 50)
        print(f"Time: {datetime.now()}")

        self.check_files()
        self.check_redis_data()
        self.check_processes()
        self.check_demo_flow()

        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("-" * 40)
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")

        if self.checks_failed == 0:
            print("\n🎉 SYSTEM IS DEMO READY!")
            self.generate_quickstart()
        else:
            print("\n⚠️ Some checks failed. Please review and fix before demo.")
            print("\nQuick fixes:")
            print("1. Ensure Redis is running: redis-server")
            print("2. Create missing directories: mkdir -p ai_career_survival")
            print("3. Check file paths and permissions")

        return self.checks_failed == 0


if __name__ == "__main__":
    checker = DemoReadinessChecker()
    ready = checker.run_all_checks()
    exit(0 if ready else 1)