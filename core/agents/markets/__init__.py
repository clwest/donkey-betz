"""
Markets Agents Package
======================

Session 558: Agents for market intelligence and analysis.
Session 995B: Added GamePredictor, LineMovementAnalyzer, SharpActionDetector.

Agents:
- PredictionMarketAnalyst: Kalshi prediction market analysis
- SportsOddsAnalyst: Sports betting odds analysis (The Odds API)
- ArbitrageDetector: Cross-bookmaker arbitrage detection
- GamePredictor: Score/outcome predictions from market consensus
- LineMovementAnalyzer: Sharp money and reverse line movement detection
- SharpActionDetector: Professional betting pattern identification
"""

from .prediction_market_analyst import PredictionMarketAnalyst
from .sports_odds_analyst import SportsOddsAnalyst
from .arbitrage_detector import ArbitrageDetector
from .game_predictor import GamePredictor
from .line_movement_analyzer import LineMovementAnalyzer
from .sharp_action_detector import SharpActionDetector

__all__ = [
    'PredictionMarketAnalyst',
    'SportsOddsAnalyst',
    'ArbitrageDetector',
    'GamePredictor',
    'LineMovementAnalyzer',
    'SharpActionDetector',
]
