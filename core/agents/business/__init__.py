"""
Business Research Agents
========================

Session 293: Business Intelligence Extension
Session 335: Added BrandStrategyAgent
Session 337: Added BaseBusinessResearchAgent, ContentStrategyAgent, MarketingStrategyAgent
Session 2932: Removed duplicate business.ContentStrategyAgent — canonical class
    lives at core.agents.strategy.ContentStrategyAgent (the AGENT_MAP-registered
    class reached by the content_strategy_agent PA tool).

New agents for comprehensive business research:
- CompetitorAnalysisAgent: Track competitors, SWOT analysis, positioning
- CustomerResearchAgent: Personas, pain points, sentiment analysis
- BrandStrategyAgent: Brand positioning, messaging, visual direction
- MarketingStrategyAgent: Channel strategy, campaigns, funnel optimization (NEW - Session 337)
- BaseBusinessResearchAgent: Base class for all business research agents (NEW - Session 337)
"""

from .base_business_research_agent import BaseBusinessResearchAgent, AgentResult
from .competitor_analysis_agent import CompetitorAnalysisAgent
from .customer_research_agent import CustomerResearchAgent
from .brand_strategy_agent import BrandStrategyAgent
from .marketing_strategy_agent import MarketingStrategyAgent

__all__ = [
    'BaseBusinessResearchAgent',
    'AgentResult',
    'CompetitorAnalysisAgent',
    'CustomerResearchAgent',
    'BrandStrategyAgent',
    'MarketingStrategyAgent',
]
