"""
Knowledge Sharing System
========================

Real-time sharing of discoveries between agents.
When one agent solves a problem, ALL agents learn from it.
"""

import redis
import json
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional


class KnowledgeSharing:
    """
    Manages discovery broadcasting and knowledge sharing between agents
    """

    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True
        )
        self.pubsub = self.redis.pubsub()

    def share_discovery(self, agent_id: str, problem: str, solution: str, performance: Dict):
        """
        Broadcast new discovery to all agents

        This is called when an agent creates a NEW solution
        """
        discovery = {
            'agent_id': agent_id,
            'problem': problem,
            'solution': solution,
            'performance': performance,
            'timestamp': datetime.now().isoformat()
        }

        # Publish to discoveries channel
        self.redis.publish('discoveries', json.dumps(discovery))

        # Store in shared knowledge base
        knowledge_key = f"shared:knowledge:{hashlib.md5(problem.encode()).hexdigest()}"
        self.redis.hset(knowledge_key, mapping={
            'problem': problem,
            'solution': solution,
            'discovered_by': agent_id,
            'performance': json.dumps(performance),
            'access_count': 0,
            'timestamp': discovery['timestamp']
        })

        # Update agent's contribution score
        self.redis.hincrby(f"agent:contributions:{agent_id}", 'discoveries', 1)

        # Track in discovery feed
        feed_entry = f"{datetime.now().isoformat()}|{agent_id}|{problem[:50]}"
        self.redis.lpush("discoveries:feed", feed_entry)
        self.redis.ltrim("discoveries:feed", 0, 99)  # Keep last 100

        print(f"   📡 Broadcasting discovery to all agents")

    def learn_from_others(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """
        Agent learns from other agents' discoveries
        """
        # Get recent shared knowledge
        knowledge_keys = self.redis.keys("shared:knowledge:*")

        learned = []
        for key in knowledge_keys[-limit:]:
            knowledge = self.redis.hgetall(key)

            if knowledge and knowledge.get('discovered_by') != agent_id:
                # Increment access count
                self.redis.hincrby(key, 'access_count', 1)

                # Add to agent's learned knowledge
                self.redis.sadd(f"agent:learned:{agent_id}", key)

                # Track learning event
                self.redis.hincrby(f"agent:stats:{agent_id}", 'solutions_learned', 1)

                learned.append({
                    'problem': knowledge.get('problem'),
                    'solution': knowledge.get('solution'),
                    'from_agent': knowledge.get('discovered_by'),
                    'performance': json.loads(knowledge.get('performance', '{}'))
                })

        if learned:
            print(f"   📚 Agent {agent_id} learned {len(learned)} solutions from others")

        return learned

    def get_collaboration_stats(self) -> Dict:
        """Get statistics on knowledge sharing"""
        stats = {
            'total_discoveries': self.redis.llen("discoveries:feed"),
            'shared_knowledge_items': len(self.redis.keys("shared:knowledge:*")),
            'top_contributors': [],
            'most_accessed': []
        }

        # Get top contributors
        contributor_keys = self.redis.keys("agent:contributions:*")
        for key in contributor_keys:
            agent_id = key.split(':')[-1]
            discoveries = self.redis.hget(key, 'discoveries')
            if discoveries:
                stats['top_contributors'].append({
                    'agent': agent_id,
                    'discoveries': int(discoveries)
                })

        stats['top_contributors'].sort(key=lambda x: x['discoveries'], reverse=True)

        # Get most accessed knowledge
        knowledge_keys = self.redis.keys("shared:knowledge:*")
        for key in knowledge_keys[:10]:
            access_count = self.redis.hget(key, 'access_count')
            problem = self.redis.hget(key, 'problem')
            if access_count and int(access_count) > 0:
                stats['most_accessed'].append({
                    'problem': problem[:50],
                    'accesses': int(access_count)
                })

        stats['most_accessed'].sort(key=lambda x: x['accesses'], reverse=True)

        return stats


class LearningAgent:
    """
    An agent that actively learns from others' discoveries
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.knowledge_sharing = KnowledgeSharing()
        self.learned_solutions = {}
        self.redis = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
        self.learning_thread = None
        self.stop_learning = False

    def start_learning(self):
        """Subscribe to discoveries and learn in real-time"""

        def discovery_handler():
            """Handle incoming discoveries"""
            pubsub = self.redis.pubsub()
            pubsub.subscribe('discoveries')

            for message in pubsub.listen():
                if self.stop_learning:
                    break

                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])

                        # Don't learn from self
                        if data['agent_id'] != self.agent_id:
                            print(f"   🧠 Agent {self.agent_id} learning from {data['agent_id']}")

                            # Store learned solution
                            problem_hash = hashlib.md5(data['problem'].encode()).hexdigest()[:8]
                            self.learned_solutions[problem_hash] = {
                                'problem': data['problem'],
                                'solution': data['solution'],
                                'from_agent': data['agent_id'],
                                'performance': data['performance'],
                                'learned_at': datetime.now().isoformat()
                            }

                            # Test if it works for us
                            self.test_learned_solution(data['solution'], data['problem'])

                            # Update learning stats
                            self.redis.hincrby(f"agent:stats:{self.agent_id}", 'realtime_learns', 1)

                    except Exception as e:
                        print(f"   ❌ Learning error: {e}")

        # Start learning in background thread
        self.learning_thread = threading.Thread(target=discovery_handler, daemon=True)
        self.learning_thread.start()

        print(f"   🎓 Agent {self.agent_id} started real-time learning")
        return self.learning_thread

    def test_learned_solution(self, solution_code: str, problem: str):
        """Test if learned solution works for this agent"""
        try:
            # Simple test execution
            exec_globals = {}
            exec(solution_code, exec_globals)

            if 'solution' in exec_globals:
                # Solution learned successfully
                self.redis.hincrby(f"agent:stats:{self.agent_id}", 'solutions_tested', 1)
                return True
        except Exception as e:
            # Solution didn't work for this agent
            self.redis.hincrby(f"agent:stats:{self.agent_id}", 'solutions_failed', 1)
            return False

    def stop(self):
        """Stop learning"""
        self.stop_learning = True
        if self.learning_thread:
            self.learning_thread.join(timeout=1)

    def apply_learned_solution(self, problem: str) -> Optional[str]:
        """Check if we've learned a solution for this problem"""
        problem_hash = hashlib.md5(problem.encode()).hexdigest()[:8]

        if problem_hash in self.learned_solutions:
            learned = self.learned_solutions[problem_hash]
            print(f"   💡 Using solution learned from {learned['from_agent']}")
            return learned['solution']

        # Check similar problems
        for stored_hash, learned in self.learned_solutions.items():
            if self._is_similar(problem, learned['problem']):
                print(f"   💡 Using similar solution from {learned['from_agent']}")
                return learned['solution']

        return None

    def _is_similar(self, problem1: str, problem2: str) -> bool:
        """Check if two problems are similar"""
        words1 = set(problem1.lower().split())
        words2 = set(problem2.lower().split())

        if not words1 or not words2:
            return False

        similarity = len(words1.intersection(words2)) / len(words1.union(words2))
        return similarity > 0.6


# Test knowledge sharing
if __name__ == "__main__":
    print("🧪 Testing Knowledge Sharing System\n")

    # Create agents
    agent1 = LearningAgent("solver_001")
    agent2 = LearningAgent("learner_001")

    # Start learning
    agent1.start_learning()
    agent2.start_learning()

    # Agent 1 shares a discovery
    sharing = KnowledgeSharing()
    sharing.share_discovery(
        agent_id="solver_001",
        problem="Extract URLs from text",
        solution='''
import re
def solution(text):
    pattern = r'https?://[^\\s<>"{}|\\\\^`\\[\\]]+'
    return re.findall(pattern, text)
''',
        performance={'execution_time': 0.001, 'accuracy': 0.95}
    )

    # Wait for propagation
    import time
    time.sleep(1)

    # Check if agent2 learned it
    learned_solution = agent2.apply_learned_solution("Extract URLs from text")
    if learned_solution:
        print(f"\n✅ Agent2 successfully learned from Agent1!")
        print(f"Learned solution:\n{learned_solution}")

    # Get stats
    stats = sharing.get_collaboration_stats()
    print(f"\n📊 Collaboration Stats: {json.dumps(stats, indent=2)}")

    # Clean up
    agent1.stop()
    agent2.stop()