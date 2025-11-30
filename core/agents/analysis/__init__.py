"""
Analysis Agents Package - Clean Architecture
=============================================

Session 280: Phase 3 - Agent Architecture Unification

Analysis agents for trend detection, opportunity scoring, and intelligence gathering.

Usage:
    from core.agents.analysis import TrendAnalysisAgent, OpportunityScoringAgent

    agent = TrendAnalysisAgent(user=request.user)
    result = agent.execute(
        task="Generate daily intelligence briefing",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.analysis.trend_analysis_agent import TrendAnalysisAgent
from core.agents.analysis.opportunity_scoring_agent import OpportunityScoringAgent

__all__ = [
    'TrendAnalysisAgent',
    'OpportunityScoringAgent',
]
