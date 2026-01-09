"""
Agent Collaboration Optimizer
Autonomous system that optimizes agent collaboration patterns based on learning data
"""

import logging
from typing import List, Dict, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)


class AgentCollaborationOptimizer:
    """
    Analyzes collaboration patterns and automatically suggests optimal agent teams

    Uses learning data to:
    - Form optimal agent teams for tasks
    - Predict collaboration success
    - Suggest missing agent capabilities
    - Auto-improve team compositions
    """

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    def suggest_optimal_team(self, task_description: str, user, max_agents: int = 5) -> List[str]:
        """
        Suggest optimal agent team for a task based on learning data

        Returns: List of agent names in recommended order
        """
        cache_key = f"optimal_team_{user.id}_{hash(task_description)}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        logger.info(f"🤝 Suggesting optimal team for task: {task_description[:50]}...")

        # Analyze task to determine required capabilities
        required_capabilities = self._analyze_task_capabilities(task_description)

        # Get high-performing agents for this user
        top_agents = self._get_top_performing_agents(user, required_capabilities)

        # Find agents that work well together
        optimal_team = self._build_collaborative_team(user, top_agents, max_agents)

        # Cache the result
        cache.set(cache_key, optimal_team, self.cache_timeout)

        logger.info(f"✅ Suggested team: {', '.join(optimal_team[:3])}...")
        return optimal_team

    def _analyze_task_capabilities(self, task: str) -> Dict[str, float]:
        """
        Analyze what capabilities are needed for this task

        Returns: Dict of capability -> importance score
        """
        capabilities = {}
        task_lower = task.lower()

        # Research capabilities
        if any(word in task_lower for word in ['research', 'analyze', 'investigate', 'find']):
            capabilities['research'] = 0.9
            capabilities['data_analysis'] = 0.7

        # Content creation
        if any(word in task_lower for word in ['write', 'create', 'generate', 'content']):
            capabilities['content_creation'] = 0.9
            capabilities['creativity'] = 0.8

        # Development
        if any(word in task_lower for word in ['code', 'develop', 'build', 'implement']):
            capabilities['development'] = 0.9
            capabilities['technical'] = 0.8

        # Planning/Strategy
        if any(word in task_lower for word in ['plan', 'strategy', 'roadmap', 'design']):
            capabilities['planning'] = 0.9
            capabilities['strategic_thinking'] = 0.7

        # Data processing
        if any(word in task_lower for word in ['data', 'process', 'extract', 'transform']):
            capabilities['data_processing'] = 0.9
            capabilities['automation'] = 0.6

        # If no specific capabilities detected, use general
        if not capabilities:
            capabilities['general'] = 0.5

        return capabilities

    def _get_top_performing_agents(self, user, required_capabilities: Dict) -> List[Tuple[str, float]]:
        """
        Get agents that perform well for the required capabilities

        Returns: List of (agent_name, score) tuples
        """
        from core.models_unified_system import UserAgentLearning, Agent

        agent_scores = []

        # Get all agents
        agents = Agent.objects.all()

        for agent in agents:
            # Get learning data for this agent and user
            learning_records = UserAgentLearning.objects.filter(
                user=user,
                agent_name=agent.name
            )

            if not learning_records.exists():
                # New agent - give benefit of doubt based on specialization
                base_score = self._match_agent_to_capabilities(agent, required_capabilities)
                agent_scores.append((agent.name, base_score))
                continue

            # Calculate score from learning data
            total_score = 0
            weight_sum = 0

            for learning in learning_records:
                # Weight by confidence and success rate
                confidence = learning.confidence_score
                success_rate = learning.success_rate if hasattr(learning, 'success_rate') else 0.5

                # Check if this learning domain matches required capabilities
                domain_match = self._domain_matches_capabilities(
                    learning.learning_domain,
                    required_capabilities
                )

                if domain_match > 0:
                    score = (confidence * 0.4 + success_rate * 0.6) * domain_match
                    total_score += score
                    weight_sum += domain_match

            # Calculate final score
            if weight_sum > 0:
                final_score = total_score / weight_sum
            else:
                final_score = self._match_agent_to_capabilities(agent, required_capabilities)

            agent_scores.append((agent.name, final_score))

        # Sort by score descending
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        return agent_scores[:20]  # Top 20 candidates

    def _match_agent_to_capabilities(self, agent, required_capabilities: Dict) -> float:
        """Match agent specialization to required capabilities"""
        spec_lower = agent.specialization.lower() if agent.specialization else ''

        match_score = 0
        for capability, importance in required_capabilities.items():
            if capability.lower() in spec_lower:
                match_score += importance

        # Normalize
        return match_score / len(required_capabilities) if required_capabilities else 0.3

    def _domain_matches_capabilities(self, domain: str, capabilities: Dict) -> float:
        """Check if learning domain matches required capabilities"""
        domain_lower = domain.lower()

        match_score = 0
        for capability in capabilities.keys():
            if capability.lower() in domain_lower:
                match_score += 1

        return match_score / len(capabilities) if capabilities else 0

    def _build_collaborative_team(self, user, top_agents: List[Tuple[str, float]],
                                  max_agents: int) -> List[str]:
        """
        Build a team that works well together based on collaboration history
        """

        team = []

        # Start with highest performing agent
        if top_agents:
            team.append(top_agents[0][0])

        # Add agents that work well with existing team members
        for agent_name, score in top_agents[1:]:
            if len(team) >= max_agents:
                break

            # Check collaboration compatibility with existing team
            compatibility = self._check_team_compatibility(user, agent_name, team)

            # Add if compatible
            if compatibility > 0.5:
                team.append(agent_name)

        return team

    def _check_team_compatibility(self, user, agent_name: str, existing_team: List[str]) -> float:
        """
        Check how well an agent works with existing team members
        """
        from core.models_unified_system import UserAgentLearning

        if not existing_team:
            return 1.0

        compatibility_scores = []

        # Check collaboration history with each team member
        for team_member in existing_team:
            # Look for collaboration learning data
            learning = UserAgentLearning.objects.filter(
                user=user,
                agent_name=agent_name,
                learning_domain='collaboration_skills'
            ).first()

            if learning and isinstance(learning.learning_content, dict):
                partners = learning.learning_content.get('common_partners', {})

                if team_member in partners:
                    partner_data = partners[team_member]
                    success_rate = (
                        partner_data['successes'] / partner_data['count']
                        if partner_data['count'] > 0 else 0.5
                    )
                    compatibility_scores.append(success_rate)
                else:
                    # No history - neutral score
                    compatibility_scores.append(0.6)
            else:
                # No learning data - neutral score
                compatibility_scores.append(0.6)

        # Return average compatibility
        return sum(compatibility_scores) / len(compatibility_scores) if compatibility_scores else 0.6

    def get_collaboration_insights(self, user) -> Dict:
        """
        Get insights about agent collaboration patterns for this user
        """
        from core.models_unified_system import UserAgentLearning

        insights = {
            'top_teams': [],
            'best_collaborators': [],
            'improvement_areas': [],
            'success_patterns': []
        }

        # Get team formation learning
        team_learning = UserAgentLearning.objects.filter(
            user=user,
            learning_domain='team_formation'
        ).order_by('-confidence_score')[:5]

        for learning in team_learning:
            if isinstance(learning.learning_content, dict):
                content = learning.learning_content
                insights['top_teams'].append({
                    'team': content.get('team_members', []),
                    'success_rate': content.get('success_rate', 0),
                    'avg_duration': content.get('avg_duration', 0),
                    'task_types': content.get('task_types', [])
                })

        # Get individual agent collaboration skills
        collab_learning = UserAgentLearning.objects.filter(
            user=user,
            learning_domain='collaboration_skills'
        ).order_by('-confidence_score')[:10]

        for learning in collab_learning:
            if isinstance(learning.learning_content, dict):
                content = learning.learning_content
                success_rate = (
                    content['successful_collaborations'] / content['total_collaborations']
                    if content.get('total_collaborations', 0) > 0 else 0
                )

                if success_rate > 0.7:  # High performers
                    insights['best_collaborators'].append({
                        'agent': learning.agent_name,
                        'success_rate': success_rate,
                        'total_collaborations': content.get('total_collaborations', 0)
                    })
                elif success_rate < 0.4:  # Needs improvement
                    insights['improvement_areas'].append({
                        'agent': learning.agent_name,
                        'success_rate': success_rate,
                        'issue': 'Low collaboration success rate'
                    })

        return insights

    def auto_optimize_collaboration(self, user) -> Dict:
        """
        Automatically analyze and suggest collaboration improvements

        Returns: Dict with optimization suggestions
        """
        # Session 737: Guard against None user
        user_id = user.id if user else 'anonymous'
        logger.info(f"🔧 Auto-optimizing collaborations for user {user_id}")

        insights = self.get_collaboration_insights(user)

        optimizations = {
            'recommended_teams': [],
            'agents_to_train': [],
            'collaboration_strategies': []
        }

        # Recommend best-performing teams for common task types
        if insights['top_teams']:
            for team_data in insights['top_teams'][:3]:
                optimizations['recommended_teams'].append({
                    'team': team_data['team'],
                    'best_for': team_data['task_types'],
                    'expected_success': team_data['success_rate']
                })

        # Identify agents that need more collaboration practice
        if insights['improvement_areas']:
            for area in insights['improvement_areas']:
                optimizations['agents_to_train'].append({
                    'agent': area['agent'],
                    'issue': area['issue'],
                    'suggestion': 'Pair with high-performing collaborators for learning'
                })

        # Suggest collaboration strategies
        if insights['best_collaborators']:
            optimizations['collaboration_strategies'].append({
                'strategy': 'Use proven collaborators',
                'agents': [c['agent'] for c in insights['best_collaborators'][:3]],
                'expected_benefit': 'Higher success rate on team tasks'
            })

        logger.info(f"✅ Generated {len(optimizations['recommended_teams'])} optimization suggestions")

        return optimizations


# Singleton instance
collaboration_optimizer = AgentCollaborationOptimizer()
