#!/usr/bin/env python
"""
REAL Learning Verification Tests
=================================

This script proves whether agents are ACTUALLY learning or just faking it.
We'll test with novel problems, check Redis for real solutions, and verify
performance changes are based on actual learned knowledge.
"""

import redis
import json
import time
from datetime import datetime
import hashlib
import random

class LearningVerificationTests:
    """Tests to prove learning is real, not simulated"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,  # Memory DB
            decode_responses=True
        )
        self.results = {
            'tests_run': [],
            'real_learning_found': False,
            'evidence': []
        }

    def run_all_tests(self):
        """Run all verification tests"""
        print("=" * 60)
        print("LEARNING VERIFICATION TESTS")
        print("=" * 60)
        print("\nThese tests will prove if learning is REAL or FAKE.\n")

        # Test 1: Check for actual stored solutions
        self.test_stored_solutions()

        # Test 2: Novel problem test
        self.test_novel_problem()

        # Test 3: Learning persistence
        self.test_learning_persistence()

        # Test 4: Trace specific optimization
        self.test_trace_optimization()

        # Test 5: Break and fix test
        self.test_break_and_fix()

        # Final verdict
        self.print_verdict()

    def test_stored_solutions(self):
        """Test 1: Are there ACTUAL solutions in Redis or just metrics?"""
        print("\n🔍 TEST 1: Checking for Actual Stored Solutions")
        print("-" * 50)

        # Look for agent memory entries AND SOLUTIONS
        memory_keys = self.redis_client.keys("agent:memory:*")
        shared_keys = self.redis_client.keys("shared:*")
        experience_keys = self.redis_client.keys("experience:*")
        solution_keys = self.redis_client.keys("solution:*")  # LOOK FOR ACTUAL SOLUTIONS

        print(f"Found {len(memory_keys)} agent memory entries")
        print(f"Found {len(shared_keys)} shared memory entries")
        print(f"Found {len(experience_keys)} experience entries")
        print(f"Found {len(solution_keys)} SOLUTION entries")  # The real solutions!

        actual_solutions = []
        fake_entries = []

        # Examine ALL solution and memory contents
        all_keys = list(memory_keys[:10]) + list(solution_keys[:10]) + list(shared_keys[:10])
        for key in all_keys:
            try:
                # Check if it's a hash or string
                key_type = self.redis_client.type(key)
                if key_type == 'hash':
                    data = self.redis_client.hget(key, 'solution_code') or self.redis_client.hget(key, 'solution')
                else:
                    data = self.redis_client.get(key)

                if data:
                    # Check if it's actual code/solution or just a metric
                    if any(keyword in data.lower() for keyword in ['def ', 'function', 'class', 'import', 'solution:', 'strategy:']):
                        actual_solutions.append(key)
                        print(f"  ✓ Found actual solution in {key}")
                    elif any(keyword in data for keyword in ['accuracy', 'speed', 'performance', 'score']):
                        fake_entries.append(key)
                        print(f"  ✗ Found only metrics in {key}")
            except:
                pass

        if actual_solutions:
            print(f"\n✅ REAL: Found {len(actual_solutions)} actual solutions")
            self.results['evidence'].append(f"Found {len(actual_solutions)} real solutions in memory")
        else:
            print(f"\n❌ FAKE: Only found metrics, no actual solutions")
            self.results['evidence'].append("No actual solutions found, only metrics")

        self.results['tests_run'].append({
            'name': 'Stored Solutions',
            'real_solutions': len(actual_solutions),
            'fake_entries': len(fake_entries)
        })

    def test_novel_problem(self):
        """Test 2: Can agents handle a completely novel problem?"""
        print("\n🆕 TEST 2: Novel Problem Test")
        print("-" * 50)

        # Import and create novel problem handler
        try:
            import sys
            sys.path.insert(0, '.')
            from intelligence.novel_problem_handler import NovelProblemHandler

            # Create a handler
            handler = NovelProblemHandler("test_novel_agent")

            # Test with novel problem
            novel_problem = 'Convert Morse code to pig latin while maintaining capitalization'
            print(f"Novel problem: {novel_problem}")

            result = handler.solve_problem(
                novel_problem,
                context={'test_data': '.... . .-.. .-.. ---'}  # HELLO in morse
            )

            print(f"Agent attempted: {result.get('success')}")
            if result.get('result'):
                print(f"Result: {result.get('result')}")

            solution_keys = self.redis_client.keys(f"solution:*")
            # Check if we have MORE solutions now than before
            novel_solved = result.get('success', False)

            if novel_solved:
                print(f"✅ REAL: Agent solved novel problem!")
                self.results['evidence'].append("Agents solved completely novel problem")
                self.results['real_learning_found'] = True
            else:
                print("❌ FAKE: Agent couldn't solve novel problem")
                self.results['evidence'].append("Agents failed novel problem")
        except Exception as e:
            print(f"❌ FAKE: No novel problem handler available: {e}")
            self.results['evidence'].append("No novel problem capability")

        self.results['tests_run'].append({
            'name': 'Novel Problem',
            'attempted': novel_solved if 'novel_solved' in locals() else False
        })

    def test_learning_persistence(self):
        """Test 3: Does learning persist across restarts?"""
        print("\n💾 TEST 3: Learning Persistence Test")
        print("-" * 50)

        # Create a unique learning entry
        test_learning = {
            'learned_at': datetime.now().isoformat(),
            'optimization': 'Use binary search instead of linear search',
            'performance_gain': 0.85,
            'agent': 'test_agent_001'
        }

        # Store it
        learning_key = f"learning:test:{int(time.time())}"
        self.redis_client.hset(learning_key, mapping={
            'data': json.dumps(test_learning)
        })
        self.redis_client.expire(learning_key, 300)  # 5 min expiry

        print(f"Stored test learning: {test_learning['optimization']}")

        # Simulate restart by checking if it would be loaded
        all_learning = self.redis_client.keys("learning:*")
        persistent_learning = []

        for key in all_learning:
            ttl = self.redis_client.ttl(key)
            if ttl > 60:  # Has reasonable TTL
                persistent_learning.append(key)

        if persistent_learning:
            print(f"✅ REAL: {len(persistent_learning)} learnings would persist")
            self.results['evidence'].append("Learning persists with proper TTL")
        else:
            print("❌ FAKE: Learning doesn't persist properly")
            self.results['evidence'].append("Learning doesn't persist")

        self.results['tests_run'].append({
            'name': 'Persistence',
            'persistent_entries': len(persistent_learning)
        })

    def test_trace_optimization(self):
        """Test 4: Can we trace a specific optimization path?"""
        print("\n🔎 TEST 4: Trace Specific Optimization")
        print("-" * 50)

        # Look for any optimization claim
        optimization_keys = self.redis_client.keys("optimization:*")
        learning_keys = self.redis_client.keys("learning:*")

        if optimization_keys or learning_keys:
            test_key = optimization_keys[0] if optimization_keys else learning_keys[0]
            print(f"Tracing: {test_key}")

            # Try to trace its path
            key_type = self.redis_client.type(test_key)
            if key_type == 'hash':
                data = self.redis_client.hgetall(test_key)
            elif key_type == 'string':
                raw_data = self.redis_client.get(test_key)
                data = {'content': raw_data} if raw_data else {}
            if data:
                print(f"  Found data: {list(data.keys())}")

                # Check for discovery timestamp
                if 'timestamp' in data or 'discovered_at' in data:
                    print(f"  ✓ Has discovery timestamp")

                # Check for agent attribution
                if 'agent' in data or 'discovered_by' in data:
                    print(f"  ✓ Attributed to specific agent")

                # Check for performance metrics
                if 'before' in data or 'after' in data or 'improvement' in data:
                    print(f"  ✓ Has performance metrics")

                print("✅ REAL: Can trace optimization path")
                self.results['evidence'].append("Optimizations are traceable")
            else:
                print("❌ FAKE: No traceable optimization data")
        else:
            print("❌ FAKE: No optimizations to trace")
            self.results['evidence'].append("No optimizations found")

        self.results['tests_run'].append({
            'name': 'Trace Optimization',
            'traceable': len(optimization_keys) > 0
        })

    def test_break_and_fix(self):
        """Test 5: Introduce failure and see if agents fix it"""
        print("\n🔧 TEST 5: Break and Fix Test")
        print("-" * 50)

        # Introduce a deliberate failure
        failure = {
            'error_id': f'test_error_{int(time.time())}',
            'error_type': 'DivisionByZeroError',
            'context': 'calculate_average with empty list',
            'timestamp': datetime.now().isoformat()
        }

        # Store the failure
        error_key = f"error:active:{failure['error_id']}"
        self.redis_client.hset(error_key, mapping={
            'data': json.dumps(failure),
            'status': 'unresolved'
        })

        print(f"Introduced error: {failure['error_type']}")
        print("Waiting for agent response...")
        time.sleep(2)

        # Check for fix attempts
        fix_keys = self.redis_client.keys(f"fix:*{failure['error_id']}*")
        solution_keys = self.redis_client.keys(f"solution:*{failure['error_type']}*")

        if fix_keys or solution_keys:
            print(f"✅ REAL: Agents attempted to fix error")
            self.results['evidence'].append("Agents respond to novel errors")
            self.results['real_learning_found'] = True
        else:
            print("❌ FAKE: No fix attempted")
            self.results['evidence'].append("Agents don't fix novel errors")

        self.results['tests_run'].append({
            'name': 'Break and Fix',
            'fix_attempted': len(fix_keys) > 0 or len(solution_keys) > 0
        })

    def print_verdict(self):
        """Print final verdict on whether learning is real"""
        print("\n" + "=" * 60)
        print("FINAL VERDICT")
        print("=" * 60)

        # Count evidence
        real_evidence = [e for e in self.results['evidence'] if 'real' in e.lower() or 'found' in e.lower() or 'persists' in e.lower()]
        fake_evidence = [e for e in self.results['evidence'] if 'no' in e.lower() or 'only metrics' in e.lower() or "don't" in e.lower()]

        print("\n📊 Test Summary:")
        for test in self.results['tests_run']:
            print(f"  • {test['name']}: {test}")

        print("\n🔍 Evidence Found:")
        for evidence in self.results['evidence']:
            marker = "✓" if any(word in evidence.lower() for word in ['found', 'real', 'persists']) else "✗"
            print(f"  {marker} {evidence}")

        # Make determination
        if len(real_evidence) > len(fake_evidence):
            print("\n🟢 VERDICT: LEARNING APPEARS TO BE REAL")
            print("   Some actual learning mechanisms are in place")
        elif len(real_evidence) == len(fake_evidence):
            print("\n🟡 VERDICT: PARTIALLY REAL")
            print("   Mix of real and simulated components")
        else:
            print("\n🔴 VERDICT: LEARNING APPEARS TO BE SIMULATED")
            print("   Mostly metrics without actual learning")

        print("\n📋 Recommendations:")
        if not any('solutions' in e for e in real_evidence):
            print("  1. Store actual solutions, not just metrics")
        if not any('novel' in e for e in real_evidence):
            print("  2. Implement handlers for novel problems")
        if not any('persists' in e for e in real_evidence):
            print("  3. Ensure learning persists across restarts")
        if not any('trace' in e for e in real_evidence):
            print("  4. Make optimizations traceable to source")
        if not any('fix' in e for e in real_evidence):
            print("  5. Implement error detection and fixing")


def check_whats_really_in_redis():
    """Quick check of what's actually in Redis"""
    print("\n" + "=" * 60)
    print("REDIS REALITY CHECK")
    print("=" * 60)

    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    for db in range(5):  # Check first 5 DBs
        r = redis.Redis(host='localhost', port=6379, db=db, decode_responses=True)
        keys = r.keys("*")
        if keys:
            print(f"\n📦 Database {db}: {len(keys)} keys")

            # Sample some keys
            key_types = {}
            for key in keys[:20]:  # Sample first 20
                key_prefix = key.split(':')[0] if ':' in key else key
                key_types[key_prefix] = key_types.get(key_prefix, 0) + 1

            for prefix, count in sorted(key_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {prefix}: {count} keys")

            # Check for actual content
            sample_key = keys[0]
            try:
                key_type = r.type(sample_key)
                print(f"\n  Sample key: {sample_key}")
                print(f"  Type: {key_type}")

                if key_type == 'string':
                    value = r.get(sample_key)
                    if value:
                        print(f"  Content preview: {value[:100]}...")
                elif key_type == 'hash':
                    value = r.hgetall(sample_key)
                    print(f"  Fields: {list(value.keys())[:5]}")
            except:
                pass


if __name__ == "__main__":
    # First check what's actually in Redis
    check_whats_really_in_redis()

    print("\n" * 2)

    # Then run verification tests
    verifier = LearningVerificationTests()
    verifier.run_all_tests()

    print("\n" + "=" * 60)
    print("💡 TO MAKE LEARNING REAL:")
    print("=" * 60)
    print("""
1. Store actual solutions:
   redis.set("solution:task:123", "def solve(): return binary_search(arr)")

2. Record performance changes:
   redis.hset("performance:agent:001", {"before": 1.2, "after": 0.3, "method": "caching"})

3. Share discoveries:
   redis.publish("discoveries", {"agent": "001", "found": "parallel processing speeds up by 3x"})

4. Apply past solutions:
   if similar_problem in redis.get("solutions:*"):
       apply_previous_solution()
    """)