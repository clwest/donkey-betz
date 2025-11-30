"""
Executive Agents Package
=========================

Session 280: Phase 2 - Agent Architecture Unification

Executive agents provide high-level planning, coordination, and strategic
oversight. They analyze projects, coordinate other agents, and provide
executive-level guidance.

Available Agents:
    CTOAgent - Technical planning and code analysis (read-only)
    COOAgent - Operations planning and risk analysis
    CreativeDirectorAgent - Creative guidance and prompt enhancement
    MeetingCoordinatorAgent - Coordinates meetings between agents

Usage:
    from core.agents.executive import CTOAgent, COOAgent

    agent = CTOAgent(user=request.user)
    result = agent.execute(
        task="Analyze the authentication feature",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.executive.cto_agent import CTOAgent
from core.agents.executive.coo_agent import COOAgent
from core.agents.executive.creative_director_agent import CreativeDirectorAgent
from core.agents.executive.meeting_coordinator_agent import MeetingCoordinatorAgent

__all__ = [
    'CTOAgent',
    'COOAgent',
    'CreativeDirectorAgent',
    'MeetingCoordinatorAgent',
]
