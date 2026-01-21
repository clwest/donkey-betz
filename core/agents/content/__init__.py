"""
Content Debate Agents - Session 466, 784

Part of Autonomous Content Studio (Property #3: Internal Disagreement).

These agents debate content decisions before creation:
- TopicMinerAgent: Finds trending topics (argues FOR popular)
- ContrarianAgent: Challenges obvious choices (argues AGAINST trendy)
- PerformanceAnalystAgent: Uses data to guide decisions (argues from EVIDENCE)
- VoiceCriticAgent: Scores content voice quality (Session 784)

The debate creates better content decisions than any single agent alone.
"""

from .topic_miner_agent import TopicMinerAgent
from .contrarian_agent import ContrarianAgent
from .performance_analyst_agent import PerformanceAnalystAgent
from .voice_critic_agent import VoiceCriticAgent

__all__ = [
    'TopicMinerAgent',
    'ContrarianAgent',
    'PerformanceAnalystAgent',
    'VoiceCriticAgent',
]
