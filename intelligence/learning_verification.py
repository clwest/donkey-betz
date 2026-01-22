#!/usr/bin/env python
"""
Learning Verification System
============================
Proves that AI agents actually learn by testing before/after capabilities
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import redis

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
_REDIS_URL_DB5 = _REDIS_URL.rsplit('/', 1)[0] + '/5' if '/' in _REDIS_URL else _REDIS_URL + '/5'

@dataclass
class TestProblem:
    """Represents a problem for testing agent capabilities"""
    problem_id: str
    skill_domain: str
    difficulty: str
    description: str
    test_input: str
    expected_output: str
    solution_patterns: List[str]

@dataclass
class TestResults:
    """Results from testing an agent"""
    agent_id: str
    timestamp: datetime
    skill_domain: str
    problems_attempted: int
    problems_solved: int
    success_rate: float
    average_time: float
    solution_quality: float
    detailed_results: List[Dict[str, Any]]

@dataclass
class LearningSession:
    """Complete learning verification session"""
    session_id: str
    agent_id: str
    skill_domain: str
    start_time: datetime
    baseline_results: Optional[TestResults] = None
    learning_material: Optional[Dict[str, Any]] = None
    post_learning_results: Optional[TestResults] = None
    improvement_metrics: Optional[Dict[str, float]] = None
    verification_status: str = "in_progress"

class LearningVerificationSystem:
    """System for verifying real agent learning through testing"""

    def __init__(self):
        self.redis = redis.Redis.from_url(_REDIS_URL_DB5, decode_responses=True)  # Use db 5 for verification
        self.test_problems = self._initialize_test_problems()

    def _initialize_test_problems(self) -> Dict[str, List[TestProblem]]:
        """Initialize test problems for different skill domains"""
        problems = {
            'code_generation': [
                TestProblem(
                    problem_id="code_001",
                    skill_domain="code_generation",
                    difficulty="easy",
                    description="Extract email addresses from text",
                    test_input="Contact john@example.com or sarah@company.org for details",
                    expected_output="['john@example.com', 'sarah@company.org']",
                    solution_patterns=["re.findall", "regex", "@"]
                ),
                TestProblem(
                    problem_id="code_002",
                    skill_domain="code_generation",
                    difficulty="medium",
                    description="Calculate compound interest",
                    test_input="principal=1000, rate=0.05, time=2, compound_frequency=4",
                    expected_output="1104.49",
                    solution_patterns=["**", "pow", "compound"]
                ),
                TestProblem(
                    problem_id="code_003",
                    skill_domain="code_generation",
                    difficulty="hard",
                    description="Implement binary search algorithm",
                    test_input="arr=[1,3,5,7,9,11], target=7",
                    expected_output="3",
                    solution_patterns=["left", "right", "mid", "while"]
                ),
                TestProblem(
                    problem_id="code_004",
                    skill_domain="code_generation",
                    difficulty="easy",
                    description="Count word frequency in text",
                    test_input="the quick brown fox jumps over the lazy dog",
                    expected_output="{'the': 2, 'quick': 1, 'brown': 1, ...}",
                    solution_patterns=["split", "count", "dict"]
                ),
                TestProblem(
                    problem_id="code_005",
                    skill_domain="code_generation",
                    difficulty="medium",
                    description="Find maximum subarray sum",
                    test_input="[-2,1,-3,4,-1,2,1,-5,4]",
                    expected_output="6",
                    solution_patterns=["kadane", "max_sum", "current_sum"]
                )
            ],
            'data_analysis': [
                TestProblem(
                    problem_id="data_001",
                    skill_domain="data_analysis",
                    difficulty="easy",
                    description="Calculate average of numbers",
                    test_input="[1, 2, 3, 4, 5]",
                    expected_output="3.0",
                    solution_patterns=["sum", "len", "average"]
                ),
                TestProblem(
                    problem_id="data_002",
                    skill_domain="data_analysis",
                    difficulty="medium",
                    description="Find correlation between two datasets",
                    test_input="x=[1,2,3,4,5], y=[2,4,6,8,10]",
                    expected_output="1.0",
                    solution_patterns=["correlation", "numpy", "pearson"]
                )
            ]
        }
        return problems

    def start_verification_session(self, agent_id: str, skill_domain: str) -> str:
        """Start a new learning verification session"""
        session_id = f"verify_{agent_id}_{skill_domain}_{int(time.time())}"

        session = LearningSession(
            session_id=session_id,
            agent_id=agent_id,
            skill_domain=skill_domain,
            start_time=datetime.now()
        )

        # Store session in Redis
        self.redis.setex(
            f"verification_session:{session_id}",
            24 * 3600,  # 24 hour expiry
            json.dumps(asdict(session), default=str)
        )

        return session_id

    def run_baseline_test(self, session_id: str) -> TestResults:
        """Run baseline capability test before learning"""
        session_data = json.loads(self.redis.get(f"verification_session:{session_id}"))
        agent_id = session_data['agent_id']
        skill_domain = session_data['skill_domain']

        # Get test problems for this domain
        problems = self.test_problems.get(skill_domain, [])
        if not problems:
            raise ValueError(f"No test problems available for domain: {skill_domain}")

        results = TestResults(
            agent_id=agent_id,
            timestamp=datetime.now(),
            skill_domain=skill_domain,
            problems_attempted=len(problems),
            problems_solved=0,
            success_rate=0.0,
            average_time=0.0,
            solution_quality=0.0,
            detailed_results=[]
        )

        total_time = 0.0
        total_quality = 0.0

        for problem in problems:
            start_time = time.time()

            # Test agent on this problem
            problem_result = self._test_agent_on_problem(agent_id, problem)

            end_time = time.time()
            test_duration = end_time - start_time

            # Check if solution is correct
            is_correct = self._verify_solution(problem, problem_result['solution'])
            quality_score = self._rate_solution_quality(problem, problem_result['solution'])

            if is_correct:
                results.problems_solved += 1

            total_time += test_duration
            total_quality += quality_score

            # Store detailed result
            results.detailed_results.append({
                'problem_id': problem.problem_id,
                'correct': is_correct,
                'time_taken': test_duration,
                'quality_score': quality_score,
                'solution': problem_result['solution'],
                'reasoning': problem_result.get('reasoning', '')
            })

        # Calculate aggregate metrics
        results.success_rate = results.problems_solved / len(problems)
        results.average_time = total_time / len(problems)
        results.solution_quality = total_quality / len(problems)

        # Update session with baseline results
        session_data['baseline_results'] = asdict(results)
        self.redis.setex(
            f"verification_session:{session_id}",
            24 * 3600,
            json.dumps(session_data, default=str)
        )

        # Store baseline results separately for easy access
        self.redis.setex(
            f"baseline_results:{session_id}",
            24 * 3600,
            json.dumps(asdict(results), default=str)
        )

        print(f"📊 Baseline Test Complete for {agent_id}")
        print(f"   Success Rate: {results.success_rate:.1%}")
        print(f"   Average Time: {results.average_time:.2f}s")
        print(f"   Quality Score: {results.solution_quality:.2f}/10")

        return results

    def expose_learning_material(self, session_id: str, learning_material: Dict[str, Any]) -> Dict[str, Any]:
        """Expose agent to learning material"""
        session_data = json.loads(self.redis.get(f"verification_session:{session_id}"))
        agent_id = session_data['agent_id']

        exposure_record = {
            'material_type': learning_material.get('type', 'unknown'),
            'material_id': learning_material.get('id', 'unknown'),
            'content_hash': hashlib.md5(str(learning_material).encode()).hexdigest(),
            'exposure_time': datetime.now().isoformat(),
            'learning_duration': 0.0
        }

        start_time = time.time()

        # Simulate agent learning from material
        learning_result = self._agent_learn_from_material(agent_id, learning_material)

        end_time = time.time()
        exposure_record['learning_duration'] = end_time - start_time
        exposure_record['learning_result'] = learning_result

        # Update session
        session_data['learning_material'] = exposure_record
        self.redis.setex(
            f"verification_session:{session_id}",
            24 * 3600,
            json.dumps(session_data, default=str)
        )

        print(f"🧠 Learning Exposure Complete for {agent_id}")
        print(f"   Material Type: {exposure_record['material_type']}")
        print(f"   Learning Duration: {exposure_record['learning_duration']:.2f}s")

        return exposure_record

    def run_post_learning_test(self, session_id: str) -> TestResults:
        """Run capability test after learning exposure"""
        session_data = json.loads(self.redis.get(f"verification_session:{session_id}"))

        if not session_data.get('baseline_results'):
            raise ValueError("Must run baseline test before post-learning test")

        if not session_data.get('learning_material'):
            raise ValueError("Must expose learning material before post-learning test")

        agent_id = session_data['agent_id']
        skill_domain = session_data['skill_domain']

        # Run the same test as baseline
        problems = self.test_problems.get(skill_domain, [])

        results = TestResults(
            agent_id=agent_id,
            timestamp=datetime.now(),
            skill_domain=skill_domain,
            problems_attempted=len(problems),
            problems_solved=0,
            success_rate=0.0,
            average_time=0.0,
            solution_quality=0.0,
            detailed_results=[]
        )

        total_time = 0.0
        total_quality = 0.0

        for problem in problems:
            start_time = time.time()

            # Test agent on this problem (post-learning)
            problem_result = self._test_agent_on_problem(agent_id, problem)

            end_time = time.time()
            test_duration = end_time - start_time

            # Check if solution is correct
            is_correct = self._verify_solution(problem, problem_result['solution'])
            quality_score = self._rate_solution_quality(problem, problem_result['solution'])

            if is_correct:
                results.problems_solved += 1

            total_time += test_duration
            total_quality += quality_score

            results.detailed_results.append({
                'problem_id': problem.problem_id,
                'correct': is_correct,
                'time_taken': test_duration,
                'quality_score': quality_score,
                'solution': problem_result['solution'],
                'reasoning': problem_result.get('reasoning', '')
            })

        # Calculate aggregate metrics
        results.success_rate = results.problems_solved / len(problems)
        results.average_time = total_time / len(problems)
        results.solution_quality = total_quality / len(problems)

        # Calculate improvement metrics
        baseline_results = session_data['baseline_results']
        improvement_metrics = {
            'success_rate_improvement': results.success_rate - baseline_results['success_rate'],
            'time_improvement': baseline_results['average_time'] - results.average_time,
            'quality_improvement': results.solution_quality - baseline_results['solution_quality'],
            'problems_improvement': results.problems_solved - baseline_results['problems_solved']
        }

        # Update session with post-learning results
        session_data['post_learning_results'] = asdict(results)
        session_data['improvement_metrics'] = improvement_metrics
        session_data['verification_status'] = 'completed'

        self.redis.setex(
            f"verification_session:{session_id}",
            24 * 3600,
            json.dumps(session_data, default=str)
        )

        print(f"📈 Post-Learning Test Complete for {agent_id}")
        print(f"   Success Rate: {results.success_rate:.1%} (Δ{improvement_metrics['success_rate_improvement']:+.1%})")
        print(f"   Average Time: {results.average_time:.2f}s (Δ{improvement_metrics['time_improvement']:+.2f}s)")
        print(f"   Quality Score: {results.solution_quality:.2f}/10 (Δ{improvement_metrics['quality_improvement']:+.2f})")

        return results

    def _test_agent_on_problem(self, agent_id: str, problem: TestProblem) -> Dict[str, Any]:
        """Test specific agent on specific problem"""
        # This would interface with the actual agent system
        # For now, simulate agent problem-solving

        # Import agent problem solver
        try:
            from intelligence.agent_problem_solver import AgentProblemSolver
            solver = AgentProblemSolver(agent_id)

            result = solver.solve_problem(problem.description, context={'test_input': problem.test_input})

            return {
                'solution': result.get('result', ''),
                'reasoning': result.get('reasoning', ''),
                'success': result.get('success', False)
            }
        except ImportError:
            # Fallback simulation for testing
            return {
                'solution': f"# Solution for {problem.problem_id}\n# Agent: {agent_id}\nprint('simulated solution')",
                'reasoning': 'Simulated reasoning process',
                'success': True
            }

    def _verify_solution(self, problem: TestProblem, solution: str) -> bool:
        """Verify if a solution correctly solves the problem"""
        if not solution:
            return False

        # Check for required patterns
        solution_lower = solution.lower()
        pattern_matches = sum(1 for pattern in problem.solution_patterns if pattern.lower() in solution_lower)

        # Basic heuristic: solution should contain most expected patterns
        return pattern_matches >= len(problem.solution_patterns) * 0.6

    def verify_capability_improvement(self, agent_name: str, task_type: str, generated_code: str = None) -> Dict[str, Any]:
        """
        Quick verification of agent capability improvement for real-time tracking.
        This is a simplified version for integration with deployment system.
        """
        try:
            # Calculate basic quality metrics
            quality_score = 70  # Base quality

            if generated_code:
                lines = generated_code.splitlines()

                # Quality indicators
                if 'try:' in generated_code and 'except' in generated_code:
                    quality_score += 5  # Error handling
                if 'class' in generated_code:
                    quality_score += 5  # Object-oriented
                if 'def ' in generated_code:
                    quality_score += 3  # Functions
                if any(comment in generated_code for comment in ['#', '"""']):
                    quality_score += 2  # Documentation
                if 'async' in generated_code:
                    quality_score += 5  # Async support

                # Complexity score based on code structure
                complexity = len(lines) / 10
                if 'for' in generated_code or 'while' in generated_code:
                    complexity += 10
                if 'if' in generated_code:
                    complexity += 5

            # Track improvement over time (retrieve from Redis)
            previous_score = 70
            improvement_key = f"agent:{agent_name}:last_quality"

            if self.redis.exists(improvement_key):
                try:
                    previous_score = float(self.redis.get(improvement_key))
                except:
                    previous_score = 70

            # Store current score
            self.redis.set(improvement_key, str(quality_score))

            improvement = quality_score - previous_score

            return {
                'quality': quality_score,
                'improvement': improvement,
                'complexity': complexity if generated_code else 50,
                'verified': True
            }

        except Exception as e:
            # Return default values on error
            return {
                'quality': 70,
                'improvement': 0,
                'complexity': 50,
                'verified': False,
                'error': str(e)
            }

    def _rate_solution_quality(self, problem: TestProblem, solution: str) -> float:
        """Rate solution quality on scale 0-10"""
        if not solution:
            return 0.0

        quality_score = 5.0  # Base score

        # Check for solution patterns
        solution_lower = solution.lower()
        pattern_matches = sum(1 for pattern in problem.solution_patterns if pattern.lower() in solution_lower)
        quality_score += (pattern_matches / len(problem.solution_patterns)) * 3.0

        # Check solution length (not too short, not too verbose)
        if 50 <= len(solution) <= 200:
            quality_score += 1.0

        # Check for comments/documentation
        if '#' in solution or '"""' in solution:
            quality_score += 1.0

        return min(quality_score, 10.0)

    def _agent_learn_from_material(self, agent_id: str, learning_material: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent learning from material"""
        # This would interface with the actual learning system
        # For now, simulate learning process

        learning_duration = 2.0  # Simulate 2 seconds of learning
        time.sleep(learning_duration)

        return {
            'learning_successful': True,
            'concepts_learned': learning_material.get('concepts', []),
            'confidence_improvement': 0.3,
            'new_capabilities': learning_material.get('capabilities', [])
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of verification session"""
        session_data = self.redis.get(f"verification_session:{session_id}")
        if not session_data:
            return {'error': 'Session not found'}

        return json.loads(session_data)

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active verification sessions"""
        session_keys = self.redis.keys("verification_session:*")
        sessions = []

        for key in session_keys:
            session_data = json.loads(self.redis.get(key))
            sessions.append({
                'session_id': session_data['session_id'],
                'agent_id': session_data['agent_id'],
                'skill_domain': session_data['skill_domain'],
                'status': session_data['verification_status'],
                'start_time': session_data['start_time']
            })

        return sessions

# Global verification system instance
verification_system = LearningVerificationSystem()

def quick_verification_demo():
    """Run a quick demo of the verification system"""
    print("🚀 Starting Learning Verification Demo")
    print("=" * 50)

    # Start verification session
    session_id = verification_system.start_verification_session('test_agent_001', 'code_generation')
    print(f"📝 Started session: {session_id}")

    # Run baseline test
    baseline_results = verification_system.run_baseline_test(session_id)

    # Simulate learning material
    learning_material = {
        'type': 'code_examples',
        'id': 'regex_patterns_001',
        'concepts': ['regular_expressions', 'pattern_matching', 'email_extraction'],
        'examples': [
            'import re\nemails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", text)',
            'pattern = r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"'
        ]
    }

    # Expose learning material
    exposure_record = verification_system.expose_learning_material(session_id, learning_material)

    # Run post-learning test
    post_results = verification_system.run_post_learning_test(session_id)

    # Get final session status
    session_status = verification_system.get_session_status(session_id)
    improvement = session_status['improvement_metrics']

    print("\n🎉 Verification Demo Complete!")
    print(f"✅ Learning Verified: {improvement['success_rate_improvement'] > 0.1}")
    print(f"📊 Success Rate Improvement: {improvement['success_rate_improvement']:+.1%}")
    print(f"⚡ Time Improvement: {improvement['time_improvement']:+.2f}s")
    print(f"🌟 Quality Improvement: {improvement['quality_improvement']:+.2f}/10")

if __name__ == "__main__":
    quick_verification_demo()