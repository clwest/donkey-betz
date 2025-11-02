"""
Real Solution Model
===================

This model stores ACTUAL EXECUTABLE CODE as solutions, not just descriptions or metrics.
Every solution is real code that can be executed to solve problems.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional


class Solution:
    """
    Represents an actual solution with executable code
    """

    def __init__(self, problem_id: str, solution_code: str, discovered_by: str,
                 performance_metrics: Dict[str, Any], problem: str = ""):
        self.problem_id = problem_id
        self.problem = problem  # Store the actual problem description
        self.solution_code = solution_code  # ACTUAL EXECUTABLE CODE
        self.discovered_by = discovered_by
        self.performance_metrics = performance_metrics
        self.times_applied = 0
        self.success_rate = 0.0
        self.created_at = datetime.now()
        self.last_used = None
        self.improvements = []  # Track improvements over time

    def to_redis(self) -> Dict:
        """Convert to Redis-storable format"""
        return {
            'problem_id': self.problem_id,
            'problem': self.problem,  # The problem description
            'solution_code': self.solution_code,  # The actual code!
            'discovered_by': self.discovered_by,
            'performance': json.dumps(self.performance_metrics),
            'times_applied': self.times_applied,
            'success_rate': self.success_rate,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else '',
            'improvements': json.dumps(self.improvements)
        }

    @classmethod
    def from_redis(cls, data: Dict) -> 'Solution':
        """Reconstruct from Redis data"""
        solution = cls(
            problem_id=data['problem_id'],
            solution_code=data['solution_code'],
            discovered_by=data['discovered_by'],
            performance_metrics=json.loads(data.get('performance', '{}')),
            problem=data.get('problem', '')
        )
        solution.times_applied = int(data.get('times_applied', 0))
        solution.success_rate = float(data.get('success_rate', 0.0))
        if data.get('created_at'):
            solution.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            solution.last_used = datetime.fromisoformat(data['last_used'])
        if data.get('improvements'):
            solution.improvements = json.loads(data['improvements'])
        return solution

    def execute(self, context: Dict = None) -> Any:
        """Execute the actual solution code"""
        # Create execution environment
        exec_globals = {'context': context or {}}

        try:
            # Execute the solution code
            exec(self.solution_code, exec_globals)

            # Get the solution function
            if 'solution' in exec_globals:
                return exec_globals['solution']
            elif 'solve' in exec_globals:
                return exec_globals['solve']
            else:
                # Return all defined functions
                return {k: v for k, v in exec_globals.items()
                       if callable(v) and not k.startswith('_')}
        except Exception as e:
            return {'error': str(e), 'code': self.solution_code}

    def improve(self, new_code: str, improvement_metrics: Dict):
        """Track an improvement to this solution"""
        self.improvements.append({
            'timestamp': datetime.now().isoformat(),
            'old_code': self.solution_code,
            'new_code': new_code,
            'metrics': improvement_metrics
        })
        self.solution_code = new_code  # Update to improved version
        self.performance_metrics.update(improvement_metrics)


class SolutionPattern:
    """
    Represents a reusable solution pattern that can be applied to similar problems
    """

    def __init__(self, pattern_name: str, template_code: str, applicable_to: list):
        self.pattern_name = pattern_name
        self.template_code = template_code
        self.applicable_to = applicable_to  # List of problem types
        self.usage_count = 0
        self.success_count = 0

    def generate_solution(self, problem_specifics: Dict) -> str:
        """Generate specific solution from template"""
        # Replace placeholders in template with specifics
        solution = self.template_code

        for key, value in problem_specifics.items():
            placeholder = f"{{{key}}}"
            if placeholder in solution:
                solution = solution.replace(placeholder, str(value))

        return solution

    def applies_to_problem(self, problem_description: str) -> bool:
        """Check if this pattern applies to a given problem"""
        problem_lower = problem_description.lower()
        return any(keyword in problem_lower for keyword in self.applicable_to)