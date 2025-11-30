"""
Business Research Agents
========================

Session 293: Business Intelligence Extension

New agents for comprehensive business research:
- CompetitorAnalysisAgent: Track competitors, SWOT analysis, positioning
- CustomerResearchAgent: Personas, pain points, sentiment analysis
- MarketSizingAgent: TAM/SAM/SOM calculations (future)
- BusinessModelAgent: Revenue streams, unit economics (future)
- StrategicPlanningAgent: SWOT, go-to-market plans (future)
"""

from .competitor_analysis_agent import CompetitorAnalysisAgent
from .customer_research_agent import CustomerResearchAgent

__all__ = [
    'CompetitorAnalysisAgent',
    'CustomerResearchAgent',
]
