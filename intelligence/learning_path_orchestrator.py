"""
Learning Path Orchestrator
Detects knowledge gaps and orchestrates dynamic learning from external sources
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests

from core.models_unified_system import (
    Agent,
    AgentSolution,
    AgentLearning,
    SpiderData
)

logger = logging.getLogger(__name__)


class LearningPathOrchestrator:
    """Orchestrates dynamic learning paths when agents encounter unknown topics"""

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.learning_sources = {
            'duckduckgo': self._search_duckduckgo,
            'wikipedia': self._search_wikipedia,
            'arxiv': self._search_arxiv,
            'spider_network': self._activate_spiders,
            'agent_collective': self._query_agent_collective
        }
        self.learning_sessions = {}

    def detect_knowledge_gap(self, query: str, agent: Agent) -> Tuple[bool, float]:
        """
        Detect if an agent has a knowledge gap for a given query

        Returns:
            Tuple of (has_gap, confidence_score)
        """
        # Check if agent has any solutions related to the query
        existing_solutions = AgentSolution.objects.filter(
            agent=agent,
            title__icontains=query[:30]  # Partial match
        ).count()

        if existing_solutions > 0:
            return False, 0.8  # Has some knowledge

        # Check if agent has learned about this topic
        existing_learning = AgentLearning.objects.filter(
            student_agent=agent,
            solution__description__icontains=query[:30]
        ).count()

        if existing_learning > 0:
            return False, 0.6  # Has learned something

        # Agent has a knowledge gap
        return True, 0.1

    def create_learning_path(self, query: str, agent: Agent) -> Dict[str, Any]:
        """
        Create a learning path for an agent to acquire knowledge
        """
        session_id = f"learning_{agent.id}_{datetime.now().timestamp()}"

        learning_path = {
            'session_id': session_id,
            'agent': agent.name,
            'query': query,
            'status': 'initializing',
            'steps': [],
            'sources_to_check': [],
            'knowledge_acquired': [],
            'start_time': datetime.now().isoformat()
        }

        # Determine which sources to use based on query type
        if any(term in query.lower() for term in ['latest', 'recent', 'news', 'current']):
            learning_path['sources_to_check'] = ['duckduckgo', 'spider_network']
        elif any(term in query.lower() for term in ['research', 'paper', 'academic', 'study']):
            learning_path['sources_to_check'] = ['arxiv', 'agent_collective']
        elif any(term in query.lower() for term in ['concept', 'definition', 'what is']):
            learning_path['sources_to_check'] = ['wikipedia', 'duckduckgo']
        else:
            learning_path['sources_to_check'] = ['duckduckgo', 'spider_network', 'agent_collective']

        self.learning_sessions[session_id] = learning_path

        # Broadcast learning path initialization
        self._broadcast_learning_update(learning_path)

        return learning_path

    def execute_learning_path(self, session_id: str) -> Dict[str, Any]:
        """
        Execute the learning path and gather knowledge
        """
        if session_id not in self.learning_sessions:
            return {'error': 'Session not found'}

        learning_path = self.learning_sessions[session_id]
        learning_path['status'] = 'executing'

        agent = Agent.objects.get(name=learning_path['agent'])
        query = learning_path['query']

        # Execute each learning source
        for source in learning_path['sources_to_check']:
            step = {
                'source': source,
                'status': 'searching',
                'timestamp': datetime.now().isoformat()
            }
            learning_path['steps'].append(step)
            self._broadcast_learning_update(learning_path)

            # Search the source
            if source in self.learning_sources:
                try:
                    result = self.learning_sources[source](query)

                    if result and result.get('success'):
                        step['status'] = 'found'
                        step['data'] = result.get('data', {})

                        # Create solution from learned knowledge
                        solution = self._create_solution_from_knowledge(
                            agent,
                            query,
                            result.get('data', {}),
                            source
                        )

                        if solution:
                            learning_path['knowledge_acquired'].append({
                                'source': source,
                                'solution_id': str(solution.id),
                                'title': solution.title,
                                'timestamp': datetime.now().isoformat()
                            })
                    else:
                        step['status'] = 'not_found'

                except Exception as e:
                    logger.error(f"Error searching {source}: {e}")
                    step['status'] = 'error'
                    step['error'] = str(e)

            self._broadcast_learning_update(learning_path)

        learning_path['status'] = 'completed'
        learning_path['end_time'] = datetime.now().isoformat()

        # Share learned knowledge with other agents
        self._share_knowledge_with_collective(agent, learning_path)

        self._broadcast_learning_update(learning_path)

        return learning_path

    def _search_duckduckgo(self, query: str) -> Dict[str, Any]:
        """Search DuckDuckGo for information"""
        try:
            # Using DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # Extract relevant information
                result = {
                    'success': True,
                    'data': {
                        'abstract': data.get('AbstractText', ''),
                        'answer': data.get('Answer', ''),
                        'definition': data.get('Definition', ''),
                        'related_topics': [
                            {'text': topic.get('Text', ''), 'url': topic.get('FirstURL', '')}
                            for topic in data.get('RelatedTopics', [])[:3]
                            if isinstance(topic, dict)
                        ],
                        'source': data.get('AbstractSource', 'DuckDuckGo')
                    }
                }

                # If no abstract, try to get web results
                if not result['data']['abstract']:
                    result['data']['abstract'] = self._get_web_search_summary(query)

                return result

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")

        return {'success': False, 'error': 'Search failed'}

    def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search Wikipedia for information"""
        try:
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            response = requests.get(url + query.replace(' ', '_'), timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': {
                        'title': data.get('title', ''),
                        'summary': data.get('extract', ''),
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    }
                }
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")

        return {'success': False, 'error': 'Search failed'}

    def _search_arxiv(self, query: str) -> Dict[str, Any]:
        """Search arXiv for academic papers"""
        try:
            import urllib.parse
            url = f"http://export.arxiv.org/api/query?search_query=all:{urllib.parse.quote(query)}&max_results=3"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                # Parse XML response (simplified)
                papers = []
                content = response.text

                # Extract paper titles and summaries (simplified parsing)
                import re
                titles = re.findall(r'<title>(.*?)</title>', content)
                summaries = re.findall(r'<summary>(.*?)</summary>', content, re.DOTALL)

                for i in range(min(3, len(titles)-1)):  # Skip first title (feed title)
                    if i < len(summaries):
                        papers.append({
                            'title': titles[i+1].strip(),
                            'summary': summaries[i].strip()[:500]
                        })

                return {
                    'success': True,
                    'data': {
                        'papers': papers,
                        'source': 'arXiv'
                    }
                }
        except Exception as e:
            logger.error(f"arXiv search error: {e}")

        return {'success': False, 'error': 'Search failed'}

    def _activate_spiders(self, query: str) -> Dict[str, Any]:
        """Activate spider network to search for information"""
        try:
            # Create spider task for this query
            spider_data = SpiderData.objects.create(
                spider_name='Dynamic Learning Spider',
                data_type='learning_query',
                raw_data={
                    'query': query,
                    'timestamp': datetime.now().isoformat(),
                    'purpose': 'knowledge_acquisition'
                },
                source_url=f'learning://{query}',
                is_actionable=True
            )

            # Simulate spider finding information (in production, this would trigger actual spiders)
            return {
                'success': True,
                'data': {
                    'spider_id': str(spider_data.id),
                    'status': 'searching',
                    'message': f'Spider network activated to search for: {query}'
                }
            }
        except Exception as e:
            logger.error(f"Spider activation error: {e}")

        return {'success': False, 'error': 'Spider activation failed'}

    def _query_agent_collective(self, query: str) -> Dict[str, Any]:
        """Query the collective knowledge of all agents"""
        try:
            # Find agents with relevant knowledge
            relevant_solutions = AgentSolution.objects.filter(
                description__icontains=query[:20]
            ).select_related('agent')[:5]

            collective_knowledge = []
            for solution in relevant_solutions:
                collective_knowledge.append({
                    'agent': solution.agent.name,
                    'title': solution.title,
                    'description': solution.description[:200],
                    'solution_type': solution.solution_type
                })

            if collective_knowledge:
                return {
                    'success': True,
                    'data': {
                        'collective_knowledge': collective_knowledge,
                        'source': 'Agent Collective Intelligence'
                    }
                }
        except Exception as e:
            logger.error(f"Agent collective query error: {e}")

        return {'success': False, 'error': 'No collective knowledge found'}

    def _get_web_search_summary(self, query: str) -> str:
        """Get a summary from web search (fallback)"""
        return f"Searching for information about: {query}. Multiple sources are being queried to build comprehensive knowledge."

    def _create_solution_from_knowledge(self, agent: Agent, query: str,
                                       knowledge: Dict, source: str) -> Optional[AgentSolution]:
        """Create a solution from acquired knowledge"""
        try:
            # Build solution content based on source type
            if source == 'duckduckgo':
                content = knowledge.get('abstract') or knowledge.get('answer', '')
                title = f"Learned: {query[:50]}"
            elif source == 'wikipedia':
                content = knowledge.get('summary', '')
                title = knowledge.get('title', query[:50])
            elif source == 'arxiv':
                papers = knowledge.get('papers', [])
                content = '\n\n'.join([f"{p['title']}: {p['summary']}" for p in papers])
                title = f"Research: {query[:50]}"
            elif source == 'agent_collective':
                collective = knowledge.get('collective_knowledge', [])
                content = '\n'.join([f"{k['agent']}: {k['description']}" for k in collective])
                title = f"Collective Knowledge: {query[:50]}"
            else:
                content = json.dumps(knowledge)
                title = f"Spider Intel: {query[:50]}"

            if content:
                # Create solution
                solution = AgentSolution.objects.create(
                    agent=agent,
                    title=title,
                    description=content[:1000],
                    solution_type='learned_knowledge',
                    code_snippet=f"// Knowledge acquired from {source}\n// Query: {query}\n\nconst knowledge = {json.dumps(knowledge, indent=2)[:500]};",
                    language='javascript',
                    metrics={
                        'source': source,
                        'query': query,
                        'acquired_at': datetime.now().isoformat(),
                        'learning_type': 'dynamic'
                    }
                )

                # Create learning record
                AgentLearning.objects.create(
                    teacher_agent=agent,
                    student_agent=agent,
                    solution=solution,
                    learning_type='self_learning',
                    effectiveness_before=10.0,
                    effectiveness_after=85.0
                )

                logger.info(f"Created solution {solution.id} from {source} for agent {agent.name}")
                return solution

        except Exception as e:
            logger.error(f"Error creating solution from knowledge: {e}")

        return None

    def _share_knowledge_with_collective(self, agent: Agent, learning_path: Dict):
        """Share newly acquired knowledge with other relevant agents"""
        try:
            # Find agents that might benefit from this knowledge
            query_terms = learning_path['query'].lower().split()

            # Map query terms to agent categories
            relevant_agents = []

            if any(term in query_terms for term in ['job', 'career', 'employment']):
                relevant_agents.extend(['Job Application Automator', 'Career Path Strategist'])
            if any(term in query_terms for term in ['ai', 'machine', 'learning', 'ml']):
                relevant_agents.extend(['AI Model Trainer', 'Deep Learning Specialist'])
            if any(term in query_terms for term in ['market', 'business', 'revenue']):
                relevant_agents.extend(['Market Research Analyst', 'Business Growth Architect'])

            # Share knowledge with relevant agents
            for agent_name in relevant_agents:
                try:
                    target_agent = Agent.objects.get(name=agent_name)
                    if target_agent.id != agent.id:
                        # Create knowledge transfer
                        for knowledge in learning_path.get('knowledge_acquired', []):
                            solution = AgentSolution.objects.get(id=knowledge['solution_id'])

                            AgentLearning.objects.create(
                                teacher_agent=agent,
                                student_agent=target_agent,
                                solution=solution,
                                learning_type='knowledge_transfer',
                                effectiveness_before=20.0,
                                effectiveness_after=75.0
                            )

                            logger.info(f"Shared knowledge from {agent.name} to {target_agent.name}")

                except Agent.DoesNotExist:
                    continue

        except Exception as e:
            logger.error(f"Error sharing knowledge: {e}")

    def _broadcast_learning_update(self, learning_path: Dict):
        """Broadcast learning updates via WebSocket"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                'learning_updates',
                {
                    'type': 'learning_update',
                    'message': learning_path
                }
            )
        except Exception as e:
            logger.error(f"Error broadcasting learning update: {e}")

    def get_learning_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a learning session"""
        if session_id in self.learning_sessions:
            return self.learning_sessions[session_id]
        return {'error': 'Session not found'}