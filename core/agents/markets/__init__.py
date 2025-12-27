"""
Markets Agents Package
======================

Session 558: Agents for market intelligence and analysis.

Agents:
- PredictionMarketAnalyst: Kalshi prediction market analysis
- SportsOddsAnalyst: Sports betting odds analysis (The Odds API)
- ArbitrageDetector: Cross-bookmaker arbitrage detection
"""

from .prediction_market_analyst import PredictionMarketAnalyst
from .sports_odds_analyst import SportsOddsAnalyst
from .arbitrage_detector import ArbitrageDetector

__all__ = [
    'PredictionMarketAnalyst',
    'SportsOddsAnalyst',
    'ArbitrageDetector',
]
