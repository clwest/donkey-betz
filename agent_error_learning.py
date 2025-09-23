#!/usr/bin/env python3
"""
Agent Error Learning System
Tracks errors and learns from successful fixes to improve over time
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class AgentErrorLearning:
    """
    Learning system that tracks error patterns and successful fixes
    to help agents get better at fixing errors over time
    """

    def __init__(self, history_file: str = "error_learning_history.json"):
        self.history_file = Path(history_file)
        self.error_patterns = self.load_history()
        self.fix_success_rate = {}

    def load_history(self) -> Dict:
        """Load error history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {
            "errors_encountered": [],
            "successful_fixes": [],
            "failed_fixes": [],
            "patterns": {}
        }

    def save_history(self):
        """Save error history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.error_patterns, f, indent=2, default=str)

    def record_error(self, error_type: str, error_msg: str, file_path: str, context: Dict = None):
        """Record an encountered error"""
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_msg,
            "file_path": file_path,
            "context": context or {}
        }

        self.error_patterns["errors_encountered"].append(error_record)

        # Track pattern frequency
        pattern_key = f"{error_type}:{error_msg[:50]}"
        if pattern_key not in self.error_patterns["patterns"]:
            self.error_patterns["patterns"][pattern_key] = {
                "count": 0,
                "fixes_attempted": 0,
                "fixes_successful": 0,
                "last_seen": None
            }

        self.error_patterns["patterns"][pattern_key]["count"] += 1
        self.error_patterns["patterns"][pattern_key]["last_seen"] = datetime.now().isoformat()

        self.save_history()

    def record_fix_attempt(self, error_type: str, fix_strategy: str, success: bool, details: Dict = None):
        """Record a fix attempt and whether it was successful"""
        fix_record = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "fix_strategy": fix_strategy,
            "success": success,
            "details": details or {}
        }

        if success:
            self.error_patterns["successful_fixes"].append(fix_record)
        else:
            self.error_patterns["failed_fixes"].append(fix_record)

        # Update pattern statistics
        pattern_key = f"{error_type}:{fix_strategy}"
        if pattern_key in self.error_patterns["patterns"]:
            self.error_patterns["patterns"][pattern_key]["fixes_attempted"] += 1
            if success:
                self.error_patterns["patterns"][pattern_key]["fixes_successful"] += 1

        self.save_history()

    def get_recommended_fix(self, error_type: str, error_msg: str) -> Optional[Dict]:
        """Get recommended fix strategy based on past success"""
        recommendations = []

        # Look for similar error patterns
        for pattern_key, stats in self.error_patterns["patterns"].items():
            if error_type in pattern_key:
                success_rate = 0
                if stats["fixes_attempted"] > 0:
                    success_rate = stats["fixes_successful"] / stats["fixes_attempted"]

                recommendations.append({
                    "pattern": pattern_key,
                    "success_rate": success_rate,
                    "attempts": stats["fixes_attempted"],
                    "successes": stats["fixes_successful"]
                })

        # Sort by success rate
        recommendations.sort(key=lambda x: x["success_rate"], reverse=True)

        if recommendations:
            return recommendations[0]
        return None

    def get_learning_report(self) -> Dict:
        """Generate a learning report"""
        total_errors = len(self.error_patterns["errors_encountered"])
        total_fixes_attempted = len(self.error_patterns["successful_fixes"]) + len(self.error_patterns["failed_fixes"])
        total_successful = len(self.error_patterns["successful_fixes"])

        success_rate = 0
        if total_fixes_attempted > 0:
            success_rate = (total_successful / total_fixes_attempted) * 100

        # Find most common errors
        error_frequency = {}
        for error in self.error_patterns["errors_encountered"]:
            error_type = error["error_type"]
            error_frequency[error_type] = error_frequency.get(error_type, 0) + 1

        # Find most successful fix strategies
        fix_strategies = {}
        for fix in self.error_patterns["successful_fixes"]:
            strategy = fix["fix_strategy"]
            fix_strategies[strategy] = fix_strategies.get(strategy, 0) + 1

        return {
            "total_errors_encountered": total_errors,
            "total_fixes_attempted": total_fixes_attempted,
            "total_successful_fixes": total_successful,
            "overall_success_rate": success_rate,
            "most_common_errors": sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_successful_strategies": sorted(fix_strategies.items(), key=lambda x: x[1], reverse=True)[:5],
            "learning_patterns": len(self.error_patterns["patterns"])
        }

    def suggest_improvements(self) -> List[str]:
        """Suggest improvements based on error patterns"""
        suggestions = []

        # Analyze patterns for common issues
        for pattern_key, stats in self.error_patterns["patterns"].items():
            if "NameError" in pattern_key and "random" in pattern_key:
                if stats["count"] > 3:
                    suggestions.append(
                        "Consider always importing 'random' module in code generation templates "
                        f"(seen {stats['count']} times)"
                    )

            if "AttributeError" in pattern_key:
                if stats["count"] > 2:
                    suggestions.append(
                        "Implement method existence checking before calling methods "
                        f"(AttributeError seen {stats['count']} times)"
                    )

            if "ImportError" in pattern_key:
                if stats["count"] > 2:
                    suggestions.append(
                        "Add dependency checking in project templates "
                        f"(ImportError seen {stats['count']} times)"
                    )

        # Suggest improvements for low success rates
        for pattern_key, stats in self.error_patterns["patterns"].items():
            if stats["fixes_attempted"] > 5:
                success_rate = stats["fixes_successful"] / stats["fixes_attempted"]
                if success_rate < 0.5:
                    suggestions.append(
                        f"Improve fix strategy for {pattern_key.split(':')[0]} "
                        f"(only {success_rate*100:.1f}% success rate)"
                    )

        return suggestions


# Example usage and testing
if __name__ == "__main__":
    learner = AgentErrorLearning()

    print("🧠 Agent Error Learning System")
    print("=" * 50)

    # Record some example errors and fixes
    learner.record_error(
        "NameError",
        "name 'random' is not defined",
        "/path/to/file.py",
        {"line": 25, "module": "market_analyzer"}
    )

    learner.record_fix_attempt(
        "NameError",
        "add_import_random",
        True,
        {"fix_location": "line 8", "import_added": "import random"}
    )

    # Get recommendations
    recommendation = learner.get_recommended_fix("NameError", "name 'random' is not defined")
    if recommendation:
        print(f"\n📊 Recommended Fix Strategy:")
        print(f"Pattern: {recommendation['pattern']}")
        print(f"Success Rate: {recommendation['success_rate']*100:.1f}%")
        print(f"Previous Attempts: {recommendation['attempts']}")
        print(f"Successful Fixes: {recommendation['successes']}")

    # Generate report
    report = learner.get_learning_report()
    print(f"\n📈 Learning Report:")
    print(f"Total Errors: {report['total_errors_encountered']}")
    print(f"Fixes Attempted: {report['total_fixes_attempted']}")
    print(f"Successful Fixes: {report['total_successful_fixes']}")
    print(f"Overall Success Rate: {report['overall_success_rate']:.1f}%")
    print(f"Learning Patterns: {report['learning_patterns']}")

    # Get improvement suggestions
    suggestions = learner.suggest_improvements()
    if suggestions:
        print(f"\n💡 Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("\n✨ No improvement suggestions at this time")