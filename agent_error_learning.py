#!/usr/bin/env python3
"""
Agent Error Learning System
Tracks errors and learns from successful fixes to improve over time
Enhanced with Django database persistence for production deployment
"""

import json
import os
import django
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup Django if not already configured
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unified_donkey_betz.settings')

try:
    django.setup()
    from core.models import ErrorPattern, ErrorInstance, AgentLearningSession, LearningInsight
    DJANGO_AVAILABLE = True
except Exception:
    DJANGO_AVAILABLE = False

class AgentErrorLearning:
    """
    Learning system that tracks error patterns and successful fixes
    to help agents get better at fixing errors over time
    """

    def __init__(self, history_file: str = "error_learning_history.json"):
        self.history_file = Path(history_file)
        self.error_patterns = self.load_history()
        self.fix_success_rate = {}
        self.use_database = DJANGO_AVAILABLE

        # Session tracking for database mode
        if self.use_database:
            self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.session_start = datetime.now()
            self.session_stats = {
                'errors_encountered': 0,
                'errors_fixed': 0,
                'new_patterns_learned': 0,
                'patterns_improved': 0
            }

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

    # Enhanced database methods for production deployment
    def find_matching_pattern_db(self, error_type: str, error_message: str, file_extension: str = '.py') -> Optional['ErrorPattern']:
        """Find the best matching error pattern from the database"""
        if not self.use_database:
            return None

        patterns = ErrorPattern.objects.filter(
            error_type=error_type,
            file_extension=file_extension
        ).order_by('-confidence_score', '-success_rate')

        for pattern in patterns:
            if self._match_error_pattern(pattern.error_message_pattern, error_message):
                return pattern

        return None

    def record_error_instance_db(self, error_info: Dict, solution_applied: str, fixed_code: str, was_successful: bool) -> Optional['ErrorInstance']:
        """Record an error instance in the database"""
        if not self.use_database:
            return None

        # Find or create matching pattern
        pattern_used = self.find_matching_pattern_db(
            error_info.get('error_type', 'Unknown'),
            error_info.get('error_message', ''),
            error_info.get('file_extension', '.py')
        )

        # Create error instance
        instance = ErrorInstance.objects.create(
            project_name=error_info.get('project_name', 'unknown'),
            file_name=error_info.get('file_name', ''),
            file_path=error_info.get('file_path', ''),
            error_type=error_info.get('error_type', 'Unknown'),
            error_message=error_info.get('error_message', ''),
            error_line_number=error_info.get('line_number'),
            error_context=error_info.get('error_context', ''),
            original_code=error_info.get('original_code', ''),
            solution_applied=solution_applied,
            fixed_code=fixed_code,
            fix_method=error_info.get('fix_method', 'agent_handler'),
            was_successful=was_successful,
            pattern_used=pattern_used,
            resolved_at=datetime.now() if was_successful else None
        )

        # Update session stats
        self.session_stats['errors_encountered'] += 1
        if was_successful:
            self.session_stats['errors_fixed'] += 1

            # Update pattern success rate if pattern was used
            if pattern_used:
                self._update_pattern_success_db(pattern_used, True)

        return instance

    def create_learning_pattern_db(self, error_info: Dict, solution_strategy: str, solution_template: str) -> Optional['ErrorPattern']:
        """Create a new learning pattern in the database"""
        if not self.use_database:
            return None

        # Generalize error message for pattern matching
        generalized_pattern = self._generalize_error_message(error_info.get('error_message', ''))

        pattern = ErrorPattern.objects.create(
            error_type=error_info.get('error_type', 'Unknown'),
            error_message_pattern=generalized_pattern,
            file_extension=error_info.get('file_extension', '.py'),
            project_type=error_info.get('project_type', ''),
            solution_strategy=solution_strategy,
            solution_template=solution_template,
            confidence_score=0.7,  # Start with moderate confidence
            usage_count=1,
            success_rate=1.0
        )

        self.session_stats['new_patterns_learned'] += 1
        return pattern

    def get_solution_suggestion_db(self, error_type: str, error_message: str, file_extension: str = '.py') -> Optional[Dict]:
        """Get solution suggestion from database patterns"""
        if not self.use_database:
            return None

        pattern = self.find_matching_pattern_db(error_type, error_message, file_extension)

        if pattern:
            return {
                'strategy': pattern.solution_strategy,
                'template': pattern.solution_template,
                'confidence': pattern.confidence_score,
                'pattern_id': pattern.id,
                'success_rate': pattern.success_rate,
                'usage_count': pattern.usage_count
            }

        return None

    def get_learning_insights_db(self, limit: int = 10) -> List[Dict]:
        """Get learning insights from database"""
        if not self.use_database:
            return []

        insights = LearningInsight.objects.filter(
            confidence_level__gte=0.6
        ).order_by('-impact_score', '-confidence_level')[:limit]

        return [
            {
                'title': insight.title,
                'description': insight.description,
                'confidence': insight.confidence_level,
                'impact': insight.impact_score,
                'times_applied': insight.times_applied,
                'success_rate': insight.success_when_applied / max(1, insight.times_applied)
            }
            for insight in insights
        ]

    def finalize_learning_session_db(self) -> Optional[Dict]:
        """Finalize learning session and save to database"""
        if not self.use_database:
            return None

        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds() / 60.0

        success_rate = (
            self.session_stats['errors_fixed'] / max(1, self.session_stats['errors_encountered'])
        )

        # Save session to database
        session = AgentLearningSession.objects.create(
            session_id=self.session_id,
            agent_type='AgentErrorHandler',
            total_errors_encountered=self.session_stats['errors_encountered'],
            total_errors_fixed=self.session_stats['errors_fixed'],
            success_rate=success_rate,
            new_patterns_learned=self.session_stats['new_patterns_learned'],
            patterns_improved=self.session_stats['patterns_improved'],
            knowledge_base_size_before=ErrorPattern.objects.count() - self.session_stats['new_patterns_learned'],
            knowledge_base_size_after=ErrorPattern.objects.count(),
            ended_at=session_end,
            session_duration_minutes=duration
        )

        return {
            'session_id': self.session_id,
            'duration_minutes': duration,
            'success_rate': success_rate,
            'stats': self.session_stats,
            'knowledge_base_growth': self.session_stats['new_patterns_learned']
        }

    def _match_error_pattern(self, pattern: str, error_message: str) -> bool:
        """Check if error message matches pattern"""
        import re
        try:
            return bool(re.search(pattern, error_message, re.IGNORECASE))
        except Exception:
            return False

    def _update_pattern_success_db(self, pattern: 'ErrorPattern', was_successful: bool):
        """Update pattern success statistics"""
        pattern.usage_count += 1

        # Update success rate with weighted average
        if pattern.usage_count == 1:
            pattern.success_rate = 1.0 if was_successful else 0.0
        else:
            weight = 0.3  # Weight for new result
            pattern.success_rate = (1 - weight) * pattern.success_rate + weight * (1.0 if was_successful else 0.0)

        # Adjust confidence based on success rate and usage count
        pattern.confidence_score = min(1.0, pattern.success_rate * (1.0 + 0.1 * min(10, pattern.usage_count)))

        pattern.save()

        if was_successful:
            self.session_stats['patterns_improved'] += 1

    def _generalize_error_message(self, error_message: str) -> str:
        """Convert specific error message to a generalizable regex pattern"""
        import re
        generalized = error_message

        # Replace quoted strings with pattern
        generalized = re.sub(r"'[^']*'", r"'[^']*'", generalized)
        generalized = re.sub(r'"[^"]*"', r'"[^"]*"', generalized)

        # Replace numbers with pattern
        generalized = re.sub(r'\b\d+\b', r'\\d+', generalized)

        # Replace variable names (simple approach)
        generalized = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', r'\\w+', generalized)

        # Escape special regex characters
        for char in '.[]{}()^$+*?|\\':
            if char not in ['\\d', '\\w']:  # Don't double-escape our patterns
                generalized = generalized.replace(char, '\\' + char)

        return generalized

    def get_hybrid_recommendation(self, error_type: str, error_message: str) -> Optional[Dict]:
        """Get recommendation using both database and file-based learning"""
        # Try database first (more sophisticated)
        db_recommendation = self.get_solution_suggestion_db(error_type, error_message)
        if db_recommendation and db_recommendation['confidence'] > 0.6:
            return {**db_recommendation, 'source': 'database'}

        # Fallback to file-based learning
        file_recommendation = self.get_recommended_fix(error_type, error_message)
        if file_recommendation:
            return {**file_recommendation, 'source': 'file'}

        return None


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