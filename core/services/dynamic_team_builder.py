"""
Dynamic Team Builder Service
============================

Session 744: Replaces hardcoded coordinator teams with dynamic team formation.

Instead of coordinators having fixed sub-agents:
  - StockAuditCoordinator → [4 hardcoded agents]
  - BlockchainCoordinator → [4 hardcoded agents]

We now form teams DYNAMICALLY based on task requirements:
  - Task: "Analyze NVDA and check crypto movements"
  - Team: [StockAnalyst, WhaleWatcher, ResearchAgent, TrendAnalysis]

This enables:
  - Cross-domain collaboration by default
  - New agents automatically available
  - No coordinator silos
  - Full 72-agent ecosystem access
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TeamMember:
    """A member of a dynamically formed team."""
    agent_name: str
    relevance_score: float
    category: str
    role: str  # 'primary', 'supporting', 'specialist'
    synergy_bonus: float = 1.0


@dataclass
class DynamicTeam:
    """A dynamically formed team of agents."""
    task: str
    members: List[TeamMember]
    total_synergy: float
    formation_reason: str

    def get_agent_names(self) -> List[str]:
        return [m.agent_name for m in self.members]

    def get_primary_agents(self) -> List[str]:
        return [m.agent_name for m in self.members if m.role == 'primary']


class DynamicTeamBuilder:
    """
    Builds optimal agent teams dynamically based on task requirements.

    Replaces the hardcoded coordinator model with intelligent team formation.
    """

    # Minimum relevance score to be considered for team
    RELEVANCE_THRESHOLD = 0.3

    # Maximum team size (to prevent runaway costs)
    MAX_TEAM_SIZE = 8

    # Minimum team size
    MIN_TEAM_SIZE = 1

    def __init__(self):
        self._routing_config = None
        self._synergy_map = None
        self._embeddings_cache = {}
        self._openai_client = None
        self._agent_router = None

    # ==================== Lazy-Loaded Dependencies ====================

    @property
    def routing_config(self) -> Dict[str, Any]:
        """Lazy-load agent routing configuration."""
        if self._routing_config is None:
            from core.agents.routing_config import AGENT_ROUTING_CONFIG
            self._routing_config = AGENT_ROUTING_CONFIG
        return self._routing_config

    @property
    def synergy_map(self) -> Dict[Tuple[str, str], float]:
        """Lazy-load agent synergy mappings."""
        if self._synergy_map is None:
            from core.agents.synergy import AGENT_SYNERGY
            self._synergy_map = AGENT_SYNERGY
        return self._synergy_map

    @property
    def openai_client(self):
        """Lazy-load OpenAI client for embeddings."""
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI()
        return self._openai_client

    @property
    def agent_router(self):
        """Lazy-load agent router for execution."""
        if self._agent_router is None:
            from core.agent_router import get_agent_router
            self._agent_router = get_agent_router()
        return self._agent_router

    # ==================== Task Analysis ====================

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text, with caching."""
        cache_key = text[:100]  # Use first 100 chars as key

        if cache_key in self._embeddings_cache:
            return self._embeddings_cache[cache_key]

        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            embedding = response.data[0].embedding
            self._embeddings_cache[cache_key] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def _extract_task_keywords(self, task: str) -> List[str]:
        """Extract important keywords from task for matching."""
        # Common words to ignore
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'need', 'want',
            'i', 'me', 'my', 'we', 'our', 'you', 'your', 'it', 'its', 'this',
            'that', 'these', 'those', 'what', 'which', 'who', 'how', 'when',
            'where', 'why', 'please', 'help', 'create', 'make', 'build', 'get'
        }

        # Extract words
        words = task.lower().split()
        keywords = [w.strip('.,!?()[]{}') for w in words if w.lower() not in stop_words]

        return keywords

    # ==================== Agent Matching ====================

    def _score_agent_for_task(
        self,
        agent_name: str,
        agent_config: Dict[str, Any],
        task: str,
        task_embedding: List[float],
        task_keywords: List[str]
    ) -> float:
        """
        Score how relevant an agent is for a given task.

        Uses multiple signals:
        1. Semantic similarity (embeddings)
        2. Keyword matching
        3. Example matching
        """
        score = 0.0

        # 1. Semantic similarity with description
        description = agent_config.get('description', '')
        if description and task_embedding:
            desc_embedding = self._get_embedding(description)
            semantic_score = self._cosine_similarity(task_embedding, desc_embedding)
            score += semantic_score * 0.4  # 40% weight

        # 2. Keyword matching
        agent_keywords = agent_config.get('keywords', [])
        task_lower = task.lower()
        keyword_matches = sum(1 for kw in agent_keywords if kw.lower() in task_lower)
        if agent_keywords:
            keyword_score = min(keyword_matches / 3, 1.0)  # Cap at 3 matches
            score += keyword_score * 0.35  # 35% weight

        # 3. Task keyword matching against description
        if task_keywords and description:
            desc_lower = description.lower()
            task_kw_matches = sum(1 for kw in task_keywords if kw in desc_lower)
            if task_keywords:
                task_kw_score = min(task_kw_matches / 3, 1.0)
                score += task_kw_score * 0.15  # 15% weight

        # 4. Example similarity (check if task is similar to examples)
        examples = agent_config.get('examples', [])
        if examples and task_embedding:
            example_scores = []
            for example in examples[:3]:  # Check top 3 examples
                ex_embedding = self._get_embedding(example)
                ex_score = self._cosine_similarity(task_embedding, ex_embedding)
                example_scores.append(ex_score)
            if example_scores:
                best_example_score = max(example_scores)
                score += best_example_score * 0.1  # 10% weight

        return score

    def _find_relevant_agents(
        self,
        task: str,
        max_agents: int = None
    ) -> List[Tuple[str, float, str]]:
        """
        Find all agents relevant to a task.

        Returns:
            List of (agent_name, relevance_score, category) tuples
        """
        max_agents = max_agents or self.MAX_TEAM_SIZE

        # Get task analysis
        task_embedding = self._get_embedding(task)
        task_keywords = self._extract_task_keywords(task)

        # Score all agents
        agent_scores = []
        for agent_name, config in self.routing_config.items():
            score = self._score_agent_for_task(
                agent_name, config, task, task_embedding, task_keywords
            )
            category = config.get('category', 'other')

            if score >= self.RELEVANCE_THRESHOLD:
                agent_scores.append((agent_name, score, category))

        # Sort by score descending
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top agents
        return agent_scores[:max_agents]

    # ==================== Synergy Optimization ====================

    def _get_synergy_bonus(self, agent1: str, agent2: str) -> float:
        """Get synergy bonus between two agents."""
        pair = (agent1, agent2)
        reverse_pair = (agent2, agent1)

        if pair in self.synergy_map:
            return self.synergy_map[pair]
        elif reverse_pair in self.synergy_map:
            return self.synergy_map[reverse_pair]

        return 1.0  # Neutral synergy

    def _calculate_team_synergy(self, agents: List[str]) -> float:
        """Calculate total synergy score for a team."""
        if len(agents) <= 1:
            return 1.0

        total_synergy = 0.0
        pair_count = 0

        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                synergy = self._get_synergy_bonus(agent1, agent2)
                total_synergy += synergy
                pair_count += 1

        if pair_count == 0:
            return 1.0

        return total_synergy / pair_count

    def _optimize_team_with_synergy(
        self,
        candidates: List[Tuple[str, float, str]],
        min_size: int = 2,
        max_size: int = 6
    ) -> List[TeamMember]:
        """
        Optimize team composition considering both relevance and synergy.
        """
        if not candidates:
            return []

        # Start with top candidate as primary
        team = []
        selected_agents = set()

        # Add primary agents (top 2-3 by relevance)
        primary_count = min(3, len(candidates))
        for i in range(primary_count):
            agent_name, score, category = candidates[i]
            team.append(TeamMember(
                agent_name=agent_name,
                relevance_score=score,
                category=category,
                role='primary' if i == 0 else 'supporting',
                synergy_bonus=1.0
            ))
            selected_agents.add(agent_name)

        # Add specialists that have good synergy with primaries
        for agent_name, score, category in candidates[primary_count:]:
            if agent_name in selected_agents:
                continue

            if len(team) >= max_size:
                break

            # Calculate synergy with existing team
            synergy_scores = []
            for member in team:
                synergy = self._get_synergy_bonus(agent_name, member.agent_name)
                synergy_scores.append(synergy)

            avg_synergy = sum(synergy_scores) / len(synergy_scores) if synergy_scores else 1.0

            # Add if score * synergy is high enough
            combined_score = score * avg_synergy
            if combined_score >= self.RELEVANCE_THRESHOLD or avg_synergy > 1.1:
                team.append(TeamMember(
                    agent_name=agent_name,
                    relevance_score=score,
                    category=category,
                    role='specialist',
                    synergy_bonus=avg_synergy
                ))
                selected_agents.add(agent_name)

        return team

    # ==================== Team Building ====================

    def build_team(
        self,
        task: str,
        min_size: int = 1,
        max_size: int = 6,
        required_agents: List[str] = None
    ) -> DynamicTeam:
        """
        Build an optimal team for a task.

        Args:
            task: The task description
            min_size: Minimum team size
            max_size: Maximum team size
            required_agents: Agents that MUST be included

        Returns:
            DynamicTeam with optimal composition
        """
        logger.info(f"Building dynamic team for task: {task[:100]}...")

        # Find relevant agents
        candidates = self._find_relevant_agents(task, max_agents=max_size * 2)

        if not candidates:
            logger.warning("No relevant agents found for task")
            # Fall back to ResearchAgent
            return DynamicTeam(
                task=task,
                members=[TeamMember(
                    agent_name='ResearchAgent',
                    relevance_score=0.5,
                    category='research',
                    role='primary'
                )],
                total_synergy=1.0,
                formation_reason="Fallback: No specific agents matched"
            )

        # Optimize team with synergy
        team_members = self._optimize_team_with_synergy(
            candidates,
            min_size=min_size,
            max_size=max_size
        )

        # Add required agents if specified
        if required_agents:
            existing_names = {m.agent_name for m in team_members}
            for agent_name in required_agents:
                if agent_name not in existing_names:
                    config = self.routing_config.get(agent_name, {})
                    team_members.append(TeamMember(
                        agent_name=agent_name,
                        relevance_score=0.5,
                        category=config.get('category', 'other'),
                        role='required'
                    ))

        # Calculate total synergy
        agent_names = [m.agent_name for m in team_members]
        total_synergy = self._calculate_team_synergy(agent_names)

        # Generate formation reason
        primary = [m.agent_name for m in team_members if m.role == 'primary']
        supporting = [m.agent_name for m in team_members if m.role in ('supporting', 'specialist')]

        reason = f"Primary: {', '.join(primary)}"
        if supporting:
            reason += f" | Supporting: {', '.join(supporting)}"
        reason += f" | Synergy: {total_synergy:.2f}"

        logger.info(f"Formed team of {len(team_members)} agents: {agent_names}")

        return DynamicTeam(
            task=task,
            members=team_members,
            total_synergy=total_synergy,
            formation_reason=reason
        )

    # ==================== Team Execution ====================

    def execute_with_team(
        self,
        task: str,
        team: DynamicTeam = None,
        parallel: bool = False,
        aggregate_results: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a task using a dynamically formed team.

        Args:
            task: The task to execute
            team: Pre-built team (or None to build one)
            parallel: Whether to run agents in parallel (future)
            aggregate_results: Whether to aggregate results

        Returns:
            Dict with results from each agent and aggregated summary
        """
        # Build team if not provided
        if team is None:
            team = self.build_team(task)

        logger.info(f"Executing with team: {team.get_agent_names()}")

        results = {
            'task': task,
            'team': team.get_agent_names(),
            'team_synergy': team.total_synergy,
            'formation_reason': team.formation_reason,
            'agent_results': {},
            'success': True,
            'errors': []
        }

        # Execute each agent
        for member in team.members:
            agent_name = member.agent_name

            try:
                logger.info(f"Running {agent_name} (role: {member.role})...")

                # Route to agent
                agent_result = self.agent_router.route(
                    agent_name,
                    task,
                    context={
                        'team_context': {
                            'team_members': team.get_agent_names(),
                            'member_role': member.role,
                            'synergy_bonus': member.synergy_bonus
                        }
                    }
                )

                # Store result
                if hasattr(agent_result, 'to_dict'):
                    result_dict = agent_result.to_dict()
                elif isinstance(agent_result, dict):
                    result_dict = agent_result
                else:
                    result_dict = {
                        'success': getattr(agent_result, 'success', True),
                        'message': getattr(agent_result, 'message', str(agent_result)),
                        'data': getattr(agent_result, 'data', {})
                    }

                results['agent_results'][agent_name] = {
                    'role': member.role,
                    'relevance_score': member.relevance_score,
                    'synergy_bonus': member.synergy_bonus,
                    'result': result_dict
                }

            except Exception as e:
                logger.error(f"Error executing {agent_name}: {e}")
                results['errors'].append({
                    'agent': agent_name,
                    'error': str(e)
                })
                results['agent_results'][agent_name] = {
                    'role': member.role,
                    'error': str(e)
                }

        # Aggregate results if requested
        if aggregate_results:
            results['summary'] = self._aggregate_results(results['agent_results'])

        # Set overall success
        results['success'] = len(results['errors']) == 0

        return results

    def _aggregate_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from multiple agents into a summary."""
        summary = {
            'agents_succeeded': 0,
            'agents_failed': 0,
            'key_findings': [],
            'combined_data': {}
        }

        for agent_name, result in agent_results.items():
            if 'error' in result:
                summary['agents_failed'] += 1
                continue

            summary['agents_succeeded'] += 1

            # Extract key data
            agent_data = result.get('result', {})
            if isinstance(agent_data, dict):
                # Get message/summary
                message = agent_data.get('message', '')
                if message:
                    summary['key_findings'].append({
                        'agent': agent_name,
                        'finding': message[:200]
                    })

                # Merge data
                data = agent_data.get('data', {})
                if isinstance(data, dict):
                    summary['combined_data'][agent_name] = data

        return summary

    # ==================== Convenience Methods ====================

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """
        Analyze a task and return recommended team without executing.

        Useful for previewing what team would be formed.
        """
        team = self.build_team(task)

        return {
            'task': task,
            'recommended_team': [
                {
                    'agent': m.agent_name,
                    'role': m.role,
                    'relevance': round(m.relevance_score, 3),
                    'category': m.category,
                    'synergy_bonus': round(m.synergy_bonus, 2)
                }
                for m in team.members
            ],
            'total_synergy': round(team.total_synergy, 2),
            'formation_reason': team.formation_reason
        }

    def get_agent_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Return all agent capabilities for reference."""
        return {
            name: {
                'description': config.get('description', ''),
                'category': config.get('category', 'other'),
                'keywords': config.get('keywords', [])[:5],  # First 5 keywords
                'priority': config.get('priority', 0)
            }
            for name, config in self.routing_config.items()
        }


# ==================== Factory Function ====================

_team_builder_instance = None

def get_dynamic_team_builder() -> DynamicTeamBuilder:
    """Get singleton instance of DynamicTeamBuilder."""
    global _team_builder_instance
    if _team_builder_instance is None:
        _team_builder_instance = DynamicTeamBuilder()
    return _team_builder_instance
