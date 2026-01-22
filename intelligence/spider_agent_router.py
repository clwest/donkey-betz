"""
Spider → Agent Data Router
==========================

Automatically routes spider-collected data to appropriate agents for processing.
This is the missing link that connects data collection to intelligence processing.
"""

import os
import redis
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List
from intelligence.problem_solver import AgentProblemSolver
from intelligence.knowledge_sharing import KnowledgeSharing

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
_REDIS_URL_DB0 = _REDIS_URL.rsplit('/', 1)[0] + '/0' if '/' in _REDIS_URL else _REDIS_URL + '/0'
_REDIS_URL_DB2 = _REDIS_URL.rsplit('/', 1)[0] + '/2' if '/' in _REDIS_URL else _REDIS_URL + '/2'


class SpiderAgentRouter:
    """
    Routes data from spiders to agents based on data type and agent capabilities
    """

    def __init__(self):
        self.redis_main = redis.Redis.from_url(_REDIS_URL_DB0, decode_responses=True)
        self.redis_learning = redis.Redis.from_url(_REDIS_URL_DB2, decode_responses=True)
        self.knowledge_sharing = KnowledgeSharing()

        # Define agent specializations
        self.agent_specializations = {
            'job_matcher': ['freelance', 'job', 'opportunity', 'position'],
            'skill_analyzer': ['skills', 'requirements', 'qualifications'],
            'salary_optimizer': ['salary', 'rate', 'budget', 'compensation'],
            'resume_builder': ['resume', 'cv', 'experience', 'portfolio'],
            'application_writer': ['apply', 'application', 'cover letter'],
            'market_analyzer': ['market', 'trends', 'demand', 'analysis'],
            'opportunity_scorer': ['score', 'rank', 'evaluate', 'priority']
        }

        # Initialize agents
        self.agents = {}
        for agent_id in self.agent_specializations.keys():
            self.agents[agent_id] = AgentProblemSolver(agent_id)

    def start_routing(self):
        """
        Start the automatic routing process
        """
        print("🚀 Starting Spider → Agent Data Router")
        print(f"   Monitoring {len(self.agent_specializations)} specialized agents")

        processed_count = 0

        while True:
            try:
                # Check for new spider data
                new_data = self.check_for_new_data()

                if new_data:
                    for data_item in new_data:
                        # Route to appropriate agents
                        self.route_to_agents(data_item)
                        processed_count += 1

                        if processed_count % 10 == 0:
                            print(f"   ✅ Processed {processed_count} items")

                # Brief pause before next check
                time.sleep(2)

            except KeyboardInterrupt:
                print("\n🛑 Stopping router...")
                break
            except Exception as e:
                print(f"   ⚠️ Router error: {e}")
                time.sleep(5)

    def check_for_new_data(self) -> List[Dict]:
        """
        Check for new data from spiders
        """
        new_data = []

        # Check freelance opportunities
        freelance_keys = self.redis_main.keys('freelance:opportunity:*')
        for key in freelance_keys:
            # Check if already processed
            if not self.redis_main.exists(f"{key}:processed"):
                data_json = self.redis_main.get(key)
                if data_json:
                    try:
                        data = json.loads(data_json)
                        data['_source'] = 'freelance'
                        data['_key'] = key
                        new_data.append(data)
                    except:
                        pass

        # Check spider data points
        spider_keys = self.redis_main.keys('spider:data:*')
        for key in spider_keys:
            if not self.redis_main.exists(f"{key}:processed"):
                data = self.redis_main.hgetall(key)
                if data:
                    data['_source'] = 'spider'
                    data['_key'] = key
                    new_data.append(data)

        return new_data

    def route_to_agents(self, data: Dict):
        """
        Route data to appropriate agents based on content
        """
        print(f"\n📨 Routing: {data.get('title', data.get('_key', 'Unknown'))[:50]}...")

        # Determine relevant agents
        relevant_agents = self.find_relevant_agents(data)

        if not relevant_agents:
            # No specific match, use general agents
            relevant_agents = ['job_matcher', 'opportunity_scorer']

        print(f"   → Sending to agents: {', '.join(relevant_agents)}")

        # Send to each relevant agent
        results = {}
        for agent_id in relevant_agents:
            result = self.process_with_agent(agent_id, data)
            results[agent_id] = result

            # Store agent processing result
            self.store_agent_result(agent_id, data, result)

        # Mark as processed
        self.redis_main.set(f"{data['_key']}:processed", "1")
        self.redis_main.expire(f"{data['_key']}:processed", 86400)  # Expire after 24 hours

        # Share findings between agents
        self.share_findings(data, results)

        return results

    def find_relevant_agents(self, data: Dict) -> List[str]:
        """
        Find agents relevant to this data
        """
        relevant = []

        # Convert data to searchable text
        search_text = json.dumps(data).lower()

        # Check each agent's specialization
        for agent_id, keywords in self.agent_specializations.items():
            for keyword in keywords:
                if keyword in search_text:
                    relevant.append(agent_id)
                    break

        return list(set(relevant))  # Remove duplicates

    def process_with_agent(self, agent_id: str, data: Dict) -> Dict:
        """
        Process data with a specific agent
        """
        agent = self.agents.get(agent_id)
        if not agent:
            return {'error': 'Agent not found'}

        # Extract key information for simpler problems
        title = data.get('title', 'Unknown opportunity')
        description = data.get('description', '')[:500]  # Limit description length
        company = data.get('company', 'Unknown')

        # Create problem based on agent specialization
        problems = {
            'job_matcher': f"Match job to skills. Title: {title}. Company: {company}",
            'skill_analyzer': f"Extract skills from job: {title}. Description: {description}",
            'salary_optimizer': f"Find salary for: {title} at {company}",
            'resume_builder': f"Key points for resume from: {title}",
            'application_writer': f"Application approach for: {title} at {company}",
            'market_analyzer': f"Market demand for: {title}",
            'opportunity_scorer': f"Score opportunity 0-100: {title} at {company}"
        }

        problem = problems.get(agent_id, f"Analyze: {title}")

        # Let agent solve the problem
        result = agent.solve_problem(problem, context={'data': data})

        # Record agent activity
        self.redis_main.hset(
            f"agent:{agent_id}:activity",
            str(time.time()),
            json.dumps({
                'processed': data.get('title', 'Unknown'),
                'success': result.get('success', False),
                'timestamp': datetime.now().isoformat()
            })
        )

        return result

    def store_agent_result(self, agent_id: str, data: Dict, result: Dict):
        """
        Store the result of agent processing
        """
        result_key = f"agent:{agent_id}:result:{hashlib.md5(json.dumps(data).encode()).hexdigest()}"

        self.redis_learning.hset(result_key, mapping={
            'agent_id': agent_id,
            'data_source': data.get('_source', 'unknown'),
            'data_key': data.get('_key', ''),
            'title': data.get('title', 'Unknown'),
            'success': str(result.get('success', False)),
            'result': json.dumps(result.get('result', {})),
            'execution_time': str(result.get('execution_time', 0)),
            'timestamp': datetime.now().isoformat()
        })

        # Update agent stats
        if result.get('success'):
            self.redis_learning.hincrby(f"agent:{agent_id}:stats", 'processed_success', 1)
        else:
            self.redis_learning.hincrby(f"agent:{agent_id}:stats", 'processed_failed', 1)

    def share_findings(self, data: Dict, results: Dict):
        """
        Share findings between agents for collaborative learning
        """
        # Extract key findings from all agent results
        findings = {}

        for agent_id, result in results.items():
            if result.get('success') and result.get('result'):
                findings[agent_id] = result.get('result')

        if findings:
            # Create a collaborative knowledge entry
            knowledge_key = f"collaborative:{hashlib.md5(json.dumps(data).encode()).hexdigest()}"

            self.redis_learning.hset(knowledge_key, mapping={
                'source_data': data.get('title', 'Unknown'),
                'findings': json.dumps(findings),
                'agents_involved': ','.join(results.keys()),
                'timestamp': datetime.now().isoformat()
            })

            # Broadcast to knowledge sharing system
            self.knowledge_sharing.share_discovery(
                agent_id='router',
                problem=f"Process opportunity: {data.get('title', 'Unknown')}",
                solution=json.dumps(findings),
                performance={'agents': len(results), 'success_rate': sum(1 for r in results.values() if r.get('success')) / len(results)}
            )


