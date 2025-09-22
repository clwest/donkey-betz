#!/usr/bin/env python
"""
Live Learning Simulator
=======================

Simulates agents actively learning, solving problems, and sharing knowledge.
This creates REAL activity that can be watched on the dashboard.
"""

import sys
sys.path.insert(0, '.')
import time
import random
import threading
from datetime import datetime
from intelligence.problem_solver import AgentProblemSolver
from intelligence.novel_problem_handler import NovelProblemHandler
from intelligence.knowledge_sharing import LearningAgent, KnowledgeSharing
import redis


class LiveLearningSimulator:
    """Simulates real agent learning activity"""

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
        self.agents = {}
        self.sharing = KnowledgeSharing()
        self.running = True
        self.activity_count = 0

        # Sample problems for agents to solve
        self.problems = [
            "Extract phone numbers from text",
            "Calculate the median of numbers",
            "Sort list by multiple criteria",
            "Convert hexadecimal to decimal",
            "Find unique elements in list",
            "Parse CSV data",
            "Validate email format",
            "Extract URLs from HTML",
            "Calculate standard deviation",
            "Compress string using RLE",
            "Find longest common substring",
            "Convert Roman numerals to integers",
            "Generate fibonacci sequence",
            "Check if string is palindrome",
            "Extract hashtags from text",
            "Calculate compound interest",
            "Parse command line arguments",
            "Validate credit card number",
            "Convert temperature units",
            "Generate random password"
        ]

    def create_agents(self):
        """Create a diverse set of agents"""
        agent_types = [
            ('expert_solver', AgentProblemSolver),
            ('novel_handler', NovelProblemHandler),
            ('pattern_finder', AgentProblemSolver),
            ('optimizer', AgentProblemSolver),
            ('learner_001', NovelProblemHandler),
            ('analyzer', AgentProblemSolver),
            ('validator', NovelProblemHandler)
        ]

        print("🤖 Creating agents...")
        for agent_id, agent_class in agent_types:
            agent = agent_class(agent_id)
            learner = LearningAgent(agent_id)
            learner.start_learning()

            self.agents[agent_id] = {
                'solver': agent,
                'learner': learner,
                'problems_solved': 0,
                'solutions_created': 0,
                'knowledge_shared': 0
            }
            print(f"   ✓ Created {agent_id}")

    def simulate_problem_solving(self):
        """Simulate an agent solving a problem"""
        # Pick random agent and problem
        agent_id = random.choice(list(self.agents.keys()))
        problem = random.choice(self.problems)
        agent = self.agents[agent_id]

        print(f"\n🎯 {agent_id} attempting: {problem[:50]}...")

        # Generate test data based on problem type
        test_data = self.generate_test_data(problem)

        try:
            # Attempt to solve
            result = agent['solver'].solve_problem(problem, context={'test_data': test_data})

            if result.get('success'):
                agent['problems_solved'] += 1
                agent['solutions_created'] += 1

                # Update global stats
                self.redis.hincrby('learning:stats:global', 'problems_solved', 1)
                self.redis.hincrby('learning:stats:global', 'solutions_created', 1)

                print(f"   ✅ Solved! Result: {str(result.get('result'))[:100]}")

                # Share the discovery
                if random.random() > 0.5:
                    self.sharing.share_discovery(
                        agent_id,
                        problem,
                        result.get('solution', ''),
                        {'execution_time': result.get('execution_time', 0)}
                    )
                    agent['knowledge_shared'] += 1
                    self.redis.hincrby('learning:stats:global', 'knowledge_shared', 1)

                return True
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    def generate_test_data(self, problem):
        """Generate appropriate test data for problem"""
        problem_lower = problem.lower()

        if 'phone' in problem_lower:
            return "Call 555-1234 or (800) 555-5678 for support"
        elif 'email' in problem_lower:
            return "Contact us at info@example.com or support@test.org"
        elif 'number' in problem_lower or 'median' in problem_lower or 'average' in problem_lower:
            return [random.randint(1, 100) for _ in range(10)]
        elif 'url' in problem_lower:
            return "Visit https://example.com and http://test.org for more"
        elif 'csv' in problem_lower:
            return "name,age,city\\nJohn,30,NYC\\nJane,25,LA"
        elif 'hex' in problem_lower:
            return "FF00AA"
        elif 'roman' in problem_lower:
            return "MCMXCIV"
        elif 'palindrome' in problem_lower:
            return "racecar"
        elif 'hashtag' in problem_lower:
            return "Check out #AI and #MachineLearning trends"
        else:
            return "Test input data"

    def simulate_learning_from_others(self):
        """Simulate agents learning from shared knowledge"""
        agent_id = random.choice(list(self.agents.keys()))
        agent = self.agents[agent_id]

        print(f"\n📚 {agent_id} learning from others...")

        learned = agent['learner'].knowledge_sharing.learn_from_others(agent_id, limit=3)

        if learned:
            print(f"   ✅ Learned {len(learned)} solutions from other agents")
            self.redis.hincrby('learning:stats:global', 'solutions_learned', len(learned))
            return True
        else:
            print(f"   ℹ️ No new knowledge to learn")
            return False

    def update_dashboard_stats(self):
        """Update stats for dashboard to fetch"""
        stats = self.redis.hgetall('learning:stats:global')

        # Calculate reality score based on activity
        solutions = int(stats.get('solutions_created', 0))
        shared = int(stats.get('knowledge_shared', 0))
        learned = int(stats.get('solutions_learned', 0))

        if solutions > 0:
            reality_score = min(100, 50 + (solutions * 2) + (shared * 3) + (learned * 2))
        else:
            reality_score = 0

        # Store for dashboard
        dashboard_data = {
            'total_solutions': self.redis.scard('solutions:all'),
            'problems_solved': stats.get('problems_solved', 0),
            'knowledge_shared': stats.get('knowledge_shared', 0),
            'solutions_learned': stats.get('solutions_learned', 0),
            'reality_score': reality_score,
            'active_agents': len(self.agents),
            'timestamp': datetime.now().isoformat()
        }

        self.redis.set('learning:dashboard:stats',
                      json.dumps(dashboard_data), ex=60)

        print(f"\n📊 Dashboard Stats Updated: Reality Score = {reality_score}%")

    def run_simulation(self):
        """Main simulation loop"""
        print("\n" + "="*60)
        print("🚀 LIVE LEARNING SIMULATOR STARTED")
        print("="*60)
        print("\nAgents will now:")
        print("  • Solve real problems with actual code")
        print("  • Share discoveries with each other")
        print("  • Learn from shared knowledge")
        print("\nWatch the dashboard to see real learning happen!")
        print("\nPress Ctrl+C to stop\n")

        self.create_agents()

        while self.running:
            try:
                self.activity_count += 1

                # Choose random activity
                activity = random.random()

                if activity < 0.6:
                    # Most common: solve problems
                    self.simulate_problem_solving()
                elif activity < 0.9:
                    # Common: learn from others
                    self.simulate_learning_from_others()
                else:
                    # Occasional: update stats
                    self.update_dashboard_stats()

                # Update dashboard stats every 5 activities
                if self.activity_count % 5 == 0:
                    self.update_dashboard_stats()

                # Random delay for realism
                time.sleep(random.uniform(1, 3))

            except KeyboardInterrupt:
                print("\n\n👋 Stopping simulation...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Simulation error: {e}")
                time.sleep(2)

        # Final stats
        self.print_final_stats()

    def print_final_stats(self):
        """Print summary of learning activity"""
        print("\n" + "="*60)
        print("📊 LEARNING SIMULATION SUMMARY")
        print("="*60)

        stats = self.redis.hgetall('learning:stats:global')

        print(f"\n✅ Problems Solved: {stats.get('problems_solved', 0)}")
        print(f"✅ Solutions Created: {stats.get('solutions_created', 0)}")
        print(f"✅ Knowledge Shared: {stats.get('knowledge_shared', 0)}")
        print(f"✅ Solutions Learned: {stats.get('solutions_learned', 0)}")

        print(f"\n🤖 Agent Performance:")
        for agent_id, agent_data in self.agents.items():
            print(f"   {agent_id}:")
            print(f"      Problems: {agent_data['problems_solved']}")
            print(f"      Solutions: {agent_data['solutions_created']}")
            print(f"      Shared: {agent_data['knowledge_shared']}")

        # Stop learners
        for agent_data in self.agents.values():
            agent_data['learner'].stop()


if __name__ == "__main__":
    import json

    simulator = LiveLearningSimulator()
    simulator.run_simulation()