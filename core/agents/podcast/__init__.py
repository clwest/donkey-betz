"""
Podcast Studio Agents - Session 496

Multi-agent podcast generation system where AI agents research,
debate, and create audio content with different voices.

Agents:
- PodcastCoordinatorAgent: Orchestrates the entire podcast creation process
- DebateAdvocateAgent: Argues FOR the debate topic with research
- DebateSkepticAgent: Argues AGAINST the debate topic with research
- ModeratorAgent: Hosts the discussion, manages flow, summarizes

The workflow:
1. User provides topic → Coordinator assigns perspectives
2. Each agent researches their position using spiders
3. Structured debate occurs with back-and-forth
4. Coordinator creates podcast script from debate
5. Optional: ElevenLabs generates audio with different voices
"""

from .podcast_coordinator_agent import PodcastCoordinatorAgent
from .debate_advocate_agent import DebateAdvocateAgent
from .debate_skeptic_agent import DebateSkepticAgent
from .moderator_agent import ModeratorAgent

__all__ = [
    'PodcastCoordinatorAgent',
    'DebateAdvocateAgent',
    'DebateSkepticAgent',
    'ModeratorAgent',
]