class OpportunityDispatcher:
    """
    Dispatches processed opportunities to action systems
    """

    def __init__(self):
        self.redis_main = redis.Redis.from_url(_REDIS_URL_DB0, decode_responses=True)
        self.redis_learning = redis.Redis.from_url(_REDIS_URL_DB2, decode_responses=True)

    def dispatch_opportunity(self, opportunity: Dict, agent_results: Dict):
        """
        Dispatch opportunity based on agent analysis
        """
        # Calculate opportunity score
        scores = []
        for agent_id, result in agent_results.items():
            if agent_id == 'opportunity_scorer' and result.get('success'):
                try:
                    score = float(result.get('result', 0))
                    scores.append(score)
                except:
                    pass

        avg_score = sum(scores) / len(scores) if scores else 50

        print(f"\n🎯 Opportunity Score: {avg_score:.1f}/100")

        # Dispatch based on score
        if avg_score >= 80:
            print("   ⭐ HIGH PRIORITY - Dispatching for immediate action")
            self.dispatch_high_priority(opportunity, agent_results)
        elif avg_score >= 60:
            print("   ✅ GOOD MATCH - Adding to opportunity queue")
            self.add_to_queue(opportunity, agent_results, priority='medium')
        elif avg_score >= 40:
            print("   📋 POTENTIAL - Storing for later review")
            self.add_to_queue(opportunity, agent_results, priority='low')
        else:
            print("   ❌ LOW MATCH - Skipping")

    def dispatch_high_priority(self, opportunity: Dict, agent_results: Dict):
        """
        Dispatch high-priority opportunity for immediate action
        """
        action_key = f"action:opportunity:{hashlib.md5(json.dumps(opportunity).encode()).hexdigest()}"

        self.redis_main.hset(action_key, mapping={
            'opportunity': json.dumps(opportunity),
            'agent_results': json.dumps(agent_results),
            'priority': 'high',
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        })

        # Add to high-priority queue
        self.redis_main.lpush('queue:opportunities:high', action_key)

        # Trigger notification (could connect to notification system)
        print(f"   💬 Ready for action: {opportunity.get('title', 'Unknown')}")

    def add_to_queue(self, opportunity: Dict, agent_results: Dict, priority: str):
        """
        Add opportunity to processing queue
        """
        queue_key = f"queue:opportunity:{priority}:{hashlib.md5(json.dumps(opportunity).encode()).hexdigest()}"

        self.redis_main.hset(queue_key, mapping={
            'opportunity': json.dumps(opportunity),
            'agent_results': json.dumps(agent_results),
            'priority': priority,
            'status': 'queued',
            'created_at': datetime.now().isoformat()
        })

        # Add to appropriate queue
        self.redis_main.lpush(f'queue:opportunities:{priority}', queue_key)


def start_spider_agent_pipeline():
    """
    Start the complete spider → agent pipeline
    """
    print("="*60)
    print("STARTING SPIDER → AGENT PIPELINE")
    print("="*60)

    router = SpiderAgentRouter()
    router.start_routing()


if __name__ == "__main__":
    start_spider_agent_pipeline()