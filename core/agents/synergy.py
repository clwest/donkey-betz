"""
Agent Synergy System - Session 290

Simple synergy mapping to replace the complex Rivalry/Alliance system.
Instead of tracking detailed relationships in the database, we use
a simple static mapping of which agents work well together.

This replaces:
- Rivalry model (deprecated)
- Alliance model (deprecated)
- AgentRelationship complexity

The synergy system provides:
- Team bonus calculation for multi-agent collaboration
- Agent compatibility recommendations
- Simple, fast lookups without database queries
"""

from typing import List, Dict, Tuple, Set
import logging

logger = logging.getLogger(__name__)


# Agent synergy pairs with multiplier bonus
# Format: (agent1, agent2): bonus_multiplier
# Bonus > 1.0 = good synergy, < 1.0 = some friction
AGENT_SYNERGY: Dict[Tuple[str, str], float] = {
    # Research + Creation pairs (strong synergy)
    ('ResearchAgent', 'ImageAgent'): 1.25,
    ('ResearchAgent', 'VideoAgent'): 1.25,
    ('ResearchAgent', 'ContentStrategyAgent'): 1.30,
    ('TrendAnalysisAgent', 'ContentStrategyAgent'): 1.30,
    ('TrendAnalysisAgent', 'ResearchAgent'): 1.20,

    # Strategy + Execution pairs
    ('ContentStrategyAgent', 'ImageAgent'): 1.20,
    ('ContentStrategyAgent', 'SEOOptimizerAgent'): 1.25,
    ('BrandIdentityAgent', 'ImageAgent'): 1.30,
    ('BrandIdentityAgent', 'SocialMediaAgent'): 1.25,

    # Creative Director pairs (director boosts everyone)
    ('CreativeDirectorAgent', 'ImageAgent'): 1.20,
    ('CreativeDirectorAgent', 'VideoAgent'): 1.20,
    ('CreativeDirectorAgent', 'BrandIdentityAgent'): 1.25,

    # Executive pairs
    ('CTOAgent', 'COOAgent'): 1.15,
    ('CTOAgent', 'ResearchAgent'): 1.15,
    ('COOAgent', 'MeetingCoordinatorAgent'): 1.20,

    # Media production pairs
    ('ImageAgent', 'VideoAgent'): 1.15,
    ('VideoAgent', 'AudioAgent'): 1.25,
    ('ImageAgent', '3DGenerationAgent'): 1.20,

    # Social + SEO pairs
    ('SocialMediaAgent', 'SEOOptimizerAgent'): 1.20,
    ('SocialMediaAgent', 'TrendAnalysisAgent'): 1.25,

    # Workflow pairs
    ('WorkflowOrchestrationAgent', 'ImageAgent'): 1.10,
    ('WorkflowOrchestrationAgent', 'VideoAgent'): 1.10,
    ('WorkflowOrchestrationAgent', 'ResearchAgent'): 1.15,

    # Opportunity + Revenue pairs
    ('OpportunityScoringAgent', 'ResearchAgent'): 1.25,
    ('OpportunityScoringAgent', 'TrendAnalysisAgent'): 1.20,
}


def _normalize_pair(agent1: str, agent2: str) -> Tuple[str, str]:
    """Normalize agent pair for consistent lookup."""
    return tuple(sorted([agent1, agent2]))


def get_pair_synergy(agent1: str, agent2: str) -> float:
    """
    Get synergy bonus between two agents.

    Args:
        agent1: First agent name
        agent2: Second agent name

    Returns:
        Synergy multiplier (1.0 = neutral, >1.0 = bonus, <1.0 = penalty)
    """
    if agent1 == agent2:
        return 1.0

    # Try both orderings
    pair = (agent1, agent2)
    reverse_pair = (agent2, agent1)

    if pair in AGENT_SYNERGY:
        return AGENT_SYNERGY[pair]
    elif reverse_pair in AGENT_SYNERGY:
        return AGENT_SYNERGY[reverse_pair]

    return 1.0  # Default: neutral synergy


def get_team_synergy(agents: List[str]) -> Tuple[float, Dict[str, any]]:
    """
    Calculate total synergy bonus for a team of agents.

    Args:
        agents: List of agent names working together

    Returns:
        Tuple of (total_multiplier, details_dict)
    """
    if len(agents) < 2:
        return (1.0, {'reason': 'Single agent - no team synergy'})

    total_bonus = 1.0
    synergies = []

    # Check all pairs
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i+1:]:
            bonus = get_pair_synergy(agent1, agent2)
            if bonus != 1.0:
                total_bonus *= bonus
                if bonus > 1.0:
                    synergies.append(f"{agent1} + {agent2}: +{int((bonus-1)*100)}%")
                else:
                    synergies.append(f"{agent1} + {agent2}: {int((bonus-1)*100)}%")

    # Cap the bonus to prevent runaway multipliers
    total_bonus = max(0.5, min(total_bonus, 2.5))

    details = {
        'team_size': len(agents),
        'synergies_found': len(synergies),
        'synergy_details': synergies,
        'final_multiplier': round(total_bonus, 2),
    }

    return (total_bonus, details)


def get_recommended_partners(agent: str, top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Get recommended partner agents for collaboration.

    Args:
        agent: Agent name to find partners for
        top_n: Number of recommendations to return

    Returns:
        List of (agent_name, synergy_bonus) tuples, sorted by bonus
    """
    partners = []

    for (a1, a2), bonus in AGENT_SYNERGY.items():
        if a1 == agent:
            partners.append((a2, bonus))
        elif a2 == agent:
            partners.append((a1, bonus))

    # Sort by bonus descending
    partners.sort(key=lambda x: x[1], reverse=True)

    return partners[:top_n]


def get_all_synergy_agents() -> Set[str]:
    """Get set of all agents that have synergy relationships defined."""
    agents = set()
    for (a1, a2) in AGENT_SYNERGY.keys():
        agents.add(a1)
        agents.add(a2)
    return agents


# Convenience function for compatibility with old RelationshipInfluence
def get_relationship_influence_simple(agent_name: str) -> Dict[str, any]:
    """
    Simple replacement for the complex RelationshipInfluence dataclass.

    Returns a simplified dict with synergy info instead of full relationships.
    """
    partners = get_recommended_partners(agent_name, top_n=10)

    return {
        'allies': [p[0] for p in partners if p[1] > 1.0],  # Good synergy = "ally"
        'rivals': [],  # We no longer track rivals
        'neutral': [],  # Everyone else is neutral
        'collaboration_bonus': {p[0]: p[1] for p in partners},
        'team_synergy': 1.0,  # Will be calculated per-team
    }
