"""
Solution Storage System
=======================

Stores and retrieves ACTUAL SOLUTIONS (executable code), not just metrics.
This is where real learning gets persisted.
"""

import redis
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from intelligence.reallearning.solution import Solution, SolutionPattern


class SolutionStorage:
    """
    Manages storage of actual solutions in Redis
    """

    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=2,  # Learning database
            decode_responses=True
        )

    def store_solution(self, problem: str, solution_code: str, agent_id: str,
                      test_results: Dict = None) -> str:
        """
        Store ACTUAL solution code, not just metrics

        Args:
            problem: Problem description
            solution_code: The ACTUAL EXECUTABLE CODE
            agent_id: ID of agent that discovered this
            test_results: Performance test results

        Returns:
            solution_key: Redis key where solution is stored
        """
        # Generate unique key for this problem
        problem_hash = hashlib.md5(problem.encode()).hexdigest()[:8]
        solution_key = f"solution:{problem_hash}:{agent_id}:{int(datetime.now().timestamp())}"

        # Create solution object
        solution = Solution(
            problem_id=problem_hash,
            solution_code=solution_code,
            discovered_by=agent_id,
            performance_metrics=test_results or {},
            problem=problem
        )

        # Store the actual solution
        self.redis.hset(solution_key, mapping=solution.to_redis())

        # Index for quick lookup
        self.redis.sadd(f"solutions:by_agent:{agent_id}", solution_key)
        self.redis.sadd(f"solutions:by_problem:{problem_hash}", solution_key)
        self.redis.sadd("solutions:all", solution_key)

        # Store problem description for searching
        self.redis.hset(f"problems:{problem_hash}", mapping={
            'description': problem,
            'first_solved': datetime.now().isoformat(),
            'solution_count': 0
        })
        self.redis.hincrby(f"problems:{problem_hash}", 'solution_count', 1)

        print(f"✅ Stored actual solution: {solution_key}")
        print(f"   Code length: {len(solution_code)} chars")

        return solution_key

    def find_similar_solution(self, problem: str, similarity_threshold: float = 0.7) -> Optional[Solution]:
        """
        Find existing solution for similar problem
        """
        # Get all problems
        problem_keys = self.redis.keys("problems:*")

        best_match = None
        best_score = 0

        for key in problem_keys:
            stored_problem = self.redis.hget(key, 'description')
            if stored_problem:
                # Simple similarity check (can be improved with embeddings)
                score = self._calculate_similarity(problem, stored_problem)

                if score > best_score and score >= similarity_threshold:
                    best_score = score
                    problem_hash = key.split(':')[1]

                    # Get solutions for this problem
                    solution_keys = self.redis.smembers(f"solutions:by_problem:{problem_hash}")
                    if solution_keys:
                        # Get the best performing solution
                        best_solution_key = self._get_best_solution(solution_keys)
                        if best_solution_key:
                            solution_data = self.redis.hgetall(best_solution_key)
                            best_match = Solution.from_redis(solution_data)

        return best_match

    def _calculate_similarity(self, problem1: str, problem2: str) -> float:
        """Calculate similarity between two problems"""
        # Simple word overlap similarity
        words1 = set(problem1.lower().split())
        words2 = set(problem2.lower().split())

        if not words1 or not words2:
            return 0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _get_best_solution(self, solution_keys: set) -> Optional[str]:
        """Get best performing solution from a set of keys"""
        best_key = None
        best_score = -1

        for key in solution_keys:
            data = self.redis.hget(key, 'success_rate')
            if data:
                score = float(data)
                if score > best_score:
                    best_score = score
                    best_key = key

        return best_key or (list(solution_keys)[0] if solution_keys else None)

    def get_agent_solutions(self, agent_id: str) -> List[Solution]:
        """Get all solutions discovered by an agent"""
        solution_keys = self.redis.smembers(f"solutions:by_agent:{agent_id}")
        solutions = []

        for key in solution_keys:
            data = self.redis.hgetall(key)
            if data:
                solutions.append(Solution.from_redis(data))

        return solutions

    def update_solution_metrics(self, solution_key: str, success: bool, execution_time: float):
        """Update solution performance metrics after use"""
        # Increment usage count
        self.redis.hincrby(solution_key, 'times_applied', 1)

        # Update success rate
        times_applied = int(self.redis.hget(solution_key, 'times_applied'))
        current_rate = float(self.redis.hget(solution_key, 'success_rate') or 0)

        # Calculate new success rate
        if times_applied > 1:
            new_rate = ((current_rate * (times_applied - 1)) + (1 if success else 0)) / times_applied
        else:
            new_rate = 1 if success else 0

        self.redis.hset(solution_key, 'success_rate', new_rate)
        self.redis.hset(solution_key, 'last_used', datetime.now().isoformat())

        # Update execution time in performance metrics
        perf_data = self.redis.hget(solution_key, 'performance')
        if perf_data:
            perf = json.loads(perf_data)
            perf['last_execution_time'] = execution_time

            # Track average execution time
            if 'avg_execution_time' in perf:
                perf['avg_execution_time'] = (
                    (perf['avg_execution_time'] * (times_applied - 1) + execution_time) / times_applied
                )
            else:
                perf['avg_execution_time'] = execution_time

            self.redis.hset(solution_key, 'performance', json.dumps(perf))

    def store_pattern(self, pattern: SolutionPattern) -> str:
        """Store a reusable solution pattern"""
        pattern_key = f"pattern:{pattern.pattern_name}"

        self.redis.hset(pattern_key, mapping={
            'name': pattern.pattern_name,
            'template_code': pattern.template_code,
            'applicable_to': json.dumps(pattern.applicable_to),
            'usage_count': pattern.usage_count,
            'success_count': pattern.success_count
        })

        self.redis.sadd("patterns:all", pattern_key)
        return pattern_key

    def get_applicable_patterns(self, problem: str) -> List[SolutionPattern]:
        """Get patterns that might apply to this problem"""
        pattern_keys = self.redis.smembers("patterns:all")
        applicable = []

        for key in pattern_keys:
            data = self.redis.hgetall(key)
            if data:
                keywords = json.loads(data.get('applicable_to', '[]'))
                problem_lower = problem.lower()

                if any(keyword in problem_lower for keyword in keywords):
                    pattern = SolutionPattern(
                        pattern_name=data['name'],
                        template_code=data['template_code'],
                        applicable_to=keywords
                    )
                    pattern.usage_count = int(data.get('usage_count', 0))
                    pattern.success_count = int(data.get('success_count', 0))
                    applicable.append(pattern)

        return applicable

    def get_statistics(self) -> Dict:
        """Get learning statistics"""
        stats = {
            'total_solutions': self.redis.scard("solutions:all"),
            'total_problems': len(self.redis.keys("problems:*")),
            'total_patterns': self.redis.scard("patterns:all"),
            'agents_with_solutions': len(self.redis.keys("solutions:by_agent:*")),
            'top_solvers': []
        }

        # Get top solving agents
        agent_keys = self.redis.keys("solutions:by_agent:*")
        for key in agent_keys:
            agent_id = key.split(':')[-1]
            solution_count = self.redis.scard(key)
            stats['top_solvers'].append({
                'agent_id': agent_id,
                'solutions': solution_count
            })

        stats['top_solvers'].sort(key=lambda x: x['solutions'], reverse=True)
        stats['top_solvers'] = stats['top_solvers'][:5]

        return stats


# Test the storage
if __name__ == "__main__":
    storage = SolutionStorage()

    # Store a real solution
    test_solution = '''
def solution(skills, job_requirements):
    """Match user skills to job requirements"""
    matches = []
    for job in job_requirements:
        score = 0
        for skill in skills:
            if skill in job.get('required_skills', []):
                score += 2
            elif skill in job.get('preferred_skills', []):
                score += 1
        if score > 0:
            matches.append((job['id'], score))

    # Return sorted by score
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:10]  # Top 10 matches
'''

    key = storage.store_solution(
        problem="Match user skills to job requirements and return top 10",
        solution_code=test_solution,
        agent_id="job_matcher_001",
        test_results={'execution_time': 0.002, 'accuracy': 0.95}
    )

    print(f"\nStored solution with key: {key}")

    # Retrieve statistics
    stats = storage.get_statistics()
    print(f"\nStorage Statistics: {json.dumps(stats, indent=2)}")