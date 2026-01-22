"""
Strategy Agents Package
========================

Session 280: Phase 2 - Agent Architecture Unification

Strategy agents provide content strategy, brand identity, SEO optimization,
and social media content recommendations. They help users decide WHAT to create
and HOW to optimize it for maximum impact.

Available Agents:
    ContentStrategyAgent - Analyzes trends, recommends content types
    BrandIdentityAgent - Manages brand consistency (colors, styles)
    SEOOptimizerAgent - Generates hashtags, keywords, metadata
    SocialMediaAgent - Platform-specific content optimization

Usage:
    from core.agents.strategy import ContentStrategyAgent, BrandIdentityAgent

    agent = ContentStrategyAgent(user=request.user)
    result = agent.execute(
        task="What content should I create for a tech audience?",
        context={},
        scifi_context=scifi_service.get_context('ContentStrategyAgent'),
        spider_context=spider_service.get_insights_for_prompt(task)
    )
"""

from core.agents.strategy.content_strategy_agent import ContentStrategyAgent
from core.agents.strategy.brand_identity_agent import BrandIdentityAgent
from core.agents.strategy.seo_optimizer_agent import SEOOptimizerAgent
from core.agents.strategy.social_media_agent import SocialMediaAgent

__all__ = [
    'ContentStrategyAgent',
    'BrandIdentityAgent',
    'SEOOptimizerAgent',
    'SocialMediaAgent',
]
# Force rebuild Thu Jan 22 08:29:40 MST 2026
