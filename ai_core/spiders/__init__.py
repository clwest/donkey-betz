"""
Spider Army - Massive Intelligence Gathering Network
====================================================

This module implements the most comprehensive AI intelligence gathering network
ever created, consisting of thousands of specialized spiders that feed continuous
real-time intelligence to 102 agents and 25 legendary advisors.

Spider Army Composition:
- 500 Financial Intelligence Spiders (for Buffett-style advisors)
- 300 Innovation Tracking Spiders (for Cathie Wood-style advisors)
- 200 Market Data Spiders (real-time trading)
- 150 Social Sentiment Spiders (Reddit, Twitter, etc.)
- 120 News Harvesting Spiders (Bloomberg, Reuters, etc.)
- 100 Research Paper Spiders (arXiv, PubMed, etc.)
- 80 Patent Monitoring Spiders
- 70 Regulatory Tracking Spiders
- 50 Competitive Intelligence Spiders
- 200 General Purpose Adaptive Spiders

TOTAL: 1,770 ACTIVE SPIDERS creating personalized intelligence streams
"""

from .spider_army_orchestrator import SpiderArmyOrchestrator
from .base_spider import BaseIntelligenceSpider
from .command_center import SpiderCommandCenter

__all__ = [
    'SpiderArmyOrchestrator',
    'BaseIntelligenceSpider',
    'SpiderCommandCenter'
]