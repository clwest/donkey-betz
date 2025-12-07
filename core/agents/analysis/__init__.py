"""
Analysis Agents Package - Clean Architecture
=============================================

Session 280: Phase 3 - Agent Architecture Unification
Session 385: Added MarketIntelligenceAgent for financial market analysis

Analysis agents for trend detection, opportunity scoring, and intelligence gathering.

Usage:
    from core.agents.analysis import TrendAnalysisAgent, OpportunityScoringAgent, MarketIntelligenceAgent

    agent = TrendAnalysisAgent(user=request.user)
    result = agent.execute(
        task="Generate daily intelligence briefing",
        context={},
        scifi_context={},
        spider_context={}
    )

    market_agent = MarketIntelligenceAgent(user=request.user)
    result = market_agent.execute(
        task="What SEC filings should I pay attention to today?",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

from core.agents.analysis.trend_analysis_agent import TrendAnalysisAgent
from core.agents.analysis.opportunity_scoring_agent import OpportunityScoringAgent
from core.agents.analysis.market_intelligence_agent import MarketIntelligenceAgent

__all__ = [
    'TrendAnalysisAgent',
    'OpportunityScoringAgent',
    'MarketIntelligenceAgent',
]
