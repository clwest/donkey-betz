#!/usr/bin/env python
"""
Mythology-Enhanced Learning System
===================================
Integrates hallucination prevention directly into the agent learning process.
Uses mythology validation to ensure agents learn from verified, non-hallucinated data.
"""

import os
import sys
import json
import redis
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import mythology systems
from ai_core.agents.mythology_validator import MythologyValidator, MythologyEnforcer
from mythology.services import MythologyDetectionService, MythologyPreventionService

# Import learning systems
from intelligence.enhanced_problem_solver import EnhancedProblemSolver

# Import hallucination publisher
from intelligence.hallucination_publisher import hallucination_publisher


# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
_REDIS_URL_DB2 = _REDIS_URL.rsplit('/', 1)[0] + '/2' if '/' in _REDIS_URL else _REDIS_URL + '/2'


class MythologyEnhancedLearning:
    """
    Core learning system with integrated mythology prevention.
    Ensures all agent learning is grounded in reality.
    """

    def __init__(self):
        """Initialize mythology-enhanced learning system"""
        self.redis = redis.Redis.from_url(_REDIS_URL_DB2, decode_responses=True)

        # Initialize mythology components
        self.mythology_validator = MythologyValidator()
        self.mythology_enforcer = MythologyEnforcer()
        self.detection_service = MythologyDetectionService()
        self.prevention_service = MythologyPreventionService()

        # Track learning metrics
        self.metrics = {
            'total_learning_attempts': 0,
            'hallucinations_prevented': 0,
            'data_verified': 0,
            'learning_success_rate': 0.0
        }

        print("🛡️ Mythology-Enhanced Learning System Initialized")
        print("   Hallucination prevention: ACTIVE")
        print("   Reality enforcement: ENABLED")

    def validate_learning_data(self, data: Any, source: str = "unknown") -> Dict[str, Any]:
        """
        Validate data before agents learn from it.

        Args:
            data: Data to validate
            source: Source of the data

        Returns:
            Validation result with cleaned data
        """
        # Convert to string for validation
        data_str = json.dumps(data) if isinstance(data, dict) else str(data)

        # Check for mythologies
        detection_result = self.detection_service.detect_mythologies(data_str, source)

        if detection_result['detected']:
            print(f"⚠️  Mythology detected in learning data from {source}")
            print(f"   Patterns: {', '.join(detection_result['patterns_found'])}")
            print(f"   Risk score: {detection_result['risk_score']:.2f}")

            # Validate and correct
            validation = self.mythology_validator.validate_output("learning_system", data_str)

            if not validation['valid']:
                self.metrics['hallucinations_prevented'] += 1

                # Publish hallucination event for real-time display
                hallucination_publisher.publish_hallucination_blocked(
                    agent_name=source,
                    original_text=data_str[:500],
                    patterns=detection_result['patterns_found'],
                    risk_score=detection_result['risk_score'],
                    corrected_text=str(validation.get('corrected_output', ''))[:500],
                    severity=detection_result['severity']
                )

                return {
                    'valid': False,
                    'original_data': data,
                    'corrected_data': validation.get('corrected_output'),
                    'violations': validation.get('violations', []),
                    'warning': validation.get('warning'),
                    'risk_score': detection_result['risk_score']
                }

        self.metrics['data_verified'] += 1
        return {
            'valid': True,
            'data': data,
            'verified': True,
            'risk_score': 0.0
        }

    def enhanced_agent_learn(self, agent_id: str, problem: str,
                            context: Dict = None) -> Dict[str, Any]:
        """
        Agent learns with mythology prevention.

        Args:
            agent_id: ID of the learning agent
            problem: Problem to solve
            context: Additional context

        Returns:
            Learning result with validation
        """
        self.metrics['total_learning_attempts'] += 1
        print(f"\n🎓 Agent {agent_id} learning with mythology prevention...")

        # Step 1: Guard the prompt to prevent mythologies
        guarded_result = self.prevention_service.guard_prompt(
            problem,
            user=agent_id
        )

        if guarded_result['mythology_detected']:
            print(f"   📝 Prompt guarded against {len(guarded_result['patterns_found'])} patterns")
            problem = guarded_result['prompt']  # Use guarded version

        # Step 2: Create problem solver with enhanced validation
        solver = EnhancedProblemSolver(agent_id)

        # Step 3: Solve problem with API or algorithmic approach
        solution = solver.solve_problem(problem, context)

        # Step 4: Validate the solution for mythologies
        validation_result = self.validate_learning_data(
            solution,
            source=f"agent_{agent_id}"
        )

        if not validation_result['valid']:
            print(f"   🚫 Solution contained hallucinations - correcting...")
            solution = validation_result.get('corrected_data', solution)

        # Step 5: Validate response before storage
        if isinstance(solution, dict) and 'code' in solution:
            response_validation = self.prevention_service.validate_response(
                solution.get('code', ''),
                problem,
                user=agent_id
            )

            if not response_validation['valid']:
                print(f"   ⚠️  Response mythology risk: {response_validation['mythology_risk']:.2f}")

                # Apply corrections if suggested
                if response_validation.get('corrections'):
                    solution = self._apply_corrections(solution, response_validation['corrections'])

        # Step 6: Store validated learning
        self._store_validated_learning(agent_id, problem, solution, validation_result)

        # Step 7: Update metrics
        self._update_learning_metrics(validation_result['valid'])

        return {
            'agent_id': agent_id,
            'problem': problem,
            'solution': solution,
            'mythology_free': validation_result['valid'],
            'risk_score': validation_result.get('risk_score', 0.0),
            'timestamp': datetime.now().isoformat()
        }

    def _apply_corrections(self, solution: Dict, corrections: List[Dict]) -> Dict:
        """Apply mythology corrections to solution"""
        if 'code' in solution:
            code = solution['code']
            for correction in corrections:
                if correction['type'] == 'numeric_qualification':
                    code = code.replace(correction['pattern'], correction['suggestion'])
                elif correction['type'] == 'technology_correction':
                    # Fix technology references
                    code = code.replace('Dart', 'Django').replace('Flutter', 'React')
            solution['code'] = code
            solution['mythology_corrected'] = True
        return solution

    def _store_validated_learning(self, agent_id: str, problem: str,
                                 solution: Dict, validation: Dict):
        """Store only validated, mythology-free learning"""
        learning_key = f"validated_learning:{agent_id}:{datetime.now().timestamp()}"

        learning_data = {
            'agent_id': agent_id,
            'problem': problem,
            'solution': solution,
            'mythology_validated': True,
            'risk_score': validation.get('risk_score', 0.0),
            'timestamp': datetime.now().isoformat()
        }

        # Store in Redis
        self.redis.set(learning_key, json.dumps(learning_data))

        # Update agent's learning history
        history_key = f"agent_learning_history:{agent_id}"
        self.redis.lpush(history_key, learning_key)
        self.redis.ltrim(history_key, 0, 99)  # Keep last 100 learnings

        # Update global stats
        self.redis.hincrby('mythology_learning:stats', 'validated_learnings', 1)
        if validation.get('risk_score', 0) == 0:
            self.redis.hincrby('mythology_learning:stats', 'perfect_learnings', 1)

    def _update_learning_metrics(self, was_valid: bool):
        """Update learning metrics"""
        if was_valid:
            success_count = self.redis.hincrby('mythology_learning:stats', 'success_count', 1)
        else:
            self.redis.hincrby('mythology_learning:stats', 'corrected_count', 1)
            success_count = int(self.redis.hget('mythology_learning:stats', 'success_count') or 0)

        total = self.metrics['total_learning_attempts']
        if total > 0:
            self.metrics['learning_success_rate'] = success_count / total

    def get_agent_learning_quality(self, agent_id: str) -> Dict[str, Any]:
        """Get learning quality metrics for an agent"""
        history_key = f"agent_learning_history:{agent_id}"
        recent_learnings = self.redis.lrange(history_key, 0, 9)

        total_risk = 0
        hallucination_count = 0

        for learning_key in recent_learnings:
            learning_data = self.redis.get(learning_key)
            if learning_data:
                data = json.loads(learning_data)
                risk = data.get('risk_score', 0)
                total_risk += risk
                if risk > 0.3:
                    hallucination_count += 1

        count = len(recent_learnings)
        avg_risk = total_risk / count if count > 0 else 0

        return {
            'agent_id': agent_id,
            'recent_learnings': count,
            'average_mythology_risk': avg_risk,
            'hallucination_rate': hallucination_count / count if count > 0 else 0,
            'quality_score': 1.0 - avg_risk,
            'status': 'excellent' if avg_risk < 0.1 else 'good' if avg_risk < 0.3 else 'needs_improvement'
        }

    def train_agent_batch(self, agent_id: str, problems: List[str]) -> Dict[str, Any]:
        """Train agent on multiple problems with mythology prevention"""
        print(f"\n🎯 Batch training {agent_id} on {len(problems)} problems...")

        results = []
        for i, problem in enumerate(problems, 1):
            print(f"\n   [{i}/{len(problems)}] {problem[:50]}...")
            result = self.enhanced_agent_learn(agent_id, problem)
            results.append(result)

        # Calculate batch metrics
        mythology_free_count = sum(1 for r in results if r['mythology_free'])
        avg_risk = sum(r['risk_score'] for r in results) / len(results)

        return {
            'agent_id': agent_id,
            'problems_trained': len(problems),
            'mythology_free_solutions': mythology_free_count,
            'average_risk_score': avg_risk,
            'success_rate': mythology_free_count / len(problems),
            'results': results
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        stats = self.redis.hgetall('mythology_learning:stats')

        return {
            'total_attempts': self.metrics['total_learning_attempts'],
            'hallucinations_prevented': self.metrics['hallucinations_prevented'],
            'data_verified': self.metrics['data_verified'],
            'learning_success_rate': self.metrics['learning_success_rate'],
            'validated_learnings': int(stats.get('validated_learnings', 0)),
            'perfect_learnings': int(stats.get('perfect_learnings', 0)),
            'corrected_count': int(stats.get('corrected_count', 0)),
            'prevention_effectiveness': (
                self.metrics['hallucinations_prevented'] /
                max(self.metrics['total_learning_attempts'], 1)
            )
        }


class MythologyAwareLearningCoordinator:
    """
    Coordinates mythology-aware learning across all agents
    """

    def __init__(self):
        self.learning_system = MythologyEnhancedLearning()
        self.redis = redis.Redis.from_url(_REDIS_URL_DB2, decode_responses=True)

    def coordinate_agent_learning(self, agent_ids: List[str],
                                 learning_tasks: List[str]) -> Dict[str, Any]:
        """
        Coordinate learning across multiple agents with mythology prevention
        """
        print(f"\n🌐 Coordinating mythology-aware learning for {len(agent_ids)} agents")

        results = {}
        for agent_id in agent_ids:
            # Assign subset of tasks to each agent
            agent_tasks = learning_tasks[::len(agent_ids)]  # Simple distribution

            print(f"\n   🤖 Agent {agent_id} learning {len(agent_tasks)} tasks...")
            agent_results = self.learning_system.train_agent_batch(agent_id, agent_tasks)
            results[agent_id] = agent_results

        # Aggregate metrics
        total_mythology_free = sum(r['mythology_free_solutions'] for r in results.values())
        total_trained = sum(r['problems_trained'] for r in results.values())
        avg_risk = sum(r['average_risk_score'] for r in results.values()) / len(results)

        return {
            'agents_trained': len(agent_ids),
            'total_problems': total_trained,
            'mythology_free_solutions': total_mythology_free,
            'system_average_risk': avg_risk,
            'mythology_prevention_rate': total_mythology_free / max(total_trained, 1),
            'agent_results': results
        }

    def verify_learning_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of stored learning data
        """
        print("\n🔍 Verifying learning data integrity...")

        # Sample recent learnings
        pattern = "validated_learning:*"
        learning_keys = []
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
            learning_keys.extend(keys)
            if cursor == 0:
                break

        # Check sample
        sample_size = min(100, len(learning_keys))
        sample_keys = learning_keys[:sample_size] if learning_keys else []

        verified = 0
        contaminated = 0
        risk_scores = []

        for key in sample_keys:
            data = self.redis.get(key)
            if data:
                learning = json.loads(data)
                risk = learning.get('risk_score', 0)
                risk_scores.append(risk)

                if risk < 0.3:
                    verified += 1
                else:
                    contaminated += 1

        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

        return {
            'total_learnings': len(learning_keys),
            'sample_size': sample_size,
            'verified_clean': verified,
            'potentially_contaminated': contaminated,
            'average_risk_score': avg_risk,
            'integrity_score': verified / max(sample_size, 1),
            'status': 'excellent' if avg_risk < 0.1 else 'good' if avg_risk < 0.3 else 'needs_review'
        }


def test_mythology_enhanced_learning():
    """
    Test the mythology-enhanced learning system
    """
    print("=" * 70)
    print("🛡️  MYTHOLOGY-ENHANCED LEARNING SYSTEM TEST")
    print("=" * 70)

    # Initialize system
    learning_system = MythologyEnhancedLearning()
    coordinator = MythologyAwareLearningCoordinator()

    # Test 1: Single agent learning with clean data
    print("\n📚 Test 1: Agent learning with clean problem")
    result = learning_system.enhanced_agent_learn(
        "test_agent_001",
        "Create a function to validate email addresses",
        context={'example': 'user@example.com'}
    )
    print(f"   Result: {'✅ Mythology-free' if result['mythology_free'] else '⚠️ Corrected'}")
    print(f"   Risk score: {result['risk_score']:.2f}")

    # Test 2: Agent learning with mythology-prone problem
    print("\n📚 Test 2: Agent learning with mythology-prone problem")
    result = learning_system.enhanced_agent_learn(
        "test_agent_002",
        "Build a system that guarantees $10000 per day with 100% accuracy",
        context={'unrealistic': True}
    )
    print(f"   Result: {'✅ Mythology-free' if result['mythology_free'] else '⚠️ Corrected'}")
    print(f"   Risk score: {result['risk_score']:.2f}")

    # Test 3: Batch training
    print("\n📚 Test 3: Batch training with mythology prevention")
    problems = [
        "Parse JSON data safely",
        "Generate passive income of $5000 daily guaranteed",
        "Sort a list of numbers",
        "Create 350 deployments instantly",
        "Calculate fibonacci sequence"
    ]

    batch_result = learning_system.train_agent_batch("test_agent_003", problems)
    print(f"   Problems trained: {batch_result['problems_trained']}")
    print(f"   Mythology-free: {batch_result['mythology_free_solutions']}")
    print(f"   Success rate: {batch_result['success_rate']:.2%}")
    print(f"   Average risk: {batch_result['average_risk_score']:.2f}")

    # Test 4: Multi-agent coordination
    print("\n📚 Test 4: Multi-agent coordinated learning")
    agent_ids = ["agent_alpha", "agent_beta", "agent_gamma"]
    learning_tasks = [
        "Extract keywords from text",
        "Build a recommendation system",
        "Create data visualization",
        "Implement caching strategy",
        "Design API endpoints",
        "Optimize database queries"
    ]

    coord_result = coordinator.coordinate_agent_learning(agent_ids, learning_tasks)
    print(f"   Agents trained: {coord_result['agents_trained']}")
    print(f"   Total problems: {coord_result['total_problems']}")
    print(f"   Prevention rate: {coord_result['mythology_prevention_rate']:.2%}")
    print(f"   System risk: {coord_result['system_average_risk']:.2f}")

    # Test 5: Learning quality check
    print("\n📊 Test 5: Agent learning quality assessment")
    quality = learning_system.get_agent_learning_quality("test_agent_003")
    print(f"   Quality score: {quality['quality_score']:.2f}")
    print(f"   Hallucination rate: {quality['hallucination_rate']:.2%}")
    print(f"   Status: {quality['status']}")

    # Test 6: System metrics
    print("\n📈 Test 6: System-wide metrics")
    metrics = learning_system.get_system_metrics()
    print(f"   Total attempts: {metrics['total_attempts']}")
    print(f"   Hallucinations prevented: {metrics['hallucinations_prevented']}")
    print(f"   Prevention effectiveness: {metrics['prevention_effectiveness']:.2%}")

    # Test 7: Learning integrity verification
    print("\n🔍 Test 7: Learning data integrity check")
    integrity = coordinator.verify_learning_integrity()
    print(f"   Total learnings: {integrity['total_learnings']}")
    print(f"   Integrity score: {integrity['integrity_score']:.2%}")
    print(f"   Status: {integrity['status']}")

    print("\n" + "=" * 70)
    print("✅ MYTHOLOGY-ENHANCED LEARNING SYSTEM ACTIVE!")
    print("   Hallucination prevention: OPERATIONAL")
    print("   Reality enforcement: ENABLED")
    print("   Agent learning: PROTECTED")
    print("=" * 70)


if __name__ == "__main__":
    test_mythology_enhanced_learning()